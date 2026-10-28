# Offline validation workflow

Local lint, compilation, parameter compilation, and all 72 unittest cases passed
in Docker on 2026-10-28, using Bicep 0.37.4 and Python 3.12. The runner had networking
disabled. Nothing has been deployed. No Azure account, Azure CLI,
subscription, credentials, or authentication is required for these local checks.

The [Docker workflow](QUICKSTART.md#docker-workflow) installs the local tools during
image build and runs this same script. Rebuild the image after changing sources.
GitHub Actions execution, action/download integrity review, provider acceptance,
regional availability, effective permissions, and runtime isolation remain
unverified. The original task records describe the earlier source-only handoff;
they are historical records, superseded for local execution by this result.

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

Successful completion would mean those commands returned successfully, not that
Azure accepted a deployment or that runtime security is proven. A failure stops
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
The check script contains no formatting, cloud calls, deployment, publication,
authenticated what-if, or package installation. No passing CI, deployment compatibility, or production readiness
is claimed by this document.

## GitHub Actions

`.github/workflows/ci.yml` defines **CI**, job **checks**, for every push and pull
request on Ubuntu 24.04. It grants only `contents: read`, disables checkout credential
persistence, and cancels older runs of the same workflow/ref. It sets up Python
3.12, downloads standalone Bicep v0.37.4 to the runner's temporary directory, adds
that directory to PATH, then invokes `bash scripts/check.sh`. Download and check
failures remain failures; no security tests are skipped. The job has a 15-minute
timeout. No Azure secrets, login, cloud extensions, or deployment steps exist.

The setup uses published [checkout v4](https://github.com/actions/checkout/tree/v4)
and [setup-python v5](https://github.com/actions/setup-python/tree/v5) tags. Full
action commit SHAs have not been verified/pinned; tags can move. Final operator
review must verify action refs, prefer reviewed immutable SHA pins, and review
Bicep download integrity using the [official v0.37.4 release](https://github.com/Azure/bicep/releases/tag/v0.37.4).
The binary URL is pinned to that release's `bicep-linux-x64` asset; no checksum or
signature verification is claimed. Network access is needed for CI tool setup,
while `check.sh` itself performs local checks without cloud calls.

No workflow has been run or published by this implementation. Static source tests
in `tests/test_ci_workflow.py` inspect the authored layout and include negative
cases for removed checks, suppressed failure, and write permission. They do not
parse arbitrary YAML or establish GitHub Actions runtime behavior. The operator
must inspect an actual run before treating `checks` as a verified merge gate.

## Operator handoff checklist

The original implementation records for tasks 001-021 were IMPLEMENTED_UNVERIFIED.
The authorized local Docker run now supplies lint/build/test evidence. The following
checklist remains relevant for independent reproduction and publication review.
No cloud deployment or authenticated validation is part of this checklist.

- [ ] Review the intended checkout/commit and working diff, including staged and
  tracked files, for secrets, private identifiers, generated output, unrelated
  changes, and license/publication suitability. Keep `build/` and private operator
  records local. Do not infer tracked-file safety from ignore rules alone.
- [ ] Install the pinned standalone Bicep 0.37.4 and Python >=3.12, verify actual
  versions and binary provenance/integrity, and review published action refs before
  execution. The pinned CLI accepted the configured rules in the local Docker run.
- [ ] Run `bash scripts/check.sh` in a clean checkout. Preserve actual command
  output and exit status. Investigate every lint, compilation, parameter binding,
  or unittest failure; correct the cause and rerun from fresh artifacts. Do not
  weaken a security assertion merely to match unexpected output.
- [ ] Inspect `build/main.json`, including nested deployment templates. Confirm
  exactly the plan/site/storage resource contracts, fixed security literals,
  Web App dependency and plan reference, storage independence, and identifier-only
  outputs. Reject extra role assignments, containers, cloud scripts or resources.
- [ ] Inspect `build/dev.parameters.json` for only the six configuration fields
  and fictional nonsecret tags/values. Review name bounds, normalization collision
  risk, region/SKU assumptions and lack of global uniqueness evidence.
- [ ] Review README/quickstart, architecture, threat model, SECURITY.md,
  contribution guide and LICENSE. Review reporting
  contact preferences and actual channel availability. Check links and setup in
  the clean checkout. No runtime assurance or measured-cost claim is supported.
- [ ] Open a focused PR and verify the actual CI `checks` result for its exact
  commit. Confirm tool download, lint/build/build-params and every unittest ran
  successfully with no suppressed or skipped failures. All CI behavior is UNVERIFIED.
- [ ] Configure and verify the main ruleset/required `checks` gate after CI is
  known to work; do not assume repository files enable enforcement. Follow the
  solo-maintainer review convention without imposing a reviewer count.
- [ ] Squash merge through the reviewed PR, then verify CI for the resulting main
  commit. A passing PR run is not evidence of a passing main run.
- [ ] Human maintainer only: prepare any release notes after verification and
  state actual results. Release notes are optional and are not required by CI.
  Tag from the final verified main commit and publish only after the release
  review; no automated tagging or publication is authorized here.

## Evidence and remaining assertions

Local evidence establishes template intent only; remaining questions are not
claims that a failure has occurred:

| Area | Authored assertions and unresolved evidence |
| --- | --- |
| CLI and lint | Bicep 0.37.4 lint/build/build-params completed without diagnostics. Configuration source checks passed. |
| Compiler representation | Fresh compiled module output expressions, deployment references, dependency arrays, variable references and nested `siteConfig` passed the contract suites. |
| Provider contract | Linux reserved/SKU/capacity, identity, public-network controls, TLS/SCM, Shared Key and default OAuth passed static assertions. No Azure deployment acceptance is claimed. |
| Inspector and fixtures | Inspector, storage/Web mutation tests and security regressions passed, including named negative-control failures. The inspector does not evaluate runtime expressions or linked/symbolic templates. |
| Composition and parameters | Fresh artifacts passed inventory, safe-output and dev configuration checks. Timestamp checks cannot prove provenance; rebuild through the script. |
| Source and documentation | Layout, naming, script/CI source patterns, links, scope statements, editor conventions and license passed their authored checks. Documentation patterns are not comprehensive claim or secret scanners. |
| CI and trust | Action refs, binary integrity, runner behavior, complete test discovery, actual green status and ruleset enforcement require operator evidence. Major action tags are mutable. |

No runtime properties, policy, effective permissions, name availability or actual
costs become verified merely because these static checks eventually pass.
