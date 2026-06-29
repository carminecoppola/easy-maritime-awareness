# Repository Final Cleanup Report

Generated: `2026-06-20T19:15:27`

## Summary

- Official active baseline: `EASY-v1-rgb3-buoy-rebalanced`.
- EASY-v2 and EASY-v2.1 material was archived as closed methodological experiments.
- Raw datasets were left untouched.
- EASY-v1 symlinks were repaired to the archived EASY-v0 fallback root.

## EASY-v1 Integrity

| Check | Before | After | Status |
| --- | --- | --- | --- |
| Image files/symlinks | 19323 | 19323 | PASS |
| Label files/symlinks | 10448 | 10448 | PASS |
| Broken symlinks | 20890 | 0 | PASS |
| Symlinks repaired | - | 20890 | INFO |

## Files Kept Active

| Path | Reason |
| --- | --- |
| data/processed/EASY-v1-rgb3-buoy-rebalanced | active EASY-v1 baseline/project file |
| outputs/experiments/easy_v1_buoy_rebalanced | active EASY-v1 baseline/project file |
| outputs/reports/easy_v1_test_evaluation.md | active EASY-v1 baseline/project file |
| outputs/reports/easy_v1_buoy_rebalanced_report.md | active EASY-v1 baseline/project file |
| outputs/reports/easy_dataset_iteration_closure.md | active EASY-v1 baseline/project file |
| docs/project_memory.md | active EASY-v1 baseline/project file |
| docs/EASY_PROJECT_CURRENT_STATE_AND_NEXT_STEPS.md | active EASY-v1 baseline/project file |
| README.md | active EASY-v1 baseline/project file |
| pyproject.toml | active EASY-v1 baseline/project file |
| requirements.txt | active EASY-v1 baseline/project file |
| .gitignore | active EASY-v1 baseline/project file |

## Files And Directories Archived

| Original Path | Archive Path | Reason |
| --- | --- | --- |
| data/processed/EASY-v2-candidate | archive/cleanup_20260620_repo_reset/datasets/EASY-v2-candidate | closed v2/v2.1 candidate dataset |
| data/processed/EASY-v2.1-candidate | archive/cleanup_20260620_repo_reset/datasets/EASY-v2.1-candidate | closed v2/v2.1 candidate dataset |
| outputs/experiments/easy_v2_yolov8n | archive/cleanup_20260620_repo_reset/experiments/easy_v2_yolov8n | closed v2/v2.1 training experiment |
| outputs/experiments/easy_v2_1_yolov8n | archive/cleanup_20260620_repo_reset/experiments/easy_v2_1_yolov8n | closed v2/v2.1 training experiment |
| outputs/galleries/easy_v2_buoy_failure | archive/cleanup_20260620_repo_reset/galleries/easy_v2_buoy_failure | closed v2 gallery |
| outputs/galleries/easy_v2_pretraining_review | archive/cleanup_20260620_repo_reset/galleries/easy_v2_pretraining_review | closed v2 gallery |
| outputs/logs | archive/cleanup_20260620_repo_reset/logs/logs | stale training logs |
| configs/dataset | archive/cleanup_20260620_repo_reset/configs/dataset | closed v2/v2.1 configuration |
| configs/training | archive/cleanup_20260620_repo_reset/configs/training | closed v2/v2.1 configuration |
| scripts/dataset | archive/cleanup_20260620_repo_reset/scripts/dataset | closed experiment utility scripts |
| scripts/evaluation | archive/cleanup_20260620_repo_reset/scripts/evaluation | closed experiment utility scripts |
| scripts/analysis | archive/cleanup_20260620_repo_reset/scripts/analysis | closed experiment utility scripts |
| scripts/slurm/train_easy_v2_yolov8n.sbatch | archive/cleanup_20260620_repo_reset/scripts/slurm/train_easy_v2_yolov8n.sbatch | closed v2/v2.1 sbatch |
| scripts/slurm/train_easy_v2_1_yolov8n.sbatch | archive/cleanup_20260620_repo_reset/scripts/slurm/train_easy_v2_1_yolov8n.sbatch | closed v2/v2.1 sbatch |
| src/training | archive/cleanup_20260620_repo_reset/src/training | closed training helper |
| docs/annotation_guidelines_boat_ship.md | archive/cleanup_20260620_repo_reset/docs/annotation_guidelines_boat_ship.md | closed taxonomy/v2 policy document |
| docs/dataset_rules | archive/cleanup_20260620_repo_reset/docs/dataset_rules | closed taxonomy/v2 policy document |
| outputs/reports/ambiguous_vessel_policy.md | archive/cleanup_20260620_repo_reset/reports/ambiguous_vessel_policy.md | intermediate or closed-branch report |
| outputs/reports/boat_annotation_review.md | archive/cleanup_20260620_repo_reset/reports/boat_annotation_review.md | intermediate or closed-branch report |
| outputs/reports/boat_forensics_report.md | archive/cleanup_20260620_repo_reset/reports/boat_forensics_report.md | intermediate or closed-branch report |
| outputs/reports/boat_hard_mining_report.md | archive/cleanup_20260620_repo_reset/reports/boat_hard_mining_report.md | intermediate or closed-branch report |
| outputs/reports/boat_improvement_ranking.md | archive/cleanup_20260620_repo_reset/reports/boat_improvement_ranking.md | intermediate or closed-branch report |
| outputs/reports/boat_root_cause_validation.md | archive/cleanup_20260620_repo_reset/reports/boat_root_cause_validation.md | intermediate or closed-branch report |
| outputs/reports/boat_ship_boundary_review.md | archive/cleanup_20260620_repo_reset/reports/boat_ship_boundary_review.md | intermediate or closed-branch report |
| outputs/reports/boat_ship_taxonomy_assessment.md | archive/cleanup_20260620_repo_reset/reports/boat_ship_taxonomy_assessment.md | intermediate or closed-branch report |
| outputs/reports/boat_targeted_augmentation_plan.md | archive/cleanup_20260620_repo_reset/reports/boat_targeted_augmentation_plan.md | intermediate or closed-branch report |
| outputs/reports/boundary_ambiguity_analysis.md | archive/cleanup_20260620_repo_reset/reports/boundary_ambiguity_analysis.md | intermediate or closed-branch report |
| outputs/reports/boundary_policy_recommendation.md | archive/cleanup_20260620_repo_reset/reports/boundary_policy_recommendation.md | intermediate or closed-branch report |
| outputs/reports/buoy_forensics_report.md | archive/cleanup_20260620_repo_reset/reports/buoy_forensics_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_1_evaluation_protocol.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_1_evaluation_protocol.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_1_experiment_plan.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_1_experiment_plan.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_1_readiness_check.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_1_readiness_check.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_1_test_evaluation.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_1_test_evaluation.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_1_vs_easy_v1.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_1_vs_easy_v1.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_2_taxonomy_refined_dataset_plan.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_2_taxonomy_refined_dataset_plan.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_2_training_readiness.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_2_training_readiness.md | intermediate or closed-branch report |
| outputs/reports/easy_v1_vs_easy_v0_comparison.md | archive/cleanup_20260620_repo_reset/reports/easy_v1_vs_easy_v0_comparison.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_build_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_build_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_buoy_split_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_buoy_split_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_pretraining_gate.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_pretraining_gate.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_rebuild_plan.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_rebuild_plan.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_split_constraints.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_split_constraints.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_test_evaluation.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_test_evaluation.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_val_evaluation.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_val_evaluation.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_1_vs_easy_v1_easy_v2_results.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_1_vs_easy_v1_easy_v2_results.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_audit_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_audit_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_build_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_build_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_builder_implementation_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_builder_implementation_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_buoy_collapse_root_cause.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_buoy_collapse_root_cause.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_buoy_decision_gate.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_buoy_decision_gate.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_buoy_distribution_analysis.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_buoy_distribution_analysis.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_buoy_sanity_check.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_buoy_sanity_check.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_buoy_source_group_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_buoy_source_group_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_dataset_builder_plan.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_dataset_builder_plan.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_dataset_design.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_dataset_design.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_pretraining_quality_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_pretraining_quality_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_repository_cleanup_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_repository_cleanup_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_sequence_safe_split_report.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_sequence_safe_split_report.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_success_criteria.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_success_criteria.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_test_evaluation.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_test_evaluation.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_training_readiness_decision.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_training_readiness_decision.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_val_evaluation.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_val_evaluation.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_vs_easy_v1_dataset_comparison.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_vs_easy_v1_dataset_comparison.md | intermediate or closed-branch report |
| outputs/reports/easy_v2_vs_easy_v1_results.md | archive/cleanup_20260620_repo_reset/reports/easy_v2_vs_easy_v1_results.md | intermediate or closed-branch report |
| outputs/reports/high_confidence_annotation_patch_report.md | archive/cleanup_20260620_repo_reset/reports/high_confidence_annotation_patch_report.md | intermediate or closed-branch report |
| outputs/reports/repository_cleanup_report.md | archive/cleanup_20260620_repo_reset/reports/repository_cleanup_report.md | intermediate or closed-branch report |
| outputs/reports/taxonomy_impact_analysis.md | archive/cleanup_20260620_repo_reset/reports/taxonomy_impact_analysis.md | intermediate or closed-branch report |

## Files And Directories Removed

| Path | Reason |
| --- | --- |
| yolo26n.pt | duplicate root model artifact; matching archive model: archive/models/yolo26n.pt |
| archive/easy_v1_legacy_backup/scripts/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/src/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/src/training/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/dotenv/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyparsing/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyparsing/ai/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyparsing/ai/show_best_practices/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyparsing/diagram/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyparsing/tools/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pygments/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pygments/filters/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pygments/formatters/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pygments/lexers/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pygments/styles/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyflakes/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyflakes/scripts/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pyflakes/test/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/_polars_runtime_32/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_core/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_core/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_core/tests/examples/cython/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_core/tests/examples/limited_api/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_pyinstaller/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_pyinstaller/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_typing/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/_utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/char/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/core/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/ctypeslib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/distutils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/distutils/command/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/distutils/fcompiler/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/distutils/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/doc/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/f2py/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/f2py/_backends/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/f2py/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/fft/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/fft/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/lib/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/linalg/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/linalg/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/ma/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/ma/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/matrixlib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/matrixlib/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/polynomial/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/polynomial/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/random/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/random/_examples/cffi/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/random/_examples/numba/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/random/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/random/tests/data/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/rec/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/strings/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/testing/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/testing/_private/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/testing/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/typing/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/typing/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/numpy/typing/tests/data/pass/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/cli/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/commands/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/distributions/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/index/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/locations/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/metadata/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/metadata/importlib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/models/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/network/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/operations/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/operations/build/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/operations/install/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/req/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/resolution/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/resolution/legacy/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/resolution/resolvelib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_internal/vcs/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/cachecontrol/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/cachecontrol/caches/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/certifi/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/distlib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/distro/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/idna/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/msgpack/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/packaging/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/packaging/licenses/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pkg_resources/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/platformdirs/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pygments/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pygments/filters/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pygments/formatters/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pygments/lexers/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pygments/styles/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pyproject_hooks/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/pyproject_hooks/_in_process/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/requests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/resolvelib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/resolvelib/resolvers/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/rich/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/tomli/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/tomli_w/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/truststore/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/urllib3/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/urllib3/contrib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/urllib3/contrib/emscripten/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/urllib3/http2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pip/_vendor/urllib3/util/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/packaging/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/packaging/licenses/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/wheel/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/wheel/_commands/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/webencodings/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pure_eval/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/ptyprocess/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/nccl/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/nccl/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/nccl/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cudnn/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cudnn/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cudnn/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cufile/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cufile/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cufile/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/nvtx/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/nvtx/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/nvtx/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/curand/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/curand/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/curand/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cufft/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cufft/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cufft/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_runtime/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_runtime/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_runtime/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_nvrtc/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_nvrtc/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_nvrtc/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_cupti/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_cupti/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cuda_cupti/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cublas/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cublas/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cublas/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cusparse/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cusparse/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cusparse/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cusolver/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cusolver/include/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/nvidia/cusolver/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mpmath/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mpmath/calculus/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mpmath/functions/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mpmath/libmp/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mpmath/matrices/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mpmath/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fastjsonschema/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/widgetsnbextension/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/websocket/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/websocket/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/webcolors/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/wcwidth/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/urllib3/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/urllib3/contrib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/urllib3/contrib/emscripten/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/urllib3/http2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/urllib3/util/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/uri_template/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Africa/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/America/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/America/Argentina/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/America/Indiana/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/America/Kentucky/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/America/North_Dakota/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Antarctica/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Arctic/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Asia/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Atlantic/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Australia/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Brazil/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Canada/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Chile/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Etc/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Europe/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Indian/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Mexico/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/Pacific/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tzdata/zoneinfo/US/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/tools/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/language/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/language/extra/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/language/extra/cuda/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/language/extra/hip/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/compiler/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/ops/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/ops/blocksparse/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/runtime/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/profiler/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/backends/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/backends/amd/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/triton/backends/nvidia/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/traitlets/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/traitlets/config/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/traitlets/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/traitlets/utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tqdm/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tqdm/contrib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tornado/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tornado/platform/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tornado/test/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/tinycss2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/_distutils_hack/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/soupsieve/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pluggy/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/markupsafe/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/approximation/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/approximation/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/assortativity/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/assortativity/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/bipartite/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/bipartite/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/centrality/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/centrality/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/coloring/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/coloring/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/community/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/community/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/components/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/components/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/connectivity/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/connectivity/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/flow/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/flow/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/isomorphism/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/isomorphism/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/link_analysis/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/link_analysis/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/minors/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/minors/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/operators/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/operators/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/shortest_paths/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/shortest_paths/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/traversal/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/traversal/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/tree/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/algorithms/tree/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/classes/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/classes/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/drawing/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/drawing/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/generators/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/generators/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/linalg/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/linalg/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/readwrite/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/readwrite/json_graph/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/readwrite/json_graph/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/readwrite/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/networkx/utils/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/send2trash/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/send2trash/mac/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/send2trash/win/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/rpds/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/auth/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/backend/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/backend/cffi/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/backend/cython/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/devices/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/eventloop/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/green/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/green/eventloop/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/log/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/ssh/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/sugar/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/tests/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/zmq/utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/_yaml/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/yaml/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pytokens/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pythonjsonlogger/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pycparser/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/psutil/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/prometheus_client/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/prometheus_client/aiohttp/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/prometheus_client/bridge/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/prometheus_client/django/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/prometheus_client/openmetrics/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/prometheus_client/twisted/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/platformdirs/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/PIL/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pexpect/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/_backends/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/_backends/hyperscan/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/_backends/re2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/_backends/simple/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/patterns/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/pathspec/patterns/gitignore/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/parso/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/parso/pgen2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/parso/python/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/overrides/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/jinja2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_arrow/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_compliant/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_dask/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_duckdb/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_ibis/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_interchange/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_pandas_like/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_polars/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_spark_like/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/_sql/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/stable/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/stable/v1/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/stable/v2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/testing/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/narwhals/testing/asserts/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mistune/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mistune/directives/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mistune/plugins/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/mistune/renderers/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/_backend/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/_extension/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/_internal/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/backend/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/compliance/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/datasets/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/functional/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/io/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/lib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/models/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/models/decoder/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/models/squim/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/models/wav2vec2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/models/wav2vec2/utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/pipelines/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/pipelines/_tts/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/pipelines/_wav2vec2/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/datasets/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/functional/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/models/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/pipelines/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/pipelines/_vggish/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/prototype/transforms/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/sox_effects/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/transforms/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/torchaudio/utils/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/loguru/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/lark/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/lark/__pyinstaller/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/lark/grammars/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/lark/parsers/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/lark/tools/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/kiwisolver/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/jupyterlab_widgets/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/jupyterlab_pygments/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/json5/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/isort/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/isort/_vendored/tomli/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/isort/stdlibs/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/iniconfig/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/idna/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/h11/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fsspec/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fsspec/implementations/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fsspec/tests/abstract/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fqdn/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/cffLib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/colorLib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/config/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/cu2qu/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/designspaceLib/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/diff/__pycache__ | generated Python cache |
| archive/easy_v1_legacy_backup/root/venv/lib/python3.11/site-packages/fontTools/encodings/__pycache__ | generated Python cache |

Additional removed paths omitted from table: `1594`.

## Space Impact

| Area | Size After Cleanup | Note |
| --- | ---: | --- |
| `data/processed` | 52G | Only EASY-v1 remains active. |
| `outputs/experiments` | 14M | Only EASY-v1 experiment remains active. |
| `outputs/reports` | 80K | Only curated final reports remain active. |
| `archive/cleanup_20260620_repo_reset` | 104G | Closed v2/v2.1 datasets, experiments, reports, galleries, and scripts preserved here. |
| Repository total | 372G | Reduced from approximately 527G before cleanup; raw datasets and legacy archive remain preserved. |

## Active Reports

| Report |
| --- |
| easy_dataset_iteration_closure.md |
| easy_v1_buoy_rebalanced_report.md |
| easy_v1_test_evaluation.md |
| repository_final_cleanup_report.md |

## Active Repository Structure

```text
.
./.agents
./.codex
./.git
./.git/branches
./.git/hooks
./.git/info
./.git/logs
./.git/objects
./.git/refs
./archive
./archive/cleanup_20260618
./archive/cleanup_20260620_repo_reset
./archive/configs
./archive/datasets
./archive/docs
./archive/easy_v1_legacy_backup
./archive/logs
./archive/models
./archive/outputs
./archive/reports
./archive/runs
./archive/scripts
./archive/src
./archive/tests
./configs
./configs/evaluation
./data
./data/backups
./data/interim
./data/processed
./data/raw
./docs
./docs/project_reports
./models
./models/pretrained
./outputs
./outputs/experiments
./outputs/reports
./scripts
./scripts/slurm
./scripts/training
./src
./src/analysis
./src/dataset
./src/evaluation
./src/utils
```

## Checksums Preserved Before Cleanup

| Path | SHA256 |
| --- | --- |
| outputs/reports/easy_v1_test_evaluation.md | 4aa71cf36489abb47b9add712a954864c3ac4c886e5e17214a611934aa347e44 |
| outputs/reports/easy_v1_buoy_rebalanced_report.md | 9d3af7f8402a4f5a6f8fdb101e6eee050efebb7c129295c779af341762f779d1 |
| outputs/reports/easy_dataset_iteration_closure.md | 4fec2646dc7be507d4b6fedc6a7aa353fa60760380cca5fae2c0acc694dd10df |
| outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt | 54fd66b5fc875637fb4976dcadd6e90d0c3343cd4e28ab33b49ba6060e36e861 |

## Remaining Risks

- None identified.

## Documentation Simplification Update

Active documentation was consolidated after cleanup. The canonical docs are now:

| Document | Purpose |
| --- | --- |
| `docs/DATASET.md` | Dataset schema, official baseline, dataset status, and future dataset rules. |
| `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` | EASY-v1 metrics, v2/v2.1 results, and scientific conclusion. |
| `docs/EXECUTION_PLAN.md` | Current phase, next action, and do-not-do rules. |

Older overlapping docs were moved to `archive/cleanup_20260620_repo_reset/docs/legacy_active_docs/`.

## Recommended Next Action

Use `EASY-v1-rgb3-buoy-rebalanced` as the final baseline for reporting/presentation. Do not restart EASY-v2 split iteration without genuinely new data.
