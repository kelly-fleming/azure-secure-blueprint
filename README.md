# azure-secure-blueprint-dev

A fictional, source-only Azure Bicep reference architecture. Nothing has been
deployed. No Azure account is needed for local compilation and static tests.
Local lint, compilation, parameter compilation, and 72 tests passed in Docker on
2026-10-28. GitHub CI and Azure deployment remain unverified.
This is not production-ready and includes no runtime application.

The intended architecture places a Linux App Service Plan, Linux Web App with
system-assigned managed identity, and independent StorageV2 account in one existing
resource group. The entry point does not create the resource group. See
[Architecture and boundaries](docs/ARCHITECTURE.md) and
[ADR-001: local modules](docs/DECISIONS.md).

Template defaults require HTTPS and TLS 1.2, disable Web App public access, FTPS,
and remote debugging, and disable storage public access and Shared Key. Endpoints
remain inaccessible until future private networking is implemented. There is no
app-to-storage connection or RBAC assignment: managed identity alone grants no
storage permissions. Resources would incur costs if deployed.

For local use, install standalone Bicep CLI **0.37.4**, Python **3.12 or newer**
as `python`, and Bash, then run from the repository root:

```bash
bash scripts/check.sh
```

Alternatively, use Docker without installing Bicep or Python on the host:

```bash
docker build -t azure-secure-blueprint-checks:local .
docker run --rm --network none azure-secure-blueprint-checks:local
```

The image builds the toolchain once; each run recompiles and tests its copied
source, then exits. Rebuild after source changes. See the
[Docker workflow](docs/QUICKSTART.md#docker-workflow) for retaining generated JSON.

The script lints, compiles templates/parameters, and runs unittest. It creates
local generated ARM JSON in ignored `build/`; it performs no login or deployment.
See [Quickstart](docs/QUICKSTART.md) for installation references and direct commands,
[Toolchain](docs/TOOLCHAIN.md) for version choices, and
[Validation and CI](docs/VALIDATION.md) for failure handling and operator caveats.

Repository layout:

- `infra/main.bicep`: resource-group-scoped parameter interface, module composition, and nonsecret outputs. See [parameter contracts](docs/PARAMETERS.md).
- `infra/modules/`: independently authored storage, Linux plan, and isolated Web App modules.
- `params/dev.bicepparam`: explicit fictional, nonsecret dev configuration bound to the entry point; name availability and regional support remain unverified.
- `tests/`: standard-library unittest source and compiled-ARM assertions plus independent synthetic security regressions; see [Test strategy](docs/TEST_STRATEGY.md).
- `scripts/check.sh`: verified local lint/build/parameter-build/unittest entry point; see [Validation](docs/VALIDATION.md).
- `docs/`: [layout notes](docs/REPOSITORY_LAYOUT.md), [storage](docs/STORAGE.md), [compute](docs/COMPUTE.md), and [Web App security](docs/WEB_SECURITY.md).
- `.github/workflows/ci.yml`: nondeploying CI workflow invoking the same check script on pushes and pull requests. No passing status is claimed.

Generated ARM output will belong in ignored `build/`. Authored `.bicep` and
`.bicepparam` files remain source files. Keep credentials and local environment
configuration out of the repository. No Azure deployment has been run.
