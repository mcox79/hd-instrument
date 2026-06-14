"""
exp_substrate_f2_held_out_slice_independence_cpu_v1.py -- F2 future-held-out-slice independence test: does the abstraction ratio survive when restricted to atoms authored BEFORE this session? -- CPU/local (no heat), READ-ONLY.

ROUTING: Research GO (research_to_exp_dev_GO_build_F2_future_held_out_slice_test_...). 15th-rule independence: F2's 18.8% (SHARED) + cross-
  domain lift were authored THIS session (2026-06-13 ingest = 20267 atoms; pre-session = 1886). Test: compute realized abstraction families
  (SHARED_ABSTRACTION single-domain + CROSS_DOMAIN_ABSTRACTION) restricted to operators authored BEFORE a cutoff (creation-ts from
  data/substrate_index/*/audit.jsonl add_atom ts; earliest per atom).

  HONEST REFINEMENT (10th rule): the timestamp slice excludes this-session SUPERTYPE atoms but pre-session OPERATORS still carry THIS-session
  retyped signatures (only algebra was edited today, not atom creation). So I report TWO views per slice:
    (a) current-signatures  -- Research's literal spec (pre-session atoms, today's signatures): isolates the new-supertype-atom confound only
    (b) reverted-signatures -- pre-session atoms WITH today's retyping undone via retyped_from: the TRUE authoring-blind independence number
  Slices: 1-day (before 2026-06-13) and 2-day (before 2026-06-12, R3). Reports un-timestamped operator count (R1; don't pretend held-out).

PRE-REGISTERED (Research): report ACTUAL F2 on held-out slice + delta from current. INDEPENDENT iff held-out (reverted) F2 >= 0.15 (floor MET
  authoring-blind). AUTHORING-DEPENDENT iff held-out (reverted) F2 < 0.05 (below HARD-PASS bar -> F2 is this-session's authoring). MIDDLE in
  between. Honest both directions (7th rule). ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, glob, datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_f2_held_out_slice_independence_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CUT_1DAY = datetime.datetime(2026, 6, 13, 0, 0).timestamp()
CUT_2DAY = datetime.datetime(2026, 6, 12, 0, 0).timestamp()


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def realized(ops: List[Tuple[str, str, str, str]]) -> Tuple[int, int]:
    """ops=(name,domain,output,op). SHARED_ABSTRACTION (same domain+output,>=2 members,>=2 ops) + CROSS_DOMAIN_ABSTRACTION
    (same output,>=2 domains,>=2 ops). Returns (n_families, n_operators_unified)."""
    bydom = defaultdict(list); by_out = defaultdict(list)
    for name, dom, out, op in ops:
        if dom and out:
            bydom[dom].append((name, out, op)); by_out[out].append((dom, op, name))
    fams = 0; unified = set()
    for dom, mem in bydom.items():
        outg = defaultdict(list)
        for name, out, op in mem:
            outg[out].append((name, op))
        for out, m in outg.items():
            if len(m) >= 2 and len(set(o for _, o in m)) >= 2:
                fams += 1; unified.update(n for n, _ in m)
    for out, lst in by_out.items():
        if len(set(d for d, _, _ in lst)) >= 2 and len(set(o for _, o, _ in lst)) >= 2 and len(lst) >= 2:
            fams += 1; unified.update(n for _, _, n in lst)
    return fams, len(unified)


def _selftest():
    cur = [("a", "d1", "T", "o1"), ("b", "d1", "T", "o2")]
    f, u = realized(cur); assert f == 1 and u == 2
    assert CUT_2DAY < CUT_1DAY
    print("[selftest] PASS: substrate_f2_held_out_slice_independence_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def _load_creation_ts() -> Dict[str, float]:
    ts = {}
    for f in glob.glob(str(REPO / "data" / "substrate_index" / "*" / "audit.jsonl")):
        try:
            for ln in open(f, encoding="utf-8"):
                ln = ln.strip()
                if not ln: continue
                try: r = json.loads(ln)
                except Exception: continue
                if r.get("op") == "add_atom" and r.get("ts") and r.get("target"):
                    k = _short(r["target"]); t = float(r["ts"])
                    if k not in ts or t < ts[k]:
                        ts[k] = t
        except Exception:
            continue
    return ts


def _f2(ops):
    f, u = realized(ops)
    return {"families": f, "unified": u, "n_ops": len(ops), "ratio": round(u / len(ops), 4) if ops else 0.0}


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    ts = _load_creation_ts()
    seen = set(); ops_full = []
    for a in PartitionedStore(root).all_atoms():
        alg = getattr(a, "algebra", None)
        if not isinstance(alg, dict): continue
        op = alg.get("operation_type"); out = alg.get("signature_output_type")
        if not (op and out): continue
        s = _short(a.id)
        if s in seen: continue
        seen.add(s)
        rf = alg.get("retyped_from"); rf = rf if (rf and rf != "(none)") else None
        ops_full.append({"s": s, "dom": alg.get("domain"), "out": out, "op": op, "rf": rf, "ts": ts.get(s)})
    n_untimed = sum(1 for o in ops_full if o["ts"] is None)

    def to_tuples(rows, reverted):
        return [(o["s"], o["dom"], (o["rf"] if (reverted and o["rf"]) else o["out"]), o["op"]) for o in rows]

    full_cur = _f2(to_tuples(ops_full, False))
    out = {"n_operators_full": len(ops_full), "n_untimestamped": n_untimed, "full_current": full_cur, "slices": {}}
    for label, cut in (("before_2026-06-13", CUT_1DAY), ("before_2026-06-12", CUT_2DAY)):
        slice_rows = [o for o in ops_full if o["ts"] is not None and o["ts"] < cut]
        cur = _f2(to_tuples(slice_rows, False))
        rev = _f2(to_tuples(slice_rows, True))
        out["slices"][label] = {"n_slice_ops": len(slice_rows), "current": cur, "reverted": rev}
        print("  [%s] slice operators=%d | current F2: %d fams/%d unified ratio=%.4f | REVERTED(authoring-blind): %d fams/%d unified ratio=%.4f" % (
            label, len(slice_rows), cur["families"], cur["unified"], cur["ratio"], rev["families"], rev["unified"], rev["ratio"]), flush=True)
    print("  full (all ops, current): %d fams/%d unified ratio=%.4f | un-timestamped operators=%d" % (
        full_cur["families"], full_cur["unified"], full_cur["ratio"], n_untimed), flush=True)
    return out


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    sl = r["slices"].get("before_2026-06-13", {})
    rev = sl.get("reverted", {}).get("ratio", 0.0); cur = sl.get("current", {}).get("ratio", 0.0)
    full = r["full_current"]["ratio"]
    s = ("F2 held-out independence (15th rule). FULL (all ops, current sigs) ratio=%.4f. PRE-SESSION slice (before 2026-06-13, %d ops): "
         "current-sigs ratio=%.4f, REVERTED-sigs (authoring-blind) ratio=%.4f. 2-day slice: %s. Un-timestamped ops=%d. The REVERTED-on-slice "
         "number is the true authoring-independent F2 (pre-session atoms with pre-session signatures); current-on-slice still carries this-session "
         "retyping on pre-session operators.") % (
        full, sl.get("n_slice_ops", 0), cur, rev,
        str(r["slices"].get("before_2026-06-12", {}).get("reverted", {}).get("ratio")), r["n_untimestamped"])
    if rev >= 0.15:
        return ("HARD_PASS", "HARD_PASS (F2 AUTHORING-INDEPENDENT): held-out reverted F2=%.4f>=0.15 -- the abstraction families exist among "
                "pre-session atoms with pre-session signatures; F2 floor met independently of this session's authoring. " % rev + s)
    if rev < 0.05:
        return ("AUTHORING_DEPENDENT", "AUTHORING_DEPENDENT (honest, 7th+15th rule): held-out reverted F2=%.4f<0.05 -- below the HARD-PASS floor. "
                "The 50pct current F2 is THIS SESSION'S authoring (supertype atomization + operator retyping), NOT pre-existing independent "
                "structure. Legitimate build, but must be reported as authoring-driven; independence not established on the pre-session slice. " % rev + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: held-out reverted F2=%.4f in [0.05,0.15) -- partial independence; some abstraction predates this session. " % rev + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s cut1=%d cut2=%d" % (ANCHOR_NAME, RUN_MODE, int(CUT_1DAY), int(CUT_2DAY)), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
