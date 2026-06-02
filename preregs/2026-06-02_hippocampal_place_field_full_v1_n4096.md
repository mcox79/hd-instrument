# Pre-registration: hippocampal_place_field_full_v1_n4096

**Date:** 2026-06-02
**Script:** experiments/exp_hippocampal_place_field_full_v1_n4096.py
**Queue:** remote_cpu_queue
**N:** 4096 (PROT-018 binding)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (cosine=0.879, spearman=0.879, acc=1.0000 at N=1024)

## Hypothesis

At N=4096 with K=204 place cells (alpha=0.05), the Hopfield substrate stores hippocampal-style place fields and supports:
- Cosine retrieval >= 0.85 (pattern fidelity)
- Spearman rho >= 0.70 (spatial gradient preserved)
- Bulk accuracy >= 0.90 (classification accuracy)

Full run (N=4096, K=204) vs v1 smoke (N=1024, K=50).

## Metrics

- `cosine`: cosine similarity of retrieved place field
- `spearman_rho`: Spearman correlation of retrieved spatial gradient
- `bulk_acc`: fraction of correctly classified place field activations

## Thresholds (pre-registered)

**HARD_PASS:** cosine >= 0.85 AND spearman_rho >= 0.70 AND bulk_acc >= 0.90
**HARD_FAIL:** cosine < 0.60 OR spearman_rho < 0.40 OR bulk_acc < 0.60
**MIDDLE_BAND:** above HF, below HP

## Timeout

300s (from: smoke ~30s at N=1024; N=4096 scales ~16x but alpha=0.05 kept constant; estimated 300s generous)
