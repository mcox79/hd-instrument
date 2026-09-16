"""exp_board_rows_on_the_reader_v1 -- SCORE THE READER THE OWNER RUNS.

problem: the_boards_seven_rows_never_run_the_reader_each_rebuilds_its_own_copy_from_annotated_cased_files_so_a_
         reader_repair_worth_0_41_propn_f1_is_board_invisible_rebuild_the_rows_on_the_live_reader   (pri 122)

WHAT IS WRONG (pri 116 measured it exactly): none of the 19c-free board's SEVEN headline rows calls
`SituationReader.read`.  Each rebuilds its own copy of the read from the annotated corpus files -- its own
mention stream, its own candidate lists, its own organ layer -- so the reader's own sentence source, in-order
feed, memo, entity register and event stream are never on the scored path.  The sentence-source call count is
0 on every row in both arms of pri 116's A/B, and a repair worth +0.4106 PROPN F1 through the live reader left
all seven rows BYTE-IDENTICAL.

WHAT THIS CELL DOES: it re-derives each row's MODEL ANSWER from `SituationReader(gaz).read(path)` -- ONE read
per document, shared by every row that reads that document -- and scores it against the SAME answer key, with
every floor RECOMPUTED IN PLACE on the reader's own population and an information-free twin per row.  Each row
carries a PROVENANCE field saying, in words, which token stream it read and whether the annotation column was
supplied.

THE PROVENANCE AXIS THAT TURNED OUT TO MATTER (substrate evaluation E02/E07, 2026-09-15; re-measured here):
the reader's pronoun mentions come ONLY from the CoNLL coref column (`referent_per_np_source` seeds its
pronoun list from `parse_litbank_conll`), and the Competition-Model AGENT candidate set is that same
coref-column stream (`situation_reader._cm_agent_candidates` reads `self._coref_mentions`).  So EVERY row is
published TWICE:
    reader_annotated -- the reader's own read of the document, with the annotated coref column supplied
                        (THE READER'S CURRENT INPUT CONTRACT -- what `read()` is built to receive)
    reader_textonly  -- the identical read with the coref column blanked to `_` (annotation-free text)
The honest product number is `reader_textonly` wherever the reader is asked to comprehend raw prose; the
`reader_annotated` number is the reader's contract-satisfied number.  Both are published with their provenance
so neither can travel without the other.

ROWS AND WHERE THE READ COMES FROM
  coref (pronoun)        GUM   sm.coref_resolutions            (answer key: the GUM coref chains)
  salience               GUM   sm.entities (most-mentioned)     (answer key: the most-mentioned gold entity)
  common_noun_coref      GUM   sm.commonnoun_resolution         (answer key: the GUM coref chains)
  who_did_what_agent     UD    sm.events[].agent               (answer key: gold nsubj / obl:agent)
  who_did_what_patient   UD    sm.events[].patient             (answer key: gold obj / nsubj:pass)
  state                  UD    sm.entity_states                (answer key: gold cop predicational clauses)
  wic                    WiC   sm.select_sense (the read-BOUND closure, not the organ called directly)

GLASS-BOX: no external LLM, no spaCy, no nltk tagger, no supervised parser at inference.  MODERN gold only
(GUM / UD-EWT / WiC).  Floors recomputed per arm on that arm's own items; info-free twin per row; item- or
document-paired bootstrap with CI half-widths.  Writes ONLY to its own get_output_dir.

Run: .venv/Scripts/python.exe experiments/exp_board_rows_on_the_reader_v1.py --self-test
     ... --run [--docs N] [--ud-cap N] [--wic-cap N]          (all three corpora + the comparison table)
     ... --gum --docs 16      ... --ud --ud-cap 400      ... --wic --wic-cap 60
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import sys, argparse, json, time, random, tempfile, shutil
from collections import defaultdict, Counter
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir
ANCHOR = "board_rows_on_the_reader_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260915
UD_CHUNK = 20          # UD-EWT sentences per pseudo-document handed to read() (reported; sentences are independent)
# Extra SituationReader kwargs for a landing A/B arm (empty = the shipped default reader). Set by landings().
READER_KW = {}


# ---------------------------------------------------------------------------------------------------
# PROVENANCE -- the field the brief asks every row to carry, in plain words.
# ---------------------------------------------------------------------------------------------------
def provenance(mode, corpus, source):
    """mode in {reader_annotated, reader_textonly, rebuilt}."""
    if mode == "rebuilt":
        return {"read_by": "rebuilt in the board cell (SituationReader.read NOT called)",
                "token_stream": "loader", "case": "cased (the loader reads the FORM column raw)",
                "annotation_supplied": "yes -- the row reads the annotated file's own columns",
                "corpus": corpus, "model_source": source,
                "plain": "a rebuilt read from the annotated file"}
    ann = {"reader_annotated": "yes -- the coref column is supplied",
           "reader_textonly": "no -- the coref column is blanked to _",
           "reader_textonly_pron_discovered":
               "no gold -- the mention column carries a SINGLETON span on every token the reader's OWN "
               "category organ tags PRON (a prototype of the missing pronoun-introduction rung)"}[mode]
    plain = {"reader_annotated": "the reader's own read of the text, with the annotation column supplied",
             "reader_textonly": "the reader's own read of the raw text alone",
             "reader_textonly_pron_discovered":
                 "the reader's own read of the raw text, with the pronouns it can see itself opened as "
                 "referents"}[mode]
    return {"read_by": "SituationReader.read(path)",
            "token_stream": "reader (scene_segment.parse_conll_sentences)",
            "case": "cased (lower=False since pri 116)", "annotation_supplied": ann,
            "corpus": corpus, "model_source": source, "plain": plain}


# ---------------------------------------------------------------------------------------------------
# SHARED STATISTICS -- paired bootstrap over CLUSTERS (documents for GUM, sentences for UD), CI half-width.
# ---------------------------------------------------------------------------------------------------
def _paired(cl_a, cl_b, n_boot=2000, seed=SEED):
    """cl_a / cl_b: dict cluster -> (hits, tot) for two arms on the SAME items. Returns (delta, lo, hi, hw, sep)."""
    keys = sorted(set(cl_a) | set(cl_b))
    if not keys:
        return 0.0, 0.0, 0.0, 0.0, False
    A = np.array([[cl_a.get(k, (0, 0))[0], cl_a.get(k, (0, 0))[1]] for k in keys], float)
    B = np.array([[cl_b.get(k, (0, 0))[0], cl_b.get(k, (0, 0))[1]] for k in keys], float)

    def rate(M, idx):
        t = M[idx, 1].sum()
        return (M[idx, 0].sum() / t) if t else np.nan
    allidx = np.arange(len(keys))
    obs = rate(B, allidx) - rate(A, allidx)
    rng = np.random.default_rng(seed)
    ds = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(keys), len(keys))
        a, b = rate(A, idx), rate(B, idx)
        if a == a and b == b:
            ds.append(b - a)
    if not ds:
        return float(obs), 0.0, 0.0, 0.0, False
    ds = np.array(ds)
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    return float(obs), lo, hi, (hi - lo) / 2.0, bool(lo > 0)


def _rate(cl):
    h = sum(v[0] for v in cl.values()); t = sum(v[1] for v in cl.values())
    return ((h / t) if t else float("nan")), t


def _r4(x):
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if x != x else round(x, 4)


def _row(name, arms, model_key, floor_keys, twin_key, population, prov, n_boot=2000, seed=SEED, extra=None):
    """Build the board's per_dimension row schema from {arm_name: {cluster: (hits, tot)}}."""
    accs = {k: _rate(v)[0] for k, v in arms.items()}
    m, n = _rate(arms.get(model_key, {}))
    fk = [k for k in floor_keys if k in arms and _rate(arms[k])[1] > 0 and accs[k] == accs[k]]
    fname = max(fk, key=lambda k: accs[k]) if fk else None
    fl = accs[fname] if fname else None
    d_f = _paired(arms[fname], arms[model_key], n_boot, seed) if fname else (None, None, None, None, False)
    d_t = (_paired(arms[twin_key], arms[model_key], n_boot, seed + 1)
           if twin_key in arms else (None, None, None, None, False))
    row = {
        "n": int(n), "model_acc": _r4(m),
        "overlap_floor": _r4(fl),
        "floor_accs": {k: _r4(accs[k]) for k in floor_keys if k in arms},
        "strongest_floor_name": fname, "strongest_floor": _r4(fl),
        "twin_acc": _r4(accs.get(twin_key)),
        "model_minus_strongest": [_r4(d_f[0]), _r4(d_f[1]), _r4(d_f[2])],
        "model_minus_twin": [_r4(d_t[0]), _r4(d_t[1]), _r4(d_t[2])],
        "ci_sep_over_strongest": bool(d_f[4]), "ci_sep_over_twin": bool(d_t[4]),
        "ci_half_width_strongest": _r4(d_f[3]), "ci_half_width_twin": _r4(d_t[3]),
        "population": population, "provenance": prov, "row": name,
    }
    if extra:
        row.update(extra)
    return row


def _install_role_snapshot(reader):
    """Keep the reader's OWN role-mention stream (the text-derived referent-per-NP source) reachable for
    scoring, WITHOUT touching hdlab: wrap the bound method on this INSTANCE only.  The snapshot is read-only --
    the reader's behaviour is byte-identical (asserted in --self-test)."""
    orig = reader._resolve_commonnouns

    def wrapped(role_mentions, sents):
        reader._role_mentions_snapshot = list(role_mentions)
        return orig(role_mentions, sents)
    reader._resolve_commonnouns = wrapped
    reader._role_mentions_snapshot = []


# ===================================================================================================
# PART A -- GUM documents through the live reader:  coref (pronoun) / salience / common_noun_coref
# ===================================================================================================
def _gum_test_docs(n_docs=None, prefix=False):
    """The board's own GUM split: TEST = odd document index; decision_source from the live default (organ).

    A document CAP is an EVENLY SPACED subsample of that split, not its first n documents: GUM files are named
    by genre (GUM_academic_*, GUM_bio_*, ... GUM_whow_*) and sort that way, so a prefix cap would hand the
    reader one or two genres and call it the modern board.  `prefix=True` (the self-test only) takes the cheap
    prefix instead, which lets it load 2*n documents rather than all 257."""
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz, decision_source=G.DECISION_SOURCE,
                       limit=(2 * n_docs if (n_docs and prefix) else None))
    test = [d for i, d in enumerate(docs) if i % 2 == 1]
    if n_docs and n_docs < len(test):
        if prefix:
            test = test[:n_docs]
        else:
            step = len(test) / float(n_docs)
            test = [test[int(i * step)] for i in range(n_docs)]
    return test, gaz


def _write_two_conll(doc, dirpath):
    """(annotated_path, textonly_path). The annotated file is the reader's current input contract (gold coref
    brackets = the mention spans + clusters); the text-only file is the identical token stream with the coref
    column blanked, i.e. annotation-free prose."""
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    p_ann = os.path.join(dirpath, doc.docid + ".ann.conll")
    gum_to_conll(doc, p_ann)
    p_txt = os.path.join(dirpath, doc.docid + ".txt.conll")
    with open(p_ann, encoding="utf-8") as fh, open(p_txt, "w", encoding="utf-8") as out:
        for ln in fh:
            s = ln.rstrip("\n")
            if s.startswith("#") or not s.strip():
                out.write(s + "\n")
                continue
            c = s.split("\t")
            c[-1] = "_"
            out.write("\t".join(c) + "\n")
    # THE PROTOTYPE ARM: the same annotation-free token stream, with a SINGLETON mention on every token the
    # READER'S OWN CATEGORY ORGAN tags PRON.  No gold column is read: the spans come from the organ.
    from hdlab.scene_segment import parse_conll_sentences
    sents = parse_conll_sentences(p_txt, lower=False)
    prn = set(_organ_pron_positions(sents))
    p_prn = os.path.join(dirpath, doc.docid + ".prn.conll")
    k = 900000
    si, w = -1, 0
    with open(p_txt, encoding="utf-8") as fh, open(p_prn, "w", encoding="utf-8") as out:
        started = False
        for ln in fh:
            s = ln.rstrip("\n")
            if s.startswith("#"):
                out.write(s + "\n")
                continue
            if not s.strip():
                out.write("\n")
                started = False
                continue
            if not started:
                si += 1
                w = 0
                started = True
            c = s.split("\t")
            if (si, w) in prn:
                c[-1] = "(%d)" % k
                k += 1
            w += 1
            out.write("\t".join(c) + "\n")
    return p_ann, p_txt, p_prn


def _organ_pron_positions(sents):
    """(sent_idx, wtok) of every token THE CATEGORY ORGAN ITSELF tags PRON -- no gold column, no gazetteer,
    the same organ (hdlab.frontend.tagger() -> hdlab.lexical_categories) the reader runs.  This is the
    PROTOTYPE of the missing rung: a pronoun is a referent-introducing expression, so the organ that decides
    categories is what should be opening the referent.  It LOCATES the signal; the landed form is the organ's
    own pronoun discovery inside `referent_per_np_source` (pri 125), not this injection."""
    from hdlab import frontend as F
    tg = F.tagger()
    out = []
    for si, toks in enumerate(sents):
        up = tg.tag(list(toks))
        for w, c in enumerate(up):
            if c == "PRON":
                out.append((si, w))
    return out


def _gold_eid_by_wpos(doc):
    """(sent_idx, wtok) of a GOLD mention's HEAD token -> its gold entity id. The ANSWER KEY only."""
    gmap = {t.gidx: t for t in doc.toks}
    out = {}
    for m in doc.mentions:
        t = gmap.get(m.head_g)
        if t is not None:
            out.setdefault((t.sent, t.idx - 1), m.eid)
    return out


def _reader_pronoun_targets(ms, reader=None):
    """The reader's OWN pronoun question set: `coref.discovered_pronoun_targets` when the substrate has it
    (the gold-gate-free builder), else `build_pronoun_targets` (today's shipped gate). Returns a list whose
    entries carry a "target" mention, which is all the floors need."""
    import hdlab.coref as CO
    fn = getattr(CO, "discovered_pronoun_targets", None)
    if fn is not None:
        for kw in ({"reader": reader}, {}):
            try:
                tg = fn(ms, **kw) if kw else fn(ms)
                return list(tg)
            except TypeError:
                continue
            except Exception:
                break
    return list(CO.build_pronoun_targets(ms))


def score_gum_doc(doc, sm, reader, rng):
    """Score the three GUM rows for ONE document from the SituationModel the live reader returned.
    Every floor and the twin are computed on the reader's OWN items -- the identical decision list."""
    out = {"coref": defaultdict(lambda: [0, 0]), "salience": defaultdict(lambda: [0, 0]),
           "common_noun_coref": defaultdict(lambda: [0, 0])}
    diag = {}

    # ---------------- coref (pronoun): the reader's OWN resolutions --------------------------------
    # THE QUESTION SET IS WHICHEVER ONE THE READER ITSELF USED. Today that is `build_pronoun_targets` (whose
    # population is gated on a shared GOLD cluster id -- see the SOLVED); when the organ that replaces it
    # lands (`discovered_pronoun_targets`, pri 125), this picks it up WITHOUT an edit here, so the row starts
    # reporting a population the moment the upstream gate is opened instead of silently staying at n=0.
    # 2026-09-15 (strategy, pri 131 landing; the row's ANSWER KEY was the reader's own fresh singleton id --
    # exp_board_rows_on_the_reader_v1.py:333 in the landed form -- so model, floors and twin all scored 0 once
    # pri 125 discovered pronouns): the answer key is the GUM GOLD ENTITY at the target's position, the model's
    # answer is the gold entity at the picked ANTECEDENT SPAN (pri 131's contract: entity + span, None = abstain),
    # ABSTENTION = WRONG, and a target with no gold entity at its position is UNSCOREABLE (counted, excluded).
    ms = list(getattr(reader, "_coref_mentions", []) or [])
    res = list(sm.coref_resolutions)
    eid_at = _gold_eid_by_wpos(doc)
    diag["n_coref_mentions"] = len(ms)
    diag["n_reader_resolutions"] = len(res)
    scoreable = [r for r in res if (r.sent_idx, getattr(r, "target_wpos", -1)) in eid_at]
    diag["n_coref_scoreable"] = len(scoreable)
    diag["n_coref_unscoreable"] = len(res) - len(scoreable)
    diag["coref_aligned"] = bool(scoreable)

    def _span_eid(span):
        if not span:
            return None
        si, a, b = span[0], span[1], span[2] if len(span) > 2 else span[1]
        for w in range(int(a), int(b) + 1):
            e = eid_at.get((si, w))
            if e is not None:
                return e
        return None

    for r in scoreable:
        tpos = (r.sent_idx, r.target_wpos)
        gold = eid_at[tpos]
        ans = _span_eid(getattr(r, "antecedent_span", None))
        out["coref"]["model"][0] += int(ans is not None and ans == gold)
        out["coref"]["model"][1] += 1
        # the floors and the twin pick among the reader's OWN prior non-pronoun mentions, mapped to gold ids
        prior = [m for m in ms if not m.get("is_pronoun") and (m["sent_idx"], m["wtok_start"]) < tpos]
        prior.sort(key=lambda m: (m["sent_idx"], m["wtok_start"]))
        meid = lambda m: eid_at.get((m["sent_idx"], m["wtok_start"] + max(0, m.get("gtok_end", 0) - m.get("gtok_start", 0))),
                                    eid_at.get((m["sent_idx"], m["wtok_start"])))
        rec = prior[-1] if prior else None                       # FLOOR recency
        out["coref"]["recency"][0] += int(rec is not None and meid(rec) == gold)
        out["coref"]["recency"][1] += 1
        same = [m for m in prior                                  # FLOOR same-surface string identity
                if (m.get("head") or "").lower() == (r.pronoun or "").lower()]
        out["coref"]["string_identity"][0] += int(bool(same) and meid(same[-1]) == gold)
        out["coref"]["string_identity"][1] += 1
        g = ""                                                    # FLOOR agreement-compatible recency
        for m in ms:
            if (m["sent_idx"], m["wtok_start"]) == tpos:
                g = m.get("gender") or ""
                break
        comp = [m for m in prior if (not g) or (m.get("gender") in ("", None, g))]
        out["coref"]["compatible_recency"][0] += int(bool(comp) and meid(comp[-1]) == gold)
        out["coref"]["compatible_recency"][1] += 1
        tw = rng.choice(prior) if prior else None                 # TWIN info-free
        out["coref"]["twin"][0] += int(tw is not None and meid(tw) == gold)
        out["coref"]["twin"][1] += 1

    # ---------------- salience: the reader's most-mentioned entity ---------------------------------
    gold_counts = defaultdict(int)
    for m in doc.mentions:
        gold_counts[m.eid] += 1
    gmap = {t.gidx: t for t in doc.toks}
    gold_heads = defaultdict(set)                    # eid -> lowercased surface heads (the answer key)
    for m in doc.mentions:
        t = gmap.get(m.head_g)
        if t is not None:
            gold_heads[m.eid].add(t.form.lower())
    ents = list(sm.entities)
    diag["n_reader_entities"] = len(ents)
    rms_all = list(getattr(reader, "_role_mentions_snapshot", []) or [])
    eid_by_pos_all = _gold_eid_by_wpos(doc)
    pos_by_cluster = defaultdict(list)                # the reader's own entity -> its own mention POSITIONS
    for m in rms_all:
        pos_by_cluster[m.get("cluster")].append((m["sent_idx"], m["wtok_start"]))
    if gold_counts and len(ents) >= 2:
        gold_main = max(gold_counts, key=lambda e: (gold_counts[e], -e))

        def mapped(ent):
            """The reader entity's gold identity = the DOMINANT gold entity over its OWN mentions' positions
            (the board's rebuilt salience row uses exactly this majority-eid rule over its cluster's
            mentions); the surface-head overlap is the fallback when no mention position lines up."""
            c = Counter()
            for p in pos_by_cluster.get(ent.cluster, []):
                e = eid_by_pos_all.get(p)
                if e is not None:
                    c[e] += 1
            if c:
                return c.most_common(1)[0][0]
            hs = {str(h).lower() for h in (ent.heads or [])}
            best, bn = None, 0
            for eid, ghs in gold_heads.items():
                k = len(hs & ghs)
                if k > bn or (k == bn and k > 0 and (best is None or gold_counts[eid] > gold_counts[best])):
                    best, bn = eid, k
            return best if bn > 0 else None
        model_e = max(ents, key=lambda e: (e.n_mentions, -min(e.sent_indices or [0])))
        first_e = min(ents, key=lambda e: (min(e.sent_indices or [10 ** 6]), -e.n_mentions))
        twin_e = rng.choice(ents)
        out["salience"]["model"][0] += int(mapped(model_e) == gold_main)
        out["salience"]["model"][1] += 1
        out["salience"]["first_introduced_entity"][0] += int(mapped(first_e) == gold_main)
        out["salience"]["first_introduced_entity"][1] += 1
        out["salience"]["twin"][0] += int(mapped(twin_e) == gold_main)
        out["salience"]["twin"][1] += 1

    # ---------------- common-noun coref: the reader's OWN per-mention resolution -------------------
    cnr = list(getattr(sm, "commonnoun_resolution", []) or [])
    rms = list(getattr(reader, "_role_mentions_snapshot", []) or [])
    diag["n_commonnoun_records"] = len(cnr)
    if cnr and rms:
        eid_by_pos = _gold_eid_by_wpos(doc)
        by_midx = {m["midx"]: m for m in rms}
        gold_first = {}
        for m in doc.mentions:
            gold_first.setdefault(m.eid, m.order)
        gold_order = {}
        for m in doc.mentions:
            t = gmap.get(m.head_g)
            if t is not None:
                gold_order.setdefault((t.sent, t.idx - 1), m.order)
        recs = []
        for r in cnr:
            m = by_midx.get(r["midx"])
            if m is None:
                continue
            key = (m["sent_idx"], m["wtok_start"])
            fin = r.get("resolved_ref") if r.get("resolved_ref") is not None else r.get("own_ref")
            recs.append({"midx": r["midx"], "mtype": r.get("mtype"), "ref": fin,
                         "eid": eid_by_pos.get(key), "head": (m.get("head") or "").lower(),
                         "order": gold_order.get(key)})
        recs.sort(key=lambda x: x["midx"])
        diag["commonnoun_coverage"] = [sum(1 for x in recs if x["eid"] is not None), len(recs)]
        for i, x in enumerate(recs):
            if x["mtype"] != "common" or x["eid"] is None or x["order"] is None:
                continue
            if gold_first.get(x["eid"], 10 ** 9) >= x["order"]:
                continue                                  # not anaphoric: this mention introduces the entity
            prior = [y for y in recs[:i] if y["eid"] is not None]
            same_ref = [y for y in prior if y["ref"] == x["ref"]]      # MODEL: the reader's own referent
            out["common_noun_coref"]["model"][0] += int(bool(same_ref) and same_ref[-1]["eid"] == x["eid"])
            out["common_noun_coref"]["model"][1] += 1
            sh = [y for y in prior if y["head"] == x["head"]]          # FLOOR same-head string identity
            out["common_noun_coref"]["string_identity"][0] += int(bool(sh) and sh[-1]["eid"] == x["eid"])
            out["common_noun_coref"]["string_identity"][1] += 1
            out["common_noun_coref"]["recency"][0] += int(bool(prior) and prior[-1]["eid"] == x["eid"])
            out["common_noun_coref"]["recency"][1] += 1
            tw = rng.choice(prior) if prior else None                  # TWIN info-free
            out["common_noun_coref"]["twin"][0] += int(tw is not None and tw["eid"] == x["eid"])
            out["common_noun_coref"]["twin"][1] += 1
    return {k: {a: tuple(v) for a, v in d.items()} for k, d in out.items()}, diag




# ---------------------------------------------------------------------------------------------------
# ENTITY SET -- the reader's OWN entity partition (pri 136).  The organ that builds it
# (`hdlab.entity_resolver.cluster`) is measured CI-separated better on B-cubed while the pronoun row has
# an arithmetic ceiling of ~+0.015 for ANY clustering change, so the clustering's quality is invisible to
# every existing row.  This row scores the MERGE/SPLIT DECISION ITSELF, on the reader's own mentions.
# ---------------------------------------------------------------------------------------------------
def _b3(pred, gold):
    """B-cubed P/R/F over mention-aligned label lists (the contract of
    exp_commonnoun_coref_diagnostic_v1.b3)."""
    n = len(pred)
    if n == 0:
        return 0.0, 0.0, 0.0
    gp, gg = defaultdict(set), defaultdict(set)
    for i in range(n):
        gp[pred[i]].add(i)
        gg[gold[i]].add(i)
    ps = rs = 0.0
    for i in range(n):
        ov = len(gp[pred[i]] & gg[gold[i]])
        ps += ov / len(gp[pred[i]])
        rs += ov / len(gg[gold[i]])
    p, r = ps / n, rs / n
    return p, r, (2 * p * r / (p + r) if p + r > 0 else 0.0)


def score_entity_set(doc, sm, reader, rng):
    """THE MERGE/SPLIT DECISION, one item per re-mention.  For every NON-pronoun mention the reader filed
    that has a PRIOR mention of the same gold entity, the model is right when the reader put it in the SAME
    file as that prior mention.  Floors on the IDENTICAL items: same-head STRING IDENTITY (the strongest
    simple rule) and RECENCY (the immediately preceding mention).  The info-free TWIN files it with a random
    prior mention's file.  ALSO returns the set-level B-cubed over every mention that carries a gold entity,
    for the model and for the string-identity floor, as an `extra` field -- the partition number itself,
    which is not a per-item rate and so cannot go through `_row`."""
    out = {"entity_set": defaultdict(lambda: [0, 0])}
    eid_at = _gold_eid_by_wpos(doc)
    ms = [m for m in (getattr(reader, "_coref_mentions", []) or []) if not m.get("is_pronoun")]
    ms = sorted(ms, key=lambda m: (m["sent_idx"], m["wtok_start"]))
    rows = []
    for m in ms:
        e = eid_at.get((m["sent_idx"], int(m["wtok_start"])))
        if e is None:
            continue
        rows.append({"file": m.get("cluster"), "eid": e, "head": (m.get("head") or "").lower()})
    seen_files, seen_heads = {}, {}
    for i, x in enumerate(rows):
        prior = [y for y in rows[:i] if y["eid"] == x["eid"]]
        if not prior:                                  # this mention INTRODUCES the entity: no decision
            seen_files.setdefault(x["eid"], x["file"])
            seen_heads.setdefault(x["head"], x["eid"])
            continue
        out["entity_set"]["model"][0] += int(x["file"] == prior[-1]["file"])
        out["entity_set"]["model"][1] += 1
        sh = [y for y in rows[:i] if y["head"] == x["head"]]
        out["entity_set"]["string_identity"][0] += int(bool(sh) and sh[-1]["eid"] == x["eid"])
        out["entity_set"]["string_identity"][1] += 1
        out["entity_set"]["recency"][0] += int(bool(rows[:i]) and rows[i - 1]["eid"] == x["eid"])
        out["entity_set"]["recency"][1] += 1
        tw = rng.choice(rows[:i]) if rows[:i] else None
        out["entity_set"]["twin"][0] += int(tw is not None and tw["eid"] == x["eid"])
        out["entity_set"]["twin"][1] += 1
    b3 = {}
    if rows:
        gold = ["g%s" % x["eid"] for x in rows]
        b3["model"] = [round(v, 4) for v in _b3(["f%s" % x["file"] for x in rows], gold)]
        b3["string_identity"] = [round(v, 4) for v in _b3([x["head"] for x in rows], gold)]
    return {k: {a: tuple(v) for a, v in d.items()} for k, d in out.items()}, {"entity_set_b3": b3,
                                                                             "entity_set_n": len(rows)}



def _pooled_b3(diag_rows):
    """The set-level B-cubed MACRO-AVERAGED over documents (each document scored on its own mentions, then
    averaged -- never pooled, because two documents' file ids would otherwise merge into one cluster).
    Reported BESIDE the per-item rate, never instead of it: B-cubed is not a per-item rate and cannot go
    through `_row`'s bootstrap."""
    got = [d.get("entity_set_b3") or {} for d in diag_rows]
    out = {}
    for arm in ("model", "string_identity"):
        vals = [g[arm] for g in got if g.get(arm)]
        if vals:
            out[arm] = {"b3_p": round(sum(v[0] for v in vals) / len(vals), 4),
                        "b3_r": round(sum(v[1] for v in vals) / len(vals), 4),
                        "b3_f1": round(sum(v[2] for v in vals) / len(vals), 4),
                        "n_documents": len(vals)}
    return out


GUM_MODES = ("reader_annotated", "reader_textonly", "reader_textonly_pron_discovered")


def run_gum(n_docs=None, n_boot=2000, seed=SEED, modes=GUM_MODES):
    """ONE read per document per provenance mode; all three GUM rows scored off that one SituationModel."""
    from hdlab.situation_reader import SituationReader
    t0 = time.time()
    test, gaz = _gum_test_docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="brotr_")
    per = {m: {r: defaultdict(dict) for r in ("coref", "salience", "common_noun_coref", "entity_set")} for m in modes}
    diags = {m: [] for m in modes}
    try:
        for d in test:
            p_ann, p_txt, p_prn = _write_two_conll(d, tmp)
            for mode in modes:
                path = {"reader_annotated": p_ann, "reader_textonly": p_txt,
                        "reader_textonly_pron_discovered": p_prn}[mode]
                rdr = SituationReader(gaz=gaz, **READER_KW)
                _install_role_snapshot(rdr)
                sm = rdr.read(path)
                rng = random.Random(abs(hash((d.docid, mode))) % 100000)
                sc, dg = score_gum_doc(d, sm, rdr, rng)
                sc_e, dg_e = score_entity_set(d, sm, rdr, rng)
                sc.update(sc_e)
                dg.update(dg_e)
                dg["docid"] = d.docid
                dg["n_toks"] = len(d.toks)
                diags[mode].append(dg)
                for rname, arms in sc.items():
                    for a, ht in arms.items():
                        per[mode][rname][a][d.docid] = ht
                del sm, rdr
            for p in (p_ann, p_txt, p_prn):
                try:
                    os.remove(p)
                except OSError:
                    pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    cap_note = (" DOCUMENT CAP: %d of the split's %d test documents, EVENLY SPACED (whole documents; never an "
                "item cap)." % (len(test), n_docs) if n_docs else
                " DOCUMENT CAP: none -- the whole test split (%d documents)." % len(test))
    rows = {}
    for mode in sorted(modes):
        rows[mode] = {}
        rows[mode]["coref"] = _row(
            "coref", per[mode]["coref"], "model",
            ["compatible_recency", "recency", "string_identity"], "twin",
            "GUM (modern, TEST=odd docs) PRONOUN anaphora, THE READER'S OWN population: every pronoun the live "
            "reader RESOLVED (sm.coref_resolutions; pri 125 discovers the pronouns from text, pri 131 returns the "
            "entity + antecedent span) whose position carries a GOLD entity -- the answer key is that gold entity, "
            "the model's answer is the gold entity at its antecedent span, ABSTENTION = WRONG, unscoreable targets "
            "counted separately; floors + info-free twin recomputed on the IDENTICAL question list over the reader's "
            "own prior mentions; document-paired bootstrap." + cap_note,
            provenance(mode, "GUM", "sm.coref_resolutions"), n_boot, seed,
            extra={"reader_docs_cap": n_docs, "n_documents": len(test)})
        rows[mode]["salience"] = _row(
            "salience", per[mode]["salience"], "model", ["first_introduced_entity"], "twin",
            "GUM (modern, TEST) main-character salience, one item per document: model = the reader's "
            "MOST-MENTIONED sm.entities entry mapped to a gold entity by surface-head overlap; floor = the "
            "reader's FIRST-introduced entity (a position baseline); twin = a random reader entity. "
            "Document-paired bootstrap." + cap_note,
            provenance(mode, "GUM", "sm.entities"), n_boot, seed,
            extra={"reader_docs_cap": n_docs, "n_documents": len(test)})
        rows[mode]["common_noun_coref"] = _row(
            "common_noun_coref", per[mode]["common_noun_coref"], "model",
            ["string_identity", "recency"], "twin",
            "GUM (modern, TEST) anaphoric COMMON-NOUN mentions the reader itself filed: model = the most recent "
            "prior mention sharing the referent sm.commonnoun_resolution assigned; floors (same-head string "
            "identity / recency) + info-free twin on the identical items; document-paired bootstrap."
            + cap_note,
            provenance(mode, "GUM", "sm.commonnoun_resolution"), n_boot, seed,
            extra={"reader_docs_cap": n_docs, "n_documents": len(test)})
        rows[mode]["entity_set"] = _row(
            "entity_set", per[mode]["entity_set"], "model",
            ["string_identity", "recency"], "twin",
            "GUM (modern, TEST) the reader's OWN ENTITY PARTITION -- the merge/split decision itself, one "
            "item per re-mention: every NON-pronoun mention the reader filed whose position carries a GOLD "
            "entity that a PRIOR mention also carries; the model is right when the reader put it in the SAME "
            "file as that prior mention. Floors on the identical items: same-head string identity (the "
            "strongest simple rule) and recency; info-free twin = a random prior mention's file. The "
            "set-level B-cubed for the model and the string-identity floor is carried in `entity_set_b3` "
            "(a partition score, not a per-item rate). Document-paired bootstrap." + cap_note,
            provenance(mode, "GUM", "sm.entities / the reader's own mention files"), n_boot, seed,
            extra={"reader_docs_cap": n_docs, "n_documents": len(test),
                   "entity_set_b3": _pooled_b3(diags[mode])})
    return {"rows": rows, "diag": diags, "n_docs": len(test), "per": per,
            "docids": [d.docid for d in test],
            "n_toks": sum(len(d.toks) for d in test),
            "elapsed_s": round(time.time() - t0, 1)}


# ===================================================================================================
# PART A2 -- WHERE-IS through the live reader:  the SPACE dimension's own row (pri 137, 2026-09-16)
# ===================================================================================================
# WHY THIS ROW EXISTS. `track_space` is DEFAULT-ON, so the reader builds a per-entity location register on every
# read -- and NOTHING on the board scored it. The board's two spatial rows (`spatial_relational`,
# `spatial_extraction_precision`) run a DIFFERENT organ (spatial_relation_extractor / joint_relation_frontend) on
# SpartQA/SpaceEval; neither touches `sm.locations`. A regression in the where-is chain was therefore invisible,
# which is how pri 137's defect survived a week: its only end-to-end check switched the lever off in a module the
# reader no longer ran, so ON == OFF by construction (0.3830 both arms, 2026-09-16).
#
# HONEST SCOPE, STATED IN THE ROW'S OWN PROVENANCE: the only where-is gold on disk is the 8 AUTHOR-CONSTRUCTED
# modern passages of `exp_space_where_is_modern_v1` (n=47 query items over 8 character timelines). That is a
# WEAKER instrument than a found corpus and is labelled as such -- a corpus-age control, not a found modern
# corpus. It is still the only row that scores the space dimension end-to-end through `SituationReader.read`.
#
# THE QUESTION IS ASKED BY THE READER'S OWN FILE (the pri 131 identity contract): the register's track keys are
# the reader's own entity ids, so gold cluster ids align the question to the file the reader put the
# protagonist's mentions in, AFTER every decision. `reader._space_stream` (pri 137) is that stream; on a tree
# without it the row falls back to the gold id, which is the same answer whenever the reader has not re-filed
# the protagonist.
def _where_is_file(reader, gold_mentions):
    """The register key to ask: the file the reader itself put the protagonist's mentions in (majority over the
    answer key's own mention positions). Gold is read AFTER the read, never inside a decision."""
    stream = getattr(reader, "_space_stream", None)
    if not stream:
        # NO READER FILE ON THIS TREE (pri 137 not landed): fall back to the gold id and SAY SO -- the
        # register's keys are the reader's OWN files, so a gold-keyed question can answer None for a reason
        # that has nothing to do with the space chain. nfiles=0 marks the row as a LOWER BOUND.
        return "0", 0
    pos = {(m["sent_idx"], m["wtok_start"]): m["cluster"] for m in stream}
    cand = {}
    for m in gold_mentions:
        if m["cluster"] == 0:
            c = pos.get((m["sent_idx"], m["wtok_start"]))
            if c is not None:
                cand[c] = cand.get(c, 0) + 1
    if not cand:
        return "0", 0
    return str(max(cand.items(), key=lambda kv: (kv[1], -abs(kv[0])))[0]), len(cand)


def _blank_coref_column(src, dst):
    """The identical token stream with the coref column blanked -- annotation-free prose."""
    with open(src, encoding="utf-8") as fh, open(dst, "w", encoding="utf-8") as out:
        for ln in fh:
            t = ln.rstrip("\n")
            if t.startswith("#") or not t.strip():
                out.write(t + "\n")
                continue
            c = t.split("\t")
            c[-1] = "_"
            out.write("\t".join(c) + "\n")
    return dst


def run_where_is(n_boot=2000, seed=SEED, modes=("reader_annotated", "reader_textonly")):
    """The SPACE dimension scored through the live reader: where is the protagonist at clause t?"""
    import numpy as _np
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import parse_litbank_conll
    from hdlab.scene_segment import parse_conll_sentences
    from hdlab import space_reader as _SP
    import experiments.exp_space_where_is_modern_v1 as MOD
    from experiments.exp_space_where_is_end_to_end_v1 import (
        gold_at, correct, floor_lastment, _place_positions, _mention_gidx)
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    t0 = time.time()
    gaz = load_given_gazetteer()
    tmp = tempfile.mkdtemp(prefix="brotr_wi_")
    per = {m: defaultdict(dict) for m in modes}
    files_per_protagonist = {m: [] for m in modes}
    _ORIG_GB = _SP.ground_bind_events
    try:
        for mode in modes:
            for arm in ("model", "twin", "lastment", "abstain"):
                # the INFO-FREE TWIN keeps every firing of the named-ground pass and scrambles the ground
                # content (the landed twin: ground_bind_events(shuffle_rng=...)).
                if arm == "twin":
                    _SP.ground_bind_events = (lambda *a, **k: _ORIG_GB(
                        *a, **dict(k, shuffle_rng=_np.random.default_rng(seed))))
                else:
                    _SP.ground_bind_events = _ORIG_GB
                for p in MOD.PASSAGES:
                    cp = MOD.write_conll(p, tmp)
                    path = cp if mode == "reader_annotated" else _blank_coref_column(
                        cp, os.path.join(tmp, p[0] + ".txt.conll"))
                    rows = sorted(MOD.build_gold(p), key=lambda r: r["t"])
                    gold_m, _ = parse_litbank_conll(cp)      # the ANSWER KEY, read after the decision
                    hits = tot = 0
                    reg = key = sents = places = None
                    if arm in ("model", "twin"):
                        rdr = SituationReader(gaz=gaz, **READER_KW)
                        sm = rdr.read(path)
                        reg = sm.locations
                        key, nfiles = _where_is_file(rdr, gold_m)
                        if arm == "model":
                            files_per_protagonist[mode].append(nfiles)
                    else:
                        sents = parse_conll_sentences(cp, lower=False)
                        places = _place_positions(sents)
                    f, l = rows[0]["t"], rows[-1]["t"] + 20
                    for t in sorted({m["sent_idx"] for m in gold_m
                                     if m["cluster"] == 0 and f <= m["sent_idx"] <= l}):
                        g = gold_at(rows, t)
                        if g is None:
                            continue
                        if arm in ("model", "twin"):
                            pred = reg.where_is(key, t) if reg is not None else None
                        elif arm == "lastment":
                            pred = floor_lastment(places, _mention_gidx(sents, gold_m, 0, t), t)
                        else:
                            pred = None
                        hits += correct(pred, g[0])
                        tot += 1
                    per[mode][arm][p[0]] = (hits, tot)
                    if arm in ("model", "twin"):
                        del sm, rdr
    finally:
        _SP.ground_bind_events = _ORIG_GB
        shutil.rmtree(tmp, ignore_errors=True)
    rows_out = {}
    for mode in modes:
        rows_out[mode] = {"where_is": _row(
            "where_is", per[mode], "model", ["lastment", "abstain"], "twin",
            "WHERE-IS: the protagonist's location node at clause t, read off the live reader's own "
            "sm.locations (the Zwaan & Radvansky SPACE dimension; track_space is default-ON). One item per "
            "clause at which the answer key places the protagonist and the reader has seen a mention of them; "
            "8 AUTHOR-CONSTRUCTED modern passages (the corpus-age control of exp_space_where_is_modern_v1 -- a "
            "WEAKER instrument than a found corpus, and the only where-is gold on disk), n=47 items over 8 "
            "character timelines; the question is asked BY THE READER'S OWN ENTITY FILE (gold ids align the "
            "question after the read, never inside a decision); strongest simple floor = the stateless "
            "last-mention place noun, second floor = abstain; info-free twin = the named-ground pass firing "
            "exactly as often with its ground content scrambled; passage-paired bootstrap.",
            provenance(mode, "modern where-is passages (author-constructed)", "sm.locations.where_is"),
            n_boot, seed,
            extra={"n_documents": len(MOD.PASSAGES),
                   "files_per_protagonist": files_per_protagonist[mode],
                   "alignment": ("the entity file the reader itself used (pri 137 _space_stream)"
                                 if any(files_per_protagonist[mode]) else
                                 "GOLD ID FALLBACK: the reader file is not exposed on this tree, so a "
                                 "protagonist the reader re-filed answers None and the model number is "
                                 "a LOWER BOUND"),
                   "instrument_note": "the passage tokenizer splits on WHITESPACE ONLY, so 64 of 615 tokens "
                                      "(10.4%) reach the reader with attached punctuation ('room.'), which the "
                                      "category organ correctly calls PUNCT; splitting it off is worth +0.1064 "
                                      "CI[+0.0213,+0.1915] on this row (pri 137 probe A2) -- an INSTRUMENT "
                                      "repair, not a reader repair."})}
    return {"rows": rows_out, "n_passages": len(MOD.PASSAGES),
            "elapsed_s": round(time.time() - t0, 1)}


# ===================================================================================================
# PART B -- UD-EWT through the live reader:  who_did_what_agent / who_did_what_patient / state
# ===================================================================================================
NOMINAL = ("NOUN", "PROPN", "PRON")


def _ud_sents(cap=None):
    """UD-EWT test sentences in the two schemas the board's own arms use (list-of-dict and tuple rows)."""
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud as load_ud_dicts
    ud_test = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
    sents = load_ud_dicts(ud_test)
    if cap:
        sents = sents[:cap]
    return sents


def _ud_write_chunk(chunk, path, docid, discover_pronouns=False):
    """A reader-native CoNLL pseudo-document from UD-EWT sentences; the coref column is `_` throughout --
    UD-EWT carries NO coref annotation, so this row is ANNOTATION-FREE by construction.
    `discover_pronouns=True` writes a SINGLETON mention span on every token the reader's OWN category organ
    tags PRON (no gold read) -- the prototype of the missing pronoun-introduction rung."""
    prn = set()
    if discover_pronouns:
        prn = set(_organ_pron_positions([[t["form"] for t in s] for s in chunk]))
    lines = ["#begin document (%s); part 0" % docid]
    k = 900000
    for si, s in enumerate(chunk):
        for w, t in enumerate(s):
            coref = "_"
            if (si, w) in prn:
                coref = "(%d)" % k
                k += 1
            lines.append("\t".join([docid, "0", str(w), t["form"]] + ["_"] * 7 + [coref]))
        lines.append("")
    lines.append("#end document")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _gold_agent_items(s):
    """(verb_id, gold_agent_id, passive) off GOLD deprels -- the board arm's own recipe, verbatim."""
    out = []
    for t in s:
        if t["upos"] != "VERB":
            continue
        v = t["id"]
        deps = [d for d in s if d["head"] == v]
        passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
        ag = None
        if passive:
            for d in deps:
                if d["deprel"].startswith("obl:agent"):
                    ag = d["id"]; break
        else:
            for d in deps:
                if d["dep"] == "nsubj" and not d["deprel"].startswith("nsubj:pass"):
                    ag = d["id"]; break
        if ag is not None:
            out.append((v, ag, passive))
    return out


def _gold_patient_items(s):
    """(verb_id, gold_patient_id, passive) off GOLD deprels -- obj (active) / nsubj:pass (passive)."""
    out = []
    for t in s:
        if t["upos"] != "VERB":
            continue
        v = t["id"]
        deps = [d for d in s if d["head"] == v]
        passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
        pat = None
        for d in deps:
            if not passive and d["dep"] == "obj":
                pat = d["id"]; break
            if passive and d["deprel"].startswith("nsubj:pass"):
                pat = d["id"]; break
        if pat is not None:
            out.append((v, pat, passive))
    return out


def _norm(x):
    return (str(x) or "").strip().lower()


def _subtree_forms(s, root_id):
    """Every token form in the gold dependency subtree of `root_id` (1-based). Used ONLY by the instrument's
    own SPAN-CREDIT slice: a reader that answers "the house" where the gold head is `house` has named the same
    argument, and a bare head-string match would score it wrong.  This bounds THE INSTRUMENT'S error -- it is
    reported as a slice, never as the model_acc."""
    kids = defaultdict(list)
    for t in s:
        kids[t["head"]].append(t["id"])
    out, stack = set(), [root_id]
    while stack:
        i = stack.pop()
        tk = next((t for t in s if t["id"] == i), None)
        if tk is not None:
            out.add(_norm(tk["form"]))
        stack.extend(kids.get(i, []))
    return out


def score_ud_chunk(chunk, sm, reader, rng, base_sid):
    """Score agent / patient / state for one UD pseudo-document off the SituationModel the reader returned."""
    import experiments.exp_copular_is_a_binding_readout_v1 as COP
    out = {"who_did_what_agent": defaultdict(lambda: [0, 0]),
           "who_did_what_patient": defaultdict(lambda: [0, 0]),
           "state": defaultdict(lambda: [0, 0])}
    diag = defaultdict(int)
    ev_by = defaultdict(list)
    for e in sm.events:
        ev_by[(e.sent_idx, e.pred_idx)].append(e)
    for si, s in enumerate(chunk):
        toks = [t["form"] for t in s]
        cid = "%s:%d" % (base_sid, si)
        try:
            up = list(reader._cached_tag(list(toks)))
        except Exception:
            up = ["X"] * len(toks)
        noms = [i for i in range(len(toks)) if i < len(up) and up[i] in NOMINAL]

        # ---- who-did-what AGENT ----
        for (v, ag, passive) in _gold_agent_items(s):
            gold = _norm(toks[ag - 1])
            evs = ev_by.get((si, v - 1), [])
            diag["agent_items"] += 1
            diag["agent_answered"] += int(bool(evs))
            model = _norm(evs[0].agent) if evs else ""
            hit = int(bool(model) and model not in ("?",) and model == gold)
            # THE SLICE THAT LOCATES THE LOSS: is the gold agent a PRONOUN?  On annotation-free text the
            # reader has NO pronoun mentions, so a pronoun agent is unreachable by construction.
            kind = "pron" if (ag - 1 < len(up) and up[ag - 1] == "PRON") else "nonpron"
            diag["agent_gold_" + kind] += 1
            diag["agent_hit_" + kind] += hit
            diag["agent_unbound_" + kind] += int(bool(evs) and model in ("?", ""))
            diag["agent_span_credit"] += int(bool(model) and model not in ("?",)
                                             and model in _subtree_forms(s, ag))
            out["who_did_what_agent"]["model"][0] += hit
            out["who_did_what_agent"]["model"][1] += 1
            pre = [i for i in noms if i < v - 1]                       # FLOOR nearest PRE-verbal nominal
            out["who_did_what_agent"]["positional_nearest_preverbal"][0] += int(
                bool(pre) and _norm(toks[pre[-1]]) == gold)
            out["who_did_what_agent"]["positional_nearest_preverbal"][1] += 1
            tw = rng.choice(noms) if noms else None                    # TWIN info-free
            out["who_did_what_agent"]["twin"][0] += int(tw is not None and _norm(toks[tw]) == gold)
            out["who_did_what_agent"]["twin"][1] += 1

        # ---- who-did-what PATIENT ----
        for (v, pat, passive) in _gold_patient_items(s):
            gold = _norm(toks[pat - 1])
            evs = ev_by.get((si, v - 1), [])
            diag["patient_items"] += 1
            diag["patient_answered"] += int(bool(evs))
            model = _norm(evs[0].patient) if evs else ""
            hit = int(bool(model) and model not in ("?",) and model == gold)
            kind = "pron" if (pat - 1 < len(up) and up[pat - 1] == "PRON") else "nonpron"
            diag["patient_gold_" + kind] += 1
            diag["patient_hit_" + kind] += hit
            diag["patient_span_credit"] += int(bool(model) and model not in ("?",)
                                               and model in _subtree_forms(s, pat))
            out["who_did_what_patient"]["model"][0] += hit
            out["who_did_what_patient"]["model"][1] += 1
            post = [i for i in noms if i > v - 1]                      # FLOOR nearest POST-verbal nominal
            out["who_did_what_patient"]["positional_nearest_postverbal"][0] += int(
                bool(post) and _norm(toks[post[0]]) == gold)
            out["who_did_what_patient"]["positional_nearest_postverbal"][1] += 1
            tw = rng.choice(noms) if noms else None
            out["who_did_what_patient"]["twin"][0] += int(tw is not None and _norm(toks[tw]) == gold)
            out["who_did_what_patient"]["twin"][1] += 1

        # ---- state (copular predicational binding) ----
        tup = [(t["id"], t["form"], t["form"], t["upos"], "", t["head"], t["deprel"]) for t in s]
        gold_states = [(h, p, ty) for (h, p, ty) in COP.typed_gold(tup) if ty in ("pred_adj", "pred_nom")]
        if gold_states:
            model_props = defaultdict(set)
            for st in sm.entity_states:
                if st.sent_idx == si:
                    model_props[_norm(st.holder)].add(_norm(st.property))
            try:
                fl_pairs = COP.positional_floor(toks, up)
            except Exception:
                fl_pairs = set()
            floor_props = defaultdict(set)
            for (hh, pp) in fl_pairs:
                if 0 <= hh < len(toks) and 0 <= pp < len(toks):
                    floor_props[_norm(toks[hh])].add(_norm(toks[pp]))
            holders = [h for (h, p, ty) in gold_states]
            shuf = list(holders)
            rng.shuffle(shuf)
            for k, (h, p, ty) in enumerate(gold_states):
                gold = _norm(toks[p])
                diag["state_items"] += 1
                diag["state_answered"] += int(bool(model_props.get(_norm(toks[h]))))
                out["state"]["model"][0] += int(gold in model_props.get(_norm(toks[h]), set()))
                out["state"]["model"][1] += 1
                out["state"]["most_recent_noun"][0] += int(gold in floor_props.get(_norm(toks[h]), set()))
                out["state"]["most_recent_noun"][1] += 1
                out["state"]["twin"][0] += int(gold in model_props.get(_norm(toks[shuf[k]]), set()))
                out["state"]["twin"][1] += 1
        for rname in out:
            pass
    # re-key every arm by the chunk's own cluster id (sentence-level clusters would over-split the bootstrap;
    # the chunk is the read unit, so it is the resampling unit)
    return {k: {a: tuple(v) for a, v in d.items()} for k, d in out.items()}, dict(diag)


UD_MODES = ("reader_textonly", "reader_textonly_pron_discovered")


def run_ud(cap=None, chunk=UD_CHUNK, n_boot=2000, seed=SEED, modes=UD_MODES):
    """Read UD-EWT test through the LIVE reader in pseudo-documents; score agent / patient / state off sm.
    TWO arms: the honest annotation-free read, and the PROTOTYPE read in which the reader's own category
    organ opens a referent for every token it tags PRON (the missing rung, located)."""
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    t0 = time.time()
    gaz = load_given_gazetteer()
    sents = _ud_sents(cap)
    chunks = [sents[i:i + chunk] for i in range(0, len(sents), chunk)]
    per = {m: {r: defaultdict(dict) for r in ("who_did_what_agent", "who_did_what_patient", "state")}
           for m in modes}
    diag = {m: defaultdict(int) for m in modes}
    tmp = tempfile.mkdtemp(prefix="brotrud_")
    try:
        for ci, ch in enumerate(chunks):
            for mode in modes:
                docid = "udewt%04d" % ci
                path = os.path.join(tmp, docid + "." + mode + ".conll")
                _ud_write_chunk(ch, path, docid,
                                discover_pronouns=(mode == "reader_textonly_pron_discovered"))
                rdr = SituationReader(gaz=gaz, **READER_KW)
                sm = rdr.read(path)
                rng = random.Random(seed + ci)
                sc, dg = score_ud_chunk(ch, sm, rdr, rng, docid)
                for k, v in dg.items():
                    diag[mode][k] += v
                for rname, arms in sc.items():
                    for a, ht in arms.items():
                        per[mode][rname][a][docid] = ht
                del sm, rdr
                os.remove(path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    POP = {
        "who_did_what_agent":
            "UD-EWT test who-did-what AGENT (gold nsubj [active] / obl:agent [passive] off GOLD deprels -- "
            "the board arm's own recipe). model = the LIVE reader's sm.events[].agent at the gold verb (a gold "
            "verb at which the reader fired NO event scores as a miss); floor = nearest pre-verbal nominal on "
            "the reader's OWN categories; twin = a random sentence nominal. Chunk-paired bootstrap.",
        "who_did_what_patient":
            "UD-EWT test who-did-what PATIENT (gold obj [active] / nsubj:pass [passive]). model = the LIVE "
            "reader's sm.events[].patient at the gold verb; floor = nearest post-verbal nominal on the "
            "reader's OWN categories; twin = a random sentence nominal. Chunk-paired bootstrap.",
        "state":
            "UD-EWT copular PREDICATIONAL gold (pred_adj + pred_nom off GOLD deprels). model = the LIVE "
            "reader's sm.entity_states property for the gold holder token; floor = the most-recent-noun "
            "positional binding on the reader's OWN categories; twin = the holders shuffled within the "
            "sentence. Chunk-paired bootstrap.",
    }
    FLOOR = {"who_did_what_agent": ["positional_nearest_preverbal"],
             "who_did_what_patient": ["positional_nearest_postverbal"],
             "state": ["most_recent_noun"]}
    rows = {}
    for mode in modes:
        prov = provenance(mode, "UD-EWT", "sm.events / sm.entity_states")
        rows[mode] = {}
        for rname in POP:
            key = {"who_did_what_agent": "agent", "who_did_what_patient": "patient", "state": "state"}[rname]
            d = diag[mode]
            extra = {"answered_rate": _r4(d.get(key + "_answered", 0) / max(1, d.get(key + "_items", 1))),
                     "ud_sentence_cap": cap, "n_sentences": len(sents), "n_pseudo_documents": len(chunks),
                     "chunk_sentences": chunk}
            if key in ("agent", "patient"):
                extra["instrument_span_credit"] = {
                    "acc_if_any_token_of_the_gold_ARGUMENT_counts":
                        _r4(d.get(key + "_span_credit", 0) / max(1, d.get(key + "_items", 1))),
                    "note": "an UPPER BOUND on what a bare head-string match costs the instrument; the row's "
                            "model_acc is the strict head match."}
                extra["by_gold_head_category"] = {
                    "pronoun": {"n": d.get("%s_gold_pron" % key, 0),
                                "acc": _r4(d.get("%s_hit_pron" % key, 0) / max(1, d.get("%s_gold_pron" % key, 1)))},
                    "not_pronoun": {"n": d.get("%s_gold_nonpron" % key, 0),
                                    "acc": _r4(d.get("%s_hit_nonpron" % key, 0)
                                               / max(1, d.get("%s_gold_nonpron" % key, 1)))}}
            rows[mode][rname] = _row(rname, per[mode][rname], "model", FLOOR[rname], "twin",
                                     POP[rname], prov, n_boot, seed, extra=extra)
    # the PROTOTYPE contrast, paired on the identical items (chunk-paired bootstrap)
    contrast = {}
    if len(modes) > 1 and "reader_textonly" in modes and "reader_textonly_pron_discovered" in modes:
        for rname in POP:
            d, lo, hi, hw, sep = _paired(per["reader_textonly"][rname]["model"],
                                         per["reader_textonly_pron_discovered"][rname]["model"], n_boot, seed)
            contrast[rname] = {"delta": _r4(d), "ci": [_r4(lo), _r4(hi)], "ci_half_width": _r4(hw),
                               "ci_sep": bool(sep)}
    return {"rows": rows, "diag": {m: dict(v) for m, v in diag.items()}, "n_sents": len(sents),
            "n_chunks": len(chunks), "chunk_sentences": chunk, "per": per,
            "pron_discovery_contrast": contrast, "elapsed_s": round(time.time() - t0, 1)}


# ===================================================================================================
# PHASE 7 (a) -- WHY A BARE-CANDIDATE PRONOUN INJECTION REGRESSES THE NON-PRONOUN AGENT SLICE.
#   `situation_reader._cm_agent_candidates` builds the Competition-Model AGENT candidate set from
#   `self._coref_mentions` -- the stream parsed out of the input file MENTION column.  The prototype arm
#   writes ONLY pronoun singletons into that column, so the candidate set the competition sees contains ONLY
#   PRONOUNS and every non-pronoun nominal is missing from it.  This counts that composition per arm, which is
#   the decisive number: it is a CANDIDATE-SET composition fact, not a cue-weighting fact.
# ===================================================================================================
def candidate_composition(cap=200, chunk=UD_CHUNK, modes=UD_MODES):
    """Per provenance arm: how many mentions the AGENT competition candidate source holds, and how many of
    them are pronouns.  Counted on the reader own `_coref_mentions` after a real read."""
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    sents = _ud_sents(cap)
    chunks = [sents[i:i + chunk] for i in range(0, len(sents), chunk)]
    out = {}
    tmp = tempfile.mkdtemp(prefix="brotrcc_")
    try:
        for mode in modes:
            tot = {"mentions": 0, "pronoun": 0, "non_pronoun": 0, "sentences": 0,
                   "sentences_with_no_nonpronoun_candidate": 0}
            for ci, ch in enumerate(chunks):
                docid = "cc%04d" % ci
                path = os.path.join(tmp, docid + "." + mode + ".conll")
                _ud_write_chunk(ch, path, docid,
                                discover_pronouns=(mode == "reader_textonly_pron_discovered"))
                rdr = SituationReader(gaz=gaz, **READER_KW)
                rdr.read(path)
                ms = list(getattr(rdr, "_coref_mentions", []) or [])
                tot["mentions"] += len(ms)
                tot["pronoun"] += sum(1 for m in ms if m.get("is_pronoun"))
                tot["non_pronoun"] += sum(1 for m in ms if not m.get("is_pronoun"))
                by_sent = defaultdict(list)
                for m in ms:
                    by_sent[m["sent_idx"]].append(m)
                tot["sentences"] += len(ch)
                for si in range(len(ch)):
                    if not any(not m.get("is_pronoun") for m in by_sent.get(si, [])):
                        tot["sentences_with_no_nonpronoun_candidate"] += 1
                del rdr
                os.remove(path)
            out[mode] = tot
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out["note"] = ("`_cm_agent_candidates` reads THIS stream. An arm whose non_pronoun count is 0 cannot hand "
                   "the Competition Model a non-pronoun agent at any weight -- which is why a bare singleton "
                   "injection into the mention column regresses the non-pronoun slice, and why ONE stream "
                   "(content heads AND discovered pronouns together) does not.")
    return out


# ===================================================================================================
# PHASE 7 (b) -- WHERE THE PATIENT ROW 0.13 GOES, RUNG BY RUNG, ON THE SAME ITEMS.
#   R = the reader sm.events[].patient (through read())
#   O = the SAME organ (predicate_argument_frontend.structural_patient_pick) called directly on the READER
#       OWN tags + the READER OWN parse heads -- isolates the read event/candidate layer
#   B = the SAME organ on the FRONTEND tagger + FRONTEND parser -- the rebuilt board arm own route
# ===================================================================================================
def patient_attribution(cap=600, chunk=UD_CHUNK, n_boot=2000, seed=SEED):
    from hdlab.situation_reader import SituationReader
    from hdlab.predicate_argument_frontend import structural_patient_pick
    from hdlab import frontend as FE
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    t0 = time.time()
    gaz = load_given_gazetteer()
    tg, pr = FE.tagger(), FE.parser()
    sents = _ud_sents(cap)
    chunks = [sents[i:i + chunk] for i in range(0, len(sents), chunk)]
    arms = {a: defaultdict(lambda: [0, 0]) for a in ("R_reader_read", "O_organ_on_reader_parse",
                                                     "B_organ_on_frontend_parse")}
    cross = Counter()
    tmp = tempfile.mkdtemp(prefix="brotrpa_")
    try:
        for ci, ch in enumerate(chunks):
            docid = "pa%04d" % ci
            path = os.path.join(tmp, docid + ".conll")
            _ud_write_chunk(ch, path, docid)
            rdr = SituationReader(gaz=gaz)
            sm = rdr.read(path)
            ev = defaultdict(list)
            for e in sm.events:
                ev[(e.sent_idx, e.pred_idx)].append(e)
            for si, sent in enumerate(ch):
                toks = [t["form"] for t in sent]
                items = _gold_patient_items(sent)
                if not items:
                    continue
                up_r = list(rdr._cached_tag(list(toks)))
                try:
                    hd_r = rdr._cached_parse_heads(list(toks), up_r)
                except Exception:
                    hd_r = {}
                up_b = list(tg.tag(list(toks)))
                try:
                    po = pr.parse(list(toks), up_b)
                    hd_b = dict(po.heads) if hasattr(po, "heads") else {}
                except Exception:
                    hd_b = {}
                for (v, pat, _passive) in items:
                    gold = _norm(toks[pat - 1])
                    evs = ev.get((si, v - 1), [])
                    r = _norm(evs[0].patient) if evs else ""
                    r_ok = int(bool(r) and r != "?" and r == gold)
                    try:
                        oi = structural_patient_pick(toks, up_r, hd_r, v, np_head_reduce=True)
                    except Exception:
                        oi = None
                    o_ok = int(oi is not None and _norm(toks[oi - 1]) == gold)
                    try:
                        bi = structural_patient_pick(toks, up_b, hd_b, v, np_head_reduce=True)
                    except Exception:
                        bi = None
                    b_ok = int(bi is not None and _norm(toks[bi - 1]) == gold)
                    for name, hit in (("R_reader_read", r_ok), ("O_organ_on_reader_parse", o_ok),
                                      ("B_organ_on_frontend_parse", b_ok)):
                        arms[name][docid][0] += hit
                        arms[name][docid][1] += 1
                    cross[("R" if r_ok else "r") + ("O" if o_ok else "o") + ("B" if b_ok else "b")] += 1
            del sm, rdr
            os.remove(path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    A = {k: {d: tuple(v) for d, v in dd.items()} for k, dd in arms.items()}
    accs = {k: _r4(_rate(v)[0]) for k, v in A.items()}
    n = _rate(A["R_reader_read"])[1]
    out = {"n": n, "acc": accs, "cross_tab": dict(cross), "elapsed_s": round(time.time() - t0, 1),
           "cap_sentences": cap}
    for a, b, label in (("R_reader_read", "O_organ_on_reader_parse", "read_layer"),
                        ("O_organ_on_reader_parse", "B_organ_on_frontend_parse", "tags_and_heads_layer"),
                        ("R_reader_read", "B_organ_on_frontend_parse", "total")):
        d, lo, hi, hw, sep = _paired(A[a], A[b], n_boot, seed)
        out.setdefault("contrasts", {})[label] = {"delta_b_minus_a": _r4(d), "ci": [_r4(lo), _r4(hi)],
                                                  "ci_half_width": _r4(hw), "ci_sep": bool(sep)}
    out["note"] = ("R = the reader own read; O = the SAME landed organ on the reader OWN tags+parse; "
                   "B = the same organ on the frontend tagger+parser (the rebuilt board arm route). "
                   "read_layer = what the read event/candidate layer costs; tags_and_heads_layer = what "
                   "the reader own categories and parse cost against the frontend ones.")
    return out


# ===================================================================================================
# PART C -- WiC through the live reader: the READ-BOUND sm.select_sense closure
# ===================================================================================================
def _wic_conll(tokens, path, docid):
    lines = ["#begin document (%s); part 0" % docid]
    for w, t in enumerate(tokens):
        lines.append("\t".join([docid, "0", str(w), t] + ["_"] * 7 + ["_"]))
    lines.append("")
    lines.append("#end document")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_wic(cap=120, n_boot=2000, seed=SEED):
    """Score the board's WiC row THROUGH THE READ: each side's sentence is read by SituationReader.read and the
    sense is committed by the closure the read BINDS (`sm.select_sense`), not by calling the organ directly.

    The difference from the rebuilt arm is exactly the two things the read supplies: the closure passes
    `lemma=` and lets the organ enumerate its own candidates (the rebuilt arm hands in a pre-built
    `candidate_synsets` list), and its default context is THE PASSAGE the reader just read (the rebuilt arm
    hands in a hand-filtered content-word set with the target removed)."""
    from hdlab.situation_reader import SituationReader
    import experiments.exp_sense_wire_wic_liveness_v1 as W
    import experiments.exp_curated_foundation_wic_v1 as E
    from tools.load_wsd_benchmarks import load_wic
    t0 = time.time()
    pairs = W._prep(load_wic("dev")) + W._prep(load_wic("test"))
    # WiC ships pos as "N"/"V"; WordNet wants "n"/"v". The rebuilt arm maps it through E._WNPOS before it
    # enumerates candidates, so the read-bound closure must be handed the same thing -- with the raw tag the
    # organ enumerates ZERO candidates and abstains on 100% of pairs (measured: coverage 0.000 on 24 pairs,
    # a COVERAGE artifact of the instrument, not a fact about the reader).
    for p in pairs:
        p["pos"] = E._WNPOS.get(p["pos"], p["pos"]) or "n"
    if cap:
        pairs = pairs[:cap]
    tmp = tempfile.mkdtemp(prefix="brotrwic_")
    per = {a: defaultdict(lambda: [0, 0]) for a in ("model", "majority", "twin", "rebuilt_style_same_items")}
    rng = random.Random(seed)
    perm = list(range(len(pairs)))
    rng.shuffle(perm)
    n_abstain = 0
    scored = []
    try:
        commits = []
        for i, p in enumerate(pairs):
            sels = []
            for side, sent in (("a", p["s1"]), ("b", p["s2"])):
                fp = os.path.join(tmp, "w%05d%s.conll" % (i, side))
                _wic_conll(str(sent).split(), fp, "wic%05d%s" % (i, side))
                rdr = SituationReader(gaz={})
                sm = rdr.read(fp)
                sel = None
                twin_sel = None
                if getattr(sm, "select_sense", None) is not None:
                    try:
                        sel = sm.select_sense(p["lemma"], pos=p["pos"])
                    except Exception:
                        sel = None
                    try:                     # INFO-FREE TWIN: the same read-bound closure, a FOREIGN context
                        other = pairs[perm[i]]
                        ctx = [w for w in (str(other["s1"] if side == "a" else other["s2"]).lower().split())]
                        twin_sel = sm.select_sense(p["lemma"], context_words=ctx, pos=p["pos"])
                    except Exception:
                        twin_sel = None
                sels.append((sel, twin_sel))
                del sm, rdr
                os.remove(fp)
            # THE READ-TIME CONTRACT, ISOLATED: the rebuilt arm's EXACT call on the SAME pair -- a pre-built
            # candidate_synsets list and a hand-filtered content-word context with the target removed -- using
            # the same vec space. Any gap between this and `model` is what the read's own contract costs.
            rb = None
            try:
                from nltk.corpus import wordnet as wn
                import hdlab.underspecified_sense_reader as USR
                from experiments.exp_sense_wall_breakthrough_wic_v1 import _content
                tn = [x.name() for x in wn.synsets(p["lemma"], pos=p["pos"])]
                if tn:
                    vl = USR.default_vec_lookup()
                    c1 = [w for w in (_content(p["s1"]) - {p["lemma"]})]
                    c2 = [w for w in (_content(p["s2"]) - {p["lemma"]})]
                    r1 = USR.select_sense(c1, vl, candidate_synsets=tn, pos=p["pos"], mode="underspecified")
                    r2 = USR.select_sense(c2, vl, candidate_synsets=tn, pos=p["pos"], mode="underspecified")
                    if r1 is not None and r2 is not None:
                        rb = int(r1.get("coarse") == r2.get("coarse"))
            except Exception:
                rb = None
            commits.append((p, sels, rb))
        maj_gold = [int(bool(p["gold"])) for (p, s, _rb) in commits
                    if s[0][0] is not None and s[1][0] is not None]
        maj_label = 1 if (sum(maj_gold) / max(1, len(maj_gold))) >= 0.5 else 0
        for i, (p, sels, rb) in enumerate(commits):
            (s1, t1), (s2, t2) = sels
            if s1 is None or s2 is None:
                n_abstain += 1
                continue                                   # the organ abstains -> outside the scored population
            gold = int(bool(p["gold"]))
            pred = int(s1.get("coarse") == s2.get("coarse"))
            tw = (int(t1.get("coarse") == t2.get("coarse")) if (t1 is not None and t2 is not None) else maj_label)
            cid = "wic%04d" % (len(scored) // 20)
            scored.append(i)
            per["model"][cid][0] += int(pred == gold); per["model"][cid][1] += 1
            per["majority"][cid][0] += int(maj_label == gold); per["majority"][cid][1] += 1
            per["twin"][cid][0] += int(tw == gold); per["twin"][cid][1] += 1
            per["rebuilt_style_same_items"][cid][0] += int((rb if rb is not None else maj_label) == gold)
            per["rebuilt_style_same_items"][cid][1] += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    arms = {a: {k: tuple(v) for k, v in d.items()} for a, d in per.items()}
    row = _row("wic", arms, "model", ["majority"], "twin",
               "WiC (modern) same-sense / different-sense pairs, scored on the population where the READ-BOUND "
               "closure commits on BOTH sides. model = sm.select_sense (the closure situation_reader._read_senses "
               "installs: lemma-driven candidates, the passage's own context); floor = the majority label on "
               "that population; twin = the same closure fed a FOREIGN pair's context. Cluster-paired bootstrap "
               "over blocks of 20 scored items.",
               provenance("reader_textonly", "WiC", "sm.select_sense"), n_boot, seed,
               extra={"n_abstain": n_abstain, "n_pairs_offered": len(pairs), "wic_pair_cap": cap,
                      "coverage": _r4(len(scored) / max(1, len(pairs))),
                      "read_time_contract_cost": {
                          "rebuilt_style_acc_on_the_same_items": _r4(_rate(arms["rebuilt_style_same_items"])[0]),
                          "note": "the rebuilt arm's exact call (a pre-built candidate_synsets list + a "
                                  "hand-filtered content-word context with the target removed) on the SAME "
                                  "items. `model_acc` is what the READ's own closure commits (lemma-driven "
                                  "candidates, the passage's own context INCLUDING the target)."}})
    return {"rows": {"wic": row}, "n_abstain": n_abstain, "n_pairs_offered": len(pairs),
            "elapsed_s": round(time.time() - t0, 1)}


# ===================================================================================================
# THE REBUILT SIDE -- the board's current seven rows, for the rebuilt-vs-reader table
# ===================================================================================================
def rebuilt_rows(gum_docs=None, ud_cap=None, n_boot=1000, seed=SEED):
    """The board's OWN row functions, called with the same caps, so the table compares like with like."""
    out, err = {}, {}
    try:
        import experiments.exp_board_coref_gum_v1 as CG
        cpr, det = CG.board_coref_modern_dimension(n_docs=gum_docs)
        out["coref"] = cpr
        out["common_noun_coref"] = det["common_noun"]
        sal, _ = CG.board_salience_modern_dimension(n_docs=gum_docs, n_boot=n_boot, seed=seed)
        out["salience"] = sal
    except Exception as e:
        err["gum"] = "%s: %s" % (type(e).__name__, e)
    try:
        import experiments.exp_board_agent_slot_ud_v1 as AG
        out["who_did_what_agent"], _ = AG.board_agent_dimension(cap=ud_cap, n_boot=n_boot, seed=seed)
    except Exception as e:
        err["agent"] = "%s: %s" % (type(e).__name__, e)
    try:
        from experiments.exp_board_patient_slot_v1 import board_patient_dimension
        out["who_did_what_patient"], _ = board_patient_dimension(cap=ud_cap)
    except Exception as e:
        err["patient"] = "%s: %s" % (type(e).__name__, e)
    try:
        from experiments.exp_situation_model_state_qa_v1 import board_state_dimension
        out["state"], _ = board_state_dimension(cap=ud_cap, n_boot=n_boot, seed=seed)
    except Exception as e:
        err["state"] = "%s: %s" % (type(e).__name__, e)
    try:
        from experiments.exp_sense_wire_wic_liveness_v1 import board_wic_via_live_wire_dimension
        out["wic"], _ = board_wic_via_live_wire_dimension(mode="smoke")
    except Exception as e:
        err["wic"] = "%s: %s" % (type(e).__name__, e)
    for k, v in out.items():
        if isinstance(v, dict):
            v["provenance"] = provenance("rebuilt", v.get("population", "")[:24], "the row's own rebuilt read")
    return out, err


ROWS7 = ("coref", "salience", "common_noun_coref", "entity_set", "who_did_what_agent",
         "who_did_what_patient", "state", "wic")


# ===================================================================================================
# THE THREE MOST RECENT LANDINGS, A/B'd ON THE READER-DRIVEN ROWS (brief checklist item 6).
# pri 113 / 116 / 117 all landed with large gains on the reader's own instruments and BYTE-IDENTICAL boards.
# The question this answers is the owner's: "why did the needle not move?" -- and whether it moves now.
# ===================================================================================================
class _ForceLowercaseSentenceSource:
    """pri 116 OFF: put the reader's sentence source back to LOWERCASING every token (the pre-2026-09-15
    shipped behaviour), at every module that imported the function by value. No hdlab file is edited."""

    _MODS = ("hdlab.scene_segment", "hdlab.situation_reader", "hdlab.referent_per_np")

    def __enter__(self):
        import importlib
        self._saved = {}
        import hdlab.scene_segment as SS
        orig = SS.parse_conll_sentences

        def low(path, lower=False):
            return orig(path, True)
        for name in self._MODS:
            m = importlib.import_module(name)
            if hasattr(m, "parse_conll_sentences"):
                self._saved[name] = m.parse_conll_sentences
                m.parse_conll_sentences = low
        self._orig = orig
        return self

    def __exit__(self, *a):
        import importlib
        for name, fn in self._saved.items():
            setattr(importlib.import_module(name), "parse_conll_sentences", fn)
        return False


class _PredicateSlotOff:
    """pri 117 OFF: the category organ stops reading the clause's predicate-slot expectation (the learned cue
    that attaches a copular subject). Module global, read at call time."""

    def __enter__(self):
        import hdlab.lexical_categories as LC
        self._m = LC
        self._saved = LC.PREDICATE_SLOT
        LC.PREDICATE_SLOT = False
        return self

    def __exit__(self, *a):
        self._m.PREDICATE_SLOT = self._saved
        return False


class _Nothing:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def landings(gum_docs=16, ud_cap=400, n_boot=2000, seed=SEED):
    """Run the reader-driven rows with each of the three landings turned OFF, on the SAME capped population,
    and report the paired contrast per row. An arm that moves a row is a landing the board can finally see."""
    global READER_KW
    t0 = time.time()
    specs = [
        ("default", _Nothing, {}),
        ("pri116_off_case_lowercased", _ForceLowercaseSentenceSource, {}),
        ("pri113_off_nonverbal_predication", _Nothing, {"nonverbal_predication": False}),
        ("pri117_off_predicate_slot", _PredicateSlotOff, {}),
    ]
    got = {}
    for name, ctx, kw in specs:
        READER_KW = dict(kw)
        try:
            with ctx():
                g = run_gum(n_docs=gum_docs, n_boot=n_boot, seed=seed,
                            modes=("reader_annotated", "reader_textonly"))
                u = run_ud(cap=ud_cap, n_boot=n_boot, seed=seed, modes=("reader_textonly",))
        finally:
            READER_KW = {}
        got[name] = {"gum": g, "ud": u}
    out = {"arms": {}, "contrasts": {}, "caps": {"gum_documents": gum_docs, "ud_sentences": ud_cap},
           "elapsed_s": None}
    for name, d in got.items():
        out["arms"][name] = {}
        for mode, rr in d["gum"]["rows"].items():
            for k, r in rr.items():
                out["arms"][name]["%s[%s]" % (k, mode.replace("reader_", ""))] = {
                    "n": r["n"], "model_acc": r["model_acc"], "floor": r["strongest_floor"]}
        for k, r in d["ud"]["rows"]["reader_textonly"].items():
            out["arms"][name]["%s[textonly]" % k] = {"n": r["n"], "model_acc": r["model_acc"],
                                                     "floor": r["strongest_floor"]}
    base = got["default"]
    for name, d in got.items():
        if name == "default":
            continue
        out["contrasts"][name] = {}
        for mode in ("reader_annotated", "reader_textonly"):
            for k in ("coref", "salience", "common_noun_coref"):
                a = d["gum"]["per"][mode][k].get("model", {})
                b = base["gum"]["per"][mode][k].get("model", {})
                dd, lo, hi, hw, sep = _paired(a, b, n_boot, seed)
                out["contrasts"][name]["%s[%s]" % (k, mode.replace("reader_", ""))] = {
                    "default_minus_off": _r4(dd), "ci": [_r4(lo), _r4(hi)], "ci_half_width": _r4(hw),
                    "ci_sep": bool(sep)}
        for k in ("who_did_what_agent", "who_did_what_patient", "state"):
            a = d["ud"]["per"]["reader_textonly"][k].get("model", {})
            b = base["ud"]["per"]["reader_textonly"][k].get("model", {})
            dd, lo, hi, hw, sep = _paired(a, b, n_boot, seed)
            out["contrasts"][name]["%s[textonly]" % k] = {
                "default_minus_off": _r4(dd), "ci": [_r4(lo), _r4(hi)], "ci_half_width": _r4(hw),
                "ci_sep": bool(sep)}
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["note"] = ("`default_minus_off` > 0 with ci_sep=True means the landing is VISIBLE on that "
                   "reader-driven row. The rebuilt rows were byte-identical under all three (pri 113 and "
                   "pri 116 each counted it).")
    return out


# ---------------------------------------------------------------------------------------------------
# THE COUNTED WITNESS -- how many times does a row actually run the reader?  (pri 116 counted this for the
# sentence source and got an EXACT 0 on all seven rows; this counts BOTH the sentence source and read()
# itself, in the same process, for the rebuilt rows and for the reader-driven rows.)
# ---------------------------------------------------------------------------------------------------
class ReaderCallCounter:
    """Counts SituationReader.read + scene_segment.parse_conll_sentences calls. Monkeypatches the MODULE
    attributes for the duration only (no hdlab file is edited); restores byte-identically on exit."""

    def __init__(self):
        self.reads = 0
        self.sentence_source = 0

    def __enter__(self):
        import hdlab.scene_segment as SS
        import hdlab.situation_reader as SR
        self._ss_orig = SS.parse_conll_sentences
        self._sr_orig = SR.SituationReader.read
        self._sr_ss_orig = getattr(SR, "parse_conll_sentences", None)
        cnt = self

        def ss(path, lower=False):
            cnt.sentence_source += 1
            return cnt._ss_orig(path, lower)

        def rd(self_, conll_path):
            cnt.reads += 1
            return cnt._sr_orig(self_, conll_path)
        SS.parse_conll_sentences = ss
        if self._sr_ss_orig is not None:
            SR.parse_conll_sentences = ss
        SR.SituationReader.read = rd
        return self

    def __exit__(self, *a):
        import hdlab.scene_segment as SS
        import hdlab.situation_reader as SR
        SS.parse_conll_sentences = self._ss_orig
        if self._sr_ss_orig is not None:
            SR.parse_conll_sentences = self._sr_ss_orig
        SR.SituationReader.read = self._sr_orig
        return False


# ---------------------------------------------------------------------------------------------------
# THE PROVENANCE TABLE FOR **EVERY** BOARD ARM (checklist item 3), by static call-graph reachability.
# ---------------------------------------------------------------------------------------------------
def classify_board_arms():
    """For every `board_*_dimension` in experiments/exp_situation_model_qa_modern_v1.py, walk the experiments.*
    import graph reachable from its body and report whether `SituationReader` (the live reader) and
    `parse_conll_sentences` (the reader's ONLY sentence source) are reachable at all.  Static, so it is a
    LOCATOR, not a proof -- the counted witness above is the proof; this is what makes the table complete."""
    import re
    board = os.path.join(_REPO, "experiments", "exp_situation_model_qa_modern_v1.py")
    src = open(board, encoding="utf-8").read()
    fns = {}
    cur, buf = None, []
    for ln in src.splitlines():
        m = re.match(r"^def (board_\w*dimension)\(", ln)
        if m:
            if cur:
                fns[cur] = "\n".join(buf)
            cur, buf = m.group(1), [ln]
        elif cur is not None:
            if re.match(r"^(def |# ={10,})", ln):
                fns[cur] = "\n".join(buf)
                cur, buf = None, []
            else:
                buf.append(ln)
    if cur:
        fns[cur] = "\n".join(buf)
    cache = {}

    def mod_src(mod):
        if mod in cache:
            return cache[mod]
        p = os.path.join(_REPO, mod.replace(".", os.sep) + ".py")
        cache[mod] = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        return cache[mod]

    def deps(text):
        out = set()
        for m in re.finditer(r"(?:import|from)\s+(experiments\.[A-Za-z0-9_]+|tools\.[A-Za-z0-9_]+)", text):
            out.add(m.group(1))
        return out

    def reach(text, depth=4):
        seen, frontier, hits = set(), deps(text), {"SituationReader": "SituationReader" in text,
                                                  "parse_conll_sentences": "parse_conll_sentences" in text}
        for _ in range(depth):
            nxt = set()
            for mod in frontier:
                if mod in seen:
                    continue
                seen.add(mod)
                s = mod_src(mod)
                if "SituationReader" in s:
                    hits["SituationReader"] = True
                if "parse_conll_sentences" in s:
                    hits["parse_conll_sentences"] = True
                nxt |= deps(s)
            frontier = nxt - seen
            if not frontier:
                break
        return hits, sorted(seen)
    table = {}
    for name, body in sorted(fns.items()):
        hits, mods = reach(body)
        reaches = bool(hits["SituationReader"] or hits["parse_conll_sentences"])
        table[name] = {
            "reaches_live_reader_statically": reaches,
            "SituationReader_reachable": hits["SituationReader"],
            "sentence_source_reachable": hits["parse_conll_sentences"],
            "n_experiments_modules_walked": len(mods),
            "token_stream": "reader" if reaches else "loader",
            "read_by": ("MAY reach SituationReader.read (static)" if reaches
                        else "rebuilt in the arm (SituationReader never referenced anywhere reachable)"),
            "plain": ("may run the reading system" if reaches else "a rebuilt read from the annotated file"),
        }
    # the run() body's seven headline rows, named explicitly (they are called from run(), not from a board_* fn)
    table["_headline_seven_rows"] = {
        "rows": list(ROWS7),
        "producers": ["exp_board_coref_gum_v1.board_coref_modern_dimension",
                      "exp_board_coref_gum_v1.board_salience_modern_dimension",
                      "exp_board_agent_slot_ud_v1.board_agent_dimension",
                      "exp_board_patient_slot_v1.board_patient_dimension",
                      "exp_situation_model_state_qa_v1.board_state_dimension",
                      "exp_sense_wire_wic_liveness_v1.board_wic_via_live_wire_dimension"],
        "note": "pri 116 COUNTED the sentence-source calls these six functions make during one board run: 0 on "
                "every row in both arms of its A/B. This cell re-counts them (ReaderCallCounter) and also "
                "counts read() itself.",
    }
    return table


def aggregate(rows):
    """The board's own item-weighted cross-population summary, computed the same way (informational)."""
    have = [r for r in rows.values() if r and r.get("model_acc") is not None and r.get("n")]
    tot = sum(r["n"] for r in have)
    if not tot:
        return {}

    def wm(key):
        hv = [r for r in have if r.get(key) is not None]
        n = sum(r["n"] for r in hv)
        return round(sum(r["n"] * r[key] for r in hv) / n, 4) if n else None
    return {"n": tot, "model_acc": wm("model_acc"), "strongest_floor": wm("strongest_floor"),
            "twin_acc": wm("twin_acc"),
            "n_dims_ci_sep_over_floor": sum(1 for r in have if r.get("ci_sep_over_strongest")),
            "n_dims_total": len(have),
            "note": "CROSS-POPULATION SUMMARY (item-weighted mean), informational only -- the per-row numbers "
                    "are the load-bearing claims."}


def comparison_table(reader_rows, rebuilt):
    tab = {}
    for k in ROWS7:
        rb = rebuilt.get(k) or {}
        tab[k] = {
            "rebuilt": {"n": rb.get("n"), "model_acc": rb.get("model_acc"),
                        "strongest_floor": rb.get("strongest_floor"),
                        "provenance": "a rebuilt read from the annotated file"},
        }
        for mode, rr in reader_rows.items():
            r = rr.get(k)
            if r:
                tab[k][mode] = {"n": r.get("n"), "model_acc": r.get("model_acc"),
                                "strongest_floor": r.get("strongest_floor"),
                                "ci_sep_over_strongest": r.get("ci_sep_over_strongest"),
                                "twin_acc": r.get("twin_acc"),
                                "provenance": r["provenance"]["plain"]}
    return tab


# ===================================================================================================
def run(gum_docs=None, ud_cap=None, wic_cap=None, n_boot=2000, seed=SEED, do_rebuilt=True,
        write_metrics=True):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    res = {"anchor": ANCHOR, "seed": seed,
           "caps": {"gum_documents": gum_docs, "ud_sentences": ud_cap, "wic_items": wic_cap,
                    "ud_chunk_sentences": UD_CHUNK}}
    with ReaderCallCounter() as cr:
        g = run_gum(n_docs=gum_docs, n_boot=n_boot, seed=seed)
        u = run_ud(cap=ud_cap, n_boot=n_boot, seed=seed)
        w = run_wic(cap=wic_cap, n_boot=n_boot, seed=seed)
    res["counted_reader_calls_reader_driven_rows"] = {
        "SituationReader_read_calls": cr.reads, "sentence_source_calls": cr.sentence_source,
        "note": "the reader-driven rows' own count, in the same shape as the rebuilt count -- one read() per "
                "document per provenance mode (GUM) + one per UD pseudo-document + two per WiC pair."}
    # THE THREE PROVENANCE COLUMNS. GUM supplies all three; UD-EWT and WiC carry NO coref annotation, so their
    # `reader_annotated` column is the annotation-free row itself (each row keeps its own provenance field,
    # which says exactly what it read -- nothing is silently promoted).
    reader_rows = {m: {} for m in GUM_MODES}
    for mode in reader_rows:
        reader_rows[mode].update(g["rows"].get(mode, {}))
        ud_mode = ("reader_textonly_pron_discovered" if mode == "reader_textonly_pron_discovered"
                   else "reader_textonly")
        reader_rows[mode].update(u["rows"].get(ud_mode, {}))
        reader_rows[mode].update(w["rows"])
    res["per_dimension_reader_driven"] = reader_rows
    res["aggregate_reader_driven"] = {m: aggregate(r) for m, r in reader_rows.items()}
    # THE WHERE-IS ROW (pri 137) is published on its OWN key and is deliberately NOT folded into the seven-row
    # aggregate: its gold is author-constructed rather than found, and adding a row to an aggregate silently
    # changes every historical comparison. Strategy decides whether it joins ROWS7.
    try:
        wi = run_where_is(n_boot=n_boot, seed=seed)
        res["per_dimension_where_is"] = wi["rows"]
        res["where_is_detail"] = {k: v for k, v in wi.items() if k != "rows"}
    except Exception as _e:                                   # a new row must never take the board down
        res["per_dimension_where_is"] = {"error": "%s: %s" % (type(_e).__name__, _e)}
    res["gum_detail"] = {"n_docs": g["n_docs"], "n_toks": g["n_toks"], "elapsed_s": g["elapsed_s"],
                         "per_doc": g["diag"]}
    res["ud_detail"] = {k: v for k, v in u.items() if k != "rows"}
    res["wic_detail"] = {k: v for k, v in w.items() if k != "rows"}
    res["board_arm_provenance_static"] = classify_board_arms()
    if do_rebuilt:
        with ReaderCallCounter() as c:
            rb, err = rebuilt_rows(gum_docs=gum_docs, ud_cap=ud_cap, n_boot=min(1000, n_boot), seed=seed)
        res["per_dimension_rebuilt"] = rb
        res["rebuilt_errors"] = err
        res["aggregate_rebuilt"] = aggregate(rb)
        res["rebuilt_vs_reader"] = comparison_table(reader_rows, rb)
        res["counted_reader_calls_rebuilt_seven_rows"] = {
            "SituationReader_read_calls": c.reads, "sentence_source_calls": c.sentence_source,
            "note": "counted in THIS process while the board's own six row functions produced the seven "
                    "headline rows. An EXACT count from the call graph, not an estimate."}
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["ts_iso"] = datetime.now(timezone.utc).isoformat()
    if write_metrics:
        with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
            json.dump(res, fh, indent=2, default=str)
    return res


def board_rows_on_the_reader_dimension(smoke=False):
    """The board-ready entry point: the SEVEN rows scored from the live reader's own read, in BOTH provenance
    modes.  Returns ({mode: {row: per_dimension_row}}, detail)."""
    r = run(gum_docs=(4 if smoke else None), ud_cap=(200 if smoke else None),
            wic_cap=(12 if smoke else None), n_boot=(200 if smoke else 2000),
            do_rebuilt=False, write_metrics=not smoke)
    return r["per_dimension_reader_driven"], {"aggregate": r["aggregate_reader_driven"],
                                              "caps": r["caps"], "elapsed_s": r["elapsed_s"]}


def self_test():
    """Structural, fast, and CAN-FAIL: the snapshot wrapper is byte-identical; the reader's coref targets align
    with sm.coref_resolutions; the text-only file differs from the annotated one ONLY in the coref column; the
    row schema carries every field the board reads; the twin is info-free."""
    ok = True

    def ck(label, cond, extra=""):
        nonlocal ok
        print(("  PASS " if cond else "  FAIL ") + label + ((" -- " + str(extra)) if extra else ""))
        ok = ok and bool(cond)

    from hdlab.situation_reader import SituationReader
    test, gaz = _gum_test_docs(2, prefix=True)
    tmp = tempfile.mkdtemp(prefix="brotrst_")
    try:
        d = test[0]
        p_ann, p_txt, p_prn = _write_two_conll(d, tmp)
        a = [l.rstrip("\n").split("\t") for l in open(p_ann, encoding="utf-8") if not l.startswith("#") and l.strip()]
        b = [l.rstrip("\n").split("\t") for l in open(p_txt, encoding="utf-8") if not l.startswith("#") and l.strip()]
        ck("text-only file differs from the annotated one ONLY in the coref column",
           len(a) == len(b) and all(x[:-1] == y[:-1] for x, y in zip(a, b)) and all(y[-1] == "_" for y in b),
           "%d rows" % len(a))
        ck("the annotated file DOES carry coref brackets", any(x[-1] != "_" for x in a))
        c = [l.rstrip("\n").split("\t") for l in open(p_prn, encoding="utf-8")
             if not l.startswith("#") and l.strip()]
        prn_rows = [x for x in c if x[-1] != "_"]
        ck("the pron-discovered file differs from text-only ONLY in the mention column, and every mention it "
           "carries is a SINGLETON the category organ opened",
           len(c) == len(b) and all(x[:-1] == y[:-1] for x, y in zip(c, b))
           and all(v[-1].startswith("(") and v[-1].endswith(")") for v in prn_rows) and len(prn_rows) > 0,
           "%d discovered pronoun mentions" % len(prn_rows))
        ck("the discovered mentions are NOT the gold spans (no gold column is read)",
           sorted(x[-1] for x in c if x[-1] != "_") != sorted(x[-1] for x in a if x[-1] != "_"))
        r1 = SituationReader(gaz=gaz)
        sm1 = r1.read(p_ann)
        r2 = SituationReader(gaz=gaz)
        _install_role_snapshot(r2)
        sm2 = r2.read(p_ann)
        ck("the role-mention snapshot wrapper leaves the read byte-identical",
           (len(sm1.entities) == len(sm2.entities) and len(sm1.events) == len(sm2.events)
            and len(sm1.coref_resolutions) == len(sm2.coref_resolutions)
            and [(e.predicate, e.agent, e.patient) for e in sm1.events]
            == [(e.predicate, e.agent, e.patient) for e in sm2.events]),
           "ents %d/%d events %d/%d" % (len(sm1.entities), len(sm2.entities), len(sm1.events), len(sm2.events)))
        ck("the snapshot is populated", len(getattr(r2, "_role_mentions_snapshot", [])) > 0,
           len(getattr(r2, "_role_mentions_snapshot", [])))
        # 2026-09-15 (pri 131 landing): the row no longer aligns a gold target list to the reader's resolutions by
        # index; each resolution carries its own target position and antecedent span (pri 131's contract) and is
        # scored against the gold entity at those positions -- the claim is that the records carry them.
        res2 = list(sm2.coref_resolutions)
        ck("every resolution carries a target position (pri 131 contract)",
           bool(res2) and all(getattr(r, "target_wpos", -1) >= 0 for r in res2), "%d records" % len(res2))
        ck("every resolution carries an antecedent span or abstains (None)",
           all(getattr(r, "antecedent_span", None) is None or len(r.antecedent_span) >= 2 for r in res2), len(res2))
        sc, dg = score_gum_doc(d, sm2, r2, random.Random(0))
        for rname in ("coref", "salience", "common_noun_coref"):
            arms = sc[rname]
            if arms:
                tots = {a: t for a, (h, t) in arms.items()}
                ck("%s: every arm scores the SAME number of items" % rname,
                   len(set(tots.values())) == 1, tots)
        row = _row("t", {"model": {"d": (8, 10)}, "f": {"d": (5, 10)}, "twin": {"d": (2, 10)}},
                   "model", ["f"], "twin", "unit", provenance("reader_annotated", "unit", "unit"), n_boot=200)
        need = ("n", "model_acc", "overlap_floor", "floor_accs", "strongest_floor_name", "strongest_floor",
                "twin_acc", "model_minus_strongest", "model_minus_twin", "ci_sep_over_strongest",
                "ci_sep_over_twin", "population", "provenance")
        ck("the row schema carries every field the board reads", all(k in row for k in need))
        ck("the unit row's arithmetic is right", row["model_acc"] == 0.8 and row["strongest_floor"] == 0.5)
        # UD path, 2 chunks, BOTH arms
        u = run_ud(cap=20, chunk=10, n_boot=200)
        ck("UD rows are produced with a non-empty population",
           all(u["rows"]["reader_textonly"][k]["n"] > 0
               for k in ("who_did_what_agent", "who_did_what_patient")),
           {k: v["n"] for k, v in u["rows"]["reader_textonly"].items()})
        ck("UD provenance says annotation-free",
           u["rows"]["reader_textonly"]["who_did_what_agent"]["provenance"]
           ["annotation_supplied"].startswith("no"))
        ck("the agent row publishes the pronoun / not-pronoun slice that locates the loss",
           "by_gold_head_category" in u["rows"]["reader_textonly"]["who_did_what_agent"],
           u["rows"]["reader_textonly"]["who_did_what_agent"].get("by_gold_head_category"))
        ck("both UD arms score the SAME items (the prototype contrast is paired)",
           u["rows"]["reader_textonly"]["who_did_what_agent"]["n"]
           == u["rows"]["reader_textonly_pron_discovered"]["who_did_what_agent"]["n"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(("SELF-TEST PASS" if ok else "SELF-TEST FAIL"))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--gum", action="store_true")
    ap.add_argument("--ud", action="store_true")
    ap.add_argument("--wic", action="store_true")
    ap.add_argument("--where-is", action="store_true", dest="where_is",
                    help="pri 137: the SPACE dimension's own row (sm.locations.where_is) through the live reader")
    ap.add_argument("--landings", action="store_true",
                    help="A/B the last three landings (pri 113/116/117) ON the reader-driven rows")
    ap.add_argument("--rebuilt", action="store_true",
                    help="the board's own seven rows + the COUNTED reader-call witness")
    ap.add_argument("--attrib", action="store_true",
                    help="phase 7: the AGENT candidate-set composition + the PATIENT rung attribution")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--ud-cap", type=int, default=None)
    ap.add_argument("--wic-cap", type=int, default=None)
    ap.add_argument("--no-rebuilt", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.ud_cap == 0:
        a.ud_cap = None                     # --ud-cap 0 = the WHOLE UD-EWT test split
    if a.docs == 0:
        a.docs = None                       # --docs 0 = the WHOLE GUM test split
    if a.self_test:
        sys.exit(0 if self_test() else 1)
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.gum:
        r = run_gum(n_docs=a.docs, n_boot=a.n_boot)
        print(json.dumps({"rows": r["rows"], "n_docs": r["n_docs"], "elapsed_s": r["elapsed_s"]},
                         indent=2, default=str))
        with open(os.path.join(OUT_DIR, "gum%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(r, fh, indent=2, default=str)
        return
    if a.ud:
        r = run_ud(cap=a.ud_cap, n_boot=a.n_boot)
        print(json.dumps(r, indent=2, default=str))
        with open(os.path.join(OUT_DIR, "ud%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(r, fh, indent=2, default=str)
        return
    if a.wic:
        r = run_wic(cap=a.wic_cap, n_boot=a.n_boot)
        print(json.dumps(r, indent=2, default=str))
        with open(os.path.join(OUT_DIR, "wic%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(r, fh, indent=2, default=str)
        return
    if a.where_is:
        r = run_where_is(n_boot=a.n_boot)
        print(json.dumps(r, indent=2, default=str))
        with open(os.path.join(OUT_DIR, "where_is%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(r, fh, indent=2, default=str)
        return
    if a.attrib:
        cc = candidate_composition(cap=(a.ud_cap or 200))
        pa = patient_attribution(cap=(a.ud_cap or 600), n_boot=a.n_boot)
        out = {"candidate_composition": cc, "patient_attribution": pa}
        print(json.dumps(out, indent=2, default=str))
        with open(os.path.join(OUT_DIR, "attrib%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(out, fh, indent=2, default=str)
        return
    if a.landings:
        r = landings(gum_docs=(a.docs or 16), ud_cap=(a.ud_cap or 400), n_boot=a.n_boot)
        print(json.dumps(r, indent=2, default=str))
        with open(os.path.join(OUT_DIR, "landings%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(r, fh, indent=2, default=str)
        return
    if a.rebuilt:
        with ReaderCallCounter() as c:
            rb, err = rebuilt_rows(gum_docs=a.docs, ud_cap=a.ud_cap, n_boot=a.n_boot)
        out = {"per_dimension_rebuilt": rb, "errors": err, "aggregate_rebuilt": aggregate(rb),
               "counted_reader_calls_rebuilt_seven_rows": {
                   "SituationReader_read_calls": c.reads, "sentence_source_calls": c.sentence_source,
                   "note": "counted in THIS process while the board's own six row functions produced the seven "
                           "headline rows -- an EXACT count from the call graph."},
               "board_arm_provenance_static": classify_board_arms()}
        print(json.dumps({k: v for k, v in out.items() if k != "board_arm_provenance_static"},
                         indent=2, default=str))
        with open(os.path.join(OUT_DIR, "rebuilt%s.json" % a.tag), "w", encoding="ascii") as fh:
            json.dump(out, fh, indent=2, default=str)
        return
    if a.run:
        r = run(gum_docs=a.docs, ud_cap=a.ud_cap, wic_cap=a.wic_cap, n_boot=a.n_boot,
                do_rebuilt=not a.no_rebuilt)
        print(json.dumps({"caps": r["caps"], "aggregate_reader_driven": r["aggregate_reader_driven"],
                          "rebuilt_vs_reader": r.get("rebuilt_vs_reader"),
                          "elapsed_s": r["elapsed_s"]}, indent=2, default=str))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
