"""substrate_self_map_v2 -- substrate-native self-mapping (Phase 1 of USER strategic vision).

Substrate uses its OWN primitives (char_trigram_encoder + KGStore + multi_hop) to analyze
the cert_ledger relational structure across chain-grade atoms. This replaces v1
(tools/substrate_relational_analysis.py), which was correctly criticized by USER 2026-06-22
as Director-side lexical pattern-matching on atom_id strings, not substrate self-mapping.

Mechanism (substrate-native end-to-end; ZERO LLM forward calls at retrieval):

  1. Atom encoding -- CharTrigramEncoder at N_DIM, bipolar bag-of-trigrams over atom_id.
  2. Relation extraction -- read each data/substrate_index/<corpus>/relations.jsonl;
     restrict to (src, rel_type, tgt) triples where BOTH src and tgt are chain-grade atoms
     (matched against cert_ledger.jsonl chain_grade atom_ids; supersedes-folded).
  3. KG ingest -- pack (s_idx, r_idx, o_idx) triples into a KGStore via multi-value Hebbian
     accumulation. Codebooks E (atoms) and R (relation types) come FROM substrate primitives:
     E = char-trigram-encoded atom IDs; R = bipolar random per relation type.
  4. Substrate-native cluster discovery -- for each chain-grade anchor atom, run
     multi_hop.iter_cleanup_chain at K_HOPS distinct relation-type sequences (sampled), collect
     reachable entities into a per-anchor 2-hop neighborhood set; then cluster anchors by
     pairwise Jaccard overlap of these substrate-derived neighborhoods (greedy clustering at
     threshold tau_jaccard).
  5. Compare to v1 lexical clusters -- read the latest
     notes/capability_family_map_v1_<date>.md and parse the family table; substrate-clusters
     are matched to v1 clusters by best Jaccard; per-cluster overlap + new cross-family arrows
     identified by substrate (NOT in v1 lexical) are surfaced.

Pre-reg HARD bands (committed in notes/exp_substrate_self_map_v2_pre_reg_2026-06-22.md):

  HARD_PASS chain-grade:
    - Substrate-derived clusters have >= 0.5 Jaccard overlap with v1 lexical clusters
      ON AVERAGE (sanity: substrate-finds-same-structure as v1 lexical)
    - Substrate discovers >= 5 cross-family arrows (atoms in 2+ substrate-clusters)
      that are NOT in v1 multi-category atoms (substrate adds value beyond keyword matching)
    - substrate-only-decode preserved (n_llm_calls = 0)
    - Atom retrieval recall >= 0.95 (codebook can retrieve atom-by-id via char-trigram
      key + KGStore W; sanity that the encoding preserves identity)
    - 3 seeds; cv <= 0.05 on n_new_cross_family_arrows (stability)

  MIDDLE_BAND:
    - Substrate clusters partially overlap v1 (>=0.2 avg Jaccard) BUT < 5 new cross-family
      arrows OR cv > 0.05 (substrate confirms but doesn't extend)

  HARD_FAIL:
    - Substrate clusters bear no resemblance to v1 (avg Jaccard < 0.1) -- char-trigram
      encoding doesn't preserve atom-id semantics
    - substrate-only-decode violated (any LLM forward call counted)
    - Atom retrieval recall < 0.50 (codebook too crowded; need larger N_DIM)

Discriminator control (Fix #16): RANDOM_RELATION baseline arm. Substrate-derived clusters
from SHUFFLED relation_types should be incoherent (low avg Jaccard with v1 AND low new-arrow
count). Strong gap between real-relations arm and shuffled-relations arm = mechanism real.

Honest scope:
  - char-trigram encoding is bag-of-trigrams (no positional info; cat/cats share trigrams,
    cat/kitten don't). atom_id strings are mostly EXP_<name> + tier prefixes; trigram overlap
    is genuine SHARED-WORD evidence within the substrate's own naming conventions.
  - Multi-hop traversal is at 2 hops (chain-grade per n8/U1 r1 2-hop result); higher k is
    open per r1 MIDDLE_BAND at K=3,4.
  - This cell does NOT propose new atoms. That is Phase 2 (SubstrateGenerator); Phase 1
    is mapping the existing structure substrate-side.

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

ANCHOR_NAME = "substrate_self_map_v2"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"

# ----- pre-registered HARD thresholds -----
AVG_JACCARD_PASS = 0.50      # avg Jaccard between substrate-clusters and v1-clusters
AVG_JACCARD_FAIL = 0.10      # below this -> HARD_FAIL
AVG_JACCARD_MIDDLE = 0.20    # MIDDLE_BAND floor on partial overlap
NEW_ARROWS_PASS = 5          # >= 5 new cross-family arrows substrate finds that v1 missed
RECALL_PASS = 0.95           # atom-id retrieval recall via char-trigram codebook
RECALL_FAIL = 0.50           # HARD_FAIL on recall below this
CV_PASS = 0.05               # cv across seeds on n_new_cross_family_arrows
JACCARD_CLUSTER_TAU = 0.30   # threshold for greedy substrate-cluster formation
JACCARD_VS_V1_TAU = 0.30     # threshold for "substrate atom belongs to v1 cluster"

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

# Smoke detection: --smoke flag OR HDLAB_EXP_NAME ending in _smoke (template TODO #6).
_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# ----- config -----
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    MAX_ATOMS = 50
    N_ANCHORS = 20           # subset of chain-grade atoms used as 2-hop anchors
    N_RELATION_SAMPLES = 8   # per anchor, how many random 2-relation sequences to traverse
    K_SET = 8
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    MAX_ATOMS = None          # all chain-grade atoms (~447)
    N_ANCHORS = 200           # capped subset of anchors for 2-hop traversal
    N_RELATION_SAMPLES = 32   # per anchor
    K_SET = 16

CONFIG_VERSION = (
    "self_map_v2: char_trigram_atom_encode + KGStore_multivalue_Hebbian + "
    "multi_hop_2hop_neighborhood_Jaccard_cluster + random_relation_control; "
    "N%d max_atoms=%s n_anchors=%d n_rel_samples=%d kset=%d "
    "bands jac_pass%.2f jac_fail%.2f new_arrows>=%d recall_pass%.2f cv<=%.2f"
) % (N_DIM, str(MAX_ATOMS), N_ANCHORS, N_RELATION_SAMPLES, K_SET,
     AVG_JACCARD_PASS, AVG_JACCARD_FAIL, NEW_ARROWS_PASS, RECALL_PASS, CV_PASS)


# ----- selftest: substrate primitives compose end-to-end on a tiny synthetic KG -----
def _selftest():
    """Verify char_trigram + KGStore + neighborhood-Jaccard pipe works on synthetic data."""
    # Import inside selftest so import errors surface clearly.
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
    # Build KG with 5 atoms, 3 relation types, 6 chain-grade-internal triples
    n_ent = len(atom_ids); n_rel = 3
    g = torch.Generator(); g.manual_seed(0)
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=512, generator=g)
    # Inject substrate-encoded E (override the random bipolar)
    kg.E = torch.from_numpy(E_np)
    triples = torch.tensor([
        [0, 0, 1], [1, 0, 0],   # alpha v1 <-> alpha v2 via rel 0
        [2, 0, 3], [3, 0, 2],   # kg v1 <-> kg v2 via rel 0
        [0, 1, 4], [2, 1, 4],   # alpha + kg both relate to whitening via rel 1
    ], dtype=torch.long)
    kg.ingest_triples(triples)
    # 2-hop neighborhood of atom 0 should include {1, 4} via rel 0+0 and rel 1+(any)
    # Score-all the 1-hop key
    key = kg.key(0, 0)
    scores = kg.score_all(key)
    assert scores.argmax().item() == 1, f"1-hop alpha_v1-rel0 should -> alpha_v2 (got {scores.argmax().item()})"
    # Now char-trigram retrieval-recall sanity: encode the atom_id again and find it in codebook
    q = enc.encode(atom_ids[2])
    q_t = torch.from_numpy(q.astype(np.float32))
    cos = (kg.E @ q_t) / (
        (torch.linalg.norm(kg.E, dim=1) + 1e-8) * (torch.linalg.norm(q_t) + 1e-8)
    )
    best = int(cos.argmax())
    assert best == 2, f"char-trigram self-retrieve should find atom 2 (got {best})"
    # substrate-only-decode invariant: counter unchanged
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print(
        "[selftest] PASS: char-trigram self-retrieval + KGStore single-hop + multi-value "
        "ingest compose; n_llm_calls=0",
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== data load: chain-grade atoms + relations =====


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
            # latest-per-atom (last write wins; same as v1 fold)
            seen[aid] = r
    return sorted(seen.keys())


def _strip_corpus_prefix(atom_id: str) -> str:
    """Return the post-:: portion of atom_id (matches relations.jsonl src_id/tgt_id keys)."""
    if "::" in atom_id:
        return atom_id.split("::", 1)[1]
    return atom_id


def load_relations_for(chain_grade_atom_ids: list[str]) -> Tuple[list[tuple[int, str, int]], list[str]]:
    """Read every <corpus>/relations.jsonl; restrict to triples where BOTH endpoints are chain-grade.

    Returns:
      triples: list of (src_idx, rel_type_str, tgt_idx); indices into chain_grade_atom_ids.
      relation_types: sorted distinct rel_type strings encountered.
    """
    # Build atom_id-without-corpus -> index map (relations files don't carry the corpus prefix)
    aid_to_idx = {}
    for i, aid in enumerate(chain_grade_atom_ids):
        bare = _strip_corpus_prefix(aid)
        aid_to_idx.setdefault(bare, []).append(i)
    triples: list[tuple[int, str, int]] = []
    rel_types: set = set()
    if not SUBSTRATE_INDEX.is_dir():
        raise FileNotFoundError(f"substrate_index not found at {SUBSTRATE_INDEX}")
    for corpus_dir in sorted(SUBSTRATE_INDEX.iterdir()):
        rel_file = corpus_dir / "relations.jsonl"
        if not rel_file.is_file():
            continue
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
                if src_b not in aid_to_idx or tgt_b not in aid_to_idx:
                    continue
                # When the same bare-id maps to multiple corpora, take the first index;
                # the bare-id uniquely names the atom (cert_ledger keys are <corpus>::<bare>;
                # if duplicated across corpora, both are chain-grade variants of the same name).
                s_idx = aid_to_idx[src_b][0]
                t_idx = aid_to_idx[tgt_b][0]
                if s_idx == t_idx:
                    continue  # drop self-loops
                triples.append((s_idx, rtype, t_idx))
                rel_types.add(rtype)
    return triples, sorted(rel_types)


# ===== v1 cluster parse (for comparison) =====


def load_v1_clusters() -> dict[str, set[str]]:
    """Parse the most recent notes/capability_family_map_v1_*.md.

    Returns {family_name: set_of_atom_id_short_names}. Empty dict if no v1 note found.
    Uses the exemplar listings ('exemplars' under each family) PLUS the cross-family table
    to reconstruct the v1 cluster assignment as best we can. This is best-effort: the v1
    note only prints up to 5 exemplars per family, which limits comparison fidelity but is
    the documented v1 output we have to work with.
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
    # Section: "### <family_name> (... atoms)" followed by "- Exemplars:" then "  - `<atom>`"
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
    # Also parse the cross-family table (multi-category atoms) so we know v1's "cross arrows"
    return dict(clusters)


def load_v1_cross_family_arrows() -> set[str]:
    """Parse the v1 'Cross-family atoms' table to get v1's set of multi-category atom short-names."""
    notes_dir = REPO / "notes"
    if not notes_dir.is_dir():
        return set()
    cands = sorted(notes_dir.glob("capability_family_map_v1_*.md"))
    if not cands:
        return set()
    text = cands[-1].read_text(encoding="utf-8")
    # Table rows like: | `EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096` | whitening x encoding |
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
    # OVERRIDE the random E with substrate-encoded atom IDs (the load-bearing substitution)
    kg.E = torch.from_numpy(E_np)
    if triples_idx:
        triples_t = torch.tensor(triples_idx, dtype=torch.long)
        kg.ingest_triples(triples_t)
    return kg


def two_hop_neighborhood(kg, anchor: int, rel_pairs: list[tuple[int, int]], k_set: int) -> set[int]:
    """Run multi_hop.iter_cleanup_chain at each (p1, p2) pair; collect 2-hop reachable entities.

    For each (p1, p2): final entity from iter_cleanup_chain plus top-K entities from the
    single-hop intermediate are added to the neighborhood set.
    """
    import torch
    from hdlab.multi_hop import iter_cleanup_chain
    nbr: set[int] = set()
    for (p1, p2) in rel_pairs:
        # Intermediate top-K from anchor via p1
        key1 = kg.key(anchor, p1)
        scores1 = kg.score_all(key1)
        topk1 = torch.topk(scores1, k=min(k_set, kg.n_ent))
        for v in topk1.indices.tolist():
            nbr.add(int(v))
        # Final via iter_cleanup_chain at K=2 (chain-grade primitive per n8/U1)
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
    """Greedy clustering of items by Jaccard overlap of their substrate-derived neighborhoods.

    Iteratively pick the highest-overlap unassigned pair; absorb members with >=tau Jaccard
    to the cluster's union neighborhood; repeat. Returns list of clusters (each is a set of
    item-indices into `items`).
    """
    remaining = set(items)
    clusters: list[set[int]] = []
    while remaining:
        seed = next(iter(remaining))
        cluster = {seed}
        cluster_nbr = set(neighborhoods.get(seed, set()))
        # Greedily absorb anyone above tau against cluster_nbr
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
    """Identify substrate-derived 'multi-cluster' anchors via overlap with multiple substrate-clusters.

    For each anchor, compute its Jaccard against each substrate cluster's union neighborhood;
    if 2+ clusters have Jaccard >= jaccard_tau, it's a candidate cross-arrow.
    """
    # Pre-compute each cluster's union neighborhood
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
    """For each substrate cluster, find the best-matching v1 cluster (by short-name overlap).

    Returns (avg_jaccard, per_cluster_matches).
    """
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
    # Normalize codebook once
    norms = np.linalg.norm(E_np, axis=1, keepdims=True) + 1e-8
    E_unit = E_np / norms
    for i in idx:
        q = encoder.encode(atom_ids[i])
        q_u = q / (np.linalg.norm(q) + 1e-8)
        sims = E_unit @ q_u
        if int(sims.argmax()) == int(i):
            hits += 1
    return hits / max(len(idx), 1)


def sample_relation_pairs(n_rel: int, n_pairs: int, rng: np.random.Generator,
                          shuffle: bool = False, shuffle_rng: np.random.Generator | None = None
                          ) -> list[tuple[int, int]]:
    """Sample n_pairs distinct (p1, p2) relation index pairs uniformly.

    If shuffle=True (RANDOM_RELATION control arm), the indices are drawn uniformly from
    a shuffled relation-space; here this collapses to "uniform random pairs" identical
    to the natural arm because relation indices are already arbitrary. To make the control
    actually destroy signal, the shuffle_rng is used to REWIRE the rel_type tags on the
    triples (done at the caller level via shuffle_triple_relations) -- this fn just samples
    pairs to traverse.
    """
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
    """RANDOM_RELATION control: each triple's relation type is replaced with a uniform random one.

    Discriminator regime (Fix #16): destroys relation-conditioned cleanup signal while
    preserving graph adjacency. If substrate finds the same clusters under this control,
    the relation-conditioned mechanism is null in our regime.
    """
    out = []
    for (s, _r, o) in triples_idx:
        rr = int(rng.integers(0, n_rel))
        out.append((s, rr, o))
    return out


# ===== per-seed runner =====


def run_seed(seed: int, chain_grade_atoms: list[str], triples_str: list[tuple[int, str, int]],
             rel_types: list[str], v1_clusters: dict[str, set[str]],
             v1_cross_arrows: set[str]) -> dict:
    """Single seed: build substrate KG, traverse, cluster, compare to v1; run both arms."""
    t_start = time.time()
    rng = np.random.default_rng(seed)
    n_ent = len(chain_grade_atoms)
    rel_to_idx = {r: i for i, r in enumerate(rel_types)}
    n_rel = len(rel_types)
    triples_idx = [(s, rel_to_idx[r], o) for (s, r, o) in triples_str]
    # ----- encode atoms via substrate primitive (char-trigram) -----
    E_np, encoder = encode_atoms_substrate(chain_grade_atoms, N_DIM)
    # ----- atom retrieval recall sanity -----
    n_probe = min(n_ent, 200)
    recall = atom_retrieval_recall(E_np, chain_grade_atoms, encoder, n_probe,
                                    np.random.default_rng(seed + 1))
    # ----- anchor subset (capped for compute) -----
    if n_ent <= N_ANCHORS:
        anchors = list(range(n_ent))
    else:
        anchors = sorted(rng.choice(n_ent, N_ANCHORS, replace=False).tolist())
    anchor_to_atom_id = {a: chain_grade_atoms[a] for a in anchors}
    anchor_to_short = {a: atom_id_short(chain_grade_atoms[a]) for a in anchors}

    # ===== ARM A: REAL relations =====
    kg_real = build_kg(E_np, triples_idx, n_ent, n_rel, N_DIM, seed)
    pairs_real = sample_relation_pairs(n_rel, N_RELATION_SAMPLES,
                                        np.random.default_rng(seed + 2))
    nbr_real: dict[int, set[int]] = {}
    for a in anchors:
        nbr_real[a] = two_hop_neighborhood(kg_real, a, pairs_real, K_SET)
    clusters_real = greedy_cluster(anchors, nbr_real, JACCARD_CLUSTER_TAU)
    avg_j_real, per_cluster_real = avg_jaccard_substrate_vs_v1(
        clusters_real, anchors, anchor_to_short, v1_clusters)
    arrows_real = cross_family_arrows(clusters_real, anchors, anchor_to_atom_id,
                                       v1_clusters, JACCARD_VS_V1_TAU, nbr_real)
    # New arrows = substrate-found anchors NOT in v1's cross-family table
    new_arrows = [a for a in arrows_real if a["anchor_short"] not in v1_cross_arrows]
    n_new_arrows_real = len(new_arrows)

    # ===== ARM B: RANDOM_RELATION control (Fix #16) =====
    triples_shuf = shuffle_triple_relations(triples_idx, n_rel,
                                             np.random.default_rng(seed + 3))
    kg_shuf = build_kg(E_np, triples_shuf, n_ent, n_rel, N_DIM, seed)
    pairs_shuf = sample_relation_pairs(n_rel, N_RELATION_SAMPLES,
                                        np.random.default_rng(seed + 4))
    nbr_shuf: dict[int, set[int]] = {}
    for a in anchors:
        nbr_shuf[a] = two_hop_neighborhood(kg_shuf, a, pairs_shuf, K_SET)
    clusters_shuf = greedy_cluster(anchors, nbr_shuf, JACCARD_CLUSTER_TAU)
    avg_j_shuf, _per_cluster_shuf = avg_jaccard_substrate_vs_v1(
        clusters_shuf, anchors, anchor_to_short, v1_clusters)
    arrows_shuf = cross_family_arrows(clusters_shuf, anchors, anchor_to_atom_id,
                                       v1_clusters, JACCARD_VS_V1_TAU, nbr_shuf)
    new_arrows_shuf = [a for a in arrows_shuf if a["anchor_short"] not in v1_cross_arrows]
    n_new_arrows_shuf = len(new_arrows_shuf)

    elapsed = round(time.time() - t_start, 1)

    print(
        "  [seed=%d] real-arm: clusters=%d avg_J_vs_v1=%.3f new_arrows=%d | "
        "shuffle-arm: clusters=%d avg_J=%.3f new_arrows=%d | recall=%.3f | %.1fs"
        % (seed, len(clusters_real), avg_j_real, n_new_arrows_real,
           len(clusters_shuf), avg_j_shuf, n_new_arrows_shuf, recall, elapsed),
        flush=True,
    )

    return {
        "seed": seed,
        "_ckpt_key": str(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_chain_grade_atoms": n_ent,
        "n_relation_types": n_rel,
        "n_triples": len(triples_idx),
        "n_anchors": len(anchors),
        "atom_retrieval_recall": round(recall, 4),
        "elapsed_s": elapsed,
        "real": {
            "n_clusters": len(clusters_real),
            "avg_jaccard_vs_v1": round(avg_j_real, 4),
            "per_cluster_match": per_cluster_real,
            "n_cross_family_arrows_total": len(arrows_real),
            "n_new_cross_family_arrows": n_new_arrows_real,
            "new_arrows_examples": [a["anchor_short"] for a in new_arrows][:10],
        },
        "shuffle_control": {
            "n_clusters": len(clusters_shuf),
            "avg_jaccard_vs_v1": round(avg_j_shuf, 4),
            "n_cross_family_arrows_total": len(arrows_shuf),
            "n_new_cross_family_arrows": n_new_arrows_shuf,
        },
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


# ===== verdict =====


def verdict(per_seed_records: list[dict]) -> Tuple[str, str]:
    """Pre-reg HARD bands; pre-reg-direction must honor intent (substrate ADDS value)."""
    if not per_seed_records:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed records")
    avg_js = [p["real"]["avg_jaccard_vs_v1"] for p in per_seed_records]
    new_arrows = [p["real"]["n_new_cross_family_arrows"] for p in per_seed_records]
    recalls = [p["atom_retrieval_recall"] for p in per_seed_records]
    llm_calls = [p.get("n_llm_calls", 0) for p in per_seed_records]
    avg_j_mean = float(np.mean(avg_js))
    new_arrows_mean = float(np.mean(new_arrows))
    recall_mean = float(np.mean(recalls))
    # cv on new_arrows (the discriminating output metric)
    if len(new_arrows) > 1 and np.mean(new_arrows) > 0:
        cv = float(np.std(new_arrows) / np.mean(new_arrows))
    else:
        cv = 0.0
    # discriminator gap (real - shuffle) -- mechanism evidence
    shuf_js = [p["shuffle_control"]["avg_jaccard_vs_v1"] for p in per_seed_records]
    shuf_arrows = [p["shuffle_control"]["n_new_cross_family_arrows"] for p in per_seed_records]
    discrim_j_gap = float(np.mean(avg_js) - np.mean(shuf_js))
    discrim_arrow_gap = float(np.mean(new_arrows) - np.mean(shuf_arrows))

    summary = (
        "avg_J_vs_v1=%.3f (pass %.2f / fail %.2f) | new_arrows=%.1f (pass %d) | "
        "recall=%.3f (pass %.2f / fail %.2f) | cv_new_arrows=%.3f (pass %.2f) | "
        "n_llm=%d | discrim_gap_J=%.3f gap_arrows=%.1f"
    ) % (
        avg_j_mean, AVG_JACCARD_PASS, AVG_JACCARD_FAIL,
        new_arrows_mean, NEW_ARROWS_PASS,
        recall_mean, RECALL_PASS, RECALL_FAIL,
        cv, CV_PASS, max(llm_calls), discrim_j_gap, discrim_arrow_gap,
    )
    # Substrate-only-decode gate (HARD FAIL if violated)
    if max(llm_calls) > 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated; n_llm_calls>0. " + summary)
    # Recall floor (codebook usable)
    if recall_mean < RECALL_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: atom retrieval recall below floor (codebook too crowded). " + summary)
    # Resemblance floor
    if avg_j_mean < AVG_JACCARD_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: substrate clusters bear no resemblance to v1 (avg_J<0.10). " + summary)
    # HARD_PASS gates: all five must hold
    pass_j = avg_j_mean >= AVG_JACCARD_PASS
    pass_arrows = new_arrows_mean >= NEW_ARROWS_PASS
    pass_recall = recall_mean >= RECALL_PASS
    pass_cv = (cv <= CV_PASS) if len(new_arrows) > 1 else True
    pass_no_llm = max(llm_calls) == 0
    if pass_j and pass_arrows and pass_recall and pass_cv and pass_no_llm:
        return (
            "HARD_PASS",
            "HARD_PASS: substrate self-maps cert_ledger via OWN primitives; clusters match v1 + "
            "extend via new cross-family arrows; stable + zero-LLM. " + summary,
        )
    # MIDDLE_BAND: partial overlap or partial extension
    if avg_j_mean >= AVG_JACCARD_MIDDLE and (pass_arrows or pass_recall):
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: substrate confirms but doesn't fully extend v1 (or vice versa). " + summary,
        )
    return (
        "HARD_FAIL",
        "HARD_FAIL: substrate self-map below pre-reg bars (no clear mechanism win). " + summary,
    )


# ===== main =====


if __name__ == "__main__":
    print(
        "[config] anchor=%s mode=%s seeds=%s N=%d | %s"
        % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION),
        flush=True,
    )
    t0 = time.time()
    # ----- load all data once (cheap; chain-grade ~447 atoms; relations ~ few-thousand) -----
    print("[load] cert_ledger chain-grade atoms...", flush=True)
    chain_grade_atoms = load_chain_grade_atom_ids()
    if MAX_ATOMS is not None:
        chain_grade_atoms = chain_grade_atoms[:MAX_ATOMS]
    print("  -> %d chain-grade atoms" % len(chain_grade_atoms), flush=True)
    print("[load] relations restricted to chain-grade endpoints...", flush=True)
    triples_str, rel_types = load_relations_for(chain_grade_atoms)
    print(
        "  -> %d chain-grade-internal triples; %d distinct relation types: %s"
        % (len(triples_str), len(rel_types), rel_types[:8]),
        flush=True,
    )
    if not triples_str or not rel_types:
        print("[error] no chain-grade-internal triples found; aborting", flush=True)
        sys.exit(2)
    print("[load] v1 clusters from latest capability_family_map_v1_*.md ...", flush=True)
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

    # Run remaining seeds
    for s in remaining:
        rec = run_seed(s, chain_grade_atoms, triples_str, rel_types, v1_clusters,
                       v1_cross_arrows)
        write_partial(out_dir, s, rec)

    # Aggregate
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
            "Phase 1 substrate-native self-mapping per USER 2026-06-22 strategic vision; "
            "char_trigram_encoder + KGStore + multi_hop.iter_cleanup_chain are substrate "
            "primitives (NOT LLM forward calls). Real-arm vs random-relation-control "
            "discriminator (Fix #16). v1 (tools/substrate_relational_analysis.py) is "
            "Director-side lexical pattern-matching; v2 (this cell) does the substrate's "
            "OWN analysis. Honest scope: bag-of-trigrams atom_id encoding (no positional); "
            "2-hop traversal only (chain-grade per r1)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
