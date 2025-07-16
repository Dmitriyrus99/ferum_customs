ARG BENCH_TAG=v5.25.4
FROM frappe/bench:${BENCH_TAG} AS builder
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf || true

# Build stage: initialize bench and install app dependencies

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe
RUN bench init --skip-assets frappe-bench --python python3
WORKDIR /home/frappe/frappe-bench

RUN bench get-app ferum_customs https://github.com/Dmitriyrus99/ferum_customs.git
RUN bench setup requirements

### Runtime stage ###
FROM frappe/bench:${BENCH_TAG}
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf || true
LABEL org.opencontainers.image.source="https://github.com/<owner>/ferum_customs"
LABEL org.opencontainers.image.licenses="MIT"

# Runtime dependencies
USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER frappe
# Copy built bench and app from builder stage
COPY --chown=frappe:frappe --from=builder /home/frappe/frappe-bench /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench
