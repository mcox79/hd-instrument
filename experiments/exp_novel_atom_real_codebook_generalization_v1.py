"""Novel-atom generalization on the REAL text8 PPMI-SVD codebook -- the make-or-break revival (v1).

THE VET (atom 29380, exp_novel_atom_generalization_codebook_binding_v1): the synthetic linear-shared-
latent world made ridge induction trivially recoverable (codebook_derived collapsed 0.776 -> 0.036/chance
the instant the feature->code map was made even mildly nonlinear). The proven bound from that cell is
"imperfect codes survive composition in a LINEARLY-structured world," NOT "the codebook feature-generalizes
to NOVEL atoms." The VET named the decisive, non-construction-determined revival: run the SAME integration
(learned codebook induction + free HRR binding + cleanup) on the REAL text8 PPMI/SVD codebook (atom 29368,
exp_learned_codebook_generalization_gate_v1, held-out relatedness AUC=0.927), where the feature->code map
is GENUINELY nonlinear (PPMI's log-ratio transform + a data-driven SVD rotation of the full VxV PPMI
matrix -- not a fixed linear generative model known to the test designer) and CANNOT be trivially recovered
by a linear ridge fit on a lower-dimensional random-projection sketch of the same raw counts. THIS is the
make-or-break: pass = a genuine novel-atom chain-grade; fail = novel-atom composition is genuinely bounded.

WORLD (real, not synthetic; the "ground-truth structured space" is the REAL codebook cell's own product):
  1. Build vocab (V=10000) + word-word co-occurrence + PPMI from text8 (8,000,000 tokens; window=5;
     min_count=5) -- IDENTICAL corpus params to the codebook CG cell's FULL run (atom 29368, AUC=0.927),
     for direct regime comparability. Reuses the codebook cell's own tokenizer/vocab/cooc/ppmi/SVD
     functions directly (import), not a reimplementation -- same code path as the credited/validated cell.
  2. TRUE code table = ppmi_svd codebook (TruncatedSVD of the full PPMI matrix, seed=7) -- the "already-
     structured ground-truth space" every atom (seen or held-out) is registered into.
  3. HELD-OUT ("novel") words = F_NOVEL=30 words at vocabulary RANK 800-4800 (mid-frequency real content
     words, count 160-1013 -- excludes both the top-800 function-word band and the very-rare tail; a
     fixed deterministic rank-stride selection, no hash()/list(set()) ordering). These words' TRUE codes
     are NEVER used to fit the induction map below.
  4. SEEN words = V - F_NOVEL (~9970 words) -- the induction map is fit on THEIR (feature, true-code)
     pairs only.

THE FEATURE->CODE MAP (why this dodges the 29380 linear-construction trap):
  - FEATURE(word) = PPMI-transformed co-occurrence row, projected through a FIXED sparse-ternary random
    projection R_feat (V -> D_FEAT=256) -- structurally identical to the codebook cell's own "ppmi_rp" arm
    (reuses `sparse_ternary_projection`). For SEEN words this uses their FULL corpus row; for HELD-OUT
    words this uses a PARTIAL, NOISY row built from only a random ~30% subsample of that word's own
    occurrence positions in the token stream (a REAL, not synthetic-Gaussian, noisy observation -- the
    word's own usage pattern under-sampled, exactly analogous to "not having read every context the word
    ever appeared in").
  - TARGET (true code) = the ppmi_svd embedding, produced via TruncatedSVD -- a DATA-DRIVEN eigenrotation
    of the FULL VxV PPMI matrix. The induction map only sees a D_FEAT=256-dim random-projection SKETCH of
    PPMI (not the full V=10000-dim row SVD operates on), so recovering the SVD code from that sketch via a
    linear ridge fit is inherently lossy/approximate -- there is no construction-guaranteed exact linear
    relationship between FEATURE and TARGET (unlike 29380's shared-latent world, where both were EXACT
    linear images of the identical Z by explicit design). Pilot-verified (see calibration note): even with
    the CHEAT case (full, non-partial features on held-out words), ridge-recovered cosine-to-true caps at
    ~0.49, not 1.0 -- the map is genuinely imperfect BEFORE any held-out-specific noise is added.

ARMS (ONE variable = how the HELD-OUT word's bound filler code is produced; other-role fillers ALWAYS use
TRUE codes of randomly-drawn SEEN words in every arm):
  codebook_derived   : ridge induction map W (fit on SEEN (feature, true-code) pairs ONLY, alpha=10.0)
                       applied to a FRESH partial/noisy real feature draw of the held-out word [genuine].
  handed_ceiling     : the held-out word's TRUE ppmi_svd code, handed directly [ceiling-only control].
  random_code        : an independent unit-norm random Gaussian vector, uncorrelated with content [format-
                       only content-control].
  memorize_prototype : 1-NN over SEEN words' FULL features (Euclidean) vs the held-out word's PARTIAL
                       feature draw; predicts the nearest SEEN word's TRUE code [naive-similarity baseline
                       -- see IMPORTANT CALIBRATION NOTE below: this is NOT expected to be near-zero on
                       real data, unlike the synthetic cell's i.i.d.-atom world].

IMPORTANT CALIBRATION NOTE / HONEST DEVIATION FROM THE SYNTHETIC CELL'S TEMPLATE (pilot-verified BEFORE
dispatch, not discovered post-hoc): in atom 29380's synthetic world, held-out atoms were i.i.d. random with
NO semantic-neighborhood structure, so memorize_prototype was STRUCTURALLY guaranteed ~0.000 (a genuine
"should-fail" control). REAL text8 vocabulary has genuine distributional-semantic neighborhood structure:
a held-out word's nearest SEEN neighbor by PPMI-feature similarity is often ALSO reasonably close to it in
ppmi_svd code-space (that is precisely what "words with similar meaning cluster" means), so
memorize_prototype carries REAL, non-zero signal on real data -- pilot measured 0.225-0.32 accuracy for
memorize_prototype vs ~0.000-0.015 for random_code (see calibration sweep below). This is reported
honestly rather than forced into the synthetic template's "should collapse to 0" expectation. The
discriminating question therefore SHIFTS from "genuine arm beats a guaranteed-zero baseline" to "does the
REGRESSION-based induction map (which uses the held-out word's OWN real features, not just similarity to
seen words) add value beyond NAIVE nearest-neighbor prototype matching" -- exactly the sharper, more
demanding version of the make-or-break question. random_code remains the true chance/format-only floor.

PRIOR ART (credit; learn-from/build-on, never steal):
  - Levy & Goldberg 2015 (PPMI+SVD word embeddings); Church & Hanks 1990 (PMI); Kanerva 1988 / Sahlgren
    2005 (Random Indexing) -- all credited via the codebook CG cell this integrates with (atom 29368,
    exp_learned_codebook_generalization_gate_v1); reuses its build_vocab/build_cooc/build_ppmi/
    sparse_ternary_projection/build_codebook functions directly (import, same code path).
  - a-la-carte embeddings: Khodak, Saunshi, Liang, Ma, Stewart & Arora, ACL 2018 (linear induction map from
    context features to embedding space, fit on seen words, applied to novel/rare words) -- the ridge
    template, now on REAL features/codes instead of a synthetic linear world.
  - Prototypical Networks: Snell, Swersky & Zemel, NeurIPS 2017 (nearest-prototype baseline analog).
  - Plate 1995 HRR (circular-convolution bind/unbind on REAL dense vectors -- the codebook's codes are
    dense real L2-normalized vectors, NOT phasors, so this cell uses hdlab.binding's HRR (real, FFT
    circular-convolution) dispatch path, not the FHRR complex-phasor path the synthetic cell used).
  - "Unitary vectors" for HRR role codes (Plate 1995): a FIXED, task-agnostic, conjugate-symmetric unit-
    magnitude-spectrum construction guaranteeing near-exact bind/unbind round trip regardless of filler
    content -- pilot-verified round-trip cosine=1.000 (see self-test).
  - McClelland, McNaughton & O'Reilly 1995 (CLS); Greff, van Steenkiste & Schmidhuber 2020 (construction-
    determinism critique -- the direct motivation for this cell, credited via atom 29380's revival note).

Pre-reg: preregs/2026-07-20_novel_atom_real_codebook_generalization_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise BEFORE
except Exception (no BaseException); crlb_n/a declared; baseline_in_band (ceiling-check sanity, REAL dense
HRR mechanics, not assumed from the FHRR synthetic cell); discriminator survives scale (smoke = reduced
corpus per codebook-cell convention, explicitly checked before FULL, not assumed); HARD_PASS strictly above
floor; cardinality gate; per-unit failure-class; fixed arithmetic seeds (no hash()/list(set())).

ASCII-only. No emojis. No em dashes.
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
import scipy.sparse as sp
import torch

ANCHOR_NAME = "exp_novel_atom_real_codebook_generalization_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.binding import bind, unbind  # noqa: E402
from experiments.exp_learned_codebook_generalization_gate_v1 import (  # noqa: E402
    load_tokens, build_vocab, build_cooc, build_ppmi, sparse_ternary_projection, build_codebook,
)

# --------------------------------------------------------------------------- config (FULL; matches the
# codebook CG cell's FULL regime -- atom 29368, AUC=0.927 -- for direct comparability)
N = 1024                 # HRR dim (dense real; CLAUDE.md default)
D_FEAT = 256              # observable feature dim (PPMI + fixed sparse-ternary projection)
RI_SPARSITY = 10          # matches codebook cell's ri_sparsity
FEAT_PROJ_SEED = 9001     # fixed, task-agnostic feature-projection matrix seed
CODE_SEED = 7             # fixed seed for the ppmi_svd TRUE codebook build (TruncatedSVD random_state)
RIDGE_ALPHA = 10.0        # fixed ridge regularization (pilot-selected among {0.1,1,10,100}; see calibration)
ROLE_SEED = 1234          # fixed, task-agnostic unitary-HRR role-code seed
DISTRACTOR_SEED = 777     # fixed, task-agnostic candidate-table distractor sample
R_ROLES = 6               # roles per scene (matches prior novel-atom cell convention)
ALPHA_FRAC = 0.3          # fraction of a held-out word's OWN occurrences sampled per noisy draw
MIN_OCC_PER_DRAW = 20     # floor on occurrences per partial draw

ARMS = ["codebook_derived", "handed_ceiling", "random_code", "memorize_prototype"]
SEEDS = [7, 13, 19]       # governs ONLY per-scene noise draws (occurrence subsample, other-role fillers,
                          # random-code draw) -- the world/codebook/role-codes/candidate-table are FIXED.

FULL_CFG = dict(n_tokens=8_000_000, vocab_size=10000, window=5, min_count=5,
                rank_lo=800, rank_hi=4800, f_novel=30, n_distractor=120, k_eval=40)
SMOKE_CFG = dict(n_tokens=1_500_000, vocab_size=6000, window=5, min_count=5,
                 rank_lo=400, rank_hi=2400, f_novel=20, n_distractor=80, k_eval=20)

CEIL_CHECK_SCENES = 200

# Pre-registered bands (declared BEFORE the calibrated-final run; see prereg for the pilot sweep that set
# them; HYPOTHESIZED then MEASURED at smoke/full per the self-test + smoke gate).
HP_CODEBOOK_ACC_MIN = 0.20                 # codebook_derived must clear this outright
HP_CODEBOOK_VS_RANDOM_MARGIN = 0.15        # and beat random_code by this much
HP_CODEBOOK_VS_MEMORIZE_MARGIN = 0.05      # and beat the naive nearest-neighbor baseline by this much
HF_CODEBOOK_FLOOR = 0.05                   # collapse-toward-chance failure
HF_CODEBOOK_VS_RANDOM_MARGIN = 0.03        # "only matches random" failure
HF_CODEBOOK_VS_MEMORIZE_MARGIN = 0.00      # "adds no value over naive similarity" failure
CEIL_CHECK_MIN = 0.90                      # sanity: real dense-HRR bind/bundle/unbind/cleanup mechanics


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(marker, fh)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- real-world builders
def unitary_hrr(n_vecs: int, dim: int, seed: int) -> torch.Tensor:
    """Fixed, task-agnostic real HRR role codes: conjugate-symmetric unit-magnitude spectrum -> IFFT ->
    real vector whose circular auto/cross-correlation with any filler is (near-)exact self-inverse
    (Plate 1995 unitary-vector trick). dim must be even."""
    assert dim % 2 == 0, f"unitary_hrr requires even dim, got {dim}"
    rng_u = np.random.default_rng(seed)
    half = dim // 2
    out = np.zeros((n_vecs, dim), dtype=np.float64)
    for i in range(n_vecs):
        phases = rng_u.uniform(-np.pi, np.pi, size=half - 1)
        spec = np.zeros(dim, dtype=complex)
        spec[0] = 1.0
        spec[1:half] = np.exp(1j * phases)
        spec[half] = rng_u.choice([-1.0, 1.0])
        spec[half + 1:] = np.conj(spec[1:half][::-1])
        out[i] = np.fft.ifft(spec).real
    return torch.from_numpy(out).float()


def build_real_world(n_tokens, vocab_size, window, min_count):
    """Load text8, build vocab/cooc/ppmi/TRUE-codebook. Reuses the codebook CG cell's own functions
    (same code path as atom 29368) -- not a reimplementation."""
    tokens = load_tokens(n_tokens)
    w2i, counts = build_vocab(tokens, vocab_size=vocab_size, min_count=min_count)
    V = len(w2i)
    ids = np.fromiter((w2i.get(t, -1) for t in tokens), dtype=np.int64, count=len(tokens))
    cooc = build_cooc(tokens, w2i, window)
    ppmi = build_ppmi(cooc)
    true_codes_np = build_codebook("ppmi_svd", cooc, ppmi, V, N, CODE_SEED, RI_SPARSITY)
    return V, ids, cooc, ppmi, true_codes_np, counts


def compute_ppmi_col_stats(cooc):
    col_sum = np.asarray(cooc.sum(axis=0)).ravel().astype(np.float64)
    col_sum_a = np.power(col_sum, 0.75)
    col_total_a = float(col_sum_a.sum())
    return col_sum_a, col_total_a


def ppmi_transform_row(raw_row, col_sum_a, col_total_a):
    """Same PPMI formula as build_ppmi (alpha=0.75 context smoothing), generalized to ANY dense row
    (full-corpus row for SEEN words, or a partial/noisy row for HELD-OUT words)."""
    row_total = raw_row.sum()
    if row_total <= 0:
        return np.zeros_like(raw_row)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (raw_row * col_total_a) / (row_total * col_sum_a + 1e-30)
        pmi = np.log(ratio + 1e-30)
    return np.maximum(pmi, 0.0)


def feat_from_raw_row(raw_row, R_feat, col_sum_a, col_total_a):
    p = ppmi_transform_row(raw_row, col_sum_a, col_total_a)
    f = (sp.csr_matrix(p) @ R_feat).toarray().ravel()
    n = np.linalg.norm(f)
    return f / n if n > 1e-12 else f


def build_partial_cooc_row(ids, position_subset, V, window):
    """Real, noisy 'observation' of a word's own co-occurrence pattern: only a random subsample of that
    word's OWN occurrence positions in the token stream contributes context counts (not synthetic-Gaussian
    noise -- genuine under-sampling of the word's real usage)."""
    row = np.zeros(V, dtype=np.float64)
    n_tok = len(ids)
    for p in position_subset:
        for d in range(1, window + 1):
            if p - d >= 0:
                c = ids[p - d]
                if c >= 0:
                    row[c] += 1.0
            if p + d < n_tok:
                c = ids[p + d]
                if c >= 0:
                    row[c] += 1.0
    return row


def ridge_fit(X: np.ndarray, Y: np.ndarray, alpha: float) -> np.ndarray:
    Xb = np.concatenate([X, np.ones((X.shape[0], 1), dtype=X.dtype)], axis=1)
    d1 = Xb.shape[1]
    A = Xb.T @ Xb + alpha * np.eye(d1, dtype=X.dtype)
    B = Xb.T @ Y
    return np.linalg.solve(A, B)


def ridge_predict(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    Xb = np.concatenate([X, np.ones((X.shape[0], 1), dtype=X.dtype)], axis=1)
    return Xb @ W


# --------------------------------------------------------------------------- batched HRR ops (real dtype
# -> hdlab.binding dispatches to FFT circular convolution; verified vs hdlab in self_test)
def batched_bundle(stack: torch.Tensor) -> torch.Tensor:
    """(batch, k, n) -> (batch, n), whole-vector L2 normalize (HRR convention; matches hdlab.bundling for
    real-dtype input)."""
    s = stack.sum(dim=1)
    norm = s.norm(dim=-1, keepdim=True)
    norm = torch.where(norm > 0, norm, torch.ones_like(norm))
    return s / norm


def decode_scenes(focal_codes, other_codes, role_codes, cand_table):
    """focal_codes:(S,N) real; other_codes:(S,R-1,N) real (TRUE codes of other roles' SEEN fillers);
    role_codes:(R,N) fixed unitary real; cand_table:(C,N) real L2-normalized candidate TRUE codes.
    bind(role,filler) -> bundle -> unbind(role0) -> dot-product cleanup argmax over cand_table."""
    S = focal_codes.shape[0]
    n_dim = focal_codes.shape[-1]
    n_roles = role_codes.shape[0]
    all_fillers = torch.cat([focal_codes.unsqueeze(1), other_codes], dim=1)  # (S,R,N)
    role_b = role_codes.unsqueeze(0).expand(S, n_roles, n_dim)
    bound = bind(role_b, all_fillers)
    scene = batched_bundle(bound)
    role0_b = role_codes[0].unsqueeze(0).expand(S, n_dim)
    unbound = unbind(scene, role0_b)
    sims = unbound @ cand_table.T  # (S,C)
    return sims.argmax(dim=-1).numpy()


# --------------------------------------------------------------------------- per-seed unit
def run_one_seed(seed, V, ids, true_codes, feat_full_all, W_ridge, seen_idx, held_idx, cand_idx, cand_pos,
                  role_codes, cand_table, positions, window, k_eval, output_dir):
    rng = np.random.default_rng(seed)
    col_sum_a, col_total_a = _COL_STATS  # module-level cache set by run() to avoid recompute per seed
    seen_feats = feat_full_all[seen_idx]

    per_arm_acc = {}
    per_arm_preds = {}
    per_atom_diag = {}

    for arm in ARMS:
        n_correct = 0
        n_total = 0
        preds_all = []
        for i in held_idx:
            pos_i = positions[i]
            n_take = max(MIN_OCC_PER_DRAW, int(ALPHA_FRAC * len(pos_i)))
            n_take = min(n_take, len(pos_i))
            target_pos = cand_pos[int(i)]

            other_idx = rng.choice(seen_idx, size=(k_eval, R_ROLES - 1))
            other_codes = true_codes[torch.from_numpy(other_idx)]

            if arm == "handed_ceiling":
                focal = true_codes[i].unsqueeze(0).expand(k_eval, N).clone()
                preds = decode_scenes(focal, other_codes, role_codes, cand_table)
            elif arm == "random_code":
                rc = torch.from_numpy(
                    np.random.default_rng(seed * 100000 + int(i)).standard_normal(N)).float()
                rc = rc / rc.norm()
                focal = rc.unsqueeze(0).expand(k_eval, N).clone()
                preds = decode_scenes(focal, other_codes, role_codes, cand_table)
            else:
                # both codebook_derived and memorize_prototype need the SAME noisy partial feature draws
                feats = []
                for _k in range(k_eval):
                    subset = rng.choice(pos_i, size=n_take, replace=False)
                    raw_row = build_partial_cooc_row(ids, subset, V, window)
                    feats.append(feat_from_raw_row(raw_row, _R_FEAT, col_sum_a, col_total_a))
                feats = np.stack(feats)
                if arm == "codebook_derived":
                    pred = ridge_predict(W_ridge, feats)
                    predn = pred / np.linalg.norm(pred, axis=1, keepdims=True)
                    focal = torch.from_numpy(predn).float()
                    preds = decode_scenes(focal, other_codes, role_codes, cand_table)
                    cos_true = float((predn * true_codes.numpy()[i][None, :]).sum(axis=1).mean())
                    per_atom_diag[str(int(i))] = {"mean_cos_derived_vs_true": cos_true}
                elif arm == "memorize_prototype":
                    dists = np.linalg.norm(feats[:, None, :] - seen_feats[None, :, :], axis=-1)
                    j_star = dists.argmin(axis=-1)
                    nn_idx = seen_idx[j_star]
                    focal = true_codes[torch.from_numpy(nn_idx)]
                    preds = decode_scenes(focal, other_codes, role_codes, cand_table)
                else:
                    raise ValueError(f"unknown arm {arm!r}")

            correct = (preds == target_pos)
            n_correct += int(correct.sum())
            n_total += k_eval
            preds_all.append(preds)
        per_arm_acc[arm] = n_correct / n_total if n_total else float("nan")
        per_arm_preds[arm] = np.concatenate(preds_all)

    return {"seed": seed, "per_arm_acc": per_arm_acc,
            "per_arm_preds_hash": {a: hashlib.sha256(p.tobytes()).hexdigest() for a, p in per_arm_preds.items()},
            "novel_atom_diagnostics": per_atom_diag}


def ceiling_check(seed, true_codes, seen_idx, distractor_idx, cand_pos, role_codes, cand_table, n_scenes=CEIL_CHECK_SCENES):
    """Mechanics sanity: handed-code decode of DISTRACTOR (SEEN, in-candidate-table) words, SAME candidate
    table / role codes / R as the main experiment -- confirms real dense-HRR bind/bundle/unbind/cleanup
    mechanics work at this regime BEFORE any arm's result is interpreted."""
    rng = np.random.default_rng(90000 + seed)
    n_roles = role_codes.shape[0]  # derive from role_codes, NOT the module-level R_ROLES constant, so
                                    # this helper is reusable at any scale (self-test uses fewer roles)
    focal_local = rng.integers(0, len(distractor_idx), size=n_scenes)
    focal_global = distractor_idx[focal_local]
    other_idx = rng.choice(seen_idx, size=(n_scenes, n_roles - 1))
    focal_codes = true_codes[torch.from_numpy(focal_global)]
    other_codes = true_codes[torch.from_numpy(other_idx)]
    preds = decode_scenes(focal_codes, other_codes, role_codes, cand_table)
    target_pos = np.array([cand_pos[int(g)] for g in focal_global])
    return float((preds == target_pos).mean())


# --------------------------------------------------------------------------- runner
_COL_STATS = None
_R_FEAT = None


def run(output_dir, cfg, seeds, run_mode):
    global _COL_STATS, _R_FEAT
    t0 = time.perf_counter()
    expected_n_units = len(seeds) * len(ARMS)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"building real world: n_tokens={cfg['n_tokens']} vocab_size={cfg['vocab_size']}")
    V, ids, cooc, ppmi, true_codes_np, counts = build_real_world(
        cfg["n_tokens"], cfg["vocab_size"], cfg["window"], cfg["min_count"])
    true_codes = torch.from_numpy(true_codes_np).float()
    _hb(output_dir, f"world built: V={V}")

    _R_FEAT = sparse_ternary_projection(V, D_FEAT, RI_SPARSITY, FEAT_PROJ_SEED)
    feat_full_all = (ppmi @ _R_FEAT).toarray().astype(np.float64)
    nrm = np.linalg.norm(feat_full_all, axis=1, keepdims=True)
    nrm[nrm < 1e-12] = 1.0
    feat_full_all = feat_full_all / nrm
    _COL_STATS = compute_ppmi_col_stats(cooc)
    _hb(output_dir, "features + PPMI col-stats built")

    rank_lo, rank_hi, f_novel = cfg["rank_lo"], cfg["rank_hi"], cfg["f_novel"]
    stride = (rank_hi - rank_lo) // f_novel
    held_ranks = [rank_lo + i * stride for i in range(f_novel)]
    held_idx = np.array(held_ranks)
    held_set = set(held_ranks)
    seen_idx = np.array([i for i in range(V) if i not in held_set])
    held_counts = [float(counts[r]) for r in held_ranks]
    _hb(output_dir, f"held-out F_NOVEL={f_novel} rank[{rank_lo}:{rank_hi}] counts_range="
                    f"[{min(held_counts):.0f},{max(held_counts):.0f}]")

    X_train = feat_full_all[seen_idx]
    Y_train = true_codes_np[seen_idx]
    W_ridge = ridge_fit(X_train, Y_train, RIDGE_ALPHA)
    _hb(output_dir, f"ridge induction map fit on {len(seen_idx)} SEEN words (D_FEAT={D_FEAT})")

    distractor_rng = np.random.default_rng(DISTRACTOR_SEED)
    distractor_idx = distractor_rng.choice(seen_idx, size=cfg["n_distractor"], replace=False)
    cand_idx = np.concatenate([held_idx, distractor_idx])
    cand_table = true_codes[torch.from_numpy(cand_idx)]
    cand_pos = {int(idx): pos for pos, idx in enumerate(cand_idx)}
    chance_floor = 1.0 / len(cand_idx)
    _hb(output_dir, f"candidate table size={len(cand_idx)} chance_floor={chance_floor:.5f}")

    positions = {i: np.where(ids == i)[0] for i in held_idx}
    role_codes = unitary_hrr(R_ROLES, N, seed=ROLE_SEED)

    ceil_vals = [ceiling_check(s, true_codes, seen_idx, distractor_idx, cand_pos, role_codes, cand_table)
                 for s in seeds]
    ceiling_check_mean = float(np.mean(ceil_vals))
    baseline_in_band = ceiling_check_mean >= CEIL_CHECK_MIN
    _hb(output_dir, f"ceiling_check (mechanics sanity) mean={ceiling_check_mean:.4f}")

    per_unit = {}
    per_seed_results = {}
    n_units_done = 0
    seed_pred_hashes = {}
    for seed in seeds:
        try:
            res = run_one_seed(seed, V, ids, true_codes, feat_full_all, W_ridge, seen_idx, held_idx,
                                cand_idx, cand_pos, role_codes, cand_table, positions, cfg["window"],
                                cfg["k_eval"], output_dir)
            per_seed_results[seed] = res
            seed_pred_hashes[seed] = res["per_arm_preds_hash"]
            for arm in ARMS:
                unit_key = f"{arm}__seed{seed}"
                per_unit[unit_key] = {"arm": arm, "seed": seed,
                                       "novel_query_acc": res["per_arm_acc"][arm], "failure_class": None}
                n_units_done += 1
            _hb(output_dir, f"seed={seed}: per_arm={ {a: round(v, 3) for a, v in res['per_arm_acc'].items()} }")
        except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
            for arm in ARMS:
                unit_key = f"{arm}__seed{seed}"
                per_unit[unit_key] = {"arm": arm, "seed": seed,
                                       "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
            _hb(output_dir, f"seed={seed}: FAILED {type(e).__name__}: {e}")

    cardinality_ok = (n_units_done == expected_n_units)

    arms_differ = True
    arms_differ_detail = {}
    arms_differ_exempted = []
    for seed, hd in seed_pred_hashes.items():
        pairs = [(a, b) for a in ARMS for b in ARMS if a < b]
        for a, b in pairs:
            key = f"seed{seed}__{a}_vs_{b}"
            same = hd[a] == hd[b]
            arms_differ_detail[key] = not same
            if same:
                acc_a = per_seed_results[seed]["per_arm_acc"][a]
                acc_b = per_seed_results[seed]["per_arm_acc"][b]
                if acc_a > 0.95 and acc_b > 0.95:
                    arms_differ_exempted.append({"seed": seed, "pair": [a, b],
                                                  "rationale": "both near-ceiling; identical predictions "
                                                                "indicates ceiling-matching, not a bug",
                                                  "acc_a": acc_a, "acc_b": acc_b})
                else:
                    arms_differ = False

    def _m(vals):
        return float(np.mean(vals)) if vals else float("nan")

    arm_summary = {}
    for arm in ARMS:
        vals = [per_seed_results[s]["per_arm_acc"][arm] for s in seeds if s in per_seed_results]
        arm_summary[arm] = {"acc_mean": _m(vals), "acc_std": float(np.std(vals)) if len(vals) > 1 else 0.0,
                             "n_seeds": len(vals)}

    codebook_acc = arm_summary["codebook_derived"]["acc_mean"]
    ceiling_acc = arm_summary["handed_ceiling"]["acc_mean"]
    random_acc = arm_summary["random_code"]["acc_mean"]
    memorize_acc = arm_summary["memorize_prototype"]["acc_mean"]

    codebook_vs_random_margin = codebook_acc - random_acc
    codebook_vs_memorize_margin = codebook_acc - memorize_acc
    codebook_vs_ceiling_frac = (codebook_acc / ceiling_acc) if ceiling_acc > 1e-9 else 0.0

    discriminator_fires = (
        baseline_in_band
        and random_acc <= 0.05
        and codebook_vs_random_margin > 0.05
    )

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band:
        verdict = "HARD_FAIL_MECHANICS_SANITY_CEILING_CHECK_BELOW_BAND"
    elif (codebook_acc <= HF_CODEBOOK_FLOOR
          or codebook_vs_random_margin <= HF_CODEBOOK_VS_RANDOM_MARGIN
          or codebook_vs_memorize_margin <= HF_CODEBOOK_VS_MEMORIZE_MARGIN):
        verdict = "HARD_FAIL_NOVEL_ATOM_REAL_CODEBOOK_DOES_NOT_SURVIVE_COMPOSITION"
    elif (codebook_acc >= HP_CODEBOOK_ACC_MIN
          and codebook_vs_random_margin >= HP_CODEBOOK_VS_RANDOM_MARGIN
          and codebook_vs_memorize_margin >= HP_CODEBOOK_VS_MEMORIZE_MARGIN):
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"codebook_derived={codebook_acc:.3f} handed_ceiling={ceiling_acc:.3f} "
        f"random_code={random_acc:.3f} memorize_prototype={memorize_acc:.3f} "
        f"(chance={chance_floor:.5f}) | vs_random_margin={codebook_vs_random_margin:.3f} "
        f"vs_memorize_margin={codebook_vs_memorize_margin:.3f} vs_ceiling_frac={codebook_vs_ceiling_frac:.3f} "
        f"| ceiling_check(mechanics)={ceiling_check_mean:.3f} | discriminator_fires={discriminator_fires} "
        f"| cardinality_ok={cardinality_ok} ({n_units_done}/{expected_n_units}) arms_differ={arms_differ} "
        f"| V={V} F_NOVEL={f_novel} candidates={len(cand_idx)}"
    )

    novel_atom_diag_by_seed = {}
    for s in seeds:
        if s in per_seed_results:
            novel_atom_diag_by_seed[str(s)] = per_seed_results[s]["novel_atom_diagnostics"]

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:220]}", "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {**cfg, "N": N, "D_FEAT": D_FEAT, "RI_SPARSITY": RI_SPARSITY, "RIDGE_ALPHA": RIDGE_ALPHA,
                   "R_ROLES": R_ROLES, "ALPHA_FRAC": ALPHA_FRAC, "MIN_OCC_PER_DRAW": MIN_OCC_PER_DRAW,
                   "seeds": seeds, "V": V, "held_ranks": held_ranks, "held_counts": held_counts,
                   "n_seen": int(len(seen_idx)), "n_candidates": int(len(cand_idx))},
        "arm_summary": arm_summary,
        "ceiling_check_mechanics_acc_mean": ceiling_check_mean,
        "per_unit": per_unit,
        "novel_atom_diagnostics_by_seed": novel_atom_diag_by_seed,
        "bands": {"HP_CODEBOOK_ACC_MIN": HP_CODEBOOK_ACC_MIN,
                  "HP_CODEBOOK_VS_RANDOM_MARGIN": HP_CODEBOOK_VS_RANDOM_MARGIN,
                  "HP_CODEBOOK_VS_MEMORIZE_MARGIN": HP_CODEBOOK_VS_MEMORIZE_MARGIN,
                  "HF_CODEBOOK_FLOOR": HF_CODEBOOK_FLOOR,
                  "HF_CODEBOOK_VS_RANDOM_MARGIN": HF_CODEBOOK_VS_RANDOM_MARGIN,
                  "HF_CODEBOOK_VS_MEMORIZE_MARGIN": HF_CODEBOOK_VS_MEMORIZE_MARGIN,
                  "CEIL_CHECK_MIN": CEIL_CHECK_MIN, "CHANCE_FLOOR": chance_floor},
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units,
        "n_units_done": n_units_done, "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail, "arms_differ_exempted": arms_differ_exempted,
        "discriminator_fires": discriminator_fires, "baseline_in_band": baseline_in_band,
        "crlb_n/a": f"classification-accuracy generalization over C={len(cand_idx)} discrete candidates; "
                    f"closed-form chance floor = 1/C = {chance_floor:.5f} (THEORETICAL)",
        "prior_art": "LevyGoldberg2015 PPMI-SVD; ChurchHanks1990 PMI; Kanerva1988/Sahlgren2005 RI; "
                     "Khodak2018 a-la-carte; Snell2017 ProtoNet; Plate1995 HRR unitary vectors; "
                     "McClelland1995 CLS; GreffVanSteenkisteSchmidhuber2020",
        "integration_of": ["exp_learned_codebook_generalization_gate_v1 (real codebook CG, atom 29368, "
                           "AUC=0.927)", "atom 29380 (synthetic linear-construction-forced revival target)"],
        "honest_deviation_note": "memorize_prototype is NOT expected near-zero on real data (unlike the "
                                  "synthetic i.i.d.-atom cell) -- real vocabulary has genuine semantic-"
                                  "neighborhood structure; see docstring calibration note. random_code is "
                                  "the true chance/format-only floor.",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at tiny scale: exercises the REAL builders (no synthetic-only
    branch) -- tiny toy corpus, tiny V, tiny N (must stay even for unitary_hrr)."""
    global _COL_STATS, _R_FEAT
    print("[self-test] GUARD: unitary_hrr requires even dim; bind/unbind round trip", flush=True)
    tiny_N = 64
    role = unitary_hrr(2, tiny_N, seed=ROLE_SEED)
    filler = torch.randn(3, tiny_N)
    filler = filler / filler.norm(dim=-1, keepdim=True)
    b = bind(role[0].unsqueeze(0).expand(3, tiny_N), filler)
    rec = unbind(b, role[0].unsqueeze(0).expand(3, tiny_N))
    cos = (rec * filler).sum(dim=-1) / (rec.norm(dim=-1) * filler.norm(dim=-1))
    assert (cos > 0.99).all(), f"unitary-HRR bind/unbind round trip failed: cos={cos}"

    print("[self-test] real_code_path: exercising REAL tokenizer/vocab/cooc/ppmi/codebook builders",
          flush=True)
    base = (["cat", "pet", "feline", "purr", "whiskers"] * 8
            + ["dog", "pet", "canine", "bark", "loyal"] * 8
            + ["car", "road", "engine", "wheel", "drive"] * 8
            + ["king", "queen", "royal", "crown", "throne"] * 8
            + ["ship", "sail", "ocean", "captain", "anchor"] * 8)
    rng = np.random.default_rng(0)
    tokens = list(rng.permutation(base * 6))
    w2i, counts = build_vocab(tokens, vocab_size=50, min_count=1)
    V = len(w2i)
    assert V >= 15, f"toy vocab too small V={V}"
    ids = np.fromiter((w2i.get(t, -1) for t in tokens), dtype=np.int64, count=len(tokens))
    cooc = build_cooc(tokens, w2i, window=3)
    ppmi = build_ppmi(cooc)
    true_codes_np = build_codebook("ppmi_svd", cooc, ppmi, V, tiny_N, CODE_SEED, ri_sparsity=4)
    assert true_codes_np.shape == (V, tiny_N)
    assert np.all(np.isfinite(true_codes_np))

    R_feat = sparse_ternary_projection(V, 8, sparsity=4, seed=FEAT_PROJ_SEED)
    feat_full_all = (ppmi @ R_feat).toarray().astype(np.float64)
    nrm = np.linalg.norm(feat_full_all, axis=1, keepdims=True)
    nrm[nrm < 1e-12] = 1.0
    feat_full_all = feat_full_all / nrm
    col_sum_a, col_total_a = compute_ppmi_col_stats(cooc)

    print("[self-test] real_code_path: exercising partial-row builder + PPMI transform + ridge induction",
          flush=True)
    held = 0  # "cat" (first vocab entry by frequency)
    seen_idx = np.array([i for i in range(V) if i != held])
    X_train = feat_full_all[seen_idx]
    Y_train = true_codes_np[seen_idx]
    W = ridge_fit(X_train, Y_train, alpha=1.0)
    assert W.shape == (9, tiny_N)  # D_FEAT=8 + bias

    positions_held = np.where(ids == held)[0]
    assert len(positions_held) > 5, "toy corpus too small for a partial-row draw"
    subset = np.random.default_rng(1).choice(positions_held, size=max(5, len(positions_held) // 2),
                                              replace=False)
    raw_row = build_partial_cooc_row(ids, subset, V, window=3)
    assert raw_row.sum() > 0, "partial row is empty"
    feat = feat_from_raw_row(raw_row, R_feat, col_sum_a, col_total_a)
    pred = ridge_predict(W, feat[None, :])
    predn = pred / np.linalg.norm(pred, axis=1, keepdims=True)
    cos_true = float((predn[0] * true_codes_np[held]).sum())
    rand_vec = np.random.default_rng(2).standard_normal(tiny_N)
    rand_vec = rand_vec / np.linalg.norm(rand_vec)
    cos_rand = float((rand_vec * true_codes_np[held]).sum())
    print(f"[self-test] toy cos_derived_vs_true={cos_true:.4f} cos_random_vs_true={cos_rand:.4f}")
    # Not asserting cos_true > cos_rand strictly here: at this TINY toy scale (V~15-20, 1 held-out word,
    # D_FEAT=8) the induction map has almost no training signal -- this block exists to exercise the REAL
    # code path (Gate F.1), not to assert toy-scale accuracy (that is what --smoke is for).

    print("[self-test] real_code_path: exercising decode_scenes (bind+bundle+unbind+cleanup, real dtype)",
          flush=True)
    role_codes = unitary_hrr(3, tiny_N, seed=ROLE_SEED)
    true_codes_t = torch.from_numpy(true_codes_np).float()
    focal = true_codes_t[held].unsqueeze(0).expand(4, tiny_N).clone()
    other_idx = np.array([[1, 2], [2, 3], [1, 3], [3, 1]])
    other = true_codes_t[torch.from_numpy(other_idx)]
    cand_idx = np.arange(min(V, 10))
    cand_table = true_codes_t[torch.from_numpy(cand_idx)]
    preds = decode_scenes(focal, other, role_codes, cand_table)
    assert preds.shape == (4,)
    assert (preds == held).all(), f"handed-code decode should be exact on a clean toy world: preds={preds}"

    print("[self-test] real_code_path: exercising ceiling_check + arms-must-differ hash logic", flush=True)
    distractor_idx = np.array([i for i in range(1, min(V, 10))])
    cand_pos = {int(idx): pos for pos, idx in enumerate(cand_idx)}
    cc = ceiling_check(7, true_codes_t, seen_idx, distractor_idx, cand_pos, role_codes, cand_table,
                        n_scenes=10)
    assert 0.0 <= cc <= 1.0

    print("[self-test] PASS: real tokenizer/vocab/cooc/ppmi/codebook/ridge/partial-row/decode/ceiling all "
          f"exercised. toy cos_derived={cos_true:.4f} cos_random={cos_rand:.4f} handed-decode exact.",
          flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, SMOKE_CFG, SEEDS, run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, FULL_CFG, SEEDS, run_mode="full")
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
