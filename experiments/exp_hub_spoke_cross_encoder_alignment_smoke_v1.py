"""hub_spoke_cross_encoder_alignment_smoke_v1 -- Damasio CDZ analog (word-only).

USER 2026-06-23: test the HUB-AND-SPOKE federation mechanism at word-only scope
first; LATER cells add atom-spoke + entity-spoke + relation-spoke. The HUB is a
shared substrate HD subspace that aligns outputs from multiple encoder spokes so
the same concept produces the same hub vector regardless of which spoke encoded
it. Brain analog: Damasio convergence-divergence zones (posterior medial cortex)
integrate V1/A1/S1 streams into unified concept representations.

DESIGN (4 hub-mechanism ARMS x 3 word-encoder spokes x V words):

Reference vocab: words drawn from WordSim353 + SimLex-999 that are in-vocab on
ALL 3 spokes (word2vec_300d, glove_300d, fasttext_300d). Capped at 200 for the
"smoke_v1" scope. These are the words we KNOW have reliable cross-encoder
representations (per clean_encoder_eval_harness_v1 HARD_PASS).

Each word w -> 3 spoke vectors (300d) -> hub vector at N_DIM=4096 per ARM.

Arms (hub-mechanism candidates):
  ARM_NO_HUB_RAW          -- baseline; project each spoke's 300d to 4096d via
                             fresh random Gaussian PER-SPOKE; average the 3
                             projected vectors. Expected to fail because spoke
                             feature spaces are not aligned.
  ARM_NO_HUB_PROJECT      -- baseline; same Gaussian projection PER-SPOKE (per
                             seed) but L2-normalize each projected spoke before
                             averaging. Still expected to fail.
  ARM_BIND_BUNDLE_HUB     -- substrate-native HRR-style; bind each spoke's
                             projected 4096d vector with a SPOKE_TAG bipolar
                             hypervector (random per spoke, fixed per seed),
                             bundle by sum, sign-normalize. Read out via
                             unbind(hub, SPOKE_TAG). The proposed primitive.
  ARM_LEARNED_LINEAR_ALIGN -- learned linear projection per-spoke (W_w2v,
                             W_glove, W_ft) trained to minimize average distance
                             between projected vectors of the SAME word across
                             encoders. NumPy SGD contrastive loss; ~200 epochs.
                             Backprop arm; upper-bound baseline.

METRIC: cross-encoder alignment discrimination =
    mean_w cosine(hub_from_X[w], hub_from_Y[w]) / mean_{w!=w'} cosine(hub_from_X[w], hub_from_Y[w'])
  averaged across all encoder-pairs (X,Y) in {w2v, glove, ft}.

For ARM_BIND_BUNDLE_HUB:
  hub_from_X[w] = unbind(hub[w], SPOKE_TAG_X) projected back to 4096d (i.e. the
  spoke-X-readout of the bundled hub). Same-word same-spoke-readout cosines
  should be similar across X,Y because the BIND_BUNDLE construction shares
  geometry by design.

For ARM_LEARNED_LINEAR_ALIGN:
  hub_from_X[w] = W_X @ spoke_vec_X[w], projected to 4096d. Trained to make
  these match across spokes for the SAME word.

For ARM_NO_HUB_*:
  hub_from_X[w] = project_to_4096(spoke_vec_X[w]) (no fusion). Different X give
  different hub_X[w] so cross-spoke cosine is near 0 even for same word.

PRE-REG bands (preregs/2026-06-23_hub_spoke_cross_encoder_alignment_smoke_v1.md):
  HARD_PASS: ARM_BIND_BUNDLE_HUB discrimination >= 3.0 AND
             ARM_LEARNED_LINEAR_ALIGN discrimination >= 5.0 AND
             both >= 2x ARM_NO_HUB_RAW discrimination.
  HARD_FAIL: ALL 4 arms discrimination <= 1.5.
  MIDDLE:    partial; one mechanism works but not the other.

SANITY:
  Identity check: when all 3 spokes are IDENTICAL (artificial test using only
  word2vec for all 3 spokes), discrimination should be very high (well above
  pre-reg HARD_PASS) for ALL arms.

SCOPE CAVEAT (USER 2026-06-23):
  Word-only scope. Whether the hub mechanism transfers to atom-spokes,
  entity-spokes, relation-spokes is a SEPARATE later cell, deferred.

SUBSTRATE-NATIVE: no LLM at inference. Pretrained word encoders are static
open-weight lookups. Bind-bundle is substrate primitive (FHRR-style binary
bipolar). Learned-align is contrastive SGD in numpy.

Cites:
  - preregs/2026-06-23_hub_spoke_cross_encoder_alignment_smoke_v1.md
  - experiments/exp_clean_encoder_eval_harness_v1.py (sibling; word encoders HARD_PASS)
  - notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md
  - Damasio 1989 (convergence-divergence zones)
  - Kanerva 2009 (HRR / VSA)
  - USER_2026-06-23_hub_spoke_word_only_first_cell_approval
"""
from __future__ import annotations
import sys, os, argparse, time, hashlib, atexit
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "hub_spoke_cross_encoder_alignment_smoke_v1"
BENCH_DIR = REPO / "data" / "encoder_eval_benchmarks"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WS353_FILE = BENCH_DIR / "wordsim353_combined.csv"
SIMLEX_FILE = BENCH_DIR / "simlex999.txt"

_LLM_CALL_COUNTER = [0]

# Pre-reg discrimination bands
HP_BIND_BUNDLE_DISCRIM = 3.0
HP_LEARNED_LINEAR_DISCRIM = 5.0
HP_BEAT_NO_HUB_RATIO = 2.0
HF_DISCRIM_CEILING = 1.5

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
PRETRAIN_DIM = 300

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    VOCAB_CAP = 200
    SGD_EPOCHS = 200
else:
    SEEDS = [0]
    VOCAB_CAP = 30
    SGD_EPOCHS = 30

ARMS = [
    "ARM_NO_HUB_RAW",
    "ARM_NO_HUB_PROJECT",
    "ARM_BIND_BUNDLE_HUB",
    "ARM_LEARNED_LINEAR_ALIGN",
]
SPOKES = ["w2v", "glove", "ft"]
GENSIM_MODEL_FOR_SPOKE = {
    "w2v":   "word2vec-google-news-300",
    "glove": "glove-wiki-gigaword-300",
    "ft":    "fasttext-wiki-news-subwords-300",
}

CONFIG_VERSION = (
    "hub_spoke_cross_encoder_alignment_smoke_v1; N_DIM=%d PRETRAIN_DIM=%d "
    "seeds=%s vocab_cap=%d sgd_epochs=%d arms=%s spokes=%s mode=%s; "
    "bands HP_bind_bundle>=%.1f HP_learned>=%.1f HP_beat_no_hub>=%.1fx "
    "HF_all<=%.1f"
) % (
    N_DIM, PRETRAIN_DIM, SEEDS, VOCAB_CAP, SGD_EPOCHS, ARMS, SPOKES, RUN_MODE,
    HP_BIND_BUNDLE_DISCRIM, HP_LEARNED_LINEAR_DISCRIM, HP_BEAT_NO_HUB_RATIO,
    HF_DISCRIM_CEILING,
)


# ============================================================================
# Pretrained-model loader (shared cache; same as clean_encoder_eval_harness_v1)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(model_name)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


# ============================================================================
# Reference vocab loader
# ============================================================================

def load_wordsim_simlex_words() -> List[str]:
    """Collect unique words from WS353 + SimLex999 benchmark files; order-preserved."""
    seen = []
    sset = set()

    def _add(w: str) -> None:
        w = w.strip()
        if w and w not in sset:
            seen.append(w); sset.add(w)

    if WS353_FILE.exists():
        import csv
        with open(WS353_FILE, "r", encoding="utf-8") as fh:
            r = csv.reader(fh)
            try:
                next(r)
            except StopIteration:
                pass
            for row in r:
                if len(row) >= 2:
                    _add(row[0]); _add(row[1])

    if SIMLEX_FILE.exists():
        with open(SIMLEX_FILE, "r", encoding="utf-8") as fh:
            fh.readline()
            for line in fh:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    _add(parts[0]); _add(parts[1])

    return seen


def filter_in_vocab_all_spokes(words: List[str]) -> List[str]:
    """Keep only words in-vocab on ALL 3 spokes (word2vec / glove / fasttext)."""
    kvs = [_load_gensim_kv(GENSIM_MODEL_FOR_SPOKE[sp]) for sp in SPOKES]
    out = []
    for w in words:
        ok = True
        for kv in kvs:
            if w in kv.key_to_index or w.lower() in kv.key_to_index:
                continue
            try:
                _ = kv.get_vector(w, norm=False)
            except Exception:
                ok = False; break
        if ok:
            out.append(w)
    return out


# ============================================================================
# Substrate primitives -- HRR bipolar bind / unbind / bundle
# ============================================================================

def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def _sign_normalize(x: np.ndarray) -> np.ndarray:
    """Bipolar sign-normalize; zeros -> +1 (substrate convention)."""
    out = np.sign(x).astype(np.float32)
    if out.ndim == 1:
        out[out == 0] = 1.0
    else:
        out[out == 0] = 1.0
    return out


def _l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def bind_bipolar(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise bipolar binding (XOR-equivalent on +/-1). Self-inverse."""
    return (a * b).astype(np.float32)


def unbind_bipolar(hub: np.ndarray, tag: np.ndarray) -> np.ndarray:
    """Element-wise unbind = bind because tag*tag = +1 elementwise (bipolar)."""
    return (hub * tag).astype(np.float32)


def _spoke_tag(spoke: str, seed: int, n_dim: int) -> np.ndarray:
    """Deterministic per-(spoke, seed) bipolar tag hypervector."""
    h = hashlib.blake2b(("SPOKE_TAG:" + spoke + ":" + str(seed)).encode("utf-8"),
                         digest_size=4).digest()
    seed_val = int.from_bytes(h, "big")
    return _bipolar_hv(seed_val, n_dim)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int, salt: int = 0) -> np.ndarray:
    """Random Gaussian projection [out_dim, in_dim] with 1/sqrt(in_dim) scale (JL)."""
    rng = np.random.default_rng(seed * 991 + 73 + salt * 7919)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# ============================================================================
# Encoding to spoke vectors (300d), then per-arm hub construction
# ============================================================================

def encode_words_per_spoke(words: List[str]) -> Dict[str, np.ndarray]:
    """Per-spoke [V, PRETRAIN_DIM=300] L2-normalized matrix. Assumes filter_in_vocab."""
    V = len(words)
    out: Dict[str, np.ndarray] = {}
    for sp in SPOKES:
        kv = _load_gensim_kv(GENSIM_MODEL_FOR_SPOKE[sp])
        E = np.zeros((V, PRETRAIN_DIM), dtype=np.float32)
        for i, w in enumerate(words):
            v = None
            if w in kv.key_to_index:
                v = kv[w]
            elif w.lower() in kv.key_to_index:
                v = kv[w.lower()]
            else:
                v = kv.get_vector(w, norm=False)
            E[i] = v.astype(np.float32)
        out[sp] = _l2_normalize(E)
    return out


def arm_no_hub_raw(spoke_E300: Dict[str, np.ndarray], seed: int) -> Dict[str, np.ndarray]:
    """Per-spoke hub readout = own projection to 4096d via per-spoke Gaussian.

    No fusion across spokes. Different spokes give independent random projections
    of their own 300d. Expected discrimination near 1.0 because cosine cross-spoke
    of independent random projections is ~0.
    """
    out = {}
    for salt, sp in enumerate(SPOKES):
        P = _gaussian_projection(PRETRAIN_DIM, N_DIM, seed=seed, salt=salt + 1)
        proj = (spoke_E300[sp] @ P.T).astype(np.float32)
        out[sp] = proj  # NOT renormalized (raw)
    return out


def arm_no_hub_project(spoke_E300: Dict[str, np.ndarray], seed: int) -> Dict[str, np.ndarray]:
    """Same as RAW but each per-spoke projection is L2-normalized after projection."""
    out = {}
    for salt, sp in enumerate(SPOKES):
        P = _gaussian_projection(PRETRAIN_DIM, N_DIM, seed=seed, salt=salt + 1)
        proj = (spoke_E300[sp] @ P.T).astype(np.float32)
        out[sp] = _l2_normalize(proj)
    return out


def arm_bind_bundle_hub(spoke_E300: Dict[str, np.ndarray], seed: int) -> Dict[str, np.ndarray]:
    """Substrate-native multi-spoke integration via HRR bind+bundle (real-valued).

    Step 1: project each spoke's 300d to 4096d via a SHARED Gaussian P (one P,
            all spokes use the same projection so the only spoke-distinguishing
            signal is the BIND tag, not the projection randomness). Keep
            REAL-VALUED projection (do NOT sign-collapse) so the bundle is a
            real-valued superposition that preserves per-spoke information.
    Step 2: L2-normalize per-spoke projection for cosine-comparability.
    Step 3: bind each spoke's projection with its SPOKE_TAG_sp bipolar tag
            (element-wise multiply; bipolar tag flips signs of the projection).
    Step 4: bundle by SUM across the 3 spokes; the hub is a real-valued
            superposition. Do NOT sign-collapse: sign-collapse destroys per-
            word information by reducing the readout to tag-correlation only
            (mathematical artifact -- readout_X * readout_Y = tag_X * tag_Y
            independent of w under any sign-collapsed bundle).
    Step 5: per-spoke readout = hub * SPOKE_TAG_sp (real-valued unbind);
            L2-normalize for cosine. For same word w different X,Y readouts
            share the hub bundle so cosine(readout_X[w], readout_Y[w]) =
            (proj_X[w]*proj_Y[w]) / N + cross-talk terms (which average to
            zero across the V words assuming tag-randomness). Same-word align
            > diff-word align iff spokes carry shared semantic structure for
            the same w that survives JL projection.
    """
    V = next(iter(spoke_E300.values())).shape[0]
    P = _gaussian_projection(PRETRAIN_DIM, N_DIM, seed=seed, salt=0)
    proj: Dict[str, np.ndarray] = {}
    for sp in SPOKES:
        p = (spoke_E300[sp] @ P.T).astype(np.float32)
        proj[sp] = _l2_normalize(p)
    tags: Dict[str, np.ndarray] = {sp: _spoke_tag(sp, seed, N_DIM) for sp in SPOKES}
    # Real-valued bind + sum-bundle (NO sign-collapse).
    hub = np.zeros((V, N_DIM), dtype=np.float32)
    for sp in SPOKES:
        hub += proj[sp] * tags[sp]
    # Per-spoke readout = hub * tag (real-valued unbind); L2-normalize.
    out: Dict[str, np.ndarray] = {}
    for sp in SPOKES:
        readout = hub * tags[sp]
        out[sp] = _l2_normalize(readout).astype(np.float32)
    return out


def arm_learned_linear_align(spoke_E300: Dict[str, np.ndarray], seed: int,
                              epochs: int = 200) -> Dict[str, np.ndarray]:
    """Learn W_sp [N_DIM, 300] per spoke s.t. W_sp @ e_sp[w] matches across spokes for same w.

    Contrastive objective:
        L = mean_w_pairs same:   ||proj_X[w] - proj_Y[w]||^2
          - alpha * mean_w_pairs diff: ||proj_X[w] - proj_Y[w']||^2
    Optimized by SGD on per-spoke W. Output unit-norm projected vectors per spoke
    aligned across spokes for the SAME word.

    For speed/simplicity: initialize with the same Gaussian P (warm start aligned
    by construction); SGD reduces residual misalignment.
    """
    V = next(iter(spoke_E300.values())).shape[0]
    P0 = _gaussian_projection(PRETRAIN_DIM, N_DIM, seed=seed, salt=999)
    Ws: Dict[str, np.ndarray] = {sp: P0.copy() for sp in SPOKES}
    rng = np.random.default_rng(seed * 7919 + 31)
    # Centered E (subtract per-spoke mean) helps stability
    E_c: Dict[str, np.ndarray] = {}
    for sp in SPOKES:
        e = spoke_E300[sp]
        E_c[sp] = e - e.mean(axis=0, keepdims=True)
    lr = 0.05
    alpha = 0.5  # diff-pair repel weight
    n_diff_per_batch = max(1, V // 4)
    for ep in range(epochs):
        # Forward all spoke projections (full-batch for V <= 200)
        proj: Dict[str, np.ndarray] = {sp: (E_c[sp] @ Ws[sp].T).astype(np.float32) for sp in SPOKES}
        proj_n: Dict[str, np.ndarray] = {sp: _l2_normalize(proj[sp]) for sp in SPOKES}
        # Same-word loss: pull X[w] and Y[w] together
        grad_W: Dict[str, np.ndarray] = {sp: np.zeros_like(Ws[sp]) for sp in SPOKES}
        # Use unnormalized squared distance gradient for tractability
        for i in range(len(SPOKES)):
            for j in range(i + 1, len(SPOKES)):
                X, Y = SPOKES[i], SPOKES[j]
                diff = proj[X] - proj[Y]
                # d/dW_X (sum_w ||proj_X[w] - proj_Y[w]||^2) = 2 * diff^T @ E_X
                grad_W[X] += (2.0 / V) * (diff.T @ E_c[X])
                grad_W[Y] += -(2.0 / V) * (diff.T @ E_c[Y])
        # Diff-word repel: randomly sample non-matched pairs and push apart
        idx = rng.permutation(V)
        for i in range(len(SPOKES)):
            for j in range(i + 1, len(SPOKES)):
                X, Y = SPOKES[i], SPOKES[j]
                w_idx = np.arange(V)
                wp_idx = idx[(w_idx + 1 + (rng.integers(0, V - 1, size=V)) % (V - 1)) % V]
                wp_idx = wp_idx[:n_diff_per_batch]
                wa_idx = w_idx[:n_diff_per_batch]
                diff = proj[X][wa_idx] - proj[Y][wp_idx]
                grad_W[X] += -(alpha * 2.0 / n_diff_per_batch) * (diff.T @ E_c[X][wa_idx])
                grad_W[Y] += (alpha * 2.0 / n_diff_per_batch) * (diff.T @ E_c[Y][wp_idx])
        # SGD step
        for sp in SPOKES:
            Ws[sp] -= lr * grad_W[sp]
            # Constrain row norms to roughly the JL scale to avoid runaway
            row_norms = np.linalg.norm(Ws[sp], axis=1, keepdims=True) + 1e-12
            target = 1.0 / np.sqrt(float(PRETRAIN_DIM))
            scale = np.clip(target / row_norms, 0.5, 2.0)
            # Actually want to keep norm near (out_dim * target^2)^.5; we cap stability instead
            mx = float(np.max(row_norms))
            if mx > 5.0 * target:
                Ws[sp] = Ws[sp] * (5.0 * target / mx)
    out: Dict[str, np.ndarray] = {}
    for sp in SPOKES:
        proj = (E_c[sp] @ Ws[sp].T).astype(np.float32)
        out[sp] = _l2_normalize(proj)
    return out


# ============================================================================
# Cross-encoder alignment discrimination metric
# ============================================================================

def cross_encoder_alignment_discrim(hub_per_spoke: Dict[str, np.ndarray]) -> Dict:
    """Compute alignment discrimination ratio for an arm.

    Same-word alignment: mean cosine(hub_X[w], hub_Y[w]) over w and all (X,Y) pairs.
    Diff-word alignment: mean cosine(hub_X[w], hub_Y[w']) over w!=w' and all pairs.
    Discrimination = same / max(|diff|, eps).
    """
    spokes = list(hub_per_spoke.keys())
    V = hub_per_spoke[spokes[0]].shape[0]
    # L2-normalize for cosine; ARMs may already be normalized, harmless to renorm
    Hn = {sp: _l2_normalize(hub_per_spoke[sp]) for sp in spokes}
    same_cosines: List[float] = []
    diff_cosines: List[float] = []
    for i in range(len(spokes)):
        for j in range(i + 1, len(spokes)):
            X, Y = spokes[i], spokes[j]
            # Same word: diagonal of Hn[X] @ Hn[Y].T
            G = Hn[X] @ Hn[Y].T  # [V, V]
            same = np.diag(G).astype(np.float64)
            # Diff word: off-diagonal entries
            mask = ~np.eye(V, dtype=bool)
            diff = G[mask].astype(np.float64)
            same_cosines.extend(same.tolist())
            diff_cosines.extend(diff.tolist())
    same_mean = float(np.mean(same_cosines))
    diff_mean = float(np.mean(diff_cosines))
    eps = 1e-6
    # Magnitude-based discrimination: how much MORE aligned same-word pairs are
    # than diff-word pairs (in absolute cosine terms). Robust to sign-collapse
    # artifacts of bipolar projections; HARD_PASS bands defined on this ratio.
    # We additionally require same_mean > diff_mean (signed) for the hub to
    # actually distinguish same from different words.
    discrim_mag = float(abs(same_mean) / max(abs(diff_mean), eps))
    # Signed ordering check: is same > diff?
    signed_separation = float(same_mean - diff_mean)
    return {
        "same_word_align_mean": round(same_mean, 6),
        "diff_word_align_mean": round(diff_mean, 6),
        "discrimination": round(discrim_mag, 4),
        "signed_separation": round(signed_separation, 6),
        "n_same_pairs": len(same_cosines),
        "n_diff_pairs": len(diff_cosines),
    }


# ============================================================================
# Sanity check -- identical spokes -> infinite discrimination
# ============================================================================

def sanity_identical_spokes(seed: int, vocab: List[str]) -> Dict:
    """Make all 3 spokes IDENTICAL (use word2vec 3x); discrim should be very high."""
    kv = _load_gensim_kv(GENSIM_MODEL_FOR_SPOKE["w2v"])
    V = len(vocab)
    E = np.zeros((V, PRETRAIN_DIM), dtype=np.float32)
    for i, w in enumerate(vocab):
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        else:
            v = kv.get_vector(w, norm=False)
        E[i] = v.astype(np.float32)
    E = _l2_normalize(E)
    fake = {sp: E.copy() for sp in SPOKES}
    out = {}
    for arm in ARMS:
        hub_per_spoke = run_arm(arm, fake, seed)
        d = cross_encoder_alignment_discrim(hub_per_spoke)
        out[arm] = d["discrimination"]
    return out


def run_arm(arm: str, spoke_E300: Dict[str, np.ndarray], seed: int) -> Dict[str, np.ndarray]:
    if arm == "ARM_NO_HUB_RAW":
        return arm_no_hub_raw(spoke_E300, seed)
    if arm == "ARM_NO_HUB_PROJECT":
        return arm_no_hub_project(spoke_E300, seed)
    if arm == "ARM_BIND_BUNDLE_HUB":
        return arm_bind_bundle_hub(spoke_E300, seed)
    if arm == "ARM_LEARNED_LINEAR_ALIGN":
        return arm_learned_linear_align(spoke_E300, seed, epochs=SGD_EPOCHS)
    raise ValueError("unknown arm: " + arm)


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] loading reference vocab (WS353 + SimLex999)" % seed, flush=True)
    all_words = load_wordsim_simlex_words()
    print("[seed=%d] candidate vocab = %d words" % (seed, len(all_words)), flush=True)
    in_vocab = filter_in_vocab_all_spokes(all_words)
    print("[seed=%d] in-vocab across all 3 spokes = %d words" % (seed, len(in_vocab)),
          flush=True)
    vocab = in_vocab[:VOCAB_CAP]
    print("[seed=%d] using V=%d (cap=%d)" % (seed, len(vocab), VOCAB_CAP), flush=True)

    t_enc = time.time()
    spoke_E300 = encode_words_per_spoke(vocab)
    print("[seed=%d] spoke encoding wall=%.1fs" % (seed, time.time() - t_enc), flush=True)

    by_arm: Dict[str, Dict] = {}
    for arm in ARMS:
        t_arm = time.time()
        hub_per_spoke = run_arm(arm, spoke_E300, seed)
        metric = cross_encoder_alignment_discrim(hub_per_spoke)
        metric["wall_s"] = round(time.time() - t_arm, 2)
        by_arm[arm] = metric
        print("  [seed=%d arm=%s] same=%.4f diff=%.4f discrim=%.3f (%.1fs)" % (
            seed, arm,
            metric["same_word_align_mean"], metric["diff_word_align_mean"],
            metric["discrimination"], metric["wall_s"]), flush=True)

    sanity = sanity_identical_spokes(seed, vocab[:min(20, len(vocab))])
    print("[seed=%d] sanity (identical-spokes) discrim per arm: %s" % (seed, sanity),
          flush=True)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "sanity_identical_spokes": sanity,
        "N_DIM": N_DIM,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "vocab_size": int(len(vocab)),
        "in_vocab_pool_size": int(len(in_vocab)),
        "sgd_epochs": SGD_EPOCHS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def _mean_finite(vals: List[float]) -> Optional[float]:
    vs = [v for v in vals if v is not None and np.isfinite(v)]
    if not vs:
        return None
    return float(np.mean(vs))


def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no units recovered", {})
    arms = list(units[0]["by_arm"].keys())
    agg: Dict[str, Dict] = {}
    for arm in arms:
        discrims = [u["by_arm"][arm]["discrimination"] for u in units]
        sames = [u["by_arm"][arm]["same_word_align_mean"] for u in units]
        diffs = [u["by_arm"][arm]["diff_word_align_mean"] for u in units]
        agg[arm] = {
            "discrim_mean": round(_mean_finite(discrims) or 0.0, 4),
            "discrim_per_seed": [round(d, 4) for d in discrims],
            "same_mean": round(_mean_finite(sames) or 0.0, 6),
            "diff_mean": round(_mean_finite(diffs) or 0.0, 6),
        }

    bb_discrim = agg["ARM_BIND_BUNDLE_HUB"]["discrim_mean"]
    la_discrim = agg["ARM_LEARNED_LINEAR_ALIGN"]["discrim_mean"]
    no_hub_raw_discrim = agg["ARM_NO_HUB_RAW"]["discrim_mean"]
    no_hub_proj_discrim = agg["ARM_NO_HUB_PROJECT"]["discrim_mean"]
    # Signed separation (same - diff) per arm; require positive for HP
    bb_sep = float(_mean_finite([u["by_arm"]["ARM_BIND_BUNDLE_HUB"].get("signed_separation", 0.0)
                                   for u in units]) or 0.0)
    la_sep = float(_mean_finite([u["by_arm"]["ARM_LEARNED_LINEAR_ALIGN"].get("signed_separation", 0.0)
                                   for u in units]) or 0.0)

    bb_hp = (bb_discrim >= HP_BIND_BUNDLE_DISCRIM) and (bb_sep > 0.0)
    la_hp = (la_discrim >= HP_LEARNED_LINEAR_DISCRIM) and (la_sep > 0.0)
    bb_beats = bb_discrim >= HP_BEAT_NO_HUB_RATIO * max(no_hub_raw_discrim, 1e-6)
    la_beats = la_discrim >= HP_BEAT_NO_HUB_RATIO * max(no_hub_raw_discrim, 1e-6)
    all_hf = all(agg[a]["discrim_mean"] <= HF_DISCRIM_CEILING for a in arms)

    detail = {
        "agg": agg,
        "checks": {
            "bind_bundle_hard_pass_threshold": bool(bb_hp),
            "learned_linear_hard_pass_threshold": bool(la_hp),
            "bind_bundle_beats_no_hub_raw_2x": bool(bb_beats),
            "learned_linear_beats_no_hub_raw_2x": bool(la_beats),
            "all_arms_below_HF_ceiling": bool(all_hf),
            "bind_bundle_signed_separation": round(bb_sep, 6),
            "learned_linear_signed_separation": round(la_sep, 6),
        },
        "bands": {
            "HP_BIND_BUNDLE_DISCRIM": HP_BIND_BUNDLE_DISCRIM,
            "HP_LEARNED_LINEAR_DISCRIM": HP_LEARNED_LINEAR_DISCRIM,
            "HP_BEAT_NO_HUB_RATIO": HP_BEAT_NO_HUB_RATIO,
            "HF_DISCRIM_CEILING": HF_DISCRIM_CEILING,
        },
        "sanity_identical_spokes_per_unit": [u.get("sanity_identical_spokes") for u in units],
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Hub-and-spoke (Damasio CDZ) mechanism test at word-only scope; 4 hub "
            "mechanisms (NO_HUB_RAW / NO_HUB_PROJECT / BIND_BUNDLE_HUB / "
            "LEARNED_LINEAR_ALIGN) x 3 word encoders (w2v/glove/ft) x V<=%d in-vocab "
            "WordSim353+SimLex999 words x %d seeds. Metric: cross-encoder alignment "
            "discrimination = same-word cross-spoke cosine / diff-word cross-spoke "
            "cosine. HARD_PASS = BIND_BUNDLE>=%.1f AND LEARNED>=%.1f AND both beat "
            "NO_HUB_RAW by %.1fx. HARD_FAIL = all arms discrim<=%.1f. Word-only scope "
            "PER USER 2026-06-23 explicit caveat -- later cells will test atom-spoke / "
            "entity-spoke / relation-spoke. Substrate-native: bind-bundle uses "
            "bipolar HRR primitives; LEARNED uses contrastive numpy SGD; no LLM at "
            "inference."
        ) % (VOCAB_CAP, len(units), HP_BIND_BUNDLE_DISCRIM, HP_LEARNED_LINEAR_DISCRIM,
              HP_BEAT_NO_HUB_RATIO, HF_DISCRIM_CEILING),
        "cites": [
            "preregs/2026-06-23_hub_spoke_cross_encoder_alignment_smoke_v1.md",
            "experiments/exp_clean_encoder_eval_harness_v1.py",
            "notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md",
            "Damasio_1989_CDZ",
            "Kanerva_2009_HRR_VSA",
            "USER_2026-06-23_hub_spoke_word_only_first_cell_approval",
        ],
    }

    parts = []
    for a in arms:
        parts.append("%s=disc%.2f" % (a, agg[a]["discrim_mean"]))
    summary = "HUB_SPOKE_CROSS_ENCODER: " + " | ".join(parts) + " | scope=words_only"

    hard_pass_overall = bb_hp and la_hp and bb_beats and la_beats
    if hard_pass_overall:
        return ("HARD_PASS",
                ("HUB_SPOKE_CROSS_ENCODER HARD_PASS: BIND_BUNDLE_HUB discrim=%.2f >= %.1f "
                 "AND LEARNED_LINEAR_ALIGN discrim=%.2f >= %.1f AND both >= %.1fx NO_HUB_RAW "
                 "(=%.2f). Hub-and-spoke fusion mechanism real for words; substrate-native "
                 "multi-encoder integration works. WORD-ONLY SCOPE per USER 2026-06-23; "
                 "atom/entity/relation spoke transfer DEFERRED to later cell. "
                 % (bb_discrim, HP_BIND_BUNDLE_DISCRIM, la_discrim, HP_LEARNED_LINEAR_DISCRIM,
                     HP_BEAT_NO_HUB_RATIO, no_hub_raw_discrim)) + summary,
                detail)

    if all_hf:
        return ("HARD_FAIL",
                ("HUB_SPOKE_CROSS_ENCODER HARD_FAIL: ALL %d arms discrim <= %.1f including "
                 "LEARNED_LINEAR_ALIGN (=%.2f). Encoder feature spaces are fundamentally "
                 "incompatible even with alignment training at this V/SGD-budget. "
                 "Hub-mechanism null at word scope; do NOT extrapolate to other spokes. "
                 % (len(arms), HF_DISCRIM_CEILING, la_discrim)) + summary,
                detail)

    return ("MIDDLE_BAND",
            ("HUB_SPOKE_CROSS_ENCODER MIDDLE_BAND: partial; some hub-mechanism produces "
             "above-floor alignment but not full dual-HP. BIND_BUNDLE=%.2f LEARNED=%.2f "
             "NO_HUB_RAW=%.2f NO_HUB_PROJECT=%.2f. Route to follow-up for V/N_DIM/SGD-budget "
             "sweep before chain-grade. " % (
                 bb_discrim, la_discrim, no_hub_raw_discrim, no_hub_proj_discrim)) + summary,
            detail)


# ============================================================================
# Metrics write
# ============================================================================

def get_output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    p = REPO / "data" / ("exp_" + name)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_metrics(out_dir: Path, metrics: Dict, units: List[Dict]) -> None:
    import json
    fn = out_dir / "metrics.json"
    body = dict(metrics)
    body["per_unit"] = units
    with open(fn, "w", encoding="utf-8") as fh:
        json.dump(body, fh, indent=2)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: List[Optional[Path]] = [None]
_T0_REF: List[Optional[float]] = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, [str(s) for s in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_hub_spoke_cross_encoder_alignment_smoke_v1",
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: bipolar HV
    v = _bipolar_hv(42, 64)
    assert v.shape == (64,), "T1 shape"
    assert set(np.unique(v).tolist()).issubset({-1.0, 1.0}), "T1 not bipolar"

    # T2: sign_normalize
    x = np.array([-2.0, 0.0, 3.5], dtype=np.float32)
    s = _sign_normalize(x)
    assert s.tolist() == [-1.0, 1.0, 1.0], "T2 sign_normalize: %s" % s

    # T3: bind/unbind self-inverse
    a = _bipolar_hv(1, 128)
    b = _bipolar_hv(2, 128)
    c = bind_bipolar(a, b)
    r = unbind_bipolar(c, b)
    assert np.allclose(r, a), "T3 unbind not self-inverse"

    # T4: spoke_tag determinism + different per spoke
    t1 = _spoke_tag("w2v", 0, 256)
    t1b = _spoke_tag("w2v", 0, 256)
    t2 = _spoke_tag("glove", 0, 256)
    assert np.allclose(t1, t1b), "T4 tag not deterministic"
    assert not np.allclose(t1, t2), "T4 tag collides across spokes"

    # T5: Gaussian projection determinism + JL scale
    P1 = _gaussian_projection(300, 64, seed=7, salt=0)
    P2 = _gaussian_projection(300, 64, seed=7, salt=0)
    assert np.allclose(P1, P2), "T5 projection not deterministic"
    P3 = _gaussian_projection(300, 64, seed=7, salt=1)
    assert not np.allclose(P1, P3), "T5 salts collide"
    std_P = float(P1.std())
    assert 0.04 < std_P < 0.08, "T5 JL std out of range: %.4f" % std_P

    # T6: cross_encoder_alignment_discrim sanity -- identical hub across spokes -> high discrim
    V_test = 16
    E = np.random.default_rng(0).standard_normal((V_test, 32)).astype(np.float32)
    En = _l2_normalize(E)
    hub_same = {"w2v": En.copy(), "glove": En.copy(), "ft": En.copy()}
    d_same = cross_encoder_alignment_discrim(hub_same)
    assert d_same["same_word_align_mean"] > 0.99, "T6 same-word align not ~1: %s" % d_same
    assert d_same["discrimination"] > 10.0, "T6 identical hub low discrim: %s" % d_same

    # T7: cross_encoder discrim sanity -- random independent hubs -> discrim near 1
    rng = np.random.default_rng(1)
    hub_rand = {sp: _l2_normalize(rng.standard_normal((V_test, 32)).astype(np.float32))
                for sp in SPOKES}
    d_rand = cross_encoder_alignment_discrim(hub_rand)
    assert d_rand["discrimination"] < 5.0, "T7 random hubs discrim too high: %s" % d_rand

    # T8: arm_bind_bundle_hub on CORRELATED spoke vectors (simulate real case)
    # Build a shared "concept" vector per word, perturb per spoke; spokes should
    # share enough underlying signal for hub-bundle to recover above chance.
    V_test2 = 24
    concept = rng.standard_normal((V_test2, PRETRAIN_DIM)).astype(np.float32)
    spoke_E_corr = {}
    for k, sp in enumerate(SPOKES):
        noise = 0.3 * rng.standard_normal((V_test2, PRETRAIN_DIM)).astype(np.float32)
        spoke_E_corr[sp] = _l2_normalize(concept + noise)
    hubs = arm_bind_bundle_hub(spoke_E_corr, seed=0)
    d_bb = cross_encoder_alignment_discrim(hubs)
    # With correlated spokes, bind_bundle readouts share underlying hub geometry
    # so same-word cross-spoke cosine should exceed diff-word; sep > 0 required.
    assert d_bb["signed_separation"] > 0.0, "T8 bind_bundle no signed separation: %s" % d_bb
    assert d_bb["discrimination"] > 1.0, "T8 bind_bundle below baseline: %s" % d_bb

    # T9: arm_no_hub_raw on the SAME correlated spokes should also show some
    # discrimination (because per-spoke projections preserve some shared
    # structure even with independent JL), but BIND_BUNDLE should be HIGHER.
    hubs_raw = arm_no_hub_raw(spoke_E_corr, seed=0)
    d_raw = cross_encoder_alignment_discrim(hubs_raw)
    # Independent random projections of correlated 300d preserve some shared
    # structure post-JL but with much weaker discrimination than bind-bundle.
    assert d_raw["discrimination"] < d_bb["discrimination"], (
        "T9 no_hub_raw discrim >= bind_bundle: raw=%s bb=%s" % (d_raw, d_bb))

    # T10: verdict-shape harness
    def _mk_unit(disc_by_arm: Dict[str, float], seed: int = 0) -> Dict:
        by_arm = {}
        for a in ARMS:
            by_arm[a] = {
                "same_word_align_mean": 0.5, "diff_word_align_mean": 0.1,
                "discrimination": float(disc_by_arm[a]),
                "signed_separation": 0.4,  # positive same > diff, passes HP guard
                "n_same_pairs": 100, "n_diff_pairs": 9900, "wall_s": 0.0,
            }
        return {"seed": seed, "by_arm": by_arm,
                "sanity_identical_spokes": {a: 50.0 for a in ARMS},
                "N_DIM": 4096, "PRETRAIN_DIM": 300, "vocab_size": 200,
                "in_vocab_pool_size": 250, "sgd_epochs": 200,
                "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.0}

    # T10a: HARD_PASS path
    u_hp = [_mk_unit({"ARM_NO_HUB_RAW": 1.05, "ARM_NO_HUB_PROJECT": 1.10,
                       "ARM_BIND_BUNDLE_HUB": 3.5, "ARM_LEARNED_LINEAR_ALIGN": 6.0})]
    v, _, _ = compute_verdict(u_hp)
    assert v == "HARD_PASS", "T10a expected HARD_PASS got %s" % v

    # T10b: HARD_FAIL path
    u_hf = [_mk_unit({"ARM_NO_HUB_RAW": 1.0, "ARM_NO_HUB_PROJECT": 1.1,
                       "ARM_BIND_BUNDLE_HUB": 1.2, "ARM_LEARNED_LINEAR_ALIGN": 1.3})]
    v, _, _ = compute_verdict(u_hf)
    assert v == "HARD_FAIL", "T10b expected HARD_FAIL got %s" % v

    # T10c: MIDDLE_BAND path
    u_mb = [_mk_unit({"ARM_NO_HUB_RAW": 1.0, "ARM_NO_HUB_PROJECT": 1.1,
                       "ARM_BIND_BUNDLE_HUB": 2.5, "ARM_LEARNED_LINEAR_ALIGN": 4.0})]
    v, _, _ = compute_verdict(u_mb)
    assert v == "MIDDLE_BAND", "T10c expected MIDDLE_BAND got %s" % v

    print("[selftest] OK -- all primitives + verdict-shape T1-T10 pass")


# ============================================================================
# Main
# ============================================================================

def _signal_handler(signum, frame):
    sys.stderr.write("\n[signal] received signum=%d; atexit will synthesize partials\n" % signum)
    sys.stderr.flush()
    sys.exit(143)


def main() -> int:
    import json
    import signal as _signal

    # Self-test mode: write minimal valid metrics.json + verdict and exit
    if _ARGS.self_test:
        _selftest()
        # also write a stub metrics.json so the gate accepts --self-test
        out_dir = get_output_dir()
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "SELFTEST_OK",
            "verdict_msg": "selftest passed all unit checks T1-T10",
            "elapsed_s": 0.0,
            "summary": "selftest OK",
            "run_mode": "smoke",
            "n_seeds": 0,
            "_selftest_only": True,
        }
        with open(out_dir / "metrics.json", "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2)
        return 0

    _T0_REF[0] = time.time()
    out_dir = get_output_dir()
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        _signal.signal(_signal.SIGTERM, _signal_handler)
    except Exception:
        pass

    print("[%s] starting run; mode=%s seeds=%s out=%s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, out_dir), flush=True)

    # Resume from per-seed checkpoints
    run_cfg = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_cfg)
    print("[ckpt] %d/%d seeds already done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for sd in remaining:
        result = run_unit(sd)
        # Stamp body with N, run_mode for PROT-021 contamination guard
        result["N"] = N_DIM
        write_partial_key(out_dir, sd, result)

    # Aggregate
    partials = aggregate_partials(out_dir, [str(s) for s in SEEDS], run_config=run_cfg)
    units = list(partials.values())
    if not units:
        print("[ERROR] no partials aggregated", flush=True)
        return 2

    verdict, msg, detail = compute_verdict(units)
    elapsed = time.time() - _T0_REF[0]
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": round(elapsed, 2),
        "summary": msg.split(" | ")[0] if " | " in msg else msg[:200],
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "n_seeds": len(units),
        "n_seeds_expected": len(SEEDS),
        "detail": detail,
        "metrics_source": "hub_spoke_cross_encoder_alignment_smoke_v1",
        "substrate_only_decode_gate": "TRUE",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True

    print("\n[%s] %s" % (ANCHOR_NAME, verdict))
    print("[%s] %s" % (ANCHOR_NAME, msg))
    print("[%s] elapsed=%.1fs out=%s" % (ANCHOR_NAME, elapsed, out_dir / "metrics.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
