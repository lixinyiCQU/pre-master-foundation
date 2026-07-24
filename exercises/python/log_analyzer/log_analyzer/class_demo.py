class ExperimentAnalyzer:
    """Analyze a fixed collection of experiment records. """

    def __init__(self, experiments: list[dict[str, str | float]]) -> None:
        if not experiments:
            raise ValueError('experiments must not be empty. ')
        self.experiments = experiments

    def best(self) -> dict[str, str | float]:
        best_accuracy = max(self.experiments, key=lambda record: float(record["accuracy"]))
        return {
            "valid_count": len(self.experiments),
            "best_experiment": str(best_accuracy["experiment_name"]),
            "best_accuracy": float(best_accuracy["accuracy"]),
        }

    def average_accuracy(self) -> float:
        total = sum(float(record["accuracy"]) for record in self.experiments)
        average_accuracy = total / len(self.experiments)
        return average_accuracy

    def summary(self) -> dict[str, object]:
        return {
            "valid_count": self.best()["valid_count"],
            "best_experiment": self.best()["best_experiment"],
            "best_accuracy": self.best()["best_accuracy"],
            "average_accuracy": self.average_accuracy(),
        }