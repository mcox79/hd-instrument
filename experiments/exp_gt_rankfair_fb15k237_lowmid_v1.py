"""
gt_rankfair_fb15k237_lowmid_v1 -- REFRAMED (fair-stratum) test of the Step-1 symbolic
generate-and-test engine: does a BETTER SYMBOLIC RANKER of already-reached candidates beat
the frequency baseline ON THE LOW+MID DEGREE STRATUM of FB15k-237?

WHY THIS REFRAME (fairness VET aa7f151f). The aggregate "beat frequency" bar was UNFAIR:
high-degree hubs are frequency-guessable (POP hits@10=0.964 on the high-degree-tail stratum,
which EXCEEDS the symbolic reach-ceiling 0.647 there) and they drowned the real signal in the
aggregate (aggregate POP h@10=0.495 vs SYM 0.281). The FAIR, winnable target is the LOW+MID
degree stratum (gold-tail global degree <= q2~279, the bottom 2/3), where the reach-ceiling
(0.345 low / 0.528 mid) is FAR ABOVE the frequency baseline (POP h@10 0.107 low / 0.421 mid) --
24-30 pts of REAL headroom. The Step-1 engine already REACHES the gold there (reach 0.345 low)
but RANKS it poorly (only 0.097 into top-10) -- so the bottleneck is a RANK-ceiling, not a
recall/SNR/capacity-ceiling. This cell tests whether ANY FAIR better ranker closes that gap.
(VET explicit sequencing: prove the win CHEAPLY + SYMBOLICALLY first; NO HD/VSA/GPU this cell.
If symbolic cannot win on the fair stratum, substrate-native cannot either -> save HD compute.)

Reference numbers reproduced off-disk (headroom_recompute.py, N_EVAL=3000, all rels, MIN_SUPPORT=10):
  low  n=1017 reach 0.345 POP h@10 0.107 mrr 0.053 | SYM h@10 0.097 mrr 0.058  MEASURED
  mid  n= 986 reach 0.528 POP h@10 0.421 mrr 0.242 | SYM h@10 0.275 mrr 0.173  MEASURED
  high n= 997 reach 0.647 POP h@10 0.964 mrr 0.748 | SYM h@10 0.475 mrr 0.390  MEASURED (unfair sat)
  tertile bounds gold-tail global degree: q1=47 q2=279  MEASURED
  low+mid combined: POP h@10 ~0.262 mrr ~0.146 | SYM_BASE h@10 ~0.185 mrr ~0.115 | reach ~0.435
  => SYM_BASE currently LOSES to frequency even on the fair stratum by ~0.077 h@10.
  Fair-lever ablation (seed 7, N_EVAL=800; scratchpad rank_ablation.py): NO fair ranker beat POP
  (0.259); all 7 fair variants landed 0.118-0.160 h@10, below both POP AND the noisy-OR base.  MEASURED

THE FAIR RANKER PANEL (existential test: does ANY fair ranker beat POP?). Same reached candidate
set as Step-1 (the generator is unchanged; NOTHING about recall/reach changes). Only the RANKING
function over the reached set changes. Every panel member is HEAD-CONDITIONAL and reads ONLY the
graph adjacency + head-local structure -- NONE references candidate global degree/frequency (that
would be POP in disguise -- MUST-FAIL control #3). The panel spans the 3 crux-v1 ranking levers
(head-conditional multiplicity, hop-normalized confidence, negative-evidence) in isolation and
combined:
  SYM_BASE       -- Step-1 `propose` noisy-OR over per-GROUNDING confidences (imported, EXACT
                    Step-1 code path; positive control AND a legitimate fair symbolic ranker --
                    grounding-count is head-conditional path structure, NOT global tail freq).
  add_g05_b0     -- ADDITIVE log-form over DISTINCT rules (dedupe groundings; rewards rule-level
                    corroboration not hub-grounding-count), L2 hop-weight GAMMA=0.5. (levers 1+2)
  add_g10_b0     -- same, no hop-normalization (GAMMA=1.0). (lever 1)
  max_conf       -- max single-rule hop-weighted confidence (no multiplicity). (confidence only)
  rule_count     -- number of distinct corroborating rules (pure multiplicity). (lever 1 raw)
  noisyOR_rule   -- noisy-OR at RULE level (dedupe groundings), hop 0.5. (levers 1+2, bounded)
  add_g05_b03    -- add_g05_b0 minus BETA=0.30 head-local negative-evidence (c relates to h under
                    a DIFFERENT relation -> down-weight). (levers 1+2+3)
  score(c) forms are head-conditional; grounding dedupe uses max weight per rule; additive log =
  -log(1-min(w,0.999)) summed over distinct reaching rules.
BEST_FAIR = per-seed-averaged MAX over {SYM_BASE + panel} on low+mid (gives reasoning its BEST
fair shot; panel is PRE-REGISTERED, reads no gold labels -> no post-hoc p-hacking).

CONTROLS:
  POP_RELFREQ -- frequency baseline (per-relation tail freq), ranked ON EACH STRATUM. Must be BEATEN on low+mid.
  SCRAMBLE    -- add_g05_b0 scores randomly PERMUTED across the reached set. MUST-FAIL control #1: proves the ranking signal (not mere membership in the reached set) is load-bearing; must NOT beat POP on low+mid.

FAIRNESS + LOCALIZATION APPARATUS (MANDATORY per USER standing directive):
  - Evaluate on low+mid stratum (deg <= q2); baseline = POP computed ON THAT STRATUM (not aggregate).
  - Info-ceiling known per stratum (reach); WIN bar (beat POP on stratum) <= ceiling -> FAIR/winnable by construction. Report achieved/ceiling.
  - Degree-STRATIFIED reporting: low / mid / low+mid / high (high shown only to exhibit the unfair saturation for contrast).
  - MUST-FAIL controls: (1) SCRAMBLE must NOT beat POP on low+mid; (2) win must be on the stratum's fair comparison, NOT the aggregate (verdict gates on low+mid only; aggregate reported for context); (3) NO freq/degree signal in the rankers -- proven OPERATIONALLY: add_g05_b0 ranks recomputed on a graph whose rel_tail_freq + node_degree are SCRAMBLED (adjacency intact) must be BIT-IDENTICAL (the ranker never reads those tables); every other panel ranker + SYM_BASE reads the same adjacency-only surface.

COMPUTE ARCHITECTURE. Sequential-CPU, SYMBOLIC ONLY. Pure relational hash-joins + dict lookups;
NO substrate vectors, NO bind/unbind, NO matmul, NO GPU (VET directive: prove the win cheaply +
symbolically first). Batching is N/A (combinatorial graph traversal, not matmul). Step-1 FULL ran
25.8s/3seeds; this cell adds a ranker panel of comparable cost -> ~60-90s FULL. No
sequential-dependency, no storage (no_storage / no_composition -- symbolic graph, not the HD substrate).

DECISION (pre-registered, low+mid stratum PRIMARY; META_RULE_L strict-above-floor):
  HARD_PASS = (BEST_FAIR h@10 - POP h@10 >= 0.02 on low+mid) OR (BEST_FAIR mrr - POP mrr >= 0.01 on low+mid)
              AND SCRAMBLE does NOT beat POP on low+mid (SCRAMBLE h@10 <= POP h@10 + 0.01)
              AND freq-leak audit PASSES (rank-identical under freq scramble)
              AND BEST_FAIR h@10 <= reach-ceiling on low+mid (fair-bounded sanity)
              AND arms differ.
  HARD_FAIL = (BEST_FAIR h@10 <= POP h@10 AND BEST_FAIR mrr <= POP mrr on low+mid)  [even the BEST fair ranker does NOT beat frequency on the fair stratum -> symbolic cannot win it -> SAVE HD compute; a clean, VALUABLE negative]
              OR SCRAMBLE beats POP on low+mid (ranking signal not load-bearing / leak)
              OR freq-leak audit FAILS
              OR arms identical.
  Anything between = MIDDLE_BAND.

SELF-TEST discriminators (must FIRE): (1) planted graph where a low-mult gold is reachable but
noisy-OR (grounding-inflated) buries it under a hub reached by many groundings, and the additive
rule-dedupe ranker promotes the gold above the hub -> add ranker hits@1 > SYM_BASE hits@1;
(2) SCRAMBLE of those scores destroys the promotion (random); (3) freq-leak audit: add ranker
scores identical when tail-freq/degree tables scrambled.

ASCII-only. write_metrics. RUN_MODE defaults to full (runner invokes with no argv).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (POP vs SYM_BASE vs panel vs SCRAMBLE rank vectors hashed)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-writer os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: symbolic rank test, no additive-noise floor; info-ceiling = per-stratum reach (reported)
# - baseline_in_band at smoke (POP low+mid in (0.05,0.95); high POP saturated >0.85 = contrast present)
# - discriminator survives scale: smoke uses FULL rule-mining params (MIN_SUPPORT=10, all rels); only N_EVAL reduced
# - HARD_PASS strictly above floor (+0.02 h@10 / +0.01 mrr margins; META_RULE_L)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (per-seed strat records); verdict counts per_seed
# - per-unit failure-class instrumentation (no bare except; except Exception only)
# - calibration_check: default_ok_for_this_regime (MIN_SUPPORT/MIN_CONF inherited from Step-1 hardened cell)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
from __future__ import annotations
import sys, os, argparse, time, json, math, random, traceback, platform, hashlib, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "gt_rankfair_fb15k237_lowmid_v1"

# ---- import the Step-1 engine (REUSE apparatus; SYM_BASE = EXACT Step-1 code path) ----
_STEP1 = REPO / "experiments" / "exp_gt_induction_fb15k237_dense_v1.py"
_spec = importlib.util.spec_from_file_location("gtstep1_engine", str(_STEP1))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)   # module-level guard: exec_module does NOT run __main__ block

# ---- run mode / config -------------------------------------------------------
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# rule-mining params inherited from Step-1 hardened cell (calibration_check: default_ok_for_this_regime)
MIN_SUPPORT = 10
MIN_CONF = 0.10
MAX_RULES_PER_HEAD = 50
HUB_CAP = 60000
BETA = 0.30     # head-conditional negative-evidence penalty in log-units (lever 3)

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_EVAL = 800
else:
    SEEDS = [7, 17, 23]
    N_EVAL = 3000

EXPECTED_N_UNITS = len(SEEDS)

# fair-ranker panel names (SYM_BASE handled separately as positive control + fair member)
PANEL = ["add_g05_b0", "add_g10_b0", "max_conf", "rule_count", "noisyOR_rule", "add_g05_b03"]
FAIR_SET = ["SYM_BASE"] + PANEL   # BEST_FAIR = max over these on low+mid
REP_RANKER = "add_g05_b0"         # representative for SCRAMBLE + freq-leak audit


# ============================ fair ranker panel ===============================
def rules_reaching(g, h, rules, gamma):
    """{cand: {rule_idx: hopw*conf}} deduped so each accepted rule contributes at most ONCE per
    candidate (grounding-count / hub-ness NOT rewarded; only rule-level corroboration).
    hopw = gamma for L2 (2-hop) else 1.0. Pure adjacency traversal -- reads NO freq/degree."""
    per_cand = defaultdict(dict)
    for ri, (kind, r1, r2, conf, supp) in enumerate(rules):
        w = (gamma if kind == "L2" else 1.0) * conf
        cands = set()
        if kind == "L2":
            for b in g.out_adj_rel.get(r1, {}).get(h, ()):
                for c in g.out_adj_rel.get(r2, {}).get(b, ()):
                    if c != h:
                        cands.add(c)
        elif kind == "L1F":
            for c in g.out_adj_rel.get(r1, {}).get(h, ()):
                if c != h:
                    cands.add(c)
        elif kind == "L1I":
            for c in g.in_adj_rel.get(r1, {}).get(h, ()):
                if c != h:
                    cands.add(c)
        for c in cands:
            if w > per_cand[c].get(ri, 0.0):
                per_cand[c][ri] = w
    return per_cand


def _other_tails(g, h, r3):
    return set(t for (r, t) in g.out_by_node.get(h, ()) if r != r3)


def rank_score(name, g, h, r3, rules):
    """Dispatch a fair panel ranker by name. Returns {cand: score}. Adjacency-only + head-local."""
    if name == "SYM_BASE":
        return E.propose(g, h, r3, rules)                 # Step-1 noisy-OR over groundings
    if name == "add_g05_b0":
        per = rules_reaching(g, h, rules, 0.5)
        return {c: sum(-math.log(1.0 - min(w, 0.999)) for w in d.values()) for c, d in per.items()}
    if name == "add_g10_b0":
        per = rules_reaching(g, h, rules, 1.0)
        return {c: sum(-math.log(1.0 - min(w, 0.999)) for w in d.values()) for c, d in per.items()}
    if name == "max_conf":
        per = rules_reaching(g, h, rules, 0.5)
        return {c: max(d.values()) for c, d in per.items()}
    if name == "rule_count":
        per = rules_reaching(g, h, rules, 0.5)
        return {c: float(len(d)) + 0.001 * max(d.values()) for c, d in per.items()}
    if name == "noisyOR_rule":
        per = rules_reaching(g, h, rules, 0.5)
        out = {}
        for c, d in per.items():
            p = 1.0
            for w in d.values():
                p *= (1.0 - min(w, 0.999))
            out[c] = 1.0 - p
        return out
    if name == "add_g05_b03":
        per = rules_reaching(g, h, rules, 0.5)
        ot = _other_tails(g, h, r3)
        out = {}
        for c, d in per.items():
            s = sum(-math.log(1.0 - min(w, 0.999)) for w in d.values())
            if c in ot:
                s -= BETA
            out[c] = s
        return out
    raise ValueError("unknown ranker %r" % name)


def scramble_scores(scores, rng):
    """Randomly permute scores across the SAME reached candidate set (control #1)."""
    keys = list(scores.keys())
    vals = [scores[k] for k in keys]
    rng.shuffle(vals)
    return {k: v for k, v in zip(keys, vals)}


# ============================ freq-leak audit graph ===========================
class FreqScrambledGraph:
    """Wraps a Graph but SCRAMBLES rel_tail_freq + node_degree (adjacency untouched). A ranker that
    reads adjacency only produces BIT-IDENTICAL ranks; a leak would change. Operational control #3."""
    def __init__(self, g, seed):
        self.out_adj_rel = g.out_adj_rel
        self.in_adj_rel = g.in_adj_rel
        self.out_by_node = g.out_by_node
        self.in_by_node = g.in_by_node
        self.edge_rels = g.edge_rels
        self.n_ent = g.n_ent
        self.n_rel = g.n_rel
        rng = random.Random(seed)
        dk = list(g.node_degree.keys()); dv = [g.node_degree[k] for k in dk]; rng.shuffle(dv)
        self.node_degree = Counter({k: v for k, v in zip(dk, dv)})
        self.rel_tail_freq = defaultdict(Counter)
        for r, cnt in g.rel_tail_freq.items():
            ks = list(cnt.keys()); vs = [cnt[k] for k in ks]; rng.shuffle(vs)
            self.rel_tail_freq[r] = Counter({k: v for k, v in zip(ks, vs)})


# ============================ per-seed evaluation =============================
def _tert(d, q1, q2):
    return "low" if d <= q1 else ("high" if d > q2 else "mid")


def run_seed(train, valid, test, ent2i, rel2i, seed):
    rng = random.Random(seed)
    n_ent = len(ent2i)
    target_rels = list(rel2i.values())
    target_set = set(target_rels)

    gd = E.Graph(train, ent2i, rel2i)
    known = defaultdict(set)
    for tr in (train, valid, test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])

    tq_all = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in test if rel2i[r] in target_set]
    rng.shuffle(tq_all)
    tq = tq_all[:N_EVAL]

    acc_d, allpat_d, hub_skipped = E.mine_rules(
        gd, target_rels, MIN_SUPPORT, MIN_CONF, MAX_RULES_PER_HEAD, HUB_CAP)
    n_rules_d = sum(len(v) for v in acc_d.values())

    degs = sorted(gd.node_degree.get(g, 0) for (_, _, g) in tq)
    q1 = degs[len(degs) // 3]; q2 = degs[2 * len(degs) // 3]

    fg = FreqScrambledGraph(gd, seed * 131 + 5)

    TIE_SEED = 20260710
    # per-stratum accumulators: strat[st] = {"n","reach", ranker: {"h10","rr"}, "POP":{}, "SCR":{}}
    def _mk():
        d = {"n": 0, "reach": 0, "POP": {"h10": 0, "rr": 0.0}, "SCR": {"h10": 0, "rr": 0.0}}
        for rn in FAIR_SET:
            d[rn] = {"h10": 0, "rr": 0.0}
        return d
    strat = {"low": _mk(), "mid": _mk(), "high": _mk()}

    # per-ranker independent tie RNGs (same seed+call-order across arms -> comparable ranks)
    rngs = {rn: random.Random(TIE_SEED) for rn in FAIR_SET}
    r_pop = random.Random(TIE_SEED)
    r_scr = random.Random(TIE_SEED)
    r_scrperm = random.Random(seed * 7919 + 13)
    r_leak = random.Random(TIE_SEED)

    # freq-leak audit sequences (REP_RANKER real vs freq-scrambled)
    leak_real, leak_scram = [], []
    n_leak_check = min(400, len(tq))

    # arms-differ hash vectors (first 500 queries)
    hash_n = min(500, len(tq))
    rvec = {rn: [] for rn in FAIR_SET}
    rvec["POP"] = []; rvec["SCR"] = []

    for qi, (h, r, gold) in enumerate(tq):
        filt = known.get((h, r), set()) - {gold}
        st = _tert(gd.node_degree.get(gold, 0), q1, q2)
        s = strat[st]; s["n"] += 1

        reach = E.reachable(gd, h, r, allpat_d.get(r, []))
        if (gold in reach) and (gold not in filt):
            s["reach"] += 1

        # POP baseline
        prank = E.pop_rank(gd.rel_tail_freq.get(r, Counter()), gold, filt, r_pop, n_ent)
        if prank is not None:
            if prank <= 10: s["POP"]["h10"] += 1
            s["POP"]["rr"] += 1.0 / prank
        if qi < hash_n: rvec["POP"].append(-1 if prank is None else prank)

        # each fair ranker
        rep_rank = None
        for rn in FAIR_SET:
            sc = rank_score(rn, gd, h, r, acc_d.get(r, []))
            rk = E.strict_rank(sc, gold, filt, rngs[rn])
            if rk is not None:
                if rk <= 10: s[rn]["h10"] += 1
                s[rn]["rr"] += 1.0 / rk
            if qi < hash_n: rvec[rn].append(-1 if rk is None else rk)
            if rn == REP_RANKER:
                rep_sc = sc; rep_rank = rk

        # SCRAMBLE (control #1) on REP_RANKER scores
        scr_sc = scramble_scores(rep_sc, r_scrperm)
        srank = E.strict_rank(scr_sc, gold, filt, r_scr)
        if srank is not None:
            if srank <= 10: s["SCR"]["h10"] += 1
            s["SCR"]["rr"] += 1.0 / srank
        if qi < hash_n: rvec["SCR"].append(-1 if srank is None else srank)

        # freq-leak audit on REP_RANKER (first n_leak_check queries)
        if qi < n_leak_check:
            leak_real.append(-1 if rep_rank is None else rep_rank)
            rep_sc_f = rank_score(REP_RANKER, fg, h, r, acc_d.get(r, []))
            frank = E.strict_rank(rep_sc_f, gold, filt, r_leak)
            leak_scram.append(-1 if frank is None else frank)

    freq_leak_ok = (leak_real == leak_scram)

    def _h(v):
        return hashlib.sha256(json.dumps(v).encode()).hexdigest()[:16]
    arm_hashes = {k: _h(rvec[k]) for k in rvec}
    # arms differ: POP, SCR, SYM_BASE, and at least one panel additive ranker must be distinct
    key_arms = ["POP", "SCR", "SYM_BASE", "add_g05_b0"]
    arms_differ = len(set(arm_hashes[k] for k in key_arms)) == len(key_arms)

    # finalize per-stratum rates
    def _rates(s):
        n = max(s["n"], 1)
        out = {"n": s["n"], "reach": s["reach"] / n,
               "POP_h10": s["POP"]["h10"] / n, "POP_mrr": s["POP"]["rr"] / n,
               "SCR_h10": s["SCR"]["h10"] / n, "SCR_mrr": s["SCR"]["rr"] / n}
        for rn in FAIR_SET:
            out[rn + "_h10"] = s[rn]["h10"] / n
            out[rn + "_mrr"] = s[rn]["rr"] / n
        return out
    out = {st: _rates(strat[st]) for st in ["low", "mid", "high"]}

    # low+mid combined (FAIR primary stratum) from raw counts
    a, b = strat["low"], strat["mid"]
    n_lm = max(a["n"] + b["n"], 1)
    lm = {"n": a["n"] + b["n"], "reach": (a["reach"] + b["reach"]) / n_lm,
          "POP_h10": (a["POP"]["h10"] + b["POP"]["h10"]) / n_lm,
          "POP_mrr": (a["POP"]["rr"] + b["POP"]["rr"]) / n_lm,
          "SCR_h10": (a["SCR"]["h10"] + b["SCR"]["h10"]) / n_lm,
          "SCR_mrr": (a["SCR"]["rr"] + b["SCR"]["rr"]) / n_lm}
    for rn in FAIR_SET:
        lm[rn + "_h10"] = (a[rn]["h10"] + b[rn]["h10"]) / n_lm
        lm[rn + "_mrr"] = (a[rn]["rr"] + b[rn]["rr"]) / n_lm
    out["low_mid"] = lm

    # aggregate (context only; NOT gated)
    tot_n = a["n"] + b["n"] + strat["high"]["n"]
    n_all = max(tot_n, 1)
    agg = {"n": tot_n,
           "POP_h10": sum(strat[x]["POP"]["h10"] for x in ["low", "mid", "high"]) / n_all}
    for rn in FAIR_SET:
        agg[rn + "_h10"] = sum(strat[x][rn]["h10"] for x in ["low", "mid", "high"]) / n_all
    out["aggregate"] = agg

    out["meta"] = {"seed": seed, "q1": q1, "q2": q2, "n_ent": n_ent, "n_rel": len(rel2i),
                   "n_rules_dense": n_rules_d, "hub_skipped": hub_skipped,
                   "n_test_eval": len(tq), "avgdeg_dense": 2.0 * len(train) / n_ent,
                   "freq_leak_ok": freq_leak_ok, "arms_differ": arms_differ,
                   "arm_hashes": arm_hashes, "n_leak_check": n_leak_check}
    return out


# ============================ verdict =========================================
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_verdict(per_seed):
    def lm(k):
        return _mean([s["low_mid"][k] for s in per_seed])
    pop10 = lm("POP_h10"); popmrr = lm("POP_mrr")
    scr10 = lm("SCR_h10")
    reach_lm = lm("reach")

    # per-ranker averaged low+mid h@10 / mrr; BEST_FAIR = max over FAIR_SET
    fair_h10 = {rn: lm(rn + "_h10") for rn in FAIR_SET}
    fair_mrr = {rn: lm(rn + "_mrr") for rn in FAIR_SET}
    best_h10_name = max(fair_h10, key=fair_h10.get)
    best_mrr_name = max(fair_mrr, key=fair_mrr.get)
    best_h10 = fair_h10[best_h10_name]
    best_mrr = fair_mrr[best_mrr_name]

    freq_leak_ok = all(s["meta"]["freq_leak_ok"] for s in per_seed)
    arms_differ = all(s["meta"]["arms_differ"] for s in per_seed)

    best_beats_pop = (best_h10 - pop10 >= 0.02) or (best_mrr - popmrr >= 0.01)
    scramble_fails = (scr10 <= pop10 + 0.01)
    fair_bounded = (best_h10 <= reach_lm + 1e-9)

    hard_pass = best_beats_pop and scramble_fails and freq_leak_ok and fair_bounded and arms_differ
    ranker_loses = (best_h10 <= pop10) and (best_mrr <= popmrr)
    hard_fail = ranker_loses or (not scramble_fails) or (not freq_leak_ok) or (not arms_differ)

    if hard_pass:
        v = "HARD_PASS"
    elif hard_fail:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"

    hi_pop10 = _mean([s["high"]["POP_h10"] for s in per_seed])
    hi_reach = _mean([s["high"]["reach"] for s in per_seed])
    agg_pop10 = _mean([s["aggregate"]["POP_h10"] for s in per_seed])
    agg_best = _mean([s["aggregate"][best_h10_name + "_h10"] for s in per_seed])

    msg = ("[low+mid FAIR] POP h@10=%.3f mrr=%.3f | BEST_FAIR h@10=%.3f (%s) mrr=%.3f (%s) | "
           "SCRAMBLE h@10=%.3f | reach=%.3f ach/ceil=%.3f || "
           "best_beats_pop=%s scramble_fails=%s freq_leak_ok=%s fair_bounded=%s arms_differ=%s || "
           "[CONTRAST high] POP h@10=%.3f (reach %.3f; freq-guessable/unfair) | "
           "[aggregate] POP h@10=%.3f BEST h@10=%.3f"
           % (pop10, popmrr, best_h10, best_h10_name, best_mrr, best_mrr_name, scr10, reach_lm,
              (best_h10 / reach_lm if reach_lm > 0 else 0.0),
              best_beats_pop, scramble_fails, freq_leak_ok, fair_bounded, arms_differ,
              hi_pop10, hi_reach, agg_pop10, agg_best))
    gates = {
        "lm_POP_h10": pop10, "lm_POP_mrr": popmrr,
        "lm_SCRAMBLE_h10": scr10, "lm_reach_ceiling": reach_lm,
        "lm_fair_h10_per_ranker": fair_h10, "lm_fair_mrr_per_ranker": fair_mrr,
        "BEST_FAIR_h10": best_h10, "BEST_FAIR_h10_ranker": best_h10_name,
        "BEST_FAIR_mrr": best_mrr, "BEST_FAIR_mrr_ranker": best_mrr_name,
        "best_beats_pop": best_beats_pop, "scramble_fails": scramble_fails,
        "freq_leak_ok": freq_leak_ok, "fair_bounded": fair_bounded, "arms_differ": arms_differ,
        "high_POP_h10": hi_pop10, "high_reach": hi_reach,
        "aggregate_POP_h10": agg_pop10, "aggregate_BEST_h10": agg_best,
    }
    return v, msg, gates


# ============================ self-test =======================================
def _selftest():
    """Planted graph: low-mult gold reachable by TWO distinct rules (1 grounding each); a HUB
    reachable by ONE rule via MANY groundings (grounding-inflated noisy-OR). The additive
    rule-dedupe ranker must promote the gold above the hub where SYM_BASE does not."""
    print("[selftest] building planted rank-discriminator graph...", flush=True)
    class Rt:
        pass
    g = Rt()
    g.out_adj_rel = defaultdict(lambda: defaultdict(list))
    g.in_adj_rel = defaultdict(lambda: defaultdict(list))
    g.out_by_node = defaultdict(list)
    g.in_by_node = defaultdict(list)
    g.edge_rels = defaultdict(set)
    g.n_ent = 1000
    H, G, U = 1, 2, 3
    g.out_adj_rel[10][H] = [G]            # rule A (L1F 10) -> G
    g.out_adj_rel[11][H] = [G]            # rule B (L1F 11) -> G  (corroboration)
    mids = list(range(100, 108))          # rule C (L2 12,13) -> U via 8 groundings
    g.out_adj_rel[12][H] = mids
    for mi in mids:
        g.out_adj_rel[13][mi] = [U]
    rules = [("L1F", 10, 0, 0.6, 50), ("L1F", 11, 0, 0.6, 50), ("L2", 12, 13, 0.6, 50)]

    base = rank_score("SYM_BASE", g, H, 99, rules)
    plus = rank_score("add_g05_b0", g, H, 99, rules)
    assert base[U] > base[G], "setup broken: base should inflate U (U=%.4f G=%.4f)" % (base[U], base[G])
    assert plus[G] > plus[U], "D1 FAIL: additive rule-dedupe did not promote low-mult gold over grounding-hub (G=%.3f U=%.3f)" % (plus[G], plus[U])

    rng = random.Random(0); wins = 0
    for _ in range(200):
        sc = scramble_scores(plus, rng)
        if sc[G] > sc[U]:
            wins += 1
    frac = wins / 200.0
    assert 0.3 <= frac <= 0.7, "D2 FAIL: scramble not random (G>U frac=%.2f)" % frac

    g.node_degree = Counter({G: 3, U: 900})
    g.rel_tail_freq = defaultdict(Counter); g.rel_tail_freq[99] = Counter({U: 5000, G: 1})
    plus2 = rank_score("add_g05_b0", g, H, 99, rules)
    assert plus2 == plus, "D3 FAIL: ranker score changed when freq/degree present -> LEAK"

    # every panel ranker must produce a score dict (no crash) + differ from POP-style
    for rn in FAIR_SET:
        sc = rank_score(rn, g, H, 99, rules)
        assert G in sc and U in sc, "panel ranker %s missing candidates" % rn

    print("[selftest] PASS: D1 base(U=%.4f>G=%.4f) add(G=%.3f>U=%.3f) | D2 scramble G>U frac=%.2f | D3 no-leak | panel=%d ok"
          % (base[U], base[G], plus[G], plus[U], frac, len(FAIR_SET)), flush=True)


# ============================ start-marker / crash ============================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ============================ main ============================================
def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    t0 = time.time()
    print("[config] anchor=%s mode=%s seeds=%s N_EVAL=%d MIN_SUPPORT=%d panel=%s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_EVAL, MIN_SUPPORT, PANEL), flush=True)

    train, valid, test = E._load_fb15k237()
    ent2i, rel2i = E.build_ids(train, valid, test)
    print("[data] train=%d valid=%d test=%d ent=%d rel=%d avgdeg=%.2f"
          % (len(train), len(valid), len(test), len(ent2i), len(rel2i),
             2.0 * len(train) / len(ent2i)), flush=True)

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
        lm = r["low_mid"]
        bestn = max(FAIR_SET, key=lambda rn: lm[rn + "_h10"])
        print("[seed %d] low+mid: POP h@10=%.3f | BEST_FAIR h@10=%.3f (%s) | SYM_BASE h@10=%.3f | "
              "SCR h@10=%.3f | reach=%.3f | leak_ok=%s arms_differ=%s q1=%d q2=%d rules=%d (%.1fs)"
              % (seed, lm["POP_h10"], lm[bestn + "_h10"], bestn, lm["SYM_BASE_h10"], lm["SCR_h10"],
                 lm["reach"], r["meta"]["freq_leak_ok"], r["meta"]["arms_differ"],
                 r["meta"]["q1"], r["meta"]["q2"], r["meta"]["n_rules_dense"], time.time() - ts), flush=True)

    verdict, vmsg, gates = compute_verdict(per_seed)
    elapsed = time.time() - t0

    if len(per_seed) != EXPECTED_N_UNITS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = "expected %d seed-units got %d :: %s" % (EXPECTED_N_UNITS, len(per_seed), vmsg)

    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
               "summary": vmsg[:200], "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
               "elapsed_s": elapsed, "gates": gates, "per_seed": per_seed,
               "cardinality_ok": len(per_seed) == EXPECTED_N_UNITS}
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
