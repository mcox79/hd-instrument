# exp_dev hand-off — research: brain-faithful script/schema acquisition + consolidation rule

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_brain_script_acquisition_consolidation_2026-08-09.md` — director-requested
drill answering, from primary psych/neuro literature, what should FLAG a not-yet-understood narrative
gap, when a recurring event SCRIPT/SCHEMA should be COMMITTED vs stay episodic, and the GUARD's brain
basis, at SCRIPT grain (not word grain). Diagnosed this session: the currently-wired FLAG teacher
(`hdlab.consequence_learning_loop.teacher_verdict(signal_mode="signal_a_only")`, isolated verb-lemma
MET/UNMET polarity) is wrong-grain — no notion of a recurring event-type, no self-relative surprise
computation. Finding: two independent literatures (Event Segmentation Theory's computational model,
Reynolds/Zacks/Braver 2007; statistical event-structure learning, Baldwin et al. 2008/Stahl et al. 2014)
converge on a RELATIVE (self-referential, current-vs-own-recent-baseline) prediction-error signal as the
brain-faithful FLAG, not an absolute threshold. Separately: `hdlab/learner/core.py::per_cluster_gate` +
`mdl_select` (Perfors & Tenenbaum two-part-code MDL criterion, already returns the literal string
`KEEP_EPISODIC` on gate failure) is an ALREADY-BUILT, more principled implementation of the
Ghosh & Gilboa (2014) / Preston & Eichenbaum (2013) commit-vs-stay-episodic criterion than the currently
wired `schema_consistency_split_half` coherence heuristic — it is wired to two OTHER plugins for unrelated
cells, never to `grounding_acquisition_loop.py`.

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless
of pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable
bands, context pointers) — exp_dev owns exact implementation (exact corpus construction, exact CRP
concentration/stickiness parameters, exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_learner_mdl_gate_on_acquisition_traces_v1` (primary, do this first — cheapest, zero new grain, zero new corpus)

**Anchor pointer:** research note section 2 ("The CONSOLIDATION + GENERALIZATION rule") + section 8
anchor 1.

**Substrate-product reading:** if this HARD-PASSes (or produces a clean, harness-verified negative), it
resolves whether `hdlab.learner`'s MDL compression gate adds real discriminating power over the current
`schema_consistency_split_half`-only guard, on data this project ALREADY has results for — the cheapest
possible slice of this drill's design, with zero new mechanism risk (both organs already exist, tested,
independently). This directly operationalizes Ghosh & Gilboa's "non-specific/abstracted structure" schema
criterion (currently unimplemented — the guard only checks context congruency, never whether a genuinely
COMPRESSIBLE structural regularity exists across traces).

**Tier hint:** load-bearing if it changes ANY pass/fail verdict on the existing
`data/exp_unified_self_learning_loop_v6_replay_consolidation_smoke` items relative to the
`schema_consistency_split_half`-only gate — that would be direct evidence the two signals are
non-redundant and both matter. If it never changes a verdict on that item set, that is still informative
(the two signals may be correlated on this corpus specifically; the research note's section 5 corpus,
anchor 3, is designed to have a case where they should diverge — one-off/adversarial items with
superficially coherent context but no compressible structure).

**Why now:** cheapest possible test — `hdlab.learner.registry.learn(episodes, features,
hypothesis_space_spec={"candidate_plugins": ["ruleind"]})` + `hdlab.learner.core.per_cluster_gate` are
both already built, tested, and wired for other cells; this only requires adapting
`grounding_acquisition_loop.LibraryItem.traces` into the `episodes`/`features` shape `ruleind_plugin.learn`
expects (exp_dev owns the exact adapter) and adding the gate as a SECOND, conjunctive condition inside
`consolidation_pass` (AND, not OR, with the existing `schema_score >= schema_thresh` check — section 2 of
the research note specifies conjunction, not replacement).

**Design (from the research note, exp_dev owns implementation details):**
1. Write a thin adapter turning a `LibraryItem`'s accumulated `Trace` list into whatever
   `episodes`/`features` shape `hdlab.learner.plugins.ruleind_plugin.learn` requires (read that plugin's
   own docstring/signature — do not guess; it wraps `experiments/exp_parser_ruleinduction_cls_ppattach_v1.py`
   banked cell 29485).
2. Inside `consolidation_pass`, at the point `schema_score >= schema_thresh` is currently checked, ALSO
   fit `ruleind_plugin` over the item's traces and check `per_cluster_gate(result, min_compression_ratio=1.0)`
   (the existing default). BANK only if BOTH the schema-consistency check AND the MDL gate pass.
3. Report, per item in the existing smoke/full dataset: whether `schema_consistency_split_half` alone
   would have banked it, whether `per_cluster_gate` alone would have banked it, and whether the conjunction
   changes the verdict relative to the CURRENT (split-half-only) behavior — a 2x2 confusion breakdown, not
   just a pass/fail count.
4. Re-run the coherent-vs-scrambled and adversarial wrong-context self-tests already in
   `grounding_acquisition_loop.py::self_test` with the conjunctive gate substituted in, to confirm the
   guard's existing invariants (scrambled/adversarial items must never bank) still hold under the new gate.

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS**: the conjunctive gate changes at least one verdict relative to split-half-only on the
  existing item set AND all of `self_test`'s existing coherent/scrambled/adversarial invariants still hold
  under the new gate (zero regressions on the guard's hard invariants).
- **MIDDLE_BAND**: the conjunctive gate never changes a verdict on the CURRENT small item set (may be
  underpowered, not necessarily a negative on the mechanism — proceed to anchor 3's richer corpus before
  concluding the two signals are redundant) but all guard invariants still hold.
- **HARD-FAIL**: any coherent/scrambled/adversarial self-test invariant breaks under the new gate (the MDL
  gate creates a NEW false-consolidation path, e.g. a scrambled/adversarial trace set that happens to
  compress well) — this is the guard's one hard invariant and is never excused by "the gate is more
  principled in theory."

### 2. `exp_predictive_coding_relative_threshold_v1` (second — isolates the relative-vs-absolute signal question)

**Anchor pointer:** research note section 1 ("The ACQUISITION signal") + section 8 anchor 2.

**Substrate-product reading:** tests whether the EST-style relative (self-referential) prediction-error
signal is a real improvement over the current absolute `threshold_gate`, independent of the schema-grain
question anchor 3 addresses — isolates one variable at a time per the project's own design-gate discipline.

**Tier hint:** MEDIUM — informative regardless of outcome (a clean negative would mean the absolute
threshold is already adequate and the relative-signal literature, while real, doesn't matter at this
substrate's operating point; a clean positive licenses building anchor 3 with more confidence).

**Why now:** small, self-contained addition to `hdlab/predictive_coding.py` (one new function,
`relative_threshold_gate`, literature-pinned to Reynolds/Zacks/Braver 2007 Eq. 8: fire when
`residual_magnitude(t) / running_avg(residual_magnitude)_{t-1} >= threshold`, with the running average as
a 0.05-weighted low-pass filter per the cited paper) — no new corpus needed if a sequential stream of
prediction attempts already exists from a prior cell; exp_dev decides whether to reuse an existing
sequential eval or construct a minimal synthetic one.

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS**: relative-threshold boundary/flag detection F1 >= 0.75 against known/labeled boundaries
  (or, if no labeled-boundary corpus is available yet, >= the absolute `threshold_gate`'s own F1 by a
  non-trivial margin on a matched task) AND not worse than the current signal by more than 0.05 F1 in the
  worst case.
- **HARD-FAIL**: relative-threshold F1 < 0.50 — mandatory pre-check: confirm `residual_magnitude` itself
  discriminates a synthetic coherent-repeat sequence from a scrambled/shuffled-order control FIRST (same
  sanity-check discipline `grounding_acquisition_loop.py::self_test` already applies to
  `schema_consistency_split_half`); a flat result without this check passing is a harness bug, not a
  negative on the relative-signal mechanism.

### 3. `exp_script_grain_acquisition_loop_v1` (third — the full script-grain build, do only after 1 and 2 each independently clear or produce a pre-check-passed negative)

**Anchor pointer:** research note section 5 ("Cheap decisive test") + section 8 anchor 3 — the full design.

**Substrate-product reading:** the actual capability claim this drill targets — does the substrate
recognize a RECURRING EVENT PATTERN (not a single word's polarity) and correctly generalize it to novel
fillers, while never falsely promoting one-off or adversarial content. This is the test that would let the
project claim "comprehension generalizes to held-out narratives" at the script/schema level, not just the
lexicon-coverage level.

**Tier hint:** load-bearing — the capstone test of this drill's whole design. Do NOT attempt before
anchors 1-2 resolve (compounding three unvalidated primitives — MDL gate, relative signal, and the new
CRP-style soft-match/spawn library-keying logic — at once would make any negative uninterpretable, the same
confound-avoidance discipline the sister acquisition-loop note already established for its own two-halves
question).

**Design (from the research note, exp_dev owns implementation details):**
1. Build a synthetic multi-script corpus: >= 3 distinct recurring event-type "scripts" (role-typed scene
   templates), each realized in >= 4 instances with DIFFERENT named fillers (tests structural not lexical
   reuse), interleaved with >= 20% genuinely one-off non-recurring events (negative controls), plus a
   scrambled-sentence-order and a wrong-schema-neighborhood adversarial probe set.
2. Replace `Library`'s exact-lemma-string keying with a soft nearest-schema match: cosine of the incoming
   trace's context/situation-model register against each existing `LibraryItem`'s accumulated register
   bundle, with a "spawn a new `LibraryItem`" fallback when no existing item clears a minimum similarity
   (exp_dev decides the exact similarity threshold and any CRP-style stickiness/concentration-parameter
   analogue — the research note names the SHAPE, per Franklin/Norman/Gershman 2020's sticky-CRP, not exact
   constants).
3. Key each `LibraryItem`'s context vector off `hdlab.situation_model_accumulate.AccumulateRegister`
   (role-bound bundle across multiple episodes) rather than the current bag-of-content-words
   `context_vector` — exp_dev decides the exact role-vocabulary for the synthetic corpus.
4. Run K=5 `consolidation_pass`-style sweeps with BOTH the relative-threshold flag (anchor 2, if it
   cleared) and the conjunctive MDL+congruency gate (anchor 1, if it cleared) wired in.
5. Report per the research note's section 5 three measurements: boundary/flag quality (paired against the
   CURRENT `signal_a_only` flag on the identical corpus), schema-commit correctness (how many of the 3
   injected scripts reach `GROUNDED_*` by pass 5, with novel-filler generalization checked via a decode/
   apply call against the induced `ruleind_plugin` rule, not just a status flip), and false-consolidation
   resistance (0% of one-off/adversarial items ever promoted, at any pass).

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS** (both required): relative-threshold flag F1 >= 0.75 against known injected scene boundaries
  AND not worse than `signal_a_only` by more than 0.05 F1 on the identical corpus; the MDL+congruency gate
  promotes >= 2 of 3 injected scripts by pass 5 with correct novel-filler generalization on >= 1 held-out
  instance each, AND 0 of the one-off/adversarial items are ever promoted.
- **HARD-FAIL** (any one, subject to the mandatory pre-check): relative-threshold F1 < 0.50 (pre-check:
  `residual_magnitude` must first discriminate coherent-repeat from scrambled-order synthetic controls); any
  one-off/adversarial item reaches `GROUNDED_*` (guard failure, never excused by a pre-check); zero of the 3
  injected scripts reach `GROUNDED_*` by pass 5 (pre-check: `per_cluster_gate` must first fire `True` on a
  hand-constructed maximally-compressible synthetic trace set).

## Context pointers (files, not summaries)

- `notes/research_brain_script_acquisition_consolidation_2026-08-09.md` — full synthesis, all 3 lit-scan
  lane findings, section 1/2/3's per-mechanism owned-organ mapping tables, section 4's cross-thread
  synthesis with the two sister same-day notes, section 7's substrate-product implications.
- `notes/research_psych_acquisition_consolidation_loop_2026-08-09.md` — the sister WORD-grain drill (same
  FLAG->LIBRARY->CONSOLIDATE->GUARD->BANK shape, different grain — complementary, not competing); already
  covers Dumay & Gaskell 2007 sleep-not-just-time, Tamminen et al. 2010, Tse et al. 2007/2011, van Kesteren
  SLIMM, McClelland 2013, Warren et al. 2014 (the false-consolidation citation this drill's guard section
  extends with the specific vmPFC-congruency-circuit mechanism).
- `notes/research_script_half_synthesis_2026-08-09.md` — the sister SCRIPT-REPRESENTATION drill (VerbNet
  end-state matching, Schank/Abelson lineage, Kemp & Tenenbaum "Discovery of Structural Form" flagged there
  as unfilled for scripts — this drill's anchor 1 is a concrete first step toward filling that gap using
  `hdlab/learner`).
- `hdlab/grounding_acquisition_loop.py` — the module to extend: `Library`/`LibraryItem`/`Trace` (the
  not-yet-grounded store, currently lemma-keyed — anchor 3's soft-match-or-spawn target),
  `schema_consistency_split_half` (the existing context-congruency check, keep as one AND-gate input),
  `consolidation_pass` (the periodic sweep — anchor 1's wire-point), `surprise_order` (the existing
  Tamminen/Rasch selective-replay ordering, unchanged by this drill), `self_test` (the existing
  coherent/scrambled/adversarial invariant tests every anchor must continue to pass).
- `hdlab/predictive_coding.py` — `predict`/`residual`/`residual_magnitude`/`threshold_gate` (anchor 2's
  extension point; `residual_magnitude` reused as-is, only the gate comparison changes from absolute to
  relative).
- `hdlab/situation_model_accumulate.py` — `AccumulateRegister` (anchor 3's target register shape for
  keying library items by situation-model content instead of bag-of-words).
- `hdlab/learner/core.py` — `per_cluster_gate`, `mdl_select`, `KEEP_EPISODIC`, `glass_box_assert` (anchor
  1's target gate; already tested against `experiments/exp_learner_module_refactor_proof_v1.py`, read that
  proof script before writing the adapter).
- `hdlab/learner/registry.py` — `PLUGINS`, `learn()`, `apply()` (the top-level call anchor 1 uses;
  `ruleind_plugin` is the specific plugin to fit).
- `hdlab/consequence_learning_loop.py` — `teacher_verdict(signal_mode="signal_a_only")` (the CURRENT flag
  signal every anchor's paired comparison is measured against — do not modify this function; anchors add a
  parallel/alternative signal path, they do not remove the baseline).

## Contract section

- exp_dev owns: exact `ruleind_plugin` adapter shape for `LibraryItem.traces` (anchor 1), exact running-
  average decay constant and threshold sweep for `relative_threshold_gate` (anchor 2), exact synthetic
  corpus construction, exact CRP-style similarity threshold/stickiness constants, exact role-vocabulary for
  `AccumulateRegister` keying (anchor 3), exact cell/file naming, exact seed handling.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/MIDDLE_BAND/HARD-FAIL bands, the
  mandatory conjunctive (AND, not OR) structure of the two-signal guard, the mandatory pre-checks before any
  HARD-FAIL is accepted as a negative (per the standing "flat result = broken experiment" discipline), the
  strict sequencing (anchor 3 only after 1 and 2 resolve), and the glass-box/no-LLM-at-inference invariant —
  every organ named above is already owned; nothing in this build may introduce a trained/opaque external
  component.
- Honest calibration to carry into the pre-reg: P_deflated = 0.32 (capped at 0.50 per novel-synthesis rule,
  further deflated — see the research note's Calibration section for the full reasoning). The relative-signal
  principle (anchor 2) is the HIGH-confidence piece (independently cross-validated by two literatures); the
  CRP-style soft-match/spawn logic (anchor 3) is the genuinely novel, untested piece with no owned precedent.

## Autonomy declaration

exp_dev decides all exact implementation constants named above (adapter shapes, decay constants, corpus
construction, similarity thresholds, cell/file naming, seeds). The falsifiable bands, the mandatory
conjunctive guard structure, the mandatory pre-checks, and the anchor sequencing (1, 2 before 3) are NOT
exp_dev's to loosen or drop without flagging the change explicitly in the pre-reg.
