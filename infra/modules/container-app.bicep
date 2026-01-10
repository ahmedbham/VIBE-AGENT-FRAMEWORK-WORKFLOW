// Container App module
@description('Name of the Container App')
param name string

@description('Location for the Container App')
param location string

@description('Tags for the Container App')
param tags object = {}

@description('Container Apps Environment ID')
param containerAppsEnvironmentId string

@description('Container Registry Name')
param containerRegistryName string

@description('Container Image')
param containerImage string

@description('Environment Variables')
param environmentVariables array = []

@description('Enable managed identity')
param managedIdentity bool = true

@description('CPU cores')
param cpuCores string = '0.5'

@description('Memory size')
param memorySize string = '1Gi'

@description('Minimum replicas')
param minReplicas int = 0

@description('Maximum replicas')
param maxReplicas int = 1

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: containerRegistryName
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: tags
  identity: managedIdentity ? {
    type: 'SystemAssigned'
  } : null
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: false
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: [
        {
          name: 'registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'main'
          image: '${containerRegistry.properties.loginServer}/${containerImage}'
          resources: {
            cpu: json(cpuCores)
            memory: memorySize
          }
          env: environmentVariables
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
}

output id string = containerApp.id
output name string = containerApp.name
output uri string = containerApp.properties.configuration.ingress.fqdn
output identityPrincipalId string = managedIdentity ? containerApp.identity.principalId : ''
