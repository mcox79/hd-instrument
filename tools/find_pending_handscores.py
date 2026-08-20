"""Every landed cell whose verdict is waiting on a HUMAN hand-score that may never have happened.

WHY. Twice on 2026-08-20 I found one by accident:
  * `exp_definitional_grounding_v3/_v5` -- `STRUCTURAL_PASS_PENDING_B3`, two 50-row pre-registered
    samples marked `NOT_AUTO_SCORED`, untouched for 8 days. Scored: it settled that the definitional
    HEAD route is not distinguishable from the distributional control.
  * `exp_structured_comparator_v1` -- `STRUCTURAL_PASS_PENDING_HANDSCORE`, a 100-row blind sample
    plus its key, untouched for 7 days. Scored: the structured comparator is significantly WORSE
    than the bag-of-words it was built to replace.

**Both were the ONLY missing input to a landed cell's verdict, and both answered a question the
project was still treating as open.** Finding the second one by accident is the signal that this
should be a list rather than a lucky grep.

WHAT IT DOES. Enumerates FROM THE FILESYSTEM (`data/*/metrics.json`), not from any index -- the
standing rule is enumerate from disk, then reconcile. For each cell it reports:
  * a verdict that names a pending human score;
  * the sample artefacts present (`blind_sample`, `*audit_sample*`, `SCORING_SHEET*`, `arm_key*`);
  * whether anything that looks like a COMPLETED score exists beside them
    (`*_joined_verdicts*`, `*scored*`, `*verdicts*`).

**IT DOES NOT OPEN ANY `arm_key*` FILE.** It only records that one exists. Reading a key before its
sample is scored destroys the blinding as thoroughly as editing it, and the harness forbids editing
those files for that reason.

**A cell is only reported as UNSCORED when a sample exists and no completed-score artefact sits
beside it** -- so the output is a worklist, not a census of every pending string.
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(_REPO, "data")

PENDING_TOKENS = ("PENDING_HANDSCORE", "PENDING_B3", "PENDING_HAND_SCORE", "AWAITING_HANDSCORE",
                  "PENDING_HUMAN")
SAMPLE_HINTS = ("blind_sample", "audit_sample", "scoring_sheet", "handscore", "hand_score")
SCORED_HINTS = ("joined_verdicts", "scored", "verdicts", "handscore_result",
                # A completed hand-score is recorded BESIDE the evidence as
                # `_handscore_verdict_<date>.json` rather than by rewriting the landed
                # metrics.json -- the standing discipline. Without this hint the tool keeps
                # listing cells that HAVE been answered, which is how a worklist rots.
                "handscore_verdict")
KEY_HINTS = ("arm_key",)


def main() -> int:
    if not os.path.isdir(DATA):
        print("no data/ directory at %s" % DATA)
        return 1
    rows = []
    for name in sorted(os.listdir(DATA)):
        d = os.path.join(DATA, name)
        mpath = os.path.join(d, "metrics.json")
        if not os.path.isdir(d) or not os.path.exists(mpath):
            continue
        try:
            with open(mpath, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception:
            continue
        verdict = str(m.get("verdict") or "")
        blob = json.dumps(m)[:4000].upper()
        pending = any(t in verdict.upper() for t in PENDING_TOKENS) or \
            any(t in blob for t in PENDING_TOKENS)
        if not pending:
            continue
        try:
            files = os.listdir(d)
        except OSError:
            continue
        low = [f.lower() for f in files]
        samples = [f for f, l in zip(files, low) if any(h in l for h in SAMPLE_HINTS)]
        scored = [f for f, l in zip(files, low) if any(h in l for h in SCORED_HINTS)]
        keys = [f for f, l in zip(files, low) if any(h in l for h in KEY_HINTS)]
        rows.append((name, verdict, samples, scored, keys))

    print("=" * 92)
    print("CELLS WHOSE VERDICT NAMES A PENDING HUMAN HAND-SCORE (enumerated from data/ on disk)")
    print("=" * 92)
    if not rows:
        print("none found")
        return 0

    unscored = [r for r in rows if r[2] and not r[3]]
    have_scores = [r for r in rows if r[2] and r[3]]
    no_sample = [r for r in rows if not r[2]]

    print("\n### UNSCORED -- a sample exists and NOTHING beside it looks like a completed score."
          "\n### THIS IS THE WORKLIST. %d cell(s)." % len(unscored))
    for name, verdict, samples, _sc, keys in unscored:
        print("\n  %s" % name)
        print("      verdict: %s" % verdict[:88])
        print("      sample : %s" % ", ".join(samples[:4]))
        if keys:
            print("      key    : %s  (present, NOT opened by this tool)" % ", ".join(keys))

    print("\n### HAS A SAMPLE *AND* SOMETHING SCORE-SHAPED BESIDE IT -- probably done, verify "
          "before rescoring. %d cell(s)." % len(have_scores))
    for name, verdict, samples, sc, _k in have_scores:
        print("  %-46s %s | scored-looking: %s" % (name, verdict[:34], ", ".join(sc[:3])))

    print("\n### PENDING STRING BUT NO SAMPLE FILE FOUND -- the verdict may be stale prose, or the "
          "sample lives elsewhere. %d cell(s)." % len(no_sample))
    for name, verdict, _s, _sc, _k in no_sample[:20]:
        print("  %-46s %s" % (name, verdict[:44]))
    if len(no_sample) > 20:
        print("  ... and %d more" % (len(no_sample) - 20))

    print("\nNOTE: 'scored-looking' is a FILENAME heuristic, not proof. Both cells found by hand "
          "today\n      needed the file opened to confirm which arms the verdicts attached to -- in "
          "one case a\n      SCORING_SHEET.txt shared only 50 of 100 rows with the scored set and "
          "attached to the\n      WRONG arms entirely.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
