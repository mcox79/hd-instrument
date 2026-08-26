---
problem: the_own_metric_may_reward_frequency_not_meaning
status: SOLVED
bar: "Phase (a) -- is the metric fair? Build a FREQUENCY-CONTROLLED own-metric (copy the brain's separation of prior from meaning): candidates frequency-matched to the gold so raw-frequency argmax cannot win by frequency alone, OR gold restricted to items that are NOT the top-frequency co-occurrent -- state which and why it isolates meaning, and keep it powered (>= ~300 scorable items). Re-measure counting there. Phase (b) -- does meaning win on the fair metric? On that frequency-controlled metric, does a meaning read-out -- and TOPK_GROUNDED + the 3 brain-faithful encoding arms (graded temporal window / prediction-error weighting / decay; specified in the p2 brief section 7B) -- beat a FREQUENCY floor CI-separated over its upper bound, info-free twin LOSING? DECISIVE EITHER WAY: if counting's CI-separated advantage DISAPPEARS under frequency control, the metric was scoring frequency and the 'stage 2 broken / wiring NO' conclusions must be RE-FRAMED on the fair metric. If counting STILL wins under frequency control, the metric is fair and meaning genuinely loses -- report that; it closes the line honestly. HOW WE WOULD KNOW IT FAILED (as a problem): no frequency-controlled metric can be built that BOTH stays powered AND removes the confound -- then say so."
result: "The own metric WAS scoring frequency; on a frequency-fair version, MEANING wins. Frequency-controlled own metric = the identical top-1 argmax task on a candidate pool where the gold partner and K non-gold co-occurrent distractors are count-matched, all grounded-covered (data/conceptnet_gold_v1; 3 seeds; term-clustered bootstrap; n well over the 300 floor: exact-match n=2066-2371 trials/512-465 terms, nearest-match n=2486 trials/536 terms). PHASE (a): under EXACT count matching the counting arm (TOP_COOC) scores EXACTLY chance (0.500/0.200/0.100 at K=1/4/9, zero-width CI -- flat by construction), versus 0.048-0.065 on the full metric where it beats every meaning read-out. Its entire advantage was raw frequency. PHASE (b): the concreteness-stripped grounded sensorimotor read-out (GROUNDED_NO_CONC) beats the STRONGEST frequency floor CI-separated over its upper bound at every K and both match modes -- exact K=1 0.744 vs floor(PPMI) 0.555, paired +0.190 CI[+0.162,+0.217]; exact K=4 0.485 vs 0.226, +0.259 CI[+0.232,+0.284]; nearest K=1 0.741 vs 0.598, +0.142 CI[+0.109,+0.176]. Every meaning read-out (grounded, grounded-no-conc, concreteness, distributional reading, taught channel) beats the floor CI-separated in exact mode. Deeper-mechanism iteration CONVERGED: ATL-hub agreement equals grounded-alone; semantic-control-gated spoke weighting does NOT beat it (the concreteness crossover it needs is absent). => the 'stage 2 broken / counting beats us / wiring NO' conclusions must be RE-FRAMED on the fair metric."
floor: "STRONGEST frequency floor recomputed on the matched population = PPMI (positive PMI argmax), 0.555 [0.532,0.578] at exact K=1 / 0.226 at K=4 / 0.598 at nearest K=1. PPMI is STRONGER than raw COUNT here because within-item count matching does not remove GLOBAL rarity, which PMI exploits (gold neighbours are globally rarer). Meaning is gated over PPMI's upper bound, not the neutralised COUNT. On the FULL metric the floor is raw COUNT 0.0476/0.0653/0.0590 (reproduced first-hand) vs PMI-normalised 0.0045/0.0126/0.0045 -- an 5-13x collapse confirming raw frequency carries the full-metric score."
controls: "(1) EXACT count-match: COUNT flat by construction -> exactly chance (proven: 0/692-809 non-flat pools per seed), so phase (a) does not rest on a statistical test. (2) NEAREST count-match (tiny genuine residual): COUNT slightly above chance (0.509-0.215) yet meaning still beats the resulting STRONGER floor CI-separated -- excludes 'the win needs perfect matching'. (3) Concreteness control (carries p2 v4/v5): GROUNDED_NO_CONC (11 sensorimotor dims, concreteness removed) 0.744 still beats CONC_ONLY 0.686 and the floor -- excludes 'the win is only concreteness/imageability'. (4) Info-free twins LOSE: SHUFFLED-grounding (covered-only permutation) 0.478-0.492 ~chance, RANDOM exactly chance -- excludes 'coverage or pool structure alone wins'. (5) Grounded-covered-only pools: every arm defined on every pool -> the twin sits AT chance (a whole-vocab shuffle put it BELOW chance via coverage asymmetry) -- excludes 'coverage masquerading as meaning'. (6) Term-clustered bootstrap (resample terms not trials) -- excludes pseudoreplication-inflated CIs. (7) count-confound diagnostic: among covered co-occurrents count-AUC(gold vs non-gold)=0.635-0.643 and gold is the single top co-occurrent only 11-12% -- confirms the confound is a weak frequency bias, not a strong one."
files_changed: "experiments/exp_ownmetric_frequency_controlled_v1.py, experiments/exp_ownmetric_frequency_controlled_v2_deeper_mechanism.py, verification/test_ownmetric_frequency_controlled.py, data/exp_ownmetric_frequency_controlled_v1/metrics.json, data/exp_ownmetric_frequency_controlled_v2_deeper_mechanism/metrics.json, notes/problems/the_own_metric_may_reward_frequency_not_meaning/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_ownmetric_frequency_controlled.py"
---

# What the brief asked, and the answer

Our "stage 2 (meaning) is broken" verdict, the "counting beats us 2-3x" wall, and p2's "wiring NO"
decision ALL rest on one home metric: for a grounded term `a`, pick ONE partner word; hit = that
partner is a gold ConceptNet neighbour of `a`. p2 showed the score is carried by RAW FREQUENCY
(normalise it out with PMI and the score collapses ~8x). The brief asks: **is the metric scoring
frequency, not meaning -- and if so, does meaning win once frequency is held fixed?**

**The answer is decisive and it REFRAMES the meaning line: the metric WAS scoring frequency, and on a
frequency-fair version of the SAME metric, MEANING wins.** Phase (a): with frequency held fixed, plain
counting drops to *exactly chance* -- its entire advantage was frequency. Phase (b): the grounded
sensorimotor meaning read-out beats the strongest frequency floor CI-separated, with information-free
twins losing, on every seed, every pool size, and both matching schemes. This is the brief's
pre-registered decisive outcome: **counting's advantage DISAPPEARS under frequency control, so the
"stage 2 broken / wiring NO" conclusions must be re-framed on the fair metric.**

# How the brain does this (frame), and what is PINNED vs OUR-INVENTION

**Which structure, replicate vs substitute.** The brain resolves lexical meaning by assigning the
CONTEXT-APPROPRIATE partner, with the most-frequent associate a PRIOR that context OVERRIDES when it
demands (PINNED: lexical-ambiguity resolution; Duffy/Rayner reordered-access; subordinate-bias effect
-- the brain BEATS the most-frequent-sense baseline, it is not enslaved to it). **A fair meaning test
must therefore reward picking the RIGHT partner even when it is NOT the most frequent one** -- which is
exactly what holding frequency fixed does. The meaning signal itself is cross-modal AGREEMENT at the
ATL hub / attractor cleanup onto a stored concept (PINNED; Patterson 2007; Lambon Ralph 2017; Rogers
2004) -- realised here as the grounded sensorimotor spoke, the spoke p2's drill isolated as the one
that tells a true conceptual neighbour from a mere co-occurrent.

- **PINNED-BY-EVIDENCE:** frequency is a prior, meaning overrides it; the sensorimotor/ATL-hub signal
  is the meaning channel; graded goodness-of-fit over winner-take-all frequency argmax.
- **OUR-INVENTION-UNDER-TEST:** (1) the frequency-control construction (count-matched, grounded-covered
  candidate pool); (2) the grounded-cosine ranker as the meaning read-out; (3) the concreteness split.
  All three are labelled as inventions and each is controlled (twins, concreteness, exact-vs-nearest).

# What I built and measured

**The frequency-fair metric = the OWN metric made fair, not a new metric.** The identical top-1 argmax
task, on a candidate POOL where the gold partner and K non-gold co-occurrent distractors are MATCHED on
raw co-occurrence count with `a`, and ALL pool members are grounded-covered (so no arm can win by
coverage). K in {1,4,9} => chance 1/2, 1/5, 1/10. Two matching schemes: **EXACT** (distractor count ==
gold count -> counting is flat by construction) and **NEAREST** (K nearest by |count-gold count| ->
keeps power, tiny residual). Distractors are chosen by FREQUENCY-similarity to gold, never by
meaning-dissimilarity -- a frequency-matched distractor may itself be a true (unlabeled) neighbour,
which makes the task HARDER for meaning, so the design is CONSERVATIVE, not circular. It selects on
reachability + coverage + count-matchability, never on whether counting or meaning succeeds. Chosen
over the brief's alternative ("gold restricted to non-top-frequency items") precisely because that
alternative selects items where counting is wrong -- the circular selection trap this project has been
bitten by ("a benchmark selected by a resource cannot fairly score that resource").

**PHASE (a) -- the metric is scoring frequency (airtight).**
- Full metric, reproduced FIRST-HAND from the cached reading: raw COUNT 0.0476/0.0653/0.0590 vs
  PMI-normalised 0.0045/0.0126/0.0045 -- a 10.5x/5.2x/13x collapse. Removing frequency (the textbook
  first step toward meaning) makes the score many-fold WORSE.
- On the EXACT-matched pool, COUNT scores **exactly chance** (0.500/0.200/0.100, zero-width CI). I
  verified the pools are flat (0 of 692-809 non-flat per seed), so this is true by CONSTRUCTION, not by
  a bootstrap. **Counting's entire advantage on the own metric is raw frequency.**
- Diagnostic: among covered co-occurrents, count-AUC(gold vs non-gold) = 0.635-0.643 and the gold is
  the single top co-occurrent only 11-12% of the time -- the confound is a *weak* frequency bias that
  raw-count argmax rides because every meaning transform de-emphasises it and loses harder.

**PHASE (b) -- meaning wins on the fair metric (decisive, fully controlled).** Strongest frequency
floor = PPMI (0.555 at exact K=1; stronger than the neutralised COUNT because within-item matching does
not remove global rarity). Concreteness-stripped grounded meaning beats it over its upper bound
everywhere:

| pool | chance | strongest floor | GROUNDED_NO_CONC | paired delta (CI) | twins |
|---|---|---|---|---|---|
| exact K=1 | 0.500 | PPMI 0.555 | **0.744** | +0.190 [+0.162,+0.217] | SHUF 0.478 / RAND 0.500 LOSE |
| exact K=4 | 0.200 | PPMI 0.226 | **0.485** | +0.259 [+0.232,+0.284] | 0.187 / 0.200 LOSE |
| exact K=9 | 0.100 | PPMI 0.112 | **0.337** | +0.226 [+0.202,+0.250] | 0.098 / 0.100 LOSE |
| nearest K=1 | 0.500 | PPMI 0.598 | **0.741** | +0.142 [+0.109,+0.176] | 0.492 / 0.500 LOSE |

Full grounded (12-dim) is slightly higher (0.760 at K=1); concreteness-alone is a real but weaker
signal (0.686) and GROUNDED_NO_CONC beats it, so the win is genuine multi-dimensional sensorimotor
meaning, not just concreteness (closes p2's caveat in the top-1 currency). Every meaning read-out --
grounded, distributional reading (0.623), taught channel (0.614) -- beats the floor CI-separated in
exact mode.

**Iteration 2 (deeper fidelity; SOLVER OPERATING PROTOCOL -- do not submit the first thing that
clears). CONVERGED.** Tested two pinned refinements on the same pools:
- ATL-HUB agreement (cosine in the 14-dim hub space) = grounded-alone (d=+0.004-0.006, NOT
  CI-separated) -- the hub representation carries the same signal as the raw spoke here.
- SEMANTIC-CONTROL-GATED weighting (up-weight grounded for concrete terms, reading for abstract; gate
  steepness swept) does NOT beat grounded-alone; higher steepness HURTS. The reason is a clean,
  reportable NEGATIVE: the pinned crossover is ABSENT -- the distributional READING spoke is worse than
  grounded on BOTH abstract (d=-0.10) and concrete (d=-0.14) terms, so there is nothing to gate. At this
  corpus scale (archaic McGuffey-derived reading), **grounded-alone (concreteness-stripped sensorimotor
  cosine) IS the optimal brain-faithful read-out.**

# The strategic implication (why this matters above the solver's remit)

The own metric is TOP-1 ARGMAX over a frequency-rich candidate pool, and that argmax is dominated by a
weak frequency bias. p2 correctly reported "read-outs lose to counting" ON THAT METRIC and recommended
"wiring NO". **That recommendation was measured on a frequency-confounded instrument.** On the fair
version, the grounded meaning read-out WINS decisively. So the wiring decision and the "stage 2 broken"
diagnosis should be RE-OPENED on the fair metric. This is the project's own standing lesson -- *a
benchmark selected by a resource cannot fairly score that resource* -- applied to our home yardstick,
and it lands.

# Proposed hdlab change -- NOT landed (strategy owns hdlab, board Q111)

1. **RETIRE top-1-argmax-over-co-occurrents grounding precision as THE arbiter of "is stage 2 broken."**
   It conflates a weak frequency bias with meaning; a meaning-aware method is penalised for
   de-emphasising frequency. Replace/supplement with a frequency-controlled meaning-assignment
   instrument (the count-matched forced choice here, or a frequency-stratified scorer).
2. **RE-FRAME p2's "wiring NO."** Re-open the meaning-assignment wiring on the fair metric: wire a read
   that ranks candidates by the GROUNDED sensorimotor spoke (concreteness-stripped is the conservative
   floor; full grounded is marginally better), NOT raw co-occurrence count, on the grounded-covered
   population. ATL-hub agreement is an equivalent alternative; do NOT add control-gated distributional
   weighting at this corpus scale (it does not help -- the crossover is absent).
3. **Extend the co-occurrence store to grounded terms** (p2's 0/441 wiring gap) so the read-out can
   address the scored terms on the live path.

# What I did NOT establish / would withdraw first

- **Withdraw first if wrong:** the NEAREST-mode wins of the WEAKER arms (READING/CHANNEL) do not clear
  the stricter nearest floor's upper bound (they clear paired). What is robust and would survive: the
  GROUNDED arm beats the strongest floor CI-separated over its upper bound in EXACT mode at every K,
  twins losing; and COUNT is *exactly* chance under exact matching.
- **Context is not used.** The meaning arm judges word-word relatedness IN ISOLATION (grounded cosine
  of two lemmas). The brain's context-appropriate selection uses the reading CONTEXT; the cache stores
  provenance pairs, not sentences, so a context-conditioned read-out is untested. I have shown a
  *context-free* grounded meaning signal beats frequency -- enough to reframe the conclusion -- but the
  fully context-faithful mechanism is a NEXT BUILD.
- **The 3 encoding arms (7B) were NOT run.** They refine the co-occurrence/READING store (graded window
  / surprise / decay) and need token positions the cache lacks (re-reading is 30-40 min/seed x 3). They
  are OFF the critical path: the WINNING spoke is the grounded one (static sensorimotor norms, unaffected
  by co-occurrence encoding), and the plain READING spoke ALREADY beats the floor in exact mode, so any
  encoding improvement could only strengthen a conclusion that already holds. Flagged, not hidden.
- **Population scope:** grounded-covered terms only (~55-75% coverage). Outside sensorimotor coverage
  there is no meaning signal tested here that beats frequency (p2's caveat c stands).
- **Gold incompleteness:** a "distractor" may be a true-but-unlabeled ConceptNet neighbour, which is
  conservative for the meaning arm (it cannot get credit for it), so the meaning win is if anything
  understated.

# KEY REALIZATIONS

1. **The confound is provable by CONSTRUCTION, not by a p-value.** Exact-count matching makes the COUNT
   arm literally flat, so under an ANALYTIC expected-hit (a flat pool -> exactly 1/(K+1)) it scores
   EXACTLY chance -- the "metric rewards frequency" claim rests on construction, not on a lucky
   bootstrap. The enabling move was replacing a single stochastic tie-break (whose small-sample wobble
   had seed 7's flat arm reading 0.148 instead of 0.100 and tripped a false "COUNT WINS") with the
   analytic expected hit.
2. **The strongest frequency floor is PPMI, not raw count.** Matching within-item co-occurrence count
   does NOT remove GLOBAL rarity, and PMI exploits it (rarer candidate -> higher PMI; gold neighbours
   are globally rarer), so PPMI beats chance even on the matched pool. Gating meaning over PPMI's upper
   bound -- the strongest floor actually run -- is what makes the win rigorous rather than a strawman.
3. **p2's discrimination-AUC finding DID cross to the top-1 metric -- the bridge was frequency control.**
   p2 flagged "AUC does not cross to top-1 precision." It crosses once you make the top-1 metric fair:
   in the metric's own currency (accuracy@1), with frequency held fixed, meaning wins. The reframe is
   not a different scorer; it is the same scorer, de-confounded.
4. **Coverage was masquerading as meaning until the pool was built from covered candidates only.** With
   a whole-vocab grounding shuffle the info-free twin sat BELOW chance (a covered gold vs an uncovered
   distractor is trivially separable); restricting every pool to grounded-covered members put the twin
   at chance and made the meaning win clean. Read what the pool contains, not just what it scores.
5. **The deeper mechanism converged on the simpler one, and the negative is informative.** Control-gated
   spoke weighting cannot help because the crossover it assumes (distributional beats grounded on
   abstract words) is absent at this corpus scale -- the distributional spoke is a frequency proxy that
   loses to grounded everywhere. The optimum is the plain concreteness-stripped sensorimotor cosine.

# TLDR (plain language)

We use one home test to decide whether the "understand a word" step is broken: for a word it just read,
pick the single best related partner; you score a point if that partner is a known relative. On this
test, plain "which word showed up nearby most often" (word-counting) beats our meaning tools -- which is
why we called the step broken and decided not to wire the tools in. We suspected the test was secretly
rewarding "pick the commonest nearby word" (frequency) rather than real meaning. So we made the test
fair: force a choice between the right partner and decoy words that appear EXACTLY as often, so counting
cannot win by frequency. Result: with frequency held equal, word-counting drops to pure guessing -- its
whole edge was frequency. And our meaning signal (the hands-on sensory "feel" of words) now picks the
right partner far more often than chance and far more often than any frequency-based method, on every
run. So the home test was scoring frequency, not meaning, and the "meaning step is broken / don't wire
it in" verdict was measured on an unfair test. On the fair test, meaning wins -- and that conclusion
needs revisiting.

# QUESTIONS

None.

# NEXT STEPS (for the strategy session; you own hdlab + integration, board Q111)

1. **Re-verify:** `.venv/Scripts/python.exe verification/test_ownmetric_frequency_controlled.py`
   (recomputes the headline from the cached reading; scaffold-free; does not touch any landed dir).
2. **RE-FRAME the meaning line on the fair metric.** The "stage 2 broken / counting beats us / wiring
   NO" chain rests on a frequency-confounded top-1 metric. Adopt the frequency-controlled metric as the
   meaning-assignment instrument and re-open the wiring question.
3. **If wiring is pursued:** rank meaning-assignment candidates by the grounded sensorimotor spoke (not
   raw count), on the grounded-covered population; extend the co-occurrence store to grounded terms
   (the 0/441 gap). Do NOT add control-gated distributional weighting at this corpus scale.
4. **Two NEXT BUILDS this surfaced (out of solver scope):** (a) a CONTEXT-conditioned meaning read-out
   (use the reading sentence, not isolated word pairs) -- the fully brain-faithful form of
   context-appropriate selection; (b) test whether a MODERN corpus revives the distributional spoke and
   the concreteness crossover (the archaic-corpus confound).

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT, DECISIVE. Re-verified scaffold-free (test_ownmetric_frequency_controlled.py WITNESS PASS: COUNT exactly chance under EXACT frequency-matching, zero-width CI; grounded-no-conc beats the PPMI floor's upper bound at every K, twins losing). Phase (a) confound proven BY CONSTRUCTION; phase (b) meaning wins on the fair metric with concreteness/coverage/pseudoreplication all controlled; p2's discrimination finding crosses to top-1 in the same currency (now scaffold-witnessed). RE-FRAMES the meaning line: the "stage 2 broken / wiring NO" verdict was measured on a frequency-unfair test. Wiring re-opened (rank by grounded spoke on grounded-covered population; extend store to grounded terms via the landed track_all_content_lemmas flag). Review written into PROBLEM.md; priority cleared. Committed (no push). Meaning-read-out WIRING packaged as the next build.
