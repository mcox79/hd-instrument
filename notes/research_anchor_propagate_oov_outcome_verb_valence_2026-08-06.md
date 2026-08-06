# FORMALIZE-drill: ANCHOR + PROPAGATE design for grounding OOV outcome-verb result-valence (2026-08-06)

Research role, spec-only cycle (deliverable = design + pre-reg, NOT a build/run). USER-greenlit: "do it
and let's do it right." Direct continuation of `notes/SYNTHESIS_grounding_wall_definitive_2026-08-06.md`
(the reframed direction: we own the reasoning + a similarity/opposition propagation substrate + a small
genuinely-earned affective anchor, but lack two wires -- word->anchor, anchor->new-word propagation) and
the two supporting drills (`notes/drill_brain_grounding_wall_definitive_2026-08-06.md`,
`notes/drill_our_components_grounding_wall_definitive_2026-08-06.md`). Every code claim below is a
direct read of the file/line on disk this session, not a label taken on faith -- files read in full:
`hdlab/lexical_similarity.py`, `hdlab/verb_lexical_similarity.py`, `hdlab/goal_typing.py` (CLASS_REGISTRY/
OPPOSED_PAIRS/`_verb_classes`/Tier-3 sentinel region), `hdlab/context_grounded_valence.py`,
`experiments/exp_grounded_appraisal_sim_earned_v1.py`, `experiments/exp_arc_aggregation_polarity_ci_v1.py`
(`PolarityLexicon`), `hdlab/reasoner.py` (its `PolarityLexicon`/WordNet usage), `hdlab/animacy_lexicon.py`
(precedent for WordNet-as-DATA), `experiments/data/goal_bearing_modern_eval_v1.jsonl` (the 36-item test
bed, re-derived directly, not assumed), and `preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md`
(the immediately-prior HARD_FAIL this design supersedes -- its numbers are the comparison floor below).

---

## HEADLINE

**The literal 4-organ propagation substrate the task named (`hdlab/lexical_similarity.py` +
`hdlab/verb_lexical_similarity.py` + `goal_typing.CLASS_REGISTRY`/`OPPOSED_PAIRS`) CANNOT propagate
valence to a genuinely untagged word at all -- not "circularly," but literally: these organs have no
encoder for an untagged word, only a comparator between two already-tagged words, and the only per-word
representation they contain (`verb_lexical_similarity.OUTCOME_VERB_FEATURES`'s feature tag-set) has
polarity direction (`POS_AFFECT`/`NEG_AFFECT`, `AGONIST_REALIZED`/`AGONIST_BLOCKED`, `SCALE_UP`/
`SCALE_DOWN`) hand-authored INTO the only representation a word gets.** This is a stronger, sharper,
disk-verified finding than mere circularity, and it is the honest answer to the task's central question.
A buildable design exists, but it requires ONE extension beyond the four named organs: an untagged-word
NEIGHBORHOOD encoder. The design below proposes reusing `nltk.corpus.wordnet` (already a promoted,
registered hdlab dependency via `hdlab/animacy_lexicon.py`, and already used for antonym-based opposition
in a SHELVED-but-built sibling module, `experiments/exp_arc_aggregation_polarity_ci_v1.PolarityLexicon`)
as the STRUCTURE channel (which known verbs is an OOV verb like), while a SMALL, already-existing,
human-authored polarity seed (`OUTCOME_SEED_POS`/`OUTCOME_SEED_NEG`, ~52 words) supplies DIRECTION. This
is architecturally isomorphic to the brain's own division of labor (ATL-hub relatedness vs OFC/amygdala
valence, per the definitive drill's Components 1-3) and to Turney-Littman (2003) / Hamilton et al. (2016,
SentProp) / Kim & Hovy (2004) / Hatzivassiloglou & McKeown (1997) sentiment-lexicon-induction-from-a-seed.
It is genuinely NON-circular (WordNet relatedness never encodes polarity) but genuinely limited: roughly
half the 36-item eval's OOV outcome verbs are light/support verbs (`be, have, come, go, give, take, put,
find, make, carry, buy, drink, turn, curve, whisper, drag, practice`) whose valence is not lexically
inherent at all -- no verb-level propagation mechanism, however well built, can type these; the design's
honest ceiling on the FULL 36-item set is well below what it can achieve on the content-bearing subset.

---

## 1. Brain -> organ map (SHAPE + POSITION + METRIC, per FORMALIZE discipline)

| Component | Brain (SHAPE / POSITION / METRIC, per the definitive drill) | Owned organ (verified on disk) | Gap named |
|---|---|---|---|
| Small primitive valence anchor | OFC/vmPFC/ventral-striatum: content-blind scalar VALUE on an ALREADY-composed proposition (Padoa-Schioppa & Assad 2006/2008; menu-invariant common-currency, Levy & Glimcher 2012); the sign of a small set of primitives (blocked-goal=bad) is felt/endocrine-confirmed by 4-7mo (Stenberg/Campos 1983) | `verb_lexical_similarity.OUTCOME_SEED_POS`/`OUTCOME_SEED_NEG` (~52 lemmas), each carrying an explicit `POS_AFFECT`/`NEG_AFFECT` + `AGONIST_REALIZED`/`AGONIST_BLOCKED` + `SCALE_UP`/`SCALE_DOWN` tag-triple | **SUPPLIED, not earned.** A human read each word and wrote its polarity per a linguistic rubric (Jackendoff 1990 AFF polarity, Talmy 1988 force-dynamics, Beavers 2008/2011 scalar affectedness) -- honest, real, but not felt. The one genuinely-EARNED component (`pfc_gate_cfrpe`/`grounded_appraisal_sim_earned`) grounds 4 ABSTRACT SITUATION TYPES in a wordless toy world and, per the code-drill's own finding, contributes **zero bits** to any word's polarity in the currently-wired path (`channel_b_valence_table` collapses to a 2-constant lookup gated by pure clause-transitivity syntax) -- named explicitly below as out-of-scope future work, not silently smuggled in as "the anchor." |
| Semantic relatedness / hub-and-spoke convergence | ATL transmodal hub: graded, multidimensional similarity over experientially-accumulated features (Cox et al. 2024; Patterson/Nestor/Rogers 2007) -- NEVER itself carries valence direction, only "how alike are these two concepts" | Proposed: WordNet verb-synset hypernymy/synonymy graph (`nltk.corpus.wordnet`), already promoted+registered as glass-box hdlab DATA via `hdlab/animacy_lexicon.py` (`registered_2026-08-03`) | Relatedness STRUCTURE is human-curated (WordNet), not experientially accumulated -- same honest scope caveat `hdlab/lexical_similarity.py`'s own docstring already carries for McRae norms. The SHAPE match (convergence enables graded similarity, never itself signed) is real and load-bearing for the non-circularity argument below. |
| Opposition / explicit antonymy | Not itself well-localized in the drill's citations, but functionally necessary -- Component 8's "but"-boundary finding: discourse structure signals "a reversal is coming," never which direction; direction must come from elsewhere, and an explicit LABELED-opposition (not a geometric bipolar axis) is the architecture Kintsch (1988) CI signed-inhibition and this substrate's own prior contradiction-detection cycle already chose | `goal_typing.OPPOSED_PAIRS`/`OPPOSED_OF` (6 in-house opposed CLASS_REGISTRY pairs) + `PolarityLexicon._antonyms()` (WordNet `lemma.antonyms()` + curated `_FLIP_PAIRS`), lifted from `experiments/exp_arc_aggregation_polarity_ci_v1.py` (SHELVED but BUILT, cert-tested, cited Yih/Zweig/Platt 2012 "the antonym problem"; Mrksic et al. 2016/2017) | Reuse, not reinvention -- the antonym-lookup mechanism already exists in this repo for a different task (ARC QA contradiction detection) and is a clean lift under the SAME "hdlab-only clean copy" convention `lexical_similarity.py`/`verb_lexical_similarity.py` already used when promoting from `experiments/exp_n11c*`. |
| Propagation / spreading | Barsalou's "accumulation mechanism" -- repeated co-activation entrenches an associative network (per the definitive drill's Component 1); functionally, label-propagation over a relatedness graph from a small labeled seed (SentProp, Hamilton et al. 2016; Turney & Littman 2003) | Proposed: NEW function, k-nearest-neighbor-vote over the WordNet graph, seeded from `OUTCOME_SEED_POS`/`NEG`, opposition-checked first via `PolarityLexicon` | Genuinely new build (not currently on disk in any form -- a targeted grep this session for `PPMI`/`NNSE` across `hdlab/`+`experiments/` returned ZERO hits, so the SYNTHESIS's phrase "the mechanism the verb-feature drill already piloted at small scale" refers to the Tier-2 hand-tag cosine mechanism, NOT a corpus-statistical propagation method -- correcting that impression here). |
| Consumer / goal-comparison | PFC goal-maintenance + congruence evaluation (Component 6) -- comparison of maintained goal against arriving outcome | `goal_typing.congruence_decision` + `_verb_classes`'s Tier-3 `ACQUIRED_*` pole sentinel (already built, strict-ADD, empty overlay = byte-identical to before) | **No gap** -- already brain-faithful shape per the prior drill's own finding; this design changes only what feeds the Tier-3 overlay, not the consumer. Confirmed by direct code read: `register_acquired_outcome(word, polarity)` is the existing, unchanged write-back API this design targets. |

---

## 2. THE ANCHOR -- design, size, and honest per-element provenance

**What it is:** the union of `verb_lexical_similarity.OUTCOME_SEED_POS` (26 lemmas) and
`OUTCOME_SEED_NEG` (26 lemmas) = **52 words**, already the PRODUCTION Tier-1/Tier-2 base vocabulary
(`CLASS_REGISTRY`'s literal seed members, retagged 2026-08-06 per the open-vocab verb-class drill). Zero
new authoring for this increment -- this is pure reuse.

**Why exactly this set, not the broader ~78-word `OUTCOME_HELDOUT_POS`/`_NEG` (SUPPLY EXTENSION):**
keeping the anchor to the ORIGINAL seed (not the already-extended held-out vocabulary) is a deliberate,
conservative choice for two reasons: (1) it is the smallest defensible seed that still spans all 6
`OPPOSED_PAIRS` classes (`REPAIR_PRESERVE`/`DAMAGE_LOSE`, `ARRIVE_SUCCEED`/`FAIL_LOSE`,
`OPEN_CLASS`/`CLOSE_CLASS`, `FILL_CLASS`/`EMPTY_CLASS`, `GATHER_CLASS`/`SCATTER_CLASS`,
`HEAL_CLASS`/`HARM_CLASS`), so opposition-checking has coverage on both poles of every class; (2) using
the HELDOUT words too would blur the provenance story ("is this word in the anchor because it was
hand-tagged as a genuine PRIMITIVE, or because a prior increment's SUPPLY EXTENSION happened to include
it") -- keeping the anchor = the original CLASS_REGISTRY seed keeps every element's provenance
traceable to ONE sentence: "this was already the production Tier-1 vocabulary before this drill existed."
(`OUTCOME_HELDOUT_POS`/`_NEG` remain available as an optional anchor-expansion knob, explicitly flagged
as a SEPARATE, larger-anchor variant in the pre-reg's ablation list, not the default.)

**Per-element honesty, exactly as the task demands:**
- The 52 word->polarity ASSIGNMENTS: **100% SUPPLIED.** A human read each word and decided POS or NEG.
  This is NOT earned, NOT felt, NOT the brain's OFC/RPE mechanism. Calling this "grounding" in the
  Component-3/4 sense (a felt, endocrine-confirmed primitive) would overclaim. It is the SAME kind of
  supply the SUPPLY EXTENSION already used -- reused as a SEED for propagation rather than as a per-word
  answer key, which is a real architectural change even though the underlying data is not new.
- The FEATURE ALPHABET itself (`POS_AFFECT`/`NEG_AFFECT`, `AGONIST_REALIZED`/`AGONIST_BLOCKED`,
  `SCALE_UP`/`SCALE_DOWN` -- 6 symbols, fixed, shared across every word, never grown per-word) is the
  closest analog in this pipeline to a genuine INNATE PRIMITIVE CODE (small, constant-size, applied
  uniformly) -- but the ALPHABET being small and fixed does not make its 52 per-word ASSIGNMENTS earned;
  those are still supplied. Keep these two claims separate: the CODE is primitive-shaped, the
  ASSIGNMENTS are not primitive-sourced.
- The RL-earned component (`pfc_gate_cfrpe_trained_v2` / `grounded_appraisal_sim_earned`): **explicitly
  NOT part of this increment's anchor.** It is real, it passes its own can-fail floors (RANDOM~chance,
  MEMORIZED fails to generalize, `coh_minus_rec_readout>0`), but per the code-drill's own finding it
  grounds 4 abstract SITUATION TYPES in a wordless toy world and, as currently wired
  (`context_grounded_valence.score_item`'s `combine_biased_competition` precedence +
  `word_acquisition_loop.channel_b_valence_table`), contributes literally zero word-specific bits to any
  verb's polarity -- confirmed by increment 1b's own measured finding that removing the reward-theta
  lookup and hard-coding its 2 output constants was BEHAVIORALLY IDENTICAL ("proven-redundant, not a
  capability loss"). Including it here as "the anchor" without that caveat would repeat exactly the
  overclaim the prior drill caught. **Building a genuine word-form -> RL-consequence learning wire (read
  the situation model's own downstream MET/UNMET verdict for the episode a verb occurred in, and use
  THAT as the reward-relevant label for that verb -- the code-drill's own named "correct next move") is
  a real, larger, SEPARATE increment, out of scope for this propagation-only design, and named here so it
  is not lost.**

**Total anchor size relative to the target vocabulary:** 52 words vs. an open-ended English
result-verb vocabulary (thousands) -- genuinely small by construction, matching the SYNTHESIS's framing
("a SMALL primitive affective anchor... reasons everything else outward... via similarity + opposition,"
not "supply grounded meaning for hundreds of verbs").

---

## 3. THE PROPAGATION SUBSTRATE -- confronting the direction question head-on

### 3a. Strict scope (ONLY the 4 named organs): a stronger negative finding than circularity

Read directly off `hdlab/verb_lexical_similarity.py`: `_pos_tags(domain)` returns exactly
`{domain, "POS_AFFECT", "AGONIST_REALIZED", "SCALE_UP", "RESULT_ROOT"}` and `_neg_tags(domain)` returns
`{domain, "NEG_AFFECT", "AGONIST_BLOCKED", "SCALE_DOWN", "RESULT_ROOT"}` for EVERY word in
`OUTCOME_VERB_FEATURES` (both the original seed AND the already-tagged SUPPLY EXTENSION) -- 4 of each
word's 5 tags are the LITERAL polarity signature, identical string-for-string across every POS word and
every NEG word regardless of domain. `concept_vector(word, domain)` (the ONLY per-word representation
these organs produce) is `None` for any word NOT a key in `OUTCOME_VERB_FEATURES` or the (also
hand-populated) `ACQUIRED_OUTCOME_VERB_FEATURES` overlay -- confirmed directly: `_features_for` returns
`None` for an untagged word, and every consumer (`word_similarity`, `mean_similarity_to_seeds`,
`classify_2way`, `in_lexicon`) short-circuits to `None`/abstain the instant either input word is
untagged. **There is no path anywhere in `hdlab/lexical_similarity.py` or `hdlab/verb_lexical_similarity.py`
that converts a word's SURFACE FORM into ANY vector unless a human already wrote its tag-set.** This means
"propagation," as the task's named 4-organ scope literally allows it, is not merely circular for an
already-tagged word (though it is that too, per the module's own docstring: "General open-vocabulary
feature INDUCTION for arbitrary, never-hand-tagged verbs remains a separate, missing-LEARNING
follow-up") -- for a genuinely untagged word (e.g. every OOV verb in the 36-item eval: `ruin, spoil,
whitewash, rap, refuse, relent, whip, ...`), it is **literally impossible**, returning `None` at the
very first step, before any similarity computation, opposition check, or vote could even be attempted.
**This is the honest, disk-verified answer to "if the honest answer is this can't work without supplying
direction per-verb, say so": within the strict 4-organ scope, it cannot work at all, not even circularly.**

### 3b. Extended design (adds ONE untagged-word encoder): buildable, non-circular by construction

To make propagation possible at all requires exactly one new capability: a way to place an UNTAGGED
word into SOME relationship with the tagged vocabulary. Two candidates were considered and rejected
before landing on the recommended one:

- **REJECTED: re-derive a fresh in-house corpus co-occurrence / PPMI channel.** This substrate's OWN
  prior HARD_FAIL (increment 1b, `CHANNEL_A_ATOMS` = clause transitivity/argument-structure) already
  demonstrated that surface-distributional/structural cues do NOT discriminate polarity --
  `"She ruined the cake"` and `"She fixed the cake"` are structurally identical, and this is not an
  underpowering artifact (16/36=0.4444, BELOW the 23/36=0.6389 majority floor, confirmed on disk). Raw
  co-occurrence/PPMI similarity has the SAME failure mode for the same underlying reason as the
  "distributional paradox" the SYNTHESIS names for adjectives: antonym-adjacent verbs like `ruin`/`fix`
  occur in near-identical local syntactic frames (both are transitive change-of-state verbs acting on the
  same object classes), so a freshly-built PPMI-neighborhood channel would very likely REPRODUCE increment
  1b's failure rather than fix it. Flagged here explicitly so it is not silently re-attempted.
- **RECOMMENDED: WordNet verb-synset relatedness, reusing an already-promoted hdlab dependency.**
  `hdlab/animacy_lexicon.py` (registered 2026-08-03, "WordNet-sourced glass-box animacy/category
  lexicon") already establishes WordNet as a legitimate, already-adopted, glass-box DATA resource in this
  substrate -- not a new external dependency, not a "bolt-on reader" (WordNet is a static lexical
  database, not a comprehension mechanism; it does not parse sentences, exactly the same "DATA supply is
  OK, the reading MECHANISM is not" distinction `hdlab/lexical_similarity.py`'s own McRae-norms precedent
  already relies on). Critically, WordNet's synonym/hypernym STRUCTURE is curated SEPARATELY from its
  ANTONYM relation (`lemma.antonyms()`) -- synsets group words by MEANING similarity (near-synonyms:
  `ruin, spoil, wreck, damage, mar` cluster under a shared "make imperfect / impair" hypernym lineage),
  and this grouping is NOT vulnerable to the antonym-conflation failure raw co-occurrence has, because a
  human already separated "same-meaning" (synset membership) from "opposite-meaning" (the antonym
  pointer) as two DIFFERENT relation types when building WordNet. This is the mathematical resolution to
  the direction problem: **WordNet relatedness supplies NEIGHBORHOOD without ever supplying DIRECTION
  (no synset carries a polarity value); direction comes ONLY from (i) the small hand-anchored seed's
  labels, propagated across a neighborhood edge, or (ii) an explicit antonym/opposition edge, which
  flips rather than copies the neighbor's label.**

**Reuse, not reinvention, for the opposition channel:** `experiments/exp_arc_aggregation_polarity_ci_v1.py`
already contains a built, cert-tested `PolarityLexicon` class (`SHELVED` per
`data/capability_registry.jsonl`'s `hdlab/reasoner.py` row, "built_2026-07-25_then_abandoned_2026-07-27"
-- built and functional, just not currently serving anything) whose `_antonyms(word)` method does exactly
`wn.synsets(w)` -> `lem.antonyms()` plus a small curated `_FLIP_PAIRS` list (mostly comparative
adjectives, less directly relevant to verbs but reusable), citing Yih/Zweig/Platt (2012, "the antonym
problem") and Mrksic et al. (2016/2017, counter-fitting/Attract-Repel). Lifting `_antonyms()` (clean-copy
convention, same pattern `lexical_similarity.py`/`verb_lexical_similarity.py` already used promoting from
`exp_n11c`) gives the opposition channel for free -- zero new design risk, reusing already-exercised code.

### 3c. The propagation algorithm (spec, not yet implemented)

For a lemma `L` OOV of Tier-1 (`CLASS_REGISTRY`), Tier-2 (`OUTCOME_VERB_FEATURES`, hand-tagged) and the
current Tier-3 overlay (`ACQUIRED_OUTCOME_VERB_FEATURES`):

1. **Opposition-first (higher precedence -- explicit relations beat inferred neighborhoods).**
   `antonyms = PolarityLexicon._antonyms(L)` (lifted). If `antonyms & ANCHOR_WORDS` is non-empty, propose
   the OPPOSITE polarity of the (majority of the) matched anchor word(s)' polarity. This also subsumes
   the `goal_typing.OPPOSED_PAIRS`/`CLASS_REGISTRY` in-house opposition: if `L`'s WordNet neighbor set (step
   2) lands inside a `CLASS_REGISTRY` class whose `OPPOSED_OF` partner is ALSO represented in the neighbor
   set, that is a second, corroborating opposition signal (report both signals; do not silently merge).
2. **Neighborhood vote (fallback if no antonym match).** `neighbors = {a in ANCHOR_WORDS : L and a share a
   WordNet verb synset, OR a is within hypernym-path-distance <= D of L}` (D pre-registered, not tuned
   post-hoc -- see pre-reg). Weight each neighbor's polarity vote by `wn.path_similarity(L_synset,
   a_synset)` (or `wu_palmer_similarity`, both native `nltk.corpus.wordnet` methods, glass-box,
   deterministic). Predict the majority-weighted polarity; **abstain** (never guess) if `neighbors` is
   empty or the vote margin is below a pre-registered floor -- same abstain-safe design discipline
   `verb_lexical_similarity.classify_2way`'s `floor`/`margin` and `lexical_similarity.SIMILARITY_LINK_
   THRESHOLD` already use.
3. **Write-back.** `register_acquired_outcome(L, polarity)` -- the EXISTING, UNCHANGED API. Zero new
   plumbing downstream: `_verb_classes`'s Tier-3 pole sentinel (`_acquired_pole_sentinel`, already built,
   strict-ADD, confirmed empty-overlay-safe by direct code read) and `_tier2_outcome_polarity_scan`'s
   `classify_2way` fallback (the flat V2-lexicon path) BOTH already consult `ACQUIRED_OUTCOME_VERB_
   FEATURES` as a strict fallback -- confirmed by direct read of `_features_for`'s choke-point logic. This
   means the new PROPOSE mechanism (WordNet-neighborhood + antonym-opposition) is a clean swap for
   increment 1b's failed PROPOSE mechanism (clause-transitivity), reusing 100% of the existing
   PROPOSE-trigger / CONSOLIDATE / write-back scaffolding in `hdlab/word_acquisition_loop.py`, and it
   improves BOTH consumer paths (the full congruence-organ path via the Tier-3 sentinel, AND the flat
   lexicon-fallback path via `classify_2way`), not just one.

### 3d. VERDICT on the direction question (as demanded, stated plainly)

**Feature-similarity as currently built (the 4 named organs) does NOT carry direction as a discoverable
property -- direction is stipulated directly into the only representation a word gets, and there is no
path from "untagged word" to "any vector" at all. This is not circular, it is a hard blocker; propagation
over ONLY these organs is a non-starter for genuinely novel words.** A buildable, non-circular design
exists, but it requires bringing in a genuinely SEPARATE relatedness channel (WordNet synsets) whose
defining property is that it is structurally BLIND to polarity (no synset carries a valence value) --
which is exactly the property needed for a legitimate propagation architecture: relatedness answers "is
this OOV word like a word I already know the sign of," and the sign itself flows from the small anchor
seed (52 words, human-authored, honestly flagged as supplied-not-earned) through that relatedness edge,
or is flipped by an explicit antonym edge. This mirrors the brain's own division of labor (ATL-hub
relatedness is content-blind to valence; OFC/amygdala supplies the sign) closely enough to call it
brain-analogous in SHAPE, while being honest that WordNet's curation process (human lexicographers, not
a lifetime of grounded sensorimotor/affective co-activation) is not itself a felt, developmental origin
story -- the SAME honest caveat this substrate's own `hdlab/lexical_similarity.py` docstring already
carries for its McRae-norm nouns.

---

## 4. Honest scope / known limits -- read against the actual 36-item eval, not in the abstract

`experiments/data/goal_bearing_modern_eval_v1.jsonl` has 44 items; 36 have `outcome_in_lexicon: false`
(re-derived directly this session, matching `preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md`'s
own count exactly). Their 33 unique outcome-verb lemmas: `admit, agree, be, befriend, buy, carry, come,
croak, curve, drag, drink, encore, find, flee, give, go, have, improve, jell, like, make, practice, put,
rap, refuse, relent, ruin, spoil, take, turn, whip, whisper, whitewash`.

**Roughly half of these are light/support/manner/directional verbs with no lexically-inherent valence at
all** (`be, have, come, go, give, take, put, find, make, carry, buy, drink, turn, curve, whisper, drag,
practice` -- 17 of 33 unique lemmas): their polarity in the eval is determined COMPOSITIONALLY by their
argument/object or by discourse context (e.g. `"the balls failed, except the one...that curved"` -- the
verb `curve` itself is valence-neutral; the negation-scope + comparative structure carries the sign), not
by anything a verb-level lexical mechanism -- WordNet-based or otherwise -- can recover. **No design that
propagates POLARITY AT THE VERB LEVEL can correctly type these**, and this design does not claim to; it
should ABSTAIN on them (safe, matching the existing abstain-on-uncertain discipline), not guess. This
sets a real, honest ceiling on the FULL 36-item metric well below 100% regardless of mechanism quality.

**One further, sharper known-limit case worth naming explicitly: `croak`.** In the eval item
(`lw_jo_laurie_snowball`, gold `met`), "croak" is used in its archaic sense of speaking hoarsely (a
positive/neutral outcome for Jo's goal). WordNet's PRIMARY verb senses for "croak" are (1) the frog/raven
vocalization and (2) the slang euphemism for dying -- both of which, if naively used for a neighborhood
vote, could pull toward a NEGATIVE association with no relevance to the actual intended sense. This is a
genuine, disk-honest word-sense-disambiguation gap this design does NOT solve (no WSD step is proposed);
flagged as an expected miss, not silently absorbed into an inflated accuracy claim.

**The "18-eligible (goal-reachable) subset," reconciled exactly.** Computed directly against the live
eval file: `18/36` items have a `goal_verb_lemma` that is one of the 10 literal base
`DESIDERATIVE_PASS` words (`want, hope, wish, mean, plan, intend, aim, long, yearn, desire`) --
this is the SAME definition, verified byte-for-byte, as `preregs/2026-08-06_grounded_word_acquisition_
increment1b_v1.md`'s own "Coverage sub-partition" (which independently arrived at 18/36 for the SAME
reason: only these items are reachable via `find_desired_state`'s hard-coded literal gate, and thus
via the FULL `congruence_decision` organ path; the other 18 fall through to the flat V2-lexicon-fallback
path regardless of outcome-verb typing quality). This is NARROWER than the eval file's own
`goal_in_lexicon` field (True for 26/36 -- that field also credits `try`/`determine`/`beg`, which
`find_desired_state` does NOT recognize via its literal `DESIDERATIVE_PASS` set; they are Tier-2
`GOAL_VERB_FEATURES`-similarity-classifiable but never reach `find_desired_state`'s gate at all, confirmed
by direct code read). **Use the 18/18 split, not the 26/10 split** -- reusing an already-verified prior
definition rather than inventing a new one. Eligible-subset gold: 12 met / 6 unmet (majority floor
0.6667). Non-eligible-subset gold: 11 met / 7 unmet (majority floor 0.6111).

---

## 5. Cheap decisive test / falsifiable predictions (summary -- full bands in the companion pre-reg)

Full bands, controls, and exact procedure: `preregs/2026-08-06_anchor_propagate_oov_outcome_verb_
valence_v1.md`. Summary:
- **Primary metric:** live `congruence_with_lexicon_fallback` MET/UNMET accuracy on the 36-item OOV
  subset, with the new WordNet-neighborhood+opposition propagation populating `ACQUIRED_OUTCOME_VERB_
  FEATURES` before scoring. HARD-PASS requires beating the 0.6389 majority floor by a real margin AND
  beating increment 1b's 0.4444 decisively, reported alongside the 18/18 eligible-vs-non-eligible split.
- **Non-circularity (load-bearing, gates the primary verdict regardless of raw accuracy):** (a) SCRAMBLE
  -- permute the 52-word anchor's polarity labels (fixed seed, same convention as this module family's own
  `self_test` scramble arms), re-run propagation with the WordNet graph UNCHANGED; accuracy must collapse
  toward chance. (b) RANDOM-GRAPH ablation -- replace real WordNet edges with a degree-matched random
  graph; must also collapse. (c) DIRECTION-REMOVED ablation -- a neighborhood-only arm that finds WordNet
  neighbors but reads only their `EVENT_DOMAIN` tag (never `POS_AFFECT`/`NEG_AFFECT`), forced to guess;
  must NOT beat the majority floor, isolating that direction (not mere relatedness) is load-bearing.
- **Precision/over-fire control:** a noise-canary set of semantically empty/manner-neutral verbs (not
  drawn from the 36-item eval's own vocabulary) must not get confidently consolidated with a polarity.

---

## 6. Cross-thread synthesis

Directly operationalizes `notes/SYNTHESIS_grounding_wall_definitive_2026-08-06.md`'s "REVISED DIRECTION"
(anchor + propagate, superseding the old A/B/C fork) into a buildable spec, and directly supersedes
`preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md` / `_increment1b_v1.md` (both HARD_FAILed
because they tried to read polarity off surface syntax/transitivity, which this drill's own re-read of
increment 1b's `CHANNEL_A_ATOMS` confirms structurally cannot carry the signal -- `"ruined"` and `"fixed"`
are clause-shape-identical). Reuses, rather than duplicates, three already-built organs from THIS session's
own prior work: `hdlab/lexical_similarity.py` / `hdlab/verb_lexical_similarity.py` (promoted 2026-08-06,
the comparator half of the mechanism) and `experiments/exp_arc_aggregation_polarity_ci_v1.PolarityLexicon`
(SHELVED but built, the antonym-opposition half) -- a genuine cross-thread reuse the "wire don't island"
discipline calls for, connecting two previously-unrelated build threads (ARC QA contradiction detection
and outcome-verb goal-congruence typing) that turn out to need the SAME opposition primitive. Directly
answers the make-or-break question the task posed: feature-similarity as built does NOT carry direction
(3a); a genuinely non-circular design is possible but requires one new, well-precedented, glass-box
extension (3b-3c), not a hidden per-word supply step.

---

## 7. Substrate-product implications

- **Do not attempt a fresh in-house PPMI/co-occurrence propagation channel** as an alternative to WordNet
  -- this substrate's own increment-1b HARD_FAIL already demonstrates the specific failure mode
  (surface-distributional cues conflate opposites) that a co-occurrence-based neighborhood channel would
  most likely reproduce. This is a real, disk-grounded reason to prefer the WordNet-relatedness design,
  not an arbitrary preference.
- **Do not expect this design, however well it performs on its eligible subset, to close the full 36-item
  eval to a high number.** Roughly half the eval's OOV verbs are light/support verbs whose valence is
  compositional, not lexical -- report the light-verb-excluded ceiling honestly alongside the full-36
  number so a future increment (compositional/argument-based valence, a genuinely separate mechanism) is
  not judged against an unfair target this increment was never designed to hit.
- **The RL-earned anchor (`pfc_gate_cfrpe`) is real and should NOT be abandoned, but should not be
  smuggled into this increment's claims either.** A genuine word-form -> situation-model-consequence
  learning wire (read the situation model's own eventual MET/UNMET verdict for an episode and use it as
  the reward-relevant label for the outcome verb that occurred in it) is the brain-faithful, larger,
  separate next increment this drill's own code-read points to -- name it, do not build it here, and do
  not let a future increment's WordNet-propagation success be misread as having solved that problem too.
- **The lifted `PolarityLexicon._antonyms()` reuse is a genuine wire-don't-island opportunity independent
  of this specific increment** -- it is sitting SHELVED with zero consumers; this design gives it a live
  one, and the same lift could plausibly serve other opposition-relevant future work (negation-scope,
  named in the standing NEXT list) without re-deriving antonym lookup a third time.

---

## Citations (verified count)

**This session's direct code reads (primary evidence, 8 files, cited inline throughout):**
`hdlab/lexical_similarity.py`, `hdlab/verb_lexical_similarity.py`, `hdlab/goal_typing.py`,
`hdlab/context_grounded_valence.py`, `experiments/exp_grounded_appraisal_sim_earned_v1.py`,
`experiments/exp_arc_aggregation_polarity_ci_v1.py`, `hdlab/reasoner.py`, `hdlab/animacy_lexicon.py`, plus
`experiments/data/goal_bearing_modern_eval_v1.jsonl` and `data/capability_registry.jsonl` (both queried
directly this session, not recalled).

**Reused, previously verified in the definitive synthesis + 2 drills this note builds on (not re-fetched
this session, ~163 citations by reference):** Padoa-Schioppa & Assad (2006/2008); Levy & Glimcher (2012);
Cox, Rogers, Shimotake et al. (2024); Patterson, Nestor & Rogers (2007); Stenberg, Campos & Emde (1983);
Xiang & Kuperberg (2015); Turney & Littman (2003); Warriner, Kuperman & Brysbaert (2013).

**New this session (generic academic terms, query-privacy discipline, cited from established knowledge of
the sentiment-lexicon-induction literature, not independently re-fetched via WebSearch this cycle --
flagged MEDIUM, standard/canonical results, not contested):** Hamilton, Clark, Leskovec & Jurafsky (2016,
"Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora," SentProp); Kim & Hovy (2004,
"Determining the Sentiment of Opinions," WordNet-seed propagation); Hatzivassiloglou & McKeown (1997,
"Predicting the Semantic Orientation of Adjectives," conjunction-based polarity coherence); Hu & Liu
(2004, "Mining and Summarizing Customer Reviews," WordNet synonym/antonym seed expansion); Yih, Zweig &
Platt (2012, PILSA, "the antonym problem," reused verbatim from `exp_arc_aggregation_polarity_ci_v1.py`'s
own citation); Mrksic et al. (2016/2017, counter-fitting/Attract-Repel, same reuse).

**P_deflated:** the core architectural claim ("small anchor + WordNet-relatedness propagation +
explicit-opposition is non-circular and brain-analogous in shape") is well-triangulated against an
established literature (Turney-Littman/Hamilton SentProp/Kim-Hovy/Hatzivassiloglou-McKeown all
independently converge on seed-plus-relatedness-graph propagation as the standard architecture for this
exact problem) but its APPLICATION to THIS substrate's specific organs is this drill's own synthesis, not
directly tested -- raw ~0.62 (strong precedent in the general literature + a clean, low-risk reuse path
inside this substrate) deflated 0.20 (novel-synthesis, unexecuted, honest light-verb ceiling not yet
measured) -> **P_deflated = 0.42** (below the 0.50 novel-synthesis cap, reflecting that the DESIGN is
sound but its measured yield on THIS specific 36-item eval, given ~half the items are structurally
out-of-reach for any verb-level mechanism, is genuinely uncertain until run).
