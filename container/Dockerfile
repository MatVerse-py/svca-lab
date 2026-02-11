FROM debian@sha256:2a0c9e1b8f0d7a4f0f9c8c9a6c8a6e4c2f5b6d7a9e0b1c2d3e4f5a6b7c8d9e0

ENV LC_ALL=C
ENV TZ=UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates curl git build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# Instalar Go deterministicamente (pinned version + hash)
ENV GO_VERSION=1.22.3
ENV GO_SHA256=8920ea521bad8f6b7bc377b482498c1ad3226a1970d573a287d9a7fcdb0625d5
RUN wget -q https://dl.google.com/go/go${GO_VERSION}.linux-amd64.tar.gz && \
    echo "${GO_SHA256}  go${GO_VERSION}.linux-amd64.tar.gz" | sha256sum -c && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH=/usr/local/go/bin:$PATH

WORKDIR /app
COPY . .
RUN chmod +x build.sh verify.sh

CMD ["./build.sh"]
