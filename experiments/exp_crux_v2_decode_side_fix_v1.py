"""
crux_v2_decode_side_fix_v1 -- DECODE-SIDE FIX for the crux v2 HARD_FAIL_A (confidence-rerank + relaxed gate).

WHY (disambiguation result, MEASURED@data/exp_crux_v2_decode_budget_sweep_v1/metrics.json). The
  decode-budget sweep proved the crux v2 wall is DECODE-side, not encode: at t_iter 20->100 the RAW
  candidate-recall@10 was DEAD FLAT (0.1333) BUT gold-surfaced-at-any-rank rose 0.213->0.300 raw
  (0.615->0.865 of reachable). The gold IS recoverable from the FROZEN bundle (encode did not destroy
  it); it just was not RANKED into the top-10. Root cause pinned to two decode artifacts in
  crux.resonator_recover:
    (A) rank_score = t_iter - it  -> rewards recovery ORDER; the first ~10 deflation picks are
        identical regardless of t_iter, so top-10 is STRUCTURALLY frozen and late-but-correct golds
        (small residual coefficient after crosstalk removed) can never enter top-10.
    (B) RESIDUAL RE-BIND GATE at rebind_k=2.5 * sigma0(INITIAL sims) -> a fixed high floor that
        rejects genuine late recoveries (gated@10 flat 0.060 while at-any-rank hit 0.300).

THE FIX (three decode-side changes; encode/compose FROZEN, byte-identical to crux v2 via import):
  1. CONFIDENCE RANK (load-bearing): rank each recovered candidate by its matching-pursuit COEFFICIENT
     (peak residual-similarity pv at time of recovery, union-MAX over restarts/iterations) instead of
     recovery order. Matching pursuit explains-away strong crosstalk first, so a genuine late gold's pv
     estimates its TRUE bundle coefficient (crosstalk-removed) -- the resonator's actual value-add. A
     late-but-high-confidence gold now ranks INTO the top-10.
  2. RELAXED / RE-BASED GATE: replace the fixed rebind_k*sigma0(initial) floor with a PER-ITERATION
     relative gate pv > GATE_K * sigma_it, sigma_it = MAD of the CURRENT residual's sims that step
     (1.4826*MAD). A genuine late recovery that stands above ITS residual's noise floor passes; pure
     crosstalk does not. GATE_K is set on the PLANTED self-test (genuine late gold passes; spurious
     late recovery gated out) -- NOT tuned on eval (no p-hacking). Report BOTH gated + ungated recall@10.
  3. BUDGET t_iter >= 80: sweep showed at-any-rank still climbing at t_iter=100; use enough budget to
     surface the golds, then confidence-rank them. T_ITER=100 (smoke) / 100 (full).

PRE-REGISTERED BARS (relative to THIS run's own arms; regime-robust):
  STAGE-1 (the fix WORKS -- decode recovers the buried recall):
     res_conf_gated_recall@10 >= single_shot_recall@10 + STAGE1_MARGIN   (clears single-shot)
     AND res_conf ranking closes a material fraction of the (sym_ceiling - single_shot) gap.
  STAGE-2 (the prize -- reasoning engine BEATS frequency):
     RESONATOR_CONF_GT.mrr >= POP_RELFREQ.mrr + EPS  AND  .h@1 >= POP_RELFREQ.h@1 + EPS.
  Load-bearing gates: BIND_ABLATED.mrr <= 0.7*res.mrr (bind load-bearing); BROKEN.mrr <= 0.5*res.mrr.
  HONEST INFO-CEILING (flagged, per compute-the-ceiling discipline): candidate-recall ceiling caps mrr
  at ~ceiling (unreachable golds contribute 0); POP_RELFREQ ranks ALL entities (not reach-capped), so
  STAGE-2 can be near-unattainable on a small smoke subgraph even with perfect decode -- a STAGE-1
  pass + STAGE-2 fail is the informative "recall recovered, frequency-wall moves" outcome (HARD_FAIL_B
  class), reported honestly, not a cell defect. Degree-stratified (low/mid/high tertile) reported since
  the crux-v2 gap concentrated in mid/high-degree tertiles.

CONTRACT. Encode/compose is FROZEN: bundles built by crux.build_query_bundle (imported, byte-identical).
  ONLY the decode readout is new (this file). SMOKE runs local on the crux-v2 smoke frozen config.
  FULL is the multi-seed GPU canonical judge (dispatched by the orchestrator to overnight_queue/remote).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (hash-test on per-arm metric dicts)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash writer os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: rank-based KG-completion, no closed-form noise floor; reachability via candidate-recall
#   ceiling > POP_RELFREQ.h@1 => beat physically reachable on the queries where gold is proposed.
# - baseline_in_band: POP_RELFREQ neither 0 nor 1 at smoke.
# - discriminator survives scale: self-test (planted rerank+gate, scale-independent) fires; FULL is the
#   canonical beat-frequency judge. GATE_K set on planted self-test, fixed constant applied to eval.
# - calibration_check: adaptive_with_discriminator_gate -- GATE_K per-iteration MAD floor; planted
#   self-test asserts genuine-passes / spurious-rejected still fires at the chosen GATE_K.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; verdict counts len(per_seed).
# - progress_logging: print_flush_true (smoke < 5min; full emits per-seed + per-eval-arm progress lines).
# - all numbers in header tagged MEASURED@/THEORETICAL@.

ASCII-only. write_metrics. RUN_MODE defaults to full (runner invokes with no argv); --smoke for local.
"""
from __future__ import annotations
import sys, os, argparse, time, json, math, random, traceback, platform
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
# import the FROZEN crux v2 encode/compose + arm scaffolding (byte-identical bundle)
import experiments.exp_crux_engine_v2_resonator_decode_v1 as crux

ANCHOR_NAME = "crux_v2_decode_side_fix_v1"

DEVICE = crux.DEVICE
CUDA_AVAIL = crux.CUDA_AVAIL

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---- frozen encode config (inherit crux v2) ----
MIN_CONF = crux.MIN_CONF          # 0.05
L_MAX = crux.L_MAX                # 3
RECALL_C = 10
HITS_KS = (1, 10)
EPS = 0.02                        # META_RULE_L strict-above-floor margin (STAGE-2 beat-frequency)
STAGE1_MARGIN = 0.02              # STAGE-1: res_conf_gated_recall@10 must clear single_shot by this

# ---- DECODE-FIX params ----
TAU = crux.RES_TAU                # 0.4 init-only dither (inherit)
# GATE_K set on the planted self-test below (genuine late gold passes; spurious late recovery rejected).
# Per-iteration relative gate pv > GATE_K * (1.4826*MAD of current residual sims). 3.0 = ~3 robust-sigma.
GATE_K = 3.0

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 2048
    N_EVAL = 150
    TOP_K_RELS = 25
    PROFILE_EDGES_PER_REL = 120
    HUB_CAP = 20000
    BRANCH_CAP = 15
    PATH_CAP = 250
    MIN_SUPPORT = 3
    T_ITER = 100
    N_RESTART = 8
else:
    SEEDS = [7, 17, 23]
    N_DIM = 2048
    N_EVAL = 3000
    TOP_K_RELS = 0
    PROFILE_EDGES_PER_REL = 1000
    HUB_CAP = 60000
    BRANCH_CAP = 30
    PATH_CAP = 800
    MIN_SUPPORT = 10
    T_ITER = 100
    N_RESTART = 16


# ============================ DECODE-SIDE FIX: confidence-rank resonator ============================
def resonator_recover_conf(q, E, cand_ids, n_dim, t_iter, n_restart, tau, gate_k, gen):
    """Confidence-ranked deflation cleanup. Returns (raw_scores, gated_scores, telem).

    FIX vs crux.resonator_recover:
      - rank score = matching-pursuit COEFFICIENT pv (peak residual-sim at recovery), union-MAX over
        restarts/iters -- NOT recovery order (t_iter - it). A late-but-strong gold now ranks high.
      - gate = PER-ITERATION relative floor pv > gate_k * (1.4826*MAD of current residual sims), NOT a
        fixed rebind_k*sigma0(initial). Genuine late recoveries above their residual noise pass.
    """
    if not cand_ids:
        return {}, {}, {"n_raw": 0, "n_gated": 0, "spurious_rate": 0.0, "n_iter": 0}
    idx = torch.tensor(cand_ids, device=DEVICE)
    Ecand = E[idx]                                    # (n_cand, N)
    Q = q.unsqueeze(0).repeat(n_restart, 1)           # (R, N)
    if tau > 0.0:
        ph = (torch.rand(n_restart, n_dim, generator=gen) * (2.0 * math.pi)).to(DEVICE)
        amp = (tau * torch.ones(n_restart, n_dim)).to(DEVICE)
        Q = Q + torch.polar(amp, ph).to(torch.complex64)
    residual = Q.clone()
    raw_scores, gated_scores = {}, {}
    n_iter_used = 0
    for it in range(t_iter):
        sim = (residual @ Ecand.conj().t()).real / n_dim     # (R, n_cand)  N_DIM x N_entities matmul
        pk = sim.argmax(dim=1)                                # (R,)
        pv = sim.gather(1, pk.unsqueeze(1)).squeeze(1)        # (R,) matching-pursuit coefficient
        # per-iteration robust noise floor (pooled over restarts) -> relative gate
        flat = sim.reshape(-1)
        med = flat.median()
        mad = (flat - med).abs().median()
        sigma_it = float(1.4826 * mad)
        thresh = gate_k * max(sigma_it, 1e-9)
        for r in range(n_restart):
            ci = int(idx[pk[r]].item()); v = float(pv[r])
            if v > raw_scores.get(ci, -1e18):
                raw_scores[ci] = v                           # CONFIDENCE rank = max coefficient
            if v > thresh and v > gated_scores.get(ci, -1e18):
                gated_scores[ci] = v                         # relaxed per-iteration gate
            residual[r] = residual[r] - pv[r] * Ecand[pk[r]] # deflate (explain-away)
        n_iter_used = it + 1
    n_raw = len(raw_scores); n_gated = len(gated_scores)
    return raw_scores, gated_scores, {"n_raw": n_raw, "n_gated": n_gated,
                                      "spurious_rate": (n_raw - n_gated) / max(n_raw, 1),
                                      "n_iter": n_iter_used}


# ============================ per-seed (FROZEN encode + FIXED decode) ============================
def run_seed(train, valid, test, ent2i, rel2i, seed):
    rng = random.Random(seed)
    n_ent = len(ent2i)
    R = crux.make_rel_vectors(len(rel2i), N_DIM, seed)

    rel_freq = Counter()
    for (h, r, t) in train:
        rel_freq[rel2i[r]] += 1
    if TOP_K_RELS and TOP_K_RELS < len(rel2i):
        target_rels = [r for r, _ in rel_freq.most_common(TOP_K_RELS)]
    else:
        target_rels = list(rel2i.values())
    target_set = set(target_rels)

    gd = crux.Graph(train, ent2i, rel2i)
    known = defaultdict(set)
    for tr in (train, valid, test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])

    tq_all = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in test if rel2i[r] in target_set]
    rng.shuffle(tq_all)
    tq = tq_all[:N_EVAL]

    (conf, prof_bind, prof_add, prof_neg_bind, prof_neg_add, allpat, cc_bind, cc_add,
     pos_rtups, neg_rtups) = crux.build_models(
        gd, target_rels, R, N_DIM, MIN_SUPPORT, MIN_CONF,
        PROFILE_EDGES_PER_REL, L_MAX, BRANCH_CAP, PATH_CAP, seed)
    n_rules = sum(len(v) for v in conf.values())

    E = crux.make_entity_vectors(n_ent, N_DIM, seed)

    cand_cache, q_cache = {}, {}
    def get_cand(h, r3):
        d = cand_cache.get((h, r3))
        if d is None:
            d = crux.propose_candidates(gd, h, r3, L_MAX, BRANCH_CAP, PATH_CAP)
            cand_cache[(h, r3)] = d
        return d
    def get_q(h, r3, op):
        v = q_cache.get((h, r3, op))
        if v is None:
            v = crux.build_query_bundle(get_cand(h, r3), conf.get(r3, {}), cc_bind, E, N_DIM, op)
            q_cache[(h, r3, op)] = v
        return v

    res_cache = {}
    def get_res(h, r3, op):
        v = res_cache.get((h, r3, op))
        if v is None:
            q, cand_ids = get_q(h, r3, op)
            gseed = (seed * 100003 + (h % 99991) * 131 + r3 * 17 + (7 if op == "bind" else 11)) & 0x7fffffff
            gen = torch.Generator().manual_seed(gseed)
            v = resonator_recover_conf(q, E, cand_ids, N_DIM, T_ITER, N_RESTART, TAU, GATE_K, gen)
            res_cache[(h, r3, op)] = v
        return v

    # ---- arms ----
    def single_shot_rank(h, r, gold, filt, rr):
        q, cand_ids = get_q(h, r, "bind")
        return crux.strict_rank(crux.single_shot_scores(q, E, cand_ids, N_DIM), gold, filt, rr)
    m_single = crux.eval_arm(single_shot_rank, tq, known, arm_label="SINGLE_SHOT")

    def res_conf_gated_rank(h, r, gold, filt, rr):        # HEADLINE arm (gated)
        _, gtd, _ = get_res(h, r, "bind")
        return crux.strict_rank(gtd, gold, filt, rr)
    m_res = crux.eval_arm(res_conf_gated_rank, tq, known, arm_label="RESONATOR_CONF_GT")

    def res_conf_raw_rank(h, r, gold, filt, rr):          # ungated diagnostic
        raw, _, _ = get_res(h, r, "bind")
        return crux.strict_rank(raw, gold, filt, rr)
    m_res_raw = crux.eval_arm(res_conf_raw_rank, tq, known)

    def ablated_rank(h, r, gold, filt, rr):               # bind->add, must collapse
        _, gtd, _ = get_res(h, r, "add")
        return crux.strict_rank(gtd, gold, filt, rr)
    m_abl = crux.eval_arm(ablated_rank, tq, known, arm_label="BIND_ABLATED")

    def symbolic_rank(h, r, gold, filt, rr):
        return crux.strict_rank(crux.score_symbolic(get_cand(h, r), r, conf), gold, filt, rr)
    m_sym = crux.eval_arm(symbolic_rank, tq, known)

    brng = random.Random(seed * 991 + 7)
    ent_rand = [brng.random() for _ in range(n_ent)]
    def broken_rank(h, r, gold, filt, rr):
        return crux.strict_rank(crux.score_broken(get_cand(h, r), ent_rand), gold, filt, rr)
    m_broken = crux.eval_arm(broken_rank, tq, known)

    def pop_relfreq_rank(h, r, gold, filt, rr):
        return crux.pop_rank(gd.rel_tail_freq.get(r, Counter()), gold, filt, rr, n_ent)
    m_pop_rf = crux.eval_arm(pop_relfreq_rank, tq, known)

    def pop_deg_rank(h, r, gold, filt, rr):
        return crux.pop_rank(gd.node_degree, gold, filt, rr, n_ent)
    m_pop_deg = crux.eval_arm(pop_deg_rank, tq, known)

    # ---- recall@C + ceiling + gate telemetry ----
    ss_rC = sym_rC = resg_rC = resraw_rC = ceil_hit = 0
    n_gated_sum = n_raw_sum = 0
    for (h, r, gold) in tq:
        filt = known.get((h, r), set()) - {gold}
        cand = get_cand(h, r)
        if (gold in cand) and (gold not in filt):
            ceil_hit += 1
        q_b, cand_ids = get_q(h, r, "bind")
        sc_ss = crux.single_shot_scores(q_b, E, cand_ids, N_DIM)
        sc_s = crux.score_symbolic(cand, r, conf)
        raw, gtd, tel = get_res(h, r, "bind")
        if crux.topc_has_gold(sc_ss, gold, filt, RECALL_C): ss_rC += 1
        if crux.topc_has_gold(sc_s, gold, filt, RECALL_C): sym_rC += 1
        if crux.topc_has_gold(gtd, gold, filt, RECALL_C): resg_rC += 1
        if crux.topc_has_gold(raw, gold, filt, RECALL_C): resraw_rC += 1
        n_gated_sum += tel["n_gated"]; n_raw_sum += tel["n_raw"]
    nq = len(tq)
    ceiling = ceil_hit / nq

    # ---- degree-stratified (low/mid/high tertile): RESONATOR_CONF vs POP_RELFREQ ----
    gold_degs = sorted(gd.node_degree.get(g_, 0) for (_, _, g_) in tq)
    q1 = gold_degs[len(gold_degs) // 3] if gold_degs else 0
    q2 = gold_degs[2 * len(gold_degs) // 3] if gold_degs else 0
    def _strat(node):
        dgr = gd.node_degree.get(node, 0)
        return "low" if dgr <= q1 else ("mid" if dgr <= q2 else "high")
    strat_of_gold = {g_: _strat(g_) for (_, _, g_) in tq}
    sn = ("low", "mid", "high")
    ds_res = crux.eval_arm_stratified(res_conf_gated_rank, tq, known, strat_of_gold, sn)
    ds_pf = crux.eval_arm_stratified(pop_relfreq_rank, tq, known, strat_of_gold, sn)
    degree_stratified = {s: {
        "n": ds_res[s]["n"], "deg_tertile_bounds": [q1, q2],
        "RESONATOR_CONF_GT": {"hits@1": ds_res[s]["hits@1"], "mrr": ds_res[s]["mrr"]},
        "POP_RELFREQ": {"hits@1": ds_pf[s]["hits@1"], "mrr": ds_pf[s]["mrr"]},
        "margin_vs_relfreq": {"hits@1": ds_res[s]["hits@1"] - ds_pf[s]["hits@1"],
                              "mrr": ds_res[s]["mrr"] - ds_pf[s]["mrr"]},
    } for s in sn}

    return {
        "seed": seed, "n_ent": n_ent, "n_rel": len(rel2i), "n_train": len(train),
        "n_test_eval": nq, "n_rules": n_rules, "N_DIM": N_DIM, "GATE_K": GATE_K, "T_ITER": T_ITER,
        "device": str(DEVICE), "cuda_avail": CUDA_AVAIL, "ceiling": ceiling,
        "RESONATOR_CONF_GT": m_res, "RESONATOR_CONF_RAW": m_res_raw, "SINGLE_SHOT": m_single,
        "BIND_ABLATED": m_abl, "SYMBOLIC_GT": m_sym, "POP_RELFREQ": m_pop_rf, "POP_DEGREE": m_pop_deg,
        "BROKEN_VERIFIER": m_broken,
        "res_conf_gated_recall@%d" % RECALL_C: resg_rC / nq,
        "res_conf_raw_recall@%d" % RECALL_C: resraw_rC / nq,
        "single_shot_recall@%d" % RECALL_C: ss_rC / nq,
        "sym_recall@%d" % RECALL_C: sym_rC / nq,
        "mean_n_gated": n_gated_sum / nq, "mean_n_raw": n_raw_sum / nq,
        "degree_stratified": degree_stratified,
    }


# ============================ verdict ============================
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_verdict(per_seed):
    def agg(arm, k):
        return _mean([s[arm][k] for s in per_seed])
    res1 = agg("RESONATOR_CONF_GT", "hits@1"); resmrr = agg("RESONATOR_CONF_GT", "mrr")
    res10 = agg("RESONATOR_CONF_GT", "hits@10")
    ss1 = agg("SINGLE_SHOT", "hits@1"); ssmrr = agg("SINGLE_SHOT", "mrr")
    abl_mrr = agg("BIND_ABLATED", "mrr")
    sym1 = agg("SYMBOLIC_GT", "hits@1"); symmrr = agg("SYMBOLIC_GT", "mrr")
    pf1 = agg("POP_RELFREQ", "hits@1"); pfmrr = agg("POP_RELFREQ", "mrr")
    b1 = agg("BROKEN_VERIFIER", "hits@1"); bmrr = agg("BROKEN_VERIFIER", "mrr")
    ceil = _mean([s["ceiling"] for s in per_seed])

    RCK = "res_conf_gated_recall@%d" % RECALL_C
    RRK = "res_conf_raw_recall@%d" % RECALL_C
    SCK = "single_shot_recall@%d" % RECALL_C
    SYK = "sym_recall@%d" % RECALL_C
    res_gated = _mean([s[RCK] for s in per_seed])       # HEADLINE STAGE-1 metric
    res_raw = _mean([s[RRK] for s in per_seed])
    ss_recall = _mean([s[SCK] for s in per_seed])
    sym_recall = _mean([s[SYK] for s in per_seed])

    # STAGE-1: fix recovers recall -> gated recall clears single_shot + closes the (sym - ss) gap
    stage1_pass = (res_gated >= ss_recall + STAGE1_MARGIN)
    gap_closed_frac = ((res_gated - ss_recall) / max(sym_recall - ss_recall, 1e-9)) \
        if (sym_recall - ss_recall) > 0 else 0.0
    # STAGE-2: the prize -- reranked engine beats frequency
    stage2_pass = (resmrr >= pfmrr + EPS) and (res1 >= pf1 + EPS)
    # load-bearing gates
    bind_loadbearing = (abl_mrr <= 0.7 * max(resmrr, 1e-9))
    broken_fails = (bmrr <= 0.5 * max(resmrr, 1e-9)) and (b1 <= 0.5 * max(res1, 1e-9))

    hard_pass = stage1_pass and stage2_pass and bind_loadbearing and broken_fails
    if hard_pass:
        v = "HARD_PASS"
    elif stage1_pass and (not stage2_pass):
        v = "HARD_FAIL_B_WALL_MOVES"        # recall recovered, still loses frequency (valuable)
    elif not stage1_pass:
        v = "HARD_FAIL_A_DECODE_FIX_INSUFFICIENT"   # confidence rerank did NOT clear single_shot
    elif not bind_loadbearing:
        v = "HARD_FAIL_BIND_NOT_LOADBEARING"
    elif not broken_fails:
        v = "HARD_FAIL_BROKEN_VERIFIER_INFERS"
    else:
        v = "MIDDLE_BAND"

    msg = ("RES_CONF h@1=%.3f mrr=%.3f h@10=%.3f | gated_recall@%d=%.3f raw=%.3f (single_shot=%.3f "
           "sym=%.3f gap_closed=%.2f) | POP_RF h@1=%.3f mrr=%.3f | SYM h@1=%.3f mrr=%.3f | "
           "ABLATED mrr=%.3f (ratio=%.2f) | BROKEN mrr=%.3f | ceiling=%.3f || "
           "STAGE1=%s STAGE2=%s bind_lb=%s broken_fails=%s"
           % (res1, resmrr, res10, RECALL_C, res_gated, res_raw, ss_recall, sym_recall, gap_closed_frac,
              pf1, pfmrr, sym1, symmrr, abl_mrr, abl_mrr / max(resmrr, 1e-9), bmrr, ceil,
              stage1_pass, stage2_pass, bind_loadbearing, broken_fails))
    gates = {
        "RESONATOR_CONF_hits1": res1, "RESONATOR_CONF_mrr": resmrr, "RESONATOR_CONF_hits10": res10,
        "SINGLE_SHOT_hits1": ss1, "SINGLE_SHOT_mrr": ssmrr,
        "SYMBOLIC_hits1": sym1, "SYMBOLIC_mrr": symmrr,
        "POP_RELFREQ_hits1": pf1, "POP_RELFREQ_mrr": pfmrr,
        "res_conf_gated_recall@C": res_gated, "res_conf_raw_recall@C": res_raw,
        "single_shot_recall@C": ss_recall, "sym_recall@C": sym_recall, "gap_closed_frac": gap_closed_frac,
        "ABLATED_mrr": abl_mrr, "ablated_ratio": abl_mrr / max(resmrr, 1e-9),
        "BROKEN_mrr": bmrr, "ceiling": ceil,
        "stage1_pass": stage1_pass, "stage2_pass": stage2_pass,
        "bind_loadbearing": bind_loadbearing, "broken_fails": broken_fails,
        "pop_relfreq_at_ceiling_frac": pfmrr / max(ceil, 1e-9),
    }
    return v, msg, gates


# ============================ self-test (rerank + gate discriminator) ============================
def _topk_ids(scores, k):
    return set(sorted(scores.keys(), key=lambda c: -scores[c])[:k])


def _selftest():
    print("[selftest] device=%s cuda_avail=%s GATE_K=%.2f" % (DEVICE, CUDA_AVAIL, GATE_K), flush=True)
    Nt = 256
    E = crux.make_entity_vectors(120, Nt, 0)
    # bundle: 3 golds with a WEAK/LATE one (0.22) buried below 4 distractors; single-shot top-10 must
    # miss the weak gold, confidence-rerank must rank ALL 3 golds into top-10 AND pass the gate.
    golds = [5, 41, 88]; gweights = [1.0, 0.55, 0.22]
    distr = [12, 33, 60, 99]; dweights = [0.80, 0.74, 0.70, 0.66]
    q = torch.zeros(Nt, dtype=torch.complex64, device=DEVICE)
    for i, w in zip(golds + distr, gweights + dweights):
        q = q + w * E[i]
    cand_ids = list(range(120))
    ss = crux.single_shot_scores(q, E, cand_ids, Nt)
    ss_top10 = _topk_ids(ss, 10)
    assert not set(golds).issubset(ss_top10) or (88 not in ss_top10), \
        "selftest PRECONDITION: single-shot already surfaces weak gold; no burial to fix"
    gen = torch.Generator().manual_seed(1)
    raw, gtd, tel = resonator_recover_conf(q, E, cand_ids, Nt, 100, 6, TAU, GATE_K, gen)
    # FIX-1: confidence rerank puts all 3 golds in top-10 (raw, ungated)
    raw_top10 = _topk_ids(raw, 10)
    n_raw_g = len(set(golds) & raw_top10)
    assert n_raw_g == 3, "selftest FIX-1 FAIL: confidence rerank top-10 has %d/3 golds (%s)" % (n_raw_g, sorted(raw_top10))
    # FIX-2a: gate PASSES the genuine golds (they are real signal above residual noise)
    n_gated_g = len(set(golds) & set(gtd.keys()))
    assert n_gated_g == 3, "selftest FIX-2a FAIL: gate rejected genuine golds (%d/3 passed)" % n_gated_g
    # FIX-2b: gate REJECTS spurious recoveries on a PURE-NOISE query (no stored bundle)
    gen2 = torch.Generator().manual_seed(2)
    phn = (torch.rand(Nt, generator=gen2) * 2.0 * math.pi)
    qn = torch.polar(torch.ones(Nt), phn).to(torch.complex64).to(DEVICE)
    _rn, gtn, _tn = resonator_recover_conf(qn, E, cand_ids, Nt, 100, 6, TAU, GATE_K, gen2)
    assert len(gtn) <= 3, "selftest FIX-2b FAIL: gate accepted %d spurious recoveries on pure noise" % len(gtn)
    # FIX-3: budget -- with only t_iter=5 the weak late gold is NOT surfaced (justifies t_iter>=80)
    gen3 = torch.Generator().manual_seed(3)
    raw5, _g5, _t5 = resonator_recover_conf(q, E, cand_ids, Nt, 5, 6, TAU, GATE_K, gen3)
    n_raw5 = len(set(golds) & _topk_ids(raw5, 10))
    print("[selftest] PASS: FIX1 rerank golds_top10=%d/3 | FIX2a gated_golds=%d/3 noise_gated=%d "
          "| FIX3 t_iter5 golds=%d/3 vs t_iter100 golds=3/3 | gate_k=%.2f"
          % (n_raw_g, n_gated_g, len(gtn), n_raw5, GATE_K), flush=True)


# ============================ start-marker / crash ============================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


def _arms_must_differ(arms_outputs):
    import hashlib
    digests = {n: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
               for n, o in arms_outputs.items()}
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], \
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (names[i], names[j])
    return digests


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, len(SEEDS))
    t0 = time.time()
    print("[config] anchor=%s mode=%s seeds=%s N_DIM=%d N_EVAL=%d TOP_K_RELS=%d T_ITER=%d N_RESTART=%d "
          "GATE_K=%.2f device=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_EVAL, TOP_K_RELS, T_ITER,
                                      N_RESTART, GATE_K, DEVICE), flush=True)

    train, valid, test = crux._load_fb15k237()
    ent2i, rel2i = crux.build_ids(train, valid, test)
    print("[data] train=%d valid=%d test=%d ent=%d rel=%d" % (len(train), len(valid), len(test),
                                                              len(ent2i), len(rel2i)), flush=True)

    per_seed = []
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")
    for si, seed in enumerate(SEEDS):
        ts = time.time()
        r = run_seed(train, valid, test, ent2i, rel2i, seed)
        per_seed.append(r)
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit_idx": si, "total_units": len(SEEDS),
                                "elapsed_s": time.time() - t0}) + "\n")
        print("[seed %d] RES_CONF h@1=%.3f mrr=%.3f | POP_RF h@1=%.3f mrr=%.3f | SYM mrr=%.3f | "
              "ABL mrr=%.3f | BROKEN mrr=%.3f | ceil=%.3f | gated_recall@%d=%.3f raw=%.3f "
              "(single_shot=%.3f sym=%.3f) (%.1fs)"
              % (seed, r["RESONATOR_CONF_GT"]["hits@1"], r["RESONATOR_CONF_GT"]["mrr"],
                 r["POP_RELFREQ"]["hits@1"], r["POP_RELFREQ"]["mrr"], r["SYMBOLIC_GT"]["mrr"],
                 r["BIND_ABLATED"]["mrr"], r["BROKEN_VERIFIER"]["mrr"], r["ceiling"], RECALL_C,
                 r["res_conf_gated_recall@%d" % RECALL_C], r["res_conf_raw_recall@%d" % RECALL_C],
                 r["single_shot_recall@%d" % RECALL_C], r["sym_recall@%d" % RECALL_C],
                 time.time() - ts), flush=True)

    s0 = per_seed[0]
    _arms_must_differ({a: s0[a] for a in
                       ["RESONATOR_CONF_GT", "SINGLE_SHOT", "BIND_ABLATED", "SYMBOLIC_GT",
                        "POP_RELFREQ", "POP_DEGREE", "BROKEN_VERIFIER"]})

    verdict, vmsg, gates = compute_verdict(per_seed)
    elapsed = time.time() - t0
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
               "summary": vmsg[:200], "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
               "device": str(DEVICE), "cuda_avail": CUDA_AVAIL, "arms_differ_verified": True,
               "elapsed_s": elapsed, "gates": gates, "per_seed": per_seed}
    write_metrics(out_dir, metrics, per_seed)
    print("[verdict] %s :: %s" % (verdict, vmsg), flush=True)
    print("[metrics] written to %s (%.1fs)" % (out_dir, elapsed), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir_for_crash, e)
        raise
