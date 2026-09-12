# OVERNIGHT PLAN — night of 2026-09-11/12 (Fable 5.1 strategy session; stop hook ARMED, scoped to this session)

**Owner authorization (board Q131, 2026-09-12 02:11Z):** fold in the three finished pieces — *"Yes, but confirm that they are
fully, mathematically, brain foundational. If needed, run research to confirm. ... systematically, from the top down of
the live substrate ... fully understand the signals that all downstream, brain foundational (mathematically) components
need, and that these upstream changes are accommodating them. It's worth getting a broad understanding, and then
starting to implement from the top down."*

**Standing rules for every step:** path-limited commits, nothing pushed; cores capped; surgical edits; every landing
gated by its witnesses + the board self-test (standing 0.6313) + the per-dimension trend gate; a regression = revert
and record a located negative, never a weakened gate; a denied tool call = stop and report. Plain-language status to
the owner at every step; `notes/SCORECARD.md` hand sections updated at every landing. Recovery after compaction:
this file + `notes/STATUS.md` + `python tools/substrate_health.py`.

## STEP 0 — record the owner's verdict (minutes)
Write `owner_verdict: DONE` (citing Q131) into the three OWNER_NOTES.md files: `harm_help_valence_is_a_fitted_verb_list…`,
`pos_tagger_is_a_notbf_maxmargin_perceptron…`, `type_generalized_selectional_preference…`. GATE: `substrate_health`
shows fold-in backlog 3. (Done in this turn.)

## STEP 1 — the SIGNAL-FLOW MAP, top-down (the owner's "broad understanding" first)
Build `notes/SIGNAL_FLOW_MAP.md` (+ a derived helper `tools/signal_flow_map.py` where a static scan helps): starting
from `SituationReader.read()`'s outputs (the board dimensions), list for each organ the wave touches — `pos_tagger`
(25 hdlab consumers), `arc_labeler` (7), `force_dynamics_valence` (2 + the board arm), the who-affected reranker — every
LIVE consumer, the exact signal it consumes (UPOS tag string per token; dependency label set; `harm_help` →
{HARM, HELP, NA, None}; patient index + confidence), the invariants it relies on (tag set unchanged, label set unchanged,
abstention semantics), and how the change accommodates it. GATE: every consumer named in the map has a witness or a
board arm to run in STEP 3. Fallback: a consumer with no witness gets one (small) before its upstream changes.

## STEP 2 — confirm MATHEMATICAL brain-foundationality per piece (research where unclear)
Per-rung equation tables (PINNED / computational-level / FOUNDATION / OUR-INVENTION) into the INTEGRATION_LEDGER
READY-WAVE block:
- harm/help: Wolff force dynamics (agonist/antagonist → PREVENT/ENABLE/CAUSE) × grounded endstate valence (Warriner
  norms = OFC/amygdala outcome evaluation) × graded affectedness E[proto-patient | sense] (Beavers; McRae-Tanenhaus
  thematic fit) → sign. Subject-experiencer exclusion (psych verbs). Swept: τ_affect.
- upstream POS: Bayesian lexical-category posterior P(NOUN | word, DP-head) = lexical prior odds × syntactic
  likelihood ratio (MacDonald-Seidenberg constraint satisfaction; Trueswell-Tanenhaus) — land THIS (the solver's
  mathematically-right refinement), not the sense-count heuristic.
- upstream labeler: voice correction nsubj→nsubj:pass under be/get-aux + participle (Bornkessel-Schlesewsky) — a
  deterministic grammatical operation; learned patient identification via the frozen Competition-Model ranker.
- typed selectional preference: Resnik class association A(v,c) = P(c|v) log(P(c|v)/P(c)) / SPS(v) over the supersense
  cut — an information-theoretic model of typed thematic-fit expectation (McRae/Ferretti; Warren-Paczynski N400 tier).
- pos-tagger located negative: characterization only; the CRF interface stays OFF (measured −0.010).
RESEARCH (one dispatched scan, no fan-out, note to `notes/RESEARCH_harm_help_and_selectional_math_2026-09-12.md`):
(a) is KL-based selectional association a defensible computational-level model of the brain's thematic-fit expectation,
or is there a pinned alternative? (b) force structure × outcome valence as the appraisal computation — what is pinned
(OFC value; amygdala), what is analogy? (c) the Bayesian category-posterior evidence. GATE: every rung labelled; any
rung that turns out OUR-INVENTION-as-mechanism is NOT landed (replaced or the piece is held, with the reason written).

## STEP 3 — land pri-7 TOP-DOWN along the map (the behaviour-changing landing)
Order (each sub-step: land → run the named consumers' witnesses + board self-test → commit → status line):
 3a. `hdlab/pos_tagger.py`: Bayesian nominal-head category correction as a post-pass on `PosTagger.tag` (from
     `exp_pos_bayesian_category_v1.py` / `exp_pos_nominal_head_correction_v1.py`; witness 6/6). Consumers: all 25.
 3b. `hdlab/arc_labeler.py`: voice post-correction `label_voice_correct` (witness `test_fd_harm_help_learned_extraction`
     3/3). Consumers: 7.
 3c. `hdlab/force_dynamics_valence.py`: replace the frame-list machinery with `harm_help_arithmetic` (graded
     affectedness version), remove the read-path FrameNet enumeration; `__bf_status__` NOT_BF → BF_SPIRIT (+ registry
     row; NOT_BF 7 → 6). Consumers: `context_grounded_valence`, the board `affect_harm_help` arm.
 3d. Route harm/help patient identification through the frozen `argstruct_patient_ranker` where the reader binds it.
 GATE per sub-step: witnesses green, self-test AGG unchanged or explained; after 3d a FULL board `--run` (detached) and
 the per-dimension gate; `affect_harm_help` expected to move up (0.778 standing). Fallback: revert the sub-step, record.

## STEP 4 — land typed selectional preference
Promote `TypedSelectionalPreference` to `hdlab/typed_selectional_preference.py` (offline build from the selectional
store; registry row BF_SPIRIT), consume it in the who-affected reranker behind a strong margin gate (τ≈0.3, swept);
witness 5/5; `affected_entity` arm no-regress. GATE as above.

## STEP 5 — land the pos-tagger located negative
§2b + registry characterization; the gated CRF interface option in `causation_typing._frontend` OFF with the measured
reason written beside it. No behaviour change; tag gate + self-test.

## STEP 6 — close the wave
§2b entries (3), registry, BF ledger rows → APPLIED, INTEGRATION_LEDGER → INTEGRATED, `INTEGRATED_BY_STRATEGY` markers,
KNOWLEDGE_ASSET_REGISTER (selectional organ), SCORECARD hand sections (what changed / not-yet-BF list shrinks by one),
STATUS + project_state, BOARD_TREND row from the full run. Plain status to the owner.

## STEP 7 — if time remains: the two merges that were waiting on pri-7
Force (`force_dynamics_lexicon` + `causation_typing` force arm; drop the retired valence list) and appraisal
(`occ_appraisal` + `context_grounded_valence`) — ONE AT A TIME, delegated byte-identity refactors with the temporal
template (baseline → merge → identical board rows → witness → commit), then the consolidation audit rows.

## STOP CONDITIONS
A denied tool call; a regression that survives a revert; an owner note in `notes/COMMENTARY.md` saying stop;
`python tools/autoloop.py disarm`. Morning hand-back: STATUS header + SCORECARD + this file's step checkmarks.

## PROGRESS (tick as done)
- [x] STEP 0
- [x] STEP 1 (notes/SIGNAL_FLOW_MAP.md; all 7 label consumers already handle nsubj:pass; harm/help contract identical; Bayesian terms must be a persisted asset)  - [x] STEP 2 (RESEARCH_harm_help_and_selectional_math: all three = computational-level composites; none OUR-INVENTION-as-mechanism; Resnik superseded by Bicknell 2010 -> noted for pri-1)  - [x] STEP 3a  - [x] 3b  - [x] 3c (+ valence-coverage boundary recorded; synonym backoff tried+withdrawn)  - [x] 3d (gov_idx = the reader's bound predicate)  - [x] STEP 4 (organ promoted, LATENT -> pri-1; gated rerank measured neutral so not wired live)  - [x] STEP 5 (located negative folded; CRF not flipped, pri-11 addendum)  - [x] STEP 6 (full run 2026-09-12 03:11Z: AGG 0.6408, affect 0.778->0.972, affected_entity 0.373->0.387, no regression; trend gate 2 rows; docs + markers + SCORECARD done)  - [x] STEP 7 resolved by code check: force = composition (one truth table imported), appraisal = two distinct checks, no duplicated equation → audit corrected, no merge
