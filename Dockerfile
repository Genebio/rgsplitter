FROM python:3.11-bullseye

LABEL org.opencontainers.image.authors="genebio91@gmail.com"

RUN apt-get update && \
    apt-get --yes --no-install-recommends install pigz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV SEQKIT_VERSION v2.6.1
ENV SEQKIT_DIR /opt/seqkit

WORKDIR ${SEQKIT_DIR}
ENV PATH="$PATH:${SEQKIT_DIR}"
RUN wget --no-cache -q https://github.com/shenwei356/seqkit/releases/download/${SEQKIT_VERSION}/seqkit_linux_amd64.tar.gz && \
    tar -zxvf seqkit_linux_amd64.tar.gz && \
    rm seqkit_linux_amd64.tar.gz

WORKDIR /usr/local/src

COPY run.py ./

ENTRYPOINT ["/usr/local/bin/python3.11","/usr/local/src/run.py"]
