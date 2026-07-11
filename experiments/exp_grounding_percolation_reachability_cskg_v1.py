"""
grounding_percolation_reachability_cskg_v1 -- SEEDED-REACHABILITY / GROUNDING-PERCOLATION ACCEPTANCE
TEST on the CSKG cross-cutting commonsense core. Pure graph BFS audit. NO training, NO substrate
vectors, NO new data acquisition (all inputs already on disk under data/grounding_testbed/).

QUESTION. Is abstract-concept grounding a PERCOLATION / seeded-reachability property of the ingested
graph? I.e. does a concreteness-ANCHORED seed set S reach the abstract-concept target population A on
the real CSKG cross-cutting graph, AND does the REAL edge structure (not just the degree sequence, not
just seed-set size) carry that reach? Pre-registered design:
  notes/research_grounding_percolation_reachability_cskg_audit_2026-07-11.md ("Cheap decisive test" +
  "Falsifiable predictions"). This cell operationalizes Predictions 1/2/3 verbatim.

WHY THE CONTROLS ARE LOAD-BEARING (not optional). Dense scale-free graphs (degree exponent <= 3, which
commonsense KGs typically are) percolate almost trivially: raw "does S reach A at all" PASSES by
construction for ANY reasonably-sized seed set. So a raw-reachability pass alone is VACUOUS. The
discriminating signal lives in the MUST-FAIL controls:
  Control A -- random-seed-same-graph: same |S|, seeds drawn uniformly over graph nodes, >=20 draws.
              Tests whether GROUNDED (concreteness) seed selection beats an arbitrary seed set of the
              same size (Prediction 2).
  Control B -- grounded-seed-scrambled-graph: same S, same A, on a DEGREE-PRESERVING randomized
              (double-edge-swap / configuration-model) rewiring of the SAME graph, >=20 rewirings.
              Tests whether the REAL edge structure carries reach beyond the degree sequence
              (Prediction 1's non-vacuity requirement -- the Bender-Koller form-without-content control).
  Control C -- kernel/hub seed: same |S|, seeds = highest-DEGREE nodes. Tests whether "most
              topologically central" and "most exogenously grounded/concrete" are the same node
              population or systematically different (Prediction 3; Vincent-Lamarre 2016 dictionary-graph
              finding: core/kernel words are LESS concrete than satellites).

DATA (already on disk; no crawl):
  - CSKG cross-cutting subgraph from data/grounding_testbed/cskg.tsv.gz (Zenodo 4331372), restricted to
    the commonsense SPINE relations (strips the 79% lexical/taxonomic dilution) per
    notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md. BFS graph = largest connected component
    of that cross-cutting simple-undirected graph (dense core PLUS its periphery, for hop-count headroom).
  - Brysbaert, Warriner & Kuperman (2014) concreteness norms (Conc.M, 1=abstract..5=concrete; 39,954
    words) from data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt. EXOGENOUS
    (human-rated) anchor. Joined by lowercased exact label match to CSKG node labels.

PROCEDURE (pure graph computation):
  1. Grounded seed set S = the N_SEED most-concrete covered non-function-word nodes in the LCC.
  2. Abstract target set A = covered non-function-word LCC nodes with Conc.M <= CONC_LOW, disjoint from S.
  3. Multi-source BFS from S over the LCC -> hop-distance from each A node to nearest seed; reach curve
     reach_S[k] = frac of A within <= k hops, k=1..KMAX; median hop-distance.
  4. Control A: repeat step 3 for N_RANDOM_DRAWS random size-|S| seed sets. Distribution.
  5. Control B: repeat step 3 with S/A fixed on N_REWIRES degree-preserving rewirings. Distribution.
  6. Control C: repeat step 3 with S = top-N_SEED highest-degree nodes; report its mean concreteness.

PREDICTIONS / BANDS (pre-registered; see the prereg for the falsifiable-predictions table, lifted here):
  P1 (percolation framing real; CSKG passes where a thin/islanded graph fails, NON-VACUOUSLY):
     HARD-PASS: reach_S(k<=4) >= P1_RAW_REACH_BAR (0.70) AND real structure beats the degree-preserving
                scramble -- median_hop_S strictly below the Control-B rewiring distribution (S median <
                ControlB 5th percentile) so reach is carried by the real edge structure, not just the
                degree sequence.
     HARD-FAIL: reach_S(k<=4) < 0.70 at every k<=KMAX (closed-relational-island failure) OR reach is
                statistically indistinguishable from Control B (form-without-content).
  P2 (grounded seed selection beats generic seed-set size; Control A):
     HARD-PASS: reach_S(k<=2) above the Control-A reach(k<=2) 95th percentile (non/barely overlapping)
                AND median_hop_S < mean Control-A median hop.
     HARD-FAIL: reach_S(k<=2) inside the Control-A [5th,95th] band AND median hop comparable.
  P3 (kernel/hub nodes are NOT the concreteness-anchored population):
     HARD-PASS: mean Conc.M(Control-C hub seeds) <= mean Conc.M(S) - P3_CONC_MARGIN (0.5) AND mean
                Conc.M(hub) < 3.0 (hubs are materially less concrete; centrality != groundedness).
     HARD-FAIL: mean Conc.M(hub) >= mean Conc.M(S) - 0.1 (hubs as concrete as S; centrality is an OK
                grounding proxy).
  Headline verdict tracks P1 (the primary prediction); P2/P3 sub-verdicts reported in gates + verdict_msg.

SELF-TEST (tiny planted graph; deterministic; discriminators must FIRE; exits 0; does NOT touch CSKG):
  (a) BFS correctness: planted grounded->abstract path reachable within its planted hop; a planted ISLAND
      of abstract nodes is UNREACHABLE (dist == -1).
  (b) degree-preserving swap preserves the degree sequence EXACTLY, and destroys the specific short
      grounded->abstract paths -> scrambled reach < real reach (Control B fires).
  (c) grounded (near-target) seeds reach more of the planted targets than random seeds (Control A fires).
  (d) a planted LOW-concreteness hub is caught: hub-seed mean concreteness < anchor-seed mean concreteness
      (Control C / Prediction 3 fires).
  (e) arms differ: reach vectors for S / ControlA / ControlB / ControlC not bit-identical.

## Compute architecture
Class (b) sequential-CPU with justification: pure combinatorial graph traversal (multi-source BFS,
set-guarded double-edge-swap, dict joins). NO substrate vectors, NO bind/unbind, NO matmul, NO torch ->
GPU batching does not apply. BFS neighbourhood-gather is numpy-vectorized (CSR). Storage strategy:
no_storage / no_composition. Routes to remote_cpu_queue (CPU; keeps the laptop free per the
no-local-smokes lock). numpy + stdlib only (parity-safe: same self-contained discipline as
exp_cskg_dense_core_headroom_acceptance_v1, which ran on the remote runner without networkx).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor/cardinality):
  - arms_differ_verified at self-test (>=4 distinct reach-vector sigs: S/ControlA/ControlB/ControlC).
  - final_metrics_atomicity=tmp_replace (write_metrics + crash-writer both tmp+os.replace).
  - except SystemExit: raise BEFORE except Exception; no BaseException.
  - crlb_n/a: no quantitative noise floor -- this is a graph-reachability audit, not an estimator; the
    discriminator is a distribution-separation test (S vs degree-preserving null / random-seed null), and
    the self-test proves the separation is DETECTABLE by construction.
  - baseline_in_band: the "baseline" is the null (Control A / Control B); it must NOT already equal S
    (else no signal) NOR be zero (disconnected). At full scale this is an OPEN MEASUREMENT reported as
    the verdict, not a smoke-abort; the self-test guarantees the machinery CAN detect a real separation.
  - discriminator survives scale (analytical, option B): reach(k<=4) may SATURATE for both S and the
    scramble on a dense graph -- so P1's structural signal uses MEDIAN HOP-DISTANCE (S vs Control B),
    which does NOT saturate for a modest |S|; P2 uses reach(k<=2), also non-saturated for |S|=300 in a
    ~1M-edge LCC (k=1 neighbourhood of 300 seeds covers well under 100% of nodes). Small-k metrics carry
    the resolution.
  - HP bands strictly declared above (P1 raw bar 0.70 + scramble-beat; P2 95th-pct non-overlap; P3 0.5
    concreteness margin).
  - cardinality_ok: EXPECTED control draws = N_RANDOM_DRAWS (Control A) + N_REWIRES (Control B); short
    count -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
  - per-unit failure-class instrumentation (no bare except; specific classes; recorded to metrics).
  - calibration_check=default_ok_for_this_regime (BFS + double-edge-swap are parameter-free apparatus).
  - progress_logging=print_flush_true (all logs flush=True; heartbeat during Control B rewirings).
  - cell_chunked=false (single graph; no per-seed chunking); start_marker + crash_diagnostic present.

ASCII-only. No em dashes in output. RUN_MODE defaults to full (runner invokes with no argv).
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "grounding_percolation_reachability_cskg_v1"
TESTBED = REPO / "data" / "grounding_testbed"
CSKG_PATH = TESTBED / "cskg.tsv.gz"
CSKG_URL = "https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content"
CONC_PATH = TESTBED / "Concreteness_ratings_Brysbaert_et_al_BRM.txt"
CONC_URL = ("https://raw.githubusercontent.com/ArtsEngine/concreteness/master/"
            "Concreteness_ratings_Brysbaert_et_al_BRM.txt")

# ---- run mode / config -------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ---- pre-registered bands (picked BEFORE the run; lifted from the prereg) -----
KMAX = 6                    # report reach curve k=1..KMAX
P1_RAW_REACH_BAR = 0.70     # P1 raw reach floor (matches the 70% grounding-reach threshold in the note)
P1_EVAL_K = 4               # P1 evaluates reach at k<=4
P2_EVAL_K = 2               # P2 evaluates reach at k<=2 (non-saturated small-k resolution)
P3_CONC_MARGIN = 0.5        # P3: hub mean concreteness must be this far BELOW S mean concreteness
P3_HUB_ABS_MAX = 3.0        # P3: hub mean concreteness must be below the mid-scale point
CONC_LOW = 2.5             # abstract target threshold (Conc.M <= this) per the note
MIN_SEEDS = 100             # data-sufficiency floors
MIN_TARGETS = 200

if RUN_MODE == "smoke":
    N_SEED = 40
    N_RANDOM_DRAWS = 5
    N_REWIRES = 5
    SWAP_MULT = 2
    CSKG_MAX_LINES = 250000     # small slice (assembly + apparatus proof; NOT the full graph)
else:
    N_SEED = 300               # modest grounded seed budget -> graded hop-distance in a dense LCC
    N_RANDOM_DRAWS = 20         # Control A draws (>=20 floor)
    N_REWIRES = 20              # Control B rewirings (>=20 floor)
    SWAP_MULT = 3               # double-edge swaps per rewiring = SWAP_MULT * n_edges
    CSKG_MAX_LINES = 0          # 0 = stream the whole graph

# CROSS-CUTTING commonsense relation spine (CITED@notes/cskg_commonsense_core_kcore_density_gate sec.3):
# the 20.9% commonsense SPINE; strips the 79.1% lexical/taxonomic dilution. Copied inline (self-contained).
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

# Function / grammatical words excluded from S and A (Vincent-Lamarre: function words behave differently
# and confound the concrete/abstract contrast). Compact, standard closed-class list.
STOPWORDS = frozenset("""
a an the this that these those and or but nor so yet for as if then than of to in on at by with from
into onto over under above below up down out off about across after before between through during
without within is am are was were be been being do does did done have has had having will would shall
should can could may might must not no yes i you he she it we they me him her us them my your his its
our their mine yours hers ours theirs who whom whose which what where when why how all any both each few
more most other some such only own same very just also too again here there once ever never always
""".split())


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.3f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _norm_word(w):
    return str(w).strip().lower().replace("_", " ")


def _rel_token(rel_label):
    """Canonical cross-cutting relation token for a CSKG relation label, or None if lexical/other."""
    r = rel_label.lower()
    for tok in LEXICAL_REL_TOKENS:
        if tok in r:
            return None
    for tok in XCUT_REL_TOKENS:
        if tok in r:
            return tok
    return None


# ============================ data acquisition ================================
def _ensure_file(path, url, min_bytes, header_needle=None):
    """Self-acquire a public testbed input if absent. Returns True iff present + (optionally) header-valid."""
    if os.path.exists(str(path)):
        return True
    try:
        import subprocess
        os.makedirs(os.path.dirname(str(path)), exist_ok=True)
        tmp = str(path) + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "1800", "-o", tmp, url], check=True)
        if os.path.getsize(tmp) < min_bytes:
            os.remove(tmp)
            return False
        if header_needle is not None:
            with open(tmp, encoding="utf-8", errors="replace") as f:
                if header_needle not in f.readline():
                    os.remove(tmp)
                    return False
        os.replace(tmp, str(path))
        _log("acquired %s" % url)
        return True
    except Exception as e:
        _log("self-acquire failed for %s: %s: %s" % (url, type(e).__name__, str(e)[:150]))
        return False


def load_concreteness_map(path):
    """label(lowercased) -> Conc.M float. Columns: Word Bigram Conc.M Conc.SD ..."""
    conc = {}
    with open(str(path), encoding="utf-8", errors="replace") as f:
        header = f.readline()
        if "Conc.M" not in header:
            raise RuntimeError("concreteness header missing Conc.M: %r" % header[:80])
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3:
                try:
                    conc[p[0].strip().lower()] = float(p[2])
                except (ValueError, IndexError):
                    continue
    return conc


def _iter_cskg_triples(max_lines=0):
    """Yield (word1, word2) for CROSS-CUTTING commonsense edges from cskg.tsv.gz.
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
            if _rel_token(p[i_rel]) is None:
                continue
            w1 = _norm_word(p[i_l1].split("|")[0])
            w2 = _norm_word(p[i_l2].split("|")[0])
            if w1 and w2 and w1 != w2:
                yield (w1, w2)


# ============================ graph primitives ================================
def build_lcc(edge_pairs):
    """edge_pairs: iterable of (label1, label2). Build a simple undirected graph, keep the LARGEST
    connected component. Returns (labels, edges_uv, indptr, indices, deg).
      labels: list[str] node label per index (LCC only)
      edges_uv: int64 [E,2] canonical u<v edge list (LCC only)
      indptr, indices: CSR adjacency (undirected: each edge appears both directions)
      deg: int64 [n] degree
    """
    # dedupe simple undirected edges by canonical (min,max) label tuple
    eset = set()
    for (a, b) in edge_pairs:
        if a == b:
            continue
        e = (a, b) if a < b else (b, a)
        eset.add(e)
    # label -> id
    lab2id = {}

    def _id(w):
        i = lab2id.get(w)
        if i is None:
            i = len(lab2id)
            lab2id[w] = i
        return i

    E = np.empty((len(eset), 2), dtype=np.int64)
    for k, (a, b) in enumerate(eset):
        E[k, 0] = _id(a)
        E[k, 1] = _id(b)
    n_all = len(lab2id)
    id2lab = [None] * n_all
    for w, i in lab2id.items():
        id2lab[i] = w

    # connected components via union-find
    parent = np.arange(n_all, dtype=np.int64)

    def _find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    for k in range(E.shape[0]):
        ra, rb = _find(int(E[k, 0])), _find(int(E[k, 1]))
        if ra != rb:
            parent[ra] = rb
    roots = np.array([_find(i) for i in range(n_all)], dtype=np.int64)
    # largest component
    uniq, counts = np.unique(roots, return_counts=True)
    lcc_root = int(uniq[int(np.argmax(counts))])
    in_lcc = roots == lcc_root
    # remap LCC node ids -> compact 0..m-1
    old_ids = np.where(in_lcc)[0]
    remap = -np.ones(n_all, dtype=np.int64)
    remap[old_ids] = np.arange(old_ids.shape[0], dtype=np.int64)
    labels = [id2lab[int(o)] for o in old_ids]
    keep_e = in_lcc[E[:, 0]] & in_lcc[E[:, 1]]
    Elcc = remap[E[keep_e]]
    # canonical u<v
    lo = np.minimum(Elcc[:, 0], Elcc[:, 1])
    hi = np.maximum(Elcc[:, 0], Elcc[:, 1])
    edges_uv = np.stack([lo, hi], axis=1).astype(np.int64)
    m = len(labels)
    indptr, indices, deg = _csr_from_edges(edges_uv, m)
    return labels, edges_uv, indptr, indices, deg


def _csr_from_edges(edges_uv, n):
    """Undirected CSR from canonical edge list [E,2]. Returns (indptr, indices, deg)."""
    u = edges_uv[:, 0]
    v = edges_uv[:, 1]
    src = np.concatenate([u, v])
    dst = np.concatenate([v, u])
    deg = np.bincount(src, minlength=n).astype(np.int64)
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(deg, out=indptr[1:])
    order = np.argsort(src, kind="stable")
    indices = dst[order].astype(np.int64)
    return indptr, indices, deg


def multi_source_bfs(indptr, indices, seeds, n, kmax):
    """Multi-source BFS. Returns dist int32 [n]: hop-distance to nearest seed, -1 if unreached within kmax."""
    dist = np.full(n, -1, dtype=np.int32)
    seeds = np.asarray(seeds, dtype=np.int64)
    if seeds.size == 0:
        return dist
    dist[seeds] = 0
    frontier = np.unique(seeds)
    for d in range(kmax):
        if frontier.size == 0:
            break
        # vectorized CSR neighbourhood gather over the whole frontier
        counts = (indptr[frontier + 1] - indptr[frontier]).astype(np.int64)
        total = int(counts.sum())
        if total == 0:
            break
        starts = indptr[frontier]
        # offset[i] = starts[repeat] + (i - cumstart[repeat])
        rep_starts = np.repeat(starts, counts)
        cs = np.cumsum(counts) - counts
        rep_cs = np.repeat(cs, counts)
        pos = np.arange(total, dtype=np.int64) - rep_cs
        nbr = indices[rep_starts + pos]
        nbr = np.unique(nbr)
        new_nodes = nbr[dist[nbr] == -1]
        if new_nodes.size == 0:
            break
        dist[new_nodes] = d + 1
        frontier = new_nodes
    return dist


def reach_curve(dist, target_ids, kmax):
    """Reach curve over target set: reach[k] = frac of targets with 0 < dist <= k, for k=1..kmax.
    (dist==0 targets excluded from numerator/denominator? No -- targets are disjoint from seeds by
    construction, so dist>=1 or -1.) Returns (reach list len kmax, median_hop over REACHED targets,
    frac_unreached)."""
    dt = dist[target_ids].astype(np.int64)
    ntar = dt.shape[0]
    reach = []
    for k in range(1, kmax + 1):
        reach.append(float(np.mean((dt >= 1) & (dt <= k))) if ntar else float("nan"))
    reached = dt[dt >= 1]
    median_hop = float(np.median(reached)) if reached.size else float("inf")
    frac_unreached = float(np.mean(dt == -1)) if ntar else float("nan")
    return reach, median_hop, frac_unreached


def degree_preserving_swap(edges_uv, n_swaps, rng):
    """Degree-preserving double-edge swap on canonical edge list [E,2] (u<v). Returns a NEW edge array.
    Preserves the degree sequence EXACTLY. Rejects self-loops and multi-edges. Batched RNG for speed."""
    E = edges_uv.copy()
    m = E.shape[0]
    eset = set(map(tuple, map(tuple, E.tolist())))  # canonical (u,v) with u<v
    done = 0
    batch = 1 << 20
    guard = 0
    max_guard = n_swaps * 20 + batch
    while done < n_swaps and guard < max_guard:
        bi = rng.integers(0, m, size=batch)
        bj = rng.integers(0, m, size=batch)
        bc = rng.random(size=batch) < 0.5
        for t in range(batch):
            guard += 1
            if done >= n_swaps:
                break
            i = int(bi[t])
            j = int(bj[t])
            if i == j:
                continue
            a, b = int(E[i, 0]), int(E[i, 1])
            c, d = int(E[j, 0]), int(E[j, 1])
            if bc[t]:
                p, q, r, s = a, d, c, b   # new edges (a,d),(c,b)
            else:
                p, q, r, s = a, c, b, d   # new edges (a,c),(b,d)
            if p > q:
                p, q = q, p
            if r > s:
                r, s = s, r
            if p == q or r == s:
                continue                  # self-loop
            e1 = (p, q)
            e2 = (r, s)
            if e1 == e2:
                continue
            if e1 in eset or e2 in eset:
                continue                  # multi-edge
            old1 = (a, b) if a < b else (b, a)
            old2 = (c, d) if c < d else (d, c)
            eset.discard(old1)
            eset.discard(old2)
            eset.add(e1)
            eset.add(e2)
            E[i, 0], E[i, 1] = p, q
            E[j, 0], E[j, 1] = r, s
            done += 1
    return E, done


# ============================ seed / target selection =========================
def build_seed_target_sets(labels, deg, conc, n_seed):
    """Join concreteness to LCC labels; build S (top-concreteness), A (abstract targets), hub-seed
    (top-degree). Returns dict with ids + provenance."""
    m = len(labels)
    y = np.full(m, np.nan, dtype=np.float64)
    for i, w in enumerate(labels):
        v = conc.get(w)
        if v is None:
            v = conc.get(w.replace(" ", ""))
        if v is not None:
            y[i] = v
    covered = np.isfinite(y)
    is_stop = np.array([lab in STOPWORDS for lab in labels], dtype=bool)
    eligible = covered & (~is_stop)
    elig_ids = np.where(eligible)[0]

    # S = n_seed most-concrete eligible nodes
    order = elig_ids[np.argsort(-y[elig_ids], kind="stable")]
    seed_S = order[:n_seed].astype(np.int64)
    S_set = set(seed_S.tolist())

    # A = eligible abstract targets (Conc.M <= CONC_LOW), disjoint from S
    abstract_ids = elig_ids[y[elig_ids] <= CONC_LOW]
    target_A = np.array([i for i in abstract_ids.tolist() if i not in S_set], dtype=np.int64)

    # Control C hub seed = top-n_seed highest-degree LCC nodes (kernel/hub; NOT concreteness-selected)
    hub_seed = np.argsort(-deg, kind="stable")[:n_seed].astype(np.int64)

    # degree-concreteness rank relationship over covered nodes (Prediction 3 context)
    cov_ids = np.where(covered)[0]
    if cov_ids.shape[0] >= 10:
        dr = np.argsort(np.argsort(deg[cov_ids].astype(np.float64)))
        cr = np.argsort(np.argsort(y[cov_ids]))
        drc = dr - dr.mean()
        crc = cr - cr.mean()
        denom = float(np.sqrt((drc ** 2).sum() * (crc ** 2).sum()))
        deg_conc_spearman = float((drc * crc).sum() / denom) if denom > 0 else float("nan")
    else:
        deg_conc_spearman = float("nan")

    prov = dict(
        n_lcc=m, n_covered=int(covered.sum()), coverage_frac=float(covered.mean()),
        n_eligible=int(eligible.sum()), n_stop_excluded=int((covered & is_stop).sum()),
        n_seed=int(seed_S.shape[0]), n_targets=int(target_A.shape[0]),
        S_conc_mean=float(np.nanmean(y[seed_S])) if seed_S.size else float("nan"),
        S_conc_min=float(np.nanmin(y[seed_S])) if seed_S.size else float("nan"),
        A_conc_mean=float(np.nanmean(y[target_A])) if target_A.size else float("nan"),
        A_conc_max=float(np.nanmax(y[target_A])) if target_A.size else float("nan"),
        hub_conc_mean=float(np.nanmean(y[hub_seed])) if hub_seed.size else float("nan"),
        hub_deg_mean=float(np.mean(deg[hub_seed])) if hub_seed.size else float("nan"),
        S_deg_mean=float(np.mean(deg[seed_S])) if seed_S.size else float("nan"),
        deg_conc_spearman=deg_conc_spearman,
    )
    return dict(y=y, covered=covered, eligible=eligible, seed_S=seed_S, target_A=target_A,
                hub_seed=hub_seed, prov=prov)


# ============================ audit ===========================================
def _reach_sig(reach):
    return hashlib.sha256(json.dumps([round(float(x), 5) for x in reach]).encode()).hexdigest()


def run_audit(indptr, indices, edges_uv, deg, n, sets, seed):
    """Run S BFS + Control A (random) + Control B (scramble) + Control C (hub). Returns metrics dict."""
    rng = np.random.default_rng(seed)
    S = sets["seed_S"]
    A = sets["target_A"]
    hub = sets["hub_seed"]

    # --- S (grounded) ---
    dist_S = multi_source_bfs(indptr, indices, S, n, KMAX)
    reach_S, med_S, unreach_S = reach_curve(dist_S, A, KMAX)
    _log("S grounded: reach[k=1..%d]=%s median_hop=%s unreached=%s"
         % (KMAX, ["%.3f" % r for r in reach_S], _fmt(med_S), _fmt(unreach_S)))

    # --- Control A: random size-|S| seeds, N_RANDOM_DRAWS draws ---
    ca_reach = []
    ca_med = []
    for di in range(N_RANDOM_DRAWS):
        rs = rng.choice(n, size=int(S.shape[0]), replace=False)
        d = multi_source_bfs(indptr, indices, rs, n, KMAX)
        rc, md, _ur = reach_curve(d, A, KMAX)
        ca_reach.append(rc)
        ca_med.append(md)
    ca_reach = np.array(ca_reach, dtype=np.float64)   # [draws, KMAX]
    ca_med = np.array(ca_med, dtype=np.float64)
    _log("ControlA random (%d draws): reach(k<=%d) mean=%.3f p95=%.3f | median_hop mean=%.3f"
         % (N_RANDOM_DRAWS, P2_EVAL_K, float(ca_reach[:, P2_EVAL_K - 1].mean()),
            float(np.percentile(ca_reach[:, P2_EVAL_K - 1], 95)), float(np.nanmean(ca_med))))

    # --- Control B: same S/A, degree-preserving scramble, N_REWIRES rewirings ---
    n_swaps = int(SWAP_MULT * edges_uv.shape[0])
    cb_reach = []
    cb_med = []
    cb_swaps_done = []
    hb_path = os.path.join(str(get_output_dir(ANCHOR_NAME)), "_heartbeat.jsonl")
    for ri in range(N_REWIRES):
        srng = np.random.default_rng(seed * 1000 + ri + 1)
        E2, done = degree_preserving_swap(edges_uv, n_swaps, srng)
        cb_swaps_done.append(int(done))
        ip2, ix2, _dg2 = _csr_from_edges(E2, n)
        d = multi_source_bfs(ip2, ix2, S, n, KMAX)
        rc, md, _ur = reach_curve(d, A, KMAX)
        cb_reach.append(rc)
        cb_med.append(md)
        try:
            with open(hb_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                    "unit": "controlB_rewire", "idx": ri, "swaps_done": int(done)}) + "\n")
        except OSError:
            pass
    cb_reach = np.array(cb_reach, dtype=np.float64)
    cb_med = np.array(cb_med, dtype=np.float64)
    _log("ControlB scramble (%d rewirings, %d swaps each target): reach(k<=%d) mean=%.3f | median_hop "
         "mean=%.3f p5=%.3f" % (N_REWIRES, n_swaps, P1_EVAL_K, float(cb_reach[:, P1_EVAL_K - 1].mean()),
                                float(np.nanmean(cb_med)), float(np.nanpercentile(cb_med, 5))))

    # --- Control C: hub/kernel seed ---
    dist_H = multi_source_bfs(indptr, indices, hub, n, KMAX)
    reach_H, med_H, _urH = reach_curve(dist_H, A, KMAX)
    _log("ControlC hub-seed: reach[k=1..%d]=%s median_hop=%s | hub_conc_mean=%.3f S_conc_mean=%.3f"
         % (KMAX, ["%.3f" % r for r in reach_H], _fmt(med_H),
            sets["prov"]["hub_conc_mean"], sets["prov"]["S_conc_mean"]))

    return dict(
        reach_S=reach_S, median_hop_S=med_S, unreached_S=unreach_S,
        controlA_reach_mean=ca_reach.mean(axis=0).tolist(),
        controlA_reach_p5=np.percentile(ca_reach, 5, axis=0).tolist(),
        controlA_reach_p95=np.percentile(ca_reach, 95, axis=0).tolist(),
        controlA_median_hop_mean=float(np.nanmean(ca_med)),
        controlA_reach_all=ca_reach.tolist(), controlA_median_all=ca_med.tolist(),
        controlB_reach_mean=cb_reach.mean(axis=0).tolist(),
        controlB_reach_p5=np.percentile(cb_reach, 5, axis=0).tolist(),
        controlB_reach_p95=np.percentile(cb_reach, 95, axis=0).tolist(),
        controlB_median_hop_mean=float(np.nanmean(cb_med)),
        controlB_median_hop_p5=float(np.nanpercentile(cb_med, 5)),
        controlB_reach_all=cb_reach.tolist(), controlB_median_all=cb_med.tolist(),
        controlB_swaps_done=cb_swaps_done, controlB_n_swaps_target=n_swaps,
        reach_H=reach_H, median_hop_H=med_H,
        n_random_draws=int(ca_reach.shape[0]), n_rewires=int(cb_reach.shape[0]),
        arm_sigs=dict(S=_reach_sig(reach_S), controlA=_reach_sig(ca_reach.mean(axis=0).tolist()),
                      controlB=_reach_sig(cb_reach.mean(axis=0).tolist()), controlC=_reach_sig(reach_H)),
    )


def compute_verdict(res, prov):
    reach_S = res["reach_S"]
    reach_S_k4 = reach_S[P1_EVAL_K - 1]
    reach_S_k2 = reach_S[P2_EVAL_K - 1]
    med_S = res["median_hop_S"]

    # --- P1: raw reach bar AND real structure beats degree-preserving scramble (saturation-robust: median hop) ---
    cb_med_p5 = res["controlB_median_hop_p5"]
    p1_raw_ok = bool(reach_S_k4 >= P1_RAW_REACH_BAR)
    p1_beats_scramble = bool(np.isfinite(med_S) and np.isfinite(cb_med_p5) and med_S < cb_med_p5)
    reach_S_any = max(reach_S)
    if p1_raw_ok and p1_beats_scramble:
        p1 = "HARD_PASS"
    elif (reach_S_any < P1_RAW_REACH_BAR) or (not p1_beats_scramble):
        # islanded (never hits bar) OR indistinguishable from scramble (form-without-content)
        p1 = "HARD_FAIL"
    else:
        p1 = "MIDDLE_BAND"

    # --- P2: grounded seed selection beats random size-matched seed (Control A) ---
    ca_p95_k2 = res["controlA_reach_p95"][P2_EVAL_K - 1]
    ca_p5_k2 = res["controlA_reach_p5"][P2_EVAL_K - 1]
    ca_med_mean = res["controlA_median_hop_mean"]
    p2_reach_ok = bool(reach_S_k2 > ca_p95_k2)
    p2_med_ok = bool(np.isfinite(med_S) and np.isfinite(ca_med_mean) and med_S < ca_med_mean)
    if p2_reach_ok and p2_med_ok:
        p2 = "HARD_PASS"
    elif bool(ca_p5_k2 <= reach_S_k2 <= ca_p95_k2) and not p2_med_ok:
        p2 = "HARD_FAIL"
    else:
        p2 = "MIDDLE_BAND"

    # --- P3: kernel/hub nodes are NOT the concreteness-anchored population ---
    hub_c = prov["hub_conc_mean"]
    s_c = prov["S_conc_mean"]
    if np.isfinite(hub_c) and np.isfinite(s_c):
        p3_margin_ok = bool(hub_c <= s_c - P3_CONC_MARGIN and hub_c < P3_HUB_ABS_MAX)
        p3_fail = bool(hub_c >= s_c - 0.1)
    else:
        p3_margin_ok = False
        p3_fail = False
    if p3_margin_ok:
        p3 = "HARD_PASS"
    elif p3_fail:
        p3 = "HARD_FAIL"
    else:
        p3 = "MIDDLE_BAND"

    # headline tracks P1 (primary prediction)
    headline = {
        "HARD_PASS": "HARD_PASS_GROUNDING_PERCOLATES",
        "HARD_FAIL": "HARD_FAIL_GROUNDING_NOT_STRUCTURAL",
        "MIDDLE_BAND": "MIDDLE_BAND_PARTIAL",
    }[p1]

    msg = (
        "%s || P1=%s P2=%s P3=%s || reach_S[k=1..%d]=%s reach_S(k<=4)=%.3f (bar>=%.2f) "
        "median_hop_S=%s || P1 beats_scramble(med_S<ControlB_p5=%s)=%s || "
        "P2 reach_S(k<=2)=%.3f vs ControlA p95=%.3f (>p95=%s) median_hop_S<ControlA_mean(%.2f)=%s || "
        "P3 hub_conc=%.3f S_conc=%.3f (margin>=%.2f -> %s) deg_conc_spearman=%.3f || "
        "coverage=%.1f%% n_lcc=%d |S|=%d |A|=%d n_random=%d n_rewire=%d run=%s" % (
            headline, p1, p2, p3, KMAX, ["%.3f" % r for r in reach_S], reach_S_k4, P1_RAW_REACH_BAR,
            _fmt(med_S), _fmt(cb_med_p5), p1_beats_scramble,
            reach_S_k2, ca_p95_k2, p2_reach_ok, ca_med_mean, p2_med_ok,
            hub_c, s_c, P3_CONC_MARGIN, p3, prov["deg_conc_spearman"],
            100.0 * prov["coverage_frac"], prov["n_lcc"], prov["n_seed"], prov["n_targets"],
            res["n_random_draws"], res["n_rewires"], RUN_MODE))

    gates = dict(
        headline=headline, p1_verdict=p1, p2_verdict=p2, p3_verdict=p3,
        p1=dict(reach_S_k4=reach_S_k4, raw_bar=P1_RAW_REACH_BAR, raw_ok=p1_raw_ok,
                median_hop_S=med_S, controlB_median_hop_p5=cb_med_p5, beats_scramble=p1_beats_scramble),
        p2=dict(reach_S_k2=reach_S_k2, controlA_p95_k2=ca_p95_k2, controlA_p5_k2=ca_p5_k2,
                reach_ok=p2_reach_ok, median_hop_S=med_S, controlA_median_mean=ca_med_mean, med_ok=p2_med_ok),
        p3=dict(hub_conc_mean=hub_c, S_conc_mean=s_c, margin=P3_CONC_MARGIN, hub_abs_max=P3_HUB_ABS_MAX,
                margin_ok=p3_margin_ok, fail=p3_fail, deg_conc_spearman=prov["deg_conc_spearman"]),
        bands=dict(P1_RAW_REACH_BAR=P1_RAW_REACH_BAR, P1_EVAL_K=P1_EVAL_K, P2_EVAL_K=P2_EVAL_K,
                   P3_CONC_MARGIN=P3_CONC_MARGIN, P3_HUB_ABS_MAX=P3_HUB_ABS_MAX, CONC_LOW=CONC_LOW,
                   KMAX=KMAX, N_SEED=N_SEED, N_RANDOM_DRAWS=N_RANDOM_DRAWS, N_REWIRES=N_REWIRES,
                   SWAP_MULT=SWAP_MULT),
    )
    return headline, msg, gates


# ============================ self-test =======================================
def _planted_graph(seed=11):
    """Deterministic planted graph engineered so the directional discriminators fire with a LARGE,
    swap-robust margin (no local execution is available to tune it, per the no-local-smokes lock):
      - A random SPARSE background of BG nodes (avg deg ~2) -> non-trivial diameter; random seeds land
        FAR from targets.
      - TARGETS t0..t{T-1} embedded in the background (low concreteness).
      - Each grounded ANCHOR a_i has a DIRECT (hop-1) edge to target t_i (high concreteness). So grounded
        reach at k<=1 is DETERMINISTICALLY 1.0, while random-seed reach at k<=1 is ~0 and a
        degree-preserving scramble (which relocates the anchor->target edges) drops it sharply.
      - A disjoint ISLAND component of abstract nodes (UNREACHABLE from the background/anchors).
      - A few LOW-concreteness HUB nodes wired to many background nodes (highest degree; Prediction 3).
    Returns (labels, edges_uv, indptr, indices, deg, conc, anchor_ids, target_ids, island_ids)."""
    rng = np.random.default_rng(seed)
    T = 20                                  # anchors and targets (1:1 direct edges)
    BG = 400                                # background nodes (includes the targets)
    NHUB = 3
    ISL = 8
    bg = ["bg%d" % i for i in range(BG)]
    anc = ["anc%d" % i for i in range(T)]
    hub = ["hub%d" % i for i in range(NHUB)]
    isl = ["isl%d" % i for i in range(ISL)]
    labels = bg + anc + hub + isl
    idx = {w: k for k, w in enumerate(labels)}
    edges = set()

    def _add(x, y):
        a, b = idx[x], idx[y]
        if a != b:
            edges.add((a, b) if a < b else (b, a))

    # sparse random background: each node gets ~2 random neighbours (undirected) -> connected-ish, diameter>1
    for i in range(BG):
        for _ in range(2):
            j = int(rng.integers(0, BG))
            _add("bg%d" % i, "bg%d" % j)
    # ensure background connectivity backbone (a spanning path) so it is one component with real distances
    for i in range(BG - 1):
        _add("bg%d" % i, "bg%d" % (i + 1))
    # targets = first T background nodes; each grounded anchor has a DIRECT edge to its target + 1 bg edge
    target_ids = np.array([idx["bg%d" % i] for i in range(T)], dtype=np.int64)
    for i in range(T):
        _add("anc%d" % i, "bg%d" % i)                       # the planted grounded->target hop-1 link
        _add("anc%d" % i, "bg%d" % int(rng.integers(0, BG)))  # 1 background tie (keeps anchor in the LCC)
    # low-concreteness hubs: wired to MANY background nodes -> highest degree
    for h in range(NHUB):
        for _ in range(40):
            _add("hub%d" % h, "bg%d" % int(rng.integers(0, BG)))
    # disjoint island (abstract; unreachable)
    for i in range(ISL - 1):
        _add("isl%d" % i, "isl%d" % (i + 1))

    edges_uv = np.array(sorted(edges), dtype=np.int64)
    n = len(labels)
    indptr, indices, deg = _csr_from_edges(edges_uv, n)
    conc = {}
    for i in range(BG):
        conc["bg%d" % i] = 3.0
    for i in range(T):
        conc["bg%d" % i] = 1.5              # targets = abstract
        conc["anc%d" % i] = 5.0             # anchors = concrete
    for h in range(NHUB):
        conc["hub%d" % h] = 1.7             # LOW-concreteness hubs (Prediction 3 planted)
    for i in range(ISL):
        conc["isl%d" % i] = 1.4
    anchor_ids = np.array([idx["anc%d" % i] for i in range(T)], dtype=np.int64)
    island_ids = np.array([idx["isl%d" % i] for i in range(ISL)], dtype=np.int64)
    return labels, edges_uv, indptr, indices, deg, conc, anchor_ids, target_ids, island_ids


def _selftest():
    print("[selftest] planted grounded->abstract reachability discriminators...", flush=True)
    labels, edges_uv, indptr, indices, deg, conc, anchor_ids, target_ids, island_ids = _planted_graph()
    n = len(labels)
    n_swaps = 20 * edges_uv.shape[0]

    # (a) BFS correctness: each target reachable at hop 1 from its anchor; island UNREACHABLE from anchors.
    dist = multi_source_bfs(indptr, indices, anchor_ids, n, KMAX)
    assert int(dist[target_ids].max()) == 1, \
        "SELFTEST(a) FAIL: not every target at hop 1 from its anchor: %s" % dist[target_ids].tolist()
    assert int(dist[island_ids].max()) == -1, \
        "SELFTEST(a) FAIL: island reachable from anchors (should be disjoint): %s" % dist[island_ids].tolist()

    # (b) degree-preserving swap: degree sequence EXACTLY preserved; scramble relocates the anchor->target
    #     edges -> k<=1 reach drops well below the real 1.0 (Control B fires).
    d_real, _mr, _ur = reach_curve(dist, target_ids, KMAX)
    assert abs(d_real[0] - 1.0) < 1e-9, "SELFTEST(b) FAIL: real k<=1 reach not 1.0 (%.3f)" % d_real[0]
    scr_reach1 = []
    for ri in range(8):
        rr = np.random.default_rng(100 + ri)
        Es, done = degree_preserving_swap(edges_uv, n_swaps, rr)
        _ips, _ixs, deg2 = _csr_from_edges(Es, n)
        assert np.array_equal(np.sort(deg), np.sort(deg2)), "SELFTEST(b) FAIL: swap changed degree sequence"
        assert done > 0, "SELFTEST(b) FAIL: no swaps applied"
        rc, _md, _u = reach_curve(multi_source_bfs(_ips, _ixs, anchor_ids, n, KMAX), target_ids, KMAX)
        scr_reach1.append(rc[0])
    scr_mean1 = float(np.mean(scr_reach1))
    assert d_real[0] > scr_mean1 + 0.3, \
        "SELFTEST(b) FAIL: scramble did not drop k<=1 reach enough (real=%.3f scr_mean=%.3f); ControlB inert" \
        % (d_real[0], scr_mean1)

    # (c) Control A: grounded anchors reach targets at k<=1 (=1.0); random seeds ~0 -> grounded beats random.
    rrng = np.random.default_rng(7)
    rand_reach1 = []
    for _ in range(20):
        rs = rrng.choice(n, size=anchor_ids.shape[0], replace=False)
        rc, _m, _u = reach_curve(multi_source_bfs(indptr, indices, rs, n, KMAX), target_ids, KMAX)
        rand_reach1.append(rc[0])
    rand_p95 = float(np.percentile(rand_reach1, 95))
    assert d_real[0] > rand_p95, \
        "SELFTEST(c) FAIL: grounded seeds do not beat random at k<=1 (grounded=%.3f rand_p95=%.3f)" \
        % (d_real[0], rand_p95)

    # (d) Prediction 3: highest-degree (hub) nodes have LOWER mean concreteness than the concrete anchors.
    hub_ids = np.argsort(-deg, kind="stable")[:3]
    hub_c = float(np.mean([conc[labels[int(h)]] for h in hub_ids]))
    anchor_c = float(np.mean([conc[labels[int(a)]] for a in anchor_ids]))
    assert hub_c < anchor_c - 0.5, \
        "SELFTEST(d) FAIL: hub concreteness not below anchor concreteness (hub=%.2f anchor=%.2f)" \
        % (hub_c, anchor_c)
    assert all(labels[int(h)].startswith("hub") for h in hub_ids), \
        "SELFTEST(d) FAIL: top-degree nodes are not the planted hubs: %s" % [labels[int(h)] for h in hub_ids]

    # (e) arms differ: grounded / random-mean / scramble-mean / hub reach vectors not all identical.
    hub_reach, _hm, _hu = reach_curve(multi_source_bfs(indptr, indices, hub_ids, n, KMAX), target_ids, KMAX)
    sig_S = _reach_sig(d_real)
    sig_A = _reach_sig([float(np.mean(rand_reach1))] * KMAX)
    sig_B = _reach_sig([scr_mean1] * KMAX)
    sig_C = _reach_sig(hub_reach)
    assert len({sig_S, sig_A, sig_B, sig_C}) >= 3, "SELFTEST(e) FAIL: reach-arm sigs not >=3 distinct"

    print("[selftest] PASS: (a) BFS hop1+island (b) swap degree-preserved + ControlB fires "
          "(real k<=1=%.3f > scr=%.3f) (c) ControlA fires (grounded=%.3f > rand_p95=%.3f) "
          "(d) hub_conc=%.2f < anchor_conc=%.2f (e) arms differ (>=3 sigs)" %
          (d_real[0], scr_mean1, d_real[0], rand_p95, hub_c, anchor_c), flush=True)


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
    _write_start_marker(out_dir, RUN_MODE, N_RANDOM_DRAWS + N_REWIRES)
    t0 = time.time()
    _log("config: mode=%s N_SEED=%d N_RANDOM_DRAWS=%d N_REWIRES=%d SWAP_MULT=%d KMAX=%d CONC_LOW=%.1f"
         % (RUN_MODE, N_SEED, N_RANDOM_DRAWS, N_REWIRES, SWAP_MULT, KMAX, CONC_LOW))

    if not _ensure_file(CSKG_PATH, CSKG_URL, 50_000_000):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_DATA_MISSING", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="cskg.tsv.gz absent + self-acquire failed on runner: %s" % CSKG_PATH,
            summary="CSKG data missing", elapsed_s=time.time() - t0))
        raise SystemExit(1)
    if not _ensure_file(CONC_PATH, CONC_URL, 100_000, header_needle="Conc.M"):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_DATA_MISSING", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="concreteness norms absent + self-acquire failed: %s" % CONC_PATH,
            summary="concreteness data missing", elapsed_s=time.time() - t0))
        raise SystemExit(1)

    _log("streaming CSKG cross-cutting edges (max_lines=%s)..." % (CSKG_MAX_LINES or "ALL"))
    labels, edges_uv, indptr, indices, deg = build_lcc(_iter_cskg_triples(CSKG_MAX_LINES))
    n = len(labels)
    _log("LCC: n=%d edges=%d avg_deg=%.2f deg[max]=%d"
         % (n, edges_uv.shape[0], 2.0 * edges_uv.shape[0] / max(1, n), int(deg.max()) if n else 0))

    conc = load_concreteness_map(CONC_PATH)
    sets = build_seed_target_sets(labels, deg, conc, N_SEED)
    prov = sets["prov"]
    _log("join: coverage=%.1f%% (%d/%d) eligible=%d |S|=%d (conc_mean=%.2f,min=%.2f) |A|=%d "
         "(conc_mean=%.2f,max=%.2f) hub_conc_mean=%.2f deg_conc_spearman=%.3f"
         % (100 * prov["coverage_frac"], prov["n_covered"], prov["n_lcc"], prov["n_eligible"],
            prov["n_seed"], prov["S_conc_mean"], prov["S_conc_min"], prov["n_targets"],
            prov["A_conc_mean"], prov["A_conc_max"], prov["hub_conc_mean"], prov["deg_conc_spearman"]))

    if prov["n_seed"] < MIN_SEEDS or prov["n_targets"] < MIN_TARGETS:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_DATA_INSUFFICIENT", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="insufficient seeds/targets: |S|=%d (need>=%d) |A|=%d (need>=%d) coverage=%.1f%%"
                        % (prov["n_seed"], MIN_SEEDS, prov["n_targets"], MIN_TARGETS,
                           100 * prov["coverage_frac"]),
            summary="data insufficient", elapsed_s=time.time() - t0, provenance=prov))
        raise SystemExit(1)

    res = run_audit(indptr, indices, edges_uv, deg, n, sets, seed=7)

    # cardinality gate (META_RULE_H): every Control-A draw + Control-B rewiring must have completed.
    if res["n_random_draws"] != N_RANDOM_DRAWS or res["n_rewires"] != N_REWIRES:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="expected ControlA=%d ControlB=%d got A=%d B=%d"
                        % (N_RANDOM_DRAWS, N_REWIRES, res["n_random_draws"], res["n_rewires"]),
            summary="cardinality breach", elapsed_s=time.time() - t0, provenance=prov, audit=res))
        raise SystemExit(1)

    # arms-must-differ (META_RULE_AF)
    sigs = res["arm_sigs"]
    if len(set(sigs.values())) < 3:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="reach-arm sigs not distinct: %s" % sigs, summary="arms identical",
            elapsed_s=time.time() - t0, provenance=prov, audit=res))
        raise SystemExit(1)

    headline, msg, gates = compute_verdict(res, prov)
    elapsed = time.time() - t0
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=headline, verdict_msg=msg, summary=msg[:200],
        run_mode=RUN_MODE, n_seeds=1, elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        arms_differ_verified=True, arm_sigs=sigs, gates=gates, provenance=prov, audit=res,
        config=dict(N_SEED=N_SEED, N_RANDOM_DRAWS=N_RANDOM_DRAWS, N_REWIRES=N_REWIRES,
                    SWAP_MULT=SWAP_MULT, KMAX=KMAX, CONC_LOW=CONC_LOW),
    )
    write_metrics(out_dir, metrics, results=[{"elapsed_s": elapsed}])
    _log("VERDICT: %s" % msg)
    _log("done (%.1fs)" % elapsed)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    _selftest()                 # tiny planted-graph discriminators; asserts fire before any CSKG work
    if _ARGS.self_test:
        _od = get_output_dir(ANCHOR_NAME)
        write_metrics(_od, dict(
            verdict="SELFTEST_PASS", run_mode="self_test", anchor_name=ANCHOR_NAME,
            verdict_msg="SELFTEST_PASS: BFS+island correct; degree-preserving swap preserves degree seq + "
                        "ControlB fires; ControlA fires; hub<anchor concreteness (P3); arms differ",
            summary="SELFTEST_PASS", elapsed_s=0.0))
        sys.exit(0)
    _od = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
