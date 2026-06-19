"""
exp_substrate_aaa3_definitive_uniform_criterion_permutation_null_cpu_v1.py -- CELL-AAA-3-definitive: load-bearing axis (Reservation C) with a UNIFORM criterion + permutation null -- CPU/local (no heat, read-only).

ROUTING: Research handoff exp_dev_handoff_research_uniform_criterion_SHARES_MATH_AAA3_definitive (Anchor 1, PRIMARY). The canonical AAA-3
  (0.94x) was CONFOUNDED (batch-authored SHARES_MATH cliques); my intrinsic AAA-3 was SUPPORT but used raw ratios (no null model). This is
  the STATISTICALLY RIGOROUS test: build a SHARES_MATH-PROXY graph by a UNIFORM rule applied to ALL atoms (tools + materials alike) -- two
  atoms are linked iff they share >= 1 serves_capability (criterion C3, uniform, NOT batch-authored). Then test whether TOOLS have higher
  out-degree than MATERIALS BEYOND what node degrees alone predict, via a LABEL-PERMUTATION null (degree-aware: the graph+degrees are fixed,
  only the tool/material labels are shuffled) + bootstrap CI + the excess-ratio. This resolves the confound AND adds rigor my intrinsic
  cell lacked. NO LLM; capability graph + numpy permutation/bootstrap; no heat. READ-ONLY.

PRE-REGISTERED (Research Anchor-1 thresholds):
  HARD-PASS: excess_ratio >= 1.25 AND 95% bootstrap CI lower > 1.0 AND permutation p < 0.01 AND naive_ratio >= 1.30.
  HARD-FAIL: excess_ratio <= 1.05 OR 95% CI crosses 1.0 OR permutation p >= 0.10.
  MIDDLE_BAND: otherwise (1.05 < excess < 1.25) -> recommends the C2/FCA cross-check (Anchor 2) before a final verdict.
  (excess_ratio = observed tool:material mean-degree ratio / mean ratio under label-permutation null; permutation null is degree-aware.)
  UNKNOWN if too few tools / no capability graph. ASCII-only. --self-test + --smoke + metrics.json.
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
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_aaa3_definitive_uniform_criterion_permutation_null_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_PERM = 2000; N_BOOT = 2000; SEED = 1028; MAX_BUCKET = 200
CURATED_TOOLS = set("""
fhrr_bind fhrr_unbind circular_convolution cleanup cosine_similarity superposition bundling discriminative_perceptron metric_space
spectral_gap theta_gamma_binding tracy_widom_distribution kappa_4_free mp_bulk_kl vsa_family unit_modulus vector_space gradient
inner_product role_filler_binding algebraic_binding context_binding cleanup_retrieval cosine_cleanup permutation_indexed_binding
resonator_network_decoder modern_hopfield_ramsauer hopfield_family superposition_aggregation unbinders ghrr_noncommutative_bind
theta_gamma_to_hrr qubit_to_fhrr_phasor
""".split())


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def build_capability_graph(caps: Dict[str, set], max_bucket=MAX_BUCKET):
    """UNIFORM rule applied to ALL atoms: edge(a,b) iff they share >=1 capability. Return degree dict over all atoms with caps."""
    cap2atoms = defaultdict(set)
    for a, cs in caps.items():
        for c in cs:
            cap2atoms[c].add(a)
    nbr = defaultdict(set)
    for c, atoms in cap2atoms.items():
        a = list(atoms)
        if 1 < len(a) <= max_bucket:
            for i in range(len(a)):
                for j in range(i + 1, len(a)):
                    nbr[a[i]].add(a[j]); nbr[a[j]].add(a[i])
    return nbr


def perm_test(deg_arr: np.ndarray, is_tool: np.ndarray, n_perm: int, rng) -> Tuple[float, float, float]:
    """Label-permutation null (degree-aware: degrees fixed, labels shuffled). Returns (observed_ratio, excess_ratio, p_value)."""
    nt = int(is_tool.sum())
    obs = deg_arr[is_tool].mean() / (deg_arr[~is_tool].mean() + 1e-12)
    n = len(deg_arr); null = np.empty(n_perm)
    for k in range(n_perm):
        idx = rng.permutation(n); tmask = np.zeros(n, dtype=bool); tmask[idx[:nt]] = True
        null[k] = deg_arr[tmask].mean() / (deg_arr[~tmask].mean() + 1e-12)
    p = float((null >= obs).mean())
    excess = float(obs / (null.mean() + 1e-12))
    return float(obs), excess, p


def bootstrap_ci(tool_deg: np.ndarray, mat_deg: np.ndarray, n_boot: int, rng) -> Tuple[float, float]:
    rr = np.empty(n_boot)
    for k in range(n_boot):
        t = tool_deg[rng.integers(0, len(tool_deg), len(tool_deg))]
        m = mat_deg[rng.integers(0, len(mat_deg), len(mat_deg))]
        rr[k] = t.mean() / (m.mean() + 1e-12)
    return float(np.percentile(rr, 2.5)), float(np.percentile(rr, 97.5))


def _selftest():
    rng = np.random.default_rng(0)
    # synthetic: tools have systematically higher degree -> excess>1, small p, CI>1
    deg = np.concatenate([rng.integers(8, 12, 20), rng.integers(1, 3, 80)]).astype(float)
    is_tool = np.zeros(100, dtype=bool); is_tool[:20] = True
    obs, excess, p = perm_test(deg, is_tool, 500, np.random.default_rng(1))
    assert obs > 3 and excess > 2 and p < 0.01, (obs, excess, p)
    lo, hi = bootstrap_ci(deg[is_tool], deg[~is_tool], 500, np.random.default_rng(2))
    assert lo > 1.0, (lo, hi)
    # null case: labels random wrt degree -> excess~1, p large
    deg2 = rng.integers(1, 5, 100).astype(float); it2 = np.zeros(100, dtype=bool); it2[:20] = True
    _, ex2, p2 = perm_test(deg2, it2, 500, np.random.default_rng(3))
    assert 0.7 < ex2 < 1.4 and p2 > 0.05, (ex2, p2)
    assert len(CURATED_TOOLS) == 33
    print("[selftest] PASS: substrate_aaa3_definitive_uniform_criterion_permutation_null_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    caps = {}
    for a in atoms:
        sid = _short(a.id); cs = getattr(a, "serves_capability", ()) or ()
        if cs:
            caps[sid] = set(_short(c) for c in cs)
    nbr = build_capability_graph(caps)
    nodes = sorted(set(caps))                              # atoms that serve >=1 capability (the uniform-graph node set)
    if len(nodes) < 20:
        return {"error": "too_few_capability_atoms", "n": len(nodes)}
    deg = np.array([len(nbr.get(n, ())) for n in nodes], dtype=float)
    is_tool = np.array([n in CURATED_TOOLS for n in nodes], dtype=bool)
    n_tools = int(is_tool.sum())
    if n_tools < 5:
        return {"error": "too_few_tools_in_capability_graph", "n_tools": n_tools}
    rng = np.random.default_rng(SEED)
    n_perm = N_PERM if RUN_MODE != "smoke" else 300; n_boot = N_BOOT if RUN_MODE != "smoke" else 300
    obs, excess, p = perm_test(deg, is_tool, n_perm, rng)
    ci_lo, ci_hi = bootstrap_ci(deg[is_tool], deg[~is_tool], n_boot, rng)
    naive = round(float(deg[is_tool].mean() / (deg[~is_tool].mean() + 1e-12)), 3)
    print("  uniform capability-sharing graph: %d nodes (>=1 capability), %d tools | naive ratio=%.3f" % (len(nodes), n_tools, naive), flush=True)
    print("  observed tool:material mean-degree ratio=%.3f | excess_ratio (vs label-perm null)=%.3f | permutation p=%.4f" % (obs, excess, p), flush=True)
    print("  95%% bootstrap CI on ratio = [%.3f, %.3f]" % (ci_lo, ci_hi), flush=True)
    return {"n_nodes": len(nodes), "n_tools": n_tools, "naive_ratio": naive, "observed_ratio": round(obs, 3),
            "excess_ratio": round(excess, 3), "perm_p": round(p, 4), "ci_lower": round(ci_lo, 3), "ci_upper": round(ci_hi, 3),
            "tool_mean_deg": round(float(deg[is_tool].mean()), 2), "mat_mean_deg": round(float(deg[~is_tool].mean()), 2)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n", r.get("n_tools", ""))))
    ex = r["excess_ratio"]; p = r["perm_p"]; lo = r["ci_lower"]; naive = r["naive_ratio"]
    s = ("uniform capability-sharing graph (%d nodes, %d tools): naive tool:material degree ratio=%.3f; excess_ratio=%.3f (vs degree-aware "
         "label-permutation null); permutation p=%.4f; 95%% bootstrap CI=[%.3f,%.3f]. (tool mean-deg %.2f vs material %.2f.) UNIFORM rule -> "
         "no batch-clique confound; permutation null -> degree-aware.") % (
        r["n_nodes"], r["n_tools"], naive, ex, p, lo, r["ci_upper"], r["tool_mean_deg"], r["mat_mean_deg"])
    if ex >= 1.25 and lo > 1.0 and p < 0.01 and naive >= 1.30:
        return ("HARD_PASS", "HARD_PASS (Reservation C DEFINITIVELY CONFIRMED): TOOLS have higher capability-sharing degree than MATERIALS BEYOND degree-chance -- excess_ratio %.2f>=1.25, CI lower %.2f>1.0, permutation p=%.4f<0.01, naive %.2f>=1.30. The load-bearing axis is REAL with statistical rigor (uniform criterion + degree-aware null) -- resolves the canonical 0.94x confound AND adds the null model my intrinsic test lacked. 13th methodology rule empirically grounded. " % (ex, lo, p, naive) + s)
    if ex <= 1.05 or lo <= 1.0 or p >= 0.10:
        return ("HARD_FAIL", "HARD_FAIL (Reservation C NOT supported by the rigorous test): excess_ratio %.2f / CI lower %.2f / p %.4f fail the bar -- tools are NOT load-bearing beyond degree-chance; reconsider Axis 2 per 7th rule. " % (ex, lo, p) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: excess_ratio %.2f in (1.05,1.25) -- partial; recommend the C2/FCA cross-check (Anchor 2) before a final verdict. " % ex + s)


print("[config] anchor=%s mode=%s n_perm=%d n_boot=%d tools=%d" % (ANCHOR_NAME, RUN_MODE, N_PERM, N_BOOT, len(CURATED_TOOLS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
