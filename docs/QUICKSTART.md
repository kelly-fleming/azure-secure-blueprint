# Local quickstart

This fictional, source-only Azure Bicep example has not been deployed. No Azure
account, subscription, Azure CLI, or credentials are needed for local checks.
There is no runtime application to open in a browser. This workflow demonstrates
compiled JSON and static assertions, not a live website or production readiness.
Local checks passed in Docker on 2026-10-28; GitHub CI and Azure remain unverified.

## Docker workflow

From the repository root:

```bash
docker build -t azure-secure-blueprint-checks:local .
docker run --rm --network none azure-secure-blueprint-checks:local
```

The build requires internet access for Python, Debian packages, and standalone
Bicep 0.37.4. The image includes Python 3.12 and ICU, which Bicep needs on Debian.
No host tool installation or Azure credentials are required. Each run checks the
source copied into the image and exits with the script's status; rebuild after
editing sources. This is a check runner with no HTTP service or exposed ports.

To keep generated JSON in the checkout's ignored `build/` folder, create it first:

```powershell
New-Item -ItemType Directory -Force build | Out-Null
docker run --rm --network none --mount "type=bind,source=$((Get-Location).Path)/build,target=/workspace/build" azure-secure-blueprint-checks:local
```

On Bash, use `mkdir -p build` and replace the mount argument with
`"type=bind,source=$(pwd)/build,target=/workspace/build"`.

## Prerequisites

Use a local checkout with Bash and standard `dirname`, `mkdir`, and `rm` utilities.
On Windows, Git Bash is one option; use LF shell files as configured by the repo.

- Install standalone Bicep CLI **0.37.4** from the
  [official release](https://github.com/Azure/bicep/releases/tag/v0.37.4), following
  the [standalone installation guidance](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/install).
  Choose the appropriate OS/architecture asset, review its integrity, and put it
  on PATH as `bicep`. Azure CLI installation/authentication is unnecessary.
- Install [Python 3.12 or newer](https://www.python.org/downloads/) so `python` on
  PATH selects that interpreter. No third-party Python dependencies are needed.

See [Toolchain](TOOLCHAIN.md) for pins, API choices, and coordinated update policy.
The script checks tool availability and Python's minimum version; it does not
enforce the Bicep version. Select the documented compiler explicitly.

## Supported check workflow

From the repository root, when local execution is authorized:

```bash
bash scripts/check.sh
```

The script anchors its own paths, clears stale generated artifacts, and stops on
the first failure. It compiles `infra/main.bicep` and the fictional
`params/dev.bicepparam`, then runs all unittest cases. Its outputs are local
`build/main.json` and `build/dev.parameters.json`; `build/` is ignored and must not
be committed. No Azure login, what-if, publication, or deployment is performed.

For separate operator investigation, these are the direct steps from the root:

```bash
mkdir -p -- build
rm -f -- build/main.json build/dev.parameters.json
bicep lint infra/main.bicep
bicep build infra/main.bicep --outfile build/main.json
bicep build-params params/dev.bicepparam --outfile build/dev.parameters.json
python -m unittest discover -s tests -v
```

Stop if any direct command fails; do not treat old or partial output as validation.
Prefer rerunning the full script after fixing the cause. Missing artifacts cause
compiled tests to fail with setup advice, and boundary tests reject outputs older
than their inputs. Avoid concurrent checks in one checkout.

Inspect the generated JSON for the three nested modules, fixed security settings,
Web App plan reference, and nonsecret name/ID/principal outputs. Tests do not
evaluate runtime ARM expressions or supply an actual principal ID. Example names
are not reserved or guaranteed globally unique; `eastus`/B1 availability is
unverified. See [Parameters](PARAMETERS.md) before changing example values.

## Interpretation

The [CI workflow](../.github/workflows/ci.yml) invokes the same script without Azure
credentials. It is authored but has no verified passing result; action refs and
compiler download integrity await operator review. See [Validation](VALIDATION.md).
Source tests, generated-template assertions, and synthetic regression fixtures
provide different evidence; [Test strategy](TEST_STRATEGY.md) explains their limits.

Compilation alone cannot prove provider acceptance, name availability, costs,
effective network isolation, or authorization. Public access is disabled and no
private networking or app-to-storage RBAC exists. Managed identity grants no
permissions by itself. Review [Architecture](ARCHITECTURE.md) and
[Decisions](DECISIONS.md) for scope and tradeoffs. Resources are cost-bearing if
separately deployed; this guide includes no deployment path.
