# HDLAB INTEGRATION SPEC -- route the reader through the graded probabilistic parse (Q111)

Strategy lands; the solver writes no `hdlab/`. Every piece REUSES an existing organ; the graded parse is
already built + brute-force-verified (`hdlab.graded_parser`). Recall/recognition path stays byte-identical.

## ITEM 1 (land unconditionally) -- consume the graded posterior, drop the fitted logistic

**1a. Exact graded decode on the reader path.** `hdlab.arc_parser.ArcParser.parse` already accepts
`decode="exact"` (exact Chu-Liu/Edmonds MAP) and `want_marginals=True` (exact single-root Matrix-Tree
marginals) -- both ADDITIVE and already landed as opt-in. FLIP the reader's parse call
(`situation_reader._cached_parse_heads` / `_cached_parse_conf`, ~L2053-2096) to `decode="exact"`.
- Effect: heads change ONLY on the 7.2% invalid-tree sentences; UAS +0.00199 CI-sep [0.0010,0.0029]
  (`exp_parser_graded_decode_regimes_v1`). Per-token margins are head-independent -> unchanged.
- No-regress: 98% of tokens keep their head; downstream label consumers see identical heads except on the
  cycle sentences (which were invalid before, so strictly an improvement). Measure the modern board AGG
  before flipping default-on (no-more-default-off: turn on if net-nonneg).

**1b. Replace the NOT_BF fitted-logistic `parse_confidence` with the raw graded marginal.** The raw
single-root marginal `mu(head->dep)` separates right-from-wrong attachment at AUC **0.8546** (this
measurement) / 0.782 obl (prior) -- BEATING the fitted logistic (0.736). Route
`parse_confidence.obl_reliability_marginal` (already in-module) as the reader's reliability signal and
compute the marginal once per read (`ArcParser.parse(want_marginals=True)` -> `ParseResult.marginals`;
ONE matrix inverse, reused). This REMOVES a learned/fitted NOT_BF component (a frozen offline logistic),
not adds one. `parse_confidence`'s logistic stays as a reference; the live reliability = the marginal.

## ITEM 2 (wire through the competition, measure on the board) -- read the DISTRIBUTION not the single head

The true argument the single committed parse drops is almost always alive in the posterior's top-2:
patient-arc recall **0.9512 -> 0.9906** (+0.0394 CI-sep, shuffled twin 0.4432 loses)
(`exp_parser_graded_downstream_whodidwhat_v1`). Admit each token's TOP-2 marginal heads as candidate
attachments into the role competition (`predicate_argument_frontend.route_predicate_arguments` already
does a version of this -- "the marginal's top-2 parse-miss reach", +0.0065 who-did-what).
**CRITICAL (measured, `exp_parser_graded_reliability_gated_patient_v1`): do NOT widen the beam blindly** --
a naive top-2 admission COLLAPSES precision (patient-arc F1 0.4182 -> 0.2689). RANK/GATE the admitted
candidates by the marginal reliability (item 1b) inside the existing `graded_competition` (the pinned
Lewis-Vasishth reliability-weighted cue integration): reliability-GATED top-2 NET-beats the hard head F1
CI-sep (0.4182 -> 0.4218, +0.0036 [0.0012,0.0059]; shuffled-marginal twin 0.1414 loses). Wire point:
`graded_competition.graded_pick` with the marginal as the reliability weight. Measure who-did-what
patient/agent on `exp_situation_model_qa_modern_v1` (the modern board) before/after; the net board move is
expected SMALL (the hard head already recovers 95%), concentrated on hard/ambiguous items.

## INVARIANTS (do NOT change)
- Recall/recognition path (attractor: `ca3_completer`, `gap_detector`, `hippocampal_encoder`) is untouched
  -- it reads the normalized vectors, not the parse; byte-identical.
- The graded marginal is computed from the SAME arc-factored scores; no new asset, no retrain.
- No external tool/LLM at inference; glass-box; the graded algorithms are brute-force-verified
  (`hdlab.graded_parser.self_test`).

## BF-STATUS DELTAS to record (Q111)
- `arc_parser` / `arceager_parser`: remain NOT_BF as a HARD-DECODE, but with `decode="exact"` on the read
  path the DECODE half becomes BF (exact global MAP); the residual NOT_BF is the frozen SUPERVISED SCORER
  (the acquisition follow-on). Note in the registry: "decode routed through graded_parser (BF); scorer
  acquisition = open follow-on."
- `parse_confidence`: fitted logistic -> raw graded marginal reliability (a NOT_BF fitted component REMOVED
  from the live path). Registry `parse_confidence` NOT_BF note's "UPGRADE (gated on a live defer consumer)"
  is now unblocked by item 1b.
- `graded_parser`: DORMANT -> LIVE (a brain-faithful PASS wired onto the read path).

## REVERIFY
`.venv/Scripts/python.exe verification/test_parser_graded_route_through.py` (18 checks; reads the landed
metrics + runs `graded_parser.self_test` + a live parse). Full re-run of the sweeps: the four
`experiments/exp_parser_*_v1.py --mode full`.
