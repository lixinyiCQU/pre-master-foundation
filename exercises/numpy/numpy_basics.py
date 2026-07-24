from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

def demonstrate_array_basics() -> None:
    matrix = np.arange(12).reshape(3, 4)
    print("matrix:\n", matrix)
    print("ndim:", matrix.ndim)
    print("shape:", matrix.shape)
    print("size:", matrix.size)
    print("dtype:", matrix.dtype)
    print("second row:", matrix[1, :])
    print("third column:", matrix[:, 2])
    print("submatrix:\n", matrix[:2, 1:])
    print("reshape (2, 6):\n", matrix.reshape(2, 6))
    print("transpose:\n", matrix.T)

def demonstrate_broadcasting() -> None:
    matrix = np.arange(12).reshape(3, 4)
    column_offset = np.array([10, 20, 30, 40])
    row_scale = np.array([[1], [10], [100]])

    print("matrix + column_offset:\n", matrix + column_offset)
    print("matrix * row_scale:\n", matrix * row_scale)

    try:
        invalid = matrix + np.array([1, 2, 3])
        print(invalid)
    except ValueError as exc:
        print("expected broadcasting error:", exc)

def demonstrate_matrix_multiplication() -> None:
    a = np.array([[1, 2, 3], [4, 5, 6]])
    b = np.array([[7, 8], [9, 10], [11, 12]])
    product = a @ b
    expected = np.array([[58, 64], [139, 154]])
    print("A @ B:\n", product)
    assert product.shape == (2, 2)
    assert np.array_equal(product, expected)

def demonstrate_statistics() -> None:
    runs = np.array([
        [0.81, 0.84, 0.85, 0.86],
        [0.79, 0.83, 0.86, 0.87],
        [0.80, 0.82, 0.84, 0.88],
    ])
    print("overall mean:", runs.mean())
    print("mean by epoch:", runs.mean(axis=0))
    print("mean by run:", runs.mean(axis=1))
    print("variance by epoch:", runs.var(axis=0))
    print("standard deviation by epoch:", runs.std(axis=0))

def generate_simulated_history(
    seed: int = 20260723,
    num_epochs: int = 40,
) -> dict[str, np.ndarray]: # 返回一个字典，key为str，value是一个数组
    rng = np.random.default_rng(seed) # 随机种子
    epochs = np.arange(1, num_epochs + 1) # epochs是一个(40, )的一维数组

    # 模拟训练损失，先构造一个下降趋势的损失曲线exp(-x)，然后再加上随机噪声
    train_loss = 1.15 * np.exp(-epochs / 12) + 0.08
    train_loss += rng.normal(0, 0.012, size=epochs.shape)
    # train_loss是一个(40, )的数组，每一个元素代表每个epoch的训练损失

    # 模拟验证损失，模拟的是“训练早期下降很快，后期可能略有回升”的曲线。过拟合现象，背答案，泛化能力下降
    val_loss = 1.20 * np.exp(-epochs / 10) + 0.12
    # epoch - 20 = [-19, -18, ..., 20]
    # np.maximun(epoch - 20) = [0, 0, ..., 20]，前20个元素为0，从第21个元素开始有值，并且越来越大
    val_loss += 0.006 * np.maximum(epochs - 20, 0) ** 1.25
    val_loss += rng.normal(0, 0.016, size=epochs.shape)
    # 同样，val_loss也是一个(40, )的数组，每一个元素代表每个epoch的验证损失

    # 训练准确率是一个逐渐上升的曲线，最大不超过1，并且有随机扰动
    train_accuracy = 0.48 + 0.50 * (1 - np.exp(-epochs / 10))
    train_accuracy += rng.normal(0, 0.004, size=epochs.shape)

    # 模拟验证准确率，同样是逐渐上升的曲线，后期略有下降，同样模拟过拟合现象，再加入随机噪声
    val_accuracy = 0.46 + 0.44 * (1 - np.exp(-epochs / 9))
    val_accuracy -= 0.0018 * np.maximum(epochs - 24, 0)
    val_accuracy += rng.normal(0, 0.006, size=epochs.shape)

    return {
        "epochs": epochs, # 训练epoch
        "train_loss": train_loss, # 训练损失
        "val_loss": val_loss, # 验证损失
        "train_accuracy": np.clip(train_accuracy, 0, 1), # 训练准确率，但是钳制在0-1
        "val_accuracy": np.clip(val_accuracy, 0, 1), # 验证准确率，但是钳制在0-1
    }# dict[str, ndarray(40, )]

def validate_history(history: dict[str, np.ndarray]) -> None:
    """
    会严格检查返回的历史数据字典是否满足：
    
    必须有 5 个关键字段
    所有字段的数组 shape 一致
    都是 1 维数组
    不能有 NaN 或 inf
    """
    required_keys = {
        "epochs",
        "train_loss",
        "val_loss",
        "train_accuracy",
        "val_accuracy",
    }
    missing = required_keys - history.keys()
    # 如果少了任何一个必需字段，就抛出 KeyError
    if missing:
        raise KeyError(f"Missing history keys: {sorted(missing)}")

    # shapes是一个集合，里面存放的是训练字典中每一个元素的形状的种类
    shapes = {history[key].shape for key in required_keys}
    # 如果集合中元素个数不为1，也就意味着训练字典中的元素存在不同形状的数组
    if len(shapes) != 1:
        raise ValueError("All history arrays must have the same shape.")

    # 检查具体的数组形状
    for key in required_keys:
        # 如果数组的维度不为1，则抛出ValueError
        if history[key].ndim != 1:
            raise ValueError(f"{key} must be one-dimensional.")
        # 检查数组不能出现NaN或inf，Not a number或者无穷大
        if not np.isfinite(history[key]).all():
            raise ValueError(f"{key} contains NaN or infinite values.")

def plot_loss_curves(history: dict[str, np.ndarray], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
    ax.plot(history["epochs"], history["train_loss"], label="Training loss")
    ax.plot(history["epochs"], history["val_loss"], label="Validation loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Simulated training and validation loss")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)

def plot_accuracy_curves(history: dict[str, np.ndarray], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
    ax.plot(history["epochs"], history["train_accuracy"], label="Training accuracy")
    ax.plot(history["epochs"], history["val_accuracy"], label="Validation accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.set_title("Simulated training and validation accuracy")
    ax.set_ylim(0.4, 1.0)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)

def plot_experiment_comparison(output_path: Path) -> None:
    names = ["Baseline", "Lower LR", "Regularized"]
    scores = np.array([0.862, 0.878, 0.887])

    fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
    bars = ax.bar(names, scores)
    ax.set_ylabel("Final validation accuracy")
    ax.set_title("Comparison of simulated experiments")
    ax.set_ylim(0.82, 0.91)
    ax.bar_label(bars, fmt="%.3f", padding=3)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)

def summarize_history(history: dict[str, np.ndarray]) -> dict[str, float | int]:
    best_index = int(np.argmin(history["val_loss"]))
    return {
        "best_val_loss_epoch": int(history["epochs"][best_index]),
        "best_val_loss": float(history["val_loss"][best_index]),
        "mean_train_loss": float(history["train_loss"].mean()),
        "variance_val_loss": float(history["val_loss"].var()),
        "final_val_accuracy": float(history["val_accuracy"][-1]),
    }

def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    demonstrate_array_basics()
    demonstrate_broadcasting()
    demonstrate_matrix_multiplication()
    demonstrate_statistics()

    history = generate_simulated_history()
    validate_history(history)

    plot_loss_curves(history, output_dir / "simulated_loss_curve.png")
    plot_accuracy_curves(history, output_dir / "simulated_accuracy_curve.png")
    plot_experiment_comparison(output_dir / "experiment_comparison.png")

    for key, value in summarize_history(history).items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
