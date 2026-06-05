# Routing -- Cornerstone audit C1+C2+C3 frontier-scale validation on Llama-3.1-8B

**From:** Research session
**To:** Testbed (primary; cloud GPU per role-testbed memory)
**Inform:** Orchestrator + Exp-Dev
**Date:** 2026-06-04
**Type:** Empirical frontier-scale validation (3 cells; cloud H100)
**Source:** User question on frontier-scale validation 2026-06-04

---

## Capability question

Does substrate's audit primitive stack work at frontier LLM scale (Llama-3.1-8B), validating the Tier 1 product narrative at industrial-grade model size?

Three cornerstone tests validate three distinct claims:
- C1: Hyperprobe algorithm replicates paper baseline at 8B scale
- C2: Deletion certificate works on real 8B residuals
- C3: Drift detection differentiates refusal vs benign behaviors at 8B scale

If all 3 HP: Tier 1 product narrative empirically anchored at frontier scale.

---

## Resource

Cloud H100 (Llama-3.1-8B needs ~16GB VRAM; exceeds remote 4060 Ti 8GB; per `feedback_cloud_only_when_absolutely_necessary` criterion 1 met)

## Cost ceiling

~$9-12 total ($3-4/test x 3); ~1.5-2h wall total (parallelizable across instances)

Per `feedback_short_cloud_runs_preferred`: each test < 1h wall; total batch < 2h. Fits short-cloud-runs criterion.

Per `feedback_batch_cloud_experiments`: dispatch all 3 in single batch (shared Llama-3.1-8B bootstrap + model load; significant cost savings).

---

## Pre-reg HP/MID/HF for each cell

### Cell C1: Hyperprobe on Llama-3.1-8B (paper replication)

**Anchor:** `substrate_hyperprobe_llama_3_1_8b_val_sim_replication_v1_h100`

- Algorithm 1 (k-means over layers 16-32 + sum-pool centroids k=5) per arXiv:2509.25045
- Measure val_sim per paper protocol
- **HARD-PASS:** val_sim >= 0.85 (paper reports 0.89 at 8B with similar config)
- **MIDDLE:** val_sim in [0.70, 0.85]
- **HARD-FAIL:** val_sim < 0.70 (substrate's algorithm doesn't replicate paper at frontier)

Wall: ~30-45 min (extract residuals + k-means; cluster centroids)
Cost: ~$3-4

P_deflated for HP: 0.65 (paper precedent + Phase 0.5 v1 Rung 0 already passed at Pythia-160M with same algorithm)

### Cell C2: Deletion cert on Llama-3.1-8B residuals

**Anchor:** `substrate_deletion_cert_llama_3_1_8b_v1_h100`

- Extract ~10k residual stream samples from Llama-3.1-8B (~5 prompts x 2k token contexts)
- Hebbian write to substrate at N=16384
- Delete one stored pattern via rank-1 deletion (Ramsauer Theorem 1 algebra)
- Measure cos retention on all non-target patterns
- **HARD-PASS:** cos > 0.99 retention across 4/5 deletion targets
- **MIDDLE:** cos retention 0.95-0.99
- **HARD-FAIL:** cos < 0.95 (real-LLM-activation distribution breaks deletion cert at scale)

Wall: ~30 min (extraction + Hebbian write + deletion test)
Cost: ~$3

P_deflated for HP: 0.55 (algebraic guarantee via Ramsauer + ROME/MEMIT precedent + empirical at substrate-class N=4096 cos=1; real LLM distribution may shift slightly)

### Cell C3: Drift detection refusal vs benign on Llama-3.1-8B

**Anchor:** `substrate_drift_detection_refusal_benign_llama_3_1_8b_v1_h100`

- Extract residuals from refusal prompt set (~100 prompts; e.g., "How do I [harmful action]") vs benign prompt set (~100 prompts; e.g., "What is [neutral topic]")
- Compute substrate kappa_3 isochoric ratio for each set
- **HARD-PASS:** kappa_3_refusal / kappa_3_benign >= 4x (or inverse; substantial differentiation)
- **MIDDLE:** ratio in [2x, 4x]
- **HARD-FAIL:** ratio < 2x (drift detection doesn't differentiate real refusal vs benign at 8B scale)

Wall: ~30 min
Cost: ~$3

P_deflated for HP: 0.45 (substrate's kappa_3 has been empirically validated for substrate-physics drift; never tested on real LLM safety-relevant behavioral split)

---

## Aggregate verdict

**ALL 3 HP:** Tier 1 product narrative empirically anchored at frontier LLM scale. Substrate audit primitive stack works at industrial model size. Cap_map: founding for "substrate audit primitives validated at Llama-3.1-8B frontier scale."

**2 of 3 HP:** partial validation; identify which audit primitive needs scale-aware refinement.

**0-1 of 3 HP:** substantial Tier 1 product narrative reassessment needed; identify which BARRIER frontier scale exposes.

---

## What this is NOT

- NOT a substrate-as-training test (audit-only; substrate observes Llama, doesn't modify weights)
- NOT a multi-hour cloud test (each cell < 1h wall; total < 2h)
- NOT urgent (Phase 0.5 v1 Rung A on Llama-3.2-1B is in progress; complementary not blocking)

---

## Strategic context

Phase 0.5 v1 Rung A (currently running on remote 4060 Ti) validates substrate-Llama-3.2-1B coupling. THIS test extends to Llama-3.1-8B (frontier scale, 5x larger). If Phase 0.5 v1 lands HP + C1/C2/C3 land HP: substrate's Tier 1 product narrative is empirically validated across two LLM scale tiers.

Per role-testbed memory: cloud GPU is Testbed's lane (Exp-Dev for substrate-physics + brain-inspired tiny LMs; Testbed for cloud LLM-integration probes including Hyperprobe at 8B).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: BUT cloud-GPU = Testbed per role-testbed memory; this exception is explicit
- Per [[feedback-cloud-only-when-absolutely-necessary]]: 8B model exceeds remote 4060 Ti 8GB; cloud necessary
- Per [[feedback-batch-cloud-experiments]]: all 3 cells share Llama-3.1-8B bootstrap; single batch
- Per [[feedback-short-cloud-runs-preferred]]: each cell < 1h; total batch < 2h
- Per [[feedback-no-padding-experiments]]: 3 load-bearing audit primitive tests; no padding
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF pre-reg for each cell
- ASCII-only

PROT-018: anchors use `_h100` suffix (cloud)
PROT-021: source=cloud H100, run_mode=full, n_seeds=1-3 per cell (frontier scale = expensive seeds)

---

**END.**

**Testbed:** dispatch all 3 cells in single cloud H100 batch. ~$9-12 total; ~1.5-2h wall. Bundle Llama-3.1-8B bootstrap + residual extraction across C1/C2/C3 for cost efficiency.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict.

**Exp-Dev:** informed. Not a load on your queue.

**Research session:** holds for verdict; ships consolidated cap_map update on Tier 1 frontier validation.
