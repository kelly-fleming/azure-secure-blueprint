# Storage module security contract

`infra/modules/storage.bicep` is an independently authored resource-group module
for one `Microsoft.Storage/storageAccounts@2023-05-01` resource. It accepts `name`,
`location`, and nonsecret `tags`. The caller must supply a globally unique name
using 3-24 lowercase ASCII letters/digits; length decorators enforce bounds, while
the main parameter contract normalizes name characters. Name availability and
provider acceptance remain operator checks.

The module defines StorageV2 with Standard_LRS and fixes these properties rather
than exposing access-control overrides:

| Property | Value | Intended restriction |
| --- | --- | --- |
| `supportsHttpsTrafficOnly` | `true` | Require HTTPS for supported storage requests. |
| `minimumTlsVersion` | `TLS1_2` | Require TLS 1.2 or newer. |
| `allowBlobPublicAccess` | `false` | Block anonymous blob public access. |
| `allowSharedKeyAccess` | `false` | Disable Shared Key authorization. |
| `defaultToOAuthAuthentication` | `true` | Prefer OAuth in the portal; this grants no permissions. |
| `publicNetworkAccess` | `Disabled` | Disable public network access. |

The selected API documents these properties in the Microsoft
[storage account reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/2023-05-01/storageaccounts).
Encryption at rest uses Azure-managed keys by default; this module relies on that
platform default and does not configure customer-managed keys or Key Vault.
No containers, private endpoints, DNS, networking exceptions, or RBAC assignments
are created. There is no storage data-plane access until future private networking
and RBAC are implemented. An App Service managed identity alone grants no storage
permissions, and no application connection is configured here.

Outputs are only `storageId` and `storageName`, both nonsecret resource identifiers.
The module never retrieves account keys, connection strings, or SAS tokens.
An output expression is configuration, not proof that a resource has been deployed.

Nothing has been deployed. `infra/main.bicep` calls this module independently of
the plan and Web App. The compiled contract tests in
`tests/test_storage_contract.py` inspect nested storage resources in a freshly
generated `build/main.json` from the composed entry point. A missing artifact or absent
storage resource fails explicitly. These tests reject expressions in fixed security
properties rather than pretending to evaluate ARM expressions. Compilation and
these contract tests passed in Docker on 2026-10-28. Template intent alone cannot establish
runtime security or deployment compatibility. Storage is cost-bearing if deployed.
