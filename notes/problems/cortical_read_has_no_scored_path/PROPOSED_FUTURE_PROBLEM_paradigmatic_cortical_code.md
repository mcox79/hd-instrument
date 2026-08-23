# PROPOSED FUTURE PROBLEM (drafted by solver-B, 2026-08-23, for the strategy session to file or discard)

**Working slug:** `cortical_read_needs_a_paradigmatic_code`
**Parent:** falls out of `cortical_read_has_no_scored_path` (REFUTED) -- it names the ONE lever that
result identified. Distinct from the already-filed `cortical_read_never_tested_where_it_matters`
(that was the powered *test*, now answered negative; THIS is a *build* of a new representation).

> ⚠️ This is a solver-B PROPOSAL, not a filed problem. Filing is the strategy session's lane
> (owner ruling Q113). I did not create a problem folder or touch `notes/` outside my own.

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

The cortical read failed its fair test for one diagnosable reason: the "settled knowledge" it stores
captures **which words appeared together** and **how concrete a word is** -- but not **which words
MEAN similar things**. In the brain, cortical semantic memory is a *distributed, overlapping* code:
similar concepts have similar patterns, which is what lets you recognise a concept in a situation
you were never trained on. Our consolidated code does not have that shape. **Build a consolidated
code whose similarity tracks MEANING (second-order structure), and re-run the fair test to see if
the cortical read can then recognise a concept in a new situation where word-counting can't.**

## 2. WHY THIS ONE

`cortical_read_has_no_scored_path` proved (powered, fair, brain-foundational) that the cortical read
adds nothing beyond "prefer concrete words" in the regime that should favour it. It also proved the
bottleneck is the **representation**, not the ranking rule or retrieval dynamics -- an attractor
cannot retrieve structure the store does not hold. So this is the *only* lever that could make the
organ earn a place on the live path. Everything else about the cortical read is downstream of it.
**High value, and unusually well-instrumented: the fair test already exists** (see section 7), so
this is a representation build against a ready-made, powered evaluation -- not a build plus a new eval.

## 3. MEASURED vs INFERRED

**MEASURED (solver-B, 2026-08-23, `data/solverB_cortical_generalization_v1/metrics.json`):**
- On the generalisation regime (target never co-occurred with the cue words; n=177-188/seed, 3
  seeds), the paradigmatic sensorimotor space's hit@10 (0.056-0.067) is *identical* to a cue-blind
  concreteness prior (0.056-0.074) and clears it at NO k on NO seed. The generalisation signal IS
  concreteness.
- The first-order context space is worse still (hit@10 0.017-0.022, at the frequency floor).

**INFERRED, NOT MEASURED (this is the problem to settle):**
- That a **second-order / paradigmatic** consolidated code (where *dog* is near *cat* because they
  occur in similar contexts, not because they co-occur) would clear the concreteness floor on the
  generalisation regime. This is a hypothesis. It is motivated by the brain (the distributed
  overlapping code IS pinned) but the specific CONSTRUCTION (e.g. reduced-dim co-occurrence, a
  learned hub fusion) is OUR-INVENTION-UNDER-TEST and must be labelled so.

## 4. ALREADY TRIED (do not redo)

- **Context space (first-order accumulated context vectors):** fails on generalisation (at the
  frequency floor). Do not re-run.
- **Sensorimotor spoke space (paradigmatic-but-concreteness-dominated):** fails -- it IS the
  concreteness floor. Do not re-run as-is.
- **The cloze-with-co-occurrence-floor task, and the similarity-statistic family:** exhausted; the
  answer is the same each time. The missing thing is a **better representation**, tested on the
  EXISTING generalisation instrument.

## 5. VERIFY BEFORE YOU START

- `python experiments/solverB_cortical_generalization_v1.py --mode full --seeds 3` -- reproduce the
  baseline this must beat (SPOKE/BOTH at the concreteness floor on the unseen regime).
- `python tools/before_you_start.py "second order paradigmatic cortical code LSA consolidation"`.
- Read `hdlab/cortical_recall.py:build_cortical_index` -- the space is the lever; the cue/rank code
  is fine.
- Check whether a second-order code is PINNED or OURS: read `notes/ORGAN_MAP.md` and
  `tools/organ_map_cite.py` for anything already ruled out about consolidated-code shape.

## 6. THE BAR

**A paradigmatic consolidated code whose cortical read CLEARS the CONCRETENESS floor's upper CI on
the UNSEEN-co-occurrence regime, CI-separated, on the existing instrument (>=100 unseen items/seed,
3 seeds), while the information-free twins (scramble, random) LOSE.** Chance and the concreteness
prior are BOTH mandatory floors -- concreteness because it is the confound that has now killed this
organ's story twice. A legitimate outcome is that no brain-faithful code clears it, in which case the
cortical read is a genuine dead end and B3' should be shelved, not merely NEEDS_ADAPTER.

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the space to change | `hdlab/cortical_recall.py::build_cortical_index` (solver proves in `experiments/`, does NOT edit hdlab) |
| the ready-made fair test | `experiments/solverB_cortical_generalization_v1.py` (train simplewiki, test fiction, seen/unseen split, concreteness floor) |
| the current codes | `Substrate.profile()` (context), `hdlab/sensorimotor_spoke.py` (spoke) |
| brain frame | CLS interleaved replay extracting structure (McClelland/O'Reilly 1995); LSA as a model of human semantic acquisition (Landauer & Dumais 1997); ATL amodal hub (Lambon Ralph 2017) |

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 The `8/8` consolidation-sensitivity or any exact-key score as evidence of quality.
- 🚫 The cloze-with-co-occurrence-floor task -- it is biased toward counting and is exhausted.
- 🚫 "sensorimotor space generalises" -- it does not; it is the concreteness floor.
- 🚫 Presenting a second-order/SVD/learned-hub construction as PINNED brain -- it is brain-motivated
  but OUR-INVENTION-UNDER-TEST; label it so.
