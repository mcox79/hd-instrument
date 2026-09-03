"""reader_capabilities.py -- the DERIVED "what can the live reader do, and is it ON by default?" view.

WHY THIS EXISTS (2026-08-31): the assembly wires validated dimensions into hdlab.situation_reader
behind capability flags. UPDATE 2026-09-03 (owner-authorized flip): the net-positive flags are now
DEFAULT-ON (SituationReader() is the FULLY-CAPABLE reader; reader-QA agg 0.2903->0.3598). To reproduce
the historical WEAK reader, pass every flag False explicitly. A solver (or strategy) who measures a
floor/baseline must still know which flags are on -- but now the DEFAULT is the strong reader, so the
prior hazard (measuring against an artificially weak default) is INVERTED: an explicit-off baseline is
the one that understates. STILL DEFAULT-OFF: parser_arceager (19c-negative), causation_typed +
spacy_pred_gate (spaCy -> not remote-safe). This tool INTROSPECTS the constructor so the table is exact.
This tool is the single canonical, ROT-PROOF answer: it INTROSPECTS the reader's constructor for every
capability flag + its default, and cross-references the capability registry for what each does + its
witness. Run it before measuring anything against "the reader".

  python tools/reader_capabilities.py            # the manifest table
  python tools/reader_capabilities.py --enable    # the exact kwargs to build the FULLY-ON reader

Glass-box, no deps beyond stdlib + inspect on the reader signature. ASCII-only.
"""
from __future__ import annotations

import inspect
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

REG = os.path.join(_REPO, "data", "capability_registry.jsonl")

# The capability FLAGS (as opposed to tuning params). Each names the reader kwarg that turns a
# validated dimension ON. Descriptions are one-line; the AUTHORITATIVE detail is the registry entry
# (id) + the witness, both printed. Keeping the flag->id map here is the ONLY hand-maintained bit;
# everything else (default state, capability text, witness) is DERIVED.
CAP_FLAGS = {
    "tense_agnostic_events": "extraction_frontend_tense_agnostic_detector_v1",
    "preserve_tense": "preserve_tense_live_reader_v1",          # refines tense_agnostic_events (composed tense)
    "causation_typed": "causation_typed_live_reader_v1",
    "timeline_register": "timeline_register_live_reader_v1",
    "track_space": "track_space_live_reader_v1",                # SPACE dimension -> sm.locations
    "verb_subcat_gate": "verb_subcat_gate_live_reader_v1",      # who-did-what PRESENCE (suppress spurious patients)
    "predict_surprisal": "predict_surprisal_live_reader_v1",    # N400 surprisal -> EventRecord.patient_surprisal (error-risk flag)
    "track_belief": "belief_dimension_live_reader_v1",          # BELIEF/ToM -> sm.believes/sm.knows (the 5th dimension)
    "bind_event_tokens": "bound_event_token_backbone_live_reader_v1",  # the ASSEMBLY: sm.event_tokens + sm.episodic_store (the JOINT the silos can't store)
    "predict_revise": "predict_revise_live_reader_v1",          # parse-RECALL drop-fill: recover the DROPPED patient via relcl_resolver (EventRecord.patient_prerevise)
    "track_world_state": "world_state_dimension_live_reader_v1",  # mutable WORLD-STATE -> sm.world_state (who-has-what / open-closed at story-time t)
    "parser_arceager": "parser_arceager_route_live_reader_v1",    # route the WIRED who-did-what front end through the improved arc-eager parser (refines role_route='wired')
    # role_route is a string ("positional" = off; "wired"/other = the assembly who-did-what path)
    "role_route": None,
    "spacy_pred_gate": None,
}


def _reg_by_id():
    out = {}
    if not os.path.exists(REG):
        return out
    with open(REG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[e.get("id")] = e   # last wins
    return out


def _reader_defaults():
    from hdlab.situation_reader import SituationReader
    sig = inspect.signature(SituationReader.__init__)
    return {n: p.default for n, p in sig.parameters.items()
            if p.default is not inspect.Parameter.empty}


def manifest():
    defaults = _reader_defaults()
    reg = _reg_by_id()
    rows = []
    for flag, cap_id in CAP_FLAGS.items():
        if flag not in defaults:
            continue
        default = defaults[flag]
        # "off" = the byte-identical default; for role_route the off value is "positional"
        is_off = (default in (False, "positional", None))
        e = reg.get(cap_id) if cap_id else None
        cap = (e.get("name") if e else "(string mode flag; see role_route in situation_reader)") or ""
        witness = (e.get("witness") if e else "") or ""
        rows.append((flag, repr(default), "OFF" if is_off else "ON", cap_id or "-", cap, witness))
    return rows


def print_manifest():
    rows = manifest()
    print("=" * 100)
    print("LIVE READER CAPABILITY FLAGS -- default state (SituationReader() = net-positive flags ON since 2026-09-03)")
    print("=" * 100)
    for flag, default, state, cid, cap, witness in rows:
        print("\n[%s]  default=%s  -> %s" % (flag, default, state))
        print("   capability : %s" % (cap[:140]))
        if cid != "-":
            print("   registry   : %s" % cid)
        if witness:
            print("   witness    : %s" % witness)
    n_off = sum(1 for r in rows if r[2] == "OFF")
    n_on = len(rows) - n_off
    print("\n" + "-" * 100)
    print("SUMMARY: %d of %d capability flags are ON by default (flipped 2026-09-03); %d stay OFF (parser_arceager +"
          " the two spaCy flags). `SituationReader()` is now the FULLY-CAPABLE reader." % (n_on, len(rows), n_off))
    print("BEFORE MEASURING a floor/baseline against 'the reader', note the DEFAULT is now the STRONG reader; pass")
    print("flags False explicitly for the historical weak baseline. Disable-all: build_reader(capable=False).")
    print("NOTE: the fully-on default reader reproduces the reader-QA kept-stack aggregate 0.3598 (16 docs, 19c LitBank).")


def print_enable():
    print("# The FULLY-ON reader = the DEFAULT reader since the 2026-09-03 owner-authorized flip (SituationReader()).")
    print("# ✅ FLIPPED DEFAULT-ON 2026-09-03 (owner: 'switch them on, 1 at a time, top down, measure net positives').")
    print("# The greedy forward-activation sweep (tools/flag_activation_sweep.py) measured each flag one-at-a-time:")
    print("# reader-QA agg 0.2903 (all-off) -> 0.3598 (kept stack), NO real downstream regression (the apparent causal")
    print("# -0.23 under tense_agnostic_events is a MEASUREMENT artifact -- gold built from the densified sm.events,")
    print("# readout from flag-independent sm.causal_links; causal answers byte-identical). This SUPERSEDES the prior")
    print("# 2026-08-31 'no dimension flag should be flipped default-ON yet -- the fully-on reader is N parallel silos'")
    print("# caution, because bind_event_tokens (the JOINT binder) is now ALSO default-ON, so the dimensions BIND.")
    print("# ✅ FIXED 2026-09-01 (the_assembled_reader_is_parallel_silos..., p4 owner-DONE, EXCELLENT): the")
    print("# integration fix -- the TIERED bound-event-token backbone -- is now LANDED as the default-off")
    print("# bind_event_tokens flag: read() builds sm.event_tokens (ONE FHRR bound token per event = the JOINT")
    print("# the silos can't store) + sm.episodic_store (resolve/corefer readout). JOINT coref 1.000 vs late-")
    print("# fusion-of-marginals 0.600 CI-sep on old+modern text. Turning it ON is the integration; it was FLIPPED")
    print("# default-ON on 2026-09-03 (owner-authorized -- the JOINT binder). The remaining ecological lever is the")
    print("# FRONT-END role assignment (agent-role 0.271 while event recall 0.953), NOT more flags.")
    print("# ✅ FIXED 2026-08-31 (QA-instrument coupling): the QA capstone exp_situation_model_qa_v1 used to run the")
    print("# DEFAULT weak reader and read temporal off sm.events tense, which tense_agnostic_events rewrites to a")
    print("# placeholder -> temporal questions collapse 86->0. It now defaults to the CAPABLE reader (build_reader:")
    print("# tense_agnostic_events+preserve_tense+timeline_register) and reads temporal off the tense-independent")
    print("# sm.timeline_order -- the correct baseline. So: when scoring temporal, read sm.timeline_order, NOT the")
    print("# naive sm.events tense readout (witness verification/test_situation_model_qa.py).")
    print("SituationReader(")
    print("    tense_agnostic_events=True,   # event recall 0.33->0.95 (extraction keystone)")
    print("    preserve_tense=True,          # composed Reichenbach tense/is_pp (refines tense_agnostic_events; feeds TIME)")
    print("    causation_typed=True,         # typed CAUSE/ENABLE/PREVENT (sm.typed_causal_links)")
    print("    timeline_register=True,       # whole-passage chronological order (sm.timeline_order)")
    print("    track_space=True,             # SPACE / WHERE dimension (sm.locations; where_is/present_in_scene)")
    print("    verb_subcat_gate=True,        # who-did-what PRESENCE (suppress spurious patients on intransitives)")
    print("    role_route='wired',           # assembly who-did-what role routing (the one aggregate-positive flag)")
    print("    spacy_pred_gate=True,         # supplied-grammar predicate gate (changes the event set; measure it)")
    print("    bind_event_tokens=True,       # the ASSEMBLY: sm.event_tokens + sm.episodic_store (the JOINT the silos can't store)")
    print("    track_world_state=True,       # mutable WORLD-STATE / STATE dimension (sm.world_state; who-has-what / open-closed at t)")
    print(")")


if __name__ == "__main__":
    if "--enable" in sys.argv:
        print_enable()
    else:
        print_manifest()
