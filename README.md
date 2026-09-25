# netbox-exporter

[![tests](https://github.com/morilloinaki/netboxexportertest/actions/workflows/tests.yml/badge.svg)](https://github.com/morilloinaki/netboxexportertest/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A small command-line tool to pull inventory out of [NetBox](https://github.com/netbox-community/netbox) into **CSV** or **JSON**. Handy for audits, quick reports or feeding other scripts without fighting the API.

- Automatic pagination (50 or 50,000 devices, doesn't matter)
- Native API filters (`site`, `tenant`, `status`, `tag`…)
- Compatible with NetBox 3.x and 4.x
- No weird dependencies: just `requests`

## Supported resources

| Resource       | Endpoint              |
|----------------|-----------------------|
| `devices`      | `dcim/devices`        |
| `sites`        | `dcim/sites`          |
| `ip-addresses` | `ipam/ip-addresses`   |
| `prefixes`     | `ipam/prefixes`       |
| `vlans`        | `ipam/vlans`          |

## Installation

```bash
git clone https://github.com/morilloinaki/netboxexportertest.git
cd netboxexportertest
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

```bash
cp .env.example .env
# edit .env with your NetBox URL and token
export $(grep -v '^#' .env | xargs)
```

The token only needs read permissions.

| Variable            | Description                          | Default |
|---------------------|--------------------------------------|---------|
| `NETBOX_URL`        | Base URL of your NetBox instance     | —       |
| `NETBOX_TOKEN`      | API token                            | —       |
| `NETBOX_VERIFY_SSL` | Set to `false` to skip SSL checks    | `true`  |

## Usage

```bash
# All devices to CSV
netbox-export devices

# Several resources to JSON in a custom folder
netbox-export devices prefixes vlans -f json -o reports/

# Everything, filtered by site and status
netbox-export all --filter site=madrid-dc1 --filter status=active

# Lab with a self-signed certificate
netbox-export sites --insecure
```

Sample output:

```
✓ devices          1342 records → export/devices.csv (2.8s)
✓ prefixes          418 records → export/prefixes.csv (0.6s)
✓ vlans             212 records → export/vlans.csv (0.4s)
```

## Adding a new resource

Just add an entry to `RESOURCES` in `netbox_exporter/exporters.py` with the endpoint and the columns you want. Each column accepts several fallback paths in case a field changes between NetBox versions:

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

Tests run automatically on every push and pull request via GitHub Actions.

## License

MIT
