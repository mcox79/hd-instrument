# Brain-drill: metacognitive calibration = the oracle-escalation trigger (2026-07-21)

**Purpose (directive-#4, drill-the-brain-first for the next component):** the oracle-escalation reading loop's make-or-break is CALIBRATION -- does the reader reliably KNOW WHEN IT'S UNSURE (so it escalates the right sentences to the oracle, not random ones)? Drill how the BRAIN does this, then design the trigger around that mechanism. Web-enabled (my WebFetch/WebSearch work; headless subagents can't auth).

## The brain's mechanism = BIFURCATED metacognitive monitoring

"Know when you know" is NOT a single confidence number. It is a **two-channel** system:

1. **CONFLICT / ERROR MONITORING -- anterior cingulate cortex (ACC/dACC).** The dACC detects mismatches between expected and actual, and fires not only on errors but on correct-but-high-competition responses -> it monitors COGNITIVE CONFLICT broadly. ACC size correlates with introspective accuracy; ACC+insula activity tracks feeling-of-knowing strength.
2. **SIGNAL STRENGTH / COHERENCE -- parietal evidence accumulation.** Confidence emerges from the clarity and consistency (coherence) of the task-related neural representation; posterior->anterior information flow during confidence judgments. Computational framing: a system can "know when it knows" by evaluating the COHERENCE of the neural signal in response to a query.

**The integration (the load-bearing point):** confidence = ACC conflict-signal PAIRED WITH signal-strength/coherence -- "not just whether an error occurred, but how confident based on the clarity and consistency of the underlying signal." A prediction-error framework driving adaptive strategy adjustment + learning.

## Direct map to our escalation triggers (design-around-the-mechanism)

| Brain channel | Our substrate analog | Status |
|---|---|---|
| ACC conflict-monitor | the state-of-mind CONTRADICTION-FLAG (running model disagrees with the parse) | built; 1.71x error-lift (atom 29411), fires 1.43x more on McGuffey than UD |
| Parietal signal-strength/coherence | the parse/vote MARGIN (top1-top2 decisiveness) | built; the abstain-gate threshold |

**DESIGN IMPLICATION for the oracle-escalation loop:** the escalation trigger should be the BIFURCATED COMBINATION -- escalate when EITHER (a) signal-strength is low (margin below tau = feeling-of-not-knowing) OR (b) conflict fires (contradiction-flag = ACC mismatch), ideally a weighted/learned combination rather than a single threshold. This is brain-faithful (two-channel metacognition), and it matches independent evidence: the state-of-mind VET (fold the flag INTO the abstain gate alongside margin) + the McGuffey census (escalation load splits ~evenly margin 0.092 / flag 0.090). Neither channel alone is sufficient (flag = weak 1.71x alone; margin fires less on simple McGuffey syntax) -- the brain uses BOTH, so should we.

## Honest scope
Literature synthesis (metacognition / comprehension-monitoring neuroscience), NOT a substrate measurement -- informs the loop's calibration DESIGN; the calibration itself must still be built + measured (does the combined trigger fire on the reader's ACTUAL errors on real text, precision/recall) as the design-gated can-fail cell, with oracle labels. Same-limit brain-check caveat: the brain's monitoring is ALSO imperfect (illusions of knowing / fluency-biased overconfidence) -- expect the trigger to miss some errors; that's a real bound, not a bug.

Sources: metacognitive-monitoring reading-comprehension review (MDPI Intelligence 2026); "neurological implications of metacognition" (PMC12971950 / Frontiers Psychology 2026); metacognition overview (OECS/MIT).

Related: [[project_build_the_missing_learning_self_monitoring_layer_from_adopted_prior_art_2026-07-20]] (self-monitoring = the missing layer); atom 29411 (contradiction-flag error-detector); the McGuffey census (escalation load).
