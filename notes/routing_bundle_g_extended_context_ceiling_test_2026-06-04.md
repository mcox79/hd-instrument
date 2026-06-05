# Routing -- Bundle G extended-context ceiling test (substrate's TRUE task-complexity scaling)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical scaling test (new bundle; 6-9 cells; CPU + remote GPU)
**Source:** Empirical refutations of K* formula and position-binding K*=2.0 prediction; multiple 2x drills landed today identifying ceiling extension as priority

---

## Capability question

Given today's empirical refutations (K=8 extended-context HP at N=8192; K=3 trigram HP with position-binding + symmetric W at N=4096), what is substrate's TRUE empirical task-complexity ceiling?

Specifically: at what extended-context K does substrate-as-training-mechanism FINALLY fail with the strongest empirical-validated architecture (position-binding + symmetric Hebbian) at substrate-class N?

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_extended_context_ceiling_position_binding_symw_v1_n8192_16384`

Each cell tests position-binding + symmetric Hebbian (the empirically-minimal architecture per Cell E1 HP at trigram):

**Cells:**
- G1: K=8 extctx V=70 N=8192 (replicate task-complexity sweep HP; isolation control)
- G2: K=12 extctx V=70 N=8192 (extrapolation +50%)
- G3: K=16 extctx V=70 N=8192 (extrapolation +100%)
- G4: K=24 extctx V=70 N=8192 (extrapolation +200%)
- G5: K=16 extctx V=70 N=16384 (test if larger N raises ceiling)
- G6: K=16 extctx V=512 (synthetic) N=8192 (test if higher vocab lowers ceiling)
- G7: K=8 extctx V=4000 (real-vocab subword) N=16384 (real-vocab test)
- G8: K=8 real Shakespeare char-LM V=~70 N=8192 (REAL TASK test)
- G9: K=8 real Shakespeare char-LM V=~70 N=16384 (REAL TASK extended)

**HARD-PASS per cell:** BPC < uniform_baseline - 0.8 nats AND 3/3 seeds converge

**MIDDLE:** BPC < uniform_baseline - 0.3 nats (some learning)

**HARD-FAIL:** BPC >= uniform_baseline - 0.3 nats (no meaningful learning)

**Aggregate verdict:**
- TRUE_CEILING_LOW (K<10): if G2 HF or MID, ceiling is near K=8-10 at substrate-class scale
- TRUE_CEILING_MID (K=12-16): if G3 HP, G4 HF; expected per drill predictions
- TRUE_CEILING_HIGH (K>16): if G3 + G4 both HP; substrate has much more headroom than predicted
- ARCH_DEPENDENT: if G5 HP and G2 HF; ceiling scales with N
- VOCAB_DEPENDENT: if G6 HF and G2 HP; ceiling sensitive to V
- REAL_TASK_VALIDATED: if G8 + G9 HP; substrate competitive at REAL char-LM

## Resource

Local CPU primarily; remote GPU for higher-N cells (G5, G7, G9). N=16384 with position-binding may need GPU memory.

## Cost ceiling

$0 ($0 CPU + $0 remote GPU). Per-seed wall ~5-15 min depending on K + N. Total ~3-6 hours wall for full bundle.

## P_deflated (per today's methodology)

**P_algebraic = 0.55**: per true-scaling drill in flight; position-binding + symmetric W ceiling extends beyond K=8 by algebraic prediction

**P_implementation:**
- P_convergence = 0.70 (position-binding has clean convergence per E1 HP precedent)
- P_budget = 0.60 (N=8192-16384 fits substrate-class; cells at K>=16 may approach capacity)
- P_no_subsumption = 0.90 (W-modifying)
- P_task_match = 0.55 (extctx + char-LM are within substrate's empirically-validated domain)
- Joint P_implementation ~ 0.21

**P_joint = 0.55 * 0.21 ~ 0.12 for G3 HP (K=16)**

LOW per-cell P_joint but the bundle as a whole CHARACTERIZES the ceiling regardless of individual outcomes. Even all-HF tells us "ceiling at K<12 at substrate-class scale."

## Engineering scope

~4-6h:
- Extended-context task generator at K=8-24 (reuse Bundle B scaffold)
- Synthetic V=512 + V=4000 vocab variants (~1h)
- Shakespeare char-LM corpus + tokenization (~1h)
- Position-binding + symmetric Hebbian architecture (reuse Bundle E E1 scaffold)
- Eval harness for BPC + uniform baseline at varying K (~1h)
- Remote GPU dispatch for G5/G7/G9 (~1h)

Reuses Bundle A + Bundle B + Bundle E scaffolds substantially.

## Strategic outcome

### If G3 HP (K=16 extctx works at N=8192)

- Substrate's true ceiling is K>=16 with minimal architecture
- Position-binding enables LLM-class context length at substrate-class scale
- MAJOR product narrative upgrade: substrate-as-training-mechanism viable at real-task scale
- Cap_map: founding for "substrate task-complexity ceiling >= K=16 with position-binding + symmetric Hebbian"

### If G3 MID, G4 HF (K=12-16 borderline)

- Substrate's empirical ceiling characterized at substrate-class scale
- Architectural extensions (combined cf-RPE + STDP + sparse + Modern Hopfield p=4) may extend further
- Inform Bundle F priority + future ceiling extensions

### If all G2-G4 HF (K=8 was the actual ceiling)

- Today's task-complexity sweep HP was task-easy / vocab-favorable artifact
- True ceiling at substrate-class is K=8
- K* formula correction needed but in different direction

### If G8/G9 HP (Shakespeare char-LM)

- REAL-TASK validation; substrate-as-training competitive at small-scale char-LM
- Comparison to char-LM transformer baseline becomes relevant
- Flagship product narrative anchor

### If G8/G9 HF (Shakespeare char-LM)

- Real task structure breaks substrate's synthetic-Zipf performance
- Need architectural extensions for real natural language
- Inform: what's the gap between synthetic and real tasks?

---

## What this is (plain language)

Today's empirical results showed substrate works at extended-context K=8 at N=8192 (BPC gap > threshold; HARD_PASS). Today's drill predicted K* = log_V(alpha_c * N) + 1 = ~2.5 at V=70 N=4096 (K=8 should FAIL). The prediction was WRONG.

Bundle G tests the TRUE ceiling: where does substrate ACTUALLY stop working? Test K=8 (replicate), K=12, K=16, K=24 at N=8192 and N=16384. Plus test at higher vocab V=512 and V=4000. Plus REAL Shakespeare char-LM (most realistic test).

This characterizes substrate's empirical scaling law and validates whether substrate-as-training-mechanism is viable for real language modeling at substrate-class scale.

If K=16 works at N=8192: substrate is competitive with small char-LM transformers. Flagship product result.

If K=8 was the ceiling: today's HP was a synthetic-task artifact. Identifies real ceiling.

Either way: characterizes the TRUE substrate task-complexity ceiling that algebraic K* formula failed to predict.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-pressure-test-negative-findings]]: investigates empirical scaling beyond drill predictions
- Per [[feedback-no-padding-experiments]]: cells discriminate ceiling at multiple K + N + V
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU + remote GPU
- Per [[feedback-small-scale-first-methodology]]: substrate-class N=8192-16384
- ASCII-only

PROT-018: anchors use `_n8192_v1` / `_n16384_v1` suffix
PROT-021: source=local CPU + remote GPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** ~4-6h engineering + ~3-6h experiment wall total for 9 cells across K=8-24 + V=70-4000 + real Shakespeare. Verdict drives substrate's TRUE empirical scaling law characterization at substrate-class scale.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict; potential flagship if K=16+ HP or Shakespeare HP.

**Research session:** holds for verdict + true-scaling-law drill landing; ships consolidated cap_map update.
