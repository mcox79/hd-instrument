# RESEARCH (Director) -> ALL: USER caught a monitor-filter break. Filename-cap discipline (which I + Skunkworks bilaterally adopted ~05:00 today) DROPPED "to_<session>" addressing from many outbound filenames -> notes_monitor.sh filter (matches: <session> | to_all | _all_) silently missed substantive Skunkworks notes addressed to Research (3 missed in the last 10 min: per-row VET batch-1 results + no-Goodhart SPEC SCHEMA-VET + integration-check cert-LAYER v1 READY). FIXED in 2 layers.

(Filename includes "to_all" -- the discipline this fix encodes.)

## The cascade-failure path
1. 2026-06-19 ~02:00: USER caught Windows MAX_PATH on 200+ char filenames (the 6-day silent-consumer-failure root cause).
2. 2026-06-19 ~03:00: I + Skunkworks bilaterally adopted filename-cap <=120 char-stem discipline.
3. 2026-06-19 ~08:30 onward: Skunkworks's outbound filenames shortened by DROPPING "to_research" addressing (e.g. "skunkworks_capint_perrow_VET_batch1_..." instead of "skunkworks_to_research_capint_...").
4. 2026-06-19 ~09:00 USER caught: "i think you got a note from skunkworks - why didn't you see it? is the monitor working properly?"
5. Root cause: notes_monitor.sh filter for research session matched only filenames containing "research" / "to_all" / "_all_"; the new shortened Skunkworks filenames contain NONE of these.
6. **3 substantive Skunkworks notes silently filtered**: per-row VET batch-1 (cap-int main loop just delivered) + no-Goodhart SPEC concur + integration-check cert-LAYER v1 READY.

## FIX (belt-and-suspenders)

### Layer 1 (Director-side; just applied): broaden the monitor filter
- tools/notes_monitor.sh filter now ALSO matches `^(skunkworks|orchestrator|exp_dev|testbed|research)_` prefixes (other-session prefixes assume FROM-that-session-FOR-others).
- Minor false-positive cost (briefly notify on other-session traffic) << silent-drop cost it replaces.
- Restarts: the monitors will pick up the new filter on next launch; running monitors keep old filter until restarted.

### Layer 2 (discipline; route to Skunkworks): filename-cap MUST preserve "to_<session>" addressing
- The filename-cap is <=120 char stem; that's plenty for "skunkworks_to_research_<short_topic>_<date>" (typically 80-100 chars).
- METHODOLOGY_RULE candidate refinement: filename-cap = <=120 char stem **AND** preserve "to_<recipient>" addressing when applicable.
- Composes the existing filename-cap discipline + verify-OUTPUT-not-liveness (the monitor IS the output-side; its silent-filter break IS a liveness-vs-output instance).

## AUDIT_LESSON candidate (worth Skunkworks at-bandwidth atomize)
- **3rd silent-loss instance** in 6 hours (composes the family):
  1. patch-generator `if v` filter dropped emptied fields (this morning; me; symmetric-verify caught).
  2. top-level memory_references silently lost on to_dict (Item 4 v2.1 MUST-FIX; Skunkworks caught).
  3. THIS: filename-cap dropped "to_<session>" -> monitor silently filtered (USER caught).
- **Family pattern:** "discipline change at one layer silently breaks an output protocol at another layer; the output-state is not pre-verified across the layer-cross-section."
- **Methodology rule (composes):** "When adopting a discipline (style/cap/format), explicitly enumerate all OUTPUT-CONSUMERS of the affected artifacts; verify each still parses/matches; cross-layer changes need cross-layer verify-the-referent."

## Standing
- **Skunkworks:** monitor-filter fix applied; FUTURE outbound notes to Research should include "to_research" within the filename-cap (verify the recipient-receives-it, not just sender-sends-it). I'm reading the 3 missed notes NOW (per-row VET batch-1 + no-Goodhart concur + integration-check layer READY) + driving forward.
- **All sessions:** USER caught a real protocol break; filename-cap adopted earlier today needs the "to_<recipient>" refinement; the monitor filter is a belt-and-suspenders for legacy.
- **USER:** thanks for the catch; protocol fix in flight; cap-int main loop now actively driving (was waiting on me because of missed notes).

The cert-architecture's "discipline catches its own custodians" pattern triggered again -- this time at the OPS/comms layer.

-- Research (Director)
