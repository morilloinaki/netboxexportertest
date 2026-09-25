"""Punto de entrada de línea de comandos."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .client import NetBoxClient, NetBoxError
from .exporters import RESOURCES, flatten, write_csv, write_json


def parse_filters(raw: list[str]) -> dict[str, str]:
    filters = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Filtro inválido '{item}', usa clave=valor")
        key, value = item.split("=", 1)
        filters[key.strip()] = value.strip()
    return filters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netbox-export",
        description="Exporta inventario de NetBox a CSV o JSON.",
    )
    parser.add_argument("resources", nargs="+", choices=[*RESOURCES, "all"],
                        help="Qué exportar (o 'all')")
    parser.add_argument("-f", "--format", choices=["csv", "json"], default="csv")
    parser.add_argument("-o", "--output", default="export", help="Carpeta de salida")
    parser.add_argument("--filter", action="append", default=[], metavar="CLAVE=VALOR",
                        help="Filtro de la API de NetBox, repetible (ej: --filter site=madrid)")
    parser.add_argument("--insecure", action="store_true", help="No verificar SSL")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    resources = list(RESOURCES) if "all" in args.resources else args.resources

    try:
        filters = parse_filters(args.filter)
        client = NetBoxClient.from_env(verify_ssl=False if args.insecure else None)
    except (argparse.ArgumentTypeError, NetBoxError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in resources:
        spec = RESOURCES[name]
        start = time.perf_counter()
        target = out_dir / f"{name}.{args.format}"
        try:
            rows = (flatten(r, spec["columns"]) for r in client.get_all(spec["endpoint"], **filters))
            if args.format == "csv":
                count = write_csv(rows, list(spec["columns"]), target)
            else:
                count = write_json(rows, target)
        except NetBoxError as exc:
            print(f"✗ {name}: {exc}", file=sys.stderr)
            continue
        elapsed = time.perf_counter() - start
        print(f"✓ {name:<13} {count:>6} registros → {target} ({elapsed:.1f}s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
