"""exp_readout_sign_cue_overlap_curve_v1 -- IS THE TERMINAL sign() FREE AT AN EXACT KEY AND
EXPENSIVE UNDER A PARTIAL CUE, ON THE *REAL* OPEN-VOCABULARY READ-OUT?

PRE-REG: preregs/2026-08-16_exp_readout_sign_cue_overlap_curve_v1.md, written BEFORE this ran.
Every arm, floor, band, gate and brain-fidelity tag is frozen there.

THE PREMISE WAS CHECKED BY RUNTIME OBSERVATION FIRST (PLAN R12), not by grep. numpy.sign was
monkeypatched with a caller-frame recorder and the REAL C3 harness driven end to end
(tools/audit_readout_sign_sites.py). Under the LIVE default HD_GRADED_COMPARATOR=1 the C3
open-vocabulary read-out reaches ZERO sign() calls; under =0 it reaches four switch-aware sites
(grounding_acquisition_loop.py:160, reading_grounding_loop.py:506, :520, :806). ONE site is
SWITCH-BLIND and fires under both: canonicalize() at reading_grounding_loop.py:757, which is on
the live grounding path (:1273 in _make_grounding_gate.gate, :1492 in checkpoint) and which
disagrees with canonicalize_fast on 37.0% of items under the live default. The prior null
(exp_graded_path_vs_orthographic_floor_v1, +0.0015 CI [-0.0055,+0.0083]) flipped the SWITCH, so it
covers the switch-aware sites at the EXACT-KEY point ONLY and does not cover :757 at all. This
cell's GS arm (graded field, SIGNED query) IS the :757 configuration.

WHAT IS MEASURED: the real read-out (C3 B5_OPEN_REAL), unchanged -- open-vocabulary argmax over
5491 anchors, n=4000 items, WordNet gold, identical scorer/n/pool/gold across every arm. Reported:
open-vocabulary hit@1, fraction of gold in the top 50, median rank. NO 2AFC proxy.

ARITHMETIC NOTE, and it is load-bearing. Scores are computed as `M[sel] @ q / (Mn[sel] * qn)` --
the landed cells' OWN expression, fancy-indexed by the eligibility mask. The obvious speed-up
(full-field matvec then mask) was WRITTEN, TESTED AND REJECTED: ST2 measured it diverging from the
reference at up to 1.110e-16 on 24 of 25 fixture trials, because BLAS row-blocking depends on the
row count. That is enough to move an argmax and would have put the bit-exact reproduction gates
PV1/PV2/PV3 out of reach. The row copy is instead amortised by scoring ITEM-MAJOR: every arm
sharing a field and an eligibility rule reuses one copy per item.

REUSES the harness, does not reinvent it: corpus/buckets/space/items/gold come from
experiments/exp_grounding_readout_known_answer_v1.py; the trigram floor from
experiments/exp_meaning_supply_separation_v1.py. NOTHING under hdlab/ is modified.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace; SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-SEGMENT checkpoint via tools/exp_checkpoint with a CONFIG FINGERPRINT in every key
#   (tools/exp_checkpoint.py's own collision defect is UNFIXED -- PLAN item 2), sorted(set()) resume
# - arms-must-differ: sha256 digest over each arm's hit vector; only pre-declared endpoint
#   identities are permitted collisions
# - floors are ARMS, not assertions; each is a STANDALONE channel, never an ablation
# - known-answer arm and null arm fail INDEPENDENTLY
# - progress_logging: flushed progress lines throughout (the run exceeds 1800 s)
ASCII-only. No external LLM (asserted at runtime over sys.modules).

Run:  .venv/Scripts/python.exe experiments/exp_readout_sign_cue_overlap_curve_v1.py
        [--smoke | --self-test]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("HD_GRADED_COMPARATOR", "1")

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

import hdlab.reading_grounding_loop as RGL  # noqa: E402
from hdlab.reading_grounding_loop import CTX_D, ConceptSpace, normalize_lemma  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_readout_sign_cue_overlap_curve_v1"
PREREG_PATH = "preregs/2026-08-16_exp_readout_sign_cue_overlap_curve_v1.md"

MASTER_SEED = C3.MASTER_SEED           # 20260814
N_BOOT = 5000
F_LEVELS = (1.00, 0.80, 0.50, 0.20, 0.00)
CONVENTIONS = ("GG", "SS", "GS", "SG")   # (field, query): G=graded, S=signed
SMOKE_MAX_ITEMS = 300
CHUNK = 500
SELF_RETRIEVAL_FLOOR = 0.70
K_SELF_MIN = 0.99

# LANDED REPRODUCTION TARGETS (PV1/PV2/PV3), each read off a committed metrics.json:
#   0.0480 = data/exp_grounding_readout_known_answer_v1 B5_OPEN_REAL (== A1_BASE == A1_GRADED_ON)
#   0.0465 = data/exp_graded_path_vs_orthographic_floor_v1 A9_GRADED_OFF
#   0.0870 = data/exp_orthographic_floor_vet_v1 A6_TRIGRAM_ONLY (== A5_STRINGCTRL)
REPRO_GG = 0.0480
REPRO_SS = 0.0465
REPRO_ORTHO = 0.0870
REPRO_TOL = 1e-9


# ------------------------------------------------------------------ plumbing
def _out_dir(smoke: bool) -> str:
    p = os.path.join(_REPO, "data", ANCHOR_NAME + ("_smoke" if smoke else ""))
    os.makedirs(p, exist_ok=True)
    return p


def _config_fp(run_mode: str, n_items: int) -> str:
    """tools/exp_checkpoint.unit_key is caller-composed with NO config discriminator (PLAN item 2,
    UNFIXED). Every key this cell writes carries this fingerprint, so a smoke partial can never be
    reloaded by a full."""
    payload = json.dumps({"cell": ANCHOR_NAME, "run_mode": run_mode, "d": CTX_D,
                          "f_levels": list(F_LEVELS), "conventions": list(CONVENTIONS),
                          "n_items": n_items, "seed": MASTER_SEED, "chunk": CHUNK,
                          "record_schema": "picks_v3_multidonor"},
                         sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v).astype(np.int8).tobytes()).hexdigest()[:16]


def _pick_digest(v: np.ndarray) -> str:
    """AMENDMENT A1 (dated 2026-08-16, TIGHTENS). The arms-must-differ gate digests the PICK
    vector, not the hit vector: at a ~5% hit rate a correctness vector cannot distinguish two arms
    that make entirely DIFFERENT wrong picks, and the smoke run proved it collides 16 arms."""
    return hashlib.sha256(np.asarray(v).astype(np.int32).tobytes()).hexdigest()[:16]


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(json.dumps(obj, indent=1).encode("utf-8"))
    os.replace(tmp, path)


def _no_external_llm() -> dict:
    """PV11. A runtime assertion over sys.modules, not an inspection of the source."""
    banned = ("openai", "anthropic", "cohere", "google.generativeai", "mistralai", "ollama",
              "litellm", "llama_cpp", "vllm")
    hit = sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))
    assert not hit, "EXTERNAL LLM MODULE ON THE RUNTIME PATH: %r" % hit
    return {"banned_checked": list(banned), "found": hit, "ok": True}


# ------------------------------------------------------------------ scoring core
def _gold_positions_in_sel(sel: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Positions within `sel` of the gold anchors that survived eligibility. `sel` is ascending."""
    if g.size == 0 or sel.size == 0:
        return np.zeros(0, dtype=np.int64)
    p = np.searchsorted(sel, g)
    p = np.clip(p, 0, sel.size - 1)
    return p[sel[p] == g]


def _score_one(Msel: np.ndarray, Mnsel: np.ndarray, sel: np.ndarray, q: np.ndarray, qn: float,
               g: np.ndarray, gsel: np.ndarray, mode: str,
               self_pos: int) -> Tuple[bool, int, bool, int]:
    """The landed cells' OWN expression, unchanged: `M[sel] @ q / (Mn[sel] * qn)`."""
    sc = (Msel @ q) / (Mnsel * qn)
    b = int(np.argmax(sc))
    pick = int(sel[b])
    if mode == "self":
        return (pick == self_pos), 0, False, pick
    hit = bool(g.size and bool(np.any(g == pick)))
    if gsel.size:
        bg = float(np.max(sc[gsel]))
        rank = int(np.count_nonzero(sc > bg)) + 1
        return hit, rank, rank <= 50, pick
    return hit, int(sel.size), False, pick


def score_all(n: int, fieldspecs: Dict[str, tuple], armspecs: List[dict],
              excl: List[np.ndarray], gold_idx: List[np.ndarray], self_pos: List[int],
              lo: int, hi: int, t0: float) -> Dict[str, dict]:
    """ITEM-MAJOR scoring over items [lo, hi). Every arm sharing a (field, eligibility rule)
    reuses ONE `M[sel]` copy per item, which is what makes the exact arithmetic affordable."""
    res = {a["name"]: {"hits": np.zeros(hi - lo, dtype=bool),
                       "ranks": np.zeros(hi - lo, dtype=np.int64),
                       "top50": np.zeros(hi - lo, dtype=bool),
                       "picks": np.full(hi - lo, -1, dtype=np.int32)} for a in armspecs}
    groups: Dict[Tuple[str, bool], List[dict]] = defaultdict(list)
    for a in armspecs:
        groups[(a["field"], a["exclude"])].append(a)
    cache_noexcl: Dict[str, tuple] = {}
    for i in range(lo, hi):
        r = i - lo
        for (fname, doexcl), arms in sorted(groups.items()):
            M, Mn, ok = fieldspecs[fname]
            if doexcl:
                keep = ok.copy()
                keep[excl[i]] = False
                sel = np.flatnonzero(keep)
                if sel.size == 0:
                    continue
                Msel, Mnsel = M[sel], Mn[sel]
            else:
                if fname not in cache_noexcl:
                    s = np.flatnonzero(ok)
                    cache_noexcl[fname] = (s, M[s], Mn[s])
                sel, Msel, Mnsel = cache_noexcl[fname]
                if sel.size == 0:
                    continue
            g = gold_idx[i]
            gsel = _gold_positions_in_sel(sel, g)
            for a in arms:
                if not a["live"][i]:
                    continue
                qn = float(a["Qn"][i])
                if qn < 1e-9:
                    continue
                h, rk, t5, pk = _score_one(Msel, Mnsel, sel, a["Q"][i], qn, g, gsel, a["mode"],
                                           self_pos[i])
                res[a["name"]]["hits"][r] = h
                res[a["name"]]["ranks"][r] = rk
                res[a["name"]]["top50"][r] = t5
                res[a["name"]]["picks"][r] = pk
        if (i + 1 - lo) % 100 == 0:
            print("[score] item %d/%d (chunk %d-%d) elapsed=%.1fs"
                  % (i + 1, n, lo, hi, time.time() - t0), flush=True)
    return res


def _landed_reference_score_space(anchors: List[str], pos: Dict[str, int], mat: np.ndarray,
                                  mat_nrm: np.ndarray, mat_ok: np.ndarray, norm2idx,
                                  items: List[dict], gold_fn):
    """A LITERAL transcription of exp_graded_path_vs_orthographic_floor_v1._score_space, kept
    ONLY as the ST2 reference. If this and score_all ever disagree, score_all is wrong."""
    n = len(items)
    hits = np.zeros(n, dtype=bool)
    ranks = np.zeros(n, dtype=np.int64)
    top50 = np.zeros(n, dtype=bool)
    anchor_arr = np.array(anchors)
    for i, it in enumerate(items):
        L = it["L"]
        gold = gold_fn(L)
        elig = mat_ok.copy()
        for k in sorted(set(norm2idx[normalize_lemma(L)] + ([pos[L]] if L in pos else []))):
            elig[k] = False
        sel = np.flatnonzero(elig)
        if sel.size == 0 or L not in pos:
            continue
        gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)
        q = mat[pos[L]]
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        sc = (mat[sel] @ q) / (mat_nrm[sel] * qn)
        b = int(np.argmax(sc))
        hits[i] = str(anchor_arr[sel[b]]) in gold
        if gsel.size:
            bg = float(np.max(sc[gsel]))
            ranks[i] = int(np.sum(sc > bg)) + 1
            top50[i] = ranks[i] <= 50
        else:
            ranks[i] = sel.size
    return hits, ranks, top50


# ------------------------------------------------------------------ bootstrap
def shared_bootstrap(arms: Dict[str, np.ndarray], contrasts: Sequence[Tuple[str, str, str]],
                     dids: Sequence[Tuple[str, str, str, str, str]], n_boot: int,
                     seed: int) -> dict:
    """ONE set of resample indices shared by EVERY arm, so any contrast -- including a
    difference-in-differences across two cue levels -- is paired."""
    keys = sorted(arms)
    mat = np.stack([arms[k].astype(np.float64) for k in keys], axis=0)
    n = mat.shape[1]
    rng = np.random.default_rng(seed)
    boot = np.empty((n_boot, len(keys)), dtype=np.float64)
    done = 0
    while done < n_boot:
        m = min(50, n_boot - done)
        idx = rng.integers(0, n, size=(m, n))
        boot[done:done + m] = mat[:, idx].mean(axis=2).T
        done += m
    out = {"n_boot": n_boot, "seed": seed, "n_items": int(n), "arm_acc_ci": {}, "deltas": {},
           "did": {}}
    for j, k in enumerate(keys):
        lo, hi = np.percentile(boot[:, j], [2.5, 97.5])
        out["arm_acc_ci"][k] = {"acc": float(mat[j].mean()), "ci_lo": float(lo),
                                "ci_hi": float(hi), "sd": float(boot[:, j].std())}
    ki = {k: j for j, k in enumerate(keys)}
    for name, a, b in contrasts:
        if a not in ki or b not in ki:
            continue
        d = boot[:, ki[a]] - boot[:, ki[b]]
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["deltas"][name] = {"delta": float(mat[ki[a]].mean() - mat[ki[b]].mean()),
                               "ci_lo": float(lo), "ci_hi": float(hi), "sd": float(d.std()),
                               "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0)}
    for name, a, b, c, e in dids:
        if any(x not in ki for x in (a, b, c, e)):
            continue
        d = (boot[:, ki[a]] - boot[:, ki[b]]) - (boot[:, ki[c]] - boot[:, ki[e]])
        lo, hi = np.percentile(d, [2.5, 97.5])
        point = float((mat[ki[a]].mean() - mat[ki[b]].mean())
                      - (mat[ki[c]].mean() - mat[ki[e]].mean()))
        out["did"][name] = {"did": point, "ci_lo": float(lo), "ci_hi": float(hi),
                            "sd": float(d.std()), "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0)}
    return out


# ------------------------------------------------------------------ space + cue models
def build_space_and_cues(sents: List[str], buckets: Dict[str, List[int]]
                         ) -> Tuple[ConceptSpace, List[str], Dict[float, np.ndarray],
                                    Dict[str, int], np.ndarray]:
    """Replicates C3.build_space EXACTLY (same lemma order, same sentence order, same
    context_vector_masked calls, so the ConceptSpace is bit-identical to C3's) and, in the SAME
    pass, accumulates MODEL B's nested evidence-subsample sums.

    MODEL B: for a lemma with n_p profile sentences, a per-lemma permutation selects a NESTED
    subset of ceil(f*n_p); the subset is summed in INCREASING ORIGINAL ORDER, so f=1.00 is
    BIT-IDENTICAL to ConceptSpace's own insertion-order sum (asserted below and in ST3)."""
    sp = ConceptSpace(d=CTX_D)
    lemmas = sorted(buckets)
    pos = {w: i for i, w in enumerate(lemmas)}
    subs = {f: np.zeros((len(lemmas), CTX_D), dtype=np.float64) for f in F_LEVELS if f > 0.0}
    n_obs = np.zeros(len(lemmas), dtype=np.int64)
    t0 = time.time()
    for k, w in enumerate(lemmas):
        idxs = buckets[w][:C3._n_profile(len(buckets[w]))]
        n_p = len(idxs)
        n_obs[pos[w]] = n_p
        perm = np.random.default_rng(C3._seed_for("cueB|" + w)).permutation(n_p)
        keep = {}
        for f in F_LEVELS:
            if f > 0.0:
                keep[f] = set(int(x) for x in perm[:max(1, int(math.ceil(f * n_p)))])
        for j, i in enumerate(idxs):
            cv = RGL.context_vector_masked(sents[i], w)
            sp.observe(w, cv)
            for f, s in keep.items():
                if j in s:
                    subs[f][pos[w]] += cv
        if k % 500 == 0 or k == len(lemmas) - 1:
            print("[space] %d/%d lemmas elapsed=%.1fs" % (k + 1, len(lemmas), time.time() - t0),
                  flush=True)
    anchors = sorted(sp.anchors())
    assert anchors == lemmas, "anchor order drifted from the buckets order"
    bad = [w for w in lemmas if not np.array_equal(subs[1.0][pos[w]], sp.bundle(w))]
    assert not bad, ("MODEL B f=1.00 is NOT bit-identical to ConceptSpace's own sum for %d lemmas "
                     "(first: %r)" % (len(bad), bad[:3]))
    return sp, anchors, subs, pos, n_obs


# ------------------------------------------------------------------ self-tests
def _st_signed_matches_switch() -> dict:
    """ST1 / PV10. np.sign(mat) and np.sign(bundle) must be BIT-IDENTICAL to what the REAL
    ConceptSpace methods return when GRADED_COMPARATOR is False. The module constant is
    monkeypatched, not the environment (which is inert after import)."""
    sp = ConceptSpace(d=16)
    rng = np.random.default_rng(0)
    for w in ("alpha", "beta", "gamma"):
        for _ in range(5):
            sp.observe(w, rng.normal(size=16))
    an_g, mat_g = sp.anchor_matrix()
    q_g = sp.bundle("alpha")
    local_mat, local_q = np.sign(mat_g), np.sign(q_g)
    prior = RGL.GRADED_COMPARATOR
    RGL.GRADED_COMPARATOR = False
    sp._mat_cache = None
    try:
        an_s, mat_s = sp.anchor_matrix()
        q_s = sp.bundle("alpha")
    finally:
        RGL.GRADED_COMPARATOR = prior
        sp._mat_cache = None
    assert np.array_equal(mat_s, local_mat), "signed FIELD diverges from the real OFF path"
    assert np.array_equal(q_s, local_q), "signed QUERY diverges from the real OFF path"
    assert an_s == an_g
    return {"ok": True, "n_anchors": len(an_g)}


def _st_full_matvec_shortcut_is_rejected() -> dict:
    """ST2a. RECORD, do not assume: the full-field matvec shortcut is NOT bit-identical to the
    landed `M[sel] @ q`, because BLAS row-blocking depends on the row count. This is why the cell
    pays for the row copy. A measured reason, not a stylistic one."""
    rng = np.random.default_rng(11)
    M = rng.normal(size=(900, CTX_D))
    M[7] = 0.0
    Mn = np.linalg.norm(M, axis=1)
    ok = Mn >= 1e-9
    n_exact, worst = 0, 0.0
    for t in range(25):
        q = rng.normal(size=CTX_D) * (t + 1)
        keep = ok.copy()
        keep[rng.integers(0, 900, size=5)] = False
        sel = np.flatnonzero(keep)
        qn = float(np.linalg.norm(q))
        ref = (M[sel] @ q) / (Mn[sel] * qn)
        with np.errstate(invalid="ignore", divide="ignore"):
            full = ((M @ q) / (Mn * qn))[sel]
        n_exact += int(np.array_equal(ref, full))
        worst = max(worst, float(np.max(np.abs(ref - full))))
    assert n_exact < 25, ("the shortcut is bit-identical after all -- this ST is stale and the "
                          "cell could be sped up")
    return {"trials": 25, "shortcut_bit_identical": n_exact, "worst_abs_diff": worst,
            "conclusion": "shortcut REJECTED; the cell uses M[sel] @ q, the landed expression"}


def _st_score_all_matches_landed_reference() -> dict:
    """ST2b. score_all must reproduce a LITERAL transcription of the landed
    exp_graded_path_vs_orthographic_floor_v1._score_space -- hits, ranks and top50, bit-identical
    -- on a real ConceptSpace built from real sentences. This is what licenses every number."""
    sents = ["The poet wrote verses and published a book of poems every winter here.",
             "A famous poet read verses aloud at the library and the school today.",
             "The river flows through the valley and past the bridge each spring here.",
             "Boats travel along the river between the town and the sea today.",
             "The writer published a book about the valley and the river last winter.",
             "A book of poems about boats and the sea was read at the school."]
    sp = ConceptSpace(d=CTX_D)
    words = ["poet", "river", "book", "valley", "sea", "school", "boat", "verse"]
    for w in words:
        for s in sents:
            sp.observe(w, RGL.context_vector_masked(s, w))
    anchors, mat = sp.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    mn = np.linalg.norm(mat, axis=1)
    ok = mn >= 1e-9
    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    items = [{"L": a} for a in anchors]
    gold_fn = C3.gold_meaning_set
    r_hits, r_ranks, r_t50 = _landed_reference_score_space(anchors, pos, mat, mn, ok, norm2idx,
                                                           items, gold_fn)
    excl = [np.array(sorted(set(norm2idx[normalize_lemma(it["L"])] + [pos[it["L"]]])),
                     dtype=np.int64) for it in items]
    gold_idx = [np.array(sorted(pos[g] for g in gold_fn(it["L"]) if g in pos), dtype=np.int64)
                for it in items]
    Q = np.stack([mat[pos[it["L"]]] for it in items], axis=0)
    arm = [{"name": "T", "field": "G", "Q": Q, "Qn": np.linalg.norm(Q, axis=1),
            "live": np.ones(len(items), dtype=bool), "exclude": True, "mode": "gold"}]
    got = score_all(len(items), {"G": (mat, mn, ok)}, arm, excl, gold_idx,
                    [pos[it["L"]] for it in items], 0, len(items), time.time())["T"]
    assert np.array_equal(got["hits"], r_hits), "score_all hits diverge from the landed reference"
    assert np.array_equal(got["ranks"], r_ranks), "score_all ranks diverge from the reference"
    assert np.array_equal(got["top50"], r_t50), "score_all top50 diverges from the reference"
    return {"n_anchors": len(anchors), "n_items": len(items), "hits": int(r_hits.sum()),
            "bit_identical_to_landed_reference": True}


def _st_sign_selection_commute() -> dict:
    """ST4. Elementwise selection and sign() COMMUTE, so MODEL A's mix-then-sign vs sign-then-mix
    ordering is not a free choice and cannot be a confound. Asserted, not argued."""
    rng = np.random.default_rng(5)
    a, b = rng.normal(size=512), rng.normal(size=512)
    m = rng.random(512) < 0.4
    assert np.array_equal(np.sign(np.where(m, a, b)), np.where(m, np.sign(a), np.sign(b))), \
        "sign() and elementwise selection do not commute"
    return {"ok": True}


def _st_cue_models() -> dict:
    """ST3. MODEL A: f=1.00 returns the target EXACTLY, f=0.00 the donor EXACTLY, and the measured
    cos(q_f, q_1.00) is STRICTLY DECREASING. MODEL B: a subset sum over the full index set is
    BIT-IDENTICAL to ConceptSpace's own insertion-order sum."""
    rng = np.random.default_rng(3)
    tgt, don = rng.normal(size=CTX_D), rng.normal(size=CTX_D)
    dperm = np.random.default_rng(9).permutation(CTX_D)
    coss = []
    for f in F_LEVELS:
        m = np.zeros(CTX_D, dtype=bool)
        m[dperm[:int(math.ceil(f * CTX_D))]] = True
        q = np.where(m, tgt, don)
        if f == 1.0:
            assert np.array_equal(q, tgt), "MODEL A f=1.00 is not the target vector"
        if f == 0.0:
            assert np.array_equal(q, don), "MODEL A f=0.00 is not the donor vector"
        coss.append(float(np.dot(q, tgt) / (np.linalg.norm(q) * np.linalg.norm(tgt))))
    assert all(coss[i] > coss[i + 1] for i in range(len(coss) - 1)), \
        "MODEL A cue axis is not strictly decreasing: %r" % coss
    sp = ConceptSpace(d=32)
    rng2 = np.random.default_rng(4)
    cvs = [rng2.normal(size=32) for _ in range(9)]
    acc = np.zeros(32)
    for cv in cvs:
        sp.observe("w", cv)
        acc += cv
    assert np.array_equal(acc, sp.bundle("w")), \
        "MODEL B f=1.00 subset sum is NOT bit-identical to ConceptSpace's own sum"
    return {"modelA_cos_by_f": dict(zip(["%.2f" % f for f in F_LEVELS], coss)),
            "modelB_exact": True}


def _st_bootstrap() -> dict:
    """ST9. The bootstrap detects a real delta and does not manufacture one."""
    rng = np.random.default_rng(3)
    base = (rng.random(400) < 0.50).astype(float)
    better = np.maximum(base, (rng.random(400) < 0.30).astype(float))
    bs = shared_bootstrap({"A": better, "B": base}, [("d", "A", "B")], [], 400, 7)
    assert bs["deltas"]["d"]["ci_excludes_zero"], "bootstrap missed a real delta"
    fp = 0
    for s in range(6):
        r2 = np.random.default_rng(1000 + s)
        null = {"A": (r2.random(800) < 0.5).astype(float),
                "B": (r2.random(800) < 0.5).astype(float)}
        if shared_bootstrap(null, [("d", "A", "B")], [], 400, 7)["deltas"]["d"]["ci_excludes_zero"]:
            fp += 1
    assert fp <= 1, "bootstrap false-positive rate too high: %d/6" % fp
    return {"real_delta_detected": True, "null_false_positives": fp}


def _st_did_detects_interaction() -> dict:
    """ST9b. The difference-in-differences -- the cell's PRIMARY discriminator -- must FIRE on a
    planted interaction and must NOT fire when the two gaps are equal. A discriminator that cannot
    do both is not a discriminator."""
    rng = np.random.default_rng(21)
    n = 4000
    a_hi = (rng.random(n) < 0.30).astype(float)
    b_hi = (rng.random(n) < 0.20).astype(float)
    a_lo = (rng.random(n) < 0.30).astype(float)
    b_lo = (rng.random(n) < 0.30).astype(float)
    bs = shared_bootstrap({"AH": a_hi, "BH": b_hi, "AL": a_lo, "BL": b_lo}, [],
                          [("did", "AH", "BH", "AL", "BL")], 1000, 5)
    assert bs["did"]["did"]["ci_excludes_zero"] and bs["did"]["did"]["did"] > 0, \
        "DiD missed a planted interaction: %r" % bs["did"]["did"]
    bs2 = shared_bootstrap({"AH": a_hi, "BH": b_hi, "AL": a_hi.copy(), "BL": b_hi.copy()}, [],
                           [("did", "AH", "BH", "AL", "BL")], 1000, 5)
    assert not bs2["did"]["did"]["ci_excludes_zero"], \
        "DiD fired on two IDENTICAL gaps: %r" % bs2["did"]["did"]
    return {"planted_did": bs["did"]["did"]["did"], "planted_fires": True,
            "flat_did": bs2["did"]["did"]["did"], "flat_fires": False}


def _st_arms_must_differ_detects() -> dict:
    """ST7. The collision detector must actually fire on a deliberate duplicate."""
    a = np.array([1, 0, 1, 1], dtype=bool)
    d = {"X": _digest(a), "Y": _digest(a.copy()), "Z": _digest(~a)}
    groups = defaultdict(list)
    for k, v in d.items():
        groups[v].append(k)
    coll = {v: sorted(ks) for v, ks in groups.items() if len(ks) > 1}
    assert coll and sorted(list(coll.values())[0]) == ["X", "Y"], "collision detector is blind"
    return {"ok": True}


def _st_canonicalize_is_switch_blind() -> dict:
    """ST10. Bakes the runtime enumeration into the cell: under the LIVE graded default,
    canonicalize() (reading_grounding_loop.py:757) STILL calls np.sign on the query while
    canonicalize_fast() does NOT. Measured by monkeypatching np.sign, not by reading the source."""
    assert RGL.GRADED_COMPARATOR is True, "this self-test assumes the live graded default"
    sp = ConceptSpace(d=32)
    rng = np.random.default_rng(2)
    for w in ("alpha", "beta", "gamma"):
        for _ in range(4):
            sp.observe(w, rng.normal(size=32))
    q = sp.bundle("alpha") + rng.normal(size=32) * 0.01
    counts = {"n": 0}
    real = np.sign

    def traced(x, *a, **k):
        counts["n"] += 1
        return real(x, *a, **k)

    RGL.np.sign = traced
    try:
        counts["n"] = 0
        RGL.canonicalize_fast("zz", q, sp, thresh=-1.0)
        n_fast = counts["n"]
        counts["n"] = 0
        RGL.canonicalize("zz", q, sp, thresh=-1.0)
        n_slow = counts["n"]
    finally:
        RGL.np.sign = real
    assert n_fast == 0, "canonicalize_fast signed the query under the graded default (%d)" % n_fast
    assert n_slow >= 1, "canonicalize did NOT sign the query -- the :757 site has changed"
    return {"sign_calls_canonicalize_fast": n_fast, "sign_calls_canonicalize": n_slow,
            "site": "hdlab/reading_grounding_loop.py:757",
            "reading": "canonicalize is SWITCH-BLIND and is on the live grounding path "
                       "(:1273 _make_grounding_gate.gate, :1492 checkpoint)"}


def _st_gold_set() -> dict:
    """ST5. The gold standard fires where it must and not where it must not (C3's own asserts)."""
    g = C3.gold_meaning_set("dog")
    assert "canine" in g and "puppy" in g and "democracy" not in g and "dog" not in g
    return {"n_gold_dog": len(g), "ok": True}


def self_test() -> int:
    t0 = time.time()
    res = {
        "ST1_signed_matches_real_switch": _st_signed_matches_switch(),
        "ST2a_full_matvec_shortcut_rejected": _st_full_matvec_shortcut_is_rejected(),
        "ST2b_score_all_matches_landed_reference": _st_score_all_matches_landed_reference(),
        "ST3_cue_models": _st_cue_models(),
        "ST4_sign_selection_commute": _st_sign_selection_commute(),
        "ST5_gold_set": _st_gold_set(),
        "ST6_no_external_llm": _no_external_llm(),
        "ST7_arms_must_differ_detects": _st_arms_must_differ_detects(),
        "ST9_bootstrap": _st_bootstrap(),
        "ST9b_did_detects_interaction": _st_did_detects_interaction(),
        "ST10_canonicalize_is_switch_blind": _st_canonicalize_is_switch_blind(),
    }
    res["elapsed_s"] = round(time.time() - t0, 3)
    print(json.dumps(res, indent=1), flush=True)
    print("ALL SELF-TESTS PASSED", flush=True)
    return 0


# ------------------------------------------------------------------ the run
def run(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    smoke = run_mode == "smoke"
    _no_external_llm()
    assert RGL.GRADED_COMPARATOR is True, (
        "GRADED_COMPARATOR is False at import -- the live default has changed and the GG arm would "
        "no longer BE the live read-out. STOP.")

    sents = C3.build_corpus("smoke" if smoke else "full")
    print("[corpus] n_sentences=%d elapsed=%.1fs" % (len(sents), time.time() - t0), flush=True)
    buckets, counts = C3.build_buckets(sents)
    space, anchors, subs, apos, n_obs = build_space_and_cues(sents, buckets)
    n_anchors = len(anchors)
    items, item_diag = C3.build_items(space, buckets, counts,
                                      SMOKE_MAX_ITEMS if smoke else C3.MAX_ITEMS)
    n = len(items)
    cfp = _config_fp(run_mode, n)
    print("[build] n_items=%d n_anchors=%d config_fp=%s elapsed=%.1fs"
          % (n, n_anchors, cfp, time.time() - t0), flush=True)

    _an, mat_G = space.anchor_matrix()
    assert _an == anchors
    mat_S = np.sign(mat_G)

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(apos[a])
    excl = [np.array(sorted(set(norm2idx[normalize_lemma(it["L"])] + [apos[it["L"]]])),
                     dtype=np.int64) for it in items]
    gold_sets = [C3.gold_meaning_set(it["L"]) for it in items]
    gold_idx = [np.array(sorted(apos[g] for g in gs if g in apos), dtype=np.int64)
                for gs in gold_sets]
    self_pos = [apos[it["L"]] for it in items]
    gold_base_rate = float(np.mean([g.size / max(1, n_anchors) for g in gold_idx]))

    # ---- cue construction -------------------------------------------------------------------
    donor = np.random.default_rng(MASTER_SEED + 21).permutation(n)   # matches the landed floor
    B_L = np.stack([mat_G[apos[it["L"]]] for it in items], axis=0)
    B_D = np.stack([mat_G[apos[items[int(donor[i])]["L"]]] for i in range(n)], axis=0)

    # AMENDMENT A5: each substituted DIMENSION takes its value from an INDEPENDENTLY drawn anchor
    # (never the target or its normalized-lemma siblings), so the non-target part of the cue is
    # incoherent noise instead of ONE coherent competitor whose own anchor row is an exact match.
    # The smoke run proved the single-donor construction degenerate: the signed arms returned the
    # donor on 300/300 items at f=0.20 and f=0.50. Fixed per (item, dimension) so the curve nests.
    rng_dim = np.random.default_rng(MASTER_SEED + 33)
    dim_perm = np.stack([rng_dim.permutation(CTX_D) for _ in range(n)], axis=0)
    rng_src = np.random.default_rng(MASTER_SEED + 55)
    src = rng_src.integers(0, n_anchors, size=(n, CTX_D))
    for i in range(n):
        bad = np.isin(src[i], excl[i])
        while bad.any():
            src[i, bad] = rng_src.integers(0, n_anchors, size=int(bad.sum()))
            bad = np.isin(src[i], excl[i])
    MIX = mat_G[src, np.arange(CTX_D)[None, :]]
    assert MIX.shape == (n, CTX_D)

    QRAW: Dict[Tuple[str, float], np.ndarray] = {}
    for f in F_LEVELS:
        k = int(math.ceil(f * CTX_D))
        m = np.zeros((n, CTX_D), dtype=bool)
        for i in range(n):
            m[i, dim_perm[i, :k]] = True
        QRAW[("MA", f)] = np.where(m, B_L, MIX)
        QRAW[("MB", f)] = MIX.copy() if f <= 0.0 else \
            np.stack([subs[f][apos[it["L"]]] for it in items], axis=0)
    assert np.array_equal(QRAW[("MA", 1.0)], B_L), "MODEL A f=1.00 is not the exact key"
    assert np.array_equal(QRAW[("MB", 1.0)], B_L), "MODEL B f=1.00 is not the exact key"
    assert np.array_equal(QRAW[("MA", 0.0)], MIX) and np.array_equal(QRAW[("MB", 0.0)], MIX)

    def _mean_cos(Q: np.ndarray) -> float:
        a = np.einsum("ij,ij->i", Q, B_L)
        d = np.linalg.norm(Q, axis=1) * np.linalg.norm(B_L, axis=1)
        good = d >= 1e-12
        return float(np.mean(a[good] / d[good]))

    cue_axis = {"MODEL_A": {("%.2f" % f): _mean_cos(QRAW[("MA", f)]) for f in F_LEVELS},
                "MODEL_B": {("%.2f" % f): _mean_cos(QRAW[("MB", f)]) for f in F_LEVELS}}
    print("[cue-axis] %s" % json.dumps(cue_axis), flush=True)

    # ---- fields ------------------------------------------------------------------------------
    t_mat, t_cov = MS.trigram_matrix(anchors)
    rng_null = np.random.default_rng(MASTER_SEED + 77)
    mat_N = np.zeros_like(mat_G)
    for j in range(n_anchors):
        mat_N[j] = rng_null.choice([-1.0, 1.0],
                                   size=(int(max(1, n_obs[j])), CTX_D)).sum(axis=0)
    mat_NS = np.sign(mat_N)
    fieldspecs = {}
    for nm, M in (("G", mat_G), ("S", mat_S), ("N", mat_N), ("NS", mat_NS)):
        nrm = np.linalg.norm(M, axis=1)
        fieldspecs[nm] = (M, nrm, nrm >= 1e-9)
    fieldspecs["T"] = (t_mat, np.ones(n_anchors, dtype=np.float64), t_cov.copy())

    # ---- held-out-sentence cue (what production actually has at question time)
    Q_H = np.zeros((n, CTX_D), dtype=np.float64)
    for i, it in enumerate(items):
        if it["sent_idx"] is not None:
            Q_H[i] = RGL.context_vector_masked(sents[it["sent_idx"]], it["L"])
    live_H = np.array([it["sent_idx"] is not None for it in items], dtype=bool) \
        & (np.linalg.norm(Q_H, axis=1) >= 1e-9)

    # ---- the arm table -----------------------------------------------------------------------
    live_all = np.ones(n, dtype=bool)
    live_T = np.array([bool(t_cov[apos[it["L"]]]) for it in items], dtype=bool)
    armspecs: List[dict] = []

    def _add(name: str, field: str, Q: np.ndarray, live: np.ndarray, exclude: bool = True,
             mode: str = "gold", note: str = "") -> None:
        armspecs.append({"name": name, "field": field, "Q": Q,
                         "Qn": np.linalg.norm(Q, axis=1), "live": live, "exclude": exclude,
                         "mode": mode, "note": note})

    for model in ("MA", "MB"):
        for f in F_LEVELS:
            tag = "%s_f%03d" % (model, int(round(f * 100)))
            Qg = QRAW[(model, f)]
            Qs = np.sign(Qg)
            _add(tag + "_GG", "G", Qg, live_all, note="LIVE default: graded field, graded query")
            _add(tag + "_SS", "S", Qs, live_all, note="pre-2026-08-14 convention: signed both")
            _add(tag + "_GS", "G", Qs, live_all,
                 note="THE canonicalize:757 CONFIGURATION -- graded field, SIGNED query")
            _add(tag + "_SG", "S", Qg, live_all, note="signed field, graded query")

    Q_T = np.stack([t_mat[apos[it["L"]]] for it in items], axis=0)
    _add("F_ORTHO", "T", Q_T, live_T, note="FLOOR: character-trigram profile only, ZERO substrate")
    _add("F_SCRAMBLE_G", "G", B_D, live_all,
         note="FLOOR: one donor's whole bundle as the query -- the landed cells' construction")
    _add("F_SCRAMBLE_S", "S", np.sign(B_D), live_all, note="FLOOR: signed donor bundle")
    Q_N = np.stack([mat_N[apos[it["L"]]] for it in items], axis=0)
    _add("N_NULLCONTENT_G", "N", Q_N, live_all, note="NULL: random field, matched obs counts")
    _add("N_NULLCONTENT_S", "NS", np.sign(Q_N), live_all, note="NULL: signed random field")
    for conv in CONVENTIONS:
        _add("H_SENT_" + conv, conv[0], np.sign(Q_H) if conv[1] == "S" else Q_H, live_H,
             note="single HELD-OUT SENTENCE query -- the production cue")
    _add("K_SELF_GG", "G", B_L, live_all, exclude=False, mode="self",
         note="KNOWN-ANSWER: the target's own anchor stays ELIGIBLE")
    _add("K_SELF_SS", "S", np.sign(B_L), live_all, exclude=False, mode="self",
         note="KNOWN-ANSWER, signed convention")

    print("[arms] %d arms, %d groups" % (
        len(armspecs), len({(a["field"], a["exclude"]) for a in armspecs})), flush=True)

    # ---- scoring, per-SEGMENT checkpointed ---------------------------------------------------
    done = completed_units(output_dir)
    prior = load_units(output_dir) if done else {}
    acc = {a["name"]: {"hits": np.zeros(n, dtype=bool), "ranks": np.zeros(n, dtype=np.int64),
                       "top50": np.zeros(n, dtype=bool),
                       "picks": np.full(n, -1, dtype=np.int32)} for a in armspecs}
    for lo in sorted(set(range(0, n, CHUNK))):
        hi = min(lo + CHUNK, n)
        key = unit_key("chunk", cfp, "%06d" % lo)
        if key in done and key in prior:
            r = prior[key]
            print("[resume] chunk %d-%d" % (lo, hi), flush=True)
        else:
            got = score_all(n, fieldspecs, armspecs, excl, gold_idx, self_pos, lo, hi, t0)
            r = {k: {"hits": [int(x) for x in v["hits"]], "ranks": [int(x) for x in v["ranks"]],
                     "top50": [int(x) for x in v["top50"]],
                     "picks": [int(x) for x in v["picks"]]} for k, v in got.items()}
            record_unit(output_dir, key, r)
        for k, v in r.items():
            acc[k]["hits"][lo:hi] = np.array(v["hits"], dtype=bool)
            acc[k]["ranks"][lo:hi] = np.array(v["ranks"], dtype=np.int64)
            acc[k]["top50"][lo:hi] = np.array(v["top50"], dtype=bool)
            acc[k]["picks"][lo:hi] = np.array(v["picks"], dtype=np.int32)
        print("[chunk] %d-%d done elapsed=%.1fs" % (lo, hi, time.time() - t0), flush=True)

    arms_hit: Dict[str, np.ndarray] = {}
    arms_pick: Dict[str, np.ndarray] = {}
    per_arm: Dict[str, dict] = {}
    for a in armspecs:
        nm = a["name"]
        h, rk, t5, lv = acc[nm]["hits"], acc[nm]["ranks"], acc[nm]["top50"], a["live"]
        arms_hit[nm] = h.astype(float)
        arms_pick[nm] = acc[nm]["picks"]
        per_arm[nm] = {"hit_at_1": float(h.mean()),
                       "hit_at_1_on_live_subset": float(h[lv].mean()) if lv.any() else None,
                       "n_live": int(lv.sum()),
                       "median_rank": float(np.median(rk[lv])) if lv.any() else None,
                       "frac_gold_in_top50": float(t5.mean()), "note": a["note"]}
        print("[arm] %-18s hit@1=%.4f top50=%.4f med_rank=%s"
              % (nm, per_arm[nm]["hit_at_1"], per_arm[nm]["frac_gold_in_top50"],
                 per_arm[nm]["median_rank"]), flush=True)

    # ---- frequency floor (a standalone channel, no vector arithmetic at all)
    freq_vec = np.array([counts[a] for a in anchors], dtype=np.float64)
    freq_hits = np.zeros(n, dtype=bool)
    for i in range(n):
        sc = freq_vec.copy()
        sc[excl[i]] = -np.inf
        b = int(np.argmax(sc))
        freq_hits[i] = bool(gold_idx[i].size and bool(np.any(gold_idx[i] == b)))
    arms_hit["F_FREQ"] = freq_hits.astype(float)
    per_arm["F_FREQ"] = {"hit_at_1": float(freq_hits.mean()), "n_live": int(n),
                         "note": "FLOOR: most frequent eligible anchor"}
    print("[arm] F_FREQ hit@1=%.4f | F_SCRAMBLE_G=%.4f F_SCRAMBLE_S=%.4f"
          % (freq_hits.mean(), per_arm["F_SCRAMBLE_G"]["hit_at_1"],
             per_arm["F_SCRAMBLE_S"]["hit_at_1"]), flush=True)

    # ---- 2AFC positive control (the harness's own)
    def _self_retrieval(M: np.ndarray, signed_q: bool, seed: int) -> Tuple[float, int]:
        r = np.random.default_rng(seed)
        hits, m = 0, 0
        for it in items[:min(300, n)]:
            L = it["L"]
            if it["sent_idx"] is None:
                continue
            other = anchors[int(r.integers(n_anchors))]
            tries = 0
            while tries < 20 and (other == L or C3._is_variant(other, L)):
                other = anchors[int(r.integers(n_anchors))]
                tries += 1
            if other == L:
                continue
            q = RGL.context_vector_masked(sents[it["sent_idx"]], L)
            q = np.sign(q) if signed_q else q
            qn = float(np.linalg.norm(q))
            if qn < 1e-9:
                continue
            cv = np.stack([M[apos[L]], M[apos[other]]], axis=0)
            cn = np.linalg.norm(cv, axis=1)
            if not bool((cn >= 1e-9).all()):
                continue
            hits += int(int(np.argmax((cv @ q) / (cn * qn))) == 0)
            m += 1
        return hits / max(1, m), m

    sr_g, sr_ng = _self_retrieval(mat_G, False, MASTER_SEED + 9)
    sr_s, sr_ns = _self_retrieval(mat_S, True, MASTER_SEED + 9)
    print("[positive-control] self-retrieval G=%.4f (n=%d) S=%.4f (n=%d) floor=%.2f"
          % (sr_g, sr_ng, sr_s, sr_ns, SELF_RETRIEVAL_FLOOR), flush=True)

    # ---- bootstrap ---------------------------------------------------------------------------
    contrasts: List[Tuple[str, str, str]] = []
    dids: List[Tuple[str, str, str, str, str]] = []
    for model in ("MA", "MB"):
        for f in F_LEVELS:
            tag = "%s_f%03d" % (model, int(round(f * 100)))
            for pair in ("SS", "GS", "SG"):
                contrasts.append(("d_%s_GG_minus_%s" % (tag, pair), tag + "_GG", tag + "_" + pair))
            for conv in CONVENTIONS:
                for fl in ("F_ORTHO", "F_FREQ", "F_SCRAMBLE_G"):
                    contrasts.append(("d_%s_%s_minus_%s" % (tag, conv, fl), tag + "_" + conv, fl))
        for f in (0.80, 0.50, 0.20, 0.00):
            tag = "%s_f%03d" % (model, int(round(f * 100)))
            for pair in ("SS", "GS", "SG"):
                dids.append(("did_%s_GGminus%s_f%03d_vs_f100" % (model, pair, int(round(f * 100))),
                             tag + "_GG", tag + "_" + pair,
                             "%s_f100_GG" % model, "%s_f100_%s" % (model, pair)))
    for pair in ("SS", "GS", "SG"):
        contrasts.append(("d_H_SENT_GG_minus_%s" % pair, "H_SENT_GG", "H_SENT_" + pair))
    for fl in ("F_ORTHO", "F_FREQ", "F_SCRAMBLE_G"):
        contrasts.append(("d_H_SENT_GG_minus_%s" % fl, "H_SENT_GG", fl))

    print("[bootstrap] n_arms=%d n_contrasts=%d n_did=%d" % (len(arms_hit), len(contrasts),
                                                             len(dids)), flush=True)
    bs = shared_bootstrap(arms_hit, contrasts, dids, N_BOOT, MASTER_SEED + 5)
    print("[bootstrap] done elapsed=%.1fs" % (time.time() - t0), flush=True)

    # ---- PRE-REGISTERED VALIDITY GATES -------------------------------------------------------
    # AMENDMENT A1 (TIGHTENS): the gate digests PICKS. Hit digests are still reported.
    digests = {k: _digest(v.astype(bool)) for k, v in arms_hit.items()}
    pick_digests = {k: _pick_digest(v) for k, v in arms_pick.items()}
    groups = defaultdict(list)
    for k, v in pick_digests.items():
        groups[v].append(k)
    collisions = {v: sorted(ks) for v, ks in groups.items() if len(ks) > 1}
    allowed = set()
    for conv in CONVENTIONS:
        allowed.add(tuple(sorted(["MA_f100_%s" % conv, "MB_f100_%s" % conv])))
        allowed.add(tuple(sorted(["MA_f000_%s" % conv, "MB_f000_%s" % conv])))
    # AMENDMENT A2 (LOOSENS, stated as loosening): the two KNOWN-ANSWER arms are identical BY
    # CONSTRUCTION -- PV7 requires both to return the target -- so demanding they differ is
    # incoherent with the gate that demands they both succeed.
    allowed.add(tuple(sorted(["K_SELF_GG", "K_SELF_SS"])))
    # AMENDMENT A6 (LOOSENS; mechanism ANALYTICALLY PINNED and reproduced from disk): a single
    # donor's whole bundle makes that donor's own anchor row an exact match at cos ~1 in BOTH
    # fields, so quantisation cannot change the argmax. The landed
    # exp_graded_path_vs_orthographic_floor_v1 carries F_SCRAMBLE_ON and F_SCRAMBLE_OFF at the same
    # 0.01375 with the IDENTICAL digest 4596b30dc13e9692. This is the mechanism A5 removed from the
    # CURVE arms; the floor keeps it because the landed floor has it.
    allowed.add(tuple(sorted(["F_SCRAMBLE_G", "F_SCRAMBLE_S"])))
    unexpected = {v: ks for v, ks in collisions.items() if tuple(sorted(ks)) not in allowed}

    got_gg, got_ss = per_arm["MA_f100_GG"]["hit_at_1"], per_arm["MA_f100_SS"]["hit_at_1"]
    got_or = per_arm["F_ORTHO"]["hit_at_1"]
    cue_mono = {}
    for model in ("MODEL_A", "MODEL_B"):
        vals = [cue_axis[model]["%.2f" % f] for f in F_LEVELS]
        cue_mono[model] = bool(all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)))

    scr_g = per_arm["F_SCRAMBLE_G"]["hit_at_1"]
    scr_s = per_arm["F_SCRAMBLE_S"]["hit_at_1"]
    pv = {
        "PV1_MA_f100_GG_reproduces_0.0480": {
            "observed": got_gg, "target": REPRO_GG, "abs_diff": abs(got_gg - REPRO_GG),
            "passed": None if smoke else bool(abs(got_gg - REPRO_GG) < REPRO_TOL)},
        "PV2_MA_f100_SS_reproduces_0.0465": {
            "observed": got_ss, "target": REPRO_SS, "abs_diff": abs(got_ss - REPRO_SS),
            "passed": None if smoke else bool(abs(got_ss - REPRO_SS) < REPRO_TOL)},
        "PV3_F_ORTHO_reproduces_0.0870": {
            "observed": got_or, "target": REPRO_ORTHO, "abs_diff": abs(got_or - REPRO_ORTHO),
            "passed": None if smoke else bool(abs(got_or - REPRO_ORTHO) < REPRO_TOL)},
        "PV4_MB_f100_bit_identical_to_MA_f100": {
            "passed": bool(all(digests["MA_f100_%s" % c] == digests["MB_f100_%s" % c]
                               for c in CONVENTIONS))},
        "PV5_cue_axis_strictly_decreasing": {"observed": cue_axis, "per_model": cue_mono,
                                             "passed": bool(all(cue_mono.values()))},
        "PV6_no_overlap_control_at_matched_scramble": {
            "values": {c: per_arm["MA_f000_%s" % c]["hit_at_1"] for c in CONVENTIONS},
            "scramble_G": scr_g, "scramble_S": scr_s,
            "note": "AMENDMENT A5: f=0.00 is now a MULTI-DONOR mixture (zero target content); "
                    "F_SCRAMBLE_* is the separate single-donor floor the landed cells used",
            "passed": bool(per_arm["MA_f000_GG"]["hit_at_1"] <= scr_g + 1e-12
                           and per_arm["MA_f000_SS"]["hit_at_1"] <= scr_s + 1e-12)},
        "PV7_known_answer_and_self_retrieval": {
            "K_SELF_GG": per_arm["K_SELF_GG"]["hit_at_1"],
            "K_SELF_SS": per_arm["K_SELF_SS"]["hit_at_1"],
            "self_retrieval_G": sr_g, "self_retrieval_S": sr_s,
            "n_self_retrieval": [sr_ng, sr_ns],
            "passed": bool(per_arm["K_SELF_GG"]["hit_at_1"] >= K_SELF_MIN
                           and per_arm["K_SELF_SS"]["hit_at_1"] >= K_SELF_MIN
                           and sr_g >= SELF_RETRIEVAL_FLOOR and sr_s >= SELF_RETRIEVAL_FLOOR
                           and min(sr_ng, sr_ns) >= 30)},
        "PV8_null_content_at_base_rate": {
            "gold_base_rate": gold_base_rate,
            "N_NULLCONTENT_G": per_arm["N_NULLCONTENT_G"]["hit_at_1"],
            "N_NULLCONTENT_S": per_arm["N_NULLCONTENT_S"]["hit_at_1"],
            "passed": bool(abs(per_arm["N_NULLCONTENT_G"]["hit_at_1"] - gold_base_rate) <= 0.01
                           and abs(per_arm["N_NULLCONTENT_S"]["hit_at_1"]
                                   - gold_base_rate) <= 0.01)},
        "PV9_arms_must_differ": {
            "gate_object": "PICK vector (AMENDMENT A1, TIGHTENS; hit digests reported not gated)",
            "n_arms_in_gate": len(pick_digests),
            "excluded_from_gate": ["F_FREQ (a count argmax, no vector pick)"],
            "unexpected_collisions": unexpected,
            "permitted": [sorted(x) for x in sorted(allowed)],
            "passed": bool(len(unexpected) == 0)},
        "PV10_signed_construction_matches_real_switch": _st_signed_matches_switch(),
        "PV11_no_external_llm": _no_external_llm(),
        "PV12_canonicalize_switch_blind_reconfirmed": _st_canonicalize_is_switch_blind(),
    }
    pv_failed = sorted(k for k, v in pv.items() if isinstance(v, dict) and v.get("passed") is False)

    # ---- Q1 (axis dependence) and Q2 (capability), decided SEPARATELY ------------------------
    floors = {k: bs["arm_acc_ci"][k]["ci_hi"] for k in ("F_ORTHO", "F_FREQ", "F_SCRAMBLE_G")}
    floor_name = max(floors, key=lambda x: floors[x])
    floor_hi = floors[floor_name]
    q2 = {}
    for nm in sorted(arms_hit):
        if not (nm.startswith("MA_") or nm.startswith("MB_") or nm.startswith("H_SENT")):
            continue
        lo_ci = bs["arm_acc_ci"][nm]["ci_lo"]
        q2[nm] = {"ci_lo": lo_ci, "strongest_floor": floor_name, "floor_ci_hi": floor_hi,
                  "CI_SEPARATED_ABOVE_FLOOR": bool(lo_ci > floor_hi)}
    any_good = sorted(k for k, v in q2.items() if v["CI_SEPARATED_ABOVE_FLOOR"])
    fired_pos = sorted(k for k, v in bs["did"].items()
                       if v["ci_excludes_zero"] and v["did"] > 0 and ("f050" in k or "f020" in k))
    fired_neg = sorted(k for k, v in bs["did"].items()
                       if v["ci_excludes_zero"] and v["did"] < 0 and ("f050" in k or "f020" in k))

    if pv_failed:
        verdict = "INSTRUMENT_STILL_LOOSE"
        verdict_msg = ("pre-registered validity gates FAILED: %s -- NO quality number is published"
                       % ", ".join(pv_failed))
    elif fired_pos:
        verdict = "SIGN_COSTS_MORE_UNDER_PARTIAL_CUE"
        verdict_msg = ("Q1 POSITIVE: %d difference-in-differences CI-separated ABOVE zero at "
                       "f=0.50/0.20 (%s). Q2 %s: strongest floor %s, arms clearing it: %s"
                       % (len(fired_pos), ", ".join(fired_pos[:4]),
                          "POSITIVE" if any_good else "NEGATIVE", floor_name,
                          ", ".join(any_good) if any_good else "NONE"))
    elif fired_neg:
        verdict = "SIGN_COSTS_LESS_UNDER_PARTIAL_CUE"
        verdict_msg = ("Q1 REVERSED: %s. Q2 %s (strongest floor %s)"
                       % (", ".join(fired_neg[:4]),
                          ", ".join(any_good) if any_good else "NEGATIVE", floor_name))
    else:
        verdict = "SIGN_IS_AXIS_INDEPENDENT"
        verdict_msg = ("Q1 NULL: no difference-in-differences at f=0.50 or f=0.20 excludes zero "
                       "for either cue model -- the prior exact-key null GENERALISES off the "
                       "exact-key point. Q2 %s (strongest floor %s)."
                       % (", ".join(any_good) if any_good else "NEGATIVE", floor_name))

    rep = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "prereg": PREREG_PATH,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict, "verdict_msg": verdict_msg,
        "GRADED_COMPARATOR_at_import": bool(RGL.GRADED_COMPARATOR),
        "config_fingerprint": cfp, "n_items": n, "n_anchors": n_anchors, "d": CTX_D,
        "item_construction": item_diag, "gold_base_rate": gold_base_rate,
        "cue_axis_measured_cos_to_exact_key": cue_axis,
        "per_arm": per_arm, "arm_hit_digests": digests, "arm_pick_digests": pick_digests,
        "permitted_endpoint_identities": [sorted(x) for x in sorted(allowed)],
        "amendments_after_smoke_before_full": {
            "A1": "PV9 digests PICKS not HITS -- TIGHTENS. A ~5% hit vector collided 16 arms at "
                  "smoke including arms with provably different queries; the gate was measuring "
                  "the wrong object. No threshold changed.",
            "A2": "K_SELF_GG == K_SELF_SS added to the permitted-identity set -- LOOSENS, and it "
                  "is stated as loosening. Two known-answer arms both required to be >= 0.99 are "
                  "identical by construction. No threshold changed.",
            "A3": "PV8 NOT changed. Its smoke failure was pre-diagnosed as UNDERPOWER: at n=300 "
                  "the +-0.01 band is 0.96 SE wide; at n=4000 it is 3.52 SE wide. A full-scale "
                  "failure is therefore a REAL leak.",
            "A5": "MODEL A's substituted dimensions now come from MANY donors, one per dimension. "
                  "FIXES A DEGENERATE ARM, not a threshold: with ONE donor supplying every "
                  "non-target dimension, that donor's own anchor row is a near-exact match in the "
                  "eligible pool, and the signed arms returned the donor on 300/300 items at "
                  "f=0.20 and f=0.50 -- pick vectors bit-identical to the floor. F_SCRAMBLE_* is "
                  "restored as a separate STANDALONE single-donor floor arm, the landed "
                  "construction. PV1/PV2/PV3 are unaffected (all at f=1.00).",
        },
        "bootstrap": bs, "PV_GATES": pv, "PV_FAILED": pv_failed,
        "Q1_axis_dependence_difference_in_differences": bs["did"],
        "Q1_fired_positive": fired_pos, "Q1_fired_negative": fired_neg,
        "Q2_capability_vs_strongest_floor": q2, "Q2_arms_clearing_the_floor": any_good,
        "self_retrieval": {"G": {"acc": sr_g, "n": sr_ng}, "S": {"acc": sr_s, "n": sr_ns},
                           "floor": SELF_RETRIEVAL_FLOOR},
        "runtime_sign_site_enumeration": {
            "method": "numpy.sign monkeypatched with a caller-frame recorder; the REAL C3 harness "
                      "was driven end to end. NOT grep. (tools/audit_readout_sign_sites.py)",
            "live_default_G1": "ZERO sign calls in ENCODE / ACCUMULATE / FIELD / QUERY / COMPARE",
            "G0_switch_aware_sites": ["hdlab/grounding_acquisition_loop.py:160 context_vector",
                                      "hdlab/reading_grounding_loop.py:506 anchor_matrix",
                                      "hdlab/reading_grounding_loop.py:520 bundle",
                                      "hdlab/reading_grounding_loop.py:806 canonicalize_fast"],
            "switch_blind_site_fires_under_BOTH":
                "hdlab/reading_grounding_loop.py:757 canonicalize -- on the live grounding path at "
                ":1273 (_make_grounding_gate.gate) and :1492 (checkpoint); disagrees with "
                "canonicalize_fast on 37.0% of 200 C3 items under the live default",
            "prior_null_coverage":
                "exp_graded_path_vs_orthographic_floor_v1 flipped the SWITCH, so it covers the "
                "four switch-aware sites at the EXACT-KEY point ONLY (= f=1.00 here) and does NOT "
                "cover :757 at any cue overlap. The GS arm IS the :757 configuration.",
        },
        "limitations": [
            "This measures the READ-OUT. Every arm shares an encoder that is measurably the "
            "structure-axis null; no number here licenses a claim about meaning.",
            "Both cue models are OUR OPERATIONALISATION, not brain facts.",
            "NO COMPLETER IS BUILT. The code is measured with no CA3-shaped pattern completion in "
            "front of it. That is the current substrate, not the brain.",
            "The :757 site is measured as a READ-OUT CONFIGURATION (GS). This cell does not re-run "
            "the reading loop and does not measure what the banked store would contain.",
        ],
        "elapsed_s": round(time.time() - t0, 2),
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
    print("VERDICT:", verdict, flush=True)
    print("VERDICT_MSG:", verdict_msg, flush=True)
    print("WROTE", os.path.join(output_dir, "metrics.json"), flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run("smoke" if args.smoke else "full", _out_dir(args.smoke))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(_out_dir("--smoke" in sys.argv), "_crash_diagnostic.json"),
                     {"anchor_name": ANCHOR_NAME, "error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
