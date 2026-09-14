"""exp_entity_instruments_gold_free_v1 -- MAKE THE TWO ENTITY INSTRUMENTS GOLD-FREE (pri-109).

THE PROBLEM (the brief). The two board rows that measure the entity layer are not measuring the live system:
  (1) `experiments/gum_coref._mention_type` branches on `head_tok.upos`, and that upos is `cols[3]` of the GUM
      CoNLL-U -- THE GOLD CATEGORY COLUMN. So the board's `coref`, `common_noun_coref` and `salience` rows are
      scored with a name/common/pronoun split the live reader never has (it has a capitalisation rule).
  (2) the reader's own entity question instrument (`exp_situation_model_qa_v1.build_coref_questions`) has been
      building ZERO questions since 2026-09-09, so `test_coref_which_entity...` scores 0.0 on the model AND
      both floors.

WHAT AN INSTRUMENT MAY READ (the opening move, for an instrument). The brain question "how does the reader decide
that this span is a name?" is answered by the CATEGORY ORGAN: a proper name is a word that picks out an INDIVIDUAL
(Kripke 1980) and the referent route that stores it (left temporal pole; Semenza 2006/2009 proper-name anomia;
Damasio et al. 1996) sits ABOVE and is FED BY the posterior-temporal word-form/category level. So the instrument
may read what the live system knows at decision time -- the category organ through `hdlab.frontend.tagger()` --
and NOTHING from the answer key. Gold is the answer key (the coref chains in MISC, which is what is being
scored), never an input to a decision.

THE FIVE GOLD READS AT DECISION TIME, ENUMERATED ON DISK (checklist item 3; `--witness` prints them live):
    cols[3] upos   -> `_mention_type` (name/common/pronoun) and `_head_of_span`'s non-PUNCT/DET/ADP preference
    cols[2] lemma  -> `Mention.lemma_head`, the surface identity key of EVERY common-noun coref decision
    cols[5] feats  -> `_gender_number` (Gender/Number agreement in the pronoun pick)
    cols[6] head   -> `_head_of_span` (which token of the span is the head)
    cols[7] deprel -> `URG._role` (SUBJECT/OBJECT/POSSESSIVE -> ACT-R role prominence) and
                      `_appos_copula_isa` (the in-text is-a edges the common-noun type bridge rides on)

THE GOLD-FREE REPLACEMENTS, ORGAN BY ORGAN (every one already live in the substrate):
    upos    -> `hdlab.frontend.tagger()` = `hdlab.lexical_categories` (count-based generative category model)
    head    -> the head-final nominal rule over the PREDICTED categories (the last NOUN/PROPN of the run) --
               the rule `hdlab/attachment_arm` uses inside an NP and the one pri 104's shipped
               `coref._span_head_is_name` uses. No parse needed: English nominals are head-final.
    lemma   -> `hdlab.morphology` (the dual-route glass-box morphy port, BF, no nltk at inference)
    gender  -> the closed-class pronoun table (gold-free by construction) + the given-name gazetteer
               (an offline FOUNDATION asset, admissible supply)
    number  -> the morphology organ's decomposition (a stripped plural suffix IS the number cue)
    deprel  -> the POSITIONAL role rule over predicted categories (preverbal -> SUBJECT, postverbal -> OBJECT,
               's / possessive pronoun -> POSSESSIVE): the proxy the live reader's own `_assign_roles` uses and
               the one `URG.Resolver(positional_roles=True)` already exposes as an ablation.
    appos/cop -> `goldfree_isa`: the two CONSTRUCTIONS ("X , the Y ," and "X is a Y") detected from predicted
               categories + surface commas, instead of the gold `appos` / `cop` arcs.

ARMS (all on the SAME GUM documents; `--arms a,b,c`):
    gold        the board exactly as it stands today (every gold column)     [reproduces 0.4681 / 0.5671]
    caps        name/common from `coref.name_content_tokens` (capitalisation) -- what the LIVE reader does
    cat         name/common from the live category organ; every OTHER column still gold [isolates the rung]
    gf          FULL gold-free: categories + head + lemma + gender/number + positional roles
    gf_isa      gf + the gold-free construction is-a detector (the quality push)
    gf_wire     gf_isa + pri 104's SHIPPED forward wire (`name_content_tokens(span, upos=...)`) as the typer
    gf_twin     THE WITNESS: cols 2/3/4/5/6/7 SCRAMBLED inside each document, then the gf layer applied.
                Must be BYTE-IDENTICAL to `gf` -- that is the proof no gold column is read at decision time.

Glass-box; no external LLM, no spaCy, no nltk at inference. ASCII. Own output dir.
Run: .venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --witness
     .venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --board --arms gold,caps,cat,gf
     .venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --qa --docs 8
"""
from __future__ import annotations
import os, sys, json, time, random, argparse, re
from collections import Counter, defaultdict
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

ANCHOR = "entity_instruments_gold_free_v1"
SEED = 20260914


def get_output_dir():
    d = os.path.join(_REPO, "data", "exp_entity_instruments_gold_free_v1")
    os.makedirs(d, exist_ok=True)
    return d


# ===================================================================================================
# 0. THE WITNESS: every gold column read at decision time, located on disk (checklist item 3)
# ===================================================================================================
_WITNESS_FILES = ["experiments/gum_coref.py", "experiments/exp_board_coref_gum_v1.py",
                  "experiments/exp_unified_referent_gum_v1.py",
                  "experiments/exp_commonnoun_diffhead_anatomy_gum_v1.py"]
_WITNESS_PAT = re.compile(r"\.(upos|xpos|lemma|deprel|feats)\b|cols\[(2|3|4|5|6|7)\]|lemma_head|\bt\.head\b")


def witness_gold_reads(verbose=True):
    """GREP-LEVEL WITNESS (bar 8a): the decision-time gold-column reads in the board's coref chain."""
    hits = []
    for rel in _WITNESS_FILES:
        p = os.path.join(_REPO, rel)
        if not os.path.exists(p):
            continue
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            s = line.split("#")[0]
            if _WITNESS_PAT.search(s):
                hits.append((rel, i, line.rstrip()[:140]))
    if verbose:
        print("GOLD-COLUMN WITNESS -- %d decision-time reads across %d files" % (len(hits), len(_WITNESS_FILES)))
        for rel, i, txt in hits:
            print("  %-52s %5d  %s" % (rel, i, txt.strip()))
    return hits


# ===================================================================================================
# 1. THE GOLD-FREE DECISION LAYER
# ===================================================================================================
_PRED_CACHE = {}
_PROB_CACHE = {}
BE_FORMS = frozenset({"is", "are", "was", "were", "be", "been", "being", "am"})
POSS_PRON = frozenset({"his", "her", "its", "their", "my", "your", "our", "whose",
                       "theirs", "hers", "ours", "yours"})
SING_PRON = frozenset({"he", "him", "his", "himself", "she", "her", "hers", "herself",
                       "it", "its", "itself", "i", "me", "my", "mine", "myself", "this", "that"})
PLUR_PRON = frozenset({"they", "them", "their", "theirs", "themselves", "we", "us", "our", "ours",
                       "ourselves", "these", "those", "yourselves"})
NOMINAL = ("NOUN", "PROPN")


def predicted_tags(doc):
    """The LIVE category organ's tags for every token of one GUM document, sentence by sentence, in order.
    Reads token FORMS only (never a gold column) -> identical under the scrambled-gold twin, by construction."""
    if doc.docid in _PRED_CACHE:
        return _PRED_CACHE[doc.docid]
    from hdlab import frontend as F
    tg = F.tagger()
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, []).append(t)
    pred, prob = {}, {}
    for s in sorted(by_sent):
        row = sorted(by_sent[s], key=lambda t: t.idx)
        tags, post = tg.tag_with_posterior([t.form for t in row])
        for k, t in enumerate(row):
            pred[t.gidx] = tags[k]
            p = post[k] if post else {}
            prob[t.gidx] = (float(p.get("PROPN", 0.0)), float(p.get("PRON", 0.0)))
    _PRED_CACHE[doc.docid] = pred
    _PROB_CACHE[doc.docid] = prob
    return pred


def _lemma_goldfree(form, dual_route=False):
    """The identity key of every common-noun coref decision. `dual_route`: when the STORED route is silent
    (the string is not in the lexicon -- most names and most technical nouns) the RULE route still strips the
    regular plural, so `Pediatricians` keys with `Pediatrician` instead of staying a distinct string."""
    from hdlab.morphology import morphy
    low = form.lower()
    lem = morphy(low, "n")
    if lem:
        return lem
    if dual_route and low.isalpha() and len(low) > 3 and low.endswith("s") \
            and not low.endswith(_NOT_PLURAL_S):
        if low.endswith("ies"):
            return low[:-3] + "y"
        if low.endswith("es") and low[:-2].endswith(("s", "x", "z", "ch", "sh")):
            return low[:-2]
        return low[:-1]
    return low


_NOT_PLURAL_S = ("ss", "us", "is", "as", "os")


def _number_goldfree(form, dual_route=False):
    """The morphology organ's decomposition IS the number cue: a stripped plural suffix -> plural.
    dual_route (Pinker/Ullman words-and-rules; the mode `hdlab.morphology` itself ships): when the STORED
    route is silent -- the word is not in the lexicon at all, which is most proper names and most technical
    nouns -- the RULE route still fires on the -s suffix. Without it every unknown plural reads SINGULAR
    and the pronoun pick's number agreement is silently wrong on exactly the referents that matter."""
    from hdlab.morphology import morphy
    low = form.lower()
    if not low.isalpha():
        return ""
    lem = morphy(low, "n")
    if lem and lem != low:
        return "plur"
    if lem:
        return "sing"
    if dual_route and low.endswith("s") and not low.endswith(_NOT_PLURAL_S) and len(low) > 3:
        return "plur"                        # the RULE route: the stored route was silent
    return "sing"


def _gn_goldfree(head_form, mtype, gaz, dual_route=False):
    low = head_form.lower()
    if mtype == "pronoun":
        g = G.GENDERED_PRON.get(low, "")
        if not g and low in ("it", "its", "itself"):
            g = "n"
        num = "plur" if low in PLUR_PRON else ("sing" if low in SING_PRON else "")
        return g, num
    g = ""
    if mtype == "name" and gaz is not None:
        g = {"masc": "m", "fem": "f", "m": "m", "f": "f"}.get(gaz.get(low, ""), "")
    return g, _number_goldfree(head_form, dual_route=dual_route)


# the categories that CLOSE an English NP run: a preposition, a coordinator, a clause marker, a verb,
# a relative pronoun or a comma all start a NEW nominal domain -- everything after them modifies, and the
# head of the whole span is the last nominal BEFORE the first of them.
_NP_BREAK = ("ADP", "CCONJ", "SCONJ", "VERB", "AUX", "PART")
_REL = frozenset({"who", "whom", "whose", "which", "that"})


def _head_goldfree(span, pred, np_run=False):
    """HEAD of a mention span from PREDICTED categories only.

    v1 (`np_run=False`) HEAD-FINAL: the last NOUN/PROPN of the span -- the rule hdlab/attachment_arm uses
    inside an NP and the one pri 104's shipped `coref._span_head_is_name` uses.
    v2 (`np_run=True`) THE NP-RUN HEAD: English NPs are head-final WITHIN the head domain, but a
    preposition / coordinator / relative marker / comma OPENS A NEW DOMAIN ("the American College of
    Pediatricians" heads on College, "Kim and Jo" on Kim, "Kim , the doctor" on Kim). So the head is the
    last NOUN/PROPN of the FIRST nominal domain. This is the same domain boundary the attachment arm's
    NP_SPLIT cue uses, and it is what the gold `head` column encodes for these spans."""
    toks = list(span)
    if np_run:
        cut = len(toks)
        seen_nom = False
        for i, t in enumerate(toks):
            c = pred.get(t.gidx, "X")
            low = t.form.lower()
            if c in NOMINAL:
                seen_nom = True
                continue
            if seen_nom and (c in _NP_BREAK or c == "PUNCT" or low in _REL):
                cut = i
                break
        toks = toks[:cut] or list(span)
    noms = [t for t in toks if pred.get(t.gidx) in NOMINAL]
    if noms:
        return noms[-1]
    prons = [t for t in span if pred.get(t.gidx) == "PRON" or t.form.lower() in G.PRONOUNS_ALL]
    if prons:
        return prons[-1]
    nonp = [t for t in span if pred.get(t.gidx) != "PUNCT"]
    return (nonp or span)[-1]


def _mtype_goldfree(head, span, pred, wire=False, tau=None, prob=None):
    up = pred.get(head.gidx, "X")
    low = head.form.lower()
    if tau is not None and prob is not None:
        # PHASE DIAGRAM (the brief authorises sweeping the posterior mass): type by the category organ's
        # POSTERIOR MASS on PROPN rather than its argmax. A graded belief, thresholded once at the point of
        # decision -- the decision the entity layer has to make is binary (open a name file or not), but the
        # evidence it reads is graded, and the operating point on that graded evidence is free.
        pp, pr = prob.get(head.gidx, (0.0, 0.0))
        if low in G.PRONOUNS_ALL and pp < tau:
            return "pronoun", up
        if pr >= 0.5 and pp < tau:
            return "pronoun", up
        return ("name" if pp >= tau else "common"), up
    if up == "PRON" or (low in G.PRONOUNS_ALL and up != "PROPN"):
        return "pronoun", up
    if wire:
        from hdlab.coref import name_content_tokens
        forms = [t.form for t in span]
        ups = [pred.get(t.gidx, "X") for t in span]
        return ("name" if name_content_tokens(forms, upos=ups) else "common"), up
    return ("name" if up == "PROPN" else "common"), up


def positional_deprel(doc, pred, per_predicate=False):
    """GOLD-FREE role source over PREDICTED categories.

    v1 (`per_predicate=False`) THE LIVE READER'S OWN PROXY: one verb per SENTENCE -- preverbal nominal ->
    nsubj, postverbal -> obj. This is `URG.Resolver(positional_roles=True)` and the reader's `_assign_roles`.
    v2 (`per_predicate=True`) THE COMPETITION MODEL'S WORD-ORDER CUE, applied PER PREDICATE (MacWhinney &
    Bates: preverbal = actor, postverbal = undergoer -- the strongest cue in English, and it is a cue about
    THIS clause, not about the sentence). A sentence with three verbs has three preverbal slots; v1 hands
    every nominal after the first verb to OBJECT, which flattens Centering's Subject > Object ranking
    (Grosz, Joshi & Weinstein 1995) for every clause but the first.
    Possessive ('s / possessive pronoun) -> nmod:poss in both."""
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, []).append(t)
    out = {}
    for s, ts in by_sent.items():
        row = sorted(ts, key=lambda t: t.idx)
        forms = [t.form.lower() for t in row]
        cats = [pred.get(t.gidx, "X") for t in row]
        for t in row:
            out[t.gidx] = ""
        # nominal-run heads (the argument candidates), in order
        heads = []
        i = 0
        while i < len(row):
            if cats[i] in NOMINAL or cats[i] == "PRON":
                j = i
                while j + 1 < len(row) and (cats[j + 1] in NOMINAL or cats[j + 1] == "PRON"):
                    j += 1
                heads.append(j)
                i = j + 1
            else:
                i += 1
        for j in heads:
            nxt = forms[j + 1] if j + 1 < len(row) else ""
            if forms[j] in POSS_PRON or nxt in ("'s", "s", "'"):
                out[row[j].gidx] = "nmod:poss"
        verbs = [k for k, c in enumerate(cats) if c in ("VERB", "AUX")]
        if not per_predicate:
            fv = verbs[0] if verbs else None
            for j in heads:
                if out[row[j].gidx]:
                    continue
                out[row[j].gidx] = "nsubj" if (fv is None or j < fv) else "obj"
            continue
        for vi, v in enumerate(verbs):
            prev_v = verbs[vi - 1] if vi else -1
            nxt_v = verbs[vi + 1] if vi + 1 < len(verbs) else len(row)
            pre = [j for j in heads if prev_v < j < v and not out[row[j].gidx]]
            post = [j for j in heads if v < j < nxt_v and not out[row[j].gidx]]
            if pre:
                out[row[pre[-1]].gidx] = "nsubj"      # the NEAREST preverbal nominal is this verb's actor
            if post:
                out[row[post[0]].gidx] = "obj"        # the FIRST postverbal nominal is its undergoer
        for j in heads:                                # everything else is an oblique / modifier
            if not out[row[j].gidx]:
                out[row[j].gidx] = "obl" if (verbs and j > verbs[0]) else "nmod"
    return out


def goldfree_isa(doc, pred, strict=False):
    """THE QUALITY PUSH: the in-text is-a edges the common-noun type bridge rides on, read from the two
    CONSTRUCTIONS instead of the gold `appos` / `cop` arcs.
      apposition  NOMINAL_RUN , (DET|ADJ|NUM)* NOMINAL_RUN      'Kim , the doctor ,'
      copula      NOMINAL_RUN BE (DET|ADJ|NUM|ADV)* NOMINAL_RUN 'Kim is a doctor'
    Both are surface constructions in the predicted-category stream; neither reads a gold column."""
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, []).append(t)
    links = set()
    for s, ts in by_sent.items():
        row = sorted(ts, key=lambda t: t.idx)
        cats = [pred.get(t.gidx, "X") for t in row]
        forms = [t.form for t in row]
        runs = []
        i = 0
        while i < len(row):
            if cats[i] in NOMINAL:
                j = i
                while j + 1 < len(row) and cats[j + 1] in NOMINAL:
                    j += 1
                runs.append((i, j))
                i = j + 1
            else:
                i += 1
        for a in range(len(runs) - 1):
            (s1, e1), (s2, e2) = runs[a], runs[a + 1]
            gap = forms[e1 + 1:s2]
            gapc = cats[e1 + 1:s2]
            if not gap or len(gap) > 4:
                continue
            low = [w.lower() for w in gap]
            is_appos = gap[0] == "," and all(c in ("DET", "ADJ", "NUM", "PUNCT") for c in gapc)
            is_cop = any(w in BE_FORMS for w in low) and \
                all(c in ("DET", "ADJ", "NUM", "VERB", "AUX", "ADV") for c in gapc)
            if strict:
                # PRECISION (the v1 detector fired on any two adjacent nominal runs with a BE or a comma
                # between them -- 522 edges, 59 of them shared with the gold appos/cop arcs). The two
                # constructions that actually STATE a type are narrower:
                #   apposition       a NAME followed by a DETERMINED common nominal:  'Kim , the doctor ,'
                #   predicate nominal a BE followed by a DETERMINED common nominal:   'Kim is a doctor'
                # A bare predicate nominal ('the field is data') is a different construction -- it states an
                # identity between two kinds, not a type of an individual -- so the DETERMINER is required.
                has_det = any(c == "DET" for c in gapc)
                is_appos = is_appos and has_det and cats[e1] == "PROPN"
                is_cop = is_cop and has_det and cats[e2] == "NOUN"
            if is_appos or is_cop:
                la, lb = _lemma_goldfree(forms[e1]), _lemma_goldfree(forms[e2])
                if la != lb:
                    links.add(frozenset((la, lb)))
    typed = {}
    for l in links:
        a, b = tuple(l)
        typed.setdefault(a, set()).add(b)
        typed.setdefault(b, set()).add(a)
    return typed


def scramble_gold_columns(doc, seed=SEED):
    """THE TWIN: permute the six GOLD columns across the tokens of each document (forms and the MISC
    Entity= answer key untouched). A gold-free arm must be byte-identical under this."""
    rng = random.Random(seed + (abs(hash(doc.docid)) & 0xFFFF))
    fields = [(t.upos, t.xpos, t.lemma, t.feats, t.head, t.deprel) for t in doc.toks]
    rng.shuffle(fields)
    for t, f in zip(doc.toks, fields):
        t.upos, t.xpos, t.lemma, t.feats, t.head, t.deprel = f


def is_scrubbed(doc, thresh=0.5):
    """GUM's 18 `GUM_reddit_*` documents are REDACTED: the FORM column is replaced by underscores (the
    lemma/upos/head columns are intact, because the text itself cannot be redistributed -- GUM ships
    `process_underscores.py` to restore it). 16,364 of 273,103 tokens (6.0%), and in those 18 documents it
    is 100% of the tokens. A GOLD instrument never noticed, because it reads the columns; the LIVE reader
    has NO TEXT there at all. `gum_coref.load_docs` already carries an `exclude_scrubbed=True` parameter --
    and nothing in the function body ever reads it."""
    n = len(doc.toks)
    if not n:
        return False
    m = sum(1 for t in doc.toks if t.form and set(t.form) == {"_"})
    return m / n > thresh


_ISA_CACHE = {}


def parse_arm(arm):
    """`gf+lemma+feats_twin` -> ('gf', {'lemma','feats'}, True). The `+col` suffixes are the HOLD-ONE-GOLD
    ablations that trace which gold column carries the signal, rung by rung."""
    scram = arm.endswith("_twin")
    base = arm[:-5] if scram else arm
    parts = base.split("+")
    return parts[0], set(parts[1:]), scram


def apply_arm(docs, arm, gaz):
    """Rewrite every DECISION-TIME field of every doc for one arm. `gold` = untouched."""
    _ISA_CACHE.clear()
    if arm.startswith("gold"):
        return docs
    from hdlab.coref import name_content_tokens
    base, keep, scram = parse_arm(arm)
    full = base.startswith("gf")
    v2 = base.startswith("gf2") or base.startswith("gf3")
    v3 = base.startswith("gf3")           # + the dual-route LEMMA (the stored route is silent on most names)
    tau = None
    if "tau" in base:
        tau = float(base.split("tau")[1].split("_")[0]) / 100.0
    for d in docs:
        if scram:
            scramble_gold_columns(d)
        pred = predicted_tags(d)
        gmap = {t.gidx: t for t in d.toks}
        if full:
            dep = positional_deprel(d, pred, per_predicate=v2)
            if "isa" in base or base.endswith("_wire"):
                if "deprel" not in keep:
                    _ISA_CACHE[d.docid] = goldfree_isa(d, pred, strict=("isa2" in base))
            for t in d.toks:
                if "upos" not in keep:
                    t.upos = pred.get(t.gidx, "X")
                    t.xpos = ""
                if "lemma" not in keep:
                    t.lemma = _lemma_goldfree(t.form, dual_route=v3)
                if "feats" not in keep:
                    t.feats = {}
                if "head" not in keep:
                    t.head = 0
                if "deprel" not in keep:
                    t.deprel = dep.get(t.gidx, "")
        for m in d.mentions:
            span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
            span = [t for t in span if t.sent == m.sent] or span
            if not span:
                continue
            if not full:
                # pri 104's isolation: ONLY the name-vs-common decision moves; pronouns held FIXED
                if m.mtype == "pronoun":
                    continue
                head = gmap.get(m.head_g)
                if head is None:
                    continue
                if base == "caps":
                    is_name = bool(name_content_tokens([t.form for t in span]))
                else:
                    up = pred.get(head.gidx, "X")
                    is_name = (up == "PROPN")
                    m.upos = up
                m.mtype = "name" if is_name else "common"
                continue
            if "head" in keep:
                head = gmap.get(m.head_g) or _head_goldfree(span, pred, np_run=v2)
            else:
                head = _head_goldfree(span, pred, np_run=v2)
            if "upos" in keep:
                mt = G._mention_type(head, span)
                up = head.upos
            else:
                mt, up = _mtype_goldfree(head, span, pred, wire=base.endswith("_wire"),
                                         tau=tau, prob=_PROB_CACHE.get(d.docid))
            m.head_g = head.gidx
            m.upos = up
            m.mtype = mt
            m.lemma_head = (head.lemma.lower() if "lemma" in keep
                            else _lemma_goldfree(head.form, dual_route=v3))
            if "feats" in keep:
                m.gender, m.number = G._gender_number(head, mt, gaz)
            else:
                m.gender, m.number = _gn_goldfree(head.form, mt, gaz, dual_route=v2)
    return docs


# ===================================================================================================
# 2. THE BOARD ROWS UNDER EACH ARM
# ===================================================================================================
def _isa_shim(doc):
    return _ISA_CACHE.get(doc.docid, {})


def run_board_arms(arms, n_docs=None, out=None, drop_scrubbed=False):
    """Run the board's coref / common-noun / salience rows under each arm, on the SAME populations."""
    import experiments.exp_board_coref_gum_v1 as BCG
    import experiments.exp_commonnoun_diffhead_anatomy_gum_v1 as ANAT
    gaz = load_given_gazetteer()
    orig_load = BCG._load_test
    orig_isa = ANAT._appos_copula_isa
    keys = ("n", "model_acc", "strongest_floor", "strongest_floor_name", "twin_acc",
            "model_minus_strongest", "model_minus_twin", "ci_sep_over_strongest", "ci_sep_over_twin")
    res = {"arms": {}, "n_docs": n_docs, "utc": datetime.now(timezone.utc).isoformat()}
    for arm in arms:
        docs_all = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz)
        if drop_scrubbed:
            docs_all = [d for d in docs_all if not is_scrubbed(d)]
        apply_arm(docs_all, arm, gaz)
        test = [d for i, d in enumerate(docs_all) if i % 2 == 1]

        def patched(nd=None, _d=docs_all, _t=test, _g=gaz):
            return _d, _t, _g

        BCG._load_test = patched
        _b, _keep, _s = parse_arm(arm)
        if _b == "gold_noisa":
            ANAT._appos_copula_isa = lambda doc: {}      # is the in-text is-a seed load-bearing AT ALL?
        elif not _b.startswith("gf") or "deprel" in _keep:
            ANAT._appos_copula_isa = orig_isa            # gold appos/cop arcs are still there
        elif "isa" in _b or _b.endswith("_wire"):
            ANAT._appos_copula_isa = _isa_shim           # the gold-free CONSTRUCTION detector
        else:
            ANAT._appos_copula_isa = lambda doc: {}      # gold arcs GONE, nothing put back
        t0 = time.time()
        try:
            row, detail = BCG.board_coref_modern_dimension(n_docs=n_docs)
            sal, _sd = BCG.board_salience_modern_dimension(n_docs=n_docs)
        finally:
            BCG._load_test = orig_load
            ANAT._appos_copula_isa = orig_isa
        mt = Counter(m.mtype for d in test for m in d.mentions)
        rec = {"coref_pronoun": {k: row.get(k) for k in keys},
               "common_noun": {k: detail["common_noun"].get(k) for k in keys},
               "entity_kb_hardlink": {k: detail["entity_kb_hardlink"].get(k) for k in keys},
               "salience": {k: sal.get(k) for k in keys},
               "mention_types_test": dict(mt),
               "elapsed_s": round(time.time() - t0, 1)}
        res["arms"][arm] = rec
        print("ARM %-10s coref n=%-5s acc=%-7s floor=%-7s | common n=%-5s acc=%-7s floor=%-7s | "
              "salience acc=%-7s | name/common/pron %d/%d/%d  (%ss)"
              % (arm, rec["coref_pronoun"]["n"], rec["coref_pronoun"]["model_acc"],
                 rec["coref_pronoun"]["strongest_floor"], rec["common_noun"]["n"],
                 rec["common_noun"]["model_acc"], rec["common_noun"]["strongest_floor"],
                 rec["salience"]["model_acc"], mt.get("name", 0), mt.get("common", 0),
                 mt.get("pronoun", 0), rec["elapsed_s"]), flush=True)
    if out:
        json.dump(res, open(out, "w", encoding="ascii"), indent=1, sort_keys=True)
        print("wrote", out)
    return res


def type_confusion(arm="gf2", n_docs=None):
    """THE SIGNAL-LOSS TRACE AT THE TYPING RUNG, in counts: gold mention type x the arm's mention type, on
    the board's own TEST documents, plus the head-token agreement and the lemma-key agreement. This is what
    the board's two entity rows lose when the gold columns go away."""
    gaz = load_given_gazetteer()
    gold_docs = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz)
    gold_test = [d for i, d in enumerate(gold_docs) if i % 2 == 1]
    gold_m = {(d.docid, m.start_g, m.end_g): m for d in gold_test for m in d.mentions}
    arm_docs = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz)
    apply_arm(arm_docs, arm, gaz)
    arm_test = [d for i, d in enumerate(arm_docs) if i % 2 == 1]
    conf = Counter(); head_ok = head_tot = 0; lem_ok = lem_tot = 0
    slip = Counter()
    for d in arm_test:
        for m in d.mentions:
            g = gold_m.get((d.docid, m.start_g, m.end_g))
            if g is None:
                continue
            conf[(g.mtype, m.mtype)] += 1
            head_tot += 1
            head_ok += int(g.head_g == m.head_g)
            lem_tot += 1
            lem_ok += int(g.lemma_head == m.lemma_head)
            if g.mtype != m.mtype and len(slip) < 4000:
                slip[(g.mtype, m.mtype, m.text[:26])] += 1
    tot = sum(conf.values())
    print("TYPE CONFUSION  arm=%s  n=%d   (gold -> %s)" % (arm, tot, arm))
    for gt in ("name", "common", "pronoun"):
        row = [conf[(gt, at)] for at in ("name", "common", "pronoun")]
        print("  gold %-8s -> name %-5d common %-5d pronoun %-5d   (recall %.4f)"
              % (gt, row[0], row[1], row[2], row[["name", "common", "pronoun"].index(gt)] / max(1, sum(row))))
    agree = sum(conf[(x, x)] for x in ("name", "common", "pronoun"))
    print("  type agreement %.4f | span-head agreement %.4f | lemma-key agreement %.4f"
          % (agree / max(1, tot), head_ok / max(1, head_tot), lem_ok / max(1, lem_tot)))
    print("  biggest slips:", slip.most_common(12))
    return {"confusion": {"%s->%s" % k: v for k, v in conf.items()}, "n": tot,
            "type_agreement": round(agree / max(1, tot), 4),
            "head_agreement": round(head_ok / max(1, head_tot), 4),
            "lemma_agreement": round(lem_ok / max(1, lem_tot), 4)}


def twin_identity_check(res):
    """BAR 8a: the scrambled-gold twin must leave a gold-free arm BYTE-IDENTICAL."""
    ok = True
    for arm in list(res["arms"]):
        if not arm.endswith("_twin"):
            continue
        base = arm[:-5]
        if base not in res["arms"]:
            continue
        a = {k: v for k, v in res["arms"][base].items() if k != "elapsed_s"}
        b = {k: v for k, v in res["arms"][arm].items() if k != "elapsed_s"}
        same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
        ok = ok and same
        print("TWIN %-14s vs %-10s BYTE-IDENTICAL=%s" % (arm, base, same))
        if not same:
            for k in a:
                if json.dumps(a[k], sort_keys=True) != json.dumps(b[k], sort_keys=True):
                    print("   DIFFERS:", k, "\n     base:", a[k], "\n     twin:", b[k])
    return ok


# ===================================================================================================
# 3. THE READER'S OWN ENTITY QA INSTRUMENT -- the diagnosis and the gold-free repair
# ===================================================================================================
def qa_diagnose(n_docs=8, verbose=True):
    """WHY ZERO QUESTIONS. `build_coref_questions` names a gold cluster through `_named_clusters(sm)`, which is
    keyed by `sm.entities[].cluster`. Since 2026-09-09 `online_entity_cluster` is DEFAULT-ON and re-keys every
    NON-pronoun mention to a fresh NEGATIVE online file id, while `sm.coref_resolutions[].gold_cluster` stays in
    the POSITIVE coref-column id space -> the two key spaces are disjoint -> `names.get(gold_cluster)` is always
    None. This function counts the disjointness per document."""
    import experiments.exp_situation_model_qa_v1 as Q
    from hdlab.situation_reader import SituationReader
    gaz = load_given_gazetteer()
    rows = []
    for doc in Q.load_docs(n_docs):
        path = os.path.join(Q.CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        sm = Q.build_reader(gaz, capable=True).read(path)
        names = Q._named_clusters(sm)
        gold_cl = {r.gold_cluster for r in sm.coref_resolutions}
        neg = sum(1 for e in sm.entities if isinstance(e.cluster, int) and e.cluster < 0)
        rows.append({"doc": doc, "entities": len(sm.entities), "neg_id_entities": neg,
                     "named_clusters": len(names), "persons": sum(1 for e in sm.entities if e.is_person),
                     "persons_with_heads": sum(1 for e in sm.entities if e.is_person and e.heads),
                     "resolutions": len(sm.coref_resolutions),
                     "gold_clusters": len(gold_cl),
                     "key_overlap": len(gold_cl & set(names)),
                     "questions": len(Q.build_coref_questions(sm))})
        if verbose:
            r = rows[-1]
            print("  %-26s entities=%-4d neg_ids=%-4d named=%-4d persons=%-3d w/heads=%-3d res=%-4d "
                  "gold_cl=%-3d overlap=%-3d Q=%d"
                  % (r["doc"], r["entities"], r["neg_id_entities"], r["named_clusters"], r["persons"],
                     r["persons_with_heads"], r["resolutions"], r["gold_clusters"], r["key_overlap"],
                     r["questions"]))
    return rows


_PRON = None


def _is_pron_word(w):
    global _PRON
    if _PRON is None:
        import experiments.exp_situation_model_qa_v1 as Q
        _PRON = Q._PRONOUNS
    return str(w).lower() in _PRON


def gold_cluster_names(coref_mentions):
    """THE ANSWER KEY (legitimate): gold cluster -> its canonical surface name, the longest distinct
    non-pronoun mention span of that gold chain. This is the gold side of the question, nothing else."""
    by = defaultdict(list)
    for m in coref_mentions:
        if m.get("is_pronoun"):
            continue
        by[m["cluster"]].append(" ".join(m.get("span_toks", [m["head"]])))
    out = {}
    for c, hs in by.items():
        hs = [h for h in hs if h and not _is_pron_word(h)]
        if hs:
            out[c] = max(hs, key=len)
    return out


def reader_file_names(sm):
    """THE MODEL'S OWN NAMING (gold-free): head string -> the canonical name of the reader's OWN entity file
    that holds it. This is the entity layer doing the job it exists for -- no gold cluster is consulted."""
    head2name = {}
    for e in sm.entities:
        hs = [h for h in e.heads if h and not _is_pron_word(h)]
        if not hs:
            continue
        canon = max(hs, key=len)
        for h in hs:
            for key in (h.lower(), h.lower().split()[-1] if h.split() else ""):
                if key and (key not in head2name or len(canon) > len(head2name[key])):
                    head2name[key] = canon
    return head2name


def _canon(head, head2name):
    if head is None:
        return None
    low = str(head).lower()
    return head2name.get(low) or head2name.get(low.split()[-1] if low.split() else "") or str(head)


def qa_goldfree(n_docs=8, verbose=True):
    """THE REPAIRED INSTRUMENT, in two naming schemes, on the same questions.
      question  : one per cross-sentence pronoun target whose GOLD chain has a nameable span (the answer key)
      cluster_named (INFORMATIONAL): the 2026-09-07 readout -- the model's pick is named through the GOLD
                  cluster of the mention it picked (a gold read at READOUT: two surface forms of one gold
                  chain are made identical for free)
      head_named (THE HONEST ARM): the model's pick is its own `resolved_head`, canonicalised through the
                  READER'S OWN entity files. No gold column anywhere on the model side.
    Floors (recomputed in BOTH schemes): recency = the nearest preceding non-pronoun mention;
    mostfreq = the most-mentioned nameable entity."""
    import experiments.exp_situation_model_qa_v1 as Q
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets
    gaz = load_given_gazetteer()
    orig = SituationReader._read_entities

    def patched(self, mentions, targets, n_sents):
        res, ec, ss = orig(self, mentions, targets, n_sents)
        self._last_recs_ec = ec
        return res, ec, ss

    SituationReader._read_entities = patched
    rows = {"cluster_named": [], "head_named": []}
    per_doc = {"cluster_named": [], "head_named": []}
    nq = 0
    try:
        for doc in Q.load_docs(n_docs):
            path = os.path.join(Q.CONLL_DIR, doc + ".conll")
            if not os.path.exists(path):
                continue
            mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
            targets = build_pronoun_targets(mentions)
            rd = Q.build_reader(gaz, capable=True)
            sm = rd.read(path)
            recs = getattr(rd, "_last_recs_ec", [])
            gnames = gold_cluster_names(mentions)               # the ANSWER KEY
            fnames = reader_file_names(sm)                      # the MODEL's own files
            cnt = Counter(m["cluster"] for m in mentions if not m.get("is_pronoun") and gnames.get(m["cluster"]))
            mf_cluster = gnames[cnt.most_common(1)[0][0]] if cnt else None
            fcnt = Counter()
            for e in sm.entities:
                hs = [h for h in e.heads if h and not _is_pron_word(h)]
                if hs:
                    fcnt[max(hs, key=len)] += e.n_mentions
            mf_head = fcnt.most_common(1)[0][0] if fcnt else None
            pd = {"cluster_named": [0, 0, 0, 0], "head_named": [0, 0, 0, 0]}   # n, model, recency, mostfreq
            for i, r in enumerate(sm.coref_resolutions):
                if r.sent_dist < 1:
                    continue
                gold = gnames.get(r.gold_cluster)
                if gold is None:
                    continue
                nq += 1
                tgt = targets[i]["target"]
                rec_m = _recency_mention(tgt, mentions)
                for scheme in ("cluster_named", "head_named"):
                    if scheme == "cluster_named":
                        ans = gnames.get(r.resolved_cluster)
                        rfl = gnames.get(rec_m["cluster"]) if rec_m else None
                        mfl = mf_cluster
                    else:
                        rh = recs[i].get("resolved_head") if i < len(recs) else None
                        ans = _canon(rh, fnames) if rh else None
                        rfl = _canon(" ".join(rec_m.get("span_toks", [rec_m["head"]])), fnames) if rec_m else None
                        mfl = mf_head
                    m_ok = int(Q._match(ans, gold, "coref"))
                    r_ok = int(Q._match(rfl, gold, "coref"))
                    f_ok = int(Q._match(mfl, gold, "coref"))
                    rows[scheme].append({"model": m_ok, "recency": r_ok, "mostfreq": f_ok})
                    p = pd[scheme]
                    p[0] += 1; p[1] += m_ok; p[2] += r_ok; p[3] += f_ok
            for scheme in ("cluster_named", "head_named"):
                if pd[scheme][0]:
                    per_doc[scheme].append(pd[scheme])
            if verbose:
                cn = [pd["cluster_named"][j] / max(1, pd["cluster_named"][0]) for j in (1, 2, 3)]
                hn = [pd["head_named"][j] / max(1, pd["head_named"][0]) for j in (1, 2, 3)]
                print("  %-26s Qs=%-4d  cluster_named m/r/f %.3f/%.3f/%.3f | head_named m/r/f %.3f/%.3f/%.3f"
                      % (doc, pd["cluster_named"][0], cn[0], cn[1], cn[2], hn[0], hn[1], hn[2]), flush=True)
    finally:
        SituationReader._read_entities = orig
    out = {"n_questions": nq, "schemes": {}}
    for scheme in ("cluster_named", "head_named"):
        rs = rows[scheme]
        n = len(rs)
        acc = {k: (sum(r[k] for r in rs) / n if n else 0.0) for k in ("model", "recency", "mostfreq")}
        boot = {k: _paired_boot_docs(per_doc[scheme], j, 1) for k, j in (("recency", 2), ("mostfreq", 3))}
        out["schemes"][scheme] = {"n": n, "acc": {k: round(v, 4) for k, v in acc.items()},
                                  "model_minus_recency": boot["recency"],
                                  "model_minus_mostfreq": boot["mostfreq"]}
        print("QA %-14s n=%-4d model=%.4f recency=%.4f mostfreq=%.4f  d_rec=%s d_mf=%s"
              % (scheme, n, acc["model"], acc["recency"], acc["mostfreq"],
                 boot["recency"], boot["mostfreq"]))
    return out


def _recency_mention(target_mention, mentions):
    ts, tw = target_mention["sent_idx"], target_mention.get("wtok_start", 0)
    best = None
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        if (m["sent_idx"], m.get("wtok_start", 0)) <= (ts, tw):
            if best is None or (m["sent_idx"], m.get("wtok_start", 0)) > (best["sent_idx"], best.get("wtok_start", 0)):
                best = m
    return best


def _paired_boot_docs(per_doc, j_model, j_floor_unused, n_boot=2000, seed=13):
    """Doc-paired bootstrap of (model - floor). per_doc rows are [n, model, recency, mostfreq]."""
    rng = random.Random(seed)
    n = len(per_doc)
    if n == 0:
        return [0.0, 0.0, 0.0]
    idx = list(range(n))
    ds = []
    for _ in range(n_boot):
        samp = [rng.choice(idx) for _ in range(n)]
        tot = sum(per_doc[i][0] for i in samp) or 1
        a = sum(per_doc[i][1] for i in samp) / tot
        b = sum(per_doc[i][j_model] for i in samp) / tot
        ds.append(a - b)
    ds.sort()
    tot = sum(p[0] for p in per_doc) or 1
    d = sum(p[1] for p in per_doc) / tot - sum(p[j_model] for p in per_doc) / tot
    return [round(d, 4), round(ds[int(0.025 * n_boot)], 4), round(ds[int(0.975 * n_boot)], 4)]


# ===================================================================================================
def _self_test():
    """Cheap structural self-tests -- no corpus pass."""
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=4, name_gazetteer=gaz)
    d = docs[0]
    pred = predicted_tags(d)
    assert len(pred) == len(d.toks), (len(pred), len(d.toks))
    before = dict(pred)
    scramble_gold_columns(d)
    _PRED_CACHE.pop(d.docid, None)
    after = predicted_tags(d)
    assert before == after, "predicted tags moved under a scrambled gold column -- a gold read leaked in"
    assert _lemma_goldfree("dogs") == "dog" and _number_goldfree("dogs") == "plur"
    assert _number_goldfree("dog") == "sing"
    g, n = _gn_goldfree("she", "pronoun", gaz)
    assert g == "f" and n == "sing", (g, n)
    print("PASS self-test: organ tags invariant under gold-column scramble; lemma/number/gender gold-free")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--witness", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--qa", action="store_true")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--confusion", default="")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--arms", default="gold,caps,cat,gf,gf_isa,gf_wire,gf_twin")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--tag", default="")
    ap.add_argument("--drop-scrubbed", action="store_true")
    a = ap.parse_args()
    od = get_output_dir()
    if a.self_test:
        return _self_test()
    if a.witness:
        witness_gold_reads()
    if a.diagnose:
        rows = qa_diagnose(a.docs or 8)
        json.dump(rows, open(os.path.join(od, "qa_diagnose%s.json" % a.tag), "w", encoding="ascii"), indent=1)
    if a.confusion:
        out = {arm: type_confusion(arm, a.docs) for arm in a.confusion.split(",")}
        json.dump(out, open(os.path.join(od, "type_confusion%s.json" % a.tag), "w", encoding="ascii"), indent=1)
    if a.board:
        res = run_board_arms(a.arms.split(","), n_docs=a.docs, drop_scrubbed=a.drop_scrubbed,
                             out=os.path.join(od, "board_arms%s.json" % a.tag))
        twin_identity_check(res)
    if a.qa:
        res = qa_goldfree(a.docs or 8)
        json.dump(res, open(os.path.join(od, "qa_goldfree%s.json" % a.tag), "w", encoding="ascii"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
