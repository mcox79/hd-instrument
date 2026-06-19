#!/usr/bin/env bash
# EXP-DEV cycle-start SELF-CHECK (LAYER 2 heartbeat backstop; DECISION 161 canonical architecture).
# Run at the TOP of every work cycle / on every 10-15 min heartbeat (13th USER-LOCKED rule).
# Purpose: self-heal the monitor-consumer-death + tail-F reattach-gap failure modes. The INBOX
# (mtime-aware widenet over notes/) is AUTHORITATIVE -> catches notes addressed to me EVEN IF the
# harness Monitor (LAYER 1) died or dropped lines during a reconnect window. ASCII only.
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null || exit 1
echo "=== EXP-DEV CYCLE CHECK ==="
WINDOW_MIN=20

# 1. AUTHORITATIVE inbound: notes addressed TO exp_dev (or broadcast _to_all_) modified in the
#    last WINDOW_MIN min, EXCLUDING my own outbound (exp_dev_to_*). Catches missed dispatches.
RECENT=$(find notes/ -maxdepth 1 -type f -mmin -"$WINDOW_MIN" \( -name '*exp_dev*' -o -name '*_to_all_*' \) ! -name 'exp_dev_to_*' 2>/dev/null | sort)
N_RECENT=$(printf '%s\n' "$RECENT" | grep -c . )
echo "INBOX (to-me/broadcast, last ${WINDOW_MIN}min): $N_RECENT"
if [ "$N_RECENT" -gt 0 ]; then
  printf '%s\n' "$RECENT" | sed 's,^,  >> ,'
  echo "  >> ACTION: if you were NOT notified by the LAYER-1 monitor, it is DEAD or dropped a"
  echo "     reattach-window line -> RE-ARM Monitor (persistent, tail -n0 --retry -F data/events/exp_dev.log,"
  echo "     filter ROUTING|BROADCAST, author-out grep -v 'notes/exp_dev_'). Then READ+ACT the notes above."
fi

# 2. SHARED event-bus PRODUCER alive? (feeds ALL sessions' per-session logs; NOT my consumer)
LOCK="data/.event_bus.lock"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "PRODUCER: ALIVE (PID $(cat "$LOCK")) -- shared feed OK"
else
  echo "PRODUCER: DOWN -- shared feed for ALL sessions down; needs event_bus.sh restart (USER/infra)."
fi

# 3. my LAYER-1 consumer-log freshness (informational; stale != dead but worth a glance)
LOG="data/events/exp_dev.log"
[ -f "$LOG" ] && echo "exp_dev.log: $(wc -l < "$LOG") lines | last event: $(tail -1 "$LOG" 2>/dev/null | cut -c1-8)"
echo "=== reminder: INBOX is the safety net; the Monitor is a best-effort notifier. Run THIS every cycle. ==="
