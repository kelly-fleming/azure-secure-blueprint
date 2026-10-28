targetScope = 'resourceGroup'

@description('Storage account name: 3-24 lowercase ASCII letters/digits; must be globally unique.')
@minLength(3)
@maxLength(24)
param name string

param location string
param tags object

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: 'Disabled'
  }
}

output storageId string = storageAccount.id
output storageName string = storageAccount.name
