# Strategy request to Experiment Dev — 2026-05-21 cycle 19 followup

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev (session 5)
**Topic**: Three research-unblocked bets ready to queue — explicit nudge

## What I'm asking

Queue three experiments that have been sitting research-unblocked while
the 2/cycle cadence has gone toward extending validated bets (A, C, G, H)
and probing the composition surface. User explicitly asked Strategy to
push these up.

All three are pre-blocking — Research has already landed the prerequisite
2× deep research notes. Strategy has the multi-probe success criteria
and kill criteria specified in `active_priorities.md`.

## The three experiments

### 1. `wave14d_multi_task_cl_v1` (Bet B, Tier-1 KILLER)

**Spec source**: `notes/research_R5_corpus_C_design_2026-05-21.md`
(landed 2026-05-21 10:21)

**Multi-probe success criteria** (per Bet B in active_priorities.md):
- Phase-A held-out bpc retention: ≥ 80% of baseline after C-phase
- Phase-B held-out bpc retention: ≥ 80% of baseline after C-phase
- Phase-C learn-curve: positive bpc gain vs untrained substrate
- 3 seeds minimum, all three retention floors hold
- BWT (backward transfer) at end-of-C: ≥ 0 (no catastrophic forgetting)

**Kill criterion**: any one of A/B retention drops below 50% of baseline
across 3 seeds.

**Why this matters**: closes one of the two remaining unresolved Tier-1
KILLER rows ("True continual learning at production scale"). The single-
shift continual learning capability is already ✅ (R7 replay mechanism);
multi-domain A→B→C→D would lift the Tier-1 score from 4/6 to 5/6 ✅.

### 2. `wave14r_multihop_FHRR_v1` + `wave14r_multihop_hybrid_v1` (R8 rehab, parallel pair)

**Spec source**: `notes/research_R8_chained_CAM_binding_algebras_2026-05-21.md`
(landed 2026-05-21 10:42, sections 2.3 + 2.4 + experiment design at 3.x)

**Multi-probe success criteria** (per R8 + Bet F-style multi-probe):
- char_entropy preserved at all hop depths up to 50
- acc_50hop ≥ 0.80 at NUM_FACTS=100 (depth-extension target)
- Both FHRR (A1, pure) and hybrid BSC-store+FHRR-chain (C1) tested
- 3 seeds minimum

**Kill criterion**: 0/2 candidates clear acc_50hop ≥ 0.80 at NUM_FACTS=100.

**Why this matters**: multi-hop reasoning is currently 🟡 PROVISIONAL with
depth cliff localized at d=25 (cap_map v23 from `wave14yp`). R8 identifies
FHRR as the mechanism correction (continuous-group binding avoids the
Walsh-XOR-closure pathology that killed the v17 Hadamard rescue). R8 also
flagged C1 as a NEW substrate-coherent variant Strategy missed. Test both
in parallel per the 2/cycle cadence.

**Important per [[feedback-rehabilitation-after-rejection]]**: cycle 7's
Hadamard cross-pollination prediction was falsified empirically
(`wave14z_multihop_hadamard_entities`). Pre-arm 5 axis-combination rescue
sketches in the prereg in case FHRR + hybrid both fail.

### 3. `wave14_ssh_bsc_v2_protected` (Bet F, Tier-2 substrate-physics)

**Spec source**: `notes/research_R10_SSH_BSC_topological_probe_2026-05-21.md`
(landed 2026-05-21 11:02)

**Multi-probe success criteria** (per Bet F in active_priorities.md):
- Categorical recovery rate vs noise level p: monotone decay with kink at
  p_c ≈ 1/(2·ν_density)
- Winding-number Z-quantization holds for p < p_c (integer-recovery
  probe — must include this, missing from original v1)
- Charge sweep q ∈ {2, 5, 10, 20}: empirical p_c scales 1/q matching
  Hasan-Kane prediction within 30%
- 3 seeds per (q, p) cell

**Kill criterion**: after R10's probe redesign, no sharp transition
observed across noise sweep OR Z-quantization fails for all p.

**Why this matters**: Bet F has been 🟡 NEEDS_REVIEW since 2026-05-20
13:32 — original probe didn't fire (`categorical_correct=0.0` at all p).
That was a methodology gap, not a substrate finding. R10 designs the
proper probe. If validated, integer winding-protected memories are a
substrate-unique product story.

**Important per PROT-004**: prereg must pre-arm 5 axis-combination rescue
sketches in case v2 also fails. The v1 NEEDS_REVIEW state has been static
22+ hours; closing or validating it is the goal of v2.

## Suggested queue order

Per [[feedback-two-experiments-per-cycle]] (continuous-pipeline cadence):

- Cycle A: queue Bet B + first multi-hop FHRR
- Cycle B: queue second multi-hop (C1 hybrid) + Bet F
- (Other cycles: continue smoke/composition work in parallel as bandwidth)

## What you need from me

Nothing — all three have spec source files. Multi-probe success criteria
+ kill criteria are in `active_priorities.md`. Just queue.

## Cross-references

- `notes/active_priorities.md` "🔝 TOP-PRIORITY QUEUE" section (just
  added this cycle)
- `notes/substrate_capability_map.md` v31 (incoming) notes the push
- This file (request log)
