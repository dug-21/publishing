#!/usr/bin/env ruby
# Extracts the structure of the standard from the parsed AsciiDoc document and
# writes it as JSON. This file is the single source for the structural checks,
# the OSCAL catalog and the spreadsheet export.
#
# Usage: extract_requirements.rb SOURCE.adoc OUTPUT.json [-a name=value ...]
require 'asciidoctor'
require 'json'
require 'cgi'

source, output, *rest = ARGV
abort 'usage: extract_requirements.rb SOURCE.adoc OUTPUT.json [-a name=value]' unless source && output
attrs = {}
rest.each_slice(2) { |flag, kv| k, v = kv.split('=', 2); attrs[k] = v.to_s if flag == '-a' }

doc = Asciidoctor.load_file(source, safe: :unsafe, sourcemap: true, attributes: attrs)
ROOT = File.expand_path(Dir.pwd)

def strip_html(html)
  text = html.to_s.gsub(%r{<sup class="footnote(ref)?".*?</sup>}m, '').gsub(/<[^>]+>/, '')
  CGI.unescapeHTML(text).gsub(/[ \t]*\n[ \t]*/, ' ').gsub(/[ \t]+/, ' ').strip
end

def plain(block)
  case block.context
  when :paragraph then strip_html(block.content)
  when :ulist, :olist
    block.items.map { |i| (['- ' + strip_html(i.text)] + i.blocks.map { |b| plain(b) }).join("\n") }.join("\n")
  when :dlist
    block.items.map { |terms, dd| "#{terms.map { |t| strip_html(t.text) }.join(', ')}: #{dd ? strip_html(dd.text) : ''}" }.join("\n")
  when :table
    (block.rows.head + block.rows.body).map { |r| r.map { |c| strip_html(c.text) }.join(' | ') }.join("\n")
  else
    block.blocks.map { |b| plain(b) }.reject(&:empty?).join("\n\n")
  end
end

def location(node)
  node = node.parent until node.nil? || (node.respond_to?(:source_location) && node.source_location)
  return { 'file' => nil, 'line' => nil } unless node
  loc = node.source_location
  file = loc.file ? File.expand_path(loc.file).sub("#{ROOT}/", '') : nil
  { 'file' => file, 'line' => loc.lineno }
end

INFORMATIVE_ROLES = %w[informative guidance].freeze

def informative?(node)
  while node && node.context != :document
    return true if node.context == :admonition
    return true if node.respond_to?(:roles) && (node.roles & INFORMATIVE_ROLES).any?
    node = node.parent
  end
  false
end

def number_of(section)
  section.numbered ? section.sectnum.to_s.chomp('.') : nil
end

sections = doc.find_by(context: :section) { |s| s.level > 0 }.map do |s|
  {
    'id' => s.id, 'title' => strip_html(s.title), 'number' => number_of(s), 'level' => s.level,
    'kind' => s.sectname, 'roles' => s.roles, 'informative' => informative?(s),
    'parent' => (s.parent.context == :section ? s.parent.id : nil)
  }.merge(location(s))
end

requirements = doc.find_by(context: :section) { |s| s.has_role?('requirement') }.map do |s|
  statement = s.blocks.find { |b| b.has_role?('statement') }
  testing = s.blocks.find { |b| b.context == :dlist && b.has_role?('testing') }
  guidance = s.blocks.find { |b| b.has_role?('guidance') }
  procedures = (testing ? testing.items : []).map do |terms, dd|
    raw = terms.first.text
    {
      'id' => raw[/<a id="([^"]+)"/, 1], 'label' => strip_html(raw),
      'text' => dd ? ([strip_html(dd.text)] + dd.blocks.map { |b| plain(b) }).reject(&:empty?).join("\n\n") : ''
    }.merge(location(terms.first))
  end
  group = s.parent.context == :section ? s.parent : nil
  clause = group && group.parent.context == :section ? group.parent : group
  {
    'id' => s.id, 'number' => number_of(s), 'title' => strip_html(s.title),
    'clause' => clause && { 'id' => clause.id, 'number' => number_of(clause), 'title' => strip_html(clause.title) },
    'group' => group && { 'id' => group.id, 'number' => number_of(group), 'title' => strip_html(group.title) },
    'statement' => statement ? plain(statement) : nil,
    'testing_procedures' => procedures,
    'guidance' => guidance ? plain(guidance) : nil
  }.merge(location(s))
end

terms = []
(doc.find_by(context: :section) { |s| s.id == 'terms' }.first&.blocks || []).each do |b|
  next unless b.context == :dlist
  b.items.each do |ts, dd|
    raw = ts.first.text
    terms << { 'id' => raw[/<a id="([^"]+)"/, 1], 'term' => strip_html(raw),
               'definition' => dd ? strip_html(dd.text) : '' }.merge(location(ts.first))
  end
end

# Every piece of prose with its normative status, for the keyword-placement rule.
prose = []
add = lambda do |node, text, kind|
  prose << { 'kind' => kind, 'text' => text, 'informative' => informative?(node) }.merge(location(node)) unless text.empty?
end
doc.find_by(context: :paragraph).each { |b| add.call(b, strip_html(b.content), 'paragraph') }
doc.find_by(context: :list_item).each do |i|
  text = i.respond_to?(:text) && i.text? ? strip_html(i.text) : ''
  add.call(i, text, 'list item')
end
doc.find_by(context: :table).each do |t|
  (t.rows.head + t.rows.body).flatten.each { |c| add.call(t, strip_html(c.text), 'table cell') }
end

result = {
  'schema_version' => '1.0',
  'document' => {
    'title' => doc.doctitle, 'version' => doc.attr('revnumber'), 'date' => doc.attr('revdate'),
    'lang' => doc.attr('lang', 'en'), 'source' => source
  },
  'sections' => sections, 'terms' => terms, 'requirements' => requirements, 'prose' => prose
}
File.write(output, JSON.pretty_generate(result) + "\n")
warn "extracted #{requirements.size} requirements, #{requirements.sum { |r| r['testing_procedures'].size }} testing procedures, #{terms.size} terms"
