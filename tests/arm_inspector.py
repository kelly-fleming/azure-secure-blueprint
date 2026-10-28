"""Inspect ARM JSON structure only; never evaluate ARM or contact Azure.

Property keys retain exact JSON casing. Type lookups are case-insensitive.
Inline deployment templates are traversed; linked templates and symbolic resource
maps fail explicitly rather than producing an incomplete resource inventory.
"""

import json
from pathlib import Path


class InspectionError(AssertionError):
    """An artifact cannot establish the requested static contract."""


def parse_template(source, label='ARM JSON'):
    try:
        template = json.loads(source)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise InspectionError(f'{label}: invalid JSON: {error}') from error
    if not isinstance(template, dict):
        raise InspectionError(f'{label}: template root must be an object')
    return template


def load_template(path):
    path = Path(path)
    try:
        source = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as error:
        raise InspectionError(
            f'{path}: cannot read ARM artifact; generate fresh output with Bicep before inspection: {error}'
        ) from error
    return parse_template(source, str(path))


def walk_resources(template):
    """Yield resource objects from all inline template levels, including deployments."""
    if not isinstance(template, dict):
        raise InspectionError('Template must be an object')
    resources = template.get('resources')
    if not isinstance(resources, list):
        raise InspectionError('Template resources must be an array; missing or symbolic resources are unsupported')
    for index, resource in enumerate(resources):
        if not isinstance(resource, dict):
            raise InspectionError(f'Resource at index {index} must be an object')
        resource_type = resource.get('type')
        if not isinstance(resource_type, str) or not resource_type:
            raise InspectionError(f'Resource at index {index} is missing a string type')
        yield resource
        if resource_type.lower() == 'microsoft.resources/deployments':
            properties = resource.get('properties')
            if not isinstance(properties, dict) or not isinstance(properties.get('template'), dict):
                raise InspectionError(
                    f"Deployment {resource.get('name', '<unnamed>')}: inline properties.template required; linked/unresolved templates cannot be inspected"
                )
            yield from walk_resources(properties['template'])


def find_resources(template, resource_type):
    # Materialize traversal so unsupported branches cannot be hidden by an early match.
    return [resource for resource in walk_resources(template)
            if resource['type'].lower() == resource_type.lower()]


def require_resource(template, resource_type):
    matches = find_resources(template, resource_type)
    if len(matches) != 1:
        names = [resource.get('name', '<unnamed>') for resource in matches]
        raise InspectionError(f'Expected exactly one {resource_type}; found {len(matches)}: {names}')
    return matches[0]


def is_expression(value):
    """Recognize an ARM expression; [[ escapes a literal opening bracket in ARM."""
    return isinstance(value, str) and value.startswith('[') and not value.startswith('[[')


def require_literal(value, label='value'):
    """Return static JSON, rejecting expressions anywhere inside arrays/objects.

    Escaped ARM strings are retained exactly as authored, not decoded. This does
    not resolve parameters, variables, reference(), list*(), or other functions.
    """
    if is_expression(value):
        raise InspectionError(f'{label}: unresolved ARM expression; a static literal is required')
    if isinstance(value, dict):
        for key, child in value.items():
            require_literal(child, f'{label}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_literal(child, f'{label}[{index}]')
    return value


def require_property(resource, *path, literal=True):
    """Read exact-case object keys, requiring static values unless explicitly opted out."""
    value = resource
    traversed = []
    for key in path:
        traversed.append(key)
        if not isinstance(value, dict) or key not in value:
            raise InspectionError(f"Missing property {'.'.join(traversed)} (keys are case-sensitive)")
        value = value[key]
    label = '.'.join(path) or 'resource'
    return require_literal(value, label) if literal else value
