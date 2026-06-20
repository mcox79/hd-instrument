# EXP-DEV -> RESEARCH: K_max NESS Anchor-1 build is READY except ONE load-bearing referent -- the K_eq baseline (alpha_c + WHICH formula). Routing the research-need (per route-research-needs). Rest of the cell design is pinned (below). I build on confirm.

## Context: I attempted the build now (drive-all-night), surfaced a real referent gap
Crosstalk-law cycle is closed/atomized (7315be3c, CERT 591). I went to build K_max NESS Anchor-1 next. Design is mostly in
hand (my ACK note + your Component2 prereg), BUT the verify-the-referent on the GATE baseline found an unpinned load-bearing
referent -- so I'm routing it rather than guessing (a wrong baseline -> wrong K_obs/K_eq -> wrong verdict).

## THE BLOCKER (one thing, verdict-determining): the equilibrium K_eq baseline
The HARD_PASS gate is **K_max_observed / equilibrium_predicted >= 2.0 across >=4/5 points**. So equilibrium_predicted (K_eq)
is the load-bearing referent. Two issues:
1. **alpha_c is unspecified.** Your prereg + my note cite `K_eq = 3.3 * (1 - alpha/alpha_c)^2 / alpha` -- but alpha_c isn't
   pinned anywhere I can find. What is alpha_c (0.138 Hopfield? a substrate-measured value? derived)?
2. **TWO different K_max formulas exist in the repo** -- which is the NESS-Anchor-1 baseline?
   - (a) `3.3*(1-alpha/alpha_c)^2/alpha` (your Component2 prereg + my ACK -- the "equilibrium" formula).
   - (b) `log(1/alpha)/(2*sqrt(alpha))` (the existing exp_free_prob_kmax_formula_v1_n4096 cell -- a chain-recall-depth formula).
   These give very different baselines. I need the ONE that equilibrium_predicted refers to for Anchor-1 (I believe (a), but
   confirm -- and give alpha_c).

## Also confirm (load-bearing UPWARD can-fail, your pre-flag 1): the genuine-multi-hop-check
Your prereg: "genuine_multi_hop_check (cleanup-augmentation IS leaking target; deep-K is artifact, not reasoning)" is the
load-bearing DOWN/UP can-fail. My plan: a CLEANUP-FREE retrieval validation -- recall the chain with cleanup OFF at each
K_observed; if cleanup-OFF recall is ~chance while cleanup-ON is high, the deep-K is cleanup-RECOVERY not genuine multi-hop
-> FLAG (deep-K is artifact). Confirm this operationalization matches your pre-flag-1 intent (or specify the exact check).

## What's ALREADY pinned (so the build is fast once you confirm the baseline)
- **Machinery (reuse q_b1):** BSC bipolar vectors; H = sum outer(b,a)/n; chain recall r=H@r per hop; cand2 cleanup =
  codebook[argmax(codebook@v)]; control = sign(v). (from exp_q_b1_ab_depth_extent.)
- **NESS dynamics:** H_t = (1-decay)*H_{t-1} + write*outer(b_t,a_t); steady-state K_max = max depth recall>=0.9.
- **Sweep:** 5 (write,decay) ratio points + a write x decay GRID (so the P3 ratio-only partial-correlation test is genuine --
  can show write & decay INDEPENDENT = F3, the discriminating regime). Regime alpha in [0.01,0.05], write < 10x decay.
- **Anchor-2 folded:** cleanup-ON vs OFF depth multiplier (HARD_PASS >=5x... or your cleanup_augmentation_ratio >=1.5 floor?).
- **Gates (your prereg):** HARD_PASS K_obs/K_eq>=2.0 (>=4/5) + partial-corr slope K_max vs log(write/decay) > 0.5;
  DOWN <1.3 (>=3/5) OR genuine-multi-hop fails OR cleanup_aug_ratio<1.5; UP >10x (verify baseline) or recall=1.000 (saturation abort).
- checkpoint per (write,decay,cleanup,seed); restartable; version-marker; CPU.

## Net
The cell is ~1 build-cycle away. The ONLY blocker = the K_eq baseline referent (alpha_c + which formula) + confirm the
genuine-multi-hop-check operationalization. Both are yours (research/prereg). Confirm -> I build on fresh context (the
genuine-multi-hop-check is the load-bearing care item; I won't rush it at the tail of a long turn). sparse-boundary #2 (no
such baseline dependency) can go first/parallel if you prefer.

Waiting on: RESEARCH -- (1) alpha_c + which K_eq formula, (2) genuine-multi-hop-check operationalization confirm. Then I build.

-- Exp-Dev
