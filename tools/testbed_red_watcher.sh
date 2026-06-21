#!/usr/bin/env bash
# testbed_red_watcher.sh -- poll Health endpoint every 60s; emit notification on
# transitions to RED (drift detector flips to RED, or aggregate status worsens).
# Run via Monitor tool with persistent:true so each emitted line becomes a
# task-notification that wakes Testbed. Per USER 2026-06-21.
set -u
URL="http://localhost:8765/api/dashboard/v2/health"
STATE_FILE="/tmp/testbed_red_watcher_state.json"
PREV_REDS=""
PREV_AGG=""

echo "RED-WATCHER-ARMED: polling ${URL} every 60s; transitions only (no spam)"

while true; do
  sleep 60
  body=$(curl -sS --max-time 10 "$URL" 2>/dev/null) || continue
  if [ -z "$body" ]; then continue; fi
  # Parse RED detector names + aggregate status via python (jq not assumed)
  parsed=$(echo "$body" | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
agg = (d.get('aggregate') or {}).get('status', '?')
red = sorted([det['name'] for det in d.get('drift_detectors', []) if det.get('status') == 'RED'])
# Also surface integrity light if it's FLAGS
ig = (d.get('substrate_trust') or {}).get('integrity') or {}
if ig.get('status') == 'FLAGS' and ig.get('n_flags', 0) > 30:
    red.append('integrity-flags-rising')
print(f'{agg}|{\",\".join(red)}')
" 2>/dev/null)
  if [ -z "$parsed" ]; then continue; fi
  agg="${parsed%%|*}"
  reds="${parsed#*|}"
  # Emit on RED-list change OR aggregate transition to WORSE state
  if [ "$reds" != "$PREV_REDS" ]; then
    if [ -n "$reds" ] && [ "$reds" != "$PREV_REDS" ]; then
      # New REDs appeared (or set changed)
      new=$(echo ",$reds," | sed "s|,${PREV_REDS},||" | tr -d ',' || echo "$reds")
      echo "RED-ALERT: drift detector(s) NOW RED: ${reds}  (agg=${agg})"
    elif [ -z "$reds" ] && [ -n "$PREV_REDS" ]; then
      echo "RED-CLEARED: all drift detectors back to OK  (agg=${agg})"
    fi
    PREV_REDS="$reds"
  fi
  if [ "$agg" != "$PREV_AGG" ] && [ -n "$PREV_AGG" ]; then
    # Aggregate transitioned
    case "$agg" in
      ERROR) echo "AGG-WORSE: aggregate -> ERROR (was $PREV_AGG)" ;;
      WARN)  if [ "$PREV_AGG" = "OK" ]; then echo "AGG-WORSE: aggregate -> WARN (was OK)"; fi ;;
      OK)    echo "AGG-BETTER: aggregate -> OK (was $PREV_AGG)" ;;
    esac
  fi
  PREV_AGG="$agg"
done
