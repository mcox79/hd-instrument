# Active priorities

Owner: Strategy session. Updated atomically; downstream sessions (Experiment
Dev, Research, Visibility, Queue Health, META) read this.

**Last updated:** 2026-05-21 cycle 3 (in-loop self-pacing)
**Cap map version this refers to:** v13

---

## Recently resolved (since cycle 1)

| Bet | Outcome | Trigger |
|---|---|---|
| Bet 1 — ICL saturation curve | ✅ VALIDATED. slope on log2(ICTX) = +0.14, gain at ICTX=16384 = +1.41 bpc, kNN-LM-like log-linear through 4× substrate width. Tier-S #1 ICL gap closed at v1. | `wave14d_icl_via_pool_v3_scaling` full |
| Bet 2 — GDPR/surgical erase v3 (orthogonal-key path) | ✅ VALIDATED at M_stored/N ≤ 0.78. Hadamard subcode + anti-Hebbian rank-1 W edit passes all 5 Mirage probes. | `wave14r_erase_orthkeys_v1` + `wave14r_orthkeys_capsweep` |
| Bet 3 — Random-key iterative charge-flipping forensics | ❌ CLOSED at kill criterion. improvement=+0.03 over SVD (target +0.2). Structured-key WHT-forensics ✅ remains (separate path). | `wave14s_chargeflip_forensics_v1` |

## Top capability bets v2 (in priority order)

### Bet A — Edit-then-query end-to-end pipeline (Tier-1 KILLER, now unblocked)

**Claim.** A user-uploaded correction on an orthogonal-key substrate
propagates through the full pipeline: pool entry removed AND W-side
anti-Hebbian rank-1 edit applied AND subsequent queries reflect the
correction in cleanup-output ranking.

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

**Who acts.** Experiment Dev (build `wave14d_edit_then_query_v1` on top
of the validated Bet 2 erase primitive); Strategy (cap_map upgrade on
positive).

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

### Bet C — Full Kerdock + snap for dense-codebook regime (Bet 2 follow-up)

**Claim.** Full Kerdock(m=12) codebook (2^24 codewords from Z₄-Gray-mapped
Z₄-linear code) with snap-to-codebook paraphrase tolerance pass all 5
Mirage probes at M_stored > N (the dense-codebook regime where the
Hadamard-subcode v1 cannot operate).

**Why now.** Bet 2 v1 used Hadamard which is the exactly-orthogonal
limit (only valid M ≤ N). Product systems with M > N stored facts
need a richer codebook. Kerdock's bounded inner-product structure
(magnitudes in {0, 1/64} for N=4096) should give the same Mirage
protection at M up to ~ 2^16 stored facts.

**Multi-probe success criteria**:
- Same 5 Mirage probes as Bet 2 v1, sweep M_stored ∈ {N/2, N, 2N, 4N,
  8N}
- Snap-to-codebook reduces paraphrase_leak ≥ 50% vs no-snap variant
- argmax/rank/norm/cos/paraphrase floors all hold per Bet 2 thresholds

**Kill criterion.** At M_stored = 2N, any probe fails. Then dense-
codebook Mirage protection bounded; product story stays at M ≤ N.

**Who acts.** Research (audit Hammons-Kumar-Calderbank-Sloane-Solé
implementation details, Kerdock decoder choices); Experiment Dev (build
`wave14r_erase_orthkeys_v2_kerdock`).

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
- **R8 (NEW, rehab-routed, multi-hop)**: Noise accumulation in chained
  content-addressable memory. 2x pass; substrate-compatible variants
  ranked by depth-50 accuracy extension at NUM_FACTS=100. Strategy's 6
  sketches in cap_map v14 unvetted draft.
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
