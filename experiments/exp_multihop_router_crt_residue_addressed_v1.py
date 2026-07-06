# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: per-arm per-hop routing-accuracy vectors hash-distinct
#     (oracle/crt/naive/static/random/scram must NOT be bit-identical). Oracle route==1.0 by
#     construction; crt/naive/static/random/scram route-vectors compared as ARTIFACTS.
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: within-partition random-guess floor = 1/PART_SIZE = 1/10 = 0.10;
#     routing random-guess floor = 1/N_PARTITIONS = 1/20 = 0.05. HP e2e=0.70 >> 0.10;
#     HP route=0.90 >> 0.05 -> both reachable. crlb_reference below.
# - baseline_in_band (META_RULE_AG): NAIVE_CENTROID (the informative baseline / prior real
#     candidate ~0.66) MUST sit in (0.05,0.95). ORACLE is the CEILING arm (exempt, ~0.955);
#     STATIC_BRIDGE + RANDOM_ROUTER + SCRAMBLED_CRT are DESIGNED-WEAK controls (exempt).
# - discriminator survives scale: smoke runs at the FULL envelope regime (N=8192, V=200, K=5);
#     smoke reduces n_chains/seed-count ONLY, never N/V/K. oracle-reproduce + crt-vs-naive +
#     random/scram collapse all FIRE in smoke.
# - HARD_PASS strictly above floor: crt route floor 0.90 (>> 0.05 chance), e2e 0.70 (>> 0.10),
#     AND crt route > naive route + 0.05 (must beat the prior real candidate).
# - HP_SCOPE: HARD_PASS gates apply to CRT_RESIDUE_ROUTER only. ORACLE has its own reproduce
#     gate (>=0.85 e2e). Controls (static/random/scram) have collapse gates, not HP gates.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MULTI-HOP ROUTER -- CRT-RESIDUE ADDRESSED (THALAMIC DYNAMIC ROUTER)  v1
# ======================================================================
# BRAIN-GROUNDING: the thalamus routes cortical traffic dynamically (Sherman-Guillery 2017;
# Halassa-Kastner 2017). This cell builds the missing thalamic-relay component: a DYNAMIC router
# that replaces the static bridge / oracle cheat in the certified 5-hop reasoning chain.
#
# WHAT IS CERTIFIED (the asterisk we are closing): partition_routed_chain (hdlab/multi_hop.py) is
# CHAIN_GRADE at K=5 (ARM_COMPOSE_PARTITION_5HOP mean=0.9550 cv=0.0074, seeds {7,17,23}, N=8192,
# V_C=200, n_partitions=20, part_size=10)  CITED@hdlab/multi_hop.py:317-331  -- but ONLY under
# oracle_routing=True (the router is handed the ground-truth partition of each hop's true target).
# The docstring names RC1/RC2/RC3 as open follow-ups. This cell is RC2 (algebraic/CRT router).
#
# THE MECHANISM (reused, no new machinery): the ALREADY-CHAIN_GRADE CRT-residue decode
# (exp_generation_decoder_rns_crt_highvocab_v1, HARD_PASS, V=65536 via residues + CRT) is
# repurposed as the ROUTER. We re-architect the partition scheme to be CRT-residue-aligned:
#   partition(id) = id mod N_PARTITIONS = CRT(id mod m1, id mod m2)   with coprime moduli (4,5),
#   product = 20 = N_PARTITIONS. Each entity's HD vector carries its residue ADDRESS in two
#   disjoint sub-blocks (residue codebooks, m-way, iid) PLUS an iid identity region. The router
#   transits the state (state = W @ (E[s]*R[p]*sq)), decodes each residue by sub-block argmax,
#   CRT-reconstructs the partition index -- deterministic, parameter-free, glass-box. The
#   within-partition argmax (over the identity dims, shared-address cancels) then picks the exact
#   entity, exactly as in the certified mechanism.
#
# WHY residue routing MIGHT beat naive-centroid (the hypothesis, P~0.30): decoding a low-arity
# residue (4-way / 5-way) over a dedicated sub-block is a lower-arity decision than a V=200-way
# full argmax; if the address sub-blocks carry a clean residue signal it should be more
# noise-robust for the ROUTING sub-task. Genuinely uncertain -- the residue signal lives in a
# fraction of the dims and shares the same crosstalk. SMOKE (full-N) measures it directly.
#
# ARMS (all PAIRED on the same chains per seed; router differs, everything else identical):
#   ORACLE_ROUTING     : partition = true_target mod 20 (ground-truth cheat). CEILING/reproduce. [CEILING]
#   CRT_RESIDUE_ROUTER : decode residues from state address sub-blocks + CRT -> partition.       [MECHANISM]
#   NAIVE_CENTROID     : full V-way argmax on state; partition = argmax_id mod 20.               [BASELINE]
#   STATIC_BRIDGE      : partition = relation_idx mod 20 (content-independent static plumbing).  [CONTROL]
#   RANDOM_ROUTER      : partition ~ uniform[0,20) (chance anchor; broken-router).               [CONTROL]
#   SCRAMBLED_CRT      : decode residues then DERANGE before CRT -> wrong partition (collapse).  [CONTROL]
# Load-bearing PAIRED comparisons: CRT vs ORACLE (upper bound), CRT vs NAIVE (prior real
# candidate), CRT vs STATIC_BRIDGE (current plumbing), SCRAMBLED/RANDOM collapse (routing is
# load-bearing; the CRT reconstruction specifically is load-bearing).
#
# HONEST scope: an algebraic CRT router does NOT need to reach oracle parity (0.955). Per the
# Markov-floor analysis (partition_oracle_recovery_mechanism_G_correction_2026-07-01), "close the
# routing gap" is scoped as "materially better than naive-centroid, chain-grade-COMPOSABLE at
# K=5", i.e. per-hop route >= 0.90 and e2e >= 0.70 (>=73% of oracle), NOT 0.955.
#
# Sources (CITED@):
#  - hdlab/multi_hop.py::partition_routed_chain (certified K=5 mechanism; oracle_routing scope flag)
#  - experiments/exp_multihop_reasoning_partition_size_sweep_gpu_v1.py (arm_part_oracle_at_depth template)
#  - experiments/exp_generation_decoder_rns_crt_highvocab_v1.py (CRT residue decode; egcd/modinv/crt reused)
#  - notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md (RC2 spec, bands)
#  - Sherman & Guillery 2017; Halassa & Kastner 2017 (thalamic dynamic routing); Roller et al. 2021
#    (Hash Layers: fixed/algebraic routing matches-or-beats learned MoE gating)
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Self-contained (synthetic
# KG chains + CRT-residue-structured codebook; no pool/re-encode dependency).
# Run: python experiments/exp_multihop_router_crt_residue_addressed_v1.py [--self-test | --smoke]
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
import torch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

ANCHOR_NAME = "multihop_router_crt_residue_addressed_v1"
REPO = Path(__file__).resolve().parents[1]

DEVICE = torch.device("cpu")  # task-mandated CPU probe; runner does not pass argv -> default cpu

# --- Certified regime (matched exactly; hdlab/multi_hop.py:317 + partition_size_sweep) ---
N_DIM = 8192               # substrate compositional default == certified regime (all modes; never reduced)
V_CONCEPTS = 200           # entities (== certified V_C)
N_PARTITIONS = 20          # == certified n_partitions
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # == 10 (certified)
K_HOPS = 5                 # == certified K=5 chain
N_RELATIONS = 8            # relation alphabet
assert V_CONCEPTS % N_PARTITIONS == 0

# --- CRT-residue addressing (coprime moduli, product == N_PARTITIONS) ---
MODULI = (4, 5)            # coprime; prod = 20 = N_PARTITIONS; partition(id)=id mod 20=CRT(id%4,id%5)
assert math.prod(MODULI) == N_PARTITIONS
# Address sub-block sizes (one per modulus). Shared within a partition; the rest = identity dims.
# A = sum(ADDR_DIMS) kept modest (~9.4% of N) so identity region (7424 dims) preserves within-
# partition 10-way argmax while giving the residue decode SNR headroom.
ADDR_DIMS = (384, 384)     # sum = 768; identity region = N_DIM - 768 = 7424
A_TOTAL = sum(ADDR_DIMS)

SEEDS_FULL = (7, 13, 19)
SEEDS_SMOKE = (7, 13, 19)  # multi-seed even in smoke (cv needed; cell is CPU-cheap)

ARMS = ["oracle", "crt_residue", "naive_centroid", "static_bridge", "random_router", "scrambled_crt"]

# --- Pre-registered bands (HYPOTHESIZED; MEASURED on smoke clearance) ---
HP_CRT_ROUTE = 0.90        # HARD_PASS: crt per-hop routing accuracy (>= 0.90) HYPOTHESIZED (RC2 target)
HP_CRT_E2E = 0.70          # HARD_PASS: crt end-to-end 5-hop (>= 0.70 ~ >=73% of oracle 0.955) HYPOTHESIZED
HP_CV = 0.05               # HARD_PASS: cross-seed cv of crt e2e (< 0.05) HYPOTHESIZED
CRT_BEATS_NAIVE_MARGIN = 0.05  # HARD_PASS: crt route > naive route + margin (beat prior real candidate)
ORACLE_REPRO_FLOOR = 0.85  # POSITIVE-CONTROL (Gate D): oracle e2e reproduce (>=0.85 of certified 0.955)
RANDOM_ROUTE_CEIL = 0.15   # discriminator: random routing near chance (1/20=0.05) -> setup not vacuous
SCRAM_E2E_CEIL = 0.10      # discriminator control: scrambled-CRT e2e must collapse (CRT load-bearing)
NAIVE_BAND_LO, NAIVE_BAND_HI = 0.05, 0.95  # META_RULE_AG: informative baseline in measurable band
HF_CRT_E2E = 0.20          # HARD_FAIL: crt e2e below composable floor (naive-centroid-composed floor)

CRLB_WITHIN_PARTITION = 1.0 / PART_SIZE     # 0.10 THEORETICAL@random-guess over PART_SIZE=10
CRLB_ROUTING = 1.0 / N_PARTITIONS           # 0.05 THEORETICAL@random-guess over N_PARTITIONS=20


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
# CRT number theory (formula self-test target) -- reused from generation decoder
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


def crt_addressing_selftest(moduli) -> bool:
    """Formula self-test (CRT-residue ADDRESSING correctness):
    (a) moduli pairwise coprime; (b) CRT(id mod mi) == id mod prod(mi) for all id in [0, V);
    i.e. the residue address of every entity reconstructs to exactly its partition index."""
    if not _coprime(moduli):
        return False
    M, Mi, yi = _crt_setup(moduli)
    for idv in range(V_CONCEPTS):
        res = [idv % m for m in moduli]
        part = _crt(res, moduli, M, Mi, yi)
        if part != (idv % M):
            return False
        if not (0 <= part < N_PARTITIONS):
            return False
    return True


# ============================================================
# Codebooks + KG construction
# ============================================================


def _bipolar(m: int, n: int, g: torch.Generator) -> torch.Tensor:
    """Bipolar {-1,+1} hypervectors [m,n] (substrate atom format)."""
    return (torch.randint(0, 2, (m, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32).to(DEVICE)


def build_codebooks(seed: int):
    """Build CRT-residue-structured entity codebook E, relation codebook R, and residue codebooks.

    E[id]: dims [0,A_TOTAL) = concat of residue codes (residue_cb_i[id mod m_i]); shared within a
    partition. dims [A_TOTAL, N_DIM) = iid identity (unique per entity). All bipolar {-1,+1}.
    """
    g = torch.Generator(device="cpu")
    g.manual_seed(1000 + seed)
    E = _bipolar(V_CONCEPTS, N_DIM, g)              # start fully iid (identity everywhere)
    R = _bipolar(N_RELATIONS, N_DIM, g)
    res_cbs = []
    offsets = []
    off = 0
    for i, m in enumerate(MODULI):
        a = ADDR_DIMS[i]
        cb = _bipolar(m, a, g)                       # m-way residue codebook for sub-block i
        res_cbs.append(cb)
        offsets.append((off, off + a))
        idx = torch.arange(V_CONCEPTS) % m            # (V,) residue label per entity
        E[:, off:off + a] = cb[idx]                   # overwrite sub-block with shared residue code
        off += a
    return E, R, res_cbs, offsets


def make_chains(n_chains: int, g: np.random.Generator):
    """Synthetic KG chains: each = list of K (s,p,o) triples with distinct nodes; returns
    (all_triples, chains). VERBATIM shape of partition_size_sweep make_deep_chains."""
    all_triples = []
    chains = []
    tries = 0
    used_s = set()
    while len(chains) < n_chains and tries < n_chains * 200:
        tries += 1
        s = int(g.integers(0, V_CONCEPTS))
        if s in used_s:
            continue
        nodes = [s]
        for _ in range(K_HOPS):
            cand = int(g.integers(0, V_CONCEPTS))
            while cand in nodes:
                cand = int(g.integers(0, V_CONCEPTS))
            nodes.append(cand)
        chain = [(nodes[i], int(g.integers(0, N_RELATIONS)), nodes[i + 1]) for i in range(K_HOPS)]
        all_triples.extend(chain)
        chains.append(chain)
        used_s.add(s)
    if len(chains) < n_chains:
        raise RuntimeError(f"make_chains: only {len(chains)}/{n_chains}")
    return all_triples, chains


def ingest_hebbian(triples, E, R, sq):
    """Multi-value Hebbian W = sum outer(E[o], E[s]*R[p]*sq)/N (certified binding)."""
    W = torch.zeros((N_DIM, N_DIM), dtype=torch.float32, device=DEVICE)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]); p_idx = torch.from_numpy(tr[:, 1]); o_idx = torch.from_numpy(tr[:, 2])
    B = 500
    for b in range(0, len(tr), B):
        s_s = s_idx[b:b + B]; p_s = p_idx[b:b + B]; o_s = o_idx[b:b + B]
        Kmat = E[s_s] * R[p_s] * sq
        W = W + (E[o_s].T @ Kmat) / N_DIM
    return W


# ============================================================
# Routers (partition selection) -- the load-bearing arm difference
# ============================================================


def _decode_residues_batch(states, res_cbs, offsets):
    """states (n,N) -> list of (n,) residue-label tensors, one per modulus (sub-block argmax)."""
    out = []
    for i, (lo, hi) in enumerate(offsets):
        scores = states[:, lo:hi] @ res_cbs[i].T          # (n, m_i)
        out.append(torch.argmax(scores, dim=1))            # (n,)
    return out


def _crt_batch(residue_labels, crt_ctx):
    """residue_labels: list of (n,) tensors (t mod m_i). Return (n,) partition indices via CRT."""
    M, Mi, yi = crt_ctx
    n = residue_labels[0].shape[0]
    part = torch.zeros(n, dtype=torch.long, device=DEVICE)
    for i in range(len(MODULI)):
        part = part + (residue_labels[i] % MODULI[i]) * (Mi[i] * yi[i])
    return part % M


def route_batch(arm, states, allscores, p_vec, target_vec, res_cbs, offsets, crt_ctx,
                ent_part, rng_np, scramble):
    """Vectorized router: return (n,) predicted partition indices in [0, N_PARTITIONS)."""
    n = states.shape[0]
    if arm == "oracle":
        return target_vec % N_PARTITIONS
    if arm == "crt_residue":
        res = _decode_residues_batch(states, res_cbs, offsets)
        return _crt_batch(res, crt_ctx)
    if arm == "scrambled_crt":
        res = _decode_residues_batch(states, res_cbs, offsets)
        res = [res[scramble[i]] for i in range(len(res))]              # derangement -> wrong partition
        return _crt_batch(res, crt_ctx)
    if arm == "naive_centroid":
        pred_id = torch.argmax(allscores, dim=1)                        # full V-way argmax (n,)
        return ent_part[pred_id]
    if arm == "static_bridge":
        return p_vec % N_PARTITIONS                                     # content-independent plumbing
    if arm == "random_router":
        return torch.from_numpy(rng_np.integers(0, N_PARTITIONS, size=n)).to(torch.long)
    raise ValueError(f"unknown arm {arm}")


def run_arm(arm, chains, E, R, sq, W, ent_part, res_cbs, offsets, crt_ctx, seed):
    """Batched routed K-hop chain (all chains at once; no matmul in a python loop). Returns per-hop
    routing accuracy, per-hop step accuracy, end-to-end accuracy."""
    n = len(chains)
    Wt = W.T.contiguous()
    Et = E.T.contiguous()
    s = torch.tensor([c[0][0] for c in chains], dtype=torch.long, device=DEVICE)        # (n,)
    P = torch.tensor([[c[i][1] for i in range(K_HOPS)] for c in chains], dtype=torch.long)  # (n,K)
    T = torch.tensor([[c[i][2] for i in range(K_HOPS)] for c in chains], dtype=torch.long)  # (n,K)
    scramble = [(i + 1) % len(MODULI) for i in range(len(MODULI))]      # cyclic derangement
    rng_np = np.random.default_rng(50000 + seed)
    route_hits = np.zeros(K_HOPS, dtype=np.int64)
    step_hits = np.zeros(K_HOPS, dtype=np.int64)
    NEG = torch.finfo(torch.float32).min
    for i in range(K_HOPS):
        p_vec = P[:, i]
        target_vec = T[:, i]
        keys = E[s] * R[p_vec] * sq            # (n,N)
        states = keys @ Wt                     # (n,N)  == (W @ key) per row
        allscores = states @ Et                # (n,V)  full entity scores (reused by naive + within-part)
        parts = route_batch(arm, states, allscores, p_vec, target_vec, res_cbs, offsets,
                            crt_ctx, ent_part, rng_np, scramble)         # (n,)
        if int(parts.min()) < 0 or int(parts.max()) >= N_PARTITIONS:
            raise ValueError(f"router {arm} returned out-of-range partition")
        true_part = target_vec % N_PARTITIONS
        route_hits[i] = int((parts == true_part).sum())
        # within-partition argmax: mask entities not in chosen partition, argmax over the rest.
        mask = ent_part.unsqueeze(0) == parts.unsqueeze(1)               # (n,V) bool
        masked = torch.where(mask, allscores, torch.full_like(allscores, NEG))
        s_pred = torch.argmax(masked, dim=1)                            # (n,)
        step_hits[i] = int((s_pred == target_vec).sum())
        s = s_pred
    e2e = int((s == T[:, K_HOPS - 1]).sum())
    route_acc = (route_hits.astype(np.float64) / max(n, 1)).tolist()
    step_acc = (step_hits.astype(np.float64) / max(n, 1)).tolist()
    return {
        "route_acc_per_hop": [round(x, 4) for x in route_acc],
        "route_acc_mean": round(float(np.mean(route_acc)), 4),
        "step_acc_per_hop": [round(x, 4) for x in step_acc],
        "step_acc_mean": round(float(np.mean(step_acc)), 4),
        "e2e": round(e2e / max(n, 1), 4),
        "n_chains": n,
    }


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"n_chains": 12, "seeds": (7,)}
    if mode == "smoke":
        # FULL crosstalk density (n_chains=200 == binding-density-determining param) so the
        # discriminator FIRES at the same M/N ratio as FULL; reduce SEEDS only for wall-time.
        return {"n_chains": 200, "seeds": SEEDS_SMOKE}
    return {"n_chains": 200, "seeds": SEEDS_FULL}


def expected_units(cfg) -> int:
    return len(ARMS) * len(cfg["seeds"])


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    n_chains, seeds = cfg["n_chains"], cfg["seeds"]
    sq = math.sqrt(N_DIM)
    crt_ctx = _crt_setup(MODULI)
    # CRT-residue partition scheme: partition(id) = id % N_PARTITIONS. ent_part[v] = v's partition.
    ent_part = (torch.arange(V_CONCEPTS, device=DEVICE) % N_PARTITIONS).to(torch.long)
    for k in range(N_PARTITIONS):
        cnt = int((ent_part == k).sum())
        if cnt != PART_SIZE:
            raise ValueError(f"partition {k} has {cnt} != PART_SIZE={PART_SIZE}")

    per_unit = []
    arm_route_digests = {}
    total_units = expected_units(cfg)
    unit = 0
    for seed in seeds:
        E, R, res_cbs, offsets = build_codebooks(seed)
        cg = np.random.default_rng(90000 + seed)
        triples, chains = make_chains(n_chains, cg)
        W = ingest_hebbian(triples, E, R, sq)
        for arm in ARMS:
            res = run_arm(arm, chains, E, R, sq, W, ent_part, res_cbs, offsets, crt_ctx, seed)
            unit += 1
            per_unit.append({"seed": seed, "arm": arm, **res})
            arm_route_digests.setdefault(arm, []).append(res["route_acc_per_hop"])
            _heartbeat(output_dir, unit, total_units, t0,
                       extra={"seed": seed, "arm": arm,
                              "route": res["route_acc_mean"], "e2e": res["e2e"]})
            _say(f"  [seed {seed}] {arm:16s} route={res['route_acc_mean']:.3f} "
                 f"step={res['step_acc_mean']:.3f} e2e={res['e2e']:.3f} "
                 f"route_per_hop={res['route_acc_per_hop']}")
    return cfg, per_unit, arm_route_digests


def _agg(per_unit, arm, key):
    vals = [u[key] for u in per_unit if u["arm"] == arm]
    return (float(np.mean(vals)) if vals else float("nan")), [round(float(v), 4) for v in vals]


def _cv(vals):
    if not vals:
        return float("nan")
    m = float(np.mean(vals))
    if m == 0.0:
        return 0.0 if float(np.std(vals)) == 0.0 else float("inf")
    return float(np.std(vals)) / m


def classify(per_unit, cfg, mode: str):
    exp = expected_units(cfg)
    if len(per_unit) < exp:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {len(per_unit)}/{exp} units", False)

    crt_route_m, crt_route_s = _agg(per_unit, "crt_residue", "route_acc_mean")
    crt_e2e_m, crt_e2e_s = _agg(per_unit, "crt_residue", "e2e")
    orc_e2e_m, _ = _agg(per_unit, "oracle", "e2e")
    orc_route_m, _ = _agg(per_unit, "oracle", "route_acc_mean")
    naive_route_m, _ = _agg(per_unit, "naive_centroid", "route_acc_mean")
    naive_e2e_m, _ = _agg(per_unit, "naive_centroid", "e2e")
    static_route_m, _ = _agg(per_unit, "static_bridge", "route_acc_mean")
    rand_route_m, _ = _agg(per_unit, "random_router", "route_acc_mean")
    scram_e2e_m, _ = _agg(per_unit, "scrambled_crt", "e2e")
    cv_e2e = _cv(crt_e2e_s)
    crt_beats_naive = crt_route_m - naive_route_m

    diag = (f"ORACLE route={orc_route_m:.3f} e2e={orc_e2e_m:.3f}(reproduce) | "
            f"CRT route={crt_route_m:.3f}(cv_e2e={cv_e2e:.3f}) e2e={crt_e2e_m:.3f} | "
            f"NAIVE route={naive_route_m:.3f} e2e={naive_e2e_m:.3f} | "
            f"STATIC route={static_route_m:.3f} | RANDOM route={rand_route_m:.3f} | "
            f"SCRAM e2e={scram_e2e_m:.3f} | crt_minus_naive_route={crt_beats_naive:.3f}")

    # --- discriminator-fires + control gates (ALL modes incl smoke) ---
    if not (orc_e2e_m >= ORACLE_REPRO_FLOOR):
        return ("POSITIVE_CONTROL_FAIL",
                f"ORACLE did NOT reproduce certified 5-hop at test regime (oracle_e2e={orc_e2e_m:.3f} "
                f"< {ORACLE_REPRO_FLOOR}): the CRT-residue codebook redesign broke the base mechanism "
                f"(Gate D). Downstream router arms are UNRELIABLE. {diag}", False)
    if not (rand_route_m <= RANDOM_ROUTE_CEIL):
        return ("SETUP_VACUOUS",
                f"random routing NOT near chance (random_route={rand_route_m:.3f} > {RANDOM_ROUTE_CEIL}): "
                f"partition scheme is saturated/degenerate; routing is trivially right. {diag}", False)
    if not (scram_e2e_m <= SCRAM_E2E_CEIL):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"scrambled-CRT did NOT collapse (scram_e2e={scram_e2e_m:.3f} > {SCRAM_E2E_CEIL}): CRT "
                f"reconstruction is not load-bearing / partition leaks. {diag}", False)
    if not (NAIVE_BAND_LO < naive_route_m < NAIVE_BAND_HI):
        return ("BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"naive-centroid route={naive_route_m:.3f} outside ({NAIVE_BAND_LO},{NAIVE_BAND_HI}): "
                f"informative baseline saturated or floored; re-spec regime. {diag}", False)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: oracle reproduces ({orc_e2e_m:.3f}>={ORACLE_REPRO_FLOOR}), naive in "
                f"band ({naive_route_m:.3f}), random near chance ({rand_route_m:.3f}), scram collapses "
                f"({scram_e2e_m:.3f}); all at N={N_DIM} V={V_CONCEPTS} K={K_HOPS}. CRT router measured "
                f"route={crt_route_m:.3f} e2e={crt_e2e_m:.3f} (deliverable band FULL-only, canonical=remote). "
                f"{diag}", True)

    # --- FULL pre-registered bands (gate on CRT_RESIDUE_ROUTER only) ---
    hp = (crt_route_m >= HP_CRT_ROUTE and crt_e2e_m >= HP_CRT_E2E and cv_e2e < HP_CV
          and crt_beats_naive > CRT_BEATS_NAIVE_MARGIN)
    if hp:
        return ("HARD_PASS",
                f"THALAMIC CRT-RESIDUE ROUTER WORKS: per-hop route={crt_route_m:.3f}(>={HP_CRT_ROUTE}) "
                f"e2e={crt_e2e_m:.3f}(>={HP_CRT_E2E}, {100*crt_e2e_m/max(orc_e2e_m,1e-9):.0f}% of oracle) "
                f"cv={cv_e2e:.3f}(<{HP_CV}), beats naive by {crt_beats_naive:.3f}(>{CRT_BEATS_NAIVE_MARGIN}). "
                f"Algebraic router replaces the oracle cheat -> certified-for-real. {diag}", True)
    hf = (crt_beats_naive <= CRT_BEATS_NAIVE_MARGIN) or (crt_e2e_m <= HF_CRT_E2E)
    if hf:
        return ("HARD_FAIL",
                f"CRT-residue router FAILS: does not beat naive-centroid by margin "
                f"(crt_minus_naive_route={crt_beats_naive:.3f}<={CRT_BEATS_NAIVE_MARGIN}) OR e2e collapses "
                f"(crt_e2e={crt_e2e_m:.3f}<={HF_CRT_E2E}). Algebraic-router hypothesis fails -> needs a "
                f"learned router (RC3). {diag}", True)
    return ("MIDDLE_BAND",
            f"partial router win: crt route={crt_route_m:.3f} in [naive+{CRT_BEATS_NAIVE_MARGIN}, "
            f"{HP_CRT_ROUTE}) or e2e={crt_e2e_m:.3f} in ({HF_CRT_E2E}, {HP_CRT_E2E}) or cv={cv_e2e:.3f} high. "
            f"Real improvement over naive, below chain-grade-composable bar; needs learned top-up. {diag}",
            True)


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
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} V={V_CONCEPTS} K={K_HOPS} n_parts={N_PARTITIONS} "
         f"part_size={PART_SIZE} moduli={MODULI} addr_dims={ADDR_DIMS} seeds={cfg['seeds']} "
         f"n_chains={cfg['n_chains']} arms={ARMS} expected_units={exp}")

    # formula self-test (CRT-residue ADDRESSING correctness) -- ALL modes.
    if not crt_addressing_selftest(MODULI):
        raise AssertionError(f"CRT_ADDRESSING_SELFTEST_FAIL for moduli={MODULI} "
                             f"(coprimality or partition-address reconstruction incorrect)")
    _say(f"[{ANCHOR_NAME}] CRT addressing self-test PASSED (moduli={MODULI}, "
         f"partition(id)=CRT(id%{MODULI[0]},id%{MODULI[1]})=id%{N_PARTITIONS} for all id<{V_CONCEPTS})")

    cfg, per_unit, arm_route_digests = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): per-arm route-vectors must not be bit-identical.
    digests = {arm: _digest(v) for arm, v in arm_route_digests.items()}
    reasons = []
    arms = list(digests)
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            if digests[arms[i]] == digests[arms[j]]:
                reasons.append(f"{arms[i]}=={arms[j]} route-vectors bit-identical")
    if reasons:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, ok = classify(per_unit, cfg, mode)
    elapsed = time.perf_counter() - t0

    def arm_summary(arm):
        r_m, r_s = _agg(per_unit, arm, "route_acc_mean")
        s_m, s_s = _agg(per_unit, arm, "step_acc_mean")
        e_m, e_s = _agg(per_unit, arm, "e2e")
        return {"route_acc_mean": round(r_m, 4), "route_acc_per_seed": r_s,
                "step_acc_mean": round(s_m, 4), "step_acc_per_seed": s_s,
                "e2e_mean": round(e_m, 4), "e2e_per_seed": e_s, "e2e_cv": round(_cv(e_s), 4)}

    arms_summary = {arm: arm_summary(arm) for arm in ARMS}

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: thalamic CRT-residue dynamic router vs oracle/naive/static ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "config": {"N": N_DIM, "V_CONCEPTS": V_CONCEPTS, "N_PARTITIONS": N_PARTITIONS,
                   "PART_SIZE": PART_SIZE, "K_HOPS": K_HOPS, "N_RELATIONS": N_RELATIONS,
                   "MODULI": list(MODULI), "ADDR_DIMS": list(ADDR_DIMS), "A_TOTAL": A_TOTAL,
                   "n_chains": cfg["n_chains"], "seeds": list(cfg["seeds"]),
                   "partition_scheme": "residue_class_id_mod_Npartitions",
                   "mechanism": "crt_residue_addressed_router_over_certified_partition_chain",
                   "binding": "hebbian_outer_product_EoR_p"},
        "arms": arms_summary,
        "per_unit": per_unit,
        "arm_route_digests": digests,
        "arms_differ_verified": len(reasons) == 0,
        "crlb": {"within_partition_floor": CRLB_WITHIN_PARTITION, "routing_floor": CRLB_ROUTING,
                 "formula": "within=1/PART_SIZE=0.10; routing=1/N_PARTITIONS=0.05"},
        "bands": {"HP_crt_route": HP_CRT_ROUTE, "HP_crt_e2e": HP_CRT_E2E, "HP_cv": HP_CV,
                  "crt_beats_naive_margin": CRT_BEATS_NAIVE_MARGIN, "oracle_repro_floor": ORACLE_REPRO_FLOOR,
                  "random_route_ceil": RANDOM_ROUTE_CEIL, "scram_e2e_ceil": SCRAM_E2E_CEIL,
                  "naive_band": [NAIVE_BAND_LO, NAIVE_BAND_HI], "HF_crt_e2e": HF_CRT_E2E},
        "controls": {"scram_collapsed": ok},
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
    ok_crt = crt_addressing_selftest(MODULI)
    cfg, per_unit, _dg = run_all("selftest", output_dir, t0)
    orc_e2e, _ = _agg(per_unit, "oracle", "e2e")
    scram_e2e, _ = _agg(per_unit, "scrambled_crt", "e2e")
    rand_route, _ = _agg(per_unit, "random_router", "route_acc_mean")
    # selftest sanity: CRT addressing correct; oracle routes perfectly (route==1.0 by construction);
    # scramble collapses; random near chance. (e2e magnitude not gated here -- 12 chains only.)
    orc_route, _ = _agg(per_unit, "oracle", "route_acc_mean")
    ok = ok_crt and (orc_route >= 0.999) and (scram_e2e <= 0.20) and (rand_route <= 0.25)
    # Diagnostic-hygiene: selftest writes a run_mode=self_test marker so the output dir never
    # shows the ambiguous "heartbeat-present / metrics-absent" state (which reads as a death).
    # This is NOT a deliverable verdict (n_chains=12, 1 seed; deliverable bands NOT applied).
    verdict = "SELFTEST_PASS" if ok else "SELFTEST_FAIL"
    _write_metrics_atomic(output_dir, {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": (f"{verdict} (module self-test; NOT a deliverable run). crt_addr={ok_crt} "
                        f"oracle_route={orc_route:.3f} oracle_e2e={orc_e2e:.3f} "
                        f"scram_e2e={scram_e2e:.3f} random_route={rand_route:.3f}"),
        "summary": f"{verdict}: machinery self-test (n_chains=12, seed 7); deliverable bands NOT applied",
        "run_mode": "self_test",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "n_units": len(per_unit),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    })
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: crt_addr={ok_crt} "
         f"oracle_route={orc_route:.3f} oracle_e2e={orc_e2e:.3f} scram_e2e={scram_e2e:.3f} "
         f"random_route={rand_route:.3f} [{time.perf_counter()-t0:.1f}s]")
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
