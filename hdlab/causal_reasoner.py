"""hdlab/causal_reasoner.py -- a glass-box CAUSAL-NETWORK REASONER (multi-hop chains + counterfactual
necessity), the comprehension->REASONING pivot. Promoted VERBATIM (owner-DONE
reason_over_the_causal_network_multi_hop_chains_and_counterfactuals, Q111 strategy landing 2026-09-06)
from experiments/_causal_reasoner.py -- the CausalGraph / AdjacencyFloor / ChainItem class bodies are
UNCHANGED (byte-identical; the landing witness verification/test_causal_reasoner_landing.py asserts
inspect.getsource identity against the reference). Only this provenance paragraph is prepended to the
module header. Depends on stdlib only (numpy is imported LAZILY inside CausalGraph.shuffled()).

This is the FIRST inference organ over the situation model. It CONSUMES a causal network
(sm.causal_links / experiments._causal_network edges) and REASONS over it; it does NOT
re-extract or re-type links.

BRAIN GROUNDING (PINNED -- copy the COMPUTATION):
  * Trabasso & van den Broek 1985; Trabasso, van den Broek & Suh 1989; van den Broek 1990:
    a reader represents a narrative as a CAUSAL NETWORK and reasons over it. Events on the
    connected cause->consequence CHAIN are better recalled and judged more important; salience
    = network CONNECTIVITY (degree), NOT recency. Comprehension TRACES the chain:
      - ULTIMATE cause  = the root ancestor of an outcome (walk cause<-effect edges to a source).
      - MEDIATING cause = a node on the path between two events.
      - CHAIN OF CONSEQUENCE = forward reachability (descendants of an event).
  * Counterfactual necessity (Trabasso's own attribution account; Pearl SCM at the computational
    level; Kahneman & Miller norm theory; Khemlani & Johnson-Laird mental-model simulation):
    "would the outcome have occurred WITHOUT the cause?" is answered by a SIMULATED INTERVENTION
    -- remove/negate the node, re-propagate reachability along the edges, and read whether the
    outcome still holds. Necessity = removing the cause DISCONNECTS the outcome from its roots.

OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the mapping of a surface question onto a network
query (ultimate / mediating / chain / necessity); the intervention rule (remove-and-re-propagate
reachability vs negate-and-re-propagate SIGN); traversal-depth / abstention thresholds.

REUSE: this lifts the traversal pattern PROVEN in hdlab.goal_hierarchy_graph (ancestors / root /
connectivity + the shuffled-EDGE info-free twin) from the GOAL graph onto CAUSAL edges. The goal
graph's edges point child->parent (subgoal->superordinate); a causal edge points cause->effect, so
"ancestors of the outcome" = its causal predecessors and "root" = its ultimate cause -- the same
walk, one relation renamed. (The graphs differ in shape -- goal_hierarchy_graph is a single-parent
TREE, this is a multi-parent DAG -- so the walk is re-expressed as a multi-predecessor BFS rather
than reused call-for-call; the pattern is shared, the traversal primitive is not.) Glass-box,
stdlib-only, NO external LLM (the invariant).
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


# ---------------------------------------------------------------------------
# THE CAUSAL GRAPH (nodes = events; directed cause -> effect edges, optional polarity)
# ---------------------------------------------------------------------------
class CausalGraph:
    """A directed cause->effect graph the reasoner traverses. Edges may carry a POLARITY
    (+1 promote / -1 inhibit) for signed counterfactual propagation; unsigned graphs treat
    every edge as +1. Answers off the accumulated graph; never re-reads text."""

    def __init__(self):
        self.nodes: Set[str] = set()
        self.fwd: Dict[str, Dict[str, int]] = defaultdict(dict)   # cause -> {effect: polarity}
        self.bwd: Dict[str, Dict[str, int]] = defaultdict(dict)   # effect -> {cause: polarity}
        self.nec: Dict[Tuple[str, str], float] = {}              # (cause, effect) -> graded necessity in [0,1]
        self.abnormal: Set[str] = set()                          # Kahneman-Miller: mutable/abnormal/controllable nodes

    # ---- construction ---------------------------------------------------------
    def add_node(self, n: str) -> None:
        self.nodes.add(n)

    def add_edge(self, cause: str, effect: str, polarity: int = 1, necessity: float = 1.0) -> None:
        """necessity = graded causal-necessity weight of this edge (PINNED: Trabasso/van den Broek/Suh
        1989 weight edges by graded necessity; the discrete edge is a lossy read-out). Defaults to 1.0
        (a fully-necessary link) so unsigned/unweighted callers behave as boolean reachability."""
        if cause == effect:
            return
        self.nodes.add(cause)
        self.nodes.add(effect)
        self.fwd[cause][effect] = polarity
        self.bwd[effect][cause] = polarity
        self.nec[(cause, effect)] = float(necessity)

    def mark_abnormal(self, node: str) -> None:
        """Kahneman & Miller norm theory: flag a node as the abnormal/controllable/exceptional one --
        the antecedent a reader preferentially MUTATES in a counterfactual ('if only X hadn't...')."""
        self.abnormal.add(node)

    @classmethod
    def from_edges(cls, edges: Iterable[Sequence], nodes: Optional[Iterable[str]] = None) -> "CausalGraph":
        """edges = iterable of (cause, effect) or (cause, effect, polarity)."""
        g = cls()
        if nodes:
            for n in nodes:
                g.add_node(n)
        for e in edges:
            pol = int(e[2]) if len(e) >= 3 else 1
            nec = float(e[3]) if len(e) >= 4 else 1.0
            g.add_edge(e[0], e[1], pol, nec)
        return g

    def n_edges(self) -> int:
        return sum(len(d) for d in self.fwd.values())

    # ---- reachability (the load-bearing primitive) ----------------------------
    def descendants(self, start: str, blocked: Optional[Set[str]] = None) -> Set[str]:
        """CHAIN OF CONSEQUENCE: every node forward-reachable from `start` along cause->effect
        edges. `blocked` nodes are treated as REMOVED (the intervention primitive)."""
        blocked = blocked or set()
        if start in blocked:
            return set()
        seen: Set[str] = set()
        dq = deque([start])
        while dq:
            cur = dq.popleft()
            for nxt in self.fwd.get(cur, {}):
                if nxt in blocked or nxt in seen:
                    continue
                seen.add(nxt)
                dq.append(nxt)
        return seen

    def ancestors(self, node: str, blocked: Optional[Set[str]] = None) -> Set[str]:
        """Every node that can causally REACH `node` (its causal predecessors). `blocked`
        nodes are treated as removed."""
        blocked = blocked or set()
        if node in blocked:
            return set()
        seen: Set[str] = set()
        dq = deque([node])
        while dq:
            cur = dq.popleft()
            for prev in self.bwd.get(cur, {}):
                if prev in blocked or prev in seen:
                    continue
                seen.add(prev)
                dq.append(prev)
        return seen

    def reachable(self, a: str, b: str, blocked: Optional[Set[str]] = None) -> bool:
        """Is `b` forward-reachable from `a`? (b is a consequence of a.)"""
        if a == b:
            return a not in (blocked or set())
        return b in self.descendants(a, blocked=blocked)

    # ---- Trabasso salience: connectivity, not recency -------------------------
    def connectivity(self, node: str) -> int:
        """Number of causal connections (in-degree + out-degree) -- the PINNED Trabasso &
        van den Broek 1985 salience metric (recall + judged importance track degree)."""
        return len(self.bwd.get(node, {})) + len(self.fwd.get(node, {}))

    def roots_of(self, node: str, blocked: Optional[Set[str]] = None) -> List[str]:
        """The SOURCE ancestors of `node` (ancestors with no in-edge inside the graph) --
        the candidate ULTIMATE causes. Deterministic order (connectivity desc, then id)."""
        anc = self.ancestors(node, blocked=blocked)
        blocked = blocked or set()
        srcs = [a for a in anc if not [p for p in self.bwd.get(a, {}) if p not in blocked]]
        return sorted(srcs, key=lambda a: (-self.connectivity(a), a))

    # ---- READOUT 1: ULTIMATE CAUSE (root ancestor) ----------------------------
    def ultimate_cause(self, outcome: str) -> Optional[str]:
        """'What ULTIMATELY caused Z?' -- the root ancestor of `outcome`. If several roots reach
        it, the most causally-CONNECTED wins (Trabasso salience), ties broken deterministically.
        Returns None if the outcome has no causal antecedent (a source itself)."""
        srcs = self.roots_of(outcome)
        return srcs[0] if srcs else None

    def all_ultimate_causes(self, outcome: str) -> List[str]:
        return self.roots_of(outcome)

    # ---- READOUT 2: MEDIATING CAUSE (node on the path between two events) ------
    def mediators(self, cause: str, outcome: str) -> List[str]:
        """Nodes on SOME path cause->...->outcome (the mediating events). = descendants(cause)
        INTERSECT ancestors(outcome), excluding the endpoints. Connectivity-ranked."""
        if not self.reachable(cause, outcome):
            return []
        mids = (self.descendants(cause) & self.ancestors(outcome)) - {cause, outcome}
        return sorted(mids, key=lambda m: (-self.connectivity(m), m))

    def necessary_mediators(self, cause: str, outcome: str) -> List[str]:
        """Nodes on EVERY path cause->outcome (removing one disconnects them) -- the true
        bottleneck mediators (cut vertices of the cause->outcome flow)."""
        out = []
        for m in self.mediators(cause, outcome):
            if not self.reachable(cause, outcome, blocked={m}):
                out.append(m)
        return sorted(out, key=lambda m: (-self.connectivity(m), m))

    def mediating_cause(self, cause: str, outcome: str) -> Optional[str]:
        """The single most salient MEDIATING cause between two events (prefer a necessary
        mediator; else the most-connected mediator)."""
        nm = self.necessary_mediators(cause, outcome)
        if nm:
            return nm[0]
        m = self.mediators(cause, outcome)
        return m[0] if m else None

    # ---- READOUT 3: COUNTERFACTUAL NECESSITY (simulated intervention) ----------
    def is_necessary(self, cause: str, outcome: str) -> bool:
        """'If CAUSE had not happened, would OUTCOME still have happened?' -- answered by a
        SIMULATED INTERVENTION (Pearl / Trabasso / Kahneman-Miller): REMOVE the cause node,
        re-propagate reachability, and check whether the outcome is STILL reachable from the
        network's (remaining) roots. Necessary == removing the cause DISCONNECTS the outcome.

        Faithful to Trabasso's 'necessary in the circumstances': the outcome must currently be
        supported by the cause (reachable from it), and no BYPASS root-path may keep it up once
        the cause is gone."""
        if cause == outcome:
            return False
        if not self.reachable(cause, outcome):
            return False                       # cause does not even feed the outcome -> not necessary
        # SIMULATED INTERVENTION: remove the cause, then ask whether the outcome is still driven by
        # a REMAINING exogenous root. Necessity == removing the cause leaves the outcome with no
        # exogenous support (Trabasso 'necessary in the circumstances'; Pearl do(cause=absent)).
        blocked = {cause}
        remaining_roots = [n for n in self.nodes if n != cause and not self.bwd.get(n)]
        # if the cause WAS the only exogenous root, no remaining root drives the outcome -> supported
        # is False -> necessary. (No 'has-ancestors' fallback: orphaned ancestors are not support.)
        supported = any(self.reachable(r, outcome, blocked=blocked) for r in remaining_roots)
        return not supported

    def counterfactual_answer(self, cause: str, outcome: str) -> str:
        """Return 'necessary' (outcome would NOT have happened without cause) or
        'not_necessary' (outcome would still have happened -- a bypass exists)."""
        return "necessary" if self.is_necessary(cause, outcome) else "not_necessary"

    def is_actual_cause(self, cause: str, outcome: str) -> bool:
        """HALPERN-PEARL ACTUAL CAUSATION (the psychology of causal SELECTION -- what people judge a
        cause, Kahneman & Miller; Halpern & Pearl 2005). Simple but-for necessity (is_necessary) is
        too STRONG: under OVER-DETERMINATION (two rocks each shatter the bottle; two roots each drive
        the outcome) neither is but-for necessary, yet a reader judges EACH a cause. AC2: `cause` is
        an actual cause of `outcome` if there is a WITNESS CONTINGENCY (hold the over-determining
        alternative supports fixed at 'off') under which do(cause=absent) FLIPS the outcome.

        Operationally: `cause` is an actual cause iff it reaches the outcome AND either it is but-for
        necessary, OR removing the bypassing alternative roots (the minimal witness) makes it so."""
        if cause == outcome or not self.reachable(cause, outcome):
            return False
        if self.is_necessary(cause, outcome):
            return True                                       # a but-for cause is trivially actual
        roots = [n for n in self.nodes if not self.bwd.get(n)]
        # the over-determining alternatives = other roots that reach the outcome WITHOUT `cause`
        witness = {r for r in roots if r != cause and self.reachable(r, outcome, blocked={cause})}
        if not witness:
            return False
        # under the contingency (witness held off): does `cause` still reach, and does removing it flip?
        if not self.reachable(cause, outcome, blocked=witness):
            return False
        remaining = [r for r in roots if r != cause and r not in witness]
        still = any(self.reachable(r, outcome, blocked=witness | {cause}) for r in remaining)
        return not still

    # ---- READOUT 4: SIGNED counterfactual (more / less / no_effect) ------------
    def propagate_sign(self, perturbed: str, sign: int = 1,
                       blocked: Optional[Set[str]] = None) -> Dict[str, int]:
        """Propagate a signed perturbation from `perturbed` forward along the network. Each node
        inherits sign = (path sign product). When a node is reachable by paths of CONFLICTING
        sign the result is 0 (ambiguous/cancels). Returns {node: net_sign in {-1,0,+1}} over the
        forward cone. This is the SIGNED intervention (negate/boost a node, read the outcome)."""
        blocked = blocked or set()
        net: Dict[str, int] = {perturbed: sign}
        # topological-ish relaxation over the reachable cone (bounded iterations = |cone|)
        cone = {perturbed} | self.descendants(perturbed, blocked=blocked)
        for _ in range(len(cone) + 1):
            changed = False
            for u in list(cone):
                if u == perturbed or u in blocked:
                    continue
                incoming = [net[p] * pol for p, pol in self.bwd.get(u, {}).items()
                            if p in net and p not in blocked]
                if not incoming:
                    continue
                s = incoming[0] if all(x == incoming[0] for x in incoming) else 0
                if net.get(u) != s:
                    net[u] = s
                    changed = True
            if not changed:
                break
        return net

    def signed_effect(self, perturbed: str, outcome: str, sign: int = 1) -> str:
        """'Suppose PERTURBED (with this sign) happens -- how does OUTCOME change?' Signed
        forward propagation to the outcome: +1 -> 'more', -1 -> 'less', unreachable/0 ->
        'no_effect'. This is the WIQA-style counterfactual readout over the network."""
        if not self.reachable(perturbed, outcome):
            return "no_effect"
        net = self.propagate_sign(perturbed, sign=sign)
        s = net.get(outcome, 0)
        return "more" if s > 0 else ("less" if s < 0 else "no_effect")

    # ---- READOUT 5: GRADED NECESSITY (PINNED Trabasso/van den Broek/Suh 1989) --
    def graded_necessity(self, cause: str, outcome: str) -> float:
        """The graded causal necessity of `cause` for `outcome` = the STRONGEST causal path
        (max over paths of the product of edge necessities). 1.0 = a fully necessary chain; 0.0 =
        no path. The discrete is_necessary() boolean is a lossy read-out of this continuous weight
        (audit :1045-1046). Bellman-Ford-style relaxation over the reachable cone (products, so
        max-product = longest-in-log-space; DAG-safe, bounded by |cone| iterations)."""
        if cause == outcome:
            return 1.0
        if not self.reachable(cause, outcome):
            return 0.0
        cone = {cause} | (self.descendants(cause) & (self.ancestors(outcome) | {outcome}))
        best: Dict[str, float] = {cause: 1.0}
        for _ in range(len(cone) + 1):
            changed = False
            for u in list(cone):
                if u == cause:
                    continue
                cand = [best[p] * self.nec.get((p, u), 1.0)
                        for p in self.bwd.get(u, {}) if p in best]
                if not cand:
                    continue
                m = max(cand)
                if m > best.get(u, 0.0) + 1e-12:
                    best[u] = m
                    changed = True
            if not changed:
                break
        return best.get(outcome, 0.0)

    # ---- READOUT 6: GENERAL PEARL COUNTERFACTUAL (cut incoming, set value, compare) --
    def intervene_and_compare(self, node: str, outcome: str, cf_value: int = 0) -> Dict:
        """The FAITHFUL Pearl counterfactual (abduction->action->prediction; research drill
        2026-06-07:409-422 = rank-1 downdate + re-write = twin-network): SURGERY on `node` --
        cut its incoming determination and SET it to a counterfactual value -- then re-propagate
        and COMPARE the outcome against the factual world.

          cf_value = 0  -> 'if NODE had not happened' (remove: node absent, sign 0).
          cf_value = -1 -> negate NODE (Pearl twin: flip the node's sign, re-simulate).

        Returns {factual, counterfactual, changed, necessary}. `necessary` = the outcome's
        realized state CHANGES under the intervention (Trabasso 'necessary in the circumstances').
        This generalises is_necessary() from boolean reachability to a valued re-simulation."""
        roots = [n for n in self.nodes if not self.bwd.get(n)]
        # factual realized sign of the outcome under the actual roots (all +1 exogenous)
        fact = self._realize(outcome, root_signs={r: 1 for r in roots})
        if cf_value == 0:
            cf = self._realize(outcome, root_signs={r: 1 for r in roots}, blocked={node})
        else:
            forced = {node: int(cf_value)}
            cf = self._realize(outcome, root_signs={r: 1 for r in roots}, forced=forced)
        changed = (fact != cf)
        return {"factual": fact, "counterfactual": cf, "changed": changed, "necessary": changed}

    def _realize(self, outcome: str, root_signs: Dict[str, int],
                 blocked: Optional[Set[str]] = None, forced: Optional[Dict[str, int]] = None) -> int:
        """Forward-propagate signs from the exogenous roots to `outcome`. `blocked` = removed nodes;
        `forced` = nodes clamped to a counterfactual sign (do-surgery: their incoming is ignored).
        Conflicting incoming signs cancel to 0 (the 'no determinate effect' state)."""
        blocked = blocked or set()
        forced = forced or {}
        net: Dict[str, int] = {}
        for r, s in root_signs.items():
            if r not in blocked:
                net[r] = forced.get(r, s)
        for n, s in forced.items():
            if n not in blocked:
                net[n] = s
        order_nodes = self.nodes - blocked
        for _ in range(len(order_nodes) + 1):
            changed = False
            for u in order_nodes:
                if u in net and u in forced:
                    continue
                if u in root_signs and u not in forced:
                    continue
                incoming = [net[p] * pol for p, pol in self.bwd.get(u, {}).items()
                            if p in net and p not in blocked]
                if not incoming:
                    continue
                s = incoming[0] if all(x == incoming[0] for x in incoming) else 0
                if net.get(u) != s:
                    net[u] = s
                    changed = True
            if not changed:
                break
        return net.get(outcome, 0)

    # ---- Kahneman & Miller NORM THEORY: which node does a reader mutate? --------
    def most_mutable_cause(self, outcome: str) -> Optional[str]:
        """Norm theory (Kahneman & Miller 1986): a reader's counterfactual mutates the ABNORMAL /
        CONTROLLABLE / exceptional antecedent, not an arbitrary one. Among the outcome's causal
        ancestors, prefer an explicitly-marked abnormal node; else the most FOREGROUNDED one =
        highest causal connectivity (Hopper & Thompson high-transitivity foregrounding, audit
        :465-467). OUR-INVENTION (literature-grounded): the graph gives foregrounding = degree."""
        anc = self.ancestors(outcome)
        if not anc:
            return None
        marked = [a for a in anc if a in self.abnormal]
        pool = marked or list(anc)
        return sorted(pool, key=lambda a: (-self.connectivity(a), a))[0]

    # ---- INFO-FREE TWIN: shuffle the edges (same nodes + edge count) -----------
    def shuffled(self, seed: int) -> "CausalGraph":
        """The info-free twin: keep every node and the NUMBER of edges, but REWIRE each edge to a
        uniformly-random acyclic endpoint pair (same design as hdlab.goal_hierarchy_graph.
        shuffled_graph). Destroys the causal TOPOLOGY (which node is the root, what reaches what)
        while preserving node set + edge count -- so if the reasoner's answers came from the real
        structure, the twin must LOSE."""
        import numpy as np
        rng = np.random.default_rng(seed)
        nodes = sorted(self.nodes)
        m = self.n_edges()
        # preserve edge polarities as a multiset (shuffled onto random pairs)
        pols = [pol for d in self.fwd.values() for pol in d.values()]
        rng.shuffle(pols)
        T = CausalGraph()
        for n in nodes:
            T.add_node(n)
        assigned = 0
        guard = 0
        while assigned < m and guard < 50 * (m + 1):
            guard += 1
            a = nodes[int(rng.integers(0, len(nodes)))]
            b = nodes[int(rng.integers(0, len(nodes)))]
            if a == b or b in T.fwd.get(a, {}):
                continue
            # keep acyclic: no edge that would let b already reach a
            if a in T.descendants(b):
                continue
            T.add_edge(a, b, pols[assigned] if assigned < len(pols) else 1)
            assigned += 1
        return T


# ---------------------------------------------------------------------------
# ADJACENCY / MOST-RECENT FLOOR (the control that MUST LOSE on multi-hop)
# ---------------------------------------------------------------------------
class AdjacencyFloor:
    """The non-brain-faithful floor the bar requires: answer causal questions with the ONE-HOP
    neighbour, never tracing the chain. It is correct exactly when depth == 1 and WRONG whenever
    the ultimate cause / necessity depends on a longer chain -- that gap is what proves the
    multi-hop traversal is load-bearing (Trabasso's point: the true cause often is NOT the
    immediately-prior event)."""

    def __init__(self, g: CausalGraph):
        self.g = g

    def ultimate_cause(self, outcome: str) -> Optional[str]:
        """Most-recent floor: the IMMEDIATE predecessor (1 hop back), not the root."""
        preds = sorted(self.g.bwd.get(outcome, {}).keys(),
                       key=lambda p: (-self.g.connectivity(p), p))
        return preds[0] if preds else None

    def is_necessary(self, cause: str, outcome: str) -> bool:
        """1-hop necessity: call the cause 'necessary' iff it is a DIRECT predecessor of the
        outcome. Ignores multi-hop bypasses AND multi-hop support -> wrong off depth 1."""
        return cause in self.g.bwd.get(outcome, {})

    def signed_effect(self, perturbed: str, outcome: str, sign: int = 1) -> str:
        """1-hop signed floor: only a DIRECT edge perturbed->outcome transmits; else no_effect."""
        pol = self.g.fwd.get(perturbed, {}).get(outcome)
        if pol is None:
            return "no_effect"
        s = sign * pol
        return "more" if s > 0 else ("less" if s < 0 else "no_effect")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
@dataclass
class ChainItem:
    """One multi-hop / counterfactual gold instance over a causal network."""
    kind: str                 # ultimate | mediating | chain | necessity | signed
    edges: List[Tuple]        # the network (cause, effect[, polarity])
    query: Tuple              # (outcome,) or (cause, outcome) or (perturbed, outcome, sign)
    gold: object              # gold answer (node id / bool / label)
    meta: dict = field(default_factory=dict)
