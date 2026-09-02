---
problem: the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold
status: REFUTED
bar: "PASS = an agent-COMPOSED, taxonomically-SMOOTHED thematic-fit store (built from raw 19c exposure, glass-box, NO LLM) that, on a CLEANED held-out 19c/literary direct-object gold (the cleaning is part of the deliverable, with its rule/criteria stated and its size reported), picks the patient CI-separated over ALL of: (1) linear position, (2) the marginal verb->object store, (3) a bag-of-args (uncomposed) store -- with an info-free AGENT-SHUFFLE twin AND a verb-shuffle twin both LOSING CI-separated; AND a demonstration that the composition margin over the marginal store is now POWERED (report n, CI half-width, null p95). BONUS/if wired: a live 19c who-did-what lift through the reader attributable to the store. A rigorous located NEGATIVE -- the cleaned gold still cannot power the composition margin, OR the knowledge is too sparse at 19c register -- is a FULL PASS if it names the ceiling with the number and mechanism. FOUNDATION IS FREE TO BUILD (a static offline store + a hand/rule-cleaned gold are admissible)."
result: "LOCATED NEGATIVE (the bar's sanctioned full-pass form), and it CORRECTS the parent's own numbers. I cleaned the 19c who-did-what gold at scale (parser-free surface rule, precision-validated) to n=669 direct-object items -- 3.9x the parent's parse-cleaned 171 -- and powering the composition margin makes it EVAPORATE, not separate. On the cleaned gold: (1) LINEAR POSITION DOMINATES -- the nearest post-verbal noun IS the patient 91.8% of the time (POS_NEAR 0.9178), and the agent-composed store scores 0.344, losing to position -0.575 CI[-0.618,-0.535]; (2) COMPOSITION DOES NOT POWER UP -- COMPOSED ties its info-free AGENT-SHUFFLE twin (+0.0065 CI[-0.0162,+0.0276], half=0.022, null_p95=0.023, n=617) and ties the MARGINAL store (-0.0097 CI[-0.0292,+0.0097]); under the parent's EXACT reachable-candidate setup at the larger gold (n=286) it is the same (COMPOSED-vs-AGENTSHUF +0.028 CI[-0.011,+0.066] ns, COMPOSED-vs-MARGINAL +0.007 ns); (3) THE PARENT'S +0.076 WAS SMALL-SAMPLE NOISE -- at n=171 subsamples of the larger gold the COMPOSED-vs-AGENTSHUF margin CI-separates only 7% of the time (mean d=+0.0285, sd=0.0164). What SURVIVES is verb-keying, not agent-composition: COMPOSED beats a bag-of-arguments twin +0.0762 CI[+0.036,+0.117] and a verb-shuffle twin +0.0891 CI[+0.045,+0.131] CI-sep -- a real verb-specific signal, but one that is crushed by linear position on this regime. THE REAL LEVER underneath is STRUCTURAL, not semantic: 89.1% of the 55 residual position errors are NP-head chunking (compound-modifier 65.5% + genitive/possessive-head 23.6%; only 10.9% is any semantic selection), and an NP-head-aware positional selector beats nearest-position +0.0433 CI[+0.0254,+0.0628] CI-sep, reaching 0.9611. THE CEILING NAMED: the 19c who-did-what gold is 100% active voice (0/5999 passive) -- the position-AMBIGUOUS patient regime where a thematic-fit store beats position (p3's modern-passive win, position 0.29) is STRUCTURALLY ABSENT from the only available 19c gold, and cleaning to direct objects REMOVES the position-ambiguity rather than creating store headroom. The genuine 19c data blocker is a position-ambiguous (non-canonical/passive) 19c patient gold, not a clean direct-object one -- and its auto-construction is blocked by 19c parser-era-robustness (p3's parser-layer negative). BRAIN-FAITHFUL POSITIVE (the fair test, on the instrument the brain actually uses): a literature drill (Competition Model; Bicknell 2010; Chersoni; Altmann-Kamide 1999; McRae 1998) confirms the negative is brain-consistent -- English who-did-what IS word-order-dominant, and the agent x verb effect is a graded PREDICTION/pre-activation phenomenon (reading-time/N400/typicality) measured where syntax already fixes the object, NOT a selection choice -- so measuring composition as selection accuracy on canonical DOs is the wrong instrument. Re-run on the RIGHT instrument (held-out forward prediction of the patient given agent x verb, n=4000 held-out 19c triples, mean reciprocal rank over a 300-patient pool): COMPOSITION IS REAL AND CI-SEPARATED -- COMPOSED beats the MARGINAL +0.0322 CI[+0.0239,+0.0401] and beats its AGENT-SHUFFLE twin +0.0403 CI[+0.0328,+0.0473] (agent-conditioning carries genuine predictive signal). So composition is a real mechanism that was MIS-TASKED as a selector; its brain-faithful home is the forward-prediction pathway (the substrate's p2 N400/surprisal organ), not the who-did-what selector."
floor: "Strongest floor actually run = LINEAR POSITION as nearest post-verbal grounded candidate (POS_NEAR) = 0.9178 on the cleaned direct-object 19c gold (n=617 composition-eligible; 0.9178 also at n=669 in the taxonomy cell). The agent-composed store (0.3436) loses to it CI-separated -0.575 CI[-0.618,-0.535]. The parent beat only the WEAK farthest-noun floor POS_FAR=0.235; POS_NEAR is the honest strong floor and was never run before. Also run: MARGINAL verb-role store 0.3533, BAG-of-arguments 0.2674, AGENT-SHUFFLE twin 0.3371, VERB-SHUFFLE twin 0.2545."
controls: "AGENT-SHUFFLE twin (agent keys permuted in the composition reweighting) -- COMPOSED does NOT beat it (+0.0065 ns, n=617; +0.028 ns, n=286 reachable) => the agent x verb conjunction carries no separable signal here (refutes the composition hypothesis). VERB-SHUFFLE twin (fillers kept, verb keys permuted) -- COMPOSED beats it +0.089 CI-sep => the verb-KEYING is real (so the agent-composition null is specific, not a dead store). BAG-of-arguments (role-collapsed) twin -- COMPOSED beats it +0.076 CI-sep => verb-specificity real. POWER SUBSAMPLE (300 reps at n=171) -- CI-separates 7% of the time => the parent's n=171 CI-sep was noise, the effect does not exist at power. POSITION floors BOTH run (POS_NEAR 0.918 strong, POS_FAR 0.235 weak) and gated on the strong one => the store loses. CLEANER PRECISION: parser-free surface rule vs tagger-ADP rule agree 98.5% (n=2801), hand-inspection sample dumped (clean=genuine direct objects, contaminated=genuine PP-obliques), independent 1500-subsample recompute of the clean share 0.284 vs landed 0.239. NP-HEAD vs NEAREST -- +0.043 CI-sep => the residual is structural. PREDICTION INSTRUMENT (the fair positive test, disjoint 80/20 build/test split, no instance leakage): AGENT-SHUFFLE twin on held-out MRR -- COMPOSED BEATS it +0.0403 CI-sep => agent-conditioning is real predictive signal (not a scoring artifact); MARGINAL baseline on MRR -- COMPOSED beats it +0.0322 CI-sep => the agent x verb conjunction predicts the held-out patient better than the verb alone. Each control excludes a specific alternative: agent-shuffle-on-SELECTION kills 'composition is the selection lever'; agent-shuffle-on-PREDICTION confirms 'composition is a real prediction mechanism'; verb-shuffle/bag confirm 'verb-keying is real'; position floor kills 'the store beats position'; NP-head locates the real (structural) selection lever; voice recompute names the absent regime; the build/test split excludes memorization on the prediction test."
files_changed: "experiments/exp_19c_composed_cleaned_gold_v1.py (the cleaner at scale + composed/smoothed store + all 9 arms on the cleaned gold + position-hard subset), experiments/exp_19c_composition_powered_v1.py (the parent's EXACT composition test powered on the larger gold + the n=171 power-subsample curve), experiments/exp_19c_whodidwhat_residual_taxonomy_v1.py (NP-head vs nearest + structural-vs-semantic error taxonomy), experiments/exp_19c_composition_as_prediction_v1.py (composition on the BRAIN'S instrument: held-out forward-prediction MRR, build/test split), experiments/exp_predictive_reader_composition_upgrade_v1.py (adjacent-component fidelity eval: composed-exemplar vs the predictive_reader organ's centroid-marginal, in the organ's 12-d grounded space AND a 100-d PPMI hub proxy), experiments/exp_composition_representation_optimization_v1.py (OPTIMIZATION: composition margin dose-response vs PPMI dimensionality + hub/spoke/concat + gamma sweep), experiments/exp_ideal_composed_predictor_v1.py (THE IDEAL predictor assembled as a brain-faithful ablation ladder -- 2.2x organ MRR, representation is the lever), experiments/exp_composition_diagnosticity_v1.py (drill: composition gain binned by gold-blind agent-shift -- raw composition HURTS high-shift), experiments/exp_composition_precision_weighted_v1.py (the fix: precision-weighted composition beats the verb-prior centroid net +0.014 CI-sep, removes the high-shift damage), experiments/exp_ideal_recipe_v1.py (THE IDEAL RECIPE assembled as a reusable IdealComposedPredictor class + PROVEN end-to-end: beats the organ +0.083 CI-sep / 2.3x MRR, both info-free twins lose, precision term earns its place), experiments/exp_whodidwhat_full_system_v1.py (the FULLY FUNCTIONAL who-did-what system: STAGE1 NP-head chunking +0.063 CI-sep -> 0.981 selection, STAGE2 order-dominant Competition-Model selection where thematic-fit adds ZERO, STAGE3 the 2.38x prediction -- one system, both jobs, each cue where it is valid), experiments/exp_more_ideal_system_v1.py (FAITHFUL implementation of the 3 brain gaps -- Bayesian multiplicative cue integration + accuracy-calibrated reliability + multimodal fusion + event context + dense-kNN coverage: HONEST NEGATIVE -- does NOT beat the hub-only ideal; the bottleneck is cue QUALITY, not the integration op; coverage 43%->98%), verification/test_19c_composed_cleaned_gold.py (witness, 14/14), data/exp_19c_composed_cleaned_gold_v1/{metrics.json,cleaner_inspection.json}, data/exp_19c_composition_powered_v1/metrics.json, data/exp_19c_whodidwhat_residual_taxonomy_v1/metrics.json, data/exp_19c_composition_as_prediction_v1/metrics.json, notes/problems/the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold/{SOLVED.md, BRAIN_MECHANISM_DRILL_composition_prediction.md, BRAIN_FIDELITY_AND_ADJACENT_COMPONENTS.md}. REUSED (not modified): experiments/exp_19c_distributional_thematic_fit_prototype_v1.py (build_dist_space PPMI-SVD), experiments/exp_19c_composition_thematic_fit_prototype_v1.py (build_avp/estimators), experiments/exp_verbrole_exemplar_which_arg_v1.py (grounded cands/lemma), hdlab/grounded_semantic_graph.py + nltk WordNet (taxonomic smoothing back-off), hdlab/distributional_meaning_channel.py (ppmi_svd)."
reverify: ".venv/Scripts/python.exe verification/test_19c_composed_cleaned_gold.py"
---

# The 19c who-did-what lever is NOT the agent-composed thematic-fit store -- powering the margin makes it evaporate, and cleaning the gold reveals linear position already solves clean direct objects

**Bottom line: REFUTED, delivered as the bar's sanctioned LOCATED NEGATIVE -- and it corrects two of the parent's
own numbers.** I did exactly what the brief asked: cleaned the ~85%-oblique 19c who-did-what gold to a *larger*
direct-object test (n=669, 3.9x the parent's 171, precision-validated), built the agent-COMPOSED,
taxonomically-SMOOTHED thematic-fit store from raw 19c exposure, and powered the composition margin. **Powering it
does not CI-separate it -- it collapses it to zero.** The parent's `+0.076 vs agent-shuffle CI-sep` at n=171 was a
small-sample artifact (at that n it separates only 7% of the time), and the parent's `+0.158 over position` beat a
*weak* floor (the farthest noun, 0.235); the honest strong floor (nearest post-verbal noun) is **0.918** and it
dominates every store. The real residual on clean 19c who-did-what is **structural (NP-head chunking), not
semantic** -- so a thematic-fit store, composed or not, is not the lever.

## WHAT I BUILT (all glass-box, no LLM, parser-free where it matters)
1. **The cleaner, at scale (the deliverable's first half).** A *parser-free* surface rule -- open verb; post-verbal
   gold; **no preposition** (modern or archaic -- by tagger-ADP OR an expanded `CLEAN_PREPS` wordlist that adds
   `amongst/unto/upon/as/down/toward/within/...`) strictly between the verb and the gold; gold among >=2 grounded
   candidates. It is parser-free deliberately: p3's 19c negative was that *the modern parser is too degraded on
   archaic prose to extract clean structure*, so I do not lean on it. **Result: 669 clean direct-object items out
   of 2,801 post-verbal open-verb items = 23.9% clean, 76.1% oblique-contaminated** (the parent's parse-based
   ~85% is the same story by a stricter rule). **Cleaner precision validated three ways:** surface-rule vs
   tagger-ADP rule agree **98.5%** (n=2801); an independent 1,500-item subsample recomputes the clean share at
   0.284 (landed 0.239); and the dumped hand-inspection sample is clean (CLEAN = `kept->suitors`,
   `devastated->country`, `entertained->friends`; CONTAMINATED = `retired->earth` in "from the face of the earth",
   `sits->court` in "at the very heart of the fog") -- see `cleaner_inspection.json`.
2. **The store (the deliverable's second half).** Register-native PPMI-SVD space over 120k held-out 19c LitBank
   sentences (`distributional_meaning_channel.ppmi_svd`); verb->patient exemplars and (agent,patient) pairs by
   proximity extraction from raw exposure; **COMPOSED** = `P(patient|agent,verb)` (agent-conditioned exemplar
   reweighting, Erk-Pado EPP-style); **COMPOSED_SMOOTH** = Resnik taxonomic back-off of OOV candidates through
   WordNet synonyms/hypernyms into the in-space vectors; plus **MARGINAL**, **BAG**-of-arguments, **INTEGRATED**
   (position x fit), and the info-free **AGENT-SHUFFLE** and **VERB-SHUFFLE** twins.

## THE THREE FINDINGS (worst-first)

### 1. Linear position DOMINATES clean direct-object selection -- cleaning removes the headroom, it does not create it
| arm | acc on cleaned DO gold (n=617) |
|---|---|
| **POS_NEAR (nearest post-verbal noun)** | **0.9178** |
| INTEGRATED (position x composed fit) | 0.8363 |
| MARGINAL verb-role store | 0.3533 |
| COMPOSED `P(patient|agent,verb)` | 0.3436 |
| COMPOSED_SMOOTH | 0.3436 |
| AGENT-SHUFFLE twin | 0.3371 |
| BAG-of-arguments | 0.2674 |
| VERB-SHUFFLE twin | 0.2545 |
| POS_FAR (farthest -- the parent's floor) | 0.2350 |

`COMPOSED - POS_NEAR = -0.575 CI[-0.618,-0.535]`. In canonical active SVO English **the direct object *is* the
nearest post-verbal noun** -- so cleaning the gold to direct objects lands the metric squarely in the regime where
position is strongest and a thematic-fit store has nothing to add. The brief's implicit premise (clean DOs give the
store headroom over position) is exactly backwards: cleaning *removes* position-ambiguity.

### 2. Powering the composition margin EVAPORATES it (the parent's number was noise)
| contrast | parent (n=171) | this work, all-grounded cands (n=617) | this work, parent's reachable cands (n=286) |
|---|---|---|---|
| COMPOSED vs AGENT-SHUFFLE | +0.076 CI[+0.029,+0.123] **CI-sep** | **+0.0065 CI[-0.016,+0.028] ns** | **+0.028 CI[-0.011,+0.066] ns** |
| COMPOSED vs MARGINAL | +0.041 (ns) | **-0.0097 CI[-0.029,+0.010] ns** | **+0.007 CI[-0.028,+0.042] ns** |
| COMPOSED vs BAG | +0.076 (ns) | +0.076 CI[+0.036,+0.117] CI-sep | +0.066 CI[+0.004,+0.133] CI-sep |
| COMPOSED vs VERB-SHUFFLE | -- | +0.089 CI[+0.045,+0.131] CI-sep | -- |

Under **both** candidate definitions, at power, agent-composition ties its agent-shuffle twin AND ties the
marginal. The **power subsample is decisive**: drawing n=171 items (the parent's n) from the larger clean gold 300
times, COMPOSED-vs-AGENT-SHUFFLE CI-separates **only 7% of the time** (mean d=+0.0285). The parent landed in that
7% tail. What *does* survive every twin is **verb-keying** (COMPOSED/MARGINAL beat BAG and VERB-SHUFFLE CI-sep) --
a real verb-specific selectional signal, consistent with p3 -- but it is a ~0.35-accuracy signal against a
0.918 positional floor, so it moves nothing on this task.

### 3. The REAL residual is STRUCTURAL (NP-head), not semantic -- so I solved the problem underneath a different way
POS_NEAR misses 8.2% (55/669). Taxonomizing those errors: **89.1% are NP-head chunking** -- 65.5%
compound-modifier ("drove a *trade delivery* **van**" -> nearest picks `trade`, gold is `van`) + 23.6%
genitive/possessive-head ("entered an *officers'* **hospital**", "left the *undertaker's* **shop**" -> nearest
picks the possessor, gold is the head). Only **10.9% (6 items)** is any kind of semantic selection, and those are
mostly ditransitive/small-clause ("call her father's bungalow a **place**"). An NP-head-aware positional selector
(rightmost noun of the first post-verbal noun-run) beats nearest **+0.0433 CI[+0.0254,+0.0628] CI-sep, reaching
0.9611**. **The lever for clean 19c who-did-what is NP-head identification (compound + genitive chunking) -- a
parser/chunker refinement -- not a thematic-fit store.**

## THE CEILING, NAMED (per the bar)
- **The position-ambiguous patient regime is structurally ABSENT from the 19c gold.** LitBank drop-fill is
  **100% active voice (0/5999 passive)**. The regime where a thematic-fit store *does* beat position -- passive /
  patient-preverbal, where p3 measured position at 0.29 and the structured store won -- simply is not in the only
  19c who-did-what gold we have. On the regime we *do* have (canonical active DOs), position wins by construction.
- **So the genuine 19c data blocker is not a clean direct-object gold (I built that, 669 items) -- it is a
  position-AMBIGUOUS 19c patient gold** (passive / fronted / relative), which does not exist and whose automatic
  construction is blocked by the same 19c **parser-era-robustness** wall p3 located (the modern parser degrades on
  archaic prose, so it cannot reliably extract non-canonical argument structure to build such a gold).
- **The store is a real mechanism where position fails (cited, not re-derived):** p3 established the structured
  verb-role store beats position +0.14 CI-sep on the MODERN passive slice. My composition layer adds nothing on
  19c only because the 19c regime has no position-ambiguity, not because the mechanism is dead.

## IS THE WALL BRAIN-FAITHFUL? -- yes, and the mechanism is real on the instrument the brain ACTUALLY uses
A miss is not a ceiling until two gates pass: FAIR TEST and EXACTLY-LIKE-THE-BRAIN. A literature drill
(`BRAIN_MECHANISM_DRILL_composition_prediction.md`) closes both, and it forced the decisive reframe.
- **The negative is brain-CONSISTENT, not an implementation failure (4 pillars, high confidence).** (1) COMPETITION
  MODEL (Bates & MacWhinney; MacWhinney, Bates & Kliegl 1984): English who-did-what is WORD-ORDER-dominant --
  when order conflicts with animacy, English speakers follow ORDER (Italian/German follow morphology). So
  position=0.918 on clean active DOs is the English cue hierarchy showing through, exactly as the brain does it.
  (2) The BICKNELL 2010 / CHERSONI agent x verb effect is measured as reading-time / N400 / plausibility-typicality
  on items where SYNTAX ALREADY FIXES the object ("mechanic checked the brakes" vs "journalist checked the spelling"
  -- patient is post-verbal by position in both; only its predictedness differs) -- a graded PREDICTION signal, NOT
  an argument choice. (3) ALTMANN & KAMIDE 1999 / KUTAS-FEDERMEIER: thematic fit is forward PRE-ACTIVATION of the
  upcoming argument; McRae/Spivey-Knowlton/Tanenhaus 1998: it changes the SELECTION/parse only at points of
  SYNTACTIC AMBIGUITY -- absent from a 100%-active gold. (4) NP-head finding (compound Right-hand Head Rule; genitive
  DP-head) is a distinct SYNTACTIC operation that precedes role assignment -- so "89% structural" is a real level
  distinction. **Verdict: measuring composition as SELECTION accuracy on canonical DOs is the wrong instrument;
  position beating fit there is what the brain does.**
- **So I ran the FAIR test -- composition on the brain's ACTUAL instrument (forward prediction), and WE CAN DO IT.**
  `exp_19c_composition_as_prediction_v1`: disjoint 80/20 build/test split of raw 19c exposure (no instance leakage);
  held-out (agent, verb, patient) triples; rank the TRUE patient among a 300-patient pool by mean reciprocal rank
  -- the graded held-out-likelihood analogue of the Bicknell prediction measure. On n=4000 held-out triples:

  | arm | MRR | hit@10 |
  |---|---|---|
  | MARGINAL `P(patient|verb)` | 0.1267 | 0.2512 |
  | **COMPOSED `P(patient|agent,verb)`** | **0.1590** | **0.2680** |
  | AGENT-SHUFFLE twin | 0.1187 | 0.1995 |

  **COMPOSED beats MARGINAL +0.0322 CI[+0.0239,+0.0401] CI-sep and beats its AGENT-SHUFFLE twin +0.0403
  CI[+0.0328,+0.0473] CI-sep.** The agent x verb conjunction genuinely predicts the held-out patient better than the
  verb alone, and a WRONG agent loses -- the Bicknell/Chersoni mechanism, replicated on our 19c substrate, on the
  metric the brain uses. **This does NOT revive the selection negative** (position still dominates canonical-DO
  selection); it establishes that composition is a REAL mechanism that was MIS-TASKED as a selector. Its
  brain-faithful home is the forward-PREDICTION pathway (the substrate's p2 N400/surprisal organ), where prediction
  is not pre-empted by word order -- not the who-did-what selector. *This is the load-bearing guard: "not a
  selection lever in position-dominant English" must NOT be read as "not a mechanism." The mechanism is real; the
  instrument was wrong.*

## WHY THE BRIEF (and the parent) POINTED HERE, AND WHAT IT GOT WRONG
The parent's "27% reachable-but-mispicked = SELECTION" and "composition +0.076 CI-sep" both came from a
72-85%-oblique-contaminated gold and a weak (farthest-noun) position floor. Cleaning the gold and running the
strong floor dissolves both: the "selection gap" was mostly gold contamination, and the clean residual is 89%
structural. This does not fault the parent's diagnosis discipline -- it is exactly the "clean the gold before
quoting a target number" caveat the parent's own drill flagged, now cashed out.

## KEY REALIZATIONS (the moves that turned the brief's build into a refutation)
- **Run the STRONG floor, not the convenient one.** The parent beat the farthest-noun floor (0.235); the honest
  floor is the nearest noun (0.918). Swapping the floor -- not any new model -- is what flipped the verdict. *A
  weak floor gaming a metric is the same failure as an info-free twin gaming it, just in the other direction.*
- **"Underpowered" can mean the effect isn't there.** The brief read n=171 `+0.076 ns-on-the-margin` as "needs a
  bigger gold to confirm a real effect." Powering it (4x the n, plus a 300-rep subsample at the old n) showed the
  point estimate marching to +0.03 and separating 7% of the time -- the null was the truth, not low power. *Power
  a promising margin before building on it; do not assume size will rescue it.*
- **Cleaning a gold can DELETE the phenomenon, not just de-noise it.** Restricting to clean direct objects removed
  precisely the position-ambiguity that would let a thematic-fit store matter. *Ask what a filter removes, not just
  what it purifies.*
- **Inspect the residual before naming the lever.** Reading the 55 position errors (not just their count) showed
  89% are compound/possessive NP-heads -- a chunking problem wearing a "selection" costume. *The error taxonomy,
  not the aggregate accuracy, located the real lever.*
- **Parser-free cleaning dodged p3's wall.** Building the clean gold from surface cues (tagger-ADP + prep wordlist)
  rather than the arc-eager parse sidesteps the 19c parser-degradation that blocked p3's no-gold store -- and it
  is what made the 3.9x-larger gold possible.
- **A SMALL NET EFFECT can be an ESTIMATOR under-regularization, not a ceiling -- drill it before believing it.**
  Precision-weighted composition beats the verb-prior base +0.014 CI-sep where the RAW estimator was +0.005 ns,
  because raw composition HURT on high-agent-shift items (sparse evidence -> spurious over-commitment). The brain's
  fix (Friston precision-weighting -- already the `predictive_reader` organ's stated principle, just unimplemented)
  removed the damage. *When a real mechanism's net gain is surprisingly small, bin the gain by where it should fire
  and check whether it is HURTING somewhere -- an under-regularized estimator can cancel its own signal.*
- **THE WRONG INSTRUMENT can null a real mechanism.** Composition ties every twin on SELECTION accuracy yet beats
  them CI-sep on forward PREDICTION (held-out MRR) -- because the brain's agent x verb effect IS a prediction/N400
  phenomenon (Bicknell), and position pre-empts it on canonical-DO selection. *Before calling a brain mechanism
  dead, test it on the behavioural signature the brain actually shows it on -- selection accuracy and reading-time
  prediction are different instruments and this one flips the verdict.* This is the move that turned a flat
  negative into a brain-faithful "refuted-as-asked, validated-and-re-homed."

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **The parent's `composition beats agent-shuffle +0.076 CI-sep (n=171)` does NOT survive powering** -- at n=617
  it is +0.0065 ns; at the parent's reachable-candidate setup (n=286) +0.028 ns; a 300-rep n=171 subsample
  separates only 7% of the time. Re-scope: agent-composition (`P(patient|agent,verb)`) is NOT a demonstrated 19c
  who-did-what lever. What survives is verb-keying (beats bag/verb-shuffle), consistent with p3.
- **The parent's `composition/selection beats position +0.158` beat a WEAK farthest-noun floor.** The strong floor
  (nearest post-verbal noun) is 0.918 on the cleaned direct-object gold; every store loses to it. The 19c
  who-did-what "selection gap" (base 0.43) was ~76% gold oblique-contamination, not a selection failure.
- **On clean 19c who-did-what the residual is 89% STRUCTURAL (NP-head: compound 65% + genitive 24%), <=11%
  semantic.** The lever is NP-head chunking (a positional NP-head selector beats nearest +0.043 CI-sep, reaching
  0.961), not a thematic-fit/composition store.
- **The 19c who-did-what gold is 100% active voice (0 passive).** The position-ambiguous patient regime where a
  thematic-fit store beats position is absent; the genuine data blocker is a position-ambiguous 19c gold, blocked
  by 19c parser-era-robustness (p3). Flag the LitBank drop-fill population as canonical-active-only for any 19c
  selection claim.
- **Agent x verb COMPOSITION is a real FORWARD-PREDICTION mechanism on 19c (NEW, brain-faithful positive):** on the
  brain's actual instrument (held-out patient prediction, MRR) COMPOSED beats the marginal +0.032 CI-sep and its
  agent-shuffle twin +0.040 CI-sep (n=4000). It was mis-tasked as a who-did-what SELECTOR (where English word-order
  dominance and the 100%-active regime pre-empt it). Its brain-faithful home is the FORWARD-PREDICTION organ
  (`hdlab/predictive_reader`), not the who-did-what role selector. This aligns the audit's "selection store" entry with
  the Competition Model: fit is a prediction/pre-activation cue, secondary to word order for English who-did-what.
- **Composition is REPRESENTATION-bounded, and the differ is precisely located (NEW):** `hdlab/predictive_reader`
  predicts from the marginal role-specific CENTROID over a 12-d sensorimotor SPOKE (Lancaster). In that 12-d space
  agent-composition ties its agent-shuffle twin (+0.002 ns) and the exemplar beats the centroid (+0.036); in a 100-d
  register-native PPMI-SVD HUB proxy, composition is real (+0.040 vs agent-shuffle CI-sep) and the composed-exemplar
  beats the organ's centroid-marginal +0.014 CI-sep (`exp_predictive_reader_composition_upgrade_v1`, n=4000). Per the
  drill (Lambon Ralph 2017 Controlled Semantic Cognition; Frankland & Greene 2015): fine agent individuation lives in
  the high-D transmodal ATL HUB, not the low-D sensorimotor SPOKES -- so the fix is REPRESENTATIONAL (feed hub-grade
  high-D fillers into the conjunction), NOT algebraic. KEEP FHRR (the binding algebra is already high-D and faithful).
- **The `graded_role_assigner` Competition-Model cue set is MISSING morphological CASE (NEW, verified on disk):** its
  cues are [order, adjacency, passive_strong, passive_weak, gap, unacc, byagent, animacy] -- no nominative/accusative
  (he/him, who/whom). Case is the highest-validity cue where it exists and is BETTER PRESERVED IN 19c prose -- the
  cheapest fundable who-did-what SELECTION lever, and it is register-matched.

## WHAT I WOULD WITHDRAW FIRST IF WRONG
The whole negative rests on **nearest-post-verbal being the fair "linear position" floor.** If the intended
who-did-what task is specifically the *non-canonical* subset (where nearest fails by construction), then position
is not 0.918 and a store could matter -- but that subset is 0% of this 19c gold (0 passive) and I could not build
it without the parser p3 showed is too degraded. Second: the composition null is on a proximity-extracted store; a
*parse*-typed agent/patient store might carry more agent x verb signal -- but p3 already showed the 19c parse is
too degraded to extract clean typed slots, so this is the same wall, and the verb-keying signal that *does* survive
already ties position, so even a better store would not clear the floor here.

## TLDR (plain English)
The job was to fix "who did what" on 200-year-old prose by cleaning up the noisy answer key and building a
memory-of-typical-events that combines the doer and the action to guess the thing-done-to. I cleaned the answer key
properly (it was about three-quarters polluted with the wrong kind of word) and got a test four times bigger than
before. Two things then became clear. First, on the clean test the "memory of typical events" idea does not
actually help: once you give it enough data to measure honestly, combining the doer and the action adds essentially
nothing over just the action, and the earlier small-sample result that said it helped was a fluke. Second, and more
importantly, on clean sentences the boring rule "the thing right after the verb is what the verb acts on" is already
right about 92% of the time -- so there is almost no room for a cleverer meaning-based method to help. The few
mistakes it makes are almost all about picking the wrong word inside a two-word name ("trade delivery *van*" ->
grabbing "trade") or a possessive ("the undertaker's *shop*" -> grabbing "undertaker"), which is a grammar-chunking
fix, not a meaning fix. The real missing ingredient for this to be a hard "who did what" problem is old-prose
sentences with unusual word order (like the passive "the letter was written by..."), and those simply are not in
the available old-prose test set -- and we can't reliably auto-build them because the grammar-reader is too shaky on
old prose. So: clean answer key built and delivered; the meaning-memory idea is honestly refuted for this task; the
genuine fix is better grammar-chunking, and the genuine missing data is unusual-word-order old prose.
**One important twist, to be fair to the meaning-memory idea and to how the brain works:** the brain's own version
of "combine the doer and the action" is not used to CHOOSE which word is the object -- in English the brain mostly
uses word order for that. It is used to PREDICT/anticipate the likely next word (which is why psychologists measure
it with reading speed and brain waves, not with which-word-is-it choices). When I test our version the same way the
brain is tested -- does combining doer+action predict the actual upcoming word better than the action alone -- it
DOES, reliably (and using the wrong doer breaks it). So the meaning-memory is a real, working ability; it was just
being graded on the wrong test. Its right job is prediction/anticipation, and it belongs with the part of the
system that predicts upcoming words, not the part that labels who-did-what.

## QUESTIONS
None blocking. Two routing decisions for strategy (both with a recommendation):
1. The demonstrated-real lever on clean 19c who-did-what SELECTION is **NP-head chunking** (+0.043 CI-sep, reaching
   0.961) -- a parser/chunker refinement, not a meaning store. My recommendation: file a small
   `reader_picks_np_modifier_not_head` problem (compound + genitive head selection), a clean measurable structural win.
2. Agent x verb **composition** is real on the PREDICTION instrument (+0.032 MRR CI-sep). My recommendation: route it
   to the **forward-prediction pathway** (the p2 N400/surprisal organ), evaluated on a graded prediction/typicality
   metric -- NOT the who-did-what selector, where it is dominated by word order (brain-faithful, per the Competition
   Model). Do NOT fund a bigger-gold composition SELECTION build (I built the bigger gold; selection ties its twin).

## NEXT STEPS FOR STRATEGY (ordered)
1. **Retire "agent-composition is the 19c who-did-what SELECTION lever" -- but KEEP the mechanism, re-homed.** It
   ties its info-free twin on SELECTION at power (the parent's n=171 CI-sep was noise, 7% at power); do NOT fund a
   bigger-gold composition SELECTION build (I built the bigger gold and it kills the selection effect). BUT on the
   brain's actual instrument (forward PREDICTION) composition is REAL: +0.032 MRR over marginal, +0.040 over
   agent-shuffle, CI-sep (n=4000). Route composition to the FORWARD-PREDICTION organ (`hdlab/predictive_reader`),
   not the role selector -- this is where the brain shows the Bicknell effect. **CANDIDATE NEXT PROBLEM (measured,
   de-risked):** upgrade `predictive_reader` from marginal-CENTROID-over-12d-SPOKE to agent-COMPOSED-EXEMPLAR over
   HUB-grade (register-native high-D) fillers -- +0.014 MRR CI-sep over the organ's current method; a REPRESENTATION
   swap (spoke->hub proxy), KEEP FHRR. OPTIMIZED SETTINGS (measured dose-response,
   `exp_composition_representation_optimization_v1`): the composition margin GROWS monotonically with representational
   capacity (12-d spoke +0.002 ns -> 200-d hub +0.044 CI-sep; MRR 0.059 -> 0.164, peaks ~200 dims), gamma~3.0, and
   do NOT naively concat spoke+hub (dilutes). This confirms representation is the bottleneck. See
   `BRAIN_FIDELITY_AND_ADJACENT_COMPONENTS.md` Part 3.
2. **The clean 19c who-did-what residual is STRUCTURAL:** file/route NP-head chunking (compound + genitive head
   selection), which recovers most of the 8% residual (POS_NPHEAD 0.961, +0.043 CI-sep). This is the real,
   measurable lever for this metric.
2b. **MISSED CHEAP CUE -- morphological CASE (NEW, verified on disk):** `hdlab/graded_role_assigner`'s Competition-
   Model cue set [order, adjacency, passive_strong, passive_weak, gap, unacc, byagent, animacy] has NO
   nominative/accusative cue (he/him, who/whom). Case is the highest-validity who-did-what cue where it exists and is
   BETTER PRESERVED in 19c prose -- the cheapest fundable selection lever, register-matched. **File it as the top
   adjacent next problem.** (Full adjacent-component evaluation + wall-drill: `BRAIN_FIDELITY_AND_ADJACENT_COMPONENTS.md`.)
3. **Correct the baseline board's 19c who-did-what arm:** the ~0.43 number is ~76% gold oblique-contamination.
   Report the CLEANED-gold number (position ~0.92) as the honest who-did-what accuracy on canonical active 19c DOs;
   the "selection gap" was mostly measurement.
4. **The genuine 19c data blocker is a position-AMBIGUOUS (non-canonical/passive) 19c patient gold**, not a clean
   direct-object one. Building it needs 19c-robust parsing/SRL (p3's parser-era-robustness wall). Only there would
   a thematic-fit store (which p3 already proved on MODERN passive) have a chance to matter at 19c.
5. **Keep the composed/verb-keyed store for where position FAILS** (modern passive, p3's regime) -- it is a real
   verb-specific signal (beats bag/verb-shuffle CI-sep); just do not deploy it as a standalone 19c who-did-what
   selector, where it is dominated by position.
6. **DO NOT** re-open the parse/POS-data, PP-attachment, or register-tagging routes (parent-refuted), and DO NOT
   re-run the composition margin expecting a bigger gold to separate it (it does the opposite).
