# Linux App Service Plan

`infra/modules/app-plan.bicep` defines one resource-group-scoped
`Microsoft.Web/serverfarms@2024-04-01` resource. This stable API choice follows
[the toolchain policy](TOOLCHAIN.md) and the Microsoft
[serverfarms resource reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.web/2024-04-01/serverfarms).
The plan is Linux (`kind: 'linux'`, `properties.reserved: true`).

Inputs are `name`, `location`, nonsecret `tags`, and `sku`. The name is bounded to
1-60 characters; the main parameter contract supplies a narrower alphanumeric and
hyphen name. The SKU defaults to `B1` and permits `B1`, `B2`, or `B3`, matching the
entry point's `appServicePlanSku` choices. Tier is fixed to `Basic`, with explicit
capacity of one worker. Free, Shared, Windows, and other SKU tiers are outside this
module's contract. Region availability, quota, provider acceptance, and current
pricing require independent operator review.

Outputs are only `planId` and `planName`. The ID is a nonsecret resource ID that
main composition passes to the Web App as its plan reference. No credentials,
publishing profiles, or runtime state are retrieved. `infra/main.bicep` calls this
module with the selected SKU, deterministic name, location, and shared tags.

The plan SKU is cost-bearing if provisioned, even without a Web App workload or
traffic. No runtime workload, application code, or artifact deployment is included
in this module. A plan's compute capacity does not create a storage connection or
grant permissions. Nothing has been deployed, and no cost measurement or runtime
security result is claimed.

`tests/test_compute_contract.py` contains independent nested-template traversal
and assertions for the resource type/API, Linux settings, Basic SKU parameter
contract, explicit capacity, and ID/name-only outputs. It expects fresh
`build/main.json` after composition and compilation; missing output or an absent
plan fails explicitly. It checks known ARM expressions structurally without
evaluating deployment parameters or claiming Azure acceptance. No compilation,
tests, or other execution checks have been performed.
