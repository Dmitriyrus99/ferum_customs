# Installation Guide

This document explains how to install the `ferum_customs` app in your Frappe/ERPNext environment.

1. Ensure you have a working [bench](https://github.com/frappe/bench) setup.
2. Clone this repository inside your bench directory:
   ```bash
   bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
   ```
3. Install the application on your site:
   ```bash
   bench --site YOUR_SITE_NAME install-app ferum_customs
   ```
4. Build assets and restart bench:
   ```bash
   bench build && bench restart
   ```

After installation, you should see new DocTypes and customizations available in your ERPNext instance.
