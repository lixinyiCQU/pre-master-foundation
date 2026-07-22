"""Command-line entry point for the experiment log analyzer."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .analyzer import analyze_experiments
from .data_loader import load_experiments
from .report import format_report, write_report

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Analyze machine-learning experiment logs."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="INFO",
    )
    return parser


def configure_logging(level_name: str) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level_name),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    """Run the application and return a process exit code."""
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level)

    output_path = args.output_dir / "analysis_report.txt"

    try:
        experiments, errors = load_experiments(args.input)
        result = analyze_experiments(experiments)
        report_text = format_report(result, errors)
        write_report(report_text, output_path)
    except (FileNotFoundError, ValueError, OSError) as exc:
        logger.error("Analysis failed: %s", exc)
        return 1

    print(report_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
