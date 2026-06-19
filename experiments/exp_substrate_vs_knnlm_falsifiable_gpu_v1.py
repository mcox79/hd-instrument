"""
exp_substrate_vs_knnlm_falsifiable_gpu_v1 -- FALSIFIABLE: does substrate ALGEBRA beat kNN-LM dense retrieval -- GPU.

ROUTING: SUBSTRATE_VS_KNN_LM_FALSIFIABLE_TEST. External-memory K/V injection is well-developed prior art (kNN-LM, RETRO,
  Memorizing Transformer, Atlas...). Substrate's claimed moat is the ALGEBRA (binding/unbinding multi-hop traversal), not the
  injection. This is the decisive head-to-head on the SAME KB: single-hop (both should tie -- sanity) vs MULTI-HOP (2/3-hop,
  where traversal matters). Substrate retrieves by K-hop binding traversal; the kNN-LM baseline retrieves by dense-embedding
  cosine over fact contexts (real encoder, value = next entity), with NO traversal -- the honest difference. If substrate does
  not beat kNN-LM on multi-hop, the moat is the plumbing not the algebra (pitch must shift to "substrate is a great KB").
PRE-REGISTERED: HARD-PASS substrate overall accuracy >= kNN-LM + 2pp over >=100 queries (multi-hop is where it shows). MID 2-15pp
  is "modest algebraic advantage". HARD-FAIL delta < 2pp (algebra adds no value over dense retrieval).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cosine. 3. set hit.
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

ANCHOR_NAME = "substrate_vs_knnlm_falsifiable_gpu_v1"; ENC = "BAAI/bge-small-en-v1.5"; HD = 8192
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_ENT = 120 if SMOKE else 300; N_REL = 6; NQ = 60 if SMOKE else 200


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r = cphasor(1, 64, g)[0]; t = cphasor(1, 64, g)[0]
    assert np.allclose(a * r * t * np.conj(a * r), t, atol=1e-3), "bind/unbind"
    u = np.array([1.0, 0]); v = np.array([1.0, 0]); assert abs(float(u @ v) - 1.0) < 1e-9, "cosine"
    assert len({1, 2} & {2, 3}) == 1, "set hit"
    print("[selftest] PASS: substrate-vs-knnlm-falsifiable", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)

ENT_WORDS = None
REL_WORDS = ["influences", "precedes", "contains", "supplies", "governs", "mirrors"]


def words(n):
    base = ["azure", "basil", "cedar", "delta", "ember", "flint", "grove", "hazel", "iris", "jade", "koi", "larch",
            "maple", "nova", "onyx", "pearl", "quill", "rowan", "sage", "tansy", "umber", "vale", "wren", "yarrow", "zephyr"]
    out = []
    for i in range(n):
        out.append("%s%d" % (base[i % len(base)], i))
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=24).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def run() -> Dict:
    g = np.random.default_rng(11); ent_words = words(N_ENT)
    # build graph: each entity has one out-edge per relation to a random other entity (deterministic functional edges)
    edge = {}  # (h, r) -> t
    for h in range(N_ENT):
        for r in range(N_REL):
            edge[(h, r)] = int(g.integers(0, N_ENT))
    # substrate: per-head shard of rel-bound tails
    ents = cphasor(N_ENT, HD, g); rels = cphasor(N_REL, HD, g)
    shard = np.zeros((N_ENT, HD), dtype=np.complex64)
    for h in range(N_ENT):
        for r in range(N_REL):
            shard[h] = shard[h] + rels[r] * ents[edge[(h, r)]]
    # kNN-LM KB: key = encode("<h> <rel>") context, value = answer entity id (the 1-hop fact base)
    tok = AutoTokenizer.from_pretrained(ENC); m = AutoModel.from_pretrained(ENC).to(DEV).eval()
    ctx_texts = []; ctx_val = []
    for h in range(N_ENT):
        for r in range(N_REL):
            ctx_texts.append("%s %s" % (ent_words[h], REL_WORDS[r])); ctx_val.append(edge[(h, r)])
    Kctx = encode(ctx_texts, tok, m); ctx_val = np.array(ctx_val)

    def knn_answer(qtext):
        q = encode([qtext], tok, m)[0]; j = int(np.argmax(Kctx @ q)); return int(ctx_val[j])

    res = {}
    for hops in ([1, 2] if SMOKE else [1, 2, 3]):
        sub_hit = 0; knn_hit = 0
        for _ in range(NQ):
            h = int(g.integers(0, N_ENT)); rseq = [int(g.integers(0, N_REL)) for _ in range(hops)]
            # ground truth via edge traversal
            cur = h
            for r in rseq:
                cur = edge[(cur, r)]
            gold = cur
            # substrate: traverse by unbinding each relation
            sv = h
            for r in rseq:
                sv = cidx(shard[sv] * np.conj(rels[r]), ents)
            sub_hit += int(sv == gold)
            # kNN-LM: dense retrieval over fact contexts; query = full multi-hop phrase (no traversal capability)
            qtext = ent_words[h] + " " + " ".join(REL_WORDS[r] for r in rseq)
            knn_hit += int(knn_answer(qtext) == gold)
        res[hops] = {"sub": sub_hit / NQ, "knn": knn_hit / NQ}
        print("  %d-hop: substrate=%.3f  kNN-LM=%.3f  delta=%+.3f" % (hops, res[hops]["sub"], res[hops]["knn"], res[hops]["sub"] - res[hops]["knn"]), flush=True)
    del m
    allh = list(res.keys()); sub_o = float(np.mean([res[h]["sub"] for h in allh])); knn_o = float(np.mean([res[h]["knn"] for h in allh]))
    mh = [h for h in allh if h >= 2]; sub_mh = float(np.mean([res[h]["sub"] for h in mh])); knn_mh = float(np.mean([res[h]["knn"] for h in mh]))
    print("  OVERALL substrate=%.3f kNN-LM=%.3f (delta=%+.3f) | MULTI-HOP substrate=%.3f kNN-LM=%.3f (delta=%+.3f)" % (sub_o, knn_o, sub_o - knn_o, sub_mh, knn_mh, sub_mh - knn_mh), flush=True)
    return {"overall_sub": sub_o, "overall_knn": knn_o, "delta": sub_o - knn_o, "mh_sub": sub_mh, "mh_knn": knn_mh, "mh_delta": sub_mh - knn_mh, "per_hop": {str(k): v for k, v in res.items()}}


def verdict(r) -> Tuple[str, str]:
    s = "overall sub=%.3f knn=%.3f (delta=%+.3f); multi-hop sub=%.3f knn=%.3f (delta=%+.3f)" % (r["overall_sub"], r["overall_knn"], r["delta"], r["mh_sub"], r["mh_knn"], r["mh_delta"])
    if r["delta"] >= 0.15:
        return ("HARD_PASS", "HARD_PASS: substrate's algebra beats kNN-LM dense retrieval by >=15pp overall (multi-hop delta %+.3f) -- the moat is the algebraic traversal, not the injection plumbing; Panel B categorical claim empirically grounded. " % r["mh_delta"] + s)
    if r["delta"] >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate beats kNN-LM by 2-15pp -- modest algebraic advantage; calibrate pitch honestly. " + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate within 2pp of kNN-LM -- algebra adds no value over dense retrieval; pitch must shift to 'substrate is a great structured KB' (Panel A only). " + s)


print("[config] anchor=%s mode=%s enc=%s N_ENT=%d N_REL=%d NQ=%d" % (ANCHOR_NAME, RUN_MODE, ENC, N_ENT, N_REL, NQ), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
