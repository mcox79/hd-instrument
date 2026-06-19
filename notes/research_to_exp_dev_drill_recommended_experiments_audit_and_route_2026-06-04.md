# Research -> Exp-Dev: Consolidated routing for drill-recommended experiments (audit + catch up)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Honest gap audit -- 6 drill-recommended experiments NOT yet routed. Consolidating + routing now. User flagged this gap.

---

## Why this note

User correctly noted: "I've seen a lot of recent experimental results with proposed next experiments that look very promising - are you also routing those to exp dev?"

Honest audit: I've been routing user-priority items (Tier 6 + Tier 4 + Stage A + Priority 1 compositions) but letting other drill recommendations accumulate. 6 experiments below have NOT been routed despite being drill-recommended.

Routing now. Each cell has explicit HP/MID/HF + cost estimate.

---

## Cell R1: 4-modulator hippocampal-tier rescue (Priority 1 from negatives drill; P=0.45)

**Source:** Negatives drill 2026-06-04 (research_drill_substrate_negative_results_structural_analysis_2x); identified as highest-P escape path for "single-modulator insufficient" structural limit.

**Anchor:** `substrate_4modulator_hippocampal_tier_rescue_v1_n4096`

### Architecture

Extend substrate with 4-modulator system (per bio-tier-scaling drill Tier 2 hippocampal-class):
- DA (dopamine analog): cf-RPE rank-1 substitution (already validated)
- ACh (acetylcholine analog): attention/focus modulator (boost writes for surprising patterns)
- NA (noradrenaline analog): arousal modulator (global gain control)
- 5HT (serotonin analog): mood/satiety modulator (capacity-management gate)

Each modulator gates writes independently. Combined: 4-modulator gating signal.

### Pre-reg

- HP: 4-modulator system >= 1.5x performance vs single-modulator (cf-RPE alone) at substrate-class task
- MID: 1.1-1.5x improvement
- HF: <= cf-RPE alone (multi-modulator adds noise without gain)

### Cost + wall

$0 CPU. ~30-60 min wall. 3 seeds. Engineering ~2-3h (extends Bundle A cf-RPE scaffold).

### Strategic significance

Tests **Tier 2 hippocampal-class transition** in bio-scaling ladder. If HP: substrate climbs one tier. If HF: substrate may be stuck at MB-class (Tier 1) without architectural change.

---

## Cell R2: Sparse resonator replication (Frady-Sommer arXiv:2404.19126; K=26 at N=5000)

**Source:** Negatives drill + earlier resonator capacity drill. Sparse resonator K=26 letters at N=5000 (published 2024 empirical).

**Anchor:** `substrate_sparse_resonator_replication_arxiv_2024_K26_v1_n5000`

### Architecture

Replicate sparse resonator at N=5000 with sparse codebook (f=0.02):
- K=26 factor recovery (letters of alphabet)
- Sparse vector representations + iterative coordinate-descent
- 50 iterations max
- 5 seeds

### Pre-reg

- HP: K=26 factor recovery >= 85% accuracy within 50 iterations (matches published)
- MID: 60-85% accuracy
- HF: < 60% (replication failure; check implementation against paper)

### Cost + wall

$0 CPU. ~30-60 min wall.

### Strategic significance

Extends substrate's Mode 4 resonator from dense (K=7-9) baseline to sparse (K=26+). Validates substrate's NC1 capability at substrate-class scale with published precedent.

---

## Cell R3: Bloom-substrate variant for SQ6 graph membership (architectural escape)

**Source:** Negatives drill structural analysis. SQ6 graph adjacency naive HF + SQ6-v2 cleanup HF revealed architectural gap: substrate handles RECOVERY but not MEMBERSHIP queries.

**Anchor:** `substrate_bloom_filter_variant_graph_membership_v1_n4096`

### Architecture

Bloom-filter-inspired substrate variant:
- Multiple hash functions (k=3-5) project graph edges to bipolar substrate
- Membership query: AND across all k hash positions
- Probabilistic membership; tunable false-positive rate

### Pre-reg

- HP: edge-membership accuracy >= 90% at E/N=0.5 with false-positive rate < 5%
- MID: 70-90% accuracy
- HF: < 70% (Bloom-substrate variant insufficient; architectural gap fundamental)

### Cost + wall

$0 CPU. ~20-30 min wall.

### Strategic significance

If HP: substrate has architectural primitive for membership queries via Bloom variant. Closes the SQ6 gap.
If HF: confirms structural gap; substrate's graph reasoning limited to recovery (factor decomposition).

---

## Cell R4: cf-RPE nonlinear-write for B5 fundamental escape

**Source:** Negatives drill. B5 replay-consolidation FUNDAMENTAL in additive-W mode (3 independent reasons). Cheapest escape: cf-RPE nonlinear write rule.

**Anchor:** `substrate_b5_nonlinear_cfrpe_replay_escape_v1_n2048`

### Architecture

Replace linear additive write with cf-RPE nonlinear write:
- W += eta * (target - predicted) * x^T (TD-error class)
- This introduces nonlinearity into update rule
- Test if replay-order benefit emerges

### Pre-reg

- HP: STDP-ordered replay > random replay by >= 1.3x retention at near-capacity (nonlinear write breaks commutativity)
- MID: 1.1-1.3x retention
- HF: <= 1.1x (cf-RPE nonlinear write insufficient to break commutativity at substrate-class scale)

### Cost + wall

$0 CPU. ~15-20 min wall.

### Strategic significance

If HP: substrate replay-consolidation rescuable via cf-RPE nonlinearity (4th independent test of B5 negative; rescued).
If HF: confirms B5 fundamental at substrate-class regardless of nonlinearity flavor; accept fully.

---

## Cell R5: B2 x B8 additive composition (D-RIP baseline sanity)

**Source:** D-RIP unification drill 2026-06-04 (research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x). Predicted ADDITIVE composition (same sparse axis).

**Anchor:** `substrate_b2_sparse_x_b8_logit_residual_additive_v1_n2048`

### Architecture

- B2 DG sparse-expansion (f=0.02) on patterns
- B8 logit-space sparse residual encoding on top
- Combined: double sparse projection
- Compare to B2 alone + B8 alone

### Pre-reg

- HP: combined capacity >= 90% of additive prediction (B2_gain + B8_gain)
- MID: 70-90% (sub-additive; partial composition)
- HF: < 70% (sparse-axis collinearity beyond D-RIP prediction)

### Cost + wall

$0 CPU. ~15-20 min wall.

### Strategic significance

Validates D-RIP unification framework's same-axis ADDITIVE prediction. Counterpart to cell R6 below.

---

## Cell R6: B2 x sparse-resonator super-additive composition (D-RIP orthogonal prediction)

**Source:** D-RIP unification drill. Predicted SUPER-ADDITIVE (sparse storage + sparse recovery are orthogonal axes per D-RIP).

**Anchor:** `substrate_b2_sparse_x_resonator_super_additive_v1_n4096`

### Architecture

- B2 DG sparse-expansion (f=0.02) for STORAGE
- Sparse resonator (per cell R2 above) for RECOVERY
- Tests: combined storage + recovery K_max

### Pre-reg

- HP: K_max >= 1.5x best-single-primitive (super-additive per D-RIP)
- MID: 1.0-1.5x
- HF: < 1.0x (sparse storage + sparse recovery collinear at substrate-class)

### Cost + wall

$0 CPU. ~20-30 min wall.

### Strategic significance

Direct empirical test of D-RIP framework's orthogonal-axis prediction. If HP: D-RIP unification empirically validated as composition predictor.

### Dependency

Depends on Cell R2 (sparse resonator replication) succeeding first; the resonator scaffold must work before composition test.

---

## Total budget for all 6 cells

- **CPU wall:** ~2.5-4h total
- **Engineering:** ~6-10h across all 6 (most reuse existing scaffolds)
- **Cost:** $0
- **No GPU dependency** (all CPU-friendly at substrate-class N=2048-5000)

---

## Priority order

**Highest expected information gain:**
1. **Cell R1: 4-modulator hippocampal-tier rescue** — tests Tier 2 transition; flagship architectural extension
2. **Cell R2: Sparse resonator replication** — validates substrate's Mode 4 NC1 capacity extension
3. **Cell R4: cf-RPE nonlinear B5 escape** — tests if B5 fully fundamental or rescuable
4. **Cell R3: Bloom-substrate SQ6 escape** — tests architectural gap closure
5. **Cell R6: B2 x resonator super-additive** — depends on R2; tests D-RIP unification empirically
6. **Cell R5: B2 x B8 additive** — D-RIP sanity check; lower urgency

---

## Honest acknowledgment

I should have routed these earlier. Today's heavy drill output (15+ drills + many empirical landings) generated a queue of recommended experiments that I let accumulate while focusing on user-priority items. Should be routing as drills land going forward.

Per [[feedback-no-padding-experiments]]: each cell discriminates a specific hypothesis from a specific drill recommendation. Not padding.

---

## Existing queue (for context; not new)

Already in Exp-Dev queue:
- Tier 6 Phase D (committed; CPU-feasible per earlier note)
- Tier 4 Hopfield-attention substitution (pending Pythia scaffold OR cloud)
- Stage A training-speed full at Shakespeare extctx-K=8
- 5 Priority 1 compositions (SQ2 x cf-RPE; SQ2 x Hierarchical; B6 x SQ2; Position-binding x B2; STDP x B2)
- EX-CONCEPT-1 REAL (pending Pythia extraction)
- EX-OPTION-C-W_proj (pending Llama v7)
- Capacity scaling N=4096/N=8192 (running)

Cells R1-R6 above are ADDITIONS, not replacements.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell tests distinct drill-recommended hypothesis
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU all 6 cells
- Per [[feedback-pressure-test-negative-findings]]: R1-R4 are escape-path tests for current negatives
- ASCII-only

PROT-018: `_r1_v1` through `_r6_v1` suffixes
PROT-021: source=local CPU + remote CPU, run_mode=smoke/full, n_seeds=3

---

**END.**

**Exp-Dev:** 6 drill-recommended experiments now routed. Total ~2.5-4h CPU + ~6-10h engineering across all 6. No GPU contention.

Priority order: R1 (4-modulator) → R2 (sparse resonator) → R4 (B5 nonlinear escape) → R3 (Bloom membership) → R6 (D-RIP super-additive; depends R2) → R5 (D-RIP additive sanity).

Build at your pace. When verdicts land: scorecard + composition matrix updated per system protocol.

**Research session:** going forward, will route drill recommendations as drills land (not let accumulate). Cadence continues.
