---
problem: bridging_inference_infer_the_unstated_link_between_adjacent_sentences
status: SOLVED
bar: "PASS = a glass-box bridging inference that, given two adjacent sentences with an unstated coherence link, infers the correct bridge (which entity is the instrument / that A caused B / which whole a part belongs to), CI-separated over BOTH (a) a no-inference floor (the reader WITHOUT the bridge; e.g. most-recent / most-salient entity, or the connective-only causal_links) AND (b) a meaning-SHUFFLED info-free twin (the same selector reading a permuted/shuffled meaning store) -- and the TWIN MUST LOSE, proving the semantic-relatedness signal is load-bearing (not salience or a shape artifact). Report the bootstrap CI half-width AND the null p95; recompute each floor on the item's OWN population; no number crosses scorers or populations. Prefer to report per-bridge-type (instrument / causal / part) separately -- a win on one type and a negative on another is a real, useful result."
result: "Scorer = argmax==gold antecedent-selection accuracy, item bootstrap CI (2000x), held-out. ANTECEDENT SELECTION (the brief's which-whole / which-event, meaning store = the ATL PPMI+SVD hub, glass-box): REFERENTIAL-PART on WordNet meronymy (n_pooled=6350, 5 splits) RAW_HUB 0.4720 vs no-inference floor 0.2000 (+0.2720 CI[+0.2524,+0.2921]) and vs most-salient floor 0.1737 (+0.2976 CI[+0.2728,+0.3213]); shuffled-meaning twin 0.1969 (RAW-TWIN +0.2752 CI[+0.2508,+0.3008]). REFERENTIAL-PART on ConceptNet PartOf (independent 2nd source, n=3775) RAW_HUB 0.6087 / meaning_foundation 0.6541 vs floor 0.2000 (+0.4087) twin 0.2021. INSTRUMENT on ConceptNet UsedFor (artifact subject, n=3390) RAW_HUB 0.4522 vs floor 0.2000 (+0.2522 CI[+0.2354,+0.2699]) twin 0.1968. All CI-separated ABOVE both floors; every twin collapses to chance (0.20). INTEGRATION/CONDITIONING LEVER (candidate set WITH salient distractors -- the realistic confound): salience-discounted specificity (COND, N400/predictive-coding) beats raw relatedness CI-separated on all three types (+0.050/+0.049/+0.048, each CI-lo >0.039). END-TO-END over a parsed situation model (n=1005 generated modern 2-sentence items) COND 0.4965 vs recency/no-inference floor 0.0 (gold placed non-recently) vs shuffled twin 0.2886 (COND-TWIN +0.208 CI[+0.167,+0.250]). LOCATED SUB-NEGATIVES: (i) relation-TYPE selection (3-way, chance 0.333, n=5145) exemplar 0.7854 but its SEMANTIC contribution over the shape twin is only +0.050 [+0.038,+0.062] -- the relation LABEL is mostly lexical/structural, not distributional relatedness; (ii) a linear relation-OFFSET selector is a shape artifact (offset-minus-twin +0.029 vs raw-minus-twin +0.275) -- a coherence relation is not a single linear direction. CAUSAL antecedent selection corroborates on the associative axis (RAW/COND beat floor+twin on ConceptNet Causes) but is NOT redone as a mechanism -- the force+mental unstated-causal selector is already SOLVED on disk (exp_causal_unified_bridge_event_type_v1). SIGNAL-LOSS TRACE (measured, same population, exp_bridging_signal_loss_ladder_v1): vs a perfect reader the loss decomposes as ESTIMATOR -0.505 (dominant: even gold-vs-4-random-words the static hub gets 0.495) >> gold-ambiguity -0.047 >> salience-confound -0.007 (population-level, minor) + conditioning recovery +0.048; extraction + typing are downstream. BRAIN-FIDELITY: NOT 100% -- the two biggest deviations (a STATIC bag-cosine estimator vs the ATL's relational settling; a ONE-STEP discount vs Kintsch's iterative integration) COINCIDE with the biggest signal loss. Closing that gap (exp_bridging_ppr_integration_v1): the FAITHFUL iterative spreading-activation integration (PPR over the relational graph, meronymy/PartOf/UsedFor HELD OUT) fused with the distributional read BEATS the static estimator held-out -- INSTRUMENT FUSE 0.531 vs HUB 0.441 (+0.090 CI[+0.074,+0.106]), PART FUSE 0.485 vs 0.449 (+0.036 CI[+0.019,+0.052]), random-seed PPR twin collapses to chance. OPTIMIZATIONS PROTOTYPED (all brain-foundational, research-anchored): selective/abstaining bridging via graded-competition ENTROPY (confident quartile 0.81 vs ~0.52 blanket, twin flat) + multi-cue Competition-Model fusion (+0.048..+0.062 over best single cue) + context-modulation (additive +0.138, twin flat) + coref-referent recovery (pronoun target OOV -> +0.239) + structural relation typing (0.790, feature-twin at chance -> typing is structural not distributional) + hypernymy densification (+0.061 PART PPR). WALL RESEARCHED + AUDIT CORRECTED: semantic control (LIFG/pMTG) is BIASED COMPETITION/selection, NOT multiplicative gain -- so the additive-drive+softmax-competition form is the brain-faithful one (the audit's C3 'additive where control is multiplicative' is REFUTED)."
floor: "Strongest floor actually run = the most-SALIENT-candidate floor (hubness = mean cosine to a 2000-word vocab sample), recomputed per population: PartOf 0.1579, part_wn 0.1737, INSTRUMENT 0.2059; PLUS the no-inference RANDOM/recency floor 0.2000 (and 0.0 end-to-end by construction). The meaning-store arm is CI-separated ABOVE both on every type. Null p95: the shuffled-meaning twin sits at chance (part_wn 0.1969, PartOf 0.2021, INSTRUMENT 0.1968; 3-way type twin 0.7353; end-to-end twin 0.2886) -- the meaning-minus-twin margin excludes zero everywhere the mechanism is claimed."
controls: "(1) SHUFFLED-MEANING TWIN (hub vectors permuted across the vocabulary; same task shape) -> collapses to chance on every antecedent-selection type -> excludes 'shape/salience/frequency wins'; the specific word<->meaning map is load-bearing. (2) MOST-SALIENT-CANDIDATE floor (hubness) -> beaten CI-separated -> excludes 'pick the generically-frequent entity' (the confound a yield probe exposed: raw hub ranks knife~john 0.282 > knife~murder 0.099). (3) RANDOM/RECENCY no-inference floor -> beaten CI-separated. (4) LINEAR-OFFSET arm + its own twin -> the offset's lift is a shape artifact (offset-twin +0.029 << raw-twin +0.275) -> excludes 'the win is a word2vec-analogy trick' AND locates a negative. (5) HELD-OUT 50/50 splits x5 for every fitted component (the relation direction, the conditioning beta). (6) TYPE-selection shape twin (shuffled meaning, exemplar typer) -> 0.7353, isolating the small +0.050 semantic contribution. (7) end-to-end RECENCY floor 0.0 by construction (gold antecedent placed non-recently in S1) + shuffled twin 0.2886 as the real end-to-end floor."
files_changed: "experiments/exp_bridging_selection_partof_v1.py (first PART instrument + the offset negative), experiments/exp_bridging_selection_v2.py (unified PART[WordNet+ConceptNet]+INSTRUMENT antecedent selection + meaning_foundation comparison arm), experiments/exp_bridging_type_selection_v1.py (3-way relation-TYPE selection, two-sided), experiments/exp_bridging_salience_conditioning_v1.py (the construction-integration conditioning lever vs the salience confound), experiments/exp_bridging_discourse_endtoend_v1.py (end-to-end over a parsed situation model + glass-box canonical trace), experiments/exp_bridging_signal_loss_ladder_v1.py (the MEASURED signal-loss trace, stage by stage), experiments/exp_bridging_ppr_integration_v1.py (the brain-fidelity upgrade: the ACTUAL Kintsch spreading-activation integration, held-out), experiments/exp_bridging_graded_integration_v1.py (optimization: Competition-Model multi-cue fusion + entropy-gated SELECTIVE bridging), experiments/exp_bridging_context_modulation_v1.py (#4 context-modulation + the multiplicative-vs-additive wall), experiments/exp_bridging_structural_typing_v1.py (#7 structural typing organ), experiments/exp_bridging_coref_referent_v1.py (#6 coref-referent recovery), experiments/exp_bridging_denser_graph_v1.py (#8 hypernymy densification), verification/test_bridging_inference.py (33/33 scaffold-free witness), data/bridge_relation_assets_v1/ (offline-built static typed-relation asset from ConceptNet 5.7: UsedFor/PartOf/MadeOf/HasA/ReceivesAction/Causes, admissible), notes/problems/bridging_inference_infer_the_unstated_link_between_adjacent_sentences/SOLVED.md. NO hdlab/ write (Q111); proposed wire below."
reverify: ".venv/Scripts/python.exe verification/test_bridging_inference.py"
---

# What was built and measured

The brief asked: build a glass-box CONSTRUCTION-INTEGRATION bridge that, over adjacent situation-model
events/entities, PROPOSES the small closed set of coherence-required bridges (causal / instrument /
referential-part) and SELECTS the one best supported by semantic relatedness in the meaning store -- and it
named this as the FIRST live `read()`-time consumer of the currently-LATENT meaning channel. I built exactly
that operation and measured it per bridge type, with the full control suite. The disk gives a clear,
decomposed answer.

**HEADLINE (the brief's core "infers the correct bridge"): meaning-store associative relatedness SELECTS the
correct bridge ANTECEDENT -- which whole a part belongs to, which event an instrument serves -- CI-separated
over the no-inference floor AND the most-salient-entity floor, with the meaning-shuffled twin collapsing to
chance, on BOTH unclaimed types across TWO independent gold sources.** The relation TYPE is only weakly
recoverable from relatedness (mostly lexical/structural -- a located sub-negative). The situation-model
CONDITIONING (specificity beyond generic salience -- the N400 lever) gives a small but CI-separated lift over
raw relatedness. End-to-end over a parsed situation model the conditioned selector beats the recency floor and
its twin, bounded (~0.50) by extraction + the residual salience confound + pronoun coref -- the same
extraction wall the sibling discourse SOLVEDs mapped.

## 1. HOW THE BRAIN DOES THIS (the opening move) -- what is PINNED vs OUR-INVENTION
- **PINNED (replicate the operation):** Kintsch (1988) CONSTRUCTION-INTEGRATION -- comprehension constructs a
  weakly-connected network of stated propositions plus a small set of likely inferences, then integrates by
  spreading activation until it settles; the bridging inferences are the links that survive. The relatedness
  that says which instrument/whole/cause is plausible comes from the ATL semantic hub (Lambon Ralph 2017,
  graded/distributional). The "select the specific coherent link, not the generically-salient one" is the
  N400 / predictive-coding signal -- relatedness BEYOND baseline expectation (Kuperberg & Jaeger 2016).
- **OUR-INVENTION-UNDER-TEST (flagged, swept, not adopted):** the relatedness estimator (compared THREE: the
  PPMI+SVD hub; the curated `meaning_foundation` w2v sense signatures; a linear relation-offset -- refuted);
  the salience-discount coefficient beta (swept, held-out-selected = 2.0); the candidate-set construction and
  the closed type inventory {PART, INSTRUMENT, CAUSAL}.

## 2. THE CAN-FAIL INSTRUMENT (resource-grounded, held-out, modern)
There is NO modern human-annotated bridging corpus on disk (confirmed: only GAP pronoun-coref; no
ISNotes/GUM/PDTB), so per the bar I built the gold from REAL resources -- WordNet part/substance meronymy
(concrete nouns) and ConceptNet 5.7 (PartOf, UsedFor-with-artifact-subject, Causes) -- restricted to modern
single-token common lemmas covered by the hub (the 19c ban is about archaic TEXT, not lexical relations). The
task: given a bridging TARGET and a candidate SET of prior situation-model entities/events (gold + K
distractors, gold position RANDOMIZED so recency == chance), select the correct antecedent. HELD-OUT 50/50
x5 for any fitted component. This is the "carefully-constructed modern given-new bridge items ... each with an
info-free twin" the bar sanctions; the gold LABELS come from the resource, not my judgement, so it is not a
hand-authored answer key.

### 2a. Antecedent selection -- the win (per type)
| type (source) | n_pooled | meaning arm | no-inference floor | most-salient floor | shuffled twin |
|---|---|---|---|---|---|
| PART (WordNet meronymy) | 6350 | RAW_HUB **0.472** | 0.200 (+0.272 CI[+0.252,+0.292]) | 0.174 (+0.298) | 0.197 (+0.275) |
| PART (ConceptNet PartOf) | 3775 | RAW_HUB 0.609 / MEAN_FND **0.654** | 0.200 (+0.409) | 0.158 (+0.451) | 0.202 (+0.407) |
| INSTRUMENT (ConceptNet UsedFor) | 3390 | RAW_HUB **0.452** | 0.200 (+0.252 CI[+0.235,+0.270]) | 0.206 (+0.246) | 0.197 (+0.256) |

**Every meaning arm is CI-separated ABOVE both floors, and every shuffled-meaning twin collapses to chance --
so the semantic-relatedness signal is genuinely load-bearing for bridge-antecedent selection, on both
unclaimed types, replicated across two independent gold sources.** `meaning_foundation` (the curated LATENT
asset the INTEGRATION_LEDGER flags as the highest-leverage latent block) is the strongest single source on
PartOf (0.654) and competitive elsewhere -- so this problem is not merely *a* live consumer of the meaning
channel, the curated foundation is its *best* bridge selector.

### 2b. The integration/conditioning lever (the salience confound, and the fix)
A yield probe exposed the wall the raw signal hits: raw hub cosine ranks knife closer to the frequent name
"john" (0.282) than to the coherence-required event "murder" (0.099) -- the "swamped by salience" wall the
sibling discourse SOLVEDs hit. With a realistic candidate set that INCLUDES salient distractors (the top-hubness
generic words), the construction-integration CONDITIONING -- score = relatedness - beta*salience, i.e.
relatedness BEYOND generic expectation (N400/predictive coding; hub-normalized spreading activation) -- beats
raw relatedness CI-separated on all three types (**+0.050 / +0.049 / +0.048**, each CI-lo > 0.039; beta=2.0
held-out; twins collapse). The lift is modest because raw PMI already discounts frequency somewhat, but it is
real, consistent, and the correct brain-faithful direction (the specific link, not the salient one).

### 2c. Relation-TYPE selection -- a located sub-negative (honest)
The other half of the operation ("propose the closed set and select the best-supported TYPE"): a held-out
exemplar (k-NN in relation-offset space) classifies a bridged pair among {PART, INSTRUMENT, CAUSAL} at 0.785
(chance 0.333) -- BUT its shuffled-meaning twin also reaches 0.735, so the genuine SEMANTIC contribution is
only **+0.050 [+0.038,+0.062]**. **The relation LABEL is mostly carried by lexical/structural regularity
(which words appear), not by distributional relatedness.** This is brain-consistent: the ATL hub supplies the
relatedness that finds WHICH elements cohere; the relation TYPE comes from schema/syntax/connective cues -- which
is exactly where the on-disk causal-bridge cells get it (force dynamics, connectives, verb frames), NOT from a
distributional read. So the meaning store's job is antecedent selection; typing is a different organ's job.

## 3. END-TO-END over the situation model (the discourse demonstration + the honest bound)
Generated 1005 modern 2-sentence items from the real gold pairs, parsed each into a situation model (entities =
NOUN/PROPN of S1, events = VERB of S1 -- mirroring `SituationReader.sm.entities`/`sm.events`, the live wire
point), proposed a bridge from the S2 target to each prior element, and selected by the conditioned relatedness.
The correct antecedent was placed NON-recently, so recency is a genuine (here, defeated) competitor.
**COND 0.4965 vs recency/no-inference floor 0.0 vs shuffled twin 0.2886 (COND-TWIN +0.208 CI[+0.167,+0.250]);
per-type PART 0.548 / INSTRUMENT 0.478 / CAUSAL 0.455.** The glass-box trace on the brief's own examples is
diagnostic: it gets the CLEAN cases right (engine->car, nail->hammer) and fails the brief's three for three
distinct, named reasons -- (i) knife->"john" and key->"want": the salience confound PERSISTS on tiny candidate
sets even with the discount; (ii) water/fire: the target "It" is a PRONOUN (needs coref -- a different organ);
(iii) beer->"supplies": generic-container wholes are weakly hub-related. **This is where along the chain we
lose signal: the mechanism (2a) is strong; the situation-model CONSTRUCTION stage (extraction of clean
entities/events, pronoun resolution) and the residual salience confound cost the end-to-end number -- the same
extraction-bound wall the discourse-fact SOLVEDs measured, not a new failure of the bridge.**

## 4. Why the wins are real and the negatives are located (fair test)
The wins beat the STRONGEST floor actually run (most-salient candidate) and are killed by the meaning-shuffle
twin, on two independent gold sources per type, held-out -- so they are neither a shape artifact nor a salience
artifact nor a fitted-to-test artifact. The negatives are located and numbered: the relation is not a linear
offset (offset-twin +0.029 << raw-twin +0.275); typing is not distributional (+0.050 over shape); the
end-to-end residual is extraction + salience + coref (traced item-by-item). Nothing was claimed that a control
did not survive.

## 4b. WHERE THE SIGNAL IS LOST -- traced stage by stage, MEASURED on one population (owner's question)
A signal-loss ladder (exp_bridging_signal_loss_ladder_v1) holds the scorer FIXED (raw hub) and peels away one
degradation at a time on the SAME PART pairs (K=4, chance 0.20, n=5075), so each drop is attributable. The
result CORRECTS my first framing (which over-blamed the salience confound):

| stage (what changes) | acc | loss attributed to this step |
|---|---|---|
| PERFECT reader (human ceiling) | 1.000 | -- |
| CEIL: gold vs 4 RANDOM words (best case) | 0.495 | **-0.505 = the ESTIMATOR itself (+gold noise)** |
| PLAUS: distractors are other plausible wholes | 0.448 | -0.047 = gold-ambiguity / relatedness resolution |
| SAL: add 2 salient distractors (raw) | 0.441 | -0.007 = the salience confound (population-level: MINOR) |
| SAL + conditioning (specificity discount) | 0.489 | +0.048 = the conditioning recovery |
| end-to-end over a PARSED situation model | ~0.50 | extraction/construction (pronoun targets, generic-verb candidates) |
| relation TYPE label | ~structural | +0.050 only from meaning (typing is not distributional) |

**THE DOMINANT LOSS IS THE ESTIMATOR, not the confound.** Even distinguishing the true whole from 4 RANDOM
unrelated words, the static hub relatedness gets only 0.495 (instrument 0.474) -- so ~half the signal a competent
reader has is simply not in the static bag-cosine read (part of this residual is WordNet gold noise -- obscure
meronyms like reserve->bench -- which I did not fully separate; MEAN_FND raises the ceiling to 0.580, so >=0.085
of it is estimator-choice, not gold). The salience confound that the knife~john probe exposed is real on
adversarial singletons but only -0.007 at the population level. Gold-ambiguity is -0.047. Extraction and typing
are downstream. **So the highest-leverage place to recover signal is the relatedness ESTIMATOR + the INTEGRATION
step -- which is exactly the least brain-faithful part of the pipeline (next section).**

## 4c. ARE WE 100% BRAIN-FOUNDATIONAL? -- NO. Component-by-component audit (honest)
| component | brain op | our impl | verdict |
|---|---|---|---|
| situation model (entities/events) | event-indexing (Zwaan); discourse referents | reader's extraction; I used raw NPs | PINNED op; DEVIATION: not coref-resolved referents -> pronoun targets lost |
| CONSTRUCTION (propose closed set) | Kintsch: stated props + likely inferences | fixed inventory {PART,INSTR,CAUSAL} | PINNED idea; OUR-INVENTION inventory (graded/open in the brain) |
| relatedness ESTIMATOR | ATL: graded, compositional, context-modulated settling (Lambon Ralph) | STATIC PPMI+SVD bag-of-words cosine | **BIGGEST DEVIATION** -- and 4b shows it is the biggest signal loss |
| INTEGRATION (settle) | iterative spreading activation to a fixed point (Kintsch) | ONE-STEP salience discount (score - b*sal) | **LARGE DEVIATION** -- a shortcut, not the recurrent settling |
| SELECTION | graded competition / softmax settling | hard argmax + abstain | minor deviation |
| TYPING | schema/syntax/connective | not built (measured structural, not distributional) | GAP (a different organ) |

**So: NO, not 100% brain-foundational -- and, decisively, the two biggest fidelity gaps (a static bag-cosine
estimator; a one-step discount standing in for iterative integration) are EXACTLY where 4b says the signal is
lost. The fidelity gap and the accuracy gap coincide.** That is the opposite of a benchmark artifact: it says the
route to overcoming the wall is to make those two components brain-faithful -- which I then did (4d).

## 4d. CLOSING THE GAP: the ACTUAL Kintsch integration recovers signal (the owner's "every component brain-foundational")
I replaced the static estimator + one-step discount with the FAITHFUL operation: PERSONALIZED PAGERANK
(iterative spreading activation to settling) over the WordNet++ relational graph, seeded by the target, reading
the settled activation on each candidate (exp_bridging_ppr_integration_v1). Crucially the graph is built from
ConceptNet + SyntagNet ONLY -- so the PART meronymy / ConceptNet PartOf / UsedFor gold edges are HELD OUT: the
settling must recover the bridge from surrounding relational structure, not the direct edge (the parent
discourse-fact SOLVED's held-out-edge test). Held-out, K=4, chance 0.20:

| type | HUB (static, current) | PPR (spreading activation) | FUSE (graph + distributional) | PPR twin (random seed) |
|---|---|---|---|---|
| INSTRUMENT (n=4041) | 0.441 | **0.509 (+0.068 CI[+0.048,+0.088])** | **0.531 (+0.090 CI[+0.074,+0.106])** | 0.205 (collapses) |
| PART (n=3045) | 0.449 | 0.419 (-0.030) | **0.485 (+0.036 CI[+0.019,+0.052])** | 0.204 (collapses) |

**The more-brain-foundational estimator wins, held-out, on both types: the ATL as BOTH relational
spreading-activation AND distributional (FUSE) beats the static bag-cosine (+0.036 PART, +0.090 INSTRUMENT), and
the target-specific spread is load-bearing (random-seed PPR twin collapses to chance).** For INSTRUMENT the pure
spreading-activation already beats the static read (+0.068); for PART the graph alone is weaker (meronymy is
sparse in ConceptNet+SyntagNet co-occurrence) but the fusion still wins. This is the concrete demonstration that
overcoming the wall = making the component brain-faithful, and it is the recommended estimator for the landing.

## 4e. BRAIN-FOUNDATIONAL OPTIMIZATION OPPORTUNITIES (ranked by MEASURED leverage; the top ones prototyped)
Every opportunity below is tied to a measured loss (4b) and a named fidelity gap (4c), not a wishlist.

**PROTOTYPED + MEASURED (they deliver, held-out; exp_bridging_graded_integration_v1 + _ppr_integration_v1):**
1. **Selective / abstaining bridging via the maintained-distribution ENTROPY (biggest win).** The brain does not
   force a guess; it commits when the competition settles and defers when it does not (Levy 2008 entropy =
   difficulty; Friston precision; the metacognitive abstain the brief asks for). Fusing the ATL cues through the
   pinned Competition Model (hdlab.graded_competition) and ranking by 1-normalized-entropy: the CONFIDENT subset
   is far more accurate than blanket -- top quartile 0.81, top half 0.66 (PART) / 0.70 (INSTRUMENT) vs ~0.52-0.54
   blanket; selective@50 +0.139 / +0.158 CI-separated; SHUFFLED-confidence twin FLAT. **This turns the ~0.5
   blanket into a high-precision committed subset + an honest abstain -- the single highest-value optimization,
   and it reuses a proven organ.**
2. **Multi-cue Competition-Model fusion (the ATL integrates cues, it does not pick one).** No single relatedness
   channel is best on every type (mfnd on PART, spreading-activation PPR on INSTRUMENT). Additive-cue -> softmax
   with held-out weights (the pinned FLMP/Bayesian posterior) beats the BEST single cue +0.062 (PART) / +0.048
   (INSTRUMENT) CI-separated.
3. **Faithful iterative INTEGRATION (spreading activation) instead of the one-step discount** (4d): FUSE beats the
   static estimator +0.036 (PART) / +0.090 (INSTRUMENT) held-out.

**ALSO NOW PROTOTYPED + MEASURED (each with a can-fail floor + info-free twin; wins AND located negatives):**
4. **Context-modulated relatedness (#4) -- WINS (attacks the dominant estimator loss).**
   exp_bridging_context_modulation_v1. On AMBIGUOUS items (a part with TWO valid WordNet wholes, so part-only
   relatedness is at chance 0.475), ADDITIVE context composition (compose the target with an independent
   associate of the gold whole) lifts to 0.613 -- **+0.138 CI[+0.110,+0.167] over the context-free read, shuffled-
   context twin FLAT.** This directly recovers the estimator loss (4b). **WALL / located negative:** the
   MULTIPLICATIVE gain form (my cos*cos proxy for IFG gain) does NOT beat additive (MULT-ADD -0.023, CI includes
   0) -- so the audit's C3 "control is multiplicative" is NOT supported by this test; either the brain's gain is
   not multiplicative at the level that matters here, or my similarity-product proxy is the wrong implementation
   of feature-level gain. RESOLVED by research (see "RESEARCH RESOLUTION OF THE #4 WALL" below): the
   multiplicative-gain premise is an over-claim; additive-drive + competition is the faithful form.
5. **Sense-resolved relatedness (#5) -- LOCATED NEGATIVE.** Resolving the target to its context WordNet sense
   (meaning_foundation per-sense signatures) barely helps (+0.038 over RAW, CI[-0.006,+0.082], NOT separated) --
   these concrete-noun bridges are not sense-ambiguous, so WSD-before-relatedness is a near-no-op here. Honest:
   the estimator loss is not a sense-resolution problem for this task (it may matter for polysemous targets).
   RESEARCH-CONFIRMED brain-foundational + the null EXPECTED: LIFG/pMTG resolve ambiguity ONLY when senses
   compete (Rodd/Davis/Johnsrude 2005 -- homonymy costs, polysemy does not); concrete monosemous nouns give
   little for control to do, so gate WSD on sense-competition/entropy (fire only when it is hard).
6. **Coref-resolved referents (#6) -- WINS, and it is NECESSARY not optional.** exp_bridging_coref_referent_v1.
   A pronoun target ("It went out") is a FUNCTION WORD and is OOV in the content-meaning store (no vector) -> the
   SURFACE bridge is stuck at chance (0.201); resolving to the referent recovers the FULL signal (0.439,
   **RESOLVED-SURFACE +0.239 CI[+0.222,+0.257]**). Brain-foundational (Garrod-Sanford referent-based bonding).
   The fix: run selection over coref-resolved sm.entities (the existing coref organ), not surface NPs.
7. **Structural relation TYPING (#7) -- WINS DECISIVELY, and confirms 2c.** exp_bridging_structural_typing_v1. A
   glass-box logistic over SCHEMA features (WordNet lexname/category + POS/verbiness) types the 3-way relation at
   **0.790 (chance 0.333) with the feature-shuffled twin at CHANCE (0.334)** -- ALL the lift is structural, vs the
   distributional typer whose shape twin sat at 0.735 (only +0.05 real). So the relation LABEL is carried by the
   entity SCHEMA + syntax, NOT distributional relatedness (Kehler/Hobbs coherence relations) -- this is the typing
   organ that completes propose-score-select.
8. **Denser relational graph for PART (#8) -- WINS.** exp_bridging_denser_graph_v1. Adding WordNet HYPERNYMY edges
   (general taxonomic knowledge the ATL holds; meronymy gold still HELD OUT) lifts PART spreading-activation
   0.444 -> 0.506 (**+0.061 CI[+0.037,+0.087]**), and PPR_dense now BEATS the static hub for PART too (it was
   worse before, 4d). Twin (random seed) collapses. The ATL is a DENSE relational store; sparsity was the limit.

### RESEARCH RESOLUTION OF THE #4 WALL (owner: research the walls) -- and it CORRECTS the project audit
A literature drill resolves why additive beat multiplicative: **"context modulates the ATL MULTIPLICATIVELY
(gain)" is an OVER-CLAIM.** Semantic control (LIFG/pMTG) is **biased competition / controlled SELECTION /
inhibition, NOT a scalar gain** (Lambon Ralph 2017 CSC; Jefferies 2013 + Whitney TMS 2012/2015; Badre & Wagner
2007; Hoffman/McClelland/Lambon Ralph 2018 constraint-satisfaction). The decisive evidence: TMS to LIFG disrupts
WEAK/ambiguous associations but NOT strong ones -- a uniform multiplicative gain would scale both. "Multiplicative
gain" is a VISUAL-attention mechanism (Reynolds & Heeger 2009) imported without license. **So my additive result
is the MORE brain-faithful one** (additive context DRIVE into a settling/competition network is closer to the
brain than a product of cosines -- which is why it won), and the maximally-faithful form is additive drive ->
SOFTMAX / divisive-normalization over candidates (any "gain" belongs in the normalization DENOMINATOR) = exactly
hdlab.graded_competition (optimization #1). The context-modulation optimization IS brain-foundational in its
additive-drive-plus-competition form; the multiplicative variant that correctly lost was the LESS-faithful one.

### ARE ALL THE OPTIMIZATIONS 100% BRAIN-FOUNDATIONAL? -- verdict per mechanism (research-anchored)
| optimization | brain mechanism | verdict |
|---|---|---|
| selective/abstaining bridging (entropy gate) | Levy 2008 distribution-over-interpretations; Friston precision; McKoon-Ratcliff 1992 minimalist (commit only coherence-REQUIRED inferences) | **PINNED** |
| multi-cue Competition-Model fusion | additive-cue -> softmax = FLMP/Bayesian posterior (McClelland 2013; Lewis-Vasishth) | **PINNED** |
| iterative spreading-activation integration | Kintsch 1988 CI = constraint-satisfaction to a fixed point; Collins-Loftus; ATL settling (Lambon Ralph 2017) | **PINNED (computational level)** |
| context-modulation (ADDITIVE drive + competition) | LIFG/pMTG biased-competition selection (Jefferies 2013; Badre-Wagner 2007; Hoffman 2018) | **PINNED** (additive form) |
| multiplicative-gain context (the tested variant) | -- (Reynolds-Heeger 2009 is VISUAL attention, not semantic control) | **RETIRED -- over-claim, correctly lost** |
| sense-resolution before relatedness (competition-gated) | Rodd/Davis/Johnsrude 2005 LIFG homonymy resolution | **PINNED** (null on concrete nouns EXPECTED) |
| coref-resolved referents | Garrod-Sanford 1994 bonding-and-resolution; bridging binds to referents (Clark/Haviland-Clark) | **PINNED** |
| structural relation typing | Kehler 2002 / Hobbs 1979 / RST / PDTB: type from connective+syntax+schema | **PINNED** |
| denser (taxonomic) relational graph | ATL = dense transmodal hub read by spreading activation (Lambon Ralph 2017) | **PINNED** |
**Answer: YES -- every LANDED/recommended mechanism is now brain-foundational (PINNED). The ONE non-foundational
idea (multiplicative gain) was tested, correctly lost, and is retired with a specific reason. The remaining
deviation named in 4c (the STATIC estimator) is precisely what the additive-context + spreading-activation +
competition upgrades replace.**

## 5. Upstream brain-foundational component + downstream no-regress (the owner's standing push)
- **UPSTREAM = the relatedness estimator itself, and it is where BOTH the signal (4b) and the fidelity (4c) are
  lost.** Three brain-foundational upgrades measured, all glass-box: (1) the N400/predictive-coding CONDITIONING
  (relatedness beyond generic expectation) recovers +0.048..+0.050 CI-sep (2b); (2) the curated
  `meaning_foundation` (w2v sense signatures) is a stronger source than the raw hub (2a); (3) THE big one -- the
  FAITHFUL Kintsch INTEGRATION (iterative spreading activation / PPR over the relational graph) fused with the
  distributional read beats the static estimator held-out (+0.036 PART / +0.090 INSTRUMENT, 4d). The recommended
  landing estimator is the FUSE (ATL = relational settling AND distributional), not the raw static cosine -- that
  is the maximally-brain-faithful, highest-signal read of the three.
- **NO DOWNSTREAM REGRESSION -- by construction.** The meaning channel is currently LATENT (no live read()-time
  consumer), so there is nothing downstream of it to regress; the bridge is the FIRST consumer. The proposed
  wire is ADDITIVE: it READS `sm.entities`/`sm.events`/`sm.causal_links` and APPENDS a new `sm.bridges`
  annotation; it mutates no existing field, so who-did-what, coref, causal typing, space, belief and the
  timeline are byte-identical. (Same additive shape the strategy session accepted for the discourse-fact organ.)
- **CAUSAL is reused, not redone.** The unstated-CAUSAL selector (physical force + mental schema) is already
  SOLVED on disk (`exp_causal_unified_bridge_event_type_v1`, force+mental, acc 1.0 on its dissociation bank);
  the LitBank causal-QA gold is a known positional confound (`exp_causal_selection_instrument_diagnostic_v1`).
  My CAUSAL arm corroborates on the associative axis (ConceptNet Causes: relatedness beats floor+twin) but I do
  NOT rebuild the causal mechanism -- I cite it and unify all three types under the one propose-score-select frame.

# What I did NOT establish (and would withdraw first if wrong)
1. **The end-to-end number (0.50) is NOT a natural-corpus bridging accuracy.** It is on GENERATED modern items
   with clean templates (twin-controlled); the real-corpus bound is lower and extraction-dominated -- a real-text
   yield probe found genuine part-of bridging anaphora are rare and mostly degenerate WordNet meronymy
   (months->year) with polysemy noise, exactly as the discourse-fact SOLVEDs measured. **Withdraw first any
   reading of "50% on real prose."** The clean capability (section 2a) is the load-bearing claim; the
   end-to-end is a demonstration + honest bound.
2. **The relation TYPE is not selected by meaning relatedness** (section 2c, +0.050 over shape). If a reviewer
   wants "the bridge fully typed by the meaning store", that is a located negative -- the type comes from
   schema/syntax. Withdraw any claim that the meaning store types the bridge.
3. **The conditioning lift is small (~0.05).** Real but modest; I would withdraw any claim that salience
   discounting "solves" the confound -- it partially mitigates it (knife->john still fails on a 2-candidate set).
4. **No hdlab landing measured on the live board.** The wire is proposed + argued additive, not landed (Q111);
   the live-board consumer lift is unmeasured until the `reader_meaning_channel` stage lands the read.

# KEY REALIZATIONS (the enabling moves)
1. **The yield probe reframed the whole problem.** Testing raw relatedness on the brief's own examples FIRST
   showed the signal EXISTS but is salience-confounded (knife~john > knife~murder). That single probe turned
   "is there signal?" (yes) into the real question "does conditioning separate the coherence link from
   salience?" -- and told me the linear-offset idea and the naive raw read were both incomplete before I built
   anything heavy.
2. **Let the twin, not intuition, kill the typed-offset arm.** I expected a relation-conditioned direction to
   be the lever; the shuffled twin exposed it as a geometric shape artifact (part-whole is multi-modal, not one
   direction). The twin also exposed that 0.735 of the 0.785 type-classification accuracy is lexical shape --
   the difference between "the meaning store types the bridge" (false) and "it selects the antecedent; type is
   structural" (true).
3. **Two independent gold sources per type is what makes the antecedent win credible.** WordNet meronymy AND
   ConceptNet PartOf both give the same CI-separated, twin-collapsing result -- so it is not an artifact of one
   resource's construction.
4. **Salience-discount = the N400 specificity signal.** Recasting "beat the salience confound" as "relatedness
   beyond baseline expectation" connected the fix to a PINNED brain mechanism (predictive coding) rather than an
   ad-hoc trick, and it is exactly the hub-normalization the audit flags PPR needs.
5. **Compare the relatedness sources; do not assume one.** The brief said so; doing it found `meaning_foundation`
   (the LATENT curated asset) is the best source -- which is the concrete justification for wiring it live.
6. **The signal-loss LADDER (peel one degradation at a time, same population) relocated the wall.** My first
   writeup blamed the salience confound; the ladder showed the ESTIMATOR is the dominant loss (-0.505) and the
   salience confound is minor at population scale (-0.007). Measuring each stage, rather than reasoning about it,
   is what turned a plausible-but-wrong story into the correct one -- and pointed every optimization at the
   estimator/integration, not the confound.
7. **An on-disk NEGATIVE + a research drill CORRECTED the project's own audit.** additive context beat the
   multiplicative "IFG gain" form; instead of filing that as a failed optimization, the drill showed WHY --
   semantic control is biased COMPETITION/selection, not a scalar gain (the TMS strong-vs-weak dissociation),
   and "multiplicative gain" was a visual-attention import. So the null was the brain telling us the audit's C3
   was backwards; additive-drive + softmax-competition is the faithful operation. The lesson: when a
   brain-motivated arm loses, ask whether the brain claim itself is right before discarding the arm.
8. **Entropy-gated abstention turns a mediocre blanket number into a high-precision capability.** The bridge is
   ~0.5 if forced to answer everything, but 0.81 on its confident quartile with a flat shuffled-confidence twin
   -- so the win is not "higher accuracy" but "the bridge knows which inferences to trust" (McKoon-Ratcliff
   minimalist: commit only the coherence-required inferences), which is the brain-faithful shape.

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md Section 2b / Section 6)
- **Construction-Integration (Kintsch) -- MISSING -> ATTEMPTED/PARTLY-BUILT.** A glass-box propose-score-select
  bridge over the situation model now exists (experiments/verification). The CONSTRUCTION (propose the closed
  coherence set) + a simple INTEGRATION (salience-discounted / hub-normalized relatedness = N400 specificity)
  are built. MEASURED: meaning-store relatedness SELECTS the correct bridge ANTECEDENT CI-separated over
  no-inference + salience floors, twin collapses (PART + INSTRUMENT, two gold sources); the conditioning lever
  adds +0.05 CI-sep. LOCATED NEGATIVES: relation-TYPE selection is only weakly semantic (+0.05 over a shape
  twin -- typing is lexical/structural, not distributional); a linear relation-offset is a shape artifact.
  PINNED refs added: Kintsch 1988; Lambon Ralph 2017 (ATL graded relatedness); Kuperberg & Jaeger 2016 (N400).
  **INTEGRATION now BUILT faithfully (not just the one-step shortcut):** iterative spreading activation (PPR over
  the relational graph, gold edges held out) fused with the distributional read BEATS the static estimator
  held-out (+0.036 PART / +0.090 INSTRUMENT; random-seed twin collapses) -- so the Kintsch integration deviation
  is now partly CLOSED, and the signal-loss trace (estimator dominates -0.505 >> salience -0.007) localizes the
  remaining deviation to the relatedness estimator's static/non-compositional read.
- **DISCOURSE / BRIDGING of the UNSTATED (Graesser) -- "thin/UNPINNED, IS coref in disguise" -> REFINED +
  MEASURED.** Elaborative bridging of the unstated is now measured for PART + INSTRUMENT: the ANTECEDENT read
  reuses the coref-style selection (confirming "coref in disguise" for the WHICH-element half) but the RELATION
  TYPE is NOT coref and NOT distributional -- it is schema/syntax (consistent with the on-disk causal-bridge
  cells). The residual on real discourse is extraction + salience + pronoun coref (the discourse-fact SOLVEDs'
  wall), not the bridge selector.
- **CORRECTION to DEVIATION C3 ("ADDITIVE where semantic control is MULTIPLICATIVE gain") -- REFUTED, replace
  the entry.** A research drill (Lambon Ralph 2017 CSC; Jefferies 2013 + Whitney TMS 2012/2015; Badre & Wagner
  2007; Hoffman/McClelland/Lambon Ralph 2018) + a direct on-disk test (exp_bridging_context_modulation: additive
  context composition +0.138 CI-sep; the multiplicative form does NOT beat it, MULT-ADD not separated) establish
  that semantic control (LIFG/pMTG) is **biased competition / controlled SELECTION**, NOT a scalar multiplicative
  gain. The decisive evidence: TMS to LIFG disrupts WEAK/ambiguous associations but NOT strong ones (a uniform
  gain would scale both). "Multiplicative gain" (Reynolds & Heeger 2009) is a VISUAL-attention mechanism imported
  without license. The faithful rule is **additive context DRIVE -> softmax/divisive-normalization over
  candidates** (any gain in the normalization denominator) = graded_competition. So the audit's "context enters
  additively where it should be multiplicative" has the fidelity BACKWARDS for the semantic case: additive-drive-
  plus-competition IS the faithful operation; the deviation is the STATIC (non-context-modulated, non-settling)
  read, not the additivity.
- **Meaning channel -- LATENT -> HAS A DEMONSTRATED FIRST CONSUMER.** Bridge-antecedent selection is a live
  read()-time consumer of the meaning store, and `meaning_foundation` is its best source (0.654 on PartOf) --
  the concrete load-bearing justification for landing the `reader_meaning_channel` read.

# ADJACENT COMPONENTS -- capabilities / limitations / brain status (seeds the next problems)
1. **The situation-model CONSTRUCTION stage (extraction) is the end-to-end bottleneck.** CAPABILITY: clean
   entity/event extraction on simple prose. LIMITATION (measured): pronoun targets (water/fire "It") and generic
   verbs entering the candidate set cost the end-to-end number; the mechanism itself is stronger than 0.50.
   BRAIN STATUS: the reader's entity/event extraction is built; PRONOUN-TARGET bridging needs the coref organ
   (a DIFFERENT organ -- named, not mine). OPTIMIZATION: run bridge selection over `sm.entities` (coref-resolved
   referents) rather than raw NPs -- couples this to the coref line.
2. **The relation-TYPING organ is the open sub-problem.** The type is structural (schema/syntax/connective),
   not distributional. A dedicated glass-box typer (definite-NP + meronym-head -> PART; instrument-near-event
   -> INSTRUMENT; connective/force -> CAUSAL) is the natural follow-on -- it would complete the propose-score-
   select loop where the meaning store cannot.
3. **The relatedness estimator (upstream).** `meaning_foundation` (curated) beats the raw hub; the hub needs
   hub-normalization (the N400 discount) to be usable for bridging. Both brain-foundational. OPTIMIZATION: a
   typed relatedness channel (PartOf-conditioned vs UsedFor-conditioned) if the type organ supplies the relation.
4. **CAUSAL bridging is the mature sibling** (force+mental selector SOLVED). It TYPES a proposed link; this
   problem SELECTS the antecedent. Unifying them into one situation-model `sm.bridges` register is the landing.

# PROPOSED hdlab DIRECTION (strategy lands; Q111 -- I did NOT write hdlab)
- Land a NEW, ADDITIVE situation-model organ (`hdlab/discourse_bridge.py` or an extension of
  `situation_reader`): over `sm.entities`/`sm.events`, PROPOSE bridge candidates, SCORE by salience-discounted
  meaning relatedness reading `meaning_foundation` (the best source) -- this is the FIRST live read()-time
  meaning consumer, and it wires cleanly to the `reader_meaning_channel` stage. Emit `sm.bridges`
  (target, antecedent, type, score, abstain-if-low-margin). ADDITIVE -> byte-identical existing dimensions.
- Score with the FUSE estimator (spreading-activation PPR over `grounded_semantic_graph` + the distributional
  meaning read) and the N400/specificity CONDITIONING, NOT the raw static cosine -- 4c/4d show the static cosine
  is BOTH the least brain-faithful component AND the biggest signal loss, and the faithful integration recovers
  signal held-out. Add an honest abstain; do NOT expect the meaning store to TYPE the bridge (measured weak) --
  take the type from the causal-bridge cells / a structural typer. Measure the live-board comprehension consumer
  AFTER the meaning-read stage lands.

---

## TLDR (plain language)
People automatically fill in the missing link between two sentences -- that the knife is the murder weapon, that
the beer is one of the picnic supplies. I built the quiet step that does this and proved the useful half works:
using the reader's stored word-meaning knowledge, it can pick WHICH earlier thing a later word connects to (which
whole a part belongs to, which action a tool is for) far better than guessing or than "just pick the most-talked-
about thing", and when I scramble the meaning knowledge the skill vanishes -- so it genuinely runs on meaning,
not on a trick. It works on two separate knowledge sources and on both the "part-of" and the "tool-for" kinds of
link. Two honest limits: (1) naming WHAT KIND of link it is (part vs tool vs cause) barely uses meaning -- that
comes from grammar and sentence shape, not word-relatedness; (2) end to end on messy sentences it gets about half
right, because reading the sentence into clean pieces (and handling "it") is where signal is lost -- the same wall
earlier work already mapped. This is also the first time the reader's meaning knowledge is actually used WHILE it
reads, and the curated meaning store turned out to be the best source for it.

## QUESTIONS
One labelling judgement for you at integration. I set status **SOLVED** because the brief's central operation --
infer the correct bridge (which whole a part belongs to / which event an instrument serves) by meaning-store
relatedness -- is demonstrated CI-separated over both floors with the twin collapsing, on both unclaimed types and
two gold sources, with the conditioning lever and controls. The relation-TYPE half and the end-to-end number are
honestly bounded (located negatives). If you weight the end-to-end (0.50, extraction-bound) or the type-selection
negative more heavily, **PARTIAL** is defensible; the content is identical either way. I lean SOLVED-on-the-
capability. (CAUSAL is cited, not redone -- if you want it re-measured as a first-class arm here rather than
reused, say so.)

## NEXT STEPS
1. **(Strategy)** Reverify the witness (`verification/test_bridging_inference.py`, **33/33**, recomputes every
   headline from source). Fold the AUDIT UPDATE into Section 2b/5/6: Construction-Integration MISSING -> built
   (propose-score-select + spreading-activation integration); the meaning channel now has a demonstrated first
   consumer; typing is structural not distributional; **and the C3 correction (semantic control is biased
   competition/selection, NOT multiplicative gain -- retire the Reynolds-Heeger framing)**.
2. **(Strategy, hdlab)** Land the ADDITIVE `sm.bridges` organ per PROPOSED DIRECTION, in its brain-faithful form
   proven here: score with the FUSE estimator (spreading-activation PPR over the DENSER graph + distributional
   read), integrate context as ADDITIVE drive into `graded_competition` (softmax competition, NOT a scalar
   multiplicative gain), gate the commit on the maintained-distribution ENTROPY (selective/abstaining bridging),
   run over coref-resolved `sm.entities`, and take the relation TYPE from the structural typer -- coupling to the
   `reader_meaning_channel` stage. Then measure the live-board comprehension lift (twin LOSING, no-regress).
3. **(Follow-on problems, seeded by the adjacent evaluation -- what is NOT yet done):** (a) validate on a real
   modern bridging corpus if one can be sourced (the end-to-end is generated-modern + extraction-bounded here);
   (b) the polysemous-target sense-resolution arm (this task's concrete nouns were monosemous, so #5 was a
   near-no-op -- it should matter for ambiguous targets, competition-gated); (c) a divisive-normalization
   (Reynolds-Heeger denominator) form of the competition if a finer gain effect is sought. The structural typer
   (#7), coref-referent (#6), denser graph (#8), context-modulation (#4), and selective/fusion (opt 1-2) are
   PROTOTYPED here -- they are LANDING items, not open problems.
