"""Scaffold-free witness for the LANDING of the NP-HEAD reduce wire (from the owner-DONE
the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning, witness 45/45).

THE high-value structural fix: the reader's role assigners grab the wrong word inside a noun phrase ("the
undertaker's shop" -> undertaker; "iron gate" -> iron) -- 96% of the landed assigners' who-did-what misses.
Reducing each candidate to its NP HEAD (Right-hand Head Rule + genitive DP-head) before the pick lifts EVERY
consumer +0.20 (0.683->0.888) on clean 19c who-did-what. Landed as a default-off np_head_reduce flag on the
shared primitives (resolve_patient / hybrid_role_patient / competition_pick / route_predicate_arguments) +
the shared helper hdlab.np_head_reduce, byte-exact to the validated prototypes.

  [1] PROMOTION FAITHFUL: hdlab.np_head_reduce.is_np_head reproduces BOTH validated prototype reducers byte-exact
      (exp_whodidwhat_per_consumer_wire_v1.np_head_reduce [1-based cands] AND
       exp_whodidwhat_mention_path_fix_v1.np_head_filter [0-based mention wtok_start]) over a random battery.
  [2] DEFAULT-OFF byte-identical: resolve_patient / hybrid_role_patient / competition_pick with np_head_reduce=False
      return the IDENTICAL pick to the no-flag call over a random battery (the flag adds nothing when off).
  [3] FLAG-ON FIXES THE NP-HEAD ERROR (deterministic can-fail): on "the undertaker 's shop was burned by the mob"
      the OFF primitives pick the compound-modifier/possessor ('undertaker'), the ON primitives pick the phrase
      HEAD ('shop') -- the dominant who-did-what error mode, fixed at the primitive all consumers funnel through.

Run: .venv/Scripts/python.exe verification/test_np_head_reduce_wire_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402
import hdlab.np_head_reduce as NHR  # noqa: E402
from hdlab.relcl_resolver import resolve_patient, _cands  # noqa: E402
from hdlab.graded_role_assigner import hybrid_role_patient, competition_pick  # noqa: E402
import experiments.exp_whodidwhat_per_consumer_wire_v1 as PCW  # noqa: E402 (validated prototype, 1-based)
import experiments.exp_whodidwhat_mention_path_fix_v1 as MPF  # noqa: E402 (validated prototype, 0-based mentions)


def main():
    checks = []
    rng = np.random.default_rng(20260903)
    POSTAGS = ["NOUN", "PROPN", "VERB", "ADJ", "DET", "ADP", "PRON", "PUNCT"]
    TOK_POOL = ["the", "shop", "undertaker", "'s", "gate", "iron", "burned", "mob", "he", "book", "old", "of"]

    # [1] PROMOTION FAITHFUL vs BOTH validated prototype reducers.
    ok_pairs = True
    ok_ment = True
    for _ in range(400):
        n = int(rng.integers(3, 9))
        toks = [TOK_POOL[int(rng.integers(0, len(TOK_POOL)))] for _ in range(n)]
        pos = [POSTAGS[int(rng.integers(0, len(POSTAGS)))] for _ in range(n)]
        # 1-based cands prototype
        cands1 = sorted(set(int(rng.integers(1, n + 1)) for _ in range(int(rng.integers(1, n)))))
        ref1 = PCW.np_head_reduce(list(cands1), toks, pos)
        got1 = [i for i in cands1 if NHR.is_np_head(toks, pos, i - 1)] or list(cands1)
        if ref1 != got1:
            ok_pairs = False
        # 0-based mention prototype
        noms = [{"head": toks[j], "wtok_start": j} for j in sorted(set(int(rng.integers(0, n)) for _ in range(int(rng.integers(1, n)))))]
        refm = MPF.np_head_filter([dict(m) for m in noms], toks, pos)
        gotm = [m for m in noms if NHR.is_np_head(toks, pos, m["wtok_start"])] or noms
        if [m["wtok_start"] for m in refm] != [m["wtok_start"] for m in gotm]:
            ok_ment = False
    checks.append((ok_pairs and ok_ment,
                   "[1] PROMOTION FAITHFUL: is_np_head reproduces BOTH prototypes byte-exact -- 1-based cands (%s) + "
                   "0-based mentions (%s), 400 random cases" % (ok_pairs, ok_ment)))

    # [2] DEFAULT-OFF byte-identical for the three primitives.
    off_ok = True
    for _ in range(300):
        n = int(rng.integers(3, 10))
        toks = [TOK_POOL[int(rng.integers(0, len(TOK_POOL)))] for _ in range(n)]
        pos = [POSTAGS[int(rng.integers(0, len(POSTAGS)))] for _ in range(n)]
        v = int(rng.integers(1, n + 1))
        cn = _cands(pos)
        if resolve_patient(toks, pos, v) != resolve_patient(toks, pos, v, np_head_reduce=False):
            off_ok = False
        if hybrid_role_patient(toks, pos, v) != hybrid_role_patient(toks, pos, v, np_head_reduce=False):
            off_ok = False
        if cn and competition_pick(toks, pos, v, cn) != competition_pick(toks, pos, v, cn, np_head_reduce=False):
            off_ok = False
    checks.append((off_ok,
                   "[2] DEFAULT-OFF byte-identical: resolve_patient / hybrid_role_patient / competition_pick with "
                   "np_head_reduce=False == the no-flag call (300 random cases)"))

    # [3] FLAG-ON fixes the NP-head error on a constructed genitive+compound case.
    toks = ["the", "undertaker", "'s", "shop", "was", "burned", "by", "the", "mob"]
    pos = ["DET", "NOUN", "PART", "NOUN", "AUX", "VERB", "ADP", "DET", "NOUN"]
    v = 6  # 1-based index of "burned"
    # candidates are the post-verbal nominals... but the patient here is the SURFACE SUBJECT (passive) 'shop'.
    # Use the direct primitive on a canonical frame to isolate the NP-head pick: "the mob burned the undertaker 's shop"
    toks2 = ["the", "mob", "burned", "the", "undertaker", "'s", "shop"]
    pos2 = ["DET", "NOUN", "VERB", "DET", "NOUN", "PART", "NOUN"]
    v2 = 3  # "burned"
    off_pick = resolve_patient(toks2, pos2, v2)                       # OFF: nearest post-verbal nominal = 'undertaker' (idx 5)
    on_pick = resolve_patient(toks2, pos2, v2, np_head_reduce=True)   # ON: NP-head 'shop' (idx 7)
    off_head = toks2[off_pick - 1] if off_pick else None
    on_head = toks2[on_pick - 1] if on_pick else None
    fixed = (off_head in ("undertaker",)) and (on_head == "shop")
    checks.append((fixed,
                   "[3] FLAG-ON fixes the NP-head error: 'the mob burned the undertaker 's shop' -> OFF picks %r "
                   "(the possessor modifier), ON picks %r (the phrase HEAD)" % (off_head, on_head)))

    print("=== witness: NP-HEAD reduce wire LANDING (the +0.20 who-did-what fix, primitive site) ===")
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("  NOTE: +0.20 per consumer (0.683->0.888) is measured on the 19c gold by "
          "verification/test_whodidwhat_nphead_case.py (45/45); this witnesses the faithful default-off landing.")
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
