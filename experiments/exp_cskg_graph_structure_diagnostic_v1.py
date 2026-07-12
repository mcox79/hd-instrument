"""
cskg_graph_structure_diagnostic_v1 -- PURE GRAPH-STRUCTURE DIAGNOSTIC on the CSKG cross-cutting
commonsense graph and its k=12 dense core (the actual fair-test graph). ZERO training, ZERO substrate
vectors, ZERO GPU, ZERO new data acquisition (reuses data/grounding_testbed/cskg.tsv.gz already on disk).

QUESTION (two-part, pre-registered in
  notes/research_kg_degree_community_diagnostic_2026-07-12.md, section C + the four falsifiable
  predictions -- this cell operationalizes Predictions 1/2/3/4 verbatim):
  (A) How big is frequency's structural moat on the actual test graph, and does it grow with scale?
  (B) Does the graph structurally support a FACTORIZED (reusable-relation-operator) map-builder, or is it
      too hub-dominated / schema-blurred for one shared operator per relation to help?

EIGHT MEASURES (note section C, computed on three graphs: FULL / CROSS-CUTTING / 12-CORE test graph):
  1. Degree-distribution power-law fit (Clauset-Shalizi-Newman discrete MLE: alpha, x_min, KS-distance;
     vs exponential-tail alternative) -- NOT a log-log eyeball slope.
  2. Gini coefficient of the degree sequence (closed form).
  3. Max-degree-to-mean-degree ratio, measured WITHIN each induced subgraph.
  4. Global clustering coefficient (sampled average local clustering; scalable + unbiased).
  5. PER-RELATION cardinality profile (TransH-style tphr/hptr => 1-1 / 1-N / N-1 / N-N; symmetry fraction)
     on the FULL relation set (58 relations) -- this is where Prediction 2's SYNONYM/IS_A test lives, since
     the cross-cutting spine STRIPS the lexical relations. The single sharpest structural predictor.
  6. Community detection + modularity (pure-python Louvain local-moving, parity-safe -- no networkx dep) on
     the 12-core test graph, with a schema cross-tab (community vs relation-type-class AND vs source
     provenance). Answers: are communities schema-flavoured or one undifferentiated blob?
  7. Core-periphery: k-core decomposition (Batagelj-Zaversnik) of the cross-cutting graph; the ultra-dense
     k>=20 kernel; and the STRUCTURAL cross-reference of that kernel against the high-degree tertile (how
     concentrated is the hub mass). NOTE: the PERFORMANCE-margin concentration (POP-vs-ROTATE inside the
     kernel) needs the course_c model scores and is OUT OF SCOPE for this pure-graph cell -- Prediction 4 is
     answered at the STRUCTURAL-precondition level only (marked HYPOTHESIZED for the performance half).
  8. Fair-stratum-size-vs-degree-cutoff curve: sweep degree-percentile cutoffs; at each report (a) fraction
     of entities below cutoff (the "fair" beatable population) and (b) fraction of total edge-mass below
     cutoff (how much the fair zone shrinks as a share of mass). Direct measurement of the scaling drill's
     HEADLINE-4 prediction on the REAL degree distribution rather than generic Barabasi-Albert theory.

GRAPHS:
  G_full  = simple undirected graph over ALL 58 relations (2.16M nodes / ~5.17M simple edges).
  G_xcut  = simple undirected over the CROSS-CUTTING commonsense spine (501k / ~1.18M).
  G_core  = the k=12 core of G_xcut -- the LOAD-BEARING graph (matches course_c k_core=12 test graph).

PRE-REGISTERED BANDS (verbatim from the note's four falsifiable predictions; picked BEFORE the run):
  P1 (12-core is moderately, not extremely, hub-dominated):
     HARD-PASS: max/mean-degree ratio on G_core in [P1_RATIO_LO, P1_RATIO_HI]=[10,50] AND
                Gini in [P1_GINI_LO, P1_GINI_HI]=[0.35,0.60].
     HARD-FAIL: max/mean ratio > P1_RATIO_FAIL=100 OR Gini > P1_GINI_FAIL=0.70 on G_core.
  P2 (per-relation cardinality heterogeneity reproduces the functional-form gap from pure structure):
     HARD-PASS: the SYNONYM-class (symmetric) and IS_A-class (1-to-N) relations rank in the WORST
                (least single-operator-friendly) tertile of the full relation set by the composite
                operator-difficulty score.
     HARD-FAIL: SYNONYM/IS_A land in the BEST tertile (no structural signal; gap is fit-specific).
  P3 (map-builder prerequisite -- community structure exists AND is schema-flavoured):
     HARD-PASS (supports factorized map-builder, partially): modularity Q > P3_Q_PASS=0.30 on G_core AND
                communities show non-uniform relation-type/source composition
                (schema_alignment > P3_ALIGN_PASS above the uniform-null baseline).
     HARD-FAIL (too hub-dominated / schema-poor): Q < P3_Q_FAIL=0.15 OR near-uniform relation-type mixing
                (schema_alignment <= P3_ALIGN_FAIL).
  P4 (frequency's win localizes to a small ultra-dense kernel -- STRUCTURAL precondition only):
     STRUCTURAL-PASS: the k>=20 ultra-dense kernel is a small, sharply-identifiable node set (kernel node
                fraction < P4_KERNEL_NODE_FRAC=0.20 of G_core) that carries a DISPROPORTIONATE degree-mass
                share (kernel edge-mass share / kernel node share > P4_MASS_CONCENTRATION=2.0).
     STRUCTURAL-FAIL: no sharp kernel (mass share ~ node share; concentration <= 1.3).
     (performance-margin concentration = HYPOTHESIZED@this prereg; needs course_c model scores.)

HEADLINE = the map-builder decision, driven primarily by P3 (does the graph support a factorized operator),
with P1/P2/P4 as sub-verdicts reported in gates + verdict_msg.

## Compute architecture
Class (b) sequential-CPU with justification: pure combinatorial graph computation (streaming triple parse,
union-find, Batagelj-Zaversnik k-core, CSR neighbourhood gather, local-moving modularity optimisation, dict
group-bys). NO substrate vectors, NO bind/unbind, NO matmul, NO torch => GPU batching does not apply.
Neighbourhood gathers + degree math are numpy-vectorized. Storage strategy: no_storage / no_composition.
Routes to remote_cpu_queue (CPU; keeps the laptop free per the no-local-smokes lock). numpy + stdlib ONLY
(parity-safe: same self-contained discipline as exp_grounding_percolation_reachability_cskg_v1, which ran on
the remote runner without networkx). Community detection is a pure-python Louvain local-moving optimiser, NOT
a networkx/python-louvain call, so there is NO optional-dependency parity risk on the remote runner.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor/cardinality):
  - arms_differ_verified at self-test (>=3 distinct graph fingerprints: schema-clean control / schema-blurred
    control / real-apparatus planted core are not bit-identical).
  - final_metrics_atomicity=tmp_replace (write_metrics + crash-writer both tmp+os.replace).
  - except SystemExit: raise BEFORE except Exception; no BaseException.
  - crlb_n/a: no quantitative estimator-noise floor -- this is a graph-structure census + a
    distribution/partition audit, not an estimator. Discriminators are threshold bands on measured graph
    statistics; the self-test proves each band FIRES by construction on planted positive/negative controls.
  - baseline_in_band: the "baseline"/null is the schema-BLURRED hub-dominated synthetic control, which by
    construction FAILS P1 and P3; the schema-CLEAN synthetic control by construction PASSES. Both proven in
    self-test so the discriminators are shown to separate. On the REAL graph the outcome is an OPEN
    MEASUREMENT reported as the verdict, not a smoke-abort.
  - discriminator survives scale (analytical, option B): the measures are graph-size-invariant ratios and
    partition-quality scores (Gini, max/mean, modularity Q, cardinality ratios), NOT accuracies that saturate
    with N. The 12-core is the actual full-scale test graph, so there is no smaller-than-scale smoke gap.
  - HP bands strictly declared above (P1 ratio+Gini bands; P2 worst-tertile; P3 Q>0.30 + schema alignment;
    P4 kernel node-frac + mass-concentration).
  - cardinality_ok: EXPECTED sweep units = len(FAIR_PCTL_GRID) fair-stratum points; short count ->
    HARD_FAIL_CARDINALITY_BREACH_META_RULE_H. Per-relation profile reports n_relations actually measured.
  - per-unit failure-class instrumentation (no bare except; specific classes; recorded to metrics).
  - calibration_check=default_ok_for_this_regime (CSN-MLE, Gini, Batagelj-Zaversnik, local-moving Louvain are
    parameter-free / literature-standard apparatus; the only free knobs are the pre-registered band cutoffs).
  - progress_logging=print_flush_true (all logs flush=True; heartbeat during the graph builds + Louvain).
  - cell_chunked=false (single graph census; no per-seed chunking); start_marker + crash_diagnostic present.

ASCII-only. No em dashes in output. RUN_MODE defaults to full (runner invokes with no argv).
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
import zlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "cskg_graph_structure_diagnostic_v1"
TESTBED = REPO / "data" / "grounding_testbed"
CSKG_PATH = TESTBED / "cskg.tsv.gz"
CSKG_URL = "https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content"

# ---- run mode / config -------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ---- pre-registered bands (picked BEFORE the run; lifted from the note) -------
# P1 -- 12-core degree skew
P1_RATIO_LO, P1_RATIO_HI = 10.0, 50.0     # HARD-PASS max/mean-degree ratio band
P1_RATIO_FAIL = 100.0                     # HARD-FAIL above this
P1_GINI_LO, P1_GINI_HI = 0.35, 0.60       # HARD-PASS Gini band
P1_GINI_FAIL = 0.70                       # HARD-FAIL above this
# P2 -- per-relation cardinality
CARD_MANY_THRESH = 1.5                    # TransH: avg-per-side >= 1.5 => "many" side
P2_WORST_FRAC = 1.0 / 3.0                 # bottom tertile = "worst" operator-difficulty
P2_TARGET_RELS = ("synonym", "isa")       # relation tokens Prediction 2 says must be worst
# P3 -- community / modularity on the 12-core
P3_Q_PASS = 0.30                          # modularity clear-structure floor
P3_Q_FAIL = 0.15                          # weak/no-structure ceiling
P3_ALIGN_PASS = 0.15                      # schema-alignment lift above uniform-null (HARD-PASS)
P3_ALIGN_FAIL = 0.05                      # near-uniform mixing ceiling (HARD-FAIL)
# P4 -- ultra-dense kernel (structural)
KERNEL_K = 20                             # k>=KERNEL_K = ultra-dense kernel (per the k-core note)
P4_KERNEL_NODE_FRAC = 0.20                # kernel must be < this fraction of G_core nodes (small kernel)
P4_MASS_CONCENTRATION = 2.0              # kernel edge-mass share / node share must exceed this (disprop.)
P4_MASS_CONCENTRATION_FAIL = 1.3         # concentration at/below this = diffuse, no sharp kernel
# item 8 -- fair-stratum cutoff sweep
FAIR_PCTL_GRID = [10, 25, 33, 50, 67, 75, 90]
CORE_K = 12                               # the load-bearing test graph = k=CORE_K core of G_xcut
CLUST_SAMPLE = 3000                       # nodes sampled for average local clustering coefficient
POWERLAW_XMIN_CAP = 200                   # cap on x_min scan candidates (CSN discrete MLE)

if RUN_MODE == "smoke":
    CSKG_MAX_LINES = 300000               # small slice: assembly + apparatus proof, NOT the full graph
    CAP_PER_REL = 40000
else:
    CSKG_MAX_LINES = 0                     # 0 = stream the whole graph
    CAP_PER_REL = 250000                  # per-relation directed-edge subsample cap (bounds memory)

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
# coarse schema-class map for the P3 community cross-tab (cross-cutting tokens only)
SCHEMA_CLASS = {
    "xattr": "atomic_event", "xwant": "atomic_event", "xeffect": "atomic_event", "xneed": "atomic_event",
    "xreact": "atomic_event", "xintent": "atomic_event", "owant": "atomic_event", "oeffect": "atomic_event",
    "oreact": "atomic_event",
    "locatednear": "spatial", "atlocation": "spatial", "partof": "spatial",
    "usedfor": "functional", "capableof": "functional", "receivesaction": "functional",
    "madeof": "functional", "createdby": "functional",
    "causes": "causal", "causesdesire": "causal", "hassubevent": "causal", "hasprerequisite": "causal",
    "hasfirstsubevent": "causal", "haslastsubevent": "causal", "entails": "causal", "motivatedbygoal": "causal",
    "mayhaveproperty": "property", "hasproperty": "property", "hasa": "property", "desires": "property",
    "notdesires": "property", "mannerof": "property", "obstructedby": "property",
}


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
    """Canonical relation token for a CSKG relation label.
    Returns (token, is_xcut). Lexical tokens return (token, False); cross-cutting return (token, True);
    unknown returns (last-path-segment, False)."""
    r = rel_label.lower()
    for tok in LEXICAL_REL_TOKENS:
        if tok in r:
            return tok, False
    for tok in XCUT_REL_TOKENS:
        if tok in r:
            return tok, True
    # fall back to a stable short label for the relation (keep for the full-graph 58-relation census)
    seg = r.split("/")[-1].split(":")[-1]
    return (seg or "other"), False


# ============================ data acquisition ================================
def _ensure_file(path, url, min_bytes):
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
        os.replace(tmp, str(path))
        _log("acquired %s" % url)
        return True
    except Exception as e:
        _log("self-acquire failed for %s: %s: %s" % (url, type(e).__name__, str(e)[:150]))
        return False


# ============================ streaming graph build ===========================
class GraphBuild:
    """Single streaming pass over cskg.tsv.gz. Accumulates:
      - global label->id
      - full simple-undirected edge codes (all relations), deduped at finalize
      - cross-cutting simple-undirected edge codes (spine relations only)
      - per-relation directed-triple census for cardinality (subsampled to CAP_PER_REL per relation)
      - per relation-token source-provenance counts (for the schema cross-tab context)
    Edge code = u*STRIDE + v with u<v (canonical). STRIDE fixed after node count known -> we store raw
    (u,v) int pairs in growable buffers and encode at finalize.
    """

    def __init__(self):
        self.lab2id = {}
        self.full_u = []          # list of np.int64 chunk arrays
        self.full_v = []
        self.xcut_u = []
        self.xcut_v = []
        self._bu, self._bv = [], []          # full pending buffers
        self._xu, self._xv = [], []          # xcut pending buffers
        # per-relation census: rel_token -> dict(heads=set, tails=set, n=int, dir_pairs=set(capped), src=Counter)
        self.rel = defaultdict(lambda: dict(heads=set(), tails=set(), n=0, dir_pairs=set(),
                                            n_sampled=0, src=defaultdict(int)))
        self.n_rows = 0
        self.n_edges_full_raw = 0
        self.n_edges_xcut_raw = 0

    def _id(self, w):
        i = self.lab2id.get(w)
        if i is None:
            i = len(self.lab2id)
            self.lab2id[w] = i
        return i

    def _flush(self):
        if self._bu:
            self.full_u.append(np.asarray(self._bu, dtype=np.int64))
            self.full_v.append(np.asarray(self._bv, dtype=np.int64))
            self._bu, self._bv = [], []
        if self._xu:
            self.xcut_u.append(np.asarray(self._xu, dtype=np.int64))
            self.xcut_v.append(np.asarray(self._xv, dtype=np.int64))
            self._xu, self._xv = [], []

    def add(self, w1, rel_label, w2, source):
        tok, is_xcut = _rel_token(rel_label)
        h = self._id(w1)
        t = self._id(w2)
        # per-relation directed census (subsampled deterministically by triple hash to bound memory)
        rc = self.rel[tok]
        rc["n"] += 1
        # deterministic (crc32, NOT builtin hash which is per-process randomized): keep a thin uniform
        # tail beyond the cap so cardinality ratios stay representative for very large relations.
        keep = (CAP_PER_REL <= 0) or (rc["n_sampled"] < CAP_PER_REL) or \
               ((zlib.crc32(("%s|%s|%s" % (tok, w1, w2)).encode("utf-8", "replace")) & 0xFFFF) < 4)
        if keep and rc["n_sampled"] < (CAP_PER_REL * 2 if CAP_PER_REL > 0 else 1 << 62):
            rc["heads"].add(h)
            rc["tails"].add(t)
            rc["dir_pairs"].add((h, t))
            rc["src"][source] += 1
            rc["n_sampled"] += 1
        # simple undirected structural edge (skip self-loops)
        if h != t:
            u, v = (h, t) if h < t else (t, h)
            self._bu.append(u)
            self._bv.append(v)
            self.n_edges_full_raw += 1
            if is_xcut:
                self._xu.append(u)
                self._xv.append(v)
                self.n_edges_xcut_raw += 1
        if len(self._bu) >= (1 << 20):
            self._flush()

    def finalize(self):
        self._flush()
        n_nodes = len(self.lab2id)
        stride = np.int64(n_nodes + 1)

        def _dedup(us, vs):
            if not us:
                return np.zeros((0, 2), dtype=np.int64)
            u = np.concatenate(us)
            v = np.concatenate(vs)
            code = u * stride + v
            code = np.unique(code)
            uu = (code // stride).astype(np.int64)
            vv = (code % stride).astype(np.int64)
            return np.stack([uu, vv], axis=1)

        full_edges = _dedup(self.full_u, self.full_v)
        xcut_edges = _dedup(self.xcut_u, self.xcut_v)
        return n_nodes, full_edges, xcut_edges


def _csr_from_edges(edges_uv, n):
    """Undirected CSR from canonical edge list [E,2] (u<v). Returns (indptr, indices, deg)."""
    if edges_uv.shape[0] == 0:
        return np.zeros(n + 1, dtype=np.int64), np.zeros(0, dtype=np.int64), np.zeros(n, dtype=np.int64)
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


# ============================ k-core (Batagelj-Zaversnik) =====================
def kcore_number(indptr, indices, deg, n):
    """Coreness (max k for which each node is in the k-core) via Batagelj-Zaversnik O(E). Returns core[n]."""
    core = deg.copy()
    if n == 0:
        return core
    md = int(core.max())
    # bin-sort vertices by current degree
    bin_ = np.zeros(md + 2, dtype=np.int64)
    for d in core:
        bin_[d] += 1
    start = 0
    for d in range(md + 1):
        c = bin_[d]
        bin_[d] = start
        start += c
    pos = np.zeros(n, dtype=np.int64)
    vert = np.zeros(n, dtype=np.int64)
    binptr = bin_.copy()
    for vtx in range(n):
        d = int(core[vtx])
        pos[vtx] = binptr[d]
        vert[binptr[d]] = vtx
        binptr[d] += 1
    # restore bin starts
    bin_ = np.concatenate([[0], np.cumsum(np.bincount(core, minlength=md + 1))]).astype(np.int64)
    deg_work = core.copy()
    for i in range(n):
        v = int(vert[i])
        dv = int(deg_work[v])
        for j in range(int(indptr[v]), int(indptr[v + 1])):
            u = int(indices[j])
            if deg_work[u] > deg_work[v]:
                du = int(deg_work[u])
                pu = int(pos[u])
                pw = int(bin_[du])
                w = int(vert[pw])
                if u != w:
                    vert[pu] = w
                    pos[w] = pu
                    vert[pw] = u
                    pos[u] = pw
                bin_[du] += 1
                deg_work[u] -= 1
    return deg_work


def induced_subgraph(edges_uv, keep_mask, n):
    """Induce subgraph on nodes where keep_mask True. Returns (sub_edges[E',2] remapped, old_ids, n_sub)."""
    old_ids = np.where(keep_mask)[0]
    remap = -np.ones(n, dtype=np.int64)
    remap[old_ids] = np.arange(old_ids.shape[0], dtype=np.int64)
    ke = keep_mask[edges_uv[:, 0]] & keep_mask[edges_uv[:, 1]]
    sub = remap[edges_uv[ke]]
    lo = np.minimum(sub[:, 0], sub[:, 1])
    hi = np.maximum(sub[:, 0], sub[:, 1])
    return np.stack([lo, hi], axis=1).astype(np.int64), old_ids, int(old_ids.shape[0])


def kcore_curve(edges_uv, n, ks):
    """Return {k: (n_nodes, internal_avg_deg)} for each k in ks, from the coreness numbers."""
    ip, ix, deg = _csr_from_edges(edges_uv, n)
    core = kcore_number(ip, ix, deg, n)
    out = {}
    for k in ks:
        mask = core >= k
        sub, _oi, ns = induced_subgraph(edges_uv, mask, n)
        avg = (2.0 * sub.shape[0] / ns) if ns else 0.0
        out[k] = (ns, avg)
    return core, out


# ============================ degree statistics ===============================
def gini(vals):
    """Gini coefficient of a non-negative sequence (closed form via sorted cumulative)."""
    x = np.sort(np.asarray(vals, dtype=np.float64))
    n = x.shape[0]
    if n == 0 or x.sum() == 0:
        return float("nan")
    idx = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * np.sum(idx * x) / (n * np.sum(x))) - (n + 1.0) / n)


def powerlaw_fit(deg, xmin_cap=POWERLAW_XMIN_CAP):
    """Discrete power-law MLE (Clauset-Shalizi-Newman). Scan x_min over observed values (capped), pick the
    x_min minimising the KS distance between empirical and fitted CCDF; return alpha, x_min, KS, n_tail, and
    a crude exponential-alternative KS for comparison. Continuous-approx MLE for alpha (fast + adequate for a
    diagnostic)."""
    d = np.asarray(deg, dtype=np.float64)
    d = d[d >= 1]
    if d.shape[0] < 50:
        return dict(alpha=float("nan"), x_min=float("nan"), ks=float("nan"), n_tail=int(d.shape[0]),
                    ks_exp=float("nan"), method="insufficient")
    cand = np.unique(d)
    cand = cand[cand >= 1]
    if cand.shape[0] > xmin_cap:
        cand = cand[np.linspace(0, cand.shape[0] - 1, xmin_cap).astype(int)]
    best = None
    for xmin in cand:
        tail = d[d >= xmin]
        nt = tail.shape[0]
        if nt < 50:
            continue
        # continuous MLE for alpha given x_min (Clauset eq. 3.1 with 0.5 correction)
        s = np.sum(np.log(tail / (xmin - 0.5)))
        if s <= 0:
            continue
        alpha = 1.0 + nt / s
        # KS distance between empirical CCDF and fitted power-law CCDF on the tail
        xs = np.sort(tail)
        emp = np.arange(nt, dtype=np.float64) / nt          # empirical CDF (below)
        fit_cdf = 1.0 - (xs / xmin) ** (1.0 - alpha)         # fitted CDF for continuous power law
        ks = float(np.max(np.abs(emp - fit_cdf)))
        if best is None or ks < best["ks"]:
            # exponential alternative fit on same tail: rate = 1/mean(tail - xmin + 1)
            shift = tail - xmin + 1.0
            rate = 1.0 / max(1e-9, float(np.mean(shift)))
            exp_cdf = 1.0 - np.exp(-rate * (xs - xmin + 1.0))
            ks_exp = float(np.max(np.abs(emp - exp_cdf)))
            best = dict(alpha=float(alpha), x_min=float(xmin), ks=ks, n_tail=int(nt),
                        ks_exp=ks_exp, method="csn_discrete_scan")
    if best is None:
        return dict(alpha=float("nan"), x_min=float("nan"), ks=float("nan"), n_tail=0,
                    ks_exp=float("nan"), method="no_valid_xmin")
    return best


def avg_clustering_sampled(indptr, indices, deg, n, n_sample, seed=7):
    """Unbiased sampled average local clustering coefficient. For sampled nodes with deg>=2, C_i =
    2*links_between_neighbours / (k*(k-1)). Returns (mean_C, n_used)."""
    rng = np.random.default_rng(seed)
    elig = np.where(deg >= 2)[0]
    if elig.shape[0] == 0:
        return float("nan"), 0
    take = min(n_sample, elig.shape[0])
    samp = rng.choice(elig, size=take, replace=False)
    cs = []
    for v in samp.tolist():
        nb = indices[indptr[v]:indptr[v + 1]]
        k = nb.shape[0]
        if k < 2:
            continue
        nbset = set(nb.tolist())
        links = 0
        # count edges among neighbours (iterate smaller side)
        for w in nb.tolist():
            ww = indices[indptr[w]:indptr[w + 1]]
            # intersection of ww with nbset, avoid double count by w<neighbour handled via /2 below
            links += int(np.count_nonzero(np.isin(ww, nb)))
        # each internal edge counted twice above
        c = links / (k * (k - 1))
        cs.append(c)
    return (float(np.mean(cs)) if cs else float("nan")), len(cs)


# ============================ per-relation cardinality =========================
def relation_cardinality(rel_census):
    """From the streaming per-relation directed census, compute TransH-style tphr/hptr, cardinality class,
    symmetry fraction, and a composite single-operator-difficulty score per relation. Returns list of dicts
    sorted by difficulty (hardest first)."""
    rows = []
    for tok, rc in rel_census.items():
        n = rc["n_sampled"]
        nh = len(rc["heads"])
        nt = len(rc["tails"])
        if n < 20 or nh == 0 or nt == 0:
            continue
        tphr = n / nh          # avg tails per head (1-to-N-ness)
        hptr = n / nt          # avg heads per tail (N-to-1-ness)
        many_h = hptr >= CARD_MANY_THRESH   # many heads per tail
        many_t = tphr >= CARD_MANY_THRESH   # many tails per head
        if not many_h and not many_t:
            cls = "1-1"
        elif many_t and not many_h:
            cls = "1-N"
        elif many_h and not many_t:
            cls = "N-1"
        else:
            cls = "N-N"
        # symmetry: fraction of directed pairs whose reverse is also present
        dp = rc["dir_pairs"]
        if dp:
            sym = float(np.mean([1.0 if (t, h) in dp else 0.0 for (h, t) in dp]))
        else:
            sym = float("nan")
        # composite single-operator-difficulty: many-ness (max of the two ratios, log-scaled) + symmetry.
        # higher = harder for a single global relation operator (per TransH/RotatE critique).
        many_score = math.log1p(max(tphr, hptr) - 1.0)
        difficulty = many_score + 1.5 * (0.0 if sym != sym else sym)
        rows.append(dict(rel=tok, n=rc["n"], n_sampled=n, n_heads=nh, n_tails=nt,
                         tphr=round(tphr, 3), hptr=round(hptr, 3), cls=cls, sym=round(sym, 4),
                         difficulty=round(float(difficulty), 4)))
    rows.sort(key=lambda r: -r["difficulty"])
    return rows


# ============================ Louvain (pure python) ===========================
def louvain(indptr, indices, deg, n, seed=7, max_pass=20, max_levels=2):
    """Pure-python Louvain local-moving modularity optimisation (unweighted undirected). Returns
    (labels[n], modularity_Q, n_communities). Parity-safe (numpy + stdlib only)."""
    if n == 0 or indices.shape[0] == 0:
        return np.zeros(n, dtype=np.int64), 0.0, (1 if n else 0)
    two_m = float(indices.shape[0])          # = 2*|E|
    m2 = two_m
    rng = np.random.default_rng(seed)

    # working graph as CSR with unit weights; supernode aggregation between levels
    cur_ptr, cur_idx = indptr.copy(), indices.copy()
    cur_deg = deg.astype(np.float64).copy()
    node_comm_global = np.arange(n, dtype=np.int64)   # maps original node -> current supernode
    nn = n

    for level in range(max_levels):
        comm = np.arange(nn, dtype=np.int64)
        sigma_tot = cur_deg.copy()               # sum of degrees in each community
        # k_i,in cache computed per move
        order = np.arange(nn)
        improved_any = False
        for _p in range(max_pass):
            rng.shuffle(order)
            moved = 0
            for v in order.tolist():
                cv = comm[v]
                kv = cur_deg[v]
                # links from v to each neighbour community
                nb = cur_idx[cur_ptr[v]:cur_ptr[v + 1]]
                if nb.shape[0] == 0:
                    continue
                nbc = comm[nb]
                # weight to each community (unit weights): count
                links = defaultdict(float)
                for c in nbc.tolist():
                    links[c] += 1.0
                # remove v from its community
                sigma_tot[cv] -= kv
                ki_in_cur = links.get(cv, 0.0)
                best_c = cv
                best_gain = 0.0
                # gain of moving to community c: links_to_c - sigma_tot[c]*kv/(2m)
                for c, l_to in links.items():
                    gain = l_to - sigma_tot[c] * kv / m2
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_c = c
                # also consider staying-as-own (gain vs cv baseline already relative)
                comm[v] = best_c
                sigma_tot[best_c] += kv
                if best_c != cv:
                    moved += 1
            if moved == 0:
                break
            improved_any = True
        # relabel communities compactly
        uniq, comm = np.unique(comm, return_inverse=True)
        n_comm = uniq.shape[0]
        # push labels to global mapping
        node_comm_global = comm[node_comm_global]
        if n_comm == nn or not improved_any:
            nn = n_comm
            break
        # aggregate: build supernode graph
        agg = defaultdict(float)
        agg_self = np.zeros(n_comm, dtype=np.float64)
        for v in range(nn):
            cv = int(comm[v])
            nb = cur_idx[cur_ptr[v]:cur_ptr[v + 1]]
            for w in nb.tolist():
                cw = int(comm[w])
                if cv == cw:
                    agg_self[cv] += 1.0
                else:
                    a, b = (cv, cw) if cv < cw else (cw, cv)
                    agg[(a, b)] += 1.0
        # rebuild CSR for supernodes (undirected). agg counts each cross edge twice (v->w and w->v).
        eu, ev, ew = [], [], []
        for (a, b), wgt in agg.items():
            eu.append(a); ev.append(b); ew.append(wgt / 2.0)
        # supernode degrees = sum of original degrees in community
        sdeg = np.bincount(comm, weights=cur_deg, minlength=n_comm).astype(np.float64)
        # build weighted CSR
        if eu:
            eu = np.asarray(eu, dtype=np.int64); ev = np.asarray(ev, dtype=np.int64)
            ew = np.asarray(ew, dtype=np.float64)
            src = np.concatenate([eu, ev]); dst = np.concatenate([ev, eu]); w = np.concatenate([ew, ew])
        else:
            src = np.zeros(0, dtype=np.int64); dst = np.zeros(0, dtype=np.int64); w = np.zeros(0)
        cnt = np.bincount(src, minlength=n_comm).astype(np.int64)
        nptr = np.zeros(n_comm + 1, dtype=np.int64); np.cumsum(cnt, out=nptr[1:])
        o = np.argsort(src, kind="stable")
        cur_ptr, cur_idx = nptr, dst[o].astype(np.int64)
        cur_deg = sdeg
        nn = n_comm
        # NOTE: self-loop weight (agg_self) folded into degree already via sdeg; unit-weight local-moving on
        # the aggregate is an approximation adequate for a diagnostic Q read (not an exact multilevel Louvain).

    labels = node_comm_global
    # modularity Q on the ORIGINAL graph from the final labels
    q = modularity(indptr, indices, deg, labels, two_m)
    uniqf = np.unique(labels)
    return labels, q, int(uniqf.shape[0])


def modularity(indptr, indices, deg, labels, two_m):
    """Newman modularity Q for an unweighted undirected graph given a labelling."""
    if two_m == 0:
        return 0.0
    # sum over edges of same-community indicator
    E = indices.shape[0]  # directed count = 2m
    same = 0.0
    # vectorized: for each directed endpoint pair (src via indptr, dst=indices)
    src = np.repeat(np.arange(deg.shape[0]), np.diff(indptr))
    same = float(np.sum(labels[src] == labels[indices]))  # counts each edge twice
    e_in = same / two_m           # 2 * (edges within) / 2m  = fraction of edge-ends inside communities
    # sum_c (sigma_tot_c / 2m)^2
    sigma = np.bincount(labels, weights=deg, minlength=int(labels.max()) + 1).astype(np.float64)
    a2 = float(np.sum((sigma / two_m) ** 2))
    return e_in - a2


def schema_alignment(edges_uv, edge_relclass, labels, n_comm):
    """For each community, the relation-CLASS composition of its INTERNAL edges. schema_alignment =
    mean over communities (weighted by internal-edge count) of the max relation-class fraction, MINUS the
    global max relation-class fraction (the uniform-null baseline). > 0 means communities are more
    relation-class-pure than the graph as a whole (schema-flavoured)."""
    # global class distribution
    classes = sorted(set(edge_relclass))
    cidx = {c: i for i, c in enumerate(classes)}
    gc = np.zeros(len(classes), dtype=np.float64)
    for c in edge_relclass:
        gc[cidx[c]] += 1
    global_max = float(gc.max() / gc.sum()) if gc.sum() else float("nan")
    # per-community internal-edge class histograms
    comm_hist = defaultdict(lambda: np.zeros(len(classes), dtype=np.float64))
    internal_tot = 0
    for e in range(edges_uv.shape[0]):
        a = labels[edges_uv[e, 0]]
        b = labels[edges_uv[e, 1]]
        if a == b:
            comm_hist[a][cidx[edge_relclass[e]]] += 1
            internal_tot += 1
    if internal_tot == 0:
        return float("nan"), global_max, 0
    num = 0.0
    den = 0.0
    for c, h in comm_hist.items():
        tot = h.sum()
        if tot <= 0:
            continue
        num += tot * float(h.max() / tot)
        den += tot
    weighted_purity = num / den if den else float("nan")
    return float(weighted_purity - global_max), global_max, internal_tot


# ============================ degree-stat bundle ==============================
def degree_report(edges_uv, n, label, do_powerlaw=True, do_clustering=True):
    ip, ix, deg = _csr_from_edges(edges_uv, n)
    dpos = deg[deg > 0]
    m = dpos.shape[0]
    rep = dict(
        graph=label, n_nodes=int(n), n_nodes_nonzero=int(m), n_edges=int(edges_uv.shape[0]),
        deg_mean=float(dpos.mean()) if m else float("nan"),
        deg_max=int(dpos.max()) if m else 0,
        deg_median=float(np.median(dpos)) if m else float("nan"),
        max_over_mean=float(dpos.max() / dpos.mean()) if m else float("nan"),
        gini=gini(dpos),
    )
    if do_powerlaw:
        rep["powerlaw"] = powerlaw_fit(dpos)
    if do_clustering:
        c, nc = avg_clustering_sampled(ip, ix, deg, n, CLUST_SAMPLE)
        rep["avg_clustering_sampled"] = c
        rep["clustering_n_sampled"] = nc
    return rep, ip, ix, deg


# ============================ fair-stratum curve ==============================
def fair_stratum_curve(deg, pctls):
    dpos = deg[deg > 0].astype(np.float64)
    total_mass = float(dpos.sum())
    n = dpos.shape[0]
    curve = []
    for p in pctls:
        cut = float(np.percentile(dpos, p))
        below = dpos <= cut
        curve.append(dict(pctl=p, deg_cut=cut,
                          frac_entities_below=float(np.mean(below)),
                          frac_edgemass_below=float(dpos[below].sum() / total_mass) if total_mass else float("nan")))
    return curve


# ============================ real-graph run ==================================
def _gsig(edges_uv):
    """Bit fingerprint of a graph's canonical edge array (arms-differ)."""
    return hashlib.sha256(np.ascontiguousarray(np.sort(edges_uv, axis=0)).tobytes()).hexdigest()


def _iter_cskg(max_lines=0):
    with gzip.open(str(CSKG_PATH), "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            i_rel = header.index("relation")
            i_l1 = header.index("node1;label")
            i_l2 = header.index("node2;label")
            i_src = header.index("source")
        except ValueError:
            i_rel, i_l1, i_l2, i_src = 2, 4, 5, 9
        n = 0
        for line in f:
            n += 1
            if max_lines and n > max_lines:
                break
            p = line.rstrip("\n").split("\t")
            if len(p) <= max(i_rel, i_l1, i_l2):
                continue
            w1 = _norm_word(p[i_l1].split("|")[0])
            w2 = _norm_word(p[i_l2].split("|")[0])
            src = p[i_src] if len(p) > i_src else "?"
            if w1 and w2:
                yield w1, p[i_rel], w2, src


def run_diagnostic(out_dir, triple_iter=None, quiet=False):
    """Assemble the graphs from a triple stream and compute all eight measures. triple_iter yields
    (w1, rel_label, w2, source); defaults to the CSKG gzip stream. Injectable for the synthetic-stream
    self-test (exercises the FULL assembly path locally without CSKG compute)."""
    t0 = time.time()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(stage, **extra):
        try:
            with open(hb_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(ts_iso=datetime.now(timezone.utc).isoformat(), stage=stage,
                                        elapsed_s=round(time.time() - t0, 1), **extra)) + "\n")
        except OSError:
            pass

    def _lg(m):
        if not quiet:
            _log(m)

    if triple_iter is None:
        triple_iter = _iter_cskg(CSKG_MAX_LINES)
    _lg("streaming CSKG (max_lines=%s)..." % (CSKG_MAX_LINES or "ALL"))
    gb = GraphBuild()
    for w1, rel, w2, src in triple_iter:
        gb.add(w1, rel, w2, src)
        gb.n_rows += 1
        if gb.n_rows % 500000 == 0:
            _lg("  parsed %d rows (nodes=%d)" % (gb.n_rows, len(gb.lab2id)))
            _hb("parse", rows=gb.n_rows, nodes=len(gb.lab2id))
    n_nodes, full_edges, xcut_edges = gb.finalize()
    _lg("graphs: FULL n=%d E=%d | XCUT n(nodes total)=%d E=%d | rows=%d relations=%d"
         % (n_nodes, full_edges.shape[0], n_nodes, xcut_edges.shape[0], gb.n_rows, len(gb.rel)))
    _hb("finalized", full_E=int(full_edges.shape[0]), xcut_E=int(xcut_edges.shape[0]))

    # ---- degree reports on FULL + XCUT (context) ----
    full_rep, _fp, _fi, _fd = degree_report(full_edges, n_nodes, "FULL",
                                             do_powerlaw=True, do_clustering=False)
    _lg("FULL: mean_deg=%.2f max=%d max/mean=%.1f gini=%.3f alpha=%s"
         % (full_rep["deg_mean"], full_rep["deg_max"], full_rep["max_over_mean"], full_rep["gini"],
            _fmt(full_rep["powerlaw"]["alpha"])))
    _hb("full_degree")

    xcut_rep, xip, xix, xdeg = degree_report(xcut_edges, n_nodes, "XCUT",
                                             do_powerlaw=True, do_clustering=True)
    _lg("XCUT: mean_deg=%.2f max=%d max/mean=%.1f gini=%.3f clustering=%s alpha=%s"
         % (xcut_rep["deg_mean"], xcut_rep["deg_max"], xcut_rep["max_over_mean"], xcut_rep["gini"],
            _fmt(xcut_rep["avg_clustering_sampled"]), _fmt(xcut_rep["powerlaw"]["alpha"])))
    _hb("xcut_degree")

    # ---- k-core curve of XCUT + derive the 12-core test graph (G_core) ----
    ks = [5, 8, 10, 11, 12, 13, 14, 15, 20, 37, 50]
    core_num, kcurve = kcore_curve(xcut_edges, n_nodes, ks)
    _lg("XCUT k-core curve: " + " ".join("k%d=%d@%.1f" % (k, kcurve[k][0], kcurve[k][1]) for k in ks))
    _hb("kcore")

    core_mask = core_num >= CORE_K
    core_edges, core_old_ids, n_core = induced_subgraph(xcut_edges, core_mask, n_nodes)
    core_rep, cip, cix, cdeg = degree_report(core_edges, n_core, "CORE12",
                                             do_powerlaw=True, do_clustering=True)
    _lg("CORE12: n=%d E=%d mean_deg=%.2f max=%d max/mean=%.2f gini=%.3f clustering=%s"
         % (n_core, core_edges.shape[0], core_rep["deg_mean"], core_rep["deg_max"],
            core_rep["max_over_mean"], core_rep["gini"], _fmt(core_rep["avg_clustering_sampled"])))
    _hb("core_degree", n_core=n_core)

    # ---- per-relation cardinality (FULL relation set) ----
    rel_rows = relation_cardinality(gb.rel)
    n_rel = len(rel_rows)
    hardest = [r["rel"] for r in rel_rows[:max(1, n_rel // 3)]]
    _lg("per-relation cardinality: %d relations; hardest tertile (top-difficulty): %s"
         % (n_rel, ", ".join("%s(%s,sym%.2f)" % (r["rel"], r["cls"], r["sym"]) for r in rel_rows[:8])))
    _hb("cardinality", n_rel=n_rel)

    # ---- community + modularity on G_core (+ schema cross-tab) ----
    labels, Q, n_comm = louvain(cip, cix, cdeg, n_core)
    # relation-class per core edge (need to recover a relation-class for each core edge). We re-derive by a
    # second thin pass keyed on the core node label set (only cross-cutting edges among core nodes).
    core_label_set = set(gb_finalize_labels(gb, core_old_ids))
    edge_relclass = core_edge_relclasses(core_edges, core_old_ids, gb, core_label_set)
    align, global_max, internal_tot = schema_alignment(core_edges, edge_relclass, labels, n_comm)
    comm_sizes = np.bincount(labels).tolist()
    comm_sizes.sort(reverse=True)
    _lg("CORE12 community: Q=%.4f n_comm=%d top5_sizes=%s schema_align=%s (global_max=%.3f internal=%d)"
         % (Q, n_comm, comm_sizes[:5], _fmt(align), global_max, internal_tot))
    _hb("louvain", Q=round(float(Q), 4), n_comm=n_comm)

    # ---- P4 structural kernel cross-reference ----
    kernel_mask_core = core_num[core_old_ids] >= KERNEL_K
    kernel_n = int(kernel_mask_core.sum())
    kernel_node_frac = kernel_n / n_core if n_core else float("nan")
    kernel_mass = float(cdeg[kernel_mask_core].sum())
    total_mass = float(cdeg.sum())
    kernel_mass_frac = kernel_mass / total_mass if total_mass else float("nan")
    mass_concentration = (kernel_mass_frac / kernel_node_frac) if kernel_node_frac else float("nan")
    # high-degree tertile of G_core, overlap with kernel
    hi_cut = float(np.percentile(cdeg[cdeg > 0], 67))
    hi_mask = cdeg >= hi_cut
    hi_n = int(hi_mask.sum())
    overlap = int((hi_mask & kernel_mask_core).sum())
    _lg("P4 kernel(k>=%d): n=%d frac=%.4f mass_frac=%.4f concentration=%.2f | hi-tertile n=%d kernel-in-hi=%d"
         % (KERNEL_K, kernel_n, kernel_node_frac, kernel_mass_frac, mass_concentration, hi_n, overlap))
    _hb("kernel")

    # ---- fair-stratum curve on G_core ----
    fair = fair_stratum_curve(cdeg, FAIR_PCTL_GRID)
    _lg("fair-stratum (G_core): " + " ".join(
        "p%d:ent=%.2f/mass=%.2f" % (r["pctl"], r["frac_entities_below"], r["frac_edgemass_below"])
        for r in fair))
    _hb("fairstratum")

    return dict(
        elapsed_build_s=time.time() - t0,
        n_rows=gb.n_rows, n_nodes=n_nodes,
        full=full_rep, xcut=xcut_rep, core=core_rep,
        kcore_curve={int(k): dict(n_nodes=int(kcurve[k][0]), avg_deg=round(kcurve[k][1], 2)) for k in ks},
        n_core=n_core, core_k=CORE_K,
        relations=rel_rows, n_relations=n_rel, hardest_tertile=hardest,
        community=dict(modularity_Q=float(Q), n_communities=n_comm, top_sizes=comm_sizes[:20],
                       schema_alignment=align, global_max_relclass_frac=global_max,
                       internal_edges=internal_tot),
        p4_kernel=dict(kernel_k=KERNEL_K, kernel_n=kernel_n, kernel_node_frac=kernel_node_frac,
                       kernel_mass_frac=kernel_mass_frac, mass_concentration=mass_concentration,
                       hi_tertile_n=hi_n, kernel_in_hi_tertile=overlap, hi_deg_cut=hi_cut),
        fair_stratum=fair,
        graph_sigs=dict(full=_gsig(full_edges)[:16], xcut=_gsig(xcut_edges)[:16], core=_gsig(core_edges)[:16]),
    )


def gb_finalize_labels(gb, old_ids):
    """id->label reverse lookup for a subset of ids (core nodes)."""
    id2lab = {i: w for w, i in gb.lab2id.items()}
    return [id2lab[int(o)] for o in old_ids]


def core_edge_relclasses(core_edges, core_old_ids, gb, core_label_set):
    """Assign a coarse relation-CLASS to each CORE edge by looking up the dominant cross-cutting relation
    between the two node labels (second thin pass over the census dir_pairs). Falls back to 'mixed' when
    unknown. Returns list[str] len == core_edges.shape[0]."""
    id2lab = {i: w for w, i in gb.lab2id.items()}
    core_ids = core_old_ids.tolist()
    # map old_id -> core_index
    old2core = {int(o): k for k, o in enumerate(core_ids)}
    # Build a lookup (h_id,t_id)->schema_class from the per-relation dir_pairs (cross-cutting only).
    pair_class = {}
    for tok, rc in gb.rel.items():
        sc = SCHEMA_CLASS.get(tok)
        if sc is None:
            continue
        for (h, t) in rc["dir_pairs"]:
            a, b = (h, t) if h < t else (t, h)
            if a in old2core and b in old2core:
                pair_class[(a, b)] = sc          # last-writer; fine for a coarse cross-tab
    out = []
    # core_edges are remapped to 0..n_core-1; recover old ids via core_old_ids
    for e in range(core_edges.shape[0]):
        oa = int(core_old_ids[int(core_edges[e, 0])])
        ob = int(core_old_ids[int(core_edges[e, 1])])
        a, b = (oa, ob) if oa < ob else (ob, oa)
        out.append(pair_class.get((a, b), "mixed"))
    return out


# ============================ verdict =========================================
def compute_verdict(res):
    core = res["core"]
    ratio = core["max_over_mean"]
    g = core["gini"]
    # ---- P1 ----
    p1_pass = bool(P1_RATIO_LO <= ratio <= P1_RATIO_HI and P1_GINI_LO <= g <= P1_GINI_HI)
    p1_fail = bool(ratio > P1_RATIO_FAIL or g > P1_GINI_FAIL)
    p1 = "HARD_PASS" if p1_pass else ("HARD_FAIL" if p1_fail else "MIDDLE_BAND")

    # ---- P2 ----
    rows = res["relations"]
    n_rel = len(rows)
    worst_k = max(1, int(round(n_rel * P2_WORST_FRAC)))
    best_k = max(1, int(round(n_rel * P2_WORST_FRAC)))
    ranked = [r["rel"] for r in rows]                     # already sorted hardest-first
    worst_set = set(ranked[:worst_k])
    best_set = set(ranked[-best_k:])
    tgt_found = {t: (t in [r["rel"] for r in rows]) for t in P2_TARGET_RELS}
    tgt_worst = {t: (t in worst_set) for t in P2_TARGET_RELS if tgt_found[t]}
    tgt_best = {t: (t in best_set) for t in P2_TARGET_RELS if tgt_found[t]}
    any_present = any(tgt_found.values())
    all_present_worst = any_present and all(tgt_worst.get(t, False) for t in P2_TARGET_RELS if tgt_found[t])
    any_in_best = any(tgt_best.get(t, False) for t in P2_TARGET_RELS if tgt_found[t])
    if not any_present:
        p2 = "MIDDLE_BAND"                                # targets absent (e.g. smoke slice); inconclusive
    elif all_present_worst:
        p2 = "HARD_PASS"
    elif any_in_best:
        p2 = "HARD_FAIL"
    else:
        p2 = "MIDDLE_BAND"

    # ---- P3 (headline) ----
    Q = res["community"]["modularity_Q"]
    align = res["community"]["schema_alignment"]
    align_ok = bool(np.isfinite(align) and align > P3_ALIGN_PASS)
    align_fail = bool((not np.isfinite(align)) or align <= P3_ALIGN_FAIL)
    p3_pass = bool(Q > P3_Q_PASS and align_ok)
    p3_fail = bool(Q < P3_Q_FAIL or align_fail)
    if p3_pass:
        p3 = "HARD_PASS"
    elif p3_fail:
        p3 = "HARD_FAIL"
    else:
        p3 = "MIDDLE_BAND"

    # ---- P4 (structural) ----
    k = res["p4_kernel"]
    conc = k["mass_concentration"]
    small_kernel = bool(np.isfinite(k["kernel_node_frac"]) and k["kernel_node_frac"] < P4_KERNEL_NODE_FRAC)
    p4_pass = bool(small_kernel and np.isfinite(conc) and conc > P4_MASS_CONCENTRATION)
    p4_fail = bool(np.isfinite(conc) and conc <= P4_MASS_CONCENTRATION_FAIL)
    if p4_pass:
        p4 = "STRUCT_PASS"
    elif p4_fail:
        p4 = "STRUCT_FAIL"
    else:
        p4 = "STRUCT_MIDDLE"

    # headline = the map-builder decision, driven by P3
    headline = {
        "HARD_PASS": "SUPPORTS_FACTORIZED_MAP_BUILDER",
        "HARD_FAIL": "TOO_HUB_DOMINATED_OR_SCHEMA_POOR",
        "MIDDLE_BAND": "PARTIAL_MAP_BUILDER_SUPPORT",
    }[p3]

    msg = (
        "%s || P1(skew)=%s [max/mean=%.2f in[%.0f,%.0f]? gini=%.3f in[%.2f,%.2f]?] || "
        "P2(cardinality)=%s [targets=%s worst_tertile=%s] || "
        "P3(map-builder)=%s [Q=%.4f>%.2f? align=%s>%.2f?] || "
        "P4(kernel,struct)=%s [k>=%d frac=%.4f<%.2f? conc=%.2f>%.1f?] || "
        "n_core=%d n_rel=%d run=%s"
        % (headline, p1, ratio, P1_RATIO_LO, P1_RATIO_HI, g, P1_GINI_LO, P1_GINI_HI,
           p2, dict(tgt_found), dict(tgt_worst),
           p3, Q, P3_Q_PASS, _fmt(align), P3_ALIGN_PASS,
           p4, k["kernel_k"], k["kernel_node_frac"], P4_KERNEL_NODE_FRAC, conc, P4_MASS_CONCENTRATION,
           res["n_core"], n_rel, RUN_MODE))

    gates = dict(
        headline=headline, p1_verdict=p1, p2_verdict=p2, p3_verdict=p3, p4_verdict=p4,
        p1=dict(max_over_mean=ratio, gini=g, ratio_band=[P1_RATIO_LO, P1_RATIO_HI],
                gini_band=[P1_GINI_LO, P1_GINI_HI], ratio_fail=P1_RATIO_FAIL, gini_fail=P1_GINI_FAIL,
                pass_=p1_pass, fail=p1_fail),
        p2=dict(n_relations=n_rel, worst_tertile_k=worst_k, targets_present=dict(tgt_found),
                targets_in_worst=dict(tgt_worst), targets_in_best=dict(tgt_best),
                hardest=ranked[:worst_k]),
        p3=dict(modularity_Q=Q, Q_pass=P3_Q_PASS, Q_fail=P3_Q_FAIL, schema_alignment=align,
                align_pass=P3_ALIGN_PASS, align_fail=P3_ALIGN_FAIL, pass_=p3_pass, fail=p3_fail),
        p4=dict(mass_concentration=conc, small_kernel=small_kernel, kernel_node_frac=k["kernel_node_frac"],
                node_frac_band=P4_KERNEL_NODE_FRAC, conc_pass=P4_MASS_CONCENTRATION,
                conc_fail=P4_MASS_CONCENTRATION_FAIL,
                performance_margin_note="HYPOTHESIZED@this_prereg: POP-vs-ROTATE margin-in-kernel needs "
                                        "course_c model scores; out of scope for this pure-graph cell"),
        bands=dict(P1_RATIO_LO=P1_RATIO_LO, P1_RATIO_HI=P1_RATIO_HI, P1_RATIO_FAIL=P1_RATIO_FAIL,
                   P1_GINI_LO=P1_GINI_LO, P1_GINI_HI=P1_GINI_HI, P1_GINI_FAIL=P1_GINI_FAIL,
                   P3_Q_PASS=P3_Q_PASS, P3_Q_FAIL=P3_Q_FAIL, P3_ALIGN_PASS=P3_ALIGN_PASS,
                   P3_ALIGN_FAIL=P3_ALIGN_FAIL, KERNEL_K=KERNEL_K,
                   P4_KERNEL_NODE_FRAC=P4_KERNEL_NODE_FRAC, P4_MASS_CONCENTRATION=P4_MASS_CONCENTRATION,
                   CORE_K=CORE_K, CARD_MANY_THRESH=CARD_MANY_THRESH),
    )
    return headline, msg, gates


# ============================ self-test =======================================
def _planted_schema_clean(seed=3):
    """POSITIVE control: K well-separated communities, each internally dense, each dominated by ONE
    relation-class -> high modularity Q AND high schema alignment (a factorized operator SHOULD work).
    Returns (edges_uv, n, rel_of_edge:list[str])."""
    rng = np.random.default_rng(seed)
    K = 6
    per = 60
    n = K * per
    edges = set()
    rel_map = {}
    classes = ["atomic_event", "spatial", "functional", "causal", "property", "spatial"]
    for c in range(K):
        base = c * per
        # dense intra-community (each node ~ deg 8 inside)
        for i in range(per):
            for _ in range(8):
                j = base + int(rng.integers(0, per))
                a, b = base + i, j
                if a != b:
                    e = (a, b) if a < b else (b, a)
                    edges.add(e)
                    rel_map[e] = classes[c]        # community -> one relation-class
        # a few sparse inter-community bridges (keep modularity high)
        for _ in range(3):
            a = base + int(rng.integers(0, per))
            b = ((c + 1) % K) * per + int(rng.integers(0, per))
            e = (a, b) if a < b else (b, a)
            edges.add(e)
            rel_map.setdefault(e, "mixed")
    euv = np.array(sorted(edges), dtype=np.int64)
    relc = [rel_map[(int(euv[i, 0]), int(euv[i, 1]))] for i in range(euv.shape[0])]
    return euv, n, relc


def _planted_hub_blurred(seed=5):
    """NEGATIVE control: one giant hub connected to nearly all nodes, relation-classes assigned UNIFORMLY at
    random (no schema structure) -> low modularity Q, extreme degree skew (Gini>0.7, max/mean>100), near-
    uniform relation mixing (a factorized operator should NOT help)."""
    rng = np.random.default_rng(seed)
    n = 400
    edges = set()
    hub = 0
    for i in range(1, n):
        edges.add((hub, i))                       # star: everyone attached to hub
        if i + 1 < n and rng.random() < 0.01:     # a tiny sprinkle of peripheral edges
            edges.add((i, i + 1))
    euv = np.array(sorted(edges), dtype=np.int64)
    classes = ["atomic_event", "spatial", "functional", "causal", "property"]
    relc = [classes[int(rng.integers(0, len(classes)))] for _ in range(euv.shape[0])]
    return euv, n, relc


def _planted_relations():
    """Planted directed relation census for the cardinality classifier: a 1-1, a 1-N, an N-1, an N-N, and a
    symmetric relation. Returns a rel-census dict shaped like GraphBuild.rel."""
    census = {}

    def _mk(pairs):
        heads = set(h for h, _ in pairs)
        tails = set(t for _, t in pairs)
        return dict(heads=heads, tails=tails, n=len(pairs), n_sampled=len(pairs),
                    dir_pairs=set(pairs), src=defaultdict(int))
    census["rel_1_1"] = _mk([(i, 1000 + i) for i in range(50)])                     # 1-1
    census["rel_1_n"] = _mk([(i // 5, 2000 + i) for i in range(50)])                # 1-N (5 tails/head)
    census["rel_n_1"] = _mk([(3000 + i, i // 5) for i in range(50)])                # N-1
    census["rel_n_n"] = _mk([(i % 7, (i * 3) % 11) for i in range(60)])             # N-N
    sym = [(i, i + 1) for i in range(0, 40, 2)] + [(i + 1, i) for i in range(0, 40, 2)]
    census["rel_sym"] = _mk(sym)                                                     # symmetric
    return census


def _selftest():
    print("[selftest] graph-structure diagnostic apparatus + planted positive/negative controls...",
          flush=True)

    # (1) k-core correctness on a planted graph: a 5-clique has coreness 4; attached leaves have coreness 1.
    clique = [(a, b) for a in range(5) for b in range(a + 1, 5)]
    leaves = [(0, 5), (1, 6)]
    euv = np.array(sorted(set((min(a, b), max(a, b)) for a, b in clique + leaves)), dtype=np.int64)
    ncc = 7
    ip, ix, deg = _csr_from_edges(euv, ncc)
    core = kcore_number(ip, ix, deg, ncc)
    assert core[:5].min() == 4, "SELFTEST(1) FAIL: 5-clique coreness != 4: %s" % core[:5].tolist()
    assert core[5] == 1 and core[6] == 1, "SELFTEST(1) FAIL: leaf coreness != 1: %s" % core[5:].tolist()

    # (2) degree-skew discriminators FIRE on the correct side: uniform ring -> low Gini/ratio; star hub ->
    #     Gini>0.7 AND max/mean>100 (Prediction-1 HARD-FAIL side).
    ring = np.array([(i, (i + 1) % 200) for i in range(200)], dtype=np.int64)
    ring = np.array(sorted(set((min(a, b), max(a, b)) for a, b in ring)), dtype=np.int64)
    rr, _rp, _ri, _rd = degree_report(ring, 200, "ring", do_powerlaw=False, do_clustering=False)
    assert rr["gini"] < 0.15 and rr["max_over_mean"] < 2.0, \
        "SELFTEST(2) FAIL: uniform ring not low-skew (gini=%.3f ratio=%.2f)" % (rr["gini"], rr["max_over_mean"])
    hub_euv, hub_n, _hrelc = _planted_hub_blurred()
    hr, _hp, _hi, _hd = degree_report(hub_euv, hub_n, "hub", do_powerlaw=False, do_clustering=False)
    # a pure star's degree-Gini is ~0.5 (many equal degree-1 leaves); its max/mean ratio is what makes it
    # hub-dominated -> P1 HARD-FAIL fires via the ratio>100 branch of the pre-registered OR condition.
    assert hr["max_over_mean"] > 100.0 and hr["gini"] > 0.40, \
        "SELFTEST(2) FAIL: hub graph not hub-dominated (gini=%.3f ratio=%.2f) -- P1 HARD-FAIL side inert" \
        % (hr["gini"], hr["max_over_mean"])
    # exercise the Gini>0.70 HARD-FAIL branch on a genuine heavy-tailed (multi-degree) sequence.
    _heavy = np.array([1] * 2000 + [50] * 100 + [2000] * 10, dtype=np.int64)
    assert gini(_heavy) > 0.70, \
        "SELFTEST(2b) FAIL: heavy-tail Gini not > 0.70 (%.3f) -- Gini HARD-FAIL branch inert" % gini(_heavy)

    # (3) POSITIVE control: schema-clean modular graph -> Q>0.30 AND schema_alignment>0.15 -> P3 HARD_PASS.
    ce, cn, crelc = _planted_schema_clean()
    cip, cix, cdeg = _csr_from_edges(ce, cn)
    labels, Q, n_comm = louvain(cip, cix, cdeg, cn)
    assert Q > 0.30, "SELFTEST(3) FAIL: schema-clean modular Q not > 0.30 (Q=%.4f) -- Louvain inert" % Q
    align, gmax, itot = schema_alignment(ce, crelc, labels, n_comm)
    assert np.isfinite(align) and align > 0.15, \
        "SELFTEST(3) FAIL: schema-clean alignment not > 0.15 (align=%.4f) -- schema cross-tab inert" % align
    res_pos = dict(core=dict(max_over_mean=25.0, gini=0.45),          # neutral P1 for the positive control
                   relations=[], n_core=cn,
                   community=dict(modularity_Q=Q, schema_alignment=align, n_communities=n_comm),
                   p4_kernel=dict(kernel_k=KERNEL_K, kernel_node_frac=0.1, kernel_mass_frac=0.3,
                                  mass_concentration=3.0, hi_tertile_n=1, kernel_in_hi_tertile=1))
    hpos, _mp, gpos = compute_verdict(res_pos)
    assert gpos["p3_verdict"] == "HARD_PASS", \
        "SELFTEST(3) FAIL: positive control P3 not HARD_PASS (got %s)" % gpos["p3_verdict"]
    assert hpos == "SUPPORTS_FACTORIZED_MAP_BUILDER", \
        "SELFTEST(3) FAIL: positive control headline wrong (%s)" % hpos

    # (4) NEGATIVE control: hub-blurred graph -> low Q + uniform mixing -> P3 HARD_FAIL AND P1 HARD_FAIL.
    hlabels, hQ, hnc = louvain(_csr_from_edges(hub_euv, hub_n)[0], _csr_from_edges(hub_euv, hub_n)[1],
                               _csr_from_edges(hub_euv, hub_n)[2], hub_n)
    halign, _hg, _hit = schema_alignment(hub_euv, _hrelc, hlabels, hnc)
    res_neg = dict(core=dict(max_over_mean=hr["max_over_mean"], gini=hr["gini"]),
                   relations=[], n_core=hub_n,
                   community=dict(modularity_Q=hQ, schema_alignment=halign, n_communities=hnc),
                   p4_kernel=dict(kernel_k=KERNEL_K, kernel_node_frac=0.005, kernel_mass_frac=0.5,
                                  mass_concentration=100.0, hi_tertile_n=1, kernel_in_hi_tertile=1))
    hneg, _mn, gneg = compute_verdict(res_neg)
    assert gneg["p1_verdict"] == "HARD_FAIL", \
        "SELFTEST(4) FAIL: negative control P1 not HARD_FAIL (got %s)" % gneg["p1_verdict"]
    assert gneg["p3_verdict"] == "HARD_FAIL", \
        "SELFTEST(4) FAIL: negative control P3 not HARD_FAIL (Q=%.4f align=%s got %s)" \
        % (hQ, _fmt(halign), gneg["p3_verdict"])
    assert hneg == "TOO_HUB_DOMINATED_OR_SCHEMA_POOR", \
        "SELFTEST(4) FAIL: negative control headline wrong (%s)" % hneg

    # (5) cardinality classifier + symmetry on planted relations.
    rc = relation_cardinality(_planted_relations())
    cls = {r["rel"]: r["cls"] for r in rc}
    symd = {r["rel"]: r["sym"] for r in rc}
    assert cls.get("rel_1_1") == "1-1", "SELFTEST(5) FAIL: 1-1 misclassified: %s" % cls
    assert cls.get("rel_1_n") == "1-N", "SELFTEST(5) FAIL: 1-N misclassified: %s" % cls
    assert cls.get("rel_n_1") == "N-1", "SELFTEST(5) FAIL: N-1 misclassified: %s" % cls
    assert symd.get("rel_sym", 0) > 0.9, "SELFTEST(5) FAIL: symmetric relation not detected: %s" % symd
    assert symd.get("rel_1_1", 1) < 0.1, "SELFTEST(5) FAIL: 1-1 falsely flagged symmetric: %s" % symd
    # difficulty ranking: symmetric + N-N should outrank the clean 1-1 relation.
    diff = {r["rel"]: r["difficulty"] for r in rc}
    assert diff["rel_sym"] > diff["rel_1_1"] and diff["rel_n_n"] > diff["rel_1_1"], \
        "SELFTEST(5) FAIL: difficulty ranking wrong: %s" % diff

    # (6) fair-stratum monotonicity: frac_entities_below and frac_edgemass_below both non-decreasing in pctl.
    fair = fair_stratum_curve(hr and _hd, FAIR_PCTL_GRID)
    ent = [r["frac_entities_below"] for r in fair]
    mass = [r["frac_edgemass_below"] for r in fair]
    assert all(ent[i] <= ent[i + 1] + 1e-9 for i in range(len(ent) - 1)), "SELFTEST(6) FAIL: ent non-mono"
    assert all(mass[i] <= mass[i + 1] + 1e-9 for i in range(len(mass) - 1)), "SELFTEST(6) FAIL: mass non-mono"
    # fair-zone shrinks as share of mass: at the median cutoff, entity-share should exceed mass-share on a
    # skewed graph (the HEADLINE-4 shape).
    mid = next(r for r in fair if r["pctl"] == 50)
    assert mid["frac_entities_below"] > mid["frac_edgemass_below"], \
        "SELFTEST(6) FAIL: fair zone not mass-shrinking on skewed graph"

    # (7) arms differ: the three planted graphs are not bit-identical.
    sigs = {_gsig(ce), _gsig(hub_euv), _gsig(euv)}
    assert len(sigs) == 3, "SELFTEST(7) FAIL: planted graph sigs not distinct"

    # (8) power-law MLE returns a finite alpha in a sane range on a synthetic power-law degree sequence.
    rng = np.random.default_rng(1)
    synth = (rng.pareto(2.0, size=5000) + 1) * 3      # heavy tail
    pl = powerlaw_fit(np.round(synth).astype(int))
    assert np.isfinite(pl["alpha"]) and 1.5 < pl["alpha"] < 5.0, \
        "SELFTEST(8) FAIL: power-law alpha out of range: %s" % pl

    # (9) FULL-ASSEMBLY end-to-end on a SYNTHETIC triple stream (exercises GraphBuild.add/finalize, the
    #     edge-code dedup, k-core extraction, core_edge_relclasses, louvain, and compute_verdict together --
    #     the streaming path that the CSKG gzip would otherwise first hit only on the remote runner).
    def _synth_stream():
        rgn = np.random.default_rng(9)
        toks = ["xeffect", "atlocation", "usedfor", "causes", "mayhaveproperty"]  # cross-cutting spine
        # build several dense concept clusters so a >=CORE_K core survives; plus lexical dilution edges.
        for c in range(5):
            for i in range(80):
                for _ in range(30):
                    j = int(rgn.integers(0, 80))
                    yield ("c%d_n%d" % (c, i), toks[c], "c%d_n%d" % (c, j), "conceptnet")
            # lexical dilution (stripped from the spine): synonym/isa many-to relations
            for i in range(40):
                yield ("c%d_n%d" % (c, i), "/r/Synonym", "syn_%d" % (i % 3), "roget")
                yield ("c%d_n%d" % (c, i), "/r/IsA", "cat_%d" % (i % 2), "wordnet")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        res9 = run_diagnostic(Path(td), triple_iter=_synth_stream(), quiet=True)
        assert res9["n_core"] > 0, "SELFTEST(9) FAIL: synthetic assembly produced empty k-core"
        assert len(res9["fair_stratum"]) == len(FAIR_PCTL_GRID), "SELFTEST(9) FAIL: fair-stratum short"
        assert len(set(res9["graph_sigs"].values())) >= 2, "SELFTEST(9) FAIL: graph sigs not distinct"
        # synthetic lexical relations must appear in the FULL relation census (Prediction-2 targets exist).
        rel_names = {r["rel"] for r in res9["relations"]}
        assert "synonym" in rel_names and "isa" in rel_names, \
            "SELFTEST(9) FAIL: lexical relations missing from census: %s" % sorted(rel_names)
        h9, m9, g9 = compute_verdict(res9)
        assert g9["headline"] in ("SUPPORTS_FACTORIZED_MAP_BUILDER", "TOO_HUB_DOMINATED_OR_SCHEMA_POOR",
                                  "PARTIAL_MAP_BUILDER_SUPPORT"), \
            "SELFTEST(9) FAIL: assembly verdict malformed: %s" % h9

    print("[selftest] PASS: (1) k-core (2) skew discriminators fire both sides (3) POS control P3 HARD_PASS "
          "Q=%.3f align=%.3f (4) NEG control P1+P3 HARD_FAIL Q=%.3f (5) cardinality+symmetry (6) fair-stratum "
          "mass-shrink (7) arms differ (8) power-law MLE (9) full-assembly end-to-end on synthetic stream "
          "(n_core=%d headline=%s)" % (Q, align, hQ, res9["n_core"], h9), flush=True)


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
    _write_start_marker(out_dir, RUN_MODE, len(FAIR_PCTL_GRID))
    t0 = time.time()
    _log("config: mode=%s CSKG_MAX_LINES=%s CAP_PER_REL=%d CORE_K=%d KERNEL_K=%d"
         % (RUN_MODE, CSKG_MAX_LINES or "ALL", CAP_PER_REL, CORE_K, KERNEL_K))

    if not _ensure_file(CSKG_PATH, CSKG_URL, 50_000_000):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_DATA_MISSING", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="cskg.tsv.gz absent + self-acquire failed on runner: %s" % CSKG_PATH,
            summary="CSKG data missing", elapsed_s=time.time() - t0))
        raise SystemExit(1)

    res = run_diagnostic(out_dir)

    # cardinality gate (META_RULE_H): every fair-stratum sweep point must have completed.
    if len(res["fair_stratum"]) != len(FAIR_PCTL_GRID):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="expected %d fair-stratum points got %d"
                        % (len(FAIR_PCTL_GRID), len(res["fair_stratum"])),
            summary="cardinality breach", elapsed_s=time.time() - t0, diagnostic=res))
        raise SystemExit(1)

    # arms-must-differ (META_RULE_AF): the three graphs must be structurally distinct.
    sigs = res["graph_sigs"]
    if len(set(sigs.values())) < 3:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF", run_mode=RUN_MODE, anchor_name=ANCHOR_NAME,
            verdict_msg="graph sigs not distinct: %s" % sigs, summary="arms identical",
            elapsed_s=time.time() - t0, diagnostic=res))
        raise SystemExit(1)

    headline, msg, gates = compute_verdict(res)
    elapsed = time.time() - t0
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=headline, verdict_msg=msg, summary=msg[:200],
        run_mode=RUN_MODE, n_seeds=1, elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        arms_differ_verified=True, graph_sigs=sigs, gates=gates, diagnostic=res,
        config=dict(CSKG_MAX_LINES=CSKG_MAX_LINES, CAP_PER_REL=CAP_PER_REL, CORE_K=CORE_K, KERNEL_K=KERNEL_K,
                    FAIR_PCTL_GRID=FAIR_PCTL_GRID, CLUST_SAMPLE=CLUST_SAMPLE),
    )
    write_metrics(out_dir, metrics, results=[{"elapsed_s": elapsed}])
    _log("VERDICT: %s" % msg)
    _log("done (%.1fs)" % elapsed)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    _selftest()                 # planted positive/negative controls; asserts fire before any CSKG work
    if _ARGS.self_test:
        _od = get_output_dir(ANCHOR_NAME)
        write_metrics(_od, dict(
            verdict="SELFTEST_PASS", run_mode="self_test", anchor_name=ANCHOR_NAME,
            verdict_msg="SELFTEST_PASS: k-core correct; skew discriminators fire both sides; POS control "
                        "P3 HARD_PASS; NEG control P1+P3 HARD_FAIL; cardinality+symmetry classifier; "
                        "fair-stratum mass-shrink; arms differ; power-law MLE sane",
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
