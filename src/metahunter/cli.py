from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from . import cleaner
from . import analyzer
from . import ai_client  # Asegúrate de que exista este módulo
from .integrity import build_integrity_report


# ---------------------------------------------------------------------------
# Utilidad para logging JSONL
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def log_event(
    log_path: Path,
    run_id: str,
    module: str,
    level: str,
    event: str,
    details: Dict | None = None,
) -> None:
    record = {
        "timestamp": _now_iso(),
        "run_id": run_id,
        "module": module,
        "level": level,
        "event": event,
        "details": details or {},
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="metahunter",
        description="MetaHunter - Escáner, limpiador y analizador inteligente de metadatos.",
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Carpeta de entrada con archivos RAW a procesar.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Carpeta donde se guardarán los archivos limpios.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        required=True,
        help="Ruta al archivo JSONL de logs (por ejemplo: examples/logs.jsonl).",
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Si se activa, ejecuta la integración con IA (ai_client.py).",
    )
    parser.add_argument(
        "--stats-path",
        type=Path,
        help="Ruta del JSON con estadísticas (por defecto: examples/stats_<run_id>.json).",
    )
    parser.add_argument(
        "--ai-summary-path",
        type=Path,
        help="Ruta del JSON con el resumen de IA (por defecto: examples/ai_summary_<run_id>.json).",
    )
    parser.add_argument(
        "--ai-report-path",
        type=Path,
        help="Ruta del reporte Markdown generado por IA (por defecto: reports/ai_report_<run_id>.md).",
    )
    parser.add_argument(
        "--integrity-report",
        dest="integrity_report_path",
        type=Path,
        help="Ruta de un JSON donde se guardará el reporte de integridad (Merkle root).",
    )

    return parser.parse_args()


def _collect_input_files(input_dir: Path) -> List[Path]:
    """
    Devuelve lista de archivos dentro de input_dir (no recursivo).
    Si quieres recursivo, cambia a rglob('*').
    """
    return [p for p in input_dir.iterdir() if p.is_file()]


def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    log_path: Path,
    use_ai: bool,
    stats_path: Path | None = None,
    ai_summary_path: Path | None = None,
    ai_report_path: Path | None = None,
    integrity_report_path: Path | None = None,
) -> None:
    # Generar run_id tipo 20251120T225112Z
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Defaults de rutas según patrón del README
    if stats_path is None:
        stats_path = Path("examples") / f"stats_{run_id}.json"
    if ai_summary_path is None:
        ai_summary_path = Path("examples") / f"ai_summary_{run_id}.json"
    if ai_report_path is None:
        ai_report_path = Path("reports") / f"ai_report_{run_id}.md"

    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()
    log_path = log_path.resolve()
    stats_path = stats_path.resolve()
    ai_summary_path = ai_summary_path.resolve()
    ai_report_path = ai_report_path.resolve()
    if integrity_report_path is not None:
        integrity_report_path = integrity_report_path.resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    log_event(
        log_path,
        run_id,
        "cli",
        "INFO",
        "run_started",
        {
            "input_dir": str(input_dir),
            "output_dir": str(output_dir),
            "use_ai": use_ai,
        },
    )

    files = _collect_input_files(input_dir)
    if not files:
        log_event(
            log_path,
            run_id,
            "cli",
            "WARNING",
            "no_input_files",
            {"input_dir": str(input_dir)},
        )
        print(f"[MetaHunter] No se encontraron archivos en {input_dir}")
        return

    # -----------------------------------------------------------------------
    # 1) Limpieza de metadatos + cálculo de hashes limpios
    # -----------------------------------------------------------------------
    clean_files: List[Path] = []
    processed_hashes: Dict[str, str] = {}

    for f in files:
        out_path = output_dir / f.name

        try:
            # Se asume que cleaner.clean_file existe y limpia metadatos
            cleaner.clean_file(f, out_path)

            # Después de limpiar, dejamos que analyzer recalcule el hash SHA-256
            clean_files.append(out_path)

            log_event(
                log_path,
                run_id,
                "cleaner",
                "INFO",
                "file_cleaned",
                {"input": str(f), "output": str(out_path)},
            )
            print(f"[cleaner] OK  {f} -> {out_path}")
        except Exception as e:  # noqa: BLE001
            log_event(
                log_path,
                run_id,
                "cleaner",
                "ERROR",
                "file_clean_error",
                {"input": str(f), "error": str(e)},
            )
            print(f"[cleaner] ERR {f}: {e}")

    # -----------------------------------------------------------------------
    # 2) Análisis técnico + avanzado (riesgo, forense, IA-heurstica)
    # -----------------------------------------------------------------------
    stats = analyzer.analyze_files(clean_files)
    analyzer.save_stats(stats, stats_path)

    log_event(
        log_path,
        run_id,
        "analyzer",
        "INFO",
        "stats_saved",
        {"output": str(stats_path), "files": len(stats)},
    )
    print(f"[analyzer] Stats guardadas en {stats_path}")

    # Para el reporte de integridad, sacamos los hashes limpios del dict stats
    for file_path, info in stats.items():
        sha256 = info.get("sha256")
        if sha256:
            processed_hashes[file_path] = sha256

    # -----------------------------------------------------------------------
    # 3) IA (opcional) - resumen + reporte Markdown
    # -----------------------------------------------------------------------
    if use_ai:
        try:
            # Asegúrate de que ai_client tenga esta función o ajusta el nombre
            ai_client.run_ai_pipeline(
                stats_path=stats_path,
                summary_path=ai_summary_path,
                report_path=ai_report_path,
                run_id=run_id,
                log_path=log_path,
            )

            log_event(
                log_path,
                run_id,
                "ai_client",
                "INFO",
                "ai_pipeline_finished",
                {
                    "stats_path": str(stats_path),
                    "summary_path": str(ai_summary_path),
                    "report_path": str(ai_report_path),
                },
            )
            print(f"[ai_client] Resumen IA en {ai_summary_path}")
            print(f"[ai_client] Reporte IA en {ai_report_path}")
        except Exception as e:  # noqa: BLE001
            log_event(
                log_path,
                run_id,
                "ai_client",
                "ERROR",
                "ai_pipeline_error",
                {"error": str(e)},
            )
            print(f"[ai_client] ERROR ejecutando IA: {e}")

    # -----------------------------------------------------------------------
    # 4) Reporte de integridad (Merkle root)
    # -----------------------------------------------------------------------
    if integrity_report_path is not None and processed_hashes:
        try:
            integrity_report = build_integrity_report(processed_hashes)
            integrity_report_path.parent.mkdir(parents=True, exist_ok=True)
            integrity_report_path.write_text(
                json.dumps(integrity_report.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            log_event(
                log_path,
                run_id,
                "cli",
                "INFO",
                "integrity_report_generated",
                {
                    "output": str(integrity_report_path),
                    "files": len(processed_hashes),
                    "algorithm": integrity_report.algorithm,
                },
            )
            print(f"[integrity] Reporte de integridad: {integrity_report_path}")
        except Exception as e:  # noqa: BLE001
            log_event(
                log_path,
                run_id,
                "cli",
                "ERROR",
                "integrity_report_error",
                {"error": str(e)},
            )
            print(f"[integrity] ERROR generando reporte de integridad: {e}")

    # -----------------------------------------------------------------------
    # 5) Fin de ejecución
    # -----------------------------------------------------------------------
    log_event(
        log_path,
        run_id,
        "cli",
        "INFO",
        "run_finished",
        {"files_processed": len(clean_files)},
    )
    print(f"[MetaHunter] Ejecución completada. Archivos procesados: {len(clean_files)}")


def main() -> None:
    args = parse_args()
    run_pipeline(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        log_path=args.log_path,
        use_ai=args.use_ai,
        stats_path=args.stats_path,
        ai_summary_path=args.ai_summary_path,
        ai_report_path=args.ai_report_path,
        integrity_report_path=args.integrity_report_path,
    )


if __name__ == "__main__":
    main()
