# CELL-TEMPLATE MANDATORY (applicable subset; single bounded local pass, not GPU/sweep/multi-seed):
# - arms_differ_verified at final gate (hash real/learned/scramble prediction vectors)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit / KeyboardInterrupt: raise BEFORE except Exception (no bare except:/BaseException)
# - crlb_n/a: official positive-only micro-F1 over a fixed real corpus slice; feasibility = DEV floor
# - calibration_check: adaptive_with_discriminator_gate (GAM subsample ratio selected on a TRAIN
#   held-out split, dev-blind; discriminator-fires = full_v2 fires >0 positive predictions on dev)
# - real_code_path_exercised: self-test loads REAL PosTagger + ArcParser + calls REAL gam_plugin
# - deterministic_seeding: true (hashlib-seeded scramble perm + fixed-seed subsample RNG)
# - no_leak: cue/feature fns take only structural mention-meta + parse args; causal_relations read
#   only by official_gold_labels (eval) + the learner's TRAIN-gold training (train/dev split)
# - resumable: per-doc exp_checkpoint caching of the expensive arc-parse feature rows
# - progress_logging: print_flush_true (heartbeat every 25 docs over the ~800-doc parse loop)
# See preregs/2026-08-11_maven_ere_convergence_gated_causal_v2.md for full pre-reg (bands, arms,
# decomposition, controls, HP_SCOPE, compute architecture).
"""exp_maven_ere_convergence_gated_causal_v2 -- does the convergence-gate approach CLIMB above the
honest order+majority floor (v1 ablation, F1 7.40), or PLATEAU there?

Two brain-foundational levers over the validated v1 convergence gate (reuse owned organs, rule d):
  Lever 1 (entity-continuity cue): per event mention, extract argument-noun lemmas via the OWNED
    glass-box hdlab.arc_parser.ArcParser + hdlab.pos_tagger.PosTagger (syntactic dependents of the
    trigger + nominal head + nominal siblings); cross-event continuity = shared content lemma.
  Lever 2 (learned readout, rule b -- reuse hdlab/learner, do NOT hand-roll): the convergence gate
    proposes a recall-oriented candidate set; a GAM/EBM learned readout (hdlab.learner.plugins.
    gam_plugin -- glass-box additive log-odds shape tables + MDL-gated pairwise interactions)
    decides {NONE, CAUSE, PRECONDITION} per gate-passed pair, learning the precision filter AND the
    CAUSE-vs-PRECOND label from TRAIN cue-patterns. Trained on gate-passed TRAIN pairs with NONE
    subsampled to a balanced ratio selected on a TRAIN held-out split (dev-blind).

Reuses v1's cues/gate verbatim (import, not reimplement). NO LLM, NO nltk, NO torch in the decision
path. stdlib + hdlab.pos_tagger + hdlab.arc_parser + hdlab.learner.plugins.gam_plugin. ASCII-only.
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
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check"))

from maven_ere_official_eval import (  # noqa: E402
    candidate_pairs,
    official_gold_labels,
    official_prf,
    macro_f1_all_labels,
    accuracy_pct,
)
from maven_ere_trap_check import (  # noqa: E402
    fit_majority,
    predict_majority,
    predict_adjacent_sentence_heuristic,
    fit_bag_of_event_types,
    predict_bag_of_event_types,
)
# v1 cue/gate machinery -- imported, NOT reimplemented (rule d: reuse).
import exp_maven_ere_convergence_gated_causal_v1 as v1  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.learner.plugins import gam_plugin  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "exp_maven_ere_convergence_gated_causal_v2_smoke"
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "maven_ere")
POS_MODEL_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_MODEL_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
CKPT_DIR = os.path.join(OUTPUT_DIR, "_rowcache")

N_DEV_DOCS = 200
N_TRAIN_DOCS = 600
SOTA_CAUSAL_F1 = 31.96
SUBSAMPLE_RATIOS = [1.0, 1.5, 2.0]
NOMINAL = {"NOUN", "PROPN"}
SCRAMBLE_KEY = "maven_ere_causal_v2_scramble"
SUBSAMPLE_SEED = 20260811


# ============================================================================ deterministic RNG
def _doc_scramble_perm(doc_id: str, n: int) -> List[int]:
    for attempt in range(5):
        perm = v1._deterministic_perm(f"{SCRAMBLE_KEY}::{doc_id}::a{attempt}", n)
        if perm == list(range(n)):
            continue
        if sum(1 for i in range(n) if perm[i] == i) <= max(1, n // 2):
            return perm
    raise RuntimeError(f"SCRAMBLE_DEGENERATE_AFTER_RETRIES: doc={doc_id} n={n}")


# ============================================================================ arc-parse entity sets
def entity_sets(doc: dict, tagger: PosTagger, parser: ArcParser) -> Dict[str, List[str]]:
    """Per mention_id -> sorted list of argument-noun lemmas (content words) from the arc parse.
    NO-LEAK: reads only tokens/offsets, never causal_relations. Lists (JSON-serializable for the
    per-doc row cache)."""
    meta = v1._build_mention_context_meta(doc)
    tb = doc["tokens"]
    trig_sents = set(m["sent_id"] for m in meta.values())
    parse_cache: Dict[int, Tuple[list, dict]] = {}
    for sid in trig_sents:
        st = tb[sid]
        if not st:
            parse_cache[sid] = ([], {})
            continue
        pos = tagger.tag(st)
        pr = parser.parse(st, pos)
        parse_cache[sid] = (pos, pr.heads)
    out: Dict[str, List[str]] = {}
    for mid, m in meta.items():
        sid = m["sent_id"]
        pos, heads = parse_cache[sid]
        st = tb[sid]
        tidx = m["offset_start"] + 1  # 1-based trigger index
        args: Set[int] = set()
        for i in range(1, len(st) + 1):
            if pos[i - 1] in NOMINAL and heads.get(i) == tidx:
                args.add(i)
        h = heads.get(tidx)
        if h and h != 0 and h <= len(st) and pos[h - 1] in NOMINAL:
            args.add(h)
        if h:
            for i in range(1, len(st) + 1):
                if pos[i - 1] in NOMINAL and heads.get(i) == h and i != tidx:
                    args.add(i)
        lem = sorted(set(st[i - 1].lower() for i in args
                         if len(st[i - 1]) >= 3 and st[i - 1].lower() not in v1.STOPWORDS))
        out[mid] = lem
    return out


# ============================================================================ features
def _rate_bucket(r: Optional[float]) -> str:
    if r is None:
        return "na"
    if r < 0.01:
        return "r0"
    if r < 0.02:
        return "r1"
    if r < 0.04:
        return "r2"
    if r < 0.08:
        return "r3"
    return "r4"


def pair_features(m1_meta: dict, m2_meta: dict, sent_flags, win1: Set[str], win2: Set[str],
                  ent1: Set[str], ent2: Set[str], type_rate_table, global_rate,
                  include_entity: bool) -> List[str]:
    """Glass-box string features for the GAM readout. Reads only structural + parse-derived fields."""
    s1, s2 = m1_meta["sent_id"], m2_meta["sent_id"]
    lo, hi = min(s1, s2), max(s1, s2)
    d = abs(s1 - s2)
    ch = any(sent_flags[i][0] for i in range(lo, hi + 1)) if d <= 1 else False
    ph = any(sent_flags[i][1] for i in range(lo, hi + 1)) if d <= 1 else False
    order = (s1, m1_meta["offset_start"]) <= (s2, m2_meta["offset_start"])
    winshare = bool(win1 & win2)
    entshare = bool(ent1 & ent2)
    key = (m1_meta["type"], m2_meta["type"])
    r = type_rate_table.get(key)
    tc = (r is not None) and (r > v1.TYPE_COMPAT_MULT * global_rate)
    f = [
        "cc:" + str(ch), "pc:" + str(ph), "ord:" + str(order),
        "win:" + str(winshare), "ss:" + str(s1 == s2), "adj:" + str(d == 1),
        "sd:" + ("3p" if d >= 3 else str(d)), "tc:" + str(tc), "rb:" + _rate_bucket(r),
        "tA:" + m1_meta["type"], "tB:" + m2_meta["type"],
    ]
    if include_entity:
        f.append("ent:" + str(entshare))
    return f


# ============================================================================ per-doc extraction (cached)
def extract_doc_rows(doc: dict, tagger: PosTagger, parser: ArcParser, type_rate_table,
                     global_rate) -> dict:
    """All gate-passed candidate pairs for a doc, with their cues + feature strings + gold + the
    per-mention window/entity sets (for scramble). JSON-serializable for the row cache."""
    gold = official_gold_labels(doc, "causal")
    meta = v1._build_mention_context_meta(doc)
    sent_flags = v1._sentence_connective_flags(doc["sentences"])
    ctx = v1.build_doc_context(doc, tagger)  # window arg sets + sent_flags
    win = ctx["arg_sets"]
    ent = entity_sets(doc, tagger, parser)
    keys, _ = candidate_pairs(doc)
    rows = []
    for (m1, m2) in keys:
        cues = v1._pair_cues(meta[m1], meta[m2], sent_flags, win[m1], win[m2],
                             type_rate_table, global_rate)
        rows.append({
            "m1": m1, "m2": m2, "gold": gold[(m1, m2)],
            "n_other_fired": cues["n_other_fired"], "cue_order": cues["cue_order"],
            "cause_hit": cues["cause_hit"], "precond_hit": cues["precond_hit"],
            "type_pair": list(cues["type_pair"]),
        })
    # per-mention structural evidence kept for scramble + feature recomputation
    mmeta = {mid: meta[mid] for mid in meta}
    return {
        "doc_id": doc["id"], "rows": rows, "sent_flags": sent_flags,
        "mention_meta": mmeta, "win": {mid: sorted(win[mid]) for mid in win}, "ent": ent,
    }


def get_doc_extractions(docs, split, tagger, parser, type_rate_table, global_rate, t0):
    """Resumable per-doc extraction via exp_checkpoint. Returns {doc_id: extraction}."""
    done = completed_units(CKPT_DIR)
    for i, doc in enumerate(docs):
        k = unit_key(split, doc["id"])
        if k in done:
            continue
        ext = extract_doc_rows(doc, tagger, parser, type_rate_table, global_rate)
        record_unit(CKPT_DIR, k, ext)
        if (i + 1) % 25 == 0:
            print(f"[EXTRACT-{split}] {i + 1}/{len(docs)} docs elapsed={time.time() - t0:.1f}s", flush=True)
    loaded = load_units(CKPT_DIR)
    out = {}
    for doc in docs:
        out[doc["id"]] = loaded[unit_key(split, doc["id"])]
    return out


# ============================================================================ cue-arm predictions
def _decide_label_from_row(row: dict, majority_table, global_majority) -> int:
    if row["cause_hit"]:
        return 2
    if row["precond_hit"]:
        return 1
    return majority_table.get(tuple(row["type_pair"]), global_majority)


def predict_cue_arm(ext: dict, gate: str, majority_table, global_majority,
                    ent_map: Dict[str, Set[str]]) -> Dict[Tuple[str, str], int]:
    """gate in {order_only, gate, gate_entity}. Returns {(m1,m2): label} over ALL candidate pairs."""
    pred = {}
    for row in ext["rows"]:
        m1, m2 = row["m1"], row["m2"]
        if gate == "order_only":
            passes = row["cue_order"]
        elif gate == "gate":
            passes = row["cue_order"] and (row["n_other_fired"] >= 1)
        elif gate == "gate_entity":
            entshare = bool(ent_map[m1] & ent_map[m2])
            passes = row["cue_order"] and ((row["n_other_fired"] + int(entshare)) >= 1)
        else:
            raise ValueError(gate)
        pred[(m1, m2)] = _decide_label_from_row(row, majority_table, global_majority) if passes else 0
    return pred


# ============================================================================ learned-readout arms
def _gate_passed(row: dict) -> bool:
    return row["cue_order"] and (row["n_other_fired"] >= 1)


def build_learner_rows(extractions: Dict[str, dict], type_rate_table, global_rate,
                       include_entity: bool, scramble: bool) -> Dict[str, List[dict]]:
    """For each doc: gate-passed rows with feature strings + gold. If scramble, per-doc permute the
    mention -> (meta, win, ent) identity before computing features (gold stays on real pairs)."""
    out: Dict[str, List[dict]] = {}
    for doc_id, ext in extractions.items():
        meta = ext["mention_meta"]
        win = {mid: set(ext["win"][mid]) for mid in ext["win"]}
        ent = {mid: set(ext["ent"][mid]) for mid in ext["ent"]}
        sent_flags = ext["sent_flags"]
        if scramble:
            mids = sorted(meta.keys())
            n = len(mids)
            if n >= 2:
                perm = _doc_scramble_perm(doc_id, n)
                meta = {mids[i]: meta[mids[perm[i]]] for i in range(n)}
                win = {mids[i]: win[mids[perm[i]]] for i in range(n)}
                ent = {mids[i]: ent[mids[perm[i]]] for i in range(n)}
        doc_rows = []
        for row in ext["rows"]:
            if not _gate_passed(row):
                continue
            m1, m2 = row["m1"], row["m2"]
            feats = pair_features(meta[m1], meta[m2], sent_flags, win[m1], win[m2],
                                  ent[m1], ent[m2], type_rate_table, global_rate, include_entity)
            doc_rows.append({"m1": m1, "m2": m2, "gold_class": row["gold"], "feats": feats})
        out[doc_id] = doc_rows
    return out


def _train_gam(train_rows_flat: List[dict], ratio: float):
    rng = random.Random(SUBSAMPLE_SEED)
    pos = [r for r in train_rows_flat if r["gold_class"] != 0]
    neg = [r for r in train_rows_flat if r["gold_class"] == 0]
    keep = min(len(neg), int(len(pos) * ratio))
    negs = list(neg)
    rng.shuffle(negs)
    tr = pos + negs[:keep]
    spec = {"classes": [0, 1, 2], "label_fn": lambda e: e["gold_class"],
            "min_coverage": 5, "max_singles_for_pairing": 40, "max_interactions": 40}
    res = gam_plugin.learn(tr, lambda e: e["feats"], spec, {})
    return res.hypothesis, res.metrics


def _f1_on(rows_by_doc: Dict[str, List[dict]], docs, dev_gold_by_id, hyp) -> dict:
    devmap = {}
    for doc_id, rows in rows_by_doc.items():
        for r in rows:
            devmap[(doc_id, r["m1"], r["m2"])] = r["feats"]
    all_gold, all_pred = [], []
    for doc in docs:
        gold = dev_gold_by_id[doc["id"]]
        for (m1, m2), g in gold.items():
            all_gold.append(g)
            feats = devmap.get((doc["id"], m1, m2))
            all_pred.append(gam_plugin.apply(hyp, feats) if feats is not None else 0)
    return {
        "official_micro_f1_positive_only": official_prf(all_gold, all_pred, "causal"),
        "macro_f1_all_labels": macro_f1_all_labels(all_gold, all_pred, "causal"),
        "accuracy_pct": accuracy_pct(all_gold, all_pred),
        "all_pred": all_pred,
    }


def select_ratio_on_train(train_ext: Dict[str, dict], train_docs, type_rate_table, global_rate,
                          include_entity: bool) -> Tuple[float, dict]:
    """Dev-blind operating-point selection: split TRAIN docs 80/20 by deterministic id sort, fit at
    each ratio on the 80, pick the ratio maximizing positive-only F1 on the 20 held-out TRAIN docs."""
    ids = sorted(train_ext.keys())
    n_fit = int(len(ids) * 0.8)
    fit_ids, val_ids = set(ids[:n_fit]), ids[n_fit:]
    fit_ext = {i: train_ext[i] for i in train_ext if i in fit_ids}
    val_ext = {i: train_ext[i] for i in train_ext if i in val_ids}
    fit_rows = build_learner_rows(fit_ext, type_rate_table, global_rate, include_entity, scramble=False)
    val_rows = build_learner_rows(val_ext, type_rate_table, global_rate, include_entity, scramble=False)
    fit_flat = [r for rows in fit_rows.values() for r in rows]
    val_gold = {i: official_gold_labels(_id2doc[i], "causal") for i in val_ids}
    val_docs = [_id2doc[i] for i in val_ids]
    scores = {}
    for ratio in SUBSAMPLE_RATIOS:
        hyp, _ = _train_gam(fit_flat, ratio)
        f1 = _f1_on(val_rows, val_docs, val_gold, hyp)["official_micro_f1_positive_only"]["f1"]
        scores[ratio] = f1
    best = max(SUBSAMPLE_RATIOS, key=lambda r: scores[r])
    return best, scores


_id2doc: Dict[str, dict] = {}  # populated in run() for the train-val split helper


# ============================================================================ crash diagnostic
def _write_crash_metrics(output_dir: str, anchor_name: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def _selftest() -> dict:
    tagger = PosTagger.load(POS_MODEL_PATH)
    parser = ArcParser.load(ARC_MODEL_PATH)
    assert isinstance(tagger, PosTagger) and isinstance(parser, ArcParser), "REAL_CODE_PATH"
    doc_a = {
        "id": "toyA",
        "sentences": ["The storm hit the coast.", "The village flooded because of the storm."],
        "tokens": [["The", "storm", "hit", "the", "coast", "."],
                   ["The", "village", "flooded", "because", "of", "the", "storm", "."]],
        "events": [
            {"id": "e1", "type": "Impact", "mention": [{"id": "a1", "sent_id": 0, "offset": [2, 3], "trigger_word": "hit"}]},
            {"id": "e2", "type": "Flood", "mention": [{"id": "a2", "sent_id": 1, "offset": [2, 3], "trigger_word": "flooded"}]},
        ],
        "causal_relations": {"CAUSE": [["e1", "e2"]], "PRECONDITION": []},
        "subevent_relations": [],
    }
    ent = entity_sets(doc_a, tagger, parser)
    assert "a1" in ent and "a2" in ent, f"entity extraction must cover both mentions, got {ent}"
    ext = extract_doc_rows(doc_a, tagger, parser, {}, 0.0)
    assert any(r["gold"] == 2 for r in ext["rows"]), "toyA must contain the gold CAUSE pair"
    assert set(ext["mention_meta"]["a1"].keys()) == {"sent_id", "offset_start", "offset_end", "trigger", "type"}, (
        "NO_LEAK: mention-meta must carry only structural fields")

    # feature vectors differ with/without entity flag
    meta = ext["mention_meta"]
    fa_no = pair_features(meta["a1"], meta["a2"], ext["sent_flags"], set(ext["win"]["a1"]),
                          set(ext["win"]["a2"]), set(ext["ent"]["a1"]), set(ext["ent"]["a2"]),
                          {}, 0.0, include_entity=False)
    fa_yes = pair_features(meta["a1"], meta["a2"], ext["sent_flags"], set(ext["win"]["a1"]),
                           set(ext["win"]["a2"]), set(ext["ent"]["a1"]), set(ext["ent"]["a2"]),
                           {}, 0.0, include_entity=True)
    assert any(f.startswith("ent:") for f in fa_yes) and not any(f.startswith("ent:") for f in fa_no), (
        "entity feature flag must add/drop the ent: feature")

    # REAL gam_plugin train + apply on a tiny 3-class synthetic set (exercises the learner path).
    synth = ([{"feats": ["cc:True", "ss:True"], "gold_class": 2}] * 6
             + [{"feats": ["pc:True", "adj:True"], "gold_class": 1}] * 6
             + [{"feats": ["cc:False", "ss:False"], "gold_class": 0}] * 6)
    spec = {"classes": [0, 1, 2], "label_fn": lambda e: e["gold_class"], "min_coverage": 2}
    res = gam_plugin.learn(synth, lambda e: e["feats"], spec, {})
    assert gam_plugin.apply(res.hypothesis, ["cc:True", "ss:True"]) == 2, "GAM must learn CAUSE pattern"
    assert gam_plugin.apply(res.hypothesis, ["pc:True", "adj:True"]) == 1, "GAM must learn PRECOND pattern"

    # scramble changes learner rows on a 2-mention doc
    real_rows = build_learner_rows({"toyA": ext}, {}, 0.0, include_entity=True, scramble=False)
    scr_rows = build_learner_rows({"toyA": ext}, {}, 0.0, include_entity=True, scramble=True)
    assert real_rows["toyA"] != scr_rows["toyA"], "SCRAMBLE_NO_OP: scrambled learner rows must differ"

    return {"self_test": "PASS", "entity_a1": ent["a1"], "entity_a2": ent["a2"],
            "gam_mains": res.metrics.get("n_main_keys")}


# ============================================================================ main
def run(self_test: bool = False):
    if self_test:
        return _selftest()

    t0 = time.time()
    print(f"[START] {ANCHOR_NAME} pid={os.getpid()}", flush=True)

    train_all = v1.load_jsonl(os.path.join(DATA_DIR, "train.jsonl"), limit=N_TRAIN_DOCS * 3)
    train_docs = sorted(train_all, key=lambda d: d["id"])[:N_TRAIN_DOCS]
    dev_all = v1.load_jsonl(os.path.join(DATA_DIR, "valid.jsonl"))
    dev_docs = sorted(dev_all, key=lambda d: d["id"])[:N_DEV_DOCS]
    print(f"[LOAD] train_docs={len(train_docs)} dev_docs={len(dev_docs)}", flush=True)

    global _id2doc
    _id2doc = {d["id"]: d for d in train_docs}

    tagger = PosTagger.load(POS_MODEL_PATH)
    parser = ArcParser.load(ARC_MODEL_PATH)

    type_rate_table, global_rate, majority_table, global_majority = v1.fit_type_pair_table(train_docs)
    train_gold = [official_gold_labels(d, "causal") for d in train_docs]
    maj_label, _ = fit_majority(train_gold)
    bag_table, bag_fallback, _ = fit_bag_of_event_types(train_docs, train_gold)

    dev_gold_by_id = {d["id"]: official_gold_labels(d, "causal") for d in dev_docs}
    n_pairs = sum(len(g) for g in dev_gold_by_id.values())
    n_gold_pos = sum(1 for g in dev_gold_by_id.values() for v_ in g.values() if v_ != 0)
    print(f"[CARDINALITY] dev candidate_pairs={n_pairs} gold_positives={n_gold_pos}", flush=True)
    if n_gold_pos < 500:
        raise RuntimeError(f"UNDERPOWERED_SLICE: only {n_gold_pos} gold positives (< 500)")

    # ---------------------------------------------------- per-doc extraction (resumable)
    print("[EXTRACT] building per-doc cue+feature rows (arc-parse; cached/resumable)...", flush=True)
    train_ext = get_doc_extractions(train_docs, "train", tagger, parser, type_rate_table, global_rate, t0)
    dev_ext = get_doc_extractions(dev_docs, "dev", tagger, parser, type_rate_table, global_rate, t0)
    print(f"[EXTRACT] done elapsed={time.time() - t0:.1f}s", flush=True)

    def eval_pred(pred_by_pair) -> dict:
        all_gold, all_pred = [], []
        for doc in dev_docs:
            g = dev_gold_by_id[doc["id"]]
            for k, v_ in g.items():
                all_gold.append(v_)
                all_pred.append(pred_by_pair[doc["id"]][k])
        return {
            "official_micro_f1_positive_only": official_prf(all_gold, all_pred, "causal"),
            "macro_f1_all_labels": macro_f1_all_labels(all_gold, all_pred, "causal"),
            "accuracy_pct": accuracy_pct(all_gold, all_pred),
        }

    dev_ent_map = {doc_id: {mid: set(ext["ent"][mid]) for mid in ext["ent"]} for doc_id, ext in dev_ext.items()}

    # ---------------------------------------------------- cue arms
    def cue_arm(gate):
        return {doc_id: predict_cue_arm(dev_ext[doc_id], gate, majority_table, global_majority,
                                        dev_ent_map[doc_id]) for doc_id in dev_ext}
    floor_eval = eval_pred(cue_arm("order_only"))
    gate_eval = eval_pred(cue_arm("gate"))
    gate_entity_eval = eval_pred(cue_arm("gate_entity"))

    # ---------------------------------------------------- baselines on slice
    baselines = {
        "majority": eval_pred({d["id"]: predict_majority(d, maj_label) for d in dev_docs}),
        "adjacent_sentence_heuristic": eval_pred({d["id"]: predict_adjacent_sentence_heuristic(d) for d in dev_docs}),
        "bag_of_event_types": eval_pred({d["id"]: predict_bag_of_event_types(d, bag_table, bag_fallback) for d in dev_docs}),
    }

    # ---------------------------------------------------- learned-readout arms
    def learned_arm(include_entity: bool):
        ratio, val_scores = select_ratio_on_train(train_ext, train_docs, type_rate_table, global_rate, include_entity)
        train_rows = build_learner_rows(train_ext, type_rate_table, global_rate, include_entity, scramble=False)
        train_flat = [r for rows in train_rows.values() for r in rows]
        hyp, gam_metrics = _train_gam(train_flat, ratio)
        dev_rows = build_learner_rows(dev_ext, type_rate_table, global_rate, include_entity, scramble=False)
        ev = _f1_on(dev_rows, dev_docs, dev_gold_by_id, hyp)
        return ev, hyp, ratio, val_scores, gam_metrics

    noentity_eval, _, noent_ratio, noent_val, _ = learned_arm(include_entity=False)
    full_eval, full_hyp, full_ratio, full_val, full_gam_metrics = learned_arm(include_entity=True)

    # ---------------------------------------------------- scramble control (full_v2, scrambled dev)
    dev_rows_scr = build_learner_rows(dev_ext, type_rate_table, global_rate, include_entity=True, scramble=True)
    scramble_eval = _f1_on(dev_rows_scr, dev_docs, dev_gold_by_id, full_hyp)

    # discriminator-fires + arms-differ
    n_full_pos = sum(1 for p in full_eval["all_pred"] if p != 0)
    if n_full_pos == 0:
        raise RuntimeError("DISCRIMINATOR_DOES_NOT_FIRE: full_v2 predicted zero positives")

    def _hash(preds):
        h = hashlib.sha256()
        for p in preds:
            h.update(str(p).encode("ascii"))
        return h.hexdigest()
    digests = {"full_v2": _hash(full_eval["all_pred"]),
               "gate_learned_noentity": _hash(noentity_eval["all_pred"]),
               "scramble": _hash(scramble_eval["all_pred"])}
    assert len(set(digests.values())) == 3, f"META_RULE_AF: arms not distinct: {digests}"

    # ---------------------------------------------------- bands
    floor_f1 = floor_eval["official_micro_f1_positive_only"]["f1"]
    gate_f1 = gate_eval["official_micro_f1_positive_only"]["f1"]
    gate_entity_f1 = gate_entity_eval["official_micro_f1_positive_only"]["f1"]
    noent_f1 = noentity_eval["official_micro_f1_positive_only"]["f1"]
    full_f1 = full_eval["official_micro_f1_positive_only"]["f1"]
    scramble_f1 = scramble_eval["official_micro_f1_positive_only"]["f1"]
    best_base = max(v_["official_micro_f1_positive_only"]["f1"] for v_ in baselines.values())

    climbs = full_f1 >= 1.8 * floor_f1
    levers_load_bearing = full_f1 > gate_f1 + 1.0
    scramble_collapses = scramble_f1 <= 0.5 * full_f1 if full_f1 > 0 else False
    headroom_survives = (SOTA_CAUSAL_F1 - full_f1) >= 8.0

    no_lift = full_f1 < 1.3 * floor_f1
    levers_add_nothing = full_f1 <= gate_f1
    scramble_no_collapse = (scramble_f1 > 0.8 * full_f1) if full_f1 > 0 else True

    if no_lift or levers_add_nothing or scramble_no_collapse:
        band = "HARD-FAIL"
    elif climbs and levers_load_bearing and scramble_collapses and headroom_survives:
        band = "HARD-PASS"
    else:
        band = "MIDDLE_BAND"

    decomposition = {
        "floor_order_majority_f1": floor_f1,
        "gate_lift_over_floor": gate_f1 - floor_f1,
        "lever1_gatecue_lift_over_gate": gate_entity_f1 - gate_f1,
        "lever2_learner_lift_over_gate": noent_f1 - gate_f1,
        "lever1_in_learner_lift": full_f1 - noent_f1,
        "full_v2_lift_over_floor": full_f1 - floor_f1,
        "full_v2_vs_floor_ratio": (full_f1 / floor_f1) if floor_f1 > 0 else None,
    }
    verdict_msg = (
        f"floor={floor_f1:.2f} gate={gate_f1:.2f} gate+entity={gate_entity_f1:.2f} "
        f"learner_noent={noent_f1:.2f} full_v2={full_f1:.2f} scramble={scramble_f1:.2f} "
        f"best_base={best_base:.2f} | climbs={climbs} levers_load_bearing={levers_load_bearing} "
        f"scramble_collapses={scramble_collapses} headroom={SOTA_CAUSAL_F1 - full_f1:.1f} band={band}"
    )
    print(f"[VERDICT] {verdict_msg}", flush=True)
    print(f"[DECOMP] {json.dumps(decomposition)}", flush=True)

    def _strip(ev):
        return {k: v_ for k, v_ in ev.items() if k != "all_pred"}

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": "smoke", "verdict": band, "verdict_msg": verdict_msg,
        "summary": f"MAVEN-ERE convergence-gate v2 climb-or-plateau: {band}",
        "elapsed_s": time.time() - t0, "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "n_dev_docs": len(dev_docs), "n_train_docs": len(train_docs),
        "n_candidate_pairs": n_pairs, "n_gold_positives": n_gold_pos, "n_full_v2_positive_predictions": n_full_pos,
        "arms": {
            "order_majority_floor": floor_eval, "gate_only": gate_eval, "gate_plus_entity": gate_entity_eval,
            "gate_learned_noentity": _strip(noentity_eval), "full_v2": _strip(full_eval),
            "scramble": _strip(scramble_eval),
        },
        "baselines_on_slice": baselines,
        "learner_config": {
            "plugin": "hdlab.learner.plugins.gam_plugin (GAM/EBM, glass-box additive log-odds + MDL pairwise interactions)",
            "subsample_ratio_selected_noentity": noent_ratio, "trainval_scores_noentity": noent_val,
            "subsample_ratio_selected_full": full_ratio, "trainval_scores_full": full_val,
            "full_gam_metrics": full_gam_metrics, "ratio_candidates": SUBSAMPLE_RATIOS,
            "ratio_selected_on": "TRAIN 80/20 held-out split (dev-blind)",
        },
        "decomposition": decomposition,
        "bands_prereg": {
            "climbs_above_1.8x_floor": climbs, "levers_load_bearing": levers_load_bearing,
            "scramble_collapses": scramble_collapses, "headroom_survives": headroom_survives,
            "no_lift": no_lift, "levers_add_nothing": levers_add_nothing, "scramble_no_collapse": scramble_no_collapse,
        },
        "cited_published_baselines": {"sota_causal_f1_protoem_2023": SOTA_CAUSAL_F1},
        "arms_differ_digests": digests, "arms_differ_verified": True, "no_leak_verified": True,
        "deterministic_seeding": True, "resumable_rowcache": True,
        "prereg_path": "preregs/2026-08-11_maven_ere_convergence_gated_causal_v2.md",
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
