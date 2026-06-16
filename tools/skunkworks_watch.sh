#!/usr/bin/env bash
# SKUNKWORKS PUSH watcher: blocks until a NEW/UPDATED note addressed to skunkworks appears,
# then PRINTS it and EXITS. Run via run_in_background -> the harness fires a task-notification
# on exit, so notes PUSH to me instead of me having to poll. Re-arm after each fire.
#
# Light by design (cheap ls-glob + comm on a narrow pattern; NOT a find/grep/ssh over 3000 notes),
# so it does not reproduce the multi-session overheating that the single-producer bus was built to fix.
# Self-limits to ~25 min then exits as a heartbeat so a quiet period still re-prompts a re-arm.
set -u
cd "$(dirname "$0")/.." || exit 1
MAX=${1:-50}      # iterations
GAP=${2:-30}      # seconds between checks
i=0
while [ "$i" -lt "$MAX" ]; do
  out="$(bash tools/skunkworks_inbox.sh 2>/dev/null)"
  n="$(printf '%s\n' "$out" | sed -n 's/^=== SKUNKWORKS INBOX: \([0-9]\+\).*/\1/p' | head -1)"
  if [ -n "$n" ] && [ "$n" -gt 0 ]; then
    echo "PUSH: $n unread/updated skunkworks note(s) arrived -- process then re-arm the watcher."
    echo "$out"
    exit 0
  fi
  i=$((i+1))
  sleep "$GAP"
done
echo "HEARTBEAT: no new skunkworks notes in ~$((MAX*GAP/60)) min. Re-arm watcher + do lane work."
exit 0
