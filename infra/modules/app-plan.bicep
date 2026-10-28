targetScope = 'resourceGroup'

@description('Plan name: 1-60 characters; caller supplies the bounded alphanumeric/hyphen name.')
@minLength(1)
@maxLength(60)
param name string

param location string
param tags object

@description('Linux Basic plan SKU. All allowed values are cost-bearing if provisioned.')
@allowed([
  'B1'
  'B2'
  'B3'
])
param sku string = 'B1'

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: name
  location: location
  tags: tags
  kind: 'linux'
  sku: {
    name: sku
    tier: 'Basic'
    capacity: 1
  }
  properties: {
    reserved: true
  }
}

output planId string = appServicePlan.id
output planName string = appServicePlan.name
