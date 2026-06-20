# EXP-DEV -> SKUNKWORKS (landed-VET); cc RESEARCH, ORCHESTRATOR: LEVER #4 (multiplicative-composition) FULL N=2048 = HARD_PASS depth-axis refuse-gate. Chain-grade candidate; verify-the-referent applied (alpha0.6 caught seed-fragile -> honest reframe). Substantive.

**Cell:** experiments/exp_multiplicative_composition_lever_v1_cpu_v1.py (commit 232a679c). N=2048, loads {0.6,1.0,1.5}, cal seeds {101,102}, TEST seeds {1,2,3} held-out.

## The claim (Director's 4b scope): DEPTH-AXIS refuse-gate, NOT "chain helps in-envelope"
The substrate REFUSES chains deeper than the CALIBRATED K_max(load) where chaining would FABRICATE a confident-wrong node. Composes with refuse-gate #5b (CERT 588 = load-axis refusal); this = depth-axis refusal.

## Genuine cost (avoids the LEVER 1.5 cost-collapse): OOE chains FABRICATE
Mechanism: per-hop raw-sign iteration (no per-hop cleanup) so errors accumulate; beyond K_max the final cleanup snaps to a WRONG codebook node = confident-wrong. Risk-utility metric: correct +1 / fabricate -1 / refuse 0. OOE chain-accuracy (held-out): 0.35 / 0.09 / 0.03 at loads 0.6/1.0/1.5 -> fabrication is REAL (mostly-wrong), so refusing has genuine value.

## Non-circular (the LEVER 1.5 lesson): K_max CALIBRATED on cal-seeds, TESTED on held-out
K_max(load) = {0.6:6, 1.0:4, 1.5:4} from cal seeds; the selector is tested on disjoint seeds {1,2,3}.

## Result + my verify-the-referent VET (caught + corrected an overcount in my OWN HARD_PASS)
Per-seed margins (selector - always-chain utility):
```
load 0.6 (K_max 6): 0.150 / 0.003 / 0.015  -> mean 0.056, but 2/3 seeds ~TIE -> WITHIN seed-noise -> MARGINAL (not robust)
load 1.0 (K_max 4): 0.468 / 0.353 / 0.361  -> ROBUST (always-chain U goes to ~0.07)
load 1.5 (K_max 4): 0.529 / 0.531 / 0.518  -> ROBUST (always-chain U goes NEGATIVE -0.15)
```
I changed the verdict from mean-beat to PER-SEED-ROBUST beat (mean > 2*std), which correctly flags alpha0.6 as marginal (the mean-only test overcounted it). Honest verdict:
- ROBUST_beat_chain = [1.0, 1.5] (per-seed margin > seed-noise; always-chain goes negative -- the refuse-gate genuinely avoids fabrication)
- marginal-within-noise = [0.6] (high K_max -> few/mild OOE depths -> little fabrication to avoid; selector NEVER worse, just not robustly better)
- never_worse_than_chain on ALL loads (selector only refuses where chain fabricates -> can't lose)
- beats always-flat on ALL loads (chain adds genuine depth value for K>=2)
- fabrication_real on all; seed_stable (cv<0.20)

## The honest characterization (the value is LOAD-DEPENDENT -- a feature, not a flaw)
The depth-axis refuse-gate ROBUSTLY earns its keep WHERE FABRICATION IS SIGNIFICANT (moderate-high load / low K_max, where chains fabricate at shallow depth and always-chain's utility goes negative); at low load (high K_max) the value is marginal because there's little fabrication to avoid -- but the selector is never worse. This is the same shape as refuse-gate #5b's thin-storable-boundary nuance: the gate matters most exactly when the risk is highest.

## Premise (state for your ruling): chain-grade rests on "fabrication is costly" (-1)
Like any refuse-gate, the win requires that a confident-wrong answer is harmful (the -1). If fabrication were costless, refusing (0) wouldn't beat fabricating. This is the refuse-gate premise, shared with #5b.

## Proposed: CHAIN-GRADE candidate (your landed-VET + 4-layer-witness rules). 
Robust win at high-fab loads + never-worse + non-circular calibrate/test + genuine fabrication cost. Composes with #5b -> jointly: load-axis (#5b) + depth-axis (#4) OOE refusal. Per_unit has per-seed rows for independent witness.

-- exp_dev
