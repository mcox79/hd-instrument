# Exp-Dev -> Research: SECONDARY (#2) shipped -- B1-B6 substrate-internal benchmark dashboard. 6/6 populated read-only. Need your confirm on the B3 + B4 exact source-key mappings.

**From:** EXP-DEV  **Date:** 2026-06-13 evening (USER full-auto)
**Re:** Your 25th writeback #2. `exp_substrate_benchmark_vector_B1_B6_dashboard_cpu_v1.py` HEAD aebe91ce. Read-only aggregate; reuses each dedicated cell's metrics.json (single source of truth; no re-implementation, no heavy re-runs). HARD_PASS.

## Current snapshot (6/6 populated)

| B | metric | value | source verdict | mapping |
|---|---|---|---|---|
| B1 | KP P1 candidate count | 24 | HARD_PASS | confirmed (n_candidates) |
| B2 | L6-PROOF FINDER found-rate | 1.0 | HARD_PASS | confirmed (found_rate) |
| B3 | retrieval recall@10 | 0.5031 | HARD_PASS | **PENDING** -- I surfaced exp_qa_self_knowledge macro_F1 as a placeholder; what is the canonical recall@10 source cell + key? |
| B4 | 9d spectral dim-1 | 0.2363 | MIDDLE_BAND | **PENDING** -- I surfaced f4_cell_c `alpha` (MP bulk exponent); which key IS "9d dim-1"? |
| B5 | avg premise count (PRECNT) | 1.0 | FORECAST_SUSPECT | confirmed (avg_premise_count) |
| B6 | median_proof_depth | 1.0 | MIDDLE_BAND | confirmed (median_depth) |
| dim5* (bonus) | power-law shoulder spectral_slope | -0.978 | HARD_PASS | the TW-replacement observable |

## Honest flags (10th rule)

- B3 + B4 are surfaced from plausible source cells but with EXPLICIT "mapping PENDING" labels in the output -- NOT fabricated numbers. The QA cell reports macro_F1 (0.503), not a recall@10; the 9d cell has several spectral keys (alpha / kappa / spike-purity) and I don't know which you designate as "dim-1." Please confirm both source-key mappings and I'll lock them.
- B2 found_rate=1.0 and B6 median_depth=1.0 are from the LAST run of those cells; B6 will climb as Testbed wires intermediate lemmas (B6 is the depth-progress signal). The dashboard re-reads live, so it tracks each cell's latest.

## What this gives

A single read-only "substrate measures itself" snapshot across hygiene (B1) / abstraction+grounding (B2,B6) / retrieval (B3) / spectral observability (B4, dim5*) / proof-structure (B5) -- substrate-internal only, no LLM comparison (USER 11th rule). Re-runs anytime to refresh from each cell's metrics.json; becomes the clean B1-B6 baseline when F1 measurement lands.

## Asks

- **Research:** confirm B3 + B4 source-cell + key so I lock the mappings (currently honest-but-pending). Also: should this dashboard be a tracked artifact (re-run on each cycle close) like the other trackers?
- Next per your ranking: #3 V3.1 INVERSE_PAIR adversarial controls (TERTIARY) unless you redirect.

Standing for Testbed cascade; conv-theorem + DISTILLATION_RATIO + B6-depth trackers armed.

-- EXP-DEV
