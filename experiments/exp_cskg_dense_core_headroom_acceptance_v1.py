"""
cskg_dense_core_headroom_acceptance_v1 -- FAIRNESS / HEADROOM ACCEPTANCE TEST for the CSKG dense
commonsense core, BEFORE committing to build a reasoning engine on it.

WHY. The fairness VET (aa7f151f) proved FB15k-237's aggregate "beat frequency" bar is UNFAIR: its
high-degree hub tails are FREQUENCY-GUESSABLE by construction -- POP hits@10 saturates/exceeds the
reasoning reach-ceiling at the hub end, so NO path-reasoner can beat frequency where the answer just IS
the popular tail. The VET's own degree-tertile HEADROOM table on FB15k-237 (reachable-by-composition AND
pop-misses-top-10) collapses at high degree:
    CITED@notes VET table (FB15k-237): LOW 0.320  MID 0.299  HIGH 0.027  ALL 0.011.
A FAIR reasoning testbed must have DERIVABLE held-out relations where frequency does NOT saturate the
info-ceiling ACROSS degree strata, INCLUDING at higher degree. This cell MEASURES whether the CSKG
cross-cutting dense commonsense core (12-core, ~23.6k nodes @ avg-deg 38, per the density gate) is such a
testbed -- it does NOT assume CSKG is better; it runs the SAME headroom apparatus and reports the CSKG
degree-tertile table SIDE-BY-SIDE with FB15k-237's.

APPARATUS (reused, apples-to-apples). Imports the FB15k-237 STEP-1 cell's OWN Graph / mine_rules /
reachable / pop_rank so the CSKG numbers use the identical code path as the VET's FB15k-237 numbers.
For each held-out test edge (h, r, gold), stratified by GLOBAL degree tertile of the gold TAIL:
  - reach-ceiling  = frac where gold is REACHABLE by ANY mined L1/L2 body pattern (pre-verifier) and not
                     in the filtered-known set  (max hits a perfect reasoner could achieve).
  - POP_RELFREQ    = frac where per-relation tail-frequency ranks gold in top-10 (the frequency baseline).
  - HEADROOM       = frac where gold is REACHABLE by composition BUT POP misses top-10
                     (= the additional hits@10 a perfect reasoning ranker could WIN over frequency).

ARMS / CORPORA (each run through the IDENTICAL headroom apparatus):
  1. CSKG_XCUT_CORE  -- CSKG cross-cutting commonsense subgraph, restricted to its k=12 dense core
                        (CITED@notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md), random
                        90/5/5 edge split. THE CANDIDATE.
  2. FB15K237        -- full FB15k-237 standard split (the VET's corpus). Reproduces the VET table as a
                        POSITIVE-CONTROL / real-corpus MUST-FAIL witness (its HIGH stratum must collapse).
  3. SYN_COMPOSITIONAL  -- synthetic planted-composition corpus with UNIFORM (non-popular) tails: gold is
                        reachable-by-composition but NOT frequency-guessable. Analytically headroom-HIGH
                        at ANY scale. POSITIVE control (apparatus detects reasoning headroom).
  4. SYN_FREQ_GUESSABLE -- synthetic corpus where the gold tail IS the single dominant popular tail of its
                        relation (reachable, but frequency already ranks it #1). Analytically headroom~0
                        at ANY scale. MUST-FAIL control (apparatus reports NO headroom where freq saturates
                        -- the FB15k-237 hub failure mode, isolated and scale-invariant).

FAIRNESS GATE (the test discriminates good-vs-bad reasoning corpora, does NOT auto-pass): SYN_FREQ_
GUESSABLE (and FB15k-237's HIGH stratum) must show ~NO headroom under the same apparatus, while SYN_
COMPOSITIONAL shows LARGE headroom. If the freq-guessable control shows headroom, the apparatus is broken
and the CSKG result is INCONCLUSIVE.

DECISION (pre-registered; see prereg for exact bands):
  ACCEPT     = CSKG shows MATERIAL headroom across strata INCLUDING higher degree (HIGH >= 0.10, all strata
               >= 0.05) AND the must-fail control FIRES (SYN_FREQ_GUESSABLE <= 0.02, SYN_COMPOSITIONAL
               >= 0.15) AND FB15k-237's HIGH stratum reproduces its hub-collapse (<= 0.10).
  REJECT     = CSKG HIGH < 0.05 (freq saturates hubs like FB15k-237 -> unfair at high degree) OR any CSKG
               stratum < 0.02 (no reasoning reach) OR the must-fail control does NOT fire (apparatus
               broken -> INCONCLUSIVE, not acceptance).
  MIDDLE_BAND = otherwise (e.g. CSKG HIGH in [0.05, 0.10)).

## Compute architecture
Class (b) sequential-CPU with justification: pure symbolic relational hash-joins + dict lookups
(mine_rules L2 path composition, reachable-set traversal, filtered ranking). NO substrate vectors, NO
bind/unbind, NO matmul -- GPU batching does not apply (combinatorial graph traversal, not linear algebra).
Same justification as the imported FB15k-237 STEP-1 cell. Storage strategy: no_storage / no_composition
(no substrate vectors are stored or composed). k-core decomposition is an iterative degree-peel (linear
in edges).

ASCII-only. write_metrics. RUN_MODE defaults to full (runner invokes with no argv). --smoke small local
slice (assembly + apparatus validation only); --self-test runs the scale-invariant discriminators.
"""
from __future__ import annotations
import sys, os, argparse, time, json, gzip, random, traceback, platform, subprocess, hashlib
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
# APPARATUS REUSE (apples-to-apples with the FB15k-237 VET; identical code path).
from experiments.exp_gt_induction_fb15k237_dense_v1 import (
    Graph, build_ids, mine_rules, reachable, pop_rank, _load_fb15k237,
)

ANCHOR_NAME = "cskg_dense_core_headroom_acceptance_v1"
TESTBED = REPO / "data" / "grounding_testbed"
CSKG_PATH = TESTBED / "cskg.tsv.gz"
CSKG_URL = "https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content"

# ---- run mode / config -------------------------------------------------------
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Rule-mining / verifier params -- MATCHED to the FB15k-237 FULL regime (calibration_check:
# default_ok_for_this_regime; the same MIN_SUPPORT/MIN_CONF the VET used, so reach-ceiling is comparable).
MIN_SUPPORT = 10
MIN_CONF = 0.10
MAX_RULES_PER_HEAD = 50
HUB_CAP = 60000
K_CORE = 12                 # CITED@notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md (dense band)

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_EVAL = 150
    CSKG_MAX_LINES = 150000     # stream only a small slice (assembly + apparatus proof; NOT the full core)
    K_CORE = 2                  # a tiny slice cannot sustain a 12-core; low-k just proves assembly
    CSKG_MAX_NODES = 1200
    MIN_SUPPORT = 3
    RUN_FB = False              # FB15k-237 full-scale reproduction is a FULL-only concern
else:
    SEEDS = [7, 17, 23]
    N_EVAL = 3000
    CSKG_MAX_LINES = 0          # 0 = stream the whole graph
    CSKG_MAX_NODES = 0          # 0 = keep the whole k-core
    RUN_FB = True

HITS_K = 10

# ---- CROSS-CUTTING commonsense relation set (CITED@notes/cskg_commonsense_core_kcore_density_gate sec.3):
#      the 20.9% commonsense SPINE; strips the 79.1% lexical/taxonomic dilution. Match on relation-label
#      suffix (case-insensitive substring). Copied inline (self-contained; do NOT import the reach cell). ----
XCUT_REL_TOKENS = [
    "xattr", "xwant", "xeffect", "xneed", "xreact", "xintent", "owant", "oeffect", "oreact",
    "locatednear", "mayhaveproperty", "usedfor", "capableof", "partof", "atlocation", "hassubevent",
    "hasprerequisite", "causes", "hasa", "mannerof", "motivatedbygoal", "hasproperty", "receivesaction",
    "causesdesire", "desires", "madeof", "createdby", "entails", "hasfirstsubevent", "haslastsubevent",
    "notdesires", "obstructedby",
]
LEXICAL_REL_TOKENS = [
    "relatedto", "synonym", "antonym", "formof", "derivedfrom", "isa", "hascontext", "haslexicalunit",
    "etymologicallyrelatedto", "similarto", "distinctfrom", "definedas", "instanceof", "sameas", "dbpedia",
]


def _norm_word(w):
    return str(w).strip().lower().replace("_", " ")


def _rel_token(rel_label):
    """Return the canonical cross-cutting relation token for a CSKG relation label, or None if lexical/other."""
    r = rel_label.lower()
    for tok in LEXICAL_REL_TOKENS:
        if tok in r:
            return None
    for tok in XCUT_REL_TOKENS:
        if tok in r:
            return tok
    return None


# ============================ CSKG ingest =====================================
def _ensure_cskg():
    if CSKG_PATH.exists():
        return True
    try:
        os.makedirs(str(TESTBED), exist_ok=True)
        tmp = str(CSKG_PATH) + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "1800", "-o", tmp, CSKG_URL], check=True)
        if os.path.getsize(tmp) < 50_000_000:
            os.remove(tmp)
            return False
        os.replace(tmp, str(CSKG_PATH))
        return True
    except Exception as e:
        print("[cskg] self-acquire failed: %s: %s" % (type(e).__name__, str(e)[:150]), flush=True)
        return False


def _iter_cskg_triples(max_lines=0):
    """Yield (word1, rel_token, word2) for CROSS-CUTTING commonsense edges from cskg.tsv.gz.
    Columns: id node1 relation node2 node1;label node2;label relation;label relation;dimension source sentence."""
    with gzip.open(str(CSKG_PATH), "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            i_rel = header.index("relation")
            i_l1 = header.index("node1;label")
            i_l2 = header.index("node2;label")
        except ValueError:
            i_rel, i_l1, i_l2 = 2, 4, 5
        n = 0
        for line in f:
            n += 1
            if max_lines and n > max_lines:
                break
            p = line.rstrip("\n").split("\t")
            if len(p) <= max(i_rel, i_l1, i_l2):
                continue
            rk = _rel_token(p[i_rel])
            if rk is None:
                continue
            w1 = _norm_word(p[i_l1].split("|")[0])
            w2 = _norm_word(p[i_l2].split("|")[0])
            if w1 and w2 and w1 != w2:
                yield (w1, rk, w2)


def _kcore_nodes(edges, k):
    """Iterative degree-peel k-core on the SIMPLE UNDIRECTED graph of edges [(w1,rel,w2)].
    Returns the set of node labels in the k-core (matches the density-gate note's core definition)."""
    adj = defaultdict(set)
    for (w1, _r, w2) in edges:
        adj[w1].add(w2)
        adj[w2].add(w1)
    deg = {u: len(nb) for u, nb in adj.items()}
    # repeatedly remove nodes with degree < k
    changed = True
    alive = set(deg.keys())
    while changed:
        changed = False
        to_remove = [u for u in alive if deg[u] < k]
        if to_remove:
            changed = True
            for u in to_remove:
                alive.discard(u)
                for v in adj[u]:
                    if v in alive:
                        deg[v] -= 1
                deg[u] = 0
    return alive


def _dedupe_canonical(edges):
    """Dedupe exact directed relational triples into a PROCESS-INVARIANT canonical order.
    sorted() (NOT list(set(...))) makes the downstream seeded shuffle + 5/5/90 split a pure deterministic
    function of (config, seed), so separate cells/processes (map-builder / comparator) reconstruct the
    bit-identical held-out split. list(set(string_tuples)) is ordered by the per-process PYTHONHASHSEED
    (unpinned) -> a bare list() made rng.shuffle(seed) yield a DIFFERENT permutation each process -> a
    genuinely different held-out edge subset every run (the 2026-07-11 split-identity-breach root cause;
    empirically: PYTHONHASHSEED=1 vs =2 give different test partitions with list(), identical with sorted()).
    Keep this the SINGLE dedupe path so the comparator's split-determinism self-guard tests the real
    primitive (no copy-drift)."""
    return sorted({(w1, r, w2) for (w1, r, w2) in edges})


def build_cskg_core_triples(max_lines, k_core, max_nodes, seed):
    """Stream CSKG -> cross-cutting edges -> k-core node set -> induced triples -> 90/5/5 split.
    Returns (train, valid, test, prov). Each triple is (head_label, rel_token, tail_label)."""
    edges = list(_iter_cskg_triples(max_lines))
    core = _kcore_nodes(edges, k_core)
    if max_nodes and len(core) > max_nodes:
        rng0 = random.Random(seed)
        core = set(rng0.sample(sorted(core), max_nodes))
    core_edges = [(w1, r, w2) for (w1, r, w2) in edges if w1 in core and w2 in core]
    core_edges = _dedupe_canonical(core_edges)   # process-invariant canonical order (split-identity fix)
    rng = random.Random(seed)
    rng.shuffle(core_edges)
    n = len(core_edges)
    n_test = max(1, int(0.05 * n))
    n_valid = max(1, int(0.05 * n))
    test = core_edges[:n_test]
    valid = core_edges[n_test:n_test + n_valid]
    train = core_edges[n_test + n_valid:]
    nodes = set()
    for (w1, _r, w2) in core_edges:
        nodes.add(w1); nodes.add(w2)
    avgdeg = (2.0 * n / max(1, len(nodes)))
    prov = dict(n_xcut_edges_streamed=len(edges), k_core=k_core, n_core_nodes=len(core),
                n_core_edges=n, n_core_nodes_in_split=len(nodes), core_avgdeg=avgdeg,
                n_train=len(train), n_valid=len(valid), n_test=len(test),
                n_rel_tokens=len({r for (_a, r, _b) in core_edges}))
    return train, valid, test, prov


# ============================ synthetic controls ==============================
def build_syn_compositional(seed, n_person=400, n_tail=60, n_distract=6):
    """Planted rule rA(p,m) & rB(m,t) => rC(p,t), tails UNIFORM (non-popular). gold reachable-by-
    composition but NOT frequency-guessable -> headroom analytically HIGH at any scale. Distractor
    relations add junk reach so freq/reach differ. Returns (train, valid, test)."""
    rr = random.Random(seed)
    P = ["p%d" % i for i in range(n_person)]
    M = ["m%d" % i for i in range(n_tail)]     # one middle per tail (bijective m_i -> t_i)
    T = ["t%d" % i for i in range(n_tail)]
    train = []
    gold = []
    for i, p in enumerate(P):
        ti = rr.randrange(n_tail)              # uniform tail assignment (no popular tail)
        m = M[ti]; t = T[ti]
        train.append((p, "rA", m))             # p -> m
        train.append((m, "rB", t))             # m -> t   (shared across persons w/ same tail)
        gold.append((p, "rC", t))              # target (person -> tail), held out below
        # distractors: p -> several random middles (junk reach through rB to wrong tails)
        for _d in range(n_distract):
            mj = M[rr.randrange(n_tail)]
            train.append((p, "rVis", mj))
    # ensure rB edges deduped
    train = list({e for e in train})
    rr.shuffle(gold)
    n_test = max(1, int(0.5 * len(gold)))
    test = gold[:n_test]
    train = train + gold[n_test:]              # half the rC edges in train (so rule is minable)
    valid = []
    return train, valid, test


def build_syn_freq_guessable(seed, n_person=400, n_tail=60):
    """gold tail IS the single dominant popular tail T* of its relation: reachable (planted rule) but
    frequency already ranks it #1 -> headroom analytically ~0 at any scale (the FB15k-237 hub failure
    mode, isolated). Returns (train, valid, test)."""
    rr = random.Random(seed)
    P = ["p%d" % i for i in range(n_person)]
    Tstar = "TSTAR"
    m0 = "mstar"
    train = []
    gold = []
    for p in P:
        train.append((p, "rA", m0))            # every person -> the single middle
        gold.append((p, "rC", Tstar))          # every gold tail = the single popular tail
    train.append((m0, "rB", Tstar))            # middle -> popular tail (planted rule reaches T*)
    train = list({e for e in train})
    rr.shuffle(gold)
    n_test = max(1, int(0.5 * len(gold)))
    test = gold[:n_test]
    train = train + gold[n_test:]              # rest of rC edges in train (all tail = T* -> freq #1)
    valid = []
    return train, valid, test


# ============================ headroom apparatus ==============================
def headroom_table(train, valid, test, corpus_name, n_eval, seed, min_support):
    """Run the IDENTICAL reach-ceiling / POP_RELFREQ / HEADROOM apparatus, stratified by gold-tail
    global-degree tertile. Reuses the FB15k-237 cell's Graph / mine_rules / reachable / pop_rank."""
    ent2i, rel2i = build_ids(train, valid, test)
    n_ent = len(ent2i)
    g = Graph(train, ent2i, rel2i)             # mine on TRAIN only
    target_rels = list(rel2i.values())
    known = defaultdict(set)
    for tr in (train, valid, test):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    _acc, allpat, _hub = mine_rules(g, target_rels, min_support, MIN_CONF, MAX_RULES_PER_HEAD, HUB_CAP)

    tq_all = [(ent2i[h], rel2i[r], ent2i[t]) for (h, r, t) in test]
    rng = random.Random(seed)
    rng.shuffle(tq_all)
    tq = tq_all[:n_eval] if n_eval else tq_all
    if not tq:
        return {"corpus": corpus_name, "n_test_eval": 0, "empty": True}

    # tail-degree tertile bounds (global node degree of GOLD tail on the mined train graph)
    degs = sorted(g.node_degree.get(gold, 0) for (_h, _r, gold) in tq)
    q1 = degs[len(degs) // 3]
    q2 = degs[2 * len(degs) // 3]

    def tert(d):
        return "low" if d <= q1 else ("high" if d > q2 else "mid")

    rrng = random.Random(12345)
    strat = defaultdict(lambda: {"n": 0, "reach": 0, "pop_h10": 0, "headroom": 0})
    for (h, r, gold) in tq:
        filt = known.get((h, r), set()) - {gold}
        st = tert(g.node_degree.get(gold, 0))
        s = strat[st]; s["n"] += 1
        reach = reachable(g, h, r, allpat.get(r, []))
        reachable_hit = (gold in reach) and (gold not in filt)
        if reachable_hit:
            s["reach"] += 1
        prank = pop_rank(g.rel_tail_freq.get(r, Counter()), gold, filt, rrng, n_ent)
        pop_hit = prank is not None and prank <= HITS_K
        if pop_hit:
            s["pop_h10"] += 1
        if reachable_hit and not pop_hit:
            s["headroom"] += 1

    out = {"corpus": corpus_name, "n_test_eval": len(tq), "n_ent": n_ent, "n_rel": len(rel2i),
           "tert_q1": q1, "tert_q2": q2, "strata": {}}
    tot = {"n": 0, "reach": 0, "pop_h10": 0, "headroom": 0}
    for st in ["low", "mid", "high"]:
        s = strat[st]; nn = max(s["n"], 1)
        for k in tot:
            tot[k] += s[k]
        out["strata"][st] = {"n": s["n"], "reach_ceiling": s["reach"] / nn,
                             "pop_relfreq_h10": s["pop_h10"] / nn, "headroom": s["headroom"] / nn}
    nn = max(tot["n"], 1)
    out["strata"]["all"] = {"n": tot["n"], "reach_ceiling": tot["reach"] / nn,
                            "pop_relfreq_h10": tot["pop_h10"] / nn, "headroom": tot["headroom"] / nn}
    return out


def _table_digest(tbl):
    """Deterministic hash of a headroom table's per-stratum headroom values (for ARMS-MUST-DIFFER)."""
    if tbl.get("empty"):
        return hashlib.sha256(b"empty").hexdigest()
    vals = [round(tbl["strata"][st]["headroom"], 4) for st in ["low", "mid", "high", "all"]]
    return hashlib.sha256(json.dumps(vals).encode()).hexdigest()


def _mean_strata(tables):
    """Mean per-stratum headroom/ceiling/pop across a list of per-seed tables (same corpus)."""
    out = {}
    for st in ["low", "mid", "high", "all"]:
        for metric in ["reach_ceiling", "pop_relfreq_h10", "headroom", "n"]:
            vals = [t["strata"][st][metric] for t in tables if not t.get("empty")]
            out.setdefault(st, {})[metric] = (sum(vals) / len(vals)) if vals else 0.0
    return out


# ============================ verdict =========================================
def compute_verdict(cskg_mean, fb_mean, syn_comp, syn_freq):
    ck = cskg_mean
    h_low = ck["low"]["headroom"]; h_mid = ck["mid"]["headroom"]
    h_high = ck["high"]["headroom"]; h_all = ck["all"]["headroom"]
    h_min = min(h_low, h_mid, h_high)

    syn_comp_h = syn_comp["strata"]["all"]["headroom"]
    syn_freq_h = syn_freq["strata"]["all"]["headroom"]
    control_fires = (syn_freq_h <= 0.02) and (syn_comp_h >= 0.15)

    fb_high = fb_mean["high"]["headroom"] if fb_mean else None
    fb_reproduces = True if fb_mean is None else (fb_high <= 0.10)

    material_cross_strata = (h_high >= 0.10) and (h_min >= 0.05)
    reject_hub_saturates = (h_high < 0.05)
    reject_no_reach = (h_min < 0.02)
    reject_control_broken = not control_fires

    if reject_control_broken or reject_hub_saturates or reject_no_reach:
        v = "REJECT"
    elif material_cross_strata and control_fires and fb_reproduces:
        v = "ACCEPT"
    else:
        v = "MIDDLE_BAND"

    gates = {
        "cskg_headroom_low": h_low, "cskg_headroom_mid": h_mid, "cskg_headroom_high": h_high,
        "cskg_headroom_all": h_all, "cskg_headroom_min": h_min,
        "syn_compositional_headroom": syn_comp_h, "syn_freq_guessable_headroom": syn_freq_h,
        "control_fires": control_fires, "fb15k237_high_headroom": fb_high, "fb_reproduces_collapse": fb_reproduces,
        "material_cross_strata": material_cross_strata,
    }
    msg = ("CSKG headroom LOW=%.3f MID=%.3f HIGH=%.3f ALL=%.3f | FB15k-237 HIGH=%s | "
           "control[SYN_COMP=%.3f SYN_FREQ=%.3f fires=%s] || material_cross_strata=%s fb_collapse=%s :: %s"
           % (h_low, h_mid, h_high, h_all,
              ("%.3f" % fb_high) if fb_high is not None else "n/a",
              syn_comp_h, syn_freq_h, control_fires, material_cross_strata, fb_reproduces, v))
    return v, msg, gates


# ============================ self-test =======================================
def _selftest():
    print("[selftest] scale-invariant synthetic discriminators...", flush=True)
    tc_train, tc_v, tc_test = build_syn_compositional(seed=0, n_person=200, n_tail=50)
    tc = headroom_table(tc_train, tc_v, tc_test, "SYN_COMPOSITIONAL", 0, 0, 3)
    comp_h = tc["strata"]["all"]["headroom"]; comp_reach = tc["strata"]["all"]["reach_ceiling"]
    assert comp_reach >= 0.8, "D1 FAIL: compositional gold not reachable (ceiling=%.3f)" % comp_reach
    assert comp_h >= 0.15, "D1 FAIL: compositional headroom too low (%.3f); apparatus misses reasoning reach" % comp_h

    tf_train, tf_v, tf_test = build_syn_freq_guessable(seed=0, n_person=200)
    tf = headroom_table(tf_train, tf_v, tf_test, "SYN_FREQ_GUESSABLE", 0, 0, 3)
    freq_h = tf["strata"]["all"]["headroom"]; freq_reach = tf["strata"]["all"]["reach_ceiling"]
    assert freq_reach >= 0.8, "D2 FAIL: freq-guessable gold not reachable (ceiling=%.3f) -> vacuous not saturated" % freq_reach
    assert freq_h <= 0.02, "D2 FAIL: freq-guessable shows headroom (%.3f); must-fail control did NOT fire" % freq_h

    # D3: arms differ (the two synthetic tables must not be bit-identical)
    assert _table_digest(tc) != _table_digest(tf), "D3 FAIL: SYN arms bit-identical"
    print("[selftest] PASS: SYN_COMP headroom=%.3f reach=%.3f | SYN_FREQ headroom=%.3f reach=%.3f (control fires)"
          % (comp_h, comp_reach, freq_h, freq_reach), flush=True)


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
    _write_start_marker(out_dir, RUN_MODE, len(SEEDS))
    t0 = time.time()
    print("[config] anchor=%s mode=%s seeds=%s N_EVAL=%d K_CORE=%d MIN_SUPPORT=%d RUN_FB=%s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_EVAL, K_CORE, MIN_SUPPORT, RUN_FB), flush=True)
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.time() - t0}) + "\n")

    # ---- scale-invariant synthetic controls (single build; seed 7) ----
    sc_train, sc_v, sc_test = build_syn_compositional(seed=7)
    syn_comp = headroom_table(sc_train, sc_v, sc_test, "SYN_COMPOSITIONAL", 0, 7, MIN_SUPPORT)
    sf_train, sf_v, sf_test = build_syn_freq_guessable(seed=7)
    syn_freq = headroom_table(sf_train, sf_v, sf_test, "SYN_FREQ_GUESSABLE", 0, 7, MIN_SUPPORT)
    print("[control] SYN_COMPOSITIONAL headroom_all=%.3f reach=%.3f | SYN_FREQ_GUESSABLE headroom_all=%.3f reach=%.3f"
          % (syn_comp["strata"]["all"]["headroom"], syn_comp["strata"]["all"]["reach_ceiling"],
             syn_freq["strata"]["all"]["headroom"], syn_freq["strata"]["all"]["reach_ceiling"]), flush=True)
    _hb("controls", 0)

    # ---- CSKG cross-cutting dense core (per seed: independent 90/5/5 split) ----
    if not _ensure_cskg():
        raise RuntimeError("CSKG data absent and self-acquire failed (need %s)" % CSKG_PATH)
    cskg_tables = []
    cskg_prov = None
    for si, seed in enumerate(SEEDS):
        ts = time.time()
        train, valid, test, prov = build_cskg_core_triples(CSKG_MAX_LINES, K_CORE, CSKG_MAX_NODES, seed)
        cskg_prov = prov
        print("[cskg seed=%d] core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d train=%d test=%d"
              % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                 prov["n_rel_tokens"], prov["n_train"], prov["n_test"]), flush=True)
        tbl = headroom_table(train, valid, test, "CSKG_XCUT_CORE", N_EVAL, seed, MIN_SUPPORT)
        cskg_tables.append(tbl)
        s = tbl["strata"]
        print("[cskg seed=%d] headroom LOW=%.3f MID=%.3f HIGH=%.3f ALL=%.3f | ceiling ALL=%.3f pop ALL=%.3f (%.1fs)"
              % (seed, s["low"]["headroom"], s["mid"]["headroom"], s["high"]["headroom"],
                 s["all"]["headroom"], s["all"]["reach_ceiling"], s["all"]["pop_relfreq_h10"],
                 time.time() - ts), flush=True)
        _hb("cskg", si)
    cskg_mean = _mean_strata(cskg_tables)

    # ---- FB15k-237 (positive-control reproducer / real-corpus must-fail witness) ----
    fb_tables = []
    fb_mean = None
    if RUN_FB:
        fb_train, fb_valid, fb_test = _load_fb15k237()
        for si, seed in enumerate(SEEDS):
            ts = time.time()
            tbl = headroom_table(fb_train, fb_valid, fb_test, "FB15K237", N_EVAL, seed, MIN_SUPPORT)
            fb_tables.append(tbl)
            s = tbl["strata"]
            print("[fb15k seed=%d] headroom LOW=%.3f MID=%.3f HIGH=%.3f ALL=%.3f (%.1fs)"
                  % (seed, s["low"]["headroom"], s["mid"]["headroom"], s["high"]["headroom"],
                     s["all"]["headroom"], time.time() - ts), flush=True)
            _hb("fb15k", si)
        fb_mean = _mean_strata(fb_tables)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF): the corpus tables must not be bit-identical ----
    digests = {"CSKG": _table_digest(cskg_tables[0]),
               "SYN_COMPOSITIONAL": _table_digest(syn_comp),
               "SYN_FREQ_GUESSABLE": _table_digest(syn_freq)}
    if RUN_FB:
        digests["FB15K237"] = _table_digest(fb_tables[0])
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], \
                "META_RULE_AF VIOLATION: %s and %s headroom tables bit-identical" % (names[i], names[j])

    verdict, vmsg, gates = compute_verdict(cskg_mean, fb_mean, syn_comp, syn_freq)
    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg[:200],
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed, "gates": gates,
        "arms_differ_verified": True, "table_digests": digests,
        "cskg_mean_strata": cskg_mean, "cskg_per_seed": cskg_tables, "cskg_provenance": cskg_prov,
        "fb15k237_mean_strata": fb_mean, "fb15k237_per_seed": fb_tables,
        "syn_compositional": syn_comp, "syn_freq_guessable": syn_freq,
        "reference_fb_vet_table": {"low": 0.320, "mid": 0.299, "high": 0.027, "all": 0.011,
                                   "source": "CITED@notes VET aa7f151f (FB15k-237 headroom)"},
    }
    write_metrics(out_dir, metrics, cskg_tables)
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
