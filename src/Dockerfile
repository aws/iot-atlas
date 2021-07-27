# Version of Hugo to build.
# NOTE: For now, version 0.82.0 needed until hard-coded files for PlantUML addressed
ARG HUGO_VERSION=0.82.0

################################################################################
FROM public.ecr.aws/ubuntu/ubuntu:20.04_stable AS base

RUN apt-get update && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl ruby ruby-dev make cmake build-essential bison flex graphviz \
    openjdk-11-jre python git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

################################################################################
# Build hugo executable using golang
FROM base AS builder

# Version of golang to build.
ARG GO_VERSION=1.16.3

ARG HUGO_VERSION

ENV PATH="${PATH}:/usr/local/go/bin"
WORKDIR /tmp

# Install golang
RUN curl -JLO https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz

# Configure GOPROXY if passed in as build argument
ARG GOPROXY
RUN (test -n "$GOPROXY" && go env -w GOPROXY="${GOPROXY}") || true

# Download Hugo source
RUN curl -JLO https://github.com/gohugoio/hugo/archive/refs/tags/v${HUGO_VERSION}.tar.gz \
    && tar xzf hugo-${HUGO_VERSION}.tar.gz

# Prepare source file changes
# Hard-coded files for now, specific to Hugo 0.82.0
COPY ./docker_assets/convert.go /tmp/hugo-${HUGO_VERSION}/markup/goldmark/convert.go
COPY ./docker_assets/config.go /tmp/hugo-${HUGO_VERSION}/markup/goldmark/goldmark_config/config.go

# Download dependencies (with a single retry to catch timeouts) and compile Hugo
ARG GOLDMARK_PLANTUML="github.com/OhYee/goldmark-plantuml@v1.0.3"
RUN cd hugo-${HUGO_VERSION} \
    && (go get ${GOLDMARK_PLANTUML} || go get ${GOLDMARK_PLANTUML}) \
    && go install --tags extended \
    && mv $HOME/go/bin/hugo /hugo

################################################################################
# Build the operational container
FROM base
ENV DOCUMENT_DIR=/hugo-project
COPY --from=builder /hugo /usr/local/bin

# Install plantuml
RUN mkdir -p /opt/plantuml && cd /opt/plantuml \
    && UML=http://sourceforge.net/projects/plantuml/files/plantuml.jar/download \
    && curl -JLO ${UML}
COPY ./docker_assets/plantuml /usr/local/bin/plantuml
RUN chmod a+x /usr/local/bin/plantuml

# install ASCIIDOC support
RUN gem install --no-document asciidoctor asciidoctor-revealjs asciidoctor-html5s \
    rouge asciidoctor-confluence asciidoctor-diagram coderay pygments.rb

RUN mkdir ${DOCUMENT_DIR}
WORKDIR ${DOCUMENT_DIR}

VOLUME ${DOCUMENT_DIR}
ENV CLASSPATH=/opt/plantuml
ENV PATH=${DOCUMENT_DIR}:$PATH
CMD ["hugo", "server", "--bind", "0.0.0.0"]

HEALTHCHECK --interval=2s --timeout=3s \
    CMD curl -f http://localhost:1313/ || exit 1
