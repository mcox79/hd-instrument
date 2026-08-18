"""PHASE-2 reader parser-swap: does the higher-UAS MST parser lift the end-to-end who-is-affected reader?

ONE-VARIABLE swap: replace ONLY the arc parser (baseline greedy ArcParser UAS 0.7868 -> MstArcParser
  UAS 0.7965, the Phase-1 S1b MST-retrain @ arc_parser_mst_retrain_ud_ewt.npz). EVERYTHING else identical:
  same POS tagger, same UD tokenizer, same arc_labeler, same candidate-gen rules, same integrated VOTE,
  same verb-disjoint splits, same 3 seeds, same abstain. Reuses experiments.<v2>.build_instances +
  experiments.<v1> helpers verbatim -- only the CandidateGenerator's parser differs.

WHY (convergent lever, CITED@backup-doc 2026-07-20): the reader is EXTRACTION-bound; the biggest single
  extraction-loss source is the PARSER attach-miss (gold patient absent from the pool because the verb->patient
  arc is wrong/missing). MST global decode is designed to fix exactly the tree-constraint attachment errors the
  greedy local-argmax leaves. Phase-1 produced a genuinely higher-UAS parser (+0.0097 UAS); this cell measures
  whether that transfers to the reader on the archaic McGuffey gold (the coupling question).

ARMS (per parser: baseline vs mst): the v2 arms UNLABELED / LABELED_V1(+conjfix) / LABELED_HARDENED /
  LABELED_BACKOFF, plus CRUDE. Primary reader numbers = BACKOFF (remembered 0.762) and LABELED_V1 (0.742).

KEY DIAGNOSTICS:
  (1) attach-miss RECOVERY (seed-independent; the direct extraction measurement): align pos instances by
      (sid, v_lemma) across the two parsers; count gold_in_pool transitions base->mst:
        recovered = base MISS & mst HIT ; lost = base HIT & mst MISS ; net = recovered - lost.
      Reported on the UNLABELED pool (pure parser attach) AND the BACKOFF pool. This is "how many of the
      attach-misses does the higher UAS recover".
  (2) FAVORABLE-COUPLING check: does the recall gain come WITH an end-to-end gain (recovered candidate is the
      CORRECT one, low distractor cost) -- OR does it add distractors that cost decision (recall up, e2e flat/down)?
  (3) per-construction end-to-end delta (pronoun / coordination / simple / relative / control).
  (4) NEGATION-GATE spot-check: per-instance correctness-flip list (pos + nopat) base->mst, so any
      negation/true-negative items that resolve (or regress) are visible.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = the reader with the CURRENT persisted parser (0.7868), re-derived LIVE this run (not the
      remembered 0.762/0.742).
  (2) CAN-FAIL: (a) the +0.0097 UAS gain may NOT transfer to McGuffey archaic (domain-shift: UD-EWT dev != 1841
      McGuffey prose; the attach-fixes may be on UD sentences irrelevant to the gold); (b) the specific 13
      attach-miss gold pairs may be on the hard/archaic sentences the classical ladder ALSO fails; (c) even
      recovered candidates may add distractors that offset the extraction gain (unfavorable coupling) -> reader
      flat/down. Reader-lift is NOT guaranteed; a FLAT result is the informative plateau (parser-attach is not
      the liftable lever; the bottleneck is elsewhere -- labeler / domain-shift / decision).
  (3) DIFFICULTY-ON: pronoun + coordination slices reported per-construction; attach-miss instances surfaced.
  (4) ONE-VARIABLE = the parser (gen). Same labeler/vote/split/seeds/abstain across both parsers.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- primary deliverable = the numbers + the coupling verdict):
  READER_LIFTED_BY_PARSER: mst BACKOFF >= base BACKOFF + 0.02 AND min-over-seeds delta >= 0 AND net-recovered > 0.
  READER_REGRESSED:        mst BACKOFF < base BACKOFF - 0.02 (recovered distractors cost more than they gain).
  PARSER_ATTACH_NOT_LIFTABLE (informative plateau): |mst - base| < 0.02 on BACKOFF (UAS gain does NOT transfer
                            to the reader -- the bottleneck is domain-shift / labeler / decision, not attach).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: ~114 gold sentences parsed twice + mining once +
  3-seed vote fits per arm per parser; v2 full ~9min -> ~2x for two parsers ~ <20min). Storage: no_storage.
  progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, default_rng, sorted(set);
  NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO store write.

CELL-TEMPLATE: except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace metrics;
  arms_differ (base vs mst vote weights bit-differ); baseline_in_band; all numbers tagged.

PRIOR-WORK CHECK (substrate_query.sh "dependency parser MST second-order arc attachment UAS upgrade"):
  top hits cosine 0.26/0.25/0.248 all BELOW 0.30; the reader-parser-swap coupling test is NOVEL (no prior cell
  swapped the parser under a fixed reader to measure attach-lever transfer). CITED@backup-doc 2026-07-20.

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

ANCHOR_NAME = "reader_parser_swap_mst_endtoend_v1"
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
from experiments.exp_parser_uas_ladder_mst_retrain_v1 import MstArcParser  # noqa: E402

MST_ARC = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_mst_retrain_ud_ewt.npz")


def build_gen(kind):
    tagger = PosTagger.load(E.POS_PATH)
    if kind == "baseline":
        parser = ArcParser.load(E.ARC_PATH)
    elif kind == "mst":
        parser = MstArcParser.load(MST_ARC)
    else:
        raise ValueError(kind)
    return CandidateGenerator(tagger, parser)


def _pos_key_map(insts):
    """map (sid, v_lemma) -> gold_in_pool for the POS instances (seed-independent pool composition)."""
    out = {}
    for i in insts:
        if i["is_pos"]:
            out[(i["sid"], i["v_lemma"])] = i
    return out


def attach_recovery(base_insts, mst_insts):
    """seed-independent extraction diff: gold_in_pool transitions base->mst over aligned POS instances."""
    bm = _pos_key_map(base_insts)
    mm = _pos_key_map(mst_insts)
    keys = sorted(set(bm) & set(mm))
    recovered, lost, both_hit, both_miss = [], [], 0, 0
    for k in keys:
        b = bool(bm[k]["gold_in_pool"])
        m = bool(mm[k]["gold_in_pool"])
        if not b and m:
            recovered.append({"sid": k[0], "v": k[1], "gold": mm[k]["gold_patient"],
                              "constr": mm[k]["construction"],
                              "mst_pool": [c["p"] for c in mm[k]["cands"]]})
        elif b and not m:
            lost.append({"sid": k[0], "v": k[1], "gold": bm[k]["gold_patient"],
                         "constr": bm[k]["construction"],
                         "base_pool": [c["p"] for c in bm[k]["cands"]]})
        elif b and m:
            both_hit += 1
        else:
            both_miss += 1
    base_ceiling = round(sum(1 for k in keys if bm[k]["gold_in_pool"]) / len(keys), 4) if keys else None
    mst_ceiling = round(sum(1 for k in keys if mm[k]["gold_in_pool"]) / len(keys), 4) if keys else None
    return {"n_aligned_pos": len(keys), "base_ceiling": base_ceiling, "mst_ceiling": mst_ceiling,
            "n_recovered": len(recovered), "n_lost": len(lost), "net_recovered": len(recovered) - len(lost),
            "both_hit": both_hit, "both_miss": both_miss,
            "recovered": recovered, "lost": lost}


def build_all_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn):
    return {
        "unlabeled": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "unlabeled"),
        "labeled_v1": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_v1"),
        "labeled_hardened": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_hardened"),
        "labeled_backoff": E2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_backoff"),
    }


def instance_correct_map(w, insts):
    """per POS instance (sid,v): 1 if vote picks gold else 0 (empty pool -> 0). Seed-dependent."""
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
        # full-set correctness map (all verbs) for the negation/flip spot-check (seed-averaged later).
        corr_maps_bk[seed] = instance_correct_map(w_bk, [i for i in lab_bk if i["is_pos"]])

        per_seed.append({"seed": seed, "n_test_pos": n_bk,
                         "crude": acc_crude, "unlabeled": acc_unlab, "v1": acc_v1,
                         "hardened": acc_hard, "backoff": acc_bk,
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

    # per-construction aggregate.
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


def negation_flip_spotcheck(base_res, mst_res):
    """per-instance correctness flips base->mst on the BACKOFF arm, seed-averaged. Surfaces any items (incl
    negation/true-negative-adjacent) that resolve or regress. mean over the 3 seeds (0..1)."""
    keys = set()
    for s in base_res["corr_maps_bk"].values():
        keys.update(s.keys())
    flips = []
    for k in sorted(keys):
        b = np.mean([base_res["corr_maps_bk"][s].get(k, 0) for s in base_res["corr_maps_bk"]])
        m = np.mean([mst_res["corr_maps_bk"][s].get(k, 0) for s in mst_res["corr_maps_bk"]])
        if abs(m - b) >= 0.5:  # a real majority flip across seeds
            flips.append({"sid": k[0], "v": k[1], "base_correct_frac": round(float(b), 3),
                          "mst_correct_frac": round(float(m), 3),
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
    print(f"[{ANCHOR_NAME}:{mode}] labeler+mining loaded ({gfit_stats['n_object_classes']} gfit, {n_mine} sents)", flush=True)

    base_res = run_reader("baseline", order, sent_text, reader_svo, gold, labeler, gfit_fn, sel_fn, cfg)
    mst_res = run_reader("mst", order, sent_text, reader_svo, gold, labeler, gfit_fn, sel_fn, cfg)

    # attach-miss recovery (seed-independent) on unlabeled + backoff pools.
    recov_unlab = attach_recovery(base_res["instances"]["unlabeled"], mst_res["instances"]["unlabeled"])
    recov_bk = attach_recovery(base_res["instances"]["labeled_backoff"], mst_res["instances"]["labeled_backoff"])
    flip = negation_flip_spotcheck(base_res, mst_res)

    b_bk, m_bk = base_res["mean"]["backoff"], mst_res["mean"]["backoff"]
    b_v1, m_v1 = base_res["mean"]["v1"], mst_res["mean"]["v1"]
    delta_bk = round((m_bk or 0) - (b_bk or 0), 4)
    delta_v1 = round((m_v1 or 0) - (b_v1 or 0), 4)
    min_delta_bk = round(min((ms["backoff"] or 0) - (bs["backoff"] or 0)
                             for bs, ms in zip(base_res["per_seed"], mst_res["per_seed"])), 4)
    net_recovered = recov_bk["net_recovered"]
    # favorable coupling = recall up (ceiling) AND end-to-end up.
    ceil_up = (mst_res["ceiling"]["backoff"] or 0) > (base_res["ceiling"]["backoff"] or 0) + 1e-9
    favorable = bool(ceil_up and delta_bk > 0)

    if delta_bk >= 0.02 and min_delta_bk >= 0 and net_recovered > 0:
        verdict = "READER_LIFTED_BY_PARSER"
    elif delta_bk < -0.02:
        verdict = "READER_REGRESSED"
    else:
        verdict = "PARSER_ATTACH_NOT_LIFTABLE"

    arms_differ = all(base_res["bk_digests"][s] != mst_res["bk_digests"][s] for s in cfg["seeds"])
    baseline_in_band = bool(b_bk is not None and 0.05 < b_bk < 0.95)

    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} gold_pos={base_res['n_gold_pos']} "
           f"| BACKOFF base={b_bk} mst={m_bk} (delta={delta_bk:+.4f} min_seed={min_delta_bk:+.4f}) "
           f"| V1 base={b_v1} mst={m_v1} (delta={delta_v1:+.4f}) "
           f"| ceiling(backoff) base={base_res['ceiling']['backoff']} mst={mst_res['ceiling']['backoff']} "
           f"| ATTACH-RECOVERY backoff: recovered={recov_bk['n_recovered']} lost={recov_bk['n_lost']} "
           f"net={net_recovered} (unlab: rec={recov_unlab['n_recovered']} lost={recov_unlab['n_lost']} "
           f"net={recov_unlab['net_recovered']}) | favorable_coupling={favorable} "
           f"| negation/flip majority_flips={flip['n_majority_flips']} "
           f"| parser_UAS base=0.7868 mst=0.7965 (+0.0097) | arms_differ={arms_differ} baseline_in_band={baseline_in_band}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(time.perf_counter() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "slice_lessons": cfg["slice_lessons"], "n_gold_pos_pairs": base_res["n_gold_pos"],
        "parser_uas": {"baseline_greedy": 0.7868, "mst_retrain": 0.7965, "delta": 0.0097,
                       "source": "MEASURED@data/exp_parser_uas_ladder_mst_retrain_v1/metrics.json"},
        "reader_baseline_parser": {"means": base_res["mean"], "ceiling": base_res["ceiling"],
                                   "per_construction": base_res["per_construction"], "per_seed": base_res["per_seed"]},
        "reader_mst_parser": {"means": mst_res["mean"], "ceiling": mst_res["ceiling"],
                              "per_construction": mst_res["per_construction"], "per_seed": mst_res["per_seed"]},
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
    # (1) both parsers load + generate compatibly.
    gb = build_gen("baseline")
    gm = build_gen("mst")
    rb = gb.generate("He showed him the seeds.")
    rm = gm.generate("He showed him the seeds.")
    assert rb.tokens == rm.tokens and len(rb.pos) == len(rm.pos), "tokenizer/tagger must be identical across parsers"
    assert isinstance(rb.heads, dict) and isinstance(rm.heads, dict) and rb.margins and rm.margins
    print(f"[selftest] base heads={rb.heads} | mst heads={rm.heads}", flush=True)
    # (2) attach_recovery aligns + counts transitions.
    bi = [{"is_pos": True, "sid": "s1", "v_lemma": "eat", "gold_patient": "apple", "gold_in_pool": False,
           "construction": "simple", "cands": []},
          {"is_pos": True, "sid": "s1", "v_lemma": "take", "gold_patient": "ball", "gold_in_pool": True,
           "construction": "simple", "cands": [{"p": "ball"}]}]
    mi = [{"is_pos": True, "sid": "s1", "v_lemma": "eat", "gold_patient": "apple", "gold_in_pool": True,
           "construction": "simple", "cands": [{"p": "apple"}]},
          {"is_pos": True, "sid": "s1", "v_lemma": "take", "gold_patient": "ball", "gold_in_pool": True,
           "construction": "simple", "cands": [{"p": "ball"}]}]
    r = attach_recovery(bi, mi)
    assert r["n_recovered"] == 1 and r["n_lost"] == 0 and r["net_recovered"] == 1, r
    print(f"[selftest] attach_recovery OK: {r['n_recovered']} recovered", flush=True)
    # (3) build_gen swaps ONLY the parser (same tagger class, different parser class).
    assert type(gb.parser).__name__ == "ArcParser" and type(gm.parser).__name__ == "MstArcParser"
    assert type(gb.tagger).__name__ == type(gm.tagger).__name__ == "PosTagger"
    print("[selftest] PASS: parser-swap one-variable + attach-recovery + margins", flush=True)
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
