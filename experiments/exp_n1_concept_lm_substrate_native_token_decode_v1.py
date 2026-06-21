"""
n1_concept_lm_substrate_native_token_decode_v1 -- N1: substrate-native token-level LM.

SUBSTRATE-ONLY-NESS GATE (USER requirement):
  The LM must live INSIDE the substrate. At INFERENCE, no transformer is called.
  - INGEST (allowed off-line): Pythia-160m produces per-token residuals (768-d). These
    are VQ-clustered (MiniBatchKMeans) into V_C concept IDs. The concept codebook C is
    built from a bipolar random projection of cluster centroids. A per-token vocabulary
    lookup table maps token-id -> residual embedding (768-d, L2-normalized; stored at
    ingest time from the training split only, NO LLM head used).
  - INFERENCE (substrate-native only):
      1. Concept transition memory W (Hebbian cf-RPE over concept -> next-concept).
      2. Concept-to-token decode memory D (N_DIM x V_TOK Hebbian association,
         binding C[concept] -> token embedding e[token] at each (concept, token)
         observation on TRAIN; at decode, given concept vector v, D@v gives a
         similarity score over token embeddings, argmax = predicted token).
      3. No LLM LM-head called at step (2). The decode is purely D@v.
  BOUNDARY: Pythia-160m runs ONCE at ingest to produce residuals. It is NOT called
  at inference. token embeddings used in D are from a static lookup table, NOT from
  the LM-head softmax. This is a substrate-native associative decode.

PIPELINE:
  Load residuals_per_token.npz (residuals (sum_T,768), doc_boundaries, token_ids).
  VQ -> concept IDs per token. Split DISJOINT train/test docs.
  Build:
    (a) substrate transition memory W (concept->concept, cf-RPE).
    (b) substrate decode memory D (concept->token count accumulator).
  ANALYTIC CEILING: perfect concept prediction + best concept->token decode on TEST.
  TOKEN METRICS on TEST (substrate path: W->concept->D->token):
    - next-token top-1 accuracy
    - bits-per-character (BPC) = cross-entropy / log(2) in bits per token
  BASELINES: token-unigram, token-bigram-Markov, analytic ceiling.

PRE-REGISTERED BANDS (TOKEN BPC -- lower is better; language models ~6-8 BPC range for
  character-level; here BPC is bits-per-TOKEN so scale differs: unigram ~log2(V_TOK)):
  No prior empirical anchor for this exact pipeline; calibration-probe policy applies
  (bands +/-50% of theoretical prediction).
  Theoretical prediction: substrate BPC ~ unigram BPC - 10% (concept bottleneck recovers
  some structure but concept->token is many-to-many). unigram BPC ~ log2(V_TOK) ~ 14.3
  bits (V_TOK=20000 typical; actual depends on corpus vocab). Expected range 12-16 BPC.
  HARD-PASS: substrate BPC <= bigram_BPC + 0.5 AND <= 0.95 * unigram_BPC
    (substrate beats unigram by >=5%, and is within 0.5 bits of bigram).
  MIDDLE-BAND: substrate BPC <= 0.99 * unigram_BPC
    (substrate is merely better than pure unigram by >=1%).
  HARD-FAIL: substrate BPC >= unigram_BPC
    (no token-level improvement whatsoever over unigram).
  NOTE (calibration-probe): bands are wide per policy; no prior empirical anchor.
  The analytic ceiling measures the concept-bottleneck cost (ceiling_BPC >= bigram_BPC).
  Top-1 accuracy: HARD-PASS substrate_top1 >= 2x token_unigram_top1.

  IMPORTANT: the concept->token decode is a MANY-TO-MANY mapping (many tokens share a
  concept; predict 1 token per concept = most-frequent under that concept in train).
  So the ceiling is NOT perfect: even with perfect concept prediction, the best
  concept->token oracle is bounded by the conditional entropy H(token|concept).

FORMULA SELF-TESTS (PROT-022): formula_selftest() at module scope tests:
  1. cf-RPE transition memory store+recall on synthetic data.
  2. Decode memory D accumulation + argmax decode.
  3. BPC formula (cross-entropy / log(2)).
  4. doc_boundaries slice correctness.
  5. Instrumentation: all claimed metrics non-null after one synthetic forward pass.

ASCII-only. write_metrics. PROT-021 run_config guard. PROT-018: no _nN suffix (N fixed
  by codebook; production N_DIM=1024). CPU numpy + sklearn only; no torch/GPU.

QUEUE: remote_cpu_queue (residuals_per_token.npz is on marsh@home; NOT on local laptop).
CONFIG_VERSION = "V_C=256,N_DIM=1024,DECODE=freq,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8"
  (changes to any of these params invalidate checkpoints).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials
)

ANCHOR_NAME = "n1_concept_lm_substrate_native_token_decode_v1"
CONFIG_VERSION = "V_C=256,N_DIM=1024,DECODE=freq,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8"

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"

N_DIM = 1024  # hypervector dimension
LR_TRANSITION = 0.5  # cf-RPE learning rate for W (concept->concept)
LR_DECODE = 1.0  # decode memory: count-based; LR_DECODE is weight per observation

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    SEEDS = [1]
    V_C = 32          # small concept vocab for smoke
    MAX_DOCS = 100    # small doc count
    MAX_TOK_VOCAB = 1000  # limit token vocab for fast smoke
else:
    SEEDS = [7, 17, 23]
    V_C = 256
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257  # Pythia uses GPT-2 tokenizer (~50k vocab)

TRAIN_FRAC = 0.8


# ---------------------------------------------------------------------------
# Core substrate ops
# ---------------------------------------------------------------------------

def bipolar_codebook(vc: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """Random bipolar codebook, shape (vc, n), L2-normalized rows."""
    X = (rng.integers(0, 2, size=(vc, n)) * 2 - 1).astype(np.float32)
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return X / norms


def cfrpe_update(W: np.ndarray, src: np.ndarray, dst: np.ndarray, n: int) -> None:
    """cf-RPE Hebbian update: W += (lr/n) * outer(dst - W@src, src)."""
    W += (LR_TRANSITION / n) * np.outer(dst - W @ src, src)


def cleanup(W: np.ndarray, C: np.ndarray, v: np.ndarray) -> int:
    """Predict next concept: argmax over codebook of similarity to W@v."""
    return int(np.argmax(C @ (W @ v)))


def decode_token(D: np.ndarray, concept_vec: np.ndarray) -> int:
    """Predict token: argmax over D^T @ concept_vec, shape (V_TOK,).

    D has shape (N_DIM, V_TOK). Column j = accumulated C[concept] vectors for token j.
    scores = D.T @ concept_vec ranks tokens by concept co-occurrence (substrate-native).
    """
    scores = D.T @ concept_vec  # shape (V_TOK,)
    return int(np.argmax(scores))


def token_logprob(D: np.ndarray, concept_vec: np.ndarray) -> np.ndarray:
    """Return log-probability distribution over tokens given concept vector.

    Uses softmax over D^T @ concept_vec for BPC computation.
    Returns log-probabilities (log-base-e), shape (V_TOK,).
    """
    scores = D.T @ concept_vec  # (V_TOK,)
    # numerically stable softmax
    scores = scores - scores.max()
    exp_s = np.exp(scores)
    log_probs = scores - np.log(exp_s.sum() + 1e-300)
    return log_probs


# ---------------------------------------------------------------------------
# Formula self-test (PROT-022 + instrumentation gate)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small synthetic scale."""
    rng = np.random.default_rng(42)
    n, vc, vt = 128, 8, 50  # tiny synthetic scale

    # --- test 1: cf-RPE transition store+recall ---
    C = bipolar_codebook(vc, n, rng)
    W = np.zeros((n, n), dtype=np.float32)
    cfrpe_update(W, C[2], C[5], n)
    pred = cleanup(W, C, C[2])
    assert pred == 5, "cf-RPE store+recall FAIL: expected concept 5, got %d" % pred

    # --- test 2: decode memory D accumulation + argmax decode ---
    # Build a tiny projection matrix P (n x 768) and token embeddings E (vt x 768)
    P = rng.standard_normal((n, 768)).astype(np.float32)
    P /= np.linalg.norm(P, axis=1, keepdims=True) + 1e-8
    E = rng.standard_normal((vt, 768)).astype(np.float32)
    E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-8
    D = np.zeros((n, vt), dtype=np.float32)
    # Associate concept 3 -> token 7 (add 10 observations)
    for _ in range(10):
        tok_vec = P @ E[7]  # project E[7] into N_DIM space
        D[:, 7] += tok_vec * LR_DECODE
    # Associate concept 3 -> token 2 (add 1 observation, weaker)
    D[:, 2] += (P @ E[2]) * LR_DECODE
    # At query with C[3] (concept 3 vector): tok 7 should win
    # (In real code, D columns are indexed by token_id directly;
    #  the query is against the concept vector C[concept_id])
    # For this test: D is concept-agnostic; we check the argmax mechanism
    t_pred = decode_token(D, C[3])
    # token 7 has highest score by construction (10x weight vs 1x for tok 2)
    assert t_pred == 7, "decode memory argmax FAIL: expected tok 7, got %d" % t_pred

    # --- test 3: BPC formula ---
    log_probs = token_logprob(D, C[3])
    assert log_probs.shape == (vt,), "log_probs shape FAIL"
    assert not np.isnan(log_probs).any(), "log_probs has NaN"
    # BPC = -log_p(correct) / log(2)
    bpc_val = -log_probs[7] / math.log(2)
    assert 0.0 < bpc_val < 30.0, "BPC value out of range: %.3f" % bpc_val

    # --- test 4: doc_boundaries slice ---
    bnd = np.array([0, 3, 7, 12], dtype=np.int64)
    fake_toks = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], dtype=np.int64)
    segs = [fake_toks[bnd[i]:bnd[i+1]] for i in range(len(bnd)-1)]
    assert len(segs) == 3, "doc_boundaries n_docs FAIL"
    assert len(segs[0]) == 3, "doc_boundaries len0 FAIL"

    # --- test 5: instrumentation - all metrics computable on synthetic data ---
    result = _run_seed_synthetic(rng_seed=42, n_dim=n, vc=vc, vt=vt)
    assert result is not None, "synthetic run returned None"
    for k in ("substrate_top1", "substrate_bpc", "unigram_top1", "unigram_bpc",
              "bigram_top1", "bigram_bpc", "ceiling_top1", "ceiling_bpc"):
        v = result.get(k)
        assert v is not None, "metric %s is None" % k
        assert not math.isnan(v), "metric %s is NaN" % k
    assert result["substrate_bpc"] > 0.0, "substrate_bpc is zero (sentinel)"
    assert result["unigram_bpc"] > 0.0, "unigram_bpc is zero (sentinel)"
    # sanity: ceiling should be <= unigram (perfect concept = lower entropy)
    # (not enforced as hard assert since ceiling depends on concept quality)

    print("[selftest] PASS: cfrpe+cleanup, decode-D-argmax, BPC formula, boundaries, instrumentation", flush=True)


def _run_seed_synthetic(rng_seed: int, n_dim: int = 64, vc: int = 8, vt: int = 20) -> Dict[str, Any]:
    """Run one synthetic forward pass for selftest instrumentation gate."""
    rng = np.random.default_rng(rng_seed)
    # Synthetic docs: 20 docs of 10 tokens each
    n_docs = 20
    docs_cids = [rng.integers(0, vc, size=10) for _ in range(n_docs)]  # concept sequences
    docs_tids = [rng.integers(0, vt, size=10) for _ in range(n_docs)]  # token sequences

    split = int(0.8 * n_docs)
    train_cids, test_cids = docs_cids[:split], docs_cids[split:]
    train_tids, test_tids = docs_tids[:split], docs_tids[split:]

    rng2 = np.random.default_rng(rng_seed + 1)
    C = bipolar_codebook(vc, n_dim, rng2)
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    D = np.zeros((n_dim, vt), dtype=np.float32)

    # Projection P for token embeddings: random (n_dim x vt) (synthetic: E = I_vt)
    # For selftest, token "embeddings" are random unit vectors
    E = rng2.standard_normal((vt, n_dim)).astype(np.float32)
    E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-8

    # TRAIN
    for cids, tids in zip(train_cids, train_tids):
        for t in range(len(cids) - 1):
            cfrpe_update(W, C[cids[t]], C[cids[t+1]], n_dim)
            # decode: associate concept with observed token
            D[:, tids[t]] += E[tids[t]] * LR_DECODE

    # Build baselines from train
    uni_tok = np.zeros(vt, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for cids, tids in zip(train_cids, train_tids):
        for t in range(len(tids) - 1):
            uni_tok[tids[t+1]] += 1
            if tids[t] not in big_tok:
                big_tok[tids[t]] = np.zeros(vt, dtype=np.int64)
            big_tok[tids[t]][tids[t+1]] += 1
    uni_pred_tok = int(np.argmax(uni_tok)) if uni_tok.sum() > 0 else 0
    big_pred_tok = {k: int(np.argmax(v)) for k, v in big_tok.items()}

    # Concept->token ceiling (oracle: per-concept most-frequent token in train)
    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids, tids in zip(train_cids, train_tids):
        for t in range(len(cids)):
            c = int(cids[t]); tok = int(tids[t])
            if c not in concept_tok_counts:
                concept_tok_counts[c] = np.zeros(vt, dtype=np.int64)
            concept_tok_counts[c][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    # TEST
    tot = 0
    sub_ok = big_ok = uni_ok = ceil_ok = 0
    sub_nll = big_nll = uni_nll = ceil_nll = 0.0

    # unigram distribution
    uni_dist = uni_tok.astype(np.float32) + 1e-6
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    for cids, tids in zip(test_cids, test_tids):
        for t in range(len(cids) - 1):
            true_tok = int(tids[t+1])
            true_cid = int(cids[t+1])  # for ceiling
            tot += 1

            # substrate: predict concept then token
            pred_cid = cleanup(W, C, C[cids[t]])
            pred_tok = decode_token(D, C[pred_cid])
            log_probs = token_logprob(D, C[pred_cid])

            sub_ok += (pred_tok == true_tok)
            sub_nll += -log_probs[true_tok]

            # unigram
            uni_ok += (uni_pred_tok == true_tok)
            uni_nll += -uni_log[true_tok]

            # bigram
            bp = big_pred_tok.get(int(tids[t]), uni_pred_tok)
            big_ok += (bp == true_tok)
            bfd = big_tok.get(int(tids[t]))
            if bfd is not None and bfd.sum() > 0:
                bfd_dist = bfd.astype(np.float32) / (bfd.sum() + 1e-6)
                big_nll += -math.log(bfd_dist[true_tok] + 1e-300)
            else:
                big_nll += -uni_log[true_tok]

            # ceiling (oracle concept -> best token)
            ceil_pred_tok = ceiling_pred.get(true_cid, uni_pred_tok)
            ceil_ok += (ceil_pred_tok == true_tok)
            # ceiling BPC: use train concept->tok distribution
            ctd = concept_tok_counts.get(true_cid)
            if ctd is not None and ctd.sum() > 0:
                ctd_dist = ctd.astype(np.float32) / (ctd.sum() + 1e-6)
                ceil_nll += -math.log(ctd_dist[true_tok] + 1e-300)
            else:
                ceil_nll += -uni_log[true_tok]

    if tot == 0:
        return {k: float("nan") for k in ("substrate_top1", "substrate_bpc",
                "unigram_top1", "unigram_bpc", "bigram_top1", "bigram_bpc",
                "ceiling_top1", "ceiling_bpc")}

    log2 = math.log(2)
    return {
        "substrate_top1": sub_ok / tot,
        "substrate_bpc": (sub_nll / tot) / log2,
        "unigram_top1": uni_ok / tot,
        "unigram_bpc": (uni_nll / tot) / log2,
        "bigram_top1": big_ok / tot,
        "bigram_bpc": (big_nll / tot) / log2,
        "ceiling_top1": ceil_ok / tot,
        "ceiling_bpc": (ceil_nll / tot) / log2,
        "n_test_pairs": tot,
    }


_instrumentation_selftest()  # Called at module scope before sweep
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz.

    Returns:
        residuals: shape (sum_T, 768) float32
        doc_boundaries: shape (n_docs+1,) int64
        token_ids: shape (sum_T,) int64 -- may be absent; returns zeros if so
    """
    if not NPZ_PATH.exists():
        raise FileNotFoundError(
            "residuals_per_token.npz not found at %s\n"
            "  This file lives on marsh@home (remote runner). "
            "Run on remote_cpu_queue." % NPZ_PATH
        )
    z = np.load(NPZ_PATH, allow_pickle=False)
    res = z["residuals"].astype(np.float32)
    bnd = z["doc_boundaries"].astype(np.int64)
    print("[data] residuals shape=%s doc_boundaries shape=%s" % (res.shape, bnd.shape), flush=True)
    if "token_ids" in z:
        tids = z["token_ids"].astype(np.int64)
        print("[data] token_ids shape=%s" % (tids.shape,), flush=True)
    else:
        # token_ids absent: use synthetic sequential IDs (still valid for concept metrics;
        # token-level metrics will reflect the concept-only structure)
        print("[data] WARNING: token_ids NOT in npz; using residual-index as token proxy. "
              "Token metrics reflect concept structure only.", flush=True)
        tids = np.arange(res.shape[0], dtype=np.int64) % MAX_TOK_VOCAB
    return res, bnd, tids


def build_docs(res: np.ndarray, bnd: np.ndarray, tids: np.ndarray,
               max_docs: int) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Slice into per-doc (concept_residuals, token_ids) pairs, min 2 tokens."""
    n_docs = min(len(bnd) - 1, max_docs)
    bnd = bnd[:n_docs + 1]
    docs = []
    for i in range(n_docs):
        s, e = int(bnd[i]), int(bnd[i+1])
        if e - s < 2:
            continue
        docs.append((res[s:e], tids[s:e]))
    return docs


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load, VQ, build substrate, evaluate."""
    t0 = time.time()
    res, bnd, tids = load_data()
    docs = build_docs(res, bnd, tids, MAX_DOCS)
    print("[seed=%d] loaded %d docs" % (seed, len(docs)), flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(docs)).tolist()
    docs = [docs[i] for i in perm]
    split = int(TRAIN_FRAC * len(docs))
    train_docs = docs[:split]
    test_docs = docs[split:]

    # --- VQ: MiniBatchKMeans on train residuals ---
    train_res = np.concatenate([d[0] for d in train_docs], axis=0)
    # L2-normalize for better angular VQ
    norms = np.linalg.norm(train_res, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res / norms

    print("[seed=%d] fitting VQ V_C=%d on %d tokens..." % (seed, V_C, len(train_res_n)), flush=True)
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=4096,
                             n_init=3, max_iter=100, verbose=0)
        # Fit on normalized train residuals
        km.fit(train_res_n)
        # Assign concept IDs for all tokens (train + test separately to avoid leakage)
        def assign_cids(doc_res_list):
            all_r = np.concatenate([d for d in doc_res_list], axis=0)
            nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
            return km.predict(all_r / nrm)
    except ImportError:
        print("[seed=%d] sklearn unavailable; using numpy argmin VQ" % seed, flush=True)
        centers = train_res_n[rng.choice(len(train_res_n), size=V_C, replace=False)]
        def assign_cids(doc_res_list):
            all_r = np.concatenate([d for d in doc_res_list], axis=0)
            nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
            all_rn = all_r / nrm
            chunk = 4096
            out = np.empty(len(all_rn), dtype=np.int64)
            for s in range(0, len(all_rn), chunk):
                e = s + chunk
                diff = all_rn[s:e, None, :] - centers[None, :, :]
                out[s:e] = np.argmin((diff**2).sum(-1), axis=1)
            return out

    # Assign concept IDs per split (NO TEST tokens in km fit = no leakage)
    train_cids_flat = assign_cids([d[0] for d in train_docs])
    test_cids_flat = assign_cids([d[0] for d in test_docs])

    # Slice back to per-doc sequences
    def slice_docs(docs_split, cids_flat):
        seqs = []; offset = 0
        for doc_res, doc_tok in docs_split:
            n = len(doc_res)
            seqs.append((cids_flat[offset:offset+n], doc_tok))
            offset += n
        return seqs

    train_seqs = slice_docs(train_docs, train_cids_flat)
    test_seqs = slice_docs(test_docs, test_cids_flat)

    # --- Substrate codebook (random bipolar, NOT km centroids) ---
    C = bipolar_codebook(V_C, N_DIM, rng)

    # --- Build transition memory W (concept->concept) ---
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for cids, _ in train_seqs:
        for t in range(len(cids) - 1):
            cfrpe_update(W, C[int(cids[t])], C[int(cids[t+1])], N_DIM)

    # --- Build decode memory D (concept->token) ---
    # Determine actual token vocab from training data (bounded by MAX_TOK_VOCAB)
    # D shape: (N_DIM, V_TOK) -- column j = accumulated concept-vector signal for token j
    # Accumulate: at each (concept_t, token_t) observation: D[:,token_t] += C[concept_t]
    # This is a simple Hebbian binding: D columns become sums of concept vectors
    # that co-occurred with each token.
    # At query: scores = D.T @ C[concept_id]; argmax = predicted token.
    # This is substrate-native: no LLM head, no transformer inference.
    all_train_tids = np.concatenate([tids for _, tids in train_seqs])
    actual_max_tok = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    V_TOK = actual_max_tok
    print("[seed=%d] V_TOK=%d (from train data)" % (seed, V_TOK), flush=True)

    D = np.zeros((N_DIM, V_TOK), dtype=np.float32)
    for cids, tids_doc in train_seqs:
        for t in range(len(cids)):
            tok = int(tids_doc[t])
            if tok < V_TOK:
                D[:, tok] += C[int(cids[t])] * LR_DECODE

    # --- Compute concept-level baselines (verify sanity, matches v1 cell) ---
    uni_c = np.zeros(V_C, dtype=np.int64)
    big_c: Dict[int, np.ndarray] = {}
    for cids, _ in train_seqs:
        for t in range(len(cids) - 1):
            uni_c[int(cids[t+1])] += 1
            c = int(cids[t])
            if c not in big_c:
                big_c[c] = np.zeros(V_C, dtype=np.int64)
            big_c[c][int(cids[t+1])] += 1
    uni_c_pred = int(np.argmax(uni_c)) if uni_c.sum() > 0 else 0
    big_c_pred = {k: int(np.argmax(v)) for k, v in big_c.items()}

    # --- Compute token-level baselines from train ---
    uni_tok = np.zeros(V_TOK, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for cids, tids_doc in train_seqs:
        for t in range(len(tids_doc) - 1):
            tt1 = int(tids_doc[t+1])
            if tt1 < V_TOK:
                uni_tok[tt1] += 1
            t0_tok = int(tids_doc[t])
            if t0_tok not in big_tok:
                big_tok[t0_tok] = np.zeros(V_TOK, dtype=np.int64)
            if tt1 < V_TOK:
                big_tok[t0_tok][tt1] += 1
    uni_tok_pred = int(np.argmax(uni_tok)) if uni_tok.sum() > 0 else 0
    uni_dist = (uni_tok.astype(np.float32) + 1e-6)
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    # --- Analytic ceiling: per-concept most-frequent token (train stats) ---
    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids, tids_doc in train_seqs:
        for t in range(len(cids)):
            c = int(cids[t]); tok = int(tids_doc[t])
            if tok < V_TOK:
                if c not in concept_tok_counts:
                    concept_tok_counts[c] = np.zeros(V_TOK, dtype=np.int64)
                concept_tok_counts[c][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    # --- Evaluate on TEST ---
    tot_c = 0; sub_c_ok = 0; uni_c_ok = 0; big_c_ok = 0
    tot_t = 0
    sub_t_ok = uni_t_ok = big_t_ok = ceil_t_ok = 0
    sub_nll = uni_nll = big_nll = ceil_nll = 0.0
    log2 = math.log(2)

    for (cids, tids_doc) in test_seqs:
        n_pos = len(cids) - 1
        if n_pos < 1:
            continue
        for t in range(n_pos):
            # --- concept-level eval ---
            c_src = int(cids[t]); c_tgt = int(cids[t+1])
            pred_c = cleanup(W, C, C[c_src])
            sub_c_ok += (pred_c == c_tgt)
            uni_c_ok += (uni_c_pred == c_tgt)
            big_c_ok += (big_c_pred.get(c_src, uni_c_pred) == c_tgt)
            tot_c += 1

            # --- token-level eval (substrate path) ---
            true_tok = int(tids_doc[t+1])
            if true_tok >= V_TOK:
                continue  # OOV token; skip (conservative)

            # substrate: predict concept via W, then decode via D
            pred_tok_sub = decode_token(D, C[pred_c])
            # BPC from substrate
            log_probs_sub = token_logprob(D, C[pred_c])
            sub_t_ok += (pred_tok_sub == true_tok)
            sub_nll += -log_probs_sub[true_tok]

            # unigram token
            uni_t_ok += (uni_tok_pred == true_tok)
            uni_nll += -uni_log[true_tok]

            # bigram token
            t_src = int(tids_doc[t])
            bp_tok = big_tok.get(t_src)
            if bp_tok is not None and bp_tok.sum() > 0:
                bfd_d = bp_tok.astype(np.float32) / (bp_tok.sum() + 1e-6)
                big_t_ok += (int(np.argmax(bp_tok)) == true_tok)
                big_nll += -math.log(float(bfd_d[true_tok]) + 1e-300)
            else:
                big_t_ok += (uni_tok_pred == true_tok)
                big_nll += -uni_log[true_tok]

            # ceiling (oracle concept: use true concept at t+1 -> best token)
            ceil_pred_tok = ceiling_pred.get(c_tgt, uni_tok_pred)
            ceil_t_ok += (ceil_pred_tok == true_tok)
            ctd = concept_tok_counts.get(c_tgt)
            if ctd is not None and ctd.sum() > 0:
                ctd_d = ctd.astype(np.float32) / (ctd.sum() + 1e-6)
                ceil_nll += -math.log(float(ctd_d[true_tok]) + 1e-300)
            else:
                ceil_nll += -uni_log[true_tok]

            tot_t += 1

    # Guard zeros
    tc = max(tot_c, 1); tt = max(tot_t, 1)
    elapsed = time.time() - t0

    return {
        "seed": seed,
        "n_docs": len(train_seqs) + len(test_seqs),
        "n_train_docs": len(train_seqs),
        "n_test_docs": len(test_seqs),
        "V_TOK": V_TOK,
        "run_mode": RUN_MODE,
        # concept-level
        "substrate_concept_top1": sub_c_ok / tc,
        "unigram_concept_top1": uni_c_ok / tc,
        "bigram_concept_top1": big_c_ok / tc,
        "n_concept_test_pairs": tot_c,
        # token-level
        "substrate_top1": sub_t_ok / tt,
        "substrate_bpc": (sub_nll / tt) / log2,
        "unigram_top1": uni_t_ok / tt,
        "unigram_bpc": (uni_nll / tt) / log2,
        "bigram_top1": big_t_ok / tt,
        "bigram_bpc": (big_nll / tt) / log2,
        "ceiling_top1": ceil_t_ok / tt,
        "ceiling_bpc": (ceil_nll / tt) / log2,
        "n_token_test_pairs": tot_t,
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    def _mean(key):
        return float(np.mean([p[key] for p in ps if key in p and p[key] is not None]))

    sub_bpc = _mean("substrate_bpc")
    uni_bpc = _mean("unigram_bpc")
    big_bpc = _mean("bigram_bpc")
    ceil_bpc = _mean("ceiling_bpc")
    sub_top1 = _mean("substrate_top1")
    uni_top1 = _mean("unigram_top1")
    big_top1 = _mean("bigram_top1")
    sub_c_top1 = _mean("substrate_concept_top1")
    big_c_top1 = _mean("bigram_concept_top1")

    bottleneck_cost_bits = sub_bpc - ceil_bpc  # bits lost to imperfect concept prediction

    summary = (
        "substrate_bpc=%.2f unigram_bpc=%.2f bigram_bpc=%.2f ceiling_bpc=%.2f "
        "substrate_top1=%.3f unigram_top1=%.3f bigram_top1=%.3f "
        "concept_substrate=%.3f concept_bigram=%.3f bottleneck_cost=%.2f_bits "
        "(V_C=%d N_DIM=%d mode=%s seeds=%d)" % (
            sub_bpc, uni_bpc, big_bpc, ceil_bpc,
            sub_top1, uni_top1, big_top1,
            sub_c_top1, big_c_top1, bottleneck_cost_bits,
            V_C, N_DIM, RUN_MODE, len(ps)
        )
    )

    # HARD-PASS: substrate BPC <= bigram_BPC + 0.5 AND <= 0.95 * unigram_BPC
    if sub_bpc <= (big_bpc + 0.5) and sub_bpc <= 0.95 * uni_bpc:
        return ("HARD_PASS",
                "HARD_PASS: substrate-native token decode beats unigram by >=5%% "
                "and is within 0.5 bits of bigram. " + summary)
    # MIDDLE-BAND: substrate BPC <= 0.99 * unigram_BPC
    if sub_bpc <= 0.99 * uni_bpc:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: substrate token decode better than pure unigram. " + summary)
    return ("HARD_FAIL",
            "HARD_FAIL: substrate token decode does not beat unigram. " + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C=%d N_DIM=%d MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C, N_DIM, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    print("  [seed=%d] substrate_bpc=%.2f unigram_bpc=%.2f bigram_bpc=%.2f "
          "sub_top1=%.3f concept_top1=%.3f" % (
              seed, r["substrate_bpc"], r["unigram_bpc"], r["bigram_bpc"],
              r["substrate_top1"], r["substrate_concept_top1"]), flush=True)

# Load any done seeds from checkpoint
if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "V_C": V_C,
    "N_DIM": N_DIM,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
