# Research note: the 4th signal's CORRECT function — retrieval/attention prioritization vs. active-reading acquisition-order

**Date:** 2026-07-16
**Trigger:** `exp_importance_downstream_reach_ingest_prioritization_real_codex_v1` HARD_FAILED importance/downstream-reach
as a foundation-GROWTH-ORDER signal on real CoDEx (`data/exp_importance_downstream_reach_ingest_prioritization_real_codex_v1/metrics.json`
— `beats_both: false`, `fails: true`, margins negative vs. both frequency and random order) despite the signal being
genuinely real and popularity-decorrelated (`part1_separability`: `importance_btwn_unique_variance=0.867`,
`separability_tier: SEPARABLE`, `max_pop_corr=0.220`). Per the all-3-brain-signals-load-bearing lock, a signal that
looks inert is presumed an implementation/role-mismatch bug, not a dead signal — this drill leads with biology to
find where importance's genuine role actually lives, tests two hypotheses (retrieval/attention allocation vs.
active-learning-what-to-read-next), and recommends the smallest decisive cell. Method: 3 parallel Sonnet lit-scans
(generic terms only, no substrate specifics off-platform) — (1) value-based attention/priority-maps/precision-
weighting/retrieval-competition, (2) active-learning/curiosity/value-of-information + the redundancy failure mode,
(3) graph-centrality-as-retrieval-relevance in classical IR/KGQA — cross-checked against
`research_consolidation_function_inventory_schema_reorg_2026-07-16.md` (keep-gate framing, pruning not-needed for
an unbounded store) and `research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md` (importance as
4th axis = downstream-reach/value-of-information, unique-variance finding first surfaced there).

---

## HEADLINE

**The already-run HARD_FAIL cell *is* hypothesis (b) — active-learning acquisition-ordering — already tested and
already failed, and the literature independently explains the failure mechanism (naive centrality-greedy selection
without a diversity/redundancy correction is a well-documented anti-pattern in active learning, not evidence that
value-of-information is meaningless). Hypothesis (a) — retrieval/attention-time prioritization — is a mechanistically
DIFFERENT question (ranking/surfacing among already-stored facts at USE time, not deciding acquisition ORDER of
not-yet-stored facts) that has NOT been tested on this substrate, is well-precedented in classical information
retrieval (PageRank/HITS/personalized-PageRank exist specifically because graph centrality is a textbook-strength
retrieval-relevance signal, separate from crawl-order), and is directly reachable with near-zero new compute by
reusing this cell's own already-fitted resolvent/importance machinery against the held-out test set as a
retrieval-relevance ground truth instead of a growth-curve ground truth. Recommended verdict: (a) is the correct,
load-bearing function for a glass-box substrate with an unbounded exact store; (b) is not abandoned but is
deprioritized behind a specific, named fix (diversity-corrected reselection) that should only be attempted if (a)
also fails. P_deflated (verdict + recommended cell, novel-synthesis capped) = 0.44.**

---

## (a) RETRIEVAL / ATTENTION — biology-first

**Value/salience gates retrieval-time competition, not just encoding, and this is real, dissociable, multi-literature
evidence (deflated confidence 0.55 from lit-scan, further deflated to 0.45 for cross-substrate extrapolation):**

- **Value-driven attentional capture** (Anderson, Laurent & Yantis, *PNAS* 2011; Anderson 2013, *PLOS ONE*, "Learned
  Value Magnifies Salience-Based Attentional Capture"): reward-paired stimuli involuntarily win attentional
  competition on LATER, reward-irrelevant trials — an explicitly retrieval/selection-time effect on already-learned
  associations, not a re-description of encoding strength.
- **Priority maps** (Fecteau & Munoz 2006, *Trends Cogn Sci* 9:382; Klink, Jentgens & Lorteije 2014, *J Neurosci* 34:
  13867): parietal/frontal/superior-colliculus circuits sum value + goal-relevance + physical salience into a single
  competition arena that decides what wins attention NOW — a downstream, use-time allocation mechanism, separate
  from whatever process laid down the value association in the first place.
- **Precision-weighting / attention-as-precision** (Feldman & Friston 2010, *Front Hum Neurosci* 4:215, verified full
  text): attention is formally the PRECISION (inverse variance) assigned to a prediction-error/hidden-cause at
  INFERENCE time — higher precision means a hidden cause dominates current belief-updating and gets represented more
  strongly RIGHT NOW, independent of how it was stored. (Contested: Friston's own later commentary on whether
  precision fully *is* attention is not universal consensus — flagged, not smoothed over.)
- **Retrieval-time utility over already-stored memories, the cleanest direct hit**: Mattar & Daw 2018 (*Nature
  Neuroscience* 21:1609, PMC6203620) formalize hippocampal replay/retrieval priority as **Gain x Need** — a utility
  computed over memories ALREADY in the store, to decide which to access first for planning. This is explicitly a
  retrieval-time prioritization function, structurally distinct from a consolidation/keep-gate.
- **Honest complication**: Cohen/Ranganath et al. 2022 (*Nature Communications*) find event centrality predicts BOTH
  encoding strength (hippocampal boundary response) AND later recall strength — the two functions are not always
  cleanly separable in the data even where they are separable in theory. Braun, Wimmer & Shohamy 2018 (*Nature
  Communications*) similarly shows reward *retroactively* reorganizes what gets consolidated, meaning value acts at
  BOTH consolidation and retrieval jointly in the best studies, not retrieval alone.

**Does downstream-reach predict retrieval relevance specifically? Strong adjacent-math precedent, not yet biology
per se:** Brin & Page 1998 (WWW7, canonical) and Kleinberg 1999 (*JACM*, canonical — HITS is explicitly computed on
a QUERY-INDUCED subgraph, making hub/authority score a retrieval-relevance metric BY CONSTRUCTION, with no crawl-
order claim at all). Olston & Najork 2010 (*Foundations and Trends in IR*, "Web Crawling") is the field's own
explicit statement that centrality-for-ranking and centrality-for-crawl-priority are TWO SEPARATE, historically
distinct optimization problems that happen to reuse the same score — direct, precedented support for treating (a)
and (b) as genuinely different questions rather than the same question asked twice. KGQA popularity-bias literature
(CR-LT-KGQA, arXiv:2403.01395, verified preprint) documents real query distributions concentrating on high-
degree/head entities, and personalized-PageRank/random-walk-with-restart is a mature, query-time-seeded relevance
mechanism in recommender systems and entity search (multiple 2020-2024 sources, verified). Lit-scan confidence for
this sub-claim: 0.75 (high — this is textbook classical IR, not novel synthesis at the general level; the extension
to THIS substrate's specific downstream-reach computation is what remains untested).

## (b) ACTIVE LEARNING / VALUE-OF-INFORMATION — biology-first, and why it already failed

**The already-run HARD_FAIL cell's `part2_foundation_growth` (order candidate facts by importance, measure
AUAC-of-accuracy-as-graph-grows toward a fixed budget) is precisely an implementation of hypothesis (b) — it is
value-of-information-guided acquisition-order, operationalized exactly as "reading this next unlocks the most."**
It lost to both frequency and random order (`margin_imp_freq_mean=-0.037`, `margin_imp_rand_mean=-0.091`,
`beats_both=false`). The literature independently and convergently explains why a NAIVE version of this specific
mechanism is expected to underperform, and this is a mature, textbook-level finding, not speculation:

- **BatchBALD** (Kirsch, van Amersfoort & Gal, NeurIPS 2019, arXiv:1906.08158, verified): states directly that
  greedy top-k acquisition by a per-item informativeness score "acquires similar and redundant points... sometimes
  performing worse than randomly acquiring data" — points near a high-scoring point score highly too, so pure
  greedy-by-score clusters selection on a correlated subset instead of covering the space.
- **Coreset active learning** (Sener & Savarese, ICLR 2018, arXiv:1708.00489, verified): the same failure mode for
  uncertainty-based selection, fixed by reframing as a coverage/facility-location objective instead of a per-item
  greedy score.
- **Submodular coverage theory** (Nemhauser-Wolsey-Fisher 1978; general submodular set-function literature): the
  near-optimality guarantee for greedy selection only holds when the OBJECTIVE ITSELF is submodular over the
  growing selected set — a static, per-item centrality score computed once (as in the HARD_FAIL cell's ordering) is
  not automatically submodular, so greedy-by-that-score forfeits the diminishing-returns structure needed for good
  coverage.
- **Graph-specific version, more inferential but consistent** (hierarchical graph sampling arXiv:2503.00860; ALINC
  arXiv:2606.04647): traversal/uncertainty sampling over-selects high-degree "core" nodes and under-represents
  low-degree "periphery," a documented redundancy/bias pattern consistent with (but not a direct proof of) "hubs are
  redundantly inferable via many alternate paths, so acquiring them first buys less marginal coverage than acquiring
  periphery first."
- **Biology's own fix, and the reason it doesn't transfer to a naive greedy score**: Gottlieb, Oudeyer, Lopes &
  Baranes 2013 (*Trends Cogn Sci* 17:585) and Poli et al. 2022 (PMC9194910, children) show biological curiosity is
  consistently a TWO-TERM signal — expected learning progress x novelty/habituation — never a pure informativeness-
  greedy score. Habituation to repeated/redundant stimuli is the load-bearing diversity correction biology builds in
  by default; the HARD_FAIL cell's importance-order arm had no equivalent term.

**Calibrated confidence that redundancy/no-diversity-correction is the correct, well-precedented explanation for the
already-observed HARD_FAIL: 0.55** (lit-scan's own number; this is the standard textbook active-learning story, but
no source in the scan directly demonstrates the SAME collapse for a graph-centrality-flavored score specifically, so
kept at moderate rather than high confidence).

**Verdict on (b): tested, failed, and the failure has a named, plausible, precedented mechanism (redundancy) —
but this does NOT mean (b) is definitionally wrong for this substrate, only that the specific naive-greedy
implementation already run is a known anti-pattern.** A diversity/coverage-corrected re-attempt (e.g. facility-
location or degree-decorrelated marginal-coverage scoring instead of raw top-k by centrality) is a legitimate,
specific, named follow-up — but it is NOT this drill's primary recommendation, because (a) is cheaper, untested, and
does not require re-fighting a documented anti-pattern from scratch.

## (c) Which is load-bearing for THIS substrate, and the recommended cell

**Brain-check on why the biology's answer differs from a naive read of "importance = keep gate":** the prior
consolidation-inventory note already established that keep/prune-style gating is NOT-NEEDED for an unbounded exact
store (no capacity pressure to relieve). This drill's two-hypothesis split shows the SAME logic applies again, one
level up: biological value/salience machinery genuinely serves BOTH a write-time role (partially, per the mixed
Cohen/Ranganath and Braun findings above) AND a distinct, well-evidenced retrieval-time role (Mattar & Daw's
Gain x Need, priority maps, value-driven capture) — and for an architecture that has already removed the
capacity-driven NEED for aggressive write-time gating, the retrieval-time role is the one that remains genuinely
load-bearing, because retrieval/reasoning on this substrate is NOT unbounded the way storage is: multi-hop
resonator completion, beam width in iterated argmax, and any bounded reasoning/context window are all real, finite
resources at USE time, exactly the kind of competitive-allocation problem priority maps and Gain x Need retrieval
utility exist to solve in the brain. **This is the correct-function verdict: (a) retrieval/attention allocation,
not (b) active-reading acquisition-order, is where importance/downstream-reach genuinely pays for this substrate.**

**Recommended cell (pointer-only; smallest decisive test, near-zero new compute — reuses this cell's own already-
built machinery against a different, already-available ground truth):**

Reuse `experiments/exp_importance_downstream_reach_ingest_prioritization_real_codex_v1.py`'s already-computed
per-entity importance signal (the `importance_btwn_orth` degree-orthogonalized variant — same primary metric already
validated as `SEPARABLE` in `part1_separability`) and the SAME real CoDEx train/test split already loaded by
`load_dataset`/`read_triples`. Do NOT re-run the growth-order simulation. Instead:

1. **New ground truth, zero new acquisition**: for each entity, `test_query_count` = number of appearances as head
   or tail across the `n_test=3656` held-out test triples (already on disk via the existing data loader — literally
   a groupby-count, no new labeling, no new data).
2. **Test**: does `importance_btwn_orth` (or a freshly computed personalized-PageRank / SR-resolvent-style score
   over the ADMITTED train graph, reusing `sr_foundation`/`_sr_M`) predict `test_query_count` with INCREMENTAL
   variance beyond `[degree, rel_freq]` — reuse `separability_analysis`'s exact OLS-residual/unique-variance method
   (already built, already validated on this exact dataset for a different target variable).
3. **Degree-orthogonalization discipline is mandatory** (per the KGQA popularity-bias literature above, raw
   query-frequency will almost certainly correlate strongly with raw degree — this is the expected, non-surprising
   part; the decisive question is whether downstream-reach adds anything BEYOND that, exactly the same discipline
   already proven out in `part1_separability`/`part3_popularity_neutrality` of the HARD_FAIL cell).

**Falsifiable predictions (deflated per lit-scan calibration; HARD-PASS/HARD-FAIL mandatory):**

- **HARD-PASS:** unique/incremental variance of `importance_btwn_orth` on `test_query_count`, controlling for
  `[degree, rel_freq]`, is >= 0.15 (partial R², same OLS-residual method as `part1_separability`'s
  `unique_variance` computation) AND top-tertile-by-importance entities show >= 15 percentage points higher
  test-appearance rate than bottom-tertile entities AT MATCHED degree bins (reuse `degree_matched_order`, already
  built). This would mean downstream-reach carries genuine, non-popularity retrieval-relevance signal — directly
  actionable as a ranking/beam-allocation weight at query time, not merely a redundant restatement of popularity.
- **HARD-FAIL:** the degree/rel_freq-residualized correlation between `importance_btwn_orth` and `test_query_count`
  is < 0.05, OR degree-matched arms show no separation in test-appearance rate — meaning retrieval relevance IS
  just popularity in disguise for this substrate, and the correct, honest product move is to use raw
  degree/frequency directly as the retrieval-priority signal with no separate downstream-reach machinery for this
  purpose either. This is the pre-registered "importance is genuinely low-value here too" outcome the task asked
  to watch for honestly — it would mean NEITHER (a) NOR (b) pays, and importance's only remaining role is the
  already-established separability finding itself (a real, distinct, measurable quantity) without yet finding
  ANY use for it on this substrate — a legitimate, valuable, fully negative result, not a failure to search hard
  enough.
- **MIDDLE (plausible modal outcome):** partial correlation 0.05-0.15 — real but modest incremental signal.
  Route to a v2 that tests the HEAVIER but more decisive version: does surfacing high-downstream-reach facts
  FIRST within a bounded multi-hop retrieval width (reusing `sr_foundation`'s resolvent-AUROC machinery under a
  fixed retrieval budget analogous to the HARD_FAIL cell's `budget_grid`, but applied to RETRIEVAL width per query
  rather than ingestion order) improves downstream answer accuracy vs. popularity-first or random-first ranking —
  this is the genuine "attention allocation during reasoning" test, more expensive but more directly product-
  relevant than the cheap correlational test above.

**Pre-registered HARD-FAIL localization guidance:** if the cheap test HARD-FAILs, do not conclude "importance is
useless, drop the signal entirely" — the separability finding (`unique_variance=0.867` vs. popularity/schema-
fit/recurrence) still stands as a real, measured, distinct quantity; what would be closed is specifically "importance
has no additional predictive value for retrieval-priority beyond raw popularity," which is a narrower and more
useful claim than "importance is dead." Distinguish this from the redundancy-based (b) HARD_FAIL, which was about
ACQUISITION order, not retrieval order — the two failures would have different, independently-informative
implications if both occur.

---

## Cross-thread synthesis

- Directly extends, does not redo, `exp_importance_downstream_reach_ingest_prioritization_real_codex_v1`
  (`data/exp_importance_downstream_reach_ingest_prioritization_real_codex_v1/metrics.json`): that cell tested
  hypothesis (b) exactly and HARD_FAILed it; this note (i) explains the failure mechanism via independent
  literature (redundancy/no-diversity-correction, a well-precedented active-learning anti-pattern, not evidence
  importance is meaningless) and (ii) identifies hypothesis (a) as an untested, mechanistically distinct, cheaper,
  better-precedented alternative reusing the SAME cell's machinery against a different ground truth.
- Directly reconciles with `research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md`: that note
  first proposed downstream-reach as a "4th signal" analog of EFE's parameter-level epistemic value / Schmidhuber
  learning-progress, explicitly flagging it as untested on this substrate's coordinate geometry (P=0.40). This note
  is the direct empirical follow-through that note called for, and narrows the open question from "is downstream-
  reach a genuine 4th signal" (that note) to "which USE of the now-confirmed-separable signal is load-bearing"
  (this note) — a real narrowing, not a restatement.
- Consistent with `research_consolidation_function_inventory_schema_reorg_2026-07-16.md`'s core method (biology
  decomposes a seemingly-unitary function into multiple sub-functions with different triggers/currencies, each
  scored independently as COVERED/GAP/NOT-YET-NEEDED) — applied here to "importance" itself: encoding-gate role
  (not-needed, per that note's a5 + the growth-order HARD_FAIL), retrieval/attention role (this note's (a),
  recommended), active-reading/acquisition-order role (this note's (b), tested-and-explained-failure, not
  abandoned but deprioritized).
- Consistent with the two-frontiers framing (brain-faithful world first): the recommended cell tests the
  brain-faithful NEED (does downstream-reach predict genuine retrieval-relevance, as the Mattar-Daw/priority-map/
  PageRank literature would predict) before assuming any native-substrate shortcut: an unbounded exact store removes
  the WRITE-time pressure the brain solves with keep-gates, but does NOT remove the READ-time competitive-allocation
  problem the brain solves with priority maps and Gain x Need retrieval utility — multi-hop resonator completion,
  iterated-argmax beam width, and any bounded reasoning/context budget are all still finite at query time on this
  substrate, exactly where the brain's retrieval-prioritization machinery, not its encoding-gate machinery, is the
  correct biological analog to import.

## Substrate-product implications

1. **If the recommended cell HARD-PASSes**: the product story becomes "the foundation surfaces the facts that
   matter most to a query first, using a computable, zero-external-input signal reused from already-built
   machinery" — directly useful for any bounded-width retrieval, multi-hop beam allocation, or context-budget
   ranking problem, and a genuinely different, additive claim from "the foundation never forgets" (exact-write) or
   "the foundation integrates new facts efficiently" (schema-fit write-time gate).
2. **If it HARD-FAILs cleanly (redundant with popularity)**: this is still a useful, actionable negative — it means
   raw degree/frequency, already trivially available with zero extra machinery, is the correct retrieval-priority
   signal, and downstream-reach's separability finding (real, but so far unused) should not be over-invested in
   a bespoke retrieval-ranking role. Follow the evidence: this is the honest "importance may be low-value here too"
   outcome the task explicitly asked to watch for, and it would be a legitimate, complete answer, not an
   unfinished search.
3. **(b)'s failure is not closed forever**: if (a) also fails, the next legitimate move is NOT to abandon
   value-of-information-guided acquisition but to retry it with a NAMED, specific fix — diversity/coverage-corrected
   selection (facility-location or degree-decorrelated marginal-coverage score instead of raw top-k centrality),
   per the BatchBALD/coreset precedent — rather than either re-running the same naive greedy order again or
   concluding value-of-information itself is a dead concept. This is flagged as a lower-priority fallback, not the
   next dispatch.
4. **Sequencing note**: this cell should ideally run AFTER any pending pairwise schema-fit upgrade referenced in
   the surprise-decomposition note lands (if not already landed), so the redundancy check against schema-fit-like
   signals uses the corrected form — but this is a nice-to-have ordering, not a blocker, since the recommended
   cell's primary comparison is against `[degree, rel_freq]`, not schema-fit.

## Calibration reasoning

- Sub-agent 1 (retrieval/attention biology): raw confidence 0.55 that value/importance is a real, distinct
  retrieval-time prioritization function (not purely an encoding-time one) — kept close to the lit-scan's own
  number since the dissociation evidence (Mattar & Daw Gain x Need; value-driven capture; priority maps) is
  primary-source-verified and convergent, but genuinely imperfect (Cohen/Ranganath, Braun et al. show real
  encoding-retrieval entanglement in the best individual studies) → **deflated to 0.45** for this note's specific
  claim (applies cleanly to THIS substrate's use-case, not just to biology in general).
- Sub-agent 2 (active-learning redundancy mechanism): 0.55 raw, kept at 0.50 — this is a well-precedented,
  textbook-level mechanism (BatchBALD, coreset, submodularity), but the graph-hub-specific sub-claim (angle 3) is
  more analogical than directly demonstrated for a centrality-flavored score specifically.
- Sub-agent 3 (centrality-as-retrieval-relevance, classical IR): 0.75 raw — this is genuinely well-established,
  general theory (PageRank/HITS/PPR), not novel synthesis at the general level, so kept relatively high; the
  NOVEL part is applying it to this substrate's specific downstream-reach computation and dataset, which is
  untested and where the novel-synthesis cap applies.
- **Overall P_deflated for the verdict ((a) is the correct load-bearing function, recommended cell as specified) =
  0.44** — capped below 0.50 per the mandatory novel-synthesis ceiling (this is a first-of-its-kind mapping from
  three converging literatures onto this substrate's specific already-computed signal, not an imported, directly-
  precedented result), and set close to the ceiling because the supporting literature is unusually convergent
  across three independent angles (retrieval/attention biology, active-learning redundancy mechanism explaining the
  known failure, and classical-IR precedent for exactly the proposed re-target) and the recommended test reuses
  100% already-built, already-validated machinery rather than proposing anything architecturally new.

## Citations (verified count: 20 distinct sources across 3 lit-scans + this note's synthesis)

**Retrieval/attention prioritization:** Anderson, Laurent & Yantis 2011, *PNAS* 108:10367 (verified primary);
Anderson 2013, *PLOS ONE*, "Learned Value Magnifies Salience-Based Attentional Capture" (verified); Anderson 2019
review, *Curr Opin Psychol* (verified); Fecteau & Munoz 2006, *Trends Cogn Sci* 10:382 (verified full text);
Klink, Jentgens & Lorteije 2014, *J Neurosci* 34:13867 (verified abstract); Menon & Uddin 2010, *Brain Struct
Funct* 214:655 (verified via secondary sources); Feldman & Friston 2010, *Front Hum Neurosci* 4:215 (verified full
text, PMC2854285); Mattar & Daw 2018, *Nature Neuroscience* 21:1609 (PMC6203620, verified primary); Braun, Wimmer
& Shohamy 2018, *Nature Communications* (verified abstract); Cohen/Ranganath et al. 2022, *Nature Communications*
(verified via search snippets); ACT-R fan-effect literature (Anderson & Reder, verified via act-r.psy.cmu.edu);
retrieval-induced forgetting review (PubMed 23687918, verified).

**Active-learning redundancy:** Schmidhuber 2010, *IEEE TAMD*, "Formal Theory of Creativity, Fun, and Intrinsic
Motivation" (verified primary); Gottlieb, Oudeyer, Lopes & Baranes 2013, *Trends Cogn Sci* 17:585 (verified);
Poli et al. 2022, PMC9194910 (verified primary); Houlsby et al. 2011, BALD (verified via arXiv); Kirsch, van
Amersfoort & Gal 2019, BatchBALD, arXiv:1906.08158 (verified primary); Sener & Savarese 2018, ICLR, arXiv:1708.00489
(verified primary); Nemhauser-Wolsey-Fisher 1978 submodularity guarantee (verified, canonical); hierarchical graph
sampling, arXiv:2503.00860 (verified preprint); ALINC, arXiv:2606.04647 (verified preprint).

**Centrality as retrieval relevance:** Brin & Page 1998, WWW7 (verified, canonical); Kleinberg 1999, *JACM*
(verified, canonical); Borodin et al. 2005, *ACM TOIT*, "Link Analysis Ranking" (verified survey); Olston & Najork
2010, *Foundations and Trends in IR*, "Web Crawling" (verified survey); CR-LT-KGQA, arXiv:2403.01395 (verified
preprint); personalized-PageRank/RWR recommender-systems sources (arXiv:1711.04101, arXiv:2403.05198, verified).

## Next-drill candidate

If the cheap decisive test HARD-PASSes or lands MIDDLE: `network-science-graph-theory` (Tier-1 in the field
advisor) — specifically comparing personalized-PageRank-style downstream-reach against simpler degree/frequency
baselines for the HEAVIER v2 test (bounded-width retrieval ranking vs. accuracy), to establish which centrality
flavor best matches genuine query-time relevance rather than defaulting to the cheapest available metric. If it
HARD-FAILs cleanly: no new research drill needed on this specific question — redirect to whichever open
combination-law question (schema-fit x surprise, or salience x surprise) is next in the queue, per the
surprise-decomposition note's own next-drill recommendation.
