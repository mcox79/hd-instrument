# TEST-FAIRNESS AUDIT (angle 3/3, AUDIT-ONLY): goal-owner evaluation as-run

**Auditor:** skunkworks (independent, off-disk recompute, in-process foreground). **Question (USER):** is the goal-owner test, AS ACTUALLY RUN this session, a FAIR brain-aligned test, or is it measuring an artifact / on unfair banks? Deflationary, measured-not-asserted.

**Artifacts recomputed off disk:**
- Banks: `experiments/data/goal_outcome_c3mined_v1.jsonl` (38), `goal_outcome_oov_psych_v1.jsonl` (21), `goal_outcome_oov_psych_gold_v1.jsonl` (6).
- Cells/metrics: `data/exp_c5_realtext_c3mined_v1/metrics.json`, `data/exp_c5_realtext_c3mined_v2_38item_v1/metrics.json`, `data/exp_c5_quote_speaker_wired_v1/metrics.json`.
- Code READ: `hdlab/goal_owner_select.py` (directed_goal_outcome_score), `experiments/exp_c5_realtext_c3mined_v1.py` (type_sentence_events_c3 / run_item), `..._v2_38item_v1.py`, `exp_component5_gold_role_isolated_v1.py` (GeneralRecencyEntityResolver / ContentMatchResolver / build_positions).

---

## HEADLINE VERDICT: the test as-run is UNFAIR / non-informative about goal-owner binding.

The number the pipeline reports (`outcome_binding_accuracy` 0.64-0.71) is dominated by upstream syntactic-subject resolution + verb-lexicon typing. The C5 goal-owner SELECTION organ (`directed_goal_outcome_score`) — the thing under test — was actually exercised on **1 clean real-text item** across both banks. It does NOT clear a fair baseline: on the 15-item bank it equals recency to the digit; on the 38-item bank the entire +0.06 margin is a single item. The banks additionally do not contain the discourse structure the capability is defined on (a maintained goal bound to a protagonist across a distractor), and the "gold" is a circular restatement of the miner's own subject-picker.

---

## AXIS 1 — METRIC VALIDITY: **UNFAIR (measures a proxy, and mostly measures the wrong module).**

**What the metric actually computes (read off `run_item`):** `matches_gold = (final_owner == gold)` where `final_owner = adopted_cluster_ids[outcome_pos]` = the entity the resolver assigned as the SUBJECT of the outcome-bearing sentence, and `gold = mined.goal_owner` = the miner's syntactic subject of the goal sentence. So the metric is: *does the outcome-sentence subject-resolution reproduce the miner's goal-sentence subject-pick?* That is a coref/subject-resolution agreement check, **not** goal->owner binding in a situation model.

**The C5 organ barely touches the number.** `directed_goal_outcome_score(role_seq, cluster_ids, outcome_pos)` returns `1.0` iff the entity at the outcome slot carries ANY GOAL under that candidate's own assignment, else `0.0`. But `final_owner` is `adopted[outcome_pos]` regardless of the raw score — the score only changes the answer through `delta = score_c - score_b` -> `decide_keep_or_revert`. That delta is non-zero only when the recency (`baseline_owner`) and content-match (`content_owner`) candidates DISAGREE at the outcome slot. Recomputed off `metrics.json` per-item (21 typed items, 38-bank):

- `baseline_owner != content_owner` on **2/21** items only: `c3_113_the_secret_garden` (base=sahib, cont=mary, gold=mary — genuine win) and `c3_145_middlemarch` (base=dorothea, cont=celia, gold=celia — but gate did NOT adopt, final=dorothea, and this gold is itself wrong: "knowing" is a predicate adjective).
- On the other 19/21, `outcome_binding_accuracy == recency_baseline` term-by-term (`matches_gold == recency_alone_matches_gold` on every non-divergent item).

**So the organ under test decided exactly ONE real item (secret garden).** role_seq inspection confirms the degeneracy: most items are `[GOAL, OUTCOME_*]` with BOTH events attributed to the SAME resolved subject (`type_sentence_events_c3` attributes every fired event to the one clause `subject`), so `score` is trivially 1.0 for the subject and the "binding" is vacuous (an entity that holds the goal and is handed the outcome in the same breath).

**F1~0.64 predicate/agent/patient — NOT REPRODUCIBLE ON DISK.** I searched all committed `.py/.md/.json` (non-node_modules). No `0.64`/`0.636` predicate-agent-patient extractor metric exists. The closest committed extraction-quality numbers (`exp_coherence_gate_extraction_correctness_independent_gold_v1`, litbank slices) are **F1 0.23-0.30**, not 0.64. **The cited 0.64 target cannot be verified and should not be propagated.** Even taken at face value, token-match predicate/agent/patient F1 rewards positional token overlap, not goal-owner binding — it is the wrong target for this capability.

**FIX:** score the organ ONLY on items where the two candidates diverge at the outcome slot (report N_divergent explicitly and never average it away into a subject-resolution number); and define the gold as *who the maintained goal belongs to*, decoupled from whoever happens to be the outcome-sentence subject.

## AXIS 2 — BANK FAIRNESS: **UNFAIR / construction-determined on every bank. Clean-N < any usable floor.**

**(a) Can the bank discriminate the capability?** Largely no. `gold = goal_owner`, and `owner_resolution == "syntactic_subject_name"` for the mined items — i.e. gold IS the output of a syntactic subject-picker. A trivial "pick the goal-sentence syntactic subject" baseline scores **100% on the owner-correct subset by construction**. There is no held-out distractor forcing a bind: the outcome is not an independent referent that could disagree with the goal-holder in a way the system must resolve.

**(b) Is the gold correct?** 38-bank: **7/38 owner-ID wrong** (OWNER_WRONG_IDS, independently re-derived: place-metonyms `York`/`England`/`Portsmouth`, predicate-adjective `knowing`/Celia, vocative `Judy`, tool-sense `saw`/Jim, garbled Evelina). OOV-21 bank: gold-VET (`notes/goldvet_oov_psych_bank.md`) found **5/21 wrong-owner + 1 broken**, only **13/21 owner-clean, 9/21 strict-clean**. Outcome-polarity gold is separately unreliable on both.

**(c) Leakage / trivialization.** `outcome_span` is auto-extracted TRAILING text, frequently about a DIFFERENT character and causally disconnected from the goal — recomputed examples: owner=`York` -> outcome=`"Archer allowed smoking."`; owner=`Tom` -> `"...Aunt Polly was vexed..."`; owner=`Celia` -> `"Riding was an indulgence which she allowed her..."`. The "outcome" is not the goal's outcome, so outcome-binding gold is not a real target. Foils are contaminated with places/languages/generics (`Bath`, `Nantucket`, `Christians`, `French`) on 4-5 OOV items, and on the 38-bank several foils are the OTHER character in the (unrelated) outcome span (`foil=Archer` while owner=`York` and outcome is about Archer) — making the foil either trivially wrong or perversely the real referent.

**(d) Is difficulty real?** No cross-sentence distractor-bind is enforced; 9/38 items are `nofoil` (single-target by design); the divergence structure the organ resolves arises on ~1 item.

**Per-bank clean count (recomputed / from gold-VET):**
- 38-bank: 31/38 owner-correct; but only **17/31 even TYPE** (14 TYPING_MISS), and the selection organ fires on **1**. Effective discriminating-N ~1.
- OOV-21: **13/21 owner-clean, 9/21 strict-clean; effective testable N ~3** (3/6 gold items not even extractable upstream).

**Invalidated prior conclusions:** any statement of the form "real-text C5 outcome-binding = 0.64-0.71" as evidence the C5 organ works on real prose is **not supported** — it is upstream subject-resolution. The `SELECTION_MECHANISM_UNTESTED_NO_CANDIDATE_DIVERGENCE_ON_REALTEXT` verdict in `exp_c5_realtext_c3mined_v1` is the honest one and should be the headline, not the 0.64. The v2 `MEASURED_HONEST_NUMBER` 0.7059-vs-0.6471 must be re-scoped to "1/17 divergent; organ decided 1 item."

## AXIS 3 — CAN-FAIL / BASELINE: **UNFAIR baseline as-run (degenerate) + the real-text "win" does NOT clear it.**

- `exp_c5_realtext_c3mined_v1` (15-item): `outcome_binding=0.6364`, `recency_baseline=0.6364` — **identical**, `beats_recency=False`, `candidate_divergence_rate=0.0`, `scramble_collapse_rate=0.0`, `non_vacuous_scramble=False`. The scramble control is VACUOUS here (collapse 0.0) — the discriminator did not fire, so this bank cannot fail-or-pass the organ.
- `exp_c5_realtext_c3mined_v2` (38-item): margin +0.0588 = exactly 1 item; full-pipeline 0.5714 vs 0.5238 similarly 1-item-driven.
- The "recency baseline" as coded is not the classic recency floor — both resolvers return the first explicit roster NAME token and only diverge in the pronoun branch, so "recency" here is itself a subject-resolver. The genuinely fair floor — "pick the goal-sentence syntactic subject" — **equals gold by construction (=1.0)**, i.e. the system cannot beat the trivial baseline; it can only match or underperform it.
- The ONLY non-vacuous, scramble-passing result this arc is the **isolated GOLD-role hand-authored bank** (`exp_component5_gold_role_isolated_v1`, `outcome_binding=1.0` vs recency `0.0435`, scramble collapse True). That is a legitimate mechanism-exists proof on 23 hand-built recency-trap items with GIVEN (lexicon) roles — but it is NOT the real-text test and does not transfer: on real prose the trap structure it needs (0.0435 recency floor) does not arise.

**Net:** the pre-registered can-fail bands are met only where the discriminator is vacuous. No real-text "win" cleared a fair baseline this session.

## AXIS 4 — BRAIN-ALIGNMENT of the test: **UNFAIR (not the brain's task).**

Brain-faithful goal-owner probing = maintain a protagonist's goal across a discourse, introduce a distractor entity, and require binding the eventual outcome/affect to the goal-HOLDER (Zwaan event-indexing + situation-model updating). The test as-run is **sentence-local**: goal and outcome are typically the same clause, both auto-attributed to one resolved subject; there is no maintained-across-distractor bind. It tests "can a lexical psych-verb + a subject-picker co-fire in one sentence," which is a lexical-pattern-match, not the maintenance/update dynamics comprehension needs. The task is not the brain's task.

## AXIS 5 — CONFOUNDS: **UNFAIR (extraction quality and binding quality are entangled; buckets leak).**

- `TYPING_MISS=14/38` items never fire a goal+outcome pair at all (participial / VP-coordination / dialogue-fractured spans — cf. `exp_c5_quote_speaker_wired_v1`), so 14/38 are dropped UPSTREAM by the extractor and never reach the binding organ. A binding failure and an extraction failure are therefore NOT separable at the aggregate number — the reported accuracy is conditioned on the extractor's own biased 17/38 survivors.
- The 4-bucket decomposition (`OWNER_ID_ERROR / TYPING_MISS / BINDING_ERROR / CORRECT`) is cleaner than the aggregate (good), but it still leaks: `OWNER_ID_ERROR` is charged to "the mined gold is wrong" (a BANK defect) while sitting in the same denominator as pipeline behavior; and `BINDING_ERROR` (5) cannot distinguish "wrong bind" from "right bind onto a broken/unrelated outcome_span." The extractor F1 (whatever its true value; not 0.64 on disk) confounds EVENT-EXTRACTION with BINDING because binding is only ever scored on extracted survivors.

---

## WHICH PAST CONCLUSIONS MUST BE RE-SCOPED

1. "Real-text C5 outcome-binding ~0.64-0.71" as evidence the SELECTION organ works on real prose -> **RE-SCOPE**: it is upstream subject-resolution; organ decided 1 item.
2. "Beats recency on real text" -> **FALSE as-run** (15-item: exactly ties; 38-item: +1 item, not powered).
3. Extractor "predicate/agent/patient F1~0.64" -> **UNVERIFIABLE**; committed extraction F1 is 0.23-0.30. Do not cite 0.64.
4. Any outcome-polarity conclusion from these banks -> **REJECT** (auto-extracted trailing spans; polarity gold unreliable, one inverted in OOV).
5. The `MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS` isolated-gold result -> **KEEP but SCOPE**: valid mechanism-exists proof on hand-authored GIVEN-role traps; NOT a real-text or earned-role result.

## CORRECTED FAIR TEST DESIGN (metric + bank + baseline)

**Bank (build to discriminate):** hand-curate/verify >=25 items each with (i) a protagonist P who holds a goal, (ii) a DISTRACTOR entity D mentioned between goal and outcome (real person, gender-matched to force the resolver to work), (iii) an outcome/affect clause CAUSALLY tied to P's goal but syntactically closer to D (so subject-picking D is the recency trap), (iv) verified owner gold = P AND verified outcome-polarity gold, (v) balanced polarity + OOV/in-vocab verbs + a matched no-distractor control. Reject auto-extracted outcome_spans — outcomes must be authored/verified as the goal's actual outcome.

**Metric:** report on the DIVERGENT subset (N reported prominently) `owner-ID accuracy` where gold = the goal-HOLDER (decoupled from outcome-sentence subject); keep the 4-bucket decomposition but move `OWNER_ID_ERROR` out of the capability denominator (it is a bank-gold defect, scored separately). Add a `selection_exercised` gate: an item counts toward the capability number ONLY if baseline!=content at the outcome slot.

**Baselines (all three, per bank):** (1) always-pick-goal-sentence-syntactic-subject (the construction-trivial ceiling — system must at least match), (2) recency = pick nearest gender-compatible entity to the outcome clause (the trap floor — system must BEAT), (3) majority/most-frequent-entity. Pre-register: PASS = beats recency by a margin significant at the divergent-N, on a bank where recency floor < 0.5 (proving the trap is real). Fix the extractor gaps (participial / VP-coord / dialogue) FIRST so N recovers past ~3-17 and the binding number is not conditioned on a biased survivor set.

---

*Boundary: AUDIT-ONLY. I recomputed off committed metrics/banks/code; I did not author or run a cell. The 1/21-divergent and 0.6364==0.6364 figures are read directly off the on-disk metrics.json, not from a cell I dispatched.*
