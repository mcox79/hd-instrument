# Research request — antiRM(1,16) coset bias mechanism drill — 2026-05-24

**Trigger**: orchestrator autonomous cycle. Strategy shoreup matrix `notes/strategy_research_shoreup_matrix_2026-05-23.md` Weakness #4 named this as a HIGH-leverage cheap Research-only drill; v152 substrate-physics row still labeled "mechanism unknown" and stale since cycle 145. Per [[feedback-dont-dismiss-adjacent-methods]] the QECC-Kerdock-MUB adjacency from cross-domain probe #2 was flagged STRONG; dismissing it without dispatch is exactly the dominant failure mode the rule was named for.

Pause flag CLEARED at dispatch (no compute, so pause-flag check only matters for the followup); Research drills are unaffected by experiment pause regardless.

## Task hand-off (per [[feedback-no-experiment-design-in-prompts]])

WHAT: drill the mechanism behind the 0% within-linear-subcode overlap finding at v152 that REFUTED the RM(1,16) 25% prediction. Currently labeled "substrate-physics observable without mechanism narrative" — find a mechanism narrative OR confirm honest closure.

WHY (pointers, not summaries):
- Strategy shoreup matrix entry: `notes/strategy_research_shoreup_matrix_2026-05-23.md` Section "Weakness #4".
- Cap_map context: v181; the v152 anti-RM finding is the only "mechanism unknown" substrate-physics row in the portfolio per Pattern 6 (structural framings dominate the durable tier).
- Three candidate frameworks the matrix surfaced:
  1. QECC-Kerdock-MUB stabilizer-code-native vocabulary (off-syndrome condition); cross-domain probe #2 STRONG.
  2. Weight enumerators on RM(1,16) complement (cross-domain probe #2 WEAK but suggestive).
  3. Free cumulants on the v166 codeword-overlap distribution (KS=0.259); Pattern 7 cross-family consistency check with v164a R-transform asymmetry.
- v169 Kerdock-MUB-stabilizer isomorphism (LOAD-BEARING) is now closed-form and could provide the missing vocabulary directly.

CONTRACT:
- Type: research-only drill, no compute.
- Cost: ~30 min wallclock.
- Generic-math query framings per [[feedback-query-privacy-decomposition]]: "anti-coset bias in Kerdock 4-coset / RM(1,m) frame constructions"; "moment-based discriminators between coset and anti-coset subspaces"; "stabilizer code off-syndrome statistics on Z_4-linear Kerdock lifts"; "RM(1,m) complement weight enumerator asymmetry".
- Deliverable shape: short note (max 400 words body) at `notes/research_antiRM_mechanism_drill_2026-05-24.md` with: (a) lit-scan findings (citations); (b) which of the 3 candidate frameworks the lit-scan most strongly supports; (c) verdict: PROMOTE-TO-THEOREM-ANCHOR / CLOSE-AS-MECHANISM-UNKNOWN-CONFIRMED / NEEDS-COMPUTE-FOLLOWUP; (d) IF (c) is PROMOTE, a one-sentence draft mechanism statement that could land in cap_map as the row's mechanism annotation.
- Per [[feedback-lit-scan-calibration-penalty]] deflate P estimates 0.15-0.25 in uncharted regime; novel-synthesis cap P=0.50.
- Per [[feedback-no-smoke]]: if no lit-scan finding supports any of the 3 frameworks AND no clean substrate-internal kappa_n connection emerges, return CLOSE-AS-MECHANISM-UNKNOWN-CONFIRMED — that is a valid outcome, not a failure.

AUTONOMY DECLARATION: Research decides — exact query terms, sub-agent dispatch count, P calibration, framework ranking weights, decision boundaries between PROMOTE/CLOSE/NEEDS-COMPUTE, draft mechanism statement phrasing.

## Why ship now, not later

1. Strategy shoreup matrix #4 named this 1 day ago; it has not been dispatched.
2. Pattern 6 risk: non-structural rows drift. Either upgrade to theorem-anchored or close cleanly — both move the substrate-product story forward.
3. v169 Kerdock-MUB-stabilizer isomorphism JUST landed (recent verdict cycle) — that vocabulary may now make a clean mechanism statement tractable that wasn't 2 days ago.
4. Cheap (~30 min, no compute) and parallel to in-flight experiment pipeline — doesn't compete for CPU/GPU.

## Honest framing per [[feedback-no-smoke]]

This is a "math missing" gap not a "probe missing" gap. The substrate observation (0% within-linear-subcode overlap) is solid; what's absent is the published vocabulary that explains it. Three plausible mechanism families are named; lit-scan should find ONE that fits substrate's exact setup (Z_4-linear Kerdock, RM(1,16) complement, finite-N) or honestly conclude none does.

Expected outcomes (subjective prior):
- 45% PROMOTE-TO-THEOREM-ANCHOR via QECC-stabilizer off-syndrome framing (highest because v169 just landed).
- 25% CLOSE-AS-MECHANISM-UNKNOWN-CONFIRMED (honest closure; row's narrative changes to "observable without mechanism — substrate-physics empirical").
- 20% NEEDS-COMPUTE-FOLLOWUP (lit-scan surfaces a kappa_n / weight-enumerator angle that needs a ~30 min CPU probe to confirm; orchestrator queues that as a separate dispatch in next cycle).
- 10% LIT-SCAN-RETURNS-MULTIPLE-FRAMEWORKS (more than one fits; Research picks the cheapest-to-verify; orchestrator dispatches the verification cell).

Per [[feedback-dont-overextend-theorems]]: PROMOTE bar requires direct fit, not handwaved adjacency. If only adjacent-mechanism fits exist, return NEEDS-COMPUTE-FOLLOWUP rather than PROMOTE.

## status_log

Per [[feedback-for-you-tab-primary-channel]]: orchestrator writes status_log entry at dispatch (MEDIUM importance — research drill, not a compute ship); Research writes status_log entry at delivery (HIGH if PROMOTE, MEDIUM if CLOSE/NEEDS-FOLLOWUP).
