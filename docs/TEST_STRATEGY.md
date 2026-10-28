# Static test strategy and evidence limits

The suite uses Python 3.12 standard-library unittest. Nothing has been deployed.
Local lint, compilation, parameter compilation, and all 72 tests passed in Docker
on 2026-10-28. This verifies the source and compiled-template contracts.
See [Validation](VALIDATION.md) for completed checks and their technical scope.

## Separate evidence sources

Source assertions inspect authored paths, parameter declarations, and documentation.
They cannot establish compiler acceptance or the effective ARM resource graph.
Compiled tests inspect `build/main.json` and `build/dev.parameters.json`, generated
locally by the authored offline check pipeline. Missing artifacts fail with build
advice. Boundary tests reject artifacts older than their source/configuration
inputs, but timestamps are not provenance. The check pipeline must remove stale
output and compile afresh; no checked-in or synthetic fixture substitutes for the
production artifact in a compiled test.

Synthetic cases in `tests/test_security_regressions.py` never read build artifacts.
They reuse the independent synthetic composition graph and explicitly author the
positive storage and Web App controls. These fixtures are not snapshots of the
implementation. Each negative starts from a fresh baseline, calls the same validator
used by the artifact tests, mutates one control, and requires `InspectionError` to
identify the intended field. A missing unrelated field or other exception must
not count as a successful negative case.

| Mutation | Validator code path | Required failure field |
| --- | --- | --- |
| Storage HTTPS off | `assert_storage_security` | `properties.supportsHttpsTrafficOnly` |
| Storage TLS lowered | `assert_storage_security` | `properties.minimumTlsVersion` |
| Shared Key enabled | `assert_storage_security` | `properties.allowSharedKeyAccess` |
| Blob public access enabled | `assert_storage_security` | `properties.allowBlobPublicAccess` |
| Storage public network enabled | `assert_storage_security` | `properties.publicNetworkAccess` |
| Web HTTPS off | `assert_web_security` | `properties.httpsOnly` |
| Main/SCM TLS lowered | `assert_web_security` | `properties.siteConfig.minTlsVersion` / `scmMinTlsVersion` |
| Web public network enabled | `assert_web_security` | `properties.publicNetworkAccess` |
| Managed identity removed | `assert_web_security` | missing `identity` |
| FTPS enabled | `assert_web_security` | `properties.siteConfig.ftpsState` |
| Remote debugging enabled | `assert_web_security` | `properties.siteConfig.remoteDebuggingEnabled` |
| Key-returning output | Storage and composition output checks | named output or output inventory |

Positive cases passed all three validators, checking the fixture's own validity. Negative coverage does not establish full
coverage of provider behavior, every secret encoding, or every possible regression.

## Expressions and runtime limitations

Bicep compilation can preserve ARM expressions such as parameter references,
module outputs, and runtime `reference()` calls. The inspector does not evaluate
them. Security controls that should be fixed literals fail on unresolved expressions;
known plan and identifier wiring is checked structurally. Identity principal IDs
are unavailable until deployment and are not treated as runtime evidence.

The passing static checks do not prove Azure accepted deployment, effective
policy/RBAC, actual network isolation, name uniqueness, SKU availability, pricing,
or production readiness. The reference has no application workload, private
networking, or authorized app-to-storage data path. The suite reports contract
results rather than runtime coverage or performance benchmarks.
