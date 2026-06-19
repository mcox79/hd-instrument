#!/usr/bin/env bash
# EXP-DEV queue watcher v2: pending-DROP trigger (robust to fast cells) + EXP-DONE on running change. Laptop checked first (fast); GPU ssh resilient.
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null
last_lcr="init"; last_lcp=99; last_gpr="init"; last_gpp=99
idle_lc=0; idle_gp=0   # consecutive idle polls per lane (30s each -> 10 polls = 5 min)
while true; do
  # --- laptop local CPU queue (local file, fast) ---
  lc=$(python -c "import json;j=json.load(open('data/local_cpu_queue/queue.json',encoding='utf-8'));e=j['experiments'];r=[x['name'] for x in e if x.get('status') in('running','claimed')];p=len([x for x in e if x.get('status')=='pending']);print((r[0] if r else 'idle')+'|'+str(p))" 2>/dev/null)
  if [ -n "$lc" ]; then
    lcr="${lc%%|*}"; lcp="${lc##*|}"
    if [ "$lcr" != "$last_lcr" ]; then
      [ "$last_lcr" != "init" ] && [ "$last_lcr" != "idle" ] && echo "EXP-DONE [laptop-CPU]: ${last_lcr} finished; now ${lcr} (pend=${lcp})"
      last_lcr="$lcr"
    fi
    if [ "$lcp" -lt 5 ] 2>/dev/null && [ "$lcp" -lt "$last_lcp" ] 2>/dev/null; then echo "REFILL [laptop-CPU]: pend=${lcp} (<5, drained)"; fi
    last_lcp="$lcp"
    if [ "$lcr" = "idle" ] && [ "$lcp" -eq 0 ] 2>/dev/null; then idle_lc=$((idle_lc+1)); if [ $((idle_lc % 10)) -eq 0 ]; then echo "IDLE [laptop-CPU]: nothing running for ~$((idle_lc/2))min -- queue/build authorized work"; fi; else idle_lc=0; fi
  fi
  # --- GPU lane on home (resilient ssh; skip cleanly on failure) ---
  gp=$(ssh -o ConnectTimeout=10 marsh@home "powershell -NoProfile -Command \"\$g=(Get-Content C:/dev/hd-instrument/data/overnight_queue/queue.json -Raw|ConvertFrom-Json).experiments; \$r=@(\$g|?{\$_.status -in 'running','claimed'}|%{\$_.name}); \$p=@(\$g|?{\$_.status -eq 'pending'}).Count; \$(if(\$r.Count){\$r[-1]}else{'idle'})+'|'+\$p\"" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$gp" ] && echo "$gp" | grep -q '|'; then
    gpr="${gp%%|*}"; gpp="${gp##*|}"
    if [ "$gpr" != "$last_gpr" ]; then
      [ "$last_gpr" != "init" ] && [ "$last_gpr" != "idle" ] && echo "EXP-DONE [GPU]: ${last_gpr} finished; now ${gpr} (pend=${gpp})"
      last_gpr="$gpr"
    fi
    if [ "$gpp" -lt 5 ] 2>/dev/null && [ "$gpp" -lt "$last_gpp" ] 2>/dev/null; then echo "REFILL [GPU]: pend=${gpp} (<5, drained)"; fi
    last_gpp="$gpp"
    if [ "$gpr" = "idle" ] && [ "$gpp" -eq 0 ] 2>/dev/null; then idle_gp=$((idle_gp+1)); if [ $((idle_gp % 10)) -eq 0 ]; then echo "IDLE [GPU]: nothing running for ~$((idle_gp/2))min -- queue/build authorized work"; fi; else idle_gp=0; fi
  fi
  # --- incoming routing notes RELEVANT to exp_dev so handoffs + cross-notes are never missed (cheap: only grep files newer than last poll) ---
  mk="data/.queue_watch_notes_marker"
  [ -f "$mk" ] || touch -d '2 minutes ago' "$mk" 2>/dev/null
  newf=$(find notes -maxdepth 1 -name "*.md" -newer "$mk" 2>/dev/null)
  while IFS= read -r path; do
    [ -z "$path" ] && continue
    grep -qilE "exp.?dev" -- "$path" 2>/dev/null || continue
    f=$(basename "$path")
    if echo "$f" | grep -qiE "to_exp_dev|exp_dev_handoff|strategy_request_to_exp_dev"; then
      echo "ROUTING [exp_dev]: NEW handoff -- notes/$f -- READ + ACT before any idle/queue work"
    elif echo "$f" | grep -qiE "^exp_dev_to_|^exp_dev_handoff_from_exp"; then
      : # self-authored outgoing note -- suppress (not incoming work)
    else
      echo "ROUTING [exp_dev-relevant]: NEW note mentions Exp-Dev -- notes/$f -- review for relevance"
    fi
  done <<< "$newf"
  touch "$mk" 2>/dev/null   # advance marker to now (simple + robust; sub-second race is inconsequential for routing notes)
  sleep 30
done 2>&1
