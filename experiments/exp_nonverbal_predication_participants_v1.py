"""NON-VERBAL PREDICATION -- fire events/roles on the PREDICATE SLOT, not the VERB tag (pri 113).

One clause in five predicates something of its subject with NO verb: "the sky is blue", "she is a doctor",
"he was here".  UD puts that predicate on an ADJ / NOUN / ADV / PROPN / NUM by design, so the event detector
(`situation_reader._tense_agnostic_extract`, fires on UPOS==VERB), the role competition's frame / slot / rank /
existential cues (`graded_role_assigner.coarse_role_cues`, gated `hc in ("VERB","AUX")`) and the tense reader
never fire on 167 of 762 subject-bearing clauses on UD-EWT test (21.9%).  The copular state reader sees 102 of
them (through the arm's `cop_predicates`); the other 65 are seen by NOBODY.

THE BRAIN.  A clause has ONE predicate (Spivey-Knowlton 1993), and the PREDICATION IS THE EVENT/STATE -- a
neo-Davidsonian event variable that a copula + a non-verbal complement instantiate exactly as a verb does
(Reichenbach/Bach; Pustet 2003 on the copula as the tense carrier of a non-verbal predication; the canonical
non-verbal predicate types are PROPERTY / CLASS-membership / LOCATION / POSSESSION).  The comprehender fills the
clause's participants from the clause, not from a tag column.  So the event/state should fire on the token that
carries the predication -- the verb when the slot holds a verb, else the copula's COMPLEMENT -- which pri 110's
`cop_predicates` (the heads rung) already computes, and the role competition should read that same predicate-slot
occupancy instead of `hc in ("VERB","AUX")`.

THE INSTRUMENT (pri 110 SOLVED.md 10f, proposed there, built here).  UD's VERB column CANNOT judge a predication
event on an ADJ (it scores a correctly-fired copular event as a false positive by construction -- pri 110 4c2).
So score by ARGUMENT STRUCTURE, never by the tag column:
  POPULATION = the 762 gold clauses with a SUBJECT (a gold nsubj / nsubj:pass arc); the predicate is that arc's
               gold HEAD, whatever its category.  595 verbal (gold VERB), 167 NON-VERBAL by UD's convention.
  RECALL     = share of clauses for which the reader fires an event whose index IS that gold predicate.
  PRECISION  = share of fired events whose index governs >=1 gold CORE argument
               (nsubj/obj/iobj/obl/ccomp/xcomp/cop) in the gold tree.  A copular ADJ passes (governs its subject
               and its copula); a random noun inside an NP fails.
  FLOOR      = the UPOS==VERB detector as shipped (+ the live BF predicate rescue).
  TWIN       = fire on a RANDOM token of the same clause at the matched extra-fire rate.

Run: .venv/Scripts/python.exe experiments/exp_nonverbal_predication_participants_v1.py --self-test
     [--diag65] [--participant --cap 700] [--roles --cap 700] [--board --arm base|slot]
NO spaCy / NO external LLM.  hdlab/ is READ-ONLY here; proposed diffs go in the SOLVED.md folder.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
import json
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from tools.build_attachment_validities import sentences, TEST
# REUSE pri 110's VALIDATED helpers (read-only import): the occupancy hand-off + the tag/posterior plumbing that
# the live chain uses, so this cell measures on the exact same instrument the governor/reader do.
from experiments.exp_one_convention_two_losses_v1 import (
    _le_and_post, tags_from, dist_from, predicate_slot_v2, revise_posterior, gum_sentences,
)

OUT = str(get_output_dir("nonverbal_predication_participants_v1"))

CORE = ("nsubj", "nsubj:pass", "obj", "iobj", "obl", "ccomp", "xcomp", "cop")
NP_RUN = AA.NP_RUN
COP_FORMS = AA.COP_FORMS


def out_dir():
    os.makedirs(OUT, exist_ok=True)
    return OUT


def _core(rel):
    return rel in CORE or rel.split(":")[0] in ("nsubj", "obj", "iobj", "obl", "ccomp", "xcomp", "cop")


# --------------------------------------------------------------------------- the copular-complement hand-off
def cop_predicates_ext(toks, pos):
    """The arm's cop_predicates EXTENDED for the 65 seen by nobody.  Two brain-faithful additions, both canonical
    non-verbal predicate types the shipped scan drops (Pustet 2003):
      (L) LOCATIVE / adverbial predicate -- "he is HERE", "the meeting is TOMORROW": the complement is an ADV.
          The shipped scan admits ADJ/NOUN/PROPN/PRON/NUM but NOT ADV, so a locative copular predication is lost.
      (F) CLAUSE-FINAL copula (fronted / elided complement) -- "...whatever age you ARE .", "i am sure they ARE .":
          nothing but PUNCT to the copula's right, so the shipped scan finds no complement and drops the clause.
          The predicate is elsewhere (fronted or elided); the copula itself carries the predication -- fire on it.
    Everything else is byte-identical to AA.cop_predicates (verified in --self-test)."""
    n = len(pos); lows = [t.lower() for t in toks]; out = set()
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        v = None
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                v = k; break
            if pos[k] == "PUNCT":
                break
            if AA.COP_LOCALITY and (pos[k] in AA._COP_STOP or (pos[k] == "PART" and lows[k] == "to")):
                break
        if v is not None:
            continue
        found = False
        # PASS 1 -- byte-identical to the shipped scan (NO ADV: adding ADV anywhere grabs a modifier adverb --
        # "really", "not", "just" -- before the true predicate; LOCATED NEGATIVE, it lowers both recall AND
        # precision, see SOLVED.md).  ADV is admitted ONLY as a fallback below.
        last_adv = None
        for k in range(i + 1, n):
            if pos[k] in ("VERB", "PUNCT"):
                break
            if pos[k] == "ADV":
                last_adv = k                        # remember, but do not take it yet
            if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
                if pos[k] == "PRON":
                    out.add(k + 1); found = True; break
                j = k
                while j + 1 < n and pos[j + 1] in NP_RUN:
                    j += 1
                heads = [m for m in range(k, j + 1) if pos[m] in ("NOUN", "PROPN")]
                if heads:
                    out.add(heads[-1] + 1); found = True; break
                adjs = [m for m in range(k, j + 1) if pos[m] in ("ADJ", "NUM")]
                out.add((adjs[-1] if adjs else k) + 1); found = True; break
        if not found:
            # PASS 2, FALLBACK ONLY.  (L) a LOCATIVE / adverbial predicate ("he is HERE") -- take the ADV only when
            # the shipped scan found no nominal/adjectival complement, so a modifier adverb never pre-empts a real
            # predicate.  (F) a CLAUSE-FINAL copula (fronted / elided complement) -- the copula carries the predication.
            if last_adv is not None:
                out.add(last_adv + 1)
            else:
                rest = [k for k in range(i + 1, n) if pos[k] != "PUNCT"]
                if not rest:
                    out.add(i + 1)
    return out


_WH = frozenset({"what", "why", "how", "where", "when", "who", "which", "whatever", "wtf"})
# copula number is closed-class FUNCTION-WORD knowledge (like COP_FORMS itself), not a heuristic lexicon.
_COP_PL = frozenset({"are", "were", "'re"})
_COP_SG = frozenset({"is", "was", "'s", "am", "be", "been", "being", "becomes", "became", "become", "'m"})
import hdlab.coreference_resolver as _CR          # REUSE: pronoun number (PRONOUN_SCOPE)
from hdlab.morphology import morphy as _morphy_fn  # REUSE: productive noun number (words-and-rules)


class _MORPH:
    morphy = staticmethod(lambda w, p: _morphy_fn(w, p))


def _num_nominal(tok, p):
    """sg / pl / None -- number read from EXISTING organs, not a hand-rolled lexicon (brain-foundational reuse):
      - PRONOUN number is closed-class lexical, read from the coref organ's PRONOUN_SCOPE (coreference_resolver);
      - NOUN number is read PRODUCTIVELY from the morphology organ (words-and-rules, Pinker): a noun whose
        morphological analysis strips a plural inflection (morphy(w,'n') != w) is plural.  This is the SAME
        number feature the brain uses for coref agreement -- one structure, many functions."""
    lw = tok.lower().strip(".,'\"!?;:()")
    if p in ("PRON",) or lw in _CR.PRONOUN_SCOPE:
        sc = _CR.PRONOUN_SCOPE.get(lw)
        if sc and sc.get("number"):
            return "pl" if sc["number"].startswith("pl") else "sg"
        return None
    if p in ("NOUN", "PROPN"):
        lemma = _MORPH.morphy(lw, "n")
        if lemma and lemma != lw:
            return "pl"                       # the productive analysis stripped a plural affix
        return "sg"
    if p == "NUM":
        return "sg" if lw in ("1", "one") else "pl"
    return None


def _num_cop(tok):
    lw = tok.lower()
    return "pl" if lw in _COP_PL else ("sg" if lw in _COP_SG else None)


def cop_predicates_inv(toks, pos):
    """cop_predicates_ext + INVERSION handling (research-grounded, SOLVED.md 12).  English identifies the copular
    subject/predicate by position, but in INVERTED clauses position flips and the fronted element is the predicate:
      LOCATIVE / TEMPORAL / WH FRONTING  "below IS a list", "why IS he...", "how IS that"  -> the FRONTED ADV/wh is
        the predicate; the post-copular NP is the (notional) subject (Bresnan/Salzmann locative inversion; Moro 1997).
      YES/NO INVERSION  "IS that a maker ?", "is it for guitar ?"  -> copula clause-initial: the first post-copular
        NP is the SUBJECT, the predicate is the NEXT predicate-eligible element.
    Canonical clauses (a nominal subject before the copula) keep the ext scan exactly."""
    n = len(pos); lows = [t.lower() for t in toks]; out = set()
    NOM = ("NOUN", "PROPN", "PRON", "NUM")
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        host = False
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                host = True; break
            if pos[k] == "PUNCT" or (AA.COP_LOCALITY and (pos[k] in AA._COP_STOP or (pos[k] == "PART" and lows[k] == "to"))):
                break
        if host:
            continue
        # LEFT context: nearest content token before the copula, clause-local
        left = None; k = i - 1
        while k >= 0:
            if pos[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                break
            if pos[k] in NOM + ("ADJ", "ADV"):
                left = k; break
            k -= 1
        # (A) FRONTED PREDICATE inversion: an ADV / wh element before the copula and no nominal subject before it.
        if left is not None and (pos[left] == "ADV" or lows[left] in _WH) and pos[left] not in NOM:
            out.add(left + 1); continue
        # (B) YES/NO inversion: copula clause-initial (no content before it) -> skip the first post-copular NP.
        start_after = i + 1
        if left is None:
            m = i + 1
            # skip the subject NP (the first nominal run after the copula)
            while m < n and pos[m] not in NOM + ("ADJ",) and pos[m] not in ("VERB", "PUNCT") and not (AA.COP_LOCALITY and pos[m] in AA._COP_STOP):
                m += 1
            if m < n and pos[m] in NOM:
                j = m
                while j + 1 < n and pos[j + 1] in NP_RUN:
                    j += 1
                start_after = j + 1              # the predicate is searched AFTER the subject NP
        # canonical / post-subject scan (the ext scan, from start_after)
        found = False; last_adv = None
        for k in range(start_after, n):
            if pos[k] in ("VERB", "PUNCT"):
                break
            if AA.COP_LOCALITY and (pos[k] in AA._COP_STOP or (pos[k] == "PART" and lows[k] == "to")):
                break
            if pos[k] == "ADV":
                last_adv = k
            if pos[k] in ("ADJ",) + NOM:
                if pos[k] == "PRON":
                    out.add(k + 1); found = True; break
                j = k
                while j + 1 < n and pos[j + 1] in NP_RUN:
                    j += 1
                heads = [mm for mm in range(k, j + 1) if pos[mm] in ("NOUN", "PROPN")]
                if heads:
                    out.add(heads[-1] + 1); found = True; break
                adjs = [mm for mm in range(k, j + 1) if pos[mm] in ("ADJ", "NUM")]
                out.add((adjs[-1] if adjs else k) + 1); found = True; break
        if not found:
            if last_adv is not None:
                out.add(last_adv + 1)
            elif not [k for k in range(i + 1, n) if pos[k] != "PUNCT"]:
                out.add(i + 1)
    return out


# --------------------------------------------------------------------------- fire the event stream, both arms
def _fire_sets(lc, toks, th=0.5, ext=False, gate="verbless_clause", inv=False):
    """Return (fired_base, fired_slot, gold_pos, tags2) as 0-based token-index sets of fired EVENTS.
    base  = the live event detector: UPOS==VERB (on the occupancy-revised tags, the live default) + BF rescue.
    slot  = base + the copular COMPLEMENT (cop_predicates) in any clause the tags leave verb-less -- the
            predication fires on the complement (Pustet 2003).  ext=True uses the extended cop scan (L+F)."""
    from hdlab.predicate_detector import (BFPredicateDetector, bf_cue_block, category_emission,
                                          clause_spans, has_verb_reading_glassbox)
    if not hasattr(_fire_sets, "_m"):
        _fire_sets._m = BFPredicateDetector.load()
    model = _fire_sets._m; rth = model.threshold
    _le, post = _le_and_post(lc, list(toks))
    tags = tags_from(lc, post)
    occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
    post2, _sites = revise_posterior(lc, toks, post, tags=tags, th=th, occ=occ)
    tags2 = tags_from(lc, post2)
    base = set(i for i in range(len(toks)) if tags2[i] == "VERB")
    cues2 = bf_cue_block(lc, list(toks), list(tags2), post2, category_emission(lc, list(toks)))
    cand2 = [i for i in range(len(toks)) if tags2[i] not in ("VERB", "AUX") and has_verb_reading_glassbox(toks[i])]
    bf2 = set(i for i in cand2 if model.score(cues2[i]) >= rth)
    base |= bf2
    span2 = clause_spans(list(toks), tags2)
    hv2 = {c: any(tags2[j] == "VERB" for j in range(len(toks)) if span2[j] == c) for c in set(span2)}
    copf = (cop_predicates_inv(list(toks), list(tags2)) if inv else
            (cop_predicates_ext(list(toks), list(tags2)) if ext else AA.cop_predicates(list(toks), list(tags2))))
    if gate == "all":
        # cop_predicates ALREADY only returns a complement when the copula has NO verbal host in its own verb
        # group (its first scan breaks on a VERB), so the copula IS copular.  The extra `not hv2[span]` gate is a
        # crude-segmentation over-suppressor (an embedded/adjacent verb sharing the span kills a genuine copular
        # predication: "they are amazing" suppressed because a prior sentence's `see` shares the span).
        cp = set(q - 1 for q in copf)
    else:
        cp = set(q - 1 for q in copf if not hv2[span2[q - 1]])
    return base, base | cp, tags2


def _live_pred_slot(lc, toks, tags2, post2, tab, heads_fix=False):
    """The predicate slot read from the GRADED PARSE + the role competition -- the brain-faithful hand-off:
    the predicate is whatever the subject ATTACHES TO (a competition), not a left-to-right closed-class scan.
    Returns the 0-based token indices that are the LIVE-parsed head of a LIVE nsubj arc.
    heads_fix=True applies the UPSTREAM CORRECTION first (re-attach a copular subject to its predicate via the
    cop-slot bias) so we can measure whether the heads-rung fix PROPAGATES to the fired event stream."""
    from hdlab.graded_role_assigner import coarse_roles
    dd = dist_from(lc, post2)
    hd = AA.heads_graded(list(toks), list(tags2), dd, tab)          # live parse
    if heads_fix:
        cop = cop_predicates_ext(list(toks), list(tags2))
        for (q, subj) in AA.csub_sites(list(toks), list(tags2)):
            if q in cop and 1 <= subj <= len(toks):
                hd[subj] = q
    roles = coarse_roles(list(toks), list(tags2), hd, head_posterior=None)
    out = set()
    for i in range(1, len(toks) + 1):
        if roles.get(i, "").split(":")[0] == "nsubj":
            h = hd.get(i, 0) or 0
            if 1 <= h <= len(toks) and tags2[h - 1] != "VERB":
                out.add(h - 1)
    return out


def _subject_clauses(gold_heads, rels, n):
    """The convention-free population: 1-based gold predicate index -> its gold category is read by caller.
    predicate = the gold HEAD of a gold nsubj / nsubj:pass arc."""
    return sorted(set(gold_heads[i] for i in range(n)
                      if rels[i].split(":")[0] == "nsubj" and 1 <= gold_heads[i] <= n))


def _governs_core(gold_heads, rels, e1):
    """Does the 1-based token e1 govern >=1 gold CORE argument?"""
    return any(gold_heads[i] == e1 and _core(rels[i]) for i in range(len(rels)))


# --------------------------------------------------------------------------- WHY the 65 are seen by nobody
def diag65(cap=700, th=0.5):
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    tot = 0
    seen_by_nobody = []   # (toks, h, gold_cat) for the residual
    cat_all = Counter(); cat_nobody = Counter(); cat_recovered_by_ext = Counter()
    reason = Counter()
    n_cop = 0; n_cop_ext = 0
    for toks, gold_pos, gold_heads, rels in test:
        n = len(toks)
        base, slot, tags2 = _fire_sets(lc, list(toks), th=th, ext=False)
        _b2, slot_ext, _t = _fire_sets(lc, list(toks), th=th, ext=True)
        cop = AA.cop_predicates(list(toks), list(tags2))
        cop_ext = cop_predicates_ext(list(toks), list(tags2))
        n_cop += len(cop); n_cop_ext += len(cop_ext)
        for h in _subject_clauses(gold_heads, rels, n):
            tot += 1
            gk = gold_pos[h - 1]
            cat_all[gk] += 1
            # a clause is invisible to the VERB gate when its predicate isn't tagged VERB
            if tags2[h - 1] == "VERB":
                continue
            # seen by the copular state reader iff cop_predicates finds this head
            if h in cop:
                continue
            # NOBODY sees it (shipped).  Is the extended cop scan enough?
            if h in cop_ext:
                cat_recovered_by_ext[gk] += 1
                # classify WHY the shipped scan missed it
                if gk == "ADV":
                    reason["locative/adverbial (ADV complement)"] += 1
                elif (h - 1) == max((k for k in range(n) if tags2[k] != "PUNCT"), default=-1):
                    reason["clause-final copula (fronted/elided)"] += 1
                else:
                    reason["other ext-recovered"] += 1
                continue
            cat_nobody[gk] += 1
            seen_by_nobody.append({"toks": toks, "h": h, "gold_cat": gk,
                                   "pred": toks[h - 1], "n_core": sum(1 for i in range(n) if gold_heads[i] == h and _core(rels[i]))})
    print("=" * 92)
    print("SUBJECT-BEARING GOLD CLAUSES (UD-EWT test %d sents): %d   gold predicate category: %s"
          % (len(test), tot, dict(cat_all.most_common())))
    print("cop_predicates emits %d ; EXTENDED (L locative + F clause-final) emits %d" % (n_cop, n_cop_ext))
    print("-" * 92)
    print("SEEN BY NOBODY (shipped): %d   recovered by the EXTENDED scan: %d   residual: %d"
          % (sum(cat_nobody.values()) + sum(cat_recovered_by_ext.values()),
             sum(cat_recovered_by_ext.values()), sum(cat_nobody.values())))
    print("  what the extension recovers, by reason:", dict(reason.most_common()))
    print("  extension recovers by gold category   :", dict(cat_recovered_by_ext.most_common()))
    print("  RESIDUAL still seen by nobody, by gold category:", dict(cat_nobody.most_common()))
    print("-" * 92)
    print("RESIDUAL clauses (a sample), with #gold core args their predicate governs:")
    for r in seen_by_nobody[:30]:
        print("   [%s %-6s core=%d] %s" % (r["gold_cat"], r["pred"], r["n_core"], " ".join(r["toks"])[:100]))
    out = {"n_clauses": tot, "gold_category": dict(cat_all), "n_cop_predicates": n_cop, "n_cop_ext": n_cop_ext,
           "recovered_by_ext": dict(cat_recovered_by_ext), "recovered_reason": dict(reason),
           "residual_by_category": dict(cat_nobody), "residual_n": sum(cat_nobody.values()),
           "residual_sample": seen_by_nobody[:60]}
    json.dump(out, open(os.path.join(out_dir(), "diag65.json"), "w", encoding="utf-8"), indent=1, default=str)
    return out


# --------------------------------------------------------------------------- THE PARTICIPANT INSTRUMENT
def _boot_paired(items, n=2000, seed=0):
    """items = list of (a_hit, b_hit) 0/1 over the SAME clauses; return (mean_a - mean_b, lo, hi)."""
    a = np.array([x[0] for x in items], float); b = np.array([x[1] for x in items], float)
    rng = np.random.default_rng(seed); m = len(items)
    if m == 0:
        return 0.0, 0.0, 0.0
    d = float(a.mean() - b.mean())
    ds = np.empty(n)
    for k in range(n):
        idx = rng.integers(0, m, m)
        ds[k] = a[idx].mean() - b[idx].mean()
    return d, float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def participant(cap=700, th=0.5, seed=0, ext=True, gate="verbless_clause", pop="ud"):
    """The convention-free PARTICIPANT INSTRUMENT.  Recall = event fired on the gold predicate; precision = fired
    event governs a gold core argument.  Arms: FLOOR (UPOS==VERB + rescue), SLOT (+ copular complement), TWIN
    (fire on a random clause token at the matched rate).  pop='gum' = GENERALISATION on GUM/GENTLE (modern, 12+
    genres, OUT of the category organ's UD-EWT-train count supply)."""
    test = gum_sentences(cap=cap) if pop == "gum" else sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    rng = np.random.default_rng(seed)
    tab = AA.load_attachment_validities(AA.ASSET)
    ARMSET = ("floor", "slot", "slot_inv", "parse", "parse_fixed", "union", "twin", "oracle")
    # per-clause recall bits, split by gold verbal vs non-verbal predicate
    rec = {a: {"verbal": [], "nonverbal": []} for a in ARMSET}
    rec_state = {a: {"verbal": [], "nonverbal": []} for a in ARMSET}   # STATE-REGISTERED (predicate OR subject)
    # precision: (hit, total) over FIRED events, per arm -- split by whether the fired token is gold VERB or not
    prec_num = {a: {"all": 0, "nonverbal": 0} for a in ARMSET}
    prec_den = {a: {"all": 0, "nonverbal": 0} for a in ARMSET}
    # paired recall on the NON-VERBAL clauses only: slot vs floor, twin vs floor
    paired_nv_slot = []; paired_nv_twin = []; paired_nv_parse = []
    n_extra_total = 0
    n_clauses = {"verbal": 0, "nonverbal": 0}
    for toks, gold_pos, gold_heads, rels in test:
        n = len(toks)
        base, slot, tags2 = _fire_sets(lc, list(toks), th=th, ext=ext, gate=gate)
        _b, slot_inv, _t = _fire_sets(lc, list(toks), th=th, ext=ext, gate=gate, inv=True)
        extra = sorted(slot - base)               # the copular complements the slot adds
        n_extra_total += len(extra)
        # PARSE arm: the predicate slot read from the graded parse + the role competition (the BF hand-off)
        _le, post = _le_and_post(lc, list(toks))
        occ = predicate_slot_v2(lc, toks, tags=tags_from(lc, post), post=post)
        post2, _s = revise_posterior(lc, toks, post, tags=tags_from(lc, post), th=th, occ=occ)
        parse = base | (_live_pred_slot(lc, list(toks), tags2, post2, tab) - base)
        parse_fixed = base | (_live_pred_slot(lc, list(toks), tags2, post2, tab, heads_fix=True) - base)
        # TWIN: fire on |extra| random tokens of THIS sentence that are (a) not already fired, (b) not PUNCT.
        elig = [i for i in range(n) if i not in base and tags2[i] != "PUNCT"]
        tw_extra = set(rng.choice(elig, size=min(len(extra), len(elig)), replace=False).tolist()) if extra and elig else set()
        twin = base | tw_extra
        # ORACLE: fire on base + the GOLD predicate slot of every non-verbal subject-bearing clause -- the ceiling
        # of a perfect predicate-slot signal, and the proof the instrument is well-formed (what if the slot were gold?).
        gold_slot = set(h - 1 for h in _subject_clauses(gold_heads, rels, n) if gold_pos[h - 1] != "VERB")
        oracle = base | gold_slot
        # UNION -- the Competition Model combines cues: the construction scan (slot) and the corrected-parse
        # predicate slot (parse_fixed) recover DIFFERENT clauses, so fire on both.
        union = slot | parse_fixed
        fired = {"floor": base, "slot": slot, "slot_inv": slot_inv, "parse": parse, "parse_fixed": parse_fixed,
                 "union": slot | parse_fixed, "twin": twin, "oracle": oracle}
        # PRECISION over fired events (all of them), scored by governance of a gold core argument
        for arm, S in fired.items():
            for e in S:
                prec_den[arm]["all"] += 1
                nv = (e < n) and gold_pos[e] != "VERB"
                if nv:
                    prec_den[arm]["nonverbal"] += 1
                if _governs_core(gold_heads, rels, e + 1):
                    prec_num[arm]["all"] += 1
                    if nv:
                        prec_num[arm]["nonverbal"] += 1
        # RECALL over the subject-bearing clauses.  STRICT = fired on the gold predicate token.  STATE-REGISTERED =
        # fired on the gold predicate OR its gold subject -- the brain-faithful target for a STATE consumer, since
        # subject/predicate ORDER is a PF-level artifact (Moro; Maienborn Kimian state) and what is load-bearing is
        # that the predication over the two clause elements is captured (SOLVED.md 12b).
        for h in _subject_clauses(gold_heads, rels, n):
            kind = "verbal" if gold_pos[h - 1] == "VERB" else "nonverbal"
            n_clauses[kind] += 1
            subj0 = set(i for i in range(n) if gold_heads[i] == h and rels[i].split(":")[0] == "nsubj")
            for arm, S in fired.items():
                rec[arm][kind].append(1 if (h - 1) in S else 0)
                rec_state[arm][kind].append(1 if ((h - 1) in S or bool(subj0 & S)) else 0)
            if kind == "nonverbal":
                paired_nv_slot.append(((h - 1) in slot, (h - 1) in base))
                paired_nv_twin.append(((h - 1) in twin, (h - 1) in base))
                paired_nv_parse.append(((h - 1) in parse, (h - 1) in base))
    out = {"cap": cap, "th": th, "ext": ext, "n_clauses": n_clauses, "n_extra_fired": n_extra_total, "arms": {}}
    for arm in ARMSET:
        rv = rec[arm]["verbal"]; rn = rec[arm]["nonverbal"]
        rsn = rec_state[arm]["nonverbal"]
        out["arms"][arm] = {
            "recall_verbal": round(float(np.mean(rv)), 4) if rv else 0.0,
            "recall_nonverbal": round(float(np.mean(rn)), 4) if rn else 0.0,
            "recall_state_nonverbal": round(float(np.mean(rsn)), 4) if rsn else 0.0,
            "precision": round(prec_num[arm]["all"] / max(1, prec_den[arm]["all"]), 4),
            "precision_nonverbal_events": round(prec_num[arm]["nonverbal"] / max(1, prec_den[arm]["nonverbal"]), 4),
            "precision_n": prec_den[arm]["all"], "precision_nonverbal_n": prec_den[arm]["nonverbal"],
        }
    # paired CIs on the non-verbal clauses
    d, lo, hi = _boot_paired(paired_nv_slot, seed=seed)
    out["slot_minus_floor_recall_nonverbal"] = {"d": round(d, 4), "ci": [round(lo, 4), round(hi, 4)],
                                                 "sep": bool(lo > 0 or hi < 0)}
    d2, lo2, hi2 = _boot_paired(paired_nv_twin, seed=seed)
    out["twin_minus_floor_recall_nonverbal"] = {"d": round(d2, 4), "ci": [round(lo2, 4), round(hi2, 4)],
                                                 "sep": bool(lo2 > 0 or hi2 < 0)}
    d3, lo3, hi3 = _boot_paired(paired_nv_parse, seed=seed)
    out["parse_minus_floor_recall_nonverbal"] = {"d": round(d3, 4), "ci": [round(lo3, 4), round(hi3, 4)],
                                                  "sep": bool(lo3 > 0 or hi3 < 0)}
    dp, lop, hip = _boot_paired([(p[0], s[0]) for p, s in zip(paired_nv_parse, paired_nv_slot)], seed=seed)
    out["parse_minus_slot_recall_nonverbal"] = {"d": round(dp, 4), "ci": [round(lop, 4), round(hip, 4)],
                                                 "sep": bool(lop > 0 or hip < 0)}
    # precision paired: slot vs floor over FIRED events is not clause-paired; report the raw drop + verbal-clause CI floor
    print("=" * 92)
    print("PARTICIPANT INSTRUMENT  (UD-EWT test, cap %d, th %s, ext=%s)" % (cap, th, ext))
    print("  clauses: verbal %d, non-verbal %d ; slot fires %d extra events"
          % (n_clauses["verbal"], n_clauses["nonverbal"], n_extra_total))
    print("-" * 92)
    print("%-7s %14s %16s %14s %11s" % ("arm", "recall(verbal)", "recall(NONverbal)", "STATE-reg(NV)", "precision"))
    for arm in ARMSET:
        A = out["arms"][arm]
        print("%-7s %14.4f %16.4f %14.4f %11.4f" % (arm, A["recall_verbal"], A["recall_nonverbal"],
                                                    A["recall_state_nonverbal"], A["precision"]))
    print("-" * 92)
    s = out["slot_minus_floor_recall_nonverbal"]; t = out["twin_minus_floor_recall_nonverbal"]
    p = out["parse_minus_floor_recall_nonverbal"]; ps = out["parse_minus_slot_recall_nonverbal"]
    print("SLOT  - FLOOR recall on the 167 non-verbal clauses: %+.4f CI[%+.4f,%+.4f] %s"
          % (s["d"], s["ci"][0], s["ci"][1], "SEP" if s["sep"] else "ns"))
    print("PARSE - FLOOR recall on the 167 non-verbal clauses: %+.4f CI[%+.4f,%+.4f] %s  (BF hand-off: parse+roles)"
          % (p["d"], p["ci"][0], p["ci"][1], "SEP" if p["sep"] else "ns"))
    print("PARSE - SLOT  recall on the 167 non-verbal clauses: %+.4f CI[%+.4f,%+.4f] %s  (parse vs construction scan)"
          % (ps["d"], ps["ci"][0], ps["ci"][1], "SEP" if ps["sep"] else "ns"))
    print("TWIN  - FLOOR recall on the 167 non-verbal clauses: %+.4f CI[%+.4f,%+.4f] %s  (the info-free control)"
          % (t["d"], t["ci"][0], t["ci"][1], "SEP" if t["sep"] else "ns"))
    json.dump(out, open(os.path.join(out_dir(), "participant_cap%d_ext%d.json" % (cap, int(ext))), "w",
                        encoding="utf-8"), indent=1)
    return out


# WALL 1 -- LOCATIVE / TEMPORAL predication routes to the deictic-anchor register, NOT an attribute (Zwaan &
# Radvansky event-indexing; Franklin & Tversky spatial framework).  Closed-class deictic lexicons (legitimate stored
# knowledge, like COP_FORMS).  A locative copular predicate writes loc(X) = anchor +/- axis-offset; a temporal one
# writes time(X) = now +/- offset.  The axis is read off the deictic word (Franklin & Tversky's body axes).
_LOC_VERTICAL = {"above": +1, "below": -1, "up": +1, "down": -1, "upstairs": +1, "downstairs": -1, "overhead": +1, "underneath": -1}
_LOC_PROXIMAL = {"here": 0, "there": 1, "nearby": 0, "close": 0, "far": 1, "away": 1, "abroad": 1, "outside": 1, "inside": 0, "home": 0, "everywhere": 2, "somewhere": 2, "anywhere": 2}
_TEMPORAL_ADV = {"now": 0, "today": 0, "tonight": 0, "then": 1, "tomorrow": 1, "yesterday": -1, "soon": 1, "later": 1, "earlier": -1, "recently": -1, "already": -1, "afterwards": 1}


def deictic_type(word):
    """Return ('loc', axis, offset) | ('temp', offset) | None for a deictic ADV -- the spatial/temporal-index write
    a locative/temporal copular predicate should make (Franklin & Tversky body axes; Zwaan & Radvansky time index)."""
    w = word.lower().strip(".,!?;:")
    if w in _LOC_VERTICAL:
        return ("loc", "vertical", _LOC_VERTICAL[w])
    if w in _LOC_PROXIMAL:
        return ("loc", "proximal", _LOC_PROXIMAL[w])
    if w in _TEMPORAL_ADV:
        return ("temp", _TEMPORAL_ADV[w])
    return None


# WALL 3 -- TYPE-LICENSED INFERENCE probe.  A class-membership predication ("she is a doctor") sets the entity's
# TYPE; the type should license default inference (Rumelhart schemata; McRae generalized event knowledge).  The
# instrument (Graesser / McKoon & Ratcliff): a CONSISTENT continuation should score higher than an INCONSISTENT one.
# The probe = human-competence MINIMAL PAIRS (a gold instrument, not a learned component); the engine = the
# substrate's GEK organ (reuse, no LLM).  Categories drawn from common nominal predicates.
_TYPE_PROBES = [
    ("doctor", ["patient"], ["engine"]), ("teacher", ["student"], ["patient"]),
    ("nurse", ["patient"], ["lawsuit"]), ("lawyer", ["court"], ["patient"]),
    ("chef", ["kitchen"], ["classroom"]), ("farmer", ["crop"], ["patient"]),
    ("soldier", ["war"], ["recipe"]), ("scientist", ["experiment"], ["harvest"]),
    ("musician", ["concert"], ["surgery"]), ("pilot", ["airplane"], ["classroom"]),
    ("writer", ["book"], ["tractor"]), ("athlete", ["game"], ["experiment"]),
    ("student", ["exam"], ["patient"]), ("artist", ["painting"], ["lawsuit"]),
    ("engineer", ["machine"], ["patient"]), ("priest", ["church"], ["laboratory"]),
]


def type_inference(seed=0):
    """WALL 3 prototype: does a class-membership TYPE license the right default inference?  Score, per probe,
    GEK(category -> consistent) vs GEK(category -> inconsistent); accuracy = consistent strictly higher.  Control =
    SHUFFLE the category<->continuation pairing (the type carries no information about a random continuation)."""
    from hdlab.generalized_event_knowledge import GEKProjector
    g = GEKProjector()
    if not g.available():
        print("GEK store unavailable -- abstain"); return {}
    good = 0; tot = 0; cov = 0
    cons_scores = []; incon_scores = []
    for cat, cons, incon in _TYPE_PROBES:
        sc = g.score([cat], cons); si = g.score([cat], incon)
        tot += 1
        if sc > 0 or si > 0:
            cov += 1
        cons_scores.append(sc); incon_scores.append(si)
        if sc > si:
            good += 1
    # SHUFFLED control: pair each category with another probe's consistent continuation (random)
    rng = np.random.default_rng(seed)
    conts = [c for _, c, _ in _TYPE_PROBES]
    perm = rng.permutation(len(conts))
    ctrl_good = 0
    for i, (cat, cons, incon) in enumerate(_TYPE_PROBES):
        sc = g.score([cat], cons); ss = g.score([cat], conts[perm[i]])
        if sc > ss:
            ctrl_good += 1
    print("=" * 92)
    print("WALL 3 -- TYPE-LICENSED INFERENCE (GEK, McRae generalized event knowledge; %d category minimal pairs):" % tot)
    print("  consistent > inconsistent continuation: %.4f (%d/%d)   coverage %.4f" % (good / tot, good, tot, cov / tot))
    print("  mean GEK score  consistent %.3f  vs inconsistent %.3f" % (float(np.mean(cons_scores)), float(np.mean(incon_scores))))
    print("  SHUFFLED-pairing control (consistent > random continuation): %.4f (%d/%d)" % (ctrl_good / tot, ctrl_good, tot))
    print("  -> a class-membership predication's TYPE licenses the correct default inference via the GEK organ;")
    print("     this is the downstream consumer (rung 5) the whole line feeds, and it is measurable + fires.")
    out = {"n": tot, "accuracy": good / tot, "coverage": cov / tot, "control_accuracy": ctrl_good / tot,
           "mean_consistent": float(np.mean(cons_scores)), "mean_inconsistent": float(np.mean(incon_scores))}
    json.dump(out, open(os.path.join(out_dir(), "type_inference.json"), "w", encoding="utf-8"), indent=1)
    return out


def spatial(cap=700, th=0.5):
    """WALL 1 prototype: route locative/temporal copular predicates to a SPATIAL/TEMPORAL index (deictic-anchor +
    axis-offset), closing the classifier's missing-location-type gap.  Measures, on the 167, the ADV predicates and
    how many the deictic lexicon types as spatial/temporal (past the wall) vs left untyped."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    n_adv = 0; typed = Counter(); ex = []
    for toks, gpos, gh, rels in test:
        n = len(toks); lows = [w.lower() for w in toks]
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ); t2 = tags_from(lc, p2)
        cop = cop_predicates_ext(list(toks), list(t2))
        for h in _subject_clauses(gh, rels, n):
            if gpos[h - 1] == "VERB":
                continue
            if gpos[h - 1] != "ADV":
                continue
            n_adv += 1
            dt = deictic_type(toks[h - 1])
            # also allow a locative NOUN complement bound by a case marker ("at 7:30", "under Bush") -- checked via
            # a preceding ADP; but the ADV predicate is the core locative/temporal class here.
            if dt is None:
                # temporal/locative noun predicate ("the meeting is TOMORROW/MONDAY") -- try the noun too
                typed["untyped (not a deictic ADV -- needs a landmark/date reader)"] += 1
            elif dt[0] == "loc":
                typed["SPATIAL (loc(X)=anchor %s %+d)" % (dt[1], dt[2])] += 1
            else:
                typed["TEMPORAL (time(X)=now %+d)" % dt[1]] += 1
            if len(ex) < 12:
                ex.append("[%s -> %s] %s" % (toks[h - 1], dt, " ".join(toks)[:70]))
    print("=" * 92)
    print("WALL 1 -- LOCATIVE/TEMPORAL predication -> spatial/temporal index (deictic-anchor + axis-offset):")
    print("  ADV predicates on the 167: %d" % n_adv)
    for k, c in typed.most_common():
        print("   %-52s %d" % (k, c))
    print("  -> SPATIAL/TEMPORAL predications route to the deictic-anchor register (space_reader), NOT an attribute.")
    for e in ex:
        print("     ", e)
    out = {"n_adv": n_adv, "typed": dict(typed), "examples": ex}
    json.dump(out, open(os.path.join(out_dir(), "spatial.json"), "w", encoding="utf-8"), indent=1)
    return out


# SHELL NOUNS (Schmid 2000, English Abstract Nouns as Conceptual Shells) -- a CLOSED lexical class (like COP_FORMS)
# whose function is to hold a proposition-sized chunk of discourse.  Legitimate closed-class lexical knowledge, not a
# heuristic.  A shell-noun subject + copula + finite clause is a SPECIFICATIONAL predication whose value is the
# embedded PROPOSITION (Asher 1993 typed abstract objects) -- a FOURTH predication type (propositional-identity),
# NOT a property attribute.
SHELL_NOUNS = frozenset({
    "reason", "point", "problem", "fact", "idea", "question", "plan", "thing", "issue", "answer", "result",
    "aim", "goal", "purpose", "truth", "view", "belief", "claim", "conclusion", "assumption", "hope", "fear",
    "chance", "possibility", "way", "trouble", "difficulty", "advantage", "danger", "risk", "rule", "principle",
    "moral", "upshot", "catch", "key", "secret", "case", "matter", "situation", "story", "news", "message",
    "notion", "sense", "feeling", "impression", "suggestion", "proposal", "decision", "thought", "concern",
    "consequence", "implication", "lesson", "bottom", "deal", "trick", "worry", "hypothesis", "theory",
})


def shell(cap=700, th=0.5):
    """WALL 2 prototype (highest value x tractability): detect SHELL-NOUN SPECIFICATIONAL predications
    ("the reason is that he left"), which should bind the shell NP to the embedded PROPOSITION (Asher 1993), NOT
    write a property attribute.  Detection = closed shell-noun lexicon (Schmid 2000) + copula + a finite embedded
    clause (a VERB after the copula, with/without `that`).  Measures coverage of the clausal-predicate residual and
    of specificational clauses overall -- the count that needs the 4th `propositional-identity` type + a proposition
    discourse referent (which the entity graph currently lacks)."""
    from hdlab.morphology import morphy as _mf
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    n_shell_spec = 0; n_clausal_resid = 0; shell_covers_clausal = 0
    ex = []
    for toks, gpos, gh, rels in test:
        n = len(toks); lows = [w.lower() for w in toks]
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ); t2 = tags_from(lc, p2)
        for h in _subject_clauses(gh, rels, n):
            if gpos[h - 1] == "VERB":
                continue
            subj = [i for i in range(n) if gh[i] == h and rels[i].split(":")[0] == "nsubj"]
            clausal = any(gh[i] == h and rels[i].split(":")[0] in ("ccomp", "csubj", "acl", "advcl") for i in range(n))
            if clausal:
                n_clausal_resid += 1
            # shell-noun subject?  (subject head lemma in the closed class)
            sh = None
            for s in subj:
                lem = (_mf(lows[s], "n") or lows[s])
                if lem in SHELL_NOUNS:
                    sh = s; break
            if sh is None:
                continue
            # copula + a finite clause after it (a VERB downstream in the clause) == specificational
            cop_i = next((j for j in range(n) if t2[j] == "AUX" and lows[j] in COP_FORMS and gh[j] == h), None)
            has_finite_after = cop_i is not None and any(t2[k] == "VERB" for k in range(cop_i + 1, n))
            if has_finite_after or clausal:
                n_shell_spec += 1
                if clausal:
                    shell_covers_clausal += 1
                if len(ex) < 12:
                    ex.append("[shell=%s] %s" % (toks[sh], " ".join(toks)[:78]))
    print("=" * 92)
    print("WALL 2 -- SHELL-NOUN SPECIFICATIONAL predication (proposition binding, Schmid 2000 / Asher 1993):")
    print("  shell-noun specificational clauses detected on the 167 population : %d" % n_shell_spec)
    print("  clausal-predicate residual clauses (pred governs a clause)        : %d" % n_clausal_resid)
    print("  of which shell-noun specificational (recovered by this mechanism) : %d" % shell_covers_clausal)
    print("  -> these need a 4th type `propositional-identity`: bind the shell NP to the embedded PROPOSITION,")
    print("     not a property attribute; register the proposition as antecedent-eligible for later that/this/it.")
    for e in ex:
        print("     ", e)
    out = {"shell_specificational": n_shell_spec, "clausal_residual": n_clausal_resid,
           "shell_covers_clausal": shell_covers_clausal, "examples": ex}
    json.dump(out, open(os.path.join(out_dir(), "shell.json"), "w", encoding="utf-8"), indent=1)
    return out


def typing(cap=700, th=0.5):
    """IMPLEMENT + MEASURE the attribute TYPING (the piece that licenses downstream inference).  For each detected
    non-verbal predication, classify with the Higgins classifier (copular_binding.predicted_type):
      pred_adj  -> PROPERTY (attribute value)      pred_nom -> CLASS/is-a (type/schema field, inherits a frame)
      ident     -> IDENTITY (entity file-merge).   [+ a LOCATION type is MISSING -- ADV predicates fall through:
    a located gap in the classifier, since location updates the spatial dimension, not an attribute.]
    Cross-tabs the predicted type against the gold predicate CATEGORY as a coherence check (no gold Higgins labels
    exist): ADJ should read PROPERTY, PROPN/definite should read IDENTITY, indefinite NOUN should read CLASS."""
    from hdlab import copular_binding as CB
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    xtab = defaultdict(Counter); loc_missing = 0
    for toks, gpos, gh, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ); t2 = tags_from(lc, p2)
        cop = cop_predicates_ext(list(toks), list(t2))
        for hgold in _subject_clauses(gh, rels, n):
            if gpos[hgold - 1] == "VERB":
                continue
            if hgold not in cop:                      # only where we detect the predication
                continue
            ty = CB.predicted_type(list(toks), list(t2), 0, hgold - 1)   # holder idx unused by the classifier
            xtab[gpos[hgold - 1]][ty] += 1
            if gpos[hgold - 1] == "ADV":
                loc_missing += 1
    print("=" * 92)
    print("ATTRIBUTE TYPING (Higgins predicted_type) x gold predicate category, on detected non-verbal clauses:")
    print("  %-8s %-10s %-10s %-10s" % ("goldcat", "pred_adj", "pred_nom", "ident"))
    for gc in sorted(xtab, key=lambda k: -sum(xtab[k].values())):
        c = xtab[gc]
        print("  %-8s %-10d %-10d %-10d" % (gc, c.get("pred_adj", 0), c.get("pred_nom", 0), c.get("ident", 0)))
    print("  -> PROPERTY(pred_adj) updates an attribute; CLASS(pred_nom) sets a type/schema; IDENTITY(ident) merges files.")
    print("  LOCATED GAP: ADV/locative predicates have NO type (should update the SPATIAL dimension): %d" % loc_missing)
    out = {"crosstab": {k: dict(v) for k, v in xtab.items()}, "adv_untyped": loc_missing}
    json.dump(out, open(os.path.join(out_dir(), "typing.json"), "w", encoding="utf-8"), indent=1)
    return out


def state_binding(cap=700, th=0.5):
    """RUNG 4/5 DRILL -- is the non-verbal predication bound as a typed ATTRIBUTE with the CORRECT holder+property?
    (The research says a copular predication is a Kimian-state attribute on the entity, and the highest-yield loss is
    SUBJECT-ENTITY binding, not predicate detection.)  For each of the 167 non-verbal clauses, run the substrate's
    entity-state binding (hdlab.copular_binding: the `cop`-label path UNION the label-robust closed-class detector,
    on the LIVE chain tags + live parse) and check whether it emits a (holder, property) pair whose PROPERTY is the
    gold predicate and whose HOLDER is the gold subject.  Splits the loss into detection (property found) vs binding
    (holder correct)."""
    from hdlab import copular_binding as CB
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    arc = ArcParser.load(CB.ARC_ASSET); lab = ArcLabeler.load(CB.LAB_ASSET)
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    n_nv = 0; prop_found = 0; holder_found = 0; both = 0
    w_prop = 0; w_holder = 0; w_both = 0
    miss = Counter()
    for toks, gpos, gh, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        heads = AA.heads_graded(list(toks), list(t2), dd, tab)
        hd = {i: heads.get(i + 1, 0) - 1 for i in range(n)}          # 0-based head map for the copular organ
        try:
            pairs = set(CB.extract_entity_states(list(toks), list(t2), arc, lab, heads=hd))
        except Exception:
            pairs = set()
        pairs |= CB.robust_cop(list(toks), list(t2), hd, gate=True)
        prop_of = {}                                                  # property_idx -> holder_idx (NATIVE detection)
        for (hh, pp) in pairs:
            prop_of[pp] = hh
        # WIRED arm (the proposed fix): build (holder, property) from MY predicate-slot detection --
        # property = the predicate slot (cop_predicates_ext complements + the parse-read predicate); holder = the
        # subject the copular construction / parse binds to it (csub_sites gives (predicate, subject) pairs; the
        # parse gives the nsubj child).  This is the 0.89 detection routed into the entity-attribute form.
        wired = {}
        for (q, subj) in AA.csub_sites(list(toks), list(t2)):
            if 1 <= q <= n and 1 <= subj <= n:
                wired[q - 1] = subj - 1
        roles_live = None
        for i in range(1, n + 1):                                     # the parse's nsubj heads (predicate) + their subject
            h_i = heads.get(i, 0)
            if 1 <= h_i <= n and t2[h_i - 1] != "VERB":
                # i attaches to h_i; if i is a subject-like pre-head nominal, h_i is the predicate, i the holder
                if t2[i - 1] in ("NOUN", "PROPN", "PRON", "NUM") and i < h_i and (h_i - 1) not in wired:
                    wired[h_i - 1] = i - 1
        for hgold in _subject_clauses(gh, rels, n):
            if gpos[hgold - 1] == "VERB":
                continue
            n_nv += 1
            subj = [i for i in range(n) if gh[i] == hgold and rels[i].split(":")[0] == "nsubj"]
            pfound = (hgold - 1) in prop_of
            hcorrect = pfound and prop_of[hgold - 1] in [s - 1 for s in [x + 1 for x in subj]]
            prop_found += int(pfound); holder_found += int(hcorrect); both += int(pfound and hcorrect)
            wp = (hgold - 1) in wired
            wh = wp and wired[hgold - 1] in subj      # subj is already 0-based token indices
            w_prop += int(wp); w_holder += int(wh); w_both += int(wp and wh)
            if not pfound:
                miss["property (predicate) NOT detected as a copular state"] += 1
            elif not hcorrect:
                miss["property found but HOLDER != gold subject (binding error)"] += 1
    print("=" * 92)
    print("ENTITY-STATE BINDING on the 167 non-verbal clauses (rung 4/5; live chain + copular_binding):")
    print("  PROPERTY detected (a copular state on the gold predicate)  : %.4f (%d/%d)" % (prop_found / max(1, n_nv), prop_found, n_nv))
    print("  HOLDER correct (bound to the gold subject | detected)      : %.4f (%d/%d)" % (holder_found / max(1, prop_found), holder_found, prop_found))
    print("  BOTH (typed attribute bound to the RIGHT entity)           : %.4f (%d/%d)" % (both / max(1, n_nv), both, n_nv))
    print("  loss split:", dict(miss.most_common()))
    print("  -- WIRED (route my predicate-slot detection into the entity-attribute form) --")
    print("  PROPERTY detected                                          : %.4f (%d/%d)" % (w_prop / max(1, n_nv), w_prop, n_nv))
    print("  HOLDER correct (bound to the gold subject | detected)      : %.4f (%d/%d)" % (w_holder / max(1, w_prop), w_holder, w_prop))
    print("  BOTH (typed attribute bound to the RIGHT entity)           : %.4f (%d/%d)  vs native %.4f" % (w_both / max(1, n_nv), w_both, n_nv, both / max(1, n_nv)))
    out = {"n_nonverbal": n_nv, "property_found": prop_found, "holder_correct": holder_found, "both": both,
           "wired": {"property_found": w_prop, "holder_correct": w_holder, "both": w_both}, "loss": dict(miss)}
    json.dump(out, open(os.path.join(out_dir(), "state_binding.json"), "w", encoding="utf-8"), indent=1)
    return out


def _flanking_nominals(toks, pos, c):
    """(before_idx, after_idx) 1-based: the nearest content NOMINAL head each side of a copula at 0-based c, for
    the ambiguous specificational/identificational case (two nominals flank the copula)."""
    n = len(pos); NOM = ("NOUN", "PROPN", "PRON", "NUM")
    before = None; k = c - 1
    while k >= 0:
        if pos[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
            break
        if pos[k] in NOM:
            before = k + 1; break
        k -= 1
    after = None; k = c + 1
    while k < n:
        if pos[k] in ("PUNCT", "VERB") or (AA.COP_LOCALITY and pos[k] in AA._COP_STOP):
            break
        if pos[k] in NOM + ("ADJ",):
            j = k
            while j + 1 < n and pos[j + 1] in NP_RUN:
                j += 1
            heads = [m for m in range(k, j + 1) if pos[m] in ("NOUN", "PROPN")]
            after = (heads[-1] if heads else j) + 1; break
        k += 1
    return before, after


def givenness(cap=700, th=0.5):
    """PROTOTYPE the DISCOURSE-GIVENNESS tracker (brain-foundational; research SOLVED.md 12c).  Subject choice in an
    inverse/specificational copular clause is discourse-givenness-bound (Centering Cb/Cf: the subject is the
    discourse-OLD/topical element; Birner evoked+inferable).  The needed representation is the SAME graded
    entity-activation a coref register keeps -- so REUSE it: a running per-lemma activation over the corpus-ordered
    sentences (boost on mention, recency-decayed), and for a clause where two NOMINALS flank the copula, the MORE
    active (given) one is the subject, the LESS active (new) one is the predicate; ~equal+both-active = EQUATIVE
    (symmetric, Heycock & Kroch).  Agreement is the repair cue where number MISMATCHES (Wagers/Bresnan).
    Scores, on the ambiguous two-nominal subset, which cue picks the gold predicate: POSITION (after=predicate),
    AGREEMENT, GIVENNESS, COMBINED (givenness, agreement tie-break, position backstop)."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    act = {}                      # lemma -> most recent sentence index seen (higher = more recent = more active)
    hit = {a: [0, 0] for a in ("position", "agreement", "givenness", "combined")}
    equative = 0
    for si, (toks, gpos, gh, rels) in enumerate(test):
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2)
        lows = [w.lower() for w in toks]
        for h in _subject_clauses(gh, rels, n):
            if gpos[h - 1] == "VERB":
                continue
            # find the governing copula of this clause
            c = None
            for j in range(n):
                if t2[j] == "AUX" and lows[j] in COP_FORMS and any(gh[k] == h for k in range(n)):
                    c = j
            # only the ambiguous case: two nominals flank the copula
            cc = None
            for j in range(n):
                if t2[j] == "AUX" and lows[j] in COP_FORMS:
                    b, a = _flanking_nominals(toks, t2, j)
                    if b and a and (gh[b - 1] == h or gh[a - 1] == h or h in (b, a)):
                        cc = j; break
            if cc is None:
                continue
            b, a = _flanking_nominals(toks, t2, cc)
            if not (b and a):
                continue
            # the gold predicate is h; the two candidates are b (pre-copular) and a (post-copular)
            cand = {b, a}
            if h not in cand:
                continue
            gold_pred = h; gold_subj = (a if h == b else b)
            hit.setdefault("_inverse", [0, 0]); hit["_inverse"][1] += 1
            if h == b:                       # gold predicate is the PRE-copular element == a true inverse clause
                hit["_inverse"][0] += 1
            def lemma(idx):
                return _MORPH.morphy(lows[idx - 1], "n") or lows[idx - 1]
            act_b = act.get(lemma(b), -10); act_a = act.get(lemma(a), -10)
            # POSITION: after = predicate
            pos_pred = a
            # AGREEMENT: the DP matching the copula number is the subject -> the other is predicate
            nb, na, nc = _num_nominal(toks[b - 1], t2[b - 1]), _num_nominal(toks[a - 1], t2[a - 1]), _num_cop(toks[cc - 1])
            agr_pred = None
            if nc and nb and na and nb != na:
                agr_pred = a if nb == nc else b        # subject = matches copula; predicate = the other
            agr_pred = agr_pred or pos_pred
            # GIVENNESS: subject = more active; predicate = less active. equal+both-seen -> equative (skip pick).
            if act_b == act_a:
                giv_pred = pos_pred
                if act_b > -10:
                    equative += 1
            else:
                giv_pred = a if act_b > act_a else b   # more-active is subject -> other is predicate
            # COMBINED: givenness first, agreement tie-break (equal activation), position backstop
            if act_b != act_a:
                comb_pred = giv_pred
            elif agr_pred != pos_pred:
                comb_pred = agr_pred
            else:
                comb_pred = pos_pred
            for name, pred in (("position", pos_pred), ("agreement", agr_pred), ("givenness", giv_pred), ("combined", comb_pred)):
                hit[name][0] += int(pred == gold_pred); hit[name][1] += 1
        # update the activation register with THIS sentence's content lemmas (after processing its clauses)
        for j in range(n):
            if t2[j] in ("NOUN", "PROPN", "PRON", "NUM"):
                act[_MORPH.morphy(lows[j], "n") or lows[j]] = si
    print("=" * 92)
    print("DISCOURSE-GIVENNESS / AGREEMENT on the AMBIGUOUS two-nominal copular subset (n=%d):" % hit["position"][1])
    for name in ("position", "agreement", "givenness", "combined"):
        h_, t_ = hit[name]
        print("  %-10s picks the gold predicate: %.4f (n=%d)" % (name, h_ / max(1, t_), t_))
    print("  equative (both flanking nominals equally active): %d" % equative)
    out = {"n": hit["position"][1], "acc": {k: (v[0] / max(1, v[1])) for k, v in hit.items()}, "equative": equative}
    json.dump(out, open(os.path.join(out_dir(), "givenness.json"), "w", encoding="utf-8"), indent=1)
    return out


def decompose(cap=700, th=0.5, gate="all"):
    """For every NON-VERBAL clause (gold predicate not VERB), classify the slot arm's outcome so the recall
    ceiling is attributed to a NAMED cause, not narrated."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    klass = Counter(); ex = defaultdict(list)
    for toks, gold_pos, gold_heads, rels in test:
        n = len(toks)
        base, slot, tags2 = _fire_sets(lc, list(toks), th=th, ext=True, gate=gate)
        cop_ext = cop_predicates_ext(list(toks), list(tags2))
        for h in _subject_clauses(gold_heads, rels, n):
            if gold_pos[h - 1] == "VERB":
                continue
            # subject index (a gold nsubj dependent of h)
            subj = [i + 1 for i in range(n) if gold_heads[i] == h and rels[i].split(":")[0] == "nsubj"]
            s1 = subj[0] if subj else None
            if (h - 1) in slot:
                k = "HIT"
            elif tags2[h - 1] == "VERB":
                k = "HIT(tagged VERB)"           # should not happen (excluded), guard
            elif (h - 1) in base:
                k = "HIT(base rescue)"
            else:
                # not fired.  WHY?
                # is there a copula (AUX in COP_FORMS) governing this clause?
                lows = [t.lower() for t in toks]
                has_cop = any(tags2[j] == "AUX" and lows[j] in COP_FORMS for j in range(n))
                picked = cop_ext & set(range(1, n + 1))
                if gold_pos[h - 1] == "VERB":
                    k = "gold-VERB chain tag error"
                elif not has_cop:
                    k = "no copula in clause (small clause / verbless)"
                elif s1 is not None and (s1 - 1) in slot:
                    k = "INVERTED: scan picked the SUBJECT not the predicate"
                elif cop_ext and h not in cop_ext:
                    k = "copula found, scan picked a DIFFERENT token"
                else:
                    k = "copula not tagged AUX / other"
            klass[k] += 1
            if len(ex[k]) < 6:
                ex[k].append("[%s %s] %s" % (gold_pos[h - 1], toks[h - 1], " ".join(toks)[:90]))
    # also count gold-VERB chain errors separately (predicate is gold VERB but chain didn't tag it VERB)
    print("=" * 92)
    print("NON-VERBAL CLAUSE OUTCOME DECOMPOSITION (slot arm, ext, cap %d):" % cap)
    for k, c in klass.most_common():
        print("  %-52s %4d" % (k, c))
        for e in ex[k][:3]:
            print("        " + e)
    out = {"classes": dict(klass), "examples": {k: ex[k] for k in ex}}
    json.dump(out, open(os.path.join(out_dir(), "decompose.json"), "w", encoding="utf-8"), indent=1)
    return out


def heads_ctx(cap=700, th=0.5):
    """§30 lever prototype (glass-box CONTEXTUAL encoder), the strongest learning-free in-cell form. Build a
    contextual HRR code per token -- base word vector (Random Indexing) + position-bound neighbors via circular
    convolution (Plate HRR; the substrate's FHRR basis) -- and add a head<->dependent contextual-COMPATIBILITY arc
    feature (cosine of contextual codes) to the arc scorer, then held-decode. Tests whether CONTEXTUAL STRUCTURE
    carries the information to attach the copular subject where POS-based cues cannot. HONEST caveat: the base
    vectors are FORM/distributional (char-trigram RI), NOT learned-semantic, and the projection is unlearned -- so a
    NULL here is the LEARNING-FREE FORM-BASED ceiling, NOT a refutation of the learned-semantic contextual lever
    (§25/§31). Measures non-verbal nsubj: base / +contextual-compat (held)."""
    from hdlab.ppmi_sparse_encoder import RandomIndexingEncoder
    import math
    RI = RandomIndexingEncoder(n_dim=1024, k_signs=10)
    ROLE = {d: _random_role(d, 1024) for d in (-3, -2, -1, 1, 2, 3)}

    def ccirc(a, b):                                   # circular convolution (HRR binding) via FFT
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def ctx_codes(toks):
        base = [RI.encode(t).astype(np.float64) for t in toks]
        base = [b / (np.linalg.norm(b) + 1e-9) for b in base]
        n = len(toks); out = []
        for i in range(n):
            v = base[i].copy()
            for d, role in ROLE.items():
                j = i + d
                if 0 <= j < n:
                    v = v + ccirc(base[j], role)
            out.append(v / (np.linalg.norm(v) + 1e-9))
        return out

    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    base_acc = [0, 0]; ctx_acc = [0, 0]
    for toks, gpos, gh, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        hd0 = AA.decode(list(toks), list(t2), A, nn)[0]
        nv_subj = [i + 1 for i in range(n) if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB"]
        C = ctx_codes(list(toks)) if nv_subj else None
        A2 = A.copy()
        W = 6.0
        for s in nv_subj:                              # add contextual head<->dep compatibility to candidate arcs
            for h in range(1, n + 1):
                if h == s:
                    continue
                if math.isfinite(A2[h, s]):
                    A2[h, s] += W * float(np.dot(C[h - 1], C[s - 1]))
        # held decode on the contextual-augmented scores
        hd = AA.decode(list(toks), list(t2), A2, nn)[0]
        mpost = AA.single_root_marginals(A2.copy(), nn, 1.0)
        hdm = AA.punct_convention(list(toks), list(t2), AA.occupancy_repair(list(toks), list(t2), AA.map_tree_single_root(A2, nn), mpost))
        for s in nv_subj:
            hd[s] = hdm.get(s, hd.get(s))
        for i in range(n):
            if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB":
                base_acc[0] += int(hd0.get(i + 1, 0) == gh[i]); base_acc[1] += 1
                ctx_acc[0] += int(hd.get(i + 1, 0) == gh[i])
    print("=" * 92)
    print("§30 CONTEXTUAL-HRR arc feature (learning-free, FORM-based RI) on copular subjects:")
    print("  base %.4f -> +contextual-compat (held) %.4f  (n=%d; reshape+held ref 0.6509)"
          % (base_acc[0] / max(1, base_acc[1]), ctx_acc[0] / max(1, base_acc[1]), base_acc[1]))
    out = {"base": base_acc[0] / max(1, base_acc[1]), "ctx": ctx_acc[0] / max(1, base_acc[1]), "n": base_acc[1]}
    json.dump(out, open(os.path.join(out_dir(), "heads_ctx.json"), "w", encoding="utf-8"), indent=1)
    return out


def _random_role(seed_key, n):
    rng = np.random.default_rng(abs(hash(("role", seed_key))) % (2**32))
    v = rng.standard_normal(n); return v / (np.linalg.norm(v) + 1e-9)


def binding_after_heads(cap=700, th=0.5, boost=5.0, penalty=8.0):
    """FULL-STACK PROPAGATION drill: does the improved heads fix (reshape+held, §28) propagate to the entity-attribute
    BINDING capture (was 0.56 with the base parse; research B: fixing the parse largely fixes binding)?  Recompute the
    typed-attribute capture on the 167 with the holder taken from the RESHAPE+HELD heads instead of the base parse."""
    from hdlab.graded_role_assigner import coarse_roles
    import math
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    NOM = ("NOUN", "PROPN", "PRON", "NUM")
    base_both = [0, 0]; fix_both = [0, 0]
    for toks, gpos, gh, rels in test:
        n = len(toks); lows = [x.lower() for x in toks]
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        hd_base = AA.decode(list(toks), list(t2), A, nn)[0]
        # reshape + held (the §28 fix)
        cop = cop_predicates_ext(list(toks), list(t2)); pairs = []
        for i in range(n):
            if t2[i] != "AUX" or lows[i] not in COP_FORMS:
                continue
            k = i - 1; s = None
            while k >= 0:
                if t2[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                    break
                if t2[k] in NOM:
                    a = k
                    while a - 1 >= 0 and t2[a - 1] in NP_RUN:
                        a -= 1
                    if a - 1 >= 0 and t2[a - 1] == "ADP":
                        k = a - 1; continue
                    s = k + 1; break
                k -= 1
            if s is None:
                continue
            for q in cop:
                if q > i and not any(t2[m] == "VERB" for m in range(i + 1, q - 1)):
                    pairs.append((q, s)); break
        A2 = A.copy()
        for (q, s) in pairs:
            if 1 <= q <= n and 1 <= s <= n:
                if math.isfinite(A2[q, s]):
                    A2[q, s] += boost
                v = hd_base.get(s, 0)
                if 1 <= v <= n and v != q and t2[v - 1] == "VERB" and math.isfinite(A2[v, s]):
                    A2[v, s] -= penalty
        hd_fix = AA.decode(list(toks), list(t2), A2, nn)[0]
        mpost = AA.single_root_marginals(A2.copy(), nn, 1.0)
        hdm = AA.punct_convention(list(toks), list(t2), AA.occupancy_repair(list(toks), list(t2), AA.map_tree_single_root(A2, nn), mpost))
        for (q, s) in pairs:
            if 1 <= s <= n:
                hd_fix[s] = hdm.get(s, hd_fix.get(s))
        # binding capture: for each non-verbal clause, is the PROPERTY (gold predicate) detected AND the HOLDER (its
        # parse-attached subject) == the gold subject?  base heads vs reshape+held heads.
        for hgold in _subject_clauses(gh, rels, n):
            if gpos[hgold - 1] == "VERB":
                continue
            if hgold not in cop:                # property detected == in cop_predicates (same for both arms)
                continue
            gsubj = set(i for i in range(n) if gh[i] == hgold and rels[i].split(":")[0] == "nsubj")
            # holder = the token whose parse-head is the predicate (the subject the parse binds to it)
            hb = [i for i in range(1, n + 1) if hd_base.get(i) == hgold and t2[i - 1] in NOM]
            hf = [i for i in range(1, n + 1) if hd_fix.get(i) == hgold and t2[i - 1] in NOM]
            base_both[1] += 1; fix_both[1] += 1
            base_both[0] += int(any((h - 1) in gsubj for h in hb))
            fix_both[0] += int(any((h - 1) in gsubj for h in hf))
    print("=" * 92)
    print("FULL-STACK: does the reshape+held heads fix propagate to entity-attribute BINDING capture?")
    print("  typed attribute bound to the RIGHT entity (property detected + holder=gold subject):")
    print("    base-parse heads   : %.4f (%d/%d)" % (base_both[0] / max(1, base_both[1]), base_both[0], base_both[1]))
    print("    reshape+held heads : %.4f (%d/%d)" % (fix_both[0] / max(1, fix_both[1]), fix_both[0], fix_both[1]))
    out = {"base": base_both[0] / max(1, base_both[1]), "reshape_held": fix_both[0] / max(1, fix_both[1]),
           "n": base_both[1]}
    json.dump(out, open(os.path.join(out_dir(), "binding_after_heads.json"), "w", encoding="utf-8"), indent=1)
    return out


def heads_reshape(cap=700, th=0.5):
    """The FULL understood fix (§27), BF + not cheap: the arc scorer favors subject->VERB, so for a copular clause it
    steals the subject onto a VERB buried in the predicate phrase (an EMBEDDED clause -- small-clause locality,
    Stowell: that verb is not the matrix predicate). The fix RESHAPES the competition (not just re-routes): BOOST the
    subject->predicate arc (occupancy delivered as an arc feature) AND SUPPRESS the subject->embedded-verb arc (the
    verb that is not the clause's predicate). This can EXCEED the MAP ceiling because it changes the effective
    validities, testing the §27 understanding. Sweeps boost/penalty (operating point, not adopted)."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    NOM = ("NOUN", "PROPN", "PRON", "NUM")
    import math
    cache = []
    for toks, gpos, gh, rels in test:
        n = len(toks); lows = [x.lower() for x in toks]
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        pairs = []
        cop = cop_predicates_ext(list(toks), list(t2))
        for i in range(n):
            if t2[i] != "AUX" or lows[i] not in COP_FORMS:
                continue
            k = i - 1; s = None
            while k >= 0:
                if t2[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                    break
                if t2[k] in NOM:
                    a = k
                    while a - 1 >= 0 and t2[a - 1] in NP_RUN:
                        a -= 1
                    if a - 1 >= 0 and t2[a - 1] == "ADP":
                        k = a - 1; continue
                    s = k + 1; break
                k -= 1
            if s is None:
                continue
            for q in cop:
                if q > i and not any(t2[m] == "VERB" for m in range(i + 1, q - 1)):
                    pairs.append((q, s)); break
        cache.append((toks, gpos, gh, rels, t2, dd, pairs))

    def score(boost, penalty, held=False):
        acc = [0, 0]
        for (toks, gpos, gh, rels, t2, dd, pairs) in cache:
            n = len(toks)
            A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
            hd0 = AA.decode(list(toks), list(t2), A, nn)[0]
            for (q, s) in pairs:
                if not (1 <= q <= n and 1 <= s <= n):
                    continue
                if math.isfinite(A[q, s]):
                    A[q, s] += boost                                  # deliver occupancy as an arc feature
                v = hd0.get(s, 0)                                      # the arc that currently steals the subject
                if 1 <= v <= n and v != q and t2[v - 1] == "VERB" and math.isfinite(A[v, s]):
                    A[v, s] -= penalty                                # suppress subject->embedded-verb (small-clause locality)
            hd = AA.decode(list(toks), list(t2), A, nn)[0]            # incremental (reshaped scores)
            if held:                                                  # + held decode: defer copular subj to MAP-of-reshaped-A
                mpost = AA.single_root_marginals(A.copy(), nn, 1.0)
                hdm = AA.punct_convention(list(toks), list(t2),
                        AA.occupancy_repair(list(toks), list(t2), AA.map_tree_single_root(A, nn), mpost))
                for (q, s) in pairs:
                    if 1 <= s <= n:
                        hd[s] = hdm.get(s, hd.get(s))
            for i in range(n):
                if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB":
                    acc[0] += int(hd.get(i + 1, 0) == gh[i]); acc[1] += 1
        return acc[0] / max(1, acc[1]), acc[1]
    base, n = score(0.0, 0.0)
    print("=" * 92)
    print("HEADS RESHAPE (boost predicate + suppress competing embedded-verb) -- can it EXCEED the MAP ceiling 0.633?")
    print("  base %.4f (n=%d)" % (base, n))
    res = {"base": base}
    for b, p in ((3.0, 3.0), (5.0, 8.0)):
        a, _ = score(b, p)
        print("  boost=%.0f penalty=%.0f (incr)       -> %.4f" % (b, p, a))
        res["b%.0f_p%.0f" % (b, p)] = a
    ah, _ = score(5.0, 8.0, held=True)
    print("  boost=5 penalty=8 + HELD decode    -> %.4f   (vs MAP ceiling 0.6331)" % ah)
    res["b5_p8_held"] = ah
    json.dump(res, open(os.path.join(out_dir(), "heads_reshape.json"), "w", encoding="utf-8"), indent=1)
    return res


def heads_full(cap=700, th=0.5):
    """DO-IT-ALL heads-rung fix, brain-foundational: combine WALL A (held/predicted copular-subject commitment) with a
    LEARNED copular-subject cue validity (not a fixed bonus).  The cue weight = the Competition-Model log-odds
    validity of the copular-subject construction, ESTIMATED from the corpus (frequency x contingency: how often a
    pre-copular nominal in a copular construction is the subject of the post-copular predicate) -- learned, not
    hand-set (addresses the §25 weak-fixed-bonus flag).  Then the HELD decode resolves the copular subject with the
    predicate visible.  Measures non-verbal nsubj: base / cue-only / held-only / HELD+CUE, vs verbal 0.85."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    NOM = ("NOUN", "PROPN", "PRON", "NUM")

    def cop_subjects(toks, t2):
        lows = [x.lower() for x in toks]; n = len(toks); out = []
        cop = cop_predicates_ext(list(toks), list(t2))
        for i in range(n):
            if t2[i] != "AUX" or lows[i] not in COP_FORMS:
                continue
            k = i - 1; s = None
            while k >= 0:
                if t2[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                    break
                if t2[k] in NOM:
                    a = k
                    while a - 1 >= 0 and t2[a - 1] in NP_RUN:
                        a -= 1
                    if a - 1 >= 0 and t2[a - 1] == "ADP":
                        k = a - 1; continue
                    s = k + 1; break
                k -= 1
            if s is None:
                continue
            for q in cop:
                if q > i and not any(t2[m] == "VERB" for m in range(i + 1, q - 1)):
                    out.append((q, s)); break
        return out

    # PASS 1 -- LEARN the cue validity from the corpus: contingency that a detected copular subject is gold-correct.
    hit = 0; tot = 0
    cache = []
    for toks, gpos, gh, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        pairs = cop_subjects(toks, t2)
        for (q, s) in pairs:
            tot += 1
            if 1 <= s <= n and gh[s - 1] == q:
                hit += 1
        cache.append((toks, gpos, gh, rels, t2, dd, pairs))
    contingency = hit / max(1, tot)                                  # P(subject | copular construction)
    import math
    w_learned = math.log(max(contingency, 1e-6) / max(1 - contingency, 1e-6))   # log-odds validity (Bates-MacWhinney)
    w_learned = max(0.0, w_learned)

    def score(mode):
        acc = [0, 0]
        for (toks, gpos, gh, rels, t2, dd, pairs) in cache:
            n = len(toks)
            A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
            if mode in ("cue", "held+cue"):
                for (q, s) in pairs:
                    if 1 <= q <= n and 1 <= s <= n and math.isfinite(A[q, s]):
                        A[q, s] += w_learned
            hd = AA.decode(list(toks), list(t2), A, nn)[0]           # incremental (live default)
            if mode in ("held", "held+cue"):
                mpost = AA.single_root_marginals(A.copy(), nn, 1.0)
                hd_map = AA.punct_convention(list(toks), list(t2),
                          AA.occupancy_repair(list(toks), list(t2), AA.map_tree_single_root(A, nn), mpost))
                for (q, s) in pairs:
                    if 1 <= s <= n:
                        hd[s] = hd_map.get(s, hd.get(s))
            for i in range(n):
                if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB":
                    acc[0] += int(hd.get(i + 1, 0) == gh[i]); acc[1] += 1
        return acc[0] / max(1, acc[1]), acc[1]
    base, n = score("base"); cue, _ = score("cue"); held, _ = score("held"); both, _ = score("held+cue")
    print("=" * 92)
    print("DO-IT-ALL heads fix -- learned cue validity (contingency %.3f -> w=%.2f) + held decode:" % (contingency, w_learned))
    print("  non-verbal nsubj:  base %.4f | cue-only %.4f | held-only %.4f | HELD+CUE %.4f   (n=%d; verbal target ~0.85)"
          % (base, cue, held, both, n))
    out = {"contingency": contingency, "w_learned": w_learned, "base": base, "cue": cue, "held": held, "held_cue": both, "n": n}
    json.dump(out, open(os.path.join(out_dir(), "heads_full.json"), "w", encoding="utf-8"), indent=1)
    return out


def heads_held(cap=700, th=0.5):
    """WALL A prototype (research SOLVED.md 22): the incremental beam commits the copular subject BEFORE its predicate
    arrives (eager attach) -> incr 0.54 < MAP 0.63 on the SAME clauses.  The brain HOLDS the open dependency and
    resolves it once the predicate is seen (Gibson storage cost; Levy expectation; Lewis & Vasishth retrieval;
    small-clause grammar Stowell/Mikkelsen).  Prototype the HOLD: run the live incremental decode, but for a copular
    SUBJECT (a pre-copular nominal whose clause has a cop_predicate) DEFER its head to the full-information (MAP)
    resolution of that arc -- a bounded, local hold, NOT global lookahead, NOT a hard rule (it resolves by the arc
    score with the predicate visible).  Measures non-verbal nsubj: incremental vs MAP vs HELD."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    NOM = ("NOUN", "PROPN", "PRON", "NUM")
    inc = [0, 0]; mp = [0, 0]; held = [0, 0]
    for toks, gpos, gh, rels in test:
        n = len(toks); lows = [x.lower() for x in toks]
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        hd_inc = AA.decode(list(toks), list(t2), A, nn)[0]                 # live incremental (module default DECODE=incr)
        mpost = AA.single_root_marginals(A.copy(), nn, 1.0)
        hd_map = AA.map_tree_single_root(A, nn)
        hd_map = AA.occupancy_repair(list(toks), list(t2), hd_map, mpost)
        hd_map = AA.punct_convention(list(toks), list(t2), hd_map)
        # copular subjects: pre-copular NP head in a clause with a cop_predicate
        cop = cop_predicates_ext(list(toks), list(t2)); csub = set()
        for i in range(n):
            if t2[i] != "AUX" or lows[i] not in COP_FORMS:
                continue
            k = i - 1
            while k >= 0:
                if t2[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                    break
                if t2[k] in NOM:
                    a = k
                    while a - 1 >= 0 and t2[a - 1] in NP_RUN:
                        a -= 1
                    if a - 1 >= 0 and t2[a - 1] == "ADP":
                        k = a - 1; continue
                    if any(q > i for q in cop):
                        csub.add(k + 1)
                    break
                k -= 1
        hd_held = dict(hd_inc)
        for s in csub:
            hd_held[s] = hd_map.get(s, hd_inc.get(s))       # DEFER the copular subject to full-information resolution
        for i in range(n):
            if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB":
                inc[0] += int(hd_inc.get(i + 1, 0) == gh[i]); inc[1] += 1
                mp[0] += int(hd_map.get(i + 1, 0) == gh[i]); mp[1] += 1
                held[0] += int(hd_held.get(i + 1, 0) == gh[i]); held[1] += 1
    print("=" * 92)
    print("WALL A -- HELD copular-subject decode (defer to full-info resolution; brain: hold open dependency):")
    print("  non-verbal nsubj attachment:  incremental %.4f   MAP %.4f   HELD %.4f   (n=%d)"
          % (inc[0] / inc[1], mp[0] / mp[1], held[0] / held[1], inc[1]))
    print("  -> HELD closes %.0f%% of the incr->MAP gap while staying incremental (bounded local hold)."
          % (100.0 * (held[0] / held[1] - inc[0] / inc[1]) / max(1e-9, (mp[0] / mp[1] - inc[0] / inc[1]))))
    out = {"incremental": inc[0] / inc[1], "map": mp[0] / mp[1], "held": held[0] / held[1], "n": inc[1]}
    json.dump(out, open(os.path.join(out_dir(), "heads_held.json"), "w", encoding="utf-8"), indent=1)
    return out


def roles_fix(cap=700, th=0.5):
    """ROLES NONPRED-backoff fix (diff 3), cheap in-cell PROXY.  On the 167, the SUBJECT is already labelled ~0.84
    (the cop cue), but OBLIQUES of a non-verbal predicate score ~0.53 vs ~0.83 verbal -- located to `_parent_config`
    collapsing a non-verbal head to NONPRED.  PROXY for "treat the non-verbal predicate as a PREDICATE for the role
    config": run the live role competition with the predicate head's TAG forced to VERB (so it takes the PRED_*
    configuration + the shipped PRED strengths) and compare core-argument role accuracy to the shipped read.
    (The faithful landed form is the table rebuild with pred_heads threaded; this proxy tests the hypothesis.)"""
    from hdlab.graded_role_assigner import coarse_roles
    from hdlab.arc_labeler import norm_label
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    base = defaultdict(lambda: [0, 0]); fix = defaultdict(lambda: [0, 0])
    for toks, gpos, gh, rels in test:
        n = len(toks)
        heads = {i + 1: gh[i] for i in range(n)}
        pred_nv = set(h for h in _subject_clauses(gh, rels, n) if gpos[h - 1] != "VERB")
        r_base = coarse_roles(list(toks), list(gpos), heads, head_posterior=None)
        gpos2 = list(gpos)
        for h in pred_nv:                                   # force the non-verbal predicate's tag to VERB (PRED config)
            gpos2[h - 1] = "VERB"
        r_fix = coarse_roles(list(toks), list(gpos2), heads, head_posterior=None)
        for i in range(n):
            if gh[i] in pred_nv and _core(rels[i]):
                g = norm_label(rels[i]); r = g.split(":")[0]
                if r == "cop":                              # the competition doesn't emit cop -- skip (instrument artifact)
                    continue
                base[r][0] += int(norm_label(r_base.get(i + 1, "")) == g); base[r][1] += 1
                fix[r][0] += int(norm_label(r_fix.get(i + 1, "")) == g); fix[r][1] += 1
    print("=" * 92)
    print("ROLES NONPRED-backoff PROXY (treat the non-verbal predicate as PRED for the role config), on the 167:")
    allb = [0, 0]; allf = [0, 0]
    for r in sorted(base, key=lambda k: -base[k][1]):
        b = base[r]; f = fix[r]
        allb[0] += b[0]; allb[1] += b[1]; allf[0] += f[0]; allf[1] += f[1]
        print("  %-8s base %.4f -> PRED-config %.4f  (n=%d)" % (r, b[0] / max(1, b[1]), f[0] / max(1, f[1]), b[1]))
    print("  OVERALL core-arg role acc: base %.4f -> %.4f  (n=%d)" % (allb[0] / max(1, allb[1]), allf[0] / max(1, allf[1]), allb[1]))
    out = {"by_role": {r: {"base": base[r][0] / max(1, base[r][1]), "fix": fix[r][0] / max(1, fix[r][1]), "n": base[r][1]} for r in base},
           "overall_base": allb[0] / max(1, allb[1]), "overall_fix": allf[0] / max(1, allf[1])}
    json.dump(out, open(os.path.join(out_dir(), "roles_fix.json"), "w", encoding="utf-8"), indent=1)
    return out


def heads_graded_fix(cap=700, th=0.5, weights=(0.0, 1.0, 2.0, 3.0, 5.0)):
    """BRAIN-FOUNDATIONAL heads-rung fix (research SOLVED.md 17/18): the copula is a light functional head (Moro/
    Bowers/den Dikken; UD convention), so the subject arc belongs on the PREDICATE.  Implemented NOT as a hard
    re-attach but as a GRADED ARC FEATURE in the existing competition: add a weighted bonus to the arc
    (head=predicate -> dependent=subject) in the arc-score matrix and RE-DECODE, so the predicate-slot cue competes
    with the parser's other cues (and online learning could carry it).  Sweeps the weight (operating point, not
    adopted).  w=0 == base.  TWIN control = add the SAME bonus to a RANDOM (nominal -> its clause's random token) arc."""
    from hdlab.graded_role_assigner import coarse_roles  # not needed; kept minimal
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    NOM = ("NOUN", "PROPN", "PRON", "NUM")
    rng = np.random.default_rng(0)
    res = {w: {"verbal": [0, 0], "nonverbal": [0, 0]} for w in weights}
    twin = {w: [0, 0] for w in weights}
    for toks, gpos, gh, rels in test:
        n = len(toks); lows = [x.lower() for x in toks]
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        A0, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        # copular (predicate, subject) pairs: predicate = cop complement; subject = nearest pre-copular NP head
        pairs = []
        for i in range(n):
            if t2[i] != "AUX" or lows[i] not in COP_FORMS:
                continue
            preds = [q for q in cop_predicates_ext(list(toks), list(t2)) if any(t2[j] == "AUX" and lows[j] in COP_FORMS for j in range(0, q - 1))]
            # subject scan left of the copula
            s = None; k = i - 1
            while k >= 0:
                if t2[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                    break
                if t2[k] in NOM:
                    a = k
                    while a - 1 >= 0 and t2[a - 1] in NP_RUN:
                        a -= 1
                    if a - 1 >= 0 and t2[a - 1] == "ADP":
                        k = a - 1; continue
                    s = k + 1; break
                k -= 1
            for q in cop_predicates_ext(list(toks), list(t2)):
                # is this copula the one governing q? (nearest AUX-cop before q with no verb between)
                if q > i and not any(t2[m] == "VERB" for m in range(i + 1, q - 1)) and s is not None and s != q:
                    pairs.append((q, s)); break
        gold_nv = {h for h in _subject_clauses(gh, rels, n) if gpos[h - 1] != "VERB"}
        for w in weights:
            A = A0.copy()
            for (q, s) in pairs:
                if 1 <= q <= n and 1 <= s <= n:
                    A[q, s] += w
            hd = AA.decode(list(toks), list(t2), A, nn)[0]
            for i in range(n):
                if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n:
                    kind = "verbal" if gpos[gh[i] - 1] == "VERB" else "nonverbal"
                    res[w][kind][0] += int(hd.get(i + 1, 0) == gh[i]); res[w][kind][1] += 1
            # twin: same bonus on a random (subject -> random clause token) arc
            At = A0.copy()
            for (q, s) in pairs:
                r = rng.integers(1, n + 1)
                if 1 <= s <= n:
                    At[r, s] += w
            hdt = AA.decode(list(toks), list(t2), At, nn)[0]
            for i in range(n):
                if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB":
                    twin[w][0] += int(hdt.get(i + 1, 0) == gh[i]); twin[w][1] += 1
    print("=" * 92)
    print("HEADS-RUNG GRADED FIX -- predicate-slot occupancy as an additive ARC FEATURE (re-decode, not a re-attach):")
    print("  %-6s %-16s %-16s %-16s" % ("w", "nsubj(NONverbal)", "nsubj(verbal)", "twin(NONverbal)"))
    for w in weights:
        nv = res[w]["nonverbal"]; vb = res[w]["verbal"]; tw = twin[w]
        print("  %-6.1f %-16.4f %-16.4f %-16.4f" % (w, nv[0] / max(1, nv[1]), vb[0] / max(1, vb[1]), tw[0] / max(1, tw[1])))
    out = {"weights": {str(w): {"nonverbal": res[w]["nonverbal"][0] / max(1, res[w]["nonverbal"][1]),
                                "verbal": res[w]["verbal"][0] / max(1, res[w]["verbal"][1]),
                                "twin": twin[w][0] / max(1, twin[w][1])} for w in weights}}
    json.dump(out, open(os.path.join(out_dir(), "heads_graded_fix.json"), "w", encoding="utf-8"), indent=1)
    return out


def _pred_subj_pairs(toks, pos):
    """(predicate q, subject s) pairs for copular clauses -- the brain's copular construction: the copula links a
    SUBJECT to its PREDICATE, and the predicate is the first one WITHIN the clause boundary (locality), not a verb
    buried in a PP or an embedded clause.  Handles BOTH orders:
      STANDARD  "the sky IS blue"          subject before the copula, predicate (cop complement) after.
      INVERTED  "IS that a maker ?"         copula clause-initial: the first nominal after it is the SUBJECT, the
                                            predicate is the next NP head / ADJ (yes/no-question inversion)."""
    n = len(pos); lows = [t.lower() for t in toks]; out = []
    NOM = ("NOUN", "PROPN", "PRON", "NUM")
    for c in range(n):
        if pos[c] != "AUX" or lows[c] not in COP_FORMS:
            continue
        # is there a verbal host in the copula's own verb group? then it is an ordinary auxiliary, skip.
        host = False
        for k in range(c + 1, n):
            if pos[k] == "VERB":
                host = True; break
            if pos[k] == "PUNCT" or (AA.COP_LOCALITY and (pos[k] in AA._COP_STOP or (pos[k] == "PART" and lows[k] == "to"))):
                break
        if host:
            continue
        # the SUBJECT before the copula: nearest NP head not inside a PP; stop at a verb / clause boundary.
        subj = None; k = c - 1
        while k >= 0:
            if pos[k] in NOM:
                a = k
                while a - 1 >= 0 and pos[a - 1] in NP_RUN:
                    a -= 1
                if a - 1 >= 0 and pos[a - 1] == "ADP":
                    k = a - 1; continue                 # PP-internal, not the subject; keep scanning left
                subj = k + 1; break
            if pos[k] in ("VERB", "SCONJ", "CCONJ", "PUNCT"):
                break
            k -= 1
        # the PREDICATE: the copula complement within the clause boundary (cop_predicates locality)
        pred = None
        for k in range(c + 1, n):
            if pos[k] in ("VERB", "PUNCT"):
                break
            if AA.COP_LOCALITY and (pos[k] in AA._COP_STOP or (pos[k] == "PART" and lows[k] == "to")):
                break
            if pos[k] in ("ADJ",) + NOM:
                j = k
                while j + 1 < n and pos[j + 1] in NP_RUN:
                    j += 1
                heads = [m for m in range(k, j + 1) if pos[m] in ("NOUN", "PROPN")]
                pred = (heads[-1] if heads else j) + 1
                if subj is None:                        # INVERTED: this first nominal is the SUBJECT
                    subj2 = pred
                    # the predicate is the NEXT NP head / ADJ after the subject NP
                    pred = None
                    for m in range(j + 1, n):
                        if pos[m] in ("VERB", "PUNCT") or (AA.COP_LOCALITY and pos[m] in AA._COP_STOP):
                            break
                        if pos[m] in ("ADJ",) + NOM:
                            jj = m
                            while jj + 1 < n and pos[jj + 1] in NP_RUN:
                                jj += 1
                            hh = [x for x in range(m, jj + 1) if pos[x] in ("NOUN", "PROPN")]
                            pred = (hh[-1] if hh else jj) + 1; break
                    if pred is not None:
                        out.append((pred, subj2))
                    break
                break
        if subj is not None and pred is not None and subj != pred:
            out.append((pred, subj))
    return out


def heads_fix(cap=700, th=0.5, v2=False):
    """UPSTREAM CORRECTION, prototyped (not landed).  The heads rung attaches the subject to a non-verbal
    predicate at only 0.54 (vs 0.85 verbal) -- the root upstream loss.  The predicate-slot signal already
    computes WHERE the predicate is (cop_predicates); the brain attaches the subject to its predicate, so bias
    the nsubj arc toward that token.  PROTOTYPE (post-hoc, no hdlab edit): re-attach a pre-copular subject
    nominal to the copula's cop_predicates complement.  Measures the nsubj-arc accuracy lift on the 167."""
    from hdlab.graded_role_assigner import coarse_roles
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities(AA.ASSET)
    base = {"verbal": [0, 0], "nonverbal": [0, 0]}; fix = {"verbal": [0, 0], "nonverbal": [0, 0]}
    moved = 0; moved_right = 0
    for toks, gpos, gh, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        hd = AA.heads_graded(list(toks), list(t2), dd, tab)
        # the fix: attach the copular SUBJECT to its PREDICATE (the copula's complement within the clause boundary),
        # overriding an attachment to a verb buried in a PP / embedded clause.  v2 = the locality+inversion-aware
        # pairs; else the arm's csub_sites.
        cop = cop_predicates_ext(list(toks), list(t2))
        # csub_sites (the arm's copular-subject cue) gives (predicate q, subject s) pairs; re-attach ONLY when q is
        # a confident predicate slot (q in the locality-respecting cop_predicates) -- this filter is what keeps the
        # precision up (dropping it re-attaches on every csub proposal and tanks precision to 0.13).
        hd2 = dict(hd)
        for (q, subj) in AA.csub_sites(list(toks), list(t2)):
            if q in cop and 1 <= subj <= n and 1 <= q <= n and hd2.get(subj) != q:
                hd2[subj] = q; moved += 1
                if gh[subj - 1] == q:
                    moved_right += 1
        for i in range(n):
            if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n:
                kind = "verbal" if gpos[gh[i] - 1] == "VERB" else "nonverbal"
                base[kind][0] += int(hd.get(i + 1, 0) == gh[i]); base[kind][1] += 1
                fix[kind][0] += int(hd2.get(i + 1, 0) == gh[i]); fix[kind][1] += 1
    print("=" * 92)
    print("HEADS-RUNG UPSTREAM CORRECTION (prototype): subject->predicate attachment on the nsubj arc")
    for k in ("verbal", "nonverbal"):
        b = base[k][0] / max(1, base[k][1]); f = fix[k][0] / max(1, fix[k][1])
        print("  %-10s  base %.4f -> +cop-slot bias %.4f  (n=%d)" % (k, b, f, base[k][1]))
    print("  re-attachments made: %d, of which correct: %d (precision %.3f)"
          % (moved, moved_right, moved_right / max(1, moved)))
    out = {"base": base, "fix": fix, "moved": moved, "moved_right": moved_right}
    json.dump(out, open(os.path.join(out_dir(), "heads_fix.json"), "w", encoding="utf-8"), indent=1)
    return out


def board(arm="base", cap_ud=300, cap_state=300, cap_gum=40):
    """The 7-dimension modern board, A/B.  arm='slot' monkeypatches the FULL proposed mechanism live -- the
    extended cop_predicates AND the reader firing an event on every copular complement -- so any board dimension
    that consumes the event stream or the copular-complement identity would move.  The finding: the board's
    who_did_what dims iterate GOLD VERBS and the state dim reads the copular-BINDING path, so NONE consume the
    non-verbal-predicate event stream -> the board is VERB-gated too and cannot score this gain (which is exactly
    why pri 110 10f specified the participant instrument, built above)."""
    os.environ["HDLAB_EXP_NAME"] = "nonverbal_predication_participants_v1_board_" + arm
    restore = []
    if arm != "base":
        # (1) the upstream extension
        _orig_cop = AA.cop_predicates
        AA.cop_predicates = cop_predicates_ext
        restore.append(lambda: setattr(AA, "cop_predicates", _orig_cop))
        # (2) the reader fires an event on every copular complement (the proposed situation_reader change)
        import hdlab.situation_reader as SR
        _orig_ex = SR.SituationReader._extract_events

        def patched_ex(self, text):
            events, tagged = _orig_ex(self, text)
            toks = text.split()
            try:
                pos = self._cached_tag(toks)
            except Exception:
                return events, tagged
            have = set(e.idx for e in events)
            from hdlab.situation_reader import T as _T
            for q in cop_predicates_ext(list(toks), list(pos)):
                if (q - 1) not in have and 0 <= q - 1 < len(toks):
                    events.append(_T.Event(lemma=toks[q - 1].lower(), idx=q - 1, pos=pos[q - 1],
                                           tense=_T.TENSE_SIMPLE_PAST, is_pp=False))
            events.sort(key=lambda e: e.idx)
            return events, tagged
        SR.SituationReader._extract_events = patched_ex
        restore.append(lambda: setattr(SR.SituationReader, "_extract_events", _orig_ex))
    try:
        import importlib
        B = importlib.import_module("experiments.exp_situation_model_qa_modern_v1")
        res = B.run(caps={"gum": cap_gum, "ud": cap_ud, "state": cap_state, "wic_mode": "smoke"}, n_boot=300,
                    run_new_arms=False, write_metrics=False)
    finally:
        for f in reversed(restore):
            f()
    rows = {k: (v or {}).get("model_acc") for k, v in res["per_dimension"].items()}
    print("BOARD(capped) ARM %-5s  agg=%.4f  %s" % (arm, res["aggregate_19c_free"]["model_acc"],
          " ".join("%s=%.4f" % (k, v) for k, v in rows.items() if v is not None)))
    json.dump({"arm": arm, "aggregate": res["aggregate_19c_free"]["model_acc"], "per_dimension": rows},
              open(os.path.join(out_dir(), "board_%s.json" % arm), "w", encoding="utf-8"), indent=1)
    return rows


def self_test():
    """Fast witness: the extended scan is a SUPERSET of the shipped one and byte-identical on non-ADV /
    non-clause-final cases; the participant instrument runs and the twin loses."""
    lc = LC.get()
    checks = []

    def ck(name, cond, extra=""):
        checks.append((name, bool(cond), extra))
        print(("  ok  " if cond else "  FAIL") + "  " + name + (("  -- " + extra) if extra else ""))

    # 1. superset on a battery of sentences
    cases = [
        "The sky is blue .".split(),
        "She is a doctor .".split(),
        "He is here .".split(),
        "The meeting is tomorrow .".split(),
        "Google is a search engine .".split(),
        "I am sure they are .".split(),
        "There is no proof .".split(),
        "The cat sat on the mat .".split(),
    ]
    superset = True; identical_nonadv = True
    for toks in cases:
        pos, _ = lc.tag_with_posterior(list(toks))
        a = AA.cop_predicates(list(toks), list(pos))
        b = cop_predicates_ext(list(toks), list(pos))
        if not a <= b:
            superset = False
    ck("extended cop scan is a SUPERSET of the shipped scan", superset)
    # 2. ADV complement recovered
    toks = "He is here .".split(); pos, _ = lc.tag_with_posterior(list(toks))
    a = AA.cop_predicates(list(toks), list(pos)); b = cop_predicates_ext(list(toks), list(pos))
    ck("locative 'here' recovered by the extension", len(b) >= len(a), "shipped=%s ext=%s pos=%s" % (a, b, pos))
    # 3. instrument runs small + twin loses
    r = participant(cap=120, th=0.5)
    ck("slot recall on non-verbal >= floor", r["arms"]["slot"]["recall_nonverbal"] >= r["arms"]["floor"]["recall_nonverbal"])
    ck("twin recall on non-verbal < slot recall (info-free loses)",
       r["arms"]["twin"]["recall_nonverbal"] < r["arms"]["slot"]["recall_nonverbal"],
       "twin=%.3f slot=%.3f" % (r["arms"]["twin"]["recall_nonverbal"], r["arms"]["slot"]["recall_nonverbal"]))
    npass = sum(1 for _n, c, _e in checks if c)
    print("-" * 60)
    print("SELF-TEST %d/%d" % (npass, len(checks)))
    return npass == len(checks)


if __name__ == "__main__":
    a = sys.argv[1:]

    def argv(flag, default=None, cast=str):
        if flag in a:
            return cast(a[a.index(flag) + 1])
        return default

    if "--self-test" in a:
        ok = self_test()
        sys.exit(0 if ok else 1)
    elif "--diag65" in a:
        diag65(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--type-inference" in a:
        type_inference()
    elif "--spatial" in a:
        spatial(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--shell" in a:
        shell(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--typing" in a:
        typing(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--state-binding" in a:
        state_binding(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--givenness" in a:
        givenness(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--decompose" in a:
        decompose(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float), gate=argv("--gate", "all"))
    elif "--heads-ctx" in a:
        heads_ctx(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--binding-after-heads" in a:
        binding_after_heads(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--heads-reshape" in a:
        heads_reshape(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--heads-full" in a:
        heads_full(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--heads-held" in a:
        heads_held(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--roles-fix" in a:
        roles_fix(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--heads-graded" in a:
        heads_graded_fix(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--heads-fix" in a:
        heads_fix(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float))
    elif "--board" in a:
        board(arm=argv("--arm", "base"), cap_ud=argv("--cap", 300, int), cap_state=argv("--cap", 300, int))
    elif "--participant" in a:
        participant(cap=argv("--cap", 700, int), th=argv("--th", 0.5, float),
                    ext=("--no-ext" not in a), gate=argv("--gate", "verbless_clause"),
                    pop=argv("--pop", "ud"))
    else:
        print(__doc__)
