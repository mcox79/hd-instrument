"""INTEGRATION-VERIFY (Step 0 of post-encoder plan): wire the regime-switch
encoder through the LIVE substrate store code path and prove serialization /
dtype / normalization / the store's similarity metric do NOT silently degrade
retrieval or the key algebra.

Reference plan: notes/post_encoder_integration_ordered_gated_plan_reencode_
ingest_cortex_2026-07-04.md (step 0). This is the gate in front of re-encode /
ingest. It is fork-independent: plug in whichever checkpoint ships.

ENCODER (regime-switch, do NOT retrain -- reuse trained checkpoints):
  KEY   = 2%-sparse HARD block code (KB=128, BLK_L=32 -> 4096-dim), source
          v6 HARD_STE checkpoint (_encode_hard_block). Used for storage /
          addressing / bind-unbind ALGEBRA.
  VALUE = dense sign readout (4096-dim), source v6 ANNEAL_STE checkpoint
          (_dense_sign_codes). Used for RETRIEVAL. Isotonic recal is an
          order-preserving post-hoc score map -> ret_agree10 identical with or
          without it (verified here as Gate E).

WHAT THIS TESTS (that offline ret_agree10 never touches):
  Gate A  in-store ret_agree10 vs offline ret_agree10 on the SAME checkpoint,
          measured THROUGH the real Retriever.semantic() cosine path
          (matrix @ q over the store's float32 _semantic_matrix). |delta| small
          => serialization / dtype / the store's similarity metric preserve
          retrieval. (Absolute-vs-0.65 requires the FULL checkpoint + 177899
          teacher cache; the same cell reports that on ship. Locally we have
          only the smoke checkpoint, so the load-bearing gate is the
          offline-vs-in-store DELTA on that checkpoint.)
  Gate B  keyed@J (bind/unbind/cleanup, real hdlab.binding primitives) on the
          RELOADED-from-disk KEY codebook vs the IN-MEMORY KEY codebook.
          |delta| ~ 0 => store serialization preserves the sparse-key algebra.
  Gate C  dtype / normalization / shape integrity at every write+read boundary
          (float32, no complex64, shape 4096, unit-norm rows in the store
          matrix).
  Gate D  bit-stability: KEY + VALUE codebooks survive npz save+reload
          (the store cached-index format: keys semantic/composite/id_order_json)
          np.array_equal bit-exact.
  Gate E  isotonic monotone-invariance: applying the fitted isotonic map to
          cosine scores leaves ret_agree10 unchanged (order-preserving) AND
          reduces calib_err. Confirms the recalibration integrates cleanly.

If a gate FAILS that is the finding (the silent integration bug) -- diagnose it.

Real store machinery exercised (NOT numpy reimplementation):
  backend.substrate_index.store.Store        (add_atom + save_atoms JSONL roundtrip)
  backend.substrate_index.partition.PartitionedStore (reachability via coordinator)
  backend.substrate_index.retrieve.Retriever (rebuild_index float32 matrix + semantic() cosine)
  hdlab.binding.bind / unbind                (real HRR circular-conv key algebra)
  experiments...v1_core._chunked_cleanup_argmax (real cleanup)

ASCII-only. No emojis. No em dashes.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ: EXEMPTED -- the in-memory vs reloaded "arms" are INTENTIONALLY
#   bit-identical; that identity IS Gate D (serialization roundtrip). Declared
#   arms_differ_exempted in pre-reg.
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor -- integration/serialization test,
#   gates are delta-tolerances not a physics-bounded discriminator threshold.
# - baseline_in_band: N/A -- no baseline arm; gates are self-consistency deltas.
# - discriminator survives scale: N/A -- plumbing test; the "discriminator" is a
#   serialization delta that is scale-independent (a dtype/norm bug shows at any M).
# - cardinality_ok: N/A -- no sweep axis (single M, single checkpoint).
# - calibration_check: default_ok_for_this_regime -- store uses cosine over
#   L2-normalized float32 exactly as the offline metric does; Gate C asserts it.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ in the pre-reg.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
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
from hdlab.binding import bind, unbind  # noqa: E402  (real substrate primitives)
from backend.substrate_index.schema import (  # noqa: E402
    Atom, Corpus, Tier, AtomKind,
)
from backend.substrate_index.store import Store  # noqa: E402
from backend.substrate_index.partition import PartitionedStore  # noqa: E402
from backend.substrate_index.retrieve import Retriever  # noqa: E402
from backend.substrate_index.encode import AtomVectors  # noqa: E402

ANCHOR_NAME = "regime_switch_encoder_instore_integration_verify_v1"
KB, BLK_L = 128, 32                 # v6 K=128 sparse KEY (3.125% active); out=4096
OUT_DIM = KB * BLK_L
J_DEPTHS = [1, 2, 3, 4, 5]

# ---- Gate thresholds (pre-registered) ----
RET_DELTA_TOL = 0.02               # Gate A: |in_store_ret - offline_ret|
KEYED_DELTA_TOL = 0.01             # Gate B: |keyed_reload - keyed_inmem| at each J
NORM_TOL = 1e-4                    # Gate C: max |row_norm - 1| in store matrix
# Gate E: isotonic (PAVA) is WEAKLY monotone -- flat plateaus create ties, so a
# few rank-10-boundary neighbors can swap. The property tested is "no ranking
# BREAK beyond tie-noise AND calibration improves", not strict bit-invariance.
ISO_INVARIANCE_TOL = 0.01         # Gate E: |ret_iso - ret_base| tie-noise band
OFFLINE_FULL_TARGET = 0.65         # HYPOTHESIZED@plan; only valid on FULL checkpoint


# ============================================================
# Defensive-error-checking helpers (per exp_dev canonical section 13)
# ============================================================

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


# ============================================================
# Encoder packaging (reuse trained checkpoints; DO NOT retrain)
# ============================================================

def _infer_hidden(state_dict: dict) -> int:
    """Read the MLP hidden width from the checkpoint (smoke=256, full=2048).

    Checkpoint-independent: works for whichever checkpoint ships.
    """
    w = state_dict.get("net.0.weight")
    if w is None:
        raise KeyError("checkpoint student missing net.0.weight (unexpected arch)")
    return int(w.shape[0])


def _load_student(ckpt_path: Path, in_dim: int) -> torch.nn.Module:
    ck = torch.load(str(ckpt_path), map_location="cpu")
    hidden = _infer_hidden(ck["student"])
    orig = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = hidden
    try:
        student = v3._make_student("mlp", in_dim, OUT_DIM, "cpu", seed=0)
    finally:
        v3.MLP_HIDDEN = orig
    student.load_state_dict(ck["student"])   # strict: raises on any dim mismatch
    student.eval()
    return student, hidden


def encode_key_value(ckpt_dir: Path, X: torch.Tensor):
    """Package the regime-switch encoder: X (teacher BGE) -> (KEY sparse, VALUE dense).

    Both float32 (M, 4096). KEY = hard block code (HARD_STE). VALUE = dense sign
    code (ANNEAL_STE). No training; checkpoints loaded read-only.
    """
    key_ckpt = ckpt_dir / "_ckpt_HARD_STE.pt"
    val_ckpt = ckpt_dir / "_ckpt_ANNEAL_STE.pt"
    for p in (key_ckpt, val_ckpt):
        if not p.exists():
            raise FileNotFoundError(f"checkpoint not found: {p}")
    key_student, key_hidden = _load_student(key_ckpt, X.shape[1])
    val_student, val_hidden = _load_student(val_ckpt, X.shape[1])
    KEY = v3._encode_hard_block(key_student, X, KB, BLK_L)   # (M, 4096) float32 sparse
    VALUE = v3._dense_sign_codes(val_student, X)             # (M, 4096) float32 dense
    return KEY, VALUE, {"key_hidden": key_hidden, "val_hidden": val_hidden}


# ============================================================
# Offline reference metrics (numpy path -- the eval harness) + isotonic
# ============================================================

def _topk_sets(query_n: torch.Tensor, cb_n: torch.Tensor, self_idx: torch.Tensor,
               k: int = 10, chunk: int = 512):
    """Top-k codebook indices per query row, excluding each row's own index."""
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


def _pava(x: np.ndarray, y: np.ndarray):
    order = np.argsort(x, kind="mergesort")
    ys = y[order].astype(np.float64)
    xs = x[order].astype(np.float64)
    vals, cnts = [], []
    for v in ys:
        vals.append(float(v)); cnts.append(1)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            v2 = vals.pop(); c2 = cnts.pop()
            v1 = vals.pop(); c1 = cnts.pop()
            vals.append((v1 * c1 + v2 * c2) / (c1 + c2)); cnts.append(c1 + c2)
    out = np.empty(len(ys), dtype=np.float64)
    idx = 0
    for v, c in zip(vals, cnts):
        out[idx:idx + c] = v; idx += c
    return xs, out


def _apply_iso(xs, yhat, q):
    return np.interp(q, xs, yhat, left=float(yhat[0]), right=float(yhat[-1]))


# ============================================================
# Key algebra through bind/unbind/cleanup (real substrate primitives)
# ============================================================

def keyed_at_J(KEY: torch.Tensor, qsub: torch.Tensor, rng, gen, J: int) -> float:
    """Compose J keys (bundle of bind(role_j, key_j)), unbind query role, cleanup
    against the KEY codebook; fraction recovering the correct index. keyed@J.
    """
    M = KEY.shape[0]
    KEY3 = KEY.reshape(M, KB, BLK_L)
    key_ests = torch.zeros(qsub.shape[0], OUT_DIM)
    for r, q in enumerate(qsub.tolist()):
        if J > 1:
            dr = rng.choice(M, size=J - 1, replace=False)
            dr = dr[dr != q][:J - 1]
            while dr.shape[0] < J - 1:
                extra = int(rng.integers(0, M))
                if extra != q and extra not in dr:
                    dr = np.append(dr, extra)
            fi = np.concatenate([[q], dr])
        else:
            fi = np.array([q])
        roles = v3._random_block_codes(J, KB, BLK_L, gen).reshape(J, KB, BLK_L)
        bundle = torch.zeros(KB, BLK_L)
        for j in range(J):
            bundle = bundle + bind(roles[j], KEY3[int(fi[j])])
        key_ests[r] = unbind(bundle, roles[0]).reshape(OUT_DIM)
    pred, _, _ = v3._chunked_cleanup_argmax(key_ests, KEY, "cpu")
    return float((pred == qsub).float().mean())


# ============================================================
# Main
# ============================================================

def run(args) -> int:
    t0 = time.perf_counter()
    output_dir = str(_REPO / "data" / (
        f"exp_{ANCHOR_NAME}_smoke" if args.run_mode == "smoke"
        else f"exp_{ANCHOR_NAME}"))
    _write_start_marker(output_dir, args.run_mode, expected_n_units=1)

    seed = args.seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    # ---- Teacher cache (the concept-vector representation the store retrieves) ----
    cache_path = v3._resolve_teacher_cache(args.teacher_cache)
    X_all, ids_all = v3._load_teacher(cache_path)
    V = X_all.shape[0]

    # Held subset (a few hundred to few thousand concepts is enough to catch plumbing).
    rng = np.random.default_rng(seed)
    M = min(args.n_concepts, V)
    sel = rng.choice(V, size=M, replace=False)
    sel.sort()
    Xhe = X_all[torch.from_numpy(sel.copy())].contiguous()
    ids = [ids_all[i] for i in sel.tolist()]
    # id uniqueness (real ingest risk: collisions collapse store entries).
    n_unique = len(set(ids))
    id_collisions = M - n_unique
    print(f"[verify] cache={cache_path.name} V={V} M={M} dim={Xhe.shape[1]} "
          f"id_collisions={id_collisions}", flush=True)

    # ---- Package encoder + encode (reuse checkpoints; no retrain) ----
    ckpt_dir = Path(args.ckpt_dir)
    if not ckpt_dir.is_absolute():
        ckpt_dir = _REPO / ckpt_dir
    KEY, VALUE, hid = encode_key_value(ckpt_dir, Xhe)
    print(f"[verify] encoded KEY{tuple(KEY.shape)} {KEY.dtype} VALUE"
          f"{tuple(VALUE.shape)} {VALUE.dtype} hidden={hid}", flush=True)

    # Normalized VALUE (what the store stores + queries with -- cosine metric).
    VALUE_n = (VALUE / (VALUE.norm(dim=-1, keepdim=True) + 1e-8)).contiguous()
    Xhe_n = Xhe / (Xhe.norm(dim=-1, keepdim=True) + 1e-8)

    nq = min(args.n_query, M)
    qsub = torch.from_numpy(rng.choice(M, size=nq, replace=False))
    teacher_top10 = _topk_sets(Xhe_n[qsub], Xhe_n, qsub)
    value_top10_offline = _topk_sets(VALUE_n[qsub], VALUE_n, qsub)
    offline_ret = _agree(value_top10_offline, teacher_top10)
    print(f"[verify] OFFLINE ret_agree10={offline_ret:.4f} (same checkpoint) nq={nq}",
          flush=True)

    gate = {}

    # ============================================================
    # Gate D: bit-stability through the store cached-index npz serialization
    # ============================================================
    npz_dir = os.path.join(output_dir, "_serialize")
    os.makedirs(npz_dir, exist_ok=True)
    key_np = KEY.numpy().astype(np.float32)
    val_np = VALUE.numpy().astype(np.float32)
    valn_np = VALUE_n.numpy().astype(np.float32)
    key_npz = os.path.join(npz_dir, "key_codebook.npz")
    val_npz = os.path.join(npz_dir, "value_codebook.npz")
    # Store cached-index format: semantic + composite + id_order_json.
    np.savez(key_npz, semantic=key_np, composite=key_np,
             id_order_json=json.dumps(ids))
    np.savez(val_npz, semantic=valn_np, composite=valn_np,
             id_order_json=json.dumps(ids))
    dkey = np.load(key_npz, allow_pickle=False)
    dval = np.load(val_npz, allow_pickle=False)
    key_reload = dkey["semantic"]
    valn_reload = dval["semantic"]
    ids_reload = json.loads(str(dval["id_order_json"]))
    key_bit = bool(np.array_equal(key_np, key_reload))
    val_bit = bool(np.array_equal(valn_np, valn_reload))
    ids_ok = bool(ids_reload == ids)
    gate["D_bitstability"] = {
        "pass": key_bit and val_bit and ids_ok,
        "key_array_equal": key_bit, "value_array_equal": val_bit,
        "id_order_preserved": ids_ok,
        "key_dtype_reload": str(key_reload.dtype),
        "value_dtype_reload": str(valn_reload.dtype),
    }
    print(f"[verify] Gate D bitstability key={key_bit} value={val_bit} "
          f"ids={ids_ok}", flush=True)

    # ============================================================
    # Real store machinery: Store (JSONL) + PartitionedStore + Retriever
    # ============================================================
    store_root = os.path.join(output_dir, "_store")
    concept_root = os.path.join(store_root, "concept")
    os.makedirs(concept_root, exist_ok=True)
    atoms = [
        Atom(id=aid, name=aid.replace("/", " ").replace("_", " "),
             corpus=Corpus.CONCEPT, tier=Tier.TIER_NA, kind=AtomKind.PRIMITIVE,
             description=f"integration-verify test concept: {aid}")
        for aid in ids
    ]
    # Witness the incremental add_atom path on a handful (real audit-log write).
    store = Store(Path(concept_root))
    for a in atoms[:5]:
        store.add_atom(a, source="integration_verify", note="incremental add witness")
    # Bulk-persist the rest via the same real machinery (save_atoms JSONL roundtrip
    # with validate_atom_roundtrip on every atom). Re-load a fresh Store from disk.
    from backend.substrate_index.schema import save_atoms
    save_atoms(atoms, Path(concept_root) / "atoms.jsonl")
    store = Store(Path(concept_root))
    n_loaded = len(store.all_atoms())
    # PartitionedStore reachability (the coordinator M3/cortex would use).
    pstore = PartitionedStore(Path(store_root))
    n_pstore_concept = pstore.stats()["partitions"]["concept"]["n_atoms"]
    print(f"[verify] store atoms loaded={n_loaded} pstore.concept={n_pstore_concept} "
          f"(expected {M})", flush=True)

    # ---- Shim encoder feeding the RELOADED-from-npz VALUE into the real Retriever ----
    id_to_valn = {aid: valn_reload[i].astype(np.float32) for i, aid in enumerate(ids)}
    id_to_key = {aid: key_reload[i].astype(np.float32) for i, aid in enumerate(ids)}

    class _ShimEncoder:
        """Duck-typed AtomEncoder: returns the RELOADED regime-switch VALUE as the
        store's semantic/composite vector (dim=4096). encode_query_text(atom_id)
        returns that atom's normalized VALUE for a self-neighbor query."""
        dim = OUT_DIM

        def encode_atoms(self, atoms_in):
            out = {}
            for a in atoms_in:
                v = id_to_valn[a.id]
                out[a.id] = AtomVectors(
                    atom_id=a.id, semantic=v, identity=id_to_key[a.id],
                    composite=v)
            return out

        def encode_query_text(self, text):
            v = id_to_valn[text].astype(np.float32)
            return v / (np.linalg.norm(v) + 1e-12)

    retr = Retriever(store, _ShimEncoder())
    retr.rebuild_index()

    # ============================================================
    # Gate C: dtype / normalization / shape integrity of the store matrix
    # ============================================================
    sm = retr._semantic_matrix
    cm = retr._composite_matrix
    row_norms = np.linalg.norm(sm, axis=1)
    max_norm_dev = float(np.max(np.abs(row_norms - 1.0)))
    # Integrity of the STORE MATRIX itself: dtype float32, not complex, correct
    # dim, unit-norm rows, rows == atoms actually in the store. (Row COUNT is
    # validated against the store's own count n_loaded, NOT M -- id-dedup is a
    # data property surfaced by Gate F, not a dtype/normalization bug.)
    gate["C_dtype_norm"] = {
        "pass": (sm.dtype == np.float32 and sm.shape[1] == OUT_DIM
                 and sm.shape[0] == n_loaded
                 and max_norm_dev < NORM_TOL and not np.iscomplexobj(sm)),
        "matrix_dtype": str(sm.dtype),
        "matrix_shape": list(sm.shape),
        "store_atom_count": n_loaded,
        "expected_dim": OUT_DIM,
        "max_row_norm_dev": max_norm_dev,
        "is_complex": bool(np.iscomplexobj(sm)),
        "composite_matches_semantic": bool(np.array_equal(sm, cm)),
    }
    print(f"[verify] Gate C dtype={sm.dtype} shape={sm.shape} "
          f"max_norm_dev={max_norm_dev:.2e}", flush=True)

    # ============================================================
    # Gate F: completeness / addressability (id-dedup finding)
    # ============================================================
    # The Store is id-keyed, so duplicate concept-id STRINGS in the teacher cache
    # silently collapse to one atom. Completeness holds iff the store keeps every
    # UNIQUE id (n_loaded == n_unique). id_collisions > 0 is a data-quality finding
    # flagged for the re-encode/ingest completeness assert (plan step 1).
    completeness_ok = (n_loaded == n_unique and n_pstore_concept == n_unique)
    gate["F_completeness_addressability"] = {
        "pass": completeness_ok,
        "atoms_submitted": M,
        "atoms_unique_ids": n_unique,
        "atoms_in_store": n_loaded,
        "atoms_in_pstore_concept": n_pstore_concept,
        "id_collisions": id_collisions,
        "finding": (f"{id_collisions} duplicate concept-id string(s) in the teacher "
                    f"cache collapse under the id-keyed store; re-encode/ingest MUST "
                    f"assert unique ids or namespace them (completeness risk)."
                    if id_collisions else "no duplicate ids; full addressability"),
    }
    print(f"[verify] Gate F completeness store={n_loaded} unique={n_unique} "
          f"collisions={id_collisions} pass={completeness_ok}", flush=True)

    # ============================================================
    # Gate A: in-store ret_agree10 THROUGH the real Retriever.semantic() cosine
    # ============================================================
    # For each query concept, retrieve top-10 value-neighbors via the store's own
    # matrix @ q path, exclude self, compare to teacher neighbors. Also a known-item
    # self-retrieval sanity (self must come back rank-1).
    instore_top10 = torch.zeros(nq, 10, dtype=torch.long)
    id_index = {aid: i for i, aid in enumerate(ids)}
    rank1_self_hits = 0
    for r, qi in enumerate(qsub.tolist()):
        cands = retr.semantic(ids[qi], top_k=11, use_composite=True)
        got = [id_index[c.atom_id] for c in cands]
        if got and got[0] == qi:
            rank1_self_hits += 1
        neigh = [g for g in got if g != qi][:10]
        while len(neigh) < 10:
            neigh.append(-1)
        instore_top10[r] = torch.tensor(neigh[:10], dtype=torch.long)
    instore_ret = _agree(instore_top10, teacher_top10)
    rank1_self_acc = rank1_self_hits / nq
    ret_delta = abs(instore_ret - offline_ret)
    gate["A_retrieval_serialization"] = {
        "pass": ret_delta <= RET_DELTA_TOL,
        "instore_ret_agree10": instore_ret,
        "offline_ret_agree10": offline_ret,
        "delta": ret_delta,
        "tol": RET_DELTA_TOL,
        "known_item_self_rank1_acc": rank1_self_acc,
        "note_vs_0.65": ("absolute-vs-0.65 valid only on FULL checkpoint; "
                         "smoke checkpoint offline ret is the local reference"),
    }
    print(f"[verify] Gate A instore_ret={instore_ret:.4f} offline_ret={offline_ret:.4f} "
          f"delta={ret_delta:.4f} self_rank1={rank1_self_acc:.4f}", flush=True)

    # ============================================================
    # Gate B: key algebra keyed@J on RELOADED keys vs IN-MEMORY keys
    # ============================================================
    KEY_reload_t = torch.from_numpy(key_reload).contiguous()
    n_alg = min(args.n_alg, M)
    algq = torch.from_numpy(rng.choice(M, size=n_alg, replace=False))
    keyed_inmem, keyed_reload, keyed_deltas = {}, {}, {}
    for J in J_DEPTHS:
        # Both arms use freshly-seeded MATCHED generators -> identical roles +
        # distractors -> the only difference is in-memory vs reloaded keys.
        ki = keyed_at_J(KEY, algq, np.random.default_rng(seed + 900 + J),
                        torch.Generator().manual_seed(seed + 71 + J), J)
        kr = keyed_at_J(KEY_reload_t, algq, np.random.default_rng(seed + 900 + J),
                        torch.Generator().manual_seed(seed + 71 + J), J)
        keyed_inmem[J] = ki
        keyed_reload[J] = kr
        keyed_deltas[J] = abs(ki - kr)
        print(f"[verify] Gate B J={J} keyed_inmem={ki:.4f} keyed_reload={kr:.4f} "
              f"delta={abs(ki - kr):.4f}", flush=True)
    max_keyed_delta = max(keyed_deltas.values())
    gate["B_algebra_serialization"] = {
        "pass": max_keyed_delta <= KEYED_DELTA_TOL,
        "keyed_at_J_inmem": {str(J): keyed_inmem[J] for J in J_DEPTHS},
        "keyed_at_J_reload": {str(J): keyed_reload[J] for J in J_DEPTHS},
        "keyed_delta_at_J": {str(J): keyed_deltas[J] for J in J_DEPTHS},
        "max_keyed_delta": max_keyed_delta,
        "tol": KEYED_DELTA_TOL,
        "keyed_at_J5_inmem": keyed_inmem[5],
        "note_vs_1.00": ("keyed@J5 ~ 1.00 target is the FULL-checkpoint measured "
                         "value; smoke checkpoint may differ. Gate is the "
                         "reload-vs-inmem DELTA, which is checkpoint-independent."),
    }

    # ============================================================
    # Gate E: isotonic monotone-invariance of ret_agree10 + calibration improvement
    # ============================================================
    half = M // 2
    def _pairs(lo, hi, n_pairs, s):
        r = np.random.default_rng(s)
        i = r.integers(lo, hi, n_pairs); j = r.integers(lo, hi, n_pairs)
        keep = i != j; i, j = i[keep], j[keep]
        ti = torch.from_numpy(i.copy()); tj = torch.from_numpy(j.copy())
        tp = (Xhe_n[ti] * Xhe_n[tj]).sum(-1).numpy()
        sp = (VALUE_n[ti] * VALUE_n[tj]).sum(-1).numpy()
        return sp.astype(np.float64), tp.astype(np.float64)
    n_pairs = args.n_pairs
    sp_fit, tp_fit = _pairs(0, half, n_pairs, seed + 101)
    sp_ev, tp_ev = _pairs(half, M, n_pairs, seed + 202)
    xs, yhat = _pava(sp_fit, tp_fit)
    m8 = tp_ev >= 0.80
    if m8.sum() > 0:
        hi80_t = float(tp_ev[m8].mean())
        base_calib = abs(float(sp_ev[m8].mean()) - hi80_t)
        iso_calib = abs(float(_apply_iso(xs, yhat, sp_ev)[m8].mean()) - hi80_t)
    else:
        base_calib = iso_calib = float("nan")
    # ret_agree10 invariance under the monotone map, over the query subsample.
    def _ret_with_map(map_fn):
        out = torch.zeros(nq, 10, dtype=torch.long)
        for lo in range(0, nq, 512):
            hi = min(lo + 512, nq)
            ss = VALUE_n[qsub[lo:hi]] @ VALUE_n.T
            if map_fn is not None:
                ss = torch.from_numpy(map_fn(ss.numpy().astype(np.float64)
                                             ).astype(np.float32))
            ss[torch.arange(hi - lo), qsub[lo:hi]] = -2.0
            out[lo:hi] = ss.topk(10, dim=1).indices
        return _agree(out, teacher_top10)
    ret_base = _ret_with_map(None)
    ret_iso = _ret_with_map(lambda s: _apply_iso(xs, yhat, s))
    iso_inv_delta = abs(ret_base - ret_iso)
    gate["E_isotonic_invariance"] = {
        "pass": (iso_inv_delta < ISO_INVARIANCE_TOL
                 and (np.isnan(iso_calib) or iso_calib <= base_calib + 1e-6)),
        "ret_base": ret_base, "ret_iso": ret_iso, "ret_delta": iso_inv_delta,
        "base_calib_err": base_calib, "iso_calib_err": iso_calib,
        "calib_improved": bool(np.isnan(iso_calib) or iso_calib <= base_calib),
        "note": ("isotonic is weakly-monotone (PAVA plateaus -> ties); ret change "
                 "within tie-noise band is rank-preserving-up-to-ties, not a break. "
                 "calib_err must drop (the point of recalibration)."),
    }
    print(f"[verify] Gate E iso_invariance ret_base={ret_base:.4f} ret_iso={ret_iso:.4f} "
          f"delta={iso_inv_delta:.2e} calib {base_calib:.4f}->{iso_calib:.4f}", flush=True)

    # ============================================================
    # Verdict
    # ============================================================
    all_pass = all(g["pass"] for g in gate.values())
    failed = [k for k, g in gate.items() if not g["pass"]]
    verdict = "HARD_PASS" if all_pass else "HARD_FAIL"
    if all_pass:
        vmsg = (f"IN-STORE INTEGRATION VERIFIED: retrieval delta={ret_delta:.4f}<="
                f"{RET_DELTA_TOL} (instore={instore_ret:.3f} vs offline={offline_ret:.3f}); "
                f"key-algebra reload-delta max={max_keyed_delta:.4f}; bit-stable; "
                f"float32 cosine store metric intact. run_mode={args.run_mode} "
                f"ckpt={ckpt_dir.name} (absolute-vs-0.65 needs FULL checkpoint).")
    else:
        vmsg = (f"INTEGRATION GATE FAIL {failed}: this IS the silent integration bug. "
                f"ret_delta={ret_delta:.4f} keyed_delta={max_keyed_delta:.4f} "
                f"run_mode={args.run_mode} ckpt={ckpt_dir.name}.")

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": args.run_mode,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "checkpoint_dir": str(ckpt_dir),
        "teacher_cache": cache_path.name,
        "M_concepts": M, "n_query": nq, "n_alg_trials": n_alg,
        "id_collisions": id_collisions,
        "store_atoms_loaded": n_loaded,
        "pstore_concept_atoms": n_pstore_concept,
        "hidden_widths": hid,
        "gates": gate,
        "all_gates_pass": all_pass,
        "failed_gates": failed,
        "offline_full_target_0.65": OFFLINE_FULL_TARGET,
    }
    _write_metrics(output_dir, metrics)
    print(f"[RESULT] {verdict} {vmsg}", flush=True)
    print(f"[RESULT] metrics -> {os.path.join(output_dir, 'metrics.json')} "
          f"elapsed={elapsed:.1f}s", flush=True)
    return 0 if all_pass else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--ckpt-dir", type=str,
                    default="data/substrate_concept_encoder_v6_annealste_seed7_smoke")
    ap.add_argument("--teacher-cache", type=str, default=None,
                    help="explicit .npz; default = largest bge_large_v2_name_*.npz")
    ap.add_argument("--n-concepts", type=int, default=1500)
    ap.add_argument("--n-query", type=int, default=800)
    ap.add_argument("--n-alg", type=int, default=400)
    ap.add_argument("--n-pairs", type=int, default=100_000)
    args = ap.parse_args()
    if args.run_mode == "full":
        # ship defaults: FULL checkpoint + 177899 teacher cache + larger held set.
        if args.n_concepts == 1500:
            args.n_concepts = 8000
        if args.n_query == 800:
            args.n_query = 2000
    return run(args)


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:   # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _out = str(_REPO / "data" / f"exp_{ANCHOR_NAME}_smoke")
        _write_crash_metrics(_out, e, "smoke")
        raise
    sys.exit(rc)
