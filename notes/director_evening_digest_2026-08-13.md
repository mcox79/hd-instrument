# Director evening digest -- 2026-08-13

The fuller narrative behind the 2026-08-13 evening rewrite of `notes/STATUS.md`. Every number
below was read off the cited `metrics.json` at HEAD `804b02246` on 2026-08-13 night.

**The day's real conclusion in one sentence: four cells tested CONTEXT-FREE word-pair similarity,
all four failed, and per the same day's brain drill that framing is itself un-brain-faithful --
the brain never computes a context-free word-word similarity.**

---

## 1. `exp_wire_definitional_v1` -- band `MASS_NOT_CONTENT` (CLOSES the former top item)

`data/exp_wire_definitional_v1/metrics.json`, `run_mode: full`, no `verdict` key; the band field
reads `MASS_NOT_CONTENT`. Held-out B, n=661: ON recall@1 **0.037821** vs OFF **0.007564**
(delta **+0.030257** against a +0.03 bar) -- but **SHUFFLE is identical to ON to six decimal
places on every held-out metric**. FREQMATCH delta **+0.0015**.

The manipulation demonstrably worked, so this is a valid control and not a smoke failure: the
injected-A circularity witness shows ON `live_banked` **394/394** correct vs SHUFFLE **0/394** at
identical banked counts, and the OFF regression check reproduced 386 == 386.

**Interpretation: the gain is fact MASS, not fact CONTENT.** Banking 394 definitional facts raises
availability by ~+0.53 and drags recall along with it; banking 394 facts whose subject-object
pairings have been SHUFFLED does the same thing to six decimals. Nothing the definitions SAY is
being consumed. This closes the one route that promised to go AROUND the comparator by supplying
pre-formed facts. Full entry, with the reopen criterion: `notes/STATUS_LESSONS.md` DO NOT REDO 23.

*Record note:* this entry was already on disk in `STATUS.md` and `STATUS_LESSONS.md` before this
rewrite (it landed earlier the same day), so no new DO-NOT-REDO entry was needed for it.

## 2. `exp_distinctiveness_weighted_composition_v1` (dbac1ae9c) -- `HARD_FAIL_SHAPE`

Planned finding: distinctiveness WEIGHTING does not help. weighted-minus-uniform is
**-0.0175** on B_CSKG (coverage 1.000, n=999) and **-0.0004** on C_CSKG_NOLEXREL (n=639), against
a +0.08 pass bar. The zero-noise **analytic** arms reproduce the NULL (B 0.6545 weighted vs 0.6443
uniform; C 0.0826 vs 0.0790 -- both differences are an order of magnitude below the bar, and the
sign is not even stable across supplies: A is -0.0152), so this is not an instrumentation defect.

Scope, which must travel: this refutes distinctiveness weighting **as implemented** (log-IDF).
It does NOT refute every distinctiveness transform -- PMI is also logarithmic, and the realised
weights span only ~1.5-1.75x across shared features (`weight_shared_ratio_p95_p05` 1.5421 / 1.7481
/ 1.6346), so the manipulation had little dynamic range to work with.

**The UNPLANNED finding is the important one.** Deleting ConceptNet's synonym/relatedness edges
collapses the comparator from rho **0.5361** (B) to **0.0804** (C) on the same construction, while
raw sensorimotor scores **0.3003** on those same 639 pairs. The comparator was, to a first
approximation, an embedded similarity LOOKUP TABLE: its apparent competence was carried by
lexical-relation edges that state the answer, not by composed features. Recorded as CORRECTION C8.

## 3. `exp_differentia_feature_supply_v1` (9825510bf) -- `HARD_FAIL` on both clauses

Stage 1 failed its own coverage gate at **29 usable SimLex pairs** (bar 50) and correctly diagnosed
DOMAIN rather than volume: the biology segment supplies 1,111 terms but only 3 pairs. Prereg
amendment A1 (`64a4ea4c2`, filed BEFORE extraction and BEFORE any arm) authorised a supply fix -- 169,982 COPULA/GLOSSARY facts extracted from simplewiki in about five minutes,
taking coverage of SimLex-999 from 2.9% to **35.0%** and 29 pairs to **350**.

Supply is therefore no longer the binding constraint, **and the answer is still no**:
A_DIFFERENTIA **0.0247**, B_GENUS_ONLY **0.0179**, B_STRICT_GENUS **-0.0464**,
D_CSKG_NOLEXREL **0.0751**, E_SCRAMBLE **-0.0235**, C_GROUNDED_RAW **0.2759**.
A-B is **+0.0068** with CI **[-0.1179, +0.1395]** (includes 0) and A <= D. Neither clause survives.

Controls that make the negative informative rather than a null run:
- **Positive control:** arm D reproduced the predecessor exactly -- rho_weighted **0.0804** at
  n=639 vs prior **0.0804**, `abs_deviation` **0.0**, `reproduced: true`.
- **Leak controls excluded 216 of 566 covered pairs** before the primary: L1 direct leak (definiens
  names the other word) **145**, L2 synonym-statement **113**, L3 same source sentence **8**.
- `forbidden_conceptnet_edges_in_treatment_arms` PASS; `pattern_restriction_frozen_in_advance` PASS.

## 4. `exp_near_vs_far_diagnostic_v1` (804b02246) -- read `NEAR_COLLAPSE`, **caveat travels**

Read source SPLIT1_TAXONOMIC. Sensorimotor arm C: pooled **0.2759** CI [0.1727, 0.3798] ->
FAR (n=272) **0.3042** CI [0.1828, 0.4155] -> NEAR (strict shared-synset / shared-direct-hypernym
siblings, n=78) **0.1245** CI [-0.0926, 0.3315], null. Symbolic arms sit at chance in BOTH halves
(on FAR: A **0.0308**, B **0.0137**, D **0.0992**, none excluding 0).

**Two caveats that must travel with any citation of this read:**

1. **At n=78 the MDE is 0.2116.** The NEAR null therefore means COULD NOT DETECT, not proven zero.
2. **The balanced co-primary split does NOT show collapse.** SPLIT1B_WN_PATH_MEDIAN NEAR_G
   (n=218) is **0.2185** CI [0.0787, 0.3520] -- still significant, against FAR_G **0.2559**.

So the honest shape is **MONOTONE DEGRADATION as nearness tightens**, not a clean collapse.

Two further results from the same run:
- **CSKG-minus-lexrel is significantly NEGATIVE on NEAR:** D **-0.2146** CI [-0.4027, -0.0038],
  excludes 0. On the hardest pairs the symbolic graph is worse than useless.
- **No dual-coding separation:** CONCRETE **0.3123** [0.1933, 0.4234] vs ABSTRACT **0.2612**
  [0.0257, 0.4688] -- CIs overlap heavily.

## 5. Brain drill: the encoder / lexical semantics (471798502, scans ce2e99388)

`notes/brain_drill_encoder_lexical_semantics_2026-08-13.md` (`471798502`), plus five full
literature scans rescued verbatim from transient transcripts at `ce2e99388`.

Mechanism that matters: the brain separates near-neighbours via **DISTINCTIVE features** --
weakly-correlated and low-redundancy, therefore FRAGILE, which is why they are the first thing lost
in semantic dementia and why that syndrome's earliest errors are **coordinate confusions within a
category**. Riding on top is a **semantic-control system that applies GAIN** to context-relevant
features rather than selecting from a candidate list.

**Element E4, now the head item and UNTESTED:** our `concept_similarity(a, b)` is a bare two-argument
function with **no context port at all**. The brain never computes a context-free word-word
similarity, so the four cells above optimised an operation the reference system does not perform.

## 6. Research persistence

`data/literature_cache/` created (4fbe50f91) with add/find tooling, `index.jsonl`, and a passing
guard self-test. Before it, the repo held 65 PDFs and **every one was an experiment dashboard --
zero papers**. Five full lit scans were rescued from transient transcripts at `ce2e99388`.

The policy note `notes/research_persistence_policy_2026-08-13.md` is **WRITTEN BUT UNCOMMITTED**
(its commit call was declined; it remains untracked and is deliberately left that way here).

**CORRECTION TO RECORD (C9): experiment RESULTS are searchable.** The director_kb's last ingest
discovered **7,501** `metrics` sources (alongside 9,197 notes and 3,689 preregs), per
`data/director_kb_continuous_state.json`. An earlier same-day claim of the Director's that results
might not be searchable is WRONG. The KB's own retrieval encoder is `char_trigram_v1`
(`tools/director_kb_query.py:87`).

## 7. Two open items carried forward

**(a) `exp_encoder_swap_behind_fixed_brain_stack_v1` results are UNCOMMITTED.**
`data/exp_encoder_swap_behind_fixed_brain_stack_v1/metrics.json` is untracked (`git ls-files
--error-unmatch` errors on it); the prereg and cell are committed as `f36ba7626`. Its verdict is
HARD_PASS / `REFUTES_USER_CLAIM`, A_tuned **0.6386** vs B_char_trigram **0.0873**,
delta_AB **+0.5513**.

**(b) That verdict does NOT settle the trained-vs-simple question**, because the cell ran on the
encoder's OWN TUNING HARNESS: `experiments/exp_encoder_swap_behind_fixed_brain_stack_v1.py:93`
imports `exp_continuous_curriculum_learn_as_you_go_v1 as base_loop` -- the same base loop as the
08-01 transfer cluster -- and takes its assembly loop, readout and held-out split from it. A
neutral-ground test is still owed.

Its own **span control** says the same thing from the other side: when localization is given, all
five encoder arms tie at **1.000** (A_tuned, A0_frozen_base, B_char_trigram, C_ppmi,
D_random_init_twin), with only E_scramble_floor at 0.0497. Everything the tuned encoder buys on
this harness is localization, and localization is exactly what the harness supplies.

**(c) USER QUESTION, OPEN: is the GAP-DRIVEN LEARNING LOOP functioning?** A HUMAN, not the loop,
noticed that the differentia supply was biology-only -- exactly the kind of gap the loop is supposed
to name for itself. An audit is in flight from another agent and will land at
`notes/gap_driven_learning_loop_audit_2026-08-13.md`.

## 8. The earned discipline (STANDING DISCIPLINE 5)

**Before gating on a benchmark, check that the BRAIN performs the operation the benchmark scores.**
Four cells in one day optimised context-free word-pair similarity, an operation the reference
system does not perform. A benchmark can be standard, well-controlled, well-powered and still
measure a function the reference system never computes.

This is **distinct from** STANDING DISCIPLINE 1 (floor-limited discriminators): those cells could
not RESOLVE an answer; these resolved one cleanly for a question worth little. Discipline 1 is
about power; this one is about whether the question was the right question at all.
