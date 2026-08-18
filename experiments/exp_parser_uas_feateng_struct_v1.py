"""Parser UAS classical-feature-engineering terminus: does the STRUCTURAL first-order family reach lit?

Settles the ONE remaining open classical-parser lever the headroom-cell VET (skunkworks a04fb3fa)
confirmed is NOT saturated. Amends banked atom 29402 ("classical nearly-tapped ~0.80") either way.

WHAT IS ALREADY KNOWN (dedup, builds-on, credits):
  - CANON greedy 1st-order (hdlab.arc_parser, ~20 templates), UPOS, ep10: uas_all 0.7868 / nopunct 0.8120.
    MEASURED@data/exp_parser_uas_headroom_leakhunt_v1/metrics.json.
  - The headroom cell swept EPOCHS+DATA+POS-COLUMN(orig features): overall_best 0.8062 (combo@ep10),
    lift +0.0194 -> verdict SATURATED_29402_HOLDS. The VET found that verdict is a BAND ARTIFACT (fires
    unless lift>=0.0200; combo's +0.0194 missed by 0.0006). MEASURED@same metrics.json.
  - An OOV/LEXICAL-AFFIX rich-feature cell ALREADY RAN: exp_parser_uas_ladder_richfeat_v1 = base + char
    prefix/suffix + word-shape + affix x POS-pair. Verdict RICHFEAT_LIFT_REAL, RICH 0.7925 (+0.0057) at
    ep10, UPOS only, no nopunct, no epoch sweep. MEASURED@data/exp_parser_uas_ladder_richfeat_v1/metrics.json.
    That family is the OOV-backoff family; it lifted only +0.0057 and did NOT help OOV arcs (delta -0.0041).

WHAT IS STILL OPEN (this cell; genuinely un-run, NOT a rediscovery):
  The McDonald-2005 / Zhang-Nivre FIRST-ORDER STRUCTURAL-CONTEXT feature family -- distinct in KIND from
  the OOV-affix family above: systematic SURROUNDING-4-POS conjunctions (hp-1,hp,dp-1,dp and the +1
  variants), FULL direction x distance-bucket crosses of the head/dep POS+word templates, and the GENERAL
  all-in-between-POS templates (canon only fires VERB/PUNCT between). Plus the three dimensions the two
  prior cells never crossed on the rich features: (a) EPOCH OPTIMUM (avg-perceptron overfits past ~ep5;
  each arm's own optimum is swept, not a fixed ep10), (b) the UPOS|XPOS COMBO POS-column as an oracle-POS
  upper bound, (c) nopunct reporting (the convention fair to the lit 0.86-0.89 UD-EWT numbers).

  HONEST SCOPE (do NOT overclaim the framing): TRUE higher-order Zhang-Nivre features (head-child-
  GRANDCHILD, SIBLING, VALENCY) require the PARTIAL TREE and are UN-COMPUTABLE in this first-order
  arc-factored greedy-head decoder without reading gold structure -- which would be a catastrophic LEAK
  (the exact thing the mutation probe guards). This cell therefore builds the realizable + leak-clean +
  UPOS-deployable subset: the McDonald FIRST-ORDER structural-context set. Grandchild/sibling/valency
  would need a decoder rebuild (2nd-order Eisner or transition-based) and are explicitly OUT OF SCOPE.

ARMS (all GREEDY decode, verbatim hdlab._decode; ONE VARIABLE per comparison = the feature fn / POS source):
  base_upos   : hdlab._arc_ids (canon feats), UPOS         -- control, reproduces canon; epoch sweep
  struct_upos : base + STRUCTURAL-CONTEXT family, UPOS      -- ISOLATES the open lever's own contribution
  full_upos   : base + OOV-affix (credit prior cell) + STRUCTURAL, UPOS -- the DEPLOYABLE classical ceiling
  full_combo  : full features on UPOS|XPOS combo POS-column -- ORACLE-POS upper bound (needs a 49-tag XPOS
                tagger we do NOT have to deploy; reported as an UPPER BOUND only, not a deployable number)
  Each arm: ONE train run to ep_max, averaged-weight SNAPSHOTS at {2,3,4,5,6,8} (epoch optimum found per arm).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = persisted canon 0.7868 greedy, re-derived LIVE on UD-EWT dev (phase A positive control)
      AND the base_upos retrain arm (harness-matched). NOT a strawman.
  (2) CAN-FAIL (all informative): (a) structural features may give ~0 lift or NET-HURT (more templates ->
      more hash collisions in the fixed 2^21 space + avg-perceptron overfit); (b) may lift a little but stay
      < +0.02 (within the combo-oracle noise the VET flagged) = 29402 HOLDS, classical terminus, IDLE
      justified; (c) may climb >= +0.04 toward lit = 29402 OVER-READ, classical feature axis is a LIVE
      reader lever worth a follow-on fold. All three reportable.
  (3) DIFFICULTY-ON = held-out UD-EWT dev (1989 sents / ~24444 arcs), same eval as the persisted parser; NOT
      train accuracy. Epoch overfit is the difficulty (best dev epoch < max epoch expected).
  (4) ONE-VARIABLE per comparison: base_upos vs struct_upos vs full_upos = feature templates (POS held UPOS,
      decode held greedy, epochs swept per arm); full_upos vs full_combo = POS-column content (features held).

VERDICT BANDS (pre-registered; DEPLOYABLE lever = full_upos BEST-epoch uas_all vs canon 0.7868):
  LIVE_LEVER_29402_OVERREAD : full_upos_best >= 0.8268 (canon +0.04; meaningfully toward lit 0.86-0.89) ->
                              classical feature axis IS a real reader lever, worth a follow-on fold.
  PARTIAL_HEADROOM          : 0.8068 <= full_upos_best < 0.8268 (+0.02 to +0.04) -> real but modest;
                              amends 29402 to "small classical headroom, not lever-grade".
  SATURATED_29402_HOLDS     : full_upos_best < 0.8068 (< +0.02, i.e. within the combo-oracle band artifact)
                              -> classical structural axis tapped; 29402 fully holds; terminus; IDLE justified.
  (nopunct read reported against lit 0.86-0.89 as the fairer-convention cross-check; combo arm = upper bound.)

LEAK-HUNT (mutation probe, in self_test AND logged in metrics): every feature reads ONLY sent[k][1] (form)
  and sent[k][2] (POS); NEVER sent[k][3] (gold head) or sent[k][4] (deprel). Garble the head+deprel columns
  of every token and assert the full feature-id vector is BIT-IDENTICAL for a sample of arcs. Feature output
  invariant to garbled gold columns => no gold-structure leak (same probe the headroom VET used).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: pure-python averaged perceptron, greedy O(n^2)
  decode; UD-EWT avg len ~16. MEASURED calib base 1ep full ~18s; full feats ~3.4x ~61s/ep; ep_max=8 x 4 arms
  ~ 25-32 min; precompute freed between arms to cap peak RAM ~2GB). Storage: no_storage (writes only diagnostic
  metrics; persists NO substrate atoms, NO frontend asset). progress_logging: print_flush_true (long cell;
  per-epoch + per-snapshot flush). Determinism: FIXED int seed, numpy default_rng, sorted/enumerated
  iteration, deterministic crc32 hash; NO hash()-seeded RNG, NO list(set()). LOCAL-ONLY foreground-to-
  completion; NO queue, NO origin push, NO remote-persist, NO substrate store write, NO git add.

CELL-TEMPLATE: except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace
  metrics; start-marker + crash-diagnostic + heartbeat; arms_differ (distinct feature-id digests); all
  numbers tagged MEASURED@/CITED@/THEORETICAL@.

NO LLM. NO nltk. NO torch. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

from hdlab.arc_parser import _arc_ids, _decode, _h, _dist, SIZE, ArcParser  # noqa: E402
# Build-on + credit the prior OOV-affix rich cell (its rich extras = the OOV/lexical family).
from exp_parser_uas_ladder_richfeat_v1 import _arc_ids_rich as _arc_ids_oov  # noqa: E402

ANCHOR_NAME = "parser_uas_feateng_struct_v1"
UD_DIR = REPO / "experiments" / "data" / "ud_english_ewt"
FRONTEND_DIR = REPO / "data" / "frontend_assets"
CANON_ARC = FRONTEND_DIR / "arc_parser_hashed_ud_ewt.npz"   # canon greedy 1st-order (0.7868)
OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"
CKPT_DIR = OUT_DIR / "ckpt"

BASELINE_CANON_UAS = 0.7868   # MEASURED@data/exp_parser_uas_headroom_leakhunt_v1/metrics.json:phase_A
CANON_NOPUNCT = 0.8120        # MEASURED@same:canon_nopunct
OOV_RICH_EP10 = 0.7925        # MEASURED@data/exp_parser_uas_ladder_richfeat_v1/metrics.json:rich_uas
LIT_LOW, LIT_HIGH = 0.86, 0.89  # CITED@notes/research_drill_dep_parse_0787_to_085 (feat-eng UD-EWT dev)
SEED = 1027
MAXLEN = 50


# ================================================================================================
# STRUCTURAL-CONTEXT feature family (McDonald 2005 first-order). Surface-only: reads sent[k][1] (form)
# and sent[k][2] (POS) ONLY -- never sent[k][3] (gold head) / sent[k][4] (deprel). This is the leak
# invariant, asserted by the mutation probe.
# ================================================================================================
def _struct_extra_feats(sent: Sequence[tuple], i: int, h: int) -> List[str]:
    """New STRUCTURAL first-order feature strings (surrounding-4-POS, dir x dist crosses, all-between-POS)."""
    n = len(sent)
    dw, dp = sent[i - 1][1].lower(), sent[i - 1][2]
    if h == 0:
        hw, hp = "<ROOT>", "ROOT"
        d = 0
    else:
        hw, hp = sent[h - 1][1].lower(), sent[h - 1][2]
        d = h - i
    dr = "L" if d < 0 else "R"
    db = _dist(d)
    # surrounding POS context (1-based positions; boundary tokens). POS column only.
    hp_m1 = sent[h - 2][2] if h >= 2 else "<S>"
    hp_p1 = sent[h][2] if 0 < h < n else "<E>"
    dp_m1 = sent[i - 2][2] if i >= 2 else "<S>"
    dp_p1 = sent[i][2] if i < n else "<E>"
    F = [
        # --- McDonald surrounding-4-POS conjunctions (canon only has partial trigram context) ---
        "S_c1:%s_%s_%s_%s" % (hp, hp_p1, dp_m1, dp),
        "S_c2:%s_%s_%s_%s" % (hp_m1, hp, dp_m1, dp),
        "S_c3:%s_%s_%s_%s" % (hp, hp_p1, dp, dp_p1),
        "S_c4:%s_%s_%s_%s" % (hp_m1, hp, dp, dp_p1),
        # --- surrounding-4-POS conjoined with direction+distance (the distance-bucketed context lift) ---
        "S_c1_dd:%s_%s_%s_%s|%s_%s" % (hp, hp_p1, dp_m1, dp, dr, db),
        "S_c2_dd:%s_%s_%s_%s|%s_%s" % (hp_m1, hp, dp_m1, dp, dr, db),
        # --- full direction x distance-bucket crosses of the head/dep POS+word core (canon splits these) ---
        "S_hpdp_dd:%s_%s_%s_%s" % (hp, dp, dr, db),
        "S_hwdp_dd:%s_%s_%s_%s" % (hw, dp, dr, db),
        "S_hpdw_dd:%s_%s_%s_%s" % (hp, dw, dr, db),
        "S_hwdw_dir:%s_%s_%s" % (hw, dw, dr),
        # --- head-context x dep POS trigram backoffs ---
        "S_hm1_hp_dp:%s_%s_%s" % (hp_m1, hp, dp),
        "S_hp1_hp_dp:%s_%s_%s" % (hp_p1, hp, dp),
        "S_dm1_dp_hp:%s_%s_%s" % (dp_m1, dp, hp),
        "S_dp1_dp_hp:%s_%s_%s" % (dp_p1, dp, hp),
    ]
    # --- GENERAL all-in-between POS (canon fires only VERB/PUNCT between) ---
    if h != 0:
        lo, hi = min(i, h), max(i, h)
        between = [sent[k - 1][2] for k in range(lo + 1, hi)]
        seen_b = set()
        for b in between:
            if b in seen_b:
                continue
            seen_b.add(b)
            F.append("S_btw:%s_%s_%s" % (hp, b, dp))
        F.append("S_btwct_dir:%s_%s_%s_%s" % (hp, dp, _dist(len(between)), dr))
    return F


def _mk_ff(pos_kind_note: str, use_oov: bool, use_struct: bool):
    """Build a feature fn = canon base ids [+ OOV-affix extras] [+ structural extras]. Leak-clean by construction."""
    def ff(sent, i, h):
        if use_oov:
            ids = _arc_ids_oov(sent, i, h)   # already = canon base + OOV-affix family (monotone superset)
        else:
            ids = _arc_ids(sent, i, h)
        if use_struct:
            se = _struct_extra_feats(sent, i, h)
            extra = np.fromiter((_h(f) for f in se), dtype=np.int64, count=len(se))
            ids = np.concatenate([ids, extra])
        return ids
    ff._tag = pos_kind_note  # for debugging
    return ff


FF_BASE = _mk_ff("base", use_oov=False, use_struct=False)
FF_STRUCT = _mk_ff("struct", use_oov=False, use_struct=True)
FF_FULL = _mk_ff("full", use_oov=True, use_struct=True)


# ================================================================================================
# Loader: POS-column content is the ONLY thing that varies for the combo arm. upos_sents always carries
# UPOS (for the punct-exclusion eval mask, arm-independent). Matches the headroom cell's loader.
# ================================================================================================
def _load(split: str, pos_kind: str) -> Tuple[list, list]:
    fp = UD_DIR / ("en_ewt-ud-%s.conllu" % split)
    sents: list = []
    upos_sents: list = []
    cur: list = []
    cur_u: list = []
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); upos_sents.append(cur_u); cur = []; cur_u = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]:
                continue
            try:
                idx = int(c[0]); head = int(c[6])
            except Exception:
                continue
            upos, xpos = c[3], c[4]
            if pos_kind == "upos":
                pf = upos
            elif pos_kind == "combo":
                pf = upos + "|" + (xpos if xpos not in ("", "_") else upos)
            else:
                raise ValueError("pos_kind %r" % pos_kind)
            cur.append((idx, c[1], pf, head, c[7]))
            cur_u.append((idx, c[1], upos, head, c[7]))
    if cur:
        sents.append(cur); upos_sents.append(cur_u)
    keep = [i for i, s in enumerate(sents) if 1 <= len(s) <= MAXLEN]
    return [sents[i] for i in keep], [upos_sents[i] for i in keep]


# ================================================================================================
# Train (avg-perceptron, greedy in-loop, verbatim algorithm) parametrized by feat_fn; snapshots weights.
# ================================================================================================
def _precompute(sents, feat_fn) -> list:
    out = []
    for s in sents:
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = feat_fn(s, i, h)
        out.append(arc)
    return out


def train_snapshots(train, feat_fn, checkpoints: List[int], max_ep: int, seed: int,
                    hb=None) -> Dict[int, np.ndarray]:
    rng = np.random.default_rng(seed)
    tr_arc = _precompute(train, feat_fn)
    W = np.zeros(SIZE)
    CW = np.zeros(SIZE)
    c = 1
    snaps: Dict[int, np.ndarray] = {}
    cps = set(checkpoints)
    for ep in range(max_ep):
        te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]
            arc = tr_arc[si]
            n = len(s)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n:
                    continue
                best_h, best_s = -1, -1e18
                for h in range(0, n + 1):
                    if h == i:
                        continue
                    sc = W[arc[i][h]].sum()
                    if sc > best_s:
                        best_s, best_h = sc, h
                if best_h != gold_h:
                    np.add.at(W, arc[i][gold_h], 1.0)
                    np.add.at(CW, arc[i][gold_h], c)
                    np.add.at(W, arc[i][best_h], -1.0)
                    np.add.at(CW, arc[i][best_h], -c)
                c += 1
        if (ep + 1) in cps:
            snaps[ep + 1] = (W - CW / c).copy()
        print("[%s]   ep %d done %.1fs (snap=%s)" % (ANCHOR_NAME, ep + 1, time.time() - te, (ep + 1) in cps),
              flush=True)
        if hb is not None:
            hb(ep + 1, max_ep, time.time())
    del tr_arc  # free the precompute before the next arm (cap peak RAM)
    return snaps


def eval_both(avg: np.ndarray, dev, dev_upos, feat_fn, maxlen: int = MAXLEN) -> Dict[str, float]:
    corr_all = tot_all = corr_np = tot_np = 0
    for si, s in enumerate(dev):
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = feat_fn(s, i, h)
        head, _ = _decode(avg, arc, n)
        us = dev_upos[si]
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n:
                continue
            ok = int(head.get(i, -1) == gh)
            corr_all += ok; tot_all += 1
            if us[i - 1][2] != "PUNCT":
                corr_np += ok; tot_np += 1
    return {"uas_all": round(corr_all / tot_all, 4) if tot_all else 0.0,
            "uas_nopunct": round(corr_np / tot_np, 4) if tot_np else 0.0,
            "n_arcs_all": tot_all, "n_arcs_nopunct": tot_np}


# ================================================================================================
# Leak-hunt mutation probe: garble gold head (c[3]) + deprel (c[4]); assert feature ids BIT-IDENTICAL.
# ================================================================================================
def mutation_probe(feat_fn, sents, n_sent: int = 30, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    checked = 0
    for s in sents[:n_sent]:
        n = len(s)
        # garbled copy: head->random junk, deprel->"XXX" (columns 3 and 4). form/pos (1,2) untouched.
        gs = [(t[0], t[1], t[2], int(rng.integers(-9, 99)), "XXX") for t in s]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                a = feat_fn(s, i, h)
                b = feat_fn(gs, i, h)
                if not np.array_equal(a, b):
                    return {"leak_clean": False, "first_fail": {"i": i, "h": h}}
                checked += 1
    return {"leak_clean": True, "n_arcs_checked": checked}


# ================================================================================================
def _cfg(smoke: bool) -> dict:
    if smoke:
        return {"n_train": 300, "cps": [1, 2], "ep_max": 2}
    return {"n_train": None, "cps": [2, 3, 4, 5, 6, 8], "ep_max": 8}


def _write_start_marker(expected_units: int) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "expected_n_units": expected_units, "host": platform.node()}
    tmp = OUT_DIR / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, OUT_DIR / "_start_marker.json")


def _hb(arm: str):
    def cb(ep, max_ep, ts):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "arm": arm, "ep": ep, "max_ep": max_ep}
        with open(OUT_DIR / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return cb


def _digest(feat_fn, s) -> str:
    ids = feat_fn(s, 2, 3)
    return hashlib.sha256(ids.tobytes()).hexdigest()


def self_test() -> bool:
    print("=== %s self-test (real code paths) ===" % ANCHOR_NAME, flush=True)
    dev, dev_u = _load("dev", "upos")
    assert len(dev) > 100 and len(dev) == len(dev_u), (len(dev), len(dev_u))
    # (1) feature superset ordering: struct/full contain the base ids as a prefix (monotone).
    s0 = dev[0]
    b = _arc_ids(s0, 2, 3)
    st = FF_STRUCT(s0, 2, 3)
    fu = FF_FULL(s0, 2, 3)
    assert len(st) > len(b) and np.array_equal(st[:len(b)], b), "struct must be base-superset"
    assert len(fu) > len(st), ("full must add oov+struct over base", len(fu), len(st), len(b))
    print("[selftest] feat counts base=%d struct=%d full=%d" % (len(b), len(st), len(fu)), flush=True)
    # (2) ARMS-MUST-DIFFER: base/struct/full produce distinct feature-id digests.
    dg = {"base": _digest(FF_BASE, s0), "struct": _digest(FF_STRUCT, s0), "full": _digest(FF_FULL, s0)}
    assert len(set(dg.values())) == 3, ("arms must differ", dg)
    # combo POS-column differs from upos in the POS field (arms-must-differ across POS source).
    dvc, _ = _load("dev", "combo")
    assert "|" in dvc[0][0][2] and dvc[0][0][2].startswith(dev[0][0][2]), ("combo malformed", dvc[0][0][2])
    print("[selftest] arms differ (base/struct/full digests distinct; combo POS-column differs)", flush=True)
    # (3) LEAK-HUNT mutation probe on the FULL fn (the richest; if clean, subsets clean).
    mp = mutation_probe(FF_FULL, dev, n_sent=20)
    assert mp["leak_clean"], ("MUTATION PROBE LEAK", mp)
    print("[selftest] leak-clean: %d arcs invariant to garbled gold head/deprel" % mp["n_arcs_checked"], flush=True)
    # (4) positive control: persisted canon weights reproduce ~0.7868 on a dev slice via base fn + real eval.
    avg = ArcParser.load(str(CANON_ARC)).avg
    r = eval_both(avg, dev[:80], dev_u[:80], FF_BASE)
    assert 0.5 < r["uas_all"] <= 1.0 and r["uas_nopunct"] >= r["uas_all"] - 0.06, r
    # (5) tiny real train exercises the snapshot perceptron on the FULL fn.
    snaps = train_snapshots(dev[:50], FF_FULL, [1], 1, SEED)
    assert 1 in snaps and snaps[1].shape == (SIZE,), snaps.keys()
    print("[selftest] PASS: superset + arms-differ + leak-clean + canon-repro + snapshot-train", flush=True)
    return True


def run(smoke: bool, resume: bool) -> dict:
    t0 = time.time()
    cfg = _cfg(smoke)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    _write_start_marker(expected_units=4)

    dev_u_sents, dev_u_mask = _load("dev", "upos")
    dev_c_sents, _ = _load("dev", "combo")
    print("[%s] dev=%d sents smoke=%s cps=%s" % (ANCHOR_NAME, len(dev_u_sents), smoke, cfg["cps"]), flush=True)

    # ---- PHASE A: re-derive REAL canon baseline (positive control) ----
    A = _read_ckpt("phase_A") if resume else None
    if A is None:
        canon = ArcParser.load(str(CANON_ARC)).avg
        canon_ev = eval_both(canon, dev_u_sents, dev_u_mask, FF_BASE)
        A = {"canon_greedy": canon_ev, "canon_cited": BASELINE_CANON_UAS,
             "baseline_reproduces": abs(canon_ev["uas_all"] - BASELINE_CANON_UAS) <= 0.003}
        _write_ckpt("phase_A", A)
    print("[%s] PHASE A: canon all=%.4f nopunct=%.4f reproduces=%s"
          % (ANCHOR_NAME, A["canon_greedy"]["uas_all"], A["canon_greedy"]["uas_nopunct"],
             A["baseline_reproduces"]), flush=True)

    # ---- leak-hunt on FULL fn (logged) ----
    lk = _read_ckpt("leak") if resume else None
    if lk is None:
        lk = mutation_probe(FF_FULL, dev_u_sents, n_sent=40)
        _write_ckpt("leak", lk)
    print("[%s] leak-hunt full-fn: %s" % (ANCHOR_NAME, lk), flush=True)

    # ---- arms ----
    arm_specs = [
        ("base_upos", FF_BASE, "upos"),
        ("struct_upos", FF_STRUCT, "upos"),
        ("full_upos", FF_FULL, "upos"),
        ("full_combo", FF_FULL, "combo"),
    ]
    dev_by_pos = {"upos": (dev_u_sents, dev_u_mask), "combo": (dev_c_sents, dev_u_mask)}
    arms: Dict[str, dict] = {}
    arm_digests: Dict[str, str] = {}
    for arm, ff, pos_kind in arm_specs:
        ck = _read_ckpt("arm_%s" % arm) if resume else None
        if ck is not None:
            arms[arm] = ck
            print("[%s] arm=%s (resumed)" % (ANCHOR_NAME, arm), flush=True)
            continue
        tr, _ = _load("train", pos_kind)
        if cfg["n_train"]:
            tr = tr[:cfg["n_train"]]
        arm_digests[arm] = _digest(ff, tr[0])
        print("[%s] arm=%s pos=%s train=%d ..." % (ANCHOR_NAME, arm, pos_kind, len(tr)), flush=True)
        snaps = train_snapshots(tr, ff, cfg["cps"], cfg["ep_max"], SEED, hb=_hb(arm))
        dv_s, dv_m = dev_by_pos[pos_kind]
        curve = {}
        for ep in sorted(snaps):
            curve[ep] = eval_both(snaps[ep], dv_s, dv_m, ff)
            print("[%s]   arm=%s ep=%d -> all=%.4f nopunct=%.4f"
                  % (ANCHOR_NAME, arm, ep, curve[ep]["uas_all"], curve[ep]["uas_nopunct"]), flush=True)
        best_ep = max(curve, key=lambda e: curve[e]["uas_all"])
        best_ep_np = max(curve, key=lambda e: curve[e]["uas_nopunct"])
        arms[arm] = {"pos_kind": pos_kind, "curve": {str(k): v for k, v in curve.items()},
                     "best_ep_uas_all": best_ep, "best_uas_all": curve[best_ep]["uas_all"],
                     "best_ep_nopunct": best_ep_np, "best_uas_nopunct": curve[best_ep_np]["uas_nopunct"]}
        _write_ckpt("arm_%s" % arm, arms[arm])
        print("[%s] arm=%s DONE best all=%.4f@ep%d nopunct=%.4f@ep%d"
              % (ANCHOR_NAME, arm, arms[arm]["best_uas_all"], best_ep,
                 arms[arm]["best_uas_nopunct"], best_ep_np), flush=True)

    # ---- verdict ----
    canon_all = A["canon_greedy"]["uas_all"]
    canon_np = A["canon_greedy"]["uas_nopunct"]
    struct_best = arms["struct_upos"]["best_uas_all"]
    full_up_best = arms["full_upos"]["best_uas_all"]        # DEPLOYABLE lever (UPOS)
    full_up_best_np = arms["full_upos"]["best_uas_nopunct"]
    full_cb_best = arms["full_combo"]["best_uas_all"]        # ORACLE-POS upper bound
    full_cb_best_np = arms["full_combo"]["best_uas_nopunct"]
    lift_full_upos = round(full_up_best - canon_all, 4)
    lift_struct = round(struct_best - canon_all, 4)

    if full_up_best >= 0.8268:
        verdict = "LIVE_LEVER_29402_OVERREAD"
        live_lever = True
    elif full_up_best >= 0.8068:
        verdict = "PARTIAL_HEADROOM"
        live_lever = False
    else:
        verdict = "SATURATED_29402_HOLDS"
        live_lever = False

    msg = ("%s | canon all=%.4f nopunct=%.4f | struct_upos best=%.4f(%+.4f) | full_upos best=%.4f(%+.4f) "
           "nopunct=%.4f | full_combo(oracle-POS) best=%.4f nopunct=%.4f | lit=%.2f-%.2f | live_lever=%s"
           % (verdict, canon_all, canon_np, struct_best, lift_struct, full_up_best, lift_full_upos,
              full_up_best_np, full_cb_best, full_cb_best_np, LIT_LOW, LIT_HIGH, live_lever))

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": ("smoke" if smoke else "full"),
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(time.time() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "phase_A_baseline": A, "leak_hunt": lk, "arms": arms,
        "deployable_lever_full_upos_best_uas_all": full_up_best,
        "deployable_lever_full_upos_best_uas_nopunct": full_up_best_np,
        "struct_only_best_uas_all": struct_best,
        "oracle_upper_bound_full_combo_best_uas_all": full_cb_best,
        "oracle_upper_bound_full_combo_best_uas_nopunct": full_cb_best_np,
        "lift_full_upos_vs_canon": lift_full_upos, "lift_struct_vs_canon": lift_struct,
        "live_lever": live_lever, "canon_cited": BASELINE_CANON_UAS, "oov_rich_ep10_cited": OOV_RICH_EP10,
        "lit_target": [LIT_LOW, LIT_HIGH], "arm_feature_digests": arm_digests,
        "compute_architecture": "sequential-CPU (justified)", "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "progress_logging": "print_flush_true",
        "one_variable_per_comparison": "feature_fn (base/struct/full) at fixed UPOS+greedy; POS-column for combo",
        "scope_note": "first-order McDonald structural family only; grandchild/sibling/valency OUT OF SCOPE "
                      "(need partial tree = decoder rebuild or gold-structure leak).",
    }
    tmp = OUT_DIR / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, OUT_DIR / "metrics.json")
    print("[%s] DONE %.1fs -> %s" % (ANCHOR_NAME, time.time() - t0, verdict), flush=True)
    print(msg, flush=True)
    return payload


def _write_ckpt(name: str, payload: dict) -> None:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CKPT_DIR / (name + ".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, CKPT_DIR / (name + ".json"))


def _read_ckpt(name: str):
    p = CKPT_DIR / (name + ".json")
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(smoke=args.smoke, resume=args.resume)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUT_DIR / "metrics.json.tmp", "w", encoding="utf-8") as f:
            json.dump({"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                       "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
                       "summary": "CELL_CRASHED", "elapsed_s": 0.0,
                       "traceback": traceback.format_exc()[:5000]}, f, indent=2)
        os.replace(OUT_DIR / "metrics.json.tmp", OUT_DIR / "metrics.json")
        raise
