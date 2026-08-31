"""Within-store CONSISTENCY / CORRECTNESS cleanup for the substrate knowledge base.

PROBLEM (the_knowledge_store_has_no_correctness_or_consistency_cleanup): hd_fact_store
INGEST-VET vets SOURCE-TRUST only -- a clean (non-conflicting) fact just STORES, and same-(s,r)
conflicts resolve by SOURCE RANK, never by whether the fact CONTRADICTS the coherent majority of
what is already known. So the foundation accumulates every extraction error. Build the missing
"does this fit?" check: score each stored fact for CONSISTENCY with the surrounding knowledge and
down-weight the ones that contradict the coherent majority -- using ONLY what is inside the store
(no external LLM, no external truth oracle at inference).

BRAIN FRAME (PINNED, from two literature drills in this problem folder):
  * schema congruence / conflict monitoring: the brain flags a claim that lights up something
    INCOMPATIBLE with a coherent web of related knowledge (ACC conflict = Hopfield energy
    -Sum a_i a_j w_ij; mPFC match-to-activated-schema; van Kesteren, Ghosh & Gilboa, Botvinick).
  * the judgement is over the concept's ACTIVATED ASSOCIATIVE NETWORK, not a lonely fact -- so a
    fact with too little related knowledge gets NO signal (INSUFFICIENT_SUPPORT is brain-faithful,
    not a defect; the coverage bound re-points to p1 = denser extraction).
  * grounding drill: deriving semantic geometry FROM the relational graph is exactly how the
    congenitally blind ground meaning (dorsal ATL hub fed by the linguistic spoke; Wang/Bi, Bedny,
    Landau). The graph's quality is the ceiling; text recovers RELATIONAL structure and loses modal
    particulars/qualia. So we build the associative geometry from BOTH the relational graph AND the
    store's own evidence sentences (the linguistic spoke), never from an external embedding.

MECHANISM (OUR-INVENTION under test, glass-box). For a fact f=(s, isa, g) score its ENERGY
(conflict; high == contradicts the majority) as 1 - consistency, where consistency ensembles two
within-store views of s's activated associative network, EXCLUDING f:
  (A) RELATIONAL: how compatible g is with the genera implied by s's OTHER genera + its siblings,
      where genus-genus COMPATIBILITY = member-set overlap in the graph (concepts that share
      members get correlated -- the phase-diagram shift the raw orthogonal-code store lacks).
  (B) DISTRIBUTIONAL: does s's own usage (source-sentence context, GENUS WORDS STRIPPED to kill
      the definition-string leak) look like the usage of the OTHER things assigned genus g?
The two z-normalised energies are averaged; a fact scorable by neither (a lonely singleton with no
context) -> INSUFFICIENT_SUPPORT. Ensemble because (A) is clean but sparse (coverage ~0.35) and (B)
adds coverage + a distributional view; together coverage ~0.69.

VALIDATION on the REAL extracted is-a/genus store (definitional_facts_v5; modern SimpleWiki +
OpenStax-biology; NO McGuffey age confound). Controlled corruption (gold-free: we know what we
injected). PRIMARY metrics are robust to the store already being noisy:
  * PAIRED within-subject: for the SAME subject, does the CORRUPTED genus score higher energy than
    its OWN original genus? (immune to base-store noise; the info-free twin is 0.5.)
  * AUC: injected-vs-noninjected energy ranking (contaminated by real store noise -> a LOWER bound).
Reported over floors (source-trust INGEST-VET; a frequency/degree prior) and the random-drop twin,
with a FAR/NEAR distance curve (gross clashes vs within-family near-misses -- the brain's graded
response) and the honest COVERAGE bound.

ASCII-only. No spaCy, no torch (pure python/math). Deterministic (seeded injection).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics as st
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# KB_REFERENT: data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl
DEFAULT_STORE = os.path.join(
    _REPO, "data", "foundation", "reading_grounding_v5_termboundary",
    "definitional_facts_v5.jsonl")
OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_store_consistency_cleanup_v1")

_STOP = set("the a an of to and in is are was were be as for on with by that this it its from at "
            "or which who whom whose into other more most some such can may also they their there "
            "these those has have had not but if then than when where while what how our your his "
            "her out one two use used using both each any all will would could should about".split())


# =========================================================================================
# 1. LOAD the real store as an is-a graph
# =========================================================================================
@dataclass
class Fact:
    fid: int
    s: str          # subject / term (definiendum)
    g: str          # object / genus (is-a parent)
    seg: str = ""
    patt: str = ""
    n_att: int = 1
    ctx: str = ""   # source-sentence text (the linguistic spoke)
    injected: bool = False   # True == a planted error (gold-free ground truth)


def load_facts(path: str) -> List[Fact]:
    facts: List[Fact] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            s = str(r["subject"]).strip().lower()
            g = str(r["object"]).strip().lower()
            if not s or not g or s == g:
                continue
            ctx = " ".join(r.get("source_sentences", []) or [])
            facts.append(Fact(fid=len(facts), s=s, g=g, seg=r.get("segment", ""),
                              patt=r.get("pattern", ""),
                              n_att=int(r.get("n_attestations", 1) or 1), ctx=ctx.lower()))
    return facts


# =========================================================================================
# 2. GRAPH + genus-genus compatibility (relational geometry) and the CONTEXT geometry
# =========================================================================================
class Graph:
    def __init__(self, facts: Sequence[Fact]):
        self.subj2gen: Dict[str, set] = defaultdict(set)
        self.gen2subj: Dict[str, set] = defaultdict(set)
        self.subj2fids: Dict[str, List[int]] = defaultdict(list)
        for f in facts:
            self.subj2gen[f.s].add(f.g)
            self.gen2subj[f.g].add(f.s)
            self.subj2fids[f.s].append(f.fid)
        self._compat: Dict[Tuple[str, str], float] = {}

    def compat(self, g1: str, g2: str) -> float:
        """Member-set Jaccard: genera that share member terms are the same family."""
        if g1 == g2:
            return 1.0
        key = (g1, g2) if g1 <= g2 else (g2, g1)
        c = self._compat.get(key)
        if c is not None:
            return c
        a, b = self.gen2subj.get(g1, set()), self.gen2subj.get(g2, set())
        inter = len(a & b)
        c = inter / (len(a) + len(b) - inter) if inter else 0.0
        self._compat[key] = c
        return c

    def assoc_network(self, s: str, exclude_genus: str) -> Counter:
        """s's activated associative network (genera), EXCLUDING the fact under test: s's OTHER
        genera (strong) + the genera of terms that share those other genera with s (siblings)."""
        other = set(self.subj2gen.get(s, set())) - {exclude_genus}
        net: Counter = Counter()
        for og in other:
            net[og] += 3
        for og in other:
            for t in self.gen2subj.get(og, ()):
                if t == s:
                    continue
                for tg in self.subj2gen.get(t, ()):
                    if tg != exclude_genus:
                        net[tg] += 1
        return net


class DiffusedGeometry:
    """GRAPH-DIFFUSED code geometry -- the phase-diagram shift made native. The raw store's symbol
    codes are random-ORTHOGONAL (distinct genera have ~0 cosine), so schema-congruence-by-cosine is
    impossible on it. We instead DIFFUSE each genus's code over the relational graph so genera that
    describe similar terms become CORRELATED (process~event~reaction; molecule~protein~macromolecule)
    -- exactly the Hebbian mechanism by which brain schemas develop overlapping representations. This
    lifts genus-genus compatibility from the sparse member-Jaccard (near-0 for most pairs -> no
    separation) to a graded family similarity, and it is what makes the absolute conflict-energy
    ranking clean. Built from the store's OWN structure (no external embedding); the dimensional
    audit's lesson is honoured -- CODE ORTHOGONALITY, not n_dim, is the fidelity axis.

    Affinity = co-genus (two genera of the SAME subject) + member-set overlap; diffused as
    D = I + a P + a^2 P^2 (2-hop reach); compat = cosine of L2-normalised rows.

    REJECTED AS DEFAULT (documented ablation): built from the store-WITH-errors it LEAKS via error
    self-camouflage -- each injected fact's co-genus edge is SPREAD by the diffusion, pulling its own
    wrong genus toward the real family so the error looks consistent (honest paired ~0.50, vs a leaky
    AUC 0.98 when the geometry is built from the clean store). member-Jaccard's LOCALITY avoids this.
    The principled fix is leave-one-out geometry (exclude the scored fact's edge) -- a follow-on.
    """

    def __init__(self, facts: Sequence[Fact], alpha: float = 0.25):
        subj2gen: Dict[str, set] = defaultdict(set)
        gen2subj: Dict[str, set] = defaultdict(set)
        for f in facts:
            subj2gen[f.s].add(f.g)
            gen2subj[f.g].add(f.s)
        genera = sorted(gen2subj)
        self._idx = {g: i for i, g in enumerate(genera)}
        n = len(genera)
        M = np.zeros((n, n), dtype=np.float64)
        for gs in subj2gen.values():                       # co-genus edges
            gl = [self._idx[g] for g in gs]
            for i in gl:
                for j in gl:
                    if i != j:
                        M[i, j] += 1.0
        for g1 in genera:                                  # member-overlap edges (shared family)
            m1 = gen2subj[g1]
            if len(m1) < 2:
                continue
            i1 = self._idx[g1]
            for g2 in genera:
                if g1 >= g2:
                    continue
                inter = len(m1 & gen2subj[g2])
                if inter >= 2:
                    i2 = self._idx[g2]
                    M[i1, i2] += inter
                    M[i2, i1] += inter
        rs = M.sum(1, keepdims=True)
        rs[rs == 0] = 1.0
        P = M / rs
        D = np.eye(n) + alpha * P + alpha * alpha * (P @ P)
        nn = np.linalg.norm(D, axis=1, keepdims=True)
        nn[nn == 0] = 1.0
        self._D = D / nn

    def compat(self, g1: str, g2: str) -> float:
        if g1 == g2:
            return 1.0
        i, j = self._idx.get(g1), self._idx.get(g2)
        if i is None or j is None:
            return 0.0
        return float(max(0.0, self._D[i] @ self._D[j]))


class ContextGeometry:
    """Distributional view built from the store's OWN evidence sentences (the linguistic spoke).
    GENUS WORDS ARE STRIPPED so the "X is a Y" definition string cannot leak the answer -- only the
    residual surrounding usage (amino, bond, cell...) is used. A term is consistent with genus g if
    its usage looks like the usage of the OTHER terms assigned g (leakage-controlled: exclude s)."""

    def __init__(self, facts: Sequence[Fact]):
        genus_words = set()
        for f in facts:
            for tok in f.g.split():
                w = "".join(c for c in tok if c.isalpha())
                if w:
                    genus_words.add(w)
        self._genus_words = genus_words
        self.subj_ctx: Dict[str, Counter] = {f.s: self._words(f.ctx) for f in facts}
        df: Counter = Counter()
        for c in self.subj_ctx.values():
            for w in c:
                df[w] += 1
        S = max(1, len(self.subj_ctx))
        self.subj_vec: Dict[str, Dict[str, float]] = {}
        for s, c in self.subj_ctx.items():
            self.subj_vec[s] = {w: cnt * math.log((S + 1) / (1 + df[w])) for w, cnt in c.items()}
        self._norm = {s: (math.sqrt(sum(x * x for x in v.values())) or 1.0)
                      for s, v in self.subj_vec.items()}
        self.gen2subj: Dict[str, List[str]] = defaultdict(list)
        for f in facts:
            self.gen2subj[f.g].append(f.s)

    def _words(self, text: str) -> Counter:
        out: Counter = Counter()
        for tok in text.replace(".", " ").replace(",", " ").split():
            tok = "".join(c for c in tok if c.isalpha())
            if len(tok) >= 4 and tok not in _STOP and tok not in self._genus_words:
                out[tok] += 1
        return out

    def _cos(self, s1: str, s2: str) -> float:
        a, b = self.subj_vec.get(s1), self.subj_vec.get(s2)
        if not a or not b:
            return 0.0
        ks = a.keys() & b.keys()
        if not ks:
            return 0.0
        return sum(a[k] * b[k] for k in ks) / (self._norm[s1] * self._norm[s2])

    def consistency(self, s: str, g: str, min_members: int = 2) -> Optional[float]:
        if not self.subj_vec.get(s):        # no usage context -> this view abstains (coverage bound)
            return None
        members = [t for t in self.gen2subj.get(g, ()) if t != s and self.subj_vec.get(t)]
        if len(members) < min_members:
            return None
        return sum(self._cos(s, t) for t in members) / len(members)


# =========================================================================================
# 3. ENSEMBLE energy scorer
# =========================================================================================
@dataclass
class Verdict:
    fid: int
    s: str
    g: str
    energy: float                 # HIGH == contradicts the majority (flag)
    status: str                   # SCORED | INSUFFICIENT_SUPPORT
    e_rel: Optional[float] = None
    e_ctx: Optional[float] = None
    confidence: Optional[float] = None  # schema SHARPNESS (soft-Simpson coherence) = Friston precision
                                        # (inverse variance, NOT amount). High == basic-level, sharp
                                        # schema -> reliable verdict; low == generic/superordinate.


class Scorer:
    """Ensemble energy = mean of z-normalised relational + distributional energies. Facts scorable
    by neither view -> INSUFFICIENT_SUPPORT (the coverage bound)."""

    def __init__(self, facts: Sequence[Fact], k_min: int = 2, geometry: str = "jaccard",
                 alpha: float = 0.25, diffused: Optional[DiffusedGeometry] = None):
        self.graph = Graph(facts)
        self.ctx = ContextGeometry(facts)
        self.k_min = k_min
        self.geometry = geometry
        # DIFFUSED (default): native graph-correlated codes. JACCARD: sparse member-overlap (ablation).
        # `diffused` can be injected to run an INFO-FREE geometry twin (built from a shuffled store).
        self._diff = diffused if diffused is not None else (
            DiffusedGeometry(facts, alpha) if geometry == "diffused" else None)
        self._facts = list(facts)
        self._calibrate()

    def _compat(self, g1: str, g2: str) -> float:
        if self._diff is not None:
            return self._diff.compat(g1, g2)
        return self.graph.compat(g1, g2)

    # raw per-view energies (None if that view cannot score the fact)
    def _rel_energy(self, s: str, g: str) -> Optional[float]:
        net = self.graph.assoc_network(s, exclude_genus=g)
        tot = sum(net.values())
        if tot < self.k_min:
            return None
        num = sum(w * self._compat(g, g2) for g2, w in net.items())
        return 1.0 - num / tot

    def _ctx_energy(self, s: str, g: str) -> Optional[float]:
        c = self.ctx.consistency(s, g)
        return None if c is None else 1.0 - c

    def _coherence(self, s: str, g: str) -> Optional[float]:
        """Schema SHARPNESS = soft-Simpson probability that two random neighbours in s's activated
        network agree on a family. This is Friston precision (inverse variance of the estimate), NOT
        the amount of evidence. Generic/superordinate subjects have DIFFUSE networks -> low
        coherence -> low-confidence verdict (the brain's basic-level advantage). g-independent (g
        only enters via exclusion), so it cannot launder the label under test."""
        net = self.graph.assoc_network(s, exclude_genus=g)
        tot = sum(net.values())
        if tot < self.k_min:
            return None
        gs = list(net)
        ws = [net[x] / tot for x in gs]
        return sum(ws[i] * ws[j] * self._compat(gs[i], gs[j])
                   for i in range(len(gs)) for j in range(len(gs)))

    def _calibrate(self) -> None:
        rel = [e for f in self._facts for e in [self._rel_energy(f.s, f.g)] if e is not None]
        ctx = [e for f in self._facts for e in [self._ctx_energy(f.s, f.g)] if e is not None]
        self._mr, self._sr = (st.mean(rel), st.pstdev(rel) or 1.0) if rel else (0.0, 1.0)
        self._mc, self._sc = (st.mean(ctx), st.pstdev(ctx) or 1.0) if ctx else (0.0, 1.0)

    def score(self, s: str, g: str, fid: int = -1) -> Verdict:
        er, ec = self._rel_energy(s, g), self._ctx_energy(s, g)
        zs = []
        if er is not None:
            zs.append((er - self._mr) / self._sr)
        if ec is not None:
            zs.append((ec - self._mc) / self._sc)
        if not zs:
            return Verdict(fid=fid, s=s, g=g, energy=float("nan"),
                           status="INSUFFICIENT_SUPPORT", e_rel=er, e_ctx=ec)
        return Verdict(fid=fid, s=s, g=g, energy=sum(zs) / len(zs), status="SCORED",
                       e_rel=er, e_ctx=ec, confidence=self._coherence(s, g))


# =========================================================================================
# 4. CONTROLLED CORRUPTION (gold-free ground truth)
# =========================================================================================
def inject_errors(facts: List[Fact], graph: Graph, rate: float, rng: random.Random,
                  distance: str = "far") -> Tuple[List[Fact], List[int]]:
    """Add contradictory facts on subjects that retain INDEPENDENT evidence (>=1 other genus), with
    the wrong genus at a chosen compatibility DISTANCE. Errors on lonely singletons are undetectable
    by ANY within-store check (incl. the brain) and belong to the coverage bound, not the error set."""
    genera = [g for g, mem in graph.gen2subj.items() if len(mem) >= 3]
    eligible = [f for f in facts if len(graph.subj2gen.get(f.s, set())) >= 2]
    n_inject = max(1, int(round(len(eligible) * rate)))
    rng.shuffle(eligible)
    injected_fids: List[int] = []
    new_facts = list(facts)
    for f in eligible[:n_inject]:
        cands = [(g, graph.compat(f.g, g)) for g in genera
                 if g != f.g and g not in graph.subj2gen.get(f.s, set())]
        if not cands:
            continue
        if distance == "far":
            pool = [g for g, c in cands if c == 0.0] or [g for g, _ in sorted(cands, key=lambda x: x[1])[:20]]
        elif distance == "near":
            pool = [g for g, c in cands if 0.0 < c <= 0.34] or [g for g, _ in sorted(cands, key=lambda x: -x[1])[:20]]
        else:
            pool = [g for g, _ in cands]
        g_wrong = rng.choice(pool)
        nf = Fact(fid=len(new_facts), s=f.s, g=g_wrong, seg=f.seg, patt="INJECTED",
                  n_att=1, ctx=f.ctx, injected=True)
        new_facts.append(nf)
        injected_fids.append(nf.fid)
    return new_facts, injected_fids


# =========================================================================================
# 5. FLOORS
# =========================================================================================
def floor_ingest_vet(facts: Sequence[Fact]) -> Dict[int, float]:
    """SOURCE-TRUST INGEST-VET: sees only same-(s,r) conflicts and, at equal trust, FLAGS both
    without picking the outlier. Suspicion = 1.0 if the fact's subject carries a multi-genus
    conflict, else 0.0 -- it cannot say WHICH side is wrong (the whole gap)."""
    multi = {s for s, c in Counter(f.s for f in facts).items()}
    seen: Dict[str, set] = defaultdict(set)
    for f in facts:
        seen[f.s].add(f.g)
    return {f.fid: (1.0 if len(seen[f.s]) >= 2 else 0.0) for f in facts}


def floor_frequency(facts: Sequence[Fact], graph: Graph) -> Dict[int, float]:
    """Frequency/degree prior: suspicion = 1/(n_att * (1+genus_degree)) -- 'rare facts are suspect'."""
    return {f.fid: 1.0 / (f.n_att * (1 + len(graph.gen2subj.get(f.g, set())))) for f in facts}


# =========================================================================================
# 6. METRICS
# =========================================================================================
def _auc(pos: List[float], neg: List[float], rng: random.Random, n: int = 30000) -> float:
    if not pos or not neg:
        return float("nan")
    w = t = 0
    for _ in range(n):
        a, b = rng.choice(pos), rng.choice(neg)
        if a > b:
            w += 1
        elif abs(a - b) < 1e-12:
            t += 1
    return (w + 0.5 * t) / n


def _boot_ci(vals: List[float], rng: random.Random, n: int = 2000) -> Tuple[float, float]:
    if not vals:
        return float("nan"), float("nan")
    means = []
    L = len(vals)
    for _ in range(n):
        means.append(sum(vals[rng.randrange(L)] for _ in range(L)) / L)
    means.sort()
    return means[int(0.025 * (n - 1))], means[int(0.975 * (n - 1))]


def evaluate_distance(facts: List[Fact], rate: float, distance: str, k_min: int,
                      seed: int) -> Dict:
    rng = random.Random(seed)
    base = Graph(facts)
    new_facts, injected = inject_errors(facts, base, rate=rate, rng=rng, distance=distance)
    inj_set = set(injected)
    scorer = Scorer(new_facts, k_min=k_min)

    verdicts = {f.fid: scorer.score(f.s, f.g, f.fid) for f in new_facts}
    scored = [v for v in verdicts.values() if v.status == "SCORED"]
    inj_e = [verdicts[fid].energy for fid in injected if verdicts[fid].status == "SCORED"]
    non_e = [v.energy for v in scored if v.fid not in inj_set]

    coverage_all = len(scored) / len(new_facts)
    coverage_inj = len(inj_e) / len(injected) if injected else 0.0
    auc = _auc(inj_e, non_e, random.Random(seed + 1))

    # INFO-FREE GEOMETRY TWIN: rebuild the diffused geometry from a LABEL-SHUFFLED store (destroys the
    # real family structure) and re-score the SAME injections. If the AUC collapses toward 0.5, the
    # real graph-diffused geometry is load-bearing (not an artifact of degree/shape).
    twin_auc = float("nan")
    if scorer.geometry == "diffused":
        rng_s = random.Random(seed + 9)
        labels = [f.g for f in new_facts]
        rng_s.shuffle(labels)
        shuffled = [Fact(f.fid, f.s, labels[i], f.seg, f.patt, f.n_att, f.ctx)
                    for i, f in enumerate(new_facts)]
        twin_geo = DiffusedGeometry(shuffled, alpha=0.25)
        twin_scorer = Scorer(new_facts, k_min=k_min, geometry="diffused", diffused=twin_geo)
        tv = {f.fid: twin_scorer.score(f.s, f.g, f.fid) for f in new_facts}
        t_scored = [v for v in tv.values() if v.status == "SCORED"]
        t_inj = [tv[fid].energy for fid in injected if tv[fid].status == "SCORED"]
        t_non = [v.energy for v in t_scored if v.fid not in inj_set]
        twin_auc = _auc(t_inj, t_non, random.Random(seed + 10))

    # PAIRED within-subject: corrupted genus vs the subject's own ORIGINAL genera (same network)
    orig = defaultdict(list)
    for f in facts:
        orig[f.s].append(f.g)
    pair_wins: List[float] = []
    pair_conf: List[Tuple[float, float]] = []          # (confidence, win) for the confident-tier gate
    for fid in injected:
        v = verdicts[fid]
        if v.status != "SCORED":
            continue
        for gc in orig.get(v.s, []):
            vc = scorer.score(v.s, gc)
            if vc.status == "SCORED":
                win = 1.0 if v.energy > vc.energy else 0.0
                pair_wins.append(win)
                if v.confidence is not None:
                    pair_conf.append((v.confidence, win))
    paired = sum(pair_wins) / len(pair_wins) if pair_wins else float("nan")
    p_lo, p_hi = _boot_ci(pair_wins, random.Random(seed + 2))

    # CONFIDENT TIER: the top-half by schema-sharpness (coherence = Friston precision). The brain's
    # basic-level advantage -- verdicts on sharp-schema subjects are materially more reliable.
    paired_confident = float("nan")
    confident_keep = 0.0
    if pair_conf:
        cs = sorted(c for c, _ in pair_conf)
        thr = cs[len(cs) // 2]
        conf_wins = [w for c, w in pair_conf if c >= thr]
        paired_confident = sum(conf_wins) / len(conf_wins) if conf_wins else float("nan")
        confident_keep = len(conf_wins) / len(pair_conf)

    # OPERATIONAL RANK VIEW. A fixed absolute threshold is uninformative here: the store is already
    # noisy, so REAL inconsistent facts out-rank our planted far-errors in absolute energy (the organ
    # flagging real noise is a FEATURE, but it caps threshold-precision). We instead report where the
    # injected errors sit in the energy ranking: the median injected fact's PERCENTILE among all
    # scored facts, and recall in the top energy quantiles. High-energy facts above the injected set
    # are dominated by genuine store noise (hand-verifiable), not false positives.
    energies_sorted = sorted((v.energy for v in scored))
    def pct_below(x: float) -> float:
        lo = 0
        for e in energies_sorted:
            if e < x:
                lo += 1
            else:
                break
        return lo / len(energies_sorted) if energies_sorted else float("nan")
    inj_pctls = sorted(pct_below(e) for e in inj_e)
    inj_median_pctl = inj_pctls[len(inj_pctls) // 2] if inj_pctls else float("nan")
    n_scored = len(scored)
    top_ids = [v.fid for v in sorted(scored, key=lambda v: -v.energy)]
    def recall_at(frac: float) -> float:
        k = max(1, int(frac * n_scored))
        return len(set(top_ids[:k]) & inj_set) / len(injected) if injected else 0.0

    # floors on the paired test (can they pick the outlier?)
    fv = floor_ingest_vet(new_facts)
    ff = floor_frequency(new_facts, scorer.graph)
    def floor_paired(susp: Dict[int, float]) -> float:
        wins = []
        for fid in injected:
            nf = new_facts[fid]
            for of in [x for x in new_facts if x.s == nf.s and not x.injected]:
                wins.append(1.0 if susp[fid] > susp[of.fid] else (0.5 if susp[fid] == susp[of.fid] else 0.0))
        return sum(wins) / len(wins) if wins else float("nan")

    return {
        "distance": distance, "rate": rate,
        "n_facts": len(new_facts), "n_injected": len(injected),
        "coverage_all": round(coverage_all, 4), "coverage_injected": round(coverage_inj, 4),
        "auc_injected_vs_noninjected": round(auc, 4),
        "auc_geometry_shuffle_twin": round(twin_auc, 4) if twin_auc == twin_auc else None,
        "auc_beats_geometry_twin": (auc - twin_auc) > 0.1 if twin_auc == twin_auc else None,
        "paired_corrupted_gt_original": round(paired, 4),
        "paired_ci_lo": round(p_lo, 4), "paired_ci_hi": round(p_hi, 4),
        "paired_n": len(pair_wins),
        "paired_confident_tier": round(paired_confident, 4),
        "confident_tier_keep_frac": round(confident_keep, 4),
        "twin_paired": 0.5, "beats_twin_paired_ci": p_lo > 0.5,
        "energy_injected_mean": round(st.mean(inj_e), 4) if inj_e else None,
        "energy_noninjected_mean": round(st.mean(non_e), 4) if non_e else None,
        "injected_median_energy_percentile": round(inj_median_pctl, 4),
        "recall_at_top10pct": round(recall_at(0.10), 4),
        "recall_at_top25pct": round(recall_at(0.25), 4),
        "floor_ingestvet_paired": round(floor_paired(fv), 4),
        "floor_frequency_paired": round(floor_paired(ff), 4),
    }


def inject_matching_context(facts: List[Fact], graph: Graph, rate: float,
                            rng: random.Random) -> Tuple[List[Fact], List[int]]:
    """HARDEST adversary: the injected fact's CONTEXT is borrowed from a real term that IS the wrong
    genus, so its usage SUPPORTS the wrong label. Defeats the DISTRIBUTIONAL arm; only the
    context-immune RELATIONAL arm can catch it. Used to show which arm is adversary-robust."""
    genera = [g for g, m in graph.gen2subj.items() if len(m) >= 3]
    gmem: Dict[str, List[Fact]] = defaultdict(list)
    for f in facts:
        gmem[f.g].append(f)
    eligible = [f for f in facts if len(graph.subj2gen.get(f.s, set())) >= 2]
    rng.shuffle(eligible)
    n_inject = max(1, int(round(len(eligible) * rate)))
    new_facts = list(facts)
    injected_fids: List[int] = []
    for f in eligible[:n_inject]:
        cands = [g for g in genera if g != f.g and g not in graph.subj2gen.get(f.s, set())
                 and graph.compat(f.g, g) == 0.0]
        if not cands:
            continue
        g_wrong = rng.choice(cands)
        donors = [d for d in gmem.get(g_wrong, ()) if d.ctx]
        ctx = rng.choice(donors).ctx if donors else f.ctx     # borrow context that MATCHES g_wrong
        nf = Fact(fid=len(new_facts), s=f.s, g=g_wrong, seg=f.seg, patt="INJECTED",
                  n_att=1, ctx=ctx, injected=True)
        new_facts.append(nf)
        injected_fids.append(nf.fid)
    return new_facts, injected_fids


def _paired_by_arm(new_facts: List[Fact], injected: List[int], base_orig: Dict[str, List[str]],
                   arm: str) -> float:
    """Paired discrimination (corrupted > original) using a single arm: 'rel' | 'ctx' | 'mean' | 'max'."""
    sc = Scorer(new_facts, k_min=2)

    def energy(s: str, g: str) -> Optional[float]:
        er, ec = sc._rel_energy(s, g), sc._ctx_energy(s, g)
        zr = None if er is None else (er - sc._mr) / sc._sr
        zc = None if ec is None else (ec - sc._mc) / sc._sc
        vals = [z for z in (zr, zc) if z is not None]
        if not vals:
            return None
        if arm == "rel":
            return zr
        if arm == "ctx":
            return zc
        if arm == "max":
            return max(vals)
        return sum(vals) / len(vals)                            # mean

    wins = []
    for fid in injected:
        ew = energy(new_facts[fid].s, new_facts[fid].g)
        if ew is None:
            continue
        for gc in base_orig.get(new_facts[fid].s, []):
            ec = energy(new_facts[fid].s, gc)
            if ec is not None:
                wins.append(1.0 if ew > ec else 0.0)
    return sum(wins) / len(wins) if wins else float("nan")


def evaluate_arm_robustness(facts: List[Fact], rate: float, seed: int) -> Dict:
    """Per-arm paired discrimination under the STANDARD far injection vs the MATCHING-CONTEXT
    adversary. Shows the RELATIONAL arm is the adversary-robust core; the context arm is exploitable."""
    base = Graph(facts)
    orig: Dict[str, List[str]] = defaultdict(list)
    for f in facts:
        orig[f.s].append(f.g)
    std_facts, std_inj = inject_errors(facts, base, rate=rate, rng=random.Random(seed), distance="far")
    adv_facts, adv_inj = inject_matching_context(facts, base, rate=rate, rng=random.Random(seed))
    out = {}
    for arm in ("mean", "max", "rel", "ctx"):
        out[f"standard_{arm}"] = round(_paired_by_arm(std_facts, std_inj, orig, arm), 4)
        out[f"adversary_{arm}"] = round(_paired_by_arm(adv_facts, adv_inj, orig, arm), 4)
    return out


def high_confidence(facts: Sequence[Fact]) -> List[Fact]:
    """A CLEAN base: multi-attested OR biology-textbook COPULA/GLOSSARY facts. On this the
    non-injected negative class is genuinely clean, so the discrimination is not depressed by the
    store's OWN extraction noise -- isolating the mechanism from the foundation's quality."""
    kept = [f for f in facts if (f.n_att >= 2 or (f.seg == "bio_new" and f.patt in ("COPULA", "GLOSSARY_COLON")))]
    return [Fact(i, f.s, f.g, f.seg, f.patt, f.n_att, f.ctx) for i, f in enumerate(kept)]


def run(store_path: str, rate: float = 0.15, k_min: int = 2, seed: int = 0,
        smoke: bool = False) -> Dict:
    facts = load_facts(store_path)
    if smoke:
        facts = [Fact(i, f.s, f.g, f.seg, f.patt, f.n_att, f.ctx) for i, f in enumerate(facts[:500])]
    clean = high_confidence(facts)
    out = {"store": os.path.relpath(store_path, _REPO), "n_facts_base": len(facts),
           "n_facts_clean": len(clean), "k_min": k_min, "seed": seed}
    # FULL (noisy) store: the real operating point; NEGATIVE class contaminated with real noise.
    out["full_far"] = evaluate_distance(facts, rate, "far", k_min, seed)
    out["full_near"] = evaluate_distance(facts, rate, "near", k_min, seed)
    # CLEAN base: isolates the MECHANISM from the foundation's noise (the ceiling test).
    out["clean_far"] = evaluate_distance(clean, rate, "far", k_min, seed)
    out["clean_near"] = evaluate_distance(clean, rate, "near", k_min, seed)
    # ARM ROBUSTNESS: the relational arm is adversary-robust; the context arm is exploitable.
    out["arm_robustness_clean"] = evaluate_arm_robustness(clean, rate, seed)
    return out


# =========================================================================================
# 7. self-test (CAN-FAIL) + CLI
# =========================================================================================
def _self_test() -> None:
    fs = []
    for i in range(8):
        fs.append(Fact(len(fs), f"bioterm{i}", "process", ctx="cell enzyme reaction metabolism"))
        fs.append(Fact(len(fs), f"bioterm{i}", "molecule", ctx="cell enzyme reaction metabolism"))
    for i in range(8):
        fs.append(Fact(len(fs), f"geoterm{i}", "country", ctx="border capital population region"))
        fs.append(Fact(len(fs), f"geoterm{i}", "region", ctx="border capital population region"))
    sc = Scorer(fs, k_min=2)
    bad = sc.score("bioterm0", "country")     # cross-family -> high energy
    ok = sc.score("bioterm0", "molecule")     # within-family -> low energy
    assert bad.status == "SCORED" and ok.status == "SCORED", (bad, ok)
    assert bad.energy > ok.energy, (bad, ok)
    lone = Scorer(list(fs) + [Fact(999, "loner_xyz", "process")], k_min=2).score("loner_xyz", "process")
    assert lone.status == "INSUFFICIENT_SUPPORT", lone
    print("[self-test] PASS: cross-family energy > within-family; lonely fact abstains")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["full", "smoke"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--store", default=DEFAULT_STORE)
    ap.add_argument("--rate", type=float, default=0.15)
    ap.add_argument("--k-min", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return
    smoke = bool(args.smoke) or args.mode == "smoke"
    res = run(args.store, rate=args.rate, k_min=args.k_min, seed=args.seed, smoke=smoke)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
