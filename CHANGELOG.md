# Changelog

## v0.1.0 - 2026-10-28

Source-only milestone approved by the maintainer; verification pending for GitHub
CI and publication checks. Nothing has been deployed.
Local lint, compilation, parameter compilation, and 72 tests passed in Docker on
2026-10-28; GitHub CI remains unverified. Release date: 2026-10-28.

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

### Limitations and verification

No Azure subscription is required for the supported local workflow. No live
validation has been performed. The resources and security controls describe
template intent, not observed deployment or runtime security. Provider acceptance,
global name availability, regional SKU support, and effective policy are unverified.
CI is authored, not known to pass; action refs and Bicep download integrity require
operator review. The existing MIT [license](LICENSE) is retained.

There are no private endpoints, role assignments, Key Vault, monitoring, or
authorized app-to-storage connection. Managed identity alone grants no storage
permissions. Endpoints remain inaccessible until future networking and authorization
work. This is not production-ready. Resources would incur costs if deployed;
there is no measured-cost claim or pricing estimate.

Tagging and publishing are human only, after actual verification and review of
the intended main commit. No tag or GitHub release has been created.
See [Validation](docs/VALIDATION.md).
