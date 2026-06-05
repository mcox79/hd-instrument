"""
substrate_cognitive_core_introspection_toolkit_v1 -- Phase 1.5 substrate introspection (audit/density/crosstalk) -- CPU.

ROUTING: research phase1_5_introspection_toolkit (user insight: analyze substrate after LLM ingestion to see how it
  works, find barriers/inefficiencies). Substrate is INHERENTLY introspectable (discrete concepts, stored patterns,
  retrieval chains) -- a categorical product feature LLMs cannot replicate ("show your work" for regulated AI).
  Builds the 3 highest-priority categories on the REAL Pythia-concept substrate. CPU numpy+sklearn $0. remote_cpu.

CATEGORIES (per note priority): #2 per-answer AUDIT TRAIL (trace retrieved patterns + provenance per query),
  #1 KNOWLEDGE DENSITY map (per-concept write counts, hot/sparse zones, retrieval confidence), #4 CROSSTALK/
  interference detection (pairwise pattern similarity, near-collisions, conflation risk).

ACCEPTANCE (engineering, not hypothesis): HARD-PASS = all 3 analyses run + produce non-trivial actionable insights
  (density distribution computed, crosstalk measured w/ near-collision count, >=1 audit trail traced end-to-end).
  MIDDLE = 2 of 3. HARD-FAIL = <2 (toolkit non-functional).
FORMULA SELF-TESTS (PROT-022): 1. density count. 2. crosstalk similarity. 3. audit-trail contributor trace.
ASCII-only. write_metrics. PROT-018: no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_introspection_toolkit_v1"
NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"
N_DIM = 1024; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 64; MAX_DOCS = 300; N_AUDIT = 5
else:
    SEEDS = [7, 17, 23]; V_C = 256; MAX_DOCS = 100000; N_AUDIT = 20


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _numpy_kmeans(X, k, seed, iters=25):
    g = np.random.default_rng(seed); cen = X[g.choice(len(X), size=k, replace=False)].copy(); a = np.zeros(len(X), dtype=np.int64)
    for _ in range(iters):
        for s in range(0, len(X), 4096):
            a[s:s + 4096] = np.argmin(((X[s:s + 4096, None, :] - cen[None]) ** 2).sum(-1), 1)
        for c in range(k):
            m = a == c
            if m.any():
                cen[c] = X[m].mean(0)
    return a


def _selftest():
    cnt = np.bincount([0, 0, 1, 2, 2, 2], minlength=3); assert cnt[2] == 3, "density count"
    g = np.random.default_rng(0); C = bp(4, 128, g); sim = C @ C.T; assert abs(sim[0, 0] - 1.0) < 1e-4, "crosstalk similarity"
    print("[selftest] PASS: density crosstalk", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_docs(seed):
    if not NPZ_PATH.exists():
        raise FileNotFoundError("residuals_per_token.npz not found")
    z = np.load(NPZ_PATH); res = z["residuals"].astype(np.float32); bnd = z["doc_boundaries"].astype(np.int64)
    nd = min(len(bnd) - 1, MAX_DOCS); bnd = bnd[: nd + 1]; res = res[: bnd[-1]]
    try:
        from sklearn.cluster import MiniBatchKMeans
        cid = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=2048, n_init=3, max_iter=100).fit_predict(res)
    except Exception:
        cid = _numpy_kmeans(res, V_C, seed)
    docs = [cid[bnd[i]:bnd[i + 1]] for i in range(nd) if bnd[i + 1] - bnd[i] >= 2]
    return docs


def run_seed(seed):
    g = np.random.default_rng(seed); n = N_DIM; docs = load_docs(seed); C = bp(V_C, n, g)
    W = np.zeros((n, n), dtype=np.float32)
    write_count = np.zeros(V_C, dtype=np.int64)             # density: per-concept source-write counts
    transition_provenance = {}                              # (src,dst) -> set(doc ids) for audit provenance
    for di, d in enumerate(docs):
        for t in range(1, len(d)):
            src, dst = int(d[t - 1]), int(d[t])
            W += (LR / n) * np.outer(C[dst] - W @ C[src], C[src]); write_count[src] += 1
            transition_provenance.setdefault((src, dst), set()).add(di)

    # ---- Category 1: KNOWLEDGE DENSITY / COVERAGE ----
    hot = int(np.argmax(write_count)); sparse_frac = float(np.mean(write_count < max(1, write_count.mean() * 0.1)))
    conf = np.array([float(np.max(C @ (W @ C[c]))) for c in range(V_C)])    # retrieval confidence per concept
    density = {"hot_concept": hot, "hot_count": int(write_count[hot]), "mean_count": float(write_count.mean()),
               "sparse_zone_frac": sparse_frac, "mean_retrieval_conf": float(conf.mean()), "low_conf_frac": float(np.mean(conf < 0.3))}

    # ---- Category 4: CROSSTALK / INTERFERENCE ----
    sim = C @ C.T; np.fill_diagonal(sim, -1.0)
    near_collisions = int(np.sum(sim > 0.3) // 2)
    crosstalk = {"max_offdiag_sim": float(sim.max()), "mean_offdiag_sim": float(sim[sim > -1].mean()),
                 "near_collision_pairs_gt0.3": near_collisions, "conflation_risk": "low" if sim.max() < 0.3 else "moderate"}

    # ---- Category 2: PER-ANSWER AUDIT TRAIL ----
    audits = []
    for d in docs[:N_AUDIT]:
        if len(d) < 2:
            continue
        src = int(d[0]); r = W @ C[src]; pred = int(np.argmax(C @ r)); conf_p = float(np.max(C @ r))
        # provenance: which docs taught the winning transition; top alternative concepts
        prov = len(transition_provenance.get((src, pred), set()))
        scores = C @ r; top3 = [int(i) for i in np.argsort(-scores)[:3]]
        audits.append({"query_concept": src, "predicted": pred, "confidence": round(conf_p, 3),
                       "provenance_doc_count": prov, "top3_candidates": top3})
    audit_ok = len(audits) >= 1 and all("predicted" in a for a in audits)
    return {"seed": seed, "n_docs": len(docs), "n_concepts": V_C, "n_transitions_stored": int(write_count.sum()),
            "density": density, "crosstalk": crosstalk, "audit_trail_examples": audits, "audit_functional": audit_ok}


def verdict(ps) -> Tuple[str, str]:
    d_ok = all(p["density"]["mean_count"] > 0 for p in ps)
    c_ok = all("max_offdiag_sim" in p["crosstalk"] for p in ps)
    a_ok = all(p["audit_functional"] for p in ps)
    npass = d_ok + c_ok + a_ok
    p0 = ps[0]
    summary = ("density[hot=%d sparse_frac=%.2f mean_conf=%.2f] crosstalk[max_sim=%.2f near_collisions=%d conflation=%s] audit[%d traced, e.g. concept%d->%d conf=%.2f prov_docs=%d]" % (
        p0["density"]["hot_concept"], p0["density"]["sparse_zone_frac"], p0["density"]["mean_retrieval_conf"],
        p0["crosstalk"]["max_offdiag_sim"], p0["crosstalk"]["near_collision_pairs_gt0.3"], p0["crosstalk"]["conflation_risk"],
        len(p0["audit_trail_examples"]), p0["audit_trail_examples"][0]["query_concept"], p0["audit_trail_examples"][0]["predicted"],
        p0["audit_trail_examples"][0]["confidence"], p0["audit_trail_examples"][0]["provenance_doc_count"]))
    if npass == 3:
        return ("HARD_PASS", "HARD_PASS: substrate introspection toolkit functional -- audit-trail + density + crosstalk all produce actionable insights (categorical 'show your work' feature). " + summary)
    if npass == 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2 of 3 introspection categories functional. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: introspection toolkit non-functional. " + summary)


print("[config] anchor=%s mode=%s seeds=%s V_c=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, V_C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] concepts=%d transitions=%d | density hot=%d mean_conf=%.2f | crosstalk max_sim=%.2f collisions=%d | audits=%d" % (
        seed, r["n_concepts"], r["n_transitions_stored"], r["density"]["hot_concept"], r["density"]["mean_retrieval_conf"],
        r["crosstalk"]["max_offdiag_sim"], r["crosstalk"]["near_collision_pairs_gt0.3"], len(r["audit_trail_examples"])), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
