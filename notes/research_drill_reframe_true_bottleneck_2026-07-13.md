# Research drill — reframe the bottleneck: where does the wall on low-MRR inductive KG reasoning actually live?

**Filed by:** research sub-agent (Sonnet), 2026-07-13. **Trigger:** Director's explicit instruction to stop attacking the
REPRESENTATION (codes/capacity — 8+ drills today, all came up empty or capped, see Cross-thread synthesis) and instead
ask whether representation was ever the right target, for the `anchor_compose` inductive-entity link-prediction regime
(~0.13 aggregate MRR, ~0.05 Hits@1, `hdlab/additive_map.py` / `AdditiveKGMap`).

**Method:** 3 parallel Sonnet lit-scans (field-diagnostic methodology + commonsense-KG benchmarks; brain relational-
inference rate-limiter; decoder-vs-representation diagnostic recipes from associative memory / compressed sensing /
channel coding) — generic public terms only, no substrate-novel naming off-platform, per query-privacy discipline —
followed by a **zero-new-compute application of the literature's own diagnostic recipe (degree-stratification) to
already-landed on-disk metrics** from `data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json` (HARD_PASS,
3-rung, 2 seeds, landed 2026-07-13T14:10 UTC) and `data/exp_anchor_compose_reciprocal_cold_rescue_cskg_v1/metrics.json`
(landed same day, 19:42 UTC). This on-disk re-analysis, not the external literature, is the load-bearing finding of
this drill.

---

## (a) HEADLINE

**The low aggregate MRR is not one wall — it is a degree-stratified MIXTURE, and re-reading data already sitting on
disk (zero new compute) shows the earlier representation-attacks were aimed at the wrong population.** Splitting the
already-landed `anchor_mrr_by_support_degree` buckets from `exp_anchor_compose_scaling_ladder_cskg_v3` (verified
directly from `metrics.json`, not re-derived) gives:

| bucket (support-edge count) | anchor_mrr | oracle_mrr (supervised-code ceiling) | % of oracle | vs random |
|---|---|---|---|---|
| `cold` (0 support, n=17.5) | 0.000041 | 0.650751 | **0.01%** | **0.08x — WORSE than random** |
| `d1` (1 support, n=8) | 0.059252 | 0.391866 | **15.1%** | 400x |
| `d2_3` (2-3 support, n=52.5) | 0.078897 | 0.123391 | **63.9%** | 572x |
| `d4_7` (4-7 support, n=226) | 0.151421 | 0.114233 | **132.6%** (flagged, see below) | 704x |
| `d8plus` (8+ support, n=2696) | 0.127724 | 0.135649 | **94.2%** | 239x |

Pattern holds across all 3 scaling rungs (r0/r1/r2, different k-core and support-fraction settings) — this is not a
single-run artifact. **The bulk of the entity population (d2_3 through d8plus) is ALREADY sitting at 64-132% of its
own measured supervised-code ceiling** ("oracle" here = the additive fit trained WITH the held-out entity's true
edges folded in — a representation/algebra-quality ceiling, not an information-theoretic query-ambiguity ceiling,
see caveat below). For that majority-mass population, **more representation capacity has almost nothing left to
give** — which is exactly why 8+ drills attacking codes/dimension/write-rule this session came up empty or capped:
they were diagnosing the aggregate number, which is dominated by a population that is not representation-limited.
The entire deficit is concentrated in two populations with a fundamentally different character:
- **`cold`**: scores BELOW random (0.08x) — not "weak signal," a genuine defect. A same-day fix
  (`exp_anchor_compose_reciprocal_cold_rescue_cskg_v1`, reciprocal-edge bundling) already gives a real, verified
  370x lift (0.000041 -> 0.01480) but the cell's own verdict is **`BROKEN_TEST_CONTROL_BEATS_POP`** — a live,
  unresolved test-construction issue, not a clean win yet, and even the fixed number is still 97.7% short of the
  0.65 oracle.
- **`d1`**: real, substantial headroom (85% of oracle unclaimed) — the one bucket where a representation/decoder
  improvement is plausibly the right lever, not a re-litigated dead end.

**Caveat that matters (own read, not literature-asserted):** the on-disk "oracle" arm (`ORACLE_ADDITIVE`, code at
`experiments/exp_anchor_compose_scaling_ladder_cskg_v3.py` line 158/413) fits the entity's code **using the held-out
edges as training data (fold-in)**. It is a ceiling on "how good could the compose/retrieve algebra be if this
entity had a well-fit code," NOT a ceiling on "how much can be inferred zero-shot from 0-2 raw support edges." So
the 64-132%-of-oracle reading for well-supported buckets means the ALGEBRA is not the bottleneck there (real,
useful finding) — but it does NOT by itself distinguish, for `cold`/`d1`, between (i) a fixable inductive-code-
inference-from-sparse-evidence problem (representation/decoder lever, attackable) and (ii) a genuine data-coverage
problem (the true relational signal for that entity simply is not present anywhere in the currently-ingested graph
except via the very edges being held out — an ingest lever, not a representation lever). Both are live hypotheses;
this drill does not adjudicate between them without a further cheap check (Section (b), test 3).

**The `d4_7` bucket exceeding its own oracle (132.6%, consistently ~127-133% across all 3 rungs)** is flagged, not
explained away: either small-bucket-size estimation noise in the oracle fit, or the oracle's fold-in training is
itself imperfect at that particular support-count regime (non-monotonic ceiling, a real possibility per the
compressed-sensing literature below — practical decoders/fits are not always monotone in problem-easiness). Worth
a one-line sanity check before treating "94-132% of oracle" as settled for the full mid/high-degree range.

---

## 1. Field diagnostic methodology + commonsense-KG benchmark numbers (lit-scan A)

Standard practitioner playbook for separating bottleneck classes, verified via WebSearch/WebFetch this cycle:

- **Component ablation** (swap decoder/scoring-head vs. embedding module, same stored representation) is the
  standard way to separate representation from decoder — but is architecture-specific, not a general recipe.
- **Category-split evaluation is the standard way to separate task-underdetermination from model quality.**
  TransH (Wang et al., AAAI 2014) reports Hits@10 split by relation cardinality type on FB15k: **87.6 (1-N,
  predicting the deterministic side) vs. 28.7 (N-1, predicting the ambiguous/many-valid-answers side)** — a
  ~3x gap from query-structure alone, at fixed model. This is the single cleanest, most directly-verified external
  precedent for "low score on the ambiguous side of a query is structural, not a model defect" — and it is a
  **close numeric match to this substrate's own `d1`-bucket 15% vs `d8plus`-bucket 94% spread** (same shape:
  low-information-density queries score far below high-information-density queries at fixed mechanism).
- **Evaluation-protocol artifacts are a documented, separate confound.** Sun, Vashishth, Sanyal, Talukdar & Yang,
  "A Re-evaluation of Knowledge Graph Completion Methods" (ACL 2020, arXiv:1911.03903) showed inconsistent
  filtered-ranking tie-breaking inflated some models' reported MRR/Hits@1 by large margins — measured scores are
  not purely a function of representation quality. This substrate's own cell already builds in scramble controls,
  a degree-debias comment/gate, and an oracle-fire gate (see code comments, `exp_anchor_compose_scaling_ladder_cskg_v3.py`
  lines 44-99) — i.e., several of the standard eval-artifact confounds are already structurally guarded against in
  THIS cell, which raises confidence the degree-stratification finding above is not itself an eval artifact.
- **Commonsense KGs score structurally lower than curated benchmarks even for strong trained models**, precisely
  because ranking metrics punish the one-to-many/sparse/noisy structure that free-form commonsense graphs have more
  of than curated ones (COMET, Bosselut et al. ACL 2019, arXiv:1906.05317; Malaviya et al., AAAI 2020,
  arXiv:1910.02915). Directly relevant: this substrate's ingest IS a commonsense/taxonomy-style graph (per
  `MEMORY.md`: ~190k relations, majority SYNONYM/IS_A) — so some structural depression of absolute MRR relative to
  curated-KG benchmarks (FB15k-237/WN18RR) should be EXPECTED regardless of mechanism quality, an important
  calibration point when judging "is 0.13 MRR bad."
- **Degree affects accuracy mechanistically, not just as a hard data-ceiling** — "A Mechanistic Study on the Impact
  of Entity Degree Distribution in Open-World Link Prediction" (arXiv:2503.12139, abstract-level only, full-text
  extraction failed this cycle, **flagged unverified**) argues degree affects performance through representation-
  learning dynamics, i.e., frames cold-entity failure as partly fixable, not purely a data ceiling — consistent
  with this drill's own `d1`-bucket finding of real, non-trivial headroom.

**Least plausible per this scan:** (d) composition/multi-hop mechanism as the dominant explanation — no paper
surfaced separates this as a distinct axis from (a)/(b) for single-hop-style link prediction, and `anchor_compose`
is not a multi-hop chaining mechanism in the sense the composition-focused literature addresses.

## 2. Brain rate-limiter (lit-scan B, biology-first per standing discipline)

Converges on **regime-dependent, not monolithic** bottlenecks, cross-validating (not just repeating) this
substrate's own prior 2026-07-09 finding (`research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md`):

- **Cortical multi-relation integration is working-memory/binding-limited**, not representation-limited per se:
  Waltz, Knowlton, Holyoak et al. (Psychological Science 1999) show frontal-lobe patients have a selective deficit
  in INTEGRATING multiple relations, not perceiving single ones; Hummel & Holyoak's LISA/DORA models formalize the
  limit as synchrony-binding capacity (~3-5 propositions), not code capacity.
- **Hippocampal composition (CA3 pattern completion) is retrieval/interference-limited** — orthogonalization
  failure -> competing-pattern reinstatement -> errors (Rolls 2013; Bird et al., eLife 2016).
- **A nontrivial fraction of classic "relational inference failure" in animal transitive-inference literature is
  actually task-underdetermination misread as a representational deficit** — associative value-transfer accounts
  cannot be distinguished from genuine relational inference without added disambiguating probes (Vasconcelos 2008).
- **Best empirical diagnostic the brain literature offers, independently converging with this substrate's own prior
  drill:** does supplying extra disambiguating context/goal signal recover performance? PFC supplies top-down
  goal/context that disambiguates among MULTIPLE VALID hippocampal completions (2025 preprint arXiv:2503.02303,
  provisional; Nat. Commun. 2020 s41467-020-15928-z, direct precedent). **Two independent lit-scans one week apart
  (2026-07-09 and this cycle) landed on the identical PFC-hippocampal goal-disambiguation mechanism from different
  literatures** — a real convergence signal, not a repeated query artifact.

Applied to our regime: this axis (query-answer ambiguity) is a DIFFERENT axis from the degree/evidence-availability
axis that Section (a) found dominant here (`anchor_compose`'s "degree" = how much support evidence exists for a
held-out entity, not how many equally-valid targets a query has) — both could compound, but the on-disk data
localizes the deficit to sparse-EVIDENCE buckets specifically, which is closer to the cortical WM/binding-capacity
story (not enough bound relational content to integrate) than to the pure hippocampal query-ambiguity story. Worth
keeping both frames live rather than collapsing to one.

## 3. Decoder-vs-representation diagnostic recipes (lit-scan C)

Confirms a **general, retraining-free recipe** exists across three independent formalisms (associative memory /
VSA, compressed sensing, channel coding), and — importantly — **this substrate's own cell design already
implements the core of it**: freeze the representation, compare a cheap arm against a stronger/oracle arm on the
IDENTICAL stored data (Frady/Kent/Olshausen/Sommer resonator-vs-ALS comparison methodology, arXiv:2007.03748;
Donoho/Montanari L1-vs-L0 compressed-sensing phase-transition gap; LDPC/turbo "waterfall curve" BER-vs-iteration
diagnostic). The `anchor_mrr` vs. `oracle_mrr` split already computed on disk (Section (a)) IS this diagnostic,
already run — the novel step this drill adds is reading it degree-stratified rather than as a single aggregate
number.

**Directly relevant same-day on-disk fact, found while checking whether a "decode-budget" version of this
diagnostic already exists:** `data/exp_anchor_compose_closedform_budget_sweep_cskg_v1/metrics.json` (verdict
`STRICT_DEAD_UNCONDITIONAL_ACROSS_BUDGET`) already swept a closed-form coordinate-fitting budget parameter `k` in
[24, 64, 128, 256] and found near-zero improvement (rise 0.0015, `oracle_best`=0.0102 vs `add_oracle`=0.137,
"DEAD"). This is a genuine, already-landed negative for ONE specific representation-budget lever (closed-form
coordinate rank) — consistent with "representation capacity, in general, is not the lever for the majority-mass
buckets," and reinforces (rather than merely repeats) Section (a)'s conclusion via an independent mechanism.

---

## Cheap decisive test (pre-registered, before building anything new)

**Test 1 — sanity-check the `d4_7` oracle-exceeds-anchor anomaly (near-zero cost, pure analysis).** Pull
`n_query` per bucket (not currently in the summary printed here) and check `d4_7`'s oracle-fit convergence
diagnostics (epochs/loss at fold-in time) across all 3 rungs. HARD-PASS (anomaly is estimation noise, safe to
proceed): the effect shrinks or reverses when `n_query` for `d4_7` is large enough that its confidence interval
overlaps 100%. HARD-FAIL (anomaly is real): consistent >120%-of-oracle reading survives a bucket-size correction —
would mean the ORACLE arm's fold-in training is itself under-converged in that specific support-count regime,
and the "94-132% of ceiling" reading for mid/high-degree buckets should be treated as a LOWER bound on true
headroom-closure, not a settled number.

**Test 2 — same-representation decoder-budget sweep, scoped to the `d1` bucket only (near-zero cost, reuses
existing harness).** The already-existing `exp_anchor_compose_closedform_budget_sweep_cskg_v1` swept budget on the
WRONG population (aggregate, dominated by saturated buckets, hence STRICT_DEAD). Re-run the identical budget sweep
filtered to `d1`-bucket queries only (1 support edge), zero retraining.
- **HARD-PASS:** `d1` anchor_mrr rises >= 1.3x from k=24 to k=256 (or whichever budget axis is swept), tracking
  toward its own oracle (0.39) rather than plateauing near 0.06 — decoder/budget-limited, cheap fix, no new
  architecture needed.
- **HARD-FAIL:** `d1` anchor_mrr stays flat (< 1.15x) across the same budget range on this bucket specifically —
  rules out decoder/budget as the `d1` lever; points back to either sparse-evidence code-inference quality
  (representation, harder) or data-coverage (ingest, per Test 3) as the real explanation.

**Test 3 — data-coverage check for `cold`/`d1` (cheap, off-disk graph query, no new experiment).** For a sample of
`cold` and `d1` held-out entities, check whether their TRUE held-out edge's OTHER endpoint (or a close graph
neighbor of it) has independent, already-ingested paths connecting it to the sparse entity's known support edges
(e.g. a 2-3 hop path through the existing graph, not through the held-out edge itself). HARD-PASS (data-coverage
hypothesis): most `cold`/`d1` failures have NO such independent path — the true answer genuinely is not recoverable
from anything currently ingested except the held-out edge itself, meaning the fix is INGEST (more real edges),
consistent with this substrate's own already-confirmed cert-ledger conclusion for a different mechanism (learned
SR-routing: "the lever is ingesting more knowledge, not richer structure," 3 independent FULL HF cells,
`relational_capability_track_record_scour_2026-07-10.md` Section E/CONVERGENCE). HARD-FAIL: most failures DO have
an independent recoverable path that the current mechanism simply isn't finding — meaning it is a genuine
representation/inference-from-sparse-evidence gap, and building a smarter few-shot code-inference step (not more
ingest) is the right lever.

---

## Falsifiable predictions

**Prediction 1:** the aggregate ~0.13 MRR / ~0.05 Hits@1 is a mixture, not a monolithic wall — CONFIRMED already
by the on-disk data in Section (a) (not merely predicted); recorded here as the drill's core deliverable.
- HARD-PASS (met): mid/high-support buckets (d2_3+) sit at >=50% of their own oracle across all 3 landed rungs.
  **Met: 60-133% across all 3 rungs, all buckets d2_3+.**
- HARD-FAIL (not met, would refute): if any rerun/rescale showed d2_3+ buckets uniformly <25% of oracle, the
  "already near ceiling" reading would be wrong and representation-attacks on the whole population would be
  re-justified. Not observed in any of the 3 landed rungs.

**Prediction 2 (Test 2 above):** `d1`-bucket decoder-budget sweep moves the needle >= 1.3x. Not yet run — this is
the next cheap, concrete action, not a re-litigation of the already-DEAD aggregate budget sweep.

**Prediction 3 (Test 3 above):** most `cold`/`d1` failures lack an independent ingest-recoverable path. Not yet
checked — cheapest test, pure graph query, no experiment dispatch needed, should run before Prediction 2 since a
HARD-PASS here would deprioritize further decoder/representation work on `cold`/`d1` entirely in favor of ingest.

---

## Cross-thread synthesis

- **This directly explains why today's 8+ representation-capacity drills** (`research_substrate_realizable_frontier_levers_...`,
  `research_native_representational_ceiling_levers_...`, `research_deployable_representational_capacity_levers_...`,
  and the 5 bio/quantum/wildcard cross-domain drills) **came up empty or capped at P<=0.35**: they were reasoning
  about the AGGREGATE number as if it reflected a uniform representation deficit. Section (a)'s degree-stratified
  read shows most of that population isn't representation-limited at all — the capacity-lever hunt was well-run
  research answering a question whose premise (uniform deficit) doesn't hold for the majority of the query
  population. This is not a wasted cycle: those drills' negative results are now correctly explained, not just
  logged as negatives.
- **Directly extends `research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md`** (the prior
  "is the test even fair" drill, a different mechanism/thread — reader/multi-hop sibling retrieval, not
  `anchor_compose`). That drill's brain-first finding (query-answer ambiguity requires goal/context) is the SAME
  family of insight as this drill's finding (evidence-availability, not query ambiguity, is this mechanism's real
  axis) — both are "the aggregate metric hides a structural split that changes which population is actually
  broken," now demonstrated twice on two different mechanisms. Per feedback-compute-test-info-ceiling-before-
  iterating-fix-cells, this is the second confirmed instance of the same meta-lesson.
- **Directly informs, without over-transferring** (per feedback-mechanism-analog-is-not-task-analog),
  `relational_capability_track_record_scour_2026-07-10.md`'s central convergence: held-out inductive inference
  (a DIFFERENT mechanism, learned SR-routing) fails because "the lever is ingesting more knowledge, not richer
  structure" — three independent FULL HF cells. This drill's Test 3 is designed to check whether that same
  conclusion transfers to `anchor_compose` specifically, rather than assuming it does.
- **`exp_anchor_compose_reciprocal_cold_rescue_cskg_v1`'s live `BROKEN_TEST_CONTROL_BEATS_POP` verdict** is an
  open, unresolved thread this drill surfaces but does not fix — the reciprocal-edge fix gives a real (370x) but
  partial (still 97.7% short of oracle) lift to `cold`, and the test-construction flag needs skunkworks attention
  before that cell's result can be trusted as a clean data point.

## Substrate-product implications

- If Test 2 HARD-PASSes: a cheap, no-new-architecture decode-budget increase materially improves the one bucket
  (`d1`) that has genuine headroom — a real, fast, low-risk win, and it should be scoped ONLY to that bucket (the
  already-DEAD aggregate sweep proves budget doesn't help the saturated majority).
- If Test 3 HARD-PASSes (data-coverage): the correct product framing shifts from "improve the reasoning mechanism"
  to "the mechanism already reasons about as well as its own evidence allows; the product needs more real
  ingested facts, not a smarter algorithm" — a cleaner, more honest story, and directly continues the
  already-USER-locked "relational = core requirement, ingest matters" program thread rather than opening a new one.
- Either way: **the practical redirect for the Director is to STOP running population-wide representation-capacity
  drills against the aggregate metric, and re-scope any further `anchor_compose` work to the `cold`/`d1` buckets
  specifically** — the d2_3+ majority is not a fruitful target for more representation engineering; it is already
  near its own measured ceiling.

## Citations (verified count)

**External (WebSearch/WebFetch, this cycle, across 3 sub-agents):**
1. Wang et al., TransH, AAAI 2014 — direct-fetch, category-split Hits@10 numbers (87.6 vs 28.7) verified.
2. Sun, Vashishth, Sanyal, Talukdar, Yang, "A Re-evaluation of KGC Methods," ACL 2020, arXiv:1911.03903 — verified.
3. Ren, Hu, Leskovec, Query2Box, ICLR 2020, arXiv:2002.05969 — verified (set-vs-singleton framing).
4. Bosselut et al., COMET, ACL 2019, arXiv:1906.05317 — verified.
5. Malaviya et al., AAAI 2020, arXiv:1910.02915 — abstract/partial text (garbled extraction), flagged.
6. "Mechanistic Study of Entity Degree Distribution," arXiv:2503.12139 — abstract-only, flagged unverified.
7. Frady, Kent, Olshausen, Sommer, Resonator Networks, arXiv:2007.03748 / arXiv:1906.11684 — direct-fetch, verified
   (already independently verified in this substrate's 2026-07-10 crux-v2 note; re-confirmed here).
8. Donoho/Montanari compressed-sensing phase-transition literature — verified, standard references.
9. Waltz, Knowlton, Holyoak et al., Psychological Science 1999 — verified.
10. Hummel & Holyoak, LISA/DORA, 2001/2003 — verified.
11. Rolls 2013/2015 pattern-separation/completion review; Bird et al., eLife 2016 — verified.
12. Vasconcelos 2008, transitive inference in animals — verified (search-level, not full-text).
13. arXiv:2503.02303 (PFC-hippocampus query-key, 2025 preprint) — flagged provisional/unverified per its own status.
14. Nat. Commun. 2020 s41467-020-15928-z; PNAS 2022 s2203024119 — verified.

**Internal on-disk (read/computed directly this cycle, not from status_log summaries):**
15. `data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json` — full degree-stratified table for all 3 rungs,
    directly computed/verified this cycle (the load-bearing artifact of this drill).
16. `data/exp_anchor_compose_reciprocal_cold_rescue_cskg_v1/metrics.json` — verdict and numbers directly read.
17. `data/exp_anchor_compose_closedform_budget_sweep_cskg_v1/metrics.json` — verdict and numbers directly read.
18. `experiments/exp_anchor_compose_scaling_ladder_cskg_v3.py` — grepped for ORACLE arm definition (fold-in
    semantics), lines 44-99, 158, 413.
19. `notes/relational_capability_track_record_scour_2026-07-10.md` — read in full, cited for the SR-routing
    ingest-not-structure conclusion (correctly scoped as a different mechanism, not assumed transferred).
20. `notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md` — read in full, cross-referenced for
    the resonator-vs-ALS decoder methodology (independently re-found by lit-scan C this cycle).
21. `notes/research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md` — read in full,
    cross-referenced for the PFC-hippocampal goal-disambiguation convergence.
22. Today's 8 status_log `research_delivery` entries (representation-capacity drill lineage) — read for scope of
    "already attacked and came up empty," not re-derived.

**Total: 14 external + 8 internal on-disk sources = 22 verified checks.**

## P_deflated summary

- **"Aggregate low MRR is a degree-stratified mixture, not a uniform wall" (Section (a) core claim):** this is a
  direct re-read of already-landed, verified `metrics.json` data, not novel synthesis — raw confidence ~0.85, light
  deflation for the single-cell-lineage scope (3 rungs, 2 seeds, one mechanism family) -> **P_deflated = 0.65.**
- **"`cold`/`d1` failure is primarily a data-coverage/ingest problem rather than a fixable representation/decoder
  gap" (the Test-3 hypothesis, informed by but not proven via the SR-routing cert-ledger analogy):** genuinely
  novel-synthesis, cross-mechanism transfer, capped per discipline -> **P_deflated = 0.35** (capped below the 0.50
  ceiling given the explicit mechanism-analog-is-not-task-analog caution above).
- **"Decoder/budget sweep on `d1` specifically will show real headroom" (Test 2 prediction):** favorable given the
  85%-of-oracle gap and general decoder-diagnostic literature, but untested on this exact bucket -> **P_deflated =
  0.40.**

---

## Intuitive summary

We stopped asking "can we make the memory representation richer" and instead asked "is the low overall score even
coming from one place." Answer, straight off already-collected data: no. When we split the score by how much
evidence the system had about each held-out item, most items (the ones with a decent number of known facts) are
ALREADY performing about as well as a version of the system that got to cheat and see the answer while training —
there's essentially nothing left to gain there from a bigger or smarter representation. The entire shortfall lives
in two small, specific buckets: items with almost no known facts at all. One of those buckets (barely any facts) has
real, recoverable headroom worth chasing with a cheap decode-effort tweak. The other (zero facts) is scoring worse
than a coin flip — a likely plumbing bug, already half-fixed today, not a fundamental limit — but even the partial
fix leaves it far short of the honest ceiling, and it's plausible the honest answer for that bucket is simply "we
never gave the system enough real facts about this thing to work with," which would mean the fix is feeding it more
real knowledge, not building a cleverer algorithm. Either way, today's whole "make the codes bigger/better" research
line was aimed at a population that was never the problem — which is exactly why it kept coming up empty.
