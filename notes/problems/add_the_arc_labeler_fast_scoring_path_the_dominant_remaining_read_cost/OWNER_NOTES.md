---
owner_verdict: DONE
---

SOLVED (pending your verdict) — add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost (opus 4.8 solver)

Write-up: notes/problems/add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost/SOLVED.md
Reverify (reruns NO landed cell): .venv/Scripts/python.exe verification/test_arc_labeler_fastpath_landing.py   # 5/5

ASSIGNED DELIVERABLE — DONE, land-ready, excellent:
Byte-identical fast path for the arc labeler (ArcLabeler._predict_label), the dominant remaining read-time
lever. Byte-identity is a THEOREM (no label contains the '~' separator, so the split is exact) AND verified on
22,921 held-out arcs across two populations (LitBank predicted-heads + UD-EWT-test gold-heads), 0 divergence,
plus a full-model regression guard (fresh-reader read byte-identical across events/entity_states/causal/coref/
timeline). Labeler scoring 8.7-9.8x faster (~4.2s/read on full docs). Brain-foundational bonus (reuses the
landed graded_competition organ): the fast path materializes lane[] for free -> a graded readout that is
argmax-byte-identical (MAP-optimality, zero consumer regression) AND whose entropy flags labeling errors
gold-free (AUC 0.930; info-free twin 0.481). Proposed hdlab diff: _FastLabelPlan + lazy _ensure_fast in
label(), _predict_label/_score kept as training path + reference. NO hdlab writes (Q111); ledger clean.

>>> PARSER WORK — FLAGGED (you directed this escalation; it EXCEEDED the arc-labeler scope; documented in
SOLVED.md sections D-O; it is EXPLORATORY, not landable as-is; FILE AS ITS OWN PROBLEM(S)):
 - The dominant read-time/accuracy leak is the PARSER, not the labeler. The live reader runs the WEAKER of two
   parsers it already has; switching on the dormant arc-eager (UAS 0.79->0.84, already built, byte-safe) is a
   free win but LOW-leverage in the general path (only feeds entity_states; the who-did-what path already uses
   arc-eager).
 - Full-chain signal-loss traced + compared to the brain (research-backed): supervised chain tagger 0.94 ->
   parser 0.79 -> labeler LAS 0.72; brain/SOTA ~0.95. The parsers are SUPERVISED on gold trees, which is NOT how
   the brain learns. I built a self-supervised, online, prediction-error-driven, never-frozen structure learner
   (on hdlab.predictive_coding) that LEARNS as it reads (control-verified) but caps ~0.42 UAS. The grand goal
   (brain-foundational parser matching supervised) is NOT achieved; online learning is not yet stable.
 - Aggressively vetted the grounding negative -> ROOT CAUSE = meaning vectors are near-collinear (cosine 0.92),
   a known averaged-embedding degeneracy; FIX = whiten (remove common component). Two PROTOTYPE wins from that
   fix: (i) grounded meaning now BEATS its scrambled control on meaning-sensitive arcs (+0.020, a flip from
   losing); (ii) whitening lifts the LIVE WSD meaning channel a_s +0.018-0.058 (n=2676).

HONEST CAVEATS / would withdraw first:
 - The meaning-channel whitening (+0.018) is UNVERIFIED: I ran only the a_s number, NOT the shuffled-diagnosticity
   twin, NOT a significance test, NOT a comparison vs the curated-foundation baseline (current best). Confirm
   before landing.
 - The parser-grounding lift is modest and subset-only (meaning's job is ROLE/non-canonical, not the word-order
   skeleton). The self-sup parser is not deployable; its stability/consolidation is unsolved.

RECOMMENDATION: (1) accept the ARC-LABELER fast path as done and land the Q111 diff (5/5 witness). (2) File two
follow-on problems: "whiten the meaning-channel embedding" (nearest testable win, +0.018 on its own instrument,
needs twin+significance+baseline) and "self-supervised + grounded front-end parser" (the north-star program).
(3) The free byte-safe parser win: flip the dormant arc-eager on for the general front-end too.

owner_verdict: (blank — yours to set)
