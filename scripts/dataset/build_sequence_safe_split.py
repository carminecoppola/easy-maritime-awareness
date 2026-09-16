#!/usr/bin/env python3
"""Costruttore di split train/val/test sequence-safe.

Assegna sempre l'intera sequenza (video/blocco sorgente) a un solo split,
mai la singola immagine, con audit di leakage obbligatorio a fine build.
Vedi outputs/reports/EASY_v3_results.md per il contesto (leakage nello
split ufficiale EASY-v1).

Supporta piu' source-root e, se presente un manifest.csv (stem/filename,
sequence_id) nella cartella sorgente, usa quello invece di inferire la
sequenza dal nome file.

Uso:
    venv/bin/python scripts/dataset/build_sequence_safe_split.py \
        --source-root archive/datasets/EASY-v0-rgb3-clean \
        --output-root data/processed/<nome-candidato> \
        --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 \
        --seed 42

Il dataset prodotto è un candidato da valutare, non sostituisce
automaticamente EASY-v1-rgb3-buoy-rebalanced.
"""

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

SPLITS = ("train", "val", "test")
CLASS_NAMES = {0: "boat", 1: "ship", 2: "buoy"}
BUOY_CLASS_ID = 2
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


@dataclass(frozen=True)
class Item:
    image_path: Path
    label_path: Path
    stem: str
    dataset_prefix: str
    sequence_id: str
    image_fingerprint: str
    objects: tuple


class UnionFind:
    """Fonde pseudo-sequenze quando due immagini risultano identiche (stesso
    contenuto file), cosi' un duplicato accidentale tra due sequenze diverse
    non puo' comunque finire in split diversi."""

    def __init__(self):
        self.parent = {}

    def add(self, value):
        self.parent.setdefault(value, value)

    def find(self, value):
        self.add(value)
        if self.parent[value] != value:
            self.parent[value] = self.find(self.parent[value])
        return self.parent[value]

    def union(self, left, right):
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source-root", required=True, action="append",
                   help="dataset da includere nello split: o con images/{train,val,test} e labels/{train,val,test} "
                        "(dataset gia' splittato altrove, viene ri-splittato da zero), oppure con images/ e labels/ "
                        "piatte senza sotto-cartelle di split (pool unico, es. un dataset esterno curato apposta). "
                        "Ripetibile per includere piu' sorgenti nello stesso split sequence-safe (es. dati EASY "
                        "attuali + un dataset pubblico aggiuntivo). Ogni fonte mantiene il proprio prefisso "
                        "dataset (dal nome file, es. 'aboships__...') quindi le sequenze non collidono tra fonti.")
    p.add_argument("--output-root", required=True)
    p.add_argument("--report", default=None, help="default: <output-root>/split_report.md")
    p.add_argument("--pinned-assignments", default=None,
                   help="YAML opzionale {sequence_id: split} per fissare manualmente alcune sequenze note (es. stress-test), tutte le altre vengono stratificate automaticamente")
    p.add_argument("--train-ratio", type=float, default=0.7)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--test-ratio", type=float, default=0.15)
    p.add_argument("--seaships-block-size", type=int, default=256)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def partial_file_fingerprint(path, chunk_size=8192):
    stat = path.stat()
    digest = hashlib.sha256()
    digest.update(str(stat.st_size).encode("ascii"))
    with path.open("rb") as handle:
        digest.update(handle.read(chunk_size))
        if stat.st_size > chunk_size:
            handle.seek(max(0, stat.st_size - chunk_size))
            digest.update(handle.read(chunk_size))
    return f"{stat.st_size}:{digest.hexdigest()}"


def parse_label(path):
    if not path.exists():
        return tuple()
    objects = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if len(parts) != 5:
            continue
        objects.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
    return tuple(objects)


def parse_sequence_id(stem, seaships_block_size):
    """Deriva un identificatore di sequenza dal nome file. Stesso schema gia'
    validato in `archive/scripts/build_easy_v0_rgb3_balanced_v2_split.py`
    (SMD: video sorgente; SeaShips: blocco di N frame consecutivi, dato che
    SeaShips non espone un id di sequenza esplicito nel nome file)."""
    if "__" in stem:
        dataset_prefix, source_id = stem.split("__", 1)
    else:
        match = re.match(r"(?P<prefix>[A-Za-z]+)", stem)
        dataset_prefix = match.group("prefix").lower() if match else "unknown"
        source_id = stem

    smd_match = re.match(r"(?P<video>.+?)_frame_(?P<number>\d+)$", source_id)
    if dataset_prefix == "smd" and smd_match:
        return dataset_prefix, source_id, f"smd:{smd_match.group('video')}"

    # ABOships: durante la curation lo stem viene costruito come
    # "aboships__<YYYYMMDD>_<nome originale>" (la data e' la cartella di
    # sessione di registrazione originale, l'unico raggruppamento in
    # sequenze disponibile per questo dataset). Una sessione/giorno = una
    # sequenza, mai una singola immagine.
    aboships_match = re.match(r"(?P<date>\d{8})_", source_id)
    if dataset_prefix == "aboships" and aboships_match:
        return dataset_prefix, source_id, f"aboships:{aboships_match.group('date')}"

    generic_match = re.match(r"(?P<prefix>.*?)(?P<number>\d+)$", source_id)
    if dataset_prefix == "seaships" and generic_match:
        raw_prefix = generic_match.group("prefix").rstrip("_-")
        number = int(generic_match.group("number"))
        if raw_prefix:
            return dataset_prefix, source_id, f"seaships:{raw_prefix}"
        return dataset_prefix, source_id, f"seaships:block_{number // seaships_block_size:04d}"

    if generic_match and generic_match.group("prefix").rstrip("_-"):
        raw_prefix = generic_match.group("prefix").rstrip("_-")
        return dataset_prefix, source_id, f"{dataset_prefix}:{raw_prefix}"

    return dataset_prefix, source_id, f"single:{stem}"


def load_manifest(source_root):
    """Carica manifest.csv (colonne stem/filename, sequence_id) se presente
    nel source-root. Ritorna {} se assente."""
    manifest_path = source_root / "manifest.csv"
    if not manifest_path.exists():
        return {}
    mapping = {}
    with open(manifest_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        stem_field = "stem" if "stem" in (reader.fieldnames or []) else "filename"
        for row in reader:
            stem = Path(row[stem_field]).stem
            mapping[stem] = row["sequence_id"]
    return mapping


def _collect_from_dir(image_dir, label_dir, seaships_block_size, manifest, dataset_tag):
    items = []
    if not image_dir.exists():
        return items
    for image_path in sorted(image_dir.iterdir()):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        label_path = label_dir / f"{image_path.stem}.txt"
        if image_path.stem in manifest:
            # Manifest esplicito: fonte di verita', nessuna inferenza per regex.
            dataset_prefix = dataset_tag
            sequence_id = manifest[image_path.stem]
        else:
            dataset_prefix, _source_id, sequence_id = parse_sequence_id(image_path.stem, seaships_block_size)
        items.append(Item(
            image_path=image_path,
            label_path=label_path,
            stem=image_path.stem,
            dataset_prefix=dataset_prefix,
            sequence_id=sequence_id,
            image_fingerprint=partial_file_fingerprint(image_path),
            objects=parse_label(label_path),
        ))
    return items


def collect_items(source_roots, seaships_block_size):
    """Accetta una o più cartelle sorgente: già splittate
    (images/{train,val,test}) o pool piatti (images/ + labels/). Se presente
    un manifest.csv, la sequenza dichiarata ha precedenza sull'inferenza dal
    nome file."""
    items = []
    for source_root in source_roots:
        manifest = load_manifest(source_root)
        dataset_tag = source_root.name
        found_split_layout = any((source_root / "images" / split).exists() for split in SPLITS)
        if found_split_layout:
            for split in SPLITS:
                items.extend(_collect_from_dir(
                    source_root / "images" / split, source_root / "labels" / split,
                    seaships_block_size, manifest, dataset_tag,
                ))
        else:
            items.extend(_collect_from_dir(
                source_root / "images", source_root / "labels",
                seaships_block_size, manifest, dataset_tag,
            ))
    return items


def merge_duplicate_sequences(items):
    """Se un'immagine identica (stesso fingerprint) compare sotto due
    pseudo-sequenze diverse, le fonde in un unico componente: altrimenti un
    duplicato accidentale potrebbe finire in due split diversi."""
    uf = UnionFind()
    by_sequence = defaultdict(list)
    by_fingerprint = defaultdict(list)
    for item in items:
        uf.add(item.sequence_id)
        by_sequence[item.sequence_id].append(item)
        by_fingerprint[item.image_fingerprint].append(item)
    for group in by_fingerprint.values():
        if len(group) <= 1:
            continue
        anchor = group[0].sequence_id
        for item in group[1:]:
            uf.union(anchor, item.sequence_id)
    components = defaultdict(list)
    for sequence_id, seq_items in by_sequence.items():
        components[uf.find(sequence_id)].extend(seq_items)
    return dict(components)


def sequence_stats(component_id, items):
    class_counts = Counter({cid: 0 for cid in CLASS_NAMES})
    for item in items:
        for class_id, *_ in item.objects:
            class_counts[class_id] += 1
    return {
        "component_id": component_id,
        "images": len(items),
        "class_counts": dict(class_counts),
        "buoy_images": sum(1 for item in items if any(c == BUOY_CLASS_ID for c, *_ in item.objects)),
    }


def stratified_assign(components_stats, pinned, train_ratio, val_ratio, test_ratio, seed):
    """Assegna ogni sequenza (mai una singola immagine) a esattamente uno
    split. Le sequenze pinnate vanno dove richiesto; le altre sono ordinate in
    modo deterministico (seed) e assegnate greedy allo split che ne ha piu'
    bisogno per restare vicino ai target di immagini E di boe, cosi' la
    stratificazione sulle boe avviene a livello di sequenza invece che di
    immagine (il bug che ha causato la leakage nello split ufficiale)."""
    import random

    targets = {"train": train_ratio, "val": val_ratio, "test": test_ratio}
    total = sum(t for t in targets.values())
    targets = {k: v / total for k, v in targets.items()}

    assignment = {}
    running_images = {s: 0 for s in SPLITS}
    running_buoy_images = {s: 0 for s in SPLITS}

    remaining = []
    for component_id, stats in components_stats.items():
        if component_id in pinned:
            split = pinned[component_id]
            assignment[component_id] = split
            running_images[split] += stats["images"]
            running_buoy_images[split] += stats["buoy_images"]
        else:
            remaining.append(stats)

    rng = random.Random(seed)
    rng.shuffle(remaining)
    # Ordine deterministico via seed per non favorire sistematicamente una
    # sorgente dataset a parita' di boe.
    buoy_sequences = [s for s in remaining if s["buoy_images"] > 0]
    plain_sequences = [s for s in remaining if s["buoy_images"] == 0]
    buoy_sequences.sort(key=lambda s: -s["buoy_images"])

    total_images = sum(s["images"] for s in components_stats.values())
    total_buoy_images = sum(s["buoy_images"] for s in components_stats.values()) or 1
    BUOY_WEIGHT = 3.0

    # Fase 1: distribuire SOLO le sequenze con boe (risorsa scarsa: solo
    # poche in tutto il dataset) pesando sia il deficit immagini che quello
    # boe, cosi' la stratificazione sulle boe avviene a livello di sequenza
    # invece che di immagine (il bug che ha causato la leakage nello split
    # ufficiale).
    for stats in buoy_sequences:
        best_split, best_score = None, None
        for split in SPLITS:
            image_deficit = (targets[split] * total_images - running_images[split]) / total_images
            buoy_deficit = (targets[split] * total_buoy_images - running_buoy_images[split]) / total_buoy_images
            score = image_deficit + BUOY_WEIGHT * buoy_deficit
            if best_score is None or score > best_score:
                best_score, best_split = score, split
        assignment[stats["component_id"]] = best_split
        running_images[best_split] += stats["images"]
        running_buoy_images[best_split] += stats["buoy_images"]

    # Fase 2: il resto (nessuna boe in gioco) segue solo il bilanciamento
    # immagini. Separata dalla fase 1 apposta: un deficit di boe ormai
    # irraggiungibile per uno split (perche' le boe sono finite) non deve
    # continuare a distorcere per sempre la distribuzione delle immagini
    # restanti verso gli altri split.
    for stats in plain_sequences:
        best_split, best_score = None, None
        for split in SPLITS:
            image_deficit = targets[split] * total_images - running_images[split]
            if best_score is None or image_deficit > best_score:
                best_score, best_split = image_deficit, split
        assignment[stats["component_id"]] = best_split
        running_images[best_split] += stats["images"]

    return assignment


def reset_output(output_root, overwrite):
    if output_root.exists():
        if not overwrite:
            raise FileExistsError(f"{output_root} esiste gia'; passa --overwrite per ricostruirlo")
        shutil.rmtree(output_root)
    for split in SPLITS:
        (output_root / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_root / "labels" / split).mkdir(parents=True, exist_ok=True)


def link_or_copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        import os
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def write_dataset(items_by_split, output_root):
    for split, items in items_by_split.items():
        for item in items:
            link_or_copy(item.image_path, output_root / "images" / split / item.image_path.name)
            if item.label_path.exists():
                link_or_copy(item.label_path, output_root / "labels" / split / item.label_path.name)
    dataset_yaml = {
        "path": str(output_root.resolve()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 3,
        "names": CLASS_NAMES,
    }
    (output_root / "dataset.yaml").write_text(
        yaml.safe_dump(dataset_yaml, sort_keys=False, default_flow_style=False), encoding="utf-8",
    )


def audit_no_cross_split_leakage(assignment, components):
    """Verifica che nessuna sequenza compaia in più di uno split."""
    sequence_to_split = defaultdict(set)
    for component_id, items in components.items():
        split = assignment[component_id]
        for item in items:
            sequence_to_split[item.sequence_id].add(split)
    violations = {seq: splits for seq, splits in sequence_to_split.items() if len(splits) > 1}
    return violations


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(v) for v in row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(output_root, source_roots, items_by_split, components_by_split, assignment, violations, args):
    split_rows = []
    class_rows = []
    for split in SPLITS:
        items = items_by_split[split]
        class_counts = Counter({cid: 0 for cid in CLASS_NAMES})
        for item in items:
            for class_id, *_ in item.objects:
                class_counts[class_id] += 1
        n_sequences = len(components_by_split[split])
        split_rows.append([split, len(items), sum(class_counts.values()), n_sequences])
        total = sum(class_counts.values())
        for class_id, name in CLASS_NAMES.items():
            count = class_counts[class_id]
            pct = "0.00%" if total == 0 else f"{count / total * 100:.2f}%"
            class_rows.append([split, name, count, pct])

    buoy_seq_rows = []
    for split in SPLITS:
        for stats in sorted(components_by_split[split], key=lambda s: -s["buoy_images"]):
            if stats["buoy_images"] > 0:
                buoy_seq_rows.append([split, stats["component_id"], stats["images"], stats["buoy_images"]])

    audit_status = "PASS — nessuna sequenza divisa tra split" if not violations else "FAIL"
    lines = [
        "# Report split sequence-safe",
        "",
        f"- Sorgenti: {', '.join(f'`{p}`' for p in source_roots)}",
        f"- Output: `{output_root}`",
        f"- Ratio target: train={args.train_ratio}, val={args.val_ratio}, test={args.test_ratio}",
        f"- Seed: {args.seed}",
        "",
        "## Audit leakage (obbligatorio)",
        "",
        f"**{audit_status}**",
        "",
    ]
    if violations:
        lines.append("Sequenze divise (BUG — non dovrebbe mai succedere per costruzione):")
        for seq, splits in violations.items():
            lines.append(f"- `{seq}`: {sorted(splits)}")
        lines.append("")

    lines += [
        "## Conteggi per split",
        "",
        table(["Split", "Immagini", "Oggetti", "Sequenze"], split_rows),
        "",
        "## Distribuzione classi",
        "",
        table(["Split", "Classe", "Oggetti", "%"], class_rows),
        "",
        "## Distribuzione boe per sequenza (attenzione: dati scarsi)",
        "",
        "Il dataset attuale ha poche sequenze con boe. Una stratificazione a "
        "livello di sequenza (corretta, qui applicata) puo' comunque produrre "
        "uno split con zero o pochissime boe in un dato split, semplicemente "
        "perche' non ci sono abbastanza sequenze-boe da distribuire in modo "
        "equilibrato. Questo NON e' un bug dello script: e' il problema di "
        "scarsita' dati gia' osservato nei tentativi EASY-v2/v2.1 (recall boe "
        "collassato a 0.00). Controllare questa tabella prima di allenare.",
        "",
        table(["Split", "Sequenza", "Immagini", "Immagini con boe"], buoy_seq_rows) if buoy_seq_rows else "_Nessuna sequenza con boe trovata._",
        "",
    ]
    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    source_roots = [Path(p) for p in args.source_root]
    output_root = Path(args.output_root)
    report_path = Path(args.report) if args.report else output_root / "split_report.md"

    pinned = {}
    if args.pinned_assignments:
        with open(args.pinned_assignments) as fh:
            pinned = yaml.safe_load(fh) or {}

    items = collect_items(source_roots, args.seaships_block_size)
    if not items:
        raise SystemExit(f"Nessuna immagine trovata sotto {source_roots}")

    components = merge_duplicate_sequences(items)
    components_stats = {cid: sequence_stats(cid, its) for cid, its in components.items()}

    unknown_pinned = sorted(set(pinned) - set(components_stats))
    if unknown_pinned:
        raise SystemExit(f"Sequenze pinnate non trovate nel dataset: {unknown_pinned}")

    assignment = stratified_assign(
        components_stats, pinned, args.train_ratio, args.val_ratio, args.test_ratio, args.seed,
    )

    violations = audit_no_cross_split_leakage(assignment, components)
    if violations:
        raise RuntimeError(f"Leakage strutturale rilevato (non dovrebbe essere possibile): {violations}")

    items_by_split = {s: [] for s in SPLITS}
    components_by_split = {s: [] for s in SPLITS}
    for component_id, comp_items in components.items():
        split = assignment[component_id]
        items_by_split[split].extend(comp_items)
        components_by_split[split].append(components_stats[component_id])

    reset_output(output_root, args.overwrite)
    write_dataset(items_by_split, output_root)

    report = render_report(output_root, source_roots, items_by_split, components_by_split, assignment, violations, args)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    build_summary = {
        "source_roots": [str(p) for p in source_roots],
        "output_root": str(output_root),
        "seed": args.seed,
        "ratios": {"train": args.train_ratio, "val": args.val_ratio, "test": args.test_ratio},
        "pinned_assignments": pinned,
        "assignment": assignment,
        "leakage_audit": "PASS" if not violations else "FAIL",
        "counts": {s: len(items_by_split[s]) for s in SPLITS},
    }
    (output_root / "build_summary.json").write_text(json.dumps(build_summary, indent=2), encoding="utf-8")

    print(f"Leakage audit: {'PASS' if not violations else 'FAIL'}")
    for s in SPLITS:
        print(f"{s}: {len(items_by_split[s])} immagini, {len(components_by_split[s])} sequenze")
    print(f"Report: {report_path}")
    print(f"Dataset: {output_root}")


if __name__ == "__main__":
    main()
