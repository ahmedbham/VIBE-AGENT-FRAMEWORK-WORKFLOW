# GitHub Actions Deployment with OIDC Setup

This guide explains how to configure **OIDC Federated Credentials** for secure Azure deployments from GitHub Actions without storing secrets.

---

## Prerequisites

- Azure CLI installed locally
- GitHub repository admin access
- Azure subscription with Contributor/Owner role

---

## Setup Steps

### Option 1: Using Azure Developer CLI (Recommended)

The easiest way to configure OIDC is using `azd pipeline config`:

```bash
# From your project root
azd pipeline config --provider github
```

This command will:
- Create an Azure AD application and service principal
- Configure federated credentials for your GitHub repo
- Set up necessary GitHub secrets and variables
- Grant service principal access to your Azure subscription

### Option 2: Manual Setup with Azure CLI

If you prefer manual configuration:

#### 1. Create Azure AD Application and Service Principal

```bash
# Set variables
REPO_OWNER="<your-github-username-or-org>"
REPO_NAME="<your-repo-name>"
SUBSCRIPTION_ID="<your-azure-subscription-id>"
RESOURCE_GROUP="<your-resource-group>"

# Create the Azure AD app
APP_NAME="github-actions-oidc-$REPO_NAME"
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)

# Create service principal
az ad sp create --id $APP_ID

# Get service principal object ID
SP_OBJECT_ID=$(az ad sp show --id $APP_ID --query id -o tsv)

# Assign Contributor role at subscription or resource group level
az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope "/subscriptions/$SUBSCRIPTION_ID"
```

#### 2. Configure Federated Credential for GitHub Actions

```bash
# Create federated credential for main branch
az ad app federated-credential create \
  --id $APP_ID \
  --parameters "{
    \"name\": \"github-actions-main\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:$REPO_OWNER/$REPO_NAME:ref:refs/heads/main\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }"

# Optional: Add federated credential for pull requests
az ad app federated-credential create \
  --id $APP_ID \
  --parameters "{
    \"name\": \"github-actions-pr\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:$REPO_OWNER/$REPO_NAME:pull_request\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }"
```

#### 3. Configure GitHub Secrets and Variables

Add these as **Repository Secrets** in GitHub (Settings → Secrets and variables → Actions):

```
AZURE_CLIENT_ID: <APP_ID from above>
AZURE_TENANT_ID: <your Azure tenant ID>
AZURE_SUBSCRIPTION_ID: <your subscription ID>
```

Add these as **Repository Variables**:

```
AZURE_ENV_NAME: <your azd environment name, e.g., "dev">
AZURE_LOCATION: <Azure region, e.g., "eastus">
```

To get your tenant ID:
```bash
az account show --query tenantId -o tsv
```

---

## Verify Configuration

1. **Check federated credentials**:
   ```bash
   az ad app federated-credential list --id $APP_ID
   ```

2. **Test GitHub Actions workflow**:
   - Push to `main` branch or trigger workflow manually
   - Verify OIDC authentication succeeds in workflow logs

---

## Workflow File

The workflow file [.github/workflows/aca-deploy.yml](.github/workflows/aca-deploy.yml) is configured with:

- **`permissions: id-token: write`** – Required for OIDC token generation
- **`azure/login@v2`** – Authenticates using federated credentials (no password/secret)
- **`azd up`** – Provisions infrastructure and deploys the container app

---

## Security Benefits

✅ **No secrets stored** – GitHub Actions uses short-lived OIDC tokens  
✅ **Scoped to specific repos/branches** – Federated credential restricts access  
✅ **Azure Managed Identity** – Service principal tied to Azure RBAC  
✅ **Automatic token rotation** – No manual credential management  

---

## Troubleshooting

### Error: "AADSTS70021: No matching federated identity record found"

**Cause**: The `subject` claim in the federated credential doesn't match the GitHub Actions context.

**Solution**: Verify the subject matches exactly:
- For main branch: `repo:OWNER/REPO:ref:refs/heads/main`
- For pull requests: `repo:OWNER/REPO:pull_request`

### Error: "Insufficient privileges to complete the operation"

**Cause**: Service principal lacks necessary Azure RBAC permissions.

**Solution**: Grant Contributor role to the service principal at subscription or resource group scope.

---

## Next Steps

After setup, push code to trigger the workflow:

```bash
git add .
git commit -m "Add GitHub Actions deployment with OIDC"
git push origin main
```

Monitor deployment in **Actions** tab of your GitHub repository.
