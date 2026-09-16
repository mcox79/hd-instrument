"""Scaffold-free witness for pri 139 -- the belief reader is ONE ORGAN.

THE DEFECT.  `hdlab/belief_reader.py` was promoted out of `experiments/_belief_reader.py` on 2026-09-09
(6c49804fd) and the live reader was repointed at it (`hdlab/situation_reader.py:2956`; `track_belief`
defaults to **True**, so it runs on every default read).  The copy was left behind, every belief cell and
witness kept importing it as `BR`, and the two DRIFTED: the promotion removed the spaCy STATUS branch from
the organ and the copy kept it.  So `verification/test_belief_at_t_end_to_end_organ.py`'s W15 was reporting
`status state_register 0.6`, a number produced by a branch the product does not run (on the organ it is
`0.000`).  Same shape as the space reader's copy (pri 137).

THE FIX WITNESSED HERE.  `experiments/_belief_reader.py` becomes a `sys.modules` ALIAS of
`hdlab.belief_reader`, so the two NAMES are one OBJECT (not two objects kept in sync, and not a star-import,
which would COPY references and re-create the defect for every monkeypatch-based check).

WHY THIS WITNESS CANNOT PASS VACUOUSLY.  It DETECTS which tree it is on (alias landed or not) and then
asserts the state it detected -- pri 137's defect-presence / defect-absence control.  Before the landing a
stub on `experiments._belief_reader` MUST be a no-op on the organ (that IS the defect); after it MUST bite.
A tree in neither state fails the witness.

  W1  STATE DETECTION -- the shipped `experiments/_belief_reader.py` is an alias, or it is the copy.
  W2  DEFECT-PRESENCE / DEFECT-ABSENCE -- a stub through the old name is a NO-OP before and BITES after.
  W3  ONE ORGAN -- `experiments._belief_reader IS hdlab.belief_reader` under every import spelling
      (plain import, package attribute, importlib, and a `from ... import <function>`), and the organ is
      the module the LIVE reader binds in `_read_belief`.
  W4  NO NAME LOST -- every module-level public name of the pre-collapse copy exists on the organ.
  W5  EQUIVALENCE -- copy vs organ on the belief instrument's own documents, live semantics, 0 mismatches.
  W6  EVERY ENUMERATED IMPORTER imports green and its `BR` IS the organ.
  W7  NO STAND-IN -- with `spacy`/`nltk` made UNIMPORTABLE (the poison is asserted to bite first), the live
      `SituationReader.read` completes and answers a belief query.
  W8  ONE STATUS PATH -- the organ ignores `nlp` (the removed branch has no second life): a marker that
      RAISES if called is accepted and the answer is identical to `nlp=None`.
  W9  THE COMMENTS THAT NAME THE COPY -- `hdlab/situation_reader.py` no longer points readers at
      `experiments._belief_reader` for the module it actually imports.

Glass-box, NO LLM, deterministic, ASCII, CPU-only.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def main():
    import experiments.exp_belief_one_organ_v1 as C
    from hdlab import belief_reader as ORGAN

    # -- W1 -------------------------------------------------------------------------------------------
    src = open(C.COPY_PATH, encoding="utf-8").read()
    is_alias = ("sys.modules[__name__]" in src) and ("def drive(" not in src)
    is_copy = ("def drive(" in src) and ("sys.modules[__name__]" not in src)
    check("W1 STATE DETECTED: experiments/_belief_reader.py is either the ALIAS or the pre-collapse COPY",
          is_alias != is_copy,
          "LANDED (alias)" if is_alias else ("NOT LANDED (still the %d-line copy)" % len(src.splitlines())))
    if not (is_alias or is_copy):
        print("\nWITNESS FAILED: the file is in neither state; refusing to assert anything about it.")
        return 1

    # -- W2 defect-presence / defect-absence ----------------------------------------------------------
    # Import the old name WITHOUT the cell's emulation, stub it, and see whether the organ notices.
    import importlib
    old = importlib.import_module("experiments._belief_reader")
    saved_old = getattr(old, "extract_belief_assertions", None)
    saved_organ = ORGAN.extract_belief_assertions
    SENT = [["Anna", "believed", "the", "marble", "was", "in", "the", "basket", "."]]
    FACT = {"fact_aliases": ["marble"], "value_vocab": ["basket", "box"], "fact_type": "status",
            "fact_cluster": None}
    try:
        old.extract_belief_assertions = lambda *a, **k: [("box", 0, "STUB")]
        got = ORGAN.extract_belief_assertions(SENT, {0: []}, ["Anna"], ["marble"], ["basket", "box"])
        stub_bites = (got == [("box", 0, "STUB")])
    finally:
        if saved_old is not None:
            old.extract_belief_assertions = saved_old
        ORGAN.extract_belief_assertions = saved_organ
    if is_alias:
        check("W2 DEFECT-ABSENCE: a stub through the OLD name reaches the ORGAN (one object, not two)",
              stub_bites, "stub bit the organ = %s (expected True on the landed tree)" % stub_bites)
    else:
        check("W2 DEFECT-PRESENCE: on the UNPATCHED tree a stub through the old name is a NO-OP on the "
              "organ -- the defect this problem exists to fix, reproduced",
              not stub_bites, "stub bit the organ = %s (expected False before the landing)" % stub_bites)

    # From here the checks describe the LANDED behaviour.  Off the landed tree, the cell's in-process
    # emulation installs exactly what the aliased module installs (`sys.modules[__name__] = _organ`), so
    # the same assertions are made about the same objects.
    organ, how = C.install_alias()
    if not is_alias:
        print("     [emulating the landed state in-process: %s]" % how)

    # -- W3 identity ----------------------------------------------------------------------------------
    b = C.arm_b_identity()
    check("W3 ONE ORGAN: experiments._belief_reader IS hdlab.belief_reader under every import spelling",
          b["is_organ_plain_import"] and b["is_organ_package_attr"] and b["is_organ_import_module"]
          and b["from_import_function_is_organ_function"] and b["sys_modules_entry_is_organ"],
          "plain=%s attr=%s importlib=%s from-import=%s file=%s"
          % (b["is_organ_plain_import"], b["is_organ_package_attr"], b["is_organ_import_module"],
             b["from_import_function_is_organ_function"], b["module_file_is_hdlab"]))
    # the LIVE reader binds the same object in _read_belief
    from hdlab.situation_reader import SituationReader
    r = SituationReader()
    r._read_belief.__func__  # attribute exists
    import hdlab.situation_reader as SR
    src_sr = open(SR.__file__, encoding="utf-8").read()
    check("W3b the LIVE reader's _read_belief imports the ORGAN, not the experiments name",
          "from hdlab import belief_reader as _BR" in src_sr
          and "from experiments import _belief_reader" not in src_sr,
          "hdlab/situation_reader.py binds `from hdlab import belief_reader as _BR`")

    # -- W4 surface -----------------------------------------------------------------------------------
    check("W4 NO NAME LOST: every public module-level name of the pre-collapse copy exists on the organ",
          b["surface_is_superset"],
          "checked %d names; lost = %s" % (b["n_public_names_checked"], b["names_lost_by_importers"] or "none"))

    # -- W5 equivalence -------------------------------------------------------------------------------
    pre = C.load_pre_collapse()
    from hdlab.perceptual_access_ledger import PerceptualAccessLedger
    led = PerceptualAccessLedger()
    docs = C._belief_documents()
    mism = []
    for it in docs:
        a = C._call_all(pre, it, nlp=None, led=led)
        z = C._call_all(organ, it, nlp=None, led=led)
        mism += [(it["sid"], k) for k in sorted(a) if a[k] != z[k]]
    check("W5 EQUIVALENCE on the live path (nlp=None, the product semantics): 0 mismatches",
          not mism, "%d documents x %d entry points, %d mismatches" % (len(docs), 6, len(mism)))

    # -- W6 importers ---------------------------------------------------------------------------------
    bad = []
    for (path, _ln, _stmt) in C.IMPORTERS:
        if not os.path.exists(os.path.join(REPO, path)):
            bad.append((path, "MISSING"))
            continue
        modname = path.replace("/", ".").replace("\\", ".")[:-3]
        if modname.startswith("verification."):
            # witnesses run as scripts, not importable packages -- assert the SOURCE still addresses the
            # old name (which is now the organ) and that the file compiles.
            txt = open(os.path.join(REPO, path), encoding="utf-8").read()
            if "_belief_reader" not in txt:
                bad.append((path, "no longer references the belief reader"))
            try:
                compile(txt, path, "exec")
            except SyntaxError as e:
                bad.append((path, "SyntaxError: %s" % e))
            continue
        try:
            m = importlib.import_module(modname)
        except Exception as e:
            bad.append((path, "%s: %s" % (type(e).__name__, str(e)[:80])))
            continue
        br = getattr(m, "BR", None)
        if br is not None and br is not organ:
            bad.append((path, "its BR is NOT the organ"))
    check("W6 every enumerated importer of the old name is green and reaches the ORGAN",
          not bad, "%d importers; problems = %s" % (len(C.IMPORTERS), bad or "none"))

    # -- W7 no stand-in -------------------------------------------------------------------------------
    f = C.arm_f_poison(n_docs=1)
    check("W7 NO STAND-IN: with spacy/nltk UNIMPORTABLE (poison asserted to bite) the live reader reads and "
          "answers a belief query",
          bool(f.get("ok")),
          "poison_bites=%s ledger_nlp_is_none=%s live_reads=%s belief_queries=%s%s"
          % (f.get("poison_bites"), f.get("ledger_nlp_is_none"), f.get("live_reads_completed"),
             f.get("live_belief_queries_completed"), ("  ERR " + f["error"] if f.get("error") else "")))

    # -- W8 one status path ---------------------------------------------------------------------------
    class _Raises(object):
        def __call__(self, *a, **k):
            raise AssertionError("the organ must not call nlp(): the spaCy STATUS branch is gone")
    same = True
    for it in docs:
        s = it["sents"]; bs = {i: [] for i in range(len(s))}
        fact = dict(it["fact"]); fact.setdefault("fact_type", it.get("fact_type", "status"))
        if organ.extract_reality_events(s, bs, fact, nlp=None) != \
           organ.extract_reality_events(s, bs, fact, nlp=_Raises()):
            same = False
            break
    check("W8 ONE STATUS PATH: the organ ignores `nlp` -- a marker that RAISES if called is accepted and the "
          "answer is identical to nlp=None (the removed spaCy branch has no second life)",
          same, "%d documents, identical on all" % len(docs))

    # -- W9 the comments ------------------------------------------------------------------------------
    stale = [ln for ln in src_sr.splitlines()
             if "experiments._belief_reader" in ln or "experiments/_belief_reader" in ln]
    if is_alias:
        check("W9 hdlab/situation_reader.py no longer points readers at the experiments name for the module "
              "it imports", not stale, "%d stale mentions" % len(stale))
    else:
        check("W9 (pre-landing) the stale comments are PRESENT and enumerated for the patch to fix",
              bool(stale), "%d stale mentions at hdlab/situation_reader.py (1210/1216/2949)" % len(stale))

    print("\n" + ("ALL %d CHECKS PASS  [%s]" % (11 - len(FAILS), "LANDED" if is_alias else "PRE-LANDING")
                  if not FAILS else "WITNESS FAILED: " + "; ".join(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
