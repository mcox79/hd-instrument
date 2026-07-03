"""Stage 2 VSA Cell 3 -- Multi-hop Reasoning (SMOKE).

Parent prereg: preregs/2026-07-03_stage2_vsa_cell3_multi_hop_reasoning_smoke.md
Roadmap prereg: preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md
Anchor: stage2_vsa_cell3_multi_hop_reasoning_smoke

Task class C (multi-hop reasoning): chain of role-filler bindings; substrate
must compose multiple bind/unbind operations sequentially. Example:
  Fact chain: Alice --spouse--> Bob --employer--> Acme --city--> Boston
  Query: (Alice, spouse, employer, city) -> ? = Boston  (HOP=3 chain).

Design (canonical FHRR / Plate 2003; recurrent unbind + intermediate cleanup):
  Entities: 100 atomic phasor vectors (unit magnitude complex128, n_dim=2048).
  Roles:    5 atomic phasor vectors (spouse, employer, city, boss, mentor).
  Facts:    each entity has EXACTLY 5 role-filler bindings (one per role),
            filler sampled uniformly from all entities. 500 total facts.

  SHARDED storage: per-entity bundle
    M_entities[e] = bundle_r [ bind(role_r, filler_{e,r}) ]     shape (n_dim,)
  Stored as matrix M_ents of shape (N_ENT, n_dim).

  Multi-hop query at HOP=L:
    Given (entity_start_idx, role_seq [r_1, r_2, ..., r_L]),
    ground truth is entity reached by following each role in fact-table.

Arms (5):
  ARM_HRR_RECURRENT_UNBIND_CLEANUP (LOAD-BEARING) --
    For hop h in 1..L:
      1. Take M_ents[current_idx]  (SHARDED lookup)
      2. Augment with K_DISTRACTORS=10 random distractor bindings
      3. filler_hat = unbind(augmented_bundle, R[r_h])
      4. current_idx = argmax cos(filler_hat, entities_codebook)
    Predict entity_hat = current_idx at end.

  ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP (physics-law ablation) --
    Same as above BUT skip step 4: use filler_hat directly as fuzzy entity key.
    Next step's "lookup" becomes cosine-weighted soft combine:
      M_soft = sum_e cos(current_entity_hat, entities[e]) * M_ents[e]
    Then unbind + no cleanup -> propagate noisy filler_hat.
    Physics-law prediction (SHARDED_STORAGE META 2026-07-02): collapses at L>=2
    because bundled composition without intermediate denoising accumulates noise.

  ARM_HRR_BUNDLED_LOOKUP (fair baseline: cheat-lookup) --
    At "training": build M_paths_L = sum over N_TRAIN_CHAINS=300 seen chains of
      bind(e_start, bind(r_1, bind(r_2, ..., bind(r_L, e_end))))
    At test: build query key K_q = bind(e_start, bind(r_1, ..., bind(r_L, X)))
    and try to recover e_end via unbind + cleanup over entities.
    Test chains are HELD-OUT (never in training set); expected near-zero.

  ARM_COSINE_ARGMAX_BASELINE (weak) --
    argmax_i cos(entities[e_start], entities[i]) -- ignores roles.

  ARM_RANDOM_BASELINE --
    Random entity index in [0, N_ENT).

HP_SCOPE (from prereg):
  HP1: CLEANUP r@1 at HOP=2 >= 0.50
  HP2: (CLEANUP - NO_CLEANUP) at HOP=3 >= 0.15
  HP3: CLEANUP @ HOP=3 >= 0.30 AND (CLEANUP - BUNDLED_LOOKUP) >= 0.20
  HP4: (CLEANUP - COSINE) at HOP=2 >= 0.30

HF: CLEANUP @ HOP=2 < 0.30
MB: partial (subset of HPs clear).

Cell-template mandates: META_RULE_AF (arms-must-differ), META_RULE_AH (atomic
metrics write via tmp+os.replace), except SystemExit: raise BEFORE except
Exception, start_marker, crash_diagnostic. ASCII-only. FHRR complex phasors.

Framing (USER-locked): SUBSTRATE KNOWS ALMOST NOTHING. This is a MECHANISM
COMPOSITION probe on SUPERVISED SYNTHETIC role-filler-chain regime. Entity
names in comments are labels only; substrate operates on integer indices +
FHRR phasors. Multi-hop reasoning via recurrent unbind is CANONICAL FHRR/HRR
(Plate 1995; Eliasmith 2005; Frady-Sommer 2020); NOT novel primitive.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "stage2_vsa_cell3_multi_hop_reasoning_smoke"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "smoke").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "smoke").lower()
)


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
N_DIM = 2048
N_ENTITIES = 100
N_ROLES = 5                 # spouse, employer, city, boss, mentor (labels only)
FACTS_PER_ENTITY = 5        # one filler per role; 500 total facts (fully-defined KB)
HOPS = (2, 3, 4)
N_QUERIES_PER_HOP = 60
K_DISTRACTORS = 10          # per-query per-hop noise inflation (Cell 1 K sweep threshold)
N_TRAIN_CHAINS_PER_HOP = 300  # BUNDLED_LOOKUP training set size (held-out excluded)
SEEDS = [11, 17, 23]

ARM_NAMES = (
    "ARM_HRR_RECURRENT_UNBIND_CLEANUP",
    "ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP",
    "ARM_HRR_BUNDLED_LOOKUP",
    "ARM_COSINE_ARGMAX_BASELINE",
    "ARM_RANDOM_BASELINE",
)

EXPECTED_N_UNITS = len(SEEDS) * len(HOPS) * len(ARM_NAMES)  # 3 * 3 * 5 = 45

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},n_dim={N_DIM},N_ENT={N_ENTITIES},"
    f"N_ROLES={N_ROLES},FPE={FACTS_PER_ENTITY},"
    f"HOPS={'-'.join(str(h) for h in HOPS)},"
    f"N_Q={N_QUERIES_PER_HOP},K_DIST={K_DISTRACTORS},"
    f"N_TRAIN_CH={N_TRAIN_CHAINS_PER_HOP},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},arms=5,binding=FHRR_complex_phasors,storage=SHARDED_per_entity"
)


# -----------------------------------------------------------------------------
# FHRR primitives (Plate 2003). Unit-magnitude complex phasors.
# -----------------------------------------------------------------------------
def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind: elementwise complex multiply."""
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR unbind: elementwise multiply by conjugate."""
    return c * b.conj()


def bundle(vecs: np.ndarray) -> np.ndarray:
    """FHRR bundle: per-coord phase-average, unit-normalized per-coord.
    vecs: (K, n_dim) complex128 -> (n_dim,) complex128.
    """
    s = vecs.sum(axis=0)
    mag = np.abs(s)
    mag[mag < 1e-12] = 1.0
    return s / mag


def _fhrr_sim(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """FHRR cosine sim: Re(<codebook, conj(query)>) / n_dim.
    codebook: (M, n_dim) complex; query: (n_dim,) complex -> sims: (M,) real.
    """
    dots = (codebook @ query.conj()).real
    return dots / float(query.shape[0])


def cosine_argmax(query: np.ndarray, codebook: np.ndarray) -> int:
    """argmax_i sim(query, codebook[i]). codebook: (M, n_dim) complex."""
    return int(np.argmax(_fhrr_sim(query, codebook)))


def _rand_phasors(rng: np.random.Generator, shape) -> np.ndarray:
    """Return unit-magnitude complex phasors of the given shape."""
    phases = rng.uniform(-np.pi, np.pi, size=shape).astype(np.float64)
    return np.exp(1j * phases)


# -----------------------------------------------------------------------------
# Codebook + KB
# -----------------------------------------------------------------------------
def build_codebooks(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (entities, roles) as complex phasor codebooks."""
    rng = np.random.default_rng(seed)
    E = _rand_phasors(rng, (N_ENTITIES, N_DIM))
    R = _rand_phasors(rng, (N_ROLES, N_DIM))
    return E, R


def build_fact_table(seed: int) -> np.ndarray:
    """Fact table: (N_ENT, N_ROLES) int64 -- fact_table[e, r] = filler entity idx.

    Each entity has exactly N_ROLES role-filler assignments (one per role).
    Filler index is uniform in [0, N_ENT); self-loops permitted for simplicity.
    """
    rng = np.random.default_rng(seed + 313)
    return rng.integers(0, N_ENTITIES, size=(N_ENTITIES, N_ROLES), dtype=np.int64)


def build_sharded_entity_memory(E: np.ndarray, R: np.ndarray,
                                fact_table: np.ndarray) -> np.ndarray:
    """SHARDED per-entity bundles: M_ents[e] = bundle over roles of bind(R[r], E[filler]).

    Returns (N_ENT, n_dim) complex128. Used by CLEANUP arm (LOAD-BEARING).
    Compliant with SHARDED_STORAGE_DEFAULT META rule (2026-07-02).
    """
    M_ents = np.empty((N_ENTITIES, N_DIM), dtype=np.complex128)
    for e in range(N_ENTITIES):
        vecs = np.empty((N_ROLES, N_DIM), dtype=np.complex128)
        for r in range(N_ROLES):
            filler_idx = int(fact_table[e, r])
            vecs[r] = R[r] * E[filler_idx]
        M_ents[e] = bundle(vecs)
    return M_ents


def build_bundled_kb_memory(E: np.ndarray, R: np.ndarray,
                             fact_table: np.ndarray) -> np.ndarray:
    """Fully-BUNDLED KB memory: M_KB = bundle over all entities of
        bind(E[e], bundle_over_roles( bind(R[r], E[filler_{e,r}]) ))

    Used by NO_CLEANUP arm as the physics-law discriminator: bundled storage
    at chain composition L>=2 without intermediate cleanup catastrophically
    collapses per META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW (2026-07-02).

    Bundled here is per META rule 30 exception (b): explicitly testing
    bundle-storage as a discriminator arm (positive control for
    bundled-vs-sharded / no-cleanup vs cleanup comparison).
    """
    vecs = np.empty((N_ENTITIES, N_DIM), dtype=np.complex128)
    for e in range(N_ENTITIES):
        role_vecs = np.empty((N_ROLES, N_DIM), dtype=np.complex128)
        for r in range(N_ROLES):
            filler_idx = int(fact_table[e, r])
            role_vecs[r] = R[r] * E[filler_idx]
        e_bundle = bundle(role_vecs)
        vecs[e] = E[e] * e_bundle
    return bundle(vecs)


# -----------------------------------------------------------------------------
# Chain sampling
# -----------------------------------------------------------------------------
def sample_chains(seed: int, n_chains: int, hop: int) -> np.ndarray:
    """Sample n_chains chains of length `hop`.

    Returns (n_chains, 1 + hop) int64: columns [entity_start, r_1, r_2, ..., r_hop].
    Ground-truth target is computed downstream from fact_table.
    """
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, N_ENTITIES, size=n_chains, dtype=np.int64)
    roles = rng.integers(0, N_ROLES, size=(n_chains, hop), dtype=np.int64)
    return np.concatenate([starts[:, None], roles], axis=1)


def resolve_chain_ground_truth(chain: np.ndarray, fact_table: np.ndarray) -> int:
    """Follow chain through fact_table. chain: (1 + hop,) int64."""
    e = int(chain[0])
    for r in chain[1:]:
        e = int(fact_table[e, int(r)])
    return e


def sample_disjoint_train_test_chains(seed: int, hop: int, n_train: int,
                                      n_test: int) -> Tuple[np.ndarray, np.ndarray]:
    """Sample n_train + n_test chains disjoint by tuple. Returns (train, test)."""
    rng = np.random.default_rng(seed + 8191 + hop * 101)
    seen = set()
    train_out = []
    test_out = []
    max_tries = (n_train + n_test) * 100
    tries = 0
    while (len(train_out) < n_train or len(test_out) < n_test) and tries < max_tries:
        tries += 1
        s = int(rng.integers(0, N_ENTITIES))
        rs = tuple(int(rng.integers(0, N_ROLES)) for _ in range(hop))
        key = (s,) + rs
        if key in seen:
            continue
        seen.add(key)
        chain = np.array((s,) + rs, dtype=np.int64)
        if len(train_out) < n_train:
            train_out.append(chain)
        elif len(test_out) < n_test:
            test_out.append(chain)
    if len(train_out) < n_train or len(test_out) < n_test:
        raise AssertionError(
            f"sample_disjoint_train_test_chains: exhausted tries at hop={hop} "
            f"(got train={len(train_out)}/{n_train}, test={len(test_out)}/{n_test})"
        )
    return np.stack(train_out), np.stack(test_out)


# -----------------------------------------------------------------------------
# Per-arm inference
# -----------------------------------------------------------------------------
def _augment_bundle_with_distractors(M_e: np.ndarray, E: np.ndarray, R: np.ndarray,
                                     rng: np.random.Generator) -> np.ndarray:
    """Add K_DISTRACTORS random bind(role, entity) distractors to the per-entity
    bundle. Effective K per hop = FACTS_PER_ENTITY + K_DISTRACTORS = 15.
    """
    dist_roles = rng.integers(0, N_ROLES, size=K_DISTRACTORS, dtype=np.int64)
    dist_fillers = rng.integers(0, N_ENTITIES, size=K_DISTRACTORS, dtype=np.int64)
    # Note: M_e is already normalized; combine sum-of-original + distractors as raw sum then normalize
    orig = M_e * FACTS_PER_ENTITY  # rough scale back (bundle divides by mag; approximate)
    dist_vecs = np.empty((K_DISTRACTORS, N_DIM), dtype=np.complex128)
    for k in range(K_DISTRACTORS):
        dist_vecs[k] = R[int(dist_roles[k])] * E[int(dist_fillers[k])]
    s = orig + dist_vecs.sum(axis=0)
    mag = np.abs(s)
    mag[mag < 1e-12] = 1.0
    return s / mag


def infer_recurrent_cleanup(chain: np.ndarray, E: np.ndarray, R: np.ndarray,
                             M_ents: np.ndarray,
                             rng: np.random.Generator) -> int:
    """LOAD-BEARING: recurrent unbind + intermediate cleanup at each hop."""
    current_idx = int(chain[0])
    for r_idx in chain[1:]:
        r_idx = int(r_idx)
        M_e = M_ents[current_idx]
        aug = _augment_bundle_with_distractors(M_e, E, R, rng)
        filler_hat = unbind(aug, R[r_idx])
        current_idx = cosine_argmax(filler_hat, E)
    return current_idx


def infer_recurrent_no_cleanup(chain: np.ndarray, E: np.ndarray, R: np.ndarray,
                                M_KB: np.ndarray) -> int:
    """Physics-law ablation: recurrent unbind on fully-BUNDLED M_KB WITHOUT
    intermediate cleanup at each hop.

    M_KB = bundle_e [ bind(E[e], bundle_r [ bind(R[r], E[filler_{e,r}]) ]) ]

    At each hop h:
      1. current_key holds the (initially clean, subsequently noisy) entity key.
      2. per_entity_bundle_hat = unbind(M_KB, current_key)   -- noisy per-entity bundle
      3. filler_hat = unbind(per_entity_bundle_hat, R[r_h])  -- noisy filler
      4. current_key = filler_hat    (NO CLEANUP; noise carries forward)

    Physics-law prediction: bundled composition without intermediate cleanup
    collapses at L>=2 (SHARDED_STORAGE_DEFAULT META 2026-07-02).
    """
    current_key = E[int(chain[0])].copy()
    for r_idx in chain[1:]:
        r_idx = int(r_idx)
        per_entity_hat = unbind(M_KB, current_key)
        filler_hat = unbind(per_entity_hat, R[r_idx])
        current_key = filler_hat  # NO CLEANUP
    return cosine_argmax(current_key, E)


def infer_bundled_lookup(chain: np.ndarray, E: np.ndarray, R: np.ndarray,
                          M_paths_L: np.ndarray) -> int:
    """Fair-baseline cheat-lookup: try to answer chain query via monolithic path
    memory. M_paths_L was built from N_TRAIN_CHAINS_PER_HOP SEEN chains at same
    hop level; test chains are HELD-OUT so query hits noise-floor.

    Query key: bind(E[start], bind(R[r_1], bind(R[r_2], ...bind(R[r_L], X))))
    Answer via: unbind M_paths_L by that partial key, then argmax over entities.
    """
    # Build nested key: K = E[start] * R[r_1] * R[r_2] * ... * R[r_L]
    K = E[int(chain[0])].copy()
    for r_idx in chain[1:]:
        K = K * R[int(r_idx)]
    # Unbind M_paths_L by K to isolate residual == cleaned entity signature (if chain seen).
    residual = unbind(M_paths_L, K)
    return cosine_argmax(residual, E)


def infer_cosine_baseline(chain: np.ndarray, E: np.ndarray) -> int:
    """Weak baseline: argmax cos(entities[start], entities[i])."""
    return cosine_argmax(E[int(chain[0])], E)


def infer_random(rng: np.random.Generator) -> int:
    """Chance floor: random entity idx in [0, N_ENT)."""
    return int(rng.integers(0, N_ENTITIES))


def build_M_paths_L(train_chains: np.ndarray, fact_table: np.ndarray,
                     E: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Build monolithic path-memory M_paths_L over training chains at same hop.

    For chain (e_start, r_1, ..., r_L): resolve ground truth e_end via fact_table,
    then bundle sum of bind(E[e_start], bind(R[r_1], bind(...bind(R[r_L], E[e_end])))).
    """
    n = train_chains.shape[0]
    vecs = np.empty((n, N_DIM), dtype=np.complex128)
    for i in range(n):
        chain = train_chains[i]
        e_end = resolve_chain_ground_truth(chain, fact_table)
        # Nested binding
        v = E[e_end].copy()
        for r_idx in chain[1:][::-1]:  # innermost first
            v = R[int(r_idx)] * v
        v = E[int(chain[0])] * v
        vecs[i] = v
    return bundle(vecs)


# -----------------------------------------------------------------------------
# Selftests
# -----------------------------------------------------------------------------
def _selftest_bind_unbind_roundtrip() -> None:
    rng = np.random.default_rng(0)
    a = _rand_phasors(rng, (N_DIM,))
    b = _rand_phasors(rng, (N_DIM,))
    c = bind(a, b)
    a_hat = unbind(c, b)
    sim = float((a_hat @ a.conj()).real / N_DIM)
    if not np.isfinite(sim):
        raise AssertionError(f"bind/unbind sim non-finite: {sim}")
    if sim < 0.999:
        raise AssertionError(f"bind/unbind sim={sim:.6f} < 0.999 at n_dim={N_DIM}")


def _selftest_cleanup_argmax_correct() -> None:
    E, R = build_codebooks(seed=13)
    for i in range(min(5, N_ENTITIES)):
        if cosine_argmax(E[i], E) != i:
            raise AssertionError(f"atomic entity argmax mismatch at i={i}")
    for j in range(min(3, N_ROLES)):
        if cosine_argmax(R[j], R) != j:
            raise AssertionError(f"atomic role argmax mismatch at j={j}")


def _selftest_scale_sentinel_8192() -> None:
    rng = np.random.default_rng(19)
    n_big = 8192
    a = _rand_phasors(rng, (n_big,))
    b = _rand_phasors(rng, (n_big,))
    c = bind(a, b)
    a_hat = unbind(c, b)
    if not np.all(np.isfinite(a_hat)):
        raise AssertionError("scale sentinel n_dim=8192 non-finite")
    sim = float((a_hat @ a.conj()).real / n_big)
    if sim < 0.999:
        raise AssertionError(f"scale sentinel n_dim=8192 sim={sim:.6f}")


def _selftest_kb_chain_validity() -> None:
    """Verify sampled chains resolve deterministically through fact_table."""
    fact_table = build_fact_table(seed=7)
    chains = sample_chains(seed=7, n_chains=20, hop=4)
    for i in range(chains.shape[0]):
        e = resolve_chain_ground_truth(chains[i], fact_table)
        if not (0 <= e < N_ENTITIES):
            raise AssertionError(
                f"chain {i} resolves to invalid entity {e} (n_ent={N_ENTITIES})"
            )


def _selftest_disjoint_train_test() -> None:
    """Verify BUNDLED_LOOKUP train/test splits are tuple-disjoint."""
    train, test = sample_disjoint_train_test_chains(
        seed=13, hop=2, n_train=50, n_test=20
    )
    tset = {tuple(int(x) for x in row) for row in train}
    xset = {tuple(int(x) for x in row) for row in test}
    if tset & xset:
        raise AssertionError(
            f"train/test overlap: {len(tset & xset)} tuples"
        )
    if len(tset) != 50 or len(xset) != 20:
        raise AssertionError(
            f"disjoint sample size mismatch: train={len(tset)} test={len(xset)}"
        )


def _selftest_hop_1_regression() -> None:
    """HOP=1 mechanism sanity: single unbind + cleanup on augmented per-entity
    bundle recovers correct filler at high recall.

    This is the MECHANISM-level regression to Cell 2 compositional-generalization
    primitive: same bind/unbind/cleanup at K_effective=15 SNR=11.7. Expected r@1
    at HOP=1: >= 0.90 (higher than Cell 2's 0.410 due to smaller per-entity
    fanout of 5 vs Cell 2's per-query K=10 distractors, but same primitive).
    """
    seed = 41
    E, R = build_codebooks(seed=seed)
    fact_table = build_fact_table(seed=seed)
    M_ents = build_sharded_entity_memory(E, R, fact_table)
    rng_probe = np.random.default_rng(seed + 71)
    n_probe = 100
    chains = sample_chains(seed=seed + 5, n_chains=n_probe, hop=1)
    n_hits = 0
    for i in range(n_probe):
        rng_arm = np.random.default_rng(seed + i * 3)
        pred = infer_recurrent_cleanup(chains[i], E, R, M_ents, rng_arm)
        truth = resolve_chain_ground_truth(chains[i], fact_table)
        if pred == truth:
            n_hits += 1
    recall = n_hits / float(n_probe)
    if recall < 0.90:
        raise AssertionError(
            f"HOP=1 regression: CLEANUP r@1={recall:.3f} < 0.90 "
            f"(mechanism-level primitive check failed; investigate FHRR SNR "
            f"at K_eff=15 n_dim={N_DIM})"
        )


def _selftest_deterministic_seed_invariance() -> None:
    """Same seed reproduces recurrent-cleanup r@1 to 1e-6 tolerance."""
    def _run(seed: int) -> float:
        E, R = build_codebooks(seed=seed)
        fact_table = build_fact_table(seed=seed)
        M_ents = build_sharded_entity_memory(E, R, fact_table)
        chains = sample_chains(seed=seed + 5, n_chains=15, hop=2)
        n_hits = 0
        for i in range(chains.shape[0]):
            rng_arm = np.random.default_rng(seed + i * 3)
            pred = infer_recurrent_cleanup(chains[i], E, R, M_ents, rng_arm)
            truth = resolve_chain_ground_truth(chains[i], fact_table)
            if pred == truth:
                n_hits += 1
        return n_hits / float(chains.shape[0])
    r1 = _run(42)
    r2 = _run(42)
    if abs(r1 - r2) > 1e-6:
        raise AssertionError(
            f"seed invariance broken: r1={r1:.6f} r2={r2:.6f}"
        )


def _selftest_arms_must_differ() -> None:
    """META_RULE_AF: 5 arms produce distinct predictions on shared probe batch."""
    seed = 101
    E, R = build_codebooks(seed=seed)
    fact_table = build_fact_table(seed=seed)
    M_ents = build_sharded_entity_memory(E, R, fact_table)
    M_KB = build_bundled_kb_memory(E, R, fact_table)
    hop = 2
    train, test = sample_disjoint_train_test_chains(
        seed=seed, hop=hop, n_train=50, n_test=32
    )
    M_paths = build_M_paths_L(train, fact_table, E, R)
    preds_per_arm: Dict[str, np.ndarray] = {}
    rng_rand = np.random.default_rng(seed + 999)
    for arm in ARM_NAMES:
        preds = np.empty(test.shape[0], dtype=np.int64)
        for i in range(test.shape[0]):
            rng_arm = np.random.default_rng(seed + i * 7)
            if arm == "ARM_HRR_RECURRENT_UNBIND_CLEANUP":
                preds[i] = infer_recurrent_cleanup(test[i], E, R, M_ents, rng_arm)
            elif arm == "ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP":
                preds[i] = infer_recurrent_no_cleanup(test[i], E, R, M_KB)
            elif arm == "ARM_HRR_BUNDLED_LOOKUP":
                preds[i] = infer_bundled_lookup(test[i], E, R, M_paths)
            elif arm == "ARM_COSINE_ARGMAX_BASELINE":
                preds[i] = infer_cosine_baseline(test[i], E)
            elif arm == "ARM_RANDOM_BASELINE":
                preds[i] = infer_random(rng_rand)
            else:
                raise AssertionError(f"unknown arm: {arm}")
        preds_per_arm[arm] = preds
    digests = {n: hashlib.sha256(p.tobytes()).hexdigest() for n, p in preds_per_arm.items()}
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {names[i]!r} and "
                    f"{names[j]!r} bit-identical predictions"
                )


def _instrumentation_selftest() -> None:
    t0 = time.time()
    try:
        _selftest_bind_unbind_roundtrip()
        _selftest_cleanup_argmax_correct()
        _selftest_scale_sentinel_8192()
        _selftest_kb_chain_validity()
        _selftest_disjoint_train_test()
        _selftest_hop_1_regression()
        _selftest_deterministic_seed_invariance()
        _selftest_arms_must_differ()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        sys.exit(3)
    elapsed = time.time() - t0
    print(
        f"[selftest] PASS  n_dim={N_DIM}  N_ENT={N_ENTITIES}  N_ROLES={N_ROLES}  "
        f"FPE={FACTS_PER_ENTITY}  HOPS={HOPS}  N_Q={N_QUERIES_PER_HOP}  "
        f"K_DIST={K_DISTRACTORS}  mode={RUN_MODE}  elapsed={elapsed:.2f}s",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# -----------------------------------------------------------------------------
# Per-seed runner
# -----------------------------------------------------------------------------
def _run_arm_at_hop(arm_name: str, seed: int, hop: int,
                     E: np.ndarray, R: np.ndarray,
                     fact_table: np.ndarray,
                     M_ents: np.ndarray,
                     M_KB: np.ndarray,
                     test_chains: np.ndarray,
                     M_paths: np.ndarray) -> Dict:
    """Compute r@1 for one (arm, hop) combination over test_chains."""
    t0 = time.time()
    try:
        n_q = test_chains.shape[0]
        n_hits = 0
        rng_rand = np.random.default_rng(seed + hop * 991 + 555)
        for i in range(n_q):
            rng_arm = np.random.default_rng(seed + hop * 991 + i * 7)
            chain = test_chains[i]
            truth = resolve_chain_ground_truth(chain, fact_table)
            if arm_name == "ARM_HRR_RECURRENT_UNBIND_CLEANUP":
                pred = infer_recurrent_cleanup(chain, E, R, M_ents, rng_arm)
            elif arm_name == "ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP":
                pred = infer_recurrent_no_cleanup(chain, E, R, M_KB)
            elif arm_name == "ARM_HRR_BUNDLED_LOOKUP":
                pred = infer_bundled_lookup(chain, E, R, M_paths)
            elif arm_name == "ARM_COSINE_ARGMAX_BASELINE":
                pred = infer_cosine_baseline(chain, E)
            elif arm_name == "ARM_RANDOM_BASELINE":
                pred = infer_random(rng_rand)
            else:
                raise ValueError(f"unknown arm: {arm_name}")
            if pred == truth:
                n_hits += 1
        recall = n_hits / float(n_q)
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "hop": int(hop),
            "recall_at_1": float(recall),
            "n_queries": int(n_q),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "hop": int(hop),
            "recall_at_1": float("nan"),
            "n_queries": 0,
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


def run_seed(seed: int) -> Dict:
    t_seed_start = time.time()
    E, R = build_codebooks(seed)
    fact_table = build_fact_table(seed)
    M_ents = build_sharded_entity_memory(E, R, fact_table)
    M_KB = build_bundled_kb_memory(E, R, fact_table)
    print(f"  [seed={seed}] built codebooks E=({N_ENTITIES},{N_DIM}) "
          f"R=({N_ROLES},{N_DIM}); SHARDED M_ents=({N_ENTITIES},{N_DIM}) "
          f"BUNDLED M_KB=({N_DIM},) "
          f"fact_table=({N_ENTITIES},{N_ROLES})", flush=True)

    per_hop_results = []
    for hop in HOPS:
        # Sample disjoint train/test chains for this hop level
        train_chains, test_chains = sample_disjoint_train_test_chains(
            seed=seed, hop=hop,
            n_train=N_TRAIN_CHAINS_PER_HOP, n_test=N_QUERIES_PER_HOP,
        )
        # Build BUNDLED_LOOKUP path memory (seen chains only)
        M_paths = build_M_paths_L(train_chains, fact_table, E, R)
        print(
            f"  [seed={seed} hop={hop}] train_chains={train_chains.shape[0]} "
            f"test_chains={test_chains.shape[0]} (tuple-disjoint); "
            f"M_paths built", flush=True
        )
        arms_at_hop = []
        for arm_name in ARM_NAMES:
            out = _run_arm_at_hop(arm_name, seed, hop, E, R, fact_table,
                                    M_ents, M_KB, test_chains, M_paths)
            arms_at_hop.append(out)
            print(
                f"  [seed={seed} hop={hop} {arm_name}] "
                f"r@1={out['recall_at_1']:.3f} n_q={out['n_queries']} "
                f"status={out['arm_status']} wall={out['wall_s']:.2f}s",
                flush=True,
            )
        per_hop_results.append({
            "hop": int(hop),
            "arms": arms_at_hop,
        })
    elapsed = time.time() - t_seed_start
    return {
        "seed": seed,
        "N": N_DIM,
        "n_dim": N_DIM,
        "N_ENT": N_ENTITIES,
        "N_ROLES": N_ROLES,
        "FACTS_PER_ENTITY": FACTS_PER_ENTITY,
        "HOPS": list(HOPS),
        "N_QUERIES_PER_HOP": N_QUERIES_PER_HOP,
        "K_DISTRACTORS": K_DISTRACTORS,
        "N_TRAIN_CHAINS_PER_HOP": N_TRAIN_CHAINS_PER_HOP,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_hop": per_hop_results,
        "elapsed_s": float(elapsed),
    }


# -----------------------------------------------------------------------------
# Verdict
# -----------------------------------------------------------------------------
def _lookup(per_hop: List[Dict], hop: int, arm: str) -> float:
    for h in per_hop:
        if int(h["hop"]) == hop:
            for a in h["arms"]:
                if a["arm_name"] == arm:
                    return float(a["recall_at_1"])
    raise KeyError(f"(hop={hop}, arm={arm}) not found")


def _status_ok(per_hop: List[Dict]) -> Tuple[bool, str]:
    for h in per_hop:
        for a in h["arms"]:
            if a["arm_status"] != "OK":
                return False, f"hop={h['hop']} arm={a['arm_name']}: {a['arm_status']}"
    return True, ""


def compute_verdict(results: List[Dict]) -> Tuple[str, str, Dict]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.", {})

    # Cardinality
    n_seeds = len(results)
    total_arms = 0
    for r in results:
        for h in r.get("per_hop", []):
            total_arms += len(h.get("arms", []))
    if n_seeds != len(SEEDS) or total_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"n_seeds={n_seeds}/{len(SEEDS)}, "
                f"total_arms={total_arms}/{EXPECTED_N_UNITS}", {})

    for r in results:
        ok, msg = _status_ok(r["per_hop"])
        if not ok:
            return ("HARD_FAIL",
                    f"HARD_FAIL_ARM_ERROR seed={r['seed']}: {msg}", {})

    # Aggregate per (arm, hop) across seeds
    mean_per_arm_hop: Dict[Tuple[str, int], float] = {}
    std_per_arm_hop: Dict[Tuple[str, int], float] = {}
    for arm in ARM_NAMES:
        for hop in HOPS:
            vals = [_lookup(r["per_hop"], hop, arm) for r in results]
            mean_per_arm_hop[(arm, hop)] = float(np.mean(vals))
            std_per_arm_hop[(arm, hop)] = float(np.std(vals))

    def m(arm: str, hop: int) -> float:
        return mean_per_arm_hop[(arm, hop)]

    cleanup_h2 = m("ARM_HRR_RECURRENT_UNBIND_CLEANUP", 2)
    cleanup_h3 = m("ARM_HRR_RECURRENT_UNBIND_CLEANUP", 3)
    cleanup_h4 = m("ARM_HRR_RECURRENT_UNBIND_CLEANUP", 4)
    no_cleanup_h2 = m("ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP", 2)
    no_cleanup_h3 = m("ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP", 3)
    no_cleanup_h4 = m("ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP", 4)
    bundled_h2 = m("ARM_HRR_BUNDLED_LOOKUP", 2)
    bundled_h3 = m("ARM_HRR_BUNDLED_LOOKUP", 3)
    bundled_h4 = m("ARM_HRR_BUNDLED_LOOKUP", 4)
    cosine_h2 = m("ARM_COSINE_ARGMAX_BASELINE", 2)
    random_h2 = m("ARM_RANDOM_BASELINE", 2)

    hp1 = cleanup_h2 >= 0.50
    hp2 = (cleanup_h3 - no_cleanup_h3) >= 0.15
    hp3 = (cleanup_h3 >= 0.30) and ((cleanup_h3 - bundled_h3) >= 0.20)
    hp4 = (cleanup_h2 - cosine_h2) >= 0.30

    gates = {
        "cleanup_h2": cleanup_h2, "cleanup_h3": cleanup_h3, "cleanup_h4": cleanup_h4,
        "no_cleanup_h2": no_cleanup_h2, "no_cleanup_h3": no_cleanup_h3, "no_cleanup_h4": no_cleanup_h4,
        "bundled_h2": bundled_h2, "bundled_h3": bundled_h3, "bundled_h4": bundled_h4,
        "cosine_h2": cosine_h2, "random_h2": random_h2,
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3), "hp4": bool(hp4),
        "hp2_gap": cleanup_h3 - no_cleanup_h3,
        "hp3_gap": cleanup_h3 - bundled_h3,
        "hp4_gap": cleanup_h2 - cosine_h2,
        "hop_degradation": {
            "h2_to_h3": cleanup_h2 - cleanup_h3,
            "h3_to_h4": cleanup_h3 - cleanup_h4,
            "monotone": (cleanup_h2 >= cleanup_h3) and (cleanup_h3 >= cleanup_h4),
        },
        "std_per_arm_hop": {f"{a}@h{h}": std_per_arm_hop[(a, h)]
                              for a in ARM_NAMES for h in HOPS},
    }

    # HARD_FAIL bands
    if cleanup_h2 < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL_HF1: CLEANUP r@1 at HOP=2 = {cleanup_h2:.3f} < 0.30. "
                f"Substrate cannot chain unbinds even at 2-hop. "
                f"cleanup@h2={cleanup_h2:.3f} @h3={cleanup_h3:.3f} @h4={cleanup_h4:.3f} | "
                f"no_cleanup@h3={no_cleanup_h3:.3f} bundled@h3={bundled_h3:.3f} "
                f"cosine@h2={cosine_h2:.3f} random@h2={random_h2:.3f}",
                gates)

    if bundled_h2 > cleanup_h2 + 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL_bundled_beats_mechanism: BUNDLED_LOOKUP@h2={bundled_h2:.3f} "
                f"> CLEANUP@h2={cleanup_h2:.3f} + 0.05. Likely test-chain leakage "
                f"into training-chain bundle.",
                gates)

    summary = (
        f"n_seeds={n_seeds} n_dim={N_DIM} N_ENT={N_ENTITIES} FPE={FACTS_PER_ENTITY} "
        f"K_DIST={K_DISTRACTORS} N_Q/hop={N_QUERIES_PER_HOP} | "
        f"CLEANUP@h2={cleanup_h2:.3f}+/-{std_per_arm_hop[('ARM_HRR_RECURRENT_UNBIND_CLEANUP',2)]:.3f} "
        f"@h3={cleanup_h3:.3f}+/-{std_per_arm_hop[('ARM_HRR_RECURRENT_UNBIND_CLEANUP',3)]:.3f} "
        f"@h4={cleanup_h4:.3f}+/-{std_per_arm_hop[('ARM_HRR_RECURRENT_UNBIND_CLEANUP',4)]:.3f} | "
        f"NO_CLEANUP@h2={no_cleanup_h2:.3f} @h3={no_cleanup_h3:.3f} @h4={no_cleanup_h4:.3f} | "
        f"BUNDLED@h2={bundled_h2:.3f} @h3={bundled_h3:.3f} @h4={bundled_h4:.3f} | "
        f"COSINE@h2={cosine_h2:.3f} RANDOM@h2={random_h2:.3f} | "
        f"HP1(cleanup@h2>=0.50)={hp1} "
        f"HP2(cleanup-no_cleanup@h3>=0.15)={hp2}(gap={gates['hp2_gap']:+.3f}) "
        f"HP3(cleanup@h3>=0.30 & vs_bundled>=0.20)={hp3}(gap={gates['hp3_gap']:+.3f}) "
        f"HP4(cleanup-cosine@h2>=0.30)={hp4}(gap={gates['hp4_gap']:+.3f}) | "
        f"hop_deg_monotone={gates['hop_degradation']['monotone']}"
    )

    if hp1 and hp2 and hp3 and hp4:
        return ("HARD_PASS",
                f"HARD_PASS: HP1+HP2+HP3+HP4 all cleared. VSA-native recurrent-unbind "
                f"mechanism performs multi-hop reasoning on held-out chain queries; "
                f"intermediate cleanup earns keep at HOP=3 (physics-law discriminator "
                f"vs NO_CLEANUP); mechanism beats bundled-chain cheat-lookup on held-out "
                f"queries. {summary}",
                gates)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: HP checks partial "
            f"hp=[hp1={hp1},hp2={hp2},hp3={hp3},hp4={hp4}]. {summary}",
            gates)


# -----------------------------------------------------------------------------
# Start marker + crash diagnostic
# -----------------------------------------------------------------------------
def _write_start_marker(output_dir: Path) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(diag, fh, indent=2)
    os.replace(str(tmp), str(final))


# -----------------------------------------------------------------------------
# Main driver
# -----------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)

    run_config = {
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds complete; running {remaining}",
          flush=True)

    t_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] stage2_vsa_cell3_multi_hop_reasoning "
              f"n_dim={N_DIM} N_ENT={N_ENTITIES} FPE={FACTS_PER_ENTITY} "
              f"HOPS={HOPS} K_DIST={K_DISTRACTORS} N_Q/hop={N_QUERIES_PER_HOP} "
              f"mode={RUN_MODE}...", flush=True)
        result = run_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg, gates = compute_verdict(all_results)
    elapsed_s = time.time() - t_start

    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.2f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    total_arm_count = 0
    for r in all_results:
        for h in r.get("per_hop", []):
            total_arm_count += len(h.get("arms", []))
    cardinality_ok = (
        len(all_results) == len(SEEDS)
        and total_arm_count == EXPECTED_N_UNITS
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} n_dim={N_DIM} N_ENT={N_ENTITIES} "
            f"FPE={FACTS_PER_ENTITY} HOPS={HOPS} K_DIST={K_DISTRACTORS} "
            f"N_Q/hop={N_QUERIES_PER_HOP} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "n_dim": N_DIM,
        "N_ENT": N_ENTITIES,
        "N_ROLES": N_ROLES,
        "FACTS_PER_ENTITY": FACTS_PER_ENTITY,
        "HOPS": list(HOPS),
        "N_QUERIES_PER_HOP": N_QUERIES_PER_HOP,
        "K_DISTRACTORS": K_DISTRACTORS,
        "N_TRAIN_CHAINS_PER_HOP": N_TRAIN_CHAINS_PER_HOP,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "gates": gates,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "per_hop": r.get("per_hop"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


if __name__ == "__main__":
    output_dir = get_output_dir(ANCHOR_NAME)
    try:
        _main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(output_dir, _exc)
        raise
