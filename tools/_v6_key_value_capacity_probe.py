"""PRIORITY-1 CAPACITY ENVELOPE for the KEY->VALUE regime-switch link
(read-only, NO GPU, NO training, NO canonical writes). Stresses the LINK test
(tools/_v6_key_value_link_probe.py) toward the real operating point to find the
composition-depth / codebook-size CLIFF.

Three stressors (coordinator, 2026-07-04):
  (a) scale M (codebook size) from the 17790-held pool toward the FULL 177899
      concepts (real, semantically-clustered keys as distractors);
  (b) push composition depth J beyond 5 until the SBC bundle SNR margin crosses
      zero and pointer recovery breaks;
  (c) NEAR-NEIGHBOR co-bundling: co-bundle each query with its J-1 nearest
      TEACHER-neighbors (their sparse KEYS may collide under composition) rather
      than random well-separated items -- the realistic worst case.

KEY = v6 HARD_STE 2%-sparse block code (keyed@J5=1.00 source). VALUE = v6
ANNEAL_STE dense readout (ret~0.64). All 177899 concepts encoded once; smaller M
codebooks are random subsets that always CONTAIN the query items.

Reported per (M, J, co-bundle mode): pointer_acc, composed_val_ret_agree10,
snr_margin, and baseline (un-composed) val_ret at that M. HARD-PASS floor =
composed_val_ret >= 0.35. The (M, J) where it first crosses below 0.35 is the
capacity envelope.

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
KB, BLK_L = 128, 32
HIDDEN = 2048
HARDPASS_RET = 0.35
DEVICE = "cpu"  # force CPU to avoid contending with the running K455 GPU job


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


def _top10_excl_self(query_n: torch.Tensor, cb_n: torch.Tensor,
                     self_row: torch.Tensor, chunk: int = 512) -> torch.Tensor:
    nq = query_n.shape[0]
    out = torch.zeros(nq, 10, dtype=torch.long)
    for lo in range(0, nq, chunk):
        hi = min(lo + chunk, nq)
        sims = query_n[lo:hi] @ cb_n.T
        sims[torch.arange(hi - lo), self_row[lo:hi]] = -2.0
        out[lo:hi] = sims.topk(10, dim=1).indices
    return out


def _agree10(a: torch.Tensor, b: torch.Tensor) -> float:
    n = a.shape[0]
    s = 0.0
    for r in range(n):
        s += len(set(a[r].tolist()) & set(b[r].tolist())) / 10.0
    return s / n


def _cleanup_argmax(Q: torch.Tensor, cb: torch.Tensor, chunk: int = 4096):
    """cosine argmax + top2 margin of Q rows against codebook cb."""
    qn = Q / (Q.norm(dim=-1, keepdim=True) + 1e-8)
    cbn = cb / (cb.norm(dim=-1, keepdim=True) + 1e-8)
    nq = Q.shape[0]
    best = torch.full((nq,), -2.0)
    second = torch.full((nq,), -2.0)
    best_i = torch.zeros(nq, dtype=torch.long)
    for lo in range(0, cb.shape[0], chunk):
        sims = qn @ cbn[lo:lo + chunk].T
        top2 = sims.topk(min(2, sims.shape[1]), dim=1)
        v1 = top2.values[:, 0]
        i1 = top2.indices[:, 0] + lo
        v2 = top2.values[:, 1] if sims.shape[1] > 1 else torch.full((nq,), -2.0)
        upd = v1 > best
        second = torch.where(upd, torch.maximum(best, v2), torch.maximum(second, v1))
        best_i = torch.where(upd, i1, best_i)
        best = torch.where(upd, v1, best)
    return best_i, best, second


def run(seed: int, n_queries: int) -> int:
    torch.manual_seed(seed)
    cache_path = v3._resolve_teacher_cache(TEACHER_CACHE)
    X, ids = v3._load_teacher(cache_path)
    Vtot = X.shape[0]
    rng = np.random.default_rng(seed)

    print(f"[cap] seed={seed} teacher={cache_path.name} V={Vtot} encoding all keys+values "
          f"(one pass each; may take ~1-2 min CPU)...", flush=True)
    key_ckpt = (_REPO / "data" / f"substrate_concept_encoder_v6_annealste_seed{seed}"
                / "_ckpt_HARD_STE.pt")
    val_ckpt = (_REPO / "data" / f"substrate_concept_encoder_v6_annealste_seed{seed}"
                / "_ckpt_ANNEAL_STE.pt")
    for p in (key_ckpt, val_ckpt):
        if not p.exists():
            print(f"[cap] FATAL: checkpoint missing: {p}", flush=True)
            return 3
    KEY = v3._encode_hard_block(_load_student(key_ckpt, X.shape[1]), X, KB, BLK_L)
    VALUE = v3._dense_sign_codes(_load_student(val_ckpt, X.shape[1]), X)
    Xn = X / (X.norm(dim=-1, keepdim=True) + 1e-8)
    val_n = VALUE / (VALUE.norm(dim=-1, keepdim=True) + 1e-8)
    print(f"[cap] encoded KEY{tuple(KEY.shape)} VALUE{tuple(VALUE.shape)}", flush=True)

    # Query set: held items (never in the train set), fixed across the sweep.
    perm = rng.permutation(Vtot)
    n_he = min(int(round(Vtot * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    held = perm[Vtot - n_he:]
    q_glob = rng.choice(held, size=min(n_queries, len(held)), replace=False)
    nq = len(q_glob)
    print(f"[cap] n_queries={nq} (held); HARD-PASS floor composed_val_ret>=0.35\n", flush=True)

    M_LIST = [17790, 50000, 177899]
    J_LIST = [2, 5, 10, 20, 40, 64, 100]

    def build_codebook(M: int):
        M = min(M, Vtot)
        rest = np.setdiff1d(np.arange(Vtot), q_glob, assume_unique=False)
        n_extra = max(0, M - nq)
        extra = rng.choice(rest, size=min(n_extra, len(rest)), replace=False)
        cb_idx = np.concatenate([q_glob, extra])
        rng.shuffle(cb_idx)
        cb_idx = cb_idx[:M]
        # ensure all queries present
        missing = np.setdiff1d(q_glob, cb_idx)
        if len(missing):
            cb_idx = np.concatenate([cb_idx[:M - len(missing)], missing])
        pos = {int(g): r for r, g in enumerate(cb_idx.tolist())}
        q_row = torch.tensor([pos[int(g)] for g in q_glob])
        return torch.from_numpy(cb_idx.copy()), q_row

    def sweep(M: int, J_list, mode: str):
        cb_idx, q_row = build_codebook(M)
        KEY_cb = KEY[cb_idx]
        KEY_cb3 = KEY_cb.reshape(KEY_cb.shape[0], KB, BLK_L)
        VAL_cb_n = val_n[cb_idx]
        X_cb_n = Xn[cb_idx]
        teacher_top10 = _top10_excl_self(Xn[torch.from_numpy(q_glob.copy())], X_cb_n, q_row)
        base_top10 = _top10_excl_self(val_n[torch.from_numpy(q_glob.copy())], VAL_cb_n, q_row)
        base_val_ret = _agree10(base_top10, teacher_top10)
        # near-neighbor pool: for each query, its nearest teacher-neighbors WITHIN cb
        nn_pool = None
        if mode == "nn":
            nn_pool = _top10_excl_self(Xn[torch.from_numpy(q_glob.copy())], X_cb_n, q_row,
                                       chunk=512)  # 10 nearest; enough for J<=11
        print(f"[cap] M={M} mode={mode} baseline(J=0) val_ret={base_val_ret:.4f}", flush=True)
        gen = torch.Generator().manual_seed(seed + 137 + M % 1000)
        for J in J_list:
            key_ests = torch.zeros(nq, KB * BLK_L)
            for r in range(nq):
                qrow = int(q_row[r])
                if J == 1:
                    fi = [qrow]
                elif mode == "nn":
                    pool = [int(x) for x in nn_pool[r].tolist() if int(x) != qrow]
                    while len(pool) < J - 1:
                        cand = int(rng.integers(0, KEY_cb.shape[0]))
                        if cand != qrow and cand not in pool:
                            pool.append(cand)
                    fi = [qrow] + pool[:J - 1]
                else:  # random distractors
                    picks = []
                    while len(picks) < J - 1:
                        cand = int(rng.integers(0, KEY_cb.shape[0]))
                        if cand != qrow and cand not in picks:
                            picks.append(cand)
                    fi = [qrow] + picks
                roles = v3._random_block_codes(J, KB, BLK_L, gen).reshape(J, KB, BLK_L)
                bundle = torch.zeros(KB, BLK_L)
                for j in range(J):
                    bundle = bundle + v3.bind(roles[j], KEY_cb3[fi[j]])
                key_ests[r] = v3.unbind(bundle, roles[0]).reshape(KB * BLK_L)
            pred, best, second = _cleanup_argmax(key_ests, KEY_cb)
            ptr_acc = float((pred == q_row).float().mean())
            rec_top10 = _top10_excl_self(VAL_cb_n[pred], VAL_cb_n, pred)
            comp_ret = _agree10(rec_top10, teacher_top10)
            flag = "" if comp_ret >= HARDPASS_RET else "  <-- BELOW 0.35 HARD-PASS"
            print(f"[cap]   J={J:3d}: pointer_acc={ptr_acc:.4f} "
                  f"composed_val_ret={comp_ret:.4f} snr_margin={float((best-second).mean()):+.4f}"
                  f"{flag}", flush=True)
        print("", flush=True)
        return base_val_ret

    print("=== SWEEP 1: full real codebook M=177899, near-neighbor co-bundle, J-depth ===",
          flush=True)
    sweep(177899, J_LIST, "nn")
    print("=== SWEEP 2: M-scaling at fixed J=20, near-neighbor co-bundle ===", flush=True)
    for M in M_LIST:
        sweep(M, [20], "nn")
    print("=== SWEEP 3: near-neighbor vs random co-bundle contrast at M=177899, J=20,40 ===",
          flush=True)
    sweep(177899, [20, 40], "random")
    print("[cap] DONE. The (M,J) where composed_val_ret first drops below 0.35 is the "
          "capacity envelope.", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n-queries", type=int, default=500)
    args = ap.parse_args()
    return run(args.seed, args.n_queries)


if __name__ == "__main__":
    sys.exit(main())
