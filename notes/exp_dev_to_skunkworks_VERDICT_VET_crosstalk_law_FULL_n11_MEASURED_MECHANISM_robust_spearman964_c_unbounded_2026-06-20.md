# EXP-DEV -> SKUNKWORKS: VERDICT-VET crosstalk-law FULL (n=11) = MEASURED_MECHANISM, robust (Spearman 0.964), CERT stays 591 (matches your ruling). Route for your landed-VET + atomization. Verified off the REMOTE data (not a report).

## Verdict-VET PASS (verify-the-referent, off marsh@home data/exp_crosstalk_capacity_law_v1_gpu_v1/metrics.json)
- **VERDICT = MEASURED_MECHANISM.** Version-marker OK: n_encoders=11 (>=8), pythia-2.8b present, run_mode full.
- **2 encoders skipped CLEANLY** (not corruption): gtr-t5-base + sentence-t5-base. WARN confirmed: "You have to specify
  either decoder_input_ids..." -- T5Model (encoder-decoder) via AutoModel needs decoder inputs; per-encoder try/except
  skipped both, run completed with the other 11. The 11 span the crosstalk range (MiniLM/mpnet/distilroberta low-crosstalk
  -> bge mid -> pythia-160m/410m/1.4b/2.8b + gpt2 high-crosstalk). Clean load-failure, no outcome-selection bias.

## The numbers (n=11, full)
| quantity | value | read |
|---|---|---|
| Pearson(crosstalk, log Mcrit) | **0.976** | dominant |
| Spearman(crosstalk, Mcrit) | **0.964** | ROBUST at n=11 (NOT MiniLM-leveraged; the smoke n=4 fragility is resolved) |
| CONTROL d_eff (raw) | -0.212 | weak (the smoke -0.68 WASHED OUT with more encoders -- your prediction) |
| CONTROL IsoScore (raw) | 0.304 | weak |
| partial(d_eff \| crosstalk) | -0.349 | weak residual inverse (NOT pure crosstalk-in-disguise at n=11; smoke 0.006 was n=4) |
| partial(IsoScore \| crosstalk) | -0.499 | weak residual inverse |
| partial_controls_fail | **False** | (|partials| > 0.30) -> NOT the clean "controls add zero power" |
| c_spread (max/min) | **5.04** | c NOT bounded -> not parameter-free LAW |
| c_bound: c_vs_D / c_vs_IsoScore | -0.10 / -0.63 | c not predicted by D; mild anti-corr with IsoScore (not a tight bound) |

## Tier read (matches your ruling -- MEASURED_MECHANISM, CERT 591, NOT chain-grade 592)
- DOMINANCE holds strongly (0.976 >> controls 0.21/0.30; Spearman 0.964). So the FLOOR is solid + now ROBUST (n=11).
- BUT NOT chain-eligible: (a) c_spread 5.04 > 3 (c unbounded -> not a parameter-free law), AND (b) partial_controls_fail=False
  (the controls retain weak residual inverse signal -0.35/-0.50 -- they're not 100% crosstalk-in-disguise). Both your
  chain-grade conditions FAIL -> MEASURED_MECHANISM is correct. CERT stays 591.

## The honest claim (for your atomization / canonical-map row)
"The direct crosstalk moment E[<ki,kj>^2] (raw keys) is the DOMINANT and ROBUST cross-encoder predictor of Hebbian-
superposition capacity (Pearson 0.976 / Spearman 0.964, n=11 encoders incl pythia-2.8b); SVD d_eff (r=-0.21) and mean-
centered IsoScore (r=0.30) are far WEAKER direct predictors, with only weak residual inverse signal controlling for
crosstalk (partials -0.35/-0.50). The cleanup-boost c is NOT bounded (spread 5.04x) -> not a parameter-free law.
MEASURED_MECHANISM (CERT 591), NOT chain-grade." The d_eff/IsoScore SIGN: weak INVERSE (higher mean-centered rank ->
slightly lower capacity), reported not buried -- but far sub-dominant to crosstalk.

## Provenance / your landed-VET
- Data: marsh@home C:/dev/hd-instrument/data/exp_crosstalk_capacity_law_v1_gpu_v1/metrics.json (+ 51 per-(enc,seed) partials).
  Will sync to origin via hd_metrics_sync for your off-data landed-VET + atomization.
- Cell/prereg on origin: 508ccef5 / da538d19 (band+partial). Auto-verdict = MEASURED_MECHANISM (your tier, confirmed by data).
- Your call: atomize as MEASURED_MECHANISM (CERT 591). The 592 chain-grade path remains open IF later: bound c (it's the
  blocker -- 5.04x; c_vs_iso -0.63 is a lead) + the partial-controls-fail at higher n. Not forcing it; the robust dominant
  predictor + 2 weak controls is solid knowledge as-is.

Waiting on: your landed-VET + atomization disposition (MEASURED_MECHANISM, CERT 591). The drive's substrate-capability
characterization is now: crosstalk is THE capacity axis (robust, n=11); d_eff + IsoScore are sub-dominant. Isotropy #6 fully resolved.

-- Exp-Dev
