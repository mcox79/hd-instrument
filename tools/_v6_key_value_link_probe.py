"""PRIORITY-1 encoder CLOSE (read-only, NO GPU, NO training, NO canonical writes):
the KEY->VALUE LINK test for the regime-switch encoder (coordinator B4 crux).

Regime-switch architecture:
  KEY   = a 2%-sparse HARD block code (K128, blk_l=32) with keyed@J5=1.00
          (source: v6 HARD_STE checkpoint; its BLOCK keyed@J5 = 1.00
           MEASURED@data/exp_encoder_v6_..._seed7/metrics.json per_unit).
  VALUE = the annealed dense readout (ret_agree10 ~ 0.64; source: v6 ANNEAL_STE
          checkpoint dense sign codes). Isotonic post-hoc only rescales VALUE
          cosine (order-preserving), so ret_agree10 of VALUE is identical with
          or without isotonic -- for this retrieval metric we use the raw dense
          value.

Test: store per-item (KEY, VALUE) associations; COMPOSE keys by binding each
item's sparse KEY with a random ROLE vector and bundling J of them
(bundle = sum_j bind(role_j, key_j)); UNBIND a query role to recover the KEY
POINTER; CLEANUP the recovered pointer against the KEY codebook to an item
index i'; then FOLLOW the pointer to VALUE[i'] and measure whether the
composed-key-addressed VALUE still retrieves correctly.

Reported per composition depth J in {1,2,3,4,5}:
  pointer_acc@J       = fraction of query items whose composed key recovers the
                        CORRECT item index (this is the SBC KEY algebra;
                        expected ~1.00 through J=5 since keyed@J5=1.00).
  composed_val_ret@J  = ret_agree10 of the composed-key-addressed VALUE:
                        mean over query items of top-10 overlap between
                        top10(VALUE[i'] vs VALUE codebook) and
                        top10(teacher[q] vs teacher codebook). If the pointer is
                        correct (i'==q) this contributes q's own value ret; if
                        wrong it contributes ~chance.
  baseline (J=0)      = un-composed VALUE ret_agree10 (reproduces ~0.64).

HARD-PASS (coordinator): composed key still recovers the right value at
composed_val_ret >= 0.35 through J >= 3. Same canonical held split + canonical
checkpoints as the v6 landing.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)

TEACHER_CACHE = "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"
KB, BLK_L = 128, 32          # v6 K=128 sparse KEY (3.125% active)
HIDDEN = 2048                # both HARD_STE (key) and ANNEAL_STE (value) width
J_DEPTHS = [1, 2, 3, 4, 5]
Q_SUB = 2000                 # query subsample (against the FULL held codebook)
HARDPASS_RET = 0.35
HARDPASS_MIN_J = 3


def _load_student(ckpt_path: Path, in_dim: int) -> torch.nn.Module:
    orig = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = HIDDEN
    try:
        student = v3._make_student("mlp", in_dim, KB * BLK_L, "cpu", seed=0)
    finally:
        v3.MLP_HIDDEN = orig
    ck = torch.load(str(ckpt_path), map_location="cpu")
    student.load_state_dict(ck["student"])
    student.eval()
    return student


def _top10(query_norm: torch.Tensor, cb_norm: torch.Tensor, self_idx: torch.Tensor,
           chunk: int = 1024) -> torch.Tensor:
    """top-10 codebook indices per query row, excluding the query's own index."""
    nq = query_norm.shape[0]
    out = torch.zeros(nq, 10, dtype=torch.long)
    for lo in range(0, nq, chunk):
        hi = min(lo + chunk, nq)
        sims = query_norm[lo:hi] @ cb_norm.T
        rows = torch.arange(lo, hi)
        sims[torch.arange(hi - lo), self_idx[lo:hi]] = -2.0
        out[lo:hi] = sims.topk(10, dim=1).indices
    return out


def _agree10(idx_a: torch.Tensor, idx_b: torch.Tensor) -> float:
    n = idx_a.shape[0]
    s = 0.0
    for r in range(n):
        s += len(set(idx_a[r].tolist()) & set(idx_b[r].tolist())) / 10.0
    return s / n


def run(seed: int) -> int:
    torch.manual_seed(seed)
    cache_path = v3._resolve_teacher_cache(TEACHER_CACHE)
    X, ids = v3._load_teacher(cache_path)
    V = X.shape[0]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(V)
    n_he = min(int(round(V * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    n_tr = V - n_he
    he_idx = perm[n_tr:n_tr + n_he]
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    M = Xhe.shape[0]
    print(f"[link] seed={seed} teacher={cache_path.name} V={V} held M={M}", flush=True)

    key_ckpt = (_REPO / "data" / f"substrate_concept_encoder_v6_annealste_seed{seed}"
                / "_ckpt_HARD_STE.pt")
    val_ckpt = (_REPO / "data" / f"substrate_concept_encoder_v6_annealste_seed{seed}"
                / "_ckpt_ANNEAL_STE.pt")
    for p in (key_ckpt, val_ckpt):
        if not p.exists():
            print(f"[link] FATAL: checkpoint not found: {p}", flush=True)
            return 3

    key_student = _load_student(key_ckpt, Xhe.shape[1])
    val_student = _load_student(val_ckpt, Xhe.shape[1])
    KEY = v3._encode_hard_block(key_student, Xhe, KB, BLK_L)   # (M, 4096) sparse block KEY
    VALUE = v3._dense_sign_codes(val_student, Xhe)             # (M, 4096) dense VALUE
    print(f"[link] KEY=HARD_STE block (keyed@J5=1.00 source) VALUE=ANNEAL_STE dense "
          f"(ret~0.64 source)", flush=True)

    val_n = VALUE / (VALUE.norm(dim=-1, keepdim=True) + 1e-8)
    Xhe_n = Xhe / (Xhe.norm(dim=-1, keepdim=True) + 1e-8)

    # Query subsample + precomputed neighbor sets.
    qsub = torch.from_numpy(rng.choice(M, size=min(Q_SUB, M), replace=False))
    self_all = torch.arange(M)
    teacher_top10_q = _top10(Xhe_n[qsub], Xhe_n, qsub)           # teacher neighbors of q
    value_top10_q = _top10(val_n[qsub], val_n, qsub)             # value neighbors of q (baseline)

    base_ret = _agree10(value_top10_q, teacher_top10_q)
    print(f"[link] BASELINE (J=0, un-composed) value ret_agree10 = {base_ret:.4f} "
          f"(reproduces ~0.64) n_q={qsub.shape[0]}", flush=True)

    KEY3 = KEY.reshape(M, KB, BLK_L)
    gen = torch.Generator().manual_seed(seed + 71)
    results = {}
    for J in J_DEPTHS:
        key_ests = torch.zeros(qsub.shape[0], KB * BLK_L)
        for r, q in enumerate(qsub.tolist()):
            # distractors: J-1 other held items (never q)
            if J > 1:
                dr = rng.choice(M, size=J - 1, replace=False)
                dr = dr[dr != q][:J - 1]
                while dr.shape[0] < J - 1:
                    extra = rng.integers(0, M)
                    if extra != q and extra not in dr:
                        dr = np.append(dr, extra)
                fi = np.concatenate([[q], dr])
            else:
                fi = np.array([q])
            roles = v3._random_block_codes(J, KB, BLK_L, gen).reshape(J, KB, BLK_L)
            bundle = torch.zeros(KB, BLK_L)
            for j in range(J):
                bundle = bundle + v3.bind(roles[j], KEY3[int(fi[j])])
            qj = 0  # q is always at position 0 in fi
            key_ests[r] = v3.unbind(bundle, roles[qj]).reshape(KB * BLK_L)
        pred, best, second = v3._chunked_cleanup_argmax(key_ests, KEY, "cpu")
        pointer_acc = float((pred == qsub).float().mean())

        # Follow pointers to VALUE[i'] and measure its retrieval vs q's teacher.
        recovered_val_n = val_n[pred]                          # (n_q, 4096)
        # top10 of the RECOVERED value against the full value codebook, excluding
        # the recovered item's own index (self-exclusion by pred, matching q's).
        rec_val_top10 = _top10(recovered_val_n, val_n, pred)
        composed_ret = _agree10(rec_val_top10, teacher_top10_q)
        results[J] = (pointer_acc, composed_ret)
        print(f"[link] J={J}: pointer_acc={pointer_acc:.4f} "
              f"composed_val_ret_agree10={composed_ret:.4f} "
              f"snr_margin={float((best - second).mean()):.4f}", flush=True)

    ok_js = [J for J in J_DEPTHS if J >= HARDPASS_MIN_J and results[J][1] >= HARDPASS_RET]
    hardpass = all(results[J][1] >= HARDPASS_RET for J in J_DEPTHS if J >= HARDPASS_MIN_J)
    print(f"[RESULT] seed={seed} base_ret={base_ret:.4f} "
          + " ".join(f"J{J}=(ptr{results[J][0]:.3f},val{results[J][1]:.3f})"
                     for J in J_DEPTHS)
          + f" HARDPASS_ret>=0.35_through_J>=3={hardpass}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    return run(args.seed)


if __name__ == "__main__":
    sys.exit(main())
