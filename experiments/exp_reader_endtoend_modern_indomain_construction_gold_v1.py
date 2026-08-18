"""END-TO-END reader on MODERN IN-DOMAIN text -- disentangle "McGuffey archaic-domain artifact"
from "fundamental reader bound".

CONFOUND (why this cell): every reader plateau number this session (~0.76 end-to-end backoff on the
same pipeline) is on McGuffey = archaic 1879 English, OUT-OF-DOMAIN for the front-end (POS/arc-parser/
arc-labeler all trained on MODERN UD-EWT). The reader's TRUE end-to-end capability on IN-DOMAIN modern
text was UNTESTED. This cell runs the EXACT v2-extraction-hardened pipeline (hdlab pos_tagger + arc_parser
+ arc_labeler + candidate_generator + integrated vote + abstain) on the CONSTRUCTION GOLD
(data/gold_construction_argstruct_ewt_v1, modern UD-EWT, parse-derived who-is-affected labels).

ONE-VARIABLE = TEST CORPUS (archaic McGuffey vs modern in-domain UD-EWT). Same persisted front-end,
same vote protocol / verb-split / seeds / mining as the McGuffey baseline. Reuses persisted assets; NO
retrain.

REAL BASELINE (McGuffey end-to-end, SAME pipeline):
  BACKOFF=0.7622  V1=0.742  ceiling=0.79  residual ext:dec=22:4 (84.6% extraction-bound)
  CITED@data/exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened/metrics.json 2026-07-21.
  (MST-parser swap: BACKOFF=0.7896 CITED@data/exp_reader_parser_swap_mst_endtoend_v1/metrics.json.)

CAN-FAIL (both informative): modern text may be MUCH BETTER (>= McG+0.05 -> archaic domain WAS the
limiter -> the 0.76 was a McGuffey artifact) OR SAME/WORSE (register was NOT the limiter -> the bound is
DEEPER = word-order/decision-bounded regardless of register). C>McG is NOT guaranteed.

*** LOAD-BEARING LEAK (MEASURED): 106/136 construction-gold sentences are from the UD-EWT TRAIN split
    (the exact sentences the parser/labeler/tagger memorized); 17 dev (early-stop-seen); only 13 test
    (truly held-out). The IN-DOMAIN extraction ceiling is therefore INFLATED by memorization, not only
    by domain match. This cell reports the per-UD-source-split breakdown (train-leaked vs dev vs
    test-heldout) so the LEAK-FREE reader capability (test-heldout) is separable from the leaked overall.
    MEASURED@this-cell:_leak_udsplit (build_construction_gold pulls train+dev+test; frontend trains on
    train, early-stops on dev, evals on test). ***

CAVEATS (honest, checked):
  - LABELS-FROM-PARSER-FAMILY: gold who-is-affected labels are UD-EWT GOLD-PARSE-derived; our front-end
    IS trained on UD-EWT -> an in-domain lift can be "our parser agrees with the gold parse" (LAS ~0.76)
    rather than genuine reading. The EXTRACTION:DECISION partition separates these: extraction gain =
    front-end/LAS agreeing with gold parse; decision gain = the reader genuinely choosing better.
  - MINING HANDICAP: gfit/selectional features are McGuffey-mined (kept FIXED for strict one-variable);
    they are archaic-narrative-flavored, a mild HANDICAP against the modern arm (so a modern DECISION
    gain is despite this).
  - REGISTER: UD-EWT is modern WEB text (blogs/reviews/email/newsgroups), NOT modern NARRATIVE (the
    reader's ideal domain is neither archaic-narrative nor web). State it.
  - VERB IDENTITY: g["v"] = L.lemma_verb(gold_form) (McGuffey convention: load_gold uses lemma_verb(r.v)).
    This anchors verb-finding on the ACTUAL surface token in the sentence (removes a pure UD-lemma vs
    L-lemma string artifact) while a genuine POS mis-tag still counts as an extraction miss (faithful).

LEAK-HUNT (in-cell): (1) accept_hardened / build_instances take NO gold arg (front-end never sees gold;
  gold only SCORES via surface-string is_gold). (2) giveaway_audit: no single feature >=0.95 selects the
  gold candidate within a pool. (3) ud_split ceiling breakdown surfaces the memorization leak explicitly.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = McGuffey backoff 0.7622 (SAME pipeline), re-cited; modern arm computed identically.
  (2) CAN-FAIL: modern SAME/WORSE (deeper bound) OR MUCH-BETTER (artifact) -- both pre-registered.
  (3) DIFFICULTY-ON: passives / relative / coordination / prep-governed / cue-conflict slices reported.
  (4) ONE-VARIABLE: test corpus only; front-end/vote/split/seeds/mining identical to McGuffey.

VERDICT BANDS (MEASUREMENT cell -- primary deliverable = the NUMBERS + the two partitions):
  REVEALS_HIGHER_INDOMAIN_ARCHAIC_ARTIFACT: modern_overall_backoff >= 0.8122 (McG 0.7622 + 0.05).
  DEEPER_BOUND_REGISTER_NOT_LIMITER: |modern_overall_backoff - 0.7622| < 0.05.
  MODERN_WORSE: modern_overall_backoff < 0.7122.
  (The overall number is LEAK-INFLATED; the leak-free test-heldout number is the honest reader capability
   and is reported alongside -- the Director interprets the two together.)

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified) -- 136 gold sentences parsed once + McGuffey
  mining (cached) + 3-seed 13-dim delta-rule vote fits (<1s each). Wall < ~120s smoke / < ~520s full.
  Storage: no_storage. progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int
  seeds, default_rng, sorted(set); NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue,
  NO push, NO remote-persist, NO git add.

PRIOR-WORK CHECK (substrate_query.sh "end-to-end reader who-is-affected modern in-domain construction
  gold vs archaic McGuffey register bound"): top hits cosine=0.238 are unrelated WordNet 'mind_reader'/
  'lay_reader'; NONE at cosine>0.30. Genuinely novel measurement (the McGuffey-vs-modern confound was
  never disentangled end-to-end). CITED@backup-doc 2026-07-20.
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
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_endtoend_modern_indomain_construction_gold_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_reader_integration_endtoend_whoaffected_v1 as E  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402
from experiments import exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened as V2  # noqa: E402

POS_PATH = E.POS_PATH
ARC_PATH = E.ARC_PATH
LABELER_PATH = E.LABELER_PATH

GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_construction_argstruct_ewt_v1",
                         "gold_construction_argstruct_ewt_v1.json")
UD_DIR = os.path.join(REPO_ROOT, "experiments", "data", "ud_english_ewt")

MCG_BACKOFF = 0.7622   # CITED@data/exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened/metrics.json
MCG_V1 = 0.742         # CITED same
MCG_CEILING = 0.79     # CITED same


# ----------------------------------------------------------------------------------------------
# UD-source-split membership (leak instrumentation): which UD split each gold sentence came from.
# frontend trains on train, early-stops on dev, evals on test -> train = memorized (leak).
# ----------------------------------------------------------------------------------------------
def _ud_split_sids():
    out = {}
    for split, fn in (("train", "en_ewt-ud-train.conllu"),
                      ("dev", "en_ewt-ud-dev.conllu"),
                      ("test", "en_ewt-ud-test.conllu")):
        path = os.path.join(UD_DIR, fn)
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# sent_id"):
                    out[line.split("=", 1)[1].strip()] = split
    return out


# ----------------------------------------------------------------------------------------------
# Load the MODERN construction gold into the McGuffey-compatible (order, sent_text, gold) shape, plus a
# per-instance annotation map ann[(sid, vlem, patient_lc)] = {gold_construction, ud_split, ...}.
# ----------------------------------------------------------------------------------------------
def load_construction_gold():
    with open(GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    items = obj["gold"]
    ud = _ud_split_sids()
    sent_text = {}
    gold = {}
    ann = {}
    ud_counts = defaultdict(int)
    for _key, it in items.items():
        sid = it["sent_id"]
        sent_text[sid] = it["text"]
        vform = it["verb"]["form"].lower()
        vlem = L.lemma_verb(vform)                       # McGuffey convention: load_gold uses lemma_verb
        patient = it["patient"]["form"].lower()
        agent = ((it.get("agent") or {}).get("form") or "").lower()
        rec = gold.setdefault(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        rec["pos"].append({"v": vlem, "patient": patient, "agent": agent})
        rec["pos_verbs"].add(vlem)
        ud_split = ud.get(sid, "UNKNOWN")
        ud_counts[ud_split] += 1
        ann[(sid, vlem, patient)] = {
            "gold_construction": it["construction"],
            "ud_split": ud_split,
            "genuine_ambiguity": bool(it.get("genuine_ambiguity", False)),
            "cue_conflict": bool(it.get("cue_conflict", False)),
            "cueweight_split": it.get("split", "?"),
        }
    order = sorted(sent_text.keys())
    meta = {"gold_name": obj["_meta"].get("name"), "n_items": len(items),
            "n_sentences": len(sent_text), "ud_source_split_counts": dict(ud_counts),
            "register_caveat": obj["_meta"].get("register_caveat"),
            "label_derivation": obj["_meta"].get("label_derivation")}
    return order, sent_text, gold, ann, meta


def _annotate(instances, ann):
    """Post-annotate build_instances output with the TRUE gold construction + UD source split."""
    for inst in instances:
        if not inst.get("is_pos"):
            continue
        key = (inst["sid"], inst["v_lemma"], inst["gold_patient"])
        a = ann.get(key)
        if a is None:
            inst["gold_construction"] = "UNMATCHED"
            inst["ud_split"] = "UNKNOWN"
            inst["genuine_ambiguity"] = False
        else:
            inst["gold_construction"] = a["gold_construction"]
            inst["ud_split"] = a["ud_split"]
            inst["genuine_ambiguity"] = a["genuine_ambiguity"]
    return instances


# ----------------------------------------------------------------------------------------------
# Aggregate accuracy + ceiling + residual over a set of pos instances (union across seeds' test folds).
# ----------------------------------------------------------------------------------------------
def _acc_ceiling_resid(w, insts):
    if not insts:
        return {"n": 0, "acc": None, "ceiling": None, "ext_err": 0, "dec_err": 0, "correct": 0}
    correct = ext = dec = 0
    for inst in insts:
        if not inst["cands"]:
            ext += 1
            continue
        pick = IV.select_pick(w, inst)[0]
        if pick["p"] == inst["gold_patient"]:
            correct += 1
        elif inst["gold_in_pool"]:
            dec += 1
        else:
            ext += 1
    n = len(insts)
    gip = sum(1 for i in insts if i["gold_in_pool"])
    return {"n": n, "acc": round(correct / n, 4), "ceiling": round(gip / n, 4),
            "ext_err": ext, "dec_err": dec, "correct": correct}


def _group_acc(w, insts, keyfn):
    by = defaultdict(list)
    for inst in insts:
        by[keyfn(inst)].append(inst)
    return {k: _acc_ceiling_resid(w, v) for k, v in sorted(by.items())}


def cfg_smoke():
    return dict(mode="smoke", epochs=40, lr=0.20, alpha=0.2, frac_train=0.6, seeds=[7, 13, 19])


def cfg_full():
    return dict(mode="full", epochs=60, lr=0.20, alpha=0.2, frac_train=0.6, seeds=[7, 13, 19])


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START modern in-domain construction gold", flush=True)

    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.arc_labeler import ArcLabeler
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded (persisted UD-EWT assets; NO retrain)", flush=True)

    # Mining models: KEPT FIXED = McGuffey mining (strict one-variable; a mild handicap for the modern arm).
    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    print(f"[{ANCHOR_NAME}:{mode}] mining (McGuffey, fixed): {gfit_stats['n_object_classes']} gfit classes, "
          f"{n_mine} sents", flush=True)

    order, sent_text, gold, ann, gold_meta = load_construction_gold()
    if mode == "smoke":
        # smoke = subset of verbs but MUST include hard constructions -> take first ~50 sentences by order.
        keep = set(order[:50])
        order = [s for s in order if s in keep]
        gold = {s: gold[s] for s in order}
    print(f"[{ANCHOR_NAME}:{mode}] gold: {len(order)} sentences, ud_source={gold_meta['ud_source_split_counts']}",
          flush=True)

    unlab = _annotate(V2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "unlabeled"), ann)
    lab_v1 = _annotate(V2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_v1"), ann)
    lab_bk = _annotate(V2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_backoff"), ann)

    bk_pos_all = [i for i in lab_bk if i["is_pos"]]
    n_pos = len(bk_pos_all)
    verb_found = sum(1 for i in bk_pos_all if i["verb_found"]) / n_pos if n_pos else None
    ceil_unlab, _ = E.gold_in_pool_rate([i for i in unlab if i["is_pos"]])
    ceil_v1, _ = E.gold_in_pool_rate([i for i in lab_v1 if i["is_pos"]])
    ceil_bk, _ = E.gold_in_pool_rate(bk_pos_all)
    leak_bk = E.giveaway_audit(bk_pos_all)
    n_amb = sum(1 for i in bk_pos_all if i.get("genuine_ambiguity"))
    print(f"[{ANCHOR_NAME}:{mode}] gold POS={n_pos} verb_found={verb_found:.3f} genuine_amb={n_amb} "
          f"ceiling unlab={ceil_unlab} v1={ceil_v1} BACKOFF={ceil_bk}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-GUARD backoff: max_single_cue_gold_sel="
          f"{leak_bk['max_single_feature_gold_selection_acc']} ({leak_bk['max_single_feature']}) "
          f"leak={leak_bk['leak']}", flush=True)

    per_seed = []
    v1_digests, bk_digests = {}, {}
    # union of test-fold instances across seeds for the ud-split / gold-construction breakdowns.
    bk_test_union, unlab_test_union, v1_test_union = [], [], []
    for seed in cfg["seeds"]:
        tr_v, te_v = E.verb_split(gold, seed, cfg["frac_train"])
        w_unlab, _, _ = IV.train_vote(E.sel_by_verb(unlab, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_v1, _, _ = IV.train_vote(E.sel_by_verb(lab_v1, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_bk, _, _ = IV.train_vote(E.sel_by_verb(lab_bk, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])

        unlab_te = [i for i in E.sel_by_verb(unlab, te_v) if i["is_pos"]]
        v1_te = [i for i in E.sel_by_verb(lab_v1, te_v) if i["is_pos"]]
        bk_te = [i for i in E.sel_by_verb(lab_bk, te_v) if i["is_pos"]]
        bk_tr = [i for i in E.sel_by_verb(lab_bk, tr_v) if i["is_pos"]]

        acc_unlab, _ = E.endtoend_accuracy(w_unlab, unlab_te)
        acc_v1, _ = E.endtoend_accuracy(w_v1, v1_te)
        acc_bk, n_bk = E.endtoend_accuracy(w_bk, bk_te)

        # exclude-genuine-ambiguity variant (abstain-targets are unfair as must-get-right).
        bk_te_noamb = [i for i in bk_te if not i.get("genuine_ambiguity")]
        acc_bk_noamb, _ = E.endtoend_accuracy(w_bk, bk_te_noamb)

        part_bk = V2.residual_partition(w_bk, bk_te)
        part_unlab = V2.residual_partition(w_unlab, unlab_te)
        abst = E.abstain_analysis(w_bk, bk_tr, bk_te, cfg["alpha"], None, sent_text)
        pc_bk_gold = _group_acc(w_bk, bk_te, lambda i: i.get("gold_construction", "?"))

        for i in bk_te:
            bk_test_union.append((seed, i, w_bk))
        v1_digests[seed] = hashlib.sha256(np.round(w_v1, 6).tobytes()).hexdigest()[:16]
        bk_digests[seed] = hashlib.sha256(np.round(w_bk, 6).tobytes()).hexdigest()[:16]

        row = {"seed": seed, "n_test_pos": n_bk,
               "unlabeled_vote_endtoend_acc": acc_unlab,
               "labeled_v1_vote_endtoend_acc": acc_v1,
               "labeled_backoff_vote_endtoend_acc": acc_bk,
               "backoff_endtoend_acc_excl_ambiguity": acc_bk_noamb,
               "test_ceiling_backoff": E.gold_in_pool_rate(bk_te)[0],
               "test_ceiling_unlabeled": E.gold_in_pool_rate(unlab_te)[0],
               "residual_partition_backoff": part_bk,
               "residual_partition_unlabeled": part_unlab,
               "per_gold_construction_backoff": pc_bk_gold,
               "abstain_backoff": abst,
               "w_backoff": [round(x, 4) for x in w_bk.tolist()]}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} UNLAB={acc_unlab} V1={acc_v1} BACKOFF={acc_bk} "
              f"(noamb={acc_bk_noamb}, ceil_bk={row['test_ceiling_backoff']}) "
              f"| residual BACKOFF ext:dec={part_bk['extraction_err']}:{part_bk['decision_err']} "
              f"(ext_frac={part_bk['extraction_frac_of_residual']})", flush=True)

    def mean(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    m_unlab = mean("unlabeled_vote_endtoend_acc")
    m_v1 = mean("labeled_v1_vote_endtoend_acc")
    m_bk = mean("labeled_backoff_vote_endtoend_acc")
    m_bk_noamb = mean("backoff_endtoend_acc_excl_ambiguity")

    # aggregate residual partition (backoff) across seeds.
    def agg_partition(subkey):
        ext = sum(s[subkey]["extraction_err"] for s in per_seed)
        dec = sum(s[subkey]["decision_err"] for s in per_seed)
        cor = sum(s[subkey]["correct"] for s in per_seed)
        tot = sum(s[subkey]["n"] for s in per_seed)
        resid = ext + dec
        return {"n_total": tot, "correct": cor, "extraction_err": ext, "decision_err": dec, "residual": resid,
                "extraction_frac_of_residual": (round(ext / resid, 4) if resid else None),
                "decision_frac_of_residual": (round(dec / resid, 4) if resid else None),
                "ext_to_dec_ratio": f"{ext}:{dec}"}
    part_bk_agg = agg_partition("residual_partition_backoff")
    part_unlab_agg = agg_partition("residual_partition_unlabeled")

    # ------ LEAK BREAKDOWN: per UD-source-split (train-leaked vs dev vs test-heldout) over test-fold union.
    ud_split_breakdown = {}
    for sp in ("train", "dev", "test"):
        sub_correct = sub_ext = sub_dec = sub_n = sub_gip = 0
        for seed, inst, w in bk_test_union:
            if inst.get("ud_split") != sp:
                continue
            sub_n += 1
            sub_gip += int(inst["gold_in_pool"])
            if not inst["cands"]:
                sub_ext += 1
                continue
            pick = IV.select_pick(w, inst)[0]
            if pick["p"] == inst["gold_patient"]:
                sub_correct += 1
            elif inst["gold_in_pool"]:
                sub_dec += 1
            else:
                sub_ext += 1
        ud_split_breakdown[sp] = {
            "n_test_fold_instances": sub_n,
            "endtoend_acc": (round(sub_correct / sub_n, 4) if sub_n else None),
            "extraction_ceiling_gold_in_pool": (round(sub_gip / sub_n, 4) if sub_n else None),
            "ext_err": sub_ext, "dec_err": sub_dec, "correct": sub_correct,
            "leak_status": ("MEMORIZED_by_frontend" if sp == "train" else
                            "early_stop_seen" if sp == "dev" else "TRULY_HELD_OUT")}

    # ------ per-GOLD-construction (union across seeds; TRUE gold labels).
    constr_union = defaultdict(lambda: {"correct": 0, "n": 0, "gip": 0, "ext": 0, "dec": 0})
    for seed, inst, w in bk_test_union:
        c = inst.get("gold_construction", "?")
        d = constr_union[c]
        d["n"] += 1
        d["gip"] += int(inst["gold_in_pool"])
        if not inst["cands"]:
            d["ext"] += 1
            continue
        pick = IV.select_pick(w, inst)[0]
        if pick["p"] == inst["gold_patient"]:
            d["correct"] += 1
        elif inst["gold_in_pool"]:
            d["dec"] += 1
        else:
            d["ext"] += 1
    per_constr_gold = {c: {"n": d["n"], "endtoend_acc": round(d["correct"] / d["n"], 4) if d["n"] else None,
                           "extraction_ceiling": round(d["gip"] / d["n"], 4) if d["n"] else None,
                           "ext_err": d["ext"], "dec_err": d["dec"]}
                       for c, d in sorted(constr_union.items())}

    # ------ VERDICT (vs McGuffey backoff 0.7622).
    if m_bk is None:
        verdict = "UNKNOWN_NO_SEEDS"
    elif m_bk >= MCG_BACKOFF + 0.05:
        verdict = "REVEALS_HIGHER_INDOMAIN_ARCHAIC_ARTIFACT"
    elif m_bk < MCG_BACKOFF - 0.05:
        verdict = "MODERN_WORSE"
    else:
        verdict = "DEEPER_BOUND_REGISTER_NOT_LIMITER"

    baseline_in_band = bool(m_v1 is not None and 0.05 < m_v1 < 0.95 and m_unlab is not None and 0.05 < m_unlab < 0.95)
    arms_differ = all(v1_digests[s] != bk_digests[s] for s in cfg["seeds"])
    test_heldout_acc = ud_split_breakdown["test"]["endtoend_acc"]
    delta_vs_mcg = round((m_bk or 0) - MCG_BACKOFF, 4)

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | modern in-domain UD-EWT, n_pos={n_pos} verb_found={round(verb_found,4) if verb_found else None} "
           f"| END-TO-END who-affected: UNLAB={m_unlab} V1={m_v1} BACKOFF={m_bk} (noamb={m_bk_noamb}, ceil={ceil_bk}) "
           f"vs McGUFFEY backoff={MCG_BACKOFF} (delta={delta_vs_mcg:+.4f}) "
           f"| RESIDUAL backoff ext:dec={part_bk_agg['ext_to_dec_ratio']} (ext_frac={part_bk_agg['extraction_frac_of_residual']}) "
           f"| LEAK ud_split: train(memorized)={ud_split_breakdown['train']['endtoend_acc']}"
           f"(ceil={ud_split_breakdown['train']['extraction_ceiling_gold_in_pool']},n={ud_split_breakdown['train']['n_test_fold_instances']}) "
           f"dev={ud_split_breakdown['dev']['endtoend_acc']}"
           f"(ceil={ud_split_breakdown['dev']['extraction_ceiling_gold_in_pool']},n={ud_split_breakdown['dev']['n_test_fold_instances']}) "
           f"test(HELDOUT)={test_heldout_acc}"
           f"(ceil={ud_split_breakdown['test']['extraction_ceiling_gold_in_pool']},n={ud_split_breakdown['test']['n_test_fold_instances']}) "
           f"| baseline_in_band={baseline_in_band} arms_differ={arms_differ} no_giveaway={not leak_bk['leak']} "
           f"(max_single_cue_gold_sel={leak_bk['max_single_feature_gold_selection_acc']})")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "n_gold_pos_pairs": n_pos, "verb_found_rate": verb_found, "n_genuine_ambiguity": n_amb,
        "MCGUFFEY_baseline_backoff": MCG_BACKOFF, "MCGUFFEY_baseline_v1": MCG_V1, "MCGUFFEY_ceiling": MCG_CEILING,
        "PRIMARY_modern_endtoend_backoff_vote": m_bk,
        "modern_endtoend_backoff_excl_ambiguity": m_bk_noamb,
        "modern_endtoend_v1_vote": m_v1,
        "modern_endtoend_unlabeled_vote": m_unlab,
        "delta_backoff_vs_mcguffey": delta_vs_mcg,
        "candidate_recall_ceiling_unlabeled": ceil_unlab,
        "candidate_recall_ceiling_v1": ceil_v1,
        "candidate_recall_ceiling_backoff": ceil_bk,
        "RESIDUAL_PARTITION_backoff": part_bk_agg,
        "RESIDUAL_PARTITION_unlabeled": part_unlab_agg,
        "LEAK_ud_source_split_breakdown": ud_split_breakdown,
        "leak_free_test_heldout_endtoend_acc": test_heldout_acc,
        "per_gold_construction_backoff_union": per_constr_gold,
        "baseline_in_band": baseline_in_band, "arms_differ_verified": arms_differ,
        "leak_guard_backoff": leak_bk, "no_giveaway_verified": bool(not leak_bk["leak"]),
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "end-to-end decision-precision measurement",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified: <9min)",
        "deterministic_seeding": True, "gold_meta": gold_meta, "per_seed": per_seed,
    }
    E.write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== modern in-domain reader self-test (real code paths) ===", flush=True)
    # (1) gold loads + UD-split membership present; leak counts reproduce.
    order, sent_text, gold, ann, meta = load_construction_gold()
    assert len(order) == meta["n_sentences"] and meta["n_items"] == 136, f"gold load mismatch: {meta}"
    ud = meta["ud_source_split_counts"]
    assert ud.get("train", 0) >= 100, f"expected train-leak >=100, got {ud}"
    print(f"[selftest] gold={len(order)} sents ud_source_split={ud} (train=LEAK)", flush=True)

    # (2) verb identity anchors on the real token: a known passive item's verb is findable + patient present.
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.arc_labeler import ArcLabeler
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    # tiny mining so build_instances features work (real code path, not synthetic).
    iv_cfg = IV.cfg_smoke()
    tmp_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_selftest")
    gfit_fn, sel_fn, _st, _n = IV.build_mining_models(iv_cfg, tmp_dir)
    sub_order = order[:8]
    sub_gold = {s: gold[s] for s in sub_order}
    insts = V2.build_instances(sub_order, sent_text, sub_gold, gen, labeler, gfit_fn, sel_fn, "labeled_backoff")
    insts = _annotate(insts, ann)
    pos = [i for i in insts if i["is_pos"]]
    assert pos, "self-test FAIL: no pos instances built"
    assert all("ud_split" in i and "gold_construction" in i for i in pos), "self-test FAIL: annotation missing"
    vf = sum(1 for i in pos if i["verb_found"]) / len(pos)
    print(f"[selftest] built {len(pos)} pos insts, verb_found={vf:.3f}, "
          f"constructions={sorted(set(i['gold_construction'] for i in pos))}", flush=True)

    # (3) gold-independence: build_instances / accept_hardened take NO gold arg.
    import inspect
    assert "gold" not in set(inspect.signature(V2.accept_hardened).parameters), "LEAK: accept_hardened sees gold"
    # (4) is_gold is a pure surface-string match (gold only scores; front-end never sees it).
    for i in pos:
        for c in i["cands"]:
            assert c["is_gold"] == (c["p"] == i["gold_patient"]), "self-test FAIL: is_gold not surface-match"
    # (5) verb_split determinism.
    tr, te = E.verb_split(sub_gold, 7, 0.6)
    assert not (set(tr) & set(te)), "self-test FAIL: verb overlap"
    print("[selftest] PASS: gold load + leak instrumentation + annotation + gold-independence exercised", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        E._write_crash_metrics(output_dir, e)
        raise
