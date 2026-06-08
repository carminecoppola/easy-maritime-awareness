"""
Helpers for reading Singapore Maritime Dataset MATLAB annotations.
"""

from pathlib import Path


SMD_CLASS_ALIASES = {
    "ferry": "ship",
    "vessel/ship": "ship",
    "vessel": "ship",
    "ship": "ship",
    "speed boat": "boat",
    "speedboat": "boat",
    "boat": "boat",
    "kayak": "boat",
    "sail boat": "boat",
    "sailboat": "boat",
    "swimming person": "swimmer",
    "person": "person",
    "swimmer": "swimmer",
    "buoy": "buoy",
    "other": "other",
    "flying bird/plane": "other",
}


def _lazy_load_scipy():
    try:
        import scipy.io
    except ImportError as exc:
        raise RuntimeError(
            "scipy is required to read SMD MATLAB annotations"
        ) from exc
    return scipy.io


def _to_python_scalar(value):
    try:
        import numpy as np
    except ImportError:
        np = None

    if np is not None and isinstance(value, np.ndarray):
        if value.size == 0:
            return None
        if value.size == 1:
            return _to_python_scalar(value.reshape(-1)[0])
        return [_to_python_scalar(item) for item in value.tolist()]

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore").strip()

    if isinstance(value, str):
        return value.strip()

    if hasattr(value, "item") and not isinstance(value, (int, float, str, bytes)):
        try:
            return _to_python_scalar(value.item())
        except Exception:
            return value

    return value


def normalize_smd_class_name(raw_class_name):
    cleaned = (_to_python_scalar(raw_class_name) or "").strip()
    if not cleaned:
        return ""
    return SMD_CLASS_ALIASES.get(cleaned.lower(), cleaned.lower())


def _normalize_rows(value):
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("numpy is required to normalize SMD arrays") from exc

    if value is None:
        return []

    if isinstance(value, np.ndarray):
        if value.size == 0:
            return []
        if value.ndim == 1:
            if value.shape[0] == 4 and value.dtype != object:
                return [value.astype(float).tolist()]
            return [[_to_python_scalar(item)] for item in value.tolist()]
        if value.ndim >= 2:
            return [[_to_python_scalar(item) for item in row] for row in value.tolist()]

    scalar = _to_python_scalar(value)
    if scalar is None:
        return []
    if isinstance(scalar, list):
        return [[item] if not isinstance(item, list) else item for item in scalar]
    return [[scalar]]


def _normalize_bbox_rows(bb_value):
    rows = _normalize_rows(bb_value)
    normalized = []
    for row in rows:
        if not row:
            continue
        if len(row) < 4:
            continue
        normalized.append([float(row[0]), float(row[1]), float(row[2]), float(row[3])])
    return normalized


def _normalize_label_rows(value, expected_count):
    rows = _normalize_rows(value)
    values = []
    for row in rows:
        if not row:
            values.append("")
        else:
            values.append(str(_to_python_scalar(row[0]) or "").strip())
    while len(values) < expected_count:
        values.append("")
    return values[:expected_count]


def load_smd_object_frames(mat_path):
    scipy_io = _lazy_load_scipy()
    payload = scipy_io.loadmat(str(mat_path), struct_as_record=False)
    struct_xml = payload["structXML"].reshape(-1)

    frames = []
    for frame_index, frame_struct in enumerate(struct_xml):
        bbox_rows = _normalize_bbox_rows(getattr(frame_struct, "BB", None))
        object_types = _normalize_label_rows(getattr(frame_struct, "ObjectType", None), len(bbox_rows))
        motion_types = _normalize_label_rows(getattr(frame_struct, "MotionType", None), len(bbox_rows))
        distance_types = _normalize_label_rows(getattr(frame_struct, "DistanceType", None), len(bbox_rows))
        object_codes = _normalize_label_rows(getattr(frame_struct, "Object", None), len(bbox_rows))
        motion_codes = _normalize_label_rows(getattr(frame_struct, "Motion", None), len(bbox_rows))
        distance_codes = _normalize_label_rows(getattr(frame_struct, "Distance", None), len(bbox_rows))

        objects = []
        for obj_index, bbox_xywh in enumerate(bbox_rows):
            raw_class = object_types[obj_index]
            normalized_class = normalize_smd_class_name(raw_class)
            objects.append(
                {
                    "source_object_index": obj_index,
                    "original_class": raw_class,
                    "normalized_class": normalized_class,
                    "bbox_xywh": bbox_xywh,
                    "bbox_xyxy": [
                        bbox_xywh[0],
                        bbox_xywh[1],
                        bbox_xywh[0] + bbox_xywh[2],
                        bbox_xywh[1] + bbox_xywh[3],
                    ],
                    "attributes": {
                        "source_object_code": object_codes[obj_index],
                        "source_motion_code": motion_codes[obj_index],
                        "source_motion_type": motion_types[obj_index],
                        "source_distance_code": distance_codes[obj_index],
                        "source_distance_type": distance_types[obj_index],
                    },
                }
            )

        frames.append(
            {
                "frame_index": frame_index,
                "objects": objects,
            }
        )

    return frames


def discover_smd_sequence_pairs(source_root):
    source_root = Path(source_root)
    candidates = []
    for view_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        object_dir = view_dir / "ObjectGT"
        video_dir = view_dir / "Videos"
        if not object_dir.exists() or not video_dir.exists():
            continue
        for mat_path in sorted(object_dir.glob("*_ObjectGT.mat")):
            sequence_stem = mat_path.name.replace("_ObjectGT.mat", "")
            video_path = video_dir / (sequence_stem + ".avi")
            if not video_path.exists():
                continue
            horizon_path = view_dir / "HorizonGT" / (sequence_stem + "_HorizonGT.mat")
            track_path = view_dir / "TrackGT" / (sequence_stem + "_TrackGT.mat")
            candidates.append(
                {
                    "view_name": view_dir.name,
                    "sequence_stem": sequence_stem,
                    "object_gt_path": mat_path,
                    "video_path": video_path,
                    "horizon_gt_path": horizon_path if horizon_path.exists() else None,
                    "track_gt_path": track_path if track_path.exists() else None,
                }
            )
    return candidates
