#!/usr/bin/env bash
# testbed_red_watcher.sh -- poll Health endpoint every 60s; emit notification on
# transitions to RED (drift detector flips to RED, or aggregate status worsens).
# Run via Monitor tool with persistent:true so each emitted line becomes a
# task-notification that wakes Testbed. Per USER 2026-06-21.
set -u
URL="http://localhost:8765/api/dashboard/v2/health"
NOTES_DIR="/d/AI/hd-instrument/notes"
STATE_FILE="/tmp/testbed_red_watcher_state.json"
SEEN_RED_NOTES_FILE="/tmp/testbed_red_watcher_seen_notes.txt"
PREV_REDS=""
PREV_AGG=""

# Initialize seen-set with current RED-class notes so we only alert on NEW ones (no spam)
: > "$SEEN_RED_NOTES_FILE"
if [ -d "$NOTES_DIR" ]; then
  find "$NOTES_DIR" -maxdepth 1 -name '*.md' 2>/dev/null \
    | grep -Eai "(red_flag|red-alert|data_referent_drift|data-drift|reproducibility_hazard|hold_chaingrade|runaway|leak|failed|cuda_oom|i_missed|missed_it|stall|crash|hang|hazard|over_call|self_catch)" \
    | sort -u > "$SEEN_RED_NOTES_FILE"
fi

echo "RED-WATCHER-ARMED: polling ${URL} + notes/ every 60s; transitions + new RED-class notes (no spam)"

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

  # === NEW: poll notes/ for new RED-class substantive notes ===
  # Catches cell-level RED-flags (data drift, runaway, leak, hold-chaingrade, etc.)
  # that aren't surfaced by dashboard drift detectors. Diff vs seen-set.
  if [ -d "$NOTES_DIR" ]; then
    current_red=$(find "$NOTES_DIR" -maxdepth 1 -name '*.md' 2>/dev/null \
      | grep -Eai "(red_flag|red-alert|data_referent_drift|data-drift|reproducibility_hazard|hold_chaingrade|runaway|leak|failed|cuda_oom|i_missed|missed_it|stall|crash|hang|hazard|over_call|self_catch)" \
      | sort -u)
    new_red=$(comm -23 <(echo "$current_red") <(sort -u "$SEEN_RED_NOTES_FILE" 2>/dev/null))
    if [ -n "$new_red" ]; then
      while IFS= read -r note; do
        [ -z "$note" ] && continue
        basename=$(basename "$note")
        echo "RED-NOTE-NEW: ${basename}"
      done <<< "$new_red"
      # Update seen-set
      echo "$current_red" | sort -u > "$SEEN_RED_NOTES_FILE"
    fi
  fi
done
