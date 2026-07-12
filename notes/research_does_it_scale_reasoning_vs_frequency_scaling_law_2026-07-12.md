# Research: Does glass-box relational reasoning SCALE, or does it hit walls? (2026-07-12)

Synthesis drill, 4 parallel Sonnet lit-scan sub-agents (KGE dimension-vs-N scaling laws; frequency/popularity-baseline
dynamics at scale; inductive-vs-memorization generalization; brain hippocampal-entorhinal scaling mechanisms) +
on-disk re-read of the current fair-test result (`data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json`)
and the full relational-capability track record
(`notes/relational_capability_track_record_scour_2026-07-10.md`). Extends, does not duplicate,
`notes/research_how_others_beat_frequency_dissect_training_glassbox_recreate_functional_form_gap_2026-07-11.md`
(functional-form/TransE-vs-rotation diagnosis) and `notes/the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md`
(the map-builder narrative arc). This note's job: the scaling axis those did not address — as N grows, does the
whole reasoning-vs-frequency race get easier, harder, or structurally different in kind?

---

## HEADLINE

1. **The current result is a MIDDLE_BAND_PARTIAL, not a clean win — read the numbers straight before projecting a
   trend from them.** Re-read directly off `metrics.json` (not paraphrased): at N=25,752 entities / 29 relations /
   511,164 core edges, `ONESHOT_ROTATE` fair (low+mid) Hits@10 = **0.0772** vs `BASELINE_POP` = **0.0442** (aggregate
   win, ~1.75x) — but `ADDITIVE_TRANSE` fair = **0.1039**, i.e. additive beats rotation on the SAME fair stratum, on
   BOTH the low tertile (0.0653 vs 0.0307) and the mid tertile (0.1431 vs 0.1244) individually. At the high-degree
   tertile, `BASELINE_POP` = 0.4155 beats both `ONESHOT_ROTATE` (0.3955) and `ADDITIVE_TRANSE` (0.3213) outright.
   Scramble collapses relative to real geometry (0.1118 vs 0.3955 at high — real geometric content is present), but
   the backdoor correlation check **FAILED** (`backdoor_r=0.3118` against a `<0.20` gate) — the cell's own verdict
   is `MIDDLE_BAND_PARTIAL`, `win_form=False`, `g_backdoor=False`. **The honest starting point for a scaling
   question is: we do not yet have a clean, backdoor-clear win to extrapolate from — we have a partial, degree-confound-flagged
   signal, on a form (rotation) that additive TransE currently beats on its own home turf (low/mid degree).** Any
   scaling-curve design must carry this caveat forward, not launder it into "our winning method, at scale."
2. **No published law cleanly ties required embedding dimension to N — but the newest and most relevant result ties
   it to LOCAL DEGREE, not global entity count.** Full-expressiveness bounds (ComplEx `d=n_e·n_r`; SimplE
   `d=min(n_e·n_r, edges+1)`, tied to edge density not raw N; TuckER far tighter, `d_e=n_e`) are worst-case, not
   typical-achieved-capacity results. The most directly relevant 2025 result (arXiv:2506.22271, "Breaking Rank
   Bottlenecks") proves dot-product-decoder KGE needs **d ≥ 2c+1 where c = max out-degree** for a practical
   sufficiency bound — dimension is governed by **local connectivity/branching factor**, not N itself. This is the
   single most load-bearing external fact this drill found: **it means naive N-scaling (more entities, similar
   typical degree) does NOT by itself force dimension up — what forces dimension up is degree/density growth, which
   is a DIFFERENT and more diagnosable axis than raw N.** Same paper states outright "there is no theoretical
   analysis of the minimum embedding dimensions required by a knowledge graph" — the clean log-N/sqrt-N law asked
   for in the mission does not exist in the literature; this is a genuine open gap, not a coverage failure of this
   drill.
3. **Billion-scale KGE systems solve the ENGINEERING problem (memory/speed), not the reasoning-vs-frequency
   problem — accuracy stays roughly flat under partitioning at fixed dimension.** PyTorch-BigGraph on full Freebase
   (121M entities, 2.4B edges): MRR 0.170 (1 partition) → 0.174 (16 partitions); only mild drop (0.171→0.163) under
   8-way parallelization. Marius and DGL-KE report similar "same accuracy, faster/cheaper" framing. **None of the
   three billion-scale systems surveyed publishes an accuracy-vs-N degradation curve at fixed dimension** — this
   question (does PURE PREDICTIVE QUALITY degrade as N grows, holding dimension and density fixed) appears to be a
   genuine literature gap that only this substrate's own scaling-curve experiment (Section "Scaling-curve design"
   below) can answer directly for CSKG-shaped commonsense graphs.
4. **The frequency baseline's moat is governed by DEGREE SKEW, not raw graph size — and generic scale-free growth
   theory says naive N-scaling (crawling/merging more overlapping commonsense sources) grows skew, not shrinks
   it.** Degree-bias literature (Shomer et al., WWW 2023, KG-Mixup) shows the low-vs-high-degree accuracy gap tracks
   skew magnitude directly: FB15k-237 (skewed) shows a 58.6-point gap between low- and high-degree triples; NELL-995
   (less skewed) shows only 32.3 points; WN18RR (nearly flat degree distribution) shows negligible degree bias at
   all. Barabasi-Albert preferential-attachment theory: hub degree scales as `k_max ~ N^(1/(gamma-1))` (≈√N for the
   canonical gamma=3), while mean degree stays roughly constant — **the hub/mean ratio (skew) necessarily grows with
   N under naive attachment-style growth.** Combined with Leskovec-Kleinberg-Faloutsos's "graphs over time" finding
   that real-world graphs also densify (edges grow super-linearly in N), the honest prediction is: **as CSKG-style
   corpora are grown by merging/crawling more overlapping commonsense sources, both average degree AND skew rise —
   the high-degree "frequency wins" regime gets a LARGER absolute population AND a larger SHARE of total edge mass,
   even as the low/mid-degree ("fair") population also grows in absolute count.** This directly answers mission
   question B: **the fair stratum most likely grows in absolute size (more long-tail entities in total) but SHRINKS
   as a fraction of total graph mass/query traffic — meaning a scaling program MUST keep reporting degree-stratified
   metrics forever, not just now.** An aggregate (non-stratified) metric will get systematically more frequency-favorable
   as N grows, purely from skew growth, independent of any change in the reasoning mechanism's quality.
5. **The make-or-break property is REUSABLE RELATION OPERATORS vs PER-ENTITY MEMORIZATION — and we already have a
   FULL HARD_FAIL on our own substrate testing exactly this axis.** The inductive-KGE literature (Teru et al. GraIL,
   ICML 2020; Zhu et al. NBFNet, NeurIPS 2021) draws a hard architectural line: fixed per-entity embedding tables
   (TransE/ComplEx/RotatE/additive, including our own `ONESHOT_ROTATE`/`ADDITIVE_TRANSE`) **cannot even be evaluated
   on entities unseen at train time** without retraining a new vector per entity — this is stated as an architectural
   fact, not a tuning gap. Truly inductive methods (subgraph reasoning, relational message passing, rule-mining
   operators like DRUM/Neural LP) use relation-level operators that transfer to new entity combinations BY
   CONSTRUCTION: NBFNet's inductive Hits@10 on FB15k-237/WN18RR v1-v4 splits (0.834-0.960) is comparable in
   magnitude to its OWN transductive number (0.599) — the architecture class, not scale, is what determines whether
   generalization is even possible. **Our own on-disk track record already ran this exact test on a structurally
   similar mechanism and got a clean FULL HARD_FAIL:** `grounding_learned_sr_heldout_reasoning_v1` (3 seeds, FULL,
   2026-07-10) found learned SR codes route NO BETTER than random codes on held-out entity-combination edges
   (reach@2 0.1148 vs random-code 0.104, delta 0.011, below the 0.05 margin) even though the same codes clearly beat
   a memoryless baseline on KNOWN edges (0.462 vs 0.017) — i.e. real memorized traversal, zero inductive inference.
   **The current CSKG rotation cell has NOT yet been run through this specific gauntlet** (it tests genuine 2-hop
   COMPOSITION between entities both present at train time, not generalization to unseen ENTITIES) — this is the
   single highest-value cheap test this drill identifies (see "Cheap decisive test" below), because the harness to
   run it already exists on this substrate from a different cell.

**Calibration note on this note's central scaling claim (points 4-5, the "fair stratum shrinks as a fraction while
frequency's moat grows" synthesis):** this bridges Barabasi-Albert scale-free theory (well-established) with
degree-bias empirics (well-established, Shomer et al.) via an inference about how CSKG-style corpus growth behaves
(not directly measured in the literature at this specific intersection). Per lit-scan calibration discipline, capped
at **P=0.50** (novel-synthesis cap) even though both supporting external results are individually solid.

---

## Cheap decisive test

**Reuse the `grounding_learned_sr_heldout_reasoning_v1` held-out-ENTITY split harness (already built, already
landed once) on the CURRENT `ONESHOT_ROTATE`/`ADDITIVE_TRANSE` fit codes, instead of building new infrastructure.**
That cell already implements: (a) a held-out-entity split (entities entirely absent from train, present only in
test edges), (b) a `CODEALIAS`/random-code control, (c) a memoryless baseline. Apply the SAME split methodology to
the rotation/additive fit's entity codes on CSKG (same 25,752-entity graph already in hand — no new corpus needed
for this specific check).

**HARD-PASS (reusable-operator hypothesis survives — worth building the full inductive scaling ladder):**
held-out-entity reach@2 (or fair Hits@10-equivalent) for `ONESHOT_ROTATE`/`ADDITIVE_TRANSE` clears the random-code
control by **>= 0.05 absolute** margin (the SAME bar the SR-code cell used) — i.e. the rotation/additive fit codes
carry SOME transferable relational signal to genuinely unseen entities, not just to unseen EDGES between known
entities.

**HARD-FAIL (expected outcome, given the architectural argument in HEADLINE point 5 and the prior FULL HARD_FAIL
on a structurally similar mechanism):** held-out-entity performance is statistically indistinguishable from the
random-code control (delta < 0.05) — this would mean our current fit, exactly like the SR-code cell, does memorized
search over the trained entity set and nothing more. This is the SINGLE cheapest, most decisive falsifier of "does
naive N-scaling of the current mechanism work" — if it fails here, no amount of additional N will fix it, because
per-entity embedding tables are, by the GraIL/NBFNet architectural argument, incapable of encoding an unseen entity
at all (there is no vector for it). **This test should run BEFORE committing compute to the multi-N scaling ladder
below** — it is cheap (reuses an existing 25.7k-entity graph and an existing split harness) and is the load-bearing
prerequisite: if the current architecture fails this, the scaling-curve experiment's headline question changes from
"does the fair-stratum margin hold up at bigger N" to "we need a genuinely inductive/operator-based architecture
before scale is even the right question to ask."

**Must-fail control:** run the SAME held-out-entity split on `BASELINE_POP` (fit-free, always available) — its
score should be unaffected by the split (fit-independence sanity check), confirming any observed rotation/additive
degradation is a genuine inductive-generalization gap, not a harness artifact.

---

## Falsifiable predictions (the multi-N scaling-curve experiment)

**Design:** build degree-stratified fair-test subgraphs at N ≈ 5k / 25k (current, reuse existing build) / 100k,
using the SAME construction methodology as the current cell (k-core density gate + L2-genuine 2-hop pattern
extraction + low/mid/high degree tertile stratification), sourced by progressively merging more of the CSKG
source graphs already surveyed (`notes/research_cskg_prior_art_novelty_due_diligence_2026-07-10.md` lists the
7-corpus survey) or a larger public commonsense-KG superset (full ConceptNet, ATOMIC, or an ogbl-wikikg2 subsample
matched for relation-type mix). Run the EXISTING 7-arm harness verbatim at each N-rung (`ONESHOT_ROTATE`,
`ADDITIVE_TRANSE`, `BASELINE_POP`, `DISCRETE_BIND`, `SCRAMBLE_ROTATE`, `RANDOM_CODES`, `ORACLE_TRANSDUCTIVE`), report
fair (low+mid) Hits@10 per arm, the backdoor correlation, AND a graph-level skew statistic (Gini coefficient of the
degree distribution, or max-degree/mean-degree ratio) at each rung, per-rung atomic checkpointing (reuse the
`oracle_capacity_ladder` cell's rung-checkpoint pattern so a dropped remote connection loses at most one rung, per
the cron-redispatch discipline). Route: remote_cpu_queue for 5k/25k rungs (CPU-safe, matches current compute
class), overnight_queue (GPU) for the 100k rung, with explicit per-seed memory isolation and adaptive batch sizing
— the current substrate already hit ONE `HARD_FAIL_CARDINALITY_BREACH` from CUDA OOM on a related map-builder cell
at this same entity count (`data/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1/metrics.json`, 3/3 seeds OOM'd),
so the 100k rung's memory budget needs headroom planned in, not discovered live.

**HARD-PASS (naive scaling basically works, no material wall):**
1. Fair (low+mid) `ONESHOT_ROTATE` margin over `BASELINE_POP` at N=100k is within 30% relative of the N=25k value
   (i.e. does not collapse toward zero as N grows 4x).
2. Backdoor correlation `r` does not climb monotonically and stay above the 0.20 gate at EVERY rung (some
   improvement or stability, not a steadily worsening confound).
3. The low+mid-degree tertile's ABSOLUTE entity count grows with N (confirming the fair arena is not vanishing in
   absolute terms, even if its share shrinks) — a direct empirical check of the Barabasi-Albert-derived prediction
   in HEADLINE point 4.
4. The held-out-entity inductive test (from the Cheap decisive test above) clears its `>=0.05` margin at EVERY
   rung, not just at N=25k — generalization capability, if real, should not require re-discovery at each scale.

**HARD-FAIL (a real wall — naive scaling degrades the reasoning-vs-frequency race):**
1. Fair margin shrinks toward zero or flips negative by N=100k — frequency's relative advantage GROWS with scale,
   consistent with the skew-growth mechanism in HEADLINE point 4 dominating.
2. Backdoor correlation `r` rises monotonically across rungs (0.31 at 25k -> higher at 100k) — the "win" becomes
   MORE confounded with degree as N grows, not less, meaning any apparent aggregate win is increasingly riding
   popularity rather than genuine structure.
3. The held-out-entity inductive test fails (delta < 0.05 vs random-code control) at ANY rung, replicating
   `grounding_learned_sr_heldout_reasoning_v1`'s finding on the rotation/additive mechanism specifically — this
   would confirm the wall is architectural (memorization, not reasoning) and INDEPENDENT of N, meaning the fix is
   not "wait for bigger graphs" but "build a genuinely inductive/factorized-operator architecture" (see brain
   grounding below).
4. Compute/memory cost scales worse than near-linear in N (i.e. the engineering axis itself becomes the blocker
   before the reasoning-quality axis can even be measured at 100k) — distinguish this explicitly from a reasoning
   degradation, since billion-scale systems (PyTorch-BigGraph, Marius) show this is solvable in principle with
   proper partitioning/disk-based training, so an engineering-only failure should NOT be conflated with a
   reasoning-quality wall.

**P_deflated summary:**
- The held-out-entity inductive test (cheap decisive test) passes on the CURRENT architecture: **P=0.15-0.20**
  (deflated hard — we already have a FULL HARD_FAIL on a structurally similar held-out-entity mechanism on this
  exact substrate; the GraIL/NBFNet architectural argument gives an independent reason to expect the same failure
  on any fixed per-entity embedding table, which is what both `ONESHOT_ROTATE` and `ADDITIVE_TRANSE` are).
- Given the inductive test fails (expected), a genuinely factorized/operator-based architecture (TEM-style
  structure/content split, or NBFNet-style relational message passing) WOULD pass a comparable inductive test if
  built: **P=0.35-0.40** (capped; strong architectural + brain-grounded motivation, but nothing of this shape has
  been built or tested on this substrate yet — newer ground than the rotation-vs-additive fix).
- Fair-margin (non-inductive, in-sample composition) holds up at N=100k without material shrinkage: **P=0.30**
  (the skew-growth argument in HEADLINE point 4 is the dominant reason to expect erosion; this is somewhat
  independent of the inductive question — even memorized-search-style composition could plausibly hold up in
  ABSOLUTE fair-stratum terms even as its SHARE of total mass shrinks).
- Backdoor correlation improves (drops below 0.20) rather than worsens as N grows: **P=0.25** (no strong prior
  either way in the literature; the current 0.31 reading is itself concerning and there's no external precedent
  cited in this drill for backdoor correlation trending down with scale specifically).

---

## Brain-grounding: what the mechanism NEEDS to scale gracefully

**The convergence this drill found, unprompted, across two independent literatures (KGE theory and
computational neuroscience) is the single most useful fact for architecture decisions:** the newest KGE
expressiveness result (`d >= 2c+1`, c=max local degree, arXiv:2506.22271) and the classical Treves-Rolls
sparse-associative-memory capacity law for hippocampal CA3 (`p_max ~ k * C_RC * ln(1/a)`, capacity governed by
connections-PER-NEURON and coding sparsity, NOT total neuron count) say the SAME thing in two different fields:
**capacity/dimension requirements are governed by LOCAL connectivity/branching density, not by the GLOBAL size of
the space.** This is direct, independent, cross-domain support for the mission's framing that density/degree
(not raw N) is the right axis to track as the substrate scales.

Three further brain mechanisms directly answer "what would a mechanism need to scale gracefully":

1. **Grid-cell modular reuse (Stensola et al., Nature 2012; Fiete/Burak/Brunel, J. Neurosci. 2008):** the brain
   does NOT allocate new neurons per new environment/space — it reuses a small, fixed set of ~4-5 spatial-scale
   modules, and the JOINT phase across modules gives an unambiguous range that grows EXPONENTIALLY with the number
   of modules (a combinatorial/CRT-like code), not linearly with neuron count. **Direct implication: a relational
   code that scales should be a small, fixed set of REUSABLE relation-operators combined combinatorially, not a
   flat per-entity or per-relation-instance table that grows 1:1 with graph size.** Our current `ONESHOT_ROTATE`/
   `ADDITIVE_TRANSE` fits are exactly the latter (a per-entity vector table) — this is architecturally the OPPOSITE
   of the brain's scaling solution, independent of whether the score function is additive or rotational.
2. **The Tolman-Eichenbaum Machine (Whittington et al., Cell 2020) factorizes STRUCTURE from CONTENT** — a small
   reusable relational/transition code (generalizes across domains) bound only at retrieval time to per-item
   sensory content. This is architecturally the same distinction the KGE literature draws between GraIL/NBFNet
   (relation-level operators, generalize to new entities) and TransE/RotatE/ComplEx (per-entity tables, do not).
   **The brain and the best-performing inductive KGE methods have independently converged on the same design
   principle: separate the reusable RELATIONAL machinery from the per-instance CONTENT.** Our substrate has not
   yet built anything in this shape for CSKG — the map-builder / replay-consolidation direction named in
   `the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md` (Course C) is the closest existing
   intent, but per that note's own caveat, a prerequisite HD-binding limit (`stage3_hrr_involutive_systematic_generalization_v1`,
   HARD_FAIL, "systematic generalization via involutive HRR = mechanism null") must be confronted first.
3. **Consolidation/schema compression (McClelland CLS 1995/2013; Tse et al., Science 2007/2011)** is the piece
   that lets the hippocampal system avoid needing capacity proportional to LIFETIME experience: fast episodic
   traces get continuously compressed into slow cortical schemas, and — critically — once a schema exists, NEW
   schema-consistent facts can be assimilated almost immediately (one-trial learning) because they reuse existing
   structure rather than adding raw storage. **Our current fit approach has no analog of this at all** — it is a
   single flat, non-consolidating fit over the WHOLE graph at once, structurally closer to an un-consolidated
   hippocampal index than to a cortical schema. Cortical-scale extensions of sparse-coding capacity theory
   (Kropff & Treves; Boboeva, Brasselet & Treves, Entropy 2018) put whole-cortex semantic capacity at roughly
   ~10^7 concepts via sparse coding + factorized generative structure — CSKG-core's 25,752 entities is nowhere
   near that ceiling, but the MECHANISM credited for reaching it (factorization + sparsity + consolidation, not
   a bigger flat table) is exactly what our current architecture lacks.

**Net brain-grounded prediction:** the current flat per-entity fit (rotation or additive) is not the shape of
mechanism the brain literature credits with graceful scaling. It may still show a positive fair-margin at N=100k
(memorized composition can genuinely extend some distance), but per points 1-3 above, it should NOT be expected to
solve the held-out-ENTITY generalization question at any scale without a factorized-operator/consolidation-shaped
redesign — this is an architectural gap, not a data or capacity gap, and matches the independent GraIL/NBFNet
argument from the KGE literature (HEADLINE point 5) exactly.

---

## Cross-thread synthesis

- Directly extends `notes/research_how_others_beat_frequency_dissect_training_glassbox_recreate_functional_form_gap_2026-07-11.md`
  (which diagnosed additive-TransE's provable symmetric/1-to-N blind spots and recommended a rotation-native fit).
  **This drill's finding that additive TransE currently BEATS rotation on the fair low/mid stratum (0.1039 vs
  0.0772) is a live, on-disk data point that has not yet been reconciled with that note's theoretical prediction** —
  worth flagging explicitly rather than assuming the theory has already played out; the rotation-native swap that
  note recommended may not yet be the fit actually running in `course_c_rotate_cskg_l2_seed_17_gpu1024_v1` (that
  note found the CSKG fit code stayed additive-Euclidean under a rotation-shaped readout in ALL three of its
  variants as of 2026-07-11 — if `ONESHOT_ROTATE` in this cell is a genuinely different, corrected construction,
  that reconciliation should be checked directly against the fit code before the next cycle draws conclusions from
  either number).
- Directly builds on `notes/relational_capability_track_record_scour_2026-07-10.md`'s central convergence finding
  ("memorized structure vs. inductive inference" is the through-line of the ENTIRE relational program, not just
  this cell) — this drill's "cheap decisive test" is a direct, low-cost application of that scour's own
  recommendation to test every new relational mechanism against the held-out-entity bar that already burned
  `grounding_learned_sr_heldout_reasoning_v1`.
- Complements `notes/the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md`'s Course C
  (map-builder/consolidation direction) — this drill supplies the SCALING argument for why Course C's factorized
  design is not just theoretically nicer but NECESSARY for graceful scaling (brain-grounding section above),
  independent of whether the current rotation-fit reaches a clean HARD_PASS on today's N=25.7k graph.
- New fact this drill adds that none of the three same-week sibling notes surfaced: **the KGE-theory / hippocampal
  sparse-coding convergence on "capacity is governed by local degree/connectivity, not global N"** (HEADLINE
  point 2 + brain-grounding section) — a genuinely new, citable, cross-domain synthesis point.

---

## Substrate-product implications

- **The honest, defensible product claim right now:** "our current fair-test result at N=25.7k is a partial,
  degree-confound-flagged signal, not a clean win — and the literature says the RIGHT question to ask before
  claiming this scales is not 'does N get bigger' but 'does the mechanism carry a genuinely reusable relational
  operator, tested on entities it has never seen.' We have already run that exact test once on a related mechanism
  and it failed (memorized search, not reasoning); the cheapest next step is re-running that SAME test on the
  current rotation/additive fit before spending compute on a multi-N ladder that would only tell us whether
  memorization scales, not whether reasoning does."
- **This reframes "does it scale" from a compute/engineering question (which the billion-scale KGE literature says
  is solvable) into an architecture question (which the inductive-KGE and brain literature both say requires a
  factorized-operator/consolidation design the substrate does not yet have).** Product messaging should not promise
  "and it gets better as we ingest more knowledge" without first clearing the held-out-entity bar — per this
  program's own standing discipline, construction-proofs and in-sample wins are not capability wins.
- **The degree-stratified reporting discipline is not a today-only fairness patch — it is a permanent scaling
  requirement.** Per HEADLINE point 4, aggregate (non-stratified) metrics will structurally favor frequency more
  and more as the corpus grows, purely from scale-free skew growth, independent of any change in the reasoning
  mechanism. Any dashboard or product number that reports an aggregate Hits@k without a degree breakdown will look
  like it is "getting harder to beat frequency" over time even if the underlying mechanism is unchanged or
  improving — this is a measurement artifact to guard against explicitly, not a reasoning regression to chase.

---

## Citations (verified count)

**On-disk, read in full this cycle:** `data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json` (full
gates/strat_hits/backdoor fields); `data/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1/metrics.json` (OOM
HARD_FAIL cross-check); `notes/relational_capability_track_record_scour_2026-07-10.md`;
`notes/research_how_others_beat_frequency_dissect_training_glassbox_recreate_functional_form_gap_2026-07-11.md`;
`notes/the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md`; `notes/research_cskg_prior_art_novelty_due_diligence_2026-07-10.md`;
`notes/substrate_capability_map.md`. **7 on-disk sources.**

**External literature (4 parallel Sonnet lit-scans, generic ML/neuroscience terms only, no substrate-novel
names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*KGE dimension/scale:* Trouillon et al. (ComplEx, JMLR 2017, arXiv:1702.06879); Kazemi & Poole (SimplE, NeurIPS
2018, arXiv:1802.04868); Balazevic et al. (TuckER, EMNLP 2019, arXiv:1901.09590); "Breaking Rank Bottlenecks in
Knowledge Graph Embeddings" (arXiv:2506.22271, 2025); Lerer et al. (PyTorch-BigGraph, MLSys 2019, arXiv:1903.12287);
Mohoney et al. (Marius, OSDI 2021, arXiv:2101.08358); Zheng et al. (DGL-KE, arXiv:2004.08532); "On Large-Scale
Evaluation of Embedding Models for Knowledge Graph Completion" (arXiv:2504.08970); OGB ogbl-wikikg2/ogbl-biokg
benchmark numbers; Amit-Gutfreund-Sompolinsky (Hopfield/Gardner capacity, replica method); Mazumdar et al.
(sparse-recovery associative memory capacity).

*Frequency-baseline-at-scale:* Mohamed et al. (Popularity-Agnostic Evaluation, UAI 2020, PMLR v124); Shomer, Jin,
Wang, Tang (KG-Mixup / Degree Bias, WWW 2023, arXiv:2302.05044); Sun et al. (Re-evaluation of KGC Methods, ACL 2020,
arXiv:1911.03903); Safavi & Koutra (CoDEx, EMNLP 2020, arXiv:2009.07810); Barabasi & Albert (Science 1999);
Leskovec, Kleinberg, Faloutsos (Graphs over Time, KDD 2005); Dacrema, Cremonesi, Jannach (RecSys 2019,
arXiv:1907.06902); Abdollahpouri et al. (Popularity Bias in Recommendation survey, arXiv:2008.08551).

*Inductive vs memorization:* Teru et al. (GraIL, ICML 2020, arXiv:1911.06962); Zhu, Zhang, Xhonneux, Tang (NBFNet,
NeurIPS 2021, arXiv:2106.06935); Yang et al. (Neural LP, 2017); Sadeghian et al. (DRUM, NeurIPS 2019,
arXiv:1911.00055); kNN-KGE / "Reasoning Through Memorization" (arXiv:2201.05575); "Generalizing to Unseen Elements"
survey (arXiv:2302.01859); Lake & Baroni (SCAN, ICML 2018); Sinha et al. (CLUTRR, EMNLP-IJCNLP 2019); Guu, Miller,
Liang (EMNLP 2015, arXiv:1506.01094); Das et al. (MINERVA, ICLR 2018, arXiv:1711.05851); Zhu et al. (A*Net, 2022,
arXiv:2206.04798); Zhang et al. (Rethinking Generalization, ICLR 2017, arXiv:1611.03530); Belkin et al. (Double
Descent, PNAS 2019, arXiv:1812.11118).

*Brain scaling mechanisms:* Stensola et al. (Nature 2012); Fiete, Burak, Brunel (J. Neurosci. 2008); Sreenivasan &
Fiete (Nat. Neurosci. 2011) / related PLoS Comp Biol grid-cell coding work; Treves & Rolls (Network 1991/2013;
Rolls 2024 review); Rolls (pattern completion/separation review); Whittington et al. (TEM, Cell 2020); Whittington,
Warren, Behrens (arXiv:2112.04035, ICLR 2022); McClelland, McNaughton, O'Reilly (Psych. Review 1995); McClelland
(J. Exp. Psych: General 2013); Tse et al. (Science 2007, 2011); Kropff & Treves; Naim, Boboeva, Kang, Treves;
Boboeva, Brasselet, Treves (Entropy 2018).

**Total: 7 on-disk sources read in full + 43 external sources across 4 parallel lit-scans = 50 verified checks.**

---

## Intuitive summary

The short answer: **it's not yet a clean "does it scale" question — the current result is a partial win with an
open red flag (its score correlates too much with plain popularity), and a plainer method (simple addition) is
currently beating the fancier one (rotation) on the exact arena where structure is supposed to shine.** Before
asking "what happens at 10x the data," the honest first move is fixing that.

On the scaling question itself, three things came back clearly. First, the plumbing (memory, compute, training
time) is a solved problem at huge scale — billion-entity systems already exist and don't lose accuracy just from
being bigger, they mainly need smarter engineering. So "can we afford to scale" is not the risk.

Second, the popularity-baseline's home turf (very well-connected, famous things) almost certainly gets a BIGGER
share of the graph's total mass as things grow — that's just how real-world networks grow (a few things become
mega-hubs, and that effect gets stronger, not weaker, the bigger the network gets). That means we have to keep
measuring "does structure beat frequency" separately for rare/unusual things and for famous things, forever, not
just as a today-only fairness check — otherwise the numbers will look like they're getting worse purely because
the popular stuff is drowning out the interesting stuff in any single blended score.

Third, and most important: the real make-or-break question isn't about SIZE at all, it's about KIND. Does the
system learn a reusable RULE about how relationships work (which would automatically apply to brand-new things it's
never seen), or does it just memorize a big lookup table of specific facts (which gets bigger and more
memorization-heavy, but never actually learns to reason, no matter how much you feed it)? The brain's answer is
unambiguous: it builds a small set of reusable relational "rules of thumb" (like a handful of measuring sticks it
reuses everywhere) completely separate from the specific facts they get applied to — that's WHY it can handle an
essentially unlimited world without running out of room. We already ran the test that tells rule-learning apart
from memorization on a closely related part of our system, and it came back negative — it was memorizing, not
reasoning. We have not yet run that same test on today's newest result. That's the single cheapest, most important
thing to check next — cheaper than any bigger experiment — because if it fails there too, more data won't fix it;
we'd need to change the KIND of mechanism, not the amount of knowledge we feed it.
