#!/usr/bin/env bash
# SKUNKWORKS durable inbox -- the AUTHORITATIVE unread/updated-note check. Run at the START of
# every cycle. Do NOT rely on the bus tail alone (it is lossy: logged only 1 of 3 notes 2026-06-13).
#
# MTIME-AWARE (per research_to_all_MONITOR_SETUP_MTIME_AWARE_2026-06-09): the ledger stores
# "filename|mtime" pairs, so a note that is APPENDED/EDITED after being marked seen re-surfaces
# as UPDATED. Filename-only tracking misses appends to daily-rolled / edited notes -- that bug
# already cost Research a verdict batch. We do not repeat it.
#
# Widenet: notes addressed to skunkworks + broadcasts (*_to_all_*) + handoffs-to-self.
#
# Usage:
#   bash tools/skunkworks_inbox.sh         # show NEW + UPDATED unread (does NOT mark seen)
#   bash tools/skunkworks_inbox.sh --seen  # show them, then record current filename|mtime
set -u
cd "$(dirname "$0")/.." || exit 1
LEDGER="data/skunkworks_seen_notes.txt"
touch "$LEDGER"

# One-time migration: convert any legacy plain-filename ledger lines to "filename|mtime".
if grep -qv '|' "$LEDGER" 2>/dev/null; then
  TMP_MIG="$(mktemp)"
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    case "$line" in
      *'|'*) echo "$line" ;;
      *) m=$(stat -c '%Y' "notes/$line" 2>/dev/null || echo 0); echo "$line|$m" ;;
    esac
  done < "$LEDGER" | sort -u > "$TMP_MIG"
  mv "$TMP_MIG" "$LEDGER"
fi

# Current candidate notes with mtime -> "filename|mtime"
: > /tmp/sk_inbox_cur.txt
# Match ANY note naming skunkworks as a recipient (primary OR secondary, e.g.
# research_to_testbed_skunkworks_*) + broadcasts. Mirrors the producer routing fix
# (DECISION 104b): use *skunkworks* (match anywhere) NOT *to_skunkworks* (which silently
# missed multi-recipient notes). Author-out guard: skip my OWN outbound skunkworks_to_*.
for f in notes/*skunkworks* notes/*_to_all_*; do
  [ -e "$f" ] || continue
  b=$(basename "$f")
  case "$b" in skunkworks_*) continue ;; esac   # author-out: ALL my own notes (skunkworks_to_/phase_B_/post_/TIER3_ ...); peer notes start with author name (research_/exp_dev_/testbed_), never skunkworks_
  m=$(stat -c '%Y' "$f" 2>/dev/null || echo 0)
  echo "$b|$m" >> /tmp/sk_inbox_cur.txt
done
sort -u /tmp/sk_inbox_cur.txt -o /tmp/sk_inbox_cur.txt
sort -u "$LEDGER" -o "$LEDGER"

# Unread = current (filename|mtime) not in ledger. Classify NEW vs UPDATED by filename presence.
comm -23 /tmp/sk_inbox_cur.txt "$LEDGER" > /tmp/sk_inbox_unread.txt
N=$(grep -c . /tmp/sk_inbox_unread.txt 2>/dev/null); N=${N:-0}
echo "=== SKUNKWORKS INBOX: $N unread/updated (ledger $(grep -c . "$LEDGER") entries) ==="
if [ "$N" -eq 0 ]; then echo "(caught up; nothing new or updated)"; exit 0; fi

: > /tmp/sk_inbox_files.txt
while IFS= read -r pair; do
  [ -z "$pair" ] && continue
  b="${pair%%|*}"
  if cut -d'|' -f1 "$LEDGER" | grep -qxF "$b"; then tag="UPDATED (appended/edited since last read)"; else tag="NEW"; fi
  echo
  echo "############################################################"
  echo "## $tag: $b"
  echo "############################################################"
  cat "notes/$b" 2>/dev/null
  echo "$b" >> /tmp/sk_inbox_files.txt
done < /tmp/sk_inbox_unread.txt

if [ "${1:-}" = "--seen" ]; then
  # Record current filename|mtime for the read files; drop their stale prior entries.
  grep -vxF -f <(sed 's/$/|/' /tmp/sk_inbox_files.txt | sed 's/|$//' | while read b; do grep "^$b|" "$LEDGER"; done) "$LEDGER" > /tmp/sk_ledger_new.txt 2>/dev/null || cp "$LEDGER" /tmp/sk_ledger_new.txt
  cat /tmp/sk_inbox_unread.txt >> /tmp/sk_ledger_new.txt
  sort -u /tmp/sk_ledger_new.txt -o /tmp/sk_ledger_new.txt
  mv /tmp/sk_ledger_new.txt "$LEDGER"
  echo; echo "=== marked $N seen (mtime-aware); ledger now $(grep -c . "$LEDGER") entries ==="
fi
