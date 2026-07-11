"""
grounding_labelshuffle_null_cskg_v2 -- REDESIGNED grounding-percolation audit on the CSKG cross-cutting
commonsense core. Pure graph BFS audit. NO training, NO substrate vectors, NO new data acquisition (all
inputs already on disk under data/grounding_testbed/).

WHY v2 (what the v1 VET caught). v1 (exp_grounding_percolation_reachability_cskg_v1) landed HARD_FAIL but
the landed-VET returned ARTIFACT_INCONCLUSIVE: its P1 must-fail control was a degree-preserving
double-edge-swap scramble, and the pre-reg bet "real graph reaches abstract targets at SHORTER hop-distance
than the scramble." That direction is near-UNWINNABLE BY CONSTRUCTION: degree-preserving randomization
GENERICALLY SHORTENS path length (it destroys clustering and injects long-range shortcuts -- textbook
small-world). So the scramble almost always beats the real graph on median hop, forcing HARD_FAIL regardless
of whether grounding is structural. The confound is in the NULL MODEL, not the substrate.

v2 REPLACES that confounded null with a CONCRETENESS-LABEL-SHUFFLE null -- the strongest possible
TOPOLOGY-PRESERVING null. It preserves the ENTIRE graph structure EXACTLY (degree sequence, clustering
coefficient, community structure -- everything), and permutes ONLY the exogenous concreteness labels across
the nodes. This is the limiting case of the "clustering-preserving null" (it preserves not just clustering
but all topology), so it cannot suffer the small-world path-shortening artifact that confounded v1 -- there
is no rewiring at all. It isolates the ONE thing that matters: is the grounded-seed reachability advantage
carried by the real GROUNDING-signal-to-topology ALIGNMENT, or would ANY labeling of the same graph do just
as well (the Bender-Koller form-without-content / octopus failure mode)?

  [Design note: a concrete->abstract BRIDGE-SURVIVAL test (the other option) was prototyped and REJECTED as
   inherently confounded here: the reach target (the concrete seed set S) and the "bridges" (concrete-
   crossing edges) are BOTH defined by the same concreteness axis, so bridges always point toward S's region
   and their deletion hurts concrete-reach REGARDLESS of grounding; label-shuffling does not break this
   because S and the bridge set stay co-defined. The self-test measured a persistent ~0.03 tautological
   offset under shuffled labels. The label-shuffle null has no such coupling and its negative control goes
   cleanly to ~0.]

v2 also LEANS ON THE ONE VALID POSITIVE v1 already found (this control was NOT confounded): grounded
(concreteness-selected) seeds beat size-matched RANDOM seeds at small k on the SAME real graph (v1:
reach_S(k<=2)=0.467 > random 0.368). That within-graph, same-graph, no-rewiring comparison is the real
signal; v2 promotes it to a FIRST-CLASS HARD-PASS arm (P2) and FAIRS it (random seeds drawn from the
NON-TARGET pool, matched to S which is disjoint from A -- v1 drew random from all nodes, letting a random
seed land ON a target and spuriously depressing random reach).

Predictions (headline = grounding is STRUCTURAL iff P2 AND P1 both HARD_PASS):
  P2 (grounded-seed advantage; the valid v1 positive, promoted + faired): reach_S(k<=2) beats the random
     NON-TARGET-seed reach distribution 95th percentile AND beats its MEAN by a pre-registered effect bar
     AND grounded median hop < random mean median hop.
  P1 (form-without-content / topology-preserving null; the REDESIGNED null): the REAL grounded-seed
     advantage margin exceeds the concreteness-LABEL-SHUFFLE null distribution (real margin > null 95th pct
     AND real margin - null mean >= a pre-registered structural effect bar). I.e. the advantage is carried
     by the real grounding labels, not by topology/degree that any labeling would inherit.
  P3 (kernel/hub != grounded population; v1's un-confounded secondary, kept): highest-degree hub nodes are
     materially LESS concrete than the grounded seed set (Vincent-Lamarre 2016 dictionary-graph finding).

ACHIEVABILITY + FORM-WITHOUT-CONTENT (self-test on synthetic graphs; the POSTER-CHILD gate for the confound
this cell fixes):
  POSITIVE control -- a synthetic graph with a REAL grounded->abstract structure: concrete anchors bridge to
      an otherwise-isolated abstract mesh. MUST clear BOTH the P2 and the P1 HARD-PASS bars (proves the bars
      are ACHIEVABLE -- exactly what v1's confounded/unwinnable bar failed).
  NEGATIVE control -- the SAME topology with concreteness labels RANDOMLY SHUFFLED (identical FORM, scrambled
      CONTENT): grounded selection confers no advantage. MUST FAIL both bars DETERMINISTICALLY over repeats
      WITH MARGIN. If the test passed on shuffled labels it would be reading topology, not grounding -- the
      test itself would be invalid.
The POSITIVE and NEGATIVE controls run the SAME grounded-advantage + label-shuffle-null code path the real
CSKG audit uses (no separate synthetic logic to drift), so passing them validates the real arms.

DATA (already on disk; the cell self-acquires if absent on the runner):
  - CSKG cross-cutting subgraph from data/grounding_testbed/cskg.tsv.gz (Zenodo 4331372), restricted to the
    commonsense SPINE relations (strips the ~79% lexical/taxonomic dilution) per
    notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md. BFS graph = largest connected component.
  - Brysbaert, Warriner & Kuperman (2014) concreteness norms (Conc.M, 1=abstract..5=concrete; 39,954 words)
    from data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt. EXOGENOUS (human-rated) anchor.

DETERMINISM. All node/edge set construction routes through _dedupe_canonical_edges (sorted(), NOT
list(set(...))) so node ids, edge order, and seed/target selection are a deterministic function of (input,
seed), NOT of the per-process PYTHONHASHSEED. Same split-identity fix as commit 754c5620b
(exp_cskg_dense_core_headroom_acceptance_v1._dedupe_canonical).

## Compute architecture
Class (b) sequential-CPU with justification: pure combinatorial graph traversal (multi-source BFS, dict
joins, label permutation). NO substrate vectors, NO bind/unbind, NO matmul, NO torch -> GPU batching does
not apply. BFS neighbourhood-gather is numpy-vectorized (CSR). No degree-preserving swap (v1's expensive +
confounded step is GONE); the label-shuffle null only permutes a length-n float array + re-selects seeds
(cheap) then reuses the SAME CSR -> v2 is strictly CHEAPER than v1 (v1 landed 271s WITH the swap). Storage
strategy: no_storage / no_composition. Routes to remote_cpu_queue (CPU; keeps the laptop free per the
no-local-smokes lock). numpy + stdlib only (parity-safe: same self-contained discipline as
exp_cskg_dense_core_headroom_acceptance_v1, which ran on the remote runner without networkx).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor/cardinality + validity-preflight):
  - arms_differ_verified at self-test AND full (>=3 distinct sigs: S / controlA-random-seed / labelshuffle /
    controlC-hub). Exercised at self-test scale (full_gates_exercised).
  - final_metrics_atomicity=tmp_replace (write_metrics + crash-writer both tmp+os.replace).
  - except SystemExit: raise BEFORE except Exception; no BaseException.
  - crlb_n/a: no quantitative estimator noise floor -- graph-reachability distribution-separation audit
    (grounded vs random-seed null; real vs label-shuffle null). ACHIEVABILITY proven by the synthetic
    POSITIVE control clearing the bar; the FORM-WITHOUT-CONTENT NEGATIVE control failing it with margin
    (validity preflight).
  - baseline_in_band: the "baseline" is the random-seed null (P2) + the label-shuffle null (P1); at full
    scale this is an OPEN MEASUREMENT reported as the verdict, not a smoke-abort.
  - discriminator survives scale (analytical, option B): reach at large k SATURATES on a dense graph, so all
    metrics are evaluated at SMALL k (k<=2), where reach of |S|=300 seeds in a ~1M-edge / ~471k-node LCC is
    well below 100% (v1 measured reach_S(k<=2)=0.467). Small-k reach carries the resolution; it does not
    saturate.
  - HARD_PASS bands strictly declared below (P2 effect bar + p95 non-overlap; P1 structural effect bar +
    null-p95 non-overlap; P3 concreteness margin). Bars proven ACHIEVABLE by the positive control.
  - cardinality_ok: EXPECTED units = N_RANDOM_DRAWS (P2) + N_LABEL_SHUFFLE (P1); short -> HARD_FAIL_
    CARDINALITY_BREACH_META_RULE_H.
  - per-unit failure-class instrumentation (no bare except; specific classes; recorded to metrics).
  - calibration_check=default_ok_for_this_regime (BFS + label permutation are parameter-free apparatus).
  - progress_logging=print_flush_true (all logs flush=True; heartbeat during label-shuffle draws).
  - cell_chunked=false (single graph; no per-seed chunking); start_marker + crash_diagnostic present.
  - validity-preflight DECLARED (all four): positive_control (mandatory), metric_moves,
    full_gates_exercised, negative_control_margin. Imported as
    `from experiments._validity_preflight import run_validity_preflight` (triggers auto-SCP of the module).

ASCII-only. No em dashes in output. RUN_MODE defaults to full (runner invokes with no argv).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import gzip
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
# `from experiments._validity_preflight import ...` (not a bare import) so queue_add auto-SCPs the module.
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

ANCHOR_NAME = "grounding_labelshuffle_null_cskg_v2"
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

# ---- pre-registered bands (picked BEFORE the run) ----------------------------
KMAX = 6                    # report reach curve k=1..KMAX
P2_EVAL_K = 2               # all grounded-advantage metrics at k<=2 (non-saturated small-k resolution)
P2_EFFECT_BAR = 0.05        # P2: reach_S(k<=2) must beat random-seed MEAN by >= this (real v1 effect ~0.10)
STRUCT_EFFECT_BAR = 0.03    # P1: real grounded margin must beat label-shuffle-null MEAN by >= this
P3_CONC_MARGIN = 0.5        # P3: hub mean concreteness must be this far BELOW S mean concreteness
P3_HUB_ABS_MAX = 3.0        # P3: hub mean concreteness must be below the mid-scale point
CONC_LOW = 2.5              # abstract target threshold (Conc.M <= this)
MIN_SEEDS = 100             # data-sufficiency floors (real graph)
MIN_TARGETS = 200

if RUN_MODE == "smoke":
    N_SEED = 40
    N_RANDOM_DRAWS = 5
    N_LABEL_SHUFFLE = 5
    N_RAND_PER_SHUFFLE = 3
    CSKG_MAX_LINES = 250000     # small slice (assembly + apparatus proof; NOT the full graph)
else:
    N_SEED = 300               # modest grounded seed budget -> graded small-k reach in a dense LCC
    N_RANDOM_DRAWS = 20         # P2 random-seed draws (>=20 floor)
    N_LABEL_SHUFFLE = 20        # P1 concreteness-label-shuffle null draws (>=20 floor)
    N_RAND_PER_SHUFFLE = 5      # random-seed draws WITHIN each label-shuffle (to estimate that shuffle's margin)
    CSKG_MAX_LINES = 0          # 0 = stream the whole graph

# CROSS-CUTTING commonsense relation spine (CITED@notes/cskg_commonsense_core_kcore_density_gate sec.3):
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
    """Yield (word1, word2) for CROSS-CUTTING commonsense edges from cskg.tsv.gz."""
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
def _dedupe_canonical_edges(pairs):
    """PROCESS-INVARIANT canonical undirected dedupe (split-identity fix, per commit 754c5620b).
    Returns a SORTED list of (min_label, max_label) tuples. sorted() -- NOT list(set(...)) -- so node-id
    assignment + seed/target selection are a deterministic function of (input, seed), not of the per-process
    PYTHONHASHSEED. list(set(string_tuples)) is ordered by the unpinned hash seed -> a different node-id map
    / edge order each process (the 2026-07-11 CSKG split-identity-breach root cause)."""
    s = set()
    for (a, b) in pairs:
        if a == b:
            continue
        s.add((a, b) if a < b else (b, a))
    return sorted(s)


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


def build_lcc(edge_pairs):
    """edge_pairs: iterable of (label1, label2). Build a simple undirected graph via SORTED-CANONICAL dedupe,
    keep the LARGEST connected component. Deterministic node ids (sorted label order) + sorted edge order.
    Returns (labels, edges_uv, indptr, indices, deg)."""
    edges_sorted = _dedupe_canonical_edges(edge_pairs)
    labset = set()
    for (a, b) in edges_sorted:
        labset.add(a)
        labset.add(b)
    sorted_labels = sorted(labset)                 # deterministic node-id order
    lab2id = {w: i for i, w in enumerate(sorted_labels)}
    E = np.empty((len(edges_sorted), 2), dtype=np.int64)
    for k, (a, b) in enumerate(edges_sorted):
        E[k, 0] = lab2id[a]
        E[k, 1] = lab2id[b]
    n_all = len(sorted_labels)
    id2lab = sorted_labels

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
    uniq, counts = np.unique(roots, return_counts=True)
    lcc_root = int(uniq[int(np.argmax(counts))])
    in_lcc = roots == lcc_root
    old_ids = np.where(in_lcc)[0]                   # ascending -> labels stay sorted
    remap = -np.ones(n_all, dtype=np.int64)
    remap[old_ids] = np.arange(old_ids.shape[0], dtype=np.int64)
    labels = [id2lab[int(o)] for o in old_ids]
    keep_e = in_lcc[E[:, 0]] & in_lcc[E[:, 1]]
    Elcc = remap[E[keep_e]]
    lo = np.minimum(Elcc[:, 0], Elcc[:, 1])
    hi = np.maximum(Elcc[:, 0], Elcc[:, 1])
    edges_uv = np.stack([lo, hi], axis=1).astype(np.int64)
    order = np.lexsort((edges_uv[:, 1], edges_uv[:, 0]))   # deterministic edge order
    edges_uv = edges_uv[order]
    m = len(labels)
    indptr, indices, deg = _csr_from_edges(edges_uv, m)
    return labels, edges_uv, indptr, indices, deg


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
        counts = (indptr[frontier + 1] - indptr[frontier]).astype(np.int64)
        total = int(counts.sum())
        if total == 0:
            break
        starts = indptr[frontier]
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
    """reach[k] = frac of targets with 0 < dist <= k (k=1..kmax). Returns (reach list, median_hop, frac_unreached)."""
    dt = dist[target_ids].astype(np.int64)
    ntar = dt.shape[0]
    reach = []
    for k in range(1, kmax + 1):
        reach.append(float(np.mean((dt >= 1) & (dt <= k))) if ntar else float("nan"))
    reached = dt[dt >= 1]
    median_hop = float(np.median(reached)) if reached.size else float("inf")
    frac_unreached = float(np.mean(dt == -1)) if ntar else float("nan")
    return reach, median_hop, frac_unreached


def _reach_sig(vec):
    return hashlib.sha256(json.dumps([round(float(x), 5) for x in vec]).encode()).hexdigest()


# ============================ grounded-advantage core =========================
# Real P2 AND every label-shuffle-null draw AND the synthetic controls all call THIS -> one code path.
def grounded_advantage(indptr, indices, n, seed_S, target_A, n_random_draws, rng, want_full=False):
    """reach_S(k<=2) minus the random-NON-TARGET-seed reach distribution. Random seeds are matched in size
    to S and drawn from the NON-TARGET pool (S is disjoint from A by construction; drawing random seeds from
    all nodes would let one land ON a target -> dist 0 -> counted unreached -> spuriously depressed random
    reach). Returns a dict of scalars (+ full reach curve / median if want_full)."""
    dist_S = multi_source_bfs(indptr, indices, seed_S, n, KMAX)
    reach_S, med_S, unreach_S = reach_curve(dist_S, target_A, KMAX)
    reach_S_k2 = reach_S[P2_EVAL_K - 1]

    in_A = np.zeros(n, dtype=bool)
    in_A[np.asarray(target_A, dtype=np.int64)] = True
    nontarget_pool = np.where(~in_A)[0].astype(np.int64)
    ns = int(seed_S.shape[0])
    ca_k2 = []
    ca_med = []
    for _di in range(n_random_draws):
        rs = rng.choice(nontarget_pool, size=min(ns, nontarget_pool.shape[0]), replace=False)
        d = multi_source_bfs(indptr, indices, rs, n, KMAX)
        rc, md, _ur = reach_curve(d, target_A, KMAX)
        ca_k2.append(rc[P2_EVAL_K - 1])
        ca_med.append(md)
    ca_k2 = np.array(ca_k2, dtype=np.float64)
    ca_med = np.array(ca_med, dtype=np.float64)
    ca_mean = float(ca_k2.mean())
    out = dict(
        reach_S_k2=reach_S_k2, controlA_mean_k2=ca_mean,
        controlA_p95_k2=float(np.percentile(ca_k2, 95)), controlA_p5_k2=float(np.percentile(ca_k2, 5)),
        margin=reach_S_k2 - ca_mean, median_hop_S=med_S, controlA_median_hop_mean=float(np.nanmean(ca_med)),
        n_random_draws=int(ca_k2.shape[0]),
    )
    if want_full:
        out["reach_S"] = reach_S
        out["unreached_S"] = unreach_S
    return out


def _select_sets_from_y(y, is_stop, deg, n_seed):
    """Given a per-node concreteness array y (nan = uncovered), select S (top-conc eligible), A (abstract
    eligible, disjoint from S), hub (top-degree). Deterministic (stable argsort over sorted-id nodes)."""
    covered = np.isfinite(y)
    eligible = covered & (~is_stop)
    elig_ids = np.where(eligible)[0]
    order = elig_ids[np.argsort(-y[elig_ids], kind="stable")]
    seed_S = order[:n_seed].astype(np.int64)
    S_set = set(seed_S.tolist())
    abstract_ids = elig_ids[y[elig_ids] <= CONC_LOW]
    target_A = np.array([i for i in abstract_ids.tolist() if i not in S_set], dtype=np.int64)
    hub_seed = np.argsort(-deg, kind="stable")[:n_seed].astype(np.int64)
    return seed_S, target_A, hub_seed


def label_shuffle_null(indptr, indices, deg, n, y, is_stop, n_seed, n_shuffle, n_rand_per, rng, hb_path=None):
    """TOPOLOGY-PRESERVING null: permute the concreteness labels y across the COVERED nodes (uncovered stay
    uncovered), re-select S'/A' from the shuffled labels, and measure that shuffle's grounded-advantage
    margin. The graph (CSR) is untouched -> degree, clustering, community structure all preserved EXACTLY.
    Returns the array of per-shuffle margins (each ~0 if grounding is not carried by the real labels)."""
    covered_ids = np.where(np.isfinite(y))[0]
    y_cov = y[covered_ids].copy()
    margins = []
    for si in range(n_shuffle):
        y_s = np.full(n, np.nan, dtype=np.float64)
        y_s[covered_ids] = y_cov[rng.permutation(covered_ids.shape[0])]   # permute labels among covered nodes
        S_s, A_s, _hub_s = _select_sets_from_y(y_s, is_stop, deg, n_seed)
        if S_s.shape[0] < max(10, n_seed // 3) or A_s.shape[0] < 20:
            margins.append(0.0)                     # degenerate split under this shuffle -> no signal
            continue
        adv = grounded_advantage(indptr, indices, n, S_s, A_s, n_rand_per, rng)
        margins.append(adv["margin"])
        if hb_path is not None:
            try:
                with open(hb_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                        "unit": "label_shuffle", "idx": si,
                                        "margin": adv["margin"]}) + "\n")
            except OSError:
                pass
    return np.array(margins, dtype=np.float64)


# ============================ audit ===========================================
def run_audit(indptr, indices, deg, n, y, is_stop, seed_S, target_A, hub_seed, prov, rng, hb_path=None):
    """P2 (grounded vs random-seed) + P1 (real margin vs label-shuffle null) + P3 (hub concreteness)."""
    p2 = grounded_advantage(indptr, indices, n, seed_S, target_A, N_RANDOM_DRAWS, rng, want_full=True)
    null_margins = label_shuffle_null(indptr, indices, deg, n, y, is_stop, int(seed_S.shape[0]),
                                      N_LABEL_SHUFFLE, N_RAND_PER_SHUFFLE, rng, hb_path=hb_path)
    null_mean = float(null_margins.mean())
    null_p95 = float(np.percentile(null_margins, 95))
    null_p5 = float(np.percentile(null_margins, 5))

    hub_conc_mean = float(np.nanmean(y[hub_seed])) if hub_seed.size else float("nan")
    s_conc_mean = float(np.nanmean(y[seed_S])) if seed_S.size else float("nan")
    dist_H = multi_source_bfs(indptr, indices, hub_seed, n, KMAX)
    reach_H, _mh, _uh = reach_curve(dist_H, target_A, KMAX)

    arm_sigs = dict(
        S=_reach_sig(p2["reach_S"]),
        controlA=_reach_sig([p2["controlA_mean_k2"], p2["controlA_p95_k2"]]),
        labelshuffle=_reach_sig([null_mean, null_p95, null_p5]),
        controlC=_reach_sig(reach_H),
    )
    return dict(
        reach_S=p2["reach_S"], reach_S_k2=p2["reach_S_k2"], median_hop_S=p2["median_hop_S"],
        unreached_S=p2["unreached_S"],
        controlA_mean_k2=p2["controlA_mean_k2"], controlA_p95_k2=p2["controlA_p95_k2"],
        controlA_p5_k2=p2["controlA_p5_k2"], controlA_median_hop_mean=p2["controlA_median_hop_mean"],
        margin_p2=p2["margin"], n_random_draws=p2["n_random_draws"],
        null_margins=null_margins.tolist(), null_mean=null_mean, null_p95=null_p95, null_p5=null_p5,
        n_label_shuffle=int(null_margins.shape[0]), struct_margin=p2["margin"] - null_mean,
        hub_conc_mean=hub_conc_mean, s_conc_mean=s_conc_mean, reach_H=reach_H,
        arm_sigs=arm_sigs,
    )


def verdict_p2(res):
    reach_ok = bool(res["reach_S_k2"] > res["controlA_p95_k2"])
    effect_ok = bool(res["margin_p2"] >= P2_EFFECT_BAR)
    med_ok = bool(np.isfinite(res["median_hop_S"]) and np.isfinite(res["controlA_median_hop_mean"])
                  and res["median_hop_S"] < res["controlA_median_hop_mean"])
    if reach_ok and effect_ok and med_ok:
        return "HARD_PASS", reach_ok, effect_ok, med_ok
    inside_band = bool(res["controlA_p5_k2"] <= res["reach_S_k2"] <= res["controlA_p95_k2"])
    if inside_band and not effect_ok:
        return "HARD_FAIL", reach_ok, effect_ok, med_ok
    return "MIDDLE_BAND", reach_ok, effect_ok, med_ok


def verdict_p1(res):
    beats_null = bool(res["margin_p2"] > res["null_p95"])
    effect_ok = bool(res["struct_margin"] >= STRUCT_EFFECT_BAR)
    if beats_null and effect_ok:
        return "HARD_PASS", beats_null, effect_ok
    inside_band = bool(res["null_p5"] <= res["margin_p2"] <= res["null_p95"])
    if inside_band and not effect_ok:
        return "HARD_FAIL", beats_null, effect_ok
    return "MIDDLE_BAND", beats_null, effect_ok


def verdict_p3(res):
    hub_c = res["hub_conc_mean"]
    s_c = res["s_conc_mean"]
    if not (np.isfinite(hub_c) and np.isfinite(s_c)):
        return "INSUFFICIENT", False, False
    margin_ok = bool(hub_c <= s_c - P3_CONC_MARGIN and hub_c < P3_HUB_ABS_MAX)
    fail = bool(hub_c >= s_c - 0.1)
    if margin_ok:
        return "HARD_PASS", margin_ok, fail
    if fail:
        return "HARD_FAIL", margin_ok, fail
    return "MIDDLE_BAND", margin_ok, fail


def compute_verdict(res, prov):
    p2, p2_reach, p2_eff, p2_med = verdict_p2(res)
    p1, p1_null, p1_eff = verdict_p1(res)
    p3, p3_marg, p3_fail = verdict_p3(res)

    if p2 == "HARD_PASS" and p1 == "HARD_PASS":
        headline = "HARD_PASS_GROUNDING_STRUCTURAL"
    elif p2 == "HARD_FAIL" or p1 == "HARD_FAIL":
        headline = "HARD_FAIL_GROUNDING_NOT_STRUCTURAL"
    else:
        headline = "MIDDLE_BAND_PARTIAL"

    msg = (
        "%s || P2=%s P1_labelshuffle=%s P3=%s || "
        "P2: reach_S(k<=2)=%.3f vs randMean=%.3f (margin=%.3f>=%.2f?%s) randP95=%.3f (beat?%s) "
        "medHop_S=%s<randMed=%.2f?%s || "
        "P1: real_margin=%.3f vs labelShuffleNull mean=%.3f p95=%.3f (beat_p95?%s struct_margin=%.3f>=%.2f?%s) "
        "n_shuffle=%d || P3: hub_conc=%.3f S_conc=%.3f (margin>=%.2f?%s) || "
        "reach_S[k=1..%d]=%s coverage=%.1f%% n_lcc=%d |S|=%d |A|=%d nRand=%d run=%s" % (
            headline, p2, p1, p3,
            res["reach_S_k2"], res["controlA_mean_k2"], res["margin_p2"], P2_EFFECT_BAR, p2_eff,
            res["controlA_p95_k2"], p2_reach, _fmt(res["median_hop_S"]), res["controlA_median_hop_mean"], p2_med,
            res["margin_p2"], res["null_mean"], res["null_p95"], p1_null, res["struct_margin"],
            STRUCT_EFFECT_BAR, p1_eff, res["n_label_shuffle"],
            res["hub_conc_mean"], res["s_conc_mean"], P3_CONC_MARGIN, p3_marg,
            KMAX, ["%.3f" % r for r in res["reach_S"]],
            100.0 * prov["coverage_frac"], prov["n_lcc"], prov["n_seed"], prov["n_targets"],
            res["n_random_draws"], RUN_MODE))

    gates = dict(
        headline=headline, p2_verdict=p2, p1_labelshuffle_verdict=p1, p3_verdict=p3,
        p2=dict(reach_S_k2=res["reach_S_k2"], controlA_mean_k2=res["controlA_mean_k2"],
                controlA_p95_k2=res["controlA_p95_k2"], controlA_p5_k2=res["controlA_p5_k2"],
                margin_p2=res["margin_p2"], effect_bar=P2_EFFECT_BAR, reach_beats_p95=p2_reach,
                effect_ok=p2_eff, median_hop_S=res["median_hop_S"],
                controlA_median_hop_mean=res["controlA_median_hop_mean"], median_ok=p2_med),
        p1=dict(real_margin=res["margin_p2"], null_mean=res["null_mean"], null_p95=res["null_p95"],
                null_p5=res["null_p5"], struct_margin=res["struct_margin"], effect_bar=STRUCT_EFFECT_BAR,
                beats_null_p95=p1_null, effect_ok=p1_eff, n_label_shuffle=res["n_label_shuffle"]),
        p3=dict(hub_conc_mean=res["hub_conc_mean"], s_conc_mean=res["s_conc_mean"],
                margin=P3_CONC_MARGIN, hub_abs_max=P3_HUB_ABS_MAX, margin_ok=p3_marg, fail=p3_fail),
        bands=dict(P2_EFFECT_BAR=P2_EFFECT_BAR, STRUCT_EFFECT_BAR=STRUCT_EFFECT_BAR, P2_EVAL_K=P2_EVAL_K,
                   P3_CONC_MARGIN=P3_CONC_MARGIN, P3_HUB_ABS_MAX=P3_HUB_ABS_MAX, CONC_LOW=CONC_LOW,
                   KMAX=KMAX, N_SEED=N_SEED, N_RANDOM_DRAWS=N_RANDOM_DRAWS, N_LABEL_SHUFFLE=N_LABEL_SHUFFLE),
    )
    return headline, msg, gates


# ============================ real seed/target build ==========================
def build_real_sets(labels, deg, conc, n_seed):
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
    seed_S, target_A, hub_seed = _select_sets_from_y(y, is_stop, deg, n_seed)
    prov = dict(
        n_lcc=m, n_covered=int(covered.sum()), coverage_frac=float(covered.mean()),
        n_eligible=int((covered & (~is_stop)).sum()), n_stop_excluded=int((covered & is_stop).sum()),
        n_seed=int(seed_S.shape[0]), n_targets=int(target_A.shape[0]),
        S_conc_mean=float(np.nanmean(y[seed_S])) if seed_S.size else float("nan"),
        S_conc_min=float(np.nanmin(y[seed_S])) if seed_S.size else float("nan"),
        A_conc_mean=float(np.nanmean(y[target_A])) if target_A.size else float("nan"),
        A_conc_max=float(np.nanmax(y[target_A])) if target_A.size else float("nan"),
        hub_conc_mean=float(np.nanmean(y[hub_seed])) if hub_seed.size else float("nan"),
    )
    return dict(y=y, is_stop=is_stop, seed_S=seed_S, target_A=target_A, hub_seed=hub_seed, prov=prov)


# ============================ synthetic controls ==============================
def _synthetic_grounded_graph(seed=11):
    """Deterministic synthetic graph sized so reach fractions CONCENTRATE (low variance) -> the negative
    (label-shuffled) control fails ROBUSTLY, not just probabilistically. Genuinely grounded:
      - CONCRETE ANCHORS (S, conc=4.8): the grounded floor.
      - ABSTRACT TARGETS (A, conc=1.7): an ISOLATED abstract mesh whose only route to the concrete floor is
        via bridge edges from anchors.
      - BACKGROUND (mid-conc 3.0): a dense-ish bulk connected to anchors + itself but NOT to the abstract
        mesh -> random seeds land here, far from A -> low reach (grounded seeds beat them).
      - LOW-conc HUBS (conc=1.5): highest-degree nodes (Prediction 3).
    Returns (labels, edges_uv, indptr, indices, deg, y, is_stop)."""
    rng = np.random.default_rng(seed)
    C, T, B, NHUB = 150, 400, 3000, 5
    anc = ["anc%d" % i for i in range(C)]
    tar = ["tar%d" % i for i in range(T)]
    bg = ["bg%d" % i for i in range(B)]
    hub = ["hub%d" % i for i in range(NHUB)]
    labels = anc + tar + bg + hub
    idx = {w: k for k, w in enumerate(labels)}
    edges = set()

    def _add(x, y_):
        a, b = idx[x], idx[y_]
        if a != b:
            edges.add((a, b) if a < b else (b, a))

    for i in range(B):
        for _ in range(4):
            _add("bg%d" % i, "bg%d" % int(rng.integers(0, B)))
    for i in range(B - 1):
        _add("bg%d" % i, "bg%d" % (i + 1))
    for i in range(C):
        for _ in range(3):
            _add("anc%d" % i, "bg%d" % int(rng.integers(0, B)))
    for i in range(T - 1):
        _add("tar%d" % i, "tar%d" % (i + 1))
    for i in range(T):
        _add("tar%d" % i, "tar%d" % int(rng.integers(0, T)))
        _add("tar%d" % i, "anc%d" % (i % C))         # bridges: only concrete->abstract crossing edges
    for h in range(NHUB):
        for _ in range(300):
            _add("hub%d" % h, "bg%d" % int(rng.integers(0, B)))

    edges_uv = np.array(sorted(edges), dtype=np.int64)
    order = np.lexsort((edges_uv[:, 1], edges_uv[:, 0]))
    edges_uv = edges_uv[order]
    n = len(labels)
    indptr, indices, deg = _csr_from_edges(edges_uv, n)
    y = np.full(n, np.nan, dtype=np.float64)
    for i in range(C):
        y[idx["anc%d" % i]] = 4.8
    for i in range(T):
        y[idx["tar%d" % i]] = 1.7
    for i in range(B):
        y[idx["bg%d" % i]] = 3.0
    for h in range(NHUB):
        y[idx["hub%d" % h]] = 1.5
    is_stop = np.zeros(n, dtype=bool)
    return labels, edges_uv, indptr, indices, deg, y, is_stop


# ============================ self-test =======================================
def _selftest():
    print("[selftest] grounding label-shuffle-null: positive-control PASSES (achievable), form-without-"
          "content NEGATIVE FAILS with margin (validity preflight, all 4 checks)...", flush=True)
    n_seed_st = 150
    exercised_gates = set()

    labels, e, ip, ix, deg, y, is_stop = _synthetic_grounded_graph(seed=11)
    n = len(labels)
    S, A, hub = _select_sets_from_y(y, is_stop, deg, n_seed_st)
    assert S.size >= 50 and A.size >= 100, "SELFTEST setup: too few S/A (%d/%d)" % (S.size, A.size)

    # ---------- POSITIVE control (genuinely grounded) ----------
    rng = np.random.default_rng(101)
    p2 = grounded_advantage(ip, ix, n, S, A, 20, rng, want_full=True)
    null_m = label_shuffle_null(ip, ix, deg, n, y, is_stop, n_seed_st, 12, 5, rng)
    pos = dict(reach_S=p2["reach_S"], reach_S_k2=p2["reach_S_k2"], median_hop_S=p2["median_hop_S"],
               controlA_mean_k2=p2["controlA_mean_k2"], controlA_p95_k2=p2["controlA_p95_k2"],
               controlA_p5_k2=p2["controlA_p5_k2"], controlA_median_hop_mean=p2["controlA_median_hop_mean"],
               margin_p2=p2["margin"], null_mean=float(null_m.mean()),
               null_p95=float(np.percentile(null_m, 95)), null_p5=float(np.percentile(null_m, 5)),
               struct_margin=p2["margin"] - float(null_m.mean()),
               hub_conc_mean=float(np.nanmean(y[hub])), s_conc_mean=float(np.nanmean(y[S])))
    p2v, _a, _b, _c = verdict_p2(pos)
    p1v, _d, _e2 = verdict_p1(pos)
    pc_p2_pass = (p2v == "HARD_PASS")
    pc_p1_pass = (p1v == "HARD_PASS")
    assert pc_p2_pass, ("SELFTEST(positive) FAIL: P2 not HARD_PASS on grounded synthetic "
                        "(reach_S_k2=%.3f randMean=%.3f margin=%.3f randP95=%.3f)"
                        % (pos["reach_S_k2"], pos["controlA_mean_k2"], pos["margin_p2"], pos["controlA_p95_k2"]))
    assert pc_p1_pass, ("SELFTEST(positive) FAIL: P1 not HARD_PASS on grounded synthetic "
                        "(real_margin=%.3f nullMean=%.3f nullP95=%.3f struct=%.3f)"
                        % (pos["margin_p2"], pos["null_mean"], pos["null_p95"], pos["struct_margin"]))
    positive_control_passed = pc_p2_pass and pc_p1_pass

    # metric-moves: reach_S(k<=2) moves from an EMPTY seed set (0.0) to grounded seeds (>0).
    dist_empty = multi_source_bfs(ip, ix, np.array([], dtype=np.int64), n, KMAX)
    reach_empty, _me, _ue = reach_curve(dist_empty, A, KMAX)
    reach_null_k2 = reach_empty[P2_EVAL_K - 1]
    reach_grounded_k2 = pos["reach_S_k2"]

    # full-gates-exercised: cardinality (draw counts) + arms-differ at self-test scale.
    if p2["n_random_draws"] == 20 and null_m.shape[0] == 12:
        exercised_gates.add("cardinality")
    dist_H = multi_source_bfs(ip, ix, hub, n, KMAX)
    reach_H, _mh, _uh = reach_curve(dist_H, A, KMAX)
    sigs = {_reach_sig(pos["reach_S"]),
            _reach_sig([pos["controlA_mean_k2"], pos["controlA_p95_k2"]]),
            _reach_sig([pos["null_mean"], pos["null_p95"], pos["null_p5"]]),
            _reach_sig(reach_H)}
    assert len(sigs) >= 3, "SELFTEST(arms_differ) FAIL: <3 distinct arm sigs"
    exercised_gates.add("arms_differ")

    # ---------- NEGATIVE control (form-without-content: shuffled labels) ----------
    # Each REPEAT = mean over N_INNER independent label-shufflings, so the per-repeat score is a stable
    # estimate of the null margin (~0) -> the must-fail check fails ROBUSTLY, not by luck. Same topology,
    # only concreteness permuted; SAME grounded_advantage code path.
    N_REPEATS, N_INNER = 4, 8
    neg_p2_margins, neg_struct_margins = [], []
    covered_ids = np.where(np.isfinite(y))[0]
    y_cov = y[covered_ids].copy()
    for r in range(N_REPEATS):
        p2s, sts = [], []
        for j in range(N_INNER):
            rngp = np.random.default_rng(9000 + r * 100 + j)
            y2 = np.full(n, np.nan, dtype=np.float64)
            y2[covered_ids] = y_cov[rngp.permutation(covered_ids.shape[0])]
            S2, A2, _h2 = _select_sets_from_y(y2, is_stop, deg, n_seed_st)
            if S2.size < 20 or A2.size < 40:
                p2s.append(0.0)
                sts.append(0.0)
                continue
            rng2 = np.random.default_rng(200 + r * 100 + j)
            adv = grounded_advantage(ip, ix, n, S2, A2, 20, rng2)
            nm = label_shuffle_null(ip, ix, deg, n, y2, is_stop, n_seed_st, 8, 3, rng2)
            p2s.append(adv["margin"])
            sts.append(adv["margin"] - float(nm.mean()))
        neg_p2_margins.append(float(np.mean(p2s)))
        neg_struct_margins.append(float(np.mean(sts)))

    # ---------- VALIDITY PREFLIGHT (all four declared; poster-child gate) ----------
    ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": positive_control_passed,
         "control_name": "synthetic_grounded_graph", "headline_name": "P2_and_P1_HARD_PASS"},
        {"kind": "metric_moves", "metric_name": "reach_S_k2",
         "before": reach_null_k2, "after": reach_grounded_k2},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["cardinality", "arms_differ"],
         "exercised_gates": exercised_gates},
        {"kind": "negative_control_margin", "control_scores": neg_p2_margins,
         "headline_threshold": P2_EFFECT_BAR, "higher_is_pass": True, "margin": 0.02,
         "control_name": "form_without_content_P2"},
        {"kind": "negative_control_margin", "control_scores": neg_struct_margins,
         "headline_threshold": STRUCT_EFFECT_BAR, "higher_is_pass": True, "margin": 0.01,
         "control_name": "form_without_content_labelshuffle"},
    ], run_mode="self_test")

    assert max(neg_p2_margins) < P2_EFFECT_BAR, \
        "SELFTEST(negative) FAIL: a shuffled-label repeat cleared the P2 effect bar: %s" % neg_p2_margins
    assert max(neg_struct_margins) < STRUCT_EFFECT_BAR, \
        "SELFTEST(negative) FAIL: a shuffled-label repeat cleared the P1 struct bar: %s" % neg_struct_margins

    print("[selftest] PASS: positive P2 reach_S_k2=%.3f>randMean=%.3f (margin=%.3f) P1 real_margin=%.3f>"
          "nullP95=%.3f (struct=%.3f) | negative P2 margins=%s (all<%.2f) struct margins=%s (all<%.2f) | "
          "metric-moves %.3f->%.3f | gates=%s | preflight_ok=%s" %
          (pos["reach_S_k2"], pos["controlA_mean_k2"], pos["margin_p2"], pos["margin_p2"], pos["null_p95"],
           pos["struct_margin"], ["%.3f" % v for v in neg_p2_margins], P2_EFFECT_BAR,
           ["%.3f" % v for v in neg_struct_margins], STRUCT_EFFECT_BAR,
           reach_null_k2, reach_grounded_k2, sorted(exercised_gates), ok), flush=True)


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
    _write_start_marker(out_dir, RUN_MODE, N_RANDOM_DRAWS + N_LABEL_SHUFFLE)
    t0 = time.time()
    _log("config: mode=%s N_SEED=%d N_RANDOM_DRAWS=%d N_LABEL_SHUFFLE=%d N_RAND_PER_SHUFFLE=%d KMAX=%d CONC_LOW=%.1f"
         % (RUN_MODE, N_SEED, N_RANDOM_DRAWS, N_LABEL_SHUFFLE, N_RAND_PER_SHUFFLE, KMAX, CONC_LOW))

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
    sets = build_real_sets(labels, deg, conc, N_SEED)
    prov = sets["prov"]
    _log("join: coverage=%.1f%% (%d/%d) eligible=%d |S|=%d (conc_mean=%.2f,min=%.2f) |A|=%d "
         "(conc_mean=%.2f,max=%.2f) hub_conc_mean=%.2f"
         % (100 * prov["coverage_frac"], prov["n_covered"], prov["n_lcc"], prov["n_eligible"],
            prov["n_seed"], prov["S_conc_mean"], prov["S_conc_min"], prov["n_targets"],
            prov["A_conc_mean"], prov["A_conc_max"], prov["hub_conc_mean"]))

    if prov["n_seed"] < MIN_SEEDS or prov["n_targets"] < MIN_TARGETS:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_DATA_INSUFFICIENT", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="insufficient seeds/targets: |S|=%d (need>=%d) |A|=%d (need>=%d) coverage=%.1f%%"
                        % (prov["n_seed"], MIN_SEEDS, prov["n_targets"], MIN_TARGETS,
                           100 * prov["coverage_frac"]),
            summary="data insufficient", elapsed_s=time.time() - t0, provenance=prov))
        raise SystemExit(1)

    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")
    rng = np.random.default_rng(7)
    res = run_audit(indptr, indices, deg, n, sets["y"], sets["is_stop"], sets["seed_S"], sets["target_A"],
                    sets["hub_seed"], prov, rng, hb_path=hb_path)
    _log("P2: reach_S(k<=2)=%.3f randMean=%.3f randP95=%.3f margin=%.3f | P1: real_margin=%.3f nullMean=%.3f "
         "nullP95=%.3f struct=%.3f | P3: hub_conc=%.3f S_conc=%.3f"
         % (res["reach_S_k2"], res["controlA_mean_k2"], res["controlA_p95_k2"], res["margin_p2"],
            res["margin_p2"], res["null_mean"], res["null_p95"], res["struct_margin"],
            res["hub_conc_mean"], res["s_conc_mean"]))

    if res["n_random_draws"] != N_RANDOM_DRAWS or res["n_label_shuffle"] != N_LABEL_SHUFFLE:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="expected P2 draws=%d label-shuffles=%d got draws=%d shuffles=%d"
                        % (N_RANDOM_DRAWS, N_LABEL_SHUFFLE, res["n_random_draws"], res["n_label_shuffle"]),
            summary="cardinality breach", elapsed_s=time.time() - t0, provenance=prov, audit=res))
        raise SystemExit(1)

    sigs = res["arm_sigs"]
    if len(set(sigs.values())) < 3:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="arm sigs not distinct: %s" % sigs, summary="arms identical",
            elapsed_s=time.time() - t0, provenance=prov, audit=res))
        raise SystemExit(1)

    headline, msg, gates = compute_verdict(res, prov)
    elapsed = time.time() - t0
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=headline, verdict_msg=msg, summary=msg[:200],
        run_mode=RUN_MODE, n_seeds=1, elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        arms_differ_verified=True, arm_sigs=sigs, gates=gates, provenance=prov, audit=res,
        config=dict(N_SEED=N_SEED, N_RANDOM_DRAWS=N_RANDOM_DRAWS, N_LABEL_SHUFFLE=N_LABEL_SHUFFLE,
                    N_RAND_PER_SHUFFLE=N_RAND_PER_SHUFFLE, KMAX=KMAX, CONC_LOW=CONC_LOW,
                    P2_EFFECT_BAR=P2_EFFECT_BAR, STRUCT_EFFECT_BAR=STRUCT_EFFECT_BAR),
    )
    write_metrics(out_dir, metrics, results=[{"elapsed_s": elapsed}])
    _log("VERDICT: %s" % msg)
    _log("done (%.1fs)" % elapsed)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    _selftest()                 # synthetic positive+negative controls + validity preflight; asserts fire first
    if _ARGS.self_test:
        _od = get_output_dir(ANCHOR_NAME)
        write_metrics(_od, dict(
            verdict="SELFTEST_PASS", run_mode="self_test", anchor_name=ANCHOR_NAME,
            verdict_msg="SELFTEST_PASS: positive-control clears P2+P1 bars (achievable); form-without-content "
                        "label-shuffle FAILS both with margin; reach moves 0->grounded; cardinality+"
                        "arms_differ exercised; validity-preflight all 4 declared",
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
