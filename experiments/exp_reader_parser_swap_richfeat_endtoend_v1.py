"""PHASE-2 reader parser-swap: does the RICHER-FEATURE arc parser lift the end-to-end who-is-affected reader?

ONE-VARIABLE swap: replace ONLY the arc parser (baseline greedy ArcParser -> RichArcParser, the richer-static-
  feature retrain from exp_parser_uas_ladder_richfeat_v1 @ arc_parser_richfeat_ud_ewt.npz). EVERYTHING else
  identical: same POS tagger, same UD tokenizer, same arc_labeler, same candidate-gen rules, same integrated
  VOTE, same verb-disjoint splits, same 3 seeds, same abstain. Structurally identical to the already-run MST
  swap cell (exp_reader_parser_swap_mst_endtoend_v1) -- only the parser referent differs.

WHY (Lever D coupling test): Cell-1 (parser ladder) measures whether richer classical arc-scorer features lift
  UAS on UD-EWT dev. This cell measures whether ANY such UAS gain TRANSFERS to the reader on archaic McGuffey
  gold (the extraction-bound coupling question). Precedent: the MST +0.0097 UAS gave the reader BACKOFF
  0.7622 -> 0.7896 (recovered attach-misses); this cell asks the same of the richer-feature parser.

*** PRECONDITION: this cell REQUIRES data/frontend_assets/arc_parser_richfeat_ud_ewt.npz, which is persisted
    ONLY by the FULL run of exp_parser_uas_ladder_richfeat_v1. Do NOT dispatch this cell's FULL run until the
    Cell-1 FULL parser has landed. The self_test runs a PLUMBING check on a stand-in (CANON weights) when the
    real asset is absent, and LOUDLY flags that the real number needs the persisted rich parser. ***

KEY DIAGNOSTICS (mirror the MST swap cell):
  (1) attach-miss RECOVERY (seed-independent): align pos instances by (sid, v_lemma) across the two parsers;
      count gold_in_pool transitions base->rich (recovered / lost / net) on UNLABELED + BACKOFF pools.
  (2) FAVORABLE-COUPLING check: recall gain WITH an end-to-end gain (correct recovered candidate) vs added
      distractors that cost decision.
  (3) per-construction end-to-end delta.
  (4) negation/flip spot-check (per-instance correctness-flip base->rich on BACKOFF).

LEAK-HUNT (in-cell): (1) the rich parser features are SURFACE char/POS only (Cell-1 leak-guard); the reader
  output never sees the who-is-affected gold (gold only SCORES via surface-string is_gold in the reader
  harness). (2) *** McGuffey is archaic OUT-OF-DOMAIN for the UD-EWT-trained rich parser -- a rich-parser gain
  on McGuffey is genuine cross-domain generalization; a modern-in-domain gain (the sibling modern cell) is
  LEAK-INFLATED (106/136 modern construction-gold sentences are UD-EWT TRAIN, memorized by the parser). Report
  which corpus is being measured. (3) no single vote feature >0.95-predicts the gold (inherited from E harness).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = the reader with the CURRENT persisted parser (BACKOFF ~0.762 McGuffey), re-derived LIVE.
  (2) CAN-FAIL: (a) Cell-1 may show the rich UAS gain is ~0 (classical tapped) -> nothing to transfer (FLAT);
      (b) even a real UAS gain may not transfer to McGuffey archaic (domain shift, MST precedent was small);
      (c) recovered candidates may add distractors (unfavorable coupling) -> reader flat/down. A FLAT result is
      the informative plateau (parser-feature is not the liftable lever; bottleneck is elsewhere).
  (3) DIFFICULTY-ON: pronoun + coordination + relative slices per-construction; attach-miss instances surfaced.
  (4) ONE-VARIABLE = the parser. Same labeler/vote/split/seeds/abstain across both parsers.

VERDICT BANDS (pre-registered; MEASUREMENT cell):
  READER_LIFTED_BY_RICHFEAT: rich BACKOFF >= base BACKOFF + 0.02 AND min-over-seeds delta >= 0 AND net-recovered > 0.
  READER_REGRESSED:          rich BACKOFF < base BACKOFF - 0.02.
  RICHFEAT_ATTACH_NOT_LIFTABLE (informative plateau): |rich - base| < 0.02 on BACKOFF.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: ~114 gold sentences parsed twice + mining once +
  3-seed vote fits per arm per parser; MST-swap sibling full ~<20min). Storage: no_storage.
  progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, default_rng, sorted(set);
  NO hash()-seeded RNG. LOCAL-ONLY; NO queue, NO push, NO remote-persist, NO store write.

CELL-TEMPLATE: except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace metrics;
  arms_differ (base vs rich vote weights bit-differ); baseline_in_band; all numbers tagged.

PRIOR-WORK CHECK: same lineage as the MST swap cell (which was NOVEL at cosine<0.30); this is the Lever-D
  feature-parser analog of that swap. CITED@exp_reader_parser_swap_mst_endtoend_v1 + drill 2026-06-11.

NO LLM. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_parser_swap_richfeat_endtoend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

from experiments import exp_reader_integration_endtoend_whoaffected_v1 as E  # noqa: E402
from experiments import exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened as E2  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from experiments.exp_parser_uas_ladder_richfeat_v1 import RichArcParser  # noqa: E402

RICH_ARC = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_richfeat_ud_ewt.npz")


def build_gen(kind):
    tagger = PosTagger.load(E.POS_PATH)
    if kind == "baseline":
        parser = ArcParser.load(E.ARC_PATH)
    elif kind == "richfeat":
        if not os.path.exists(RICH_ARC):
            raise FileNotFoundError(
                "RICH parser asset missing: %s -- run exp_parser_uas_ladder_richfeat_v1 --(full) first" % RICH_ARC)
        parser = RichArcParser.load(RICH_ARC)
    else:
        raise ValueError(kind)
    return CandidateGenerator(tagger, parser)


def _pos_key_map(insts):
    out = {}
    for i in insts:
        if i["is_pos"]:
            out[(i["sid"], i["v_lemma"])] = i
    return out


def attach_recovery(base_insts, rich_insts):
    bm = _pos_key_map(base_insts)
    mm = _pos_key_map(rich_insts)
    keys = sorted(set(bm) & set(mm))
    recovered, lost, both_hit, both_miss = [], [], 0, 0
    for k in keys:
        b = bool(bm[k]["gold_in_pool"])
        m = bool(mm[k]["gold_in_pool"])
        if not b and m:
            recovered.append({"sid": k[0], "v": k[1], "gold": mm[k]["gold_patient"],
                              "constr": mm[k]["construction"], "rich_pool": [c["p"] for c in mm[k]["cands"]]})
        elif b and not m:
            lost.append({"sid": k[0], "v": k[1], "gold": bm[k]["gold_patient"],
                         "constr": bm[k]["construction"], "base_pool": [c["p"] for c in bm[k]["cands"]]})
        elif b and m:
            both_hit += 1
        else:
            both_miss += 1
    base_ceiling = round(sum(1 for k in keys if bm[k]["gold_in_pool"]) / len(keys), 4) if keys else None
    rich_ceiling = round(sum(1 for k in keys if mm[k]["gold_in_pool"]) / len(keys), 4) if keys else None
    return {"n_aligned_pos": len(keys), "base_ceiling": base_ceiling, "rich_ceiling": rich_ceiling,
            "n_recovered": len(recovered), "n_lost": len(lost), "net_recovered": len(recovered) - len(lost),
            "both_hit": both_hit, "both_miss": both_miss, "recovered": recovered, "lost": lost}


def build_all_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn):
    return {
        "unlabeled": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "unlabeled"),
        "labeled_v1": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_v1"),
        "labeled_hardened": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_hardened"),
        "labeled_backoff": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_backoff"),
    }


def instance_correct_map(w, insts):
    out = {}
    for inst in insts:
        if not inst["is_pos"]:
            continue
        if not inst["cands"]:
            out[(inst["sid"], inst["v_lemma"])] = 0
            continue
        pick = IV.select_pick(w, inst)[0]
        out[(inst["sid"], inst["v_lemma"])] = int(pick["p"] == inst["gold_patient"])
    return out


def run_reader(kind, order, sent_text, reader_svo, gold, labeler, gfit_fn, sel_fn, cfg):
    gen = build_gen(kind)
    inst = build_all_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn)
    unlab, lab_v1, lab_hard, lab_bk = (inst["unlabeled"], inst["labeled_v1"],
                                       inst["labeled_hardened"], inst["labeled_backoff"])
    n_pos = len([i for i in lab_bk if i["is_pos"]])
    ceil = {
        "unlabeled": E.gold_in_pool_rate([i for i in unlab if i["is_pos"]])[0],
        "v1": E.gold_in_pool_rate([i for i in lab_v1 if i["is_pos"]])[0],
        "hardened": E.gold_in_pool_rate([i for i in lab_hard if i["is_pos"]])[0],
        "backoff": E.gold_in_pool_rate([i for i in lab_bk if i["is_pos"]])[0],
    }
    per_seed = []
    bk_digests = {}
    corr_maps_bk = {}
    for seed in cfg["seeds"]:
        tr_v, te_v = E.verb_split(gold, seed, cfg["frac_train"])
        w_unlab = IV.train_vote(E.sel_by_verb(unlab, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])[0]
        w_v1 = IV.train_vote(E.sel_by_verb(lab_v1, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])[0]
        w_hard = IV.train_vote(E.sel_by_verb(lab_hard, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])[0]
        w_bk = IV.train_vote(E.sel_by_verb(lab_bk, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])[0]

        unlab_te = [i for i in E.sel_by_verb(unlab, te_v) if i["is_pos"]]
        v1_te = [i for i in E.sel_by_verb(lab_v1, te_v) if i["is_pos"]]
        hard_te = [i for i in E.sel_by_verb(lab_hard, te_v) if i["is_pos"]]
        bk_te = [i for i in E.sel_by_verb(lab_bk, te_v) if i["is_pos"]]

        acc_unlab = E.endtoend_accuracy(w_unlab, unlab_te)[0]
        acc_v1 = E.endtoend_accuracy(w_v1, v1_te)[0]
        acc_hard = E.endtoend_accuracy(w_hard, hard_te)[0]
        acc_bk, n_bk = E.endtoend_accuracy(w_bk, bk_te)
        acc_crude = E.crude_endtoend(order, sent_text, reader_svo, gold, cfg["epochs"], 0.45, seed, te_v)[0]

        pc_bk = E.per_construction_endtoend(w_bk, bk_te)
        bk_digests[seed] = hashlib.sha256(np.round(w_bk, 6).tobytes()).hexdigest()[:16]
        corr_maps_bk[seed] = instance_correct_map(w_bk, [i for i in lab_bk if i["is_pos"]])

        per_seed.append({"seed": seed, "n_test_pos": n_bk, "crude": acc_crude, "unlabeled": acc_unlab,
                         "v1": acc_v1, "hardened": acc_hard, "backoff": acc_bk,
                         "test_ceiling_backoff": E.gold_in_pool_rate(bk_te)[0],
                         "per_construction_backoff": pc_bk})
        print(f"[{ANCHOR_NAME}:{kind}] seed={seed} CRUDE={acc_crude} UNLAB={acc_unlab} V1={acc_v1} "
              f"HARD={acc_hard} BACKOFF={acc_bk} (ceil_bk={ceil['backoff']})", flush=True)

    def mean(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    def minv(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.min(vals)), 4) if vals else None

    cagg = defaultdict(lambda: {"acc": [], "gip": [], "n": []})
    for s in per_seed:
        for c, d in s["per_construction_backoff"].items():
            if d["endtoend_acc"] is not None:
                cagg[c]["acc"].append(d["endtoend_acc"])
            if d["gold_in_pool"] is not None:
                cagg[c]["gip"].append(d["gold_in_pool"])
            cagg[c]["n"].append(d["n"])
    per_constr = {c: {"mean_endtoend_acc": round(float(np.mean(v["acc"])), 4) if v["acc"] else None,
                      "mean_gold_in_pool": round(float(np.mean(v["gip"])), 4) if v["gip"] else None,
                      "mean_n": round(float(np.mean(v["n"])), 2)} for c, v in sorted(cagg.items())}

    return {
        "kind": kind, "n_gold_pos": n_pos, "ceiling": ceil,
        "mean": {"crude": mean("crude"), "unlabeled": mean("unlabeled"), "v1": mean("v1"),
                 "hardened": mean("hardened"), "backoff": mean("backoff")},
        "min_backoff": minv("backoff"), "min_v1": minv("v1"),
        "per_construction": per_constr, "per_seed": per_seed,
        "bk_digests": bk_digests, "corr_maps_bk": corr_maps_bk,
        "instances": {"unlabeled": unlab, "labeled_backoff": lab_bk},
    }


def negation_flip_spotcheck(base_res, rich_res):
    keys = set()
    for s in base_res["corr_maps_bk"].values():
        keys.update(s.keys())
    flips = []
    for k in sorted(keys):
        b = np.mean([base_res["corr_maps_bk"][s].get(k, 0) for s in base_res["corr_maps_bk"]])
        m = np.mean([rich_res["corr_maps_bk"][s].get(k, 0) for s in rich_res["corr_maps_bk"]])
        if abs(m - b) >= 0.5:
            flips.append({"sid": k[0], "v": k[1], "base_correct_frac": round(float(b), 3),
                          "rich_correct_frac": round(float(m), 3),
                          "direction": "RESOLVED" if m > b else "REGRESSED"})
    return {"n_majority_flips": len(flips), "flips": flips}


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = E.cfg_smoke() if mode == "smoke" else E.cfg_full()
    output_dir = _out_dir(mode)
    os.makedirs(output_dir, exist_ok=True)
    print(f"[{ANCHOR_NAME}:{mode}] START slice={'+'.join(cfg['slice_lessons'])}", flush=True)

    from hdlab.arc_labeler import ArcLabeler
    labeler = ArcLabeler.load(E.LABELER_PATH)
    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])
    print(f"[{ANCHOR_NAME}:{mode}] labeler+mining loaded ({gfit_stats['n_object_classes']} gfit, {n_mine} sents)",
          flush=True)

    base_res = run_reader("baseline", order, sent_text, reader_svo, gold, labeler, gfit_fn, sel_fn, cfg)
    rich_res = run_reader("richfeat", order, sent_text, reader_svo, gold, labeler, gfit_fn, sel_fn, cfg)

    recov_unlab = attach_recovery(base_res["instances"]["unlabeled"], rich_res["instances"]["unlabeled"])
    recov_bk = attach_recovery(base_res["instances"]["labeled_backoff"], rich_res["instances"]["labeled_backoff"])
    flip = negation_flip_spotcheck(base_res, rich_res)

    b_bk, m_bk = base_res["mean"]["backoff"], rich_res["mean"]["backoff"]
    b_v1, m_v1 = base_res["mean"]["v1"], rich_res["mean"]["v1"]
    delta_bk = round((m_bk or 0) - (b_bk or 0), 4)
    delta_v1 = round((m_v1 or 0) - (b_v1 or 0), 4)
    min_delta_bk = round(min((ms["backoff"] or 0) - (bs["backoff"] or 0)
                             for bs, ms in zip(base_res["per_seed"], rich_res["per_seed"])), 4)
    net_recovered = recov_bk["net_recovered"]
    ceil_up = (rich_res["ceiling"]["backoff"] or 0) > (base_res["ceiling"]["backoff"] or 0) + 1e-9
    favorable = bool(ceil_up and delta_bk > 0)

    if delta_bk >= 0.02 and min_delta_bk >= 0 and net_recovered > 0:
        verdict = "READER_LIFTED_BY_RICHFEAT"
    elif delta_bk < -0.02:
        verdict = "READER_REGRESSED"
    else:
        verdict = "RICHFEAT_ATTACH_NOT_LIFTABLE"

    arms_differ = all(base_res["bk_digests"][s] != rich_res["bk_digests"][s] for s in cfg["seeds"])
    baseline_in_band = bool(b_bk is not None and 0.05 < b_bk < 0.95)

    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} gold_pos={base_res['n_gold_pos']} "
           f"| BACKOFF base={b_bk} rich={m_bk} (delta={delta_bk:+.4f} min_seed={min_delta_bk:+.4f}) "
           f"| V1 base={b_v1} rich={m_v1} (delta={delta_v1:+.4f}) "
           f"| ceiling(backoff) base={base_res['ceiling']['backoff']} rich={rich_res['ceiling']['backoff']} "
           f"| ATTACH-RECOVERY backoff: recovered={recov_bk['n_recovered']} lost={recov_bk['n_lost']} "
           f"net={net_recovered} | favorable_coupling={favorable} "
           f"| negation/flip majority_flips={flip['n_majority_flips']} "
           f"| arms_differ={arms_differ} baseline_in_band={baseline_in_band}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(time.perf_counter() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "slice_lessons": cfg["slice_lessons"], "n_gold_pos_pairs": base_res["n_gold_pos"],
        "corpus": "mcguffey_archaic_out_of_domain",
        "rich_parser_uas_source": "MEASURED@data/exp_parser_uas_ladder_richfeat_v1/metrics.json (Cell-1 full)",
        "reader_baseline_parser": {"means": base_res["mean"], "ceiling": base_res["ceiling"],
                                   "per_construction": base_res["per_construction"], "per_seed": base_res["per_seed"]},
        "reader_richfeat_parser": {"means": rich_res["mean"], "ceiling": rich_res["ceiling"],
                                   "per_construction": rich_res["per_construction"], "per_seed": rich_res["per_seed"]},
        "delta_backoff": delta_bk, "delta_backoff_min_seed": min_delta_bk, "delta_v1": delta_v1,
        "attach_recovery_backoff": recov_bk, "attach_recovery_unlabeled": recov_unlab,
        "favorable_coupling": favorable, "net_recovered_backoff": net_recovered,
        "negation_flip_spotcheck": flip,
        "arms_differ_verified": arms_differ, "baseline_in_band": baseline_in_band,
        "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true",
        "compute_architecture": "sequential-CPU (justified)", "deterministic_seeding": True,
        "gold_meta": gold_meta,
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(time.perf_counter()-t0,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print(f"=== {ANCHOR_NAME} self-test (real code paths) ===", flush=True)
    # baseline parser always available; rich parser may be pending Cell-1 full -> stand-in on CANON weights.
    gb = build_gen("baseline")
    rb = gb.generate("He showed him the seeds.")
    assert isinstance(rb.heads, dict) and rb.margins
    if os.path.exists(RICH_ARC):
        gm = build_gen("richfeat")
        rm = gm.generate("He showed him the seeds.")
        assert rb.tokens == rm.tokens and len(rb.pos) == len(rm.pos), "tokenizer/tagger identical across parsers"
        assert type(gm.parser).__name__ == "RichArcParser"
        print(f"[selftest] REAL rich asset present | base heads={rb.heads} rich heads={rm.heads}", flush=True)
    else:
        stand_in = RichArcParser(ArcParser.load(E.ARC_PATH).avg)
        r = stand_in.parse(["He", "showed", "him", "the", "seeds", "."],
                           ["PRON", "VERB", "PRON", "DET", "NOUN", "PUNCT"])
        assert isinstance(r.heads, dict) and r.margins
        print("[selftest] WARN: rich asset ABSENT -- plumbing verified on stand-in; FULL run needs "
              "exp_parser_uas_ladder_richfeat_v1 --(full) to persist arc_parser_richfeat_ud_ewt.npz", flush=True)
    # attach_recovery counts transitions.
    bi = [{"is_pos": True, "sid": "s1", "v_lemma": "eat", "gold_patient": "apple", "gold_in_pool": False,
           "construction": "simple", "cands": []}]
    mi = [{"is_pos": True, "sid": "s1", "v_lemma": "eat", "gold_patient": "apple", "gold_in_pool": True,
           "construction": "simple", "cands": [{"p": "apple"}]}]
    r = attach_recovery(bi, mi)
    assert r["n_recovered"] == 1 and r["net_recovered"] == 1, r
    print("[selftest] PASS: parser-swap plumbing + attach-recovery", flush=True)
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
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "metrics.json.tmp"), "w", encoding="utf-8") as f:
            json.dump({"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                       "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}", "summary": "CELL_CRASHED",
                       "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000]}, f, indent=2)
        os.replace(os.path.join(output_dir, "metrics.json.tmp"), os.path.join(output_dir, "metrics.json"))
        raise
