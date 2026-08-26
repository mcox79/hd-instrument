---
priority:
review: EXCELLENT
review_text: "Re-verified scaffold-free (WITNESS PASS) and DECISIVE -- it re-frames the meaning line. Phase (a): the home metric WAS scoring frequency, proven BY CONSTRUCTION -- on a frequency-EXACT-matched candidate pool raw counting reads exactly chance (0.5000/0.2000, zero-width CI). Phase (b): on that fair metric, concreteness-stripped grounded meaning beats the STRONGER PPMI floor's upper bound CI-separated at every pool size (0.741 vs 0.558 at K=1), info-free twins losing; concreteness, coverage and pseudoreplication all controlled. p2's discrimination finding crosses to the top-1 metric in the SAME currency (accuracy@1, de-confounded). So the 'stage 2 broken / wiring NO' verdict was measured on a frequency-unfair test -- on the fair test meaning WINS. Converged: the deeper control-gated mechanism collapses to grounded-alone (no crossover to gate at this ~200-year-old-corpus scale). The wiring is re-opened and is mine to land (Q111)."
---

> # MY REVIEW -- EXCELLENT, AND DECISIVE: IT RE-FRAMES THE MEANING LINE. THE OWN METRIC WAS SCORING FREQUENCY.
> *Reviewed 2026-08-26 (owner marked DONE). Re-verified scaffold-free: `verification/test_ownmetric_frequency_controlled.py` -> WITNESS PASS. Reproduced first-hand: the raw-vs-PMI collapse (x5-x10), COUNT = exactly chance under EXACT frequency-matching (0.5000 [0.5000,0.5000] at K=1; 0.2000 at K=4), and grounded-no-concreteness beating the PPMI floor's upper bound (0.741 vs 0.558 at K=1).*
>
> ## PHASE (a) -- THE CONFOUND IS PROVEN BY CONSTRUCTION, NOT A p-VALUE
> Build the candidate pool so the gold partner and its distractors have IDENTICAL raw co-occurrence counts with the term, and raw-count argmax is flat by construction -> it reads exactly chance with a zero-width CI. Counting's entire 2-3x "win" on the home metric was raw frequency. (The solver even caught its own artifact: a stochastic tie-break made seed 7's flat arm read 0.148 and tripped a false COUNT-WINS; an analytic expected-hit estimator removed it -- a checker-shares-a-flaw catch.)
>
> ## PHASE (b) -- ON THE FAIR METRIC, MEANING WINS, AND THE CONTROLS ALL BIND
> Against the STRONGER floor (PPMI, which rides the global rarity that within-item matching leaves behind), concreteness-stripped grounded meaning clears the floor's UPPER bound CI-separated at every K (1/4/9), info-free twins (shuffled grounding, random pick) at chance. Concreteness is controlled (grounded-no-conc beats conc-only), coverage is controlled (covered-only pools put the twin at chance), pseudoreplication is controlled (term-clustered bootstrap). This is the measurement bar, met.
>
> ## IT CLOSES p2's OPEN CAVEAT IN THE SAME CURRENCY
> STATUS carried the discrimination-AUC reframe as "the solver's controlled finding but NOT yet scaffold-witnessed (reverify covers top-1 only)." This resolves it: p2's discrimination finding CROSSES to the top-1 metric -- same scorer (accuracy@1), de-confounded by frequency control, now scaffold-witnessed. Not a different scorer.
>
> ## CONVERGED, AND THE NEGATIVE IS INFORMATIVE (THE SOLVER OPERATING PROTOCOL WORKED)
> The solver iterated deeper before submitting instead of shipping the first clear: ATL-hub agreement = grounded-alone (not separated); semantic-control-gated spoke weighting does NOT help, because the crossover it assumes is absent -- the distributional reading spoke is worse than grounded on BOTH abstract (-0.10) and concrete (-0.14) terms, so there is nothing to gate. At this archaic (McGuffey-derived, ~200-year-old) corpus scale, plain concreteness-stripped sensorimotor cosine is the optimal brain-faithful read-out. A clean convergence.
>
> ## HONEST LIMITS (as flagged, withdraw-first)
> Robust and defended last: grounded beats the strongest floor CI-separated in EXACT mode at every K, twins losing; COUNT exactly chance under exact matching. Softer (withdraw first): nearest-mode wins of the weaker arms clear only the paired test, not the stricter nearest floor's upper bound. The win is CONTEXT-FREE (isolated word pairs; the cache stores provenance pairs, not sentences) -- the brain's context-driven selection is a next build, not tested here. Scope = grounded-covered terms only (~55-75%); gold incompleteness biases AGAINST the meaning arm (conservative).
>
> ## WHAT THIS CHANGES -- THE WIRING IS RE-OPENED
> Retire top-1-argmax-over-co-occurrents grounding precision as the arbiter of "is stage 2 broken" -- it conflates a weak frequency bias with meaning. **Re-open p2's "wiring NO":** the meaning read-out should rank candidates by the grounded sensorimotor spoke (NOT raw count) on the grounded-covered population, and the co-occurrence store must be extended to grounded terms (p2's 0/441 gap -- the Route B `track_all_content_lemmas` flag I landed default-off is exactly that channel). Do NOT add control-gated distributional weighting at this corpus scale. **This is the meaning-read-out WIRING, and it is now mine to build/land (Q111) -- packaged next.**

# PROBLEM: our "stage 2 is broken" verdict rests on a home metric that may be scoring FREQUENCY, not MEANING

**slug:** `the_own_metric_may_reward_frequency_not_meaning` - **opened:** 2026-08-25 by the strategy session
**status:** OPEN - **the confound is first-hand and re-verified (from p2), not relayed**

> **PRIORITY NOTE:** filed at `2` as the direct successor to `meaning_read_out_untested_on_the_own_metric`
> (p2, just integrated). It sits UNDER the whole meaning line, so on evidence it may deserve to sit above
> some of it. Re-rank against the goal-bearing line (p1) if you judge that higher.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
> **Iterate to the OPTIMAL brain-foundational solution; do NOT submit the first thing that clears.** Set up
> your own 30-min cron (`CronCreate "13,43 * * * *"`) that each fire pushes you ONE LEVEL DEEPER into brain
> fidelity: "how does the brain REALLY do this, deeper than my current mechanism?" -> implement -> test
> (can-fail, strongest real floor, info-free twin LOSING) -> iterate. Cancel it (`CronDelete`) and submit
> ONLY when successive iterations stop improving fidelity AND result (you have CONVERGED on the optimum).
> **You are NOT boxed in by this brief.** If you find a MORE brain-foundational method that this brief's
> specific instructions -- OR the substrate integration points you must tie into -- are NOT ~compatible with,
> SUBMIT that alternative solution or solution DIRECTION instead (say what is incompatible and why yours is
> more brain-faithful).

## 1. THE PROBLEM IN PLAIN LANGUAGE

We call the meaning stage "broken" because, on our home test, plain word-counting beats our meaning
organs 2-3x. The home test: for a word the reader grounded, pick ONE partner word; you score a hit if
that partner is a known related word (a ConceptNet neighbour). p2 just showed something alarming about
this test: **the score is carried almost entirely by RAW FREQUENCY.** Normalise frequency out (PMI) and
the score collapses ~8x. Every genuinely meaning-based method loses on this test PRECISELY BECAUSE it
stops rewarding "just pick the most frequent partner." So the test may be rewarding "guess the commonest
neighbour" -- which is frequency, not meaning. If that is true, "beat counting on this test" is not a
fair bar for a meaning read-out; it asks meaning to win a frequency contest.

## 2. WHY THIS ONE

It sits UNDER the whole meaning line. The "stage 2 is broken" diagnosis, the "counting beats us" wall,
and the p2 wiring decision (NO) ALL rest on this one metric. If the metric conflates meaning with
frequency, those conclusions are measuring the wrong thing and a real meaning win could be invisible.
This is the project's own standing lesson -- *a benchmark selected by a resource cannot fairly score that
resource* -- applied to our home yardstick. Get it right and everything downstream is re-framed on solid
ground; get it wrong and we keep declaring meaning broken on a frequency test.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

The brain assigns the CONTEXT-APPROPRIATE meaning, not the most frequent associate -- sense selection is
driven by current context, and frequency is a PRIOR that context overrides (PINNED: lexical-ambiguity
resolution; the most-frequent-sense is a baseline the brain BEATS when context demands). A fair meaning
test must therefore reward picking the RIGHT partner even when it is NOT the most frequent one. The
discipline: separate the two things the metric currently confounds -- frequency (a prior) and meaning
(context-appropriate relatedness) -- and check whether our read-outs win on the meaning part once
frequency is held fixed.

## 4. MEASURED vs INFERRED

MEASURED (p2, re-verified to the digit): on the current metric, TOP_COOC (raw-frequency argmax)
`0.048-0.065` beats every meaning read-out (`0.007-0.023`), and PMI-normalised counting collapses to
`0.004-0.013` (~8x below raw) -- the metric rewards raw frequency; normalising it out destroys the
signal. Oracle ceiling ~`0.46-0.50` (the gold partner is reachable ~half the time -> misses are RANKING
failures, not coverage).
INFERRED (the open question, decisive either way): that a FREQUENCY-CONTROLLED version of the metric
(where raw-frequency argmax cannot win by frequency alone) either (a) ERASES counting's advantage -- the
metric was scoring frequency -- or (b) PRESERVES it -- the metric is fair and meaning genuinely loses.

## 5. ALREADY TRIED (do not re-run)

- The read-outs vs counting on the CURRENT metric -- done (p2, they lose CI-separated). Do NOT re-run.
- TOPK_GROUNDED (frequency-salience selects, grounded hub discriminates) on the CURRENT metric -- done
  (p2: beats its twin CI-separated, beats counting numerically, CI touches zero -- sub-threshold). Its
  re-test belongs on the FAIR metric (phase b below), NOT the current one.
Query `experiment_index.py query "grounding precision"`, `query "frequency"`, `query "most frequent"` and
check the ledger first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `data/exp_grounding_precision_gold_v1/` + `experiments/exp_meaning_readout_own_metric_v1.py` and
  reproduce the raw-vs-PMI 8x collapse yourself. Confirm how the candidate pool is built (what counting
  argmaxes over) and that the gold is ConceptNet neighbours.
- Confirm the confound in one check: are the GOLD partners themselves usually the HIGH-FREQUENCY
  co-occurrents? If the gold answer IS typically the most frequent co-occurrent, that is the confound.

## 7. THE BAR

**Phase (a) -- is the metric fair?** Build a FREQUENCY-CONTROLLED own-metric (copy the brain's separation
of prior from meaning): candidates frequency-matched to the gold so raw-frequency argmax cannot win by
frequency alone, OR gold restricted to items that are NOT the top-frequency co-occurrent -- state which
and why it isolates meaning, and keep it powered (>= ~300 scorable items). Re-measure counting there.
**Phase (b) -- does meaning win on the fair metric?** On that frequency-controlled metric, does a meaning
read-out -- and TOPK_GROUNDED + the 3 brain-faithful encoding arms (graded temporal window /
prediction-error weighting / decay; specified in the p2 brief section 7B) -- beat a FREQUENCY floor
CI-separated over its upper bound, info-free twin LOSING?
**DECISIVE EITHER WAY:** if counting's CI-separated advantage DISAPPEARS under frequency control, the
metric was scoring frequency and the "stage 2 broken / wiring NO" conclusions must be RE-FRAMED on the
fair metric. If counting STILL wins under frequency control, the metric is fair and meaning genuinely
loses -- report that; it closes the line honestly. HOW WE WOULD KNOW IT FAILED (as a problem): no
frequency-controlled metric can be built that BOTH stays powered AND removes the confound -- then say so.

## 8. FILES AND ENTRY POINTS

- `data/exp_grounding_precision_gold_v1/`, `experiments/exp_meaning_readout_own_metric_v1.py` (+ `_ksweep`)
  -- the current metric, the p2 read-outs, and the counting floor.
- `data/conceptnet_gold_v1` -- the gold neighbours.
- The 3 brain-faithful encoding arms are specified in
  `notes/problems/meaning_read_out_untested_on_the_own_metric/PROBLEM.md` section 7B -- reuse for phase (b).
- Prove in `experiments/` + `verification/`; propose any hdlab wiring in `SOLVED.md` (strategy lands it,
  board Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT re-run the read-outs vs counting on the CURRENT metric (p2 did it).
- Do NOT quote the borrowed-scorer numbers (WordSim `0.45`, substitutability `0.84`) here -- different scorers.
