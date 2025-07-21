# Dockerfile for ERPNext with Ferum Customs app
ARG BENCH_TAG=v5.25.4
ARG ERPNEXT_BRANCH=version-15
FROM frappe/bench:${BENCH_TAG} AS builder

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-server \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe

# Initialize bench environment
RUN bench init --skip-assets frappe-bench --python python3
WORKDIR /home/frappe/frappe-bench

# Clone ERPNext application
RUN if [ "${ERPNEXT_BRANCH}" = "erpnext" ]; then \
      bench get-app erpnext https://github.com/frappe/erpnext; \
    else \
      bench get-app --branch ${ERPNEXT_BRANCH} erpnext https://github.com/frappe/erpnext; \
    fi

# Add local Ferum Customs custom app
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/ferum_customs
RUN bench setup requirements

### Runtime image ###
FROM frappe/bench:${BENCH_TAG}
LABEL org.opencontainers.image.source="https://github.com/Dmitriyrus99/ferum_customs"
LABEL org.opencontainers.image.licenses="MIT"

USER frappe
# Copy built bench directory from builder stage
COPY --chown=frappe:frappe --from=builder /home/frappe/frappe-bench /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench
