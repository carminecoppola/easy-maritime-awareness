# Project Overview

## Purpose

`EASY` (`Environmental Awareness by the Sea and beYond`) is a maritime perception project designed to build a reproducible foundation for RGB and thermal object understanding in marine scenes.

The current repository focuses on the **data pipeline layer** needed before training:
- source dataset selection
- taxonomy freezing
- controlled raw staging
- intermediate normalization
- YOLO export preparation
- HPC-safe orchestration
- validation of dataset readiness

## Current Status

Current state of implementation:
- canonical taxonomy is frozen
- official source datasets are selected
- lightweight staging utilities exist
- SMD parsing and controlled staging are implemented
- partial YOLO export from staged SMD data is implemented
- full EASY-v0 merge is not yet complete
- official baseline training has not yet started

## Official Scope Right Now

Mandatory current scope:
- maritime object detection dataset preparation
- RGB-first pipeline with thermal companion support
- reproducible storage and staging policy
- compatibility with HPC execution and later embedded deployment

Not yet in active operational scope:
- production training campaigns
- segmentation-first workflows
- tracking-first workflows
- full multimodal fusion
- embedded deployment packaging

## Roadmap Direction

Near-term direction:
1. finish controlled staging of official datasets
2. convert official sources into normalized intermediate records
3. export stable YOLO-ready subsets
4. validate merged EASY-v0 structure
5. start baseline training only after dataset readiness is confirmed

## Repository Interpretation

This repository should be read primarily as:
- a **dataset engineering repository**
- a **policy and orchestration repository**
- a **pre-training preparation repository**

It should not currently be interpreted as a finished benchmark release or a completed training pipeline.

## Repository Boundary

This repository now intentionally excludes non-core AI surfaces such as training, inference, and visualization.
Those concerns are downstream of dataset readiness and are not part of the active working tree anymore.
