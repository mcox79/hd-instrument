# Exp-Dev (Prover) POST-COMPACTION BRIEF -- 2026-06-15 (~17:30)

Resume state for the Exp-Dev (Prover) session. Read this first after any compaction. Latest prior brief was 2026-06-12_cycle50 (stale).

## ROLE
Exp-Dev (Prover): build experiment cells / pre-check gates, run them (laptop CPU or remote GPU), report via notes routed on the event bus. EXECUTE don't narrate; honest decisive results incl negatives; verify-before-asserting (10th rule); refuse-what-cannot-prove (18th rule).

## COMPUTE (corrected this session; the "remote down" story was WRONG)
- LAPTOP: `d:/AI/hd-instrument/.venv/Scripts/python.exe` -- torch 2.12 CPU + transformers + sentence_transformers; BAAI/bge-large-en-v1.5 cached. AtomEncoder loads ~8s. Use for structural + small-bge jobs.
- REMOTE GPU: `ssh marsh@home` -> `C:/dev/hd-instrument/.venv/Scripts/python.exe` -- torch 2.5.1+cu121, RTX 4060 Ti, bge ~5.8s. Windows-native (NOT WSL; the WSL path /home/marsh/... was a stale red herring). For GPU runs: scp cell + any laptop-created data into C:/dev/hd-instrument; remote substrate state may lag laptop (sync if post-cleanup state needed).
- bge env vars: HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1.

## MONITOR (fixed this session)
Tail consumer on data/events/exp_dev.log (shared event_bus.sh producer, PID 1773732 post-106a restart). ROUTING GAP found + fixed: `*to_exp_dev*` glob missed multi-recipient notes where exp_dev was not first after "to_" (missed DECISION 102-105). Fix: line 34 `*exp_dev*` (+ orchestrator broadened testbed/research/skunkworks). Verified live (105-108, 116 now route). If monitor ever silent on multi-recipient notes again: backstop with `find notes -iname "*exp_dev*" -newermt "Nmin ago"` (NOT a heavy loop).

## PRE-CHECK GATE STACK (my core deliverable; experiments/ + tools/)
Run BEFORE any non-additive Testbed ratify. 4 independent gates, operation-class-invariant + corpus-scoped:
1. forward-walk reachability -- experiments/exp_substrate_88c_forward_walk_reachability_precheck_cpu_v1.py
   `precheck_batch(tier, adj, removals, adds, tier_changes=[], corpus=None) -> {stranded, monotone_violations, ok}`.
   FORWARD = {DEPENDS_ON, SPECIALIZES}; axiom = T1; catches leaf-stranding from edge-inversion (87c) AND tier-mutation (84a). Monotone is corpus-scoped (92a/94: cross-corpus exempt). USES/non-FORWARD rel-types exempt (93d-1). `load()` returns (tier, adj, corpus).
2. axiom-termination -- backward_chain from exp_substrate_proof_finder_backward_chaining_cpu_v1 (visited-set + depth cap; cycles sound per 78d).
3. retrieval-F1 -- exp_substrate_82g (M4d held-out unchanged check; needs bge).
4. all-rel-type dangling + CROSS-STORE -- tools/substrate_cross_store_cleanup_v1.py
   `cross_store_cleanup(ps, deleted_qualified_id, execute=False)` + `find_cross_store_dangling(ps, qid)`. Closes the cross-store-TARGET dangling gap (remove_atom misses other-store (local_src, rel, X_qualified) tuples). execute=False = dry-run for pre-check; execute=True for Testbed merge flow.
Merge flow per atom-delete: re-point distinct OUT to canonical -> ps.remove_atom -> cross_store_cleanup(execute=True) -> post: dry-run must return [].

## SESSION DELIVERABLES (this session)
- Phase 2/3: M4d 0.272 (in-distribution amplifier); Iter 1/2 CO-EVOLVE; Claim 12 (72b).
- Iter 3: HARD_FAIL tier-flatness -> motivated W-TYPE-SIG lever (Claim 13).
- Iter 4 (100a): 0 new STRICT (measure_space->set vet-REJECTED as mis-typed composed_of). Claim 5 SPLIT -> 5a member-growth MEASURED (17 STRICT via Phase-4e), 5b autonomous-discovery OPEN (authoring-time-bound boundary).
- GPU experiments: 73g (STRICT-tier dilution-safe) + 82g (cleanup preserves M4d F1).
- Built the 4-gate pre-check stack; gated BOTH HARD_FAIL recovery arcs (batch-2b 89b, 84a-RETRY) + 101b/101c + Phase-3 sub-batches.
- 105c cross-store cleanup primitive (smoke PASS).
- Fixed event_bus exp_dev routing gap.

## CURRENT STATE / PENDING (as of ~17:30)
- Phase 3 atom-MERGE/SPECIALIZES_fix in flight (DECISION 105-116):
  - Tier 1A (6 stub deletes): RATIFIED HARD_PASS (107a).
  - Sub-batch 4 (SPECIALIZES_fix) + Tier 1B (4 conv-dup merges): RATIFIED HARD_PASS (109b/113); my pre-checks were the gate; matrix_decomposition leaf-strand rescue verified.
  - Sub-batch 2 (kl_divergence T1 merge): pre-check GREEN (43 cross-store refs need 105c); Testbed ratify dispatched (113). AWAITING Testbed exec.
  - Sub-batch 3 (collins word-order merge): pre-check GREEN (26 cross-store refs need 105c); Testbed ratify dispatched (116). AWAITING Testbed exec.
- Standing: pre-check support for remaining Phase-3 work; verify post-op 0-dangling on merges Testbed routes me; Iter 5 / Phase-4e Author-N if dispatched.
- Drills A/B (110/111) + authoring-blind audit (114) = Testbed/Skunkworks lanes (Goodhart/Claim-5a-positioning); I am "standing pre-check support" only.

## SUBSTRATE-PRODUCT POSITIONING: ~16 claims; 15 MEASURED/OPERATIONAL + 1 OPEN (Claim 5b autonomous STRICT-discovery). Claim 14 (self-corrects own graph) strongest: 5 op-classes + 2 recovery arcs + 4-gate pre-check + rollback. USER Level-2 hand-off CLOSED at production (Claim 15).

## KEY RULES: 11th (no LLM; substrate-internal) / 10th (verify-before-asserting) / 18th (refuse-what-cannot-prove) / 22nd (held-outs DO-NOT-INGEST; 56d SHA 22d7eb01, 56d-v2 untouched). Methodology FROZEN at 24. Report ACTUAL numbers.

-- EXP-DEV (Prover)
