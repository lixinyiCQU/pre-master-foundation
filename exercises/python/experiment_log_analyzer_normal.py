from pathlib import Path
import csv


def main():
    repo_root = Path(__file__).resolve().parent
    csv_path = repo_root / "data" / "experiments.csv"

    valid_records = []
    errors = []

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            experiment_name = row["experiment_name"].strip()

            try:
                train_loss = float(row["train_loss"].strip())
                val_loss = float(row["val_loss"].strip())
                accuracy = float(row["accuracy"].strip())
            except (ValueError, TypeError):
                errors.append(row)
                continue

            if (
                experiment_name
                and 0 <= train_loss <= 1
                and 0 <= val_loss <= 1
                and 0 <= accuracy <= 1
            ):
                valid_records.append({
                    "experiment_name": experiment_name,
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "accuracy": accuracy,
                })
            else:
                errors.append(row)

    max_accuracy_record = max(valid_records, key=lambda record: record["accuracy"])
    average_accuracy = sum(record['accuracy'] for record in valid_records) / len(valid_records)
    print(max_accuracy_record)
    print('-----')
    print(average_accuracy)

if __name__ == "__main__":
    main()