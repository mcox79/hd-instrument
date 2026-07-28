# Parser lift: GLOBAL beam training + early-update to break local-argmax saturation (2026-07-23)

## WHY (USER-directed: parser is the load-bearing foundation; dedup-derived lever)
The parser is the load-bearing wall of the reader (agreement/roles/meaning all lean on it). Current glass-box state (disk-verified):
- arc-eager transition parser (atom 29451): UAS 0.811, structured-perceptron, dynamic-oracle, beam DECODE(w4) but LOCAL training -> beam decode HURT (0.75<0.81 greedy) = classic LABEL-BIAS mismatch (locally-trained scorer can't exploit search).
- feateng_struct: structural features already give +0.04 -> ~0.83-0.85 nopunct, then "live_lever=False" (plateau).
- headroom leak-hunt: SATURATED ~0.81 with LOCAL ARGMAX; classical target 0.86-0.89. The gap is a SEARCH/GLOBAL-TRAINING gap, NOT a feature gap.
- 2nd-order graph features HARD_FAIL; argstruct/valency (LCCP) HARD_PASS (reduces misattach, generalizes).

CONCLUSION: features are fine; LOCAL greedy decoding saturates. The untried classic glass-box fix = GLOBAL structured training with beam + early-update (Collins-Roark 2004; Zhang-Clark 2008; Huang max-violation 2012) so beam HELPS instead of hurting. BRAIN-FAITHFUL: parallel maintenance of multiple parse hypotheses (garden-path effects show the brain entertains + reranks parses) + structural error-driven learning.

## WHAT to build
Upgrade the arc-eager transition parser to GLOBAL structured-perceptron training:
- BEAM training (width e.g. 4-16): score whole ACTION SEQUENCES cumulatively; maintain a beam of partial parses.
- EARLY-UPDATE (Collins-Roark): when the gold derivation falls OFF the beam, stop, update toward gold-prefix vs the beam's best-wrong-prefix. (Or MAX-VIOLATION / Huang: update at the max-margin-violation point.) Averaged perceptron.
- Reuse the STRUCTURAL feature set that already gave +0.04 (feateng_struct) + arc-eager config/stack features (top-k stack items, their POS, leftmost/rightmost attached dependents, distance buckets). Optionally add the argstruct/valency signal (LCCP HARD_PASS) as a feature.
- Glass-box: linear averaged-perceptron weights, inspectable; NO gradient/autograd; beam items are explicit (stack,buffer,heads,score).

## ARMS (one variable = training regime, features held fixed)
- ARM_LOCAL (baseline = 29451): local dynamic-oracle greedy training, greedy decode. Expect ~0.81.
- ARM_GLOBAL_BEAM: global beam + early-update training, beam decode (same width). HYPOTHESIS: beam now HELPS -> UAS toward 0.85-0.88.
- (control) ARM_LOCAL + beam decode (no global training): should REPRODUCE the beam-hurts anomaly (~0.75) -> confirms the mechanism is the TRAINING not the decode.

## DISCRIMINATOR (can-fail; real gap exists)
- HARD_PASS: ARM_GLOBAL_BEAM UAS clears ARM_LOCAL by a clean margin (>= +0.03, 2SE-clean) and approaches classical 0.86-0.89; the beam-decode control confirms local+beam still hurts (isolates training as the lever); LEARNING CURVE rises (flexible/improving).
- HARD_FAIL (must be possible): global-beam training does NOT beat local greedy (>= +0.03) -> search doesn't help our feature set -> saturation is deeper than decode (an earned bound; then the lever is richer features/representation, not search).
- FAIR: same features + same eval split across arms; ONE variable = training regime; report nopunct + all; hard-attachment (long-distance / nested) breakdown; real UD-EWT.

## POINTERS (read; do not re-summarize)
- experiments/exp_depparse_transition_arceager_cpu_v1.py (29451) -- the parser to upgrade; has beam decode + local training; reuse its transition system + eval harness.
- experiments/exp_parser_uas_feateng_struct_v1.py -- the structural features that gave +0.04 (reuse them).
- experiments/exp_parser_uas_headroom_leakhunt_v1.py -- the SATURATED-at-local-argmax finding this aims to break.
- experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py -- the valency/argstruct signal (HARD_PASS) optionally add as a feature.

## AUTONOMY
exp_dev designs ALL params: beam width, early-update vs max-violation, epochs, feature set specifics, seeds, HARD-PASS/HARD-FAIL band VALUES, queue/inline, anchor name, ETA. Do NOT pre-bake them.
