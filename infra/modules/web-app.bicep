targetScope = 'resourceGroup'

@description('Web App name: 2-60 alphanumeric/hyphen characters, starting and ending alphanumeric.')
@minLength(2)
@maxLength(60)
param name string

param location string
param tags object

@description('Resource ID of the Linux App Service Plan; composition supplies the plan module output.')
@minLength(1)
param planId string

resource webApp 'Microsoft.Web/sites@2024-04-01' = {
  name: name
  location: location
  tags: tags
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: planId
    httpsOnly: true
    publicNetworkAccess: 'Disabled'
    siteConfig: {
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.2'
      ftpsState: 'Disabled'
      remoteDebuggingEnabled: false
    }
  }
}

output appId string = webApp.id
output appName string = webApp.name
output principalId string = webApp.identity.principalId
