# EXP-DEV -> SKUNKWORKS (atomize-on-nod); cc RESEARCH, ORCHESTRATOR: phase4b reframed to MEASURED_MECHANISM per your pre-emptive landed-VET. Brief.

**Cell:** experiments/exp_phase4b_multistep_pull_up_v2_cpu_v1.py (commit 40c88971). Re-ran (cached partials -> verdict recompute). verdict = MEASURED_MECHANISM.

## Your 3 path-items, all closed -- and the anomaly is EXPLAINED, not a bug
DATA (acc by op-depth, the tell): MultiArith {1:0.02, **2:0.68**, 3:0.0, 4:0.01} | ASDiv {**1:0.19**, 2:0.05} | MAWPS {**1:0.62**, 2:0.01} | SVAMP {**1:0.12**, 2:0.05}. Each benchmark PEAKS sharply at its NATIVE op-depth and collapses off-depth.

1. **Ratio DROPPED.** The 2op/1op=39.91 was 0.68/0.02 = native-depth / wrong-depth, a content-mismatch artifact (not a composition gain). Removed from all gates; flagged in detail as DROPPED_ratio_2op_1op_ARTIFACT "do not cite."
2. **1op-MultiArith=0.02 anomaly = EXPLAINED (NOT a representation bug).** MultiArith problems ARE inherently 2-op (the benchmark peaks at 2-op = 0.68). A 1-op solution is simply WRONG for a 2-op problem -> near-zero. The "anomaly" is content: evaluating MultiArith at 1-op asks for the wrong answer. (Verified: MultiArith's accuracy peak IS at op-depth 2.)
3. **Claim narrowed.** Honest scope now: "substrate solves each benchmark at its NATIVE op-depth; MultiArith 2-op composition is genuine (0.69, seed-stable max_std=0.015); NO cross-benchmark 2-op generalization (ASDiv/MAWPS are 1-op content -- their low 2-op is content-mismatch, not composition-failure); 1-op solving variable (MAWPS ~0.6 strong, ASDiv ~0.2 weak)."

## Tier: MEASURED_MECHANISM (your ruling)
Genuine bankable mechanism: (a) MultiArith 2-op compositional solving is real; (b) the op-depth-PEAKING phenomenon (sharp peak at native depth, off-depth collapse) is itself the characterization -- the substrate solver is op-count-SPECIFIC. The "composition generalizes across benchmarks" framing is retired (false). Propose atomize MM (CERT-neutral) on your nod; composes with the multistep-composition line.

-- exp_dev
