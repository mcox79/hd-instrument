"""substrate_self_map_v2c -- substrate-native self-mapping, FULL-STORE ingest (Phase 1).

v2c is the Option-2 recovery path from v2b's MIDDLE_BAND verdict (CERT-architecture
META atom + cell-author's recommended HARD_FAIL recovery path; v2b landed
n_clusters_real=2 vs shuf=1 cluster_gap=1 at 96 admitted triples / 489 atom universe
-- mechanism present but below HARD_PASS bars). v2c gives substrate the FULL atomized
Store to map (~200k relations across 177k atoms), while still drawing ANCHORS from
the ~447 chain-grade subset.

Mechanism is identical to v2b end-to-end (substrate-native; ZERO LLM forward calls at
retrieval): char_trigram_encoder + KGStore + multi_hop. The only changes are:

  1. load_relations_for(...) now admits EVERY (src, rel_type, tgt) triple in every
     data/substrate_index/<corpus>/relations.jsonl (self-loops dropped). No EITHER-
     endpoint chain-grade filter; no atomized-set filter on endpoints. The combined
     atom universe = chain-grade prefix + every atom_id appearing in any admitted
     triple (and also in any corpus atoms.jsonl, to keep the codebook honest).
  2. Anchors STILL drawn only from the chain-grade prefix; substrate maps how the
     ~447 chain-grade atoms sit in the FULL ~200k-relation atomized graph.
  3. Compute hyperparams tightened: N_ANCHORS=100 (was 200), N_RELATION_SAMPLES=20
     (was 32). At n_ent ~ 177k + n_dim=4096, each kg.E @ transit call is ~725M
     float ops; the dominant cost is anchor-traversal score_all calls. Lower
     N_ANCHORS keeps wall to ~25min/seed at the remote_cpu BLAS rate.

Honest expected scale (frozen 2026-06-22):
  - 203,462 relations total across 11 corpora (concept dominates at 189,654)
  - ~177k atomized atom_ids (chain-grade is a subset of size 447)
  - admitted relation_types likely >> 17 (v2b saw only 3 in its narrow scope)

Same HARD bands as v2b -- the discriminator metric is identical (cluster-gap
real vs shuffle); only the substrate scope changes.

Pre-reg HARD bands (committed in preregs/2026-06-22_substrate_self_map_v2c_full_store.md):

  HARD_PASS chain-grade:
    - n_clusters_real - n_clusters_shuffle >= 2  (real has more granular structure)
    - n_clusters_real >= 3                       (mechanism produces structure)
    - substrate-only-decode preserved (n_llm_calls = 0)
    - atom_retrieval_recall >= 0.95              (codebook preserves atom-id identity
                                                  -- harder gate now: 177k atoms in
                                                  a 4096-D char-trigram codebook)
    - 3 seeds; cv on n_clusters_real <= 0.10

  MIDDLE_BAND:
    - n_clusters_real >= 2 AND cluster_gap >= 1

  HARD_FAIL:
    - n_clusters_real <= 1   (mechanism null even on full Store)
    - cluster_gap <= 0       (shuffle as granular as real)
    - n_llm_calls > 0
    - atom_retrieval_recall < 0.50

Discriminator control (Fix #16): RANDOM_RELATION baseline arm.

Substrate-only-decode gate (Skunkworks structural blocker #3): ZERO transformers /
AutoModel imports; _LLM_CALL_COUNTER must stay at 0.

CPU; ASCII; per-seed checkpoint via experiments/_seed_checkpoint.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

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

# ----- substrate-only-decode gate (Skunkworks structural blocker #3) -----
_LLM_CALL_COUNTER = [0]   # MUST stay at 0; we never import transformers/torch/AutoModel.

ANCHOR_NAME = "substrate_self_map_v2c"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"

# ----- pre-registered HARD thresholds (v2c full-Store ingest; bands match v2b) -----
N_CLUSTERS_REAL_PASS = 3
N_CLUSTERS_REAL_MIDDLE = 2
N_CLUSTERS_GAP_PASS = 2
N_CLUSTERS_GAP_MIDDLE = 1
N_CLUSTERS_GAP_FAIL = 0
RECALL_PASS = 0.95
RECALL_FAIL = 0.50
CV_PASS = 0.10
JACCARD_CLUSTER_TAU = 0.30
JACCARD_VS_V1_TAU = 0.30

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# ----- config -----
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    # Smoke: cap admitted-triple count + anchors so smoke completes in <120s on
    # remote_cpu even with full-Store ingest path active. The cap is on
    # the number of relations actually ingested (uniform-random subsample);
    # this confirms the data-load + ingest + traversal pipe composes
    # end-to-end at full-Store scale without paying the full wall.
    MAX_INGEST_TRIPLES = 5000
    N_ANCHORS = 20
    N_RELATION_SAMPLES = 8
    K_SET = 12
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    MAX_INGEST_TRIPLES = None     # no cap: ingest everything we admit
    N_ANCHORS = 100               # tightened from v2b=200 (controls traversal cost)
    N_RELATION_SAMPLES = 20       # tightened from v2b=32 (controls traversal cost)
    K_SET = 16

CONFIG_VERSION = (
    "v2c-full-store-ingest-chain-grade-anchors: char_trigram_atom_encode + "
    "KGStore_multivalue_Hebbian + multi_hop_2hop_neighborhood_Jaccard_cluster + "
    "random_relation_control; FULL-Store admit (every relations.jsonl triple); "
    "chain-grade-only anchor sampling; cluster-count discriminator (real - shuffle); "
    "N%d max_ingest_triples=%s n_anchors=%d n_rel_samples=%d kset=%d "
    "bands n_clusters>=%d cluster_gap>=%d recall>=%.2f cv<=%.2f"
) % (N_DIM, str(MAX_INGEST_TRIPLES), N_ANCHORS, N_RELATION_SAMPLES, K_SET,
     N_CLUSTERS_REAL_PASS, N_CLUSTERS_GAP_PASS, RECALL_PASS, CV_PASS)


# ----- selftest: substrate primitives compose end-to-end on tiny synthetic KG -----
def _selftest():
    """Verify char_trigram + KGStore + neighborhood-Jaccard pipe works on synthetic data."""
    import torch
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    from hdlab.kg_traversal import KGStore

    enc = CharTrigramEncoder(n_dim=512)
    atom_ids = [
        "math::T3/EXP_alpha_capacity_v1",
        "math::T3/EXP_alpha_capacity_v2",
        "math::T3/EXP_kg_ingest_v1",
        "math::T3/EXP_kg_ingest_v2",
        "math::T3/EXP_whitening_pca_v1",
    ]
    E_np = enc.encode_batch(atom_ids).astype(np.float32)
    n_ent = len(atom_ids); n_rel = 3
    g = torch.Generator(); g.manual_seed(0)
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=512, generator=g)
    kg.E = torch.from_numpy(E_np)
    triples = torch.tensor([
        [0, 0, 1], [1, 0, 0],
        [2, 0, 3], [3, 0, 2],
        [0, 1, 4], [2, 1, 4],
    ], dtype=torch.long)
    kg.ingest_triples(triples)
    key = kg.key(0, 0)
    scores = kg.score_all(key)
    assert scores.argmax().item() == 1, f"1-hop alpha_v1-rel0 should -> alpha_v2 (got {scores.argmax().item()})"
    q = enc.encode(atom_ids[2])
    q_t = torch.from_numpy(q.astype(np.float32))
    cos = (kg.E @ q_t) / (
        (torch.linalg.norm(kg.E, dim=1) + 1e-8) * (torch.linalg.norm(q_t) + 1e-8)
    )
    best = int(cos.argmax())
    assert best == 2, f"char-trigram self-retrieve should find atom 2 (got {best})"
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print(
        "[selftest] PASS: char-trigram self-retrieval + KGStore single-hop + multi-value "
        "ingest compose; n_llm_calls=0",
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== data load: chain-grade atoms + FULL-Store relations =====


def load_chain_grade_atom_ids() -> list[str]:
    """Read cert_ledger.jsonl; collect distinct chain-grade atom_ids (supersedes-folded)."""
    if not LEDGER.exists():
        raise FileNotFoundError(f"cert_ledger not found at {LEDGER}")
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
    return sorted(seen.keys())


def _strip_corpus_prefix(atom_id: str) -> str:
    """Return the post-:: portion of atom_id (matches relations.jsonl src_id/tgt_id keys)."""
    if "::" in atom_id:
        return atom_id.split("::", 1)[1]
    return atom_id


def load_atomized_atom_ids() -> set[str]:
    """Collect every atom_id appearing in any <corpus>/atoms.jsonl (bare form, post-`::`)."""
    out: set[str] = set()
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
                    out.add(aid)
    return out


def load_relations_for(
    chain_grade_atom_ids: list[str],
    atomized_atom_ids: set[str],
    max_ingest_triples: int | None,
    rng: np.random.Generator,
) -> Tuple[list[tuple[int, str, int]], list[str], list[str], int]:
    """v2c FULL-Store ingest: admit every (src, rel_type, tgt) triple in every
    <corpus>/relations.jsonl. Self-loops dropped. No EITHER-endpoint filter; no
    atomized-set filter (we union endpoints into the universe directly).

    If max_ingest_triples is not None, apply a uniform-random subsample AFTER
    admission to keep smoke wall bounded.

    Returns:
      triples: list of (src_idx, rel_type_str, tgt_idx) indexed into combined_atom_ids.
      relation_types: sorted distinct rel_type strings encountered.
      combined_atom_ids: ordered list with chain-grade prefix FIRST (so anchors are
        0..n_chain_grade-1), then all other atom_ids appearing in admitted triples,
        union with anything in atomized_atom_ids (for codebook honesty).
      n_chain_grade: length of the chain-grade prefix in combined_atom_ids.
    """
    chain_grade_bare: set[str] = {_strip_corpus_prefix(a) for a in chain_grade_atom_ids}
    # First pass: collect every admitted (src, rel_type, tgt) bare-form triple.
    admitted: list[tuple[str, str, str]] = []
    rel_types: set = set()
    endpoint_atoms: set[str] = set()
    n_files = 0
    if not SUBSTRATE_INDEX.is_dir():
        raise FileNotFoundError(f"substrate_index not found at {SUBSTRATE_INDEX}")
    for corpus_dir in sorted(SUBSTRATE_INDEX.iterdir()):
        rel_file = corpus_dir / "relations.jsonl"
        if not rel_file.is_file():
            continue
        n_files += 1
        with open(rel_file, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                src_b = r.get("src_id", "")
                tgt_b = r.get("tgt_id", "")
                rtype = r.get("rel_type", "")
                if not src_b or not tgt_b or not rtype:
                    continue
                if src_b == tgt_b:
                    continue  # drop self-loops
                admitted.append((src_b, rtype, tgt_b))
                rel_types.add(rtype)
                endpoint_atoms.add(src_b)
                endpoint_atoms.add(tgt_b)
    # Optional subsample (smoke path).
    n_admitted_total = len(admitted)
    if max_ingest_triples is not None and n_admitted_total > max_ingest_triples:
        idx = rng.choice(n_admitted_total, size=max_ingest_triples, replace=False)
        admitted = [admitted[i] for i in sorted(idx.tolist())]
        # Re-collect rel_types and endpoints from the subsample.
        rel_types = set(); endpoint_atoms = set()
        for (s, r, t) in admitted:
            rel_types.add(r)
            endpoint_atoms.add(s)
            endpoint_atoms.add(t)
    # Build combined atom universe: chain-grade prefix FIRST (so anchors are 0..n_cg-1),
    # then every other endpoint atom (union with atomized for codebook honesty).
    combined: list[str] = []
    seen: set[str] = set()
    for aid in chain_grade_atom_ids:
        bare = _strip_corpus_prefix(aid)
        if bare in seen:
            continue
        combined.append(bare)
        seen.add(bare)
    n_chain_grade = len(combined)
    # Frontier portion: everything else that appears in admitted triples, plus
    # anything in atomized_atom_ids (in case we want to score it even if no
    # admitted triple references it -- keeps the codebook honest).
    frontier = (endpoint_atoms | atomized_atom_ids) - seen
    for b in sorted(frontier):
        combined.append(b)
        seen.add(b)
    bare_to_idx = {b: i for i, b in enumerate(combined)}
    # Second pass: convert admitted to index triples.
    triples: list[tuple[int, str, int]] = []
    for (s, r, t) in admitted:
        s_idx = bare_to_idx.get(s)
        t_idx = bare_to_idx.get(t)
        if s_idx is None or t_idx is None:
            continue
        if s_idx == t_idx:
            continue
        triples.append((s_idx, r, t_idx))
    print(
        "  -> scanned %d relations.jsonl files; admitted %d triples (subsample: %s); "
        "n_admitted_total_raw=%d" % (n_files, len(triples), str(max_ingest_triples),
                                     n_admitted_total),
        flush=True,
    )
    return triples, sorted(rel_types), combined, n_chain_grade


# ===== v1 cluster parse (for comparison; informational only in v2c) =====


def load_v1_clusters() -> dict[str, set[str]]:
    """Parse the most recent notes/capability_family_map_v1_*.md.

    Informational only in v2c; v1 was chain-grade-only lexical clustering.
    """
    notes_dir = REPO / "notes"
    if not notes_dir.is_dir():
        return {}
    cands = sorted(notes_dir.glob("capability_family_map_v1_*.md"))
    if not cands:
        return {}
    latest = cands[-1]
    text = latest.read_text(encoding="utf-8")
    clusters: dict[str, set[str]] = defaultdict(set)
    cur_family = None
    for line in text.splitlines():
        m = re.match(r"^### (\w[\w_]*) \(\d+", line)
        if m:
            cur_family = m.group(1)
            continue
        if cur_family is not None:
            m2 = re.match(r"^\s*-\s+`([^`]+)`", line)
            if m2:
                clusters[cur_family].add(m2.group(1))
    return dict(clusters)


def load_v1_cross_family_arrows() -> set[str]:
    """Parse the v1 'Cross-family atoms' table to get v1's set of multi-category short-names."""
    notes_dir = REPO / "notes"
    if not notes_dir.is_dir():
        return set()
    cands = sorted(notes_dir.glob("capability_family_map_v1_*.md"))
    if not cands:
        return set()
    text = cands[-1].read_text(encoding="utf-8")
    out: set[str] = set()
    in_table = False
    for line in text.splitlines():
        if line.startswith("| atom | categories spanned |"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                in_table = False
                continue
            m = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
            if m:
                out.add(m.group(1))
    return out


# ===== substrate-native cluster discovery =====


def encode_atoms_substrate(atom_ids: list[str], n_dim: int):
    """Encode each atom_id via CharTrigramEncoder; return (E_np[N, n_dim], encoder)."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    E = enc.encode_batch(atom_ids).astype(np.float32)
    return E, enc


def build_kg(E_np: np.ndarray, triples_idx: list[tuple[int, int, int]], n_ent: int,
             n_rel: int, n_dim: int, seed: int):
    """Substrate KG: char-trigram E codebook + random bipolar R + multi-value Hebbian W."""
    import torch
    from hdlab.kg_traversal import KGStore
    g = torch.Generator(); g.manual_seed(seed)
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=n_dim, generator=g)
    kg.E = torch.from_numpy(E_np)
    if triples_idx:
        triples_t = torch.tensor(triples_idx, dtype=torch.long)
        kg.ingest_triples(triples_t)
    return kg


def two_hop_neighborhood(kg, anchor: int, rel_pairs: list[tuple[int, int]], k_set: int) -> set[int]:
    """Run multi_hop.iter_cleanup_chain at each (p1, p2) pair; collect 2-hop reachable entities."""
    import torch
    from hdlab.multi_hop import iter_cleanup_chain
    nbr: set[int] = set()
    for (p1, p2) in rel_pairs:
        key1 = kg.key(anchor, p1)
        scores1 = kg.score_all(key1)
        topk1 = torch.topk(scores1, k=min(k_set, kg.n_ent))
        for v in topk1.indices.tolist():
            nbr.add(int(v))
        final, _confs, _term = iter_cleanup_chain(
            kg, start=anchor, relations=[p1, p2], k_set=k_set, beta=None,
            tau_terminate=None, k_inner=1, shuffle_top=False,
        )
        if final is not None:
            nbr.add(int(final))
    nbr.discard(anchor)
    return nbr


def jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two sets; |A ^ B| / |A v B|. Returns 0 for both empty."""
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def greedy_cluster(items: list[int], neighborhoods: dict[int, set[int]],
                   tau: float) -> list[set[int]]:
    """Greedy clustering of items by Jaccard overlap of their substrate-derived neighborhoods."""
    remaining = set(items)
    clusters: list[set[int]] = []
    while remaining:
        seed = next(iter(remaining))
        cluster = {seed}
        cluster_nbr = set(neighborhoods.get(seed, set()))
        changed = True
        while changed:
            changed = False
            for it in list(remaining - cluster):
                if jaccard(neighborhoods.get(it, set()), cluster_nbr) >= tau:
                    cluster.add(it)
                    cluster_nbr |= neighborhoods.get(it, set())
                    changed = True
        clusters.append(cluster)
        remaining -= cluster
    return clusters


def atom_id_short(atom_id: str) -> str:
    """Match the v1 short form: post-`/` last segment, capped at 60 chars."""
    short = atom_id.split("/")[-1]
    return short[:60]


def cross_family_arrows(clusters: list[set[int]], items: list[int],
                        anchor_to_atom_id: dict[int, str], v1_clusters: dict[str, set[str]],
                        jaccard_tau: float, neighborhoods: dict[int, set[int]]) -> list[dict]:
    """Identify substrate-derived multi-cluster anchors via overlap with multiple substrate-clusters."""
    cluster_nbrs = []
    for cl in clusters:
        union = set()
        for it in cl:
            union |= neighborhoods.get(it, set())
        cluster_nbrs.append(union)
    arrows = []
    for anchor in items:
        nbr = neighborhoods.get(anchor, set())
        if not nbr:
            continue
        scores = []
        for ci, cnbr in enumerate(cluster_nbrs):
            j = jaccard(nbr, cnbr)
            if j >= jaccard_tau:
                scores.append((ci, j))
        if len(scores) >= 2:
            arrows.append({
                "anchor_atom_id": anchor_to_atom_id[anchor],
                "anchor_short": atom_id_short(anchor_to_atom_id[anchor]),
                "n_substrate_clusters_above_tau": len(scores),
                "jaccards": [round(j, 3) for _, j in scores],
            })
    return arrows


def avg_jaccard_substrate_vs_v1(substrate_clusters: list[set[int]],
                                items: list[int], anchor_to_short: dict[int, str],
                                v1_clusters: dict[str, set[str]]) -> Tuple[float, list[dict]]:
    """For each substrate cluster, find the best-matching v1 cluster (informational)."""
    per_cluster = []
    js = []
    for ci, cl in enumerate(substrate_clusters):
        sub_shorts = {anchor_to_short[it] for it in cl}
        if not sub_shorts:
            continue
        best_v1 = None
        best_j = 0.0
        for fname, fatoms in v1_clusters.items():
            j = jaccard(sub_shorts, fatoms)
            if j > best_j:
                best_j = j
                best_v1 = fname
        per_cluster.append({
            "substrate_cluster": ci,
            "size": len(cl),
            "best_v1_family": best_v1,
            "best_jaccard": round(best_j, 3),
        })
        js.append(best_j)
    avg = float(np.mean(js)) if js else 0.0
    return avg, per_cluster


def atom_retrieval_recall(E_np: np.ndarray, atom_ids: list[str], encoder, n_probe: int,
                          rng: np.random.Generator) -> float:
    """Self-retrieve atom-by-id from char-trigram codebook; recall@1 = top-1 hit rate."""
    n = len(atom_ids)
    if n == 0:
        return 0.0
    idx = rng.permutation(n)[:min(n_probe, n)]
    hits = 0
    norms = np.linalg.norm(E_np, axis=1, keepdims=True) + 1e-8
    E_unit = E_np / norms
    for i in idx:
        q = encoder.encode(atom_ids[i])
        q_u = q / (np.linalg.norm(q) + 1e-8)
        sims = E_unit @ q_u
        if int(sims.argmax()) == int(i):
            hits += 1
    return hits / max(len(idx), 1)


def sample_relation_pairs(n_rel: int, n_pairs: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    """Sample n_pairs distinct (p1, p2) relation index pairs uniformly."""
    if n_rel <= 0:
        return []
    pairs: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    tries = 0
    while len(pairs) < n_pairs and tries < n_pairs * 50:
        tries += 1
        a = int(rng.integers(0, n_rel))
        b = int(rng.integers(0, n_rel))
        if (a, b) in seen:
            continue
        seen.add((a, b))
        pairs.append((a, b))
    return pairs


def shuffle_triple_relations(triples_idx: list[tuple[int, int, int]],
                             n_rel: int, rng: np.random.Generator
                             ) -> list[tuple[int, int, int]]:
    """RANDOM_RELATION control: each triple's relation type is replaced with a uniform random one."""
    out = []
    for (s, _r, o) in triples_idx:
        rr = int(rng.integers(0, n_rel))
        out.append((s, rr, o))
    return out


def cluster_coherence(clusters: list[set[int]], neighborhoods: dict[int, set[int]]) -> float:
    """Mean pairwise Jaccard among same-cluster anchors; informational only in v2c."""
    js = []
    for cl in clusters:
        members = list(cl)
        if len(members) < 2:
            continue
        pair_js = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                pair_js.append(jaccard(neighborhoods.get(members[i], set()),
                                        neighborhoods.get(members[j], set())))
        if pair_js:
            js.append(float(np.mean(pair_js)))
    if not js:
        return 0.0
    return float(np.mean(js))


# ===== per-seed runner =====


def run_seed(seed: int, combined_atoms: list[str], triples_str: list[tuple[int, str, int]],
             rel_types: list[str], n_chain_grade: int, v1_clusters: dict[str, set[str]],
             v1_cross_arrows: set[str]) -> dict:
    """Single seed: build substrate KG over FULL-Store triples, traverse, cluster; both arms."""
    t_start = time.time()
    rng = np.random.default_rng(seed)
    n_ent = len(combined_atoms)
    rel_to_idx = {r: i for i, r in enumerate(rel_types)}
    n_rel = len(rel_types)
    triples_idx = [(s, rel_to_idx[r], o) for (s, r, o) in triples_str]
    # ----- encode atoms via substrate primitive (char-trigram) -----
    t_enc0 = time.time()
    E_np, encoder = encode_atoms_substrate(combined_atoms, N_DIM)
    t_enc = round(time.time() - t_enc0, 1)
    print("  [seed=%d] encoded %d atoms at N=%d in %.1fs" % (seed, n_ent, N_DIM, t_enc),
          flush=True)
    # ----- atom retrieval recall sanity (subsample to 200 probes; full 177k too costly) -----
    n_probe = min(n_ent, 200)
    recall = atom_retrieval_recall(E_np, combined_atoms, encoder, n_probe,
                                    np.random.default_rng(seed + 1))
    # ----- anchor subset (capped; SAMPLED FROM CHAIN-GRADE PREFIX ONLY) -----
    if n_chain_grade <= N_ANCHORS:
        anchors = list(range(n_chain_grade))
    else:
        anchors = sorted(rng.choice(n_chain_grade, N_ANCHORS, replace=False).tolist())
    anchor_to_atom_id = {a: combined_atoms[a] for a in anchors}
    anchor_to_short = {a: atom_id_short(combined_atoms[a]) for a in anchors}

    # ===== ARM A: REAL relations =====
    t_real0 = time.time()
    kg_real = build_kg(E_np, triples_idx, n_ent, n_rel, N_DIM, seed)
    pairs_real = sample_relation_pairs(n_rel, N_RELATION_SAMPLES,
                                        np.random.default_rng(seed + 2))
    nbr_real: dict[int, set[int]] = {}
    for a in anchors:
        nbr_real[a] = two_hop_neighborhood(kg_real, a, pairs_real, K_SET)
    clusters_real = greedy_cluster(anchors, nbr_real, JACCARD_CLUSTER_TAU)
    coherence_real = cluster_coherence(clusters_real, nbr_real)
    avg_j_real, per_cluster_real = avg_jaccard_substrate_vs_v1(
        clusters_real, anchors, anchor_to_short, v1_clusters)
    arrows_real = cross_family_arrows(clusters_real, anchors, anchor_to_atom_id,
                                       v1_clusters, JACCARD_VS_V1_TAU, nbr_real)
    new_arrows = [a for a in arrows_real if a["anchor_short"] not in v1_cross_arrows]
    n_new_arrows_real = len(new_arrows)
    t_real = round(time.time() - t_real0, 1)
    print("  [seed=%d] arm REAL  done in %.1fs (clusters=%d coh=%.3f)"
          % (seed, t_real, len(clusters_real), coherence_real), flush=True)

    # ===== ARM B: RANDOM_RELATION control (Fix #16) =====
    t_shuf0 = time.time()
    triples_shuf = shuffle_triple_relations(triples_idx, n_rel,
                                             np.random.default_rng(seed + 3))
    kg_shuf = build_kg(E_np, triples_shuf, n_ent, n_rel, N_DIM, seed)
    pairs_shuf = sample_relation_pairs(n_rel, N_RELATION_SAMPLES,
                                        np.random.default_rng(seed + 4))
    nbr_shuf: dict[int, set[int]] = {}
    for a in anchors:
        nbr_shuf[a] = two_hop_neighborhood(kg_shuf, a, pairs_shuf, K_SET)
    clusters_shuf = greedy_cluster(anchors, nbr_shuf, JACCARD_CLUSTER_TAU)
    coherence_shuf = cluster_coherence(clusters_shuf, nbr_shuf)
    avg_j_shuf, _per_cluster_shuf = avg_jaccard_substrate_vs_v1(
        clusters_shuf, anchors, anchor_to_short, v1_clusters)
    arrows_shuf = cross_family_arrows(clusters_shuf, anchors, anchor_to_atom_id,
                                       v1_clusters, JACCARD_VS_V1_TAU, nbr_shuf)
    new_arrows_shuf = [a for a in arrows_shuf if a["anchor_short"] not in v1_cross_arrows]
    n_new_arrows_shuf = len(new_arrows_shuf)
    t_shuf = round(time.time() - t_shuf0, 1)
    print("  [seed=%d] arm SHUF  done in %.1fs (clusters=%d coh=%.3f)"
          % (seed, t_shuf, len(clusters_shuf), coherence_shuf), flush=True)

    elapsed = round(time.time() - t_start, 1)

    print(
        "  [seed=%d] real: clusters=%d coh=%.3f avg_J_vs_v1=%.3f new_arrows=%d | "
        "shuf: clusters=%d coh=%.3f avg_J=%.3f new_arrows=%d | recall=%.3f | %.1fs"
        % (seed, len(clusters_real), coherence_real, avg_j_real, n_new_arrows_real,
           len(clusters_shuf), coherence_shuf, avg_j_shuf, n_new_arrows_shuf, recall, elapsed),
        flush=True,
    )

    return {
        "seed": seed,
        "_ckpt_key": str(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_chain_grade_atoms": n_chain_grade,
        "n_atoms_universe": n_ent,
        "n_relation_types": n_rel,
        "n_triples": len(triples_idx),
        "n_anchors": len(anchors),
        "atom_retrieval_recall": round(recall, 4),
        "elapsed_s": elapsed,
        "t_encoding_s": t_enc,
        "t_arm_real_s": t_real,
        "t_arm_shuf_s": t_shuf,
        "real": {
            "n_clusters": len(clusters_real),
            "coherence": round(coherence_real, 4),
            "avg_jaccard_vs_v1": round(avg_j_real, 4),
            "per_cluster_match": per_cluster_real,
            "n_cross_family_arrows_total": len(arrows_real),
            "n_new_cross_family_arrows": n_new_arrows_real,
            "new_arrows_examples": [a["anchor_short"] for a in new_arrows][:10],
        },
        "shuffle_control": {
            "n_clusters": len(clusters_shuf),
            "coherence": round(coherence_shuf, 4),
            "avg_jaccard_vs_v1": round(avg_j_shuf, 4),
            "n_cross_family_arrows_total": len(arrows_shuf),
            "n_new_cross_family_arrows": n_new_arrows_shuf,
        },
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


# ===== verdict =====


def verdict(per_seed_records: list[dict]) -> Tuple[str, str]:
    """v2c HARD bands match v2b: n_clusters_real and (n_clusters_real - n_clusters_shuf)."""
    if not per_seed_records:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed records")
    n_clusters_real = [p["real"]["n_clusters"] for p in per_seed_records]
    n_clusters_shuf = [p["shuffle_control"]["n_clusters"] for p in per_seed_records]
    recalls = [p["atom_retrieval_recall"] for p in per_seed_records]
    llm_calls = [p.get("n_llm_calls", 0) for p in per_seed_records]
    n_clusters_mean = float(np.mean(n_clusters_real))
    n_clusters_shuf_mean = float(np.mean(n_clusters_shuf))
    cluster_gap = n_clusters_mean - n_clusters_shuf_mean
    recall_mean = float(np.mean(recalls))
    if len(n_clusters_real) > 1 and np.mean(n_clusters_real) > 0:
        cv = float(np.std(n_clusters_real) / np.mean(n_clusters_real))
    else:
        cv = 0.0
    coh_real = [p["real"]["coherence"] for p in per_seed_records]
    coh_shuf = [p["shuffle_control"]["coherence"] for p in per_seed_records]
    avg_js = [p["real"]["avg_jaccard_vs_v1"] for p in per_seed_records]
    new_arrows = [p["real"]["n_new_cross_family_arrows"] for p in per_seed_records]

    summary = (
        "n_clusters_real=%.1f (pass %d / middle %d) | n_clusters_shuf=%.1f | "
        "cluster_gap=%.1f (pass %d / middle %d) | recall=%.3f (pass %.2f / fail %.2f) | "
        "cv_clusters=%.3f (pass %.2f) | n_llm=%d | info: coh_real=%.3f coh_shuf=%.3f "
        "avg_J_vs_v1=%.3f new_arrows=%.1f"
    ) % (
        n_clusters_mean, N_CLUSTERS_REAL_PASS, N_CLUSTERS_REAL_MIDDLE,
        n_clusters_shuf_mean, cluster_gap, N_CLUSTERS_GAP_PASS, N_CLUSTERS_GAP_MIDDLE,
        recall_mean, RECALL_PASS, RECALL_FAIL,
        cv, CV_PASS, max(llm_calls),
        float(np.mean(coh_real)), float(np.mean(coh_shuf)),
        float(np.mean(avg_js)), float(np.mean(new_arrows)),
    )
    if max(llm_calls) > 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated; n_llm_calls>0. " + summary)
    if recall_mean < RECALL_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: atom retrieval recall below floor. " + summary)
    if n_clusters_mean <= 1.0:
        return (
            "HARD_FAIL",
            "HARD_FAIL: mechanism null on FULL-Store ingest (n_clusters_real<=1); "
            "substrate-native self-mapping fails even given the entire atomized graph. "
            + summary,
        )
    if cluster_gap <= N_CLUSTERS_GAP_FAIL:
        return (
            "HARD_FAIL",
            "HARD_FAIL: shuffle as granular as real (cluster_gap<=0); "
            "relation-conditioned mechanism null on full Store. " + summary,
        )
    pass_n_clusters = n_clusters_mean >= N_CLUSTERS_REAL_PASS
    pass_gap = cluster_gap >= N_CLUSTERS_GAP_PASS
    pass_recall = recall_mean >= RECALL_PASS
    pass_cv = (cv <= CV_PASS) if len(n_clusters_real) > 1 else True
    pass_no_llm = max(llm_calls) == 0
    if pass_n_clusters and pass_gap and pass_recall and pass_cv and pass_no_llm:
        return (
            "HARD_PASS",
            "HARD_PASS: v2c substrate self-maps FULL-Store atomized KG; clusters>=3 + "
            "real-vs-shuffle cluster-count gap>=2; stable + zero-LLM. " + summary,
        )
    if n_clusters_mean >= N_CLUSTERS_REAL_MIDDLE and cluster_gap >= N_CLUSTERS_GAP_MIDDLE:
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: mechanism present but below HARD_PASS bars on full Store. " + summary,
        )
    return (
        "HARD_FAIL",
        "HARD_FAIL: v2c below pre-reg bars (mechanism weak or unstable). " + summary,
    )


# ===== main =====


if __name__ == "__main__":
    print(
        "[config] anchor=%s mode=%s seeds=%s N=%d | %s"
        % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION),
        flush=True,
    )
    t0 = time.time()
    print("[load] cert_ledger chain-grade atoms...", flush=True)
    chain_grade_atoms = load_chain_grade_atom_ids()
    print("  -> %d chain-grade atoms" % len(chain_grade_atoms), flush=True)
    print("[load] atomized atom universe across all corpora atoms.jsonl...", flush=True)
    atomized = load_atomized_atom_ids()
    print("  -> %d atomized atom_ids" % len(atomized), flush=True)
    print("[load] FULL-Store relations admit (every relations.jsonl triple)...", flush=True)
    load_rng = np.random.default_rng(0)  # deterministic subsample seed for smoke
    triples_str, rel_types, combined_atoms, n_chain_grade = load_relations_for(
        chain_grade_atoms, atomized, MAX_INGEST_TRIPLES, load_rng)
    print(
        "  -> %d admitted triples; %d distinct relation types; first 8: %s"
        % (len(triples_str), len(rel_types), rel_types[:8]),
        flush=True,
    )
    print(
        "  -> %d combined atoms (%d chain-grade prefix + %d frontier)"
        % (len(combined_atoms), n_chain_grade, len(combined_atoms) - n_chain_grade),
        flush=True,
    )
    if not triples_str or not rel_types:
        print("[error] no v2c-admitted triples found; aborting", flush=True)
        sys.exit(2)
    print("[load] v1 clusters from latest capability_family_map_v1_*.md (informational)...",
          flush=True)
    v1_clusters = load_v1_clusters()
    v1_cross_arrows = load_v1_cross_family_arrows()
    print(
        "  -> %d v1 families; %d v1 cross-family atoms"
        % (len(v1_clusters), len(v1_cross_arrows)),
        flush=True,
    )

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        "[ckpt] %d of %d seeds already complete; running %s"
        % (len(done), len(SEEDS), remaining),
        flush=True,
    )

    for s in remaining:
        rec = run_seed(s, combined_atoms, triples_str, rel_types, n_chain_grade,
                       v1_clusters, v1_cross_arrows)
        write_partial(out_dir, s, rec)

    agg = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    v, vmsg = verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION,
        "per_seed": per_seed,
        "zero_llm_calls_at_inference": all(p.get("n_llm_calls", 0) == 0 for p in per_seed),
        "elapsed_s": round(time.time() - t0, 1),
        "DESIGN_NOTE": (
            "Phase 1 substrate-native self-mapping (v2c FULL-Store ingest) per USER 2026-06-22 "
            "strategic vision. v2c is the Option-2 recovery path from v2b MIDDLE_BAND: ingest "
            "EVERY relations.jsonl triple across all corpora (~200k relations / ~177k atoms); "
            "anchor sampling still restricted to chain-grade (~447 atoms). Bands match v2b; "
            "scope change is the only variable. char_trigram + KGStore + multi_hop are "
            "substrate primitives. Mechanism = substrate self-maps how chain-grade atoms sit "
            "in the FULL atomized graph; HARD_PASS means substrate finds at least 3 clusters "
            "of chain-grade atoms with cluster_gap>=2 over shuffled-relation control."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
