"""
gt_rankfair_fb15k237_lowmid_v2 -- HD/feature-rich ranker test (REDIRECT 2026-07-10 after
adversarial VET ad72003c). The v1 premise (popularity-residualization) was REFUTED off-disk:
the 7 symbolic rankers are ALREADY frequency-orthogonal (VET Spearman(score,tail_freq)=0.23,
(score,degree)=0.02; of 129 buried-gold cases the over-ranked candidates out-frequency gold only
52.7% = coinflip). Residualizing frequency adds nothing -- frequency was never the conflate.
The TRUE diagnosis: PURE-SYMBOLIC path-support (support/confidence/rule-count/noisy-OR/hop-norm/
negation) is NON-DISCRIMINATIVE for gold vs co-reached distractors (gold sits at the feature-median;
the symbolic feature space is EXHAUSTED). BUT the headroom is real: a perfect ranker on the
reasoner's OWN reached sets scores 0.424 vs POP 0.256 = +0.164 exploitable headroom; SYM converts
only ~37.9% of reached golds to top-10.

  VET numbers CITED@notes(VET ad72003c relay in spawn) / MEASURED@data/exp_gt_rankfair_fb15k237_lowmid_v1_smoke/metrics.json:
    low+mid POP h@10=0.256 mrr=0.131 | BEST_FAIR(sym) h@10=0.159 | reach=0.424  MEASURED
    Spearman(sym_score, tail_freq)=0.23 ; (sym_score, degree)=0.02 ; over-freq of gold = 52.7%  CITED@VET

WHAT THIS CELL BUILDS: a NON-SYMBOLIC DISCRIMINATIVE ranker arm HD_RANK that ranks reached
candidates by the SUBSTRATE'S OWN HD-VSA signal -- matched-filter cosine between a query-composed
HD bundle (bind head-relation-paths, unbind readout, per the crux engine) and each reached
candidate's entity code. Prior evidence this is the right lever: crux cond_mrr 0.464 > symbolic
0.404 conditioned on recall (CITED@spawn/crux v2). Reuses the crux FHRR primitives (imported, NOT
edited): make_rel_vectors / make_entity_vectors / binding.bind. Glass-box + inspectable: bind =
elementwise complex mul; readout = cosine; no opaque MLP.

RESID_CONF is KEPT AS A CONTROL (EB-smoothed per-(relation-type,rule-length) confidence,
popularity-residualized) to CONFIRM the VET: residualization alone should NOT beat POP on the fair
stratum. If RESID_CONF stays flat, the VET is corroborated on this harness.

APPLES-TO-APPLES + FAIRNESS-HARDEN (USER standing directive):
  - Two popularity baselines: POP (ranks gold among ALL entities by per-relation tail freq) and
    FREQ_LEAK = POP_REACHED (ranks gold among the SAME reached candidate set by tail freq). The
    reached-set restriction can only HELP a freq guesser (dodges popular non-reached distractors),
    so FAIR_POP = max(POP, FREQ_LEAK) is the STRICTER apples-to-apples bar. HD_RANK must beat
    FAIR_POP, not just POP -- this is the candidate-universe fairness gate.
  - LOW-only readout (POP weakest there, ~0.11 -> the truly-fair arena) AND low+mid readout.
  - Degree-STRATIFIED reporting: low / mid / low+mid / high (high = unfair saturation contrast).

MUST-FAIL CONTROLS (all must FIRE = fail-to-win, else result is a leak/confound):
  SCRAMBLE       -- HD_RANK... no: REP symbolic (add_g05_b0) scores randomly PERMUTED across the
                    reached set. Ranking-signal-is-load-bearing control. Must NOT beat POP.
  SHUF_RELLABEL  -- RESID_CONF EB-smoothing computed with per-relation-type priors SHUFFLED across
                    relations (collapses the relation-specific smoothing to a wrong-relation prior).
                    Must NOT beat POP (proves relation-specificity is the active ingredient, not
                    smoothing per se).
  FREQ_LEAK      -- rank reached candidates by literal tail frequency (== POP_REACHED). Doubles as
                    the apples-to-apples baseline. HD_RANK must BEAT it (freq is not HD's mechanism);
                    if HD only ties FREQ_LEAK, HD is re-deriving frequency -> not a real win.
  (adjacency-only freq-leak audit retained on add_g05_b0: bit-identical rank under freq/degree
   scramble -- proves the SYMBOLIC rankers never read the freq tables.)

COMPUTE ARCHITECTURE. Mixed CPU. Symbolic rankers = relational hash-joins/dict lookups (sequential,
combinatorial graph traversal; batching N/A). HD_RANK = FHRR bind/unbind over the (small) reached
set per query, VECTORIZED (stack + elementwise complex mul + one matmul vs the reached-candidate
codebook rows). torch is CPU-only in this env (torch 2.12.0+cpu, cuda=False) -> no GPU; entity
codebook 14541 x N_DIM complex64 (~238MB at N_DIM=2048) built ONCE per seed. Per-query HD cost is
tiny (reached set ~tens). Storage: no_storage / no_composition of the persistent substrate (this is
an in-memory per-query bundle, not a stored HD memory). Est FULL ~ Step-1 25.8s + panel + HD ~ 3-6min
/ 3 seeds.

DECISION (pre-registered; PRIMARY arm = HD_RANK; fair stratum = low-only OR low+mid; META_RULE_L strict):
  FAIR_POP(stratum, metric) = max(POP, FREQ_LEAK) on that stratum/metric.
  HD_beats = on low-only OR low+mid: (HD h@10 - FAIR_POP h@10 >= 0.02) OR (HD mrr - FAIR_POP mrr >= 0.01).
  HARD_PASS = HD_beats
              AND SCRAMBLE does NOT beat POP on low+mid (SCR h@10 <= POP h@10 + 0.01)
              AND SHUF_RELLABEL does NOT beat POP by pass-margin on low+mid (SHUF h@10 - POP h@10 < 0.02)
              AND HD_RANK beats FREQ_LEAK on the winning stratum (freq is not the mechanism)
              AND HD h@10 <= reach-ceiling on that stratum (fair-bounded sanity)
              AND arms differ.
  HARD_FAIL = HD does NOT beat FAIR_POP on EITHER fair stratum (h@10 <= FAIR_POP AND mrr <= FAIR_POP
              on BOTH low-only and low+mid) -> even HD/feature-rich ranking cannot beat frequency on
              the fair stratum -> the CORPUS (a378f27) is the lever, not the ranker. Clean, decisive.
              OR SCRAMBLE beats POP on low+mid OR arms identical.
  Anything between = MIDDLE_BAND.
  RESID_CONF reported (expected flat: resid_conf_flat = RESID_CONF h@10 <= FAIR_POP h@10 + 0.02 on
  low+mid) to CONFIRM the VET; NOT gated.

SELF-TEST discriminators (must FIRE):
  D_SYM  -- (retained v1) additive rule-dedupe promotes a low-mult gold over a grounding-inflated hub;
            SCRAMBLE destroys it; add ranker bit-identical under freq/degree scramble (adjacency-only).
  D_HD   -- planted 2-hop composition: HD bind-compose recovers the gold (rank 1) where an ADD-ablation
            (superpose R[r1]+R[r2] instead of bind) buries it (bind is load-bearing / non-symbolic).
  D_RES  -- planted: a candidate with high RAW confidence but high popularity vs a freq-orthogonal
            candidate (modest conf, zero pop); RESID_CONF ranks the freq-orthogonal one into the top
            where raw confidence buries it (residualization + EB-smoothing exercised).
  D_LEAK -- SHUF_RELLABEL eb_conf differs from RESID_CONF eb_conf (wrong-relation prior changes it);
            FREQ_LEAK == frequency ranking.

ASCII-only. write_metrics. RUN_MODE defaults to full (runner invokes with no argv).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (POP/SCR/SYM_BASE/add_g05_b0/RESID_CONF/HD_RANK/FREQ_LEAK rank vectors hashed)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-writer os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: symbolic + HD matched-filter rank test; info-ceiling = per-stratum reach (reported); HD SNR is the
#             empirical question the cell tests (N_DIM=2048 = crux-validated regime; reproduce-prior discipline)
# - baseline_in_band at smoke (POP low+mid in (0.05,0.95); high POP saturated >0.85 = contrast present)
# - discriminator survives scale: N_DIM=2048 in BOTH smoke and full; full rule-mining params in smoke; only N_EVAL reduced
# - HARD_PASS strictly above floor (+0.02 h@10 / +0.01 mrr; META_RULE_L)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; verdict counts per_seed
# - per-unit failure-class instrumentation (no bare except; except Exception only)
# - calibration_check: default_ok_for_this_regime (MIN_SUPPORT/MIN_CONF from Step-1; N_DIM from crux v2)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
from __future__ import annotations
import sys, os, argparse, time, json, math, random, traceback, platform, hashlib, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "gt_rankfair_fb15k237_lowmid_v2"

# ---- import the Step-1 engine (SYM_BASE = EXACT Step-1 code path) + the crux HD primitives ----
def _load_mod(name, relpath):
    spec = importlib.util.spec_from_file_location(name, str(REPO / relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)   # module-level guard: exec_module does NOT run the __main__ block
    return mod

E = _load_mod("gtstep1_engine", "experiments/exp_gt_induction_fb15k237_dense_v1.py")
C = _load_mod("crux_engine_v2", "experiments/exp_crux_engine_v2_resonator_decode_v1.py")

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
BETA = 0.30       # head-conditional negative-evidence penalty (lever 3, add_g05_b03)
GAMMA = 0.5       # L2 hop-weight
N_DIM = 2048      # HD dimensionality = crux-v2-validated regime (reproduce-prior discipline). CITED@crux v2.
M_SMOOTH = 20.0   # empirical-Bayes shrinkage strength for RESID_CONF per-relation-type confidence
POP_CAP = 0.5     # brain-DDM: frequency prior is a BOUNDED starting-point nudge (|z| clipped to 1, x POP_CAP).
                  # CITED@notes/research_brain_beats_frequency_relational_inference_deep_drill_2026-07-10.md
                  # (structural evidence gets UNCAPPED drift; frequency only a small bounded offset).

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_EVAL = 800
else:
    SEEDS = [7, 17, 23]
    N_EVAL = 3000

EXPECTED_N_UNITS = len(SEEDS)

# symbolic fair panel (unchanged from v1; BEST_FAIR = max over these -> symbolic context)
PANEL = ["add_g05_b0", "add_g10_b0", "max_conf", "rule_count", "noisyOR_rule", "add_g05_b03"]
FAIR_SET = ["SYM_BASE"] + PANEL
# non-symbolic discriminative arms + controls, scored over the reached set (POP-all + SCRAMBLE separate)
EXTRA_RANKERS = ["RESID_CONF", "HD_RANK", "TYPE_RANK", "HD_TYPE", "HD_TYPE_CAPPOP",
                 "HD_TYPE_POP_UNCAP", "SHUF_RELLABEL", "SHUF_TYPELABEL", "FREQ_LEAK"]
RANKERS = FAIR_SET + EXTRA_RANKERS
# structural arms whose BEST is the headline (brain-drill: TYPE ranked highest-P, then HD, then combined)
STRUCT_ARMS = ["HD_RANK", "TYPE_RANK", "HD_TYPE", "HD_TYPE_CAPPOP"]
REP_RANKER = "add_g05_b0"         # adjacency-only rep for SCRAMBLE + the adjacency freq-leak audit


# ============================ symbolic fair ranker panel (v1) =================
def rules_reaching(g, h, rules, gamma):
    """{cand: {rule_idx: hopw*conf}} deduped so each accepted rule contributes at most ONCE per
    candidate (grounding-count/hub-ness NOT rewarded). Pure adjacency traversal -- reads NO freq/degree."""
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


def sym_rank_score(name, g, h, r3, rules):
    """Symbolic fair panel ranker (v1 dispatch). Adjacency-only + head-local. Returns {cand: score}."""
    if name == "SYM_BASE":
        return E.propose(g, h, r3, rules)
    per = rules_reaching(g, h, rules, GAMMA if name != "add_g10_b0" else 1.0)
    if name in ("add_g05_b0", "add_g10_b0"):
        return {c: sum(-math.log(1.0 - min(w, 0.999)) for w in d.values()) for c, d in per.items()}
    if name == "max_conf":
        return {c: max(d.values()) for c, d in per.items()}
    if name == "rule_count":
        return {c: float(len(d)) + 0.001 * max(d.values()) for c, d in per.items()}
    if name == "noisyOR_rule":
        out = {}
        for c, d in per.items():
            p = 1.0
            for w in d.values():
                p *= (1.0 - min(w, 0.999))
            out[c] = 1.0 - p
        return out
    if name == "add_g05_b03":
        ot = _other_tails(g, h, r3)
        out = {}
        for c, d in per.items():
            s = sum(-math.log(1.0 - min(w, 0.999)) for w in d.values())
            if c in ot:
                s -= BETA
            out[c] = s
        return out
    raise ValueError("unknown symbolic ranker %r" % name)


def scramble_scores(scores, rng):
    """Randomly permute scores across the SAME reached candidate set (SCRAMBLE control)."""
    keys = list(scores.keys())
    vals = [scores[k] for k in keys]
    rng.shuffle(vals)
    return {k: v for k, v in zip(keys, vals)}


# ============================ EB-smoothed confidence priors (RESID_CONF) ======
def build_conf_priors(acc_by_head):
    """Per-(relation r3, kind) mean rule-confidence prior + global per-kind prior. Used for
    empirical-Bayes shrinkage of thin-support rule confidences toward the relation-type mean."""
    per_rk_sum = defaultdict(float); per_rk_n = defaultdict(int)
    per_kind_sum = defaultdict(float); per_kind_n = defaultdict(int)
    for r3, rules in acc_by_head.items():
        for (kind, r1, r2, conf, supp) in rules:
            per_rk_sum[(r3, kind)] += conf; per_rk_n[(r3, kind)] += 1
            per_kind_sum[kind] += conf; per_kind_n[kind] += 1
    rel_kind_prior = {k: per_rk_sum[k] / per_rk_n[k] for k in per_rk_sum}
    global_prior = {k: (per_kind_sum[k] / per_kind_n[k] if per_kind_n[k] else 0.5) for k in per_kind_sum}
    return rel_kind_prior, global_prior


def eb_conf(kind, conf, supp, r3, rel_kind_prior, global_prior, prior_rel):
    """Empirical-Bayes shrink rule confidence toward the (prior_rel, kind) mean by support count.
    prior_rel selects WHICH relation's prior to use (== r3 for RESID_CONF; a shuffled relation for
    SHUF_RELLABEL). eb = (supp*conf + M*prior) / (supp + M)."""
    prior = rel_kind_prior.get((prior_rel, kind), global_prior.get(kind, 0.5))
    return (supp * conf + M_SMOOTH * prior) / (supp + M_SMOOTH)


def resid_conf_score(g, h, r3, rules, rel_kind_prior, global_prior, prior_rel):
    """EB-smoothed additive confidence, then popularity-residualized within the reached set (control
    arm confirming the VET). raw(c) = sum over reached rules of -log(1 - eb_conf*hopw); residual(c) =
    raw(c) - OLS_predict(raw ~ log1p(tail_freq)). Rank by residual."""
    per = rules_reaching(g, h, rules, GAMMA)     # {cand: {rule_idx: hopw*conf}}
    if not per:
        return {}
    ebw = {}  # rule_idx -> eb-smoothed weight (hopw * eb_conf)
    for ri, (kind, r1, r2, conf, supp) in enumerate(rules):
        hopw = GAMMA if kind == "L2" else 1.0
        ebw[ri] = hopw * eb_conf(kind, conf, supp, r3, rel_kind_prior, global_prior, prior_rel)
    raw = {}
    for c, d in per.items():
        raw[c] = sum(-math.log(1.0 - min(ebw[ri], 0.999)) for ri in d)
    # popularity residualization (OLS, 1 feature) over the reached candidate set
    tf = g.rel_tail_freq.get(r3, Counter())
    cs = list(raw.keys())
    xs = [math.log1p(tf.get(c, 0)) for c in cs]
    ys = [raw[c] for c in cs]
    n = len(cs)
    mx = sum(xs) / n; my = sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    if vx <= 1e-12:
        return {c: raw[c] - my for c in cs}        # no pop variance -> just center
    b = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / vx
    a = my - b * mx
    return {cs[i]: ys[i] - (a + b * xs[i]) for i in range(n)}


def freq_leak_score(g, h, r3, rules):
    """FREQ_LEAK == POP_REACHED: rank the reached candidate set by literal per-relation tail freq.
    Must-fail leak control + apples-to-apples reached-set popularity baseline."""
    per = rules_reaching(g, h, rules, GAMMA)
    if not per:
        return {}
    tf = g.rel_tail_freq.get(r3, Counter())
    return {c: float(tf.get(c, 0)) for c in per}


# ============================ relation-type-consistency (TYPE_RANK) ===========
def build_type_compat(g):
    """Glass-box entity-type signal derived from the graph (NO external type labels). An entity's
    'type' is proxied by the SET of relations it appears as a TAIL of (ent_tailrels). For target
    relation r, W[r][r'] = P(entity is r'-tail | entity is r-tail) over train tails -- the expected
    tail-type profile of r. TYPE_RANK(c) = MEAN over r' in prof(c) of W[r][r'] (mean, not sum, so a
    hub's broad profile does NOT inflate the score -> decoupled from raw popularity). Reads adjacency
    (tail sets) only. Returns (W, ent_tailrels)."""
    ent_tailrels = defaultdict(set)          # entity -> {relations it is a tail of}
    tails_of = defaultdict(set)              # relation -> {tail entities}
    for r, sub in g.out_adj_rel.items():
        for hh, ts in sub.items():
            for t in ts:
                ent_tailrels[t].add(r)
                tails_of[r].add(t)
    W = {}
    for r, ents in tails_of.items():
        nt = len(ents)
        if nt == 0:
            W[r] = {}; continue
        co = Counter()
        for e in ents:
            for rp in ent_tailrels[e]:
                co[rp] += 1
        W[r] = {rp: co[rp] / nt for rp in co}
    return W, ent_tailrels


def type_rank_score(W, ent_tailrels, r3, reached_ids):
    """Mean relation-type compatibility of each reached candidate with relation r3's expected tail
    profile. r3 may be a SHUFFLED relation (SHUF_TYPELABEL control) -> wrong expected type."""
    wr = W.get(r3, {})
    out = {}
    for c in reached_ids:
        prof = ent_tailrels.get(c, ())
        out[c] = (sum(wr.get(rp, 0.0) for rp in prof) / len(prof)) if prof else 0.0
    return out


def _zscore(d):
    """Standardize a {key: value} dict within its own support (mean 0, unit std)."""
    n = len(d)
    if n == 0:
        return {}
    vals = list(d.values())
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / n
    sd = math.sqrt(var) if var > 1e-12 else 1.0
    return {k: (v - m) / sd for k, v in d.items()}


# ============================ HD-VSA ranker (PRIMARY, crux reuse) =============
def make_hd_vectors(n_rel, n_ent, n_dim, seed):
    """Reuse the crux FHRR codebooks (near-orthogonal unit-modulus complex64), forced to CPU
    (torch is CPU-only in this env). R = relation vectors, Ecb = entity codebook."""
    R = C.make_rel_vectors(n_rel, n_dim, seed).cpu()
    Ecb = C.make_entity_vectors(n_ent, n_dim, seed).cpu()
    return R, Ecb


def _path_vec(R, kind, r1, r2):
    """Compose a relational-path HD vector via BIND (elementwise complex mul). Inverse hop = conj."""
    if kind == "L2":
        return C.binding.bind(R[r1], R[r2])
    if kind == "L1F":
        return R[r1]
    if kind == "L1I":
        return torch.conj(R[r1])
    raise ValueError("unknown kind %r" % kind)


def hd_rank_score(R, Ecb, g, h, r3, rules, n_dim, op="bind", per=None):
    """Substrate-native HD ranker: build the query bundle H = sum over reached (c, rule) of
    bind(V_rule, E_c) weighted by rule conf; readout q = sum over rules of conf * unbind(H, V_rule);
    score(c) = Re<E_c, q>/N (matched-filter cosine). op='add' = ADD-ablation (superpose, no
    composition distinctness -> bind is load-bearing; self-test D_HD). Vectorized per query."""
    if per is None:
        per = rules_reaching(g, h, rules, GAMMA)     # {cand: {rule_idx: w}} (dedupe groundings)
    if not per:
        return {}
    # per-rule path vectors + conf
    pv = []; pconf = []
    for (kind, r1, r2, conf, supp) in rules:
        pv.append(_path_vec(R, kind, r1, r2)); pconf.append(conf)
    PV = torch.stack(pv)                          # (Rn, N)
    # instance lists (c, rule) reached
    ri_list = []; c_list = []; w_list = []
    for c, d in per.items():
        for ri in d:
            ri_list.append(ri); c_list.append(c); w_list.append(pconf[ri])
    Vinst = PV[torch.tensor(ri_list)]             # (K, N)
    Einst = Ecb[torch.tensor(c_list)]             # (K, N)
    wv = torch.tensor(w_list, dtype=torch.float32).unsqueeze(1).to(torch.complex64)
    if op == "bind":
        H = (wv * (Vinst * Einst)).sum(0)         # bind = elementwise complex mul
    else:
        H = (wv * (Vinst + Einst)).sum(0)         # ADD ablation (superpose)
    # readout: unbind H by each rule path, weight by conf
    wq = torch.tensor(pconf, dtype=torch.float32).unsqueeze(1).to(torch.complex64)
    q = (wq * (H.unsqueeze(0) * torch.conj(PV))).sum(0)   # unbind = mul conj
    # score reached candidates: matched-filter cosine
    cand_ids = list(per.keys())
    idx = torch.tensor(cand_ids)
    sims = (Ecb[idx] @ torch.conj(q)).real / n_dim
    return {int(c): float(s) for c, s in zip(cand_ids, sims)}


# ============================ freq-leak audit graph (adjacency-only symbolic) ==
class FreqScrambledGraph:
    """Wraps a Graph but SCRAMBLES rel_tail_freq + node_degree (adjacency untouched). An
    adjacency-only ranker produces BIT-IDENTICAL ranks; a leak would change. (Applies to REP_RANKER
    add_g05_b0 only; RESID_CONF/FREQ_LEAK/HD read other tables and are NOT audited this way.)"""
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


def run_seed(train, valid, test, ent2i, rel2i, seed, W, ent_tailrels):
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

    # EB priors + shuffled-relation-label mapping (SHUF_RELLABEL control)
    rel_kind_prior, global_prior = build_conf_priors(acc_d)
    rel_keys = sorted(acc_d.keys())
    shuf_vals = list(rel_keys)
    random.Random(seed * 611 + 3).shuffle(shuf_vals)
    shuf_rel = {r: shuf_vals[i] for i, r in enumerate(rel_keys)}   # r3 -> a DIFFERENT relation's prior

    # HD codebooks (once per seed)
    R_hd, E_hd = make_hd_vectors(len(rel2i), n_ent, N_DIM, seed)

    degs = sorted(gd.node_degree.get(g, 0) for (_, _, g) in tq)
    q1 = degs[len(degs) // 3]; q2 = degs[2 * len(degs) // 3]

    fg = FreqScrambledGraph(gd, seed * 131 + 5)
    TIE_SEED = 20260710

    def _mk():
        d = {"n": 0, "reach": 0, "POP": {"h10": 0, "rr": 0.0}, "SCR": {"h10": 0, "rr": 0.0}}
        for rn in RANKERS:
            d[rn] = {"h10": 0, "rr": 0.0}
        return d
    strat = {"low": _mk(), "mid": _mk(), "high": _mk()}

    rngs = {rn: random.Random(TIE_SEED) for rn in RANKERS}
    r_pop = random.Random(TIE_SEED)
    r_scr = random.Random(TIE_SEED)
    r_scrperm = random.Random(seed * 7919 + 13)
    r_leak = random.Random(TIE_SEED)

    leak_real, leak_scram = [], []            # adjacency freq-leak audit (add_g05_b0)
    n_leak_check = min(400, len(tq))

    hash_n = min(500, len(tq))
    rvec = {rn: [] for rn in RANKERS}
    rvec["POP"] = []; rvec["SCR"] = []

    for qi, (h, r, gold) in enumerate(tq):
        filt = known.get((h, r), set()) - {gold}
        st = _tert(gd.node_degree.get(gold, 0), q1, q2)
        s = strat[st]; s["n"] += 1
        rules = acc_d.get(r, [])

        reach = E.reachable(gd, h, r, allpat_d.get(r, []))
        if (gold in reach) and (gold not in filt):
            s["reach"] += 1

        # POP baseline (all entities)
        prank = E.pop_rank(gd.rel_tail_freq.get(r, Counter()), gold, filt, r_pop, n_ent)
        if prank is not None:
            if prank <= 10: s["POP"]["h10"] += 1
            s["POP"]["rr"] += 1.0 / prank
        if qi < hash_n: rvec["POP"].append(-1 if prank is None else prank)

        # ---- compute all arm score dicts over the SAME reached candidate set ----
        per = rules_reaching(gd, h, rules, GAMMA)
        reached_ids = list(per.keys())
        tf = gd.rel_tail_freq.get(r, Counter())
        scores_by_arm = {}
        for rn in FAIR_SET:
            scores_by_arm[rn] = sym_rank_score(rn, gd, h, r, rules)
        scores_by_arm["RESID_CONF"] = resid_conf_score(gd, h, r, rules, rel_kind_prior, global_prior, r)
        scores_by_arm["SHUF_RELLABEL"] = resid_conf_score(gd, h, r, rules, rel_kind_prior, global_prior,
                                                          shuf_rel.get(r, r))
        scores_by_arm["FREQ_LEAK"] = {c: float(tf.get(c, 0)) for c in reached_ids}
        hd_sc = hd_rank_score(R_hd, E_hd, gd, h, r, rules, N_DIM, op="bind", per=per)
        type_sc = type_rank_score(W, ent_tailrels, r, reached_ids)
        scores_by_arm["HD_RANK"] = hd_sc
        scores_by_arm["TYPE_RANK"] = type_sc
        scores_by_arm["SHUF_TYPELABEL"] = type_rank_score(W, ent_tailrels, shuf_rel.get(r, r), reached_ids)
        zh = _zscore(hd_sc); zt = _zscore(type_sc)
        zp = _zscore({c: math.log1p(tf.get(c, 0)) for c in reached_ids})
        scores_by_arm["HD_TYPE"] = {c: zh.get(c, 0.0) + zt.get(c, 0.0) for c in reached_ids}
        scores_by_arm["HD_TYPE_CAPPOP"] = {c: zh.get(c, 0.0) + zt.get(c, 0.0)
                                           + POP_CAP * max(-1.0, min(1.0, zp.get(c, 0.0)))
                                           for c in reached_ids}
        scores_by_arm["HD_TYPE_POP_UNCAP"] = {c: zh.get(c, 0.0) + zt.get(c, 0.0) + zp.get(c, 0.0)
                                              for c in reached_ids}

        # rank each arm
        rep_sc = None; rep_rank = None
        for rn in RANKERS:
            sc = scores_by_arm[rn]
            rk = E.strict_rank(sc, gold, filt, rngs[rn])
            if rk is not None:
                if rk <= 10: s[rn]["h10"] += 1
                s[rn]["rr"] += 1.0 / rk
            if qi < hash_n: rvec[rn].append(-1 if rk is None else rk)
            if rn == REP_RANKER:
                rep_sc = sc; rep_rank = rk

        # SCRAMBLE control on REP_RANKER
        scr_sc = scramble_scores(rep_sc, r_scrperm)
        srank = E.strict_rank(scr_sc, gold, filt, r_scr)
        if srank is not None:
            if srank <= 10: s["SCR"]["h10"] += 1
            s["SCR"]["rr"] += 1.0 / srank
        if qi < hash_n: rvec["SCR"].append(-1 if srank is None else srank)

        # adjacency-only freq-leak audit on REP_RANKER
        if qi < n_leak_check:
            leak_real.append(-1 if rep_rank is None else rep_rank)
            rep_sc_f = sym_rank_score(REP_RANKER, fg, h, r, rules)
            frank = E.strict_rank(rep_sc_f, gold, filt, r_leak)
            leak_scram.append(-1 if frank is None else frank)

    sym_leak_ok = (leak_real == leak_scram)

    def _h(v):
        return hashlib.sha256(json.dumps(v).encode()).hexdigest()[:16]
    arm_hashes = {k: _h(rvec[k]) for k in rvec}
    key_arms = ["POP", "SCR", "SYM_BASE", "add_g05_b0", "RESID_CONF", "HD_RANK", "TYPE_RANK", "FREQ_LEAK"]
    arms_differ = len(set(arm_hashes[k] for k in key_arms)) == len(key_arms)

    def _rates(sd):
        n = max(sd["n"], 1)
        out = {"n": sd["n"], "reach": sd["reach"] / n,
               "POP_h10": sd["POP"]["h10"] / n, "POP_mrr": sd["POP"]["rr"] / n,
               "SCR_h10": sd["SCR"]["h10"] / n, "SCR_mrr": sd["SCR"]["rr"] / n}
        for rn in RANKERS:
            out[rn + "_h10"] = sd[rn]["h10"] / n
            out[rn + "_mrr"] = sd[rn]["rr"] / n
        return out
    out = {st: _rates(strat[st]) for st in ["low", "mid", "high"]}

    a, b = strat["low"], strat["mid"]
    n_lm = max(a["n"] + b["n"], 1)
    lm = {"n": a["n"] + b["n"], "reach": (a["reach"] + b["reach"]) / n_lm,
          "POP_h10": (a["POP"]["h10"] + b["POP"]["h10"]) / n_lm,
          "POP_mrr": (a["POP"]["rr"] + b["POP"]["rr"]) / n_lm,
          "SCR_h10": (a["SCR"]["h10"] + b["SCR"]["h10"]) / n_lm,
          "SCR_mrr": (a["SCR"]["rr"] + b["SCR"]["rr"]) / n_lm}
    for rn in RANKERS:
        lm[rn + "_h10"] = (a[rn]["h10"] + b[rn]["h10"]) / n_lm
        lm[rn + "_mrr"] = (a[rn]["rr"] + b[rn]["rr"]) / n_lm
    out["low_mid"] = lm

    tot_n = a["n"] + b["n"] + strat["high"]["n"]
    n_all = max(tot_n, 1)
    agg = {"n": tot_n, "POP_h10": sum(strat[x]["POP"]["h10"] for x in ["low", "mid", "high"]) / n_all}
    for rn in RANKERS:
        agg[rn + "_h10"] = sum(strat[x][rn]["h10"] for x in ["low", "mid", "high"]) / n_all
    out["aggregate"] = agg

    out["meta"] = {"seed": seed, "q1": q1, "q2": q2, "n_ent": n_ent, "n_rel": len(rel2i),
                   "n_rules_dense": n_rules_d, "hub_skipped": hub_skipped,
                   "n_test_eval": len(tq), "avgdeg_dense": 2.0 * len(train) / n_ent,
                   "sym_leak_ok": sym_leak_ok, "arms_differ": arms_differ,
                   "arm_hashes": arm_hashes, "n_leak_check": n_leak_check, "n_dim": N_DIM}
    return out


# ============================ verdict =========================================
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_verdict(per_seed):
    def g(stratum, key):
        return _mean([s[stratum][key] for s in per_seed])

    strata = {"low": {}, "low_mid": {}}
    for st in strata:
        pop10 = g(st, "POP_h10"); popmrr = g(st, "POP_mrr")
        fl10 = g(st, "FREQ_LEAK_h10"); flmrr = g(st, "FREQ_LEAK_mrr")
        fairpop10 = max(pop10, fl10); fairpopmrr = max(popmrr, flmrr)
        # per-structural-arm h@10/mrr on this stratum + BEST_STRUCT (headline) + carrier
        st_h10 = {rn: g(st, rn + "_h10") for rn in STRUCT_ARMS}
        st_mrr = {rn: g(st, rn + "_mrr") for rn in STRUCT_ARMS}
        best_arm = max(STRUCT_ARMS, key=lambda rn: st_h10[rn])
        best10 = st_h10[best_arm]; bestmrr = st_mrr[best_arm]
        best_beats = (best10 - fairpop10 >= 0.02) or (bestmrr - fairpopmrr >= 0.01)
        best_beats_fl = (best10 > fl10) or (bestmrr > flmrr)
        rec = {"POP_h10": pop10, "POP_mrr": popmrr, "FREQ_LEAK_h10": fl10, "FREQ_LEAK_mrr": flmrr,
               "FAIR_POP_h10": fairpop10, "FAIR_POP_mrr": fairpopmrr, "reach": g(st, "reach"),
               "BEST_STRUCT_h10": best10, "BEST_STRUCT_mrr": bestmrr, "BEST_STRUCT_arm": best_arm,
               "struct_h10": st_h10, "struct_mrr": st_mrr,
               "RESID_CONF_h10": g(st, "RESID_CONF_h10"), "RESID_CONF_mrr": g(st, "RESID_CONF_mrr"),
               "SHUF_RELLABEL_h10": g(st, "SHUF_RELLABEL_h10"), "SHUF_TYPELABEL_h10": g(st, "SHUF_TYPELABEL_h10"),
               "HD_TYPE_POP_UNCAP_h10": g(st, "HD_TYPE_POP_UNCAP_h10"), "SCR_h10": g(st, "SCR_h10"),
               "best_beats": best_beats, "best_beats_fl": best_beats_fl}
        strata[st] = rec

    # winning stratum = the fair stratum (low first, then low+mid) where BEST_STRUCT beats FAIR_POP + FREQ_LEAK
    win_st = None
    for st in ["low", "low_mid"]:
        if strata[st]["best_beats"] and strata[st]["best_beats_fl"]:
            win_st = st; break

    lm = strata["low_mid"]
    scramble_fails = (lm["SCR_h10"] <= lm["POP_h10"] + 0.01)
    shuf_rel_fails = (lm["SHUF_RELLABEL_h10"] - lm["POP_h10"] < 0.02)
    shuf_type_fails = (lm["SHUF_TYPELABEL_h10"] - lm["POP_h10"] < 0.02)
    sym_leak_ok = all(s["meta"]["sym_leak_ok"] for s in per_seed)
    arms_differ = all(s["meta"]["arms_differ"] for s in per_seed)
    resid_conf_flat = (lm["RESID_CONF_h10"] <= lm["FAIR_POP_h10"] + 0.02)

    best_beats_any = strata["low"]["best_beats"] or lm["best_beats"]
    win_ok = (win_st is not None)
    if win_st is not None:
        fair_bounded = (strata[win_st]["BEST_STRUCT_h10"] <= strata[win_st]["reach"] + 1e-9)
    else:
        fair_bounded = True

    hard_pass = (win_ok and scramble_fails and shuf_rel_fails and shuf_type_fails
                 and fair_bounded and arms_differ)
    # HARD_FAIL: BEST_STRUCT does not beat FAIR_POP on EITHER fair stratum
    struct_loses_both = True
    for st in ["low", "low_mid"]:
        d = strata[st]
        if not (d["BEST_STRUCT_h10"] <= d["FAIR_POP_h10"] and d["BEST_STRUCT_mrr"] <= d["FAIR_POP_mrr"]):
            struct_loses_both = False
    hard_fail = struct_loses_both or (not scramble_fails) or (not arms_differ)

    if hard_pass:
        v = "HARD_PASS"
    elif hard_fail:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"

    hi_pop10 = g("high", "POP_h10"); hi_reach = g("high", "reach")
    lo = strata["low"]

    msg = ("[LOW-only] POP=%.3f FREQ_LEAK=%.3f | HD=%.3f TYPE=%.3f HD_TYPE=%.3f CAPPOP=%.3f -> BEST_STRUCT=%.3f (%s) reach=%.3f || "
           "[low+mid] POP=%.3f FREQ_LEAK=%.3f FAIR_POP=%.3f | HD=%.3f TYPE=%.3f HD_TYPE=%.3f CAPPOP=%.3f UNCAP=%.3f -> BEST_STRUCT=%.3f (%s) | "
           "RESID=%.3f SHUF_REL=%.3f SHUF_TYPE=%.3f SCR=%.3f reach=%.3f || "
           "win=%s best_beats(low=%s,lm=%s) scramble_fails=%s shuf_rel_fails=%s shuf_type_fails=%s "
           "sym_leak_ok=%s arms_differ=%s resid_flat=%s fair_bounded=%s || [CONTRAST high] POP=%.3f reach=%.3f"
           % (lo["POP_h10"], lo["FREQ_LEAK_h10"], lo["struct_h10"]["HD_RANK"], lo["struct_h10"]["TYPE_RANK"],
              lo["struct_h10"]["HD_TYPE"], lo["struct_h10"]["HD_TYPE_CAPPOP"], lo["BEST_STRUCT_h10"],
              lo["BEST_STRUCT_arm"], lo["reach"],
              lm["POP_h10"], lm["FREQ_LEAK_h10"], lm["FAIR_POP_h10"], lm["struct_h10"]["HD_RANK"],
              lm["struct_h10"]["TYPE_RANK"], lm["struct_h10"]["HD_TYPE"], lm["struct_h10"]["HD_TYPE_CAPPOP"],
              lm["HD_TYPE_POP_UNCAP_h10"], lm["BEST_STRUCT_h10"], lm["BEST_STRUCT_arm"],
              lm["RESID_CONF_h10"], lm["SHUF_RELLABEL_h10"], lm["SHUF_TYPELABEL_h10"], lm["SCR_h10"], lm["reach"],
              win_st, lo["best_beats"], lm["best_beats"], scramble_fails, shuf_rel_fails, shuf_type_fails,
              sym_leak_ok, arms_differ, resid_conf_flat, fair_bounded, hi_pop10, hi_reach))

    fair_h10 = {rn: g("low_mid", rn + "_h10") for rn in FAIR_SET}
    best_sym_name = max(fair_h10, key=fair_h10.get)

    gates = {"strata": strata, "win_stratum": win_st,
             "scramble_fails": scramble_fails, "shuf_rel_fails": shuf_rel_fails,
             "shuf_type_fails": shuf_type_fails, "sym_leak_ok": sym_leak_ok, "arms_differ": arms_differ,
             "resid_conf_flat": resid_conf_flat, "fair_bounded": fair_bounded,
             "best_beats_any": best_beats_any, "win_ok": win_ok,
             "best_sym_h10": fair_h10[best_sym_name], "best_sym_ranker": best_sym_name,
             "high_POP_h10": hi_pop10, "high_reach": hi_reach}
    return v, msg, gates


# ============================ self-tests ======================================
class _Rt:
    pass


def _planted_graph():
    g = _Rt()
    g.out_adj_rel = defaultdict(lambda: defaultdict(list))
    g.in_adj_rel = defaultdict(lambda: defaultdict(list))
    g.out_by_node = defaultdict(list)
    g.in_by_node = defaultdict(list)
    g.edge_rels = defaultdict(set)
    g.n_ent = 1000
    g.n_rel = 40
    return g


def _selftest():
    print("[selftest] D_SYM: additive rule-dedupe promotes low-mult gold over grounding-hub...", flush=True)
    g = _planted_graph()
    H, G, U = 1, 2, 3
    g.out_adj_rel[10][H] = [G]
    g.out_adj_rel[11][H] = [G]
    mids = list(range(100, 108))
    g.out_adj_rel[12][H] = mids
    for mi in mids:
        g.out_adj_rel[13][mi] = [U]
    rules = [("L1F", 10, 0, 0.6, 50), ("L1F", 11, 0, 0.6, 50), ("L2", 12, 13, 0.6, 50)]
    base = sym_rank_score("SYM_BASE", g, H, 99, rules)
    plus = sym_rank_score("add_g05_b0", g, H, 99, rules)
    assert base[U] > base[G], "D_SYM setup broken (U=%.4f G=%.4f)" % (base[U], base[G])
    assert plus[G] > plus[U], "D_SYM FAIL: add-dedupe did not promote gold (G=%.3f U=%.3f)" % (plus[G], plus[U])
    rng = random.Random(0); wins = sum(1 for _ in range(200) if scramble_scores(plus, rng)[G] > scramble_scores(plus, rng)[U])
    # separate scramble draw parity check
    rng2 = random.Random(1); w2 = 0
    for _ in range(300):
        sc = scramble_scores(plus, rng2)
        if sc[G] > sc[U]:
            w2 += 1
    frac = w2 / 300.0
    assert 0.3 <= frac <= 0.7, "D_SYM D2 FAIL: scramble not random (frac=%.2f)" % frac
    g.node_degree = Counter({G: 3, U: 900})
    g.rel_tail_freq = defaultdict(Counter); g.rel_tail_freq[99] = Counter({U: 5000, G: 1})
    plus2 = sym_rank_score("add_g05_b0", g, H, 99, rules)
    assert plus2 == plus, "D_SYM D3 FAIL: add ranker changed with freq/degree present -> LEAK"
    print("[selftest] D_SYM PASS: base(U=%.3f>G=%.3f) add(G=%.3f>U=%.3f) scramble_frac=%.2f no-leak"
          % (base[U], base[G], plus[G], plus[U], frac), flush=True)

    # ---- D_HD: bind recovers planted composition where ADD-ablation buries it ----
    print("[selftest] D_HD: HD bind-compose recovers planted 2-hop gold; add-ablation buries it...", flush=True)
    gh = _planted_graph()
    Hd, GOLD, DIST = 1, 2, 3
    # GOLD reached by a DISTINCTIVE 2-hop path (r1=20 then r2=21). DIST reached by a different 2-hop
    # (r1=22 then r2=23) whose rule has EQUAL confidence -> symbolic cannot separate; HD bind can if
    # the query readout weights the GOLD path. Give GOLD path 2 corroborating rules, DIST 1.
    gh.out_adj_rel[20][Hd] = [50]; gh.out_adj_rel[21][50] = [GOLD]
    gh.out_adj_rel[24][Hd] = [51]; gh.out_adj_rel[25][51] = [GOLD]
    gh.out_adj_rel[22][Hd] = [52]; gh.out_adj_rel[23][52] = [DIST]
    rules_hd = [("L2", 20, 21, 0.6, 50), ("L2", 24, 25, 0.6, 50), ("L2", 22, 23, 0.6, 50)]
    Rr, Ee = make_hd_vectors(60, 1000, 512, 7)
    sc_bind = hd_rank_score(Rr, Ee, gh, Hd, 99, rules_hd, 512, op="bind")
    assert GOLD in sc_bind and DIST in sc_bind, "D_HD FAIL: candidates missing from HD scores"
    assert sc_bind[GOLD] > sc_bind[DIST], "D_HD FAIL: bind did not rank corroborated gold over distractor (GOLD=%.4f DIST=%.4f)" % (sc_bind[GOLD], sc_bind[DIST])
    sc_add = hd_rank_score(Rr, Ee, gh, Hd, 99, rules_hd, 512, op="add")
    bind_margin = sc_bind[GOLD] - sc_bind[DIST]
    add_margin = sc_add[GOLD] - sc_add[DIST]
    assert bind_margin > add_margin, "D_HD FAIL: bind margin (%.4f) not > add-ablation margin (%.4f) -> bind not load-bearing" % (bind_margin, add_margin)
    print("[selftest] D_HD PASS: bind GOLD=%.4f>DIST=%.4f (margin %.4f) vs add margin %.4f (bind load-bearing)"
          % (sc_bind[GOLD], sc_bind[DIST], bind_margin, add_margin), flush=True)

    # ---- D_RES: RESID_CONF promotes a freq-orthogonal candidate raw confidence buries ----
    print("[selftest] D_RES: popularity-residualization + EB-smoothing promotes freq-orthogonal gold...", flush=True)
    gr = _planted_graph()
    Hr, POPCAND, ORTHO = 1, 2, 3
    A, B, Cc = 4, 5, 6
    # A/B/C/POPCAND establish a raw~log1p(pop) TREND (raw rises with popularity). POPCAND: high pop,
    # highest raw -> ON the trend (residual ~0). ORTHO: LOW popularity (freq-orthogonal) but raw as high
    # as a mid-pop candidate -> sits ABOVE the trend line (large positive residual). Raw confidence
    # buries ORTHO (POPCAND raw higher); residualization removes the popularity component -> ORTHO rises.
    # Needs >=3 candidates with pop variance so OLS is non-degenerate.
    plant = [(A, 30, 1, 0.30), (B, 31, 10, 0.50), (Cc, 32, 100, 0.70),
             (POPCAND, 33, 5000, 0.90), (ORTHO, 34, 1, 0.85)]
    gr.rel_tail_freq = defaultdict(Counter)
    rules_r = []
    for (cand, rel, pop, conf) in plant:
        gr.out_adj_rel[rel][Hr] = [cand]
        rules_r.append(("L1F", rel, 0, conf, 50))
        gr.rel_tail_freq[99][cand] = pop
    acc_r = {99: rules_r}
    rkp, gp = build_conf_priors(acc_r)
    resid = resid_conf_score(gr, Hr, 99, rules_r, rkp, gp, 99)
    raw_pop = -math.log(1.0 - min(eb_conf("L1F", 0.90, 50, 99, rkp, gp, 99), 0.999))
    raw_ortho = -math.log(1.0 - min(eb_conf("L1F", 0.85, 50, 99, rkp, gp, 99), 0.999))
    assert raw_pop > raw_ortho, "D_RES setup broken: raw conf should favor POPCAND (%.3f vs %.3f)" % (raw_pop, raw_ortho)
    assert resid[ORTHO] > resid[POPCAND], "D_RES FAIL: residualization did not promote freq-orthogonal ORTHO (ORTHO=%.4f POPCAND=%.4f)" % (resid[ORTHO], resid[POPCAND])
    print("[selftest] D_RES PASS: raw(POP=%.3f>ORTHO=%.3f) -> resid(ORTHO=%.4f>POPCAND=%.4f)"
          % (raw_pop, raw_ortho, resid[ORTHO], resid[POPCAND]), flush=True)

    # ---- D_LEAK: SHUF_RELLABEL changes eb_conf; FREQ_LEAK == frequency ranking ----
    print("[selftest] D_LEAK: shuffled-relation prior changes eb_conf; FREQ_LEAK tracks frequency...", flush=True)
    acc_two = {99: [("L1F", 30, 0, 0.9, 5)], 88: [("L1F", 40, 0, 0.1, 5)]}
    rkp2, gp2 = build_conf_priors(acc_two)
    eb_true = eb_conf("L1F", 0.9, 5, 99, rkp2, gp2, 99)     # uses r3=99 prior (0.9)
    eb_shuf = eb_conf("L1F", 0.9, 5, 99, rkp2, gp2, 88)     # uses r3=88 prior (0.1) -> lower
    assert abs(eb_true - eb_shuf) > 1e-6, "D_LEAK FAIL: shuffled-relation prior did not change eb_conf (%.4f vs %.4f)" % (eb_true, eb_shuf)
    fl = freq_leak_score(gr, Hr, 99, rules_r)
    assert fl[POPCAND] > fl[ORTHO], "D_LEAK FAIL: FREQ_LEAK did not rank by frequency"
    print("[selftest] D_LEAK PASS: eb_true=%.4f != eb_shuf=%.4f (thin-support shrinks to relation prior); FREQ_LEAK ranks by freq"
          % (eb_true, eb_shuf), flush=True)

    # ---- D_TYPE: relation-type consistency separates gold from a structurally-identical wrong-type
    #      distractor; SHUF_TYPELABEL (wrong relation's type) does NOT preserve the separation ----
    print("[selftest] D_TYPE: type-consistency separates gold from wrong-type distractor...", flush=True)
    gt = _planted_graph()
    Ht, GOLDt, WRONGt = 1, 2, 3
    TARGET = 99
    # Build a train-like adjacency so build_type_compat derives real profiles. TARGET's typical tails
    # are 'country-like' entities that are tails of relations 200,201. GOLDt shares that profile;
    # WRONGt is a 'person-like' entity (tail of relations 210,211) -- structurally reached the same way
    # but the WRONG type. Seed several exemplar country-tails of TARGET so W[TARGET] favors 200/201.
    for i in range(20, 40):                       # 20 exemplar country-tails of TARGET
        gt.out_adj_rel[TARGET][1000 + i].append(i)
        gt.out_adj_rel[200][2000 + i].append(i)   # each is a tail of 200 and 201 (country profile)
        gt.out_adj_rel[201][2100 + i].append(i)
    gt.out_adj_rel[200][3000].append(GOLDt)       # GOLDt has the country profile (tail of 200,201)
    gt.out_adj_rel[201][3001].append(GOLDt)
    gt.out_adj_rel[210][3002].append(WRONGt)      # WRONGt has a person profile (tail of 210,211)
    gt.out_adj_rel[211][3003].append(WRONGt)
    Wt, etr = build_type_compat(gt)
    ts_scores = type_rank_score(Wt, etr, TARGET, [GOLDt, WRONGt])
    assert ts_scores[GOLDt] > ts_scores[WRONGt], "D_TYPE FAIL: type-consistency did not favor correct-type gold (GOLD=%.4f WRONG=%.4f)" % (ts_scores[GOLDt], ts_scores[WRONGt])
    # SHUF control: score against a DIFFERENT relation's expected type (210 = person) -> should NOT
    # favor the country-typed gold (separation collapses / reverses)
    ts_shuf = type_rank_score(Wt, etr, 210, [GOLDt, WRONGt])
    shuf_sep = ts_shuf[GOLDt] - ts_shuf[WRONGt]
    true_sep = ts_scores[GOLDt] - ts_scores[WRONGt]
    assert shuf_sep < true_sep, "D_TYPE FAIL: shuffled type-label kept the separation (true_sep=%.4f shuf_sep=%.4f) -> not type-specific" % (true_sep, shuf_sep)
    print("[selftest] D_TYPE PASS: TYPE GOLD=%.4f>WRONG=%.4f (sep %.4f); shuf-relation sep=%.4f (type-specific)"
          % (ts_scores[GOLDt], ts_scores[WRONGt], true_sep, shuf_sep), flush=True)

    print("[selftest] ALL PASS (D_SYM, D_HD, D_RES, D_LEAK, D_TYPE)", flush=True)


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
    print("[config] anchor=%s mode=%s seeds=%s N_EVAL=%d N_DIM=%d MIN_SUPPORT=%d rankers=%s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_EVAL, N_DIM, MIN_SUPPORT, RANKERS), flush=True)

    train, valid, test = E._load_fb15k237()
    ent2i, rel2i = E.build_ids(train, valid, test)
    print("[data] train=%d valid=%d test=%d ent=%d rel=%d avgdeg=%.2f"
          % (len(train), len(valid), len(test), len(ent2i), len(rel2i),
             2.0 * len(train) / len(ent2i)), flush=True)

    # relation-type-consistency table (seed-independent; derived from train adjacency) -- built ONCE
    gd0 = E.Graph(train, ent2i, rel2i)
    W, ent_tailrels = build_type_compat(gd0)
    print("[type] built relation-type compat: rels=%d entities-with-profile=%d" % (len(W), len(ent_tailrels)), flush=True)

    per_seed = []
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")
    for si, seed in enumerate(SEEDS):
        ts = time.time()
        r = run_seed(train, valid, test, ent2i, rel2i, seed, W, ent_tailrels)
        per_seed.append(r)
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit_idx": si, "total_units": len(SEEDS),
                                "elapsed_s": time.time() - t0}) + "\n")
        lm = r["low_mid"]; lo = r["low"]
        print("[seed %d] LOW: POP=%.3f HD=%.3f TYPE=%.3f HD_TYPE=%.3f CAPPOP=%.3f FREQ_LEAK=%.3f | "
              "low+mid: POP=%.3f HD=%.3f TYPE=%.3f HD_TYPE=%.3f CAPPOP=%.3f FREQ_LEAK=%.3f RESID=%.3f "
              "SHUF_REL=%.3f SHUF_TYPE=%.3f SCR=%.3f | reach(lm)=%.3f leak_ok=%s arms_differ=%s rules=%d (%.1fs)"
              % (seed, lo["POP_h10"], lo["HD_RANK_h10"], lo["TYPE_RANK_h10"], lo["HD_TYPE_h10"],
                 lo["HD_TYPE_CAPPOP_h10"], lo["FREQ_LEAK_h10"],
                 lm["POP_h10"], lm["HD_RANK_h10"], lm["TYPE_RANK_h10"], lm["HD_TYPE_h10"],
                 lm["HD_TYPE_CAPPOP_h10"], lm["FREQ_LEAK_h10"], lm["RESID_CONF_h10"],
                 lm["SHUF_RELLABEL_h10"], lm["SHUF_TYPELABEL_h10"], lm["SCR_h10"], lm["reach"],
                 r["meta"]["sym_leak_ok"], r["meta"]["arms_differ"], r["meta"]["n_rules_dense"],
                 time.time() - ts), flush=True)

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
