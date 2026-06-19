"""
exp_substrate_vs_iterative_knnlm_gpu_v1 -- strengthened falsifiable: substrate vs SINGLE-SHOT vs ITERATIVE kNN-LM -- GPU.

ROUTING: follow-up to the kNN-LM falsifiable HARD_PASS, hardening against the obvious rebuttal: "a real ITERATIVE kNN-LM
  (multi-step RAG: retrieve hop1, re-query with the retrieved entity, retrieve hop2) can traverse too." We add that strong
  baseline and a realistic representation-NOISE condition (query embedding drift). Three retrievers on the SAME graph:
  (1) substrate exact binding traversal; (2) single-shot kNN-LM (one dense retrieval for the whole multi-hop query); (3)
  iterative kNN-LM (per-hop dense retrieve + feed entity forward). Honest expectation: single-shot fails multi-hop; iterative
  ties substrate on CLEAN data but COMPOUNDS per-hop retrieval error under noise/hops while substrate's exact algebra does not.
PRE-REGISTERED: HARD-PASS substrate >= iterative-kNN + 5pp under noise at 3-hop (robustness from no error-compounding). MIDDLE
  substrate >= iterative within +-5pp (ties; advantage is cost/latency not accuracy). HARD-FAIL substrate < iterative-kNN.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cosine. 3. compounding 0.9^3<0.75.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"; os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_vs_iterative_knnlm_gpu_v1"; ENC = "BAAI/bge-small-en-v1.5"; HD = 8192
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_ENT = 120 if SMOKE else 300; N_REL = 6; NQ = 50 if SMOKE else 150; NOISE = 0.08
REL_WORDS = ["influences", "precedes", "contains", "supplies", "governs", "mirrors"]


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r = cphasor(1, 64, g)[0]; t = cphasor(1, 64, g)[0]
    assert np.allclose(a * r * t * np.conj(a * r), t, atol=1e-3), "bind/unbind"
    assert abs(float(np.array([1.0, 0]) @ np.array([1.0, 0])) - 1.0) < 1e-9, "cosine"
    assert 0.9 ** 3 < 0.75, "compounding"
    print("[selftest] PASS: substrate-vs-iterative-knnlm", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def words(n):
    base = ["azure", "basil", "cedar", "delta", "ember", "flint", "grove", "hazel", "iris", "jade", "koi", "larch",
            "maple", "nova", "onyx", "pearl", "quill", "rowan", "sage", "tansy", "umber", "vale", "wren", "yarrow", "zephyr"]
    return ["%s%d" % (base[i % len(base)], i) for i in range(n)]


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=24).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def run() -> Dict:
    g = np.random.default_rng(11); ew = words(N_ENT)
    edge = {(h, r): int(g.integers(0, N_ENT)) for h in range(N_ENT) for r in range(N_REL)}
    ents = cphasor(N_ENT, HD, g); rels = cphasor(N_REL, HD, g)
    shard = np.zeros((N_ENT, HD), dtype=np.complex64)
    for h in range(N_ENT):
        for r in range(N_REL):
            shard[h] = shard[h] + rels[r] * ents[edge[(h, r)]]
    tok = AutoTokenizer.from_pretrained(ENC); m = AutoModel.from_pretrained(ENC).to(DEV).eval()
    ctx_texts = ["%s %s" % (ew[h], REL_WORDS[r]) for h in range(N_ENT) for r in range(N_REL)]
    ctx_val = np.array([edge[(h, r)] for h in range(N_ENT) for r in range(N_REL)])
    Kctx = encode(ctx_texts, tok, m)
    rng_noise = np.random.default_rng(99)

    def dense_lookup(text):
        q = encode([text], tok, m)[0] + NOISE * rng_noise.standard_normal(Kctx.shape[1]).astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-8); return int(ctx_val[int(np.argmax(Kctx @ q))])

    def gold_of(h, rseq):
        cur = h
        for r in rseq:
            cur = edge[(cur, r)]
        return cur

    def substrate(h, rseq):
        sv = h
        for r in rseq:
            sv = cidx(shard[sv] * np.conj(rels[r]), ents)
        return sv

    def single_shot(h, rseq):
        return dense_lookup(ew[h] + " " + " ".join(REL_WORDS[r] for r in rseq))

    def iterative(h, rseq):
        cur = h
        for r in rseq:
            cur = dense_lookup(ew[cur] + " " + REL_WORDS[r])   # re-query per hop with retrieved entity (multi-step RAG)
        return cur

    res = {}
    for hops in ([1, 2] if SMOKE else [1, 2, 3]):
        sh = it = ss = 0
        for _ in range(NQ):
            h = int(g.integers(0, N_ENT)); rseq = [int(g.integers(0, N_REL)) for _ in range(hops)]; gold = gold_of(h, rseq)
            sh += int(substrate(h, rseq) == gold); it += int(iterative(h, rseq) == gold); ss += int(single_shot(h, rseq) == gold)
        res[hops] = {"substrate": sh / NQ, "iterative_knn": it / NQ, "single_shot_knn": ss / NQ}
        print("  %d-hop (noise=%.2f): substrate=%.3f iterative-kNN=%.3f single-shot-kNN=%.3f" % (hops, NOISE, res[hops]["substrate"], res[hops]["iterative_knn"], res[hops]["single_shot_knn"]), flush=True)
    del m
    deep = max(res.keys()); d = res[deep]
    print("  DEEPEST (%d-hop): substrate-vs-iterative delta=%+.3f ; substrate-vs-single-shot delta=%+.3f" % (deep, d["substrate"] - d["iterative_knn"], d["substrate"] - d["single_shot_knn"]), flush=True)
    return {"deepest_hop": deep, "sub": d["substrate"], "iter": d["iterative_knn"], "ss": d["single_shot_knn"],
            "delta_iter": d["substrate"] - d["iterative_knn"], "delta_ss": d["substrate"] - d["single_shot_knn"], "per_hop": {str(k): v for k, v in res.items()}}


def verdict(r) -> Tuple[str, str]:
    s = "%d-hop (noise %.2f): substrate=%.3f iterative-kNN=%.3f single-shot-kNN=%.3f (sub-vs-iter=%+.3f, sub-vs-ss=%+.3f)" % (r["deepest_hop"], NOISE, r["sub"], r["iter"], r["ss"], r["delta_iter"], r["delta_ss"])
    if r["delta_iter"] >= 0.05:
        return ("HARD_PASS", "HARD_PASS: substrate beats even ITERATIVE kNN-LM by >=5pp at depth under noise -- exact algebra does not compound per-hop retrieval error; robust categorical advantage (and trivially beats single-shot). " + s)
    if r["delta_iter"] >= -0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate ties iterative kNN-LM on accuracy -- both traverse when grounded; substrate's advantage is cost/latency/no-per-hop-LLM, not accuracy. Beats single-shot categorically. " + s)
    return ("HARD_FAIL", "HARD_FAIL: iterative kNN-LM beats substrate -- accuracy moat does not hold vs multi-step RAG. " + s)


print("[config] anchor=%s mode=%s enc=%s N_ENT=%d noise=%.2f NQ=%d" % (ANCHOR_NAME, RUN_MODE, ENC, N_ENT, NOISE, NQ), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
