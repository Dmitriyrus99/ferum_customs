# Zero-downtime upgrade

To upgrade the application without noticeable downtime:

1. Build new Docker images and start a second set of containers on the same database.
2. Put the old site into maintenance mode:
   ```bash
   bench --site ${SITE_NAME} set-maintenance-mode on
   ```
3. Run database migrations on the new containers:
   ```bash
   bench --site ${SITE_NAME} migrate
   ```
4. Switch traffic to the new containers (for example via load balancer or `docker compose up -d --scale`).
5. Disable maintenance mode:
   ```bash
   bench --site ${SITE_NAME} set-maintenance-mode off
   ```
6. Stop the old containers after verifying the new release is healthy.

Always test migrations on a staging environment before applying them in production.

