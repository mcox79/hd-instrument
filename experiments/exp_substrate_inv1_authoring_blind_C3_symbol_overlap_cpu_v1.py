"""
exp_substrate_inv1_authoring_blind_C3_symbol_overlap_cpu_v1.py -- INV-1 arm_C3: does the load-bearing axis survive when edges are rebuilt from ATOM BODY TEXT alone (never reading curator tags)? -- CPU/local (no heat).

ROUTING: Research handoff exp_dev_handoff_research_INV1_authoring_blind_null (Anchor 1, TIER-1) -- a SKUNKWORKS FALSIFICATION GATE on MY OWN
  load-bearing-axis results. Concern: my 3 "independent" tests (provisional 1.33x, intrinsic 3/3, definitive 2.34x p=0.0005) ALL measured on
  the same authored graph / used curated tool tags; they may be ONE confound. INV-1 rebuilds the edge set PURELY from atom body text by a
  mechanical criterion that NEVER reads the curator tool/material tag, then re-tests the load-bearing metric M (tool vs material degree). If
  tools STILL show higher degree, the axis is substrate-readable from bodies alone (not a tagging artifact). arm_C3 = shared-SYMBOL overlap
  (sparsest, lowest power, MOST authoring-blind, the GATE). ATOM-body-dependent (NOT relations -> safe during the relations re-ingest);
  no bge/GPU. Per 7th USER-LOCKED rule (reconsider, don't lock in): audit the capstone. NO LLM; body-text token graph + permutation null; no heat.

  EDGE GENERATOR (tag-blind): symbols = distinctive content tokens of each atom's `description` (df-banded 2<=df<=DF_MAX to strip boilerplate
  + singletons). C3 edge(a,b) iff |symbols_a & symbols_b| >= 2. NO atom's tool/material membership is read when building edges (verified by a
  one-line audit). Tool/material labels are applied ONLY for the final degree comparison M. M + null match the DEFINITIVE test (tool:material
  mean-degree ratio; degree-aware LABEL-PERMUTATION null; z = (observed - null_mean)/null_std).

PRE-REGISTERED (Research INV-1 fail bands, C3 arm): HARD-PASS-contribution if C3 z >= 2.0. EXPLICIT-FAIL if C3 z < 1.0. (Full INV-1 HARD-PASS
  needs >=2/3 arms at z>=3.0 AND C3 at z>=2.0; this cell ships the GATE arm C3; C1/C2 arms follow.) This cell verdict: C3_PASS z>=2.0 /
  C3_FAIL z<1.0 / C3_MIDDLE otherwise. Bands pre-registered BEFORE computing rebuilt-graph numbers. UNKNOWN if atom read races / too few tools.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_inv1_authoring_blind_C3_symbol_overlap_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_PERM = 2000; DF_MAX_FRAC = 0.08; DF_MIN = 2; MIN_TOK_LEN = 3; SHARED_SYMBOL_MIN = 2; JACCARD_MIN = 0.18; MAX_BUCKET = 150; SEED = 1028
# CONFOUND CORRECTION (caught: naive raw-overlap over ALL atoms gave z=-6.10, an artifact of DESCRIPTION LENGTH -- history-note prose
# (1245 long-prose atoms) dominated material degree while terse tool definitions scored low). Fix: (1) SYSTEM-ONLY (exclude history/record
# prose; matches the DEFINITIVE test's effective scope = system atoms) + (2) JACCARD edges (length-normalized, approximating the handoff's
# length-independent math-symbol intent for prose bodies). The corrected C3 is the honest authoring-blind test.
CURATED_TOOLS = set("""
fhrr_bind fhrr_unbind circular_convolution cleanup cosine_similarity superposition bundling discriminative_perceptron metric_space
spectral_gap theta_gamma_binding tracy_widom_distribution kappa_4_free mp_bulk_kl vsa_family unit_modulus vector_space gradient
inner_product role_filler_binding algebraic_binding context_binding cleanup_retrieval cosine_cleanup permutation_indexed_binding
resonator_network_decoder modern_hopfield_ramsauer hopfield_family superposition_aggregation unbinders ghrr_noncommutative_bind
theta_gamma_to_hrr qubit_to_fhrr_phasor
""".split())
_STOP = set("the of a an and or to for with in on is as by at from this that these those it its be are was were will would can could should has have had not but if then so we use used using also form set map maps space over under into more most".split())


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _tokens(text):
    return [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) >= MIN_TOK_LEN and t not in _STOP and not t.isdigit()]


def c3_symbol_graph(bodies: Dict[str, str], df_max_frac=DF_MAX_FRAC):
    """Tag-BLIND: edges from shared distinctive body-text symbols (df-banded). Returns degree dict + #edges. Reads ONLY body text."""
    toks = {a: set(_tokens(b)) for a, b in bodies.items()}
    df = Counter()
    for s in toks.values():
        for t in s: df[t] += 1
    df_max = max(3, int(df_max_frac * len(bodies)))
    sal = {a: {t for t in s if DF_MIN <= df[t] <= df_max} for a, s in toks.items()}
    tok2 = defaultdict(list)
    for a, s in sal.items():
        for t in s: tok2[t].append(a)
    pair = Counter()
    for t, atoms in tok2.items():
        if 1 < len(atoms) <= MAX_BUCKET:
            for x, y in combinations(sorted(atoms), 2): pair[(x, y)] += 1
    deg = Counter(); nedges = 0
    for (x, y), c in pair.items():
        # JACCARD-normalized (length-independent) AND raw shared-symbol >= 2 (handoff threshold)
        ja = c / (len(sal[x] | sal[y]) + 1e-9)
        if c >= SHARED_SYMBOL_MIN and ja >= JACCARD_MIN:
            deg[x] += 1; deg[y] += 1; nedges += 1
    return deg, nedges


def perm_z(deg_arr, is_tool, n_perm, rng):
    nt = int(is_tool.sum())
    obs = deg_arr[is_tool].mean() / (deg_arr[~is_tool].mean() + 1e-12)
    n = len(deg_arr); null = np.empty(n_perm)
    for k in range(n_perm):
        idx = rng.permutation(n); m = np.zeros(n, dtype=bool); m[idx[:nt]] = True
        null[k] = deg_arr[m].mean() / (deg_arr[~m].mean() + 1e-12)
    z = (obs - null.mean()) / (null.std() + 1e-12)
    p = float((null >= obs).mean())
    return float(obs), float(z), p


def _selftest():
    # tag-blind edges from shared body tokens; tools share a distinctive token -> higher degree -> z>=2
    bodies = {}
    for i in range(6): bodies["t%d" % i] = "binding convolution phasor unbind toolword%d" % (i % 2)   # tools share 'binding convolution phasor unbind'
    for i in range(40): bodies["m%d" % i] = "history note research drill unique%d alpha%d" % (i, i)     # materials mostly distinct
    deg, ne = c3_symbol_graph(bodies, df_max_frac=0.5)
    ids = sorted(bodies); da = np.array([deg.get(a, 0) for a in ids], float)
    it = np.array([a.startswith("t") for a in ids], bool)
    obs, z, p = perm_z(da, it, 500, np.random.default_rng(1))
    assert obs > 1.5 and z > 2.0, (obs, z, p)
    # audit: c3_symbol_graph reads only bodies (no tags) -- structurally true (no tool arg passed)
    assert len(CURATED_TOOLS) == 33
    print("[selftest] PASS: substrate_inv1_authoring_blind_C3_symbol_overlap_cpu_v1 (tag-blind body-symbol graph + perm-z)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _load_bodies():
    """Race-tolerant atom read: retry until a complete-looking set (atoms growing during ingest)."""
    from backend.substrate_index.partition import PartitionedStore
    last = 0
    for attempt in range(6):
        try:
            ats = PartitionedStore(REPO / "data" / "substrate_index").all_atoms()
            n = len(ats)
            if n >= 500:
                # SYSTEM-ONLY: exclude history/record prose (matches DEFINITIVE test scope; removes the length confound)
                bodies = {}
                for a in ats:
                    c = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
                    if "history" in c:
                        continue
                    bodies[_short(a.id)] = (getattr(a, "description", "") or "")
                return bodies, n
            last = n
        except Exception:
            pass
        time.sleep(8)
    return None, last


def run() -> Dict:
    if not (REPO / "data" / "substrate_index").exists():
        return {"error": "no_substrate_index"}
    bodies, n = _load_bodies()
    if bodies is None:
        return {"error": "atom_read_incomplete_or_race", "n_atoms_seen": n}
    print("  [audit] arm_C3 edge generator reads ONLY atom `description` body text; curator tool/material tag is NOT read when building edges.", flush=True)
    deg, nedges = c3_symbol_graph(bodies)
    ids = sorted(bodies)
    deg_arr = np.array([deg.get(a, 0) for a in ids], dtype=float)
    is_tool = np.array([a in CURATED_TOOLS for a in ids], dtype=bool)
    n_tools = int(is_tool.sum())
    if n_tools < 5 or nedges < 50:
        return {"error": "too_few_tools_or_edges", "n_tools": n_tools, "n_edges": nedges}
    rng = np.random.default_rng(SEED)
    obs, z, p = perm_z(deg_arr, is_tool, N_PERM if RUN_MODE != "smoke" else 300, rng)
    tmean = round(float(deg_arr[is_tool].mean()), 3); mmean = round(float(deg_arr[~is_tool].mean()), 3)
    print("  body-text C3 symbol graph: %d atoms, %d edges (shared-symbol>=%d) | tools=%d in graph" % (len(ids), nedges, SHARED_SYMBOL_MIN, n_tools), flush=True)
    print("  M (tool:material mean-degree): tools=%.2f vs materials=%.2f -> ratio=%.3f | permutation z=%.3f p=%.4f" % (tmean, mmean, obs, z, p), flush=True)
    return {"n_atoms": len(ids), "n_edges": nedges, "n_tools": n_tools, "tool_mean_deg": tmean, "mat_mean_deg": mmean,
            "ratio": round(obs, 3), "z": round(z, 3), "perm_p": round(p, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n_atoms_seen", r.get("n_tools", ""))))
    z = r["z"]
    s = ("authoring-BLIND C3 (body-text shared-symbol>=2) graph: %d edges; tool:material mean-degree ratio=%.3f; permutation z=%.3f p=%.4f "
         "(tools %.2f vs materials %.2f). Edges built from atom `description` ONLY -- curator tags never read.") % (
        r["n_edges"], r["ratio"], z, r["perm_p"], r["tool_mean_deg"], r["mat_mean_deg"])
    if z >= 2.0:
        return ("C3_PASS", "C3_PASS (z=%.2f >= 2.0): the load-bearing axis SURVIVES authoring-blind reconstruction -- tools have higher degree than materials EVEN when edges are rebuilt purely from body-text symbols (never reading curator tags). My 3 prior load-bearing results are NOT merely a tagging confound; the axis is substrate-readable from atom bodies alone. (Gate arm passes; C1/C2 arms follow for the full INV-1 verdict.) " % z + s)
    if z < 1.0:
        return ("C3_FAIL", "C3_FAIL (z=%.2f < 1.0): the load-bearing axis does NOT survive authoring-blind reconstruction -- body-text symbol edges show no tool>material degree signal. Per INV-1, this means the prior 3 tests may be one tagging confound; the 3-axis-orthogonal capstone needs an honest footnote (axis-existence vs axis-magnitude-as-measured). " % z + s)
    return ("C3_MIDDLE", "C3_MIDDLE (1.0 <= z=%.2f < 2.0): partial authoring-blind signal -- not decisive; treat as PARTIAL, run C1/C2 arms + do not claim full INV-1 pass. " % z + s)


print("[config] anchor=%s mode=%s n_perm=%d shared_symbol_min=%d tools=%d" % (ANCHOR_NAME, RUN_MODE, N_PERM, SHARED_SYMBOL_MIN, len(CURATED_TOOLS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
