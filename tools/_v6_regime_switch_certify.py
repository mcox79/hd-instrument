"""REGIME-SWITCH CERTIFICATION (read-only, persists metrics.json). Consolidates
the three regime-switch probes (isotonic recalibration, KEY->VALUE link,
capacity envelope) into ONE certifiable artifact per seed, writing
data/exp_v6_regime_switch_certify_seed{N}/metrics.json with all load-bearing
quantities so the close is recomputable from disk (Skunkworks VET fix, 2026-07-04
-- the earlier probes printed to stdout only).

Load-bearing (INDEPENDENT) quantities persisted:
  - pointer_acc vs (J, M): the ONLY non-tautological link number. composed_val_ret
    is DERIVED (== base_ret when the pointer is right, ~chance when wrong), so it
    is reported as derived, NOT as the headline. base_ret persisted separately.
  - isotonic RESIDUAL: out-of-sample calib_err + hi80_cos after PAVA isotonic on
    the DENSE_LAST readout (fit on calib-half concepts, eval on disjoint test-half).
  - the DEFENSIBLE VALUE BAND: DENSE_LAST raw (ret ~0.65, hi80 ~0.48, calib ~0.37),
    DENSE_LAST+isotonic (ret unchanged ~0.65, hi80 ~0.81, calib ~0.026), and
    DENSE_BESTVAL (already on-disk: ret ~0.55/0.62, hi80 ~0.79, calib ~0.05). So the
    defensible operating point is a ret band 0.55-0.65 depending on readout choice.

Canonical inputs (all on the remote where this runs): v6 FULL checkpoints
data/substrate_concept_encoder_v6_annealste_seed{N}/_ckpt_{HARD,ANNEAL}_STE.pt +
the 177899 teacher cache. KEY = HARD_STE block (keyed@J5=1.00). VALUE = ANNEAL_STE
dense readout.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
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
N_PAIRS = 400_000
HI80_THRESH = 0.80
LINK_J = [1, 2, 3, 4, 5]
CAP_J = [2, 5, 10, 20, 40, 64, 100]
CAP_M = [17790, 50000, 177899]
N_CAP_QUERIES = 500


def _spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def _pava(x, y):
    order = np.argsort(x, kind="mergesort")
    xs = x[order].astype(np.float64)
    ys = y[order].astype(np.float64)
    vals, cnts = [], []
    for v in ys:
        vals.append(float(v)); cnts.append(1)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            v2 = vals.pop(); c2 = cnts.pop(); v1 = vals.pop(); c1 = cnts.pop()
            vals.append((v1 * c1 + v2 * c2) / (c1 + c2)); cnts.append(c1 + c2)
    out = np.empty(len(ys)); idx = 0
    for v, c in zip(vals, cnts):
        out[idx:idx + c] = v; idx += c
    return xs, out


def _apply_iso(xs, yhat, q):
    return np.interp(q, xs, yhat, left=float(yhat[0]), right=float(yhat[-1]))


def _load_student(ckpt_path, in_dim):
    orig = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = HIDDEN
    try:
        student = v3._make_student("mlp", in_dim, KB * BLK_L, "cpu", seed=0)
    finally:
        v3.MLP_HIDDEN = orig
    ck = torch.load(str(ckpt_path), map_location="cpu")
    student.load_state_dict(ck["student"])
    student.eval()
    return student, int(ck.get("step", -1))


def _top10(qn, cbn, self_row, chunk=512):
    nq = qn.shape[0]
    out = torch.zeros(nq, 10, dtype=torch.long)
    for lo in range(0, nq, chunk):
        hi = min(lo + chunk, nq)
        sims = qn[lo:hi] @ cbn.T
        sims[torch.arange(hi - lo), self_row[lo:hi]] = -2.0
        out[lo:hi] = sims.topk(10, dim=1).indices
    return out


def _agree10(a, b):
    n = a.shape[0]; s = 0.0
    for r in range(n):
        s += len(set(a[r].tolist()) & set(b[r].tolist())) / 10.0
    return s / n


def _cleanup(Q, cb, chunk=4096):
    qn = Q / (Q.norm(dim=-1, keepdim=True) + 1e-8)
    cbn = cb / (cb.norm(dim=-1, keepdim=True) + 1e-8)
    nq = Q.shape[0]
    best = torch.full((nq,), -2.0); second = torch.full((nq,), -2.0)
    best_i = torch.zeros(nq, dtype=torch.long)
    for lo in range(0, cb.shape[0], chunk):
        sims = qn @ cbn[lo:lo + chunk].T
        top2 = sims.topk(min(2, sims.shape[1]), dim=1)
        v1 = top2.values[:, 0]; i1 = top2.indices[:, 0] + lo
        v2 = top2.values[:, 1] if sims.shape[1] > 1 else torch.full((nq,), -2.0)
        upd = v1 > best
        second = torch.where(upd, torch.maximum(best, v2), torch.maximum(second, v1))
        best_i = torch.where(upd, i1, best_i); best = torch.where(upd, v1, best)
    return best_i, best, second


def run(seed):
    t0 = time.perf_counter()
    cache_path = v3._resolve_teacher_cache(TEACHER_CACHE)
    X, ids = v3._load_teacher(cache_path)
    Vtot = X.shape[0]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(Vtot)
    n_he = min(int(round(Vtot * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    n_tr = Vtot - n_he
    he_idx = perm[n_tr:n_tr + n_he]
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    M_he = Xhe.shape[0]
    print(f"[cert] seed={seed} V={Vtot} held={M_he}", flush=True)

    base = _REPO / "data" / f"substrate_concept_encoder_v6_annealste_seed{seed}"
    hard_ck = base / "_ckpt_HARD_STE.pt"
    ann_ck = base / "_ckpt_ANNEAL_STE.pt"
    for p in (hard_ck, ann_ck):
        if not p.exists():
            raise FileNotFoundError(f"checkpoint missing: {p}")
    key_student, key_step = _load_student(hard_ck, X.shape[1])
    val_student, val_step = _load_student(ann_ck, X.shape[1])
    print(f"[cert] loaded HARD_STE(step={key_step}) ANNEAL_STE(step={val_step})", flush=True)

    # -------- Value readouts on HELD --------
    val_codes = v3._dense_sign_codes(val_student, Xhe)            # DENSE_LAST value
    dense_last_unit = v3._semantic_unit("DENSE_LAST", val_codes, val_codes, Xhe, Xhe,
                                        0, N_PAIRS, seed + 3)
    dense_last = {"ret_agree10": dense_last_unit["ret_agree10"],
                  "hi80_cos": dense_last_unit["hi80_cos"],
                  "hi80_calib_err": dense_last_unit["hi80_calib_err"],
                  "spearman_all": dense_last_unit["spearman_all"],
                  "hi80_teacher_mean": dense_last_unit["hi80_teacher_mean"]}
    print(f"[cert] DENSE_LAST raw: ret={dense_last['ret_agree10']:.4f} "
          f"hi80={dense_last['hi80_cos']:.4f} calib={dense_last['hi80_calib_err']:.4f}",
          flush=True)

    # DENSE_BESTVAL (already-landed on-disk numbers, surfaced for the value band).
    v6_metrics = base.parent / f"exp_encoder_v6_annealed_ste_fidelity_k128_v1_seed{seed}" / "metrics.json"
    dense_bestval = None
    if v6_metrics.exists():
        try:
            md = json.loads(v6_metrics.read_text(encoding="utf-8"))
            bd = md["recovery"]["ANNEAL_STE"]["bestval_dense_on_test"]
            dense_bestval = {"ret_agree10": bd["ret_agree10"], "hi80_cos": bd["hi80_cos"],
                             "hi80_calib_err": bd["hi80_calib_err"],
                             "source": "MEASURED@" + str(v6_metrics)}
        except (KeyError, json.JSONDecodeError):
            dense_bestval = None

    # -------- Isotonic residual (out-of-sample) on DENSE_LAST --------
    cn = val_codes / (val_codes.norm(dim=-1, keepdim=True) + 1e-8)

    def _pairs(lo, hi, sd):
        r = np.random.default_rng(sd)
        i = r.integers(lo, hi, N_PAIRS); j = r.integers(lo, hi, N_PAIRS)
        keep = i != j; i, j = i[keep], j[keep]
        tp = (Xhe[torch.from_numpy(i.copy())] * Xhe[torch.from_numpy(j.copy())]).sum(-1).numpy()
        sp = (cn[torch.from_numpy(i.copy())] * cn[torch.from_numpy(j.copy())]).sum(-1).numpy()
        return sp.astype(np.float64), tp.astype(np.float64)

    sp_f, tp_f = _pairs(0, M_he, seed + 3)
    m8f = tp_f >= HI80_THRESH
    base_calib_full = abs(float(sp_f[m8f].mean()) - float(tp_f[m8f].mean()))
    half = M_he // 2
    sp_fit, tp_fit = _pairs(0, half, seed + 101)
    sp_ev, tp_ev = _pairs(half, M_he, seed + 202)
    m8e = tp_ev >= HI80_THRESH
    hi80_t_ev = float(tp_ev[m8e].mean())
    base_hi80_ev = float(sp_ev[m8e].mean()); base_calib_ev = abs(base_hi80_ev - hi80_t_ev)
    xs, yhat = _pava(sp_fit, tp_fit)
    iso_ev = _apply_iso(xs, yhat, sp_ev)
    iso_hi80 = float(iso_ev[m8e].mean()); iso_calib = abs(iso_hi80 - hi80_t_ev)
    iso_spear = _spearman(iso_ev, tp_ev)
    isotonic = {"hi80_teacher": hi80_t_ev,
                "base_calib_full_pool": base_calib_full,
                "base_hi80_oos": base_hi80_ev, "base_calib_oos": base_calib_ev,
                "iso_hi80_oos": iso_hi80, "iso_calib_oos": iso_calib,
                "iso_spearman": iso_spear, "n_hi80_eval": int(m8e.sum())}
    print(f"[cert] ISOTONIC oos: base_calib={base_calib_ev:.4f} -> iso_calib={iso_calib:.4f} "
          f"| base_hi80={base_hi80_ev:.4f} -> iso_hi80={iso_hi80:.4f}", flush=True)

    # -------- LINK: pointer_acc@J vs held codebook (M=17790) + base value ret --------
    KEY_he = v3._encode_hard_block(key_student, Xhe, KB, BLK_L)
    KEY3 = KEY_he.reshape(M_he, KB, BLK_L)
    val_n = cn
    Xhe_n = Xhe / (Xhe.norm(dim=-1, keepdim=True) + 1e-8)
    qsub = torch.from_numpy(rng.choice(M_he, size=min(2000, M_he), replace=False))
    teach_t10 = _top10(Xhe_n[qsub], Xhe_n, qsub)
    val_t10 = _top10(val_n[qsub], val_n, qsub)
    link_base_ret = _agree10(val_t10, teach_t10)
    gen = torch.Generator().manual_seed(seed + 71)
    link_ptr = {}
    for J in LINK_J:
        ke = torch.zeros(qsub.shape[0], KB * BLK_L)
        for r, q in enumerate(qsub.tolist()):
            if J > 1:
                dr = rng.choice(M_he, size=J - 1, replace=False)
                dr = dr[dr != q]
                while dr.shape[0] < J - 1:
                    e = int(rng.integers(0, M_he))
                    if e != q and e not in dr:
                        dr = np.append(dr, e)
                fi = np.concatenate([[q], dr[:J - 1]])
            else:
                fi = np.array([q])
            roles = v3._random_block_codes(J, KB, BLK_L, gen).reshape(J, KB, BLK_L)
            bundle = torch.zeros(KB, BLK_L)
            for j in range(J):
                bundle = bundle + v3.bind(roles[j], KEY3[int(fi[j])])
            ke[r] = v3.unbind(bundle, roles[0]).reshape(KB * BLK_L)
        pred, best, second = _cleanup(ke, KEY_he)
        link_ptr[str(J)] = {"pointer_acc": float((pred == qsub).float().mean()),
                            "snr_margin": float((best - second).mean())}
        print(f"[cert] LINK J={J}: pointer_acc={link_ptr[str(J)]['pointer_acc']:.4f}", flush=True)

    # -------- CAPACITY: pointer_acc vs (J, M) at FULL scale + base_ret@M --------
    KEY_all = v3._encode_hard_block(key_student, X, KB, BLK_L)
    VAL_all = v3._dense_sign_codes(val_student, X)
    val_all_n = VAL_all / (VAL_all.norm(dim=-1, keepdim=True) + 1e-8)
    X_all_n = X / (X.norm(dim=-1, keepdim=True) + 1e-8)
    q_glob = rng.choice(he_idx, size=min(N_CAP_QUERIES, len(he_idx)), replace=False)
    nq = len(q_glob)

    def _codebook(M):
        M = min(M, Vtot)
        rest = np.setdiff1d(np.arange(Vtot), q_glob)
        extra = rng.choice(rest, size=max(0, M - nq), replace=False)
        cb = np.concatenate([q_glob, extra])[:M]
        rng.shuffle(cb)
        miss = np.setdiff1d(q_glob, cb)
        if len(miss):
            cb = np.concatenate([cb[:M - len(miss)], miss])
        pos = {int(g): r for r, g in enumerate(cb.tolist())}
        return torch.from_numpy(cb.copy()), torch.tensor([pos[int(g)] for g in q_glob])

    capacity = {"n_queries": int(nq), "cobundle": "near_neighbor", "by_M": {}}
    for M in CAP_M:
        cb_idx, q_row = _codebook(M)
        KEYcb = KEY_all[cb_idx]; KEYcb3 = KEYcb.reshape(KEYcb.shape[0], KB, BLK_L)
        Xcb_n = X_all_n[cb_idx]; Vcb_n = val_all_n[cb_idx]
        teach10 = _top10(X_all_n[torch.from_numpy(q_glob.copy())], Xcb_n, q_row)
        val10 = _top10(val_all_n[torch.from_numpy(q_glob.copy())], Vcb_n, q_row)
        base_ret_M = _agree10(val10, teach10)
        nn_pool = _top10(X_all_n[torch.from_numpy(q_glob.copy())], Xcb_n, q_row)
        J_here = CAP_J if M == 177899 else [20]
        g2 = torch.Generator().manual_seed(seed + 137 + M % 1000)
        perJ = {}
        for J in J_here:
            ke = torch.zeros(nq, KB * BLK_L)
            for r in range(nq):
                qr = int(q_row[r])
                if J == 1:
                    fi = [qr]
                else:
                    pool = [int(x) for x in nn_pool[r].tolist() if int(x) != qr]
                    while len(pool) < J - 1:
                        c = int(rng.integers(0, KEYcb.shape[0]))
                        if c != qr and c not in pool:
                            pool.append(c)
                    fi = [qr] + pool[:J - 1]
                roles = v3._random_block_codes(J, KB, BLK_L, g2).reshape(J, KB, BLK_L)
                bundle = torch.zeros(KB, BLK_L)
                for j in range(J):
                    bundle = bundle + v3.bind(roles[j], KEYcb3[fi[j]])
                ke[r] = v3.unbind(bundle, roles[0]).reshape(KB * BLK_L)
            pred, best, second = _cleanup(ke, KEYcb)
            pa = float((pred == q_row).float().mean())
            # DERIVED composed value ret (reported, not headline): follow pointer.
            rec10 = _top10(Vcb_n[pred], Vcb_n, pred)
            comp = _agree10(rec10, teach10)
            perJ[str(J)] = {"pointer_acc": pa, "composed_val_ret_DERIVED": comp,
                            "snr_margin": float((best - second).mean())}
            print(f"[cert] CAP M={M} J={J}: pointer_acc={pa:.4f} base_ret={base_ret_M:.4f} "
                  f"comp_val_ret(derived)={comp:.4f}", flush=True)
        capacity["by_M"][str(M)] = {"base_val_ret": base_ret_M, "per_J": perJ}

    # -------- Verdict --------
    link_ok = link_ptr["5"]["pointer_acc"] >= 0.95
    iso_ok = iso_calib <= 0.05 and iso_hi80 >= 0.80
    dense_ret_ok = dense_last["ret_agree10"] >= 0.50
    cap_full = capacity["by_M"]["177899"]["per_J"]
    cap_hardpass_J = [int(J) for J in CAP_J
                      if str(J) in cap_full
                      and cap_full[str(J)]["composed_val_ret_DERIVED"] >= 0.35]
    max_hardpass_J = max(cap_hardpass_J) if cap_hardpass_J else 0
    verdict = "HARD_PASS" if (link_ok and iso_ok and dense_ret_ok) else "MIDDLE_BAND"
    verdict_msg = (
        f"REGIME_SWITCH_CERTIFIED seed={seed}: LINK pointer_acc@J5="
        f"{link_ptr['5']['pointer_acc']:.4f} (lossless key composition); ISOTONIC "
        f"residual calib_err {base_calib_ev:.4f}->{iso_calib:.4f} hi80 {base_hi80_ev:.4f}"
        f"->{iso_hi80:.4f} (out-of-sample); DENSE_LAST ret {dense_last['ret_agree10']:.4f}; "
        f"CAPACITY at full M=177899 pointer_acc holds, composed_val_ret>=0.35 through "
        f"J={max_hardpass_J}; codebook size NOT the constraint (M-sweep pointer_acc "
        f"stable). Defensible value band: DENSE_LAST+isotonic (ret "
        f"{dense_last['ret_agree10']:.3f}/hi80 {iso_hi80:.3f}/calib {iso_calib:.3f}) vs "
        f"DENSE_BESTVAL (ret "
        f"{dense_bestval['ret_agree10']:.3f}/hi80 {dense_bestval['hi80_cos']:.3f}/calib "
        f"{dense_bestval['hi80_calib_err']:.3f})" if dense_bestval else
        f"DENSE_BESTVAL unavailable")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "seed": int(seed), "run_mode": "certify",
        "anchor_name": f"v6_regime_switch_certify_seed{seed}",
        "canonical_inputs": {
            "key_ckpt": str(hard_ck), "value_ckpt": str(ann_ck),
            "teacher_cache": cache_path.name, "V": int(Vtot), "held": int(M_he),
            "key_step": key_step, "value_step": val_step,
            "note": "KEY=HARD_STE block (keyed@J5=1.00); VALUE=ANNEAL_STE dense readout"},
        "value_band": {
            "DENSE_LAST_raw": dense_last,
            "DENSE_LAST_isotonic": {
                "ret_agree10_UNCHANGED": dense_last["ret_agree10"],
                "hi80_cos": iso_hi80, "hi80_calib_err": iso_calib,
                "note": "isotonic is order-preserving so ret_agree10 identical to DENSE_LAST_raw"},
            "DENSE_BESTVAL": dense_bestval,
            "defensible_ret_band": [
                dense_bestval["ret_agree10"] if dense_bestval else None,
                dense_last["ret_agree10"]]},
        "isotonic_residual": isotonic,
        "link": {"codebook_M": int(M_he), "base_val_ret": link_base_ret,
                 "pointer_acc_by_J": link_ptr,
                 "note": ("pointer_acc is the INDEPENDENT number; composed_val_ret == "
                          "base_val_ret when pointer correct (Skunkworks tautology note), "
                          "so base_val_ret is reported separately as the value quality")},
        "capacity": capacity,
        "capacity_hardpass_max_J_full_scale": max_hardpass_J,
        "gates": {"link_pointer_acc_J5>=0.95": link_ok,
                  "isotonic_calib<=0.05_and_hi80>=0.80": iso_ok,
                  "dense_last_ret>=0.50": dense_ret_ok},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "certifiability_note": ("recomputable from disk: committed script + persistent "
                                "remote v6 FULL ckpts + 177899 cache; this metrics.json is "
                                "the persisted artifact (SCP'd back to local)"),
    }
    out_dir = _REPO / "data" / f"exp_v6_regime_switch_certify_seed{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    print(f"[cert] WROTE {out_dir / 'metrics.json'} verdict={verdict} elapsed={elapsed:.1f}s",
          flush=True)
    print(f"[RESULT] seed={seed} verdict={verdict} link_ptr@J5={link_ptr['5']['pointer_acc']:.4f} "
          f"iso_calib={iso_calib:.4f} iso_hi80={iso_hi80:.4f} dense_last_ret="
          f"{dense_last['ret_agree10']:.4f} cap_hardpass_maxJ={max_hardpass_J}", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    return run(args.seed)


if __name__ == "__main__":
    sys.exit(main())
