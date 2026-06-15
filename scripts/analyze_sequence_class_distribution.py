#!/usr/bin/env python3
"""Analyze class distribution per pseudo-sequence for the active balanced-v2 dataset."""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


CLASS_NAMES = {0: "boat", 1: "ship", 2: "buoy"}
SPLITS = ("train", "val", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze pseudo-sequence class distribution")
    parser.add_argument("--dataset-root", default="data/processed/EASY-v0-rgb3-balanced-v2")
    parser.add_argument("--md-output", default="outputs/reports/sequence_class_distribution.md")
    parser.add_argument("--csv-output", default="outputs/reports/sequence_class_distribution.csv")
    return parser.parse_args()


def parse_pseudo_sequence(stem: str, seaships_block_size: int = 256) -> tuple[str, str]:
    if "__" in stem:
        dataset_prefix, source_id = stem.split("__", 1)
    else:
        match = re.match(r"(?P<prefix>[A-Za-z]+)", stem)
        dataset_prefix = match.group("prefix").lower() if match else "unknown"
        source_id = stem

    smd_match = re.match(r"(?P<video>.+?)_frame_(?P<number>\d+)$", source_id)
    if dataset_prefix == "smd" and smd_match:
        return dataset_prefix, f"smd:{smd_match.group('video')}"

    generic_match = re.match(r"(?P<prefix>.*?)(?P<number>\d+)$", source_id)
    if dataset_prefix == "seaships" and generic_match:
        raw_prefix = generic_match.group("prefix").rstrip("_-")
        number = int(generic_match.group("number"))
        if raw_prefix:
            return dataset_prefix, f"seaships:{raw_prefix}"
        return dataset_prefix, f"seaships:block_{number // seaships_block_size:04d}"

    if generic_match and generic_match.group("prefix").rstrip("_-"):
        raw_prefix = generic_match.group("prefix").rstrip("_-")
        return dataset_prefix, f"{dataset_prefix}:{raw_prefix}"

    return dataset_prefix, f"single:{stem}"


def safe_mean(values):
    return sum(values) / len(values) if values else 0.0


def load_sequences(dataset_root: Path) -> dict[str, dict]:
    sequences = defaultdict(
        lambda: {
            "source": None,
            "images": 0,
            "original_splits": Counter(),
            "class_counts": Counter({class_id: 0 for class_id in CLASS_NAMES}),
            "class_area": defaultdict(list),
            "class_ar": defaultdict(list),
        }
    )
    for split in SPLITS:
        label_dir = dataset_root / "labels" / split
        for label_path in sorted(label_dir.glob("*.txt")):
            source, pseudo = parse_pseudo_sequence(label_path.stem)
            record = sequences[pseudo]
            record["source"] = source
            record["images"] += 1
            record["original_splits"][split] += 1
            for line in label_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split()
                class_id = int(parts[0])
                width = float(parts[3])
                height = float(parts[4])
                area = width * height
                aspect = 0.0 if height == 0 else width / height
                record["class_counts"][class_id] += 1
                record["class_area"][class_id].append(area)
                record["class_ar"][class_id].append(aspect)
    return sequences


def dominance_label(record: dict) -> tuple[str, float]:
    total = sum(record["class_counts"].values())
    if total == 0:
        return "empty", 0.0
    class_id, count = max(record["class_counts"].items(), key=lambda item: item[1])
    return CLASS_NAMES[class_id], count / total


def quasi_monoclass(record: dict) -> bool:
    _, share = dominance_label(record)
    return share >= 0.90


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def top_sequences(sequences: dict[str, dict], class_id: int, limit: int = 10):
    rows = []
    for pseudo, record in sequences.items():
        count = record["class_counts"][class_id]
        if count == 0:
            continue
        rows.append((pseudo, count, record["images"], record["source"]))
    return sorted(rows, key=lambda row: (-row[1], -row[2], row[0]))[:limit]


def proposed_balanced_v2_assignment(pseudo: str) -> tuple[str, str]:
    manual = {
        "smd:MVI_0790_VIS_OB": (
            "train",
            "Mixed boat+buoy sequence; indispensable to couple buoy with real boat background and avoid a pure-buoy-only train regime.",
        ),
        "smd:MVI_0801_VIS_OB": (
            "val",
            "Small held-out SMD boat-only sequence; useful validation anchor for boat without removing the main boat-only SMD support from train.",
        ),
        "smd:MVI_1469_VIS": (
            "val",
            "Large vertical buoy regime; best validation stress-test for buoy generalization.",
        ),
        "smd:MVI_1474_VIS": (
            "train",
            "Highest buoy count and tiny-buoy regime; indispensable for buoy learning.",
        ),
        "smd:MVI_1481_VIS": (
            "test",
            "Second large vertical buoy regime; best reserved as held-out buoy test.",
        ),
        "smd:MVI_1486_VIS": (
            "train",
            "Bridge buoy regime between tiny and large vertical buoys; needed in train for buoy diversity.",
        ),
        "smd:MVI_1584_VIS": (
            "train",
            "Major boat-only SMD sequence; necessary to prevent boat collapse on SMD-style boats.",
        ),
        "smd:MVI_1587_VIS": (
            "train",
            "Second major boat-only SMD sequence; complements MVI_1584 and stabilizes boat training support.",
        ),
        "seaships:block_0008": (
            "val",
            "Mixed boat/ship block with strong boat presence; useful validation coverage for SeaShips boat+ship.",
        ),
        "seaships:block_0009": (
            "val",
            "Ship-dominant but boat-rich SeaShips block; good validation anchor for mixed maritime scenes.",
        ),
        "seaships:block_0010": (
            "train",
            "One of the strongest boat-rich SeaShips blocks; keep in train to support boat learning.",
        ),
        "seaships:block_0011": (
            "train",
            "Another strongest boat-rich SeaShips block; keep in train to support boat learning.",
        ),
        "seaships:block_0016": (
            "test",
            "Boat-heavy SeaShips hold-out block; useful for boat test coverage.",
        ),
        "seaships:block_0017": (
            "test",
            "Mixed boat/ship hold-out block; complements test boat coverage.",
        ),
        "seaships:block_0020": (
            "val",
            "Largest ship-heavy SeaShips component; good validation anchor for ship without exhausting train.",
        ),
        "seaships:block_0023": (
            "test",
            "Second large ship-heavy SeaShips component; useful independent ship test anchor.",
        ),
        "seaships:block_0026": (
            "test",
            "Boat-rich SeaShips hold-out block; complements block_0016 in test.",
        ),
        "seaships:block_0027": (
            "test",
            "Small mixed hold-out block; low-risk addition to test.",
        ),
    }
    if pseudo in manual:
        return manual[pseudo]
    return (
        "train",
        "Default to train to maximize data volume unless the sequence is explicitly needed as a held-out validation/test anchor.",
    )


def write_csv(path: Path, sequences: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "pseudo_sequence",
        "source",
        "images",
        "boat_count",
        "ship_count",
        "buoy_count",
        "boat_area_mean",
        "ship_area_mean",
        "buoy_area_mean",
        "boat_aspect_mean",
        "ship_aspect_mean",
        "buoy_aspect_mean",
        "dominant_class",
        "dominant_share",
        "quasi_monoclass",
        "proposed_balanced_v2_split",
        "proposed_reason",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for pseudo, record in sorted(sequences.items()):
            dominant, share = dominance_label(record)
            split, reason = proposed_balanced_v2_assignment(pseudo)
            writer.writerow(
                [
                    pseudo,
                    record["source"],
                    record["images"],
                    record["class_counts"][0],
                    record["class_counts"][1],
                    record["class_counts"][2],
                    f"{safe_mean(record['class_area'][0]):.6f}",
                    f"{safe_mean(record['class_area'][1]):.6f}",
                    f"{safe_mean(record['class_area'][2]):.6f}",
                    f"{safe_mean(record['class_ar'][0]):.6f}",
                    f"{safe_mean(record['class_ar'][1]):.6f}",
                    f"{safe_mean(record['class_ar'][2]):.6f}",
                    dominant,
                    f"{share:.4f}",
                    "yes" if quasi_monoclass(record) else "no",
                    split,
                    reason,
                ]
            )


def write_markdown(path: Path, sequences: dict[str, dict], csv_path: Path) -> None:
    rows = []
    buoy_sequences = []
    boat_sequences = []
    ship_sequences = []
    quasi = []
    for pseudo, record in sorted(sequences.items()):
        dominant, share = dominance_label(record)
        split, reason = proposed_balanced_v2_assignment(pseudo)
        rows.append(
            [
                pseudo,
                record["source"],
                record["images"],
                record["class_counts"][0],
                record["class_counts"][1],
                record["class_counts"][2],
                f"{safe_mean(record['class_area'][0]):.5f}",
                f"{safe_mean(record['class_area'][1]):.5f}",
                f"{safe_mean(record['class_area'][2]):.5f}",
                f"{safe_mean(record['class_ar'][0]):.3f}",
                f"{safe_mean(record['class_ar'][1]):.3f}",
                f"{safe_mean(record['class_ar'][2]):.3f}",
                dominant,
                f"{share*100:.1f}%",
                "yes" if quasi_monoclass(record) else "no",
                split,
            ]
        )
        if record["class_counts"][2] > 0:
            buoy_sequences.append(pseudo)
        if record["class_counts"][0] > 0:
            boat_sequences.append(pseudo)
        if record["class_counts"][1] > 0:
            ship_sequences.append(pseudo)
        if quasi_monoclass(record):
            quasi.append((pseudo, dominant, share))

    class_answers = {
        "boat": top_sequences(sequences, 0),
        "ship": top_sequences(sequences, 1),
        "buoy": top_sequences(sequences, 2),
    }

    train_indispensable = [
        ("smd:MVI_1474_VIS", "largest tiny-buoy source; without it the model loses the main small-buoy regime"),
        ("smd:MVI_1486_VIS", "mid-scale buoy bridge sequence; needed to avoid a single buoy morphology in train"),
        ("smd:MVI_0790_VIS_OB", "only mixed boat+buoy sequence; anchors buoy in real boat context"),
        ("smd:MVI_1584_VIS", "largest boat-only SMD regime"),
        ("smd:MVI_1587_VIS", "second boat-only SMD regime; complements MVI_1584"),
        ("seaships:block_0010", "strong SeaShips boat support"),
        ("seaships:block_0011", "strong SeaShips boat support"),
        ("seaships:block_0009", "largest mixed boat/ship SeaShips support"),
        ("seaships:block_0020", "largest ship-heavy SeaShips support if train ratio allows"),
    ]

    val_indispensable = [
        ("smd:MVI_1469_VIS", "best held-out buoy validation regime; large vertical buoy domain"),
        ("smd:MVI_0801_VIS_OB", "held-out SMD boat validation anchor"),
        ("seaships:block_0008", "mixed boat/ship validation support"),
        ("seaships:block_0009", "mixed ship-dominant validation support if not kept in train"),
        ("seaships:block_0020", "ship-heavy validation anchor if not kept in train"),
    ]

    proposed_rows = []
    for pseudo, record in sorted(sequences.items()):
        split, reason = proposed_balanced_v2_assignment(pseudo)
        proposed_rows.append([pseudo, split, reason])

    lines = [
        "# Sequence Class Distribution",
        "",
        f"CSV export: `{csv_path}`",
        "",
        "## Full Table",
        "",
        markdown_table(
            [
                "Pseudo-sequence",
                "Source",
                "Images",
                "Boat",
                "Ship",
                "Buoy",
                "Boat area mean",
                "Ship area mean",
                "Buoy area mean",
                "Boat AR mean",
                "Ship AR mean",
                "Buoy AR mean",
                "Dominant",
                "Dominant share",
                "Quasi monoclasse",
                "balanced_v2",
            ],
            rows,
        ),
        "",
        "## Answers",
        "",
        "### 1. Quali sequenze contengono buoy?",
        "",
    ]
    lines.extend([f"- `{sequence}`" for sequence in buoy_sequences])
    lines.extend(["", "### 2. Quali sequenze contengono boat?", ""])
    lines.extend([f"- `{sequence}`" for sequence in boat_sequences])
    lines.extend(["", "### 3. Quali sequenze contengono ship?", ""])
    lines.extend([f"- `{sequence}`" for sequence in ship_sequences])

    lines.extend(["", "### 4. Quali sequenze dominano ogni classe?", ""])
    for class_name in ["boat", "ship", "buoy"]:
        lines.append(f"Top `{class_name}` sequences:")
        lines.extend([f"- `{seq}`: {count} {class_name} objects over {images} images ({source})" for seq, count, images, source in class_answers[class_name]])
        lines.append("")

    lines.extend(["### 5. Esistono sequenze quasi monoclasse?", ""])
    lines.extend([f"- `{seq}`: dominant class `{dominant}` at {share*100:.1f}% of objects" for seq, dominant, share in quasi])
    lines.extend(
        [
            "",
            "Interpretation:",
            "- Many SeaShips blocks are effectively `ship`-only or `ship`-dominant.",
            "- `smd:MVI_1469_VIS`, `smd:MVI_1474_VIS`, `smd:MVI_1481_VIS`, `smd:MVI_1486_VIS` are pure `buoy` sequences.",
            "- `smd:MVI_1584_VIS` and `smd:MVI_1587_VIS` are pure `boat` sequences.",
            "- `smd:MVI_0790_VIS_OB` is the only meaningful mixed `boat+buoy` SMD sequence.",
            "",
            "### 6. Quali sequenze sono indispensabili per train?",
            "",
        ]
    )
    lines.extend([f"- `{seq}`: {reason}" for seq, reason in train_indispensable])
    lines.extend(["", "### 7. Quali sequenze sono indispensabili per validation?", ""])
    lines.extend([f"- `{seq}`: {reason}" for seq, reason in val_indispensable])
    lines.extend(
        [
            "",
            "## balanced_v2 Proposal",
            "",
            "Key constraint:",
            "- There are only **5** buoy-bearing pseudo-sequences in the whole dataset.",
            "- Of those 5, only **1** (`smd:MVI_0790_VIS_OB`) is mixed with another class.",
            "- Therefore it is impossible to give train, validation and test all rich buoy diversity while also keeping strict sequence isolation.",
            "",
            "Design principle for `balanced_v2`:",
            "- Prioritize **train diversity** for buoy and boat so the model can actually learn both classes.",
            "- Use validation as a **hard held-out buoy generalization check**.",
            "- Keep test as an additional held-out check, but accept that buoy support there will remain sparse.",
            "",
            markdown_table(["Pseudo-sequence", "Proposed split", "Reason"], proposed_rows),
            "",
            "Practical recommendation:",
            "- Keep `smd:MVI_1474_VIS`, `smd:MVI_1486_VIS` and `smd:MVI_0790_VIS_OB` in `train`.",
            "- Keep `smd:MVI_1584_VIS` and `smd:MVI_1587_VIS` in `train` to avoid another `boat` collapse.",
            "- Use `smd:MVI_1469_VIS` as the main `val` buoy stress-test.",
            "- Use `smd:MVI_1481_VIS` as the main `test` buoy hold-out.",
            "- Build the final split solver around these fixed anchors, then distribute SeaShips blocks to restore approximate ratio and ship coverage.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root)
    md_output = Path(args.md_output)
    csv_output = Path(args.csv_output)
    sequences = load_sequences(dataset_root)
    write_csv(csv_output, sequences)
    write_markdown(md_output, sequences, csv_output)
    print(md_output)
    print(csv_output)


if __name__ == "__main__":
    main()
