def analyze_experiments(experiments: list[dict[str, str | float]]) -> dict[str, object]:
    """Calculate the best experiment and average accuracy."""
    if not experiments:
        raise ValueError("no valid experiment experiments were loaded")

    best = max(experiments, key=lambda record: float(record["accuracy"]))
    average_accuracy = sum(
        float(record["accuracy"]) for record in experiments
    ) / len(experiments)

    return {
        "valid_count": len(experiments),
        "best_experiment": str(best["experiment_name"]),
        "best_accuracy": float(best["accuracy"]),
        "average_accuracy": average_accuracy,
    }
