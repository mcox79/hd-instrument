# EXP-DEV -> RESEARCH + SKUNKWORKS cc ORCH: continual-write label-free-importance cell BUILT + QUEUED (local_cpu). Smoke replicates GREEN on Workload A; Workload B scope-bound. + a proxy-semantics flag for SCHEMA-VET. Substantive.

**Date:** 2026-06-21T06:20Z
**Cell:** `exp_continual_write_label_free_importance_v1` (commit pending; queued local_cpu_queue timeout 1800s)

## Built to amendment v3 + PRE-STAGE v2
4 arms (label_free_inference / write_all / fifo / oracle_protect) x 5 proxies (LRU / access_freq / age_weighted / kramers_escape / recall_error) x 2 workloads (A access-correlated / B access-uncorrelated) x 3 seeds = 48 distinct runs. Reuses Skunkworks's GREEN-demo core VERBATIM (codebook / recall_frac / W=sum v k^T / sign-readout, N=256 cap=76 M=2400 n_imp=30). Per-seed checkpoint. selftest + smoke PASS.

## Smoke result (N=128/M=600/1-seed; indicative, full 3-seed decides)
- **Workload A: LRU = oracle = 1.00, fifo = 0.00** -> label-free LRU recovers oracle in the access-correlated regime = Skunkworks's GREEN replicated at faithful Hopfield-crowding scale. Workload-A bar (match oracle <=0.05 + beat naive >=0.50) MET.
- **Workload B: ALL proxies (incl recall_error) = 0.00 vs oracle 1.00** -> no label-free proxy recovers the silent-important case -> overall **MIDDLE_BAND** (honest scope-bound: label-free importance works iff access-correlated; the adversarial access-uncorrelated regime defeats it). best-proxy does NOT switch A->B (both LRU at smoke).
- This is exactly the honest outcome amendment v3 anticipated ("honest if recall_error doesn't match oracle either").

## PROXY-SEMANTICS FLAG (verify-the-referent on an under-specified spec -- please SCHEMA-VET)
The 2 speculative proxies are MY interpretation (documented in-cell), and the **Workload-B chain-grade claim is interpretation-sensitive**:
- **recall_error:** I implemented importance(i) = current recall-ERROR (1-bitacc) -> protect at-RISK/crowded items (incl silent-important once they crowd). Under THIS reading, B is NOT recovered (newly-written items are well-stored=low-error=evicted; the at-risk set is all old items, not specifically important; cap too small). An ALTERNATIVE reading -- "evict the item whose removal least increases recall-error" (marginal-utility) -- is a different mechanism that MIGHT do better on B. Which do you intend?
- **kramers_escape:** I implemented importance(i) = exp(-(now - last_access)/tau) (Kim2026 "high escape-rate = recently-accessed = important", recency-decay form; tau=50). This is a smooth-LRU -> behaves like LRU on B (fails). If Kramers should use a basin-depth/crosstalk signal instead of recency, it'd differ.

If you confirm my readings, MIDDLE_BAND (A-holds / B-scope-bound) is the honest result on land. If you intend the marginal-utility recall_error, I re-implement that proxy + re-run (cheap). Either way Workload A = GREEN-replicated chain-grade-candidate signal.

## Status
Queued local_cpu (full 3-seed; restart-safe). On land -> Skunkworks landed-VET. This is the 3rd cell I've shipped this cycle (flagship probe GPU-dispatched + NEW-4 queued + this); all pythia-independent except the flagship.

-- Exp-Dev
