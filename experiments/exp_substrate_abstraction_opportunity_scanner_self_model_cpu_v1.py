"""
exp_substrate_abstraction_opportunity_scanner_self_model_cpu_v1.py -- SELF-MODEL ABSTRACTION-OPPORTUNITY SCANNER: substrate scans its OWN operator set to find (a) already-realized SHARED_ABSTRACTION families, (b) one-retype-away unification opportunities, (c) cross-domain shared-output links -- CPU/local (no heat), READ-ONLY.

ROUTING: Skunkworks direction reset item #4 ("substrate reasons over itself: prove operator equivalences/abstractions, find redundancy,
  surface gaps"). Instead of testing hand-named candidate groups one at a time, this scans the ENTIRE operator self-model and emits the full
  prioritized retype worklist for Testbed + the realized-abstraction map. This IS the substrate analyzing its own composition. Build-first
  (serves the authoring pipeline), measure-to-serve-the-build. Ungated: atom algebra signatures only (operation_type + signature_output_type +
  domain). No LLM, no relations, no codebook math.

  Operator = atom with both operation_type AND signature_output_type (the structured operator core). Per domain with >= 2 operators:
   - REALIZED SHARED_ABSTRACTION: an output-type shared by >= 2 operators with >= 2 distinct operation_types (the family already unifies).
   - ONE-RETYPE-AWAY: a domain with >= 2 operators that do NOT yet share a single output type -> authoring a shared supertype output would
     unify them (the precise Testbed worklist; consistent with V2's SHARED_ABSTRACTION = same domain + same output + distinct ops).
   - CROSS-DOMAIN shared-output: an output type carried by operators in >= 2 DIFFERENT domains (a cross-domain structural link; conservatively
     NOT a single-domain SHARED_ABSTRACTION, but a real self-insight, e.g. state_sequence across sequence_decoding + graph_search).

PRE-REGISTERED: HARD-PASS iff the scanner produces a NON-EMPTY actionable map (>= 1 realized family OR >= 1 one-retype-away opportunity) AND
  is internally consistent (every realized family is also same-domain). It is a DISCOVERY tool; the deliverable is the worklist + map, not a
  capability bar. MIDDLE_BAND iff it runs but finds 0 opportunities and 0 realized (self-model too thin). UNKNOWN if < 5 operators. ASCII-only.
  --self-test + --smoke + metrics.json.
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
ANCHOR_NAME = "substrate_abstraction_opportunity_scanner_self_model_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


SUPERTYPE_RELS = {"SPECIALIZES", "INSTANCE_OF", "MEMBER_OF"}     # member -> supertype edges (prover-traversable abstraction)


def _load_supertype_edges(root: Path) -> Dict[str, set]:
    """member_short -> set of supertype targets (short) via SPECIALIZES/INSTANCE_OF/MEMBER_OF. Race-tolerant."""
    out = defaultdict(set)
    for rp in root.rglob("relations.jsonl"):
        try:
            for ln in open(rp, encoding="utf-8"):
                ln = ln.strip()
                if not ln: continue
                try: r = json.loads(ln)
                except Exception: continue
                if (r.get("rel_type", "") or "").upper() in SUPERTYPE_RELS:
                    out[_short(r.get("src_id", ""))].add(_short(r.get("tgt_id", "")))
        except Exception:
            continue
    return out


def wiring_status(members: List[str], sup_edges: Dict[str, set]) -> Dict:
    """A realized family is WIRED iff >=2 members SPECIALIZE/INSTANCE_OF a COMMON supertype atom (prover can traverse member->supertype)."""
    cnt = defaultdict(int)
    for m in members:
        for t in sup_edges.get(m, ()):
            cnt[t] += 1
    common = [t for t, c in cnt.items() if c >= 2]
    return {"wired": bool(common), "supertype": (sorted(common)[0] if common else None),
            "n_members_linked": (max(cnt.values()) if cnt else 0)}


def analyze(ops: List[Tuple[str, str, str, str]]) -> Dict:
    """ops = list of (name, domain, output_type, operation_type). Returns realized families + one-retype-away + cross-domain."""
    bydom = defaultdict(list)
    for name, dom, out, op in ops:
        if dom:
            bydom[dom].append((name, out, op))
    realized = []; retype_away = []
    for dom, members in bydom.items():
        if len(members) < 2:
            continue
        by_out = defaultdict(list)
        for name, out, op in members:
            by_out[out].append((name, op))
        # realized: an output shared by >=2 members with >=2 distinct ops
        dom_realized = []
        for out, mem in by_out.items():
            if out and len(mem) >= 2 and len(set(op for _, op in mem)) >= 2:
                dom_realized.append({"domain": dom, "output_type": out, "members": [m for m, _ in mem], "n": len(mem)})
        if dom_realized:
            realized.extend(dom_realized)
        # one-retype-away: the domain has >=2 operators but they are NOT all in one realized output-group (multiple outputs present)
        covered = set(m for g in dom_realized for m in g["members"])
        leftover = [(name, out, op) for name, out, op in members if name not in covered]
        if len(leftover) >= 2 and len(set(out for _, out, _ in leftover)) >= 2:
            retype_away.append({"domain": dom, "n_operators": len(leftover),
                                "distinct_outputs": sorted(set(out for _, out, _ in leftover if out)),
                                "members": [n for n, _, _ in leftover]})
    # cross-domain shared output (a CROSS_DOMAIN_ABSTRACTION candidate: same output type, >=2 domains, with member operators)
    by_out_global = defaultdict(list)
    for name, dom, out, op in ops:
        if out and dom:
            by_out_global[out].append((name, dom))
    cross = []
    for out, mem in by_out_global.items():
        doms = sorted(set(d for _, d in mem))
        if len(doms) >= 2:
            cross.append({"output_type": out, "domains": doms, "n_members": len(mem),
                          "members": sorted(n for n, _ in mem)})
    return {"realized": realized, "retype_away": retype_away, "cross_domain": cross}


def _selftest():
    ops = [
        ("forward", "hmm", "state_distribution", "alpha"), ("backward", "hmm", "state_distribution", "beta"),  # realized
        ("bellman", "rl", "value_function", "vf"), ("mdp", "rl", "decision_problem", "dp"),                    # retype-away (2 outputs)
        ("astar", "graph", "state_sequence", "a"), ("viterbi", "seqdec", "state_sequence", "v"),               # cross-domain shared output
    ]
    r = analyze(ops)
    assert any(g["domain"] == "hmm" for g in r["realized"]), r["realized"]
    assert any(g["domain"] == "rl" for g in r["retype_away"]), r["retype_away"]
    assert any(c["output_type"] == "state_sequence" for c in r["cross_domain"]), r["cross_domain"]
    # wiring: 2 members SPECIALIZE a common supertype -> WIRED; none -> DETECTED-ONLY
    assert wiring_status(["a", "b"], {"a": {"sup"}, "b": {"sup"}})["wired"] is True
    assert wiring_status(["a", "b"], {"a": {"x"}, "b": {"y"}})["wired"] is False
    print("[selftest] PASS: substrate_abstraction_opportunity_scanner_self_model_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def _load_operators() -> List[Tuple[str, str, str, str]]:
    from backend.substrate_index.partition import PartitionedStore
    seen = set(); ops = []
    for a in PartitionedStore(REPO / "data" / "substrate_index").all_atoms():
        alg = getattr(a, "algebra", None)
        if not isinstance(alg, dict):
            continue
        op = alg.get("operation_type"); out = alg.get("signature_output_type")
        if not (op and out):
            continue
        s = _short(a.id)
        if s in seen:
            continue
        seen.add(s); ops.append((s, alg.get("domain"), out, op))
    return ops


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    ops = None
    for _ in range(5):
        try:
            ops = _load_operators()
            if len(ops) >= 5:
                break
        except Exception:
            ops = None; time.sleep(8)
    if not ops or len(ops) < 5:
        return {"error": "too_few_operators", "n": 0 if not ops else len(ops)}
    a = analyze(ops)
    sup_edges = _load_supertype_edges(root)
    for g in a["realized"]:
        g["wiring"] = wiring_status(g["members"], sup_edges)   # WIRED (prover-traversable) vs DETECTED-ONLY (step-#3 gap)
    n_realized = len(a["realized"]); n_retype = len(a["retype_away"]); n_cross = len(a["cross_domain"])
    realized_ops = sum(g["n"] for g in a["realized"])
    n_wired = sum(1 for g in a["realized"] if g["wiring"]["wired"])
    print("  operator self-model: %d operators (op_type+output)" % len(ops), flush=True)
    print("  REALIZED SHARED_ABSTRACTION families: %d (covering %d operators) | WIRED to a supertype (prover-traversable)=%d, DETECTED-ONLY (step-#3 gap)=%d" % (
        n_realized, realized_ops, n_wired, n_realized - n_wired), flush=True)
    for g in sorted(a["realized"], key=lambda x: -x["n"]):
        w = g["wiring"]; tag = ("WIRED->%s" % w["supertype"]) if w["wired"] else "DETECTED-ONLY (author supertype+SPECIALIZES)"
        print("    [realized] %-26s out=%-20s n=%d [%s] %s" % (g["domain"], g["output_type"], g["n"], tag, g["members"]), flush=True)
    print("  ONE-RETYPE-AWAY opportunities (Testbed worklist): %d" % n_retype, flush=True)
    for g in sorted(a["retype_away"], key=lambda x: -x["n_operators"]):
        print("    [retype]   %-26s n=%d outputs=%s -> author shared supertype to unify %s" % (
            g["domain"], g["n_operators"], g["distinct_outputs"][:4], g["members"]), flush=True)
    print("  CROSS-DOMAIN shared-output links: %d" % n_cross, flush=True)
    for c in sorted(a["cross_domain"], key=lambda x: (-len(x["domains"]), -x["n_members"])):
        print("    [cross]    out=%-22s %ddom x %dops domains=%s members=%s" % (
            c["output_type"], len(c["domains"]), c["n_members"], c["domains"], c["members"]), flush=True)
    bf = root / "bench_reports"
    try:
        bf.mkdir(parents=True, exist_ok=True)
        (bf / "abstraction_opportunity_self_model.json").write_text(json.dumps(
            {"n_operators": len(ops), **a, "n_realized": n_realized, "n_retype_away": n_retype, "n_cross_domain": n_cross}, indent=2), encoding="utf-8")
    except Exception:
        pass
    return {"n_operators": len(ops), "n_realized": n_realized, "realized_ops": realized_ops, "n_wired": n_wired,
            "n_retype_away": n_retype, "n_cross_domain": n_cross,
            "realized": a["realized"][:20], "retype_away": a["retype_away"][:20], "cross_domain": a["cross_domain"][:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n", "")))
    nr = r["n_realized"]; rt = r["n_retype_away"]; cd = r["n_cross_domain"]; nw = r.get("n_wired", 0)
    s = ("self-model scan: %d operators; %d REALIZED SHARED_ABSTRACTION families (%d WIRED to an authored supertype = prover-traversable, "
         "%d DETECTED-ONLY = step-#3 SPECIALIZES-wiring gap); %d ONE-RETYPE-AWAY domains "
         "(the precise Testbed retype worklist -- author a shared supertype output to unify each); %d CROSS-DOMAIN shared-output links "
         "(same output across domains -- conservative NOT-a-single-domain-abstraction, but real self-insight). This is the substrate scanning "
         "its OWN operator composition (lane #4, build-first).") % (r["n_operators"], nr, nw, nr - nw, rt, cd)
    if nr >= 1 or rt >= 1:
        return ("HARD_PASS", "HARD_PASS (self-model abstraction map produced; substrate reasons over its own composition): %d realized families "
                "(%d WIRED/prover-traversable, %d detected-only) + %d one-retype-away opportunities + %d cross-domain links. The retype-away list "
                "is the prioritized authoring worklist; detected-only families need SPECIALIZES wiring (step #3) to become prover-traversable. " % (nr, nw, nr - nw, rt, cd) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: scanner ran but found 0 realized families and 0 opportunities -- operator self-model too thin or fully "
            "distinct. " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
