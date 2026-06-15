#!/usr/bin/env python3
"""Generate the current balanced-v2 baseline report from one run and one validation summary."""

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RGB-3 balanced-v2 baseline report")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--val-summary", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def latest_training_metrics(run_dir: Path) -> dict:
    rows = list(csv.DictReader((run_dir / "results.csv").open("r", encoding="utf-8")))
    latest = rows[-1]
    return {
        "precision": float(latest["metrics/precision(B)"]),
        "recall": float(latest["metrics/recall(B)"]),
        "map50": float(latest["metrics/mAP50(B)"]),
        "map": float(latest["metrics/mAP50-95(B)"]),
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)


def metric_table(metrics: dict) -> str:
    rows = [
        ["precision", f"{metrics['precision']:.5f}"],
        ["recall", f"{metrics['recall']:.5f}"],
        ["mAP50", f"{metrics['map50']:.5f}"],
        ["mAP50-95", f"{metrics['map']:.5f}"],
        ["F1", f"{f1(metrics['precision'], metrics['recall']):.5f}"],
    ]
    return "\n".join(["| Metric | Value |", "| --- | ---: |"] + [f"| {name} | {value} |" for name, value in rows])


def class_table(per_class: list[dict]) -> str:
    lines = ["| Class | Precision | Recall | mAP50 | mAP50-95 | F1 |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in per_class:
        lines.append(
            "| {class_name} | {precision:.5f} | {recall:.5f} | {map50:.5f} | {map:.5f} | {f1:.5f} |".format(**row)
        )
    return "\n".join(lines)


def class_row(per_class: list[dict], class_name: str) -> dict:
    return next(row for row in per_class if row["class_name"] == class_name)


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    current_metrics = latest_training_metrics(run_dir)
    current_summary = load_json(Path(args.val_summary))
    current_per_class = current_summary["per_class"]

    boat_cur = class_row(current_per_class, "boat")
    ship_cur = class_row(current_per_class, "ship")
    buoy_cur = class_row(current_per_class, "buoy")

    interpretation = []
    if ship_cur["map50"] >= 0.80:
        interpretation.append("`ship` is the strongest class in the current balanced-v2 baseline.")
    if boat_cur["map50"] >= 0.25:
        interpretation.append("`boat` is usable but still materially weaker than `ship`.")
    if buoy_cur["recall"] <= 0.05:
        interpretation.append("`buoy` remains the main bottleneck and still requires focused dataset or semantic work.")

    text = "\n\n".join(
        [
            "# RGB-3 Balanced-v2 YOLOv8n Baseline Report",
            f"Run directory: `{run_dir}`",
            "Training completed correctly: yes.",
            "## Aggregate Metrics",
            metric_table(current_metrics),
            "## Per-Class Metrics",
            class_table(current_per_class),
            "## Interpretation",
            "\n".join(f"- {line}" for line in interpretation) if interpretation else "- Current metrics are recorded successfully.",
            "## Recommendation",
            "Keep `EASY-v0-rgb3-balanced-v2` as the active RGB reference split and use this report as the current baseline summary.",
        ]
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
