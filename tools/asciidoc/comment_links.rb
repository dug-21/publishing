# Asciidoctor extension: adds a "Comment on this requirement" link to every
# requirement section. The link opens the feedback issue form with the
# requirement ID prefilled. Enabled when the `feedback-url` attribute is set.
require 'asciidoctor/extensions'
require 'erb'

Asciidoctor::Extensions.register do
  tree_processor do
    process do |doc|
      base = doc.attr('feedback-url')
      next doc unless base

      label = doc.attr('comment-label', 'Comment on requirement')
      doc.find_by(context: :section) { |s| s.has_role?('requirement') }.each do |sec|
        number = sec.id.to_s.sub(/\AREQ-/, '')
        query = {
          'template' => 'requirement-comment.yml',
          'requirement-id' => sec.id,
          'title' => "[#{sec.id}] "
        }.map { |k, v| "#{k}=#{ERB::Util.url_encode(v)}" }.join('&')
        text = "link:++#{base}?#{query}++[#{label} #{number}]"
        sec << create_paragraph(sec, text, { 'role' => 'comment-link' }, subs: :normal)
      end
      doc
    end
  end
end
