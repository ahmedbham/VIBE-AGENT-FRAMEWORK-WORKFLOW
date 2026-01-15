# Manual Configuration Steps for Container App Managed Identity Access

## Overview

The Website Summarizer container app uses Azure Managed Identity to authenticate with Azure OpenAI Foundry. This document describes the **manual steps** that administrators need to perform to grant the necessary permissions.

## Issue

The container app `ca-website-summarizer-dev` produces an error when trying to access the Foundry project:
```
Error processing https://google.com:
```

This error occurs because the container app's managed identity does not have permission to access the Azure AI Foundry project.

## Solution Options

### Option 1: Automated via Bicep (Recommended)

If you know the Foundry resource ID during deployment, you can set the `FOUNDRY_RESOURCE_ID` environment variable and the Bicep template will automatically grant the required permissions.

#### Steps:

1. **Get the Foundry Resource ID**:
   ```bash
   # Find your Foundry project
   az ml workspace list --output table
   
   # Get the full resource ID
   FOUNDRY_RESOURCE_ID=$(az ml workspace show \
     --name <your-foundry-name> \
     --resource-group <foundry-resource-group> \
     --query id -o tsv)
   
   echo $FOUNDRY_RESOURCE_ID
   # Output example: /subscriptions/xxx/resourceGroups/xxx/providers/Microsoft.MachineLearningServices/workspaces/my-foundry
   ```

2. **Set the environment variable before deployment**:
   
   **For azd deployment**:
   ```bash
   azd env set FOUNDRY_RESOURCE_ID "$FOUNDRY_RESOURCE_ID"
   azd provision  # or azd up
   ```
   
   **For Azure CLI deployment**:
   ```bash
   az deployment sub create \
     --location <location> \
     --template-file infra/main.bicep \
     --parameters infra/main.parameters.json \
     --parameters foundryResourceId="$FOUNDRY_RESOURCE_ID"
   ```

3. **Verify the role assignment**:
   ```bash
   # Get the container app's managed identity principal ID
   PRINCIPAL_ID=$(az containerapp show \
     --name ca-website-summarizer-dev \
     --resource-group <resource-group> \
     --query identity.principalId -o tsv)
   
   # List role assignments
   az role assignment list \
     --assignee $PRINCIPAL_ID \
     --all \
     --output table
   ```

### Option 2: Manual Configuration (Post-Deployment)

If the Foundry resource ID is not available during deployment or if you prefer to grant permissions manually, follow these steps:

#### Prerequisites:
- Azure CLI installed and authenticated
- Appropriate permissions to:
  - View the Container App details
  - Assign roles on the Foundry project

#### Steps:

1. **Get the Container App's Managed Identity Principal ID**:
   ```bash
   # Set your resource group and app name
   RESOURCE_GROUP="rg-website-summarizer-dev"
   APP_NAME="ca-website-summarizer-dev"
   
   # Get the principal ID
   PRINCIPAL_ID=$(az containerapp show \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --query identity.principalId -o tsv)
   
   echo "Principal ID: $PRINCIPAL_ID"
   ```
   
   **Note**: If this returns empty, the managed identity is not enabled. Enable it with:
   ```bash
   az containerapp identity assign \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --system-assigned
   ```

2. **Get the Foundry Project Resource ID**:
   ```bash
   # List all Foundry projects
   az ml workspace list --output table
   
   # Get the specific Foundry project resource ID
   FOUNDRY_NAME="my-vibe-foundry"
   FOUNDRY_RG="vibe-rg"
   
   FOUNDRY_RESOURCE_ID=$(az ml workspace show \
     --name $FOUNDRY_NAME \
     --resource-group $FOUNDRY_RG \
     --query id -o tsv)
   
   echo "Foundry Resource ID: $FOUNDRY_RESOURCE_ID"
   ```

3. **Grant "Cognitive Services OpenAI User" Role**:
   ```bash
   # Assign the role
   az role assignment create \
     --assignee $PRINCIPAL_ID \
     --role "Cognitive Services OpenAI User" \
     --scope $FOUNDRY_RESOURCE_ID
   
   echo "✓ Role assignment created successfully"
   ```
   
   **Alternative role options**:
   - `Cognitive Services OpenAI User` (5a97b65f3-24c7-4388-baec-2e87135dc908) - Read access for inference
   - `Cognitive Services OpenAI Contributor` (a001fd3d-188f-4b5d-821b-7da978bf7442) - Full access
   
   To use a specific role by ID:
   ```bash
   az role assignment create \
     --assignee $PRINCIPAL_ID \
     --role "5a97b65f3-24c7-4388-baec-2e87135dc908" \
     --scope $FOUNDRY_RESOURCE_ID
   ```

4. **Verify the Role Assignment**:
   ```bash
   # List all role assignments for the managed identity
   az role assignment list \
     --assignee $PRINCIPAL_ID \
     --all \
     --output table
   
   # Verify specifically on the Foundry resource
   az role assignment list \
     --scope $FOUNDRY_RESOURCE_ID \
     --assignee $PRINCIPAL_ID \
     --output table
   ```

5. **Restart the Container App** (if already running):
   ```bash
   # Get the latest revision name
   REVISION=$(az containerapp revision list \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --query "[0].name" -o tsv)
   
   # Restart the revision
   az containerapp revision restart \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --revision $REVISION
   
   echo "✓ Container app restarted"
   ```

6. **Verify the Fix**:
   ```bash
   # Stream logs to verify the app is working
   az containerapp logs show \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --follow
   
   # Look for successful API calls instead of authentication errors
   ```

## Verification

After granting permissions, verify that the application can successfully access the Foundry project:

1. **Check Container App Logs**:
   ```bash
   az containerapp logs show \
     --name ca-website-summarizer-dev \
     --resource-group <resource-group> \
     --follow
   ```

2. **Look for Success Indicators**:
   - No more "Error processing" messages
   - Successful API responses from Azure OpenAI
   - Workflow completing without authentication errors

3. **Test the Application**:
   - If the app has an HTTP endpoint, send a test request
   - Monitor the logs for successful processing

## Troubleshooting

### Issue: "Principal ID is empty"
**Solution**: Ensure managed identity is enabled on the container app:
```bash
az containerapp identity assign \
  --name ca-website-summarizer-dev \
  --resource-group <resource-group> \
  --system-assigned
```

### Issue: "Insufficient privileges to complete the operation"
**Solution**: Ensure you have one of the following roles:
- `Owner` on the Foundry resource
- `User Access Administrator` on the Foundry resource
- `Contributor` + `User Access Administrator` on the subscription

### Issue: "Role assignment already exists"
**Solution**: This is expected if the role was already assigned. Verify with:
```bash
az role assignment list --assignee $PRINCIPAL_ID --all --output table
```

### Issue: "Still getting authentication errors after role assignment"
**Solutions**:
1. Wait 5-10 minutes for permissions to propagate
2. Restart the container app
3. Verify the FOUNDRY_ENDPOINT environment variable matches the Foundry resource
4. Check that the managed identity is the correct type (System-assigned)

### Issue: "Cannot find Foundry workspace"
**Solution**: Ensure Azure ML extension is installed:
```bash
az extension add --name ml
az extension update --name ml
```

## Required Azure Permissions

To perform these steps, you need:

| Task | Required Role | Scope |
|------|--------------|-------|
| View Container App details | Reader | Container App or Resource Group |
| Enable Managed Identity | Contributor | Container App |
| Grant role on Foundry | Owner or User Access Administrator | Foundry Project |
| View Foundry details | Reader | Foundry Project |
| Restart Container App | Contributor | Container App |

## Complete Example Script

Here's a complete script that performs all steps:

```bash
#!/bin/bash

# Configuration
RESOURCE_GROUP="rg-website-summarizer-dev"
APP_NAME="ca-website-summarizer-dev"
FOUNDRY_NAME="my-vibe-foundry"
FOUNDRY_RG="vibe-rg"

echo "=== Granting Container App Managed Identity Access to Foundry ==="
echo ""

# 1. Ensure managed identity is enabled
echo "Step 1: Ensuring managed identity is enabled..."
az containerapp identity assign \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --system-assigned

# 2. Get the principal ID
echo ""
echo "Step 2: Getting managed identity principal ID..."
PRINCIPAL_ID=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId -o tsv)

echo "Principal ID: $PRINCIPAL_ID"

# 3. Get Foundry resource ID
echo ""
echo "Step 3: Getting Foundry resource ID..."
FOUNDRY_RESOURCE_ID=$(az ml workspace show \
  --name $FOUNDRY_NAME \
  --resource-group $FOUNDRY_RG \
  --query id -o tsv)

echo "Foundry Resource ID: $FOUNDRY_RESOURCE_ID"

# 4. Grant role
echo ""
echo "Step 4: Granting 'Cognitive Services OpenAI User' role..."
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope $FOUNDRY_RESOURCE_ID

echo ""
echo "✓ Role assignment created successfully"

# 5. Verify
echo ""
echo "Step 5: Verifying role assignment..."
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --scope $FOUNDRY_RESOURCE_ID \
  --output table

# 6. Restart container app
echo ""
echo "Step 6: Restarting container app..."
REVISION=$(az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[0].name" -o tsv)

az containerapp revision restart \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --revision $REVISION

echo ""
echo "✓ Container app restarted"
echo ""
echo "=== Configuration Complete ==="
echo ""
echo "Next steps:"
echo "1. Wait 2-5 minutes for permissions to propagate"
echo "2. Monitor logs: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "3. Test the application to verify it's working"
```

## Additional Resources

- [Azure Container Apps Managed Identity](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)
- [Azure OpenAI Service RBAC](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the container app logs
3. Verify all prerequisites are met
4. Open an issue in the GitHub repository with error details
