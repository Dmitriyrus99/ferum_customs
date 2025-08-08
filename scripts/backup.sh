#!/bin/bash
cd /home/user/ferum_customs
docker-compose exec -T frappe bench backup
docker-compose exec -T frappe rclone copy /home/frappe/frappe-bench/sites/erp.ferumrus.ru/private/backups gdrive:ferum_customs_backups
