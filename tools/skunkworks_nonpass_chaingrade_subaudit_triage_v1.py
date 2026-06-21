"""Skunkworks 2026-06-21 -- NON-PASS CHAIN-GRADE SUB-AUDIT triage (read-only).
The 147 non-PASS chain-grade atoms (MIDDLE_BAND / HARD_FAIL / custom-verdict) are the headline-honesty population:
each must be a GENUINE chain-grade result (a rigorous, reproducible, CAN-fail measurement -- a proven-bound or honest
middle/negative that meets the bar) vs UNDER-classified (should reframe-MM / demote) -- or, symmetrically, under-recorded.
This triage does NOT rule; it surfaces, per atom, the reproducibility signals a per-atom ruling needs, and buckets:
  CLEAN-KEEP  : cell metrics present + multi-seed + per_unit rows + a discriminating/cliff signal -> genuine chain-grade
                measurement; keep as proven-bound (deep-rule only if spot-check disagrees).
  SUSPECT     : missing >=1 of {local metrics, multi-seed, per_unit, can-fail/cliff signal} OR run_mode=smoke
                -> needs deep per_unit review (candidate reframe/demote); listed explicitly for drilling.
  CHAIN-BROKEN: metrics_path missing/unreadable, OR the metrics anchor_name/exp-name disagrees with the atom id
                (the t3_phaseA2 broken-cert-chain class -- metrics point to a DIFFERENT experiment).
Filter by --band (MIDDLE_BAND default / HARD_FAIL / custom / all). Read-ONLY. ASCII. Exit 0.
"""
from __future__ import annotations
import argparse, ast, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

CLIFF_HINTS = ("cliff","onset","boundary","m_crit","k_max","alpha_c","degrad","drop","knee","forget","threshold","stress","cv")


def kn(a): return a.kind.value if hasattr(a.kind,"value") else str(a.kind)
def pq(a): return (a.metadata or {}).get("provenance_quality")


def band(a):
    v = str((a.metadata or {}).get("verdict","")).upper()
    if v.startswith(("HARD_PASS","PASS")) or "CHAIN_GRADE" in v: return "PASS"
    if "MIDDLE" in v: return "MIDDLE_BAND"
    if "FAIL" in v: return "HARD_FAIL"
    return "custom"


def _load_metrics(mp):
    if not mp or not isinstance(mp, str): return None
    p = Path(mp)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _has_per_unit(d):
    for k in ("per_unit","per_seed","detail","rows","by_seed"):
        v = d.get(k)
        if isinstance(v,(list,dict)) and len(v) > 0: return True
    return False


def _n_seeds(d, md):
    for src in (d, md):
        for k in ("n_seeds","num_seeds","seeds"):
            v = src.get(k) if isinstance(src,dict) else None
            if isinstance(v,int) and v>0: return v
            if isinstance(v,(list,tuple)) and len(v)>0: return len(v)
    return None


def _cliff_signal(d, md):
    blob = " ".join(str(x).lower() for x in [
        d.get("verdict_msg",""), d.get("metrics_source",""), md.get("honest_scope",""),
        md.get("finding",""), " ".join(map(str,(d.get("summary") or {}).keys())) if isinstance(d.get("summary"),dict) else "",
        " ".join(map(str,d.keys())), str(md.get("key_metrics",""))])
    return any(h in blob for h in CLIFF_HINTS)


def _chain_ok(aid, d):
    # the metrics anchor/exp-name should relate to the atom id stem (broken-cert-chain guard, t3_phaseA2 class)
    stem = aid.split("/")[-1].lower().replace("exp_","").replace("_cpu_v1","").replace("_v1","")
    anchor = str(d.get("anchor_name") or d.get("exp_name") or d.get("name") or "").lower()
    if not anchor: return None  # no anchor field to check -> unknown (not a positive break)
    toks = [t for t in re.split(r"[_\-]", stem) if len(t) >= 4]
    if not toks: return None
    hit = sum(1 for t in toks if t in anchor)
    return hit >= 1  # at least one substantive token of the id appears in the metrics anchor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", default="MIDDLE_BAND", choices=["MIDDLE_BAND","HARD_FAIL","custom","all"])
    ap.add_argument("--show", type=int, default=80)
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    cg = [a for a in ps.all_atoms() if pq(a)=="CERT_CHAIN_GRADE" and kn(a)=="experiment_record"]
    sel = [a for a in cg if (args.band=="all" and band(a)!="PASS") or band(a)==args.band]

    clean, suspect, broken = [], [], []
    for a in sel:
        md = a.metadata or {}; aid = str(a.id); mp = md.get("metrics_path")
        d = _load_metrics(mp)
        if d is None:
            broken.append((aid, "metrics_missing", mp)); continue
        chain = _chain_ok(aid, d)
        if chain is False:
            broken.append((aid, "anchor_mismatch:%s" % str(d.get("anchor_name") or d.get("exp_name"))[:30], mp)); continue
        ns = _n_seeds(d, md); per = _has_per_unit(d); cliff = _cliff_signal(d, md)
        smoke = str(md.get("run_mode","")).lower()=="smoke" or str(d.get("run_mode","")).lower()=="smoke"
        reasons = []
        if smoke: reasons.append("smoke")
        if not (isinstance(ns,int) and ns>=2): reasons.append("seeds<2(%s)"%ns)
        if not per: reasons.append("no_per_unit")
        if not cliff: reasons.append("no_cliff_signal")
        if reasons:
            suspect.append((aid, ",".join(reasons)))
        else:
            clean.append((aid, "seeds=%s per_unit cliff" % ns))

    print("="*84)
    print("NON-PASS CHAIN-GRADE SUB-AUDIT TRIAGE -- band=%s -- %d atoms" % (args.band, len(sel)))
    print("-"*84)
    print("  CLEAN-KEEP  : %d  (multi-seed + per_unit + cliff/can-fail signal -> genuine chain-grade measurement)" % len(clean))
    print("  SUSPECT     : %d  (missing a reproducibility signal -> deep per_unit review)" % len(suspect))
    print("  CHAIN-BROKEN: %d  (metrics missing OR anchor disagrees with atom id -> the t3_phaseA2 class)" % len(broken))
    print("-"*84)
    print("SUSPECT (deep-review queue):")
    for aid, why in suspect[:args.show]:
        print("  %-58s %s" % (aid[:58], why))
    if len(suspect) > args.show: print("  ... +%d more" % (len(suspect)-args.show))
    print("-"*84)
    print("CHAIN-BROKEN (priority -- candidate broken-cert-chain):")
    for aid, why, mp in broken[:args.show]:
        print("  %-50s %s" % (aid[:50], why))
    if not broken: print("  (none)")
    print("="*84)
    print("Read-only triage. CLEAN-KEEP = spot-check only; SUSPECT = deep per_unit ruling; CHAIN-BROKEN = priority verify-referent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
