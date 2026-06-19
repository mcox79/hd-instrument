"""
exp_semantic_a_v2_multifield_rrf_gpu_v1.py -- Semantic-A v2 Multi-field RRF prototype (Research drill: semantic-A beyond bge cosine).

Builds on the fixed semantic-A finding (bge description+aliases best-k=8 F1=0.369 vs keyword 0.185). Research drill rank-1: bge encodes
only the description(+aliases) text; substrate atoms carry MORE structured fields the default retriever ignores. Reciprocal Rank Fusion
(Cormack 2009) over multiple per-field bge rankings should lift A-axis recall (drill projection 0.369 -> 0.43 +/- 0.04).

READ-ONLY PROTOTYPE: encodes fields in-memory + measures A-axis F1; does NOT write a cached index to the (Testbed-owned) store. The
production cached Multi-field RRF lives in tools/substrate_benchmark.py (Testbed). This cell gives a go/no-go signal + per-field
ablation before that build.

Fields (each bge-encoded separately, then RRF-fused):
  desc   : description + aliases       (= the current 0.369 baseline signal)
  idtok  : id token-decomposition      (e.g. "T3/discriminative_perceptron" -> "discriminative perceptron") -- strong untapped signal
  name   : atom.name
  serves : serves_capability ids (sparse)

Metric: A-axis set-overlap F1 (canonical), per single-field + the RRF fusion, vs the 0.369 desc-only baseline + keyword 0.185.
Pre-reg (per drill): HP RRF A-F1 >= 0.43 + beats desc-only by >= +0.04; MIDDLE +0.02-0.04; FAIL < +0.02 (RRF saturates -> desc dominates).

GPU (bge-large). Runs on the revived home runner. --self-test + --smoke + write_metrics. No LLM-judge.
"""
from __future__ import annotations
import json, os, re, sys, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "semantic_a_v2_multifield_rrf_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELF_TEST = "--self-test" in sys.argv
KS = [5, 8, 12]
RRF_C = 60
FIELDS = ["desc", "idtok", "name", "serves"]


def _norm(s):
    return s.split("::", 1)[1] if "::" in s else s


def _f1(r, g):
    if not g:
        return 1.0 if not r else 0.0
    if not r:
        return 0.0
    tp = len(r & g)
    if tp == 0:
        return 0.0
    p = tp / len(r); rc = tp / len(g)
    return 2 * p * rc / (p + rc)


def _id_tokens(aid):
    leaf = aid.split("::", 1)[-1]
    leaf = re.sub(r"^(T\d|LEX\w*|CAP|RULE|CROSSDISC|RETRIEVAL)/", "", leaf)  # drop leading tier/kind segment
    return re.sub(r"[/_\-.]+", " ", leaf).strip()


def _field_text(a, field):
    if field == "desc":
        t = a.description or ""
        if getattr(a, "aliases", None):
            t = t + " " + " ".join(a.aliases)
        return t or a.id
    if field == "idtok":
        return _id_tokens(a.id)
    if field == "name":
        return getattr(a, "name", "") or _id_tokens(a.id)
    if field == "serves":
        sc = getattr(a, "serves_capability", None) or ()
        return " ".join(_id_tokens(x) for x in sc) if sc else ""
    return ""


def _rrf(rank_lists, ids, c=RRF_C):
    """rank_lists: list of arrays of atom-index order (best first). Returns RRF score per atom index."""
    n = len(ids)
    score = np.zeros(n, dtype=np.float64)
    for order in rank_lists:
        ranks = np.empty(n, dtype=np.int64)
        ranks[order] = np.arange(n)
        score += 1.0 / (c + ranks)
    return score


def run():
    from sentence_transformers import SentenceTransformer
    from backend.substrate_index.partition import PartitionedStore
    idx = REPO / "data" / "substrate_index"
    bench_fp = idx / "benchmark_corpus_v2_60q.jsonl"
    if not bench_fp.exists():
        return {"error": "no_canonical_benchmark"}
    bench = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    A = [q for q in bench if q.get("type", "").startswith("A") and q.get("answerable", True)]
    ps = PartitionedStore(idx); atoms = ps.all_atoms()
    if SMOKE:
        atoms = atoms[:300]
    ids = [_norm(a.id) for a in atoms]
    allids = set(ids)
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    # per-field atom embedding matrices (L2-normalized)
    field_emb = {}
    field_has = {}
    for f in FIELDS:
        texts = [_field_text(a, f) for a in atoms]
        field_has[f] = np.array([1.0 if t.strip() else 0.0 for t in texts])
        emb = model.encode([t if t.strip() else " " for t in texts], normalize_embeddings=True,
                           batch_size=64, show_progress_bar=False)
        field_emb[f] = np.asarray(emb, dtype=np.float32)
    per_field = {f: {} for f in FIELDS}
    rrf_per_k = {}
    desc_per_k = {}
    for K in KS:
        f1_rrf = []; f1_desc = []
        f1_field = {f: [] for f in FIELDS}
        for q in A:
            m = re.search(r"about (.+?)\s*\??$", q["question"], re.I)
            topic = m.group(1) if m else q["question"]
            gold = {_norm(g) for g in q.get("ground_truth_atoms", []) if _norm(g) in allids}
            qv = np.asarray(model.encode([topic], normalize_embeddings=True)[0], dtype=np.float32)
            rank_lists = []
            for f in FIELDS:
                scores = field_emb[f] @ qv
                scores = np.where(field_has[f] > 0, scores, -2.0)  # absent field -> push down
                order = np.argsort(-scores)
                rank_lists.append(order)
                topf = {ids[i] for i in order[:K]}
                f1_field[f].append(_f1(topf, gold))
            # desc-only baseline
            f1_desc.append(f1_field["desc"][-1])
            # RRF fusion over all fields
            rrf = _rrf(rank_lists, ids)
            top_rrf = {ids[i] for i in np.argsort(-rrf)[:K]}
            f1_rrf.append(_f1(top_rrf, gold))
        rrf_per_k[K] = round(sum(f1_rrf) / len(f1_rrf), 4)
        desc_per_k[K] = round(sum(f1_desc) / len(f1_desc), 4)
        for f in FIELDS:
            per_field[f][K] = round(sum(f1_field[f]) / len(f1_field[f]), 4)
    best_k = max(rrf_per_k, key=rrf_per_k.get)
    return {"rrf_per_k": rrf_per_k, "desc_per_k": desc_per_k, "per_field_per_k": per_field,
            "best_k": best_k, "rrf_best": rrf_per_k[best_k], "desc_best": max(desc_per_k.values()),
            "keyword_baseline": 0.185, "n_A": len(A), "n_atoms": len(atoms)}


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rrf = r["rrf_best"]; desc = r["desc_best"]; lift = round(rrf - desc, 4)
    s = ("RRF best-k=%d F1=%.4f vs desc-only %.4f (lift %+.4f) vs keyword 0.185 | per-field best: %s | n_A=%d atoms=%d"
         % (r["best_k"], rrf, desc, lift,
            {f: max(r["per_field_per_k"][f].values()) for f in FIELDS}, r["n_A"], r["n_atoms"]))
    if rrf >= 0.43 and lift >= 0.04:
        return ("HARD_PASS", "HARD_PASS: Multi-field RRF lifts A-axis to >=0.43 (+>=0.04 over desc-only) -- substrate structured fields add retrieval signal bge-description-only ignores. " + s)
    if lift >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Multi-field RRF adds +0.02-0.04 on A-axis. " + s)
    return ("HARD_FAIL", "HARD_FAIL: Multi-field RRF lift <+0.02 -- description field dominates; extra fields don't add A-axis signal. " + s)


SMOKE = RUN_MODE == "smoke"


def _self_test():
    assert _id_tokens("math::T3/discriminative_perceptron") == "discriminative perceptron", _id_tokens("math::T3/discriminative_perceptron")
    assert _f1({"a", "b"}, {"a"}) == 2 * (0.5 * 1.0) / 1.5
    o = [np.array([2, 0, 1]), np.array([0, 1, 2])]
    sc = _rrf(o, ["x", "y", "z"])
    assert len(sc) == 3
    print("[self-test] PASS: id-token decomposition + F1 + RRF fusion")


if __name__ == "__main__":
    if SELF_TEST:
        _self_test(); sys.exit(0)
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
               "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written", flush=True)
