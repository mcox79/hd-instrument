"""gum_coref -- parse the OntoGUM CoNLL-U coref layer (modern gold) into discourse referents.

Foundation for `form_the_unified_discourse_referent_before_the_pronoun_pick_the_shared_entity_lever`.
GUM CoNLL-U carries, per token: id form lemma upos xpos feats head deprel deps misc, with
coreference in MISC as `Entity=(N ... N)` (GRP scheme, numeric group ids, concatenated brackets).

Gives, per document:
  - sentences of tokens (with gold UD POS + morph feats)
  - coref chains: entity_id -> ordered list of Mention
  - per Mention: type (name / common / pronoun) from the UD head UPOS; gender; number; salience inputs.

Reusable by the experiment cells; NO external LLM.

GOLD-FREE DECISION LAYER (pri-109, 2026-09-14). Until now EVERY decision this module makes was taken from a
GOLD CoNLL-U column, so the board rows that consume it (`coref`, `common_noun_coref`, `salience`) were scored
with information the live reader never has:
    cols[3] upos   -> `_mention_type` (name / common / pronoun) AND `_head_of_span`'s category preference
    cols[2] lemma  -> `Mention.lemma_head`, the identity key of every common-noun coref decision
    cols[5] feats  -> `_gender_number` (the agreement filter in the pronoun pick)
    cols[6] head   -> `_head_of_span`
    cols[7] deprel -> `URG._role` (ACT-R role prominence) and the in-text is-a edges
`decision_source="organ"` (env `HDLAB_GUM_DECISION=organ`) replaces all five with the LIVE organs -- the
category organ through `hdlab.frontend.tagger()`, the head-final NP-run rule over its categories, the
`hdlab.morphology` lemma, the closed-class pronoun table + the given-name gazetteer, and the Competition
Model's per-predicate word-order cue. The gold columns are kept on the Tok as `gold_*` for the ANSWER KEY
only. `decision_source="gold"` (the default) is byte-identical to the pre-2026-09-14 module.
MEASURED on all 275 GUM docs, TEST = odd docs (`experiments/exp_entity_instruments_gold_free_v1.py --board`):
    coref (pronoun)   gold 0.4681 / floor 0.3621 margin +0.1060 [+0.0786,+0.1327]
                      organ 0.4172 / floor 0.3202 margin +0.0970 [+0.0734,+0.1206]   -- CAPABILITY SURVIVES
    common_noun       gold 0.5671 / floor 0.5412 margin +0.0259 [+0.0134,+0.0385]
                      organ 0.4891 / floor 0.4876 margin +0.0015 [-0.0079,+0.0107]   -- WIN DOES NOT SURVIVE
    salience          gold 0.2555 -> organ 0.2993 (neither CI-separated; underpowered at n=137)
Run:  .venv/Scripts/python.exe experiments/gum_coref.py --self-test
"""
from __future__ import annotations

import glob
import os
import re
import sys
from dataclasses import dataclass, field

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUM_CONLLU = os.path.join(_REPO, "data", "corpora", "gum", "conllu")

PRONOUNS_ALL = {
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves", "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "yourselves", "we", "us", "our", "ours", "ourselves",
    "this", "that", "these", "those", "who", "whom", "whose", "which",
}
THIRD_PERSON = {"he", "him", "his", "himself", "she", "her", "hers", "herself",
                "it", "its", "itself", "they", "them", "their", "theirs", "themselves"}
GENDERED_PRON = {"he": "m", "him": "m", "his": "m", "himself": "m",
                 "she": "f", "her": "f", "hers": "f", "herself": "f"}


DECISION_SOURCE = os.environ.get("HDLAB_GUM_DECISION", "organ")    # "organ" (DEFAULT since 2026-09-14: the board rows are GOLD-FREE -- the live
# organs decide category / lemma / features / head / deprel at scoring time; pri 109) | "gold" (the retired gold-split scorer, kept for the comparison table only)


@dataclass
class Tok:
    idx: int          # 1-indexed within sentence
    form: str
    lemma: str
    upos: str
    xpos: str
    feats: dict
    head: int         # 1-indexed within sentence, 0 = root
    deprel: str
    sent: int         # sentence index within doc
    gidx: int         # global token index within doc
    # THE ANSWER KEY, never an input to a decision (pri-109): under decision_source="organ" the six fields
    # above carry the ORGAN's values and these carry what the treebank said, for scoring and diagnosis only.
    gold_upos: str = ""
    gold_lemma: str = ""
    gold_feats: dict = field(default_factory=dict)
    gold_head: int = 0
    gold_deprel: str = ""


@dataclass
class Mention:
    eid: int                  # gold entity id
    sent: int
    start_g: int              # global token indices (inclusive)
    end_g: int
    head_g: int               # global index of syntactic head token
    text: str
    mtype: str                # 'name' | 'common' | 'pronoun'
    upos: str                 # head UPOS
    gender: str               # 'm' | 'f' | 'n' | '' (unknown)
    number: str               # 'sing' | 'plur' | ''
    lemma_head: str
    order: int = -1           # position in the document reading order (assigned later)


@dataclass
class Doc:
    docid: str
    genre: str
    corpus: str               # 'GUM' | 'GENTLE'
    toks: list                # flat list of Tok, global order
    mentions: list            # list[Mention] in reading order (by start_g)
    chains: dict = field(default_factory=dict)   # eid -> [Mention,...] in reading order


def _parse_feats(s):
    if s == "_" or not s:
        return {}
    out = {}
    for kv in s.split("|"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k] = v
    return out


def _entity_ops(cell):
    """Tokenize a concatenated GUM Entity= cell into ordered ops.
    Grammar: '(N' open, 'N)' close, '(N)' singleton. e.g. '(3(4)' -> [open 3, single 4]."""
    ops, i = [], 0
    while i < len(cell):
        m = re.match(r"\((\d+)\)", cell[i:])
        if m:
            ops.append(("single", int(m.group(1)))); i += m.end(); continue
        m = re.match(r"\((\d+)", cell[i:])
        if m:
            ops.append(("open", int(m.group(1)))); i += m.end(); continue
        m = re.match(r"(\d+)\)", cell[i:])
        if m:
            ops.append(("close", int(m.group(1)))); i += m.end(); continue
        i += 1
    return ops



# ===============================================================================================
# THE GOLD-FREE DECISION LAYER (pri-109). Every function here reads token FORMS and the live
# organs only -- scrambling the six gold columns leaves every one of them byte-identical, which is
# the witness `exp_entity_instruments_gold_free_v1.twin_identity_check` asserts.
# ===============================================================================================
_NOMINAL = ("NOUN", "PROPN")
_NP_BREAK = ("ADP", "CCONJ", "SCONJ", "VERB", "AUX", "PART")
_REL = frozenset({"who", "whom", "whose", "which", "that"})
_NOT_PLURAL_S = ("ss", "us", "is", "as", "os")
_POSS_PRON = frozenset({"his", "her", "its", "their", "my", "your", "our", "whose",
                        "theirs", "hers", "ours", "yours"})
_SING_PRON = frozenset({"he", "him", "his", "himself", "she", "her", "hers", "herself",
                        "it", "its", "itself", "i", "me", "my", "mine", "myself", "this", "that"})
_PLUR_PRON = frozenset({"they", "them", "their", "theirs", "themselves", "we", "us", "our", "ours",
                        "ourselves", "these", "those", "yourselves"})
_BE_FORMS = frozenset({"is", "are", "was", "were", "be", "been", "being", "am"})
# TYPE-STATING CONNECTIVES -- a CONNECTIVE LEXICON, the same form the substrate already uses for causation
# (`hdlab/causal_network` CONNECTIVE_CAUSE_FIRST). MEASURED (pri-109, gold-free common-noun margin on the
# readable GUM population): no seed +0.0020 -> apposition/copula only +0.0056 -> + these connectives +0.0063
# -> + a wider gap +0.0073. RECALL IS THE BINDING CONSTRAINT on this consumer (the bridge is NON-WRITING, so
# a false edge only offers a candidate the salience competition declines while a missing edge removes the
# only path) -- the higher-PRECISION variant scores HALF as well (+0.0030).
_ISA_CONNECTIVES = (
    ("such", "as"), ("including",), ("especially",), ("known", "as"), ("called",),
    ("namely",), ("like",), ("other",), ("kind", "of"), ("type", "of"), ("sort", "of"), ("form", "of"),
)
_ISA_MAX_GAP = 6


def _connective_in_gap(gap_low):
    for pat in _ISA_CONNECTIVES:
        n = len(pat)
        for i in range(len(gap_low) - n + 1):
            if tuple(gap_low[i:i + n]) == pat:
                return True
    return False


def organ_tags(toks):
    """The LIVE category organ (hdlab.frontend.tagger() -> hdlab.lexical_categories) for every token of one
    document, sentence by sentence, in reading order. Reads FORMS only."""
    from hdlab import frontend as F
    tg = F.tagger()
    by_sent = {}
    for t in toks:
        by_sent.setdefault(t.sent, []).append(t)
    pred = {}
    for s in sorted(by_sent):
        row = sorted(by_sent[s], key=lambda x: x.idx)
        for x, c in zip(row, tg.tag([x.form for x in row])):
            pred[x.gidx] = c
    return pred


def organ_lemma(form, dual_route=True):
    """hdlab.morphology (glass-box morphy port). DUAL ROUTE (Pinker/Ullman words-and-rules): when the STORED
    route is silent -- most names and most technical nouns are not in the lexicon -- the RULE route still
    strips the regular plural, so `Pediatricians` keys with `Pediatrician`."""
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


def organ_number(form, dual_route=True):
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
        return "plur"
    return "sing"


def _head_of_span_organ(span_toks, pred):
    """English NPs are head-final WITHIN the head domain; a preposition / coordinator / relative marker /
    comma OPENS A NEW DOMAIN ("the American College of Pediatricians" heads on College, "Kim and Jo" on Kim,
    "Kim , the doctor" on Kim). So the head is the last NOUN/PROPN of the FIRST nominal domain -- the same
    domain boundary the attachment arm's NP_SPLIT cue uses, and what the gold `head` column encodes here."""
    toks = list(span_toks)
    cut, seen = len(toks), False
    for i, t in enumerate(toks):
        c = pred.get(t.gidx, "X")
        low = t.form.lower()
        if c in _NOMINAL:
            seen = True
            continue
        if seen and (c in _NP_BREAK or c == "PUNCT" or low in _REL):
            cut = i
            break
    dom = toks[:cut] or list(span_toks)
    noms = [t for t in dom if pred.get(t.gidx) in _NOMINAL]
    if noms:
        return noms[-1]
    prons = [t for t in span_toks if pred.get(t.gidx) == "PRON" or t.form.lower() in PRONOUNS_ALL]
    if prons:
        return prons[-1]
    nonp = [t for t in span_toks if pred.get(t.gidx) != "PUNCT"]
    return (nonp or list(span_toks))[-1]


def _mention_type_organ(head_tok, span_toks, pred):
    up = pred.get(head_tok.gidx, "X")
    low = head_tok.form.lower()
    if up == "PRON" or (low in PRONOUNS_ALL and up != "PROPN"):
        return "pronoun"
    return "name" if up == "PROPN" else "common"


def _gender_number_organ(head_tok, mtype, name_gazetteer=None):
    low = head_tok.form.lower()
    if mtype == "pronoun":
        g = GENDERED_PRON.get(low, "")
        if not g and low in ("it", "its", "itself"):
            g = "n"
        num = "plur" if low in _PLUR_PRON else ("sing" if low in _SING_PRON else "")
        return g, num
    g = ""
    if mtype == "name" and name_gazetteer is not None:
        g = {"masc": "m", "fem": "f", "m": "m", "f": "f"}.get(name_gazetteer.get(low, ""), "")
    return g, organ_number(head_tok.form)


def positional_deprel(toks, pred):
    """THE COMPETITION MODEL'S WORD-ORDER CUE, applied PER PREDICATE (MacWhinney & Bates: preverbal = actor,
    postverbal = undergoer -- the strongest cue in English, and it is a cue about THIS clause). A sentence
    with three verbs has three preverbal slots; a one-verb-per-sentence proxy hands every nominal after the
    first verb to OBJECT and flattens Centering's Subject > Object ranking for every clause but the first."""
    by_sent = {}
    for t in toks:
        by_sent.setdefault(t.sent, []).append(t)
    out = {}
    for s, ts in by_sent.items():
        row = sorted(ts, key=lambda t: t.idx)
        forms = [t.form.lower() for t in row]
        cats = [pred.get(t.gidx, "X") for t in row]
        for t in row:
            out[t.gidx] = ""
        heads, i = [], 0
        while i < len(row):
            if cats[i] in _NOMINAL or cats[i] == "PRON":
                j = i
                while j + 1 < len(row) and (cats[j + 1] in _NOMINAL or cats[j + 1] == "PRON"):
                    j += 1
                heads.append(j)
                i = j + 1
            else:
                i += 1
        for j in heads:
            nxt = forms[j + 1] if j + 1 < len(row) else ""
            if forms[j] in _POSS_PRON or nxt in ("'s", "s", "'"):
                out[row[j].gidx] = "nmod:poss"
        verbs = [k for k, c in enumerate(cats) if c in ("VERB", "AUX")]
        for vi, v in enumerate(verbs):
            prev_v = verbs[vi - 1] if vi else -1
            nxt_v = verbs[vi + 1] if vi + 1 < len(verbs) else len(row)
            pre = [j for j in heads if prev_v < j < v and not out[row[j].gidx]]
            post = [j for j in heads if v < j < nxt_v and not out[row[j].gidx]]
            if pre:
                out[row[pre[-1]].gidx] = "nsubj"
            if post:
                out[row[post[0]].gidx] = "obj"
        for j in heads:
            if not out[row[j].gidx]:
                out[row[j].gidx] = "obl" if (verbs and j > verbs[0]) else "nmod"
    return out


def construction_isa(toks, pred):
    """The in-text is-a edges the common-noun type bridge rides on, read from the two CONSTRUCTIONS instead
    of the gold `appos` / `cop` arcs:
        apposition  NOMINAL_RUN , (DET|ADJ|NUM)* NOMINAL_RUN      'Kim , the doctor ,'
        copula      NOMINAL_RUN BE (DET|ADJ|NUM|ADV)* NOMINAL_RUN 'Kim is a doctor'
    MEASURED: it recovers about HALF of the +0.0097 the gold arcs are worth; the residual needs a
    real appos/cop LABELLER -- see SOLVED sections 6 and 20."""
    by_sent = {}
    for t in toks:
        by_sent.setdefault(t.sent, []).append(t)
    links = set()
    for s, ts in by_sent.items():
        row = sorted(ts, key=lambda t: t.idx)
        cats = [pred.get(t.gidx, "X") for t in row]
        forms = [t.form for t in row]
        runs, i = [], 0
        while i < len(row):
            if cats[i] in _NOMINAL:
                j = i
                while j + 1 < len(row) and cats[j + 1] in _NOMINAL:
                    j += 1
                runs.append((i, j))
                i = j + 1
            else:
                i += 1
        for a in range(len(runs) - 1):
            (s1, e1), (s2, e2) = runs[a], runs[a + 1]
            gap, gapc = forms[e1 + 1:s2], cats[e1 + 1:s2]
            if not gap or len(gap) > _ISA_MAX_GAP:
                continue
            low = [w.lower() for w in gap]
            is_appos = gap[0] == "," and all(c in ("DET", "ADJ", "NUM", "PUNCT") for c in gapc)
            is_cop = any(w in _BE_FORMS for w in low) and \
                all(c in ("DET", "ADJ", "NUM", "VERB", "AUX", "ADV") for c in gapc)
            is_conn = _connective_in_gap(low)
            if is_appos or is_cop or is_conn:
                la, lb = organ_lemma(forms[e1]), organ_lemma(forms[e2])
                if la != lb:
                    links.add(frozenset((la, lb)))
    typed = {}
    for l in links:
        a, b = tuple(l)
        typed.setdefault(a, set()).add(b)
        typed.setdefault(b, set()).add(a)
    return typed


def apply_organ_layer(toks):
    """Move the six gold columns onto `gold_*` and replace them with the live organs' values IN PLACE."""
    pred = organ_tags(toks)
    dep = positional_deprel(toks, pred)
    for t in toks:
        t.gold_upos, t.gold_lemma, t.gold_feats = t.upos, t.lemma, t.feats
        t.gold_head, t.gold_deprel = t.head, t.deprel
        t.upos = pred.get(t.gidx, "X")
        t.xpos = ""
        t.lemma = organ_lemma(t.form)
        t.feats = {}
        t.head = 0
        t.deprel = dep.get(t.gidx, "")
    return pred


def _mention_type(head_tok, span_toks):
    up = head_tok.upos
    low = head_tok.form.lower()
    if up == "PRON" or low in PRONOUNS_ALL and up not in ("PROPN",):
        # relative/demonstrative pronouns count as pronoun mentions
        return "pronoun"
    if up == "PROPN":
        return "name"
    # a span containing a PROPN head-adjacent (e.g. determiner+PROPN) still name; else common
    if any(t.upos == "PROPN" for t in span_toks) and head_tok.upos in ("PROPN",):
        return "name"
    return "common"


def _head_of_span(span_toks):
    """UD head = the token whose head points outside the span (or is root). Leftmost such."""
    ids = {t.idx for t in span_toks}
    cands = [t for t in span_toks if t.head == 0 or t.head not in ids]
    if cands:
        # prefer a non-punct, non-det head
        for t in cands:
            if t.upos not in ("PUNCT", "DET", "ADP"):
                return t
        return cands[0]
    return span_toks[0]


def _gender_number(head_tok, mtype, name_gazetteer=None):
    feats = head_tok.feats
    number = ""
    if feats.get("Number") == "Sing":
        number = "sing"
    elif feats.get("Number") == "Plur":
        number = "plur"
    gender = ""
    if mtype == "pronoun":
        gender = GENDERED_PRON.get(head_tok.form.lower(), "")
        if not gender:
            g = feats.get("Gender", "")
            gender = {"Masc": "m", "Fem": "f", "Neut": "n"}.get(g, "")
    elif mtype == "name":
        if name_gazetteer is not None:
            gz = name_gazetteer.get(head_tok.form.lower(), "")
            gender = {"masc": "m", "fem": "f", "m": "m", "f": "f"}.get(gz, "")
        if not gender:
            g = feats.get("Gender", "")
            gender = {"Masc": "m", "Fem": "f", "Neut": "n"}.get(g, "")
    else:  # common noun
        g = feats.get("Gender", "")
        gender = {"Masc": "m", "Fem": "f", "Neut": "n"}.get(g, "")
    return gender, number


def parse_gum_conllu(path, name_gazetteer=None, decision_source=None):
    base = os.path.basename(path).replace(".conllu", "")
    parts = base.split("_")
    corpus = parts[0]
    genre = parts[1] if len(parts) > 1 else "?"
    toks = []
    sent = -1
    gidx = 0
    sent_local = {}          # (sent, idx)->Tok for head lookup later; but we store per-token
    # open-bracket stacks per entity id: eid -> list of (start_gidx)
    open_stacks = {}
    raw_mentions = []        # (eid, start_g, end_g)
    cur_sent_toks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc") or line.startswith("#") and "sent_id" not in line and not line.strip() == "#":
                # metadata; sentence boundaries handled by blank lines
                pass
            if not line.strip():
                if cur_sent_toks:
                    cur_sent_toks = []
                continue
            if line.startswith("#"):
                if line.startswith("# sent_id") or line.startswith("# text"):
                    pass
                # a new sentence begins at first token line after a blank; we bump sent on token id==1
                continue
            cols = line.split("\t")
            if len(cols) < 10:
                continue
            tid = cols[0]
            if "-" in tid or "." in tid:   # multiword-token range / empty node
                continue
            idx = int(tid)
            if idx == 1:
                sent += 1
            feats = _parse_feats(cols[5])
            head = int(cols[6]) if cols[6].isdigit() else 0
            t = Tok(idx=idx, form=cols[1], lemma=cols[2] if cols[2] != "_" else cols[1],
                    upos=cols[3], xpos=cols[4], feats=feats, head=head, deprel=cols[7],
                    sent=sent, gidx=gidx)
            toks.append(t)
            # coref ops
            misc = cols[9]
            ent_val = ""
            for kv in misc.split("|"):
                if kv.startswith("Entity="):
                    ent_val = kv[7:]
            if ent_val:
                for op, eid in _entity_ops(ent_val):
                    if op == "single":
                        raw_mentions.append((eid, gidx, gidx))
                    elif op == "open":
                        open_stacks.setdefault(eid, []).append(gidx)
                    elif op == "close":
                        st = open_stacks.get(eid)
                        if st:
                            s0 = st.pop()
                            raw_mentions.append((eid, s0, gidx))
            gidx += 1
    # index tokens for head lookup
    by_sent = {}
    for t in toks:
        by_sent.setdefault(t.sent, {})[t.idx] = t
    gmap = {t.gidx: t for t in toks}

    # pri-109: the DECISION LAYER. "gold" -> every decision below reads a treebank column (the pre-2026-09-14
    # behaviour, byte-identical). "organ" -> the live organs decide and the treebank is the answer key only.
    src = decision_source or DECISION_SOURCE
    pred = apply_organ_layer(toks) if src == "organ" else None

    mentions = []
    for eid, s0, s1 in raw_mentions:
        span = [gmap[g] for g in range(s0, s1 + 1) if g in gmap]
        if not span:
            continue
        # restrict head search to tokens in the same sentence as the span majority
        sent_id = span[0].sent
        span_same = [t for t in span if t.sent == sent_id] or span
        if pred is None:
            head = _head_of_span(span_same)
            mtype = _mention_type(head, span_same)
            gender, number = _gender_number(head, mtype, name_gazetteer)
        else:
            head = _head_of_span_organ(span_same, pred)
            mtype = _mention_type_organ(head, span_same, pred)
            gender, number = _gender_number_organ(head, mtype, name_gazetteer)
        text = " ".join(t.form for t in span)
        mentions.append(Mention(eid=eid, sent=sent_id, start_g=s0, end_g=s1, head_g=head.gidx,
                                text=text, mtype=mtype, upos=head.upos, gender=gender,
                                number=number, lemma_head=head.lemma.lower()))
    mentions.sort(key=lambda m: (m.start_g, m.end_g))
    for i, m in enumerate(mentions):
        m.order = i
    chains = {}
    for m in mentions:
        chains.setdefault(m.eid, []).append(m)
    return Doc(docid=base, genre=genre, corpus=corpus, toks=toks, mentions=mentions, chains=chains)


def _is_scrubbed(toks, frac=0.5):
    """True when the document's surface text is redacted (form == '_' / '__') on more than `frac` of its tokens."""
    n = sum(1 for t in toks if t.form.strip("_") == "")
    return n > frac * len(toks)


def load_docs(gum_only=True, genres=None, limit=None, name_gazetteer=None, exclude_scrubbed=True,
              decision_source=None):
    files = sorted(glob.glob(os.path.join(GUM_CONLLU, "*.conllu")))
    if gum_only:
        files = [f for f in files if os.path.basename(f).startswith("GUM_")]
    docs = []
    for fp in files:
        base = os.path.basename(fp)
        if genres and not any(("_" + g + "_") in base for g in genres):
            continue
        d = parse_gum_conllu(fp, name_gazetteer=name_gazetteer, decision_source=decision_source)
        if exclude_scrubbed and d.toks and _is_scrubbed(d.toks):
            # pri 109 (strategy 2026-09-14): 18 GUM_reddit_* documents ship with the FORM column redacted to
            # underscores (gold columns intact) -- a live reader has no text there; the parameter was declared and
            # never read. Decided on the TEXT, not the filename.
            continue
        docs.append(d)
        if limit and len(docs) >= limit:
            break
    return docs


def _self_test():
    # pri-109: the GOLD-FREE arm must decide identically under a SCRAMBLED gold column (the twin witness).
    import random as _r
    _d = load_docs(gum_only=True, limit=2, decision_source="organ")[0]
    _before = [(m.mtype, m.head_g, m.lemma_head, m.gender, m.number) for m in _d.mentions]
    _raw = load_docs(gum_only=True, limit=2)[0]
    _f = [(t.gold_upos or t.upos, t.gold_lemma or t.lemma, t.gold_feats or t.feats,
           t.gold_head or t.head, t.gold_deprel or t.deprel) for t in _raw.toks]
    _r.Random(0).shuffle(_f)
    for _t, _v in zip(_raw.toks, _f):
        _t.upos, _t.lemma, _t.feats, _t.head, _t.deprel = _v
    apply_organ_layer(_raw.toks)
    _gm = {t.gidx: t for t in _raw.toks}
    _after = []
    for _m in _raw.mentions:
        _sp = [_gm[g] for g in range(_m.start_g, _m.end_g + 1) if g in _gm]
        _sp = [t for t in _sp if t.sent == _m.sent] or _sp
        _pr = {t.gidx: t.upos for t in _raw.toks}
        _h = _head_of_span_organ(_sp, _pr)
        _mt = _mention_type_organ(_h, _sp, _pr)
        _g, _n = _gender_number_organ(_h, _mt, None)
        _after.append((_mt, _h.gidx, organ_lemma(_h.form), _g, _n))
    assert len(_before) == len(_after)
    print("  GOLD-FREE TWIN: %d mentions decided identically under a scrambled gold column: %s"
          % (len(_after), all(a[:3] == b[:3] for a, b in zip(_before, _after))))
    docs = load_docs(gum_only=True)
    assert len(docs) > 150, "expected >150 GUM docs, got %d" % len(docs)
    n_ment = sum(len(d.mentions) for d in docs)
    # chains with >=2 mentions (resolvable coref)
    n_chain = sum(1 for d in docs for e, ms in d.chains.items() if len(ms) >= 2)
    tc = {"name": 0, "common": 0, "pronoun": 0}
    for d in docs:
        for m in d.mentions:
            tc[m.mtype] += 1
    # anaphoric (non-first) mentions by type, and gold-resolvability positive control
    ana = {"name": 0, "common": 0, "pronoun": 0}
    for d in docs:
        for e, ms in d.chains.items():
            for m in ms[1:]:
                ana[m.mtype] += 1
    print("SELFTEST GUM parse:")
    print("  docs=%d  mentions=%d  chains>=2=%d" % (len(docs), n_ment, n_chain))
    print("  mention types: name=%d common=%d pronoun=%d" % (tc["name"], tc["common"], tc["pronoun"]))
    print("  anaphoric (non-first) by type: name=%d common=%d pronoun=%d" % (ana["name"], ana["common"], ana["pronoun"]))
    # positive control: a 3rd-person pronoun antecedent exists for most 3p pronoun anaphora
    p3 = p3_res = 0
    for d in docs:
        for e, ms in d.chains.items():
            for i, m in enumerate(ms):
                if i > 0 and m.mtype == "pronoun" and m.text.lower() in THIRD_PERSON:
                    p3 += 1
                    if any(pm.start_g < m.start_g for pm in ms):
                        p3_res += 1
    print("  3rd-person pronoun anaphora=%d, have a prior antecedent=%d (%.3f)" % (p3, p3_res, p3_res / max(1, p3)))
    assert tc["pronoun"] > 500 and tc["name"] > 500 and tc["common"] > 500, "type distribution looks wrong"
    assert ana["pronoun"] > 300, "too few anaphoric pronouns"
    print("  PASS")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print("import module; or run --self-test")
