# Nonsecret parameters and naming contracts

`infra/main.bicep` targets an existing resource group. Nothing has been deployed.
Its interface configures three local resource modules. No Azure account is needed
to edit this source.

| Parameter | Type and default | Contract |
| --- | --- | --- |
| `environment` | string, `dev` | Only `dev` is allowed. |
| `location` | string, `resourceGroup().location` | Shared Azure region; availability remains an operator check. |
| `projectPrefix` | string, `demo` | 2-6 characters; use lowercase ASCII letters and digits. |
| `uniqueSuffix` | string, `sample01` | 6-12 characters; use lowercase ASCII letters and digits; choose globally unique final names. The fictional default does not guarantee availability. |
| `appServicePlanSku` | string, `B1` | Allowed B1, B2, B3 Linux Basic SKUs; all are cost-bearing if deployed. |
| `tags` | object, environment `dev` and project `fictional-blueprint` | Shared nonsecret tags; do not put credentials or private identifiers in tags. |

Length and allowed-value decorators constrain the interface. For naming, uppercase
ASCII letters are lowercased and each character outside ASCII letters/digits is
replaced with `0`. The source performs this normalization before composing every
name so arbitrary punctuation cannot produce invalid name characters. Supply the
documented lowercase alphanumeric inputs instead of relying on replacement.
Different inputs can normalize to the same name; no global uniqueness is asserted.

## Deterministic names

With `p` and `s` the normalized prefix and suffix:

| Resource | Formula | Length from input bounds | Fictional default |
| --- | --- | --- | --- |
| StorageV2 | `p + environment + s` | 11-21 | `demodevsample01` |
| App Service Plan | `p-dev-plan-s` | 18-28 | `demo-dev-plan-sample01` |
| Web App | `p-dev-web-s` | 17-27 | `demo-dev-web-sample01` |

The storage name contains only lowercase ASCII alphanumerics and stays within
Azure's 3-24 character limit. Plan names stay within 1-60 characters using a
restricted alphanumeric/hyphen subset; Web App names stay within 2-60 characters
and start/end with alphanumeric characters. See Microsoft's
[resource naming restrictions](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules)
and [parameter decorators](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/parameters).
Name availability, reserved words, regional SKU support, and provider acceptance
still need operator review. Syntactically safe names are not evidence of availability.

## Module and output boundaries

The storage module receives name/location/tags; the plan module receives
name/location/tags/SKU; the Web App receives name/location/tags and the plan ID.
Location and tags are passed to all modules, and SKU to the plan. The Web App
plan ID is wired from `plan.outputs.planId`; storage remains independent.

Outputs `storageName`, `planName`, `appName`, `storageId`, `planId`, `appId`, and
`principalId` are wired from module outputs. Their values resolve at deployment;
none is evidence of a deployed resource. A principal
ID is not a credential, but its value requires the identity to exist at deployment.

There are no secret parameters or public-network-access overrides. The required
first-release module posture is `publicNetworkAccess: 'Disabled'` for both Web App
and storage, fixed in their resource definitions. No private networking, RBAC,
or application connection settings are included in composition.
Compiled-template tests require
a newly generated `build/main.json`; they do not evaluate ARM naming expressions
or check global uniqueness. Compilation and parameter contract tests passed in
Docker on 2026-10-28.

## Fictional dev example

`params/dev.bicepparam` uses `using '../infra/main.bicep'` and explicitly assigns
all six parameters. It selects `dev`, region `eastus`, prefix `demo`, suffix
`sample01`, and Basic SKU `B1`. Its environment/project/purpose tags describe only
this fictional source example and contain no private organization information.
It includes no subscription IDs, tenant addresses, resource IDs, or credentials.

These values produce `demodevsample01`, `demo-dev-plan-sample01`, and
`demo-dev-web-sample01` under the deterministic naming rules above. The storage
and Web App names must be globally unique; the example suffix does not establish
uniqueness or reserve names. Choose an appropriate lowercase alphanumeric suffix
within the documented bounds before any separately authorized deployment.
The illustrative `eastus` region is not a placement recommendation. Select a
region with suitable Linux Basic availability, quota, and provider support before
deployment. B1 is the lowest Basic SKU allowed by this interface and remains
cost-bearing if provisioned; no price or measured-cost claim is made.

Parameter compilation and binding checks passed in Docker on 2026-10-28.
The compiled example contains the six documented parameters and fictional tags.
An example parameter file is not proof of deployment. Source assertions in
`tests/test_dev_params.py` cover the explicit parameter set, name syntax, and common
identifier/secret patterns; they are not a comprehensive secret scanner or a
substitute for compiler validation.
