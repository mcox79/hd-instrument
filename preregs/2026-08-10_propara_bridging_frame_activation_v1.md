# Pre-registration: exp_propara_bridging_frame_activation_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator build spec, mid-drill USER steer
(charter fork resolved to B: brain-faithful FRAME/SCRIPT-ACTIVATION reading), sharpened by a
parallel brain-fidelity drill's disk-VET'd root-cause finding + full spec at
`notes/research_frame_script_reading_build_spec_2026-08-10.md`.

## Prior-work check (SUBSTRATE-KB)
`bash tools/substrate_query.sh "frame semantics script activation combustion process physics
ProPara reading"` -> top hit cosine=0.3145 (entity='combustion', WordNet+atoms), no prior arc cell
above 0.30 proposing THIS specific fix (graded frame-activation replacing literal-keyword bridging).
Direct successor of the SAME bridging sub-arc (`exp_propara_bridging_distilled_kb_endtoend_v1`,
357143e98, HARD_FAIL survival=0.1823) -- novelty inherited from that arc's own prior checks; this
cell is NOT a rediscovery, it is the mechanism-level fix the arc's own HARD_FAIL residual pointed at.

## THE ONE-VARIABLE TEST
Hold KB CONTENT fixed (SAME `data/benchmark_trap_check/propara_process_physics_kb_v1.json`, zero
edits to its 18-process signature/consumes/produces/moves lists). Swap ONLY the matching operator:
literal `set() & text_toks` (the 0.1823-floor cell) -> graded `hdlab.lexical_similarity.
concept_similarity` (this cell). If survival climbs off 0.1823 toward the oracle's +0.1062 lift with
controls clean, it proves the wall was the MECHANISM (matcher), not the knowledge.

## VET-CAUGHT PREREQUISITE (before writing this cell -- material deviation from the literal build
spec, disclosed)
The build spec named `hdlab/lexical_similarity.py::concept_similarity` as the ready-to-use organ.
DISK-CHECKED this build: its pre-existing 89-concept lexicon had **ZERO usable overlap** with this
KB's 197-word vocabulary (MEASURED@this build: intersection = {water, mountain, fix}, 3/197). Using
`concept_similarity` unmodified would have returned `None` (honest-abstain) for nearly every
paragraph-token x KB-word pair -- graded matching could not have fired AT ALL, silently regressing
below even the literal floor. **Fix (not optional, load-bearing):** a SUPPLY EXTENSION to
`hdlab/lexical_similarity.py` (same file, same convention as its 3 prior extensions --
ferry/sister/rival 2026-08-06, goal_outcome_relation vocabulary 2026-08-09), two parts:
1. MECHANICAL (auto-generated from the KB's own JSON, zero hand-typing, zero new knowledge -- pure
   re-encoding of already-hand-vetted content): every literal signature/consumes/produces/moves word
   gets a `<PROCESS>_DOM` + `<PROCESS>_<ROLE>_ROLE` compound tag. Guarantees literal-match parity as
   a floor (self-similarity=1.0 for every KB word against itself).
2. PARAPHRASE (hand-authored from general middle-school-science + common-synonym knowledge, NOT from
   reading ProPara TEST paragraphs, ~35 words: log/timber/kindling->wood, blaze->fire, ember->ash,
   mist->vapor, sun->sunlight, carcass->body, boulder->rock, gasp->breathe, crude->petroleum, ...).
   This is the part that actually tests "many surface forms -> one frame" -- the mechanical part
   alone cannot beat the floor by itself (it only reproduces literal-match parity).
MEASURED@this build's interactive probe (hdlab/lexical_similarity.py self_test() + ad hoc checks):
log~wood=1.0, blaze~fire=1.0, ember~ash=1.0, carcass~body=1.0, timber~fuel=0.5245, mist~vapor=0.5906,
sun~sunlight=0.6748 (true paraphrases, cleared); wood~ash=0.4077, wood~fire=0.4130,
boulder~rock=0.3503, log~oxygen=0.3802 (same-domain-DIFFERENT-role, must NOT cross-bind); log~vessel
= -0.01, log~happy = -0.0002 (unrelated domains, near-zero, no false cross-linking). This gives a
clean separation band: DOM+ROLE-identical pairs = 1.0; DOM-only (wrong role) pairs <= ~0.41;
unrelated pairs ~ 0.

## Thresholds (DEV-pinned per the above separation band; smoke re-verifies discriminator-fires)
- `FRAME_SIM_THRESH = 0.45` (paragraph-token vs SIGNATURE-word; broader net for frame-ID).
- `ROLE_SIM_THRESH = 0.55` (participant-token vs role-word; sits above the ~0.41 domain-only-bleed
  ceiling, precision-favoring for role-mapping).
- `MIN_FRAME_SIG_HITS = 1`, top-2 process match (matches the literal cell's own DEV-chosen k).
- `calibration_check: adaptive_with_discriminator_gate` -- smoke MUST re-verify the graded matcher
  fires on paraphrase-only synth (self-test does this: `n_graded_only_role_hits >= 1` on a synth
  paragraph using ONLY 'blaze'/'timber', words absent from literal KB signature/consumes lists).

## Organs reused (Section 2 audit of the build-spec note; disk-checked, not assumed)
- `hdlab.lexical_similarity.concept_similarity` -- THE graded matcher (Step 2a/2b).
- `experiments.exp_propara_bridging_knowledge_vs_mechanism_v1._grids` / `_paragraph_precompute` /
  `_prior_lesion_grids` -- UNCHANGED downstream retrieve-validate-advance consumption; bit-identical
  contract to the literal cell (`pre[pid]["bridge"][participant] -> {effect: set(trigger_classes)}`).
- `propara_process_physics_kb_v1.json` -- UNCHANGED KB content.
- `experiments.exp_propara_decisive_inference_arm1_oracle_v1._deterministic_perm` -- hashlib-seeded
  permutation helper (PROT-023/F.5-compliant), reused for the scramble-KB-content control.

**NOT reused (both disk-checked, not assumed -- honest naming-collision catches):**
- `hdlab/frame_induction.py` -- FALSE FRIEND. OOV-VERB thematic-role induction (AGENT/EXPERIENCER
  from syntactic cues), not process-frame identification. Confirmed by direct code read.
- `hdlab/script_grain_acquisition_loop.py::ScriptLibrary` -- right SHAPE (FHRR bind-then-bundle
  associative matching) but only 4 fixed roles, consumes already-typed category tags not raw text,
  and this cell's downstream consumer (`_grids`) only needs a plain
  `{effect: set(trigger_classes)}` dict -- introducing FHRR script-instance objects would not change
  the scored F1 output at all (pure decoration for THIS contract). Scoped out per
  compute-proportionality (match method weight to the question); a genuine future upgrade path
  (learn new process types from corpus exposure) is out of scope for this build.

## Implicit-entity SCOPE NOTE (honest, disk-checked)
Build spec asked for implicit-entity allocation for frame-slot fillers with no textual mention.
DISK-CHECKED: `_grids` only ever consumes `pre[pid]["bridge"][participant]` for `participant in
para["participants"]` -- ProPara's OWN gold participant list, which ALREADY includes every tracked
entity regardless of textual mention at a given step (that IS what "unmentioned subset" means in
this arc). No NEW entity needs allocating for the scored metric to move. What IS added: an
IMPLICIT-vs-MENTIONED audit tag per (paragraph, participant) (`n_never_mentioned_participants`,
`n_facts_sourced_for_never_mentioned_IMPLICIT` in stats), inspectable without changing the `_grids`
contract.

## Controls (reused from the distilled cell's harness, unchanged, PLUS one new)
- `prior_lesion`, `without_knowledge` (ablation), `with_oracle` (ceiling) -- unchanged.
- NO-LEAK: `with_frame_activation_f1` must stay < `LEAK_CEILING=0.95` AND not approach oracle
  (< oracle - `LEAK_ORACLE_MARGIN=0.02`).
- **NEW: `with_frame_activation_scramble_kb`** -- deterministic hashlib-seeded permutation
  (`_deterministic_perm`, never python `hash()`) reassigning each process's signature/consumes/
  produces/moves lists to a DIFFERENT process. If the win SURVIVES this scramble, it is a threshold
  artifact, not genuine frame-content matching -- gates HARD-PASS, not just reported.

## HARD-PASS / HARD-FAIL / MIDDLE_BAND bands (pre-registered BEFORE `--full`; TEST-split numbers)
MEASURED@`data/exp_propara_bridging_distilled_kb_endtoend_v1/metrics.json` (TEST, run_mode=full):
`LITERAL_SURVIVAL_FLOOR_TEST=0.1823`, `LITERAL_PAIR_RECALL_TEST=0.2469`,
`LITERAL_PAIR_PRECISION_TEST=0.0905`. MEASURED@`data/exp_propara_bridging_knowledge_vs_mechanism_v1/
metrics.json`: `ORACLE_LIFT_TEST=+0.1062`.
- `FRAME_SURVIVAL_HARD_PASS = 0.3646` (2x the literal floor -- "a doubling", the build spec's own
  suggested margin).
- `FRAME_SURVIVAL_HARD_FAIL = 0.2005` (within ~10% of the literal floor -- mechanism swap didn't
  matter).
- **HARD-PASS** requires ALL of: `survival >= 0.3646` AND `pair_recall > 0.2469` AND
  `pair_precision > 0.0905` (BOTH must move -- recall-only means the threshold is just looser) AND
  `scramble_retained_fraction <= 0.50` (scramble-KB control collapses to <= half the real arm's
  lift) AND ablation collapses (`without_f1 < 0.60`) AND no leak AND arms differ AND decode >= 0.99
  on all 5 arms.
- **HARD-FAIL** on any of: infra fail (arms don't differ / decode < 0.99); ablation didn't collapse;
  leak; `survival >= HARD_PASS` bar but `scramble_retained_fraction > 0.50` (threshold artifact, not
  genuine frame-content matching); `survival >= HARD_PASS` bar but `pair_precision` did NOT improve
  (softer phone-book problem -- more spurious matches, not better ones); OR `survival <= 0.2005`
  (mechanism swap didn't matter -- routes to "the 18-process KB's TEST-split coverage is the real
  ceiling", i.e. SUPPLY more process types, not fix the matcher).
- **MIDDLE_BAND**: survival in the open interval (0.2005, 0.3646) -- recall improves but precision
  doesn't (or vice versa), localizing whether the residual is frame-IDENTIFICATION or ROLE-MAPPING
  specifically; iterate the weaker half before spending further FULL budget.

## HP_SCOPE
`{frame_activation: [survival_beats_literal_floor, pair_recall_up, pair_precision_up,
scramble_kb_collapses, ablation_collapses, no_leak, arms_differ]}`.

## Honest scoping caveat (carried forward from the prior cell's own finding, MUST NOT be dropped)
`exp_propara_bridging_distilled_kb_endtoend_v1`'s own TEST finding (357143e98) diagnosed the deep
residual as **TRIGGER-LOCALIZATION**: the downstream `_assign` placement mechanism searches for a
candidate unmentioned STEP via GENERIC verb-class detection on text
(`step_vclass[t-1] & trig`), where `trig` is a FIXED set per EFFECT TYPE
(`consumes->{DESTROY,CREATE}`, `produces->{CREATE}`, `moves->{MOVE}`) -- independent of WHICH
SPECIFIC PROCESS supplied the role hit. This cell's fix targets STEP 2 (paragraph->process,
participant->role FACT SOURCING / coverage-and-precision), which is a fair, well-scoped, isolated
test of "was it the KNOWLEDGE/MATCHER or the MECHANISM" -- but it does NOT touch the SEPARATE
trigger-localization bottleneck in `_assign`. **If `pair_recall`/`pair_precision` genuinely improve
but overall `survival` stays capped near the literal floor regardless, that is NOT a refutation of
this cell's hypothesis -- it is confirmatory evidence for the prior cell's trigger-localization
diagnosis as an ADDITIONAL, separate wall.** Report both readings distinctly; do not conflate them.

## Cell-template mandates
arms_differ (asserted self-test + recorded, 5 arms); final_metrics_atomicity tmp_replace; except
SystemExit before except Exception (grep-verified, no bare except); crlb_n/a (F1-comparison over a
fixed real corpus, no noise-floor threshold); calibration_check adaptive_with_discriminator_gate;
deterministic_seeding true (hashlib-seeded `_deterministic_perm`, never python `hash()` /
`list(set())` ordering); progress_logging print_flush_true.

## Compute architecture
Sequential-CPU, justified: pure F1-evaluation over a fixed small real corpus (43 DEV / ~54 TEST
paragraphs), no training, no GPU. `concept_similarity` calls are MEMOIZED in-cell (pure/deterministic
function; nested paragraph x process x signature-word x text-token loops re-query the same word
pairs thousands of times -- unmemoized this made a single DEV smoke run take >75s and made
threshold-calibration intractable under system load; memoized self-test runs in seconds). No
batching needed at this scale.

## Self-test findings (real code path)
**MEASURED@`data/exp_propara_bridging_frame_activation_v1/metrics.json` (self_test, run_mode=
self_test):** 18-process KB loaded; official_eval self-test 3 fixtures green. Mechanism-fires proof:
synth paragraph text uses ONLY paraphrases absent from the literal KB ('blaze consumes the timber' --
neither word appears in combustion's literal `signature`/`consumes` lists) -- literal matching gets
`literal_score_synth=0` (structurally cannot fire), graded matching gets `frame_score_synth=0.941,
hits_synth=8` and sources a DESTROY fact (`n_graded_only_role_hits=1`, i.e. a hit literal matching
would have missed). Over-link guard verified (`wood_ash_overlink_guard=0.4077 < ROLE_SIM_THRESH`).
Scramble-KB determinism verified (bit-identical facts across repeat calls with the same seed). 6
verdict-logic unit checks correct (hard_pass / leak / scramble_not_collapsed / no_go / void /
middle_band all classify correctly).

## Smoke findings (DEV) -- SEE COMPLETION REPORT for the measured numbers + threshold-iteration
outcome (iterated post-initial-smoke per the "precision must move" discipline; this pre-reg's bands
above are the FINAL, TEST-facing bands after DEV iteration, per the discipline "DEV-pinned before
TEST, applied unchanged to TEST, no test-set peeking").

## AMENDMENT 2026-08-11 -- MECHANISM-BUG FIX + re-smoke (exp_dev, root-cause-confirmed on disk)
First smoke (ROLE_SIM_THRESH=0.55) HARD_FAILed with TWO confirmed, disk-verified, LOCALIZED
mechanism bugs, not sample noise:
1. `_scramble_kb_processes` moved each process's WHOLE dict (signature+consumes/produces/moves) as
   the SAME Python object to a new name key -- `sorted(id(v) for v in procs.values()) ==
   sorted(id(v) for v in scrambled.values())` was True. Since `_graded_frame_score`/top-2 selection
   never inspects the process NAME (content-driven only), the permutation was a structural no-op --
   `scramble_retained_fraction=1.0` exactly, bit-identical arms, NOT because the win is a threshold
   artifact but because the control never perturbed anything downstream code reads.
   FIX: DOUBLE independent permutation (perm_sig, perm_roles via `_deterministic_perm` with two
   distinct hashlib-seeded keys) decoupling which process's SIGNATURE a name gets from which
   process's ROLE-WORD lists it gets. Frame IDENTIFICATION is unperturbed (same 18 real signatures,
   matching quality preserved); frame EFFECT-SOURCING is now genuinely decoupled from the matched
   frame. `_scramble_kb_processes` self-asserts >=50% of entries have a different sig-donor vs
   role-donor (n_decoupled >= n//2) -- MEASURED@this build: 16/18 signatures and 17/18 role-lists
   differ from their own original name's content after scrambling.
2. `_graded_frame_score` ranked processes by MEAN best-match similarity, not commensurate with the
   literal cell's COUNT-based ranking (`len(set(signature) & text_toks)`) -- a process with one
   spuriously-high-similarity word could outrank a genuinely-matching process with many weaker real
   hits, hijacking top-2 selection. MEASURED@original smoke: graded pair_precision (0.0538) AND
   pair_recall (0.2381) were BOTH below the literal floor (0.0905 / 0.2469) despite graded being a
   structural superset of literal (self-similarity=1.0 for every exact match) -- only explainable by
   process-selection regression. FIX: rank by COUNT of signature words clearing FRAME_SIM_THRESH
   (paralleling literal exactly, generalizing the per-word test from EXACT to GRADED).

RE-CALIBRATION (both bugs fixed; DEV-split grid sweep, 12+ operating points, FRAME_SIM_THRESH x
ROLE_SIM_THRESH, run in-process reusing the memoized similarity cache): no single ROLE_SIM_THRESH
in [0.55, 0.98] simultaneously satisfies all three re-smoke asks on this 43-paragraph DEV split --
ROLE_SIM_THRESH in [0.55,0.65] gives a cleanly-collapsing scramble control (scramble_retained well
under 0, i.e. the decoupled KB does WORSE than the real one -- the control now genuinely fires) but
frame_lift stays negative; ROLE_SIM_THRESH>=0.70 turns frame_lift positive and improves precision
monotonically (plateaus at n_role_hits=139 for any value >=0.80, i.e. all remaining hits are
near-1.0 self-similarity / literal-adjacent) but makes scramble_retained_fraction numerically
unstable (near-zero frame_lift denominator inflates the ratio even though the control structurally
still perturbs the output). RE-PINNED: ROLE_SIM_THRESH=0.70 (the lowest value at which frame_lift
turns positive -- an honest minimum re-pin, not cherry-picked for the best-looking number);
FRAME_SIM_THRESH unchanged at 0.45 (uniformly best across the sweep).

CANONICAL re-smoke (--smoke, DEV, ROLE_SIM_THRESH=0.70): verdict=HARD_FAIL
(HARD_FAIL_FRAME_ACTIVATION_DOES_NOT_BEAT_LITERAL_FLOOR_residual). frame_lift=+0.0061 (was -0.0113),
survival=0.0808 (was -0.1498), pair_recall=0.2619 > LITERAL_PAIR_RECALL_TEST=0.2469 (up, was 0.2381
down), pair_precision=0.0655 < LITERAL_PAIR_PRECISION_TEST=0.0905 (up from 0.0538 but still short),
scramble_retained_fraction=2.417 (was 1.0 exactly -- the control now genuinely differs from the real
arm at every threshold tested, but does not land "well under 0.5" at this operating point).
MEASURED@`data/exp_propara_bridging_frame_activation_v1_smoke/metrics.json`.

HONEST RESIDUAL DIAGNOSIS (neither of this pre-reg's two hypothesized residuals -- slot-instantiation
degeneracy or KB frame-coverage-too-small -- is what the evidence shows; RECALL is fine/better, so
coverage is not the wall): the residual is **KB ROLE-VOCABULARY PROMISCUITY**. The top-2-processes /
full-role-list-per-process architecture (shared with the literal cell -- this is not a graded-only
design flaw) checks a participant against BOTH matched processes' entire consumes/produces/moves
vocabulary; several role-words recur across DIFFERENT processes (generic terms like heat/water/
material). Literal already pays a precision cost for this (TEST pair_precision=0.0905 is itself
low); graded's broader coverage extends BOTH true and false positives from the same promiscuous
surface, and on this DEV split the net effect is a recall win but not (yet) a precision win.
CAVEAT (disclosed, not rationalized post-hoc): this pre-reg's OWN docstring already records
`LITERAL_SURVIVAL_FLOOR_DEV=0.033` vs `LITERAL_SURVIVAL_FLOOR_TEST=0.182` -- a 5.5x gap -- and the
literal cell's OWN DEV smoke (`data/exp_propara_bridging_distilled_kb_endtoend_v1_smoke/
metrics.json`) was ALSO formally HARD_FAIL (survival=0.033) yet still proceeded to its TEST-split
FULL run (357143e98). DEV is a known-noisier/harder split for this entire corpus/architecture, not
specific to this fix. Recorded as context for the strategic FULL/no-FULL call, not as license to
route around the re-smoke gate -- exp_dev did NOT dispatch FULL given re-smoke does not clear all
three explicitly-asked gates (scramble well-under-0.5 not met; precision_up not met; frame_lift>0
met; recall_up met).

## AMENDMENT 2 2026-08-11 -- OPTION-b CONVERGENCE GATE + HARD PRE-COMMITTED EXIT (exp_dev)
Director decision (rejecting FULL-despite-DEV-shortfall; the reason reframes the problem): the v2
tiny frame_lift is NOT correct-frame-binding -- the scramble control (0.0 oracle overlap) gave
scramble_lift=+0.0147 > frame_lift=+0.0061 and scramble_f1 0.3388 > frame_f1 0.3302, i.e. WRONG
facts beat RIGHT facts (a correctness-ANTI-correlated signal no DEV/TEST scaling can fix). Whole game
for Option-b: make CORRECT frame binding beat SCRAMBLED binding with a real margin; if not, the
matcher route is done.

FIX BUILT (brain: coincidence detection): CO-PARTICIPATION-GATED frame selection -- a process may
donate fates only if the paragraph convergently CONFIRMS it (>= MIN_CONVERGENT_ROLES=2 DISTINCT roles
each filled by a participant AND >= MIN_CONVERGENT_FILLERS=2 DISTINCT participants doing the filling).
A hard boolean GATE on which process may donate, NOT an additive score. PRIOR-ART CAUTION honored
(SIQa iter-1 79c354a6d / iter-2 e7cee79ae): raw convergence-COUNT as an additive scoring feature was
a net drag and was dropped; iter-2 kept convergence ONLY as a >=2-distinct STRUCTURAL gate -- this
gate reuses that exact validated pattern. ONE VARIABLE vs v2 = the frame-SELECTION criterion (KB
content, thresholds, role-mapping, downstream _grids, oracle/without/prior_lesion arms all UNCHANGED).

DISK CONFIRMATION the gate changes selection (director-mandated pre-smoke check, throwaway print):
on 12 real DEV paragraphs, REAL-KB donors 16 -> 15 (barely touched -- correct processes converge:
fossilization roles=3/fillers=4, electricity_generation roles=3/fillers=5, combustion roles=2-3),
SCRAMBLE-KB donors 16 -> 1 (decoupled random role-word lists do NOT convergently co-occur). The
coincidence detector WORKS as designed -- asymmetric in exactly the intended direction.

RE-SMOKE (DEV, convergence gate, operating point CAND_K=4 / MIN_FILL=2; identical across the full
CAND_K in {3,4,6} x MIN_FILL in {2,3} sweep -- all 6 configs fail the same way):
MEASURED@`data/exp_propara_bridging_frame_activation_v1_smoke/metrics.json`:
- without_f1 (bridge OFF)        = 0.3242
- scramble_f1 (bridge ON ~empty) = 0.3388   <- HIGHEST non-oracle arm
- frame_f1   (bridge ON gated)   = 0.3273
- oracle_f1  (bridge ON gold)    = 0.3993   <- knowledge IS usable, far above all matcher arms
- frame_lift = +0.0032 (DOWN from v2 +0.0061), scramble_lift = +0.0147 (UNCHANGED)
- frame precision = 0.0625 (< literal 0.0905), recall = 0.2143
- gate-pass asymmetry: real 0.30 vs scramble 0.012 (26x) -- structural gate works; scramble sources
  only 5 role-hits / 1 donor / 2 participants.

VERDICT = HARD_FAIL. BOTH pre-committed EXIT conditions are met: (1) scramble matches/exceeds real
(scramble_f1 > frame_f1; scramble_lift > frame_lift), AND (2) precision stays below the literal floor
(0.0625 < 0.0905). Per the director's HARD pre-committed exit, exp_dev did NOT iterate a third
mechanism variant.

WHY (mechanism-level, airtight): the convergence gate correctly fixed PROCESS SELECTION (scramble
donors collapse 16->1) but F1 is driven by the per-participant ROLE->EFFECT ASSIGNMENT, which the
gate does not touch. Even for a correctly-selected, well-evidenced process (combustion in a
combustion paragraph), deciding WHICH participant gets DESTROY vs CREATE vs MOVE via promiscuous
role-word lists is ~94% wrong (precision 0.0625), and those wrong bridge facts mislead the placement
loop worse than sourcing none (frame 0.3273 < near-empty scramble 0.3388). The oracle arm (gold
per-participant facts) sits at 0.3993 -- the knowledge is usable; the matcher cannot source the
correct per-participant fate from the prose.

STRATEGIC FINDING (for director/USER, not a thing to keep tuning): the residual is CONTEXT-CONDITIONED
per-participant frame-role assignment = reading the specific participant's specific fate out of the
prose = the SITUATION-MODEL / EXTRACTION wall, NOT frame SELECTION (which is now solved by the
convergence gate) and NOT missing KNOWLEDGE (oracle proves it usable). The associative-matcher route
to ProPara bridging is DONE; the next lever is reading prose into the right per-entity structure
(situation-model / extraction), a separate build. Convergence-gate code is retained (CONVERGENCE_GATE
= True) because the mechanism is correct and brain-faithful and the negative F1 result IS the finding;
its metrics.json records the exit.

## AMENDMENT 3 2026-08-11 -- OPTION-c NATIVE THEMATIC-ROLE ASSIGNER (owned labeler) (exp_dev)
Director-directed (explicitly NOT a violation of the Option-b pre-committed exit: that exit forbade
more FRAME-SELECTION tuning; the convergence gate is DONE and correct. This attacks the DIAGNOSED
residual -- per-participant ROLE->EFFECT assignment -- with the RIGHT owned tool).

THE OWNED ORGAN (reused, not reimplemented): hdlab/thematic_role_labeler.py -- MacWhinney
Competition-Model cue-integration, an averaged perceptron over surface cues (word-order/animacy/voice)
weighted by learned cue-validity + verb selectional frames. Parse front-end = owned hdlab/pos_tagger
+ arc_parser (UAS ~0.79) via hdlab/candidate_generator. NO spaCy/SRL/LLM -- 100% glass-box.
Registry-validated +0.264 over a matched positional baseline on non-canonical held-out. Trained via
the validated cell's recipe (exp_thematic_role_labeler_cue_integration_v1.build_data; that cell's
module-level run was guarded under __main__ this build so build_data is importable WITHOUT running its
experiment -- behavior-preserving, verified via --self-test parity).

ONE VARIABLE vs the promiscuous frame arm: the per-participant role assigner ONLY. Convergence-gated
frame SELECTION, the KB, thresholds, downstream _grids, and oracle/without/prior_lesion arms are
UNCHANGED. Promiscuous arm KEPT as the comparison baseline (with_frame_activation), native arm ADDED
(with_frame_activation_native_roles) + its scramble control.

MECHANISM (_compute_native_effects): per (paragraph, participant), read the set of {CREATE/DESTROY/
MOVE} effects the participant UNDERGOES directly from text -- a participant undergoes a governing
verb's effect-class (owned VERB_CLASS_SETS lexicon) iff at some argument-mention it is a thematic
UNDERGOER: (a) trained pred_fn role in {PATIENT,EXPERIENCER}, OR (b) passive-clause subject, OR (c)
UNACCUSATIVE -- inanimate subject (owned animacy_lexicon) of an INTRANSITIVE change verb (the
'water evaporates'/'rock forms' case the narrative-agent-trained perceptron mislabels AGENT). The
KB is KB-INDEPENDENT here; the KB gates downstream via convergence + slot-license, so the SAME native
map feeds both the real and scramble native arms (isolating 'does scrambling the KB collapse it?').

DATA GATE (director-mandated, measured BEFORE wiring): (1) parse-coverage of change-step participants
as verb args = 0.952 (157/165) -- the owned parser finds them. (2) verb-frame coverage: 8/34 ProPara
scientific verbs in VERB_FRAMES, 26/34 hit DEFAULT_FRAME (still subj->AGENT/obj->PATIENT, workable).
(3) 5-sentence + full labeler smoke: trained pred_fn correctly assigns PATIENT to PASSIVE subjects
('fuel is consumed', 'remains are buried', 'CO2 is released', 'sediment is deposited' all -> PATIENT
-- the labeler's real value over positional). The ONE systematic gap = active-intransitive
unaccusatives ('water evaporates' -> AGENT), which the owned animacy+intransitivity rule (c) recovers.

CAVEATS stated in metrics (director-required): pred_fn is McGuffey-canonical-trained (USER standing
rule = MODERN sources only) -- if the arm shows promise a follow-up retrains on modern process text;
arc_parser UAS ~0.79 injects parse error (measured as coverage).

DECISIVE MEASURES (all pre-registered; native_roles_verdict): HARD_PASS requires ALL of --
(a) native pair-precision > promiscuous pair-precision AND > literal floor 0.0905;
(b) native captures >= 30% of the oracle per-participant lift (native_survival >= 0.30);
(c) scramble-KB COLLAPSES the native arm (native_scramble_retained_fraction <= 0.50);
plus infra (arms differ + decode >= 0.99) + ablation-collapse + no-leak. Any miss -> HARD_FAIL naming
the failed gate (director: report WHY -- coverage / mapping / parse-error -- do not paper over).

RE-SMOKE (DEV; MEASURED@`data/exp_propara_bridging_frame_activation_v1_smoke/metrics.json`):
- native_f1 = 0.3388, native_scramble_f1 = 0.3388 (BIT-IDENTICAL), promiscuous_f1 = 0.3273,
  oracle_f1 = 0.3993, without_f1 = 0.3242.
- native_precision = 0.0357 (< promiscuous 0.0625 < literal 0.0905) -- gate (a) FAILS.
- native_recall = 0.0476 (<< literal 0.2469). native_lift = +0.0147, native_survival = 0.195 (<0.30)
  -- gate (b) FAILS. native_scramble_retained = 1.0 -- gate (c) FAILS.
- VERDICT = HARD_FAIL[precision_not_above_promiscuous_and_literal + does_not_capture_oracle_lift +
  scramble_kb_does_not_collapse].
The owned labeler READS well (not a parse failure): parse-coverage 0.9486; role_distribution PATIENT
288 > AGENT 223 (trained perceptron correctly flips passives); 15 unaccusatives recovered.

PRECISE WHY (director-mandated; probed over the 62 dev oracle-fact participants) -- DUAL cause:
1. COVERAGE (dominant): native effect PRESENT for only 24/62 = 0.387 of oracle-fact participants.
   61% get NO native effect -- their fate is NOT locally predicated as an undergoer relation (they are
   the UNMENTIONED-fate participants: sediment/fuel/heat -> DESTROY, material/oil -> CREATE, mechanical
   energy/water/truck -> MOVE all native=[]). A text-reading role labeler structurally cannot source a
   fate the text does not state.
2. MAPPING: of the 24 present, native effect OVERLAPS oracle only 10/24 (~42%); the governing-verb
   effect-class disagrees with the gold per-participant effect >half the time (bacteria buried ->
   native MOVE but gold DESTROY; trash -> native CREATE but gold MOVE). Effect-distribution mismatch:
   oracle MOVE=36 (dominant) but native MOVE=7; native over-produces CREATE (16 vs oracle 12) from
   passive 'deposited/formed' predications.
3. gate (c) bit-identical-under-scramble: native effects are text-derived (KB-INDEPENDENT), so
   scrambling the KB cannot perturb them -- itself proof the native arm does LOCAL READING, not
   KB-frame binding, and local reading cannot reach the unmentioned fates.

STRATEGIC FINDING (triangulated, 3rd independent angle): the residual is UNMENTIONED per-participant
fate INFERENCE, NOT local role-reading. The owned thematic-role labeler reads LOCAL roles well
(passives, unaccusatives), but 61% of the target fates are not in the text to read. This CONVERGES
with + SHARPENS the Option-b situation-model/extraction-wall finding: the wall is specifically
INFERRING fates for participants whose change is never textually predicated -- an inference-over-
knowledge problem the oracle (gold unmentioned facts, 0.3993) solves but neither the KB word-matcher,
the convergence gate, NOR the owned role labeler can source. Per the do-not-keep-tuning discipline,
exp_dev did NOT build a 4th mechanism variant; this is the strategic finding for director/USER.

Owned organs REUSED (not reimplemented): thematic_role_labeler, pos_tagger, arc_parser,
candidate_generator, animacy_lexicon, VERB_CLASS_SETS; the validating cell's build_data recipe made
importable via a behavior-preserving __main__ guard (verified via --self-test parity). Native arm
retained (NATIVE_ROLES_ARM=True); its metrics.json records the finding.
