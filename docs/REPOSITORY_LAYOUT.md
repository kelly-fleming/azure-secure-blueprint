# Source layout

`infra/main.bicep` is the resource-group-scoped entry point. It defines nonsecret
parameters, composes three resource modules, and returns nonsecret outputs.
`infra/modules/` contains the local Bicep modules;
it does not depend on generated templates or downloaded modules.

`params/dev.bicepparam` binds to the entry point with explicit fictional dev
assignments. Only nonsecret development configuration belongs here. Authored
Bicep and Bicep parameter files must remain trackable.

`tests/` contains Python unittest source checks, compiled ARM assertions, and
independent synthetic security regression fixtures. Compiled tests require fresh
`build/` artifacts. `scripts/check.sh` defines the offline lint/build/test pipeline
with tool preflight and stale-output removal. `Dockerfile` packages Bicep and Python
to run that same pipeline; see [Validation](VALIDATION.md) for observed results.

`docs/` holds architecture, trust boundaries, security limitations, and
validation instructions. This layout note is
not an architecture or security assessment.

`build/`, `.bicep/`, Python caches, `.venv/`, local environment files, credential
files, Terraform state, private PEM/PFX files, and Azure profile directories are
ignored local artifacts. Do not store secrets in source files even if their
extensions are trackable. Generated output is not required to establish the
source layout and must not be committed.
