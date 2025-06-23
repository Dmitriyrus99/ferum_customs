# Backup and Recovery

To restore your `ferum_customs` deployment you need:

1. The application source code from the same GitHub commit/tag that is running in production.
2. A recent SQL dump of the site database.
3. The files directory from your Frappe/ERPNext bench, which contains user attachments.

The application stores all business data inside the database. No other persistent state is kept except attachments in the site `files` folder. Keep regular backups of the SQL dump and the files directory. When restoring, deploy the same version of the app, import the database dump and copy the files directory back to `sites/<site-name>/public/files`.
