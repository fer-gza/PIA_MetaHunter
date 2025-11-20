import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from cleaner import clean_file               # IMPORT DIRECTO
from ai_client import generate_ai_summary     # IMPORT DIRECTO


def log_event(log_path: Path, run_id: str, module: str, level: str, event: str, details: dict) -> None:
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "run_id": run_id,
        "module": module,
        "level": level,
        "event": event,
        "details": details,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_args():
    p = argparse.ArgumentParser(
        prog="metahunter",
        description="Pipeline de escaneo, limpieza de metadatos y resumen con IA."
    )
    p.add_argument("--input-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--log-path", required=True, type=Path)
    p.add_argument("--use-ai", action="store_true")
    return p.parse_args()


def run_pipeline(input_dir: Path, output_dir: Path, log_path: Path, use_ai: bool) -> int:
    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    if not input_dir.exists():
        raise FileNotFoundError(f"El directorio de entrada no existe: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    log_event(log_path, run_id, "cli", "INFO", "run_start",
              {"input": str(input_dir), "output": str(output_dir), "use_ai": use_ai})

    supported = {".jpg", ".jpeg", ".png", ".pdf", ".docx", ".txt", ".md"}
    files = [p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in supported]

    log_event(log_path, run_id, "cli", "INFO", "scan_files", {"total": len(files)})

    processed = 0
    files_info = []

    for f in files:
        try:
            out_path = output_dir / f.name
            out_path.write_bytes(f.read_bytes())

            clean_file(str(out_path))  # <<< LIMPIEZA

            info = {
                "input": str(f),
                "output": str(out_path),
                "extension": f.suffix.lower(),
            }
            files_info.append(info)

            log_event(log_path, run_id, "cleaner", "INFO", "file_cleaned", info)
            processed += 1

        except Exception as e:
            log_event(log_path, run_id, "cleaner", "ERROR", "file_error",
                      {"input": str(f), "error": str(e)})

    if use_ai and files_info:
        prompt_path = Path("prompts") / "prompt_v1.json"

        summary = generate_ai_summary(run_id, files_info, prompt_path)

        ai_output_path = Path("examples") / f"ai_summary_{run_id}.json"
        ai_output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        log_event(log_path, run_id, "ai_client", "INFO", "ai_summary_generated",
                  {"output": str(ai_output_path)})

    log_event(log_path, run_id, "cli", "INFO", "run_finished",
              {"total": len(files), "procesados": processed})

    return 0


def main():
    args = parse_args()
    try:
        exit_code = run_pipeline(args.input_dir, args.output_dir, args.log_path, args.use_ai)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
