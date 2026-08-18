# exp_crossview_convergence_hub_v1: the negative is REAL, and the apparent partial success is RANK REDUCTION

Research drill, 2026-08-18. Target: `experiments/exp_crossview_convergence_hub_v1.py`,
`data/exp_crossview_convergence_hub_v1/metrics.json`,
`preregs/2026-08-18_crossview_convergence_hub_v1.md`.

New measurement made by this drill: `tools/rank_matched_null_dissociation.py` (durable, read-only;
it rebuilds the cell's own 202-row surviving population off disk and ASSERTS the reconstruction --
242 -> 202 rows and 3,064 fit words both matched, and the incumbent store re-scored to 0.0603,
identical to the landed arm. That triple match is what licenses everything below).

---

## 1. FAIR-TEST VERDICT: LEGITIMATE NEGATIVE. Two sub-claims must be RETRACTED.

The negative stands and is safe. No leak, no construction error. Verified independently:
group-disjoint held-out split (eval words excluded from SVD basis, feature vocabulary, CCA, ridge,
lam and k* selection; assertion present and passing), feature vocabulary built from fit words only,
regression gate reproducing the landed incumbent (0.0710 +/- 0.006), L0 licensing passing
(KNOWN_ANSWER 0.9612, RANDOM at chance, all four floors at chance), 41 arms with 41 distinct
digests, deterministic SVD/CCA asserted bit-identical, neither trap firing. The population and the
incumbent baseline were re-derived off disk by this drill and matched exactly.

**What must be retracted is the reading "the shared component moved us from 0.06 to 0.31 -- it
genuinely strips co-occurrence".** It does not. The instrument's incumbent baseline sits FAR BELOW
0.5, so destroying information moves the score UP toward 0.5. The entire interval (0.06, 0.50) is
reachable by degradation alone, and the cell's battery contains no control that separates
extraction from degradation.

Measured now (`tools/rank_matched_null_dissociation.py`, 200 reps, identical 202-row population,
random projections of the incumbent store that have NEVER SEEN the definitional channel):

| rank k | AUC of a RANDOM k-dim projection | landed arm at that rank |
|---|---|---|
| 2 | 0.4127 [p05 0.3651, p95 0.4596] | |
| 4 | 0.3661 [0.3261, 0.4156] | |
| **8** | **0.3079 [0.2697, 0.3495]** | **HUB_CCA_BOTH = 0.3129 (k\* = 8)** |
| 16 | 0.2426 [0.2082, 0.2798] | MAIN_COUNTS_DEF HUB_CCA_BOTH = 0.3095 (k\* = 15) |
| 32 | 0.1770 [0.1451, 0.2064] | |
| 64 | 0.1207 [0.0995, 0.1400] | |
| 128 | 0.0798 [0.0678, 0.0919] | |
| 256 | 0.0536 (= centred full rank) | raw store 0.0603 |

Centring alone reads 0.0536, so this is RANK, not centring.

**The primary arm (0.3129) sits inside the p05-p95 band of a random 8-dimensional projection
(0.2697-0.3495).** The whole reported movement is accounted for by rank.

Worse, on the pipeline-matched null -- identical whitening, identical rho weights, identical
k\* = 8, only the DIRECTIONS randomised -- random directions score **higher** than the
cross-view-selected ones:

- `HUB_CCA_X` landed 0.2458; random-direction null 0.3312 [0.2869, 0.3745]; **100% of 200 random
  draws beat the real arm.**
- `HUB_CCA_BOTH` landed 0.3129; random-directions-plus-an-information-free-addend null 0.4137
  [0.3732, 0.4604]; **100% of draws beat the real arm.**

So the cross-view-predictable directions are *more* co-occurrence-loaded than an arbitrary
subspace, and the definitional-side variate drags the hub *back toward* the co-occurrence pole
relative to a random addend. There is no partial success. There is zero measured extraction, and
the direction-selection is measurably worse than chance direction-selection.

Second retraction, minor: "the definitional channel alone 0.4780" should be stated as
**0.4780 [0.4223, 0.5350], NOT SEPARATED FROM CHANCE** -- the second channel was measured at
chance before the hub was built on it.

### Was the setup guaranteed to fail? Four items, none fatal, two load-bearing.

1. **The channel-independence preflight has a CEILING but NO FLOOR.** `REDUNDANT_CROSS = 0.95`
   voids a pairing that is too similar; nothing gates a pairing that is too weakly coupled. The
   MAIN pairing measured cross_sim_r = **0.0363**, mean held-out canonical rho = **0.0910**, only
   **8 of 128** components above rho 0.10, and a ridge held-out cosine (usage -> definitional) of
   **0.0512**. The two channels are measured to be very nearly mutually unpredictable. No
   pre-registered gate could catch that before the run.
2. **The definitional channel discarded the one categorical field available.**
   `build_definitional_cache` does `bucket.update(d.definiens_lemmas)` -- the bag of ALL content
   words in the definiens (mean 27 features per word). `hdlab/definitional_extraction.py` also
   computes `Definition.head`, the GENUS term, described in its own docstring as "the answer to
   'X is a kind of ___'", and that field is thrown away. The module exists, per its docstring,
   precisely because distributional co-occurrence "is structurally unable to separate 'X means Y'
   from 'X occurs near Y'". A bag of definiens words puts "occurs near Y" straight back in, inside
   the definition. This is the single choice most likely to have produced a topical second channel.
3. **Hyperparameter selected at the GRID BOUNDARY.** `lam_rel = 1.0` is the largest value in
   `CCA_LAM_GRID` and was selected in 3 of 4 pairings with the held-out objective still climbing
   (MAIN_STORE_DEF: 0.0669 -> 0.0670 -> 0.0681 -> 0.0766 -> 0.0910). The ridge likewise selected
   `lam = 10.0`, the top of its grid, with held-out cosine still improving. So k\* = 8 is a lower
   bound set by a truncated search, not a measured optimum. Real, modest.
4. **The planted positive control does not exercise the actual failure mode.** In `planted_world`
   the nuisance (`Nx`, `Ny`) is drawn INDEPENDENTLY per view, so no nuisance direction is
   cross-predictable and CCA cannot smuggle it into the hub. In the real data the nuisance (topic)
   IS shared across both views -- it is the ONLY thing they share. The discriminator-fires gate
   passes, but it proves less than it claims.

**n = 202 is adequate for THIS negative** (HI = 0.3644 against BAR = 0.5510, i.e. 3.7 half-widths
clear) and **inadequate for any future near-bar arm** (HW = 0.0507 against a chance-to-bar interval
of 0.0510 -- an arm at 0.55 would be indeterminate). Any successor needs a larger population.

**Is A_DEF's 0.4780 a ceiling on anything built from it?** Not mathematically -- a projection can
amplify buried signal. Empirically it behaves worse than a ceiling: adding the definitional variate
moved the hub LESS toward chance than a random addend would, i.e. the definitional channel
contributes co-occurrence-aligned information, not orthogonal information.

**Does CCA have the degrees of freedom?** The question dissolves. At low rank the representation is
noise (random k=8 reads 0.3079); at high rank it is topic (random k=128 reads 0.0798, full rank
0.0536). There is no rank at which a linear function of these two views can clear 0.55. That is a
structural statement about the CHANNEL PAIR, not about linearity.

---

## 2. THE OBJECTIVE MISMATCH: real, correctly identified, and NOT load-bearing here.

**The difference is real, and it is mathematics, not opinion.** CCA is invariant to any invertible
linear transform of either view -- it whitens both sides, so it ignores variance entirely and will
select a low-variance direction if it correlates. A reconstruction objective is not invariant: it
weights each direction by how much of the target's variance it explains. The two provably select
different subspaces. (Note the standard subtlety: the MAXVAR/GCCA "reconstruction" formulation
reconstructs the PROJECTIONS and stays correlation-flavoured; reconstructing the RAW channel is the
PLS / cross-reconstruction-autoencoder family and is variance-weighted.)

**It is also, correctly, what the published hub-and-spoke modelling does.** Those are PDP networks
with a shared hidden layer trained by backpropagated error to regenerate attribute patterns across
modalities; the hub is that hidden layer, and it "uses information from the modality-specific spoke
regions to develop modality-invariant conceptual representations".

**But it is not the binding constraint on this shortfall.** Four reasons, in order of strength:

1. **The cell already ran the cross-reconstruction arm and it went the wrong way.** `HUB_RRR` is
   ridge from usage to definitional with the hub defined as the PREDICTED definitional vector --
   that is literally "the hub must carry enough to regenerate the other channel", in closed form.
   It read **0.1365 [0.1036, 0.1727]**, CI-separated WORSE than HUB_CCA_BOTH's 0.3129, and worse
   than its own rank-matched noise. The objective swap has been measured in its linear form.
2. **Reconstruction is variance-weighted, and the top-variance directions of both channels are
   TOPIC** -- both channels are bags of content words over the same corpus vocabulary. A
   reconstruction objective would emphasise the confound MORE than CCA does. The ridge diagnostics
   agree: held-out cosine usage -> definitional is 0.0512.
3. **There is no partial success to convert.** An objective change picks a better subspace of the
   SAME information. Here the shared information is measured to be near zero (cross_sim_r 0.0363;
   mean held-out rho 0.0910; 8 of 128 components above 0.10), and the arm is indistinguishable from
   a random projection of the same rank.
4. **In the modelling literature the explanatory weight sits on the DATA, not the loss.** What
   makes category structure differentiate in the hidden layer is COHERENT COVARIATION of properties
   -- the same ensemble of features (has wings, has feathers, can fly) recurring across many items.

**PINNED vs CONVENTION, stated explicitly.**
PINNED: the ATL acts as a transmodal hub whose representations are modality-invariant; damage to it
reproduces the semantic-dementia profile; in the computational models, category structure in the
hidden layer emerges from coherent covariation of properties. CONVENTION: that backprop through a
bottleneck IS the hub's objective. The brain does not backpropagate; that is the modelling vehicle,
and how the ATL actually computes its invariant is not settled at the algorithmic level. Treating
"reconstruction rather than correlation" as a brain-derived requirement would be mislabelling a
modelling choice as biology.

---

## 3. THE FOUR CANDIDATE DIFFERENCES, RANKED

**#1 CHANNEL FORMAT -- two spokes of the same kind. This is where the whole shortfall lives.**
Both channels are bags of content words over the same corpus vocabulary. What such bags share is
TOPIC, and topic is precisely what this instrument punishes (SET S is TOP-CO-OCCURRING pairs).
Evidence, all measured: cross_sim_r 0.0363; ridge held-out cosine 0.0512; mean held-out rho 0.0910;
A_DEF at chance; HUB_CCA_X below 100% of rank-matched random-direction draws; the definitional
addend moving the hub LESS toward chance than a random addend. A second text view is a second
SAMPLE of the same statistic, not a second MODALITY.
Corroborating published result: how the CONTEXT is defined is what decides whether a distributional
representation encodes topical relatedness or functional/co-hyponym similarity -- bag-of-words
contexts give topical similarity, typed syntactic contexts give functional similarity, and
symmetric-coordination contexts do better still. Both our channels are bag-of-words contexts.
Corroborating published result: distributional models score well on association-mixed gold sets and
far below the human ceiling on genuine-similarity gold sets. Our instrument is the
genuine-similarity case in extremis (synonyms that NEVER co-occur vs top-co-occurring associates).

**#2 WHAT SUPPLIES THE INVARIANT -- no shared referent.** The deeper reason for #1. The biological
hub's channels are anchored by a shared REFERENT: "dog" and "hound" have different strings and
different contexts but the same percept, and that identity is what makes the invariant categorical.
Two text views of a word are both about the STRING. Nothing in this design supplies the anchor.
Not directly measured here -- it is the structural explanation for the measured #1, and should be
labelled as such.

**#3 LINEARITY -- much weaker than it looks.** The failure is not a linear map missing a curved
manifold. At low rank the representation is noise and at high rank it is topic; a nonlinear
extractor searches a richer function class over two channels whose measured mutual predictability
is ~5%. Nonlinearity helps only if the shared structure is present but nonlinearly encoded, and
that has a cheap prior test: a nonlinear cross-channel predictor must beat held-out cosine 0.0512
BEFORE any hub is built on it. Recurrent settling is a real biological feature but it is a
completion mechanism, and there is nothing here to complete.

**#4 TRAINING REGIME -- least.** The closed-form fit is the global optimum of its objective on this
data; slow interleaved learning approaches the same optimum more slowly, with implicit
regularisation and protection against catastrophic interference. Neither creates information that
is absent. In the modelling literature the slow interleaved regime governs the ORDER in which
structure differentiates (broad before specific) and retention, not whether the structure is
extractable at all. Becomes relevant only once the channels demonstrably share something.

---

## 4. WHAT WOULD ACTUALLY BE DIFFERENT

### ROUTE VERDICT: the cross-view-EXTRACTOR route is EXHAUSTED. Do not build a fifth hub.

Four attempts now: `exp_self_teacher_gloss_relational_predictive_heldout_new_v1` (-0.0105),
`exp_redundancy_decorrelation_from_coherence_gate_precheck_v1` (HARD_FAIL_NO_SAFE_SECOND_VIEW),
this cell's CCA arm (indistinguishable from a rank-matched random projection, direction-selection
worse than random), this cell's RRR arm (worse still). The failure is not in the extractor and not
in the objective. It is that both channels are the same statistic.

What is NOT exhausted, and must be named or this becomes an over-generalised negative:
**no channel whose primitive is a RELATION rather than a BAG has ever been scored on this
instrument.** Every channel scored to date -- store, usage counts, corpus halves, store dim-halves,
definiens bags -- is a bag of co-occurring tokens.

### THE ONE CONCRETE CHANGE: build the second channel as the GENUS/ISA RELATION, not the definiens bag.

For each word, its second-channel vector is the sparse indicator over the GENUS HEADS asserted of
it (`extract_definitions(...).head`), optionally extended one hop to CO-HYPONYMS (other words
asserted to share a genus). Two synonyms are asserted to have the SAME genus; two top-co-occurring
associates are asserted to have DIFFERENT genera. This is the only categorical signal the codebase
owns, it needs no new corpus (the 3,646 definienda are already extracted and cached), and it is a
different FIELD of data already computed and discarded at
`exp_crossview_convergence_hub_v1.py:build_definitional_cache`.

**Run it as a MEASUREMENT before any mechanism.** Score the genus-head channel ALONE on the
identical 202-row population with all four floors recomputed on it and the rank-matched null
reported at its own rank. If its CI upper bound does not clear its own bar, the channel is empty,
no extractor of any objective or depth will produce substitutability from it, and the text-only
second-view route closes completely. That is a can-fail gate costing one script run.

**Brain justification, honestly labelled.**
PINNED: the hub's invariant is anchored to a shared referent, not a shared string; explicit
definitional/relational encoding is a fast hippocampal-relational bind, distinct from slow cortical
distributional accumulation (the CLS pair, which is `hdlab/definitional_extraction.py`'s own stated
rationale); a genus relation is a proposition about KIND, which is the categorical content the hub
is described as holding.
OUR-INVENTION-UNDER-TEST: that a text-extracted genus-head channel is an adequate stand-in for a
referent-anchored channel. It is not. It is the closest thing we own that is a RELATION rather than
a BAG, chosen because the genuinely brain-faithful move is currently unmeasurable:
`data/foundation/**` covers 11-14 of 242 rows. **The honest brain-first answer is "expand referent
coverage until a referent-anchored channel is measurable on >= 150 rows"; the genus-head channel is
the measurable stand-in in the meantime, and it should be labelled a stand-in in its own pre-reg.**

**Explicitly SHELVED with a revival criterion**, because they are the right idea and the wrong
scale: symmetric-coordination contexts ("X and Y") and typed syntactic-dependency contexts are the
two published, non-circular ways to make a TEXT channel encode substitutability rather than topic,
and the symmetric-pattern variant is reported to beat parser-derived dependency contexts. Both are
COUNT-BASED and were measured on 10^8-10^9-token corpora; our usage corpus is 34,169 sentences
(~10^6 tokens). Partitioning an already-thin count into typed slots or coordination instances
leaves nearly every pair at zero. REVIVAL CRITERION: usage corpus exceeds ~10^8 tokens. The
shelving is on DATA SCALE, not on the mechanism.

### DEFLATED PRIORS

- P(the genus-head channel ALONE clears its own recomputed bar, CI-separated) = **0.25**.
  Down: 4 prior negatives in this class; simplewiki genus heads will be dominated by weak heads
  (kind / name / term / city); 1-5 heads per word means pair overlap is rare and the AUC rides on
  few hits; SET P skews to obscure synonym pairs whose simplewiki definitions may be shallow;
  lit-scan calibration penalty. Up: it is the only categorical signal available; it targets a
  MEASURED cause rather than a guessed one; coverage will not collapse (582 of 617 eval words
  already have a definitional record and `head` is non-None by construction wherever a definition
  was extracted).
- P(a hub built on that channel clears the bar) = **0.15** -- strictly lower, since a hub adds the
  extractor's failure modes back on top.
- P(the text-only-second-channel route ever reaches the bar) = **0.15-0.20**.

---

## 5. STANDING RULE THIS DRILL EARNED (generalises beyond this cell)

**On an instrument whose incumbent baseline is BELOW chance, movement toward chance is not
evidence. A floor battery without a RANK/CAPACITY-MATCHED null cannot distinguish extraction from
degradation.** F_SCRAMBLE and F_CONSTANT_PROTOTYPE destroy the representation ENTIRELY and land AT
chance, so they bound the top of the range and say nothing about the middle; F_ORTHOGRAPHIC and
F_FREQUENCY are representation-independent. Nothing in the four asks what an arm of THIS RANK would
score with uninformative directions.

Therefore: **any arm that reduces rank must report its AUC beside the rank-matched null AT ITS OWN
RANK, and only a CI-separated CROSSING of 0.5 counts as substitutability.** Tool:
`tools/rank_matched_null_dissociation.py`. This is the same defect class as "a control that
excludes nothing is not a control" -- a control that cannot fire on the arm's actual failure mode
is not a control.
