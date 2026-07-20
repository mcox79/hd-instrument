"""Derived structural (slot/position address) code vs hand-stipulated random code (v1).

Structural-code complement to the content-codebook test (exp_learned_codebook_generalization_gate_v1).
Tests "stipulated vs derived representation" for the STRUCTURAL / role / slot-ADDRESS code. Question:
can the substrate DERIVE its structural code from data (transition / co-occurrence statistics) and
match-or-beat the current HAND-STIPULATED (fixed-random) address code on (a) pairwise separation and
(b) bind/unbind retrieval -- OR does deriving it HURT (the VSA field consensus warns role vectors
should stay random/orthogonal for addressing)? Base-loop INDEPENDENT.

PRIOR ART (credit; learn-from / build-on, never steal):
  - Successor Representation: Dayan (1993, Neural Computation); Stachenfeld, Botvinick & Gershman
    (2017, Nat. Neurosci.). On a 1D chain the SR eigenvectors are the DCT/sinusoid basis.
  - Oja's rule / Sanger's generalized Hebbian algorithm: Oja (1982); Sanger (1989); non-negativity
    producing grid-like fields: Dordek, Soudry, Meir & Derdikman (2016, eLife).
  - Laplacian eigenmaps: Belkin & Niyogi (2003). Sign-random-projection / SimHash: Charikar (2002).
  - VSA field consensus being probed: Plate (1995, IEEE TNN); Kanerva (2009, Cognitive Computation)
    -- role vectors SHOULD be fixed/random to preserve generalization (the design risk carried).
  - REUSES the FLAT bind/unbind retrieval primitive + cleanup semantics from
    hdlab/role_slot_summarizer.py (elementwise-bipolar bind = _bipolar_bind; sign-bundle =
    _bipolar_quantize; nearest-neighbor cleanup = cleanup_argmax). ONE variable is swapped: the
    structural (address) code; everything else in the retrieval harness is held fixed. self_test()
    asserts the numpy bind/cleanup used here are bit-equivalent to the torch role_slot_summarizer
    primitives (faithful reuse, not a re-invented favorable task).

Pre-reg: preregs/2026-07-19_derived_structural_code_vs_stipulated_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise
BEFORE except Exception (no BaseException); crlb_n/a declared; baseline in band; discriminator fires
at full geometry; cardinality gate; per-unit failure-class; fixed seeds (no hash()/list(set())); all
numbers tagged. ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "exp_derived_structural_code_vs_stipulated_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- config (FULL defaults; --smoke overrides) --------------------------------
K_EIG = [2, 4, 8, 16, 32, 48, 63]   # eigenvector-count sweep (P-1=63 = near-full-rank/best shot)
ROUTES = ["derived_sr", "derived_oja"]
ARMS = ["stipulated"] + ROUTES
SEEDS = [7, 13, 19, 23, 31]
GAMMA_SR = 0.9                 # SR discount

# ---- pre-registered bands (declared BEFORE running; NOT tuned to pass) --------
RETR_DROP_TOL = 0.05           # >= this retrieval drop vs stipulated = HURTS
SEP_SIGMA_MULT = 2.0           # derived SEP within stipulated + 2*sigma = "not worse separated"
GEN_GAP_TOL = 0.05             # derived sampling gap beyond this = overfit-to-statistics
BASELINE_BAND = (0.55, 0.92)   # stipulated RETR must land here (META_RULE_AG)


# --------------------------------------------------------------------------- io
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics(output_dir, diag)


# ------------------------------------------------ bipolar primitives (REUSE math)
# Bit-equivalent to hdlab.role_slot_summarizer._bipolar_bind / cleanup_argmax /
# _bipolar_quantize (asserted in self_test). Vectorized numpy for the full run.
def bipolar_bind_np(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Elementwise bipolar bind (== _bipolar_bind: a * b). Self-inverse for bipolar b."""
    return a * b


def sign_bundle_np(x: np.ndarray) -> np.ndarray:
    """Sign-quantize a summed bundle (== _bipolar_quantize: sign, ties -> +1)."""
    q = np.sign(x)
    q[q == 0] = 1.0
    return q.astype(np.float32)


def cleanup_argmax_np(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Nearest-neighbor (max dot) cleanup (== cleanup_argmax / k_NN_lookup for bipolar).

    query: (..., N) ; codebook: (V, N). Returns argmax index per query row.
    """
    scores = query @ codebook.T
    return np.argmax(scores, axis=-1)


def bipolar_random_np(shape, rng: np.random.Generator) -> np.ndarray:
    """Random bipolar {-1,+1} (matches _bipolar_random distribution; own deterministic RNG)."""
    return np.where(rng.random(shape) < 0.5, -1.0, 1.0).astype(np.float32)


# ----------------------------------------------------- transition / co-occurrence
def analytic_chain_T(P: int) -> np.ndarray:
    """Symmetric nearest-neighbor random-walk transition on a ring of P slots.

    SR eigenvectors of this are the DCT/sinusoid basis (Stachenfeld 2017; the 1D-track case).
    """
    A = np.zeros((P, P), dtype=np.float64)
    for i in range(P):
        A[i, (i - 1) % P] = 1.0
        A[i, (i + 1) % P] = 1.0
    T = A / A.sum(axis=1, keepdims=True)
    return T


def sample_sequences(P: int, n_seq: int, seq_len: int, rng: np.random.Generator) -> np.ndarray:
    """Sample slot-visit sequences from a STRUCTURED noisy-ring Markov chain (the data).

    True chain: mostly step +1 around the ring (p_fwd), sometimes -1, rarely jump. Estimating T
    from these sequences is 'derive from data'; finite samples give a noisy T_hat.
    """
    p_fwd, p_back, p_jump = 0.70, 0.20, 0.10
    seqs = np.zeros((n_seq, seq_len), dtype=np.int64)
    for s in range(n_seq):
        cur = int(rng.integers(0, P))
        for t in range(seq_len):
            seqs[s, t] = cur
            u = rng.random()
            if u < p_fwd:
                cur = (cur + 1) % P
            elif u < p_fwd + p_back:
                cur = (cur - 1) % P
            else:
                cur = int(rng.integers(0, P))
    return seqs


def estimate_T_C(seqs: np.ndarray, P: int) -> tuple[np.ndarray, np.ndarray]:
    """Empirical transition T_hat (row-normalized adjacency counts) + symmetric co-occurrence C_hat."""
    counts = np.ones((P, P), dtype=np.float64)  # Laplace smoothing (avoid zero rows)
    for s in range(seqs.shape[0]):
        row = seqs[s]
        for t in range(1, row.shape[0]):
            counts[row[t - 1], row[t]] += 1.0
    T = counts / counts.sum(axis=1, keepdims=True)
    C = 0.5 * (counts + counts.T)  # symmetric co-occurrence
    C = C / C.sum()
    return T, C


# ------------------------------------------------------------ derivation routes
def derive_sr_embedding(T: np.ndarray, k: int) -> np.ndarray:
    """SR route: M = (I - gamma T)^-1; top-k eigenvectors of symmetrized M -> P x k embedding.

    Dayan (1993); Stachenfeld et al. (2017). Symmetrize M for a real orthonormal eigenbasis
    (the relational geometry); drop the top (near-constant / stationary) eigenvector, keep the
    next k structure-carrying eigenvectors.
    """
    P = T.shape[0]
    M = np.linalg.inv(np.eye(P) - GAMMA_SR * T)
    Ms = 0.5 * (M + M.T)
    evals, evecs = np.linalg.eigh(Ms)          # ascending
    order = np.argsort(evals)[::-1]            # descending
    evecs = evecs[:, order]
    # evecs[:,0] is the dominant (near-constant DC) mode; skip it, take next k.
    sel = evecs[:, 1:1 + k]
    return sel.astype(np.float64)


def derive_oja_embedding(C: np.ndarray, k: int, seed: int, n_iter: int = 400,
                         lr: float = 0.05, nonneg: bool = True) -> tuple[np.ndarray, float]:
    """Oja/Sanger route: iterative Hebbian top-k PCs of centered co-occurrence C (NO SVD).

    Sanger's generalized Hebbian algorithm (Sanger 1989) with a non-negativity (ReLU) constraint
    per Dordek et al. (2016). Returns (P x k embedding, convergence_delta). Genuinely iterative
    Hebbian derivation from data statistics.
    """
    P = C.shape[0]
    Cc = C - C.mean(axis=0, keepdims=True)     # center columns (features)
    rng = np.random.default_rng(seed + 90001)
    W = rng.standard_normal((k, P)) * 0.1      # k components, each a P-vector
    # normalize rows
    W /= (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
    last = None
    delta = 1.0
    for it in range(n_iter):
        # Treat each row of Cc as an input sample x (P-dim); Sanger update.
        y = Cc @ W.T                            # (P_samples, k)
        # Sanger: dW = lr * (y^T x - LT(y^T y) W)
        yx = y.T @ Cc                           # (k, P)
        yy = y.T @ y                            # (k, k)
        lt = np.tril(yy)                        # lower-triangular incl diag
        dW = lr * (yx - lt @ W)
        W = W + dW
        if nonneg:
            W = np.maximum(W, 0.0)              # Dordek non-negativity
        norms = np.linalg.norm(W, axis=1, keepdims=True)
        W = W / (norms + 1e-12)
        if last is not None:
            # sign/permutation-robust convergence: subspace projector delta
            delta = float(np.linalg.norm(W @ W.T - last @ last.T))
        last = W.copy()
    emb = W.T                                   # P x k
    return emb.astype(np.float64), delta


def embed_to_hd(emb: np.ndarray, n_dim: int, seed: int) -> np.ndarray:
    """Sign-random-projection of a P x k embedding into P x n_dim bipolar HD (SimHash; Charikar 2002).

    Fixed Gaussian projection R (deterministic seed). Angle structure of the embedding is
    approximately preserved (SimHash), then hard-quantized to bipolar {-1,+1}.
    """
    P, k = emb.shape
    rng = np.random.default_rng(seed + 12345)
    R = rng.standard_normal((k, n_dim))
    proj = emb @ R                              # (P, n_dim)
    code = np.sign(proj)
    code[code == 0] = 1.0
    return code.astype(np.float32)


def build_code(arm: str, k: int, T: np.ndarray, C: np.ndarray, n_dim: int, P: int,
               seed: int) -> tuple[np.ndarray, float]:
    """Return (P x n_dim bipolar address code, oja_conv_delta or nan)."""
    if arm == "stipulated":
        rng = np.random.default_rng(seed + 777)
        return bipolar_random_np((P, n_dim), rng), float("nan")
    if arm == "derived_sr":
        emb = derive_sr_embedding(T, k)
        return embed_to_hd(emb, n_dim, seed), float("nan")
    if arm == "derived_oja":
        emb, delta = derive_oja_embedding(C, k, seed)
        return embed_to_hd(emb, n_dim, seed), delta
    raise ValueError(f"unknown arm {arm!r}")


# ------------------------------------------------------------------- metrics
def mean_pairwise_abscos(code: np.ndarray) -> float:
    """Mean |cosine| over all address-vector pairs. Lower = better separated."""
    n = np.linalg.norm(code, axis=1, keepdims=True)
    u = code / (n + 1e-12)
    G = u @ u.T
    P = code.shape[0]
    iu = np.triu_indices(P, k=1)
    return float(np.mean(np.abs(G[iu])))


def flat_retrieval_accuracy(addr: np.ndarray, n_dim: int, V: int, n_trials: int,
                            seed: int) -> float:
    """FLAT bind/unbind retrieval (role_slot_summarizer FLAT primitive), reused verbatim in math.

    Each trial: bind each of the P addresses to a random value code; sign-bundle into one summary;
    recover each value via cleanup_argmax(bind(summary, addr_j), codebook). Accuracy = fraction of
    positions recovered. Value codebook is random bipolar, SHARED identically across arms.
    """
    P = addr.shape[0]
    rng = np.random.default_rng(seed + 55555)
    codebook = bipolar_random_np((V, n_dim), rng)  # shared content codebook (identical across arms)
    correct = 0
    total = 0
    for _ in range(n_trials):
        val_idx = rng.integers(0, V, size=P)
        val_vecs = codebook[val_idx]                # (P, n_dim)
        bound = bipolar_bind_np(addr, val_vecs)     # (P, n_dim)
        summary = sign_bundle_np(bound.sum(axis=0))  # (n_dim,)
        val_hat = bipolar_bind_np(summary[None, :], addr)  # (P, n_dim)
        preds = cleanup_argmax_np(val_hat, codebook)       # (P,)
        correct += int(np.sum(preds == val_idx))
        total += P
    return correct / total


# --------------------------------------------------------------------- run
def run(output_dir, P, n_dim, V, n_trials, n_seq_many, n_seq_few, seq_len, seeds, run_mode):
    t0 = time.time()
    expected_n_units = len(seeds) * (1 + len(K_EIG) * len(ROUTES))
    _write_start_marker(output_dir, run_mode, expected_n_units)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} P={P} N={n_dim} V={V} trials={n_trials} "
          f"seeds={seeds} K_EIG={K_EIG}", flush=True)

    T_analytic = analytic_chain_T(P)
    per_unit = []        # (arm, k, seed) rows
    failures = []
    code_hashes_seed0 = {}   # for arms_differ at first seed

    for si, seed in enumerate(seeds):
        srng = np.random.default_rng(seed)
        seqs_many = sample_sequences(P, n_seq_many, seq_len, srng)
        seqs_few = sample_sequences(P, n_seq_few, seq_len, srng)
        T_many, C_many = estimate_T_C(seqs_many, P)
        T_few, C_few = estimate_T_C(seqs_few, P)

        # stipulated (k-independent)
        try:
            addr, _ = build_code("stipulated", 0, T_many, C_many, n_dim, P, seed)
            sep = mean_pairwise_abscos(addr)
            retr = flat_retrieval_accuracy(addr, n_dim, V, n_trials, seed)
            per_unit.append({"arm": "stipulated", "k": None, "seed": seed,
                             "sep": sep, "retr": retr, "retr_few": retr, "oja_delta": None})
            if si == 0:
                code_hashes_seed0["stipulated"] = hashlib.sha256(
                    np.ascontiguousarray(np.sign(addr)).tobytes()).hexdigest()
            print(f"  seed={seed} stipulated sep={sep:.4f} retr={retr:.4f}", flush=True)
        except (np.linalg.LinAlgError, ValueError, FloatingPointError) as e:
            failures.append({"arm": "stipulated", "k": None, "seed": seed,
                             "failure_class": type(e).__name__, "msg": str(e)[:200]})

        # derived routes x k
        for route in ROUTES:
            for k in K_EIG:
                try:
                    # PRIMARY code from empirical many-sample statistics (derive-from-data).
                    addr_many, delta = build_code(route, k, T_many, C_many, n_dim, P, seed)
                    sep = mean_pairwise_abscos(addr_many)
                    retr = flat_retrieval_accuracy(addr_many, n_dim, V, n_trials, seed)
                    # generalization / overfit probe: few-sample statistics.
                    addr_few, _ = build_code(route, k, T_few, C_few, n_dim, P, seed)
                    retr_few = flat_retrieval_accuracy(addr_few, n_dim, V, n_trials, seed)
                    per_unit.append({"arm": route, "k": k, "seed": seed, "sep": sep,
                                     "retr": retr, "retr_few": retr_few,
                                     "oja_delta": (None if delta != delta else round(delta, 5))})
                    if si == 0 and k == K_EIG[0]:
                        code_hashes_seed0[route] = hashlib.sha256(
                            np.ascontiguousarray(addr_many).tobytes()).hexdigest()
                    print(f"  seed={seed} {route} k={k} sep={sep:.4f} retr={retr:.4f} "
                          f"retr_few={retr_few:.4f}", flush=True)
                except (np.linalg.LinAlgError, ValueError, FloatingPointError) as e:
                    failures.append({"arm": route, "k": k, "seed": seed,
                                     "failure_class": type(e).__name__, "msg": str(e)[:200]})

    # ---- cardinality gate (META_RULE_H)
    n_units = len(per_unit)
    cardinality_ok = (n_units == expected_n_units) and (len(failures) == 0)

    # ---- arms_differ (META_RULE_AF): stipulated vs derived_sr vs derived_oja at seed0/k0 bit-distinct
    arms_differ = (len(set(code_hashes_seed0.values())) == len(code_hashes_seed0)
                   and len(code_hashes_seed0) == len(ARMS))

    # ---- aggregate helpers
    def agg(arm, k):
        rows = [u for u in per_unit if u["arm"] == arm and u["k"] == k]
        if not rows:
            return None
        seps = np.array([r["sep"] for r in rows])
        retrs = np.array([r["retr"] for r in rows])
        retrs_few = np.array([r["retr_few"] for r in rows])
        return {"n": len(rows),
                "sep_mean": float(seps.mean()), "sep_std": float(seps.std()),
                "retr_mean": float(retrs.mean()), "retr_std": float(retrs.std()),
                "retr_few_mean": float(retrs_few.mean())}

    stip = agg("stipulated", None)
    random_null = float(np.sqrt(2.0 / (np.pi * n_dim)))  # analytic mean|cos| for random bipolar

    derived_agg = {}
    for route in ROUTES:
        for k in K_EIG:
            a = agg(route, k)
            if a is not None:
                derived_agg[f"{route}_k{k}"] = a

    # ---- baseline in band (META_RULE_AG)
    baseline_in_band = (stip is not None
                        and BASELINE_BAND[0] < stip["retr_mean"] < BASELINE_BAND[1])

    # ---- discriminator fires: derived_sr k=2 SEP measurably > random null AND arms differ
    sr_k2 = derived_agg.get("derived_sr_k2")
    discriminator_fires = bool(arms_differ and sr_k2 is not None
                               and sr_k2["sep_mean"] > random_null * 1.5)

    # ---- verdict logic (per pre-registered bands)
    verdict = "UNKNOWN"
    verdict_msg = ""
    best_win = None
    if stip is None:
        verdict = "CELL_ERROR_NO_BASELINE"
        verdict_msg = "no stipulated baseline computed"
    elif not baseline_in_band:
        verdict = "SMOKE_GATE_FAIL_BASELINE_OUT_OF_BAND"
        verdict_msg = (f"stipulated retr={stip['retr_mean']:.3f} outside "
                       f"{BASELINE_BAND} (META_RULE_AG: iterate N/K/V before trusting arms)")
    elif not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = f"n_units={n_units} expected={expected_n_units} failures={len(failures)}"
    elif not discriminator_fires:
        verdict = "MIDDLE_BAND_DISCRIMINATOR_VACUOUS"
        verdict_msg = ("derived_sr k=2 did not produce structure above random null OR arms not "
                       "distinct; separation discriminator vacuous")
    else:
        R_stip = stip["retr_mean"]
        S_stip = stip["sep_mean"]
        S_sig = stip["sep_std"]
        # scan for a DERIVE_WINS unit: retr within 5% AND not worse-separated AND generalizes
        wins = []
        for key, a in derived_agg.items():
            retr_ok = a["retr_mean"] >= R_stip - RETR_DROP_TOL
            sep_ok = a["sep_mean"] <= S_stip + SEP_SIGMA_MULT * S_sig
            gen_gap = a["retr_mean"] - a["retr_few_mean"]
            gen_ok = gen_gap <= GEN_GAP_TOL
            # A genuine win must RETAIN derived structure (sep meaningfully above the random
            # null). A high-k code that matches retrieval only by washing out to near-random is
            # INERT (it reproduces the stipulated random code), NOT a win for derivation.
            structure_ok = a["sep_mean"] > random_null * 1.5
            if retr_ok and sep_ok and gen_ok and structure_ok:
                wins.append((key, a, gen_gap))
        # best retrieval among derived
        best_key = max(derived_agg, key=lambda kk: derived_agg[kk]["retr_mean"])
        best_a = derived_agg[best_key]
        best_gen_gap = best_a["retr_mean"] - best_a["retr_few_mean"]
        all_hurt = all(a["retr_mean"] < R_stip - RETR_DROP_TOL for a in derived_agg.values())
        best_inert = (best_a["retr_mean"] >= R_stip - RETR_DROP_TOL
                      and best_a["sep_mean"] <= random_null * 1.5)

        if wins:
            # a real win must also not be merely inert (must be better-or-equal separated with
            # structure, i.e. genuinely derived-and-still-orthogonal)
            best_win = sorted(wins, key=lambda w: -w[1]["retr_mean"])[0][0]
            verdict = "HARD_PASS_DERIVE_WINS"
            wa = derived_agg[best_win]
            verdict_msg = (f"{best_win}: retr={wa['retr_mean']:.3f} (stip {R_stip:.3f}) "
                           f"sep={wa['sep_mean']:.4f} (stip {S_stip:.4f}); derive matches/beats "
                           f"stipulate -- REFUTES Plate/Kanerva for this substrate")
        elif all_hurt:
            verdict = "HARD_FAIL_DERIVE_HURTS"
            verdict_msg = (f"ALL derived routes/k drop retr >= {RETR_DROP_TOL} vs stipulated "
                           f"({R_stip:.3f}); best derived {best_key} retr={best_a['retr_mean']:.3f}; "
                           f"CONFIRMS Plate/Kanerva: derive HURTS structural addressing")
        elif best_gen_gap > GEN_GAP_TOL:
            verdict = "HARD_FAIL_DERIVE_OVERFITS"
            verdict_msg = (f"best derived {best_key} sampling gap many-vs-few="
                           f"{best_gen_gap:.3f} > {GEN_GAP_TOL}; overfits transition statistics")
        elif best_inert:
            verdict = "MIDDLE_BAND_DERIVE_INERT"
            verdict_msg = (f"best derived {best_key} retr={best_a['retr_mean']:.3f} within 5% of "
                           f"stipulated but sep~random_null ({best_a['sep_mean']:.4f} vs null "
                           f"{random_null:.4f}); eigenstructure washed out -- derive buys nothing")
        else:
            verdict = "MIDDLE_BAND_CHARACTERIZED"
            verdict_msg = (f"k-dependent tradeoff; best derived {best_key} retr="
                           f"{best_a['retr_mean']:.3f} sep={best_a['sep_mean']:.4f} vs stipulated "
                           f"retr={R_stip:.3f} sep={S_stip:.4f}; no clean win, no full kill")

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:160]}",
        "elapsed_s": round(elapsed, 3),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {"P": P, "n_dim": n_dim, "V": V, "n_trials": n_trials,
                   "n_seq_many": n_seq_many, "n_seq_few": n_seq_few, "seq_len": seq_len,
                   "seeds": seeds, "K_EIG": K_EIG, "gamma_sr": GAMMA_SR},
        "bands": {"retr_drop_tol": RETR_DROP_TOL, "sep_sigma_mult": SEP_SIGMA_MULT,
                  "gen_gap_tol": GEN_GAP_TOL, "baseline_band": list(BASELINE_BAND)},
        "gates": {"cardinality_ok": cardinality_ok, "arms_differ": arms_differ,
                  "baseline_in_band": baseline_in_band,
                  "discriminator_fires": discriminator_fires,
                  "n_units": n_units, "expected_n_units": expected_n_units},
        "random_null_abscos": random_null,
        "stipulated": stip,
        "derived": derived_agg,
        "best_derive_win": best_win,
        "per_unit": per_unit,
        "failures": failures,
        "arm_hashes_seed0": code_hashes_seed0,
    }
    _write_metrics(output_dir, metrics)
    print(f"[{ANCHOR_NAME}] VERDICT {verdict} | {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.2f}s units={n_units}/{expected_n_units}", flush=True)
    return metrics


# --------------------------------------------------------------------- self_test
def self_test():
    """Real-code-path self-test: exercises the REAL derivation + retrieval + reuse-fidelity asserts."""
    print("[self-test] reuse-fidelity: numpy bind/cleanup == role_slot_summarizer torch primitives",
          flush=True)
    import torch
    from hdlab.role_slot_summarizer import (_bipolar_bind, _bipolar_quantize,
                                            cleanup_argmax as rss_cleanup)
    rng = np.random.default_rng(0)
    a = bipolar_random_np((5, 32), rng)
    b = bipolar_random_np((5, 32), rng)
    ta = torch.from_numpy(a)
    tb = torch.from_numpy(b)
    assert np.array_equal(bipolar_bind_np(a, b), _bipolar_bind(ta, tb).numpy()), "bind mismatch"
    s = a.sum(axis=0)
    assert np.array_equal(sign_bundle_np(s), _bipolar_quantize(torch.from_numpy(s)).numpy()), \
        "sign-bundle mismatch"
    cb = bipolar_random_np((8, 32), rng)
    q = bipolar_random_np((32,), rng)
    assert int(cleanup_argmax_np(q[None, :], cb)[0]) == rss_cleanup(torch.from_numpy(q),
                                                                    torch.from_numpy(cb)), \
        "cleanup mismatch"

    print("[self-test] real derivation routes + retrieval at tiny scale", flush=True)
    P, n_dim, V = 12, 128, 16
    T = analytic_chain_T(P)
    seqs = sample_sequences(P, 30, 40, np.random.default_rng(1))
    Th, Ch = estimate_T_C(seqs, P)
    exercised = set()
    hashes = {}
    for arm in ARMS:
        code, delta = build_code(arm, 4, Th, Ch, n_dim, P, seed=7)
        assert code.shape == (P, n_dim), f"{arm} shape {code.shape}"
        assert set(np.unique(code).tolist()).issubset({-1.0, 1.0}), f"{arm} not bipolar"
        sep = mean_pairwise_abscos(code)
        acc = flat_retrieval_accuracy(code, n_dim, V, n_trials=10, seed=7)
        assert 0.0 <= acc <= 1.0, f"{arm} acc out of range {acc}"
        assert np.isfinite(sep), f"{arm} sep non-finite"
        hashes[arm] = hashlib.sha256(np.ascontiguousarray(code).tobytes()).hexdigest()
        exercised.add(arm)
    assert exercised == set(ARMS), f"real_code_path: not all arms exercised {exercised}"
    assert len(set(hashes.values())) == len(hashes), "META_RULE_AF: arm codes not bit-distinct"

    # SR analytic-chain sanity: top eigenvector of the SR matrix should be low-frequency (adjacent
    # slots more similar than distant) -> mean|cos| of a low-k derived code > random null.
    sr_code = embed_to_hd(derive_sr_embedding(T, 2), 512, seed=7)
    null = float(np.sqrt(2.0 / (np.pi * 512)))
    assert mean_pairwise_abscos(sr_code) > null, "SR k=2 code not more correlated than random null"

    # Oja convergence diagnostic present + finite.
    _, d = derive_oja_embedding(Ch, 4, seed=7)
    assert np.isfinite(d), "oja convergence delta non-finite"
    print(f"[self-test] PASS: reuse-fidelity OK; {len(ARMS)} arms distinct; SR structure > null; "
          f"oja_delta={d:.4f}", flush=True)


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, P=64, n_dim=1024, V=128, n_trials=60, n_seq_many=400, n_seq_few=25,
            seq_len=80, seeds=[7, 13], run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, P=64, n_dim=1024, V=128, n_trials=200, n_seq_many=400, n_seq_few=25,
            seq_len=80, seeds=SEEDS, run_mode="full")
    sys.exit(0)


if __name__ == "__main__":
    _out = os.path.join(REPO, "data", ANCHOR_NAME)
    if "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out, e)
        raise
