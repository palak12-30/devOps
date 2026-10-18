FROM docker:cli AS dockercli

FROM jenkins/jenkins:lts-jdk21
USER root

RUN for lab_source in /etc/apt/sources.list /etc/apt/sources.list.d/*.sources; do \
        if [ -f "$lab_source" ]; then \
            sed -i 's|http://deb.debian.org|https://deb.debian.org|g' "$lab_source"; \
        fi; \
    done \
    && apt-get -o Acquire::Retries=2 -o Acquire::https::Timeout=30 update \
    && DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=2 -o Acquire::https::Timeout=30 install -y --no-install-recommends python3 python3-venv curl git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=dockercli /usr/local/libexec/docker/cli-plugins/ /usr/local/libexec/docker/cli-plugins/

USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator git
