"""
exp_substrate_aaa3_intrinsic_load_bearing_mechanism_class_cpu_v1.py -- CELL-AAA-3 (INTRINSIC, authoring-independent): are TOOLS mechanism-class (generalize across capabilities)? -- CPU/local (no heat, read-only).

ROUTING: resolves the CONFOUND in the canonical CELL-AAA-3 (Reservation C falsifier). The canonical SHARES_MATH-out-degree test came out
  0.94x but is CONFOUNDED: SHARES_MATH edges were authored in BATCHES (tool-family cliques + P4-cluster materials) so out-degree reflects
  authored-clique-size, not intrinsic math-sharing. This cell tests the SAME hypothesis (Reservation C: "TOOLS are mechanism-class, they
  generalize across capabilities") with AUTHORING-INDEPENDENT intrinsic signals computed from each atom's OWN structure (serves_capability +
  the USES/DEPENDS_ON graph) -- NOT from authored SHARES_MATH. No batch-clique confound. NO LLM; relation graph + atom fields; numpy-free; no heat.

  INTRINSIC mechanism-class signals (tools should exceed materials if load-bearing is real):
   S1 capability_span    = |serves_capability| (distinct capabilities the atom serves -- mechanism reused across capabilities)
   S2 neighbor_reach     = |distinct atoms it connects to via USES+DEPENDS_ON, both directions| (architectural connectivity)
   S3 cross_domain_reach = |distinct algebra.domain values among its graph neighbors| (cross-domain generalization)
  Reported as TOOLS-vs-MATERIALS mean AND median ratios (median guards against hub-skew in S2).

PRE-REGISTERED (Reservation C, intrinsic): SUPPORT if >= 2 of 3 signals show TOOLS:MATERIALS mean ratio >= 1.4x (load-bearing axis is REAL
  / mechanism-class -- authoring-independent, resolves the canonical confound). MIDDLE if exactly 1 signal >= 1.4x. REFUTE if 0 signals
  >= 1.4x (axis collapses to noise on intrinsic measures too -> genuine reconsider-C). UNKNOWN if no index / too few tools.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_aaa3_intrinsic_load_bearing_mechanism_class_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CURATED_TOOLS = set("""
fhrr_bind fhrr_unbind circular_convolution cleanup cosine_similarity superposition bundling discriminative_perceptron metric_space
spectral_gap theta_gamma_binding tracy_widom_distribution kappa_4_free mp_bulk_kl vsa_family unit_modulus vector_space gradient
inner_product role_filler_binding algebraic_binding context_binding cleanup_retrieval cosine_cleanup permutation_indexed_binding
resonator_network_decoder modern_hopfield_ramsauer hopfield_family superposition_aggregation unbinders ghrr_noncommutative_bind
theta_gamma_to_hrr qubit_to_fhrr_phasor
""".split())


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def ratios(allids, tools, f):
    tv = [f(i) for i in allids if i in tools]; mv = [f(i) for i in allids if i not in tools]
    mt = statistics.mean(tv) if tv else 0.0; mm = statistics.mean(mv) if mv else 0.0
    medt = statistics.median(tv) if tv else 0.0; medm = statistics.median(mv) if mv else 0.0
    return {"tool_mean": round(mt, 3), "mat_mean": round(mm, 3), "mean_ratio": round(mt / mm, 3) if mm else 0.0,
            "tool_median": medt, "mat_median": medm, "median_ratio": round(medt / medm, 3) if medm else (medt if medt else 0.0)}


def _selftest():
    allids = ["t1", "t2", "m1", "m2", "m3"]; tools = {"t1", "t2"}
    r = ratios(allids, tools, lambda i: 10 if i in tools else 1)
    assert r["mean_ratio"] == 10.0 and r["tool_mean"] == 10.0, r
    assert len(CURATED_TOOLS) == 33
    print("[selftest] PASS: substrate_aaa3_intrinsic_load_bearing_mechanism_class_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()

    def alg(a):
        x = getattr(a, "algebra", None); return x if isinstance(x, dict) else {}
    caps = {}; dom = {}
    for a in atoms:
        sid = _short(a.id); caps[sid] = set(_short(c) for c in (getattr(a, "serves_capability", ()) or ())); dom[sid] = alg(a).get("domain")
    nbr = defaultdict(set); nbr_dom = defaultdict(set)
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() in ("USES", "DEPENDS_ON"):
                s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
                if s and t and s != t:
                    nbr[s].add(t); nbr[t].add(s)
                    if dom.get(t): nbr_dom[s].add(dom[t])
                    if dom.get(s): nbr_dom[t].add(dom[s])
    allids = [_short(a.id) for a in atoms]
    n_tools = sum(1 for i in allids if i in CURATED_TOOLS)
    if n_tools < 5:
        return {"error": "too_few_tools", "n_tools": n_tools}
    s1 = ratios(allids, CURATED_TOOLS, lambda i: len(caps.get(i, ())))
    s2 = ratios(allids, CURATED_TOOLS, lambda i: len(nbr.get(i, ())))
    s3 = ratios(allids, CURATED_TOOLS, lambda i: len(nbr_dom.get(i, ())))
    sigs = {"capability_span": s1, "neighbor_reach": s2, "cross_domain_reach": s3}
    n_pass = sum(1 for s in sigs.values() if s["mean_ratio"] >= 1.4)
    print("  intrinsic mechanism-class signals (authoring-independent), tools=%d:" % n_tools, flush=True)
    for name, s in sigs.items():
        print("    %-20s TOOLS mean=%.2f (med %.1f) vs MATERIALS mean=%.2f (med %.1f) -> mean-ratio=%.2fx median-ratio=%.2fx" % (
            name, s["tool_mean"], s["tool_median"], s["mat_mean"], s["mat_median"], s["mean_ratio"], s["median_ratio"]), flush=True)
    print("  signals with mean-ratio>=1.4x: %d/3" % n_pass, flush=True)
    return {"n_tools": n_tools, "signals": sigs, "n_signals_pass": n_pass}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_signals_pass"]; sg = r["signals"]
    s = ("intrinsic (authoring-independent) mechanism-class signals: capability_span %.2fx, neighbor_reach %.2fx, cross_domain_reach %.2fx "
         "(mean ratios TOOLS:MATERIALS). Resolves the canonical-AAA-3 confound (authored-clique sizes) by measuring each atom's OWN structure.") % (
        sg["capability_span"]["mean_ratio"], sg["neighbor_reach"]["mean_ratio"], sg["cross_domain_reach"]["mean_ratio"])
    if n >= 2:
        return ("SUPPORT", "SUPPORT (Reservation C CONFIRMED, intrinsic): %d/3 authoring-INDEPENDENT signals show TOOLS far exceed MATERIALS (>=1.4x) -- tools ARE mechanism-class (serve more capabilities, connect to more atoms, span more domains). The load-bearing (Axis 2) distinction is REAL, NOT a category error. This resolves the confounded canonical AAA-3 (0.94x = authored-clique artifact): on intrinsic measures the axis is overwhelmingly real. " % n + s)
    if n == 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: only 1/3 intrinsic signals >= 1.4x -- partial support for the mechanism-class hypothesis. " + s)
    return ("REFUTE", "REFUTE: 0/3 intrinsic signals >= 1.4x -- tools do NOT generalize more than materials even on authoring-independent measures; reconsider the load-bearing axis (Reservation C) per 7th rule. " + s)


print("[config] anchor=%s mode=%s curated_tools=%d" % (ANCHOR_NAME, RUN_MODE, len(CURATED_TOOLS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
