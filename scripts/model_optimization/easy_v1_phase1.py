#!/usr/bin/env python3
"""EASY-v1 RGB Phase 1 helpers.

This script uses only the Python standard library so it can run even in a
partially provisioned environment and emit clear blocker reports.
"""

from __future__ import print_function

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_config(path):
    with open(path, "r") as handle:
        return json.load(handle)


def abspath(path):
    return os.path.join(ROOT, path)


def repo_rel(path):
    return os.path.relpath(path, ROOT)


def ensure_parent(path):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)


def write_json(path, payload):
    ensure_parent(path)
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path, text):
    ensure_parent(path)
    with open(path, "w") as handle:
        handle.write(text)


def file_size_mb(path):
    if not os.path.exists(path):
        return None
    return os.path.getsize(path) / float(1024 * 1024)


def format_float(value, digits=5):
    if value is None:
        return "n/a"
    return ("%%.%df" % digits) % value


def get_runtime_python(config):
    preferred = config.get("runtime_requirements", {}).get("preferred_python")
    if preferred:
        full = abspath(preferred)
        if os.path.exists(full):
            return full
    return sys.executable


def run_external_python(python_bin, code):
    try:
        output = subprocess.check_output(
            [python_bin, "-c", code],
            cwd=ROOT,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return {"ok": True, "output": output.strip()}
    except subprocess.CalledProcessError as exc:  # pragma: no cover - env dependent
        return {"ok": False, "output": exc.output.strip() or str(exc)}
    except Exception as exc:  # pragma: no cover - env dependent
        return {"ok": False, "output": str(exc)}


def gather_runtime_status(config):
    req = config["runtime_requirements"]
    runtime_python = get_runtime_python(config)
    py_probe = run_external_python(
        runtime_python,
        "import sys; print('%d.%d.%d' % sys.version_info[:3])",
    )
    version_str = py_probe["output"] if py_probe["ok"] else "unknown"
    try:
        py_tuple = tuple(int(piece) for piece in version_str.split(".")[:2])
    except Exception:
        py_tuple = (0, 0)

    min_py = tuple(req["python_min"])
    py_ok = py_probe["ok"] and py_tuple >= min_py
    modules = {}
    for name in req["modules"]:
        probe = run_external_python(
            runtime_python,
            (
                "import importlib;"
                "m=importlib.import_module('%s');"
                "print(getattr(m,'__version__','unknown'))"
            )
            % name,
        )
        if probe["ok"]:
            modules[name] = {"available": True, "version": probe["output"] or "unknown"}
        else:
            modules[name] = {"available": False, "error": probe["output"]}

    cuda_probe = run_external_python(
        runtime_python,
        (
            "import torch;"
            "print(torch.cuda.is_available());"
            "print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'torch installed but CUDA not available')"
        ),
    )
    cuda_available = False
    cuda_info = "torch unavailable"
    if cuda_probe["ok"]:
        lines = [line.strip() for line in cuda_probe["output"].splitlines() if line.strip()]
        if lines:
            cuda_available = lines[0].lower() == "true"
        if len(lines) > 1:
            cuda_info = lines[1]

    pretrained = []
    for rel_path in req["required_pretrained_weights"]:
        full = abspath(rel_path)
        pretrained.append(
            {
                "path": rel_path,
                "exists": os.path.exists(full),
                "size_mb": file_size_mb(full),
            }
        )

    baseline_weights = config["baseline"]["weights"]
    baseline_exists = os.path.exists(abspath(baseline_weights))

    status = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "python": {
            "executable": repo_rel(runtime_python) if runtime_python.startswith(ROOT) else runtime_python,
            "version": version_str,
            "minimum_required": ".".join(str(v) for v in min_py),
            "ok": py_ok,
        },
        "modules": modules,
        "cuda": {
            "required": bool(req["require_cuda"]),
            "available": cuda_available,
            "details": cuda_info,
        },
        "baseline_weights": {
            "path": baseline_weights,
            "exists": baseline_exists,
            "size_mb": file_size_mb(abspath(baseline_weights)),
        },
        "pretrained_weights": pretrained,
        "blockers": [],
    }

    if not py_ok:
        status["blockers"].append(
            "Python %s is below required %s"
            % (version_str, status["python"]["minimum_required"])
        )
    for name, module_info in sorted(modules.items()):
        if not module_info.get("available"):
            status["blockers"].append("Missing Python module: %s" % name)
    if req["require_cuda"] and not cuda_available:
        status["blockers"].append("CUDA-capable runtime not available")
    if not baseline_exists:
        status["blockers"].append("Baseline weights missing")
    for item in pretrained:
        if not item["exists"]:
            status["blockers"].append("Required pretrained weights missing: %s" % item["path"])

    return status


def iter_files(path):
    if not os.path.isdir(path):
        return []
    return sorted(os.listdir(path))


def parse_label_line(path, line_number, raw_line):
    parts = raw_line.strip().split()
    if len(parts) != 5:
        return None, {
            "path": path,
            "line": line_number,
            "issue": "expected 5 fields, found %d" % len(parts),
            "raw": raw_line.rstrip(),
        }

    try:
        class_id = int(float(parts[0]))
        coords = [float(value) for value in parts[1:]]
    except ValueError:
        return None, {
            "path": path,
            "line": line_number,
            "issue": "non-numeric YOLO fields",
            "raw": raw_line.rstrip(),
        }

    errors = []
    if class_id < 0:
        errors.append("negative class id")
    for value in coords:
        if value < 0.0 or value > 1.0:
            errors.append("normalized coordinate out of range")
            break
    if coords[2] <= 0.0 or coords[3] <= 0.0:
        errors.append("non-positive width/height")

    if errors:
        return None, {
            "path": path,
            "line": line_number,
            "issue": "; ".join(sorted(set(errors))),
            "raw": raw_line.rstrip(),
        }

    return {"class_id": class_id}, None


def gather_dataset_status(config):
    dataset = config["dataset"]
    class_names = dataset["class_names"]
    valid_exts = tuple(dataset["image_extensions"])
    root = abspath(dataset["root"])
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "dataset_root": dataset["root"],
        "exists": os.path.isdir(root),
        "splits": {},
        "totals": {"images": 0, "labels": 0, "objects": 0},
        "checks": {},
        "issues": {
            "empty_labels": [],
            "broken_symlinks": [],
            "missing_images_for_labels": [],
            "missing_labels_for_images": [],
            "malformed_rows": [],
        },
    }

    if not report["exists"]:
        report["checks"]["dataset_root_exists"] = False
        report["checks"]["all_splits_exist"] = False
        return report

    all_split_dirs_exist = True
    for split in dataset["splits"]:
        image_dir = os.path.join(root, "images", split)
        label_dir = os.path.join(root, "labels", split)
        image_dir_exists = os.path.isdir(image_dir)
        label_dir_exists = os.path.isdir(label_dir)
        all_split_dirs_exist = all_split_dirs_exist and image_dir_exists and label_dir_exists

        image_basenames = set()
        image_entries = []
        for name in iter_files(image_dir):
            path = os.path.join(image_dir, name)
            if os.path.islink(path) and not os.path.exists(path):
                report["issues"]["broken_symlinks"].append(path)
            _, ext = os.path.splitext(name)
            if ext.lower() in valid_exts:
                image_entries.append(name)
                image_basenames.add(os.path.splitext(name)[0])

        label_entries = []
        label_basenames = set()
        class_counts = Counter()
        malformed = []
        empty_labels = []

        for name in iter_files(label_dir):
            path = os.path.join(label_dir, name)
            if os.path.islink(path) and not os.path.exists(path):
                report["issues"]["broken_symlinks"].append(path)
            if not name.endswith(".txt"):
                continue
            label_entries.append(name)
            label_basenames.add(os.path.splitext(name)[0])
            if os.path.getsize(path) == 0:
                empty_labels.append(path)
                report["issues"]["empty_labels"].append(path)
                continue

            with open(path, "r") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    if not raw_line.strip():
                        malformed.append(
                            {
                                "path": path,
                                "line": line_number,
                                "issue": "blank line in label file",
                                "raw": "",
                            }
                        )
                        continue
                    parsed, error = parse_label_line(path, line_number, raw_line)
                    if error:
                        malformed.append(error)
                        continue
                    class_id = parsed["class_id"]
                    if class_id < 0 or class_id >= len(class_names):
                        malformed.append(
                            {
                                "path": path,
                                "line": line_number,
                                "issue": "class id out of declared range",
                                "raw": raw_line.rstrip(),
                            }
                        )
                        continue
                    class_counts[class_names[class_id]] += 1

        missing_images = sorted(label_basenames - image_basenames)
        missing_labels = sorted(image_basenames - label_basenames)

        report["issues"]["missing_images_for_labels"].extend(
            [os.path.join(label_dir, name + ".txt") for name in missing_images]
        )
        report["issues"]["missing_labels_for_images"].extend(
            [os.path.join(image_dir, name) for name in missing_labels]
        )
        report["issues"]["malformed_rows"].extend(malformed)

        objects = sum(class_counts.values())
        split_summary = {
            "image_dir_exists": image_dir_exists,
            "label_dir_exists": label_dir_exists,
            "images": len(image_entries),
            "labels": len(label_entries),
            "objects": objects,
            "class_counts": {name: class_counts.get(name, 0) for name in class_names},
            "empty_labels": len(empty_labels),
            "missing_images_for_labels": len(missing_images),
            "missing_labels_for_images": len(missing_labels),
            "malformed_rows": len(malformed),
        }
        report["splits"][split] = split_summary
        report["totals"]["images"] += len(image_entries)
        report["totals"]["labels"] += len(label_entries)
        report["totals"]["objects"] += objects

    report["checks"]["dataset_root_exists"] = True
    report["checks"]["all_splits_exist"] = all_split_dirs_exist
    report["checks"]["all_images_have_labels"] = not report["issues"]["missing_labels_for_images"]
    report["checks"]["all_labels_have_images"] = not report["issues"]["missing_images_for_labels"]
    report["checks"]["no_broken_symlinks"] = not report["issues"]["broken_symlinks"]
    report["checks"]["no_empty_labels"] = not report["issues"]["empty_labels"]
    report["checks"]["no_malformed_rows"] = not report["issues"]["malformed_rows"]
    report["checks"]["pass"] = all(report["checks"].values())
    return report


def write_dataset_report(config, dataset_status):
    out_path = abspath(config["outputs"]["dataset_report"])
    lines = []
    checks = dataset_status["checks"]
    lines.append("# EASY-v1 Dataset Status")
    lines.append("")
    lines.append("Generated: `%s`" % dataset_status["generated_at"])
    lines.append("")
    lines.append("Dataset root: `%s`" % dataset_status["dataset_root"])
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Check | Status |")
    lines.append("| --- | --- |")
    for key in [
        "dataset_root_exists",
        "all_splits_exist",
        "all_images_have_labels",
        "all_labels_have_images",
        "no_broken_symlinks",
        "no_empty_labels",
        "no_malformed_rows",
        "pass",
    ]:
        lines.append("| %s | %s |" % (key, "PASS" if checks.get(key) else "FAIL"))
    lines.append("")
    lines.append("## Split Counts")
    lines.append("")
    lines.append("| Split | Images | Labels | Objects | Boat | Ship | Buoy | Empty labels | Missing images for labels | Missing labels for images | Malformed rows |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for split in config["dataset"]["splits"]:
        entry = dataset_status["splits"].get(split, {})
        class_counts = entry.get("class_counts", {})
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
            % (
                split,
                entry.get("images", "n/a"),
                entry.get("labels", "n/a"),
                entry.get("objects", "n/a"),
                class_counts.get("boat", "n/a"),
                class_counts.get("ship", "n/a"),
                class_counts.get("buoy", "n/a"),
                entry.get("empty_labels", "n/a"),
                entry.get("missing_images_for_labels", "n/a"),
                entry.get("missing_labels_for_images", "n/a"),
                entry.get("malformed_rows", "n/a"),
            )
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Image counting includes only `.jpg`, `.jpeg`, `.png`.")
    lines.append("- Cache artifacts such as `.npy` are ignored.")
    lines.append("- Full machine-readable audit: `%s`." % config["outputs"]["dataset_json"])
    lines.append("")
    issue_lengths = {
        "broken_symlinks": len(dataset_status["issues"]["broken_symlinks"]),
        "empty_labels": len(dataset_status["issues"]["empty_labels"]),
        "missing_images_for_labels": len(dataset_status["issues"]["missing_images_for_labels"]),
        "missing_labels_for_images": len(dataset_status["issues"]["missing_labels_for_images"]),
        "malformed_rows": len(dataset_status["issues"]["malformed_rows"]),
    }
    lines.append("## Issue Counts")
    lines.append("")
    lines.append("| Issue | Count |")
    lines.append("| --- | ---: |")
    for key in sorted(issue_lengths):
        lines.append("| %s | %d |" % (key, issue_lengths[key]))
    lines.append("")
    write_text(out_path, "\n".join(lines) + "\n")


def write_runtime_report(config, runtime_status):
    out_path = abspath(config["outputs"]["runtime_report"])
    lines = []
    lines.append("# EASY-v1 Runtime Status")
    lines.append("")
    lines.append("Generated: `%s`" % runtime_status["generated_at"])
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Requirement | Status | Detail |")
    lines.append("| --- | --- | --- |")
    py = runtime_status["python"]
    lines.append(
        "| Python >= %s | %s | `%s` via `%s` |"
        % (
            py["minimum_required"],
            "PASS" if py["ok"] else "FAIL",
            py["version"],
            py["executable"],
        )
    )
    for name in sorted(runtime_status["modules"]):
        item = runtime_status["modules"][name]
        detail = item.get("version") or item.get("error", "n/a")
        lines.append(
            "| Module `%s` | %s | %s |"
            % (name, "PASS" if item["available"] else "FAIL", detail)
        )
    lines.append(
        "| CUDA | %s | %s |"
        % (
            "PASS" if runtime_status["cuda"]["available"] else "FAIL",
            runtime_status["cuda"]["details"],
        )
    )
    base = runtime_status["baseline_weights"]
    lines.append(
        "| Baseline weights | %s | `%s` |"
        % ("PASS" if base["exists"] else "FAIL", base["path"])
    )
    for item in runtime_status["pretrained_weights"]:
        lines.append(
            "| Pretrained weights `%s` | %s | size `%s MB` |"
            % (
                item["path"],
                "PASS" if item["exists"] else "FAIL",
                format_float(item["size_mb"], 2) if item["size_mb"] is not None else "n/a",
            )
        )
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if runtime_status["blockers"]:
        for blocker in runtime_status["blockers"]:
            lines.append("- %s" % blocker)
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("Machine-readable status: `%s`." % config["outputs"]["runtime_json"])
    lines.append("")
    write_text(out_path, "\n".join(lines) + "\n")


def load_metrics(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as handle:
        return json.load(handle)


def write_error_analysis_scaffold(config, runtime_status):
    root = abspath(config["outputs"]["error_analysis_root"])
    buckets = [
        "true_positives",
        "false_positives",
        "false_negatives",
        "buoy_missed",
        "boat_buoy_confusion",
        "low_confidence",
        "difficult_samples",
    ]
    if not os.path.isdir(root):
        os.makedirs(root)

    blocker_note = (
        "Full visual error analysis requires a provisioned Ultralytics runtime and "
        "fresh prediction artifacts for both validation and test splits. Current "
        "status: %s"
        % ("; ".join(runtime_status["blockers"]) if runtime_status["blockers"] else "ready")
    )
    for bucket in buckets:
        bucket_dir = os.path.join(root, bucket)
        if not os.path.isdir(bucket_dir):
            os.makedirs(bucket_dir)
        manifest_path = os.path.join(bucket_dir, "index.csv")
        with open(manifest_path, "w") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "image_id",
                    "split",
                    "confidence",
                    "iou",
                    "gt_class",
                    "predicted_class",
                    "source_artifact_path",
                    "status",
                ]
            )
            writer.writerow(["", "", "", "", "", "", "", "blocked"])
        write_text(os.path.join(bucket_dir, "README.md"), "# %s\n\n%s\n" % (bucket, blocker_note))

    write_text(os.path.join(root, "README.md"), "# EASY-v1 Baseline Error Analysis\n\n%s\n" % blocker_note)


def metric_row(label, metrics):
    per_class = {}
    for item in metrics.get("per_class", []):
        per_class[item["class_name"]] = item
    return {
        "label": label,
        "precision": metrics.get("box_precision"),
        "recall": metrics.get("box_recall"),
        "map50": metrics.get("box_map50"),
        "map": metrics.get("box_map"),
        "f1": metrics.get("box_f1"),
        "boat": per_class.get("boat"),
        "ship": per_class.get("ship"),
        "buoy": per_class.get("buoy"),
    }


def synthesize_global_metrics(metrics):
    per_class = metrics.get("per_class", [])
    if not per_class:
        return metrics
    precision = sum(item["precision"] for item in per_class) / float(len(per_class))
    recall = sum(item["recall"] for item in per_class) / float(len(per_class))
    map50 = sum(item["map50"] for item in per_class) / float(len(per_class))
    map95 = sum(item["map"] for item in per_class) / float(len(per_class))
    f1_values = []
    for item in per_class:
        p = item["precision"]
        r = item["recall"]
        f1_values.append((2 * p * r / (p + r)) if (p + r) else 0.0)
    metrics = dict(metrics)
    metrics["box_precision"] = precision
    metrics["box_recall"] = recall
    metrics["box_map50"] = map50
    metrics["box_map"] = map95
    metrics["box_f1"] = sum(f1_values) / float(len(f1_values))
    return metrics


def write_baseline_report(config, runtime_status):
    val_metrics = load_metrics(abspath(config["baseline"]["historical_val_metrics"]))
    test_metrics = load_metrics(abspath(config["baseline"]["historical_test_metrics"]))

    lines = []
    lines.append("# EASY-v1 Baseline Full Evaluation")
    lines.append("")
    lines.append("Generated as part of the Phase 1 optimization scaffolding.")
    lines.append("")
    lines.append("## Baseline Reference")
    lines.append("")
    lines.append("- Run: `%s`" % config["baseline"]["name"])
    lines.append("- Weights: `%s`" % config["baseline"]["weights"])
    lines.append("- Historical project dir: `%s`" % config["baseline"]["project_dir"])
    lines.append("- Preferred runtime executable: `%s`" % runtime_status["python"]["executable"])
    lines.append("")
    lines.append("## Runtime Status")
    lines.append("")
    if runtime_status["blockers"]:
        lines.append("Fresh baseline re-evaluation is currently blocked.")
        lines.append("")
        for blocker in runtime_status["blockers"]:
            lines.append("- %s" % blocker)
    else:
        lines.append("Runtime is ready for fresh re-evaluation.")
    lines.append("")

    for split_name, metrics in [("Validation", val_metrics), ("Test", test_metrics)]:
        lines.append("## %s Metrics" % split_name)
        lines.append("")
        if not metrics:
            lines.append("Metrics file not found.")
            lines.append("")
            continue
        metrics = synthesize_global_metrics(metrics)
        lines.append("| Metric | Value |")
        lines.append("| --- | ---: |")
        lines.append("| Precision | %s |" % format_float(metrics.get("box_precision")))
        lines.append("| Recall | %s |" % format_float(metrics.get("box_recall")))
        lines.append("| mAP50 | %s |" % format_float(metrics.get("box_map50")))
        lines.append("| mAP50-95 | %s |" % format_float(metrics.get("box_map")))
        lines.append("| F1 | %s |" % format_float(metrics.get("box_f1")))
        lines.append("")
        lines.append("| Class | Precision | Recall | mAP50 | mAP50-95 | F1 |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for item in metrics.get("per_class", []):
            f1 = item.get("f1")
            if f1 is None:
                p = item["precision"]
                r = item["recall"]
                f1 = (2 * p * r / (p + r)) if (p + r) else 0.0
            lines.append(
                "| %s | %s | %s | %s | %s | %s |"
                % (
                    item["class_name"],
                    format_float(item["precision"]),
                    format_float(item["recall"]),
                    format_float(item["map50"]),
                    format_float(item["map"]),
                    format_float(f1),
                )
            )
        lines.append("")

    lines.append("## Confusion Matrices")
    lines.append("")
    lines.append("- Historical train/eval confusion matrix: `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/confusion_matrix.png`")
    lines.append("- Historical validation confusion matrix: `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced_val/confusion_matrix.png`")
    lines.append("- Test confusion matrix is not available as a standalone historical artifact in the current repository snapshot.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- This report consolidates verified historical metrics already present in the repository.")
    lines.append("- A fresh Phase 1 re-run on both validation and test is intentionally deferred until the runtime blockers in `docs/model_optimization/easy_v1_runtime_status.md` are cleared.")
    lines.append("- No new evaluation metrics were fabricated in the blocked state.")
    lines.append("")
    write_text(abspath(config["outputs"]["baseline_report"]), "\n".join(lines) + "\n")


def write_comparison_report(config, runtime_status):
    baseline_test = load_metrics(abspath(config["baseline"]["historical_test_metrics"]))
    baseline_val = load_metrics(abspath(config["baseline"]["historical_val_metrics"]))
    if baseline_test:
        baseline_test = synthesize_global_metrics(baseline_test)
    if baseline_val:
        baseline_val = synthesize_global_metrics(baseline_val)

    def split_section(title, baseline_metrics):
        lines = []
        lines.append("## %s" % title)
        lines.append("")
        lines.append("| Run name | Model | imgsz | epochs | precision | recall | mAP50 | mAP50-95 | boat P/R/mAP50 | ship P/R/mAP50 | buoy P/R/mAP50 | model size | inference speed | qualitative notes |")
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |")
        if baseline_metrics:
            boat = baseline_metrics["per_class"][0]
            ship = baseline_metrics["per_class"][1]
            buoy = baseline_metrics["per_class"][2]
            lines.append(
                "| %s | YOLOv8n | 640 | 50 | %s | %s | %s | %s | %s/%s/%s | %s/%s/%s | %s/%s/%s | %s MB | unavailable | Historical baseline artifact already in repo |"
                % (
                    config["baseline"]["name"],
                    format_float(baseline_metrics.get("box_precision")),
                    format_float(baseline_metrics.get("box_recall")),
                    format_float(baseline_metrics.get("box_map50")),
                    format_float(baseline_metrics.get("box_map")),
                    format_float(boat["precision"]),
                    format_float(boat["recall"]),
                    format_float(boat["map50"]),
                    format_float(ship["precision"]),
                    format_float(ship["recall"]),
                    format_float(ship["map50"]),
                    format_float(buoy["precision"]),
                    format_float(buoy["recall"]),
                    format_float(buoy["map50"]),
                    format_float(file_size_mb(abspath(config["baseline"]["weights"])), 2),
                )
            )
        for experiment in config["experiments"]:
            lines.append(
                "| %s | %s | %s | %s | blocked | blocked | blocked | blocked | blocked | blocked | blocked | n/a | n/a | Waiting for runtime provisioning: %s |"
                % (
                    experiment["run_name"],
                    experiment["model"],
                    experiment["imgsz"],
                    experiment["epochs"],
                    "; ".join(runtime_status["blockers"]) if runtime_status["blockers"] else "runtime ready",
                )
            )
        lines.append("")
        return lines

    lines = []
    lines.append("# EASY-v1 Experiment Comparison")
    lines.append("")
    lines.append("This comparison report is scaffolded now and will become authoritative after the three Phase 1 experiments are executed.")
    lines.append("")
    lines.extend(split_section("Validation", baseline_val))
    lines.extend(split_section("Test", baseline_test))
    lines.append("## Notes")
    lines.append("")
    lines.append("- Baseline rows come from repository artifacts already present.")
    lines.append("- Experiments A/B/C remain intentionally unrun until the ML runtime blockers are removed.")
    lines.append("")
    write_text(abspath(config["outputs"]["comparison_report"]), "\n".join(lines) + "\n")


def write_selection_report(config, runtime_status):
    lines = []
    lines.append("# EASY-v1 Model Selection")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    if runtime_status["blockers"]:
        lines.append("Final model selection is deferred.")
        lines.append("")
        lines.append("Reason: the Phase 1 experiment matrix was not executed because the required runtime is not provisioned.")
        lines.append("")
        for blocker in runtime_status["blockers"]:
            lines.append("- %s" % blocker)
        lines.append("")
        lines.append("No file was copied to `models/easy_v1_best_rgb.pt` because that would falsely imply a new Phase 1 selection.")
    else:
        lines.append("Runtime is ready; execute the comparison and selection workflow.")
    lines.append("")
    lines.append("## Selection Criteria")
    lines.append("")
    lines.append("1. Buoy recall")
    lines.append("2. Recall stability across boat/ship/buoy")
    lines.append("3. Global mAP50")
    lines.append("4. Global mAP50-95")
    lines.append("5. Model size")
    lines.append("6. Raspberry deployability")
    lines.append("")
    write_text(abspath(config["outputs"]["selection_report"]), "\n".join(lines) + "\n")


def write_deployment_notes(config, runtime_status):
    lines = []
    lines.append("# Deployment Notes")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    if runtime_status["blockers"]:
        lines.append("ONNX export is blocked because no final Phase 1 model has been selected and the required runtime is missing.")
        lines.append("")
        for blocker in runtime_status["blockers"]:
            lines.append("- %s" % blocker)
    else:
        lines.append("Runtime ready for ONNX export.")
    lines.append("")
    lines.append("## Planned Export Command")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 -m ultralytics export model=models/easy_v1_best_rgb.pt format=onnx imgsz=640 opset=12 simplify=True")
    lines.append("```")
    lines.append("")
    lines.append("Planned runtime executable: `%s`." % runtime_status["python"]["executable"])
    lines.append("")
    lines.append("## Deployment Defaults")
    lines.append("")
    lines.append("- Class mapping: `0=boat`, `1=ship`, `2=buoy`.")
    lines.append("- Preprocessing must match RGB input with Ultralytics letterbox behavior for the chosen `imgsz`.")
    lines.append("- Raspberry validation still needs latency, memory, and numerical parity checks on representative maritime frames.")
    lines.append("")
    write_text(abspath(config["outputs"]["deployment_notes"]), "\n".join(lines) + "\n")


def write_command_log(config):
    runtime_python = config["runtime_requirements"].get("preferred_python", "python3")
    lines = []
    lines.append("# EASY-v1 Phase 1 Command Log")
    lines.append("")
    lines.append("## Commands run in this repository snapshot")
    lines.append("")
    lines.append("```bash")
    lines.append("%s scripts/model_optimization/easy_v1_phase1.py runtime-check" % runtime_python)
    lines.append("%s scripts/model_optimization/easy_v1_phase1.py dataset-audit" % runtime_python)
    lines.append("%s scripts/model_optimization/easy_v1_phase1.py scaffold-phase1" % runtime_python)
    lines.append("```")
    lines.append("")
    lines.append("## Commands to run after runtime provisioning")
    lines.append("")
    lines.append("```bash")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_setup_runtime.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_runtime_check.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_baseline_full.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_exp_a.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_exp_b.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_exp_c.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_eval_a.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_eval_b.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_eval_c.sbatch")
    lines.append("sbatch scripts/slurm/easy_v1_phase1_finalize.sbatch")
    lines.append("```")
    lines.append("")
    write_text(abspath(config["outputs"]["command_log"]), "\n".join(lines) + "\n")


def write_slurm_scripts(config):
    slurm = config["slurm"]
    job_dir = abspath(slurm["job_dir"])
    log_dir = abspath(slurm["logs_dir"])
    if not os.path.isdir(job_dir):
        os.makedirs(job_dir)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    def build_script(job_name, command):
        lines = [
            "#!/bin/bash",
            "#SBATCH --job-name=%s" % job_name,
            "#SBATCH --output=%s/%%x-%%j.out" % log_dir,
            "#SBATCH --error=%s/%%x-%%j.err" % log_dir,
            "#SBATCH --time=%s" % slurm["time"],
            "#SBATCH --cpus-per-task=%s" % slurm["cpus_per_task"],
            "#SBATCH --mem=%s" % slurm["mem"],
        ]
        if slurm.get("partition"):
            lines.append("#SBATCH --partition=%s" % slurm["partition"])
        if slurm.get("gres"):
            lines.append("#SBATCH --gres=%s" % slurm["gres"])
        lines.extend(
            [
                "",
                "set -euo pipefail",
                "cd %s" % ROOT,
                "PYTHON_BIN=%s" % abspath(config["runtime_requirements"]["preferred_python"]),
                "export MPLCONFIGDIR=/tmp/easy_v1_mpl_${SLURM_JOB_ID:-local}",
                "mkdir -p \"$MPLCONFIGDIR\"",
                "if [ ! -x \"$PYTHON_BIN\" ]; then",
                "  echo \"Missing runtime python: $PYTHON_BIN\"",
                "  exit 1",
                "fi",
                "",
                command,
                "",
            ]
        )
        return lines

    scripts = {
        "scripts/slurm/easy_v1_phase1_setup_runtime.sbatch": build_script(
            "easyv1_setup",
            "\n".join(
                [
                    "mkdir -p models/pretrained",
                    "\"$PYTHON_BIN\" -m pip install --upgrade onnx",
                    "\"$PYTHON_BIN\" - <<'PY'",
                    "from ultralytics.utils.downloads import attempt_download_asset",
                    "import os, shutil",
                    "target = os.path.join('models', 'pretrained', 'yolov8s.pt')",
                    "if not os.path.exists(target):",
                    "    source = attempt_download_asset('yolov8s.pt')",
                    "    shutil.copy2(source, target)",
                    "print('ready', target, os.path.getsize(target))",
                    "PY",
                ]
            ),
        ),
        "scripts/slurm/easy_v1_phase1_runtime_check.sbatch": build_script(
            "easyv1_rtcheck",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1.py runtime-check",
        ),
        "scripts/slurm/easy_v1_phase1_dataset_audit.sbatch": build_script(
            "easyv1_dsaudit",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1.py dataset-audit",
        ),
        "scripts/slurm/easy_v1_phase1_scaffold.sbatch": build_script(
            "easyv1_scaffold",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1.py scaffold-phase1",
        ),
        "scripts/slurm/easy_v1_phase1_baseline_full.sbatch": build_script(
            "easyv1_base",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py baseline-full",
        ),
        "scripts/slurm/easy_v1_phase1_rebuild_baseline_artifacts.sbatch": build_script(
            "easyv1_baseart",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py rebuild-baseline-artifacts",
        ),
        "scripts/slurm/easy_v1_phase1_exp_a.sbatch": build_script(
            "easyv1_exp_a",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py run-experiment --experiment-id A",
        ),
        "scripts/slurm/easy_v1_phase1_exp_b.sbatch": build_script(
            "easyv1_exp_b",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py run-experiment --experiment-id B",
        ),
        "scripts/slurm/easy_v1_phase1_exp_c.sbatch": build_script(
            "easyv1_exp_c",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py run-experiment --experiment-id C",
        ),
        "scripts/slurm/easy_v1_phase1_eval_a.sbatch": build_script(
            "easyv1_eval_a",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py eval-experiment --experiment-id A",
        ),
        "scripts/slurm/easy_v1_phase1_eval_b.sbatch": build_script(
            "easyv1_eval_b",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py eval-experiment --experiment-id B",
        ),
        "scripts/slurm/easy_v1_phase1_eval_c.sbatch": build_script(
            "easyv1_eval_c",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py eval-experiment --experiment-id C",
        ),
        "scripts/slurm/easy_v1_phase1_finalize.sbatch": build_script(
            "easyv1_final",
            "\"$PYTHON_BIN\" scripts/model_optimization/easy_v1_phase1_ultralytics.py finalize",
        ),
    }

    for rel_path, lines in scripts.items():
        write_text(abspath(rel_path), "\n".join(lines))


def cmd_runtime_check(config):
    runtime_status = gather_runtime_status(config)
    write_json(abspath(config["outputs"]["runtime_json"]), runtime_status)
    write_runtime_report(config, runtime_status)
    print("Wrote runtime status to %s" % config["outputs"]["runtime_report"])


def cmd_dataset_audit(config):
    dataset_status = gather_dataset_status(config)
    write_json(abspath(config["outputs"]["dataset_json"]), dataset_status)
    write_dataset_report(config, dataset_status)
    print("Wrote dataset status to %s" % config["outputs"]["dataset_report"])


def cmd_scaffold_phase1(config):
    runtime_status = gather_runtime_status(config)
    write_json(abspath(config["outputs"]["runtime_json"]), runtime_status)
    write_runtime_report(config, runtime_status)
    dataset_status = gather_dataset_status(config)
    write_json(abspath(config["outputs"]["dataset_json"]), dataset_status)
    write_dataset_report(config, dataset_status)
    write_baseline_report(config, runtime_status)
    write_error_analysis_scaffold(config, runtime_status)
    write_comparison_report(config, runtime_status)
    write_selection_report(config, runtime_status)
    write_deployment_notes(config, runtime_status)
    write_command_log(config)
    write_slurm_scripts(config)
    print("Scaffolded Phase 1 reports and blocker artifacts.")


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/model_optimization/easy_v1_phase1.json",
        help="Path to Phase 1 config JSON relative to repo root.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    subparsers.add_parser("runtime-check")
    subparsers.add_parser("dataset-audit")
    subparsers.add_parser("scaffold-phase1")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(abspath(args.config))
    if args.command == "runtime-check":
        cmd_runtime_check(config)
    elif args.command == "dataset-audit":
        cmd_dataset_audit(config)
    elif args.command == "scaffold-phase1":
        cmd_scaffold_phase1(config)
    else:  # pragma: no cover
        parser.error("unknown command: %s" % args.command)


if __name__ == "__main__":
    main()
