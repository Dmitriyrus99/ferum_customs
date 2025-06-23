# Simple Dockerfile for running ferum_customs with bench
FROM python:3.10-slim

ENV FRAPPE_PATH=/home/frappe
WORKDIR ${FRAPPE_PATH}

# Install bench and dependencies
RUN pip install frappe-bench && \
    apt-get update && apt-get install -y mariadb-client redis-tools && \
    rm -rf /var/lib/apt/lists/*

# Initialize bench
RUN bench init --skip-redis-config-generation --skip-assets --python $(which python) frappe-bench

WORKDIR ${FRAPPE_PATH}/frappe-bench

# Copy app into bench apps directory
COPY . apps/ferum_customs

# Install app requirements and build assets
RUN bench setup requirements --dev && \
    bench new-site --db-root-password root --admin-password admin test_site && \
    bench --site test_site install-app ferum_customs && \
    bench build

CMD ["bench", "start"]
