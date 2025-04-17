# Deployment Guide

## Environment Configurations

### Development
```yaml
# values-dev.yaml
database:
  type: sqlite
  path: /data/optin-manager.db

branding:
  logoPath: /config/logo.png

templates:
  configMapName: message-templates-dev

monitoring:
  enabled: false
```

### Production
```yaml
# values-prod.yaml
database:
  type: postgresql
  host: ${POSTGRES_HOST}
  port: 5432
  database: optin_manager
  credentials:
    secretName: postgres-credentials

branding:
  logoPath: /config/logo.png

templates:
  configMapName: message-templates-prod

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
```

## Helm Chart Structure
```
helm/optin-manager/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── serviceaccount.yaml
└── charts/
    └── postgresql/
```

## FluxCD Configuration
```yaml
# optin-manager.yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: optin-manager
  namespace: flux-system
spec:
  interval: 1m
  url: https://your-helm-repo.example.com

---
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: optin-manager
  namespace: messaging
spec:
  interval: 5m
  chart:
    spec:
      chart: optin-manager
      version: "1.x"
      sourceRef:
        kind: HelmRepository
        name: optin-manager
  values:
    replicaCount: 3
    image:
      repository: your-registry/optin-manager
      tag: 1.0.0
```

## Required Secrets

### Database Credentials
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
type: Opaque
stringData:
  username: optin_manager_user
  password: your-secure-password
```

## ConfigMaps

### Message Templates
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: message-templates-prod
data:
  opt-in.txt: |
    Welcome! Reply YES to confirm your subscription to {{service_name}}.
    Msg&Data rates may apply. Reply STOP to cancel.
  
  opt-out.txt: |
    You've been unsubscribed from {{service_name}}. 
    Visit {{opt_in_url}} to resubscribe.
```

### Branding Assets
Store logo and branding assets in a ConfigMap or use a shared volume.

## Database Migration

### Development to Production
1. Use schema migration tools (e.g., Flyway, Liquibase)
2. Keep migration scripts in version control
3. Run migrations as Kubernetes jobs
4. Include rollback procedures

## Monitoring Setup

### Prometheus Metrics
- Message delivery rates
- Opt-in/opt-out rates
- API latency
- Database performance
- Queue depths

### Grafana Dashboards
- System overview
- Message statistics
- User engagement
- Error rates

## Backup and Recovery

### Database Backup
- Use PostgreSQL native backup tools
- Store backups in object storage (e.g., S3, GCS)
- Regular backup schedule
- Point-in-time recovery capability

### Configuration Backup
- Store all configurations in Git
- Use sealed secrets for sensitive data
- Document recovery procedures

## Security Considerations

- Use minimal permission sets for all service accounts
- Regular key rotation for secrets
- Secure API endpoints
- Encrypted storage for sensitive data
