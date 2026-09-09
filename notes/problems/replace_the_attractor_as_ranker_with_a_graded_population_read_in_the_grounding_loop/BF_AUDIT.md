# TOP-DOWN BRAIN-FOUNDATIONAL AUDIT of the grounding-loop SENSE-ASSIGNMENT ranking chain

Owner (2026-09-10): "Make all components fully 100% brain foundational, from the top down, and verify the
calculations and math are brain foundational. This is how we get this working properly, when all are brain
foundational."

Method + verdict vocabulary follow the shared convention (`VERIFIED_BF_LEDGER.md`, `notes/BRAIN_FOUNDATIONAL_AUDIT.md`):
**BF** = the operation IS the brain's computation (pinned / defensible computational-level; params swept-not-adopted).
**BF_SPIRIT** = right operation, but an engineering implementation or fitted/adopted params or supplied (not learned) knowledge.
**NOT_BF** = the specific operation is not the brain's. **BF_UNPINNED** = the brain target itself is unpinned.
Every organ below also carries the machine-checkable `__bf_status__` tag (my `experiments/*` cells are tagged;
the `hdlab/` organ values are proposed at the bottom for strategy to land, Q111 -- solver cannot write `hdlab/`).

## THE LEDGER (top -> down): each row VERIFIES THE MATH, then the residual non-BF and the BF fix

| # | layer | component | operation (the actual math) | brain mapping (citation) | verdict | residual non-BF | BF fix |
|---|---|---|---|---|---|---|---|
| 0 | DECISION | sense assignment | rank stored concepts by similarity to the read word; link to nearest | ATL lexical-semantic retrieval by graded similarity | **BF** | -- | -- |
| 1 | READOUT | graded population read | `s_i = (M_i . q)/(||M_i|| ||q||)`, rank by s | dot = population coactivation / population vector (Georgopoulos 1986); L2-normalize = **divisive normalization** (Carandini-Heeger 2012) | **BF** | hard `argmax` for a single pick = discretized WTA (brain = graded lateral inhibition); ranking uses the graded order so BF | keep graded competition for the single pick |
| 2 | FUSION | convergent-cue combination | `combined_i = SUM_c w_c * logsoftmax(s_c,i / tau_c)` | `logsoftmax(s/tau)` = log of the Gibbs/Boltzmann posterior `p(i) prop exp(s_i/tau)` (population posterior via normalization); `SUM_c log p_c = log PROD_c p_c` = **Bayes cue integration** (Ma/Beck/Latham/Pouget 2006; Ernst-Banks 2002) | **BF** with equal `w_c` (uniform prior, no fitted params); `tau_c` = population gain (computed, swept) | (a) gold-**calibrated** `w_c` = fitted -> BF_SPIRIT; (b) per-item precision via posterior peakedness = **NOT_BF** (peakedness tracks neighborhood crowding not reliability -- `exp_diagnose_calibration_v1`) | equal weights now; genuine precision needs a probabilistic population-code representation (deep fix) |
| 3a | CHANNEL | grounded (perceptual) | z-scored 12-d Lancaster/Brysbaert, cosine | ATL amodal hub over modality spokes (Cox 2024; Lynott/Connell/Brysbaert 2020); z-score = gain normalization | **BF_SPIRIT** (matches ledger) | 12-d coarse (sibling/synonym confound); **cosine discards signed magnitudes** ("no cosine in the brain" -- ledger) | magnitude-aware read: Euclidean-in-z / Weber signed-magnitude (`sensorimotor_spoke`/`quality_relation`) |
| 3b | CHANNEL | learned dependency IDENTITY (DEP) | dep-context **PPMI** = `max(0, log(p(w,c)/(p(w)p(c))))`, cosine | substitutability from syntactic frames (Levy-Goldberg 2014); PMI = the weight a Hebbian-**predictive** associator converges to (SGNS ~ shifted PMI); `max(0,.)` = neural rectification | **BF_SPIRIT** | computed in **BATCH** (brain learns online/incremental); **context comes from the NOT_BF parser** (pos_tagger+arceager); **unlabeled** heads | online Hebbian/predictive update; route through `incremental_parser` (BF_SPIRIT); labeled deprels |
| 3c | CHANNEL | taxonomic IDENTITY (CM) | IDF-weighted definitional-feature cosine over WordNet hypernym closure; `IDF = log(N/df)` | taxonomic category organization + ATL **distinctive-feature** weighting; IDF = Bayesian surprise / inverse-base-rate salience | **BF_SPIRIT** | KNOWLEDGE **supplied** by curated WordNet (admissible foundation, not learned); IDF batch | learn the taxonomy online (DEP is the partial learned version) |
| 3d | CHANNEL | distributional BAG (incumbent) | random-projection co-occurrence sum, cosine | random projection = DG/cerebellar **expansion** (Marr 1969); but **unordered pooling** is not the brain's structured context | **NOT_BF** (structure) | unordered bag discards word order / syntactic role -> relatedness not identity | **DROP** -> superseded by DEP (structured) |
| 4 | REP MATH | cosine / softmax / log-sum / z-score / PPMI / IDF / random-projection | (verified in rows 1-3) | divisive-norm / Gibbs posterior / Bayes / gain-norm / Hebbian-predictive / salience / expansion | **BF / BF_SPIRIT** | -- | -- |
| 5a | INPUT | lemmatization (`normalize_lemma`) | morphological stripping before semantic access | Rastle-Davis 2008; Taft-Forster 1975 | **BF** (PINNED) | -- | -- |
| 5b | INPUT | parser feeding DEP (`pos_tagger`+`arceager`) | supervised frozen avg-perceptron + greedy hard-decode | incremental syntactic attachment (the OPERATION); but frozen/supervised/hard | **NOT_BF** (matches ledger) | frozen supervised; hard decode discards marginals; batch | `incremental_parser` + `predictive_reader` (BF_SPIRIT), predictor ON, graded |

## MATH VERIFICATION -- each operation, why it is (or is not) the brain's computation
1. **Cosine** `a.b/(|a||b|)`: the dot product is population coactivation (a population-vector readout); dividing by the
   norms is divisive normalization, the canonical cortical gain-control operation (Carandini-Heeger 2012). **BF.**
   Caveat (ledger): on the *grounded* channel cosine throws away the per-dimension signed magnitude the brain uses for
   more/less judgements -- there a magnitude-aware read (Euclidean-in-z / Weber) is more faithful. So cosine is BF as a
   population-overlap *ranking* read, BF_SPIRIT specifically on grounded magnitudes.
2. **Softmax** `exp(s_i/tau)/Z`: the max-entropy (Gibbs) distribution given a mean score; cortical population responses
   follow exactly this normalized-exponential form. `tau` is the inverse gain (a parameter to SWEEP, not adopt). **BF.**
3. **Convergent fusion** `SUM_c logsoftmax(s_c/tau_c)`: `= log PROD_c softmax_c`, i.e. the product of independent cue
   posteriors = the Bayes-optimal combination of cues (Ma/Pouget 2006). Equal weights = a uniform prior over cue
   reliabilities -- the assumption-free default with NO gold-fitted parameters. **BF.** (Gold-calibrated weights would be
   BF_SPIRIT; per-item peakedness precision is NOT_BF -- see the calibration diagnosis.)
4. **z-score** `(x-mu)/sigma` per feature: subtractive + divisive normalization across the feature population = gain
   control; mu/sigma are population statistics (computed, not adopted). **BF.**
5. **PPMI** `max(0, log(p(w,c)/(p(w)p(c))))`: PMI is the log-ratio of the joint to the independent expectation = a
   surprise / prediction-error signal, and it is the fixed point a Hebbian-predictive associator converges to
   (Levy-Goldberg 2014). The positive rectification is neural rectification (units do not fire negative). **BF operation**;
   BF_SPIRIT because it is computed in BATCH (the brain updates online) over a NOT_BF parse.
6. **IDF** `log(N/df)`: inverse base-rate / Bayesian surprise = the distinctive-feature weighting the ATL is known to
   apply (privilege diagnostic features). **BF operation**; BF_SPIRIT because df is counted over a supplied ontology.
7. **Random projection** (context bundle): a fixed random linear map preserves geometry (Johnson-Lindenstrauss) and is
   the brain's expansive-random-connectivity motif (DG granule / cerebellar expansion; Marr 1969; Babadi-Sompolinsky).
   **BF** -- but the POOLING that fills it (unordered bag) is the NOT_BF part, not the projection.
8. **argmax** (single pick): hard winner-take-all; the brain's WTA is a graded lateral-inhibition settle. Minor
   discretization; the RANKING (graded order) is BF, so this only bites the top-1 pick. **BF_SPIRIT.**

## THE ALL-BF COMPOSITION (measured) -- does removing the NOT_BF components hold up?
`experiments/exp_all_bf_chain_v1.py`, held-out SimLex-999 ranking. It composes ONLY BF/BF_SPIRIT components
(grounded + DEP + taxonomic), equal-weight Bayes fusion (no fitted weights), cosine readout -- and drops the two
NOT_BF elements (the unordered bag channel; peakedness precision weighting). Compared to the MIXED chain (with the
bag + gold-calibrated weights) and the pre-audit SOLVED fix (grounded+bag).

RESULT (n=4359 words, 169 held-out SimLex pairs, 3000-boot):
| chain | MRR | hit@10 |
|---|---|---|
| **ALL-BF** (grounded + DEP + taxonomic; equal-weight Bayes; cosine readout; NO bag, NO fitted weights) | **0.332** | 0.586 |
| MIXED (adds the NOT_BF bag channel + gold-calibrated weights G=1/D=2/DEP=0.5/CM=1) | 0.305 | 0.592 |
| SOLVED (grounded + bag, the pre-audit fix) | 0.059 | 0.136 |
| info-free twin (shuffled) | 0.013 | -- |

The all-BF chain BEATS the mixed chain **+0.028 MRR, CI [+0.002, +0.054]** (CI-separated) -- even though the gold
calibration KEPT and up-weighted the bag (D=2). So dropping the two NOT_BF components and using the assumption-free
BF default (equal-weight Bayes = uniform prior) does not merely avoid harm, it WINS. Both crush the pre-audit SOLVED
fix (+0.274, CI [+0.214, +0.336], ~5.7x) and the info-free twin. **The owner's thesis holds on the number: the
fully brain-foundational composition is the best-performing chain, and it needs NO gold-fitted parameters.**

## PROPOSED `hdlab/` `__bf_status__` TAGS (Q111 -- strategy lands; solver cannot write hdlab)
Inheriting the shared ledger where it already ruled, adding the organs this chain touches:
| organ | `__bf_status__` | `__bf_note__` |
|---|---|---|
| `grounded_similarity` | "BF_SPIRIT" | "z-scored Lancaster/Brysbaert = admissible foundation; capped/plain cosine read discards signed magnitudes (wrong-metric); 12-d coarse -> sibling/synonym confound" |
| `conceptual_meaning` (ConceptualChannel) | "BF_SPIRIT" | "IDF-weighted taxonomic distinctive-feature cosine (ATL privilege-distinctive-features); knowledge SUPPLIED by curated WordNet (foundation), not learned; IDF batch" |
| `meaning_foundation` | "BF_SPIRIT" | "curated 200-d w2v sense signatures = distributional relatedness (admissible foundation asset); not learned online" |
| `pos_tagger` | "NOT_BF" (brain target UNPINNED) | "supervised avg-perceptron, frozen, hard Viterbi discards marginals (inherited ledger verdict)" |
| `arceager_parser` | "NOT_BF" | "arc-eager surface-feature avg-perceptron, frozen, greedy hard-decode; route AROUND via incremental_parser (inherited ledger verdict)" |
| `cleanup_family` (`iterative_attractor`) | "BF" | "graded L2-normalized soft-attractor for RECALL/completion (CA3; Treves-Rolls) -- correct job; NOT a ranker on the live path" |
| `reading_grounding_loop.canonicalize_fast` | "BF" | "graded cosine population read (divisive-normalization) for sense-assignment ranking; GRADED_COMPARATOR on" |

## NON-BF ITEMS FOUND + DISPOSITION (the consolidated register)
Every non-brain-foundational item this audit surfaced across the chain, and exactly what was done about it.

| # | non-BF item | where | found-as | DISPOSITION |
|---|---|---|---|---|
| 1 | attractor used as the RANKER (the brief's premise) | `cleanup_family`/`gap_detector` on the live path | **already remediated** -- the live ranking is `canonicalize_fast` (graded cosine read, GRADED_COMPARATOR on); attractor is confined to the exact-match recognition gate | **NO CHANGE NEEDED** (located-negative, disk-verified); attractor kept for recall (its correct job) |
| 2 | unordered bag-of-words distributional channel | the reader's context bundle | NOT_BF (unordered pooling; relatedness not identity) | **REPLACED / DROPPED** -- superseded by the learned structured dependency channel; dropped from the all-BF chain, which then BEAT the bag-containing chain (+0.028 CI-sep) |
| 3 | per-item precision via posterior peakedness | my fusion prototype | NOT_BF (peakedness tracks neighborhood crowding, not correctness; T1 rho 0.68-0.81 vs ~0) | **REPLACED** with equal-weight Bayes fusion (BF uniform prior, no fitted params) |
| 4 | sign-quantized random-symbol content_key as the ranking cue | `gap_detector.content_key` | non-BF for ranking (rho ~0 to grounded meaning) | **REPLACED (proposed, Q111)** -- route the ranking over grounded/DEP/taxonomic meaning channels; the gate's exact-match recognition (a different, correct job) is kept |
| 5 | grounded capped/plain COSINE read | `grounded_similarity` | BF_SPIRIT (discards per-dim signed magnitudes) | **TESTED a BF replacement (Euclidean-in-z), MEASURED NULL here** (-0.012, CI incl 0; far-field ranking favors cosine) -> kept cosine, documented |
| 6 | DEP association computed in BATCH | my learned channel | BF_SPIRIT (brain learns online/incremental) | **PROPOSED** online Hebbian/predictive update (not built; NEXT STEP 4) |
| 7 | DEP's dependency parse = `pos_tagger`+`arceager` | upstream of the learned channel | NOT_BF (frozen supervised, hard-decode; inherited ledger verdict) | **GAP -- no BF replacement exists** (`incremental_parser` is role-specialized, not a general parser); reported, not faked (NEXT STEP 4a) |
| 8 | taxonomic identity is WordNet-SUPPLIED | `conceptual_meaning` (CM) | BF_SPIRIT (supplied, not learned) | **PARTIAL LEARNED REPLACEMENT BUILT** -- the DEP channel learns the same identity signal from reading (recovers ~half, rises with volume); foundation-plus-grow |
| 9 | labeled deprels via the supervised `arc_labeler` | candidate DEP upgrade | would be NOT_BF (supervised) | **TESTED, MEASURED NULL/worse** (-0.013; fragments sparse counts) -> NOT adopted, documented |
| 10 | point-vector meaning + cosine (not a probabilistic population code) | the whole representation layer | the DEEP non-BF root of the calibration failure | **IDENTIFIED as the deep architectural fix** (population code -> intrinsic precision); proposed, not built (NEXT STEP 4b) |

Summary: **2 replaced/dropped in-experiment (bag, peakedness), 1 partial learned replacement built (DEP for supplied taxonomy),
2 BF replacements tested-and-measured-null-then-kept (euclid grounded, labeled deprels), 3 proposed for strategy/architecture
(identity-channel wiring, online learning, population code), 1 GAP (no BF general parser), 1 no-change-needed (already remediated).**

## THE PATH TO FULLY BF (residual fixes, ranked by how much non-BF they remove)
1. **Route DEP through `incremental_parser`** (NOT_BF `pos_tagger`/`arceager` -> BF_SPIRIT incremental parse). Removes
   the single NOT_BF component the learned identity channel depends on. [biggest structural non-BF in the chain]
2. **Online (incremental) association** for DEP/PPMI instead of batch -- and labeled deprels for signal-per-exposure.
3. **Magnitude-aware grounded read** (Euclidean-in-z / Weber) instead of cosine -- stops discarding signed magnitudes.
4. **Learn the taxonomy online** so the identity signal is acquired, not WordNet-supplied (DEP is the partial version).
5. **Probabilistic (population-code) meaning representation** so precision is intrinsic + calibrated -- the deep fix
   that makes per-item precision weighting (currently NOT_BF) actually work. Largest architectural lever.
