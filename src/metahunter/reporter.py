#!/usr/bin/env python3
# reporter.py
# Resume logs .jsonl (JSON Lines) de /examples o archivos sueltos y genera reportes JSON/CSV/Markdown.

import argparse, json, sys, csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Iterable, Tuple
from collections import Counter, defaultdict

# --------- Utilidades ---------
ISO_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
)

def parse_ts(s: str):
    for f in ISO_FORMATS:
        try:
            return datetime.strptime(s, f)
        except Exception:
            pass
    return None

def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                yield obj
            except json.JSONDecodeError as e:
                sys.stderr.write(f"[WARN] {path.name}:{i} no es JSON válido: {e}\n")

def iter_logs(paths: List[Path]) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    for p in paths:
        if p.is_dir():
            for f in sorted(p.rglob("*.jsonl")):
                for obj in load_jsonl(f):
                    yield f, obj
        elif p.is_file():
            for obj in load_jsonl(p):
                yield p, obj
        else:
            sys.stderr.write(f"[WARN] Ruta no encontrada: {p}\n")

# --------- Agregación ---------
def aggregate(records: Iterable[Tuple[Path, Dict[str, Any]]]) -> Dict[str, Any]:
    total = 0
    level_counts = Counter()
    status_counts = Counter()
    task_counts = Counter()
    durations = []
    inputs = outputs = 0
    first_ts = last_ts = None

    examples = []  # primeras N entradas para mostrar en el MD
    N_EXAMPLES = 5

    for src_path, r in records:
        total += 1

        level = str(r.get("level", "")).lower() or "info"
        status = str(r.get("status", "")).lower() or ("ok" if level in ("info","debug") else level)
        task = r.get("task") or r.get("module") or r.get("name") or "unknown"

        level_counts[level] += 1
        status_counts[status] += 1
        task_counts[task] += 1

        # duración (ms o s)
        dur = r.get("duration_ms")
        if dur is None and "duration_s" in r:
            try:
                dur = float(r["duration_s"]) * 1000.0
            except Exception:
                dur = None
        if isinstance(dur, (int, float)):
            durations.append(float(dur))

        # conteos de IO si vienen
        try:
            inputs += int(r.get("records_in") or 0)
            outputs += int(r.get("records_out") or 0)
        except Exception:
            pass

        # timestamps
        ts = r.get("timestamp") or r.get("time") or r.get("@timestamp")
        if isinstance(ts, str):
            dt = parse_ts(ts)
            if dt:
                if first_ts is None or dt < first_ts:
                    first_ts = dt
                if last_ts is None or dt > last_ts:
                    last_ts = dt

        # ejemplos
        if len(examples) < N_EXAMPLES:
            ex = {
                "source_file": str(src_path),
                "timestamp": ts,
                "task": task,
                "status": status,
                "level": level,
                "message": r.get("message") or r.get("msg"),
                "records_in": r.get("records_in"),
                "records_out": r.get("records_out"),
                "duration_ms": r.get("duration_ms") or r.get("duration_s"),
            }
            examples.append(ex)

    summary: Dict[str, Any] = {}
    summary["total_events"] = total
    summary["levels"] = dict(level_counts)
    summary["status"] = dict(status_counts)
    summary["tasks"] = dict(task_counts)
    summary["duration_ms"] = {
        "count": len(durations),
        "min": min(durations) if durations else None,
        "avg": (sum(durations)/len(durations)) if durations else None,
        "max": max(durations) if durations else None,
        "sum": sum(durations) if durations else None,
    }
    summary["records"] = {"in": inputs, "out": outputs}
    summary["window"] = {
        "start": first_ts.isoformat() if first_ts else None,
        "end": last_ts.isoformat() if last_ts else None,
    }
    summary["examples"] = examples
    return summary

# --------- Salidas ---------
def write_json(summary: Dict[str, Any], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

def write_csv(summary: Dict[str, Any], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # se genera CSV de resumen plano
    flat = [
        ("total_events", summary.get("total_events")),
        ("levels", json.dumps(summary.get("levels", {}), ensure_ascii=False)),
        ("status", json.dumps(summary.get("status", {}), ensure_ascii=False)),
        ("tasks", json.dumps(summary.get("tasks", {}), ensure_ascii=False)),
        ("duration_ms.min", summary.get("duration_ms", {}).get("min")),
        ("duration_ms.avg", summary.get("duration_ms", {}).get("avg")),
        ("duration_ms.max", summary.get("duration_ms", {}).get("max")),
        ("duration_ms.sum", summary.get("duration_ms", {}).get("sum")),
        ("records.in", summary.get("records", {}).get("in")),
        ("records.out", summary.get("records", {}).get("out")),
        ("window.start", summary.get("window", {}).get("start")),
        ("window.end", summary.get("window", {}).get("end")),
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerows(flat)

def write_md(summary: Dict[str, Any], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = []
    md.append("# Reporte de ejecución – MetaHunter\n")
    md.append("Este reporte resume los logs en formato **JSON Lines (.jsonl)**.\n")

    md.append("## Resumen\n")
    md.append(f"- **Eventos totales:** {summary.get('total_events', 0)}\n")
    dm = summary.get("duration_ms", {})
    md.append(f"- **Duración (ms):** min={dm.get('min')}, avg={dm.get('avg')}, max={dm.get('max')}, sum={dm.get('sum')}\n")
    rec = summary.get("records", {})
    md.append(f"- **Registros:** in={rec.get('in')}, out={rec.get('out')}\n")
    win = summary.get("window", {})
    md.append(f"- **Ventana temporal:** {win.get('start')} → {win.get('end')}\n")

    def dict_table(title: str, d: Dict[str, Any]):
        if not d:
            md.append(f"\n### {title}\n(No hay datos)\n")
            return
        md.append(f"\n### {title}\n")
        md.append("| clave | conteo |\n|---|---:|\n")
        for k, v in sorted(d.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            md.append(f"| {k} | {v} |\n")

    dict_table("Niveles (level)", summary.get("levels", {}))
    dict_table("Estatus (status)", summary.get("status", {}))
    dict_table("Tareas (task)", summary.get("tasks", {}))

    ex = summary.get("examples", [])
    if ex:
        md.append("\n### Ejemplos de eventos\n")
        md.append("| archivo | timestamp | task | status | level | msg | in | out | dur |\n|---|---|---|---|---|---|---:|---:|---:|\n")
        for e in ex:
            md.append(f"| {Path(e.get('source_file','')).name} | {e.get('timestamp')} | {e.get('task')} | "
                      f"{e.get('status')} | {e.get('level')} | {str(e.get('message')).replace('|','/')} | "
                      f"{e.get('records_in') or ''} | {e.get('records_out') or ''} | {e.get('duration_ms') or ''} |\n")

    with out_path.open("w", encoding="utf-8") as f:
        f.write("".join(md))

# --------- CLI ---------
def main():
    ap = argparse.ArgumentParser(
        description="Genera reportes (JSON/CSV/MD) a partir de logs .jsonl"
    )
    ap.add_argument(
        "--logs",
        nargs="+",
        default=["examples"],
        help="Rutas a archivos o carpetas con .jsonl (por defecto: 'examples')",
    )
    ap.add_argument(
        "--outdir",
        default="docs/reports",
        help="Directorio de salida para los reportes (default: docs/reports)",
    )
    ap.add_argument("--json", action="store_true", help="Escribir summary.json")
    ap.add_argument("--csv", action="store_true", help="Escribir summary.csv")
    ap.add_argument("--md", action="store_true", help="Escribir summary.md")
    ap.add_argument(
        "--all",
        action="store_true",
        help="Escribir todos los formatos (JSON, CSV, MD)",
    )
    args = ap.parse_args()

    paths = [Path(p) for p in args.logs]
    records = list(iter_logs(paths))
    if not records:
        sys.stderr.write("[ERROR] No se encontraron eventos en .jsonl\n")
        sys.exit(2)

    summary = aggregate(records)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.all or args.json:
        write_json(summary, outdir / "summary.json")
    if args.all or args.csv:
        write_csv(summary, outdir / "summary.csv")
    if args.all or args.md:
        write_md(summary, outdir / "summary.md")

    # salida por consola mínima para CI
    print(json.dumps({"ok": True, "events": summary["total_events"], "outdir": str(outdir)}, ensure_ascii=False))

if __name__ == "__main__":
    main()

