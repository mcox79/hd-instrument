"""self_map_v2f_pretrained_encoder_smoke_v1 -- Gap-2 V3 gate retry with PRETRAINED encoder.

v2e diagnosis (Skunkworks landed-VET): modularity-Z self-mapping HARD_FAIL was encoder-bound,
not discriminator-bound. The 5x drill concluded "encoder must move from name-bigram to
dependency-graph-context embedding." We now have validated semantic encoders cached at
data/gensim_cache/ (word2vec-google-news-300, Spearman ~0.6 vs human similarity).

This cell swaps the encoder family across 4 arms while holding the v2e discriminator family
(modularity-Z + Louvain at gamma sweep, vs degree-preserving null) fixed:

  ARM_CHAR_TRIGRAM_NAME_LEAK  -- substrate-native: char_trigram on FULL atom_id (this is
                                  what v2e tested; benefits from name lexical leak)
  ARM_CHAR_TRIGRAM_STRIPPED   -- char_trigram on atom_id with mechanism keyword replaced
                                  by random hash (honest lexical baseline, no name-leak)
  ARM_WORD2VEC_KEYWORDS       -- extract semantic keywords from atom_id; encode each via
                                  cached word2vec-google-news-300; bundle into atom vector
  ARM_HYBRID                   -- bundle(word2vec keywords, char_trigram stripped) --
                                  composition of semantic + lexical signal

Discriminator (same as v2e): modularity Z-score against degree-preserving null at
gamma sweep [0.5, 1.0, 2.0, 4.0]. Same KGStore Hebbian W path. Same multi_hop K=2
2-hop Jaccard adjacency. Only the atom encoding changes per arm.

PRE-REG HARD bands (per Director task spec 2026-06-22):
  HARD_PASS: ARM_WORD2VEC_KEYWORDS mod_Z >= 3.0 at any gamma AND
             mod_Z(WORD2VEC) / mod_Z(STRIPPED) >= 2.0 (semantic beats stripped-lexical by 2x)
             AND mod_Z(WORD2VEC) > mod_Z(NAME_LEAK) (semantic also beats name-leak)
  HARD_FAIL: all semantic arms mod_Z < 1.5 at every gamma OR no arm beats stripped by 1.5x
  MIDDLE_BAND: partial improvement.

Sanity self-test (--self-test): on a planted 3-block partition of synthetic atom_ids
(ground-truth communities; differing keyword set per block), ARM_WORD2VEC_KEYWORDS
mod_Z >> ARM_CHAR_TRIGRAM_STRIPPED. Endpoint check; sys.exit(0) on pass.

ASCII-only. Per-seed checkpoint. Substrate-only-decode (zero LLM forward calls).
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

# Direct gensim cache (mirrors exp_encoder_word2vec_substrate_bind_v1.py)
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ["GENSIM_DATA_DIR"] = GENSIM_CACHE_DIR

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

# v2c primitives parse argv at import; strip our own argv to avoid sys.exit(0).
_saved_argv = sys.argv[:]
sys.argv = [sys.argv[0]]
from experiments.exp_substrate_self_map_v2c_full_store_v1 import (
    load_chain_grade_atom_ids, load_atomized_atom_ids, load_relations_for,
    build_kg, two_hop_neighborhood, jaccard,
    atom_id_short, atom_retrieval_recall, sample_relation_pairs,
)
from experiments.exp_v2e_modularity_Z_LRG_self_mapping_v1 import (
    build_jaccard_adjacency, threshold_adjacency,
    louvain_partition, modularity_Q, degree_preserving_rewire, modularity_Z_score,
)
sys.argv = _saved_argv

_LLM_CALL_COUNTER = [0]

ANCHOR_NAME = "self_map_v2f_pretrained_encoder_smoke_v1"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

# ----- pre-registered HARD thresholds -----
MOD_Z_PASS = 3.0
MOD_Z_RATIO_PASS = 2.0
MOD_Z_FAIL = 1.5
MOD_Z_RATIO_FAIL = 1.5
RECALL_PASS = 0.95
RECALL_FAIL = 0.50

# ----- arms -----
ARM_NAME_LEAK = "ARM_CHAR_TRIGRAM_NAME_LEAK"
ARM_STRIPPED = "ARM_CHAR_TRIGRAM_STRIPPED"
ARM_W2V = "ARM_WORD2VEC_KEYWORDS"
ARM_HYBRID = "ARM_HYBRID"
ARMS = [ARM_NAME_LEAK, ARM_STRIPPED, ARM_W2V, ARM_HYBRID]
SEMANTIC_ARMS = [ARM_W2V, ARM_HYBRID]

# ----- mechanism keywords to strip (regex; case-insensitive) -----
# Heuristic: keywords that name a substrate mechanism family; replacing these with a
# stable hash kills the name-leak while preserving structure (_v1_n4096 etc).
MECHANISM_KEYWORDS = [
    "cleanup", "storage", "generation", "refuse", "multi_hop", "kg", "kg_traversal",
    "modularity", "lrg", "self_map", "self_mapping", "encoder", "word2vec", "glove",
    "fasttext", "bge", "hopfield", "modern_hopfield", "minilm", "trigram", "char_trigram",
    "whitening", "vq", "kwta", "sparse", "deletion", "negative_knowledge", "embedding",
    "ingest", "sequence", "binding", "compose", "composition", "cross_layer", "kv",
    "hebbian", "iterate", "iterative", "attractor", "discrim", "discriminator",
    "ner", "transition", "noise", "cert", "phase", "transform", "transit",
    "n_sweep", "scan", "sweep", "battery", "boundary", "phase_portrait",
    "router", "paraphrase", "robustness", "marianmt", "multidoc", "synthesis",
    "deletion_cert", "intent", "classifier", "knowledge", "memory", "store",
    "subgraph", "graph", "router", "head", "tail", "norm", "regression",
    "regulation", "sigma", "ablation", "merkle", "audit", "timing", "immunity",
    "gate", "ratio", "control", "split", "join", "pairwise", "consensus",
    "configuration", "stress", "stability", "diffusion", "smoothing", "smoothed",
    "softmax", "logit", "policy", "value", "actor", "critic", "drill", "scout",
]
_MECH_RE = re.compile(
    r"\b(" + "|".join(sorted(MECHANISM_KEYWORDS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# Config (this anchor is smoke-class only per Director task; production at v3 if PASS).
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 4096
    MAX_INGEST_TRIPLES = 5000
    N_ANCHORS = 100             # production-ish; per Director spec
    N_RELATION_SAMPLES = 10
    K_SET = 12
    N_NULL_REWIRES = 30         # smoke margin
    JACCARD_TAU = 0.05
else:
    # NOTE: this anchor is _smoke_v1; full-class anchor would have different name.
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    MAX_INGEST_TRIPLES = None
    N_ANCHORS = 150
    N_RELATION_SAMPLES = 20
    K_SET = 16
    N_NULL_REWIRES = 100
    JACCARD_TAU = 0.10

GAMMA_SWEEP = [0.5, 1.0, 2.0, 4.0]
PRETRAIN_DIM = 300
W2V_MODEL_NAME = "word2vec-google-news-300"

CONFIG_VERSION = (
    "v2f-pretrained-encoder: 4 arms (char_trigram_name_leak / char_trigram_stripped / "
    "word2vec_keywords / hybrid) X same v2e modularity-Z (Louvain @ gamma sweep) vs "
    "degree-preserving null; KGStore + multi_hop 2-hop Jaccard adjacency; N%d "
    "n_anchors=%d n_rel_samples=%d kset=%d n_null=%d jac_tau=%.2f gammas=%s "
    "arms=%s bands mod_Z>=%.1f w2v/stripped>=%.1f recall>=%.2f"
) % (N_DIM, N_ANCHORS, N_RELATION_SAMPLES, K_SET, N_NULL_REWIRES, JACCARD_TAU,
     GAMMA_SWEEP, ARMS, MOD_Z_PASS, MOD_Z_RATIO_PASS, RECALL_PASS)


# ============================================================================
# atom_id parsing + keyword extraction
# ============================================================================

def _strip_mechanism(atom_id: str, seed: int) -> str:
    """Replace each MECHANISM_KEYWORDS occurrence with a stable hash token.

    Preserves the lexical structure of the atom_id (positions of _v / _n / etc.)
    but zeroes out the keyword that would otherwise leak community membership.
    Hash is deterministic per (atom_id, seed) so identical atoms across calls
    get the same stripped form (reproducibility).
    """
    h = hashlib.md5((atom_id + ":" + str(seed)).encode("utf-8")).hexdigest()[:6]
    def _sub(m):
        return h
    return _MECH_RE.sub(_sub, atom_id)


def _extract_keywords(atom_id: str) -> list[str]:
    """Extract semantic keyword tokens from an atom_id for word2vec lookup.

    Strategy: take the post-`/` last segment, split on underscore, drop short
    tokens (<=2 chars), drop version markers (v\\d+, n\\d+), drop pure-numeric.
    Returns lowercased tokens; order preserved.
    """
    short = atom_id.split("/")[-1]
    # Drop EXP_ prefix if present
    if short.startswith("EXP_"):
        short = short[4:]
    tokens = short.split("_")
    out = []
    for t in tokens:
        tl = t.lower()
        if len(tl) <= 2:
            continue
        if re.fullmatch(r"v\d+", tl) or re.fullmatch(r"n\d+", tl):
            continue
        if tl.isdigit():
            continue
        # split intra-token camel/digit boundaries cheaply
        out.append(tl)
    return out


# ============================================================================
# Encoders (per ARM)
# ============================================================================

def encode_arm_char_trigram_name_leak(atom_ids: list[str], n_dim: int, seed: int):
    """ARM 1: substrate-native baseline; char-trigram on full atom_id."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    E = enc.encode_batch(atom_ids).astype(np.float32)
    return E, enc


def encode_arm_char_trigram_stripped(atom_ids: list[str], n_dim: int, seed: int):
    """ARM 2: char-trigram on stripped atom_id (mechanism keyword -> hash)."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    stripped = [_strip_mechanism(a, seed) for a in atom_ids]
    E = enc.encode_batch(stripped).astype(np.float32)
    return E, enc


_W2V_KV = [None]   # in-process cache (avoid reloading 1.5GB)


def _load_w2v():
    if _W2V_KV[0] is None:
        import gensim.downloader as gd
        try:
            gd.base_dir = GENSIM_CACHE_DIR
            gd.BASE_DIR = GENSIM_CACHE_DIR
        except Exception:
            pass
        _W2V_KV[0] = gd.load(W2V_MODEL_NAME)
    return _W2V_KV[0]


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    """Random Gaussian projection PRE_DIM x N_DIM; deterministic per seed."""
    rng = np.random.default_rng(seed + 9001)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32)
    P /= np.sqrt(in_dim)
    return P


def _l2_normalize(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    return X / n


def encode_arm_word2vec_keywords(atom_ids: list[str], n_dim: int, seed: int):
    """ARM 3: keyword extraction + word2vec lookup + bundle (mean) + project."""
    kv = _load_w2v()
    P = _gaussian_projection(in_dim=PRETRAIN_DIM, out_dim=n_dim, seed=seed)
    # First pass: assemble 300d pre-projection codebook
    pre = np.zeros((len(atom_ids), PRETRAIN_DIM), dtype=np.float32)
    n_hit_atoms = 0
    n_oov_atoms = 0
    total_kw_hits = 0
    total_kw_misses = 0
    for i, aid in enumerate(atom_ids):
        kws = _extract_keywords(aid)
        if not kws:
            n_oov_atoms += 1
            continue
        vecs = []
        for kw in kws:
            if kw in kv.key_to_index:
                vecs.append(kv[kw])
                total_kw_hits += 1
            elif kw.lower() in kv.key_to_index:
                vecs.append(kv[kw.lower()])
                total_kw_hits += 1
            else:
                total_kw_misses += 1
        if not vecs:
            n_oov_atoms += 1
            continue
        v = np.mean(np.stack(vecs, 0), axis=0).astype(np.float32)
        pre[i] = v
        n_hit_atoms += 1
    # L2-normalize 300d then project to n_dim
    pre_n = _l2_normalize(pre)
    E = (pre_n @ P.T).astype(np.float32)
    print("  [w2v-keyword-stats] hit_atoms=%d oov_atoms=%d kw_hits=%d kw_misses=%d"
          % (n_hit_atoms, n_oov_atoms, total_kw_hits, total_kw_misses), flush=True)
    return E, None


def encode_arm_hybrid(atom_ids: list[str], n_dim: int, seed: int):
    """ARM 4: bundle(word2vec_keywords, char_trigram_stripped). Both L2-normed then summed."""
    E_w2v, _ = encode_arm_word2vec_keywords(atom_ids, n_dim, seed)
    E_str, _ = encode_arm_char_trigram_stripped(atom_ids, n_dim, seed)
    E_w2v_n = _l2_normalize(E_w2v)
    E_str_n = _l2_normalize(E_str)
    # bundle by sum + renormalize (HD-style)
    E_bundle = E_w2v_n + E_str_n
    E_bundle = _l2_normalize(E_bundle).astype(np.float32)
    return E_bundle, None


def encode_arm(arm: str, atom_ids: list[str], n_dim: int, seed: int):
    if arm == ARM_NAME_LEAK:
        return encode_arm_char_trigram_name_leak(atom_ids, n_dim, seed)
    if arm == ARM_STRIPPED:
        return encode_arm_char_trigram_stripped(atom_ids, n_dim, seed)
    if arm == ARM_W2V:
        return encode_arm_word2vec_keywords(atom_ids, n_dim, seed)
    if arm == ARM_HYBRID:
        return encode_arm_hybrid(atom_ids, n_dim, seed)
    raise ValueError(f"unknown arm: {arm}")


# ============================================================================
# Sanity self-test: planted 3-block partition with distinct keyword sets
# ============================================================================

def _selftest():
    """Endpoint: planted 3-block community via DISTINCT keyword sets per block.

    Block A: anchors with keywords {dog, cat, animal, pet, bird}
    Block B: anchors with keywords {car, vehicle, truck, road, drive}
    Block C: anchors with keywords {music, song, guitar, sound, melody}

    ARM_WORD2VEC_KEYWORDS should produce vectors that cluster intra-block (semantic
    coherence); ARM_CHAR_TRIGRAM_STRIPPED has no semantic signal so should not
    cluster. We check mod_Z(W2V) > mod_Z(STRIPPED) on the resulting adjacency.
    """
    print("[selftest] building planted 3-block atom_ids...", flush=True)
    np.random.seed(42)
    # Build synthetic atom_ids; each block has 15 atoms; each atom has 3-5 keywords
    block_kws = {
        "A": ["dog", "cat", "animal", "pet", "bird", "fish", "wildlife", "puppy"],
        "B": ["car", "vehicle", "truck", "road", "drive", "engine", "motor", "wheel"],
        "C": ["music", "song", "guitar", "sound", "melody", "piano", "drum", "rhythm"],
    }
    rng = np.random.default_rng(42)
    atoms_test = []
    truth = []
    for bi, (blk, kws) in enumerate(block_kws.items()):
        for j in range(15):
            n_kw = int(rng.integers(3, 6))
            picked = rng.choice(kws, size=n_kw, replace=False).tolist()
            aid = "math::T3/EXP_" + "_".join(picked) + "_v1_n4096"
            atoms_test.append(aid)
            truth.append(bi)
    print("[selftest] %d atoms across 3 blocks; encoding via stripped + w2v..."
          % len(atoms_test), flush=True)

    # Quick test: ensure key extraction works
    sample_kws = _extract_keywords(atoms_test[0])
    print("[selftest] sample atom_id=%s -> keywords=%s"
          % (atoms_test[0], sample_kws), flush=True)
    assert len(sample_kws) >= 2, "keyword extraction returned <2 keywords"

    # Encode each arm; build small KG-less synthetic adjacency from atom-vec cosine
    # (we don't need full KG; verify the ENCODER produces block-structured similarity)
    E_stripped, _ = encode_arm_char_trigram_stripped(atoms_test, n_dim=1024, seed=7)
    E_w2v, _ = encode_arm_word2vec_keywords(atoms_test, n_dim=1024, seed=7)
    # cosine sim -> threshold -> adjacency
    def _cosine_adj(E, thr):
        En = _l2_normalize(E)
        S = (En @ En.T).astype(np.float32)
        np.fill_diagonal(S, 0.0)
        S[S < thr] = 0.0
        return S
    A_str = _cosine_adj(E_stripped, thr=0.2)
    A_w2v = _cosine_adj(E_w2v, thr=0.2)
    z_str = modularity_Z_score(A_str, gamma=1.0, n_rewires=20,
                                rng=np.random.default_rng(7), base_seed=7)
    z_w2v = modularity_Z_score(A_w2v, gamma=1.0, n_rewires=20,
                                rng=np.random.default_rng(7), base_seed=7)
    print("[selftest] planted 3-block: Z_STRIPPED=%.2f Z_W2V=%.2f n_clusters_str=%d n_clusters_w2v=%d"
          % (z_str["Z"], z_w2v["Z"], z_str["n_clusters"], z_w2v["n_clusters"]), flush=True)
    assert z_w2v["Z"] > z_str["Z"], (
        "planted 3-block selftest FAIL: Z_W2V=%.2f not greater than Z_STRIPPED=%.2f"
        % (z_w2v["Z"], z_str["Z"])
    )
    assert z_w2v["Z"] >= 1.5, "planted 3-block selftest FAIL: Z_W2V=%.2f < 1.5" % z_w2v["Z"]
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print("[selftest] PASS: w2v encoder discriminates planted 3-block; n_llm_calls=0",
          flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int, combined_atoms: list[str], triples_str: list[tuple[int, str, int]],
             rel_types: list[str], n_chain_grade: int) -> dict:
    t_start = time.time()
    rng = np.random.default_rng(seed)
    n_ent = len(combined_atoms)
    rel_to_idx = {r: i for i, r in enumerate(rel_types)}
    n_rel = len(rel_types)
    triples_idx = [(s, rel_to_idx[r], o) for (s, r, o) in triples_str]

    # anchors from chain-grade prefix
    if n_chain_grade <= N_ANCHORS:
        anchors = list(range(n_chain_grade))
    else:
        anchors = sorted(rng.choice(n_chain_grade, N_ANCHORS, replace=False).tolist())
    print("  [seed=%d] %d anchors chosen from %d chain-grade prefix"
          % (seed, len(anchors), n_chain_grade), flush=True)

    pairs = sample_relation_pairs(n_rel, N_RELATION_SAMPLES,
                                    np.random.default_rng(seed + 2))

    arm_results = {}

    for arm in ARMS:
        t_arm0 = time.time()
        print("  [seed=%d arm=%s] encoding %d atoms at N=%d..."
              % (seed, arm, n_ent, N_DIM), flush=True)
        t_enc0 = time.time()
        E_np, encoder = encode_arm(arm, combined_atoms, N_DIM, seed)
        t_enc = round(time.time() - t_enc0, 1)
        print("    [seed=%d arm=%s] encoded in %.1fs" % (seed, arm, t_enc), flush=True)

        # atom retrieval recall (only meaningful when encoder is invertible; for w2v
        # without an explicit codebook the recall is over its own E; skip for non-trigram).
        if encoder is not None:
            n_probe = min(n_ent, 100)
            recall = atom_retrieval_recall(E_np, combined_atoms, encoder, n_probe,
                                            np.random.default_rng(seed + 1))
        else:
            # Self-recall via L2-normalized cosine argmax: each row should match itself.
            En = _l2_normalize(E_np)
            n_probe = min(n_ent, 100)
            probe_idx = np.random.default_rng(seed + 1).choice(n_ent, n_probe, replace=False)
            S = En[probe_idx] @ En.T
            pred = np.argmax(S, axis=1)
            recall = float(np.mean(pred == probe_idx))

        # Build KG with THIS arm's E
        t_kg0 = time.time()
        kg = build_kg(E_np, triples_idx, n_ent, n_rel, N_DIM, seed)
        t_kg = round(time.time() - t_kg0, 1)

        # 2-hop neighborhoods for anchors
        t_nbr0 = time.time()
        nbr: dict[int, set[int]] = {}
        for a in anchors:
            nbr[a] = two_hop_neighborhood(kg, a, pairs, K_SET)
        t_nbr = round(time.time() - t_nbr0, 1)

        # Build adjacency from Jaccard
        A_raw = build_jaccard_adjacency(anchors, nbr)
        A_thr = threshold_adjacency(A_raw, JACCARD_TAU)
        n_edges = int((A_thr > 0).sum() // 2)

        # Modularity-Z sweep
        t_modz0 = time.time()
        sweep = []
        for gamma in GAMMA_SWEEP:
            z = modularity_Z_score(A_thr, gamma, N_NULL_REWIRES,
                                    np.random.default_rng(seed + 10 + int(gamma * 10)),
                                    base_seed=seed)
            z_summary = {k: v for k, v in z.items() if k != "labels"}
            sweep.append(z_summary)
            print("    [seed=%d arm=%s gamma=%.1f] Z=%.2f K=%d"
                  % (seed, arm, gamma, z["Z"], z["n_clusters"]), flush=True)
        t_modz = round(time.time() - t_modz0, 1)
        best = max(sweep, key=lambda r: r["Z"])

        arm_results[arm] = {
            "best_gamma": best["gamma"],
            "best_Z": best["Z"],
            "modularity_Z_sweep": sweep,
            "n_edges": n_edges,
            "atom_retrieval_recall": round(recall, 4),
            "t_encoding_s": t_enc,
            "t_kg_build_s": t_kg,
            "t_neighborhoods_s": t_nbr,
            "t_modularity_Z_s": t_modz,
            "t_arm_total_s": round(time.time() - t_arm0, 1),
        }
        # release KG memory before next arm
        del kg, E_np
        print("    [seed=%d arm=%s] DONE in %.1fs | best gamma=%.1f Z=%.2f recall=%.3f edges=%d"
              % (seed, arm, time.time() - t_arm0, best["gamma"], best["Z"], recall, n_edges),
              flush=True)

    elapsed = round(time.time() - t_start, 1)

    # Compute cross-arm ratios for verdict
    Z_namelk = arm_results[ARM_NAME_LEAK]["best_Z"]
    Z_stripped = arm_results[ARM_STRIPPED]["best_Z"]
    Z_w2v = arm_results[ARM_W2V]["best_Z"]
    Z_hyb = arm_results[ARM_HYBRID]["best_Z"]

    print("  [seed=%d] DONE all 4 arms in %.1fs | Z: name_leak=%.2f stripped=%.2f w2v=%.2f hybrid=%.2f"
          % (seed, elapsed, Z_namelk, Z_stripped, Z_w2v, Z_hyb), flush=True)

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
        "elapsed_s": elapsed,
        "arms": arm_results,
        "Z_name_leak": Z_namelk,
        "Z_stripped": Z_stripped,
        "Z_w2v": Z_w2v,
        "Z_hybrid": Z_hyb,
        "Z_w2v_over_stripped": round(Z_w2v / max(Z_stripped, 1e-3), 3),
        "Z_hybrid_over_stripped": round(Z_hyb / max(Z_stripped, 1e-3), 3),
        "Z_w2v_over_name_leak": round(Z_w2v / max(Z_namelk, 1e-3), 3),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


# ============================================================================
# Verdict
# ============================================================================

def verdict(per_seed_records: list[dict]) -> Tuple[str, str]:
    if not per_seed_records:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed records")
    Z_w2v = [p["Z_w2v"] for p in per_seed_records]
    Z_stripped = [p["Z_stripped"] for p in per_seed_records]
    Z_namelk = [p["Z_name_leak"] for p in per_seed_records]
    Z_hyb = [p["Z_hybrid"] for p in per_seed_records]
    ratio_w2v_str = [p["Z_w2v_over_stripped"] for p in per_seed_records]
    ratio_w2v_nlk = [p["Z_w2v_over_name_leak"] for p in per_seed_records]
    recalls = []
    for p in per_seed_records:
        for arm_data in p["arms"].values():
            recalls.append(arm_data["atom_retrieval_recall"])
    llm_calls = [p.get("n_llm_calls", 0) for p in per_seed_records]
    recall_min = float(np.min(recalls)) if recalls else 0.0

    mean_Z_w2v = float(np.mean(Z_w2v))
    mean_Z_stripped = float(np.mean(Z_stripped))
    mean_Z_namelk = float(np.mean(Z_namelk))
    mean_Z_hyb = float(np.mean(Z_hyb))
    mean_ratio_str = float(np.mean(ratio_w2v_str))
    mean_ratio_nlk = float(np.mean(ratio_w2v_nlk))

    summary = (
        "Z(name_leak)=%.2f Z(stripped)=%.2f Z(w2v)=%.2f Z(hybrid)=%.2f | "
        "Z_w2v/Z_stripped=%.2f (pass>=%.1f) Z_w2v/Z_name_leak=%.2f | "
        "recall_min=%.3f (fail<=%.2f) | n_llm=%d"
    ) % (mean_Z_namelk, mean_Z_stripped, mean_Z_w2v, mean_Z_hyb,
         mean_ratio_str, MOD_Z_RATIO_PASS, mean_ratio_nlk,
         recall_min, RECALL_FAIL, max(llm_calls))

    if max(llm_calls) > 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated; n_llm_calls>0. "
                + summary)
    if recall_min < RECALL_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: arm atom retrieval recall below floor. " + summary)

    # HARD_PASS: ARM_W2V mod_Z >= 3 at any seed best gamma AND ratio_w2v/stripped >= 2 AND
    # Z_w2v > Z_name_leak (semantic also beats name-leak baseline).
    pass_w2v_modZ = max(Z_w2v) >= MOD_Z_PASS
    pass_ratio_str = mean_ratio_str >= MOD_Z_RATIO_PASS
    pass_beats_nlk = mean_Z_w2v > mean_Z_namelk
    if pass_w2v_modZ and pass_ratio_str and pass_beats_nlk:
        return ("HARD_PASS",
                "HARD_PASS: semantic encoder breaks substrate self-mapping; "
                "Z(w2v) >= %.1f at some gamma + 2x stripped-lexical baseline + "
                "beats name-leak baseline. " % MOD_Z_PASS + summary)

    # HARD_FAIL: all semantic arms Z < 1.5 OR no arm beats stripped by 1.5x
    all_semantic_below = max(Z_w2v) < MOD_Z_FAIL and max(Z_hyb) < MOD_Z_FAIL
    no_arm_beats_stripped = max(mean_ratio_str,
                                 mean_Z_hyb / max(mean_Z_stripped, 1e-3)) < MOD_Z_RATIO_FAIL
    if all_semantic_below or no_arm_beats_stripped:
        return ("HARD_FAIL",
                "HARD_FAIL: self-mapping null even with semantic encoder; "
                "substrate self-mapping fundamentally hard regardless of encoder. "
                + summary)

    # MIDDLE: partial improvement
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: partial encoder improvement; some lift over stripped baseline "
            "but not the 2x + 3.0 thresholds. " + summary)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    t0 = time.time()
    print("[load] cert_ledger chain-grade atoms...", flush=True)
    chain_grade_atoms = load_chain_grade_atom_ids()
    print("  -> %d chain-grade atoms" % len(chain_grade_atoms), flush=True)
    print("[load] atomized atom universe across all corpora atoms.jsonl...", flush=True)
    atomized = load_atomized_atom_ids()
    print("  -> %d atomized atom_ids" % len(atomized), flush=True)
    print("[load] FULL-Store relations admit...", flush=True)
    load_rng = np.random.default_rng(0)
    triples_str, rel_types, combined_atoms, n_chain_grade = load_relations_for(
        chain_grade_atoms, atomized, MAX_INGEST_TRIPLES, load_rng)
    print("  -> %d admitted triples; %d distinct relation types"
          % (len(triples_str), len(rel_types)), flush=True)
    print("  -> %d combined atoms (%d chain-grade prefix + %d frontier)"
          % (len(combined_atoms), n_chain_grade, len(combined_atoms) - n_chain_grade),
          flush=True)
    if not triples_str or not rel_types:
        print("[error] no admitted triples; aborting", flush=True)
        sys.exit(2)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s"
          % (len(done), len(SEEDS), remaining), flush=True)

    for s in remaining:
        rec = run_seed(s, combined_atoms, triples_str, rel_types, n_chain_grade)
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
            "v2f retry of substrate self-mapping with PRETRAINED encoder (word2vec) "
            "vs char_trigram (with and without mechanism-keyword name-leak). Per "
            "Skunkworks v2e diagnosis: encoder was the bottleneck, not the discriminator. "
            "4 arms hold v2e modularity-Z + Louvain + degree-preserving null fixed; "
            "swap only the atom encoding. HARD_PASS = w2v breaks self-mapping; "
            "HARD_FAIL = even semantic encoder cannot rescue; substrate self-mapping "
            "fundamentally hard regardless of encoder."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
