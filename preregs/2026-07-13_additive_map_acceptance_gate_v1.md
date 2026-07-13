# Pre-reg: additive_map_acceptance_gate_v1 (AdditiveKGMap live-capability acceptance gate)

Date: 2026-07-13. Cell: `experiments/exp_additive_map_acceptance_gate_v1.py`.
Design source: `notes/research_additive_map_builder_integration_endgame_2026-07-13.md`.
Capability under test: `hdlab/additive_map.py::AdditiveKGMap` (Phase-1 promotion of the additive inductive map-builder).

## Purpose
Scaffold-free witness that fits the additive inductive map LIVE VIA THE CLASS on the CSKG held-out-ENTITY arena and
reproduces the VET-confirmed held-out-entity ANCHOR_COMPOSE MRR. The mechanism is driven ONLY through the class
(fit -> compose_into_table -> score); the ARENA helpers (split, filtered MRR) are imported verbatim from the
already-VET-confirmed cell `exp_anchor_compose_inductive_entity_cskg_v1` so the comparison is apples-to-apples.

## Reproduction target (MEASURED)
- VET mean ANCHOR_COMPOSE MRR = 0.12821
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE
  (verdict HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE, run_mode full, device cuda, seeds [7,13,17], elapsed 12073s).

## Pre-registered acceptance bands (picked BEFORE the run)
- PASS (`ACCEPTANCE_PASS_ADDITIVE_MAP_REPRODUCES_VET`): mean ANCHOR MRR over seeds [7,13,17] in [0.10, 0.16]
  (VET +/- ~0.02, device-float tolerance) AND fires_vs_random (anchor_mrr - random_mrr > 0) AND
  relation_signal_vs_scramble (anchor_mrr - scramble_mrr > 0) AND seed-7 fitted map round-trips save/load.
- FAIL (`ACCEPTANCE_FAIL`): any band unmet -> the live-wire reproduces the offline win only partially; investigate
  the representational-mismatch hazard (R1 in the design source).
- Reproduction is bit-faithful by construction: the class's LearnedSGDCoordinateSource calls the SAME fit_kge_anchor1
  with the SAME (k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, reciprocal, lr=A1_LR) on the SAME pinned
  build_ids index maps + SAME held-out split; only device-float summation order can drift the MRR.

## Arms (all zero-training from ONE class-driven additive fit per seed)
- ANCHOR: compose_into_table (mean_i X[h_i]+D[r_i]) -> direct-distance MRR (mechanism).
- SCRAMBLE: same bundle with support relation ids permuted (rng seed*4441+17) -> must-underperform ANCHOR.
- RANDOM: random X,D (rng seed*333+9, *0.1) + same readout -> null; ANCHOR must clear it.

## Persistence gate (the load-bearing promotion win)
Seed-7 fitted map persisted one-time to `data/exp_additive_map_acceptance_gate_v1/fitted_map_seed7/`
(coords.safetensors + index.json); reloaded and re-scored -> score_all must be identical (persist_reload_ok).

## Compute / discipline
- device=auto (cuda on GPU host; matches VET device), matmul-heavy minibatch-SGD fit (GPU-batching honored),
  neg-chunked; readout query-chunked; storage SHARDED. Seeds sequential, empty_cache between. Read-only w.r.t.
  KGStore (zero regression to CERT-584/585).
- Hardening: except SystemExit before except Exception (no bare/BaseException), start-marker, crash-diagnostic,
  heartbeat, atomic write_metrics, progress_logging print_flush_true, run_mode verified.
- Self-test (`--self-test`, CPU, class-driven planted arena) PASSED on .venv: anchor 0.4008 >> scramble 0.0964 >>
  random 0.0075, persist round-trip ok, 27s.

## Numbers (tagged)
- anchor MRR target 0.12821 MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json
- self-test anchor 0.4008 / scramble 0.0964 / random 0.0075 MEASURED@data/exp_additive_map_acceptance_gate_v1_selftest/metrics.json
- unit-test anchor 0.3846 / scramble 0.0234 / random 0.0140 MEASURED@verification/verify_additive_map_api.py (local run)
