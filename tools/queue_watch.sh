#!/usr/bin/env bash
# EXP-DEV queue watcher: emits on experiment completion (running-name change) or pending<5, per lane. Deduped via state.
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null
st=/tmp/exp_dev_qwatch_state
: > "$st"
get() { grep -E "^$1=" "$st" 2>/dev/null | tail -1 | cut -d= -f2-; }
set_() { grep -vE "^$1=" "$st" 2>/dev/null > "$st.tmp"; echo "$1=$2" >> "$st.tmp"; mv "$st.tmp" "$st"; }
LPY="C:/dev/hd-instrument/.venv/Scripts/python.exe"   # (local python via system)
while true; do
  # --- laptop local CPU queue (local file, no ssh) ---
  lc=$(python -c "import json;j=json.load(open('data/local_cpu_queue/queue.json',encoding='utf-8'));e=j['experiments'];r=[x['name'] for x in e if x.get('status') in('running','claimed')];p=len([x for x in e if x.get('status')=='pending']);print((r[0] if r else 'idle')+'|'+str(p))" 2>/dev/null)
  lcr="${lc%%|*}"; lcp="${lc##*|}"
  if [ -n "$lc" ]; then
    if [ "$lcr" != "$(get lcr)" ]; then
      prev="$(get lcr)"; [ -n "$prev" ] && [ "$prev" != "idle" ] && echo "EXP-DONE [laptop-CPU]: $prev finished; now running ${lcr} (pend=${lcp})"
      set_ lcr "$lcr"
    fi
    if [ "$lcp" -lt 5 ] 2>/dev/null && [ "$(get lclow)" != "1" ]; then echo "REFILL [laptop-CPU]: pend=${lcp} (<5)"; set_ lclow 1; fi
    [ "$lcp" -ge 5 ] 2>/dev/null && set_ lclow 0
  fi
  # --- GPU lane on home (one ssh) ---
  gp=$(ssh -o ConnectTimeout=12 marsh@home "powershell -NoProfile -Command \"\$g=(Get-Content C:/dev/hd-instrument/data/overnight_queue/queue.json -Raw|ConvertFrom-Json).experiments; \$r=@(\$g|?{\$_.status -in 'running','claimed'}|%{\$_.name}); \$p=@(\$g|?{\$_.status -eq 'pending'}).Count; \$(if(\$r.Count){\$r[-1]}else{'idle'})+'|'+\$p\"" 2>/dev/null | tr -d '[:space:]')
  gpr="${gp%%|*}"; gpp="${gp##*|}"
  if [ -n "$gp" ] && [ -n "$gpp" ]; then
    if [ "$gpr" != "$(get gpr)" ]; then
      prev="$(get gpr)"; [ -n "$prev" ] && [ "$prev" != "idle" ] && echo "EXP-DONE [GPU]: $prev finished; now running ${gpr} (pend=${gpp})"
      set_ gpr "$gpr"
    fi
    if [ "$gpp" -lt 5 ] 2>/dev/null && [ "$(get gplow)" != "1" ]; then echo "REFILL [GPU]: pend=${gpp} (<5)"; set_ gplow 1; fi
    [ "$gpp" -ge 5 ] 2>/dev/null && set_ gplow 0
  fi
  sleep 90
done 2>&1
