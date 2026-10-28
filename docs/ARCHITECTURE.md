# Architecture and trust boundaries

This is a fictional, source-only reference architecture. Nothing has been deployed.
It is not production-ready. The entry point composes three local resource modules;
the resources and controls below describe authored template intent,
not evidence of running infrastructure. No Azure account is needed to edit source.

## Scope and components

`infra/main.bicep` targets an existing resource group (`targetScope = 'resourceGroup'`).
It will not create the resource group or subscription-level resources. All three
resources belong to that one resource group:

| Source responsibility | Intended resource and contract |
| --- | --- |
| `infra/main.bicep` | Compose local modules with shared location, tags, and deterministic names; pass the plan resource ID to the Web App. |
| `infra/modules/app-plan.bicep` | Linux App Service Plan providing compute capacity; return nonsecret resource ID/name. |
| `infra/modules/web-app.bicep` | Linux Web App on that plan with system-assigned managed identity; return nonsecret resource ID/name and identity principal ID. |
| `infra/modules/storage.bicep` | Independent StorageV2 account; return nonsecret resource ID/name. |

All three local modules and main composition are authored. Shared location and
tags flow to every module; the plan also receives the selected SKU. The Web App
receives `plan.outputs.planId`, establishing its dependency on the plan deployment.
Storage has no dependency on the plan or Web App and grants neither access.
Main outputs only storage/plan/app names and IDs plus the identity principal ID;
the values resolve during deployment and are not observed resource evidence.
There is no code or artifact deployment and no runtime application. The plan's
compute association does not create a data path to storage.

## Component and data-flow diagram

```text
Local authored sources (no cloud connection needed for editing)
  main.bicep -- intended module composition --> Azure control plane
                                                |
                          existing resource group boundary
                          +------------------------------------+
                          | Linux App Service Plan             |
                          |   ^ plan ID / hosting association  |
                          | Linux Web App                      |
                          |   system-assigned managed identity |
                          |                                    |
                          | Independent StorageV2 account      |
                          +------------------------------------+

Internet clients --X--> Web App public data plane
Internet clients --X--> Storage public data plane
Web App          --X--> Storage data plane (no connection or RBAC)

X = intentionally absent or blocked path in the intended configuration.
No application traffic or deployed resource is represented as observed evidence.
```

The control-plane composition arrows describe resource configuration dependencies,
not application requests. The resource group is a management scope, not a network
isolation boundary. Each data plane has its own access controls; sharing a resource
group does not authorize access between resources.

## Access and identity boundaries

Public network access will be disabled by default for both Web App and storage,
with no public-access override in the first release. Endpoints remain inaccessible
until private networking is implemented in a future release. This release supplies
no private endpoints, private DNS, or other authorized network path; it does not
offer a functioning public website or a storage connectivity demonstration.

A managed identity alone grants no storage permissions. It provides an identity
that could later authenticate, but authorization needs an explicit role assignment
and data-plane reachability needs a network path. There are no role assignments
(RBAC), App Service-to-storage connections, storage credentials, or application
settings connecting the resources. The storage account remains independent.
No secret outputs, account keys, or connection strings are part of the contracts.

## Evidence and operational limits

Compilation and source assertions, when implemented and run, can inspect template
intent; they cannot prove deployed network isolation, effective authorization,
provider acceptance, global name uniqueness, regional SKU availability, or runtime
security. Neither compilation nor live validation has been performed here.

The App Service Plan and storage are cost-bearing resources if deployed, even
without application traffic. This repository does not provision resources or
provide a measured cost estimate. Any future operator must review pricing and
deployment suitability independently. Networking, application delivery, and
authorization are later work and are not implicitly enabled by this design.
