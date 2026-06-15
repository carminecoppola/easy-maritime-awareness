# Model Artifact Policy

`models/` is the local workspace for reusable model files. Its contents are intentionally ignored by Git, except this policy file.

Canonical local layout:

```text
models/
├── pretrained/   # downloaded base weights, e.g. yolov8n.pt, yolov8s.pt
├── checkpoints/  # optional manually curated checkpoints
└── exported/     # optional exported inference formats
```

Training runs must not place reusable `.pt` files in the repository root.

Current rule:
- put pretrained weights in `models/pretrained/`
- keep run-specific YOLO weights in `outputs/runs/<experiment>/<run>/weights/`
- keep exported deployment artifacts in `models/exported/` only when explicitly needed

