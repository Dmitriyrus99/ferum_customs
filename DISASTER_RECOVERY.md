# Disaster Recovery Plan

## 1. Restore from backup

1.  Restore the latest backup from Google Drive to the `frappe-bench/sites/erp.ferumrus.ru/private/backups` directory.
2.  Run `docker-compose exec -T frappe bench restore --with-public-files /path/to/backup.sql --with-private-files /path/to/private-files.zip`

## 2. Rebuild the environment

1.  Clone the repository.
2.  Create a `.env` file from `.env.example`.
3.  Run `docker-compose up -d --build`.
4.  Restore the database from backup (see above).
