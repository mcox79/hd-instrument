#!/usr/bin/env python
"""Compose N ready-work queue items into N Agent-tool-ready briefs, boilerplate auto-composed.

WHY THIS EXISTS (2026-08-15, owner directive): hand-composing the mandatory per-brief
boilerplate (disclosure rule, no-spawn constraint, fragment-report convention, current
DO-NOT-TOUCH list) is itself friction that biases toward fewer, hand-typed dispatches. This
tool claims N items from tools/dispatch_queue.py's queue and prints N complete, self-contained
prompt bodies -- paste each one into a separate Agent tool_use block in the SAME message to get
real concurrent dispatch (the measured defect this whole effort responds to: 0/235 spawns in
the audited transcript ever batched more than one Agent call in a single message, see
notes/agent_usage_practices_audit_2026-08-14.md).

This tool does NOT call the Agent tool itself -- it has no access to it. It prepares text.
The dispatcher (a Director-role session) still issues the actual tool_use calls, in one message.

BOILERPLATE SOURCE (kept here, in ONE place, so it can be updated without touching every
queue item's brief field): the disclosure rule text is quoted VERBATIM from CLAUDE.md
"Every brief carries the disclosure rule". The DO-NOT-TOUCH list is read live from
data/dispatch_batch_do_not_touch.txt (one path per line) rather than hardcoded, so it can be
updated for a session without editing this script -- see that file's own header comment for
why it is not CLAUDE.md itself (CLAUDE.md is DO-NOT-TOUCH / concurrent writers this session).

USAGE
  python tools/dispatch_batch.py --count 4 --by director-2026-08-15
  python tools/dispatch_batch.py --ids metrics-triage-batch-00,organ-missing-d7 --by director-2026-08-15
  python tools/dispatch_batch.py --count 3 --category organ-missing --by director-2026-08-15
  python tools/dispatch_batch.py --count 4 --by X --dry-run     # preview, does NOT claim
  python tools/dispatch_batch.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import dispatch_queue as dq  # noqa: E402

DO_NOT_TOUCH_FILE = REPO_ROOT / "data" / "dispatch_batch_do_not_touch.txt"

DISCLOSURE_RULE = (
    "If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a "
    "variant, and do not silently proceed without the denied step. A dropped precondition "
    "invalidates the declared gate even when the result may be fine -- disclose, the operator "
    "decides. (Per CLAUDE.md 'Every brief carries the disclosure rule'.)"
)

NO_SPAWN_RULE = (
    "You may NOT spawn further sub-agents (no Agent tool calls from inside this dispatch). Do "
    "the work yourself. If the task is genuinely too large for one agent, say so in your report "
    "rather than fanning out further -- unmonitored recursive fan-out is a measured failure mode "
    "this session (a prior chain spawned 6 children with no surviving parent)."
)

FRAGMENT_RULE = (
    "Return your finding as PROSE in your final message, under 400 words unless the task "
    "explicitly says otherwise -- do not write a report .md file unless the task tells you to. "
    "The dispatching session reads your returned text, not files you create as a side effect."
)

# ---------------------------------------------------------------------------
# MANDATORY BRAIN-FIDELITY BLOCK (owner standing directive, 2026-08-15)
#
# THE OWNER'S WORDS, VERBATIM AND LOAD-BEARING:
#   "your response there is really important - you overlooked that key aspect about brain
#    fidelity - I want you to SOLIDIFY that sentiment - you need to approach every problem
#    with that consideration."
#   "I see you talking about exact-key retrieval only - wtf is that? we need to be doing
#    brain foundational things - not maximizing performance in single areas"
#   "the way we lose is by trying fancy available tools. The way we win is by understanding
#    exactly how the brain does it (which is NOT necessarily a trigram encoder), and
#    replicating it as exactly as we can."
#
# THE INCIDENT THAT EARNED IT (cited here so the rule is never unsourced prose): the landed
# capability hdlab/perirhinal_conjunctive.py was SHELVED with the revival criterion "exact-key
# retrieval only" -- a PERFORMANCE-ENGINEERING framing, in a project whose entire thesis is
# brain fidelity. The brain NEVER retrieves with an exact key; it COMPLETES FROM A PARTIAL CUE.
# The correct, brain-framed criterion is that conjunction is not testable until PATTERN
# COMPLETION (hippocampal CA3) sits in front of it, because separation (dentate gyrus) and
# completion (CA3) are a MATCHED PAIR. The engineering framing did not merely sound wrong: it
# would have shelved a component FOR THE WRONG REASON and hidden the actual missing organ. That
# is the cost being prevented -- a wrong frame closes a live research direction.
#
# The question this block forces is NOT "did we consider the brain?" It is "WHICH BRAIN
# STRUCTURE, and are we replicating it or substituting something convenient?"
#
# It lives HERE, in the composer, rather than in prose in a plan document, because prose is
# exactly what got overlooked. Every composed brief carries it by construction.
# ---------------------------------------------------------------------------
BRAIN_FIDELITY_RULE = (
    "The DEFAULT OPENING MOVE on ANY component is HOW DOES THE BRAIN DO THIS -- before "
    "surveying available tools, before measuring, before optimising what we already have. "
    "The question is never 'did we consider the brain?'; it is 'WHICH BRAIN STRUCTURE, and "
    "are we replicating it or substituting something convenient?'\n"
    "  For EACH component you touch, STATE ALL FOUR in your report:\n"
    "  (a) BRAIN STRUCTURE -- the neural system it corresponds to (hippocampal CA3, dentate "
    "gyrus, perirhinal cortex, DMN, TPJ, left IFG...), NOT a cognitive-theory label "
    "('working memory', 'attention', 'binding' are labels, not structures). If the "
    "literature does not pin it, write UNPINNED -- an honest UNPINNED beats an invented "
    "anatomy. UNPINNED does NOT mean stop: propose the best brain-motivated candidate and "
    "TEST it (USER 2026-08-15). What is barred is reaching for a convenient available tool "
    "INSTEAD of asking how the brain does it.\n"
    "  (b) ORGAN REUSE -- does this REUSE an organ we already own? The brain reuses circuits; "
    "a parallel build is BOTH unfaithful AND islanding. Query "
    "data/capability_registry.jsonl before building. Name the organ reused, or state why no "
    "existing organ serves.\n"
    "  (c) FIDELITY BASIS per design choice -- mark each as PINNED-BY-EVIDENCE (neuroscience "
    "or a measured result pins this shape/order/metric) or OUR-INVENTION-BEING-TESTED. "
    "Invention is AUTHORISED; presenting an invention as pinned is NOT.\n"
    "  (d) BRAIN-FRAMED SHELVE/REVIVAL -- if you SHELVE anything or write a revival "
    "criterion, the reason must be BRAIN-FRAMED, never performance-framed. 'Revive when "
    "exact-key retrieval is needed' is a performance frame and is REJECTED; 'not testable "
    "until pattern completion (CA3) sits in front of it, because separation (DG) and "
    "completion (CA3) are a matched pair' is the brain frame. A performance-framed shelve "
    "closes a live research direction for the wrong reason and hides the missing organ -- "
    "that is the measured incident this rule comes from (hdlab/perirhinal_conjunctive.py, "
    "2026-08-15)."
)


def _read_do_not_touch() -> list[str]:
    if not DO_NOT_TOUCH_FILE.exists():
        return []
    lines = []
    for line in DO_NOT_TOUCH_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def compose_brief(item: dict, do_not_touch: list[str]) -> str:
    dnt = ("\n\nDO NOT TOUCH this session (ask if your task seems to require touching one of "
           "these; do not route around silently): " + "; ".join(do_not_touch)) if do_not_touch else ""
    return (
        f"{item['brief']}\n\n"
        f"--- MANDATORY BOILERPLATE (do not skip) ---\n"
        f"DISCLOSURE: {DISCLOSURE_RULE}\n"
        f"NO-SPAWN: {NO_SPAWN_RULE}\n"
        f"BRAIN FIDELITY (MANDATORY, applies to every component you touch): {BRAIN_FIDELITY_RULE}\n"
        f"REPORT FORMAT: {FRAGMENT_RULE}"
        f"{dnt}\n\n"
        f"--- QUEUE PROVENANCE ---\n"
        f"queue id: {item['id']} | category: {item['category']} | priority: {item['priority']} | "
        f"source: {item['source']}\n"
        f"When done, the dispatcher will run: "
        f"python tools/dispatch_queue.py done {item['id']}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queue", default=str(dq.DEFAULT_QUEUE))
    ap.add_argument("--count", type=int, default=0, help="claim up to N unclaimed items")
    ap.add_argument("--ids", default="", help="comma-separated explicit item ids instead of --count")
    ap.add_argument("--category", default=None, choices=sorted(dq.CATEGORIES))
    ap.add_argument("--by", default=None, help="claimant name (required unless --dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="preview without claiming")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.dry_run and not args.by:
        print("[dispatch_batch] --by is required unless --dry-run", file=sys.stderr)
        return 2

    path = Path(args.queue)
    do_not_touch = _read_do_not_touch()

    if args.ids:
        target_ids = [s.strip() for s in args.ids.split(",") if s.strip()]
    else:
        if args.count <= 0:
            print("[dispatch_batch] need --count N or --ids a,b,c", file=sys.stderr)
            return 2
        pool = dq.load_items(path)
        pool = [it for it in pool if it["status"] == "unclaimed"]
        if args.category:
            pool = [it for it in pool if it["category"] == args.category]
        # Priority order H > M > L, stable within a category.
        order = {"H": 0, "M": 1, "L": 2}
        pool.sort(key=lambda it: order.get(it["priority"], 9))
        target_ids = [it["id"] for it in pool[: args.count]]

    if not target_ids:
        print("[dispatch_batch] no matching unclaimed items found", file=sys.stderr)
        return 1

    briefs = []
    for item_id in target_ids:
        items = dq.load_items(path)
        item = next((it for it in items if it["id"] == item_id), None)
        if item is None:
            print(f"[dispatch_batch] WARNING no such id, skipping: {item_id}", file=sys.stderr)
            continue
        if not args.dry_run:
            try:
                item = dq.claim(path, item_id, args.by)
            except (KeyError, dq.QueueLockError) as e:
                print(f"[dispatch_batch] WARNING could not claim {item_id}: {e}", file=sys.stderr)
                continue
        briefs.append(item)

    if not briefs:
        print("[dispatch_batch] nothing claimed -- all candidates were already taken", file=sys.stderr)
        return 1

    for i, item in enumerate(briefs, 1):
        print(f"\n===== BRIEF {i}/{len(briefs)} -- queue id: {item['id']} "
              f"({'DRY-RUN, not claimed' if args.dry_run else 'claimed by ' + args.by}) =====\n")
        print(compose_brief(item, do_not_touch))

    print(f"\n[dispatch_batch] {len(briefs)} brief(s) ready. Paste each into a separate Agent "
          f"tool_use block IN THE SAME MESSAGE for real concurrent dispatch.", file=sys.stderr)
    return 0


def _self_test() -> int:
    import tempfile
    ok = True
    tmp_dir = Path(tempfile.mkdtemp(prefix="dispatch_batch_selftest_"))
    qpath = tmp_dir / "queue.jsonl"

    seed = [
        dq._mk("s1", "metrics-triage", "T1", "Brief text 1", "H", "src1"),
        dq._mk("s2", "atom-triage", "T2", "Brief text 2", "M", "src2"),
        dq._mk("s3", "organ-missing", "T3", "Brief text 3", "L", "src3"),
    ]
    dq.add_items(qpath, seed)

    # 1. --count claims exactly N and returns N composed briefs, priority-ordered
    rc = main(["--queue", str(qpath), "--count", "2", "--by", "selftest-agent"])
    if rc == 0:
        items_after = dq.load_items(qpath)
        claimed = [it for it in items_after if it["status"] == "claimed"]
        if len(claimed) == 2 and {it["id"] for it in claimed} == {"s1", "s2"}:
            print("[self-test] PASS --count 2 claims the 2 highest-priority unclaimed items")
        else:
            print(f"[self-test] FAIL wrong items claimed: {[it['id'] for it in claimed]}", file=sys.stderr)
            ok = False
    else:
        print("[self-test] FAIL main() returned nonzero on a normal --count run", file=sys.stderr)
        ok = False

    # 2. a second --count call (asking for more than remain) claims only the REMAINING
    #    unclaimed item (s3) and does not touch s1/s2's existing ownership.
    rc2 = main(["--queue", str(qpath), "--count", "5", "--by", "selftest-agent-2"])
    items_after2 = dq.load_items(qpath)
    by_id = {it["id"]: it for it in items_after2}
    if (by_id["s1"]["claimed_by"] == "selftest-agent" and by_id["s2"]["claimed_by"] == "selftest-agent"
            and by_id["s3"]["claimed_by"] == "selftest-agent-2"):
        print("[self-test] PASS already-claimed items keep their original owner; only the "
              "genuinely-unclaimed remainder goes to the second batch call")
    else:
        print(f"[self-test] FAIL ownership after second call: "
              f"{[(k, v['claimed_by']) for k, v in by_id.items()]}", file=sys.stderr)
        ok = False

    # 3. --dry-run does not mutate queue state
    qpath2 = tmp_dir / "queue2.jsonl"
    dq.add_items(qpath2, [dq._mk("d1", "metrics-triage", "T", "B", "M", "src")])
    main(["--queue", str(qpath2), "--count", "1", "--dry-run"])
    still = dq.load_items(qpath2)
    if still[0]["status"] == "unclaimed":
        print("[self-test] PASS --dry-run does not claim")
    else:
        print("[self-test] FAIL --dry-run mutated queue state", file=sys.stderr)
        ok = False

    # 4. composed brief carries disclosure + no-spawn + report-format + provenance
    brief_text = compose_brief(dq.load_items(qpath2)[0], ["notes/STATUS.md", "CLAUDE.md"])
    checks = [
        ("STOP and report the exact denial text verbatim" in brief_text, "disclosure rule present"),
        ("may NOT spawn further sub-agents" in brief_text, "no-spawn rule present"),
        ("under 400 words" in brief_text, "report-format rule present"),
        ("notes/STATUS.md" in brief_text and "CLAUDE.md" in brief_text, "do-not-touch list present"),
        ("queue id: d1" in brief_text, "queue provenance present"),
        # --- MANDATORY BRAIN-FIDELITY BLOCK (2026-08-15) ---
        # Asserted clause-by-clause, not as one "is the block present" check: the whole point
        # of the incident is that a rule can be nominally present and still not carry the
        # part that would have caught the defect. Each of (a)-(d) is checked on its own.
        ("HOW DOES THE BRAIN DO THIS" in brief_text,
         "brain-fidelity: default-opening-move clause present"),
        ("WHICH BRAIN STRUCTURE, and are we replicating it or substituting something convenient?"
         in brief_text, "brain-fidelity: the framing question present verbatim"),
        ("(a) BRAIN STRUCTURE" in brief_text and "NOT a cognitive-theory label" in brief_text,
         "brain-fidelity (a): names a NEURAL STRUCTURE, not a cognitive-theory label"),
        ("(b) ORGAN REUSE" in brief_text and "capability_registry.jsonl" in brief_text,
         "brain-fidelity (b): organ-reuse requirement + registry query present"),
        ("PINNED-BY-EVIDENCE" in brief_text and "OUR-INVENTION-BEING-TESTED" in brief_text,
         "brain-fidelity (c): both fidelity-basis markers present"),
        ("BRAIN-FRAMED SHELVE/REVIVAL" in brief_text and "never performance-framed" in brief_text,
         "brain-fidelity (d): brain-framed shelve/revival requirement present"),
        ("perirhinal_conjunctive" in brief_text,
         "brain-fidelity: the earning INCIDENT is cited inline (rule is never unsourced prose)"),
        ("exact-key retrieval" in brief_text and "REJECTED" in brief_text,
         "brain-fidelity: the rejected performance framing is quoted as the negative example"),
        ("CA3" in brief_text and ("dentate gyrus" in brief_text.lower() or "(DG)" in brief_text),
         "brain-fidelity: the CORRECT brain-framed criterion (DG/CA3 matched pair) is shown"),
        ("UNPINNED" in brief_text and "does NOT mean stop" in brief_text,
         "brain-fidelity: UNPINNED-is-honest but does-not-mean-stop clause present"),
    ]
    for passed, label in checks:
        if passed:
            print(f"[self-test] PASS {label}")
        else:
            print(f"[self-test] FAIL missing: {label}", file=sys.stderr)
            ok = False

    # 4b. NEGATIVE CONTROL for the brain-fidelity block -- a check that cannot fail is not a
    # check. This project has shipped multiple guards that silently did nothing, so the
    # assertions in (4) are re-run against a brief composed WITHOUT the block; every one of
    # them MUST flip to False. If any survives, that assertion is matching incidental text
    # somewhere else in the boilerplate and is not actually testing the block.
    stripped = brief_text.replace(BRAIN_FIDELITY_RULE, "")
    bf_labels = [lab for _, lab in checks if lab.startswith("brain-fidelity")]
    bf_preds_on_stripped = [
        "HOW DOES THE BRAIN DO THIS" in stripped,
        "WHICH BRAIN STRUCTURE, and are we replicating it or substituting something convenient?" in stripped,
        "(a) BRAIN STRUCTURE" in stripped and "NOT a cognitive-theory label" in stripped,
        "(b) ORGAN REUSE" in stripped and "capability_registry.jsonl" in stripped,
        "PINNED-BY-EVIDENCE" in stripped and "OUR-INVENTION-BEING-TESTED" in stripped,
        "BRAIN-FRAMED SHELVE/REVIVAL" in stripped and "never performance-framed" in stripped,
        "perirhinal_conjunctive" in stripped,
        "exact-key retrieval" in stripped and "REJECTED" in stripped,
        "CA3" in stripped and ("dentate gyrus" in stripped.lower() or "(DG)" in stripped),
        "UNPINNED" in stripped and "does NOT mean stop" in stripped,
    ]
    survivors = [lab for lab, still_true in zip(bf_labels, bf_preds_on_stripped) if still_true]
    if survivors:
        print(f"[self-test] FAIL negative control: {len(survivors)} brain-fidelity assertion(s) "
              f"still pass with the block REMOVED, so they do not test it: {survivors}",
              file=sys.stderr)
        ok = False
    else:
        print(f"[self-test] PASS negative control: all {len(bf_labels)} brain-fidelity "
              f"assertions flip to FAIL when the block is removed (they test the block, "
              f"not incidental boilerplate text)")

    # 5. --by required unless --dry-run
    rc3 = main(["--queue", str(qpath2), "--count", "1"])
    if rc3 == 2:
        print("[self-test] PASS missing --by (without --dry-run) is refused")
    else:
        print("[self-test] FAIL missing --by was not refused", file=sys.stderr)
        ok = False

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {tmp_dir}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
