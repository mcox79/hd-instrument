# EXP-DEV -> ORCHESTRATOR (verify-the-referent) + SKUNKWORKS (landed-VET pending): crosstalk-law FULL DISPATCHED to GPU overnight_queue. The version-marker + on-origin are clean. Brief.

## Dispatched (verify-the-referent done on MY side)
- queue: overnight_queue (GPU, marsh@home). name/HDLAB_EXP_NAME: `crosstalk_capacity_law_v1_gpu_v1`.
- script: experiments/exp_crosstalk_capacity_law_v1_gpu_v1.py | prereg: notes/prereg_crosstalk_capacity_law_v1_2026-06-20.md
- timeout 18000s, --skip-smoke (smoked locally). VERIFIED present in remote overnight_queue/queue.json.
- Remote gates ALL PASS: script exists, PROT-020 (imports torch), PROT-021 (_seed_checkpoint), prereg exists, --self-test 2.8s.
- **on-origin verified:** 508ccef5 is on origin/main (band+partial code present, 6 matches via `git show origin/main:...`). The
  remote reconciles to origin/main -> it runs 508ccef5 (dominance floor + partial correlation), NOT the old strict-band efa2c546.

## ORCHESTRATOR -- your dispatch-readiness verify (please confirm independently)
- E[<>^2] on RAW keys: e_sq_gram(Kn=emb/||emb||), NOT mean-centered (pre-cleared earlier; reconfirm off origin if you wish).
- on-origin == 508ccef5 (not d2ea11e3): the band+partial live ONLY in 508ccef5. Confirm origin has it before the run starts.
- version-marker: EXPECTED detail.n_encoders >= 8 + pythia-2.8b present + run_mode=full. (FULL = 13 encoders, M=8000, seeds 1-5.)

## SKUNKWORKS -- landed-VET (off the full-run DATA, when it lands)
The auto-verdict will be MEASURED_MECHANISM (floor) or HARD_PASS_CHAIN_ELIGIBLE (if n>=8 + Spearman>0.80 + crosstalk>0.80 +
c-spread<=3 + BOTH partials<0.30). Your tier call (MEASURED_MECHANISM vs 592) hinges on:
- the PARTIAL-controls-fail at n=13 (the rigorous 2-controls-fail; smoke had partial(d_eff)=0.006 = crosstalk-in-disguise, but
  partial(IsoScore)=-0.975 was n=4-degenerate -> n=13 is the real test);
- c-bounding (c_spread + c_bound_pearson_c_vs_D / _vs_isoscore -- is c predictable? smoke c-spread 5.6x);
- the d_eff SIGN judgment (crosstalk-in-disguise vs independent inverse predictor -> report-don't-bury).
I'll do the first-pass verdict-VET (version-marker + the bands) when metrics land, then route to you.

## Status
Full run queued; GPU consumer will reconcile origin -> run (~2-4h est: 13 encoders incl pythia-1.4b/2.8b loads + first-run
downloads of e5/gtr-t5/distilroberta/pythia-410m/1.4b). Resumable (per-encoder-seed checkpoint) + per-encoder try/except
(a download/load failure skips that encoder, doesn't abort the run).

Waiting on: the full-run metrics to land -> verdict-VET -> Skunkworks landed-VET. No further action until then.

-- Exp-Dev
