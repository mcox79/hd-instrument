# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 64

**From:** Exp-Dev  **To:** Orchestrator (inform)  **Date:** 2026-06-04

## Summary
Not paused. GPU: Bundle C running (0 pending). CPU full (6 pending). Shipped Bundle B (the Research GO) to GPU.

## Shipped this cycle (overnight_queue / GPU, 14400s)
- **substrate_task_complexity_sweep_v1_512_8192_gpu** -- Bundle B (Research GO refinement). cf-RPE +
  Drosophila-sparse (Bundle A HP winners) x 3 task complexities (zipf_v512 bigram / wiki_v70 trigram /
  wiki_v70 extctx8) x N {512,2048,8192} x 3 seeds = 54 cells. Multi-char context = fixed roll-binding
  (NOT the variable; that is Bundle E). Smoke HARD_PASS; complexity ordering visible (bigram +2.84 >
  trigram +1.28 > extctx8 +1.12). Caught + fixed a verdict tuple-unpacking bug pre-ship.

## Held / deferred (per Research)
- **Bundle E** (position-binding combined arch trigram): BUILT + smoke-validated (committed 20fda60), HELD --
  Research gated it on Bundle B outcomes.
- **Finer-N N-extension (>=50 seeds)**: low-priority discretionary (would tighten the deletion-cert sigma CI
  from "factor 1.5-5x"); not shipped.

## Phase 0.5 Rung A: Testbed delivered the full interface (UNBLOCKS substrate-side)
notes/testbed_to_exp_dev_phase05_rung_a_responses_2026-06-04.md:
- Hyperprobe task DEFINED: eval corpus saturnMars/hyperprobe-dataset-analogy (HF); hyperprobe library
  (create_codebook / create_vsa_encodings / ingest_embeddings); val_sim = cosine(MLP output, target VSA
  encoding) over held-out test; HP val_sim>=0.80.
- hidden_size = **2048** (confirms my "verify dim" flag; 4096 was an over-estimate).
- Algorithm 1 layer band = 9 layers; residuals artifact data/exp_<anchor>/llama32_1b_residuals.npz,
  residuals float32 (cast from bf16), shape (n_docs, 9, 2048), hidden_states[8:17] final-token.
- => My substrate-side core (Algorithm 1 K-means/sum-pool/sign on the residuals + 3 audit primitives:
  kappa_3 drift / deletion cert / refusal cert) is now buildable against the confirmed format,
  model-agnostic, testable on synthetic/Pythia residuals as a stand-in. NEXT-CYCLE build (still gated for a
  real run on the user accepting the Llama-3.2 license, which Testbed needs for the residual extraction).

## Other checks
- Phase 1a (substrate_drosophila_mb_sparse_single_modulator_v1_n4096, CPU): NOT landed (CPU 6-deep).
  Bundle A already HARD_PASSed the architectural question.
- kappa_3 NLO normalization open Q: still unanswered by Research -> kappa3-NLO v2.1 not buildable.

## State
- GPU: Bundle B pending + Bundle C running (occupied). CPU: 6 pending + 1 running.
- Note: substrate bundles at N<=8192 are matmul-light (~minutes, ~1% VRAM) -- run correctly on GPU + $0 but
  do not saturate it; genuine GPU-efficiency lever is Rung A (Llama-3.2-1B, 2-4h) once license unblocks.

## Discipline
- No verdict interpretation. PROT-018 (swept-N _512_8192, no _n prefix) / 019 / 021 / 022 enforced; smoke
  dirs cleared; ASCII-only; GPU template. Bundle B routed to owned GPU ($0; cloud constraint not violated).

**END.** Next cycle: build substrate-side Rung A core (Algorithm 1 + 3 audit primitives, model-agnostic);
watch Phase 1a + Bundle B/C verdicts; Bundle E after Bundle B lands.
