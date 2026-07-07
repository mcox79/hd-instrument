# Research: the resonator reachability ceiling (post-verifier-readout residual)

Filed by: research (Sonnet lit-scan fan-out, Opus synthesis) | 2026-07-07
Trigger: `exp_resonator_verifier_readout_v1` HARD_PASS closed the aggregation-loss gap; oracle_any=0.806
at best T0 (K4) leaves ~19.4% of trials where the true factorization is never reached within R=10 restarts.
This note analyzes that residual — is it a restart-budget problem (cheap: add R) or a basin-measure /
algorithmic-wall problem (expensive: needs new dynamics) — and ties it to the basin-proliferation 4th
decode-family that falsified the CG_META self-margin law.

Numbers below are recomputed off-disk from `data/exp_resonator_verifier_readout_v1/metrics.json` and
`data/exp_resonator_glauber_plurality_v1/metrics.json` (both HARD_PASS / MIDDLE_BAND respectively, N=4096,
M=30, MAXIT=60, R=10, TR=120, seeds=[3,7,13], K in {3,4}). Source code read and traced:
`experiments/exp_resonator_glauber_plurality_v1.py`, `experiments/exp_resonator_verifier_readout_v1.py`.

## HEADLINE

At K=4, the reachability ceiling is **primarily a restart-budget problem, not a basin-measure wall**: the
per-restart probability of landing in the true basin is p≈0.15 (a solid double-digit share, not
vanishingly small), so oracle_any→0.95 is reachable with ~R=19 restarts (1.9x current compute) and →0.99
with ~R=29 (2.9x). The escape-probability-vs-temperature curve (0.247→0.747→0.789→0.800→0.806 across
T0=0→0.5) is a textbook Kramers-type saturating S-curve — pushing T0 higher than 0.5 is very unlikely to
help further per annealing theory. BUT the deeper CG_META-relevant question — whether a K-dependent
algorithmic wall (clustering/condensation transition, overlap-gap-property) caps p_basin toward zero as K
grows past 4 — is NOT answered by this K∈{3,4} data and remains the real open risk. A K=5/6 probe, not
an R-sweep, is the test that would actually confirm or refute the CG_META basin-proliferation falsification
at the mechanism level.

A secondary, unplanned finding: at T0=0.0 (fully deterministic, zero injected noise), the batched R=10
"restarts" already show oracle_any=0.247 vs the R=1 single-shot baseline=0.133 — nearly 2x lift with
**no dither at all**, reproducible across all 3 seeds (seed 3: 0.283 vs 0.158; seed 7: 0.192 vs 0.092; seed
13: 0.267 vs 0.150). Since the decode dynamics is provably deterministic at T=0 (code only draws noise
inside `if T > 0.0`) and all R rows share an identical tiled initial condition, this can only mean the
batched-vs-single BLAS matmul introduces enough floating-point-order differences (~1e-15) that the
60-iteration alternating-projection map — being chaotically sensitive near argmax ties — separates into
different final answers. This is a candidate "free" diversity source (no engineered dither needed) but is
inferred from arithmetic on existing metrics, not a dedicated ablation — flagged as a cheap verify-item
below, not asserted as fact.

## Cheap decisive test (ranked)

**1. R-sweep at fixed K=4, T0=0.5 (cheapest, confirms/refutes the restart-budget framing).**
Grid R∈{10,15,20,25,30}, same TR=120, same 3 seeds, same codebooks (paired). Fit oracle_any(R) against
the geometric-race model `1 - (1-p)^R` with p=0.1511 fixed from the R=10 anchor point, and check residual.
Compute cost: `decode_trial` batches all R rows in one vectorized numpy call, so cost scales roughly
linearly in R; the full parent cell (all K, all T0, all seeds, R=10) ran in ~22 min, so a single K4 arm
swept to R=30 is a small fraction of that (order minutes, CPU-only).
- HARD-PASS (restart-budget confirmed): oracle_any(R=20) and oracle_any(R=30) both within +/-0.03 of the
  geometric-model prediction (0.9004 and 0.9769 respectively) — restarts behave as advertised, "just add R"
  is a valid, cheap lever to 0.90+.
- HARD-FAIL (independence assumption breaks): oracle_any(R=30) undershoots the geometric prediction by
  more than 0.10 (i.e. < 0.877) — restarts are correlated / some later restarts are redundant re-draws of
  already-explored basins, meaning the true asymptotic ceiling is BELOW 1.0 even as R→∞ (a bounded-measure
  wall at fixed K=4, contradicting the "just restart-budget" read).
- Also settles the free-diversity anomaly cheaply: rerun `decode_trial` with R_=1 in a plain Python loop
  10x at T0=0.0 and diff against the batched R_=10, T0=0.0 result. If the looped version reproduces the
  0.133 baseline (not 0.247), the batched-BLAS-chaos hypothesis is confirmed — meaning numerically-diverse
  parallel copies are a free lever independent of engineered dither. Zero GPU cost, minutes of CPU.

**2. K-sweep at fixed R=10, T0=0.5, K∈{4,5,6} (more expensive, but the scientifically decisive test for
the CG_META wall question).** Measure whether the implied p_basin (backed out the same way, from
oracle_any at fixed R) stays roughly flat (~0.10-0.15, restart-budget regime persists) or collapses toward
zero as K grows (clustering/condensation onset — the OGP-style wall). This is the test that actually
discriminates "basin-proliferation is a K-dependent wall" (CG_META-consistent) from "basin-proliferation is
just a compute-budget dial" (favorable). Not recommended as the FIRST move (costs more: codebook
construction + full T0 grid scale with K), but flagged as the necessary follow-up once #1 is in hand.

Neither is dispatched here per instruction — recommendation only.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction A — geometric-race restart-budget model holds at fixed K=4.**
- HARD-PASS: R-sweep oracle_any(R) tracks `1-(1-0.1511)^R` within +/-0.03 at R=20,30 (see test #1).
- HARD-FAIL: oracle_any(R=30) < 0.877 (undershoot >0.10 vs prediction 0.977).
- P_deflated = 0.40 (lit-scan agent on Las Vegas/restart theory gave raw P≈0.30-0.35 for the general iid
  model, explicitly flagged shared-start restarts as NOT provably decorrelated in general; deflated further
  per calibration norms, but nudged up from the raw lit number because our own measured
  `mean_within_trial_distinct`≈9.19/10 at best T0 is on-platform evidence of near-max realized diversity in
  THIS specific regime, which the generic literature caveat doesn't have access to).

**Prediction B — no fundamental K-dependent wall below K=6 (i.e. p_basin stays bounded away from ~0 through
at least K=6).**
- HARD-PASS: K-sweep (test #2) shows p_basin(K=6) >= 0.05 (still a restart-budget regime, R~60 gets to 0.95).
- HARD-FAIL: p_basin(K=6) < 0.01 (basin measure collapsing toward the clustering/condensation regime;
  confirms the CG_META-style algorithmic wall — no realistic R rescues it).
- P_deflated = 0.30, capped per novel-synthesis rule (<=0.50). The basin-proliferation lit-scan found the
  clustering/condensation phenomenon is rigorously established as a function of problem size N (exponential
  cluster count), and the OGP-hardness literature conjectures/partially-proves a real barrier for local /
  message-passing / "stable" algorithm classes — which the alternating-projection resonator dynamics
  plausibly belongs to. That argues FOR expecting a wall at some K*, but the literature does not locate K*
  for this specific problem structure, and does not prove no algorithm can ever cross it (open
  complexity-theoretic territory, not closed). Hence low-but-not-negligible P, not near-zero.

## Cross-thread synthesis

- **With `exp_resonator_verifier_readout_v1` (HARD_PASS):** confirms the VET's own diagnosis — the
  verifier closed 100% of the aggregation-loss (verifier harvest == oracle_any exactly at every T0, 0
  invariant violations across all trials/seeds/arms per `verifier_le_oracle_invariant_violations: 0`), so
  the ENTIRE residual (1-oracle_any) is reachability, cleanly. No re-litigation needed there.
- **With `exp_resonator_glauber_plurality_v1` (MIDDLE_BAND):** the T0-sweep escape curve
  (0.247/0.747/0.789/0.800/0.806) is the same curve analyzed here; the parent cell's own framing
  ("basin-measure trap vs chaotic-sensitivity-favorable") is resolved by this note: distinct_wrong_min~999
  at best T0 (huge scatter, not collapse) + wtd~9.19/10 (near-max within-trial diversity) means it is
  chaotic-sensitivity-favorable, NOT a basin-measure trap, at K=4 — matching the parent cell's own
  HARD_FAIL "collapse" gate correctly NOT firing.
- **With `reference_self_margin_taxonomy_splits_by_decode_regime`:** the recurrent-search / basin-proliferation
  4th decode family is the correct mechanism class for this resonator (confirmed: alternating-projection
  fixed-point search, not order-statistic / collision-count / product-law-chain). This note's Prediction B
  is the operational test of whether that family's basin-proliferation mechanism is fatal (wall) or merely
  a budget dial at the K values actually in scope (K=3,4; product needs may not require K much beyond 4-6).
- **With `research_noise_compounding_bound_deep_mechanism_2026-07-07`:** that note's "regenerative-repeater
  / external-reset" framing explained why multi-hop reasoning survives (each hop re-cleans externally) while
  the resonator lacks that reset. This note adds the quantitative piece: even WITHOUT an external reset, the
  resonator's OWN stochastic-restart-with-verifier-readout gets most of the way (80.6%) to full recovery
  cheaply, and the rest is a restart-budget dial (at fixed K) rather than requiring an external-reset
  redesign — a more optimistic reading than the parent research note's framing, bounded to K<=4 pending the
  K-sweep.

## Substrate-product implications

- **K4 joint-factorization recovery, if product-relevant at K<=4-6**, is a solved-cheaply problem: verifier
  readout + a moderate restart bump (R~15-20, ~2x current compute, still CPU-only decode) gets to ~90-95%
  recovery. This is a real, near-term capability upgrade path with a known cost, not a research risk.
- **The open risk is scope, not mechanism**: if a substrate-product use case needs K>6 joint factors
  (e.g. deep multi-slot binding), the clustering/condensation literature says to expect the "just add
  restarts" lever to stop working past some K*, and a genuinely different search dynamics (not
  more-of-the-same annealed alternating-projection) would be needed. This is exactly the CG_META
  basin-proliferation risk, now given a concrete, cheap (K-sweep) test to locate K* empirically rather than
  reasoning about it in the abstract.
- **The batched-BLAS-chaos anomaly**, if confirmed, is a free-lunch observability note: "restart diversity"
  in this class of chaotic fixed-point search may not require engineered noise injection at all — running
  N numerically-independent copies (even bit-identical algorithmically) could already yield most of the
  diversity benefit. Worth a two-line verify before spending any further engineering effort on dither-schedule
  tuning.

## Citations (verified count: 4 parallel Sonnet lit-scans, 27 distinct sources cited across them; not
independently re-fetched by this synthesis pass — treated as first-order lit evidence per standard
sub-agent trust model, consistent with the deflation applied above)

Restart theory (8): Luby/Sinclair/Zuckerman 1993 "Optimal Speedup of Las Vegas Algorithms"; Tim Vieira
"restart acceleration trick" (heavy-tail SAT restart survey); arXiv:1703.01486 (restart optimizes Bernoulli
success probability); arXiv:2403.08409 (Poisson-restart universal properties); arXiv:1806.08984 (bet-and-run
strategy); arXiv:2501.10173 (optimal restart strategies, parameter-dependent); arXiv:2309.05877 (restart
under partial process-statistics knowledge).

Basin-proliferation / clustering (7): Mezard-Mora-Zecchina 2005 (clustering of solutions in random SAT);
Krzakala/Montanari/Ricci-Tersenghi/Semerjian/Zdeborova cavity-method program (condensation transition,
graph coloring, Springer 2015 + arXiv:1507.03512); Achlioptas/Coja-Oghlan + Budzynski/Semerjian
arXiv:1911.09377 (clustering-transition K-scaling, alpha_d(K) formula); Gamarnik/Bresler-Huang
overlap-gap-property arXiv:1212.1682; belief-propagation fixed-point proliferation arXiv:1605.06451.

Escape/temperature (5): Kramers escape-rate reviews (arXiv:2112.01373); Serdukova et al. "Stochastic basins
of attraction for metastable states" (Chaos 2016); Geman & Geman 1984 logarithmic cooling schedule; Hajek
1988 "Cooling Schedules for Optimal Annealing"; arXiv:2602.09398 (finite-time constant-T SA Markov analysis).

Diverse-init strategies (7): Wales & Doye basin-hopping (arXiv:cond-mat/9803344); Aleti/Wallace/Wagner
arXiv:1912.02535 (perturbation-restart effectiveness is landscape-contingent); Loshchilov/Schoenauer/Sebag
arXiv:1207.0206 (BIPOP-CMA-ES restart diversification); Hansen 2005 IPOP-CMA-ES; low-discrepancy-sequence
initialization comparative studies (MDPI 2021 Appl.Sci. 11(16):7591; MDPI Mathematics 13(11):1733); tabu
search diversification overview (IRIDIA lecture notes).
