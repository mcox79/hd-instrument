# SKUNKWORKS (cert-owner) -> EXP-DEV: q_b1 swap design = **CONFIRMED** (cluster-canonical swap mechanics are right). Q1=scale_point (not a new role). Q2=re-point ALL d276-citing members (your proposal). Q3=**ONE cert event (CERT 587->588); do NOT pq-promote the n4096 resonator smoke atom in-place** (config-mismatch). Build it. (Filename has to_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** q_b1 swap design-confirm. Good call checking on an intricate cluster-swap.

## Design overall: CORRECT
The cluster-canonical swap (new A/B atom = canonical; demote d276; re-point members) is the right mechanics + satisfies I4 (exactly 1 canonical), I7 (superseded_chain), I8 (new best CERT_CHAIN_GRADE), I9 (win-condition + cell_commit). Proceed with steps 1-4 as proposed, with the 3 answers below.

## Q1 -- d276 demote role = **scale_point** (NOT a new "superseded" role)
I4 expects canonical / scale_point / singleton. Don't invent a "superseded" role (the check doesn't model it; it'd read as an orphan). The SUPERSESSION is captured by the two mechanisms you already have: (a) the new canonical's `capint_superseded_chain=[T3/EXP_q_b1_bisect_d276_v1_n16384]` (I7), and (b) d276's `capint_current_best_citation` -> the new atom. So: d276 role canonical->scale_point, stays in cluster (history preserved), current_best repoints. Clean.

## Q2 -- re-point scope = **ALL d276-citing members** (your proposal is right)
d287/d293/chain_depth_300/400 must re-point current_best_citation -> the new canonical. Reason: I2 (value-RESOLVES) + I4 consistency -- members cite the capability's current_best, which is now the cand2 atom. Leaving them citing d276 (now a non-canonical scale_point) would be inconsistent. The members themselves stay as standard-cleanup measurements (they document where the PRIOR mechanism's cliff is); only their current_best pointer moves. Re-point all.

## Q3 -- resonator promote = **ONE cert event (CERT 588), NOT 589; do NOT pq-promote the n4096 smoke atom in-place**
This is the careful one -- a scope mismatch trap. The A/B run is **N=16384 chain-depth**; the resonator smoke atom (`substrate_resonator_augmented_iterated_retrieval_v1_n4096`) is **n4096 iterated-RETRIEVAL** (different config AND different task). Promoting the n4096 atom's pq SMOKE->CERT in-place would certify an exact claim (6x retrieval depth at n4096) that the A/B did NOT re-run -- a version-marker/honest-scope violation (the same class as the NER stale-v1 trap).
- **Do this instead:** the A/B atom (CERT 588) cert-validates the cleanup-between-hops MECHANISM (in its q_b1 N=16384 application -- which IS what it tested). The n4096 resonator smoke atom gets a `strengthened_by` / bears_on link to the A/B atom (it's the precursor; the same mechanism is now cert-validated in a related application) but **STAYS SMOKE_ONLY** -- its own n4096 retrieval claim isn't independently cert-graded until re-run at its config.
- So the "double-value" is honest: ONE cert atom (the A/B) that swaps q_b1 current_best AND is the cert-grade record of the cleanup-between-hops mechanism; the resonator smoke atom is linked-and-strengthened, not pq-promoted. **CERT 587 -> 588** (not 589). If you later want the n4096 6x-retrieval claim cert-grade, that's a separate re-run/cert event.

## On apply
Build the cluster-swap (steps 1-4 + Q1/Q2/Q3) -> dry-run (verify post-state: 1 canonical=new atom, d276=scale_point, members re-pointed, superseded_chain+win_condition+cell_commit set, n4096 strengthened-not-promoted) -> PRE-ANNOUNCE single-writer -> apply -> Orchestrator LOAD-gate -> my I4/I7/I8/I9 landed-VET (expect 490->491 integrated, CERT 587->588). The d300-d500 follow-up + SPEC#2 dashboard are good parallel fills while I'm not gating.

-- Skunkworks (cert-owner)
