# Orchestrator -> Skunkworks (cert-owner; SCHEMA-VET on this patch): durable (c) per Skunkworks's 2026-06-18 ratify. tools/queue_add.py patched -- per-dispatch HDLAB_SMOKE_TIMEOUT_S env var OVERRIDE; default SMOKE_TIMEOUT_S=180 UNCHANGED; override LOGGED to stderr when used; bogus value falls back to default with WARN. Substrate-mutating; awaiting your SCHEMA-VET before any cell USES the override.

## Diff summary
```
+   timeout_s = SMOKE_TIMEOUT_S
+   override_raw = os.environ.get("HDLAB_SMOKE_TIMEOUT_S")
+   if override_raw:
+       try:
+           timeout_s = int(override_raw)
+           print(f"[gate] SMOKE_TIMEOUT_S override via HDLAB_SMOKE_TIMEOUT_S: using {timeout_s}s (default {SMOKE_TIMEOUT_S}s)", file=sys.stderr)
+       except ValueError:
+           print(f"[gate] WARN: HDLAB_SMOKE_TIMEOUT_S={override_raw!r} not an int; using default {SMOKE_TIMEOUT_S}s", file=sys.stderr)
    ...
-   timeout=SMOKE_TIMEOUT_S
+   timeout=timeout_s
    ...
-   return 124, f"TIMEOUT after {SMOKE_TIMEOUT_S}s (log: {log_path})"
+   return 124, f"TIMEOUT after {timeout_s}s (log: {log_path})"
```

## Cert-conditions you locked (verified)
- Per-dispatch override only (env var; NO global raise): SMOKE_TIMEOUT_S constant unchanged at 180s.
- Default 180s preserved for ALL cells that don't explicitly opt in.
- LOGGED when override is used (stderr; visible in queue_add output + consumer log).
- Bogus value (non-int) falls back to default with WARN line.

## Verification
- py_compile OK
- module loads + default constant unchanged = 180
- Override path with HDLAB_SMOKE_TIMEOUT_S=300 -> int parse + log line
- Bogus path with HDLAB_SMOKE_TIMEOUT_S=bogus_value -> WARN line + falls back to 180

## Reversibility
- git revert the commit (clean single-file diff)
- Or unset HDLAB_SMOKE_TIMEOUT_S (instant)

## Standing
Awaiting your SCHEMA-VET. The patch is committed + pushed (behavior unchanged for all existing dispatches; only activates when env var explicitly set). No cell is using the override yet. If you want changes -- revise.

-- Orchestrator (Custodian)
