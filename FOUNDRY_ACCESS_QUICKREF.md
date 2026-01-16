# Quick Reference: Foundry Access Configuration

## Problem
The container app `ca-website-summarizer-dev` gets an authentication error when trying to access the Azure AI Foundry project because the managed identity doesn't have permission.

## Solution

### Option 1: Automatic (During Deployment)

Set the `FOUNDRY_RESOURCE_ID` before deployment:

```bash
# Get your Foundry resource ID
FOUNDRY_RESOURCE_ID=$(az ml workspace show \
  --name <your-foundry-name> \
  --resource-group <foundry-rg> \
  --query id -o tsv)

# For azd
azd env set FOUNDRY_RESOURCE_ID "$FOUNDRY_RESOURCE_ID"
azd up

# For Azure CLI
az deployment sub create \
  --location <location> \
  --template-file infra/main.bicep \
  --parameters foundryResourceId="$FOUNDRY_RESOURCE_ID"
```

### Option 2: Manual (After Deployment)

Run this one-liner after deployment:

```bash
# Set your values
RESOURCE_GROUP="rg-website-summarizer-dev"
APP_NAME="ca-website-summarizer-dev"
FOUNDRY_NAME="my-vibe-foundry"
FOUNDRY_RG="vibe-rg"

# Get principal ID and grant access
PRINCIPAL_ID=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query identity.principalId -o tsv) && \
FOUNDRY_ID=$(az ml workspace show --name $FOUNDRY_NAME --resource-group $FOUNDRY_RG --query id -o tsv) && \
az role assignment create --assignee $PRINCIPAL_ID --role "Cognitive Services OpenAI User" --scope $FOUNDRY_ID && \
echo "✓ Access granted"
```

## Verification

Check the container app logs:
```bash
az containerapp logs show \
  --name ca-website-summarizer-dev \
  --resource-group <resource-group> \
  --follow
```

## More Information

- Full manual steps with troubleshooting: [MANUAL_CONFIGURATION_STEPS.md](MANUAL_CONFIGURATION_STEPS.md)
- Deployment guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
