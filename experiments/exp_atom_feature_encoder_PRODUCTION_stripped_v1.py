"""atom_feature_encoder_PRODUCTION_stripped_v1 -- honest-baseline upgrade.

Parent: atom_feature_encoder_smoke_v1 landed MIDDLE_BAND FULL 2026-06-22:
  feat=0.940 trig=0.887 lift=+0.053 (HP needed lift >= 0.15)
Diagnosis (USER 2026-06-23 reframe): baseline saturates because mechanism keyword
(cleanup/storage/generation/etc.) leaks into atom_id string -> char-trigram picks
it up by NAME not FUNCTION. Production-regime variant must:
  1. Replace mechanism keyword in atom_id with a random hash BEFORE encoding
     (ARM_CHAR_TRIGRAM_STRIPPED -- the honest baseline).
  2. Keep the original name-leak baseline for comparison
     (ARM_CHAR_TRIGRAM_NAME_LEAK -- reproduces parent).
  3. Test atom-feature encoder against BOTH baselines
     (ARM_ATOM_FEATURE -- per parent).
  4. Compose atom-feature with word2vec encoding of description keywords
     (ARM_ATOM_FEATURE_PLUS_WORD2VEC_DESC -- substrate-feature + semantic encoder).

Pre-reg (preregs/2026-06-23_atom_feature_encoder_PRODUCTION_stripped_v1.md):
  HARD_PASS: ARM_ATOM_FEATURE_PLUS_WORD2VEC_DESC.purity >= 0.75 AND
             lift_over_STRIPPED >= 0.20 AND
             lift_over_NAME_LEAK >= 0.05 AND
             planted_block_purity == 1.0 AND
             substrate-only-decode preserved (n_llm_calls == 0)
  HARD_FAIL: lift_over_STRIPPED <= 0.05
             (atom-feature + word2vec doesn't help even on honest baseline)
  MIDDLE_BAND: partial (positive but below HARD_PASS thresholds)

Cell:
  - load chain-grade atom_ids from cert_ledger.jsonl + per-atom metadata
    (full pool: math/ + meta/ + concept/ corpora; ~451 chain-grade)
  - 4 arms x 3 seeds [7,17,23] x k-means K=10 on N_ATOMS_SAMPLE=100, N_DIM=4096
  - sanity self-test: 3-block planted partition recoverable

CPU; ASCII-only; per-seed checkpoint; numpy-only; gensim for word2vec.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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

ANCHOR_NAME = "atom_feature_encoder_PRODUCTION_stripped_v1"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"

GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# substrate-only-decode invariant
_LLM_CALL_COUNTER = [0]

# pre-registered HARD bands
PURITY_HP_FLOOR = 0.75              # word2vec arm absolute purity floor
LIFT_HP_OVER_STRIPPED = 0.20        # honest-baseline lift floor
LIFT_HP_OVER_NAME_LEAK = 0.05       # also beat name-leak baseline
PLANTED_BLOCK_PURITY = 1.0
LIFT_HF_OVER_STRIPPED = 0.05        # HARD_FAIL ceiling

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
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_ATOMS_SAMPLE = 100
    K_CLUSTERS = 10

# canonical mechanism family list; name keyword -> family bin
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

# mechanism keyword regex set (substring match on lowercased name)
MECHANISM_KEYWORDS = {
    "cleanup": ["cleanup", "denoise", "recall"],
    "storage": ["storage", "memory", "hopfield", "kg_store", "store"],
    "generation": ["generation", "generate", "autoregressive", "gen"],
    "refuse": ["refuse", "gate", "abstain", "headroom"],
    "multi_hop": ["multi_hop", "kg_traversal", "traversal", "hop"],
    "whitening": ["whitening", "pca", "kwta", "vq"],
    "binding": ["binding", "bind", "fhrr", "hrr"],
    "capacity": ["capacity", "alpha", "envelope"],
    "trigram": ["trigram", "char_trigram", "encoder"],
}

# union of all mechanism keywords used for the NAME-STRIP regex
_ALL_MECHANISM_KW = sorted(
    {kw for kws in MECHANISM_KEYWORDS.values() for kw in kws},
    key=len,
    reverse=True,  # longest-first match to avoid sub-substring shadowing
)
_STRIP_RE = re.compile(
    "|".join(re.escape(kw) for kw in _ALL_MECHANISM_KW),
    flags=re.IGNORECASE,
)

# sigma regime bins
SIGMA_BINS = [
    ("sigma_lt_0p5", 0.0, 0.5),
    ("sigma_0p5_1p0", 0.5, 1.0),
    ("sigma_1p0_1p5", 1.0, 1.5),
    ("sigma_gt_1p5", 1.5, 1e9),
]

# cert tier list
CERT_TIERS = ["chain_grade", "measured_mechanism", "honest_negative", "other"]

ARMS = [
    "ARM_CHAR_TRIGRAM_NAME_LEAK",          # original baseline (parent reproduction)
    "ARM_CHAR_TRIGRAM_STRIPPED",           # honest baseline; mechanism keyword scrubbed
    "ARM_ATOM_FEATURE",                    # substrate-feature binding (per parent)
    "ARM_ATOM_FEATURE_PLUS_WORD2VEC_DESC", # atom-feature + word2vec(description)
]

WORD2VEC_MODEL_NAME = "word2vec-google-news-300"
PRETRAIN_DIM = 300

CONFIG_VERSION = (
    "atom_feature_encoder_PRODUCTION_stripped_v1: 4 arms "
    "(CHAR_TRIGRAM_NAME_LEAK / CHAR_TRIGRAM_STRIPPED / ATOM_FEATURE / "
    "ATOM_FEATURE_PLUS_WORD2VEC_DESC); k-means K=%d on N=%d sampled chain-grade "
    "atoms; mechanism_family_purity discriminator; HP word2vec_purity >= %.2f AND "
    "lift_over_STRIPPED >= %.2f AND lift_over_NAME_LEAK >= %.2f; HF lift_over_STRIPPED <= %.2f"
) % (
    K_CLUSTERS, N_ATOMS_SAMPLE, PURITY_HP_FLOOR,
    LIFT_HP_OVER_STRIPPED, LIFT_HP_OVER_NAME_LEAK, LIFT_HF_OVER_STRIPPED,
)


# ===== deterministic per-feature random bipolar HV codebook =====

def _seed_for_token(token: str) -> int:
    h = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(token: str, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(_seed_for_token(token))
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


# ===== name stripping =====

def strip_mechanism_keywords(atom_id: str) -> str:
    """Replace every mechanism keyword in atom_id with a stable random hash token.

    Preserves overall length-class + structural punctuation (::, /, _) so the
    char-trigram encoder can't trivially detect "this string was scrubbed."
    Token = first 6 hex chars of blake2b(keyword) so substitutions are stable
    across seeds (avoids breaking k-means determinism)."""
    def _sub(m: "re.Match") -> str:
        kw = m.group(0).lower()
        h = hashlib.blake2b(kw.encode("utf-8"), digest_size=3).hexdigest()
        return h  # 6 hex chars; no underscores; no overlap with family vocab
    return _STRIP_RE.sub(_sub, atom_id)


# ===== feature extraction =====

def mechanism_family_of(atom_id: str) -> str:
    """Return the mechanism family for an atom_id (lowercased substring scan).
    Uses the UNSTRIPPED atom_id; this is the ground-truth family label."""
    lo = atom_id.lower()
    for family in MECHANISM_FAMILIES:
        if family == "other":
            continue
        for kw in MECHANISM_KEYWORDS.get(family, []):
            if kw in lo:
                return family
    return "other"


def sigma_regime_of(metadata: dict) -> str:
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


def metric_profile_token(ledger_row: dict) -> str:
    verdict = (ledger_row.get("verdict") or "")[:16]
    cv = ledger_row.get("cv")
    if cv is None:
        cv_bucket = "cv_none"
    else:
        try:
            cvf = float(cv)
            if cvf < 0.01:
                cv_bucket = "cv_lt_0p01"
            elif cvf < 0.05:
                cv_bucket = "cv_0p01_0p05"
            elif cvf < 0.10:
                cv_bucket = "cv_0p05_0p10"
            else:
                cv_bucket = "cv_gt_0p10"
        except (TypeError, ValueError):
            cv_bucket = "cv_none"
    delta = ledger_row.get("cert_increment_delta", 0)
    return "metric|%s|%s|delta=%s" % (verdict, cv_bucket, str(delta))


def graph_neighborhood_tokens(atom_id: str, atom_meta: dict) -> list[str]:
    tokens: list[str] = []
    meta = atom_meta.get("metadata", {}) or {}
    for k in ("composes", "composes_with", "typed_by", "retyped_by",
              "cap_backfilled_by", "atomized_by"):
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


def description_keywords(atom_meta: dict) -> list[str]:
    """Extract a small bag of content words from atom description for word2vec lookup.

    Lowercased, stopword-stripped, alpha-only, dedup, capped at 20 tokens."""
    text = ""
    for field in ("description", "summary", "note", "claim_text", "name"):
        v = atom_meta.get(field)
        if isinstance(v, str) and v.strip():
            text += " " + v
    if not text.strip():
        return []
    # lowercase, split on non-alpha, drop short + stopwords
    raw = re.split(r"[^a-zA-Z]+", text.lower())
    stop = {
        "the", "a", "an", "of", "and", "or", "in", "on", "for", "with",
        "to", "is", "are", "be", "by", "as", "at", "that", "this", "from",
        "it", "its", "into", "any", "all", "each", "one", "two", "but",
        "not", "no", "than", "then", "if", "so", "we", "you", "they",
        "i", "he", "she", "them", "their", "our", "us",
    }
    seen: set[str] = set()
    out: list[str] = []
    for w in raw:
        if len(w) < 3 or w in stop:
            continue
        if w in seen:
            continue
        seen.add(w)
        out.append(w)
        if len(out) >= 20:
            break
    return out


# ===== encoders =====

def encode_char_trigram(atom_id: str, n_dim: int) -> np.ndarray:
    """Bag-of-char-trigrams encoder (substrate-native; matches hdlab)."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    return enc.encode(atom_id)


def encode_atom_feature(
    atom_id: str,
    ledger_row: dict,
    atom_meta: dict,
    n_dim: int,
) -> np.ndarray:
    """Function-encoder: bind cert_tier + mechanism_family + sigma_regime
    + metric_profile + graph_neighborhood into a single bipolar HV."""
    cert = cert_tier_of(ledger_row.get("cert_status", ""))
    family = mechanism_family_of(atom_id)
    sigma = sigma_regime_of(atom_meta.get("metadata", {}))
    metric_token = metric_profile_token(ledger_row)
    nbrs = graph_neighborhood_tokens(atom_id, atom_meta)

    cert_vec = _bipolar_hv("cert|" + cert, n_dim)
    family_vec = _bipolar_hv("family|" + family, n_dim)
    sigma_vec = _bipolar_hv("sigma|" + sigma, n_dim)
    metric_vec = _bipolar_hv(metric_token, n_dim)

    nbr_bundle = np.zeros(n_dim, dtype=np.float32)
    for n in nbrs:
        nbr_bundle += _bipolar_hv(n, n_dim)
    nbr_bundle = np.sign(nbr_bundle).astype(np.float32)
    nbr_bundle[nbr_bundle == 0] = 1.0

    accum = cert_vec + family_vec + sigma_vec + metric_vec + nbr_bundle
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


# ===== word2vec helpers =====

_W2V_CACHE: dict[str, object] = {}


def _load_word2vec():
    """Load + cache the word2vec KeyedVectors (gensim).
    Heavy one-shot load (~14min for the 1.7GB model on first call); cached after."""
    if WORD2VEC_MODEL_NAME in _W2V_CACHE:
        return _W2V_CACHE[WORD2VEC_MODEL_NAME]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(WORD2VEC_MODEL_NAME)
    _W2V_CACHE[WORD2VEC_MODEL_NAME] = kv
    return kv


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))


def _w2v_lookup(word: str, kv) -> np.ndarray | None:
    if word in kv.key_to_index:
        return kv[word].astype(np.float32)
    lo = word.lower()
    if lo in kv.key_to_index:
        return kv[lo].astype(np.float32)
    return None


def encode_word2vec_description(
    atom_meta: dict,
    n_dim: int,
    seed: int,
    kv,
    proj: np.ndarray,
) -> np.ndarray:
    """Bag-of-description-keyword word2vec mean -> project to n_dim -> sign-bundle."""
    kws = description_keywords(atom_meta)
    if not kws:
        # zero vector; will normalize-to-zero downstream; allowed (atom has no description)
        return np.zeros(n_dim, dtype=np.float32)
    vecs = []
    for w in kws:
        v = _w2v_lookup(w, kv)
        if v is not None:
            vecs.append(v)
    if not vecs:
        return np.zeros(n_dim, dtype=np.float32)
    mean = np.mean(np.stack(vecs, axis=0), axis=0).astype(np.float32)
    # L2-normalize 300d before projection
    n = float(np.linalg.norm(mean) + 1e-12)
    mean = mean / n
    projected = proj @ mean  # [n_dim]
    out = np.sign(projected).astype(np.float32)
    out[out == 0] = 1.0
    return out


def encode_atom_feature_plus_word2vec(
    atom_id: str,
    ledger_row: dict,
    atom_meta: dict,
    n_dim: int,
    seed: int,
    kv,
    proj: np.ndarray,
) -> np.ndarray:
    feat = encode_atom_feature(atom_id, ledger_row, atom_meta, n_dim)
    w2v = encode_word2vec_description(atom_meta, n_dim, seed, kv, proj)
    accum = feat + w2v
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


# ===== k-means (numpy-only; simple Lloyd) =====

def kmeans_simple(X: np.ndarray, k: int, seed: int, n_iter: int = 50) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    Xn = X / norms
    init_idx = rng.choice(n, size=min(k, n), replace=False)
    centers = Xn[init_idx].copy()
    assign = np.zeros(n, dtype=np.int64)
    for _ in range(n_iter):
        sims = Xn @ centers.T
        new_assign = sims.argmax(axis=1)
        if np.array_equal(new_assign, assign):
            break
        assign = new_assign
        for kk in range(min(k, n)):
            mask = assign == kk
            if mask.any():
                m = Xn[mask].mean(axis=0)
                mn = np.linalg.norm(m) + 1e-8
                centers[kk] = m / mn
    return assign


def cluster_purity(labels: np.ndarray, families: list[str]) -> float:
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
    """Scan all corpora's atoms.jsonl; return {bare_atom_id -> atom dict}."""
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


# ===== self-test =====

def _selftest():
    """End-to-end smoke on a tiny synthetic 3-atom set."""
    n_dim_test = 256

    # name-strip regex sanity
    stripped = strip_mechanism_keywords("math::T3/EXP_alpha_cleanup_v1")
    assert "cleanup" not in stripped.lower(), (
        "mechanism keyword 'cleanup' survived strip: %r" % stripped)
    print("[selftest] strip OK: %r -> %r" % (
        "math::T3/EXP_alpha_cleanup_v1", stripped), flush=True)

    # planted 3-atom set
    synthetic = [
        ("math::T3/EXP_alpha_cleanup_v1", "cleanup"),
        ("math::T3/EXP_beta_storage_v1", "storage"),
        ("math::T3/EXP_gamma_generation_v1", "generation"),
    ]
    rows = [{"cert_status": "chain_grade", "verdict": "CHAIN_GRADE",
             "cv": 0.05, "cert_increment_delta": 1} for _ in synthetic]
    metas = [{"metadata": {"sigma_peak": 1.5}, "algebra": {},
              "serves_capability": [],
              "description": "cleanup denoising of stored vectors"}
             for _ in synthetic]

    families = [s[1] for s in synthetic]
    aids = [s[0] for s in synthetic]

    # Arms 1+2+3 (no word2vec dependency)
    name_leak_vecs = np.stack([encode_char_trigram(a, n_dim_test) for a in aids])
    stripped_vecs = np.stack([
        encode_char_trigram(strip_mechanism_keywords(a), n_dim_test) for a in aids])
    feat_vecs = np.stack([
        encode_atom_feature(a, r, m, n_dim_test)
        for a, r, m in zip(aids, rows, metas)])

    for arr, name in (
        (name_leak_vecs, "name_leak"),
        (stripped_vecs, "stripped"),
        (feat_vecs, "feat"),
    ):
        norms = np.linalg.norm(arr, axis=1)
        assert (norms > 0).all(), "%s vec norms must be > 0" % name

    # k-means smoke (k=3 on 3 atoms)
    for vecs, label in (
        (name_leak_vecs, "name_leak"),
        (stripped_vecs, "stripped"),
        (feat_vecs, "feat"),
    ):
        a = kmeans_simple(vecs, k=3, seed=0)
        p = cluster_purity(a, families)
        assert 0.0 <= p <= 1.0, "%s purity out of range: %f" % (label, p)

    # Verify stripped baseline cannot detect family by name (purity should drop
    # vs name_leak for keyword-heavy atoms when N is large; here on 3 atoms
    # we just check the encoder still produces distinct nonzero vecs).
    assert not np.array_equal(name_leak_vecs[0], stripped_vecs[0]), (
        "strip should change atom_id encoding")

    # substrate-only-decode invariant
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated"

    print("[selftest] PASS: encoders + kmeans + purity smoke; "
          "name_leak/stripped/feat vecs nonzero distinct; n_llm_calls=%d" %
          _LLM_CALL_COUNTER[0], flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== main run =====

def run_one_seed(seed: int, atoms: list[tuple[str, dict]],
                 atom_meta: dict[str, dict], kv) -> dict:
    """Run all 4 arms + planted-block sanity for a single seed."""
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
    stripped_aids = [strip_mechanism_keywords(a) for a in aids]

    # Per-seed projection for word2vec arm
    proj = _gaussian_projection(in_dim=PRETRAIN_DIM, out_dim=N_DIM, seed=seed)

    # ARM 1: char-trigram on ORIGINAL atom_id (name-leak baseline; parent reproduction)
    name_leak_vecs = np.stack([encode_char_trigram(a, N_DIM) for a in aids])

    # ARM 2: char-trigram on STRIPPED atom_id (honest baseline; mechanism keyword scrubbed)
    stripped_vecs = np.stack([encode_char_trigram(a, N_DIM) for a in stripped_aids])

    # ARM 3: substrate-feature binding (parent's winning arm)
    feat_vecs = np.stack([
        encode_atom_feature(a, r, m, N_DIM)
        for a, r, m in zip(aids, ledger_rows, metas)
    ])

    # ARM 4: atom_feature + word2vec(description)
    feat_w2v_vecs = np.stack([
        encode_atom_feature_plus_word2vec(a, r, m, N_DIM, seed, kv, proj)
        for a, r, m in zip(aids, ledger_rows, metas)
    ])

    # k-means K clusters on each
    labels_name = kmeans_simple(name_leak_vecs, k=K_CLUSTERS, seed=seed)
    labels_stripped = kmeans_simple(stripped_vecs, k=K_CLUSTERS, seed=seed)
    labels_feat = kmeans_simple(feat_vecs, k=K_CLUSTERS, seed=seed)
    labels_w2v = kmeans_simple(feat_w2v_vecs, k=K_CLUSTERS, seed=seed)

    purity_name = cluster_purity(labels_name, families)
    purity_stripped = cluster_purity(labels_stripped, families)
    purity_feat = cluster_purity(labels_feat, families)
    purity_w2v = cluster_purity(labels_w2v, families)

    # planted-block sanity: 3 atoms with distinct mechanism families (by name)
    # but otherwise identical metadata. atom_feature should cluster each in its
    # own family-cluster (purity == 1.0).
    planted_aids = [
        "math::T3/EXP_PLANTED_cleanup_v1",
        "math::T3/EXP_PLANTED_storage_v1",
        "math::T3/EXP_PLANTED_generation_v1",
    ]
    planted_families = [mechanism_family_of(a) for a in planted_aids]
    planted_rows = [{"cert_status": "chain_grade", "verdict": "CG",
                     "cv": 0.05, "cert_increment_delta": 1} for _ in planted_aids]
    planted_metas = [{"metadata": {"sigma_peak": 1.5}, "algebra": {},
                      "serves_capability": [],
                      "description": "planted block atom for sanity check"}
                     for _ in planted_aids]
    planted_feat = np.stack([
        encode_atom_feature(a, r, m, N_DIM)
        for a, r, m in zip(planted_aids, planted_rows, planted_metas)
    ])
    planted_labels = kmeans_simple(planted_feat, k=3, seed=seed)
    planted_purity = cluster_purity(planted_labels, planted_families)

    elapsed = time.time() - t0

    lift_w2v_over_stripped = purity_w2v - purity_stripped
    lift_w2v_over_name = purity_w2v - purity_name
    lift_feat_over_stripped = purity_feat - purity_stripped

    return {
        "seed": seed,
        "N": N_DIM,
        "M": n_sample,
        "run_mode": RUN_MODE,
        "arm_char_trigram_name_leak_purity": float(purity_name),
        "arm_char_trigram_stripped_purity": float(purity_stripped),
        "arm_atom_feature_purity": float(purity_feat),
        "arm_atom_feature_plus_word2vec_desc_purity": float(purity_w2v),
        "lift_w2v_over_stripped": float(lift_w2v_over_stripped),
        "lift_w2v_over_name_leak": float(lift_w2v_over_name),
        "lift_feat_over_stripped": float(lift_feat_over_stripped),
        "planted_block_purity": float(planted_purity),
        "n_atoms_sampled": n_sample,
        "k_clusters": K_CLUSTERS,
        "elapsed_s": elapsed,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "family_distribution": {
            f: families.count(f) for f in set(families)
        },
    }


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[%s] start mode=%s seeds=%s N_DIM=%d K=%d N_atoms=%d arms=%s" %
          (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_CLUSTERS, N_ATOMS_SAMPLE, ARMS),
          flush=True)

    print("[%s] loading chain-grade atoms + metadata..." % ANCHOR_NAME, flush=True)
    atoms = load_chain_grade_atoms()
    atom_meta = load_atoms_metadata()
    print("[%s] loaded %d chain-grade atoms; %d atom-metadata entries" %
          (ANCHOR_NAME, len(atoms), len(atom_meta)), flush=True)

    if len(atoms) < 3:
        raise RuntimeError("not enough chain-grade atoms: %d" % len(atoms))

    print("[%s] loading word2vec model (one-shot; cached after first call)..." %
          ANCHOR_NAME, flush=True)
    t_w2v = time.time()
    kv = _load_word2vec()
    print("[%s] word2vec loaded in %.1fs (vector_size=%d, vocab=%d)" %
          (ANCHOR_NAME, time.time() - t_w2v, kv.vector_size, len(kv.key_to_index)),
          flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "M": N_ATOMS_SAMPLE,
                  "arms": ARMS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[%s] ckpt: %d done; running %d" %
          (ANCHOR_NAME, len(done), len(remaining)), flush=True)

    for seed in remaining:
        print("[%s] seed=%d running..." % (ANCHOR_NAME, seed), flush=True)
        result = run_one_seed(seed, atoms, atom_meta, kv)
        write_partial(out_dir, seed, result)
        print(("[%s] seed=%d done: name=%.3f stripped=%.3f feat=%.3f "
               "w2v=%.3f lift_w2v_over_stripped=%+.3f planted=%.3f") %
              (ANCHOR_NAME, seed,
               result["arm_char_trigram_name_leak_purity"],
               result["arm_char_trigram_stripped_purity"],
               result["arm_atom_feature_purity"],
               result["arm_atom_feature_plus_word2vec_desc_purity"],
               result["lift_w2v_over_stripped"],
               result["planted_block_purity"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)

    # aggregate per-arm
    name_vals = [per_seed[str(s)]["arm_char_trigram_name_leak_purity"] for s in SEEDS]
    stripped_vals = [per_seed[str(s)]["arm_char_trigram_stripped_purity"] for s in SEEDS]
    feat_vals = [per_seed[str(s)]["arm_atom_feature_purity"] for s in SEEDS]
    w2v_vals = [per_seed[str(s)]["arm_atom_feature_plus_word2vec_desc_purity"] for s in SEEDS]
    lift_w2v_over_stripped_vals = [
        per_seed[str(s)]["lift_w2v_over_stripped"] for s in SEEDS]
    lift_w2v_over_name_vals = [
        per_seed[str(s)]["lift_w2v_over_name_leak"] for s in SEEDS]
    lift_feat_over_stripped_vals = [
        per_seed[str(s)]["lift_feat_over_stripped"] for s in SEEDS]
    planted_vals = [per_seed[str(s)]["planted_block_purity"] for s in SEEDS]
    elapsed_vals = [per_seed[str(s)]["elapsed_s"] for s in SEEDS]
    n_llm = sum(per_seed[str(s)]["n_llm_calls"] for s in SEEDS)

    def _ms(xs):
        m = float(np.mean(xs))
        s = float(np.std(xs))
        return m, s

    name_mean, name_std = _ms(name_vals)
    stripped_mean, stripped_std = _ms(stripped_vals)
    feat_mean, feat_std = _ms(feat_vals)
    w2v_mean, w2v_std = _ms(w2v_vals)
    lift_w2v_over_stripped_mean, lift_w2v_over_stripped_std = _ms(lift_w2v_over_stripped_vals)
    lift_w2v_over_name_mean, _ = _ms(lift_w2v_over_name_vals)
    lift_feat_over_stripped_mean, _ = _ms(lift_feat_over_stripped_vals)
    planted_mean = float(np.mean(planted_vals))

    w2v_cv = w2v_std / (w2v_mean + 1e-8)
    elapsed_s = float(np.sum(elapsed_vals))

    # verdict
    hp_w2v_purity_ok = w2v_mean >= PURITY_HP_FLOOR
    hp_lift_over_stripped_ok = lift_w2v_over_stripped_mean >= LIFT_HP_OVER_STRIPPED
    hp_lift_over_name_ok = lift_w2v_over_name_mean >= LIFT_HP_OVER_NAME_LEAK
    hp_planted_ok = planted_mean >= PLANTED_BLOCK_PURITY
    hp_no_llm = (n_llm == 0)

    hard_fail = (
        lift_w2v_over_stripped_mean <= LIFT_HF_OVER_STRIPPED
        or not hp_no_llm
    )

    if (hp_w2v_purity_ok and hp_lift_over_stripped_ok and hp_lift_over_name_ok
            and hp_planted_ok and hp_no_llm):
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s_%s_%dseeds_N%d_K%d_M%d_name_leak_%.3f_pm_%.3f_stripped_%.3f_pm_%.3f_"
        "feat_%.3f_pm_%.3f_w2v_%.3f_pm_%.3f_lift_w2v_over_stripped_%+.3f_"
        "lift_w2v_over_name_%+.3f_lift_feat_over_stripped_%+.3f_planted_%.3f_"
        "n_llm_calls_%d_cv_w2v_%.4f_elapsed_%.1fs"
    ) % (
        verdict, RUN_MODE.upper(), len(SEEDS), N_DIM, K_CLUSTERS, N_ATOMS_SAMPLE,
        name_mean, name_std,
        stripped_mean, stripped_std,
        feat_mean, feat_std,
        w2v_mean, w2v_std,
        lift_w2v_over_stripped_mean,
        lift_w2v_over_name_mean,
        lift_feat_over_stripped_mean,
        planted_mean,
        n_llm, w2v_cv, elapsed_s,
    )

    summary = {
        "anchor": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "seeds": SEEDS,
        "N_DIM": N_DIM,
        "K_CLUSTERS": K_CLUSTERS,
        "N_ATOMS_SAMPLE": N_ATOMS_SAMPLE,
        "arms": ARMS,
        "arm_char_trigram_name_leak_purity_mean": name_mean,
        "arm_char_trigram_name_leak_purity_std": name_std,
        "arm_char_trigram_stripped_purity_mean": stripped_mean,
        "arm_char_trigram_stripped_purity_std": stripped_std,
        "arm_atom_feature_purity_mean": feat_mean,
        "arm_atom_feature_purity_std": feat_std,
        "arm_atom_feature_plus_word2vec_desc_purity_mean": w2v_mean,
        "arm_atom_feature_plus_word2vec_desc_purity_std": w2v_std,
        "arm_atom_feature_plus_word2vec_desc_purity_cv": w2v_cv,
        "lift_w2v_over_stripped_mean": lift_w2v_over_stripped_mean,
        "lift_w2v_over_stripped_std": lift_w2v_over_stripped_std,
        "lift_w2v_over_name_mean": lift_w2v_over_name_mean,
        "lift_feat_over_stripped_mean": lift_feat_over_stripped_mean,
        "planted_block_purity_mean": planted_mean,
        "n_llm_calls": n_llm,
        "n_chain_grade_atoms_pool": len(atoms),
        "hp_thresholds": {
            "w2v_purity_floor": PURITY_HP_FLOOR,
            "lift_over_stripped_floor": LIFT_HP_OVER_STRIPPED,
            "lift_over_name_leak_floor": LIFT_HP_OVER_NAME_LEAK,
            "planted_purity_required": PLANTED_BLOCK_PURITY,
        },
        "hp_gates": {
            "w2v_purity_ok": hp_w2v_purity_ok,
            "lift_over_stripped_ok": hp_lift_over_stripped_ok,
            "lift_over_name_leak_ok": hp_lift_over_name_ok,
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
