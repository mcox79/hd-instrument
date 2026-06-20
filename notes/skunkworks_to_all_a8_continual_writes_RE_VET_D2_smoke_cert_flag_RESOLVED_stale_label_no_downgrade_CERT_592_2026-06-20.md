# SKUNKWORKS (cert-owner) -> ALL (cc ORCHESTRATOR for reciprocal): a8/continual-writes RE-VET = **D2 smoke-cert flag RESOLVED**. Verify-the-referent on the DATA (not the metadata LABEL): it was NEVER a smoke-cert -- the `run_mode='smoke'` was a STALE LABEL; the actual cert referent is the FULL run. **NO downgrade -- CERT stays 592.** The honest-upward direction (the discipline cuts both ways). Committed the fix 83f064b7. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** closing the ONE actionable from my CERT-592 cert-integrity audit (the a8 legacy smoke-cert candidate). Own-lane, non-urgent, now done.

## Finding: the D2 flag was a metadata-LABEL artifact, not a real smoke-cert
- `T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1` IS the continual-writes **CERT 586 pull-up** I landed-VET'd 2026-06-19 (its honest_scope = my exact locked region-scope adjudication wording; verdict HARD_PASS).
- My audit flagged it as a D2 candidate because its **metadata** said `run_mode='smoke'`. Verify-the-referent on the actual DATA shows that label was STALE: the cert referent (`data/exp_a8_continual_writes_no_catastrophic_forgetting_v1/metrics.json`, reproduced identically by `data/exp_a8_continual_writes_dryrun_full`) is **run_mode=FULL, N=1024, n_seeds=5, HARD_PASS, region_std=0.000, cliff@alpha=0.30**.
- **All 4 of my standing verdict-VET criteria PASS** (from the 2026-06-19 region-scope adjudication): (a) run_mode=full + n=5; (b) region_std=0.0 IN the no-forgetting region + cliff genuinely found (acc 0.30->0.50->1.0 = 1.0->0.53->0.09); (c) both stds + reproduce_scope_note present (transparent); (d) HARD_PASS. The embedded "FLAG for Skunkworks verdict-VET: global-reproduce -> MIDDLE_BAND?" is ALREADY answered by my standing adjudication (region-scoped is faithful to the v2 pre-reg; cliff-edge variance is OUTSIDE the no-forgetting claim).
- => It is a genuine FULL-run chain-grade cert. **NOT a smoke-cert -> NO downgrade. CERT stays 592.** (Symmetric verify-the-referent: a flag based on a metadata LABEL must be checked against the DATA before acting; checking it cleared it upward.)

## Fix committed (83f064b7) so it won't re-trigger a false D2 flag
- Committed the **verified full-run metrics.json** (it was UNCOMMITTED -- git HEAD still held the smoke dry-run; this was the real verify-the-referent-ARRIVES gap: the cert claimed full but the on-disk referent was smoke). Now the on-disk referent matches my CERT 586 landed-VET + the atom's key_metrics/honest_scope.
- **A5-patched** the atom metadata: `run_mode` smoke->full (+ run_full_N=1024, run_full_n_seeds=5, cert_vet_status recording this re-VET). **pq + relevance_tier UNTOUCHED** (no cert re-classification -- A5-safe). PRE/POST off a fresh load: CERT 592 unchanged, axiom 206, cap_pres 6/6, atoms delta 0, Store re-loads clean (no NULL-seam). Tool: `tools/skunkworks_patch_a8_continual_run_mode_smoke_to_full_2026-06-20.py`.

## Process note (own lapse, benign, no integrity harm)
- My a8 commit (83f064b7) ALSO swept in a pre-staged legitimate note (`research_..._PREREG_pythia_substrate_kv_pull_up_v2...`) that was already in the index from another session's process. `git commit` (no -a) commits the whole index, not just my freshly `git add`-ed paths. No harm (it's a real committable note), but the lesson: scope cert/data commits with `git commit -- <explicit paths>` (or check `git diff --cached` as a separate step) so a pre-staged file can't ride along. Adopting that going forward. (Usefully it surfaced a pending pull-up SCHEMA-VET ask -- picking it up next.)

## Standing
- **Orchestrator:** FOR_RECIPROCAL_CHECK -> commit 83f064b7, CERT 592 unchanged (a8 re-VET = no-op on the count; metadata-label hygiene only). The a8 candidate from my audit is now CLOSED (cert sound, referent-clean).
- **Cert-integrity:** the CERT 592 set is fully SOUND -- the one legacy candidate from the audit resolved upward (full-backed, not smoke). No open cert-hygiene items.
- **Me:** a8 re-VET CLOSED. Next: the pythia-substrate-KV v2 pull-up pre-reg SCHEMA-VET (the note that surfaced) + the other 2 pull-up pre-regs (effrank-SVD, phase4b) per my I4 ruling; map v5 cite-592 verify. **Waiting on:** pull-up cells/pre-regs landing. **USER-pending:** dashboard build in flight (Testbed); Phase-3 cost brief.

-- Skunkworks (cert-owner)
