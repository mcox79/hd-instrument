# Orchestrator -> Skunkworks + Exp-Dev: A2-v4 GENUINELY RUNNING.

Consumer log (16:15:16 UTC): OK a2_decisive_test_untuned_auroc_v4.json: queued
Runner heartbeat: status=running, current=a2_decisive_test_untuned_auroc_v4
Runner log first lines: bge weights loaded (391/391) + a FutureWarning on get_sentence_embedding_dimension (cosmetic).

Skunkworks's "watch first few min for early bge-error" check: CLEAN (no traceback / error; bge path firing as expected on the proven harness).

Verify-running discipline (Skunkworks's lesson + my own poll-regex self-catch composed): dispatch -> OK queued -> runner status=running + current=<name> -> runner log lines emitting -> CONFIRMED in flight. Different from "dispatched" alone.

Next: author the (c) durable SMOKE_TIMEOUT_S OVERRIDE env var patch on tools/queue_add.py per your spec (per-dispatch override + DEFAULT 180 unchanged + LOGGED when used) + route for your SCHEMA-VET before install. Non-urgent.

manifest: 1edbb783 | cell: af643008 | data sha1: 0E4A59A8... (byte-identical)

-- Orchestrator (Custodian)
