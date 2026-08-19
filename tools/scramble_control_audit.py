"""AUDIT: which cells use a WORD-ORDER scramble as a control while scoring a BAG representation?

WHY THIS EXISTS. On 2026-08-19 the Phase 2 cell's own pre-committed reading caught its scramble
control tying the real cue EXACTLY -- hit@1 0.7 vs 0.7, permutation p = 1.0000. The cause is
structural, not a bug: `context_vector_masked` and every bag-of-words scorer are INVARIANT TO WORD
ORDER, so shuffling a sentence's tokens produces THE IDENTICAL VECTOR. A control that cannot move
the number is not a weak control; it is a no-op wearing a control's name, and this project has
already retired two others of exactly that shape (a near-rank-preserving corruption control, and a
coverage control that dropped 0 of 242 pairs).

WHAT IT REPORTS, AND WHAT IT DELIBERATELY DOES NOT CLAIM. This is a TRIAGE that enumerates from
the filesystem and reports CO-OCCURRENCE OF TWO CODE SHAPES in one file. It does NOT prove any
particular cell's control was void -- an order-shuffle is a real control for an ORDER-SENSITIVE
scorer (a parser, an arc representation, a positional encoder), and many of these cells will have
one. It produces a READ LIST, ranked, and the reading is done by a human or an audit agent.
Keep EXISTS / IS-REACHED / IS-GOOD separate: this measures EXISTS.

HOW IT ENUMERATES (an absence claim requires an enumeration, not a search -- and this file states
its method so the next reader does not have to guess): `os.walk` over `experiments/`, `hdlab/`,
`tools/` and `verification/`, EVERY `.py`, no sampling, no early exit. The count of files scanned
is printed BEFORE any result, so an empty answer can never read as an established absence.

USAGE
  python tools/scramble_control_audit.py                 # ranked report
  python tools/scramble_control_audit.py --json          # machine-readable
  python tools/scramble_control_audit.py --self-test     # proves the detectors fire and abstain
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOTS = ("experiments", "hdlab", "tools", "verification")

# A shuffle applied to something token-shaped. Deliberately narrow: a shuffle of ARMS, SEEDS or
# ITEMS is not a scramble control and must not be counted.
ORDER_SHUFFLE = re.compile(
    r"(?:random\.shuffle|rng\.shuffle|\.shuffle)\s*\(\s*(\w*(?:tok|word|term|lemma|sent|text)\w*)",
    re.I)
ORDER_PERM = re.compile(
    r"(?:np\.random\.permutation|rng\.permutation)\s*\(\s*(\w*(?:tok|word|term|lemma)\w*)", re.I)
JOIN_SHUFFLED = re.compile(r"[\"']\s+[\"']\s*\.join\s*\(\s*\w*(?:shuf|scram|perm)\w*", re.I)

# A scorer that is INVARIANT to word order.
BAG_SCORER = re.compile(
    r"context_vector|content_lemmas|bag_counts|bag_of_words|Counter\s*\(\s*\w*(?:tok|word|lemma)",
    re.I)

# The word "scramble" used as a control label -- raises confidence that the shuffle IS the control.
SCRAMBLE_LABEL = re.compile(r"scramble|SCRAMBLED?_|_SCRAM", re.I)

# An ORDER-SENSITIVE scorer in the same file EXONERATES it: order-shuffle is a real control there.
ORDER_SENSITIVE = re.compile(
    r"arc_parser|arc_labeler|pos_tagger|deprel|upos|positional|n_gram|ngram|bigram|trigram|"
    r"sequence_encoder|StructuralEncoder|word_order|permutation_invarian", re.I)


# Content-destroying scrambles -- the kind that DOES bind against a bag scorer.
CONTENT_SCRAMBLE = re.compile(
    r"scramble_context_source|donor|unrelated_sent|foreign_sent|shuffle_labels|"
    r"label_permut|permuted_magnitude|random_context|_wrongpool|rand_sent", re.I)

# Any shuffle at all, however the target is named. Broad ON PURPOSE -- see scan_file.
ANY_SHUFFLE = re.compile(r"\.shuffle\s*\(|\.permutation\s*\(|random\.sample\s*\(", re.I)


def _rel(path: str) -> str:
    """relpath, but a temp dir on another mount must not crash the scan (self-test uses C:)."""
    try:
        return os.path.relpath(path, REPO).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def scan_file(path: str) -> Dict:
    """LABEL-FIRST, and that ordering is the correction that makes this tool honest.

    The first version keyed on a token-shaped shuffle target and found ONE file in 13,553 -- which
    would have been reported as "this defect does not exist here". It does not exist IN MY REGEX.
    A cell can scramble by shuffling an INDEX array, by `random.sample`, or by naming its variable
    anything at all, and none of those match a target-name pattern.

    So: start from cells that DECLARE a scramble control and score a bag, then classify HOW they
    scramble. That population is enumerable and small enough to read.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    except OSError:
        return {}
    labelled = bool(SCRAMBLE_LABEL.search(src))
    bag = bool(BAG_SCORER.search(src))
    if not (labelled and bag):
        return {}

    order_shuf = ORDER_SHUFFLE.findall(src) + ORDER_PERM.findall(src)
    if JOIN_SHUFFLED.search(src):
        order_shuf.append("<join-of-shuffled>")
    content_scram = bool(CONTENT_SCRAMBLE.search(src))
    any_shuf = bool(ANY_SHUFFLE.search(src))
    order_sensitive = bool(ORDER_SENSITIVE.search(src))

    # A content-destroying scramble BINDS against a bag scorer -- it is the correct control and
    # is cleared regardless of anything else in the file.
    if content_scram:
        risk = "OK_CONTENT_SCRAMBLE"
    elif order_shuf and not order_sensitive:
        risk = "HIGH"                 # order shuffle, bag scorer, nothing order-sensitive present
    elif order_shuf:
        risk = "CHECK"                # both kinds of scorer present; which one is guarded matters
    elif any_shuf:
        risk = "CHECK"                # scrambles somehow, but not by a recognisable token shuffle
    else:
        risk = "NO_SHUFFLE_FOUND"     # declares a scramble and no shuffle is visible: read it
    return {"path": _rel(path), "shuffled": sorted(set(order_shuf))[:6],
            "content_scramble": content_scram, "any_shuffle": any_shuf,
            "order_sensitive_scorer": order_sensitive, "risk": risk}


def run() -> Tuple[int, List[Dict]]:
    n_files = 0
    hits: List[Dict] = []
    for root in ROOTS:
        base = os.path.join(REPO, root)
        for dirpath, _dirs, files in os.walk(base):
            for f in files:
                if not f.endswith(".py"):
                    continue
                n_files += 1
                r = scan_file(os.path.join(dirpath, f))
                if r:
                    hits.append(r)
    order = {"HIGH": 0, "NO_SHUFFLE_FOUND": 1, "CHECK": 2, "OK_CONTENT_SCRAMBLE": 3}
    hits.sort(key=lambda h: (order.get(h["risk"], 9), h["path"]))
    return n_files, hits


def self_test() -> int:
    """The detectors must FIRE on the shape and ABSTAIN on its near-misses."""
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        ok = ok and bool(cond)

    td = tempfile.mkdtemp(prefix="scramctl_")

    def write(name, src):
        p = os.path.join(td, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
        return p

    hi = write("a.py", "rng.shuffle(tokens)\nSCRAMBLE_ARM=1\nv=context_vector(s)\n")
    check(scan_file(hi).get("risk") == "HIGH",
          "fires HIGH on order shuffle + scramble label + bag scorer")

    chk = write("b.py", "rng.shuffle(tokens)\nSCRAMBLE=1\nv=context_vector(s)\nfrom x import "
                        "arc_parser\n")
    check(scan_file(chk).get("risk") == "CHECK",
          "downgrades to CHECK when an ORDER-SENSITIVE scorer is present -- an order shuffle is "
          "a REAL control there")

    okc = write("f.py", "SCRAMBLE=1\nv=context_vector(s)\nscramble_context_source=pool\n")
    check(scan_file(okc).get("risk") == "OK_CONTENT_SCRAMBLE",
          "CLEARS a content-destroying scramble -- that one binds against a bag scorer")

    # The correction this tool exists to embody: a shuffle whose TARGET is not token-shaped must
    # still be seen. The first version keyed on the target name and found 1 file in 13,553.
    idx = write("g.py", "SCRAMBLE=1\nv=context_vector(s)\nrng.shuffle(idx)\nb=[a[i] for i in idx]\n")
    check(scan_file(idx).get("risk") == "CHECK",
          "still flags a scramble that shuffles an INDEX ARRAY -- the target-name regex misses "
          "it, and that miss is why this tool is label-first")

    none = write("h.py", "SCRAMBLE=1\nv=context_vector(s)\n")
    check(scan_file(none).get("risk") == "NO_SHUFFLE_FOUND",
          "declares a scramble with no visible shuffle -> flagged for reading, never cleared")

    # near-miss: a bag scorer that never mentions a scramble is out of scope
    nm3 = write("e.py", "v=context_vector(s)\n")
    check(not scan_file(nm3), "abstains when no scramble control is declared")

    nm4 = write("i.py", "SCRAMBLE=1\nscore=edit_distance(a,b)\n")
    check(not scan_file(nm4), "abstains when the file has no order-invariant scorer")

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    n_files, hits = run()
    # ROWS SCANNED PRINTED BEFORE RESULTS -- so silence can never read as absence.
    print(f"[scramble-audit] scanned {n_files} .py files under {list(ROOTS)}")
    print(f"[scramble-audit] {len(hits)} file(s) contain BOTH a token-shuffle and an "
          f"order-invariant scorer")
    if a.json:
        print(json.dumps({"n_files_scanned": n_files, "hits": hits}, indent=2))
        return 0
    by = {}
    for h in hits:
        by.setdefault(h["risk"], []).append(h)
    for risk in ("HIGH", "CHECK", "LOW"):
        rows = by.get(risk, [])
        print(f"\n=== {risk}  ({len(rows)})")
        if risk == "HIGH":
            print("    a labelled SCRAMBLE control + a bag scorer + NO order-sensitive scorer.")
            print("    That control CANNOT MOVE THE NUMBER. Read these first.")
        for h in rows:
            print(f"  {h['path']}   shuffles={h['shuffled']}")
    print("\nTHIS MEASURES *EXISTS*, NOT *IS-VOID*. An order shuffle is a genuine control for an "
          "order-sensitive scorer; the reading is still a human's.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
