# Active priorities

Owner: Strategy session. Updated atomically; downstream sessions (Experiment
Dev, Research, Visibility, Queue Health, META) read this.

**Last updated:** 2026-05-21 cycle 14 (Bet G ✅; generation caveat)
**Cap map version this refers to:** v25

---

## Recently resolved (since cycle 1)

| Bet | Outcome | Trigger |
|---|---|---|
| Bet 1 — ICL saturation curve | ✅ VALIDATED. slope on log2(ICTX) = +0.14 at low/mid ICTX; soft-saturating to +0.05 at high ICTX (≤65536). Monotone positive through 16× substrate width. | `wave14d_icl_via_pool_v3_scaling` full + `wave14w_icl_extended` full |
| Bet 2 — GDPR/surgical erase v3 (orthogonal-key path) | ✅ VALIDATED at M_stored/N ≤ 0.78. Hadamard subcode + anti-Hebbian rank-1 W edit passes all 5 Mirage probes. | `wave14r_erase_orthkeys_v1` + `wave14r_orthkeys_capsweep` |
| Bet 3 — Random-key iterative charge-flipping forensics | ❌ PROVISIONAL per rehab discipline (cap_map v14). +0.03 over SVD (target +0.2). R7 routed. | `wave14s_chargeflip_forensics_v1` |
| Bet C — Full Kerdock + structured codebook for dense regime (M > N) | ✅ VALIDATED at N=4096, M_stored up to 8N via wave14ya_erase_kerdock_v4 (extended from initial 2N target). | `wave14v_erase_kerdock_v2` + `wave14y_erase_kerdock_v3` + `wave14ya_erase_kerdock_v4` |
| **Bet A — Edit-then-query end-to-end pipeline (Tier-1 KILLER)** | ✅ VALIDATED. Both Kerdock + correlated arms: edit-acc=1.000, kept-acc=1.000, side-effect=0.0, paraphrase preserved at h ∈ {4, 8}. Tier-1 board now 4/6 ✅. Audit-divergence note: v5's 93% leak didn't reproduce; v20 cap_map flags for follow-up. | `wave14yb_edit_then_query_kerdock` |
| **Bet G — Substrate calibration rescue** | ✅ RESCUED via TEMPSCALE at β=32 (ECE 0.59 → 0.0000 over 3 seeds). First ❌ PROVISIONAL to close ✅ under the v14 rehab framework. Strategy sketch #1 (Platt/temperature) worked; R11 retrospective confirmation. | `wave14yx_calibration_temp_scaling` |

## Top capability bets v4 (in priority order; Bets C ✅; E and F added per user 2026-05-21 ~10:35)

### Bet H — Autoregressive generation rescue (NEW 🟡; rehab-routed)

**Claim (target).** A sampling rescue (top-k, nucleus, repetition
penalty, β tuning, or multi-seed-with-different-prefix) restores
512-byte autoregressive char_entropy to ≥2.5 and reduces 4-gram
repetition below 0.5.

**Why now.** `wave14yy_autoregressive_generation` (cycle 14): under
α=1.0, β=8, single seed (17), generation collapses to "  e  e  e..."
(char_entropy 0.917, ngram_repetition 1.000). v3's K=16 strict-baseline
PASS measured single-position prediction, not autoregressive multi-step.
Existing generation ✅ row keeps single-position evidence; this rescue
targets the multi-step regime.

**Multi-probe success criteria** (any rescue passing all):
- char_entropy ≥ 2.5 (over 512 chars)
- ngram_repetition ≤ 0.5 (4-grams)
- 3 seeds minimum
- self_bpc < 4.0

**Kill criterion.** If 0/5 rescues clear char_entropy ≥ 2.5,
autoregressive multi-step generation closes ❌-with-current-readout;
single-position K=16 capability survives as degraded ✅.

**Who acts.** Research (R12 routed — sampling-rescue literature 2x
pass); Experiment Dev (test top-ranked rescue once R12 lands).

---

### Bet G — RESOLVED ✅ via TEMPSCALE at β=32 (see "Recently resolved")

`wave14yx_calibration_temp_scaling` full: ECE = 0.0000 at β=32 over
3 seeds. First ❌ PROVISIONAL to close ✅ under the v14 rehab
framework. Strategy sketch #1 (Platt/temperature) worked; R11
retrospectively confirms.

---

### (prior Bet G spec — kept for reference but resolved)

#### Bet G — Calibration rescue (NEW ❌-PROVISIONAL needs rehab)

**Claim (target).** A substrate calibration rescue (post-hoc
temperature scaling, isotonic, Bayesian σ², multi-vote, or
norm-based confidence) reduces ECE below 0.15 on the
fact-retrieval-confidence test.

**Why now.** `wave14yd_calibration_fact_retrieval` (10:47) returned
ECE=0.59 / Brier=0.35 — substrate retrieves at accuracy 1.0 but its
confidence scores are not predictive. Calibration was on cap_map's
UNSURE list (Tier-3) since v1; now closed PROVISIONAL ❌ per the
rehab discipline. Important caveat: this does NOT affect Tier-1
KILLER capabilities; calibration is Tier-3 (matters for production
deployment but not core product story).

**Multi-probe success criteria** (any rescue passing all of these):
- ECE < 0.15 on fact-retrieval (matching the v1 kill criterion
  threshold)
- Brier < 0.20
- Overall accuracy preserved at ≥ 0.95 (calibration fix doesn't
  degrade retrieval)
- 3 seeds, N=4096
- Per-bin coverage (test set spans confidence range)

**Kill criterion.** If 0 of 5 R11 rescues clear ECE < 0.15, substrate
calibration closes ❌-structural and product story drops
"trustworthy confidence scores."

**Who acts.** Research (R11 — 2x deep research routed); Experiment Dev
(test rescue candidate after R11 ranks).

---

### Bet A — RESOLVED ✅ (see "Recently resolved" table above)

`wave14yb_edit_then_query_kerdock` full mode: both arms pass edit +
query at 1.000 / 1.000 / 0.0 side-effect / paraphrase preserved.
Tier-1 KILLER board now 4/6 ✅. Open audit item: why didn't v5's
93% leak reproduce? Two interpretations (setup-specific artifact or
different failure mode); flagged in cap_map v20 for follow-up.

---

### (prior Bet A spec — kept for reference but resolved)

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

### Bet E — Parisi P(q) overlap structure as substrate fingerprint

**Claim.** The Parisi overlap distribution P(q) — measured on the
substrate's stored bundles — varies meaningfully with substrate
configuration (codebook structure, K, M_stored). If true, P(q) shape
becomes a substrate-forensics primitive that needs no query access:
shape characterizes operating point.

**Why now.** `wave14e2_parisi_ultrametricity` (v3) validated RSB phase
*structurally* at one operating point (P(q) multi-peaked at q=0.138 and
0.276; ultrametricity 0.357 > 0.33 chance threshold). The structural
finding has been static since 2026-05-20. With Bet C's structured-codebook
substrates now ✅ through M/N=8.0, the question of whether P(q) discriminates
between random ±1 substrate, Hadamard substrate, and Kerdock substrate is
testable. Also: does P(q) shift as M_stored crosses Bet C boundaries
(M=N, M=2N, M=8N)? Per [[feedback-materials-science-probe]] the
spin-glass framing applies directly (P(q) is the canonical order
parameter from Mezard-Parisi-Virasoro 1987).

**Multi-probe success criteria** (each required):
- P(q) measured at 3 substrate configs (random ±1, Hadamard, Kerdock)
  at N=4096, K=400, M_stored=2N: peak counts / peak locations /
  ultrametricity distinguishable across configs (≥2σ separation on
  at least one metric)
- P(q) measured at 3 M_stored values (M=0.5N, M=N, M=2N) for fixed
  random substrate: shape shift detectable
- All cells satisfy ultrametricity > 0.33 (chance threshold) — i.e.,
  RSB phase persists across configs
- 3 seeds per cell

**Kill criterion.** P(q) shapes statistically indistinguishable across
the 3 substrate configs AND across the 3 M_stored values (no metric
shows ≥2σ shift). Then P(q) is a generic spin-glass property of any
high-dim random ±1 matrix, not a substrate-informative probe — moves
from 🔬 to "descriptive only, no product story."

**Who acts.** Research (verify methodology — Parisi protocol is
well-established but the substrate-specific measurement details
matter); Experiment Dev (`wave14_parisi_pq_sweep_v1` once Research
confirms the protocol).

---

### Bet F — SSH-BSC topological winding-protected memories (Tier-2 KILLER probe revisit)

**Claim.** Substrate-encoded facts tagged with an integer winding
number (via sublattice / domain-wall structure per Hasan-Kane chiral
class AIII) have categorical noise immunity: noise below threshold
p_c shifts winding count by ±1 only at wall-adjacent sites; larger
shifts require coordinated multi-bit flips with probability ~p².
Sharp transition at p_c ≈ 1/(2·ν_density), q-dependent (ν_density
proportional to q).

**Why now.** The original `wave14e2_ssh_bsc_topological`
(2026-05-20 CPU-fallback window) returned categorical_correct=0.0 at
all noise levels — flagged as `NEEDS_REVIEW`. The probe was raw
wall-count data with no Z-quantization recovery metric, so the test
couldn't distinguish "substrate has no topological protection" from
"probe didn't measure topological protection." Capability has sat at
🟡 since v6. Bumping to active bet means committing to a clean redo.

**Multi-probe success criteria** (each required):
- Categorical recovery rate vs noise level p: monotone decay with a
  detectable kink at predicted p_c ≈ 1/(2·ν_density)
- Winding-number distribution Z-quantization holds for p < p_c
  (Hopf-style integer recovery — must include the integer-recovery
  probe missing from v1)
- Charge sweep q ∈ {2, 5, 10, 20}: empirical p_c scales 1/q (matches
  Hasan-Kane prediction within 30%)
- 3 seeds per (q, p) cell

**Kill criterion.** After probe redesign + retest, no sharp transition
observed in categorical recovery across noise sweep, OR Z-quantization
fails for all p. Then SSH-BSC topology doesn't give predicted
protection in BSC substrate — closes at ❌-with-rehab-discipline
(5 axis-combination rescues listed before broader topological-
protection family closes).

**Who acts.** **Research first (R10)** — need a lit-vetted protocol
for measuring topological invariants in BSC substrates per [[feedback-unbiased-research]]
(the original probe didn't fire; that's a methodology gap, not a
substrate finding). Pass 1: external lit scan of Hasan-Kane class AIII
probes, SSH-model topology metrics, Z-quantization recovery tests.
Pass 2: substrate-compatible drill. Experiment Dev queues
`wave14_ssh_bsc_v2_protected` once Research delivers the probe spec.

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
- **R9 (rehab-routed, Yonelinas)**: Source-vs-item memory
  dissociation models beyond DPSD. 2x pass NOT pre-filtered to AI/ML
  framings. Strategy's 5 sketches in cap_map v14 unvetted draft.
- **R11 (Bet G prerequisite)**: LANDED 2026-05-21 11:14. Bet G
  resolved ✅ via TEMPSCALE at β=32 (Strategy sketch #1 was correct).
  R11 retrospective-confirms.
- **R12 (NEW, Bet H prerequisite, rehab-routed)**: Neural-LM sampling
  rescues preventing repetition collapse. 2x pass: pass 1 broad (top-k,
  nucleus/top-p, beam, repetition penalty, contrastive decoding,
  frequency penalty, typical sampling, mirostat); pass 2 substrate-
  compatible drill. Output: ranked rescue list with predicted
  char_entropy-improvement per rescue. Strategy's 5 draft sketches
  (β tuning, top-p, repetition penalty, multi-seed, prefix selection)
  unvetted.
- **R10 (Bet F prerequisite)**: SSH-BSC topological probe design.
  Original `wave14e2_ssh_bsc_topological` returned categorical_correct=0
  at all noise — methodology gap, not substrate finding. 2x pass:
  pass 1 broad (Hasan-Kane class AIII probes, SSH-model topology
  metrics, Z-quantization recovery tests, charge-flipping topology
  literature, condensed-matter SSH chain protocols); pass 2 drill
  substrate-compatible probe specifying integer-recovery metric,
  q-dependent p_c sweep design, control arm (random non-topological
  encoding).

Per [[feedback-unbiased-research]] and [[project-research-playbook]]
item 9: each rehab-routed R-request expects Research's 2x pass to
*generate* the rescue list, not to vet a Strategy-drafted one. The
DRAFT sketches are starting points only.

## Open experiment requests (routed to Experiment Dev)

- **E_A (Bet A)**: RESOLVED ✅ by `wave14yb_edit_then_query_kerdock`.
  Follow-up audit (low priority): why did v5's 93% leak not reproduce?
- **E_G (Bet G, R11 LANDED 2026-05-21 11:14)**: TEMPSCALE smoke
  passed at β=16 (ECE → 0); full mode running. If full positive,
  Bet G closes ✅.
- **E_MH (Multi-hop rescue, gated on R8 ✅)**: queue BOTH
  `wave14r_multihop_FHRR_v1` (A1 mechanism correction) AND
  `wave14r_multihop_hybrid_v1` (C1 substrate-coherent variant) per R8.
- **E_B (Bet B, UNBLOCKED — R5 landed 2026-05-21 10:21)**:
  `wave14d_multi_task_cl_v1` — Corpus-C-domain transfer test per
  `notes/research_R5_corpus_C_design_2026-05-21.md` specifications.
  Ready to queue.
- **E_C (Bet C, gated on R6)**: `wave14r_erase_orthkeys_v2_kerdock`.
- **E_D (lower priority, K=32/K=64 generation)**: analyze the existing
  `wave14d_generation_v2_K32` and `wave14d_generation_v2_K64`
  metrics.json (COMPLETED_NEEDS_ANALYSIS in v7) to determine if
  generation quality monotone in K. Closes Tier-1 KILLER "GPT-quality
  generation" partial.
- **E_E (Bet E)**: `wave14_parisi_pq_sweep_v1` — P(q) measurement
  across (codebook config, M_stored) grid. Multi-probe per Bet E.
  Research methodology review optional but recommended before queue.
- **E_F (Bet F, R10 LANDED 2026-05-21 11:02 — unblocked)**:
  `wave14_ssh_bsc_v2_protected` — redo topological probe per
  `notes/research_R10_SSH_BSC_topological_probe_2026-05-21.md`
  protocol spec. Multi-probe per Bet F.

## Items deliberately NOT on the priority list

- Iterative charge-flipping for random-key forensics (closed by kill criterion this cycle)
- Multi-hop reasoning at 50-hop with current architecture (bounded; needs research-first redesign per R4)
- Edit-then-query on correlated-key substrates (mechanism closed; only orthogonal-key path is viable)
- All cycle-1 list items remain off (R3 rescues, MIR replay, basis_modification, pre-shift bpc, etc.)
