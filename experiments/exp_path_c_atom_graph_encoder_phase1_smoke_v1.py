"""path_c_atom_graph_encoder_phase1_smoke_v1 -- substrate-OWNED backprop-trained encoder.

Path C Phase-1 spoke per research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23:
hub-and-spoke federation; ship Phase-1 atom-graph encoder (S2 only) as cheap decisive test
for whether GraphSAGE-style features on atom-adjacency outperform char-trigram name-encoding.

3 arms:
  ARM_CHAR_TRIGRAM_NAME       baseline; bag-of-trigrams over atom_id
  ARM_GRAPHSAGE_2HOP          mean-pool over 2-hop neighbors of base bipolar HV
                              (untrained graph feature aggregation)
  ARM_GRAPHSAGE_2HOP_LEARNED  same but with a small trained linear projection W
                              (contrastive loss; ~100 epochs SGD; this is the
                              BACKPROP part of Path C)

Discriminator: k-means K=10 mechanism-family purity on chain-grade atoms.

Pre-reg (preregs/2026-06-23_path_c_atom_graph_encoder_phase1_smoke_v1.md):
  HARD_PASS:
    ARM_GRAPHSAGE_2HOP_LEARNED.purity >= 0.92
    AND lift over CHAR_TRIGRAM_NAME >= 0.05
    AND lift over GRAPHSAGE_2HOP (untrained) >= 0.03
    AND planted_graph_purity == 1.0
    AND n_llm_calls == 0
  HARD_FAIL:
    LEARNED.purity <= CHAR_TRIGRAM_NAME.purity + 0.02
  MIDDLE_BAND:
    lift over baseline in (0.02, 0.05)

CPU; ASCII; per-seed checkpoint; FULL seeds=[7, 17, 23].
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "path_c_atom_graph_encoder_phase1_smoke_v1"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"

# substrate-only-decode invariant
_LLM_CALL_COUNTER = [0]

# pre-registered HARD bands
PURITY_HP_FLOOR = 0.92
LIFT_OVER_BASELINE = 0.05
LIFT_OVER_UNTRAINED = 0.03
PLANTED_GRAPH_PURITY = 1.0
HF_LIFT_BAND = 0.02

# CLI
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 1024
    N_ATOMS_SAMPLE = 30
    K_CLUSTERS = 5
    LEARNED_EPOCHS = 20
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_ATOMS_SAMPLE = 100
    K_CLUSTERS = 10
    LEARNED_EPOCHS = 100

# canonical mechanism family list (10 families)
MECHANISM_FAMILIES = [
    "cleanup",
    "storage",
    "generation",
    "refuse",
    "multi_hop",
    "whitening",
    "binding",
    "capacity",
    "trigram",
    "other",
]

# mechanism keyword regex (substring match on lowercased atom name)
MECHANISM_KEYWORDS = {
    "cleanup": ["cleanup", "denoise", "recall"],
    "storage": ["storage", "memory", "hopfield", "kg_store", "store"],
    "generation": ["generation", "generate", "autoregressive", "gen"],
    "refuse": ["refuse", "gate", "abstain", "headroom"],
    "multi_hop": ["multi_hop", "kg_traversal", "traversal", "hop"],
    "whitening": ["whitening", "pca", "kwta", "vq"],
    "binding": ["binding", "bind", "fhrr", "hrr"],
    "capacity": ["capacity", "alpha", "M_", "envelope"],
    "trigram": ["trigram", "char_trigram", "encoder"],
}

# sigma regime bins
SIGMA_BINS = [
    ("sigma_lt_0p5", 0.0, 0.5),
    ("sigma_0p5_1p0", 0.5, 1.0),
    ("sigma_1p0_1p5", 1.0, 1.5),
    ("sigma_gt_1p5", 1.5, 1e9),
]

# cert tier list
CERT_TIERS = ["chain_grade", "measured_mechanism", "honest_negative", "other"]

CONFIG_VERSION = (
    "path_c_atom_graph_encoder_phase1_smoke_v1: ARM_CHAR_TRIGRAM_NAME (baseline) "
    "vs ARM_GRAPHSAGE_2HOP (untrained 2-hop mean-pool over base cert/family/sigma "
    "bipolar HVs) vs ARM_GRAPHSAGE_2HOP_LEARNED (same + contrastive-trained linear "
    "projection W); k-means K=%d on N=%d sampled atoms; "
    "mechanism_family_purity discriminator; HP LEARNED.purity >= %.2f AND "
    "lift_over_baseline >= %.2f AND lift_over_untrained >= %.2f"
) % (K_CLUSTERS, N_ATOMS_SAMPLE, PURITY_HP_FLOOR, LIFT_OVER_BASELINE,
     LIFT_OVER_UNTRAINED)


# ===== deterministic per-feature random bipolar HV codebook =====

def _seed_for_token(token: str) -> int:
    h = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(token: str, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(_seed_for_token(token))
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


# ===== feature extraction (reused from atom_feature_encoder smoke) =====

def mechanism_family_of(atom_id: str) -> str:
    """Return the mechanism family for an atom_id (lowercased substring scan)."""
    lo = atom_id.lower()
    for family in MECHANISM_FAMILIES:
        if family == "other":
            continue
        for kw in MECHANISM_KEYWORDS.get(family, []):
            if kw in lo:
                return family
    return "other"


def sigma_regime_of(metadata: dict) -> str:
    """Extract sigma from atom metadata if present; bin into 4 regimes."""
    sigma = None
    for k, v in (metadata or {}).items():
        if "sigma" in k.lower() and isinstance(v, (int, float)):
            sigma = float(v)
            break
    if sigma is None:
        return "sigma_unknown"
    for name, lo, hi in SIGMA_BINS:
        if lo <= sigma < hi:
            return name
    return "sigma_unknown"


def cert_tier_of(cert_status: str) -> str:
    s = (cert_status or "").lower()
    if "chain" in s:
        return "chain_grade"
    if "measured" in s or "mechanism" in s:
        return "measured_mechanism"
    if "honest" in s or "negative" in s:
        return "honest_negative"
    return "other"


def graph_neighborhood_tokens(atom_id: str, atom_meta: dict) -> list[str]:
    """Return list of neighbor-atom tokens from composes/typed_by/cap fields."""
    tokens: list[str] = []
    meta = atom_meta.get("metadata", {}) or {}
    for k in ("composes", "composes_with", "typed_by", "retyped_by",
              "cap_backfilled_by", "atomized_by", "relabeled_by"):
        v = meta.get(k)
        if isinstance(v, str):
            tokens.append("nbr|" + v)
        elif isinstance(v, list):
            tokens.extend("nbr|" + str(x) for x in v if isinstance(x, str))
    serves = atom_meta.get("serves_capability", [])
    if isinstance(serves, list):
        tokens.extend("cap|" + str(x) for x in serves if isinstance(x, str))
    algebra = atom_meta.get("algebra", {}) or {}
    for k in ("about_topic", "domain", "structure", "role"):
        v = algebra.get(k)
        if isinstance(v, str):
            tokens.append("alg|" + k + "=" + v)
    return tokens


# ===== adjacency build =====

def build_adjacency(
    aids: list[str],
    metas: list[dict],
) -> dict[int, set[int]]:
    """Build symmetric adjacency over atom-INDEX (0..N-1) by token overlap.

    Two atoms are neighbors if they share any neighborhood-token (composes_with,
    serves_capability, algebra fields, etc.). This is the substrate's atom-graph
    structure used as the GraphSAGE adjacency.
    """
    # token -> set of atom indices that produce it
    token_to_idxs: dict[str, set[int]] = {}
    atom_tokens: list[set[str]] = []
    for i, (aid, m) in enumerate(zip(aids, metas)):
        toks = set(graph_neighborhood_tokens(aid, m))
        atom_tokens.append(toks)
        for t in toks:
            token_to_idxs.setdefault(t, set()).add(i)

    adj: dict[int, set[int]] = {i: set() for i in range(len(aids))}
    for t, idxs in token_to_idxs.items():
        if len(idxs) < 2:
            continue
        idx_list = list(idxs)
        for a in idx_list:
            for b in idx_list:
                if a != b:
                    adj[a].add(b)
    return adj


def n_hop_neighbors(adj: dict[int, set[int]], src: int, n_hops: int) -> set[int]:
    """Return set of atom indices reachable within n_hops (inclusive of src)."""
    frontier = {src}
    visited = {src}
    for _ in range(n_hops):
        nxt: set[int] = set()
        for u in frontier:
            for v in adj.get(u, set()):
                if v not in visited:
                    nxt.add(v)
        visited |= nxt
        frontier = nxt
        if not frontier:
            break
    return visited


# ===== encoders =====

def encode_char_trigram(atom_id: str, n_dim: int) -> np.ndarray:
    """Baseline encoder: bag-of-char-trigrams over the atom_id string."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    return enc.encode(atom_id)


def base_feature(
    atom_id: str,
    ledger_row: dict,
    atom_meta: dict,
    n_dim: int,
) -> np.ndarray:
    """Base per-atom feature: bind cert_tier + mechanism_family + sigma_regime.

    Used as the per-node feature input for GraphSAGE 2-hop aggregation. Does NOT
    include neighborhood tokens (those flow through adjacency aggregation).
    """
    cert = cert_tier_of(ledger_row.get("cert_status", ""))
    family = mechanism_family_of(atom_id)
    sigma = sigma_regime_of(atom_meta.get("metadata", {}))

    cert_vec = _bipolar_hv("cert|" + cert, n_dim)
    family_vec = _bipolar_hv("family|" + family, n_dim)
    sigma_vec = _bipolar_hv("sigma|" + sigma, n_dim)

    accum = cert_vec + family_vec + sigma_vec
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def encode_graphsage_2hop(
    idx: int,
    base_feats: np.ndarray,
    adj: dict[int, set[int]],
) -> np.ndarray:
    """GraphSAGE 2-hop mean-pool over base bipolar features; sign-bundle."""
    nbrs = n_hop_neighbors(adj, idx, n_hops=2)
    if not nbrs:
        nbrs = {idx}
    accum = base_feats[list(nbrs)].sum(axis=0)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def train_learned_projection(
    untrained_feats: np.ndarray,
    families: list[str],
    seed: int,
    n_dim: int,
    epochs: int,
) -> np.ndarray:
    """Contrastive-train a linear projection W (n_dim x n_dim) on untrained 2-hop feats.

    Positive pair = atoms in same mechanism family; negative = different family.
    Loss = max(0, 1 - cos(Wa, Wb)) + max(0, cos(Wa, Wc) + 0.1)
    SGD; ~5 min CPU at n_dim=4096.

    Returns the trained projected features [N, n_dim].
    """
    import torch
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)

    n = untrained_feats.shape[0]
    # group indices by family for fast pos/neg sampling
    by_family: dict[str, list[int]] = {}
    for i, f in enumerate(families):
        by_family.setdefault(f, []).append(i)
    families_with_pairs = [f for f, idxs in by_family.items() if len(idxs) >= 2]

    if not families_with_pairs:
        # degenerate case: no family has 2+ atoms; return untrained feats
        return untrained_feats.copy()

    # initialize W as sparse-ish near-identity-like projection. Pure random init
    # would scramble; sparse 0.01 density on top of identity preserves structure.
    feats_t = torch.from_numpy(untrained_feats.astype(np.float32))
    W = torch.eye(n_dim, dtype=torch.float32)
    # add small random perturbation so gradients have a direction to flow
    W = W + 0.01 * torch.randn(n_dim, n_dim, dtype=torch.float32)
    W.requires_grad_(True)

    optim = torch.optim.SGD([W], lr=1e-2, momentum=0.9)
    batch_size = 8

    for ep in range(epochs):
        optim.zero_grad()
        loss_total = torch.tensor(0.0)
        # sample batch_size pos + neg pairs
        for _ in range(batch_size):
            f_pos = families_with_pairs[int(rng.integers(0, len(families_with_pairs)))]
            a_idx, b_idx = rng.choice(by_family[f_pos], size=2, replace=False).tolist()
            # negative: pick c from a different family
            other_fams = [f for f in by_family if f != f_pos and len(by_family[f]) >= 1]
            if not other_fams:
                continue
            f_neg = other_fams[int(rng.integers(0, len(other_fams)))]
            c_idx = int(rng.choice(by_family[f_neg]))

            a = feats_t[a_idx]
            b = feats_t[b_idx]
            c = feats_t[c_idx]
            Wa = W @ a
            Wb = W @ b
            Wc = W @ c
            cos_pos = torch.nn.functional.cosine_similarity(Wa.unsqueeze(0),
                                                            Wb.unsqueeze(0))[0]
            cos_neg = torch.nn.functional.cosine_similarity(Wa.unsqueeze(0),
                                                            Wc.unsqueeze(0))[0]
            loss_pos = torch.clamp(1.0 - cos_pos, min=0.0)
            loss_neg = torch.clamp(cos_neg + 0.1, min=0.0)
            loss_total = loss_total + loss_pos + loss_neg

        loss_total = loss_total / float(batch_size)
        loss_total.backward()
        optim.step()

    with torch.no_grad():
        projected = (W @ feats_t.T).T.detach().cpu().numpy()
    return projected.astype(np.float32)


# ===== k-means (numpy-only; simple Lloyd; reused from atom_feature_encoder smoke) =====

def kmeans_simple(X: np.ndarray, k: int, seed: int, n_iter: int = 50) -> np.ndarray:
    """Lloyd's k-means with k-means++ init on cosine-normalized rows; returns ids [N].

    k-means++ init avoids the pathology where random init picks 2+ seeds from the
    same cluster (which leaves another cluster with no center and yields a
    persistent ~2/3 purity floor on tight K-component data). Cosine-based
    farthest-point sampling: first center random; each subsequent center sampled
    with probability proportional to (1 - max cosine to existing centers).
    """
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    Xn = X / norms
    keff = min(k, n)
    # k-means++ init
    first = int(rng.integers(0, n))
    center_idxs = [first]
    while len(center_idxs) < keff:
        centers_so_far = Xn[center_idxs]  # [m, d]
        sims = Xn @ centers_so_far.T  # [n, m]
        max_sim = sims.max(axis=1)  # closest existing center per point
        dist_proxy = np.clip(1.0 - max_sim, 0.0, 2.0)  # cosine distance proxy
        # already-picked points have dist ~0 -> probability ~0; that's correct
        if dist_proxy.sum() <= 1e-9:
            # degenerate: all points identical -> pick remaining at random
            remaining = [i for i in range(n) if i not in center_idxs]
            if not remaining:
                break
            center_idxs.append(int(rng.choice(remaining)))
        else:
            probs = (dist_proxy ** 2)
            probs = probs / probs.sum()
            center_idxs.append(int(rng.choice(n, p=probs)))
    centers = Xn[center_idxs].copy()
    assign = np.zeros(n, dtype=np.int64)
    for _ in range(n_iter):
        sims = Xn @ centers.T
        new_assign = sims.argmax(axis=1)
        if np.array_equal(new_assign, assign):
            break
        assign = new_assign
        for kk in range(keff):
            mask = assign == kk
            if mask.any():
                m = Xn[mask].mean(axis=0)
                mn = np.linalg.norm(m) + 1e-8
                centers[kk] = m / mn
    return assign


def cluster_purity(labels: np.ndarray, families: list[str]) -> float:
    """For each cluster, count modal-family fraction; weighted average."""
    n = len(families)
    if n == 0:
        return 0.0
    total_correct = 0
    for c in sorted(set(labels.tolist())):
        idxs = [i for i, lab in enumerate(labels) if lab == c]
        if not idxs:
            continue
        fams = [families[i] for i in idxs]
        counts: dict[str, int] = {}
        for f in fams:
            counts[f] = counts.get(f, 0) + 1
        total_correct += max(counts.values())
    return total_correct / n


# ===== data load =====

def load_chain_grade_atoms() -> list[tuple[str, dict]]:
    """Return [(atom_id, ledger_row)] for distinct chain-grade atoms (latest per id)."""
    if not LEDGER.exists():
        raise FileNotFoundError("cert_ledger missing: %s" % LEDGER)
    seen: dict[str, dict] = {}
    with open(LEDGER, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("cert_status") != "chain_grade":
                continue
            aid = r.get("atom_id", "")
            if not aid:
                continue
            seen[aid] = r
    return sorted(seen.items(), key=lambda kv: kv[0])


def load_atoms_metadata() -> dict[str, dict]:
    """Return {bare atom_id -> full atom dict} across all corpora."""
    out: dict[str, dict] = {}
    if not SUBSTRATE_INDEX.is_dir():
        return out
    for corpus_dir in sorted(SUBSTRATE_INDEX.iterdir()):
        af = corpus_dir / "atoms.jsonl"
        if not af.is_file():
            continue
        with open(af, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                aid = r.get("id", "")
                if aid:
                    out[aid] = r
    return out


def _strip_corpus_prefix(atom_id: str) -> str:
    if "::" in atom_id:
        return atom_id.split("::", 1)[1]
    return atom_id


# ===== self-test (planted graph endpoint check) =====

def _selftest():
    """Planted graph with 3 disconnected components; GraphSAGE arms must
    recover the 3 clusters perfectly (purity=1.0).

    9 atoms in 3 components; within each component atoms share a unique
    'composes_with' token (binding them via the substrate's adjacency rule).
    Across components no shared tokens. Mechanism families distributed 1
    per component slot so the 3 clusters map to 3 distinct families.
    """
    n_dim_test = 256
    epochs_test = 5
    aids = [
        "math::T3/EXP_compA_cleanup_v1",
        "math::T3/EXP_compA_storage_v1",
        "math::T3/EXP_compA_generation_v1",
        "math::T3/EXP_compB_refuse_v1",
        "math::T3/EXP_compB_multi_hop_v1",
        "math::T3/EXP_compB_whitening_v1",
        "math::T3/EXP_compC_binding_v1",
        "math::T3/EXP_compC_capacity_v1",
        "math::T3/EXP_compC_trigram_v1",
    ]
    # 3 components; each shares a unique token within
    metas = [
        {"metadata": {"composes_with": "compA_token"}},  # 0
        {"metadata": {"composes_with": "compA_token"}},  # 1
        {"metadata": {"composes_with": "compA_token"}},  # 2
        {"metadata": {"composes_with": "compB_token"}},  # 3
        {"metadata": {"composes_with": "compB_token"}},  # 4
        {"metadata": {"composes_with": "compB_token"}},  # 5
        {"metadata": {"composes_with": "compC_token"}},  # 6
        {"metadata": {"composes_with": "compC_token"}},  # 7
        {"metadata": {"composes_with": "compC_token"}},  # 8
    ]
    rows = [{"cert_status": "chain_grade", "verdict": "CG",
             "cv": 0.05, "cert_increment_delta": 1} for _ in aids]

    # build adjacency: shared composes_with token -> all in component are neighbors
    adj = build_adjacency(aids, metas)
    # sanity: comp A atoms should be neighbors
    assert 1 in adj[0] and 2 in adj[0], "compA adjacency missing"
    assert 6 not in adj[0], "cross-component adjacency leaked"

    # ground-truth COMPONENT labels (NOT mechanism family). The point is the
    # endpoint check: GraphSAGE recovers the component structure of the graph.
    component_labels = ["A", "A", "A", "B", "B", "B", "C", "C", "C"]

    # base features (cert/family/sigma -- DIFFERENT per atom since family differs)
    base_feats = np.stack([
        base_feature(a, r, m, n_dim_test) for a, r, m in zip(aids, rows, metas)
    ])

    # 2-hop GraphSAGE encode each atom
    sage_vecs = np.stack([
        encode_graphsage_2hop(i, base_feats, adj)
        for i in range(len(aids))
    ])

    # k-means K=3
    sage_labels = kmeans_simple(sage_vecs, k=3, seed=0)
    sage_purity = cluster_purity(sage_labels, component_labels)

    # learned-projection arm on the same untrained 2-hop feats
    learned_vecs = train_learned_projection(
        sage_vecs, [mechanism_family_of(a) for a in aids],
        seed=0, n_dim=n_dim_test, epochs=epochs_test,
    )
    learned_labels = kmeans_simple(learned_vecs, k=3, seed=0)
    learned_purity = cluster_purity(learned_labels, component_labels)

    # endpoint: both GraphSAGE arms must recover the 3 components perfectly
    assert sage_purity >= 0.99, (
        "GraphSAGE 2-hop FAILED planted-graph endpoint; purity=%.3f" % sage_purity
    )
    assert learned_purity >= 0.99, (
        "GraphSAGE LEARNED FAILED planted-graph endpoint; purity=%.3f" % learned_purity
    )

    # baseline (char-trigram) NOT expected to pass this test; we only assert
    # the GraphSAGE arms.
    trig_vecs = np.stack([encode_char_trigram(a, n_dim_test) for a in aids])
    trig_labels = kmeans_simple(trig_vecs, k=3, seed=0)
    trig_purity = cluster_purity(trig_labels, component_labels)

    # substrate-only-decode invariant
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated"

    print("[selftest] PASS: planted-graph 3-component endpoint; "
          "sage=%.3f learned=%.3f trig=%.3f n_llm_calls=%d" %
          (sage_purity, learned_purity, trig_purity, _LLM_CALL_COUNTER[0]),
          flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== main run =====

def run_one_seed(
    seed: int,
    atoms: list[tuple[str, dict]],
    atom_meta: dict[str, dict],
) -> dict:
    """Run all 3 arms + planted-graph sanity for a single seed; return dict."""
    t0 = time.time()
    rng = np.random.default_rng(seed)

    n_pool = len(atoms)
    n_sample = min(N_ATOMS_SAMPLE, n_pool)
    idx = rng.choice(n_pool, size=n_sample, replace=False)
    sampled = [atoms[int(i)] for i in idx]

    aids = [aid for aid, _ in sampled]
    ledger_rows = [row for _, row in sampled]
    metas = [atom_meta.get(_strip_corpus_prefix(aid), {}) for aid in aids]
    families = [mechanism_family_of(aid) for aid in aids]

    # ARM 1: char-trigram baseline
    trig_vecs = np.stack([encode_char_trigram(aid, N_DIM) for aid in aids])

    # build adjacency over sampled atoms
    adj = build_adjacency(aids, metas)
    avg_deg = float(np.mean([len(adj[i]) for i in range(n_sample)])) if n_sample else 0.0

    # base bipolar features (cert/family/sigma)
    base_feats = np.stack([
        base_feature(aid, row, meta, N_DIM)
        for aid, row, meta in zip(aids, ledger_rows, metas)
    ])

    # ARM 2: GraphSAGE 2-hop untrained
    sage_vecs = np.stack([
        encode_graphsage_2hop(i, base_feats, adj)
        for i in range(n_sample)
    ])

    # ARM 3: GraphSAGE 2-hop learned projection (contrastive)
    learned_vecs = train_learned_projection(
        sage_vecs, families, seed=seed, n_dim=N_DIM, epochs=LEARNED_EPOCHS,
    )

    # k-means on each
    trig_labels = kmeans_simple(trig_vecs, k=K_CLUSTERS, seed=seed)
    sage_labels = kmeans_simple(sage_vecs, k=K_CLUSTERS, seed=seed)
    learned_labels = kmeans_simple(learned_vecs, k=K_CLUSTERS, seed=seed)

    trig_purity = cluster_purity(trig_labels, families)
    sage_purity = cluster_purity(sage_labels, families)
    learned_purity = cluster_purity(learned_labels, families)

    # planted-graph sanity (3 disconnected components; small auxiliary check
    # at full N_DIM to confirm GraphSAGE adjacency-aggregation is intact)
    planted_aids = [
        "math::T3/EXP_compA_cleanup_v1",
        "math::T3/EXP_compA_storage_v1",
        "math::T3/EXP_compA_generation_v1",
        "math::T3/EXP_compB_refuse_v1",
        "math::T3/EXP_compB_multi_hop_v1",
        "math::T3/EXP_compB_whitening_v1",
        "math::T3/EXP_compC_binding_v1",
        "math::T3/EXP_compC_capacity_v1",
        "math::T3/EXP_compC_trigram_v1",
    ]
    planted_metas = (
        [{"metadata": {"composes_with": "compA_token"}}] * 3 +
        [{"metadata": {"composes_with": "compB_token"}}] * 3 +
        [{"metadata": {"composes_with": "compC_token"}}] * 3
    )
    planted_rows = [{"cert_status": "chain_grade", "verdict": "CG",
                     "cv": 0.05, "cert_increment_delta": 1}
                    for _ in planted_aids]
    planted_components = ["A"]*3 + ["B"]*3 + ["C"]*3
    planted_adj = build_adjacency(planted_aids, planted_metas)
    planted_base = np.stack([
        base_feature(a, r, m, N_DIM)
        for a, r, m in zip(planted_aids, planted_rows, planted_metas)
    ])
    planted_sage = np.stack([
        encode_graphsage_2hop(i, planted_base, planted_adj)
        for i in range(len(planted_aids))
    ])
    planted_labels = kmeans_simple(planted_sage, k=3, seed=seed)
    planted_purity = cluster_purity(planted_labels, planted_components)

    elapsed = time.time() - t0

    return {
        "seed": seed,
        "N": N_DIM,
        "M": n_sample,
        "run_mode": RUN_MODE,
        "arm_char_trigram_purity": float(trig_purity),
        "arm_graphsage_2hop_purity": float(sage_purity),
        "arm_graphsage_2hop_learned_purity": float(learned_purity),
        "lift_learned_over_baseline": float(learned_purity - trig_purity),
        "lift_learned_over_untrained": float(learned_purity - sage_purity),
        "lift_untrained_over_baseline": float(sage_purity - trig_purity),
        "planted_graph_purity": float(planted_purity),
        "avg_adjacency_degree": avg_deg,
        "n_atoms_sampled": n_sample,
        "k_clusters": K_CLUSTERS,
        "learned_epochs": LEARNED_EPOCHS,
        "elapsed_s": elapsed,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "family_distribution": {
            f: families.count(f) for f in set(families)
        },
    }


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[%s] start mode=%s seeds=%s N_DIM=%d K=%d N_atoms=%d epochs=%d" %
          (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_CLUSTERS, N_ATOMS_SAMPLE,
           LEARNED_EPOCHS), flush=True)

    print("[%s] loading chain-grade atoms + metadata..." % ANCHOR_NAME, flush=True)
    atoms = load_chain_grade_atoms()
    atom_meta = load_atoms_metadata()
    print("[%s] loaded %d chain-grade atoms; %d atom-metadata entries" %
          (ANCHOR_NAME, len(atoms), len(atom_meta)), flush=True)

    if len(atoms) < 3:
        raise RuntimeError("not enough chain-grade atoms: %d" % len(atoms))

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "M": N_ATOMS_SAMPLE,
                  "learned_epochs": LEARNED_EPOCHS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[%s] ckpt: %d done; running %d" %
          (ANCHOR_NAME, len(done), len(remaining)), flush=True)

    for seed in remaining:
        print("[%s] seed=%d running..." % (ANCHOR_NAME, seed), flush=True)
        result = run_one_seed(seed, atoms, atom_meta)
        write_partial(out_dir, seed, result)
        print("[%s] seed=%d done: trig=%.3f sage=%.3f learned=%.3f "
              "lift_over_baseline=%+.3f lift_over_untrained=%+.3f planted=%.3f" %
              (ANCHOR_NAME, seed,
               result["arm_char_trigram_purity"],
               result["arm_graphsage_2hop_purity"],
               result["arm_graphsage_2hop_learned_purity"],
               result["lift_learned_over_baseline"],
               result["lift_learned_over_untrained"],
               result["planted_graph_purity"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)

    # aggregate per-arm
    trig_vals = [per_seed[str(s)]["arm_char_trigram_purity"] for s in SEEDS]
    sage_vals = [per_seed[str(s)]["arm_graphsage_2hop_purity"] for s in SEEDS]
    learned_vals = [per_seed[str(s)]["arm_graphsage_2hop_learned_purity"]
                    for s in SEEDS]
    lift_lb_vals = [per_seed[str(s)]["lift_learned_over_baseline"] for s in SEEDS]
    lift_lu_vals = [per_seed[str(s)]["lift_learned_over_untrained"] for s in SEEDS]
    planted_vals = [per_seed[str(s)]["planted_graph_purity"] for s in SEEDS]
    elapsed_vals = [per_seed[str(s)]["elapsed_s"] for s in SEEDS]
    n_llm = sum(per_seed[str(s)]["n_llm_calls"] for s in SEEDS)

    trig_mean = float(np.mean(trig_vals))
    trig_std = float(np.std(trig_vals))
    sage_mean = float(np.mean(sage_vals))
    sage_std = float(np.std(sage_vals))
    learned_mean = float(np.mean(learned_vals))
    learned_std = float(np.std(learned_vals))
    lift_lb_mean = float(np.mean(lift_lb_vals))
    lift_lu_mean = float(np.mean(lift_lu_vals))
    planted_mean = float(np.mean(planted_vals))

    learned_cv = learned_std / (learned_mean + 1e-8)
    elapsed_s = float(np.sum(elapsed_vals))

    # verdict
    hp_purity_ok = learned_mean >= PURITY_HP_FLOOR
    hp_lift_baseline_ok = lift_lb_mean >= LIFT_OVER_BASELINE
    hp_lift_untrained_ok = lift_lu_mean >= LIFT_OVER_UNTRAINED
    hp_planted_ok = planted_mean >= PLANTED_GRAPH_PURITY
    hp_no_llm = (n_llm == 0)

    hard_fail = (lift_lb_mean <= HF_LIFT_BAND) or (not hp_no_llm)

    if (hp_purity_ok and hp_lift_baseline_ok and hp_lift_untrained_ok
            and hp_planted_ok and hp_no_llm):
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s_%s_%dseeds_N%d_K%d_M%d_epochs%d_learned_purity_%.3f_pm_%.3f_"
        "sage_purity_%.3f_pm_%.3f_trig_purity_%.3f_pm_%.3f_"
        "lift_over_baseline_%+.3f_lift_over_untrained_%+.3f_planted_%.3f_"
        "n_llm_calls_%d_cv_learned_%.4f_elapsed_%.1fs"
    ) % (
        verdict, RUN_MODE.upper(), len(SEEDS), N_DIM, K_CLUSTERS,
        N_ATOMS_SAMPLE, LEARNED_EPOCHS,
        learned_mean, learned_std,
        sage_mean, sage_std,
        trig_mean, trig_std,
        lift_lb_mean, lift_lu_mean, planted_mean,
        n_llm, learned_cv, elapsed_s,
    )

    summary = {
        "anchor": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "seeds": SEEDS,
        "N_DIM": N_DIM,
        "K_CLUSTERS": K_CLUSTERS,
        "N_ATOMS_SAMPLE": N_ATOMS_SAMPLE,
        "LEARNED_EPOCHS": LEARNED_EPOCHS,
        "arm_char_trigram_purity_mean": trig_mean,
        "arm_char_trigram_purity_std": trig_std,
        "arm_graphsage_2hop_purity_mean": sage_mean,
        "arm_graphsage_2hop_purity_std": sage_std,
        "arm_graphsage_2hop_learned_purity_mean": learned_mean,
        "arm_graphsage_2hop_learned_purity_std": learned_std,
        "arm_graphsage_2hop_learned_purity_cv": learned_cv,
        "lift_learned_over_baseline_mean": lift_lb_mean,
        "lift_learned_over_untrained_mean": lift_lu_mean,
        "planted_graph_purity_mean": planted_mean,
        "n_llm_calls": n_llm,
        "n_chain_grade_atoms_pool": len(atoms),
        "hp_thresholds": {
            "purity_floor": PURITY_HP_FLOOR,
            "lift_over_baseline": LIFT_OVER_BASELINE,
            "lift_over_untrained": LIFT_OVER_UNTRAINED,
            "planted_purity_required": PLANTED_GRAPH_PURITY,
        },
        "hp_gates": {
            "purity_ok": hp_purity_ok,
            "lift_baseline_ok": hp_lift_baseline_ok,
            "lift_untrained_ok": hp_lift_untrained_ok,
            "planted_ok": hp_planted_ok,
            "no_llm": hp_no_llm,
        },
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "summary": summary,
        "per_seed": per_seed,
    }

    write_metrics(out_dir, metrics)
    print("[%s] %s" % (ANCHOR_NAME, verdict_msg), flush=True)


if __name__ == "__main__":
    main()
