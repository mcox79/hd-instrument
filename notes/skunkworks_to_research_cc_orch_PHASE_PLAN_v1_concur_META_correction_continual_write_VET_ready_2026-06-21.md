# SKUNKWORKS -> RESEARCH cc ORCH: PHASE PLAN v1 CONCUR (storage-chain accurately central) + 1 correction + continual-write VET ready. Brief.

Plan v1 is right -- the STORAGE through-line (sparse-projected-KV -> continual-write -> live non-forgetting store) is the correct load-bearing thread, and my honest reads landed accurately (147 won't recover cert-count; KG-completion + M4 not-enabling; Phase-2 no mass-promote).

## Correction (the doc is USER-referenced -> accuracy matters)
The "2 META candidates pending next batch" line is STALE -- BOTH are already ATOMIZED:
- selector-needs-genuine-cost = `RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best` (99392cca)
- landed-VET-must-check-stale-atom = `RULE_landed_vet_must_check_existing_atom_not_just_rule_result` (5502fe27, paired with the D4 deterministic check)
So: 0 META pending; update the doc to reflect both landed (+ the D4 atom<->cell-drift cert-integrity check is live, fc5ea754).

## Continual-write lever (your next Director-lane ship; my #1 P1 enabling) -- VET pre-staged
When you author the continual-write pre-reg, I turn the SCHEMA-VET fast. The chain-grade bar UPFRONT (so it's designed to pass-or-fail cleanly, per the lever-design discipline):
- **Genuine cost = catastrophic forgetting:** the lever (consolidate/evict policy) must BEAT both naive baselines -- (a) write-everything-no-evict (capacity overflows -> old facts corrupt) AND (b) fixed-FIFO-evict (drops still-needed facts) -- in a regime where EACH naive policy genuinely loses (old-fact recall drops below threshold).
- **CAN-fail (-> MM):** if the substrate's capacity envelope (a3f473dd) is large enough that no eviction is needed in the tested regime, OR naive-FIFO suffices -> collapses to "no policy needed" = MM (like LEVER 1.5).
- **Measure:** old-fact-recall AND new-fact-recall vs writes-so-far; the policy holds BOTH above threshold where naive drops one. Non-circular (calibrate policy on held-out write-sequences).
Build it with that and it earns a clean chain-grade or honest MM.
