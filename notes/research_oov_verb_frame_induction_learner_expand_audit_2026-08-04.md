# DESIGN/INTEGRATION AUDIT: OOV verb-frame acquisition -- expand the learner, don't island

**Trigger:** skunkworks re-VET DOWNGRADE of `thematic_role_labeler_cue_integration_v1`
(`notes/skunkworks_reVET_thematic_role_labeler_cue_integration_v1.md`, commit d71da0858).
Revival criterion #2: "OOV psych-verb handling: learned frame induction/bootstrapping, not a
static ~150-lemma dict; report OOV-verb accuracy explicitly." USER directive: "don't we already
have a learning function? can it be expanded to this?" -- audit only, no cell run.

## HEADLINE

**EXPAND, not build-new.** `hdlab/learner/registry.py::learn()`/`apply()` already accepts
arbitrary `(episodes, features, hypothesis_space_spec)` and auto-selects across 4 hypothesis
classes via MDL. Frame induction (novel-verb-in-construction -> subj=AGENT-vs-EXPERIENCER) is
directly expressible as an existing-plugin CONFIG problem: `episodes` = one per (verb-occurrence,
gold subj-role), `features` = a NEW cue-atom encoder that excludes the verb lemma itself (so the
induced hypothesis genuines transfers to unseen verbs), `hypothesis_space_spec['candidate_plugins']
= ["estimation","ruleind","proginduction"]`. **No new plugin file is required** -- `core.py` and
`registry.py` need zero changes; the only new code is a per-competence feature-encoder module
(`hdlab/frame_induction.py`, does not exist yet) plus the wiring edit in
`thematic_role_labeler.py::frame_slot_role`. This is the cleanest possible EXPAND: the module's
own docstring ("adding a new hypothesis class means writing one new plugin... core.py needs zero
changes") undersells it -- you don't even need a new plugin here, just new CONFIG, which the
module explicitly treats as caller-owned input.

Two mislabels caught in the task prompt while disk-verifying (per session discipline "trust
nothing by name"):
1. **`hdlab/self_improving_loop.py` is NOT a "mint engine."** Disk-verified: it is the
   coherence-gated autonomous keep/revert ROUTER (promoted 2026-08-02 from
   `exp_coref_autonomous_fix_router_v1`) -- decides whether to ADOPT a candidate whole-passage
   coreference resolution vs keep baseline, using FHRR role-decode margin deltas. It has nothing
   to do with minting new types. The actual "read -> detect novel -> MINT new causal-role type"
   engine is `experiments/exp_self_extension_loop_v1.py` (mints event/schema TYPES like
   'goal-blocker', triggered by `predictive_coding.residual_magnitude` against a seed schema
   library `W`) -- a different axis (event-schema minting, continuous FHRR residual) from
   verb-ARGUMENT-STRUCTURE frame induction (discrete AGENT/EXPERIENCER per verb, syntactic-cue
   driven). Composable in principle (same residual-gate PRINCIPLE) but NOT the same mechanism and
   NOT already wired to `thematic_role_labeler.py`.
2. **`hdlab/predictive_coding.py`'s novelty gate is a poor SHAPE match for OOV-verb triggering**,
   even though it is real and does work (verified: bipolar residual-magnitude threshold/
   proportional gates for an FHRR associative-memory `W`). Frame lookup is a DISCRETE dict
   (`VERB_FRAMES.get(lemma, DEFAULT_FRAME)`); "is this verb OOV" is already a trivial, exact
   `lemma not in VERB_FRAMES` membership test -- reaching for a continuous bipolar-residual novelty
   signal here would be a forced reuse (wrong shape: continuous vector mismatch vs discrete
   symbol-table lookup) for a problem that doesn't need one. Recommend NOT wiring
   predictive_coding into this path; note it honestly rather than force it for "wire-don't-island"
   optics.

## Asset table (disk-verified)

| Asset | What it ACTUALLY does (verified) | Reusable for OOV thematic-frame induction? |
|---|---|---|
| `hdlab/learner/core.py` (`mdl_select`, `per_cluster_gate`, `LearnResult`) | Generic two-part-code MDL selection across ANY plugin fits for ONE task; glass-box assert; episodic-fallback gate. Domain-agnostic, verified no task-specific code. | **VERBATIM.** This is the shared engine; needs zero edits. |
| `hdlab/learner/registry.py` (`learn`/`apply`) | Fits every candidate plugin on caller-supplied `(episodes, features, hypothesis_space_spec)`, MDL-selects, returns glass-box hypothesis. | **VERBATIM.** Call directly with new CONFIG; no plugin registration edit needed if reusing `estimation`/`ruleind`/`proginduction`. |
| `estimation_plugin` (Laplace-smoothed single-key counting, `generic_mdl` mode) | `key_fn(ep) -> label` counting table, MDL-scored. Cheap, O(1) lookup, no conjunction search. | **ADAPT (config only).** Good baseline candidate: key = a single pre-conjoined cue-bundle string. |
| `ruleind_plugin` (MDL-gated sequential-covering conjunction rules) | Searches feature-VALUE conjunctions (axis-aligned regions), covers with residual episodic fallback. Verified: wraps `exp_parser_ruleinduction_cls_ppattach_v1.induce_rules` verbatim. | **ADAPT (config only).** Best fit for discovering WHICH cue conjunction (e.g. `stative:yes ^ obj_animacy:no`) predicts EXPERIENCER, rather than hand-picking one. |
| `proginduction_plugin` (bounded enumerative boolean-DSL synthesis over declared atoms) | Total boolean function over declared atoms; evaluates on UNSEEN atom-combinations (not a lookup table). Verified: this plugin's own docstring names the EXACT failure class the re-VET found (marginal-driven cue-conflict on a combo whose marginals point the wrong direction) as its reason for existing. | **ADAPT (config only), HIGH VALUE.** Directly targets the re-VET's diagnosed failure mode (linear/lookup mechanisms let `order:pre` majority-marginal override the correct frame cue). Recommend as a 3rd candidate plugin, not just estimation+ruleind. |
| `gam_plugin` | Not read in depth this pass (out of scope; additive-shape hypothesis class) -- no obvious fit, skip. | Not evaluated / low priority. |
| `exp_read_grow_oov_verb_extension_v1.py` (`_classify_unk_token`, `_oov_verb_base_and_form`, `ie_extract_verb_extended`) | Disk-verified: solves a DIFFERENT problem -- classical-tagger MISTAG recovery for a CLOSED-RELATION extraction schema (eats/chases/lives_in). `OOV_VERB_BASE_LEX` is a hand-declared SYNONYM->relation dict (9 entries: munch/nibble/devour/gobble->eats, etc), looked up by morphological base-form recovery, NOT induced from syntactic construction. HARD_PASS was measured on POS-tag coverage/precision, zero AGENT/EXPERIENCER/thematic content anywhere in the file. | **NO (not verbatim), ADAPT-marginal at best.** `thematic_role_labeler.lemma_verb()` already does equivalent morphological stripping for this task's needs. The only transferable idea is the PATTERN (suffix-strip + irregular table + tagger-fallback), which is already independently present in the target file. Reusing the actual code here would be a forced/wrong-shape fit (solves POS recovery, not frame semantics). |
| `exp_read_grow_construction_induction_dop_fragments_v1.py` (DOP-style POS+deprel SHAPE fragment induction) | Disk-verified: induces variable-grain SYNTACTIC SHAPE fragments (form only, no thematic-role/meaning labels) from gold UD trees via frequency counting; MDL-flavored (`-log P(shape)` surprisal). Genuine "grow constructions from reading, no per-construction hand-authoring" precedent -- closest existing MECHANISM-PRINCIPLE analog to Gleitman bootstrapping (frequency-counted construction inventory grows via exposure). | **NO (not verbatim; useful as PRECEDENT only).** Confirms the "frequency-counted construction growth = MDL principle already validated in this codebase" pattern the frame-induction plan reuses, but operates on FORM not verb-argument SEMANTICS; no thematic-role code to import. |
| `exp_read_grow_knowledge_guided_bootstrap_v1.py` (self-bootstrapped concept-CLASS set from 0 seed) | Disk-verified: IS-A / hypernym-class induction (Hearst-pattern copula extraction), self-bootstraps a genus-noun recognizer via `>= MIN_SUPPORT` distinct co-occurring hyponyms, compounds via re-reading + interleaving multiple books. Zero verb/thematic-role content. | **NO.** Different axis entirely (noun taxonomy, not verb argument structure). Precedent value only: "0-curated-seed, compounding self-bootstrap from accumulated reading" is the right SHAPE of ambition for frame induction, but the code is IS-A-specific. |
| `hdlab/thematic_role_labeler.py` | The organ being fixed. `frame_slot_role(lemma, slot)` does `VERB_FRAMES.get(lemma, DEFAULT_FRAME)` -- OOV lemma always falls to `DEFAULT_FRAME` (`subj:AGENT`), confirmed the exact bug (cherish/loathe/crave/covet -> AGENT). `role_feats()` already computes `order`, `dist_bucket`, `arc_rule`, `animacy`, `voice`, `vxo` (voice x order) as feature atoms for its OWN (separately re-VET'd, DOWNGRADED) perceptron -- these are directly reusable as PART of the frame-induction cue-atom set. `lemma_verb()` (irregular table + suffix strip) already covers OOV-verb lemmatization; no need to import `oov_verb_extension`'s version. | **Target of the wiring edit**, and a partial feature-atom source. |
| `hdlab/predictive_coding.py` | Real, verified (bipolar residual-magnitude gate for FHRR `W` writes). Not currently wired to any lexical/discrete OOV trigger anywhere in the repo (grep found only continuous-embedding / associative-memory cells using it). | **NO -- shape-mismatched for this task** (see mislabel #2 above). Do not force it in. |
| `hdlab/self_improving_loop.py` | Real, verified (coherence-margin keep/revert ROUTER for coreference resolutions, promoted 2026-08-02). Unrelated to type-minting or frame induction. | **NO** (mislabel #1 above; wrong asset entirely for "mint engine" framing). |
| `experiments/exp_self_extension_loop_v1.py` | The actual mint engine (mints causal-role/schema TYPES like 'goal-blocker' via `predictive_coding.residual_magnitude` novelty against a seed schema library). Verified via grep (`mint_signature`, `MINT`, van Kesteren 2012 schema-incongruity citation). | **NOT DIRECTLY** (different axis: schema-type minting, not per-verb argument-role frame induction) but architecturally the RIGHT sibling to point at if/when the substrate needs a "mint a wholly novel THEMATIC ROLE label" capability (not needed for THIS fix -- AGENT/EXPERIENCER/PATIENT/RECIPIENT/GOAL/none is a closed, already-declared `ROLES` tuple; the gap is FRAME ASSIGNMENT for a known role-vocabulary, not role-vocabulary minting). |

## THE RECOMMENDATION

**EXPAND `hdlab/learner/` by writing ONE new config module (`hdlab/frame_induction.py`), zero
edits to `core.py`/`registry.py`, zero edits to `estimation_plugin.py`/`ruleind_plugin.py`/
`proginduction_plugin.py`.** This is a config-reuse EXPAND, not a plugin-registration EXPAND
(even lighter-weight than the pattern the module's own docstring advertises for "a third
hypothesis class").

Why not build-new: the learner's plugin interface (`learn(episodes, features,
hypothesis_space_spec, prior) -> LearnResult`; `apply(hypothesis, ...) -> label`) is already
domain-agnostic by construction -- `estimation_plugin` was proved to generalize to PP-attachment
(a task the source condenser cell never ran on) via the SAME generic-MDL config path this plan
proposes for frame induction. There is no structural reason frame induction is different in kind
from PP-attachment as far as the learner's contract is concerned: both are "predict a discrete
label from a discrete feature-atom set, MDL-select the hypothesis class." Forcing a bespoke
standalone learner here would duplicate the MDL-selection/glass-box/episodic-fallback machinery
this module already owns, for no shape-mismatch reason (unlike predictive_coding, which genuinely
IS shape-mismatched for this task).

## CONCRETE PLAN

### 1. Cue-atom feature encoder (`hdlab/frame_induction.py`, new file)

`episode_feats(tokens, pos, v_idx, a_idx, rule_tag, is_passive) -> list[str]` -- reuses
`thematic_role_labeler.role_feats`'s non-lemma, non-frame_slot atoms VERBATIM (`order`,
`dist_bucket`, `arc_rule`, `animacy`, `voice`, `vxo`) via direct import, PLUS 2-3 new small
glass-box detectors matching the `is_passive_clause` scope/style (~20-30 lines each, no external
parser dependency):
  - `has_sentential_complement(tokens, pos, v_idx) -> bool` (CP/that-complement licensing --
    Fisher/Gillette/Gleitman 1999 "human simulation paradigm" cue: psych/cognition verbs like
    know/believe/want/fear disproportionately license sentential complements; agentive-transitive
    verbs like kick/build rarely do).
  - `is_stative_aspect(tokens, pos, v_idx) -> bool` (resists progressive/imperative-command form --
    classic stative-vs-eventive diagnostic; Naigles 1990-style aspectual cue).
  - `is_degree_modifiable(tokens, pos, v_idx) -> bool` ("very much Xed" -- experiencer-verb
    diagnostic; agentive-manner verbs resist degree modification).

**CRITICAL: the feature atom list must NEVER include the verb lemma or any n-gram containing
it.** This is what makes the induced hypothesis transfer to an unseen verb at test time (the key
the plugin conjunction-searches over is construction shape, not lexical identity) and is the
direct fix for the 92%-feature-overlap / near-memorization failure mode the re-VET found in the
shelved perceptron.

### 2. Episode generation (bootstrap from the SUPPLIED `VERB_FRAMES` dict, applied over a reading corpus)

For every (verb, sentence) occurrence of an IN-VOCAB verb (`lemma in VERB_FRAMES`) encountered
while reading: `episode = {"feats": episode_feats(...), "gold_class": frame_slot_role(lemma,
"subj")}`. This is distant/weak supervision from the already-trusted supplied dictionary --
matches the Gleitman proposal directly: children use KNOWN verbs' syntactic-distribution
statistics to learn which construction patterns correlate with which argument-structure meanings,
then transfer the correlation to novel verbs by construction overlap, not lexical identity.

### 3. Learn + auto-select

```python
from hdlab.learner import registry
chosen_name, chosen, all_results = registry.learn(
    episodes, feat_fn,
    {"candidate_plugins": ["estimation", "ruleind", "proginduction"],
     "key_fn": lambda ep: "|".join(sorted(ep["feats"])),        # estimation
     "atoms": DECLARED_CUE_ATOMS, "max_nodes": 9,                # proginduction
     "min_coverage": 3, "purity_thresh": 0.75},                  # ruleind
    prior={},
)
```
`proginduction` is included specifically because its docstring names the EXACT failure class the
re-VET diagnosed (a lookup/linear mechanism gets an unseen atom-combination wrong when marginals
point the wrong direction) as its reason for existing -- this is not a speculative fit, it is the
plugin the codebase already built for this failure mode, previously exercised only on the
implicative-sign x negation task (banked 29492).

### 4. Wire into `thematic_role_labeler.frame_slot_role`

```python
def frame_slot_role(lemma, slot, feats=None, induced_hypothesis=None, plugin_name=None):
    frame = VERB_FRAMES.get(lemma, None)
    if frame is not None:
        return frame.get(slot, "none")
    if slot == "subj" and induced_hypothesis is not None:
        pred = registry.apply(plugin_name, induced_hypothesis, feats)
        if pred is not None:
            return pred
    return DEFAULT_FRAME.get(slot, "none")
```
Replaces the silent `DEFAULT_FRAME -> AGENT` fallback with an induced-hypothesis consult FIRST,
falling back to the current (known-bad) default only when the plugin itself abstains
(`KEEP_EPISODIC` / no rule fires / residual lookup empty) -- an honest, measurable
degrade-gracefully path, not a silent override.

### 5. Eval design: HELD-OUT NOVEL VERBS (anti-memorization, matches the re-VET's revival criteria)

**Lemma-level split**, not sentence-level (this directly fixes the 92%-feature-overlap leakage
the re-VET caught): partition `PSYCH_VERBS` and the agentive lemma pools into
`TRAIN_LEMMAS`/`TEST_LEMMAS` such that `cherish`, `loathe`, `crave`, `covet` (the re-VET's own
demo failures) are in `TEST_LEMMAS` and appear in ZERO training episodes under ANY surface form.
Generate train episodes only from `TRAIN_LEMMAS` sentences; fit per step 3. Generate held-out eval
sentences from `TEST_LEMMAS` only; predict via step 4's induced-hypothesis path using ONLY
`episode_feats` (construction cues), never the lemma.

Report per-axis (experiencer axis specifically, matching the re-VET's own slicing) against three
baselines:
  - `DEFAULT_FRAME`-always (current bug: structurally 0% on the experiencer axis)
  - `positional`-only (order cue alone, the re-VET's weakest baseline: 0.429 in-vocab / 0.000 on
    gold-EXPERIENCER-only)
  - in-vocab `frame_only` ceiling reference (0.857, NOT achievable out-of-vocab by construction --
    included only as an upper reference, not a bar this design must clear)

**HARD-PASS:** held-out-novel-verb experiencer-axis accuracy `>= 0.55` (chosen conservatively
below the in-vocab frame_only=0.857 ceiling and above the DEFAULT_FRAME/positional floors) AND
does not regress the agentive/ditransitive held-out-lemma axis below its own frame_only reference
band AND a scramble control (permute the induced rule set's `majority_class`/`out_map` values,
same discipline as `thematic_role_labeler.scramble_weights`) collapses performance (proves the
induced hypothesis is load-bearing, not decorative).

**HARD-FAIL:** held-out-novel-verb experiencer-axis accuracy `< 0.35` (no better than chance
among the 5 non-`none` role labels weighted toward AGENT) OR the scramble control does NOT
collapse performance (decorative-hypothesis red flag) OR feature-atom leakage is found (any atom
directly or indirectly encodes lemma identity).

## Cross-thread synthesis

This plan closes exactly ONE of the re-VET's two revival criteria (#2: OOV/frame-induction,
replacing the static dict). It does **NOT** address revival criterion #1 (the earned perceptron's
`order:pre -> AGENT` cue-conflict override, measured at -0.24 lift even when `frame_slot` is
already correct) -- that is a SEPARATE, still-unresolved problem in the DOWNSTREAM role-assignment
perceptron, not in frame-lookup itself. Both must be fixed before `thematic_role_labeler` can be
re-submitted for promotion; shipping only this plan and re-testing end-to-end would likely still
show the perceptron overriding a now-correctly-induced `frame_slot:EXPERIENCER` cue back to AGENT
on `order:pre` items, reproducing the re-VET's Check-4 finding. Recommend treating the
cue-conflict fix (per-verb-class cue weighting / lexical gating, per the re-VET's own revival
criterion #1) as a follow-up drill, itself possibly ALSO expressible in the same learner (a
gated/hierarchical cue-integration hypothesis class, e.g. `proginduction_plugin` again, or a
lexically-gated variant of `ruleind_plugin` keyed jointly on `frame_slot` + `order`) rather than
hand-tuning perceptron weights -- worth a follow-up audit once this frame-induction piece lands.

## Substrate-product implications

If this lands, the substrate gains a general REUSABLE pattern (not a one-off): "supplied
dictionary knowledge over a closed vocabulary generates weak-supervision episodes; the learner
induces a construction-signature hypothesis that transfers to unseen vocabulary items" is directly
re-applicable to any other closed-dict-with-OOV-fallback organ in the reading pipeline (e.g. if
`animacy_lexicon` or other supplied tables show the same "OOV falls to a bad default" shape). This
plan is a template for that class of fix, not a single-purpose patch.

## Citations (verified count: 0 external; this is a code-audit, no external lit-scan dispatched)

Internal precedent citations verified by direct file read (not external): Perfors & Tenenbaum 2009
two-part-code MDL criterion (cited in `hdlab/learner/core.py::per_cluster_gate` docstring, not
independently re-verified this pass); Muggleton & De Raedt 1994 ILP framing and Bod DOP (cited in
`proginduction_plugin.py` / `exp_read_grow_construction_induction_dop_fragments_v1.py` docstrings,
not independently re-verified this pass -- carried over from those files' own citations).
Psycholinguistic framing in this note (Gleitman 1990 structural sources of verb meaning;
Naigles 1990; Fisher/Gillette/Gleitman 1999 human simulation paradigm; MacWhinney Competition
Model, already cited in `thematic_role_labeler.py`'s own header) is domain background supplied by
this audit, not independently literature-verified this pass -- flagged as HYPOTHESIZED framing,
not CITED-verified, per the calibration discipline.

## P_deflated and biggest risk

P_deflated = **0.35** (novel-synthesis cap 0.50 applies; deflated further for: (a) the plan is
untested design, no cell has run; (b) data-sparsity risk -- `PSYCH_VERBS` is a ~40-lemma closed
class, so held-out-lemma episode counts per construction-cue bucket may be thin even before the
lemma-level train/test split, risking the SAME MDL/marginal-driven cue-conflict this plan is
trying to avoid, just one level up; (c) this plan explicitly does NOT fix the downstream
perceptron cue-conflict (revival criterion #1), so an end-to-end re-submission built on ONLY this
piece would likely still fail re-VET on the full pipeline even if frame induction itself works).

**Biggest risk:** the SAME failure class the re-VET found could recur ONE LEVEL UP. If natural
reading exposure gives few sentential-complement / degree-modifiable / stative-aspect instances
relative to the numerically-dominant `order:pre + animate-subject` pattern (which is true of BOTH
psych verbs AND ordinary agentive verbs), `estimation_plugin`'s single-key counting or even
`ruleind_plugin`'s conjunction search could still let the majority-marginal cue win by MDL
compression on a construction-signature key that happens to correlate with AGENT more often than
EXPERIENCER in the training distribution -- reproducing the "order:pre overrides frame cue"
problem inside the INDUCTION step itself rather than fixing it. `proginduction_plugin`'s
total-boolean-function-over-declared-atoms design is the strongest available defense against this
(it doesn't fall back to majority-marginal on unseen combos, per its own stated purpose), but this
has not been empirically confirmed on THIS task -- it is a design choice informed by the plugin's
documented purpose, not a measured result. Second risk: none of the new cue detectors
(`has_sentential_complement`, `is_stative_aspect`, `is_degree_modifiable`) exist yet and would need
their own small self-tests (matching `is_passive_clause`'s ~30-line, no-hard-override discipline)
before this plan can be smoke-tested.
