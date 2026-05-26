# Research 15-angles triage — 2026-05-24

**Source**: user-pasted synthesis of 15 candidate research angles to unlock multi-hop reasoning
and continual learning on the substrate.

**Triage author**: orchestrator main thread (post-compaction, post-pause-clear).

**Cap_map context at triage time**: v181; Bet B at 73% retention (needs 80% threshold);
multi-hop cliff at d~50 (Cap 11/12 zone); Cap-13 candidates F-4 Clifford-TN and
F-14 Tropical-margin KILLED 2026-05-24 batched cycle 202.

---

## Tier-1 (top three — substantial leverage, P>=0.40, target Tier-1-adjacent gaps)

### A1. State Space Models (SSM / S4 / HiPPO) — multi-hop depth extension
- **Target gap**: multi-hop cliff past d=50 (Cap 11/12 zone)
- **Mechanism**: HiPPO operator yields O(1) decay of past-context contribution per layer; stacked S4 layers extend effective context length without per-step binding-algebra rebinding
- **Predicted contribution**: depth extension d>50 without binding-algebra changes
- **Cost**: ~1 week full port; smoke at N=4096 single-layer = ~45 min CPU
- **First-probe**: 100-line single-channel S4 cleanup layer on synthetic chained-cleanup task at N=4096; smoke whether depth extends past current cliff
- **P (substrate-novel synthesis)**: 0.45 (after [[feedback-lit-scan-calibration-penalty]] deflation)
- **Status**: NOT in current queue; not in current experiments/ dir

### A2. Mixture of Experts (MoE) for cross-talk reduction
- **Target gap**: cross-talk-bounded capabilities (multiple Tier-1 gaps; capacity ceiling at N=4096)
- **Mechanism**: K expert sub-matrices selected by gating; effectively partitions the binding space; cross-talk scales sublinearly in expert count instead of M_stored
- **Predicted contribution**: linear capacity multiplier on expert-count for cross-talk-bounded caps
- **Cost**: ~30-60 min CPU for smoke (split Kerdock codebook into K=4 expert sub-matrices via key-modulus gating, measure cross-talk at fixed M_stored)
- **P**: 0.50
- **Status**: NOT in current queue; could share infrastructure with Wave 14 Kerdock experiments

### A3. Self-supervised concept discovery (SimCLR/BYOL/DINO style) to replace PPMI
- **Target gap**: PPMI is brittle; substrate-internal atoms could be discovered from data
- **Mechanism**: contrastive loss between augmented views of byte n-grams; substrate-internal representations as positives, random as negatives
- **Predicted contribution**: discovered atoms better than PPMI for downstream binding/cleanup
- **Cost**: ~60 min CPU for smoke at N=4096, byte n-gram pairs
- **P**: 0.40
- **Status**: NOT in current queue

---

## Tier-2 (secondary — worth queuing, P>=0.35)

### B1. EWC / Synaptic Intelligence / MAS for Bet B retention
- **Target gap**: Bet B is at 73%, threshold 80%, Tier-1 KILLER status
- **Mechanism**: Fisher-information-diagonal weighting on Phase-A loss; W updates during Phase-B/C are penalized in directions important for Phase-A retention
- **Predicted contribution**: 5-15pp lift over random-replay baseline (Kirkpatrick 2017 published margin)
- **Cost**: ~45 min CPU for smoke (Fisher-diagonal on W after Phase-A; quadratic penalty during Phase-B/C)
- **P**: 0.55
- **Tractability**: HIGHEST — well-published, smallest delta from existing Bet B scaffolding (exp_wave14d_betB_kovacs_v1.py)
- **Status**: NOT in current queue
- **TRIAGE DECISION**: First probe (see below)

### B2. Hypernetworks / fast weights (Schlag-Irie)
- **Target gap**: was on v1 list, skipped; could rebrand W as a function of context rather than static accumulator
- **Mechanism**: a small net produces per-context W updates; fast-weights formulation maps to substrate as time-varying outer products
- **Cost**: ~60-90 min CPU smoke
- **P**: 0.35

### B3. MPS / tensor network substrate (Wave 9 never built)
- **Target gap**: Cap-13 candidate space; F-4 Clifford-TN was just KILLED 2026-05-24, but MPS bond-dim >1 is RESCUE-ADJACENT
- **Mechanism**: bond-dim-D MPS as substrate; magic content tunable via bond truncation
- **Cost**: ~2-3 hr CPU smoke at small bond dim
- **P**: 0.35 (deflated since the Clifford-TN parent just KILLED; TN-rescue narrow)

### B4. RBM / Boltzmann framing for substrate uncertainty
- **Target gap**: Cap 8 uncertainty quantification; not in current queue
- **Mechanism**: free-energy-style scoring of substrate states; gives calibrated confidence
- **Cost**: ~90 min CPU smoke
- **P**: 0.30

---

## Tier-3 (closure-adjacent — skip unless explicitly requested)

- **R13/14/15 advanced math axis** (finite-dim, type-I, 1D trivialization): user-flagged as closed
  for shipping capability. Theoretical drilling continues only in non-load-bearing background.
- **Substrate-physics convergence** (R23 + R26 + R29 + R16): coherent framework now;
  a fifth confirming angle is low marginal value.

---

## First-probe sequencing decision

Per [[feedback-rescue-sketch-first-sequencing]] (cheapest tractable first) and the orchestrator's
job to keep CPU/GPU busy:

| Candidate | ETA | P | Novelty | Tractability | First-probe? |
|---|---|---|---|---|---|
| **B1 EWC for Bet B** | **~45 min CPU** | **0.55** | Mod (well-pub'd) | **HIGH** (smallest delta) | **YES** |
| A2 MoE smoke | 30-60 min CPU | 0.50 | High | Med | secondary |
| A1 S4 toy port | 45 min CPU | 0.45 | High | Med | secondary |
| A3 contrastive PPMI | 60 min CPU | 0.40 | High | Med-low | secondary |

**Decision**: ship B1 EWC as the first probe; queue A2 MoE + A1 S4 + (A3 contrastive OR B2 fast-weights)
as secondaries for pipeline depth.

---

## Honest reading: rescue probes or new capabilities?

- **B1 EWC**: pure rescue for existing Bet B row (cap_map B). If passes, lifts row from 73%→>80%; NOT a 13th capability.
- **A1 SSM/S4**: if it works, this is a substrate-augmentation pattern (new mechanism plugged into existing substrate). Could justify a 13th capability ("auditable depth extension via state-space dynamics") IF the cleanup task shows d>50 at acceptable cross-talk.
- **A2 MoE**: capacity-multiplier on EXISTING caps; lifts ceiling but is not a new capability class. Rescue/lift, not new row.
- **A3 contrastive concept discovery**: would replace PPMI (an existing component); lift not new row.

**Verdict**: 1 of 4 (A1 SSM/S4) is a plausible 13th-capability candidate IF the cleanup-depth probe
clears the cliff. The other three are rescue/lift probes for existing rows.

This is honest per [[feedback-no-smoke]]: I am not claiming 4 new capabilities; I am claiming
1 plausible-new-row + 3 rescue/lift probes. The user's framing ("primarily rescue probes") is
substantially correct.

---

## Blockers / caveats

- A2 MoE depends on stable Kerdock codebook; recent wave14_kerdock_batched_vamp_gpu_n4096_v1
  is in flight or completed — check before MoE smoke runs (gating function should not collide
  with Kerdock symmetry orbits).
- A1 S4 requires complex64 dtype care (HiPPO matrices are complex); substrate convention is
  complex64 for FHRR but float32 for BSC. Smoke should pick the substrate intentionally.
- B1 EWC: Fisher-diagonal on outer-product W is unusual (W is not a gradient-descent parameter
  in standard sense); need to compute Fisher as `E[(d log p / d W_ij)^2]` over Phase-A retrieval
  samples. Smoke should validate Fisher-diagonal scaling before scaling up.

---

## Ship outcome — 2026-05-24 (orchestrator main, full autonomy)

Smokes run locally (3 of 4 candidates had scripts already on disk; 4th — A3 contrastive
PPMI — has no script and is deferred):

| Candidate | Smoke verdict | Decision |
|---|---|---|
| B1 EWC (wave14e_betB_ewc_smoke_v1) | BET_B_EWC_PASS (retA=0.856 at lam=0.01 @ N=512) | SHIP full N=4096 to remote_cpu_queue |
| A2 MoE (wave14e_moe_xtalk_smoke_v1) | MOE_PASS (ratio 1.44 at M=2000 K=4 @ N=512) | SHIP full N=4096 to overnight_queue GPU |
| A1 S4 (wave14e_s4_depth_smoke_v1) | **S4_KILLED at smoke** | **HOLD — script needs redesign**: chain task uses closed-form XOR cleanup so binding-only achieves perfect recovery (depth_at_half=50/50); SSM cannot extend what is already at infinity. Mechanism premise broken at task level. Fix requires noisy chain or vocab-cleanup variant. Defer to next cycle. Per [[feedback-no-smoke]] do NOT ship a script with a known mechanism bug. |
| B1' EWC parallel (wave15_ewc_betB_smoke_v1) | EWC_INCONCLUSIVE at smoke (smoke baseline already saturated at 0.987) | SHIP full N=4096 to remote_cpu_queue — independent EWC implementation for cross-validation |

**3 anchors shipped, all VERIFIED on remote queue.json**:

| # | Anchor | Queue | ETA | Verified |
|---|---|---|---|---|
| 1 | wave14e_betB_ewc_smoke_v1 | remote_cpu_queue | 45-90 min | running |
| 2 | wave14e_moe_xtalk_smoke_v1 | overnight_queue (GPU) | 30-60 min | pending |
| 3 | wave15_ewc_betB_smoke_v1 | remote_cpu_queue | 60-90 min | pending |

**Mix**: 2 CPU + 1 GPU. Honest read: both EWC variants test the SAME hypothesis from
different scaffolding; if both PASS, Bet B rehab is robust; if one PASSes and the
other doesn't, mechanism is implementation-sensitive (informative-negative).

**Honest reading**: this ship attacks the rescue/lift gaps (Bet B retention + cross-talk
ceiling), NOT a 13th capability candidate. The 13th-cap candidate from the 15 angles
(A1 SSM/S4 for multi-hop) was identified but its smoke killed at the mechanism level;
needs a fix before it can land as a 13th-cap probe. Per [[feedback-no-smoke]]
substrate-novel framings of the other 3 angles (A2/B1/B1') are rescue/lift only.

**Post-ship queue state** (verified on remote queue.json at 11:41):
- remote_cpu_queue: 2 pending+running (incl. my 2 new EWC anchors)
- overnight_queue: 2 pending+running (1 was already there from earlier; my MoE is #2)
- local_cpu_queue: 0 (runner dead per `notes/orchestrator_post_compaction_brief.md` § project_cpu_resource_underutilized)

**Blockers**: none for the shipped anchors. The S4 redesign is a separate work item;
filing as a future exp_dev dispatch.

**Next-cycle handoff**:
- When EWC anchors land, verdict_handler should compose retention_A across both
  implementations to call Bet B rehab signal
- MoE verdict feeds candidate 13th-cap "MoE-partitioned binding" if it PASSes
- S4 redesign: chain task needs noise or vocab-cleanup variant; current XOR-only chain
  is a closed-form invertible operation
