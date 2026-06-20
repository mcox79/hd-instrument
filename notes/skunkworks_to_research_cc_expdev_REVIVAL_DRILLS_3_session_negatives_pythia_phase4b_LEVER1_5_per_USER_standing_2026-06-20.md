# SKUNKWORKS (cert-owner) -> RESEARCH (cc EXP-DEV): ROUTING 3 session negatives for 2x/3x REVIVAL DRILLS (USER standing directive 2026-06-20: every negative -> Research revival drill; routing is my job). Each with a candidate revival angle. Substantive.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** USER directive -- "whenever there is a negative result, Research should be performing 2x/3x research drills on them for potential revival; you should be routing that work to Research." Applying it to this session's NOT-chain-grade rulings.

## Negative 1: pythia_substrate_kv_pull_up_v2 -> NOT chain-grade (DEGENERATE SATURATION)
- **The negative:** recall=1.0 on all 90 points (no margin, no degradation) -> non-discriminating; couldn't be a capacity cert.
- **Revival angle (2x/3x):** is the saturation itself a HIDDEN POSITIVE? Two sub-questions: (a) are Pythia-2.8B last-token keys SO separable that they genuinely support >>100k facts (a strong positive -- the glass-box-KV-at-scale claim) -- testable by the nearest-neighbor MARGIN (if margin is large + stable to high M, it's genuine capacity, not a metric artifact); OR (b) is the recall metric trivially saturated (a null)? The margin analysis + a random-key control DISCRIMINATE these. This is a textbook negative-was-positive candidate (saturated-metric vs trivially-separable-keys). Worth a drill.

## Negative 2: phase4b_multistep_pull_up_v2 -> NOT chain-grade (div-by-near-zero ratio + 2op-only-MultiArith)
- **The negative:** "2-op composition generalizes to 3 benchmarks" is false (only MultiArith does 2-op); the 40x ratio is a 1op-MultiArith=0.017 divide-by-near-zero artifact.
- **Revival angle (2x/3x):** (a) is MultiArith-2op (0.69, seed-stable) a genuine NARROWER chain-grade ("substrate composes 2-op on MultiArith")? (b) the 1-op MultiArith ANOMALY (0.017 -- the easiest case near-zero) -> is this a fixable REPRESENTATION/encoding gap (word-order? operand-binding?) that, if fixed, REVIVES the generalization to ASDiv/MAWPS 2-op? The anomaly is the lever -- if 1-op MultiArith is fixable, the whole composition story may revive. Worth a drill on the representation gap.

## Negative 3: LEVER 1.5 v2 capacity-sweet-spot -> MEASURED_MECHANISM (no selection value)
- **The negative:** the adaptive selector doesn't earn its keep -- a fixed sparsest-f (0.01) is never beaten because the sweet-spot is BROAD (no over-sparsity cost in the recall-only metric).
- **Revival angle (2x/3x):** find a regime where over-sparsity has a GENUINE COST (storage/bytes per active dim, precision/SNR at very-sparse f, compute, or a downstream task where sparser hurts) -> a NARROW sweet-spot -> the selector REVIVES as chain-grade (the cost is what makes selection a real problem; per my atomized lever-design discipline 99392cca). The K_MIN cost dim wasn't enough; what cost makes the sweet-spot narrow? Worth a drill on the cost-dimension design.

## Process note
Per the USER standing directive, I'll route EVERY future negative I rule (NOT-chain-grade / HARD_FAIL / demote / fell-short MM) to you for a revival drill, in the same cycle, with a candidate angle. (Atomized as a standing discipline.) The 5MM demotes (a1_multihop = by-construction control [not revivable as a win]; t3_phaseA2 + partof_2level = broken-referent -> RE-RUN is already their revival path per my disposition) -- noted, the re-runs ARE their revival; flag if you want a deeper drill.

## Standing
- **Research:** 3 negatives routed for 2x/3x revival (pythia-saturation-or-positive / phase4b-MultiArith-2op-revive-+-1op-anomaly / LEVER-1.5-find-the-cost-dimension). Your drill cadence; each is a genuine revival candidate (not a forced revive -- data-decides, symmetric).
- **Exp-Dev (cc):** these overlap your queued reframes (pythia margin+control, phase4b narrow-claim, LEVER 1.5 cost-dim) -- Research's revival drill + your reframe compose.
- **Me:** routing-for-revival now standing per-negative. CERT 587 (588 pending refuse-gate #5 b raw-witness). `fleet_waiting_on.md` current.

-- Skunkworks (cert-owner)
