"""SYMBOLIC working-memory discourse overlay (state-of-mind) for the base-first reader.

CANONICAL packaging of the VALIDATED two-layer state-of-mind arc (2026-07-17, SETTLED).
This is the WORKING OVERLAY layer only: a symbolic, exact, salience-weighted tracker of
the few active discourse threads (the reader's real operating point). It is the layer that
was proven to beat HD-bundle superposition in every encoding at working-memory scale.

TWO-LAYER ARCHITECTURE (crossover ~8x overload; do NOT collapse the layers):
  (1) OVERLAY (this module): working-memory scale, few active threads -> SYMBOLIC EXACT.
  (2) DURABLE MEMORY (separate): overload / corpus scale -> HD lossy bundle wins. Wire the
      overlay's SURPRISE / recognize-KNOWN probe to that durable store (see DURABLE_MEMORY_WIRING).

VALIDATED BEHAVIOR PRESERVED (the reason this module exists):
  the recency / salience DOUBLE-DISSOCIATION on real coref-gold (LitBank CC-BY):
    - RECENCY owns SHORT-distance reference (near antecedent) -- brain-aligned local resolution.
    - maintained SALIENCE / FREQUENCY owns LONG-distance reference (a frequently-evoked far
      antecedent that the recency window dropped).
  HONEST LEVER CAVEAT (VET a7ca3db1): at long distance the pure-FREQUENCY resolver is the actual
  lever (freq_only 0.123 > maintained_overlay 0.099 > recency 0.037); the recency TIE-BREAK inside
  the maintained overlay slightly HURTS at distance. The maintained overlay still beats recency at
  distance (the packaged claim), but freq is the mechanism. Both resolvers are ported faithfully so
  the caller can choose; nothing is "improved" over the validated logic.

PROVENANCE (faithful extraction, no reinvention):
  - resolvers + salience arithmetic + gender/number agreement + surface-head entity grouping:
    experiments/exp_read_discourse_overlay_longdist_reference_v1.py (git 49bb99c24; VET ledger a7ca3db1).
  - proper-NAME -> entity instantiation + attribute (number/animacy/gender) tracking:
    experiments/exp_read_discourse_overlay_context_precision_reopen_v1.py (git 7e3acab66).
  Where the 11 exp_read_discourse_* cells disagree on overlay details, the LATEST VET'd cell
  (longdist 49bb99c24) is authoritative; earlier cells are superseded.

SURPRISE / recognize-KNOWN (requirement, reuse-not-reinvent): a mention is recognized-KNOWN if its
head is present in the DURABLE BASE, else it is SURPRISE-FLAGGED as new (absent = high surprise). The
base-membership signal IS the surprise signal; a KnownBase seam lets the caller wire the real durable
store (AdditiveKGMap.entity_to_idx membership, or a graded probe via AdditiveKGMap.score_all) without
this module reinventing a surprise metric. Proper names are the canonical new-entity case: a
capitalized mid-sentence proper noun is absent from the base -> high surprise -> INSTANTIATE a new
entity in the overlay, resolvable by later pronouns.

GLASS-BOX: pure symbolic; NO torch phasors, NO external LLM, NO network. ASCII-only, no em-dashes.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Protocol, Tuple

# ---------------------------------------------------------------------------
# Canonical durable-memory wiring note (requirement 3): the overlay is the WORKING layer; the reader
# must wire recognize-KNOWN / durable recall to the REAL store below, NOT a dict stub.
# ---------------------------------------------------------------------------
DURABLE_MEMORY_WIRING = (
    "The overlay is the SYMBOLIC working layer only. Wire the reader's DURABLE memory to: "
    "(1) hdlab.memory.Codebook (named-atom cosine cleanup, attention-gated lookup); "
    "(2) backend.substrate_index PartitionedStore (persisted atom store; A5-gated writes); "
    "(3) hdlab.working_memory multi-bank (K-capacity chain-grade at K=4096, k_per_bank>=64). "
    "recognize-KNOWN / surprise flows through a KnownBase built over the durable store's index "
    "(e.g. AdditiveMapKnownBase over hdlab.additive_map.AdditiveKGMap.entity_to_idx); do NOT back "
    "the base with an ad-hoc dict."
)

# ---------------------------------------------------------------------------
# VALIDATED constants -- ported VERBATIM from longdist 49bb99c24 (do not tune).
# ---------------------------------------------------------------------------
PRONOUN_SCOPE: Dict[str, Dict[str, str]] = {
    "he":   {"number": "singular", "gender": "masc"},
    "him":  {"number": "singular", "gender": "masc"},
    "his":  {"number": "singular", "gender": "masc"},
    "she":  {"number": "singular", "gender": "fem"},
    "her":  {"number": "singular", "gender": "fem"},
    "hers": {"number": "singular", "gender": "fem"},
    "it":   {"number": "singular", "gender": "neuter"},
    "its":  {"number": "singular", "gender": "neuter"},
    "they": {"number": "plural",   "gender": "any"},
    "them": {"number": "plural",   "gender": "any"},
    "their": {"number": "plural",  "gender": "any"},
}
# Animate gendered singular pronouns carry a real agreement axis (the coref-heavy prose case).
TARGET_PRONOUNS = {"he", "him", "his", "she", "her", "hers"}

MASC_CUES = {"mr", "mister", "sir", "lord", "master", "gentleman", "man", "men",
             "boy", "boys", "father", "dad", "papa", "son", "brother", "uncle",
             "king", "prince", "husband", "widower", "nephew", "grandfather",
             "he", "him", "his", "himself"}
FEM_CUES = {"mrs", "miss", "ms", "madam", "madame", "lady", "mistress", "woman",
            "women", "girl", "girls", "mother", "mom", "mama", "daughter",
            "sister", "aunt", "queen", "princess", "wife", "widow", "niece",
            "grandmother", "maid", "she", "her", "hers", "herself"}

# Validated salience knobs (longdist 49bb99c24): frequency-primary accumulator, recency as tie-break.
OVERLAY_BETA = 0.5              # recency tie-break weight (frequency counts dominate)
OVERLAY_TIEBREAK_LAMBDA = 0.1   # tie-break decay rate
WINDOW_K_DEFAULT = 5            # recency-window cutoff (the structural-wall illustration arm)


def infer_nominal_gender(span_toks: List[str]) -> Optional[str]:
    """Glass-box gender from title / gendered-noun cues; 'masc' / 'fem' / None (unknown -> any)."""
    toks = {t.lower().strip(".,'") for t in span_toks}
    m = bool(toks & MASC_CUES)
    f = bool(toks & FEM_CUES)
    if m and not f:
        return "masc"
    if f and not m:
        return "fem"
    return None


def compatible(target_gender: Optional[str], target_number: Optional[str],
               cand_gender: Optional[str], cand_number: Optional[str]) -> bool:
    """Weak agreement filter (identical across resolvers): compatible unless a KNOWN attr conflicts."""
    if (cand_gender is not None and target_gender not in ("any", None)
            and cand_gender not in ("any", None) and cand_gender != target_gender):
        return False
    if (cand_number is not None and target_number not in ("any", None)
            and cand_number not in ("any", None) and cand_number != target_number):
        return False
    return True


# ---------------------------------------------------------------------------
# Recognize-KNOWN / surprise seam (durable-base membership IS the surprise signal).
# ---------------------------------------------------------------------------
class KnownBase(Protocol):
    """Durable-base membership probe: known() gates recognize-vs-surprise; surprise() is graded in [0,1]."""

    def known(self, head: str) -> bool:
        ...

    def surprise(self, head: str) -> float:
        ...


class SetKnownBase:
    """Default KnownBase over a set of known heads: absent -> surprise 1.0, present -> 0.0."""

    def __init__(self, known_heads: Optional[set] = None) -> None:
        self._known = set(known_heads or set())

    def known(self, head: str) -> bool:
        return head.lower() in self._known

    def surprise(self, head: str) -> float:
        return 0.0 if self.known(head) else 1.0


class AdditiveMapKnownBase:
    """KnownBase over hdlab.additive_map.AdditiveKGMap: membership via its entity index = the base vocab.

    Binary membership is the default surprise signal (absent = new entity = high surprise). For a GRADED
    surprise the caller may pass graded_surprise_fn wired to AdditiveKGMap.score_all (how poorly the map
    predicts the mention in a given relation); this module does not reinvent that metric.
    """

    def __init__(self, amap, graded_surprise_fn: Optional[Callable[[str], float]] = None) -> None:
        self._amap = amap
        self._graded = graded_surprise_fn

    def known(self, head: str) -> bool:
        return head.lower() in getattr(self._amap, "entity_to_idx", {})

    def surprise(self, head: str) -> float:
        if self._graded is not None:
            return float(self._graded(head))
        return 0.0 if self.known(head) else 1.0


# ---------------------------------------------------------------------------
# Overlay state objects.
# ---------------------------------------------------------------------------
class EntityState:
    """A tracked discourse entity (surface-head grouping): mention midxs + agreement attributes."""

    def __init__(self, head: str, gender: Optional[str], number: Optional[str],
                 is_named: bool) -> None:
        self.head = head
        self.gender = gender
        self.number = number
        self.is_named = is_named
        self.mention_midxs: List[int] = []

    @property
    def count(self) -> int:
        """Number of times this entity has been mentioned (the frequency salience term)."""
        return len(self.mention_midxs)

    @property
    def last_midx(self) -> int:
        """Mention-stream position of the most recent mention (recency term)."""
        return self.mention_midxs[-1]

    def salience(self, now: int, beta: float, lam: float) -> float:
        """Validated salience = count + beta * exp(-lam * (now - last_midx)) (freq-primary, recency tie-break)."""
        return self.count + beta * math.exp(-lam * (now - self.last_midx))


class ObserveResult:
    """Outcome of observing one token: surprise flag + entity binding (None for a pronoun reference)."""

    def __init__(self, head: str, midx: int, is_pronoun: bool, is_known: bool,
                 surprise: float, entity: Optional[EntityState], is_new_entity: bool) -> None:
        self.head = head
        self.midx = midx
        self.is_pronoun = is_pronoun
        self.is_known = is_known
        self.surprise = surprise
        self.entity = entity
        self.is_new_entity = is_new_entity


# ---------------------------------------------------------------------------
# The reusable overlay.
# ---------------------------------------------------------------------------
class WorkingOverlay:
    """Symbolic salience-weighted working overlay: observe mentions, resolve references by strategy.

    Resolution strategies (ported faithfully from longdist 49bb99c24):
      'recency'         nearest COMPATIBLE entity (unbounded Hobbs recency) -- owns SHORT distance.
      'recency_window'  nearest compatible entity within window K (structural-wall illustration).
      'maintained'      argmax salience = count + beta*exp(-lam*dist) -- the maintained overlay.
      'freq'            argmax count (pure frequency) -- the actual LONG-distance lever (VET note).
    """

    def __init__(self, base: Optional[KnownBase] = None, *, beta: float = OVERLAY_BETA,
                 lam: float = OVERLAY_TIEBREAK_LAMBDA, window_k: int = WINDOW_K_DEFAULT) -> None:
        self.base: KnownBase = base if base is not None else SetKnownBase()
        self.beta = beta
        self.lam = lam
        self.window_k = window_k
        self._entities: Dict[str, EntityState] = {}
        self._next_midx = 0

    # ---- observation ------------------------------------------------------
    def observe(self, head: str, *, is_pronoun: bool = False, gender: Optional[str] = None,
                number: Optional[str] = None, is_proper_name: bool = False) -> ObserveResult:
        """Observe one mention. Pronouns advance the stream but do not create entities (they are references);
        nominal / proper-name mentions are grouped by lowercased head into the active set. Returns the
        surprise flag (recognize-KNOWN vs new) + the bound entity."""
        head = head.lower()
        midx = self._next_midx
        self._next_midx += 1
        is_known = self.base.known(head)
        surprise = self.base.surprise(head)
        if is_pronoun:
            return ObserveResult(head, midx, True, is_known, surprise, None, False)
        is_new = head not in self._entities
        if is_new:
            self._entities[head] = EntityState(head, gender, number, is_proper_name)
        ent = self._entities[head]
        # keep a known attribute if a later mention supplies one the first lacked
        if ent.gender is None and gender is not None:
            ent.gender = gender
        if ent.number is None and number is not None:
            ent.number = number
        if is_proper_name:
            ent.is_named = True
        ent.mention_midxs.append(midx)
        return ObserveResult(head, midx, False, is_known, surprise, ent, is_new)

    def observe_surface(self, surface: str, *, at_sentence_start: bool = False) -> ObserveResult:
        """Glass-box classify a raw surface token then observe it. A capitalized MID-sentence token that is
        not a pronoun is treated as a PROPER NAME -> instantiates a new entity (the name->entity mechanism);
        a known pronoun surface -> a reference; otherwise a common nominal. Number defaults to singular."""
        low = surface.lower().strip(".,'\"!?;:")
        if low in PRONOUN_SCOPE:
            sc = PRONOUN_SCOPE[low]
            return self.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
        is_proper = bool(surface[:1].isupper() and not at_sentence_start)
        gender = infer_nominal_gender([surface])
        return self.observe(low, gender=gender, number="singular", is_proper_name=is_proper)

    # ---- resolution -------------------------------------------------------
    def _compatible_entities(self, gender: Optional[str], number: Optional[str]) -> List[EntityState]:
        """Active entities whose known attributes do not conflict with the (gender, number) target."""
        return [e for e in self._entities.values()
                if compatible(gender, number, e.gender, e.number)]

    def resolve(self, *, gender: Optional[str] = None, number: Optional[str] = None,
                strategy: str = "maintained", now: Optional[int] = None) -> Optional[EntityState]:
        """Resolve a pronoun reference against the active set under the chosen strategy. Returns the chosen
        EntityState (its last_midx = the concrete antecedent mention) or None if no compatible entity."""
        if now is None:
            now = self._next_midx
        cands = self._compatible_entities(gender, number)
        if not cands:
            return None
        if strategy == "recency":
            return max(cands, key=lambda e: e.last_midx)
        if strategy == "recency_window":
            in_win = [e for e in cands if (now - e.last_midx) <= self.window_k]
            if not in_win:
                return None
            return max(in_win, key=lambda e: e.last_midx)
        if strategy == "freq":
            best = None
            best_count = -1
            for e in cands:                       # first-wins tie-break (matches ported freq_only)
                if e.count > best_count:
                    best_count = e.count
                    best = e
            return best
        if strategy == "maintained":
            best = None
            best_sal = -1.0
            for e in cands:                       # first-wins tie-break (matches ported maintained_overlay)
                sal = e.salience(now, self.beta, self.lam)
                if sal > best_sal:
                    best_sal = sal
                    best = e
            return best
        raise ValueError("unknown strategy: %r" % strategy)

    def resolve_pronoun(self, pronoun: str, *, strategy: str = "maintained",
                        now: Optional[int] = None) -> Optional[EntityState]:
        """Convenience: resolve by a surface pronoun string using its scoped gender/number agreement."""
        sc = PRONOUN_SCOPE.get(pronoun.lower())
        if sc is None:
            raise ValueError("not an in-scope pronoun: %r" % pronoun)
        return self.resolve(gender=sc["gender"], number=sc["number"], strategy=strategy, now=now)

    # ---- introspection ----------------------------------------------------
    def active_set(self, *, top: Optional[int] = None,
                   now: Optional[int] = None) -> List[Tuple[EntityState, float]]:
        """Salience-ranked (entity, salience) list -- the maintained working state of mind."""
        if now is None:
            now = self._next_midx
        ranked = sorted(self._entities.values(),
                        key=lambda e: e.salience(now, self.beta, self.lam), reverse=True)
        if top is not None:
            ranked = ranked[:top]
        return [(e, e.salience(now, self.beta, self.lam)) for e in ranked]

    def entities(self) -> List[EntityState]:
        """All tracked entities in first-mention order."""
        return list(self._entities.values())

    @property
    def n_observed(self) -> int:
        """Total tokens observed (the mention-stream length; the distance unit for recency/salience)."""
        return self._next_midx
