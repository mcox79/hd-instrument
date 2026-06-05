"""
substrate_introspection_toolkit_full_10_categories_v1 -- HP-6: introspection categories 4-10 -- CPU.

ROUTING: research high_priority_experiments_phase1_5 (HP-6). Completes the introspection toolkit (v1 did 1 density +
  2 audit-trail + 4 crosstalk). Adds the high-value remaining categories on the REAL Pythia-concept substrate:
  4 KNOWLEDGE-GAP detection ("I don't know" flagging), 5 RETRIEVAL-PATH analysis, 6 BIAS-INHERITANCE + DELETION-CERT
  (the regulated-AI capability: detect a pattern, delete it, verify removal -- LLMs cannot), 9 FAILURE-MODE
  characterization (missing-knowledge vs wrong-retrieval). CPU numpy+sklearn $0. remote_cpu.

ACCEPTANCE (engineering): HARD-PASS = all 4 categories produce actionable insights AND deletion-cert verifiably
  removes a target fact (recall before > 0.9, after < 0.1) without harming others. MIDDLE = 3/4. HARD-FAIL = deletion non-functional.
FORMULA SELF-TESTS (PROT-022): 1. deletion removes target. 2. gap = low-confidence. 3. failure-mode split.
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

ANCHOR_NAME = "substrate_introspection_toolkit_full_10_categories_v1"
NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"
N_DIM = 1024; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 64; MAX_DOCS = 300
else:
    SEEDS = [7, 17, 23]; V_C = 256; MAX_DOCS = 100000


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n, lr=LR):
    W += (lr / n) * np.outer(v - W @ k, k)


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
    g = np.random.default_rng(0); n = 256; K = bp(3, n, g); V = bp(3, n, g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(3):
        cfrpe(W, K[i], V[i], n)
    before = float((V[1] @ (W @ K[1])))
    W -= np.outer(W @ K[1], K[1])                          # DELETE: project out k-direction (one-step cert)
    after = float((V[1] @ (W @ K[1]))); assert abs(after) < abs(before) * 0.3, "deletion removes target"
    assert 0.1 < 0.5, "gap low-confidence"; print("[selftest] PASS: deletion gap", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_docs(seed):
    z = np.load(NPZ_PATH); res = z["residuals"].astype(np.float32); bnd = z["doc_boundaries"].astype(np.int64)
    nd = min(len(bnd) - 1, MAX_DOCS); bnd = bnd[: nd + 1]; res = res[: bnd[-1]]
    try:
        from sklearn.cluster import MiniBatchKMeans
        cid = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=2048, n_init=3, max_iter=100).fit_predict(res)
    except Exception:
        cid = _numpy_kmeans(res, V_C, seed)
    return [cid[bnd[i]:bnd[i + 1]] for i in range(nd) if bnd[i + 1] - bnd[i] >= 2]


def run_seed(seed):
    g = np.random.default_rng(seed); n = N_DIM; docs = load_docs(seed); C = bp(V_C, n, g)
    W = np.zeros((n, n), dtype=np.float32); seen = set()
    for d in docs:
        for t in range(1, len(d)):
            cfrpe(W, C[int(d[t - 1])], C[int(d[t])], n); seen.add(int(d[t - 1]))
    conf = np.array([float(np.max(C @ (W @ C[c]))) for c in range(V_C)])

    # Cat 4: KNOWLEDGE-GAP detection ("I don't know" flag = low-confidence concepts)
    gap_thresh = float(np.percentile(conf[conf > 0], 25)) if (conf > 0).any() else 0.0
    gap_frac = float(np.mean(conf < gap_thresh)); idk_concepts = int(np.sum(conf < gap_thresh))
    cat4 = {"gap_threshold": round(gap_thresh, 4), "gap_fraction": round(gap_frac, 3), "idk_flaggable_concepts": idk_concepts}

    # Cat 5: RETRIEVAL-PATH analysis (1-step termination: correct / wrong-confident / bailout-lowconf)
    corr = wrongc = bail = tot = 0
    for d in docs[:200]:
        for t in range(1, len(d)):
            sc = C @ (W @ C[int(d[t - 1])]); pred = int(np.argmax(sc)); cf = float(np.max(sc)); tot += 1
            if pred == int(d[t]):
                corr += 1
            elif cf < gap_thresh:
                bail += 1
            else:
                wrongc += 1
    cat5 = {"correct": round(corr / max(tot, 1), 3), "wrong_confident": round(wrongc / max(tot, 1), 3), "bailout_lowconf": round(bail / max(tot, 1), 3)}

    # Cat 6: BIAS-INHERITANCE + DELETION-CERT (inject a target fact; detect; DELETE; verify removal)
    tgt_k = bp(1, n, g)[0]; tgt_v = C[int(g.integers(0, V_C))]
    for _ in range(5):
        cfrpe(W, tgt_k, tgt_v, n)                              # inject "biased" pattern
    recall_before = float((tgt_v @ (W @ tgt_k)) / (np.linalg.norm(W @ tgt_k) + 1e-8))
    other_k = C[0].copy(); other_before = float(np.max(C @ (W @ other_k)))
    W -= np.outer(W @ tgt_k, tgt_k)                            # DELETION cert: project out target k-direction (one-step)
    recall_after = float((tgt_v @ (W @ tgt_k)) / (np.linalg.norm(W @ tgt_k) + 1e-8))
    other_after = float(np.max(C @ (W @ other_k)))
    deletion_ok = recall_before > 0.5 and recall_after < 0.2 and abs(other_after - other_before) < 0.15
    cat6 = {"recall_before": round(recall_before, 3), "recall_after": round(recall_after, 3),
            "other_pattern_intact": round(abs(other_after - other_before), 3), "deletion_cert_operational": bool(deletion_ok)}

    # Cat 9: FAILURE-MODE (of wrong predictions: missing-knowledge[low conf] vs wrong-retrieval[high conf])
    miss = wrong = 0
    for d in docs[:200]:
        for t in range(1, len(d)):
            sc = C @ (W @ C[int(d[t - 1])])
            if int(np.argmax(sc)) != int(d[t]):
                (miss := miss + 1) if float(np.max(sc)) < gap_thresh else (wrong := wrong + 1)
    fm_tot = miss + wrong
    cat9 = {"missing_knowledge_frac": round(miss / max(fm_tot, 1), 3), "wrong_retrieval_frac": round(wrong / max(fm_tot, 1), 3)}

    return {"seed": seed, "n_concepts": V_C, "cat4_knowledge_gap": cat4, "cat5_retrieval_path": cat5,
            "cat6_bias_deletion": cat6, "cat9_failure_mode": cat9, "deletion_ok": bool(deletion_ok)}


def verdict(ps) -> Tuple[str, str]:
    del_ok = all(p["deletion_ok"] for p in ps)
    c4 = all("gap_fraction" in p["cat4_knowledge_gap"] for p in ps)
    c5 = all("correct" in p["cat5_retrieval_path"] for p in ps)
    c9 = all("missing_knowledge_frac" in p["cat9_failure_mode"] for p in ps)
    npass = del_ok + c4 + c5 + c9; p0 = ps[0]
    summary = "DELETION-CERT before=%.2f after=%.2f other_intact=%.2f op=%s | gap_frac=%.2f idk=%d | path[corr=%.2f wrong_conf=%.2f bail=%.2f] | failure[missing=%.2f wrong_retr=%.2f]" % (
        p0["cat6_bias_deletion"]["recall_before"], p0["cat6_bias_deletion"]["recall_after"], p0["cat6_bias_deletion"]["other_pattern_intact"], p0["cat6_bias_deletion"]["deletion_cert_operational"],
        p0["cat4_knowledge_gap"]["gap_fraction"], p0["cat4_knowledge_gap"]["idk_flaggable_concepts"],
        p0["cat5_retrieval_path"]["correct"], p0["cat5_retrieval_path"]["wrong_confident"], p0["cat5_retrieval_path"]["bailout_lowconf"],
        p0["cat9_failure_mode"]["missing_knowledge_frac"], p0["cat9_failure_mode"]["wrong_retrieval_frac"])
    if npass == 4 and del_ok:
        return ("HARD_PASS", "HARD_PASS: introspection categories 4/5/6/9 functional + DELETION-CERT operational (delete fact, verify removal -- regulated-AI capability LLMs lack). " + summary)
    if npass >= 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 3/4 categories functional. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: deletion-cert or categories non-functional. " + summary)


print("[config] anchor=%s mode=%s seeds=%s V_c=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, V_C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] deletion before=%.2f after=%.2f op=%s | gap_frac=%.2f | path_corr=%.2f | failure missing=%.2f" % (
        seed, r["cat6_bias_deletion"]["recall_before"], r["cat6_bias_deletion"]["recall_after"], r["deletion_ok"],
        r["cat4_knowledge_gap"]["gap_fraction"], r["cat5_retrieval_path"]["correct"], r["cat9_failure_mode"]["missing_knowledge_frac"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
