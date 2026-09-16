"""WITNESS -- THE SEAL.  No builder, witness or board row can reach the sealed modern holdout.

problem: seal_a_document_level_modern_holdout_never_read_by_any_builder_or_board_declare_the_split_and_the_
         scorer_before_the_first_answer_is_examined   (pri 126)

A holdout is only a holdout while nothing else reads it, and "nothing else reads it" is a claim that rots the
moment somebody adds a loader.  This witness re-proves it on every certification run, by ENUMERATION:

  W1  every .py under hdlab/ tools/ experiments/ verification/ is walked (not grepped for the files I
      expected) and NONE of them names the sealed corpus directory, the sealed corpus file, the manifest or
      the corpus, except the instrument itself and this witness.
  W2  the sealed corpus does not sit at any path an existing loader already globs -- not in
      data/corpora/ud_english_ewt/, not in experiments/data/ud_english_ewt/, not in data/corpora/gum/conllu/.
  W3  the manifest exists, declares its rule, seed, scorer and configuration, and says so BEFORE the answers.
  W4  every sealed document's SHA-256 still matches the manifest, and holdout and reserve are disjoint.
  W5  RESERVE_V2 has never been read: no landing record in the board arm's log names it.
  W6  the scorer named by the manifest still exists, and its current file hash is reported against the hash
      recorded at the seal (a moved scorer is surfaced, never silently accepted).
  W7  THE WITNESS CAN FAIL: a deliberate leak planted in a scratch copy of the tree is detected.  The check
      runs on a temporary directory; nothing in the repository is modified.

Run: .venv/Scripts/python.exe verification/test_sealed_holdout_is_unread.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

RESULTS = []


def check(name, cond, extra=""):
    RESULTS.append((name, bool(cond)))
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   %s" % (extra,)) if extra != "" else ""))
    return bool(cond)


def main():
    import experiments.exp_sealed_modern_holdout_v1 as S

    print("[witness] THE SEAL -- sealed modern holdout is unread (pri 126)")

    # ---- W1: the enumeration ------------------------------------------------------------------
    enum = S.enumerate_readers()
    check("W1a the enumeration WALKED the tree (it is an enumeration, not a search)",
          enum["n_python_files_walked"] > 500, "%d .py files" % enum["n_python_files_walked"])
    check("W1b the enumeration can SEE a reader when one exists (GUM/GENTLE readers are found)",
          enum["counts"]["GUM + GENTLE"]["files"] > 50,
          "%d files name GUM/GENTLE" % enum["counts"]["GUM + GENTLE"]["files"])
    named = set(enum["sealed_holdout_named_by"]) - set(S.SEAL_EXEMPT)
    check("W1c NOTHING but the instrument and this witness names the sealed holdout",
          not named, sorted(named) or "none")

    # ---- W2: the corpus is not parked where an existing loader looks ---------------------------
    forbidden = ["data/corpora/ud_english_ewt", "experiments/data/ud_english_ewt",
                 "data/corpora/gum/conllu", "data/foundation", "data/frontend_assets"]
    rel = os.path.relpath(S.CORPUS_FILE, _REPO).replace("\\", "/")
    check("W2a the sealed corpus lives outside every directory an existing loader globs",
          not any(rel.startswith(f) for f in forbidden), rel)
    stray = []
    for f in forbidden:
        d = os.path.join(_REPO, f.replace("/", os.sep))
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if "pud" in fn.lower():
                    stray.append(os.path.join(f, fn))
    check("W2b no copy of the sealed corpus has been dropped into a read directory", not stray, stray)

    # ---- W3/W4/W5/W6: the manifest --------------------------------------------------------------
    if not os.path.exists(S.MANIFEST_PATH):
        check("W3 the sealed manifest exists (run --fetch then --seal)", False, S.MANIFEST_PATH)
    else:
        man = json.load(open(S.MANIFEST_PATH, encoding="utf-8"))
        check("W3a the manifest declares itself written BEFORE any answer was examined",
              bool(man.get("declared_before_first_answer")))
        for key in ("rule", "scorer", "configuration", "enumeration", "overlap_audit", "corpus"):
            check("W3b the manifest carries its %s" % key, key in man)
        check("W3c the draw rule names a seed, a unit and a stratification",
              all(k in man["rule"] for k in ("seed", "unit", "stratify_by", "rule")), man["rule"].get("seed"))
        check("W3d the scorer is declared with its module, rows, floors, twin and abstention convention",
              all(k in man["scorer"] for k in ("module", "rows", "floors", "twin", "abstention",
                                               "uncertainty_unit")),
              man["scorer"].get("uncertainty_unit"))
        check("W3e the unit of uncertainty is the DOCUMENT",
              str(man["scorer"].get("uncertainty_unit", "")).startswith("document"))
        check("W3f the overlap audit found NO sealed sentence in any corpus a builder or board reads",
              all(v.get("shared_sentences", 0) == 0 for k, v in man["overlap_audit"].items()
                  if isinstance(v, dict) and v.get("present")),
              {k: v.get("shared_sentences") for k, v in man["overlap_audit"].items()
               if isinstance(v, dict) and v.get("present")})

        hold = set(d["docid"] for d in man["holdout_v1"]["docs"])
        res = set(d["docid"] for d in man["reserve_v2"]["docs"])
        check("W4a holdout and reserve are disjoint", not (hold & res),
              "%d holdout / %d reserve" % (len(hold), len(res)))
        if os.path.exists(S.CORPUS_FILE):
            by = {d["docid"]: d for d in S.parse_pud()}
            bad = [d["docid"] for d in man["holdout_v1"]["docs"] + man["reserve_v2"]["docs"]
                   if d["docid"] not in by or by[d["docid"]]["sha256"] != d["sha256"]]
            check("W4b every sealed document's SHA-256 still matches the manifest", not bad, bad[:5])
            check("W4c the sealed corpus file hash still matches the manifest",
                  S._sha256_file(S.CORPUS_FILE) == man["corpus"]["file_sha256"])
        else:
            check("W4b/W4c the sealed corpus is on disk (re-acquire with --fetch)", False, S.CORPUS_FILE)

        lp = os.path.join(S.OUT_DIR, "board_landings.jsonl")
        reads = 0
        touched_reserve = False
        heads = []
        scorer_moved_latest = False
        if os.path.exists(lp):
            for ln in open(lp, encoding="utf-8"):
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                reads += 1
                heads.append(r.get("head_sha"))
                scorer_moved_latest = bool(r.get("scorer_moved_since_seal"))
                if r.get("which") == "reserve_v2":
                    touched_reserve = True
        check("W5 RESERVE_V2 has never been read (it is the rolling second seal)", not touched_reserve,
              "%d landing reads of HOLDOUT_V1 so far" % reads)

        # ---- W8: THE RETIREMENT POLICY -- the seal's budget is a number, not a judgement call ----
        pol = man.get("retirement_policy") or {}
        check("W8a the manifest carries a retirement policy",
              all(k in pol for k in ("read_budget", "reserve_stays_unread_until", "on_trigger")))
        check("W8b the policy names the 20-read / scorer-change trigger",
              "20" in str(pol.get("reserve_stays_unread_until", ""))
              and "scorer" in str(pol.get("reserve_stays_unread_until", "")).lower(),
              pol.get("reserve_stays_unread_until", "")[:90])
        stamped = [h for h in heads if h]
        check("W8c one read per landing: no git HEAD appears twice in the landing log",
              len(stamped) == len(set(stamped)),
              ("%d reads, %d HEAD-stamped, %d distinct" % (reads, len(stamped), len(set(stamped))))
              + ("   <-- VACUOUS until landing_board_hook_patch.diff lands: no record carries a head_sha "
                 "yet, so this check currently excludes nothing" if not stamped else ""))
        trig_reads = reads >= 20
        check("W8d HOLDOUT_V1 has NOT yet hit its retirement trigger (else promote RESERVE_V2)",
              not trig_reads and not scorer_moved_latest,
              "reads=%d/20  scorer_moved_since_seal=%s" % (reads, scorer_moved_latest))

        sp = os.path.join(_REPO, man["scorer"]["module"])
        check("W6a the declared scorer still exists", os.path.exists(sp), man["scorer"]["module"])
        if os.path.exists(sp):
            now = S._sha256_file(sp)
            dec = man["configuration"]["source_sha256"].get(man["scorer"]["module"])
            print("      scorer hash at seal %s" % dec)
            print("      scorer hash now     %s%s" % (now, "" if now == dec else "   <-- THE SCORER MOVED"))
            check("W6b the scorer hash is RECORDED so a change cannot pass unnoticed", bool(dec))

    # ---- W7: THE WITNESS CAN FAIL ----------------------------------------------------------------
    tmp = tempfile.mkdtemp(prefix="sealleak_")
    try:
        fake = os.path.join(tmp, "tools")
        os.makedirs(fake)
        with open(os.path.join(fake, "build_leaky_asset.py"), "w", encoding="utf-8") as fh:
            fh.write("P = 'data/corpora/holdout/ud_pud_sealed_v1/en_pud-ud-test.conllu'\n")
        pats = [re.compile(p) for ps in S.ENUM_TARGETS["THE SEALED HOLDOUT"] for p in [ps]]
        txt = open(os.path.join(fake, "build_leaky_asset.py"), encoding="utf-8").read()
        detected = any(p.search(txt) for p in pats)
        check("W7 the seal check CAN FAIL: a planted builder that names the sealed corpus is detected "
              "(scratch copy; the repository is untouched)", detected)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
