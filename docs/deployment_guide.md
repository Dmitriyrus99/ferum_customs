# Deployment Guide

This document outlines a basic approach to deploy Ferum Customs in Kubernetes using the official helm chart.

## Helm chart
1. Add the frappe helm repository:
   ```bash
   helm repo add frappe https://helm.frappe.io
   helm repo update
   ```
2. Create a `values.yaml` overriding the site name and image tags:
   ```yaml
   site_name: erp.example.com
   apps:
     - ferum_customs
   env:
     - name: FRAPPE_ADMIN_PASSWORD
       value: change_me
   ```
3. Install the release:
   ```bash
   helm install ferum frappe/erpnext -f values.yaml
   ```
This deploys MariaDB, Redis and Frappe workers. Expose the ingress via an ingress controller of your choice.

## Docker Swarm
For a simpler setup you can use Docker Swarm. Convert `docker-compose.yml` to a stack file and deploy:
```bash
docker stack deploy -c docker-compose.yml ferum
```
Make sure the database volume is persistent and attach a reverse proxy (Traefik or Nginx) with TLS termination.

