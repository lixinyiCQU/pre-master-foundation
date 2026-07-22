from __future__ import annotations

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "experiment_name",
    "train_loss",
    "val_loss",
    "accuracy",
}


def configure_logging(log_path: Path) -> None:
    """Configure console and file logging for this script."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
        ],
    )


def parse_float(
    raw_value: str | None,
    field_name: str,
    row_number: int,
) -> float:
    """Convert and validate one numeric CSV field."""
    if raw_value is None or not raw_value.strip():
        raise ValueError(f"{field_name} is empty")

    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be numeric, got {raw_value!r}"
        ) from exc

    if field_name in {"train_loss", "val_loss"} and value < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value}")

    if field_name == "accuracy" and not 0 <= value <= 1:
        raise ValueError(f"accuracy must be within [0, 1], got {value}")

    return value


def parse_experiment_row(
    row: dict[str, str | None],
    row_number: int,
    seen_names: set[str],
) -> dict[str, str | float]:
'''
定义一个名为 parse_experiment_row 的函数。
它接收三个参数：
1. row：
   一个字典，键是字符串，值是字符串或 None。
2. row_number：
   一个整数。
3. seen_names：
   一个只包含字符串的集合。
函数返回：
一个字典，键是字符串，值是字符串或浮点数。
'''
    """Validate one CSV row and return a typed experiment record."""
    raw_name = row.get("experiment_name")
    name = raw_name.strip() if raw_name else ""

    if not name:
        raise ValueError("experiment_name is empty")
    if name in seen_names:
        raise ValueError(f"duplicate experiment_name {name!r}")

    record: dict[str, str | float] = {
        "experiment_name": name,
        "train_loss": parse_float(row.get("train_loss"), "train_loss", row_number),
        "val_loss": parse_float(row.get("val_loss"), "val_loss", row_number),
        "accuracy": parse_float(row.get("accuracy"), "accuracy", row_number),
    }

    seen_names.add(name)
    return record


def load_experiments(
    csv_path: Path,
) -> tuple[list[dict[str, str | float]], list[str]]:
    """Load valid records and collect recoverable row-level errors."""
    valid_records: list[dict[str, str | float]] = []
    errors: list[str] = []
    seen_names: set[str] = set()
'''
定义函数 load_experiments。
输入：
    csv_path
    类型为 Path，表示 CSV 文件路径。
输出：
    一个包含两个元素的元组。
    第一个元素：
        有效实验记录列表。
        每条记录是一个字典。
        字典键是字符串，值是字符串或浮点数。
    第二个元素：
        错误信息列表。
        每条错误信息是字符串。

函数开始时创建：
    一个空的有效记录列表；
    一个空的错误信息列表；
    一个空的实验名称集合。
'''
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        actual_fields = set(reader.fieldnames or [])
        missing_fields = REQUIRED_FIELDS - actual_fields
        extra_fields = actual_fields - REQUIRED_FIELDS

        if missing_fields:
            raise ValueError(
                f"missing required columns: {sorted(missing_fields)}"
            )
            
        if extra_fields:
            raise ValueError(
                f'extra required columns: {sorted(extra_fields)}'
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                record = parse_experiment_row(row, row_number, seen_names)
            except (KeyError, ValueError) as exc:
                message = f"row {row_number}: {exc}"
                errors.append(message)
                logger.warning(message)
                continue

            valid_records.append(record)

    return valid_records, errors


def summarize_experiments(
    records: list[dict[str, str | float]],
) -> dict[str, str | float | int]:
    """Calculate the best experiment and average accuracy."""
    if not records:
        raise ValueError("no valid experiment records were loaded")

    best = max(records, key=lambda record: float(record["accuracy"]))
    average_accuracy = sum(
        float(record["accuracy"]) for record in records
    ) / len(records)

    return {
        "valid_count": len(records),
        "best_experiment": str(best["experiment_name"]),
        "best_accuracy": float(best["accuracy"]),
        "average_accuracy": average_accuracy,
    }


def print_report(
    summary: dict[str, str | float | int],
    errors: list[str],
) -> None:
    """Print a concise user-facing summary."""
    print("\nExperiment Log Summary")
    print("-" * 22)
    print(f"Valid experiments : {summary['valid_count']}")
    print(f"Best experiment   : {summary['best_experiment']}")
    print(f"Best accuracy     : {float(summary['best_accuracy']):.2%}")
    print(f"Average accuracy  : {float(summary['average_accuracy']):.2%}")
    print(f"Invalid rows      : {len(errors)}")
    print("\nSee outputs/analyzer.log for details.")


def main() -> int:
    """Run the complete experiment-log analysis workflow."""
    repo_root = Path(__file__).resolve().parents[2]
    csv_path = repo_root / "exercises" / "python" / "data" / "experiments.csv"
    log_path = repo_root / "exercises" / "python" / "outputs" / "analyzer.log"

    configure_logging(log_path)
    logger.info("starting analysis for %s", csv_path)

    try:
        records, errors = load_experiments(csv_path)
        summary = summarize_experiments(records)
    except (FileNotFoundError, PermissionError, csv.Error, ValueError) as exc:
        logger.error("analysis failed: %s", exc)
        return 1

    logger.info(
        "analysis completed: %d valid rows, %d invalid rows",
        len(records),
        len(errors),
    )
    print_report(summary, errors)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
