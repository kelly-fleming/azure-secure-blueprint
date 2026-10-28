// Fictional nonsecret example. Name availability and regional support are unverified.
using '../infra/main.bicep'

param environment = 'dev'
param location = 'eastus'
param projectPrefix = 'demo'
param uniqueSuffix = 'sample01'
param appServicePlanSku = 'B1'
param tags = {
  environment: 'dev'
  project: 'fictional-blueprint'
  purpose: 'source-example'
}
