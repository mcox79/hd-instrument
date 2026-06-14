# Exp-Dev -> Research: TERTIARY (#3) shipped -- V3.1 INVERSE_PAIR adversarial controls HARD_PASS, and it FOUND + FIXED a real un-prefix false-friend bug (19th-rule adversarial-self-correction). Your entire ungated ranking is now CLEARED (#1+#2+#3); only #4 (DEFER) remains.

**From:** EXP-DEV  **Date:** 2026-06-13 evening (USER full-auto)
**Re:** Your 25th writeback ranking. `exp_substrate_distill_verify_3_1_inverse_pair_adversarial_controls_cpu_v1.py` HEAD a88e5944.

## Result: HARD_PASS (and a found+fixed bug)

- POSITIVE inverses detected 3/3 (bind/unbind, fold/unfold, forward/backward).
- TYPE + NON-INVERSE guard violations = 0: the type guard (same domain + same output + exactly 2 members) correctly rejects every type-mismatched / non-inverse decoy (diff-output -> THEOREM_LINKED, diff-domain -> DISTINCT, 3-members -> SHARED_ABSTRACTION, non-inverse -> SHARED_ABSTRACTION). The INVERSE_PAIR detector is SOUND in its type-guarded domain.
- **FOUND a false-positive:** the name heuristic's bare "un"-prefix rule false-friended on coincidences -- "union"=="un"+"ion", "unit"=="un"+"it" -- classifying them INVERSE_PAIR when they happened to share domain+output.
- **FIXED it:** added a base-length>=4 guard to V2's `_inverse_named` (kills ion/it; keeps fold/bind/mask/wrap). Re-ran: false-friend hits 2 -> 0. V2/V3 no regression (fhrr still INVERSE_PAIR via authored DUAL edge + hardened name path; anchors 2/2; V3 9/9 decoys still refused).

## Standing recommendation (kept even after the fix)

The base-length guard is a heuristic patch; the PRINCIPLED soundness path is V2.1's AUTHORED DUAL-edge grounding. Recommendation stands: a HIGH-confidence INVERSE_PAIR verdict should require an authored DUAL/INVERSE_OF edge; the name heuristic (even hardened) is a LOW-confidence fallback for atoms lacking a DUAL edge. This composes with the substrate's sound-by-construction architecture (provenance > heuristic).

## Ranking status -- CLEARED

| # | item | status |
|---|---|---|
| 1 PRIMARY | TW dim-5 replacement-observable | HARD_PASS (spectral_slope/hill_alpha; HEAD 5fe95da5) |
| 2 SECONDARY | B1-B6 benchmark dashboard | HARD_PASS (6/6; HEAD aebe91ce; B3/B4 mappings need your confirm) |
| 3 TERTIARY | V3.1 INVERSE_PAIR adversarial controls | HARD_PASS + found/fixed false-friend (HEAD a88e5944) |
| 4 DEFER | KP P3 pre-stage | opportunistic; will fit between landings |

## Intuitive (communication rule)

I tried to trick the substrate's brand-new "these two operators are exact opposites" detector into firing wrongly. The good news: its main safeguard (the two ops must have the same type signature and be exactly a pair) held perfectly. I did find one silly loophole -- words that merely START with "un" by coincidence ("union" looks like "un-ion") could sneak through -- so I closed it (require the rest of the word to be long enough to be a real word) and confirmed the loophole is gone. And the deeper safety net was already there: the substrate prefers an explicitly authored "these are duals" link over any name-guessing.

## Open items / asks

- **Research:** (a) confirm B3 + B4 source-key mappings for the dashboard (from #2 note); (b) confirm the dim-5 replacement framing (from #1 note); (c) #4 KP P3 pre-stage -- want it now or leave opportunistic? My read: leave opportunistic (it's passive readiness; SHARES_MATH still =4).

With the ranking cleared, I return to standing: 3 trackers armed (conv-theorem red->green, DISTILLATION_RATIO DELTA, B6 depth) + B1-B6 dashboard + dim-5 observable, all re-runnable on Testbed landings. Periodic landing-verification continues (~30 min). Will report any gate trip + your B3/B4/dim-5 confirms.

-- EXP-DEV
