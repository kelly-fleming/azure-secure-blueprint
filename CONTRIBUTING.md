# Contributing

This is a fictional, source-only reference. Nothing has been deployed; no runtime
application or production-readiness claim is included. Local checks passed in
Docker on 2026-10-28. The source-only release is validated and ready to publish.
See [Security](SECURITY.md) for limitations and private reporting guidance; do not
open public issues containing sensitive details.

## Scope and checks

Start a feature branch from current main and keep each change limited to one
coherent requirement. Preserve unrelated work. Describe the behavior changed,
security implications, and evidence available. Do not introduce credentials in
source, parameters, tags, fixtures, logs, or PR descriptions. Use fictional,
nonsecret inputs; do not include subscription/tenant identifiers or customer data.
Generated `build/` output remains local and ignored.

Follow `.editorconfig`: UTF-8, LF, final newline, spaces, two-space infrastructure/
shell/document indentation and four-space Python indentation. Formatting is human
source maintenance; CI does not rewrite files. Do not use formatting as an excuse
to modify unrelated source.

When execution is authorized, install the documented standalone Bicep CLI and
Python >=3.12 and run the supported workflow from the repository root:

```bash
bash scripts/check.sh
```

For direct investigation, the corresponding commands are:

```bash
mkdir -p -- build
rm -f -- build/main.json build/dev.parameters.json
bicep lint infra/main.bicep
bicep build infra/main.bicep --outfile build/main.json
bicep build-params params/dev.bicepparam --outfile build/dev.parameters.json
python -m unittest discover -s tests -v
```

Stop on any failure and rebuild fresh output after corrections. Python source and
compiled-ARM assertions must match the actual contract. For changed security
controls, author independent positive and negative regression fixtures calling the
same validators; require the intended failing field rather than an unrelated
exception. Do not remove tests or suppress failures to obtain green checks.
No Azure credentials are required for local checks or CI. Do not add cloud login,
deployment, or authenticated what-if to the check script or CI workflow.

See [Validation](docs/VALIDATION.md), [Toolchain](docs/TOOLCHAIN.md), and
[Test strategy](docs/TEST_STRATEGY.md) for setup, pins, freshness and evidence limits.

## Code review

Open a PR from the feature branch with a concise description of the changed
behavior and completed validation results. Review module parameter/output wiring,
fixed security defaults, regression cases, documentation, and accidental secrets.
A solo maintainer may perform this review.

Prepare release documentation in the same change as the code. Describe the
implemented behavior, completed checks, and technical scope.
