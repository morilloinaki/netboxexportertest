# netbox-exporter

Pequeña herramienta de línea de comandos para sacar inventario de [NetBox](https://github.com/netbox-community/netbox) a **CSV** o **JSON**. Útil para auditorías, informes rápidos o para alimentar otros scripts sin pelearse con la API.

- Paginación automática (da igual que tengas 50 o 50.000 dispositivos)
- Filtros nativos de la API (`site`, `tenant`, `status`, `tag`…)
- Compatible con NetBox 3.x y 4.x
- Sin dependencias raras: solo `requests`

## Recursos soportados

| Recurso        | Endpoint              |
|----------------|-----------------------|
| `devices`      | `dcim/devices`        |
| `sites`        | `dcim/sites`          |
| `ip-addresses` | `ipam/ip-addresses`   |
| `prefixes`     | `ipam/prefixes`       |
| `vlans`        | `ipam/vlans`          |

## Instalación

```bash
git clone https://github.com/morilloinaki/netbox-exporter.git
cd netbox-exporter
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuración

```bash
cp .env.example .env
# edita .env con tu URL y token
export $(grep -v '^#' .env | xargs)
```

El token necesita solo permisos de lectura.

## Uso

```bash
# Todos los dispositivos a CSV
netbox-export devices

# Varios recursos a JSON en otra carpeta
netbox-export devices prefixes vlans -f json -o informes/

# Todo, filtrando por sede y estado
netbox-export all --filter site=madrid-dc1 --filter status=active

# Lab con certificado autofirmado
netbox-export sites --insecure
```

Salida de ejemplo:

```
✓ devices          1342 registros → export/devices.csv (2.8s)
✓ prefixes          418 registros → export/prefixes.csv (0.6s)
✓ vlans             212 registros → export/vlans.csv (0.4s)
```

## Añadir un recurso nuevo

Basta con añadir una entrada en `RESOURCES` (`netbox_exporter/exporters.py`) indicando el endpoint y las columnas. Cada columna admite varias rutas alternativas por si el campo cambia entre versiones:

```python
"circuits": {
    "endpoint": "circuits/circuits",
    "columns": {
        "cid": ["cid"],
        "provider": ["provider.name"],
        "status": ["status.value"],
    },
},
```

## Tests

```bash
pytest
```

## Licencia

MIT
