// Resource group scoped role assignment module
targetScope = 'resourceGroup'

@description('Principal ID of the managed identity')
param principalId string

@description('Name of the Foundry workspace')
param foundryName string

@description('Role Definition ID for the role to assign')
param roleDefinitionId string

// Reference the existing Foundry workspace
resource foundryProject 'Microsoft.MachineLearningServices/workspaces@2023-10-01' existing = {
  name: foundryName
}

// Create role assignment scoped to the Foundry workspace
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundryProject.id, principalId, roleDefinitionId)
  scope: foundryProject
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output roleAssignmentId string = roleAssignment.id
output roleAssignmentName string = roleAssignment.name
