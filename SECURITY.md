# Security Policy

All security vulnerabilities should be reported via email to [support@ferum.ru](mailto:support@ferum.ru). We will respond as soon as possible.

Please do not disclose security issues publicly until they have been investigated and patched.

## Compatibility

This app has been tested with **Frappe/ERPNext 15.0**. Installing on other major versions may require additional testing.

## Security Features

- **Audit Trail:** All DocTypes enable the *Track Changes* option so that every update is stored in the standard `Version` DocType.
- **Error Logging:** Critical events are written to the built‑in *Error Log*.
- **Role Based Permissions:** Permissions and workflows restrict actions to roles such as *Проектный менеджер* and *Инженер*.
- **Dynamic Queries:** Additional permission query conditions limit records visible to users with the *Заказчик* role.

## Administrator Checklist

1. Install the app with `bench install-app ferum_customs` or add it to your Docker image (see below).
2. Log in as **Administrator** and open **Role List**. Ensure that the roles `Проектный менеджер`, `Инженер` and `Заказчик` exist and assign them to the appropriate users.
3. Review the **Service Request Workflow** and adjust states or transitions if required.
4. Monitor the *Error Log* for security related messages.

## Production Notes

For production deployments run `bench setup production` to enable process managers and serve the site over HTTPS. Keep your bench environment and the app up to date with regular updates.

## Docker Setup

If you use the official Frappe Docker images, add `ferum_customs` to `apps.txt` (or `apps.json` for multi-app setups) and rebuild the image. Example:

```bash
# apps.txt
frappe
erpnext
ferum_customs
```

After rebuilding, run `bench --site <your-site> install-app ferum_customs` inside the container.
