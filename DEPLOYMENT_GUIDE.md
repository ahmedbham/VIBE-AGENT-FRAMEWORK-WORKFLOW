# Deployment Guide: Website Summarizer Workflow to Azure Container Apps

This guide provides detailed instructions for deploying the Website Summarizer Workflow to Azure Container Apps (ACA) using two approaches:
1. **GitHub Actions** - Automated CI/CD pipeline
2. **Azure Developer CLI (azd)** - Command-line deployment tool

## Table of Contents
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Approach 1: GitHub Actions](#deployment-approach-1-github-actions)
- [Deployment Approach 2: Azure Developer CLI (azd)](#deployment-approach-2-azure-developer-cli-azd)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Clean Up Resources](#clean-up-resources)

## Prerequisites

### Required Tools
- **Azure CLI** (version 2.50.0 or later)
  ```bash
  az --version
  ```
  Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

- **Docker** (for local testing)
  ```bash
  docker --version
  ```
  Install from: https://docs.docker.com/get-docker/

- **Azure Developer CLI (azd)** (for azd approach)
  ```bash
  azd version
  ```
  Install from: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd

- **Git**
  ```bash
  git --version
  ```

### Azure Requirements
- Active Azure subscription
- Sufficient permissions to create:
  - Resource Groups
  - Container Registry
  - Container Apps
  - Log Analytics Workspace
  - Managed Identities
- Azure OpenAI or Azure AI Foundry endpoint with deployed model

### Required Information
Before deploying, gather the following:
- **Foundry Endpoint URL**: Your Azure OpenAI or Foundry endpoint (e.g., `https://your-foundry.services.ai.azure.com`)
- **Model Deployment Name**: Name of your deployed model (e.g., `gpt-4.1-mini`)
- **API Version**: Azure OpenAI API version (e.g., `2024-10-21`)

## Architecture Overview

The deployment creates the following Azure resources:

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Subscription                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Resource Group                           │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │   Azure Container Registry (ACR)                │ │  │
│  │  │   - Stores Docker images                        │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │   Log Analytics Workspace                       │ │  │
│  │  │   - Collects logs and metrics                   │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │   Container Apps Environment                    │ │  │
│  │  │   - Hosts container apps                        │ │  │
│  │  │   ┌───────────────────────────────────────────┐ │ │  │
│  │  │   │  Website Summarizer Container App        │ │ │  │
│  │  │   │  - Python application                    │ │ │  │
│  │  │   │  - Managed Identity enabled              │ │ │  │
│  │  │   │  - Environment variables configured      │ │ │  │
│  │  │   └───────────────────────────────────────────┘ │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components
- **Container Registry**: Stores the Docker image of the application
- **Container Apps Environment**: Provides the runtime environment with networking and scaling
- **Container App**: Runs the Website Summarizer Workflow application
- **Log Analytics**: Captures application logs and telemetry
- **Managed Identity**: Enables secure authentication to Azure services

## Deployment Approach 1: GitHub Actions

GitHub Actions provides automated CI/CD for continuous deployment.

### Step 1: Set Up Azure Service Principal

Create a service principal with appropriate permissions:

```bash
# Set variables
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
RESOURCE_GROUP="rg-website-summarizer"
APP_NAME="website-summarizer-sp"

# Create service principal
az ad sp create-for-rbac \
  --name $APP_NAME \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth
```

Save the JSON output - you'll need it for GitHub secrets.

### Step 2: Create Azure Resources (Initial Setup)

First, provision the infrastructure using azd or manually:

```bash
# Login to Azure
az login

# Set variables
LOCATION="eastus"
ENVIRONMENT_NAME="dev"

# Create resource group
az group create \
  --name rg-website-summarizer-$ENVIRONMENT_NAME \
  --location $LOCATION

# Create Container Registry
REGISTRY_NAME="crwebsummarizer${ENVIRONMENT_NAME}"
az acr create \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --name $REGISTRY_NAME \
  --sku Basic \
  --admin-enabled true

# Create Log Analytics Workspace
WORKSPACE_NAME="log-website-summarizer-${ENVIRONMENT_NAME}"
az monitor log-analytics workspace create \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --workspace-name $WORKSPACE_NAME \
  --location $LOCATION

# Get workspace IDs
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --workspace-name $WORKSPACE_NAME \
  --query customerId -o tsv)

WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --workspace-name $WORKSPACE_NAME \
  --query primarySharedKey -o tsv)

# Create Container Apps Environment
ENV_NAME="cae-website-summarizer-${ENVIRONMENT_NAME}"
az containerapp env create \
  --name $ENV_NAME \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --location $LOCATION \
  --logs-workspace-id $WORKSPACE_ID \
  --logs-workspace-key $WORKSPACE_KEY

# Create Container App (initial deployment)
APP_NAME="ca-website-summarizer-${ENVIRONMENT_NAME}"
az containerapp create \
  --name $APP_NAME \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --environment $ENV_NAME \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 8000 \
  --ingress internal \
  --cpu 0.5 \
  --memory 1Gi \
  --min-replicas 0 \
  --max-replicas 1 \
  --registry-server ${REGISTRY_NAME}.azurecr.io \
  --system-assigned
```

### Step 3: Configure GitHub Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AZURE_CLIENT_ID` | Service Principal Client ID | From Step 1 JSON output |
| `AZURE_TENANT_ID` | Azure Tenant ID | From Step 1 JSON output |
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID | From Step 1 JSON output |
| `AZURE_CONTAINER_REGISTRY` | Container Registry name (without .azurecr.io) | `crwebsummarizerdev` |
| `AZURE_RESOURCE_GROUP` | Resource Group name | `rg-website-summarizer-dev` |
| `CONTAINER_APP_NAME` | Container App name | `ca-website-summarizer-dev` |
| `FOUNDRY_ENDPOINT` | Azure OpenAI Foundry endpoint | `https://your-foundry.services.ai.azure.com` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4.1-mini` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-10-21` |

### Step 4: Configure Federated Credentials (for OIDC)

For enhanced security using OpenID Connect:

```bash
# Get the Application (client) ID
APP_ID=$(az ad sp list --display-name $APP_NAME --query [0].appId -o tsv)

# Create federated credential for main branch
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-main-branch",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_GITHUB_ORG/YOUR_REPO:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Create federated credential for pull requests
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-pull-requests",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_GITHUB_ORG/YOUR_REPO:pull_request",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

Replace `YOUR_GITHUB_ORG/YOUR_REPO` with your repository path.

### Step 5: Trigger Deployment

The GitHub Actions workflow (`.github/workflows/deploy-to-aca.yml`) will automatically trigger on:
- Push to `main` branch
- Manual workflow dispatch

To manually trigger:
1. Go to GitHub repository → Actions
2. Select "Deploy Website Summarizer to Azure Container Apps"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

### Step 6: Monitor Deployment

1. **GitHub Actions Tab**: Watch the workflow execution in real-time
2. **Azure Portal**: Monitor Container App deployment status
3. **Logs**: View application logs in Log Analytics

```bash
# View Container App logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group rg-website-summarizer-$ENVIRONMENT_NAME \
  --follow
```

## Deployment Approach 2: Azure Developer CLI (azd)

Azure Developer CLI (azd) provides a streamlined deployment experience.

### Step 1: Install Azure Developer CLI

```bash
# macOS/Linux
curl -fsSL https://aka.ms/install-azd.sh | bash

# Windows (PowerShell)
powershell -ex AllSigned -c "Invoke-RestMethod 'https://aka.ms/install-azd.ps1' | Invoke-Expression"

# Verify installation
azd version
```

### Step 2: Initialize Environment

Navigate to the repository root and initialize azd:

```bash
cd /path/to/VIBE-AGENT-FRAMEWORK-WORKFLOW

# Login to Azure
azd auth login

# Initialize environment (first time only)
azd init

# When prompted:
# - Environment name: dev (or your preferred name)
# - Subscription: Select your Azure subscription
# - Location: Select your preferred region (e.g., eastus)
```

This creates a `.azure` directory with your environment configuration.

### Step 3: Set Environment Variables

Create or update `.azure/<environment-name>/.env` file:

```bash
# Required environment variables
FOUNDRY_ENDPOINT="https://your-foundry.services.ai.azure.com"
AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini"
AZURE_OPENAI_API_VERSION="2024-10-21"

# Optional: Override default names
AZURE_LOCATION="eastus"
AZURE_ENV_NAME="dev"
```

Or set them using azd:

```bash
azd env set FOUNDRY_ENDPOINT "https://your-foundry.services.ai.azure.com"
azd env set AZURE_OPENAI_DEPLOYMENT "gpt-4.1-mini"
azd env set AZURE_OPENAI_API_VERSION "2024-10-21"
```

### Step 4: Provision Infrastructure

Provision all Azure resources defined in the Bicep templates:

```bash
# Provision infrastructure
azd provision

# This will:
# 1. Deploy the Bicep templates
# 2. Create all Azure resources
# 3. Output resource details
```

The provision command creates:
- Resource Group
- Container Registry
- Log Analytics Workspace
- Container Apps Environment
- Container App (initial placeholder)

### Step 5: Deploy Application

Build and deploy the Docker container:

```bash
# Deploy application
azd deploy

# This will:
# 1. Build the Docker image
# 2. Push to Azure Container Registry
# 3. Update the Container App with new image
```

### Step 6: Access Application

After deployment, azd outputs the application URL:

```bash
# View environment variables and outputs
azd env get-values

# Get specific output
azd env get-value WEBSITE_SUMMARIZER_APP_URL
```

### Step 7: Update and Redeploy

To update the application:

```bash
# Make code changes...

# Redeploy (builds and pushes new image)
azd deploy

# To redeploy everything (infrastructure + app)
azd up
```

### Step 8: Monitor and Debug

```bash
# View deployment status
azd monitor

# Stream logs (if configured)
azd monitor --logs

# SSH into container (for debugging)
az containerapp exec \
  --name ca-website-summarizer-<env-name> \
  --resource-group rg-website-summarizer-<env-name> \
  --command /bin/bash
```

## Configuration

### Environment Variables

The application requires the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FOUNDRY_ENDPOINT` | Azure OpenAI/Foundry endpoint URL | Yes | - |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | Yes | `gpt-4.1-mini` |
| `AZURE_OPENAI_API_VERSION` | API version | Yes | `2024-10-21` |

### Container App Configuration

Default configuration (can be modified in `infra/modules/container-app.bicep`):

- **CPU**: 0.5 cores
- **Memory**: 1 GiB
- **Min Replicas**: 0 (scales to zero when idle)
- **Max Replicas**: 1
- **Ingress**: Internal (not publicly accessible)
- **Target Port**: 8000

To modify:

```bash
# Update CPU and memory
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --cpu 1.0 \
  --memory 2Gi

# Update scaling
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 5

# Enable external ingress (make publicly accessible)
az containerapp ingress update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --type external
```

### Authentication

The application uses Azure Managed Identity for authentication to Azure OpenAI/Foundry.

#### Automated Configuration (Recommended)

To automatically grant the necessary permissions during deployment, set the `FOUNDRY_RESOURCE_ID` environment variable:

```bash
# Get your Foundry resource ID
FOUNDRY_RESOURCE_ID=$(az ml workspace show \
  --name <your-foundry-name> \
  --resource-group <foundry-resource-group> \
  --query id -o tsv)

# For azd deployment
azd env set FOUNDRY_RESOURCE_ID "$FOUNDRY_RESOURCE_ID"
azd provision  # or azd up

# For Azure CLI deployment
az deployment sub create \
  --location <location> \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json \
  --parameters foundryResourceId="$FOUNDRY_RESOURCE_ID"
```

The Bicep template will automatically grant the "Cognitive Services OpenAI User" role to the container app's managed identity.

#### Manual Configuration (Post-Deployment)

If you prefer to grant permissions after deployment, or if you didn't set `FOUNDRY_RESOURCE_ID` during deployment:

1. **Get the Managed Identity Principal ID**:
   ```bash
   PRINCIPAL_ID=$(az containerapp show \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --query identity.principalId -o tsv)
   ```

2. **Grant permissions to Azure AI Foundry**:
   ```bash
   # Get your Foundry resource ID
   FOUNDRY_RESOURCE_ID=$(az ml workspace show \
     --name <your-foundry-name> \
     --resource-group <foundry-resource-group> \
     --query id -o tsv)
   
   # Grant the role
   az role assignment create \
     --assignee $PRINCIPAL_ID \
     --role "Cognitive Services OpenAI User" \
     --scope $FOUNDRY_RESOURCE_ID
   ```

For detailed manual configuration steps, including troubleshooting, see [MANUAL_CONFIGURATION_STEPS.md](MANUAL_CONFIGURATION_STEPS.md).

## Verification

### 1. Verify Infrastructure

```bash
# List all resources in the resource group
az resource list \
  --resource-group rg-website-summarizer-dev \
  --output table

# Check Container App status
az containerapp show \
  --name ca-website-summarizer-dev \
  --resource-group rg-website-summarizer-dev \
  --query "properties.{Status:runningStatus, Health:health, URL:configuration.ingress.fqdn}" \
  --output table
```

### 2. Test Docker Image Locally

Before deploying, test the Docker image locally:

```bash
# Build image
docker build -t website-summarizer:test .

# Run container
docker run -it --rm \
  -e FOUNDRY_ENDPOINT="your-endpoint" \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini" \
  -e AZURE_OPENAI_API_VERSION="2024-10-21" \
  website-summarizer:test

# For interactive testing
docker run -it --rm \
  -e FOUNDRY_ENDPOINT="your-endpoint" \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini" \
  -e AZURE_OPENAI_API_VERSION="2024-10-21" \
  website-summarizer:test \
  /bin/bash
```

### 3. View Application Logs

```bash
# Stream logs
az containerapp logs show \
  --name ca-website-summarizer-dev \
  --resource-group rg-website-summarizer-dev \
  --follow

# Query logs in Log Analytics
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(1h) | order by TimeGenerated desc" \
  --output table
```

### 4. Test Application Functionality

If ingress is enabled as external:

```bash
# Get the app URL
APP_URL=$(az containerapp show \
  --name ca-website-summarizer-dev \
  --resource-group rg-website-summarizer-dev \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Test (if you've exposed an HTTP endpoint)
curl https://$APP_URL
```

## Troubleshooting

### Common Issues

#### 1. Image Pull Failures

**Error**: "Failed to pull image from registry"

**Solutions**:
```bash
# Verify Container Registry credentials
az acr credential show \
  --name $REGISTRY_NAME

# Check if image exists
az acr repository list \
  --name $REGISTRY_NAME \
  --output table

# Verify Container App can access registry
az containerapp registry list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

#### 2. Authentication Errors

**Error**: "Failed to authenticate to Azure OpenAI"

**Solutions**:
```bash
# Verify managed identity is enabled
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query identity

# Check role assignments
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --output table

# Verify environment variables
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env"
```

#### 3. Application Not Starting

**Error**: Container app shows "Provisioning" status indefinitely

**Solutions**:
```bash
# Check revision provisioning state
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table

# View detailed logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Check resource limits
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].resources"
```

#### 4. GitHub Actions Deployment Fails

**Error**: Various GitHub Actions errors

**Solutions**:
```bash
# Verify secrets are set correctly in GitHub
# Check service principal permissions
az role assignment list \
  --assignee <client-id> \
  --output table

# Test Azure login locally
az login --service-principal \
  --username <client-id> \
  --password <client-secret> \
  --tenant <tenant-id>

# Verify Container Registry access
az acr login --name $REGISTRY_NAME
```

#### 5. azd Deployment Issues

**Error**: azd provision or deploy fails

**Solutions**:
```bash
# Check azd version
azd version

# View detailed logs
azd provision --debug
azd deploy --debug

# Verify environment configuration
azd env get-values

# Reset environment if needed
azd env refresh
```

### Debug Commands

```bash
# Get Container App details
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# View all revisions
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# Get system logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --type system

# View metrics
az monitor metrics list \
  --resource $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --resource-type "Microsoft.App/containerApps" \
  --metric-names "Requests,CpuUsage,MemoryUsage"

# Execute commands in running container
az containerapp exec \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --command /bin/bash
```

## Clean Up Resources

### Option 1: Delete Resource Group (Complete Cleanup)

```bash
# Delete entire resource group
az group delete \
  --name rg-website-summarizer-dev \
  --yes \
  --no-wait
```

### Option 2: Delete Specific Resources

```bash
# Delete Container App
az containerapp delete \
  --name ca-website-summarizer-dev \
  --resource-group rg-website-summarizer-dev \
  --yes

# Delete Container Apps Environment
az containerapp env delete \
  --name cae-website-summarizer-dev \
  --resource-group rg-website-summarizer-dev \
  --yes

# Delete Container Registry
az acr delete \
  --name crwebsummarizerdev \
  --resource-group rg-website-summarizer-dev \
  --yes

# Delete Log Analytics
az monitor log-analytics workspace delete \
  --workspace-name log-website-summarizer-dev \
  --resource-group rg-website-summarizer-dev \
  --yes
```

### Option 3: Using azd

```bash
# Delete all resources provisioned by azd
azd down

# Delete and purge completely
azd down --purge --force
```

## Cost Optimization

### Tips to Reduce Costs

1. **Scale to Zero**: Configure min replicas to 0
   ```bash
   az containerapp update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --min-replicas 0
   ```

2. **Use Basic SKU**: For dev/test, use Basic tier for Container Registry
   ```bash
   az acr update \
     --name $REGISTRY_NAME \
     --sku Basic
   ```

3. **Reduce Log Retention**: Lower retention period in Log Analytics
   ```bash
   az monitor log-analytics workspace update \
     --workspace-name $WORKSPACE_NAME \
     --resource-group $RESOURCE_GROUP \
     --retention-time 30
   ```

4. **Delete Unused Resources**: Regularly review and delete unused resources
   ```bash
   # List all resource groups
   az group list --output table
   
   # Delete unused resource groups
   az group delete --name <unused-rg> --yes
   ```

## Best Practices

1. **Use Managed Identity**: Avoid storing credentials; use managed identities
2. **Enable Monitoring**: Configure Application Insights for better observability
3. **Tag Resources**: Use tags for cost tracking and organization
4. **Version Docker Images**: Tag images with version numbers or git SHA
5. **Use Private Ingress**: Keep ingress internal unless public access is required
6. **Implement Health Checks**: Add health endpoints to your application
7. **Use Secrets**: Store sensitive data in Azure Key Vault or Container App secrets
8. **CI/CD Best Practices**: Use separate environments (dev, staging, prod)
9. **Resource Limits**: Set appropriate CPU/memory limits
10. **Backup**: Regularly backup configuration and data

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review Azure Container Apps logs
- Open an issue in the GitHub repository
- Consult Azure documentation

---

**Last Updated**: 2026-01-10
**Version**: 1.0.0
