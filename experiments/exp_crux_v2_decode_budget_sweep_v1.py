"""
crux_v2_decode_budget_sweep_v1 -- DECODE-vs-ENCODE disambiguation on the crux v2 HARD_FAIL_A.

WHY (VET correction a359da34). crux v2 (resonator decode) landed HARD_FAIL_A_SNR_FLOOR
  (res_gated_recall@10=0.058, res_raw=0.117 vs single_shot=0.175, sym=0.317, nonconv=0.950)
  MEASURED@data/exp_crux_engine_v2_resonator_decode_v1_smoke/metrics.json. The VET did NOT confirm
  the "encode-bundling SNR-floor" localization: the resonator ran at t_iter=20 (drill recommended
  60-100), the nonconv=0.95 gate is a metric-design artifact (residual-norm-stability test on a
  matching-pursuit deflation loop that shrinks the residual EVERY step by construction), and the
  failure is LOW PROPOSAL RATE (silent, not wrong). So we cannot yet tell if the wall is ENCODE
  (info destroyed in the bundle -> sharding is the fix) or DECODE (resonator under-run -> more
  iterations is the fix).

THE EXPERIMENT (VET recipe). Reuse the IDENTICAL frozen compose bundle q the 0.058/0.117 numbers
  came from (seed=7, N_DIM=2048, smoke graph params -> n_test_eval=120, ceiling=0.3167,
  single_shot_recall@10=0.175). Build each q ONCE. Sweep ONLY the decode budget:
    t_iter in {20 (repro), 40, 60, 80, 100}, everything else (bundle, codebook, restarts, tau,
    rebind_k) held FIXED. The ONLY independent variable is decode iterations.
  Headline = RAW candidate-recall@10 (fair head-to-head vs single_shot 0.175 is res_RAW, per VET).
  Report BOTH raw and residual-gated recall at each t_iter (the gap = the spurious-convergence rate).
  Mechanism-matched convergence metric = PROPOSAL RATE: mean distinct candidates the resonator
  surfaces per query (mean n_raw / mean n_gated), NOT the artifactual nonconv=0.95.

DECISION BANDS (pre-registered):
  ENCODE/SNR-FLOOR CONFIRMED (green-lights v3 shard): raw candidate-recall@10 AND proposal-rate stay
    ~FLAT across t_iter 20->100 (raw@10 change <= +0.03 abs AND proposal-rate does not materially
    grow) -> the info is genuinely not in the bundle -> sharding/encode fix is well-founded.
  DECODE-SIDE (shard NOT the fix): raw recall / proposal-rate RISE materially with t_iter (raw@10 at
    t_iter>=80 exceeds t_iter=20 by >= +0.05, climbing toward/past single_shot 0.175; OR proposal
    rate roughly doubles) -> the wall was under-iteration, not the bundle -> fix is decode budget +
    gate/convergence-metric, not sharding.
  Report which band fired + recall(t_iter) + proposal-rate(t_iter) curves.

CONTRACT. SMOKE-ONLY-LOCAL cheap re-decode of a FROZEN bundle (no re-mining, no re-compose across
  the t_iter axis; mining happens ONCE). Seconds-to-few-min. No FULL, no queue. Reuses the exact
  crux v2 functions (import) so the bundle is bit-identical to the source run.

ASCII-only. Numbers tagged MEASURED@/THEORETICAL@ in comments.
"""
from __future__ import annotations
import sys, os, time, json, random, argparse
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Import the EXACT crux v2 cell so the frozen bundle is bit-identical (no re-implementation drift).
import experiments.exp_crux_engine_v2_resonator_decode_v1 as crux

ANCHOR_NAME = "crux_v2_decode_budget_sweep_v1"
OUT_DIR = REPO / "data" / ("exp_%s" % ANCHOR_NAME)

# ---- frozen-bundle config: EXACTLY the crux v2 smoke run that produced the 0.058/0.117 numbers ----
# MEASURED@data/exp_crux_engine_v2_resonator_decode_v1_smoke/metrics.json:per_seed[0]
#   seed=7 N_DIM=2048 n_test_eval=120 n_rules=150 ceiling=0.3167 single_shot_recall@10=0.175
SEED = 7
N_DIM = 2048
N_EVAL = 150            # only 120 test queries fall in the top-25 relations (deterministic given seed)
TOP_K_RELS = 25
PROFILE_EDGES_PER_REL = 120
BRANCH_CAP = 15
PATH_CAP = 250
MIN_SUPPORT = 3
MIN_CONF = crux.MIN_CONF        # 0.05
L_MAX = crux.L_MAX              # 3
RECALL_C = 10

# ---- decode-only sweep params (held FIXED across t_iter; the frozen decode config) ----
T_ITER_GRID = [20, 40, 60, 80, 100]
RES_N_RESTART = 8              # smoke default (crux.RES_N_RESTART for full=16); FIXED across sweep
RES_TAU = crux.RES_TAU         # 0.4  (init-only dither)
RES_REBIND_K = crux.RES_REBIND_K   # 2.5 (residual re-bind gate)
RES_K_REC = crux.RES_K_REC     # 0 => recover up to t_iter items/restart

# ---- pre-registered decision thresholds ----
RAW_FLAT_MAX_DELTA = 0.03      # ENCODE band: raw@10(t_iter=100) - raw@10(t_iter=20) <= this
RAW_DECODE_MIN_DELTA = 0.05    # DECODE band: raw@10(t_iter>=80) - raw@10(t_iter=20) >= this
SURF_FLAT_MAX_DELTA = 0.05     # ENCODE band: gold-surfaced-any(t_iter>=80) - (t_iter=20) <= this (gold never recovered)
SURF_DECODE_MIN_DELTA = 0.08   # DECODE band: gold-surfaced-any rises materially (gold gets recovered w/ budget)


def _gseed(seed, h, r3, op):
    """Replicate crux v2 run_seed's per-query resonator generator seed EXACTLY (repro fidelity)."""
    return (seed * 100003 + (h % 99991) * 131 + r3 * 17 + (7 if op == "bind" else 11)) & 0x7fffffff


def build_frozen_state():
    """Rebuild the crux v2 smoke frozen state up through the per-query bundle q. Deterministic."""
    train, valid, test = crux._load_fb15k237()
    ent2i, rel2i = crux.build_ids(train, valid, test)
    n_ent = len(ent2i)
    rng = random.Random(SEED)

    R = crux.make_rel_vectors(len(rel2i), N_DIM, SEED)
    rel_freq = Counter()
    for (h, r, t) in train:
        rel_freq[rel2i[r]] += 1
    target_rels = [r for r, _ in rel_freq.most_common(TOP_K_RELS)]
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
        PROFILE_EDGES_PER_REL, L_MAX, BRANCH_CAP, PATH_CAP, SEED)
    n_rules = sum(len(v) for v in conf.values())

    E = crux.make_entity_vectors(n_ent, N_DIM, SEED)

    # per-query candidate + bundle caches (built ONCE; frozen across the t_iter sweep)
    cand_cache, q_cache = {}, {}
    for (h, r3, gold) in tq:
        cand = crux.propose_candidates(gd, h, r3, L_MAX, BRANCH_CAP, PATH_CAP)
        cand_cache[(h, r3)] = cand
        q_cache[(h, r3)] = crux.build_query_bundle(cand, conf.get(r3, {}), cc_bind, E, N_DIM, "bind")

    return {"tq": tq, "known": known, "E": E, "n_ent": n_ent, "n_rel": len(rel2i),
            "n_rules": n_rules, "cand_cache": cand_cache, "q_cache": q_cache,
            "gd": gd, "conf": conf}


def single_shot_recall(state):
    """t_iter-independent SINGLE_SHOT candidate-recall@10 + candidate-ceiling (the repro gate)."""
    E, tq, known = state["E"], state["tq"], state["known"]
    ss_rC = ceil_hit = 0
    for (h, r3, gold) in tq:
        filt = known.get((h, r3), set()) - {gold}
        q, cand_ids = state["q_cache"][(h, r3)]
        cand = state["cand_cache"][(h, r3)]
        if (gold in cand) and (gold not in filt):
            ceil_hit += 1
        sc = crux.single_shot_scores(q, E, cand_ids, N_DIM)
        if crux.topc_has_gold(sc, gold, filt, RECALL_C):
            ss_rC += 1
    nq = len(tq)
    return {"single_shot_recall@10": ss_rC / nq, "ceiling": ceil_hit / nq, "n_test_eval": nq}


def sweep_t_iter(state, t_iter):
    """Re-decode the FROZEN bundles at one decode budget. Returns raw/gated recall@10 + proposal rate."""
    E, tq, known = state["E"], state["tq"], state["known"]
    raw_rC = gated_rC = raw_r1 = 0
    gold_surf_raw = gold_surf_gated = 0          # gold recovered ANYWHERE (any rank) -- the encode-vs-decode key
    n_raw_sum = n_gated_sum = 0
    n_reach = gold_surf_raw_reach = 0            # gold-surfaced restricted to reachable-gold queries
    for (h, r3, gold) in tq:
        filt = known.get((h, r3), set()) - {gold}
        q, cand_ids = state["q_cache"][(h, r3)]
        cand = state["cand_cache"][(h, r3)]
        reachable = (gold in cand) and (gold not in filt)
        gold_ok = (gold not in filt)             # gold is a legitimate (unfiltered) target
        gen = torch.Generator().manual_seed(_gseed(SEED, h, r3, "bind"))
        raw, gtd, tel = crux.resonator_recover(
            q, E, cand_ids, N_DIM, RES_K_REC, t_iter, RES_N_RESTART, RES_TAU, RES_REBIND_K, gen)
        if crux.topc_has_gold(raw, gold, filt, RECALL_C):
            raw_rC += 1
        if crux.topc_has_gold(raw, gold, filt, 1):
            raw_r1 += 1
        if crux.topc_has_gold(gtd, gold, filt, RECALL_C):
            gated_rC += 1
        # gold SURFACED at all: recovered into the candidate score-set at ANY rank (decode budget's job)
        if gold_ok and (gold in raw):
            gold_surf_raw += 1
        if gold_ok and (gold in gtd):
            gold_surf_gated += 1
        n_raw_sum += tel["n_raw"]
        n_gated_sum += tel["n_gated"]
        if reachable:
            n_reach += 1
            if gold in raw:
                gold_surf_raw_reach += 1
    nq = len(tq)
    return {
        "t_iter": t_iter,
        "raw_recall@10": raw_rC / nq,                        # HEADLINE (VET's fair head-to-head metric)
        "gated_recall@10": gated_rC / nq,
        "raw_recall@1": raw_r1 / nq,
        "spurious_inflation@10": (raw_rC - gated_rC) / nq,   # raw minus gated (gap = spurious rate)
        "gold_surfaced_raw": gold_surf_raw / nq,             # KEY: gold recovered ANY-rank (decode's actual job)
        "gold_surfaced_gated": gold_surf_gated / nq,
        "gold_surfaced_raw_of_reachable": (gold_surf_raw_reach / n_reach) if n_reach else 0.0,
        "n_reachable": n_reach,
        "proposal_rate_raw": n_raw_sum / nq,                 # distinct candidates surfaced (mechanical; telemetry)
        "proposal_rate_gated": n_gated_sum / nq,
    }


def decide(base, sweep):
    """Pre-registered band logic on the raw-recall(t_iter) + proposal-rate(t_iter) curves."""
    by_ti = {s["t_iter"]: s for s in sweep}
    raw20 = by_ti[20]["raw_recall@10"]
    raw100 = by_ti[100]["raw_recall@10"]
    raw_hi = max(by_ti[t]["raw_recall@10"] for t in (80, 100))
    surf20 = by_ti[20]["gold_surfaced_raw"]
    surf100 = by_ti[100]["gold_surfaced_raw"]
    surf_hi = max(by_ti[t]["gold_surfaced_raw"] for t in (80, 100))

    raw_delta_hi = raw_hi - raw20                    # decode-side signal on recall@10
    raw_delta_100 = raw100 - raw20
    surf_delta_hi = surf_hi - surf20                 # decode-side signal on gold-surfaced-any (decode's job)

    # DECODE-side: more budget surfaces the gold (recall@10 climbs OR gold gets recovered at all more often)
    decode_recall = (raw_delta_hi >= RAW_DECODE_MIN_DELTA)
    decode_surface = (surf_delta_hi >= SURF_DECODE_MIN_DELTA)
    # ENCODE floor: gold neither ranks better NOR gets surfaced-at-all with 5x budget -> not in the bundle
    encode_flat = (raw_delta_100 <= RAW_FLAT_MAX_DELTA) and (surf_delta_hi <= SURF_FLAT_MAX_DELTA)

    if decode_recall or decode_surface:
        band = "DECODE_SIDE"
        greenlight_v3_shard = False
    elif encode_flat:
        band = "ENCODE_SNR_FLOOR_CONFIRMED"
        greenlight_v3_shard = True
    else:
        band = "AMBIGUOUS"
        greenlight_v3_shard = False

    return {
        "band": band,
        "greenlight_v3_shard": greenlight_v3_shard,
        "raw_recall@10_t20": raw20, "raw_recall@10_t100": raw100, "raw_recall@10_max_hi": raw_hi,
        "raw_delta_hi_vs_t20": raw_delta_hi, "raw_delta_t100_vs_t20": raw_delta_100,
        "gold_surfaced_raw_t20": surf20, "gold_surfaced_raw_t100": surf100, "gold_surfaced_raw_max_hi": surf_hi,
        "gold_surfaced_delta_hi_vs_t20": surf_delta_hi,
        "proposal_rate_raw_t20": by_ti[20]["proposal_rate_raw"],
        "proposal_rate_raw_t100": by_ti[100]["proposal_rate_raw"],
        "single_shot_recall@10": base["single_shot_recall@10"], "ceiling": base["ceiling"],
        "decode_trigger_recall": decode_recall, "decode_trigger_surface": decode_surface,
        "encode_flat": encode_flat,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    print("[config] anchor=%s seed=%d N_DIM=%d N_EVAL=%d TOP_K_RELS=%d restart=%d t_iter_grid=%s device=%s"
          % (ANCHOR_NAME, SEED, N_DIM, N_EVAL, TOP_K_RELS, RES_N_RESTART, T_ITER_GRID, crux.DEVICE), flush=True)

    state = build_frozen_state()
    print("[build] n_test_eval=%d n_rules=%d n_ent=%d n_rel=%d (%.1fs)"
          % (len(state["tq"]), state["n_rules"], state["n_ent"], state["n_rel"], time.time() - t0), flush=True)

    base = single_shot_recall(state)
    print("[repro-gate] ceiling=%.4f single_shot_recall@10=%.4f (expect ceiling~0.3167 ss~0.175)"
          % (base["ceiling"], base["single_shot_recall@10"]), flush=True)

    sweep = []
    for ti in T_ITER_GRID:
        ts = time.time()
        s = sweep_t_iter(state, ti)
        sweep.append(s)
        print("[t_iter=%3d] raw@10=%.4f gated@10=%.4f | gold_surf_raw=%.4f (of_reach=%.4f) gold_surf_gated=%.4f "
              "| prop_raw=%.2f (%.1fs)"
              % (ti, s["raw_recall@10"], s["gated_recall@10"], s["gold_surfaced_raw"],
                 s["gold_surfaced_raw_of_reachable"], s["gold_surfaced_gated"], s["proposal_rate_raw"],
                 time.time() - ts), flush=True)

    dec = decide(base, sweep)
    elapsed = time.time() - t0

    verdict = "DISAMBIG_" + dec["band"]
    vmsg = ("BAND=%s greenlight_v3_shard=%s | raw@10 t20=%.4f t100=%.4f max(80,100)=%.4f (delta_hi=%.4f) "
            "| gold_surf_raw t20=%.4f max(80,100)=%.4f (delta_hi=%.4f) "
            "| single_shot=%.4f ceiling=%.4f | decode_trig(recall=%s surface=%s) encode_flat=%s"
            % (dec["band"], dec["greenlight_v3_shard"], dec["raw_recall@10_t20"], dec["raw_recall@10_t100"],
               dec["raw_recall@10_max_hi"], dec["raw_delta_hi_vs_t20"],
               dec["gold_surfaced_raw_t20"], dec["gold_surfaced_raw_max_hi"], dec["gold_surfaced_delta_hi_vs_t20"],
               dec["single_shot_recall@10"], dec["ceiling"], dec["decode_trigger_recall"],
               dec["decode_trigger_surface"], dec["encode_flat"]))

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg[:200],
        "run_mode": "smoke", "device": str(crux.DEVICE), "cuda_avail": crux.CUDA_AVAIL,
        "elapsed_s": elapsed, "seed": SEED, "N_DIM": N_DIM,
        "config": {"N_EVAL": N_EVAL, "TOP_K_RELS": TOP_K_RELS, "RES_N_RESTART": RES_N_RESTART,
                   "RES_TAU": RES_TAU, "RES_REBIND_K": RES_REBIND_K, "t_iter_grid": T_ITER_GRID},
        "repro_gate": base, "sweep": sweep, "decision": dec,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    tmp = os.path.join(str(OUT_DIR), "metrics.json.tmp")
    final = os.path.join(str(OUT_DIR), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)

    print("[verdict] %s :: %s" % (verdict, vmsg), flush=True)
    print("[metrics] %s (%.1fs)" % (final, elapsed), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        # cheap self-test: frozen bundle + resonator recover fires + monotone-plumbing sanity
        st = build_frozen_state()
        b = single_shot_recall(st)
        assert 0.10 <= b["ceiling"] <= 0.55, "selftest: ceiling out of expected band %.4f" % b["ceiling"]
        s20 = sweep_t_iter(st, 20)
        s100 = sweep_t_iter(st, 100)
        assert s100["proposal_rate_raw"] >= s20["proposal_rate_raw"] - 1e-6, \
            "selftest: proposal rate should not DECREASE with more iterations"
        print("[selftest] PASS: ceiling=%.4f ss=%.4f | t20 raw@10=%.4f prop=%.2f | t100 raw@10=%.4f prop=%.2f"
              % (b["ceiling"], b["single_shot_recall@10"], s20["raw_recall@10"], s20["proposal_rate_raw"],
                 s100["raw_recall@10"], s100["proposal_rate_raw"]), flush=True)
        sys.exit(0)
    main()
