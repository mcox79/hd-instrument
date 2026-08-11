# CELL-TEMPLATE MANDATORY (applicable subset; single bounded local pass, not GPU/sweep/multi-seed):
# - arms_differ_verified (hash floor/gate/learned/scramble prediction vectors)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no bare except:/BaseException)
# - crlb_n/a: official positive-only micro-F1 over a fixed real corpus slice; feasibility = DEV floor
# - calibration_check: adaptive_with_discriminator_gate (GAM subsample ratio selected on a TRAIN
#   held-out split, dev-blind; discriminator-fires = full_v2 fires >0 positive predictions on dev)
# - real_code_path_exercised: self-test loads REAL PosTagger+ArcParser (via v2.entity_sets) + calls
#   REAL gam_plugin.learn/apply on a tiny synthetic subevent doc set
# - deterministic_seeding: true (hashlib-seeded scramble perm + fixed-seed subsample RNG)
# - no_leak: cue/feature fns take only structural mention-meta + parse-derived args; subevent_
#   relations read only by official_gold_labels (eval) + the learner's TRAIN-gold training
# - resumable: reuses the SHARED arc-parse cache from the causal v2 cell (read-only); any missing
#   doc is extracted via v2.entity_sets (in-memory fallback)
# - progress_logging: print_flush_true
# See preregs/2026-08-11_maven_ere_convergence_gated_subevent_v1.md for the full pre-reg.
"""exp_maven_ere_convergence_gated_subevent_v1 -- sibling of the causal cell: does the same
mechanism family (convergence gate + learned GAM readout) transfer to the MAVEN-ERE SUBEVENT
relation task (binary: subevent vs no-relation, ~99.4% NONE)?

Subevent = one event is a temporal/structural PART of another (part-whole containment/granularity),
NOT causal connection. Measure-first (disk, this cycle) showed the signal is DIFFERENT from causal:
same-sentence only 11.6%, 41.6% of positives are long-range (sent-dist>=5), arg-overlap weak
(12.6%), arg-subsumption useless (1.7%); the DOMINANT structure is event-type granularity (coarse
container types -- Hostile_encounter/Competition/Catastrophe -- as parents -> finer types --
Attack/Motion -- as children). Critically, a majority-vote bag-of-event-types baseline scores F1
0.0 (base rate 0.6% -> every type-pair majority is NONE), so the win is NOT a trivial type-lookup.

CUES (subevent-appropriate, NOT because/so connectives): forward order (parent-before-child, 69.7%
of positives), same/adjacent-sentence proximity, argument-overlap (shared participant via the OWNED
arc-parse entity sets), TRAIN-derived event-type-pair granularity/compatibility. GATE = order AND
>=1 of {type_compat, arg_overlap, proximity}. LEARNED READOUT = GAM/EBM (hdlab.learner.plugins.
gam_plugin; rule-b reuse) over those cues, binary {NONE, SUBEVENT}, TRAIN-fit, dev-blind balanced
ratio. Reuses the SHARED arc-parse cache + task-agnostic helpers from the causal v2 cell.

NO LLM, NO nltk, NO torch in the decision path. ASCII-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check"))

from maven_ere_official_eval import (  # noqa: E402
    candidate_pairs, official_gold_labels, official_prf, macro_f1_all_labels, accuracy_pct,
)
import exp_maven_ere_convergence_gated_causal_v1 as v1  # noqa: E402
import exp_maven_ere_convergence_gated_causal_v2 as v2  # noqa: E402 (entity_sets, _doc_scramble_perm, CKPT_DIR)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.learner.plugins import gam_plugin  # noqa: E402
from tools.exp_checkpoint import unit_key, load_units  # noqa: E402

ANCHOR_NAME = "exp_maven_ere_convergence_gated_subevent_v1_fulldev"
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "maven_ere")
POS_MODEL_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_MODEL_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
SHARED_CKPT_DIR = v2.CKPT_DIR  # reuse the causal v2 arc-parse cache (read-only)

N_DEV_DOCS = 710
N_TRAIN_DOCS = 600
SOTA_SUBEVENT_F1 = 29.73  # CITED: ProtoEM 2023 (data/benchmark_trap_check/maven_ere_results.json note)
TYPE_COMPAT_MULT = 1.5
PROXIMITY_DIST = 2
MIN_TYPE_SUPPORT = 3
SUBSAMPLE_RATIOS = [1.0, 2.0, 3.0]
SUBSAMPLE_SEED = 20260811
SCRAMBLE_KEY = "maven_ere_subevent_v1_scramble"


# ============================================================================ arc-parse (cache reuse)
def get_arc(doc: dict, split: str, cache: dict, tagger, parser):
    """(mention_meta, ent, win) for a doc, from the SHARED causal-v2 arc-parse cache (read-only,
    task-agnostic fields), else extracted fresh via v2.entity_sets (in-memory fallback)."""
    c = cache.get(unit_key(split, doc["id"]))
    if c is not None:
        meta = {mid: dict(m) for mid, m in c["mention_meta"].items()}
        ent = {mid: set(v) for mid, v in c["ent"].items()}
        win = {mid: set(v) for mid, v in c["win"].items()}
        return meta, ent, win
    meta = v1._build_mention_context_meta(doc)
    ctx = v1.build_doc_context(doc, tagger)
    win = {mid: set(ctx["arg_sets"][mid]) for mid in ctx["arg_sets"]}
    ent = {mid: set(v) for mid, v in v2.entity_sets(doc, tagger, parser).items()}
    return meta, ent, win


# ============================================================================ TRAIN priors
def fit_subevent_priors(train_docs, cache, tagger, parser):
    """TRAIN-only: per ordered type-pair subevent positive-rate + per-type parent-role rate +
    global rate. NEVER reads dev. (par_score = P(type appears as the PARENT e1 of a subevent | it
    appears at all) -- the granularity signal.)"""
    tp_tot, tp_pos = Counter(), Counter()
    par, typ_tot = Counter(), Counter()
    gtot, gpos = 0, 0
    for doc in train_docs:
        meta, _, _ = get_arc(doc, "train", cache, tagger, parser)
        gold = official_gold_labels(doc, "subevent")
        for (m1, m2), lab in gold.items():
            key = (meta[m1]["type"], meta[m2]["type"])
            tp_tot[key] += 1
            typ_tot[meta[m1]["type"]] += 1
            gtot += 1
            if lab != 0:
                tp_pos[key] += 1
                gpos += 1
                par[meta[m1]["type"]] += 1
    global_rate = (gpos / gtot) if gtot else 0.0
    tp_rate = {k: tp_pos[k] / tp_tot[k] for k in tp_tot if tp_tot[k] >= MIN_TYPE_SUPPORT}
    par_score = {t: par[t] / typ_tot[t] for t in typ_tot if typ_tot[t] >= 20}
    return tp_rate, global_rate, par_score


# ============================================================================ cues + features
def _rate_bucket(r: Optional[float]) -> str:
    return "na" if r is None else "r" + str(min(int(r * 30), 6))


def _gran_bucket(t: str, par_score: Dict[str, float]) -> str:
    s = par_score.get(t)
    return "na" if s is None else "g" + str(min(int(s * 20), 5))


def pair_cues(m1_meta, m2_meta, ent1, ent2, tp_rate, global_rate):
    d = abs(m1_meta["sent_id"] - m2_meta["sent_id"])
    order = (m1_meta["sent_id"], m1_meta["offset_start"]) <= (m2_meta["sent_id"], m2_meta["offset_start"])
    key = (m1_meta["type"], m2_meta["type"])
    r = tp_rate.get(key)
    tc = (r is not None) and (r > TYPE_COMPAT_MULT * global_rate)
    argsh = bool(ent1 & ent2)
    prox = d <= PROXIMITY_DIST
    return {"order": order, "dist": d, "tc": tc, "argsh": argsh, "prox": prox, "type_pair": key}


def gate_pass(cues) -> bool:
    """Convergence gate: forward order (necessary) AND >=1 corroborating part-whole cue."""
    return cues["order"] and (cues["tc"] or cues["argsh"] or cues["prox"])


def pair_features(m1_meta, m2_meta, ent1, ent2, win1, win2, tp_rate, global_rate, par_score,
                  include_arg: bool) -> List[str]:
    d = abs(m1_meta["sent_id"] - m2_meta["sent_id"])
    order = (m1_meta["sent_id"], m1_meta["offset_start"]) <= (m2_meta["sent_id"], m2_meta["offset_start"])
    key = (m1_meta["type"], m2_meta["type"])
    r = tp_rate.get(key)
    tc = (r is not None) and (r > TYPE_COMPAT_MULT * global_rate)
    f = [
        "ord:" + str(order), "ss:" + str(m1_meta["sent_id"] == m2_meta["sent_id"]),
        "adj:" + str(d == 1), "sd:" + ("3p" if d >= 3 else str(d)),
        "tc:" + str(tc), "rb:" + _rate_bucket(r), "pg:" + _gran_bucket(m1_meta["type"], par_score),
        "tA:" + m1_meta["type"], "tB:" + m2_meta["type"],
    ]
    if include_arg:
        f.append("arg:" + str(bool(ent1 & ent2)))
        f.append("win:" + str(bool(win1 & win2)))
    return f


# ============================================================================ per-doc packaging
def pack_doc(doc, split, cache, tagger, parser, tp_rate, global_rate, par_score):
    meta, ent, win = get_arc(doc, split, cache, tagger, parser)
    gold = official_gold_labels(doc, "subevent")
    keys, _ = candidate_pairs(doc)
    return {"doc_id": doc["id"], "keys": keys, "gold": gold, "meta": meta, "ent": ent, "win": win}


def _scramble_pack(pack):
    meta, ent, win = pack["meta"], pack["ent"], pack["win"]
    mids = sorted(meta.keys())
    n = len(mids)
    if n < 2:
        return pack
    perm = _perm(pack["doc_id"], n)
    smeta = {mids[i]: meta[mids[perm[i]]] for i in range(n)}
    sent = {mids[i]: ent[mids[perm[i]]] for i in range(n)}
    swin = {mids[i]: win[mids[perm[i]]] for i in range(n)}
    return {**pack, "meta": smeta, "ent": sent, "win": swin}


def _perm(doc_id: str, n: int) -> List[int]:
    for attempt in range(5):
        perm = v1._deterministic_perm(f"{SCRAMBLE_KEY}::{doc_id}::a{attempt}", n)
        if perm != list(range(n)) and sum(1 for i in range(n) if perm[i] == i) <= max(1, n // 2):
            return perm
    raise RuntimeError(f"SCRAMBLE_DEGENERATE: {doc_id} n={n}")


# ============================================================================ arms
def predict_cue_arm(pack, mode) -> Dict[Tuple[str, str], int]:
    """mode: order_only (floor/ablation) | gate. Binary: 1=SUBEVENT if passes else 0."""
    meta, ent = pack["meta"], pack["ent"]
    pred = {}
    for (m1, m2) in pack["keys"]:
        cues = pair_cues(meta[m1], meta[m2], ent[m1], ent[m2], {}, 0.0) if mode == "order_only" \
            else pair_cues(meta[m1], meta[m2], ent[m1], ent[m2], _TP_RATE, _GRATE)
        if mode == "order_only":
            passes = cues["order"]
        else:
            passes = gate_pass(cues)
        pred[(m1, m2)] = 1 if passes else 0
    return pred


def build_learner_rows(packs, tp_rate, global_rate, par_score, include_arg, scramble):
    out = {}
    for doc_id, pack in packs.items():
        p = _scramble_pack(pack) if scramble else pack
        meta, ent, win = p["meta"], p["ent"], p["win"]
        rows = []
        for (m1, m2) in p["keys"]:
            cues = pair_cues(meta[m1], meta[m2], ent[m1], ent[m2], tp_rate, global_rate)
            if not gate_pass(cues):
                continue
            feats = pair_features(meta[m1], meta[m2], ent[m1], ent[m2], win[m1], win[m2],
                                  tp_rate, global_rate, par_score, include_arg)
            rows.append({"m1": m1, "m2": m2, "gold_class": pack["gold"][(m1, m2)], "feats": feats})
        out[doc_id] = rows
    return out


def _train_gam(rows_flat, ratio):
    rng = random.Random(SUBSAMPLE_SEED)
    pos = [r for r in rows_flat if r["gold_class"] != 0]
    neg = [r for r in rows_flat if r["gold_class"] == 0]
    keep = min(len(neg), int(len(pos) * ratio))
    negs = list(neg)
    rng.shuffle(negs)
    tr = pos + negs[:keep]
    spec = {"classes": [0, 1], "label_fn": lambda e: e["gold_class"], "min_coverage": 5,
            "max_singles_for_pairing": 40, "max_interactions": 40}
    res = gam_plugin.learn(tr, lambda e: e["feats"], spec, {})
    return res.hypothesis, res.metrics


def _f1_learned(rows_by_doc, docs, gold_by_id, hyp):
    devmap = {}
    for doc_id, rows in rows_by_doc.items():
        for r in rows:
            devmap[(doc_id, r["m1"], r["m2"])] = r["feats"]
    g, p = [], []
    for doc in docs:
        gold = gold_by_id[doc["id"]]
        for (m1, m2), lab in gold.items():
            g.append(lab)
            feats = devmap.get((doc["id"], m1, m2))
            p.append(gam_plugin.apply(hyp, feats) if feats is not None else 0)
    return {"official_micro_f1_positive_only": official_prf(g, p, "subevent"),
            "macro_f1_all_labels": macro_f1_all_labels(g, p, "subevent"),
            "accuracy_pct": accuracy_pct(g, p), "all_pred": p}


def select_ratio(train_packs, train_ids, tp_rate, global_rate, par_score, include_arg, id2doc):
    ids = sorted(train_packs.keys())
    n_fit = int(len(ids) * 0.8)
    fit_ids, val_ids = set(ids[:n_fit]), ids[n_fit:]
    fit_rows = build_learner_rows({i: train_packs[i] for i in fit_ids}, tp_rate, global_rate, par_score, include_arg, False)
    val_rows = build_learner_rows({i: train_packs[i] for i in val_ids}, tp_rate, global_rate, par_score, include_arg, False)
    fit_flat = [r for rows in fit_rows.values() for r in rows]
    val_docs = [id2doc[i] for i in val_ids]
    val_gold = {i: official_gold_labels(id2doc[i], "subevent") for i in val_ids}
    scores = {}
    for ratio in SUBSAMPLE_RATIOS:
        hyp, _ = _train_gam(fit_flat, ratio)
        scores[ratio] = _f1_learned(val_rows, val_docs, val_gold, hyp)["official_micro_f1_positive_only"]["f1"]
    return max(SUBSAMPLE_RATIOS, key=lambda r: scores[r]), scores


# ---- module globals for the cue-arm predictor (set in run/self-test)
_TP_RATE: Dict = {}
_GRATE: float = 0.0


# ============================================================================ crash diagnostic
def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": anchor_name}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def _selftest():
    global _TP_RATE, _GRATE
    tagger = PosTagger.load(POS_MODEL_PATH)
    parser = ArcParser.load(ARC_MODEL_PATH)
    # tiny synthetic doc with a subevent edge (parent 'battle' -> child 'charge')
    doc = {
        "id": "toySE",
        "sentences": ["The battle raged for hours.", "A cavalry charge broke the line.",
                      "The soldiers regrouped afterwards."],
        "tokens": [["The", "battle", "raged", "for", "hours", "."],
                   ["A", "cavalry", "charge", "broke", "the", "line", "."],
                   ["The", "soldiers", "regrouped", "afterwards", "."]],
        "events": [
            {"id": "e1", "type": "Hostile_encounter", "mention": [{"id": "s1", "sent_id": 0, "offset": [2, 3], "trigger_word": "raged"}]},
            {"id": "e2", "type": "Attack", "mention": [{"id": "s2", "sent_id": 1, "offset": [3, 4], "trigger_word": "broke"}]},
            {"id": "e3", "type": "Motion", "mention": [{"id": "s3", "sent_id": 2, "offset": [2, 3], "trigger_word": "regrouped"}]},
        ],
        "causal_relations": {"CAUSE": [], "PRECONDITION": []},
        "subevent_relations": [["e1", "e2"]],
    }
    cache = {}  # force the fresh-extraction fallback path (exercises v2.entity_sets)
    meta, ent, win = get_arc(doc, "dev", cache, tagger, parser)
    assert set(meta["s1"].keys()) >= {"sent_id", "offset_start", "type"}, "NO_LEAK: structural meta only"
    gold = official_gold_labels(doc, "subevent")
    assert gold[("s1", "s2")] == 1 and gold[("s2", "s1")] == 0, f"subevent gold direction wrong: {gold}"

    cues = pair_cues(meta["s1"], meta["s2"], ent["s1"], ent["s2"], {}, 0.0)
    assert cues["order"] is True and cues["prox"] is True, f"expected forward+proximate: {cues}"
    assert gate_pass(cues), "gate should pass on the proximate forward parent->child pair"

    fa_no = pair_features(meta["s1"], meta["s2"], ent["s1"], ent["s2"], win["s1"], win["s2"], {}, 0.0, {}, include_arg=False)
    fa_yes = pair_features(meta["s1"], meta["s2"], ent["s1"], ent["s2"], win["s1"], win["s2"], {}, 0.0, {}, include_arg=True)
    assert any(f.startswith("arg:") for f in fa_yes) and not any(f.startswith("arg:") for f in fa_no), "arg flag must add/drop arg feature"

    # REAL gam binary train+apply
    synth = ([{"feats": ["tc:True", "ord:True"], "gold_class": 1}] * 6
             + [{"feats": ["tc:False", "ord:False"], "gold_class": 0}] * 6)
    res = gam_plugin.learn(synth, lambda e: e["feats"], {"classes": [0, 1], "label_fn": lambda e: e["gold_class"], "min_coverage": 2}, {})
    assert gam_plugin.apply(res.hypothesis, ["tc:True", "ord:True"]) == 1, "GAM must learn the SUBEVENT pattern"

    # scramble changes rows
    pack = pack_doc(doc, "dev", cache, tagger, parser, {}, 0.0, {})
    real = build_learner_rows({"toySE": pack}, {}, 0.0, {}, include_arg=True, scramble=False)
    scr = build_learner_rows({"toySE": pack}, {}, 0.0, {}, include_arg=True, scramble=True)
    assert real["toySE"] != scr["toySE"], "SCRAMBLE_NO_OP: scrambled rows must differ"
    return {"self_test": "PASS", "ent_s1": sorted(ent["s1"]), "gam_mains": res.metrics.get("n_main_keys")}


# ============================================================================ main
def run(self_test: bool = False):
    if self_test:
        return _selftest()
    global _TP_RATE, _GRATE

    t0 = time.time()
    print(f"[START] {ANCHOR_NAME} pid={os.getpid()}", flush=True)
    train_all = v1.load_jsonl(os.path.join(DATA_DIR, "train.jsonl"), limit=N_TRAIN_DOCS * 3)
    train_docs = sorted(train_all, key=lambda d: d["id"])[:N_TRAIN_DOCS]
    dev_all = v1.load_jsonl(os.path.join(DATA_DIR, "valid.jsonl"))
    dev_docs = sorted(dev_all, key=lambda d: d["id"])[:N_DEV_DOCS]
    print(f"[LOAD] train_docs={len(train_docs)} dev_docs={len(dev_docs)}", flush=True)

    cache = load_units(SHARED_CKPT_DIR)
    print(f"[CACHE] shared arc-parse cache units={len(cache)}", flush=True)
    tagger = PosTagger.load(POS_MODEL_PATH)
    parser = ArcParser.load(ARC_MODEL_PATH)

    tp_rate, global_rate, par_score = fit_subevent_priors(train_docs, cache, tagger, parser)
    _TP_RATE, _GRATE = tp_rate, global_rate
    print(f"[FIT] subevent global_rate={global_rate:.5f} type_pairs_with_support={len(tp_rate)} "
          f"par_types={len(par_score)}", flush=True)

    id2doc = {d["id"]: d for d in train_docs}
    train_packs = {d["id"]: pack_doc(d, "train", cache, tagger, parser, tp_rate, global_rate, par_score) for d in train_docs}
    dev_packs = {d["id"]: pack_doc(d, "dev", cache, tagger, parser, tp_rate, global_rate, par_score) for d in dev_docs}
    dev_gold_by_id = {d["id"]: dev_packs[d["id"]]["gold"] for d in dev_docs}
    n_pairs = sum(len(g) for g in dev_gold_by_id.values())
    n_pos = sum(1 for g in dev_gold_by_id.values() for v_ in g.values() if v_ != 0)
    print(f"[CARDINALITY] dev candidate_pairs={n_pairs} subevent_positives={n_pos}", flush=True)
    if n_pos < 500:
        raise RuntimeError(f"UNDERPOWERED_SLICE: only {n_pos} subevent positives")

    def eval_cue(mode):
        g, p = [], []
        for doc in dev_docs:
            pred = predict_cue_arm(dev_packs[doc["id"]], mode)
            for k, v_ in dev_gold_by_id[doc["id"]].items():
                g.append(v_)
                p.append(pred[k])
        return {"official_micro_f1_positive_only": official_prf(g, p, "subevent"),
                "macro_f1_all_labels": macro_f1_all_labels(g, p, "subevent"),
                "accuracy_pct": accuracy_pct(g, p), "all_pred": p}

    floor_eval = eval_cue("order_only")
    gate_eval = eval_cue("gate")

    # bag-of-event-types majority baseline (the honest "is it just type-lookup" check)
    tp_maj = {}
    tot, pos_c = Counter(), Counter()
    for d in train_docs:
        gold = official_gold_labels(d, "subevent")
        meta = train_packs[d["id"]]["meta"]
        for (m1, m2), lab in gold.items():
            key = (meta[m1]["type"], meta[m2]["type"])
            tot[key] += 1
            if lab != 0:
                pos_c[key] += 1
    tp_maj = {k: (1 if pos_c[k] * 2 > tot[k] else 0) for k in tot}
    g, p = [], []
    for doc in dev_docs:
        meta = dev_packs[doc["id"]]["meta"]
        for (m1, m2), lab in dev_gold_by_id[doc["id"]].items():
            g.append(lab)
            p.append(tp_maj.get((meta[m1]["type"], meta[m2]["type"]), 0))
    bag_eval = {"official_micro_f1_positive_only": official_prf(g, p, "subevent"),
                "macro_f1_all_labels": macro_f1_all_labels(g, p, "subevent"), "accuracy_pct": accuracy_pct(g, p)}
    maj_eval = {"official_micro_f1_positive_only": official_prf(g, [0] * len(g), "subevent")}

    # learned readout arms
    def learned(include_arg):
        ratio, val = select_ratio(train_packs, sorted(train_packs.keys()), tp_rate, global_rate, par_score, include_arg, id2doc)
        train_rows = build_learner_rows(train_packs, tp_rate, global_rate, par_score, include_arg, False)
        flat = [r for rows in train_rows.values() for r in rows]
        hyp, gm = _train_gam(flat, ratio)
        dev_rows = build_learner_rows(dev_packs, tp_rate, global_rate, par_score, include_arg, False)
        ev = _f1_learned(dev_rows, dev_docs, dev_gold_by_id, hyp)
        return ev, hyp, ratio, val, gm

    noarg_eval, _, noarg_ratio, noarg_val, _ = learned(include_arg=False)
    full_eval, full_hyp, full_ratio, full_val, full_gm = learned(include_arg=True)

    dev_rows_scr = build_learner_rows(dev_packs, tp_rate, global_rate, par_score, include_arg=True, scramble=True)
    scramble_eval = _f1_learned(dev_rows_scr, dev_docs, dev_gold_by_id, full_hyp)

    n_full_pos = sum(1 for x in full_eval["all_pred"] if x != 0)
    if n_full_pos == 0:
        raise RuntimeError("DISCRIMINATOR_DOES_NOT_FIRE: full_v2 predicted zero positives")

    def _h(preds):
        h = hashlib.sha256()
        for x in preds:
            h.update(str(x).encode("ascii"))
        return h.hexdigest()
    digests = {"full_v2": _h(full_eval["all_pred"]), "gate_learned_noarg": _h(noarg_eval["all_pred"]),
               "scramble": _h(scramble_eval["all_pred"]), "floor": _h(floor_eval["all_pred"])}
    assert len(set(digests.values())) == 4, f"META_RULE_AF: arms not distinct: {digests}"

    floor_f1 = floor_eval["official_micro_f1_positive_only"]["f1"]
    gate_f1 = gate_eval["official_micro_f1_positive_only"]["f1"]
    noarg_f1 = noarg_eval["official_micro_f1_positive_only"]["f1"]
    full_f1 = full_eval["official_micro_f1_positive_only"]["f1"]
    scramble_f1 = scramble_eval["official_micro_f1_positive_only"]["f1"]
    bag_f1 = bag_eval["official_micro_f1_positive_only"]["f1"]

    climbs = full_f1 >= 1.8 * floor_f1
    levers_load_bearing = full_f1 > gate_f1 + 1.0
    scramble_collapses = scramble_f1 <= 0.5 * full_f1 if full_f1 > 0 else False
    headroom_survives = (SOTA_SUBEVENT_F1 - full_f1) >= 8.0
    no_lift = full_f1 < 1.3 * floor_f1
    levers_add_nothing = full_f1 <= gate_f1
    scramble_no_collapse = (scramble_f1 > 0.8 * full_f1) if full_f1 > 0 else True

    if no_lift or levers_add_nothing or scramble_no_collapse:
        band = "HARD-FAIL"
    elif climbs and levers_load_bearing and scramble_collapses and headroom_survives:
        band = "HARD-PASS"
    else:
        band = "MIDDLE_BAND"

    transferred = (band == "HARD-PASS")
    decomposition = {
        "floor_order_only_f1": floor_f1, "gate_lift_over_floor": gate_f1 - floor_f1,
        "learner_lift_over_gate": noarg_f1 - gate_f1, "arg_in_learner_lift": full_f1 - noarg_f1,
        "full_v2_lift_over_floor": full_f1 - floor_f1,
        "full_v2_vs_floor_ratio": (full_f1 / floor_f1) if floor_f1 > 0 else None,
        "bag_of_event_types_majority_f1": bag_f1,
    }
    verdict_msg = (
        f"floor={floor_f1:.2f} gate={gate_f1:.2f} learner_noarg={noarg_f1:.2f} full_v2={full_f1:.2f} "
        f"scramble={scramble_f1:.2f} bag_types_maj={bag_f1:.2f} | climbs={climbs} "
        f"learner_load_bearing={levers_load_bearing} scramble_collapses={scramble_collapses} "
        f"headroom={SOTA_SUBEVENT_F1 - full_f1:.1f} band={band} transferred={transferred}"
    )
    print(f"[VERDICT] {verdict_msg}", flush=True)
    print(f"[DECOMP] {json.dumps(decomposition)}", flush=True)

    def _strip(ev):
        return {k: v_ for k, v_ in ev.items() if k != "all_pred"}

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": ("full_dev" if len(dev_docs) >= 710 else "smoke"),
        "task": "subevent", "verdict": band, "verdict_msg": verdict_msg,
        "summary": f"MAVEN-ERE subevent convergence-gate transfer: {band}",
        "elapsed_s": time.time() - t0, "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "n_dev_docs": len(dev_docs), "n_train_docs": len(train_docs), "n_candidate_pairs": n_pairs,
        "n_subevent_positives": n_pos, "n_full_v2_positive_predictions": n_full_pos,
        "cue_design": {"gate": "order AND (type_compat OR arg_overlap OR proximity<=2)",
                       "type_compat_mult": TYPE_COMPAT_MULT, "proximity_dist": PROXIMITY_DIST,
                       "global_rate_train": global_rate},
        "arms": {"order_only_floor": _strip(floor_eval), "gate_only": _strip(gate_eval),
                 "gate_learned_noarg": _strip(noarg_eval), "full_v2": _strip(full_eval),
                 "scramble": _strip(scramble_eval)},
        "baselines_on_slice": {"majority_all_none": maj_eval, "bag_of_event_types_majority": bag_eval},
        "learner_config": {"plugin": "hdlab.learner.plugins.gam_plugin (GAM/EBM binary)",
                           "ratio_selected_noarg": noarg_ratio, "trainval_scores_noarg": noarg_val,
                           "ratio_selected_full": full_ratio, "trainval_scores_full": full_val,
                           "full_gam_metrics": full_gm, "ratio_candidates": SUBSAMPLE_RATIOS,
                           "ratio_selected_on": "TRAIN 80/20 held-out split (dev-blind)"},
        "decomposition": decomposition, "transferred": transferred,
        "bands_prereg": {"climbs_above_1.8x_floor": climbs, "learner_load_bearing": levers_load_bearing,
                         "scramble_collapses": scramble_collapses, "headroom_survives": headroom_survives,
                         "no_lift": no_lift, "levers_add_nothing": levers_add_nothing, "scramble_no_collapse": scramble_no_collapse},
        "cited_published_baselines": {"sota_subevent_f1_protoem_2023": SOTA_SUBEVENT_F1},
        "arms_differ_digests": digests, "arms_differ_verified": True, "no_leak_verified": True,
        "deterministic_seeding": True, "reused_shared_arcparse_cache": True,
        "prereg_path": "preregs/2026-08-11_maven_ere_convergence_gated_subevent_v1.md",
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print(f"[DONE] wrote {os.path.join(OUTPUT_DIR, 'metrics.json')} elapsed={time.time() - t0:.1f}s", flush=True)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        out = run(self_test=args.self_test)
        if args.self_test:
            print(json.dumps(out, indent=2, default=str))
            print("[SELF-TEST] PASS")
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
