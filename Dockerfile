# Local compiler/test runner; this project contains no runtime application.
FROM python:3.12-slim-bookworm

ARG TARGETARCH
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl libicu72 \
    && rm -rf /var/lib/apt/lists/* \
    && case "$TARGETARCH" in amd64) bicep_arch=x64 ;; arm64) bicep_arch=arm64 ;; *) exit 1 ;; esac \
    && curl --fail --silent --show-error --location --retry 3 \
       "https://github.com/Azure/bicep/releases/download/v0.37.4/bicep-linux-${bicep_arch}" \
       --output /usr/local/bin/bicep \
    && chmod +x /usr/local/bin/bicep \
    && bicep --version

WORKDIR /workspace
COPY . .
CMD ["bash", "scripts/check.sh"]
