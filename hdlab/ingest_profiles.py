"""hdlab/ingest_profiles.py -- named LEAN INGEST PROFILES for reading a corpus FOR A PURPOSE.
Promoted VERBATIM (owner-DONE lean_ingest_profile_and_parallel_corpus_read_harness_for_scale, Q111 landing
2026-09-05) from experiments/exp_lean_ingest_profiles_v1.build_reader (+ ADDITIVE_DIMS / _ALL_ADDITIVE_OFF).

BRAIN FRAME (PINNED): the brain reads FOR A PURPOSE and engages only the machinery that purpose needs. The
who-did-what harvest core {events, entities, coref, timeline_frames, causal_links} is the obligatory parse +
role binding (~44% of a full read -- irreducible); the 9 additive downstream dimensions (timeline-register,
space, world-state, entity-states, goals, affect, belief, bound-event tokens, surprisal) are ADDITIVE
elaborations that each ONLY write their own SituationModel field and read the FINAL event set -- none feeds
back into sm.events (proven byte-identical: `selpref` == full on the harvest core, verified per-dim across 24
LitBank docs). So a lean profile that drops the additive dims is BYTE-IDENTICAL to the full read on the kept
dims, at a measured speedup (roles-keeping `selpref` ~2x; role-free `lean_floor` ~9x -- the parse is the floor,
so the speedup is per-profile, NOT one flat number). Glass-box, reuses the existing flag plumbing, NO LLM.

Profiles:
  full        the default reader (every dimension).
  selpref     events + parsed thematic roles; the 9 additive dims OFF. Byte-identical to full on the harvest
              core {events, entities, coref, timeline_frames, causal_links}. The selectional-preference harvest.
  lean_floor  = SituationReader.all_capabilities_off() -- no parse, positional roles. The fast role-free floor.
  <dim>_kept  selpref + exactly one additive dim (e.g. `affect_register_kept`) -- proves any dimension leans
              in/out and its output equals the full read on that dim.
"""
from __future__ import annotations

from hdlab.situation_reader import SituationReader

# The 9 additive downstream dimensions: {SituationModel field -> the reader kwarg(s) that produce it}.
# Each ONLY writes its own field and reads the final event set -- none feeds back into sm.events (proven
# byte-identical). Dropping all of them == the "selpref" profile.
ADDITIVE_DIMS = {
    "timeline_order":  {"timeline_register": True},
    "locations":       {"track_space": True},
    "world_state":     {"track_world_state": True, "densify_world_state": True},
    "entity_states":   {"bind_entity_states": True},
    "goal_register":   {"track_goals": True},
    "affect_register": {"track_affect": True},
    "belief":          {"track_belief": True},
    "event_tokens":    {"bind_event_tokens": True},
    "surprisal":       {"predict_surprisal": True},
}
_ALL_ADDITIVE_OFF = {}
for _d in ADDITIVE_DIMS.values():
    for _k in _d:
        _ALL_ADDITIVE_OFF[_k] = False

PROFILES = ["full", "selpref", "lean_floor"] + [d + "_kept" for d in ADDITIVE_DIMS]


def reader_for_profile(profile, gaz=None):
    """The authoritative profile builder. `full` = default reader; `selpref` = default minus the 9 additive
    dims; `lean_floor` = all_capabilities_off; `<dim>_kept` = selpref + that one additive dim. Byte-identical to
    the full read on the profile's kept dimensions (reuses the existing capability-flag plumbing)."""
    if profile == "full":
        return SituationReader(gaz=gaz)
    if profile == "selpref":
        return SituationReader(gaz=gaz, **_ALL_ADDITIVE_OFF)
    if profile == "lean_floor":
        return SituationReader.all_capabilities_off(gaz=gaz)
    if profile.endswith("_kept"):
        dim = profile[:-5]
        cfg = dict(_ALL_ADDITIVE_OFF)
        cfg.update(ADDITIVE_DIMS[dim])
        return SituationReader(gaz=gaz, **cfg)
    raise ValueError("unknown ingest profile %r (see hdlab.ingest_profiles.PROFILES)" % profile)
