# COMPONENT-HEALTH AUDIT — grounded affective/goal COMPREHENSION organ

Auditor: Skunkworks (AUDIT-ONLY, independent). Date 2026-08-05. Branch `dataprep/mcguffey-graded-corpus`. LOCAL-only, no push.
Method: READ THE CODE + independent recompute off on-disk `metrics.json` (not docstring/label trust). Every number below cites its disk path; where I recomputed, I say RECOMPUTED. Deflationary — labels are treated as claims to be checked, not facts.

Scope note: this is a MEASURED health map, not a re-run of every cell. Where a cell's own metrics.json is the only artifact, I read the raw arm counts and recomputed the headline metric from them rather than trusting the stored summary string.

---

## HEADLINE FINDINGS (read first)

1. **WEAKEST LOAD-BEARING LINK = EVENT EXTRACTION, and its label is a MISLABEL.** The extraction that actually feeds the situation model measures **F1 = 0.232 ungated / 0.278 gated_structural / 0.297 FULL** (verdict MIDDLE_BAND) against independent gold — RECOMPUTED from raw counts (tp=11, n_pred=61, n_gold=34 -> P=0.180, R=0.324, F1=0.2316), path `data/exp_coherence_gate_extraction_correctness_independent_gold_v1/metrics.json`. The docstring `hdlab/situation_reader.py:34` still advertises "F1~0.64 on McGuffey LCCP gold, 29502". That 0.64 is (a) for a DIFFERENT, narrower "calibrated single-sentence role reader" (atom 29502), (b) on DIFFERENT gold (McGuffey LCCP, not the independent L04+L05 gold), and (c) NOT the number that governs the load-bearing extraction. Anyone reading "0.64" as the extraction's health is off by ~2x. Everything downstream (situation model, goal-typing, outcome-valence, goal-owner on real text) inherits recall 0.324 — you cannot bind, type, or attribute an event you never extracted.

2. **Two more real-health-worse-than-label components:**
   - **OUTCOME-VALENCE is split across two cells and the generative one HARD_FAILs.** `exp_goal_congruence_outcome_valence_v1` is labeled `HARD_PASS` (delta_acc +0.333) but **REGRESSES -0.400 on lexicon-covered items** (detector 0.400 vs baseline 0.800; RECOMPUTED) — it is a lexicon-MISS patch, not a drop-in. The genuinely-generative detector `exp_outcome_valence_detector_v1` is **HARD_FAIL: detection_acc=0.0** (vs 0.55 floor, N=38 real items) — path `data/exp_outcome_valence_detector_v1/metrics.json`.
   - **COREFERENCE is the most MATURE organ but its "beats-floor" headline is THIN.** Reputed HARD_PASS; measured, the raw match-or-allocate is `HARD_FAIL_LEARNABLE_DOES_NOT_BEAT_FLOOR` (learnable_f1=0.8710 vs recency_floor_f1=0.8581, **beats_recency=False**), and the strict-Cb pronoun lift (+0.037 B3-F1) does NOT propagate to the situation-model query in one test (strict_cb 0.583 vs recency 0.833). It is faithful and wired, but its lift over a trivial recency floor is marginal, not commanding.

3. **Registry audit** (`tools/capability_registry_audit.py`, 2026-08-05T20:14Z): 65 rows — WIRED=36, ISLAND=18, TRAPPED_SHARED=9. Of 36 WIRED hdlab modules only **7 are pipeline-reachable**; 29 are wired-but-not-reachable. **55 high-signal invisible islands** flagged. ToM (Sally-Anne) is one such island.

---

## PER-COMPONENT HEALTH TABLE

| # | Component | File | MEASURED status (disk) | HEALTH | On crit path? |
|---|-----------|------|------------------------|--------|---------------|
| 1 | EVENT EXTRACTION | `experiments/_temporal_ordering.py::extract_events`, `hdlab/situation_reader.py::_read_events` | F1 0.232 ungated / 0.278 gated / 0.297 FULL, MIDDLE_BAND (`exp_coherence_gate_extraction_correctness_independent_gold_v1`). Docstring "F1~0.64" = MISLABEL (different reader/gold). | **WEAK + MISLABELED** | **YES — root** |
| 2 | COREFERENCE | `hdlab/coreference_resolver.py` | pron-B3 F1 ~0.703; match-or-allocate 0.871 but beats_recency=FALSE (floor 0.858); iddem-query lift +0.035 (oracle 0.930); compositional gating HARD_PASS (delta 0.143). | **SOLID (faithful, wired) — but thin lift** | YES |
| 3 | THEMATIC-ROLE LABELING | `hdlab/frame_induction.py`, `hdlab/thematic_role_labeler.py` (VERB_FRAMES n=224) | in-vocab frame_primary 0.877 HARD_PASS (frame-ablation collapses to 0.0); cue-integration lift +0.264; end-to-end effective 0.769 (resolve_rate 0.80 = bottleneck, on-resolved 0.962); **OOV on REAL data: subj 0.833 but beats_position=FALSE (pos=1.0), obj 0.455** (`exp_frame_induction_oov_psych_real_v1` MIDDLE_BAND). | **SOLID in-vocab / WEAK OOV+real** | YES |
| 4 | CONTEXT-GROUNDED VALENCE | `hdlab/context_grounded_valence.py` | Certified animacy axis Bopen=1.000/5-seed, scramble 0.400, BOW/gov 0.500 (`notes/landed_vet_bridge1_foundation.md`). Force-verb axis CLOSED/test-fitted; body-part/social/abstract gaps documented. | **SOLID (narrow, honestly bounded)** | partial |
| 5 | AFFECT DIMENSION | `EventRecord.affect` wire (force-dynamics) | Force-dynamics-only wire; valuation via frozen theta (random-theta ~0 witness, cert doc AXIS 4). Narrow. | **SOLID-narrow / STUBBED beyond force** | partial |
| 6 | SITUATION MODEL | `hdlab/situation_reader.py` | Faithful skeleton (entities/events/timeline/causal). Own docstring HONEST-CAVEATs: causation REDUCIBLE to connective-else-recent; roles NOT re-scored here. Quality ceiling = component 1's recall 0.324. | **SOLID skeleton, extraction-starved** | YES |
| 7 | GOAL-TYPING | lexical psych-verb -> GOAL (in role/frame tables) | Generative gap: real-text TYPING_MISS ~13-14/38 (`exp_c5_quote_speaker_wired_v1` decomp); foundation coverage goal_blocking[n=2]=0.000, overall EARNED grounded 0.214 (`exp_foundation_coverage_baseline_v1`). Lexical fire only; no inference from action verbs. | **WEAK / lexical-STUB** | YES |
| 8 | OUTCOME-VALENCE | `exp_goal_congruence_outcome_valence_v1`, `exp_outcome_valence_detector_v1` | congruence cell HARD_PASS label but REGRESSES -0.400 on covered (RECOMPUTED); generative detector HARD_FAIL detection_acc=0.0 vs 0.55 floor (N=38). | **WEAK / label-inflated; generative HARD_FAIL** | YES |
| 9 | FORWARD-PREDICTION | `exp_forward_projection_affect_isolate_v1` | Isolate gate PASSES (forward-NEG 3/3 vs static 0/3, gap 100pt, scramble collapses) BUT `PARTIAL_..._REGRESSION_FP` — breaks 2 sincere items; setup-cue detector STUBBED/lexical. | **PARTIAL / setup-cue STUBBED** | partial |
| 10 | GOAL-OWNER SELECTION (Comp-5) | `hdlab/goal_owner_select.py` | Fair primacy-trap number NOW on disk: SYSTEM(divergent)=**0.6429** vs recency_floor 0.0, scrambled 0.0, twin_control 1.0 (`exp_c5_fair_goal_owner_v1`, INSTRUMENT_VALID_PIPELINE_BEATS_RECENCY_FAIR). Isolated gold-role & real-C3 end-to-end both outcome_binding=1.0 (N=23) MIDDLE_BAND_SMALL_N. | **SOLID mechanism, small-N** | **YES — the integrator** |
| 11 | QUOTATIVE SPEAKER-ATTRIB | `coreference_resolver` deixis | Wired-for-coref (deixis +0.035). Wired to outcome-attribution = NET-ZERO: OLD e2e 0.3158 == QUOTEWIRED e2e 0.3158 (`exp_c5_quote_speaker_wired_v1`), gated by TYPING_MISS bucket. | **SOLID(coref)/net-zero(attrib)** | partial |
| 12 | ToM / MENTALIZING | `exp_theory_of_mind_sally_anne_nested_hrr_v1` | HARD_PASS: Q2 0.806 vs base 0.138 (gap 0.668), cv 0.034, 5 seeds. But no registry row / not pipeline-reachable. | **SOLID but ISLANDED** | not yet (island) |

---

## RANKED IMPROVEMENT ROADMAP (leverage x how-broken)

**#1 — EVENT EXTRACTION (Component 1).** Highest leverage (root of the chain) x most-broken (recall 0.324, mislabeled 2x). Fix-class = **missing-PRIMITIVE (build) + missing-LEARNING**: the misses are (a) no relevance/salience gate over-segmenting (61 pred for 34 gold — precision 0.18), and (b) participial/coordinated-VP gaps that are TAGGER-limited (a VBG mistagged as a noun is unrecoverable by the current additive rules). Recall is capped by an upstream POS signal, not by the assembly rules -> this is where a learned extractor (reuse hdlab/learner, don't hand-add more rule branches) earns its keep. **FIRST ACTION (cheap, do now): correct the `situation_reader.py:34` docstring** so no downstream work inherits the 0.64 miscite. Everything else is gated by this component.

**#2 — GOAL-TYPING (Component 7).** High leverage (goal-owner and outcome-valence both consume it) x lexical-stub (TYPING_MISS ~37% on real text; goal_blocking 0/2; overall grounded 0.214). Fix-class = **missing-LEARNING / missing-PRIMITIVE**: psych-verb lexical firing cannot infer a goal from an ACTION ("she reached for / chased / guarded X"). Needs a generative goal-inference step (frame/telos-based), reusing the frame-induction learner rather than extending the lexicon. This is the "action-implied goal" gap.

**#3 — OUTCOME-VALENCE (Component 8).** High leverage (the "did the goal succeed?" signal feeding affect) x generatively-HARD_FAIL (0.0) and label-inflated (-0.400 regression on covered). Fix-class = **missing-LEARNING**: the covered cell is a lexicon patch that HURTS covered items; the generative detector fires 7.9% of the time. Needs a real achieved/blocked-outcome detector, and the congruence cell should be RELABELED off HARD_PASS to a bounded MEASURED_MECHANISM (lexicon-miss patch that regresses on covered).

**#4 — THEMATIC-ROLE OOV / real-data (Component 3).** Medium leverage x half-broken: in-vocab is genuinely SOLID (0.877, frame-primary, ablation-clean) but OOV on real data does NOT beat the trivial position baseline (subj 0.833 vs pos 1.0; obj 0.455). Fix-class = **missing-LEARNING (data-starved)**: the induction mechanism is proven on synthetic (0.667 beats position 0.0) but collapses to a position+animacy proxy on sparse real distributions — it needs more construction-diverse real episodes, not a new mechanism. Also raise end-to-end resolve_rate (0.80) since on-resolved acc is already 0.962.

**#5 — WIRE ToM off its island (Component 12) + QUOTATIVE-to-attribution (Component 11).** Lower leverage now (not yet on the goal-owner path) but both are DONE-but-islanded/net-zero. Fix-class = **used-wrong -> loop/wire**, not build. ToM: add a registry row + a pipeline entry so the HARD_PASS organ is discoverable. Quotative: its net-zero is downstream-gated by TYPING_MISS (Component 7), so it unblocks automatically once #2 lands — do NOT rebuild it.

**Not on the near-term critical path (healthy, leave alone):** Component 4 (context-grounded valence — narrow but certified/honest), Component 5 (affect force-dynamics wire), Component 10 goal-owner MECHANISM (0.643 fair, beats recency; small-N is the only limit -> deepen N, don't rebuild), Component 6 situation-model skeleton (faithful; its ceiling IS Component 1).

---

## CRITICAL-PATH SUMMARY for goal-owner comprehension
`EVENT EXTRACTION (1) -> ROLE LABELING (3) -> GOAL-TYPING (7) -> GOAL-OWNER SELECT (10) -> OUTCOME-VALENCE (8) -> AFFECT (5)`, with COREF (2) and SITUATION MODEL (6) as the shared substrate. The INTEGRATOR (10) is healthy (0.643 fair, beats-recency, scramble-clean); it is starved by its inputs. **Fix the chain head-first: (1) then (7) then (8).** The three MISLABELS to correct in code/registry: situation_reader.py:34 "F1~0.64", the goal_congruence HARD_PASS label, and the missing ToM registry row.
