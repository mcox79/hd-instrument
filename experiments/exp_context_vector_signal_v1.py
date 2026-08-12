"""exp_context_vector_signal_v1 -- does the per-encounter context vector carry ANY signal?

MEASUREMENT ONLY. This cell modifies NOTHING in hdlab/reading_grounding_loop.py or
hdlab/grounding_acquisition_loop.py; it reads their organs and re-scores their own encounters.

Pre-reg: preregs/2026-08-12_context_vector_signal_v1.md (filed BEFORE any run).

QUESTION (director's hypothesis, may be wrong): the per-encounter context vector is NOISE, and
that one cause explains (a) the ~90% per-encounter argmax flip rate, (b) PBV's inability to
verify, (c) context-conditioned sense selection at chance.

DESIGN: take the REAL reading loop's OWN encounters (recovered bit-identically from
state.evidence + state.sentence_pool, gate `trace_alignment_ok`), then re-score the SAME
encounters under 5 context conditions against the SAME anchor space with the SAME unmodified
canonicalize_fast read-out:
    REAL / SCRAMBLE_SENT (primary null) / SCRAMBLE_WORD / LESION_RANDOM / LESION_ZERO
in TWO regimes: PER-ENCOUNTER (one trace vector) and TRACE-SUM (sign of the sum of all a lemma's
traces -- reading_grounding_loop.py:567, the regime the 0.0100 swap-drop was measured over).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; sha256 over each arm's context matrix)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a declared in prereg sec 11 (primary statistic is a paired DIFFERENCE, not an estimator)
# - baseline_in_band: SCRAMBLE_SENT flip rate must not be ceiling-pinned > 0.98
# - discriminator survives scale: FULL runs the IDENTICAL 1500-sentence/segment stream the PBV
#   smoke ran, so the numbers are directly comparable to its MEASURED 7048/788
# - HARD bands strictly pre-committed in prereg sec 6 (D >= 0.10 signal / D < 0.05 noise)
# - cardinality_ok: EXPECTED_N_ARMS = 5, EXPECTED_N_REGIMES = 2
# - per-unit failure-class instrumentation: no bare except anywhere; crash -> CELL_CRASHED metrics
# - calibration_check: default_ok_for_this_regime (thresholds taken verbatim from the organ)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs ReadingLoopState / HDFactStore / ConceptSpace and calls
#   process_sentence + canonicalize_fast at ~12 sentences (not a synthetic-only branch)
# - substrate_signature: every substrate call bound against inspect.signature, base kwargs only
# - deterministic seeding: fixed ints + hashlib only; no builtin hash(), no list(set())

ASCII-only.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # progress_logging: print_flush_true

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.closed_class_lexicon import is_eligible_meaning
from hdlab.grounding_acquisition_loop import D as CTX_D
from hdlab.grounding_acquisition_loop import content_words, context_vector
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    PBV_INFORMATIVE_MIN,
    SENSE_MATCH_THRESH,
    ConceptSpace,
    ReadingLoopState,
    canonicalize_fast,
    checkpoint,
    context_vector_masked,
    normalize_lemma,
    process_sentence,
    seed_known_words,
)

from experiments._cell_heartbeat import emit_heartbeat
from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, build_curriculum_pool, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import CHUNK_SIZE, SEGMENT_POOL_LOADERS

ANCHOR_NAME = "context_vector_signal_v1"
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]
ARMS = ["REAL", "SCRAMBLE_SENT", "SCRAMBLE_WORD", "LESION_RANDOM", "LESION_ZERO"]
EXPECTED_N_ARMS = len(ARMS)
EXPECTED_N_REGIMES = 2
PRIMARY_NULL = "SCRAMBLE_SENT"

SMOKE_LIMIT_PER_SEGMENT = 200
FULL_LIMIT_PER_SEGMENT = 1500          # identical to the PBV smoke stream (comparability)
STORE_SEED = 4101
SCRAMBLE_SEED = 20260812
N_BOOTSTRAP = 2000
BLOCK = 1500                            # encounters per scoring block (memory bound)

# ---- pre-registered bands (prereg sec 6; frozen before any run) ---------------------------------
D_NOISE_MAX = 0.05          # D = flip(SCRAMBLE_SENT) - flip(REAL); below this + CI covers 0 = noise
D_SIGNAL_MIN = 0.10         # at/above this + CI excludes 0 = context carries signal
SCRAMBLE_CEILING = 0.98     # scramble flip rate above this = ceiling-limited, no primary verdict
TS_DEAD_RAW_MIN = 0.80      # trace-sum REAL-vs-SCRAMBLE raw agreement for TRACE_SUM_DEAD
TS_DEAD_KAPPA_MAX = 0.10
TS_ALIVE_KAPPA_MIN = 0.20   # AMENDED-AWAY (see AMENDMENT A2 in finalize); kept only to recompute
                            # the pre-registered LITERAL secondary verdict for the audit trail
TS_ALIVE_RAW_MAX = 0.30     # A2: the summed argmax must still DEPEND on which contexts went in
TS_SEP_MIN = 0.05           # A2: REAL minus SCRAMBLE summed-match rate at SENSE_MATCH_THRESH
TS_PREFIX_GAIN_MIN = 0.05   # A2: SCRAMBLE minus REAL prefix-sum flip rate
POSCTRL_INFORMATIVE_REF = 0.393912   # MEASURED@data/exp_pbv_hypothesis_v1_smoke/metrics.json:
                                      # arms.B_PBV.trajectory.informative_encounter_rate
POSCTRL_TOL = 0.10


# =============================================================== harness plumbing
def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_ARMS * EXPECTED_N_REGIMES, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)                      # META_RULE_AH


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "metrics.json"), diag)


def _seed_from(tag: str) -> int:
    """Deterministic integer seed from a string. hashlib, NEVER builtin hash() (PROT-023 / F.5)."""
    return int.from_bytes(hashlib.sha256(tag.encode("utf-8")).digest()[:8], "big") % (2 ** 32)


# =============================================================== corpus
def build_stream(limit: Optional[int]) -> List[Tuple[str, str]]:
    """(segment_tag, sentence) over the EXISTING reading-path corpus, in curriculum order.
    Composed EXACTLY as experiments/exp_pbv_hypothesis_v1.py:build_stream composes it, so the
    encounter population is the same one the PBV smoke measured. The 117,642 newly acquired
    OpenStax sentences are deliberately NOT read (prereg design constraint)."""
    out: List[Tuple[str, str]] = [("bootstrap", s) for _t, s in build_curriculum_pool(limit)]
    for seg in SEGMENTS[1:]:
        out.extend((seg, s) for _t, s in SEGMENT_POOL_LOADERS[seg](limit))
    return out


# =============================================================== word-vector memo
_WORD_VEC: Dict[str, np.ndarray] = {}


def word_vec(w: str, d: int = CTX_D) -> np.ndarray:
    """The per-word bipolar draw context_vector() uses, memoized. Replicates that function's math
    verbatim (sha256 -> default_rng -> choice([-1,1])). Legitimacy of the memo is not assumed: the
    `trace_alignment_ok` gate asserts our rebuilt REAL vectors are BIT-IDENTICAL to the loop's own
    stored trace.context_vec for EVERY encounter."""
    v = _WORD_VEC.get(w)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
        _WORD_VEC[w] = v
    return v


def bundle_words(words: Sequence[str], d: int = CTX_D) -> np.ndarray:
    """sign(sum of word vectors), zeros -> +1. Byte-identical to context_vector() on the same
    word list; returns the all-zero vector when the list is empty (same as context_vector)."""
    if not words:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in words:
        acc += word_vec(w, d)
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


# =============================================================== the real reading pass
def run_real_pass(stream: List[Tuple[str, str]], output_dir: str) -> Tuple[ReadingLoopState, Dict[str, object]]:
    """Run the EXISTING reading loop (arm-A configuration: pbv=False) over `stream`, unmodified,
    snapshotting the ConceptSpace at the end of each curriculum segment. Returns the final state
    plus the snapshots."""
    store = HDFactStore(n_dim=N_DIM, seed=STORE_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, load_base_vocab_seed(), source="seed_base_vocabulary")

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    snapshots: Dict[str, Tuple[List[str], np.ndarray]] = {}
    seg_of_chunk: Dict[int, str] = {}
    t0 = time.time()
    for ci in range(n_chunks):
        chunk = stream[ci * CHUNK_SIZE:(ci + 1) * CHUNK_SIZE]
        for i, (seg, sent) in enumerate(chunk):
            process_sentence(state, sent, f"real_{ci}_{i}", pass_idx=ci)
        seg_tag = chunk[-1][0] if chunk else "unknown"
        seg_of_chunk[ci] = seg_tag
        checkpoint(state, pass_idx=ci, source_tag=seg_tag, schema_thresh=SCHEMA_THRESH_FULL)
        nxt = stream[(ci + 1) * CHUNK_SIZE][0] if (ci + 1) * CHUNK_SIZE < len(stream) else None
        if nxt != seg_tag:                      # last chunk of this segment -> snapshot
            anchors, mat = state.space.anchor_matrix()
            snapshots[seg_tag] = (list(anchors), np.array(mat, copy=True))
        if ci % 10 == 0 or ci == n_chunks - 1:
            emit_heartbeat(output_dir, unit_idx=ci, total_units=n_chunks,
                           elapsed_s=time.time() - t0)
            print(f"[progress] real_pass chunk={ci + 1}/{n_chunks} "
                  f"anchors={len(state.space.anchors())} elapsed={time.time() - t0:.1f}s", flush=True)
    return state, {"snapshots": snapshots, "seg_of_chunk": seg_of_chunk,
                   "n_chunks": n_chunks, "pass_elapsed_s": round(time.time() - t0, 2)}


# =============================================================== pass cache
def _cache_paths(output_dir: str) -> Tuple[str, str]:
    return (os.path.join(output_dir, "_pass_cache.npz"),
            os.path.join(output_dir, "_pass_encounters.json"))


def save_pass_cache(output_dir: str, space: ConceptSpace, snapshots: dict,
                    encounters: List[dict], meta: dict) -> None:
    """Persist the reading pass so SCORING can run in a SECOND foreground call if the first is
    close to the 10-minute inline-local budget. Only SIGN matrices are stored: canonicalize_fast
    reads the space exclusively through `anchor_matrix()`, which is sign(sums), and sign(sign(x))
    == sign(x), so a ConceptSpace re-seeded from these signs is EXACT for every read this cell
    performs -- and the readout-fidelity gate re-runs against the REBUILT space, so the claim is
    checked, not assumed."""
    npz_path, enc_path = _cache_paths(output_dir)
    anchors, mat = space.anchor_matrix()
    payload = {"anchors": np.array(list(anchors), dtype=object), "mat": mat}
    for seg, (sa, sm) in snapshots.items():
        payload[f"snap_anchors__{seg}"] = np.array(list(sa), dtype=object)
        payload[f"snap_mat__{seg}"] = sm
    np.savez_compressed(npz_path + ".tmp.npz", **payload)
    os.replace(npz_path + ".tmp.npz", npz_path)
    _atomic_json(enc_path, {"encounters": encounters, "meta": meta})


def load_pass_cache(output_dir: str):
    npz_path, enc_path = _cache_paths(output_dir)
    if not (os.path.exists(npz_path) and os.path.exists(enc_path)):
        return None
    z = np.load(npz_path, allow_pickle=True)
    space = ConceptSpace()
    anchors = [str(a) for a in z["anchors"].tolist()]
    mat = z["mat"]
    for i, a in enumerate(anchors):
        space.seed_from_bundle(a, mat[i])
    snapshots = {}
    for k in z.files:
        if k.startswith("snap_anchors__"):
            seg = k[len("snap_anchors__"):]
            snapshots[seg] = ([str(a) for a in z[k].tolist()], z[f"snap_mat__{seg}"])
    with open(enc_path, encoding="utf-8") as f:
        blob = json.load(f)
    return space, snapshots, blob["encounters"], blob["meta"]


# =============================================================== encounter table
def build_encounters(state: ReadingLoopState, seg_of_chunk: Dict[int, str]) -> Tuple[List[dict], dict]:
    """Recover the loop's OWN encounters, in trace order, with the source sentence text.

    `trace_alignment_ok` gate: per-lemma evidence-row count must equal trace count, AND the
    rebuilt context vector must be BIT-IDENTICAL to the stored trace.context_vec for every
    encounter. Any mismatch raises -- this is the real_code_path proof that the encounter table is
    the loop's, not a re-derivation that drifted."""
    encounters: List[dict] = []
    n_mismatch = 0
    for lemma in sorted(state.evidence):
        rows = state.evidence[lemma]
        item = state.library.items.get(lemma)
        if item is None:
            raise AssertionError(f"evidence row for {lemma!r} with no library item")
        if len(rows) != len(item.traces):
            raise AssertionError(
                f"trace_alignment_ok VIOLATION: {lemma!r} has {len(rows)} evidence rows but "
                f"{len(item.traces)} traces")
        for k, (row, tr) in enumerate(zip(rows, item.traces)):
            sid = row["sent_id"]
            sent = state.sentence_pool[sid]
            words = [w for w in content_words(sent) if normalize_lemma(w) != lemma]
            vec = bundle_words(words)
            if not np.array_equal(vec, tr.context_vec):
                n_mismatch += 1
                raise AssertionError(
                    f"trace_alignment_ok VIOLATION: rebuilt context vector for {lemma!r} "
                    f"encounter {k} differs from the stored trace.context_vec")
            encounters.append({"lemma": lemma, "k": k, "sent_id": sid,
                               "pass_idx": row["pass_idx"], "words": words,
                               "segment": seg_of_chunk.get(row["pass_idx"], "unknown")})
    gates = {"trace_alignment_ok": n_mismatch == 0, "n_encounters": len(encounters),
             "n_lemmas": len(state.evidence)}
    return encounters, gates


# =============================================================== arm construction
def build_arm_contexts(encounters: List[dict]) -> Tuple[Dict[str, np.ndarray], dict]:
    """Context matrix (n_enc x CTX_D) per arm. Every arm scores the IDENTICAL encounter set."""
    n = len(encounters)
    lemmas = [e["lemma"] for e in encounters]
    real_words = [e["words"] for e in encounters]

    # --- SCRAMBLE_SENT: a global permutation of which encounter's SOURCE SENTENCE supplies the
    # window, then re-masked for THIS encounter's target lemma. Preserves the encoder geometry
    # exactly (still a real sentence's bag-of-content-words bundle); removes ONLY the
    # lemma <-> context association. A within-lemma shuffle would NOT be a valid null (prereg 7).
    rng = np.random.default_rng(SCRAMBLE_SEED)
    perm = rng.permutation(n)
    fixed = np.flatnonzero(perm == np.arange(n))
    for idx in fixed:                                   # break fixed points deterministically
        j = int((idx + 1) % n)
        perm[idx], perm[j] = perm[j], perm[idx]
    scr_sent_words: List[List[str]] = []
    for i in range(n):
        src = encounters[int(perm[i])]
        cand = [w for w in src["words"] if normalize_lemma(w) != lemmas[i]]   # no-leak re-mask
        scr_sent_words.append(cand)

    # --- SCRAMBLE_WORD: re-deal the GLOBAL pooled multiset of context words, preserving each
    # encounter's window LENGTH, then re-mask. Destroys within-sentence co-occurrence too, so it
    # is the SECONDARY null (prereg sec 3).
    pool: List[str] = []
    for ws in real_words:
        pool.extend(ws)
    pool_arr = np.array(pool, dtype=object)
    rng2 = np.random.default_rng(SCRAMBLE_SEED + 1)
    pool_perm = rng2.permutation(len(pool_arr))
    scr_word_words: List[List[str]] = []
    cur = 0
    for i in range(n):
        ln = len(real_words[i])
        take = [str(pool_arr[j]) for j in pool_perm[cur:cur + ln]]
        cur += ln
        scr_word_words.append([w for w in take if normalize_lemma(w) != lemmas[i]])

    # --- paired-drop: an encounter whose window is EMPTY under ANY arm is dropped from ALL arms.
    keep = [i for i in range(n)
            if real_words[i] and scr_sent_words[i] and scr_word_words[i]]
    keep_set = set(keep)
    n_dropped = n - len(keep)

    mats: Dict[str, np.ndarray] = {}
    mats["REAL"] = np.stack([bundle_words(real_words[i]) for i in keep])
    mats["SCRAMBLE_SENT"] = np.stack([bundle_words(scr_sent_words[i]) for i in keep])
    mats["SCRAMBLE_WORD"] = np.stack([bundle_words(scr_word_words[i]) for i in keep])
    lr = np.empty((len(keep), CTX_D), dtype=np.float64)
    for r, i in enumerate(keep):
        lr[r] = np.random.default_rng(_seed_from(f"lesion_random_{i}")).choice([-1.0, 1.0], size=CTX_D)
    mats["LESION_RANDOM"] = lr
    mats["LESION_ZERO"] = np.zeros((len(keep), CTX_D), dtype=np.float64)

    # no-leak: no arm's window may contain the target lemma
    leaks = 0
    for r, i in enumerate(keep):
        for ws in (real_words[i], scr_sent_words[i], scr_word_words[i]):
            leaks += sum(1 for w in ws if normalize_lemma(w) == lemmas[i])
    digests = {a: hashlib.sha256(m.tobytes()).hexdigest() for a, m in mats.items()}
    if len(set(digests.values())) != len(digests):
        raise AssertionError(f"META_RULE_AF VIOLATION: arms bit-identical; digests={digests}")

    info = {"n_encounters_scored": len(keep), "n_dropped_empty_window": n_dropped,
            "no_leak_violations": leaks, "arms_differ_verified": True,
            "arm_digests": digests, "keep_index": keep, "keep_set_size": len(keep_set)}
    return mats, info


# =============================================================== scoring
def _eligible_anchor_view(anchors: Sequence[str], mat: np.ndarray) -> Tuple[List[str], np.ndarray, np.ndarray]:
    """Restrict the anchor matrix to ELIGIBLE, non-degenerate anchors. Restricting is equivalent to
    canonicalize_fast's -inf masking (ineligible anchors can never win), and the sorted order is
    preserved so the first-max tie-break is identical."""
    mask = np.array([is_eligible_meaning(a) for a in anchors], dtype=bool)
    norms = np.linalg.norm(mat, axis=1)
    mask &= norms >= 1e-9
    idx = np.flatnonzero(mask)
    sub_anchors = [anchors[i] for i in idx]
    sub_mat = mat[idx]
    sub_norms = norms[idx]
    return sub_anchors, sub_mat, sub_norms


def score_argmax(ctx: np.ndarray, target_lemmas: Sequence[str], anchors: Sequence[str],
                 mat: np.ndarray, norms: np.ndarray,
                 anchor_pos: Dict[str, int]) -> Tuple[np.ndarray, np.ndarray]:
    """Batched equivalent of canonicalize_fast's argmax. Returns (argmax_anchor_index, best_cos);
    index -1 marks 'no scannable anchor' (zero-norm probe), matching that function's self-return."""
    n = ctx.shape[0]
    out_idx = np.full(n, -1, dtype=np.int64)
    out_cos = np.zeros(n, dtype=np.float64)
    self_idx = np.array([anchor_pos.get(l, -1) for l in target_lemmas], dtype=np.int64)
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        X = ctx[s:e]
        xn = np.linalg.norm(X, axis=1)
        sims = (X @ mat.T) / np.outer(np.maximum(xn, 1e-12), norms)
        rows = np.flatnonzero(self_idx[s:e] >= 0)
        if rows.size:
            sims[rows, self_idx[s:e][rows]] = -np.inf   # exclude the target itself
        best = np.argmax(sims, axis=1)
        out_idx[s:e] = best
        out_cos[s:e] = sims[np.arange(e - s), best]
        zero = xn < 1e-9
        out_idx[s:e][zero] = -1
        out_cos[s:e][zero] = 0.0
    return out_idx, out_cos


# =============================================================== statistics
def _per_lemma_flip_counts(lemma_ids: np.ndarray, argmax: np.ndarray, n_lemmas: int) -> Tuple[np.ndarray, np.ndarray]:
    """(flips, pairs) per lemma over ADJACENT encounters in stream order. Encounters arrive grouped
    by lemma and ordered within lemma by construction (build_encounters)."""
    flips = np.zeros(n_lemmas, dtype=np.float64)
    pairs = np.zeros(n_lemmas, dtype=np.float64)
    same_lemma = lemma_ids[1:] == lemma_ids[:-1]
    diff_arg = argmax[1:] != argmax[:-1]
    np.add.at(pairs, lemma_ids[1:][same_lemma], 1.0)
    np.add.at(flips, lemma_ids[1:][same_lemma & diff_arg], 1.0)
    return flips, pairs


def _modal_share(lemma_ids: np.ndarray, argmax: np.ndarray, n_lemmas: int) -> np.ndarray:
    """Per lemma: share of its encounters whose argmax equals that lemma's modal argmax."""
    from collections import Counter, defaultdict
    by = defaultdict(list)
    for li, a in zip(lemma_ids.tolist(), argmax.tolist()):
        by[li].append(a)
    out = np.full(n_lemmas, np.nan)
    for li, vals in by.items():
        c = Counter(vals)
        out[li] = c.most_common(1)[0][1] / len(vals)
    return out


def _boot_indices(n_lemmas: int, n_boot: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_lemmas, size=(n_boot, n_lemmas))


def _flip_rate_ci(flips: np.ndarray, pairs: np.ndarray, boot: np.ndarray) -> Tuple[float, List[float], np.ndarray]:
    tot_p = pairs.sum()
    point = float(flips.sum() / tot_p) if tot_p > 0 else float("nan")
    bf = flips[boot].sum(axis=1)
    bp = pairs[boot].sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        dist = np.where(bp > 0, bf / np.maximum(bp, 1e-12), np.nan)
    lo, hi = np.nanpercentile(dist, [2.5, 97.5])
    return point, [float(lo), float(hi)], dist


def _agreement(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    """Raw argmax agreement + chance-corrected (Cohen-kappa style). Raw agreement is
    uninterpretable when the argmax marginal is concentrated; the corrected figure is the
    load-bearing one (prereg sec 4)."""
    n = a.shape[0]
    raw = float(np.mean(a == b))
    ua, ca = np.unique(a, return_counts=True)
    ub, cb = np.unique(b, return_counts=True)
    pa = dict(zip(ua.tolist(), (ca / n).tolist()))
    pb = dict(zip(ub.tolist(), (cb / n).tolist()))
    chance = float(sum(pa[k] * pb.get(k, 0.0) for k in pa))
    kappa = float((raw - chance) / (1.0 - chance)) if chance < 1.0 else float("nan")
    return {"raw": round(raw, 6), "chance": round(chance, 6), "kappa": round(kappa, 6)}


def _concentration(argmax: np.ndarray) -> Dict[str, float]:
    n = argmax.shape[0]
    _u, c = np.unique(argmax, return_counts=True)
    p = c / n
    ent = float(-(p * np.log(p)).sum())
    max_ent = math.log(len(p)) if len(p) > 1 else 1.0
    return {"n_distinct_argmax": int(len(p)), "top1_share": round(float(p.max()), 6),
            "norm_entropy": round(ent / max_ent, 6) if max_ent > 0 else 0.0}


# =============================================================== main measurement
def measure(run_mode: str, output_dir: str) -> dict:
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode == "smoke" else FULL_LIMIT_PER_SEGMENT
    cached = load_pass_cache(output_dir)
    if cached is not None:
        space, snaps, encounters, meta = cached
        align = meta["align"]
        pass_info = {"snapshots": snaps, "pass_elapsed_s": meta["pass_elapsed_s"],
                     "n_sentences": meta["n_sentences"], "cache_hit": True}
        print(f"[info] pass cache HIT: encounters={align['n_encounters']} "
              f"lemmas={align['n_lemmas']} anchors={len(space.anchors())}", flush=True)
    else:
        stream = build_stream(limit)
        print(f"[info] stream sentences={len(stream)} limit_per_segment={limit}", flush=True)
        state, pass_info = run_real_pass(stream, output_dir)
        encounters, align = build_encounters(state, pass_info["seg_of_chunk"])
        space = state.space
        snaps = pass_info["snapshots"]
        pass_info["n_sentences"] = len(stream)
        pass_info["cache_hit"] = False
        save_pass_cache(output_dir, space, snaps, encounters,
                        {"align": align, "pass_elapsed_s": pass_info["pass_elapsed_s"],
                         "n_sentences": len(stream), "limit_per_segment": limit})
        print(f"[info] encounters={align['n_encounters']} lemmas={align['n_lemmas']}", flush=True)
    if align["n_encounters"] == 0:
        raise AssertionError("no encounters recovered -- regime too small to fire the discriminator")

    mats, arm_info = build_arm_contexts(encounters)
    keep = arm_info["keep_index"]
    kept = [encounters[i] for i in keep]
    lemma_list = sorted({e["lemma"] for e in kept})
    lemma_pos = {l: i for i, l in enumerate(lemma_list)}
    lemma_ids = np.array([lemma_pos[e["lemma"]] for e in kept], dtype=np.int64)
    target_lemmas = [e["lemma"] for e in kept]
    n_lemmas = len(lemma_list)

    anchors_all, mat_all = space.anchor_matrix()
    anchors, amat, anorms = _eligible_anchor_view(list(anchors_all), mat_all)
    anchor_pos = {a: i for i, a in enumerate(anchors)}
    print(f"[info] anchors_total={len(anchors_all)} eligible={len(anchors)}", flush=True)

    # ---- read-out fidelity: our batched argmax must equal canonicalize_fast on a sample
    fid_rng = np.random.default_rng(_seed_from("readout_fidelity"))
    sample = fid_rng.choice(len(kept), size=min(200, len(kept)), replace=False)
    elig_mask_full = np.array([is_eligible_meaning(a) for a in anchors_all], dtype=bool)
    n_fid_mismatch = 0
    sub_idx, sub_cos = score_argmax(mats["REAL"][sample], [target_lemmas[i] for i in sample],
                                    anchors, amat, anorms, anchor_pos)
    for r, i in enumerate(sample.tolist()):
        ref_obj, ref_cos = canonicalize_fast(target_lemmas[i], mats["REAL"][i], space,
                                             thresh=PBV_INFORMATIVE_MIN,
                                             eligible_mask=elig_mask_full)
        mine = anchors[int(sub_idx[r])] if sub_idx[r] >= 0 else target_lemmas[i]
        mine_out = mine if sub_cos[r] >= PBV_INFORMATIVE_MIN else target_lemmas[i]
        if mine_out != ref_obj or abs(float(sub_cos[r]) - float(ref_cos)) > 1e-9:
            n_fid_mismatch += 1
    if n_fid_mismatch:
        raise AssertionError(
            f"readout_fidelity VIOLATION: batched argmax disagrees with canonicalize_fast on "
            f"{n_fid_mismatch}/{len(sample)} sampled encounters")

    boot = _boot_indices(n_lemmas, N_BOOTSTRAP, _seed_from("bootstrap"))
    per_enc: Dict[str, dict] = {}
    argmaxes: Dict[str, np.ndarray] = {}
    flip_parts: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    t0 = time.time()
    for arm in ARMS:
        idx, cos = score_argmax(mats[arm], target_lemmas, anchors, amat, anorms, anchor_pos)
        argmaxes[arm] = idx
        flips, pairs = _per_lemma_flip_counts(lemma_ids, idx, n_lemmas)
        flip_parts[arm] = (flips, pairs)
        fr, ci, _ = _flip_rate_ci(flips, pairs, boot)
        ms = _modal_share(lemma_ids, idx, n_lemmas)
        ms_boot = np.nanmean(ms[boot], axis=1)
        in_window = float(np.mean([
            (anchors[int(idx[r])] in set(kept[r]["words"])) if idx[r] >= 0 else False
            for r in range(len(kept))]))
        per_enc[arm] = {
            "flip_rate": round(fr, 6), "flip_rate_ci95": [round(ci[0], 6), round(ci[1], 6)],
            "n_pairs": int(pairs.sum()),
            "modal_share_mean": round(float(np.nanmean(ms)), 6),
            "modal_share_ci95": [round(float(np.nanpercentile(ms_boot, 2.5)), 6),
                                 round(float(np.nanpercentile(ms_boot, 97.5)), 6)],
            "informative_rate": round(float(np.mean(cos >= PBV_INFORMATIVE_MIN)), 6),
            "sense_thresh_rate": round(float(np.mean(cos >= SENSE_MATCH_THRESH)), 6),
            "best_cos_mean": round(float(np.mean(cos)), 6),
            "argmax_in_own_window_rate": round(in_window, 6),
            "concentration": _concentration(idx),
        }
        print(f"[progress] per_encounter arm={arm} flip={fr:.4f} elapsed={time.time() - t0:.1f}s",
              flush=True)

    # ---- paired REAL - SCRAMBLE difference, bootstrapped on the SAME resampled lemma sets
    def _paired_D(null_arm: str) -> dict:
        fR, pR = flip_parts["REAL"]
        fS, pS = flip_parts[null_arm]
        _, _, dR = _flip_rate_ci(fR, pR, boot)
        _, _, dS = _flip_rate_ci(fS, pS, boot)
        diff = dS - dR
        return {"D_point": round(float(per_enc[null_arm]["flip_rate"] - per_enc["REAL"]["flip_rate"]), 6),
                "D_ci95": [round(float(np.nanpercentile(diff, 2.5)), 6),
                           round(float(np.nanpercentile(diff, 97.5)), 6)],
                "D_frac_above_zero": round(float(np.nanmean(diff > 0)), 6)}

    paired = {n: _paired_D(n) for n in ("SCRAMBLE_SENT", "SCRAMBLE_WORD", "LESION_RANDOM")}

    agree = {}
    for i, a in enumerate(ARMS):
        for b in ARMS[i + 1:]:
            agree[f"{a}|{b}"] = _agreement(argmaxes[a], argmaxes[b])

    # ---- TRACE-SUM regime: sign(sum of a lemma's trace context vectors), the
    # reading_grounding_loop.py:567 collapse, scored with SENSE_MATCH_THRESH as that gate does.
    ts: Dict[str, dict] = {}
    ts_argmax: Dict[str, np.ndarray] = {}
    order = np.argsort(lemma_ids, kind="stable")
    for arm in ARMS:
        sums = np.zeros((n_lemmas, CTX_D), dtype=np.float64)
        np.add.at(sums, lemma_ids, mats[arm])
        sig = np.sign(sums)
        sig[sig == 0] = 1.0
        zero_rows = np.all(sums == 0, axis=1)
        sig[zero_rows] = 0.0
        idx, cos = score_argmax(sig, lemma_list, anchors, amat, anorms, anchor_pos)
        ts_argmax[arm] = idx
        ts[arm] = {"n_lemmas": int(n_lemmas),
                   "sense_thresh_rate": round(float(np.mean(cos >= SENSE_MATCH_THRESH)), 6),
                   "informative_rate": round(float(np.mean(cos >= PBV_INFORMATIVE_MIN)), 6),
                   "best_cos_mean": round(float(np.mean(cos)), 6),
                   "concentration": _concentration(idx)}
    ts_agree = {}
    for i, a in enumerate(ARMS):
        for b in ARMS[i + 1:]:
            ts_agree[f"{a}|{b}"] = _agreement(ts_argmax[a], ts_argmax[b])

    # ---- prefix-sum convergence (REAL + primary null): does summing settle, and on WHOSE answer
    prefix = {}
    for arm in ("REAL", PRIMARY_NULL):
        acc = np.zeros((n_lemmas, CTX_D), dtype=np.float64)
        pre = np.empty_like(mats[arm])
        for r in order.tolist():
            li = int(lemma_ids[r])
            acc[li] += mats[arm][r]
            s = np.sign(acc[li])
            s[s == 0] = 1.0
            pre[r] = s
        idx, _cos = score_argmax(pre, target_lemmas, anchors, amat, anorms, anchor_pos)
        f, p = _per_lemma_flip_counts(lemma_ids, idx, n_lemmas)
        fr, ci, _ = _flip_rate_ci(f, p, boot)
        prefix[arm] = {"prefix_sum_flip_rate": round(fr, 6),
                       "prefix_sum_flip_ci95": [round(ci[0], 6), round(ci[1], 6)]}

    # ---- space-drift check: re-score against the segment's OWN ConceptSpace snapshot
    drift = {}
    if snaps:
        for arm in ("REAL", PRIMARY_NULL):
            idx = np.full(len(kept), -1, dtype=np.int64)
            for seg, (sanch, smat) in snaps.items():
                rows = np.flatnonzero(np.array([e["segment"] == seg for e in kept]))
                if rows.size == 0:
                    continue
                sa, sm, sn = _eligible_anchor_view(list(sanch), smat)
                if not sa:
                    continue
                spos = {a: i for i, a in enumerate(sa)}
                si, _sc = score_argmax(mats[arm][rows], [target_lemmas[r] for r in rows],
                                       sa, sm, sn, spos)
                # map snapshot-local anchor index into the GLOBAL anchor index space so that
                # cross-segment adjacent encounters compare like-for-like
                idx[rows] = np.array([anchor_pos.get(sa[int(j)], -2) if j >= 0 else -1
                                      for j in si.tolist()], dtype=np.int64)
            f, p = _per_lemma_flip_counts(lemma_ids, idx, n_lemmas)
            fr, ci, _ = _flip_rate_ci(f, p, boot)
            drift[arm] = {"snapshot_space_flip_rate": round(fr, 6),
                          "snapshot_space_flip_ci95": [round(ci[0], 6), round(ci[1], 6)]}

    return {"per_encounter": per_enc, "paired_D": paired, "argmax_agreement": agree,
            "trace_sum": ts, "trace_sum_agreement": ts_agree, "prefix_sum": prefix,
            "space_drift": drift,
            "config": {"run_mode": run_mode, "limit_per_segment": limit,
                       "n_sentences": pass_info["n_sentences"], "n_anchors_total": len(anchors_all),
                       "n_anchors_eligible": len(anchors), "n_lemmas": n_lemmas,
                       "ctx_d": CTX_D, "informative_min": PBV_INFORMATIVE_MIN,
                       "sense_match_thresh": SENSE_MATCH_THRESH, "n_bootstrap": N_BOOTSTRAP,
                       "store_seed": STORE_SEED, "scramble_seed": SCRAMBLE_SEED},
            "integrity": {**align, **{k: v for k, v in arm_info.items() if k != "keep_index"},
                          "readout_fidelity_mismatches": n_fid_mismatch,
                          "readout_fidelity_n_sampled": int(len(sample)),
                          "cardinality_ok": len(per_enc) == EXPECTED_N_ARMS and len(ts) == EXPECTED_N_ARMS,
                          "n_regimes": EXPECTED_N_REGIMES,
                          "pass_elapsed_s": pass_info["pass_elapsed_s"],
                          "n_segment_snapshots": len(snaps)}}


# =============================================================== verdict
def finalize(res: dict) -> dict:
    pe = res["per_encounter"]
    integ = res["integrity"]
    D = res["paired_D"][PRIMARY_NULL]
    d_pt, d_lo, d_hi = D["D_point"], D["D_ci95"][0], D["D_ci95"][1]
    ci_excludes_zero = (d_lo > 0.0) or (d_hi < 0.0)

    blockers = []
    if not integ.get("trace_alignment_ok"):
        blockers.append("TRACE_ALIGNMENT_FAIL")
    if integ.get("no_leak_violations", 1) != 0:
        blockers.append("NO_LEAK_VIOLATION")
    if integ.get("readout_fidelity_mismatches", 1) != 0:
        blockers.append("READOUT_FIDELITY_FAIL")
    if not integ.get("cardinality_ok"):
        blockers.append("CARDINALITY_BREACH_META_RULE_H")
    if not integ.get("arms_differ_verified"):
        blockers.append("META_RULE_AF_ARMS_IDENTICAL")
    # LESION_ZERO is pinned by construction (prereg sec 7): a non-zero value means the HARNESS is
    # wrong, not that the lesion did something. It carries no verdict weight either way.
    lz = pe["LESION_ZERO"]["flip_rate"]
    lesion_zero_pinned = (lz == 0.0) or (lz != lz)   # 0.0, or NaN when no lemma has >= 2 kept enc
    if not lesion_zero_pinned:
        blockers.append("LESION_ZERO_NOT_PINNED_HARNESS_BUG")
    # META_RULE_K: the discriminator must be able to fire at all.
    if len(set(pe[a]["flip_rate"] for a in ARMS if a != "LESION_ZERO")) == 1:
        blockers.append("DISCRIMINATOR_DEGENERATE_ALL_ARMS_IDENTICAL")

    scr = pe[PRIMARY_NULL]["flip_rate"]
    real = pe["REAL"]["flip_rate"]

    # ---- AMENDMENT A1 (2026-08-12, disclosed in prereg sec 13; applied BEFORE the FULL run) ----
    # The pre-registered ceiling guard fired on `scr > SCRAMBLE_CEILING` ALONE. Its stated
    # rationale was "no room left for REAL to be more stable" -- a premise the smoke DIRECTLY
    # FALSIFIED (scramble 0.9953, REAL 0.7666, D +0.2287). As written the guard can only ever
    # SUPPRESS A POSITIVE and can never rescue a null, which is the opposite of what a validity
    # guard is for; and a near-1.0 scramble flip rate is the CORRECT value for a working null
    # (independent draws over ~10^3 anchors), not an artifact. Amended: ceiling-limited requires
    # BOTH arms pinned. `prereg_literal_primary` below records what the UNAMENDED rule said, so
    # the amendment is auditable and cannot hide the original outcome.
    ceiling_limited_amended = (scr > SCRAMBLE_CEILING) and (real > SCRAMBLE_CEILING)
    if blockers:
        prereg_literal_primary = "VOID"
    elif scr > SCRAMBLE_CEILING:
        prereg_literal_primary = "MIDDLE_BAND_CEILING_LIMITED"
    elif d_pt < D_NOISE_MAX and not ci_excludes_zero:
        prereg_literal_primary = "CONTEXT_IS_NOISE"
    elif d_pt >= D_SIGNAL_MIN and ci_excludes_zero:
        prereg_literal_primary = "CONTEXT_CARRIES_SIGNAL"
    else:
        prereg_literal_primary = "MIDDLE_BAND_WEAK_SIGNAL"

    if blockers:
        primary = "VOID"
    elif ceiling_limited_amended:
        primary = "MIDDLE_BAND_CEILING_LIMITED"
    elif d_pt < D_NOISE_MAX and not ci_excludes_zero:
        primary = "CONTEXT_IS_NOISE"
    elif d_pt >= D_SIGNAL_MIN and ci_excludes_zero:
        primary = "CONTEXT_CARRIES_SIGNAL"
    else:
        primary = "MIDDLE_BAND_WEAK_SIGNAL"

    tsa = res["trace_sum_agreement"][f"REAL|{PRIMARY_NULL}"]
    pea = res["argmax_agreement"][f"REAL|{PRIMARY_NULL}"]
    ts = res["trace_sum"]
    ts_sep = round(ts["REAL"]["sense_thresh_rate"] - ts[PRIMARY_NULL]["sense_thresh_rate"], 6)
    pfx = res["prefix_sum"]
    d_prefix = round(pfx[PRIMARY_NULL]["prefix_sum_flip_rate"] - pfx["REAL"]["prefix_sum_flip_rate"], 6)

    # ---- AMENDMENT A2 (2026-08-12, disclosed in prereg sec 13; applied BEFORE the FULL run) ----
    # The pre-registered TRACE_SUM_ALIVE criterion ("chance-corrected REAL-vs-SCRAMBLE agreement
    # >= 0.20") was written BACKWARDS. HIGH real-vs-scramble agreement means the sum returns the
    # same anchor regardless of its input -- that is the DEAD signature, not the alive one. As
    # written, DEAD and ALIVE were both defined by high agreement and no observation could ever
    # be classified ALIVE. Amended to the direction the signature table in prereg sec 6 actually
    # requires: ALIVE = input-dependent AND the real sum separates from the scrambled sum.
    if blockers:
        secondary = "VOID"
    elif tsa["raw"] >= TS_DEAD_RAW_MIN and tsa["kappa"] <= TS_DEAD_KAPPA_MAX:
        secondary = "TRACE_SUM_DEAD_GENERIC_ATTRACTOR"
    elif ts_sep < TS_SEP_MIN and d_prefix < TS_PREFIX_GAIN_MIN:
        secondary = "TRACE_SUM_DEAD_NO_GAIN_OVER_SCRAMBLE"
    elif tsa["raw"] < TS_ALIVE_RAW_MAX and (ts_sep >= TS_SEP_MIN or d_prefix >= TS_PREFIX_GAIN_MIN):
        secondary = "TRACE_SUM_ALIVE"
    else:
        secondary = "TRACE_SUM_MIDDLE"
    prereg_literal_secondary = (
        "VOID" if blockers else
        "TRACE_SUM_DEAD" if (tsa["raw"] >= TS_DEAD_RAW_MIN and tsa["kappa"] <= TS_DEAD_KAPPA_MAX)
        else "TRACE_SUM_ALIVE" if (tsa["kappa"] >= TS_ALIVE_KAPPA_MIN and tsa["kappa"] > pea["kappa"])
        else "TRACE_SUM_MIDDLE")

    pos_dev = abs(pe["REAL"]["informative_rate"] - POSCTRL_INFORMATIVE_REF)
    pos_ctrl = {"measured_informative_rate": pe["REAL"]["informative_rate"],
                "reference_arm_B_informative_rate": POSCTRL_INFORMATIVE_REF,
                "abs_deviation": round(pos_dev, 6), "tolerance": POSCTRL_TOL,
                "flag": "POSITIVE_CONTROL_DRIFT" if pos_dev > POSCTRL_TOL else "ok",
                "note": ("arm B scored against the LIVE space at each encounter; this cell scores "
                         "against the FINAL space, so exact equality is not expected")}

    verdict = "HARD_FAIL" if blockers else ("MIDDLE_BAND" if primary.startswith("MIDDLE_BAND") else "HARD_PASS")
    msg = (f"primary={primary} (prereg-literal={prereg_literal_primary}) "
           f"D({PRIMARY_NULL}-REAL)={d_pt:+.4f} CI95[{d_lo:+.4f},{d_hi:+.4f}] | "
           f"flip REAL={pe['REAL']['flip_rate']:.4f} {PRIMARY_NULL}={scr:.4f} "
           f"WORD={pe['SCRAMBLE_WORD']['flip_rate']:.4f} RAND={pe['LESION_RANDOM']['flip_rate']:.4f} | "
           f"argmax agree REAL|{PRIMARY_NULL} raw={pea['raw']:.4f} kappa={pea['kappa']:.4f} | "
           f"secondary={secondary} trace-sum agree raw={tsa['raw']:.4f} kappa={tsa['kappa']:.4f}")
    if blockers:
        msg = "BLOCKED: " + ",".join(blockers) + " | " + msg

    return {"verdict": verdict, "verdict_msg": msg, "summary": msg[:300],
            "primary_verdict": primary, "secondary_verdict": secondary,
            "prereg_literal_primary": prereg_literal_primary,
            "prereg_literal_secondary": prereg_literal_secondary,
            "amendments": [
                "A1 ceiling guard: pre-registered rule fired on the NULL arm alone, which can only "
                "suppress a positive; amended to require BOTH arms pinned. prereg_literal_primary "
                "records the unamended outcome.",
                "A2 trace-sum ALIVE criterion was written backwards (high REAL-vs-SCRAMBLE "
                "agreement is the DEAD signature); amended to input-dependence + separation. "
                "prereg_literal_secondary records the unamended outcome."],
            "trace_sum_separation": ts_sep, "prefix_sum_D": d_prefix,
            "blockers": blockers, "positive_control": pos_ctrl,
            "bands": {"D_noise_max": D_NOISE_MAX, "D_signal_min": D_SIGNAL_MIN,
                      "scramble_ceiling": SCRAMBLE_CEILING,
                      "ts_dead_raw_min": TS_DEAD_RAW_MIN, "ts_dead_kappa_max": TS_DEAD_KAPPA_MAX,
                      "ts_alive_kappa_min_PREREG_LITERAL": TS_ALIVE_KAPPA_MIN,
                      "ts_alive_raw_max": TS_ALIVE_RAW_MAX, "ts_sep_min": TS_SEP_MIN,
                      "ts_prefix_gain_min": TS_PREFIX_GAIN_MIN},
            "cannot_fail_declared": [
                "LESION_ZERO (zero probe -> canonicalize_fast self-return; flip rate 0.000 by "
                "construction; harness sanity only, no verdict weight)"],
            **res}


# =============================================================== self-test
def self_test() -> dict:
    """Fast gate on the REAL substrate code path at tiny N (gate F.1) plus live-signature binding
    (gate F.2). Constructs the ACTUAL objects the FULL run uses -- no synthetic-only branch."""
    exercised = set()

    # F.2 -- bind every substrate call against the LIVE signature, base/portable kwargs only.
    for name, obj, kwargs in (
        ("HDFactStore", HDFactStore, {"n_dim": 64, "seed": 1}),
        ("process_sentence", process_sentence,
         {"state": None, "sentence": "", "episode_id": "", "pass_idx": 0}),
        ("canonicalize_fast", canonicalize_fast,
         {"new_lemma": "", "new_raw_sum": None, "space": None}),
        ("context_vector_masked", context_vector_masked, {"sentence": "", "target_lemma": ""}),
        ("checkpoint", checkpoint, {"state": None, "pass_idx": 0, "source_tag": ""}),
    ):
        sig = inspect.signature(obj)
        sig.bind_partial(**kwargs)
        exercised.add(name)

    # F.1 -- construct + run the REAL objects.
    store = HDFactStore(n_dim=256, seed=7,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["water", "plant", "animal", "light", "food", "grow"],
                     source="selftest_seed")
    exercised.update({"HDFactStore", "ReadingLoopState", "seed_known_words"})
    sents = [
        "the photosynthesis needs water and light to grow",
        "a plant uses photosynthesis with light and water",
        "the photosynthesis in a plant makes food from light",
        "an animal eats food that a plant made",
        "the photosynthesis stores light as food inside a plant",
        "water and light drive photosynthesis in every plant",
    ]
    for ci in range(2):
        for i, s in enumerate(sents):
            process_sentence(state, s, f"real_{ci}_{i}", pass_idx=ci)
        checkpoint(state, pass_idx=ci, source_tag="selftest", schema_thresh=SCHEMA_THRESH_FULL)
    exercised.update({"process_sentence", "checkpoint", "ConceptSpace"})
    assert isinstance(state.space, ConceptSpace)
    assert state.space.anchors(), "self-test built an EMPTY ConceptSpace -- cell would measure nothing"

    # word_vec memo must reproduce the organ's own context_vector BIT-IDENTICALLY.
    probe = "water and light drive growth"
    assert np.array_equal(bundle_words(content_words(probe)), context_vector(probe)), \
        "word_vec memo diverges from grounding_acquisition_loop.context_vector"
    exercised.add("context_vector")

    # encounter recovery + bit-identity gate on the REAL loop's own traces
    encounters, align = build_encounters(state, {0: "selftest", 1: "selftest"})
    assert align["trace_alignment_ok"], "trace_alignment_ok failed at self-test scale"
    assert encounters, "no encounters recovered at self-test scale"

    mats, info = build_arm_contexts(encounters)
    assert info["arms_differ_verified"] and info["no_leak_violations"] == 0
    assert len(set(info["arm_digests"].values())) == EXPECTED_N_ARMS, "META_RULE_AF: arms collide"

    # batched argmax must equal canonicalize_fast exactly on the real space
    anchors_all, mat_all = state.space.anchor_matrix()
    anchors, amat, anorms = _eligible_anchor_view(list(anchors_all), mat_all)
    apos = {a: i for i, a in enumerate(anchors)}
    keep = info["keep_index"]
    tl = [encounters[i]["lemma"] for i in keep]
    idx, cos = score_argmax(mats["REAL"], tl, anchors, amat, anorms, apos)
    emask = np.array([is_eligible_meaning(a) for a in anchors_all], dtype=bool)
    for r in range(len(tl)):
        ref_obj, ref_cos = canonicalize_fast(tl[r], mats["REAL"][r], state.space,
                                             thresh=PBV_INFORMATIVE_MIN, eligible_mask=emask)
        mine = anchors[int(idx[r])] if idx[r] >= 0 else tl[r]
        mine = mine if cos[r] >= PBV_INFORMATIVE_MIN else tl[r]
        assert mine == ref_obj and abs(float(cos[r]) - float(ref_cos)) < 1e-9, \
            f"readout fidelity broke at self-test row {r}: {mine!r} vs {ref_obj!r}"
    exercised.add("canonicalize_fast")

    # LESION_ZERO must be pinned (declared non-failable control, prereg sec 7)
    zi, zc = score_argmax(mats["LESION_ZERO"], tl, anchors, amat, anorms, apos)
    assert np.all(zi == -1) and np.all(zc == 0.0), "LESION_ZERO not pinned -- harness bug"

    # source scan: no builtin hash()-derived seeding, no list(set()) ordering, no bare/BaseException
    # handlers (F.5 / PROT-023 / META_RULE_J). Lines carrying SCANMARK are the scanner's own
    # literals and are skipped, else the scanner flags itself.
    scanmark = "SCAN" + "MARK"
    banned = ["list(" + "set(", "hash(", "except " + "BaseException", "except" + ":"]  # SCANMARK
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        lines = f.read().splitlines()
    for bad in banned:
        offenders = [ln for ln in lines
                     if bad in ln and scanmark not in ln and not ln.lstrip().startswith("#")
                     and "hashlib" not in ln]
        assert not offenders, f"F.5/META_RULE_J: forbidden construct {bad!r}: {offenders[:2]}"

    return {"real_code_path_exercised": sorted(exercised),
            "n_encounters_selftest": len(encounters),
            "n_anchors_selftest": len(anchors),
            "selftest_ok": True}


# =============================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full", "self_test"], default="full")
    ap.add_argument("--self-test", action="store_true", dest="self_test_flag")
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test_flag else args.mode

    if run_mode == "self_test":
        st = self_test()
        print(json.dumps(st, indent=2), flush=True)
        sys.exit(0)

    output_dir = _output_dir(run_mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, run_mode)
    t0 = time.time()
    st = self_test()
    res = measure(run_mode, output_dir)
    out = finalize(res)
    out.update({"anchor_name": ANCHOR_NAME, "run_mode": run_mode,
                "elapsed_s": round(time.time() - t0, 2),
                "ts_iso": datetime.now(timezone.utc).isoformat(),
                "prereg": "preregs/2026-08-12_context_vector_signal_v1.md",
                "self_test": st, "wire_status": "MEASUREMENT_ONLY_NO_WIRE"})
    _atomic_json(os.path.join(output_dir, "metrics.json"), out)
    print(json.dumps({k: out[k] for k in ("verdict", "verdict_msg", "primary_verdict",
                                          "secondary_verdict", "blockers", "elapsed_s")}, indent=2),
          flush=True)


if __name__ == "__main__":
    _OUT = _output_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                       # NOT BaseException
        for _m in ("smoke", "full"):
            _d = _output_dir(_m)
            if os.path.isdir(_d):
                _write_crash_metrics(_d, _e)
        raise
