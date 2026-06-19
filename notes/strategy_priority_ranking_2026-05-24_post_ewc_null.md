# Strategy priority ranking refresh — 2026-05-24 post-EWC-null

**Trigger**: User-delivered Research-grade analysis on the EWC null result from earlier in session. Filed verbatim below + Strategy translation into priority ranking + active_priorities update.

**Cap_map version**: v183.
**Decision log paired entry**: notes/strategy_decisions_2026-05-24.md Cycle 205.
**Active priorities update**: notes/active_priorities.md cycle 205.

---

## User-delivered analysis (verbatim)

> The EWC null is the most informative result in the batch, and it changes the priority ranking on the remaining items. EWC's failure is structural, not just empirical: both EWC arms inconclusive vs λ=0 says Fisher-weighted parameter-importance regularization provides zero traction on substrate retention. Per R26: substrate's W = Σ vᵢkᵢᵀ is maximally distributed; every fact contributes to every weight; no 'this parameter is critical' structure for EWC to exploit. Fisher matrix is approximately uniform.
>
> Practical implication: Bet B's 73% retention_A is not going to move via parameter-importance methods. EWC, MAS, SI, Path Integral all in this family — SKIP them. The 73% is the genuine retention level under random replay; methods exploiting non-uniform parameter importance cannot do better on this substrate by construction.
>
> What this means for MoE (still pending): MoE becomes HIGHER leverage after EWC fails. EWC + MoE attack same gap via opposite axes (parameter importance vs structural separation). EWC's failure says parameter-importance axis is empty; MoE works on orthogonal axis (structural separation), so its prior should go UP not down. If MoE shows even moderate Bet B lift when GPU lands, that confirms structural-separation is the live axis for retention.
>
> SSM/S4 task-design failure is recoverable. Smoke-killed-at-task-design is different from substrate-rejected. W·k iteration is mathematically S4-adjacent; failed smoke probably wrapped substrate in a task that did not exercise HiPPO-stable spectrum properly. Re-queue with: substrate W as state transition matrix, key as input, value as readout, standard copy-task or selective-copying benchmark.
>
> Tropical R2 closed-form match is a quiet big deal. 0.0e+0 match at N=4 means analytic prediction is exact. Rare in substrate-physics work (R16 free probability landed at 'within 20%'). Tropical R2 should jump to HIGH priority for substrate-scale validation.
>
> Updated priority ranking on remaining 12 of 15:
> 1. MoE GPU run (waiting): single highest-leverage active item
> 2. Tropical R2 substrate-scale test
> 3. SSM/S4 re-queue with corrected task
> 4. Self-supervised contrastive (once script lands)
> 5. F-6 Boolean re-queue with proper schema
> DEMOTE: EWC-family follow-ups (MAS, SI, Path Integral).
>
> NEW ABLATIONS unlocked by EWC failure:
> A. Per-task sub-substrate ablation: train 3 separate W matrices on Bet B's three corpora, concatenate at retrieval. If retention_A jumps to ~95%+, structural separation IS the load-bearing axis.
> B. Replay-only ablation at varying fractions: if random replay alone explains 73%, increasing replay fraction toward 1.0 should monotonically improve retention until cost dominates. If retention plateaus before 80% regardless of replay fraction, that bounds achievable retention without structural separation.

---

## Strategy translation

### Closed-deferred for Bet B retention work

**EWC family is OFFICIALLY CLOSED-DEFERRED**: EWC, MAS, SI, Path Integral. The EWC null is structural per R26 — substrate W = sum v_i k_i^T is maximally distributed; Fisher matrix is approximately uniform; parameter-importance regularization provides zero traction on substrate retention by construction. Bet B's 73% retention_A is the genuine retention level under random replay; methods exploiting non-uniform parameter importance cannot do better on this substrate by construction. DROP from queue. This is a substantive structural-closure framing (substrate property → method-family inapplicability), not a per-experiment empirical kill.

### Elevated to HIGH priority

1. **MoE GPU run** — single highest-leverage active item. Attacks Bet B retention via structural-separation axis ORTHOGONAL to EWC's parameter-importance axis. EWC's failure says parameter-importance axis is empty; MoE works on the orthogonal axis. Status: smoke PASSED at N=512 (ratio=1.44 at M=2000 K=4). GPU full attempt crashed at runtime (exit_code=1 in 2.4s). MUST FIX OR REBUILD.

2. **Tropical R2 substrate-scale validation** — 0.0e+0 closed-form analytic-match at N=4 is rare in substrate-physics work (R16 free probability landed within 20%). HIGH priority for substrate-scale test.

### New ablations added to ship queue

- **Ablation A — per-task sub-substrate**: train 3 separate W matrices on Bet B's three corpora, concatenate at retrieval. If retention_A jumps to ~95%+, structural separation IS the load-bearing axis. This is the structural-separation-axis falsifier for the EWC-null implication.
- **Ablation B — replay-only sweep at varying fractions**: if random replay alone explains 73%, increasing replay fraction toward 1.0 should monotonically improve retention until cost dominates. If retention plateaus before 80% regardless of replay fraction, that bounds achievable retention without structural separation.

### Demoted

EWC-family follow-ups (MAS, SI, Path Integral). DO NOT QUEUE.

### Full ranked list (12 remaining of 15)

1. **MoE GPU run (FIX REQUIRED)** — highest leverage; structural-separation axis.
2. **Tropical R2 substrate-scale test** — exact analytic match at N=4 is rare; HIGH.
3. **SSM/S4 re-queue with corrected task** — smoke-killed-at-task-design recoverable; substrate W as state transition matrix + standard copy-task / selective-copying benchmark.
4. **Self-supervised contrastive** (once script lands).
5. **F-6 Boolean re-queue** with proper schema.
6. **Ablation A** per-task sub-substrate (NEW).
7. **Ablation B** replay-only sweep (NEW).

DEMOTED / DO NOT SHIP: EWC, MAS, SI, Path Integral, any parameter-importance-regularization variant.

### Falsifier statements pre-registered

- **Ablation A**: HARD-PASS retention_A >= 95% with 3-corpus sub-substrate concatenation -> structural separation IS the load-bearing axis for Bet B retention.
- **Ablation A**: HARD-FAIL retention_A < 80% with 3-corpus sub-substrate concatenation -> structural separation NOT load-bearing.
- **Ablation B**: HARD-PASS monotone improvement in retention_A across replay fraction 0.1 -> 1.0 with peak >= 90% -> replay alone can close the gap; cost-vs-retention frontier is the design knob.
- **Ablation B**: HARD-FAIL retention_A plateaus < 80% across all replay fractions -> ceiling at ~73-80% bounded by structural property of the substrate; only structural-separation routes (e.g., MoE) can break this ceiling.

### Pipeline pacing

queue depth 0 across all three CPU queues at decision-time (GPU runner alive on amp_se_kerdock_longiter). Strategy refresh fires exp_dev queue-refill per [[feedback-pipeline-pacing]]. Pause flag CLEARED — ACTIVE — refill authorized.

### Discipline pointers

- per [[feedback-strategy-shore-up-capabilities]] proactive shore-up: Bet Z.5 🟢 promotion + Bet V 🟡 promotion + Cap 8 structural-closure annotation at v183 are direct shore-up moves on existing capabilities.
- per [[feedback-dont-overextend-theorems]] EWC null is interpreted at substrate-property layer (W = sum v_i k_i^T is maximally distributed), not at single-experiment layer.
- per [[feedback-rehabilitation-after-rejection]] EWC family closed with 2 rehab paths filed (Ablation A structural-separation; Ablation B replay-only sweep) BEFORE closing the EWC arm.
- per [[feedback-no-papers-product-only]] all framings are substrate-product; Bet B retention is a customer-facing capability; the EWC null narrows the design space but does not change the product framing.
- per [[feedback-no-smoke]] honest reading: 73% retention is the genuine ceiling under random replay on this substrate by structural argument; methods that exploit parameter-importance cannot improve it; methods that operate on structural-separation might.

