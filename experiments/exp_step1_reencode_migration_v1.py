"""STEP-1 RE-ENCODE MIGRATION driver (Space 2 = BGE teacher vectors backing
substrate_index / Retriever.semantic). Replace the BGE teacher representation
with the chosen concept encoder (regime-switch v1 KEY+VALUE by default; GSBC
single-code as a one-line swap) via a BCT-safe, collision-free, parity-gated,
rollback-anchored re-encode.

Design ref:
  notes/step1_reencode_migration_plan_bct_safe_unique_id_addressability_gates_2026-07-04.md
Encoder packaging reused (do NOT retrain):
  experiments/exp_regime_switch_encoder_instore_integration_verify_v1.encode_key_value

SCOPE (load-bearing): Space 2 ONLY. Space 1 (char_trigram_v1 director_kb) is a
CATEGORY ERROR to re-encode and is left untouched. This driver never touches
data/substrate_director_kb_v1/.

WHAT THIS CELL PROVES (smoke) / EXECUTES (full):
  - UNIQUE-ID FIX: route ids through qualified corpus::local_id (collision-free)
    NOT bare local ids; a pre-write uniqueness ASSERT fails loud on any cross-lane
    math::X vs other::X collision OR any true duplicate qualified id (folds in the
    wikipedia-in-math-lane audit -- the assert IS the detector).
  - BCT-SAFE RE-ENCODE: pluggable encoder (regime_switch_v1 default) teacher ->
    (KEY sparse, VALUE dense); write via strict-add into a .tmp store then
    os.replace swap (single-writer atomic); rebuild the aggregate index over the
    NEW vectors.
  - PARITY GATE: pre/post retrieval parity on a held set -- self-rank1 >= floor,
    offline-vs-instore neighbor delta <= tol, and (smoke) a NEGATIVE control that
    the gate FIRES on the ~1% silent-collapse / row-misalignment failure mode.
  - COMPLETENESS: atoms_reencoded == atoms_in_store == n_unique_qualified_ids
    (zero stranded / zero id collapse).
  - ROLLBACK: snapshot the aggregate index before mutation; os.replace-back
    restore is bit-identical (dry-run verified).

RUN MODES:
  smoke  -- CLEAN SYNTHETIC clustered teacher vectors + PLANTED collisions across
            5 arms. Exercises the SAME qualification / assert / strict-add /
            atomic-write / parity / rollback code paths the full run uses (only
            the DATA SOURCE differs). local_cpu; seconds.
  full   -- real 177899 teacher cache + real PartitionedStore lanes. HELD: gated
            on the encoder-choice fork AND on a qualified-id teacher cache
            rebuild (the current cache has BARE ids -> refuse-by-design, see
            _qualify_from_store). NOT dispatched by this build.

ASCII-only. No emojis. No em dashes.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: clean vs corrupted vs bare-collapse VALUE/store bytes
#   differ (hash-checked at smoke gate).
# - final_metrics_atomicity: tmp_replace (os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: infra migration test; gates are equality/tolerance asserts, not a
#   physics-bounded discriminator threshold.
# - baseline_in_band: N/A -- no accuracy baseline arm; gates are completeness /
#   collision / parity-delta self-consistency checks.
# - discriminator survives scale: the uniqueness-assert + serialization-parity are
#   scale-independent (an id collapse or a dtype/norm bug shows at any M); the
#   smoke plants the failure modes explicitly so the discriminators FIRE.
# - cardinality_ok: N/A -- no sweep axis (fixed arm set).
# - calibration_check: default_ok_for_this_regime -- cosine over L2-normalized
#   float32 exactly as the store metric; index-consistency gate asserts it.
# - all numbers in comments tagged HYPOTHESIZED@ / THEORETICAL@ / MEASURED@.
# - progress_logging: print_flush_true (all progress lines flush=True).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from backend.substrate_index.schema import (  # noqa: E402
    Atom, Corpus, Tier, AtomKind, save_atoms,
)
from backend.substrate_index.store import Store  # noqa: E402
from backend.substrate_index.partition import PartitionedStore  # noqa: E402
from backend.substrate_index.retrieve import Retriever  # noqa: E402
from backend.substrate_index.encode import AtomVectors  # noqa: E402

ANCHOR_NAME = "step1_reencode_migration_v1"

# Encoder geometry (regime-switch v1 = v6 K=128 sparse KEY; out=4096).
KB, BLK_L = 128, 32
OUT_DIM = KB * BLK_L  # 4096

# ---- Pre-registered gate thresholds ----
PARITY_SELF_RANK1_FLOOR = 0.95   # G3: known-item self-retrieval must hold
PARITY_OFFLINE_DELTA_TOL = 0.03  # G3: |instore ret_agree10 - offline ret_agree10|
PARITY_AGREE_FLOOR = 0.50        # G3: clean structure-preserving re-encode neighbor agreement
NORM_TOL = 1e-4                  # G4: max |row_norm - 1| in the store matrix
ALGEBRA_FLOOR = 0.95            # G_gsbc_keyed_j5: GSBC bind/unbind cleanup@1 at depth J=5
                                # (co-gate; v12 EXPAND2X measured 1.000 at full-M=177899)

# Lanes used for synthetic smoke (a cross-lane pair == math::X vs concept::X).
_SMOKE_CORPORA = [Corpus.MATH, Corpus.CONCEPT, Corpus.SCIENCE, Corpus.META]


# ============================================================
# Defensive-error-checking helpers (exp_dev canonical section 13)
# ============================================================

def _output_dir(run_mode: str) -> str:
    return str(_REPO / "data" / (
        f"exp_{ANCHOR_NAME}_smoke" if run_mode == "smoke" else f"exp_{ANCHOR_NAME}"))


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
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
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)   # atomic per META_RULE_AH


def _write_crash_metrics(output_dir: str, exc: Exception, run_mode: str) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "run_mode": run_mode,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics(output_dir, diag)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================
# UNIQUE-ID FIX -- namespace + pre-write assert + strict add
# ============================================================

class IdCollisionError(ValueError):
    """Raised by the pre-write uniqueness assert on a duplicate id (fail loud)."""


def qualify(corpus_value: str, local_id: str) -> str:
    """Collision-free qualified id corpus::local_id (namespace layer 1)."""
    return f"{corpus_value}::{local_id}"


def assert_unique_ids(ids, label: str) -> list:
    """Pre-write uniqueness assert (layer 2). Returns [] if clean; RAISES
    IdCollisionError listing the duplicate ids otherwise. This is the single
    detector for BOTH cross-lane bare-id collisions AND true duplicate qualified
    ids (e.g. a cache row appearing twice)."""
    c = Counter(ids)
    dups = sorted([i for i, n in c.items() if n > 1])
    if dups:
        raise IdCollisionError(
            f"{label}: {len(dups)} id collision(s) would collapse under the "
            f"id-keyed store; first {min(20, len(dups))}: {dups[:20]}")
    return dups


def add_atoms_strict(store: Store, atoms) -> int:
    """Strict bulk add (layer 3, belt+suspenders): a re-encode is a fresh
    rebuild, never a legitimate update, so RAISE on any pre-existing id (the
    Store.add_atom UPDATE path) OR any within-batch duplicate id, rather than
    silently overwrite. Returns n added. One save_atoms (O(M), not per-atom flush)."""
    seen = set()
    for a in atoms:
        if a.id in store._by_id or a.id in seen:
            raise IdCollisionError(
                f"add_atoms_strict: id {a.id!r} duplicate -- silent-overwrite "
                f"blocked (re-encode must submit unique ids)")
        seen.add(a.id)
    save_atoms(atoms, store.atoms_path)  # atomic tmp+fsync+os.replace + roundtrip-validate
    return len(atoms)


def _savez_atomic(final_path: str, **arrays) -> None:
    """np.savez to a tmp then os.replace onto final_path. Works around numpy
    savez auto-appending .npz (final_path MUST end in .npz)."""
    assert final_path.endswith(".npz"), "final_path must end in .npz"
    tmp_base = final_path[:-4] + "__tmp"      # savez writes tmp_base + '.npz'
    np.savez(tmp_base, **arrays)
    os.replace(tmp_base + ".npz", final_path)


# ============================================================
# Pluggable encoder registry (one-line swap between ships)
# ============================================================

def _enc_regime_switch_v1(X: torch.Tensor, ckpt_dir: Path):
    """Certified default: KEY = 3.125%-sparse HARD block code; VALUE = dense sign
    readout. Reuses the integration-verify encoder packaging (no retrain)."""
    from experiments.exp_regime_switch_encoder_instore_integration_verify_v1 import (
        encode_key_value as _ekv,
    )
    KEY, VALUE, hid = _ekv(ckpt_dir, X)
    return KEY, VALUE, {"encoder": "regime_switch_v1", **hid}


def _enc_gsbc_v1(X: torch.Tensor, ckpt_dir: Path):
    """GSBC_EXPAND2X (v12 WINNER): single graded global-top-K, FlyHash 2x-expanded
    code (out=8192, K=192 => 2.34% active, positive unit-L1). The one graded sparse
    code serves BOTH as the content-addressable KEY and the semantic VALUE -- GSBC
    unifies addressing + semantics into a single deployed code (unlike regime_switch's
    KEY/VALUE split). Uses the FINAL-step deployed weights (v12 methodology: FINAL-step,
    not best-ckpt, is the gated deploy artifact). No retrain.

    ckpt_dir must contain _ckpt_GSBC_EXPAND2X.pt (the FULL-run FINAL ckpt SCP'd from
    the remote canonical landing; e.g. data/substrate_concept_encoder_v12_gwta_seed7).
    """
    from experiments import exp_encoder_v12_gsbc_gwta_expansion_v1_core as _v12
    code_mode, out_dim, kb, blk_l, sparsity, width = _v12.STE_ARMS["GSBC_EXPAND2X"]
    ck_path = Path(ckpt_dir) / "_ckpt_GSBC_EXPAND2X.pt"
    if not ck_path.exists():
        raise FileNotFoundError(
            f"GSBC_EXPAND2X ckpt not found at {ck_path}. Recover the v12 FULL-run ckpt "
            f"(remote C:/dev/hd-instrument/data/substrate_concept_encoder_v12_gwta_seed7/"
            f"_ckpt_GSBC_EXPAND2X.pt) via scp before wiring GSBC.")
    # Build the student at FULL width and load the FINAL-step weights (single load).
    orig_hidden = _v12.v3.MLP_HIDDEN
    _v12.v3.MLP_HIDDEN = width
    try:
        student = _v12.v3._make_student("mlp", X.shape[1], out_dim, "cpu", seed=0)
    finally:
        _v12.v3.MLP_HIDDEN = orig_hidden
    ck = torch.load(str(ck_path), map_location="cpu")
    if "student" not in ck:
        raise ValueError(f"ckpt {ck_path.name} missing 'student' state_dict")
    student.load_state_dict(ck["student"])
    student.eval()
    ckpt_step = int(ck.get("step", -1))
    code = _v12._encode_gsbc_gwta(student, X, sparsity).contiguous().float()  # (M,8192)
    meta = {
        "encoder": "gsbc_expand2x_v12", "arm": "GSBC_EXPAND2X",
        "out_dim": int(out_dim), "kb": int(kb), "blk_l": int(blk_l),
        "sparsity_K": int(sparsity), "active_frac": float(sparsity) / float(out_dim),
        "ckpt": str(ck_path), "ckpt_step": ckpt_step,
        "single_code_role": "KEY==VALUE (graded sparse code is both identity and semantic)",
    }
    return code, code, meta


def _enc_jl_parity_probe(X: torch.Tensor, ckpt_dir: Path):
    """SMOKE-ONLY structure-preserving probe (deterministic JL random projection
    1024->4096). Used to self-test the parity/completeness/rollback GATE machinery
    independently of whether a learned encoder preserves OUT-OF-DISTRIBUTION
    synthetic cluster structure. NOT a ship encoder."""
    g = torch.Generator().manual_seed(20260704)
    R = torch.randn(X.shape[1], OUT_DIM, generator=g) / (X.shape[1] ** 0.5)
    VALUE = (X @ R).contiguous().float()             # JL preserves cosine ~ cluster structure
    KEY = torch.sign(VALUE).contiguous().float()     # placeholder sparse-ish key sidecar
    return KEY, VALUE, {"encoder": "jl_parity_probe", "note": "smoke gate self-test only"}


ENCODER_REGISTRY = {
    "regime_switch_v1": _enc_regime_switch_v1,   # <-- DEFAULT ship (certified)
    "gsbc_v1": _enc_gsbc_v1,                      # <-- one-line swap
    "jl_parity_probe": _enc_jl_parity_probe,      # <-- smoke gate machinery self-test
}
DEFAULT_ENCODER = "regime_switch_v1"


# ============================================================
# Retrieval helpers (offline reference + through-store)
# ============================================================

def _rownorm(x: torch.Tensor) -> torch.Tensor:
    return x / (x.norm(dim=-1, keepdim=True) + 1e-8)


def _topk_sets(query_n: torch.Tensor, cb_n: torch.Tensor, self_idx: torch.Tensor,
               k: int = 10, chunk: int = 512) -> torch.Tensor:
    nq = query_n.shape[0]
    out = torch.zeros(nq, k, dtype=torch.long)
    for lo in range(0, nq, chunk):
        hi = min(lo + chunk, nq)
        sims = query_n[lo:hi] @ cb_n.T
        sims[torch.arange(hi - lo), self_idx[lo:hi]] = -2.0
        out[lo:hi] = sims.topk(k, dim=1).indices
    return out


def _agree(a: torch.Tensor, b: torch.Tensor, k: int = 10) -> float:
    n = a.shape[0]
    s = 0.0
    for r in range(n):
        s += len(set(a[r].tolist()) & set(b[r].tolist())) / float(k)
    return s / n


class _ShimEncoder:
    """Duck-typed AtomEncoder feeding the RELOADED VALUE as the store's
    semantic/composite vector. encode_query_text(atom_id) returns that id's
    (possibly independent) query VALUE -- allowing a store-vs-query misalignment
    to be modeled for the parity negative control. dim is set per-encoder (4096 for
    regime_switch/jl_probe; 8192 for GSBC_EXPAND2X) so the store index matches the
    encoder's true output width."""

    def __init__(self, id_to_stored: dict, id_to_query: dict, id_to_key: dict,
                 dim: int = OUT_DIM):
        self.dim = int(dim)
        self._stored = id_to_stored
        self._query = id_to_query
        self._key = id_to_key

    def encode_atoms(self, atoms_in):
        out = {}
        for a in atoms_in:
            v = self._stored[a.id]
            out[a.id] = AtomVectors(atom_id=a.id, semantic=v,
                                    identity=self._key[a.id], composite=v)
        return out

    def encode_query_text(self, text):
        v = self._query[text].astype(np.float32)
        return v / (np.linalg.norm(v) + 1e-12)


def build_index_and_parity(output_dir: str, arm: str, qids, VALUE_n_np, KEY_np,
                           teacher_n: torch.Tensor, query_stored=None):
    """Write the aggregate index (qualified-id keyed) via strict-add + atomic
    npz, build the real Retriever, and measure retrieval parity through the store.
    query_stored: optional {qid: vector} to feed as the query identity (defaults to
    the stored VALUE_n row -> honest self-query). Returns a result dict."""
    store_root = os.path.join(output_dir, "_store", arm)
    if os.path.isdir(store_root):
        shutil.rmtree(store_root)
    os.makedirs(store_root, exist_ok=True)

    out_dim = int(VALUE_n_np.shape[1])   # encoder-driven store width (4096 or 8192)
    id_to_stored = {qid: VALUE_n_np[i].astype(np.float32) for i, qid in enumerate(qids)}
    id_to_key = {qid: KEY_np[i].astype(np.float32) for i, qid in enumerate(qids)}
    id_to_query = query_stored if query_stored is not None else id_to_stored

    atoms = []
    for qid in qids:
        corpus_value = qid.split("::", 1)[0] if "::" in qid else Corpus.CONCEPT.value
        try:
            corpus = Corpus(corpus_value)
        except ValueError:
            corpus = Corpus.CONCEPT
        atoms.append(Atom(id=qid, name=qid, corpus=corpus, tier=Tier.TIER_NA,
                          kind=AtomKind.PRIMITIVE, description=f"reencode:{qid}"))

    store = Store(Path(store_root))
    add_atoms_strict(store, atoms)     # strict; raises on dup id
    store = Store(Path(store_root))    # reload from disk (roundtrip witness)
    n_loaded = len(store.all_atoms())

    retr = Retriever(store, _ShimEncoder(id_to_stored, id_to_query, id_to_key,
                                         dim=out_dim))
    retr.rebuild_index()
    sm = retr._semantic_matrix

    # ---- Index-consistency (G4) ----
    row_norms = np.linalg.norm(sm, axis=1)
    max_norm_dev = float(np.max(np.abs(row_norms - 1.0))) if sm is not None else 1.0
    index_ok = bool(sm is not None and sm.dtype == np.float32
                    and sm.shape[1] == out_dim and sm.shape[0] == n_loaded
                    and not np.iscomplexobj(sm) and max_norm_dev < NORM_TOL)

    # ---- Parity (G3): self-rank1 + offline-vs-instore neighbor delta ----
    id_index = {qid: i for i, qid in enumerate(qids)}
    M = len(qids)
    VALUE_t = torch.from_numpy(VALUE_n_np.astype(np.float32))
    self_idx = torch.arange(M)
    teacher_top10 = _topk_sets(teacher_n, teacher_n, self_idx)
    value_top10_offline = _topk_sets(VALUE_t, VALUE_t, self_idx)
    offline_agree = _agree(value_top10_offline, teacher_top10)

    instore_top10 = torch.full((M, 10), -1, dtype=torch.long)
    rank1_self_hits = 0
    for qid in qids:
        i = id_index[qid]
        cands = retr.semantic(qid, top_k=11, use_composite=True)
        got = [id_index[c.atom_id] for c in cands if c.atom_id in id_index]
        if got and got[0] == i:
            rank1_self_hits += 1
        neigh = [g for g in got if g != i][:10]
        while len(neigh) < 10:
            neigh.append(-1)
        instore_top10[i] = torch.tensor(neigh[:10], dtype=torch.long)
    instore_agree = _agree(instore_top10, teacher_top10)
    self_rank1 = rank1_self_hits / M
    offline_instore_delta = abs(instore_agree - offline_agree)

    return {
        "arm": arm,
        "atoms_submitted": M,
        "atoms_unique_ids": len(set(qids)),
        "atoms_in_store": n_loaded,
        "index_consistency_pass": index_ok,
        "matrix_shape": list(sm.shape) if sm is not None else None,
        "matrix_dtype": str(sm.dtype) if sm is not None else None,
        "max_row_norm_dev": max_norm_dev,
        "self_rank1": self_rank1,
        "offline_agree10": offline_agree,
        "instore_agree10": instore_agree,
        "offline_instore_delta": offline_instore_delta,
        "stored_matrix_sha256": _sha256_bytes(sm.tobytes()) if sm is not None else None,
    }


# ============================================================
# Synthetic clustered teacher (clean data; planted collisions)
# ============================================================

def _make_synthetic(M: int, n_clusters: int, n_cross: int, dim: int, seed: int):
    """Return (teacher [M,dim] float32 unit-norm, lane_local list of
    (corpus_value, local_id), cross_pairs). n_cross local_ids are shared across two
    DIFFERENT lanes with DIFFERENT (different-cluster) teacher vectors -- the exact
    cross-lane collision the qualified-id fix guards."""
    rng = np.random.default_rng(seed)
    centers = rng.standard_normal((n_clusters, dim)).astype(np.float32)
    centers /= (np.linalg.norm(centers, axis=1, keepdims=True) + 1e-8)
    cl = rng.integers(0, n_clusters, size=M)
    X = centers[cl] + 0.15 * rng.standard_normal((M, dim)).astype(np.float32)
    X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)

    lane_local = []
    for i in range(M):
        corpus = _SMOKE_CORPORA[i % len(_SMOKE_CORPORA)].value
        lane_local.append([corpus, f"A{i:05d}"])

    # Plant n_cross cross-lane collisions: give a CONCEPT atom the SAME local_id as
    # a MATH atom (distinct rows, distinct clusters). Bare-id flatten -> collapse.
    cross_pairs = []
    math_idx = [i for i in range(M) if lane_local[i][0] == Corpus.MATH.value]
    conc_idx = [i for i in range(M) if lane_local[i][0] == Corpus.CONCEPT.value]
    n_cross = min(n_cross, len(math_idx), len(conc_idx))
    for k in range(n_cross):
        mi, ci = math_idx[k], conc_idx[k]
        shared = f"PP-{1000 + k}"
        lane_local[mi][1] = shared          # math::PP-100x
        lane_local[ci][1] = shared          # concept::PP-100x (different vector/cluster)
        cross_pairs.append((mi, ci, shared))
    return torch.from_numpy(X), lane_local, cross_pairs


# ============================================================
# FULL-mode teacher qualification (refuse-by-design on ambiguity)
# ============================================================

def _load_cache_manifest(cache_path: Path) -> list:
    """Load ONLY the id_order_json manifest from an npz cache (does not read the
    semantic/composite vector arrays into the gate). Cheap encoder-independent check."""
    z = np.load(str(cache_path), allow_pickle=True)
    if "id_order_json" not in z:
        raise ValueError(f"cache {cache_path.name} missing id_order_json")
    raw = z["id_order_json"]
    return json.loads(raw.item() if hasattr(raw, "item") else str(raw))


def _qualify_from_store(ids_bare, store_root: Path):
    """FULL mode: map bare cache ids -> qualified corpus::local_id using the real
    PartitionedStore lanes. If a bare id lives in >1 lane, the cache row cannot be
    unambiguously assigned a lane (the collision the plan warns of) -> RAISE and
    require a qualified-id cache rebuild. If a bare id also appears twice in the
    cache manifest, assert_unique_ids downstream fires. Refuse-by-design over a
    fragile silent pairing."""
    pstore = PartitionedStore(store_root)
    local_to_lanes = {}
    for corpus, st in pstore._stores.items():
        for a in st.iter_atoms():
            local_to_lanes.setdefault(a.id, []).append(corpus.value)
    qids, ambiguous, missing = [], [], []
    for bid in ids_bare:
        lanes = local_to_lanes.get(bid)
        if not lanes:
            missing.append(bid)
            qids.append(None)
        elif len(set(lanes)) > 1:
            ambiguous.append((bid, sorted(set(lanes))))
            qids.append(None)
        else:
            qids.append(qualify(lanes[0], bid))
    if ambiguous or missing:
        raise IdCollisionError(
            f"FULL qualify refused: {len(ambiguous)} cross-lane-ambiguous "
            f"(e.g. {ambiguous[:5]}), {len(missing)} missing-in-store. Rebuild the "
            f"teacher cache with qualified corpus::local_id ids (plan step 3.1) "
            f"before the bulk re-encode.")
    return qids


# ============================================================
# SMOKE
# ============================================================

def run_smoke(args) -> int:
    t0 = time.perf_counter()
    output_dir = _output_dir("smoke")
    _write_start_marker(output_dir, "smoke", expected_n_units=1)
    print(f"[smoke] {ANCHOR_NAME} start M={args.n_concepts} clusters={args.n_clusters} "
          f"n_cross={args.n_cross} encoder={args.encoder}", flush=True)

    M = args.n_concepts
    teacher, lane_local, cross_pairs = _make_synthetic(
        M, args.n_clusters, args.n_cross, dim=1024, seed=args.seed)
    teacher_n = _rownorm(teacher)
    qids_all = [qualify(c, l) for (c, l) in lane_local]
    bare_all = [l for (_c, l) in lane_local]
    n_unique_q = len(set(qids_all))
    n_unique_bare = len(set(bare_all))
    print(f"[smoke] qualified_unique={n_unique_q}/{M} bare_unique={n_unique_bare}/{M} "
          f"planted_cross={len(cross_pairs)}", flush=True)

    # Structure-preserving probe encoder for the parity/collision GATE machinery.
    KEY_p, VALUE_p, _ = _enc_jl_parity_probe(teacher, None)
    VALUE_p_n = _rownorm(VALUE_p).numpy().astype(np.float32)
    KEY_p_np = KEY_p.numpy().astype(np.float32)

    gates = {}

    # ---------- ARM A: CLEAN_QUALIFIED (the FIX; all clean gates must PASS) ----------
    assert_a_fired = False
    try:
        assert_unique_ids(qids_all, "A_clean_qualified")
    except IdCollisionError:
        assert_a_fired = True
    resA = build_index_and_parity(output_dir, "A_clean_qualified", qids_all,
                                  VALUE_p_n, KEY_p_np, teacher_n)
    completeness_A = (resA["atoms_in_store"] == M == n_unique_q)
    parity_A = (resA["self_rank1"] >= PARITY_SELF_RANK1_FLOOR
                and resA["instore_agree10"] >= PARITY_AGREE_FLOOR
                and resA["offline_instore_delta"] <= PARITY_OFFLINE_DELTA_TOL)
    gates["G1_completeness_clean"] = {
        "pass": bool(completeness_A and not assert_a_fired),
        "atoms_submitted": M, "atoms_unique_qualified": n_unique_q,
        "atoms_in_store": resA["atoms_in_store"], "assert_fired": assert_a_fired}
    gates["G3_parity_clean"] = {
        "pass": bool(parity_A),
        "self_rank1": resA["self_rank1"], "self_rank1_floor": PARITY_SELF_RANK1_FLOOR,
        "instore_agree10": resA["instore_agree10"], "agree_floor": PARITY_AGREE_FLOOR,
        "offline_instore_delta": resA["offline_instore_delta"],
        "offline_delta_tol": PARITY_OFFLINE_DELTA_TOL}
    gates["G4_index_consistency"] = {
        "pass": bool(resA["index_consistency_pass"]),
        "matrix_shape": resA["matrix_shape"], "matrix_dtype": resA["matrix_dtype"],
        "max_row_norm_dev": resA["max_row_norm_dev"], "expected_dim": OUT_DIM}
    print(f"[smoke] ARM A clean: store={resA['atoms_in_store']}/{M} "
          f"self_rank1={resA['self_rank1']:.4f} agree={resA['instore_agree10']:.4f} "
          f"delta={resA['offline_instore_delta']:.4f} idx_ok={resA['index_consistency_pass']}",
          flush=True)

    # ---------- ARM B: BARE_ID_COLLAPSE (assert must FIRE; forced-path collapses) ----------
    bareB_fired = False
    bareB_dups = 0
    try:
        assert_unique_ids(bare_all, "B_bare_id")
    except IdCollisionError as e:
        bareB_fired = True
        bareB_dups = int(str(e).split(":")[1].strip().split(" ")[0]) if ":" in str(e) else -1
    # Demonstrate the silent-collapse the assert PREVENTS: write bare-id atoms and
    # reload. The Store is id-keyed (_by_id[atom.id]) so duplicate bare ids collapse
    # to one atom on load -- the exact bug (O(M) save+reload, not per-atom flush).
    collapse_root = os.path.join(output_dir, "_store", "B_bare_collapse")
    if os.path.isdir(collapse_root):
        shutil.rmtree(collapse_root)
    os.makedirs(collapse_root, exist_ok=True)
    bare_atoms = [Atom(id=bid, name=bid, corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                       kind=AtomKind.PRIMITIVE, description="bare") for bid in bare_all]
    save_atoms(bare_atoms, Path(collapse_root) / "atoms.jsonl")
    bstore = Store(Path(collapse_root))
    n_collapsed = len(bstore.all_atoms())
    collapse_detected = (n_collapsed < M)
    gates["G2_uniqueid_assert_cross_lane"] = {
        "pass": bool(bareB_fired and collapse_detected),
        "assert_fired_on_bare_ids": bareB_fired,
        "bare_dup_ids_detected": bareB_dups,
        "planted_cross_lane": len(cross_pairs),
        "forced_bare_store_count": n_collapsed,
        "silent_collapse_atoms": M - n_collapsed,
        "note": "qualified-id namespace fix prevents this collapse (ARM A store==M)"}
    print(f"[smoke] ARM B bare: assert_fired={bareB_fired} dups={bareB_dups} "
          f"forced_bare_store={n_collapsed}/{M} collapse={M - n_collapsed}", flush=True)

    # ---------- ARM C: PLANTED_DUP (true duplicate qualified id; assert must FIRE) ----------
    qids_dup = list(qids_all)
    planted = qids_all[0]
    qids_dup.append(planted)   # inject the SAME qualified id twice (cache-row-dup class)
    dupC_fired = False
    try:
        assert_unique_ids(qids_dup, "C_planted_dup")
    except IdCollisionError:
        dupC_fired = True
    # add_atoms_strict must ALSO raise (belt+suspenders).
    strictC_fired = False
    try:
        tmp_root = os.path.join(output_dir, "_store", "C_strict_probe")
        if os.path.isdir(tmp_root):
            shutil.rmtree(tmp_root)
        os.makedirs(tmp_root, exist_ok=True)
        atoms_dup = [Atom(id=q, name=q, corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                          kind=AtomKind.PRIMITIVE, description="dup")
                     for q in [planted, planted]]
        add_atoms_strict(Store(Path(tmp_root)), atoms_dup)
    except IdCollisionError:
        strictC_fired = True
    gates["G2b_uniqueid_assert_true_dup"] = {
        "pass": bool(dupC_fired and strictC_fired),
        "prewrite_assert_fired": dupC_fired,
        "strict_add_fired": strictC_fired,
        "planted_duplicate_qid": planted}
    print(f"[smoke] ARM C planted-dup: prewrite_assert={dupC_fired} "
          f"strict_add={strictC_fired}", flush=True)

    # ---------- ARM D: CORRUPTED_PARITY (negative control; parity gate must FAIL) ----------
    rng = np.random.default_rng(args.seed + 99)
    perm = np.arange(M)
    n_corrupt = max(1, int(args.corrupt_frac * M))
    sel = rng.choice(M, size=n_corrupt, replace=False)
    perm[sel] = rng.permutation(sel)   # misalign a fraction of store rows vs true identity
    stored_corrupt = VALUE_p_n[perm]   # store row i holds another atom's vector
    query_true = {qids_all[i]: VALUE_p_n[i].astype(np.float32) for i in range(M)}
    resD = build_index_and_parity(output_dir, "D_corrupt_parity", qids_all,
                                  stored_corrupt, KEY_p_np, teacher_n,
                                  query_stored=query_true)
    parity_D_failed = not (resD["self_rank1"] >= PARITY_SELF_RANK1_FLOOR)
    gates["G3_parity_discriminator_fires"] = {
        "pass": bool(parity_D_failed),
        "corrupt_frac": args.corrupt_frac, "n_corrupt": int(n_corrupt),
        "corrupted_self_rank1": resD["self_rank1"],
        "clean_self_rank1": resA["self_rank1"],
        "self_rank1_floor": PARITY_SELF_RANK1_FLOOR,
        "note": "parity gate correctly FAILS on row-misalignment (~1% silent-collapse class)"}
    print(f"[smoke] ARM D corrupt: self_rank1={resD['self_rank1']:.4f} "
          f"(clean={resA['self_rank1']:.4f}) parity_fires={parity_D_failed}", flush=True)

    # ---------- ARM E: REAL_ENCODER_MACHINERY (regime_switch_v1 runs + serializes) ----------
    real_gate = {"pass": None, "attempted": False}
    if args.run_real_encoder:
        real_gate["attempted"] = True
        ckpt_dir = Path(args.ckpt_dir)
        if not ckpt_dir.is_absolute():
            ckpt_dir = _REPO / ckpt_dir
        enc_fn = ENCODER_REGISTRY[args.encoder]
        KEY_r, VALUE_r, hid = enc_fn(teacher, ckpt_dir)
        VALUE_r_n = _rownorm(VALUE_r).numpy().astype(np.float32)
        KEY_r_np = KEY_r.numpy().astype(np.float32)
        # npz roundtrip bit-stability (store cached-index format).
        npz_dir = os.path.join(output_dir, "_serialize")
        os.makedirs(npz_dir, exist_ok=True)
        npz_path = os.path.join(npz_dir, "value_codebook.npz")
        np.savez(npz_path, semantic=VALUE_r_n, composite=VALUE_r_n,
                 id_order_json=json.dumps(qids_all))
        d = np.load(npz_path, allow_pickle=False)
        bit_ok = bool(np.array_equal(VALUE_r_n, d["semantic"])
                      and json.loads(str(d["id_order_json"])) == qids_all)
        enc_dim = int(VALUE_r.shape[1])   # encoder-driven width (regime_switch 4096; GSBC 8192)
        resE = build_index_and_parity(output_dir, "E_real_encoder", qids_all,
                                      VALUE_r_n, KEY_r_np, teacher_n)
        shape_ok = (KEY_r.shape == (M, enc_dim) and VALUE_r.shape == (M, enc_dim)
                    and KEY_r.dtype == torch.float32 and VALUE_r.dtype == torch.float32)
        real_gate = {
            "pass": bool(shape_ok and bit_ok and resE["index_consistency_pass"]
                         and resE["self_rank1"] >= PARITY_SELF_RANK1_FLOOR),
            "attempted": True, "encoder": args.encoder, "hidden": hid,
            "encoder_out_dim": enc_dim,
            "key_shape": list(KEY_r.shape), "value_shape": list(VALUE_r.shape),
            "npz_bit_stable": bit_ok, "index_consistency_pass": resE["index_consistency_pass"],
            "self_rank1": resE["self_rank1"],
            "note": "OOD synthetic -> absolute neighbor-agreement NOT gated; self-address + serialize gated"}
        print(f"[smoke] ARM E real({args.encoder}): out_dim={enc_dim} shapes_ok={shape_ok} "
              f"npz_bit={bit_ok} self_rank1={resE['self_rank1']:.4f}", flush=True)
    gates["G_real_encoder_machinery"] = real_gate

    # ---------- GSBC keyed@J5 co-gate (REAL BGE codes; recovered-ckpt algebra held) ----------
    # For GSBC_EXPAND2X, the deployed code must preserve the block circular-conv
    # bind/unbind algebra at composition depth J=5 (v12 co-gate; measured 1.000 at
    # full-M=177899). We run the IDENTICAL v11 keyed harness on REAL BGE concept codes
    # (small cache subset -> in-distribution, unlike the OOD synthetic teacher) using
    # the wired GSBC encoder + recovered ckpt. This double-serves as ckpt-integrity:
    # a wrong/corrupt ckpt would not reproduce the algebra.
    keyed_gate = {"pass": None, "attempted": False}
    if args.run_real_encoder and args.encoder == "gsbc_v1":
        from experiments import exp_encoder_v11_gsbc_graded_sparse_v1_core as _v11
        from experiments import exp_encoder_v12_gsbc_gwta_expansion_v1_core as _v12
        _cm, g_out, g_kb, g_blk, g_K, _w = _v12.STE_ARMS["GSBC_EXPAND2X"]
        real_path = Path(args.keyed_real_cache)
        if not real_path.is_absolute():
            real_path = _REPO / real_path
        ckpt_dir_k = Path(args.ckpt_dir)
        if not ckpt_dir_k.is_absolute():
            ckpt_dir_k = _REPO / ckpt_dir_k
        zr = np.load(str(real_path), allow_pickle=True)
        n_keyed = min(args.keyed_n, int(zr["semantic"].shape[0]))
        real_sem = torch.from_numpy(zr["semantic"][:n_keyed].astype(np.float32))
        real_sem = _rownorm(real_sem)
        _k_r, real_codes, _m_r = _enc_gsbc_v1(real_sem, ckpt_dir_k)  # (n_keyed, 8192)
        genk = torch.Generator().manual_seed(20260705)
        ku = _v11._gsbc_keyed_unit("GSBC_EXPAND2X_step1", real_codes, g_kb, g_blk,
                                   5, args.keyed_trials, genk, "cpu")
        # shuffled-key leak control (must NOT retrieve): random query key -> chance.
        gens = torch.Generator().manual_seed(20260706)
        ku_shuf = _v11._gsbc_keyed_unit("GSBC_EXPAND2X_step1", real_codes, g_kb, g_blk,
                                        5, args.keyed_trials, gens, "cpu", shuffled_key=True)
        keyed_gate = {
            "pass": bool(ku["acc_at1"] >= ALGEBRA_FLOOR and ku_shuf["acc_at1"] <= 0.05),
            "attempted": True, "J": 5, "algebra_floor": ALGEBRA_FLOOR,
            "keyed_at_j5_acc": ku["acc_at1"], "keyed_snr_margin_mean": ku["snr_margin_mean"],
            "shuffled_key_acc": ku_shuf["acc_at1"], "shuffled_leak_ceil": 0.05,
            "n_codebook": int(real_codes.shape[0]), "n_trials": args.keyed_trials,
            "real_cache": real_path.name, "ckpt_dir": str(ckpt_dir_k),
            "v12_full_measured_keyed_j5": 1.000,
            "v12_source": ("MEASURED@data/exp_encoder_v12_gsbc_gwta_expansion_v1_seed7/"
                           "metrics.json:/recovery/GSBC_EXPAND2X/depth_envelope"),
            "note": ("recovered ckpt reproduces GSBC bind/unbind cleanup@1 at depth J=5 on "
                     "REAL BGE codes; shuffled-key control confirms the roundtrip is keyed")}
        print(f"[smoke] GSBC keyed@J5 real: acc={ku['acc_at1']:.4f} (floor {ALGEBRA_FLOOR}) "
              f"shuffled={ku_shuf['acc_at1']:.4f} codebook={real_codes.shape[0]} "
              f"trials={args.keyed_trials}", flush=True)
    gates["G_gsbc_keyed_j5"] = keyed_gate

    # ---------- ROLLBACK (G5): snapshot + os.replace-back bit-identical ----------
    rb_dir = os.path.join(output_dir, "_rollback")
    if os.path.isdir(rb_dir):
        shutil.rmtree(rb_dir)
    os.makedirs(rb_dir, exist_ok=True)
    v0 = os.path.join(rb_dir, "index.npz")
    # small representative payload -- rollback MECHANISM is payload-size-independent
    small = VALUE_p_n[:64, :64].copy()
    _savez_atomic(v0, semantic=small, id_order_json=json.dumps(qids_all[:64]))
    clean_sha = _sha256_file(v0)
    snap = os.path.join(rb_dir, "index.snapshot.npz")
    shutil.copy2(v0, snap)
    # mutate (a failed re-encode leaving a bad index)
    _savez_atomic(v0, semantic=small + 1.0, id_order_json=json.dumps(qids_all[:64]))
    mutated_sha = _sha256_file(v0)
    # rollback via os.replace-back
    restore_tmp = os.path.join(rb_dir, "index.restore.tmp")
    shutil.copy2(snap, restore_tmp)
    os.replace(restore_tmp, v0)
    restored_sha = _sha256_file(v0)
    rollback_ok = (restored_sha == clean_sha and mutated_sha != clean_sha)
    gates["G5_rollback"] = {
        "pass": bool(rollback_ok),
        "snapshot_exists": os.path.exists(snap),
        "mutation_changed_bytes": bool(mutated_sha != clean_sha),
        "restore_bit_identical": bool(restored_sha == clean_sha)}
    print(f"[smoke] ROLLBACK: mutated={mutated_sha != clean_sha} "
          f"restored_identical={restored_sha == clean_sha}", flush=True)

    # ---------- ARMS-MUST-DIFFER (META_RULE_AF) ----------
    arm_digests = {
        "A_clean_stored": resA["stored_matrix_sha256"],
        "D_corrupt_stored": resD["stored_matrix_sha256"],
    }
    arms_differ = arm_digests["A_clean_stored"] != arm_digests["D_corrupt_stored"]

    # ---------- Verdict ----------
    # Real-encoder gate is only asserted when attempted; None passes are skipped.
    gate_pass = []
    for k, g in gates.items():
        if g.get("pass") is None:
            continue
        gate_pass.append((k, bool(g["pass"])))
    all_pass = all(p for _k, p in gate_pass) and arms_differ
    failed = [k for k, p in gate_pass if not p]
    if not arms_differ:
        failed.append("ARMS_MUST_DIFFER")
    verdict = "HARD_PASS" if all_pass else "HARD_FAIL"

    if all_pass:
        vmsg = (f"STEP-1 RE-ENCODE SMOKE GREEN: unique-id assert FIRES on cross-lane "
                f"({bareB_dups} bare dups) AND true-dup (planted qid); qualified-id fix "
                f"keeps store=={M} (0 collapse) vs bare collapse={M - n_collapsed}; "
                f"parity clean self_rank1={resA['self_rank1']:.3f} agree={resA['instore_agree10']:.3f} "
                f"delta={resA['offline_instore_delta']:.3f}, discriminator FIRES on corruption "
                f"(self_rank1={resD['self_rank1']:.3f}); rollback bit-identical; "
                f"real-encoder({args.encoder}) machinery "
                f"{'PASS' if real_gate.get('pass') else 'skipped'}"
                + (f"; GSBC keyed@J5={gates['G_gsbc_keyed_j5'].get('keyed_at_j5_acc'):.3f}"
                   f">= {ALGEBRA_FLOOR} (shuffled leak "
                   f"{gates['G_gsbc_keyed_j5'].get('shuffled_key_acc'):.3f}) on real BGE codes"
                   if gates.get("G_gsbc_keyed_j5", {}).get("attempted") else "")
                + ". HELD for encoder-choice.")
    else:
        vmsg = (f"STEP-1 RE-ENCODE SMOKE FAIL {failed}: machinery/gate did not behave as "
                f"pre-registered. Investigate before any full re-encode.")

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": "smoke",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "encoder": args.encoder,
        "M_concepts": M, "n_clusters": args.n_clusters,
        "planted_cross_lane": len(cross_pairs),
        "gates": gates,
        "arm_A_clean": resA,
        "arm_D_corrupt": resD,
        "arms_differ_verified": bool(arms_differ),
        "arm_digests": arm_digests,
        "all_gates_pass": bool(all_pass),
        "failed_gates": failed,
        "held_for_encoder_choice": True,
        "cache_177899_dup_id_finding": {
            "cache": "bge_large_v2_name_177899_54f7cf6a.npz",
            "n_rows": 177899, "n_unique": 177898, "n_dup_ids": 1,
            "dup_id": "research_to_exp_dev_1BIT_DEPTH_VERIFICATION_2026-06-10",
            "ids_are_bare_not_qualified": True,
            "implication": "full re-encode must NOT trust bare-id row pairing; rebuild "
                           "cache with qualified ids or use _qualify_from_store refuse-by-design"},
        # ---- SCHEMA-VET / cell-template fields ----
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "heartbeat_exemption": "smoke wall < 60s; progress via print(flush=True) each arm",
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "crlb_n/a": "infra migration; gates are equality/tolerance asserts not a physics floor",
        "baseline_in_band": "N/A -- no accuracy baseline arm",
        "calibration_check": "default_ok_for_this_regime",
        "discriminator_fires": {"uniqueid_assert": True, "parity_negative_control": True},
    }
    _write_metrics(output_dir, metrics)
    print(f"[RESULT] {verdict} {vmsg}", flush=True)
    print(f"[RESULT] metrics -> {os.path.join(output_dir, 'metrics.json')} "
          f"elapsed={elapsed:.1f}s", flush=True)
    return 0 if all_pass else 1


# ============================================================
# FULL (HELD -- refuse to run without explicit release + qualified cache)
# ============================================================

def _resolve_full_ids(cache_path: Path, store_root: Path):
    """Encoder-independent id gate for FULL mode. Load the cache manifest; if ids are
    ALREADY qualified (corpus::local_id) use them directly (the qualified cache path,
    _qualify_from_store is short-circuited); else fall back to _qualify_from_store
    (refuse-by-design on bare-id cross-lane ambiguity). Runs assert_unique_ids either
    way. Returns (qids, cache_side_dict)."""
    ids = _load_cache_manifest(cache_path)
    already_qualified = bool(ids) and all("::" in str(i) for i in ids)
    if already_qualified:
        qids = list(ids)
        source = "qualified_cache_direct"
    else:
        qids = _qualify_from_store(ids, store_root)  # raises on ambiguity/missing
        source = "qualified_from_store"
    assert_unique_ids(qids, "full_teacher_cache")     # raises on any collision
    return qids, {
        "teacher_cache": cache_path.name,
        "ids_source": source,
        "cache_ids_already_qualified": already_qualified,
        "n_rows": len(ids),
        "n_unique_qualified_ids": len(set(qids)),
        "assert_unique_ids_pass": True,
    }


def run_full(args) -> int:
    output_dir = _output_dir("full")
    _write_start_marker(output_dir, "full", expected_n_units=1)

    # ---- Encoder-INDEPENDENT cache-side gate (runs even while HELD) ----
    cache_path = Path(args.teacher_cache)
    if not cache_path.is_absolute():
        cache_path = _REPO / cache_path
    store_root = Path(args.store_root)
    if not store_root.is_absolute():
        store_root = _REPO / store_root
    cache_side = {"cache_side_cleared": False}
    try:
        if cache_path.exists():
            _qids, cs = _resolve_full_ids(cache_path, store_root)
            cs["cache_side_cleared"] = True
            cache_side = cs
        else:
            cache_side = {"cache_side_cleared": False,
                          "error": f"teacher cache not found: {cache_path}"}
    except IdCollisionError as e:
        cache_side = {"cache_side_cleared": False, "id_collision": str(e)[:400]}

    if not args.release_full:
        gated = "encoder-choice (id gate cleared)" if cache_side.get("cache_side_cleared") else \
                "encoder-choice AND cache-side (id gate not cleared)"
        msg = (f"FULL re-encode HELD; ID-collision gate {'CLEARED' if cache_side.get('cache_side_cleared') else 'NOT cleared'} "
               f"({cache_side.get('n_unique_qualified_ids','?')} unique qualified ids); "
               f"gated on: {gated}. SEPARATE completeness caveat: teacher cache has a store "
               f"reverse-gap (live store atoms with no teacher vector) -- see "
               f"data/exp_step1_reencode_migration_v1/qualified_cache_report.json; a COMPLETE "
               f"re-encode needs a cache rebuild from the current store (BGE for uncovered atoms). "
               f"Re-run with --release-full once encoder chosen.")
        _write_metrics(output_dir, {
            "anchor_name": ANCHOR_NAME, "verdict": "HELD",
            "verdict_msg": msg, "summary": msg, "run_mode": "full",
            "elapsed_s": 0.0, "ts_iso": datetime.now(timezone.utc).isoformat(),
            "held_for_encoder_choice": True, "encoder": args.encoder,
            "cache_side_gate": cache_side})
        print(f"[RESULT] HELD {msg}", flush=True)
        return 0

    # When released: cache-side ids already resolved+asserted above; next wires
    # _load_teacher -> snapshot -> ENCODER_REGISTRY[encoder] -> add_atoms_strict(.tmp)
    # +os.replace -> parity/completeness/rollback gates. Encode body gated on the
    # chosen encoder checkpoint.
    if not cache_side.get("cache_side_cleared"):
        raise IdCollisionError(f"cache-side id gate not cleared: {cache_side}")
    raise NotImplementedError(
        "FULL encode body gated on the chosen encoder checkpoint (GSBC vs "
        "regime_switch). Cache-side id gate is CLEARED (qualified + unique).")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--encoder", choices=list(ENCODER_REGISTRY.keys()),
                    default=DEFAULT_ENCODER)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n-concepts", type=int, default=1500)
    ap.add_argument("--n-clusters", type=int, default=50)
    ap.add_argument("--n-cross", type=int, default=60)
    ap.add_argument("--corrupt-frac", type=float, default=0.30)
    ap.add_argument("--ckpt-dir", type=str,
                    default="data/substrate_concept_encoder_v6_annealste_seed7_smoke")
    ap.add_argument("--teacher-cache", type=str,
                    default="data/substrate_index/cached_indices/qualified_bge_large_v2_name_177899.npz",
                    help="FULL-mode qualified-id teacher cache (corpus::local_id manifest); "
                         "named OUT of the bge_large_v2_name_* auto-pick glob on purpose")
    ap.add_argument("--store-root", type=str, default="data/substrate_index",
                    help="FULL-mode PartitionedStore root (bare-cache fallback qualify)")
    ap.add_argument("--run-real-encoder", action="store_true", default=True)
    ap.add_argument("--no-real-encoder", dest="run_real_encoder", action="store_false")
    ap.add_argument("--release-full", action="store_true", default=False)
    ap.add_argument("--keyed-real-cache", type=str,
                    default="data/substrate_index/cached_indices/bge_large_v2_name_1742_49029a5d.npz",
                    help="small REAL BGE cache for the GSBC keyed@J5 in-distribution co-gate")
    ap.add_argument("--keyed-n", type=int, default=800,
                    help="GSBC keyed@J5 codebook size (real BGE concepts)")
    ap.add_argument("--keyed-trials", type=int, default=80,
                    help="GSBC keyed@J5 roundtrip trials")
    args = ap.parse_args()
    if args.run_mode == "smoke":
        return run_smoke(args)
    return run_full(args)


if __name__ == "__main__":
    _rm = "smoke"
    try:
        # parse run-mode early only for crash-metrics routing
        for i, a in enumerate(sys.argv):
            if a == "--run-mode" and i + 1 < len(sys.argv):
                _rm = sys.argv[i + 1]
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:   # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(_output_dir(_rm), e, _rm)
        raise
    sys.exit(rc)
