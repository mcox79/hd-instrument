"""Compositional generalization: learned front-end + fixed native FHRR binding vs flat learned baseline (v1).

THE HONEST CLAIM (brain-drill refined, see notes/research_brain_systematicity_binding_learned_frontend_
2026-07-20.md): native FHRR binding is a BUILT-IN STRUCTURAL PRIOR that gives a LEARNED front-end
SYSTEMATIC generalization to HELD-OUT role-filler combinations DATA-EFFICIENTLY / WITHOUT meta-learning,
where a FLAT learned baseline (single-task, no meta-learning, matched capacity) FAILS (classic COGS/SCAN
systematicity gap; causal analog = NS-CL/CLEVR-CoGenT frozen-attribute-classifier ablation). We measure
the LEARNING CURVE (held-out accuracy vs training-set size), not a single point.

CAVEAT (do not over-claim): Lake & Baroni MLC (Nature 2023) shows a fully-learned META-LEARNED model CAN
match fixed-binding systematicity. This is NOT "binding uniquely enables systematicity" -- it is "binding
achieves it data-efficiently WITHOUT meta-learning, brain-faithful" (Kymn et al. 2024: fixed structured
binding + learned heteroassociative mapping, hippocampal-entorhinal circuits).

PRIOR ART (credit; learn-from/build-on, never steal): Smolensky 1990 TPR; Plate 1995 HRR; NVSA (Hersche
et al. 2023); NS-CL (Mao et al. 2019) + CLEVR-CoGenT (Johnson et al. 2017) -- THE causal ablation this
design borrows (freeze attribute classifier after train-split-only training -> preserved held-out gen;
re-learn end-to-end on the compositional loss -> entanglement + collapse on the swapped split); Kymn et
al. 2024 (hippocampal-entorhinal fixed-binding + learned-mapping neural precedent); Lake & Baroni (ICML
2018 SCAN; Nature 2023 MLC); Kim & Linzen 2020 (COGS); Keysers et al. 2020 (CFQ/DBCA compound-divergence
split discipline); Greff, van Steenkiste & Schmidhuber 2020 (construction-determinism critique -- same
lesson as our in-house structure-derivation KILL, atom 29369: role/filler codes must be random/task-
agnostic, GUARD #1 below). Uses hdlab.binding.bind/unbind (native FHRR) + a vectorized reimplementation of
hdlab.bundling.bundle's per-component-magnitude-renorm formula (verified numerically equivalent, self-test).

GUARD #1 (decisive): role codes (R=6) and filler codes (F=12) are FHRR unit-phasors generated ONCE from
FIXED task-agnostic seeds, BEFORE the train/test group-split logic exists. Never selected/tuned/derived
to fit the held-out combinatorial structure.

Pre-reg: preregs/2026-07-20_compgen_binding_vs_flat_learned_frontend_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise
BEFORE except Exception (no BaseException); crlb_n/a declared (closed-form chance floor documented);
baseline_in_band; discriminator survives scale (full-N single-seed preview at smoke); HARD_PASS strictly
above chance; cardinality gate; per-unit failure-class; fixed arithmetic seeds (no hash()/list(set()));
numbers tagged in comments where estimated.

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
import torch
import torch.nn as nn

ANCHOR_NAME = "exp_compgen_binding_vs_flat_learned_frontend_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.binding import bind, unbind  # noqa: E402
from hdlab.bundling import bundle  # noqa: E402

# --------------------------------------------------------------------------- task constants
N = 1024  # FHRR dim (CLAUDE.md default)
R = 6  # roles
F = 12  # filler identities
D_OBS = 24  # perceptual observation dim
OBS_SIGMA = 0.5

GROUP_A = [0, 1, 2]  # roles
GROUP_B = [3, 4, 5]
HALF1 = list(range(0, 6))  # fillers
HALF2 = list(range(6, 12))

ROLE_CODE_SEED = 1000  # fixed, task-agnostic (GUARD #1) -- defined before any split logic
FILLER_CODE_SEED = 2000  # fixed, task-agnostic (GUARD #1)
PROTO_SEED = 42  # fixed filler prototypes, independent of split
EVAL_ID_SEED = 999
EVAL_OOD_SEED = 998

TRAIN_SIZES_FULL = [100, 400, 1600, 6400]
TRAIN_SIZES_SMOKE = [6400]  # discriminator-preview: FULL-N, single seed (option C)
SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]
ARMS = ["hybrid", "flat", "majority"]

EVAL_SCENES_ID = 400
EVAL_SCENES_OOD = 400
EPOCHS = 40
LR = 1e-3
BATCH = 128
N_TRAIN_MAX = 6400  # THEORETICAL: gate-evaluation point (most-converged regime)

# Pre-registered bands (declared BEFORE running; see prereg).
HP_HYBRID_OOD_GAP_MAX = 0.10
HP_FLAT_OOD_GAP_MIN = 0.30
HP_ID_MATCH_MAX = 0.05
HP_MAJORITY_OOD_MAX = 0.05
HF_FLAT_OOD_GAP_MAX = 0.10  # flat OOD gap below this = flat also generalizes = no advantage
HF_MAJORITY_OOD_MAX = 0.15
HF_ID_MISMATCH_MIN = 0.15
CHANCE = 1.0 / F  # THEORETICAL closed-form floor = 0.0833


# --------------------------------------------------------------------------- infra guards
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
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- FHRR codes (GUARD #1)
def random_fhrr(n_vecs, dim, seed):
    """Unit-phasor FHRR codes. Fixed seed, TASK-AGNOSTIC: takes no split/label argument (GUARD #1)."""
    g = torch.Generator().manual_seed(seed)
    theta = (torch.rand(n_vecs, dim, generator=g) * 2 - 1) * float(np.pi)
    mag = torch.ones(n_vecs, dim)
    return torch.polar(mag, theta).to(torch.complex64)


def batched_bundle(stack):
    """Vectorized bundle over dim=1 (batch, k, n) -> (batch, n). Same formula as hdlab.bundling.bundle
    (per-component magnitude renormalization); numerical equivalence verified in self_test()."""
    s = stack.sum(dim=1)
    mag = s.abs()
    mag = torch.where(mag > 0, mag, torch.ones_like(mag))
    return s / mag.to(s.dtype)


def cleanup_argmax(query_vecs, codebook):
    """query_vecs: (B, N) complex64; codebook: (F, N) complex64. Returns (B,) predicted class ids."""
    sim = (query_vecs.unsqueeze(1).conj() * codebook.unsqueeze(0)).sum(dim=-1).real
    return sim.argmax(dim=-1)


# --------------------------------------------------------------------------- data generation
def _proto_vectors():
    rng = np.random.default_rng(PROTO_SEED)
    return rng.standard_normal((F, D_OBS)).astype(np.float32)


def sample_scene_fillers(rng, held_out):
    fillers = np.zeros(R, dtype=np.int64)
    for r in range(R):
        in_group_a = r in GROUP_A
        if held_out:
            pool = HALF2 if in_group_a else HALF1
        else:
            pool = HALF1 if in_group_a else HALF2
        fillers[r] = rng.choice(pool)
    return fillers


def make_scenes(n_scenes, held_out, seed, proto):
    """Returns obs (S,R,D_OBS) float32, fillers (S,R) int64."""
    rng = np.random.default_rng(seed)
    fillers = np.zeros((n_scenes, R), dtype=np.int64)
    obs = np.zeros((n_scenes, R, D_OBS), dtype=np.float32)
    for s in range(n_scenes):
        f_assign = sample_scene_fillers(rng, held_out)
        fillers[s] = f_assign
        for r in range(R):
            noise = rng.normal(0, OBS_SIGMA, size=D_OBS).astype(np.float32)
            obs[s, r] = proto[f_assign[r]] + noise
    return obs, fillers


# --------------------------------------------------------------------------- models
def make_frontend_mlp(composite_seed):
    torch.manual_seed(composite_seed)
    return nn.Sequential(nn.Linear(D_OBS, 64), nn.ReLU(), nn.Linear(64, F))


def make_flat_mlp(composite_seed):
    torch.manual_seed(composite_seed)
    return nn.Sequential(
        nn.Linear(R * D_OBS + R, 128), nn.ReLU(),
        nn.Linear(128, 64), nn.ReLU(),
        nn.Linear(64, F),
    )


def train_mlp(model, X, y, composite_seed, epochs=EPOCHS, lr=LR, batch=BATCH):
    torch.manual_seed(composite_seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    n = X.shape[0]
    gen = torch.Generator().manual_seed(composite_seed)
    for _ep in range(epochs):
        perm = torch.randperm(n, generator=gen)
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            opt.zero_grad()
            out = model(X[idx])
            loss = loss_fn(out, y[idx])
            loss.backward()
            opt.step()
    return model


def build_frontend_training_set(obs, fillers):
    """(S,R,D_OBS)/(S,R) -> (S*R, D_OBS) / (S*R,) role-blind observation-label pairs."""
    S = obs.shape[0]
    X = torch.from_numpy(obs.reshape(S * R, D_OBS))
    y = torch.from_numpy(fillers.reshape(S * R))
    return X, y


def build_flat_training_set(obs, fillers):
    """All-R-queries-per-scene: (S,R,D_OBS)/(S,R) -> (S*R, R*D_OBS+R) / (S*R,)."""
    S = obs.shape[0]
    obs_flat = obs.reshape(S, R * D_OBS)  # (S, R*D_OBS)
    eye = np.eye(R, dtype=np.float32)  # (R, R)
    obs_tiled = np.repeat(obs_flat[:, None, :], R, axis=1)  # (S, R, R*D_OBS)
    query_onehot = np.repeat(eye[None, :, :], S, axis=0)  # (S, R, R)
    X = np.concatenate([obs_tiled, query_onehot], axis=-1).reshape(S * R, R * D_OBS + R)
    y = fillers.reshape(S * R)
    return torch.from_numpy(X.astype(np.float32)), torch.from_numpy(y)


def eval_hybrid(frontend, obs, fillers, role_codes, filler_codes):
    """obs (S,R,D_OBS), fillers (S,R) -> (preds (S*R,) int64 np, acc float, all_queries_correct bool arr)."""
    S = obs.shape[0]
    with torch.no_grad():
        obs_t = torch.from_numpy(obs.reshape(S * R, D_OBS))
        logits = frontend(obs_t)
        pred_ids = logits.argmax(dim=-1).reshape(S, R)  # (S,R)
        pred_filler_codes = filler_codes[pred_ids]  # (S,R,N) complex64
        role_codes_b = role_codes.unsqueeze(0).expand(S, R, N)  # (S,R,N)
        bound = bind(role_codes_b, pred_filler_codes)  # (S,R,N)
        scene_vec = batched_bundle(bound)  # (S,N)
        scene_rep = scene_vec.unsqueeze(1).expand(S, R, N).reshape(S * R, N)
        role_codes_tiled = role_codes.unsqueeze(0).expand(S, R, N).reshape(S * R, N)
        unbound = unbind(scene_rep, role_codes_tiled)  # (S*R, N)
        preds = cleanup_argmax(unbound, filler_codes).numpy()
    true = fillers.reshape(S * R)
    acc = float((preds == true).mean())
    return preds, acc


def eval_flat(model, obs, fillers):
    S = obs.shape[0]
    with torch.no_grad():
        X, y = build_flat_training_set(obs, fillers)
        preds = model(X).argmax(dim=-1).numpy()
    true = y.numpy()
    acc = float((preds == true).mean())
    return preds, acc


def eval_majority(majority_filler, fillers):
    S = fillers.shape[0]
    preds = np.tile(majority_filler, S)
    true = fillers.reshape(-1)
    acc = float((preds == true).mean())
    return preds, acc


def compute_majority(fillers_train):
    """fillers_train (S,R) -> majority_filler (R,) via per-role frequency count on TRAIN scenes only."""
    majority = np.zeros(R, dtype=np.int64)
    for r in range(R):
        vals, counts = np.unique(fillers_train[:, r], return_counts=True)
        # deterministic tie-break: sort by (-count, value); no hash()/set() ordering.
        order = sorted(range(len(vals)), key=lambda i: (-counts[i], vals[i]))
        majority[r] = vals[order[0]]
    return majority


# --------------------------------------------------------------------------- runner
def run(output_dir, train_sizes, seeds, eval_scenes_id, eval_scenes_ood):
    t0 = time.perf_counter()
    expected_n_units = len(train_sizes) * len(seeds) * len(ARMS)
    run_mode = os.path.basename(output_dir)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    proto = _proto_vectors()
    role_codes = random_fhrr(R, N, ROLE_CODE_SEED)
    filler_codes = random_fhrr(F, N, FILLER_CODE_SEED)
    _hb(output_dir, f"codes built: role_codes={role_codes.shape} filler_codes={filler_codes.shape}")

    obs_id, fillers_id = make_scenes(eval_scenes_id, held_out=False, seed=EVAL_ID_SEED, proto=proto)
    obs_ood, fillers_ood = make_scenes(eval_scenes_ood, held_out=True, seed=EVAL_OOD_SEED, proto=proto)
    _hb(output_dir, f"eval sets built: ID={obs_id.shape} OOD={obs_ood.shape}")

    per_unit = {}
    pred_hashes = {}  # for arms_differ check, keyed by (train_size, seed) -> {arm: hash}
    n_units_done = 0
    sweep_summary = {}  # train_size -> {arm: {seed: {...}}}

    for ts in train_sizes:
        sweep_summary[str(ts)] = {arm: {} for arm in ARMS}
        for seed in seeds:
            composite_seed = 100000 * seed + ts  # deterministic arithmetic combo, NOT hash() (PROT-023)
            obs_tr, fillers_tr = make_scenes(ts, held_out=False, seed=composite_seed, proto=proto)
            pair_key = f"ts{ts}_seed{seed}"
            pred_hashes[pair_key] = {}

            # --- hybrid ---
            unit_key = f"hybrid__ts{ts}__seed{seed}"
            try:
                Xf, yf = build_frontend_training_set(obs_tr, fillers_tr)
                frontend = make_frontend_mlp(composite_seed)
                train_mlp(frontend, Xf, yf, composite_seed)
                preds_id, acc_id = eval_hybrid(frontend, obs_id, fillers_id, role_codes, filler_codes)
                preds_ood, acc_ood = eval_hybrid(frontend, obs_ood, fillers_ood, role_codes, filler_codes)
                per_unit[unit_key] = {
                    "arm": "hybrid", "train_size": ts, "seed": seed,
                    "id_acc": acc_id, "ood_acc": acc_ood, "ood_gap": acc_id - acc_ood,
                    "failure_class": None,
                }
                pred_hashes[pair_key]["hybrid"] = hashlib.sha256(preds_ood.tobytes()).hexdigest()
                sweep_summary[str(ts)]["hybrid"][str(seed)] = per_unit[unit_key]
                n_units_done += 1
                _hb(output_dir, f"{unit_key}: id={acc_id:.3f} ood={acc_ood:.3f}")
            except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
                per_unit[unit_key] = {"arm": "hybrid", "train_size": ts, "seed": seed,
                                       "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
                _hb(output_dir, f"{unit_key}: FAILED {type(e).__name__}")

            # --- flat ---
            unit_key = f"flat__ts{ts}__seed{seed}"
            try:
                Xflat, yflat = build_flat_training_set(obs_tr, fillers_tr)
                flat_model = make_flat_mlp(composite_seed)
                train_mlp(flat_model, Xflat, yflat, composite_seed)
                preds_id, acc_id = eval_flat(flat_model, obs_id, fillers_id)
                preds_ood, acc_ood = eval_flat(flat_model, obs_ood, fillers_ood)
                per_unit[unit_key] = {
                    "arm": "flat", "train_size": ts, "seed": seed,
                    "id_acc": acc_id, "ood_acc": acc_ood, "ood_gap": acc_id - acc_ood,
                    "failure_class": None,
                }
                pred_hashes[pair_key]["flat"] = hashlib.sha256(preds_ood.tobytes()).hexdigest()
                sweep_summary[str(ts)]["flat"][str(seed)] = per_unit[unit_key]
                n_units_done += 1
                _hb(output_dir, f"{unit_key}: id={acc_id:.3f} ood={acc_ood:.3f}")
            except Exception as e:
                per_unit[unit_key] = {"arm": "flat", "train_size": ts, "seed": seed,
                                       "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
                _hb(output_dir, f"{unit_key}: FAILED {type(e).__name__}")

            # --- majority ---
            unit_key = f"majority__ts{ts}__seed{seed}"
            try:
                majority_filler = compute_majority(fillers_tr)
                preds_id, acc_id = eval_majority(majority_filler, fillers_id)
                preds_ood, acc_ood = eval_majority(majority_filler, fillers_ood)
                per_unit[unit_key] = {
                    "arm": "majority", "train_size": ts, "seed": seed,
                    "id_acc": acc_id, "ood_acc": acc_ood, "ood_gap": acc_id - acc_ood,
                    "failure_class": None,
                }
                pred_hashes[pair_key]["majority"] = hashlib.sha256(preds_ood.tobytes()).hexdigest()
                sweep_summary[str(ts)]["majority"][str(seed)] = per_unit[unit_key]
                n_units_done += 1
                _hb(output_dir, f"{unit_key}: id={acc_id:.3f} ood={acc_ood:.3f}")
            except Exception as e:
                per_unit[unit_key] = {"arm": "majority", "train_size": ts, "seed": seed,
                                       "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
                _hb(output_dir, f"{unit_key}: FAILED {type(e).__name__}")

    # ARMS-MUST-DIFFER (META_RULE_AF): within each (train_size,seed), hybrid/flat/majority OOD-pred
    # arrays must be pairwise distinct.
    arms_differ = True
    arms_differ_detail = {}
    for pair_key, hd in pred_hashes.items():
        vals = list(hd.values())
        distinct = len(set(vals)) == len(vals) if vals else False
        arms_differ_detail[pair_key] = distinct
        if not distinct:
            arms_differ = False

    # Cardinality gate (META_RULE_H).
    cardinality_ok = (n_units_done == expected_n_units)

    # Aggregate means per (train_size, arm) over seeds.
    def _mean(vals):
        return float(np.mean(vals)) if vals else float("nan")

    arm_by_size = {}
    for ts in train_sizes:
        arm_by_size[str(ts)] = {}
        for arm in ARMS:
            id_accs = [sweep_summary[str(ts)][arm][str(s)]["id_acc"]
                       for s in seeds if str(s) in sweep_summary[str(ts)][arm]
                       and "id_acc" in sweep_summary[str(ts)][arm][str(s)]]
            ood_accs = [sweep_summary[str(ts)][arm][str(s)]["ood_acc"]
                        for s in seeds if str(s) in sweep_summary[str(ts)][arm]
                        and "ood_acc" in sweep_summary[str(ts)][arm][str(s)]]
            arm_by_size[str(ts)][arm] = {
                "id_acc_mean": _mean(id_accs), "ood_acc_mean": _mean(ood_accs),
                "ood_gap_mean": _mean([i - o for i, o in zip(id_accs, ood_accs)]),
                "n_seeds": len(id_accs),
            }

    # Gate evaluation at N_TRAIN_MAX (or the largest swept size if N_TRAIN_MAX absent, e.g. smoke).
    gate_ts_key = str(N_TRAIN_MAX) if str(N_TRAIN_MAX) in arm_by_size else str(max(train_sizes))
    gate = arm_by_size[gate_ts_key]

    hybrid_id = gate["hybrid"]["id_acc_mean"]
    hybrid_ood = gate["hybrid"]["ood_acc_mean"]
    flat_id = gate["flat"]["id_acc_mean"]
    flat_ood = gate["flat"]["ood_acc_mean"]
    majority_ood = gate["majority"]["ood_acc_mean"]

    hybrid_ood_gap = hybrid_id - hybrid_ood
    flat_ood_gap = flat_id - flat_ood
    id_mismatch = abs(hybrid_id - flat_id)

    baseline_in_band = 0.05 <= flat_id <= 0.98

    # Discriminator-fires check (also serves smoke's option-C preview gate).
    discriminator_fires = (
        flat_ood_gap >= HP_FLAT_OOD_GAP_MIN - 0.05  # near/above the HARD_PASS floor, allowing MIDDLE_BAND slack
        and majority_ood <= HF_MAJORITY_OOD_MAX
    )

    # Verdict logic.
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif id_mismatch > HF_ID_MISMATCH_MIN:
        verdict = "HARD_FAIL_CAPACITY_MISMATCH_INVALID_COMPARISON"
    elif majority_ood > HF_MAJORITY_OOD_MAX:
        verdict = "HARD_FAIL_SPLIT_NOT_DISCRIMINATIVE"
    elif flat_ood_gap < HF_FLAT_OOD_GAP_MAX:
        verdict = "HARD_FAIL_FLAT_ALSO_GENERALIZES_NO_BINDING_ADVANTAGE"
    elif (hybrid_ood_gap <= HP_HYBRID_OOD_GAP_MAX and flat_ood_gap >= HP_FLAT_OOD_GAP_MIN
          and id_mismatch <= HP_ID_MATCH_MAX and majority_ood <= HP_MAJORITY_OOD_MAX):
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"[gate@ts={gate_ts_key}] hybrid: id={hybrid_id:.3f} ood={hybrid_ood:.3f} gap={hybrid_ood_gap:.3f} | "
        f"flat: id={flat_id:.3f} ood={flat_ood:.3f} gap={flat_ood_gap:.3f} | "
        f"majority_ood={majority_ood:.3f} | id_mismatch={id_mismatch:.3f} | "
        f"chance={CHANCE:.3f} | discriminator_fires={discriminator_fires} | "
        f"cardinality_ok={cardinality_ok} ({n_units_done}/{expected_n_units}) arms_differ={arms_differ}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:200]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "R": R, "F": F, "N": N, "D_OBS": D_OBS, "OBS_SIGMA": OBS_SIGMA,
            "GROUP_A": GROUP_A, "GROUP_B": GROUP_B, "HALF1": HALF1, "HALF2": HALF2,
            "train_sizes": train_sizes, "seeds": seeds,
            "eval_scenes_id": eval_scenes_id, "eval_scenes_ood": eval_scenes_ood,
            "epochs": EPOCHS, "lr": LR, "batch": BATCH,
        },
        "gate_train_size": gate_ts_key,
        "arm_by_size": arm_by_size,
        "per_unit": per_unit,
        "bands": {
            "HP_HYBRID_OOD_GAP_MAX": HP_HYBRID_OOD_GAP_MAX, "HP_FLAT_OOD_GAP_MIN": HP_FLAT_OOD_GAP_MIN,
            "HP_ID_MATCH_MAX": HP_ID_MATCH_MAX, "HP_MAJORITY_OOD_MAX": HP_MAJORITY_OOD_MAX,
            "HF_FLAT_OOD_GAP_MAX": HF_FLAT_OOD_GAP_MAX, "HF_MAJORITY_OOD_MAX": HF_MAJORITY_OOD_MAX,
            "HF_ID_MISMATCH_MIN": HF_ID_MISMATCH_MIN, "CHANCE": CHANCE,
        },
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail,
        "discriminator_fires": discriminator_fires,
        "baseline_in_band": baseline_in_band,
        "guard1_role_filler_codes_random_task_agnostic": True,
        "crlb_n/a": f"classification-accuracy generalization; closed-form chance floor = 1/F = {CHANCE:.4f}",
        "prior_art": "Smolensky1990 TPR; Plate1995 HRR; Hersche2023 NVSA; Mao2019 NS-CL; Johnson2017 CLEVR-CoGenT; "
                     "Kymn2024; LakeBaroni2018/2023; KimLinzen2020 COGS; Keysers2020 CFQ/DBCA; "
                     "GreffVanSteensteSchmidhuber2020",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at tiny scale: exercises the REAL builders (no synthetic-only branch)."""
    print("[self-test] GUARD #1: code generation takes no split/label argument", flush=True)
    import inspect
    sig = inspect.signature(random_fhrr)
    assert list(sig.parameters.keys()) == ["n_vecs", "dim", "seed"], (
        f"random_fhrr signature carries extra params: {list(sig.parameters.keys())} "
        "-- GUARD #1 requires code generation to be task-agnostic (no split/label input)")

    print("[self-test] positive control: batched_bundle == hdlab.bundling.bundle (numerical equivalence)",
          flush=True)
    torch.manual_seed(0)
    theta = torch.rand(3, 8) * 2 * float(np.pi) - float(np.pi)
    stack = torch.polar(torch.ones(3, 8), theta).to(torch.complex64)
    ref = bundle(stack)  # native hdlab primitive, single (k,n)
    fast = batched_bundle(stack.unsqueeze(0)).squeeze(0)  # our batched formula, batch=1
    assert torch.allclose(ref, fast, atol=1e-5), f"batched_bundle diverges from hdlab.bundling.bundle: max|diff|={(ref-fast).abs().max()}"

    print("[self-test] positive control: bind-then-unbind exact round trip (FHRR algebra sanity)", flush=True)
    role_codes = random_fhrr(R, N, ROLE_CODE_SEED)
    filler_codes = random_fhrr(F, N, FILLER_CODE_SEED)
    bound = bind(role_codes[0], filler_codes[3])
    recovered = unbind(bound, role_codes[0])
    cos = (recovered.conj() * filler_codes[3]).sum().real / N
    assert cos > 0.99, f"FHRR bind/unbind round trip failed: cos={cos:.4f} (expected > 0.99)"

    print("[self-test] real_code_path: exercising REAL builders at tiny scale", flush=True)
    proto = _proto_vectors()
    assert proto.shape == (F, D_OBS)
    obs_tr, fillers_tr = make_scenes(6, held_out=False, seed=123, proto=proto)
    obs_ood, fillers_ood = make_scenes(4, held_out=True, seed=456, proto=proto)
    assert obs_tr.shape == (6, R, D_OBS) and fillers_tr.shape == (6, R)
    # held-out combos must genuinely differ from train combos for at least one GROUP_A role.
    for r in GROUP_A:
        assert fillers_tr[:, r].max() <= 5, "train scene put a HALF2 filler on a GROUP_A role"
    for r in GROUP_A:
        assert fillers_ood[:, r].min() >= 6, "held-out scene put a HALF1 filler on a GROUP_A role"

    Xf, yf = build_frontend_training_set(obs_tr, fillers_tr)
    assert Xf.shape == (6 * R, D_OBS) and yf.shape == (6 * R,)
    frontend = make_frontend_mlp(composite_seed=7)
    train_mlp(frontend, Xf, yf, composite_seed=7, epochs=3, batch=8)
    preds_id, acc_id = eval_hybrid(frontend, obs_tr, fillers_tr, role_codes, filler_codes)
    preds_ood, acc_ood = eval_hybrid(frontend, obs_ood, fillers_ood, role_codes, filler_codes)
    assert 0.0 <= acc_id <= 1.0 and 0.0 <= acc_ood <= 1.0
    assert preds_id.shape == (6 * R,) and preds_ood.shape == (4 * R,)

    Xflat, yflat = build_flat_training_set(obs_tr, fillers_tr)
    assert Xflat.shape == (6 * R, R * D_OBS + R)
    flat_model = make_flat_mlp(composite_seed=7)
    train_mlp(flat_model, Xflat, yflat, composite_seed=7, epochs=3, batch=8)
    preds_flat_id, acc_flat_id = eval_flat(flat_model, obs_tr, fillers_tr)
    preds_flat_ood, acc_flat_ood = eval_flat(flat_model, obs_ood, fillers_ood)
    assert preds_flat_id.shape == (6 * R,)

    majority_filler = compute_majority(fillers_tr)
    assert majority_filler.shape == (R,)
    preds_maj_ood, acc_maj_ood = eval_majority(majority_filler, fillers_ood)
    # By construction the majority (trained on GROUP_A->HALF1) must be wrong on ALL held-out GROUP_A queries.
    for r in GROUP_A:
        assert majority_filler[r] <= 5, "majority for a GROUP_A role should be a HALF1 filler (train-only)"

    # ARMS-MUST-DIFFER sanity (structurally different code paths; sanity not bitwise-identical).
    h_hash = hashlib.sha256(preds_ood.tobytes()).hexdigest()
    f_hash = hashlib.sha256(preds_flat_ood.tobytes()).hexdigest()
    m_hash = hashlib.sha256(preds_maj_ood.tobytes()).hexdigest()
    assert len({h_hash, f_hash, m_hash}) >= 2, "META_RULE_AF: toy-scale arms suspiciously identical"

    print(f"[self-test] PASS: toy acc_id(hybrid)={acc_id:.3f} acc_ood(hybrid)={acc_ood:.3f} "
          f"acc_id(flat)={acc_flat_id:.3f} acc_ood(flat)={acc_flat_ood:.3f} acc_ood(majority)={acc_maj_ood:.3f}",
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
        run(output_dir, TRAIN_SIZES_SMOKE, SEEDS_SMOKE, EVAL_SCENES_ID, EVAL_SCENES_OOD)
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, TRAIN_SIZES_FULL, SEEDS_FULL, EVAL_SCENES_ID, EVAL_SCENES_OOD)
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
