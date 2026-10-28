# Isolated Linux Web App contract

`infra/modules/web-app.bicep` defines a resource-group-scoped Linux Web App using
`Microsoft.Web/sites@2024-04-01`. Inputs are `name`, `location`, nonsecret `tags`,
and `planId`. The caller supplies the resource ID of a compatible Linux App Service
Plan in the same region; main composition obtains it from the plan module.
The name must follow the main naming contract; decorators bound it to 2-60
characters. `infra/main.bicep` calls the module with `plan.outputs.planId`,
establishing the deployment dependency without any storage connection.

The resource uses `kind: 'app,linux'` with system-assigned managed identity. Fixed
properties require HTTPS, disable public network access, and set main and SCM
minimum TLS to `1.2`. `siteConfig.ftpsState` is `Disabled` and
`siteConfig.remoteDebuggingEnabled` is `false`. These controls are not exposed as
parameters. The chosen API's property contract is documented in Microsoft's
[sites reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.web/2024-04-01/sites).

Platform runtime settings are intentionally minimal: no language stack version,
container image, startup command, app settings, publishing credentials, or package
is configured. No code or artifact deployment and no runtime application are
included. This is an infrastructure shell, not a functioning application or
public website. A future workload must make its own explicit runtime choices.

Public endpoints remain inaccessible until future private networking is
implemented; no private endpoints, DNS, public-access exceptions, or network
integration are supplied here. No storage connection or RBAC assignment exists.
A managed identity alone grants no storage permissions. Authentication identity,
network reachability, and authorization are separate requirements.

Only nonsecret `appId`, `appName`, and `principalId` are output. A principal ID is
an identity identifier, not a credential. Its expression is resolved by Azure only
when the Web App identity exists at deployment; source inspection and template
compilation cannot supply or verify an actual principal ID. No runtime references
are treated as verified values by the static assertions.

Nothing has been deployed. These settings describe template intent and do not
establish production readiness, effective policy, provider acceptance, or runtime
security. The associated plan is cost-bearing if deployed. Tests in
`tests/test_web_security_contract.py` inspect the future nested resource in fresh
`build/main.json` after composition. They require literal values for fixed security
controls, check plan-reference/output wiring structurally, and fail explicitly
when the artifact or Web App is missing. No compilation, tests, or live checks have
been run.
