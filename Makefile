# One entry point for authors and CI. Every target runs inside the pinned
# toolbox image (tools/Dockerfile), so results are the same everywhere.
#
#   make check    run every validation layer
#   make build    build HTML, PDF, OSCAL catalog and CSV/XLSX
#   make publish  assemble the versioned site and release artifacts
#   make help     list all targets

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

TOOLBOX_TAG := $(shell cat tools/Dockerfile tools/requirements.txt tools/package.json tools/package-lock.json | sha256sum | cut -c1-12)
IMAGE ?= standards-toolbox:$(TOOLBOX_TAG)

ifndef IN_TOOLBOX
GH_TOKEN ?= $(shell gh auth token 2>/dev/null)
GH_REPO ?= $(shell gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
export GH_TOKEN GH_REPO
# ---------------------------------------------------------------------------
# Outside the toolbox: build the image if needed, then re-run make inside it.
# ---------------------------------------------------------------------------
GOALS := $(or $(filter-out toolbox toolbox-tag,$(MAKECMDGOALS)),$(if $(MAKECMDGOALS),,help))
.PHONY: toolbox toolbox-tag $(GOALS)

toolbox:
	@docker image inspect $(IMAGE) >/dev/null 2>&1 || docker build -t $(IMAGE) tools

toolbox-tag:
	@echo $(IMAGE)

ifneq ($(GOALS),)
$(firstword $(GOALS)): toolbox
	@docker run --rm -u $$(id -u):$$(id -g) -v "$(CURDIR)":/work -w /work \
	  -e SOURCE_DATE_EPOCH -e GITHUB_REPOSITORY -e GH_TOKEN -e GH_REPO $(IMAGE) \
	  make --no-print-directory $(GOALS) $(MAKEOVERRIDES)
$(wordlist 2,99,$(GOALS)):
	@:
endif

else
# ---------------------------------------------------------------------------
# Inside the toolbox.
# ---------------------------------------------------------------------------
SRC ?= src/en
BUILD ?= build
LANGS ?= en es ja
VERSION ?= $(shell cat VERSION)
NAME ?= mdss
REPO ?= $(or $(GITHUB_REPOSITORY),$(GH_REPO),dug-21/publishing)
CHANNEL ?= draft
FEEDBACK_URL ?= https://github.com/$(REPO)/issues/new
PDF_FLAGS ?= --pdf-variant pdf/ua-1
SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)
export SOURCE_DATE_EPOCH
REVDATE := $(shell date -u -d @$(SOURCE_DATE_EPOCH) +%Y-%m-%d)
MODIFIED := $(shell date -u -d @$(SOURCE_DATE_EPOCH) +%Y-%m-%dT%H:%M:%SZ)

SITE := $(BUILD)/site
DIST := $(BUILD)/dist
REQS := $(BUILD)/requirements.json
OSCAL := $(DIST)/$(NAME)-$(VERSION)-catalog.json
CHECK_OSCAL ?= $(OSCAL)
GRC := $(DIST)/$(NAME)-$(VERSION)
HTML := $(foreach l,$(LANGS),$(SITE)/$(l)/index.html)
PDFS := $(foreach l,$(LANGS),$(DIST)/$(NAME)-$(VERSION)-$(l).pdf)
PDF ?= $(PDFS)
SOURCES := $(wildcard $(SRC)/*.adoc $(SRC)/images/*)
ADOC_ATTRS = -a revnumber=$(VERSION) -a revdate=$(REVDATE) -a reproducible
-include l10n/attributes.mk
srcdir = $(if $(filter en,$(1)),$(SRC),$(BUILD)/src/$(1))

.DEFAULT_GOAL := help
.PHONY: help check build publish clean \
  check-source check-structure check-language check-links check-terms check-prose \
  check-html check-pdf check-oscal check-exports check-a11y check-a11y-html check-a11y-pdf \
  check-fixtures check-scale html pdf oscal grc l10n-update \
  feedback-setup feedback-template feedback-export feedback-import release-notes

help: ## List targets
	@grep -hE '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-18s %s\n", $$1, $$2}'

# ---- Build ----------------------------------------------------------------

build: html pdf oscal grc feedback-template ## Build HTML, PDF, OSCAL catalog, CSV/XLSX and the comment template

html: $(HTML) ## Build the HTML edition for every language
pdf: $(PDFS) ## Build the tagged PDF for every language
oscal: $(OSCAL) ## Build the OSCAL catalog
grc: $(GRC)-requirements.xlsx ## Build the CSV/XLSX exports for GRC tools

$(REQS): $(SOURCES) tools/extract_requirements.rb
	@mkdir -p $(@D)
	ruby tools/extract_requirements.rb $(SRC)/standard.adoc $@ -a revnumber=$(VERSION) -a revdate=$(REVDATE)

# Translated source trees are generated from the PO files, all languages at once.
$(BUILD)/src/.stamp: $(SOURCES) l10n/po4a.cfg $(wildcard l10n/po/*.po)
	@mkdir -p $(@D)
	po4a --no-update --keep 0 --destdir $(BUILD)/src l10n/po4a.cfg >/dev/null
	@for l in $(filter-out en,$(LANGS)); do mkdir -p $(BUILD)/src/$$l/images && cp -r $(SRC)/images/. $(BUILD)/src/$$l/images/; done
	@touch $@

.SECONDEXPANSION:
$(SITE)/%/index.html: $$(if $$(filter en,$$*),$(SOURCES),$(BUILD)/src/.stamp) theme/standard.css tools/asciidoc/comment_links.rb
	@mkdir -p $(@D)
	asciidoctor -v --failure-level INFO -r ./tools/asciidoc/comment_links.rb \
	  $(ADOC_ATTRS) -a lang=$* -a data-uri -a stylesheet=standard.css -a stylesdir=$(CURDIR)/theme \
	  -a feedback-url=$(FEEDBACK_URL) $(L10N_ATTRS_$*) -o $@ $(call srcdir,$*)/standard.adoc

$(DIST)/$(NAME)-$(VERSION)-%.pdf: $(SITE)/%/index.html
	@mkdir -p $(@D)
	weasyprint -q $(PDF_FLAGS) $< $@

$(OSCAL): $(REQS) tools/build_oscal.py
	@mkdir -p $(@D)
	python3 tools/build_oscal.py $(REQS) $@ --last-modified $(MODIFIED)

$(GRC)-requirements.xlsx: $(REQS) tools/export_grc.py
	@mkdir -p $(@D)
	python3 tools/export_grc.py $(REQS) $(GRC)

# ---- Validation -----------------------------------------------------------

check: check-source check-structure check-language check-terms check-prose \
       check-links check-html check-pdf check-oscal check-exports check-a11y ## Run every validation layer
	@echo "All checks passed."

check-source: ## AsciiDoc syntax, includes and internal cross-references
	@mkdir -p $(BUILD)
	asciidoctor -v --failure-level INFO $(ADOC_ATTRS) -o $(BUILD)/.check-source.html $(SRC)/standard.adoc
	@echo "source: OK"

check-structure: $(REQS) ## Required sections, requirement IDs, numbering
	check-jsonschema --schemafile tools/schemas/requirements.schema.json $(REQS)
	python3 tools/check_requirements.py --rules structure $(REQS)

check-language: $(REQS) ## Normative keywords only in normative text
	python3 tools/check_requirements.py --rules language $(REQS)

check-terms: ## Defined terms used as defined
	vale --no-wrap --filter='.Name matches "Terms"' $(wildcard $(SRC)/*.adoc)
	@echo "terms: OK"

check-prose: ## Prose style and spelling
	vale --no-wrap --filter='not (.Name matches "Terms")' $(wildcard $(SRC)/*.adoc)
	cspell --no-progress --no-summary $(wildcard $(SRC)/*.adoc)
	@echo "prose: OK"

check-links: $(SITE)/en/index.html ## External links and anchors resolve
	lychee --no-progress --include-fragments --max-retries 3 --exclude 'github\.com/.*/issues/new' $<

check-html: $(HTML) ## HTML is valid (Nu Html Checker)
	java -jar /opt/toolbox/node_modules/vnu-jar/build/dist/vnu.jar --errors-only $(HTML)
	@echo "html: OK"

check-a11y: check-a11y-html check-a11y-pdf ## Accessibility of HTML and PDF

check-a11y-html: $(HTML) ## WCAG 2.2 A/AA automated rules (axe-core)
	node tools/a11y.mjs $(HTML)

check-pdf: $(PDFS) ## PDFs were generated and are tagged
	python3 tools/check_pdf.py $(PDFS)

check-a11y-pdf: $(PDF) ## PDF/UA-1 (veraPDF)
	python3 tools/check_pdfua.py $(PDF)

check-oscal: $(filter $(OSCAL),$(CHECK_OSCAL)) ## OSCAL catalog validates against the NIST schema and constraints
	check-jsonschema --schemafile /opt/oscal/oscal_catalog_schema.json $(CHECK_OSCAL)
	oscal-cli validate $(CHECK_OSCAL)

check-exports: $(GRC)-requirements.xlsx ## CSV/XLSX row counts match the standard
	python3 tools/export_grc.py $(REQS) $(GRC) --verify

check-fixtures: ## Prove each validator fails on its failure fixture
	bash tools/run_fixtures.sh

check-scale: ## Prove the pipeline on a generated standard of about 400 pages
	python3 tools/generate_stress.py $(BUILD)/stress/src
	time $(MAKE) --no-print-directory SRC=$(BUILD)/stress/src BUILD=$(BUILD)/stress LANGS=en NAME=scale \
	  check-source check-structure check-language check-html check-pdf check-a11y-pdf check-oscal check-exports

# ---- Translation ----------------------------------------------------------

l10n-update: ## Refresh the POT and PO files from the English source
	po4a --no-translations l10n/po4a.cfg

# ---- Feedback ------------------------------------------------------------

TEMPLATE := $(DIST)/$(NAME)-$(VERSION)-comment-template.xlsx
FILE ?=

feedback-template: $(TEMPLATE) ## Build the spreadsheet comment template (for reviewers without a GitHub account)
$(TEMPLATE): $(SOURCES) tools/feedback.py
	@mkdir -p $(@D)
	python3 tools/feedback.py --src $(SRC) template $@

feedback-setup: ## Create the issue labels the feedback flow uses (run once per repository)
	@for l in "public-comment|Comment on a requirement or clause" "id-verified|Comment refers to a valid ID" \
	  "needs-valid-id|Comment does not refer to a valid ID" "spreadsheet-import|Comment received by spreadsheet" \
	  "disposition:accepted|Comment accepted" "disposition:rejected|Comment not accepted" "disposition:noted|Comment noted, no change"; do \
	  gh label create "$${l%%|*}" --description "$${l##*|}" --force; done

feedback-export: ## Export all public comments as a disposition matrix (CSV/XLSX)
	python3 tools/feedback.py --src $(SRC) export $(BUILD)/feedback/$(NAME)-comments

feedback-import: ## Create issues from a filled-in template: make feedback-import FILE=comments.xlsx [DRY_RUN=1]
	python3 tools/feedback.py --src $(SRC) import $(FILE) $(if $(DRY_RUN),--dry-run)

# ---- Publish --------------------------------------------------------------

publish: build ## Assemble the versioned site and release artifacts (CHANNEL=draft|release)
	python3 tools/assemble_site.py --build $(BUILD) --version $(VERSION) --name $(NAME) --langs "$(LANGS)" --channel $(CHANNEL)
	java -jar /opt/toolbox/node_modules/vnu-jar/build/dist/vnu.jar --errors-only $(BUILD)/publish/site/index.html $(BUILD)/publish/site/*/index.html
	node tools/a11y.mjs $(BUILD)/publish/site/index.html $(BUILD)/publish/site/$(if $(filter release,$(CHANNEL)),v$(VERSION),draft)/index.html

release-notes: ## Write release notes for the current tag to build/release-notes.md
	@mkdir -p $(BUILD)
	git-cliff --config cliff.toml --current --strip header -o $(BUILD)/release-notes.md || git-cliff --config cliff.toml --unreleased --strip header -o $(BUILD)/release-notes.md

clean: ## Remove build output
	rm -rf $(BUILD)

endif
