"""Reporte de llamadas al LLM a partir de logs/llm_calls.jsonl.

Uso:
    uv run scripts/report.py [ruta/al/archivo.jsonl]
"""

from __future__ import annotations

import json
from posix import stat
import sys
from pathlib import Path
import statistics

DEFAULT_PATH = Path("logs/llm_calls.jsonl")

# type for jsonl file elements
class Event:
    def __init__(self, data: dict[str, str | int | float]):
        self.request_id = data["request_id"]
        self.timestamp = data["timestamp"]
        self.provider = data["provider"]
        self.model = data["model"]
        self.tokens_in = data["tokens_in"]
        self.tokens_out = data["tokens_out"]
        self.latency_ms: float | None = float(data["latency_ms"]) if data["latency_ms"] is not None else None
        self.ttft_ms: float | None = float(data["ttft_ms"]) if data["ttft_ms"] is not None else None
        self.cost_usd: float | None = float(data["cost_usd"]) if data["cost_usd"] is not None else None
        self.fallback = data["fallback"]
        self.success = data["success"]
        self.error_type: str | None = data["error_type"] if data["error_type"] is not None else None
        self.prompt_chars = data["prompt_chars"]

class Report:
    def __init__(self, events: list[Event]):
        self.events = events
        self.latencia_p50 = statistics.quantiles([event.latency_ms for event in events if event.latency_ms is not None and event.success], n=100)[49]
        self.latencia_p95 = statistics.quantiles([event.latency_ms for event in events if event.latency_ms is not None and event.success], n=100)[94]
        self.costo_total = sum(event.cost_usd for event in events if event.cost_usd is not None)
        self.llamadas_con_fallback = sum(1 for event in events if event.fallback)
        self.llamadas_por_proveedor: dict[str, int] = {}
        for event in events:
            self.llamadas_por_proveedor[event.provider] = self.llamadas_por_proveedor.get(event.provider, 0) + 1

    def __str__(self) -> str:
        llamadas_por_proveedor_str = "\n".join([f"{provider}: {count}" for provider, count in self.llamadas_por_proveedor.items()])
        return f"""
        Costo total: {self.costo_total}
        Latencia p50: {self.latencia_p50}
        Latencia p95: {self.latencia_p95}
        Llamadas con fallback: {self.llamadas_con_fallback}
        Llamadas por proveedor:
            {llamadas_por_proveedor_str}
        """



def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(argv[0]) if argv else DEFAULT_PATH

    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else None
    if lines is None:
        print(f"Archivo no encontrado: {path}")
        return 1
    if len(lines) == 0:
        print(f"Archivo vacío: {path}")
        return 1
    events: list[Event] = [Event(json.loads(line)) for line in lines if line.strip()]
    print(f"Llamadas registradas: {len(events)}")

    # TODO(clase-1): completa el reporte. Debe imprimir:
    #   - costo total en USD,
    #   - latencia p50 y p95 (solo llamadas exitosas; usa statistics.quantiles),
    #   - % de llamadas con fallback,
    #   - número de llamadas por proveedor.
    # Usa solo la librería estándar y maneja con un mensaje el caso de que el archivo
    # no exista o esté vacío.

    report = Report(events)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
