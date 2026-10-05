# Contributing

Thank you for your interest in EASY. Issues and pull requests are welcome.

## Before you start

- Open an issue to discuss larger changes first.
- By contributing you agree that your contribution is released under the project's
  BSD 3-Clause License and that the copyright header of each file is kept.

## Ground rules for this repository

- **Never split data by image.** Use `scripts/dataset/build_sequence_safe_split.py`
  and keep its leakage audit; a leaky split silently inflates every metric.
- Do not change the frozen `EASY-v1-rgb3-buoy-rebalanced` dataset or its recorded
  metrics, and never cite its mAP50 0.942 as real performance.
- Report results with the sequence-safe split and, when relevant, the external MODD2
  benchmark. State clearly that the models are not validated for open water.
- Keep datasets, raw data and generated outputs out of git; version scripts, configs,
  reports and released model files only. New model files need an entry in
  `models/MODEL_CARD.md` and a checksum in `models/checksums.sha256`.
- Respect third-party terms: any dataset you add must keep its name, access
  conditions, licence and citation (see `THIRD_PARTY_NOTICES.md`).

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt            # dataset tooling and tests
pip install -r requirements-training.txt   # only for training/evaluation (Ultralytics)
python -m unittest discover -s tests -v
```

Write code in English, with a module docstring and a docstring on every function, and
keep the SPDX copyright header used in the existing files. Write commit
messages in the imperative mood and describe *what* changed and *why*.
