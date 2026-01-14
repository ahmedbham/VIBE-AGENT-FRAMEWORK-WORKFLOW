# Azure Container Apps Deployment - Quick Reference

Quick commands for deploying the Website Summarizer Workflow to Azure Container Apps.

## Prerequisites Checklist

- [ ] Azure CLI installed and logged in (`az login`)
- [ ] Docker installed (for local testing)
- [ ] Azure Developer CLI installed (for azd approach)
- [ ] Azure subscription with appropriate permissions
- [ ] Azure OpenAI/Foundry endpoint and model deployed

## Quick Start - Azure Developer CLI (azd)

The fastest way to deploy:

```bash
# 1. Login to Azure
azd auth login

# 2. Initialize (first time only)
azd init

# 3. Set required environment variables
azd env set FOUNDRY_ENDPOINT "https://your-foundry.services.ai.azure.com"
azd env set AZURE_OPENAI_DEPLOYMENT "gpt-4.1-mini"
azd env set AZURE_OPENAI_CHAT_DEPLOYMENT_NAME "gpt-4.1-mini"
azd env set AZURE_OPENAI_API_VERSION "2024-10-21"

# 4. Deploy everything (infrastructure + app)
azd up
```

## Quick Start - GitHub Actions

### Initial Setup

```bash
# 1. Create service principal
az ad sp create-for-rbac \
  --name "website-summarizer-sp" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth

# 2. Add secrets to GitHub (from step 1 output)
# - AZURE_CLIENT_ID
# - AZURE_TENANT_ID
# - AZURE_SUBSCRIPTION_ID
# - FOUNDRY_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT
# - AZURE_OPENAI_API_VERSION

# 3. Create initial infrastructure (see DEPLOYMENT_GUIDE.md)

# 4. Push to main branch or trigger workflow manually
```

## Common Commands

### Azure Container Apps

```bash
# View app status
az containerapp show \
  --name <app-name> \
  --resource-group <resource-group> \
  --query "properties.{Status:runningStatus, URL:configuration.ingress.fqdn}"

# View logs
az containerapp logs show \
  --name <app-name> \
  --resource-group <resource-group> \
  --follow

# Update environment variables
az containerapp update \
  --name <app-name> \
  --resource-group <resource-group> \
  --set-env-vars KEY=VALUE

# Scale app
az containerapp update \
  --name <app-name> \
  --resource-group <resource-group> \
  --min-replicas 0 \
  --max-replicas 5

# Restart app
az containerapp revision restart \
  --name <app-name> \
  --resource-group <resource-group>
```

### Azure Developer CLI (azd)

```bash
# Deploy infrastructure only
azd provision

# Deploy application only
azd deploy

# Deploy everything
azd up

# View outputs
azd env get-values

# Monitor
azd monitor

# Clean up
azd down
```

### Docker

```bash
# Build image
docker build -t website-summarizer:latest .

# Test locally
docker run -it --rm \
  -e FOUNDRY_ENDPOINT="your-endpoint" \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini" \
  -e AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4.1-mini" \
  -e AZURE_OPENAI_API_VERSION="2024-10-21" \
  website-summarizer:latest

# Push to ACR
az acr login --name <registry-name>
docker tag website-summarizer:latest <registry-name>.azurecr.io/website-summarizer:latest
docker push <registry-name>.azurecr.io/website-summarizer:latest
```

## Resource Names Convention

Following Azure naming best practices:

| Resource Type | Prefix | Example |
|---------------|--------|---------|
| Resource Group | `rg-` | `rg-website-summarizer-dev` |
| Container Registry | `cr` | `crwebsummarizerdev` |
| Log Analytics | `log-` | `log-website-summarizer-dev` |
| Container Apps Environment | `cae-` | `cae-website-summarizer-dev` |
| Container App | `ca-` | `ca-website-summarizer-dev` |

## Environment Variables

Required for the application:

```bash
FOUNDRY_ENDPOINT=https://your-foundry.services.ai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-10-21
```

## Troubleshooting Quick Fixes

```bash
# App not starting - check logs
az containerapp logs show --name <app> --resource-group <rg> --follow

# Authentication issues - verify managed identity
az containerapp show --name <app> --resource-group <rg> --query identity

# Image not found - check ACR
az acr repository list --name <registry> --output table

# Environment variables - verify configuration
az containerapp show --name <app> --resource-group <rg> \
  --query "properties.template.containers[0].env"

# Restart container app
az containerapp revision restart --name <app> --resource-group <rg>
```

## Cost Optimization

```bash
# Scale to zero when idle
az containerapp update \
  --name <app> \
  --resource-group <rg> \
  --min-replicas 0

# Use consumption plan (default in Container Apps)
# Delete unused resources regularly
az group delete --name <rg> --yes
```

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-to-aca.yml       # GitHub Actions CI/CD
├── infra/
│   ├── main.bicep                  # Main infrastructure template
│   ├── main.parameters.json        # Bicep parameters
│   ├── abbreviations.json          # Resource naming conventions
│   └── modules/
│       ├── container-registry.bicep
│       ├── log-analytics.bicep
│       ├── container-apps-environment.bicep
│       └── container-app.bicep
├── src/
│   └── joker_agent/
│       └── ...                     # Application code
├── Dockerfile                      # Container definition
├── .dockerignore                   # Docker build exclusions
├── azure.yaml                      # azd configuration
├── pyproject.toml                  # Python dependencies
└── DEPLOYMENT_GUIDE.md             # Comprehensive guide
```

## Useful Links

- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Azure Container Apps Docs](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)

## Getting Help

1. Check logs: `az containerapp logs show --follow`
2. Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) troubleshooting section
3. Verify environment variables and managed identity
4. Test Docker image locally before deploying
5. Check Azure Portal for resource status

---

For detailed instructions, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
