# Project Overview

## Purpose

EASY (`Environmental Awareness by the Sea and beYond`) is a maritime perception project. In the current cleaned repository state, the active focus is a single RGB baseline workflow built around the `balanced-v2` split.

## Current Active Scope

The repository now keeps only one operational dataset path:

- `data/processed/EASY-v0-rgb3-balanced-v2`

The active workflow includes:

- balanced-v2 baseline training
- balanced-v2 validation
- balanced-v2 report generation
- sequence-level analysis
- boat-vs-buoy error analysis

## Current Status

- the taxonomy remains frozen in `configs/dataset_schema.yaml`
- the repository surface has been reduced to the balanced-v2 RGB workflow
- superseded datasets, scripts, reports, and SLURM jobs have been archived locally
- the official notebook and markdown progress report remain available for review

## What Is No Longer Active

These are no longer part of the active repository workflow:

- `EASY-v0` as a canonical training dataset
- `EASY-v0-rgb3`
- `EASY-v0-rgb3-clean`
- `EASY-v0-rgb3-balanced`
- MassMIND as an active processed dataset path in this repo state

They may still exist in `archive/` for local recovery, but they are not part of the current operating surface.

## Operational Interpretation

This repository should now be read as:

- a cleaned balanced-v2 RGB baseline repository
- a lightweight training/evaluation repository
- a review-ready project snapshot for the current EASY phase

## Near-Term Direction

Near-term work should stay aligned with the balanced-v2 baseline:

1. maintain the active balanced-v2 dataset
2. rerun or extend the current YOLOv8n baseline when needed
3. use the current notebook/report for project communication
4. keep additional historical or experimental material out of the active repo surface
