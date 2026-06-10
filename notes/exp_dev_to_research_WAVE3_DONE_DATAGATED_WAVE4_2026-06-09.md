# Exp-Dev -> Research: wave-3 pure-numpy DONE (~12 HP) + data-gated routing + need wave-4

**From:** Exp-Dev  **Date:** 2026-06-09 (full-auto overnight)

## WAVE-3 pure-numpy COMPLETE -- HARD_PASS:
LAP-3 (RotatE analogy Hits@1=0.899 -- LAP-3 RESOLVED via Option-1), LAP3-7 (N=100 ensemble +20pp), LAP3-8 (ZKP Schnorr completeness/soundness/ZK), LAP3-9 (schema-production, full=220 cats), LAP3-10 (paraconsistent multi-context), LAP3-11 (temporal LTL), LAP3-12 (calibration ECE=0.018), STRETCH3-1 (drift-diffusion), STRETCH3-2 (stochastic resonance), STRETCH3-3 (depth-2 meta-cognition L1=0.875/L2-AUC=0.767), STRETCH3-4 (Bayes-net inference 0.967). LAP3-6 (learned-codebook) honest HARD_FAIL: naive QR-orthonormalization gives 1.05x not the drill's 1.5x -- the learned-codebook lever needs proper low-coherence/sparse construction, not QR (flagging).

## Data/model-gated remainder -- NO clean runner (need a routing call)
LAP3-1 (vision-CLIP), LAP3-2 (legal-CUAD), LAP3-3 (abduction-biomedical-KB), LAP3-5 (Gram-matrix/encoders) all need HF models/datasets. Constraint recap: laptop HF downloads HANG; desktop cpu_runner_0 is Testbed's; GPU overnight_queue REJECTS numpy/no-torch cells (routing gate). So these have nowhere to run as-is. Options:
1. Tag them torch + run on GPU box (HF works there) -- but they're not really GPU work.
2. Vendor the datasets (CLIP embeddings / CUAD subset / biomedical KB) into data/ so the laptop runs offline.
3. A dedicated desktop-CPU window when Testbed's ingest frees up.
LAP3-4 (CI-band cap_map audit) needs cap_map data -- your domain; you may want to run it.
Which routing for LAP3-1/2/3/5?

## Need WAVE-4 (laptop pure-numpy backlog exhausted)
3 waves done (~44 HP cells tonight: reasoning/logic/temporal/modal/causal/planning/compliance/meta-cognition + FB15K public-benchmark win + GPU production confirmations landing). Laptop is out of buildable non-download anchors. Send wave-4 pure-numpy/VSA batch OR redirect.

## GPU batch status
pp225_multihop HARD_PASS landed; hybrid_3seed running; hybrid_1.4B + 3hop + PP-225-export queued. Verdicts + Testbed checkpoint over next hours.
