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
# Filter discipline 2026-06-20 (USER feedback: prior filter delivered everything to
# everyone via "starts with any other session prefix" -- token waste + 5x-redundant
# chat acks). Tightened to: deliver only if the note is GENUINELY addressed to me
# (session name appears anywhere in the filename) OR is a true _to_all_/_all_
# broadcast. Senders MUST address by name (cc_<session> or to_<session>) when they
# want a specific peer to see -- the filename-cap discipline allows shortening but
# not dropping addressing. Notes that don't match my filter are still discoverable
# via filesystem when needed, but don't wake my monitor.
filt() {
  grep -Eai "${SESS}|_to_all_|_all_" \
    | grep -viE "^${SESS}_"
}

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
