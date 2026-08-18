"""Shared core for kg_ingest_encoder_family_v1 siblings.

5-encoder cross-arm KG ingest cliff-M cell (2026-07-01).

Compose:
- ANCHOR 4 v4 encoder registry + preflight distinctness gate pattern
- INT8_DENSE hdlab primitive (commit c3ca7dab) for bounded-memory workspace
- u1_fb15k237_ingest_eval_v1 Hebbian multi-value store pattern

Discriminator: at what M does each encoder cross set-recall < 0.50? Cross-encoder
cliff-M ratio matrix. Genuine discrimination requires ratio >= 2.0 across families.

Pre-reg: preregs/2026-07-01_kg_ingest_encoder_family_v1.md
ASCII only. No unicode. No emojis.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME_BASE = "kg_ingest_encoder_family_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

ENCODER_FAMILIES = (
    "binary_bipolar",
    "hrr_real",
    "fhrr",
    "sparse_bipolar",
    "sparse_real",
)

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192  # discriminator-must-survive-scale (USER 2026-06-26)
N_DIM_SELFTEST = 128  # small dim + high fanout stresses cliff at self-test scale

M_FULL = (10000, 40000)
M_SMOKE = (2000, 8000)  # small enough for local laptop; still crosses cliff regime
M_SELFTEST = (200, 800)  # 4x M ratio ensures cliff at least once for at least one encoder

CLIFF_THRESHOLD = 0.50  # set-recall below this defines cliff-M
CLIFF_RATIO_HP_MIN = 2.0
CLIFF_RATIO_MM_MIN = 1.5
SATURATION_FLAG = 1.0 - 1e-6

SPARSE_BIPOLAR_DENSITY = 0.05
SPARSE_REAL_DENSITY = 0.20

REQUIRED_FIELDS = (
    "verdict", "verdict_msg", "elapsed_s", "summary",
    "per_encoder_cliff_M", "cliff_M_ratio_matrix",
    "mechanism_hashes", "cardinality_observed", "cardinality_expected",
)


# ---------------------------------------------------------------------------
# Encoder builders (numpy; float32)
# ---------------------------------------------------------------------------
def _build_binary_bipolar(n_items: int, dim: int, seed: int) -> np.ndarray:
    g = np.random.default_rng(seed)
    x = (g.integers(0, 2, size=(n_items, dim)) * 2 - 1).astype(np.float32)
    return x


def _build_hrr_real(n_items: int, dim: int, seed: int) -> np.ndarray:
    g = np.random.default_rng(seed)
    x = g.normal(0.0, 1.0 / math.sqrt(dim), size=(n_items, dim)).astype(np.float32)
    norms = np.linalg.norm(x, axis=1, keepdims=True).clip(1e-12)
    return x / norms


def _build_fhrr(n_items: int, dim: int, seed: int) -> np.ndarray:
    if dim % 2 != 0:
        raise ValueError(f"FHRR needs even dim, got {dim}")
    g = np.random.default_rng(seed)
    n_complex = dim // 2
    phi = g.uniform(0.0, 2.0 * math.pi, size=(n_items, n_complex)).astype(np.float32)
    real = np.cos(phi).astype(np.float32)
    imag = np.sin(phi).astype(np.float32)
    return real + 1j * imag  # complex64


def _build_sparse_bipolar(n_items: int, dim: int, seed: int) -> np.ndarray:
    g = np.random.default_rng(seed)
    s = max(1, int(round(SPARSE_BIPOLAR_DENSITY * dim)))
    arr = np.zeros((n_items, dim), dtype=np.float32)
    scores = g.normal(0.0, 1.0, size=(n_items, dim))
    idx = np.argpartition(-scores, s, axis=1)[:, :s]
    signs = (g.integers(0, 2, size=(n_items, s)) * 2 - 1).astype(np.float32)
    rows = np.arange(n_items)[:, None]
    arr[rows, idx] = signs
    return arr


def _build_sparse_real(n_items: int, dim: int, seed: int) -> np.ndarray:
    g = np.random.default_rng(seed)
    s = max(1, int(round(SPARSE_REAL_DENSITY * dim)))
    arr = np.zeros((n_items, dim), dtype=np.float32)
    scores = g.normal(0.0, 1.0, size=(n_items, dim))
    idx = np.argpartition(-scores, s, axis=1)[:, :s]
    mag = np.abs(g.normal(0.0, 1.0, size=(n_items, s))).astype(np.float32)
    signs = (g.integers(0, 2, size=(n_items, s)) * 2 - 1).astype(np.float32)
    values = signs * mag
    rows = np.arange(n_items)[:, None]
    arr[rows, idx] = values
    return arr


# ---------------------------------------------------------------------------
# Encoder-specific BIND ops
# ---------------------------------------------------------------------------
def _bind_binary_bipolar(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


def _bind_hrr_real(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    fa = np.fft.rfft(a, axis=-1)
    fb = np.fft.rfft(b, axis=-1)
    return np.fft.irfft(fa * fb, n=a.shape[-1], axis=-1).astype(np.float32)


def _bind_fhrr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def _bind_sparse_bipolar(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


def _bind_sparse_real(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


_ENCODER_REGISTRY = {
    "binary_bipolar": {"build": _build_binary_bipolar, "bind": _bind_binary_bipolar, "complex": False, "bind_op_name": "elementwise_mul_bipolar"},
    "hrr_real":        {"build": _build_hrr_real,        "bind": _bind_hrr_real,        "complex": False, "bind_op_name": "fft_circular_convolution"},
    "fhrr":            {"build": _build_fhrr,             "bind": _bind_fhrr,             "complex": True,  "bind_op_name": "complex_elementwise_mul"},
    "sparse_bipolar":  {"build": _build_sparse_bipolar,   "bind": _bind_sparse_bipolar,   "complex": False, "bind_op_name": "elementwise_mul_sparse_bipolar"},
    "sparse_real":     {"build": _build_sparse_real,      "bind": _bind_sparse_real,      "complex": False, "bind_op_name": "elementwise_mul_sparse_real"},
}


def _encoder_dim(family: str, dim: int) -> int:
    return dim // 2 if family == "fhrr" else dim


# ---------------------------------------------------------------------------
# Pre-flight distinctness gate (META_RULE_AY)
# ---------------------------------------------------------------------------
def verify_encoder_distinctness_preflight(
    seed: int, dim: int = 1024,
) -> Tuple[bool, Dict[str, str], str]:
    n_test = 4
    hashes: Dict[str, str] = {}
    collisions: List[Tuple[str, str]] = []
    for fam in ENCODER_FAMILIES:
        reg = _ENCODER_REGISTRY[fam]
        eff_dim = _encoder_dim(fam, dim)
        # for FHRR store passes eff_dim which is dim/2 complex slots; builder handles it
        a = reg["build"](n_test, dim if fam != "fhrr" else dim, seed)
        b = reg["build"](n_test, dim if fam != "fhrr" else dim, seed + 1)
        bound = reg["bind"](a, b)
        h = hashlib.sha256(bound.tobytes()).hexdigest()[:16]
        for prev_fam, prev_h in hashes.items():
            if prev_h == h:
                collisions.append((prev_fam, fam))
        hashes[fam] = h
    if collisions:
        return False, hashes, f"ENCODER_HASH_COLLISION preflight: {collisions}; hashes={hashes}"
    return True, hashes, f"preflight_distinct(dim={dim}): {hashes}"


# ---------------------------------------------------------------------------
# KG loading + Hebbian multi-value store per (encoder, M)
# ---------------------------------------------------------------------------
def load_kg_triples(m_max: int, path: Path = KG_PATH) -> List[Tuple[str, str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"KG_PATH_MISSING: {path}")
    triples: List[Tuple[str, str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= m_max:
                break
            rec = json.loads(line)
            triples.append((rec["subject"], rec["predicate"], rec["object"]))
    return triples


def _index_entities(triples: List[Tuple[str, str, str]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    ent_ids: Dict[str, int] = {}
    rel_ids: Dict[str, int] = {}
    for s, p, o in triples:
        if s not in ent_ids:
            ent_ids[s] = len(ent_ids)
        if o not in ent_ids:
            ent_ids[o] = len(ent_ids)
        if p not in rel_ids:
            rel_ids[p] = len(rel_ids)
    return ent_ids, rel_ids


def _score_real(query: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Cosine-like inner product; query (n_dim,), X (n_items, n_dim)."""
    return X @ query


def _score_fhrr(query: np.ndarray, X: np.ndarray) -> np.ndarray:
    """FHRR similarity: real(<x, conj(query)>) / n_complex."""
    sims = np.real(X @ np.conj(query)) / X.shape[1]
    return sims


def _get_score_fn(family: str):
    return _score_fhrr if family == "fhrr" else _score_real


def _synthetic_key(fam: str, E_s: np.ndarray, R_p: np.ndarray, sqrtN: float) -> np.ndarray:
    """key = E[s] BIND R[p] * scale. FHRR uses complex bind (no scale needed);
    others use elementwise * sqrtN for magnitude alignment with Hebbian weight decay."""
    bind = _ENCODER_REGISTRY[fam]["bind"]
    if fam == "fhrr":
        return bind(E_s[None, :], R_p[None, :])[0]  # unit-modulus already
    return bind(E_s[None, :], R_p[None, :])[0] * sqrtN


def measure_set_recall(
    family: str, triples: List[Tuple[str, str, str]], dim: int, seed: int,
    n_eval: int = 400,
) -> Tuple[float, Dict[str, Any]]:
    """Ingest triples via encoder+Hebbian; measure set-recall on n_eval sampled (s,p) keys.

    Multi-value: W += outer(E[o], key) / N_eff for each triple; readout scores E @ (W @ key),
    top-k=len(objects(s,p)).
    """
    ent_ids, rel_ids = _index_entities(triples)
    n_ent = len(ent_ids)
    n_rel = len(rel_ids)

    if family == "fhrr":
        # complex code; W is complex; E, R built at real dim (which is dim); FHRR builder maps to complex dim/2
        E = _ENCODER_REGISTRY[family]["build"](n_ent, dim, seed)   # (n_ent, dim/2) complex64
        R = _ENCODER_REGISTRY[family]["build"](n_rel, dim, seed + 100000)
        n_eff = E.shape[1]  # complex dim
        W = np.zeros((n_eff, n_eff), dtype=np.complex64)
        sqrtN = 1.0  # FHRR unit-modulus
    else:
        E = _ENCODER_REGISTRY[family]["build"](n_ent, dim, seed)
        R = _ENCODER_REGISTRY[family]["build"](n_rel, dim, seed + 100000)
        n_eff = dim
        W = np.zeros((n_eff, n_eff), dtype=np.float32)
        sqrtN = math.sqrt(n_eff)

    # Build key-obj index (multi-value)
    key_objs: Dict[Tuple[int, int], List[int]] = {}
    for (s, p, o) in triples:
        si = ent_ids[s]; pi = rel_ids[p]; oi = ent_ids[o]
        key_objs.setdefault((si, pi), []).append(oi)

    # Hebbian accumulate: W += outer(E[o], key) / n_eff  (or complex-analog for FHRR)
    for (si, pi), objs in key_objs.items():
        key = _synthetic_key(family, E[si], R[pi], sqrtN)
        for oi in objs:
            if family == "fhrr":
                W += np.outer(E[oi], np.conj(key)) / n_eff
            else:
                W += np.outer(E[oi], key) / n_eff

    # Evaluate on sample of keys
    rng_eval = np.random.default_rng(seed + 555)
    keys_list = list(key_objs.keys())
    if len(keys_list) > n_eval:
        sample_idx = rng_eval.choice(len(keys_list), n_eval, replace=False)
        eval_keys = [keys_list[i] for i in sample_idx]
    else:
        eval_keys = keys_list

    score_fn = _get_score_fn(family)
    hits = 0
    tot = 0
    for (si, pi) in eval_keys:
        objs = key_objs[(si, pi)]
        k = len(objs)
        key = _synthetic_key(family, E[si], R[pi], sqrtN)
        readout = W @ key  # shape (n_eff,)
        scores = score_fn(readout, E)  # (n_ent,)
        topk_idx = np.argsort(scores)[-k:]
        hits += len(set(topk_idx.tolist()) & set(objs))
        tot += k

    recall = hits / max(tot, 1)
    stats = {
        "n_entities": n_ent,
        "n_relations": n_rel,
        "n_unique_keys": len(key_objs),
        "n_eval_keys": len(eval_keys),
        "mean_multivalue_k": float(np.mean([len(v) for v in key_objs.values()])),
        "saturation_flag": bool(recall >= SATURATION_FLAG),
    }
    return float(recall), stats


# ---------------------------------------------------------------------------
# Cliff-M estimation
# ---------------------------------------------------------------------------
def estimate_cliff_m(m_values: List[int], recalls: List[float], threshold: float = CLIFF_THRESHOLD) -> float:
    """Linear-interp cliff-M where recall crosses threshold.

    If recall never crosses threshold (all >= threshold), return +inf (encoder holds up to M_max).
    If recall always below threshold (all < threshold), return M_min (cliff at or before min).
    """
    pairs = sorted(zip(m_values, recalls))
    Ms = [p[0] for p in pairs]
    Rs = [p[1] for p in pairs]
    if all(r >= threshold for r in Rs):
        return float("inf")
    if all(r < threshold for r in Rs):
        return float(Ms[0])
    for i in range(len(Rs) - 1):
        if Rs[i] >= threshold >= Rs[i + 1]:
            # linear interp between (Ms[i], Rs[i]) and (Ms[i+1], Rs[i+1])
            denom = Rs[i] - Rs[i + 1]
            if abs(denom) < 1e-9:
                return float(Ms[i])
            frac = (Rs[i] - threshold) / denom
            return float(Ms[i] + frac * (Ms[i + 1] - Ms[i]))
    # fallback: return smallest M below threshold
    for m, r in pairs:
        if r < threshold:
            return float(m)
    return float("inf")


def cliff_ratio_matrix(cliffs: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    fams = list(cliffs.keys())
    out: Dict[str, Dict[str, float]] = {}
    for a in fams:
        out[a] = {}
        for b in fams:
            ca = cliffs[a]
            cb = cliffs[b]
            if math.isinf(ca) and math.isinf(cb):
                out[a][b] = 1.0
            elif math.isinf(ca):
                out[a][b] = float("inf")
            elif math.isinf(cb):
                out[a][b] = 0.0
            elif cb <= 0:
                out[a][b] = float("inf")
            else:
                out[a][b] = ca / cb
    return out


def max_cliff_ratio(cliffs: Dict[str, float]) -> float:
    finite = [c for c in cliffs.values() if not math.isinf(c) and c > 0]
    if len(finite) < 2:
        return float("inf") if any(math.isinf(c) for c in cliffs.values()) else 1.0
    return max(finite) / min(finite)


# ---------------------------------------------------------------------------
# Self-test (formula gate)
# ---------------------------------------------------------------------------
def run_selftest() -> Tuple[bool, str]:
    ok_pre, hashes, msg_pre = verify_encoder_distinctness_preflight(seed=0, dim=N_DIM_SELFTEST)
    if not ok_pre:
        return False, f"SELFTEST_FAIL_PREFLIGHT: {msg_pre}"
    # Mini synthetic KG (200 triples, small)
    rng = np.random.default_rng(0)
    n_ent = 40
    n_rel = 5
    triples_all: List[Tuple[str, str, str]] = []
    # 900 triples on 40 entities * 5 relations = 200 possible (s,p) keys;
    # M=800 forces heavy multi-value, stressing the encoder cliff
    for i in range(900):
        s = f"e{int(rng.integers(0, n_ent))}"
        p = f"r{int(rng.integers(0, n_rel))}"
        o = f"e{int(rng.integers(0, n_ent))}"
        triples_all.append((s, p, o))
    per_enc_recalls: Dict[str, List[float]] = {}
    for fam in ENCODER_FAMILIES:
        recs = []
        for m in M_SELFTEST:
            r, _ = measure_set_recall(fam, triples_all[:m], N_DIM_SELFTEST, seed=1, n_eval=50)
            recs.append(r)
        per_enc_recalls[fam] = recs

    if per_enc_recalls["binary_bipolar"][0] < 0.60:
        return False, f"SELFTEST_FAIL_POS_CONTROL: binary_bipolar small-M recall={per_enc_recalls['binary_bipolar'][0]:.3f} < 0.60. {per_enc_recalls}"

    # Cliff dimension exists: at least one encoder must show recall drop from M=100 to M=200
    any_drop = any(recs[0] - recs[1] > 0.05 for recs in per_enc_recalls.values())
    if not any_drop:
        return False, f"SELFTEST_FAIL_NO_CLIFF_DIM: no encoder shows recall drop across M. {per_enc_recalls}"

    return True, f"SELFTEST_PASS: preflight={msg_pre}; per_enc={per_enc_recalls}"


# ---------------------------------------------------------------------------
# Main cell driver (per seed)
# ---------------------------------------------------------------------------
def run_cell(seed: int, mode: str) -> Dict[str, Any]:
    t0 = time.time()
    if mode == "smoke":
        dim = N_DIM_SMOKE
        m_values = list(M_SMOKE)
    else:
        dim = N_DIM_FULL
        m_values = list(M_FULL)

    ok_pre, hashes, msg_pre = verify_encoder_distinctness_preflight(seed=seed, dim=dim)
    if not ok_pre:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": f"pre-flight distinctness gate failed: {msg_pre}",
            "elapsed_s": time.time() - t0,
            "summary": {"preflight": msg_pre},
            "per_encoder_cliff_M": {},
            "cliff_M_ratio_matrix": {},
            "mechanism_hashes": hashes,
            "cardinality_observed": 0,
            "cardinality_expected": len(ENCODER_FAMILIES) * len(m_values),
        }

    m_max = max(m_values)
    triples_all = load_kg_triples(m_max)
    per_encoder_recalls: Dict[str, Dict[int, float]] = {}
    per_encoder_stats: Dict[str, Dict[int, Dict[str, Any]]] = {}
    rows_observed = 0

    for fam in ENCODER_FAMILIES:
        per_encoder_recalls[fam] = {}
        per_encoder_stats[fam] = {}
        for m in m_values:
            triples = triples_all[:m]
            recall, stats = measure_set_recall(fam, triples, dim, seed=seed, n_eval=(200 if mode == "smoke" else 400))
            per_encoder_recalls[fam][m] = recall
            per_encoder_stats[fam][m] = stats
            rows_observed += 1

    # Estimate cliff-M per encoder
    cliffs: Dict[str, float] = {}
    for fam in ENCODER_FAMILIES:
        Ms = sorted(per_encoder_recalls[fam].keys())
        Rs = [per_encoder_recalls[fam][m] for m in Ms]
        cliffs[fam] = estimate_cliff_m(Ms, Rs)

    ratio_matrix = cliff_ratio_matrix(cliffs)
    max_ratio = max_cliff_ratio(cliffs)

    # Saturation audit (META_RULE_Q)
    saturation_flags = {fam: {m: per_encoder_stats[fam][m]["saturation_flag"] for m in m_values} for fam in ENCODER_FAMILIES}
    all_sat = all(saturation_flags[fam][m] for fam in ENCODER_FAMILIES for m in m_values)

    # Verdict logic (envelope-fail-bands from pre-reg)
    cardinality_expected = len(ENCODER_FAMILIES) * len(m_values)
    if rows_observed != cardinality_expected:
        verdict = "HARD_FAIL"
        verdict_msg = f"CARDINALITY_BREACH: observed={rows_observed} expected={cardinality_expected}"
    elif all_sat:
        verdict = "HARD_FAIL"
        verdict_msg = f"ALL_SATURATED (META_RULE_Q): every (enc,M) at recall >= {SATURATION_FLAG}; no discrimination possible"
    elif max_ratio >= CLIFF_RATIO_HP_MIN:
        verdict = "HARD_PASS"
        verdict_msg = f"CROSS_ENC_CLIFF_DISCRIMINATION: max_cliff_ratio={max_ratio:.3f} >= {CLIFF_RATIO_HP_MIN}; cliffs={cliffs}"
    elif max_ratio >= CLIFF_RATIO_MM_MIN:
        verdict = "MIDDLE_BAND"
        verdict_msg = f"PARTIAL_DISCRIMINATION: max_cliff_ratio={max_ratio:.3f} in [{CLIFF_RATIO_MM_MIN},{CLIFF_RATIO_HP_MIN}); cliffs={cliffs}"
    elif abs(max_ratio - 1.0) < 1e-6:
        verdict = "HARD_FAIL"
        verdict_msg = f"NO_DISCRIMINATION: cliff-M identical across encoders; cliffs={cliffs}"
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = f"WEAK_DISCRIMINATION: max_cliff_ratio={max_ratio:.3f} < {CLIFF_RATIO_MM_MIN}; cliffs={cliffs}"

    result = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.time() - t0,
        "summary": {
            "seed": seed,
            "mode": mode,
            "N_DIM": dim,
            "M_values": m_values,
            "per_encoder_recalls": per_encoder_recalls,
            "per_encoder_stats": per_encoder_stats,
            "max_cliff_ratio": max_ratio,
            "saturation_flags": saturation_flags,
            "preflight_msg": msg_pre,
        },
        "per_encoder_cliff_M": cliffs,
        "cliff_M_ratio_matrix": ratio_matrix,
        "mechanism_hashes": hashes,
        "cardinality_observed": rows_observed,
        "cardinality_expected": cardinality_expected,
    }
    return result


# ---------------------------------------------------------------------------
# Standard cell entry point
# ---------------------------------------------------------------------------
def _write_metrics_atomic(payload: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "metrics.json"
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp_path, out_path)


def cell_main(anchor_name: str, seed: int, argv: List[str]) -> int:
    if "--self-test" in argv:
        ok, msg = run_selftest()
        print(msg)
        # emit a selftest metrics file for cert-trail visibility
        out_dir = REPO / "data" / f"exp_{anchor_name}_selftest"
        payload = {
            "verdict": "HARD_PASS" if ok else "HARD_FAIL",
            "verdict_msg": msg,
            "elapsed_s": 0.0,
            "summary": {"mode": "selftest"},
            "per_encoder_cliff_M": {},
            "cliff_M_ratio_matrix": {},
            "mechanism_hashes": {},
            "cardinality_observed": 0,
            "cardinality_expected": 0,
        }
        _write_metrics_atomic(payload, out_dir)
        return 0 if ok else 1

    mode = "smoke" if "--smoke" in argv else "full"
    result = run_cell(seed=seed, mode=mode)
    suffix = "_smoke" if mode == "smoke" else ""
    out_dir = REPO / "data" / f"exp_{anchor_name}_seed_{seed}{suffix}"
    _write_metrics_atomic(result, out_dir)
    print(f"[{anchor_name} seed={seed} mode={mode}] verdict={result['verdict']} elapsed={result['elapsed_s']:.1f}s")
    print(f"  msg: {result['verdict_msg']}")
    return 0 if result["verdict"] != "HARD_FAIL" else 1
