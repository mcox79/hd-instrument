# Pre-registration: wave14_betS_pattern_completion_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy Phase 1 push #1 (META capability test A; 70-80% P; Lane D/F)
Author: experiment_dev session, pipeline tick 79

## Why

Per META strategic plan v79 + Strategy push: substrate does **bidirectional
recall** via Plate 1995 HRR inversion. LLMs are unidirectional. Direct
competitive advantage.

Test: store facts e = subj * rel * obj (BSC bind). Bundle M = sign(sum e_i).
Recovery via standard unbinding for ALL 3 slot directions:
- subject = M * rel * obj
- relation = M * subj * obj
- object = M * subj * rel
Cleanup against entity/relation codebooks at each.

## Multi-probe success criteria (per cap_map v75)

- Per-slot recall accuracy >= 0.85 (subject, relation, object) at K ∈ {8, 50, 200, 800}
- Slot-symmetric pass: no direction loses > 5pp to best
- 3 seeds at N=4096

## Verdict labels

- BET_S_PATTERN_COMPLETION_PASS (all 4 K, all 3 slots >= 0.85)
- BET_S_PARTIAL (some K or some slot below 0.85 but above 0.65)
- BET_S_KILLED (any direction < 0.65 across seeds at K <= 200)
- BET_S_INCONCLUSIVE

## Runtime: ~5 min
