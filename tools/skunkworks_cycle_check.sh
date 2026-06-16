#!/usr/bin/env bash
# SKUNKWORKS cycle-start SELF-CHECK (run at the TOP of every work cycle).
# Purpose: self-heal the monitor-consumer-death failure mode (2026-06-15: monitor auto-stopped
# on event volume; missed DECISION 100/101/102). The INBOX is AUTHORITATIVE (mtime-aware widenet
# over notes/) so it catches missed notes EVEN IF the harness Monitor consumer died.
# ASCII only.
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null || exit 1
echo "=== SKUNKWORKS CYCLE CHECK ==="

# 1. AUTHORITATIVE inbound: any missed/unread notes? (catches notes even if monitor is dead)
UNREAD=$(bash tools/skunkworks_inbox.sh 2>/dev/null | grep -oE "[0-9]+ unread" | grep -oE "^[0-9]+")
UNREAD=${UNREAD:-0}
echo "INBOX unread/updated: $UNREAD"
if [ "$UNREAD" -gt 0 ]; then
  echo "  >> ACTION: unread notes present. If you were NOT notified by the monitor, the harness"
  echo "     Monitor consumer is DEAD -> RE-ARM it (Monitor persistent, tail skunkworks.log, ROUTING filter)."
  echo "     Then: bash tools/skunkworks_inbox.sh  (read+process), then --seen."
fi

# 2. SHARED event-bus PRODUCER alive? (feeds ALL sessions' per-session logs; NOT my monitor)
LOCK="data/.event_bus.lock"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "PRODUCER: ALIVE (PID $(cat "$LOCK")) -- shared feed to all sessions OK"
else
  echo "PRODUCER: DOWN -- shared feed for ALL sessions is down; needs event_bus.sh restart (USER/infra)."
fi

# 3. my consumer-log freshness (informational)
LOG="data/events/skunkworks.log"
[ -f "$LOG" ] && echo "skunkworks.log: $(wc -l < "$LOG") lines | last event: $(tail -1 "$LOG" 2>/dev/null | cut -c1-8)"
echo "=== reminder: INBOX is the safety net; the Monitor is a best-effort notifier. Run THIS every cycle. ==="
