from pathlib import Path


def format_report(result: dict[str, object], errors: list[str]) -> str:
    """Format analysis results as a human-readable report."""
    report = "\n".join([
        "Experiment Log result",
        "-" * 22,
        f"Valid experiments : {result['valid_count']}",
        f"Best experiment   : {result['best_experiment']}",
        f"Best accuracy     : {float(result['best_accuracy']):.2%}",
        f"Average accuracy  : {float(result['average_accuracy']):.2%}",
        f"Invalid rows      : {len(errors)}",
        "",
        "See outputs/analysis_report.txt for details.",
    ])

    return report


def write_report(text: str, output_path: Path) -> None:
    """Write a report to disk using UTF-8 encoding."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
