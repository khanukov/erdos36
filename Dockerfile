FROM ubuntu:24.04
# Convenience environment only; the mutable base/apt snapshot is not part of
# the mathematical proof or a claim of bit-for-bit reproducibility.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgmp-dev libmpfr-dev python3 python3-pip ca-certificates curl \
    latexmk texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY . /work
CMD ["make", "verify"]
