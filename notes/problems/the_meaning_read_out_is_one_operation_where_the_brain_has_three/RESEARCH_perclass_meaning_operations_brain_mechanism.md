# Finest-resolution brain-mechanism drill: the meaning read-out is ONE operation where the brain has (at least) THREE

Solver research note for `the_meaning_read_out_is_one_operation_where_the_brain_has_three`. Web-grounded drill
(hdi_research, 2026-08-27) + on-disk verification. Every claim is labelled PINNED-BY-EVIDENCE or
OUR-INVENTION-UNDER-TEST. The disk outranks the brief; where they disagree it is flagged.

## 0. The claim, sharpened

The reader judges meaning-similarity with ONE operation: IDF-weighted feature-overlap cosine over WordNet
definitional bags (`hdlab/conceptual_meaning`). That operation is CORRECT for nouns and it wins them
(SimLex nouns: conceptual 0.599 > GloVe 0.397). It is the WRONG operator for the other classes, and the
drill shows the brain does not use two more operations but **at least four**, across two POS:

| class | brain operation (PINNED) | structure | our current op | verdict |
|---|---|---|---|---|
| NOUN | taxonomic feature/genus overlap (ATL hub) | shared features | conceptual cosine | CORRECT (landed) |
| ADJ, gradable-denotational | SIGNED-MAGNITUDE on a per-dimension analog scale (ATOM/IPS) | signed position + explicit opposition | one cosine | WRONG-OP |
| ADJ, evaluative/connotative | position in the Osgood EPA / Warriner VAD bipolar space | signed position on affect axes | one cosine | WRONG-OP |
| ADJ, classificatory/non-gradable | denominal -> TAXONOMIC (the noun op) | shared features | one cosine | the NOUN op is right |
| VERB | relational / argument-structure (thematic roles) | who-does-what-to-whom | conceptual gloss (partial) | cosine on a blended vector loses |

**So "adjectives" is not one class and the fix is a ROUTER, not one replacement operation.** That is the
deepest correction the drill produced, and it is more brain-faithful than the brief's single
"signed-magnitude adjective op."

## 1. Scalar adjectives -- the finest resolution

**(a) ATOM / IPS and the distance effect [PINNED].** Walsh's *A Theory Of Magnitude* (2003) posits a common
analog magnitude metric in parietal cortex (intraparietal sulcus) shared across number, space, time and other
"more/less" (prothetic) magnitudes. Its behavioural fingerprint is the **symbolic distance effect** (Moyer &
Landauer 1967): the time to judge which of two items is larger/fiercer/older falls as their separation on the
dimension grows, fit by a Weber-ratio, **log-compressed** law -- and it holds for *adjective* comparisons, with
a **semantic-congruity** effect (which-is-smaller is faster for small things), i.e. a reference-point/pole
process, not bare subtraction. => the representation is an **analog SIGNED scale**; magnitude is **ratio/rank
coded** (so ORDER is the robust readout, exact spacing is not); comparison **selects a pole/reference**.

**(b) Kennedy & McNally degree semantics [PINNED] -- why ONE global axis fails.** A scale = DIMENSION +
total ORDERING + DEGREES; a gradable adjective maps an entity to a degree on its lexically-fixed dimension.
Crucially the **dimension is lexically selected** (`tall`=height, `heavy`=weight) so `tall` and `heavy` are
**incommensurable** -- there is no shared axis. This is the analytic reason a *global-profile* SemAxis (project
every word onto 1263 axes) TIED its random control in prior work: irrelevant axes are pure noise. The scale is
**per-pair / per-context**. The standard/comparison-class is selected CONTEXTUALLY ("tall for a jockey"); the
neural correlate is a **semantic-control** act (LIFG/pMTG controlled retrieval) -- the SAME organ this
substrate already found missing (context-override WSD, trigger AUC 0.79). **Magnitude lives in IPS; picking the
dimension/standard is a separate control operation.**

**(c) Osgood EPA ~= Warriner VAD [PINNED, but PARTIAL].** Osgood's semantic differential factor-analyses
bipolar adjective ratings into **Evaluation, Potency, Activity** (good-bad, strong-weak, active-passive),
Evaluation dominant, replicated cross-linguistically; these map onto **Warriner Valence/Dominance/Arousal**
(on disk). This is the right low-dim space for **connotative/evaluative** adjectives but it is a **sub-space**:
it does not carry denotational dimensions (tall, wooden, frozen). One human-rated, WordNet-INDEPENDENT gold for
this branch is already on disk.

**(d) Opposition is IRREDUCIBLE [PINNED -- corroborated by this substrate's own landed valence work].**
In distributional space the neighbours of `small` are `tiny, little` (synonyms) AND `large, big` (antonyms),
indistinguishably (Nguyen et al. 2016). This substrate's `hdlab/wordnet_polarity_propagation.py` (SOLVED
EXCELLENT) measured the same for valence: antonyms are similar in EVERY feature geometry (embodied 0.270 ~=
synonym 0.266) yet flip the human rating (-0.556) -- so **the sign/opposition CANNOT be a projection; it must
come from an explicit lexical relation.** The reconciliation: a SemAxis pole-difference vector IS geometric,
but it must be **ANCHORED by an explicit antonym pair** (the two poles supplied relationally); position on the
anchored axis is then geometric. **=> our adjective op builds each bipolar axis from the explicit WordNet
antonym relation, then reads signed position geometrically.**

**(e) Gradable vs non-gradable [PINNED] -- "adjectives" is genuinely not one class.** Classificatory adjectives
(`wooden, medical, atomic`) are denominal/relational (`wooden->wood`), fail "*very X*", have no comparative,
and their similarity is **taxonomic** -- i.e. the **existing noun gloss-overlap op is already correct for
them**, and a scalar op would be wrong. The faithful design needs a **gradability GATE** (comparative form /
"very"-modifiability / WordNet antonym-dumbbell membership) as a can-fail router.

## 2. Is "signed-magnitude on a bipolar axis" the right frame?

**Yes for the gradable branch, with three corrections; and the bolder, more brain-faithful frame is
two-systems-plus-a-router.** Corrections: (i) NOT one global axis -- a bundle of per-dimension axes with a
dimension/standard-selection gate (the semantic-control organ); (ii) magnitude is Weber/log-compressed, so the
robust readout is ORDER (rank), not linear distance; (iii) the pole must be relation-anchored. The stronger
account -- which also matches this substrate's landed "two meaning systems" finding -- is a **denotational
scalar system** (ATOM/IPS, per-dimension, distance-effect) + a **connotative-affective system** (Osgood/VAD,
vmPFC/amygdala) + a **taxonomic route** for classificatory adjectives, with the adjective WIN coming from
ROUTING each adjective to the op its subclass demands.

## 3. Verbs -- relational / argument-structure [PINNED]

The brain represents verb meaning relationally: **pSTS assigns thematic roles and scales with argument-structure
complexity; LIFG selects participant-roles**; more-argument verbs load posterior temporal/parietal cortex. A
single blended distributional vector averages over contexts and keeps a bag-of-collocates while discarding
who-does-what-to-whom -- exactly the signal that makes two verbs similar -- which is why GloVe scores ~0.15 on
SimLex/SimVerb verbs. **Faithful buildable op (OWNED, disk refutes the brief's "not-yet-owned"): VerbNet
Levin-class + thematic-role + syntactic-frame overlap (primary) fused with FrameNet frame overlap (secondary),
gloss fallback.** VerbNet class = the verb analogue of the noun genus. SimVerb-3500 guarantees >=3 verbs per
VerbNet class by construction -- the natural test bed (2,871 / 3,500 pairs are VerbNet-covered on disk).

## 4. The instrument reframe (the power fix) and the selection-confound guard

The op is magnitude-native, so the fair, high-power test is **per-dimension RECOVERY + the Moyer distance
effect (ordering)**, NOT pairwise similarity -- SimLex has only 111 adjective pairs (the n=111 wall). The
INDEPENDENT, non-WordNet, human-rated golds are already on disk: **Warriner VAD (3,640 WordNet adjectives)** and
**Brysbaert concreteness (6,112 dominant-adjectives)**. Fetchable crowd-ordered sets (Wilkinson & Oates 60 adj;
Cocos CROWD 330 pairs) are the pure gradable-denotational ordering golds but are SMALLER; de Melo & Bansal is
larger but derives scales from **WordNet dumbbells** -> a benchmark-selection confound against a WordNet-antonym
op (guard flagged; not used as primary). Warriner/concreteness dodge that confound (human ratings, no WordNet in
gold construction) and are bigger -- so they are the primary golds.

## 5. What the disk says (measured this drill)

- PART 1 reproduces the incumbent per-class SimLex numbers EXACTLY: adj CONC 0.4787 < GloVe 0.5850 (wrong op);
  noun CONC 0.5994 > GloVe 0.3968; verb CONC 0.4918 > GloVe 0.1521.
- ADJECTIVE signed-magnitude recovery of the human Warriner/concreteness magnitude (op = GloVe projection onto
  the explicit-antonym-anchored dimension axis), strength tracking Osgood factor strength:
  **valence 0.698, dominance 0.311, concreteness 0.218, arousal 0.179**; the INCUMBENT feature-overlap channel
  gets **0.117 / 0.123 / -0.074 / 0.134** (it has no signed-magnitude structure), random-axis twin ~0, shuffled
  gold ~0. The **Moyer distance effect** is present (valence far-gap minus near-gap ordering accuracy +0.318).
  (Full-power numbers + CIs in `SOLVED.md`.)
- **Osgood asymmetry corroborated [PINNED positive control]:** valence (Evaluation) >> dominance (Potency) >
  arousal (Activity) is the known factor-strength order, and valence 0.698 matches the published
  SemAxis-valence literature (Hollis & Westbury; Turney & Littman) -- a positive control on the method, and the
  known fact that **arousal is the least embedding-recoverable** VAD dimension.

## 6. OUR-INVENTION-UNDER-TEST (swept, not adopted)

- The per-dimension axis construction (a-priori named seed pole-pairs; the axis = mean pole-difference). Swept
  vs the automatic best-antonym-axis-over-bank; random-axis twin controls "any projection would do."
- The gradability gate proxy (has-WordNet-antonym). The 3-way routing thresholds. The verb feature weighting
  (class-root vs thematic-role vs frame). lambda/fusion weights.

## 7. Residual-gap ledger (what is NOT solved, and why)

1. **Dimension/standard SELECTION is not built** -- we test per-named-dimension recovery, not the online
   selection of the relevant scale for an arbitrary pair. Faithful home = the semantic-control organ (buildable
   gap, not a ceiling).
2. **Denotational non-affective scales** (size, temperature, speed) are tested only via concreteness on disk;
   the pure gradable-denotational ordering golds (Wilkinson/CROWD) are the follow-up, WordNet-independent test.
3. **Arousal** is genuinely weakly recoverable from static embeddings (a representation limit of the supply,
   not the op) -- a fidelity boundary, honestly reported.
4. **Opposition** is read here from the relation-anchored axis (geometric position) rather than from the
   explicit relational-propagation organ; the geometric-vs-relational comparison for adjectives is a named
   follow-up (the landed valence organ suggests the relational route may be sharper still).
5. **FrameNet** frames are available but sparse per verb; VerbNet class overlap carries most of the verb signal.
