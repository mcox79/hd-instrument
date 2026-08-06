# FORMALIZE-BEFORE-BUILDING drill: open-vocab VERB-CLASS membership via ATL-style shared-feature similarity

**Filed by:** research (Sonnet), 2026-08-06. Triggered by the GENERALIZATION PROBE negative
(commit f496caa51, `exp_real_text_goal_owner_generalization_diagnostic_v1`, disk-VET'd): the wired
goal-owner/outcome-valence organs score owner-acc 0.30 on real McGuffey prose vs 0.70 recency
baseline, with 6/10 items `OUTCOME_NEVER_TYPED` because CLOSED-SET hand-typed verb lexicons
(`V2_OUTCOME_MET`/`_UNMET`, `CLASS_REGISTRY`, `DESIDERATIVE_PASS`, all in `hdlab/goal_typing.py`)
are out-of-vocabulary for real prose ("praise"/"accept" never fire). This note answers the design
question the fix depends on: what feature basis represents VERBS so `concept_similarity()` —
the already-proven, already-wired ATL-hub-style shared-feature organ in
`hdlab/lexical_similarity.py` — can classify novel verbs into these classes by graded similarity
to seed exemplars, instead of exact-lookup.

Per lit-scan calibration discipline ([[feedback-lit-scan-calibration-penalty]]): this is
novel-synthesis (an untested combination applied to a new problem), so P estimates below are
deflated 0.15-0.25 and novel-synthesis P is capped at 0.50, even where the underlying literature
support is strong.

---

## HEADLINE

**The mechanism-reuse is right and a real pilot (measured, not theorized) proves the construction
works on toy data with clean margins and a genuine scramble-collapse: 8/8 open-vocab outcome-verb
polarity calls correct (0.85 true-class similarity vs 0.24 opposed-class, delta 0.61) and 6/6
open-vocab goal-vs-aspectual calls correct (1.00 vs 0.00, delta 1.00), both far above the existing
`SIMILARITY_LINK_THRESHOLD=0.50` convention, with the SAME accuracy collapsing toward chance under
a global feature-tag scramble (mean 0.425 over 5 scramble seeds for outcome verbs, near-total
collapse for goal/aspect).** The open question this doesn't yet answer: whether this closes the
REAL generalization gap on REAL prose at scale — that requires an actual pre-reg'd experiment cell
with corpus-drawn held-out verbs, not a hand-picked pilot. **P_deflated=0.45** (capped near 0.50
per novel-synthesis rule) that this specific design closes a meaningful fraction of the 0.30-vs-0.70
gap; **P~0.80** (less deflation — this part is measured, not synthesized) that the
FHRR-bundle-cosine-over-hand-tagged-features CONSTRUCTION itself is sound for verb classes given a
linguistically-motivated tag scheme.

---

## 1. Brain/linguistic verb-feature basis (SHAPE)

Four parallel Sonnet lit-scans (generic academic terms only, no substrate-specific framing
off-platform). Findings below are the scans' own confidence ratings (LOW/MED/HIGH), already
lit-scan in nature — the calibration penalty is applied on top when these numbers get used for the
overall P estimate.

### 1a. OUTCOME verbs (result-state achieve-vs-block polarity)

| Framework | Dimension(s) offered | Discrete/scalar | Confidence for polarity tag | Citation |
|---|---|---|---|---|
| Levin (1993) diathesis alternations | Class = cluster of alternation participation (causative/inchoative, conative, dative, ...) | Discrete/categorical | **MED, with a caution**: her own Calibratable-Change-of-State class (45.6: increase/decrease, rise/fall, climb/plummet) groups directionally-OPPOSITE verbs together because the diagnostic is syntactic (shared measure-phrase behavior), not semantic polarity — Levin's taxonomy alone does not cleanly separate polarity, it must be supplemented | Levin, B. (1993). *English Verb Classes and Alternations*. U. Chicago Press. |
| Beavers scalar/affectedness semantics | [±scalar], scale cardinality (two-point vs multi-point), boundedness (open/closed), directedness | Hybrid (categorical typology over a graded scale) | **HIGH** for a binary "bounded result achieved / not achieved" feature; **LOW-MED** for positive/negative valence specifically — his scale ontology is polarity-neutral (a size or temperature scale carries no inherent sign); valence must be imported externally | Beavers, J. (2008) "Scalar complexity and the structure of events," in *Event Structures in Linguistic Form and Interpretation*; Beavers (2011) "On affectedness," *NLLT* 29(2); Hay, Kennedy & Levin (1999) SALT 9. |
| Talmy (1988) force dynamics | Agonist/Antagonist, tendency toward/away from rest, causing/letting/**blocking**/**helping**, extended vs onset causation | Discrete (~8-10 canonical patterns) | **MED-HIGH** (deflated from HIGH per calibration) — blocking-vs-helping/causing IS the semantic core of whether a tendency is realized or thwarted; near-direct source for an achieve/block tag | Talmy, L. (1988). "Force Dynamics in Language and Cognition." *Cognitive Science* 12(1). |
| Vendler (1957) / Dowty (1979) aspect | State/activity/accomplishment/achievement; CAUSE, BECOME, DO decompositional operators | Discrete compositional algebra | **MED** for achieved-vs-not: BECOME-culminated vs interrupted-before-culmination is native, but this is CULMINATION not VALENCE — "became open" and "became stuck" are structurally identical BECOME-events. **HIGH** for telic/atelic (native dimension). Don't conflate culmination with polarity. | Vendler, Z. (1957) "Verbs and Times," *Phil. Review* 66(2); Dowty, D. (1979) *Word Meaning and Montague Grammar*. |
| **Jackendoff's Action Tier** (1983/1987, folded into *Semantic Structures* 1990) | `AFF(Actor, Patient)` with an **explicit +/- polarity marking whether the action is beneficial or adverse to the Patient** | Discrete binary, purpose-built | **MED-HIGH** — this is a native, purpose-built valence primitive, the single best direct hit in the scan | Jackendoff, R. (1990) *Semantic Structures*, MIT Press; Jackendoff (1987) "The Status of Thematic Relations," *Linguistic Inquiry* 18(3). |
| Manner/Result Complementarity | RESULT-ROOT vs MANNER-ROOT verb typing (e.g. "break"/"clean" = result-root; "wipe"/"scrub" = manner-root) | Discrete binary | **Directly usable** as a verb-superclass tag (constant across our result-verb classes, distinguishes them from manner verbs, not itself a polarity discriminator) | Rappaport Hovav & Levin (1998) "Building Verb Meanings"; Rappaport Hovav & Levin (2010) "Reflections on Manner/Result Complementarity"; Ramchand, G. (2008) *Verb Meaning and the Lexicon: A First Phase Syntax* (note: this is the actual "First Phase Syntax" author — the task brief's attribution to Rappaport Hovav & Levin was a mix-up, corrected here). |
| McRae-style verb feature NORMS | Vinson & Vigliocco (2008) ran a McRae-style property-listing-norm study on 216 event VERBS (plus 71 event nouns) | Graded production-frequency, coded into categorical bins | **LOW** on surfacing a labeled result-polarity dimension specifically (could not confirm the exact category taxonomy from accessible sources — paywalled; flagged as a genuine gap, not a confirmed absence) — but **confirms a verb-analog of McRae's methodology already exists in the literature**, which is reassuring precedent for "hand-authoring verb features is a legitimate SUPPLY move," same as this substrate already does for nouns | Vinson, D.P. & Vigliocco, G. (2008). "Semantic feature production norms for a large set of objects and events." *Behavior Research Methods* 40(1); Vigliocco, Vinson, Lewis & Garrett (2004) *Cognitive Psychology* 48(4) (verb meaning leans on relational/motion features over visual-perceptual, vs nouns). |

**Recommended composite basis for OUTCOME verbs**: `EVENT_DOMAIN` (Levin-style coarse class,
shared within an opposed pair) x `RESULT_VALENCE` (Jackendoff Action-Tier AFF polarity — the
primary discriminator) x `FORCE_DYNAMIC_PATTERN` (Talmy blocking vs helping/causing — a second,
independent grounding of the SAME polarity, not redundant since it's derived from a different
diagnostic) x `SCALE_DIRECTION` (Beavers — which way the affected property moves along its
defining scale) x `ROOT_TYPE` (constant `RESULT_ROOT`, a verb-superclass marker).

### 1b. GOAL verbs (desiderative/intention vs aspectual/implicative)

| Framework | Dimension(s) offered | Discrete/scalar | Confidence | Citation |
|---|---|---|---|---|
| Karttunen (1971) implicative typology | `[±implicative-entailment]`: does the matrix verb entail (or negatively entail, reversing under negation) its complement's truth? Non-implicatives (want, believe, hope) entail neither. | Discrete binary | **MED** as ONE necessary discriminator — cleanly separates want-class from manage/fail-class, but under-differentiates want from try/believe/order (needs a second feature); also note the codebase's own `ASPECTUAL_STOP` set mixes true phase verbs (begin/continue, Freed 1979) with implicative verbs (manage/fail) that are technically a different Karttunen category — both are non-goal-signaling for this task's purposes, so one shared tag-set is an acceptable simplification, flagged not hidden. | Karttunen, L. (1971). "Implicative Verbs." *Language* 47(2). |
| Boulomaic/bouletic modality | Modal flavor (bouletic ordering source over a modal base, Kratzer-style); Harner & Khemlani (2020) model "want" via simulation over hypothetical/unrealized alternatives | Discrete modal-force category | **MED-HIGH** — gives a categorical `MODAL_FORCE=bouletic` + `IRREALIS complement` feature pair | Heim, I. (1992) "Presupposition Projection and the Semantics of Attitude Verbs"; Harner & Khemlani (2020) "A Theory of Bouletic Reasoning," CogSci. |
| Wierzbicka NSM | WANT is one of ~65 universal indefinable semantic primes; hope/wish/intend/plan are explicated COMPOSITIONALLY as WANT + THINK/KNOW + temporal/commitment structure | Discrete compositional | **MED-HIGH** — NSM explications for exactly this verb family already exist in the literature, supporting a small generalizable feature set | Goddard & Wierzbicka (2014); Wierzbicka (1972/1980). |
| Neural: mentalizing/ToM network | mPFC + TPJ + precuneus engaged for desire/belief/intention inference; Lin, Bi, Zhao et al. (2015) found the ToM network MORE active for social-action verbs than private-action/nonhuman verbs | HIGH confidence on the general ToM finding; **MED** on direct extension to want/hope/intend specifically (the closest study tested social-action verbs, not this exact verb set) | Lin, N., Bi, Y., Zhao, Y. et al. (2015). "The Theory-of-Mind Network in Support of Action Verb Comprehension." *Brain and Language*. |

**Recommended composite basis for GOAL verbs**: `VERB_SUPERCLASS` (`DESIDERATIVE_DOM` vs
`ASPECTUAL_DOM` — NOT shared; these are not polar opposites within one domain the way
REPAIR/DAMAGE are, they are simply different classes) x `COMPLEMENT_ENTAILMENT` (Karttunen:
non-implicative vs phase/implicative) x `MODAL_FORCE` (bouletic vs none) x `COMPLEMENT_REALIS`
(unrealized/future-directed vs ongoing/realis).

### 1c. Critical honest finding: OUTCOME and GOAL verbs likely need TWO SEPARATE feature bases, not one unified scheme

This is the single most important calibration finding, from lit-scan D (neural) crossed with
lit-scan C (desiderative semantics):

- **The ATL amodal-hub story does NOT cleanly extend to verbs the way it's established for
  concrete nouns.** A 2025 fMRI study (Muraki, Pexman & Binney, *Human Brain Mapping*, also
  bioRxiv 2024) found vATL engages for concrete and MOST abstract verb types but **NOT for
  mental-state verbs** specifically. Peelen, Romagno & Caramazza (2012, *J Cogn Neurosci*) found
  verb-selective temporal-cortex activity statistically INDEPENDENT of action/motor
  representations. Kemmerer et al. (2008, *Brain and Language*) found verb meaning fractionates
  into five dissociable componential systems (ACTION-motor, MOTION-posterolateral temporal,
  CONTACT-parietal, CHANGE-OF-STATE-ventral temporal, TOOL-USE-distributed) rather than converging
  on one hub. **No direct verb-pair graded-similarity-in-ATL study (the verb analog of the
  Cox/Rogers/Shimotake et al. 2024 noun ECoG finding this substrate's `lexical_similarity.py`
  docstring cites) was found in the literature — this is a genuine gap, not a confirmed result
  either way.**
- Meanwhile, desire/intention/goal verbs specifically look like they recruit the **mentalizing/ToM
  network** (mPFC/TPJ), not the ATL semantic hub or the posterior-temporal action-semantics
  network that handles physical-action/result verbs.

**Design implication (honest, not overclaimed):** what this substrate should reuse from
`hdlab/lexical_similarity.py` is the **glass-box shared-feature-cosine COMPUTATION** (FHRR
`bundle()` over hand-tagged feature-index vectors — a domain-general similarity mechanism, not
literally "the ATL"), not a literal claim that verb meaning lives in the ATL the same way noun
meaning does. The RIGHT framing, consistent with [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]],
is: reuse the ALREADY-BUILT computational primitive (proven, wired, glass-box) for a mechanism
that the brain plausibly instantiates via a DIFFERENT (or partially-overlapping) network for verbs
— componential posterior-temporal/motor features for physical-result verbs, ToM-network
mental-state features for desiderative verbs — **hence TWO separate feature-tag vocabularies
(`OUTCOME_CLASS_FEATURES` and `GOAL_CLASS_FEATURES`), not one shared `CONCEPT_FEATURES`-style dict
mixing verbs and nouns.** This is a REFINEMENT of the GENERALIZATION PROBE's own framing ("closed
`lemma in members` vs the ATL hub's open-vocab graded shared-feature similarity") — the MECHANISM
generalizes, the specific "it's literally the ATL" claim should be softened to "it's the same
domain-general similarity computation the ATL happens to implement for nouns; for verbs the
feature content should be grounded in the componential/mentalizing literature above, not assumed
to be ATL-amodal."

---

## 2. Feature-lexicon design (concrete, SUPPLY, uniform convention)

Follows the SAME convention `hdlab/lexical_similarity.py`'s `CONCEPT_FEATURES` already uses:
a DOMAIN tag shared within a cluster, defining tags that discriminate. Seed exemplars = the
CURRENT literal members already in `CLASS_REGISTRY` / `DESIDERATIVE_PASS` / `ASPECTUAL_STOP`
(zero new authoring risk for the seeds — they're already-vetted class-defining words).

### 2a. OUTCOME-verb classes (all 12 `CLASS_REGISTRY` classes, grouped by the 6 existing `OPPOSED_PAIRS`)

| Class | Existing seed members | `EVENT_DOMAIN` | `RESULT_VALENCE` | `FORCE_DYNAMIC_PATTERN` | `SCALE_DIRECTION` | `ROOT_TYPE` |
|---|---|---|---|---|---|---|
| REPAIR_PRESERVE | mend, fix, repair, save, rescue, protect, build, restore | STRUCT_INTEGRITY_DOM | POS_AFFECT | AGONIST_REALIZED | SCALE_UP | RESULT_ROOT |
| DAMAGE_LOSE | sink, break, fall, collapse, lose, fail, destroy, damage, wreck, crash, drown, flood | STRUCT_INTEGRITY_DOM | NEG_AFFECT | AGONIST_BLOCKED | SCALE_DOWN | RESULT_ROOT |
| ARRIVE_SUCCEED | reach, escape, arrive, win, succeed | GOAL_ATTAIN_DOM | POS_AFFECT | AGONIST_REALIZED | SCALE_UP | RESULT_ROOT |
| FAIL_LOSE | lose, fail, miss | GOAL_ATTAIN_DOM | NEG_AFFECT | AGONIST_BLOCKED | SCALE_DOWN | RESULT_ROOT |
| OPEN_CLASS | open, unlock, unseal, unbar, unbolt | APERTURE_DOM | POS_AFFECT* | AGONIST_REALIZED | SCALE_UP | RESULT_ROOT |
| CLOSE_CLASS | shut, lock, seal, bar, bolt | APERTURE_DOM | NEG_AFFECT* | AGONIST_BLOCKED | SCALE_DOWN | RESULT_ROOT |
| FILL_CLASS | fill, load, stock | CONTAINMENT_DOM | POS_AFFECT* | AGONIST_REALIZED | SCALE_UP | RESULT_ROOT |
| EMPTY_CLASS | empty, drain, unload | CONTAINMENT_DOM | NEG_AFFECT* | AGONIST_BLOCKED | SCALE_DOWN | RESULT_ROOT |
| GATHER_CLASS | gather, collect | AGGREGATION_DOM | POS_AFFECT* | AGONIST_REALIZED | SCALE_UP | RESULT_ROOT |
| SCATTER_CLASS | scatter | AGGREGATION_DOM | NEG_AFFECT* | AGONIST_BLOCKED | SCALE_DOWN | RESULT_ROOT |
| HEAL_CLASS | heal | BODILY_COND_DOM | POS_AFFECT | AGONIST_REALIZED | SCALE_UP | RESULT_ROOT |
| HARM_CLASS | worsen, fester | BODILY_COND_DOM | NEG_AFFECT | AGONIST_BLOCKED | SCALE_DOWN | RESULT_ROOT |

`*` = honest caveat: for OPEN/CLOSE, FILL/EMPTY, GATHER/SCATTER, `POS_AFFECT`/`NEG_AFFECT` is used
as a **pole-A/pole-B discriminating label**, not a literal moral-valence claim (opening a door
isn't objectively "good") — `concept_similarity` only needs internal consistency of the tag value
per pole to discriminate the two classes, not a philosophically defensible goodness judgment.
Flagged, not hidden, per the honesty discipline.

Within a class every member gets the IDENTICAL tag set (same convention as the noun lexicon's
happy/glad/joyful triple) — maximizes within-class cosine. Across an opposed pair, only
`EVENT_DOMAIN` + `ROOT_TYPE` are shared (2 of 5 tags); the other 3 differ — this mirrors the
existing dock/sailor "domain-tag-only" related-not-synonym pattern that already measures ~0.28-0.40
cosine in the production module, safely below the 0.50 threshold.

### 2b. GOAL-verb classes

| Class | Existing seed members | `VERB_SUPERCLASS` | `COMPLEMENT_ENTAILMENT` | `MODAL_FORCE` | `COMPLEMENT_REALIS` |
|---|---|---|---|---|---|
| DESIDERATIVE (`DESIDERATIVE_PASS`) | want, hope, wish, mean, plan, intend, aim, long, yearn, desire | DESIDERATIVE_DOM | NON_IMPLICATIVE_COMPLEMENT | BOULETIC_FORCE | UNREALIZED_FUTURE_DIRECTED |
| ASPECTUAL/IMPLICATIVE (`ASPECTUAL_STOP`) | begin, start, try, fail, manage, cease, stop, continue, happen | ASPECTUAL_DOM | PHASE_COMPLEMENT | ASPECTUAL_FORCE | ONGOING_REALIS |

`VERB_SUPERCLASS` is NOT shared across the two classes (unlike the outcome-verb opposed pairs) —
desiderative and aspectual verbs are not polar opposites of one shared domain, they are simply
different verb classes; a fully-disjoint tag set is the linguistically honest choice here, and
(per the pilot below) it produces the cleanest possible separation.

`OTHER_STOP_UNCHANGED` (decide/need/seem/get/choose) is explicitly OUT OF SCOPE for this drill,
matching the module's own documented scope ("conservatively left NON-goal-signaling pending their
own dedicated cell") — not addressed here.

---

## 3. Non-circular open-vocab eval — MEASURED (pilot, not theorized)

Ran the actual production mechanism (`hdlab.bundling.bundle` + `hdlab.situation_model_accumulate.
unit_phase_vec`, byte-identical `N_DIM=8192, SEED=7` convention to `hdlab/lexical_similarity.py`)
against the tag scheme above, as a scratch pilot script (not touching production code):
`C:\Users\marsh\AppData\Local\Temp\claude\d--AI\02e8b04e-1164-42ee-b96d-ac16726a826a\scratchpad\verb_class_pilot.py`
(reproducible; exp_dev should port the validated design into a real `experiments/*.py` pre-reg'd
cell rather than reuse the scratch copy).

**Design**: SEED = the existing lexicon's literal members (tags assigned BY the class definition).
HELD-OUT = words NEVER in any seed set, tagged by applying the WRITTEN rubric above to each word's
actual meaning (not copied from a seed) — this is what makes it non-circular: the classification
outcome falls out of independently-applied linguistic criteria, not from being told the answer.
Held-out set deliberately includes "praise" and "accept" — the exact two verbs disk-verified as
`OUTCOME_NEVER_TYPED` blockers in the real generalization-probe failure.

**Result (measured)**:

| Test | Held-out items | True-class mean sim | Opposed-class mean sim | Margin | Accuracy |
|---|---|---|---|---|---|
| OUTCOME polarity | praise, accept, triumph, restore (POS) / perish, founder, capsize, vanish (NEG) | 0.8468 / 0.8416 | 0.2413-0.2443 / 0.2422-0.2434 | ~0.60 | **8/8** |
| GOAL vs ASPECT | crave, aspire, resolve (GOAL) / commence, resume, persist (ASPECT) | 1.0000 | 0.0022 | ~1.00 | **6/6** |

Both margins clear the existing `SIMILARITY_LINK_THRESHOLD=0.50` convention by a wide, non-marginal
distance on both sides (matching the production module's own vessel/ferry=0.634-vs-sister/rival=
0.398 separation pattern).

**Scramble control** (global permutation of word-to-tagset assignment across the full combined
pool — same convention as the production `self_test`'s `SCRAMBLED_FEATURES` arm — then re-run the
SAME classification test on the scrambled assignment):

| Pool | Real (unscrambled) accuracy | Scrambled accuracy (1 seed) | Scrambled accuracy (mean of 5 seeds) |
|---|---|---|---|
| OUTCOME polarity (20-word pool) | 1.000 | 0.750 | **0.425** (range 0.25-0.75, n=8 so high per-draw variance is expected) |
| GOAL vs ASPECT (12-word pool) | 1.000 | 0.000 | (single draw; even more dramatic collapse) |

The mean-of-5 scrambled accuracy (0.425) sits close to the 0.50 chance line while every real,
unscrambled configuration stays pinned at 1.000 — the classification signal depends on genuine
correspondence between a word's assigned tags and its true class, not on an artifact of the
encoder or the classification rule. **Caveat, stated plainly**: n=8 for the outcome pool is small,
so any single scrambled draw can land anywhere in [0.25, 0.75] by chance alone (binomial noise at
this sample size) — the informative statistic is the mean tracking chance across draws while real
stays saturated, not any individual scrambled draw. **This is a pilot proving the construction
works, not a certified experiment** — it has NOT been run at production N, has NOT used
corpus-drawn (vs. hand-picked) held-out verbs, and has NOT been pre-registered. See Section 6 for
the actual cell spec exp_dev should run.

**Trivial-shortcut check**: none of the held-out words share a substring/orthographic root with
their seed exemplars ("praise" vs "reach/succeed/win"; "crave" vs "want/hope/wish") — ruling out a
hidden string-similarity shortcut explaining the result.

---

## 4. Integration point in `hdlab/goal_typing.py`

Three closed-set lookups are candidates; the task brief's primary ask is `CLASS_REGISTRY`, shown
in full; the same pattern applies to `V2_OUTCOME_MET`/`_UNMET` (a flat 2-way version of the same
idea) and to extending `DESIDERATIVE_PASS`/`ASPECTUAL_STOP` membership for `action_frame_feats`'s
control-verb check.

**Today** (`hdlab/goal_typing.py:425-426`):
```python
def _verb_classes(lemma: str) -> set:
    return {name for name, members in CLASS_REGISTRY.items() if lemma in members}
```

**Proposed Tier-2 extension** (exact same shape as the already-shipped Tier-2 upgrade to
`_referent_links` in this same file — threshold-gated, abstain-to-existing-behavior fallback,
strict ADD, zero regression on every lemma already covered):

```python
def _verb_classes(lemma: str) -> set:
    literal = {name for name, members in CLASS_REGISTRY.items() if lemma in members}
    if literal:
        return literal          # Tier-1 unchanged: exact membership always wins, zero regression
    return _verb_classes_similarity(lemma)   # Tier-2 (NEW): open-vocab fallback, OOV-of-Tier-1 only


def _verb_classes_similarity(lemma: str) -> set:
    """Tier-2: argmax over CLASS_REGISTRY seed-exemplar-mean shared-feature similarity
    (hdlab.verb_lexical_similarity, the verb-feature-tagged sibling of hdlab.lexical_similarity's
    ATL-hub-style organ), thresholded + margin-gated. Returns {} (abstain) if lemma is OOV of the
    verb-feature lexicon, or if the best class doesn't clear the floor, or if the top-2 classes are
    too close to call -- {} is IDENTICAL to today's OOV behavior, so this can never regress a
    caller that currently gets no class."""
    if not verb_lexicon.in_lexicon(lemma):
        return set()
    sims = {cls: verb_lexicon.mean_similarity_to_seeds(lemma, seeds)
            for cls, seeds in VERB_CLASS_SEEDS.items()}
    ranked = sorted(sims.items(), key=lambda kv: -kv[1])
    best_cls, best_sim = ranked[0]
    second_sim = ranked[1][1] if len(ranked) > 1 else -1.0
    if best_sim >= VERB_CLASS_SIM_FLOOR and (best_sim - second_sim) >= VERB_CLASS_MARGIN:
        return {best_cls}
    return set()   # abstain -- ambiguous or below floor, never forces a guess
```

`VERB_CLASS_SEEDS` = `{class_name: frozenset(existing CLASS_REGISTRY[class_name] members)}` —
literally the CURRENT lexicon, reused as seeds (zero new authoring for seeds, only the held-out
NEW verbs need tags, and only once a real held-out list is corpus-drawn per Section 6).

Proposed thresholds (PROPOSED, not fit to this pilot's numbers — pending the real pre-reg'd cell):
`VERB_CLASS_SIM_FLOOR = 0.35` (deflated below the noun lexicon's 0.50 `SIMILARITY_LINK_THRESHOLD`
since this is multi-way class-argmax, not pairwise synonymy) and `VERB_CLASS_MARGIN = 0.15`
(top-class must beat the runner-up by a real margin, not just nose ahead — guards the "both classes
are plausible" case, e.g. a verb that's genuinely ambiguous between FAIL_LOSE and DAMAGE_LOSE).

Same shape applies to `type_sentence_events_c3`'s `V2_OUTCOME_MET`/`_UNMET` check (2-way
POS_AFFECT/NEG_AFFECT argmax instead of 12-way) and to `action_frame_feats`'s
`preceding in PARTITIONED_STOP` check (test `preceding` against `DESIDERATIVE_DOM` vs
`ASPECTUAL_DOM` seeds when `preceding` is OOV of both `DESIDERATIVE_PASS` and `PARTITIONED_STOP`
literally).

**Module placement recommendation**: a NEW sibling module `hdlab/verb_lexical_similarity.py`
(imports `bundle`/`unit_phase_vec` directly, same as `lexical_similarity.py` does — not a live
import between the two, same "hdlab-only dependency, clean copy not reimplementation" convention
already documented in `lexical_similarity.py`'s own docstring), keeping verb-feature-tag vocabulary
in a separate namespace from noun-feature-tag vocabulary (avoids any future collision risk, e.g.
"praise" as a noun meaning vs "praise" as a verb meaning wanting different tags). This is
exp_dev's implementation call, not fixed here — the lighter-weight alternative (parameterize
`lexical_similarity.py`'s existing functions with an optional `lexicon:` argument, default =
current `CONCEPT_FEATURES`, zero behavior change for every existing caller) is also viable and
should be weighed on implementation cost, not re-decided by research.

---

## 5. Cheap decisive test + falsifiable predictions

**Cheap decisive test** (for exp_dev, ~2-3 hrs): port the pilot design into a pre-reg'd
`experiments/exp_verb_class_openvocab_similarity_v1.py` cell. SEED = current `CLASS_REGISTRY` +
`DESIDERATIVE_PASS`/`ASPECTUAL_STOP` literal members (tags per Section 2). HELD-OUT = (a) the
verbs that actually blocked the real generalization probe ("praise", "accept" — pull the full list
by re-scanning the 10-item McGuffey bank from `exp_real_text_goal_owner_generalization_diagnostic_v1`
for every OOV-of-lexicon result/goal verb, not just these two) PLUS (b) >=15 additional verbs per
class corpus-drawn from a McGuffey/real-prose scan (not hand-picked by the cell's author, to avoid
experimenter-selection bias) tagged via the written rubric BEFORE seeing classification output.
Run the SAME scramble control at this N.

**HARD-PASS**: held-out open-vocab classification accuracy >=80% (both outcome-polarity and
goal-vs-aspectual pools) AND scrambled-control accuracy falls within +/-15% of chance (50% for
2-way, chance-adjusted for 12-way argmax) AND the two probe-blocking verbs ("praise", "accept")
specifically get typed correctly AND re-running the full generalization-probe bank end-to-end
(owner-selection + outcome-valence) shows owner-acc improve materially toward (not necessarily
matching) the 0.70 recency baseline, with `OUTCOME_NEVER_TYPED` count dropping from 6/10.

**HARD-FAIL**: held-out accuracy <60% on either pool, OR scrambled control does NOT collapse
(stays >70%, i.e., the classification depended on some artifact unrelated to genuine tag
correspondence), OR "praise"/"accept" still fail to type, OR the end-to-end owner-acc shows no
material movement despite `OUTCOME_NEVER_TYPED` dropping (would mean the bottleneck was never
really lexicon-coverage as diagnosed, forcing a re-open of the GENERALIZATION PROBE's own
diagnosis).

**MIDDLE-BAND** (a real possible outcome, not to be strategy-hidden): held-out accuracy 60-80% or
partial scramble-collapse — would mean the mechanism-reuse direction is right but the SPECIFIC
tag-dimension choices in Section 2 need iteration (e.g. `SCALE_DIRECTION` may be under- or
over-weighted relative to `RESULT_VALENCE`), not that the approach is wrong.

---

## 6. Cross-thread synthesis

- Directly answers the design question opened by the GENERALIZATION PROBE (commit f496caa51,
  disk-VET'd 2026-08-06): "closed `lemma in members` vs the ATL hub's open-vocab graded
  shared-feature similarity" — Section 1c refines that framing (the COMPUTATION generalizes, the
  literal "it's the ATL" claim should not be overclaimed for verbs specifically).
- Reuses, does not reimplement, the WIRE-DONT-ISLAND promotion of `hdlab/lexical_similarity.py`
  (2026-08-06, same session) — that module's `concept_similarity`/`in_lexicon`/`SIMILARITY_LINK_
  THRESHOLD` pattern is the direct template for the verb-class extension proposed here, and its
  Tier-2 upgrade to `_referent_links` in `goal_typing.py` is the direct template for the
  `_verb_classes` Tier-2 extension in Section 4 — same file, same author-convention, same
  threshold-gated-abstain-fallback shape, now applied to a second closed-set lexicon in the same
  module.
- Directly instantiates [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]]:
  asked which brain structure (ATL hub, but ALSO checked whether it's the RIGHT structure for
  verbs specifically — Section 1c's honest answer is "partially, with a caveat") and confirmed the
  computational process (graded shared-feature cosine) is already built and should be REUSED, not
  re-derived.
- Feeds [[project_build_the_6yo_grounded_foundation_reading_builds_on_USER_2026-08-03]] and
  [[feedback_comprehension_is_a_growing_library_of_construction_competencies_not_one_objective_2026-07-31]]:
  open-vocab verb-classification-by-feature-similarity is itself a new, discrete, glass-box
  competency the comprehension organ gains — not a patch on an existing one.

---

## 7. Substrate-product implications

Unblocks the dominant, VET-confirmed bottleneck in real-prose generalization for the wired
goal-owner/outcome-valence organs (currently 0.30 owner-acc vs 0.70 recency baseline, 6/10
`OUTCOME_NEVER_TYPED`) WITHOUT any external LLM, borrowed embedding, or bolt-on parser — the fix is
entirely SUPPLY (a hand-authored, linguistically-motivated feature-tag lexicon, same category of
artifact as the existing McRae-style noun lexicon) composed via the substrate's OWN glass-box FHRR
`bundle()`/cosine mechanism, already proven and already wired for nouns. This is a strict ADD
(Tier-1 exact-match always wins; Tier-2 only fires on OOV) so it carries zero regression risk to
every currently-passing self-test and cert-suite entry. If the Section 5 cell HARD-PASSes, it is
the direct unlock for the generalization probe's own recommended next step and moves the
comprehension organ's real-prose ceiling meaningfully closer to the recency baseline it currently
loses to.

---

## 8. Citations (verified count)

~25 distinct sources across the 4 parallel lit-scans, each returned via live WebSearch with a
resolvable URL (see each sub-agent's own citation list above); NOT independently cross-checked
against primary full-text PDFs beyond abstract/search-snippet level except where explicitly
flagged (Levin's 45.6 subclass contents = MED-confidence recall, not directly quoted from a
snippet; Vinson & Vigliocco's exact 5-category taxonomy = unconfirmed, paywalled). One citation
correction caught and fixed during synthesis: "First Phase Syntax" is Ramchand (2008), not
Rappaport Hovav & Levin (the task brief's original attribution was a mix-up). Per lit-scan
calibration discipline, treat every confidence rating above as already-deflated by the sub-agents
and further capped at P<=0.50 for any novel-synthesis claim in this note.

---

## READY FOR EXP_DEV (inline, per USER-locked no-routing-files discipline — Director dispatches
## directly from this section, no separate handoff file)

**Anchor candidate (single, ranked #1, no others competing at this priority)**:
- **Pointer**: `experiments/exp_verb_class_openvocab_similarity_v1.py` (new cell, to be authored)
- **Substrate-product reading**: closes the dominant bottleneck identified in the GENERALIZATION
  PROBE (commit f496caa51) — real-prose OOV verb typing for the goal-owner/outcome-valence organs.
- **Tier hint**: cheap (~2-3 hr cell author + smoke), CPU-only (no GPU, no training — pure
  feature-lexicon authoring + FHRR bundle-cosine measurement, same cost class as
  `exp_n11c_shared_feature_lexical_similarity_v1.py` which this design directly extends).
- **Why now**: this is the diagnosed fix for a HIGH-severity, disk-VET'd negative result blocking
  the entire real-prose generalization claim for two just-wired production organs
  (`hdlab/goal_typing.py`'s goal-owner selection + outcome-valence congruence).
- **Design spec**: Sections 2-5 above are the complete, pre-reg-able design (feature tag tables,
  seed/held-out split discipline, scramble-control convention, integration code sketch, HARD-PASS/
  HARD-FAIL thresholds). exp_dev should treat Section 5's cell spec as the starting pre-reg, adjust
  N and exact thresholds per its own envelope-fail-band discipline, and port
  `scratchpad/verb_class_pilot.py`'s validated logic (not copy verbatim — it's a scratch file) into
  a proper `experiments/*.py` cell with checkpoint/resume per `tools/exp_checkpoint.py`.
- **Context pointers** (paths, not summaries): `hdlab/goal_typing.py` (integration target, lines
  396-434 for `CLASS_REGISTRY`/`_verb_classes`, lines 175-178 for `V2_OUTCOME_MET`/`_UNMET`, lines
  235-249 for `DESIDERATIVE_PASS`/`ASPECTUAL_STOP`); `hdlab/lexical_similarity.py` (mechanism
  template, `concept_similarity`/`in_lexicon`/`SIMILARITY_LINK_THRESHOLD` pattern to mirror);
  `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` section "GENERALIZATION PROBE" (trigger,
  commit f496caa51); this note's Section 3 pilot script path (scratchpad, non-production,
  reproducible).
