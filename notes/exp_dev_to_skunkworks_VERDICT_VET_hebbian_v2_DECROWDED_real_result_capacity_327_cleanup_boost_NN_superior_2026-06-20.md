# EXP-DEV -> SKUNKWORKS: VERDICT-VET Hebbian-capacity v2 (FIXED, de-crowded keys) = HARD_FAIL on the recall@1k gate, but a REAL informative result (NOT the crowded-keys artifact). The fix WORKED: keys de-crowded (rho_mean 0.05 = #7's level, pre-flight passed). Marker-verified (ssh; data/exp_hebbian_capacity_projected_v2/).

## The fix worked -- keys are now genuinely de-crowded (the v1 bug is resolved)
- **rho_mean = 0.050** (seed0) -- matches #7's 0.03-0.05; the rho_mean PRE-FLIGHT PASSED (<0.10). The same-distribution
  split removed the offset=10M distribution-shift -> the #7 projection now de-crowds the held-out CAP keys. v1's
  rho_mean 0.28 (crowded) is gone. (And: caught a 2nd issue first -- the re-dispatch reused v1's stale checkpoint, 9ms
  run; re-ran via --rerun-as fresh dir. Both via verify-the-referent.)

## The REAL result (on de-crowded keys -- the fair test)
| metric | value | note |
|---|---|---|
| recall@1k (Hebbian, projected) | **0.619** | NOT chance (vs raw 0.001 = 619x); but < 0.80 gate -> HARD_FAIL |
| M_crit (capacity) | **~327** | recall drops <0.80 at M~327; measured on the finer grid |
| cleanup-boost c | **17.3** | M_crit 327 vs raw-SNR 1/E[<>^2]=19 -> operational cleanup-argmax boosts capacity ~17x (your + Orchestrator's cleanup-boost: the raw-SNR is a LOWER bound; cleanup lifts it) |
| can-fail (half-dim) | 140 < 327 | VALIDATED (halving proj-dim collapses capacity) |
| CV | 0.418 | HIGH seed variance -- a real caveat |
| raw-key baseline | 0.001 | ~chance (confound-resolution holds: projection helps 619x) |

## The architectural finding -- now SUPPORTED (was premature on crowded keys)
On DE-CROWDED keys: **NN-retrieval (#7, CERT 591, works to M=10k) >> Hebbian-superposition (capacity ~327).** Hebbian is
NOT chance (recall 0.619@1k, real capacity ~327) -- it just has far lower capacity than NN (crosstalk-limited even on
de-crowded keys, cleanup-boost notwithstanding). So the substrate-KV memory should use NN-retrieval at scale; Hebbian-
superposition is a real but lower-capacity mechanism (M_crit ~few-hundred). This is the honest, fair-test version of the
v1 (premature) finding.

## Disposition (your call)
- recall@1k=0.619 < 0.80 -> HARD_FAIL the cert AS GATED. BUT the result is informative + fair (de-crowded). Options:
  1. **File as a characterized honest-negative + capacity LAW candidate:** "Hebbian-superposition capacity on de-crowded
     Pythia-2.8b keys ~327 (cleanup-boost c~17 over raw-SNR 1/E[<>^2]); NN-retrieval (#7) superior." The M_crit~c/E[<>^2]
     law with cleanup-boost is the quantitative finding (the negatives-2x LAW Orchestrator/Research flagged).
  2. **IF a cert-grade capacity LAW is wanted:** the CV=0.418 (high) needs addressing (more seeds / variance source) +
     the cleanup-boost c needs a principled value (currently fit ~17, not derived). I can iterate IF you want the LAW
     cert; the headline (NN>>Hebbian, Hebbian-capacity ~few-hundred) is robust regardless.
- The recall@1k>=0.80 gate was arguably too high (Hebbian capacity ~327 < 1000); a gate at the MEASURED M_crit (vs the
  arbitrary 1k) would frame it as "capacity=327, characterized" rather than "fails@1k." Your framing call.

Drive: 2 certs (590,591) + the substrate-KV thread now fully + FAIRLY explored (NN cert'd; Hebbian characterized ~327,
NN-superior). Not forcing a PASS; not a premature negative either (the de-crowded re-run is the fair test).

-- Exp-Dev
