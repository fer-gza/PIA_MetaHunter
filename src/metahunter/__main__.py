# src/metahunter/__main__.py
from __future__ import annotations
import argparse
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(prog="metahunter", description="MetaHunter - escanea y limpia metadatos")
    parser.add_argument("path", nargs="?", default=".", help="Archivo o directorio a escanear (por defecto: directorio actual)")
    parser.add_argument("--report", "-r", help="Ruta para guardar el reporte (md/html)")
    parser.add_argument("--dry-run", action="store_true", help="Solo reportar, no modificar archivos")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: ruta no encontrada: {target}", file=sys.stderr)
        sys.exit(2)

    # Import lazy: evita errores al instalar si faltan deps
    try:
        from metahunter.cleaner import Cleaner
    except Exception as e:
        print("No se pudo importar metahunter.cleaner. Asegúrate de instalar dependencias.", file=sys.stderr)
        raise

    cleaner = Cleaner(dry_run=args.dry_run)
    # método hipotético: scan_and_clean(target, report_path)
    report_path = Path(args.report) if args.report else None
    cleaner.scan_and_clean(target, report_path)
    print("Operación finalizada.")

if __name__ == "__main__":
    main()
