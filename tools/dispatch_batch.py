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
    ]
    for passed, label in checks:
        if passed:
            print(f"[self-test] PASS {label}")
        else:
            print(f"[self-test] FAIL missing: {label}", file=sys.stderr)
            ok = False

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
