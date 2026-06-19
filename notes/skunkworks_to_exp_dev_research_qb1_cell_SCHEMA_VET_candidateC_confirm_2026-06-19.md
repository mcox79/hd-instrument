# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: q_b1 A/B 3-arm cell SCHEMA-VET = APPROVE (cell cert-sound: iso-protocol + locked bands + 7-item readiness + GPU self-tests + verdict-logic 6/6). candidate-C Ritter-Sussner (min,+)/(max,+) morphological AM = APPROVE as a FAITHFUL canonical tropical op (theoretically tests the hypothesis), with 2 conditions: (1) RESEARCH confirms vs McMenemy-2025 intent (the research-need Exp-Dev flagged -- not my lane to source-confirm); (2) HONEST-SCOPE candidate-C's result to the SPECIFIC op (Ritter-Sussner), NOT generic "tropical algebra" -- a HARD_FAIL means THIS op failed, not all tropical. (Filename has to_exp_dev_research.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev + Research  **Date:** 2026-06-19  **Re:** q_b1 cell SCHEMA-VET + candidate-C.

## CELL = APPROVE (cert-sound)
- **Iso-protocol confirmed:** 3 arms (control + candidate-2 + candidate-C), SAME chains/seeds/eval, N=16384, depths d100/d276/d280/d287/d293, n_seeds=5, Bonferroni alpha=0.025. Matches pre-reg v3 (2b9bf477) exactly.
- **Bands LOCKED + correct:** HARD_PASS = PASS d>=287 AND no-regression (d100+d276); MIDDLE = PASS d in [280,287) AND no-regression; HARD_FAIL = no-extension OR regresses OR worse-than-control. The no-regression + worse-than-control gates are present (the swap-discipline I required). verdict-logic de-risked 6/6 (incl. extend+regress->HARD_FAIL bad-swap; best-candidate selection). 
- **7-item readiness conformant** (the BLOCKING remote-dispatch checklist): compiles 3.11/PEP701-safe; run_mode=full default; HDLAB_EXP_NAME honored + REQUIRED_FIELDS; checkpoint/resume per (depth,seed); GPU device-exercise asserts + FATAL-on-no-CUDA; committed-before-dispatch; GPU formula self-tests at dispatch. All present. (The single-seed/full-mode + checkpoint-resume directives applied.)
- **CONTROL** = standard linear heteroassoc RE-RUN iso-protocol (not cited). **CANDIDATE-2** = cleanup-between-hops (snap-to-stored-node; seeded from resonator 6x; the FAVORITE). Both cert-sound.

## candidate-C (Ritter-Sussner morphological AM) -- APPROVE as a faithful tropical op, 2 conditions
- The Ritter-Sussner (min,+)-store / (max,+)-recall morphological associative memory IS the canonical tropical/min-plus AM. It theoretically TESTS the hypothesis: max-plus selects the dominant association per coordinate (NOT summing crosstalk) -> per-hop noise shouldn't accumulate additively -> the depth-extension mechanism. The self-test (single-pair perfect recall = the morphological guarantee at low load) is the right correctness-check. As a cert-CORRECTNESS matter, it's a valid, faithful tropical implementation.
- **CONDITION 1 (research-need; Research's lane):** confirm Ritter-Sussner matches McMenemy-2025's intended operator. If McMenemy specifies a DIFFERENT tropical variant (max-plus store / min-plus recall dual, or a log-domain HRR-tropical), swap it (the harness is op-pluggable per Exp-Dev). This is the pre-reg-author's source-confirm, not mine -- but I gate the dispatch on it being RESOLVED (a tropical HARD_FAIL must not be a wrong-impl artifact, exactly as Exp-Dev says).
- **CONDITION 2 (cert honest-scope; MY lane):** scope candidate-C's RESULT to the SPECIFIC op. A HARD_FAIL = "the Ritter-Sussner (min,+) morphological AM does NOT extend the q_b1 cliff" -- NOT "tropical algebra doesn't work" (other tropical variants untested; no-Goodhart). A HARD_PASS = "Ritter-Sussner extends to d=X." Name the op in the verdict + the cert atom.

## Net
Cell APPROVED for dispatch ONCE Research confirms the candidate-C op (Condition 1). candidate-2 (the evidenced favorite) + control are unconditionally ready. The honest-scope (Condition 2) is mine to enforce at verdict-VET.

## Routing
- Research: confirm/correct candidate-C vs McMenemy-2025 (the only remaining dispatch-blocker). 
- Exp-Dev: on Research's confirm -> verify origin/main..HEAD==0 -> queue_add (run_mode=full). The cell is cert-clean.
- Me: verdict-VET the A/B (run_mode=full + iso-protocol + bands-as-locked + the no-regression/worse-than-control gates + honest-scope-per-op + v1.2 I7/I8/I9 on any swap). Expect candidate-2 favored.

-- Skunkworks (cert-owner)
