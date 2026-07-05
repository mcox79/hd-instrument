"""exp_reasoning_depth_keyslots_sharding_v1

REDIRECT TEST of the proven collision-bound reasoning-depth ceiling.

A prior cell (exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1) proved the
reasoning-depth ceiling of a shared Hebbian associative store is COLLISION-BOUND
(chain-key capacity), N-INDEPENDENT -- NOT crosstalk, NOT cleanup-bound. The depth
ceiling is set by chain-key COLLISION: storing N_TEST chains of length D_MAX puts
N_TEST*D_MAX (source,relation)->object edges over V_CHAIN*P_REL distinct key slots;
when that fill grows, keys carry multiple objects and retrieval is ambiguous.
MEASURED @ N=8192, K_SLOTS=2048: N_TEST 25 -> usable_ss ~9 (floor 0.5).
The recorded REDIRECT: deeper chains come from MORE KEY SLOTS (richer relation/node
vocabulary -> more distinct chain keys, lower collision) + SHARDED storage (partition
chains across shards to reduce per-shard collision). THIS CELL tests that redirect.

--------------------------------------------------------------------------------
LOAD-BEARING COMPARISON (paired by (seed, N_TEST, N); matched difficulty + fidelity)
--------------------------------------------------------------------------------
usable chain depth at BASELINE key-capacity vs EXPANDED key-slots AND vs SHARDED
storage, at MATCHED difficulty (same N_TEST, D_MAX, N, M/N) and the single-hop
fidelity floor (d1 >= 0.80). Two levers, predicted by the collision model to act
through the SAME mechanism (effective key capacity):

ARM_BASELINE      -- P_REL=8, S=1 bundled store. K=V_CHAIN*8=2048. Reproduces the
                     prior collision-bound ceiling. REFERENCE (the depth to beat).
ARM_KEYSLOTS_2x   -- P_REL=16, S=1. Richer RELATION vocab -> K=4096 (2x). Lever 1.
ARM_KEYSLOTS_4x   -- P_REL=32, S=1. K=8192 (4x). Lever 1 (stronger).
ARM_SHARD_2       -- P_REL=8, S=2. Partition the SAME base chains across 2 shards
                     by chain-id, route each walk to its chain's shard -> fill per
                     shard halves. Effective capacity 4096 (2x). Lever 2.
ARM_SHARD_4       -- P_REL=8, S=4. Effective capacity 8192 (4x). Lever 2 (stronger).
ARM_SHUFFLED_CTL  -- P_REL=32, S=1 store with OBJECTS label-shuffled (structure
                     destroyed) -> fidelity ~ chance (1/V). BROKEN-DISCRIMINATOR
                     RAIL (discriminator-fires control).

Cleanup = single-shot argmax (the MAP decoder for a near-orthogonal codebook; the
prior cell PROVED iterative/resonator cleanup is bit-identical to it, so cleanup-type
is FIXED and key-capacity is the sole mechanism axis).

Chains are NESTED per arm (walked once to D_MAX, prefix-accuracy at every depth);
SHARD arms reuse the BASELINE chains (identical-chain paired, only storage differs);
KEYSLOTS arms draw fresh chains at the richer relation vocab (same seed/difficulty).

usable_depth(arm) = largest d s.t. fidelity(1..d) are ALL >= FLOOR (0.5), contiguous
from 1. crossing_depth = the fidelity=0.5 crossing interpolated (continuous; used for
the cross-seed cv<0.10 stability gate; robust to integer quantization).

--------------------------------------------------------------------------------
COLLISION MODEL (the prediction; REPORTED to confirm the mechanism)
--------------------------------------------------------------------------------
effective_key_capacity(arm) = V_CHAIN * P_REL * S. effective chain-edge fill per
store = (N_TEST/S) * D_MAX / (V_CHAIN*P_REL). Occupancy collision fraction of chain
edges over K slots with M edges: collision_frac_theo = 1 - ((K-1)/K)^(M-1). Per-hop
clean prob p_clean ~ (1 - collision_frac); regenerative depth survives while all hops
clean, so predicted_usable ~ ln(0.5)/ln(p_clean). PREDICTION: usable_depth rises with
effective_key_capacity and falls with collision_frac; KEYSLOTS_2x and SHARD_2 (equal
effective capacity 4096) predict ~EQUAL usable_depth (both levers act through the same
collision physics) -- the killer mechanism cross-check. collision_frac (empirical +
theoretical) reported at each key-capacity.

--------------------------------------------------------------------------------
BANDS (per (N, seed); disc = the best-extending mechanism arm)
--------------------------------------------------------------------------------
FAIR op-point requires BASELINE IN BAND: usable(base) in [SS_BAND_LO, D_MAX-1] AND
base d1 >= 0.80 (single-hop store works AND baseline collapses within the window so
there is HEADROOM to extend). best_delta = max over mechanism arms of
(usable(arm) - usable(base)) (a censored-high mechanism arm counts usable=D_MAX).
  HARD_PASS   : base in band AND best_delta >= HP_DEPTH_MARGIN (>=2 more usable hops
                = clear rightward shift of the collision cliff) AND control usable
                <= 1 AND arms differ AND base d1 sane. Cross-seed cv<0.10 on the
                continuous crossing_depth of base and the disc arm (aggregate gate).
                => the ceiling IS collision-bound; more key slots / sharding EXTEND it.
  HARD_FAIL   : base in band AND best_delta <= 0 (NO lever extends usable depth) ->
                the ceiling is NOT collision-bound after all, or sharding doesn't help.
  HARD_FAIL_CTL: control usable_depth > 1 (broken rail recovers structure).
  ITERATE_REGIME: base not in band (saturates >D_MAX-1 or floors) -- REPORTED, not a
                refutation (needs harder N_TEST or deeper D_MAX at this N).
  MIDDLE_BAND : 0 < best_delta < HP_DEPTH_MARGIN (extends a little), OR extends but
                cross-seed unstable (cv>=0.10), OR all-N ITERATE_REGIME.
REPORTED (first-class): the capacity law usable_depth vs effective_key_capacity;
  collision_frac (emp+theo) per arm; the KEYSLOTS_2x==SHARD_2 equivalence; predicted
  vs measured usable_depth; per-arm depth-fidelity curves; N-independence of the law.
AGGREGATE: cell HARD_PASS iff >=1 N-tier majority HARD_PASS with cross-seed cv<0.10
  and no HARD_FAIL_CTL. Cell HARD_FAIL iff majority N-tiers HARD_FAIL (no lever extends
  = collision-bound model refuted). All-N ITERATE_REGIME -> MIDDLE_BAND.

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (6 arms; base != every mechanism arm; AF hash).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/discriminator_reachability: baseline depth curve spans ~0.96->chance across
#   D=1..18 (fill_base ~ 0.28 at N_TEST=32); mechanism arms lower fill -> deeper.
#   The discriminating band [0.30,0.70] is richly populated by every arm's depth curve.
# - baseline_in_band (META_RULE_AG): disc REQUIRES usable(base) in [SS_BAND_LO,D_MAX-1].
#   MEASURED prior @K=2048 N_TEST=25 D=12 -> usable 9; at N_TEST=32 D=18 expect ~5-6.
# - discriminator survives scale: the collision law is N-INDEPENDENT (occupancy over
#   key slots, not dimension) -- MEASURED N-independent by the prior cell; FULL runs
#   N in {8192,16384} to CONFIRM. Smoke runs at FULL N=8192 (option A/C preview).
# - HARD_PASS strictly above floor (best_delta>=2 vs HF best_delta<=0).
# - HP_SCOPE per-arm (prereg): HARD_PASS gates apply to mechanism arms; control gets
#   only the usable<=1 chance gate; baseline gets only the in-band gate.
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = seeds x N x N_TEST).
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = default_ok (P_REL/S/BETA are FIXED principled values, NOT
#   tuned-for-PASS; the equivalence KEYSLOTS_2x==SHARD_2 is a parameter-free prediction).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg.
# - progress_logging = line_buffered_stdout + print flush (timeout_s >= 1800).
# - start_marker + crash_diagnostic + heartbeat (defensive error checking).
# - positive_control (Gate D): ARM_BASELINE at N=8192 reproduces the prior collision-
#   bound ceiling (d1>=0.80 single-hop; graceful decay; usable in band) at the SAME
#   V=512/V_CHAIN=256/P=8 regime -> validates the reused scaffold.
--------------------------------------------------------------------------------
Compute architecture: SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 -- genuine
chained-retrieval sequential dependency exemption) + the cell IS the substrate cleanup
primitive being validated. Storage = MIXED: bundled-Hebbian per shard; sharding IS the
swept mechanism axis (S=1 bundled baseline is the discriminator reference per
META_STORAGE_STRATEGY exemption (b) -- explicitly testing bundle-vs-sharded key
capacity). Retrieval is the FACTORED store (no N x N materialization), M-chunked numpy
batched matmul across all test chains per hop; sharded retrieval routes each chain to
its shard's store by chain-id (the shard tag travels with the query in single-chain
walk -- KEYSLOTS lever needs NO routing oracle and stands alone if sharding is discounted).

PROT-018: no _n<N> suffix in anchor (this is an N-independent collision law; N is a
confirm axis, not the axis). ASCII-only; no unicode; no emojis; no em-dashes.
Author: exp_dev 2026-07-05.
"""
from __future__ import annotations

import sys

# progress_logging: line-buffered stdout so print() flushes on newline (FULL may run
# > 30 min on remote CPU at N=16384; see prereg progress_logging field).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "reasoning_depth_keyslots_sharding_v1"
_LLM_CALL_COUNTER = [0]  # substrate-only assert: must stay 0

# ---------------------------------------------------------------------------
# CLI + RUN_MODE (defaults to full per META_RULE 16; --smoke / --self-test flip;
# runner injects HDLAB_RUN_MODE=full and invokes bare, so env is the real channel)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_ENV_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _ENV_MODE == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
USABLE_FLOOR = 0.50
USABLE_FLOOR_SECONDARY = 0.30

# Fixed codebook geometry (matches the prior collision-bound cell for the positive
# control). Node codebook V_CODE is FIXED across all arms so chance-floor + crosstalk
# are constant -- the ONLY thing that changes across KEYSLOTS arms is P_REL (relation
# vocab), keeping the comparison clean.
V_CODE = 512          # total node codebook size (chance floor = 1/512)
V_CHAIN = 256         # chain nodes drawn from [0, V_CHAIN); background from [V_CHAIN, V_CODE)
BASELINE_P = 8        # baseline relation vocab (the prior regime)
P_REL_MAX = 32        # R codebook rows (largest relation vocab used)
MOVERN_FIXED = 1.0    # background fills to M/N=1 (crosstalk regime is the prior regime)

# Mechanism arms (label, p_rel, n_shards, shuffle_objects, reuse_base_chains).
# effective_key_capacity = V_CHAIN * p_rel * n_shards.
ARMS: List[Dict[str, Any]] = [
    {"label": "baseline",    "p_rel": 8,  "shards": 1, "shuffle": False, "reuse_base": True},
    {"label": "keyslots_2x", "p_rel": 16, "shards": 1, "shuffle": False, "reuse_base": False},
    {"label": "keyslots_4x", "p_rel": 32, "shards": 1, "shuffle": False, "reuse_base": False},
    {"label": "shard_2",     "p_rel": 8,  "shards": 2, "shuffle": False, "reuse_base": True},
    {"label": "shard_4",     "p_rel": 8,  "shards": 4, "shuffle": False, "reuse_base": True},
    {"label": "control",     "p_rel": 32, "shards": 1, "shuffle": True,  "reuse_base": False},
]
BASE_ARM = "baseline"
MECH_ARMS = ["keyslots_2x", "keyslots_4x", "shard_2", "shard_4"]
KEYSLOTS_ARMS = ["keyslots_2x", "keyslots_4x"]
SHARD_ARMS = ["shard_2", "shard_4"]
CTL_ARM = "control"


def eff_key_capacity(p_rel: int, shards: int) -> int:
    return V_CHAIN * p_rel * shards


def eff_fill(n_test: int, d_max: int, p_rel: int, shards: int) -> float:
    """Effective chain-edge fill per store = (N_TEST/S)*D_MAX / (V_CHAIN*P_REL)."""
    return round((n_test / float(shards)) * d_max / float(V_CHAIN * p_rel), 4)


if RUN_MODE == "self_test":
    N_LIST = [512]
    NTEST_TARGETS = [8]
    SEEDS = [0]
    D_MAX = 6
    DEPTHS = [1, 2, 3, 4, 5, 6]
elif RUN_MODE == "smoke":
    # Discriminator preview AT FULL N=8192 (option A/C). One difficulty N_TEST=32 puts
    # baseline IN BAND (fill_base ~ 0.281 -> usable ~5-6, headroom to D=18), 3 seeds for
    # cross-seed cv. The collision law is N-INDEPENDENT (prior MEASURED) so single N is
    # analytically justified for the preview.
    N_LIST = [8192]
    NTEST_TARGETS = [32]
    SEEDS = [7, 17, 23]
    D_MAX = 18
    DEPTHS = list(range(1, 19))
else:  # full
    # Sweep N_TEST (difficulty) to show the rightward cliff-shift at 3 operating points;
    # N in {8192,16384} confirms the law is N-independent (collision = key slots, not dim).
    N_LIST = [8192, 16384]
    NTEST_TARGETS = [24, 32, 40]
    SEEDS = [7, 17, 23, 31, 41]
    D_MAX = 18
    DEPTHS = list(range(1, 19))

# Operating band + HARD gates.
SS_BAND_LO = 2             # usable(base) >= this (single-hop store works within window)
HP_DEPTH_MARGIN = 2        # best mechanism usable - base usable >= 2 (real cliff shift)
HP_CTL_USABLE_MAX = 1      # control usable_depth <= 1 (structure -> chance)
HP_D1_SANITY = 0.80        # single-hop store works (base d1 >= this)
HP_CV_MAX = 0.10           # cross-seed cv of continuous crossing_depth (base + disc)
EQUIV_TOL = 2.0            # |usable(keyslots_2x)-usable(shard_2)| <= this == equivalence

# Positive control (Gate D): baseline at N=8192 reproduces the prior collision-bound
# ceiling (d1 sanity + baseline collapses in-band). CITED prior regime.
PC_N = 8192
# CITED@data/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_smoke/metrics.json
#   (K=2048, N_TEST=25, D=12 -> usable_ss ~9); here N_TEST=32/D=18 -> expect base ~5-6.

CHANCE_FLOOR = 1.0 / V_CODE
EXPECTED_N_UNITS = len(SEEDS) * len(N_LIST) * len(NTEST_TARGETS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%s,V=%d,V_CHAIN=%d,BASE_P=%d,PMAX=%d,D_MAX=%d,MOVERN=%.2f,NTEST=%s,"
    "SEEDS=%s,RUN_MODE=%s,arms=%s,store=FACTORED_HEBBIAN_sharded,difficulty=NTEST_collision,"
    "hardening=startmarker+crashdiag+heartbeat+AF+AH+AG"
) % (
    ANCHOR_NAME, "-".join(str(n) for n in N_LIST), V_CODE, V_CHAIN, BASELINE_P, P_REL_MAX,
    D_MAX, MOVERN_FIXED, "-".join(str(nt) for nt in NTEST_TARGETS),
    "-".join(str(s) for s in SEEDS), RUN_MODE, "-".join(a["label"] for a in ARMS),
)


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers (start marker / crash / heartbeat)
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "expected_n_units": expected_units, "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
        "pid": os.getpid(), "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float,
               extra: Optional[Dict[str, Any]] = None) -> None:
    row = {"ts_iso": _now_iso(), "unit_idx": unit_idx, "total_units": total_units,
           "elapsed_s": round(time.perf_counter() - t0, 2)}
    if extra:
        row["extra"] = extra
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass  # heartbeat best-effort; never fail the run on a log write


# ---------------------------------------------------------------------------
# Substrate primitives (numpy, CPU)
# ---------------------------------------------------------------------------
def make_bipolar(rows: int, n: int, g: np.random.Generator) -> np.ndarray:
    """rows x n bipolar (+/-1) float32 codebook."""
    return (g.integers(0, 2, size=(rows, n)).astype(np.float32) * 2.0 - 1.0)


def _chunk_for(n_dim: int) -> int:
    """Edge-chunk size bounding a block to ~256 MB (adaptive to N)."""
    return max(256, (1 << 26) // n_dim)


class FactoredStore:
    """Hebbian associative store held as EDGE-INDEX lists (NEVER materializes N x N W
    NOR the full (M, N) key/value matrices). retrieve(x) = x @ W.T where
    W = sum_e outer(E[o_e], E[s_e]*R[p_e]) / N. Self-test T0 proves it equals W @ x."""

    __slots__ = ("s", "p", "o", "E", "R", "n_dim", "chunk", "_edge_key")

    def __init__(self, s: np.ndarray, p: np.ndarray, o: np.ndarray,
                 E: np.ndarray, R: np.ndarray, n_dim: int):
        self.s = np.ascontiguousarray(s.astype(np.int64))
        self.p = np.ascontiguousarray(p.astype(np.int64))
        self.o = np.ascontiguousarray(o.astype(np.int64))
        self.E = E
        self.R = R
        self.n_dim = int(n_dim)
        self.chunk = _chunk_for(n_dim)
        h = hashlib.sha256()
        h.update(self.s.tobytes()); h.update(self.p.tobytes()); h.update(self.o.tobytes())
        self._edge_key = h.hexdigest()[:16]

    def retrieve(self, keys: np.ndarray) -> np.ndarray:
        """keys: (B, N) -> yhat: (B, N)."""
        m = self.s.shape[0]
        out = np.zeros((keys.shape[0], self.n_dim), dtype=np.float32)
        if m == 0 or keys.shape[0] == 0:
            return out
        for c0 in range(0, m, self.chunk):
            sl = slice(c0, c0 + self.chunk)
            kc = self.E[self.s[sl]] * self.R[self.p[sl]]   # (c, N) key vectors
            coeff = keys @ kc.T                             # (B, c)
            out += coeff @ self.E[self.o[sl]]               # (B, N)
        out /= float(self.n_dim)
        return out.astype(np.float32)

    def sha_edges(self) -> str:
        return self._edge_key


class ShardedStore:
    """S FactoredStores + a per-chain shard_id (aligned to batch/walk order). retrieve
    routes each chain's key to its shard's store (chain i -> shard i % S). Duck-typed
    retrieve(keys)->(B,N) so walk_curve consumes it identically to a FactoredStore."""

    __slots__ = ("stores", "shard_id", "n_dim")

    def __init__(self, stores: List[FactoredStore], shard_id: np.ndarray):
        assert len(stores) >= 1
        self.stores = stores
        self.shard_id = np.ascontiguousarray(shard_id.astype(np.int64))
        self.n_dim = stores[0].n_dim

    def retrieve(self, keys: np.ndarray) -> np.ndarray:
        out = np.zeros((keys.shape[0], self.n_dim), dtype=np.float32)
        for s_idx, st in enumerate(self.stores):
            idx = np.where(self.shard_id == s_idx)[0]
            if idx.size:
                out[idx] = st.retrieve(keys[idx])
        return out

    def sha_edges(self) -> str:
        h = hashlib.sha256()
        for st in self.stores:
            h.update(st.sha_edges().encode("ascii"))
        h.update(self.shard_id.tobytes())
        return h.hexdigest()[:16]


def build_W_reference(s: np.ndarray, p: np.ndarray, o: np.ndarray,
                      E: np.ndarray, R: np.ndarray, n_dim: int) -> np.ndarray:
    """Materialized Hebbian W (REFERENCE ONLY; self-test T0 proves factored == this)."""
    if s.shape[0] == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    k = E[s] * R[p]
    vv = E[o]
    return (vv.T @ k).astype(np.float32) / float(n_dim)


def argmax_clean(yhat: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Single-shot cleanup: snap each row of yhat (B, N) to nearest atom -> ids (B,)."""
    return np.argmax(yhat @ E.T, axis=1)


def _sha_of_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Chain generation (nested; reserved node partitions)
# ---------------------------------------------------------------------------
def make_chains(n_chains: int, d_max: int, p_rel: int, g: np.random.Generator) -> np.ndarray:
    """(n_chains, d_max, 3) int (s, p, o) using chain-partition nodes + p_rel relations."""
    chains = np.zeros((n_chains, d_max, 3), dtype=np.int64)
    for c in range(n_chains):
        nodes = [int(g.integers(0, V_CHAIN))]
        for _ in range(d_max):
            nxt = int(g.integers(0, V_CHAIN))
            while nxt == nodes[-1]:
                nxt = int(g.integers(0, V_CHAIN))
            nodes.append(nxt)
        for i in range(d_max):
            chains[c, i, 0] = nodes[i]
            chains[c, i, 1] = int(g.integers(0, p_rel))
            chains[c, i, 2] = nodes[i + 1]
    return chains


def make_background_edges(m_bg: int, p_rel: int, g: np.random.Generator) -> np.ndarray:
    """(m_bg, 3) distractor edges with SOURCE in [V_CHAIN, V_CODE) (never key-collide
    with chain keys), object anywhere, relation in [0, p_rel)."""
    if m_bg <= 0:
        return np.zeros((0, 3), dtype=np.int64)
    s = g.integers(V_CHAIN, V_CODE, size=m_bg)
    p = g.integers(0, p_rel, size=m_bg)
    o = g.integers(0, V_CODE, size=m_bg)
    return np.stack([s, p, o], axis=1).astype(np.int64)


# ---------------------------------------------------------------------------
# Collision-fraction measurement (empirical + theoretical occupancy)
# ---------------------------------------------------------------------------
def empirical_collision_frac(chain_edges: np.ndarray, p_rel: int) -> float:
    """Fraction of chain edges whose (s,p) key maps to >= 2 DISTINCT objects (the
    ambiguity that limits chain depth). chain_edges: (M, 3) int."""
    m = chain_edges.shape[0]
    if m == 0:
        return 0.0
    key_to_objs: Dict[int, set] = {}
    for i in range(m):
        s = int(chain_edges[i, 0]); p = int(chain_edges[i, 1]); o = int(chain_edges[i, 2])
        key = s * p_rel + p
        key_to_objs.setdefault(key, set()).add(o)
    colliding = 0
    for i in range(m):
        s = int(chain_edges[i, 0]); p = int(chain_edges[i, 1])
        key = s * p_rel + p
        if len(key_to_objs[key]) >= 2:
            colliding += 1
    return round(colliding / float(m), 4)


def theoretical_collision_frac(m_edges: int, key_slots: int) -> float:
    """Occupancy model: prob an edge shares its slot with >= 1 other edge =
    1 - ((K-1)/K)^(M-1). THEORETICAL@occupancy."""
    if m_edges <= 1 or key_slots <= 0:
        return 0.0
    return round(1.0 - ((key_slots - 1) / float(key_slots)) ** (m_edges - 1), 4)


def predicted_usable_depth(collision_frac: float, d_max: int) -> float:
    """predicted_usable ~ ln(0.5)/ln(p_clean), p_clean = 1 - collision_frac.
    THEORETICAL@regenerative-chain-survival."""
    p_clean = max(1e-6, 1.0 - collision_frac)
    if p_clean >= 1.0 - 1e-9:
        return float(d_max)
    val = math.log(0.5) / math.log(p_clean)
    return round(min(float(d_max), max(0.0, val)), 2)


# ---------------------------------------------------------------------------
# Depth-curve walk (batched across chains; regenerative clean-codeword carry).
# ONE-PASS depth curve == per-depth re-walk (self-test T2), at ~1/len(depths) cost.
# ---------------------------------------------------------------------------
def walk_curve(chains: np.ndarray, store: Any, E: np.ndarray, R: np.ndarray,
               depths: List[int], clean_fn: Callable[[np.ndarray], np.ndarray]) -> Dict[str, Any]:
    dmax = max(depths)
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    assert x.base is None, "scratchpad must be a fresh array (separate register)"
    curve: Dict[int, float] = {}
    preds: Dict[int, np.ndarray] = {}
    for k in range(dmax):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = store.retrieve(key)
        pred = clean_fn(yhat)
        d = k + 1
        if d in depths:
            curve[d] = float(np.mean(pred == chains[:, d - 1, 2]))
            preds[d] = pred
        x = E[pred].astype(np.float32)
    return {"curve": curve, "preds": preds}


def usable_depth(curve: Dict[int, float], depths: List[int], floor: float) -> int:
    """Contiguous-from-1 sustained usable depth. 0 if even d1 below floor."""
    ud = 0
    for d in sorted(depths):
        if curve.get(d, 0.0) >= floor:
            ud = d
        else:
            break
    return ud


def crossing_depth(curve: Dict[int, float], depths: List[int], floor: float) -> float:
    """Continuous fidelity=floor crossing (linear interp between last-above and first-
    below); D_MAX if never crosses (censored lower bound); 0 if d1 below floor. Used
    for the cross-seed cv gate (robust to integer quantization)."""
    ds = sorted(depths)
    if curve.get(ds[0], 0.0) < floor:
        return 0.0
    last_above = ds[0]
    for d in ds:
        if curve.get(d, 0.0) >= floor:
            last_above = d
        else:
            hi = curve.get(last_above, 0.0); lo = curve.get(d, 0.0)
            frac = (hi - floor) / (hi - lo) if hi > lo else 0.0
            return round(last_above + frac, 3)
    return float(ds[-1])  # censored: sustained to D_MAX


# ---------------------------------------------------------------------------
# Store builders per arm
# ---------------------------------------------------------------------------
def build_arm_store(arm: Dict[str, Any], chains: np.ndarray, m_bg: int,
                    E: np.ndarray, R: np.ndarray, n_dim: int,
                    g: np.random.Generator) -> Tuple[Any, np.ndarray, np.ndarray]:
    """Returns (store, chain_edges, shard_id). chain_edges is (M_chain, 3) for collision
    measurement; shard_id is per-chain (batch order). Background edges split across shards."""
    p_rel = int(arm["p_rel"]); shards = int(arm["shards"])
    n_test = chains.shape[0]
    chain_edges = chains.reshape(-1, 3)
    bg = make_background_edges(m_bg, p_rel, g)

    if shards == 1:
        all_e = np.concatenate([chain_edges, bg], axis=0)
        o_col = all_e[:, 2]
        if arm["shuffle"]:
            perm = g.permutation(V_CODE)
            o_col = perm[all_e[:, 2]]
        store = FactoredStore(all_e[:, 0], all_e[:, 1], o_col, E, R, n_dim)
        return store, chain_edges, np.zeros(n_test, dtype=np.int64)

    # sharded: chain i -> shard (i % S); each shard bundles its chains' edges + bg/S.
    shard_id = np.arange(n_test, dtype=np.int64) % shards
    bg_split = np.array_split(bg, shards) if bg.shape[0] else [np.zeros((0, 3), np.int64)] * shards
    stores: List[FactoredStore] = []
    for s_idx in range(shards):
        chain_idx = np.where(shard_id == s_idx)[0]
        ce = chains[chain_idx].reshape(-1, 3) if chain_idx.size else np.zeros((0, 3), np.int64)
        bgs = bg_split[s_idx]
        se = np.concatenate([ce, bgs], axis=0) if bgs.shape[0] else ce
        if se.shape[0] == 0:
            se = np.zeros((0, 3), np.int64)
        stores.append(FactoredStore(se[:, 0], se[:, 1], se[:, 2], E, R, n_dim))
    return ShardedStore(stores, shard_id), chain_edges, shard_id


# ---------------------------------------------------------------------------
# One (N, seed, N_TEST) unit -> all arms' depth curves + usable depths + collision
# ---------------------------------------------------------------------------
def run_unit(n_dim: int, seed: int, n_test: int, out_dir: Path,
             hb_state: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    chain_edge_count = n_test * D_MAX
    m_total_target = int(round(MOVERN_FIXED * n_dim))
    m_bg = max(0, m_total_target - chain_edge_count)

    # deterministic per-unit RNG; codebooks sized to P_REL_MAX (shared across arms).
    g = np.random.default_rng(seed * 100003 + n_dim * 7 + n_test)
    E = make_bipolar(V_CODE, n_dim, g)
    R = make_bipolar(P_REL_MAX, n_dim, g)

    # base chains (p_rel = BASELINE_P) reused by baseline + shard arms.
    base_chains = make_chains(n_test, D_MAX, BASELINE_P, g)

    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_preds_final: Dict[str, np.ndarray] = {}
    for arm in ARMS:
        label = arm["label"]; p_rel = int(arm["p_rel"]); shards = int(arm["shards"])
        if arm["reuse_base"]:
            chains = base_chains
        else:
            # fresh chains at this relation vocab (same seed/difficulty, distinct stream).
            gg = np.random.default_rng(seed * 100003 + n_dim * 7 + n_test + hash(label) % 9973)
            chains = make_chains(n_test, D_MAX, p_rel, gg)

        store, chain_edges, shard_id = build_arm_store(arm, chains, m_bg, E, R, n_dim, g)
        r = walk_curve(chains, store, E, R, DEPTHS, lambda y: argmax_clean(y, E))
        curve = {d: round(v, 4) for d, v in r["curve"].items()}
        ud = usable_depth(curve, DEPTHS, USABLE_FLOOR)
        ud_sec = usable_depth(curve, DEPTHS, USABLE_FLOOR_SECONDARY)
        xd = crossing_depth(curve, DEPTHS, USABLE_FLOOR)

        # collision fraction over CHAIN edges (per store: sharded -> per-shard then avg).
        if shards == 1:
            emp = empirical_collision_frac(chain_edges, p_rel)
            k_slots = eff_key_capacity(p_rel, 1)
            theo = theoretical_collision_frac(chain_edges.shape[0], k_slots)
        else:
            emps, theos, wts = [], [], []
            for s_idx in range(shards):
                cidx = np.where(shard_id == s_idx)[0]
                ce = chains[cidx].reshape(-1, 3) if cidx.size else np.zeros((0, 3), np.int64)
                if ce.shape[0] == 0:
                    continue
                emps.append(empirical_collision_frac(ce, p_rel))
                theos.append(theoretical_collision_frac(ce.shape[0], eff_key_capacity(p_rel, 1)))
                wts.append(ce.shape[0])
            wsum = float(sum(wts)) if wts else 1.0
            emp = round(float(np.dot(emps, wts) / wsum), 4) if wts else 0.0
            theo = round(float(np.dot(theos, wts) / wsum), 4) if wts else 0.0

        pred_ud = predicted_usable_depth(theo, D_MAX)
        arm_preds_final[label] = r["preds"][DEPTHS[-1]]
        arm_results[label] = {
            "label": label, "p_rel": p_rel, "shards": shards,
            "eff_key_capacity": eff_key_capacity(p_rel, shards),
            "eff_fill": eff_fill(n_test, D_MAX, p_rel, shards),
            "curve": curve, "usable_depth": ud, "usable_depth_secfloor": ud_sec,
            "crossing_depth": xd, "d1": curve[1],
            "collision_frac_emp": emp, "collision_frac_theo": theo,
            "predicted_usable_depth": pred_ud,
            "store_sha": store.sha_edges(),
        }

    # arms-differ (META_RULE_AF): base must differ from every mechanism arm + control.
    shas = {lab: _sha_of_array(arm_preds_final[lab]) for lab in arm_preds_final}
    all_distinct = (len(set(shas.values())) == len(shas))
    base_sha = shas[BASE_ARM]
    base_differs_from_mech = all(shas[m] != base_sha for m in MECH_ARMS + [CTL_ARM])

    base = arm_results[BASE_ARM]
    ctl = arm_results[CTL_ARM]
    base_ud = base["usable_depth"]
    base_in_band = bool(SS_BAND_LO <= base_ud <= D_MAX - 1)
    base_d1_ok = bool(base["d1"] >= HP_D1_SANITY)

    # best-extending mechanism arm (censored-high counts usable=D_MAX for delta).
    def _eff_ud(arm_lab: str) -> int:
        a = arm_results[arm_lab]
        if a["usable_depth"] >= D_MAX - 1 and a["curve"][DEPTHS[-1]] >= USABLE_FLOOR:
            return D_MAX
        return a["usable_depth"]

    deltas = {m: _eff_ud(m) - base_ud for m in MECH_ARMS}
    best_mech = max(MECH_ARMS, key=lambda m: deltas[m])
    best_delta = deltas[best_mech]
    keyslots_best_delta = max(deltas[m] for m in KEYSLOTS_ARMS)
    shard_best_delta = max(deltas[m] for m in SHARD_ARMS)

    # equivalence check: keyslots_2x vs shard_2 (equal eff capacity 4096) and 4x vs 4.
    equiv_2 = abs(arm_results["keyslots_2x"]["usable_depth"] - arm_results["shard_2"]["usable_depth"])
    equiv_4 = abs(arm_results["keyslots_4x"]["usable_depth"] - arm_results["shard_4"]["usable_depth"])
    equiv_ok = bool(equiv_2 <= EQUIV_TOL and equiv_4 <= EQUIV_TOL)

    # collision monotonicity: usable_depth should be non-increasing in collision_frac
    # across arms of increasing fill (baseline highest fill). REPORTED trend flag.
    ordered = sorted([arm_results[a] for a in [BASE_ARM] + MECH_ARMS],
                     key=lambda a: -a["collision_frac_emp"])
    uds_by_coll = [a["usable_depth"] for a in ordered]
    monotone = all(uds_by_coll[i] <= uds_by_coll[i + 1] + 1 for i in range(len(uds_by_coll) - 1))

    for depth in DEPTHS:
        hb_state["unit"] += 1
        _heartbeat(out_dir, hb_state["unit"], hb_state["total"], hb_state["t0"],
                   extra={"N": n_dim, "seed": seed, "n_test": n_test, "depth": depth})

    print("  [N=%d seed=%d N_TEST=%d M/N~%.2f] base_ud=%d(d1=%.3f in_band=%s) | "
          "ks2x=%d ks4x=%d sh2=%d sh4=%d ctl=%d | best_delta=+%d(%s) equiv(2=%d,4=%d) "
          "monotone=%s arms_distinct=%s"
          % (n_dim, seed, n_test, round((chain_edge_count + m_bg) / float(n_dim), 2),
             base_ud, base["d1"], base_in_band,
             arm_results["keyslots_2x"]["usable_depth"], arm_results["keyslots_4x"]["usable_depth"],
             arm_results["shard_2"]["usable_depth"], arm_results["shard_4"]["usable_depth"],
             ctl["usable_depth"], best_delta, best_mech, equiv_2, equiv_4, monotone,
             all_distinct), flush=True)
    print("    collision_emp: " + " ".join(
        "%s=%.3f(ud%d,pred%.1f)" % (a, arm_results[a]["collision_frac_emp"],
                                    arm_results[a]["usable_depth"],
                                    arm_results[a]["predicted_usable_depth"])
        for a in [BASE_ARM] + MECH_ARMS), flush=True)

    return {
        "N": n_dim, "seed": seed, "n_test": int(n_test), "m_bg": int(m_bg),
        "m_over_n": round((chain_edge_count + m_bg) / float(n_dim), 4),
        "V": V_CODE, "V_CHAIN": V_CHAIN, "run_mode": RUN_MODE,
        "arm_results": {a: {k: v for k, v in arm_results[a].items() if k != "curve"}
                        for a in arm_results},
        "arm_curves": {a: arm_results[a]["curve"] for a in arm_results},
        "base_usable": base_ud, "base_d1": base["d1"], "base_in_band": base_in_band,
        "base_d1_ok": base_d1_ok, "base_crossing": base["crossing_depth"],
        "deltas": deltas, "best_mech": best_mech, "best_delta": int(best_delta),
        "best_mech_crossing": arm_results[best_mech]["crossing_depth"],
        "keyslots_best_delta": int(keyslots_best_delta),
        "shard_best_delta": int(shard_best_delta),
        "ctl_usable": ctl["usable_depth"],
        "equiv_2": int(equiv_2), "equiv_4": int(equiv_4), "equiv_ok": equiv_ok,
        "collision_monotone": bool(monotone),
        "arms_all_distinct": bool(all_distinct),
        "base_differs_from_mech": bool(base_differs_from_mech),
        "arm_shas": shas,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Per (N, seed) classification
# ---------------------------------------------------------------------------
def classify_unit(row: Dict[str, Any]) -> Tuple[str, str]:
    if row["ctl_usable"] > HP_CTL_USABLE_MAX:
        return ("HARD_FAIL_CTL",
                "control usable=%d > %d (structure-shuffled store recovers -> discriminator broken)"
                % (row["ctl_usable"], HP_CTL_USABLE_MAX))
    if not row["base_differs_from_mech"]:
        return ("HARD_FAIL_ARMS",
                "baseline bit-identical to a mechanism arm (META_RULE_AF): %s" % row["arm_shas"])
    if not (row["base_in_band"] and row["base_d1_ok"]):
        return ("ITERATE_REGIME",
                "baseline not in band (usable=%d not in [%d,%d] or d1=%.3f<%.2f) -- re-spec difficulty"
                % (row["base_usable"], SS_BAND_LO, D_MAX - 1, row["base_d1"], HP_D1_SANITY))
    if row["best_delta"] >= HP_DEPTH_MARGIN:
        return ("HARD_PASS",
                "base_ud=%d best_delta=+%d(%s) keyslots=+%d shard=+%d equiv_ok=%s collision_monotone=%s "
                "(more key slots / sharding EXTEND usable depth by a real margin)"
                % (row["base_usable"], row["best_delta"], row["best_mech"],
                   row["keyslots_best_delta"], row["shard_best_delta"],
                   row["equiv_ok"], row["collision_monotone"]))
    if row["best_delta"] <= 0:
        return ("HARD_FAIL",
                "base_ud=%d best_delta=%d (NO lever extends usable depth -- the ceiling is NOT "
                "collision-bound after all, or sharding does not help)"
                % (row["base_usable"], row["best_delta"]))
    return ("MIDDLE_BAND",
            "base_ud=%d best_delta=+%d (extends a little, below the >=%d-hop margin)"
            % (row["base_usable"], row["best_delta"], HP_DEPTH_MARGIN))


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    hb_total = len(N_LIST) * len(NTEST_TARGETS) * len(DEPTHS)
    hb_state = {"unit": 0, "total": hb_total, "t0": t0}
    units: List[Dict[str, Any]] = []
    for n_dim in N_LIST:
        for n_test in NTEST_TARGETS:
            row = run_unit(n_dim, seed, n_test, out_dir, hb_state)
            tier, reason = classify_unit(row)
            row["unit_tier"] = tier
            row["unit_reason"] = reason
            print("  [N=%d seed=%d N_TEST=%d] UNIT_TIER=%s :: %s"
                  % (n_dim, seed, n_test, tier, reason), flush=True)
            units.append(row)
    return {
        "seed": seed, "run_mode": RUN_MODE, "N": N_LIST[-1],
        "n_llm_calls": _LLM_CALL_COUNTER[0], "units": units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Aggregate verdict
# ---------------------------------------------------------------------------
def _mean(xs: List[Any]) -> Optional[float]:
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return round(float(np.mean(xs)), 4) if xs else None


def _cv(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    mu = float(np.mean(xs))
    if abs(mu) < 1e-9:
        return None
    return round(float(np.std(xs)) / abs(mu), 4)


def compute_verdict(all_seed_results: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    n_seeds = len(all_seed_results)
    if n_seeds == 0:
        return "HARD_FAIL", "NO_SEED_RESULTS", {"cardinality_ok": False}

    n_units = sum(len(r["units"]) for r in all_seed_results)
    expected_units = n_seeds * len(N_LIST) * len(NTEST_TARGETS)
    if n_units != expected_units:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H units=%d expected=%d"
                % (n_units, expected_units),
                {"cardinality_ok": False, "n_units": n_units, "expected": expected_units})

    # index units by (N, n_test) across seeds.
    keyed: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for r in all_seed_results:
        for u in r["units"]:
            keyed.setdefault((u["N"], u["n_test"]), []).append(u)

    per_op: List[Dict[str, Any]] = []
    for (n_dim, n_test), rows in sorted(keyed.items()):
        tiers = [row["unit_tier"] for row in rows]
        n_pass = sum(1 for t in tiers if t == "HARD_PASS")
        n_fail = sum(1 for t in tiers if t == "HARD_FAIL")
        n_ctl = sum(1 for t in tiers if t == "HARD_FAIL_CTL")
        n_arms = sum(1 for t in tiers if t == "HARD_FAIL_ARMS")
        n_iter = sum(1 for t in tiers if t == "ITERATE_REGIME")
        n_mid = sum(1 for t in tiers if t == "MIDDLE_BAND")
        majority = (len(rows) // 2) + 1
        base_cross = [row["base_crossing"] for row in rows]
        disc_cross = [row["best_mech_crossing"] for row in rows]
        cv_base = _cv(base_cross)
        cv_disc = _cv(disc_cross)
        cv_ok = bool((cv_base is None or cv_base < HP_CV_MAX) and
                     (cv_disc is None or cv_disc < HP_CV_MAX))
        all_extend = all(row["best_delta"] >= HP_DEPTH_MARGIN for row in rows) and n_pass > 0
        if n_ctl > 0:
            op_tier = "HARD_FAIL_CTL"
        elif n_arms > 0:
            op_tier = "HARD_FAIL_ARMS"
        elif n_pass >= majority and all_extend and cv_ok:
            op_tier = "HARD_PASS"
        elif n_pass >= majority and all_extend and not cv_ok:
            op_tier = "MIDDLE_BAND"  # extends but cross-seed unstable
        elif n_fail >= majority:
            op_tier = "HARD_FAIL"
        elif n_iter >= majority:
            op_tier = "ITERATE_REGIME"
        else:
            op_tier = "MIDDLE_BAND"

        # capacity law: mean usable_depth per arm (over seeds at this op-point).
        cap_law = {}
        for a in [BASE_ARM] + MECH_ARMS + [CTL_ARM]:
            uds = [row["arm_results"][a]["usable_depth"] for row in rows]
            colls = [row["arm_results"][a]["collision_frac_emp"] for row in rows]
            preds = [row["arm_results"][a]["predicted_usable_depth"] for row in rows]
            cap_law[a] = {
                "eff_key_capacity": rows[0]["arm_results"][a]["eff_key_capacity"],
                "eff_fill": rows[0]["arm_results"][a]["eff_fill"],
                "mean_usable_depth": _mean(uds),
                "mean_collision_frac_emp": _mean(colls),
                "mean_predicted_usable_depth": _mean(preds),
            }
        per_op.append({
            "N": n_dim, "n_test": n_test, "op_tier_majority": op_tier, "seed_tiers": tiers,
            "n_pass": n_pass, "n_fail": n_fail, "n_fail_ctl": n_ctl, "n_fail_arms": n_arms,
            "n_iterate": n_iter, "n_middle": n_mid,
            "mean_base_usable": _mean([row["base_usable"] for row in rows]),
            "mean_best_delta": _mean([row["best_delta"] for row in rows]),
            "mean_keyslots_delta": _mean([row["keyslots_best_delta"] for row in rows]),
            "mean_shard_delta": _mean([row["shard_best_delta"] for row in rows]),
            "cv_base_crossing": cv_base, "cv_disc_crossing": cv_disc, "cv_ok": cv_ok,
            "all_seeds_extend": all_extend,
            "mean_equiv_2": _mean([row["equiv_2"] for row in rows]),
            "mean_equiv_4": _mean([row["equiv_4"] for row in rows]),
            "frac_equiv_ok": _mean([1.0 if row["equiv_ok"] else 0.0 for row in rows]),
            "frac_monotone": _mean([1.0 if row["collision_monotone"] else 0.0 for row in rows]),
            "mean_ctl_usable": _mean([row["ctl_usable"] for row in rows]),
            "capacity_law": cap_law,
        })

    # N-independence: for each n_test, does base_usable / best_delta vary across N?
    n_indep = {}
    for n_test in NTEST_TARGETS:
        by_N = [(op["N"], op["mean_base_usable"], op["mean_best_delta"])
                for op in per_op if op["n_test"] == n_test]
        base_vals = [b for _, b, _ in by_N if b is not None]
        n_indep[n_test] = {
            "base_usable_by_N": [(nn, b) for nn, b, _ in by_N],
            "best_delta_by_N": [(nn, d) for nn, _, d in by_N],
            "base_usable_spread": (round(max(base_vals) - min(base_vals), 3)
                                   if len(base_vals) >= 2 else None),
        }

    any_ctl = any(op["op_tier_majority"] == "HARD_FAIL_CTL" for op in per_op)
    any_arms = any(op["op_tier_majority"] == "HARD_FAIL_ARMS" for op in per_op)
    pass_ops = [op for op in per_op if op["op_tier_majority"] == "HARD_PASS"]
    fail_ops = [op for op in per_op if op["op_tier_majority"] == "HARD_FAIL"]
    iter_ops = [op for op in per_op if op["op_tier_majority"] == "ITERATE_REGIME"]

    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": expected_units,
        "n_seeds": n_seeds, "N_LIST": N_LIST, "NTEST_TARGETS": NTEST_TARGETS,
        "MOVERN_FIXED": MOVERN_FIXED, "arms": [a["label"] for a in ARMS],
        "eff_key_capacity_by_arm": {a["label"]: eff_key_capacity(a["p_rel"], a["shards"])
                                    for a in ARMS},
        "per_op": per_op, "n_independence": n_indep,
        "chance_floor": round(CHANCE_FLOOR, 5),
        "bands": {
            "USABLE_FLOOR": USABLE_FLOOR, "HP_DEPTH_MARGIN": HP_DEPTH_MARGIN,
            "HP_CTL_USABLE_MAX": HP_CTL_USABLE_MAX, "HP_D1_SANITY": HP_D1_SANITY,
            "HP_CV_MAX": HP_CV_MAX, "SS_BAND_LO": SS_BAND_LO, "EQUIV_TOL": EQUIV_TOL,
        },
    }

    def _fmt_ops(ops):
        return " ".join("N%d/NT%d:%s(base=%s,best_delta=%s,cv_base=%s,cv_disc=%s)" % (
            op["N"], op["n_test"], op["op_tier_majority"], op["mean_base_usable"],
            op["mean_best_delta"], op["cv_base_crossing"], op["cv_disc_crossing"]) for op in ops)

    summ = ("n_seeds=%d units=%d/%d | OP-POINTS: %s | eff_capacity_by_arm=%s"
            % (n_seeds, n_units, expected_units, _fmt_ops(per_op),
               extra["eff_key_capacity_by_arm"]))

    if any_ctl:
        return "HARD_FAIL", "HARD_FAIL_CONTROL (broken-discriminator rail recovered structure): " + summ, extra
    if any_arms:
        return "HARD_FAIL", "HARD_FAIL_ARMS (baseline bit-identical to a mechanism arm -- AF): " + summ, extra
    if pass_ops:
        return "HARD_PASS", ("HARD_PASS (more key slots / sharded storage EXTEND usable chain "
                             "depth over the baseline collision-bound ceiling by a real margin at "
                             "a fair operating point, cross-seed stable, control at chance -- the "
                             "reasoning-depth ceiling IS collision-bound and the REDIRECT works): ") + summ, extra
    if len(fail_ops) >= (len(per_op) // 2 + 1):
        return "HARD_FAIL", ("HARD_FAIL (NO lever extends usable depth at a fair operating point -- "
                             "the depth ceiling is NOT collision-bound after all, or sharding does "
                             "not help): ") + summ, extra
    if len(iter_ops) == len(per_op):
        return "MIDDLE_BAND", ("MIDDLE_BAND (ITERATE_REGIME at all op-points -- baseline never in "
                               "band; needs harder N_TEST or deeper D_MAX): ") + summ, extra
    return "MIDDLE_BAND", ("MIDDLE_BAND (extends but below the required margin, or cross-seed "
                           "unstable): ") + summ, extra


# ---------------------------------------------------------------------------
# Self-test (fast; small N; exits 0)
# ---------------------------------------------------------------------------
def _selftest() -> int:
    t0 = time.perf_counter()
    g = np.random.default_rng(0)
    n = 512
    global V_CHAIN, V_CODE  # noqa: F824
    _save = (V_CHAIN, V_CODE)
    V_CODE, V_CHAIN = 64, 32
    v, pmax = V_CODE, 8
    E = make_bipolar(v, n, g)
    R = make_bipolar(pmax, n, g)

    # T0: FACTORED store == materialized W.
    chains = make_chains(6, 5, 4, g)
    assert chains.shape == (6, 5, 3)
    edges = chains.reshape(-1, 3)
    bg = make_background_edges(60, 4, g)
    all_e = np.concatenate([edges, bg], axis=0)
    store = FactoredStore(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    W = build_W_reference(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    keys = make_bipolar(10, n, g)
    max_diff = float(np.max(np.abs(store.retrieve(keys) - keys @ W.T)))
    assert max_diff < 1e-3, "FACTORED != materialized W (max|diff|=%.2e)" % max_diff

    # T1: single-hop retrieval PERFECT on a COLLISION-FREE store (positive control;
    # hand-built distinct (s,p) keys so d1==1.0 is not RNG-luck sensitive to collisions).
    cf_s = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=np.int64)
    cf_p = np.array([0, 1, 2, 3, 0, 1, 2, 3], dtype=np.int64)   # keys (s,p) all distinct
    cf_o = np.array([10, 11, 12, 13, 14, 15, 16, 17], dtype=np.int64)
    clean_cf = FactoredStore(cf_s, cf_p, cf_o, E, R, n)
    cf_keys = E[cf_s] * R[cf_p]
    d1_cf = float(np.mean(argmax_clean(clean_cf.retrieve(cf_keys), E) == cf_o))
    assert d1_cf >= 0.99, "single-hop collision-free store broken: %.3f" % d1_cf

    # T2: ONE-PASS depth curve == per-depth re-walk (proves the prefix curve is exact;
    # method-equivalence, independent of accuracy -- uses the chain-edge store).
    clean = FactoredStore(edges[:, 0], edges[:, 1], edges[:, 2], E, R, n)
    ref = {}
    for dd in [1, 2, 3]:
        xx = E[chains[:, 0, 0]].astype(np.float32).copy()
        pr = None
        for kk in range(dd):
            pr = argmax_clean(clean.retrieve(xx * R[chains[:, kk, 1]]), E)
            xx = E[pr].astype(np.float32)
        ref[dd] = float(np.mean(pr == chains[:, dd - 1, 2]))
    op = walk_curve(chains, clean, E, R, [1, 2, 3], lambda y: argmax_clean(y, E))["curve"]
    assert all(abs(op[dd] - ref[dd]) < 1e-12 for dd in [1, 2, 3]), "ONE-PASS != re-walk"

    # T3: SHARD ROUTING CORRECTNESS -- a sharded walk retrieves ONLY from the chain's
    # shard. Build S=2 shards from 6 chains; the sharded retrieval for chain i must equal
    # a single-store walk over exactly shard (i%2)'s edges.
    S = 2
    shard_id = np.arange(6, dtype=np.int64) % S
    stores = []
    for si in range(S):
        cidx = np.where(shard_id == si)[0]
        ce = chains[cidx].reshape(-1, 3)
        stores.append(FactoredStore(ce[:, 0], ce[:, 1], ce[:, 2], E, R, n))
    sharded = ShardedStore(stores, shard_id)
    key_batch = E[chains[:, 0, 0]] * R[chains[:, 0, 1]]
    got = sharded.retrieve(key_batch)
    # reference: each chain retrieved from its own shard's store only.
    ref_r = np.zeros_like(got)
    for i in range(6):
        ref_r[i] = stores[int(shard_id[i])].retrieve(key_batch[i:i + 1])[0]
    assert float(np.max(np.abs(got - ref_r))) < 1e-5, "shard routing mis-routes"
    # and mis-routing to the WRONG shard changes the retrieval (routing is load-bearing).
    wrong = stores[1 - int(shard_id[0])].retrieve(key_batch[0:1])[0]
    assert float(np.max(np.abs(wrong - got[0]))) > 1e-4, "shard identity is vacuous"

    # T4: COLLISION-FRACTION model -- empirical ~ theoretical; sharding halves edges so
    # lowers collision_frac; more relations (bigger K) lowers collision_frac.
    big = make_chains(40, 8, 8, g)          # M=320 edges, K=V_CHAIN*8=192
    ce_big = big.reshape(-1, 3)
    emp = empirical_collision_frac(ce_big, 8)
    theo = theoretical_collision_frac(ce_big.shape[0], V_CHAIN * 8)
    assert abs(emp - theo) < 0.15, "collision emp %.3f vs theo %.3f mismatch" % (emp, theo)
    # sharding by 2 (half the edges per shard) reduces collision.
    half = big[np.arange(40) % 2 == 0].reshape(-1, 3)
    emp_half = empirical_collision_frac(half, 8)
    assert emp_half < emp + 1e-9, "sharding did not reduce collision (%.3f !< %.3f)" % (emp_half, emp)
    # more relations (p_rel 8->16 doubles K) reduces collision on the SAME source pattern.
    big16 = big.copy(); big16[:, :, 1] = g.integers(0, 16, size=(40, 8))
    emp16 = empirical_collision_frac(big16.reshape(-1, 3), 16)
    assert emp16 < emp + 1e-9, "more relations did not reduce collision (%.3f !< %.3f)" % (emp16, emp)

    # T5: crossing_depth logic.
    assert crossing_depth({1: 0.9, 2: 0.9, 3: 0.3}, [1, 2, 3], 0.5) == 2.667  # 2+(.9-.5)/(.9-.3)
    assert crossing_depth({1: 0.4}, [1], 0.5) == 0.0
    assert crossing_depth({1: 0.9, 2: 0.9}, [1, 2], 0.5) == 2.0  # censored to D_MAX
    assert usable_depth({1: 0.9, 2: 0.8, 3: 0.4}, [1, 2, 3], 0.5) == 2

    # T6: classify_unit -- HARD_PASS (extend), HARD_FAIL (no extend), CTL, ITERATE.
    def _row(base_ud, ks, sh, ctl, base_d1=0.95, distinct=True, curveD=0.9):
        arm_res = {}
        for lab, ud in [("baseline", base_ud), ("keyslots_2x", ks), ("keyslots_4x", ks),
                        ("shard_2", sh), ("shard_4", sh), ("control", ctl)]:
            arm_res[lab] = {"usable_depth": ud, "collision_frac_emp": 0.1,
                            "predicted_usable_depth": float(ud), "eff_key_capacity": 2048,
                            "eff_fill": 0.1, "curve": {D_MAX: curveD}}
        deltas = {"keyslots_2x": ks - base_ud, "keyslots_4x": ks - base_ud,
                  "shard_2": sh - base_ud, "shard_4": sh - base_ud}
        best = max(deltas, key=lambda m: deltas[m])
        return {"ctl_usable": ctl, "base_differs_from_mech": distinct,
                "base_in_band": bool(SS_BAND_LO <= base_ud <= D_MAX - 1),
                "base_d1_ok": base_d1 >= HP_D1_SANITY, "base_usable": base_ud, "base_d1": base_d1,
                "best_delta": deltas[best], "best_mech": best,
                "keyslots_best_delta": max(deltas["keyslots_2x"], deltas["keyslots_4x"]),
                "shard_best_delta": max(deltas["shard_2"], deltas["shard_4"]),
                "equiv_ok": True, "collision_monotone": True, "arm_shas": {}}
    assert classify_unit(_row(5, 12, 12, 0))[0] == "HARD_PASS"
    assert classify_unit(_row(5, 5, 5, 0))[0] == "HARD_FAIL"
    assert classify_unit(_row(5, 6, 5, 0))[0] == "MIDDLE_BAND"   # delta +1 < margin
    assert classify_unit(_row(5, 12, 12, 4))[0] == "HARD_FAIL_CTL"
    assert classify_unit(_row(0, 12, 12, 0, base_d1=0.4))[0] == "ITERATE_REGIME"
    assert classify_unit(_row(5, 12, 12, 0, distinct=False))[0] == "HARD_FAIL_ARMS"

    # T7: predicted_usable_depth monotone decreasing in collision_frac.
    assert predicted_usable_depth(0.05, 20) > predicted_usable_depth(0.30, 20)

    # T8: LLM counter untouched.
    assert _LLM_CALL_COUNTER[0] == 0

    V_CHAIN, V_CODE = _save
    dt = time.perf_counter() - t0
    print("[selftest] PASS factored==W(%.2e) shard-routing-ok collision(emp=%.3f theo=%.3f) "
          "d1_cf=%.3f elapsed=%.2fs" % (max_diff, emp, theo, d1_cf, dt), flush=True)
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> int:
    started = time.perf_counter()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if RUN_MODE == "self_test":
        rc = _selftest()
        res = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "HARD_PASS" if rc == 0 else "HARD_FAIL",
            "verdict_msg": "SELFTEST_PASS" if rc == 0 else "SELFTEST_FAIL",
            "summary": "selftest rc=%d" % rc, "elapsed_s": round(time.perf_counter() - started, 2),
            "ts_iso": _now_iso(), "run_mode": "self_test",
            "config_version": CONFIG_VERSION, "n_seeds": 1,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        print("[self_test] wrote %s rc=%d" % (out_dir / "metrics.json", rc), flush=True)
        return rc

    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    print("[start] anchor=%s mode=%s N_LIST=%s V=%d V_CHAIN=%d seeds=%s NTEST=%s M/N=%.2f D_MAX=%d "
          "arms=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N_LIST, V_CODE, V_CHAIN, SEEDS, NTEST_TARGETS, MOVERN_FIXED,
             D_MAX, [a["label"] for a in ARMS], EXPECTED_N_UNITS), flush=True)

    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME, "N": N_LIST[-1]}
    for pf in sorted(out_dir.glob("partial_metrics_*.json")):
        try:
            body = json.loads(pf.read_text(encoding="utf-8"))
            if "units" not in body:
                pf.unlink()
                print("[ckpt] removed incompatible-schema partial %s" % pf.name, flush=True)
        except (OSError, ValueError):
            pass
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for seed in remaining:
        print("[seed=%d] starting mode=%s ..." % (seed, RUN_MODE), flush=True)
        res = run_seed(seed, out_dir)
        res["N"] = N_LIST[-1]
        res["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, res)
        print("[seed=%d] done elapsed=%.1fs" % (seed, res["elapsed_s"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]

    verdict, verdict_msg, extra = compute_verdict(all_results)

    modes = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in modes:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL: stale smoke partials in FULL run modes=%s. %s" % (modes, verdict_msg)

    elapsed = time.perf_counter() - started
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": verdict_msg, "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(),
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "seeds": SEEDS,
        "config_version": CONFIG_VERSION,
        "N_LIST": N_LIST, "V": V_CODE, "V_CHAIN": V_CHAIN, "P_REL_MAX": P_REL_MAX,
        "D_MAX": D_MAX, "DEPTHS": DEPTHS, "NTEST_TARGETS": NTEST_TARGETS,
        "MOVERN_FIXED": MOVERN_FIXED,
        "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": extra.get("cardinality_ok", False),
        "extra": extra, "per_seed": all_results, "n_llm_forward_calls": _LLM_CALL_COUNTER[0],
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)
    print("[metrics] %s (elapsed=%.1fs)" % (out_dir / "metrics.json", elapsed), flush=True)
    return 0 if verdict != "HARD_FAIL" else 1


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(_main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:  # NOT BaseException (preserves SystemExit/KeyboardInterrupt)
        _write_crash_metrics(_out_dir_for_crash, _e)
        raise
