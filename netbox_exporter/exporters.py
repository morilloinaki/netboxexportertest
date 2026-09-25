"""Definición de recursos exportables y escritura a CSV/JSON."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

# Cada columna puede tener varias rutas alternativas: así funciona
# tanto con NetBox 3.x (device_role, site) como con 4.x (role, scope).
RESOURCES: dict[str, dict[str, Any]] = {
    "devices": {
        "endpoint": "dcim/devices",
        "columns": {
            "id": ["id"],
            "name": ["name"],
            "status": ["status.value"],
            "role": ["role.name", "device_role.name"],
            "device_type": ["device_type.model"],
            "manufacturer": ["device_type.manufacturer.name"],
            "site": ["site.name"],
            "rack": ["rack.name"],
            "tenant": ["tenant.name"],
            "primary_ip": ["primary_ip.address"],
            "serial": ["serial"],
        },
    },
    "ip-addresses": {
        "endpoint": "ipam/ip-addresses",
        "columns": {
            "id": ["id"],
            "address": ["address"],
            "status": ["status.value"],
            "dns_name": ["dns_name"],
            "vrf": ["vrf.name"],
            "tenant": ["tenant.name"],
            "assigned_to": ["assigned_object.device.name", "assigned_object.virtual_machine.name"],
            "interface": ["assigned_object.name"],
            "description": ["description"],
        },
    },
    "prefixes": {
        "endpoint": "ipam/prefixes",
        "columns": {
            "id": ["id"],
            "prefix": ["prefix"],
            "status": ["status.value"],
            "vrf": ["vrf.name"],
            "site": ["scope.name", "site.name"],
            "vlan": ["vlan.name"],
            "tenant": ["tenant.name"],
            "is_pool": ["is_pool"],
            "description": ["description"],
        },
    },
    "vlans": {
        "endpoint": "ipam/vlans",
        "columns": {
            "id": ["id"],
            "vid": ["vid"],
            "name": ["name"],
            "status": ["status.value"],
            "group": ["group.name"],
            "site": ["site.name"],
            "tenant": ["tenant.name"],
        },
    },
    "sites": {
        "endpoint": "dcim/sites",
        "columns": {
            "id": ["id"],
            "name": ["name"],
            "slug": ["slug"],
            "status": ["status.value"],
            "region": ["region.name"],
            "tenant": ["tenant.name"],
            "facility": ["facility"],
        },
    },
}


def get_path(obj: Any, path: str) -> Any:
    """Devuelve obj['a']['b']['c'] para 'a.b.c', o None si algo falta."""
    for key in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def flatten(record: dict, columns: dict[str, list[str]]) -> dict[str, Any]:
    row = {}
    for column, paths in columns.items():
        value = None
        for path in paths:
            value = get_path(record, path)
            if value not in (None, ""):
                break
        row[column] = value
    return row


def write_csv(rows: Iterable[dict], columns: list[str], path: Path) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def write_json(rows: Iterable[dict], path: Path) -> int:
    data = list(rows)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(data)
