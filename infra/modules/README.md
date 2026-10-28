# Local Bicep modules

This directory holds independently authored resource-group Bicep modules.
`storage.bicep` defines the restrictive StorageV2 contract described in
[Storage](../../docs/STORAGE.md). `app-plan.bicep` defines the Linux Basic plan
described in [Compute](../../docs/COMPUTE.md). `web-app.bicep` defines the isolated
Linux Web App described in [Web security](../../docs/WEB_SECURITY.md).
`infra/main.bicep` composes all three modules; no module has been deployed.
