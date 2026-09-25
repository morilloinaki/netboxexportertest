import json

import pytest

from netbox_exporter.cli import parse_filters
from netbox_exporter.exporters import RESOURCES, flatten, get_path, write_csv, write_json

DEVICE_V4 = {
    "id": 7,
    "name": "sw-core-01",
    "status": {"value": "active", "label": "Active"},
    "role": {"name": "Core Switch"},
    "device_type": {"model": "C9500-24Y4C", "manufacturer": {"name": "Cisco"}},
    "site": {"name": "Madrid DC1"},
    "rack": None,
    "tenant": None,
    "primary_ip": {"address": "10.0.0.1/24"},
    "serial": "FDO1234X",
}

DEVICE_V3 = {**DEVICE_V4, "role": None, "device_role": {"name": "Legacy Role"}}


def test_get_path_nested():
    assert get_path(DEVICE_V4, "device_type.manufacturer.name") == "Cisco"


def test_get_path_missing_returns_none():
    assert get_path(DEVICE_V4, "rack.name") is None
    assert get_path(DEVICE_V4, "nope.nada") is None


def test_flatten_netbox_4():
    row = flatten(DEVICE_V4, RESOURCES["devices"]["columns"])
    assert row["role"] == "Core Switch"
    assert row["primary_ip"] == "10.0.0.1/24"
    assert row["status"] == "active"


def test_flatten_falls_back_to_netbox_3_fields():
    row = flatten(DEVICE_V3, RESOURCES["devices"]["columns"])
    assert row["role"] == "Legacy Role"


def test_parse_filters():
    assert parse_filters(["site=madrid", "tag=core=x"]) == {"site": "madrid", "tag": "core=x"}


def test_parse_filters_invalid():
    with pytest.raises(Exception):
        parse_filters(["sinigual"])


def test_writers(tmp_path):
    cols = RESOURCES["devices"]["columns"]
    rows = [flatten(DEVICE_V4, cols)]

    csv_path = tmp_path / "d.csv"
    assert write_csv(iter(rows), list(cols), csv_path) == 1
    assert "sw-core-01" in csv_path.read_text()

    json_path = tmp_path / "d.json"
    assert write_json(iter(rows), json_path) == 1
    assert json.loads(json_path.read_text())[0]["site"] == "Madrid DC1"
