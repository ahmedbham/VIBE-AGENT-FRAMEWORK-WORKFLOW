// Role Assignment module for granting Container App managed identity access to Azure AI Foundry
targetScope = 'subscription'

@description('Principal ID of the managed identity')
param principalId string

@description('Resource ID of the Azure AI Foundry project')
param foundryResourceId string

@description('Role Definition ID for the role to assign. Default is Cognitive Services OpenAI User.')
param roleDefinitionId string = '5a97b65f-24c7-4388-baec-2e87135dc908' // Cognitive Services OpenAI User

// Parse resource group info from the Foundry resource ID
var subscriptionId = split(foundryResourceId, '/')[2]
var resourceGroupName = split(foundryResourceId, '/')[4]
var resourceName = split(foundryResourceId, '/')[8]

// Use a module to deploy to the correct resource group
module roleAssignmentInRg 'foundry-role-assignment-rg.bicep' = {
  name: 'role-assignment-in-rg'
  scope: resourceGroup(subscriptionId, resourceGroupName)
  params: {
    principalId: principalId
    foundryName: resourceName
    roleDefinitionId: roleDefinitionId
  }
}

output roleAssignmentId string = roleAssignmentInRg.outputs.roleAssignmentId
output roleAssignmentName string = roleAssignmentInRg.outputs.roleAssignmentName
