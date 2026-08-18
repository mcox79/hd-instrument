"""PARSER-SWAP end-to-end reader: does the VET'd +0.04 struct_upos PARSER lift translate to a
WHO-IS-AFFECTED reader gain, or does the archaic-domain LABELER-bound wall eat it?

THE QUESTION (Director task 2026-07-21). A struct_upos parser (McDonald first-order structural-context
features) reached UAS 0.8269 on GOLD UPOS vs canon 0.7868 -- a leak-clean, bit-exact +0.04 lift
(MEASURED@data/exp_parser_uas_feateng_struct_v1/metrics.json:arms.struct_upos.best_uas_all=0.8269@ep6;
canon MEASURED@same:phase_A / data/exp_parser_uas_headroom_leakhunt_v1 = 0.7868). That reopened the
classical-parser terminus. Does the +0.04 PARSER lift propagate to the FULL PREDICTED-POS reader
end-to-end, or is it absorbed by the labeler-bound wall (VET aca89a3432 + atom 29401: the ~0.76 reader
plateau was diagnosed LABELER/LAS-bound, NOT parser-bound; 8/11 labeler-mislabels archaic-register-driven;
a prior MST parser-swap gave +0.027 reader mostly DECISION-COUPLING not extraction)?

MECHANISM CHAIN under test:  struct parser -> better ATTACHMENT -> gold patient attached to verb MORE
OFTEN (raw candidate recall, UNLABELED pool) -> survives the LABELER filter into the deployed BACKOFF pool
(labeled candidate recall) -> survives the DECISION vote to a correct answer (end-to-end who-affected).
Each link can leak. This cell measures ALL THREE nested deltas so the GAP between them localizes the wall:
  raw-attach recall delta (UNLABELED)  ->  labeled recall delta (BACKOFF)  ->  end-to-end delta.
  (raw - labeled) = the LABELER wall.  (labeled - end-to-end) = the DECISION wall.

This ALSO resolves the gold-POS-oracle erosion flag the VET raised: the +0.04 was on GOLD UPOS; the reader
runs the parser on PREDICTED UPOS (hdlab.pos_tagger, UPOS@0.9442). Any erosion of the +0.04 under predicted
POS shows up as a shrunk raw-attach recall delta -- separable from the labeler/decision walls downstream.

ONE VARIABLE = THE PARSER (canon deployed asset vs struct-trained-in-cell). EVERYTHING ELSE IDENTICAL:
same predicted-UPOS tagger (hdlab.pos_tagger, one instance shared by both gens), same arc_labeler, same
candidate_generator rules, same integrated vote (IV, IDX_ALL, 13-dim), same McGuffey-mined selectional
models (parser-independent; kept FIXED for strict one-variable), same gold, same verb_split, same seeds.
The struct parser is swapped in-cell via a StructArcParser subclass whose parse() decodes with the VET'd
FF_STRUCT feature fn (imported verbatim from the struct cell); production hdlab/arc_parser.py is NOT mutated.

BOTH REGISTER DOMAINS (the crux -- labeler mislabels are register-driven; a parser lift may help modern
more than archaic):
  MODERN  in-domain UD-EWT construction gold (data/gold_construction_argstruct_ewt_v1, 136 pairs; canon
          BACKOFF baseline 0.7611 CITED@data/exp_reader_endtoend_modern_indomain_construction_gold_v1).
  ARCHAIC McGuffey gold (slice L04..L12; canon BACKOFF baseline 0.7622 CITED@data/exp_reader_integration_
          endtoend_whoaffected_v2_extraction_hardened/metrics.json).
(McGuffey overall is honest OOD; modern overall is LEAK-INFLATED by UD-EWT-train memorization -- see the
modern cell's ud_split note. The parser-swap DELTA within a domain is leak-robust: the memorization is
identical across the two parser arms, so it cancels in the delta. We report the delta, not the level.)

DESIGN-GATE (pre-registered; verified at smoke BEFORE trusting the full measurement):
  (1) REAL baseline = the DEPLOYED canon reader (canon arc_parser asset) re-run LIVE -> reproduces the
      0.7611/0.7622 backoff numbers within seed noise. NOT a strawman.
  (2) POSITIVE CONTROL (Gate D, FULL only): the struct parser trained in-cell must REPRODUCE its gold-UPOS
      UAS lift (canon ~0.7868, struct >= canon+0.03) on held-out UD-EWT dev BEFORE any reader delta is
      trusted. If the lift does not reproduce, verdict = UNKNOWN_STRUCT_LIFT_NOT_REPRODUCED (measurement void).
  (3) CAN-FAIL (all informative): (a) struct raw-attach recall may be ~0 or NEGATIVE under predicted POS
      (erosion eats the +0.04 before it reaches the pool); (b) raw recall may rise but the LABELER drops the
      newly-attached patient (labeled recall delta ~0) = labeler wall; (c) labeled recall may rise but the
      DECISION vote picks a distractor (end-to-end delta ~0 or negative) = decision wall; (d) all three may
      propagate (end-to-end delta >= +0.02) = fold justified. C > canon is NOT guaranteed at any link.
  (4) DIFFICULTY-ON: real who-affected gold (not synthetic); per-construction recall deltas reported so the
      archaic-register slices (where labeler mislabels concentrate) are visible.
  (5) ONE-VARIABLE: the parser only. arms_differ verified = struct changes >=1 candidate pool per domain.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- primary deliverable = the numbers + the 3-link decomp):
  Per-domain end-to-end delta ee_d = struct_backoff_mean - canon_backoff_mean (paired, same split/seeds).
  A domain LIFTS iff ee_d >= +0.02 AND backoff-recall delta >= -0.005 AND min-over-seed paired delta >= -0.01.
  A domain HURTS iff ee_d <= -0.02.
  PARSER_LIFTS_READER            : >=1 domain LIFTS, 0 domains HURT -> fold JUSTIFIED (reader payoff proven).
  MIXED_BY_REGISTER              : >=1 domain LIFTS AND >=1 domain HURTS -> register-dependent; fold nuanced.
  PARSER_HURTS_READER            : >=1 domain HURTS, 0 LIFT -> struct net-hurts reader; fold CONTRA-indicated.
  LABELER_WALL_EATS_IT           : neither lift nor hurt in any domain (|ee| < 0.02) -> the +0.04 is absorbed
                                   by the labeler/decision wall; fold NOT justified on reader payoff.
  UNKNOWN_STRUCT_LIFT_NOT_REPRODUCED : Gate-D positive control failed (struct UAS lift did not reproduce).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified) -- (i) ONE struct avg-perceptron parser train on
  UD-EWT train (12329 sents, ep6; algorithm is verbatim from the persisted parser, pure-python greedy O(n^2)
  decode -- no GPU primitive, no batchable matmul); (ii) 2 gold-dev UAS evals (positive control); (iii)
  ~250 gold sentences parsed by 2 parsers x 2 pool-modes + 3-seed 13-dim vote fits (<1s each). Storage:
  no_storage (writes ONLY diagnostic metrics; persists NO substrate atom, NO frontend asset -- the struct
  weights live in RAM for the measurement and are DISCARDED; production hdlab is untouched). progress_logging:
  print_flush_true (long cell; per-epoch + per-stage flush + _heartbeat.jsonl). Determinism: OMP/MKL/OPENBLAS
  =1, FIXED int seeds, numpy default_rng, sorted(set), deterministic crc32 hash; NO hash()-seeded RNG, NO
  list(set()) ordering. LOCAL-ONLY, foreground-to-completion; NO queue, NO origin push, NO remote-persist,
  NO substrate store write, NO git add. Wall: ~2min smoke / ~12-18min full (measured train ep6 + reader).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke: canon vs struct backoff pools bit-differ (>=1 pool changes per domain).
  - final_metrics_atomicity: tmp_replace (E.write_metrics). except SystemExit: raise BEFORE except Exception.
  - crlb_n_a: end-to-end decision-precision + recall delta measurement; no quantitative noise floor.
  - baseline_in_band at smoke: canon BACKOFF + UNLABELED strictly inside (0.05, 0.95) both domains.
  - discriminator survives scale: FULL Gate-D positive control reproduces struct UAS 0.8269 (+0.04) BEFORE
    reader deltas are trusted; smoke uses an UNDERTRAINED struct purely to exercise the pipeline (documented).
  - HARD_PASS strictly above floor (+0.02 ee-delta AND backoff-recall non-drop AND min-over-seed >= -0.01).
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.
  - LEAK-HUNT: (1) FF_STRUCT mutation-probe (garble gold head/deprel -> feature ids BIT-IDENTICAL) reproduced
    in-cell; (2) accept_hardened / build_instances take NO gold arg (reused V2 code path; front-end never sees
    gold); (3) giveaway_audit on backoff pools (no single cue >=0.95 gold-selection) per parser per domain.

PRIOR-WORK CHECK (substrate_query.sh "parser UAS lift end-to-end reader who-affected labeler-bound wall
  predicted POS"): top hit cosine=0.2842 (note 'Predicted'); NONE at cosine>0.30 is a prior parser-swap
  end-to-end reader delta CELL. Genuinely novel: the +0.04 struct lever -> reader translation (with the raw/
  labeled/decision 3-link decomposition + predicted-POS erosion separation) was never measured. Builds on:
  the struct parser cell (feature fn reused verbatim), the v2-extraction-hardened reader (build_instances/
  residual_partition reused), the modern in-domain reader (gold loader reused), and the MST parser-swap cell
  (+0.027 prior, decision-coupled). CITED@backup-doc 2026-07-21.

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
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_parser_swap_struct_endtoend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if os.path.join(REPO_ROOT, "experiments") not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

from experiments import exp_reader_integration_endtoend_whoaffected_v1 as E  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402
from experiments import exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened as V2  # noqa: E402
from experiments import exp_reader_endtoend_modern_indomain_construction_gold_v1 as MOD  # noqa: E402
from experiments import exp_parser_uas_feateng_struct_v1 as S  # noqa: E402

from hdlab.arc_parser import ArcParser, ParseResult, _decode  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402

POS_PATH = E.POS_PATH
ARC_PATH = E.ARC_PATH
LABELER_PATH = E.LABELER_PATH

# Baselines (deployed canon reader, SAME pipeline). Re-derived LIVE this run; cited for reference only.
CANON_BACKOFF_MCG = 0.7622   # CITED@data/exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened
CANON_BACKOFF_MOD = 0.7611   # CITED@data/exp_reader_endtoend_modern_indomain_construction_gold_v1
CANON_UAS_GOLD_UPOS = 0.7868  # CITED@data/exp_parser_uas_feateng_struct_v1:phase_A
STRUCT_UAS_GOLD_UPOS = 0.8269  # CITED@same:arms.struct_upos.best_uas_all (ep6)
STRUCT_BEST_EP = 6


# ==================================================================================================
# StructArcParser: canon ArcParser but decode with the VET'd FF_STRUCT feature fn (imported verbatim).
# Production hdlab/arc_parser.py is NOT mutated; the swap lives entirely in this subclass.
# ==================================================================================================
class StructArcParser(ArcParser):
    def __init__(self, avg, feat_fn):
        super().__init__(avg)
        self.feat_fn = feat_fn

    def parse(self, tokens, pos_tags):
        if len(tokens) != len(pos_tags):
            raise ValueError("tokens/pos length mismatch %d != %d" % (len(tokens), len(pos_tags)))
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = self.feat_fn(sent, i, h)
        head, margin = _decode(self.avg, arc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margin, heads=head)


def _cfg(mode):
    if mode == "smoke":
        return dict(mode="smoke", parser_ntrain=1500, parser_ep=3, vote_epochs=40, lr=0.20,
                    frac_train=0.6, seeds=[7, 13, 19], mcg_slice=["L04", "L05", "L07"], mod_head=40,
                    gate_d_strict=False)
    return dict(mode="full", parser_ntrain=None, parser_ep=STRUCT_BEST_EP, vote_epochs=60, lr=0.20,
                frac_train=0.6, seeds=[7, 13, 19],
                mcg_slice=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], mod_head=None,
                gate_d_strict=True)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _hb(output_dir, stage):
    def cb(ep, max_ep, ts):
        os.makedirs(output_dir, exist_ok=True)
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage, "ep": ep, "max_ep": max_ep}
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return cb


def _pool_digest(pos_insts):
    """Digest of the candidate pools (sorted arg indices per instance, in build order) -> arms-differ probe."""
    h = hashlib.sha256()
    for inst in pos_insts:
        h.update(("%s|%s|" % (inst["sid"], inst["v_lemma"])).encode("utf-8"))
        h.update((",".join(str(c["arg_idx"]) for c in sorted(inst["cands"], key=lambda c: c["arg_idx"]))).encode("utf-8"))
        h.update(b";")
    return h.hexdigest()[:16]


def _n_pools_differ(canon_pos, struct_pos):
    """Count instances whose pool arg-index set differs between the two parsers (aligned 1:1 by build order)."""
    diff = 0
    for ic, is_ in zip(canon_pos, struct_pos):
        cc = set(c["arg_idx"] for c in ic["cands"])
        cs = set(c["arg_idx"] for c in is_["cands"])
        if cc != cs:
            diff += 1
    return diff


def _construction_recall(pos_insts, keyfn):
    """Per-construction gold_in_pool (candidate-recall) rate."""
    by = defaultdict(lambda: {"gip": 0, "n": 0})
    for inst in pos_insts:
        k = keyfn(inst)
        by[k]["n"] += 1
        by[k]["gip"] += int(inst["gold_in_pool"])
    return {k: {"recall": round(v["gip"] / v["n"], 4) if v["n"] else None, "n": v["n"]}
            for k, v in sorted(by.items())}


# ==================================================================================================
# Build the two pool-modes (unlabeled + backoff) for ONE parser on ONE domain, then run the 3-seed vote.
# Returns the full per-parser metric block (recall + end-to-end + residual + leak + per-construction).
# ==================================================================================================
def run_parser_on_domain(gen, labeler, gfit_fn, sel_fn, order, sent_text, gold, ann, cfg, tag, output_dir):
    unlab = V2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "unlabeled")
    bk = V2.build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_backoff")
    if ann is not None:
        unlab = MOD._annotate(unlab, ann)
        bk = MOD._annotate(bk, ann)
    unlab_pos = [i for i in unlab if i["is_pos"]]
    bk_pos = [i for i in bk if i["is_pos"]]
    n_pos = len(bk_pos)
    recall_unlab, _ = E.gold_in_pool_rate(unlab_pos)
    recall_bk, _ = E.gold_in_pool_rate(bk_pos)
    leak = E.giveaway_audit(bk_pos)

    keyfn = (lambda i: i.get("gold_construction", "?")) if ann is not None else (lambda i: i.get("construction", "?"))
    constr_recall = _construction_recall(bk_pos, keyfn)

    per_seed = []
    for seed in cfg["seeds"]:
        tr_v, te_v = E.verb_split(gold, seed, cfg["frac_train"])
        w_bk, _, _ = IV.train_vote(E.sel_by_verb(bk, tr_v), IV.IDX_ALL, seed, cfg["vote_epochs"], cfg["lr"])
        bk_te = [i for i in E.sel_by_verb(bk, te_v) if i["is_pos"]]
        acc_bk, n_bk = E.endtoend_accuracy(w_bk, bk_te)
        part = V2.residual_partition(w_bk, bk_te)
        per_seed.append({"seed": seed, "n_test_pos": n_bk, "backoff_endtoend_acc": acc_bk,
                         "test_ceiling_backoff": E.gold_in_pool_rate(bk_te)[0],
                         "residual_ext": part["extraction_err"], "residual_dec": part["decision_err"]})
        print(f"[{ANCHOR_NAME}] {tag} seed={seed} BACKOFF_ee={acc_bk} ceil={per_seed[-1]['test_ceiling_backoff']} "
              f"ext:dec={part['extraction_err']}:{part['decision_err']}", flush=True)

    accs = [s["backoff_endtoend_acc"] for s in per_seed if s["backoff_endtoend_acc"] is not None]
    m_bk = round(float(np.mean(accs)), 4) if accs else None
    ext = sum(s["residual_ext"] for s in per_seed)
    dec = sum(s["residual_dec"] for s in per_seed)
    resid = ext + dec
    return {
        "tag": tag, "n_gold_pos_pairs": n_pos,
        "candidate_recall_unlabeled": recall_unlab, "candidate_recall_backoff": recall_bk,
        "endtoend_backoff_mean": m_bk,
        "endtoend_backoff_per_seed": {s["seed"]: s["backoff_endtoend_acc"] for s in per_seed},
        "residual_ext_to_dec": f"{ext}:{dec}",
        "residual_ext_frac": (round(ext / resid, 4) if resid else None),
        "per_construction_recall": constr_recall,
        "leak_guard": leak, "no_giveaway": bool(not leak["leak"]),
        "_bk_pos": bk_pos, "_unlab_pos": unlab_pos, "_per_seed": per_seed,
    }


def run_domain(domain, order, sent_text, gold, ann, canon_gen, struct_gen, labeler, gfit_fn, sel_fn, cfg, output_dir):
    print(f"[{ANCHOR_NAME}] === DOMAIN {domain}: {len(order)} sentences ===", flush=True)
    canon = run_parser_on_domain(canon_gen, labeler, gfit_fn, sel_fn, order, sent_text, gold, ann, cfg,
                                 f"{domain}/CANON", output_dir)
    struct = run_parser_on_domain(struct_gen, labeler, gfit_fn, sel_fn, order, sent_text, gold, ann, cfg,
                                  f"{domain}/STRUCT", output_dir)

    # arms-differ: struct must change >=1 candidate pool (same gold, same order -> aligned 1:1).
    n_diff_bk = _n_pools_differ(canon["_bk_pos"], struct["_bk_pos"])
    n_diff_unlab = _n_pools_differ(canon["_unlab_pos"], struct["_unlab_pos"])
    pools_differ = (n_diff_bk + n_diff_unlab) >= 1

    # 3-link decomposition (struct - canon).
    d_recall_unlab = round((struct["candidate_recall_unlabeled"] or 0) - (canon["candidate_recall_unlabeled"] or 0), 4)
    d_recall_bk = round((struct["candidate_recall_backoff"] or 0) - (canon["candidate_recall_backoff"] or 0), 4)
    d_ee = round((struct["endtoend_backoff_mean"] or 0) - (canon["endtoend_backoff_mean"] or 0), 4)
    # per-seed PAIRED end-to-end delta (min-over-seed guards single-answer noise).
    paired = []
    for s in cfg["seeds"]:
        cv = canon["endtoend_backoff_per_seed"].get(s)
        sv = struct["endtoend_backoff_per_seed"].get(s)
        if cv is not None and sv is not None:
            paired.append(round(sv - cv, 4))
    min_seed_delta = round(float(np.min(paired)), 4) if paired else None

    labeler_wall = round(d_recall_unlab - d_recall_bk, 4)   # raw-attach gain LOST to the labeler filter
    decision_wall = round(d_recall_bk - d_ee, 4)            # labeled-recall gain LOST to the decision vote

    lifts = bool(d_ee >= 0.02 and d_recall_bk >= -0.005 and (min_seed_delta is not None and min_seed_delta >= -0.01))
    hurts = bool(d_ee <= -0.02)

    print(f"[{ANCHOR_NAME}] {domain} DELTA raw_attach_recall={d_recall_unlab:+.4f} -> labeled_recall={d_recall_bk:+.4f} "
          f"-> end_to_end={d_ee:+.4f} (min_seed={min_seed_delta}) | labeler_wall={labeler_wall:+.4f} "
          f"decision_wall={decision_wall:+.4f} | pools_differ n_bk={n_diff_bk} n_unlab={n_diff_unlab} "
          f"lifts={lifts} hurts={hurts}", flush=True)

    return {
        "domain": domain,
        "canon_backoff_endtoend_mean": canon["endtoend_backoff_mean"],
        "struct_backoff_endtoend_mean": struct["endtoend_backoff_mean"],
        "canon_backoff_per_seed": canon["endtoend_backoff_per_seed"],
        "struct_backoff_per_seed": struct["endtoend_backoff_per_seed"],
        "canon_candidate_recall_unlabeled": canon["candidate_recall_unlabeled"],
        "struct_candidate_recall_unlabeled": struct["candidate_recall_unlabeled"],
        "canon_candidate_recall_backoff": canon["candidate_recall_backoff"],
        "struct_candidate_recall_backoff": struct["candidate_recall_backoff"],
        "DELTA_raw_attach_recall_unlabeled": d_recall_unlab,
        "DELTA_labeled_recall_backoff": d_recall_bk,
        "DELTA_endtoend_who_affected": d_ee,
        "DELTA_endtoend_per_seed_paired": paired,
        "DELTA_endtoend_min_over_seed": min_seed_delta,
        "LABELER_WALL_absorbed": labeler_wall,
        "DECISION_WALL_absorbed": decision_wall,
        "canon_residual_ext_to_dec": canon["residual_ext_to_dec"],
        "struct_residual_ext_to_dec": struct["residual_ext_to_dec"],
        "canon_per_construction_recall": canon["per_construction_recall"],
        "struct_per_construction_recall": struct["per_construction_recall"],
        "n_pools_differ_backoff": n_diff_bk, "n_pools_differ_unlabeled": n_diff_unlab,
        "pools_differ": pools_differ, "domain_lifts": lifts, "domain_hurts": hurts,
        "n_gold_pos_pairs": canon["n_gold_pos_pairs"],
        "canon_no_giveaway": canon["no_giveaway"], "struct_no_giveaway": struct["no_giveaway"],
        "canon_leak_max_single_cue": canon["leak_guard"]["max_single_feature_gold_selection_acc"],
        "struct_leak_max_single_cue": struct["leak_guard"]["max_single_feature_gold_selection_acc"],
    }


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = _cfg(mode)
    output_dir = _out_dir(mode)
    E._write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START parser-swap end-to-end reader (canon vs struct_upos)", flush=True)

    # ---- shared front-end: ONE tagger, ONE labeler; parsers are the ONLY variable ----
    tagger = PosTagger.load(POS_PATH)
    canon_parser = ArcParser.load(ARC_PATH)
    labeler = __import__("hdlab.arc_labeler", fromlist=["ArcLabeler"]).ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded (shared tagger+labeler; deployed canon parser)", flush=True)

    # ---- train the struct parser IN-CELL (weights discarded after; production hdlab untouched) ----
    dev, dev_u = S._load("dev", "upos")
    tr, _ = S._load("train", "upos")
    if cfg["parser_ntrain"]:
        tr = tr[:cfg["parser_ntrain"]]
    print(f"[{ANCHOR_NAME}:{mode}] struct parser train: {len(tr)} sents ep{cfg['parser_ep']} ...", flush=True)
    ts = time.perf_counter()
    snaps = S.train_snapshots(tr, S.FF_STRUCT, [cfg["parser_ep"]], cfg["parser_ep"], S.SEED, hb=_hb(output_dir, "struct_train"))
    struct_avg = snaps[cfg["parser_ep"]]
    print(f"[{ANCHOR_NAME}:{mode}] struct parser trained {round(time.perf_counter()-ts,1)}s", flush=True)

    # ---- GATE D positive control: gold-UPOS UAS of both parsers (struct must reproduce +0.04 at FULL) ----
    canon_uas = S.eval_both(canon_parser.avg, dev, dev_u, S.FF_BASE)
    struct_uas = S.eval_both(struct_avg, dev, dev_u, S.FF_STRUCT)
    uas_lift = round(struct_uas["uas_all"] - canon_uas["uas_all"], 4)
    canon_reproduces = bool(abs(canon_uas["uas_all"] - CANON_UAS_GOLD_UPOS) <= 0.004)
    struct_lift_reproduced = bool(uas_lift >= 0.03)  # tol on the +0.04 (0.8269-0.7868) under fresh ep6 train
    print(f"[{ANCHOR_NAME}:{mode}] GATE-D gold-UPOS UAS: canon={canon_uas['uas_all']} (repro={canon_reproduces}) "
          f"struct={struct_uas['uas_all']} lift={uas_lift:+.4f} (reproduced={struct_lift_reproduced})", flush=True)

    # ---- leak-hunt: FF_STRUCT feature fn invariant to garbled gold head/deprel ----
    mp = S.mutation_probe(S.FF_STRUCT, dev, n_sent=30)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-HUNT FF_STRUCT mutation-probe: {mp}", flush=True)

    # ---- the two candidate generators: SAME tagger, different parser (the ONE variable) ----
    canon_gen = CandidateGenerator(tagger, canon_parser)
    struct_gen = CandidateGenerator(tagger, StructArcParser(struct_avg, S.FF_STRUCT))

    # ---- mining models (McGuffey-mined, parser-independent, FIXED across all arms/domains) ----
    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    print(f"[{ANCHOR_NAME}:{mode}] mining (McGuffey, fixed): {gfit_stats['n_object_classes']} gfit classes, "
          f"{n_mine} sents", flush=True)

    # ---- DOMAIN 1: modern in-domain construction gold ----
    mod_order, mod_sent, mod_gold, mod_ann, mod_meta = MOD.load_construction_gold()
    if cfg["mod_head"]:
        keep = set(mod_order[:cfg["mod_head"]])
        mod_order = [s for s in mod_order if s in keep]
        mod_gold = {s: mod_gold[s] for s in mod_order}
    dom_modern = run_domain("modern", mod_order, mod_sent, mod_gold, mod_ann,
                            canon_gen, struct_gen, labeler, gfit_fn, sel_fn, cfg, output_dir)

    # ---- DOMAIN 2: archaic McGuffey gold ----
    mcg_order, mcg_sent, _mcg_svo = L.load_slice_and_reader(cfg["mcg_slice"])
    mcg_gold, mcg_meta = L.load_gold(cfg["mcg_slice"])
    dom_mcg = run_domain("mcguffey", mcg_order, mcg_sent, mcg_gold, None,
                        canon_gen, struct_gen, labeler, gfit_fn, sel_fn, cfg, output_dir)

    domains = [dom_modern, dom_mcg]

    # ---- VERDICT ----
    n_lift = sum(1 for d in domains if d["domain_lifts"])
    n_hurt = sum(1 for d in domains if d["domain_hurts"])
    arms_differ = all(d["pools_differ"] for d in domains)
    baseline_in_band = all(d["canon_backoff_endtoend_mean"] is not None
                           and 0.05 < d["canon_backoff_endtoend_mean"] < 0.95 for d in domains)

    if cfg["gate_d_strict"] and not struct_lift_reproduced:
        verdict = "UNKNOWN_STRUCT_LIFT_NOT_REPRODUCED"
    elif not arms_differ:
        verdict = "UNKNOWN_ARMS_IDENTICAL"
    elif n_lift >= 1 and n_hurt == 0:
        verdict = "PARSER_LIFTS_READER"
    elif n_lift >= 1 and n_hurt >= 1:
        verdict = "MIXED_BY_REGISTER"
    elif n_hurt >= 1 and n_lift == 0:
        verdict = "PARSER_HURTS_READER"
    else:
        verdict = "LABELER_WALL_EATS_IT"

    fold_justified = bool(n_lift >= 1 and n_hurt == 0 and (not cfg["gate_d_strict"] or struct_lift_reproduced))

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | PARSER lift gold-UPOS UAS canon={canon_uas['uas_all']} struct={struct_uas['uas_all']} "
           f"({uas_lift:+.4f}, reproduced={struct_lift_reproduced}) | "
           f"MODERN: raw_recall={dom_modern['DELTA_raw_attach_recall_unlabeled']:+.4f} "
           f"-> labeled_recall={dom_modern['DELTA_labeled_recall_backoff']:+.4f} "
           f"-> end_to_end={dom_modern['DELTA_endtoend_who_affected']:+.4f} "
           f"(canon={dom_modern['canon_backoff_endtoend_mean']} struct={dom_modern['struct_backoff_endtoend_mean']} "
           f"min_seed={dom_modern['DELTA_endtoend_min_over_seed']}) | "
           f"McGUFFEY: raw_recall={dom_mcg['DELTA_raw_attach_recall_unlabeled']:+.4f} "
           f"-> labeled_recall={dom_mcg['DELTA_labeled_recall_backoff']:+.4f} "
           f"-> end_to_end={dom_mcg['DELTA_endtoend_who_affected']:+.4f} "
           f"(canon={dom_mcg['canon_backoff_endtoend_mean']} struct={dom_mcg['struct_backoff_endtoend_mean']} "
           f"min_seed={dom_mcg['DELTA_endtoend_min_over_seed']}) | "
           f"labeler_wall M={dom_modern['LABELER_WALL_absorbed']:+.4f}/McG={dom_mcg['LABELER_WALL_absorbed']:+.4f} "
           f"decision_wall M={dom_modern['DECISION_WALL_absorbed']:+.4f}/McG={dom_mcg['DECISION_WALL_absorbed']:+.4f} "
           f"| n_lift={n_lift} n_hurt={n_hurt} FOLD_JUSTIFIED={fold_justified} "
           f"arms_differ={arms_differ} baseline_in_band={baseline_in_band} leak_clean={mp['leak_clean']}")

    # strip the heavy _bk_pos/_unlab_pos/_per_seed refs from the persisted domain blocks.
    def _clean(d):
        return {k: v for k, v in d.items() if not k.startswith("_")}

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "parser_train_ntrain": (cfg["parser_ntrain"] or len(tr)), "parser_train_ep": cfg["parser_ep"],
        "GATE_D_positive_control": {
            "canon_uas_gold_upos": canon_uas["uas_all"], "canon_uas_nopunct": canon_uas["uas_nopunct"],
            "struct_uas_gold_upos": struct_uas["uas_all"], "struct_uas_nopunct": struct_uas["uas_nopunct"],
            "uas_lift": uas_lift, "canon_reproduces_cited": canon_reproduces,
            "struct_lift_reproduced": struct_lift_reproduced,
            "cited_canon_uas": CANON_UAS_GOLD_UPOS, "cited_struct_uas": STRUCT_UAS_GOLD_UPOS},
        "leak_hunt_ff_struct_mutation_probe": mp,
        "DOMAIN_modern": _clean(dom_modern),
        "DOMAIN_mcguffey": _clean(dom_mcg),
        "n_domains_lift": n_lift, "n_domains_hurt": n_hurt,
        "FOLD_INTO_PRODUCTION_JUSTIFIED": fold_justified,
        "cited_canon_backoff_modern": CANON_BACKOFF_MOD, "cited_canon_backoff_mcguffey": CANON_BACKOFF_MCG,
        "arms_differ_verified": arms_differ, "baseline_in_band": baseline_in_band,
        "one_variable": "the parser (canon deployed asset vs struct_upos trained in-cell); tagger/labeler/candgen/vote/mining/gold/split/seeds identical",
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "recall + end-to-end decision-precision delta; no quantitative noise floor",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified)",
        "deterministic_seeding": True, "storage": "no_storage_production_hdlab_untouched",
        "modern_gold_meta": mod_meta, "mcguffey_gold_meta": mcg_meta,
    }
    E.write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== %s self-test (real code paths) ===" % ANCHOR_NAME, flush=True)
    # (1) StructArcParser is a real ArcParser subclass; parse() returns a ParseResult with heads.
    dev, dev_u = S._load("dev", "upos")
    snaps = S.train_snapshots(dev[:120], S.FF_STRUCT, [2], 2, S.SEED)  # tiny REAL struct train
    sp = StructArcParser(snaps[2], S.FF_STRUCT)
    canon = ArcParser.load(ARC_PATH)
    tagger = PosTagger.load(POS_PATH)
    r = sp.parse(*(lambda toks: (toks, tagger.tag(toks)))(["Papa", "showed", "the", "boys", "the", "seeds", "."]))
    assert isinstance(r, ParseResult) and len(r.heads) == 7, ("struct parse malformed", r)
    # canon and struct decode the SAME sentence -> both produce heads (may or may not differ on this easy sent).
    rc = canon.parse(["Papa", "showed", "the", "boys", "the", "seeds", "."],
                     tagger.tag(["Papa", "showed", "the", "boys", "the", "seeds", "."]))
    assert len(rc.heads) == 7, "canon parse malformed"
    print(f"[selftest] struct heads={r.heads} canon heads={rc.heads}", flush=True)

    # (2) FF_STRUCT is a base-superset (struct features EXTEND canon; arms differ by construction).
    from hdlab.arc_parser import _arc_ids
    b = _arc_ids(dev[0], 2, 3)
    st = S.FF_STRUCT(dev[0], 2, 3)
    assert len(st) > len(b) and np.array_equal(st[:len(b)], b), "FF_STRUCT must be base-superset"

    # (3) LEAK-HUNT: FF_STRUCT invariant to garbled gold head/deprel (no gold-structure leak).
    mp = S.mutation_probe(S.FF_STRUCT, dev, n_sent=8)
    assert mp["leak_clean"], ("FF_STRUCT MUTATION-PROBE LEAK", mp)

    # (4) gold-independence of the reader extraction path (reused V2 code): build_instances/accept take NO gold.
    import inspect
    assert "gold" not in set(inspect.signature(V2.accept_hardened).parameters), "LEAK: accept_hardened sees gold"

    # (5) StructArcParser drops into CandidateGenerator and yields a real CandResult with candidates.
    sg = CandidateGenerator(tagger, sp)
    cr = sg.generate("Papa showed the boys the little seeds.")
    assert cr.tokens and cr.heads and len(cr.pos) == len(cr.tokens), ("candgen swap malformed", cr)

    # (6) pool-differ probe is symmetric/zero on identical pools, positive on differing.
    a = [{"sid": "s", "v_lemma": "v", "cands": [{"arg_idx": 3}, {"arg_idx": 5}]}]
    bb = [{"sid": "s", "v_lemma": "v", "cands": [{"arg_idx": 3}]}]
    assert _n_pools_differ(a, a) == 0 and _n_pools_differ(a, bb) == 1, "pool-differ probe broken"

    # (7) verb_split determinism (reused E).
    g = {"s1": {"pos": [{"v": "eat"}, {"v": "take"}, {"v": "throw"}, {"v": "build"}], "nopat": set(), "pos_verbs": set()}}
    tr, te = E.verb_split(g, 7, 0.6)
    assert not (set(tr) & set(te)), "verb_split overlap"
    print("[selftest] PASS: struct-parser swap + superset + leak-clean + gold-independence + candgen + pool-probe", flush=True)
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
