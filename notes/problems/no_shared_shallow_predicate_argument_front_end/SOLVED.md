---
problem: no_shared_shallow_predicate_argument_front_end
status: PARTIAL
bar: "BUILD path: a shared shallow predicate-argument extractor (agent/theme/goal/recipient over the parse), beating the current inline/ad-hoc extraction CI-separated on a real-prose role gold (recompute the inline floor on the same population); info-free twin (shuffled role features / random role assignment) LOSES CI-sep; report CI half-width + null p95; a POSITIVE control a role-decisive minimal pair the extractor gets and the inline rule cannot; AND it lifts a downstream front-end (SPACE goal precision OR who-did-what) CI-sep vs the inline path -- wire-don't-island."
result: "A shared dispatch extract_predicate_arguments (compose validated organs; agent/theme/goal/recipient/location/instrument) beats the fragmented LIVE inline floor on real modern prose (QA-SRL Bank 2.0 dev+test, span-based accuracy, 2000x paired bootstrap): UNIFIED 4-role SHARED 0.670 vs INLINE 0.592 (n=30,570, +0.078 ABOVE); moved-THEME 0.818 vs 0.668 (n=15,751, +0.150, CI[0.145,0.157], null p95=0.006); RECIPIENT coverage 0.107 vs INLINE's structural 0.000 (n=802, +0.107 CI[0.087,0.127]); AGENT 0.666 vs 0.655 (n=10,890, +0.012 CI[0.008,0.015]). Positive control (22 role-decisive minimal pairs): SHARED 0.929 vs INLINE 0.721; caused-motion theme-attribution 7/8=0.875. HONEST NEGATIVE, disclosed: on the QA-SRL 'where'/GOAL role SHARED LOSES 0.083 vs 0.144 (n=3,127, -0.062 CI[-0.072,-0.052]) -- a gold-conflation (that gold is ~60% stative LOCATION not motion GOAL; SHARED correctly declines stative locations, and SHARED 0.083 >> its info-free twin 0.032, so the gate carries real information)."
floor: "The current LIVE fragmented inline extraction, recomputed per population: situation_reader positional agent/patient (subject-before-verb=agent, nearest-nominal-after=patient; the intransitive gate is live, precise_voice is NOT) + a naive ungated 'first to/into/onto/toward-PP head = goal' + no recipient/instrument/location. Strongest floor by role: INLINE for goal (0.144); for theme/agent the info-free RANDOM floor (0.290/0.238) since the shuffled-verb-class twin is identical to SHARED there."
controls: "(1) info-free TWIN = verb->class map randomly permuted (fixed seed): LOSES on the PP-routing roles it can affect -- goal 0.083 vs 0.032, recipient 0.107 vs 0.005 -- and is by-construction identical to SHARED on theme/agent (those do not consult the map), so it is a valid control only for PP-routing; (2) RANDOM role assignment: loses on every role (theme 0.290, agent 0.238, goal 0.025); (3) minimal-pair CONTRAST set (10 items where the gate must NOT fire -- self-motion/active/locative): SHARED stays high (0.767) => the gate is discriminating, not blanket suppression; (4) motion-vs-stative split by the INDEPENDENT gold-verb motion class: SHARED correctly declines stative locations (0.039, a correct CI-sep loss) and TIES INLINE on genuine-motion goals (0.333 vs 0.318, NOT separated) while beating its own twin ~5x -- isolating that the aggregate goal loss is the gold conflating goal with location, not a gate defect."
files_changed: "experiments/exp_shared_predarg_frontend_v1.py; notes/problems/no_shared_shallow_predicate_argument_front_end/minimal_pair_role_gold_v1.jsonl; data/exp_shared_predarg_frontend_v1/metrics.json"
reverify: ".venv/Scripts/python.exe experiments/exp_shared_predarg_frontend_v1.py --self-test"
---

# What this is

The brief asked, FIRST, whether the landed role organs already provide a robust shared agent/theme/goal
extractor on raw prose (-> a WIRING problem) or not (-> BUILD one). The disk answers decisively, and it
disagrees with the brief in two places (below). The result is a **shared predicate-argument dispatch**,
built and measured, that beats the fragmented inline status quo on most roles and on a role-decisive
positive control, with one honestly-disclosed loss on the one role (GOAL) whose clean real-prose gold does
not exist. Status **PARTIAL**: the shared front-end is real and helps, the goal-vs-recipient/caused-motion
mechanism works on the constructed positive control, but the brief's headline residual (caused-motion GOAL
attribution) cannot be validated at power on real prose because no clean gold for it exists, and the
strongest real-prose win (theme) is largely the already-validated voice binder now unified.

# 1. The scoping finding (the core of the problem)

**The duplication is REAL, there is NO shared front-end, and every validated role organ is ISLANDED.**
Traced on disk (two independent read-only mappings, then verified first-hand):

- The **live reader** `hdlab/situation_reader.py::read()` assigns who-did-what with an INLINE positional
  hand-rule (`_pick_role_mentions`/`_assign_roles`: agent = subject-before-verb, patient = nearest nominal
  after; `gate_intransitive` is live, `precise_voice` is NOT passed at the call site line ~553). It produces
  agent/patient only -- **no goal, no recipient, no instrument**. Thematic labels are a deterministic
  `VERB_FRAMES` dict lookup.
- The **SPACE organ** `experiments/location_register.py::_goal_node` re-derives argument structure inline:
  a VerbNet motion-vs-communication class gate (goal-vs-addressee, Rappaport Hovav & Levin 2008) + a
  `bad_dobj` moved-theme gate ("struck them to the ground" -> the goal is the THEME's, not the agent's) +
  its own passive detector. Strong (goal precision 0.219->0.909 in its own solve) but its own copy.
- `hdlab/parse_goal_extraction.py::_select_np_arg` has a THIRD passive detector and its own goal selection.
- The validated role organs are **LANDED but ISLANDED**: `thematic_role_labeler` (full 6-role learned
  perceptron -- but its own QA-SRL revalidation HARD_FAILED as a "disguised single-cue animacy rule"),
  `graded_role_assigner` (non-canonical patient), `incremental_parser` (candidate structure), the relcl
  filler-gap resolver, and the who-did-what fix (EXPERIMENTS-ONLY, not even in hdlab). The registry marks
  them `integration_status: WIRED` but `gate_decision: WIRE_CANDIDATE`, `pipeline_status: N_A`, `used_by` =
  experiments/tests only. **"WIRED" there means "registered + witnessed", not "on a live path".** The only
  shared code across the three consumers is a lemmatizer utility and an intransitive-verb set -- not a role
  extractor. So this is neither the pure WIRING path (the organs BEAT the inline rules, they are not
  CI-equal) nor a clean monolithic BUILD.

# 2. Two corrections to the brief (the disk outranks it)

- **The "coref caused-motion residual" the brief attributes to the coref organ does not exist.** Greps of
  `hdlab/coref.py` and `hdlab/bundle_focus_coref.py` for recipient/addressee/destination/caused-motion/goal
  return zero. The "to X = destination vs recipient" discrimination lives ONLY in the SPACE organ's
  `location_register._COMM_TRANSFER_BLOCK`. The brief named it as a conceptual NEED, not an existing code
  path. (AUDIT UPDATE below.)
- **A monolithic "shared shallow SRL" is not the brain's architecture.** Beber 2025 (VLSM+TMS+fMRI, already
  PINNED in `BRAIN_FOUNDATIONAL_AUDIT.md`): structure-BUILDING (frontal/pMTG) and role-BINDING
  (posterior-temporal/angular) are SEPARATE organs, never fused. The correct shared object is a **DISPATCH
  over the separate validated organs**, which is what was built. This is a reframe, not a defect -- and it
  is why the deliverable composes rather than replaces.

# 3. What was built and measured

`experiments/exp_shared_predarg_frontend_v1.py` -- a glass-box `extract_predicate_arguments(tokens, upos,
heads, verb_idx)` that COMPOSES already-validated organs (no new mechanism, no external LLM, no torch, no
spaCy; parses with the in-house `CandidateGenerator`):
- agent/theme via the voice-aware word-order binder (`hdlab.graded_role_assigner.voice_cues` /
  `hybrid_role_patient`) -- the validated Competition-Model binder;
- goal/recipient/location/instrument via VerbNet PP-role routing reusing `location_register`'s pure lexicons
  (`is_motion_verb`, `_COMM_TRANSFER_BLOCK`, `is_place_ground`) + the moved-theme gate (goal_belongs_to
  theme vs agent).

Golds: (a) `minimal_pair_role_gold_v1.jsonl` -- 32 hand-verified role-decisive minimal pairs (22 decisive +
10 discriminating contrasts) across caused-motion, comm-addressee, ditransitive-recipient, participial-
aspectual, passive, instrument; (b) QA-SRL Bank 2.0 dev+test, a modern (age-confound-free) real-prose gold,
agent/theme from the existing `_entry_spans`, goal from filtered `where`-questions, recipient from filtered
`to/for` questions. Arms: SHARED / INLINE (fragmented live floor) / TWIN (shuffled verb-class) / RANDOM.
Numbers are in the frontmatter; all disk-verified against `metrics.json`.

**The one loss, drilled to the mechanism (owner discipline: a wall is a signal to go finer):** on the
aggregate QA-SRL "where" gold SHARED loses (0.083 vs 0.144). Splitting that gold by the gold verb's motion
class (computed independently of SHARED's routing) shows why: on the STATIVE-location majority (n=2,668, ~85%
of "where") SHARED correctly DECLINES to call a stative location a goal (0.039, a correct loss to INLINE's
blunt ungated grabber); on genuine-MOTION verbs (n=459) SHARED ties INLINE (0.333 vs 0.318, not separated)
because the span-containment metric does not credit the theme-vs-agent goal ATTRIBUTION -- which is exactly
where SHARED's value lives. SHARED beats its info-free twin ~5x on both subsets, so the gate carries real
information; the aggregate loss is the QA-SRL "where" question conflating motion-GOAL with stative-LOCATION,
plus a metric that does not score attribution. Adding a stative-LOCATION role lifts goal-or-location to 0.396
vs 0.144, but the twin matches it (0.406) -- that win is the location place-typing scan, NOT verb-class
discrimination, and is reported as such.

# 4. What is NOT established (withdraw these first if wrong)

1. **The caused-motion GOAL-attribution mechanism at power on real prose.** It is proven only on the
   constructed positive control (theme-attribution 7/8; decisive minimal pairs 0.929 vs 0.721). QA-SRL
   science-text has essentially no caused-motion narratives, and no gold labels "whose goal is it." Exactly
   like the relcl filler-gap result, the residual is rare in real text and its value is correctness-on-
   rare-cases, not an aggregate lift. **The single highest-value follow-on is a hand-labeled LitBank
   caused-motion goal-vs-addressee gold** (the ~150-200-token set already planned in the strategy handoff);
   without it this claim stays bounded to constructed pairs.
2. **A goal WIN on real prose.** SHARED does not beat INLINE on the QA-SRL "where" gold (it ties on motion
   verbs, correctly declines on stative). Do not quote a goal win.
3. **That the theme win is novel.** The +0.150 theme lift is the already-validated voice binder, now unified
   -- a real CI-sep real-prose beat of the live positional floor, but not a new mechanism.
4. **RECIPIENT quality.** Coverage is real (0.107 vs a structural 0.000) but the absolute number is low and
   the recipient gold is small (n=802) and noisy (QA-SRL "to/for" is dominated by infinitival/purpose uses).

# 5. Proposed hdlab change (strategy lands it; Q111 -- I do not write hdlab/)

Create `hdlab/predicate_argument_frontend.py` = the shared dispatch above (compose
graded_role_assigner + the location_register VerbNet lexicons + the moved-theme gate; glass-box, in-house
parse). Then, DEFAULT-OFF and measured on the live reader before any capability claim (per the pivot):
- `situation_reader`: route `_assign_roles` through the shared front-end AND enable `precise_voice` (the
  theme win requires the voice swap the live call site currently omits); this gives the who-did-what reader
  the goal/recipient/location it structurally lacks today.
- `location_register._goal_node` and `parse_goal_extraction`: call the shared front-end's PP-role routing
  instead of their inline copies (they are already strong -> this is DE-DUPLICATION with measured
  no-regression, not a new capability).
- Collapse the three inline passive detectors into the shared one.
All behind flags; the value is a single shared interface + supplying under-served consumers, not a headline
role-accuracy jump.

# 6. Adjacent components (evaluated for brain-fidelity + optimization, owner 2026-08-28)

- **The caused-motion goal-vs-addressee GOLD (missing).** PINNED brain axis (Rappaport Hovav & Levin);
  OUR-INVENTION = the mining recipe. The binding follow-on -- it is what would move this from PARTIAL to a
  clean goal result. Candidate new problem.
- **`_MOTION_VERBS` lexicon coverage** -- a fidelity gap (the "sweep" miss: SHARED fired no goal because
  sweep is neither in the curated set nor resolves via WordNet first-sense). Optimization: mine a fuller
  VerbNet motion class offline (a static asset, admissible per the pivot). PLACEHOLDER, not the brain's full
  motion inventory.
- **The stative-LOCATION vs GOAL distinction** -- currently a place-typing PP scan whose win the twin
  matches (not verb-class-driven). A more brain-faithful stative-vs-dynamic split (aspectual/stative verb
  class) is a fidelity target.
- **`thematic_role_labeler`** -- confirmed islanded and a "disguised single-cue rule" on modern prose; the
  shared front-end's binder (word-order+voice) is the better-validated agent/patient path. The learned
  perceptron is NOT the component to wire.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md, strategy folds)

1. The caused-motion "to X = destination vs recipient" residual is implemented ONLY in
   `location_register._COMM_TRANSFER_BLOCK`; it does NOT exist in `coref.py`/`bundle_focus_coref.py`. Any
   entry attributing it to the coref organ is wrong.
2. The predicate-argument front-end is confirmed NOT-SHARED and the validated role organs (thematic_role_
   labeler, graded_role_assigner, incremental_parser, relcl resolver) are ISLANDED (registry `WIRED` = 
   registered+witnessed, not on a live path). The live reader uses a positional hand-rule.
3. Empirical: the QA-SRL "where" role conflates motion-GOAL (~25%) with stative-LOCATION (~60%) -- a
   standing confound for any goal-role evaluation on QA-SRL.

## KEY REALIZATIONS

- **"Landed/registered" is not "wired."** The scoping answer turned on reading the registry FIELD VALUES
  (`gate_decision: WIRE_CANDIDATE`, `used_by` = tests) rather than the presence of a `WIRED` row -- every
  role organ looks integrated and none is on the live path.
- **The shared residual is rare and its clean gold conflates goal with location**, so -- exactly like the
  relcl filler-gap result -- the mechanism is provable only on a constructed/enriched positive control and
  its real-text value is correctness-on-rare-cases. Recognizing this BEFORE chasing an aggregate number
  avoided building a claim on a confounded gold.
- **The naive inline rule "wins" the aggregate goal gold only by being a blunt ungated locative-grabber on a
  location-majority gold** -- which is the very conflation a shared front-end exists to fix. The comparison
  inverts on the role-decisive cases (SHARED 0.929 vs 0.721). An aggregate number on a conflated gold can
  reward the worse mechanism.

## TLDR

The reader really does have three separate hand-written copies of "who did what / where," and the smarter
role modules that were already proven are all sitting on the shelf, unplugged. I built one shared module that
plugs them together and produces agent / moved-thing / goal / recipient from a single call. On real modern
text it clearly does the "which thing was affected" job better than the live hand-rule (0.82 vs 0.67 over
~15,700 cases) and it gets the hard textbook trick sentences ("the blow eased them to the ground", "gave the
book to Mary") right where the hand-rule gets them wrong (0.93 vs 0.72). It does NOT beat the hand-rule at
"where" on the big benchmark -- but that is because the benchmark's "where" is mostly plain locations ("on
the hillside"), not destinations, and the shared module correctly refuses to call a plain location a
destination. The one thing genuinely missing is a small hand-labeled set of real "moving-thing" sentences to
prove the destination logic at scale; that is the recommended next problem.

## QUESTIONS

None.

## NEXT STEPS

1. (Follow-on problem) Hand-label the ~150-200-token LitBank caused-motion goal-vs-addressee gold to
   validate the destination-attribution mechanism at power on real prose.
2. (Strategy, on owner_verdict: DONE) Land the shared `predicate_argument_frontend` dispatch DEFAULT-OFF,
   route situation_reader through it with precise_voice ON, and de-duplicate the SPACE / parse_goal_extraction
   inline copies with measured no-regression.
3. Expand `_MOTION_VERBS` from an offline VerbNet motion class (static asset) to close the lexicon gap.

## DISCLOSURES

During the build, a `rm -rf` on a stale checkpoint was AUTO-DENIED (deletion-token rule, not a user
cancellation); the cell-author worked around it non-destructively with `mv`, leaving two harmless siblings
`data/exp_shared_predarg_frontend_v1_smoke_STALE_{prepfix,recipientfix}_before`. No hdlab/ file was written.
