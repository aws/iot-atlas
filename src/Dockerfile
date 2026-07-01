# Simplified Dockerfile for IoT Atlas Hugo site
# No longer needs to compile Hugo from source since PlantUML is handled client-side
ARG HUGO_VERSION=0.163.3

################################################################################
FROM public.ecr.aws/ubuntu/ubuntu:24.04_stable AS base

ARG TARGETARCH
ARG HUGO_VERSION

RUN apt-get update && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl ca-certificates ruby ruby-dev make cmake build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download pre-built Hugo extended binary
RUN curl -fsSL "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-${TARGETARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin hugo

# Install ASCIIDOC support
RUN gem install --no-document asciidoctor asciidoctor-revealjs asciidoctor-html5s \
    rouge asciidoctor-confluence asciidoctor-diagram coderay pygments.rb

################################################################################
ENV DOCUMENT_DIR=/hugo-project

RUN mkdir ${DOCUMENT_DIR}
WORKDIR ${DOCUMENT_DIR}
VOLUME ${DOCUMENT_DIR}

CMD ["hugo", "server", "--bind", "0.0.0.0"]
HEALTHCHECK --interval=2s --timeout=3s \
    CMD curl -f http://localhost:1313/ || exit 1
