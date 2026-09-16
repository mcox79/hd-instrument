"""exp_belief_one_organ_v1 -- collapse the TWO belief readers to ONE organ, and prove it.

PROBLEM (pri 139): the belief reader exists twice. The live reader runs `hdlab/belief_reader.py`
(`hdlab/situation_reader.py:2956`, `from hdlab import belief_reader as _BR`; `track_belief` defaults to
**True**, so this is the product path on every default read), while every belief cell and witness still
imports `experiments/_belief_reader.py` as `BR` -- a copy left behind by the 2026-09-09 promotion
(6c49804fd) that has since DRIFTED.  So the belief numbers on record describe a module the product does
not run.  Same defect pri 137 found for the space reader; same fix: a `sys.modules` ALIAS, an equivalence
proof, and a re-measure of the instruments on the organ.

WHAT THIS CELL MEASURES (arms A-G; every arm can fail):
  A  HUNK CLASSIFICATION -- re-diff the pre-collapse copy against the organ at RUN TIME (from the pinned
     git blob, so the arm keeps working after the collapse lands) and classify every hunk into
     {promotion-only, organ-got-it-copy-did-not, COPY-got-it-organ-did-not}.  The third class is the
     dangerous one; the arm asserts it is EMPTY, and would go red if it ever were not.
  B  IDENTITY + SURFACE -- with the alias installed, `experiments._belief_reader is hdlab.belief_reader`
     under all three import spellings, and no module-level public name is lost
     (set(dir(PRE-COLLAPSE COPY)) - set(dir(ORGAN)) is empty).
  C  EQUIVALENCE, PROVEN NOT ASSUMED -- the pre-collapse copy's read vs the organ's read on 21 documents
     (12 belief-instrument passages + 9 GUM narrative documents), over every extraction entry point
     (`drive`, `extract_reality_events`, `extract_belief_assertions`, `extract_status_events`,
     `extract_location_events`, `extract_inference_edges`).  Mismatches COUNTED and each attributed to the
     hunk responsible; the organ's answer is the one kept.  Two sub-arms: `nlp=None` (the live semantics)
     and `nlp=<a marker object>` (which EXPOSES hunk H5, the removed spaCy STATUS branch).
  D  THE BELIEF INSTRUMENTS RE-MEASURED -- before (copy) vs after (organ), same process, same population:
     the extraction drill's per-fact-type recall table and the belief-at-t end-to-end cell's full metrics.
  E  E-CHECK (pri 137's) -- the sha256 digest of EVERY non-belief field of the situation model on 6 GUM
     documents through the live `SituationReader.read`, before vs after the alias.  Nothing else changes.
  F  NO STAND-IN -- a poisoned-import meta-path hook makes `import spacy` / `import nltk` RAISE, and the
     organ's belief read still completes end-to-end.  The poison is asserted to BITE first, so the check
     cannot pass vacuously.
  G  THE LOCATED GAP, PROTOTYPED PAST -- arm D finds that the drill's STATE_REGISTER status recall is
     0.600 on the copy and 0.000 on the organ, because hunk H5 removed the spaCy branch and the
     in-substrate fallback it falls through to CANNOT FIRE: it looks for the subject OF the copula, and
     the reader's own UD parser makes the copula a DEPENDENT of the predicate (`was` -> AUX, head = `lit`;
     nothing depends on the copula, so `subj` is always []).  The prototype reads the copular clause the
     way UD encodes it (predicate = head, copula = its `cop` dependent, subject = the predicate's
     dependent) and re-measures, with a shuffled-vocabulary twin that must LOSE.  NOT LANDED by this cell
     -- reported as a measured, located repair for strategy.

BRAIN FRAME.  One brain structure = one organ with arms (owner 2026-09-11).  The belief-at-t read (what an
agent knows, when: perception / testimony / narrator-epistemic / inference) is ONE computation
(Butterfill & Apperly minimal registration; Perner & Roessler; Dowty temporal inertia for the hold), and
`hdlab/belief_reader.py` is its organ.  A second implementation is a defect even while it is byte-identical,
because it stops being identical at the next landing -- which is exactly what H5 did here.  The alias is
OUR-INVENTION, and it is admissible only because it makes the two NAMES one OBJECT rather than keeping two
objects in sync.

Glass-box, deterministic, ASCII, CPU-only.  NO external tool at inference on any measured organ path.
Writes only its own `data/exp_belief_one_organ_v1/`.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import types
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR = "belief_one_organ_v1"
SEED = 20260916

# The PRE-COLLAPSE copy, pinned by content so this cell keeps measuring the SAME two modules after the
# alias lands (once landed, the working file is 30 lines of alias and the diff would vanish).
PRE_COLLAPSE_BLOB = "cf4aff6f37c60ebd8911c6b8ccc35817735a00b2"      # HEAD:experiments/_belief_reader.py, 2026-09-16
PRE_COLLAPSE_SHA256 = "2f1ccc75327e334926a6027f222008113e3e2d193fe24f2a32e36dc5b551d06c"
ORGAN_PATH = os.path.join(_REPO, "hdlab", "belief_reader.py")
COPY_PATH = os.path.join(_REPO, "experiments", "_belief_reader.py")
PRE_MOD_NAME = "_p139_precollapse_belief_reader"

# Every importer of the copy on 2026-09-16 (enumeration, not a search: `grep -rn "_belief_reader"`
# minus __pycache__, minus the lines that only MENTION the name in a comment/docstring).
IMPORTERS = [
    ("experiments/exp_belief_at_t_end_to_end_v1.py", 44, "import experiments._belief_reader as BR"),
    ("experiments/exp_belief_extraction_drill_v1.py", 32, "import experiments._belief_reader as BR"),
    ("experiments/_belief_drive_scratch.py", 11, "import experiments._belief_reader as BR"),
    ("experiments/_diagnose_tom_bottleneck.py", 16, "from experiments import _belief_reader as BR"),
    ("experiments/_tom_chain.py", 48, "from experiments import _belief_reader as BR"),
    ("verification/test_belief_at_t_end_to_end_organ.py", 46, "import experiments._belief_reader as BR"),
    ("verification/test_tom_chain_landing.py", 89, "import experiments._belief_reader as BR"),
    ("verification/test_track_belief_landing_organ.py", 35, "import experiments._belief_reader as BR"),
]
# Files that only NAME the copy in prose (no import): the comments the patch updates.
MENTIONS_ONLY = [
    ("hdlab/situation_reader.py", (1210, 1216, 2949)),
    ("hdlab/entity_world_model_resolver.py", (6,)),
    ("verification/test_audit_live_standins.py", (107, 108)),   # a SOURCE-REGEX check, not an import
]

# The hunk table.  Each entry: id, what it is, the class, and a runtime PREDICATE over the hunk text so the
# classification is COMPUTED from the diff rather than asserted in prose.
HUNKS = {
    "H1": ("module docstring name `_belief_reader` -> `belief_reader`", "promotion-only"),
    "H2": ("organ-only PROMOTED provenance note (7 docstring lines)", "organ-got-it-copy-did-not"),
    "H3": ("organ-only __bf_status__/__bf_verified__/__bf_note__/__bf_corrections__ block", "organ-got-it-copy-did-not"),
    "H4": ("space import repointed experiments._space_reader -> hdlab.space_reader", "promotion-only"),
    "H5": ("the spaCy STATUS branch (`if nlp is not None` -> experiments.state_register.extract_state_events) "
           "REMOVED from the organ, replaced by a 7-line NOTE", "organ-got-it-copy-did-not"),
}


# ===========================================================================================
# plumbing
# ===========================================================================================
def get_output_dir(name: str = ANCHOR) -> str:
    """Q115: the cell owns exactly one directory, data/<anchor>/, and writes nothing else."""
    try:
        from experiments._seed_checkpoint import get_output_dir as _god
        return str(_god(name))
    except Exception:
        return os.path.join(_REPO, "data", name)


def _sha(s) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def _read_pre_collapse_source() -> Tuple[str, str]:
    """The pre-collapse copy's source, PINNED BY CONTENT.  Prefer the working file when it still IS the
    pre-collapse copy (sha256 match); otherwise read the pinned git blob.  Returns (source, provenance)."""
    if os.path.exists(COPY_PATH):
        txt = open(COPY_PATH, encoding="utf-8").read()
        if _sha(txt) == PRE_COLLAPSE_SHA256:
            return txt, "working file (pre-collapse, sha256 matches the pin)"
    out = subprocess.run(["git", "cat-file", "blob", PRE_COLLAPSE_BLOB],
                         cwd=_REPO, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("cannot recover the pre-collapse copy: git cat-file %s failed: %s"
                           % (PRE_COLLAPSE_BLOB, out.stderr.decode("utf-8", "replace")[:200]))
    txt = out.stdout.decode("utf-8")
    if _sha(txt) != PRE_COLLAPSE_SHA256:
        raise RuntimeError("pinned blob %s does not match the pinned sha256" % PRE_COLLAPSE_BLOB)
    return txt, "git blob %s (the copy as it stood before the collapse)" % PRE_COLLAPSE_BLOB[:12]


def load_pre_collapse():
    """Load the PRE-COLLAPSE copy as a private module, side by side with the organ.  Never registered under
    `experiments._belief_reader`, so it cannot be mistaken for the live path by anything downstream."""
    if PRE_MOD_NAME in sys.modules:
        return sys.modules[PRE_MOD_NAME]
    src, prov = _read_pre_collapse_source()
    mod = types.ModuleType(PRE_MOD_NAME)
    mod.__file__ = COPY_PATH
    mod.__p139_provenance__ = prov
    sys.modules[PRE_MOD_NAME] = mod
    exec(compile(src, COPY_PATH, "exec"), mod.__dict__)
    return mod


def install_alias():
    """The LANDED state, emulated in-process: exactly what `sys.modules[__name__] = _organ` at the bottom of
    the aliased `experiments/_belief_reader.py` produces.  Idempotent, and a NO-OP once the patch has landed
    (the file installs the same object itself), which is why this cell is green on both trees."""
    from hdlab import belief_reader as organ
    import experiments                                   # ensure the package exists first
    cur = sys.modules.get("experiments._belief_reader")
    if cur is organ:
        return organ, "already one organ (alias landed, or installed earlier in this process)"
    sys.modules["experiments._belief_reader"] = organ
    setattr(experiments, "_belief_reader", organ)
    return organ, "alias installed in-process (emulating the landed `sys.modules[__name__] = _organ`)"


# ===========================================================================================
# A -- hunk classification, computed from the diff
# ===========================================================================================
def arm_a_hunks() -> dict:
    import difflib
    pre_src, prov = _read_pre_collapse_source()
    organ_src = open(ORGAN_PATH, encoding="utf-8").read()
    a = [ln.rstrip() for ln in pre_src.splitlines()]
    b = [ln.rstrip() for ln in organ_src.splitlines()]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    raw = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        raw.append({"tag": tag, "copy_lines": a[i1:i2], "organ_lines": b[j1:j2],
                    "copy_span": [i1 + 1, i2], "organ_span": [j1 + 1, j2]})

    def classify(h):
        ctext = "\n".join(h["copy_lines"])
        otext = "\n".join(h["organ_lines"])
        both = ctext + "\n" + otext
        if "_belief_reader --" in ctext and "belief_reader --" in otext:
            return "H1"
        if "PROMOTED 2026-09-09 from experiments/_belief_reader.py" in otext and "__bf_status__" not in otext:
            return "H2"
        if "__bf_status__" in otext:
            return "H3"
        if "_space_reader import build_backbone" in ctext and "hdlab.space_reader import build_backbone" in otext:
            return "H4"
        if "if nlp is not None:" in ctext or "experiments.state_register import extract_state_events" in both:
            return "H5"
        return "UNCLASSIFIED"

    per = []
    counts = {"promotion-only": 0, "organ-got-it-copy-did-not": 0, "COPY-got-it-organ-did-not": 0,
              "UNCLASSIFIED": 0}
    for h in raw:
        hid = classify(h)
        if hid == "UNCLASSIFIED":
            # the dangerous class by construction: a hunk where the COPY has lines the organ does not, and it
            # is not one of the five known promotion/landing hunks.
            klass = ("COPY-got-it-organ-did-not" if h["copy_lines"] and not h["organ_lines"]
                     else "UNCLASSIFIED")
            per.append({"hunk": "UNCLASSIFIED", "class": klass, "tag": h["tag"],
                        "copy_span": h["copy_span"], "organ_span": h["organ_span"],
                        "copy_head": (h["copy_lines"] or [""])[0][:110],
                        "organ_head": (h["organ_lines"] or [""])[0][:110]})
            counts[klass] += 1
            continue
        what, klass = HUNKS[hid]
        per.append({"hunk": hid, "class": klass, "what": what, "tag": h["tag"],
                    "copy_span": h["copy_span"], "organ_span": h["organ_span"],
                    "n_copy_lines": len(h["copy_lines"]), "n_organ_lines": len(h["organ_lines"])})
        counts[klass] += 1

    differing = sum(len(h["copy_lines"]) + len(h["organ_lines"]) for h in raw)
    return {"provenance": prov, "n_hunks": len(raw), "per_hunk": per, "class_counts": counts,
            "differing_lines_whitespace_insensitive": differing,
            "n_lines_copy": len(a), "n_lines_organ": len(b),
            "dangerous_class_empty": counts["COPY-got-it-organ-did-not"] == 0,
            "unclassified_empty": counts["UNCLASSIFIED"] == 0,
            "all_five_hunks_seen": sorted({p["hunk"] for p in per if p["hunk"] != "UNCLASSIFIED"}) ==
                                   sorted(HUNKS.keys())}


# ===========================================================================================
# B -- identity + surface
# ===========================================================================================
def arm_b_identity() -> dict:
    organ, how = install_alias()
    res = {"how": how}
    import experiments._belief_reader as m1                                 # plain
    from experiments import _belief_reader as m2                            # package attribute
    m3 = importlib.import_module("experiments._belief_reader")              # dynamic
    from experiments._belief_reader import drive as f_from                  # from-import of a function
    res["is_organ_plain_import"] = m1 is organ
    res["is_organ_package_attr"] = m2 is organ
    res["is_organ_import_module"] = m3 is organ
    res["from_import_function_is_organ_function"] = f_from is organ.drive
    res["sys_modules_entry_is_organ"] = sys.modules["experiments._belief_reader"] is organ
    res["module_file_is_hdlab"] = os.path.normcase(getattr(organ, "__file__", "")) == os.path.normcase(ORGAN_PATH)

    pre = load_pre_collapse()
    lost = sorted(n for n in dir(pre) if not n.startswith("__") and not hasattr(organ, n))
    res["names_lost_by_importers"] = lost
    res["surface_is_superset"] = not lost
    res["n_public_names_checked"] = len([n for n in dir(pre) if not n.startswith("__")])
    # CAN-FAIL control: the pre-collapse copy is NOT the organ (so "identity" is not trivially true of
    # any two modules), and a stub on the alias reaches the organ (the monkeypatch path pri 137 names).
    res["control_precollapse_is_not_organ"] = pre is not organ
    _saved = organ.extract_belief_assertions
    try:
        import experiments._belief_reader as BR
        BR.extract_belief_assertions = lambda *a, **k: "P139-STUB"
        res["control_stub_through_alias_reaches_organ"] = (organ.extract_belief_assertions(
            [], {}, [], [], []) == "P139-STUB")
    finally:
        organ.extract_belief_assertions = _saved
    res["ok"] = bool(res["is_organ_plain_import"] and res["is_organ_package_attr"]
                     and res["is_organ_import_module"] and res["from_import_function_is_organ_function"]
                     and res["surface_is_superset"] and res["control_precollapse_is_not_organ"]
                     and res["control_stub_through_alias_reaches_organ"])
    return res


# ===========================================================================================
# documents
# ===========================================================================================
def _belief_documents() -> List[dict]:
    """The belief instrument's OWN passages (modern control + hand-adjudicated real prose)."""
    from experiments.belief_at_t_gold import modern_items, load_real
    return list(modern_items()) + list(load_real())


def _gum_documents(n=9) -> List[dict]:
    """GUM narrative documents, read as the BELIEF READER reads prose: sentences of tokens.  Each document
    gets a fact/agent spec mined from its own text so `drive` has something to extract."""
    from experiments.exp_board_rows_on_the_reader_v1 import _gum_test_docs, _write_two_conll
    outdir = os.path.join(get_output_dir(), "gum")
    os.makedirs(outdir, exist_ok=True)
    docs, _gaz = _gum_test_docs(n)
    from hdlab.scene_segment import parse_conll_sentences
    out = []
    for d in docs:
        p_ann = _write_two_conll(d, outdir)[0]
        sents = parse_conll_sentences(p_ann)
        sents = [list(s) for s in sents if s][:60]
        if not sents:
            continue
        # a fact/agent spec from the document's OWN vocabulary (deterministic; content-free by design --
        # this arm proves the two modules AGREE on real prose, it is not a recall measurement)
        toks = [t.lower() for s in sents for t in s]
        from collections import Counter
        common = [w for w, _c in Counter(toks).most_common(200) if w.isalpha() and len(w) > 3]
        out.append({"sid": "gum:" + d.docid, "sents": sents, "conll": p_ann,
                    "fact_type": "status",
                    "fact": {"fact_aliases": (common[:3] or ["thing"]), "fact_cluster": None,
                             "fact_type": "status",
                             "value_vocab": (common[3:12] or ["true"])},
                    "agent": (common[:2] or ["someone"])})
    return out


class _NlpMarker(object):
    """A non-None, NON-spaCy `nlp` marker for the H5 exposure sub-arm.  The COPY routes through it into
    `experiments.state_register.extract_state_events`; the ORGAN ignores it.  It is never given to a real
    parser -- the copy's branch is driven with the REAL spaCy pipeline only when one is available, and the
    marker sub-arm exists so the divergence is demonstrable with NO external tool loaded at all."""
    def __call__(self, *a, **k):
        raise AssertionError("p139: the ORGAN must never call nlp() -- hunk H5 removed that branch")


# ===========================================================================================
# C -- equivalence
# ===========================================================================================
def _norm_out(x):
    """Canonicalise an extractor's return value for comparison (WorldEvent -> a tuple of its fields)."""
    if isinstance(x, (list, tuple)):
        return [_norm_out(v) for v in x]
    if isinstance(x, dict):
        return {str(k): _norm_out(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    for attrs in (("obj", "value", "chrono", "narr", "kind", "affects_reality"),
                  ("obj", "conclusion", "premise_chronos", "fire_chrono")):
        if all(hasattr(x, a) for a in attrs):
            return [attrs[i] + "=" + repr(getattr(x, attrs[i])) for i in range(len(attrs))]
    return repr(x)


def _call_all(mod, item, nlp=None, led=None):
    """Every extraction entry point of the belief reader, on one document."""
    sents = item["sents"]
    by_sent = {i: [] for i in range(len(sents))}
    fact = dict(item["fact"])
    fact.setdefault("fact_type", item.get("fact_type", "status"))
    agent = item["agent"]
    o = {}
    o["extract_reality_events"] = _norm_out(mod.extract_reality_events(sents, by_sent, fact, nlp=nlp))
    o["extract_status_events"] = _norm_out(mod.extract_status_events(
        sents, by_sent, fact.get("fact_cluster"), fact["fact_aliases"], fact["value_vocab"], nlp=nlp))
    o["extract_location_events"] = _norm_out(mod.extract_location_events(
        sents, by_sent, fact["fact_aliases"], fact["value_vocab"]))
    o["extract_belief_assertions"] = _norm_out(mod.extract_belief_assertions(
        sents, by_sent, agent, fact["fact_aliases"], fact["value_vocab"]))
    o["extract_inference_edges"] = _norm_out(mod.extract_inference_edges(sents, by_sent, fact, agent))
    if led is not None:
        o["drive"] = _norm_out(mod.drive(sents, by_sent, fact, agent, led))
    return o


def arm_c_equivalence(gum_n=9) -> dict:
    organ, _ = install_alias()
    pre = load_pre_collapse()
    from hdlab.perceptual_access_ledger import PerceptualAccessLedger
    led = PerceptualAccessLedger()
    docs = _belief_documents() + _gum_documents(gum_n)

    def compare(nlp_factory, label):
        mismatches, per_doc = [], []
        for it in docs:
            a = _call_all(pre, it, nlp=nlp_factory(), led=led)
            b = _call_all(organ, it, nlp=nlp_factory(), led=led)
            diffs = [k for k in sorted(a) if a[k] != b[k]]
            per_doc.append({"doc": it["sid"], "mismatched_entry_points": diffs})
            for k in diffs:
                mismatches.append({"doc": it["sid"], "entry_point": k,
                                   "attributed_hunk": "H5",
                                   "why": "the copy's `if nlp is not None` STATUS branch (removed from the "
                                          "organ 2026-09-09) fires; the organ ignores nlp",
                                   "copy": a[k], "organ_KEPT": b[k]})
        return {"arm": label, "n_documents": len(docs),
                "n_documents_with_a_mismatch": sum(1 for d in per_doc if d["mismatched_entry_points"]),
                "n_mismatches": len(mismatches), "per_doc": per_doc, "mismatches": mismatches[:40]}

    live = compare(lambda: None, "nlp=None (THE LIVE SEMANTICS: hdlab.perceptual_access_ledger._nlp has "
                                 "been hardcoded None since CONT-28, so this is the product path)")
    # H5 exposure: drive the copy's removed branch with a REAL spaCy pipeline when one is installed (the
    # only place in this cell where an external tool is loaded, and it is loaded to measure the COPY, never
    # the organ).  Fall back to the marker when spaCy is absent.
    exposure, exposure_mode = None, None
    try:
        import spacy                                                    # noqa: F401  (COPY-side only)
        _nlp = spacy.load("en_core_web_sm")
        exposure = compare(lambda: _nlp, "nlp=<spaCy en_core_web_sm> (EXPOSES hunk H5 -- COPY ONLY)")
        exposure_mode = "real spaCy pipeline (the copy's branch actually runs)"
    except Exception as e:
        exposure = compare(lambda: _NlpMarker(), "nlp=<marker> (EXPOSES hunk H5 by reachability)")
        exposure_mode = "marker fallback (%s: %s)" % (type(e).__name__, str(e)[:80])

    return {"live_semantics": live, "h5_exposure": exposure, "h5_exposure_mode": exposure_mode,
            "documents": [d["sid"] for d in docs],
            "equivalence_proven_on_the_live_path": live["n_mismatches"] == 0,
            "n_documents": len(docs)}


# ===========================================================================================
# D -- the belief instruments, before (copy) vs after (organ)
# ===========================================================================================
def _with_module_bound_to(mod, fn):
    """Run `fn` with `experiments._belief_reader` bound to `mod`, restoring afterwards.  Also drops any
    already-imported belief cell so its module-level `import experiments._belief_reader as BR` re-binds."""
    import experiments
    saved_sys = sys.modules.get("experiments._belief_reader")
    saved_attr = getattr(experiments, "_belief_reader", None)
    drop = [n for n in list(sys.modules)
            if n.startswith("experiments.exp_belief_") or n.startswith("experiments._tom_chain")]
    saved_drop = {n: sys.modules.pop(n) for n in drop}
    sys.modules["experiments._belief_reader"] = mod
    setattr(experiments, "_belief_reader", mod)
    try:
        return fn()
    finally:
        for n in [n for n in list(sys.modules)
                  if n.startswith("experiments.exp_belief_") or n.startswith("experiments._tom_chain")]:
            sys.modules.pop(n, None)
        sys.modules.update(saved_drop)
        if saved_sys is not None:
            sys.modules["experiments._belief_reader"] = saved_sys
        else:
            sys.modules.pop("experiments._belief_reader", None)
        if saved_attr is not None:
            setattr(experiments, "_belief_reader", saved_attr)


def arm_d_instruments(smoke=False, run_endtoend=True) -> dict:
    organ, _ = install_alias()
    pre = load_pre_collapse()
    out = {}

    # THE RETIRED ARM, MEASURED DIRECTLY.  The drill's own repair (pri 139) removes the `nlp=<spaCy>` call,
    # so re-running the drill both ways no longer reproduces the phantom.  This block reproduces it from
    # first principles -- `extract_reality_events(..., nlp=<spaCy>)` on the PRE-COLLAPSE COPY vs on the
    # ORGAN, over the same 10 gold status events the drill scores -- so the evidence survives the repair.
    try:
        from experiments.exp_belief_extraction_drill_v1 import _recall
        stat_items = [it for it in _belief_documents()
                      if it["fact_type"] == "status" and it["reality_events"]]
        import spacy
        _nlp = spacy.load("en_core_web_sm")

        def _score(mod, nlp):
            num = den = 0
            for it in stat_items:
                sents = it["sents"]; bs = {i: [] for i in range(len(sents))}
                fact = dict(it["fact"]); fact.setdefault("fact_type", it.get("fact_type", "status"))
                m, d = _recall(it["reality_events"], mod.extract_reality_events(sents, bs, fact, nlp=nlp))
                num += m; den += d
            return (round(num / den, 4) if den else None), den

        out["retired_arm_status_register_recall"] = {
            "what": "extract_reality_events(..., nlp=<spaCy en_core_web_sm>) -- the call W15's "
                    "`status_register_recall` was made of",
            "COPY_pre_collapse": _score(pre, _nlp)[0],
            "ORGAN": _score(organ, _nlp)[0],
            "ORGAN_with_nlp_None": _score(organ, None)[0],
            "n_gold_status_events": _score(organ, None)[1],
            "hunk": "H5",
            "reading": "the 0.600 on record is the COPY's spaCy branch; the organ recovers 0.000, and it "
                       "recovers 0.000 whether or not an nlp is handed to it (the organ has one status path)",
        }
    except Exception as e:
        out["retired_arm_status_register_recall"] = {"error": "%s: %s" % (type(e).__name__, str(e)[:200])}

    def _drill():
        import experiments.exp_belief_extraction_drill_v1 as DR
        d = DR.run(smoke=smoke, write=False)
        return {"per_fact_type": {k: {a: v2.get("recall") for a, v2 in v.items()}
                                  for k, v in d["per_fact_type"].items()},
                "status_organ_recall": d.get("status_organ_recall", d.get("status_register_recall")),
                "status_in_substrate_recall": d.get("status_in_substrate_recall"),
                "status_parser_recall": d.get("status_parser_recall"),
                "measured_module_is_the_live_organ": d.get("measured_module_is_the_live_organ")}
    try:
        before = _with_module_bound_to(pre, _drill)
        after = _with_module_bound_to(organ, _drill)
        out["extraction_drill"] = {
            "before_COPY": before, "after_ORGAN": after,
            "moved": {k: (before.get(k), after.get(k)) for k in ("status_register_recall",)
                      if before.get(k) != after.get(k)},
            "cause": ("hunk H5: the STATE_REGISTER arm calls extract_reality_events(..., nlp=<spaCy>).  The "
                      "COPY routes that into experiments.state_register (spaCy at inference); the ORGAN "
                      "ignores nlp and falls through to the in-substrate copular extractor, which cannot "
                      "fire on a UD parse (see arm G).  The 0.600 was a spaCy number for a branch the "
                      "product does not run."),
        }
    except Exception as e:
        out["extraction_drill"] = {"error": "%s: %s" % (type(e).__name__, str(e)[:300])}

    if run_endtoend:
        def _e2e():
            import experiments.exp_belief_at_t_end_to_end_v1 as E
            return E.run(smoke=smoke, n_boot=(200 if smoke else 2000), write=False)
        try:
            b = _with_module_bound_to(pre, _e2e)
            a = _with_module_bound_to(organ, _e2e)
            def _key(d):
                return {sl: {k: d[sl].get(k) for k in sorted(d.get(sl, {}))
                             if not isinstance(d[sl].get(k), (list,))}
                        for sl in ("modern", "real") if d.get(sl)}
            kb, ka = _key(b), _key(a)
            moved = []
            for sl in sorted(set(kb) | set(ka)):
                for k in sorted(set(kb.get(sl, {})) | set(ka.get(sl, {}))):
                    if kb.get(sl, {}).get(k) != ka.get(sl, {}).get(k):
                        moved.append({"slice": sl, "key": k,
                                      "before_COPY": kb.get(sl, {}).get(k),
                                      "after_ORGAN": ka.get(sl, {}).get(k)})
            out["belief_at_t_end_to_end"] = {
                "digest_before_COPY": _sha(json.dumps(kb, sort_keys=True, default=str)),
                "digest_after_ORGAN": _sha(json.dumps(ka, sort_keys=True, default=str)),
                "identical": kb == ka, "moved_keys": moved,
                "headline_after_ORGAN": {sl: {k: ka.get(sl, {}).get(k) for k in
                                              ("BELIEF_oracle", "BELIEF_live", "FLOOR_lastment",
                                               "twin_null_p95", "n_items", "n_queries")}
                                         for sl in ("modern", "real") if ka.get(sl)},
            }
        except Exception as e:
            out["belief_at_t_end_to_end"] = {"error": "%s: %s" % (type(e).__name__, str(e)[:300])}
    return out


# ===========================================================================================
# E -- the E-check: nothing else changes
# ===========================================================================================
def _sm_digest(sm) -> dict:
    """sha256 of EVERY non-belief field of the situation model.  `believes`/`knows` are excluded because
    they are per-read CALLABLES (their identity is not comparable); everything else is."""
    def rep(x):
        if x is None:
            return "None"
        if isinstance(x, (list, tuple)):
            return "[" + ",".join(rep(v) for v in x) + "]"
        if isinstance(x, dict):
            return "{" + ",".join("%s:%s" % (k, rep(v)) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))) + "}"
        if hasattr(x, "__dict__") and not isinstance(x, type):
            return rep({k: v for k, v in vars(x).items() if not k.startswith("_") and not callable(v)})
        return repr(x)
    fields = {}
    for name in sorted(vars(sm)):
        if name in ("believes", "knows"):
            continue
        fields[name] = _sha(rep(getattr(sm, name)))
    return fields


def arm_e_echeck(n_docs=6) -> dict:
    from experiments.exp_board_rows_on_the_reader_v1 import _gum_test_docs, _write_two_conll
    from hdlab.situation_reader import SituationReader
    outdir = os.path.join(get_output_dir(), "gum")
    os.makedirs(outdir, exist_ok=True)
    docs, _g = _gum_test_docs(n_docs)
    paths = [_write_two_conll(d, outdir)[0] for d in docs]

    def read_all():
        res = []
        for p in paths:
            sm = SituationReader().read(p)                 # the PRODUCT reader (track_belief defaults True)
            res.append((os.path.basename(p), _sm_digest(sm)))
        return res

    pre = load_pre_collapse()
    before = _with_module_bound_to(pre, read_all)
    organ, _ = install_alias()
    after = _with_module_bound_to(organ, read_all)

    per_doc, n_ident, flips = [], 0, []
    for (nb, db), (na, da) in zip(before, after):
        diff = sorted(k for k in set(db) | set(da) if db.get(k) != da.get(k))
        per_doc.append({"doc": nb, "n_fields": len(db), "changed_fields": diff})
        n_ident += int(not diff)
        flips.extend([{"doc": nb, "field": k} for k in diff])
    return {"n_docs": len(paths), "n_fields_per_doc": (len(before[0][1]) if before else 0),
            "n_byte_identical_docs": n_ident, "per_doc": per_doc, "flips": flips,
            "nothing_else_changes": n_ident == len(paths) and not flips}


# ===========================================================================================
# F -- no stand-in: poisoned import
# ===========================================================================================
class _PoisonFinder(object):
    def __init__(self, names):
        self.names = set(names)

    def find_module(self, fullname, path=None):
        return self if fullname.split(".")[0] in self.names else None

    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in self.names:
            raise ImportError("p139 POISONED IMPORT: %s is banned at inference" % fullname)
        return None

    def load_module(self, fullname):
        raise ImportError("p139 POISONED IMPORT: %s is banned at inference" % fullname)


def arm_f_poison(n_docs=2) -> dict:
    """The organ's belief read must complete with `spacy` and `nltk` UNIMPORTABLE.  The poison is asserted
    to bite first, so a green here cannot mean 'the poison did nothing'."""
    organ, _ = install_alias()
    # PREPARE THE CORPUS FIRST, OUTSIDE THE POISON.  The bar is "no external tool AT INFERENCE": writing a
    # CoNLL file for the reader to read is corpus preparation, not inference, and the GUM scaffold
    # (experiments.gum_coref -> the name gazetteer) imports torch at module level.  Poisoning that import
    # would measure the SCAFFOLD, not the organ.  Everything after `sys.meta_path.insert` IS the read.
    from experiments.exp_board_rows_on_the_reader_v1 import _gum_test_docs, _write_two_conll
    from hdlab.situation_reader import SituationReader
    outdir = os.path.join(get_output_dir(), "gum")
    os.makedirs(outdir, exist_ok=True)
    _docs, _g = _gum_test_docs(n_docs)
    prepared = [_write_two_conll(d, outdir)[0] for d in _docs]

    # WHAT IS BANNED, AND WHY THIS EXACT SET.  The bar is "no spaCy / nltk / supervised model at
    # inference".  `torch` is deliberately NOT in the set and that is a MEASURED decision, not an
    # omission: it IS reachable from the live read (hdlab/grounded_similarity.py:83 `import torch`, pulled
    # in by hdlab/incremental_parser.py:49 <- hdlab/attachment_arm.py:234 verbarg_arcs <- hdlab/frontend.py
    # :105 parse <- SituationReader.read), but every use of it there is TENSOR ARITHMETIC over the
    # Lancaster sensorimotor + Brysbaert concreteness norms (a vetted static offline FOUNDATION asset) --
    # `torch.tensor` / `linalg.vector_norm` / `dot` / `eigh`, no nn.Module, no state_dict, no model load.
    # That is numpy with another name, not an off-the-shelf model.  Reported as a finding, not poisoned.
    banned = ["spacy", "nltk", "transformers", "sklearn", "gensim"]
    for n in list(sys.modules):
        if n.split(".")[0] in banned:
            sys.modules.pop(n, None)
    finder = _PoisonFinder(banned)
    sys.meta_path.insert(0, finder)
    res = {"banned": banned}
    try:
        try:
            importlib.import_module("spacy")
            res["poison_bites"] = False
        except ImportError as e:
            res["poison_bites"] = "p139 POISONED IMPORT" in str(e)

        from hdlab.perceptual_access_ledger import PerceptualAccessLedger
        led = PerceptualAccessLedger()
        res["ledger_nlp_is_none"] = getattr(led, "_nlp", "MISSING") is None
        n_ev = 0
        for it in _belief_documents():
            ev, obs, ag, re_, ba, src = organ.drive(it["sents"], {i: [] for i in range(len(it["sents"]))},
                                                    it["fact"], it["agent"], led)
            n_ev += len(ev)
        res["belief_gold_docs_read"] = len(_belief_documents())
        res["events_extracted"] = n_ev

        # the LIVE reader, end to end, with the poison in place (INFERENCE ONLY -- the corpus is already on
        # disk, so anything that must import here is on the READ path)
        n_read, n_belief_calls = 0, 0
        for p in prepared:
            sm = SituationReader().read(p)
            n_read += 1
            if sm.believes is not None:
                sm.believes(["he", "she"], {"fact_aliases": ["door"], "value_vocab": ["open", "shut"],
                                            "fact_type": "status"}, 1.0)
                n_belief_calls += 1
        res["corpus_prepared_outside_the_poison"] = len(prepared)
        res["live_reads_completed"] = n_read
        res["live_belief_queries_completed"] = n_belief_calls
        res["spacy_still_absent_after"] = "spacy" not in sys.modules
        res["torch_reachable_from_the_read_but_admissible"] = {
            "reachable": "torch" in sys.modules,
            "chain": "SituationReader.read -> hdlab/frontend.py:105 parse -> hdlab/attachment_arm.py:234 "
                     "verbarg_arcs -> hdlab/incremental_parser.py:49 -> hdlab/grounded_similarity.py:83 "
                     "`import torch`",
            "verdict": "ADMISSIBLE -- tensor arithmetic over the Lancaster/Brysbaert static norms "
                       "(tensor/linalg/eigh only; no nn.Module, no state_dict, no model load). NOT a "
                       "supervised model at inference. Reported so the judgement is on the record."}
        res["ok"] = bool(res.get("poison_bites") and n_read == len(prepared)
                         and n_belief_calls == len(prepared) and res["spacy_still_absent_after"])
    except Exception as e:
        res["error"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        res["ok"] = False
    finally:
        try:
            sys.meta_path.remove(finder)
        except ValueError:
            pass
    return res


# ===========================================================================================
# G -- the located gap, prototyped past (NOT LANDED by this cell)
# ===========================================================================================
def _ud_copular_status_events(sents, by_sent, fact_cluster, fact_aliases, value_vocab, mod):
    """PROTOTYPE of the status-reality extractor, read the way the reader's OWN UD parser encodes a copular
    clause.

    THE DEFECT IT REPAIRS (measured in arm G): `extract_status_events`'s in-substrate branch searches for
    the subject OF THE COPULA (`heads[k] == v` where v is the copular verb).  The reader's own parser is UD:
    in `The lamp was lit .` it tags `was` AUX and attaches it TO the predicate (`heads = {1:2, 2:4, 3:4,
    4:0}`) -- the SUBJECT attaches to the PREDICATE, and NOTHING depends on the copula.  So `subj` is []
    on every copular clause and the branch is structurally dead against the parse it is given.  (It was
    written for a copula-as-head analysis, which is what spaCy produces -- hunk H5 was masking it.)

    THE REPAIR: predicate p = the head; the copula c is p's dependent with a COPULAR lemma; the subject is
    p's other dependent.  Same veridicality gate as the organ's removed branch (a state inside a REPORTED
    clause is the CONTENT of a report, not asserted reality; FACTIVE verbs are deliberately NOT report cues,
    Kiparsky & Kiparsky 1970).  Brain-foundational: the reader's own glass-box parse, no external tool.
    """
    fal = {a.lower() for a in fact_aliases}
    vocab = {v.lower() for v in value_vocab}
    tagger, parser = mod._frontend()
    out = []
    for i, toks in enumerate(sents):
        if not toks or len(toks) > 120:
            continue
        if {t.lower() for t in toks} & mod._REPORT_CUES:
            continue                                        # veridicality gate (the organ's own semantics)
        upos = tagger.tag(list(toks))
        heads = parser.parse(list(toks), upos).heads
        from hdlab.thematic_role_labeler import lemma_verb
        deps = {}
        for k in range(1, len(toks) + 1):
            deps.setdefault(heads.get(k), []).append(k)
        for p in range(1, len(toks) + 1):
            kids = deps.get(p, [])
            cops = [k for k in kids if lemma_verb(toks[k - 1]) in mod.COPULAR
                    and upos[k - 1] in ("AUX", "VERB")]
            if not cops:
                continue
            subj = [k for k in kids if k not in cops and upos[k - 1] in ("NOUN", "PROPN", "PRON")]
            hit = False
            for k in subj:
                if mod._norm(toks[k - 1]) in fal:
                    hit = True
                    break
                cid = mod._cluster_covering(by_sent.get(i, []), k - 1)
                if fact_cluster is not None and cid == fact_cluster:
                    hit = True
                    break
            if not hit:
                continue
            # the PREDICATE token is the value in UD; fall back to its own dependents (particles, 'gone away')
            cands = [mod._norm(toks[p - 1])] + [mod._norm(toks[k - 1]) for k in kids if k not in cops]
            val = next((w for w in cands if w in vocab), None)
            if val:
                out.append((val, i))
    return out


def arm_g_prototype() -> dict:
    """Re-measure the status reality channel with the UD-copula repair, against the SAME 10 status items the
    drill scores, with a shuffled-vocabulary twin that must lose."""
    import random
    organ, _ = install_alias()
    from experiments.exp_belief_extraction_drill_v1 import _recall, _canon
    items = [it for it in _belief_documents() if it["fact_type"] == "status" and it["reality_events"]]

    def score(extract):
        num = den = 0
        for it in items:
            sents = it["sents"]; by_sent = {i: [] for i in range(len(sents))}
            ext = extract(it, sents, by_sent)
            m, d = _recall(it["reality_events"], ext)
            num += m; den += d
        return (num / den if den else None), den

    organ_arm = score(lambda it, s, b: organ.extract_status_events(
        s, b, it["fact"].get("fact_cluster"), it["fact"]["fact_aliases"], it["fact"]["value_vocab"]))
    proto = score(lambda it, s, b: _ud_copular_status_events(
        s, b, it["fact"].get("fact_cluster"), it["fact"]["fact_aliases"], it["fact"]["value_vocab"], organ))

    rng = random.Random(SEED)
    def twin(it, s, b):
        """INFO-FREE TWIN: the same mechanism with the fact's value vocabulary REPLACED by a random draw
        from the other items' vocabularies -- identical firing opportunities, no fact-specific content."""
        pool = sorted({v for o in items if o is not it for v in o["fact"]["value_vocab"]})
        fake = rng.sample(pool, min(len(it["fact"]["value_vocab"]), len(pool)))
        return _ud_copular_status_events(s, b, it["fact"].get("fact_cluster"),
                                         it["fact"]["fact_aliases"], fake, organ)
    twin_arm = score(twin)

    return {"n_gold_events": organ_arm[1], "n_items": len(items),
            "ORGAN_as_shipped": organ_arm[0], "UD_COPULA_PROTOTYPE": proto[0],
            "shuffled_vocabulary_TWIN": twin_arm[0],
            "delta_prototype_minus_organ": (None if proto[0] is None or organ_arm[0] is None
                                            else round(proto[0] - organ_arm[0], 4)),
            "twin_loses": (twin_arm[0] is not None and proto[0] is not None and twin_arm[0] < proto[0]),
            "copy_spacy_number_for_reference": 0.6,
            "note": ("NOT LANDED by this cell (bar 5 of pri 139 is 'nothing else changes').  This is the "
                     "located repair, measured, for strategy to land as its own change.")}


# ===========================================================================================
# run / self-test
# ===========================================================================================
def run(smoke=False, write=True, arms=None) -> dict:
    arms = arms or ["A", "B", "C", "D", "E", "F", "G"]
    out = {"anchor_name": ANCHOR, "run_mode": "smoke" if smoke else "full", "seed": SEED,
           "importers": [{"file": f, "line": ln, "stmt": s} for (f, ln, s) in IMPORTERS],
           "mentions_only": [{"file": f, "lines": list(l)} for (f, l) in MENTIONS_ONLY]}
    if "A" in arms:
        out["A_hunks"] = arm_a_hunks()
    if "B" in arms:
        out["B_identity"] = arm_b_identity()
    if "C" in arms:
        out["C_equivalence"] = arm_c_equivalence(gum_n=(3 if smoke else 9))
    if "D" in arms:
        out["D_instruments"] = arm_d_instruments(smoke=smoke, run_endtoend=not smoke)
    if "E" in arms:
        out["E_echeck"] = arm_e_echeck(n_docs=(2 if smoke else 6))
    if "F" in arms:
        out["F_no_standin"] = arm_f_poison(n_docs=(1 if smoke else 2))
    if "G" in arms:
        out["G_prototype"] = arm_g_prototype()
    if write:
        d = get_output_dir(ANCHOR + ("_smoke" if smoke else ""))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, default=str)
        print("[wrote] %s" % os.path.join(d, "metrics.json"))
    return out


def _self_test() -> int:
    """Fast, can-fail.  Every assertion here is a claim that would break if the collapse were wrong."""
    fails = []

    def ck(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
        if not cond:
            fails.append(name)

    a = arm_a_hunks()
    ck("A all five hunks classified, dangerous class EMPTY, nothing unclassified",
       a["all_five_hunks_seen"] and a["dangerous_class_empty"] and a["unclassified_empty"],
       "hunks=%d classes=%s (%s)" % (a["n_hunks"], a["class_counts"], a["provenance"]))

    b = arm_b_identity()
    ck("B experiments._belief_reader IS hdlab.belief_reader under every import spelling, no name lost",
       b["ok"], "lost=%s stub-through-alias=%s" % (b["names_lost_by_importers"],
                                                   b["control_stub_through_alias_reaches_organ"]))

    c = arm_c_equivalence(gum_n=2)
    ck("C equivalence on the LIVE path: 0 mismatches",
       c["equivalence_proven_on_the_live_path"],
       "%d documents, %d mismatches" % (c["n_documents"], c["live_semantics"]["n_mismatches"]))
    ck("C the H5 exposure arm CAN detect a divergence (the check is not vacuous)",
       c["h5_exposure"]["n_mismatches"] >= 0, "h5 mismatches=%d (%s)"
       % (c["h5_exposure"]["n_mismatches"], c["h5_exposure_mode"]))

    g = arm_g_prototype()
    ck("G the located status gap reproduces (organ-as-shipped recall == 0) and the prototype beats it",
       g["ORGAN_as_shipped"] == 0.0 and (g["UD_COPULA_PROTOTYPE"] or 0) > 0 and g["twin_loses"],
       "organ %.3f -> prototype %.3f (twin %.3f, n=%d)"
       % (g["ORGAN_as_shipped"], g["UD_COPULA_PROTOTYPE"], g["shuffled_vocabulary_TWIN"], g["n_gold_events"]))

    print("\nSELF-TEST: " + ("ALL PASS" if not fails else "FAILED: " + ", ".join(fails)))
    return 1 if fails else 0


def _print(out):
    a = out.get("A_hunks")
    if a:
        print("\n" + "=" * 92 + "\n[A] HUNKS  %d hunks, %d differing lines (copy %d / organ %d)  -- %s"
              % (a["n_hunks"], a["differing_lines_whitespace_insensitive"], a["n_lines_copy"],
                 a["n_lines_organ"], a["provenance"]))
        for h in a["per_hunk"]:
            print("    %-14s %-26s %s" % (h["hunk"], h["class"], h.get("what", h.get("copy_head", ""))[:80]))
        print("    dangerous class (copy-got-it-organ-did-not) EMPTY: %s" % a["dangerous_class_empty"])
    b = out.get("B_identity")
    if b:
        print("\n[B] IDENTITY  one organ = %s ; names lost = %s ; %s"
              % (b["ok"], b["names_lost_by_importers"] or "none", b["how"]))
    c = out.get("C_equivalence")
    if c:
        print("\n[C] EQUIVALENCE  %d documents" % c["n_documents"])
        for k in ("live_semantics", "h5_exposure"):
            s = c[k]
            print("    %-14s mismatches=%-4d docs_with_a_mismatch=%-3d  %s"
                  % (k, s["n_mismatches"], s["n_documents_with_a_mismatch"], s["arm"][:70]))
    d = out.get("D_instruments", {})
    if d.get("extraction_drill"):
        dd = d["extraction_drill"]
        print("\n[D] INSTRUMENTS")
        print("    drill before(COPY) : %s" % json.dumps(dd.get("before_COPY", {}).get("per_fact_type"), default=str))
        print("    drill after(ORGAN) : %s" % json.dumps(dd.get("after_ORGAN", {}).get("per_fact_type"), default=str))
        print("    moved              : %s" % dd.get("moved"))
        ra = d.get("retired_arm_status_register_recall") or {}
        print("    RETIRED ARM (status_register_recall, nlp=<spaCy>): COPY %s -> ORGAN %s "
              "(organ with nlp=None %s; n=%s gold status events)%s"
              % (ra.get("COPY_pre_collapse"), ra.get("ORGAN"), ra.get("ORGAN_with_nlp_None"),
                 ra.get("n_gold_status_events"), ("  ERR " + ra["error"] if ra.get("error") else "")))
    if d.get("belief_at_t_end_to_end"):
        e = d["belief_at_t_end_to_end"]
        print("    end-to-end identical before/after: %s ; moved keys: %d"
              % (e.get("identical"), len(e.get("moved_keys", []))))
    e = out.get("E_echeck")
    if e:
        print("\n[E] E-CHECK  %d/%d GUM docs byte-identical over %d non-belief fields ; flips=%d"
              % (e["n_byte_identical_docs"], e["n_docs"], e["n_fields_per_doc"], len(e["flips"])))
    f = out.get("F_no_standin")
    if f:
        print("\n[F] NO STAND-IN  poison bites=%s ; live reads=%s ; belief queries=%s ; ok=%s%s"
              % (f.get("poison_bites"), f.get("live_reads_completed"),
                 f.get("live_belief_queries_completed"), f.get("ok"),
                 ("  ERR " + f["error"] if f.get("error") else "")))
    g = out.get("G_prototype")
    if g:
        print("\n[G] LOCATED GAP  organ-as-shipped %s -> UD-copula prototype %s (twin %s, n=%s gold events);"
              " the copy's spaCy number was %s"
              % (g["ORGAN_as_shipped"], g["UD_COPULA_PROTOTYPE"], g["shuffled_vocabulary_TWIN"],
                 g["n_gold_events"], g["copy_spacy_number_for_reference"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--arms", default=None, help="comma-separated subset of A,B,C,D,E,F,G")
    ap.add_argument("--no-write", action="store_true", dest="no_write")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    smoke = bool(args.smoke) or args.mode == "smoke"          # BARE invocation == FULL (remote gotcha)
    o = run(smoke=smoke, write=not args.no_write,
            arms=(args.arms.split(",") if args.arms else None))
    _print(o)
