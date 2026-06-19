#!/usr/bin/env bash
# notes_monitor.sh -- robust notes-bus monitor (canonical v5, 2026-06-18).
#
# WHY v5: the mtime-window monitor (v4: `find -newermt "@$last"`) is fragile to
# clock/TIMEZONE changes and second-granularity boundary misses. v5 uses a
# FILENAME-SET DIFF instead -- it never reads the clock, so a TZ change / clock
# skew / future-dated mtime CANNOT break it. Each new note is reported exactly once.
#
# Usage:  bash tools/notes_monitor.sh <session>
#   <session> in: skunkworks | research | exp_dev | testbed | orchestrator
# Run it via the Monitor tool (persistent:true). Each stdout line is one event.
#
# Filter: a note is "for me" if its filename contains <session> OR to_all OR _all_,
# EXCLUDING my own outgoing notes (filename starting "<session>_").
set -u
SESS="${1:?usage: bash tools/notes_monitor.sh <session>}"
ROOT="/d/AI/hd-instrument"
cd "$ROOT" || { echo "MONITOR-ERROR: cannot cd $ROOT"; exit 1; }
LABEL="NOTE-FOR-$(printf '%s' "$SESS" | tr '[:lower:]' '[:upper:]'):"
filt() { grep -Eai "${SESS}|to_all|_all_" | grep -viE "^${SESS}_"; }

SEEN="$(mktemp)"; CUR="$(mktemp)"
trap 'rm -f "$SEEN" "$CUR"' EXIT

# Seed: treat all currently-existing matching notes as already-seen (no startup spam).
find notes -maxdepth 1 -name '*.md' -printf '%f\n' 2>/dev/null | filt | sort -u > "$SEEN"

while true; do
  sleep 20
  # List current matching notes; report any NOT already seen; then fold into SEEN.
  find notes -maxdepth 1 -name '*.md' -printf '%f\n' 2>/dev/null | filt | sort -u > "$CUR"
  comm -13 "$SEEN" "$CUR" | sed "s|^|${LABEL} |"
  sort -u "$SEEN" "$CUR" -o "$SEEN"
done
