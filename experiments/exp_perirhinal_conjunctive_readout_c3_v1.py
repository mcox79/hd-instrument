"""exp_perirhinal_conjunctive_readout_c3_v1 -- DOES A CONJUNCTIVE ("feature A AND feature B")
CONTEXT CODE BEAT THE LIVE FLAT BAG ON THE C3 OPEN-VOCABULARY KNOWN-ANSWER READ-OUT?

PRE-REG: preregs/2026-08-15_exp_perirhinal_conjunctive_readout_c3_v1.md, written BEFORE this ran.

READ SECTION 0 OF THE PRE-REG FIRST. The obvious version of this question -- wire a bound key into
the read-out -- ALREADY RAN at full scale on this exact harness earlier today
(exp_structured_code_vs_flat_bag_c3_v1, verdict STRUCTURE_HURTS, 0.03675 vs 0.0480, CI excludes
zero). This cell is NOT that cell: that one binds a relation label to a filler and then SUMS the
pairs (top-level combination stays additive); this one takes the elementwise PRODUCT over
unordered content-word pairs, which is the operator behind the banked isolation win
(exp_interference_avoidance_conjunctive_vs_additive_v1, conjunctive 1.000 vs additive 0.273) and
which has never been run on real text.

BRAIN-FIDELITY SCOPE: the conjunction OPERATOR is UNPINNED and the perirhinal feature-ambiguity
account is CONTESTED with real failed replications. Whichever way this falls it is evidence about
THIS operator on THIS task, not about brain fidelity.

REUSES the harness, does not reinvent it: corpus / buckets / item construction / gold are imported
from experiments/exp_grounding_readout_known_answer_v1.py (C3); paired_bootstrap, _score_space,
_self_retrieval, _digest, _lcp from experiments/exp_graded_path_vs_orthographic_floor_v1.py (GP);
the trigram string-control from experiments/exp_meaning_supply_separation_v1.py (MS). The organ is
hdlab/perirhinal_conjunctive.py, landed DEFAULT-OFF with a 4/4 witness.

READ-ONLY on data/foundation/*. Changes no hdlab default. WIRES NOTHING ON: this cell MEASURES.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace; SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint via tools/exp_checkpoint, resume-safe, sorted(set()) only
# - arms-must-differ: sha256 digest over each arm's correctness vector
# - floors are ARMS, not assertions
# - KNOWN-ANSWER positive control per arm (self-retrieval >= 0.70) or that arm is VOID_PLUMBING
# - between-random-projection-draw sd reported next to every CI
# - print-progress flushing: flush=True progress line every 250 lemmas / 500 items
ASCII-only.

Run:  .venv/Scripts/python.exe experiments/exp_perirhinal_conjunctive_readout_c3_v1.py
          [--smoke|--self-test]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

import hdlab.reading_grounding_loop as RGL  # noqa: E402
import hdlab.perirhinal_conjunctive as PC  # noqa: E402
from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
import experiments.exp_graded_path_vs_orthographic_floor_v1 as GP  # noqa: E402
from tools.exp_checkpoint import record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_perirhinal_conjunctive_readout_c3_v1"
PREREG_PATH = "preregs/2026-08-15_exp_perirhinal_conjunctive_readout_c3_v1.md"
MASTER_SEED = C3.MASTER_SEED
N_BOOT = 5000
N_PROJ_DRAWS = 3
SELF_RETRIEVAL_FLOOR = 0.70
SR_MAX = 300
K_FRAC = PC.DEFAULT_K_FRAC

# arm key -> mode fed to the organ. A1_BASE is the live flat bag and is NOT produced by the organ.
CONJ_ARMS = (("A2_CONJ_PAIR", "pair"), ("A3_CONJ_HYBRID", "hybrid"), ("A4_CONJ_SPARSE", "sparse"))
PRIMARY_ARMS = ("A2_CONJ_PAIR", "A3_CONJ_HYBRID")     # A4 is diagnostic only (two variables)


def _out_dir(smoke: bool) -> str:
    p = os.path.join(_REPO, "data", ANCHOR_NAME + ("_smoke" if smoke else ""))
    os.makedirs(p, exist_ok=True)
    return p


def _salted_symbol_fn(salt: str, d: int, cache: Dict[str, np.ndarray]):
    def fn(w: str) -> np.ndarray:
        v = cache.get(w)
        if v is None:
            seed = int.from_bytes(hashlib.sha256((salt + w).encode("utf-8")).digest()[:8],
                                  "big") % (2 ** 32)
            v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
            cache[w] = v
        return v
    return fn


# ------------------------------------------------------------------ space builders
def build_space_conjunctive(sents: List[str], buckets: Dict[str, List[int]], mode: str,
                            output_dir: str, tag: str,
                            symbol_fn=None) -> Tuple[RGL.ConceptSpace, dict]:
    """Same construction as C3.build_space, one variable changed: the per-occurrence encoder.
    Observes UNCONDITIONALLY (exactly as C3.build_space does) so the anchor population is
    identical to the base arm by construction."""
    enc = PC.PerirhinalEncoder(d=RGL.CTX_D, mode=mode, k_frac=K_FRAC, symbol_fn=symbol_fn)
    sp = RGL.ConceptSpace(d=RGL.CTX_D)
    t0 = time.time()
    lemmas = sorted(buckets)
    for k, w in enumerate(lemmas):
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            sp.observe(w, enc.vector(sents[i], w))
        if k % 250 == 0 or k == len(lemmas) - 1:
            print("[space_%s] %d/%d lemmas elapsed=%.1fs" % (tag, k + 1, len(lemmas),
                                                             time.time() - t0), flush=True)
            record_unit(output_dir, unit_key("space_" + tag, str(k + 1)),
                        {"k": k + 1, "n_encodings": enc.n_encodings})
    return sp, enc.stats()


def _field(space: RGL.ConceptSpace, expect_anchors: Optional[List[str]] = None):
    anchors, mat = space.anchor_matrix()
    if expect_anchors is not None:
        assert anchors == expect_anchors, "arm's anchor set diverged from the base arm's"
    nrm = np.linalg.norm(mat, axis=1)
    return anchors, mat, nrm, nrm >= 1e-9


def _self_retrieval_arm(items: List[dict], sents: List[str], anchors: List[str],
                        pos: Dict[str, int], mat: np.ndarray, mode: Optional[str],
                        seed: int) -> Tuple[float, int]:
    """KNOWN-ANSWER arm: encode L's HELD-OUT sentence with the SAME encoder the field was built
    with, then ask whether it is closer to L's own anchor than to a random other anchor.
    mode=None means the live flat bag (A1_BASE)."""
    rng = np.random.default_rng(seed)
    hits, n = 0, 0
    for it in items[:min(SR_MAX, len(items))]:
        L = it["L"]
        if it["sent_idx"] is None or L not in pos:
            continue
        other = anchors[int(rng.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or C3._is_variant(other, L)):
            other = anchors[int(rng.integers(len(anchors)))]
            tries += 1
        if other == L or other not in pos:
            continue
        s = sents[it["sent_idx"]]
        q = (RGL.context_vector_masked(s, L) if mode is None
             else PC.conjunctive_context_vector_masked(s, L, RGL.CTX_D, mode=mode, k_frac=K_FRAC))
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        cands = [L, other]
        cvecs = np.stack([mat[pos[c]] for c in cands], axis=0)
        cn = np.linalg.norm(cvecs, axis=1)
        if not (cn >= 1e-9).all():
            continue
        sc = (cvecs @ q) / (cn * qn)
        hits += int(cands[int(np.argmax(sc))] == L)
        n += 1
    return (hits / max(1, n)), n


def _scramble_arm(items: List[dict], sents: List[str], anchors: List[str], pos: Dict[str, int],
                  mat: np.ndarray, nrm: np.ndarray, norm2idx, donor: np.ndarray, gold_fn,
                  mode: Optional[str]) -> Tuple[np.ndarray, int]:
    """NULL arm: SCRAMBLED CONTEXT. Build L's query from an UNRELATED item's held-out sentence,
    with THIS ARM'S OWN encoder, and score it against this arm's own field with the identical
    eligibility mask and gold set. Destroys the item-context correspondence while preserving the
    corpus statistics, the field, the pool and the scorer.

    DESIGNED THIS WAY DELIBERATELY, and the alternative is a measured defect. The obvious cheaper
    null -- query with a DIFFERENT ANCHOR'S ROW from the same field -- degenerates: the nearest
    row to an anchor's own row is that anchor itself, which is not excluded (only L's variants
    are), so the arm collapses to the FIELD-INDEPENDENT question "is a random other item's lemma
    in this item's gold set". Every arm then produces a bit-identical correctness vector. That is
    exactly what happened in this cell's smoke run AND in the landed
    exp_structured_code_vs_flat_bag_c3_v1 full run, whose F_SCRAMBLE_BASE and F_SCRAMBLE_STRUCT
    share digest 4596b30dc13e9692 with arms_must_differ ok=false. Inherited defect, fixed here."""
    n = len(items)
    out = np.zeros(n, dtype=bool)
    scored = 0
    anchor_arr = np.array(anchors)
    for i, it in enumerate(items):
        L = it["L"]
        if L not in pos:
            continue
        donor_it = items[int(donor[i])]
        if donor_it["sent_idx"] is None or donor_it["L"] == L:
            continue
        s = sents[donor_it["sent_idx"]]
        q = (RGL.context_vector_masked(s, L) if mode is None
             else PC.conjunctive_context_vector_masked(s, L, RGL.CTX_D, mode=mode, k_frac=K_FRAC))
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        elig = np.ones(len(anchors), dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        sel = np.flatnonzero(elig & (nrm >= 1e-9))
        if sel.size == 0:
            continue
        sc = (mat[sel] @ q) / (nrm[sel] * qn)
        out[i] = anchor_arr[sel[int(np.argmax(sc))]] in gold_fn(L)
        scored += 1
    return out, scored


def _projection_draw_hits(sp: RGL.ConceptSpace, items: List[dict], gold_fn) -> float:
    an2, m2 = sp.anchor_matrix()
    p2 = {a: j for j, a in enumerate(an2)}
    nr2 = np.linalg.norm(m2, axis=1)
    ok2 = nr2 >= 1e-9
    n2idx: Dict[str, List[int]] = defaultdict(list)
    for a in an2:
        n2idx[normalize_lemma(a)].append(p2[a])
    h = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        L = it["L"]
        if L not in p2:
            continue
        base_e = np.ones(len(an2), dtype=bool)
        for k in sorted(set(n2idx[normalize_lemma(L)] + [p2[L]])):
            base_e[k] = False
        e = base_e & ok2
        sel2 = np.flatnonzero(e)
        q2 = m2[p2[L]]
        qn2 = float(np.linalg.norm(q2))
        if sel2.size and qn2 >= 1e-9:
            sc = (m2[sel2] @ q2) / (nr2[sel2] * qn2)
            h[i] = an2[sel2[int(np.argmax(sc))]] in gold_fn(L)
    return float(h.mean())


def _margin_block(m: np.ndarray) -> dict:
    return {"mean": float(np.mean(m)), "median": float(np.median(m))}


# ------------------------------------------------------------------ self-test
def self_test() -> int:
    print("[self-test] 1/4 organ self-tests", flush=True)
    r_org = PC._run_all_selftests()
    assert all(v.get("ok") for v in r_org.values()), r_org

    print("[self-test] 2/4 pair identity against an explicit double loop on REAL sentences",
          flush=True)
    sents = ["Blood travels through the artery and reaches the beating heart.",
             "The lantern flickered in the storm beside the quiet harbour wall."]
    for s in sents:
        for lem in ("artery", "lantern", "storm"):
            toks = PC.masked_content_tokens(s, lem)
            explicit = np.zeros(RGL.CTX_D)
            for i in range(len(toks)):
                for j in range(i + 1, len(toks)):
                    explicit += RGL.symbol_vector(toks[i]) * RGL.symbol_vector(toks[j])
            got = PC.conjunctive_context_vector_masked(s, lem, RGL.CTX_D, mode="pair")
            assert np.array_equal(got, explicit), "pair code != explicit double loop for %r" % lem

    print("[self-test] 3/4 arms are genuinely distinct on a fixture field", flush=True)
    v_bag = RGL.context_vector_masked(sents[0], "artery")
    v_pair = PC.conjunctive_context_vector_masked(sents[0], "artery", RGL.CTX_D, mode="pair")
    v_hyb = PC.conjunctive_context_vector_masked(sents[0], "artery", RGL.CTX_D, mode="hybrid")
    v_spr = PC.conjunctive_context_vector_masked(sents[0], "artery", RGL.CTX_D, mode="sparse")
    for a, b, nm in ((v_bag, v_pair, "bag/pair"), (v_pair, v_hyb, "pair/hybrid"),
                     (v_pair, v_spr, "pair/sparse"), (v_bag, v_hyb, "bag/hybrid")):
        assert not np.array_equal(a, b), "arms %s are bit-identical -- not distinct" % nm

    print("[self-test] 4/4 the LIVE default is untouched by importing this cell", flush=True)
    assert PC.PERIRHINAL_CONJUNCTIVE is False, "the organ switch defaulted ON"
    assert RGL.GRADED_COMPARATOR is True, "GRADED_COMPARATOR is not the live default"
    ref = RGL.context_vector_masked(sents[0], "artery", graded=True)
    assert np.array_equal(ref, PC.bag_vector(PC.masked_content_tokens(sents[0], "artery"),
                                             RGL.CTX_D)), "the organ's bag is not the live bag"
    print("[self-test] PASS 4/4", flush=True)
    return 0


# ------------------------------------------------------------------ run
def run(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    smoke = run_mode == "smoke"
    max_items = MS.SMOKE_MAX_ITEMS if smoke else C3.MAX_ITEMS

    assert RGL.GRADED_COMPARATOR is True, (
        "GRADED_COMPARATOR is False at import -- A1_BASE cannot be read as the 0.0480 headline.")
    assert PC.PERIRHINAL_CONJUNCTIVE is False, (
        "the perirhinal switch is ON at import -- the live default has been flipped, which this "
        "cell is not authorised to do. STOP.")

    sents = C3.build_corpus("full" if not smoke else "smoke")
    buckets, counts = C3.build_buckets(sents)
    print("[corpus] n_sentences=%d n_candidate_lemmas=%d elapsed=%.1fs" %
          (len(sents), len(buckets), time.time() - t0), flush=True)

    # ---- A1_BASE: the live flat bag, unmodified
    space_base = C3.build_space(sents, buckets, output_dir)
    anchors, mat_base, nrm_base, ok_base = _field(space_base)
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    items, diag = C3.build_items(space_base, buckets, counts, max_items)
    n = len(items)
    print("[build] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0),
          flush=True)
    if n < 2:
        return {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "n_items": n}

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    gold_fn = C3.gold_meaning_set

    hits = {}
    ranks = {}
    top50 = {}
    marg = {}
    picks = {}
    fields = {}
    enc_stats = {}

    h, r, t50, mg, pk = GP._score_space(anchors, pos, mat_base, nrm_base, ok_base, norm2idx,
                                        items, gold_fn, output_dir, "BASE")
    hits["A1_BASE"], ranks["A1_BASE"], top50["A1_BASE"] = h, r, t50
    marg["A1_BASE"], picks["A1_BASE"] = mg, pk
    fields["A1_BASE"] = (mat_base, nrm_base, ok_base)
    print("[arm A1_BASE] hit@1=%.4f elapsed=%.1fs" % (h.mean(), time.time() - t0), flush=True)

    # ---- conjunctive arms, identical items / anchors / gold
    for arm, mode in CONJ_ARMS:
        sp, st = build_space_conjunctive(sents, buckets, mode, output_dir, arm)
        an_a, mat_a, nrm_a, ok_a = _field(sp, expect_anchors=anchors)
        enc_stats[arm] = st
        h, r, t50, mg, pk = GP._score_space(anchors, pos, mat_a, nrm_a, ok_a, norm2idx, items,
                                            gold_fn, output_dir, arm)
        hits[arm], ranks[arm], top50[arm], marg[arm], picks[arm] = h, r, t50, mg, pk
        fields[arm] = (mat_a, nrm_a, ok_a)
        print("[arm %s] hit@1=%.4f elapsed=%.1fs %s" % (arm, h.mean(), time.time() - t0,
                                                        json.dumps(st)), flush=True)
        record_unit(output_dir, unit_key("arm", arm), {"hit_at_1": float(h.mean())})

    # ---- orthographic / frequency floors (arm-independent: pure string / count features)
    t_mat, t_cov = MS.trigram_matrix(anchors)
    trig_hits = np.zeros(n, dtype=bool)
    trig_ranks = np.zeros(n, dtype=np.int64)
    trig_top50 = np.zeros(n, dtype=bool)
    pre_hits = np.zeros(n, dtype=bool)
    pre_ranks = np.zeros(n, dtype=np.int64)
    freq_hits = np.zeros(n, dtype=bool)
    anchor_arr = np.array(anchors)
    alen = np.array([len(a) for a in anchors], dtype=np.float64)

    for i, it in enumerate(items):
        L = it["L"]
        gold = gold_fn(L)
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + ([pos[L]] if L in pos else []))):
            elig[k] = False
        sel_t = np.flatnonzero(elig & t_cov)
        if sel_t.size and L in pos and bool(t_cov[pos[L]]):
            sc = t_mat[sel_t] @ t_mat[pos[L]]
            trig_hits[i] = str(anchor_arr[sel_t[int(np.argmax(sc))]]) in gold
            gsel = np.array([j for j, a in enumerate(sel_t) if anchors[a] in gold], dtype=np.int64)
            if gsel.size:
                bg = float(np.max(sc[gsel]))
                trig_ranks[i] = int(np.sum(sc > bg)) + 1
                trig_top50[i] = trig_ranks[i] <= 50
            else:
                trig_ranks[i] = sel_t.size
        sel = np.flatnonzero(elig)
        if sel.size and L in pos:
            pre = np.array([GP._lcp(L, anchors[a]) for a in sel], dtype=np.float64)
            pre = pre / np.maximum(np.maximum(alen[sel], len(L)), 1.0)
            pre_hits[i] = str(anchor_arr[sel[int(np.argmax(pre))]]) in gold
            gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)
            pre_ranks[i] = (int(np.sum(pre > float(np.max(pre[gsel])))) + 1) if gsel.size else sel.size
            cnts = np.array([counts[anchors[a]] for a in sel])
            freq_hits[i] = anchor_arr[sel[int(np.argmax(cnts))]] in gold
        if (i + 1) % 500 == 0:
            print("[floors] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    # ---- NULL arms: per-arm scramble, one shared donor permutation
    donor = np.random.default_rng(MASTER_SEED + 21).permutation(n)
    scr = {}
    scr_n = {}
    for arm, mode in (("A1_BASE", None),) + CONJ_ARMS:
        m_, nr_, _ = fields[arm]
        scr[arm], scr_n[arm] = _scramble_arm(items, sents, anchors, pos, m_, nr_, norm2idx,
                                             donor, gold_fn, mode)
        print("[scramble %s] hit@1=%.4f n_scored=%d" % (arm, scr[arm].mean(), scr_n[arm]),
              flush=True)

    # ---- between-random-projection-draw spread (BASE and the two primary conjunctive arms)
    projdraw = {}
    proj = []
    for r_ in range(N_PROJ_DRAWS):
        sp = MS.build_salted_space(sents, buckets, "PROJDRAW_%d|" % r_, output_dir)
        proj.append(_projection_draw_hits(sp, items, gold_fn))
        print("[projdraw A1_BASE] draw=%d hit@1=%.4f" % (r_, proj[-1]), flush=True)
    projdraw["A1_BASE"] = {"draws": proj, "sd": float(np.std(proj))}
    for arm in PRIMARY_ARMS:
        mode = dict(CONJ_ARMS)[arm]
        proj = []
        for r_ in range(N_PROJ_DRAWS):
            cache: Dict[str, np.ndarray] = {}
            sp, _st = build_space_conjunctive(
                sents, buckets, mode, output_dir, "%s_PD%d" % (arm, r_),
                symbol_fn=_salted_symbol_fn("CONJ_PROJDRAW_%d|" % r_, RGL.CTX_D, cache))
            proj.append(_projection_draw_hits(sp, items, gold_fn))
            print("[projdraw %s] draw=%d hit@1=%.4f" % (arm, r_, proj[-1]), flush=True)
        projdraw[arm] = {"draws": proj, "sd": float(np.std(proj))}

    # ---- KNOWN-ANSWER arms (instrument validity), one per scored arm
    sr = {}
    for arm, mode in (("A1_BASE", None),) + CONJ_ARMS:
        acc, n_sr = _self_retrieval_arm(items, sents, anchors, pos, fields[arm][0], mode,
                                        MASTER_SEED + 9)
        sr[arm] = {"acc": acc, "n": n_sr, "ok": bool(acc >= SELF_RETRIEVAL_FLOOR and n_sr >= 30)}
        print("[self-retrieval %s] acc=%.4f n=%d ok=%s" % (arm, acc, n_sr, sr[arm]["ok"]),
              flush=True)

    # ---- bootstrap
    arms: Dict[str, np.ndarray] = {k: v.astype(float) for k, v in hits.items()}
    arms["A5_STRINGCTRL"] = trig_hits.astype(float)
    arms["A7_PREFIX_ONLY"] = pre_hits.astype(float)
    arms["F_FREQUENCY"] = freq_hits.astype(float)
    for arm in scr:
        arms["F_SCRAMBLE_" + arm] = scr[arm].astype(float)

    deltas = []
    for arm, _m in CONJ_ARMS:
        deltas += [("d_%s_minus_A1_BASE" % arm, arm, "A1_BASE"),
                   ("d_%s_minus_A5_STRINGCTRL" % arm, arm, "A5_STRINGCTRL"),
                   ("d_%s_minus_A7_PREFIX_ONLY" % arm, arm, "A7_PREFIX_ONLY"),
                   ("d_%s_minus_F_FREQUENCY" % arm, arm, "F_FREQUENCY"),
                   ("d_%s_minus_F_SCRAMBLE_%s" % (arm, arm), arm, "F_SCRAMBLE_" + arm)]
    deltas += [("d_A1_BASE_minus_A5_STRINGCTRL", "A1_BASE", "A5_STRINGCTRL"),
               ("d_A1_BASE_minus_A7_PREFIX_ONLY", "A1_BASE", "A7_PREFIX_ONLY"),
               ("d_A1_BASE_minus_F_FREQUENCY", "A1_BASE", "F_FREQUENCY"),
               ("d_A1_BASE_minus_F_SCRAMBLE_A1_BASE", "A1_BASE", "F_SCRAMBLE_A1_BASE")]
    bs = GP.paired_bootstrap(arms, deltas, N_BOOT, MASTER_SEED + 5)

    digests = {k: GP._digest(v) for k, v in arms.items()}
    groups = defaultdict(list)
    for k, dg in digests.items():
        groups[dg].append(k)
    collisions = {dg: sorted(v) for dg, v in groups.items() if len(v) > 1}

    per_arm = {}
    for k in sorted(arms):
        blk = {"hit_at_1": float(arms[k].mean())}
        if k in ranks:
            blk.update({"median_rank": float(np.median(ranks[k])),
                        "frac_gold_in_top50": float(top50[k].mean()),
                        "separation_margin_z": _margin_block(marg[k]),
                        "example_picks": picks[k][:12]})
        if k == "A5_STRINGCTRL":
            blk.update({"median_rank": float(np.median(trig_ranks)),
                        "frac_gold_in_top50": float(trig_top50.mean())})
        if k == "A7_PREFIX_ONLY":
            blk["median_rank"] = float(np.median(pre_ranks))
        per_arm[k] = blk

    a1 = per_arm["A1_BASE"]["hit_at_1"]
    # HARNESS-INTEGRITY GATE. Scoped to FULL, because at smoke scale the corpus is truncated and
    # max_items is 300, so A1_BASE CANNOT equal the full-scale 0.0480 headline by construction --
    # an unscoped gate would make every smoke run stop, which is what it did on the first smoke.
    a1_reproduces = (abs(a1 - 0.048) < 1e-9) if run_mode == "full" else None
    harness_ok = (a1_reproduces is not False)

    # ---- verdict: three independent gates per arm
    floor_names = ["A5_STRINGCTRL", "A7_PREFIX_ONLY", "F_FREQUENCY"]
    strongest_floor = max(floor_names, key=lambda k: per_arm[k]["hit_at_1"])
    arm_verdicts = {}
    for arm, _m in CONJ_ARMS:
        d_base = bs["deltas"]["d_%s_minus_A1_BASE" % arm]
        sd_gate = max(projdraw.get(arm, {"sd": 0.0})["sd"], projdraw["A1_BASE"]["sd"])
        beats_base = bool(d_base["ci_excludes_zero"] and d_base["delta"] > 0
                          and abs(d_base["delta"]) > sd_gate)
        below_base = bool(d_base["ci_excludes_zero"] and d_base["delta"] < 0
                          and abs(d_base["delta"]) > sd_gate)
        floor_ds = [bs["deltas"]["d_%s_minus_%s" % (arm, f)] for f in floor_names]
        floor_ds.append(bs["deltas"]["d_%s_minus_F_SCRAMBLE_%s" % (arm, arm)])
        clears_floor = bool(all(d["ci_excludes_zero"] and d["delta"] > 0 for d in floor_ds))
        arm_verdicts[arm] = {
            "hit_at_1": per_arm[arm]["hit_at_1"],
            "delta_vs_A1_BASE": d_base,
            "projdraw_sd_gate": sd_gate,
            "gate1_beats_base_CI_separated_and_exceeds_projdraw_sd": beats_base,
            "gate2_clears_max_orthographic_frequency_scramble": clears_floor,
            "gate3_known_answer_self_retrieval_ok": sr[arm]["ok"],
            "is_below_base_CI_separated": below_base,
            "WINS": bool(beats_base and clears_floor and sr[arm]["ok"]),
        }

    base_clears = bool(all(bs["deltas"]["d_A1_BASE_minus_%s" % f]["ci_excludes_zero"]
                           and bs["deltas"]["d_A1_BASE_minus_%s" % f]["delta"] > 0
                           for f in floor_names + ["F_SCRAMBLE_A1_BASE"]))

    winners = sorted(a for a in PRIMARY_ARMS if arm_verdicts[a]["WINS"])
    losers = sorted(a for a in PRIMARY_ARMS if arm_verdicts[a]["is_below_base_CI_separated"])

    if not harness_ok:
        verdict = "HARNESS_MISMATCH_STOP"
        verdict_msg = ("A1_BASE=%.6f does not reproduce the 0.0480 C3 headline to 1e-9 -- "
                       "harness-integrity gate FAILED, no conclusion drawn." % a1)
    elif not sr["A1_BASE"]["ok"]:
        verdict = "VOID_PLUMBING_SELF_RETRIEVAL"
        verdict_msg = ("A1_BASE known-answer arm %.4f (n=%d) is below the %.2f floor -- the "
                       "instrument is not established and no quality number is published." %
                       (sr["A1_BASE"]["acc"], sr["A1_BASE"]["n"], SELF_RETRIEVAL_FLOOR))
    elif collisions:
        verdict = "ARMS_NOT_DISTINCT"
        verdict_msg = ("arms produced bit-identical correctness vectors: %s -- the deltas between "
                       "them are not measurements." % json.dumps(collisions))
    elif winners:
        verdict = "CONJUNCTIVE_WINS_CLEARS_FLOOR"
        verdict_msg = ("%s beat the flat bag AND cleared max(orthographic,frequency,scramble) with "
                       "a passing known-answer arm." % ", ".join(winners))
    elif losers:
        verdict = "CONJUNCTIVE_HURTS"
        verdict_msg = ("no conjunctive arm beat the flat bag; %s are CI-separated BELOW it "
                       "(strongest floor is %s at %.4f, live base %.4f)." %
                       (", ".join(losers), strongest_floor,
                        per_arm[strongest_floor]["hit_at_1"], a1))
    else:
        verdict = "CONJUNCTIVE_DOES_NOT_HELP"
        verdict_msg = ("no conjunctive arm cleared all three gates and none is CI-separated below "
                       "base either; strongest floor %s=%.4f, live base=%.4f." %
                       (strongest_floor, per_arm[strongest_floor]["hit_at_1"], a1))

    rep = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "prereg": PREREG_PATH,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "GRADED_COMPARATOR_at_import": bool(RGL.GRADED_COMPARATOR),
        "PERIRHINAL_CONJUNCTIVE_at_import": bool(PC.PERIRHINAL_CONJUNCTIVE),
        "n_items": n, "n_anchors": n_anchors, "item_construction": diag,
        "encoder_stats": enc_stats,
        "a1_base_reproduces_c3_headline_0480_exactly": a1_reproduces,
        "harness_integrity_gate_scope": "full only (null at smoke by construction)",
        "known_answer_self_retrieval": {"floor": SELF_RETRIEVAL_FLOOR, "per_arm": sr},
        "scramble_null_arm": {"design": "scrambled CONTEXT, per-arm encoder, shared donor perm",
                              "n_scored_per_arm": scr_n},
        "projdraw": projdraw,
        "bootstrap": bs,
        "per_arm": per_arm,
        "strongest_no_understanding_floor": {"arm": strongest_floor,
                                             "hit_at_1": per_arm[strongest_floor]["hit_at_1"]},
        "arm_verdicts": arm_verdicts,
        "base_clears_floor": base_clears,
        "arm_digests": digests,
        "arms_must_differ": {"ok": len(collisions) == 0, "collisions": collisions},
        "primary_arms": list(PRIMARY_ARMS),
        "diagnostic_only_arms": ["A4_CONJ_SPARSE"],
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(output_dir, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print(json.dumps(per_arm, indent=1))
    print(json.dumps(arm_verdicts, indent=1))
    print("VERDICT:", verdict)
    print("VERDICT_MSG:", verdict_msg)
    print("WROTE", p)
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
        out = _out_dir("--smoke" in sys.argv)
        crash = os.path.join(out, "_crash_diagnostic.json")
        with open(crash + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME,
                       "error": "%s: %s" % (type(exc).__name__, exc),
                       "traceback": traceback.format_exc(),
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        os.replace(crash + ".tmp", crash)
        raise
