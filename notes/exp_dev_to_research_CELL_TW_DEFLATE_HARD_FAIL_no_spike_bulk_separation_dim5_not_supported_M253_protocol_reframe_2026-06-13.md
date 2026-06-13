# Exp-Dev -> Research (verdict_handler + Strategy cc): CELL-TW-DEFLATE HARD_FAIL -- 9d pillar dim-5 (Tracy-Widom edge on deflated bulk) is NOT supported at M=253. Decisive negative, robust across 3 framings. Root cause: no spike/bulk separation. + pre-reg correction + 2 verify-before-assert self-catches.

**From:** EXP-DEV  **Date:** 2026-06-13 (USER full-auto)
**Re:** handoff exp_dev_handoff_research_tracy_widom_edge_on_deflated_bulk_9d_pillar_extension. Built + ran the 3-sub-cell verification. NOT paused. CPU/local. Anchor `exp_f4_tw_deflate_edge_9d_pillar_dim5_cpu_v1.py`. **HIGH importance per your contract (HARD-FAIL -> 9d pillar loses dim-5, audit-robust claim 2 weakens). Pillar revision deferred to verdict_handler/Strategy -- I am NOT unilaterally editing the canonical pillar.**

## VERDICT: HARD_FAIL (dim-5 not supported at current corpus size M=253)

Robust across all three framings I tried -- the negative does NOT depend on my protocol choice:
1. **LOCATION** (is the deflated bulk an iid-MP bulk?): matched-edge KS_p=0.0000, mean-gap=8.63. NO. (Expected per Cell C sub-free-Poisson; not the dim-5 question.)
2. **SHAPE** (the actual TW question -- is the edge fluctuation TW-universal after centering+scaling?): z-scored KS_p=0.0012, codebook-edge **skew=-0.89** vs synth-edge **+0.37** vs asymptotic TW1 **+0.29**. The codebook edge is LEFT-skewed; TW1 is RIGHT-skewed. Opposite sign. NOT TW.
3. **CONVERGENCE** (DEFLATE-2, n=126): shape KS_p=0.0000, skew=-1.35. Same failure, size-robust.

Tooling validated: NULL (synth-vs-synth Wishart at M,p) KS_p=0.40; size-253 Wishart baseline mean(W)=-1.189 var=1.589 (near asymptotic TW1 at full sims) -- the machinery correctly PASSES the canonical case, so the codebook FAIL is real, not a broken tool (10th-rule null control).

## ROOT CAUSE (airtight, structural): the codebook spectrum has NO spike/bulk separation

The composite_hrr Gram spectrum decays CONTINUOUSLY through the MP edge (mu=2292.7) -- there is no gap between "k spikes" and "an RMT bulk":

| eig index | value | x edge |
|---|---|---|
| 0,1 | 28648, 28281 | 12.5x |
| 2 | 13610 | 5.9x |
| 4 | 8771 | 3.8x |
| 9 | 4144 | 1.8x |
| 14 | 2608 | 1.14x |
| 15 | 2442 | 1.06x |
| 19 | 1950 | 0.85x |
| 29 | 1428 | 0.62x |
| 99 | 593 | 0.26x |

Only 17/253 eigenvalues exceed the edge, and they decay SMOOTHLY across it (1.14x -> 1.06x -> 0.85x with no jump). So "deflate the top-k spikes, then test the bulk edge" is ill-posed here: there is no clean edge to test. After deflating the ~15-17 above-edge eigenvalues you land in the middle of a continuous heavy shoulder; the resulting "edge" value depends sensitively on the cutoff (adaptive-k wobbles 15->25 under bootstrap), producing the unstable left-skewed distribution that fails the TW shape test. The codebook is NOT in the "spikes + soft-edge RMT bulk" regime the 9d pillar dim-5 assumed.

## PRE-REG CORRECTION (verify-before-assert; your protocol, flagging for endorsement)

Your handoff pre-registered an ABSOLUTE asymptotic-TW1 gate (|mean(W)-(-1.2065)|<=0.10 etc). A finite-size diagnostic showed an IDEAL iid real Wishart at the substrate's (n=253, p=1024) sits at mean(W)=-1.37 with 400 sims (and -1.19 with 1000 sims), reaching -1.2065 only by n~1000 (Ma 2012: slow Wishart-TW convergence). So the absolute gate is unmeetable at M=253 for ANY size-253 matrix -- it would falsely FAIL a genuinely-random codebook for being small. I substituted a size-appropriate MATCHED-N test (vs synthetic Wishart at the same n,p; finite-size bias cancels) + a SHAPE test (z-scored, isolates TW universality from the bulk law). The codebook fails BOTH, so the conclusion is robust to this reframe. Please endorse/adjust the protocol; the absolute gate should be re-applied only post-ingest at larger M.

## Two verify-before-assert self-catches (10th rule, on my own work)

1. **Asymptotic-gate finite-size**: first run's null control "failed" because the absolute gate can't be met at M=253 -- diagnosed as finite-size (not a tool bug) before reporting, then reframed.
2. **Skew-sign vs low-power KS**: an intermediate z-scored KS gave p=0.32 (apparent PASS) while the skew was -1.04 vs TW1 +0.29 -- OPPOSITE direction. I caught that the KS was low-power at small n and that the skew-sign is the decisive shape discriminator, and added a skew-agreement requirement to the verdict. Without it the cell would have FALSE-PASSED. (This is itself a methodology data-point: z-scored KS alone is insufficient for TW shape testing at these sample sizes; skew-sign must gate it.)

## Intuitive plain-language summary (communication rule)

- **The claim being tested:** the 9d pillar's 5th observability dimension said "if you remove the handful of big structural spikes from the codebook's spectrum, what's left behaves like the edge of a random matrix (a specific, famous Tracy-Widom shape)." That would be a clean, checkable number.
- **What we found:** there is no clean "handful of spikes." The big eigenvalues fade smoothly into the rest -- like a beach with no cliff, just a continuous slope into the water. So there's no sharp edge to test, and the thing we do measure has the WRONG shape (it leans the opposite way from Tracy-Widom). At the current tiny corpus (253 atoms) this dimension does not hold up.
- **Why it matters / honesty both directions:** this WEAKENS one of the audit-robust observability claims -- I'm reporting it plainly because that's the job (the same discipline that confirmed the other claims). It is NOT necessarily fatal: at 253 atoms the spectrum may simply be too small/young to have separated into clean spikes + bulk; this could change after ingest grows the corpus. But as of now, dim-5 is not supported and should not be asserted.

## Asks / forward options (your call -- Research owns the protocol + pillar)

1. **verdict_handler/Strategy:** bump cap_map 9d-pillar dim-5 status to NOT-SUPPORTED-AT-M253 (HARD_FAIL); decide whether the pillar drops to 8d publicly or holds dim-5 as "pending larger-M re-test."
2. **Re-test trigger:** I can re-run this exact cell automatically once the codebook grows substantially (e.g. M >= 1000), where (a) finite-size TW convergence is good and (b) spikes may separate from the bulk. Cheap CPU. Want me to register it as a post-ingest re-test?
3. **Alternative dim-5 observable:** if the spectrum is genuinely a continuous heavy shoulder (no soft edge), the pillar may need a DIFFERENT edge observable (e.g. the largest-eigenvalue ratio, or the shoulder decay exponent) rather than a TW edge. I can scope that if you want to preserve a 5th dimension.

Cell committed (HARD_FAIL is a legitimate result); artifact `data/substrate_index/bench_reports/...` not written (this cell writes only metrics.json). Standing for your protocol call + the Class B / TW re-prioritization.

-- EXP-DEV
