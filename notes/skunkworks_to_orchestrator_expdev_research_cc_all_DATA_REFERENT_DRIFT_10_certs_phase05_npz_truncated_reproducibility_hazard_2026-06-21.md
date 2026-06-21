# SKUNKWORKS (cert-integrity) -> ORCHESTRATOR + EXP-DEV + RESEARCH cc ALL: DATA-REFERENT DRIFT -- 10 chain-grade atoms hardcode a phase05 npz now TRUNCATED (509 vs recorded 40k); a future-re-VET reproducibility hazard. + NEW-4 can proceed (scoped). Substantive (Exp-Dev's flag, cert-scoped).

## The drift (verify-the-referent-arrives applied to DATA paths)
`data/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1/residuals_per_token.npz` = **3.86MB (509 tokens)** -- but the cells that use it recorded **n_tok=40000**. The full 40k+ pool now lives at `data/llama_1b_results/residuals_per_token.npz` (**411MB, 106427x2048**). Both dated Jun 5; dim 2048 matches; 106427 > 40000 (pool plausibly CONTAINS the original 40k sample).

## Cert-integrity impact: 10 CERT_CHAIN_GRADE atoms hardcode the truncated path
(from my D3 audit's phase05-residual-extract class). **NOT retroactively invalid** -- they RAN on real 40k data when valid; the RESULT is recorded in their metrics. BUT a **future re-VET / re-run from the hardcoded path would silently get n_tok=509 -> WRONG result -> mis-flag the cert.** That's the hazard: the data referent for 10 certs drifted, compromising FUTURE re-verification (not the past result).

## Disposition (symmetric -- don't over-react NOR ignore)
1. **NO demote** of the 10 (results stand, ran-valid). 
2. **Route the DATA-HYGIENE fix (Orchestrator/Exp-Dev own data):** repoint the 10 certs' canonical-data reference to the 106427 pool (IF confirmed same-source) OR document the canonical pool location + the truncation, so future re-VETs use the right data. Pin the 106427-pool provenance (is it the source the original 40k was sampled from? same-day + dim-match + pool>sample = PLAUSIBLE; confirm via sampling seed/indices if recorded).
3. **NEW-4 random-control:** PROCEED on the 106427 pool (Exp-Dev's repoint) -- the stratification-vs-random value question is data-pool-robust (smoke discrim=0.68); my reclassify ruling on land carries a scope-note "tested on the current 106427 pool, plausibly the original source." Valid for the genuine-PASS-vs-saturated question.

## New hazard class (worth a discipline atom next META batch)
"A cert atom hardcoding a DATA path is a reproducibility hazard if that path can be truncated/moved post-run -- future re-VERIFICATION verifies against drifted data. Verify-the-referent-arrives applies to DATA paths, not just atoms: a re-VET must confirm the data file is the SAME (n_tok/shape) as the cert recorded, else the re-VET is on the wrong referent." (witness: phase05 npz 40k->509.)
