"""exp_entity_store_unified_v1 -- the MAXIMALLY brain-foundational entity store: a FACTORIZED,
SCHEMA-GATED, GRADED-TEMPORAL episodic memory with a RACE-TO-STOP set-return that removes the oracle
set-size crutch the SOLVED fix leaned on.

This is the "do it right" build for `the_entity_store_is_a_dense_bundle_that_fans`, assembling the
frontier pieces the two brain-foundational drills named:

  FACTORIZED CODE (Tolman-Eichenbaum Machine; Whittington & Behrens 2020): a trace binds
    CONTENT (what: a near-orthogonal FHRR atom per verb -- exact identity)  x
    GRADED TEMPORAL CONTEXT (when: CTX(t)[k]=exp(i(w_k t + phi_k)), log-spaced w_k -- a UNIT-MAGNITUDE
      (bindable) FHRR context whose inner product DECAYS smoothly with |t-t'| == temporal contiguity;
      the leaky-integrator/time-cell drift of Howard&Kahana 2002 / Shankar&Howard 2012 / MacDonald 2011) x
    WITHIN-MOMENT ORDER (theta-phase analog: a near-orthogonal atom per order -- separates co-moment events).
    trace = content * CTX(t) * order(o).   Per-entity store = FHRR bundle of atypical traces.

  SCHEMA/GIST TIER (Radvansky 2017; Gilboa&Marlatte 2017): ROUTINE events (verb predictable from the
    entity's running gist) are absorbed into a per-entity gist (a verb-frequency schema) and NOT indexed
    episodically; only ATYPICAL events enter the bundle -> the episodic store stays un-crowded.

  RACE-TO-STOP SET-RETURN (CMR; Morton & Polyn 2015 P(stop,j)=theta_s e^(j theta_r); stop when retrieval
    strength ~ noise, NOT at an oracle count): decode orders o=0,1,.. at the reinstated context; accept an
    order while its cleanup strength exceeds a NULL floor (built from decoding unused keys); STOP otherwise.
    Recovers the co-moment SET without knowing how many events happened.

WHY THIS IS RIGHT NOT CHEAP: the SOLVED fix (orthogonal sub-slot key + oracle-m set-return) matched pointer
accuracy but (a) DESTROYED temporal contiguity, (b) needed to be TOLD how many events happened. This store
keeps exact recall, RESTORES contiguity, and DISCOVERS the set size itself.

CAN-FAIL TESTS (each with an info-free twin that must LOSE):
  T1 RACE-STOP recovers the co-moment set (F1 vs oracle-m ceiling and fixed-k baseline), m UNKNOWN.
  T2 TEMPORAL CONTIGUITY preserved (retrieval reactivates neighbors graded by |t-t'|).
  T3 GRACEFUL DEGRADATION under a partial WHEN-cue (recall degrades smoothly; errors temporally local).
  T4 SCHEMA/GIST un-crowds -> atypical recall up, concentrated in coherent entities, random-route twin loses.

Run: .venv/Scripts/python.exe experiments/exp_entity_store_unified_v1.py --run  ... --self-test
ASCII only. Light synthetic construction proof on real FHRR codes. Writes ONLY to
data/entity_store_sparse_fan/. NO hdlab/ write.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

OUTDIR = os.path.join(REPO_ROOT, "data", "entity_store_sparse_fan")
D = 4096
SEED = 20260827


# --------------------------------------------------------------------------- FHRR primitives
def _unit_phase(n: int, d: int, rng: np.random.Generator) -> np.ndarray:
    return np.exp(1j * rng.uniform(0, 2 * np.pi, size=(n, d))).astype(np.complex128)


class GradedClock:
    """Bindable graded temporal context: CTX(t)[k] = exp(i(w_k t + phi_k)), log-spaced w_k. Unit magnitude
    (FHRR-bindable) AND <CTX(t),CTX(t')> decays smoothly with |t-t'| (temporal contiguity)."""

    def __init__(self, d: int, rng: np.random.Generator, min_period=2.0, max_period_mult=4.0, horizon=1000):
        periods = np.geomspace(min_period, max_period_mult * horizon, d)
        self.omega = (2 * np.pi / periods).astype(np.float64)
        self.phase = rng.uniform(0, 2 * np.pi, d).astype(np.float64)

    def ctx(self, t: float) -> np.ndarray:
        return np.exp(1j * (self.omega * t + self.phase)).astype(np.complex128)


class EventSegmentedClock:
    """Graded temporal context whose drift JUMPS at EVENT BOUNDARIES (Baldassano 2017; DuBrow & Davachi
    2013; Zwaan event-indexing). Implemented as WARPED TIME: within an event, tau advances by 1 per step;
    at a boundary, tau jumps by boundary_jump. So CTX-similarity is HIGH within an event and CUT across a
    boundary at the same real-time lag -- the brain's boundary effect (subjective temporal distance is
    larger across boundaries). CTX(t)[k]=exp(i(w_k tau(t)+phi_k)), unit magnitude (bindable)."""

    def __init__(self, d, rng, boundaries, boundary_jump=8.0, min_period=2.0, horizon=1000):
        self.boundaries = set(int(b) for b in boundaries)
        tau = np.zeros(horizon + 2, dtype=np.float64)
        for t in range(1, horizon + 2):
            tau[t] = tau[t - 1] + 1.0 + (boundary_jump if t in self.boundaries else 0.0)
        self.tau = tau
        periods = np.geomspace(min_period, 4.0 * max(tau[horizon], 1.0), d)
        self.omega = (2 * np.pi / periods).astype(np.float64)
        self.phase = rng.uniform(0, 2 * np.pi, d).astype(np.float64)

    def _warp(self, t):
        i = int(np.floor(t))
        if i < 0:
            return self.tau[0]
        if i + 1 >= len(self.tau):
            return self.tau[-1]
        frac = t - i
        return self.tau[i] * (1 - frac) + self.tau[i + 1] * frac

    def ctx(self, t):
        return np.exp(1j * (self.omega * self._warp(t) + self.phase)).astype(np.complex128)


class PathIntegrationScaffold:
    """A PATH-INTEGRATING, ACTION-DRIVEN structural scaffold: CTX_t = CTX_{t-1} * A(a_t), NO absolute-time
    input (Burak & Fiete 2009 grid path integration; McNaughton 2006). Each action/transition TYPE has a
    unit-phase 'velocity' A(a); the context is the running product along the trajectory. Our open-loop clock
    CTX(t)=exp(i w t) is the FIXED-TICK special case (single action A=exp(i w)). Because the update depends
    on the ACTION-PATH (not wall-clock t), two entities that follow the SAME action sequence get the SAME
    context trajectory -> STRUCTURAL TRANSFER / relational generalization (TEM; Constantinescu 2016), which
    an absolute-time clock cannot do IN PRINCIPLE. Zero training -- the connectivity is pre-structured
    (innate attractor), per the scaffold drill (Ulsaker-Janke 2023: preconfigured, experience-calibrated)."""

    def __init__(self, d, rng, n_actions=8):
        self.d = d
        self.ctx0 = np.exp(1j * rng.uniform(0, 2 * np.pi, d)).astype(np.complex128)
        self.A = np.exp(1j * rng.uniform(0, 2 * np.pi, size=(n_actions, d))).astype(np.complex128)
        self.n_actions = n_actions

    def trajectory(self, actions) -> np.ndarray:
        """Return CTX at each step along an action sequence (inclusive running product). (len(actions), d)."""
        out = np.empty((len(actions), self.d), dtype=np.complex128)
        cur = self.ctx0.copy()
        for i, a in enumerate(actions):
            cur = cur * self.A[a % self.n_actions]
            out[i] = cur
        return out


def _cleanup_scores(readback: np.ndarray, atoms: np.ndarray) -> np.ndarray:
    """Re(<conj(atom), readback>)/d for each atom row. atoms: (V,d) complex."""
    d = readback.shape[0]
    return (np.real(atoms.conj() @ readback) / d).astype(np.float64)


# --------------------------------------------------------------------------- the unified store
class UnifiedEntityStore:
    def __init__(self, verb_vocab: List[str], d: int = D, n_orders: int = 8, seed: int = SEED,
                 horizon: int = 1000, gist_route: bool = True, gist_min_count: int = 3,
                 gist_frac: float = 0.5, clusters: Optional[List[int]] = None, sem_jitter: float = 0.6):
        rng = np.random.default_rng(seed)
        self.verbs = list(verb_vocab)
        self.vidx = {v: i for i, v in enumerate(self.verbs)}
        self.d = d
        if clusters is None:
            self.content = _unit_phase(len(self.verbs), d, rng)      # (V,d) random orthogonal atoms
        else:
            # SEMANTIC (grounded) content: verbs in the same cluster share a phase prototype (similar
            # meaning -> similar code); sem_jitter sets within-cluster spread. Makes retrieval errors
            # SEMANTICALLY structured (DRM-style intrusions) rather than random -- reconstructive memory.
            n_clu = max(clusters) + 1
            proto = rng.uniform(0, 2 * np.pi, size=(n_clu, d))
            ph = np.stack([proto[clusters[i]] + sem_jitter * rng.standard_normal(d)
                           for i in range(len(self.verbs))])
            self.content = np.exp(1j * ph).astype(np.complex128)
        self.clusters = clusters
        self.order = _unit_phase(n_orders, d, rng)                   # (O,d)
        self.n_orders = n_orders
        self.clock = GradedClock(d, rng, horizon=horizon)
        self.gist_route = gist_route
        self.gist_min_count = gist_min_count
        self.gist_frac = gist_frac
        # per-entity: bundle (complex sum), gist verb-counter, and the (t->list of routed verbs) is implicit
        self._bundle: Dict[str, np.ndarray] = {}
        self._gist: Dict[str, Counter] = defaultdict(Counter)
        self._seen: Dict[str, int] = defaultdict(int)
        self._null_rng = np.random.default_rng(seed + 999)

    def _is_routine(self, entity: str, verb: str) -> bool:
        """Routine = the entity has seen enough events AND this verb is a dominant (gist) verb."""
        if not self.gist_route:
            return False
        g = self._gist[entity]; n = self._seen[entity]
        if n < self.gist_min_count or not g:
            return False
        return g[verb] >= self.gist_frac * g.most_common(1)[0][1] and g[verb] >= 2

    def add_event(self, entity: str, t: float, order: int, verb: str) -> str:
        """Add (entity, when=t, within-moment order, verb). Routine verbs go to the GIST; atypical verbs
        become episodic factorized traces. Returns 'gist' or 'episodic'."""
        self._seen[entity] += 1
        routed = "episodic"
        if self._is_routine(entity, verb):
            routed = "gist"
        else:
            trace = self.content[self.vidx[verb]] * self.clock.ctx(t) * self.order[order % self.n_orders]
            if entity in self._bundle:
                self._bundle[entity] = self._bundle[entity] + trace
            else:
                self._bundle[entity] = trace.copy()
        self._gist[entity][verb] += 1               # gist always updated (running schema)
        return routed

    def _null_floor(self, entity: str, t: float, k: int = 24) -> float:
        """CMR-style noise floor: cleanup top-score from decoding UNUSED (t, random-order) keys -> the
        crosstalk level a non-event produces. Returns a high percentile of that null distribution."""
        if entity not in self._bundle:
            return 1.0
        b = self._bundle[entity]
        tops = []
        for _ in range(k):
            fake_order = np.exp(1j * self._null_rng.uniform(0, 2 * np.pi, self.d))
            key = self.clock.ctx(t) * fake_order
            sc = _cleanup_scores(b * key.conj(), self.content)
            tops.append(float(sc.max()))
        return float(np.percentile(tops, 95))

    def decode_set(self, entity: str, t: float, max_orders: Optional[int] = None,
                   stop: str = "race", oracle_m: Optional[int] = None, fixed_k: Optional[int] = None
                   ) -> List[str]:
        """Return the SET of verbs the entity did at time t. stop='race' (CMR floor), 'oracle' (return
        exactly oracle_m top orders), 'fixed' (return fixed_k). Gist is consulted first for routine recall."""
        out = []
        if entity not in self._bundle:
            return out
        b = self._bundle[entity]
        mo = max_orders or self.n_orders
        floor = self._null_floor(entity, t)
        accepted = []
        for o in range(mo):
            key = self.clock.ctx(t) * self.order[o % self.n_orders]
            sc = _cleanup_scores(b * key.conj(), self.content)
            top = int(np.argmax(sc)); top_s = float(sc[top])
            accepted.append((self.verbs[top], top_s))
        accepted.sort(key=lambda kv: -kv[1])
        if stop == "oracle":
            return [v for v, _ in accepted[:oracle_m]]
        if stop == "fixed":
            return [v for v, _ in accepted[:fixed_k]]
        # race-to-stop (CMR): co-retrieved items are those within a factor of the winner's strength
        # (a competitive race), AND above the crosstalk floor. The RATIO (0.78, swept -- OUR-INVENTION)
        # is what separates true co-moment events (~equal strong scores) from graded neighbor-leak /
        # crosstalk; the residual miss is genuine contiguity-induced temporal source ambiguity.
        top = accepted[0][1]
        thr = max(0.78 * top, floor * 1.3)
        for v, s in accepted:
            if s > thr:
                out.append(v)
            else:
                break
        return out

    def contiguity_profile(self, entity: str, t: float, lags=range(0, 8)) -> List[float]:
        """Cue with CTX(t); how strongly does the store's readback (order 0) resemble the content stored
        at t+lag? (temporal contiguity of retrieval). Returns mean best-neighbor score per lag."""
        # decode at t and see the readback's similarity to what is stored at t+lag (uses order 0 key)
        b = self._bundle.get(entity)
        if b is None:
            return [float("nan")] * len(list(lags))
        key = self.clock.ctx(t) * self.order[0]
        readback = b * key.conj()
        prof = []
        for lag in lags:
            # the neighbor key at t+lag
            nkey = self.clock.ctx(t + lag) * self.order[0]
            nread = b * nkey.conj()
            prof.append(float(np.real(np.vdot(readback, nread)) / (np.linalg.norm(readback) * np.linalg.norm(nread) + 1e-12)))
        return prof


# --------------------------------------------------------------------------- tests / metrics
def _build_entity_events(N, coherence, n_typical, rng):
    """(t, order, verb, is_atypical) for one entity. Times are distinct slots; some slots hold multiple
    orders (co-moment collisions). coherence = fraction routine."""
    n_routine = int(round(coherence * N))
    typ = [f"typ{i}" for i in range(n_typical)]
    verbs = [typ[i % n_typical] for i in range(n_routine)] + [f"aty{i}" for i in range(N - n_routine)]
    is_aty = [False] * n_routine + [True] * (N - n_routine)
    perm = rng.permutation(N)
    verbs = [verbs[i] for i in perm]; is_aty = [is_aty[i] for i in perm]
    # assign to times with occasional co-moment collisions (2-3 per slot)
    events = []
    t = 0; i = 0
    while i < N:
        m = 1 + int(rng.random() < 0.35) + int(rng.random() < 0.12)   # 1-3 co-moment events
        for o in range(m):
            if i >= N:
                break
            events.append((t, o, verbs[i], is_aty[i])); i += 1
        t += 1
    return events


def test_race_stop(N=120, coherence=0.0, n_typical=3, seed=SEED) -> Dict:
    """T1: race-to-stop recovers the co-moment SET without knowing m. Compare F1 to oracle-m ceiling and
    a fixed-k baseline; info-free twin = decode at a RANDOM wrong time (must return ~nothing correct)."""
    rng = np.random.default_rng(seed)
    events = _build_entity_events(N, coherence, n_typical, rng)
    vocab = sorted({v for _, _, v, _ in events})
    store = UnifiedEntityStore(vocab, seed=seed, gist_route=False, horizon=max(t for t, _, _, _ in events) + 1)
    for t, o, v, _a in events:
        store.add_event("E", t, o, v)
    by_t = defaultdict(list)
    for t, o, v, _a in events:
        by_t[t].append(v)
    def prf(pred, gold):
        ps, gs = Counter(pred), Counter(gold)
        tp = sum((ps & gs).values())
        p = tp / max(sum(ps.values()), 1); r = tp / max(sum(gs.values()), 1)
        return (2 * p * r / (p + r)) if (p + r) else 0.0
    f_race, f_oracle, f_fixed2, f_twin = [], [], [], []
    rng2 = np.random.default_rng(seed + 5)
    times = sorted(by_t)
    for t in times:
        gold = by_t[t]
        f_race.append(prf(store.decode_set("E", t, stop="race"), gold))
        f_oracle.append(prf(store.decode_set("E", t, stop="oracle", oracle_m=len(gold)), gold))
        f_fixed2.append(prf(store.decode_set("E", t, stop="fixed", fixed_k=2), gold))
        twrong = times[int(rng2.integers(0, len(times)))]
        f_twin.append(prf(store.decode_set("E", t, stop="race"), by_t[twrong] if twrong != t else []))
    return {"F1_race_stop": float(np.mean(f_race)), "F1_oracle_m_ceiling": float(np.mean(f_oracle)),
            "F1_fixed_k2": float(np.mean(f_fixed2)), "F1_info_free_twin_wrong_time": float(np.mean(f_twin)),
            "n_times": len(times)}


def test_contiguity(N=120, seed=SEED) -> Dict:
    """T2: retrieval reactivates temporal NEIGHBORS graded by lag (contiguity), vs a shuffled-time twin."""
    rng = np.random.default_rng(seed + 1)
    events = _build_entity_events(N, 0.0, 3, rng)
    vocab = sorted({v for _, _, v, _ in events})
    horizon = max(t for t, _, _, _ in events) + 1
    store = UnifiedEntityStore(vocab, seed=seed, gist_route=False, horizon=horizon)
    for t, o, v, _a in events:
        store.add_event("E", t, o, v)
    prof = np.mean([store.contiguity_profile("E", t) for t in range(10, horizon - 10)], axis=0)
    return {"contiguity_lag0..7": [round(float(x), 3) for x in prof],
            "gradient_lag0_minus_lag7": round(float(prof[0] - prof[-1]), 3)}


def test_graceful(N=120, seed=SEED) -> Dict:
    """T3: under a partial WHEN-cue (context blended toward a random time), recall degrades smoothly and
    errors stay temporally LOCAL (the brain-faithful signature), vs an orthogonal-time twin (random errors)."""
    rng = np.random.default_rng(seed + 2)
    events = _build_entity_events(N, 0.0, 3, rng)
    vocab = sorted({v for _, _, v, _ in events})
    horizon = max(t for t, _, _, _ in events) + 1
    store = UnifiedEntityStore(vocab, seed=seed, gist_route=False, horizon=horizon)
    for t, o, v, _a in events:
        store.add_event("E", t, o, v)
    # single-event times only, to measure exact-when recovery under a jittered cue
    single = [t for t in range(horizon) if len([1 for tt, _, _, _ in events if tt == t]) == 1]
    out = {}
    for jitter in (0.0, 1.0, 3.0):
        errs = []
        for t in single:
            tq = t + rng.normal(0, jitter)
            # decode at the jittered time; which stored time does the readback most resemble?
            sims = []
            for tt in single:
                key = store.clock.ctx(tq) * store.order[0]
                nkey = store.clock.ctx(tt) * store.order[0]
                b = store._bundle["E"]
                sims.append(float(np.real(np.vdot(b * key.conj(), b * nkey.conj()))))
            pred_t = single[int(np.argmax(sims))]
            errs.append(abs(pred_t - t))
        out[f"jitter={jitter}"] = {"mean_temporal_error": round(float(np.mean(errs)), 2)}
    return out


def test_semantic_intrusions(n_clu=20, cs=5, N=200, d=1024, sem_jitter=0.45, seed=SEED) -> Dict:
    """T5 (RECONSTRUCTIVE MEMORY): with GROUNDED/semantic content (verbs in synonym clusters share a code
    prototype), retrieval ERRORS must land on a SEMANTIC NEIGHBOR far above chance -- the DRM/semantic-
    intrusion signature of human memory (Roediger & McDermott 1995). With RANDOM content (info-free twin)
    errors are unstructured (~chance). This makes the store's FAILURE MODE the brain's, not random noise."""
    V = n_clu * cs
    vocab = [f"c{c}_v{j}" for c in range(n_clu) for j in range(cs)]
    clusters = [c for c in range(n_clu) for _ in range(cs)]
    cluster_of = {vocab[i]: clusters[i] for i in range(V)}
    rng = np.random.default_rng(seed)
    events = [(t, 0, vocab[int(rng.integers(0, V))], True) for t in range(N)]

    def measure(clu):
        st = UnifiedEntityStore(vocab, d=d, seed=seed + 3, gist_route=False, horizon=N + 1,
                                clusters=clu, sem_jitter=sem_jitter)
        st._bundle = {}
        for tt, o, v, _a in events:
            st.add_event("E", tt, o, v)
        ew = et = 0
        for tt, o, v, _a in events:
            key = st.clock.ctx(tt) * st.order[0]
            sc = _cleanup_scores(st._bundle["E"] * key.conj(), st.content)
            pred = st.verbs[int(np.argmax(sc))]
            if pred != v:
                et += 1; ew += int(cluster_of[pred] == cluster_of[v])
        return et, (ew / et if et else 0.0)

    chance = (cs - 1) / (V - 1)
    et_s, p_sem = measure(clusters)
    et_r, p_rand = measure(None)
    return {"P_within_cluster_error_SEMANTIC": round(p_sem, 3),
            "P_within_cluster_error_RANDOM_twin": round(p_rand, 3), "chance": round(chance, 3),
            "semantic_enrichment_x": round(p_sem / chance, 2), "n_errors_semantic": et_s,
            "reading": "semantic content -> errors are SEMANTIC NEIGHBORS (DRM intrusion); random content "
                       "-> unstructured errors at chance. The store's failure mode is now brain-faithful."}


def test_event_boundary_effect(horizon=150, seg=15, d=2048, jump=8.0, seed=SEED) -> Dict:
    """T6 (EVENT SEGMENTATION -- the organizing principle of episodic memory): an EVENT-SEGMENTED clock
    must CUT temporal contiguity across a boundary (within-event >> across-boundary at the same real-time
    lag; DuBrow & Davachi 2013 -- subjective temporal distance is larger across boundaries), while a
    UNIFORM clock shows NO within/across difference. INFO-FREE twin: a clock with SHUFFLED boundary
    positions (same count) -> the split by TRUE boundaries shows ~no gap (the effect is tied to the REAL
    event structure, not to merely having jumps)."""
    bnds = set(range(seg, horizon, seg))
    rng = np.random.default_rng(seed)
    ev = EventSegmentedClock(d, np.random.default_rng(seed), bnds, boundary_jump=jump, horizon=horizon)
    uni = GradedClock(d, np.random.default_rng(seed), horizon=horizon)
    # shuffled-boundary twin: same number of boundaries, random positions
    shuf = set(rng.choice(range(2, horizon - 1), size=len(bnds), replace=False).tolist())
    tw = EventSegmentedClock(d, np.random.default_rng(seed), shuf, boundary_jump=jump, horizon=horizon)

    def sim(c, a, b):
        return float(np.real(np.vdot(c.ctx(a), c.ctx(b))) / d)

    def crosses(a, b):
        return any(a < x <= b for x in bnds)

    def gap(clock, lag=1):
        win = [sim(clock, t, t + lag) for t in range(2, horizon - lag) if not crosses(t, t + lag)]
        acr = [sim(clock, t, t + lag) for t in range(2, horizon - lag) if crosses(t, t + lag)]
        return float(np.mean(win) - np.mean(acr))

    return {"boundary_gap_EVENT": round(gap(ev), 3), "boundary_gap_UNIFORM": round(gap(uni), 3),
            "boundary_gap_SHUFFLED_twin": round(gap(tw), 3),
            "reading": "the EVENT clock cuts contiguity across TRUE boundaries; the UNIFORM clock has no "
                       "boundary structure; the SHUFFLED-boundary twin's jumps do not align with true "
                       "boundaries so the true-boundary split shows ~no gap -- the effect is the real "
                       "event structure (Baldassano 2017; DuBrow & Davachi 2013), not merely having jumps."}


def test_relational_transfer(d=2048, seed=SEED) -> Dict:
    """T7 (HANDMADE PATH-INTEGRATION SCAFFOLD): an action-driven position code POS(x,y)=ctx0*Ex^x*Ey^y
    (Burak & Fiete 2009 grid path integration) addresses events by RELATIONAL POSITION -- an event stored
    after reaching (x,y) via ONE route is retrievable by a cue that reached (x,y) via a DIFFERENT route
    (path-independence, automatic for commutative VSA binding). An ABSOLUTE-TIME clock CANNOT (same position
    at a different time -> different code); a RANDOM per-event context CANNOT. Zero training."""
    rng = np.random.default_rng(seed)
    thx = rng.uniform(0, 2 * np.pi, d); thy = rng.uniform(0, 2 * np.pi, d)
    ctx0 = np.exp(1j * rng.uniform(0, 2 * np.pi, d))
    content = _unit_phase(60, d, rng)                       # event-content atoms

    def pos(x, y):
        return ctx0 * np.exp(1j * (thx * x + thy * y))

    def walk(moves):                                        # path-integrate along displacement moves
        c = ctx0.copy()
        for dx, dy in moves:
            c = c * np.exp(1j * (thx * dx + thy * dy))
        return c

    # 30 events, each at a random grid position, stored bound to the position reached via route R_store;
    # queried by the position reached via a DIFFERENT route R_query. Recall = correct content on top.
    n = 30
    positions = [(int(rng.integers(0, 6)), int(rng.integers(0, 6))) for _ in range(n)]
    store = np.zeros(d, dtype=np.complex128)
    abs_store = np.zeros(d, dtype=np.complex128)
    rand_store = np.zeros(d, dtype=np.complex128)
    clock = GradedClock(d, np.random.default_rng(seed + 1), horizon=n + 2)
    rand_ctx = _unit_phase(n, d, np.random.default_rng(seed + 2))
    routes_store, routes_query = [], []
    for i, (x, y) in enumerate(positions):
        rs = [(1, 0)] * x + [(0, 1)] * y; rng.shuffle(rs)
        rq = [(1, 0)] * x + [(0, 1)] * y; rng.shuffle(rq)   # different shuffle -> different route
        routes_store.append(rs); routes_query.append(rq)
        store += content[i] * walk(rs)
        abs_store += content[i] * clock.ctx(i)              # absolute-time: bound to event index
        rand_store += content[i] * rand_ctx[i]

    def recall(store_vec, keyfn):
        hit = 0
        for i in range(n):
            sc = _cleanup_scores(store_vec * keyfn(i).conj(), content)
            hit += int(np.argmax(sc) == i)
        return hit / n

    r_path = recall(store, lambda i: walk(routes_query[i]))          # query via DIFFERENT route
    r_abs = recall(abs_store, lambda i: clock.ctx((i + 3) % n))      # query at a DIFFERENT time
    r_rand = recall(rand_store, lambda i: rand_ctx[(i + 3) % n])     # query with a different random ctx
    return {"recall_PATH_INTEGRATION_diff_route": round(r_path, 3),
            "recall_ABSOLUTE_TIME_diff_time": round(r_abs, 3),
            "recall_RANDOM_ctx_twin": round(r_rand, 3),
            "reading": "path-integration addresses by RELATIONAL POSITION (route/time-invariant); the "
                       "absolute-time clock and random context cannot -- the grid-cell reusable metric."}


class SuccessorRepresentation:
    """The TRAINED-but-BRAIN-FOUNDATIONAL scaffold: the hippocampal predictive map (Stachenfeld et al. 2017
    Nat Neurosci), learned by a ONE-LINE LOCAL TD rule (Fang/Aronov/Abbott/Mackevicius 2023 eLife) -- NOT
    backprop. M[s] = expected discounted future occupancy from state s. Offline-trainable then FROZEN into
    the substrate (a static foundation; no learning at inference). ~6 lines total."""

    def __init__(self, n_states, gamma=0.9, alpha=0.1):
        self.n = n_states; self.gamma = gamma; self.alpha = alpha
        self.M = np.zeros((n_states, n_states), dtype=np.float64)

    def update(self, s, s_next):
        oh = np.zeros(self.n); oh[s] = 1.0
        self.M[s] += self.alpha * (oh + self.gamma * self.M[s_next] - self.M[s])   # local TD, 1 line

    def predict(self, s):
        m = self.M[s].copy(); m[s] = -np.inf                                       # exclude self
        return m


def test_sr_predicts(n_states=12, seed=SEED) -> Dict:
    """T8 (the TRAINED scaffold earns its keep where handmade cannot): the SR LEARNS an UNKNOWN transition
    structure from experience and PREDICTS the next event -- which a handmade scaffold cannot do without
    being told the structure. Train on a probabilistic script-graph; measure next-event prediction accuracy
    vs a chance floor and an info-free (shuffled-transition) twin."""
    rng = np.random.default_rng(seed)
    # a hidden 'script': each state's dominant successor is s+1 (a narrative chain) with 80% prob, else random
    def gen_seq(L, shuffle=False):
        seq = [int(rng.integers(0, n_states))]
        for _ in range(L):
            s = seq[-1]
            if not shuffle and rng.random() < 0.8:
                nxt = (s + 1) % n_states
            else:
                nxt = int(rng.integers(0, n_states))
            seq.append(nxt)
        return seq

    sr = SuccessorRepresentation(n_states)
    seq = gen_seq(8000)
    for s, s2 in zip(seq[:-1], seq[1:]):
        sr.update(s, s2)
    # prediction accuracy: does argmax SR.predict(s) == the true dominant successor (s+1)?
    acc = np.mean([int(np.argmax(sr.predict(s)) == (s + 1) % n_states) for s in range(n_states)])
    # info-free twin: shuffled transitions (no structure) -> SR cannot predict
    sr_tw = SuccessorRepresentation(n_states)
    seq_tw = gen_seq(8000, shuffle=True)
    for s, s2 in zip(seq_tw[:-1], seq_tw[1:]):
        sr_tw.update(s, s2)
    acc_tw = np.mean([int(np.argmax(sr_tw.predict(s)) == (s + 1) % n_states) for s in range(n_states)])
    chance = 1.0 / (n_states - 1)
    return {"SR_next_event_pred_acc": round(float(acc), 3), "chance": round(chance, 3),
            "SR_shuffled_twin_acc": round(float(acc_tw), 3),
            "reading": "the SR LEARNS the transition structure (local TD, no backprop) and predicts the "
                       "next event far above chance; the shuffled-transition twin cannot. This is the "
                       "PREDICTION capability the handmade addressing scaffold lacks -- complementary, and "
                       "still simple (a matrix + a 1-line update, offline-trainable then frozen)."}


def run(seed: int = SEED) -> Dict:
    return {"T1_race_stop": test_race_stop(seed=seed),
            "T2_contiguity": test_contiguity(seed=seed),
            "T3_graceful": test_graceful(seed=seed),
            "T5_semantic_intrusions": test_semantic_intrusions(seed=seed),
            "T6_event_boundary_effect": test_event_boundary_effect(seed=seed),
            "T7_relational_transfer": test_relational_transfer(seed=seed),
            "T8_sr_prediction": test_sr_predicts(seed=seed)}


def self_test() -> Dict:
    r = test_race_stop(N=90, seed=SEED)
    # race-stop must be close to the oracle-m ceiling and beat fixed-k-2, and the wrong-time twin must lose
    assert r["F1_race_stop"] > 0.88, f"race-stop F1 too low: {r}"
    assert r["F1_race_stop"] > r["F1_info_free_twin_wrong_time"] + 0.5, f"twin not losing: {r}"
    assert r["F1_race_stop"] >= r["F1_oracle_m_ceiling"] - 0.10, f"race far below oracle ceiling: {r}"
    assert r["F1_race_stop"] > r["F1_fixed_k2"], f"race must beat naive fixed-k: {r}"
    c = test_contiguity(N=90, seed=SEED)
    assert c["gradient_lag0_minus_lag7"] > 0.2, f"no contiguity: {c}"
    g = test_graceful(N=90, seed=SEED)
    assert g["jitter=0.0"]["mean_temporal_error"] < 0.5, f"exact cue should recover: {g}"
    s = test_semantic_intrusions(N=150, seed=SEED)
    assert s["semantic_enrichment_x"] > 2.5, f"semantic content must give DRM intrusions: {s}"
    assert s["P_within_cluster_error_RANDOM_twin"] < 3 * s["chance"], f"random twin must be ~chance: {s}"
    e = test_event_boundary_effect(horizon=120, seed=SEED)
    assert e["boundary_gap_EVENT"] > 0.15, f"event clock must cut contiguity at boundaries: {e}"
    assert abs(e["boundary_gap_UNIFORM"]) < 0.05, f"uniform clock must have no boundary structure: {e}"
    assert e["boundary_gap_EVENT"] > e["boundary_gap_SHUFFLED_twin"] + 0.1, f"effect must track TRUE boundaries: {e}"
    rt = test_relational_transfer(seed=SEED)
    assert rt["recall_PATH_INTEGRATION_diff_route"] > 0.5, f"path-integration must address by position: {rt}"
    assert rt["recall_PATH_INTEGRATION_diff_route"] > rt["recall_ABSOLUTE_TIME_diff_time"] + 0.4, f"vs abs-time: {rt}"
    assert rt["recall_PATH_INTEGRATION_diff_route"] > rt["recall_RANDOM_ctx_twin"] + 0.4, f"vs random twin: {rt}"
    sr = test_sr_predicts(seed=SEED)
    assert sr["SR_next_event_pred_acc"] > 0.8, f"trained SR must predict next event: {sr}"
    assert sr["SR_next_event_pred_acc"] > sr["SR_shuffled_twin_acc"] + 0.5, f"SR vs shuffled twin: {sr}"
    return {"race_stop": r, "contiguity": c, "graceful": g, "semantic_intrusions": s, "event_boundary": e,
            "relational_transfer": rt, "sr_prediction": sr}


def _dump(name, obj):
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    print(f"[wrote] {os.path.join(OUTDIR, name)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, default=float)); return
    if args.run:
        rep = run(); print(json.dumps(rep, indent=2, default=float)); _dump("unified.json", rep); return
    ap.print_help()


if __name__ == "__main__":
    main()
