#!/usr/bin/env bash
# DISABLED 2026-06-21 (USER popup-fix): early-exit. Canonical event delivery is
# the v5 notes_monitor (bash or Python port) per CLAUDE.md. This bus was the
# "backstop" but spawned ~10-14 console children/min (find + ssh + python every
# 30s under Claude Code's hidden-console parent = popup flash storm). Auto-start
# launcher event_bus_launch.cmd still fires at logon but this script now no-ops.
# To re-enable: delete this exit block + restart via the launcher.
echo "[event_bus] DISABLED (popup-fix 2026-06-21). Canonical: notes_monitor."
exit 0

# --- original body below (preserved for reference; unreachable after exit 0) ---
# Single-producer EVENT BUS for the 4-session architecture.
# ONE heavy scanner (this process) polls queues + notes/ ONCE per interval and ROUTES each event to the
# correct per-session log under data/events/<session>.log. Each session then runs a cheap consumer:
#     tail -n0 -F data/events/<session>.log
# instead of its own heavy find/grep/ssh loop. Collapses N heavy scanners -> 1 producer + N cheap tails.
#
# SINGLETON: refuses to start if another live producer holds the lock (prevents the duplicate-accumulation
# that caused the laptop to overheat). Stop with: rm data/.event_bus.lock && pkill -f event_bus.sh
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null || exit 1
LOCK="data/.event_bus.lock"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "[event_bus] already running (PID $(cat "$LOCK")); this instance exits (singleton)."; exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
mkdir -p data/events
EV="data/events"
SESSIONS="exp_dev research testbed orchestrator skunkworks"
for s in $SESSIONS; do : >> "$EV/$s.log"; done
mk="data/.event_bus_notes_marker"; [ -f "$mk" ] || touch -d '2 minutes ago' "$mk" 2>/dev/null
last_gpr="init"; last_gpp=99; idle_gp=0; last_rcr="init"; last_lcr="init"
ts() { date '+%H:%M:%S'; }
route() { echo "$(ts) $2" >> "$EV/$1.log"; }   # $1=session  $2=message

echo "[event_bus] producer started PID $$ -- routing to $EV/{${SESSIONS// /,}}.log"
while true; do
  # ---------- notes/ scanned ONCE; routed by recipient convention ----------
  newf=$(find notes -maxdepth 1 -name "*.md" -newer "$mk" 2>/dev/null)
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    f=$(basename "$p")
    case "$f" in exp_dev_to_*|research_to_*|testbed_to_*|orchestrator_to_*) author_out=1;; *) author_out=0;; esac
    case "$f" in *exp_dev*|exp_dev_handoff_*|strategy_request_to_exp_dev_*) [ "$f" != "${f#exp_dev_to_}" ] || route exp_dev "ROUTING: notes/$f -- READ+ACT";; esac
    case "$f" in *research*|strategy_request_to_research_*) [ "$f" != "${f#research_to_}" ] || route research "ROUTING: notes/$f";; esac
    case "$f" in *testbed*) [ "$f" != "${f#testbed_to_}" ] || route testbed "ROUTING: notes/$f";; esac
    case "$f" in *to_all*) for s in orchestrator exp_dev research testbed skunkworks; do route $s "BROADCAST: notes/$f"; done;; esac
    case "$f" in orchestrator_to_*|*_to_orchestrator_*) route orchestrator "ROUTING: notes/$f";; esac
    case "$f" in *skunkworks*|skunkworks_handoff_*|strategy_request_to_skunkworks_*) [ "$f" != "${f#skunkworks_to_}" ] || route skunkworks "ROUTING: notes/$f -- READ+ACT";; esac
    case "$f" in skunkworks_to_*) route research "ROUTING: notes/$f (from skunkworks)"; esac 2>/dev/null
  done <<< "$newf"
  touch "$mk" 2>/dev/null

  # ---------- GPU lane (overnight_queue) -- ONE ssh, route to exp_dev ----------
  gp=$(ssh -o ConnectTimeout=10 marsh@home "powershell -NoProfile -Command \"\$g=(Get-Content C:/dev/hd-instrument/data/overnight_queue/queue.json -Raw|ConvertFrom-Json).experiments; \$r=@(\$g|?{\$_.status -in 'running','claimed'}|%{\$_.name}); \$p=@(\$g|?{\$_.status -eq 'pending'}).Count; \$(if(\$r.Count){\$r[-1]}else{'idle'})+'|'+\$p\"" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$gp" ] && echo "$gp" | grep -q '|'; then
    gpr="${gp%%|*}"; gpp="${gp##*|}"
    if [ "$gpr" != "$last_gpr" ]; then
      [ "$last_gpr" != "init" ] && [ "$last_gpr" != "idle" ] && route exp_dev "EXP-DONE [GPU]: ${last_gpr} finished; now ${gpr} (pend=${gpp})"
      last_gpr="$gpr"
    fi
    if [ "$gpr" = "idle" ] && [ "$gpp" -eq 0 ] 2>/dev/null; then idle_gp=$((idle_gp+1)); [ $((idle_gp % 20)) -eq 0 ] && route exp_dev "IDLE [GPU]: ~$((idle_gp/2))min idle"; else idle_gp=0; fi
  fi

  # ---------- desktop CPU lane (remote_cpu_queue) -- reuse same ssh round next tick (kept light) ----------
  rc=$(ssh -o ConnectTimeout=10 marsh@home "powershell -NoProfile -Command \"\$g=(Get-Content C:/dev/hd-instrument/data/remote_cpu_queue/queue.json -Raw|ConvertFrom-Json).experiments; \$r=@(\$g|?{\$_.status -in 'running','claimed'}|%{\$_.name}); \$(if(\$r.Count){\$r[-1]}else{'idle'})\"" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$rc" ] && [ "$rc" != "$last_rcr" ]; then
    [ "$last_rcr" != "init" ] && [ "$last_rcr" != "idle" ] && route exp_dev "EXP-DONE [desktop-CPU]: ${last_rcr} finished; now ${rc}"
    last_rcr="$rc"
  fi

  # ---------- laptop CPU lane (local file) ----------
  lc=$(python -c "import json;j=json.load(open('data/local_cpu_queue/queue.json',encoding='utf-8'));e=j['experiments'];r=[x['name'] for x in e if x.get('status') in('running','claimed')];print(r[0] if r else 'idle')" 2>/dev/null)
  if [ -n "$lc" ] && [ "$lc" != "$last_lcr" ]; then
    [ "$last_lcr" != "init" ] && [ "$last_lcr" != "idle" ] && route exp_dev "EXP-DONE [laptop-CPU]: ${last_lcr} finished; now ${lc}"
    last_lcr="$lc"
  fi

  sleep 30
done 2>&1
