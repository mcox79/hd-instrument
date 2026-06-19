"""
exp_tier5_self_discovery_rule_extraction_cpu_v1.py -- Tier 5: substrate self-DISCOVERY of a NOVEL methodology rule -- CPU.

ROUTING: Research Cycle 46/47 Tier-5 scope (research_to_exp_dev_testbed_VERIFICATION_COMPLETE_5TH_RULE_CONFIRMED_TIER_5_SCOPE). The
  substrate mines its OWN structured solution_history (atom.solution_history fields: capability -> solution-mechanism -> empirical_metric,
  with replacement chains) to PROPOSE a methodology rule NOT in its current 18 RULE atoms -- no human authorship; substrate-self-discovery.
  Two candidate-rule families: (A) RECURRING REPLACEMENT (old_mech -> new_mech transition that recurs across >=2 capabilities with
  consistent +lift, like count_nb->discriminative_perceptron); (B) UNIVERSAL LEVER (a mechanism that is current-best across >=3
  capabilities). Novelty = low keyword overlap with the 18 existing RULE atom names/descriptions. Cross-validation = lift-direction
  consistency across the supporting capabilities. Substrate-only, no LLM-judge. Tier 4 self-knowing -> Tier 5 self-discovery.
PRE-REGISTERED (Research): HARD-PASS substrate proposes >=1 NOVEL rule (not in 18) with > +0.05 avg lift across >=2 caps + consistent.
  MIDDLE proposes a rule with 0-0.05 lift OR re-derives an EXISTING rule (validates the miner). HARD-FAIL no candidate proposed
  (solution_history too sparse -> Tier 5 self-discovery is data/corpus-limited; honest -- supports richer-history ingestion).
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "tier5_self_discovery_rule_extraction_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
STOP = {"the", "to", "a", "of", "is", "rule", "via", "for", "and", "with", "when", "not", "substrate"}


def _toks(s):
    return set(w for w in "".join(c if c.isalnum() else " " for c in (s or "").lower()).split() if w not in STOP and len(w) > 2)


def _mech(qid):
    """short mechanism name from an atom qid: drop corpus:: + tier prefix."""
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.split("/")[-1].lower()


def _metric_val(m):
    if isinstance(m, dict): return m.get("value")
    return m if isinstance(m, (int, float)) else None


def _selftest():
    assert _mech("math::T3/discriminative_perceptron") == "discriminative_perceptron"
    assert _metric_val({"name": "acc", "value": 0.68}) == 0.68
    assert "perceptron" in _toks("count NB to discriminative perceptron")
    print("[selftest] PASS: tier5-self-discovery", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    try:
        ps = PartitionedStore(REPO / "data" / "substrate_index"); atoms = ps.all_atoms()
    except Exception as e:
        print("[load] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    # existing rule atoms (novelty baseline) -- collect tokens AND raw text (for mechanism-name containment)
    rule_tok = []; rule_text = []
    for a in atoms:
        corp = str(getattr(a.corpus, "value", a.corpus)).lower()
        if corp in ("meta", "methodology") and "rule" in (a.id or "").lower():
            txt = ((a.id or "") + " " + (getattr(a, "description", "") or "")).lower()
            rule_tok.append(_toks(txt)); rule_text.append(txt)
    # also treat the documented universal-lever finding as known (discriminative weighting is the universal lever -- memory)
    rule_text.append("discriminative perceptron weighting universal lever current best across capabilities")
    n_rules = len(rule_tok)

    def _mech_known(*mechs):
        """a candidate is NOT novel if ALL its key mechanisms already co-occur in some existing rule text."""
        for txt in rule_text:
            if all(m in txt for m in mechs): return True
        return False
    # mine solution_history: per-capability ordered solution chain + metrics
    transitions = defaultdict(lambda: {"caps": set(), "deltas": []})  # (old_mech,new_mech)->...
    lever = defaultdict(lambda: {"caps": set(), "metrics": []})       # mech -> caps it is current-best for
    n_sh = 0
    for a in atoms:
        sh = getattr(a, "solution_history", None)
        if not sh: continue
        n_sh += 1
        cap = a.id
        # order by adopted_date (None -> keep order)
        chain = sorted(sh, key=lambda e: (e.get("adopted_date") or ""))
        for i, e in enumerate(chain):
            mid = e.get("solution_atom_id"); mv = _metric_val(e.get("empirical_metric"))
            if not mid: continue
            mech = _mech(mid)
            if mv is not None and (e.get("status") == "current" or e.get("replaced_date") is None):
                lever[mech]["caps"].add(cap); lever[mech]["metrics"].append(mv)
            if i > 0:
                prev = chain[i - 1]; pmid = prev.get("solution_atom_id"); pmv = _metric_val(prev.get("empirical_metric"))
                if pmid and mv is not None and pmv is not None:
                    key = (_mech(pmid), mech)
                    transitions[key]["caps"].add(cap); transitions[key]["deltas"].append(mv - pmv)
    print("[mine] %d atoms with solution_history | %d transition-types | %d lever-mechs | %d existing rules" % (
        n_sh, len(transitions), len(lever), n_rules), flush=True)

    def is_novel(desc_tok):
        for rt in rule_tok:
            if rt and len(desc_tok & rt) / max(len(desc_tok | rt), 1) > 0.30: return False
        return True

    candidates = []
    # Pattern A: recurring replacement with consistent +lift. NOVEL iff the (old,new) mechanism pair isn't already in a rule.
    for (old, new), d in transitions.items():
        ncaps = len(d["caps"]); avg = sum(d["deltas"]) / len(d["deltas"]) if d["deltas"] else 0.0
        consistent = all(x >= 0 for x in d["deltas"]) if d["deltas"] else False
        novel = is_novel(_toks("replace %s with %s" % (old, new))) and not _mech_known(old, new)
        candidates.append({"type": "replacement", "name": "RULE_%s_to_%s" % (old, new), "n_caps": ncaps,
                           "avg_lift": round(avg, 4), "consistent": consistent, "novel": novel, "support": sorted(d["caps"])})
    # Pattern B: universal lever (mech current-best across >=3 caps). NOVEL iff the mechanism isn't already a known lever/rule.
    for mech, d in lever.items():
        ncaps = len(d["caps"])
        if ncaps >= 3:
            avgm = sum([m for m in d["metrics"] if m is not None and m <= 1.0] or d["metrics"]) / max(1, len([m for m in d["metrics"] if m is not None and m <= 1.0]) or len(d["metrics"]))
            novel = is_novel(_toks("%s universal lever" % mech)) and not _mech_known(mech)
            candidates.append({"type": "universal_lever", "name": "RULE_%s_universal_lever" % mech, "n_caps": ncaps,
                               "avg_metric": round(avgm, 4), "avg_lift": 0.0, "consistent": True, "novel": novel, "support": sorted(d["caps"])})
    # rank: novel + recurring + lift
    novel_recurring = [c for c in candidates if c["novel"] and c["n_caps"] >= 2 and
                       ((c["type"] == "replacement" and c["avg_lift"] > 0.05 and c["consistent"]) or
                        (c["type"] == "universal_lever" and c["n_caps"] >= 3))]
    novel_recurring.sort(key=lambda c: (c["n_caps"], c["avg_lift"]), reverse=True)
    re_derived = [c for c in candidates if (not c["novel"]) and c["n_caps"] >= 2]
    top = novel_recurring[0] if novel_recurring else None
    if top:
        print("  PROPOSED NOVEL rule: %s (%s, n_caps=%d, lift=%.4f, support=%s)" % (
            top["name"], top["type"], top["n_caps"], top["avg_lift"], top["support"][:4]), flush=True)
    else:
        print("  no NOVEL recurring rule; re-derived existing patterns: %d" % len(re_derived), flush=True)
        if re_derived: print("   e.g.: %s (n_caps=%d)" % (re_derived[0]["name"], re_derived[0]["n_caps"]), flush=True)
    return {"f1": round(top["avg_lift"], 4) if top else 0.0, "proposed_novel": bool(top), "top": top,
            "n_novel_recurring": len(novel_recurring), "n_re_derived": len(re_derived),
            "n_sh_atoms": n_sh, "n_transitions": len(transitions), "n_existing_rules": n_rules}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    top = r.get("top"); s = "sh_atoms=%d transitions=%d novel_recurring=%d re_derived=%d (existing_rules=%d)" % (
        r["n_sh_atoms"], r["n_transitions"], r["n_novel_recurring"], r["n_re_derived"], r["n_existing_rules"])
    if top and top["avg_lift"] > 0.05 and top["n_caps"] >= 2:
        return ("HARD_PASS", "HARD_PASS: substrate SELF-DISCOVERS a NOVEL methodology rule %s (%s, %d caps, lift %.4f) not in its %d existing rules -- Tier 5 self-discovery operational. %s" % (
            top["name"], top["type"], top["n_caps"], top["avg_lift"], r["n_existing_rules"], s))
    if r["n_re_derived"] >= 1 or (top and top["n_caps"] >= 2):
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate re-derives existing rule patterns OR proposes <0.05-lift rule (miner validated; solution_history too sparse for a strong NOVEL rule). " + s)
    return ("HARD_FAIL", "HARD_FAIL: no rule proposed -- solution_history too sparse for Tier 5 self-discovery (data-limited, NOT mechanism failure; supports richer-history ingestion). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
