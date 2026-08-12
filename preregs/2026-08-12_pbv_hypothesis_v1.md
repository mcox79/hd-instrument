# PRE-REGISTRATION -- exp_pbv_hypothesis_v1 (2026-08-12)

Anchor: `pbv_hypothesis_v1`
Cell: `experiments/exp_pbv_hypothesis_v1.py`
Organ changes under test: `hdlab/grounding_acquisition_loop.py` (69bc0223f),
`hdlab/reading_grounding_loop.py` (4ce71ceaf)
Basis: `notes/brain_fidelity_audit_word_learning_2026-08-12.md` Section G (G.1 rows 1-3, G.4.1)
WIRE STATUS: **VET_PENDING only.** No promotion is proposed by this cell.

Written BEFORE any run of this cell. Organ self-tests were run first (they are formula gates, not
the experiment); their results are stated in "already measured" below and are not what this
pre-reg adjudicates.

---

## 0. WHAT IS BEING CLAIMED, AND WHAT IS EXPLICITLY NOT

CLAIMED: the reading path now has a hypothesis object -- one carried referent hypothesis per word,
with a persisting strength, verified at each informative encounter, abandoned and re-proposed on
disconfirmation.

**NOT CLAIMED: that this fixes sense selection.** Section G.2 measured the sense-selection failure
as context-INSENSITIVITY (C1 swap drop 0.0100 against a pre-registered requirement of 0.05, v2
primary `subject` index). A missing-hypothesis gap does not predict context-insensitivity; they are
two different defects. This cell does not measure sense selection and no result from it may be
quoted as bearing on it. If a connection is later found it requires its own evidence.

**NOT CLAIMED: that PBV raises grounding quality.** Quality is measured here (B4) but it is a
secondary band. The primary question is whether the MECHANISM is present and can fail.

## 1. PRIOR-WORK CHECK (substrate-KB, run before authoring)

Query: "propose but verify single hypothesis word learning cross-situational persisting strength
abandon re-propose". Top hits: `propose` (0.3154 -- a VerbNet/WordNet lexeme entry, not prior arc
work); `notes/research_combined_dictionary_consequence_word_learning_tool_2026-08-06.md::chunk029`
(0.2803 -- Frank/Goodman/Tenenbaum **Bayesian** cross-situational learning, i.e. the COMPETING
model family PBV is defined against, not this mechanism); nothing else above 0.27.
**No prior arc cell implements a carried hypothesis. This is novel, not a rediscovery.**

## 2. THE MECHANISM (and where each piece is REUSED, not reinvented)

| piece | organ | reused verbatim? |
|---|---|---|
| PROPOSER | `reading_grounding_loop.canonicalize` | YES -- unchanged function, unchanged argmax. Section G.2 established its single-winner/no-runner-up shape is ALREADY PBV. What changed is that it is called per ENCOUNTER on ONE trace's context vector, not once per item on `np.sum(all traces)` |
| informative-encounter filter | the SAME `canonicalize` call -- its no-match self-return is the "uninformative" signal | YES -- no second mechanism |
| VERIFICATION SITE | `grounding_acquisition_loop.Library.flag` (the existing trace-append / "an encounter happened" point) | YES -- no new organ |
| persisting strength | new `Hypothesis.strength`, Bush-Mosteller update (Stevens 2017 Hybrid Pursuit) | new (4 lines); `patience` was NOT repurposed -- it is a give-up counter on a different axis and conflating them would have been the name-only match the audit flagged |
| commit gate | consolidation_pass's existing `mdl_gate_fn` extension point | YES -- zero edits to `consolidation_pass` |
| independent judge for revision quality | `hdlab.grounded_similarity` (Lancaster + Brysbaert) | YES -- and it is NOT in the acquisition path's import closure (audit A.1), which is what makes it independent of the metric being judged |

Constants (all HYPOTHESIZED, all in `grounding_acquisition_loop` / `reading_grounding_loop`):
`PBV_INIT_STRENGTH=0.5`, `PBV_GAMMA=0.5`, `PBV_ABANDON_STRENGTH=0.2`, `PBV_COMMIT_STRENGTH=0.6`,
`PBV_INFORMATIVE_MIN=0.30`, `PBV_MAX_REVIVALS=2`.
Justification: from 0.5, two consecutive disconfirmations reach 0.125 < 0.2 (ABRUPT switching,
Trueswell 2013), while a 3x-confirmed hypothesis survives one disconfirmation (Pursuit's persisting
strength). `PBV_COMMIT_STRENGTH=0.6 > PBV_INIT_STRENGTH=0.5` makes it structurally impossible to
bank on the encounter that proposed (Horst & Samuelson 2008: fast mapping is fragile, needs
re-exposure).
**CALIBRATION AMENDMENT POLICY:** `PBV_INFORMATIVE_MIN` is the one constant that may be amended at
SMOKE, and only against the measured informative-encounter rate (diagnostic D1), never against a
pass/fail band. Any amendment is disclosed in the results note with both the before and after rate.
No other constant may be moved after this file is committed.

## 3. ARMS (one corpus, one stream, four arms)

Corpus: the EXISTING reading-path corpus -- `build_curriculum_pool()` (OneStop Ele 0-50 + Int
50-100 + process_articles) then the four cycle-2 segment pools (`ele_cont`, `int_cont`, `adv_new`,
`bio_new`). Identical to what `exp_definitional_grounding_v5` reads, so results stay comparable to
the v5 baseline. **The 117,642 newly acquired OpenStax sentences are NOT ingested by this cell.**

- **A_BASELINE** -- the current path: `pbv=False`, `refuse_non_groundings=True`. Sum-then-argmax at
  the consolidation gate. This is the on-disk mechanism, re-run on this exact stream so the A/B
  comparison cannot drift.
- **B_PBV** -- `pbv=True`, PBV fns installed, `revive_terminal=True`.
- **C1_INJECT_WRONG** -- B's stream, but for each of N sampled target lemmas a deliberately WRONG
  hypothesis is injected at strength 0.9 after its first encounter. "Wrong" = an eligible anchor
  drawn deterministically from the anchor pool that is NOT the one B's own mechanism proposed for
  that lemma. Strength 0.9 (not 0.5) so abandonment requires genuinely accumulated disconfirmation,
  not fragility.
- **C2_INJECT_RIGHT** -- identical to C1 in every respect except the injected object is the one B's
  own mechanism proposed for that lemma, also at 0.9.

C2 is a **NON-TRIVIALITY CONTROL, not evidence of correctness.** It exists solely because a
mechanism that abandons everything would pass C1 vacuously. It is circular with respect to
"correct meaning" (the injected object is the substrate's own choice) and must never be reported
as accuracy.

## 4. PRE-REGISTERED BANDS

### PRIMARY (the can-fail test that matters most). All three required.

- **P1 -- injected wrong hypotheses are abandoned:** C1 abandon rate **>= 0.80**
- **P2 -- and not indiscriminately:** C2 abandon rate **<= 0.30**
- **P3 -- separation:** (C1 abandon rate - C2 abandon rate) **>= 0.50**

FAIL BAND (any one of these = the build has failed, regardless of any quality number):
C1 < 0.60; OR C2 > 0.50; OR separation < 0.30.
MIDDLE_BAND: anything between. A MIDDLE_BAND result is reported as inconclusive, not as a pass.

**FALSIFIES THE BUILD:** a wrong hypothesis surviving contact with disconfirming evidence (P1
low). Also falsifying, and equally fatal: P1 high WITH P2 high -- that is not verification, it is
churn, and it would mean the abandonment machinery is not reading evidence at all.

### SECONDARY (mechanism is doing PBV, not something else)

- **S1 -- revision actually happens:** revision rate (fraction of items that ever held a hypothesis
  and abandoned at least one) in arm B, in **[0.02, 0.60]**. Below 0.02 the mechanism never revises
  and is therefore not doing PBV (a carried hypothesis that is never dislodged is just a first-
  encounter snapshot). Above 0.60 it is thrashing, and the banked meanings are whichever encounter
  happened to come last.
- **S2 -- abrupt not smooth:** among revised items, the median number of encounters between a
  PROPOSE/REPROPOSE and the ABANDON that ends it must be **<= 4**. PBV switches abruptly.
- **S3 -- yield does not collapse:** arm B grounded count **>= 0.25 x** arm A grounded count. A PBV
  path that grounds almost nothing has traded the defect for a different one.

### DIAGNOSTIC (reported, no pass/fail attached)

- **D1** informative-encounter rate in arm B. Medina's census is ~7% highly informative / ~90%
  uninformative; our filter is a coarse proxy for that and is NOT expected to reproduce 7%. Reported
  so the calibration is visible, not to be scored.
- **D2** revision QUALITY: for each revised, banked lemma, `grounded_similarity(lemma, first_obj)`
  vs `grounded_similarity(lemma, final_obj)`. Reported as (n_better, n_worse, n_tied, n_uncovered)
  and mean delta. **Explicitly caveated:** `grounded_similarity` is concrete-biased (audit G.1 row
  8) and caps at `GROUNDED_CAP=0.45` for 16.4% of scored pairs, so coverage will be partial and a
  null here is weak evidence either way. This is a diagnostic precisely because it cannot bear a
  verdict.
- **D3** memory cost: bytes of hypothesis state (Hypothesis + hypothesis_log + rejected) per item
  and in total, and the retained-trace bytes, arm B vs arm A.
- **D4** arm A vs arm B agreement: for lemmas both arms ground, how often do they agree on the
  object? Low agreement means the two mechanisms genuinely differ; high agreement would mean the
  build changed the shape without changing the outcome.

### CARDINALITY / INTEGRITY GATES (a verdict is refused if any fails)

- All 4 arms present in `metrics.json`, all 5 segments read by each arm.
- Arm A's grounded count must be within +/-2% of the v5-comparable re-run, or the deviation is
  reported as a harness discrepancy before any A/B claim is made.
- No `(X, GROUNDED_MEANING, X)` fact in any arm (tautology gate, already enforced by the organ).
- No closed-class object in any arm.

## 5. DISCLOSED LIMITATIONS (stated before the run, not after)

1. **Hypotheses are NOT persisted across a `foundation_persistence` save/load cycle.** That module
   is owned by another agent this session and was deliberately not edited, so `library_pending.json`
   carries no hypothesis field. This cell therefore runs all five segments **in one process per
   arm** with no reload. A production multi-session run would silently lose every standing
   hypothesis at each reload. This is a real, unfixed gap, not a test artifact.
2. `PBV_INFORMATIVE_MIN` is a threshold on a distributional cosine. It is a proxy for referential
   clarity, not a measurement of it. A brain-faithful informativeness signal is not built here.
3. The proposer's METRIC is still distributional relatedness, not reference (audit B.2.2). This
   build fixes the missing hypothesis, not the wrong metric. Both were named; only one is addressed.
4. Arm C's "wrong" injection is a distractor anchor, not a semantically-verified wrong meaning. It
   tests that DISCONFIRMING EVIDENCE dislodges a held hypothesis. It does not test that the
   substrate can tell right from wrong meanings.
5. The self-test fixture had to be built with only two seed anchors. With a larger seed set of
   mutually co-occurring words (engine/tractor/barn/harvest in one scene) every anchor's profile is
   nearly the same vector, the per-encounter argmax flips, and PBV thrashes and refuses to bank.
   That is real behavior and it is exactly what S1's upper bound and S3 exist to catch at scale.

## 6. ALREADY MEASURED (organ self-tests, before this pre-reg, not the experiment)

`python -m hdlab.grounding_acquisition_loop` -- 14/14 pass, incl. backward compat (flag without
PBV fns leaves hypothesis state untouched), the PROPOSE/CONFIRM/DISCONFIRM/ABANDON/REPROPOSE event
trajectory, uninformative encounters leaving strength EXACTLY unchanged, a 3x-confirmed hypothesis
surviving one disconfirmation, and bounded revival.
`python -m hdlab.reading_grounding_loop` -- 14/14 pass, incl. `canonicalize_fast` byte-identical to
the reference loop under ties/zero-norm anchors/eligibility filtering, and the injected-wrong-
hypothesis discriminator WITH its non-triviality control.
`pytest verification/` -- 267 passed, 3 skipped. All 6 existing `foundation_persistence` snapshots
(v1, v2 and their smoke/control copies) load unchanged with `hypothesis=None`.

## 7. RUN PLAN

SMOKE: `--mode smoke` (limit 1500 sentences/segment, 30 injection targets). Gate: all four arms
complete; the C1/C2 discriminator FIRES at smoke scale (P1/P2/P3 evaluated on the smoke sample) --
a smoke that cannot fire the discriminator is not a gate. `--timeout` from the smoke's measured
wall-clock x 6 with a 1800 s floor.
FULL: local only if smoke wall-clock x scale-factor stays under the local budget; otherwise the
cell is filed and the FULL run is routed to `remote_cpu_queue` by the orchestrator (this role
cannot push).
Progress logging: per-chunk `print(..., flush=True)` per section 17 if `timeout_s >= 1800`.
