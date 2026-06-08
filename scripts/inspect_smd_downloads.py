#!/usr/bin/env python3
"""
Inspect locally staged SMD visible downloads without bulk extraction.
"""

import argparse
import json
from collections import Counter
from pathlib import Path, PurePosixPath
import zipfile


EXPECTED_FILES = {
    "explanation_of_gt_files.pdf": "gt_description_pdf",
    "VIS_Onboard.zip": "visible_onboard_archive",
    "VIS_Onshore.rar": "visible_onshore_archive",
}


def normalize_sequence_stem(filename):
    name = PurePosixPath(filename).name
    for suffix in [
        "_HorizonGT.mat",
        "HorizonGT.mat",
        "_ObjectGT.mat",
        "_TrackGT.mat",
        ".avi",
    ]:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return PurePosixPath(filename).stem


def _collect_entries(paths, root_name):
    groups = {
        "Videos": set(),
        "HorizonGT": set(),
        "ObjectGT": set(),
        "TrackGT": set(),
    }
    entries = []

    for item in paths:
        path = PurePosixPath(item)
        if len(path.parts) < 3:
            continue
        if path.parts[0] != root_name:
            continue
        group = path.parts[1]
        if group not in groups:
            continue
        if str(path).endswith("/"):
            continue
        sequence_stem = normalize_sequence_stem(path.name)
        groups[group].add(sequence_stem)
        entries.append(
            {
                "path": str(path),
                "group": group,
                "sequence_stem": sequence_stem,
            }
        )

    return entries, groups


def build_archive_summary(entries, groups, archive_name, root_name):
    videos = groups["Videos"]
    sequences = []
    selected_members = []
    for stem in sorted(videos):
        member_paths = sorted(
            entry["path"]
            for entry in entries
            if entry["sequence_stem"] == stem and entry["group"] in {"Videos", "ObjectGT", "TrackGT", "HorizonGT"}
        )
        has_object_gt = stem in groups["ObjectGT"]
        sequences.append(
            {
                "sequence_stem": stem,
                "has_video": True,
                "has_horizon_gt": stem in groups["HorizonGT"],
                "has_object_gt": has_object_gt,
                "has_track_gt": stem in groups["TrackGT"],
                "member_paths": member_paths,
            }
        )
        if has_object_gt:
            selected_members.extend(member_paths)

    counts = Counter(entry["group"] for entry in entries)
    return {
        "archive_name": archive_name,
        "root_name": root_name,
        "entry_count": len(entries),
        "group_counts": dict(sorted(counts.items())),
        "video_sequence_count": len(videos),
        "object_gt_sequence_count": len(groups["ObjectGT"]),
        "track_gt_sequence_count": len(groups["TrackGT"]),
        "horizon_gt_sequence_count": len(groups["HorizonGT"]),
        "missing_vs_videos": {
            "HorizonGT": sorted(videos - groups["HorizonGT"]),
            "ObjectGT": sorted(videos - groups["ObjectGT"]),
            "TrackGT": sorted(videos - groups["TrackGT"]),
        },
        "object_ready_sequences": [
            sequence["sequence_stem"] for sequence in sequences if sequence["has_object_gt"]
        ],
        "object_ready_member_paths": sorted(selected_members),
        "sequences": sequences,
    }


def inspect_onboard_archive(archive_path):
    with zipfile.ZipFile(archive_path) as handle:
        names = handle.namelist()
        infos = {info.filename: info.file_size for info in handle.infolist() if not info.is_dir()}

    entries, groups = _collect_entries(names, "VIS_Onboard")
    summary = build_archive_summary(entries, groups, archive_path.name, "VIS_Onboard")
    summary["sample_entries"] = [
        {"path": entry["path"], "size_bytes": infos.get(entry["path"], 0)}
        for entry in entries[:20]
    ]
    return summary


def inspect_onshore_archive(archive_path):
    try:
        import rarfile
    except ImportError as exc:
        raise RuntimeError(
            "rarfile is required to inspect VIS_Onshore.rar without extraction. "
            "Install it with `python3 -m pip install --user rarfile`."
        ) from exc

    with rarfile.RarFile(archive_path) as handle:
        infos = handle.infolist()
        names = [info.filename for info in infos]
        sizes = {info.filename: info.file_size for info in infos}

    entries, groups = _collect_entries(names, "VIS_Onshore")
    summary = build_archive_summary(entries, groups, archive_path.name, "VIS_Onshore")
    summary["sample_entries"] = [
        {"path": entry["path"], "size_bytes": sizes.get(entry["path"], 0)}
        for entry in entries[:20]
    ]
    return summary


def inspect_downloads(downloads_dir):
    downloads_path = Path(downloads_dir)
    files = {}
    missing_files = []

    for filename, logical_name in EXPECTED_FILES.items():
        path = downloads_path / filename
        if path.exists():
            files[logical_name] = {
                "filename": filename,
                "path": str(path),
                "size_bytes": path.stat().st_size,
            }
        else:
            missing_files.append(filename)

    if missing_files:
        raise FileNotFoundError(
            "Missing expected SMD downloads: {}".format(", ".join(sorted(missing_files)))
        )

    onboard = inspect_onboard_archive(downloads_path / "VIS_Onboard.zip")
    onshore = inspect_onshore_archive(downloads_path / "VIS_Onshore.rar")

    extraction_candidates = {
        "onboard_object_ready_sequences": onboard["object_ready_sequences"],
        "onshore_object_ready_sequences": onshore["object_ready_sequences"],
    }

    return {
        "downloads_dir": str(downloads_path),
        "expected_files": files,
        "archives": {
            "visible_onboard": onboard,
            "visible_onshore": onshore,
        },
        "extraction_candidates": extraction_candidates,
        "notes": [
            "No extraction performed by this inspector.",
            "Object-ready sequences are the safe candidates for controlled downstream staging.",
            "MATLAB .mat inspection is intentionally deferred to the conversion phase.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect locally staged SMD visible downloads")
    parser.add_argument("--downloads-dir", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    report = inspect_downloads(args.downloads_dir)
    payload = json.dumps(report, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
        print(str(output_path))
        return

    print(payload)


if __name__ == "__main__":
    main()
