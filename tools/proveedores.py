"""Herramienta `buscar_proveedor` sobre data/proveedores.json"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from contracts.tool_schemas import BuscarTicketArgs

# Ruta fija: nunca se construye a partir de los argumentos del modelo.
TICKETS_DB = Path(__file__).resolve().parents[1] / "data" / "proveedores.json"
HISTORY_LIMIT = 3


@lru_cache(maxsize=1)
def _proveedores() -> dict[str, dict]:
    proveedores = json.loads(TICKETS_DB.read_text(encoding="utf-8"))
    return {proveedor["nombre"]: proveedor for proveedor in proveedores}

# TODO: type works but is not verbose
def buscar_proveedor(args: BuscarTicketArgs) -> dict:
    """nombre, servicio, sla, estado, email de contacto y contratos vigentes de un proveedor."""
    proveedor = _proveedores().get(args.nombre)
    if proveedor is None:
        return {"error": f"proveedor {args.nombre} no existe"}
    return {
        "nombre": proveedor["nombre"],
        "servicio": proveedor["servicio"],
        "sla_horas": proveedor["sla_horas"],
        "estado": proveedor["estado"],
        "contacto": proveedor["contacto"],
        "contratos_vigente": proveedor["contratos_vigentes"]
    }
