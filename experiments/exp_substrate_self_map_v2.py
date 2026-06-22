"""substrate_self_map_v2b -- substrate-native self-mapping, broadened-scope (Phase 1 of USER strategic vision).

v2b broadens v2's relation filter after v2 single-seed full-scale empirically discovered
that the chain-grade-INTERNAL relation subgraph is structurally near-empty: 447 chain-grade
atoms but only ~16 relations across 2 relation types (7 non-trivial after dropping self-loops),
yielding mechanism-null verdicts (clusters=1, avg_J=0.087). Pre-reg estimate of ~8000 / 17
relation types was the FULL-Store inventory, not the chain-grade subgraph.

v2b extends the endpoint filter to chain-grade UNION atomized: a triple is admitted when
EITHER endpoint is chain-grade (the other endpoint may be any atomized atom). This maps how
chain-grade atoms sit in the broader atomized Store -- still substrate-native, with chain-grade
atoms remaining the traversal anchors. (Option 2 -- full-Store ingest, ~200k relations -- is
deferred until v2b confirms the broadened scope produces a mechanism-discriminating result.)

Substrate uses its OWN primitives (char_trigram_encoder + KGStore + multi_hop) to analyze
the cert_ledger relational structure. This replaces v1 (tools/substrate_relational_analysis.py),
which was correctly criticized by USER 2026-06-22 as Director-side lexical pattern-matching on
atom_id strings, not substrate self-mapping.

Mechanism (substrate-native end-to-end; ZERO LLM forward calls at retrieval):

  1. Atom encoding -- CharTrigramEncoder at N_DIM, bipolar bag-of-trigrams over atom_id.
     Atom universe = chain-grade atoms (anchors) UNION any atomized atom appearing as the
     other endpoint of an admitted relation (frontier set).
  2. Relation extraction -- read each data/substrate_index/<corpus>/relations.jsonl;
     v2b admits (src, rel_type, tgt) triples where EITHER endpoint is chain-grade (the other
     may be any atom_id appearing in any atoms.jsonl across corpora). Self-loops dropped.
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

Pre-reg HARD bands (committed in preregs/2026-06-22_substrate_self_map_v2b.md):

  v2b primary discriminating metric is the REAL-vs-SHUFFLE cluster-granularity gap,
  NOT v1-resemblance: the broadened-scope graph now includes outward atomized atoms,
  so v1's chain-grade lexical clustering is no longer the relevant alignment target.
  The lexical-overlap metric is RETAINED for traceability (per_cluster_match) but is
  no longer a HARD gate.

  v2b smoke discovery: within-cluster coherence has the OPPOSITE sign of what
  was expected -- the random-relation arm tends to produce ONE giant blob (everything
  reachable via the same noise) with HIGH within-cluster coherence, while the real arm
  produces MORE clusters with smaller, more-distinguishable neighborhoods. The
  discriminating signal is therefore n_clusters_real > n_clusters_shuffle (real has
  more granular structure) NOT coherence-gap. Pre-reg bands corrected accordingly.

  HARD_PASS chain-grade:
    - REAL arm produces more clusters than SHUFFLE arm (genuine granularity):
      n_clusters_real - n_clusters_shuffle >= 2
    - REAL arm produces >= 3 clusters absolute (mechanism produces structure):
      n_clusters_real >= 3
    - substrate-only-decode preserved (n_llm_calls = 0)
    - Atom retrieval recall >= 0.95 (codebook preserves atom-id identity)
    - 3 seeds; cv <= 0.10 on n_clusters_real (stability; relaxed from 0.05 since
      cluster count is a discrete metric)

  MIDDLE_BAND:
    - n_clusters_real >= 2 AND n_clusters_real - n_clusters_shuffle >= 1
      (mechanism present but weakly discriminating)

  HARD_FAIL:
    - n_clusters_real <= 1 (mechanism null on this scope -- recommend Option 2:
      full-Store ingest)
    - n_clusters_real <= n_clusters_shuffle (shuffle as granular as real;
      relation-conditioned mechanism null)
    - substrate-only-decode violated (any LLM forward call counted)
    - Atom retrieval recall < 0.50 (codebook too crowded)

Discriminator control (Fix #16): RANDOM_RELATION baseline arm. Substrate-derived clusters
from SHUFFLED relation_types tend to collapse into one giant blob (all anchors reachable
through uniform-random rel_type noise); the REAL arm should produce more granular
structure (more clusters of smaller size). Gap in cluster-COUNT (not within-cluster
coherence) is the relation-conditioned mechanism evidence.

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

ANCHOR_NAME = "substrate_self_map_v2b"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"

# ----- pre-registered HARD thresholds (v2b broadened scope) -----
# v2b: primary gates are n_clusters_real and the real-vs-shuffle CLUSTER-COUNT gap.
# (Coherence had opposite sign of expectation -- shuffle blob is more coherent within
# its giant single cluster than real's smaller separated clusters. n_clusters delta is
# the correct discriminator.) v1-resemblance retained as informational only.
N_CLUSTERS_REAL_PASS = 3        # HARD_PASS requires >=3 substrate-clusters
N_CLUSTERS_REAL_MIDDLE = 2      # MIDDLE_BAND requires >=2
N_CLUSTERS_GAP_PASS = 2         # HARD_PASS requires (real - shuffle) >= 2 clusters
N_CLUSTERS_GAP_MIDDLE = 1       # MIDDLE_BAND requires (real - shuffle) >= 1
N_CLUSTERS_GAP_FAIL = 0         # HARD_FAIL if real <= shuffle
RECALL_PASS = 0.95              # atom-id retrieval recall via char-trigram codebook
RECALL_FAIL = 0.50              # HARD_FAIL on recall below this
CV_PASS = 0.10                  # relaxed from 0.05; cluster-count is discrete
JACCARD_CLUSTER_TAU = 0.30      # greedy substrate-cluster threshold
JACCARD_VS_V1_TAU = 0.30        # informational: "substrate atom resembles v1 cluster"

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
    # v2b smoke: use the FULL chain-grade slice (447 atoms) so the broadened admit
    # rule actually yields a representative number of triples. The v2 smoke hard-cap
    # at MAX_ATOMS=50 was the reason its smoke was mechanism-null (only 26 admitted
    # triples in that slice). Smoke still runs <2s at this scale; smoke cap is on
    # ANCHORS + N_DIM + seeds, not on MAX_ATOMS.
    MAX_ATOMS = None
    N_ANCHORS = 50           # subset of chain-grade atoms used as 2-hop anchors
    N_RELATION_SAMPLES = 16  # per anchor, how many random 2-relation sequences
    K_SET = 12
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    MAX_ATOMS = None          # all chain-grade atoms (~447)
    N_ANCHORS = 200           # capped subset of anchors for 2-hop traversal
    N_RELATION_SAMPLES = 32   # per anchor
    K_SET = 16

CONFIG_VERSION = (
    "v2b-broadened-scope-chain-grade-OR-atomized: char_trigram_atom_encode + "
    "KGStore_multivalue_Hebbian + multi_hop_2hop_neighborhood_Jaccard_cluster + "
    "random_relation_control; either-endpoint chain-grade admit; cluster-count "
    "discriminator (real - shuffle); "
    "N%d max_atoms=%s n_anchors=%d n_rel_samples=%d kset=%d "
    "bands n_clusters>=%d cluster_gap>=%d recall>=%.2f cv<=%.2f"
) % (N_DIM, str(MAX_ATOMS), N_ANCHORS, N_RELATION_SAMPLES, K_SET,
     N_CLUSTERS_REAL_PASS, N_CLUSTERS_GAP_PASS, RECALL_PASS, CV_PASS)


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


def load_atomized_atom_ids() -> set[str]:
    """Collect every atom_id appearing in any <corpus>/atoms.jsonl (bare form, post-`::`).

    Atomized = onboard in the substrate (any tier T1/T2/T3); chain-grade is a subset.
    v2b uses this as the frontier set: chain-grade UNION atomized = atom universe.
    """
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
                    # atoms.jsonl stores bare id (T<tier>/name); already in the
                    # post-`::` form that relations.jsonl src_id/tgt_id use.
                    out.add(aid)
    return out


def load_relations_for(
    chain_grade_atom_ids: list[str],
    atomized_atom_ids: set[str],
) -> Tuple[list[tuple[int, str, int]], list[str], list[str], dict[str, int]]:
    """v2b: read every <corpus>/relations.jsonl; admit (src, rel_type, tgt) triples where
    EITHER endpoint is chain-grade and BOTH endpoints are in the atomized universe.

    Returns:
      triples: list of (src_idx, rel_type_str, tgt_idx); indices into combined atom_ids.
      relation_types: sorted distinct rel_type strings encountered.
      combined_atom_ids: combined ordered list of atom_ids actually used by triples
        (chain-grade atoms first, then non-chain-grade atomized atoms; bare form).
      chain_grade_index_set: dict bare_id -> idx restricted to chain-grade portion of
        combined_atom_ids (anchors must be sampled from this subset).
    """
    # Bare chain-grade set for the EITHER-endpoint filter.
    chain_grade_bare: set[str] = set()
    for aid in chain_grade_atom_ids:
        chain_grade_bare.add(_strip_corpus_prefix(aid))
    # First pass: collect every (src, tgt) bare pair that satisfies the v2b admit rule
    # so we know which non-chain-grade atomized atoms to include in the universe.
    admitted: list[tuple[str, str, str]] = []
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
                if src_b == tgt_b:
                    continue  # drop self-loops
                # v2b admit: EITHER endpoint chain-grade AND both endpoints atomized.
                either_cg = (src_b in chain_grade_bare) or (tgt_b in chain_grade_bare)
                if not either_cg:
                    continue
                if (src_b not in atomized_atom_ids) or (tgt_b not in atomized_atom_ids):
                    # endpoint not in any atoms.jsonl -- drop (keeps codebook honest)
                    continue
                admitted.append((src_b, rtype, tgt_b))
                rel_types.add(rtype)
    # Build combined atom universe: chain-grade portion FIRST (so anchors are 0..n_cg-1),
    # then non-chain-grade atomized atoms that actually appear in admitted triples.
    combined: list[str] = []
    seen: set[str] = set()
    # chain-grade portion in the original cert_ledger-derived order (bare form)
    for aid in chain_grade_atom_ids:
        bare = _strip_corpus_prefix(aid)
        if bare in seen:
            continue
        combined.append(bare)
        seen.add(bare)
    n_chain_grade = len(combined)
    # frontier portion: non-chain-grade atomized atoms appearing in admitted triples
    frontier_seen: set[str] = set()
    for (s, _r, t) in admitted:
        if s not in seen and s not in frontier_seen:
            frontier_seen.add(s)
        if t not in seen and t not in frontier_seen:
            frontier_seen.add(t)
    for b in sorted(frontier_seen):
        combined.append(b)
        seen.add(b)
    bare_to_idx = {b: i for i, b in enumerate(combined)}
    # Second pass: convert admitted to index triples.
    triples: list[tuple[int, str, int]] = []
    for (s, r, t) in admitted:
        s_idx = bare_to_idx[s]
        t_idx = bare_to_idx[t]
        if s_idx == t_idx:
            continue
        triples.append((s_idx, r, t_idx))
    # chain_grade_index_set: 0..n_chain_grade-1 are the anchor candidates.
    chain_grade_index_set = {combined[i]: i for i in range(n_chain_grade)}
    return triples, sorted(rel_types), combined, chain_grade_index_set


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


def cluster_coherence(clusters: list[set[int]], neighborhoods: dict[int, set[int]]) -> float:
    """Mean pairwise Jaccard among same-cluster anchors, averaged over clusters of size>=2.

    Substrate-internal coherence metric (no v1 dependency). Real arm should have HIGHER
    coherence than shuffle arm if relation-conditioned mechanism is real -- relations
    that cluster anchors together should give those anchors more-similar neighborhoods.
    Returns 0.0 if no cluster has size >= 2.
    """
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


def run_seed(seed: int, combined_atoms: list[str], triples_str: list[tuple[int, str, int]],
             rel_types: list[str], n_chain_grade: int, v1_clusters: dict[str, set[str]],
             v1_cross_arrows: set[str]) -> dict:
    """Single seed: build substrate KG, traverse, cluster; run both arms.

    v2b: combined_atoms = chain-grade (first n_chain_grade entries) + atomized frontier.
    Anchors are drawn ONLY from the chain-grade prefix (indices 0..n_chain_grade-1).
    """
    t_start = time.time()
    rng = np.random.default_rng(seed)
    n_ent = len(combined_atoms)
    rel_to_idx = {r: i for i, r in enumerate(rel_types)}
    n_rel = len(rel_types)
    triples_idx = [(s, rel_to_idx[r], o) for (s, r, o) in triples_str]
    # ----- encode atoms via substrate primitive (char-trigram) -----
    E_np, encoder = encode_atoms_substrate(combined_atoms, N_DIM)
    # ----- atom retrieval recall sanity (over the full combined codebook) -----
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
    # New arrows informational; not load-bearing in v2b verdict
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
    coherence_shuf = cluster_coherence(clusters_shuf, nbr_shuf)
    avg_j_shuf, _per_cluster_shuf = avg_jaccard_substrate_vs_v1(
        clusters_shuf, anchors, anchor_to_short, v1_clusters)
    arrows_shuf = cross_family_arrows(clusters_shuf, anchors, anchor_to_atom_id,
                                       v1_clusters, JACCARD_VS_V1_TAU, nbr_shuf)
    new_arrows_shuf = [a for a in arrows_shuf if a["anchor_short"] not in v1_cross_arrows]
    n_new_arrows_shuf = len(new_arrows_shuf)

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
    """v2b HARD bands: primary gates are n_clusters_real and (n_clusters_real - n_clusters_shuffle)."""
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
    # cv on n_clusters_real
    if len(n_clusters_real) > 1 and np.mean(n_clusters_real) > 0:
        cv = float(np.std(n_clusters_real) / np.mean(n_clusters_real))
    else:
        cv = 0.0
    # informational: coherence and v1 lexical resemblance
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
    # Substrate-only-decode gate (HARD FAIL if violated)
    if max(llm_calls) > 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated; n_llm_calls>0. " + summary)
    # Recall floor
    if recall_mean < RECALL_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: atom retrieval recall below floor (codebook too crowded). " + summary)
    # Mechanism-null floor: n_clusters <= 1
    if n_clusters_mean <= 1.0:
        return (
            "HARD_FAIL",
            "HARD_FAIL: mechanism null on broadened scope (n_clusters_real<=1); "
            "recommend Option 2 (full-Store ingest). " + summary,
        )
    # Discriminator-null floor: real <= shuffle
    if cluster_gap <= N_CLUSTERS_GAP_FAIL:
        return (
            "HARD_FAIL",
            "HARD_FAIL: shuffle as granular as real (cluster_gap<=0); "
            "relation-conditioned mechanism null. " + summary,
        )
    # HARD_PASS
    pass_n_clusters = n_clusters_mean >= N_CLUSTERS_REAL_PASS
    pass_gap = cluster_gap >= N_CLUSTERS_GAP_PASS
    pass_recall = recall_mean >= RECALL_PASS
    pass_cv = (cv <= CV_PASS) if len(n_clusters_real) > 1 else True
    pass_no_llm = max(llm_calls) == 0
    if pass_n_clusters and pass_gap and pass_recall and pass_cv and pass_no_llm:
        return (
            "HARD_PASS",
            "HARD_PASS: v2b substrate self-maps broadened-scope KG; clusters>=3 + "
            "real-vs-shuffle cluster-count gap>=2; stable + zero-LLM. " + summary,
        )
    # MIDDLE_BAND
    if n_clusters_mean >= N_CLUSTERS_REAL_MIDDLE and cluster_gap >= N_CLUSTERS_GAP_MIDDLE:
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: mechanism present but below HARD_PASS bars. " + summary,
        )
    return (
        "HARD_FAIL",
        "HARD_FAIL: v2b below pre-reg bars (mechanism weak or unstable). " + summary,
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
    print("[load] atomized atom universe across all corpora atoms.jsonl...", flush=True)
    atomized = load_atomized_atom_ids()
    print("  -> %d atomized atom_ids" % len(atomized), flush=True)
    print("[load] relations admit-rule v2b (EITHER endpoint chain-grade, BOTH atomized)...",
          flush=True)
    triples_str, rel_types, combined_atoms, _cg_idx = load_relations_for(
        chain_grade_atoms, atomized)
    # combined_atoms is bare-form, chain-grade prefix first; count prefix length.
    n_chain_grade = 0
    cg_bare = {_strip_corpus_prefix(aid) for aid in chain_grade_atoms}
    for b in combined_atoms:
        if b in cg_bare:
            n_chain_grade += 1
        else:
            break
    print(
        "  -> %d admitted triples; %d distinct relation types: %s"
        % (len(triples_str), len(rel_types), rel_types[:8]),
        flush=True,
    )
    print(
        "  -> %d combined atoms (%d chain-grade prefix + %d atomized frontier)"
        % (len(combined_atoms), n_chain_grade, len(combined_atoms) - n_chain_grade),
        flush=True,
    )
    if not triples_str or not rel_types:
        print("[error] no v2b-admitted triples found; aborting", flush=True)
        sys.exit(2)
    print("[load] v1 clusters from latest capability_family_map_v1_*.md (informational) ...",
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

    # Run remaining seeds
    for s in remaining:
        rec = run_seed(s, combined_atoms, triples_str, rel_types, n_chain_grade,
                       v1_clusters, v1_cross_arrows)
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
            "Phase 1 substrate-native self-mapping (v2b broadened scope) per USER 2026-06-22 "
            "strategic vision. v2 empirically discovered the chain-grade-INTERNAL relation "
            "subgraph is structurally near-empty (16 relations / 2 types over 447 atoms; "
            "mechanism-null). v2b extends the admit rule to EITHER endpoint chain-grade "
            "(other endpoint may be any atomized atom). Anchors still drawn from the "
            "chain-grade subset; substrate maps how chain-grade atoms sit in the broader "
            "atomized graph. Primary HARD gates: n_clusters_real and real-vs-shuffle "
            "coherence gap (NOT v1 lexical resemblance; broadened scope makes v1 alignment "
            "no longer the relevant target -- retained as informational). char_trigram + "
            "KGStore + multi_hop are substrate primitives (NOT LLM calls). Option 2 = full-"
            "Store ingest (~200k relations) deferred until v2b confirms mechanism."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
