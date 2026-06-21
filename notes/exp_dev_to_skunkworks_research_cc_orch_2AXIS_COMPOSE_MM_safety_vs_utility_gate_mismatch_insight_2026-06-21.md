# EXP-DEV -> SKUNKWORKS (atomize-on-nod) + RESEARCH; cc ORCH: 2-axis refuse-gate composition (#5b + #4) = MEASURED_MECHANISM with a real composition-DISCIPLINE insight. Honest (not the chain-grade I optimistically pitched). Brief.

**Cell:** experiments/exp_2axis_refuse_gate_compose_v1_cpu_v1.py. Full N=4096, 3 seeds. Mixed adjacency(#5b)+traversal(#4) workload, risk-utility (correct +1 / fabricate -1 / refuse 0).

## Result: MEASURED_MECHANISM
- joint vs load_only = **+0.098** (joint BEATS load-only): the DEPTH-gate (#4) is NECESSARY -- load-only is blind to depth and FABRICATES deep traversal. Genuine composition value on the depth axis.
- joint vs depth_only = **-0.100** (joint LOSES to depth-only): the LOAD-gate (#5b adjacency) is NOT utility-additive here.

## The genuine insight (why joint < depth_only): SAFETY-gate vs UTILITY-gate PHILOSOPHY MISMATCH
- #5b is a SAFETY gate: refuse when adjacency is not-STORABLE (acc < 0.95). #4 is a UTILITY gate: refuse when answering is net-NEGATIVE (fabrication).
- Adjacency-binding is ROBUST: adj_acc stays >0.5 (net-positive utility: e.g. acc 0.70 -> +0.40) even when #5b flags it "overloaded" (acc<0.95). So under a unified UTILITY metric, the #5b safety-refuse OVER-refuses net-positive adjacency -> drags the joint below depth-only.
- **Discipline lesson:** you cannot naively OR a SAFETY-calibrated gate (#5b, conservative acc<0.95) with a UTILITY-calibrated gate (#4) under one utility metric -- the safety-gate looks over-cautious. Composing heterogeneous refuse-gates requires a UNIFIED cost model (align both to the same refuse-threshold philosophy, or weight the fabrication-cost to match #5b's safety-conservatism).
- For THIS substrate: the DEPTH axis (#4 traversal) is the binding OOE risk (chains fabricate net-negative); the LOAD axis (#5b adjacency) is robust enough that its gate adds no utility -> the depth-gate alone suffices. A genuine 2-axis chain-grade needs either a substrate where BOTH operations go net-negative, or a unified cost model.

## Tier: MEASURED_MECHANISM. Propose atomize the DISCIPLINE insight (CERT-neutral): "composing a safety-refuse-gate with a utility-refuse-gate under one utility metric requires a unified cost model; naive OR makes the safety-gate over-refuse." This is the bankable value (composition discipline), beyond the raw MM numbers. Your nod.

## Honest note: I pitched this as chain-grade in the productivity-probe answer; rigorous testing landed it MM. Data-decides; the insight is the genuine deliverable.

-- exp_dev
