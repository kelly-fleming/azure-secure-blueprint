# Changelog

## v0.1.0 - 2026-10-28

Validated source-only release, ready to publish. Local lint, template compilation,
parameter compilation, and all 72 tests passed in Docker on 2026-10-28.
Nothing has been deployed.

### Added

- Resource-group-scoped modular Bicep composing a Linux App Service Plan, Linux
  Web App with system-assigned managed identity, and independent StorageV2 account.
- Typed nonsecret dev parameters, bounded deterministic names, a fictional example,
  and only name/resource-ID/identity-principal-ID outputs.
- StorageV2 Standard_LRS configuration requiring HTTPS/TLS 1.2, disabling anonymous
  blob access, Shared Key authorization, and public networking, with default OAuth.
- Web App configuration requiring HTTPS/main and SCM TLS 1.2, with FTPS, remote
  debugging, and public networking disabled. No application workload is included.
- Authored local lint/build/build-params/unittest pipeline, compiled-ARM inspection
  helpers, independent negative security fixtures, and nondeploying CI workflow.
- Docker check runner with pinned Bicep 0.37.4 and Python 3.12; offline execution
  and optional generated-artifact export.
- Architecture, threat model, security policy, local setup, validation,
  and contribution conventions.

### Scope and limitations

No Azure subscription is required for the supported local workflow. Verification
covers the source and compiled templates. Deployment-time provider acceptance,
global name availability, regional SKU support, and effective policy depend on the
target Azure environment. The existing MIT [license](LICENSE) is retained.

There are no private endpoints, role assignments, Key Vault, monitoring, or
authorized app-to-storage connection. Managed identity alone grants no storage
permissions. Endpoints remain inaccessible until future networking and authorization
work. This is not production-ready. Resources would incur costs if deployed;
there is no measured-cost claim or pricing estimate.

See [Validation](docs/VALIDATION.md) for completed checks and their scope.
