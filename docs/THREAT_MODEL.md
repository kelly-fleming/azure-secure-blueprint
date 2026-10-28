# Threat model and operational limitations

This fictional, source-only reference has not been deployed. It is not
production-ready. Nothing has been deployed, and no runtime security evidence is
available. Public access is disabled as static configuration in the templates;
that configuration is not proof of effective runtime isolation.

## Assets and boundaries

The assets in scope are authored infrastructure source, nonsecret example
parameters, generated local ARM JSON, and the integrity of static assertions/CI.
If provisioned separately, the plan, Web App identity, and storage account would
be additional assets. There is no customer data or runtime workload in this repo.
An existing resource group is the management scope, not a network security boundary.
See [Architecture](ARCHITECTURE.md) for the component and absent-data-flow diagram.

Assume a reviewer can inspect source and generated JSON, but compilation does not
evaluate every runtime expression or reveal effective Azure policy. A contributor
could weaken a control or its assertion; a compromised tool or mutable action tag
could undermine the checks. An operator with deployment permissions could also
change resources independently of source. Those actors and changes require review;
the template alone cannot police them.

| Threat | Authored control or boundary | Residual gap |
| --- | --- | --- |
| Unintended public data-plane exposure | Storage and Web App set `publicNetworkAccess` to `Disabled`; anonymous blob access is disabled. | No private endpoints, private DNS, or private network integration exist. Endpoints remain inaccessible until future networking; no live isolation has been verified. |
| Credential or data disclosure | No secret inputs, app settings, key retrieval, or credential outputs are included; Shared Key is disabled. | Static patterns are not a complete secret scanner. Contributors must avoid secrets in source, tags, logs, or generated output. No Key Vault is included. |
| Unauthorized app-to-storage access | No role assignments (RBAC) and no authorized app-to-storage connectivity are configured. | A managed identity alone grants no storage permissions. Authentication identity, network path, and authorization must all be designed before any future connection. |
| Weak transport or administrative exposure | Templates require HTTPS/TLS 1.2, disable FTPS and remote debugging, and set SCM TLS 1.2. | No App Service deployment runtime or application exists to assess. These properties do not prove application authentication, authorization, or patching. |
| Undetected drift or incidents | Static source and compiled-ARM assertions can detect the regressions they explicitly cover when executed. | No monitoring, alerting, audit-log integration, drift detection, or incident response automation is provisioned. No checks have been run. |
| Build or dependency compromise | Local Bicep modules and restricted CI permissions reduce dependency/access scope. | Bicep binary integrity and action refs require operator review; major action tags are mutable. Passing static checks do not independently establish tool trust. |
| Accidental spend or unsuitable placement | No deployment command exists in the supported check workflow. | Infrastructure would bill if deployed, even with no traffic. Region, quota, SKU availability, and pricing require independent operator review. |

## Explicit exclusions

There are no private endpoints, role assignments, Key Vault, or monitoring
resources. There is no App Service deployment runtime, code/artifact deployment,
application package, storage container, authorized app-to-storage connectivity, or
working website. No production support or operational recovery design is implied.
Future networking or authorization is outside this release and must not be assumed
enabled merely because an identity is declared.

Template compilation cannot prove effective policy, SKU availability, global name
uniqueness, costs, or real deployment. It also cannot prove provider acceptance,
actual TLS negotiation, effective RBAC, or network reachability. Generated identity
principal IDs remain deployment-time values, not observed evidence. Source and
synthetic tests cannot replace the real compiled artifact, and compiled assertions
cannot replace runtime assessment. See [Test strategy](TEST_STRATEGY.md) and
[Validation](VALIDATION.md) for the evidence boundaries.

Report suspected vulnerabilities according to [Security policy](../SECURITY.md).
This document records intended controls and known gaps, not a security certification.
