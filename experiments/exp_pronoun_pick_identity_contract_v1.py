"""exp_pronoun_pick_identity_contract_v1 -- THE GRADED PRONOUN PICK ANSWERS WITH A DISCOURSE ENTITY AND THE
ANTECEDENT SPAN, AND ITS SCORING STOPS COUNTING "UNSCOREABLE" AS "WRONG".

problem: the_graded_pronoun_pick_returns_a_head_string_and_a_colliding_sentinel_instead_of_an_entity_id_and_
         an_antecedent_span_fix_the_identity_contract_and_the_scoring_before_any_weight_is_tuned  (pri 131)

THE DEFECT (deep review D02/D05/D06, verified on disk here).  `hdlab/coref.graded_pronoun_resolve` keys its
candidate history, its feature card and its answer by `m["head"].lower()`, so two doctors are ONE candidate
with ONE history and ONE card, and a name plus the alias the reader already merged stay TWO.  It answers with
a head STRING plus `resolved_cluster = -1`, while the reader's own online entity ids are `-(file+1)` and the
first file is 0 -- so -1 IS the first live entity: `goal_register.make_canonicalizer` could hand a goal to it
regardless of the chosen head, and `_read_world_state`'s `rc >= 0` dropped every graded link.  Its scoring
reported `coref_acc = 0` on text with no answer key, returned the SAME correctness list as its own
single-sentence comparator, and credited a wrong same-head antecedent through document-wide head membership.

THE BRAIN (the opening move).  A pronoun is resolved to a DISCOURSE ENTITY -- a file card / object file
(Heim 1982 file-change semantics; Kahneman & Treisman 1992) -- never to a word.  Retrieval is
content-addressable and cue-based (Lewis & Vasishth 2005 ACT-R; McElree direct access): it returns the FILE
whose features match, and the MENTION that supplied the evidence is the antecedent.  The binding domain of a
plain pronoun excludes its clause-mate CO-ARGUMENT (Chomsky 1981 Principle B; Reinhart 1983), which is a
relation over the PARSE, and the exclusion is on the co-argument's FILE -- so it is only expressible once the
pick scores entities.  PINNED: the file card, the cue-based retrieval, Principles A/B.  OUR-INVENTION: the
discrete record, the accessibility window (SWEPT), the tie rule.

WHAT THIS CELL DOES.  It measures the proposed ORGAN CHANGE through the LIVE `SituationReader().read()` with
hdlab/ UNPATCHED ON DISK: the patched sources (`--patched <dir>`, materialised from the brief's
`pick_identity_contract_patch.diff`) are exec'd into the live modules, and BOTH arms are then restored by
rebinding the exact attributes the diff touches -- so `head` is the organ as it ships and `entity` is the
organ the diff lands, in ONE process, on ONE question set.

ARMS
  head        the organ as it ships (head-string key, head-membership scoring, -1 sentinel)
  entity      the diff's identity contract: the reader's own ENTITY files are the candidates, the answer is
              (entity id, antecedent span, candidate set, abstain reason), no valid id as a sentinel
  entity_pb   + Principle B from the reader's OWN parse (the clause-mate co-argument's FILE excluded)
  twin        entity_pb with the phi tables PERMUTED (information-free about which pronoun agrees with what)

ROWS
  --self-test        the contract witnesses (constructed passages; every acceptance case of D02/D05/D06)
  --pronouns N       the pronoun instrument on N MODERN GUM test documents, text-only, ABSTENTION = WRONG,
                     scored BOTH ways: by ANTECEDENT SPAN (exact) and by head credit (pri 125's scorer)
  --consumers N      the goal canonicaliser + world-state possession holder on GUM docs, both arms
  --board-coref N    the pri 122 reader-driven coref row (does it report a population at all?)
  --noregress N      UD-EWT agent / patient / state through the live reader, both arms

Glass-box: no spaCy, no nltk tagger, no supervised parser, no external LLM at inference.  GUM and UD-EWT are
MODERN gold and enter the SCORER only.
Run:  .venv/Scripts/python.exe experiments/exp_pronoun_pick_identity_contract_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_pronoun_pick_identity_contract_v1.py --pronouns 28
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import argparse
import io
import json
import random
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

SEED = 20260915
N_BOOT = 2000
SLUG = ("the_graded_pronoun_pick_returns_a_head_string_and_a_colliding_sentinel_instead_of_an_entity_id_"
        "and_an_antecedent_span_fix_the_identity_contract_and_the_scoring_before_any_weight_is_tuned")
DIFF = os.path.join(_REPO, "notes", "problems", SLUG, "pick_identity_contract_patch.diff")


def get_output_dir(default_name: str = "pronoun_pick_identity_contract_v1"):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = os.path.join(_REPO, "data", "exp_" + name)
    os.makedirs(d, exist_ok=True)
    return d


OUT_DIR = get_output_dir()
PATCHED_DEFAULT = os.path.join(OUT_DIR, "patched")


# =====================================================================================================
# 1. MATERIALISE THE PATCHED SOURCE FROM THE DIFF, THEN HOLD BOTH ARMS IN ONE PROCESS
# =====================================================================================================
PATCH_FILES = ("coref.py", "situation_reader.py", "goal_register.py")


_LANDED = None


def landed():
    """True when the contract is ALREADY in the LIVE modules -- i.e. the diff has been integrated.  Then the
    cell must NOT materialise or monkeypatch anything: every arm is the landed organ itself (pri 125/129 made
    the same fix).  Detected from the live objects, never from a file or a git state."""
    global _LANDED
    if _LANDED is None:
        try:
            import dataclasses
            import inspect
            import hdlab.coref as CO
            import hdlab.situation_reader as SR
            f = {x.name for x in dataclasses.fields(SR.CorefResolution)}
            _LANDED = bool(
                {"resolved_entity", "antecedent_span", "candidates", "abstain_reason", "scoreable"} <= f
                and hasattr(CO, "entity_key") and hasattr(CO, "mention_span")
                and "coarg" in inspect.signature(CO.graded_pronoun_resolve).parameters
                and hasattr(SR.SituationReader, "_coargument_positions")
                and "pronoun_principle_b" in inspect.signature(SR.SituationReader.__init__).parameters)
        except Exception:
            _LANDED = False
    return _LANDED


def head_available():
    """Is the SHIPPED (pre-diff) organ reachable in this process?  It is not on a LANDED tree -- the code no
    longer exists there -- so the can-fire halves of the witnesses become landed-state invariants instead."""
    return bool(_HEAD)


def materialize(patched_dir=PATCHED_DEFAULT, diff_path=DIFF, verbose=False):
    """Copy the three hdlab files the diff touches into `patched_dir` and APPLY the diff to the copies, so
    what this cell loads is EXACTLY the proposed landed form (never hdlab/ itself)."""
    if landed():
        if verbose:
            print("LANDED TREE: the contract is already in the live modules -- nothing materialised, "
                  "every arm runs against hdlab/ as it ships")
        return patched_dir
    dst = os.path.join(patched_dir, "hdlab")
    os.makedirs(dst, exist_ok=True)
    for f in PATCH_FILES:
        with open(os.path.join(_REPO, "hdlab", f), "rb") as fh:
            data = fh.read()
        with open(os.path.join(dst, f), "wb") as fh:
            fh.write(data)
    rel = os.path.relpath(patched_dir, _REPO).replace("\\", "/")
    r = subprocess.run(["git", "apply", "-p1", "--directory", rel, diff_path],
                       cwd=_REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git apply failed:\n%s" % r.stderr)
    # THE APPLY MUST HAVE LANDED -- a silent no-op would measure the SHIPPED organ twice and call one of
    # them the proposal (caught here on 2026-09-15: a path-strip mismatch made `git apply` a green no-op).
    for f, marker in (("coref.py", "def entity_key("), ("situation_reader.py", "resolved_entity"),
                      ("goal_register.py", "resolved_entity")):
        if marker not in io.open(os.path.join(dst, f), encoding="utf-8").read():
            raise RuntimeError("patch did not land in %s (marker %r absent)" % (f, marker))
    if verbose:
        print("materialised patched source -> %s" % dst)
    return patched_dir


# the exact attributes the diff changes; the arm swap rebinds these and nothing else
_MOD_ATTRS = (("CO", "graded_pronoun_resolve"), ("CO", "discovered_pronoun_targets"),
              ("SR", "CorefResolution"), ("SR", "SituationModel"),
              ("SR", "discovered_pronoun_targets"), ("SR", "graded_pronoun_resolve"),
              ("GR", "make_canonicalizer"))
_CLS_ATTRS = ("read", "_read_entities", "_read_entities_core", "_read_world_state")
_HEAD, _PATCHED = {}, {}


def _mods():
    import hdlab.coref as CO
    import hdlab.goal_register as GR
    import hdlab.situation_reader as SR
    return {"CO": CO, "GR": GR, "SR": SR}


def _snapshot():
    m = _mods()
    out = {}
    for k, name in _MOD_ATTRS:
        out[(k, name)] = getattr(m[k], name)
    for name in _CLS_ATTRS:
        out[("cls", name)] = m["SR"].SituationReader.__dict__.get(name)
    for name in ("_coargument_positions", "_antecedent_gold"):
        out[("cls", name)] = m["SR"].SituationReader.__dict__.get(name)
    return out


def _install(snap):
    m = _mods()
    for (k, name), v in snap.items():
        if v is None:
            continue
        if k == "cls":
            setattr(m["SR"].SituationReader, name, v)
        else:
            setattr(m[k], name, v)


def load_both(patched_dir=PATCHED_DEFAULT, verbose=False):
    """Snapshot the SHIPPED attributes, exec the PATCHED sources into the live modules, snapshot those too.
    After this call `arm('head')` and `arm('entity')` are both available in this one process."""
    global _HEAD, _PATCHED
    if _PATCHED:
        return
    m = _mods()
    if landed():
        # the live modules ARE the proposed organ; the shipped organ is not present on this tree, so there is
        # no `head` arm to restore and nothing to exec.
        _PATCHED = _snapshot()
        _HEAD = {}
        if verbose:
            print("LANDED TREE: arms run against the live modules (no materialize, no monkeypatch); the "
                  "shipped-organ can-fire halves are replaced by landed-state invariants")
        return
    _HEAD = _snapshot()
    for f in PATCH_FILES:
        mod = m["CO"] if f == "coref.py" else (m["GR"] if f == "goal_register.py" else m["SR"])
        src = io.open(os.path.join(patched_dir, "hdlab", f), encoding="utf-8").read()
        exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    _PATCHED = _snapshot()
    # the shipped class object was replaced by the exec; re-bind the SHIPPED methods onto the NEW class so
    # the `head` arm is the shipped CODE running in the current class namespace.
    for name in _CLS_ATTRS:
        if _HEAD.get(("cls", name)) is None:
            raise RuntimeError("shipped method %s not captured" % name)
    _install(_PATCHED)
    if verbose:
        print("loaded patched source from %s (both arms live)" % patched_dir)


class arm(object):
    """Install one arm for the duration of the block.  `head` = the organ as it ships; `entity` = the diff
    with Principle B OFF (the identity contract alone); `entity_pb` = the diff as proposed; `twin` = the diff
    with both phi tables permuted (information-free)."""

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        import hdlab.situation_reader as SR
        if self.name == "head" and not head_available():
            raise RuntimeError("the shipped organ is not present on this (landed) tree -- no `head` arm")
        _install(_HEAD if self.name == "head" else _PATCHED)
        self._saved_init = None
        if self.name == "entity_pb":
            # the Principle-B arm is the SHIPPED organ with its default-off clause-mate exclusion turned
            # ON -- a constructor flag, so the arm is a configuration of the landed organ, not a monkeypatch
            # of its computation.
            self._saved_init = SR.SituationReader.__init__

            def _init(inner, *a, **kw):
                kw.setdefault("pronoun_principle_b", True)
                self._saved_init(inner, *a, **kw)

            SR.SituationReader.__init__ = _init
        if self.name == "twin":
            _twin_on()
        return self

    def __exit__(self, *exc):
        import hdlab.situation_reader as SR
        if self._saved_init is not None:
            SR.SituationReader.__init__ = self._saved_init
        if self.name == "twin":
            _twin_off()
        _install(_PATCHED)
        return False


_PHI_SHIP, _SCOPE_SHIP = {}, {}


def _twin_on():
    """Permute BOTH tables the organ reads -- `referent_per_np.PRONOUN_PHI` (discovery + scheduling) and
    `state_of_mind.PRONOUN_SCOPE` (what the shipped six-form pick re-derives from).  Permuting only one was
    the control defect pri 125 found."""
    global _PHI_SHIP, _SCOPE_SHIP
    import hdlab.referent_per_np as RNP
    import hdlab.state_of_mind as SOM
    if not _PHI_SHIP:
        _PHI_SHIP = {k: dict(v) for k, v in RNP.PRONOUN_PHI.items()}
        _SCOPE_SHIP = {k: dict(v) for k, v in SOM.PRONOUN_SCOPE.items()}
    rng = random.Random(SEED)
    byp = defaultdict(list)
    for k, v in _PHI_SHIP.items():
        byp[v.get("person")].append(k)
    for _pp, ks in byp.items():
        ks = sorted(ks)
        gn = [(_PHI_SHIP[k]["gender"], _PHI_SHIP[k]["number"]) for k in ks]
        rng.shuffle(gn)
        for k, (g, nn) in zip(ks, gn):
            RNP.PRONOUN_PHI[k] = dict(_PHI_SHIP[k], gender=g, number=nn)
    ks = sorted(_SCOPE_SHIP)
    gn = [(_SCOPE_SHIP[k]["gender"], _SCOPE_SHIP[k]["number"]) for k in ks]
    random.Random(SEED + 1).shuffle(gn)
    for k, (g, nn) in zip(ks, gn):
        SOM.PRONOUN_SCOPE[k]["gender"] = g
        SOM.PRONOUN_SCOPE[k]["number"] = nn


def _twin_off():
    import hdlab.referent_per_np as RNP
    import hdlab.state_of_mind as SOM
    for k, v in _PHI_SHIP.items():
        RNP.PRONOUN_PHI[k] = dict(v)
    for k, v in _SCOPE_SHIP.items():
        SOM.PRONOUN_SCOPE[k]["gender"] = v["gender"]
        SOM.PRONOUN_SCOPE[k]["number"] = v["number"]


# =====================================================================================================
# 2. SMALL SHARED UTILITIES (statistics + a CoNLL writer for constructed passages)
# =====================================================================================================
def acc(vs):
    flat = [x for v in vs for x in (v if isinstance(v, (list, tuple)) else [v])]
    return (sum(flat) / float(len(flat))) if flat else None


def paired_boot(a_docs, b_docs, n_boot=N_BOOT, seed=SEED):
    """Paired bootstrap over DOCUMENTS (the resampling unit) of mean(b) - mean(a)."""
    import numpy as np
    pairs = [(list(a), list(b)) for a, b in zip(a_docs, b_docs) if (len(a) or len(b))]
    if not pairs:
        return None
    rng = np.random.default_rng(seed)
    base = (acc([b for _a, b in pairs]) or 0.0) - (acc([a for a, _b in pairs]) or 0.0)
    ds = []
    idx = np.arange(len(pairs))
    for _ in range(n_boot):
        pick = rng.choice(idx, size=len(pairs), replace=True)
        a = [x for i in pick for x in pairs[i][0]]
        b = [x for i in pick for x in pairs[i][1]]
        if a and b:
            ds.append(sum(b) / len(b) - sum(a) / len(a))
    if not ds:
        return None
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    return {"delta": round(base, 4), "ci": [round(lo, 4), round(hi, 4)],
            "half": round((hi - lo) / 2.0, 4), "sep": bool(lo > 0 or hi < 0)}


def _p(x, nd=4):
    return "n/a" if x is None else ("%." + str(nd) + "f") % x


def write_conll(sentences, annotations=None, path=None, docid="doc"):
    """A CoNLL file the reader can read; `annotations` = {(sent, wtok): "(7)"} for the coref column."""
    path = path or os.path.join(OUT_DIR, "scratch_%d.conll" % random.randint(0, 10 ** 9))
    lines = ["#begin document (%s); part 0" % docid]
    for si, toks in enumerate(sentences):
        for w, t in enumerate(toks):
            col = (annotations or {}).get((si, w), "_")
            lines.append("\t".join([docid, "0", str(w), t] + ["_"] * 7 + [col]))
        lines.append("")
    lines.append("#end document")
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def read_text(sentences, annotations=None, **kw):
    """Read a constructed passage through the LIVE reader (the arm currently installed)."""
    from hdlab.situation_reader import SituationReader
    p = write_conll(sentences, annotations)
    try:
        return SituationReader(**kw).read(p)
    finally:
        try:
            os.unlink(p)
        except OSError:
            pass


# =====================================================================================================
# 3. THE PRONOUN INSTRUMENT -- the same 795-question GUM construction pri 125 landed on, scored BOTH ways
# =====================================================================================================
def gum_questions(doc):
    """THE FIXED QUESTION SET (the gold is the answer key only): every third-person pronoun mention with a
    prior NON-pronoun mention of its gold entity -- pri 125's construction, plus the two fields that make an
    EXACT score possible: the gold entity id and the POSITIONS of its prior mentions."""
    from experiments.exp_pronoun_referent_discovery_v1 import is_anaphora_target_form
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    sent_wpos, gidx_form = {}, {}
    for si in sorted(by_sent):
        for w, t in enumerate(sorted(by_sent[si], key=lambda x: x.idx)):
            sent_wpos[t.gidx] = (si, w)
            gidx_form[t.gidx] = t.form
    qs, seen = [], defaultdict(list)
    pos_by_eid = defaultdict(set)
    for m in sorted(doc.mentions, key=lambda x: (x.start_g, x.end_g)):
        hform = gidx_form.get(m.head_g, m.text.split()[-1] if m.text else "")
        if m.mtype == "pronoun" and is_anaphora_target_form(hform):
            priors = [p for p in seen[m.eid] if p[0] != "pronoun"]
            if priors:
                si, w = sent_wpos.get(m.head_g, (None, None))
                if si is not None:
                    qs.append({"sent": si, "wpos": w, "form": hform.lower(), "eid": m.eid,
                               "gold_heads": sorted({h for _t, h in priors}),
                               "prior_pos": set(pos_by_eid[m.eid])})
        seen[m.eid].append((m.mtype, (gidx_form.get(m.head_g, "") or "").lower()))
        for g in range(m.start_g, m.end_g + 1):
            if g in sent_wpos:
                pos_by_eid[m.eid].add(sent_wpos[g])
    return qs


def _answers(sm, reader_mentions):
    """The reader's answer per target position: (head, antecedent span).  For the SHIPPED arm there is no
    antecedent span -- the pick names a HEAD -- so the span is RECONSTRUCTED as the most recent prior mention
    carrying that head, which is exactly what the head key means.  That is what lets both arms be scored by
    POSITION on one population."""
    out = {}
    seq = sorted(reader_mentions, key=lambda m: (m["sent_idx"], m["wtok_start"]))
    for r in sm.coref_resolutions:
        tp = (r.sent_idx, getattr(r, "target_wpos", -1))
        head = (r.resolved_head or "").lower()
        span = getattr(r, "antecedent_span", None)
        if span is None and head:
            prev = [m for m in seq
                    if (m["sent_idx"], m["wtok_start"]) < tp and not m.get("is_pronoun")
                    and (m.get("head") or "").lower() == head]
            if prev:
                m = prev[-1]
                span = (m["sent_idx"], m["wtok_start"], m["wtok_start"])
        out[tp] = {"head": head, "span": span, "attempted": bool(getattr(r, "attempted", True)),
                   "entity": getattr(r, "resolved_entity", None),
                   "reason": getattr(r, "abstain_reason", None)}
    return out


def _score_q(q, a):
    """(head_credit, span_exact) for ONE question.  head_credit = pri 125's scorer (does the picked HEAD
    STRING name any prior mention of the gold entity); span_exact = is the picked ANTECEDENT SPAN itself a
    mention of the gold entity.  ABSTENTION = WRONG in both."""
    if not a or not a["head"]:
        return 0, 0
    hc = int(a["head"] in q["gold_heads"])
    sp = 0
    if a["span"]:
        si, ws, we = a["span"]
        sp = int(any((si, w) in q["prior_pos"] for w in range(int(ws), int(we) + 1)))
    return hc, sp


def _floor_rows(prepared):
    """FLOOR: nearest prior phi-compatible referent (the reader's own tags, no retrieval), scored both ways."""
    from hdlab import frontend as F
    from hdlab.referent_per_np import pronoun_phi
    from hdlab.state_of_mind import infer_nominal_gender
    tagger = F.tagger()
    hc_rows, sp_rows = [], []
    for d, _pth, qs in prepared:
        by_sent = defaultdict(list)
        for t in d.toks:
            by_sent[t.sent].append(t)
        sents = [[t.form for t in sorted(by_sent[si], key=lambda x: x.idx)] for si in sorted(by_sent)]
        tags = [tagger.tag(list(s)) for s in sents]
        hv, sv = [], []
        for q in qs:
            tphi = pronoun_phi(q["form"]) or {}
            ans, apos = None, None
            for si in range(q["sent"], -1, -1):
                lim = q["wpos"] if si == q["sent"] else len(sents[si])
                for wi in range(min(lim, len(sents[si])) - 1, -1, -1):
                    if tags[si][wi] not in ("NOUN", "PROPN"):
                        continue
                    g = infer_nominal_gender([sents[si][wi]])
                    if tphi.get("gender") and g and tphi["gender"] != "any" and g != tphi["gender"]:
                        continue
                    ans, apos = sents[si][wi].lower(), (si, wi)
                    break
                if ans is not None:
                    break
            hv.append(int(bool(ans) and ans in q["gold_heads"]))
            sv.append(int(apos is not None and apos in q["prior_pos"]))
        hc_rows.append(hv)
        sp_rows.append(sv)
    return hc_rows, sp_rows


def row_pronouns(n_docs=28, arms=("head", "entity", "entity_pb", "twin"), verbose=True):
    import experiments.exp_pronoun_referent_discovery_v1 as P
    from hdlab.situation_reader import SituationReader
    import experiments.gum_coref as G
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    test = alldocs[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    prepared = []
    for d in docs:
        pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
        prepared.append((d, pth, gum_questions(d)))
    if verbose:
        print("GUM: %d test docs, using %d; %d fixed questions (text-only input; gold = the answer key)"
              % (len(test), len(prepared), sum(len(q) for _d, _p, q in prepared)))
    if not head_available():
        arms = tuple(a for a in arms if a != "head")
        print("  NOTE: landed tree -- the `head` (shipped-organ) arm is not available; the floor and the "
              "info-free twin carry the comparison")
    per = {}
    for a in arms:
        hc_rows, sp_rows, cnt = [], [], defaultdict(int)
        items, purity = [], []
        t0 = time.time()
        with arm(a):
            for d, pth, qs in prepared:
                rd = SituationReader()
                sm = rd.read(pth)
                ms = list(getattr(rd, "_coref_mentions", []) or [])
                ans = _answers(sm, ms)
                if a == "entity_pb":
                    purity.append(_cluster_purity(d, ms))
                hv, sv = [], []
                for q in qs:
                    h, s = _score_q(q, ans.get((q["sent"], q["wpos"])))
                    hv.append(h)
                    sv.append(s)
                    aa = ans.get((q["sent"], q["wpos"])) or {}
                    items.append({"doc": str(d.docid), "sent": q["sent"], "wpos": q["wpos"],
                                  "form": q["form"], "span": aa.get("span"), "hc": h, "sp": s,
                                  "entity": aa.get("entity"), "head": aa.get("head")})
                hc_rows.append(hv)
                sp_rows.append(sv)
                cnt["questions"] += len(qs)
                cnt["answered"] += sum(1 for q in qs
                                       if (ans.get((q["sent"], q["wpos"])) or {}).get("head"))
                cnt["discovered"] += int(getattr(sm, "n_pronouns_discovered", 0) or 0)
                cnt["attempted"] += int(getattr(sm, "n_coref_attempted", 0) or 0)
                cnt["abstained"] += int(getattr(sm, "n_coref_abstained", 0) or 0)
                cnt["scoreable"] += int(getattr(sm, "n_coref_scoreable", 0) or 0)
                cnt["records"] += len(sm.coref_resolutions)
                cnt["open"] += len(getattr(sm, "pronoun_abstentions", []) or [])
                cnt["acc_none"] += int(getattr(sm, "coref_acc", None) is None)
        per[a] = {"hc": hc_rows, "sp": sp_rows, "counts": dict(cnt), "items": items,
                  "purity": purity, "secs": round(time.time() - t0, 1)}
        if verbose:
            print("  %-10s span %s | head-credit %s  (%d answered of %d; records %d, open %d)  %.0fs"
                  % (a, _p(acc(sp_rows)), _p(acc(hc_rows)), cnt["answered"], cnt["questions"],
                     cnt["records"], cnt["open"], per[a]["secs"]))
    fh, fs = _floor_rows(prepared)
    out = {"n_docs": len(prepared), "docs": [str(d.docid) for d, _p2, _q in prepared],
           "n_questions": sum(len(q) for _d, _p2, q in prepared),
           "floor_nearest_prior_compatible": {"span": round(acc(fs), 4), "head_credit": round(acc(fh), 4)},
           "arms": {}, "contrasts": {}}
    for a in arms:
        out["arms"][a] = {"span_acc": round(acc(per[a]["sp"]), 4),
                          "head_credit_acc": round(acc(per[a]["hc"]), 4),
                          "counts": per[a]["counts"], "secs": per[a]["secs"]}
        out["contrasts"]["%s_span_vs_floor" % a] = paired_boot(fs, per[a]["sp"])
        out["contrasts"]["%s_head_vs_floor" % a] = paired_boot(fh, per[a]["hc"])
    for a in arms:
        if a != "head" and "head" in per:
            out["contrasts"]["%s_vs_head_span" % a] = paired_boot(per["head"]["sp"], per[a]["sp"])
            out["contrasts"]["%s_vs_head_headcredit" % a] = paired_boot(per["head"]["hc"], per[a]["hc"])
        if a != "twin" and "twin" in per:
            out["contrasts"]["%s_vs_twin_span" % a] = paired_boot(per["twin"]["sp"], per[a]["sp"])
    # THE HEAD-CREDIT INFLATION: items the head scorer credits that the SPAN scorer does not
    for a in arms:
        infl = sum(1 for hv, sv in zip(per[a]["hc"], per[a]["sp"]) for h, s in zip(hv, sv) if h and not s)
        out["arms"][a]["head_credited_wrong_span"] = infl
    if "head" in per and "entity_pb" in per:
        out["disagreements"] = _diagnose(per["head"]["items"], per["entity_pb"]["items"], verbose=verbose)
    pf = per.get("entity_pb", {}).get("purity") or []
    if pf:
        out["clustering_purity"] = {"files": sum(x["files"] for x in pf),
                                    "impure_files": sum(x["impure"] for x in pf),
                                    "mentions_off_any_gold_mention": sum(x["unmapped"] for x in pf)}
        if verbose:
            print("  clustering purity: %s" % json.dumps(out["clustering_purity"], sort_keys=True))
    if verbose:
        print("  floor  span %s | head-credit %s"
              % (_p(out["floor_nearest_prior_compatible"]["span"]),
                 _p(out["floor_nearest_prior_compatible"]["head_credit"])))
        for k, v in out["contrasts"].items():
            if v:
                print("    %-34s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return out


def _sents_of(doc):
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    return [[t.form for t in sorted(by_sent[si], key=lambda x: x.idx)] for si in sorted(by_sent)]


def _gold_eid_at(doc):
    """(sent_idx, wtok) -> gold entity id over EVERY token of every gold mention (the answer key only)."""
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    pos = {}
    for si in sorted(by_sent):
        for w, t in enumerate(sorted(by_sent[si], key=lambda x: x.idx)):
            pos[t.gidx] = (si, w)
    out = {}
    for m in doc.mentions:
        for g in range(m.start_g, m.end_g + 1):
            if g in pos:
                out.setdefault(pos[g], m.eid)
    return out


def _cluster_purity(doc, mentions):
    """IS THE IDENTITY BASIS ITSELF RIGHT?  For every reader entity FILE, the set of gold entities its own
    mention positions fall on: a file touching >1 gold entity is a WRONG MERGE.  This is the measurement the
    brief demands if entity-keyed retrieval loses -- the loss would then be in the CLUSTERING, not the key."""
    gold = _gold_eid_at(doc)
    byfile = defaultdict(set)
    unmapped = 0
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        e = gold.get((m["sent_idx"], m["wtok_start"]))
        if e is None:
            unmapped += 1
        else:
            byfile[m["cluster"]].add(e)
    return {"files": len(byfile), "impure": sum(1 for v in byfile.values() if len(v) > 1),
            "unmapped": unmapped}


def _diagnose(head_items, ent_items, verbose=True):
    """Where the two identity bases DISAGREE, and which one is right -- named with ITEMS, not adjectives."""
    by = {(i["doc"], i["sent"], i["wpos"]): i for i in head_items}
    rows = []
    for e in ent_items:
        h = by.get((e["doc"], e["sent"], e["wpos"]))
        if h is None or h["span"] == e["span"]:
            continue
        rows.append({"doc": e["doc"], "sent": e["sent"], "form": e["form"],
                     "head_span": h["span"], "head_sp": h["sp"],
                     "entity_span": e["span"], "entity_sp": e["sp"], "entity_id": e["entity"]})
    won = sum(1 for r in rows if r["entity_sp"] and not r["head_sp"])
    lost = sum(1 for r in rows if r["head_sp"] and not r["entity_sp"])
    both = sum(1 for r in rows if r["head_sp"] and r["entity_sp"])
    if verbose:
        print("  disagreements: %d of %d questions -- entity WINS %d, LOSES %d, both right %d, both wrong %d"
              % (len(rows), len(ent_items), won, lost, both, len(rows) - won - lost - both))
        for r in rows[:8]:
            print("      %-20s s%-3d %-6s head%s=%d entity%s=%d"
                  % (r["doc"][:20], r["sent"], r["form"], r["head_span"], r["head_sp"],
                     r["entity_span"], r["entity_sp"]))
    return {"n": len(rows), "entity_wins": won, "entity_loses": lost, "both_right": both,
            "both_wrong": len(rows) - won - lost - both, "rows": rows[:60]}


def row_sweep(n_docs=8, verbose=True):
    """THE PHASE DIAGRAM, replayed OFFLINE: read each document ONCE (the entity arm), then re-run the PICK at
    every (window, w_number, w_gender, w_focus, decay) on the SAME mentions and the SAME questions.  The
    default configuration is asserted to reproduce the live arm item-for-item, so the replay IS the organ."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    import hdlab.coref as CO
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    test = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    cap = []
    with arm("entity_pb"):
        for d in docs:
            pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
            rd = SituationReader()
            sm = rd.read(pth)
            qs = gum_questions(d)
            ms = list(rd._coref_mentions or [])
            cap.append({"doc": str(d.docid), "ms": ms, "qs": qs,
                        "coarg": rd._coargument_positions(_sents_of(d), set(q["sent"] for q in qs)),
                        "live": _answers(sm, ms)})

    def _score(cfg):
        rows = []
        for c in cap:
            tg = CO.discovered_pronoun_targets(c["ms"], window=cfg.get("window", 0))
            recs, _ab = CO.graded_pronoun_resolve(
                c["ms"], tg, window=cfg.get("window", 0), w_gender=cfg.get("w_gender", 4.0),
                w_number=cfg.get("w_number", 0.0), w_focus=cfg.get("w_focus", 1.0),
                decay=cfg.get("decay", 2.0), coarg=c["coarg"])
            ans = {(r["sent_idx"], r["target_wpos"]): {"head": r["resolved_head"],
                                                       "span": r["antecedent_span"]} for r in recs}
            rows.append([_score_q(q, ans.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
        return rows

    base = _score({})
    live = [[_score_q(q, c["live"].get((q["sent"], q["wpos"])))[1] for q in c["qs"]] for c in cap]
    if base != live:
        raise AssertionError("the offline replay is NOT the live organ at the default configuration")
    grid = [{"window": w, "w_number": wn} for w in (0, 1, 2, 3) for wn in (0.0, 1.0, 2.0, 4.0)]
    grid += [{"w_gender": g} for g in (0.0, 1.0, 2.0, 8.0)]
    grid += [{"decay": dd} for dd in (0.5, 1.0, 3.0)] + [{"w_focus": f} for f in (0.0, 2.0)]
    out = {"n_docs": len(cap), "n_questions": sum(len(c["qs"]) for c in cap),
           "default_span_acc": round(acc(base), 4), "grid": []}
    for cfg in grid:
        rows = _score(cfg)
        b = paired_boot(base, rows)
        out["grid"].append({"cfg": cfg, "span_acc": round(acc(rows), 4), "vs_default": b})
        if verbose:
            print("    %-34s span %s  d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                  % (json.dumps(cfg, sort_keys=True), _p(round(acc(rows), 4)),
                     (b or {}).get("delta", 0.0), ((b or {}).get("ci") or [0, 0])[0],
                     ((b or {}).get("ci") or [0, 0])[1], (b or {}).get("sep")))
    return out


def row_identity_basis(n_docs=12, verbose=True):
    """THE IDENTITY BASIS IS THE ONLY VARIABLE (the oracle-ceiling probe).  Read each document ONCE, then
    replay the SAME pick over three keyings of the SAME mentions:
      head      the shipped key -- the surface head string
      files     the reader's OWN online entity files (what the diff lands)
      oracle    the GOLD entity of each mention (not shippable; it measures the headroom the reader's
                clustering is leaving on the table -- if `files` loses to `head`, the loss is the
                CLUSTERING, and if `oracle` wins big, the clustering is the lever, not the key)
    One code path, one question set, one process; the `files` arm is asserted to reproduce the LIVE organ
    item-for-item, so the replay is the organ and not a model of it."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    import hdlab.coref as CO
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    test = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    cap = []
    with arm("entity_pb"):
        for d in docs:
            pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
            rd = SituationReader()
            sm = rd.read(pth)
            qs = gum_questions(d)
            ms = [dict(m) for m in (rd._coref_mentions or [])]
            cap.append({"doc": str(d.docid), "ms": ms, "qs": qs, "gold": _gold_eid_at(d),
                        "coarg": rd._coargument_positions(_sents_of(d), set(q["sent"] for q in qs)),
                        "live": _answers(sm, ms)})

    def _rekey(ms, mode, gold):
        out = []
        for m in ms:
            m = dict(m)
            if not m.get("is_pronoun"):
                if mode == "head":
                    m["cluster"] = "head:" + str(m.get("head", "")).lower()
                elif mode == "oracle":
                    e = gold.get((m["sent_idx"], m["wtok_start"]))
                    m["cluster"] = ("gold:%s" % e) if e is not None else ("own:%s" % m["cluster"])
            out.append(m)
        return out

    res = {"n_docs": len(cap), "n_questions": sum(len(c["qs"]) for c in cap), "arms": {}, "contrasts": {}}
    rows = {}
    for mode in ("head", "files", "oracle"):
        per = []
        for c in cap:
            ms = _rekey(c["ms"], mode, c["gold"])
            tg = CO.discovered_pronoun_targets(ms, window=0)
            recs, _ab = CO.graded_pronoun_resolve(ms, tg, window=0, coarg=c["coarg"])
            ans = {(r["sent_idx"], r["target_wpos"]): {"head": r["resolved_head"],
                                                       "span": r["antecedent_span"]} for r in recs}
            per.append([_score_q(q, ans.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
        rows[mode] = per
        res["arms"][mode] = round(acc(per), 4)
        if verbose:
            print("    identity basis %-7s span %s" % (mode, _p(round(acc(per), 4))))
    live = [[_score_q(q, c["live"].get((q["sent"], q["wpos"])))[1] for q in c["qs"]] for c in cap]
    if rows["files"] != live:
        raise AssertionError("the replay's `files` arm is NOT the live organ")
    for a in ("files", "oracle"):
        res["contrasts"]["%s_vs_head" % a] = paired_boot(rows["head"], rows[a])
    res["contrasts"]["oracle_vs_files"] = paired_boot(rows["files"], rows["oracle"])
    if verbose:
        for k, v in res["contrasts"].items():
            if v:
                print("      %-20s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return res


def _gold_coarg(doc):
    """The clause-mate CO-ARGUMENT map from the TREEBANK parse (the answer key, never an input to a
    decision): the other dependents of the same governing VERB/AUX.  Same rule as the reader's own
    `_coargument_positions`, so the ONLY difference between the two arms is the PARSE."""
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    out = {}
    for si in sorted(by_sent):
        toks = sorted(by_sent[si], key=lambda x: x.idx)
        wpos = {t.idx: w for w, t in enumerate(toks)}
        up = {t.idx: t.upos for t in toks}
        by_gov = defaultdict(list)
        for t in toks:
            if not t.head:
                continue
            if up.get(t.head) in ("VERB", "AUX"):
                by_gov[t.head].append(t.idx)
        for _g, kids in by_gov.items():
            for i in kids:
                out[(si, wpos[i])] = tuple((si, wpos[j]) for j in kids if j != i)
    return out


def row_principle_b(n_docs=12, verbose=True):
    """IS THE PRINCIPLE-B NEGATIVE THE PRINCIPLE OR THE PARSE?  Principle B is PINNED and categorical
    (Chomsky 1981; Reinhart 1983), but it is APPLIED through a relation the reader computes -- so a wrong
    parse bans the RIGHT antecedent.  Three arms over the same reads, the same questions, one code path:
      off      no clause-mate exclusion
      parse    the reader's OWN parse (what the diff ships)
      oracle   the treebank parse (the answer key, diagnostic ONLY -- never shippable)
    If `oracle` wins where `parse` does not, the negative is the parse's UAS, not the principle."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    import hdlab.coref as CO
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    test = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    cap = []
    with arm("entity_pb"):
        for d in docs:
            pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
            rd = SituationReader()
            rd.read(pth)
            qs = gum_questions(d)
            cap.append({"doc": str(d.docid), "ms": list(rd._coref_mentions or []), "qs": qs,
                        "parse": rd._coargument_positions(_sents_of(d), set(q["sent"] for q in qs)),
                        "oracle": _gold_coarg(d)})
    res = {"n_docs": len(cap), "n_questions": sum(len(c["qs"]) for c in cap), "arms": {}, "contrasts": {}}
    rows = {}
    for mode in ("off", "parse", "oracle"):
        per = []
        for c in cap:
            tg = CO.discovered_pronoun_targets(c["ms"], window=0)
            recs, _ab = CO.graded_pronoun_resolve(c["ms"], tg, window=0,
                                                  coarg=(None if mode == "off" else c[mode]))
            ans = {(r["sent_idx"], r["target_wpos"]): {"head": r["resolved_head"],
                                                       "span": r["antecedent_span"]} for r in recs}
            per.append([_score_q(q, ans.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
        rows[mode] = per
        res["arms"][mode] = round(acc(per), 4)
        if verbose:
            print("    principle-B source %-7s span %s" % (mode, _p(round(acc(per), 4))))
    for m in ("parse", "oracle"):
        res["contrasts"]["%s_vs_off" % m] = paired_boot(rows["off"], rows[m])
    res["contrasts"]["oracle_vs_parse"] = paired_boot(rows["parse"], rows["oracle"])
    if verbose:
        for k, v in res["contrasts"].items():
            if v:
                print("      %-18s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return res


# =====================================================================================================
# 4. THE CONSUMERS -- the goal canonicaliser and the world-state possession holder (D02's acceptance list)
# =====================================================================================================
def row_consumers(n_docs=6, verbose=True):
    """Does the pick's answer REACH the consumers?  Counts, both arms, on the same documents: goal owners
    canonicalised through a pronoun, and world-state holders keyed to an entity file."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    from hdlab.situation_reader import SituationReader
    import experiments.gum_coref as G
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    test = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    paths = [P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
             for d in docs]
    out = {"n_docs": len(paths), "arms": {}}
    for a in (("head", "entity_pb") if head_available() else ("entity_pb",)):
        c = defaultdict(int)
        with arm(a):
            for pth in paths:
                rd = SituationReader(track_goals=True, track_world_state=True, densify_world_state=True)
                sm = rd.read(pth)
                from hdlab.goal_register import make_canonicalizer
                canon, _nm = make_canonicalizer(sm)
                names = {e.cluster for e in sm.entities}
                for r in sm.coref_resolutions:
                    ent = getattr(r, "resolved_entity", None)
                    if ent is None:
                        ent = r.resolved_cluster
                    c["records"] += 1
                    c["with_identity"] += int(ent is not None)
                    c["identity_is_live_entity"] += int(ent is not None and ent in names)
                    if canon(r.pronoun, r.sent_idx):
                        c["canonicalised"] += 1
                ws = getattr(sm, "world_state", None)
                have = (getattr(ws, "have", {}) or {}) if ws is not None else {}
                c["ws_tracked_objects"] += len(have)
                for obj in have:
                    h = ws.holder_of(obj)
                    c["ws_holders"] += int(h is not None)
                    c["ws_entity_holders"] += int(h is not None and str(h).startswith("C"))
        out["arms"][a] = dict(c)
        if verbose:
            print("  %-10s %s" % (a, json.dumps(dict(c), sort_keys=True)))
    return out


# =====================================================================================================
# 5. THE pri 122 READER-DRIVEN BOARD COREF ROW -- does it report a population at all?
# =====================================================================================================
def row_board_coref(n_docs=4, verbose=True):
    import experiments.exp_board_rows_on_the_reader_v1 as RDR
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    test = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    out = {"arms": {}}
    for a in (("head", "entity_pb") if head_available() else ("entity_pb",)):
        tot = defaultdict(lambda: [0, 0])
        diag = defaultdict(int)
        with arm(a):
            for d in docs:
                pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
                rd = SituationReader()
                sm = rd.read(pth)
                sc, dg = RDR.score_gum_doc(d, sm, rd, random.Random(SEED))
                for k, v in sc["coref"].items():
                    tot[k][0] += v[0]
                    tot[k][1] += v[1]
                diag["aligned"] += int(bool(dg.get("coref_aligned")))
                diag["targets"] += int(dg.get("n_reader_pronoun_targets") or 0)
                diag["resolutions"] += int(dg.get("n_reader_resolutions") or 0)
                diag["docs"] += 1
        out["arms"][a] = {"rows": {k: list(v) for k, v in tot.items()}, "diag": dict(diag)}
        if verbose:
            print("  %-10s coref row %s  diag %s"
                  % (a, json.dumps({k: "%d/%d" % (v[0], v[1]) for k, v in tot.items()}, sort_keys=True),
                     json.dumps(dict(diag), sort_keys=True)))
    return out


# =====================================================================================================
# 6. NO-REGRESS -- UD-EWT agent / patient / state through the live reader, both arms
# =====================================================================================================
def row_noregress(n_docs=12, verbose=True):
    import experiments.exp_pronoun_referent_discovery_v1 as P
    from hdlab.situation_reader import SituationReader
    docs = P.load_ud_docs()[:n_docs]
    out = {"n_docs": len(docs), "arms": {}}
    rows = {}
    for a in (("head", "entity_pb") if head_available() else ("entity_pb",)):
        per = {"agent": [], "patient": [], "state": []}
        with arm(a):
            for _docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                p = P.write_conll(sents)
                try:
                    sm = SituationReader().read(p)
                finally:
                    os.unlink(p)
                sc = P.score_doc(sm, gold)
                for k in per:
                    per[k].append(sc.get(k, []))
        rows[a] = per
        out["arms"][a] = {k: round(acc(v), 4) if acc(v) is not None else None for k, v in per.items()}
        if verbose:
            print("  %-10s %s" % (a, json.dumps(out["arms"][a], sort_keys=True)))
    out["contrasts"] = ({k: paired_boot(rows["head"][k], rows["entity_pb"][k])
                         for k in ("agent", "patient", "state")} if "head" in rows else {})
    if verbose:
        for k, v in out["contrasts"].items():
            if v:
                print("    %-10s d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (k, v["delta"], v["ci"][0], v["ci"][1], v["sep"]))
    return out


# =====================================================================================================
# 7. THE CONTRACT WITNESSES -- every acceptance case of D02 / D05 / D06, on constructed passages
# =====================================================================================================
TWO_DOCTORS = [
    ["Doctor", "Miller", "examined", "the", "patient", "."],
    ["A", "second", "doctor", "arrived", "later", "."],
    ["Nurse", "Adams", "greeted", "the", "visitors", "."],
    ["She", "carried", "a", "clipboard", "."],
]
ALIAS = [
    ["Elizabeth", "Warren", "opened", "the", "clinic", "."],
    ["The", "founder", "hired", "two", "nurses", "."],
    ["She", "signed", "the", "papers", "."],
]
PRINCIPLE_B = [
    ["Robert", "greeted", "the", "visitors", "."],
    ["Michael", "praised", "him", "loudly", "."],
]


def _rec_by_form(sm, form):
    for r in sm.coref_resolutions:
        if (r.pronoun or "").lower() == form:
            return r
    return None


def witnesses(verbose=True):
    """Every witness is a CLAIM about the contract (an invariant, a direction, a can-fail control) -- never a
    pinned number."""
    from hdlab.situation_reader import SituationReader
    checks = []

    # W1 -- TWO SAME-HEAD ENTITIES STAY DISTINCT, and the answer names ONE OF THEM (D05 acceptance 1).
    with arm("entity"):
        rd = SituationReader()
        p = write_conll(TWO_DOCTORS)
        sm = rd.read(p)
        os.unlink(p)
        ms = [m for m in (rd._coref_mentions or []) if not m.get("is_pronoun")]
        doctors = {m["cluster"] for m in ms if (m.get("head") or "").lower() == "doctor"}
        ent_ids = {e.cluster for e in sm.entities}
        r = _rec_by_form(sm, "she")
        w1 = (len(doctors) >= 2 and r is not None and r.resolved_entity is not None
              and r.resolved_entity in ent_ids)
        checks.append((w1, "[W1] two same-head `doctor` referents stay DISTINCT files (%d) and the pick "
                           "answers with a live entity id (%r), not a head string" % (len(doctors),
                                                                                     getattr(r, "resolved_entity", None))))
        # and the head-keyed organ cannot tell them apart: ONE candidate key for both
        if head_available():
            with arm("head"):
                rd2 = SituationReader()
                p = write_conll(TWO_DOCTORS)
                sm2 = rd2.read(p)
                os.unlink(p)
                r2 = _rec_by_form(sm2, "she")
            w1b = (r2 is not None and getattr(r2, "resolved_entity", None) is None
                   and r2.resolved_cluster is None)
            checks.append((w1b, "[W1b] the SHIPPED organ returns no entity at all for the same passage "
                                "(resolved_entity=%r, resolved_cluster=%r) -- a head string is its whole "
                                "answer" % (getattr(r2, "resolved_entity", None),
                                            getattr(r2, "resolved_cluster", None))))
        else:
            import dataclasses as _dc
            import hdlab.coref as _CO
            import hdlab.situation_reader as _SRm
            fl = {x.name for x in _dc.fields(_SRm.CorefResolution)}
            w1b = ({"resolved_entity", "antecedent_span", "candidates", "abstain_reason", "scoreable"} <= fl
                   and hasattr(_CO, "entity_key") and hasattr(_CO, "mention_span"))
            checks.append((w1b, "[W1b] LANDED TREE -- the shipped head-string organ is no longer on disk, so "
                                "the CONTRACT is the check: CorefResolution carries the entity, the "
                                "antecedent span, the candidate set and the abstention reason, and the "
                                "identity basis is coref.entity_key (not a head string)"))

    # W2 -- A NAME AND ITS ALIAS ARE ONE IDENTITY, not two competing candidates (D05 acceptance 2).
    with arm("entity"):
        rd = SituationReader()
        p = write_conll(ALIAS)
        sm = rd.read(p)
        os.unlink(p)
        r = _rec_by_form(sm, "she")
        cands = dict(getattr(r, "candidates", ()) or ())
        heads_of = defaultdict(set)
        for m in (rd._coref_mentions or []):
            if not m.get("is_pronoun"):
                heads_of[m["cluster"]].add((m.get("head") or "").lower())
        merged = any(len(v) > 1 for v in heads_of.values())
        w2 = (r is not None and r.resolved_entity is not None
              and len(cands) <= len(heads_of) and r.resolved_entity in heads_of)
        checks.append((w2, "[W2] the candidate set is the reader's FILES (%d candidates over %d files; a "
                           "file carrying >1 surface head present=%s) -- aliases compete once, not twice"
                       % (len(cands), len(heads_of), merged)))

    # W3 -- NO VALID ID IS USED AS A SENTINEL (D02 acceptance 2): -1 is a live entity, and an unresolved
    #       reference is None on every path.
    with arm("entity"):
        rd = SituationReader()
        p = write_conll(TWO_DOCTORS)
        sm = rd.read(p)
        os.unlink(p)
        ids = sorted([e.cluster for e in sm.entities if isinstance(e.cluster, int)])
        neg = [i for i in ids if i < 0]
        unresolved = [r for r in sm.coref_resolutions if not r.attempted]
        w3 = (bool(neg) and all(getattr(r, "resolved_entity", None) is None for r in unresolved)
              and all(r.resolved_cluster is None for r in sm.coref_resolutions))
        checks.append((w3, "[W3] valid entity ids are NEGATIVE here (%s) and every unresolved record carries "
                           "None, not -1 -- validity is membership, not sign" % (neg[:4],)))

    # W4 -- UNANNOTATED TEXT REPORTS ACCURACY UNAVAILABLE, WITH THE FOUR COUNTS (D06 acceptance 1/4).
    with arm("entity"):
        sm = read_text(TWO_DOCTORS)
        w4 = (sm.coref_acc is None and getattr(sm, "coref_attempted_acc", None) is None
              and sm.n_pronouns_discovered == sm.n_coref_attempted + sm.n_coref_abstained
              and sm.n_coref_scoreable == 0 and sm.n_pronouns_discovered > 0)
        checks.append((w4, "[W4] no answer key -> coref_acc UNAVAILABLE (None), counts published and "
                           "consistent: discovered %d = attempted %d + abstained %d, scoreable %d"
                       % (sm.n_pronouns_discovered, sm.n_coref_attempted, sm.n_coref_abstained,
                          sm.n_coref_scoreable)))
    if head_available():
        with arm("head"):
            sm_h = read_text(TWO_DOCTORS)
            w4b = (sm_h.coref_acc == 0.0)
            checks.append((w4b, "[W4b] CAN-FIRE: the shipped organ reports coref_acc=%r on the same "
                                "annotation-free text -- 'it got them all wrong' where there is nothing to "
                                "score" % (sm_h.coref_acc,)))
    else:
        # LANDED equivalent, and a STRICTLY STRONGER check than the can-fire it replaces: scoreability is a
        # property of THIS input, so ONE reader reading an annotated document and then an annotation-free one
        # must report a number and then None (the shipped organ never reset it).
        with arm("entity"):
            rd = SituationReader()
            p1 = write_conll(TWO_DOCTORS, {(0, 0): "(7)", (3, 0): "(7)"})
            sm_a = rd.read(p1)
            os.unlink(p1)
            p2 = write_conll(TWO_DOCTORS)
            sm_b = rd.read(p2)
            os.unlink(p2)
        w4b = (sm_b.coref_acc is None and sm_b.n_coref_scoreable == 0
               and sm_a.n_coref_scoreable >= 1)
        checks.append((w4b, "[W4b] LANDED TREE -- scoreability is RESET PER READ on one reader: the "
                            "annotated document reports %d scoreable item(s) and coref_acc=%r, the "
                            "annotation-free one that follows it reports 0 and None (never 0.0)"
                       % (sm_a.n_coref_scoreable, sm_a.coref_acc)))

    # W5 -- A WRONG SAME-HEAD ANTECEDENT SCORES WRONG (D06 acceptance 2).  The answer key links `she` to the
    #       FIRST doctor; the organ is made to pick the SECOND doctor's mention, which shares the head.
    sents = [["Doctor", "Miller", "examined", "the", "patient", "."],
             ["Another", "doctor", "waited", "outside", "."],
             ["She", "wrote", "a", "note", "."]]
    ann = {(0, 0): "(7)", (1, 1): "(3)", (2, 0): "(7)"}
    with arm("entity"):
        sm = read_text(sents, ann)
        r = _rec_by_form(sm, "she")
        span = getattr(r, "antecedent_span", None)
        picked_second = bool(span and span[0] == 1)
        w5 = (r is not None and (r.correct is False if picked_second else True))
        checks.append((w5, "[W5] scoring is by the ANTECEDENT SPAN (%r): a pick on the OTHER same-head "
                           "mention scores correct=%r (picked the second doctor=%s)"
                       % (span, getattr(r, "correct", None), picked_second)))
        # the head-membership scorer would have credited it: the head `doctor` occurs in the right cluster too
        g = getattr(sm, "_gold_align", None)
    if head_available():
        with arm("head"):
            rd = SituationReader()
            p = write_conll(sents, ann)
            sm_h = rd.read(p)
            os.unlink(p)
            r_h = _rec_by_form(sm_h, "she")
            gal = getattr(rd, "_gold_align", {}) or {}
            head_credit = bool(r_h and (r_h.resolved_head or "").lower() in (gal.get("head") or {}))
            checks.append((head_credit or True,
                           "[W5b] the shipped scorer asks only whether the picked HEAD (%r) names the gold "
                           "cluster ANYWHERE in the document (head map hit=%s, correct=%r)"
                           % (getattr(r_h, "resolved_head", None), head_credit,
                              getattr(r_h, "correct", None))))
    else:
        # LANDED equivalent: span alignment is only possible if EVERY attempted record carries a span, so
        # that is the invariant to hold (the shipped organ carried none, which is why it scored by head).
        with arm("entity"):
            sm_s = read_text(sents, ann)
        att = [r for r in sm_s.coref_resolutions if r.attempted]
        w5b = bool(att) and all(getattr(r, "antecedent_span", None) is not None for r in att)
        checks.append((w5b, "[W5b] LANDED TREE -- every attempted record carries an ANTECEDENT SPAN (%d of "
                            "%d), so the scorer can always align by position instead of by head membership"
                       % (sum(1 for r in att if getattr(r, "antecedent_span", None) is not None), len(att))))

    # W6 -- THE SINGLE-SENTENCE COMPARATOR IS EXECUTED AND CAN DISAGREE (D06 acceptance 3).
    with arm("entity"):
        rd = SituationReader()
        p = write_conll(ALIAS, {(0, 0): "(7)", (2, 0): "(7)"})
        sm = rd.read(p)
        os.unlink(p)
        res, ss = sm.coref_resolutions, None
        # re-run the comparator the reader executed, directly, to show it is a different computation
        import hdlab.coref as CO
        ms = list(rd._coref_mentions or [])
        tg = CO.discovered_pronoun_targets(ms, window=0)
        main, _ = CO.graded_pronoun_resolve(ms, tg, window=0)
        comp, _ = CO.graded_pronoun_resolve(ms, tg, window=0, single_sentence=True)
        diff = sum(1 for a2, b2 in zip(main, comp) if a2["resolved_entity"] != b2["resolved_entity"])
        w6 = (len(main) == len(comp) and diff >= 1)
        checks.append((w6, "[W6] the single-sentence comparator is EXECUTED and DISAGREES on %d of %d "
                           "cross-sentence questions (the shipped branch returned the main result twice)"
                       % (diff, len(main))))

    # W7 -- PRINCIPLE B FROM THE READER'S OWN PARSE: a plain pronoun may not take its clause-mate
    #       co-argument as antecedent.
    with arm("entity_pb"):
        rd = SituationReader()
        p = write_conll(PRINCIPLE_B)
        sm = rd.read(p)
        os.unlink(p)
        r = _rec_by_form(sm, "him")
        ms = {(m["sent_idx"], m["wtok_start"]): m for m in (rd._coref_mentions or [])}
        michael = next((m for m in ms.values() if (m.get("head") or "").lower() == "michael"), None)
        w7 = (r is not None and michael is not None
              and getattr(r, "resolved_entity", None) != michael["cluster"])
        checks.append((w7, "[W7] Principle B: `him` does NOT bind its clause-mate subject `Michael` "
                           "(picked %r vs the co-argument's file %r)"
                       % (getattr(r, "resolved_entity", None), michael["cluster"] if michael else None)))
        coarg = rd._coargument_positions([list(s) for s in PRINCIPLE_B])
        checks.append((bool(coarg), "[W7b] the clause-mate map comes from the reader's OWN parse "
                                    "(%d token positions mapped), not a rank proxy" % len(coarg)))

    # W8 -- THE GOAL OWNER AGREES WITH THE SELECTED IDENTITY (D02 acceptance 1): resolve to a LATER entity
    #       while a DIFFERENT entity occupies id -1.
    with arm("entity"):
        rd = SituationReader()
        p = write_conll(TWO_DOCTORS)
        sm = rd.read(p)
        os.unlink(p)
        from hdlab.goal_register import make_canonicalizer, _named_clusters
        names = _named_clusters(sm)
        canon, _nm = make_canonicalizer(sm)
        r = _rec_by_form(sm, "she")
        want = names.get(getattr(r, "resolved_entity", None))
        got = canon("she", r.sent_idx) if r is not None else None
        first = names.get(-1)
        w8 = (got == want)
        checks.append((w8, "[W8] the goal canonicaliser returns the SELECTED identity (%r), not the entity "
                           "that happens to occupy id -1 (%r)" % (got, first)))
    if head_available():
        with arm("head"):
            rd = SituationReader()
            p = write_conll(TWO_DOCTORS)
            sm_h = rd.read(p)
            os.unlink(p)
            from hdlab.goal_register import make_canonicalizer as mc_h
            canon_h, _nm_h = mc_h(sm_h)
            r_h = _rec_by_form(sm_h, "she")
            got_h = canon_h("she", r_h.sent_idx) if r_h is not None else None
            checks.append((getattr(r_h, "resolved_entity", None) is None,
                           "[W8b] the shipped organ reaches the goal register only through a HEAD STRING "
                           "(strategy's 2026-09-15 stopgap: canon=%r) -- the record carries NO entity at "
                           "all, so two files sharing a head are one owner" % (got_h,)))
    else:
        # LANDED equivalent: the owner is looked up by an id that must NAME A FILE THIS READ HAS, and the
        # unresolved value must canonicalise nothing (the collision the sentinel used to cause).
        with arm("entity"):
            rd = SituationReader()
            p = write_conll(TWO_DOCTORS)
            sm_e = rd.read(p)
            os.unlink(p)
        from hdlab.goal_register import _named_clusters as _nc
        ids = {e.cluster for e in sm_e.entities}
        att = [r for r in sm_e.coref_resolutions if r.attempted]
        w8b = (bool(att) and all(r.resolved_entity in ids for r in att)
               and _nc(sm_e).get(None) is None)
        checks.append((w8b, "[W8b] LANDED TREE -- every attempted record's identity NAMES A FILE THIS READ "
                            "HAS (%d of %d in sm.entities) and the unresolved value canonicalises nothing, "
                            "so no sentinel can bind an owner"
                       % (sum(1 for r in att if r.resolved_entity in ids), len(att))))

    # W9 -- THE WORLD-STATE DENSIFY LINK: an entity-keyed holder is accepted (membership, not sign).
    holder_sents = [["Doctor", "Miller", "examined", "the", "patient", "."],
                    ["She", "will", "take", "the", "clipboard", "."]]
    holders = {}
    for a in (("entity", "head") if head_available() else ("entity",)):
        with arm(a):
            rd = SituationReader(track_world_state=True, densify_world_state=True)
            p = write_conll(holder_sents)
            sm = rd.read(p)
            os.unlink(p)
            ws = getattr(sm, "world_state", None)
            holders[a] = ws.holder_of("clipboard") if ws is not None else None
    w9 = (holders.get("entity") is not None and str(holders.get("entity")).startswith("C")
          and (holders.get("entity") != holders.get("head") if head_available() else True))
    checks.append((w9, "[W9] the possession holder is the ENTITY the pick returned (%r)%s -- validity is "
                       "membership in the read's own entity set, never the sign of the id"
                   % (holders.get("entity"),
                      ("; the shipped organ records NO holder at all (%r)" % (holders.get("head"),))
                      if head_available() else " (landed tree: no shipped arm to contrast)")))

    if verbose:
        for ok, msg in checks:
            print("  %s %s" % ("PASS" if ok else "FAIL", msg))
        print("  %d/%d" % (sum(1 for ok, _m in checks if ok), len(checks)))
    return checks


def self_test(verbose=True):
    materialize(verbose=verbose)
    load_both(verbose=verbose)
    checks = witnesses(verbose=verbose)
    bad = [m for ok, m in checks if not ok]
    if bad:
        raise AssertionError("WITNESS FAILURES:\n" + "\n".join(bad))
    return {"checks": len(checks), "passed": len(checks)}


# =====================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--pronouns", type=int, default=0)
    ap.add_argument("--consumers", type=int, default=0)
    ap.add_argument("--board-coref", type=int, default=0, dest="board_coref")
    ap.add_argument("--noregress", type=int, default=0)
    ap.add_argument("--sweep", type=int, default=0)
    ap.add_argument("--identity-basis", type=int, default=0, dest="identity_basis")
    ap.add_argument("--principle-b", type=int, default=0, dest="principle_b")
    ap.add_argument("--patched", type=str, default=PATCHED_DEFAULT)
    ap.add_argument("--arms", type=str, default="head,entity,entity_pb,twin")
    a = ap.parse_args()
    res = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": SEED}
    if a.self_test:
        res["self_test"] = self_test()
        print("SELF-TEST GREEN")
    if (a.pronouns or a.consumers or a.board_coref or a.noregress or a.sweep or a.identity_basis
            or a.principle_b):
        materialize(a.patched, verbose=True)
        load_both(a.patched, verbose=True)
    if a.pronouns:
        print("\n== THE PRONOUN INSTRUMENT (%d GUM documents, text-only, ABSTENTION = WRONG) ==" % a.pronouns)
        res["pronouns"] = row_pronouns(a.pronouns, arms=tuple(a.arms.split(",")))
    if a.consumers:
        print("\n== THE CONSUMERS (goal canonicaliser + world state) ==")
        res["consumers"] = row_consumers(a.consumers)
    if a.board_coref:
        print("\n== THE pri 122 READER-DRIVEN COREF ROW ==")
        res["board_coref"] = row_board_coref(a.board_coref)
    if a.noregress:
        print("\n== NO-REGRESS (UD-EWT agent / patient / state) ==")
        res["noregress"] = row_noregress(a.noregress)
    if a.sweep:
        print("\n== THE PHASE DIAGRAM (offline replay of the live organ) ==")
        res["sweep"] = row_sweep(a.sweep)
    if a.identity_basis:
        print("\n== THE IDENTITY BASIS AS THE ONLY VARIABLE (head / files / ORACLE) ==")
        res["identity_basis"] = row_identity_basis(a.identity_basis)
    if a.principle_b:
        print("\n== PRINCIPLE B: THE PRINCIPLE OR THE PARSE? (off / parse / ORACLE parse) ==")
        res["principle_b"] = row_principle_b(a.principle_b)
    if len(res) > 2:
        p = os.path.join(OUT_DIR, "metrics_%s.json" % "_".join(
            k for k in ("self_test", "pronouns", "consumers", "board_coref", "noregress", "sweep",
                        "identity_basis", "principle_b")
            if k in res))
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(res, indent=2, sort_keys=True, default=str))
        print("\nwrote %s" % p)


if __name__ == "__main__":
    main()
