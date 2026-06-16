#!/usr/bin/env bash
# TESTBED cycle-start SELF-CHECK (LAYER 2 heartbeat backstop; DECISION 161 canonical architecture).
# Run at the TOP of every work cycle / on every 10-15 min heartbeat (13th USER-LOCKED rule).
# Purpose: self-heal the monitor-consumer-death + tail-F reattach-gap failure modes. The INBOX
# (mtime-aware widenet over notes/) is AUTHORITATIVE -> catches notes addressed to me EVEN IF the
# harness Monitor (LAYER 1) died or dropped lines during a reconnect window. ASCII only.
cd /d/AI/hd-instrument 2>/dev/null || cd d:/AI/hd-instrument 2>/dev/null || exit 1
echo "=== TESTBED CYCLE CHECK ==="
WINDOW_MIN=20

# 1. AUTHORITATIVE inbound: notes addressed TO testbed (or broadcast _to_all_) modified in the
#    last WINDOW_MIN min, EXCLUDING my own outbound (testbed_to_*). Catches missed dispatches.
RECENT=$(find notes/ -maxdepth 1 -type f -mmin -"$WINDOW_MIN" \( -name '*testbed*' -o -name '*_to_all_*' \) ! -name 'testbed_to_*' ! -name 'testbed_phase_*' 2>/dev/null | sort)
N_RECENT=$(printf '%s\n' "$RECENT" | grep -c . )
echo "INBOX (to-me/broadcast, last ${WINDOW_MIN}min): $N_RECENT"
if [ "$N_RECENT" -gt 0 ]; then
  printf '%s\n' "$RECENT" | sed 's,^,  >> ,'
  echo "  >> ACTION: if you were NOT notified by the LAYER-1 monitor, it is DEAD or dropped a"
  echo "     reattach-window line -> RE-ARM Monitor (persistent, tail -n0 --retry -F data/events/testbed.log,"
  echo "     filter ROUTING|BROADCAST, author-out grep -v 'notes/testbed_'). Then READ+ACT the notes above."
fi

# 2. SHARED event-bus PRODUCER alive? (feeds ALL sessions' per-session logs; NOT my consumer)
LOCK="data/.event_bus.lock"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "PRODUCER: ALIVE (PID $(cat "$LOCK")) -- shared feed OK"
else
  echo "PRODUCER: DOWN -- shared feed for ALL sessions down; needs event_bus.sh restart (USER/infra)."
fi

# 3. my LAYER-1 consumer-log freshness (informational; stale != dead but worth a glance)
LOG="data/events/testbed.log"
[ -f "$LOG" ] && echo "testbed.log: $(wc -l < "$LOG") lines | last event: $(tail -1 "$LOG" 2>/dev/null | cut -c1-8)"

# 4. TESTBED-specific substrate-sanity tick (composes with TASK 3 standing duty).
#    Quick invariant check: atom + rel counts + axiom_term + module liveness.
echo "--- substrate sanity ---"
python -c "
import sys
from pathlib import Path
sys.path.insert(0, '.')
from backend.substrate_index.partition import PartitionedStore
ps = PartitionedStore(Path('data/substrate_index'))
atoms = len(ps.all_atoms())
rels = sum(1 for _ in ps.iter_all_relations())
print(f'atoms={atoms} rels={rels}')
forward = {}
for src, rel, tgt in ps.iter_all_relations():
    if rel.name in ('DEPENDS_ON','SPECIALIZES'):
        forward.setdefault(src,[]).append(tgt)
axioms=set()
for a in ps.all_atoms():
    if str(a.tier.name)!='TIER_1_FOUNDATIONAL' or str(a.corpus.name)!='MATH': continue
    role=(a.algebra or {}).get('role','')
    if (a.metadata or {}).get('is_axiom', False) or role in ('axiom_schema','axiom','type'):
        axioms.add(f'math::{a.id}')
def term(s,d=15):
    seen={s}; f=[s]
    for _ in range(d):
        n=[]
        for x in f:
            if x in axioms: return True
            for t in forward.get(x,[]):
                if t not in seen: seen.add(t); n.append(t)
        f=n
        if not f: break
    return any(x in axioms for x in seen)
ops=[a for a in ps.all_atoms() if str(a.corpus.name)=='MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE','TIER_3_ALGORITHM') and a.algebra and len(a.algebra)>=3 and 'oeis' not in str(a.id).lower() and not str(a.id).startswith('T3/wikidata_')]
t=sum(1 for op in ops if term(f'math::{op.id}'))
print(f'axiom_term={t}/{len(ops)}')
import importlib
mods=[('backend.substrate_index.hmm_decoder','viterbi_decode'),('hdlab.perceptron','StructuredPerceptron'),('backend.substrate_index.sequence_labeler','NERTagger'),('hdlab.bayesian_inference','EMMixture'),('backend.substrate_index.intent_classifier','IntentClassifier'),('backend.substrate_index.refuse_gated_retriever','RefuseGatedRetriever')]
ok=sum(1 for m,s in mods if hasattr(importlib.import_module(m),s))
print(f'modules={ok}/{len(mods)}')
" 2>&1
echo "=== reminder: INBOX is the safety net; the Monitor is a best-effort notifier. Run THIS every cycle. ==="
