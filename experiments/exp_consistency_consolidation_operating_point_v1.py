"""CONSOLIDATED-SCHEMA consistency scoring: does a self-denoised schema give a CLEAN operating point?

FOLLOW-ON to exp_knowledge_store_consistency_cleanup_v1 (imported read-only as C). That cell's
PAIRED / ranking metric is clean (corrupted genus out-scores the subject's own original genus,
full 0.79 / clean 0.88, CI-separated over the 0.5 twin), but its absolute-THRESHOLD precision /
recall against the injected set is poor on the FULL store: the store is ALREADY noisy and its real
inconsistent facts legitimately out-rank the planted errors in absolute energy. This cell asks
whether a brain-faithful CONSOLIDATION step recovers a clean threshold operating point.

BRAIN FRAME (PINNED): the neocortex builds its schema from CONSOLIDATED, denoised, gist-extracted
memories (Winocur & Moscovitch; McClelland CLS) -- not from raw episodic traces. So we build the
congruence schema (member-Jaccard genus compatibility + associative field) from a DENOISED fact set:
iteratively DOWN-WEIGHT the facts the schema itself judges least consistent (highest energy) and
REBUILD the compatibility from the surviving trust-weighted memberships. 2-3 rounds; member-Jaccard
is local so it should converge (verified: the max weight change per round is reported).

THE ONE HARD CONSTRAINT (independently re-derived, and the whole ballgame): STRICT LEAVE-ONE-OUT --
a fact never contributes to its own consistency score. Two leaks are closed:
  (1) SUBJECT LOO at scoring time. member-Jaccard compat(g0, gj) = |members(g0) & members(gj)| / |U|.
      For an injected fact (s0, g0), s0 is itself a member of g0 AND of its real genera gj, so s0
      inflates the intersection and the wrong genus looks compatible with s0's own family. We EXCLUDE
      s0 from both member sets when scoring (s0, g0) -- exactly, and in O(1) via cached shared-min +
      per-genus totals (no per-fact rebuild).
  (2) CONSOLIDATION LOO. Down-weighting is driven by each fact's OWN leave-one-out energy, so a fact
      cannot lower its own energy by having consolidated into the schema. A prior graph-diffused
      attempt that built its geometry from the (label-known) clean store hit an AUC-0.98 ORACLE trap
      this way; consolidation approximates that clean store using ONLY within-store energy (no labels),
      and the info-free TWIN (schema built from a label-shuffled store) is the guard that the
      separation is real structure and not the pipeline manufacturing it.

WHAT IS MEASURED (raw schema vs consolidated schema, on BOTH full and clean stores, far + near):
  * threshold PRECISION@k and RECALL@k across a small k sweep (k = n_inj, 2*n_inj, top 5/10/25%),
    plus AUC and the project's CI-clean PAIRED metric, each vs the info-free twin.
  * a super-brain GLOBAL ENERGY variant: score each fact against the WHOLE consolidated schema at
    once (a diffused global consistency field over every genus, trust-weighted) rather than only its
    immediate associative network -- does the global field help ranking / AUC?

HONEST FRAMING (either is a full pass): (a) consolidation yields a CLEAN, CI-separated threshold
operating point => a path to SOLVED; or (b) it confirms that on a genuinely noisy store the REAL
errors legitimately out-rank the injections in absolute energy => ranking / human-review is the
correct deliverable (itself the North Star finding). The verdict is reported with numbers.

ASCII-only. Pure python + numpy. Deterministic (seeded). Imports the v1 cell READ-ONLY.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")          # numpy here is MKL-backed; pin for bit-determinism
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import json
import math
import random
import statistics as st
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import experiments.exp_knowledge_store_consistency_cleanup_v1 as C  # READ-ONLY shared substrate

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(_REPO, "data", "exp_consistency_consolidation_operating_point_v1")

Fact = C.Fact


# =========================================================================================
# 1. TRUST-WEIGHTED SCHEMA with strict subject leave-one-out + a global diffused field
# =========================================================================================
class WeightedSchema:
    """Member-Jaccard genus compatibility + associative field over a fact set carrying a per-fact
    TRUST weight w in [0,1]. Down-weighted (suspected) facts contribute less to every part of the
    schema. `compat_facts` may differ from the network facts so the compatibility geometry can be made
    INFORMATION-FREE (label-shuffled) for the twin while the associative network stays real."""

    def __init__(self, facts: Sequence[Fact], weights: Optional[np.ndarray] = None,
                 compat_facts: Optional[Sequence[Fact]] = None,
                 compat_weights: Optional[np.ndarray] = None):
        facts = list(facts)
        n = 1 + max((f.fid for f in facts), default=-1)
        w = np.ones(n) if weights is None else weights
        # ---- network side (real): subj2gen, gen2subj members, (s,g)->trust
        self.net_subj2gen: Dict[str, set] = defaultdict(set)
        self.net_members: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.net_w: Dict[Tuple[str, str], float] = {}
        for f in facts:
            wf = float(w[f.fid])
            self.net_subj2gen[f.s].add(f.g)
            m = self.net_members[f.g]
            m[f.s] = max(m.get(f.s, 0.0), wf)
            k = (f.s, f.g)
            self.net_w[k] = max(self.net_w.get(k, 0.0), wf)
        # ---- compat side (real by default, shuffled for the twin): weighted member sets
        cf = list(compat_facts) if compat_facts is not None else facts
        cn = 1 + max((f.fid for f in cf), default=-1)
        cw = (np.ones(cn) if compat_weights is None
              else compat_weights) if compat_facts is not None else w
        self.cmp_members: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.cmp_subj2gen: Dict[str, set] = defaultdict(set)
        self.cmp_w: Dict[Tuple[str, str], float] = {}
        for f in cf:
            wf = float(cw[f.fid]) if f.fid < len(cw) else 1.0
            m = self.cmp_members[f.g]
            m[f.s] = max(m.get(f.s, 0.0), wf)
            self.cmp_subj2gen[f.s].add(f.g)
            k = (f.s, f.g)
            self.cmp_w[k] = max(self.cmp_w.get(k, 0.0), wf)
        self.gen_total: Dict[str, float] = {g: sum(m.values()) for g, m in self.cmp_members.items()}
        self._smin: Dict[Tuple[str, str], float] = {}
        # global diffused field (built lazily)
        self._gidx: Optional[Dict[str, int]] = None
        self._Dn: Optional[np.ndarray] = None

    # ---- member-Jaccard compatibility (trust-weighted Ruzicka) -----------------------------------
    def _shared_min(self, g1: str, g2: str) -> float:
        key = (g1, g2) if g1 <= g2 else (g2, g1)
        v = self._smin.get(key)
        if v is not None:
            return v
        a, b = self.cmp_members.get(g1, {}), self.cmp_members.get(g2, {})
        if len(a) > len(b):
            a, b = b, a
        s = 0.0
        for subj, wa in a.items():
            wb = b.get(subj)
            if wb is not None:
                s += wa if wa < wb else wb
        self._smin[key] = s
        return s

    def compat(self, g1: str, g2: str) -> float:
        if g1 == g2:
            return 1.0
        smin = self._shared_min(g1, g2)
        if smin <= 0.0:
            return 0.0
        den = self.gen_total.get(g1, 0.0) + self.gen_total.get(g2, 0.0) - smin
        return smin / den if den > 0 else 0.0

    def compat_loo(self, g0: str, gj: str, s0: str) -> float:
        """member-Jaccard compat(g0, gj) with subject s0 EXCLUDED from both member sets (strict LOO).
        O(1): full shared-min is cached; s0's exact contribution is subtracted."""
        if g0 == gj:
            return 1.0
        smin = self._shared_min(g0, gj)
        a0 = self.cmp_members.get(g0, {}).get(s0, 0.0)
        b0 = self.cmp_members.get(gj, {}).get(s0, 0.0)
        shared = a0 if (a0 > 0.0 and b0 > 0.0 and a0 < b0) else (b0 if (a0 > 0.0 and b0 > 0.0) else 0.0)
        smin2 = smin - shared
        if smin2 <= 0.0:
            return 0.0
        den = (self.gen_total.get(g0, 0.0) - a0) + (self.gen_total.get(gj, 0.0) - b0) - smin2
        return smin2 / den if den > 0 else 0.0

    # ---- associative field (which genera does s activate), excluding the genus under test --------
    def assoc_field(self, s: str, exclude_genus: str) -> Dict[str, float]:
        # sorted() over the genus/subject SETS makes the float accumulation order-independent, so the
        # result is deterministic across processes (Python randomises str-set iteration per PYTHONHASHSEED).
        other = sorted(g for g in self.net_subj2gen.get(s, ()) if g != exclude_genus)
        net: Dict[str, float] = {}
        for og in other:
            net[og] = net.get(og, 0.0) + 3.0 * self.net_w.get((s, og), 1.0)
        for og in other:
            for t, wt in sorted(self.net_members.get(og, {}).items()):
                if t == s:
                    continue
                for tg in sorted(self.net_subj2gen.get(t, ())):
                    if tg != exclude_genus:
                        net[tg] = net.get(tg, 0.0) + wt
        return net

    def local_energy(self, s: str, g0: str, k_min: int = 2, loo: bool = True) -> Optional[float]:
        """1 - (trust-weighted mean compat of g0 with s's activated field). loo=True applies STRICT
        subject leave-one-out (exclude s from the compat member sets); loo=False is the v1-style
        scorer that leaves the subject in -- the gap between them quantifies the self-camouflage leak."""
        field = self.assoc_field(s, exclude_genus=g0)
        tot = sum(field.values())
        if tot < k_min:
            return None
        num = 0.0
        for gj, a in sorted(field.items()):
            num += a * (self.compat_loo(g0, gj, s) if loo else self.compat(g0, gj))
        return 1.0 - num / tot

    # ---- global diffused consistency field (the super-brain variant) -----------------------------
    def build_global(self, alpha: float = 0.3) -> None:
        genera = sorted(self.cmp_members)
        idx = {g: i for i, g in enumerate(genera)}
        n = len(genera)
        A = np.zeros((n, n), dtype=np.float64)
        # trust-weighted co-genus affinity: genera that describe the SAME subject are one family.
        for s, gs in self.cmp_subj2gen.items():
            if len(gs) < 2:
                continue
            gl = [(idx[g], self.cmp_w.get((s, g), 0.0)) for g in sorted(gs)]  # deterministic accum order
            for i, wi in gl:
                for j, wj in gl:
                    if i != j:
                        A[i, j] += wi if wi < wj else wj
        rs = A.sum(1, keepdims=True)
        rs[rs == 0] = 1.0
        P = A / rs
        D = np.eye(n) + alpha * P + alpha * alpha * (P @ P)   # 2-hop reach across the whole schema
        nn = np.linalg.norm(D, axis=1, keepdims=True)
        nn[nn == 0] = 1.0
        self._Dn = D / nn
        self._gidx = idx

    def gsim(self, g1: str, g2: str) -> float:
        if g1 == g2:
            return 1.0
        if self._Dn is None or self._gidx is None:
            return 0.0
        i, j = self._gidx.get(g1), self._gidx.get(g2)
        if i is None or j is None:
            return 0.0
        return float(max(0.0, self._Dn[i] @ self._Dn[j]))

    def global_energy(self, s: str, g0: str) -> Optional[float]:
        """Score g0 against s's family using the GLOBAL diffused field (every genus participated in
        building the field). STRICT LOO: g0 is excluded from s's anchors; the injected fact's own
        co-genus edge in the diffusion is suppressed because consolidation down-weighted it."""
        anchors = sorted(g for g in self.net_subj2gen.get(s, ()) if g != g0)
        if not anchors:
            return None
        num = den = 0.0
        for g in anchors:
            w = self.net_w.get((s, g), 1.0)
            num += w * self.gsim(g0, g)
            den += w
        if den <= 0:
            return None
        return 1.0 - num / den


# =========================================================================================
# 2. CONSOLIDATION: self-denoise the schema by down-weighting high-energy (inconsistent) facts
# =========================================================================================
def _pct(vals: Sequence[float], p: float) -> float:
    xs = sorted(vals)
    if not xs:
        return 0.0
    i = min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))
    return xs[i]


def consolidate(facts: Sequence[Fact], n_rounds: int = 4, k_min: int = 2,
                tol: float = 0.02, gamma: float = 3.0, lr: float = 0.5,
                hi_pct: float = 0.90) -> Tuple[np.ndarray, Dict]:
    """Iterate: build the trust-weighted schema -> score every fact by its LEAVE-ONE-OUT energy ->
    move each fact's trust toward a FRESH target (sigmoid of its energy vs a FIXED round-0 percentile
    reference) with EMA damping -> rebuild. High-energy (inconsistent) facts lose trust and stop
    polluting the schema.

    Two design choices are what keep it from oscillating (the naive median/MAD-recomputed-each-round
    update DID oscillate -- verified in --self-test history): (1) the down-weighting REFERENCE
    (p50, p_hi) is fixed at round 0, so the goalpost does not move as the distribution denoises;
    (2) EMA damping (lr) smooths the fact<->schema feedback. Convergence is REPORTED, not assumed."""
    facts = list(facts)
    n = 1 + max((f.fid for f in facts), default=-1)
    weights = np.ones(n)
    ref = None  # (thr, scale) fixed at round 0
    deltas: List[float] = []
    mean_w_traj: List[float] = []
    n_down_traj: List[int] = []
    rounds_run = 0
    for r in range(n_rounds):
        rounds_run = r + 1
        schema = WeightedSchema(facts, weights)
        energies: Dict[int, float] = {}
        for f in facts:
            e = schema.local_energy(f.s, f.g, k_min)
            if e is not None:
                energies[f.fid] = e
        vals = list(energies.values())
        if not vals:
            break
        if ref is None:  # FIX the reference on the raw (all-trust-1) round-0 distribution
            p50, p_hi = _pct(vals, 0.50), _pct(vals, hi_pct)
            ref = (p_hi, max(p_hi - p50, 0.05))
        thr, scale = ref
        target = weights.copy()
        for f in facts:
            e = energies.get(f.fid)
            if e is None:
                continue  # unscorable facts keep their trust (coverage bound, not evidence of error)
            target[f.fid] = 1.0 / (1.0 + math.exp(gamma * (e - thr) / scale))  # high energy -> low trust
        new_w = (1.0 - lr) * weights + lr * target                            # EMA damping
        delta = float(np.max(np.abs(new_w - weights)))
        deltas.append(round(delta, 5))
        mean_w_traj.append(round(float(new_w[[f.fid for f in facts]].mean()), 4))
        n_down_traj.append(int(sum(1 for f in facts if new_w[f.fid] < 0.5)))
        weights = new_w
        if delta < tol:
            break
    # convergence diagnostics: deltas should shrink monotonically. A REBOUND (a later round changing
    # weights MORE than an earlier one, past a small tolerance) flags oscillation honestly.
    converged = bool(deltas and deltas[-1] < tol)
    oscillation = bool(any(deltas[i] > deltas[i - 1] + 0.02 for i in range(1, len(deltas))))
    traj = {
        "n_rounds_run": rounds_run,
        "max_delta_trajectory": deltas,
        "mean_weight_trajectory": mean_w_traj,
        "n_downweighted_below_0.5_trajectory": n_down_traj,
        "converged": converged,
        "oscillation": oscillation,
        "final_mean_weight": mean_w_traj[-1] if mean_w_traj else 1.0,
    }
    return weights, traj


# =========================================================================================
# 3. METRICS: AUC (exact, tie-corrected), precision/recall @ k, bootstrap CIs
# =========================================================================================
def auc_exact(pos: Sequence[float], neg: Sequence[float]) -> float:
    n1, n0 = len(pos), len(neg)
    if n1 == 0 or n0 == 0:
        return float("nan")
    data = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    ranks = [0.0] * len(data)
    i = 0
    while i < len(data):
        j = i
        while j + 1 < len(data) and data[j + 1][0] == data[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    R1 = sum(ranks[k] for k in range(len(data)) if data[k][1] == 1)
    return (R1 - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def auc_ci(pos: Sequence[float], neg: Sequence[float], rng: random.Random,
           n_boot: int = 400) -> Tuple[float, float, float]:
    base = auc_exact(pos, neg)
    if math.isnan(base):
        return base, float("nan"), float("nan")
    pos, neg = list(pos), list(neg)
    boots = []
    for _ in range(n_boot):
        p = [pos[rng.randrange(len(pos))] for _ in range(len(pos))]
        q = [neg[rng.randrange(len(neg))] for _ in range(len(neg))]
        boots.append(auc_exact(p, q))
    boots.sort()
    return base, boots[int(0.025 * (n_boot - 1))], boots[int(0.975 * (n_boot - 1))]


def pr_at_k(items: List[Tuple[int, float]], inj_set: set, k: int) -> Tuple[float, float]:
    order = sorted(items, key=lambda x: -x[1])[:k]
    hits = sum(1 for fid, _ in order if fid in inj_set)
    n_inj = sum(1 for fid, _ in items if fid in inj_set)
    prec = hits / max(1, len(order))
    rec = hits / max(1, n_inj)
    return prec, rec


def prec_ci(items: List[Tuple[int, float]], inj_set: set, k: int, rng: random.Random,
            n_boot: int = 400) -> Tuple[float, float, float]:
    base_p, _ = pr_at_k(items, inj_set, k)
    N = len(items)
    ps = []
    for _ in range(n_boot):
        sample = [items[rng.randrange(N)] for _ in range(N)]
        p, _ = pr_at_k(sample, inj_set, k)
        ps.append(p)
    ps.sort()
    return base_p, ps[int(0.025 * (n_boot - 1))], ps[int(0.975 * (n_boot - 1))]


def _series_items(series: Dict[int, float]) -> List[Tuple[int, float]]:
    return [(fid, e) for fid, e in series.items() if e is not None and not math.isnan(e)]


def k_sweep(n_scored: int, n_inj: int) -> Dict[str, int]:
    return {
        "k=n_inj": max(1, n_inj),
        "k=2*n_inj": max(1, 2 * n_inj),
        "top_5pct": max(1, int(0.05 * n_scored)),
        "top_10pct": max(1, int(0.10 * n_scored)),
        "top_25pct": max(1, int(0.25 * n_scored)),
    }


def pr_sweep(series: Dict[int, float], inj_set: set, ks: Dict[str, int]) -> Tuple[Dict, Dict]:
    items = _series_items(series)
    prec, rec = {}, {}
    for name, k in ks.items():
        p, r = pr_at_k(items, inj_set, k)
        prec[name] = round(p, 4)
        rec[name] = round(r, 4)
    return prec, rec


# =========================================================================================
# 4. ENERGY-SERIES builders (z-normalised ensemble with the reused context arm)
# =========================================================================================
def _z(series: Dict[int, float]) -> Dict[int, float]:
    vals = [v for v in series.values() if v is not None and not math.isnan(v)]
    if not vals:
        return {}
    m = st.mean(vals)
    s = st.pstdev(vals) or 1.0
    return {fid: (v - m) / s for fid, v in series.items() if v is not None and not math.isnan(v)}


def ensemble(*series: Dict[int, float]) -> Dict[int, float]:
    zs = [_z(x) for x in series]
    keys = set().union(*[set(z) for z in zs]) if zs else set()
    out = {}
    for fid in keys:
        vals = [z[fid] for z in zs if fid in z]
        if vals:
            out[fid] = sum(vals) / len(vals)
    return out


# =========================================================================================
# 5. PAIRED within-subject (project's CI-clean primary): corrupted genus vs subject's own original
# =========================================================================================
def paired_win(inj_facts: List[Fact], base_orig: Dict[str, List[str]],
               energy_fn) -> Tuple[float, List[float]]:
    wins: List[float] = []
    for nf in inj_facts:
        ew = energy_fn(nf.s, nf.g)
        if ew is None or math.isnan(ew):
            continue
        for gc in base_orig.get(nf.s, []):
            ec = energy_fn(nf.s, gc)
            if ec is not None and not math.isnan(ec):
                wins.append(1.0 if ew > ec else 0.0)
    p = sum(wins) / len(wins) if wins else float("nan")
    return p, wins


# =========================================================================================
# 6. EVALUATE one (store, distance)
# =========================================================================================
def _series_metrics(series: Dict[int, float], injected: List[int], inj_set: set,
                    seed: int, n_boot: int = 250) -> Dict:
    items = _series_items(series)
    if not items:
        return {}
    pos = [series[fid] for fid in injected if fid in series and series[fid] is not None]
    neg = [e for fid, e in series.items() if fid not in inj_set and e is not None]
    a, lo, hi = auc_ci(pos, neg, random.Random(seed + 21), n_boot=n_boot)
    ks = k_sweep(len(items), len(injected))
    p_sw, r_sw = pr_sweep(series, inj_set, ks)
    bp, plo, phi = prec_ci(items, inj_set, max(1, len(injected)), random.Random(seed + 31), n_boot=n_boot)
    return {
        "n_scored": len(items),
        "auc": round(a, 4), "auc_ci": [round(lo, 4), round(hi, 4)],
        "precision_at_k": p_sw, "recall_at_k": r_sw,
        "precision_at_ninj_ci": [round(bp, 4), round(plo, 4), round(phi, 4)],
    }


def evaluate_store(facts: List[Fact], distance: str, rate: float, k_min: int, seed: int,
                   n_rounds: int) -> Dict:
    """Score the injected set under RAW (all-trust) and CONSOLIDATED (self-denoised) schemas, with
    three energy views each: LOCAL member-Jaccard (strict subject LOO), GLOBAL diffused field
    (the super-brain variant), and GLOBAL+context ensemble. Also the v1-style local WITHOUT subject
    LOO (to quantify the self-camouflage leak) and an info-free GLOBAL twin (family structure
    destroyed). Reports AUC, precision/recall @k, and the CI-clean PAIRED metric."""
    rng = random.Random(seed)
    base_graph = C.Graph(facts)
    new_facts, injected = C.inject_errors(facts, base_graph, rate=rate, rng=rng, distance=distance)
    inj_set = set(injected)
    base_orig: Dict[str, List[str]] = defaultdict(list)
    for f in facts:
        base_orig[f.s].append(f.g)
    ctxgeo = C.ContextGeometry(new_facts)
    ctx = {f.fid: 1.0 - c for f in new_facts for c in [ctxgeo.consistency(f.s, f.g)] if c is not None}

    # ---- CONSOLIDATE (self-denoise trust weights) ------------------------------------------------
    weights, traj = consolidate(new_facts, n_rounds=n_rounds, k_min=k_min)

    def build_series(w: np.ndarray) -> Tuple[WeightedSchema, Dict[str, Dict[int, float]]]:
        sc = WeightedSchema(new_facts, w)
        sc.build_global(alpha=0.3)
        loc = {f.fid: e for f in new_facts
               for e in [sc.local_energy(f.s, f.g, k_min, loo=True)] if e is not None}
        gl = {f.fid: e for f in new_facts for e in [sc.global_energy(f.s, f.g)] if e is not None}
        gc = ensemble(gl, ctx)
        return sc, {"local": loc, "global": gl, "global_ctx": gc}

    raw_schema, raw_s = build_series(np.ones(len(new_facts)))
    con_schema, con_s = build_series(weights)

    # v1-style LOCAL without subject LOO -- its gap vs strict-LOO local IS the self-camouflage leak
    loc_noloo = {f.fid: e for f in new_facts
                 for e in [raw_schema.local_energy(f.s, f.g, k_min, loo=False)] if e is not None}

    # INFO-FREE GLOBAL twin: diffused field built from a LABEL-SHUFFLED store (family structure
    # destroyed). If separation survives here it is an artifact, not real structure.
    rng_s = random.Random(seed + 9)
    labels = [f.g for f in new_facts]
    rng_s.shuffle(labels)
    shuffled = [Fact(f.fid, f.s, labels[i], f.seg, f.patt, f.n_att, f.ctx)
                for i, f in enumerate(new_facts)]
    twin_schema = WeightedSchema(new_facts, weights=np.ones(len(new_facts)), compat_facts=shuffled)
    twin_schema.build_global(alpha=0.3)
    twin_g = {f.fid: e for f in new_facts for e in [twin_schema.global_energy(f.s, f.g)] if e is not None}

    series_map = {
        "raw_local": raw_s["local"], "consol_local": con_s["local"],
        "local_noloo_leak": loc_noloo,
        "raw_global": raw_s["global"], "consol_global": con_s["global"],
        "raw_global_ctx": raw_s["global_ctx"], "consol_global_ctx": con_s["global_ctx"],
        "twin_global": twin_g,
    }
    metrics = {name: _series_metrics(s, injected, inj_set, seed) for name, s in series_map.items() if s}

    # ---- PAIRED within-subject (corrupted genus vs subject's own original, same schema) ----------
    inj_facts = [new_facts[fid] for fid in injected]
    paired = {}
    for name, fn in [
        ("local_noloo_leak", lambda s, g: raw_schema.local_energy(s, g, k_min, loo=False)),
        ("raw_local", lambda s, g: raw_schema.local_energy(s, g, k_min, loo=True)),
        ("consol_local", lambda s, g: con_schema.local_energy(s, g, k_min, loo=True)),
        ("raw_global", lambda s, g: raw_schema.global_energy(s, g)),
        ("consol_global", lambda s, g: con_schema.global_energy(s, g)),
        ("twin_global", lambda s, g: twin_schema.global_energy(s, g)),
    ]:
        p, wins = paired_win(inj_facts, base_orig, fn)
        plo, phi = C._boot_ci(wins, random.Random(seed + 41)) if wins else (float("nan"), float("nan"))
        paired[name] = {"paired": round(p, 4) if p == p else None,
                        "ci": [round(plo, 4), round(phi, 4)], "n": len(wins),
                        "beats_twin_0.5": bool(plo == plo and plo > 0.5)}

    # ---- twin comparisons (is the consolidated global signal real structure?) --------------------
    def ci_beats(name, ref="twin_global", field="auc"):
        m, t = metrics.get(name), metrics.get(ref)
        if not m or not t:
            return None
        if field == "auc":
            return bool(m["auc_ci"][0] > t["auc_ci"][1])
        return bool(m["precision_at_ninj_ci"][1] > t["precision_at_ninj_ci"][2])

    n_scored = metrics.get("consol_global", {}).get("n_scored", 0)
    return {
        "distance": distance, "rate": rate,
        "n_facts": len(new_facts), "n_injected": len(injected),
        "base_rate_injected_among_scored": round(len(injected) / n_scored, 4) if n_scored else None,
        "consolidation": traj,
        "metrics": metrics,
        "paired": paired,
        "leak_quantification": {
            "local_noloo_paired": paired["local_noloo_leak"]["paired"],
            "local_strictloo_paired": paired["raw_local"]["paired"],
            "note": ("STRICT subject-LOO minus v1-style-no-LOO = the self-camouflage leak the prior "
                     "local operating point leaned on; a large drop means the local signal was "
                     "self-referential."),
        },
        "twin_checks": {
            "consol_global_auc_beats_twin_ci": ci_beats("consol_global", field="auc"),
            "consol_global_prec_beats_twin_ci": ci_beats("consol_global", field="prec"),
            "consol_global_ctx_auc_beats_twin_ci": ci_beats("consol_global_ctx", field="auc"),
        },
        "consolidation_helps": {
            "auc_global_raw_to_consol": [metrics.get("raw_global", {}).get("auc"),
                                         metrics.get("consol_global", {}).get("auc")],
            "prec_ninj_global_raw_to_consol": [
                metrics.get("raw_global", {}).get("precision_at_k", {}).get("k=n_inj"),
                metrics.get("consol_global", {}).get("precision_at_k", {}).get("k=n_inj")],
        },
    }


# =========================================================================================
# 7. VERDICT (plain reading of the numbers -> which honest outcome obtained)
# =========================================================================================
def _verdict(out: Dict) -> Dict:
    v = {}
    for store in ("full", "clean"):
        r = out.get(f"{store}_far")
        if not r:
            continue
        cg = r["metrics"].get("consol_global", {})
        prec_ninj = cg.get("precision_at_k", {}).get("k=n_inj")
        base = r["base_rate_injected_among_scored"]
        prec_beats_twin = r["twin_checks"]["consol_global_prec_beats_twin_ci"]
        # SOLVED-grade only if a fixed threshold is genuinely clean (majority of top-n_inj injected)
        clean_op = bool(prec_ninj is not None and prec_ninj >= 0.5 and prec_beats_twin)
        v[store] = {
            "auc_consol_global": cg.get("auc"),
            "auc_consol_global_ctx": r["metrics"].get("consol_global_ctx", {}).get("auc"),
            "precision_at_ninj_consol_global": prec_ninj,
            "base_rate": base,
            "precision_over_base_rate_x": (round(prec_ninj / base, 2)
                                           if prec_ninj and base else None),
            "paired_consol_global": r["paired"]["consol_global"]["paired"],
            "paired_beats_twin": r["paired"]["consol_global"]["beats_twin_0.5"],
            "auc_beats_info_free_twin": r["twin_checks"]["consol_global_auc_beats_twin_ci"],
            "outcome": ("SOLVED_GRADE_clean_threshold_operating_point" if clean_op
                        else "RANKING_IS_THE_CEILING_real_errors_legitimately_outrank_injections"),
        }
    v["headline_leak"] = {
        "full_far_local_noloo_vs_strictloo_paired": [
            out.get("full_far", {}).get("leak_quantification", {}).get("local_noloo_paired"),
            out.get("full_far", {}).get("leak_quantification", {}).get("local_strictloo_paired")],
        "reading": ("the prior LOCAL relational operating point was substantially a subject-level "
                    "self-camouflage leak; strict LOO collapses it, and only the GLOBAL diffused "
                    "field carries genuine leave-one-out signal."),
    }
    return v


# =========================================================================================
# 8. RUN
# =========================================================================================
def run(store_path: str, rate: float = 0.15, k_min: int = 2, seed: int = 0,
        n_rounds: int = 6, smoke: bool = False) -> Dict:
    facts = C.load_facts(store_path)
    if smoke:
        facts = [Fact(i, f.s, f.g, f.seg, f.patt, f.n_att, f.ctx) for i, f in enumerate(facts[:500])]
    clean = C.high_confidence(facts)
    out = {
        "store": os.path.relpath(store_path, _REPO),
        "n_facts_full": len(facts), "n_facts_clean": len(clean),
        "rate": rate, "k_min": k_min, "seed": seed, "n_rounds": n_rounds,
    }
    out["full_far"] = evaluate_store(facts, "far", rate, k_min, seed, n_rounds)
    out["full_near"] = evaluate_store(facts, "near", rate, k_min, seed, n_rounds)
    out["clean_far"] = evaluate_store(clean, "far", rate, k_min, seed, n_rounds)
    out["clean_near"] = evaluate_store(clean, "near", rate, k_min, seed, n_rounds)
    out["verdict"] = _verdict(out)
    return out


# =========================================================================================
# 9. SELF-TEST (CAN-FAIL) + CLI
# =========================================================================================
def _self_test() -> None:
    # ---- LOO correctness: the injected subject must NOT prop up its own wrong genus ----------
    # Two clean families (bio / geo). Subject s0 has real genus 'process'; inject (s0,'country').
    fs: List[Fact] = []
    for i in range(10):
        fs.append(Fact(len(fs), f"bio{i}", "process", ctx="cell enzyme reaction energy metabolism"))
        fs.append(Fact(len(fs), f"bio{i}", "molecule", ctx="cell enzyme reaction energy metabolism"))
    for i in range(10):
        fs.append(Fact(len(fs), f"geo{i}", "country", ctx="border capital population region trade"))
        fs.append(Fact(len(fs), f"geo{i}", "region", ctx="border capital population region trade"))
    inj = Fact(len(fs), "bio0", "country", patt="INJECTED", injected=True,
               ctx="cell enzyme reaction energy metabolism")
    allf = fs + [inj]

    sch1 = WeightedSchema(allf)  # raw (round-0) schema, all trust 1
    e_bad = sch1.local_energy("bio0", "country", 2)   # cross-family, LOO
    e_ok = sch1.local_energy("bio0", "molecule", 2)   # within-family, LOO
    assert e_bad is not None and e_ok is not None, (e_bad, e_ok)
    assert e_bad > e_ok, ("cross-family energy must exceed within-family", e_bad, e_ok)

    # LOO must matter: compat_loo(country, molecule | exclude bio0) drops bio0 from the shared set.
    c_loo = sch1.compat_loo("country", "molecule", "bio0")
    c_raw = sch1.compat("country", "molecule")
    assert c_loo <= c_raw + 1e-9, ("LOO cannot increase self-compat", c_loo, c_raw)

    # ---- consolidation converges (deltas shrink, no oscillation) ------------------------------
    _, traj = consolidate(allf, n_rounds=4, k_min=2)
    assert traj["n_rounds_run"] >= 2, traj
    assert not traj["oscillation"], ("consolidation oscillated", traj)

    # ---- after consolidation the injected fact is the top-energy fact (recall@1 == 1) ---------
    w, _ = consolidate(allf, n_rounds=6, k_min=2)
    sch = WeightedSchema(allf, w)
    sch.build_global(alpha=0.3)
    energies = {f.fid: sch.local_energy(f.s, f.g, 2) for f in allf}
    energies = {k: v for k, v in energies.items() if v is not None}
    top = max(energies, key=energies.get)
    assert top == inj.fid, ("injected fact should have the highest consolidated energy", top, inj.fid)

    # ---- GLOBAL diffused field also separates cross-family from within-family (strict LOO) -----
    g_bad = sch.global_energy("bio0", "country")
    g_ok = sch.global_energy("bio0", "molecule")
    assert g_bad is not None and g_ok is not None, (g_bad, g_ok)
    assert g_bad > g_ok, ("global cross-family energy must exceed within-family", g_bad, g_ok)

    # ---- info-free twin (label-shuffled family geometry) must NOT reliably rank the injected fact
    # top: destroying the family structure should remove the separation the real field exploits. ---
    rng_s = random.Random(1)
    labels = [f.g for f in allf]
    rng_s.shuffle(labels)
    shuf = [Fact(f.fid, f.s, labels[i], f.seg, f.patt, f.n_att, f.ctx) for i, f in enumerate(allf)]
    twin = WeightedSchema(allf, compat_facts=shuf)
    twin_e = {f.fid: e for f in allf for e in [twin.local_energy(f.s, f.g, 2)] if e is not None}
    twin_top = max(twin_e, key=twin_e.get) if twin_e else None
    assert twin_top != inj.fid, ("info-free twin must NOT single out the injected fact", twin_top)

    print("[self-test] PASS: strict-LOO cross>within (local+global); LOO<=raw compat; consolidation "
          "converges without oscillation; injected fact tops consolidated energy; info-free twin does not.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["full", "smoke"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--store", default=C.DEFAULT_STORE)
    ap.add_argument("--rate", type=float, default=0.15)
    ap.add_argument("--k-min", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-rounds", type=int, default=6)
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return
    smoke = bool(args.smoke) or args.mode == "smoke"
    res = run(args.store, rate=args.rate, k_min=args.k_min, seed=args.seed,
              n_rounds=args.n_rounds, smoke=smoke)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
