"""
crux_engine_fb15k237_vsa_gt_v1 -- SUBSTRATE-NATIVE generate-and-test inference engine on FB15k-237.

WHY. The prior cell (gt_induction_fb15k237_dense_v1, VET'd) proved DENSITY IS NECESSARY and the
VERIFIER IS LOAD-BEARING, but it was pure SYMBOLIC AMIE (L1+L2 confidence rules, ZERO substrate
primitives = a construction-proof), and it LOST to the per-relation-frequency prior:
  prior GT_DENSE (symbolic L1+L2): h@1=0.171 h@10=0.288 mrr=0.212   MEASURED@data/exp_gt_induction_fb15k237_dense_v1_fullpreview/metrics.json:per_seed
  POP_RELFREQ (bar):               h@1=0.262 h@10=0.487 mrr=0.338    MEASURED@same
  reachability ceiling (L<=2):     0.514                            MEASURED@same
So "generate-and-test infers structure beyond frequency" is NOT yet shown, and it was not our substrate.

THIS cell adds the two things that make it a real substrate-inference CAPABILITY test:
  1. SUBSTRATE-NATIVE PROPOSE: candidate scoring uses OUR chain-grade FHRR bind/unbind compose operator
     (hdlab.binding.bind / unbind). Each relation r gets a unit-modulus FHRR vector R_r. A relational
     path r1;r2;...;rk composes by BINDING: V_path = bind(R_r1, R_r2, ..., R_rk) (elementwise complex
     mul; associative, distinct-per-composition). Per target head relation r3 we accumulate a
     confidence-weighted BUNDLE of the composed path-vectors that explain r3 edges on train:
        Prof_r3 = sum over accepted path-types p of conf(p->r3) * V_p        (a distributed rule store).
     At test (h, r3, ?), for each candidate tail c reachable by a path p from h, the substrate READOUT
     is the UNBIND resonance: score += Re< unbind(Prof_r3, R_r1), R_r2..k > == Re< V_p, Prof_r3 >/N.
     bind stores, unbind reads. This is the propose-and-verify abductive design (Rel-SAR family),
     adapted to our open-vocab FHRR bind/unbind. The primitive is LOAD-BEARING: BIND_UNBIND_ABLATED
     replaces bind with elementwise ADD (superpose, no composition distinctness) -> crosstalk floods
     -> must HURT. If ablation does not hurt, the substrate is not doing the work.
  2. STRUCTURE BEYOND FREQUENCY: richer than L1+L2 -- path composition up to L_MAX=3 (L3 raises the
     reach-ceiling above the prior 0.514) and confidence-weighted (not frequency-weighted) profiles,
     so the engine can in principle capture relational structure per-relation-frequency cannot.

  SCORING LEVERS (Director course-correction 2026-07-10 -- Step-1 lost because relation-GLOBAL path
  support/confidence IS the frequency statistic, so both prior VSA + symbolic arms collapsed toward
  POP_RELFREQ; beating frequency REQUIRES head-specificity + length-fairness + a rules-out signal):
    L1 HEAD-CONDITIONAL (make-or-break): score candidate c by THIS head h's grounded-path evidence --
       per-(h,c,path-type) grounding multiplicity mult_gain(m) weights the head-specific bundle read
       against the rule profile (NBFNet-flavored aggregation of the head's relation-paths). Frequency
       is head-independent; mult_gain(m)!=const is what makes the score head-specific. The graded VSA
       bind/unbind bundle is the natural soft aggregator hard symbolic rules cannot express.
    L2 HOP-NORMALIZED: positive rule weight = conf * hop_gain(len) so genuine 2-3-hop compositional
       chains are length-fair vs high-support 1-hop (the exact bias that sank Step-1).
    L3 NEGATIVE EVIDENCE: high-body/low-conf path-types form a NEGATIVE profile; candidates reachable
       only via such unreliable paths are DOWNWEIGHTED (score -= NEG_LAMBDA * neg-resonance) -- the
       "rules-out" signal rule-methods miss and GNNs exploit.
  NOTE (Rel-SAR): borrowed only the diverse-relation-representation + propose-verify idea; Rel-SAR is a
  Raven's-Matrices VSA reasoner, NOT ported to KG. The 3 levers above are the direct KG fix.

ARMS (pre-registered):
  SUBSTRATE_GT       -- FHRR bind/unbind propose + resonance verify + L<=3 rules (the candidate).
  POP_RELFREQ        -- per-relation tail frequency prior (THE bar; prior engine LOST to it).
  POP_DEGREE         -- global node-degree prior (weaker baseline).
  SYMBOLIC_GT        -- SAME path enumeration + support/confidence dict scoring, L<=3 (delta vs VSA;
                        the compose-fidelity comparator: VSA vs symbolic candidate recall).
  BIND_UNBIND_ABLATED-- SUBSTRATE_GT with bind replaced by elementwise ADD (must HURT; primitive load-bearing).
  BROKEN_VERIFIER    -- SAME generator reach, RANDOM per-entity scores (verifier ablated; must FAIL).
  RANDOM             -- uniform-random filtered rank (floor).

DECISION (pre-registered; RELATIVE to this run's own POP_RELFREQ arm -- robust to regime/N_EVAL):
  eps = 0.02 (META_RULE_L strict-above-floor margin).
  HARD_PASS(real substrate inference engine) =
       SUBSTRATE_GT.h@1  >= POP_RELFREQ.h@1  + eps   (structure beyond frequency, precision)
   AND SUBSTRATE_GT.mrr  >= POP_RELFREQ.mrr  + eps
   AND BIND_UNBIND_ABLATED.mrr <= 0.7 * SUBSTRATE_GT.mrr           (bind/unbind LOAD-BEARING)
   AND SUBSTRATE_GT.h@10 >= 1.5 * GT_SPARSE.h@10                   (density-contrast holds)
   AND BROKEN_VERIFIER.mrr <= 0.5 * SUBSTRATE_GT.mrr
       AND BROKEN_VERIFIER.h@1 <= 0.5 * SUBSTRATE_GT.h@1           (verifier load-bearing)
  HARD_FAIL =
       SUBSTRATE_GT.mrr <= POP_RELFREQ.mrr  OR SUBSTRATE_GT.h@1 <= POP_RELFREQ.h@1  (ties/loses freq)
    OR BIND_UNBIND_ABLATED.mrr >= 0.9 * SUBSTRATE_GT.mrr           (bind NOT load-bearing -> not substrate-native)
    OR BROKEN_VERIFIER.mrr > 0.7 * SUBSTRATE_GT.mrr                (verifier not load-bearing)
  else MIDDLE_BAND.
  A clean HARD_FAIL is VALUABLE: it says even substrate-native richer generate-and-test does not beat
  frequency priors on FB15k-237 -> the mechanism needs a deeper rethink before the grounded-core
  system is worth building.

PER-STAGE DIAGNOSTIC WATERFALL (localizes the weak link whether PASS or FAIL; per coordinator):
  1. candidate_recall (propose ceiling): fraction of held-out gold reachable by ANY path (pre-verify).
  2. compose_fidelity: vsa_recall@C vs sym_recall@C on the SAME held-out set. gap = sym - vsa. If
     vsa << sym, the substrate crosstalk/cleanup-noise (SNR ~ sqrt(N/M)) is eating candidates.
  3. verifier_lift: post-verify ranking MINUS pre-verify (raw path-count) ranking; + verifier
     precision@1 conditioned on gold-proposed (true-vs-false candidate separation).
  4. rank_quality_cond: mrr/h@1 over ONLY queries where gold was proposed (ranking loss isolated
     from proposal loss).
  5. info_ceiling_per_stratum: reach-ceiling per head-relation frequency tertile (honest reach; not
     overclaimed universal).

SELF-TEST discriminators (must FIRE): D1 planted 3-hop composition recovered by VSA bind (hits@1==1.0);
  D2 ABLATED (add-compose) fails on same planted via superposition catastrophe (bind load-bearing;
  tested at neg_lambda=0 to isolate the compose primitive from negative-evidence cleanup); D2b full
  lever-stack bind still recovers planted (levers do not break the mechanism); D3 broken verifier
  recovers nothing; D4 sparse (support-stripped) fails; D5 frequency-only world -> SUBSTRATE_GT does
  NOT beat POP_RELFREQ (saturation-vacuous / null guard: no false "beats frequency" without structure).

COMPUTE. Dominant cost = combinatorial forward path-enumeration (dict lookups; inherently
sequential-CPU). Vector ops are O(unique path-types) small-N (N<=2048) FHRR bind/dot, computed ONCE
per path-type (compose is edge-independent) and memoized -> a few thousand cheap complex ops per seed,
< 10s aggregate vector time. Class: mixed (sequential-CPU graph traversal + memoized small-N vector
readout, batched matmul where candidate stacks allow). No large matmul; GPU not required. CPU-friendly.

ASCII-only. write_metrics. RUN_MODE defaults to full (runner invokes with no argv).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash writer os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: rank-based KG-completion; no closed-form noise floor. discriminator_reachability via
#   ceiling (candidate_recall) > POP_RELFREQ.h@1 => h@1 beat is physically reachable.
# - baseline_in_band at smoke (POP_RELFREQ neither 0 nor 1)
# - discriminator survives scale: self-test (planted, scale-independent) fires the VSA-vs-ablated
#   discriminator; FULL is the canonical beat-frequency judge (smoke reports honestly, does not gate).
# - HARD_PASS strictly above floor + eps (META_RULE_L)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (per-seed units); verdict counts len(per_seed)
# - per-unit failure-class: outer try writes CELL_CRASHED (no bare except)
# - calibration_check: adaptive_with_discriminator_gate -- scoring levers add hop_gain(len), mult_gain(m),
#   NEG_LAMBDA=0.5, NEG_CONF_MAX=0.02 (principled defaults, NOT tuned on smoke); self-test D1/D2 verify
#   the bind-vs-add composition discriminator still fires (D1 bind=1.0, D2 add=0.0 at neg_lambda=0).
#   MIN_SUPPORT/MIN_CONF inherit prior VET'd cell.
# - all numbers in header tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@
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
from hdlab import binding  # OUR substrate primitive: bind (elementwise complex mul) / unbind (mul conj)

ANCHOR_NAME = "crux_engine_fb15k237_vsa_gt_v1"
FB_DIR = REPO / "data" / "fb15k237_testbed"

# ---- run mode / config -------------------------------------------------------
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Rule-mining / verifier params (calibration_check: default_ok_for_this_regime; inherit prior VET'd cell).
MIN_SUPPORT = 10          # verifier: min path-type support (groundings reaching gold)
MIN_CONF = 0.05           # verifier: min path-type confidence (support / body)
L_MAX = 3                 # path composition depth (L1 direct-equiv, L2, L3) -- richer than prior L1+L2
SPARSE_TARGET_AVGDEG = 3.0
RECALL_C = 10             # candidate-recall @ C for compose-fidelity waterfall

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 1024              # FHRR vector dimension
    N_EVAL = 300             # subsample test queries
    TOP_K_RELS = 40          # restrict to most-frequent relations to bound wall
    PROFILE_EDGES_PER_REL = 200
    HUB_CAP = 20000
    BRANCH_CAP = 20          # max edges expanded per node during path enumeration
    PATH_CAP = 400           # max forward paths recorded per source node
    MIN_SUPPORT = 3
else:
    SEEDS = [7, 17, 23]
    N_DIM = 2048
    N_EVAL = 3000
    TOP_K_RELS = 0           # 0 = all relations
    PROFILE_EDGES_PER_REL = 1000
    HUB_CAP = 60000
    BRANCH_CAP = 30
    PATH_CAP = 800

HITS_KS = (1, 10)
EPS = 0.02                    # META_RULE_L strict-above-floor margin for beat-frequency gate

# ---- scoring levers (Director course-correction: BEAT frequency, not just richer rules) ----
# Step-1 lost because relation-GLOBAL path-rule support/confidence IS the frequency statistic (both
# the old VSA and symbolic arms scored candidates by conf(rtup->r3) alone, head-independent, so they
# collapsed toward POP_RELFREQ). Three levers make the verifier head-specific + length-fair + able to
# rule-out (NBFNet-flavored aggregation; graded VSA bind/unbind is the natural soft aggregator):
#   L1 HEAD-CONDITIONAL: score c by THIS head h's grounded-path evidence to c (grounding multiplicity
#      per composed path-type), not relation-global support. Frequency is relation-global; beating it
#      REQUIRES head-specificity. mult_gain(m) weights per-(h,c,rtup) grounding count (diminishing).
#   L2 HOP-NORMALIZED: positive rule weight = conf * hop_gain(len) so genuine 2-3-hop compositional
#      chains are not drowned by high-support 1-hop (the exact bias that sank Step-1).
#   L3 NEGATIVE EVIDENCE: high-body/low-conf path-types (reach many candidates, rarely the gold) form
#      a NEGATIVE profile; candidates reachable only via such unreliable paths are DOWNWEIGHTED
#      (the "rules-out" signal rule-methods miss and GNNs exploit).
HOP_GAIN_MODE = "linear"     # L2: hop_gain(L) = L  (L1->1, L2->2, L3->3)
NEG_LAMBDA = 0.5             # L3: negative-evidence penalty weight
NEG_CONF_MAX = 0.02          # L3: path-type is a negative (rules-out) pattern if conf<=this & body>=min_support


def hop_gain(L):
    """L2 hop-normalization: linear length boost so multi-hop chains are length-fair vs 1-hop."""
    return float(L)


def mult_gain(m):
    """L1 head-conditional grounding-multiplicity gain (diminishing). m=1 -> 1.0; more grounded paths
    from THIS head to the candidate -> larger (log) weight. g(m)!=const is what makes score head-specific."""
    return (1.0 + math.log(m)) if m > 0 else 0.0


# ============================ IO ==============================================
def _load_triples(path):
    tr = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) != 3:
                continue
            tr.append((p[0], p[1], p[2]))
    return tr


FB_BASE_URL = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/"
FB_EXPECT = {"train.txt": 272115, "valid.txt": 17535, "test.txt": 20466}


def _ensure_data():
    """Provision FB15k-237 standard split into FB_DIR if absent (public mirror). Fail LOUD."""
    import urllib.request
    FB_DIR.mkdir(parents=True, exist_ok=True)
    for fn, expect_lines in FB_EXPECT.items():
        p = FB_DIR / fn
        if p.exists() and sum(1 for _ in open(p, "r", encoding="utf-8")) == expect_lines:
            continue
        url = FB_BASE_URL + fn
        print("[data] fetching %s -> %s" % (url, p), flush=True)
        urllib.request.urlretrieve(url, str(p))
        n = sum(1 for _ in open(p, "r", encoding="utf-8"))
        if n != expect_lines:
            raise RuntimeError("FB15k-237 %s line-count mismatch: got %d expected %d (bad download?)"
                               % (fn, n, expect_lines))


def _load_fb15k237():
    _ensure_data()
    return (_load_triples(FB_DIR / "train.txt"),
            _load_triples(FB_DIR / "valid.txt"),
            _load_triples(FB_DIR / "test.txt"))


# ============================ graph index =====================================
class Graph:
    """Integer-id relational graph index built from a train-triple list."""
    def __init__(self, triples, ent2i, rel2i):
        self.ent2i = ent2i
        self.rel2i = rel2i
        self.n_ent = len(ent2i)
        self.n_rel = len(rel2i)
        self.out_by_node = defaultdict(list)       # b -> [(r,c)]  edges OUT of b
        self.out_adj_rel = defaultdict(lambda: defaultdict(list))  # r -> h -> [t]
        self.rel_tail_freq = defaultdict(Counter)  # r -> Counter(tail)
        self.node_degree = Counter()               # e -> global in+out degree (task baseline)
        self.rel_edge_count = Counter()            # r -> #edges
        for (h, r, t) in triples:
            hi, ri, ti = ent2i[h], rel2i[r], ent2i[t]
            self.out_by_node[hi].append((ri, ti))
            self.out_adj_rel[ri][hi].append(ti)
            self.rel_tail_freq[ri][ti] += 1
            self.rel_edge_count[ri] += 1
            self.node_degree[hi] += 1
            self.node_degree[ti] += 1


def build_ids(train, valid, test):
    ent2i, rel2i = {}, {}
    for tr in (train, valid, test):
        for (h, r, t) in tr:
            if h not in ent2i: ent2i[h] = len(ent2i)
            if t not in ent2i: ent2i[t] = len(ent2i)
            if r not in rel2i: rel2i[r] = len(rel2i)
    return ent2i, rel2i


# ============================ path enumeration ================================
def forward_paths(g, h, l_max, branch_cap, path_cap, excl_edge=None):
    """Enumerate forward relational paths from node h, up to length l_max.

    Returns list of (rel_tuple, terminal_c). Paths of ALL lengths 1..l_max are recorded.
    excl_edge = (h0, r0, t0): skip that exact edge at the FIRST hop (leave-one-out for the
    target edge during profile building). Never returns to the source h. Bounded by branch_cap
    (edges expanded per node) and path_cap (total paths recorded).
    """
    out = []
    # frontier of (node, rel_tuple). depth 0 = source.
    frontier = [(h, ())]
    for depth in range(l_max):
        nxt = []
        for (node, rtup) in frontier:
            edges = g.out_by_node.get(node, ())
            if not edges:
                continue
            nb = 0
            for (r, c) in edges:
                if nb >= branch_cap:
                    break
                if depth == 0 and excl_edge is not None and \
                        node == excl_edge[0] and r == excl_edge[1] and c == excl_edge[2]:
                    continue
                if c == h:
                    continue
                nb += 1
                new_tup = rtup + (r,)
                out.append((new_tup, c))
                if len(out) >= path_cap:
                    return out
                if depth + 1 < l_max:
                    nxt.append((c, new_tup))
        frontier = nxt
        if not frontier:
            break
    return out


# ============================ FHRR substrate layer ============================
def make_rel_vectors(n_rel, n_dim, seed):
    """n_rel unit-modulus FHRR vectors (complex64). Random phases; near-orthogonal."""
    gtor = torch.Generator().manual_seed(seed * 100003 + 11)
    theta = torch.rand(n_rel, n_dim, generator=gtor) * (2.0 * math.pi)
    return torch.polar(torch.ones(n_rel, n_dim), theta).to(torch.complex64)  # (n_rel, N)


class ComposeCache:
    """Memoize composed path-vectors. op='bind' (FHRR bind, LOAD-BEARING) or 'add' (ablation)."""
    def __init__(self, R, op):
        self.R = R
        self.op = op
        self._cache = {}

    def get(self, rtup):
        v = self._cache.get(rtup)
        if v is not None:
            return v
        v = self.R[rtup[0]].clone()
        for r in rtup[1:]:
            if self.op == "bind":
                v = binding.bind(v, self.R[r])        # OUR substrate primitive (elementwise complex mul)
            else:
                v = v + self.R[r]                     # ABLATION: superpose, no composition distinctness
        self._cache[rtup] = v
        return v


def resonance(v, prof, n_dim):
    """UNBIND readout: Re< v, prof >/N. For unitary a: Re<prof, bind(a,b)> == Re<unbind(prof,a), b>,
    so the dot-product resonance IS the substrate unbind-and-cleanup readout."""
    return float(torch.vdot(prof, v).real) / n_dim


# ============================ model build =====================================
def build_models(g, target_rels, R, n_dim, min_support, min_conf,
                 profile_edges_per_rel, l_max, branch_cap, path_cap, seed):
    """Mine path-type support/body over sampled train edges; build symbolic conf + FHRR/ADD profiles.

    Returns dict per head r3:
      conf[r3][rtup]          -- symbolic confidence (support/body), support>=min_support & conf>=min_conf
      prof_bind[r3]           -- FHRR POSITIVE bundle: sum (conf*hop_gain(len)) * bind-compose(rtup)  (L2)
      prof_add[r3]            -- ADD positive bundle (BIND_UNBIND_ABLATED; bind->add swap)
      prof_neg_bind[r3]       -- FHRR NEGATIVE bundle: sum (1-conf) * bind-compose(rtup) over high-body
                                 low-conf path-types (L3 rules-out signal)
      prof_neg_add[r3]        -- ADD negative bundle (ablation-matched)
      allpat_support[r3]      -- set of rtup with support>=1 (pre-verifier reach; ceiling + BROKEN reach)
    Plus caches cc_bind / cc_add (compose memo) reused at test.
    """
    rng = random.Random(seed * 7 + 3)
    cc_bind = ComposeCache(R, "bind")
    cc_add = ComposeCache(R, "add")

    support = defaultdict(Counter)   # r3 -> Counter(rtup)  paths reaching gold t
    body = defaultdict(Counter)      # r3 -> Counter(rtup)  paths reaching ANY c
    allpat = defaultdict(set)        # r3 -> {rtup} support>=1

    _t_mine = time.time()
    for _ri, r3 in enumerate(target_rels):
        if len(target_rels) >= 50 and _ri % 50 == 0:
            print("[build] mining rel %d/%d (%.1fs)" % (_ri, len(target_rels), time.time() - _t_mine), flush=True)
        ht = g.out_adj_rel.get(r3, {})
        edges = [(h, t) for h, ts in ht.items() for t in ts]
        if not edges:
            continue
        if len(edges) > profile_edges_per_rel:
            edges = rng.sample(edges, profile_edges_per_rel)
        for (h, t) in edges:
            paths = forward_paths(g, h, l_max, branch_cap, path_cap, excl_edge=(h, r3, t))
            seen_rtup_c = set()
            for (rtup, c) in paths:
                key = (rtup, c)
                if key in seen_rtup_c:
                    continue
                seen_rtup_c.add(key)
                body[r3][rtup] += 1
                if c == t:
                    support[r3][rtup] += 1
                    allpat[r3].add(rtup)

    conf = defaultdict(dict)
    prof_bind, prof_add = {}, {}
    prof_neg_bind, prof_neg_add = {}, {}
    for r3 in target_rels:
        pb = torch.zeros(n_dim, dtype=torch.complex64)
        pa = torch.zeros(n_dim, dtype=torch.complex64)
        pnb = torch.zeros(n_dim, dtype=torch.complex64)
        pna = torch.zeros(n_dim, dtype=torch.complex64)
        any_rule = False
        # POSITIVE rules (hop-normalized weight, L2): reliable path-types reaching gold.
        for rtup, s in support[r3].items():
            b = body[r3].get(rtup, 0)
            if b <= 0:
                continue
            cf = s / b
            if s >= min_support and cf >= min_conf:
                w = cf * hop_gain(len(rtup))          # L2 hop-normalization
                conf[r3][rtup] = cf
                pb = pb + w * cc_bind.get(rtup)
                pa = pa + w * cc_add.get(rtup)
                any_rule = True
        # NEGATIVE rules (L3): high-body low-conf path-types (reach many candidates, rarely gold).
        for rtup, b in body[r3].items():
            if b < min_support:
                continue
            cf = support[r3].get(rtup, 0) / b
            if cf <= NEG_CONF_MAX:
                nw = 1.0 - cf                         # unreliability weight (~1 for pure distractors)
                pnb = pnb + nw * cc_bind.get(rtup)
                pna = pna + nw * cc_add.get(rtup)
        if any_rule:
            prof_bind[r3] = pb
            prof_add[r3] = pa
            prof_neg_bind[r3] = pnb
            prof_neg_add[r3] = pna
    return conf, prof_bind, prof_add, prof_neg_bind, prof_neg_add, allpat, cc_bind, cc_add


# ============================ scoring / propose ===============================
def _noisy_or(vals):
    pn = 1.0
    for v in vals:
        pn *= (1.0 - v)
    return 1.0 - pn


def propose_candidates(g, h, r3, l_max, branch_cap, path_cap):
    """Enumerate forward paths from h; return cand -> {rtups:set, ground:int, rtup_counts:Counter}.
    rtup_counts[(r1,..)] = # of distinct grounded instances of that path-type from THIS head h to c
    (the head-conditional grounding multiplicity used by L1 head-conditional scoring)."""
    cand = {}
    for (rtup, c) in forward_paths(g, h, l_max, branch_cap, path_cap):
        d = cand.get(c)
        if d is None:
            d = {"rtups": set(), "ground": 0, "rtup_counts": Counter()}
            cand[c] = d
        d["rtups"].add(rtup)
        d["rtup_counts"][rtup] += 1     # L1: head-conditional grounding multiplicity
        d["ground"] += 1
    return cand


def score_vsa(cand, r3, prof_pos, prof_neg, cc, n_dim, reso_memo, neg_lambda=None):
    """SUBSTRATE_GT / ABLATED head-conditional score.

    For each candidate c reached from head h, aggregate its grounded path-types weighted by
    head-conditional grounding multiplicity mult_gain(m) (L1), read against the hop-normalized
    POSITIVE rule profile (L2) minus NEG_LAMBDA * the NEGATIVE rules-out profile (L3):
        score(c) = sum_rtup  mult_gain(m_{h,c,rtup}) * ( res(V_rtup, Prof_pos) - NEG_LAMBDA*res(V_rtup, Prof_neg) )
    The per-(h,c,rtup) multiplicity m is what makes this HEAD-SPECIFIC (frequency is head-independent).
    resonance(V_rtup, Prof) is the FHRR unbind-and-cleanup readout; bind is load-bearing (add-ablation
    shares composition factors -> crosstalk floods the readout). reso_memo caches (res_pos,res_neg) per
    (r3,rtup) since compose+resonance is head-independent; the head-conditional part is mult_gain(m)."""
    lam = NEG_LAMBDA if neg_lambda is None else neg_lambda
    pp = prof_pos.get(r3)
    if pp is None:
        return {}
    pn = prof_neg.get(r3)
    out = {}
    for c, d in cand.items():
        s = 0.0
        for rtup, m in d["rtup_counts"].items():
            key = (r3, rtup)
            rv = reso_memo.get(key)
            if rv is None:
                v = cc.get(rtup)
                rpos = resonance(v, pp, n_dim)
                rneg = resonance(v, pn, n_dim) if pn is not None else 0.0
                rv = (rpos, rneg)
                reso_memo[key] = rv
            g = mult_gain(m)                          # L1 head-conditional weight
            s += g * (rv[0] - lam * rv[1])            # L3 negative-evidence subtraction
        out[c] = s
    return out


def score_symbolic(cand, r3, conf):
    """SYMBOLIC_GT score: noisy-OR of path-type confidences over distinct rtups per cand."""
    cmap = conf.get(r3, {})
    out = {}
    for c, d in cand.items():
        vals = [cmap[rt] for rt in d["rtups"] if rt in cmap]
        out[c] = _noisy_or(vals) if vals else 0.0
    return out


def score_precount(cand):
    """Pre-verify score: raw path-count (structural popularity) -- verifier-lift baseline."""
    return {c: float(d["ground"]) for c, d in cand.items()}


def score_broken(cand, ent_rand):
    """BROKEN_VERIFIER: same reach, random per-entity score (verifier ablated)."""
    return {c: ent_rand[c] for c in cand.keys()}


# ============================ rank helpers ====================================
def strict_rank(scores, gold, filter_set, rng):
    """Filtered STRICT rank of gold among PROPOSED candidates. None if gold not proposed."""
    if gold not in scores:
        return None
    g_score = scores[gold]
    higher = ties = 0
    for c, sc in scores.items():
        if c == gold or c in filter_set:
            continue
        if sc > g_score:
            higher += 1
        elif sc == g_score:
            ties += 1
    return higher + 1 + rng.randint(0, ties)


def pop_rank(pop_counter, gold, filter_set, rng, n_ent):
    """Filtered rank of gold by a popularity counter (all entities ranked)."""
    g_pop = pop_counter.get(gold, 0)
    higher = ties = 0
    for c, p in pop_counter.items():
        if c == gold or c in filter_set:
            continue
        if p > g_pop:
            higher += 1
        elif p == g_pop:
            ties += 1
    if g_pop == 0:
        zero_block = n_ent - len(pop_counter)
        ties += max(0, zero_block - 1)
    return higher + 1 + rng.randint(0, ties)


def random_rank(gold, filter_set, rng, n_ent):
    pool = n_ent - len(filter_set) - 1
    if pool <= 0:
        return 1
    return rng.randint(1, pool + 1)


def topc_has_gold(scores, gold, filter_set, c):
    """True if gold is within top-c by score (filtered). For candidate-recall@C."""
    if gold not in scores:
        return False
    g_score = scores[gold]
    higher = 0
    for cc_, sc in scores.items():
        if cc_ == gold or cc_ in filter_set:
            continue
        if sc > g_score:
            higher += 1
            if higher >= c:
                return False
    return True


# ============================ evaluation ======================================
def eval_arm(rank_fn, test_queries, known_tails, arm_label=None):
    """rank_fn(h, r, gold, filt, rng) -> rank or None. Returns metrics + conditional (proposed-only)."""
    h1 = h10 = 0
    rr = 0.0
    n_prop = 0
    ch1 = 0
    crr = 0.0
    n = len(test_queries)
    rng = random.Random(12345)
    _t_ev = time.time()
    for _qi, (h, r, gold) in enumerate(test_queries):
        if arm_label is not None and n >= 1000 and _qi % 1000 == 0 and _qi > 0:
            print("[eval %s] q %d/%d (%.1fs)" % (arm_label, _qi, n, time.time() - _t_ev), flush=True)
        filt = known_tails.get((h, r), set()) - {gold}
        rank = rank_fn(h, r, gold, filt, rng)
        if rank is None:
            continue
        n_prop += 1
        if rank <= 1:
            h1 += 1; ch1 += 1
        if rank <= 10:
            h10 += 1
        rr += 1.0 / rank
        crr += 1.0 / rank
    cond = {"n_proposed": n_prop,
            "cond_hits@1": (ch1 / n_prop) if n_prop else 0.0,
            "cond_mrr": (crr / n_prop) if n_prop else 0.0}
    return {"hits@1": h1 / n, "hits@10": h10 / n, "mrr": rr / n, "n": n, **cond}


def eval_arm_stratified(rank_fn, test_queries, known_tails, strat_of_gold, strat_names):
    """Per-stratum h@1/mrr for a rank_fn. strat_of_gold: gold_node -> stratum-name.

    Ranks ALL entities (rank_fn returns a rank even when gold not proposed via POP/None handling):
    a None rank (gold not proposed by a strict GT arm) counts as a miss (contributes 0), matching
    the aggregate eval_arm convention so per-stratum and aggregate are comparable.
    """
    acc = {s: {"h1": 0, "rr": 0.0, "n": 0} for s in strat_names}
    rng = random.Random(12345)
    for (h, r, gold) in test_queries:
        s = strat_of_gold.get(gold)
        if s is None:
            continue
        acc[s]["n"] += 1
        filt = known_tails.get((h, r), set()) - {gold}
        rank = rank_fn(h, r, gold, filt, rng)
        if rank is None:
            continue
        if rank <= 1:
            acc[s]["h1"] += 1
        acc[s]["rr"] += 1.0 / rank
    return {s: {"hits@1": (acc[s]["h1"] / acc[s]["n"]) if acc[s]["n"] else 0.0,
                "mrr": (acc[s]["rr"] / acc[s]["n"]) if acc[s]["n"] else 0.0,
                "n": acc[s]["n"]} for s in strat_names}


# ============================ sparse downsample ===============================
def downsample(train, target_avgdeg, ent2i, seed):
    n_ent = len(ent2i)
    keep_e = int(target_avgdeg * n_ent / 2.0)
    rng = random.Random(seed)
    if keep_e >= len(train):
        return list(train)
    idx = list(range(len(train)))
    rng.shuffle(idx)
    keep = set(idx[:keep_e])
    return [train[i] for i in keep]


# ============================ per-seed ========================================
def run_seed(train, valid, test, ent2i, rel2i, seed):
    rng = random.Random(seed)
    n_ent = len(ent2i)
    R = make_rel_vectors(len(rel2i), N_DIM, seed)

    rel_freq = Counter()
    for (h, r, t) in train:
        rel_freq[rel2i[r]] += 1
    if TOP_K_RELS and TOP_K_RELS < len(rel2i):
        target_rels = [r for r, _ in rel_freq.most_common(TOP_K_RELS)]
    else:
        target_rels = list(rel2i.values())
    target_set = set(target_rels)

    gd = Graph(train, ent2i, rel2i)

    known = defaultdict(set)
    for tr in (train, valid, test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])

    tq_all = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in test if rel2i[r] in target_set]
    rng.shuffle(tq_all)
    tq = tq_all[:N_EVAL]

    # ---- build models on dense ----
    conf, prof_bind, prof_add, prof_neg_bind, prof_neg_add, allpat, cc_bind, cc_add = build_models(
        gd, target_rels, R, N_DIM, MIN_SUPPORT, MIN_CONF,
        PROFILE_EDGES_PER_REL, L_MAX, BRANCH_CAP, PATH_CAP, seed)
    n_rules = sum(len(v) for v in conf.values())

    reso_memo = {}
    reso_memo_abl = {}

    # per-query candidate cache (compute once; all VSA/SYM/PRE arms share)
    cand_cache = {}
    def get_cand(h, r3):
        key = (h, r3)
        d = cand_cache.get(key)
        if d is None:
            d = propose_candidates(gd, h, r3, L_MAX, BRANCH_CAP, PATH_CAP)
            cand_cache[key] = d
        return d

    # ---- SUBSTRATE_GT (FHRR bind/unbind resonance; head-conditional + hop-norm + neg-evidence) ----
    def substrate_rank(h, r, gold, filt, rr):
        sc = score_vsa(get_cand(h, r), r, prof_bind, prof_neg_bind, cc_bind, N_DIM, reso_memo)
        return strict_rank(sc, gold, filt, rr)
    m_sub = eval_arm(substrate_rank, tq, known, arm_label="SUBSTRATE_GT")

    # ---- BIND_UNBIND_ABLATED (add-compose) ----
    def ablated_rank(h, r, gold, filt, rr):
        sc = score_vsa(get_cand(h, r), r, prof_add, prof_neg_add, cc_add, N_DIM, reso_memo_abl)
        return strict_rank(sc, gold, filt, rr)
    m_abl = eval_arm(ablated_rank, tq, known)

    # ---- SYMBOLIC_GT (confidence dict, same enumeration) ----
    def symbolic_rank(h, r, gold, filt, rr):
        sc = score_symbolic(get_cand(h, r), r, conf)
        return strict_rank(sc, gold, filt, rr)
    m_sym = eval_arm(symbolic_rank, tq, known)

    # ---- BROKEN_VERIFIER (reach, random score) ----
    brng = random.Random(seed * 991 + 7)
    ent_rand = [brng.random() for _ in range(n_ent)]
    def broken_rank(h, r, gold, filt, rr):
        sc = score_broken(get_cand(h, r), ent_rand)
        return strict_rank(sc, gold, filt, rr)
    m_broken = eval_arm(broken_rank, tq, known)

    # ---- POP_RELFREQ (bar) / POP_DEGREE / RANDOM ----
    def pop_relfreq_rank(h, r, gold, filt, rr):
        return pop_rank(gd.rel_tail_freq.get(r, Counter()), gold, filt, rr, n_ent)
    m_pop_rf = eval_arm(pop_relfreq_rank, tq, known)

    def pop_deg_rank(h, r, gold, filt, rr):
        return pop_rank(gd.node_degree, gold, filt, rr, n_ent)
    m_pop_deg = eval_arm(pop_deg_rank, tq, known)

    def rand_rank(h, r, gold, filt, rr):
        return random_rank(gold, filt, rr, n_ent)
    m_random = eval_arm(rand_rank, tq, known)

    # ---- GT_SPARSE (density contrast; SUBSTRATE mechanism on downsampled graph) ----
    train_sp = downsample(train, SPARSE_TARGET_AVGDEG, ent2i, seed)
    gs = Graph(train_sp, ent2i, rel2i)
    conf_s, prof_bind_s, _pa_s, prof_neg_bind_s, _pna_s, _ap_s, cc_bind_s, _cc_add_s = build_models(
        gs, target_rels, R, N_DIM, MIN_SUPPORT, MIN_CONF,
        PROFILE_EDGES_PER_REL, L_MAX, BRANCH_CAP, PATH_CAP, seed)
    reso_memo_s = {}
    cand_cache_s = {}
    def get_cand_s(h, r3):
        key = (h, r3)
        d = cand_cache_s.get(key)
        if d is None:
            d = propose_candidates(gs, h, r3, L_MAX, BRANCH_CAP, PATH_CAP)
            cand_cache_s[key] = d
        return d
    def sparse_rank(h, r, gold, filt, rr):
        sc = score_vsa(get_cand_s(h, r), r, prof_bind_s, prof_neg_bind_s, cc_bind_s, N_DIM, reso_memo_s)
        return strict_rank(sc, gold, filt, rr)
    m_sparse = eval_arm(sparse_rank, tq, known)
    avgdeg_sp = 2.0 * len(train_sp) / n_ent

    # ============ DIAGNOSTIC WATERFALL ============
    # freq tertiles for stratum ceiling
    tr_rel_sorted = sorted(target_rels, key=lambda r: rel_freq.get(r, 0))
    third = max(1, len(tr_rel_sorted) // 3)
    strata = {"low_freq": set(tr_rel_sorted[:third]),
              "mid_freq": set(tr_rel_sorted[third:2 * third]),
              "high_freq": set(tr_rel_sorted[2 * third:])}
    ceil_hit = 0
    strat_tot = {k: 0 for k in strata}
    strat_hit = {k: 0 for k in strata}
    vsa_rC = vsa_r1 = sym_rC = sym_r1 = 0
    pre_rr = 0.0
    n_gold_prop = 0
    for (h, r, gold) in tq:
        filt = known.get((h, r), set()) - {gold}
        cand = get_cand(h, r)
        reachable = (gold in cand) and (gold not in filt)
        if reachable:
            ceil_hit += 1
        for sk, sset in strata.items():
            if r in sset:
                strat_tot[sk] += 1
                if reachable:
                    strat_hit[sk] += 1
        # compose-fidelity: top-C recall by VSA vs symbolic
        rrng = random.Random(999)
        sc_v = score_vsa(cand, r, prof_bind, prof_neg_bind, cc_bind, N_DIM, reso_memo)
        sc_s = score_symbolic(cand, r, conf)
        sc_p = score_precount(cand)
        if topc_has_gold(sc_v, gold, filt, RECALL_C): vsa_rC += 1
        if topc_has_gold(sc_v, gold, filt, 1): vsa_r1 += 1
        if topc_has_gold(sc_s, gold, filt, RECALL_C): sym_rC += 1
        if topc_has_gold(sc_s, gold, filt, 1): sym_r1 += 1
        # verifier-lift: pre-verify (path-count) MRR over proposed
        pr = strict_rank(sc_p, gold, filt, rrng)
        if pr is not None:
            n_gold_prop += 1
            pre_rr += 1.0 / pr
    nq = len(tq)
    ceiling = ceil_hit / nq
    pre_mrr = (pre_rr / n_gold_prop) if n_gold_prop else 0.0  # conditional pre-verify mrr
    waterfall = {
        "1_candidate_recall_ceiling": ceiling,
        "2_compose_fidelity": {
            "vsa_recall@%d" % RECALL_C: vsa_rC / nq, "sym_recall@%d" % RECALL_C: sym_rC / nq,
            "vsa_recall@1": vsa_r1 / nq, "sym_recall@1": sym_r1 / nq,
            "gap@%d_sym_minus_vsa" % RECALL_C: (sym_rC - vsa_rC) / nq,
            "gap@1_sym_minus_vsa": (sym_r1 - vsa_r1) / nq,
        },
        "3_verifier_lift": {
            "pre_verify_cond_mrr": pre_mrr,
            "vsa_post_verify_cond_mrr": m_sub["cond_mrr"],
            "sym_post_verify_cond_mrr": m_sym["cond_mrr"],
            "vsa_lift_over_pre": m_sub["cond_mrr"] - pre_mrr,
            "sym_lift_over_pre": m_sym["cond_mrr"] - pre_mrr,
            "vsa_precision@1_cond": m_sub["cond_hits@1"],
            "sym_precision@1_cond": m_sym["cond_hits@1"],
            "broken_precision@1_cond": m_broken["cond_hits@1"],
        },
        "4_rank_quality_cond": {
            "vsa_cond_mrr": m_sub["cond_mrr"], "vsa_cond_hits@1": m_sub["cond_hits@1"],
            "vsa_n_proposed": m_sub["n_proposed"],
            "sym_cond_mrr": m_sym["cond_mrr"], "sym_cond_hits@1": m_sym["cond_hits@1"],
        },
        "5_info_ceiling_per_stratum": {
            k: (strat_hit[k] / strat_tot[k] if strat_tot[k] else 0.0) for k in strata
        },
    }

    # ============ DEGREE/FREQUENCY-CONFOUND STRATIFICATION (tail-collapse detector) ============
    # Stratify test queries by GOLD-TAIL node degree into LOW/MID/HIGH tertiles; compare
    # SUBSTRATE_GT vs BOTH baselines (POP_RELFREQ, POP_DEGREE) per stratum. An aggregate win that
    # COLLAPSES on the LOW (rare) stratum is the tail-collapse artifact (winning on common items,
    # losing on rare ones) that reversed 4+ prior cells -> flagged HARD_FAIL_TAIL_COLLAPSE in verdict.
    gold_degs = sorted(gd.node_degree.get(g_, 0) for (_, _, g_) in tq)
    if gold_degs:
        q1 = gold_degs[len(gold_degs) // 3]
        q2 = gold_degs[2 * len(gold_degs) // 3]
    else:
        q1 = q2 = 0
    def _strat(node):
        dgr = gd.node_degree.get(node, 0)
        if dgr <= q1:
            return "low"
        if dgr <= q2:
            return "mid"
        return "high"
    strat_of_gold = {g_: _strat(g_) for (_, _, g_) in tq}
    strat_names = ("low", "mid", "high")
    ds_sub = eval_arm_stratified(substrate_rank, tq, known, strat_of_gold, strat_names)
    ds_pf = eval_arm_stratified(pop_relfreq_rank, tq, known, strat_of_gold, strat_names)
    ds_pd = eval_arm_stratified(pop_deg_rank, tq, known, strat_of_gold, strat_names)
    degree_stratified = {}
    for s in strat_names:
        degree_stratified[s] = {
            "n": ds_sub[s]["n"], "deg_tertile_bounds": [q1, q2],
            "SUBSTRATE_GT": {"hits@1": ds_sub[s]["hits@1"], "mrr": ds_sub[s]["mrr"]},
            "POP_RELFREQ": {"hits@1": ds_pf[s]["hits@1"], "mrr": ds_pf[s]["mrr"]},
            "POP_DEGREE": {"hits@1": ds_pd[s]["hits@1"], "mrr": ds_pd[s]["mrr"]},
            "margin_vs_relfreq": {"hits@1": ds_sub[s]["hits@1"] - ds_pf[s]["hits@1"],
                                  "mrr": ds_sub[s]["mrr"] - ds_pf[s]["mrr"]},
            "margin_vs_degree": {"hits@1": ds_sub[s]["hits@1"] - ds_pd[s]["hits@1"],
                                 "mrr": ds_sub[s]["mrr"] - ds_pd[s]["mrr"]},
        }

    return {
        "seed": seed,
        "n_ent": n_ent, "n_rel": len(rel2i),
        "n_train": len(train), "avgdeg_dense": 2.0 * len(train) / n_ent,
        "n_train_sparse": len(train_sp), "avgdeg_sparse": avgdeg_sp,
        "n_test_eval": nq, "n_rules": n_rules, "N_DIM": N_DIM,
        "ceiling": ceiling, "degree_stratified": degree_stratified,
        "SUBSTRATE_GT": m_sub, "BIND_UNBIND_ABLATED": m_abl, "SYMBOLIC_GT": m_sym,
        "POP_RELFREQ": m_pop_rf, "POP_DEGREE": m_pop_deg,
        "BROKEN_VERIFIER": m_broken, "RANDOM": m_random, "GT_SPARSE": m_sparse,
        "waterfall": waterfall,
    }


# ============================ verdict =========================================
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_verdict(per_seed):
    def agg(arm, k):
        return _mean([s[arm][k] for s in per_seed])
    sub1 = agg("SUBSTRATE_GT", "hits@1"); submrr = agg("SUBSTRATE_GT", "mrr"); sub10 = agg("SUBSTRATE_GT", "hits@10")
    abl_mrr = agg("BIND_UNBIND_ABLATED", "mrr")
    sym1 = agg("SYMBOLIC_GT", "hits@1"); symmrr = agg("SYMBOLIC_GT", "mrr"); sym10 = agg("SYMBOLIC_GT", "hits@10")
    pf1 = agg("POP_RELFREQ", "hits@1"); pfmrr = agg("POP_RELFREQ", "mrr"); pf10 = agg("POP_RELFREQ", "hits@10")
    b1 = agg("BROKEN_VERIFIER", "hits@1"); bmrr = agg("BROKEN_VERIFIER", "mrr")
    sp10 = agg("GT_SPARSE", "hits@10")
    ceil = _mean([s["ceiling"] for s in per_seed])

    beats_freq = (sub1 >= pf1 + EPS) and (submrr >= pfmrr + EPS)
    bind_loadbearing = (abl_mrr <= 0.7 * max(submrr, 1e-9))
    density_contrast = (sub10 >= 1.5 * max(sp10, 1e-9))
    broken_fails = (bmrr <= 0.5 * max(submrr, 1e-9)) and (b1 <= 0.5 * max(sub1, 1e-9))

    # ---- tail-collapse detector: beat-frequency bar must hold on LOW+MID (rare) strata ----
    def dstrat(stratum, arm, k):
        return _mean([s["degree_stratified"][stratum][arm][k] for s in per_seed])
    tail_collapse = False
    strat_detail = {}
    for stratum in ("low", "mid"):
        s_h1 = dstrat(stratum, "SUBSTRATE_GT", "hits@1"); s_mrr = dstrat(stratum, "SUBSTRATE_GT", "mrr")
        f_h1 = dstrat(stratum, "POP_RELFREQ", "hits@1"); f_mrr = dstrat(stratum, "POP_RELFREQ", "mrr")
        holds = (s_h1 >= f_h1 + EPS) and (s_mrr >= f_mrr + EPS)
        strat_detail[stratum] = {"sub_h1": s_h1, "sub_mrr": s_mrr, "rf_h1": f_h1, "rf_mrr": f_mrr,
                                 "beat_holds": holds}
        if not holds:
            tail_collapse = True
    # only meaningful as a FAIL when the aggregate would otherwise pass on frequency
    tail_collapse_fail = beats_freq and tail_collapse

    hard_pass = beats_freq and bind_loadbearing and density_contrast and broken_fails and (not tail_collapse)

    ties_freq = (submrr <= pfmrr) or (sub1 <= pf1)
    bind_not_loadbearing = (abl_mrr >= 0.9 * max(submrr, 1e-9))
    broken_infers = (bmrr > 0.7 * max(submrr, 1e-9))
    hard_fail = ties_freq or bind_not_loadbearing or broken_infers or tail_collapse_fail

    if hard_pass:
        v = "HARD_PASS"
    elif tail_collapse_fail:
        v = "HARD_FAIL_TAIL_COLLAPSE"
    elif hard_fail:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"

    msg = ("SUBSTRATE_GT h@1=%.3f mrr=%.3f h@10=%.3f | POP_RELFREQ h@1=%.3f mrr=%.3f h@10=%.3f | "
           "SYMBOLIC_GT h@1=%.3f mrr=%.3f | ABLATED mrr=%.3f (ratio=%.2f) | BROKEN mrr=%.3f | "
           "SPARSE h@10=%.3f | ceiling=%.3f || beats_freq=%s bind_loadbearing=%s density=%s "
           "broken_fails=%s tail_collapse=%s"
           % (sub1, submrr, sub10, pf1, pfmrr, pf10, sym1, symmrr, abl_mrr,
              abl_mrr / max(submrr, 1e-9), bmrr, sp10, ceil,
              beats_freq, bind_loadbearing, density_contrast, broken_fails, tail_collapse))
    gates = {
        "SUBSTRATE_GT_hits1": sub1, "SUBSTRATE_GT_mrr": submrr, "SUBSTRATE_GT_hits10": sub10,
        "POP_RELFREQ_hits1": pf1, "POP_RELFREQ_mrr": pfmrr, "POP_RELFREQ_hits10": pf10,
        "SYMBOLIC_GT_hits1": sym1, "SYMBOLIC_GT_mrr": symmrr,
        "ABLATED_mrr": abl_mrr, "ablated_ratio": abl_mrr / max(submrr, 1e-9),
        "BROKEN_mrr": bmrr, "GT_SPARSE_hits10": sp10, "ceiling": ceil,
        "beats_freq": beats_freq, "bind_loadbearing": bind_loadbearing,
        "density_contrast": density_contrast, "broken_fails": broken_fails,
        "tail_collapse": tail_collapse, "tail_collapse_fail": tail_collapse_fail,
        "strat_low_mid_detail": strat_detail,
    }
    return v, msg, gates


# ============================ self-test =======================================
def _build_planted(seed=0, with_support=True):
    """Planted 3-HOP composition (binding-problem demonstration; bind LOAD-BEARING):
        rBorn(A,city) & rCap(city,region) & rIn(region,country) => rNat(A,country).
    Distractor paths rVis_d(A,city') & rCap & rIn SHARE the 2-hop tail (rCap;rIn) with the gold path.
    Under FHRR bind the full composed path is orthogonal to gold's (distinct first factor) so the
    verifier separates them; under the ADD ablation the shared rCap;rIn components collide AND the
    negative-evidence profile (built from the unreliable rVis paths) penalizes gold itself via those
    same shared components -> add cannot recover -> bind is load-bearing. with_support=False strips
    rBorn (no positive path) -> D4 sparse must fail."""
    P, C, RG, K = 20, 20, 8, 12          # persons, cities, regions, countries
    N_DISTRACT = 6
    rr = random.Random(seed)
    triples = []
    ent = lambda k, i: k * 1000 + i
    city_region = {ci: ci % RG for ci in range(C)}
    region_country = {rg: rg % K for rg in range(RG)}
    for ci in range(C):
        triples.append((ent(1, ci), "rCap", ent(2, city_region[ci])))          # city -> region
    for rg in range(RG):
        triples.append((ent(2, rg), "rIn", ent(3, region_country[rg])))        # region -> country
    country_of_city = lambda ci: region_country[city_region[ci]]
    for pi in range(P):
        ci = pi % C
        if with_support:
            triples.append((ent(0, pi), "rBorn", ent(1, ci)))                  # person -> birth city
        # All N_DISTRACT visit-relations point at ONE decoy city (a wrong country). Under ADD the
        # N_DISTRACT distinct rVis_d;rCap;rIn path-types each share the rCap;rIn tail with the true rule
        # -> their partial resonances SUPERPOSE and outscore the gold's single full path (superposition
        # catastrophe). Under BIND each composed path is orthogonal to the true rule -> decoy ~0.
        decoy_city = (ci + C // 2) % C                                          # distinct from birth city
        for d in range(N_DISTRACT):
            triples.append((ent(0, pi), "rVis_%d" % d, ent(1, decoy_city)))    # person -> decoy city (noise)
    gold = [(ent(0, pi), "rNat", ent(3, country_of_city(pi % C))) for pi in range(P)]
    return triples, gold


def _eval_planted_vsa(triples, gold_train, gold_test, op, min_conf, min_support, neg_lambda=None):
    """Build FHRR (op='bind') or ADD (op='add') model on a planted graph; return hits@1 on held-out.
    neg_lambda=0.0 isolates the pure bind-vs-add COMPOSITION effect (negative-evidence off) so D2 tests
    whether the compose primitive itself is load-bearing, not whether neg-evidence cleans up add."""
    train_p = triples + gold_train
    ent2i, rel2i = build_ids(train_p, [], gold_test)
    g = Graph(train_p, ent2i, rel2i)
    R = make_rel_vectors(len(rel2i), 512, 0)
    trels = list(rel2i.values())
    conf, prof_bind, prof_add, prof_neg_bind, prof_neg_add, allpat, cc_bind, cc_add = build_models(
        g, trels, R, 512, min_support, min_conf, 1000, L_MAX, 40, 2000, 0)
    prof = prof_bind if op == "bind" else prof_add
    prof_neg = prof_neg_bind if op == "bind" else prof_neg_add
    cc = cc_bind if op == "bind" else cc_add
    reso = {}
    known = defaultdict(set)
    for tr in (train_p, gold_test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    tq = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in gold_test]
    def rk(h, r, gold, filt, rr):
        cand = propose_candidates(g, h, r, L_MAX, 40, 2000)
        sc = score_vsa(cand, r, prof, prof_neg, cc, 512, reso, neg_lambda=neg_lambda)
        return strict_rank(sc, gold, filt, rr)
    return eval_arm(rk, tq, known), (g, conf, allpat, ent2i, rel2i, known, tq)


def _selftest():
    print("[selftest] building planted graph...", flush=True)
    triples, gold = _build_planted(with_support=True)
    gtr, gte = gold[:10], gold[10:]

    # D1: SUBSTRATE_GT (FHRR bind) recovers planted 3-hop composition -> hits@1 == 1.0.
    # neg_lambda=0.0 isolates the COMPOSE primitive (no negative-evidence cleanup) so D1/D2 test whether
    # bind vs add is load-bearing for composition itself. On the clean planted graph add+neg-evidence can
    # mimic bind (neg-evidence cleans crosstalk); the pure-compose contrast is the honest primitive test.
    # At FULL/real scale the profiles bundle hundreds of path-types -> add-superposition crosstalk floods
    # -> the verdict's bind_loadbearing gate (abl_mrr <= 0.7*sub_mrr) is the real-scale empirical judge.
    m_bind, ctx = _eval_planted_vsa(triples, gtr, gte, "bind", min_conf=0.3, min_support=3, neg_lambda=0.0)
    assert m_bind["hits@1"] >= 0.99, "D1 FAIL: FHRR bind did not recover planted rule hits@1=%.3f" % m_bind["hits@1"]

    # D2: BIND_UNBIND_ABLATED (add-compose) FAILS on same planted (bind LOAD-BEARING for composition)
    m_add, _ = _eval_planted_vsa(triples, gtr, gte, "add", min_conf=0.3, min_support=3, neg_lambda=0.0)
    assert m_add["hits@1"] <= 0.5, "D2 FAIL: add-ablation still infers hits@1=%.3f (bind not load-bearing)" % m_add["hits@1"]

    # D2b: FULL-STACK sanity -- with head-conditional + hop-norm + negative-evidence ON, bind still
    # recovers the planted composition (levers do not break the working mechanism).
    m_bind_full, _ = _eval_planted_vsa(triples, gtr, gte, "bind", min_conf=0.3, min_support=3)
    assert m_bind_full["hits@1"] >= 0.99, "D2b FAIL: full-stack bind broke planted recovery hits@1=%.3f" % m_bind_full["hits@1"]

    # D3: BROKEN_VERIFIER (reach, random score) recovers nothing
    (g, conf, allpat, ent2i, rel2i, known, tq) = ctx
    brng = random.Random(1); ent_rand = [brng.random() for _ in range(len(ent2i))]
    def br(h, r, gold, filt, rr):
        cand = propose_candidates(g, h, r, L_MAX, 40, 2000)
        return strict_rank(score_broken(cand, ent_rand), gold, filt, rr)
    m_broken = eval_arm(br, tq, known)
    assert m_broken["hits@1"] <= 0.5, "D3 FAIL: broken verifier infers hits@1=%.3f" % m_broken["hits@1"]

    # D4: sparse (support-stripped) planted fails
    triples_sp, gold_sp = _build_planted(with_support=False)
    m_sp, _ = _eval_planted_vsa(triples_sp, gold_sp[:10], gold_sp[10:], "bind", min_conf=0.3, min_support=3, neg_lambda=0.0)
    assert m_sp["hits@1"] <= 0.5, "D4 FAIL: sparse planted still infers hits@1=%.3f" % m_sp["hits@1"]

    # D5: frequency-only world -> SUBSTRATE_GT does NOT beat POP_RELFREQ (null/saturation-vacuous guard)
    frng = random.Random(5)
    NE, POP = 60, [0, 1, 2, 3, 4]           # a few very-popular tails
    triples_f = []
    ent = lambda k, i: k * 1000 + i
    # target rF: tails drawn by fixed popularity; body relations = random noise uncorrelated to tail
    gold_f = []
    for hi in range(40):
        t = frng.choices(POP, weights=[16, 8, 4, 2, 1])[0]
        gold_f.append((ent(0, hi), "rF", ent(2, t)))
        for d in range(6):                   # random noise paths (no predictive composition)
            b = ent(1, frng.randrange(NE))
            triples_f.append((ent(0, hi), "rNoise_%d" % d, b))
            triples_f.append((b, "rNoise2_%d" % d, ent(2, frng.randrange(NE))))
    # also inject the popularity into train edges so POP_RELFREQ can learn it
    train_f = triples_f + gold_f[:20]
    test_f = gold_f[20:]
    ent2i_f, rel2i_f = build_ids(train_f, [], test_f)
    gf = Graph(train_f, ent2i_f, rel2i_f)
    Rf = make_rel_vectors(len(rel2i_f), 512, 0)
    conf_f, pb_f, pa_f, pnb_f, pna_f, ap_f, ccb_f, cca_f = build_models(
        gf, list(rel2i_f.values()), Rf, 512, 2, 0.0, 1000, L_MAX, 40, 2000, 0)
    known_f = defaultdict(set)
    for tr in (train_f, test_f):
        for (h, r, t) in tr:
            known_f[(ent2i_f[h], rel2i_f[r])].add(ent2i_f[t])
    tqf = [(ent2i_f[h], rel2i_f[r], ent2i_f[t]) for (h, r, t) in test_f]
    reso_f = {}
    def sub_f(h, r, gold, filt, rr):
        cand = propose_candidates(gf, h, r, L_MAX, 40, 2000)
        return strict_rank(score_vsa(cand, r, pb_f, pnb_f, ccb_f, 512, reso_f), gold, filt, rr)
    def pf_f(h, r, gold, filt, rr):
        return pop_rank(gf.rel_tail_freq.get(r, Counter()), gold, filt, rr, len(ent2i_f))
    ms = eval_arm(sub_f, tqf, known_f); mp = eval_arm(pf_f, tqf, known_f)
    assert ms["mrr"] <= mp["mrr"] + 0.05, \
        "D5 FAIL: SUBSTRATE_GT falsely beats freq in no-structure world sub_mrr=%.3f pop_mrr=%.3f" % (ms["mrr"], mp["mrr"])

    print("[selftest] PASS: D1 bind=%.2f | D2 add=%.2f | D3 broken=%.2f | D4 sparse=%.2f | "
          "D5 freq-world sub_mrr=%.3f pop_mrr=%.3f"
          % (m_bind["hits@1"], m_add["hits@1"], m_broken["hits@1"], m_sp["hits@1"],
             ms["mrr"], mp["mrr"]), flush=True)


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
def _arms_must_differ(arms_outputs):
    import hashlib
    digests = {}
    for name, out in arms_outputs.items():
        digests[name] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], \
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b)
    return digests


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, len(SEEDS))
    t0 = time.time()
    print("[config] anchor=%s mode=%s seeds=%s N_DIM=%d N_EVAL=%d TOP_K_RELS=%d L_MAX=%d MIN_SUPPORT=%d"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_EVAL, TOP_K_RELS, L_MAX, MIN_SUPPORT), flush=True)

    train, valid, test = _load_fb15k237()
    ent2i, rel2i = build_ids(train, valid, test)
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
        wf = r["waterfall"]
        print("[seed %d] SUB h@1=%.3f mrr=%.3f | POP_RF h@1=%.3f mrr=%.3f | SYM mrr=%.3f | "
              "ABL mrr=%.3f | BROKEN mrr=%.3f | SPARSE h@10=%.3f | ceil=%.3f | "
              "compose_gap@%d=%.3f (sym_r=%.3f vsa_r=%.3f) (%.1fs)"
              % (seed, r["SUBSTRATE_GT"]["hits@1"], r["SUBSTRATE_GT"]["mrr"],
                 r["POP_RELFREQ"]["hits@1"], r["POP_RELFREQ"]["mrr"], r["SYMBOLIC_GT"]["mrr"],
                 r["BIND_UNBIND_ABLATED"]["mrr"], r["BROKEN_VERIFIER"]["mrr"],
                 r["GT_SPARSE"]["hits@10"], r["ceiling"], RECALL_C,
                 wf["2_compose_fidelity"]["gap@%d_sym_minus_vsa" % RECALL_C],
                 wf["2_compose_fidelity"]["sym_recall@%d" % RECALL_C],
                 wf["2_compose_fidelity"]["vsa_recall@%d" % RECALL_C], time.time() - ts), flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF): use seed-0 per-arm metric dicts
    s0 = per_seed[0]
    _arms_must_differ({a: s0[a] for a in
                       ["SUBSTRATE_GT", "BIND_UNBIND_ABLATED", "SYMBOLIC_GT",
                        "POP_RELFREQ", "POP_DEGREE", "BROKEN_VERIFIER", "RANDOM", "GT_SPARSE"]})

    verdict, vmsg, gates = compute_verdict(per_seed)
    elapsed = time.time() - t0
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
               "summary": vmsg[:200], "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
               "arms_differ_verified": True, "elapsed_s": elapsed, "gates": gates,
               "per_seed": per_seed}
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
