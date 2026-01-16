# Implementation Summary: Foundry Access Configuration

## Issue Resolved
**Error**: Container app `ca-website-summarizer-dev` produces authentication errors when trying to access the Azure AI Foundry project.

**Root Cause**: The container app's managed identity does not have the required permissions to access the Foundry project resource.

## Solution Implemented

### 1. Infrastructure Changes (Bicep)

#### New Files Created:
- **`infra/modules/foundry-role-assignment.bicep`**: Subscription-scoped module that orchestrates cross-resource-group role assignments
- **`infra/modules/foundry-role-assignment-rg.bicep`**: Resource-group-scoped module that creates the actual role assignment

#### Modified Files:
- **`infra/main.bicep`**: 
  - Added optional `foundryResourceId` parameter
  - Added conditional role assignment module invocation
  - Added output for container app's managed identity principal ID
  
- **`infra/main.parameters.json`**: Added `FOUNDRY_RESOURCE_ID` parameter with default empty value

#### How It Works:
1. When `FOUNDRY_RESOURCE_ID` is provided during deployment, the Bicep template automatically creates a role assignment
2. The role assignment grants the container app's managed identity the "Cognitive Services OpenAI User" role (ID: `5a97b65f-24c7-4388-baec-2e87135dc908`)
3. The module handles cross-resource-group scenarios where the Foundry project may be in a different resource group than the container app

### 2. Documentation Created

#### New Documentation Files:
1. **`MANUAL_CONFIGURATION_STEPS.md`** (comprehensive guide):
   - Two configuration options: automated and manual
   - Step-by-step instructions with Azure CLI commands
   - Troubleshooting section with common issues
   - Complete example script
   - Prerequisites and required permissions table
   - Verification steps

2. **`FOUNDRY_ACCESS_QUICKREF.md`** (quick reference):
   - One-liner commands for quick access
   - Both automated and manual approaches
   - Minimal but complete

#### Modified Documentation Files:
1. **`DEPLOYMENT_GUIDE.md`**:
   - Updated "Authentication" section
   - Added automated configuration steps
   - Added manual configuration steps
   - Cross-references to MANUAL_CONFIGURATION_STEPS.md

2. **`README.md`**:
   - Added authentication requirements to deployment section
   - Included instructions for setting FOUNDRY_RESOURCE_ID
   - Added note about importance of permissions

3. **`.env.example`**:
   - Added FOUNDRY_RESOURCE_ID parameter
   - Added comments explaining how to obtain it

## Usage Instructions

### Option 1: Automated Configuration (During Deployment)

```bash
# Get your Foundry resource ID
FOUNDRY_RESOURCE_ID=$(az ml workspace show \
  --name <your-foundry-name> \
  --resource-group <foundry-rg> \
  --query id -o tsv)

# Set it as an environment variable
azd env set FOUNDRY_RESOURCE_ID "$FOUNDRY_RESOURCE_ID"

# Deploy
azd up
```

### Option 2: Manual Configuration (After Deployment)

See `MANUAL_CONFIGURATION_STEPS.md` for detailed steps, or use this quick command:

```bash
# Get container app's principal ID
PRINCIPAL_ID=$(az containerapp show \
  --name ca-website-summarizer-dev \
  --resource-group <rg> \
  --query identity.principalId -o tsv)

# Get Foundry resource ID
FOUNDRY_ID=$(az ml workspace show \
  --name <foundry-name> \
  --resource-group <foundry-rg> \
  --query id -o tsv)

# Grant access
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope $FOUNDRY_ID
```

## Security Considerations

1. **Least Privilege**: Uses "Cognitive Services OpenAI User" role which provides read-only access for inference
2. **No Credentials**: Uses Azure managed identities - no credentials stored in code or environment variables
3. **Optional**: Role assignment is conditional and only happens when `FOUNDRY_RESOURCE_ID` is provided
4. **Scoped**: Role assignment is scoped specifically to the Foundry resource, not the entire resource group or subscription

## Testing & Validation

- ✅ All Bicep files validate successfully with `az bicep build`
- ✅ No syntax errors or linting warnings
- ✅ Correct role definition ID: `5a97b65f-24c7-4388-baec-2e87135dc908`
- ✅ Stable API versions used: 
  - Machine Learning Services: `2023-10-01`
  - Role Assignments: `2022-04-01`
- ✅ Comprehensive documentation with troubleshooting

## Files Changed

```
Modified:
  .env.example
  DEPLOYMENT_GUIDE.md
  README.md
  infra/main.bicep
  infra/main.parameters.json

Created:
  MANUAL_CONFIGURATION_STEPS.md
  FOUNDRY_ACCESS_QUICKREF.md
  IMPLEMENTATION_SUMMARY.md (this file)
  infra/modules/foundry-role-assignment.bicep
  infra/modules/foundry-role-assignment-rg.bicep
```

## Next Steps for Administrator

1. **Choose Configuration Method**:
   - **Automated**: Set `FOUNDRY_RESOURCE_ID` before next deployment
   - **Manual**: Follow steps in `MANUAL_CONFIGURATION_STEPS.md`

2. **If using existing deployment**, run manual configuration:
   ```bash
   # See MANUAL_CONFIGURATION_STEPS.md for complete instructions
   # Or use the quick command from FOUNDRY_ACCESS_QUICKREF.md
   ```

3. **Verify the fix**:
   ```bash
   az containerapp logs show \
     --name ca-website-summarizer-dev \
     --resource-group <resource-group> \
     --follow
   ```
   Look for successful API calls instead of authentication errors.

4. **For future deployments**, include in your deployment script:
   ```bash
   export FOUNDRY_RESOURCE_ID="/subscriptions/.../workspaces/my-foundry"
   azd up
   ```

## Rollback Instructions

If needed, the role assignment can be removed:

```bash
# Find the role assignment
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --scope $FOUNDRY_RESOURCE_ID \
  --output table

# Delete it
az role assignment delete \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope $FOUNDRY_RESOURCE_ID
```

To revert infrastructure changes, use the previous version of the Bicep templates without the `foundryResourceId` parameter.

## Support & Documentation

- **Quick Reference**: `FOUNDRY_ACCESS_QUICKREF.md`
- **Detailed Guide**: `MANUAL_CONFIGURATION_STEPS.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Azure Documentation**: 
  - [Container Apps Managed Identity](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)
  - [Azure OpenAI RBAC](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control)
