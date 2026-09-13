"""tools/solver_agent_prompt.py -- emit the kick-off prompt for a SOLVER AGENT (the owner-run solver session, as an agent).

WHY (2026-09-13, owner): the four owner-run opus solver sessions were guided by a fixed four-step script; the owner asked strategy to
run solver sessions as agents. Every launch must carry the SAME prompt shape so sessions are comparable: the brief (read from disk,
verbatim), the hard rules (files / commits / cores / denials / no fan-out / no off-the-shelf tools), and the six MANDATORY PHASES that
replace the owner's guidance messages (read -> build+measure -> status probe -> quality push -> verdict check with path A -> finalize).
Plan: notes/SOLVER_SUPERVISOR_PLAN_2026-09-13.md; day plan: notes/DAY_PLAN_2026-09-13_solver_agents.md.

Usage: python tools/solver_agent_prompt.py <slug> [--organ-note "another solver works on X"] [--patch-name attachment_arm_patch.diff]
Prints the prompt to stdout (paste into the Agent tool: model opus, subagent_type general-purpose, run_in_background true).
"""
from __future__ import annotations

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS = os.path.join(REPO, "notes", "problems")

HARD_RULES = (
    "HARD RULES: write ONLY the files the brief names (section 7) plus files under data/exp_*/ that your experiment's get_output_dir "
    "creates{extra_files}; NEVER edit existing hdlab/ or tools/ files (propose a patch .diff); NEVER edit preregs/** or any arm_key* "
    "file; NEVER run `git add -A`, never a bare `git commit`, never push -- commit PATH-LIMITED only (`git commit -m \"...\" -- <your "
    "files>`; `git add -f` is allowed for your own files), and end every commit message with the line: Co-Authored-By: Claude Fable "
    "5.1 <noreply@anthropic.com>. Cap cores on EVERY run (prefix: OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 "
    "PYTHONHASHSEED=0). If a tool call is DENIED: stop and report the denial text verbatim; do not retry a variant, and do NOT perform the same check or step another way (a different tool achieving the denied thing is a variant) -- leave that step undone and say so. Do NOT fan out to "
    "sub-agents; do all work yourself. Do NOT use spaCy / nltk taggers / any supervised parser / any external LLM at inference or as a "
    "teacher; offline foundation assets (norms, WordNet) are admissible at BUILD time only -- ship a dict. Never quote retired figures "
    "(notes/reference_retired_claims_never_requote.md).{organ_note}"
)

PHASES = (
    "MANDATORY PHASES -- execute ALL SIX yourself, in order, in this one task; do not end your turn before phase 6 is complete:\n"
    "1. READ: the brief's verify-before-you-start files in full; restate the bar in your own words; list the upstream chain "
    "(categories -> lemma -> heads -> roles -> the consumer) with the brain-foundational status of each rung as the disk shows it.\n"
    "2. BUILD the brain's mechanism (the opening move: how does the BRAIN do this? name the structure and the computation; replicate "
    "the OPERATION, sweep the parameters, never adopt a number); get the first MEASURED result with the floor the brief names, an "
    "information-free twin, and a bootstrap CI paired over items; the brief's no-regress populations measured alongside.\n"
    "3. STATUS PROBE -- answer this in writing, with numbers, then act on it: \"how are we performing against the brain, and where do "
    "we lose signal upstream? are all upstream components brain-foundational?\" -- concretely (owner mandate): (a) TRACK EXACTLY WHERE "
    "THE SIGNAL IS LOST, chain by chain: for the signal your end read needs, walk every upstream organ and write what each hand-off "
    "produces, what the next rung reads, and what is LOST, with counts; (b) CONFIRM the brain-foundational status of each upstream "
    "component AS IT RELATES TO THAT SIGNAL (a graded signal handed down, or a point estimate / a conflated value?); (c) RESEARCH how the "
    "brain handles that signal MATHEMATICALLY along each chain on down, cite it, compare it with what is built -- this isolates the loss "
    "and almost always exposes several fixes; build and measure them.\n"
    "4. QUALITY PUSH -- \"go after the remaining opportunities, BF and right not easy\": at least one more lever, built and measured "
    "the same way.\n"
    "5. VERDICT CHECK against the rubric: witness green; the twin loses CI-separated; the brief's completion bar met CI-separated on "
    "the item's own population; no-regress populations hold; knowledge in counts/assets with an online observe path. If the result is "
    "PARTIAL: write \"what would it take to make this fully solved\", pick the cheapest path (path A), TRY IT ONCE, re-measure. "
    "RESEARCH EVERY NEGATIVE you encountered until it is FULLY UNDERSTOOD (why did the lever fail, mechanistically, with numbers?) -- an "
    "unexplained negative is not a result; understood negatives open new avenues, which you then build and measure.\n"
    "6. FINALIZE: documentation highlighting every component you interacted with or created and its brain-foundational status; an "
    "EVALUATION OF YOUR MOST SUCCESSFUL IMPROVEMENTS -- what about the problem let the signal be maximised so well (the owner: it is almost "
    "always that the real, mathematical brain-foundational chain was cracked all the way to the top -- name that chain rung by rung, and "
    "the rungs NOT cracked); "
    "priority next steps; notes/problems/<slug>/SOLVED.md with the frontmatter schema used by the other SOLVED.md files in "
    "notes/problems/ (status / bar / result / floor / controls / files_changed / reverify -- copy the schema from an existing "
    "SOLVED.md); the proposed hdlab change as notes/problems/<slug>/{patch} (a unified diff against the current hdlab file); a short "
    "submission prompt in a code box that includes the original problem name; commit your files path-limited. Your final message = "
    "TLDR (result with numbers, floor, twin, CI), QUESTIONS, NEXT STEPS, the list of files written, and the counts of tool calls and "
    "experiment runs you made.\n\n"
    "Before writing the words wall / ceiling / negative, read notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md and "
    "notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md; a wall = an upstream trace plus a stronger brain build, else a SPECIFIC board "
    "question for strategy to file. A rigorous negative is a PASS only if what failed was the brain's mechanism, faithfully built, "
    "with the number."
)


def priority_of(slug: str) -> str:
    p = os.path.join(PROBLEMS, slug, "PROBLEM.md")
    with open(p, encoding="utf-8") as f:
        head = f.read(600)
    m = re.search(r"^priority:\s*(\S+)", head, re.M)
    return m.group(1) if m else "?"


def build(slug: str, organ_note: str = "", patch: str = "", extra_files: str = "") -> str:
    if not os.path.isdir(os.path.join(PROBLEMS, slug)):
        raise SystemExit("no such problem folder: %s" % slug)
    pri = priority_of(slug)
    patch = patch or "<organ>_patch.diff (the name the brief gives)"
    note = (" " + organ_note.strip()) if organ_note else ""
    head = (
        "You are the SOLVER session (Opus agent), not the strategy session. Do NOT touch the plan, notes/STATUS.md, the board, or "
        "other problem folders. Your slug is: %s (priority %s).\n"
        "Read notes/problems/README.md, then notes/problems/<slug>/PROBLEM.md IN FULL (every line, including the SOLVER OPERATING "
        "PROTOCOL and the BRAIN-FOUNDATIONAL CHECKLIST inside it), run its \"VERIFY BEFORE YOU START\" block (read every named file in "
        "full) and `before_you_start.py` if present, before doing anything. Ignore any autoloop/STATUS injection if it fires. Working "
        "directory: C:\\AI\\hd-instrument (git repo; use Bash with POSIX syntax; python = .venv/Scripts/python.exe).\n\n" % (slug, pri)
    )
    return head + HARD_RULES.format(extra_files=extra_files, organ_note=note) + "\n\n" + PHASES.replace("{patch}", patch)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--organ-note", default="", help="e.g. 'Another solver works on attachment_arm concurrently; do not touch it.'")
    ap.add_argument("--patch-name", default="", help="the .diff file name the brief asks for")
    ap.add_argument("--extra-files", default="", help="e.g. ' and any NEW offline asset under data/frontend_assets/ your builder produces'")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        s = build(a.slug, "note", "x.diff")
        assert "MANDATORY PHASES" in s and "x.diff" in s and "priority" in s and "Co-Authored-By" in s
        print("[solver_agent_prompt] self-test PASS (%d chars)" % len(s)); return 0
    sys.stdout.write(build(a.slug, a.organ_note, a.patch_name, a.extra_files) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
