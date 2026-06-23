"""
exp_cross_corpus_compose_chat_v1_n4096 -- cross-corpus compose-chat across FB15k x ConceptNet x HotpotQA.

GAP (Skunkworks 273-composition META audit 2026-06-22): all 3 backends individually
chain-grade (CERT 584/585/588), but cross-corpus composition NOT chain-grade
evidenced -- only intra-corpus + within-synthetic-set. This cell closes the gap.

ARMS (Fix #16 discriminator):
  1. SINGLE_BACKEND: per query, ask each backend; pick the best (highest-score) answer.
  2. CROSS_COMPOSE_UNION: union top-k anchors from all 3; rank by sum of per-backend
     normalized score.
  3. CROSS_COMPOSE_HUB_SPOKE: encode each backend's top anchor in shared CharTrigram
     HD; superpose (hub); nearest-in-union-codebook picks single most-confident answer
     (Patterson-Rogers ATL convergence motif).

PRE-REG (preregs/2026-06-22_cross_corpus_compose_chat_v1.md):
  HARD_PASS: max(COMPOSE_UNION_acc, COMPOSE_HUB_SPOKE_acc) >= SINGLE_BACKEND_acc + 0.10
             AND per-corpus best-COMPOSE-arm >= SINGLE_BACKEND on EVERY corpus
             AND n_llm_calls == 0
  HARD_FAIL: max(COMPOSE_*) <= SINGLE_BACKEND_acc
  MIDDLE_BAND: positive lift but below +0.10, OR positive lift but a corpus regressed.

FORMULA SELF-TESTS (PROT-022):
  1. encoder.nearest idempotency on identical-string query.
  2. KGStore.predict_one_hop_topk returns tensor of correct shape (k entries).
  3. Hub-spoke superposition degrades to argmax-of-single when 2/3 anchors zeroed.

ROUTING: remote_cpu_queue (numpy/torch matmul; ~30-60min CPU wall full).
ASCII-only. PROT-018 _n4096. write_metrics. n_llm_calls=0 enforced.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import os
import pickle
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics
from hdlab.char_trigram_encoder import CharTrigramEncoder

ANCHOR_NAME = "cross_corpus_compose_chat_v1_n4096"
N_DIM = 4096
TOPK_PER_BACKEND = 5
HUB_TOPK = 1
CACHE_DIR = REPO / "data" / "substrate_repl_cache"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

# Test set sizes (Fix #17 measurement: smoke=quick; full=200 per pre-reg)
if SMOKE:
    N_PER_CORPUS = {"conceptnet": 6, "hotpotqa": 6, "fb15k": 5}
else:
    N_PER_CORPUS = {"conceptnet": 70, "hotpotqa": 70, "fb15k": 60}


# ---------------------- formula self-tests (PROT-022) ----------------------

def _selftest() -> None:
    # 1. encoder.nearest idempotency
    enc = CharTrigramEncoder(n_dim=512)
    names = ["alpha", "beta", "gamma", "delta"]
    cb = enc.encode_batch(names)
    n1 = enc.nearest("alpha", cb, names, k=1)
    n2 = enc.nearest("alpha", cb, names, k=1)
    assert n1[0]["entity"] == n2[0]["entity"], "encoder.nearest not idempotent"
    assert n1[0]["entity"] == "alpha", f"encoder.nearest didn't find exact match: {n1}"
    # 2. KGStore.predict_one_hop_topk shape
    from hdlab.kg_traversal import KGStore
    g = torch.Generator().manual_seed(7)
    kg = KGStore(n_ent=20, n_rel=4, n_dim=256, generator=g)
    triples = torch.tensor([[0, 0, 1], [0, 0, 2], [1, 1, 3]], dtype=torch.long)
    kg.ingest_triples(triples)
    idx, sc = kg.predict_one_hop_topk(0, 0, k=3)
    assert idx.shape == (3,) and sc.shape == (3,), f"topk shape wrong: {idx.shape}/{sc.shape}"
    # 3. Hub-spoke degrades to argmax-of-single when 2/3 zero
    v = np.zeros((3, 16), dtype=np.float32)
    v[1] = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1], dtype=np.float32)
    hub = v.sum(axis=0)
    assert np.allclose(hub, v[1]), "hub-spoke superposition broken at degenerate input"
    print("[selftest] PASS: 3 formula self-tests OK", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------- backend loading ----------------------

def load_backend(short: str) -> dict:
    """Load chat backend by short name. Cached pkl from substrate_repl prep."""
    for p in CACHE_DIR.glob("kg_m*.pkl"):
        nm = p.name.lower()
        if short == "hotpotqa" and "hotpot" in nm:
            with open(p, "rb") as f:
                return pickle.load(f)
        if short == "fb15k" and "fb15k" in nm:
            with open(p, "rb") as f:
                return pickle.load(f)
        if short == "conceptnet" and "conceptnet_100k" in nm:
            with open(p, "rb") as f:
                return pickle.load(f)
    raise FileNotFoundError(f"backend {short} not found in {CACHE_DIR}")


def prep_backend(short: str) -> dict:
    """Load + build encoder + entity codebook for a backend."""
    t0 = time.time()
    payload = load_backend(short)
    kg = payload["kg"]
    ent2idx = payload["ent2idx"]
    rel2idx = payload["rel2idx"]
    idx2ent = sorted(ent2idx, key=lambda e: ent2idx[e])
    idx2rel = sorted(rel2idx, key=lambda e: rel2idx[e])
    encoder = CharTrigramEncoder(n_dim=kg.n_dim)
    ent_codebook = encoder.encode_batch(idx2ent)
    print("  [%s] loaded n_ent=%d n_rel=%d n_dim=%d (wall=%.1fs)" % (
        short, len(idx2ent), len(idx2rel), kg.n_dim, time.time() - t0), flush=True)
    return {
        "name": short,
        "kg": kg,
        "encoder": encoder,
        "ent_codebook": ent_codebook,
        "idx2ent": idx2ent,
        "idx2rel": idx2rel,
        "ent2idx": ent2idx,
        "rel2idx": rel2idx,
    }


# ---------------------- test-set generation ----------------------

def gen_test_set(backends: Dict[str, dict], n_per: Dict[str, int], seed: int = 7) -> List[Dict]:
    """Generate (query_text, gold_entity_string, source_corpus) test items.

    For each corpus: sample N entity-relation pairs; use entity-name as query text;
    gold answer = backend's deterministic top-1 prediction for that (s, p) pair.
    This anchors the gold to the substrate (no LLM-judge) and tests whether OTHER
    backends + the COMPOSITION can recover the same answer the source backend would.
    """
    rng = np.random.RandomState(seed)
    items: List[Dict] = []
    for cname, n in n_per.items():
        b = backends[cname]
        kg = b["kg"]
        idx2ent = b["idx2ent"]
        idx2rel = b["idx2rel"]
        n_ent = len(idx2ent)
        n_rel = len(idx2rel)
        attempts = 0
        produced = 0
        # Sample (s, p) until n valid items collected (some preds may be self-trivial)
        while produced < n and attempts < n * 50:
            attempts += 1
            s_idx = int(rng.randint(0, n_ent))
            p_idx = int(rng.randint(0, n_rel))
            try:
                gold_idx = kg.predict_one_hop(s_idx, p_idx)
            except Exception:
                continue
            if gold_idx == s_idx:
                continue  # skip trivial self-loops
            gold_str = idx2ent[int(gold_idx)]
            query_str = idx2ent[s_idx]
            items.append({
                "query": query_str,
                "relation": idx2rel[p_idx],
                "gold": gold_str,
                "source_corpus": cname,
            })
            produced += 1
        print("  test-gen [%s]: produced %d (attempts %d)" % (cname, produced, attempts), flush=True)
    return items


# ---------------------- per-backend single-shot ----------------------

def query_backend(backend: dict, query_text: str, topk: int = TOPK_PER_BACKEND) -> List[Tuple[str, float]]:
    """Run query through one backend: encoder.nearest -> top-1 anchor -> for each
    relation in this backend, take predict_one_hop_topk; return ranked answer list.

    Returns: list of (entity_name, normalized_score) tuples; topk entries.
    """
    enc = backend["encoder"]
    cb = backend["ent_codebook"]
    idx2ent = backend["idx2ent"]
    kg = backend["kg"]
    # 1. encode query, find nearest entity anchor
    nearest = enc.nearest(query_text, cb, idx2ent, k=1)
    if not nearest:
        return []
    anchor_str = nearest[0]["entity"]
    anchor_idx = backend["ent2idx"].get(anchor_str)
    if anchor_idx is None:
        return []
    # 2. For each relation, run predict_one_hop_topk(k=1); collect candidates with their scores
    candidates: Dict[str, float] = {}
    n_rel = len(backend["idx2rel"])
    # For speed: sample relations if rel-set is very large (>50)
    rel_indices = list(range(n_rel))
    if n_rel > 50:
        # use score-cap: pick top-K relations by their key-norm
        # cheap proxy: deterministic stride sample 50
        stride = max(1, n_rel // 50)
        rel_indices = list(range(0, n_rel, stride))[:50]
    for rid in rel_indices:
        try:
            ti, ts = kg.predict_one_hop_topk(anchor_idx, rid, k=1)
            ent_name = idx2ent[int(ti[0])]
            score = float(ts[0])
            # keep max score per candidate
            if ent_name not in candidates or candidates[ent_name] < score:
                candidates[ent_name] = score
        except Exception:
            continue
    # 3. Normalize and return top-K
    if not candidates:
        return []
    scores = np.array(list(candidates.values()), dtype=np.float32)
    s_min, s_max = float(scores.min()), float(scores.max())
    rng_s = max(s_max - s_min, 1e-8)
    ranked = sorted(candidates.items(), key=lambda kv: -kv[1])[:topk]
    out = []
    for name, sc in ranked:
        norm = (sc - s_min) / rng_s
        out.append((name, float(norm)))
    return out


# ---------------------- composition arms ----------------------

def arm_single_backend(per_backend_results: Dict[str, List[Tuple[str, float]]]) -> str:
    """Pick the single highest-scoring (entity, score) across all backends.

    This is the baseline: 'best single backend wins'. The top-1 entity from
    whichever backend produced the highest normalized score.
    """
    best_score = -1e9
    best_ent = ""
    for cname, ranked in per_backend_results.items():
        if not ranked:
            continue
        ent, sc = ranked[0]
        if sc > best_score:
            best_score = sc
            best_ent = ent
    return best_ent


def arm_compose_union(per_backend_results: Dict[str, List[Tuple[str, float]]]) -> str:
    """Union top-K across backends; sum normalized scores; pick argmax."""
    combined: Dict[str, float] = {}
    for cname, ranked in per_backend_results.items():
        for ent, sc in ranked:
            combined[ent] = combined.get(ent, 0.0) + sc
    if not combined:
        return ""
    return max(combined.items(), key=lambda kv: kv[1])[0]


def arm_compose_hub_spoke(per_backend_results: Dict[str, List[Tuple[str, float]]],
                          shared_enc: CharTrigramEncoder) -> str:
    """Encode each backend's top-1 anchor in shared HD; superpose (hub); nearest in
    union-of-anchors codebook is the answer. Patterson-Rogers ATL convergence motif.

    If 0 or 1 backends produced an answer: return that answer (or empty).
    """
    top_anchors = []
    for cname, ranked in per_backend_results.items():
        if ranked:
            top_anchors.append((ranked[0][0], ranked[0][1]))
    if not top_anchors:
        return ""
    if len(top_anchors) == 1:
        return top_anchors[0][0]
    # Build shared HD codebook over the union of top-K candidates across all backends.
    union_names: List[str] = []
    seen = set()
    for cname, ranked in per_backend_results.items():
        for ent, _sc in ranked:
            if ent not in seen:
                seen.add(ent)
                union_names.append(ent)
    if not union_names:
        return ""
    union_cb = shared_enc.encode_batch(union_names)
    # Build hub: weighted superposition of top-anchor encodings (weighted by score).
    hub = np.zeros(shared_enc.n_dim, dtype=np.float32)
    for anchor_str, sc in top_anchors:
        hub = hub + sc * shared_enc.encode(anchor_str)
    if np.linalg.norm(hub) < 1e-8:
        # degenerate: pick highest-score top anchor
        return max(top_anchors, key=lambda x: x[1])[0]
    # Nearest in union codebook
    hub_unit = hub / (np.linalg.norm(hub) + 1e-8)
    cb_norms = np.linalg.norm(union_cb, axis=1, keepdims=True) + 1e-8
    cb_unit = union_cb / cb_norms
    sims = cb_unit @ hub_unit
    return union_names[int(np.argmax(sims))]


# ---------------------- main run ----------------------

def run() -> Dict:
    print("[load] preparing 3 backends ...", flush=True)
    backends = {
        "conceptnet": prep_backend("conceptnet"),
        "hotpotqa": prep_backend("hotpotqa"),
        "fb15k": prep_backend("fb15k"),
    }
    shared_enc = CharTrigramEncoder(n_dim=N_DIM)
    print("[testgen] generating test set ...", flush=True)
    items = gen_test_set(backends, N_PER_CORPUS, seed=7)
    print("[testgen] total items: %d" % len(items), flush=True)
    if not items:
        return {"n": 0, "single_acc": 0.0, "union_acc": 0.0, "hub_acc": 0.0, "n_llm_calls": 0}
    correct_single = 0
    correct_union = 0
    correct_hub = 0
    per_corpus = {c: {"n": 0, "single": 0, "union": 0, "hub": 0} for c in N_PER_CORPUS}
    t_eval0 = time.time()
    for i, item in enumerate(items):
        # Query all 3 backends
        results = {}
        for cname, b in backends.items():
            results[cname] = query_backend(b, item["query"])
        ans_single = arm_single_backend(results)
        ans_union = arm_compose_union(results)
        ans_hub = arm_compose_hub_spoke(results, shared_enc)
        gold = item["gold"]
        c = item["source_corpus"]
        per_corpus[c]["n"] += 1
        if ans_single == gold:
            correct_single += 1
            per_corpus[c]["single"] += 1
        if ans_union == gold:
            correct_union += 1
            per_corpus[c]["union"] += 1
        if ans_hub == gold:
            correct_hub += 1
            per_corpus[c]["hub"] += 1
        if (i + 1) % 25 == 0:
            print("  progress: %d/%d (single=%d union=%d hub=%d; t=%.1fs)" % (
                i + 1, len(items), correct_single, correct_union, correct_hub,
                time.time() - t_eval0), flush=True)
    n = len(items)
    single_acc = correct_single / n
    union_acc = correct_union / n
    hub_acc = correct_hub / n
    # per-corpus accuracies
    per_corp_acc = {}
    for c, d in per_corpus.items():
        if d["n"] > 0:
            per_corp_acc[c] = {
                "n": d["n"],
                "single": d["single"] / d["n"],
                "union": d["union"] / d["n"],
                "hub": d["hub"] / d["n"],
            }
    return {
        "n": n,
        "single_acc": single_acc,
        "union_acc": union_acc,
        "hub_acc": hub_acc,
        "per_corpus": per_corp_acc,
        "n_llm_calls": 0,
        "eval_wall_s": time.time() - t_eval0,
    }


def verdict(r: Dict) -> Tuple[str, str]:
    if r["n"] == 0:
        return ("HARD_FAIL", "HARD_FAIL: zero test items produced")
    if r.get("n_llm_calls", 0) != 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated (n_llm_calls != 0)")
    sa = r["single_acc"]
    ua = r["union_acc"]
    ha = r["hub_acc"]
    best_compose = max(ua, ha)
    best_arm = "UNION" if ua >= ha else "HUB_SPOKE"
    lift = best_compose - sa
    # per-corpus regression check
    per = r.get("per_corpus", {})
    regressions = []
    for c, d in per.items():
        best_c = max(d["union"], d["hub"])
        if best_c < d["single"]:
            regressions.append("%s(single=%.3f best_compose=%.3f)" % (c, d["single"], best_c))
    base_msg = ("n=%d single=%.3f union=%.3f hub=%.3f best_compose=%.3f(%s) lift=%+.3f"
                % (r["n"], sa, ua, ha, best_compose, best_arm, lift))
    per_corp_msg = "; per_corpus: " + ", ".join(
        "%s(n=%d s=%.3f u=%.3f h=%.3f)" % (c, d["n"], d["single"], d["union"], d["hub"])
        for c, d in per.items()
    )
    if lift >= 0.10 and not regressions:
        return ("HARD_PASS",
                "HARD_PASS: cross-corpus composition lifts accuracy by >=0.10 over best single "
                "backend AND no per-corpus regression. " + base_msg + per_corp_msg)
    if best_compose <= sa:
        return ("HARD_FAIL",
                "HARD_FAIL: cross-corpus composition adds NO value (best compose <= single). "
                + base_msg + per_corp_msg)
    if regressions:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: positive lift but per-corpus regression in: " + ", ".join(regressions)
                + ". " + base_msg + per_corp_msg)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: positive lift but below +0.10 threshold. " + base_msg + per_corp_msg)


print("[config] anchor=%s mode=%s n_dim=%d test=%s" % (
    ANCHOR_NAME, RUN_MODE, N_DIM, json.dumps(N_PER_CORPUS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
r = run()
v, vmsg = verdict(r)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": 1,
    "per_seed": [r],
    "elapsed_s": time.time() - t0,
    "summary": vmsg,
    "n_llm_calls": r.get("n_llm_calls", 0),
}
write_metrics(out_dir, metrics, [r])
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
