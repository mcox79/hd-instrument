# Deep drill (4x): what should the CPCL learning loop predict, and is "richer corpus" real or a scapegoat?

**Filed by:** research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents, generic-terms-only per
[[feedback-query-privacy-decomposition]]). **Trigger:** direct USER deep-drill request following the CPCL
(`experiments/exp_contrastive_predictive_reader_loop_cpcl_v1.py`) build-and-run-clean-but-NULL result: the
real-vs-shuffled-continuation discriminator's relative gap margin came in at ~3.7% against a pre-registered
20% firing threshold (`contrast_fires = n_informative_pairs>=5 AND rel_gap_margin>=0.20`), diagnosed by the
cell's own author as pending-VET between (a) corpus-coarseness and (b) a deeper target/operationalization
null. Builds on, does not relitigate: `notes/drill_brain_how_it_does_it_given_failures_5x_2026-07-20.md`
(the CPCL's own design rationale — contrastive rivalry + real exogenous data as the missing ingredient) and
`notes/drill_platform_maturity_base_elements_brain_sufficient_5x_2026-07-20.md` (error-driven loop ranked
most load-bearing missing element; similarity-structured content ranked #3 build item). Lit-scan calibration
penalty applied throughout: deflate 0.15-0.25 off raw agreement; novel-synthesis capped at P<=0.50.

---

## HEADLINE

**Best predictive target: entity-recurrence/coherence (Centering-Theory / entity-grid style — does the
extracted patient/agent reappear as an argument in the next N sentences, and in what role), NOT the
bag-of-words content bundle CPCL v1 used.** This ranks #1 on both brain-fidelity and small-corpus
discriminability because repeated ENTITIES are the signal (not noise) even in a tiny reused vocabulary,
and it has a direct, well-precedented computational analog (Barzilay & Lapata 2008) already built for
exactly this real-vs-shuffled discrimination task. **"Richer corpus" is MORE LIKELY A SCAPEGOAT than a real
requirement for this specific null** — the closest, most structurally-analogous precedent in the literature
(BERT's NSP vs ALBERT's SOP) is a near-exact match: an easy-but-wrong signal (topic/lexical overlap) swamped
the hard-but-right signal (coherence), and the field's fix was changing WHAT is scored and HOW negatives are
constructed on the SAME data, not sourcing new data — graded/simplified text is independently documented to
be MORE surface-cohesive than authentic text, undermining "too repetitive" as the root cause. **The brain
does predict content during reading, but the relevant literature draws a load-bearing dissociation between
"how accurate is the single best prediction" and "how DISTINCT is that prediction from its near-competitors"**
— these can come apart (Kuperberg/Brothers et al. 2023: pre-activation of a top candidate can spread
facilitation to close alternatives rather than sharpening contrast against them), and whether this
specifically collapses in graded-reader text is an **unstudied literature gap**, not a settled finding either
way — genuinely testable, not yet answered by lit-scan. **Items (the redesigned loop target and the learned
similarity-structured codebook) converge on the SAME underlying mechanism in the literature** (skip-gram-style
"predict nearby context from a word" is simultaneously a codebook-builder and a predictive objective —
Levy & Goldberg 2014 proved this is mathematically equivalent to PMI-matrix factorization) — they should be
built as one staged mechanism (codebook first, cheap and glass-box via Random Indexing/BEAGLE-style
co-occurrence, feeding the entity-recurrence loop's `content(tok)`), not sequenced as two independent,
unrelated prerequisites.

---

## Uncertainty 1 — What should the loop predict? (target-design, most important)

**Ranked candidates (brain-fidelity x small-corpus discriminability), per parallel Sonnet lit-scan:**

1. **Entity-recurrence / coherence (Centering Theory — Grosz, Joshi & Weinstein 1995; entity-grid —
   Barzilay & Lapata 2008).** Best combination: a mature, formally-specified theory of what should recur
   and in what grammatical role, AND a directly-precedented computational operationalization for exactly a
   real-vs-shuffled discrimination task (Barzilay & Lapata's own coherence-discrimination benchmark is
   structurally the same task shape as CPCL's P1/P2). Crucially, in a small reused-vocabulary corpus,
   REPEATED ENTITIES ARE THE SIGNAL, not noise from redundant vocabulary — the opposite of what happens when
   scoring at the bag-of-words level. Deflated P=0.60 (single caveat: entity-grid's own validated task is
   full-document permutation, not clause-by-clause next-mention; some extrapolation needed).
2. **Role-structure / thematic-fit / generalized event knowledge (McRae, Ferretti, Elman; Metusalem et al.
   2012, PMC3375826).** Very strong N400 evidence comprehenders pre-activate abstract event ROLES/fillers
   before the exact word — but this literature is about INTRA-episode, within-sentence pre-activation, and
   using it cross-sentence needs a working role-extractor already (circular relative to the substrate's own
   extractor gap). Deflated P=0.50, flagged: Metusalem et al. 2012 is doing a lot of the evidentiary work
   here and should be treated as one strong-but-singular data point.
3. **Event-boundary / situation-dimension continuity (Zwaan Event-Indexing Model; Zacks & Swallow Event
   Segmentation Theory).** Strong, well-replicated theory (5 situation dimensions: space/time/protagonist/
   causality/intentionality) but LOW BANDWIDTH (near-binary continuity per dimension) and presupposes the
   same extraction machinery as #2. Deflated P=0.55.
4. **Within-sentence next-word/constituent prediction (cloze, Hale/Levy surprisal).** The single
   best-evidenced human mechanism overall, but the WRONG GRAIN for CPCL's cross-sentence design, and
   vulnerable to the identical redundancy problem (function-word/high-frequency-word dominance) unless
   entropy-filtered to content tokens. Deflated P=0.40 as a distinctive discriminator at this scale.

**Verdict:** swap CPCL's `continuation_vec` (currently an IDF-weighted bag-of-content-words bundle) for an
entity-recurrence target: does the candidate patient/agent (or a co-referent/synonym of it) reappear as an
argument (any role) in the next N sentences of the same lesson — a low-cardinality, high-signal indicator,
not a washed-out word-overlap bundle. This is a targeted re-scoring of the EXISTING CPCL harness (same
rivals, same forward-model machinery, same 3-arm discriminator), not a new architecture.

## Uncertainty 2 — Is "richer corpus" real or a repeated rationalization?

**Most load-bearing lit-scan finding of this drill:** ALBERT's NSP-vs-SOP analysis (Lan et al. 2019) is a
near-exact structural match to CPCL's null. BERT's original Next-Sentence-Prediction task conflated TOPIC
prediction (easy — negatives from a different document differ in topic, so the model wins on lexical/topic
overlap alone) with COHERENCE prediction (hard — the actual signal of interest). NSP could not solve the
harder Sentence-Order-Prediction task (same-document, swapped order) at all — near chance — while SOP-trained
models generalized fine to NSP. **The documented, working fix was changing the negative-construction/scoring
granularity on the SAME underlying corpus, not sourcing richer data.** Independently: simplified/graded ESL
text is measured (Coh-Metrix studies) as MORE surface-cohesive (more explicit reference chains, more
entity/content-word repetition) than authentic adult text — directly undermining "too repetitive = no
signal" as the root cause; repetition and cohesion are largely orthogonal to coherence-discriminability.
Deflated P=0.55-0.60 that this is primarily a scoring-design issue, not a corpus-richness issue.

**Complication (do not oversell the scapegoat call — see Uncertainty 3):** CPCL's ACTUAL shuffled negatives
are drawn from anywhere in the mining corpus (not same-document-only), and the corpus itself may be
topically homogeneous ACROSS lessons too (a children's graded reader typically recycles the same small cast
of characters/settings story-to-story), unlike BERT's Wikipedia+BookCorpus training data where different
documents are genuinely different topics. If the WHOLE corpus (not just within-lesson) shares a small,
reused set of entities, then even entity-level scoring could show a smaller-than-hoped gap — this is the one
place where a real, but NARROWER, corpus property (distinct-entity/character count across the corpus, not
raw vocabulary size or sentence count) could still be load-bearing. This is testable directly and cheaply
(see Cheap decisive test) before assuming a corpus swap is needed.

**Synthesis:** favor (b) design-choice-first: re-score at entity-recurrence level AND change the shuffle
construction to within-lesson swapped order (ALBERT's SOP fix) as the first, cheap move on the EXISTING
corpus. Only escalate to "corpus needs richer/more distinct entities" if that re-scored test still shows
`rel_gap_margin` near-zero.

## Uncertainty 3 — What does the brain actually predict, and how distinctive is it?

**Load-bearing dissociation, well-evidenced:** entropy (how peaked the probability distribution over
continuations is) and semantic distance between competing candidates are FORMALLY SEPARABLE constructs
(Lowder et al. 2018, *Cognitive Science*: surprisal and entropy-reduction make independent, dissociable
contributions to reading times) — "how predictable is the right answer" and "how DIFFERENT is the right
answer from the plausible wrong ones" can come apart. Direct supporting evidence: Brothers, Morgan, Yacovone
& Kuperberg (2023, *Cognition*, PMC10783882) found that when a context supports two plausible continuations,
pre-activating the top candidate produces FACILITATION (not competitive interference) on a lower-probability
but semantically-related alternative — i.e., the brain pre-activates a COHORT of similar candidates rather
than one isolated point, and similarity among candidates blurs contrast rather than sharpening it. This is
a genuine, if indirect, evidentiary basis for "a narrow, formulaic vocabulary could produce HIGH average
predictability (children's text is plausibly more cloze-predictable, formulaic-language literature) while
simultaneously producing LOW inter-candidate contrast (all plausible continuations cluster tightly in a
small semantic space)" — these are NOT mutually exclusive.

**Honest gap (flagged, not smoothed over per [[feedback_strategic_reads_run_ahead_of_evidence...]]):** no
retrieved source directly measured cloze-probability distributions or entropy/semantic-distance dissociation
specifically in graded-reader/simplified-text corpora vs. authentic narrative. This is an UNSTUDIED gap in
the literature, not a settled finding in either direction — deflated P=0.35 on the "graded-reader text
specifically collapses inter-candidate contrast" extrapolation (vs. P=0.60 on the underlying formal
entropy/semantic-distance dissociation itself, which IS well-established).

**Adjudication of Uncertainty 2:** this is a genuine, partial counterweight to the "scapegoat" call above —
it means a small residual risk exists that even a correctly-designed entity-recurrence scorer could show a
weaker-than-hoped contrast on THIS specific corpus, if the corpus's distinct-entity/character diversity is
itself very low. The honest position: run the entity-recurrence + within-lesson-shuffle redesign FIRST
(cheap, reuses the existing harness); only if IT ALSO shows near-zero `rel_gap_margin` does this drill's
finding shift toward "corpus's entity diversity is the real, narrower bottleneck" (not "richer corpus" in
general, but "more distinct recurring entities/characters specifically").

## Uncertainty 4 — Learned similarity-structured codebook (glass-box, no external LLM)

**Brain-side:** distributional/co-occurrence statistics alone (no sensorimotor grounding required) predict a
substantial share of human semantic similarity structure — LSA cosines predict semantic-priming reaction
times (Günther et al. 2016); Mitchell et al. (2008, *Science*) showed a pure co-occurrence-feature model
predicts fMRI activation for novel nouns at ~0.77 accuracy. Grounding/experiential similarity adds real,
independent variance on top (Andrews/Frank/Vigliocco "Primacy of Experience" lineage) but is not required to
get most of the way there — consistent with, and reinforcing, the prior drill's "grounding demoted to
sufficient-not-necessary" finding. Deflated P=0.55-0.60.

**Glass-box construction path — a real, precedented, VSA-NATIVE option:** Random Indexing (Kanerva;
Sahlgren) and BEAGLE (Jones & Mewhort 2006/2007) are fully transparent, non-black-box distributional-semantics
methods built from EXACTLY the substrate's own primitives — fixed random context/index vectors, similarity
structure emerging purely from SUPERPOSITION (bundling) of co-occurring contexts (BEAGLE additionally uses
circular convolution/binding for order information). This is a direct, existing precedent for building
similarity-structured content vectors NATIVELY from raw corpus co-occurrence, with no need to import
GloVe/word2vec (though Levy & Goldberg 2014 show skip-gram-negative-sampling is itself mathematically an
implicit PMI-matrix factorization — an auditable, fixed objective over count statistics, arguably glass-box
by degree even as a dense-matrix artifact). Deflated P=0.60-0.65 that this is a legitimate, buildable,
brain-consistent, no-external-LLM path.

**Convergence with Uncertainty 1 (the load-bearing cross-thread finding of this drill):** word2vec-skipgram's
training objective — "predict nearby context words from the current word" — IS SIMULTANEOUSLY a codebook
builder and a predictive-coding-style learning signal; a large-scale N400 study (ScienceDirect,
count-based-vs-prediction-based embeddings) found prediction-based models fit N400 data BETTER than
pure-count models, consistent with the brain's own predictive-error mechanism being what shapes the
similarity space in the first place (not a separate downstream consumer of an already-built codebook).
Deflated P=0.45-0.50 (capped, novel-synthesis): the loop (Uncertainty 1's redesigned entity-recurrence
target) and the codebook (this uncertainty) are plausibly the SAME underlying learning mechanism at
different grains — word-level local-context prediction (skip-gram-style, cheap, glass-box, buildable now)
naturally builds the similarity-structured `content(tok)` vectors CPCL currently gets from random bipolar
seeds, WHILE a separate, coarser entity-recurrence-level predictive loop (this drill's Uncertainty-1 answer)
rides on top of those better vectors. These are complementary, not competing, and the literature favors
building the codebook FIRST (cheap, well-precedented, does not require solving Uncertainty 2/3 first) then
feeding it into the redesigned entity-recurrence loop, rather than requiring simultaneous joint construction
from scratch. A real, separate corpus-SCALE caveat applies here (distinct from Uncertainty 2's corpus-content
caveat): co-occurrence-based methods classically need enough TOKENS to stabilize statistics (LSA/skip-gram
corpora are typically much larger than a small graded-reader mining set) — RI/BEAGLE degrade gracefully but
not losslessly at small scale, so this should be measured empirically on the actual mining corpus size, not
assumed either way.

---

## Cross-thread synthesis

This drill sharpens, and partially revises, the prior 07-20 drills' framing: `drill_brain_how_it_does_it...`
correctly identified "contrastive rivalry + real exogenous data" as the missing ingredient, but did not
specify WHAT the real-data target should represent — this drill's answer is entity-recurrence/coherence, not
bag-of-words content, and the CPCL cell's own null result (3.7% vs 20% needed) is now mechanistically
explained by the SAME failure mode ALBERT diagnosed in BERT's NSP: an easy/wrong signal path (lexical/topic
overlap in the IDF-weighted content bundle) swamping the hard/right one (entity/coherence transitions).
`drill_platform_maturity...`'s item-3 ranking (similarity-structured content vectors, "architectural slot
exists, not populated") is directly actionable here: Uncertainty 4 supplies a concrete, glass-box, brain-
precedented construction method (Random Indexing / BEAGLE) that was previously left as "needs a real
embedding source" — this drill's answer is: build it FROM THE SAME MINING CORPUS via the substrate's own
bind/bundle ops, no external LLM, no GloVe dependency required (GloVe currently enters CPCL only as the
SHARED base teacher across all arms, per the cell's own docstring — this drill's codebook proposal would
apply to `content(tok)` specifically, the tested predictive signal, not the shared base). The standing
"richer corpus, multiple times invoked" pattern (chain-grade-needs-real-data, density-thread, now CPCL) gets
a genuine, if partial, correction: this drill's literature-based read is that MOST of the CPCL null is a
scoring-design artifact (fixable on the SAME corpus, cheaply, first), with only a narrower, unverified
residual risk (distinct-entity/character diversity specifically, not vocabulary size generally) that would
require new/different corpus content — the density-thread's own prior conclusion ("densification necessary-
but-insufficient, reader walls are structural not data") is CONSISTENT with, not contradicted by, this
drill's redirect toward scoring-design-first.

---

## Cheap decisive test

Reuse the EXISTING CPCL harness (`exp_contrastive_predictive_reader_loop_cpcl_v1.py`) unchanged except for
TWO isolated swaps, tested independently then jointly (one variable at a time, per the cell's own
design-gate discipline):

**Test A (Uncertainty 1+2, cheapest, do first):** Replace `continuation_vec`'s IDF-weighted bag-of-content-
words target with an entity-recurrence indicator: for each rival candidate patient/agent, does it (or its
WordNet/coref-resolved synonym, already available in the LCCP scaffold) reappear as ANY argument (V/A/P role)
in the next N sentences of the same lesson. Re-run the SAME 3-arm discriminator (CONTRAST/ABSOLUTE/SHUFFLED)
on the SAME corpus/gold slice. Also swap the shuffle construction from corpus-wide derangement to
within-lesson-only swapped order (kills the topic-overlap shortcut per ALBERT's SOP fix). Cost: re-target one
function, re-run the existing cell at smoke scale (~minutes).

**Test B (Uncertainty 4, second, only if Test A improves but doesn't fully clear the 20% threshold):**
Replace `build_content_vectors`'s random bipolar seeds with Random-Indexing-style vectors built by
superposing fixed random context-index vectors over the SAME mining corpus's co-occurrence windows (BEAGLE-
style bundle-only construction — cheap, no SVD, no external embedding). Re-run the same 3-arm harness with
Test A's entity-recurrence target ALSO in place (joint test, since the literature suggests these are the
same underlying mechanism at different grains).

**HARD-PASS (Test A alone):** `rel_gap_margin >= 0.20` (the existing pre-registered `contrast_fires`
threshold) fires with entity-recurrence scoring + within-lesson shuffle, where bag-of-words scoring did not
(3.7%) — confirms Uncertainty 2's "scapegoat" call and Uncertainty 1's target-ranking, no corpus change
needed.

**HARD-FAIL (Test A alone):** `rel_gap_margin` stays below ~10% even with entity-recurrence scoring and
within-lesson shuffle — would falsify the "design-not-corpus" call and shift the diagnosis toward
Uncertainty 3's residual risk (this specific corpus's distinct-entity/character count is itself too low,
a narrower and more surprising finding than the original "vocabulary too small" framing, worth its own
dedicated drill into entity-diversity metrics of the actual mining files).

**HARD-PASS (Test B, joint):** adding the Random-Indexing codebook on top of Test A's entity-recurrence
target measurably increases `rel_gap_margin` further AND improves the P3 learning-curve slope (held-out
precision moving with more mining data), consistent with Uncertainty 4's "same mechanism, different grain"
synthesis.

**HARD-FAIL (Test B, joint):** no measurable improvement over Test A alone — would mean the codebook and the
entity-recurrence loop are NOT the same mechanism at different grains (a real correction to this drill's
Uncertainty-4 cross-thread synthesis, which is explicitly novel-synthesis-capped at P<=0.50 and the least
certain claim in this note).

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered before running)

**P1 (target redesign, the crux).** P=0.55 (deflated). HARD-PASS: Test A's `rel_gap_margin >= 0.20` AND
`P[CONTRAST] > P[ABSOLUTE]` AND `P[CONTRAST] > P[SHUFFLED]` per the cell's existing verdict bands. HARD-FAIL:
`rel_gap_margin < 0.10` — reproduces the null with a different scoring target, meaning bag-of-words was not
the (or not the only) problem.

**P2 (corpus-scapegoat call).** P=0.50 (deflated; ALBERT precedent is strong but the analogy to a
topically-homogeneous small corpus is not perfect, per Uncertainty 2's own complication). HARD-PASS: Test A
alone (no corpus change, no codebook change) clears the 20% threshold. HARD-FAIL: Test A fails AND a
follow-up entity-diversity audit of the mining corpus shows genuinely low distinct-character/entity count
(<~10-15 recurring named entities across the whole mining set) — would confirm richer corpus (specifically:
more distinct entities, not more tokens or more vocabulary) is in fact required for THIS specific mechanism.

**P3 (codebook-loop joint mechanism).** P=0.42 (deflated, novel-synthesis-capped per
[[feedback-lit-scan-calibration-penalty]] — no single cited source combines skip-gram-equivalence and
entity-recurrence contrastive scoring in one package). HARD-PASS: Test B's joint construction beats Test A
alone on both `rel_gap_margin` and the P3 learning-curve slope. HARD-FAIL: no joint improvement — codebook
and loop are separable, sequence-independent components, not one mechanism.

---

## Substrate-product implications

Not a publication angle. The practical payoff: a SPECIFIC, cheap, two-step re-run of the CPCL cell that
does NOT require new corpus acquisition before the first test — re-target the scoring function to
entity-recurrence and change the shuffle construction to within-lesson (both ~1-function-level edits reusing
the existing harness, arms, and discriminator machinery), and run that BEFORE deciding whether a richer
corpus is genuinely needed. If HARD-PASS, this closes the CPCL null with a design fix, not a data-acquisition
detour, and gives the substrate its first working self-supervised, real-exogenous-data, contrastive learning
signal (the single most load-bearing missing element per the prior 07-20 platform-maturity drill) at near-zero
additional cost. If HARD-FAIL, the honest next step is a narrow, targeted entity-diversity AUDIT of the
existing mining corpus (count distinct recurring characters/entities, not vocabulary size) before deciding
whether a NEW corpus is required — and if so, what SPECIFIC property (distinct-entity count) it must have,
rather than a vague "richer/bigger" requirement repeated for a fourth time this session. The codebook
proposal (Random Indexing / BEAGLE-style, glass-box, built from the substrate's own bind/bundle ops on the
SAME corpus) directly answers the standing platform-maturity item-3 gap ("architectural slot exists, not
populated") with a concrete, brain-precedented, no-external-LLM construction method, ready to build
independent of how P1/P2 resolve.

---

## Citations (verified count)

**~28 distinct primary/named sources** across 4 parallel live lit-scans (author/year/venue as reported by
each sub-agent):

Target design: Zwaan, Langston & Graesser 1995; Zwaan & Radvansky 1998 (Event-Indexing Model); Zacks &
Swallow (Event Segmentation Theory); Kurby & Zacks 2008; Grosz, Joshi & Weinstein 1995 (Centering Theory);
Barzilay & Lapata 2008 (entity-grid coherence, *Computational Linguistics*); Metusalem et al. 2012
(PMC3375826, generalized event knowledge N400); McRae et al. 2005 (thematic-fit expectancies); Hale 2001,
Levy 2008 (surprisal); 2024 predictability-effects review (*Psychonomic Bull. & Rev.*); PNAS 2201968119
(hierarchy of linguistic predictions).

Corpus richness: McNamara et al. (Coh-Metrix); ESL simplified-text cohesion study (ERIC EJ1098661); Lan et
al. 2019 (ALBERT, NSP-vs-SOP); Barzilay & Lapata (entity grid, coherence-discrimination task); Gao, Yao &
Chen 2021 (SimCSE); word2vec negative-sampling lineage; dense-retrieval hard-negative-mining literature
(DPR-lineage).

Brain prediction distinctiveness: Taylor 1953 (cloze); Kutas & Hillyard (N400); Hale (entropy-reduction
hypothesis); Lowder, Choi, Ferreira & Henderson 2018 (*Cognitive Science*, entropy/surprisal dissociation);
DeLong et al. (anticipatory N400, article-form prediction); Nieuwland et al. (multi-lab non-replication);
Brothers, Morgan, Yacovone & Kuperberg 2023 (*Cognition*, PMC10783882, cohort pre-activation/facilitation);
formulaic-sequence processing lineage.

Learned codebook: Landauer & Dumais (LSA); Günther et al. 2016 (LSA-cosine priming fit); Mitchell et al.
2008 (*Science*, fMRI from co-occurrence features); Andrews/Frank/Vigliocco "Primacy of Experience" lineage;
Kanerva; Sahlgren (Random Indexing); Jones & Mewhort 2006/2007 (BEAGLE); Pennington, Socher & Manning 2014
(GloVe); Levy & Goldberg 2014 (skip-gram-negative-sampling = implicit PMI factorization); Baroni, Dinu &
Kruszewski 2014 ("Don't Count, Predict!"); count-vs-prediction-based N400 fit study (ScienceDirect
S0301051125000973); HDC/VSA survey (Kleyko et al.).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all P values above are already-deflated (0.15-0.25 off raw
literature agreement). The single novel-synthesis claim (Uncertainty 4's "loop and codebook are the same
mechanism at different grains," P3 above) is capped at P<=0.50 — no cited source combines skip-gram-
equivalence with entity-recurrence contrastive scoring in one package; this is this drill's own cross-
literature inference, flagged as such, not a settled consensus. Uncertainty 3's "graded-reader text
specifically collapses inter-candidate contrast" is explicitly flagged as an UNSTUDIED GAP (P=0.35), not a
literature-confirmed finding — treated here as a testable hypothesis informing Test B's design, not as
established fact informing the corpus-scapegoat verdict in Uncertainty 2.

---

## VERDICT (one line)

**The best predictive target is entity-recurrence/coherence (Centering/entity-grid), not bag-of-words
content; "richer corpus" is more likely a scapegoat than a real requirement for THIS null (ALBERT's NSP-vs-
SOP precedent is a near-exact structural match — the fix is scoring-design, not data-acquisition), with a
narrower, unverified residual risk that this specific corpus's distinct-entity/character diversity (not
vocabulary size) could still matter; the brain's own prediction is genuinely distinctive-vs-competitors only
sometimes (entropy and semantic-distance-between-candidates are separable, and whether graded-reader text
collapses the latter is an open, testable, currently-unanswered question); and the redesigned loop
(entity-recurrence target) and the learned similarity-structured codebook (Random-Indexing/BEAGLE-style,
glass-box, no external LLM) are plausibly the SAME mechanism at different grains per skip-gram=PMI-
factorization equivalence, and should be built as one staged sequence (codebook first, cheap and
corpus-native) rather than two independent prerequisites — both changes are cheap, reuse the existing CPCL
harness untouched otherwise, and should be tested (Test A then Test B) BEFORE any new corpus is sourced.**
