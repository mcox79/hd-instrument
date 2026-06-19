# Research -> Exp-Dev: Decisions to UNBLOCK Tier 6 + Tier 4 + Stage A (substrate-intrinsic-LLM-training)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + Testbed
**Date:** 2026-06-04
**Subject:** User priority focus: Tier 6 Phase D + Tier 4 Hopfield-attention substitution + Stage A training-speed full run. All three currently blocked. Decisions below remove the blockers WITHOUT requiring new GPU/cloud authorization.

---

## Summary of decisions (3 cells)

| Cell | Current blocker | DECISION |
|---|---|---|
| Tier 6 Phase D | Llama v7 holds GPU + Wikitext loader broken | **Run on CPU; use Shakespeare char-LM corpus** |
| Tier 4 Hopfield-attention substitution | Needs Pythia scaffold + extraction | **Build scaffold using Pythia-160M (loads on runner); no extraction needed for substitution test** |
| Stage A training-speed full | Earlier crossover-N-sweep HF (no crossover at N=256-4096) | **Run on harder task: Shakespeare extctx-K=8 at N=8192 (matches Bundle B HP regime)** |

All three can build NOW without GPU + without new cloud authorization. User priority focus is addressed.

---

## Cell 1: Tier 6 Phase D on CPU + Shakespeare (UNBLOCKED)

**Anchor:** `substrate_tier6_phase_D_4layer_charLM_shakespeare_CPU_v1_n2048`

### Why this unblocks

- **GPU blocker irrelevant on CPU.** 4-layer char-LM at N=2048 + Shakespeare corpus (5MB) fits CPU comfortably.
- **Wikitext loader blocker irrelevant.** Shakespeare char-LM is your already-authorized fallback per earlier note.
- **No new authorization needed.** $0 CPU; reuses validated bio-primitive scaffolds.

### Reduced architecture for CPU feasibility

Use N=2048 (not N=4096) per substrate-class scaffold + 4 layers:
- Layer 1-4: substrate-Hebbian attention (W += K @ V^T; DG sparse f=0.02; position-binding; STDP-asymmetric; D-ECR eviction)
- NO cf-RPE (drill inverts for generative)
- Gradient-trained output head only
- Shakespeare char-LM corpus (~5MB)

### Wall + cost

- Wall: ~2-4h CPU (substantial but tractable on laptop)
- Cost: $0
- 3 seeds; total ~6-12h CPU
- Run alongside other CPU work; doesn't block GPU

### Pre-reg HP/MID/HF (same as original spec)

- HP: substrate-hybrid BPC <= 1.20x gradient-baseline AND wall-time <= 0.5x gradient-baseline AND audit primitives operational
- MID: BPC in [1.20, 2.0]x baseline OR wall-time speedup in [1.0x, 2x]
- HF: BPC > 2x baseline OR substrate-hybrid slower than gradient baseline

### What user authorized (none needed)

$0 CPU + Shakespeare corpus. No GPU contention with v7. Run when CPU bandwidth available.

---

## Cell 2: Tier 4 Hopfield-attention substitution at Pythia-160M (UNBLOCKED)

**Anchor:** `substrate_tier4_hopfield_attention_substitution_pythia160m_4layer_v1`

### Why this unblocks

- Pythia-160M LOADS on the runner (per your earlier algorithm1-debug run; gate-log confirmed).
- **Loading Pythia-160M is INDEPENDENT of residual extraction.** Tier 4 swap test doesn't need pre-extracted residuals; it modifies Pythia-160M architecture during a 500-step characterization run on Wikitext-2 char (or Shakespeare).
- Test is a FORWARD/BACKWARD PASS in modified Pythia-160M; no extraction pipeline needed.

### Reduced procedure

```
1. Load Pythia-160M architecture
2. Replace layer 8 attention with substrate-Hebbian-attention layer:
   - W += K @ V^T per token (substrate-Hebbian write)
   - softmax(Q @ W) retrieval (Ramsauer 2020 identity)
3. Initialize substrate W from frozen layer 8 attention weights (cold start) OR random (cleaner test)
4. Train 500 steps on Shakespeare char (or Wikitext-2 if loader fixed)
5. Measure: attention entropy at step 500; gradient norm variance ratio (substrate-layer vs other-layers)
```

### Wall + cost

- Wall: ~30-60 min remote 4060 Ti (Pythia-160M fits 8GB easily; substrate-attention W is ~16MB)
- Cost: $0 remote
- 3 seeds; total ~1.5-3h

### Pre-reg HP/MID/HF (per 2026-06-03 Drill 2)

- HP: substrate-layer attention entropy > 50% of baseline AND gradient variance ratio < 8x AND final perplexity within 1.5x baseline
- MID: entropy 25-50% OR gradient variance 8-15x
- HF: entropy collapse < 25% OR gradient variance > 15x

### Dependency

Remote 4060 Ti must be available. Llama v7 currently holds it. **If v7 must be killed: see USER ACTION below.**

If GPU contention forces it: can also run on cloud H100 ~$3-6 for 30-60 min wall. But $0 remote is preferred.

---

## Cell 3: Stage A training-speed FULL run at harder task (UNBLOCKED)

**Anchor:** `substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192`

### Why this unblocks

- Earlier crossover-N-sweep HF was at synthetic Zipf bigram (counting-optimal task; substrate has no value to add).
- **Shakespeare extended-context K=8 at N=8192 is in the EMPIRICALLY HP regime** (Bundle B task-complexity sweep HP cycle 67).
- Substrate's speed advantage emerges when the task requires more than counting (per drill: cf-RPE INVERTS for generative; one-shot Hebbian shines at hard tasks).

### Architecture

- Substrate with full validated trick stack (B2 DG sparse + position-binding + STDP + B6 D-ECR + B4 ensemble + B3a active gating + hierarchical aggregator)
- NO cf-RPE (per generative-LM drill)
- Train to target BPC on Shakespeare extctx-K=8 at N=8192
- Compare to Adam-trained char-LM transformer at matched task

### Pre-reg

- HP: substrate >= 3x wall-time speedup vs Adam baseline at matched BPC AND BPC within 20% of baseline
- MID: 1.5-3x speedup OR partial BPC
- HF: < 1.5x speedup (substrate provides no meaningful training-speed advantage at this scale; need to drill on WHY)

### Wall + cost

- CPU + remote 4060 Ti $0; ~1-2h wall total
- 3 seeds

### Why this finally tests the speedup claim

Earlier Stage A revised was at substrate-class N=512 with bigram. **Cell 3 here is at substrate's empirically validated K=8 extended-context regime (Bundle B HP).** This is where substrate's advantage should show empirically.

---

## Priority sequencing for Exp-Dev

**Build order:**

1. **Cell 1 (Tier 6 Phase D on CPU)** — start NOW; runs in background while other CPU work continues
2. **Cell 3 (Stage A FULL at Shakespeare extctx-K=8)** — start after Cell 1 has stable scaffold; reuses Cell 1's substrate-Hebbian + Shakespeare corpus
3. **Cell 2 (Tier 4 Pythia substitution)** — start when GPU free OR if user authorizes parallel cloud run

Total engineering: ~6-12h across all 3 cells. CPU-friendly first; GPU-required last.

---

## USER ACTIONS NEEDED

User asked: "tell me what I need to do."

### Required (gates the work)

1. **Confirm Llama v7 strategy** — currently stuck on GPU; blocks Cell 2 if not killed/fixed:
   - **Option A:** Kill v7 now; defer substrate-audit-core on Llama until later (Testbed can re-attempt extraction with diagnostic flags)
   - **Option B:** Wait for Testbed to diagnose v7 hang (might take hours; Cell 2 blocked)
   - **Option C:** Authorize cloud H100 for Cell 2 at ~$3-6 (parallel to v7; bypass GPU contention)
   - **Recommend Option A** — substrate-audit-core can wait; Tier 4 substitution is higher strategic priority for substrate-intrinsic-LLM-training narrative

2. **Confirm Pythia-160M extraction priority** — currently requested but blocked by Llama v7 GPU contention:
   - **Should Testbed run Pythia extraction NOW (independent of Llama hang)?** Pythia is much smaller + has loaded successfully before; faster + more reliable.
   - **Recommend YES** — unblocks EX-CONCEPT-1 REAL + Tier 4 (if v7 keeps GPU)

### Optional (lower-priority)

3. **Cell 1 + Cell 3 CPU build** — no authorization needed; Exp-Dev can start when CPU bandwidth permits. Just confirm direction is right.

4. **Stage A Shakespeare extctx-K=8 task choice** — confirm this is the right harder task. Alternatives: trigram V=512 (per Bundle B); Pythia-160M next-token prediction (intersects with Tier 4).

---

## What this gets us if all 3 land HP

**Substrate-intrinsic-LLM-training EMPIRICALLY VALIDATED at substrate's first frontier:**

- Cell 1 HP: substrate-hybrid 4-layer char-LM beats gradient-trained baseline on Shakespeare. THE first empirical validation of substrate-AS-PART-OF-LLM training.
- Cell 2 HP: substrate-Hebbian attention training-stable in Pythia-160M scaffold. Validates Tier 4 attention substitution at small-LLM scale.
- Cell 3 HP: substrate's training-speed advantage realized at empirically-validated K=8 regime (matches Bundle B HP).

**Combined: substrate's "vastly increase LLM training speed + intrinsic part of LLM" narrative gets its first empirical anchors.** This is the user's strategic focus.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator + Testbed informed
- Per [[feedback-cloud-only-when-absolutely-necessary]]: Cell 1 = CPU $0; Cell 2 = remote GPU $0 (or cheap cloud if needed); Cell 3 = CPU + remote GPU $0
- Per [[feedback-small-scale-first-methodology]]: all 3 at substrate's empirically-validated scale (N=2048-8192; Pythia-160M)
- Per [[feedback-no-padding-experiments]]: each cell tests distinct hypothesis
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- ASCII-only

PROT-018: anchors per cell above
PROT-021: source=local CPU + remote 4060 Ti, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** 3 cells now have CPU-feasible or remote-GPU-feasible paths. Cell 1 + Cell 3 can build on CPU without any GPU contention. Cell 2 needs GPU free (currently blocked by v7).

Priority build order: Cell 1 → Cell 3 → Cell 2 (when GPU free).

**Standing for user direction on the 4 user-action items above.**

**Research session:** standing for verdicts + negatives drill + ongoing pipeline. ~20 min cadence continues.
