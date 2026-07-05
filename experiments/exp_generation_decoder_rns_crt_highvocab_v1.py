# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: single_corr codebook vs single_synth codebook hash-distinct;
#     residue codebooks hash-distinct from single codebooks; rns_scram recovered-index array differs
#     from rns_crt recovered-index array (scramble genuinely alters output). Perfect-recovery arms
#     (rns_crt / single_synth) legitimately emit identical truth tokens -> we compare ARTIFACTS + the
#     scramble-divergence, never the recovered-token arrays (same lesson as blocklocal_v1).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: block-local disjoint recovery is interference-free (ONE code per block,
#     no superposition noise WITHIN a block). RNS reconstruction is exact iff every residue is decoded
#     correctly; a residue error requires a per-sub-block codebook COLLISION, not a noise-floor event.
#     crlb_n_a declared: there is no argmax-superposition-noise floor gating the deliverable.
# - baseline_in_band (META_RULE_AG): single_corr (the discriminator baseline) MUST sit in (0.05,0.95)
#     across the sweep -- CALIBRATED to 0.90 @ V8192 D26 (near v1 native-GSBC 0.856) down to 0.167 @
#     V65536 D26. single_synth is a CEILING context arm (exempt; intentionally ~1.0); rns_scram is a
#     CONTROL arm (exempt; intentionally ~0.0).
# - discriminator survives scale: smoke runs the discriminator AT the full envelope regime (N=8192,
#     D=26, V=65536, correlated codes). Smoke reduces trials/seed-count/grid-length ONLY, never N/D/V
#     at the gate points. single_corr-cliff + rns-hold + scram-collapse + synth-ceiling all FIRE in smoke.
# - HARD_PASS strictly above floor: rns_crt exact_ordered floor 0.85 (band from HF=0.50, +5pct=0.5175;
#     0.85 well above). MEASURED rns_crt=1.000 at all gate points (calibration probe).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# GENERATION DECODER -- RNS/CRT HIGH-VOCAB ENVELOPE-PUSH  v1
# =========================================================
# Extends the CHAIN_GRADE block-local generation decoder (exp_generation_decoder_gsbc_native_blocklocal_v1,
# HARD_PASS, canonical cliff single-block exact-ordered=0.856 @ V8192 D26
# MEASURED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms.blocklocal_gsbc@V8192D26.exact_ordered_mean)
# to HIGHER VOCABULARY via Residue Number System / Chinese Remainder Theorem sub-block decomposition.
#
# WHY the cliff exists (calibration finding, this cell): the single-block cliff is a CORRELATION artifact.
# With IID codes, each disjoint block holds exactly one interference-free term, so single-block cleanup is
# exact to V=millions (MEASURED single_synth=1.000 through V65536). The v1 native-GSBC cliff (0.856) is
# because CORRELATED concept codes project to near-identical sparse block codes -> cleanup ties. More
# concepts per semantic family (higher V at fixed family count) -> denser collisions -> deeper cliff
# (MEASURED single_corr 0.90->0.73->0.50->0.167 as V 8192->16384->32768->65536 @ D26, this cell's
# correlated pipeline calibrated to reproduce the v1 cliff).
#
# THE RNS MECHANISM (brain-grounded: entorhinal grid cells are modular/RNS -- CITED@Kymn/Fiete grid-as-RNS;
# CITED@Frady/Sommer sparse block-local resonator arXiv:2404.19126): instead of coding a token id in [0,V)
# with one V-way block, code it as residues (t mod m1, t mod m2, t mod m3) with pairwise-coprime moduli in
# r=3 disjoint SUB-blocks; effective vocab = prod(m_i) >= V. Each sub-block resolves only an m_i-way residue
# alphabet (m_i ~ 20-43 << V), so per-sub-block cleanup stays trivial past the single-block cliff. Because
# residue labels (t mod m_i) are NON-SEMANTIC, the residue codebooks are naturally iid/decorrelated -- which
# is exactly the grid-cell design (modules are decorrelated) and is what sidesteps the correlation cliff.
# Decode each residue independently (interference-free sub-block argmax), then CRT-reconstruct t.
#
# ARMS (all PAIRED on the same token-id props per (V,D,seed)):
#   single_corr   : correlated V-way codebook, single-block v1 decode -> CLIFFS (the v1 baseline)   [BASELINE]
#   single_synth  : iid V-way codebook, single-block v1 decode -> iid CEILING (cliff=corr artifact) [CEILING]
#   rns_crt       : iid residue codebooks (r=3 coprime moduli), RNS/CRT decode -> HOLDS             [MECHANISM]
#   rns_scram     : rns residues decoded correctly then DERANGED before CRT -> COLLAPSES            [CONTROL]
# Load-bearing PAIRED comparison: rns_crt vs single_corr at V beyond the 0.856 cliff (V=65536 D26).
# Distinctive RNS win (quantified, not fidelity-vs-iid): effective vocab prod(m_i) reached with only
# sum(m_i) residue codes (V=70520 effective via 124 codes @ V65536) + correlation-immunity by construction.
#
# HONEST scope: rns_crt fidelity ~ single_synth iid ceiling (both ~1.0); RNS does NOT beat an iid single
# codebook on fidelity. It (1) matches the iid ceiling where the REALISTIC correlated baseline cliffs, and
# (2) does so with sub-linear codebook cost. The scrambled control (0.000) proves CRT reconstruction is
# load-bearing (not trivially robust); correlated-residue collapse (out-of-band, not shipped) shows iid
# residue relabeling is the essential design choice.
#
# Sources (CITED@):
#  - experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py  (v1 block-local decoder, HARD_PASS; reused algebra)
#  - experiments/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000.py (block-local resonator)
#  - Kymn, Fiete et al. grid cells as residue number system / modular coding
#  - Frady/Sommer sparse block-local resonator arXiv:2404.19126
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Self-contained (synthetic correlated
# codes calibrated to the v1 cliff; NO pool/re-encode dependency, so V can push past the 10000-concept pool).
# Run: python experiments/exp_generation_decoder_rns_crt_highvocab_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

ANCHOR_NAME = "generation_decoder_rns_crt_highvocab_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default == v1 == envelope regime (all modes; never reduced)
F_SPARSE = 0.02       # block-local code sparsity fraction (v1 F_SPARSE=0.02)
R_MODULI = 3          # number of RNS residues per token (coprime moduli)
# Active-dim FLOOR: F_SPARSE*sub_block rounds to k=2 at D26 (sb=105), which is too sparse -> iid residue
# codebook 2-dim collisions cause seed-dependent per-residue argmax ties (MEASURED cv=0.243 at k_sb=2;
# k_sb>=3 -> rns_crt=1.000 cv=0.000 @scratchpad/kmin_probe.py). Floor at 4 for collision-free margin. Only
# affects sub-blocks (block k=round(F*bs) is already 5-10 at D16-32, so single_corr's cliff is preserved).
K_MIN_ACTIVE = 4

# Correlated-code CALIBRATION (adaptive difficulty; reproduces the v1 native-GSBC cliff). Chosen so that
# single_corr = 0.90 @ V8192 D26 (near v1 native-GSBC 0.856) and cliffs to 0.167 @ V65536 D26.
# MEASURED@scratchpad calibration rns_corr_calib.py (n_clusters=128, frac_shared=0.85).
N_CLUSTERS = 128      # FIXED count of "semantic families"; more concepts per family at higher V -> deeper cliff
FRAC_SHARED = 0.85    # fraction of a code's active dims drawn from its family template (correlation strength)

SEEDS = (7, 13, 19)

# Pairwise-coprime, balanced moduli per target V (product >= V). Coprimality + product>=V asserted at runtime.
MODULI = {
    8192: (20, 21, 23),   # prod 9660
    12288: (22, 23, 25),  # prod 12650
    16384: (25, 27, 28),  # prod 18900
    32768: (31, 33, 35),  # prod 35805
    49152: (36, 37, 41),  # prod 54612
    65536: (40, 41, 43),  # prod 70520
}

# (V, D, region): "anchor"=near v1 cliff tie-back; "sweep"/"envelope"=vocabulary push at the D26 cliff regime;
# "boundary"=D-dependence map of the cliff.
FULL_GRID = [
    (8192, 26, "anchor"),
    (16384, 26, "sweep"),
    (32768, 26, "sweep"),
    (49152, 26, "sweep"),
    (65536, 26, "envelope"),
    (65536, 16, "boundary"),
    (65536, 32, "boundary"),
]
SMOKE_GRID = [(8192, 26, "anchor"), (65536, 26, "envelope")]   # keeps N/D/V at gate points; fires discriminator
SELFTEST_GRID = [(8192, 26, "anchor")]
ANCHOR_V, ANCHOR_D = 8192, 26
ENVELOPE_V, ENVELOPE_D = 65536, 26

ARMS = ["single_corr", "single_synth", "rns_crt", "rns_scram"]

# Pre-registered bands (MEASURED via scratchpad calibration; deflated honestly).
HP_RNS_FLOOR = 0.85       # HARD_PASS: rns_crt exact-ordered at gate points (MEASURED 1.000 -> strict-above 0.85)
HP_CV = 0.10              # HARD_PASS: cross-seed cv of rns_crt exact-ordered (MEASURED 0.000)
SINGLE_CLIFF_THRESH = 0.70  # discriminator-fires: single_corr MUST be below this at envelope (MEASURED 0.167)
RNS_GAP = 0.30            # HARD_PASS: (rns_crt - single_corr) at envelope (MEASURED 0.833)
SCRAM_COLLAPSE = 0.10     # discriminator control: rns_scram exact-ordered must collapse below (MEASURED 0.000)
SYNTH_CEILING_FLOOR = 0.90  # wiring/ceiling: iid single-block must recover (MEASURED 1.000)
HF_RNS_FLOOR = 0.50       # HARD_FAIL: rns_crt below -> mechanism cannot round-trip at envelope


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# CRT number theory (formula self-test target)
# ============================================================


def _egcd(a: int, b: int):
    if b == 0:
        return (a, 1, 0)
    g, x, y = _egcd(b, a % b)
    return (g, y, x - (a // b) * y)


def _modinv(a: int, m: int) -> int:
    g, x, _ = _egcd(a % m, m)
    if g != 1:
        raise ValueError(f"no modular inverse for {a} mod {m} (not coprime)")
    return x % m


def _coprime(moduli) -> bool:
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if math.gcd(moduli[i], moduli[j]) != 1:
                return False
    return True


def _crt_setup(moduli):
    """Return (M=prod, Mi=[M/mi], yi=[inv(Mi) mod mi]) for CRT reconstruction."""
    if not _coprime(moduli):
        raise ValueError(f"moduli not pairwise coprime: {moduli}")
    M = 1
    for m in moduli:
        M *= m
    Mi = [M // m for m in moduli]
    yi = [_modinv(Mi[i], moduli[i]) for i in range(len(moduli))]
    return M, Mi, yi


def _crt(residues, moduli, M, Mi, yi) -> int:
    """Reconstruct t in [0,M) from residues (t mod mi). Exact iff residues correct."""
    t = 0
    for i in range(len(moduli)):
        t += (int(residues[i]) % moduli[i]) * Mi[i] * yi[i]
    return t % M


def crt_selftest(moduli) -> bool:
    """Formula self-test: (a) moduli pairwise coprime; (b) CRT(t mod mi) == t for all t in [0,min(M,4096))."""
    if not _coprime(moduli):
        return False
    M, Mi, yi = _crt_setup(moduli)
    lim = min(M, 4096)
    for t in range(lim):
        res = [t % m for m in moduli]
        if _crt(res, moduli, M, Mi, yi) != t:
            return False
    # also a random high-range spot check up to M
    rng = np.random.default_rng(12345)
    for _ in range(256):
        t = int(rng.integers(0, M))
        res = [t % m for m in moduli]
        if _crt(res, moduli, M, Mi, yi) != t:
            return False
    return True


# ============================================================
# Codebooks (vectorized)
# ============================================================


def _kact(bs: int) -> int:
    return min(bs, max(K_MIN_ACTIVE, int(round(F_SPARSE * bs))))


def iid_codebook(V: int, bs: int, seed: int) -> np.ndarray:
    """IID random k-sparse bipolar codebook (V, bs). Interference-free-block CEILING construction."""
    k = _kact(bs)
    g = np.random.default_rng(seed)
    idx = np.argsort(g.random((V, bs)), axis=1)[:, :k]      # k distinct dims per row
    cb = np.zeros((V, bs), dtype=np.float32)
    rows = np.arange(V)[:, None]
    cb[rows, idx] = (g.integers(0, 2, size=(V, k)).astype(np.float32) * 2.0 - 1.0)
    return cb


def corr_codebook(V: int, bs: int, seed: int, n_clusters: int, frac_shared: float) -> np.ndarray:
    """Correlated k-sparse bipolar codebook (V, bs): each code draws frac_shared*k of its active dims (with
    signs) from its cluster/family template, the rest fresh. Reproduces the v1 correlation cliff. Vectorized."""
    k = _kact(bs)
    n_clusters = max(1, min(n_clusters, V))
    n_sh = int(round(frac_shared * k))
    n_sh = max(0, min(k, n_sh))
    g = np.random.default_rng(seed)
    tmpl_idx = np.stack([g.choice(bs, size=k, replace=False) for _ in range(n_clusters)])  # (C,k)
    tmpl_sgn = (g.integers(0, 2, (n_clusters, k)).astype(np.float32) * 2.0 - 1.0)
    assign = g.integers(0, n_clusters, size=V)
    cb = np.zeros((V, bs), dtype=np.float32)
    rows = np.arange(V)[:, None]
    if n_sh > 0:
        sh_pos = np.argsort(g.random((V, k)), axis=1)[:, :n_sh]      # (V,n_sh) positions in [0,k)
        sh_dim = tmpl_idx[assign][rows, sh_pos]                      # (V,n_sh) block dims
        sh_sgn = tmpl_sgn[assign][rows, sh_pos]
        cb[rows, sh_dim] = sh_sgn
    n_fresh = k - n_sh
    if n_fresh > 0:
        fr_dim = g.integers(0, bs, size=(V, n_fresh))               # fresh dims (rare overlap w/ shared: ok)
        fr_sgn = (g.integers(0, 2, (V, n_fresh)).astype(np.float32) * 2.0 - 1.0)
        cb[rows, fr_dim] = fr_sgn
    return cb


# ============================================================
# Decoders: single-block (v1 algebra) + RNS/CRT
# ============================================================


def single_block_decode(toks, cb: np.ndarray, bs: int, D: int, N: int):
    """v1 block-local: compose D terms into disjoint blocks (sum), recover per block via V-way argmax."""
    comp = np.zeros(N, dtype=np.float32)
    for d in range(D):
        comp[d * bs:(d + 1) * bs] += cb[toks[d]]
    return [int(np.argmax(cb @ comp[d * bs:(d + 1) * bs])) for d in range(D)]


def rns_decode(toks, res_cbs, moduli, bs: int, sb: int, D: int, N: int, M, Mi, yi, scramble_perm=None):
    """RNS/CRT: each slot d's block subdivided into r disjoint sub-blocks; sub-block i holds residue
    (t mod mi) from residue codebook i (m_i-way). Recover each residue by sub-block argmax, then CRT.
    scramble_perm (a derangement) permutes the recovered residues before CRT -> reconstruction collapse."""
    r = len(moduli)
    comp = np.zeros(N, dtype=np.float32)
    for d in range(D):
        base = d * bs
        for i in range(r):
            comp[base + i * sb: base + (i + 1) * sb] += res_cbs[i][toks[d] % moduli[i]]
    rec = []
    for d in range(D):
        base = d * bs
        residues = [int(np.argmax(res_cbs[i] @ comp[base + i * sb: base + (i + 1) * sb])) for i in range(r)]
        if scramble_perm is not None:
            residues = [residues[scramble_perm[i]] for i in range(r)]
        rec.append(_crt(residues, moduli, M, Mi, yi))
    return rec


def _multiset_hits(recovered, truth) -> int:
    pool = list(recovered)
    hits = 0
    for x in truth:
        if x in pool:
            pool.remove(x)
            hits += 1
    return hits


def _score(rec, toks):
    D = len(toks)
    exact = 1.0 if list(rec) == list(toks) else 0.0
    per_term = sum(1 for d in range(D) if rec[d] == toks[d]) / D
    per_token = _multiset_hits(rec, toks) / D
    return per_term, exact, per_token


def _sample_props(V: int, D: int, trials: int, seed: int):
    rng = np.random.default_rng(90000 + seed)
    return [[int(x) for x in rng.choice(V, size=D, replace=False)] for _ in range(trials)]


def run_arm(decode_fn, props):
    pt = ex = tk = 0.0
    rec_all = []
    for toks in props:
        rec = decode_fn(toks)
        a, b, c = _score(rec, toks)
        pt += a; ex += b; tk += c
        rec_all.extend(rec)
    n = len(props)
    return {"per_term": pt / n, "exact_ordered": ex / n, "per_token": tk / n}, rec_all


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"grid": SELFTEST_GRID, "trials": 4, "seeds": (7,)}
    if mode == "smoke":
        return {"grid": SMOKE_GRID, "trials": 12, "seeds": SEEDS}
    return {"grid": FULL_GRID, "trials": 25, "seeds": SEEDS}


def _digest_int(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


def expected_units(cfg) -> int:
    return len(cfg["grid"]) * len(ARMS) * len(cfg["seeds"])


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    grid, trials, seeds = cfg["grid"], cfg["trials"], cfg["seeds"]
    per_unit = []
    rec_digests = {}
    eff = {}
    derange = [(i + 1) % R_MODULI for i in range(R_MODULI)]   # cyclic derangement (r=3 -> [1,2,0])
    total_units = expected_units(cfg)
    unit = 0

    for seed in seeds:
        for (V, D, region) in grid:
            bs = N_DIM // D
            sb = bs // R_MODULI
            moduli = MODULI[V]
            M, Mi, yi = _crt_setup(moduli)
            if M < V:
                raise ValueError(f"moduli product {M} < V={V} for {moduli}")
            props = _sample_props(V, D, trials, seed)

            cb_corr = corr_codebook(V, bs, 4000 + seed, N_CLUSTERS, FRAC_SHARED)
            cb_synth = iid_codebook(V, bs, 7000 + seed)
            res_cbs = [iid_codebook(moduli[i], sb, 6000 + seed * 10 + i) for i in range(R_MODULI)]

            s_corr, _ = run_arm(lambda tk: single_block_decode(tk, cb_corr, bs, D, N_DIM), props)
            s_syn, _ = run_arm(lambda tk: single_block_decode(tk, cb_synth, bs, D, N_DIM), props)
            s_rns, rec_rns = run_arm(
                lambda tk: rns_decode(tk, res_cbs, moduli, bs, sb, D, N_DIM, M, Mi, yi), props)
            s_scr, rec_scr = run_arm(
                lambda tk: rns_decode(tk, res_cbs, moduli, bs, sb, D, N_DIM, M, Mi, yi, derange), props)

            for arm, rec in (("single_corr", s_corr), ("single_synth", s_syn),
                             ("rns_crt", s_rns), ("rns_scram", s_scr)):
                unit += 1
                per_unit.append({"region": region, "V": V, "D": D, "seed": seed, "arm": arm,
                                 "per_term": round(rec["per_term"], 4),
                                 "exact_ordered": round(rec["exact_ordered"], 4),
                                 "per_token": round(rec["per_token"], 4)})
            eff[f"V{V}"] = {"V": V, "moduli": list(moduli), "M_effective_vocab": M,
                            "rns_codebook_entries": int(sum(moduli)),
                            "single_codebook_entries": V,
                            "codebook_compression_x": round(V / float(sum(moduli)), 2)}
            # arms_differ (META_RULE_AF): compare DISTINCT artifacts (not perfect-recovery token arrays).
            rec_digests[f"{V}_{D}_{seed}"] = {
                "cb_corr": _digest_arr(cb_corr),
                "cb_synth": _digest_arr(cb_synth),
                "res_cb0": _digest_arr(res_cbs[0]),
                "rec_rns": _digest_int(rec_rns),
                "rec_scram": _digest_int(rec_scr)}
            _heartbeat(output_dir, unit, total_units, t0,
                       extra={"V": V, "D": D, "seed": seed, "region": region,
                              "single_corr": round(s_corr["exact_ordered"], 3),
                              "single_synth": round(s_syn["exact_ordered"], 3),
                              "rns_crt": round(s_rns["exact_ordered"], 3),
                              "rns_scram": round(s_scr["exact_ordered"], 3)})
            _say(f"  [seed {seed}] V={V} D={D} ({region}) bs={bs} sb={sb} moduli={moduli} M={M}: "
                 f"single_corr exact={s_corr['exact_ordered']:.3f} | single_synth={s_syn['exact_ordered']:.3f} "
                 f"| rns_crt={s_rns['exact_ordered']:.3f} | rns_scram={s_scr['exact_ordered']:.3f}")

    return cfg, per_unit, rec_digests, eff


def _agg(per_unit, arm, V, D, key):
    vals = [u[key] for u in per_unit if u["arm"] == arm and u["V"] == V and u["D"] == D]
    return (float(np.mean(vals)) if vals else float("nan"),
            [round(float(v), 4) for v in vals])


def _cv(per_seed_vals):
    if not per_seed_vals:
        return float("nan")
    m = float(np.mean(per_seed_vals))
    if m == 0.0:
        return 0.0 if float(np.std(per_seed_vals)) == 0.0 else float("inf")
    return float(np.std(per_seed_vals)) / m


def classify(per_unit, cfg, mode: str):
    exp = expected_units(cfg)
    if len(per_unit) < exp:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {len(per_unit)}/{exp} units", False)

    aV, aD = ANCHOR_V, ANCHOR_D
    eV, eD = ENVELOPE_V, ENVELOPE_D
    have_env = any(u["V"] == eV and u["D"] == eD for u in per_unit)
    have_anc = any(u["V"] == aV and u["D"] == aD for u in per_unit)
    if not (have_env and have_anc):
        return ("SELFTEST_OK", "selftest ran (gate points not in grid)", True)

    rns_env_m, rns_env_s = _agg(per_unit, "rns_crt", eV, eD, "exact_ordered")
    rns_anc_m, rns_anc_s = _agg(per_unit, "rns_crt", aV, aD, "exact_ordered")
    sc_env_m, _ = _agg(per_unit, "single_corr", eV, eD, "exact_ordered")
    sc_anc_m, _ = _agg(per_unit, "single_corr", aV, aD, "exact_ordered")
    sy_env_m, _ = _agg(per_unit, "single_synth", eV, eD, "exact_ordered")
    sy_anc_m, _ = _agg(per_unit, "single_synth", aV, aD, "exact_ordered")
    scr_env_m, _ = _agg(per_unit, "rns_scram", eV, eD, "exact_ordered")
    scr_anc_m, _ = _agg(per_unit, "rns_scram", aV, aD, "exact_ordered")
    cv_env = _cv(rns_env_s)
    cv_anc = _cv(rns_anc_s)
    gap = rns_env_m - sc_env_m

    # cliff map (rns vs single_corr) across the sweep
    cmap = []
    for (Vg, Dg, region) in cfg["grid"]:
        r_m, _ = _agg(per_unit, "rns_crt", Vg, Dg, "exact_ordered")
        c_m, _ = _agg(per_unit, "single_corr", Vg, Dg, "exact_ordered")
        cmap.append(f"V{Vg}D{Dg}[rns={r_m:.2f},corr={c_m:.2f}]")

    diag = (f"ANCHOR(V{aV}D{aD}) rns={rns_anc_m:.3f} single_corr={sc_anc_m:.3f} single_synth={sy_anc_m:.3f} "
            f"scram={scr_anc_m:.3f}; ENVELOPE(V{eV}D{eD}) rns={rns_env_m:.3f}(cv={cv_env:.3f}) "
            f"single_corr={sc_env_m:.3f}(cliff) single_synth={sy_env_m:.3f} scram={scr_env_m:.3f} gap={gap:.3f}; "
            f"map[{' '.join(cmap)}]")

    # --- discriminator-fires gates (ALL modes incl smoke) ---
    if not (sy_env_m >= SYNTH_CEILING_FLOOR and sy_anc_m >= SYNTH_CEILING_FLOOR):
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"iid single-block ceiling did not recover (synth_env={sy_env_m:.3f} synth_anc={sy_anc_m:.3f} "
                f"< {SYNTH_CEILING_FLOOR}): block-local WIRING failed. {diag}", False)
    if not (sc_env_m < SINGLE_CLIFF_THRESH):
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"single_corr did NOT cliff at envelope (single_corr_env={sc_env_m:.3f} >= "
                f"{SINGLE_CLIFF_THRESH}): correlated baseline is not in the failing regime, no headroom for "
                f"RNS to differentiate. Regime too easy -- re-spec correlation/V. {diag}", False)
    if not (scr_env_m <= SCRAM_COLLAPSE and scr_anc_m <= SCRAM_COLLAPSE):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"scrambled-residue control did not collapse (scram_env={scr_env_m:.3f} scram_anc={scr_anc_m:.3f} "
                f"> {SCRAM_COLLAPSE}): CRT reconstruction is not load-bearing / decode leaks order. {diag}", False)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: single_corr CLIFFS at envelope ({sc_env_m:.3f}<{SINGLE_CLIFF_THRESH}), "
                f"rns_crt HOLDS ({rns_env_m:.3f}) with gap={gap:.3f}, scram COLLAPSES ({scr_env_m:.3f}), "
                f"iid ceiling recovers ({sy_env_m:.3f}); all at N={N_DIM} D={eD} V={eV}. Deliverable band is "
                f"FULL-only (canonical = remote landing). {diag}", True)

    # --- FULL pre-registered bands (gate on rns_crt vs single_corr at anchor + envelope) ---
    if (rns_env_m >= HP_RNS_FLOOR and rns_anc_m >= HP_RNS_FLOOR and cv_env < HP_CV and cv_anc < HP_CV
            and gap >= RNS_GAP):
        return ("HARD_PASS",
                f"RNS/CRT PUSHES PAST THE CLIFF: rns_crt exact-ordered={rns_env_m:.3f} (>= {HP_RNS_FLOOR}, "
                f"cv={cv_env:.3f}<{HP_CV}) at V={eV} D={eD} where the v1-style correlated single-block has "
                f"fallen off the cliff (single_corr={sc_env_m:.3f}; gap={gap:.3f}>= {RNS_GAP}). Effective vocab "
                f"= prod(moduli) reached with sum(moduli) codes. iid ceiling ({sy_env_m:.3f}) confirms the "
                f"cliff is a correlation artifact; scram control collapses ({scr_env_m:.3f}) confirms CRT is "
                f"load-bearing. {diag}", True)
    if rns_env_m < HF_RNS_FLOOR or gap <= 0.0:
        return ("HARD_FAIL",
                f"RNS/CRT does NOT push past the cliff: rns_crt={rns_env_m:.3f} (< {HF_RNS_FLOOR}) OR ties/loses "
                f"single_corr (gap={gap:.3f}<=0) -- per-residue errors cancel the capacity gain. {diag}", True)
    return ("MIDDLE_BAND",
            f"partial envelope-push: rns_crt={rns_env_m:.3f} in [{HF_RNS_FLOOR},{HP_RNS_FLOOR}) or gap={gap:.3f} "
            f"in (0,{RNS_GAP}) or cv too high (cv_env={cv_env:.3f}). Needs regime nudge. {diag}", True)


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp = expected_units(cfg)
    _write_start_marker(output_dir, mode, exp)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} grid={cfg['grid']} seeds={cfg['seeds']} "
         f"trials={cfg['trials']} r_moduli={R_MODULI} expected_units={exp}")

    # formula self-test (CRT correctness + coprimality) for every moduli set in play -- ALL modes.
    for V in sorted({V for (V, _D, _r) in cfg["grid"]}):
        if not crt_selftest(MODULI[V]):
            raise AssertionError(f"CRT_SELFTEST_FAIL for V={V} moduli={MODULI[V]} "
                                 f"(coprimality or reconstruction incorrect)")
    _say(f"[{ANCHOR_NAME}] CRT formula self-test PASSED for moduli {[MODULI[V] for V in sorted({v for (v,_d,_r) in cfg['grid']})]}")

    cfg, per_unit, rec_digests, eff = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): DISTINCT mechanism artifacts must differ; scramble must alter output.
    arms_differ_ok = True
    reasons = []
    for key, dg in rec_digests.items():
        if dg["cb_corr"] == dg["cb_synth"]:
            arms_differ_ok = False; reasons.append(f"{key}:corr==synth codebook")
        if dg["cb_corr"] == dg["res_cb0"] or dg["cb_synth"] == dg["res_cb0"]:
            arms_differ_ok = False; reasons.append(f"{key}:single==residue codebook")
        if dg["rec_rns"] == dg["rec_scram"]:
            arms_differ_ok = False; reasons.append(f"{key}:scramble did not alter output")
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, order_ok = classify(per_unit, cfg, mode)
    elapsed = time.perf_counter() - t0

    def arm_summary(arm, V, D):
        pt_m, pt_v = _agg(per_unit, arm, V, D, "per_term")
        ex_m, ex_v = _agg(per_unit, arm, V, D, "exact_ordered")
        tk_m, tk_v = _agg(per_unit, arm, V, D, "per_token")
        return {"per_term_mean": round(pt_m, 4), "per_term_per_seed": pt_v,
                "exact_ordered_mean": round(ex_m, 4), "exact_ordered_per_seed": ex_v,
                "exact_ordered_cv": round(_cv(ex_v), 4),
                "per_token_mean": round(tk_m, 4), "per_token_per_seed": tk_v}

    grid_summary = {}
    for (V, D, region) in cfg["grid"]:
        for arm in ARMS:
            grid_summary[f"{arm}@V{V}D{D}"] = arm_summary(arm, V, D)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: RNS/CRT high-vocab generation envelope-push vs single-block ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "config": {"N": N_DIM, "F_SPARSE": F_SPARSE, "R_MODULI": R_MODULI,
                   "N_CLUSTERS": N_CLUSTERS, "FRAC_SHARED": FRAC_SHARED,
                   "grid": [[V, D, r] for (V, D, r) in cfg["grid"]],
                   "anchor": [ANCHOR_V, ANCHOR_D], "envelope": [ENVELOPE_V, ENVELOPE_D],
                   "trials": cfg["trials"], "seeds": list(cfg["seeds"]), "moduli": {str(k): list(v) for k, v in MODULI.items()},
                   "mechanism": "rns_crt_subblock_decomposition", "algebra": "block_superposition_sum",
                   "position_binding": "disjoint_block_index", "residue_binding": "disjoint_subblock_index"},
        "arms": grid_summary,
        "per_unit": per_unit,
        "efficiency": eff,
        "controls": {"scram_collapsed": order_ok},
        "arms_differ_verified": arms_differ_ok,
        "bands": {"HP_rns_floor": HP_RNS_FLOOR, "HP_cv": HP_CV, "single_cliff_thresh": SINGLE_CLIFF_THRESH,
                  "rns_gap": RNS_GAP, "scram_collapse": SCRAM_COLLAPSE, "synth_ceiling_floor": SYNTH_CEILING_FLOOR,
                  "HF_rns_floor": HF_RNS_FLOOR},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    ok_crt = all(crt_selftest(MODULI[V]) for V in MODULI)
    cfg, per_unit, _dg, _eff = run_all("selftest", output_dir, t0)
    V, D, _r = SELFTEST_GRID[0]
    rns_m, _ = _agg(per_unit, "rns_crt", V, D, "exact_ordered")
    syn_m, _ = _agg(per_unit, "single_synth", V, D, "exact_ordered")
    scr_m, _ = _agg(per_unit, "rns_scram", V, D, "exact_ordered")
    ok = ok_crt and (rns_m >= 0.90) and (syn_m >= 0.90) and (scr_m <= 0.10)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: crt_ok={ok_crt} rns_crt={rns_m:.3f} "
         f"single_synth={syn_m:.3f} rns_scram={scr_m:.3f} [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
