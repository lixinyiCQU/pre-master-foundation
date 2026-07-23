from __future__ import annotations
from pathlib import Path
import logging
import csv

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "experiment_name",
    "train_loss",
    "val_loss",
    "accuracy",
}

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
    """定义一个名为 parse_experiment_row 的函数。

    它接收三个参数：
    1. row：
    一个字典，键是字符串，值是字符串或 None。
    2. row_number：
    一个整数。
    3. seen_names：
    一个只包含字符串的集合。
    函数返回：
    一个字典，键是字符串，值是字符串或浮点数。
    """
    raw_name = row.get("experiment_name")
    name = raw_name.strip() if raw_name else ""

    if not name:
        raise ValueError("experiment_name is empty") # 实验名称为空
    if name in seen_names:
        raise ValueError(f"duplicate experiment_name {name!r}") # 重复的试验名称

    record: dict[str, str | float] = {
        "experiment_name": name,
        "train_loss": parse_float(row.get("train_loss"), "train_loss", row_number),
        "val_loss": parse_float(row.get("val_loss"), "val_loss", row_number),
        "accuracy": parse_float(row.get("accuracy"), "accuracy", row_number),
    }

    seen_names.add(name)
    return record

def load_experiments(path: Path) -> tuple[list[dict[str, str | float]], list[str]]:
    """Load valid experiment records and collect row-level errors."""
    valid_records: list[dict[str, str | float]] = []
    errors: list[str] = [] # 错误输出，是一个元素为字符串的列表
    seen_names: set[str] = set() # 见过的表头，此处使用集合是因为不需要处理元素的序号

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        actual_fields = set(reader.fieldnames or []) # 此处些reader.fieldsnames or []的原因是防止空表头，导致集合中无内容
        missing_fields = REQUIRED_FIELDS - actual_fields
        extra_fields = actual_fields - REQUIRED_FIELDS

        if missing_fields:
            raise ValueError(
                f"missing required columns: {sorted(missing_fields)}" # 检测是否缺表头
            )
            
        if extra_fields:
            raise ValueError(
                f'extra required columns: {sorted(extra_fields)}' # 检测是否多余表头
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