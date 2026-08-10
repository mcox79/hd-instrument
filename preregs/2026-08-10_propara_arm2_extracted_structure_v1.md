# Pre-registration: exp_propara_arm2_extracted_structure_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator ARM-2 follow-up to v3 (HARD_PASS
oracle: content_delta_loc +0.027, moves +0.082, median retained 0.185). The oracle arm proved the
MECHANISM; ARM 2 is the decisive end-to-end test of the extraction-as-foundation plan.

## Prior-work check (SUBSTRATE-KB)
Same arc as v1/v2/v3 (top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). Direct ARM-2
follow-up on v3's own landed oracle result; novelty inherited. Reuses the extraction-gate's
fastcoref cross-interpreter pattern (commit 3f23f2fb2), not re-sourced.

## The decisive question
Does v3's scramble-clean MOVES localization signal SURVIVE when the structure is EXTRACTED from
raw text instead of oracle-gated? One clean variable: oracle structure -> extracted structure,
keeping the v3 sequential state-conditioned verb-gated firing mechanism EXACTLY.

## What is EXTRACTED (from raw text, not oracle)
- **ENTITIES / cross-sentence linking:** fastcoref (biu-nlp/f-coref) clusters, precomputed in
  SYSTEM python (tools/benchmark_trap_check/run_fastcoref_propara_v1.py ->
  data/benchmark_trap_check/propara_fastcoref_predictions_v1.json; transformers 4.57.3, isolated
  from the .venv per the extraction-gate pattern) and aligned to participants + sentences by
  char-span overlap in-cell. Links pronoun/alias mentions (verified: Plants<->They, sediment
  cluster on real ProPara) so verb attribution reaches sentences that do not name the participant.
- **VERBS / verb-class attribution:** spaCy (en_core_web_sm) dependency parse per sentence; a verb
  is attributed to a participant iff a participant mention (exact-name OR coref-linked) is its
  subject / object / prep-object, classified by the SAME curated verb-class lexicon reused
  verbatim from v3 on the verb LEMMA. Replaces v3's participant-AGNOSTIC sentence-level verb-class
  with participant-SPECIFIC dep-parse attribution.
- **EVENT-COUNT BUDGET:** the oracle multiset is WITHHELD. Each participant's canonical budget
  (#CREATE cap 1, #MOVE, #DESTROY cap 1) is EXTRACTED = the count of verb-class events attributed
  to it across the paragraph. This is the key swap.

## What is GRANTED (flagged; standard-ProPara or arm-uniform so unbiased)
- **PARTICIPANT LIST:** the gold participant set is the TASK INPUT in ProPara (systems are given
  participants and predict their grids; the official evaluator requires exact-match participants).
  NOT oracle leakage -- standard for every ProPara system.
- **LOCATIONS:** not extracted; uniform LOCATION_UNKNOWN placeholder in EVERY predicted grid
  (identical across all arms incl. the prior-lesion), so it cannot bias the content_delta. The
  MOVES content signal is a step-LOCALIZATION signal (step_id + participant match), which the
  arm-uniform placeholder does not confound. Flagged: from->to span extraction deferred.

## Mechanism + controls
- Firing: byte-identical v3 sequential state-conditioned loop (reused imports: _canonical_sequence
  / _assign_prior_lesion / _rng / _grids_from_assign / verb-class lexicon), ONLY the (budget,
  per-sentence evidence) inputs change from oracle/sentence-level to EXTRACTED/participant-attributed.
- PRIOR-LESION control: EXTRACTED budget + random-monotonic placement (ZERO verb-firing) -- isolates
  the localization content contribution WITHIN the extracted-budget regime (so content_delta =
  benefit of verb-firing given the SAME noisy extracted budget the reasoning arm gets).
- 8 scramble seeds (7,17,29,41,53,71,83,97).

## Metric scope (identical to v3)
PRIMARY claim = LOCALIZATION official F1 (mean moves/conversions) + the MOVES category
specifically (where v3's signal lived). EXISTENCE (inputs/outputs) reported SEPARATELY, never in
the claim. FOCUS unmentioned macro-F1 secondary/reported.

## HARD-PASS / HARD-FAIL bands (v3's oracle bands, applied UNCHANGED -- ARM2 is the extraction-cost
test against v3, not re-tuned; pinned before running)
- `CONTENT_DELTA_LOC_MIN_POSITIVE = 0.02`: EXTRACTED reasoning localization F1 must beat the
  EXTRACTED prior-lesion by >= this (natural order).
- `SCRAMBLE_CLEAN_MEDIAN_HARD_PASS = 0.30`: median retained_frac_loc across 8 seeds < this.
- `SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL = 0.55`: median > this = did not collapse -> HARD_FAIL.
- **HARD-PASS (SIGNAL SURVIVES EXTRACTION)** iff content_delta_loc >= 0.02 AND median
  retained_frac_loc < 0.30. Even SMALLER than the oracle +0.027 is fine -- a surviving
  scramble-clean signal = the FIRST end-to-end glass-box comprehension signal on real prose.
- **HARD-FAIL (SIGNAL VANISHED)** iff content_delta_loc < 0.02 OR median retained_frac_loc > 0.55.
- **MIDDLE_BAND** = partial survival.
- Infra gates (HARD_FAIL_INFRA): arms_differ, decode_fidelity >= 0.99 both arms.

## Extraction-cost attribution (reported every run)
- `budget_fidelity`: EXTRACTED vs ORACLE budget per (para, participant) -- exact-match rate +
  per-class (CREATE/MOVE/DESTROY) precision/recall/F1 of the extracted event counts. Localizes the
  event-count-extraction cost; MOVE recall is the most decisive (v3's signal was MOVES).
- coref cluster count + participant mention-sentence total + attributed-verb total.
- v3 oracle reference (content_delta_loc 0.027 / moves 0.082 / median 0.185) carried in the
  headline for the cost comparison. If the signal VANISHES, the component with worst fidelity
  (coref link rate vs verb-attribution vs budget MOVE recall) is the extraction-improvement target.

## Cell-template mandates
arms_differ (META_RULE_AF; asserted self-test + recorded); final_metrics_atomicity tmp_replace;
except SystemExit before except Exception (grep-verified); crlb_n/a; calibration_check default_ok
(v3 bands, unchanged); deterministic_seeding (hashlib-seeded rng + scramble perms, no Python
hash()/list(set())); progress_logging print_flush_true.

## Compute architecture
Sequential-CPU, justified: fastcoref precomputed offline (system python, one-time); the cell does
spaCy dep-parse (43 dev / 54 test paragraphs, parsed once each) + discrete firing + FHRR decode.
No batching opportunity. spaCy parse dominates (~a few sentences/ms); MEASURED self-test 6.2s
(incl. imports + spaCy load). Expect smoke ~30-60s, full ~40-90s. Run INLINE/LOCALLY foreground.

## Self-test findings (real code path)
**MEASURED@data/exp_propara_arm2_extracted_structure_v1/metrics.json (self_test, elapsed 6.2s):**
On a clean 6-sentence synth with a coref pronoun link (It->seed): extracted_budget = {CREATE:1,
MOVE:1, DESTROY:1} (perfect vs oracle -> budget_fidelity 1.0), coref-linked "It moves" attributed
MOVE to seed, verb-firing placed [CREATE, NONE, MOVE, NONE, NONE, DESTROY] (correct localization),
arms_differ True, decode 1.0, all 4 verdict-logic unit checks correct (genuine HARD_PASS / vanished
HARD_FAIL / fragile HARD_FAIL / partial MIDDLE_BAND). Confirms the extraction + firing pipeline
runs end-to-end on the real code path. (Also observed + expected: spaCy mis-tags terse verbs like
"forms" in "A seed forms" as a NOUN -> a real parse-error cost that ARM-2's budget_fidelity
measures on the real corpus; the self-test uses "appears" which spaCy reliably tags as VERB.)

## Smoke findings (DEV, 2 seeds)
**MEASURED@..._smoke/metrics.json (dev):** content_delta_loc +0.0355, moves +0.073 (magnitude
comparable to v3 oracle), BUT median retained_frac_loc = 0.951 (does NOT collapse). Budget fidelity
17% exact, CREATE R 0.66 / MOVE R 0.36 / DESTROY R 0.37. -> HARD_FAIL_SIGNAL_VANISHED on DEV;
confirmed the pattern before the TEST run (bands = v3's, unchanged).

## Full findings (TEST, 8 seeds) -- the extraction-cost measurement -- HARD_FAIL (informative negative)
**MEASURED@data/exp_propara_arm2_extracted_structure_v1/metrics.json (test, 54 paragraphs, 236
participant-pairs, 8 seeds; run_mode=full, cardinality_ok, arms_differ True, decode 1.0).**

**The scramble-clean MOVES signal does NOT survive extraction. Verdict HARD_FAIL.**

1. **Magnitude PARTIALLY survives:** content_delta_moves = +0.043 (vs v3 oracle +0.082 -- about
   half), content_delta_loc = +0.0205. Reasoning still beats the EXTRACTED prior-lesion. BUT the
   absolute win is gone: reasoning moves-F1 = 0.366 LOSES to bow_singlestep 0.380 (and ~ties
   majority 0.363) -- the +0.043 delta is only over the extracted prior-lesion (0.323), which
   extraction dragged BELOW the baselines. So there is no absolute-best-baseline win under
   extraction.
2. **Order-dependence (the actual prize) does NOT survive:** median retained_frac_loc = **1.085**,
   list [1.05, 1.17, 1.00, 1.27, 1.12, 0.95, 0.90, 1.83], **0/8 seeds collapse** (frac<0.30 = 0.0);
   scramble moves-F1 (0.366-0.380) is IDENTICAL to natural reasoning moves (0.366). Scramble does
   not hurt at all -> the extracted signal is order-INVARIANT = local verb-spotting, NOT temporal
   composition. The scramble control correctly reports NO composition.

**Extraction fidelity (extracted budget vs oracle, 236 pairs):** budget-exact 21%; CREATE P=0.63
R=0.50 F1=0.56; MOVE P=0.54 R=0.49 F1=0.52; DESTROY P=0.80 R=0.45 F1=0.57; 142 coref clusters.
Roughly HALF of every event type is missed (recall ~0.45-0.50) -- the dep-parse + curated-lexicon
verb-event extractor is the lossy component (terse ProPara verbs, spaCy mis-tags e.g. "forms"->NOUN,
lexicon gaps), NOT coref (which links fine).

**ATTRIBUTION of the order-invariance (inline diagnostic, MEASURED this session, reproducible --
oracle budget + ARM2 attributed evidence, test split):** content_delta_loc +0.025 / moves +0.049;
scramble retained [0.98, 0.94, 0.72, 0.58], **median 0.83**. So THREE configs on test:
- v3 (oracle budget, participant-AGNOSTIC sentence verb-class): retained median **0.185** (collapses).
- diagnostic (oracle budget, participant-ATTRIBUTED dep-parse evidence): retained median **0.83**
  (mostly order-invariant).
- ARM2 (extracted budget, attributed evidence): retained median **1.085** (fully order-invariant).
The agnostic->attributed swap (0.185 -> 0.83) is what KILLS the order-dependence; the
extracted-budget noise (missed CREATEs remove state-gating) pushes it the rest of the way
(0.83 -> 1.085).

**DEEP, HONEST IMPLICATION (retro-corrects v3):** v3's scramble-clean order-dependence came
PRIMARILY from order-sensitive DISAMBIGUATION of ambiguous participant-agnostic evidence (which
sentence's verb the state machine grabs first depends on processing order), NOT from genuine
cross-step temporal composition. When extraction ATTRIBUTES verbs to participants precisely
(dep-parse + coref), the localization reduces to a LOCAL "put the event at the true step whose
verb is attributed to this participant" operation -- inherently order-invariant, needing no
composition. So the scramble-clean property does not survive precise extraction because precise
extraction removes the very ambiguity whose order-sensitive resolution v3 exploited.

**Extraction-improvement target:** the primary bottleneck is NOT coref (fine) and NOT the
"scramble-clean localization" thread (which dissolves into order-invariant local verb-spotting
under precise attribution). It is (a) verb/event-extraction RECALL (~0.50 per class; better SRL /
verb-class coverage / spaCy-mistag handling would recover magnitude), and more fundamentally (b)
the mechanism still lacks GENUINE cross-step composition for truly UNMENTIONED states -- the
unmentioned focus subset remains near ceiling (content_delta_focus +0.0265, but focus F1
reasoning 0.376 is not a compositional win). The honest program-level read: structural
comprehension over EXTRACTED structure does not yet produce an order-dependent, scramble-clean,
best-baseline-beating comprehension signal on real prose; the surviving signal is local
verb-attribution, and genuine cross-step inference for unmentioned states is the remaining wall.
