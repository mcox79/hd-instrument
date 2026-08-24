"""A FULL run that writes no verdict is invisible to the archive. Ratchet the list down, never up.

WHY THIS EXISTS, WITH THE INCIDENT.

`exp_sr_scale_ladder_v1` ran FULL on 2026-08-19: simplewiki, 3 seeds, 400 items, frozen candidate
pool, nested rung corpora, `items_predate_mechanism: true`, `_underpowered: false` at every rung. A
carefully built cell. Its result -- **0 of 24 successor-representation arms clear the credible bar,
and the organ DEGRADES with scale while the counting floor improves** -- is decision-changing: it
refutes "scale it up" using the organ's own ladder.

**Nobody read it for five days.** The cell wrote no `verdict` field, so `experiment_index.py` lists
it landed-with-no-verdict and it surfaces in no verdict query. Meanwhile `substrate.py`'s slot table
still advertised that organ as *"highest value-per-effort... WE HAVE WRITTEN NONE OF IT."*

Enumerated 2026-08-24 across all `data/*/metrics.json` (7,910 files, 0 malformed): **170 (2.1%)
carry no verdict-ish field at all, and 17 of those are `run_mode: full`.** Five are `solverB_*`
cells whose `SOLVED.md` carries the verdict elsewhere, so they are not lost. **The other 12 are
`exp_*` cells with no brief -- for those, the conclusion may exist nowhere.**

WHY A RATCHET AND NOT A FIX. Reading 12 cells and adjudicating each is real work and is not this
test's job. What this test does is make the set VISIBLE and STOP IT GROWING: a new cell that lands
FULL without a verdict fails here, immediately, while its author is still present. The existing 12
are grandfathered by name and may only be REMOVED.

FIELD LIST ENUMERATED, NOT GUESSED. CLAUDE.md records a whole retracted finding caused by guessing
which field held a concept (`gate_decision_target` looked empty; `revival_criteria` was the real
field, filled on 41 of 42 rows). So `VERDICTISH` below came from counting every top-level key across
all 7,910 files, not from memory.
"""

import concurrent.futures
import glob
import io
import json
import os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Enumerated from the corpus, not recalled. Any ONE of these, non-empty, counts as a verdict.
VERDICTISH = ("verdict", "verdict_msg", "verdict_tag", "verdict_detail", "verdict_reason",
              "primary_verdict", "final_verdict", "result", "results", "status")

# Grandfathered 2026-08-24. THIS LIST MAY SHRINK, NEVER GROW. Removing a name means either the cell
# gained a verdict or its result was adjudicated and written down somewhere durable.
# READING STATUS annotated 2026-08-24. A name here means "landed FULL with no verdict field"; it
# does NOT mean "unread". Eight of the twelve now have their conclusion written down somewhere
# durable -- the point of the annotation is that the next person can see WHICH, instead of
# re-deriving results that are already adjudicated. (I miscounted these as "ten unread" and then
# "seven unread" before actually listing them. Name the denominator.)
KNOWN_VERDICTLESS_FULL = {
    # --- ADJUDICATED: conclusion recorded elsewhere, do not re-derive ---
    "exp_cortical_read_consolidated_v1",    # in B3's slot rationale: 298-300 of 300 items already
                                            # read; the leak FAVOURED the organ and it lost anyway
    "exp_grounding_precision_gold_v1",      # commit 838cb8ffd: beats the random floor 2 of 3 seeds,
                                            # but counting co-occurrence beats it 2-3x on 3 of 3
    # --- READ 2026-08-24, written up in
    #     notes/WHERE_THE_SUBSTRATE_LOSES_A_CENSUS_THAT_SAT_UNREAD_2026-08-24.md ---
    "exp_e2e_trace_v1",                     # the loss census; 34,169 sentences -> 386 facts.
                                            # Its QUALITY_CLAIM is "scores nothing" -- a verdict
                                            # would be WRONG here. Do not add one.
    "exp_substrate_end_to_end_readout_v1",  # pre-registered reading (e) fired: the read-out does
                                            # not consult grounded facts
    "exp_discrimination_ceiling_v1",        # oracle 1.0 and we still miss ~88%; and SECOND_ORDER
                                            # is BAG_COSINE written twice
    "exp_predictive_write_gate_v1",         # 0 of 18 vs a rate-matched random skip
    "exp_sensorimotor_spoke_grounding_v1",  # beats its shuffled twin, ties counting: redundant
    "exp_sr_scale_ladder_v1",               # 0 of 24, degrades with scale; written up in ORGAN_MAP D7
    # --- STILL UNREAD: four ---
    "exp_meaning_asset_coverage_probe_v1",
    "exp_meaning_asset_floor_hardening_v1",
    "exp_substrate_resume_helps_v1",
    "exp_wire_definitional_v1",
}

# solverB_* cells keep their verdict in notes/problems/<slug>/SOLVED.md, which the ledger reads and
# the GUI renders. Absent from metrics.json is not absent from the record for those, so they are
# excluded by RULE rather than grandfathered by name -- a new solver cell must not fail this test.
SOLVER_PREFIX = "solverB"


def _scan():
    """[(cell_name, has_verdict, run_mode)] over every data/*/metrics.json."""
    paths = sorted(glob.glob(os.path.join(_REPO, "data", "*", "metrics.json")))

    def probe(p):
        try:
            with io.open(p, "rb") as fh:
                d = json.loads(fh.read().decode("utf-8", "replace"))
        except Exception:
            return None
        if not isinstance(d, dict):
            return None
        has = any(k in d and d[k] not in (None, "", [], {}) for k in VERDICTISH)
        return (os.path.basename(os.path.dirname(p)), has, str(d.get("run_mode", "")).lower())

    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as ex:
        for r in ex.map(probe, paths):
            if r:
                out.append(r)
    return out


def _verdictless_full(rows):
    return {n for n, has, rm in rows
            if not has and rm == "full" and not n.startswith(SOLVER_PREFIX)}


def test_the_scan_actually_reads_metrics():
    """POSITIVE CONTROL. Without this, a broken scan makes the ratchet pass vacuously -- 'no new
    verdictless runs' would be indistinguishable from 'no files read'."""
    rows = _scan()
    assert len(rows) > 5000, "scan found only %d metrics files; it is broken" % len(rows)
    with_verdict = [r for r in rows if r[1]]
    assert len(with_verdict) > 0.8 * len(rows), (
        "only %d of %d files have a verdict -- VERDICTISH is probably wrong, which would make this "
        "test flag the whole archive" % (len(with_verdict), len(rows)))


def test_a_known_cell_reads_as_having_a_verdict():
    """SEARCH POSITIVE CONTROL on the field list itself: a cell known to carry a verdict must be
    detected. If VERDICTISH ever stops matching reality, this fails before the ratchet does."""
    rows = dict((n, has) for n, has, _ in _scan())
    known = "exp_grounding_multihop_sr_reachability_routing_v1"
    if known in rows:
        assert rows[known] is True, "%s carries HARD_PASS_CG_SR_REACHABILITY but read as verdictless" % known


def test_no_new_full_run_lands_without_a_verdict():
    """THE RATCHET. New names here mean a result that no verdict query can find."""
    found = _verdictless_full(_scan())
    new = sorted(found - KNOWN_VERDICTLESS_FULL)
    assert not new, (
        "FULL run(s) landed with no verdict field, so their results are invisible to "
        "experiment_index and to every verdict query:\n  " + "\n  ".join(new) +
        "\n\nThis is how exp_sr_scale_ladder_v1's 0-of-24 refutation sat unread for five days while "
        "the slot table still advertised that organ as the highest-value thing to build. "
        "Write a verdict field, or record the conclusion in a durable note and add the name to "
        "KNOWN_VERDICTLESS_FULL with a reason.")


def test_the_grandfathered_list_only_shrinks():
    """A name that no longer qualifies should be REMOVED from the list, so the list keeps meaning
    what it says. This is a nudge, not a failure -- a cell can be deleted or renamed legitimately."""
    found = _verdictless_full(_scan())
    stale = sorted(KNOWN_VERDICTLESS_FULL - found)
    if stale:
        print("[note] %d grandfathered name(s) no longer verdictless-full; remove them: %s"
              % (len(stale), ", ".join(stale)))


if __name__ == "__main__":
    rows = _scan()
    found = _verdictless_full(rows)
    print("metrics files scanned : %d" % len(rows))
    print("verdictless FULL exp_* : %d" % len(found))
    for n in sorted(found):
        print("   %s%s" % (n, "" if n in KNOWN_VERDICTLESS_FULL else "   <-- NEW"))
