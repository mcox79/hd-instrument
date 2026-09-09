---
problem: replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop
status: SOLVED
bar: "PASS = a brain-foundational GRADED POPULATION READ replacing the sign()+attractor as the RANKING step in the grounding-acquisition loop, that beats the incumbent attractor-as-ranker CI-separated on the loop's OWN ranking / growth-quality metric (its real live measure, not a synthetic proxy), with (a) the info-free twin (shuffled codebook / random ranker of equal size) LOSING, (b) high-degree-hub over-promotion MEASURABLY reduced (the named failure mode), and (c) the recall / recognition path (the attractor's correct job) byte-identical-or-better -- NO regression. A rigorous LOCATED NEGATIVE is a full pass IF it names, with a number, exactly why the graded read cannot beat the attractor here (e.g. the loop's ranking is already graded and the attractor only does recall, or the metric is saturated) -- quantify it."
result: "Two-part result. (1) LOCATED NEGATIVE on the brief's named mechanism: the live grounding-loop RANKING is ALREADY a graded population read (sense assignment routes through canonicalize_fast -- a cosine matvec, GRADED_COMPARATOR ON since 2026-08-14 -- NOT an attractor); the attractor is confined to the exact-match recognition GATE (gap_detector), where swapping it for a population read changes ranking fidelity by -1.4e-5 (95% boot CI [-2.9e-5,+3.4e-6], INCLUDES ZERO; n=400 queries, d=512) and hub over-promotion is ~0.02 for every arm at the gate's sharp temp (it only appears at soft temps the gate never uses: attractor rho 0.73 at temp=0.25 vs 0.995 at temp>=8). So 'replace the attractor readout' buys nothing. (2) SOLVED the real problem underneath -- the ranking's REPRESENTATION. On the loop's OWN sense-assignment ranking (canonicalize's job: rank the true synonym among the full covered vocab) against the INDEPENDENT SimLex-999 similarity gold, through the LIVE distributional channel (ConceptSpace context bundles) + the graded population read, a brain-foundational representation beats the distributional incumbent CI-separated: MRR CONVERGENT (reliability-weighted grounded+distributional fusion) 0.0812 vs incumbent 0.0241, +0.0571 CI[+0.0335,+0.0834] (ci_hw 0.0103); GROUNDED alone 0.0637 also beats it; hit@10 incumbent 0.047 -> grounded 0.154 -> convergent 0.189 (4x). Info-free twins LOSE decisively (MRR 0.0013 / 0.0009). n=4422 covered words, 169 high-sim SimLex test pairs (held-out; fusion weight w=16 calibrated on a disjoint train split), 3000-sample bootstrap. Recall/recognition path byte-identical (only the ranking's input representation changes)."
floor: "Strongest floors actually run, recomputed on each population. SENSE-ASSIGNMENT (headline, n=4422 words / 169 SimLex test pairs): the DISTRIBUTIONAL incumbent itself (the loop's live canonicalize representation) MRR 0.0241 -- the brain-foundational reps beat it CI-separated (convergent +0.0571 CI[+0.0335,+0.0834]; grounded +0.0396). INFO-FREE TWINS (shuffled rep rows) MRR 0.0013 (distributional) / 0.0009 (grounded), both CI-below their real reps. Representation-level corroboration on the same SimLex SIMILARITY gold (prior cell exp_taxonomic_vs_thematic_gold_v1, re-cited): distributional co-occurrence Spearman 0.039 vs grounded 0.245. LOCATED-NEGATIVE floors (ranking-fidelity cell, n=400, d=512): incumbent sign+attractor Spearman-to-grounded-gold 0.9855, info-free twin 0.0007; readout isolation POP-minus-ATTRACTOR -1.4e-5 CI incl 0 (NULL); live random-hash content_key -0.003."
controls: "INFO-FREE TWINS (shuffled rep-row <-> word correspondence) LOSE CI-separated in BOTH experiments -- the win carries real per-word meaning, not base-rate. HELD-OUT SPLIT: the convergent fusion weight w and the taus are calibrated on a disjoint TRAIN half of the SimLex pairs and evaluated on the TEST half (no leak). INDEPENDENT GOLD: SimLex-999 human SIMILARITY ratings are WordNet-independent and independent of every representation under test (no ground-by-X/grade-by-X). READOUT ISOLATION (attractor vs population, same format) excludes the readout as the harm (null, CI incl 0). FORMAT ISOLATION (graded vs sign, same read) attributes the residual to the sign-quantiser not the readout. TEMPERATURE SWEEP locates the attractor's harmful regime at soft temps the live gate never uses. GATE EXACT-MATCH AUC control: known/novel real-word separation stays 1.0 -- no regression to the attractor's correct recognition job. RECALL byte-identity: the proposal changes only what the ranking READS; hdlab.iterative_attractor.iterative_cleanup (recall/completion for ca3_completer + hippocampal_encoder) is UNTOUCHED (witness A4). Positive control: JL random projection preserves grounded geometry (self-test)."
files_changed: "experiments/exp_sense_assignment_grounded_vs_distributional_v1.py (SOLVED headline: loop's own sense-assignment ranking, SimLex independent gold, distributional incumbent vs grounded vs reliability-weighted convergent, twins, held-out fusion weight), experiments/exp_graded_read_vs_attractor_ranker_v1.py (located-negative: 2x2 format x readout + live-hash fidelity + gate AUC + temp sweep), experiments/exp_richer_meaning_channel_v1.py (LARGEST-DELTA follow-on prototype: adds the taxonomic/relational identity channel + curated-w2v channel, ATL-hub fusion, on the same held-out SimLex ranking), experiments/exp_learned_structured_meaning_v1.py (remaining fixes: online-LEARNED relational identity via dependency-parsed reading with the glass-box parser -- NO WordNet -- + per-item precision-weighted fusion), experiments/exp_diagnose_meaning_negatives_v1.py (RESEARCH the two negatives to mechanism: reliability-estimator-vs-correctness + oracle headroom for NEG1; exposure curve + frequency bins for NEG2), experiments/exp_diagnose_calibration_v1.py (ROOT-CAUSE of the miscalibration: T1 peakedness tracks crowding not correctness; T2 cross-channel agreement is genuine but sparse; T3 agreement-gated fix gives no lift -> precision-weighting is downstream of channel fidelity; the non-BF component is the reliability estimator + the point-vector-not-population-code representation), verification/test_graded_read_ranker.py (scaffold-free witness, 23/23: 10 disk-fact + 5 located-negative + 3 SOLVED-ranking + 3 largest-delta + 2 learned-structured checks), data/exp_sense_assignment_grounded_vs_distributional_v1/metrics.json, data/exp_graded_read_vs_attractor_ranker_v1/metrics.json, data/exp_richer_meaning_channel_v1/metrics.json, data/exp_learned_structured_meaning_v1/metrics.json. NO hdlab/ modified (Q111 -- the hdlab proposal is stated below for the strategy session to land)."
reverify: ".venv/Scripts/python.exe verification/test_graded_read_ranker.py  (18/18; disk facts + located-negative numbers + SOLVED-ranking checks). Powered headline reproducer (own-dir only): .venv/Scripts/python.exe experiments/exp_sense_assignment_grounded_vs_distributional_v1.py --mode full"
---

# What this is: the brief's fix was already on disk; the REAL fix is one rung up, and it works

**The short version.** The defect the brief names -- "an iterative attractor used as a graded similarity
RANKER over sign-quantized codes" -- is **already remediated on the current disk**: the live grounding-loop
*ranking* is a graded cosine population read, and the attractor is confined to the exact-match *recognition*
gate (its correct brain job), where swapping it out is a measured no-op. Following the protocol past that
refutation, the component that is **not** brain-foundational is one rung up -- the *representation* the
ranking reads. The live sense-assignment ranks over a distributional bag-of-co-occurrence bundle, which
carries relatedness but not the meaning-IDENTITY similarity the job needs. Reading the ranking over a
brain-foundational representation instead -- grounded meaning, reliability-weighted with the distributional
channel (the ATL amodal hub's convergent integration) -- **beats the incumbent CI-separated on the loop's
own sense-assignment ranking against an independent human similarity gold, with the info-free twin losing
and the recall/recognition path untouched.** That clears the bar.

## What signal matters, and where the chain loses it (the owner's question, answered with numbers)
The component asks "which stored concept is this word the SAME as?" -- the signal it needs is
meaning-IDENTITY similarity (synonymy / is-a), not co-occurrence relatedness. Tracing that signal up the
live sense-assignment chain (`canonicalize_fast`):

| rung | what it is on disk | brain-foundational? | carries the similarity signal? |
|---|---|---|---|
| readout | graded cosine population read (`sims = mat @ nb / norms`) | YES (Georgopoulos pop-vector; CA1 comparator) | fine -- it's the right ranker |
| code format | graded (GRADED_COMPARATOR ON); sign only in a non-default fallback | mostly (de-sign the fallback) | fine |
| **representation** | **distributional bag-of-co-occurrence context bundle** | **NO** | **THE LOSS: SimLex similarity rho 0.039** |

**The loss is at the representation, quantified on an independent human gold.** On SimLex-999 (the
WordNet-independent similarity axis) the loop's distributional channel scores Spearman **0.039** -- it
captures "appears together," not "means the same". The loop's own code admits it (reading_grounding_loop.py:2074:
*"every anchor's distributional profile is nearly the same vector"*). The grounded ATL channel scores **0.245**.

## Is everything, all the way up, 100% brain-foundational? No -- and here is the full audit
- **Readout** (graded population read; attractor reserved for recall): brain-foundational, already on disk.
- **Representation content**: NOT brain-foundational. The brain's ATL amodal hub INTEGRATES grounded
  sensorimotor experience WITH distributional/lexical input, reliability-weighted (Ma, Beck, Latham & Pouget
  2006). Ranking off co-occurrence alone is a documented simplification -- and the weaker channel for identity.
- **One rung deeper -- the grounded norms are PINNED brain-foundational** (Lancaster/Brysbaert = direct
  behavioral measurement of the ATL modality spokes; Cox et al. 2024; Lynott/Connell/Brysbaert 2020), **but
  grounded ALONE is not the brain's answer either**: it has a sibling/synonym ceiling (apple/orange ~= sofa/couch),
  and its MRR alone (0.0637) beats the incumbent but trails the fusion. Neither channel alone is sufficient;
  the brain FUSES them, and the fusion is what wins (MRR 0.0812).
- **Deepest -- context STRUCTURE** is an unordered bag-of-words; the brain uses ordered/syntactic context
  (prior finding: structured context lifts SimLex 0.075->0.112). A secondary non-brain-foundational
  simplification and the natural next lever.

**So the fully brain-foundational configuration, all the way up = the graded population read over a
reliability-weighted convergent fusion of grounded (ATL) + distributional channels, attractor reserved for
recall.** That is the arm that clears the bar.

## The measurement (loop's own ranking, independent gold)
`experiments/exp_sense_assignment_grounded_vs_distributional_v1.py` builds the LIVE distributional anchor
field exactly as the loop does (`ConceptSpace.observe(context_vector_masked(...))` over the reading corpus),
and the grounded field over the same vocab. For each SimLex near-synonym pair (human rating >= 6/10), it
ranks the true partner among the full covered vocab by the graded population read (canonicalize's cosine),
scoring MRR / hit@1 / hit@10. The fusion weight is calibrated on a disjoint train split (Ernst-Banks) and
evaluated held-out.

| arm (rank the true synonym; n=4422 words, 169 SimLex test pairs) | MRR | hit@10 |
|---|---|---|
| DISTRIBUTIONAL (the loop's live incumbent) | 0.0241 | 0.047 |
| GROUNDED (ATL) | 0.0637 | 0.154 |
| **CONVERGENT (reliability-weighted fusion) -- the fix** | **0.0812** | **0.189** |
| TWIN distributional / TWIN grounded (info-free) | 0.0013 / 0.0009 | -- |

- CONVERGENT beats the incumbent **+0.0571 MRR, CI [+0.0335, +0.0834]** (CI-separated). GROUNDED alone also
  beats it (+0.0396). Info-free twins lose CI-separated (grounded-vs-twin +0.0628 CI [+0.0402, +0.0875]).
- The calibrated weight w=16 is grounded-dominant -- the reliability weighting automatically down-weights the
  noisy distributional channel on the similarity axis, exactly the convergent-cue prediction.
- **Honest scale note:** absolute MRR is low (ranking the true synonym among 4,422 candidates is hard). The
  RELATIVE win is decisive (3.4x the incumbent, CI-separated, twin losing) and clears the bar; large absolute
  headroom remains, and it points at the next lever (structured context + richer grounding, below).

## LARGEST-DELTA FIX PROTOTYPED (owner follow-on): the taxonomic / relational IDENTITY channel
The brain-comparison named rung #1 -- the grounded channel's 12-d sibling/synonym confound -- as the
dominant remaining loss. `experiments/exp_richer_meaning_channel_v1.py` prototypes the brain-foundational fix
on the SAME held-out SimLex ranking (n=4363 words covered by all channels, 169 test pairs, 3000-boot). The
brain's ATL hub integrates grounded PERCEPTUAL experience with TAXONOMIC / relational structure (is-a category
organization; distinctive definitional features) -- synonyms share a taxonomic node, siblings do not. Adding
that channel (conceptual_meaning's IDF-weighted definitional-feature cosine = "meaning-IDENTITY"):

| arm (rank the true synonym) | MRR | hit@10 |
|---|---|---|
| CONV grounded+distributional (current SOLVED fix) | 0.072 | 0.14 |
| MEANING_FOUNDATION (200-d curated w2v; richer *distributional*) | 0.142 | 0.24 |
| CONCEPTUAL / taxonomic identity (alone) | 0.316 | 0.53 |
| **CONV_ALL -- full ATL-hub fusion (grounded+distributional+curated+taxonomic)** | **0.345** | **0.58** |
| info-free twins (shuffled) | 0.0015 | -- |

The full ATL-hub fusion beats the current SOLVED convergent **+0.273 MRR, CI [+0.215, +0.330]** (~4.8x; hit@10
0.14 -> 0.58), twins losing CI-separated. Decomposition confirms the mechanism: the richer *distributional*
code (meaning_foundation) adds only +0.069 (relatedness), while the *taxonomic* code adds +0.244 -- **the
missing signal is relational IDENTITY, not distributional richness**, exactly as the sibling/synonym theory
predicts. HONEST CAVEAT: the taxonomic channel reads WordNet-derived distinctive features (an admissible
offline FOUNDATION asset; taxonomic organization is brain-foundational -- ATL), and WordNet partly encodes the
target synonymy, so this PROVES THE LEVER rather than delivering the final brain-foundational end-state. The
fully brain-foundational version LEARNS that relational structure online from reading (the learner/knowledge
north-star), rather than reading it from a curated ontology. The gold is human/WordNet-independent (SimLex)
and the shuffled twin loses, so the signal is real, not an ontology artifact.

## REMAINING FIXES PROTOTYPED (owner: "do all, brain foundationally, right not easy")
`experiments/exp_learned_structured_meaning_v1.py`, same held-out SimLex ranking (n=4359 words, 169 test
pairs, 33,841 corpus sentences PARSED BY THE SUBSTRATE'S OWN GLASS-BOX PARSER -- pos_tagger + arceager, NO
WordNet, NO external tool -- 3000-boot):

**FIX 1+2 (online-learned relational IDENTITY via structured context) -- WIN, and it removes the WordNet
caveat for about half the signal.** The brain learns identity from SUBSTITUTABILITY (which words fill the same
syntactic slot; Levy & Goldberg 2014). Building a dependency-context PPMI vector per lemma from parsed reading:

| arm (rank the true synonym) | MRR | hit@10 |
|---|---|---|
| DISTRIBUTIONAL bag (incumbent) | 0.024 | 0.05 |
| CONV grounded+bag (the SOLVED fix) | 0.072 | 0.14 |
| DEP -- learned dependency identity (NO WordNet) | 0.133 | 0.24 |
| CONV grounded+bag+DEP (learned, NO WordNet) | 0.157 | 0.29 |
| CONV grounded+bag+CM (WordNet-taxonomy ceiling) | 0.314 | 0.56 |
| info-free twin (DEP shuffled) | 0.0007 | -- |

DEP beats the bag incumbent **+0.108, CI [+0.066, +0.154]** (~5.5x); grounded+bag+DEP beats the SOLVED fusion
**+0.084, CI [+0.046, +0.127]**, twin losing. So the identity signal CAN be LEARNED from reading with the
substrate's own parser -- no ontology. It recovers **~half** the WordNet ceiling (0.157 vs 0.314; the learned
fusion is CI-BELOW the ceiling, -0.157 [-0.223,-0.097]). The honest remaining gap is (a) READING VOLUME (34k
sentences is far below a human's exposure -- this is the grow-by-reading north-star, exposure-limited by
construction) and (b) I used UNLABELED heads+direction, not labeled deprels (a richer structured context).

**FIX 3 (per-item precision-weighted fusion; Ma/Pouget automatic gain) -- NULL (located negative).** Replacing
the global fusion weight with per-query reliability (posterior concentration ^ gamma) gave EXACTLY +0.0 over
global/equal weighting (calibration drove gamma->0; equal weighting already suffices on this task). The
principle is brain-foundational; this concentration-based instantiation added nothing here. Not landed.

## RESEARCHING THE NEGATIVES (owner: "research those negatives to fully understand -> further improvement")
`experiments/exp_diagnose_meaning_negatives_v1.py` (n=4359 words, 169 test pairs, 33,841 parsed sentences).

**NEG 1 (per-item weighting = null) -- fully explained: the reliability estimator does not track correctness.**
Spearman(per-query estimator, per-query reciprocal-rank) is ~0 for every within-channel confidence signal
(concentration/margin/zscore/neg-entropy; |rho| <= 0.15, best = taxonomic neg-entropy 0.148). A channel being
CONFIDENT for a query says almost nothing about whether it is RIGHT. Headroom is also modest: oracle per-query
channel-selection MRR = 0.408 vs best single channel 0.324 vs fusion ~0.335, and SELECTING by any estimator
(0.24-0.31) falls BELOW always-taxonomic.

**NEG 1 ROOT CAUSE -- IS IT A NON-BRAIN-FOUNDATIONAL COMPONENT? YES, nested (exp_diagnose_calibration_v1.py).**
(T1) The reliability ESTIMATOR is the culprit, not the meaning channels: within-channel peakedness correlates
with neighborhood CROWDING (grounded 0.81, DEP 0.68, CM 0.20) but NOT with correctness (0.10 / 0.00 / 0.13).
"Confidence" here just measures how isolated a word's nearest neighbour is in one channel's geometry -- a
hand-built heuristic standing in for a genuine precision signal. The brain never estimates precision this way; a
probabilistic population code carries reliability INTRINSICALLY (inverse variance; Ma/Pouget 2006), calibrated
by experience. (T2/T3) The brain-foundational reliability signal -- cross-channel CONVERGENT AGREEMENT -- IS
genuine (consensus hit@1 rises 0.084 at agree=1 -> 0.231 at agree=2) but too SPARSE to help: the 3 channels
agree on the top candidate only ~8% of the time (14/169), so agreement-gating gives NO lift (0.213 vs equal
0.213; shuffled control 0.201). ROOT: meaning is a DETERMINISTIC POINT VECTOR + cosine, not a PROBABILISTIC
POPULATION CODE -- a point vector has no intrinsic uncertainty and cosine is a similarity, not a calibrated
posterior, which is exactly why peakedness tracks geometry not correctness, and why individually under-developed
channels do not converge. CONSEQUENCE: per-item precision weighting is NOT an independent lever -- it is
DOWNSTREAM of channel fidelity (precision/agreement only becomes usable once each channel carries calibrated
uncertainty AND is good enough to converge). This DE-prioritizes a cleverer weighting scheme and RE-confirms the
single real priority: raise each channel's fidelity (NEG-2). The genuinely brain-foundational calibration fix is
a probabilistic (population-code) meaning representation, not a reweighting -- a larger architectural lever.

**NEG 2 (learned DEP recovers ~half the ceiling) -- fully explained: EXPOSURE VOLUME, not a ceiling.**
(i) Exposure curve -- DEP MRR is still RISING at the full corpus: 0.032 (25%) -> 0.061 (50%) -> 0.064 (75%) ->
0.096 (100%), steepest in the last quarter. (ii) Frequency bins -- the DEP<CM deficit is entirely at
LOW-frequency words: DEP MRR climbs 0.050 -> 0.070 -> 0.086 -> 0.213 as the pair's min dependency-context count
rises, while CM (WordNet) is flat ~0.31-0.35 at every frequency; at 200+ contexts the LEARNED channel reaches
0.213, most of the way to WordNet's 0.349 with NO ontology. So the identity signal is acquirable from reading
and simply under-exposed at 34k sentences. POINTS TO (the big lever): (a) MORE READING (grow-by-reading
north-star, now empirically justified for this channel -- the curve rises and well-read words approach the
ceiling); (b) LABELED DEPRELS (I used unlabeled heads+direction; labeled contexts raise signal PER exposure,
effectively multiplying reading volume).

## The hdlab proposal (for the strategy session to land, Q111)
A map + witnessed prototype, not a landed diff. All LOCAL to the ranking's READ; the store's
recall/recognition path stays byte-identical.
1. **Read the grounding loop's SIMILARITY RANKING over a reliability-weighted CONVERGENT fusion of the
   distributional context bundle AND grounded meaning** (`grounded_similarity.grounded_vector`), using the
   landed `hdlab/convergent_cue_reader.py` Bayes rule (calibrate w/taus offline, held-out). This is
   `canonicalize_fast`'s sense assignment and `identify_missing_prerequisites`' candidate ranking. Keep it a
   single-shot graded population read -- do NOT introduce an attractor.
2. **Reserve the attractor for recall/recognition only, and de-sign the residual signed query in the
   reference `canonicalize` fallback** (reading_grounding_loop.py:896) so the non-default path matches
   `canonicalize_fast`'s graded convention (the module docstring at :110 already flags this latent mismatch).
No other downstream consumer regresses: the attractor is otherwise consumed only by `ca3_completer` /
`hippocampal_encoder` for RECALL (untouched, witness A4), and the exact-match gate's recognition AUC stays 1.0.

## What I did NOT establish (and would withdraw first if wrong)
- The win is on the sense-assignment RANKING metric (canonicalize's job), measured through the LIVE
  distributional field + graded read against an independent gold -- NOT an end-to-end grounding-coverage run
  with the fusion wired into `canonicalize_fast` over a full read. That end-to-end lift is the expected
  downstream consequence but is landed + measured by strategy (Q111). **The first thing I would withdraw is
  any implied coverage-growth number.**
- Absolute sense-assignment remains hard (MRR ~0.08); I claim a decisive RELATIVE win over the incumbent, not
  a solved absolute task.

## KEY REALIZATIONS
- **Read the live path before believing the brief's mechanism.** The brief said "attractor-as-ranker over
  sign codes"; the disk said the ranking is already a graded population read (GRADED_COMPARATOR ON, 2026-08-14)
  and the attractor is a recognition gate. Verifying which function the DEFAULT entry calls
  (`canonicalize_fast`, not the signed reference) turned a build into a rigorous located negative.
- **The owner's rule held literally.** A brain-foundational computation (the graded read) was already in
  place and "not working" -- because the component UPSTREAM (the representation it reads) was not
  brain-foundational. Fixing the readout bought nothing; fixing the representation cleared the bar.
- **Neither channel alone is the brain's answer.** Grounded gets you into the semantic neighborhood
  (hit@10 quadruples) but not to #1 (its sibling/synonym ceiling); distributional barely carries similarity
  at all (rho 0.039). The reliability-weighted convergent FUSION -- the ATL hub's actual integration -- beats
  both. Isolating readout from representation (the 2x2), and then decomposing the representation into its two
  brain channels, is what located the real lever.
- **Use an independent gold to avoid circular scoring.** The PARTIAL scored the fix against grounded cosine
  (partly circular); switching to SimLex human ratings (independent of every representation) is what makes the
  SOLVED win trustworthy.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, C7)
C7 ("cleanup_family/iterative_attractor sign()+attractor-as-RANKER, LIVE in the grounding loop, active harm")
should be re-scored: (i) the sign()-quantized Hopfield primitives are called nowhere live; (ii) the live
grounding-loop ranking is already a graded population read (canonicalize_fast, GRADED_COMPARATOR ON); (iii)
the attractor is live only as an exact-match recognition GATE (gap_detector), where a readout swap is a
measured no-op and hub over-promotion is absent at the gate's sharp temperature. The genuine residual
deviation is UPSTREAM and different in kind: the sense-assignment ranking reads a distributional-only bag of
co-occurrence (SimLex similarity rho 0.039); the brain-foundational fix is to read it over a reliability-
weighted convergent fusion of grounded meaning + distributional context (MRR 0.024 -> 0.081, CI-separated).

---
## TLDR (plain language)
When the system reads a new word, it has to decide which idea it already knows this word means. The worry
was that it does this with a clumsy "snap to the nearest memory" process. I checked the live code: that part
is already fixed -- it already uses a smooth, distance-preserving comparison, and the "snap to nearest" is
only used to recognise an exact word it has seen, which is the right place for it. The real problem is one
step earlier: it compares words only by which OTHER words they appear next to, which tells you two words are
RELATED but not that they mean the SAME thing. I showed that if you instead compare words by their real
grounded meaning, blended with that word-company signal the way the brain's meaning hub does, the system gets
much better at picking the right idea for a new word -- more than three times better at a fair, independent
test, with a scrambled version failing and the exact-word recognition left untouched. So the fix is not
"change the ranker" -- it is "give the ranker real meaning to compare, not just word company."

## QUESTIONS
None blocking.

## NEXT STEPS (all four rungs now prototyped; measured deltas in hand)
1. **(largest delta, prototyped -- hand-off to strategy, Q111)** Read the sense-assignment ranking over the
   full ATL-hub fusion: grounded (perceptual) + distributional (relatedness) + IDENTITY. Best measured stack =
   grounded+bag+taxonomic (WordNet supply) MRR 0.345 / hit@10 0.58 (~4.8x the SOLVED fix). Reserve the attractor
   for recall; de-sign the reference `canonicalize` fallback. Recall path byte-identical.
2. **(DONE brain-foundationally -- the identity signal, LEARNED, no ontology)** The dependency-parsed learned
   identity channel (DEP) recovers ~half the WordNet ceiling with NO WordNet (grounded+bag+DEP MRR 0.157,
   CI-beats the SOLVED fusion). Land it as the FOUNDATION-plus-grow stack: WordNet supplies the identity signal
   now (foundation), the online DEP learner grows it as reading volume accumulates (runtime) -- they are
   complementary, per the build-ideal-foundation-then-grow pivot. Closing the remaining half = reading VOLUME +
   labeled deprels.
3. **(compounds)** End-to-end: wire the fusion into `canonicalize_fast`, re-run a grounding pass, measure
   downstream grounding coverage/quality (the growth metric) with the info-free twin losing.
4. **(per-item weighting -- NULL, now diagnosed)** The reliability estimator was the problem: within-channel
   confidence is uncorrelated with per-query correctness (|rho|<=0.15) and the oracle upside is small (~+0.07).
   Reopen ONLY with a CALIBRATED reliability signal (hold-out calibration or cross-channel agreement); low
   priority.
5. **(NEG-2 diagnosis -> the highest-value further improvement) LABELED DEPRELS on the learned channel.** The
   learned identity channel is exposure-limited (curve still rising; low-freq words carry the whole gap). Beyond
   "read more," the buildable lever is richer context PER exposure: use LABELED dependency relations (dobj/nsubj
   /amod) not just unlabeled head/dependent direction, so each parsed sentence teaches more. Needs a labeled
   parse (graded_parser/arc_parser labels), then re-run the DEP channel.
