#!/usr/bin/env python3
"""Tasso di falsi positivi di un modello EASY su immagini non marittime.
Ogni detection è per definizione un falso positivo.

Uso:
    venv/bin/python scripts/validation/false_positive_scan.py \
        --weights outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt \
        --images data/external_validation/non_maritime_fp_v1/images \
        --out outputs/reports/easy_v1_false_positive_scan.json
"""

import argparse
import json
import os
from datetime import datetime, timezone

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--conf", type=float, default=0.25,
                         help="soglia di confidenza (default: soglia operativa standard YOLO)")
    parser.add_argument("--low-conf", type=float, default=0.10,
                         help="soglia bassa aggiuntiva per vedere quanto e' 'vicino' il modello a sparare FP")
    return parser.parse_args()


def scan(weights_path, images_dir, conf, low_conf):
    model = YOLO(weights_path)
    names = model.names

    image_files = sorted(
        f for f in os.listdir(images_dir)
        if os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".png")
    )

    per_image = []
    total_detections_at_conf = 0
    total_detections_at_low_conf = 0
    images_with_fp_at_conf = 0
    images_with_fp_at_low_conf = 0
    per_class_fp_counts = {name: 0 for name in names.values()}

    for fname in image_files:
        path = os.path.join(images_dir, fname)
        result = model.predict(source=path, conf=low_conf, verbose=False)[0]

        boxes_low = []
        boxes_at_conf = 0
        for box in result.boxes:
            score = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = names[cls_id]
            boxes_low.append({"class": cls_name, "confidence": round(score, 4)})
            if score >= conf:
                boxes_at_conf += 1
                per_class_fp_counts[cls_name] += 1

        total_detections_at_low_conf += len(boxes_low)
        total_detections_at_conf += boxes_at_conf
        if boxes_at_conf > 0:
            images_with_fp_at_conf += 1
        if boxes_low:
            images_with_fp_at_low_conf += 1

        per_image.append({
            "image": fname,
            "detections_at_conf": boxes_at_conf,
            "detections_at_low_conf": len(boxes_low),
            "boxes_at_low_conf": boxes_low,
        })

    n = len(image_files)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "weights": weights_path,
        "images_dir": images_dir,
        "num_images": n,
        "conf_threshold": conf,
        "low_conf_threshold": low_conf,
        "summary": {
            "images_with_false_positive_at_conf": images_with_fp_at_conf,
            "false_positive_image_rate_at_conf": round(images_with_fp_at_conf / n, 4) if n else None,
            "total_false_positive_detections_at_conf": total_detections_at_conf,
            "images_with_any_detection_at_low_conf": images_with_fp_at_low_conf,
            "false_positive_image_rate_at_low_conf": round(images_with_fp_at_low_conf / n, 4) if n else None,
            "total_detections_at_low_conf": total_detections_at_low_conf,
            "per_class_false_positives_at_conf": per_class_fp_counts,
        },
        "per_image": per_image,
    }
    return report


def main():
    args = parse_args()
    report = scan(args.weights, args.images, args.conf, args.low_conf)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w") as handle:
        json.dump(report, handle, indent=2)

    s = report["summary"]
    print(f"Immagini testate: {report['num_images']}")
    print(f"Falsi positivi @ conf>={args.conf}: {s['images_with_false_positive_at_conf']} immagini "
          f"({s['false_positive_image_rate_at_conf']*100:.1f}%), "
          f"{s['total_false_positive_detections_at_conf']} box totali")
    print(f"Per classe: {s['per_class_false_positives_at_conf']}")
    print(f"Qualsiasi detection @ conf>={args.low_conf}: {s['images_with_any_detection_at_low_conf']} immagini "
          f"({s['false_positive_image_rate_at_low_conf']*100:.1f}%)")
    print(f"Report completo scritto in: {args.out}")


if __name__ == "__main__":
    main()
