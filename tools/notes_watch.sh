#!/usr/bin/env bash
# EXP-DEV notes watcher: timeout-guarded git fetch (a hung fetch must NOT stall the loop). Deduped vs seen_file.
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null
seen_file=/tmp/exp_dev_seen_notes.txt
while true; do
  timeout 20 git fetch origin main >/dev/null 2>&1 || true
  for note in $( (git ls-tree --name-only origin/main notes/ 2>/dev/null; git ls-tree --name-only HEAD notes/ 2>/dev/null) | sort -u | grep -E 'to_exp_dev|_AUTHORIZE|_batch' | grep -v 'exp_dev_to_'); do
    if ! grep -qFx "$note" "$seen_file" 2>/dev/null; then echo "NEW_NOTE: $note"; echo "$note" >> "$seen_file"; fi
  done
  sleep 30
done 2>&1
