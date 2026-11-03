FROM debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
# Pinned official bookworm-slim OCI index, verified in docker-library/repo-info (2026-10-28).

ENV LC_ALL=C
ENV TZ=UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates curl git build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# Instalar Go deterministicamente (pinned version + hash)
ENV GO_VERSION=1.22.3
ENV GO_SHA256=8920ea521bad8f6b7bc377b4824982e011c19af27df88a815e3586ea895f1b36
RUN wget -q https://dl.google.com/go/go${GO_VERSION}.linux-amd64.tar.gz && \
    echo "${GO_SHA256}  go${GO_VERSION}.linux-amd64.tar.gz" | sha256sum -c && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH=/usr/local/go/bin:$PATH

WORKDIR /app
COPY . .
RUN chmod +x build.sh verify.sh

CMD ["./build.sh"]
