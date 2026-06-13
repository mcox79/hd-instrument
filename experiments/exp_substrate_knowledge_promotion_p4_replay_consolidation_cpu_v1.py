"""
exp_substrate_knowledge_promotion_p4_replay_consolidation_cpu_v1.py -- CELL KP path P4: sleep-replay consolidation -> T2 archetype candidates -- CPU/local (no heat, read-only).

ROUTING: Research ANCHOR 1 (exp_dev_handoff_research_optimal_external_corpus..._knowledge_promotion_mechanism_3x, Drill 3 / Prediction
  set 2). The KNOWLEDGE-PROMOTION operator has 5 substrate-only paths; P1 (frequency) already HARD_PASS (24 T3->T2 candidates). This
  cell implements PATH P4 (sleep-replay consolidation): the systems-consolidation analog -- "replay" the T3 EPISODIC atoms (re-encode
  each to its production identity vector), CLUSTER them by geometry, and a DENSE, COHERENT cluster (>= MIN_SIZE members, intra-cluster
  cosine clearly above the random-pair baseline) is an empirically-emergent SCHEMA: its centroid is a candidate consolidated T2 CORTICAL
  ARCHETYPE that the hippocampal (T3) instances should be promoted under. This is DISTINCT from P1 (frequency / graph in-degree) and from
  P3 (SHARES_MATH bisimulation, GATED -- 0 edges): P4 needs NO relation edges, only the codebook geometry, so it is feasible NOW.
  READ-ONLY: identifies archetype candidates (does NOT write the canonical substrate -- the actual T2 creation + re-parenting + the
  +0.01-macro benchmark check are Testbed steps). NO LLM; AlgebraIndex is numpy (no torch/GPU); laptop clean copy -> negligible heat.

  DESIGN (exp_dev owns):
   - REPLAY = encode every T3 atom to VECTOR_FIELD (composite_hrr, the production identity vector); skip atoms lacking it.
   - CLUSTER = deterministic single-pass LEADER clustering on L2-normalized vectors (assign to the most-similar existing centroid if
     cos >= TAU, else open a new cluster; centroid = normalized running mean). Order = sorted atom id (reproducible; no RNG in clustering).
   - TAU is DATA-CALIBRATED, not arbitrary: TAU = max(TAU_FLOOR, random_mean + Z_SIGMA * random_std) over a random-pair cosine sample,
     i.e. the "clearly above chance" line (>= 2 sigma over the random-pair mean). NOTE (v1 calibration bug, caught + fixed): v1 used the
     random-pair P99 as BOTH the merge threshold AND the coherence bar -- self-defeating, because a merge threshold at P99 fragments the
     codebook into singletons so NO cluster can reach MIN_SIZE, guaranteeing 0 candidates by construction whenever the codebook has a
     heavy similarity tail (the substrate composite_hrr does: random p99 ~ 0.60 vs mean ~ 0.12, from the name_vec text component). The
     mean+2sigma line is the standard denser-than-chance significance bar and is NOT inflated by the tail; a cluster's mean intra-cos at
     ~0.55 when random pairs average 0.12 is ~4.5x chance -- unambiguously a real emergent schema.
   - A consolidation candidate = a cluster with size >= MIN_SIZE AND mean intra-cluster cosine >= TAU. We also report each cluster's
     Z = (mean_intra_cos - random_mean) / random_std as the significance statistic. Labelled by dominant corpus + shared name tokens.

PRE-REGISTERED: HARD-PASS >= 3 coherent consolidation clusters (size >= MIN_SIZE AND mean-intra-cos >= TAU), each a recognizable
  archetype (centroid candidate T2). MIDDLE 1-2. HARD-FAIL 0 (codebook geometry does not support emergent schemas -> P4 inactive).
  UNKNOWN if too few T3 atoms / no codebook. (The downstream +0.01-macro benchmark gain is a Testbed step after actual promotion.)
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_knowledge_promotion_p4_replay_consolidation_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
VECTOR_FIELD = "composite_hrr"; MIN_SIZE = 3; TAU_FLOOR = 0.40; Z_SIGMA = 2.0; SEED = 1028
_STOP = {"the", "of", "a", "an", "and", "or", "to", "for", "with", "in", "on", "is", "as", "by"}


def _norm(x):
    return str(x).split("::")[-1].strip()


def _l2(M: np.ndarray) -> np.ndarray:
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)


def leader_cluster(V: np.ndarray, order: List[int], tau: float):
    """Single-pass deterministic leader clustering on L2-normalized rows. Returns list of member-index lists."""
    clusters: List[List[int]] = []
    centroids: List[np.ndarray] = []
    for i in order:
        v = V[i]
        if centroids:
            sims = np.array([float(np.dot(v, c)) for c in centroids])
            j = int(np.argmax(sims))
            if sims[j] >= tau:
                clusters[j].append(i)
                m = V[clusters[j]].mean(axis=0)
                centroids[j] = m / (np.linalg.norm(m) + 1e-12)
                continue
        clusters.append([i]); centroids.append(v.copy())
    return clusters


def mean_intra_cos(V: np.ndarray, members: List[int]) -> float:
    if len(members) < 2:
        return 1.0
    S = V[members] @ V[members].T
    iu = np.triu_indices(len(members), k=1)
    return float(np.mean(S[iu]))


def _selftest():
    rng = np.random.RandomState(0)
    # two tight clusters far apart + one singleton
    base_a = rng.randn(16); base_b = rng.randn(16)
    A = np.stack([base_a + 0.01 * rng.randn(16) for _ in range(4)])
    B = np.stack([base_b + 0.01 * rng.randn(16) for _ in range(3)])
    S = rng.randn(1, 16) * 5
    V = _l2(np.vstack([A, B, S]))
    cl = leader_cluster(V, list(range(V.shape[0])), tau=0.5)
    dense = [c for c in cl if len(c) >= 3 and mean_intra_cos(V, c) >= 0.5]
    assert len(dense) == 2, (len(dense), [len(c) for c in cl])
    assert abs(mean_intra_cos(V, [0, 1, 2, 3]) - 1.0) < 0.05
    print("[selftest] PASS: substrate_knowledge_promotion_p4_replay_consolidation_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _tokens(name: str):
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if t and t not in _STOP and len(t) > 2]


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    idx = AlgebraIndex()
    names: List[str] = []; corpora: List[str] = []; vecs: List[np.ndarray] = []
    for a in PartitionedStore(root).all_atoms():
        tier = str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "")
        if tier != "T3":
            continue
        av = idx.encode_atom(a)
        v = getattr(av, VECTOR_FIELD, None)
        if v is None:
            continue
        vecs.append(np.asarray(v, dtype=np.float64)); names.append(_norm(a.id))
        corpora.append(str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower())
    M = len(vecs)
    if M < 30:
        return {"error": "too_few_t3_vectors", "M": M}
    V = _l2(np.stack(vecs))
    if SMOKE:
        V = V[: max(30, M // 3)]; names = names[: V.shape[0]]; corpora = corpora[: V.shape[0]]; M = V.shape[0]
    # data-calibrate TAU from a random-pair cosine sample (p99) -> coherent = denser than chance
    rng = np.random.RandomState(SEED)
    npair = min(20000, M * (M - 1) // 2)
    ii = rng.randint(0, M, npair); jj = rng.randint(0, M, npair); ok = ii != jj
    rp = np.einsum("ij,ij->i", V[ii[ok]], V[jj[ok]])
    rp_mean = float(np.mean(rp)); rp_std = float(np.std(rp) + 1e-12); rp_p99 = float(np.percentile(rp, 99))
    tau = max(TAU_FLOOR, round(rp_mean + Z_SIGMA * rp_std, 4))
    order = sorted(range(M), key=lambda i: names[i])
    clusters = leader_cluster(V, order, tau)
    cands = []
    for c in clusters:
        if len(c) < MIN_SIZE:
            continue
        coh = mean_intra_cos(V, c)
        if coh < tau:
            continue
        cc = Counter(corpora[i] for i in c)
        toks = Counter(t for i in c for t in set(_tokens(names[i])))
        shared = [w for w, n in toks.most_common(6) if n >= max(2, len(c) // 2)]
        cands.append({"size": len(c), "mean_intra_cos": round(coh, 4), "z_over_chance": round((coh - rp_mean) / rp_std, 2),
                      "dominant_corpus": cc.most_common(1)[0][0], "corpus_mix": dict(cc),
                      "shared_tokens": shared, "members": [names[i] for i in sorted(c, key=lambda x: names[x])][:12]})
    cands.sort(key=lambda d: (-d["size"], -d["mean_intra_cos"]))
    n_math = sum(1 for d in cands if d["dominant_corpus"] in {"math", "science", "concept", "school", "meta"})
    print("  T3 replayed=%d dim=%d | random-pair cos mean=%.4f std=%.4f p99=%.4f -> TAU=mean+%.1fsigma=%.4f" % (
        M, V.shape[1], rp_mean, rp_std, rp_p99, Z_SIGMA, tau), flush=True)
    print("  clusters total=%d | coherent consolidation candidates (size>=%d AND intra-cos>=%.3f): %d (math-themed: %d)" % (
        len(clusters), MIN_SIZE, tau, len(cands), n_math), flush=True)
    for d in cands[:12]:
        print("    ARCHETYPE size=%2d coh=%.3f (z=%.1f) corpus=%-8s tokens=%s :: %s" % (
            d["size"], d["mean_intra_cos"], d["z_over_chance"], d["dominant_corpus"], d["shared_tokens"], d["members"][:6]), flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "kp_p4_replay_consolidation_archetypes.json").write_text(json.dumps(
        {"candidates": cands, "tau": tau, "tau_floor": TAU_FLOOR, "z_sigma": Z_SIGMA, "min_size": MIN_SIZE, "vector_field": VECTOR_FIELD,
         "n_t3_replayed": M, "random_pair_mean": round(rp_mean, 4), "random_pair_std": round(rp_std, 4),
         "random_pair_p99": round(rp_p99, 4)}, indent=2), encoding="utf-8")
    return {"n_t3": M, "n_clusters": len(clusters), "n_candidates": len(cands), "n_math_themed": n_math,
            "tau": tau, "random_pair_mean": round(rp_mean, 4), "random_pair_std": round(rp_std, 4), "random_pair_p99": round(rp_p99, 4),
            "candidates": cands[:20], "vector_field": VECTOR_FIELD}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("M", "")))
    n = r["n_candidates"]
    s = ("P4 consolidation candidates=%d (math-themed=%d) from %d replayed T3 atoms; TAU=mean+2sigma=%.4f (random-pair mean=%.4f "
         "std=%.4f) so each cluster is >=2sigma denser than chance; top=%s; saved bench_reports/kp_p4_replay_consolidation_archetypes.json "
         "(READ-ONLY -- Testbed creates T2 + re-parents + benchmark-validates)") % (
        n, r["n_math_themed"], r["n_t3"], r["tau"], r["random_pair_mean"], r["random_pair_std"],
        [(d["dominant_corpus"], d["shared_tokens"][:2], d["size"], d["z_over_chance"]) for d in r["candidates"][:5]])
    if n >= 3:
        return ("HARD_PASS", "HARD_PASS: sleep-replay consolidation surfaces %d coherent T2-archetype candidates -- dense, above-chance "
                "clusters of T3 episodics whose centroid is a candidate consolidated cortical schema. The promotion operator's P4 path "
                "works WITHOUT any relation edges (pure codebook geometry), complementing P1 (frequency). " % n + s)
    if n >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: only %d coherent consolidation cluster(s) -- weak emergent-schema signal at the current "
                "codebook (geometry supports few above-chance T3 clusters). " % n + s)
    return ("HARD_FAIL", "HARD_FAIL: 0 coherent consolidation clusters (no above-chance dense T3 grouping) -- P4 replay-consolidation "
            "inactive at the current codebook geometry. " + s)


print("[config] anchor=%s mode=%s field=%s min_size=%d tau_floor=%.2f" % (ANCHOR_NAME, RUN_MODE, VECTOR_FIELD, MIN_SIZE, TAU_FLOOR), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
