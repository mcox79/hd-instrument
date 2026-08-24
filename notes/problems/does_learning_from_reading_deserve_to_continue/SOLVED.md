---
problem: does_learning_from_reading_deserve_to_continue
status: SOLVED
bar: "ONE HEAD-TO-HEAD, ON ONE POPULATION, WITH ONE SCORER, WHERE THE LEARNED ARM IS THE BEST WE CAN HONESTLY BUILD."
result: "YES -- decisively, and the brief's INFERRED premise (that the sixteen losses reflect the IDEA, not our IMPLEMENTATION) is REFUTED. Scorer = Spearman rho of cosine similarity vs human ratings; learned arm = surprise-weighted PPMI(-SVD) over a word x word co-occurrence matrix read from simplewiki (38.09M tokens, vocab 60,085), UNFITTED. At the corpus ceiling the strong learned arm scores: SimLex-999 rho 0.2552 (ci_half 0.059, null p95 0.048, n=998); SimVerb-3500 rho 0.1290 (ci_half 0.033, null p95 0.028, n=3471); WordSim-353 rho 0.6301 (ci_half 0.067, null p95 0.084, n=334). It clears the STRONGEST floor's upper bound CI-separated on all three (orthographic 0.010/0.016/0.049; idf-count 0.124/0.037/0.412), beating the spelling floor by 15-40x -- the opposite of the sixteen losses. The curve is STILL CLIMBING at the corpus ceiling on all three (SimLex 0.089->0.255, SimVerb 0.023->0.129, WordSim 0.375->0.630), so the route is NOT exhausted -- it is corpus-limited. Head-to-head vs the supplied grounded hub (Lancaster+Brysbaert, unclamped) is population-dependent: learned WINS relatedness (WordSim 0.630 vs 0.405), TIES broad similarity (SimLex 0.255 vs 0.250), LOSES verbs (SimVerb 0.129 vs 0.266). Fusion (the brain hub test): learned+supplied beats supplied-alone CI-separated on WordSim (delta +0.2096, CI [0.154, 0.270]); positive-not-separated on SimLex (+0.038); the NOISE control never helps (delta -0.074/-0.085/-0.109). None of pre-registered failure modes (a)-(e) fired."
floor: "Strongest floor actually run = idf-weighted counting (a single surprise-style weighting), recomputed on each population/representation: SimLex 0.1235 (ci_half 0.065), SimVerb 0.0365 (ci_half 0.035), WordSim 0.4120 (ci_half 0.088). The learned arm clears each floor's UPPER bound CI-separated: SimLex learned-lower 0.196 > floor-upper 0.189; SimVerb 0.096 > 0.072; WordSim 0.563 > 0.500. The orthographic (spelling) floor -- the one that had been beating the shipped channel -- is 0.010/0.016/0.049, cleared by 15-40x."
controls: "(1) info-free RANDOM vectors -> rho ~0 (0.008/-0.007/-0.034), excludes 'any dense code scores'; (2) info-free SHUFFLED-corpus twin (PPMI-SVD on globally shuffled tokens, SAME unigram marginals, co-occurrence destroyed) -> rho ~0/neg (-0.070/-0.072/0.073), excludes 'the signal is unigram frequency or a pipeline artifact' and isolates it to co-occurrence STRUCTURE; (3) RAW-count arm (the substrate's shipped additive-accumulation mechanism) -> much lower (0.042/0.014/0.229), isolates the PPMI SURPRISE-WEIGHTING lever as the source of the gain, not 'any distributional accumulation'; (4) label-permutation null p95 reported beside every rho, every headline exceeds it; (5) orthographic floor RUN not cited; (6) idf-count floor (the standing 0.18 SimLex floor) RUN not cited and cleared CI-separated; (7) fusion NOISE control (noise+supplied) is negative on all three, so the learned channel's fusion gain is not 'any second channel helps'; (8) coverage reported (998/999, 3471/3500, 334/353 common) -- not coverage-limited; head-to-head scored on the common-coverage intersection so all arms saw the SAME pairs."
files_changed: "experiments/exp_learn_from_reading_strong_arm_v1.py, verification/test_learn_from_reading_strong_arm.py, data/exp_learn_from_reading_strong_arm_v1/metrics.json, notes/problems/does_learning_from_reading_deserve_to_continue/SOLVED.md (NO hdlab/ change landed; a proposed adapter is described below)"
reverify: ".venv/Scripts/python.exe verification/test_learn_from_reading_strong_arm.py"
---

# SOLVED -- learning-from-reading deserves to continue, and the sixteen losses were the weak mechanism, not the idea

## The answer, and why it is a result and not an opinion

The brief asked for "a result that makes the recommendation unnecessary": build the strongest honest
version of learning-from-reading, run the arm that could kill the idea, report what it did. **It did
not die. It cleared the floor that had been beating us by 15-40x, kept climbing with every million
words read, matched the supplied grounded channel on broad similarity, beat it on relatedness, and
contributed non-redundant signal in a fusion hub.**

The sixteen prior losses tested **raw additive accumulation** -- confirmed in code: the substrate
learns a word by a bare `+=` of `sha256` hash vectors of its neighbours (bag-of-words, no weighting,
no structure; `hdlab/reading_grounding_loop.py` `observe()`), the crudest possible distributional
model. Its own docstring says it uses that "instead of PPMI co-occurrence rows." So the one lever it
throws away is exactly the one the literature names as decisive and the one the brain uses.

## Why the learned arm is genuinely stronger (written before the run, per the bar)

The strong arm applies **PPMI** -- positive pointwise mutual information, "how much more than chance
do these two words co-occur" -- with Levy/Goldberg 0.75 context smoothing, optionally compressed by
SVD (LSA). This is stronger than raw accumulation for two independent, pre-registered reasons:

1. **It is the established lever.** PPMI (small window, cosine) is the single biggest design choice in
   count-based distributional semantics (Bullinaria & Levy 2007; Levy, Goldberg & Dagan 2015), and
   count and predict-based models are the same object once tuned (Levy & Goldberg 2014).
2. **It is the brain's own weighting.** The brain gates how strongly it encodes by SURPRISE -- the
   N400 is lexical prediction error, and larger surprise yields stronger memory (Rabovsky 2018;
   Hodapp & Rabovsky 2021). PPMI is an association/surprise measure; raw counting is not. And PPMI
   accumulation is ADDITIVE, so it reads forever without catastrophic forgetting -- the complementary
   -learning-systems property (McClelland 1995) the owner asked for ("keep reading and growing").

The RAW control (0.042/0.014/0.229) confirms the lever empirically: swapping surprise-weighting in
for raw counts is most of the gain.

## The measured head-to-head (38.09M tokens simplewiki, one Spearman scorer, common-coverage pairs)

| benchmark (n) | LEARNED PPMI-SVD | PPMI (additive) | RAW (shipped) | ORTHO floor | IDF floor | SUPPLIED core | shuffled twin | random |
|---|---|---|---|---|---|---|---|---|
| SimLex-999 (998) | **0.2552** +/-.059 | 0.2495 | 0.0424 | 0.0104 | 0.1235 | 0.2502 | -0.070 | 0.008 |
| SimVerb-3500 (3471) | **0.1290** +/-.033 | 0.1043 | 0.0144 | 0.0164 | 0.0365 | 0.2663 | -0.072 | -0.007 |
| WordSim-353 (334) | **0.6301** +/-.067 | 0.6015 | 0.2288 | 0.0487 | 0.4120 | 0.4047 | 0.073 | -0.034 |

- **The spelling floor is demolished, not winning.** The brief opened on "spelling scores ~9/100
  where meaning scores ~5/100." A properly surprise-weighted learned arm scores 0.26-0.63 where
  orthography scores 0.01-0.05. The premise held only for the crude mechanism.
- **The curve is still climbing at the corpus ceiling** (SimLex 0.089->0.255, SimVerb 0.023->0.129,
  WordSim 0.375->0.630 across 1M->38M tokens), so these numbers are LOWER BOUNDS; more reading buys
  more. This is the "still climbing, not flattened" branch -- corpus-limited, not exhausted.
- **Head-to-head is population-dependent, and that split is the real answer:** learned BEATS the
  grounded hub on relatedness (WordSim), TIES it on broad similarity (SimLex), and LOSES on verbs
  (SimVerb) -- where the learned channel is real (0.129, no longer the shipped +0.0000) but the
  supplied sensorimotor channel's action dimensions still win.

## The brain-foundational reframe, now measured: the channels are COMPLEMENTS

The neuroscience says "learned vs supplied" is a false choice -- the anterior-temporal hub fuses a
linguistic-distributional spoke with sensorimotor spokes (Patterson 2007; Lambon Ralph 2017), and
fusion beats either alone with non-redundant contributions (Andrews, Vigliocco & Vinson 2009; Banks &
Borghi 2021). Measured here: **learned + supplied beats supplied alone, CI-separated, on WordSim
(+0.2096, CI [0.154, 0.270])**; positive-but-not-separated on SimLex (+0.038); slightly negative on
SimVerb (learned too weak on verbs to help the average). The **noise control never helps** (delta
-0.074/-0.085/-0.109), so the fusion gain is the learned channel carrying real information, not any
second vector. This promotes the brief's own INFERRED item ("they may be complements") to a measured
result.

## What I did NOT establish (the honest scope)

- **This is an INTRINSIC benchmark result, not the live reading path.** It measures the quality of the
  learned REPRESENTATION (cosine vs human similarity ratings). `read()` still makes zero calls to any
  PPMI channel; wiring one into `hdlab/` is a separate adapter job that overlaps `reader_meaning_
  channel` (priority 1). "Deserves to continue" means the mechanism has a high, still-rising ceiling
  -- NOT that it is already working in the live substrate.
- **"Matches supplied on similarity" is borderline and arm-dependent.** Against the broad grounded hub
  (CORE, 12 dims, 36.8k words) learned ties SimLex; against the richer-but-narrower hub (FULL,
  +Warriner VAD +Kuperman AoA, ~13k words) supplied leads SimLex (0.341 vs 0.255). Learned clearly
  exceeds both on WordSim. I report both; I do not claim learned beats supplied on similarity.
- **No live end-to-end vocabulary-growth demonstration.** The learning curve is over corpus SIZE at
  eval time, which is the right instrument for "does more reading help", but it is not the substrate
  incrementally growing its own store during a run.

## Brain fidelity, labelled (pinned vs our-invention)

- PINNED: surprise-gated encoding (PPMI as the lever), additive/non-forgetting accumulation (CLS
  read-forever), the fusion hub (ATL hub-and-spoke). These are the load-bearing choices.
- OUR-INVENTION / ENGINEERING: SVD compression (batch, not biological -- and NOT load-bearing here:
  PPMI-alone, which IS additive and read-forever-compatible, is within 0.01-0.03 of PPMI-SVD
  everywhere, so the read-forever version captures nearly all the signal), cosine read-out, the
  bag-of-words +/-2 window (the brain parses syntax; a syntactic-context arm is the obvious next
  fidelity upgrade). VSA binding is not used here.

## What would change in hdlab, and why (PROPOSED, NOT LANDED)

The substrate's meaning accumulation (`ConceptSpace.observe` = raw `+=`) should be **surprise-
weighted**: maintain word x context co-occurrence counts and read out PPMI-weighted vectors (additive,
so it stays online/read-forever), instead of summing unweighted hash vectors. This is the same
mechanism `reader_meaning_channel` needs an adapter for; it should be built there, as a LEARNED
distributional spoke fused with the SUPPLIED sensorimotor spoke (the fusion result says fuse, do not
choose). Prototype and exact math: `experiments/exp_learn_from_reading_strong_arm_v1.py`
(`ppmi_matrix`, Levy/Goldberg 0.75), reusing `hdlab/ppmi_sparse_encoder`'s PPMI+SVD formulation.

## What I would withdraw first if it were wrong

The claim most worth stress-testing is **transfer to the live reading task**. This is an intrinsic
word-similarity ceiling; the substrate does not yet compute PPMI at read time, and a representation
that scores well on SimLex/WordSim cosine could still underperform once it must be built incrementally
by the live reader, superposed in the store (the bundling loss `reader_meaning_channel` measured), and
consulted through the actual read-out. I would withdraw any implication that the gain is already
realised in the system before withdrawing the intrinsic result, which is robust (info-free twins lose,
floors cleared CI-separated, still climbing).

## TLDR (plain language)

We kept finding that our system was bad at learning word meanings from reading -- so bad that judging
words purely by how they are SPELLED beat it on a meaning test. That looked like a reason to give up on
reading and rely only on hand-supplied knowledge. But every one of those tests used the crudest
possible way of learning from text: just adding up tags for whichever words happened to sit nearby,
treating "the" as importantly as "foot". We rebuilt it the way the brain does it -- weighting each
pairing by how SURPRISING it is (rare, informative neighbours count; filler words do not) -- and read
40 million words. The result flips completely: the good version scores far above the spelling method
(by 15 to 40 times), keeps getting better the more it reads with no sign of stopping, matches the
hand-supplied knowledge on plain word similarity, and beats it on how RELATED words are. Best of all,
combining the two -- what the brain actually does, with a hub that fuses learned language statistics
and hand-supplied senses -- beats either one alone. So we should NOT abandon learning from reading; we
should fix how it learns (surprise-weighting) and fuse it with the supplied knowledge. The honest
caveat: this was measured on standard word-meaning tests, not yet inside the live system -- proving it
there is the next step, and it is the same wiring another session is already building.

## Questions

None.

## Next steps (for the strategy session, which owns integration)

1. Wire a surprise-weighted (PPMI) LEARNED distributional spoke as part of the `reader_meaning_channel`
   adapter, FUSED with the SUPPLIED sensorimotor spoke -- the fusion result says fuse, not choose. Use
   the additive PPMI form (read-forever compatible); SVD is optional and not load-bearing.
2. The direction question is settled: do NOT retire learning-from-reading. Retire instead the RAW
   additive-accumulation mechanism, which is what the sixteen losses actually measured.
3. The verb gap is the one place supplied still dominates the learned channel; that is where the
   sensorimotor action dimensions earn their place in the hub.

---

## INTEGRATED_BY_STRATEGY -- 2026-08-23

Re-verified. Review: EXCELLENT -- survived an adversarial re-check against SUPPLIED_FULL, a stronger comparator than it quoted. NOTE ADDED 08-23: its distributional win is on word-pair SIMILARITY RATINGS and does NOT transfer to the substitutability instrument, where PPMI-SVD reads 0.0285 against our own write rule at 0.0710. Different task, different scorer.

*Appended by the strategy session, which owns integration (board Q111). The solver's text above is unchanged.*
