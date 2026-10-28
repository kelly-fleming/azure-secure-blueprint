# Toolchain and resource API policy

## Standalone compiler reference

The initial pinned standalone Bicep CLI version is **0.37.4** (release tag
`v0.37.4`). This is a reproducibility reference, not a claim that it is the latest
release. An operator can obtain the platform-appropriate standalone executable
from the [official release](https://github.com/Azure/bicep/releases/tag/v0.37.4)
and place it on PATH as `bicep`. Review release provenance and download integrity
before installation. The Docker runner installs this version during image build.

Azure CLI, Azure account authentication, and a subscription are not required for
the intended local lint/build workflow. Python 3.12 with standard-library unittest
is the test-suite reference; no third-party Python packages are required.
The offline check script and CI setup are authored; see [Validation](VALIDATION.md).
Local lint/build/tests passed in Docker on 2026-10-28; GitHub CI remains unverified.

## Lint policy

The root `bicepconfig.json` enables `analyzers.core.enabled`. It applies to Bicep
sources below the repository root, including the entry point and local modules.
Rules not listed retain the selected compiler's defaults. The structure and rule
IDs follow Microsoft's [linter configuration reference](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-config-linter).

| Published rule | Level | Reason |
| --- | --- | --- |
| `no-hardcoded-env-urls` | error | Keep cloud environment endpoints derived from the environment rather than embedding cloud-specific hosts. |
| `no-unused-params` | error | Keep the public parameter contract connected to template behavior. |
| `secure-secrets-in-params` | error | Reject parameters the analyzer identifies as possible unprotected secrets; this release should have no secret inputs. |
| `outputs-should-not-contain-secrets` | error | Reject possible secret exposure through deployment outputs, including secure parameter values and key-returning functions. |

An error-level diagnostic is intended to fail compilation rather than remain an
advisory warning. See the published rules for
[secret parameters](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter-rule-secure-secrets-in-parameters)
and [secret outputs](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter-rule-outputs-should-not-contain-secrets).
These are heuristic checks, not proof that source or outputs contain no secrets.
All four are configured published rule IDs; local lint/build accepted the
configuration with the pinned executable. Do not silently
disable a rule to accommodate an unexpected diagnostic or compiler mismatch.

## Stable resource API choices

These are explicit non-preview API versions for the future local modules, chosen
to keep the example's contracts fixed rather than follow a moving latest version.
The linked Microsoft resource references document their resource-group scope and
property contracts; they do not establish successful deployment in any region.

| Resource type | API version | Rationale and reference |
| --- | --- | --- |
| `Microsoft.Web/serverfarms` | `2024-04-01` | Stable plan contract with Linux `reserved` and SKU/capacity properties; [reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.web/2024-04-01/serverfarms). |
| `Microsoft.Web/sites` | `2024-04-01` | Same Web API generation, with identity, plan reference, HTTPS, public network access, and main/SCM TLS controls; [reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.web/2024-04-01/sites). |
| `Microsoft.Storage/storageAccounts` | `2023-05-01` | Stable StorageV2 contract with HTTPS, TLS, public/blob access, shared-key, and default OAuth properties; [reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/2023-05-01/storageaccounts). |

These versions are used by the local modules composed from the entry point.
Local compilation completed without diagnostics. Provider acceptance, policy,
and regional availability remain unverified.

## Operator-controlled updates

To change the compiler pin, review the official release notes and supported rule
IDs, then update this reference and any subsequently authored script or CI version
pins together in one change. Obtain the new standalone executable independently.
When execution is authorized, record the actual CLI version and lint/build/test
results in the operator verification record; do not infer compatibility from JSON
configuration tests alone. Investigate diagnostics before accepting the update.

To change a resource API, review its provider change log and property reference,
update this table and the corresponding module declaration together, and adjust
affected contract assertions for intentional changes. Keep non-preview versions
unless a separately documented requirement justifies otherwise. Actual compilation
and provider compatibility remain operator checks, not prerequisites for authoring
the next task's parameter contracts.
