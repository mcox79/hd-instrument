# Research: the brain's foundation-BUILDING mechanism — consolidation-loop + explicit ingest-gate design

Director drill, 2026-07-15. Two parallel Sonnet lit-scan sub-agents (schema-consolidation biology; prediction-error
+ recurrence biology) + synthesis over existing internal findings (wave14b/14c replay research, additive_map
integration endgame, reachability_audit tool, foundation-sourcing pivot memory). Research-only: no code written, no
cell dispatched. Generic neuroscience terms only in external queries per query-privacy discipline.

## HEADLINE

The brain's foundation-builder is CLS (hippocampus fast/one-shot -> neocortex slow/structured via interleaved
replay) gated by THREE separately-evidenced, NEVER-FORMALLY-UNIFIED signals — schema-congruency (Tse 2007;
McClelland 2013; van Kesteren 2012 SLIMM), novelty/prediction-error (Lisman-Grace 2005; Duszkiewicz 2019), and
cross-episode recurrence (Schapiro-Turk-Browne 2017). Both lit-scans independently confirmed NO paper gives a
combined formal rule for how these three interact — this is a genuine, not incidental, gap in the neuroscience
literature. That gap is exactly where our substrate has a real, buildable, glass-box advantage: we already have
VET-confirmed scoring primitives for two of the three signals (`hdlab/additive_map.py` score_all = a closed-loop
surprise/prediction-error metric; `hdlab/reachability_audit.py` = a schema-fit/composability metric), and the
third (recurrence) is already a validated project-level finding (degree-1/no-recurrence = structural underpower,
independently confirmed by the reachability-audit negative-result drill and the Horlbeck GI cell design). The
missing piece is not new biology, not new mechanism — it is a decision-tree that WIRES these three already-proven
signals into an explicit consolidate/skip/discard gate. That wiring is design-only and cheap to pilot.

One important caution surfaced by composing with prior findings: a structurally similar idea (a STATIC
structural-tag priority signal for replay selection) was already built and FALSIFIED on this substrate (R7,
-0.53 bpc vs random) precisely because static tags are not closed-loop on current model state. The gate proposed
here is explicitly designed to avoid that failure mode (all three signals are recomputed against the CURRENT
fitted foundation each cycle) — but this is an argument, not yet a measurement. The pilot cell in Section 6 tests
it directly before any real build commitment.

## 1. Biology — lead with this

### 1.1 Complementary Learning Systems (CLS): why two systems, why interleaved replay

McClelland, McNaughton & O'Reilly 1995 (Psych Review) and its 2016 update (Kumaran, Hassabis, McClelland, *Trends
Cogn Sci*, "What Learning Systems do Intelligent Agents Need?"): hippocampus is fast, sparse, pattern-separated
(dentate gyrus decorrelates similar inputs; CA3 autoassociative one-shot Hebbian write) — it can bind a novel
episode in a single exposure. Neocortex is slow and DISTRIBUTED/OVERLAPPING — the same units participate in many
representations, which is exactly what gives cortex its generalization power, but also means a single large direct
weight update (writing one new episode directly, at hippocampal speed) would catastrophically overwrite existing
structure shared by those units. The fix is INTERLEAVED replay: during slow-wave sleep sharp-wave ripples,
hippocampus replays recent episodes (temporally compressed ~10-20x) intermixed in small, gradient-like increments
with ongoing/old experience, so cortex integrates new structure without erasing old. Kumaran et al. 2016 explicitly
note this is the biological inspiration for experience replay in deep RL (DQN).

### 1.2 The ingest gate — three criteria, evidenced separately, never formally unified (the crux)

**(a) Schema-consistency.** Tse et al. 2007 (*Science* 316:76-82) — the founding result: rats trained for weeks on
a hippocampus-dependent flavor-place paired-associate task until a stable "schema" formed; once the schema existed,
BRAND-NEW flavor-place pairs, trained in as few as one trial, became hippocampus-independent within ~48h — versus
the normal multi-week systems-consolidation timescale. Tse et al. 2011 (*Science* 333:891-895) extends the
mechanism: schema-consistent rapid learning drove immediate-early-gene activation specifically in prelimbic mPFC,
and mPFC lesion/blockade prevented both new learning and recall of even recently-consolidated schema material —
mPFC is where the schema scaffold lives and where synaptic tagging/capture for new-but-consistent info is
accelerated. van Kesteren, Ruiter, Fernandez & Henson 2012 (SLIMM model, *Trends Neurosci* 35:211-9) formalizes the
gate: vmPFC computes a "resonance"/congruency signal against the active schema; high congruency -> vmPFC
DOWN-GATES hippocampal/MTL engagement, permitting direct fast cortical write; low congruency -> a prediction-error
signal instead recruits hippocampus for full, slow, MTL-dependent episodic encoding. Congruency itself is graded
(empirically, memory strength is U-shaped across the congruency spectrum — both highly congruent AND highly novel
material is remembered better than "medium-fit" material), but no paper found gives an explicit rate-equation for
consolidation SPEED as a function of congruency — McClelland 2013 (*J Exp Psychol Gen* 142:1190-1210, the paper
that revises the original 1995 CLS account specifically to admit a fast-schema-consistent exception) shows in
simulation that schema-consistent new info integrates via small, non-disruptive weight increments while
schema-inconsistent info still requires the slow interleaved route or causes interference — but stops at the
qualitative level. **Both lit-scan sub-agents independently confirmed this: no quantitative combination formula for
schema-fit exists in the accessible literature.** (Gilboa & Marlatte 2017, *Trends Cogn Sci* 21:618-631, is the
integrative review; also qualitative.)

**(b) Prediction-error / novelty / surprise.** Lisman & Grace 2005 (*Neuron* 46:703-713) — the hippocampal-VTA
loop: hippocampus detects that incoming info is NOT already in long-term memory (a novelty signal), relayed
subiculum -> accumbens -> ventral pallidum -> VTA, driving novelty-dependent dopamine release back into
hippocampus that gates LTP/tagging for durable storage. Duszkiewicz, McNamara, Takeuchi & Genzel 2019 (*Trends
Neurosci* 42:102-114) importantly refines this into TWO parallel novelty systems rather than one scalar gate:
"common novelty" (partial overlap with existing structure) -> VTA dopamine -> gradual systems consolidation into
generalized/semantic memory; "distinct novelty" (near-zero overlap) -> locus coeruleus co-release -> strong, fast
hippocampal consolidation of vivid EPISODIC (not immediately generalized) detail. Takeuchi et al. 2016 (*Nature*
537:357-362) shows novelty-driven behavioral tagging via LC boosts retention of an unrelated weak memory.
Multiple reviews report SWR replay content is biased toward novel/weakly-encoded experience — but this is NOT
uncontested: Farooq & Dragoi 2024 (*Science*, PMC10659301) found awake-SWR trial identity predicts sleep-replay
content (R=0.86) via intrinsic population/"trial manifold" dynamics EVEN AFTER controlling for novelty and reward —
a genuine open tension, not settled consensus, that novelty/surprise is the (sole or dominant) selector of what
gets consolidated.

**(c) Reliability / recurrence.** Schapiro & Turk-Browne 2017 (*Phil Trans R Soc B* 372:20160049) — an anatomical
dissociation, not just a metaphor: the hippocampal monosynaptic pathway (entorhinal cortex -> CA1 direct) supports
statistical-regularity extraction across MANY episodes in parallel with the trisynaptic pathway (dentate gyrus/CA3
pattern separation), which supports one-shot storage of individual, possibly one-off, episodes. Regularity
detection is reported as fast (detectable after as few as ~2 presentations in auditory statistical-learning
paradigms) but STRENGTHENING monotonically with further repetition rather than gated by a fixed universal
threshold — i.e., graded reliability, not a hard count.

**How the brain weighs/combines these three — the honest answer: it does not, as a single formal rule.** Both
lit-scans independently converged on this. Schema-fit (mPFC-MTL loop), novelty (hippocampal-VTA/LC loop), and
recurrence (EC-CA1 monosynaptic pathway) are three SEPARATE, anatomically distinct circuits that each influence
whether something gets a fast direct cortical write, a slow interleaved consolidation, or stays hippocampal/fades —
but no unified computational account (Bayesian-surprise-style or otherwise) combining all three into one decision
was located. This is a genuine hole in the literature, confirmed independently by two lit-scans with no shared
priors. It means an explicit, glass-box combination rule on our substrate is not "reproducing a known brain
algorithm, imperfectly" — it is proposing a NEW, testable combination rule informed by three separately-validated
qualitative principles, which is exactly the "our advantage over the brain's implicit gate" framing the task named.

### 1.3 How the consolidated foundation supports reasoning about new things

Tse's schema IS the scaffold for future fast learning (that is the entire point of the 2007/2011 result: a
consolidated structure changes the RULE for how future new information gets processed, not just what is already
known). McClelland's 2013 simulations and Kumaran/Hassabis/McClelland 2016's broader account frame this as
schema-based inference / extrapolation: once cortex has extracted the shared structure across many instances, a
partially-specified new instance can be filled in by projecting onto the existing structural slots. This maps
directly onto our own already-proven mechanism (Section 2): `compose_entity` composes a brand-new entity's
low-dimensional coordinate as the mean of its support edges' structural displacement vectors within the FITTED
(X, D) coordinate geometry — i.e., schema-based slot-filling, zero-training, CHAIN_GRADE (0.1282 held-out MRR,
284x the random ceiling — see `research_additive_map_builder_integration_endgame_2026-07-13.md`).

## 2. Map to our validated pieces

| Brain component | Our validated substrate piece | Status |
|---|---|---|
| Hippocampal fast one-shot, pattern-separated write | `hdlab/additive_map.py`: `insert_entity` (trivial `torch.cat` append) + `compose_entity` (zero-training mean of support-edge displacement vectors) | CHAIN_GRADE (HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE, held-out MRR 0.1282, 284x ceiling ratio) |
| Cortical slow structured foundation | The fitted `(X, D)` coordinate table, produced by slow SGD (Adam, 500 epochs) at build/consolidation time | Proven mechanism; persistence + periodic re-fit cadence not yet built (flagged as Full-stage item in the integration endgame note) |
| Sleep-replay (interleaved, offline) | Random replay as implicit gradient-direction/subspace-projection regularizer during continual writes | Confirmed mechanism (wave14c synthesis over 9 candidate mechanisms) — BUT the mechanism is projection/anti-interference, not literal "rehearsal," and STATIC structural-tag prioritization for WHICH items to replay was separately FALSIFIED (R7, -0.53 bpc). See caution below — do not conflate replay-selection-priority with the ingest gate. |
| No-catastrophic-interference | Pattern-separation storage | CHAIN_GRADE |
| Schema/structure (mPFC-MTL loop analog) | Canonical-ID hub / module-2 predictive composition | CHAIN_GRADE on the prior held-out result; a v2 upgrade (`crossmodule_interface_hub_identity_bind_heldout_v2`) is in-flight as of this drill (dispatched, remote_status=running, NOVEL-vs-SEEN verdict pending) — cite the v1 result as the landed evidence, not the in-flight v2 number. |
| Recurrence-requirement | Degree-1/no-recurrence structural underpower | Validated — independently reconfirmed by the reachability-audit negative-result drill (density-floor/degree-1 nodes are the reachability-failure mode) and by the Horlbeck-GI cell design (every gene recurs 447x, a deliberate precondition for the interaction-detection test to be meaningful at all). |

**Important nuance carried forward, not glossed over:** the wave14b/14c thread already ran a close cousin of this
exact idea — a static structural tag deciding what to prioritize — and it lost decisively to an unbiased/random
baseline (R7). The literature explanation (both the CL literature survey in `wave14b_r7_replay_literature.md` and
the mechanism synthesis in `wave14c_random_replay_mechanism_research.md`) is specific: static tags are not
closed-loop on current model state, and in our rank-1 Hebbian delta-rule, any priority score collapsed onto the
same direction the cosine-retrieval branch already uses. Two things distinguish the ingest-gate design below from
that failure: (1) it targets a DIFFERENT decision (what becomes foundational/consolidated) than what R7 targeted
(which stored items get sampled into a replay minibatch for gradient regularization) — these are not the same
lever; (2) the surprise signal proposed here is computed in the additive-map's k=24 KGE-style coordinate geometry
via `score_all`, a structurally different scoring pathway than the rank-1 Hebbian delta-rule's MIR score that
collapsed in wave14c. Point (2) is an argument, not a measurement — Section 6's pilot tests it directly rather than
assuming it away.

## 3. The consolidation-loop design

```
STEP 0  Candidate arrives (new fact/entity/edge from foundation ingest, or a runtime encounter)
STEP 1  FAST PROVISIONAL TIER
        insert_entity / compose_entity into a provisional partition (pattern-separated;
        does NOT touch the fitted (X,D) cortical coordinates). Immediately servable.
        [hippocampal fast one-shot write]
STEP 2  OFFLINE CONSOLIDATION CYCLE (batched, periodic)
  2a.   Interleaved replay regularization: mix provisional-tier candidates with a RANDOM
        sample of existing foundation edges (per the wave14c-validated projection mechanism).
        Use RANDOM sampling here, NOT structural-tag priority (R7 already falsified that for
        this exact kind of update).
  2b.   EXPLICIT INGEST GATE -- compute schema_fit, surprise, recurrence per candidate (Section 4)
  2c.   Route: CONSOLIDATE (fast-track or slow-track) / KEEP-PROVISIONAL / DISCARD
STEP 3  FOUNDATIONALIZE
        Fast-track (high schema_fit): direct compose_entity + insert_entity fold into (X,D),
        no full re-fit needed -- Tse/SLIMM-style rapid schema-consistent integration.
        Slow-track (low schema_fit, passes surprise+recurrence): queue for the next full
        interleaved SGD re-fit of (X,D) -- McClelland-1995-style, needs whole-batch gradient
        integration to avoid interference since it doesn't fit existing structure.
STEP 4  HOMEOSTASIS
        Provisional-tier candidates that fail the gate for N consecutive cycles either age out
        (discarded -- analogous to synaptic downscaling) or persist as permanently-episodic
        (not everything needs to generalize).
```

## 4. The explicit glass-box gate — three measurable criteria

**(A) SCHEMA-FIT.** Reuses `hdlab/reachability_audit.py`'s existing relational-reachability signal
(`k_hop_reachable_mass`, `distance_to_hub`, `mean_neighbor_degree`) — already built, glass-box, deterministic BFS,
no LLM. `schema_fit(e) = mean over e's support edges of reachability_score(h_i)`, weighted by whether `r_i` is an
existing relation type in `D` (brand-new relation types automatically score low). Threshold: `SCHEMA_FIT_MIN =
0.5` (majority of support edges anchor into already-reachable/well-modeled structure) routes to FAST-TRACK; below
routes to SLOW-TRACK if it otherwise passes.

**(B) SURPRISE.** Reuses `hdlab/additive_map.py`'s existing scoring pathway (`score_all` / `additive_direct_scores`
— the SAME function already VET-confirmed at HARD_PASS 0.1282 MRR). `surprise(candidate) = 1 - reciprocal_rank(true
target | current X, D)`. Recomputed against the CURRENT fitted foundation every cycle (closed-loop, per the
literature's universal finding that closed-loop signals beat static tags). Threshold: `SURPRISE_MIN = 0.5` (true
target ranked outside the top half under the current model) — below this, the candidate is redundant (foundation
already predicts it) -> SKIP, no consolidation write needed. Sub-threshold distinction (informed by Duszkiewicz
2019's two-novelty-system finding): `0.5-0.85` = "common novelty" (partial overlap, schema-adjacent) -> eligible
for gradual/slow-track fold; `>0.85` = "distinct novelty" (near-zero overlap) -> flagged for cross-source-provenance
review before consolidating, not auto-folded (a candidate the model finds shocking AND that recurs is ALSO the
profile of a systematic ingest error or an out-of-distribution batch — Duszkiewicz's LC/vivid-episodic route is
explicitly NOT immediate generalization, and neither should ours be).

**(C) RECURRENCE.** `recurrence_count(pattern)` = number of distinct entity instances (ideally from distinct
provenance sources, not just distinct mentions in one ingest batch) exhibiting the same (relation-type,
structural-motif) as the candidate. Threshold: `RECURRENCE_MIN = 3` — chosen as a concrete, testable, revisable
number (the biology gives graded-not-thresholded evidence, so we pick and pre-register our own bar rather than
pretend one is handed to us). Below this: DISCARD or hold in provisional regardless of schema_fit/surprise scores —
this is what prevents a single erroneous/hallucinated ingested fact from becoming permanently foundational.

**Gate combination logic (a decision tree, not an additive/multiplicative score — deliberate, since the biology
supplies no unified formal combination rule to borrow):**

```
if recurrence_count < RECURRENCE_MIN:                  DISCARD
elif surprise < SURPRISE_MIN:                            SKIP (redundant)
elif surprise > 0.85 (distinct-novelty band):            HOLD for provenance review
elif schema_fit >= SCHEMA_FIT_MIN:                       FAST-TRACK CONSOLIDATE
else:                                                    SLOW-TRACK CONSOLIDATE
```

Recurrence is a HARD reliability floor (gate, not a weight) evaluated FIRST and cheaply, before spending the
surprise/schema-fit computation — matching the project's own standing discipline that a genuine positive control
must fire before anything downstream is trusted (the same shape as the SYM=1.0 arbitrary-control gate used
elsewhere). This tree is a pre-registered DESIGN CHOICE to be tested, not a claimed biological fact.

## 5. KEYSTONE — the prediction-error-gated consolidation trigger, precisely specified

This is the piece the task named as not-yet-built. Precise spec:

1. Input: candidate edge/entity `e`; current fitted `(X, D)`; current entity/relation vocab.
2. Embed: `compose_entity(e)` if novel, else vocab lookup.
3. Score: run the EXISTING, already-VET-confirmed scoring function `score_all(head_idx, rel_idx)` for `e` against
   all `N` candidate targets — this reuses a proven pathway; no new mechanism is invented for the measurement
   itself.
4. Normalize: `surprise = 1 - reciprocal_rank(true_target)`. `surprise=1` means the foundation ranked the truth
   dead last (total prediction failure, maximal surprise); `surprise=0` means rank #1 (foundation already knew
   this).
5. Threshold + band (Section 4B): `SURPRISE_MIN=0.5` gates SKIP-if-redundant; the `0.5-0.85` / `>0.85` split
   implements the common-novelty/distinct-novelty distinction from Duszkiewicz 2019.
6. Compose with recurrence (evaluated first, hard floor) and schema-fit (routes fast vs. slow track) per the
   decision tree in Section 4.

**What makes this the keystone rather than a restatement of Section 4B:** it is the FIRST time "does the current
foundation already predict this" is operationalized as a reusable, closed-loop, already-proven-scoring-pathway
question on this substrate, rather than a structural/static proxy (which the project already tried and falsified
once, R7). Building it costs zero new scoring mechanism — it is a threshold + routing layer on top of
`score_all`, which already exists and is already VET-confirmed. The unresolved risk is real and explicit: whether
this KGE-geometry surprise score is genuinely independent of the schema-fit/reachability signal, or whether (as
happened to MIR in the rank-1 Hebbian delta-rule) it collapses onto the same direction as retrieval/composition and
becomes redundant with schema-fit. That is exactly what Section 6's cheap decisive test checks first, before any
larger build commitment.

## 6. Linchpin pilot cell design (pre-registered HARD-PASS/HARD-FAIL; NOT dispatched — director's call)

**Candidate name:** `exp_ingest_gate_consolidation_loop_pilot_v1` (design only).

**Setup:** reuse the already-fitted `additive_map` `(X, D)` on CSKG train edges (the same fit underlying the
0.1282 HARD_PASS result) as "the existing foundation." Construct four candidate batches:

1. **REDUNDANT** — held-out edges the model already predicts well (low expected surprise).
   HARD-PASS: gate SKIPs >=80% of these (doesn't waste consolidation writes on redundant info).
2. **GENUINE-NOVEL-RELIABLE** — withhold an entire relation type from training, then reintroduce a subset as
   candidates with recurrence deliberately varied (>= RECURRENCE_MIN across multiple distinct entities).
   HARD-PASS: gate CONSOLIDATES >=70% of these AND held-out MRR on a FRESH disjoint eval split for that relation
   improves by >= +0.02 absolute after fold-in vs. before.
3. **ONE-OFF NOISE** — single scrambled/corrupted edges (head/tail swap, per the existing SCRAMBLE-control
   convention), each presented once (recurrence=1).
   HARD-FAIL if gate consolidates more than 5% of these (recurrence floor not doing its job).
4. **INTERFERENCE CONTROL** — after running one full cycle (skip-redundant + consolidate-novel + discard-noise),
   re-measure MRR on the ORIGINAL held-out eval set from the 0.1282 result.
   HARD-FAIL if this regresses by more than 5% relative (would mean consolidation corrupted existing retrieval —
   the exact catastrophic-interference failure mode CLS exists to prevent).

**Falsifiable predictions:**
- HARD-PASS (joint, all four): batch1 skip-rate >=80%; batch2 consolidate-rate >=70% AND post-fold MRR improvement
  >=+0.02 absolute; batch3 consolidate-rate <=5%; batch4 MRR regression <=5% relative.
- HARD-FAIL localizations (each individually informative, not a wasted cycle):
  - batch2 passes gate but MRR doesn't improve -> fold-in MECHANISM problem, not a gate-design problem.
  - batch3 consolidate-rate high -> recurrence metric too weak; needs cross-source provenance, not raw count.
  - batch4 regresses -> fold-in isn't interference-safe; the wave14c-validated interleaved-replay regularization
    needs to run AT fold-in time, not be skipped for the fast-track path.
- MIDDLE band (realistic modal expectation): batch2 consolidate-rate lands 40-70% — threshold tuning, not redesign.

**Cheap decisive test (do this slice first):** batches 1 + 3 only (skip-redundant + reject-noise) against the
ALREADY-FITTED additive_map — zero new data acquisition, reuses existing `score_all` + `reachability_audit.py`
signals unchanged. This tests whether the gate's SKIP and DISCARD branches behave sanely before investing in the
harder, higher-setup CONSOLIDATE-improves-MRR claim (batch 2, which needs a held-out relation-type withholding
split).

## Falsifiable predictions summary (HARD-PASS / HARD-FAIL, restated compactly)

- **P(cheap-decisive-slice, batches 1+3, passes):** thresholds on existing, already-proven signals; simplest test.
- **P(full pilot, all 4 conditions jointly, HARD-PASSes):** the harder, compound claim.
- **P(surprise signal is genuinely non-redundant with schema-fit, i.e., avoids the R7/MIR-collapse failure mode):**
  the single biggest open uncertainty, and the one most worth resolving first since it determines whether the
  keystone spec in Section 5 is a real third signal or a relabeled schema-fit.

## Cross-thread synthesis

- Directly extends `research_additive_map_builder_integration_endgame_2026-07-13.md`'s Full-stage item 4 ("ingest
  hook... periodic re-fit / schema-gated fold-in, the CLS systems consolidation analog") — this note is that
  item's detailed design.
- Composes with `wave14b_m2_consolidation_design.md` (the original 2026-05-18 M2 design, which already proposed a
  5-step consolidation loop with need x gain replay-selection scoring) but CORRECTS it: `wave14b_r7_replay_literature.md`
  and `wave14c_random_replay_mechanism_research.md` subsequently falsified static/structural need x gain-style
  prioritization as a REPLAY-selection mechanism on this substrate. This note's ingest gate targets a different
  decision (what becomes foundational) and is designed from the start to be closed-loop, per that lesson, rather
  than repeating the R7 failure mode under a new name.
- Composes with `notes/research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md` — the
  schema-fit metric proposed here is literally the same `reachability_audit.py` machinery that note validated as
  a real-but-modest, degree-adjacent relational-failure predictor; this note proposes a SECOND use for that same
  tool (ingest-gate input, not just diagnostic).
- Consistent with `project_grounding_subsumed_by_measured_attribute_foundation_...` (grounding-as-foundation) and
  `project_foundation_conjunction_modules_ingest_real_measured_nonadditive_data_...` (foundation build-vs-research
  distinction, real-measured-data sourcing for conjunction modules) — this note's consolidation loop is the
  mechanism by which BOTH the LLM-generated factual core and the real-measured conjunction modules would get
  folded from provisional ingest into the foundation over time, once either source is live.
- The Duszkiewicz 2019 two-novelty-system distinction (common vs. distinct novelty routing to different
  consolidation speeds) is a genuinely new biological input this cycle — not previously represented in the
  wave14b/14c replay research, which focused on priority-vs-random for REPLAY SELECTION, not on novelty-graded
  ROUTING of what becomes foundational.

## Substrate-product implications

1. The keystone prediction-error trigger costs ZERO new scoring mechanism to build — it is a threshold/routing
   layer on `additive_map.score_all`, already VET-confirmed. This makes the pilot genuinely cheap relative to its
   information value.
2. The schema-fit metric likewise costs zero new scoring mechanism — `reachability_audit.py` already exists and
   is already validated as a real (if modest) relational signal. Reusing it here is a second product use for
   already-sunk validation work, not a new investment.
2b. The recurrence floor is the cheapest of the three (a count) and should be evaluated first in any
   implementation, both for cost and because it is the strongest defense against a single ingest error becoming
   permanently foundational — the most product-safety-relevant of the three gates.
3. If the pilot's batch-2 (genuine-novel-reliable) condition fails specifically on MRR-improvement while the gate
   itself routes correctly, that is a signal to invest in the FOLD-IN mechanism (making consolidation functionally
   effective), not to redesign the gate — a materially different, and cheaper, fix.
4. The distinct-novelty "flag for provenance review" branch (Section 4B) is a concrete, product-relevant safety
   valve: it means the substrate does not blindly foundationalize anything that is BOTH shocking to its current
   model AND recurs in a single ingest batch — exactly the profile of a systematic labeling error or an
   adversarial/out-of-distribution data source, which is the failure mode a foundation built from external tools
   (per the PIVOT) needs to guard against most.

## Citations (verified count: 13 distinct sources across 2 lit-scans, cross-checked for internal consistency by
director; primary-source full-text could not be independently extracted for 2 items, flagged below — treat as
reported via abstract/secondary-source, not independently verified in full)

**Schema-consolidation biology:** Tse et al. 2007, *Science* 316:76-82, DOI 10.1126/science.1135935 (verified via
Science/PubMed abstract); Tse et al. 2011, *Science* 333:891-895, DOI 10.1126/science.1205274 (verified via
Science/PubMed abstract); van Kesteren, Ruiter, Fernandez & Henson 2012 (SLIMM), *Trends Neurosci* 35:211-9
(verified via ScienceDirect abstract; primary PDF text-extraction failed, mechanism reported via abstract +
secondary citations); Gilboa & Marlatte 2017, *Trends Cogn Sci* 21:618-631 (verified via PubMed abstract; primary
PDF text-extraction failed beyond abstract-level claims); McClelland 2013, *J Exp Psychol Gen* 142:1190-1210, DOI
10.1037/a0033812 (existence + qualitative characterization verified via search-result abstracts and secondary
citations; primary-source math/simulation detail NOT independently extracted — flagged "reported, not verified"
for fine-grained mechanism); a 2026 critical piece questioning SLIMM's fMRI support ("Predictions and declarative
memory encoding... slim pickings for SLIMM," *Phil Trans R Soc B*) noted at title-level only, not independently
fetched.

**Prediction-error / recurrence biology:** Lisman & Grace 2005, *Neuron* 46:703-713, PMID 15924857 (verified via
PubMed/ScienceDirect); Duszkiewicz, McNamara, Takeuchi & Genzel 2019, *Trends Neurosci* 42:102-114 (verified via
PMC6352318); Takeuchi et al. 2016, *Nature* 537:357-362, DOI 10.1038/nature19325 (verified via Nature); SWR
selective-consolidation review, PMC6794196 (verified, general review-level claim); Farooq & Dragoi 2024, *Science*,
PMC10659301 (verified — the conflicting-evidence caveat on novelty-as-sole-replay-driver); Schapiro & Turk-Browne
2017, *Phil Trans R Soc B* 372:20160049 (verified via PMC5124075); regularity-extraction-after-few-presentations
finding (auditory statistical-learning literature, PubMed 18271740) — reported, single-paradigm evidence, not
independently cross-verified across paradigms.

## Deflated confidence (lit-scan calibration: deflate 0.15-0.25 off undeflated read; novel-synthesis capped at 0.50)

- P(cheap-decisive-slice — batches 1+3 pass on the already-fitted additive_map) = **0.45** (undeflated ~0.60-0.65;
  these route through already-VET-confirmed signals with simple thresholds, but the specific thresholds
  SCHEMA_FIT_MIN/SURPRISE_MIN/RECURRENCE_MIN are picked, not derived, so real miscalibration risk remains).
- P(full pilot, all 4 conditions jointly, HARD-PASSes) = **0.28** (undeflated ~0.45-0.55 given solid ingredients;
  deflated for compound-joint-condition risk plus the genuinely novel batch-2 fold-in-improves-MRR claim, which
  has no direct precedent on this substrate; capped well under the 0.50 novel-synthesis ceiling).
- P(the surprise signal is genuinely non-redundant with schema-fit, i.e., avoids the R7/MIR-style collapse) =
  **0.30** (the single largest open uncertainty; the argument for why it should differ from the falsified MIR case
  — different coordinate geometry, k=24 KGE-style vs. rank-1 Hebbian delta-rule — is plausible but untested, and
  the project has one directly-relevant precedent where a structurally similar idea failed for a subtle
  collapse reason that was not obvious in advance).
- P(the Duszkiewicz-style common/distinct novelty routing meaningfully improves over a single flat surprise
  threshold, i.e., the provenance-review branch catches real errors rather than adding needless friction) =
  **0.35** (plausible design, no internal or external quantitative evidence either way yet — flagged as the
  cheapest thing to drop first if the pilot shows it isn't earning its complexity).

## Next-drill candidate

If the cheap-decisive-slice (batches 1+3) is piloted and passes: the natural next drill is whether the
surprise-signal-independence question (the 0.30 P above) can be answered analytically rather than empirically —
i.e., whether the additive-map's k=24 coordinate geometry has a closed-form argument (analogous to the wave14c
rank-equivalence proof that found MIR's collapse) for when `score_all`-based surprise IS or ISN'T redundant with
reachability-based schema-fit. That would be a `free-probability` / `random-matrix-theory` or
`network-science-graph-theory` field question (both currently Tier-1 in the field advisor) — closed-form
independence conditions between a KGE-distance score and a graph-reachability score, rather than another empirical
pilot. If the pilot instead shows batch-2's MRR-improvement failing while gate-routing is correct: the next drill
is the FOLD-IN mechanism itself (does direct compose+insert actually shift `(X,D)` in the direction that improves
held-out prediction for the newly-consolidated relation, or does it need the full SGD re-fit even on the
fast-track path) — a `sparse-coding-compressed-sensing` / `AMP-VAMP`-adjacent reconstruction-fidelity question.
