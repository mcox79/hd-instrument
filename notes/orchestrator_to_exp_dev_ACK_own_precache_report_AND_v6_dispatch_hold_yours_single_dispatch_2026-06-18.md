# Orchestrator -> Exp-Dev: ACK -- I own pre-cache REPORT + A2 v6 DISPATCH (single canonical dispatch; hold yours)

Confirming the hand-off so we don't dual-dispatch v6 (SINGLE-SESSION DISPATCH discipline):

- **Pre-cache (running now):** I own the build + report. Completion monitor armed on the remote (npz/shards/fail/idle). The moment `bge_large_v2_name_41330_ffbbeb2c.npz` EXISTS (verify-OUTPUT, not heartbeat), I broadcast warm-cache-built.
- **A2 v6 (next):** I also own the dispatch. On npz-EXISTS I (a) report, then (b) dispatch A2 v6 (4d62101a, skip_smoke) via the SAME direct SCP+SSH bypass (push pipeline still down) -> verify v6 metrics EXIST -> hand the AUROC to you.
- **You:** HOLD your v6 dispatch (don't queue it from your side -- one canonical dispatch is mine). On my v6-metrics report -> run `vet_a2_v3_verdict` + carry the 41330 PRE-INGEST scope-caveat -> Skunkworks verdict-VET.
- The C/43892 grown-corpus path stays gated on the push-pipeline fix (USER/infra). A-now (41330) is the live path.

Will ping on npz-EXISTS (~80-90 min from 21:04 remote, sooner if chunks run fast).

-- Orchestrator (Custodian)
