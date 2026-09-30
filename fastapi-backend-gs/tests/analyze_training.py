#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Example:
# Training progress: 25%|...| 50/200 [..., Loss=0.1471799, Depth Loss=0.0000000]
PATTERN = re.compile(
    r"Training progress:\s+(\d+)%.*?\|\s*(\d+)/(\d+).*?"
    r"Loss=([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)"
)


def parse_training_log(log_path: Path) -> pd.DataFrame:
    """Extract the latest printed loss for each training iteration."""

    losses = {}
    target_iteration = None

    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = PATTERN.search(line)

            if not match:
                continue

            iteration = int(match.group(2))
            target_iteration = int(match.group(3))
            loss = float(match.group(4))

            # The log can print the same iteration more than once.
            # Keep the latest loss for that iteration.
            losses[iteration] = loss

    if not losses:
        raise ValueError("No training loss values were found in the log.")

    df = pd.DataFrame(
        sorted(losses.items()),
        columns=["iteration", "loss"],
    )

    df["loss_change"] = df["loss"].diff()

    initial_loss = df["loss"].iloc[0]
    df["loss_reduction_percent"] = (
        (initial_loss - df["loss"]) / initial_loss * 100
        if initial_loss != 0
        else 0
    )

    df.attrs["target_iteration"] = target_iteration

    return df


def create_loss_curve(df: pd.DataFrame, output_path: Path):
    """Create a high-resolution loss curve for the report."""

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        df["iteration"],
        df["loss"],
        marker="o",
        markersize=4,
        linewidth=2,
    )

    ax.set_title("Training Iteration vs. Loss", fontsize=16)
    ax.set_xlabel("Training Iteration", fontsize=12)
    ax.set_ylabel("Loss", fontsize=12)

    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_loss_table(df: pd.DataFrame, output_path: Path):
    """Create a PNG table suitable for a project report."""

    table_df = df[df["iteration"] % 200 == 0][["iteration", "loss"]].copy()
    table_df["loss"] = table_df["loss"].map(lambda x: f"{x:.7f}")

    fig_height = max(3.5, 0.45 * len(table_df) + 1.5)

    fig, ax = plt.subplots(figsize=(8, fig_height))
    ax.axis("off")

    table = ax.table(
        cellText=table_df.values,
        colLabels=["Training Iteration", "Loss"],
        cellLoc="center",
        colLoc="center",
        loc="center",
        colWidths=[0.45, 0.45],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.5)

    ax.set_title(
        "Training Iteration vs. Loss",
        fontsize=16,
        pad=20,
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_summary(df: pd.DataFrame, output_path: Path):
    """Create a numerical summary for the report."""

    first = df.iloc[0]
    last = df.iloc[-1]
    minimum = df.loc[df["loss"].idxmin()]

    initial_loss = float(first["loss"])
    final_loss = float(last["loss"])
    reduction = initial_loss - final_loss

    reduction_percent = (
        reduction / initial_loss * 100
        if initial_loss != 0
        else 0
    )

    target = df.attrs.get("target_iteration")

    lines = [
        "Gaussian Splatting Training Analysis",
        "====================================",
        "",
        f"Target iterations: {target}",
        f"First recorded iteration: {int(first['iteration'])}",
        f"Last recorded iteration: {int(last['iteration'])}",
        "",
        f"Initial recorded loss: {initial_loss:.7f}",
        f"Final recorded loss: {final_loss:.7f}",
        f"Absolute loss reduction: {reduction:.7f}",
        f"Loss reduction: {reduction_percent:.2f}%",
        "",
        f"Minimum recorded loss: {minimum['loss']:.7f}",
        f"Minimum-loss iteration: {int(minimum['iteration'])}",
        "",
        "Interpretation:",
        (
            "The loss curve represents the change in training loss "
            "as the number of Gaussian Splatting training iterations increases."
        ),
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Gaussian Splatting training logs."
    )

    parser.add_argument(
        "log_file",
        type=Path,
        help="Path to the training log file",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("training_analysis"),
        help="Directory where analysis files will be saved",
    )

    args = parser.parse_args()

    if not args.log_file.exists():
        raise FileNotFoundError(
            f"Log file not found: {args.log_file}"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = parse_training_log(args.log_file)

    csv_path = args.output_dir / "training_loss.csv"
    curve_path = args.output_dir / "training_loss_curve.png"
    table_path = args.output_dir / "training_loss_table.png"
    summary_path = args.output_dir / "training_analysis_summary.txt"

    df.to_csv(csv_path, index=False)

    create_loss_curve(df, curve_path)
    create_loss_table(df, table_path)
    create_summary(df, summary_path)

    print("Training analysis completed.")
    print(f"CSV:        {csv_path}")
    print(f"Loss curve: {curve_path}")
    print(f"Loss table: {table_path}")
    print(f"Summary:    {summary_path}")
    print()
    print(f"Initial loss: {df.iloc[0]['loss']:.7f}")
    print(f"Final loss:   {df.iloc[-1]['loss']:.7f}")


if __name__ == "__main__":
    main()
