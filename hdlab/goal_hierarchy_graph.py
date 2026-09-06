"""hdlab/goal_hierarchy_graph.py -- a glass-box GOAL->SUBGOAL HIERARCHY GRAPH for narrative plot comprehension.
Promoted VERBATIM (owner-DONE build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension,
Q111 strategy landing 2026-09-05) from experiments/goal_hierarchy_graph.py -- the experiment scaffolding
(the OMP env-setters + the __main__ smoke) is the only thing dropped; the GraphNode / GoalGraph /
build_goal_graph / readouts are unchanged. Depends only on stdlib + hdlab.goal_register.

Composes the LANDED flat per-agent GOAL REGISTER (hdlab.goal_register: explicit purpose/desire/intention
goals bound to the resolved agent + a status field) with the reader's CAUSAL NETWORK (sm.causal_links) into
an explicit goal->subgoal graph, so the reader can answer PLOT-STRUCTURE questions the FLAT register cannot:
  - the goal-why CHAIN over a distance ("why did X find the key?" -> "to unlock the door" -> "to escape"),
    where the flat register's why() returns only the IMMEDIATE purpose (one hop);
  - SUPERORDINATE reinstatement across intervening subgoals (return to the still-open overarching goal even
    when a more-recent sibling subgoal is active), where the flat wants() returns the most-recent-active goal.

BRAIN-FOUNDATIONAL (Trabasso & van den Broek 1985; Suh & Trabasso 1993; van den Broek 1988; story grammar
GPAO Trabasso-Secco-van den Broek 1984; Grosz & Sidner 1986 intentional structure):
- PINNED: narrative comprehension builds a CAUSAL/GOAL NETWORK. A superordinate goal MOTIVATES a subordinate
  goal/attempt (the motivation relation M); an event/outcome ENABLES a superordinate goal (enablement E).
- PINNED: a node's importance/salience = its CONNECTIVITY in the network (number of causal connections),
  NOT hierarchy depth and NOT recency (Trabasso & van den Broek 1985: recall probability + judged importance
  are both predicted by number of causal connections).
- PINNED: reinstatement returns to the still-open SUPERORDINATE goal after a subgoal completes, over a
  distance of intervening material (Suh & Trabasso 1993, four methodologies) -- NOT the most-recent goal.
- OUR-INVENTION-UNDER-TEST (swept, not adopted): the exact subgoal->superordinate LINKING rules
  (within-sentence recursive purpose nesting; the same-head chaining key; the same-agent open-goal stack for
  marker-less subgoals), the connectivity-salience tie-breaks, the reinstatement selection rule. The
  marker-less cross-sentence attachment is the Tier-2/inferential slice (the located-negative boundary).

Glass-box, rule-based, NO external LLM (the invariant). Proven in experiments/exp_goal_hierarchy_qa_v1.py.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from hdlab.goal_register import Goal, _lemma  # reuse the landed extractor's Goal + lemmatizer


# ---------------------------------------------------------------------------
# GRAPH DATA STRUCTURE
# ---------------------------------------------------------------------------
@dataclass
class GraphNode:
    """One predicate node in an agent's goal hierarchy: a stated goal, or an action/attempt that serves one."""
    key: str                    # canonical id: "<agent>::<head_lemma>"
    agent: str                  # canonical agent
    head: str                   # head predicate lemma (the goal/action)
    text: str                   # surface goal/action text
    kind: str                   # desire | intend | try | purpose_marked | purpose_bare | action
    sent_idx: int               # first mention sentence
    verb_tok: int = -1
    status: str = "active"      # active | satisfied | failed
    negated: bool = False


class GoalGraph:
    """An explicit goal->subgoal hierarchy over one passage's extracted goals + causal links.

    Edges point CHILD (subordinate action/subgoal) -> PARENT (superordinate goal). The motivation edge is
    the load-bearing structure the info-free twin SHUFFLES. Answers off the accumulated graph (never re-reads).
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.parent: Dict[str, Optional[str]] = {}            # child_key -> parent_key (motivation/enablement)
        self.children: Dict[str, List[str]] = defaultdict(list)
        self.edge_type: Dict[Tuple[str, str], str] = {}       # (child_key, parent_key) -> 'motivation'|'enablement'

    # ---- construction helpers -------------------------------------------------
    def _agent_of(self, g: Goal) -> str:
        return (g.agent_canonical or g.agent or "?").lower()

    def _node_key(self, agent: str, head: str) -> str:
        return f"{agent}::{_lemma(head)}"

    def _ensure_node(self, agent: str, head: str, text: str, kind: str, si: int, vt: int = -1) -> str:
        key = self._node_key(agent, head)
        if key not in self.nodes:
            self.nodes[key] = GraphNode(key=key, agent=agent, head=_lemma(head), text=text or head,
                                        kind=kind, sent_idx=si, verb_tok=vt)
            self.parent.setdefault(key, None)
        else:
            # keep the earliest mention; upgrade an 'action' node to a stated-goal kind if we learn it is one
            nd = self.nodes[key]
            if nd.kind == "action" and kind in ("desire", "intend", "try", "purpose_marked", "purpose_bare"):
                nd.kind = kind
            nd.sent_idx = min(nd.sent_idx, si)
        return key

    def _add_motivation(self, child_key: str, parent_key: str, etype: str = "motivation") -> None:
        if child_key == parent_key:
            return
        # do not create a cycle (a node cannot become the ancestor of its own ancestor)
        if self._is_ancestor(child_key, parent_key):
            return
        # a child keeps its FIRST-assigned superordinate (the tightest purpose); do not overwrite silently
        if self.parent.get(child_key):
            return
        self.parent[child_key] = parent_key
        self.children[parent_key].append(child_key)
        self.edge_type[(child_key, parent_key)] = etype

    def _is_ancestor(self, anc: str, node: str, _depth: int = 0) -> bool:
        if _depth > 64:
            return False
        p = self.parent.get(node)
        if p is None:
            return False
        if p == anc:
            return True
        return self._is_ancestor(anc, p, _depth + 1)

    # ---- readout: hierarchy navigation ---------------------------------------
    def ancestors(self, key: str) -> List[str]:
        """The chain of superordinate node keys from the immediate parent up to the root."""
        out, seen, cur = [], {key}, self.parent.get(key)
        while cur is not None and cur not in seen:
            out.append(cur)
            seen.add(cur)
            cur = self.parent.get(cur)
        return out

    def root(self, key: str) -> str:
        anc = self.ancestors(key)
        return anc[-1] if anc else key

    def why_chain(self, agent: str, action_head: str) -> List[str]:
        """The goal-why CHAIN behind an action: [immediate purpose, ..., root superordinate] as head lemmas.
        Empty if the action is not in the agent's hierarchy or has no superordinate. This is the multi-hop
        readout the flat register (immediate-purpose-only) cannot produce."""
        key = self._node_key((agent or "").lower(), action_head)
        return [self.nodes[a].head for a in self.ancestors(key) if a in self.nodes]

    def superordinate(self, agent: str, action_head: str) -> Optional[str]:
        """The ROOT (overarching) goal an action ultimately serves -- 'why did X do this, ultimately?'."""
        chain = self.why_chain(agent, action_head)
        return chain[-1] if chain else None

    def parent_head(self, agent: str, action_head: str) -> Optional[str]:
        """The IMMEDIATE superordinate goal of an action (one hop -- the flat register's granularity)."""
        chain = self.why_chain(agent, action_head)
        return chain[0] if chain else None

    def subgoals(self, agent: str, goal_head: str) -> List[str]:
        key = self._node_key((agent or "").lower(), goal_head)
        return [self.nodes[c].head for c in self.children.get(key, []) if c in self.nodes]

    # ---- readout: connectivity salience (PINNED Trabasso & van den Broek 1985) -----------------
    def connectivity(self, key: str) -> int:
        """Number of causal connections a node has = out-degree (children) + in-degree (has a parent).
        The PINNED salience metric -- importance is degree in the network, not depth or recency."""
        return len(self.children.get(key, [])) + (1 if self.parent.get(key) else 0)

    def most_connected(self, agent: str) -> Optional[str]:
        """The most-connected (most salient) goal for an agent -- the superordinate with the most subgoals.
        Trabasso & van den Broek 1985: the most-connected node is the most important/recalled. Ties are broken
        by head lexicographically (gold-NEUTRAL: it does not favour the earliest-mentioned/root node, so the
        info-free twin cannot win ties by position). A real superordinate wins on strict connectivity."""
        cand = [k for k, nd in self.nodes.items() if nd.agent == (agent or "").lower()]
        if not cand:
            return None
        best = max(cand, key=lambda k: (self.connectivity(k), self.nodes[k].head))
        return self.nodes[best].head

    # ---- readout: reinstatement over a distance (PINNED Suh & Trabasso 1993) --------------------
    def open_superordinate(self, agent: str) -> Optional[str]:
        """Reinstatement: the still-OPEN (active, non-negated) SUPERORDINATE goal -- the root-most active
        ancestor -- even across intervening (satisfied) subgoals or a more-recent active sibling subgoal.
        This is what the reader returns to after a subgoal completes; a status-blind recency floor (the flat
        wants()) returns the most-recent active node, which may be a sibling subgoal or a subordinate."""
        ag = (agent or "").lower()
        active = [k for k, nd in self.nodes.items()
                  if nd.agent == ag and nd.status == "active" and not nd.negated]
        if not active:
            return None
        # the open superordinate = an active node with NO still-open ancestor (i.e. it IS the top of an
        # open branch). Among those, prefer the most-connected (Trabasso salience), then the earliest.
        def open_ancestor(k):
            return any(self.nodes.get(a) and self.nodes[a].status == "active" and not self.nodes[a].negated
                       for a in self.ancestors(k))
        tops = [k for k in active if not open_ancestor(k)]
        pool = tops or active
        # gold-NEUTRAL tiebreak (head lexicographic), so the info-free twin cannot win ties by position
        best = max(pool, key=lambda k: (self.connectivity(k), self.nodes[k].head))
        return self.nodes[best].head

    def agents(self) -> List[str]:
        return sorted({nd.agent for nd in self.nodes.values() if nd.agent and nd.agent != "?"})


# ---------------------------------------------------------------------------
# GRAPH CONSTRUCTION from the flat register's goals + the causal network
# ---------------------------------------------------------------------------
def build_goal_graph(goals: List[Goal], causal_links=None, events=None,
                     link_open_stack: bool = False, sents=None) -> GoalGraph:
    """Build the goal->subgoal graph over the reader's OWN extracted goals.

    MOTIVATION edges (PINNED relation; structural for explicit purpose):
      - a purpose goal g ("agent does ACTION in order to PURPOSE") makes node(ACTION) a subgoal of
        node(PURPOSE): parent(ACTION) = PURPOSE. Chaining across sentences is automatic via the shared
        node key -- if a later goal makes PURPOSE itself an ACTION of a higher purpose, the chain extends.
      - a desire/intend/try goal ("agent wants/tries to HEAD") registers HEAD as a stated goal node (a root
        candidate); no action node (the matrix verb is only the desire marker).
    ENABLEMENT edges (PINNED relation; from the reader's causal network, optional):
      - a causal link cause->outcome whose outcome matches a goal head marks the cause as enabling that goal.
    OUR-INVENTION-UNDER-TEST (default OFF; the Tier-2 inferential slice -- the located-negative boundary):
      - link_open_stack: attach a marker-less same-agent action to the most-recent still-open dominating
        goal (Grosz-Sidner focus stack). Structural APPROXIMATION -- needs planning inference to be reliable.
    """
    G = GoalGraph()
    # 1) create nodes + within/cross-sentence purpose motivation edges (keyed on head lemma -> auto-chains)
    for g in goals:
        ag = (g.agent_canonical or g.agent or "?").lower()
        if g.kind in ("purpose_marked", "purpose_bare"):
            # ACTION (matrix verb, source_verb) is the subgoal; PURPOSE (goal_head) is the superordinate
            action_key = G._ensure_node(ag, g.source_verb, g.source_verb, "action", g.sent_idx, g.verb_tok)
            purpose_key = G._ensure_node(ag, g.goal_head, g.goal_text, g.kind, g.sent_idx, g.to_tok)
            if g.negated:
                G.nodes[action_key].negated = True
            G._add_motivation(action_key, purpose_key, "motivation")
        else:  # desire | intend | try -> a stated goal (root candidate)
            gk = G._ensure_node(ag, g.goal_head, g.goal_text, g.kind, g.sent_idx, g.to_tok)
            if g.negated:
                G.nodes[gk].negated = True

    # 2) status per node from the extracted goals (track_status already ran on the flat register) + events
    _apply_status(G, goals, events)

    # 3) enablement edges from the causal network (optional, additive)
    if causal_links:
        _add_enablement(G, causal_links)

    # 4) OUR-INVENTION Tier-2 open-stack attachment (default off; measured as the located-negative slice)
    if link_open_stack:
        _link_open_stack(G, goals, sents=sents)
    return G


def _apply_status(G: GoalGraph, goals: List[Goal], events) -> None:
    """Set node.status. Prefer the flat register's per-goal status (goal_head match); for a bare ACTION node
    with no matching goal, satisfied iff a later same-agent event realizes it (glass-box, same rule as
    hdlab.goal_register.track_status)."""
    by_head: Dict[str, str] = {}
    neg: Dict[str, bool] = {}
    for g in goals:
        ag = (g.agent_canonical or g.agent or "?").lower()
        by_head[f"{ag}::{_lemma(g.goal_head)}"] = g.status
        if g.negated:
            neg[f"{ag}::{_lemma(g.goal_head)}"] = True
    ev = []
    if events:
        for e in events:
            ev.append((getattr(e, "sent_idx", 0), _lemma(str(getattr(e, "predicate", ""))),
                       str(getattr(e, "agent", "") or "").lower()))
    for key, nd in G.nodes.items():
        if key in by_head:
            nd.status = by_head[key]
        elif ev:
            realized = any(si > nd.sent_idx and pl == nd.head and (ea == nd.agent or nd.agent in ("?", ""))
                           for (si, pl, ea) in ev)
            nd.status = "satisfied" if realized else "active"
        if neg.get(key):
            nd.negated = True
            nd.status = "failed"


def _add_enablement(G: GoalGraph, causal_links) -> None:
    """A causal (connective/bridge) link cause->outcome whose outcome lemma is a goal head marks the cause
    as ENABLING that goal (event-to-goal enablement, Trabasso relation E). Additive to motivation edges."""
    head_nodes = defaultdict(list)
    for key, nd in G.nodes.items():
        head_nodes[nd.head].append(key)
    for cl in causal_links:
        out_l = _lemma(str(getattr(cl, "outcome", "")))
        cau_l = _lemma(str(getattr(cl, "cause", "")))
        for gkey in head_nodes.get(out_l, []):
            ag = G.nodes[gkey].agent
            ck = G._ensure_node(ag, cau_l, cau_l, "action", getattr(cl, "sent_idx", 0))
            G._add_motivation(ck, gkey, "enablement")


# CONTEXTUAL inverse-planning edge (owner-DONE validate_the_ppmi_svd_means_end_bridge...): a marker-less action
# is attached to the OPEN goal most RELATED to the action's SITUATION (Baker/Jara-Ettinger inverse planning
# conditioned on state; the ATL associative relatedness hub) -- NOT recency (the recency floor is a LOCATED
# NEGATIVE: it sits inside the info-free shuffled-situation twin band; the situation-relatedness mechanism beats
# it CI-sep on modern gold, K1 0.700 vs twin p95 0.483). Lazy singleton associative store (glass-box, NO LLM).
_ASSOC = None


def _assoc():
    global _ASSOC
    if _ASSOC is None:
        import os
        import numpy as np
        _repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        d = np.load(os.path.join(_repo, "data/frontend_assets/associative_similarity_store_v1.npz"), allow_pickle=True)
        W = d["words"]; V = d["vecs"].astype(np.float32)
        V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
        _ASSOC = (V, {str(w).lower(): i for i, w in enumerate(W)})
    return _ASSOC


def _situation_relatedness(sit_words, goal_head, topk=5):
    """Top-k mean cosine between the situation's content words and the goal head, in the associative store."""
    V, w2i = _assoc()
    gi = w2i.get((goal_head or "").lower())
    if gi is None:
        return None
    gv = V[gi]
    sims = [float(V[w2i[w]] @ gv) for w in {s.lower() for s in sit_words} if w in w2i]
    if not sims:
        return None
    sims.sort(reverse=True)
    return sum(sims[:topk]) / min(topk, len(sims))


def _link_open_stack(G: GoalGraph, goals: List[Goal], sents=None, margin: float = 0.02) -> None:
    """Attach a marker-less action node that has no parent to a still-open dominating GOAL node of the same
    agent introduced before it. CONTEXTUAL when `sents` is provided: pick the OPEN goal whose head is most
    RELATED to the action's SITUATION (the sentence's content words) in the associative store, gated by a
    top-1 margin (inverse planning conditioned on state). Recency fallback (the located-negative floor) when
    no relatedness signal / no sents. Additive: only fills previously-parentless action nodes."""
    stated = defaultdict(list)  # agent -> [(sent_idx, key)] of desire/intend/try/purpose goal nodes
    for key, nd in G.nodes.items():
        if nd.kind in ("desire", "intend", "try", "purpose_marked", "purpose_bare"):
            stated[nd.agent].append((nd.sent_idx, key))
    for ag in stated:
        stated[ag].sort()
    for key, nd in list(G.nodes.items()):
        if nd.kind != "action" or G.parent.get(key):
            continue
        cands = [k for (si, k) in stated.get(nd.agent, []) if si <= nd.sent_idx and k != key]
        if not cands:
            continue
        chosen = cands[-1]                       # recency floor (fallback)
        if sents is not None and 0 <= nd.sent_idx < len(sents):
            sit = [w for w in sents[nd.sent_idx] if isinstance(w, str) and w.isalpha()]
            scored = []
            for k in cands:
                r = _situation_relatedness(sit, G.nodes[k].head)
                if r is not None:
                    scored.append((r, k))
            if scored:
                scored.sort(reverse=True)
                if len(scored) == 1 or (scored[0][0] - scored[1][0]) >= margin:
                    chosen = scored[0][1]        # CONTEXTUAL: the most situation-related open goal
        G._add_motivation(key, chosen, "motivation")


# ---------------------------------------------------------------------------
# INFO-FREE TWIN: shuffle the parent (motivation) edges -- same nodes, permuted structure.
# ---------------------------------------------------------------------------
def shuffled_graph(G: GoalGraph, seed: int) -> GoalGraph:
    """The info-free twin (SHUFFLED EDGES): keep every node + status + the NUMBER of motivation edges, but
    REWIRE each edge to a uniformly-random parent node. This destroys the hierarchy TOPOLOGY (which node is
    the root, which superordinate has the subgoals) while preserving the node set, status, and edge count --
    so if the graph's answers came from the real structure, the twin must LOSE. (Merely permuting endpoints
    is a no-op when many edges share a parent or a single sink is the unique root; drawing parents from the
    full node set is the faithful info-free control.)"""
    import numpy as np
    rng = np.random.default_rng(seed)
    T = GoalGraph()
    T.nodes = {k: GraphNode(**vars(nd)) for k, nd in G.nodes.items()}
    for c in T.nodes:
        T.parent.setdefault(c, None)
    keys = list(T.nodes.keys())
    n_edges = sum(1 for p in G.parent.values() if p is not None)
    # randomize WHICH nodes are children (so any node -- not just the original root -- can end up parentless):
    # pick n_edges distinct children in random order, each assigned a uniformly-random acyclic parent.
    order = list(keys)
    rng.shuffle(order)
    assigned = 0
    for c in order:
        if assigned >= n_edges:
            break
        for _ in range(12):
            p = keys[int(rng.integers(0, len(keys)))]
            if p != c and not T._is_ancestor(c, p) and not T._is_ancestor(p, c):
                T.parent[c] = p
                T.children[p].append(c)
                T.edge_type[(c, p)] = "motivation"
                assigned += 1
                break
    return T
