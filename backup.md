# Backup and Recovery

To restore your `ferum_customs` deployment you need:

1. The application source code from the same GitHub commit/tag that is running in production.
2. A recent SQL dump of the site database.
3. The files directory from your Frappe/ERPNext bench, which contains user attachments.

The application stores all business data inside the database. No other persistent state is kept except attachments in the site `files` folder. Keep regular backups of the SQL dump and the files directory. When restoring, deploy the same version of the app, import the database dump and copy the files directory back to `sites/<site-name>/public/files`.

## Automated backups

Create a script `backup.sh` that calls `bench backup --with-files` and moves the archive to external storage:
```bash
#!/bin/bash
cd /home/frappe/frappe-bench
bench --site ${SITE_NAME} backup --with-files
rsync -av sites/${SITE_NAME}/private/backups/ /mnt/backups/${SITE_NAME}/
```
### Cron example
Run daily at 02:00:
```cron
0 2 * * * /home/frappe/backup.sh
```
### systemd timer
Create `/etc/systemd/system/bench-backup.service`:
```ini
[Unit]
Description=Frappe backup

[Service]
Type=oneshot
User=frappe
ExecStart=/home/frappe/backup.sh
```
Create `/etc/systemd/system/bench-backup.timer`:
```ini
[Unit]
Description=Run Frappe backup daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```
Enable and start the timer:
```bash
sudo systemctl enable --now bench-backup.timer
```

