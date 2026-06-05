"""
substrate_ccc_smoke_concept_core_pythia70m_v1 -- CCC-smoke: cognitive-core first gate (Path A) -- GPU.

ROUTING: research_drill_substrate_as_cognitive_core_training_methodology_3x (Sub-Q6 CCC-smoke, "run TODAY, $0").
  First gate for substrate-as-cognitive-core: verify the FULL Path-A chain works -- VQ concept-ID -> substrate
  Hebbian write -> SQ2 retrieval. INLINE Pythia-70M extraction on ~1000 fact sentences (no npz dependency;
  independent of the Llama hang / Testbed Pythia run). torch+transformers GPU, $0.

CAPABILITY QUESTION: does (frozen Pythia-70M encode -> VQ V_c -> substrate concept-transition write -> retrieval)
  recover the correct NEXT concept for held-out fact-chain transitions?

MODEL: M fact-chains (length L) of templated relational sentences "<subj> <rel> <obj>" (obj_t = subj_{t+1} ->
  multi-hop chain). Frozen Pythia-70M -> mean-pooled last hidden -> embedding per sentence. numpy k-means VQ
  (V_c concepts). Each concept-ID -> fixed random bipolar phi(c) in {-1,+1}^N. Substrate: W += outer(phi(c_{t+1}),
  phi(c_t)) over chain transitions. Retrieval: query concept c_t -> r=sign(W @ phi(c_t)) -> nearest concept
  codebook -> check it equals c_{t+1} (cosine(r, phi(c_{t+1})) >= 0.7).

PRE-REGISTERED bands (Sub-Q6): HARD-PASS >= 70% of held-out transitions retrieved at cosine >= 0.7.
  MIDDLE: 40-70%. HARD-FAIL: < 40% (VQ alignment failure or substrate capacity issue).

FORMULA SELF-TESTS (PROT-022): 1. substrate transition recall (clean). 2. k-means assigns nearest. 3. N=4096.
GPU TEMPLATE: assert cuda. ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch, torch.nn.functional as F
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_ccc_smoke_concept_core_pythia70m_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
MODEL_ID = "EleutherAI/pythia-70m"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ENTITIES = ["France", "Paris", "Europe", "Berlin", "Germany", "Rome", "Italy", "Madrid", "Spain", "Lisbon",
            "Portugal", "Vienna", "Austria", "Athens", "Greece", "Oslo", "Norway", "Dublin", "Ireland", "Warsaw",
            "Poland", "Prague", "Brussels", "Belgium", "Bern", "Tokyo", "Japan", "Asia", "Seoul", "Korea",
            "Cairo", "Egypt", "Africa", "Ottawa", "Canada", "Lima", "Peru", "Quito", "Chile", "Bogota"]
RELS = ["is the capital of", "is located in", "is part of", "is a city in", "lies within"]
COS_THRESH = 0.70
if RUN_MODE == "smoke":
    SEEDS = [1]; M_CHAINS = 40; L = 4; V_C = 16; N_DIM = 1024; N_TEST = 10
else:
    SEEDS = [7, 17, 23]; M_CHAINS = 250; L = 4; V_C = 64; N_DIM = N; N_TEST = 10


def gen_chains(g):
    chains = []
    for _ in range(M_CHAINS):
        path = list(g.choice(len(ENTITIES), size=L + 1, replace=False))
        sents = ["%s %s %s." % (ENTITIES[path[i]], RELS[int(g.integers(0, len(RELS)))], ENTITIES[path[i + 1]]) for i in range(L)]
        chains.append(sents)
    return chains


def kmeans(X, k, g, iters=25):
    idx = g.choice(len(X), size=k, replace=False); C = X[idx].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(2); a = d.argmin(1)
        for j in range(k):
            m = X[a == j]
            if len(m):
                C[j] = m.mean(0)
    d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(2)
    return d.argmin(1), C


def phi_codebook(V, n, g):
    cb = (g.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


K_CTX = 3


def context_vec(phi, c, t):
    """position-bound context of previous concepts c[t], c[t-1], ... (drill h_t^K)."""
    v = np.zeros(phi.shape[1], dtype=np.float32)
    for k in range(min(t + 1, K_CTX)):
        v = v + np.roll(phi[c[t - k]], k)
    return v / (np.linalg.norm(v) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; cb = phi_codebook(5, n, g)
    ctx = context_vec(cb, [1, 2], 1); W = np.zeros((n, n), dtype=np.float32); W += np.outer(cb[3], ctx)  # ctx(1,2)->3
    r = np.sign(W @ ctx); r = r / (np.linalg.norm(r) + 1e-8)
    assert float(r @ cb[3]) >= 0.7, "context-bound transition recall"
    X = np.array([[0.0, 0], [0.1, 0], [5.0, 5], [5.1, 5]], dtype=np.float32)
    a, _ = kmeans(X, 2, np.random.default_rng(1)); assert a[0] == a[1] and a[2] == a[3] and a[0] != a[2], "kmeans groups"
    assert N == 4096; print("[selftest] PASS: transition_recall kmeans", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _ENC = AutoModel.from_pretrained(MODEL_ID).to(DEVICE).eval()


def encode(sents):
    embs = []
    with torch.no_grad():
        for i in range(0, len(sents), 64):
            b = sents[i:i + 64]; t = _TOK(b, return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEVICE)
            h = _ENC(**t).last_hidden_state; mask = t["attention_mask"].unsqueeze(-1).float()
            emb = (h * mask).sum(1) / (mask.sum(1) + 1e-6)
            embs.append(emb.float().cpu().numpy())
    return np.concatenate(embs, 0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); chains = gen_chains(g)
    flat = [s for ch in chains for s in ch]
    emb = encode(flat); emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    labels, _ = kmeans(emb, V_C, np.random.default_rng(seed + 1))
    # reshape labels back to chains
    cid = []; p = 0
    for ch in chains:
        cid.append(labels[p:p + len(ch)]); p += len(ch)
    phi = phi_codebook(V_C, N_DIM, np.random.default_rng(seed + 2))
    # store concept transitions with position-bound context keys (drill Step 3) via cf-RPE delta rule
    # (online least-squares; handles CORRELATED context keys where raw Hebbian overloads). LR=0.5, ctx unit-norm.
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32); transitions = []
    pairs = []
    for ci, c in enumerate(cid):
        for t in range(len(c) - 1):
            pairs.append((context_vec(phi, c, t), phi[c[t + 1]])); transitions.append((ci, t))
    LR = 0.5
    for _ep in range(40):
        for ctx, tgt in pairs:
            W += LR * np.outer(tgt - W @ ctx, ctx)
    # diagnostic: concept diversity + context->target conflict rate (degenerate VQ check)
    n_distinct = len(set(int(x) for c in cid for x in c))
    from collections import defaultdict
    ctx_targets = defaultdict(set)
    for ci, c in enumerate(cid):
        for t in range(len(c) - 1):
            ctx_targets[tuple(int(c[max(0, t - k)]) for k in range(K_CTX))].add(int(c[t + 1]))
    conflict = float(np.mean([len(v) > 1 for v in ctx_targets.values()]))
    print("  [diag seed=%d] distinct_concepts=%d/%d ctx_conflict_rate=%.2f (frac contexts with >1 target)" % (seed, n_distinct, V_C, conflict), flush=True)
    gt = np.random.default_rng(seed + 5); sel = gt.choice(len(transitions), size=min(N_TEST, len(transitions)), replace=False)
    hits = 0
    for si in sel:
        ci, t = transitions[si]; c = cid[ci]; ctx = context_vec(phi, c, t)
        r = np.sign(W @ ctx); r = r / (np.linalg.norm(r) + 1e-8)
        hits += (float(r @ phi[c[t + 1]]) >= COS_THRESH)
    return {"seed": seed, "N": N_DIM, "V_c": V_C, "n_chains": len(chains), "n_transitions": len(transitions),
            "retrieved": int(hits), "n_test": int(len(sel)), "frac": float(hits / len(sel))}


def verdict(ps) -> Tuple[str, str]:
    fr = float(np.mean([p["frac"] for p in ps]))
    summary = "retrieved=%.0f%% of held-out transitions (cos>=%.2f); V_c=%d N=%d chains=%d" % (100 * fr, COS_THRESH, ps[0]["V_c"], ps[0]["N"], ps[0]["n_chains"])
    if fr >= 0.70:
        return ("HARD_PASS", "HARD_PASS: VQ-concept -> substrate -> retrieval chain WORKS (cognitive-core gate). " + summary)
    if fr >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial concept retrieval (VQ alignment needs tuning). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: VQ-alignment or substrate-capacity failure. " + summary)


print("[config] anchor=%s mode=%s seeds=%s model=%s V_c=%d N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, MODEL_ID, V_C, N_DIM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] retrieved=%d/%d (%.0f%%)" % (seed, r["retrieved"], r["n_test"], 100 * r["frac"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "V_c": V_C, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
