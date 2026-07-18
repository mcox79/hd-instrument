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

# DEIXIS / discourse-participant pronoun classes. A 1st-person pronoun indexes the SPEAKER of the current
# quoted turn; a 2nd-person pronoun indexes the ADDRESSEE. These are NOT antecedent-resolution pronouns
# (they do not point back to a prior surface mention) -- they index a discourse ROLE, resolved through the
# quotative frame. Kept module-level + additive so the packaged antecedent resolvers are untouched.
FIRST_PERSON_PRONOUNS = frozenset({"i", "me", "my", "mine", "myself",
                                   "we", "us", "our", "ours", "ourselves"})
SECOND_PERSON_PRONOUNS = frozenset({"you", "your", "yours", "yourself", "yourselves",
                                    "ye", "thou", "thee", "thy", "thine", "thyself"})


def deixis_person(pronoun_low: str) -> Optional[str]:
    """Classify a surface token as a discourse-participant deixis: 'first' / 'second' / None (not deictic)."""
    p = pronoun_low.lower().strip(".,'\"!?;:")
    if p in FIRST_PERSON_PRONOUNS:
        return "first"
    if p in SECOND_PERSON_PRONOUNS:
        return "second"
    return None

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
    """A tracked discourse entity (surface-head grouping): mention midxs + agreement attributes.

    animacy is an OPTIONAL additive axis ('animate' / 'inanimate' / None-unknown), fed by the caller's
    grounding. It is used ONLY by the opt-in prefer_agreement resolution path (default OFF); it never
    changes the hard compatible() filter, so validated recency/salience behavior is bit-identical."""

    def __init__(self, head: str, gender: Optional[str], number: Optional[str],
                 is_named: bool, animacy: Optional[str] = None) -> None:
        self.head = head
        self.gender = gender
        self.number = number
        self.is_named = is_named
        self.animacy = animacy
        self.mention_midxs: List[int] = []

    @property
    def count(self) -> int:
        """Number of times this entity has been mentioned (the frequency salience term)."""
        return len(self.mention_midxs)

    @property
    def last_midx(self) -> int:
        """Mention-stream position of the most recent mention (recency term)."""
        return self.mention_midxs[-1]

    @property
    def first_midx(self) -> int:
        """Mention-stream position of the FIRST mention (introduction primacy = topicality tie-break)."""
        return self.mention_midxs[0]

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
        # DEIXIS / discourse-participant model (additive; default-off = None -> no-op). A DISTINCT mechanism
        # from antecedent resolution: 1st/2nd-person pronouns index a discourse ROLE (speaker / addressee),
        # not a prior surface mention. Nothing here touches _entities or any validated resolve path, so with
        # the deixis axis unused the observe / resolve / active_set behavior is bit-identical to the packaged
        # overlay (the 6/6 witness stays green). See note_turn / resolve_deixis below.
        self._speaker: Optional[str] = None
        self._addressee: Optional[str] = None
        self._prev_speaker: Optional[str] = None

    # ---- observation ------------------------------------------------------
    def observe(self, head: str, *, is_pronoun: bool = False, gender: Optional[str] = None,
                number: Optional[str] = None, is_proper_name: bool = False,
                animacy: Optional[str] = None) -> ObserveResult:
        """Observe one mention. Pronouns advance the stream but do not create entities (they are references);
        nominal / proper-name mentions are grouped by lowercased head into the active set. Returns the
        surprise flag (recognize-KNOWN vs new) + the bound entity. animacy is an OPTIONAL agreement axis
        (used only by the opt-in prefer_agreement resolution path; default None = unchanged behavior)."""
        head = head.lower()
        midx = self._next_midx
        self._next_midx += 1
        is_known = self.base.known(head)
        surprise = self.base.surprise(head)
        if is_pronoun:
            return ObserveResult(head, midx, True, is_known, surprise, None, False)
        is_new = head not in self._entities
        if is_new:
            self._entities[head] = EntityState(head, gender, number, is_proper_name, animacy=animacy)
        ent = self._entities[head]
        # keep a known attribute if a later mention supplies one the first lacked
        if ent.gender is None and gender is not None:
            ent.gender = gender
        if ent.number is None and number is not None:
            ent.number = number
        if ent.animacy is None and animacy is not None:
            ent.animacy = animacy
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

    def _agreement_preferred(self, cands: List[EntityState], gender: Optional[str],
                             expects_animate: bool) -> List[EntityState]:
        """Opt-in agreement refinement (additive; used only when prefer_agreement=True). Among the already
        hard-compatible candidates, prefer (1) a KNOWN-gender match to the target over a gender-UNKNOWN
        competitor, then (2) an ANIMATE candidate when the target pronoun is a gendered (he/she) pronoun.
        Each tier only NARROWS when a non-empty preferred subset exists; else the tier is a no-op (so a
        gender-unknown-only or animacy-unknown-only active set falls back to the base strategy)."""
        filtered = cands
        if gender in ("masc", "fem"):
            known_match = [e for e in filtered if e.gender == gender]
            if known_match:
                filtered = known_match
        if expects_animate:
            animate = [e for e in filtered if e.animacy == "animate"]
            if animate:
                filtered = animate
        return filtered

    @staticmethod
    def _topical_ranked(cands: List[EntityState]) -> Optional[EntityState]:
        """Salience-RANK / topicality resolver (Centering Theory backward-looking-center preference; opt-in).
        Among the (already agreement-narrowed) candidates prefer the TOPICAL protagonist over a merely-RECENT
        competitor: rank by (frequency count, then FIRST-MENTION primacy = earliest introduced). NO recency
        tie-break -- that is exactly the merely-recent lever this path is designed to override. Glass-box,
        deterministic (first_midx is unique per entity)."""
        if not cands:
            return None
        return max(cands, key=lambda e: (e.count, -e.first_midx))

    def resolve(self, *, gender: Optional[str] = None, number: Optional[str] = None,
                strategy: str = "maintained", now: Optional[int] = None,
                prefer_agreement: bool = False, expects_animate: bool = False,
                prefer_topical: bool = False) -> Optional[EntityState]:
        """Resolve a pronoun reference against the active set under the chosen strategy. Returns the chosen
        EntityState (its last_midx = the concrete antecedent mention) or None if no compatible entity.
        prefer_agreement (default False = validated behavior) additionally prefers a known-gender / animate
        antecedent BEFORE the recency/salience tie-break (glass-box agreement refinement).
        prefer_topical (default False = validated behavior) selects the TOPICAL protagonist (frequency +
        first-mention primacy) among the agreement-valid candidates INSTEAD of the strategy's recency/salience
        tie-break -- the Centering-Theory salience-rank cue (subject/possessor slot; caller routes by case)."""
        if now is None:
            now = self._next_midx
        cands = self._compatible_entities(gender, number)
        if not cands:
            return None
        if prefer_agreement:
            cands = self._agreement_preferred(cands, gender, expects_animate)
        if prefer_topical:
            return self._topical_ranked(cands)
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
                        now: Optional[int] = None,
                        prefer_agreement: bool = False,
                        prefer_topical: bool = False) -> Optional[EntityState]:
        """Convenience: resolve by a surface pronoun string using its scoped gender/number agreement.
        prefer_agreement (default False = validated behavior) turns on the known-gender / animate
        preference; a gendered (masc/fem) pronoun is treated as expecting an animate antecedent.
        prefer_topical (default False = validated behavior) selects the topical protagonist over a merely
        recent competitor among the agreement-valid candidates (Centering-Theory salience-rank cue)."""
        sc = PRONOUN_SCOPE.get(pronoun.lower())
        if sc is None:
            raise ValueError("not an in-scope pronoun: %r" % pronoun)
        expects_animate = sc["gender"] in ("masc", "fem")
        return self.resolve(gender=sc["gender"], number=sc["number"], strategy=strategy, now=now,
                            prefer_agreement=prefer_agreement, expects_animate=expects_animate,
                            prefer_topical=prefer_topical)

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

    # ---- deixis / discourse-participant model (additive; opt-in) ----------
    def note_turn(self, speaker: Optional[str], addressee: Optional[str] = None) -> None:
        """Register the current quoted turn's discourse participants (the deixis anchor). SPEAKER is the
        subject of the quotative frame; ADDRESSEE is the entity spoken to (a vocative / a 'to X' in the
        frame / the prior speaker in an exchange). Additive: touches NO entity state and NO validated
        resolve path. A NEW speaker rotates the previous speaker into the prev-speaker slot, so a later
        turn's 2nd-person can fall back to the prior speaker (dialogue turn-taking)."""
        if speaker is not None and speaker != self._speaker:
            self._prev_speaker = self._speaker
        self._speaker = speaker
        self._addressee = addressee

    def resolve_deixis(self, pronoun_low: str) -> Optional[str]:
        """Resolve a 1st/2nd-person (deictic) pronoun to a discourse PARTICIPANT head: 1st -> speaker,
        2nd -> addressee (falling back to the prior speaker in an exchange when no explicit addressee is
        set). Returns None if the pronoun is not deictic or the participant is unset. DISTINCT from
        resolve()/resolve_pronoun() (antecedent resolution) -- this indexes a discourse ROLE."""
        person = deixis_person(pronoun_low)
        if person == "first":
            return self._speaker
        if person == "second":
            return self._addressee if self._addressee is not None else self._prev_speaker
        return None

    def clear_turn(self) -> None:
        """Reset the discourse-participant slots (e.g. at a passage boundary). Does not touch entities."""
        self._speaker = None
        self._addressee = None
        self._prev_speaker = None

    @property
    def speaker(self) -> Optional[str]:
        """Current quoted-turn speaker head (deixis anchor for 1st-person), or None if unset."""
        return self._speaker

    @property
    def addressee(self) -> Optional[str]:
        """Current quoted-turn addressee head (deixis anchor for 2nd-person), or None if unset."""
        return self._addressee

    @property
    def prev_speaker(self) -> Optional[str]:
        """Prior turn's speaker head (dialogue turn-taking addressee fallback), or None."""
        return self._prev_speaker
