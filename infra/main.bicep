// Main Bicep template for deploying Website Summarizer Workflow to Azure Container Apps
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the container image')
param containerImageName string = ''

@description('Azure OpenAI Foundry Endpoint')
param foundryEndpoint string

@description('Azure OpenAI Deployment Name')
param azureOpenAIDeployment string = 'gpt-4.1-mini'

@description('Azure OpenAI API Version')
param azureOpenAIApiVersion string = '2024-10-21'

@description('Container Registry name')
param containerRegistryName string = ''

@description('Resource group name')
param resourceGroupName string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Container Registry
module containerRegistry './modules/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    tags: tags
  }
}

// Log Analytics Workspace for Container Apps
module logAnalytics './modules/log-analytics.bicep' = {
  name: 'log-analytics'
  scope: rg
  params: {
    name: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container Apps Environment
module containerAppsEnvironment './modules/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// Website Summarizer Container App
module websiteSummarizerApp './modules/container-app.bicep' = {
  name: 'website-summarizer-app'
  scope: rg
  params: {
    name: '${abbrs.appContainerApps}website-summarizer-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'website-summarizer' })
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
    containerRegistryName: containerRegistry.outputs.name
    containerImage: !empty(containerImageName) ? containerImageName : 'website-summarizer:latest'
    environmentVariables: [
      {
        name: 'FOUNDRY_ENDPOINT'
        value: foundryEndpoint
      }
      {
        name: 'AZURE_OPENAI_DEPLOYMENT'
        value: azureOpenAIDeployment
      }
      {
        name: 'AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'
        value: azureOpenAIDeployment
      }
      {
        name: 'AZURE_OPENAI_API_VERSION'
        value: azureOpenAIApiVersion
      }
    ]
    managedIdentity: true
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.outputs.id
output WEBSITE_SUMMARIZER_APP_NAME string = websiteSummarizerApp.outputs.name
output WEBSITE_SUMMARIZER_APP_URL string = websiteSummarizerApp.outputs.uri
