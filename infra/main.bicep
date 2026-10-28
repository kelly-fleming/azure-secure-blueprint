// Resource-group entry point composing independently authored local modules.
targetScope = 'resourceGroup'

@allowed([
  'dev'
])
param environment string = 'dev'

@description('Azure region for all resources; availability must be checked by the operator.')
param location string = resourceGroup().location

@description('Project prefix: 2-6 lowercase ASCII letters or digits only.')
@minLength(2)
@maxLength(6)
param projectPrefix string = 'demo'

@description('Suffix: 6-12 lowercase ASCII letters or digits only; operator must ensure final names are globally unique.')
@minLength(6)
@maxLength(12)
param uniqueSuffix string = 'sample01'

@description('Linux App Service Plan SKU; B1 is cost-bearing if deployed.')
@allowed([
  'B1'
  'B2'
  'B3'
])
param appServicePlanSku string = 'B1'

@description('Nonsecret resource tags. Do not include credentials or private identifiers.')
param tags object = {
  environment: 'dev'
  project: 'fictional-blueprint'
}

// Map unsupported characters to 0 so even malformed inputs cannot create invalid
// resource names. This normalization can collide; it does not establish uniqueness.
var alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
var normalizedPrefix = join(map(range(0, length(projectPrefix)), i => contains(alphabet, toLower(substring(projectPrefix, i, 1))) ? toLower(substring(projectPrefix, i, 1)) : '0'), '')
var normalizedSuffix = join(map(range(0, length(uniqueSuffix)), i => contains(alphabet, toLower(substring(uniqueSuffix, i, 1))) ? toLower(substring(uniqueSuffix, i, 1)) : '0'), '')
var storageAccountName = '${normalizedPrefix}${environment}${normalizedSuffix}'
var appServicePlanName = '${normalizedPrefix}-${environment}-plan-${normalizedSuffix}'
var webAppName = '${normalizedPrefix}-${environment}-web-${normalizedSuffix}'

module storage './modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: storageAccountName
    location: location
    tags: tags
  }
}

module plan './modules/app-plan.bicep' = {
  name: 'plan'
  params: {
    name: appServicePlanName
    location: location
    tags: tags
    sku: appServicePlanSku
  }
}

module web './modules/web-app.bicep' = {
  name: 'web'
  params: {
    name: webAppName
    location: location
    tags: tags
    planId: plan.outputs.planId
  }
}

// Resource-derived values resolve at deployment; no deployment is claimed here.
output storageName string = storage.outputs.storageName
output storageId string = storage.outputs.storageId
output planName string = plan.outputs.planName
output planId string = plan.outputs.planId
output appName string = web.outputs.appName
output appId string = web.outputs.appId
output principalId string = web.outputs.principalId
