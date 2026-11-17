# Toolbox image: every tool the pipeline uses, pinned.
# The Makefile runs all targets inside this image, locally and in CI.
FROM verapdf/cli:v1.30.4@sha256:f085855d442ad415e79fabbabcdd1803c2db4ee097cd5b94506c95ecdcfa1728 AS verapdf

FROM node:26-trixie-slim@sha256:e6bedef217677b276c591795e169840edd9096dbf13f29df8ef8d1856b8820bc

ARG ASCIIDOCTOR_VERSION=2.0.26
ARG VALE_VERSION=3.27.0
ARG VALE_SHA256=c80d62f6bce87b81843ac5b512a26e63213927b957adba0a64fc594570da2000
ARG LYCHEE_VERSION=0.24.2
ARG GIT_CLIFF_VERSION=2.14.2
ARG OSCAL_CLI_VERSION=3.2.0
ARG OSCAL_CLI_SHA256=6d8cf785880f740fd7bc3b170dbb30735800664a69828bc1d82df87d88bc0330
ARG PO4A_VERSION=0.74
ARG OSCAL_VERSION=1.2.3
ARG GH_VERSION=2.104.0

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8

# System packages: Ruby (Asciidoctor), Python, Java (vnu, veraPDF, oscal-cli),
# Pango (WeasyPrint), fonts incl. CJK, Perl modules for po4a.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git make bzip2 xz-utils unzip jq \
      ruby python3 python3-venv default-jre-headless \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
      fonts-dejavu fonts-noto-core fonts-noto-cjk \
      gettext perl libintl-perl libtext-wrapi18n-perl libunicode-linebreak-perl \
      libyaml-tiny-perl libsyntax-keyword-try-perl libpod-parser-perl \
      opensp libsgmls-perl \
    && rm -rf /var/lib/apt/lists/*

RUN gem install --no-document asciidoctor -v "${ASCIIDOCTOR_VERSION}"

COPY requirements.txt /opt/toolbox/requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /opt/toolbox/requirements.txt
ENV PATH=/opt/venv/bin:$PATH

COPY package.json package-lock.json /opt/toolbox/
RUN cd /opt/toolbox && npm ci --no-audit --no-fund \
    && PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers npx playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/* /root/.npm
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers NODE_PATH=/opt/toolbox/node_modules PATH=/opt/toolbox/node_modules/.bin:$PATH

RUN curl -fsSL -o /tmp/vale.tgz "https://github.com/errata-ai/vale/releases/download/v${VALE_VERSION}/vale_${VALE_VERSION}_Linux_64-bit.tar.gz" \
    && echo "${VALE_SHA256}  /tmp/vale.tgz" | sha256sum -c - \
    && tar -xzf /tmp/vale.tgz -C /usr/local/bin vale && rm /tmp/vale.tgz

RUN curl -fsSL "https://github.com/lycheeverse/lychee/releases/download/lychee-v${LYCHEE_VERSION}/lychee-x86_64-unknown-linux-gnu.tar.gz" \
      | tar -xz -C /tmp && install -m 0755 "$(find /tmp -name lychee -type f | head -1)" /usr/local/bin/lychee

RUN curl -fsSL "https://github.com/orhun/git-cliff/releases/download/v${GIT_CLIFF_VERSION}/git-cliff-${GIT_CLIFF_VERSION}-x86_64-unknown-linux-gnu.tar.gz" \
      | tar -xz -C /tmp && install -m 0755 "/tmp/git-cliff-${GIT_CLIFF_VERSION}/git-cliff" /usr/local/bin/git-cliff

RUN curl -fsSL -o /tmp/oscal-cli.tar.bz2 "https://repo1.maven.org/maven2/dev/metaschema/oscal/oscal-cli-enhanced/${OSCAL_CLI_VERSION}/oscal-cli-enhanced-${OSCAL_CLI_VERSION}-oscal-cli.tar.bz2" \
    && echo "${OSCAL_CLI_SHA256}  /tmp/oscal-cli.tar.bz2" | sha256sum -c - \
    && mkdir -p /opt/oscal-cli && tar -xjf /tmp/oscal-cli.tar.bz2 -C /opt/oscal-cli && rm /tmp/oscal-cli.tar.bz2 \
    && ln -s /opt/oscal-cli/bin/oscal-cli /usr/local/bin/oscal-cli

RUN curl -fsSL "https://github.com/mquinson/po4a/releases/download/v${PO4A_VERSION}/po4a-${PO4A_VERSION}.tar.gz" | tar -xz -C /opt \
    && mv "/opt/po4a-${PO4A_VERSION}" /opt/po4a \
    && printf '#!/bin/sh\nexec perl -I/opt/po4a/lib /opt/po4a/po4a "$@"\n' > /usr/local/bin/po4a && chmod +x /usr/local/bin/po4a

# NIST OSCAL JSON schema, pinned by release tag.
RUN mkdir -p /opt/oscal && curl -fsSL -o /opt/oscal/oscal_catalog_schema.json \
      "https://github.com/usnistgov/OSCAL/releases/download/v${OSCAL_VERSION}/oscal_catalog_schema.json"

# GitHub CLI, used by the feedback export/import and release targets.
RUN curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
      | tar -xz -C /tmp && install -m 0755 "/tmp/gh_${GH_VERSION}_linux_amd64/bin/gh" /usr/local/bin/gh

COPY --from=verapdf /opt/verapdf /opt/verapdf
RUN ln -s /opt/verapdf/verapdf /usr/local/bin/verapdf

ENV IN_TOOLBOX=1 HOME=/tmp
WORKDIR /work
