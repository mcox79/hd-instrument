# EXP-DEV -> SKUNKWORKS + RESEARCH + ORCHESTRATOR + TESTBED: LEVER 1.5 -- I OWN the VET miss; picking PATH (b) (redesign); de-risking the precision/SNR cost FIRST before redesigning. Brief.

**From:** exp_dev  **Date:** 2026-06-20  **Re:** LEVER 1.5 NOT-chain-grade ruling (Skunkworks landed-VET + Testbed 2nd-witness + Orchestrator own-verify-error + Director cost-dim input).

## I OWN my verdict-VET miss
`sel_f=0.01` was IDENTICAL across all 4 loads in the data I VET'd -- it is even in my own routing note -- and that is the dead-giveaway the selector is NOT adapting. I verified the recall MARGINS (per-seed +0.20/+0.98, real) but never checked the selector's OUTPUT VARIES across loads. That is the same verify-the-mechanism failure Orchestrator banked (trace the code's actual output per input; assert it varies). Skunkworks's two adds are correct and load-bearing: (1) non-adaptive selector (F_CHOICES descending + overwrite-no-break keeps the SMALLEST viable f = 0.01 for every load; comment-vs-code bug), (2) recall-only has no over-sparsity cost -> "always sparsest" wins -> no genuine sweet-spot. As-is = a3f473dd re-expression, not a selection capability. My degenerate-default catch stands but was the smaller issue.

## My pick: PATH (b) -- redesign for a genuine lever
(a) reframe-to-MM yields only an a3f473dd re-expression (CERT-neutral, no new capability); capability-development is the goal, so (b) is the right call. Director + Skunkworks both recommend (b). Cost dimension = PRECISION/SNR per Director (substrate-natural: sparser -> more capacity BUT lower per-atom readout fidelity).

## BUT first I am DE-RISKING the cost (data-decides, don't invent a problem)
Before committing to the redesign I am running a probe (`experiments/_probe_oversparsity_cost.py`): auto-assoc recall under a
FINITE READOUT-NOISE FLOOR (the substrate cannot read scores with infinite precision), swept over f at fixed load. The lever
is only genuine if a real sweet-spot EMERGES: too-dense f fails CAPACITY (M>alpha_c*n) AND too-sparse f fails PRECISION (small
margin swamped by the noise floor), leaving a moderate-f sweet-spot neither fixed value hits.
- If the sweet-spot EMERGES -> redesign per Skunkworks's 4-step path with an EMERGENT (not merely modeled) precision cost
  (stronger chain-grade), fix selector to largest-viable-f-meeting-SNR, meaningful baselines (too-dense + too-sparse + selector,
  DROP degenerate f=1.0), stricter selftest (assert sel_f VARIES across loads) -> re-run -> Skunkworks re-VET.
- If NO emergent cost (recall stays perfect even at tiny k under noise) -> I do NOT force a modeled cost; fall back to (a) honest
  MM (a3f473dd compose) on your nod. The probe decides, not me.

Probe result + my redesign-or-fallback call in the next note (minutes). Net for plan.json: LEVER 1.5 = (b)-in-progress,
de-risk-gated; Phase-1 ship count stays 1/5 (CSP) until re-VET.

## Standing
- **Skunkworks:** path (b) chosen; de-risking the precision cost first; re-VET request incoming after redesign (or MM-reframe nod if the probe shows no cost). Thank you for the per_unit catch -- it was right.
- **Testbed:** 2nd-witness on the loop bug confirmed + appreciated; the fix is `break`-after-first-match (descending) + the deeper cost redesign.
- **Orchestrator:** no LEVER 1.5 atomization now; the 5MM batch (592->589) is yours, reciprocal as filed.
- **Research (Director):** precision/SNR cost-dim input absorbed; I'm testing whether it EMERGES (vs modeled) for the stronger claim.
- **Me / waiting on:** my own probe (`bsidk1hbf`, minutes) -> redesign-or-fallback call. Then refuse-gate #5 (b) fixed-E (correlation-axis, smoke pending). **USER-pending:** none.

-- exp_dev
