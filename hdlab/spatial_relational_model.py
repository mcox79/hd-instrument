"""hdlab/spatial_relational_model.py -- a glass-box RELATIONAL SPATIAL MODEL + reasoner (the SPACE reasoning
layer over the extracted locations), the comprehension->SPATIAL-REASONING inference organ. Promoted
BYTE-FAITHFUL (owner-DONE reason_over_the_spatial_relational_model_containment_position_path_modern_gold,
Q111 strategy landing 2026-09-06) from experiments/spatial_relational_model.py -- the SpatialModel /
norm_rel / canon_entity bodies are UNCHANGED (byte-identical; the landing witness
verification/test_spatial_relational_landing.py asserts inspect.getsource identity against the reference).
Only this provenance paragraph is prepended to the module header. Depends on stdlib + the already-promoted
hdlab.location_register ONLY (NO experiments import, NO numpy at import; numpy is used only if a caller
passes an rng into shuffled_twin).

This is the SPACE-channel sibling of hdlab.causal_reasoner: a read()-time QUERY API that REASONS over the
reader's OWN location tracking (sm.locations, the hdlab.location_register.LocationRegister) -- it does NOT
modify the tracking core and emits no events. Three inference families, none settled by a single location
fact: CONTAINMENT (transitive region-nesting), RELATIVE POSITION (Franklin-Tversky framework closure +
converse + nested-frame inheritance), and PATH/TRANSFER (Goal-over-Source with the vacate-Source 'no longer'
read). Glass-box, NO external LLM at inference (the invariant).

The ORIGINAL module docstring follows.

---------------------------------------------------------------------------
GLASS-BOX RELATIONAL SPATIAL MODEL + reasoner -- the SPACE reasoning layer over the extracted locations.

The location register (hdlab.location_register.LocationRegister) tracks per-entity location STATE but its only
relational move is a two-level INDOORS/OUTDOORS containment. This module EXTENDS it to a small updatable
relational graph and REASONS by composing it -- answering questions no single location fact settles.

BRAIN FRAME (opening move; PINNED unless marked):
  * A reader represents a described scene as a small RELATIONAL model and reasons by INSPECTING it, not by
    formal rules (Johnson-Laird 1983 mental models; Byrne & Johnson-Laird 1989: build a preferred model from
    the premises, read the conclusion off it). PINNED.
  * CONTAINMENT is region-nesting and TRANSITIVE (the cognitive map is nested REGIONS -- Wiener & Mallot 2003;
    Peer & Epstein 2025; hippocampal relational/transitive inference -- Dusek & Eichenbaum 1997). So
    "key in box" + "box in drawer" |= "key in drawer". PINNED. -> transitive closure over containment edges.
  * RELATIVE POSITION is read off a spatial FRAMEWORK of reference axes (Franklin & Tversky 1990; Bryant,
    Tversky & Franklin 1992): above/below most accessible, then front/back, then left/right; reference-frame
    dependent; each relation has an INVERSE. PINNED. -> per-axis transitive closure + converse(inverse).
  * PATH/TRANSFER updates the model to the GOAL and VACATES the Source (Talmy 1985 path-in-the-satellite;
    Goal-over-Source, Lakusta & Landau 2005): "moved from K into G" |= "in G" AND "NOT in K". PINNED. -> reuse
    the LocationRegister (it already folds moves to a per-entity node track); the vacate-Source "no longer"
    inference is read off it.
  * Categorical/topological, NOT metric Euclidean coords for narrative space (Rinck 1997 rules out metric). PINNED.

  OUR-INVENTION-UNDER-TEST (sweep, do not adopt): the READOUT (question -> query type); the model-CONSTRUCTION
  rule (text spatial relations -> graph edges); the COMPOSITION rule (closure DEPTH, axis granularity, the
  abstention threshold). All swept in the experiment cells, never hard-set from a constraint we do not share.

Glass-box, ASCII only, NO external LLM, torch-free (numpy only in the cells). Pure library: writes nothing.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Optional, Sequence, Set, Tuple

# reuse the promoted tracking core for the PATH/TRANSFER spine (Q111: we do not modify it, we compose it)
from hdlab.location_register import LocationRegister, DEICTIC_SCENE, AWAY

# ---------------------------------------------------------------------------
# relation vocabulary (Franklin & Tversky spatial framework axes + inverses)
# ---------------------------------------------------------------------------
# each projective relation -> (axis, canonical positive relation P, sign): an edge (A rel B) with sign +1 means
# "A is P-of B"; sign -1 means "A is inv(P)-of B" (stored as B P A). Accessibility order (vertical>depth>horiz)
# is used only to break ties in readout, per Franklin-Tversky; it never changes an entailment.
AXIS_OF: Dict[str, Tuple[str, str, int]] = {
    "above": ("v", "above", +1), "over": ("v", "above", +1), "top": ("v", "above", +1),
    "below": ("v", "above", -1), "under": ("v", "above", -1), "underneath": ("v", "above", -1),
    "beneath": ("v", "above", -1), "bottom": ("v", "above", -1),
    "front": ("d", "front", +1), "ahead": ("d", "front", +1),
    "behind": ("d", "front", -1), "back": ("d", "front", -1),
    "left": ("h", "left", +1),
    "right": ("h", "left", -1),
    "east": ("g", "east", +1), "west": ("g", "east", -1),
    "north": ("n", "north", +1), "south": ("n", "north", -1),
}
SYMMETRIC = {"near", "far", "touching", "beside", "next"}     # proximity/adjacency: symmetric, NOT transitive
_ACCESS = {"v": 3, "d": 2, "n": 1, "g": 1, "h": 0}            # Franklin-Tversky accessibility (readout tie-break)

# containment relTypes (ISO-Space QSLINK RCC8): trajector is INSIDE landmark
CONTAIN_RELTYPES = {"IN", "NTPP", "TPP", "TPPI_INV", "INSIDE"}   # proper/tangential parthood + IN


def norm_rel(word: str) -> Optional[str]:
    """Map a surface relation word/phrase to a canonical relation token, or None if not spatial-projective."""
    w = word.lower().strip()
    w = w.replace("in front of", "front").replace("in back of", "behind").replace("next to", "near")
    w = w.replace("close to", "near").replace("far from", "far").replace("to the left of", "left")
    w = w.replace("to the right of", "right").replace("on top of", "above")
    for tok in w.split():
        if tok in AXIS_OF or tok in SYMMETRIC:
            return tok
    if w in AXIS_OF or w in SYMMETRIC:
        return w
    return None


def canon_entity(s: str) -> str:
    """Canonicalize an entity/place surface span to a node key: lowercase, strip articles/possessives/punct.
    A leading determiner is stripped ONLY when a content word follows -- so a standalone label like block 'A'
    survives ('a' as a whole mention is a name/label, not the article; 'a box' -> 'box')."""
    toks = s.lower().strip().strip(".,:;\"'()").split()
    # block-name normalization: 'a block called A' / 'second block call B' / 'block C' -> the single-letter LABEL,
    # so a block relation ('B left of A') shares the node with the objects contained in that block (else it is
    # orphaned from the containment graph and cross-block inheritance cannot traverse it).
    if "block" in toks or "blocks" in toks:
        letters = [w for w in toks if len(w) == 1 and w.isalpha()]
        if letters:
            return letters[-1]
    while len(toks) > 1 and toks[0] in ("the", "a", "an", "his", "her", "their", "its", "my", "our", "your",
                                        "this", "that", "these", "those", "some", "all", "of"):
        toks = toks[1:]
    return " ".join(toks).strip(".,:;\"'()")


class SpatialModel:
    """A small updatable relational graph over spatial entities/places, and the composition reasoner.

    Three edge families, matching the three inference types:
      * CONTAINMENT: directed figure -> ground ('figure IN ground'); answered by TRANSITIVE closure.
      * POSITION:    projective A rel B, normalized to an axis + sign; answered by per-axis transitive closure
                     + converse (inverse) -- the Franklin-Tversky framework read.
      * MOVES:       (entity, source, goal, t); folded into a LocationRegister for the PATH/TRANSFER read
                     (Goal-over-Source + vacate).
    """

    def __init__(self, max_depth: int = 8) -> None:
        self.max_depth = int(max_depth)                     # closure-depth cap (OUR-INVENTION; swept)
        self._contains: Dict[str, Set[str]] = defaultdict(set)   # figure -> {grounds} (direct edges)
        # position: axis -> directed graph on the canonical positive relation P (a -> b means 'a P b')
        self._pos: Dict[str, Dict[str, Set[str]]] = {ax: defaultdict(set) for ax in ("v", "d", "h", "g", "n")}
        self._sym: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))  # rel -> a -> {b}
        self._moves: List[Tuple[str, Optional[str], Optional[str], int]] = []
        self.entities: Set[str] = set()
        self._reach_key = None                              # EFFICIENCY: containment-reachability memo (per depth)
        self._reach_c: Dict[str, Set[str]] = {}

    def _invalidate(self) -> None:
        self._reach_key = None
        self._reach_c = {}

    # -- construction -------------------------------------------------------
    def add_containment(self, figure: str, ground: str) -> None:
        f, g = canon_entity(figure), canon_entity(ground)
        if f and g and f != g:
            self._contains[f].add(g)
            self.entities.update((f, g))
            self._invalidate()

    def add_position(self, a: str, rel: str, b: str) -> None:
        r = norm_rel(rel)
        if r is None:
            return
        ca, cb = canon_entity(a), canon_entity(b)
        if not ca or not cb or ca == cb:
            return
        self.entities.update((ca, cb))
        if r in SYMMETRIC:
            self._sym[r][ca].add(cb)
            self._sym[r][cb].add(ca)
            return
        axis, P, sign = AXIS_OF[r]
        if sign > 0:
            self._pos[axis][ca].add(cb)          # a P b
        else:
            self._pos[axis][cb].add(ca)          # a inv(P) b  <=>  b P a

    def add_move(self, entity: str, source: Optional[str], goal: Optional[str], t: int) -> None:
        e = canon_entity(entity)
        if e:
            self._moves.append((e, canon_entity(source) if source else None,
                                canon_entity(goal) if goal else None, t))
            self.entities.add(e)

    # -- CONTAINMENT reasoning (transitive closure; nested regions) ---------
    def _reachable_contain(self, f: str) -> Set[str]:
        """Set of grounds (transitively) containing f, at the current max_depth. Memoized per depth (EFFICIENCY:
        O(1) after first touch; the memo is cleared on any edge add). Deterministic (set membership only)."""
        if self._reach_key != self.max_depth:
            self._reach_key = self.max_depth
            self._reach_c = {}
        cached = self._reach_c.get(f)
        if cached is not None:
            return cached
        seen: Set[str] = set()
        frontier = deque([(f, 0)])
        while frontier:
            node, d = frontier.popleft()
            if d >= self.max_depth:
                continue
            for nxt in self._contains.get(node, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt, d + 1))
        self._reach_c[f] = seen
        return seen

    def contains_path(self, figure: str, ground: str) -> bool:
        """True iff `figure` is (transitively) inside `ground`: reachability over containment edges (memoized)."""
        f, g = canon_entity(figure), canon_entity(ground)
        if f == g:
            return False
        return g in self._reachable_contain(f)

    def _ancestors(self, x: str) -> Set[str]:
        """All (transitive) containers of x -- the nested regions x sits inside."""
        seen: Set[str] = set()
        dq = deque([x])
        while dq:
            n = dq.popleft()
            for g in self._contains.get(n, ()):
                if g not in seen and len(seen) < 64:
                    seen.add(g)
                    dq.append(g)
        return seen

    def containment_hops(self, figure: str, ground: str) -> Optional[int]:
        """Shortest containment-chain length from figure to ground (1 = direct edge), or None if unreachable."""
        f, g = canon_entity(figure), canon_entity(ground)
        if f == g:
            return 0
        seen = {f}
        frontier = deque([(f, 0)])
        while frontier:
            node, d = frontier.popleft()
            if d >= self.max_depth:
                continue
            for nxt in self._contains.get(node, ()):
                if nxt == g:
                    return d + 1
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt, d + 1))
        return None

    # -- POSITION reasoning (per-axis transitive closure + converse) --------
    def _axis_reaches(self, axis: str, a: str, b: str) -> bool:
        """True iff a P* b in the axis's directed positive-relation graph (transitive closure)."""
        if a == b:
            return False
        seen = {a}
        frontier = deque([(a, 0)])
        while frontier:
            node, d = frontier.popleft()
            if d >= self.max_depth:
                continue
            for nxt in self._pos[axis].get(node, ()):
                if nxt == b:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt, d + 1))
        return False

    def relative(self, a: str, rel: str, b: str) -> Optional[bool]:
        """Answer 'is A `rel` B?' by composing the position framework. True / False / None(=undetermined).
        Projective: YES iff the queried directed relation is entailed by closure; NO iff its INVERSE (opposite
        side on the same axis) is entailed; None otherwise. Symmetric (near/far/touching): direct membership."""
        r = norm_rel(rel)
        if r is None:
            return None
        ca, cb = canon_entity(a), canon_entity(b)
        if not ca or not cb or ca == cb:
            return None
        if r in SYMMETRIC:
            if cb in self._sym[r].get(ca, ()):
                return True
            # opposite proximity relation asserted -> False (near vs far)
            opp = "far" if r == "near" else ("near" if r == "far" else None)
            if opp and cb in self._sym[opp].get(ca, ()):
                return False
            return None
        axis, P, sign = AXIS_OF[r]
        want_fwd = (sign > 0)
        fwd = self._axis_reaches(axis, ca, cb)   # ca P cb
        rev = self._axis_reaches(axis, cb, ca)   # cb P ca  <=> ca inv(P) cb
        if fwd and not rev:
            return want_fwd
        if rev and not fwd:
            return (not want_fwd)
        if fwd and rev:
            return None
        # NESTED-FRAME INHERITANCE (Franklin-Tversky hierarchical reference frames; PINNED nested regions):
        # if A and B are not nested in each other, an object inherits its container's coarse position -- 'X in
        # block-L, Y in block-R, L left-of R' |= 'X left-of Y'. Compose position ACROSS the containment levels.
        ax_a = {ca} | self._ancestors(ca)
        ax_b = {cb} | self._ancestors(cb)
        if ca in ax_b or cb in ax_a or (ax_a & ax_b):
            return None                          # nested in each other or share a container -> no inheritance
        f2 = any(self._axis_reaches(axis, u, v) for u in ax_a for v in ax_b)
        r2 = any(self._axis_reaches(axis, v, u) for u in ax_a for v in ax_b)
        if f2 and not r2:
            return want_fwd
        if r2 and not f2:
            return (not want_fwd)
        return None                              # undetermined

    def relative_status(self, a: str, rel: str, b: str) -> str:
        """Principled abstention (Byrne & Johnson-Laird 1989: one preferred model, search for a counter-model).
        Returns 'yes'/'no'/'indeterminate'/'unknown'. INDETERMINATE = both entities are in the model but the
        relation is entailed in NEITHER direction (multiple models are consistent -- the honest 'can't tell', which
        the literature says is the brain-correct response to an under-specified scene). UNKNOWN = an entity is
        absent from the model (nothing was extracted about it) -- a different failure (missing information)."""
        ca, cb = canon_entity(a), canon_entity(b)
        ans = self.relative(ca, rel, cb)
        if ans is True:
            return "yes"
        if ans is False:
            return "no"
        if ca in self.entities and cb in self.entities:
            return "indeterminate"
        return "unknown"

    def all_rel(self, figure_head: str, rel: str, ground: str) -> Optional[bool]:
        """UNIVERSAL quantifier (Ragni & Knauff quantified spatial reasoning): do ALL entities whose head noun is
        `figure_head` stand in `rel` to `ground`? None if there are no matches. Works for containment (rel='in')
        or a projective relation. A verified capability -- NOT scored in the end-to-end (it needs only direct-
        relation aggregation, so it does not exercise multi-hop composition)."""
        g = canon_entity(ground)
        fh = figure_head.lower()
        matches = [e for e in self.entities if fh and fh in e.split()]
        if not matches or not g:
            return None
        if norm_rel(rel) == "in" or rel == "in":
            return all(self.contains_path(e, g) for e in matches)
        vals = [self.relative(e, rel, g) for e in matches]
        return all(v is True for v in vals)

    def exists_rel(self, rel: str, ground: str, figure_head: Optional[str] = None) -> Optional[bool]:
        """EXISTENTIAL (closed-world over the model's entities): is there SOME entity (optionally head==figure_head)
        standing in `rel` to `ground`? True if any does; False if all determinable and none does; None otherwise."""
        g = canon_entity(ground)
        if not g:
            return None
        cands = [e for e in self.entities if e != g and (figure_head is None or figure_head.lower() in e.split())]
        contain = (norm_rel(rel) == "in" or rel == "in")
        vals = [(self.contains_path(e, g) or None) if contain else self.relative(e, rel, g) for e in cands]
        if any(v is True for v in vals):
            return True
        if vals and all(v is False for v in vals):
            return False
        return None

    def is_consistent(self) -> bool:
        """True iff the relational model admits a single coherent layout (no impossible description). Flags a
        CONTAINMENT cycle (x in y in x) or a STRICT-AXIS cycle (x above y above x) -- the brain notices an
        impossible arrangement (mental-model construction fails on a contradictory description). Doubles as an
        extraction-error signal (a cycle usually means a mis-bound relation)."""
        for x in self.entities:                              # containment must be a DAG
            if x in self._reachable_contain_full(x):
                return False
        for axis in ("v", "d", "h", "g", "n"):               # each projective axis must be a strict order
            for x, succs in list(self._pos[axis].items()):
                for s in succs:                              # x P s ; a cycle iff s reaches back to x
                    if s == x or self._axis_reaches(axis, s, x):
                        return False
        return True

    def _reachable_contain_full(self, f: str) -> Set[str]:
        """Unbounded containment reachability (for the cycle check): does f reach itself?"""
        seen: Set[str] = set()
        frontier = deque([f])
        while frontier:
            node = frontier.popleft()
            for nxt in self._contains.get(node, ()):
                if nxt == f:
                    return {f}
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return seen

    # -- PATH / TRANSFER reasoning (reuse LocationRegister; Goal-over-Source + vacate) --
    def build_register(self, n_clauses: Optional[int] = None) -> LocationRegister:
        """Fold the moves into the promoted LocationRegister (start every mover present at t=0)."""
        movers = sorted({m[0] for m in self._moves})
        nc = (max([m[3] for m in self._moves], default=0) + 1) if n_clauses is None else n_clauses
        reg = LocationRegister().start(movers, n_clauses=nc)
        for (e, src, goal, t) in sorted(self._moves, key=lambda m: m[3]):
            if goal is not None:
                reg.apply_motion(e, "arrive", goal, t)      # Goal-over-Source: model updates to the goal
            elif src is not None:
                reg.apply_motion(e, "depart", None, t)      # left source for an unnamed destination -> AWAY
        return reg

    def where_after(self, entity: str, reg: Optional[LocationRegister] = None) -> Optional[str]:
        """The mover's current location node after all its moves (the post-move location = the Goal)."""
        reg = reg or self.build_register()
        e = canon_entity(entity)
        node = reg.where_is(e)
        return None if node in (DEICTIC_SCENE, AWAY, None) else node

    def still_at(self, entity: str, place: str, reg: Optional[LocationRegister] = None) -> Optional[bool]:
        """The vacate-Source 'is A still in K?' read: True iff A's current node equals K or is (transitively)
        contained in K; False once A has moved out (Goal-over-Source vacates the Source). None if unknown."""
        reg = reg or self.build_register()
        e, k = canon_entity(entity), canon_entity(place)
        node = reg.where_is(e)
        if node in (None, AWAY):
            return None if node is None else False   # departed to unnamed dest -> no longer at any named place
        if node == DEICTIC_SCENE:
            return None
        if node == k:
            return True
        return self.contains_path(node, k)           # still 'in K' if current node nests inside K

    # -- info-free TWIN: shuffle the relation bindings, keep node set + counts -----------
    def shuffled_twin(self, rng) -> "SpatialModel":
        """Permute the GROUND of each containment edge, the target of each position edge, and the goal of each
        move -- keeping every node, edge count and relation type. Destroys the relational CONTENT only. The
        info-free control: if it still answers, the answer was not coming from the relations."""
        tw = SpatialModel(max_depth=self.max_depth)
        tw.entities = set(self.entities)
        nodes = sorted(self.entities)
        if not nodes:
            return tw
        def perm_pick(exclude):
            for _ in range(8):
                c = nodes[int(rng.integers(len(nodes)))]
                if c != exclude:
                    return c
            return nodes[int(rng.integers(len(nodes)))]
        for f, gs in self._contains.items():
            for _g in gs:
                tw._contains[f].add(perm_pick(f))
        for axis, graph in self._pos.items():
            for a, bs in graph.items():
                for _b in bs:
                    tw._pos[axis][a].add(perm_pick(a))
        for r, graph in self._sym.items():
            for a, bs in graph.items():
                for _b in bs:
                    c = perm_pick(a)
                    tw._sym[r][a].add(c)
                    tw._sym[r][c].add(a)
        for (e, src, goal, t) in self._moves:
            tw._moves.append((e, src, perm_pick(e) if goal is not None else None, t))
        return tw
