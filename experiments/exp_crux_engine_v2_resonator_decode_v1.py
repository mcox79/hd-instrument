"""
crux_engine_v2_resonator_decode_v1 -- RESONATOR-NETWORK DECODE fix for the VET-confirmed weak link.

=============================== V2 BANNER (READ FIRST) ===============================
The v1 crux (crux_engine_fb15k237_vsa_gt_v1) HARD_FAILed. VET localized the leak precisely to the
COMPOSE decode: candidate-recall bled at the bundle readout --
  single-shot VSA vsa_recall@10 = 0.203  MEASURED@data/exp_crux_engine_fb15k237_vsa_gt_v1/metrics.json:per_seed[*].waterfall.2_compose_fidelity.vsa_recall@10 (mean 0.199/0.194/0.217)
  symbolic        sym_recall@10 = 0.491  MEASURED@same:sym_recall@10 (mean 0.492/0.491/0.488)
CONDITIONED ON RECALL the VSA rank was HEALTHY: cond_mrr 0.415 >= symbolic 0.377
  MEASURED@same:per_seed[*].SUBSTRATE_GT.cond_mrr vs SYMBOLIC_GT.cond_mrr.
So the ONLY thing to fix is the DECODE. Doubling N_DIM 1024->2048 ~doubled mrr (0.092->0.161)
  = a crosstalk-limited-compose signature. THIS cell swaps the single-shot unbind+resonance readout
  for a RESONATOR NETWORK (Frady, Kent, Olshausen, Sommer 2020, Neural Computation, "Resonator
  Networks 1" CITED; in-memory factorization Sebastian et al., Nature Nanotechnology 2023 CITED). The
  resonator ITERATIVELY factorizes the superposed rule bundle against the path-vector dictionary --
  matched-filter init, then Gram-deflation (reconstruct -> residual -> project-onto-codebook -> update
  with a non-negative cleanup) iterating to convergence -- so a candidate's grounded path-types are
  scored by crosstalk-REMOVED rule coefficients instead of a single crosstalk-laden dot product. A
  non-rule path-type (pure crosstalk under single-shot) gets coefficient ~0 under the resonator: that
  is the candidate-bleed the single-shot decode drops and the resonator recovers.

TWO-STAGE PRE-REGISTERED BARS (see compute_verdict; relative to THIS run's own arms -> regime-robust):
  STAGE-1 (the fix WORKS -- direct compose-crosstalk test; headline):
     RESONATOR res_recall@10  materially exceeds single-shot vsa_recall@10 (>= +0.10 margin)
       AND approaches symbolic (>= 0.75 * sym_recall@10).
  STAGE-2 (the ultimate bar -- knowledge/rank wall):
     RESONATOR_GT.h@1 >= POP_RELFREQ.h@1 + EPS  AND  RESONATOR_GT.mrr >= POP_RELFREQ.mrr + EPS.
  HARD_PASS   = STAGE1 and STAGE2 and load-bearing gates (bind, broken, resonator>single-shot).
  HARD_FAIL_A = resonator does NOT recover recall (res_recall@10 < vsa_recall@10 + 0.05): decode still
                lossy -> more iterations / bigger N_DIM / better codebook.
  HARD_FAIL_B = recall recovered (STAGE1) but still loses frequency (STAGE2 fails): the wall is
                elsewhere (rank/knowledge), a VALUABLE result -- the leak was not the whole story.
  else MIDDLE_BAND.
  Predicted-honest tension (flagged, NOT tuned): symbolic ITSELF loses to frequency
  (SYMBOLIC_GT h@1=0.156 mrr=0.186 < POP 0.262/0.338 MEASURED@v1), so recovering VSA *toward symbolic*
  may satisfy STAGE-1 yet trip HARD_FAIL_B. That is a real, informative outcome, not a cell defect.

COMPUTE / GPU. The resonator's per-relation iterative matmuls (dictionary D_r3 in C^{P x N} times the
  profile / coefficient vector, n_iter passes) run on CUDA when available (torch.cuda) -- codebook R,
  ComposeCache products, profiles, and resonator iterations all live on DEVICE. Graph path-enumeration
  stays CPU (inherently sequential dict traversal; justified). DEVICE + torch.cuda.is_available() are
  logged to metrics so the overnight_queue GPU FULL records device=cuda. (Local venv is torch+cpu:
  smoke runs device=cpu; GPU is exercised only on the remote runner -- confirmed at FULL by VET.)
======================================================================================

WHY (v1 context). The prior cell (gt_induction_fb15k237_dense_v1, VET'd) proved DENSITY IS NECESSARY and the
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

ANCHOR_NAME = "crux_engine_v2_resonator_decode_v1"
FB_DIR = REPO / "data" / "fb15k237_testbed"

# ---- DEVICE (GPU-heavy resonator; CUDA when available, else CPU for local smoke) -------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CUDA_AVAIL = bool(torch.cuda.is_available())

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
    N_DIM = 512              # FHRR vector dimension (small for seconds-scale local smoke)
    N_EVAL = 150             # subsample test queries
    TOP_K_RELS = 25          # restrict to most-frequent relations to bound wall
    PROFILE_EDGES_PER_REL = 120
    HUB_CAP = 20000
    BRANCH_CAP = 15          # max edges expanded per node during path enumeration
    PATH_CAP = 250           # max forward paths recorded per source node
    MIN_SUPPORT = 3
    RES_T_ITER = 12          # resonator deflation iterations (== max candidates recovered/restart)
    RES_N_RESTART = 8        # batched random restarts
    ENT_CAP = 4000           # cap entity codebook to entities in the smoke subgraph (bounds CPU wall)
    # env overrides for a full-N discriminator-preview smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option C)
    N_DIM = int(os.environ.get("HDLAB_PREVIEW_NDIM", N_DIM))
    N_EVAL = int(os.environ.get("HDLAB_PREVIEW_NEVAL", N_EVAL))
    RES_T_ITER = int(os.environ.get("HDLAB_PREVIEW_TITER", RES_T_ITER))
    RES_N_RESTART = int(os.environ.get("HDLAB_PREVIEW_RESTART", RES_N_RESTART))
else:
    SEEDS = [7, 17, 23]
    N_DIM = 2048
    N_EVAL = 3000
    TOP_K_RELS = 0           # 0 = all relations
    PROFILE_EDGES_PER_REL = 1000
    HUB_CAP = 60000
    BRANCH_CAP = 30
    PATH_CAP = 800
    RES_T_ITER = 15          # resonator deflation iterations (GPU FULL)
    RES_N_RESTART = 16       # batched random restarts (GPU-batched matmul over R)
    ENT_CAP = 0              # 0 = full 14541-entity codebook (the real N_DIM x N_entities cleanup)

# ---- entity resonator-recovery params (calibration_check: principled defaults, NOT tuned on smoke) ----
RES_K_REC = 0                # 0 => recover up to T_ITER items/restart; else cap recovered set size
RES_TAU = 0.4                # initialization-only dither amplitude (breaks limit cycles; Karunaratne 2024)
RES_REBIND_K = 2.5           # RESIDUAL RE-BIND GATE: count a recovery only if sim > REBIND_K * sigma_chance
RECALL_C_RES = 10            # candidate-recall @ C for the resonator headline

HITS_KS = (1, 10)
EPS = 0.02                   # META_RULE_L strict-above-floor margin for beat-frequency gate
# ---- pre-registered two-stage bands (drill: notes/research_resonator_decode_capacity_ceiling_crux_v2) --
STAGE1_GATED_PASS = 0.35    # residual-gated res_recall@10 >= this at N=2048 (~70% of 0.203->0.491) => STAGE-1
STAGE1_GATED_FAIL = 0.25    # residual-gated res_recall@10 < this => SNR-FLOOR HARD_FAIL_A (fix -> encode)
STAGE1_NONCONV_MAX = 0.20   # non-convergence/limit-cycle rate must be < this for a valid STAGE-1 pass
STAGE1_REL_MARGIN = 0.10    # res_recall@10 must also exceed the run's own single-shot recall by >= this

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
    """n_rel unit-modulus FHRR vectors (complex64). Random phases; near-orthogonal.

    Built on a CPU generator (determinism pinned identically across CPU/GPU) then moved to DEVICE."""
    gtor = torch.Generator().manual_seed(seed * 100003 + 11)
    theta = torch.rand(n_rel, n_dim, generator=gtor) * (2.0 * math.pi)
    R = torch.polar(torch.ones(n_rel, n_dim), theta).to(torch.complex64)  # (n_rel, N)
    return R.to(DEVICE)


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


# ============================ ENTITY-CODEBOOK RESONATOR-RECOVERY DECODE =======
# TOPOLOGY (verified against the v1 cell code + Director "N_DIM x N_entities" + the strategic drill):
# the compose leak is SUPERPOSITION RECOVERY (resonator's home turf, SIMULTANEOUS not sequential),
# not per-atom coefficient readout. Per query (h, r3) the substrate forms a bundle q that SUPERPOSES
# the entity codes of rule-reached tails plus crosstalk:
#     H_h = sum over ALL grounded (rtup, c) from h  of  m * bind(V_rtup, E_c)      (noisy superposition)
#     q   = sum over positive rule-paths p for r3   of  w_p * unbind(H_h, V_p)
#         = sum_{c reached by a rule path} w * E_c  +  crosstalk (from the other bundled terms)
# The gold tail's code E_t is IN q but buried: SINGLE-SHOT argmax-cleanup surfaces the top matched-
# filter entity and drops lower-SNR true tails (the 0.203 bleed). The RESONATOR recovers the buried
# tails by iterative-deflation cleanup against the ENTITY codebook (the N_DIM x N_entities matmul), with:
#   - BATCHED RANDOM RESTARTS (R trajectories, noise at INITIALIZATION only per Karunaratne 2024;
#     restart-budget race oracle_any(R)=1-(1-p)^R -- validated on this substrate 2026-07-07). Stacked on
#     a batch dim -> one batched matmul per step (GPU). A convex/basin-free readout shows ~0 restart lift
#     (honest diagnostic); a basin'd one shows the oracle_any gain.
#   - RESIDUAL RE-BIND GATE (anti-spurious-convergence, non-negotiable): a recovered entity is COUNTED
#     only if its code correlates with the current residual above a per-query chance floor
#     (REBIND_K * sigma of the initial cleanup sims). Report BOTH raw and residual-gated recall; the gap
#     IS the spurious-convergence rate (telemetry-sensitivity discipline).
# ADD-ABLATION: build H_h with (V+E) instead of bind(V,E) -> unbind cannot recover E_c -> recovery
# collapses (bind load-bearing). CODEBOOK: entity codes are DECOUPLED random near-orthogonal (NOT
# embedding-derived) per the correlation-hurts-capacity law; pairwise-cosine is logged. ACF HOOK: if the
# plain resonator + restarts falls short, the asymmetric-codebook factorizer (experiments/
# exp_wave14b_acf_resonator.py, cap_map row 51, 50x on the codebook-SIZE axis a 14k-entity codebook sits
# on) is the next lever -- resonator_recover accepts a recon-codebook argument so ACF wires in without a
# redesign. CAN FAIL: if the compose-time bundling load is too high for N (SNR floor), even restarts do
# not recover -> residual-gated recall stays < 0.25 -> HARD_FAIL_A (fix moves upstream to encode).

def make_entity_vectors(n_ent, n_dim, seed):
    """Entity codebook: random unit-modulus FHRR codes -- DECOUPLED store-codes (near-orthogonal, NOT
    embedding-derived) per correlation-hurts-capacity law. CPU generator (determinism pinned) -> DEVICE."""
    gtor = torch.Generator().manual_seed(seed * 100019 + 29)
    theta = torch.rand(n_ent, n_dim, generator=gtor) * (2.0 * math.pi)
    E = torch.polar(torch.ones(n_ent, n_dim), theta).to(torch.complex64)
    return E.to(DEVICE)


def codebook_cosine_stats(E, n_sample, seed):
    """Pairwise |cosine| of a random sample of codebook rows (correlation audit: near-orthogonal?)."""
    n = E.shape[0]
    if n < 2:
        return {"n_pairs": 0, "mean_abs_cos": 0.0, "p95_abs_cos": 0.0, "max_abs_cos": 0.0}
    g = torch.Generator().manual_seed(seed)
    m = min(n_sample, n)
    idx = torch.randperm(n, generator=g)[:m]
    S = E[idx]
    S = S / torch.linalg.vector_norm(S, dim=1, keepdim=True)
    G = (S @ S.conj().t()).abs()
    M = G.shape[0]
    mask = ~torch.eye(M, dtype=torch.bool, device=G.device)
    vals = G[mask].float()
    return {"n_pairs": int(vals.numel()), "mean_abs_cos": float(vals.mean()),
            "p95_abs_cos": float(torch.quantile(vals, 0.95)), "max_abs_cos": float(vals.max())}


def build_query_bundle(cand, conf_r3, cc, E, n_dim, op):
    """Substrate-native readout bundle q for one query (h,r3): a superposition of rule-reached tail
    entity codes + crosstalk, built via bind/unbind (op='bind') or the ADD ablation (op='add').

    cand: c -> {rtup_counts}. conf_r3: {rtup: conf} positive rule-paths (readout weights w=conf*hop_gain).
    Returns (q on DEVICE, cand_ids list). Batched elementwise ops (GPU-efficient, no per-item Python
    GPU calls)."""
    # ---- H_h: bundle over ALL grounded (rtup, c) instances (the noisy superposition) ----
    Vs, Es, ms = [], [], []
    cand_ids = list(cand.keys())
    for c, d in cand.items():
        Ec = E[c]
        for rtup, m in d["rtup_counts"].items():
            Vs.append(cc.get(rtup)); Es.append(Ec); ms.append(float(m))
    if not Vs:
        return torch.zeros(n_dim, dtype=torch.complex64, device=DEVICE), cand_ids
    Vs = torch.stack(Vs); Es = torch.stack(Es)
    mvec = torch.tensor(ms, dtype=torch.float32, device=DEVICE).unsqueeze(1)
    if op == "bind":
        H = (mvec * (Vs * Es)).sum(0)                 # bind = elementwise complex mul
    else:
        H = (mvec * (Vs + Es)).sum(0)                 # ADD ablation
    # ---- readout: unbind H by each positive rule-path, weight by conf*hop_gain ----
    Vp, wp = [], []
    for rtup, cf in conf_r3.items():
        Vp.append(cc.get(rtup)); wp.append(cf * hop_gain(len(rtup)))
    if not Vp:
        return torch.zeros(n_dim, dtype=torch.complex64, device=DEVICE), cand_ids
    Vp = torch.stack(Vp)
    wv = torch.tensor(wp, dtype=torch.float32, device=DEVICE).unsqueeze(1)
    q = (wv * (H.unsqueeze(0) * Vp.conj())).sum(0)    # unbind = mul by conj; recovers E_c for matching p
    return q, cand_ids


def single_shot_scores(q, E, cand_ids, n_dim):
    """SINGLE-SHOT argmax-cleanup: matched-filter score Re<E_c, q>/N over candidate entities (R=1, no
    deflation). The v1-style decode that buries lower-SNR true tails in the superposition."""
    if not cand_ids:
        return {}
    idx = torch.tensor(cand_ids, device=DEVICE)
    sims = (E[idx] @ q.conj()).real / n_dim
    return {int(c): float(s) for c, s in zip(cand_ids, sims)}


def resonator_recover(q, E, cand_ids, n_dim, k_rec, t_iter, n_restart, tau, rebind_k, gen,
                      E_recon=None):
    """RESONATOR recovery: batched-restart iterative-deflation cleanup of bundle q against the entity
    codebook (candidate rows). Returns (raw_scores, gated_scores, telem).

    raw_scores/gated_scores: c -> rank score (earlier recovery = higher; union-max over restarts).
    gated applies the RESIDUAL RE-BIND GATE (sim > REBIND_K * sigma_of_initial_sims). telem: converged,
    n_iter, n_raw, n_gated, spurious_rate. E_recon (asymmetric reconstruction codebook, e.g. ACF) may
    differ from E; defaults to E (plain resonator)."""
    if not cand_ids:
        return {}, {}, {"converged": True, "n_iter": 0, "n_raw": 0, "n_gated": 0, "spurious_rate": 0.0}
    idx = torch.tensor(cand_ids, device=DEVICE)
    Ecand = E[idx]                                    # (n_cand, N) search codebook
    Erec = Ecand if E_recon is None else E_recon[idx] # reconstruction codebook (ACF hook)
    n_cand = Ecand.shape[0]
    # per-query chance floor for the re-bind gate: ROBUST (MAD) noise sigma of the initial cleanup sims.
    # MAD (not std) so the few large signal sims do not inflate the floor and gate out true weak items.
    sim0 = (Ecand @ q.conj()).real / n_dim
    if n_cand > 2:
        med = sim0.median()
        mad = (sim0 - med).abs().median()
        sigma0 = float(1.4826 * mad)
    else:
        sigma0 = float(sim0.abs().mean())
    rebind_thresh = rebind_k * max(sigma0, 1e-9)
    # batched restarts: R residual copies with INITIALIZATION-only dither (breaks limit cycles)
    Q = q.unsqueeze(0).repeat(n_restart, 1)           # (R, N)
    if tau > 0.0:
        ph = (torch.rand(n_restart, n_dim, generator=gen) * (2.0 * math.pi)).to(DEVICE)
        amp = (tau * torch.ones(n_restart, n_dim)).to(DEVICE)
        Q = Q + torch.polar(amp, ph).to(torch.complex64)
    residual = Q.clone()
    raw_scores, gated_scores = {}, {}
    n_iter_used = 0
    prev_norm = None
    converged = False
    kk = min(t_iter, k_rec) if k_rec > 0 else t_iter
    for it in range(kk):
        sim = (residual @ Ecand.conj().t()).real / n_dim     # (R, n_cand) N_DIM x N_entities matmul (GPU)
        pk = sim.argmax(dim=1)                                # (R,)
        pv = sim.gather(1, pk.unsqueeze(1)).squeeze(1)        # (R,)
        rank_score = float(t_iter - it)                      # earlier recovery -> higher rank
        for r in range(n_restart):
            ci = int(idx[pk[r]].item()); v = float(pv[r])
            cur = rank_score + 1e-3 * v
            if cur > raw_scores.get(ci, -1e18):
                raw_scores[ci] = cur
            if v > rebind_thresh and cur > gated_scores.get(ci, -1e18):
                gated_scores[ci] = cur                       # RESIDUAL RE-BIND GATE
            residual[r] = residual[r] - pv[r] * Erec[pk[r]]  # deflate (explain-away)
        n_iter_used = it + 1
        rn = float(torch.linalg.vector_norm(residual))
        if prev_norm is not None and abs(prev_norm - rn) < 1e-4 * max(prev_norm, 1e-9):
            converged = True
        prev_norm = rn
    n_raw = len(raw_scores); n_gated = len(gated_scores)
    spurious_rate = (n_raw - n_gated) / max(n_raw, 1)
    return raw_scores, gated_scores, {"converged": converged, "n_iter": n_iter_used,
                                      "n_raw": n_raw, "n_gated": n_gated,
                                      "spurious_rate": spurious_rate, "rebind_thresh": rebind_thresh}


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
    pos_rtups, neg_rtups = {}, {}    # resonator dictionary index: r3 -> ordered list of path-types
    for r3 in target_rels:
        pb = torch.zeros(n_dim, dtype=torch.complex64, device=DEVICE)
        pa = torch.zeros(n_dim, dtype=torch.complex64, device=DEVICE)
        pnb = torch.zeros(n_dim, dtype=torch.complex64, device=DEVICE)
        pna = torch.zeros(n_dim, dtype=torch.complex64, device=DEVICE)
        any_rule = False
        pos_list, neg_list = [], []
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
                pos_list.append(rtup)                 # resonator: positive dictionary atom
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
                neg_list.append(rtup)                 # resonator: negative dictionary atom
        if any_rule:
            prof_bind[r3] = pb
            prof_add[r3] = pa
            prof_neg_bind[r3] = pnb
            prof_neg_add[r3] = pna
            pos_rtups[r3] = pos_list
            neg_rtups[r3] = neg_list
    return (conf, prof_bind, prof_add, prof_neg_bind, prof_neg_add, allpat, cc_bind, cc_add,
            pos_rtups, neg_rtups)


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

    # ---- build models on dense (rule mining -> conf dict + ComposeCache for path-vectors) ----
    (conf, prof_bind, prof_add, prof_neg_bind, prof_neg_add, allpat, cc_bind, cc_add,
     pos_rtups, neg_rtups) = build_models(
        gd, target_rels, R, N_DIM, MIN_SUPPORT, MIN_CONF,
        PROFILE_EDGES_PER_REL, L_MAX, BRANCH_CAP, PATH_CAP, seed)
    n_rules = sum(len(v) for v in conf.values())

    # ---- ENTITY codebook (DECOUPLED near-orthogonal store-codes) + correlation audit ----
    E = make_entity_vectors(n_ent, N_DIM, seed)
    cb_cos = codebook_cosine_stats(E, 1000, seed * 13 + 1)

    # per-query candidate cache (graph-traversal propose; shared by all arms)
    cand_cache = {}
    def get_cand(h, r3):
        d = cand_cache.get((h, r3))
        if d is None:
            d = propose_candidates(gd, h, r3, L_MAX, BRANCH_CAP, PATH_CAP)
            cand_cache[(h, r3)] = d
        return d

    # per-query substrate readout bundle q (superposition of rule-reached tail codes); bind + add ablation
    q_cache = {}
    def get_q(h, r3, op):
        v = q_cache.get((h, r3, op))
        if v is None:
            v = build_query_bundle(get_cand(h, r3), conf.get(r3, {}), cc_bind, E, N_DIM, op)
            q_cache[(h, r3, op)] = v
        return v

    # resonator recovery, cached per (h,r3,op); telemetry accumulated once
    res_cache = {}
    res_telem = {"n": 0, "n_conv": 0, "spur_sum": 0.0, "n_gated_sum": 0, "n_raw_sum": 0}
    def get_res(h, r3, op, accum=False):
        v = res_cache.get((h, r3, op))
        if v is None:
            q, cand_ids = get_q(h, r3, op)
            gseed = (seed * 100003 + (h % 99991) * 131 + r3 * 17 + (7 if op == "bind" else 11)) & 0x7fffffff
            gen = torch.Generator().manual_seed(gseed)
            raw, gtd, tel = resonator_recover(q, E, cand_ids, N_DIM, RES_K_REC, RES_T_ITER,
                                              RES_N_RESTART, RES_TAU, RES_REBIND_K, gen)
            v = (raw, gtd, tel)
            res_cache[(h, r3, op)] = v
        if accum:
            _, _, tel = v
            res_telem["n"] += 1
            res_telem["n_conv"] += 1 if tel["converged"] else 0
            res_telem["spur_sum"] += tel["spurious_rate"]
            res_telem["n_gated_sum"] += tel["n_gated"]
            res_telem["n_raw_sum"] += tel["n_raw"]
        return v

    # ---- SINGLE_SHOT_CLEANUP (the v1-style decode that buries lower-SNR true tails; the comparator) ----
    def single_shot_rank(h, r, gold, filt, rr):
        q, cand_ids = get_q(h, r, "bind")
        return strict_rank(single_shot_scores(q, E, cand_ids, N_DIM), gold, filt, rr)
    m_single = eval_arm(single_shot_rank, tq, known, arm_label="SINGLE_SHOT_CLEANUP")

    # ---- RESONATOR_GT (THE FIX: batched-restart iterative recovery; RESIDUAL-GATED scores) ----
    def resonator_rank(h, r, gold, filt, rr):
        _, gtd, _ = get_res(h, r, "bind")
        return strict_rank(gtd, gold, filt, rr)
    m_res = eval_arm(resonator_rank, tq, known, arm_label="RESONATOR_GT")

    # ---- RESONATOR_RAW (same, ungated) -- diagnostic; gap vs gated = spurious-convergence inflation ----
    def resonator_raw_rank(h, r, gold, filt, rr):
        raw, _, _ = get_res(h, r, "bind")
        return strict_rank(raw, gold, filt, rr)
    m_res_raw = eval_arm(resonator_raw_rank, tq, known)

    # ---- BIND_ABLATED (H built with V+E instead of bind(V,E) -> recovery collapses; bind load-bearing) ----
    def ablated_rank(h, r, gold, filt, rr):
        _, gtd, _ = get_res(h, r, "add")
        return strict_rank(gtd, gold, filt, rr)
    m_abl = eval_arm(ablated_rank, tq, known, arm_label="BIND_ABLATED")

    # ---- SYMBOLIC_GT (graph-traversal + confidence noisy-OR; the recall reference/ceiling proxy) ----
    def symbolic_rank(h, r, gold, filt, rr):
        return strict_rank(score_symbolic(get_cand(h, r), r, conf), gold, filt, rr)
    m_sym = eval_arm(symbolic_rank, tq, known)

    # ---- BROKEN_VERIFIER (reach, random score) ----
    brng = random.Random(seed * 991 + 7)
    ent_rand = [brng.random() for _ in range(n_ent)]
    def broken_rank(h, r, gold, filt, rr):
        return strict_rank(score_broken(get_cand(h, r), ent_rand), gold, filt, rr)
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
    ss_rC = ss_r1 = sym_rC = sym_r1 = 0
    resg_rC = resg_r1 = resraw_rC = 0     # residual-GATED vs RAW resonator recall
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
        # compose-fidelity: top-C recall by SINGLE-SHOT cleanup vs symbolic vs RESONATOR (gated+raw)
        rrng = random.Random(999)
        q_b, cand_ids = get_q(h, r, "bind")
        sc_ss = single_shot_scores(q_b, E, cand_ids, N_DIM)
        sc_s = score_symbolic(cand, r, conf)
        raw, gtd, _ = get_res(h, r, "bind", accum=True)   # accumulate convergence telemetry here
        sc_p = score_precount(cand)
        if topc_has_gold(sc_ss, gold, filt, RECALL_C): ss_rC += 1
        if topc_has_gold(sc_ss, gold, filt, 1): ss_r1 += 1
        if topc_has_gold(sc_s, gold, filt, RECALL_C): sym_rC += 1
        if topc_has_gold(sc_s, gold, filt, 1): sym_r1 += 1
        if topc_has_gold(gtd, gold, filt, RECALL_C): resg_rC += 1
        if topc_has_gold(gtd, gold, filt, 1): resg_r1 += 1
        if topc_has_gold(raw, gold, filt, RECALL_C): resraw_rC += 1
        # verifier-lift: pre-verify (path-count) MRR over proposed
        pr = strict_rank(sc_p, gold, filt, rrng)
        if pr is not None:
            n_gold_prop += 1
            pre_rr += 1.0 / pr
    nq = len(tq)
    ceiling = ceil_hit / nq
    pre_mrr = (pre_rr / n_gold_prop) if n_gold_prop else 0.0
    nrt = max(res_telem["n"], 1)
    nonconv_rate = 1.0 - res_telem["n_conv"] / nrt
    ss_recallC = ss_rC / nq
    sym_recallC = sym_rC / nq
    resg_recallC = resg_rC / nq
    resraw_recallC = resraw_rC / nq
    waterfall = {
        "1_candidate_recall_ceiling": ceiling,
        "2_compose_fidelity": {
            "single_shot_recall@%d" % RECALL_C: ss_recallC,
            "sym_recall@%d" % RECALL_C: sym_recallC,
            "res_gated_recall@%d" % RECALL_C: resg_recallC,        # HEADLINE (STAGE-1 metric)
            "res_raw_recall@%d" % RECALL_C: resraw_recallC,
            "single_shot_recall@1": ss_r1 / nq, "sym_recall@1": sym_r1 / nq,
            "res_gated_recall@1": resg_r1 / nq,
            "res_gain_over_single_shot@%d" % RECALL_C: resg_recallC - ss_recallC,
            "spurious_inflation@%d" % RECALL_C: resraw_recallC - resg_recallC,  # raw minus gated
            "res_closes_gap_frac": ((resg_recallC - ss_recallC) / max(sym_recallC - ss_recallC, 1e-9))
                                   if (sym_recallC - ss_recallC) > 0 else 0.0,
        },
        "2b_resonator_convergence": {
            "n_queries": res_telem["n"],
            "nonconvergence_rate": nonconv_rate,
            "mean_spurious_rate": res_telem["spur_sum"] / nrt,
            "mean_n_gated": res_telem["n_gated_sum"] / nrt,
            "mean_n_raw": res_telem["n_raw_sum"] / nrt,
            "n_restart": RES_N_RESTART, "t_iter": RES_T_ITER, "tau": RES_TAU, "rebind_k": RES_REBIND_K,
        },
        "2c_codebook_correlation": cb_cos,
        "3_verifier_lift": {
            "pre_verify_cond_mrr": pre_mrr,
            "res_post_verify_cond_mrr": m_res["cond_mrr"],
            "sym_post_verify_cond_mrr": m_sym["cond_mrr"],
            "res_lift_over_pre": m_res["cond_mrr"] - pre_mrr,
            "res_precision@1_cond": m_res["cond_hits@1"],
            "sym_precision@1_cond": m_sym["cond_hits@1"],
            "broken_precision@1_cond": m_broken["cond_hits@1"],
        },
        "4_rank_quality_cond": {
            "res_cond_mrr": m_res["cond_mrr"], "res_cond_hits@1": m_res["cond_hits@1"],
            "res_n_proposed": m_res["n_proposed"],
            "single_shot_cond_mrr": m_single["cond_mrr"], "single_shot_cond_hits@1": m_single["cond_hits@1"],
            "sym_cond_mrr": m_sym["cond_mrr"], "sym_cond_hits@1": m_sym["cond_hits@1"],
        },
        "5_info_ceiling_per_stratum": {
            k: (strat_hit[k] / strat_tot[k] if strat_tot[k] else 0.0) for k in strata
        },
    }

    # ============ DEGREE/FREQUENCY-CONFOUND STRATIFICATION (tail-collapse detector; RESONATOR arm) ====
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
    ds_res = eval_arm_stratified(resonator_rank, tq, known, strat_of_gold, strat_names)
    ds_pf = eval_arm_stratified(pop_relfreq_rank, tq, known, strat_of_gold, strat_names)
    ds_pd = eval_arm_stratified(pop_deg_rank, tq, known, strat_of_gold, strat_names)
    degree_stratified = {}
    for s in strat_names:
        degree_stratified[s] = {
            "n": ds_res[s]["n"], "deg_tertile_bounds": [q1, q2],
            "RESONATOR_GT": {"hits@1": ds_res[s]["hits@1"], "mrr": ds_res[s]["mrr"]},
            "POP_RELFREQ": {"hits@1": ds_pf[s]["hits@1"], "mrr": ds_pf[s]["mrr"]},
            "POP_DEGREE": {"hits@1": ds_pd[s]["hits@1"], "mrr": ds_pd[s]["mrr"]},
            "margin_vs_relfreq": {"hits@1": ds_res[s]["hits@1"] - ds_pf[s]["hits@1"],
                                  "mrr": ds_res[s]["mrr"] - ds_pf[s]["mrr"]},
            "margin_vs_degree": {"hits@1": ds_res[s]["hits@1"] - ds_pd[s]["hits@1"],
                                 "mrr": ds_res[s]["mrr"] - ds_pd[s]["mrr"]},
        }

    return {
        "seed": seed,
        "n_ent": n_ent, "n_rel": len(rel2i),
        "n_train": len(train), "avgdeg_dense": 2.0 * len(train) / n_ent,
        "n_test_eval": nq, "n_rules": n_rules, "N_DIM": N_DIM,
        "device": str(DEVICE), "cuda_avail": CUDA_AVAIL,
        "ceiling": ceiling, "degree_stratified": degree_stratified,
        "RESONATOR_GT": m_res, "RESONATOR_RAW": m_res_raw, "SINGLE_SHOT_CLEANUP": m_single,
        "BIND_ABLATED": m_abl, "SYMBOLIC_GT": m_sym,
        "POP_RELFREQ": m_pop_rf, "POP_DEGREE": m_pop_deg,
        "BROKEN_VERIFIER": m_broken, "RANDOM": m_random,
        "res_gated_recall@%d" % RECALL_C: resg_recallC,
        "single_shot_recall@%d" % RECALL_C: ss_recallC,
        "sym_recall@%d" % RECALL_C: sym_recallC,
        "nonconvergence_rate": nonconv_rate,
        "waterfall": waterfall,
    }


# ============================ verdict =========================================
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_verdict(per_seed):
    def agg(arm, k):
        return _mean([s[arm][k] for s in per_seed])
    res1 = agg("RESONATOR_GT", "hits@1"); resmrr = agg("RESONATOR_GT", "mrr"); res10 = agg("RESONATOR_GT", "hits@10")
    ss1 = agg("SINGLE_SHOT_CLEANUP", "hits@1"); ssmrr = agg("SINGLE_SHOT_CLEANUP", "mrr")
    abl_mrr = agg("BIND_ABLATED", "mrr")
    sym1 = agg("SYMBOLIC_GT", "hits@1"); symmrr = agg("SYMBOLIC_GT", "mrr")
    pf1 = agg("POP_RELFREQ", "hits@1"); pfmrr = agg("POP_RELFREQ", "mrr"); pf10 = agg("POP_RELFREQ", "hits@10")
    b1 = agg("BROKEN_VERIFIER", "hits@1"); bmrr = agg("BROKEN_VERIFIER", "mrr")
    ceil = _mean([s["ceiling"] for s in per_seed])

    RCK = "res_gated_recall@%d" % RECALL_C
    SCK = "single_shot_recall@%d" % RECALL_C
    SYK = "sym_recall@%d" % RECALL_C
    res_gated = _mean([s[RCK] for s in per_seed])       # HEADLINE STAGE-1 metric
    ss_recall = _mean([s[SCK] for s in per_seed])
    sym_recall = _mean([s[SYK] for s in per_seed])
    nonconv = _mean([s["nonconvergence_rate"] for s in per_seed])

    # ---- STAGE-1: the fix WORKS (resonator recovers the compose-crosstalk-dropped candidates) ----
    stage1_absolute = (res_gated >= STAGE1_GATED_PASS)                 # >= 0.35 (drill band)
    stage1_relative = (res_gated >= ss_recall + STAGE1_REL_MARGIN)     # materially beats single-shot
    stage1_converged = (nonconv < STAGE1_NONCONV_MAX)                  # < 20% non-convergence
    stage1_pass = stage1_absolute and stage1_relative and stage1_converged
    stage1_snr_floor = (res_gated < STAGE1_GATED_FAIL)                 # < 0.25 => SNR-floor HARD_FAIL_A

    # ---- STAGE-2: the ultimate bar (resonator-decoded substrate BEATS frequency) ----
    stage2_pass = (res1 >= pf1 + EPS) and (resmrr >= pfmrr + EPS)

    # ---- load-bearing gates ----
    bind_loadbearing = (abl_mrr <= 0.7 * max(resmrr, 1e-9))
    broken_fails = (bmrr <= 0.5 * max(resmrr, 1e-9)) and (b1 <= 0.5 * max(res1, 1e-9))
    resonator_helps = (res_gated >= ss_recall + STAGE1_REL_MARGIN)

    hard_pass = stage1_pass and stage2_pass and bind_loadbearing and broken_fails

    if hard_pass:
        v = "HARD_PASS"
    elif stage1_snr_floor:
        v = "HARD_FAIL_A_SNR_FLOOR"          # decode did NOT recover recall -> fix moves to encode
    elif stage1_pass and (not stage2_pass):
        v = "HARD_FAIL_B_WALL_MOVES"          # recall recovered but still loses freq -> rank/knowledge wall
    elif not bind_loadbearing:
        v = "HARD_FAIL_BIND_NOT_LOADBEARING"
    elif not broken_fails:
        v = "HARD_FAIL_BROKEN_VERIFIER_INFERS"
    else:
        v = "MIDDLE_BAND"

    msg = ("RES_GT h@1=%.3f mrr=%.3f h@10=%.3f | res_gated_recall@%d=%.3f (single_shot=%.3f sym=%.3f) | "
           "POP_RELFREQ h@1=%.3f mrr=%.3f | SYM h@1=%.3f mrr=%.3f | ABLATED mrr=%.3f (ratio=%.2f) | "
           "BROKEN mrr=%.3f | nonconv=%.3f ceiling=%.3f || STAGE1=%s(abs=%s rel=%s conv=%s) STAGE2=%s "
           "bind_lb=%s broken_fails=%s"
           % (res1, resmrr, res10, RECALL_C, res_gated, ss_recall, sym_recall,
              pf1, pfmrr, sym1, symmrr, abl_mrr, abl_mrr / max(resmrr, 1e-9), bmrr, nonconv, ceil,
              stage1_pass, stage1_absolute, stage1_relative, stage1_converged, stage2_pass,
              bind_loadbearing, broken_fails))
    gates = {
        "RESONATOR_GT_hits1": res1, "RESONATOR_GT_mrr": resmrr, "RESONATOR_GT_hits10": res10,
        "SINGLE_SHOT_hits1": ss1, "SINGLE_SHOT_mrr": ssmrr,
        "SYMBOLIC_GT_hits1": sym1, "SYMBOLIC_GT_mrr": symmrr,
        "POP_RELFREQ_hits1": pf1, "POP_RELFREQ_mrr": pfmrr, "POP_RELFREQ_hits10": pf10,
        "res_gated_recall@C": res_gated, "single_shot_recall@C": ss_recall, "sym_recall@C": sym_recall,
        "nonconvergence_rate": nonconv,
        "ABLATED_mrr": abl_mrr, "ablated_ratio": abl_mrr / max(resmrr, 1e-9),
        "BROKEN_mrr": bmrr, "ceiling": ceil,
        "stage1_pass": stage1_pass, "stage1_absolute": stage1_absolute,
        "stage1_relative": stage1_relative, "stage1_converged": stage1_converged,
        "stage1_snr_floor": stage1_snr_floor, "stage2_pass": stage2_pass,
        "bind_loadbearing": bind_loadbearing, "broken_fails": broken_fails,
        "resonator_helps": resonator_helps,
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


def _topk_ids(scores, k):
    return set(sorted(scores.keys(), key=lambda c: -scores[c])[:k])


def _selftest():
    print("[selftest] device=%s cuda_avail=%s" % (DEVICE, CUDA_AVAIL), flush=True)
    Nt = 256

    # ---- D6: RESONATOR recovers a BURIED superposition that single-shot argmax drops (THE FIX) ----
    # q superposes 3 GOLD entity codes (weights 1.0/0.6/0.28) + 3 DISTRACTOR codes (0.75/0.70/0.65).
    # The weakest gold (0.28) is buried below every distractor -> single-shot top-3 misses 2 golds.
    # The resonator deflates strong items first, then surfaces the buried gold -> recovers all 3.
    E = make_entity_vectors(100, Nt, 0)
    golds = [3, 40, 77]; gweights = [1.0, 0.6, 0.28]
    distr = [11, 55, 88]; dweights = [0.75, 0.70, 0.65]
    q = torch.zeros(Nt, dtype=torch.complex64, device=DEVICE)
    for i, w in zip(golds + distr, gweights + dweights):
        q = q + w * E[i]
    cand_ids = list(range(100))
    ss = single_shot_scores(q, E, cand_ids, Nt)
    ss_top3 = _topk_ids(ss, 3)
    assert not set(golds).issubset(ss_top3), \
        "D6 PRECONDITION FAIL: single-shot already recovers all golds (no burial to fix); top3=%s" % ss_top3
    gen = torch.Generator().manual_seed(1)
    raw, gtd, tel = resonator_recover(q, E, cand_ids, Nt, 0, 8, 4, 0.4, 2.5, gen)
    res_set = set(gtd.keys())
    n_res = len(set(golds) & res_set); n_ss = len(set(golds) & ss_top3)
    assert n_res > n_ss, "D6 FAIL: resonator (%d golds gated) did not beat single-shot top3 (%d golds)" % (n_res, n_ss)
    assert set(golds).issubset(res_set), \
        "D6 FAIL: resonator did not recover all 3 golds (gated set=%s)" % sorted(res_set)

    # ---- D6b: RESIDUAL RE-BIND GATE rejects spurious convergence on a PURE-NOISE query ----
    gen2 = torch.Generator().manual_seed(2)
    phn = (torch.rand(Nt, generator=gen2) * 2.0 * math.pi)
    qn = torch.polar(torch.ones(Nt), phn).to(torch.complex64).to(DEVICE)   # 1 random code = no stored bundle
    raw_n, gtd_n, tel_n = resonator_recover(qn, E, cand_ids, Nt, 0, 8, 4, 0.4, 2.5, gen2)
    assert len(gtd_n) <= 2, "D6b FAIL: re-bind gate accepted %d spurious recoveries on pure noise" % len(gtd_n)
    assert tel["n_gated"] >= tel_n["n_gated"], "D6b FAIL: gate not telemetry-sensitive (signal<=noise gated)"

    # ---- D7: bind LOAD-BEARING via the full pipeline (build_query_bundle bind vs add) on a planted KG ----
    triples, gold = _build_planted(with_support=True)
    train_p = triples + gold[:10]; gold_test = gold[10:]
    ent2i, rel2i = build_ids(train_p, [], gold_test)
    g = Graph(train_p, ent2i, rel2i)
    Rrel = make_rel_vectors(len(rel2i), Nt, 0)
    Ep = make_entity_vectors(len(ent2i), Nt, 0)
    (conf, _pb, _pa, _pnb, _pna, _ap, cc_bind, _cca, _pr, _nr) = build_models(
        g, list(rel2i.values()), Rrel, Nt, 3, 0.3, 1000, L_MAX, 40, 2000, 0)
    known = defaultdict(set)
    for tr in (train_p, gold_test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    tq = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in gold_test]
    def _decode_rank(op):
        def rk(h, r, gold, filt, rr):
            cand = propose_candidates(g, h, r, L_MAX, 40, 2000)
            qb, cids = build_query_bundle(cand, conf.get(r, {}), cc_bind, Ep, Nt, op)
            gen3 = torch.Generator().manual_seed(7)
            _rw, gt, _tl = resonator_recover(qb, Ep, cids, Nt, 0, 10, 6, 0.4, 2.5, gen3)
            return strict_rank(gt, gold, filt, rr)
        return eval_arm(rk, tq, known)
    m_bind = _decode_rank("bind")
    m_add = _decode_rank("add")
    assert m_bind["hits@1"] >= 0.6, "D7 FAIL: bind decode did not recover planted rule hits@1=%.3f" % m_bind["hits@1"]
    assert m_add["hits@1"] <= 0.5 * max(m_bind["hits@1"], 1e-9), \
        "D7 FAIL: add-ablation still infers hits@1=%.3f (bind not load-bearing; bind=%.3f)" % (m_add["hits@1"], m_bind["hits@1"])

    print("[selftest] PASS: D6 res_golds=%d>ss_golds=%d | D6b gate noise_gated=%d<=signal_gated=%d | "
          "D7 bind_h@1=%.2f add_h@1=%.2f | device=%s"
          % (n_res, n_ss, len(gtd_n), tel["n_gated"], m_bind["hits@1"], m_add["hits@1"], DEVICE), flush=True)


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
        cf = wf["2_compose_fidelity"]
        print("[seed %d] RES h@1=%.3f mrr=%.3f | POP_RF h@1=%.3f mrr=%.3f | SYM mrr=%.3f | "
              "ABL mrr=%.3f | BROKEN mrr=%.3f | ceil=%.3f | res_gated_recall@%d=%.3f "
              "(single_shot=%.3f sym=%.3f) spur=%.3f nonconv=%.3f (%.1fs)"
              % (seed, r["RESONATOR_GT"]["hits@1"], r["RESONATOR_GT"]["mrr"],
                 r["POP_RELFREQ"]["hits@1"], r["POP_RELFREQ"]["mrr"], r["SYMBOLIC_GT"]["mrr"],
                 r["BIND_ABLATED"]["mrr"], r["BROKEN_VERIFIER"]["mrr"], r["ceiling"], RECALL_C,
                 cf["res_gated_recall@%d" % RECALL_C], cf["single_shot_recall@%d" % RECALL_C],
                 cf["sym_recall@%d" % RECALL_C], cf["spurious_inflation@%d" % RECALL_C],
                 r["nonconvergence_rate"], time.time() - ts), flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF): use seed-0 per-arm metric dicts
    s0 = per_seed[0]
    _arms_must_differ({a: s0[a] for a in
                       ["RESONATOR_GT", "SINGLE_SHOT_CLEANUP", "BIND_ABLATED", "SYMBOLIC_GT",
                        "POP_RELFREQ", "POP_DEGREE", "BROKEN_VERIFIER", "RANDOM"]})

    verdict, vmsg, gates = compute_verdict(per_seed)
    elapsed = time.time() - t0
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
               "summary": vmsg[:200], "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
               "device": str(DEVICE), "cuda_avail": CUDA_AVAIL,
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
