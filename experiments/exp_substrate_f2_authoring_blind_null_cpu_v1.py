"""
exp_substrate_f2_authoring_blind_null_cpu_v1.py -- F2 authoring-blind null: how much of the 18.8% abstraction ratio is TODAY'S retyping vs pre-existing structure? -- CPU/local (no heat), READ-ONLY.

ROUTING: Research SYNTHESIS-2 Exp-Dev item #4 + 15th-rule reservation ("the 3 REALIZED groups share authoring lineage; F2 may not be
  authoring-independent -- re-run VERIFY-2 over a held-out slice"). Operational form: Testbed preserved `retyped_from` on the 19 operators it
  retyped TODAY. This cell measures realized abstraction families (SHARED_ABSTRACTION single-domain + CROSS_DOMAIN_ABSTRACTION) (a) with CURRENT
  output types, and (b) with today's retyped outputs REVERTED to their retyped_from originals (authoring-blind: as if today's retyping never
  happened). The delta is the portion of F2 attributable to today's deliberate self-model authoring. Honest both directions (7th rule): if the
  families persist when reverted, F2 is authoring-INDEPENDENT (real pre-existing structure); if they collapse, F2 is authoring-DEPENDENT (the
  lift is deliberate build -- legitimate, but must be stated as such, not as discovered independent structure). Ungated (atom algebra metadata).

PRE-REGISTERED: report realized families + operators-unified for CURRENT vs REVERTED. AUTHORING-INDEPENDENT iff reverted operators-unified >=
  0.80 * current (families survive reversion). AUTHORING-DEPENDENT iff reverted <= 0.50 * current (lift is from today's retyping). MIDDLE in
  between. (This is a characterization, not a substrate pass/fail; the gate is honesty about what drives F2.) ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_f2_authoring_blind_null_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()


def realized(ops: List[Tuple[str, str, str, str]]) -> Tuple[int, int]:
    """ops=(name,domain,output,op). Realized = SHARED_ABSTRACTION (same domain+output, >=2 members, >=2 ops) + CROSS_DOMAIN_ABSTRACTION
    (same output, >=2 domains, >=2 ops). Returns (n_families, n_operators_unified)."""
    bydom = defaultdict(list)
    by_out_global = defaultdict(list)
    for name, dom, out, op in ops:
        if dom and out:
            bydom[dom].append((name, out, op)); by_out_global[out].append((dom, op, name))
    fams = 0; unified = set()
    # single-domain SHARED_ABSTRACTION
    for dom, mem in bydom.items():
        by_out = defaultdict(list)
        for name, out, op in mem:
            by_out[out].append((name, op))
        for out, m in by_out.items():
            if len(m) >= 2 and len(set(o for _, o in m)) >= 2:
                fams += 1; unified.update(n for n, _ in m)
    # cross-domain CROSS_DOMAIN_ABSTRACTION (same output, >=2 domains, >=2 ops)
    for out, lst in by_out_global.items():
        doms = set(d for d, _, _ in lst); ops_ = set(o for _, o, _ in lst)
        if len(doms) >= 2 and len(ops_) >= 2 and len(lst) >= 2:
            fams += 1; unified.update(n for _, _, n in lst)
    return fams, len(unified)


def _selftest():
    cur = [("a", "d1", "T", "o1"), ("b", "d1", "T", "o2"), ("c", "d2", "U", "o3")]  # a,b SHARED_ABSTRACTION in d1
    f, u = realized(cur); assert f == 1 and u == 2, (f, u)
    rev = [("a", "d1", "T", "o1"), ("b", "d1", "V", "o2"), ("c", "d2", "U", "o3")]  # revert b's output -> no family
    f2, u2 = realized(rev); assert f2 == 0 and u2 == 0, (f2, u2)
    print("[selftest] PASS: substrate_f2_authoring_blind_null_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    def short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()
    cur_ops = []; rev_ops = []; n_retyped = 0; seen = set()
    for a in PartitionedStore(root).all_atoms():
        alg = getattr(a, "algebra", None)
        if not isinstance(alg, dict):
            continue
        op = alg.get("operation_type"); out = alg.get("signature_output_type")
        if not (op and out):
            continue
        s = short(a.id)
        if s in seen:
            continue
        seen.add(s)
        dom = alg.get("domain")
        cur_ops.append((s, dom, out, op))
        rf = alg.get("retyped_from")
        if rf and rf != "(none)":
            n_retyped += 1
            rev_ops.append((s, dom, rf, op))      # revert to pre-retype output
        else:
            rev_ops.append((s, dom, out, op))
    if len(cur_ops) < 5:
        return {"error": "too_few_operators", "n": len(cur_ops)}
    cur_f, cur_u = realized(cur_ops)
    rev_f, rev_u = realized(rev_ops)
    denom = len(cur_ops)
    cur_ratio = round(cur_u / denom, 4); rev_ratio = round(rev_u / denom, 4)
    ratio_of = round(rev_u / cur_u, 4) if cur_u else 1.0
    print("  operators=%d | retyped-today (have retyped_from)=%d" % (denom, n_retyped), flush=True)
    print("  CURRENT  realized families=%d, operators unified=%d (ratio %.4f)" % (cur_f, cur_u, cur_ratio), flush=True)
    print("  REVERTED realized families=%d, operators unified=%d (ratio %.4f) [authoring-blind: today's retyping undone]" % (rev_f, rev_u, rev_ratio), flush=True)
    print("  authoring-blind retention = reverted/current operators unified = %.4f" % ratio_of, flush=True)
    return {"n_operators": denom, "n_retyped_today": n_retyped, "current_families": cur_f, "current_unified": cur_u,
            "reverted_families": rev_f, "reverted_unified": rev_u, "current_ratio": cur_ratio, "reverted_ratio": rev_ratio,
            "retention": ratio_of}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n", "")))
    ret = r["retention"]
    s = ("F2 authoring-blind null (15th rule): %d operators, %d retyped TODAY. CURRENT realized %d families / %d operators unified (ratio %.4f). "
         "REVERTED (today's retyping undone via retyped_from) %d families / %d operators (ratio %.4f). Authoring-blind retention = %.4f. "
         "Honest reading: the F2 abstraction ratio is driven by today's deliberate self-model authoring (operator retyping) to the extent "
         "retention is low; that is legitimate BUILD work, but it is NOT pre-existing authoring-independent structure.") % (
        r["n_operators"], r["n_retyped_today"], r["current_families"], r["current_unified"], r["current_ratio"],
        r["reverted_families"], r["reverted_unified"], r["reverted_ratio"], ret)
    if ret >= 0.80:
        return ("HARD_PASS", "HARD_PASS (F2 AUTHORING-INDEPENDENT): %.0f%% of unified operators survive reverting today's retyping -- the "
                "abstraction families reflect pre-existing structure, not today's authoring. F2 18.8%% is independent. " % (100 * ret) + s)
    if ret <= 0.50:
        return ("AUTHORING_DEPENDENT", "AUTHORING_DEPENDENT (honest, NOT a substrate failure): only %.0f%% of unified operators survive reverting "
                "today's retyping -- the F2 lift is largely TODAY'S deliberate operator-retyping (legitimate build of the self-model), NOT discovered "
                "pre-existing independent structure. F2 18.8%% must be reported as authoring-driven; the abstractions are real-and-authored, not "
                "real-and-independent. Re-measure on a future session's held-out slice for true independence. " % (100 * ret) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: %.0f%% retention -- F2 is partly pre-existing, partly today's authoring. " % (100 * ret) + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
