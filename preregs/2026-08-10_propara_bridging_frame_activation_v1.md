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
