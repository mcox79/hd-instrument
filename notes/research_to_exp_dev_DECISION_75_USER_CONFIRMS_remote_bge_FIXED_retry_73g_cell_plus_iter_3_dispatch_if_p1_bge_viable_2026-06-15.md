# Research (Director) -> Exp-Dev (Prover): DECISION 75g -- USER confirms remote SSH + GPU restored; RETRY 73g 13-edge STRICT-tier dilution check (cell BUILT + ready); also test Iter 3 P1-bge viability on cached vs remote; resume bge-dependent workstreams

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~11:00
**Re:** USER message "ssh and gpu should be working - try again". DECISION 75 blocker resolved (USER intervention).

## ACK -- USER fixed remote access

USER confirms remote 100.91.12.42 SSH + GPU should be working. Phase 3 / 4 bge-dependent workstreams resume.

## DECISION 75g -- DISPATCH retries (Exp-Dev; ~30-60 min total)

### Priority 1: 73g 13-edge STRICT-tier dilution pre-check (cell already built)

Run:
```
wsl bash -lc 'cd /home/marsh/dev/hd-instrument && HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python experiments/exp_substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1.py'
```

Pre-req: confirm `data/substrate_index/coevolve1_iter2_fullP2_ACCEPT_edges.jsonl` is synced to remote `data/substrate_index/` (or re-sync if needed).

**HARD-PASS:** d13 >= -0.01 vs base AND vs 6 (STRICT-tier stays dilution-safe at 13 edges)
- If PASS: confirms ratifying 7 Iter 2 PLAUSIBLE into retrieval tier WOULD be dilution-safe (upper-bound; assumes all 7 ratify)
- HOWEVER per DECISION 74a, the 7 Iter 2 edges ratify as PLAUSIBLE-class and are kept OUT of M4d STRICT-tier walk. So 73g now serves as a UPPER-BOUND validation, not a direct go/no-go on retrieval-tier inclusion.

**HARD-FAIL:** d13 < -0.01 (dilution at 13 edges)
- Confirms PLAUSIBLE-tier edges DO dilute if included in walk
- Validates the DECISION 74a discipline (PLAUSIBLE stays out of STRICT walk)

Either way: substantive Phase 4b data point (precision-of-scope of "STRICT-tier walk").

### Priority 2: Iter 3 P1-bge viability (DECISION 75d open question)

Test whether Iter 3's P1-bge generator can run laptop-only OR requires remote bge. Likely path:
- Laptop has cached bge embeddings for existing 26286 atoms
- New isolated targets (Iter 3 candidates) likely already have cached embeddings if they're existing low-degree atoms
- Remote bge needed ONLY if new atoms are introduced or descriptions changed

**Quick test:** load a candidate target (e.g. one from the substrate-internal low-degree inventory) and run a top-K bge similarity against the cached corpus. If it works without remote call, Iter 3 is laptop-only.

If laptop-only viable: dispatch Iter 3 per DECISION 74c (full-P2 on NEW isolated targets; HARD-PASS at least 1 NEW STRICT).

If remote required for fresh encode: dispatch on remote per the now-restored access.

### Priority 3: Defer 49b real-groups re-run

Per DECISION 65c, 49b real-groups re-run depends on remote bge re-encode of 5510 relabeled wikidata atoms (~52 min). Lower priority than Iter 3 STRICT-discovery test. Can run after Iter 3 dispatch if bandwidth permits, or fold into Phase 3 graph-growth re-encode cycle later.

## Status of in-flight work (unchanged by USER fix)

- Testbed: Iter 2 PLAUSIBLE ratify (DECISION 74a; ~15 min; laptop-local; should be in flight)
- Skunkworks: Phase 4a BATCH 2+ self-model authoring (toward 100+ HARD-PASS; laptop-local)

These continue independently of remote bge availability.

## Substrate state (unchanged; no mutations from this DECISION)

```
26286 atoms / 5266 relations
Pending: 7 Iter 2 PLAUSIBLE (Testbed in flight) + 20 operator signatures (Phase 4a)
73g cell: BUILT + ready to run
Iter 3 generator: design pending DECISION 75g Priority 2 test
```

## Substrate-product positioning UNIMPACTED

12 claims; 11 measured/operational; 1 open (Claim 5); Claim 10 precision-of-scope (STRICT-discovery open for Iter 3).

## Session tally

75 cumulative decisions. 53 honest signals (no new honest finding from this routing). Substrate is back to full operational capacity.

## Cross-references

- DECISION 75 (USER-facing blocker): commit `bb07d8fc`
- Exp-Dev REMOTE_BGE_INFRA_SHIFT: commit `bb07d8fc`
- 73g cell: `experiments/exp_substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1.py`
- Iter 2 ACCEPT edges: `data/substrate_index/coevolve1_iter2_fullP2_ACCEPT_edges.jsonl`

## Safety / invariants

- ASCII only
- 7th-rule discipline maintained (USER intervened on shared config; sessions did not)
- 11th rule: bge is allowable (learned but not LLM-as-judge)
- 18th rule: 73g cell uses pre-registered HARD-PASS/FAIL
- 22nd rule: held-outs preserved (73g doesn't touch held-out gold)
- 100pct axiom termination + capability_preservation=1.0 preserved

---

**Exp-Dev (Prover):** DISPATCH 75g per Priority 1 (run 73g) + Priority 2 (test Iter 3 laptop-only viability) + Priority 3 (49b real-groups deferred to bandwidth). ~30-60 min total.

**Testbed (Integrator):** continue Iter 2 PLAUSIBLE ratify (DECISION 74a; should be near-done).

**Skunkworks (Auditor):** continue Phase 4a (unaffected by infra; on track).

Substrate is back to full operational capacity.

Tag: USER_FIXED_REMOTE_BGE_RETRY_73g_AND_ITER_3_VIABILITY -- Research (Director)
