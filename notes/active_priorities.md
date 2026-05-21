# Active priorities

Owner: Strategy session. Updated atomically; downstream sessions (Experiment
Dev, Research, Visibility, Queue Health, META) read this.

**Last updated:** 2026-05-21 cycle 7 (in-loop self-pacing)
**Cap map version this refers to:** v17

---

## Recently resolved (since cycle 1)

| Bet | Outcome | Trigger |
|---|---|---|
| Bet 1 — ICL saturation curve | ✅ VALIDATED. slope on log2(ICTX) = +0.14 at low/mid ICTX; soft-saturating to +0.05 at high ICTX (≤65536). Monotone positive through 16× substrate width. Tier-S #1 ICL gap closed; soft-saturation calibration noted in cap_map v15. | `wave14d_icl_via_pool_v3_scaling` full + `wave14w_icl_extended` full |
| Bet 2 — GDPR/surgical erase v3 (orthogonal-key path) | ✅ VALIDATED at M_stored/N ≤ 0.78. Hadamard subcode + anti-Hebbian rank-1 W edit passes all 5 Mirage probes. | `wave14r_erase_orthkeys_v1` + `wave14r_orthkeys_capsweep` |
| Bet 3 — Random-key iterative charge-flipping forensics | ❌ CLOSED (PROVISIONAL per cap_map v14 rehab discipline). improvement=+0.03 over SVD (target +0.2). Structured-key WHT-forensics ✅ remains. R7 routed for 2x deep research. | `wave14s_chargeflip_forensics_v1` |
| **Bet C — Full Kerdock + structured codebook for dense regime (M > N)** | ✅ VALIDATED at N=4096, M_stored up to 2N. Kerdock arm passes all 5 Mirage probes; correlated control reproduces Mirage. Extends Bet 2 from orthogonal-only (M ≤ N) to Welch-bound structured codebooks (M/N ≤ 2.0). | `wave14v_erase_kerdock_v2` smoke + full |

## Top capability bets v3 (in priority order; Bet C resolved this cycle)

### Bet A — Edit-then-query end-to-end pipeline (Tier-1 KILLER, now unblocked)

**Claim.** A user-uploaded correction propagates through the full
pipeline: pool entry removed AND W-side edit applied AND subsequent
queries reflect the correction. Two parallel candidate mechanisms per
R1 audit (cycle 6):
- **Primary**: AlphaEdit (ICLR 2025, arXiv:2410.02355) — published
  method scaling to 3000 sequential edits, operates on substrate's
  random keys without restructuring. 50-65% predicted Mirage-pass
  per R1 audit revision.
- **Parallel**: Kerdock 2A.i + structured codebook — already partial
  via Bet C ✅; would also unlock WHT-forensics + Kerdock cleanup
  speedup. 40-55% predicted.
Joint P(at least one passes) ~70-80%.

**Why now.** Bet 2 resolved the erase primitive. The remaining piece of
the Tier-1 KILLER edit-then-query is the integration: does a query
issued after edit_then_erase actually reflect the change in observable
behavior (cleanup output, predicted v, downstream-task accuracy)?
v8's `wave14d_query_side_integration` answered "no" with the pool-only
form (93% W-leak). The new orthogonal-key primitive should fix that.

**Multi-probe success criteria** (single-fact correction, K=8, M=200,
N=4096, Hadamard keys, α=1.0, 3 seeds):
- post-correction predict-correct on edited fact: ≥ 95% (vs pre-edit
  baseline predict-correct ~ same; argmax now reflects new v)
- post-correction predict-correct on 100 kept facts: ≥ 90% (no
  collateral damage)
- correction holds under paraphrase probes (Hamming h ∈ {2, 4, 8}):
  leak ≤ 5%
- correction holds under replay (re-train W with original (k_edit,
  v_original) NOT in the corpus): no regression
- W-only-readout test passes too (full pipeline, not just pool-side)

**Kill criterion.** Any single multi-probe fails over 3 seeds AND no
rescue variant (α tuning, M_stored slack, key-subspace orthogonalization)
closes the gap within 2 cycles. Then "edit-then-query" stays 🟢-partial
indefinitely and the Tier-1 KILLER claim downgrades.

**Who acts.** Experiment Dev (build TWO parallel experiments —
`wave14g_erase_alphaedit_v1` AND `wave14g_erase_kerdock_v1` — under the
new 2/cycle cadence; both test the full edit-then-query pipeline);
Strategy (cap_map upgrade on positive verdict from either or both).

---

### Bet B — Multi-task continual learning A → B → C → D (Tier-1 KILLER, still ⚪)

**Claim.** Substrate trained on Corpus A, then B (Phase B established
shift), then a *genuinely different* domain C (e.g., code, structured
data, hex) retains all three under random replay, with retention scoring
≥ 80% of single-task baseline on each held-out task.

**Why now.** Single-shift continual learning is at ✅ (R7 replay
mechanism). The Tier-1 KILLER claim is multi-domain. With Bet 1's ICL
characterization in hand, retention vs ICL gain is now separable: the
test is whether substrate W absorbs C-domain structure under replay
without erasing A or B.

**Multi-probe success criteria**:
- Phase-A held-out bpc retention: ≥ 80% of baseline after C-phase
- Phase-B held-out bpc retention: ≥ 80% of baseline after C-phase
- Phase-C learn-curve: positive bpc gain vs untrained substrate
- Multi-seed (3 seeds minimum), all three retention floors hold
- BWT (backward transfer) at end-of-C: ≥ 0 (no catastrophic forgetting)

**Kill criterion.** Any one of A/B retention drops below 50% of
baseline across 3 seeds. Replay-mechanism cap to single-shift confirmed.

**Who acts.** Research (design Corpus C: hex / Python / structured;
match information-content to A and B; see `wave14d_multi_task_cl_research.md`);
Experiment Dev (build `wave14d_multi_task_cl_v1`).

---

### Bet C — RESOLVED ✅ (see "Recently resolved" table above)

`wave14v_erase_kerdock_v2` full at N=4096 with M_stored ∈ {2000, 4096,
6144, 8192} → M/N up to 2.0. Kerdock arm passes all 5 Mirage probes;
correlated control reproduces Mirage. Higher-M behavior (M > 2N)
untested but not top-bet priority.

---

### Bet D — Generation K-curve analysis (Tier-1 KILLER partial → ✅?)

**Claim.** Strict-baseline generation quality is monotone in K up to
K=64 (or peaks at K=64-128 per R10 curve shape). Closes the "GPT-
quality generation with auditable memory" Tier-1 KILLER from 🟢 partial
to ✅.

**Why now.** `wave14d_generation_v2_K16` is already at ✅ (strict-
baseline). K=32 and K=64 metrics.json files exist (per v7
"COMPLETED_NEEDS_ANALYSIS"). All that's needed is an analyzer pass
comparing substrate_pool vs B3 Markov baseline at each K, then 3-seed
aggregation. No new experiments required; just metric analysis. Cheap.

**Multi-probe success criteria**:
- substrate_pool p1 > B3 Markov p1 at K=32 AND K=64, by ≥5pp (matches
  v2 K=16 PASS threshold)
- k4_validity > 0.40 at both K
- 3-seed monotone improvement K=16 → K=32 → K=64 (or peak within range)
- Per-position accuracy data lines up with v2 K=16 shape

**Kill criterion.** Either K=32 or K=64 fails the +5pp threshold OR
shows non-monotone collapse. Then generation Tier-1 KILLER stays
🟢-partial-at-K16-only.

**Who acts.** Experiment Dev (analyzer pass on existing metrics.json
files; could be a 30-min task, not a new experiment). Strategy
(cap_map upgrade on positive verdict).

---

## Recently retracted / closed

| Claim | Trigger | Lesson |
|---|---|---|
| Random-key iterative charge-flipping forensics (Bet 3) | `wave14s_chargeflip_forensics_v1`: +0.03 cos improvement (target +0.2) | Random-key forensics requires structured-key substrate; iterative refinement doesn't bridge the gap |
| Multi-hop reasoning 50+ hops viable claim | `wave14t_multihop_v3` (acc_1hop=0.93 < v2's 0.98) + `wave14u_multihop_envelope_v1` (acc_50hop=0 at NUM_FACTS=25) | wave14e v2 synthesis was optimistic; multi-hop bounded at low depth |
| (Prior cycle 1 list still applies — Yonelinas, anti-Hebbian on correlated keys, soft-trace cal, counterfactual=1.0, RSB tree-walk, LSH variants, K/N invariance) | (see cap_map v12) | — |

## Open research questions (routed to Research session)

- **R2**: Self-supervised concept discovery without PPMI — math survey
  beyond sparse_dictionary (blocked on Python-loop infra).
- **R3**: Compositional generalization test design — no clean held-out
  test specified yet.
- **R4 (modified)**: Multi-hop reasoning rescue — given v1+envelope show
  chains break at 50 hops at NUM_FACTS=25 but sustain to 40% at depth
  50 with NUM_FACTS=50, the envelope is more nuanced than v1 framing.
  **See R8 for full rehab routing.**
- **R5**: Corpus-C design for multi-task continual learning (Bet B).
- **R6**: Full Kerdock decoder implementation details (Bet C prerequisite).
- **R7 (NEW, rehab-routed, Bet 3)**: Iterative phase retrieval + sign
  recovery in random ±1 design matrices. 2x pass (broad survey then
  substrate drill). Strategy's 5 sketches in cap_map v14 (WH-sparsity,
  low-rank pre-project, K-sparse storage, hybrid CF+SVD, semi-supervised
  Sayre) are unvetted draft.
- **R8 (rehab-routed, multi-hop)**: Noise accumulation in chained
  content-addressable memory. 2x pass; substrate-compatible variants
  ranked by depth-50 accuracy extension at NUM_FACTS=100. Strategy's 6
  sketches in cap_map v14 unvetted draft. **Update (cycle 7)**: sketch #5
  (orthogonal-key allocation via Hadamard) empirically FAILED at
  substrate scale — Walsh group closes under XOR-bind, so multi-hop
  binds collide with stored Hadamard codewords. R8 priority reordered:
  drill **#4 (binding algebra swap to FHRR / Clifford)** first as the
  mechanism correction; then #1 (cleanup operator family); then #2/#3/#6.
- **R9 (NEW, rehab-routed, Yonelinas)**: Source-vs-item memory
  dissociation models beyond DPSD. 2x pass NOT pre-filtered to AI/ML
  framings. Strategy's 5 sketches in cap_map v14 unvetted draft.

Per [[feedback-unbiased-research]] and [[project-research-playbook]]
item 9: each rehab-routed R-request expects Research's 2x pass to
*generate* the rescue list, not to vet a Strategy-drafted one. The
DRAFT sketches are starting points only.

## Open experiment requests (routed to Experiment Dev)

- **E_A (Bet A)**: `wave14d_edit_then_query_v1` — orthogonal-key
  substrate + erase primitive + queried after edit. Multi-probe per
  Bet A.
- **E_B (Bet B, gated on R5)**: `wave14d_multi_task_cl_v1` —
  Corpus-C-domain transfer test once R5 specifies the third domain.
- **E_C (Bet C, gated on R6)**: `wave14r_erase_orthkeys_v2_kerdock`.
- **E_D (lower priority, K=32/K=64 generation)**: analyze the existing
  `wave14d_generation_v2_K32` and `wave14d_generation_v2_K64`
  metrics.json (COMPLETED_NEEDS_ANALYSIS in v7) to determine if
  generation quality monotone in K. Closes Tier-1 KILLER "GPT-quality
  generation" partial.

## Items deliberately NOT on the priority list

- Iterative charge-flipping for random-key forensics (closed by kill criterion this cycle)
- Multi-hop reasoning at 50-hop with current architecture (bounded; needs research-first redesign per R4)
- Edit-then-query on correlated-key substrates (mechanism closed; only orthogonal-key path is viable)
- All cycle-1 list items remain off (R3 rescues, MIR replay, basis_modification, pre-shift bpc, etc.)
