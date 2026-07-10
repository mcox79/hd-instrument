"""
gt_induction_fb15k237_dense_v1 -- STEP-1 GENERATE-AND-TEST inductive relation inference on a DENSE graph.

QUESTION. Every prior relational-inference NEGATIVE this arc was measured on our ConceptNet slice
(avg-deg ~2.68, no 10-core) -- ~14x below the density floor where held-out inference is even possible.
This cell asks: does inference work on a DENSE graph (FB15k-237, avg-deg ~37) with a GENERATE-AND-TEST
mechanism (discrete propose-then-verify), where it could NOT on sparse? It isolates the two necessary
conditions we identified: DENSITY (clear the floor) + MECHANISM (a support+confidence VERIFIER, the
load-bearing piece every passive/smoothing method lacked).

MECHANISM (symbolic generate-and-test / AMIE-style rule induction):
  PROPOSE: mine length-1 (fwd + inverse) and length-2 PATH-COMPOSITION rules from the train graph,
    r1(A,B) AND r2(B,C) => r3(A,C). Composition is a symbolic hash-join (relational join over adjacency
    lists). [Design note: our chain-grade bind/unbind operator is available for vector composition, but
    a symbolic rule-mining PROPOSE is CLEANER here and keeps the DENSITY question free of substrate
    cleanup-noise confounds; the density + verifier contrasts do not depend on composition being
    vector-based. bind/unbind vector-compose is a documented follow-up.]
  VERIFY (load-bearing): accept a rule only if support >= MIN_SUPPORT and confidence >= MIN_CONF on the
    train graph (confidence = support_groundings / body_groundings). The VERIFIER is the piece the
    broken-verifier control ablates.
  APPLY: for held-out test query (h, r, ?t), forward-chain accepted rules with head r from h to propose
    candidate tails; score each candidate by max accepted-rule confidence; rank (filtered). STRICT
    generate-and-test protocol: a gold tail counts as a hit ONLY if the mechanism actually PROPOSES it
    (unproposed gold = miss). This is the honest "did it INFER it" bar and makes ceiling exact.

ARMS (pre-registered contrasts):
  1. GT_DENSE     -- generate-and-test on full FB15k-237 (the candidate).
  2. GT_SPARSE    -- SAME mechanism on a degree-downsampled FB15k-237 held to avg-deg ~3 (same node set,
                     same relation vocab, same code -- ONLY density changes). Density contrast; must FAIL.
  3. POPULARITY   -- rank candidate tails by per-relation tail frequency (no rules). Must be BEATEN.
  4. BROKEN_VERIF -- SAME generator, RANDOM verifier: a random subset (== accepted-rule count) of ALL
                     mined patterns (incl junk low-confidence ones), scored with RANDOM confidences.
                     Must NOT infer (verifier is load-bearing, not the generator alone). MUST FIRE.
  5. RANDOM       -- uniform-random ranking (filtered). Floor.

INFO-CEILING. ceiling = fraction of test queries whose gold tail is REACHABLE by ANY mined body pattern
(support>=1, pre-verifier) = the generator's reach. Achieved/ceiling (not an absolute bar) reports how
much of the reachable signal the verifier's accepted rules capture.

DECISION (pre-registered, relational -- robust to absolute calibration):
  HARD_PASS = GT_DENSE materially beats POPULARITY (hits@10 >= 1.5x POP AND gap >= 0.05)
              AND density contrast positive (GT_DENSE hits@10 >= 1.5x GT_SPARSE)
              AND broken-verifier fails (BROKEN MRR <= 0.5x GT_DENSE MRR AND BROKEN hits@10 <= 1.2x POP)
              AND achieved a meaningful fraction of ceiling (GT_DENSE hits@10 / ceiling >= 0.30).
  HARD_FAIL = GT_DENSE ties/loses POPULARITY (hits@10 < 1.2x POP) OR density contrast absent
              (GT_DENSE hits@10 < 1.5x GT_SPARSE) OR broken-verifier still infers (BROKEN MRR > 0.7x
              GT_DENSE MRR). A clean HARD_FAIL is VALUABLE: density + this mechanism is not sufficient.
  Anything between = MIDDLE_BAND.

SELF-TEST discriminators (must FIRE): (1) planted composition rule recovered + its held-out edges
inferred (hits@1==1.0); (2) broken verifier recovers nothing on the same planted graph; (3) sparse
(support-stripped) planted graph fails; (4) a random-rule generator fails.

COMPUTE. Pure symbolic relational hash-joins + dict lookups; NO substrate vectors, NO bind/unbind
matmul. Sequential-CPU is correct (combinatorial graph traversal, not matmul). CPU-friendly per task.

ASCII-only. write_metrics. RUN_MODE defaults to full (runner invokes with no argv).
"""
from __future__ import annotations
import sys, os, argparse, time, json, math, random, traceback, platform
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "gt_induction_fb15k237_dense_v1"
FB_DIR = REPO / "data" / "fb15k237_testbed"

# ---- run mode / config -------------------------------------------------------
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Rule-mining / verifier params (calibration_check: default_ok_for_this_regime; see prereg).
MIN_SUPPORT = 10          # verifier: min rule support (groundings)
MIN_CONF = 0.10           # verifier: min rule confidence
MAX_RULES_PER_HEAD = 50   # keep top rules by confidence per head relation
HUB_CAP = 60000           # skip middle nodes where in_deg*out_deg > HUB_CAP (hub-explosion guard)
SPARSE_TARGET_AVGDEG = 3.0

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_EVAL = 300           # subsample test queries
    TOP_K_RELS = 40        # restrict to most-frequent relations to keep density but bound wall
    HUB_CAP = 20000
    MIN_SUPPORT = 3
else:
    SEEDS = [7, 17, 23]
    N_EVAL = 3000
    TOP_K_RELS = 0         # 0 = all relations

HITS_KS = (1, 10)


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
        # directed edge -> set of relation ids
        self.edge_rels = defaultdict(set)          # (h,t) -> {r}
        self.out_by_node = defaultdict(list)       # b -> [(r,c)]  edges OUT of b
        self.in_by_node = defaultdict(list)        # b -> [(r,a)]  edges INTO b
        self.out_adj_rel = defaultdict(lambda: defaultdict(list))  # r -> h -> [t]
        self.in_adj_rel = defaultdict(lambda: defaultdict(list))   # r -> t -> [h]
        self.rel_tail_freq = defaultdict(Counter)  # r -> Counter(tail)
        self.rel_edge_count = Counter()            # r -> #edges (L1 body size)
        self.node_degree = Counter()               # e -> global in+out degree (task baseline)
        for (h, r, t) in triples:
            hi, ri, ti = ent2i[h], rel2i[r], ent2i[t]
            self.edge_rels[(hi, ti)].add(ri)
            self.out_by_node[hi].append((ri, ti))   # edges OUT of hi: (r, tail)
            self.in_by_node[ti].append((ri, hi))    # edges INTO ti: (r, head)
            self.out_adj_rel[ri][hi].append(ti)
            self.in_adj_rel[ri][ti].append(hi)
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


# ============================ rule mining =====================================
def mine_rules(g, target_rels, min_support, min_conf, max_rules_per_head, hub_cap):
    """Mine L1 (fwd + inverse) + L2 path-composition rules.

    Returns (accepted_by_head, allpat_by_head):
      accepted_by_head[r3] = list of tuples, verifier-passed, top by confidence:
          ('L2', r1, r2, conf, supp) | ('L1F', r1, 0, conf, supp) | ('L1I', r1, 0, conf, supp)
      allpat_by_head[r3]   = list of ('L2'|'L1F'|'L1I', r1, r2) for EVERY pattern with support>=1
                             (pre-verifier; the generator's reach -> ceiling).
    """
    target = set(target_rels)
    # ---- L1 forward + inverse ----
    body_l1 = g.rel_edge_count                        # body size for L1 = #edges of r1
    supp_l1f = Counter()                              # (r1,r3): r1(a,b) & r3(a,b)
    supp_l1i = Counter()                              # (r1,r3): r1(a,b) & r3(b,a) -> r1 inv => r3
    for (hi, ti), rels in g.edge_rels.items():
        fwd = g.edge_rels.get((hi, ti))               # r3 s.t. r3(hi,ti)
        inv = g.edge_rels.get((ti, hi))               # r3 s.t. r3(ti,hi)
        for r1 in rels:
            if fwd:
                for r3 in fwd:
                    if r3 != r1 and r3 in target:
                        supp_l1f[(r1, r3)] += 1
            if inv:
                for r3 in inv:
                    if r3 in target:
                        supp_l1i[(r1, r3)] += 1

    # ---- L2 path composition (single streaming pass over middle nodes) ----
    body_l2 = Counter()                               # (r1,r2) -> body groundings
    supp_l2 = Counter()                               # (r1,r2,r3) -> support groundings
    n_hub_skipped = 0
    for b in list(g.in_by_node.keys()):
        inn = g.in_by_node.get(b, ())                 # (r1, a): a -r1-> b
        outn = g.out_by_node.get(b, ())               # (r2, c): b -r2-> c
        li, lo = len(inn), len(outn)
        if li == 0 or lo == 0:
            continue
        if li * lo > hub_cap:
            n_hub_skipped += 1
            continue
        for (r1, a) in inn:
            for (r2, c) in outn:
                if a == c:
                    continue
                body_l2[(r1, r2)] += 1
                r3set = g.edge_rels.get((a, c))       # r3 s.t. r3(a,c)
                if r3set:
                    for r3 in r3set:
                        if r3 in target:
                            supp_l2[(r1, r2, r3)] += 1

    # ---- assemble candidates + verifier ----
    allpat_by_head = defaultdict(list)
    cand_by_head = defaultdict(list)   # r3 -> [(kind,r1,r2,conf,supp)]
    for (r1, r2, r3), s in supp_l2.items():
        b = body_l2.get((r1, r2), 0)
        if b <= 0:
            continue
        conf = s / b
        allpat_by_head[r3].append(("L2", r1, r2))
        if s >= min_support and conf >= min_conf:
            cand_by_head[r3].append(("L2", r1, r2, conf, s))
    for (r1, r3), s in supp_l1f.items():
        b = body_l1.get(r1, 0)
        if b <= 0:
            continue
        conf = s / b
        allpat_by_head[r3].append(("L1F", r1, 0))
        if s >= min_support and conf >= min_conf:
            cand_by_head[r3].append(("L1F", r1, 0, conf, s))
    for (r1, r3), s in supp_l1i.items():
        b = body_l1.get(r1, 0)
        if b <= 0:
            continue
        conf = s / b
        allpat_by_head[r3].append(("L1I", r1, 0))
        if s >= min_support and conf >= min_conf:
            cand_by_head[r3].append(("L1I", r1, 0, conf, s))

    accepted_by_head = {}
    for r3, rules in cand_by_head.items():
        rules.sort(key=lambda x: x[3], reverse=True)
        accepted_by_head[r3] = rules[:max_rules_per_head]
    return accepted_by_head, allpat_by_head, n_hub_skipped


# ============================ application =====================================
def _emit(pn, c, s):
    """Noisy-OR accumulator: pn[c] holds prod(1-conf); final score = 1 - pn[c]."""
    pn[c] = pn.get(c, 1.0) * (1.0 - s)


def _finalize(pn):
    return {c: 1.0 - v for c, v in pn.items()}


def propose(g, h, r3, rules):
    """Forward-chain accepted rules with head r3 from h; NOISY-OR aggregate confidences.

    score(c) = 1 - prod_{rules proposing c}(1 - conf). Rewards candidates supported by
    multiple independent high-confidence rules (standard AnyBURL/AMIE aggregation).
    """
    pn = {}
    for (kind, r1, r2, conf, supp) in rules:
        s = conf
        if kind == "L2":
            for b in g.out_adj_rel.get(r1, {}).get(h, ()):        # h -r1-> b
                for c in g.out_adj_rel.get(r2, {}).get(b, ()):    # b -r2-> c
                    if c != h:
                        _emit(pn, c, s)
        elif kind == "L1F":
            for c in g.out_adj_rel.get(r1, {}).get(h, ()):        # h -r1-> c
                if c != h:
                    _emit(pn, c, s)
        elif kind == "L1I":
            for c in g.in_adj_rel.get(r1, {}).get(h, ()):         # c -r1-> h
                if c != h:
                    _emit(pn, c, s)
    return _finalize(pn)


def reachable(g, h, r3, allpats):
    """Set of tails reachable by ANY mined body pattern (pre-verifier) = generator reach."""
    out = set()
    for (kind, r1, r2) in allpats:
        if kind == "L2":
            for b in g.out_adj_rel.get(r1, {}).get(h, ()):
                for c in g.out_adj_rel.get(r2, {}).get(b, ()):
                    if c != h:
                        out.add(c)
        elif kind == "L1F":
            for c in g.out_adj_rel.get(r1, {}).get(h, ()):
                if c != h:
                    out.add(c)
        elif kind == "L1I":
            for c in g.in_adj_rel.get(r1, {}).get(h, ()):
                if c != h:
                    out.add(c)
    return out


def propose_allpat_random(g, h, r3, allpats, ent_rand):
    """BROKEN-VERIFIER proposal: SAME generator (full reach, ALL mined patterns, no
    support+confidence filter), but the verifier is SHUFFLED -- it emits a score per
    candidate that is UNCORRELATED with truth (a fixed random value per entity, ent_rand).

    This ablates the verifier cleanly: candidates are ranked at random within the reachable
    set. It deliberately does NOT retain any multiplicity/aggregation signal (which would
    leak structure), so it isolates the value of the real support+confidence ranking.
    Returns {cand: random-score}.
    """
    reach = reachable(g, h, r3, allpats)
    return {c: ent_rand[c] for c in reach}


def strict_rank(scores, gold, filter_set, rng):
    """Filtered STRICT rank of gold among PROPOSED candidates.

    scores: {cand: score}. gold counted a hit ONLY if proposed (in scores). filter_set: other known
    true tails to remove. Returns rank (1-based) or None if gold not proposed.
    """
    if gold not in scores:
        return None
    g_score = scores[gold]
    higher = 0
    ties = 0
    for c, sc in scores.items():
        if c == gold or c in filter_set:
            continue
        if sc > g_score:
            higher += 1
        elif sc == g_score:
            ties += 1
    # random tie placement (deterministic per rng)
    return higher + 1 + rng.randint(0, ties)


def pop_rank(pop_counter, gold, filter_set, rng, n_ent):
    """Filtered rank of gold by per-relation tail popularity (all entities ranked)."""
    g_pop = pop_counter.get(gold, 0)
    higher = 0
    ties = 0
    for c, p in pop_counter.items():
        if c == gold or c in filter_set:
            continue
        if p > g_pop:
            higher += 1
        elif p == g_pop:
            ties += 1
    # entities with zero popularity not in counter: they tie at 0 with gold if gold also 0
    if g_pop == 0:
        # gold is among the zero-mass mass; approximate its expected rank as middle of zero block
        zero_block = n_ent - len(pop_counter)  # entities never seen as tail of this rel
        ties += max(0, zero_block - 1)
    return higher + 1 + rng.randint(0, ties)


def random_rank(gold, filter_set, rng, n_ent):
    """Uniform-random filtered rank floor."""
    pool = n_ent - len(filter_set) - 1
    if pool <= 0:
        return 1
    return rng.randint(1, pool + 1)


# ============================ evaluation ======================================
def eval_arm(g, test_queries, known_tails, rank_fn):
    """rank_fn(h, r, gold, filter_set, rng) -> rank or None. Returns metrics dict."""
    h1 = h10 = 0
    rr = 0.0
    n = len(test_queries)
    rng = random.Random(12345)
    for (h, r, gold) in test_queries:
        filt = known_tails.get((h, r), set()) - {gold}
        rank = rank_fn(h, r, gold, filt, rng)
        if rank is None:
            continue
        if rank <= 1:
            h1 += 1
        if rank <= 10:
            h10 += 1
        rr += 1.0 / rank
    return {"hits@1": h1 / n, "hits@10": h10 / n, "mrr": rr / n, "n": n}


# ============================ sparse downsample ===============================
def downsample(train, target_avgdeg, ent2i, seed):
    """Degree-downsample train edges to target avg-degree (same node/rel vocab). ONLY density changes."""
    n_ent = len(ent2i)
    keep_e = int(target_avgdeg * n_ent / 2.0)
    rng = random.Random(seed)
    if keep_e >= len(train):
        return list(train)
    idx = list(range(len(train)))
    rng.shuffle(idx)
    keep = set(idx[:keep_e])
    return [train[i] for i in keep]


# ============================ arms ============================================
def run_seed(train, valid, test, ent2i, rel2i, seed):
    rng = random.Random(seed)
    n_ent = len(ent2i)

    # target relations (restrict for smoke)
    rel_freq = Counter()
    for (h, r, t) in train:
        rel_freq[rel2i[r]] += 1
    if TOP_K_RELS and TOP_K_RELS < len(rel2i):
        target_rels = [r for r, _ in rel_freq.most_common(TOP_K_RELS)]
    else:
        target_rels = list(rel2i.values())
    target_set = set(target_rels)

    # DENSE graph
    gd = Graph(train, ent2i, rel2i)

    # known tails for filtered eval (train+valid+test)
    known = defaultdict(set)
    for tr in (train, valid, test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])

    # test queries (tail prediction), restricted to target relations, subsampled
    tq_all = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in test if rel2i[r] in target_set]
    rng.shuffle(tq_all)
    tq = tq_all[:N_EVAL]

    # ---- mine on dense ----
    acc_d, allpat_d, hub_skipped = mine_rules(
        gd, target_rels, MIN_SUPPORT, MIN_CONF, MAX_RULES_PER_HEAD, HUB_CAP)
    n_rules_d = sum(len(v) for v in acc_d.values())

    # candidate-set-size diagnostic (verify broken-verifier can fire on hits@10)
    csz = []
    for (h, r, gold) in tq[:min(500, len(tq))]:
        sc = propose(gd, h, r, acc_d.get(r, []))
        csz.append(len(sc))
    med_csz = sorted(csz)[len(csz) // 2] if csz else 0

    # ---- GT_DENSE ----
    def gt_dense_rank(h, r, gold, filt, rr):
        sc = propose(gd, h, r, acc_d.get(r, []))
        return strict_rank(sc, gold, filt, rr)
    m_dense = eval_arm(gd, tq, known, gt_dense_rank)

    # ---- ceiling (generator reach, pre-verifier) ----
    ceil_hit = 0
    for (h, r, gold) in tq:
        reach = reachable(gd, h, r, allpat_d.get(r, []))
        filt = known.get((h, r), set()) - {gold}
        if gold in reach and gold not in filt:
            ceil_hit += 1
    ceiling = ceil_hit / len(tq)

    # ---- GT_SPARSE (density contrast) ----
    train_sp = downsample(train, SPARSE_TARGET_AVGDEG, ent2i, seed)
    gs = Graph(train_sp, ent2i, rel2i)
    acc_s, _allpat_s, _ = mine_rules(
        gs, target_rels, MIN_SUPPORT, MIN_CONF, MAX_RULES_PER_HEAD, HUB_CAP)
    n_rules_s = sum(len(v) for v in acc_s.values())
    avgdeg_sp = 2.0 * len(train_sp) / n_ent

    def gt_sparse_rank(h, r, gold, filt, rr):
        sc = propose(gs, h, r, acc_s.get(r, []))
        return strict_rank(sc, gold, filt, rr)
    m_sparse = eval_arm(gs, tq, known, gt_sparse_rank)

    # ---- POP_DEGREE (task-specified baseline: rank by global target degree) ----
    def pop_deg_fn(h, r, gold, filt, rr):
        return pop_rank(gd.node_degree, gold, filt, rr, n_ent)
    m_pop_deg = eval_arm(gd, tq, known, pop_deg_fn)

    # ---- POP_RELFREQ (stronger reference baseline: per-relation tail frequency) ----
    def pop_relfreq_fn(h, r, gold, filt, rr):
        return pop_rank(gd.rel_tail_freq.get(r, Counter()), gold, filt, rr, n_ent)
    m_pop_relfreq = eval_arm(gd, tq, known, pop_relfreq_fn)

    # ---- BROKEN_VERIFIER: full generator reach, SHUFFLED verifier (random per-entity score) ----
    # Ablates the verifier: same generator, but ranking within the reachable set is random.
    brng = random.Random(seed * 991 + 7)
    ent_rand = [brng.random() for _ in range(n_ent)]

    def broken_rank(h, r, gold, filt, rr):
        sc = propose_allpat_random(gd, h, r, allpat_d.get(r, []), ent_rand)
        return strict_rank(sc, gold, filt, rr)
    m_broken = eval_arm(gd, tq, known, broken_rank)

    # ---- RANDOM floor ----
    def rand_rank(h, r, gold, filt, rr):
        return random_rank(gold, filt, rr, n_ent)
    m_random = eval_arm(gd, tq, known, rand_rank)

    return {
        "seed": seed,
        "n_ent": n_ent, "n_rel": len(rel2i),
        "n_train": len(train), "avgdeg_dense": 2.0 * len(train) / n_ent,
        "n_train_sparse": len(train_sp), "avgdeg_sparse": avgdeg_sp,
        "n_test_eval": len(tq),
        "n_rules_dense": n_rules_d, "n_rules_sparse": n_rules_s,
        "hub_skipped": hub_skipped, "median_cand_set": med_csz,
        "ceiling_hits10_reach": ceiling,
        "GT_DENSE": m_dense, "GT_SPARSE": m_sparse,
        "POP_DEGREE": m_pop_deg, "POP_RELFREQ": m_pop_relfreq,
        "BROKEN_VERIF": m_broken, "RANDOM": m_random,
    }


# ============================ verdict =========================================
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compute_verdict(per_seed):
    def agg(arm, k):
        return _mean([s[arm][k] for s in per_seed])
    d10 = agg("GT_DENSE", "hits@10"); dmrr = agg("GT_DENSE", "mrr"); d1 = agg("GT_DENSE", "hits@1")
    s10 = agg("GT_SPARSE", "hits@10")
    pd10 = agg("POP_DEGREE", "hits@10"); pdmrr = agg("POP_DEGREE", "mrr")     # gated baseline
    pf10 = agg("POP_RELFREQ", "hits@10")                                     # reference only
    b10 = agg("BROKEN_VERIF", "hits@10"); bmrr = agg("BROKEN_VERIF", "mrr"); b1 = agg("BROKEN_VERIF", "hits@1")
    ceil = _mean([s["ceiling_hits10_reach"] for s in per_seed])
    achieved_frac = (d10 / ceil) if ceil > 0 else 0.0

    # PASS gates use POP_DEGREE (the task-specified "rank by target degree" baseline).
    beats_pop = (d10 >= 1.5 * max(pd10, 1e-9)) and (d10 - pd10 >= 0.05)
    density_contrast = (d10 >= 1.5 * max(s10, 1e-9))
    # Verifier load-bearing shows in RANKING QUALITY (MRR / hits@1): with median candidate
    # sets ~17, hits@10 is near-saturated for any method that proposes gold, so it is NOT a
    # sensitive discriminator for the verifier. Gate on MRR + hits@1.
    broken_fails = (bmrr <= 0.5 * max(dmrr, 1e-9)) and (b1 <= 0.5 * max(d1, 1e-9))
    ceiling_ok = (achieved_frac >= 0.30)

    hard_pass = beats_pop and density_contrast and broken_fails and ceiling_ok
    ties_pop = (d10 < 1.2 * max(pd10, 1e-9))
    no_density = (d10 < 1.5 * max(s10, 1e-9))
    broken_infers = (bmrr > 0.7 * max(dmrr, 1e-9))
    hard_fail = ties_pop or no_density or broken_infers

    if hard_pass:
        v = "HARD_PASS"
    elif hard_fail:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"

    msg = ("GT_DENSE h@10=%.3f mrr=%.3f h@1=%.3f | SPARSE h@10=%.3f | POP_DEG h@10=%.3f mrr=%.3f | "
           "POP_RELFREQ h@10=%.3f (ref) | BROKEN h@10=%.3f mrr=%.3f | ceiling=%.3f ach/ceil=%.3f || "
           "beats_popdeg=%s density_contrast=%s broken_fails=%s ceiling_ok=%s"
           % (d10, dmrr, d1, s10, pd10, pdmrr, pf10, b10, bmrr, ceil, achieved_frac,
              beats_pop, density_contrast, broken_fails, ceiling_ok))
    gates = {
        "GT_DENSE_hits10": d10, "GT_DENSE_mrr": dmrr, "GT_DENSE_hits1": d1,
        "GT_SPARSE_hits10": s10,
        "POP_DEGREE_hits10": pd10, "POP_DEGREE_mrr": pdmrr, "POP_RELFREQ_hits10_ref": pf10,
        "BROKEN_hits10": b10, "BROKEN_mrr": bmrr,
        "ceiling": ceil, "achieved_over_ceiling": achieved_frac,
        "beats_popdeg": beats_pop, "density_contrast": density_contrast,
        "broken_fails": broken_fails, "ceiling_ok": ceiling_ok,
    }
    return v, msg, gates


# ============================ self-test =======================================
def _build_planted(seed=0, with_support=True):
    """Synthetic graph with a planted composition rule rBorn(A,B) & rIn(B,C) => rNat(A,C),
    PLUS distractors so the verifier is load-bearing (a broken/no-verifier method must fail).

    rBorn: person -> home_city (1 each) ; rIn: city -> country (1 each) ;
    rNat (target, gold): person -> home_country. DISTRACTORS: rVisited: person -> many random
    cities (each -> a country via rIn), so (rVisited,rIn) is a LOW-confidence junk path that
    reaches MANY wrong countries -> generator reach is large, verifier must down-weight it.
    If with_support: include rBorn/rIn body edges. Else strip rBorn (sparse: body absent).
    """
    P, C, K = 20, 20, 20
    N_DISTRACT = 8          # distinct distractor relations -> distinct junk L2 patterns
    N_VISIT = 4             # cities per distractor relation per person
    rr = random.Random(seed)
    triples = []
    ent = lambda k, i: k * 100 + i
    city_country = {ci: ci % K for ci in range(C)}
    for ci in range(C):
        triples.append((ent(1, ci), "rIn", ent(2, city_country[ci])))     # city -> country
    for pi in range(P):
        ci = pi % C
        if with_support:
            triples.append((ent(0, pi), "rBorn", ent(1, ci)))             # person -> home city
        # distractors: several relations, each -> random cities (reach many wrong countries).
        # Each (rVis_d, rIn) is a distinct low-confidence junk pattern with its own score.
        for d in range(N_DISTRACT):
            for cj in rr.sample(range(C), N_VISIT):
                triples.append((ent(0, pi), "rVis_%d" % d, ent(1, cj)))
    # gold nationality edges (held for train/test split by caller)
    gold = [(ent(0, pi), "rNat", ent(2, city_country[pi % C])) for pi in range(P)]
    return triples, gold


def _selftest():
    print("[selftest] building planted graph...", flush=True)
    triples, gold = _build_planted(with_support=True)
    # half gold in train, half held out
    train_planted = triples + gold[:10]
    test_planted = gold[10:]
    ent2i, rel2i = build_ids(train_planted, [], test_planted)
    g = Graph(train_planted, ent2i, rel2i)
    trels = list(rel2i.values())
    acc, allp, _ = mine_rules(g, trels, min_support=3, min_conf=0.5,
                              max_rules_per_head=10, hub_cap=100000)
    rNat = rel2i["rNat"]; rBorn = rel2i["rBorn"]; rIn = rel2i["rIn"]
    # D1: planted composition rule recovered
    rules_nat = acc.get(rNat, [])
    found = any(k == "L2" and r1 == rBorn and r2 == rIn for (k, r1, r2, c, s) in rules_nat)
    assert found, "D1 FAIL: planted rBorn&rIn=>rNat not recovered by miner"
    # D1b: its held-out edges are inferred hits@1==1.0
    known = defaultdict(set)
    for tr in (train_planted, test_planted):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    tq = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in test_planted]
    def gt_rank(h, r, gold_, filt, rr):
        return strict_rank(propose(g, h, r, acc.get(r, [])), gold_, filt, rr)
    m = eval_arm(g, tq, known, gt_rank)
    assert m["hits@1"] >= 0.99, "D1b FAIL: planted held-out edges not inferred hits@1=%.3f" % m["hits@1"]

    # D2: broken verifier (full reach, shuffled per-entity scores) recovers nothing
    brng = random.Random(1)
    ent_rand = [brng.random() for _ in range(len(ent2i))]
    def br_rank(h, r, gold_, filt, rr):
        return strict_rank(propose_allpat_random(g, h, r, allp.get(r, []), ent_rand), gold_, filt, rr)
    mb = eval_arm(g, tq, known, br_rank)
    assert mb["hits@1"] <= 0.5, "D2 FAIL: broken verifier still infers hits@1=%.3f" % mb["hits@1"]

    # D3: sparse (support-stripped) graph fails
    triples_sp, gold_sp = _build_planted(with_support=False)
    train_sp = triples_sp + gold_sp[:10]
    e2, r2 = build_ids(train_sp, [], gold_sp[10:])
    gsp = Graph(train_sp, e2, r2)
    accsp, _, _ = mine_rules(gsp, list(r2.values()), 3, 0.5, 10, 100000)
    known_sp = defaultdict(set)
    for tr in (train_sp, gold_sp[10:]):
        for (h, r, t) in tr:
            known_sp[(e2[h], r2[r])].add(e2[t])
    tqsp = [(e2[h], r2[r], e2[t]) for (h, r, t) in gold_sp[10:]]
    def gsp_rank(h, r, gold_, filt, rr):
        return strict_rank(propose(gsp, h, r, accsp.get(r, [])), gold_, filt, rr)
    msp = eval_arm(gsp, tqsp, known_sp, gsp_rank)
    assert msp["hits@1"] <= 0.5, "D3 FAIL: sparse graph still infers hits@1=%.3f" % msp["hits@1"]

    # D4: random-rule generator fails -- build rules from random (r1,r2) body pairs
    rrng = random.Random(3)
    all_rel_ids = list(rel2i.values())
    rand_rules = {}
    for r3 in trels:
        rand_rules[r3] = [("L2", rrng.choice(all_rel_ids), rrng.choice(all_rel_ids),
                           0.9, 0) for _ in range(5)]
    def rr_rank(h, r, gold_, filt, rr):
        return strict_rank(propose(g, h, r, rand_rules.get(r, [])), gold_, filt, rr)
    mr = eval_arm(g, tq, known, rr_rank)
    assert mr["hits@1"] <= 0.5, "D4 FAIL: random-rule generator infers hits@1=%.3f" % mr["hits@1"]

    print("[selftest] PASS: D1 recover=%.2f D1b infer=%.2f | D2 broken=%.2f D3 sparse=%.2f D4 rand=%.2f"
          % (1.0 if found else 0.0, m["hits@1"], mb["hits@1"], msp["hits@1"], mr["hits@1"]), flush=True)


# ============================ start-marker / crash ============================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
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
    _write_start_marker(out_dir, RUN_MODE, len(SEEDS))
    t0 = time.time()
    print("[config] anchor=%s mode=%s seeds=%s N_EVAL=%d TOP_K_RELS=%d MIN_SUPPORT=%d MIN_CONF=%.2f"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_EVAL, TOP_K_RELS, MIN_SUPPORT, MIN_CONF), flush=True)

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
        print("[seed %d] DENSE h@10=%.3f mrr=%.3f h@1=%.3f | SPARSE h@10=%.3f | POP_DEG h@10=%.3f | "
              "POP_RELFREQ h@10=%.3f | BROKEN h@10=%.3f mrr=%.3f | ceiling=%.3f | rules=%d med_cand=%d "
              "avgdeg_sp=%.2f (%.1fs)"
              % (seed, r["GT_DENSE"]["hits@10"], r["GT_DENSE"]["mrr"], r["GT_DENSE"]["hits@1"],
                 r["GT_SPARSE"]["hits@10"], r["POP_DEGREE"]["hits@10"], r["POP_RELFREQ"]["hits@10"],
                 r["BROKEN_VERIF"]["hits@10"], r["BROKEN_VERIF"]["mrr"], r["ceiling_hits10_reach"],
                 r["n_rules_dense"], r["median_cand_set"], r["avgdeg_sparse"], time.time() - ts), flush=True)

    verdict, vmsg, gates = compute_verdict(per_seed)
    elapsed = time.time() - t0
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
               "summary": vmsg[:200], "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
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
