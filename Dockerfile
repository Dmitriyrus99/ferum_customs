
ARG BENCH_TAG=v5.25.4
FROM frappe/bench:${BENCH_TAG} AS builder

USER root
# Install required packages for bench; Redis server runs as a separate service
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-server \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe
RUN bench init --skip-assets frappe-bench --python python3
WORKDIR /home/frappe/frappe-bench

# Используйте ветку, соответствующую вашей версии Frappe.
# Так как BENCH_TAG=v5.25.4, это соответствует Frappe v15.
RUN bench get-app erpnext https://github.com/frappe/erpnext.git --branch version-15

# Установка вашего кастомного приложения
RUN bench get-app ferum_customs https://github.com/Dmitriyrus99/ferum_customs.git --branch main

# Устанавливаем все требования после получения всех приложений
RUN bench setup requirements

### Runtime stage ###
# Runtime stage
# Runtime stage
FROM frappe/bench:${BENCH_TAG}
LABEL org.opencontainers.image.source="https://github.com/<owner>/ferum_customs"
LABEL org.opencontainers.image.licenses="MIT"

USER frappe
# Copy built bench and app from builder stage
COPY --chown=frappe:frappe --from=builder /home/frappe/frappe-bench /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench
