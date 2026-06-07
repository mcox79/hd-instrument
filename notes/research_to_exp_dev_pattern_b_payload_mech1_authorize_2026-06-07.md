# Research -> Exp-Dev: Pattern B Mechanism 1 (post-bind L2 normalization) AUTHORIZED

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Pattern B payload-magnitude control 2x drill output + exp_dev handoff.

## Authorize all 3 pre-tests from the drill handoff

Per the drill's `exp_dev_handoff_research_pattern_b_payload_control_2026-06-07.md`:
- Pre-test 1: Mechanism 1 (post-bind L2 normalization) on chain-k234 -- the primary v1.1 candidate
- Pre-test 2: Mechanism 2 (bipolar sign-only) as backup/comparison
- Pre-test 3: (whatever 3rd pre-test the drill specified -- read the handoff)

HARD-PASS criteria per the drill: chain-k234 recovers from HF to HP at K=2,3,4 with
capacity retention >= 80% and storage overhead <= 10%.

## Decision rule

If Mechanism 1 HARD-PASSes, that's the v1.1 fix (2-3 day engineering). Ship in next
Pattern B production stack release.

If Mechanism 1 BORDERs or FAILs, Mechanism 2 sign-only is the fallback.

## v1.1 ship recommendation

Mechanism 1 post-bind L2 normalization. 2-3 engineer-days. Zero HP risk to existing
Pattern B capabilities. Recovers chain-k234 HF for compliance multi-attribute query
support (deep chains of role-filler bindings needed for regulated workflows).

## Cross-references

- Pattern B payload-magnitude control 2x drill: notes/research_drill_pattern_b_payload_magnitude_control_2x_2026-06-07.md
- Drill's Exp-Dev handoff (the actual pre-test specs): notes/exp_dev_handoff_research_pattern_b_payload_control_2026-06-07.md
- C6 diagnostic (cycle 164 chain-k234 root cause): see exp_dev commit d9f7f2e

---

**END.**

**Exp-Dev:** authorize all 3 pre-tests per drill handoff. Mechanism 1 is highest priority.
Apply HARD-PASS / BORDER / HARD-FAIL decision rules autonomously. File verdict on
completion.
