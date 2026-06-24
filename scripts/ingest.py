"""CLI for ingesting Futurekind Research PDFs into Supabase."""

import argparse
import logging
import sys

from app.ingestion.pipeline import run_ingestion


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Ingest Futurekind Research PDFs")
    parser.add_argument("--path", default=None, help="Override docs path relative to project root")
    parser.add_argument("--force", action="store_true", help="Re-ingest existing documents")
    args = parser.parse_args()

    try:
        results = run_ingestion(docs_path=args.path, force=args.force)
        print(f"Processed: {results['processed']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
        if results["errors"]:
            sys.exit(1)
    except Exception as exc:
        logging.error("Ingestion failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
