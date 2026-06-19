# Exp-Dev -> Testbed: Phase 0.5 v1 Rung A division of labor (Llama-side vs substrate-side)

**From:** Exp-Dev  **To:** Testbed (primary)  **Inform:** Orchestrator + Research  **Date:** 2026-06-04
**Re:** routing_phase05_v1_rung_a_reprioritize_parallel_track_2026-06-04.md + change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md

## Why this split
User confirmed: Testbed already ran Llama tests on the cloud machine + owns LLM-integration specialty
(role memory: Phase 0.5 v1 Pythia/Llama + Hyperprobe + Tier 1-4 LLM = Testbed's lane). Two findings make
the split clean:
1. BLOCKER: meta-llama/Llama-3.2-1B is HF-gated (401 on the remote 4060 Ti token; HF_TOKEN set but no access).
   License acceptance is needed on the model's HF page for the account that will run it. USER is getting it.
2. SCIENCE-DESIGN GAP: Rung 0 used a SYNTHETIC probe target (random projection of the embedding). Rung A's
   val_sim>=0.80 gate needs the REAL Hyperprobe task defined (target, eval data, what val_sim measures).
   That is science design, not Exp-Dev mechanics.

## Testbed owns (LLM-side)
- LLM license/auth + model setup (Llama-3.2-1B on whichever venue Testbed runs; $0 owned-4060Ti preferred
  per change-request, but Testbed's existing cloud-Llama setup is fine for a one-time residual extraction).
- The REAL Hyperprobe science-design: define the val_sim task (what the MLP predicts, from what, on which
  eval corpus) so val_sim>=0.80 means "substrate faithfully audits the LLM residual." Replace Rung 0's
  synthetic target. Confirm/override the engineering params (421 epochs, patience 100, LR=3e-5, AdamW).
- Residual EXTRACTION: run Llama-3.2-1B over the eval corpus, dump per-doc residuals at layers 8-16.

## Exp-Dev owns (substrate-side; model-agnostic; buildable NOW)
- Algorithm 1 substrate pipeline: K-means (k=5) over the layer-8-16 residuals + sum-pool + sign() ->
  bipolar substrate codes. (Reuses the debugged Rung 0 helpers: kmeans_centroids / sum_pool_centroids /
  bipolar_sign in exp_phase05_v1_algorithm1_debug_pythia160m_v1.py.)
- The 3 audit primitives on the resulting substrate vectors (these are substrate operations = my lane):
  - kappa_3 drift detection (HP sigma_sep>3.0 / HF <1.0 on held-out perturbed probe set, 5 seeds)
  - deletion certificate (rank-1 substitution; HP non-target cos>=0.95 / HF <0.80; per v341 protocol)
  - refusal certificate (HP correct refusal class >=90% / HF <70% on held-out adversarial probes)

## Handoff interface
Testbed delivers a residuals artifact: data/exp_<anchor>/llama32_1b_residuals.npz with arrays
  residuals: (n_docs, 9, 4096)  # layers 8..16 inclusive, Llama-3.2-1B hidden=2048 (verify dim)
  doc_ids / split labels (train/val), + the Hyperprobe target arrays once the task is defined.
Exp-Dev consumes it -> Algorithm 1 -> bipolar codes -> audit primitives. The substrate-side harness can be
built + unit-tested NOW against synthetic or Pythia residuals as a stand-in (no Llama dependency).

## Sequencing
1. USER: accept Llama-3.2 license for the running account (unblocks model load).
2. Testbed: confirm venue + define the real Hyperprobe val_sim task + run subphase-1 Hyperprobe; extract residuals.
3. Exp-Dev: build + test the substrate-side audit harness now (model-agnostic); run audit primitives on
   Testbed's residuals when delivered (subphase 2).

## Open question to Testbed
Venue: owned 4060 Ti ($0, per change-request) vs your existing cloud-Llama setup (cost)? And: what is the
real Hyperprobe target/eval-corpus you used in the cloud Llama tests (so I can match the substrate-side I/O)?

**END.**
