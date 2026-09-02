"""world_state_entity_binding -- the brain-foundational STAGE-1 reference-resolution dispatcher that turns a
raw participant mention into a canonical DISCOURSE-ENTITY key, so the mutable world-state register keys
possession on the ENTITY (Glenberg, Meyer & Lindem 1987), not the surface word. For the problem
`the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what`.

BRAIN MODEL (PINNED). Comprehension binds a participant to a persistent entity node in TWO stages that the
literature keeps distinct (Kaplan 1989; Levinson 1983; Grosz-Joshi-Weinstein 1995; Zwaan & Radvansky 1998):
  STAGE 1  reference resolution -- BIFURCATED, dispatched by mention type:
    (0) PLEONASTIC/EXPLETIVE 'it' filter (Lappin & Leass 1994): "it takes courage" has NO referent -> ABSTAIN.
    (1) INDEXICAL route (1st-person singular I/me/my): O(1) speech-role lookup -> the NARRATOR node (the
        deictic origo; Buhler; Deictic Shift Theory). Monologic-PINNED; case-invariant (I == me == my).
    (2) ANAPHORIC route (3rd-person he/she): O(n) Centering salience search -> a coref entity cluster. REUSE
        the reader's OWN resolver (hdlab.event_centrality_coref); this dispatcher just consumes its output.
    (3) OBJECT ANAPHORA (it/them): the SAME Centering machinery, entity-type-agnostic -> the salient recent
        THEME. Needs the pleonastic filter (0) first.
    (4) NOMINAL name -> its (aliased) canonical head.
  STAGE 2  entity-state update -- UNIFIED (Gernsbacher structure-building); this is the world_state_register,
    which is already faithful. This module is Stage-1 ONLY.

SCOPED OUT, NAMED (research drill 2026-09-01, so they are not silent gaps): 'we' is a GROUP entity (split-
antecedent/mereological), 'you' is a ROTATING addressee role (per speech-turn), and QUOTED 'I' opens an
EMBEDDED deictic center (re-anchors to the quoted speaker). None is the singular pinned case; each ABSTAINS
here rather than binding wrongly (never-confidently-wrong).

GLASS-BOX: pure symbolic dispatch; NO external LLM, NO network. ASCII only. Deterministic.
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

NARRATOR = "~NARRATOR"

FIRST_SG = {"i", "me", "my", "mine", "myself"}                 # (1) indexical -> NARRATOR
HE_SHE = {"he", "him", "his", "she", "her", "hers"}            # (2) anaphoric (reader coref scope)
OBJ_PRON = {"it", "them", "they", "its"}                       # (3) object anaphora
SCOPE_OUT = {"we", "us", "our", "ours", "ourselves",           # 'we' group entity
             "you", "your", "yours", "yourself", "yourselves"}  # 'you' rotating addressee

# expletive/pleonastic 'it' predicates (Lappin-Leass style, transfer-verb subset): 'it takes/gives/... <abstract>'
# When 'it' is the SUBJECT of these, or 'it' has no nominal antecedent, treat as non-referential.
PLEONASTIC_VERBS = {"take", "takes", "took", "give", "gives", "gave", "cost", "costs", "require", "requires"}


class EntityBinder:
    """Stateful per-DOCUMENT Stage-1 dispatcher. Feed it participants in reading order; it maintains the salient
    recent nominal theme (Centering-lite) for object anaphora. Glass-box: every decision returns (key, route)."""

    def __init__(self, narrator_key: str = NARRATOR):
        self.narrator = narrator_key
        self.recent_nominal_theme: Optional[str] = None
        self.stats = Counter()

    # -- classification (glass-box) ---------------------------------------
    @staticmethod
    def route_of(head: Optional[str]) -> str:
        if head is None:
            return "none"
        h = head.lower()
        if h in FIRST_SG:
            return "indexical"
        if h in HE_SHE:
            return "anaphoric"
        if h in OBJ_PRON:
            return "object_anaphora"
        if h in SCOPE_OUT:
            return "scope_out"
        return "nominal"

    def is_pleonastic_it(self, head: str, verb: Optional[str], role: str) -> bool:
        """'it' is non-referential when it is a SUBJECT of an expletive-frame transfer verb, or (as an object)
        has no salient nominal antecedent to bind to."""
        if head.lower() != "it":
            return False
        if role == "agent" and verb and verb.lower() in PLEONASTIC_VERBS:
            return True
        if role in ("theme", "object") and self.recent_nominal_theme is None:
            return True
        return False

    # -- binding ----------------------------------------------------------
    def bind_participant(self, head: Optional[str], coref_cluster: Optional[object] = None,
                         verb: Optional[str] = None, coref_entropy: Optional[float] = None,
                         abstain_tau: Optional[float] = None) -> tuple:
        """Bind a HOLDER-role participant (agent/recipient/source): a person-ish entity. Returns (key, route).
        coref_cluster = the reader's OWN he/she resolution for this mention (None if it did not resolve).
        CONFIDENCE-ABSTAIN (brain-faithful defer, Nieuwland & Van Berkum 2008): if the anaphoric resolver supplies a
        calibrated ENTROPY and it exceeds abstain_tau, DEFER (return None) rather than write a low-confidence holder --
        a wrong holder is worse than 'unknown' for downstream state tracking. Default (no entropy/tau) = commit."""
        r = self.route_of(head)
        if r == "indexical":
            self.stats["indexical"] += 1
            return self.narrator, "indexical"       # indexical is O(1), never uncertain -> no abstain
        if r == "anaphoric":
            if coref_cluster is None:
                self.stats["anaphoric_unresolved"] += 1
                return None, "anaphoric_abstain"    # reader coref abstained -> never-confidently-wrong
            if abstain_tau is not None and coref_entropy is not None and coref_entropy > abstain_tau:
                self.stats["anaphoric_low_conf_abstain"] += 1
                return None, "anaphoric_low_conf_abstain"   # defer on uncertain coref (the confidence gate)
            self.stats["anaphoric_resolved"] += 1
            return "C%s" % coref_cluster, "anaphoric"
        if r == "object_anaphora":                  # a person-role 'they'/'them' (rare) -> abstain (needs person coref)
            self.stats["participant_objpron_abstain"] += 1
            return None, "abstain"
        if r == "scope_out":
            self.stats["scope_out_abstain"] += 1
            return None, "scope_out"                 # we/you -> group/addressee, not built
        if r == "nominal":
            self.stats["nominal"] += 1
            return head.lower(), "nominal"
        return None, "none"

    def bind_theme(self, head: Optional[str], verb: Optional[str] = None) -> tuple:
        """Bind an OBJECT-role participant (theme). Object anaphora: it/them -> salient recent nominal theme
        (unless pleonastic). Updates the salient theme on a nominal. Returns (key, route)."""
        if head is None:
            return None, "none"
        r = self.route_of(head)
        if r == "object_anaphora":
            if self.is_pleonastic_it(head, verb, "theme"):
                self.stats["pleonastic_it_abstain"] += 1
                return None, "pleonastic_abstain"
            if self.recent_nominal_theme is not None:
                self.stats["object_anaphora_resolved"] += 1
                return self.recent_nominal_theme, "object_anaphora"
            self.stats["object_anaphora_noantecedent"] += 1
            return head.lower(), "object_raw"
        # nominal theme -> canonical head + becomes the salient recent theme (Centering Cf update)
        if r == "nominal":
            self.recent_nominal_theme = head.lower()
            self.stats["theme_nominal"] += 1
            return head.lower(), "nominal"
        if r == "indexical":                          # first-person object ("gave ME to..." -- rare) -> narrator
            return self.narrator, "indexical"
        return (head.lower() if head else None), r


def self_test() -> int:
    ok = True
    b = EntityBinder()
    # (1) indexical: I == me == my -> one narrator node
    k_i, _ = b.bind_participant("I")
    k_me, _ = b.bind_participant("me")
    k_my, _ = b.bind_participant("my")
    c1 = k_i == k_me == k_my == NARRATOR
    ok &= c1
    print("[self-test] indexical I/me/my collapse to narrator: %s (%s)" % (c1, k_i), flush=True)
    # (2) anaphoric he/she -> given cluster, or abstain
    k_he, r_he = b.bind_participant("he", coref_cluster=5)
    k_he0, r_he0 = b.bind_participant("she", coref_cluster=None)
    c2 = (k_he == "C5" and r_he == "anaphoric") and (k_he0 is None and r_he0 == "anaphoric_abstain")
    ok &= c2
    print("[self-test] anaphoric he->C5, unresolved she->abstain: %s" % c2, flush=True)
    # (2b) CONFIDENCE-ABSTAIN: commit a low-entropy resolution, DEFER a high-entropy one (brain-faithful defer)
    k_lo, _ = b.bind_participant("he", coref_cluster=5, coref_entropy=0.1, abstain_tau=0.5)
    k_hi, r_hi = b.bind_participant("he", coref_cluster=5, coref_entropy=0.9, abstain_tau=0.5)
    c2b = (k_lo == "C5") and (k_hi is None and r_hi == "anaphoric_low_conf_abstain")
    ok &= c2b
    print("[self-test] confidence-abstain: low-entropy commits (C5), high-entropy DEFERS: %s" % c2b, flush=True)
    # (3) object anaphora with pleonastic filter + Centering antecedent
    b2 = EntityBinder()
    kt0, rt0 = b2.bind_theme("it")               # no antecedent yet -> pleonastic abstain
    kt1, _ = b2.bind_theme("cup")                # nominal -> salient theme
    kt2, rt2 = b2.bind_theme("it")               # now resolves to cup
    c3 = (kt0 is None and rt0 == "pleonastic_abstain") and (kt1 == "cup") and (kt2 == "cup" and rt2 == "object_anaphora")
    ok &= c3
    print("[self-test] object 'it': pleonastic-abstain w/o antecedent, then ->cup: %s" % c3, flush=True)
    # (4) scope-outs abstain (never confidently wrong)
    kw, rw = b2.bind_participant("we")
    ky, ry = b2.bind_participant("you")
    c4 = kw is None and ky is None and rw == "scope_out" and ry == "scope_out"
    ok &= c4
    print("[self-test] we/you abstain (group/addressee, not built): %s" % c4, flush=True)
    # (5) expletive 'it takes' subject -> pleonastic
    c5 = b2.is_pleonastic_it("it", "takes", "agent")
    ok &= c5
    print("[self-test] expletive 'it takes' subject -> pleonastic: %s" % c5, flush=True)
    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
