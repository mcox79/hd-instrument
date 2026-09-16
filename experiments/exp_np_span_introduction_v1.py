"""exp_np_span_introduction_v1 -- ONE DISCOURSE REFERENT PER NOUN PHRASE, WITH REAL TOKEN POSITIONS.

THE PROBLEM (pri 138, `the_introduction_organ_opens_one_referent_per_content_noun_token_with_a_bare_head_
span_and_no_global_index_rebuild_it_as_one_referent_per_np_with_the_attachment_arms_span_and_real_token_
positions`).  `hdlab/referent_per_np.py` opened a discourse referent per content-noun TOKEN, stored the bare
lowercased head as the mention's span and wrote `gtok_start = gtok_end = -1`.  So 'the New York Times' was
three referents, no mention could be read for its determiner, and every consumer that needs a position
abstained silently.

THE BRAIN.  One perceived object, one object file (Kahneman, Treisman & Gibbs 1992).  One noun phrase, one
discourse referent (Karttunen 1976; Heim 1982's file card), opened by a DETERMINER PHRASE and not by a noun,
with the determiner read ON the card (Heim's Novelty-Familiarity Condition).  The phrase's head is its
rightmost member in English (Williams 1981's Right-Hand Head Rule).  WHERE it was said is part of the card.
The boundary is the reader's OWN attachment arm (its pre-head dependents) intersected with the category
organ's NP-internal categories and closed at the determiner (the D is the phrase's outermost layer, Abney
1991); post-head dependents are NOT absorbed.  Nothing here is fitted: the boundary is the parse, and the
graded arm is read at its MAP (0.5 IS the MAP boundary, not a swept threshold).

WHAT IS MEASURED HERE (all through the LIVE `SituationReader.read` on annotation-free GUM text, every arm in
ONE process, the paired bootstrap unit the DOCUMENT):
  * `--spans N`   the A table (every hdlab reader of the span, counted with the REAL consumer functions),
                  the entity partition (B-cubed), the board's entity-set re-mention row against its
                  same-head string-identity floor, the pronoun row under BOTH scorers, the crosstype
                  bridge's binds, and the RANDOM-BOUNDARY info-free twin.
  * `--boundary N` the boundary-evidence sweep on the TRAIN split (cat / arc / both / graded).
  * `--build-validities N`  the object-file cue validities RE-ACCRUED on the phrase stream (the `np`
                  adjacency cue was learned on one-token mentions, where it was a STAND-IN for the phrase
                  boundary: gap1_nom 490 same-file vs 16 different).
  * `--bars`      the three acceptance bars strategy added at the pri 136 landing (the entity-set row, the
                  inferred-emotion arm, the goal register's naming).
  * `--noregress N`  UD-EWT agent / patient / state through the live reader, both arms.
  * `--self-test` corpus-free; asserts the DEFECT on the tree as it ships and its ABSENCE once landed.
  * `--verify-landed`  compiles the shipped diff INTO the live modules and re-runs the witness there.

Run: OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 \
     .venv/Scripts/python.exe experiments/exp_np_span_introduction_v1.py --self-test
NO external LLM, no supervised parser, no chunker: the boundary comes from the reader's own organs.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

SEED = 20260916
N_BOOT = 2000

SLUG = ("the_introduction_organ_opens_one_referent_per_content_noun_token_with_a_bare_head_span_and_no_"
        "global_index_rebuild_it_as_one_referent_per_np_with_the_attachment_arms_span_and_real_token_"
        "positions")
DIFF_PATH = os.path.join(_REPO, "notes", "problems", SLUG, "np_span_patch.diff")
PATCH_FILES = ["hdlab/referent_per_np.py", "hdlab/situation_reader.py",
               "hdlab/entity_resolver.py", "hdlab/goal_register.py"]


def get_output_dir(default_name: str = "np_span_introduction_v1"):
    """Q115: the cell writes to the checkpoint's output directory when one is supplied, else its own."""
    try:
        from experiments._seed_checkpoint import get_output_dir as _g
        return _g(default_name)
    except Exception:
        p = os.path.join(_REPO, "data", "exp_" + default_name)
        os.makedirs(p, exist_ok=True)
        return p


OUT_DIR = get_output_dir()
NPSPAN_ASSET = os.path.join(_REPO, "data", "frontend_assets",
                            "object_file_validities_gum_npspan_v1.json")
V1_ASSET = os.path.join(_REPO, "data", "frontend_assets", "object_file_validities_gum_v1.json")


# =====================================================================================================
# 0.  STATISTICS (the shared forms -- paired over ITEMS within DOCUMENTS, the document the bootstrap unit)
# =====================================================================================================
def _p(x, nd=4):
    return "n/a" if x is None else ("%%.%df" % nd) % x


def acc(vs):
    f = [x for d in vs for x in d]
    return (sum(f) / len(f)) if f else 0.0


def paired_boot(a_docs, b_docs, n_boot=N_BOOT, seed=SEED):
    """b - a, resampling DOCUMENTS with replacement (the items inside a document are not independent)."""
    a_docs = [list(x) for x in a_docs]
    b_docs = [list(x) for x in b_docs]
    if not a_docs or len(a_docs) != len(b_docs):
        return None
    if sum(len(x) for x in a_docs) == 0:
        return None
    rng = np.random.default_rng(seed)
    n = len(a_docs)
    d = acc(b_docs) - acc(a_docs)
    out = []
    for _ in range(n_boot):
        ix = rng.integers(0, n, n)
        aa = [x for i in ix for x in a_docs[i]]
        bb = [x for i in ix for x in b_docs[i]]
        if not aa:
            continue
        out.append(sum(bb) / len(bb) - sum(aa) / len(aa))
    if not out:
        return None
    lo, hi = float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))
    return {"delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)],
            "half": round((hi - lo) / 2.0, 4), "sep": bool(lo > 0 or hi < 0),
            "n_items": sum(len(x) for x in a_docs), "n_docs": n}


def _b3(pred, gold):
    gp, gg = defaultdict(set), defaultdict(set)
    for i, (p, g) in enumerate(zip(pred, gold)):
        gp[p].add(i)
        gg[g].add(i)
    n = len(pred)
    if not n:
        return 0.0, 0.0, 0.0
    ps = rs = 0.0
    for i in range(n):
        ov = len(gp[pred[i]] & gg[gold[i]])
        ps += ov / len(gp[pred[i]])
        rs += ov / len(gg[gold[i]])
    p, r = ps / n, rs / n
    return p, r, (2 * p * r / (p + r) if p + r > 0 else 0.0)


def b3_macro(part_rows):
    """B-cubed MACRO-averaged over documents (never pooled -- two documents' file ids would merge)."""
    ps, rs, fs = [], [], []
    for pred, gold in part_rows:
        if not pred:
            continue
        p, r, f = _b3(pred, gold)
        ps.append(p)
        rs.append(r)
        fs.append(f)
    if not fs:
        return {"b3_p": 0.0, "b3_r": 0.0, "b3_f1": 0.0, "n_documents": 0}
    return {"b3_p": round(float(np.mean(ps)), 4), "b3_r": round(float(np.mean(rs)), 4),
            "b3_f1": round(float(np.mean(fs)), 4), "n_documents": len(fs)}


def b3_boot(a_rows, b_rows, n_boot=N_BOOT, seed=SEED):
    """The document-paired bootstrap of the MACRO B-cubed F1 difference (b - a)."""
    if not a_rows or len(a_rows) != len(b_rows):
        return None
    rng = np.random.default_rng(seed + 1)
    n = len(a_rows)
    d = b3_macro(b_rows)["b3_f1"] - b3_macro(a_rows)["b3_f1"]
    out = []
    for _ in range(n_boot):
        ix = rng.integers(0, n, n)
        out.append(b3_macro([b_rows[i] for i in ix])["b3_f1"]
                   - b3_macro([a_rows[i] for i in ix])["b3_f1"])
    lo, hi = float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))
    return {"delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)],
            "half": round((hi - lo) / 2.0, 4), "sep": bool(lo > 0 or hi < 0), "n_docs": n}


# =====================================================================================================
# 1.  THE TREE SHAPE: landed detection, and the shipped diff compiled INTO the live modules otherwise
# =====================================================================================================
def landed() -> bool:
    """TRUE when the proposed organ is LIVE.  Detected by a function ONLY this diff adds (`np_groups` on
    the introduction organ AND `parse_heads` on the reader's tag shim) -- never by a field that could exist
    for another reason."""
    import hdlab.referent_per_np as RPN
    import hdlab.situation_reader as SR
    return bool(getattr(RPN, "np_groups", None) is not None
                and hasattr(getattr(SR, "_CachedTagShim", object), "parse_heads"))


def _apply_diff_sources(diff_path=DIFF_PATH):
    """Apply the shipped diff to its files inside a throwaway temp directory (nothing in the repo is
    written) and return {rel: patched source}.  `git apply` is the applier, so the check is the one
    strategy runs at landing."""
    import shutil
    import tempfile
    d = tempfile.mkdtemp(prefix="pri138_landed_")
    try:
        for rel in PATCH_FILES:
            dst = os.path.join(d, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(_REPO, rel), dst)
        pr = subprocess.run(["git", "apply", "-p1", os.path.abspath(diff_path)],
                            cwd=d, capture_output=True, text=True)
        if pr.returncode != 0:
            raise RuntimeError("git apply failed: %s" % pr.stderr.strip())
        return {rel: io.open(os.path.join(d, rel.replace("/", os.sep)), encoding="utf-8").read()
                for rel in PATCH_FILES}
    finally:
        shutil.rmtree(d, ignore_errors=True)


_INSTALLED = {"done": False}


def install_patch(verbose=True):
    """Compile the shipped diff INTO the live modules (irreversible in-process, so the SHIPPED arm always
    runs FIRST).  A no-op once the diff has landed."""
    if _INSTALLED["done"]:
        return
    if landed():
        _INSTALLED["done"] = True
        if verbose:
            print("  [tree] the organ is LANDED -- every arm runs against the LIVE modules")
        return
    import importlib
    srcs = _apply_diff_sources()
    for rel in PATCH_FILES:
        mod = importlib.import_module(rel[:-3].replace("/", "."))
        exec(compile(srcs[rel], rel, "exec"), mod.__dict__)
    _INSTALLED["done"] = True
    if not landed():
        raise RuntimeError("the patch was installed but landed() still reads False")
    if verbose:
        print("  [tree] the shipped diff is compiled into the live modules (%d files)" % len(PATCH_FILES))


def use_asset(path):
    """Point the object-file competition at ONE validity asset (the module constant is read at call time)."""
    import hdlab.entity_resolver as ER
    ER.OBJECT_FILE_VALIDITY_ASSET = path
    ER.VALIDITY_ASSET = path
    ER._OF_VALIDITIES = None


def set_organ(span=True, collapse=True, boundary=None):
    """The organ's switches, set on the MODULE (its constants are read at import time, so an env flip
    inside a running process would be inert)."""
    import hdlab.referent_per_np as RPN
    RPN.RPN_SPAN = bool(span)
    RPN.RPN_COLLAPSE = bool(collapse)
    if boundary is not None:
        RPN.RPN_BOUNDARY = str(boundary)


# the RANDOM-BOUNDARY info-free twin -----------------------------------------------------------------
_TWIN = {"on": False, "rng": None}


def twin_on(on=True, seed=SEED):
    _TWIN["on"] = bool(on)
    _TWIN["rng"] = random.Random(seed)


def _install_twin_hook():
    """THE INFO-FREE TWIN, installed ONCE: the same mentions, the same COUNT, the same heads and the same
    sentence -- every phrase's LEFT BOUNDARY redrawn at random within its own sentence, at or before its
    head.  Shape, coverage and magnitude preserved; the boundary information destroyed."""
    import hdlab.referent_per_np as RPN
    if getattr(RPN, "_pri138_twin_wrapped", False):
        return
    inner = RPN.referent_per_np_source

    def wrapped(conll_path, tagger, *a, **kw):
        ms, n = inner(conll_path, tagger, *a, **kw)
        if not _TWIN["on"]:
            return ms, n
        from hdlab.scene_segment import parse_conll_sentences
        sents = parse_conll_sentences(conll_path, lower=False)
        offs, acc_ = [], 0
        for s in sents:
            offs.append(acc_)
            acc_ += len(s)
        rng = _TWIN["rng"]
        for m in ms:
            if m.get("is_pronoun"):
                continue
            si = m["sent_idx"]
            if si >= len(sents):
                continue
            h = int(m["wtok_start"]) + max(0, int(m.get("gtok_end", -1)) - int(m.get("gtok_start", -1)))
            a0 = rng.randint(0, h)
            m["wtok_start"] = a0
            m["span_toks"] = [sents[si][k] for k in range(a0, h + 1)]
            m["gtok_start"], m["gtok_end"] = offs[si] + a0, offs[si] + h
            up = m.get("span_upos")
            if up:
                m["span_upos"] = ["X"] * (h - a0) + [up[-1]]
            m.pop("span_post", None)
        return RPN._finalize(ms), n

    RPN.referent_per_np_source = wrapped
    RPN._pri138_twin_wrapped = True


# =====================================================================================================
# 2.  THE CORPUS AND THE LIVE READ
# =====================================================================================================
def gum_docs(n_docs, split="test"):
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    pool = alldocs[1::2] if split == "test" else alldocs[0::2]
    step = max(1, len(pool) // max(1, n_docs))
    docs = [pool[i] for i in range(0, len(pool), step)][:n_docs]
    out = []
    for d in docs:
        pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
        out.append((d, pth))
    return out


def _sents_of(doc):
    per = defaultdict(list)
    for t in doc.toks:
        per[t.sent].append((t.idx, t.form))
    return [[w for _i, w in sorted(v)] for _k, v in sorted(per.items())]


def head_wpos(m) -> int:
    """The mention's HEAD position -- the substrate's own accessor, never re-derived here."""
    from hdlab.graded_role_assigner import mention_head_wpos
    return mention_head_wpos(m)


def gold_at(gold, m):
    """The gold entity this mention names.  The answer key is keyed by the GOLD mention's HEAD token and a
    reader mention is now a whole phrase, so the alignment asks at the PHRASE'S HEAD -- and ONLY there.

    Scanning the whole span was tried first and is WRONG as an instrument: a longer span gets more chances to
    hit a gold head, so the random-boundary twin's population inflated from 229 items to 362 and its score was
    read on a different population from the organ's.  Head-only keeps the population a property of the HEADS,
    which the twin does not touch.  `gold_inside_span_not_at_head` counts what head-only alignment gives up."""
    return gold.get((m["sent_idx"], head_wpos(m)))


def gold_absorbed(gold, ms):
    """How many GOLD mention heads fall INSIDE a reader phrase without being its head -- the gold mentions the
    Right-Hand-Head collapse gives up (the honest cost of one referent per phrase)."""
    n = 0
    for m in ms:
        if m.get("is_pronoun"):
            continue
        h = head_wpos(m)
        for k in range(int(m["wtok_start"]), h):
            if gold.get((m["sent_idx"], k)) is not None:
                n += 1
    return n


# =====================================================================================================
# 3.  THE A TABLE -- every hdlab reader of the span, counted with the REAL consumer functions
# =====================================================================================================
def span_audit(ms, sents, reader=None, base_labels=None):
    from hdlab.coref import mention_span, name_content_tokens
    from hdlab.lexical_utils import definiteness, modifiers
    import hdlab.crosstype_live_adapter as A
    nonp = [m for m in ms if not m.get("is_pronoun")]
    ntok = sum(len(s) for s in sents)
    out = {
        "mentions": len(ms), "non_pronoun": len(nonp),
        "mention_span_extent_gt0": sum(1 for m in nonp if (lambda t: t[2] > t[1])(mention_span(m))),
        "definiteness": dict(Counter(definiteness(m) for m in nonp)),
        "with_modifiers": sum(1 for m in nonp if modifiers(m)),
        "name_typed": sum(1 for m in nonp if name_content_tokens(m.get("span_toks", [m["head"]]),
                                                                upos=m.get("span_upos"))),
        "multi_token_span": sum(1 for m in nonp if len(m.get("span_toks") or []) > 1),
        "gtok_in_range": sum(1 for m in nonp
                             if isinstance(m.get("gtok_start"), int)
                             and isinstance(m.get("gtok_end"), int)
                             and 0 <= m["gtok_start"] <= m["gtok_end"] < ntok),
        "span_upos_len_eq_span": sum(1 for m in nonp
                                     if len(m.get("span_upos") or []) == len(m.get("span_toks") or [])),
    }
    out["definite_readable"] = out["non_pronoun"] - out["definiteness"].get("bare", 0)
    # the crosstype bridge: does a Doc build at all, and how many binds does it license?
    can = None
    binds = 0
    try:
        doc = A.build_gold_free_doc(ms, base_labels or {}, sents, reader=reader)
        can = doc is not None
        if doc is not None:
            from hdlab.entity_resolver import EntityResolver
            binds = len(EntityResolver().bridge_links(doc, getattr(reader, "gaz", None), conf_thr=-3.0) or {})
    except Exception as e:                                        # never break a read to take a count
        out["bridge_error"] = repr(e)[:120]
    out["bridge_doc_built"] = bool(can)
    out["bridge_binds"] = binds
    return out


def same_gold_span_pairs(ms, doc):
    """Cross-FILE mentions that lie inside ONE gold mention -- the 'the New York Times is three files' count.
    The reader mention is located by its HEAD through the corpus's own (sent, wpos) -> global index map, so
    the count does not depend on the very `gtok_*` field this rung repairs."""
    gidx_of = {(t.sent, t.idx - 1): t.gidx for t in doc.toks}
    inside = {}
    for m in doc.mentions:
        for g in range(m.start_g, m.end_g + 1):
            inside.setdefault(g, (m.start_g, m.end_g))
    bygold = defaultdict(set)
    for m in ms:
        if m.get("is_pronoun"):
            continue
        g = gidx_of.get((m["sent_idx"], head_wpos(m)))
        k = inside.get(g) if g is not None else None
        if k is not None:
            bygold[k].add(m.get("cluster"))
    return sum(len(v) - 1 for v in bygold.values() if len(v) > 1)


# =====================================================================================================
# 4.  THE MAIN ROW -- the live read, arm by arm
# =====================================================================================================
def _read_arm(prepared, arm, verbose=True, online=True):
    """Read every prepared document with the LIVE reader under ONE arm; return the per-document capture."""
    from hdlab.situation_reader import SituationReader
    from experiments.exp_pronoun_pick_identity_contract_v1 import gum_questions, _answers, _gold_eid_at
    caps = []
    t0 = time.time()
    for d, pth in prepared:
        rd = SituationReader()
        sm = rd.read(pth)
        ms = [dict(m) for m in (getattr(rd, "_coref_mentions", []) or [])]
        sents = _sents_of(d)
        base = {m["midx"]: m.get("cluster") for m in ms if not m.get("is_pronoun")}
        caps.append({"doc": str(d.docid), "ms": ms, "sents": sents, "sm": sm, "gaz": rd.gaz,
                     "qs": gum_questions(d), "gold": _gold_eid_at(d), "ans": _answers(sm, ms),
                     "audit": span_audit(ms, sents, reader=rd, base_labels=base),
                     "gold_doc": d,
                     "entities": [(e.cluster, list(e.heads), list(getattr(e, "names", None) or []))
                                  for e in (sm.entities or [])]})
    if verbose:
        print("    [%s] %d documents, %d mentions, %.0fs"
              % (arm, len(caps), sum(len(c["ms"]) for c in caps), time.time() - t0))
    return caps


def _pronoun_rows(caps):
    """The pronoun row under BOTH scorers (pri 131/136's instruments, CALLED not re-implemented): the SPAN
    scorer and the IDENTITY scorer (the picked file's majority gold entity)."""
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    span, ident = [], []
    for c in caps:
        span.append([_score_q(q, c["ans"].get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
        maj = defaultdict(Counter)
        for m in c["ms"]:
            if m.get("is_pronoun"):
                continue
            e = gold_at(c["gold"], m)
            if e is not None:
                maj[m.get("cluster")][e] += 1
        best = {f: cnt.most_common(1)[0][0] for f, cnt in maj.items() if cnt}
        row = []
        for q in c["qs"]:
            a = c["ans"].get((q["sent"], q["wpos"])) or {}
            ent = a.get("entity")
            row.append(int(ent is not None and best.get(ent) == q["eid"]))
        ident.append(row)
    return span, ident


def _partition_rows(caps):
    out = []
    for c in caps:
        pred, gold = [], []
        for m in c["ms"]:
            if m.get("is_pronoun"):
                continue
            e = gold_at(c["gold"], m)
            if e is None:
                continue
            pred.append("f%s" % m.get("cluster"))
            gold.append("g%s" % e)
        out.append((pred, gold))
    return out


def _entity_set_rows(caps, pop=None):
    """THE BOARD'S ENTITY-SET ROW (the merge/split decision itself), one item per non-pronoun RE-mention:
    the model is right when the reader filed this mention with the PRIOR mention of the same gold entity.
    Floors on the identical items: same-head STRING IDENTITY and RECENCY.  `pop` (optional) fixes the
    population to another arm's (doc, sent, head) item keys -- an item this arm no longer files counts
    WRONG, which is the conservative apples-to-apples reading when the collapse removes a mention."""
    rng = random.Random(SEED)
    rows = {"model": [], "string_identity": [], "recency": [], "twin": []}
    keys = []
    for c in caps:
        ms = sorted([m for m in c["ms"] if not m.get("is_pronoun")],
                    key=lambda m: (m["sent_idx"], head_wpos(m)))
        seq = []
        for m in ms:
            e = gold_at(c["gold"], m)
            if e is None:
                continue
            seq.append({"file": m.get("cluster"), "eid": e, "head": (m.get("head") or "").lower(),
                        "key": (c["doc"], m["sent_idx"], head_wpos(m))})
        per = {k: [] for k in rows}
        got = {}
        for i, x in enumerate(seq):
            prior = [y for y in seq[:i] if y["eid"] == x["eid"]]
            if not prior:
                continue
            sh = [y for y in seq[:i] if y["head"] == x["head"]]
            tw = rng.choice(seq[:i]) if seq[:i] else None
            got[x["key"]] = {
                "model": int(x["file"] == prior[-1]["file"]),
                "string_identity": int(bool(sh) and sh[-1]["eid"] == x["eid"]),
                "recency": int(seq[i - 1]["eid"] == x["eid"]),
                "twin": int(tw is not None and tw["eid"] == x["eid"])}
        if pop is None:
            for k in rows:
                per[k] = [v[k] for v in got.values()]
            keys += list(got.keys())
        else:
            want = [k for k in pop if k[0] == c["doc"]]
            for k in rows:
                per[k] = [int(got.get(kk, {}).get(k, 0)) for kk in want]
        for k in rows:
            rows[k].append(per[k])
    return rows, keys


def row_spans(n_docs=28, arms=("shipped", "npspan", "twin"), verbose=True, online=True,
              boundary=None, collapse=True):
    """(A) THE RUNG, MEASURED THROUGH THE LIVE READ.  Every arm in ONE process; the SHIPPED arm runs FIRST,
    on the pristine tree, because compiling a diff into a live module is not reversible."""
    prepared = gum_docs(n_docs, split="test")
    out = {"n_docs": len(prepared), "arms": {}, "contrasts": {}, "boundary": boundary or "default",
           "collapse": bool(collapse), "landed_at_start": landed(),
           "n_questions": sum(len(gq) for gq in [])}
    caps = {}
    for a in arms:
        if a == "shipped":
            if landed():
                use_asset(V1_ASSET)
                set_organ(span=False, collapse=False)
                twin_on(False)
        else:
            install_patch(verbose=verbose)
            _install_twin_hook()
            if os.path.exists(NPSPAN_ASSET):
                use_asset(NPSPAN_ASSET)
            set_organ(span=True, collapse=collapse, boundary=boundary)
            twin_on(a == "twin")
        caps[a] = _read_arm(prepared, a, verbose=verbose, online=online)
        aud = Counter()
        defc = Counter()
        for c in caps[a]:
            for k, v in c["audit"].items():
                if k == "definiteness":
                    defc.update(v)
                elif isinstance(v, bool):
                    aud[k] += int(v)
                elif isinstance(v, int):
                    aud[k] += v
        sp, idn = _pronoun_rows(caps[a])
        part = _partition_rows(caps[a])
        es, keys = _entity_set_rows(caps[a])
        out["arms"][a] = {
            "audit": dict(aud), "definiteness": dict(defc),
            "pronoun_span_acc": round(acc(sp), 4), "pronoun_identity_acc": round(acc(idn), 4),
            "pronoun_n": sum(len(x) for x in sp),
            "b3": b3_macro(part),
            "entity_set": {k: round(acc(v), 4) for k, v in es.items()},
            "entity_set_n": sum(len(v) for v in es["model"]),
            "same_gold_span_cross_file_pairs": sum(
                same_gold_span_pairs(c["ms"], c["gold_doc"]) for c in caps[a]),
            "gold_heads_absorbed_into_a_phrase": sum(
                gold_absorbed(c["gold"], c["ms"]) for c in caps[a]),
        }
        out["arms"][a]["_rows"] = {"span": sp, "ident": idn, "part": part, "es": es, "keys": keys}
        if verbose:
            o = out["arms"][a]
            print("    %-9s mentions %5d (%d non-pronoun)  det-readable %4d  gtok-in-range %4d  "
                  "multi-tok %4d  bridge docs %d binds %d  gold heads absorbed %d"
                  % (a, o["audit"]["mentions"], o["audit"]["non_pronoun"],
                     o["audit"]["definite_readable"],
                     o["audit"]["gtok_in_range"], o["audit"]["multi_token_span"],
                     o["audit"]["bridge_doc_built"], o["audit"]["bridge_binds"],
                     o["gold_heads_absorbed_into_a_phrase"]))
            print("    %-9s B3 %s (P %s R %s)  entity_set model %s vs string_identity %s (n=%d)  "
                  "pronoun span %s ident %s  same-gold-span cross-file pairs %d"
                  % (a, _p(o["b3"]["b3_f1"]), _p(o["b3"]["b3_p"]), _p(o["b3"]["b3_r"]),
                     _p(o["entity_set"]["model"]), _p(o["entity_set"]["string_identity"]),
                     o["entity_set_n"], _p(o["pronoun_span_acc"]), _p(o["pronoun_identity_acc"]),
                     o["same_gold_span_cross_file_pairs"]))
    # ---- the contrasts, paired over documents -----------------------------------------------------
    R = {a: out["arms"][a].pop("_rows") for a in arms}
    def C(a, b, tag, f):
        if a in R and b in R:
            out["contrasts"]["%s_vs_%s_%s" % (b, a, tag)] = f(R[a], R[b])
    for b in [x for x in arms if x != "shipped"]:
        C("shipped", b, "b3", lambda x, y: b3_boot(x["part"], y["part"]))
        C("shipped", b, "pronoun_span", lambda x, y: paired_boot(x["span"], y["span"]))
        C("shipped", b, "pronoun_identity", lambda x, y: paired_boot(x["ident"], y["ident"]))
        C("shipped", b, "entity_set", lambda x, y: paired_boot(x["es"]["model"], y["es"]["model"]))
    if "npspan" in R and "twin" in R:
        out["contrasts"]["npspan_vs_twin_b3"] = b3_boot(R["twin"]["part"], R["npspan"]["part"])
        out["contrasts"]["npspan_vs_twin_entity_set"] = paired_boot(R["twin"]["es"]["model"],
                                                                   R["npspan"]["es"]["model"])
    # THE BAR'S OWN POPULATION: the shipped arm's items, an item this arm dropped counting WRONG
    if "shipped" in R and "npspan" in R:
        pop = R["shipped"]["keys"]
        fixed, _ = _entity_set_rows(caps["npspan"], pop=pop)
        out["entity_set_on_shipped_population"] = {
            "n": sum(len(v) for v in fixed["model"]),
            "npspan_model": round(acc(fixed["model"]), 4),
            "shipped_model": round(acc(R["shipped"]["es"]["model"]), 4),
            "shipped_string_identity": round(acc(R["shipped"]["es"]["string_identity"]), 4),
            "npspan_vs_shipped": paired_boot(R["shipped"]["es"]["model"], fixed["model"]),
            "npspan_vs_string_identity": paired_boot(R["shipped"]["es"]["string_identity"],
                                                     fixed["model"])}
        if verbose:
            e = out["entity_set_on_shipped_population"]
            print("    entity_set on the SHIPPED arm's own %d items (a dropped mention counts WRONG):"
                  % e["n"])
            print("      shipped %s | string-identity floor %s | NP-span %s"
                  % (_p(e["shipped_model"]), _p(e["shipped_string_identity"]), _p(e["npspan_model"])))
            for k in ("npspan_vs_shipped", "npspan_vs_string_identity"):
                v = e[k]
                if v:
                    print("      %-26s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                          % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    if verbose:
        for k, v in out["contrasts"].items():
            if v:
                print("      %-34s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    out["_caps"] = caps
    return out


# =====================================================================================================
# 5.  THE BOUNDARY-EVIDENCE SWEEP (on the TRAIN split -- the operating point is chosen here)
# =====================================================================================================
def row_boundary(n_docs=12, verbose=True):
    """Which EVIDENCE draws the phrase boundary?  cat = the category run alone (arc-free); arc = the
    attachment arm's projection alone; both = the conjunction; graded = both, with the arm's GRADED head
    belief deciding a token the hard arc rejects (MAP membership).  TRAIN split."""
    install_patch(verbose=verbose)
    prepared = gum_docs(n_docs, split="train")
    out = {"n_docs": len(prepared), "split": "train", "modes": {}}
    for mode in ("cat", "arc", "both", "graded"):
        set_organ(span=True, collapse=True, boundary=mode)
        twin_on(False)
        caps = _read_arm(prepared, mode, verbose=False)
        part = _partition_rows(caps)
        es, _k = _entity_set_rows(caps)
        aud = Counter()
        for c in caps:
            for k, v in c["audit"].items():
                if isinstance(v, bool):
                    aud[k] += int(v)
                elif isinstance(v, int):
                    aud[k] += v
        out["modes"][mode] = {"mentions": aud["mentions"], "multi_token": aud["multi_token_span"],
                              "det_readable": aud["definite_readable"],
                              "b3": b3_macro(part),
                              "entity_set_model": round(acc(es["model"]), 4),
                              "entity_set_string_identity": round(acc(es["string_identity"]), 4),
                              "entity_set_n": sum(len(v) for v in es["model"])}
        if verbose:
            o = out["modes"][mode]
            print("    %-7s mentions %5d  multi-tok %4d  det %4d  B3 %s  entity_set %s (floor %s, n=%d)"
                  % (mode, o["mentions"], o["multi_token"], o["det_readable"], _p(o["b3"]["b3_f1"]),
                     _p(o["entity_set_model"]), _p(o["entity_set_string_identity"]), o["entity_set_n"]))
    return out


# =====================================================================================================
# 6.  THE VALIDITIES, RE-ACCRUED ON THE PHRASE STREAM
# =====================================================================================================
def build_validities(n_docs=24, verbose=True, out_path=None, cue_set="v1"):
    """THE OBSERVE PATH'S STARTING EQUILIBRIUM, re-accrued on the NOUN-PHRASE stream.

    The `np` adjacency cue was counted on ONE-TOKEN mentions, where two adjacent nominal heads are almost
    always the same NOUN PHRASE (gap1_nom 490 same-file vs 16 different): the cue was a STAND-IN for the
    boundary this rung draws, and on the phrase stream the NP-INTERNAL observations are GONE by construction
    -- what is left at gap1/gap2 is the CROSS-PHRASE adjacency (close apposition, a name beside its title).
    The counts are therefore re-accrued through the same teacher on the same GUM TRAIN split, the reader's
    own live phrase stream supplying the mentions and the gold partition supplying `same`/`different`.
    Nothing gold is read at inference; the asset is a static, re-buildable offline foundation with the online
    accrual (`observe_file_decision`) continuing to move it as the reader reads."""
    install_patch(verbose=verbose)
    set_organ(span=True, collapse=True)
    twin_on(False)
    use_asset(V1_ASSET)                      # the teacher SCORES with the current table, then rewrites it
    import hdlab.entity_resolver as ER
    from experiments.exp_object_file_competition_v1 import (Validities, file_cues, _definiteness)
    from hdlab.coref import EntityAliaser, name_content_tokens
    from hdlab.lexical_utils import concept_lemma
    from hdlab.typed_spokes import available_entity_type
    prepared = gum_docs(n_docs, split="train")
    caps = _read_arm(prepared, "npspan(train)", verbose=verbose)
    V = Validities(cue_set=cue_set)
    have_spoke = available_entity_type()
    tot = Counter()
    for c in caps:
        aliaser = EntityAliaser()
        files = {}                            # gold entity -> a pseudo-file accumulating its mentions
        ms = sorted([m for m in c["ms"] if not m.get("is_pronoun")],
                    key=lambda m: (m["sent_idx"], m["wtok_start"], m["midx"]))
        prev_cb = None
        for order, m in enumerate(ms):
            e = gold_at(c["gold"], m)
            if e is None:
                continue
            span = m.get("span_toks", [m["head"]])
            head = concept_lemma(m["head"])
            gender = m.get("gender") or m.get("name_gender")
            number = m.get("number")
            surf = str(m["head"]).lower()
            wpos = int(m.get("wtok_start", -99))
            wend = wpos + max(0, int(m.get("gtok_end", -1)) - int(m.get("gtok_start", -1)))
            upos = (m.get("span_upos") or [""])[-1] or ""
            is_name = bool(name_content_tokens(span, upos=m.get("span_upos")))
            canon = aliaser.assign(span, gender, upos=m.get("span_upos")) if is_name else None
            definite = _definiteness(span, c["sents"], m["sent_idx"], wpos)
            for e2, f in files.items():
                cu = file_cues(m, f, head=head, canon=canon, surf=surf, gender=gender, number=number,
                               definite=definite, is_name=is_name, sent_idx=m["sent_idx"],
                               prev_cb=prev_cb, name_link=None, have_spoke=have_spoke,
                               wpos=wpos, upos=upos, sents=c["sents"], cue_set=V.cue_set)
                V.observe(cu, e2 == e)
                tot["same" if e2 == e else "different"] += 1
            V.observe_criterion(definite, e not in files)
            f = files.get(e)
            if f is None:
                f = files[e] = ER.OFile(len(files))
            rk = m.get("sent_role_rank", 99)
            role = "SUBJECT" if rk == 0 else ("OBJECT" if rk == 1 else "OTHER")
            f.update(order, role, gender, number, head, m["sent_idx"], canon, surf, is_name,
                     wpos=wend, upos=upos)
            tot["mentions"] += 1
    V.recompute()
    p = out_path or NPSPAN_ASSET
    V.save(p)
    doc = V.to_json()
    doc["source"] = ("object-file merge/split cue validities RE-ACCRUED on the NOUN-PHRASE mention stream "
                     "(pri 138: one referent per NP with real spans, so the `np` cue counts the gap BETWEEN "
                     "phrases, not inside one); counts from GUM TRAIN gold partitions through the reader's "
                     "own live phrase stream + the reader's own high-margin decisions online; "
                     "strength = log P(value|same) - log P(value|different)")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=1, sort_keys=True))
    out = {"n_docs": len(caps), "asset": p, "counts": dict(tot), "cue_set": V.cue_set,
           "np_counts": {k: list(v) for k, v in V.counts["np"].items()},
           "np_strength": {k: round(v, 4) for k, v in V.strength["np"].items()},
           "criterion_counts": {k: list(v) for k, v in V.crit.items()},
           "criterion_shift": {k: round(v, 4) for k, v in V.crit_shift.items()}}
    if verbose:
        print("    accrued %d mentions -> %d same / %d different pair observations; wrote %s"
              % (tot["mentions"], tot["same"], tot["different"], os.path.basename(p)))
        for k, v in sorted(out["np_counts"].items()):
            print("      np/%-14s same %7.0f  different %7.0f  strength %+.3f"
                  % (k, v[0], v[1], out["np_strength"][k]))
    return out


# =====================================================================================================
# 7.  THE THREE BARS strategy ADDED AT THE pri 136 LANDING
# =====================================================================================================
def row_bars(verbose=True, smoke=False):
    """(1) the inferred-emotion arm (occ_appraisal, 50 constructed modern items, two sentences each) with
    the object-file competition ON, and (2) the goal register's NAMING: does the register name a file by its
    PROPER NAME when the card holds one?  Both arms in ONE process, the shipped arm first."""
    from experiments import exp_occ_appraisal_emotion_v1 as OCCX
    out = {"arms": {}}
    for arm in ("shipped", "npspan"):
        if arm == "shipped":
            if landed():
                use_asset(V1_ASSET)
                set_organ(span=False, collapse=False)
        else:
            install_patch(verbose=verbose)
            if os.path.exists(NPSPAN_ASSET):
                use_asset(NPSPAN_ASSET)
            set_organ(span=True, collapse=True)
        gold = OCCX.load_gold() if hasattr(OCCX, "load_gold") else None
        recs = OCCX.extract_all(gold, smoke=smoke) if gold is not None else OCCX.extract_all(smoke=smoke)
        got = _occ_score(recs, gold)
        out["arms"][arm] = got
        if verbose:
            print("    %-9s occ_appraisal %s (n=%d)  goal owner named %d/%d  owner is a NAME %d"
                  % (arm, _p(got["acc"]), got["n"], got["owner_found"], got["n"], got["owner_is_name"]))
    a, b = out["arms"].get("shipped"), out["arms"].get("npspan")
    if a and b:
        out["contrast"] = paired_boot([a["items"]], [b["items"]])
    return out


def _occ_score(recs, gold):
    """Score the appraisal records against the constructed gold, and COUNT the goal register's naming."""
    n = ok = own = nm = 0
    items = []
    for r in (recs or []):
        n += 1
        pred = (r.get("pred") if isinstance(r, dict) else getattr(r, "pred", None))
        g = (r.get("gold") if isinstance(r, dict) else getattr(r, "gold", None))
        items.append(int(pred is not None and g is not None and pred == g))
        ok += items[-1]
        owner = (r.get("goal_owner") if isinstance(r, dict) else getattr(r, "goal_owner", None))
        if owner:
            own += 1
            nm += int(str(owner).strip()[:1].isupper() or str(owner).lower() in
                      {"maya", "leo", "ana", "sam", "tom", "mia", "noah", "ivy"})
    return {"n": n, "acc": round(ok / n, 4) if n else None, "owner_found": own,
            "owner_is_name": nm, "items": items}


def row_goal_naming(n_docs=6, verbose=True):
    """THE NAMING BAR, on the reader's OWN GUM read: for every entity file that holds a NAME, does
    `goal_register._cluster_name` return that name?  A card's label is its name (Kripke 1980; Semenza
    2006's proper-name route), and with whole-phrase mentions the longest-surface rule returns a
    common-noun phrase instead."""
    out = {"arms": {}}
    prepared = gum_docs(n_docs, split="test")
    for arm in ("shipped", "npspan"):
        if arm == "shipped":
            if landed():
                use_asset(V1_ASSET)
                set_organ(span=False, collapse=False)
        else:
            install_patch(verbose=verbose)
            if os.path.exists(NPSPAN_ASSET):
                use_asset(NPSPAN_ASSET)
            set_organ(span=True, collapse=True)
        twin_on(False)
        import hdlab.goal_register as GR
        from hdlab.situation_reader import SituationReader
        tot = Counter()
        for d, pth in prepared:
            rd = SituationReader()
            sm = rd.read(pth)
            for e in (sm.entities or []):
                names = list(getattr(e, "names", None) or [])
                nm = GR._cluster_name(sm, e.cluster)
                if not names:
                    tot["files_without_a_name"] += 1
                    continue
                tot["files_with_a_name"] += 1
                tot["named_by_its_name" if (nm and nm.lower() in {x.lower() for x in names})
                    else "named_by_something_else"] += 1
        out["arms"][arm] = dict(tot)
        if verbose:
            print("    %-9s files holding a name %d -> named by it %d, by something else %d"
                  % (arm, tot["files_with_a_name"], tot["named_by_its_name"],
                     tot["named_by_something_else"]))
    return out


# =====================================================================================================
# 8.  NO-REGRESS (the other consumers of the entity layer)
# =====================================================================================================
def row_noregress(n_docs=10, verbose=True):
    """UD-EWT agent / patient / state through the LIVE reader, both arms in ONE process (the shipped arm
    first).  The positional word-order cues read `wtok_start`; the repair moves it to the span start, so
    this is where a flip would show."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    from hdlab.situation_reader import SituationReader
    docs = P.load_ud_docs()[:n_docs]
    out = {"n_docs": len(docs), "arms": {}}
    rows = {}
    for arm in ("shipped", "npspan"):
        if arm == "shipped":
            if landed():
                use_asset(V1_ASSET)
                set_organ(span=False, collapse=False)
        else:
            install_patch(verbose=verbose)
            if os.path.exists(NPSPAN_ASSET):
                use_asset(NPSPAN_ASSET)
            set_organ(span=True, collapse=True)
        twin_on(False)
        per = {"agent": [], "patient": [], "state": []}
        for _docid, gold in docs:
            sents = [[t["form"] for t in s] for s in gold]
            pth = P.write_conll(sents)
            try:
                sm = SituationReader().read(pth)
            finally:
                try:
                    os.unlink(pth)
                except OSError:
                    pass
            sc = P.score_doc(sm, gold)
            for k in per:
                per[k].append(sc.get(k, []))
        rows[arm] = per
        out["arms"][arm] = {k: round(acc(v), 4) for k, v in per.items()}
        out["arms"][arm]["n"] = {k: sum(len(x) for x in v) for k, v in per.items()}
        if verbose:
            print("    %-9s %s" % (arm, json.dumps(out["arms"][arm], sort_keys=True)))
    if "shipped" in rows and "npspan" in rows:
        out["contrasts"] = {k: paired_boot(rows["shipped"][k], rows["npspan"][k])
                            for k in ("agent", "patient", "state")}
        if verbose:
            for k, v in out["contrasts"].items():
                if v:
                    print("      %-9s d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                          % (k, v["delta"], v["ci"][0], v["ci"][1], v["sep"]))
    return out


# =====================================================================================================
# 9.  SELF-TEST (corpus-free) -- asserts the DEFECT before landing and its ABSENCE after
# =====================================================================================================
_FIX = ["The", "old", "baker", "gave", "the", "New", "York", "Times", "a", "loaf", "."]
_FIX_UP = ["DET", "ADJ", "NOUN", "VERB", "DET", "PROPN", "PROPN", "PROPN", "DET", "NOUN", "PUNCT"]
# 1-based child -> head, the shape the attachment arm returns for this sentence
_FIX_HEADS = {1: 3, 2: 3, 3: 4, 4: 0, 5: 8, 6: 8, 7: 8, 8: 4, 9: 10, 10: 4, 11: 4}


def self_test(verbose=True):
    fails = []
    _ck = {"n": 0}

    def ck(ok, msg):
        _ck["n"] += 1
        print(("  PASS " if ok else "  FAIL ") + msg)
        if not ok:
            fails.append(msg)

    import hdlab.referent_per_np as RPN
    # ---- T1: the DEFECT, asserted on the tree as it ships -----------------------------------------
    if not landed():
        ck(RPN._mk_referent("baker", 0, 2, 1, -1, upos="NOUN")["gtok_start"] == -1,
           "T1 DEFECT PRESENT on the shipped tree: the organ writes gtok_start = -1")
        ck(RPN._mk_referent("baker", 0, 2, 1, -1, upos="NOUN")["span_toks"] == ["baker"],
           "T1b DEFECT PRESENT on the shipped tree: span_toks is the bare head")
    install_patch(verbose=verbose)
    set_organ(span=True, collapse=True, boundary="both")
    gov = {j - 1: h - 1 for j, h in _FIX_HEADS.items()}

    # ---- T2: ONE referent per NP, the right-hand head surviving ------------------------------------
    grp = RPN.np_groups(_FIX, _FIX_UP, [2, 5, 6, 7, 9], gov, None, "both")
    ck(sorted(grp) == [2, 7, 9],
       "T2 one referent per NOUN PHRASE: heads {2,5,6,7,9} -> {2,7,9} ('the old baker', "
       "'the New York Times', 'a loaf'); got %s" % sorted(grp))
    ck(grp.get(2, (None,))[0] == 0,
       "T2b the determiner is INSIDE the phrase: 'the old baker' starts at 0 (got %s)"
       % (grp.get(2, (None,))[0],))
    ck(grp.get(7, (None,))[0] == 4,
       "T2c the name run is ONE phrase: 'the New York Times' starts at 4 (got %s)"
       % (grp.get(7, (None,))[0],))
    ck(grp.get(7, (None, None, []))[2] == [5, 6],
       "T2d its two absorbed heads are recorded (got %s)" % (grp.get(7, (None, None, []))[2],))

    # ---- T3: a determiner CLOSES the phrase (two DPs are not one) ----------------------------------
    t3 = ["the", "dog", "the", "cat", "saw", "."]
    t3u = ["DET", "NOUN", "DET", "NOUN", "VERB", "PUNCT"]
    ck(RPN.np_left_edge(t3, t3u, 3, None, None, "cat") == 2,
       "T3 the determiner is the phrase's outermost layer: 'the cat' does not swallow 'the dog' "
       "(edge %d)" % RPN.np_left_edge(t3, t3u, 3, None, None, "cat"))

    # ---- T4: a post-head modifier is NOT absorbed --------------------------------------------------
    t4 = ["the", "baker", "of", "York"]
    t4u = ["DET", "NOUN", "ADP", "PROPN"]
    g4 = {0: 1, 1: -1, 2: 3, 3: 1}
    ck(RPN.np_groups(t4, t4u, [1, 3], g4, None, "both").get(1, (None,))[0] == 0
       and 3 in RPN.np_groups(t4, t4u, [1, 3], g4, None, "both"),
       "T4 a POST-head dependent stays its own referent ('the baker' | 'York')")

    # ---- T5: the phrase can never cross its clause's verb -----------------------------------------
    ck(RPN.np_left_edge(_FIX, _FIX_UP, 9, gov, None, "both") >= 8,
       "T5 the phrase stops at the verb: 'a loaf' cannot reach back past 'gave' (edge %d)"
       % RPN.np_left_edge(_FIX, _FIX_UP, 9, gov, None, "both"))

    # ---- T6: the canonical schema, and the head recovered by the substrate's own accessor ----------
    m = RPN._mk_referent("baker", 0, 2, 1, -1, upos="NOUN",
                         span=["The", "old", "baker"], span_upos=["DET", "ADJ", "NOUN"],
                         gtok=(0, 2), wstart=0)
    from hdlab.graded_role_assigner import mention_head_wpos
    ck(m["wtok_start"] == 0 and m["gtok_start"] == 0 and m["gtok_end"] == 2
       and m["span_toks"] == ["The", "old", "baker"],
       "T6 the CANONICAL schema: wtok_start = the span start, the raw-cased span, a real global extent")
    ck(mention_head_wpos(m) == 2,
       "T6b graded_role_assigner.mention_head_wpos recovers the head (got %d)" % mention_head_wpos(m))
    from hdlab.lexical_utils import definiteness, modifiers
    ck(definiteness(m) == "def", "T6c Heim's determiner is READABLE on the card (%s)" % definiteness(m))
    ck(set(modifiers(m)) == {"old"}, "T6d the descriptive content is on the card (%s)" % modifiers(m))
    from hdlab.coref import mention_span
    ck(mention_span(m) == (0, 0, 2), "T6e coref.mention_span returns the real extent (%s)" % (mention_span(m),))

    # ---- T7: the DEFECT IS ABSENT on the landed tree ----------------------------------------------
    ck(landed(), "T7 landed() reads True from the LIVE modules")
    import hdlab.situation_reader as SR
    ck(hasattr(SR._CachedTagShim, "parse_heads"),
       "T7b the reader serves its SHARED per-read parse to the introduction organ (no second parse)")

    # ---- T8: the switch restores the pre-2026-09-16 organ byte-for-byte ---------------------------
    set_organ(span=False, collapse=False)
    m0 = RPN._mk_referent("baker", 0, 2, 1, -1, upos="NOUN",
                          span=["The", "old", "baker"], span_upos=["DET", "ADJ", "NOUN"],
                          gtok=(0, 2), wstart=0)
    ck(m0["gtok_start"] == -1 and m0["span_toks"] == ["baker"] and m0["wtok_start"] == 2,
       "T8 HDLAB_RPN_SPAN off restores every field byte-for-byte (the A/B switch)")
    set_organ(span=True, collapse=True)

    # ---- T9: the info-free twin destroys the boundary and keeps the count -------------------------
    _install_twin_hook()
    ck(getattr(RPN, "_pri138_twin_wrapped", False), "T9 the random-boundary twin hook installs")

    # ---- T10: the graded arm reads the arm's belief at its MAP, with no fitted threshold -----------
    ck(RPN._graded_inside({3: {3: 0.9}}, 2, 2, 2) is True
       and RPN._graded_inside({3: {9: 0.9, 3: 0.1}}, 2, 2, 2) is False,
       "T10 the graded boundary is the MAP of the arm's head belief (no fitted threshold)")

    # ---- T11: the file card's LABEL is its name ----------------------------------------------------
    import hdlab.goal_register as GR
    from hdlab.situation_reader import TrackedEntity
    class _SM(object):
        entities = [TrackedEntity(cluster=1, heads=["the community championship", "maya"],
                                  sent_indices=[0], n_mentions=2, is_person=True, names=["maya"])]
    ck(GR._cluster_name(_SM(), 1) == "maya",
       "T11 a file card is labelled by its NAME, not by its longest surface (%s)"
       % GR._cluster_name(_SM(), 1))

    print("  %d checks, %d FAIL" % (_ck["n"], len(fails)))
    return {"n_checks": _ck["n"], "fails": fails, "ok": not fails}


def verify_landed(verbose=True):
    """Compile the shipped diff into the live modules and assert the DEFECT'S ABSENCE on that tree shape."""
    srcs = _apply_diff_sources()
    for rel in PATCH_FILES:
        compile(srcs[rel], rel, "exec")
        print("  PASS  %s applies with `git apply` and compiles (%d lines)"
              % (rel, srcs[rel].count("\n")))
    return self_test(verbose=verbose)


# =====================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--verify-landed", action="store_true", dest="verify_landed")
    ap.add_argument("--spans", type=int, default=0)
    ap.add_argument("--arms", type=str, default="shipped,npspan,twin")
    ap.add_argument("--boundary", type=str, default=None)
    ap.add_argument("--no-collapse", action="store_true", dest="no_collapse")
    ap.add_argument("--boundary-sweep", type=int, default=0, dest="boundary_sweep")
    ap.add_argument("--build-validities", type=int, default=0, dest="build_validities")
    ap.add_argument("--cue-set", type=str, default="v1", dest="cue_set")
    ap.add_argument("--asset", type=str, default=None)
    ap.add_argument("--bars", action="store_true")
    ap.add_argument("--goal-naming", type=int, default=0, dest="goal_naming")
    ap.add_argument("--noregress", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": SEED, "landed": landed()}
    if a.self_test:
        print("\n== SELF-TEST ==")
        res["self_test"] = self_test()
    if a.verify_landed:
        print("\n== VERIFY LANDED ==")
        res["verify_landed"] = verify_landed()
    if a.build_validities:
        print("\n== THE VALIDITIES, RE-ACCRUED ON THE NOUN-PHRASE STREAM (GUM TRAIN) ==")
        res["build_validities"] = build_validities(a.build_validities, out_path=a.asset,
                                                   cue_set=a.cue_set)
    if a.boundary_sweep:
        print("\n== THE BOUNDARY-EVIDENCE SWEEP (TRAIN) ==")
        res["boundary_sweep"] = row_boundary(a.boundary_sweep)
    if a.spans:
        print("\n== ONE REFERENT PER NOUN PHRASE, THROUGH THE LIVE READ (GUM TEST) ==")
        out = row_spans(a.spans, arms=tuple(x for x in a.arms.split(",") if x),
                        boundary=a.boundary, collapse=not a.no_collapse)
        out.pop("_caps", None)
        res["spans"] = out
    if a.bars:
        print("\n== THE INFERRED-EMOTION BAR (occ_appraisal) ==")
        res["bars"] = row_bars(smoke=a.smoke)
    if a.goal_naming:
        print("\n== THE NAMING BAR: a file card is labelled by its NAME ==")
        res["goal_naming"] = row_goal_naming(a.goal_naming)
    if a.noregress:
        print("\n== NO-REGRESS (UD-EWT agent / patient / state) ==")
        res["noregress"] = row_noregress(a.noregress)
    if len(res) > 3:
        os.makedirs(OUT_DIR, exist_ok=True)
        p = os.path.join(OUT_DIR, "metrics_%s.json" % "_".join(
            k for k in ("self_test", "verify_landed", "build_validities", "boundary_sweep", "spans",
                        "bars", "goal_naming", "noregress") if k in res))
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(res, indent=2, sort_keys=True, default=str))
        print("\nwrote %s" % p)


if __name__ == "__main__":
    main()
