"""exp_name_entity_clustering_v1 -- brain-faithful CROSS-MENTION name/entity clustering.

PROBLEM (the_name_branch_shatters_one_character_into_many_entities): the live coref NAME/NOMINAL branch
(hdlab.coreference_resolver._resolve_name_branch) clusters name mentions by TOKEN-OVERLAP (Jaccard) over
a single HEAD TOKEN per mention -- so "Elizabeth" {elizabeth} and "Bennet" {bennet} share ZERO tokens and
SHATTER one character into many entities. Measured motivation (prior coref SOLVED): 65.6% of multi-name
gold characters split, 19.5% of predicted clusters wrongly merge >=2 gold characters, name-mention purity
0.819; downstream who-did-what capped at 0.17 vs oracle-coref 0.62.

THE BRAIN (opening move). Cross-mention person identity is CONTENT-ADDRESSABLE resolution onto a single
PERSON-IDENTITY NODE (Bruce & Young 1986 PINs; Burton/Bruce/Johnston 1990 IAC; the anterior temporal lobe
as the hub for unique/person-specific semantics -- Patterson, Nestor & Rogers 2007). The online decision
"is this new mention the SAME person or a NEW one?" is hippocampal pattern COMPLETION (CA3 completes a
partial cue to a stored identity) vs SEPARATION (DG orthogonalises a genuinely new entity) -- Treves &
Rolls; Norman & O'Reilly CLS. At the discourse level this is the file-card update (Heim 1982; Kamp DRT):
a mention either UPDATES the matching card (completion) or OPENS a new one (separation).

  PINNED (the computation): content-addressable COMPLETE-or-SEPARATE onto a person node, with categorical
    identity-critical features (gender agreement; a conflicting GIVEN name) forcing SEPARATION -- the same
    role random projection plays in DG, but here the separating dimension is KNOWN (the identity feature),
    not random. Reuses the substrate's gn-agreement (PINNED) + the DG/CA3 completion currency
    (hdlab.dg_ca3_recollection_gate -- overlap = completion confidence).
  OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the FEATURE set that cues completion (full-name SPAN,
    given/surname structure, honorific/title, inferred gender) and the merge-vs-separate THRESHOLD.

WHAT THIS CELL PROVES. Three clustering arms on the SAME real-narrative population (LitBank 100 novels,
non-pronoun PER mentions, held-out), scored by B-cubed F + name-mention purity/inverse-purity + the
shatter/merge rates:
  FLOOR F0  head-token Jaccard  -- reproduces the LIVE branch (the shatter).
  FLOOR F1  full-span Jaccard   -- isolates the DATA (full spans) contribution alone.
  ORGAN     content-addressable complete-or-separate over structured person-node features (the MECHANISM).
  TWIN      the organ with per-mention name features SHUFFLED (info-free; must collapse).
The decomposition F0 -> F1 -> ORGAN separates the DATA fix from the MECHANISM fix -- the honesty the
"flat_store" refutation earned (measure what the DEFECT costs, not just that an alternative exists).

DATA. The head-token cache (data/litbank/who_did_what_events.json) is ENRICHED here: each mention is
aligned (sentence + head-token match, 100% hit, gold->chain consistency 0.9991) to its FULL SPAN from the
LitBank coref CoNLL and its entity TYPE from the LitBank entities BIO layer. The cache stream order, gold,
role and gov_verb are preserved verbatim, so the who-did-what population is untouched.

Run: .venv/Scripts/python.exe experiments/exp_name_entity_clustering_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_name_entity_clustering_v1.py --run [--docs N]
GLASS-BOX: pure symbolic + the substrate's sparse DG/CA3 currency; no torch, no external coref/LLM, no
network. Reads pre-parsed caches only (remote-safe; NO spaCy).
# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/lexicons/name_gender_gazetteer.tsv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.state_of_mind import MASC_CUES, FEM_CUES, infer_nominal_gender  # noqa: E402

CACHE = os.path.join(REPO_ROOT, "data", "litbank", "who_did_what_events.json")
CONLL_DIR = os.path.join(REPO_ROOT, "data", "litbank", "coref", "conll")
TSV_DIR = os.path.join(REPO_ROOT, "data", "litbank", "entities", "tsv")
GAZ = os.path.join(REPO_ROOT, "data", "lexicons", "name_gender_gazetteer.tsv")
SEED = 20260828

# 3rd-person + common pronoun surface forms as stored lowercased head_text in the cache (matches the
# downstream binder's PRONOUNS keys); these are NOT clustered by the name branch.
PRONOUNS = frozenset({
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves", "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "we", "us", "our", "ours", "ourselves", "that", "this",
    "who", "which", "whom", "whose",
})

# Honorific/title tokens (a subset of the substrate's gender cues that are TITLES, not gendered common
# nouns). A title carries gender but is NOT an identity token (many people share "Mr").
TITLES = frozenset({"mr", "mister", "mrs", "miss", "ms", "master", "sir", "lord", "lady", "dr",
                    "doctor", "madam", "madame", "mistress", "captain", "colonel", "major", "rev",
                    "reverend", "professor", "prof", "aunt", "uncle", "st", "saint"})

# Female-marking titles: the eldest-daughter naming convention ("Miss [Surname]" with no given name = the
# ELDEST unmarried daughter -- Mitchell, Daily Life in Victorian England 1996; verified 0/35 exceptions in
# P&P narration by the same-surname research drill) fires on these.
FEM_TITLES = frozenset({"miss", "mrs", "ms", "madam", "madame", "lady", "mistress"})

DETERMINERS = frozenset({"the", "a", "an", "this", "that", "these", "those", "my", "his", "her",
                         "its", "their", "our", "your"})
STOP = DETERMINERS | frozenset({"of", "and", "'s", "s"})


# ---------------------------------------------------------------------------
# FOUNDATION: general given-name -> gender gazetteer (anti-circular; NLTK names, not LitBank).
# ---------------------------------------------------------------------------
def load_given_gazetteer() -> Dict[str, str]:
    gaz: Dict[str, str] = {}
    with open(GAZ, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                gaz[parts[0].strip().lower()] = parts[1].strip()
    return gaz


# ---------------------------------------------------------------------------
# LOADER: reconstruct full-span mentions + entity type from the LitBank source, aligned to the cache.
# ---------------------------------------------------------------------------
def parse_conll(path: str) -> List[Tuple[int, int, int, int, List[str]]]:
    """Return coref mention spans: (chain_id, sent_idx, tok_start, tok_end, span_tokens)."""
    sents: List[List[str]] = []
    cur: List[str] = []
    coref_col: List[List[str]] = []
    cur_c: List[str] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            if not line.strip():
                if cur:
                    sents.append(cur); coref_col.append(cur_c); cur = []; cur_c = []
                continue
            parts = line.rstrip("\n").split("\t")
            cur.append(parts[3]); cur_c.append(parts[-1])
    if cur:
        sents.append(cur); coref_col.append(cur_c)
    spans: List[Tuple[int, int, int, int, List[str]]] = []
    for si, (sent, cc) in enumerate(zip(sents, coref_col)):
        open_stack: Dict[int, List[int]] = {}
        for ti, coref in enumerate(cc):
            if coref in ("_", "-", ""):
                continue
            for part in coref.split("|"):
                part = part.strip()
                m_both = re.match(r"^\((\d+)\)$", part)
                m_open = re.match(r"^\((\d+)$", part)
                m_close = re.match(r"^(\d+)\)$", part)
                if m_both:
                    cid = int(m_both.group(1)); spans.append((cid, si, ti, ti, [sent[ti]]))
                elif m_open:
                    open_stack.setdefault(int(m_open.group(1)), []).append(ti)
                elif m_close:
                    cid = int(m_close.group(1))
                    if open_stack.get(cid):
                        a = open_stack[cid].pop()
                        spans.append((cid, si, a, ti, [sent[k] for k in range(a, ti + 1)]))
    return spans


def load_tsv_bio(path: str) -> List[List[str]]:
    """Return per-sentence lists of entity BIO tags (aligned token-for-token to the CoNLL)."""
    sents: List[List[str]] = []; cur: List[str] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                if cur:
                    sents.append(cur); cur = []
                continue
            parts = line.rstrip("\n").split("\t")
            cur.append(parts[1] if len(parts) > 1 else "O")
    if cur:
        sents.append(cur)
    return sents


def _span_type(bio_sents: List[List[str]], si: int, a: int, b: int) -> str:
    """Majority entity type (PER/FAC/GPE/LOC/VEH/ORG/O) over a span's tokens."""
    if si >= len(bio_sents):
        return "O"
    tags = []
    for k in range(a, b + 1):
        if k < len(bio_sents[si]):
            t = bio_sents[si][k]
            tags.append(t.split("-", 1)[1] if "-" in t else "O")
    tags = [t for t in tags if t != "O"] or ["O"]
    return Counter(tags).most_common(1)[0][0]


def enrich_stream(cache_stream: List[dict], spans, bio_sents) -> List[dict]:
    """Attach full-span tokens + entity type to each cache mention by (sentence, head-token match,
    start proximity). 100% hit across the corpus (validated); leaves cache fields untouched."""
    by_sent: Dict[int, list] = {}
    for cid, si, a, b, toks in spans:
        by_sent.setdefault(si, []).append((cid, a, b, toks))
    out = []
    for m in cache_stream:
        s = m["sent"]; start = m["start"]; ht = m["head_text"].lower()
        best = None; bestd = 10 ** 9
        for cid, a, b, toks in by_sent.get(s, []):
            low = [t.lower().strip(".,'\"") for t in toks]
            if ht in low:
                d = abs(a - start)
                if d < bestd:
                    bestd = d; best = (cid, a, b, toks)
        r = dict(m)
        if best is not None:
            cid, a, b, toks = best
            r["span_tokens"] = toks
            r["ent_type"] = _span_type(bio_sents, s, a, b)
        else:
            r["span_tokens"] = [m["head_text"]]
            r["ent_type"] = "O"
        out.append(r)
    return out


def load_enriched(docs: Optional[int] = None) -> List[dict]:
    cache = json.load(open(CACHE, encoding="utf-8"))
    if docs:
        cache = cache[:docs]
    out = []
    for rec in cache:
        doc = rec["doc"]
        cpath = os.path.join(CONLL_DIR, doc + ".conll")
        tpath = os.path.join(TSV_DIR, doc + ".tsv")
        if not (os.path.exists(cpath) and os.path.exists(tpath)):
            continue
        spans = parse_conll(cpath)
        bio = load_tsv_bio(tpath)
        out.append({"doc": doc, "stream": enrich_stream(rec["stream"], spans, bio)})
    return out


# ---------------------------------------------------------------------------
# STRUCTURED NAME PARSING (the OUR-INVENTION feature cue -- swept).
# ---------------------------------------------------------------------------
def parse_name(span_tokens: List[str], gaz: Dict[str, str]) -> dict:
    """Parse a mention span into a structured person cue: {title, given, surname, gender, proper, toks}.
    proper=True iff the span carries >=1 capitalized proper-name token (not a title/determiner)."""
    raw = [t for t in span_tokens if t.strip()]
    lowered = [t.lower().strip(".,'\"") for t in raw]
    title = {t for t in lowered if t in TITLES}
    # proper-name tokens: Capitalized in source, not a title, not a determiner/stopword, alphabetic.
    proper = []
    for t_raw, t_low in zip(raw, lowered):
        if not t_low or t_low in TITLES or t_low in STOP:
            continue
        if t_raw[:1].isupper() and t_raw.isalpha():
            proper.append(t_low)
    given: Set[str] = set(); surname: Set[str] = set()
    if proper:
        # gazetteer-driven given/surname split; positional fallback (first=given, last=surname).
        gaz_given = [t for t in proper if t in gaz]
        if gaz_given:
            given.update(gaz_given)
            surname.update(t for t in proper if t not in gaz)
        elif len(proper) == 1:
            # a single UNKNOWN proper token is most likely a SURNAME (a title precedes a surname:
            # "Miss Bennet", "Mr Darcy"; a bare surname must NOT be read as a given name, else it
            # false-vetoes completion against the real given name -- the alias case this organ exists
            # to fix). It stays out of `given`, so it never triggers the given-conflict separation.
            surname.add(proper[0])
        else:
            given.add(proper[0]); surname.update(proper[1:])
    # gender: title/gendered-noun cue first (PINNED infer_nominal_gender), else given-name gazetteer.
    gender = infer_nominal_gender(raw)
    if gender is None:
        gv = {gaz[t] for t in proper if t in gaz}
        if len(gv) == 1:
            gender = "masc" if gv == {"masc"} else "fem"
    # soft-overlap bag = content tokens only (exclude determiners AND titles, so a shared "Mr"/"the"
    # does not create spurious completion currency between distinct people).
    all_toks = {t for t in lowered if t and t not in STOP and t not in TITLES}
    return {"title": title, "given": given, "surname": surname, "gender": gender,
            "proper": bool(proper), "toks": all_toks}


def _gender_conflict(g1: Optional[str], g2: Optional[str]) -> bool:
    return g1 is not None and g2 is not None and g1 != g2


# ---------------------------------------------------------------------------
# CLUSTERING ARMS.
# ---------------------------------------------------------------------------
# Grammatical-prominence weights for the ACT-R base-level salience tiebreak (Lewis & Vasishth 2005;
# reuses the SOLVED coref grammatical-prominence hierarchy). Cache roles: SUBJECT/OBJECT/OTHER/...
ROLE_W = {"SUBJECT": 4.0, "POSSESSIVE": 2.5, "OBJECT": 2.0, "OTHER": 1.0}


def _actr_base(hist: List[Tuple[int, str]], cur_sent: int, d: float) -> float:
    """ACT-R base-level activation B_i = ln(sum_k w_role(k) * dt_k^-d) over a node's prior mentions
    (dt = sentence distance, >=1). The discourse-salience score that breaks same-surname ambiguity
    toward the currently-active entity (Centering/ACT-R, PINNED)."""
    s = sum(ROLE_W.get(r, 1.0) * (max(cur_sent - sent, 0) + 1.0) ** (-d) for sent, r in hist)
    return math.log(s) if s > 0 else -1e9


def _tie_score(nd: dict, mode: str, cur_sent: int, d: float) -> float:
    """Candidate score for breaking a same-surname structural tie, by mechanism:
      recency   = ACT-R base-level activation (lever A; recency x role) -- TESTED NULL.
      prominence= global mention count so far (protagonist/most-prominent sibling default).
      subject   = most recent SUBJECT-role mention (Centering Cb / discourse-topic proxy).
      first     = earliest-introduced entity (19c 'Miss [Surname]' = eldest daughter proxy; higher=earlier).
    """
    if mode == "recency":
        return _actr_base(nd["hist"], cur_sent, d)
    if mode == "prominence":
        return float(nd["count"])
    if mode == "subject":
        subj = [sent for sent, role in nd["hist"] if role == "SUBJECT"]
        return float(max(subj)) if subj else -1.0
    if mode == "topic":
        # Centering Cb / topicality: accumulated grammatical-role prominence (SUBJECT weighted 4x), the
        # entity the discourse is currently ABOUT -- decorrelated from raw recency; recency breaks ties.
        w = sum(ROLE_W.get(r, 1.0) for _, r in nd["hist"])
        last = max((s for s, _ in nd["hist"]), default=-1)
        return w + last / 1e6
    if mode == "first":
        return -float(nd["created"])   # earliest created wins (eldest-daughter proxy)
    return 0.0


def _nonpron_idx(stream: List[dict]) -> List[int]:
    return [i for i, m in enumerate(stream) if m["head_text"].lower() not in PRONOUNS]


def cluster_head_jaccard(stream: List[dict]) -> List[int]:
    """FLOOR F0: the LIVE branch -- token-overlap over the single HEAD TOKEN per mention."""
    nodes: List[Set[str]] = []
    pred = [-1] * len(stream)
    for i in _nonpron_idx(stream):
        toks = {stream[i]["head_text"].lower()} - STOP - {""}
        best, bo = None, 0.0
        for j, nt in enumerate(nodes):
            if not nt or not toks:
                continue
            ov = len(toks & nt) / len(toks | nt)
            if ov > bo:
                bo, best = ov, j
        if best is not None and bo > 0.0:
            nodes[best] |= toks; pred[i] = best
        else:
            nodes.append(set(toks)); pred[i] = len(nodes) - 1
    return pred


def cluster_fullspan_jaccard(stream: List[dict]) -> List[int]:
    """FLOOR F1: same token-overlap MECHANISM, but over the FULL SPAN token bag (isolates the DATA fix)."""
    nodes: List[Set[str]] = []
    pred = [-1] * len(stream)
    for i in _nonpron_idx(stream):
        toks = {t.lower().strip(".,'\"") for t in stream[i]["span_tokens"]} - STOP - {""}
        best, bo = None, 0.0
        for j, nt in enumerate(nodes):
            if not nt or not toks:
                continue
            ov = len(toks & nt) / len(toks | nt)
            if ov > bo:
                bo, best = ov, j
        if best is not None and bo > 0.0:
            nodes[best] |= toks; pred[i] = best
        else:
            nodes.append(set(toks)); pred[i] = len(nodes) - 1
    return pred


def cluster_person_node(stream: List[dict], gaz: Dict[str, str],
                        theta: float = 0.5, w_given: float = 1.0, w_surname: float = 0.5,
                        w_tok: float = 0.4, d_decay: float = 0.5, salience_tiebreak: bool = False,
                        tiebreak_mode: Optional[str] = None, _tie_log: Optional[list] = None,
                        bridge_nominals: bool = True) -> List[int]:
    """ORGAN: content-addressable COMPLETE-or-SEPARATE onto a structured person node.

    For each non-pronoun mention: parse -> cue; among gn-compatible nodes rank candidates by a structured
    match TIER (shared given name > shared surname > soft token overlap). A CONFLICTING known given name
    VETOES completion (pattern separation of same-surname people). Best tier score >= theta -> COMPLETE
    (update node); else SEPARATE.

    salience_tiebreak (lever A, DEFAULT OFF -- a TESTED NULL): breaking same-surname ties by ACT-R
    base-level SALIENCE (recency x role) toward the active entity was the research drill's PRIORITY-1
    optimization. Evaluated on its OWN target subpopulation (PER entities with a same-surname same-gender
    sibling, `--surname-eval`): tiebreak ON 0.619 vs OFF 0.624 B-cubed F, NOT_SEP -- a HARD-FAIL by the
    drill's own criterion. Recency-based salience does NOT disambiguate same-surname siblings at LitBank
    scale; the brain uses the SITUATION MODEL (which sibling is the current discourse TOPIC), not recency --
    the same missing competence that caps nominal binding and pronoun-event binding. Kept as an off-by-
    default option so the negative is reproducible, not re-attempted blind."""
    mode = tiebreak_mode if tiebreak_mode is not None else ("recency" if salience_tiebreak else "off")
    nodes: List[dict] = []   # {given,surname,titles,gender,toks,count,created,hist:[(sent,role)]}
    pred = [-1] * len(stream)
    order = 0
    for i in _nonpron_idx(stream):
        m = stream[i]
        cur_sent = m["sent"]; role = m.get("role", "OTHER")
        f = parse_name(m["span_tokens"], gaz)
        cands = []   # (given_match, surname_match, score, j)
        for j, nd in enumerate(nodes):
            if _gender_conflict(f["gender"], nd["gender"]):
                continue
            given_match = bool(f["given"] & nd["given"])
            if f["given"] and nd["given"] and not given_match:
                continue   # SEPARATION: two known, DIFFERENT given names -> different people
            surname_match = bool(f["surname"] & nd["surname"])
            tok_ov = (len(f["toks"] & nd["toks"]) / len(f["toks"] | nd["toks"])
                      if (f["toks"] and nd["toks"]) else 0.0)
            if not (given_match or surname_match or tok_ov > 0):
                continue
            s = w_given * given_match + w_surname * surname_match + w_tok * tok_ov
            if given_match and surname_match:
                s += 0.5   # full-name agreement: very strong
            cands.append((given_match, surname_match, s, j))
        best, best_s = None, -1e9
        if cands:
            best_key = max((gm, sm) for gm, sm, s, j in cands)   # structural TIER
            tier = [(s, j) for gm, sm, s, j in cands if (gm, sm) == best_key]
            eff = None
            if mode != "off" and len(tier) > 1:
                # eldest-daughter convention: a BARE female-title surname mention ("Miss Bennet", no given)
                # denotes the eldest -> pick the earliest-introduced same-surname candidate. Modes
                # 'convention' (gate only) and 'combined' (gate, else topicality) fire it.
                conv_fires = (bool(f["title"] & FEM_TITLES) and not f["given"] and bool(f["surname"]))
                if mode in ("convention", "combined") and conv_fires:
                    eff = "first"
                elif mode == "combined":
                    eff = "topic"
                elif mode == "convention":
                    eff = None   # convention did not fire -> fall back to structural pick
                else:
                    eff = mode
            if eff is not None:
                j = max(tier, key=lambda t: _tie_score(nodes[t[1]], eff, cur_sent, d_decay))[1]
                best_s = max(s for s, jj in tier if jj == j)
                best = j
            else:
                best_s, best = max(tier)
            # DECISION-LEVEL LOG (gold used ONLY here, never in the clustering decision above): a genuine
            # ambiguous SURNAME-ONLY tie among >=2 candidates -> record whether the pick routed the mention
            # to the candidate node that really is its gold entity.
            if _tie_log is not None and best_key == (False, True) and len(tier) > 1:
                cand_js = [jj for _, jj in tier]
                cand_majgold = {jj: (nodes[jj]["golds"].most_common(1)[0][0]
                                     if nodes[jj].get("golds") else None) for jj in cand_js}
                mg = m["gold"]
                resolvable = mg in cand_majgold.values()
                correct = cand_majgold.get(best) == mg
                _tie_log.append({
                    "resolvable": resolvable, "correct": bool(correct), "n_cands": len(cand_js),
                    "form": " ".join(m["span_tokens"]), "gold": mg, "picked_gold": cand_majgold.get(best),
                    "cands": [{"gold": cand_majgold[jj], "surname": sorted(nodes[jj]["surname"])[:2],
                               "count": nodes[jj]["count"], "last_sent": nodes[jj]["hist"][-1][0],
                               "created": nodes[jj]["created"]} for jj in cand_js],
                    "cur_sent": cur_sent})
        # nominal (no proper token) with no scored match: gn-compatible unique bridging default
        if (best is None or best_s < theta) and not f["proper"] and bridge_nominals:
            compat = [j for j, nd in enumerate(nodes) if not _gender_conflict(f["gender"], nd["gender"])]
            if len(compat) == 1:
                best, best_s = compat[0], theta
        if best is not None and best_s >= theta:
            nd = nodes[best]
            nd["given"] |= f["given"]; nd["surname"] |= f["surname"]; nd["titles"] |= f["title"]
            nd["toks"] |= f["toks"]; nd["count"] += 1; nd["hist"].append((cur_sent, role))
            if nd["gender"] is None:
                nd["gender"] = f["gender"]
            if _tie_log is not None:
                nd.setdefault("golds", Counter())[m["gold"]] += 1
            pred[i] = best
        else:
            node = {"given": set(f["given"]), "surname": set(f["surname"]),
                    "titles": set(f["title"]), "gender": f["gender"],
                    "toks": set(f["toks"]), "count": 1, "created": order,
                    "hist": [(cur_sent, role)]}
            if _tie_log is not None:
                node["golds"] = Counter([m["gold"]])
            nodes.append(node)
            pred[i] = len(nodes) - 1
        order += 1
    return pred


def cluster_twin(stream: List[dict], gaz: Dict[str, str], rng: np.random.Generator, **kw) -> List[int]:
    """INFO-FREE TWIN: run the organ with each non-pronoun mention's SPAN shuffled to another mention's
    span (identity features destroyed, mention count/positions preserved). Must collapse."""
    idx = _nonpron_idx(stream)
    spans = [stream[i]["span_tokens"] for i in idx]
    perm = rng.permutation(len(spans))
    shuffled = [dict(m) for m in stream]
    for k, i in enumerate(idx):
        shuffled[i]["span_tokens"] = spans[perm[k]]
    return cluster_person_node(shuffled, gaz, **kw)


# ---------------------------------------------------------------------------
# METRICS.
# ---------------------------------------------------------------------------
def _bcubed(pred: List[int], gold: List[int]) -> Tuple[float, float, float]:
    """B-cubed precision/recall/F over the given aligned (pred, gold) label lists (already a subset)."""
    n = len(pred)
    if n == 0:
        return 0.0, 0.0, 0.0
    pred_c: Dict[int, list] = defaultdict(list); gold_c: Dict[int, list] = defaultdict(list)
    for i, (p, g) in enumerate(zip(pred, gold)):
        pred_c[p].append(i); gold_c[g].append(i)
    P = 0.0; R = 0.0
    for i, (p, g) in enumerate(zip(pred, gold)):
        pc = set(pred_c[p]); gc = set(gold_c[g]); inter = len(pc & gc)
        P += inter / len(pc); R += inter / len(gc)
    P /= n; R /= n
    F = 2 * P * R / (P + R) if (P + R) > 0 else 0.0
    return P, R, F


def _purity(pred: List[int], gold: List[int]) -> Tuple[float, float]:
    """name-mention purity (each predicted cluster's majority-gold fraction) + inverse purity."""
    n = len(pred)
    if n == 0:
        return 0.0, 0.0
    pred_c: Dict[int, Counter] = defaultdict(Counter); gold_c: Dict[int, Counter] = defaultdict(Counter)
    for p, g in zip(pred, gold):
        pred_c[p][g] += 1; gold_c[g][p] += 1
    pur = sum(c.most_common(1)[0][1] for c in pred_c.values()) / n
    inv = sum(c.most_common(1)[0][1] for c in gold_c.values()) / n
    return pur, inv


def _shatter_merge(pred: List[int], gold: List[int]) -> Tuple[float, float]:
    """shatter = frac of multi-mention gold entities split across >=2 predicted clusters; merge = frac
    of multi-mention predicted clusters covering >=2 gold entities."""
    gold_c: Dict[int, set] = defaultdict(set); pred_c: Dict[int, set] = defaultdict(set)
    gold_n: Counter = Counter(); pred_n: Counter = Counter()
    for p, g in zip(pred, gold):
        gold_c[g].add(p); pred_c[p].add(g); gold_n[g] += 1; pred_n[p] += 1
    multi_gold = [g for g in gold_c if gold_n[g] >= 2]
    multi_pred = [p for p in pred_c if pred_n[p] >= 2]
    shatter = (sum(1 for g in multi_gold if len(gold_c[g]) >= 2) / len(multi_gold)) if multi_gold else 0.0
    merge = (sum(1 for p in multi_pred if len(pred_c[p]) >= 2) / len(multi_pred)) if multi_pred else 0.0
    return shatter, merge


def per_type_subset(stream: List[dict], want_type: str = "PER", proper_only: bool = False,
                    gaz: Optional[Dict[str, str]] = None) -> List[int]:
    """Indices of non-pronoun mentions whose gold chain is majority `want_type`. proper_only keeps only
    mentions carrying a capitalized proper name (the alias-unification population)."""
    idx = _nonpron_idx(stream)
    # chain-level type = majority ent_type over the chain's non-pronoun mentions
    chain_types: Dict[int, Counter] = defaultdict(Counter)
    for i in idx:
        chain_types[stream[i]["gold"]][stream[i]["ent_type"]] += 1
    keep = []
    for i in idx:
        g = stream[i]["gold"]
        if chain_types[g].most_common(1)[0][0] != want_type:
            continue
        if proper_only:
            f = parse_name(stream[i]["span_tokens"], gaz or {})
            if not f["proper"]:
                continue
        keep.append(i)
    return keep


# ---------------------------------------------------------------------------
# EVAL HARNESS.
# ---------------------------------------------------------------------------
ARMS = ("F0_head", "F1_fullspan", "ORGAN", "TWIN")


def _doc_scores(stream, gaz, theta, seed, proper_only=False) -> Dict[str, dict]:
    preds = {
        "F0_head": cluster_head_jaccard(stream),
        "F1_fullspan": cluster_fullspan_jaccard(stream),
        "ORGAN": cluster_person_node(stream, gaz, theta=theta),
        "TWIN": cluster_twin(stream, gaz, np.random.default_rng(seed), theta=theta),
    }
    sub = per_type_subset(stream, "PER", proper_only=proper_only, gaz=gaz)
    gold = [stream[i]["gold"] for i in sub]
    out = {}
    for arm, pred in preds.items():
        p = [pred[i] for i in sub]
        P, R, F = _bcubed(p, gold)
        pur, inv = _purity(p, gold)
        sh, mg = _shatter_merge(p, gold)
        out[arm] = {"bc_p": P, "bc_r": R, "bc_f": F, "purity": pur, "inv_purity": inv,
                    "shatter": sh, "merge": mg, "n": len(sub)}
    return out


def cell(docs: Optional[int] = None, theta: float = 0.5, n_boot: int = 2000,
         proper_only: bool = False, seed: int = SEED) -> dict:
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    names = sorted(d["doc"] for d in data)
    dev = set(names[0::2]); test = set(names[1::2])
    by_doc = {d["doc"]: d["stream"] for d in data}

    def eval_set(doc_set, s0):
        rows = {arm: [] for arm in ARMS}     # per-doc metric dicts
        for di, name in enumerate(sorted(doc_set)):
            sc = _doc_scores(by_doc[name], gaz, theta, s0 + di, proper_only=proper_only)
            for arm in ARMS:
                rows[arm].append(sc[arm])
        return rows

    test_rows = eval_set(test, seed + 100)

    def agg(rows, key):
        return np.array([r[key] for r in rows], float)

    def ci_mean(vals, s):
        r = np.random.default_rng(s); n = len(vals); boots = []
        for _ in range(n_boot):
            boots.append(vals[r.integers(0, n, n)].mean())
        lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"mean": round(float(vals.mean()), 4), "lo": round(float(lo), 4),
                "hi": round(float(hi), 4), "hw": round(float(hi - lo) / 2, 4)}

    def paired(a, b, s):
        d = a - b; r = np.random.default_rng(s); n = len(d); boots = []
        for _ in range(n_boot):
            boots.append(d[r.integers(0, n, n)].mean())
        boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"delta": round(float(d.mean()), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                "hw": round(float(hi - lo) / 2, 4),
                "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    bc = {arm: ci_mean(agg(test_rows[arm], "bc_f"), seed + i) for i, arm in enumerate(ARMS)}
    metrics = {arm: {k: round(float(agg(test_rows[arm], k).mean()), 4)
                     for k in ("bc_p", "bc_r", "purity", "inv_purity", "shatter", "merge")}
               for arm in ARMS}
    n_test_mentions = int(agg(test_rows["ORGAN"], "n").sum())
    return {
        "anchor": "name_entity_clustering_v1",
        "population": f"LitBank non-pronoun PER mentions, held-out {len(test)} docs, proper_only={proper_only}",
        "theta": theta, "n_test_docs": len(test), "n_test_mentions": n_test_mentions,
        "bcubed_f": bc,
        "metrics": metrics,
        "ORGAN_vs_F0_head": paired(agg(test_rows["ORGAN"], "bc_f"), agg(test_rows["F0_head"], "bc_f"), seed + 50),
        "ORGAN_vs_F1_fullspan": paired(agg(test_rows["ORGAN"], "bc_f"), agg(test_rows["F1_fullspan"], "bc_f"), seed + 51),
        "F1_vs_F0 (data-only)": paired(agg(test_rows["F1_fullspan"], "bc_f"), agg(test_rows["F0_head"], "bc_f"), seed + 52),
        "ORGAN_vs_TWIN": paired(agg(test_rows["ORGAN"], "bc_f"), agg(test_rows["TWIN"], "bc_f"), seed + 53),
    }


def sweep_theta(docs: Optional[int] = None, seed: int = SEED) -> None:
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    names = sorted(d["doc"] for d in data)
    dev = sorted(names[0::2])
    by_doc = {d["doc"]: d["stream"] for d in data}
    print("=== THETA SWEEP on DEV (organ B-cubed F, mean over docs) ===")
    for theta in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2):
        fs = []
        for name in dev:
            sc = _doc_scores(by_doc[name], gaz, theta, seed, proper_only=False)
            fs.append(sc["ORGAN"]["bc_f"])
        print(f"  theta={theta:>4} -> organ B-cubed F {np.mean(fs):.4f}")


SIBLING_TIEBREAK_MODES = ("off", "recency", "prominence", "subject", "first",
                          "topic", "convention", "combined")


def same_surname_eval(docs: Optional[int] = None, theta: float = 0.4, n_boot: int = 2000,
                      seed: int = SEED) -> dict:
    """BRAIN-FOUNDATIONAL EVALUATION of same-surname sibling DISAMBIGUATION on its target population: PER
    entities with a SAME-SURNAME, SAME-GENDER SIBLING (a bare "Miss Bennet" is genuinely ambiguous; the IAC
    model predicts over-merge). Compares four buildable tiebreak MECHANISMS vs the no-tiebreak baseline,
    B-cubed F on the sibling subpopulation, paired-bootstrapped over the docs that HAVE siblings:
      recency    = ACT-R salience (lever A -- TESTED NULL).
      prominence = global mention count (protagonist/most-prominent sibling default).
      subject    = most-recent SUBJECT-role mention (Centering Cb / discourse-topic proxy).
      first      = earliest-introduced entity ('Miss [Surname]' = eldest-daughter convention proxy).
    The question: does ANY independent cue disambiguate same-surname siblings where recency cannot?"""
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    rows = {mode: [] for mode in SIBLING_TIEBREAK_MODES}
    stat_keys = SIBLING_TIEBREAK_MODES + ("twin",)   # twin = 'combined' on role-scrambled stream (info-free)
    tie_stats = {k: {"total": 0, "resolvable": 0, "correct": 0} for k in stat_keys}
    rng = np.random.default_rng(seed)
    sizes = []
    n_docs_with_siblings = 0
    for rec in data:
        stream = rec["stream"]
        sub = per_type_subset(stream, "PER", gaz=gaz)
        gold_sur: Dict[int, set] = defaultdict(set); gold_gen: Dict[int, Optional[str]] = {}
        for i in sub:
            f = parse_name(stream[i]["span_tokens"], gaz)
            gold_sur[stream[i]["gold"]] |= f["surname"]
            if stream[i]["gold"] not in gold_gen and f["gender"] is not None:
                gold_gen[stream[i]["gold"]] = f["gender"]
        golds = list(gold_sur)
        siblings = set()
        for a in golds:
            for b in golds:
                if a != b and (gold_sur[a] & gold_sur[b]) \
                        and gold_gen.get(a) is not None and gold_gen.get(a) == gold_gen.get(b):
                    siblings.add(a); siblings.add(b)
        sib_sub = [i for i in sub if stream[i]["gold"] in siblings]
        has_sib = len(sib_sub) >= 2
        if has_sib:
            n_docs_with_siblings += 1; sizes.append(len(sib_sub))
            gold = [stream[i]["gold"] for i in sib_sub]
        for mode in SIBLING_TIEBREAK_MODES:
            tlog: list = []
            pred = cluster_person_node(stream, gaz, theta=theta, tiebreak_mode=mode, _tie_log=tlog)
            for rd in tlog:
                tie_stats[mode]["total"] += 1
                if rd["resolvable"]:
                    tie_stats[mode]["resolvable"] += 1
                    tie_stats[mode]["correct"] += int(rd["correct"])
            if has_sib:
                rows[mode].append(_bcubed([pred[i] for i in sib_sub], gold)[2])
        # INFO-FREE TWIN: 'combined' on a stream whose clause-ROLES are scrambled (destroys the Cb/
        # topicality signal); the eldest-daughter convention is a knowledge rule not a free parameter, so
        # this isolates the topicality cue. A real topicality effect must beat this twin.
        scrambled = [dict(mm) for mm in stream]
        perm = rng.permutation(len(scrambled))
        roles = [mm["role"] for mm in scrambled]
        for k, mm in enumerate(scrambled):
            mm["role"] = roles[perm[k]]
        tlog = []
        cluster_person_node(scrambled, gaz, theta=theta, tiebreak_mode="combined", _tie_log=tlog)
        for rd in tlog:
            tie_stats["twin"]["total"] += 1
            if rd["resolvable"]:
                tie_stats["twin"]["resolvable"] += 1
                tie_stats["twin"]["correct"] += int(rd["correct"])
    if n_docs_with_siblings == 0:
        return {"anchor": "same_surname_disambiguation_eval", "n_docs_with_siblings": 0,
                "note": "NO docs have same-surname same-gender sibling entities"}
    arr = {mode: np.array(rows[mode]) for mode in SIBLING_TIEBREAK_MODES}
    off = arr["off"]

    def paired_vs_off(a, s):
        d = a - off; r = np.random.default_rng(s); n = len(d); boots = []
        for _ in range(n_boot):
            boots.append(d[r.integers(0, n, n)].mean())
        boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"delta_vs_off": round(float(d.mean()), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
                "hw": round(float(hi - lo) / 2, 4),
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    return {
        "anchor": "same_surname_disambiguation_eval",
        "population": "PER entities with a same-surname same-gender SIBLING",
        "n_docs_total": len(data), "n_docs_with_siblings": n_docs_with_siblings,
        "n_sibling_mentions": int(sum(sizes)),
        "bcubed_f": {mode: round(float(arr[mode].mean()), 4) for mode in SIBLING_TIEBREAK_MODES},
        "vs_off": {mode: paired_vs_off(arr[mode], seed + i)
                   for i, mode in enumerate(SIBLING_TIEBREAK_MODES) if mode != "off"},
        # DECISION-LEVEL (undiluted): accuracy on the actual ambiguous SURNAME-ONLY tie-decisions, among
        # those where the correct entity is one of the candidates (resolvable). chance ~= 1/n_cands.
        "tie_decisions": {mode: {
            "n_ties": tie_stats[mode]["total"], "n_resolvable": tie_stats[mode]["resolvable"],
            "decision_acc": round(tie_stats[mode]["correct"] / tie_stats[mode]["resolvable"], 4)
            if tie_stats[mode]["resolvable"] else None,
        } for mode in stat_keys},
    }


def dump_ties(docs: Optional[int] = None, theta: float = 0.4, mode: str = "off") -> None:
    """DATA DRILL: print the actual ambiguous same-surname tie-decisions so the negatives are concrete --
    what form, which candidate siblings (gold / last-mention-sentence / count / creation-order), the gold
    answer, and what `mode` picked. Reveals WHY recency (last_sent) picks wrong."""
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    n_shown = 0; n_res = 0; n_corr = 0; recency_would_be_right = 0
    print(f"=== ambiguous SAME-SURNAME tie-decisions (mode={mode}) ===")
    for rec in data:
        tlog: list = []
        cluster_person_node(rec["stream"], gaz, theta=theta, tiebreak_mode=mode, _tie_log=tlog)
        for rd in tlog:
            if not rd["resolvable"]:
                continue
            n_res += 1; n_corr += int(rd["correct"])
            # would picking the most-recent (max last_sent) candidate be right?
            rec_pick = max(rd["cands"], key=lambda c: c["last_sent"])
            recency_would_be_right += int(rec_pick["gold"] == rd["gold"])
            if n_shown < 30:
                n_shown += 1
                mark = "OK " if rd["correct"] else "XX "
                cs = "; ".join(f"g{c['gold']}(sur={c['surname']},last_s={c['last_sent']},"
                               f"n={c['count']},born={c['created']})" for c in rd["cands"])
                print(f"  {mark}{rec['doc'][:18]:18} '{rd['form'][:28]:28}' gold=g{rd['gold']} "
                      f"picked=g{rd['picked_gold']} | cands: {cs}")
    print(f"\n  resolvable ties={n_res}  mode-correct={n_corr} ({n_corr/max(n_res,1):.3f})  "
          f"most-recent-would-be-correct={recency_would_be_right} ({recency_would_be_right/max(n_res,1):.3f})")


def diagnose(docs: Optional[int] = None, theta: float = 0.4, seed: int = SEED) -> None:
    """Categorize the ORGAN's residual recall loss: for each PER gold split across >=2 organ clusters,
    classify the STRAGGLER mentions (those NOT in the gold's majority organ cluster) by form."""
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    names = sorted(d["doc"] for d in data)
    dev = sorted(names[0::2])
    by_doc = {d["doc"]: d["stream"] for d in data}
    cat = Counter(); examples = defaultdict(list)
    for name in dev:
        stream = by_doc[name]
        pred = cluster_person_node(stream, gaz, theta=theta)
        sub = per_type_subset(stream, "PER", gaz=gaz)
        # gold -> {organ_cluster: [mention idx]}
        gc: Dict[int, Dict[int, list]] = defaultdict(lambda: defaultdict(list))
        for i in sub:
            gc[stream[i]["gold"]][pred[i]].append(i)
        for g, clusters in gc.items():
            if len(clusters) < 2:
                continue
            maj = max(clusters, key=lambda c: len(clusters[c]))
            maj_forms = set()
            for i in clusters[maj]:
                maj_forms |= parse_name(stream[i]["span_tokens"], gaz)["given"]
                maj_forms |= parse_name(stream[i]["span_tokens"], gaz)["surname"]
            for c, idxs in clusters.items():
                if c == maj:
                    continue
                for i in idxs:
                    f = parse_name(stream[i]["span_tokens"], gaz)
                    form = " ".join(stream[i]["span_tokens"])
                    if not f["proper"]:
                        k = "nominal (no proper name)"
                    elif f["given"] and not (f["given"] & maj_forms):
                        k = "given-name not in majority (nickname/variant?)"
                    elif f["surname"] and not (f["surname"] & maj_forms):
                        k = "surname not in majority"
                    elif f["given"] or f["surname"]:
                        k = "shares a token but split anyway (ambiguous surname / scored-elsewhere)"
                    else:
                        k = "other"
                    cat[k] += 1
                    if len(examples[k]) < 8:
                        examples[k].append(f"{form!r} (maj_forms={sorted(maj_forms)[:4]})")
    tot = sum(cat.values())
    print(f"=== ORGAN residual straggler categories on DEV (theta={theta}); {tot} straggler mentions ===")
    for k, n in cat.most_common():
        print(f"  {n:>4} ({n/tot:.2f})  {k}")
        for ex in examples[k][:4]:
            print(f"          e.g. {ex}")


def self_test():
    """Fixture: the Bennet family + Darcy. F0 shatters (Elizabeth/Bennet split, all singletons); the
    organ COMPLETES Elizabeth<->Miss Elizabeth Bennet<->Lizzy-node via given name and SEPARATES Jane
    Bennet from Elizabeth Bennet by the conflicting given name, and separates Darcy by gender+surname."""
    gaz = {"elizabeth": "fem", "jane": "fem", "fitzwilliam": "masc"}
    stream = [
        {"head_text": "bennet", "span_tokens": ["Elizabeth", "Bennet"], "gold": 0, "sent": 0, "start": 0, "ent_type": "PER"},
        {"head_text": "elizabeth", "span_tokens": ["Elizabeth"], "gold": 0, "sent": 1, "start": 0, "ent_type": "PER"},
        {"head_text": "bennet", "span_tokens": ["Miss", "Bennet"], "gold": 0, "sent": 2, "start": 0, "ent_type": "PER"},
        {"head_text": "bennet", "span_tokens": ["Jane", "Bennet"], "gold": 1, "sent": 3, "start": 0, "ent_type": "PER"},
        {"head_text": "jane", "span_tokens": ["Jane"], "gold": 1, "sent": 4, "start": 0, "ent_type": "PER"},
        {"head_text": "darcy", "span_tokens": ["Mr", "Darcy"], "gold": 2, "sent": 5, "start": 0, "ent_type": "PER"},
        {"head_text": "he", "span_tokens": ["he"], "gold": 2, "sent": 6, "start": 0, "ent_type": "PER"},
    ]
    f0 = cluster_head_jaccard(stream)
    organ = cluster_person_node(stream, gaz, theta=0.5)
    sub = _nonpron_idx(stream)
    gold = [stream[i]["gold"] for i in sub]
    p0 = [f0[i] for i in sub]; po = [organ[i] for i in sub]
    _, _, f0f = _bcubed(p0, gold); _, _, orf = _bcubed(po, gold)
    # Elizabeth mentions (idx 0,1,2) must share ONE organ cluster; Jane (3,4) a DIFFERENT one.
    eliz = {organ[0], organ[1], organ[2]}
    jane = {organ[3], organ[4]}
    assert len(eliz) == 1, f"organ must UNIFY Elizabeth's 3 aliases, got clusters {eliz}"
    assert len(jane) == 1 and jane != eliz, f"organ must SEPARATE Jane from Elizabeth (same surname), got {jane} vs {eliz}"
    assert organ[5] not in eliz and organ[5] not in jane, "Darcy must separate from the Bennet sisters"
    # F0 shatters: Elizabeth's three surface forms land in >1 cluster
    assert len({f0[0], f0[1], f0[2]}) >= 2, "F0 head-token floor must SHATTER Elizabeth"
    assert orf > f0f, f"organ B-cubed F {orf:.3f} must beat the head-token floor {f0f:.3f}"
    print(f"SELF-TEST PASS: organ unifies Elizabeth (3->1), separates Jane & Darcy; "
          f"B-cubed F organ={orf:.3f} > floor={f0f:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--surname-eval", action="store_true", dest="surname_eval")
    ap.add_argument("--tie-dump", action="store_true", dest="tie_dump")
    ap.add_argument("--mode", type=str, default="off")
    ap.add_argument("--proper-only", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--theta", type=float, default=0.5)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.sweep:
        sweep_theta(docs=args.docs); return
    if args.diagnose:
        diagnose(docs=args.docs, theta=args.theta); return
    if args.surname_eval:
        print(json.dumps(same_surname_eval(docs=args.docs, theta=args.theta, n_boot=args.n_boot), indent=2)); return
    if args.tie_dump:
        dump_ties(docs=args.docs, theta=args.theta, mode=args.mode); return
    if args.run:
        print(json.dumps(cell(docs=args.docs, theta=args.theta, n_boot=args.n_boot,
                              proper_only=args.proper_only), indent=2))
        return
    print("use --self-test | --sweep | --run [--docs N --theta T --proper-only]")


if __name__ == "__main__":
    main()
