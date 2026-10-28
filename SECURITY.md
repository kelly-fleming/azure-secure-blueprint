# Security policy

This is a fictional, source-only Azure Bicep example. Nothing has been deployed.
It is not production-ready. Configured secure defaults are template intent, not
verified runtime security. Tests, compilation, and CI results remain unverified.
There is no runtime application or customer data in this repository.

## Reporting a vulnerability

If this repository's Security tab offers **Report a vulnerability**, use that
private reporting channel. Its availability has not been verified, and this policy
does not claim private reporting is enabled. If it is unavailable, use a private
maintainer contact only when one is explicitly published by the maintainer.
No alternate private address or monitored inbox is established by this repository.

If neither private route is available, do not publish sensitive details in an
issue or pull request. A public request for a private reporting route may describe
the need for contact without including exploit details, credentials, account
identifiers, logs containing secrets, or customer data. Do not include real secrets
in a reproduction. Once a private channel is available, describe the affected
source path, relevant revision, expected versus observed behavior, and a minimal
nonsecret reproduction. Do not deploy or probe Azure resources to demonstrate an
issue without separate authorization from their owner.

There is no support SLA, guaranteed response time, supported-version maintenance
window, or commitment to provide a fix. Disclosure handling and contact preferences
remain subject to maintainer review; no service availability is promised.

## Scope and limitations

Public network access is disabled as static configuration for storage and Web App.
There are no private endpoints, role assignments, Key Vault, monitoring resources,
or authorized app-to-storage connectivity. A managed identity alone grants no
storage permissions. Endpoints remain inaccessible until future networking and
authorization work; no App Service deployment runtime or code package is included.

Template compilation cannot prove policy, SKU availability, global name uniqueness,
costs, or real deployment. Infrastructure would bill if deployed. No live deployment
or runtime assessment supports the security claims here. See the
[Threat model](docs/THREAT_MODEL.md), [Architecture](docs/ARCHITECTURE.md), and
[Test strategy](docs/TEST_STRATEGY.md) before relying on this example.
