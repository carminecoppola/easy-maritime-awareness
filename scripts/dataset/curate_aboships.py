#!/usr/bin/env python3
"""Cura il dataset ABOships (Zenodo 10.5281/zenodo.4736931, CC BY 4.0) nel
formato piatto atteso da scripts/dataset/build_sequence_safe_split.py
(images/ + labels/, stem "aboships__<YYYYMMDD>_<nome originale>").

Mappa di classi:
    boat, sailboat, motorboat, miscboat                        -> boat
    cargoship, cruiseship, ferry, militaryship, passengership   -> ship
    seamark                                                     -> buoy
    miscellaneous (200 istanze, ambigua)                        -> scartata

Uso:
    venv/bin/python scripts/dataset/curate_aboships.py \
        --zip data/external_sources/_staging_aboships/ABOshipsDataset.zip \
        --output-root data/external_sources/aboships_v1
"""

import argparse
import csv
import json
import zipfile
from collections import defaultdict
from pathlib import Path

CLASS_MAP = {
    "boat": "boat",
    "sailboat": "boat",
    "motorboat": "boat",
    "miscboat": "boat",
    "cargoship": "ship",
    "cruiseship": "ship",
    "ferry": "ship",
    "militaryship": "ship",
    "passengership": "ship",
    "seamark": "buoy",
}
DISCARDED_CLASSES = {"miscellaneous"}
EASY_CLASS_ID = {"boat": 0, "ship": 1, "buoy": 2}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--zip", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--csv-path-in-zip", default="ABOshipsDataset/Labels/Vesibussi_Labels.csv")
    p.add_argument("--images-prefix-in-zip", default="ABOshipsDataset/Seaships/")
    return p.parse_args()


def main():
    args = parse_args()
    output_root = Path(args.output_root)
    images_dir = output_root / "images"
    labels_dir = output_root / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.zip) as zf:
        names = zf.namelist()
        # Mappa: nome file originale (senza estensione) -> path completo nello
        # zip (che include la cartella data, es. ".../20180626/xxx.png").
        image_entries = {}
        for n in names:
            if not n.startswith(args.images_prefix_in_zip):
                continue
            if not (n.endswith(".png") or n.endswith(".jpg") or n.endswith(".jpeg")):
                continue
            stem_original = Path(n).stem
            date = Path(n).parent.name  # es. "20180626"
            image_entries[stem_original] = (n, date)

        with zf.open(args.csv_path_in_zip) as fh:
            reader = csv.DictReader(line.decode("utf-8") for line in fh)
            boxes_by_image = defaultdict(list)
            skipped_class = 0
            skipped_no_image = 0
            total_rows = 0
            for row in reader:
                total_rows += 1
                cls_raw = row["class"].strip().lower()
                if cls_raw in DISCARDED_CLASSES:
                    skipped_class += 1
                    continue
                easy_class = CLASS_MAP.get(cls_raw)
                if easy_class is None:
                    skipped_class += 1
                    continue
                stem = row["filename"].strip()
                if stem not in image_entries:
                    skipped_no_image += 1
                    continue
                boxes_by_image[stem].append((
                    EASY_CLASS_ID[easy_class],
                    int(row["xmin"]), int(row["xmax"]), int(row["ymin"]), int(row["ymax"]),
                ))

        # Import differito: PIL serve solo qui, per leggere le dimensioni
        # reali di ogni immagine (necessarie per normalizzare i box in
        # formato YOLO). La descrizione del dataset dichiara 720p per tutte
        # le immagini ma non ci si fida senza verificarlo file per file.
        from PIL import Image

        written_images = 0
        written_objects = 0
        sequence_image_count = defaultdict(int)

        for stem, boxes in sorted(boxes_by_image.items()):
            zpath, date = image_entries[stem]
            out_stem = f"aboships__{date}_{stem}"
            with zf.open(zpath) as src:
                data = src.read()
            image_path = images_dir / f"{out_stem}{Path(zpath).suffix}"
            image_path.write_bytes(data)

            with Image.open(image_path) as im:
                width, height = im.size

            lines = []
            for class_id, xmin, xmax, ymin, ymax in boxes:
                xmin_c, xmax_c = max(0, min(xmin, xmax)), min(width, max(xmin, xmax))
                ymin_c, ymax_c = max(0, min(ymin, ymax)), min(height, max(ymin, ymax))
                box_w, box_h = xmax_c - xmin_c, ymax_c - ymin_c
                if box_w <= 0 or box_h <= 0:
                    continue
                x_center = (xmin_c + xmax_c) / 2.0 / width
                y_center = (ymin_c + ymax_c) / 2.0 / height
                lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {box_w / width:.6f} {box_h / height:.6f}")
                written_objects += 1

            (labels_dir / f"{out_stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            written_images += 1
            sequence_image_count[date] += 1

    summary = {
        "source_zip": args.zip,
        "output_root": str(output_root),
        "total_csv_rows": total_rows,
        "rows_skipped_discarded_class": skipped_class,
        "rows_skipped_no_matching_image": skipped_no_image,
        "images_written": written_images,
        "objects_written": written_objects,
        "sequences": {f"aboships:{date}": count for date, count in sorted(sequence_image_count.items())},
        "class_map": CLASS_MAP,
        "discarded_classes": sorted(DISCARDED_CLASSES),
    }
    (output_root / "curation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
