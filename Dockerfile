# ---------- builder ----------
ARG BENCH_TAG=v5.25.9
FROM frappe/bench:${BENCH_TAG} AS builder

ARG FRAPPE_BRANCH=version-15
ARG ERPNEXT_BRANCH=version-15

# 1) Устанавливаем redis-server для bench init
USER root
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-server rclone \
 && rm -rf /var/lib/apt/lists/*
USER frappe

WORKDIR /home/frappe

# 2) bench init (обязательно путь в конце)
RUN bench init --skip-assets \
    --frappe-branch "${FRAPPE_BRANCH}" \
    --python python3 \
    frappe-bench

WORKDIR /home/frappe/frappe-bench

# 3) ERPNext
RUN bench get-app --branch "${ERPNEXT_BRANCH}" erpnext https://github.com/frappe/erpnext --resolve-deps

# 4) Кастомное приложение
COPY --chown=frappe:frappe . apps/ferum_customs
RUN cd apps/ferum_customs \
 && git init \
 && git config user.email "build@local" \
 && git config user.name "build" \
 && git add -A \
 && git commit -m "docker build commit"

# 5) Зависимости
RUN bench setup requirements frappe erpnext ferum_customs

# 6) Сборка ассетов (не критично)
RUN bench build || true

# ---------- runtime ----------
FROM frappe/bench:${BENCH_TAG} AS runtime
WORKDIR /home/frappe/frappe-bench

COPY --from=builder /home/frappe/frappe-bench /home/frappe/frappe-bench

COPY --chown=frappe:frappe docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY --chown=frappe:frappe docker/wait_for_db.sh /usr/local/bin/wait_for_db.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/wait_for_db.sh

VOLUME ["/home/frappe/frappe-bench/sites"]
EXPOSE 8000 9000

CMD ["/usr/local/bin/docker-entrypoint.sh", "bench", "start"]
