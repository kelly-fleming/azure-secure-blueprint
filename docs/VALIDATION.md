# Offline validation workflow

Local lint, compilation, parameter compilation, and all 72 unittest cases passed
in Docker on 2026-10-28, using Bicep 0.37.4 and Python 3.12. The runner had networking
disabled. Nothing has been deployed. No Azure account, Azure CLI,
subscription, credentials, or authentication is required for these local checks.

The [Docker workflow](QUICKSTART.md#docker-workflow) installs the local tools during
image build and runs this same script. Rebuild the image after changing sources.
The source-only release is validated and ready to publish. Verification covers
local source and compiled-template contracts; deployment acceptance and runtime
behavior depend on the target Azure environment.

Additional disposable-container checks passed: invocation from another directory
and a checkout path containing spaces; replacement of stale generated artifacts;
actual invalid-Bicep compilation stopping before tests and removing old artifacts;
nonzero status propagation at lint, build, parameter-build, and unittest boundaries;
and missing-compiler setup advice. Failure-boundary checks used isolated tool
doubles; the invalid-Bicep case used the real compiler. A final rebuilt-image run
also exported fresh JSON through the documented `build/` bind mount.

Install a standalone Bicep CLI on PATH as `bicep`, using the **0.37.4** reference
in [Toolchain](TOOLCHAIN.md), and Python **3.12 or newer** on PATH as `python`.
The script checks executable availability and Python's version; it does not install
tools or enforce the Bicep pin. The operator must select the documented CLI version.
See the official [Bicep installation instructions](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/install)
and [Python downloads](https://www.python.org/downloads/). Use Bash (for example,
Git Bash on Windows) with standard `dirname`, `mkdir`, and `rm` utilities.

When execution is authorized, run from the repository root:

```bash
bash scripts/check.sh
```

The script anchors paths to its own repository directory, so invoking its absolute
path from another working directory follows the same workflow. It uses
`set -Eeuo pipefail` and stops on the first error with a nonzero status. Missing
tools or an older Python produce setup advice. It creates ignored `build/`, deletes
both named generated artifacts before lint/compilation, then runs in this order:

```bash
bicep lint infra/main.bicep
bicep build infra/main.bicep --outfile build/main.json
bicep build-params params/dev.bicepparam --outfile build/dev.parameters.json
python -m unittest discover -s tests -v
```

These commands completed successfully. They verify compilation and static
contracts; Azure deployment and runtime security are outside this workflow. A failure stops
subsequent commands; a partial output from that failed run is not evidence. Rerun
the entire pipeline after correcting the cause so it clears outputs and recompiles.
Do not run concurrent checks in the same checkout: they share the two output paths.

For separate operator investigation, the direct commands above are available;
create `build/` and remove both old generated files before compiling. Compiled tests
need actual fresh artifacts, while synthetic tests exercise independent fixtures.
Boundary checks also compare artifact/source timestamps, which cannot establish
provenance. Never substitute handcrafted fixtures for compiled output or commit
`build/`. See [Test strategy](TEST_STRATEGY.md) for what assertions can establish.

Formatting is separate human source maintenance, not a CI mutation. Consult the
selected CLI's help for supported formatting options; `bicep format infra/main.bicep`
rewrites source and should only be run intentionally, followed by diff review.
The check script performs local validation without formatting, cloud calls,
deployment, authenticated what-if, or package installation.

## Verified contracts

| Area | Completed verification |
| --- | --- |
| CLI and lint | Bicep 0.37.4 lint/build/build-params completed without diagnostics; configuration assertions passed. |
| Compiler representation | Fresh compiled module outputs, deployment references, dependency arrays, variable references, and nested `siteConfig` passed the contract suites. |
| Resource contracts | Linux reserved/SKU/capacity, identity, public-network controls, TLS/SCM, Shared Key, and default OAuth passed static assertions. |
| Inspector and fixtures | Inspector, storage/Web mutation tests, and security regressions passed, including expected negative-control failures. |
| Composition and parameters | Fresh artifacts passed resource inventory, safe-output, module wiring, and dev configuration checks. |
| Source and documentation | Layout, naming, check-script/workflow source patterns, local links, scope statements, editor conventions, and license assertions passed. |

## Technical limits

Static verification establishes the template contracts. It does not provision
resources, evaluate effective policy/RBAC, reserve names, establish regional SKU
availability, measure costs, or assess runtime security. The inspector does not
evaluate runtime expressions or linked/symbolic templates. Timestamp checks detect
stale artifacts but do not establish provenance; always rebuild through the script.

The reference contains no runtime application, private endpoints, or app-to-storage
authorization. Resources incur costs if separately deployed. See
[Architecture](ARCHITECTURE.md) and [Test strategy](TEST_STRATEGY.md).
