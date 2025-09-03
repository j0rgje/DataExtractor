# Production Best Practices for HSO Data Extractor

This document summarizes practical steps to run this app reliably and securely in production on Azure.

Key principles:
- Config via environment (App Settings), never commit secrets. Use Azure Key Vault + Managed Identity.
- Separate environments (dev/staging/prod) with isolated resources.
- Observability first: metrics, logs, alerts.

1) Configuration & Secrets
- Use App Settings: ENV=production, USE_MOCK_AZURE=false, AZURE_FUNCTION_URL, AZURE_STORAGE_ACCOUNT.
- Store secrets (Function keys, CV keys, storage connection) in Key Vault.
- Grant the app (App Service/Container) a system-assigned Managed Identity with Get/List on the needed secrets.
- Optional: use Azure App Configuration for feature flags and centralized settings.

2) Networking & Security
- Restrict Storage and Function App with Private Endpoints or at least IP Allow Lists.
- Enforce HTTPS only. Set CORS appropriately for the Streamlit frontend.
- Enable AAD authentication for Function App where possible; rotate keys regularly if used.
- Turn on diagnostic logs and resource logs for auditing.

3) Reliability & Scaling
- Use Azure Functions Consumption or Premium plan; set min instances for cold start reduction if needed.
- Configure retries with exponential backoff for outbound calls.
- Add health checks and simple smoke tests post-deploy.

4) Monitoring
- Enable Application Insights for Functions; log custom events for document lifecycle.
- Set alerts: failure rate, latency, function errors, storage capacity.
- Use Log Analytics for centralized queries and dashboards.

5) CI/CD
- Build: run unit tests, lint, and security scans.
- Release: deploy infra (Bicep/ARM/Terraform) first, then app code.
- Use environment-specific variables; no hard-coded endpoints.

6) Operations
- Backups: use GRS for Storage and point-in-time restore where applicable.
- Runbooks for incident response, key rotation, and data retention.
- Cost governance with budgets and alerts.

7) Streamlit runtime
- Configure server.port via APP_PORT setting; prefer reverse proxy or App Service ingress.
- Set LOG_LEVEL to INFO in production; DEBUG should be false.
- Disable usage stats collection if not needed.

See docs/azure_architecture.md for architecture details.
