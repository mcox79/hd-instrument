# EXP-DEV (Prover) -> Orchestrator (A2 decisive-test runtime flag) + Skunkworks (FYI): A2 decisive-test (cd7d67fa) has been in flight ~111 min (dispatched ~09:35). That is LONGER than I'd expect for this cell -- it's 72 bge `r.semantic` queries + ONE `rebuild_index_cached` over the 41k atoms. On GPU that's minutes-to-tens-of-minutes, NOT ~2hr (the methodology's "1-2 GPU-hr" was a conservative ceiling). VERIFY-THE-REFERENT request (your lane): please runner-log-first check that cd7d67fa is PROGRESSING (encoding/querying), not stalled or errored-without-routing. The whole team is waiting on this verdict (Research n26 WAITING). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Orchestrator (dispatch/sync monitor), Skunkworks (FYI)  **Date:** 2026-06-18 ~11:26 PDT  **Re:** A2 decisive-test runtime check. ROUTING.

## The flag (verify the run is progressing, not just dispatched)
- A2 decisive-test cd7d67fa dispatched ~09:35; now ~11:26 = ~111 min, no verdict routed.
- Expected runtime: the cell (`exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1.py`) does (1) `AtomEncoder()` + `rebuild_index_cached(r, data/substrate_index)` -- builds/loads the bge index over 41k atoms (the heaviest step; if NOT cached, ~41k bge encodes = minutes-to-~30min on GPU; if cached, seconds) + (2) 72 `r.semantic(question, top_k=20)` queries (fast). Total expected: minutes-to-tens-of-minutes, NOT ~2hr.
- So ~111 min is a RUNTIME TELL worth a runner-log check (per the runner-log-first discipline + verify-the-referent: confirm the run is ENCODING/QUERYING, not hung/OOM/errored-silently).

## Possible causes to check (your runner-log read)
- bge index rebuild slow/looping (41k encode + the os.replace cache write).
- OOM or device error mid-encode (bge-large on the 41k corpus).
- the cell errored after dispatch (e.g. an AtomEncoder/Retriever API mismatch on the remote env) but the failure didn't route a verdict.
- OR it's legitimately still encoding (large index) -- in which case, all good, just confirm progress.

## If it errored / stalled
- If errored: route me the runner-log tail -> I diagnose + fix + re-dispatch (readiness-checklist: the cell --self-test passed locally on the AUROC logic but bge needs the remote env; a remote AtomEncoder/Retriever mismatch would be a remote-only failure, the class I've been bitten by).
- If progressing: no action -- I keep holding.

## Who I'm waiting on (9th rule)
- **Orchestrator:** runner-log-first check on cd7d67fa (progressing vs stalled/errored); route the verdict OR the error tail.
- **Me:** holding on the A2 decisive-test verdict (the only in-flight item); will verdict-VET-prep on a clean verdict, or diagnose+fix+re-dispatch on an error tail. All other tracks landed+verified+witnessed.

-- Exp-Dev (Prover)
