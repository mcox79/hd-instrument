# FORMALIZE drill: an online grounded-word-acquisition loop (build spec)

Date: 2026-08-06. Task: audit gap #1 from `notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md`
("FEATURES: supplied vs LEARNED+GROUNDED") -- design a brain-accurate, glass-box, can-fail FIRST
increment of an online loop that adds grounded context as the substrate runs into new words, per the
project's FORMALIZE discipline (map brain mechanism SHAPE+POSITION+METRIC -> per-component compare
vs OWNED organs, verified on disk -> name the precise gap -> design the increment). This is a SPEC,
not an experiment run; the companion pre-reg is `preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md`.

## HEADLINE

The substrate already owns every PRIMITIVE this loop needs (a novelty/propose gate, a syntactic-
bootstrapping construction-cue classifier, a cross-situational propose-but-verify consolidation rule,
and a genuinely reward-EARNED appraisal valuation), each independently validated on its own task. What
does NOT exist is the WIRING that points these primitives at a NEW payload: a novel WORD's own
provisional feature-tag entry, written back into a runtime-mutable overlay the production Tier-2
open-vocab classifiers already consult. Today's "open-vocab" coverage (`hdlab/verb_lexical_similarity.py`,
built earlier today) is a SIMILARITY-TO-FIXED-SEEDS classifier, not an acquisition loop: every seed
(including the drill's own "praise"/"accept"/"invite" answers) was hand-tagged by a human applying a
written rubric, in the same file, before the substrate ever saw the word. That is fast-mapping DONE BY
A HUMAN, not the substrate -- structurally the same "supplied, not earned" pattern the audit already
named for nouns, now disk-verified for verbs. The first increment closes this for the outcome-verb
POLARITY axis specifically (the one decision-relevant dimension for `OUTCOME_NEVER_TYPED`), using a
genuinely-earned affective-valence channel (`grounded_appraisal_sim_earned`'s reward-trained theta) that
the codebase already owns but has never wired to a NEW word.

## THE BRAIN MECHANISM -> OWNED ORGAN MAP

| # | Brain mechanism (SHAPE + POSITION + METRIC, cited) | Owned organ + VERIFIED code path | Gap | Verdict |
|---|---|---|---|---|
| 1 | **Fast mapping**: one exposure creates a WEAK, GRADED, PLACEHOLDER entry, not a firm binding (Carey & Bartlett 1978, *Papers & Reports on Child Lang. Dev.* 15; Carey 2011 *Lang. Learning & Development* 6(3), "Beyond Fast Mapping": partial syntactic-category + coarse-domain tag, converges only via later "extended mapping"). Computational form: Alishahi/Fazly/Stevenson (CoNLL 2008) — p(m\|w) initialized uniform, updated by a localized-contrast alignment probability per exposure; after ONE exposure mean p(correct\|word)~=0.64, not near-1. Trigger candidates: mutual exclusivity (Markman & Wachtel 1988, 6 expts N=174) or novelty/no-name bias (Golinkoff et al. 1992) — no consensus mechanism, but a consensus SHAPE (weak, revisable, immediately usable). | `hdlab/predictive_coding.py::threshold_gate` (L102-125, residual-magnitude gate, `WriteDecision(write_strength, skipped, reason)`) as the PROPOSE trigger; `experiments/exp_self_extension_loop_v1.py::mint_signature` (L221-232) as the PLACEHOLDER-entry constructor (signature = unexplained-feature residual against the current schema, arbitrary name, content = the binding). | `mint_signature`'s payload today is a set of ALREADY-KNOWN feature atoms describing a new CAUSAL-ROLE TYPE (e.g. "goal-blocker"), not a new WORD's own lexical-feature entry. The SKELETON (propose/gate/mint) is reusable verbatim; the PAYLOAD needs to change from "which known-atom combo is unexplained" to "what tag-set does this OOV word's construction license." | **REUSE the skeleton, BUILD a new payload.** |
| 2 | **Syntactic bootstrapping**: the CONSTRUCTION (argument count/position/complement type), not scene content or the word's own identity, narrows a novel verb's meaning-hypothesis space (Gleitman 1990 *Lang. Acquisition* 1:3-55; Landau & Gleitman 1985; Naigles 1990 *Cognition* 17:357-74, "gorping" preferential-looking, well-replicated; Fisher/Gertner/Scott/Yuan 2010 *WIREs Cog.Sci.* 1(2)). Yuan & Fisher 2009 (*Psych.Science* 20(5)): merely OVERHEARING a novel verb in a transitive vs intransitive frame, no scene, seeds a durable (next-day) frame-consistent partial entry -- structure ALONE is sufficient to seed a placeholder. | `hdlab/frame_induction.py::frame_primary_role` (L415-441) -- disk-verified: OOV verb -> `induce()` over `CONSTRUCTION_ATOMS = [has_scomp, degree_mod, progressive, order_pre]` (MDL/proginduction, `hdlab.learner`, config-only) -> transfers construction->AGENT/EXPERIENCER mapping to unseen verbs "by construction OVERLAP... the verb lemma is NEVER a feature" (module docstring L22-24, verified). Sibling instance: `hdlab/goal_typing.py::action_frame_feats` (L347-367) -- verb-lemma-INDEPENDENT purpose-infinitival "to VP" detector. Both are ALREADY-VALIDATED, ALREADY-WIRED syntactic-bootstrapping implementations. | Both existing instances classify along an axis ALREADY BUILT (AGENT/EXPERIENCER; GOAL/NOT_GOAL). Neither proposes a free tag-set over the `OUTCOME_VERB_FEATURES`-shape space (`EVENT_DOMAIN x RESULT_VALENCE x FORCE_DYNAMIC_PATTERN x SCALE_DIRECTION`, `hdlab/verb_lexical_similarity.py` L86-101). A construction-cue encoder pointed at THIS tag space does not exist. | **REUSE the exact `frame_induction` PATTERN (declare atoms, MDL-induce, never leak the lemma), BUILD a new atom set + target axis.** Literature caveat (own honest read, not lit-established): argument-structure/frame cues are known to predict event ARITY/TYPE, not documented to predict emotional/evaluative VALENCE specifically -- expect this leg to be WEAK for the polarity axis; that is fine, fast-mapping placeholders are supposed to be coarse (see mechanism 1), and this motivates mechanism 5 below as the decisive leg, an explicit falsifiable sub-prediction (pre-reg Section "Ablation prediction"). |
| 3 | **Cross-situational refinement, "propose-but-verify"**: a SINGLE best-guess hypothesis is proposed and RETAINED only if the next exposure of the same word confirms it, else discarded and re-proposed (Trueswell/Medina/Hafri/Gleitman 2013 *Cog.Psych.* 66(1), eye-tracking autocorrelation) -- an iterated-fast-mapping account, distinct from gradual associative accumulation (Yu & Smith 2007 *Psych.Sci.* 18(5); Fazly/Alishahi/Stevenson 2010 *Cog.Sci.* 34(6), IBM-alignment-style incremental model). Both accounts converge empirically within a small number (2-3) of confirmatory exposures (Smith & Yu 2008 *Cognition* 106(3), 12-14mo infants, robust after ~10 exposures/word aggregate but per-item confirmatory count much lower per Trueswell's analysis). Contested: no single mechanism wins outright (2023 Frontiers review, 15 years of CSWL); current consensus is a hybrid multiple-weighted-hypotheses account closer to soft propose-verify. | `experiments/exp_self_extension_loop_v1.py::run_loop` (L353-372, the CONSOLIDATE stage) -- disk-verified: candidate mint proposals are grouped by an exact `sig_key` (signature string); a candidate promotes ONLY if `n_conf = len(p["ids"]) >= MIN_CONFIRM` (=2, L74) AND clears `hdlab/self_improving_loop.py::decide_keep_or_revert`'s abstain band (`ABSTAIN_BAND_DEFAULT=0.02`, L53). This is STRUCTURALLY Trueswell's propose-but-verify: propose once (exposure 1), require the identical hypothesis to recur (exposure 2) before it is kept. | None -- this is a clean, already-implemented, already-VET'd instance of the exact brain-consistent consolidation rule. | **REUSE VERBATIM** (both `MIN_CONFIRM>=2` signature-matching AND the `decide_keep_or_revert` abstain-band gate) as the increment's consolidation stage. |
| 4 | **Bayesian taxonomic-level / size-principle inference**: strong sampling over a taxonomic hypothesis tree; likelihood `p(X\|h) = (1/\|h\|)^n`; 1 example -> broad graded generalization (prior-dominated), 3 identical examples -> sharp narrow generalization (likelihood-dominated, "suspicious coincidence") (Xu & Tenenbaum 2007 *Psych.Review* 114(2); replication caveat on presentation format, Lewis & Frank 2018 *Psych.Science*, N=600). | None found. `hdlab.learner`'s MDL/proginduction model-selection (used by both mechanism-2 instances) is a DIFFERENT Bayesian-flavored mechanism (minimum-description-length over a BOOLEAN CONSTRUCTION hypothesis space), not a taxonomic-TREE size-principle model over word EXTENSIONS/generality-level. | Real, but this specific mechanism answers a DIFFERENT question than the one blocking `OUTCOME_NEVER_TYPED` today: "how general/specific is this word's category" (is "ferry" a synonym of "vessel" or merely same-domain?) vs "is this word's polarity POS or NEG" (a flat 2-way decision `classify_2way` already handles once a candidate entry exists). | **OUT OF SCOPE for increment 1** (per [[feedback-dont-dismiss-adjacent-methods]], flagged as a real adjacent method, not dismissed -- but it answers the taxonomic-GENERALITY question, which is a separate, real follow-up for `hdlab/lexical_similarity.py`'s CONCEPT_FEATURES clustering, not for the polarity axis this increment targets). |
| 5 | **Affective grounding of abstract/evaluative concepts**: abstract and especially GOAL/SOCIAL-evaluative words (hope, praise, fail) ground disproportionately in VALENCE x AROUSAL rather than sensorimotor statistics (Kousta/Vigliocco/Vinson/Andrews/Del Campo 2011 *JEP:General* 140; Vigliocco/Meteyard/Andrews/Kousta 2009 *Lang.& Cognition* 1(2), multidimensional semantic representation theory). Developmentally, valence predicts age-of-acquisition and valenced words are learned FASTER by children under 8-9 (Ponari/Norbury/Vigliocco 2018 *Cognition*) -- directly relevant to this project's "~6yo grounded foundation" framing. Binder 2016 (*Cog.Neuropsych.* 33) supplies ~65 experiential attributes incl. explicit Emotion/Social/Cognition dimensions (Emotion rated on a 13-pt bipolar valence scale, not intensity-only). Candidate GROUNDING SIGNAL: dopaminergic reward-prediction-error, a genuine "common neural currency" for social and non-social value (Schultz/Dayan/Montague 1997 *Science* 275; Izuma/Saito/Sadato 2008 *Neuron* 58, striatal overlap of social approval and monetary reward; Levy & Glimcher 2012 *Curr.Opin.Neurobiol.* 22, vmPFC/OFC common-currency; Padoa-Schioppa & Assad 2006 *Nature* 441, OFC economic-value neurons). | `experiments/exp_grounded_appraisal_sim_earned_v1.py::Codebook/train_theta` (L106,267-283) -- a Q-value-style theta TRAINED BY REWARD on a SIMULATED appraisal task (`reward(ep, action)`, L167; actions = {pursue, withdraw, harm(c), help(c)}; episode types BLOCK_HIGH/BLOCK_LOW/RECIPROCITY/NEUTRAL with independent congruence x coping signatures, L71-76) -- genuinely EARNED, not hand-assigned, no text at any point. Consumed live in production via `hdlab/context_grounded_valence.py::score_item` (L111-169, WIRED 2026-08-05) -> `valence = _gov.valence_for_type(cb, theta, final_type) = Q(harm@coherent) - Q(help@coherent)`. | TWO gaps, one structural, one honesty-calibration: (a) STRUCTURAL -- `context_grounded_valence`'s `final_type` today is derived from a HARM/HELP PHYSICAL-FORCE + ANIMACY domain (`GOVERNOR_VERB_CLASS`, `FORCE_CLASS_HARM_REAL`), not the GOAL-ATTAINMENT domain (`REPAIR_PRESERVE`/`ARRIVE_SUCCEED`/etc.) the outcome-polarity axis needs; there is no existing wire from "does this clause complete or thwart an antecedent goal" to `final_type`. This is real, buildable, thin glue (see "New glue" below), NOT a verbatim reuse -- flagged honestly. (b) CALIBRATION -- the lit-scan found NO published study that directly tests RPE/common-currency valuation as the ACQUISITION mechanism for lexical/social-evaluative word MEANING specifically; the Izuma/Levy-Glimcher/Padoa-Schioppa findings establish common-currency VALUATION of already-identified outcomes, not word-LEARNING. Treating `grounded_appraisal_sim`'s theta as "the brain's grounding channel for a NEW WORD's valence" is THIS PROJECT'S extrapolation from adjacent literature, not a cited finding -- deflate accordingly (see P-estimate below). | **REUSE the theta/valuation MACHINERY verbatim (genuinely earned, no text, content-blind); BUILD a new, honestly-thin domain adapter (goal-attainment clause -> {BLOCK_HIGH-like, RECIPROCITY-like} appraisal-type) as the ONE genuinely-new piece of glue code the increment requires.** |
| 6 | **Complementary Learning Systems (fast hippocampal binding -> slow cortical consolidation)**, applied to word learning: rapid hippocampal familiarization of a wordform, then SLOW (sleep-dependent) cortical consolidation; the new word enters lexical competition with existing words only AFTER consolidation (McClelland/McNaughton/O'Reilly 1995 *Psych.Review* 102(3); Davis & Gaskell 2009 *Phil.Trans.R.Soc.B* 364(1536), the direct word-learning CLS synthesis; Kumaran/Hassabis/McClelland 2016 *TiCS* 20(7), CLS-for-agents). Qualifier: neocortex CAN learn rapidly when new material is SCHEMA-CONSISTENT (McClelland 2013 *JEP:General* 142(4)) -- softens strict fast/slow dichotomy for schema-fitting material. | `hdlab/self_improving_loop.py::decide_keep_or_revert` (L92-102) IS the slow/consolidation gate (mechanism 3, reused). The "fast" leg is mechanism 1's `threshold_gate`. | None structurally; but note the McClelland-2013 qualifier is DIRECTLY RELEVANT and licenses this increment's design choice: because the new word's provisional entry slots into an ALREADY-EXISTING feature-tag SCHEMA (`OUTCOME_VERB_FEATURES`'s tag vocabulary, not a wholly novel representational format), rapid (2-exposure) uptake is schema-consistent and brain-predicted to be fast, not a violation of the fast/slow dichotomy. | **REUSE (already covered by mechanism 3); cite McClelland 2013 as the justification for why a 2-exposure consolidation window is brain-appropriate here, not corner-cutting.** |

## THE PRECISE GAP (restated, disk-verified, not inferred from labels)

Confirmed by direct execution against the live `hdlab/goal_typing.py` + `hdlab/verb_lexical_similarity.py`
(read-only verification, not an experiment run):

```
caught       lemma=catch    in_verb_lexical_similarity_outcome=False  in_V2_literal=False
obtained     lemma=obtain   in_verb_lexical_similarity_outcome=False  in_V2_literal=False
gained       lemma=gain     in_verb_lexical_similarity_outcome=False  in_V2_literal=False
...
lexicon_predict("The rat stole out, and she jumped at it and caught it.") -> NONE
```

"catch"/"caught" is not a hypothetical example: it is the LIVE, currently-unresolved blocker for
`mg1_nero_puss_rat` in `experiments/data/real_text_goal_owner_diagnostic_v1.jsonl` (row 4) -- confirmed
against `preregs/2026-08-06_verb_class_openvocab_similarity_v1.md`'s own "Known limits" section, which
named this item's sentence-SPLITTER bug as its blocker at the time; that splitter bug was independently
fixed the same day (`hdlab/goal_typing.py::_SENT_SPLIT_RE`, commit d52aa7669, module docstring
"SENTENCE-SPLITTER FIX" L622-631, verified on disk) -- which means the splitter no longer masks this
item, and its REAL remaining blocker is now the bare lexical gap on "catch." "praise"/"accept"/"invite"
(the drill's headline examples) are, as of today, NO LONGER genuinely OOV -- they were hand-added to
`OUTCOME_HELDOUT_POS` (`hdlab/verb_lexical_similarity.py` L186-190) by a human applying a written rubric
this same session. That hand-add is not a criticism of today's work (it correctly, honestly, unblocks
production) -- it IS the exact, concrete, disk-verified instance of audit gap #1: a human did the
fast-mapping the substrate should be doing.

**The gap, precisely stated:** there is no code path by which the substrate, encountering a genuinely
novel outcome-verb in a real sentence, can (a) propose a candidate polarity tag from the sentence's own
construction + the substrate's OWNED reward-earned appraisal signal, (b) require independent
confirmation before trusting it, and (c) PERSIST the result so a later encounter of the same word is
typed without a human re-opening `verb_lexical_similarity.py`.

## THE TWO-CHANNEL ARCHITECTURE

Per the task's hard constraint (the loop must keep structural and affective-grounding channels
EXPLICIT and must not let the cheap channel silently substitute for the hard one):

- **CHANNEL A (structural / syntactic-bootstrapping, WEAK by design):** a `frame_induction`-style
  construction-cue encoder (new atoms: `has_direct_object`, `patient_np_present`,
  `result_particle_present` for particles in {up, down, off, away, back}, `subject_is_animate_agent`
  from `hdlab/animacy_lexicon.py`, already-wired) -> MDL-induce (reuse `hdlab.learner` exactly,
  config-only, zero new learner code, mirroring `frame_induction.py`'s own pattern) a
  construction -> {seed-POS-like, seed-NEG-like} classifier TRAINED ON THE EXISTING SEED VERBS'
  OWN CORPUS CONTEXTS (not the target word). Expected to be a WEAK leg per the syntactic-bootstrapping
  literature (argument structure predicts event arity/type, not documented to predict evaluative
  valence) -- this is a deliberate, falsifiable, pre-registered expectation, not padding.
- **CHANNEL B (affective / reward-grounded, EXPECTED DECISIVE):** derive a coarse goal-congruence
  appraisal-type for the OOV word's clause (does the clause complete or thwart the antecedent goal's
  referent trajectory -- reusing `hdlab/goal_typing.py`'s ALREADY-BUILT `SUBJECT_IS_REFERENT_CLASSES`/
  `OBJECT_IS_REFERENT_CLASSES` referent-tracking machinery, construction-typed, NOT keyed to the OOV
  verb's own identity) -> map {completes-goal, thwarts-goal} onto `context_grounded_valence`'s existing
  {RECIPROCITY, BLOCK_HIGH} appraisal types (the ONE new, honestly-thin piece of glue this increment
  needs -- see gap 5a above) -> read `valence = Q(harm@coherent) - Q(help@coherent)` from the FROZEN,
  already-reward-trained theta (`experiments/exp_grounded_appraisal_sim_earned_v1.py`, zero new
  training) -> sign(valence) is the candidate POS/NEG tag. NO TEXT co-occurrence statistics of the
  target word are read anywhere in this channel -- it is driven entirely by the clause's causal/goal
  structure plus a signal EARNED from simulated reward experience, matching the audit's "you can't
  learn revenge/praise from a book" framing precisely.
- **ANTI-DRIFT GATE:** reuses `exp_self_extension_loop_v1`'s exact consolidation rule (mechanism 3):
  require Channel A and Channel B to AGREE at each of >=2 independent corpus occurrences of the SAME
  word before writing back. If either channel alone reproduces the combined result, that is reported
  honestly (informational, not gating) -- the two-channel design is a hard constraint from the task
  brief, not assumed load-bearing without evidence.
- **WRITE-BACK:** a new runtime-mutable dict, e.g. `hdlab/verb_lexical_similarity.py::ACQUIRED_OUTCOME_VERB_FEATURES`
  (module-level, mirrors the existing `_feature_vecs_cache`/`_concept_vec_cache` module-state pattern
  already used in this file), checked by `in_lexicon`/`mean_similarity_to_seeds`/`classify_2way` as a
  genuine TIER-3 fallback, strictly AFTER Tier-1 (exact) and Tier-2 (fixed hand-tagged-seed similarity)
  -- so this can only ever ADD coverage, never regress an already-firing case (same strict-ADD
  discipline every existing Tier in this file already follows).

## HONEST SCOPE -- what the first increment does NOT solve

- Does not solve `mg2_harry_blind_man_cents` ("could not find them") -- negation-scope over a verb is
  a DIFFERENT mechanism gap (a polarity-flip operator conditioned on clause-level negation), explicitly
  named as a separate open item in the post-compaction backup's NEXT list; conflating it with word
  ACQUISITION would muddy this increment's can-fail design. Not addressed here.
- Does not solve `mg1_chippy_chicken_bread` ("This bread is for Chippy") -- a reward-ALLOCATION
  construction with no result-state verb at all (predicate PP, not a verb-classification problem);
  would need a bridging construction closer to the already-built evaluative/affect-state bridges
  (commits 17dd3567b / 0ff1a6d97), not a verb-lexicon acquisition loop.
- Does not solve `mg1_puss_kittens_attic` -- the outcome is conveyed through an unnamed third-party
  helper's action with no explicit result-state trigger word in the outcome span; out of scope for any
  verb-lexicon mechanism.
- Does not attempt the taxonomic-GENERALITY question (mechanism 4, Xu & Tenenbaum) -- only the flat
  2-way polarity axis. A word's DOMAIN/ROOT_TYPE tags (used only for CLASS_REGISTRY grouping, not
  decision-relevant to `has_unmet`/`has_met`) are NOT proposed by increment 1; only `RESULT_VALENCE`
  (POS/NEG) is targeted, because that is the one axis load-bearing for `OUTCOME_NEVER_TYPED`.
- Does not persist across process restarts (in-memory runtime dict only, scoped to one script's
  lifetime for this increment) -- cross-session persistence (e.g. a JSON-backed acquired-lexicon file)
  is a real, cheap follow-up, deliberately deferred to keep increment 1's can-fail surface small.
- Does NOT claim the RPE-grounds-lexical-acquisition hypothesis (Channel B) is literature-established
  -- per the calibration discipline, this is flagged as the project's own extrapolation from adjacent
  (valuation, not word-learning) findings; the pre-reg's ablation ("Channel B alone" arm) is designed
  to produce genuine evidence for or against this specific claim, not to assume it.
- Does not repeat the CLOSED `binder_direct_supply_grounding` direction (registry: "Binder-65 not even
  on disk," SHELVED 2026-07-28, `data/capability_registry.jsonl` id `binder_direct_supply_grounding`)
  -- that direction hand-supplied Binder's full experiential-norm vector; this increment supplies
  neither the norms nor the tags, only the CONSTRUCTION-DETECTOR DSL and the reward-simulation's reward
  function (both mechanism definitions, not per-word data), and induces/earns the rest.

## Disk-verification / housekeeping findings (report honestly, not swept)

- `hdlab/lexical_similarity.py` and `hdlab/verb_lexical_similarity.py` -- both live, production
  dependencies of the WIRED `hdlab/goal_typing.py` (imported directly, load-bearing for Tier-2) -- have
  **NO registry row of their own** in `data/capability_registry.jsonl` (68 rows checked; neither module
  path appears in any row, including `goal_typing_outcome_valence_goal_congruence`'s own `path` list,
  which lists only `hdlab/goal_typing.py` + `hdlab/coreference_resolver.py` + experiment/verification
  files). This is a real, disk-confirmed registry-completeness gap -- not blocking (the modules ARE
  reachable and ARE production-live), but a query for "lexical similarity" or "verb similarity" against
  the registry today returns 0 rows even though the capability plainly exists and is wired. Recommend a
  registry-audit follow-up adds explicit rows for both modules.
- `experiments/exp_pfc_gate_cfrpe_trained_v2.py` (the RPE/successor-representation Go-NoGo organ the
  audit cites as "reward-PE we OWN") has **no `hdlab/` module and no registry row at all** -- it is a
  validated experiment cell (HARD_PASS per its own docstring), not a promoted capability. It also solves
  a DIFFERENT problem (operator-sequence retrieval planning via SR/TD "does this candidate move toward
  goal," not per-concept valence). The organ this spec actually reuses for affective grounding is
  `grounded_appraisal_sim_earned` (registry id present, `status: promoted... 2026-08-05` equivalent via
  its consumer `context_grounded_valence`, itself registry id `context_grounded_valence`,
  `gate_decision: WIRE`) -- confirmed correctly wired on disk. The audit's citation of `pfc_gate_cfrpe`
  as THE reward-PE organ is imprecise; `grounded_appraisal_sim_earned` is the one that actually grounds
  per-concept valence and is what this spec's Channel B calls.

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

This is a novel synthesis (no published precedent combines fast-mapping + syntactic bootstrapping +
cross-situational propose-verify + RPE-earned affective grounding into one glass-box symbolic pipeline
for a hyperdimensional-computing substrate) -- **P(increment 1 clears its pre-registered HARD-PASS band
as specified) is capped at 0.50 and further deflated to ~0.40-0.45**, reflecting two independent risk
factors disk-verified above: (1) Channel A (structural) is expected weak by the literature's own logic,
so the design leans on Channel B carrying most of the signal -- if Channel B's NEW domain-adapter glue
(the one genuinely-new code in this spec) turns out unreliable, the whole increment likely lands
MIDDLE_BAND rather than HARD_PASS; (2) the RPE-grounds-lexical-acquisition hypothesis itself is this
project's extrapolation, not a cited finding -- a clean negative here (Channel B does not beat Channel
A, or neither beats fall-through) would be a genuinely informative falsification of that hypothesis,
not merely an implementation miss. HARD-FAIL thresholds are pre-registered explicitly in the companion
pre-reg (not left implicit).

## Citations (lit-scan, 3 parallel Sonnet sub-agents, verified count = 3 scans / ~45 distinct
citations; calibration penalty applied per [[feedback-lit-scan-calibration-penalty]])

Fast mapping: Carey & Bartlett 1978; Carey 2011; Markson & Bloom 1997 *Nature* 385; Horst & Samuelson
2008 *Infancy* 13(2); Vlach & Sandhofer 2012 *Frontiers in Psychology* 3:46; Markman & Wachtel 1988
*Cog.Psych.* 20; Alishahi/Fazly/Stevenson CoNLL 2008.
Syntactic bootstrapping: Gleitman 1990; Landau & Gleitman 1985; Naigles 1990 *Cognition* 17; Fisher/
Gertner/Scott/Yuan 2010 *WIREs Cog.Sci.* 1(2); Siskind 1996 *Cognition* 61; Yuan & Fisher 2009
*Psych.Science* 20(5).
Bayesian/cross-situational: Xu & Tenenbaum 2007 *Psych.Review* 114(2); Tenenbaum & Griffiths 2001
*BBS* 24(4); Lewis & Frank 2018 *Psych.Science*; Yu & Smith 2007 *Psych.Science* 18(5); Smith & Yu 2008
*Cognition* 106(3); Fazly/Alishahi/Stevenson 2010 *Cog.Sci.* 34(6); Trueswell/Medina/Hafri/Gleitman 2013
*Cog.Psych.* 66(1); Frank/Goodman/Tenenbaum 2009 *Psych.Science* 20(5); McClelland/McNaughton/O'Reilly
1995 *Psych.Review* 102(3); Davis & Gaskell 2009 *Phil.Trans.R.Soc.B* 364(1536); Kumaran/Hassabis/
McClelland 2016 *TiCS* 20(7); McClelland 2013 *JEP:General* 142(4).
Affective grounding: Kousta/Vigliocco/Vinson/Andrews/Del Campo 2011 *JEP:General* 140; Vigliocco/
Meteyard/Andrews/Kousta 2009 *Lang.& Cognition* 1(2); Ponari/Norbury/Vigliocco 2018 *Cognition*; Ponari
et al. 2025 *Psychonomic Bulletin & Review*; Binder 2016 *Cog.Neuropsych.* 33; Schultz/Dayan/Montague
1997 *Science* 275; Izuma/Saito/Sadato 2008 *Neuron* 58; Ruff & Fehr 2014 *Nat.Rev.Neurosci.* 15; Levy &
Glimcher 2012 *Curr.Opin.Neurobiol.* 22; Padoa-Schioppa & Assad 2006 *Nature* 441; Moerland et al. 2017
*Machine Learning* 107 (arXiv:1705.05172); Scherer 2009 *Cognition & Emotion* 23(7); Niedenthal et al.
2005/2009.

Cross-thread synthesis: extends `notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md` gap #1;
uses the same organs the "inferential layer" arc validated end-to-end (`d157941c6`) and the same-day
Tier-2 open-vocab work (`preregs/2026-08-06_verb_class_openvocab_similarity_v1.md`) as its immediate
predecessor and its measured fall-through baseline.

## Substrate-product implications

A working increment would mean the substrate's open-vocabulary coverage on new prose STOPS being
gated by how many hours a human spends adding words to `verb_lexical_similarity.py` -- it becomes a
property of how much text the substrate has read, with an honest confidence/provenance trail (a Tier-3
entry always carries which two occurrences confirmed it and both channels' individual verdicts,
inspectable, not a black-box embedding). This is the generalization-critical-path item the task brief
named: real-prose coverage today is bounded by hand-curated seed lists; this closes that bound for one
axis as a proof of the pattern, reusable for the same axis in other domains (GOAL_VERB_FEATURES,
CONCEPT_FEATURES) once validated.
