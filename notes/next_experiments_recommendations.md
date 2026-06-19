# Next experiments — recommendations from capability synthesis

Written by capability-synthesis session. Updated against
`substrate_capability_map.md` v5 (2026-05-20 11:00).

## 2026-05-20 11:00 reshuffle — priorities changed by tree-walk + query-side findings

Three new outcomes (tree-walk MIXED, query-side NEGATIVE, LSH SimHash
closed) shifted the top of the queue. The two highest-priority items
this morning are no longer the v3 list.

**New top-3**:
1. **W-side edit primitive (rank-1 anti-Hebbian) + integration with pool erase.**
   Without it, edit-then-query KILLER stays 🟡. With it, the most
   product-leveraged Tier-1 KILLER closes.
2. **High-K generation v2 (K=64/128/256).** Unchanged from previous
   list; still the natural extension.
3. **ICL saturation curve at N≥4096.** Unchanged from previous list.

Previously top item (`wave14f_rsb_tree_walk_v1`) **completed and
landed mixed** — dropping it from the priority list. RSB algorithm
revisit only if pool grows past ~50K.

---

The main session decides what to queue. This file is the ordered
shopping list with reasons; treat priority numbers as the synthesis
session's view, not a binding order.

## Priorities — top of queue

### Priority 1: ICL saturation curve (CLOSE A KILLER GAP)
**Question**: where does substrate ICL gain saturate as N grows?
v2 measured ALPHA=0.3 N=2048 (+1.63 bpc) and ALPHA=1.0 N=256 (+3.19 bpc).
The kNN-LM literature predicts log-linear gain through 10^9 entries;
our substrate's saturation point is unmeasured.

**Experiment**: `wave14d_icl_via_pool_v3_scaling`
- ALPHA=1.0 (pool-only), sweep N ∈ {64, 256, 1024, 4096, 16384}
- 3 seeds per N
- Pre-registered prediction: log-linear gain through N=4096, possible
  knee somewhere between N=4K-16K once P approaches d / log d ≈ 480
  (per Frady-Sommer overfill knee at our N=4096 substrate).

**Why now**: ICL just became a Tier-1 ✅ capability. We need its
scaling envelope before we can sell "substrate scales like kNN-LM"
as a product story. ~1-2h on GPU.

### Priority 2: ~~RSB tree-walk algorithm~~ **COMPLETED 2026-05-20 — outcome MIXED**
`wave14f_rsb_tree_walk` ran. Recall@10 reached 0.768 at b=8, matching
the pre-registered prediction ("0.7-0.85 at b=2, rising sharply with
b"). But 2.2 ms/query vs brute-force 0.079 ms = 28× SLOWER at our
pool size P=1024.

Literature crossover (Beygelzimer cover trees, Beyer 1999 distance
concentration) is at N ≈ 10^4 – 10^5 for high-d vectors. At our scale,
brute force wins. **Drop from priority list.** Revisit only if pool
grows past 50K.

(Latent capability "Hierarchical retrieval (RSB) — practical algorithm"
moved from 🔬 to ❌ at P=1024 in cap map v5. Structural ultrametricity
✅ remains.)

### Priority 3: Generation v2 at higher K with strict baseline
**Question**: does generation quality scale with K, or peak at K=16?

**Experiment**: `wave14d_generation_v2_K64` + `_K128` + `_K256`
- Same v2 protocol (B3 Markov-chain baseline, k4_validity threshold)
- 3 seeds each
- Pre-registered: monotone improvement through K=64, possible peak
  K=64-128 (matches R10 curve shape)

**Why now**: v1 showed generation works at K=4/8/16 but only against
random baseline. v2 strict-baseline confirmation lives only at K=16.
This is the obvious extension and uses existing infrastructure.

## Priorities — second tier (close UNSURE killers)

### Priority 4 — PROMOTED TO P1: W-side edit primitive (rank-1 anti-Hebbian)
**2026-05-20 11:00 update**: `wave14d_query_side_integration`
landed NEGATIVE. Pool-only erase leaks 93% (the (k,v) outer-product
is absorbed into W during training; pool erasure doesn't touch it).
Edit-then-query Tier-1 KILLER dropped from 🟢-partial to 🟡 — survives
only if we add a W-side edit primitive.

**Question**: does a rank-1 anti-Hebbian W edit, applied after pool
erase, reduce leak rate from 93% → below 10% without degrading other
predictions?

**Experiment**: `wave14d_w_side_edit_v1`
- Pre-step: identify candidate fact (k, v) in pool
- Erase pool entry
- Apply W edit: `W -= alpha * (W@k - 0)(k^T C^-1) / (k^T C^-1 k)`
  (anti-Hebbian Hopfield-Feinstein-Palmer 1983, Kohonen pseudo-inverse;
  C is identity for first cut, then per-batch covariance)
- Measure (vs `wave14d_query_side_integration` baseline):
  - Leak rate (target: < 10%)
  - p_drop on erased fact (target: > 80%)
  - Side effects on 100 other random pool entries (target: < 5% degradation)
- 3 seeds, K=8, 30 facts per seed (match query_side_integration setup)

**Why now (PROMOTED)**: this is the architecturally-additive fix that
unblocks the most product-leveraged Tier-1 KILLER (surgical
fact-correction / GDPR erase). Without it, the substrate's claim of
"editable memory" doesn't compose into actual product behavior. With
it, edit-then-query closes at ✅.

**Research foundation**: math survey in event log implication
(ROME/MEMIT, Kohonen, Hopfield-Feinstein-Palmer 1983,
Guo et al. 1911.03030 cert-removal). Architecturally additive — does
not require changes to existing pool-edit primitive.

**Estimate**: ~150 LOC + 1-2h CPU. Comparable in scope to
`wave14d_sequential_edit_stress`.

(After this lands positive, the original edit-then-query end-to-end
pipeline test is the next experiment in the chain.)

### Priority 5: Multi-task transfer beyond A→B
**Question**: continual learning confirmed for A→B distribution
shift on same corpus. What about A → genuinely different domain C?

**Experiment**: `wave14d_multi_task_cl_v1`
- A=current corpus, B=current shift, C=different domain (e.g. code,
  formal language, structured data) — `wave14d_multi_task_cl_research.md`
  has design candidates
- Sequential: Phase A → Phase B → Phase C
- Measure: retention of A, retention of B, learning of C
- Use confirmed random-replay mechanism throughout
- 3 seeds

**Why now**: continual-learning capability claim is currently
"single-shift only." Product claim "LLM that genuinely learns from
interactions" requires multi-domain. Higher-risk than priority 4 but
higher-leverage if positive.

## Priorities — third tier (mechanism / framework)

### Priority 6: 3-factor binding design-space mapping
**Question**: with B=3 cliff at K/N≈0.31, which previously-planned
capabilities survive the new constraint?

**Action item (not an experiment)**: re-audit experiments_backlog.md
+ design notes for any 3-factor binding designs (polarity-tagged,
temporal-tagged, mode-tagged). Mark which ones now have K-cap
≈1270 at N=4096 and adjust their feasibility.

**Why now**: B=3 cliff finding is fresh and capability-bounded.
Cheap audit; prevents queueing experiments that can't reach their
claimed K range.

### Priority 7: SSH-BSC topological winding (Tier-2 KILLER probe)
**Experiment**: `wave14e2_ssh_bsc_topological` — already queued in
v2 but not yet run. 30-min CPU test.

**Why now**: low-cost probe of a Tier-2 KILLER (integer
winding-protected memories). If positive, opens a categorical
noise-immunity story; if negative, closes one direction cleanly.
Bounded downside, structured upside.

### Priority 8: Multi-hop reasoning v2 (UNSURE → ?)
**Experiment**: `wave14e_multi_hop_v2` — queued, not yet run.
- Encode facts as e = subj * rel * obj, superpose into M
- Probe with per-hop cleanup
- Per research: 50+ hops viable with cleanup

**Why now**: cheap-ish (1-2h GPU), tests a Tier-2 KILLER cleanly.

### Priority 9 (infra): Vectorize learn_sparse_dictionary
**Not a capability test** — infrastructure prerequisite for the
self-supervised-concept-discovery experiment.

**2026-05-20**: `wave14d_sparse_vs_ppmi` timed out at 5400s due to a
Python-loop bottleneck (~150K iterations per run). Expected runtime
post-refactor: ~1 min.

**Action**: refactor `learn_sparse_dictionary` to fully-vectorized
sparse coding before re-queueing `wave14d_sparse_vs_ppmi`. Without
this, the self-supervised concept discovery Tier-3 KILLER (⚪) cannot
be tested.

**Owner**: not synthesis session (would touch experiment code, which
synthesis does not edit). Main session.

## 2026-05-20 14:53 — Highest-leverage build identified: rank-1 anti-Hebbian W edit primitive

> **RETRACTED 2026-05-20 23:24 by next-cycle user evidence.** See
> `## 2026-05-20 23:24` section below. The anti-Hebbian rank-1 W
> edit was implemented and tested (`wave14h_alpha_sweep_v2`,
> `wave14p_erase_multiprobe`). It passes argmax but FAILS Mirage
> probes (rank, norm, cos, paraphrase) under correlated keys.
> Per the user's cap map evening update: "Don't pitch as
> GDPR-grade. Direct subtraction works mathematically but cross-talk
> magnitude persists under correlated keys."
>
> The recommendation below was correct math but insufficient as a
> selective-forgetting primitive. Argmax-pass is not enough. The
> recommendation is retracted as written; the GDPR-erase capability
> ❌ in the current architecture remains a real gap, but rank-1
> anti-Hebbian alone does NOT close it.

`wave14g_erase_under_replay` is the second independent negative on
the W-leak axis (first was `wave14d_query_side_integration`). The
mechanism is fully diagnosed and the fix is named:

**Build**: implement anti-Hebbian rank-1 W edit. Formula from the
event log (Hopfield-Feinstein-Palmer 1983 + Guo cert-removal
1911.03030):

```
W -= alpha * (W @ k - 0) * (k^T C^-1) / (k^T C^-1 . k)
```

where `k` is the key vector for the fact to forget and `C` is the
covariance of stored facts (or identity for spherical assumption).

**Why this WAS the top recommendation (now retracted)**:
- Closes the GDPR / surgical-erase capability (currently ❌ in
  current architecture)
- Unlocks the Tier-1 KILLER edit-then-query (currently 🟢 partial)
  to potentially ✅
- Per the event-log diagnosis: "architecturally additive, not a kill"
- Fits the no-backprop, Hebbian-only constraint of the substrate
- Math is well-cited; not speculative

**What went wrong**: only argmax was sanity-checked. Under Mirage
probes (per arXiv:2503.06991 "Mirage of Model Editing"), the residual
cross-talk magnitude remains detectable on correlated keys.

**Composable with existing experiments**:
- `wave14d_edit_then_query_v1` (P4 above) — would test query-side
  reflection after the W edit lands
- `wave14g_erase_under_replay` itself — re-run after W-edit to show
  erase_effective should go from 7.4% → ~100%

**Implementation pointer**: `notes/wave14g_research_wside_erasure.md`
(referenced in the event log; check if present).

This is the single most leverage-dense build in the recommendations
file as of 2026-05-20 14:53.

---

## 2026-05-20 23:24 — Retraction of v8 W-edit recommendation; acknowledgment of user evening session

User's evening session (commits `c325012` + `44e9c3b` at 22:50, 22:56)
validated the v8 recommendation experimentally and CAUGHT IT FAILING:

**Mirage failure mode confirmed**:
- `wave14h_alpha_sweep_v2`: anti-Hebbian rank-1 W edit passes argmax
  with 76.7pp leak reduction (looked GDPR-grade on first inspection)
- `wave14p_erase_multiprobe`: same edit FAILS rank/norm/cos/paraphrase
  probes. Direct subtraction works mathematically but cross-talk
  magnitude persists under correlated keys.
- `wave14anneal_selective`: selective thermal annealing in (v_e, k_e)
  subspace also caught on Mirage (same norm_ratio failure).
- Only global anneal at p=1.0 (`wave14z_anneal_erase`) collapses norm
  — that's factory reset, not selective.

**Implication for recommendations**: GDPR-grade selective forgetting
under correlated keys is HARDER than the v8 anti-Hebbian recipe
suggested. The capability remains ❌ in current architecture; the
fix space has narrowed (anti-Hebbian + selective anneal both
falsified) and now needs deeper research.

**Lesson for the synthesis session**: all future erase / edit / GDPR
recommendations must specify multi-probe verification (rank + norm
+ cos + paraphrase per Mirage paper, arXiv:2503.06991) as a
pre-registration requirement. Argmax-pass alone is no longer
sufficient evidence.

### User-added capabilities (acknowledged from cap map evening update)

These landed via direct cap map commits, not session_events.jsonl
events. Synthesis session does NOT re-touch the rows — but flagging
them here so the recommendations file stays coherent with the cap
map:

- **✅ Substrate forensics via WHT with structured keys**
  (`wave14xrd_structured_keys`): Hadamard keys give SNR 1.5e7 vs 1.3
  random. Crystallography analog validated. Bragg peaks at integer
  Walsh frequencies. **New capability product story**: structured-key
  substrate is auditable without queries (count Bragg peaks = number
  of facts; peak frequencies = identify keys).
- **✅ ALPHA_C confirmed AGS-like**: α_c = 0.153 at N=4096 (rising
  from 0.082 @ N=1024 → 0.107 @ N=2048 → 0.153 @ N=4096). Substrate
  is in canonical AGS Hopfield regime. 40 years of spin-glass theory
  applies.
- **🔬 New candidate capabilities** the user has flagged for follow-up:
  MP-edge forensics primitive, charge-flipping readout attack
  (security finding), Kerdock-coset structured codebooks (2× usable
  K + 50-350× faster cleanup via FHT), Parisi RSB pure-state
  addressing.

### Re-prioritized: what to recommend instead of the falsified v8 rec

The previous "single highest-leverage build" (anti-Hebbian rank-1
W edit) is retracted. The cleanest replacement candidates for the
GDPR-erase ❌ gap are:

1. **Kerdock-structured W rewrite** — the user flagged that the
   "decoder swap to sparse Hopfield gives exp(N) capacity" story
   was a category error (different architecture). But the
   Kerdock-coset structured-codebook variant offers a real 2×
   usable K + 50-350× faster cleanup via FHT, AND ships with the
   WHT-forensics capability. Might offer enough structural change
   to make selective erase tractable (Hadamard subspaces are more
   surgically separable than random ±1 keys).
2. **Charge-flipping erase / forensics** — the user flagged this as
   a security finding; it could equally be exploited as a primitive
   to verify which facts have been erased (audit trail). Worth
   pairing with any erase mechanism as a verification layer.
3. **Re-derive selective erase against the Mirage probe battery
   from the start** — any new erase mechanism should be evaluated
   against all four probes (rank, norm, cos, paraphrase) before
   being added to the cap map. Synthesis session will not promote
   to ✅ any future erase claim that only passes argmax.

**For now, this is a deferred build, not a recommendation.** The
user has the architectural design context; synthesis flags the gap
but does not re-propose a specific fix until the candidate map's
options have been drilled.

---

## 2026-05-20 14:15 — CRITICAL flag: ICL pool-size scaling INVERTED + augment_pool bug blocks Tier-S #1

### Substantive contradiction with v3 framing (per protocol: surfaced for user resolution)

`wave14f_icl_scaling_pool` (NEGATIVE_INVERTED_SCALING) reports slope
on log2(pool_size) = **−0.067**: gain DECREASES as pool grows from
512 → 4096 (0.38 → 0.32 → 0.26 → 0.17 bpc).

The v3 ICL ✅ promotion framing claimed "matches kNN-LM log-linear
scaling pattern, no saturation observed" based on
`wave14d_icl_via_pool_v2` which swept N (relevant examples added).
The new result sweeps pool_size (total memory store, with mostly
irrelevant items). They are NOT the same axis, but the v3 framing
was loose enough that the inversion can read as a contradiction.

**My current interpretation**: ICL capability survives at ✅, with a
caveat that scaling is on the relevant-example axis, not on raw
pool_size. v7 of the cap map records it this way. User should
confirm or correct.

### Critical infra bug to unblock Tier-S #1

`wave14g_icl_saturation_extended` failed with
RuntimeError at line 232 of `augment_pool`:
- tensor size mismatch (4096 vs 8192)
- Hardcoded POOL_SIZE=4096 doesn't handle N > POOL_SIZE
- Event log: "Fixable in ~10 lines."

**This experiment is the planned closure of the ICL saturation
question.** Until it runs at extended N, the ICL pool-saturation
capability stays 🟡. Recommend fix + re-queue as P1.

### Two completed-pending-analysis (P3 from prior cycle)

`wave14d_generation_v2_K32` (13:40) and `wave14d_generation_v2_K64`
(13:42): completed with strict baseline structure but
COMPLETED_NEEDS_ANALYSIS — verdict depends on
`substrate_pool > b3 baseline at this K`, which is computable from
the position-resolved metrics already in metrics.json. Needs analyzer
pass (~10 min of work).

`wave14f_icl_rsb_synergy` (13:43): also COMPLETED_NEEDS_ANALYSIS. If
positive, opens a new compound-capability row (ICL × RSB hierarchy).

### One mild positive walkback (engineering, not killer)

`wave14g_decompose_K_cliff_N8192`: K/N invariance breaks across N
(cliff at K/N=0.50 at N=8192 vs predicted 0.56 from N=4096).
Engineering housekeeping — production sizing needs an N-dependent
correction, not just K/N. Not a Tier-1 KILLER walkback.

---

## 2026-05-20 20:39 — wave14i/14j/14k candidate batch completed_via_healer

Three experiments from `notes/wave14i_capability_candidate_map.md`
have surfaced as `completed_via_healer` (failed status but metrics.json
exists, needs analyzer pass). User curates the candidate map; the
synthesis session does NOT add cap-map rows for these until results
are interpreted.

| Experiment | Event ts | Candidate map ref | Predicted result | Kill criterion |
|---|---|---|---|---|
| `wave14i_schema_emergence` | 19:08:14 | #7 (Tier-S, Saxe SVD) | gap ratio ~1.4 at N=200; held-out cos 0.6-0.75 | cos<0.3 or gap<1.3 |
| `wave14j_breather_slots` | 20:08:16 | B3 (materials-science) | 3-4× noise tolerance (cosine basin) | iterated cleanup doesn't contract |
| `wave14k_1bit_cs_cleanup` | 20:08:16 | M3 (math survey, "most strategic") | First cleanup operator with formal capacity/crosstalk bound | (not specified in candidate map) |

**Action item for user**: analyzer pass on the three metrics.json
files. The user's candidate-map kill criteria are precise; an
analyzer can apply them directly to the metrics output.

**Why this is queued for user, not synthesis**:
- Synthesis session writes to `substrate_capability_map.md` and
  `next_experiments_recommendations.md` only
- The candidate map is the user's strategic curation layer
- Adding placeholder 🟡 rows to the cap map for in-flight candidates
  would duplicate the user's tracking and risk drift between docs
- Once results are interpreted, the user can move validated
  candidates into the cap map via the next cap-map cycle (synthesis
  session will integrate from session_events.jsonl in the normal
  way)

If any of the three are positive, they likely upgrade Tier-S/A:
- `schema_emergence` → CLS emergent abstraction (brain-inspired)
- `breather_slots` → high-stakes-fact tier (premium feature)
- `1bit_cs_cleanup` → formal noise bound on cleanup primitive

---

## NEEDS_REVIEW backlog from CPU-fallback window (2026-05-20 13:32)

Eight `wave14e*` experiments completed during the 22h CPU-fallback
window (driver in PnP Code 43 from 14:21 yesterday to 12:01 today).
All emerged from backlog with verdict "completed" but outcome
NEEDS_REVIEW or NO_METRICS_INCONCLUSIVE.

User: I cannot move any of these capability rows until interpretation
lands. They are flagged 🟡 in the cap map v6 update. **Decision
items**:

1. **multi_hop_v2** reported `acc_1hop=0.98`. This is baseline
   retrieval, not the KILLER claim (50+ hops with cleanup). Was the
   experiment instrumented to report acc at multiple hop depths? If
   yes, retrieve them. If no, re-queue with hop depth sweep ∈ {1, 5,
   10, 25, 50}.

2. **hierarchical_composition** reported `byte_accuracy=1.0`. Without
   a no-substrate baseline this metric doesn't bear on the KILLER
   (depth-6+ composition). What was the comparison? If raw 1.0
   accuracy means substrate trivially reconstructs at K_phrase=3,
   that's not the test we want.

3. **ssh_bsc_topological** (Tier-2 KILLER probe — integer
   winding-protected memories) ran 100 trials at N=4096 but emitted
   no key metric. Need the winding-number protection vs noise-level
   curve from the metrics.json to determine if the predicted sharp
   kink at p_c ≈ 1/(2·ν_density) materializes.

4. **continuous_edits** + **continuous_edits_v2** — needed to
   determine whether Bernoulli-mix soft-bipolar continuous edits
   work as the v2 research synthesis predicted.

5. **temporal_binding** + **multi_hop_reasoning** (v1) — silent
   failures during CUDA fallback. Re-queue on real GPU.

Action item for user: triage these results manually, or queue a
research-agent pass on the metrics.json files. Synthesis session
cannot move capability rows from these without clearer signal.

## Gaps without queued experiments

These are capabilities I cannot yet propose a clean test for; flagging
so main session knows the unknown unknowns:

1. **Compositional generalization** — novel combinations of learned
   concepts. No clean held-out compositional eval designed.
2. **Calibration / uncertainty** — does the substrate's softmax temp
   match epistemic uncertainty? Tested implicitly by ICL gain but no
   direct calibration probe.
3. **Sleep-style memory consolidation** — offline replay-during-
   quiescence experiment ungated by the random-replay positive (which
   was online during Phase B, not quiescent).
4. **Self-supervised concept discovery** — without PPMI prior.
   Open since v1.

## Conflicts / things to watch

### Conflict: R3 status across notes
The map closes R3 at K≥16. STATE_2026_05_19.md and the overnight log
still carry "R3 +0.032" as a positive low-K finding. Both are right:
the substrate has a real K=4 R3-Laplace effect, but it's *literature-floor
small-effect, not substrate-unique*. Documentation drift risk if main
session pulls from older notes.

### Conflict: cpu_platform_timing inconclusive
v1 map had cpu_platform_timing 🟡 (cpu_platform_timing_redo timed out
at 3600s). Has it been re-run since the WMI runner repair? If yes and
positive, → ✅. If still hung, the consumer-CPU claim is unverified.
Recommend a clean re-run as a Priority 1.5 if not done.

### Conflict: K=2944 dip retraction
Earlier notes (overnight_log up to cycle 3) cite the 50%/61% dip as a
real cliff substructure. v3 retracts it. Old characterizations of
the K-cliff substructure should be searched and updated when relevant.

## Anti-recommendations (do not queue)

- **R3 rescue variants** — closed, mechanism understood, K-flat.
- **Compound interventions sharing W-drift correction** — closed by
  four-argument convergence.
- **MIR-style priority replay** — closed by rank-equivalence math.
- **Iterative Hopfield as label readout** — protocol mismatch closed.
- **C3 factored vs C1 classical** — retracted lambda artifact.
- **Pre-shift bpc improvements** — wrong goal per pre-shift research.
  The substrate is at hygiene-pass on pre-shift; product stories live
  at post-shift / BWT / decomposition / K-scaling.

---

## Summary for main session

Top three experiments to queue (in priority order):

1. **`wave14d_icl_via_pool_v3_scaling`** — N sweep at ALPHA=1.0 (1-2h GPU)
2. **`wave14f_rsb_tree_walk_v1`** — single-linkage MST + beam search (1-day build, CPU)
3. **`wave14d_generation_v2_K64`** through K=256 — strict-baseline generation curve (2-3h GPU)

These three close the highest-leverage gaps in the v3 map: ICL
saturation, RSB algorithm, generation-K curve. After they land, the
Tier-1 KILLER board would be 4-5 out of 6 ✅, which is a different
product than "memory backend."
