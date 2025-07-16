ARG BENCH_TAG=v5.25.4
FROM frappe/bench:${BENCH_TAG}
LABEL org.opencontainers.image.source="https://github.com/<owner>/ferum_customs"
LABEL org.opencontainers.image.licenses="MIT"

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-server \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe
RUN bench init --skip-assets frappe-bench --python $(which python)
WORKDIR /home/frappe/frappe-bench

COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/ferum_customs
RUN bench setup requirements
