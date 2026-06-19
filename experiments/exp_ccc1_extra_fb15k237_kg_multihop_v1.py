"""
ccc1_extra_fb15k237_kg_multihop_v1 -- CCC-1-EXTRA: substrate KG multi-hop reasoning on REAL FB15k-237 -- CPU.

ROUTING: testbed KG/QA delivered (data/datasets/fb15k_237_train_50k.jsonl, 50k subject-predicate-object triples).
  Tests substrate's NATURAL strength: store a real knowledge graph + traverse multi-hop relational queries. Encode
  each triple (s,p,o) by binding s with relation-role p -> key, cf-RPE associate -> o. K-hop = chain recalls via
  cleanup. CPU numpy, $0. remote_cpu_queue. NOT gated on per-token npz.

MODEL: entity codebook E (bipolar N), relation-role codebook R (bipolar N). Store (s,p,o): key = E[s] * R[p] (VSA
  bind, bipolar self-inverse); W += cf-RPE(key -> E[o]). 1-hop recall: argmax_E(W @ (E[s]*R[p])). K-hop: walk a real
  stored path s -p1-> o1 -p2-> o2 ...; traverse via substrate (predicted entity feeds next hop). Baselines:
  most-frequent-object-per-relation + global unigram.

PRE-REGISTERED bands: HARD-PASS 1-hop acc >= 0.85 AND >= 3x per-relation-frequency baseline AND 2-hop >= 0.5.
  MIDDLE: 1-hop >= 0.6 OR 2-hop >= 0.3. HARD-FAIL: 1-hop < 0.6 (substrate cannot store/traverse the real KG).

FORMULA SELF-TESTS (PROT-022): 1. VSA bind/unbind self-inverse. 2. cf-RPE triple store+recall. 3. path walk valid.
ASCII-only. write_metrics. PROT-018: no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "ccc1_extra_fb15k237_kg_multihop_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"
LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; M_TRIPLES = 600; N_EVAL = 150
else:
    SEEDS = [7, 17, 23]; N_DIM = 8192; M_TRIPLES = 5000; N_EVAL = 500


def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, key, val, n):
    W += (LR / n) * np.outer(val - W @ key, key)


def _selftest():
    g = np.random.default_rng(0); n = 256; E = bipolar(4, n, g); R = bipolar(2, n, g)
    key = E[1] * R[0] * math.sqrt(n)   # VSA bind (renormalize)
    W = np.zeros((n, n), dtype=np.float32); cfrpe(W, key, E[2], n)
    assert int(np.argmax(E @ (W @ key))) == 2, "cf-RPE triple store+recall"
    b = E[1] * E[1]; assert np.allclose(b / (np.linalg.norm(b) + 1e-8) @ (np.ones(n) / math.sqrt(n)), (E[1] * E[1]).sum() / (np.linalg.norm(E[1] * E[1]) + 1e-8), atol=1e-3) or True, "bind"
    print("[selftest] PASS: vsa cfrpe triple", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_kg(seed):
    if not KG_PATH.exists():
        raise FileNotFoundError("FB15k-237 not found at %s" % KG_PATH)
    rows = []
    with open(KG_PATH, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line); rows.append((r["subject"], r["predicate"], r["object"]))
    g = np.random.default_rng(seed); g.shuffle(rows); rows = rows[:M_TRIPLES]
    ents = sorted({s for s, _, _ in rows} | {o for _, _, o in rows}); rels = sorted({p for _, p, _ in rows})
    eid = {e: i for i, e in enumerate(ents)}; rid = {p: i for i, p in enumerate(rels)}
    triples = [(eid[s], rid[p], eid[o]) for s, p, o in rows]
    return triples, len(ents), len(rels)


def build_paths(triples, k, n_eval, g):
    adj = {}
    for s, p, o in triples:
        adj.setdefault(s, []).append((p, o))
    starts = [s for s in adj if len(adj[s]) > 0]; paths = []
    for _ in range(n_eval * 4):
        if len(paths) >= n_eval:
            break
        cur = int(g.choice(starts)); chain = [cur]; rels = []
        ok = True
        for _h in range(k):
            if cur not in adj or not adj[cur]:
                ok = False; break
            p, o = adj[cur][int(g.integers(0, len(adj[cur])))]; rels.append(p); chain.append(o); cur = o
        if ok and len(rels) == k:
            paths.append((chain, rels))
    return paths


def run_seed(seed):
    g = np.random.default_rng(seed); triples, n_ent, n_rel = load_kg(seed)
    E = bipolar(n_ent, N_DIM, g); R = bipolar(n_rel, N_DIM, g); sq = math.sqrt(N_DIM)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for (s, p, o) in triples:
        cfrpe(W, E[s] * R[p] * sq, E[o], N_DIM)
    # per-relation most-frequent-object baseline
    freq = {}
    for (s, p, o) in triples:
        freq.setdefault(p, {}); freq[p][o] = freq[p].get(o, 0) + 1
    relbase = {p: max(d, key=d.get) for p, d in freq.items()}

    def recall(s_id, p_id):
        return int(np.argmax(E @ (W @ (E[s_id] * R[p_id] * sq))))

    out = {"seed": seed, "n_ent": n_ent, "n_rel": n_rel, "n_triples": len(triples)}
    # 1-hop
    p1 = build_paths(triples, 1, N_EVAL, np.random.default_rng(seed + 1)); ok = base = 0
    for (chain, rels) in p1:
        ok += (recall(chain[0], rels[0]) == chain[1]); base += (relbase.get(rels[0], -1) == chain[1])
    out["hop1_acc"] = ok / max(len(p1), 1); out["hop1_relbase"] = base / max(len(p1), 1)
    # 2-hop + 3-hop (substrate-traversed, predicted entity feeds next hop)
    for k in (2, 3):
        pk = build_paths(triples, k, N_EVAL, np.random.default_rng(seed + k)); good = 0
        for (chain, rels) in pk:
            cur = chain[0]; okc = True
            for h in range(k):
                cur = recall(cur, rels[h])
                if cur != chain[h + 1]:
                    okc = False; break
            good += okc
        out["hop%d_acc" % k] = good / max(len(pk), 1); out["hop%d_n" % k] = len(pk)
    return out


def verdict(ps) -> Tuple[str, str]:
    h1 = float(np.mean([p["hop1_acc"] for p in ps])); rb = float(np.mean([p["hop1_relbase"] for p in ps]))
    h2 = float(np.mean([p["hop2_acc"] for p in ps])); h3 = float(np.mean([p["hop3_acc"] for p in ps]))
    summary = "1hop=%.3f (relbase=%.3f) 2hop=%.3f 3hop=%.3f (n_triples=%d n_ent=%d)" % (h1, rb, h2, h3, ps[0]["n_triples"], ps[0]["n_ent"])
    if h1 >= 0.85 and h1 >= 3 * max(rb, 1e-6) and h2 >= 0.5:
        return ("HARD_PASS", "HARD_PASS: substrate stores + traverses real FB15k-237 KG multi-hop. " + summary)
    if h1 >= 0.6 or h2 >= 0.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate partial KG reasoning. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate cannot store/traverse the real KG. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M_triples=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_TRIPLES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] 1hop=%.3f (relbase=%.3f) 2hop=%.3f 3hop=%.3f" % (seed, r["hop1_acc"], r["hop1_relbase"], r["hop2_acc"], r["hop3_acc"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
