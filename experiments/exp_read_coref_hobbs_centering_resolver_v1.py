"""exp_read_coref_hobbs_centering_resolver_v1 -- close the COREFERENCE gap in glass-box reading, NO LLM.

The v2 parser (exp_read_grow_foundation_realprose_glassbox_ie_v2) correctly ABSTAINS on a pronoun-subject
sentence with no in-sentence antecedent ("It eats the worm." -> COREF_UNRESOLVED). The research drill
(notes/research_coreference_hobbs_centering_resolver_2026-07-16.md) localized the gap as INFRASTRUCTURAL:
ie_extract(sentence) is a stateless single-sentence function, so there is nowhere to run a resolver. The fix
is two separable pieces + a rebuilt fixture set + a guardrail:

  ANCHOR 1 (corpus rebuild): the two old coref rows in v2's PROSE_CORPUS were mis-specified isolated sentences
    (gold antecedent many rows away, several intervening animal-mentions). Rebuilt here as GENUINE
    local-antecedent discourse PAIRS/TRIPLES (antecedent-establishing sentence + pronoun sentence, single
    number-compatible candidate) PLUS a separate DELIBERATELY-AMBIGUOUS fixture set (2+ candidates that survive
    BOTH number-agreement AND schema-type filtering -> correct-ABSTAIN target).
  ANCHOR 2 (discourse-memory shim): a rolling per-document list of (sidx, lemma, role, number) mentions,
    window=2 sentences, threaded through a read-loop. New STATE, not a new algorithm -- role/number are read
    off the tokens the parser already tags.
  ANCHOR 3 (Hobbs/Centering resolver, precision-first per note section (b) step 2): when ie_extract hits
    COREF_UNRESOLVED, rank memory by recency (most-recent sentence first) then subject-role-before-object
    (Centering Cf ranking, kept for provenance), FILTER by number agreement (it->singular, they->plural; this
    register's closed animal-noun lexicon has NO grammatical-gender cue -- number is the ONLY hard categorical
    filter, a register-specific weakness flagged in the research note). If EXACTLY ONE distinct lemma survives
    the number filter -> BIND (substitute the pronoun with the antecedent lemma, re-parse with the SAME
    ie_extract, tag HOBBS_COREF, carry provenance = current + antecedent sentence pointers). If ZERO or 2+
    survive -> ABSTAIN (do not guess). Precision is paramount: subject-preference is NOT used to override a
    number-tie -- a same-number ambiguity is a correct ABSTAIN, never a guess.
  ANCHOR 4 (OPTIONAL schema-type tie-breaker, Pred B): when number-agreement leaves 2+ survivors, optionally
    keep only candidates whose substituted triple is NOT gate-REJECTed (Hobbs' own selectional-restriction
    augmentation: 88.3%->91.7%). Measured, not assumed. Run as a secondary arm; reports how many number-ties
    the closed schema actually breaks. Genuine ties (both candidates type-valid) survive it -> still abstain.
  ANCHOR 5 (guardrail, NOT optional -- Pred C, the most load-bearing check): the deliberately-ambiguous
    fixtures must make the resolver ABSTAIN, not guess. A wrong guess converts a correct "no fact" into a
    WRONG-ENTITY fact -- strictly worse than the status quo, a direct hit on the zero-hallucination invariant.
    Run in the SAME pass as anchor 3.

GLASS-BOX / NO-LLM: the resolver is deterministic symbolic rules over the parser's own tag sequence + a small
  discourse-state list. It injects no facts -- it can only rebind a pronoun to a noun already present in the
  prior sentences, then re-run the SAME rule-based parser. Fully provenance-traceable.

SCOPE (research note (e) point 7): it/they pronouns referring to animals -- the pronouns the register actually
  exercises. he/she/him/her and 1st/2nd person are NOT resolved (speculative against a cue this register lacks).

FIXTURE CLASSES:
  unambiguous     -- exactly ONE number-compatible candidate in the window -> resolver BINDS it. [Prediction A]
  schema_resolvable -- 2 number-compatible candidates, but one is a type-violation the schema removes -> main
                       arm ABSTAINS (safe); the schema-tiebreak arm BINDS the type-valid one. [Prediction B]
  ambiguous       -- 2+ candidates survive BOTH number AND schema -> resolver MUST ABSTAIN. [Prediction C guardrail]
  unresolvable    -- ZERO number-compatible candidates in the window -> ABSTAIN (cannot resolve). [boundary]

METRICS (reported SEPARATELY):
  (a) LOCAL-ANTECEDENT resolution accuracy (Prediction A): over the unambiguous fixtures, fraction that BIND
      the correct antecedent (emitted triple == intended gold).
  (b) GUARDRAIL wrong-guess rate (Prediction C, MOST load-bearing): over the genuinely-tied fixtures, fraction
      that BOUND something instead of abstaining. Ship-gate: wrong_guess_rate < 0.30 (the STRICTER gate).
  (c) PRECISION preserved on the whole corpus: run the read->grow foundation loop over the full corpus
      (v2's non-coref rows + the discourse items); coref binding must not inject a wrong-entity fact.
      Reported gated (FULL), resolver-OFF (status quo), AND no-gate (isolates the resolver's raw precision).
  (d) COVERAGE lift: # coref rows that go abstain -> correct bound triple (vs the resolver-OFF status quo),
      without dropping precision.
  Pred B: how many number-ties the schema-type tie-breaker resolves (secondary arm).

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running; from the research note, NOT rounded up --
  Pred A P=0.45 deflated for register agreement-poverty; Pred C P=0.55; Pred B P=0.35):
  HARD-PASS (glass-box coref closes the local-antecedent gap WITHOUT injecting false facts):
    local_antecedent_resolution_acc >= 0.80 (Pred A bar) AND
    guardrail_wrong_guess_rate < 0.30 (Pred C ship-gate; the guardrail gates ship MORE strictly than anchor 3) AND
    FULL foundation_precision >= 0.90 AND FULL foundation_precision >= RESOLVER_OFF foundation_precision - 0.02
      (precision preserved -- turning the resolver on must not lose precision) AND
    coverage_lift >= 1 (the resolver actually resolves at least one row abstain->correct) AND
    accept_false_rate == 0.0 (type-violating FALSE injections still rejected) AND
    guardrail_wrong_guess_rate == 0.0 for the schema-tiebreak arm too (the tie-breaker must not start guessing).
  HARD-FAIL (the WORST outcome is guessing on ties = injecting false facts):
    guardrail_wrong_guess_rate >= 0.30 OR local_antecedent_resolution_acc < 0.40 (mis-binds) OR
    FULL foundation_precision < 0.85 OR FULL foundation_precision < RESOLVER_OFF foundation_precision - 0.05
      (turning the resolver on DROPS precision materially) OR accept_false_rate == 1.0.
  MIDDLE otherwise (partial: resolves some, abstains correctly, but not a clean pass -- report dominant class).

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (foundation grows fact-by-fact; wall < 20s).
Storage: SHARDED (one VSA vector per accepted fact). progress_logging = print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): RESOLVER_ON vs RESOLVER_OFF accepted-store hash differs
#     (the resolver actually injects the resolved coref facts); FULL vs NO_GATE differs (gate rejects false facts).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. Resolution is gated by PARSER rule + number agreement + discourse
#     ranking, NOT phasor noise (FHRR decode among ~25 concepts at N=1024 is ~26 sigma -> ~1.0).
# - discriminator survives scale: corpus is FIXED-size hand-authored discourse fixtures. Discriminators =
#     (1) resolver BINDS the correct antecedent on unambiguous pairs (deterministic, asserted at self-test),
#     (2) resolver ABSTAINS on genuine ties (the guardrail; asserted -- must NOT guess, even with the tie-breaker),
#     (3) the ambiguous fixtures create GENUINE ties: 2+ candidates survive number AND schema (asserted),
#     (4) RESOLVER_ON store != RESOLVER_OFF store (the lift is real), gate rejects the type-violating false fact,
#     (5) schema tie-breaker resolves the schema_resolvable class but NOT the genuine ties (Pred B, asserted).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON. Numbers tagged HYPOTHESIZED@prereg /
#     THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_coref_hobbs_centering_resolver_v1"

# --- GENUINE REUSE: the proven downstream + the v2 glass-box parser (imported, not rebuilt) ---
from experiments.exp_read_grow_foundation_endtoend_v1 import (
    N_DIM,
    RELATIONS,
    ENTITIES,
    build_typed_foundation,
    build_lexicon_train,
    FoundationStore,
    _svo_make_phasors,
    _encode_meaning,
    _decode_meaning,
    _learn_lexicon,
    _lexicon_top,
)
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (
    ie_extract,
    _tokenize,
    _tag_token,
    PROSE_CORPUS as V2_CORPUS,
)

# ---------------------------------------------------------------------------
# ANCHOR 2/3 primitives: discourse-memory mentions + the Hobbs/Centering resolver.
# ---------------------------------------------------------------------------
ROLE_RANK = {"subject": 0, "object": 1}
WINDOW_DEFAULT = 2                                # research note (e) point 4: keep the window narrow (N=1-2).


def _pron_number(p):
    """it -> singular, they -> plural. Out-of-scope pronouns -> None (not resolved -- scope is it/they)."""
    if p == "it":
        return "singular"
    if p == "they":
        return "plural"
    return None


def _noun_number(surface, lemma):
    """glass-box number: a noun is plural iff its surface form differs from its lemma (productive -s/-es)."""
    return "plural" if surface != lemma else "singular"


def _mentions_from_triples(triples, text, sidx):
    """(sidx, lemma, role, number) for each distinct subject/object noun in the emitted triples.
    role from the parser's OWN role assignment (already passive/coord/RC-correct); number from surface tokens."""
    num = {}
    for w in _tokenize(text):
        tag, lemma, _form = _tag_token(w)
        if tag == "NOUN":
            num[lemma] = _noun_number(w, lemma)
    seen = set()
    out = []
    for (s, r, o) in triples:
        for lemma, role in ((s, "subject"), (o, "object")):
            key = (lemma, role)
            if key in seen:
                continue
            seen.add(key)
            out.append({"sidx": sidx, "lemma": lemma, "role": role, "number": num.get(lemma, "singular")})
    return out


def _find_subject_pronoun(text):
    """first PRON token that precedes the first VERB (subject position). Returns (pron_lemma, tok_idx, toks)."""
    toks = _tokenize(text)
    tagged = [_tag_token(w) for w in toks]
    first_verb = None
    for i, (tag, _lm, _fm) in enumerate(tagged):
        if tag == "VERB":
            first_verb = i
            break
    for i, (tag, lemma, _fm) in enumerate(tagged):
        if tag == "PRON" and (first_verb is None or i < first_verb):
            return lemma, i, toks
    return None, None, toks


def _schema_tiebreak(pidx, toks, cands, store):
    """ANCHOR 4 (optional): among tied candidates, keep those whose substituted triple is NOT gate-REJECTed.
    Returns the single survivor lemma if exactly one, else None (tie not broken -> stays a correct abstain)."""
    ok = []
    for c in cands:
        st = list(toks)
        st[pidx] = c
        trs, _rule, _fr = ie_extract(" ".join(st))
        if not trs:
            continue
        rejected = False
        for tr in trs:
            dec, _info = store.gate(tr)
            if dec == "REJECT":
                rejected = True
                break
        if not rejected:
            ok.append(c)
    return ok[0] if len(ok) == 1 else None


def resolve_coref(text, memory, cur_sidx, window=WINDOW_DEFAULT, store=None, use_schema_tiebreak=False):
    """ANCHOR 3: deterministic Hobbs/Centering resolver over discourse memory. Returns (triples, info).
    Empty triples = ABSTAIN. Bind iff EXACTLY ONE distinct lemma survives number-agreement (precision-first);
    2+ survivors -> ABSTAIN (never guess). Bound triples carry provenance (antecedent + current pointers)."""
    pron, pidx, toks = _find_subject_pronoun(text)
    if pron is None:
        return [], {"reason": "NO_SUBJECT_PRONOUN"}
    pnum = _pron_number(pron)
    if pnum is None:
        return [], {"reason": "PRONOUN_OUT_OF_SCOPE", "pron": pron}
    cands = [m for m in memory if (cur_sidx - window) <= m["sidx"] <= (cur_sidx - 1)]
    survivors = [m for m in cands if m["number"] == pnum]        # HARD number-agreement filter (bonding stage)
    if not survivors:
        return [], {"reason": "NO_AGREEMENT_CANDIDATE", "pron": pron, "pnum": pnum, "n_cands": len(cands)}
    distinct = sorted(set(m["lemma"] for m in survivors))
    if len(distinct) >= 2:
        broke = None
        if use_schema_tiebreak and store is not None:
            broke = _schema_tiebreak(pidx, toks, distinct, store)
        if broke is None:
            return [], {"reason": "GENUINE_TIE", "pron": pron, "pnum": pnum, "tied": distinct,
                        "schema_tiebreak_used": bool(use_schema_tiebreak)}
        distinct = [broke]
    antecedent = distinct[0]
    ante_mentions = [m for m in survivors if m["lemma"] == antecedent]
    # recency-then-subject-role: most recent, subject preferred (for provenance -- lemma is already unique).
    ante_mentions.sort(key=lambda m: (-m["sidx"], ROLE_RANK[m["role"]]))
    ante_sidx = ante_mentions[0]["sidx"]
    sub = list(toks)
    sub[pidx] = antecedent
    triples, rule, _fr = ie_extract(" ".join(sub))
    if not triples:
        return [], {"reason": "POST_SUBSTITUTION_NO_PARSE", "antecedent": antecedent}
    info = {"reason": "BOUND", "antecedent": antecedent, "antecedent_sidx": ante_sidx,
            "current_sidx": cur_sidx, "pron": pron, "rule": "HOBBS_COREF", "base_rule": rule,
            "schema_broke": (len(survivors) > 0 and len(set(m["lemma"] for m in survivors)) >= 2)}
    return triples, info


# ---------------------------------------------------------------------------
# ANCHOR 1: rebuilt fixtures. Each item: kind, list of (sentence, gold_triples_for_that_sentence, role).
# role "ctx" = antecedent-establishing fact; "coref" = the pronoun sentence. For coref rows the gold is the
# INTENDED resolution (empty set == the correct answer is to ABSTAIN). "antecedent" = the lemma a correct
# resolver should bind (None for ambiguous/unresolvable).
# ---------------------------------------------------------------------------
def _S(text, gts, role):
    return {"text": text, "gts": set(gts), "role": role}


COREF_ITEMS = [
    # ---- UNAMBIGUOUS: exactly ONE number-compatible candidate in the window (single distractor is plural) ----
    {"kind": "unambiguous", "antecedent": "bird", "sents": [
        _S("The bird eats seeds.", [("bird", "eats", "seed")], "ctx"),
        _S("It chases the cat.", [("bird", "chases", "cat")], "coref")]},
    {"kind": "unambiguous", "antecedent": "frog", "sents": [
        _S("The frog eats worms.", [("frog", "eats", "worm")], "ctx"),
        _S("It lives in the pond.", [("frog", "lives_in", "pond")], "coref")]},
    {"kind": "unambiguous", "antecedent": "cow", "sents": [
        _S("The cow eats seeds.", [("cow", "eats", "seed")], "ctx"),
        _S("It lives in a field.", [("cow", "lives_in", "field")], "coref")]},
    # object antecedent, number-resolved (the plural subject is filtered out by number agreement).
    {"kind": "unambiguous", "antecedent": "cat", "sents": [
        _S("The dogs chase a cat.", [("dog", "chases", "cat")], "ctx"),
        _S("It eats the seed.", [("cat", "eats", "seed")], "coref")]},
    {"kind": "unambiguous", "antecedent": "cat", "sents": [
        _S("The birds chase a cat.", [("bird", "chases", "cat")], "ctx"),
        _S("It lives in the barn.", [("cat", "lives_in", "barn")], "coref")]},
    {"kind": "unambiguous", "antecedent": "owl", "sents": [
        _S("The owl eats worms.", [("owl", "eats", "worm")], "ctx"),
        _S("It chases the mouse.", [("owl", "chases", "mouse")], "coref")]},
    # they -> plural subject antecedent (the singular object is filtered out).
    {"kind": "unambiguous", "antecedent": "bird", "sents": [
        _S("The birds eat a seed.", [("bird", "eats", "seed")], "ctx"),
        _S("They chase the cat.", [("bird", "chases", "cat")], "coref")]},
    {"kind": "unambiguous", "antecedent": "dog", "sents": [
        _S("The dogs chase a cat.", [("dog", "chases", "cat")], "ctx"),
        _S("They eat bread.", [("dog", "eats", "bread")], "coref")]},
    {"kind": "unambiguous", "antecedent": "cat", "sents": [
        _S("The cats eat a worm.", [("cat", "eats", "worm")], "ctx"),
        _S("They chase the mouse.", [("cat", "chases", "mouse")], "coref")]},
    # recency + number: the earlier sentence's nouns are plural, only the recent singular subject matches "it".
    {"kind": "unambiguous", "antecedent": "cat", "sents": [
        _S("The dogs chase cats.", [("dog", "chases", "cat")], "ctx"),
        _S("The cat eats seeds.", [("cat", "eats", "seed")], "ctx"),
        _S("It chases the frog.", [("cat", "chases", "frog")], "coref")]},
    # ---- SCHEMA_RESOLVABLE (Pred B): 2 number-compatible candidates, one is a type-violation the schema removes.
    #      Main arm ABSTAINS (safe); schema-tiebreak arm BINDS the type-valid one. Gold = the type-valid reading.
    {"kind": "schema_resolvable", "antecedent": "bird", "sents": [
        _S("The bird eats a seed.", [("bird", "eats", "seed")], "ctx"),
        _S("It eats the worm.", [("bird", "eats", "worm")], "coref")]},   # seed-eats-worm is a type violation
    {"kind": "schema_resolvable", "antecedent": "cow", "sents": [
        _S("The cow eats grass.", [("cow", "eats", "grass")], "ctx"),
        _S("It chases the dog.", [("cow", "chases", "dog")], "coref")]},  # grass-chases-dog is a type violation
    # ---- AMBIGUOUS (genuine ties: 2+ candidates survive BOTH number AND schema -> MUST abstain) ----
    {"kind": "ambiguous", "antecedent": None, "sents": [
        _S("The cat and the dog eat grass.", [("cat", "eats", "grass"), ("dog", "eats", "grass")], "ctx"),
        _S("It chases the bird.", [], "coref")]},                         # cat vs dog (grass removed by schema)
    {"kind": "ambiguous", "antecedent": None, "sents": [
        _S("The dog chases the cat.", [("dog", "chases", "cat")], "ctx"),
        _S("It eats a seed.", [], "coref")]},                             # dog vs cat, both type-valid eaters
    {"kind": "ambiguous", "antecedent": None, "sents": [
        _S("The cat chases the bird.", [("cat", "chases", "bird")], "ctx"),
        _S("It eats a worm.", [], "coref")]},                             # cat vs bird, both type-valid
    {"kind": "ambiguous", "antecedent": None, "sents": [
        _S("The frog chases the mouse.", [("frog", "chases", "mouse")], "ctx"),
        _S("It eats a seed.", [], "coref")]},                             # frog vs mouse, both type-valid
    {"kind": "ambiguous", "antecedent": None, "sents": [
        _S("The birds and the cats chase a fish.", [("bird", "chases", "fish"), ("cat", "chases", "fish")], "ctx"),
        _S("They eat grass.", [], "coref")]},                             # bird vs cat, both type-valid
    {"kind": "ambiguous", "antecedent": None, "sents": [
        _S("The cows and the frogs eat seeds.", [("cow", "eats", "seed"), ("frog", "eats", "seed")], "ctx"),
        _S("They chase the cat.", [], "coref")]},                         # cow vs frog (seed removed by schema)
    # ---- UNRESOLVABLE (boundary: ZERO number-compatible candidates in the window) -> ABSTAIN ----
    {"kind": "unresolvable", "antecedent": None, "sents": [
        _S("The frogs eat seeds.", [("frog", "eats", "seed")], "ctx"),
        _S("It lives in the pond.", [], "coref")]},                       # "it" singular, only plural candidates
]

LOCAL_ANTECEDENT_KINDS = {"unambiguous"}                     # Prediction A denominator (bind the local antecedent)
AMBIGUOUS_KINDS = {"ambiguous"}                              # Prediction C denominator (must abstain)
SHOULD_ABSTAIN_KINDS = {"ambiguous", "unresolvable"}         # correct behaviour = empty triple list


# ---------------------------------------------------------------------------
# Corpus for metric (c): v2's non-coref rows (drop the 2 mis-specified coref rows) as single-sentence documents,
# then the discourse items as multi-sentence documents. Roles drive the accept/reject/recall classification.
# ---------------------------------------------------------------------------
def build_docs():
    docs = []
    for d in V2_CORPUS:
        if d["cls"] == "coreference":                       # ANCHOR 1: drop the old mis-specified coref rows
            continue
        docs.append([{"text": d["text"], "gts": set(d["gts"]), "role": d["role"], "label": d["label"],
                      "residual": d["residual"], "is_coref": False, "kind": None}])
    for item in COREF_ITEMS:
        doc = []
        for s in item["sents"]:
            is_coref = (s["role"] == "coref")
            doc.append({"text": s["text"], "gts": set(s["gts"]), "role": ("coref" if is_coref else "probe"),
                        "label": "TRUE_ACCEPT", "residual": None, "is_coref": is_coref, "kind": item["kind"]})
        docs.append(doc)
    return docs


def _accept_reject_recall_sets(docs):
    should_accept = set()
    should_reject = set()
    required_recall = set()
    for doc in docs:
        for s in doc:
            if s["role"] == "false":
                should_reject |= s["gts"]
            elif s["residual"] is None:
                should_accept |= s["gts"]                   # ctx + intended coref golds (ambiguous gts is empty)
            if s["role"] in ("required", "novel", "hold"):
                required_recall |= s["gts"]
    return should_accept, should_reject, required_recall


def _grounded_store(seed=0):
    """A concept-level FoundationStore grounded on the corpus's in-schema TRUE facts, for the schema tie-breaker's
    gate() type-checks (no VSA/lexicon needed -- gate() operates on concept-string triples directly)."""
    foundation = build_typed_foundation()
    C = _svo_make_phasors(np.random.default_rng(seed), len(foundation["concept_ids"]), N_DIM)
    roles = _svo_make_phasors(np.random.default_rng(seed + 1), 3, N_DIM)
    store = FoundationStore(C, roles, foundation["cid_idx"])
    for doc in build_docs():
        for s in doc:
            if s["role"] == "false" or s["residual"] is not None:
                continue
            for tr in ie_extract(s["text"])[0]:
                if tr[1] in RELATIONS and tr[0] in ENTITIES and tr[2] in ENTITIES and tr[0] != tr[2]:
                    store.commit(tr)
    return store


# ---------------------------------------------------------------------------
# METRIC (a)/(b)/(d): deterministic coref analysis (seed-independent -- pure parser + discourse memory).
# ---------------------------------------------------------------------------
def analyze_coref(window=WINDOW_DEFAULT, use_schema_tiebreak=False, resolver_on=True, store=None):
    if use_schema_tiebreak and store is None:
        store = _grounded_store()
    results = []
    n_ties_broken_by_schema = 0
    for item in COREF_ITEMS:
        memory = []
        bound = None
        info = None
        for sidx, s in enumerate(item["sents"]):
            text = s["text"]
            triples, rule, _fr = ie_extract(text)
            if rule == "COREF_UNRESOLVED":
                if resolver_on:
                    triples, info = resolve_coref(text, memory, sidx, window=window, store=store,
                                                  use_schema_tiebreak=use_schema_tiebreak)
                    if use_schema_tiebreak and info.get("reason") == "BOUND" and info.get("schema_broke"):
                        n_ties_broken_by_schema += 1
                else:
                    triples, info = [], {"reason": "RESOLVER_OFF_ABSTAIN"}
                bound = triples
            memory.extend(_mentions_from_triples(triples, text, sidx))
        gold = item["sents"][-1]["gts"]
        emitted = set(bound) if bound else set()
        if item["kind"] in SHOULD_ABSTAIN_KINDS:
            correct = (len(emitted) == 0)
        else:
            correct = (emitted == gold)
        results.append({"kind": item["kind"], "text": item["sents"][-1]["text"],
                        "intended_gold": sorted(list(t) for t in gold),
                        "emitted": sorted(list(t) for t in emitted),
                        "expected_antecedent": item.get("antecedent"), "info": info, "correct": correct})

    def _subset(kinds):
        return [r for r in results if r["kind"] in kinds]

    unamb = _subset({"unambiguous"})
    amb = _subset(AMBIGUOUS_KINDS)
    sch = _subset({"schema_resolvable"})
    unres = _subset({"unresolvable"})

    la_acc = (sum(r["correct"] for r in unamb) / float(len(unamb))) if unamb else 0.0
    n_amb_guessed = sum(1 for r in amb if len(r["emitted"]) > 0)
    wrong_guess_rate = (n_amb_guessed / float(len(amb))) if amb else 0.0
    sch_bound = sum(1 for r in sch if len(r["emitted"]) > 0 and r["correct"])
    coverage_lift = sum(1 for r in unamb if r["correct"])
    return {
        "local_antecedent_resolution_acc": la_acc,
        "guardrail_wrong_guess_rate": wrong_guess_rate,
        "guardrail_abstain_rate": 1.0 - wrong_guess_rate,
        "coverage_lift": coverage_lift,
        "n_unambiguous": len(unamb),
        "n_ambiguous": len(amb),
        "n_ambiguous_guessed": n_amb_guessed,
        "n_schema_resolvable": len(sch),
        "n_schema_resolvable_bound": sch_bound,
        "n_unresolvable": len(unres),
        "n_unresolvable_abstained": sum(1 for r in unres if r["correct"]),
        "n_ties_broken_by_schema": n_ties_broken_by_schema,
        "per_item": results,
    }


def _count_genuine_ties(window=WINDOW_DEFAULT):
    """DISCRIMINATOR: each ambiguous fixture must leave 2+ candidates AFTER number AND schema filtering."""
    store = _grounded_store()
    n = 0
    for item in COREF_ITEMS:
        if item["kind"] != "ambiguous":
            continue
        memory = []
        tie = False
        for sidx, s in enumerate(item["sents"]):
            triples, rule, _fr = ie_extract(s["text"])
            if rule == "COREF_UNRESOLVED":
                pron, pidx, toks = _find_subject_pronoun(s["text"])
                pnum = _pron_number(pron)
                cands = [m for m in memory if (sidx - window) <= m["sidx"] <= (sidx - 1)]
                distinct = sorted(set(m["lemma"] for m in cands if m["number"] == pnum))
                if len(distinct) >= 2:
                    survive = []
                    for c in distinct:
                        st = list(toks)
                        st[pidx] = c
                        trs, _r, _f = ie_extract(" ".join(st))
                        if trs and all(store.gate(t)[0] != "REJECT" for t in trs):
                            survive.append(c)
                    if len(survive) >= 2:
                        tie = True
            memory.extend(_mentions_from_triples(triples, s["text"], sidx))
        if tie:
            n += 1
    return n


# ---------------------------------------------------------------------------
# METRIC (c): discourse-aware read->grow loop over the full corpus (VSA store precision/recall/query).
# Mirrors v2 run_loop's encode/gate/commit block; adds per-document discourse memory + the coref resolver.
# ---------------------------------------------------------------------------
def run_discourse_loop(seed, use_gate, resolver_on, window=WINDOW_DEFAULT, lexicon_kind="learned",
                       use_schema_tiebreak=False):
    rng = np.random.default_rng(seed)
    scene_rng = np.random.default_rng(seed * 7 + 1)
    foundation = build_typed_foundation()
    cid_idx = foundation["cid_idx"]
    n_concept = len(foundation["concept_ids"])
    C = _svo_make_phasors(rng, n_concept, N_DIM)
    roles = _svo_make_phasors(rng, 3, N_DIM)
    inv = {v: k for k, v in cid_idx.items()}

    if lexicon_kind == "oracle":
        top_map = dict(foundation["true_map"])
    elif lexicon_kind == "random":
        top_map = {w: foundation["concept_ids"][rng.integers(n_concept)] for w in foundation["words"]}
    else:
        train = build_lexicon_train(rng, foundation, n_per_word_min=14)
        assoc, _ = _learn_lexicon(train, foundation, scene_rng, role_gating=True, soft_me=True, fast_map=True,
                                  n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0)
        top_map = _lexicon_top(assoc, foundation)
    tm = foundation["true_map"]
    mapping_acc = float(np.mean([top_map.get(w) == tm[w] for w in foundation["words"]]))

    store = FoundationStore(C, roles, cid_idx)
    docs = build_docs()
    should_accept, should_reject, required_recall = _accept_reject_recall_sets(docs)

    n_coref_bound = 0
    n_coref_abstain = 0
    for doc in docs:
        memory = []
        for sidx, s in enumerate(doc):
            text = s["text"]
            triples, rule, _fr = ie_extract(text)
            if rule == "COREF_UNRESOLVED":
                if resolver_on:
                    triples, _info = resolve_coref(text, memory, sidx, window=window, store=store,
                                                   use_schema_tiebreak=use_schema_tiebreak)
                else:
                    triples = []
                if s["is_coref"]:
                    if triples:
                        n_coref_bound += 1
                    else:
                        n_coref_abstain += 1
            for parsed in triples:                          # VSA decode + gate + commit (mirrors v2 run_loop)
                try:
                    learned = tuple(top_map.get(w) for w in parsed)
                    filler_idx = tuple(cid_idx[c] if c in cid_idx else 0 for c in learned)
                    M = _encode_meaning(filler_idx, C, roles)
                    dec_idx = _decode_meaning(M, C, roles, 3)
                    cand = tuple(inv[i] for i in dec_idx)
                except Exception:
                    continue
                well_formed = (cand[1] in RELATIONS and cand[0] != cand[2]
                               and cand[0] in ENTITIES and cand[2] in ENTITIES)
                if not well_formed:
                    continue
                if use_gate:
                    d, info = store.gate(cand)
                    store.decisions.append({"stage": "read", **info, "decision": d})
                    if d == "ACCEPT":
                        store.commit(cand)
                    elif d == "HOLD":
                        store.held.append([cand, 0])
                    store.reeval_holds()
                else:
                    store.commit(cand)
            memory.extend(_mentions_from_triples(triples, text, sidx))
    if use_gate:
        store.reeval_holds()

    accepted = store.accepted
    n_false = len(accepted & should_reject)
    precision = (len(accepted & should_accept) / float(len(accepted))) if accepted else 0.0
    true_recall = (len(accepted & required_recall) / float(len(required_recall))) if required_recall else 0.0
    accept_false_rate = (n_false / float(len(should_reject))) if should_reject else 0.0

    obj_sets = defaultdict(set)
    for (s, r, o) in accepted:
        if (s, r, o) in should_accept:
            obj_sets[(s, r)].add(o)
    q_total = 0
    q_ok = 0
    for (s, r), objs in sorted(obj_sets.items()):
        if store.query(s, r) in objs:
            q_ok += 1
        q_total += 1
    query_acc = (q_ok / float(q_total)) if q_total else 0.0

    return {
        "seed": seed, "use_gate": use_gate, "resolver_on": resolver_on, "lexicon_kind": lexicon_kind,
        "mapping_acc": mapping_acc, "n_accepted": len(accepted),
        "foundation_precision": precision, "true_recall": true_recall,
        "accept_false_rate": accept_false_rate, "n_false_in_store": n_false, "query_acc": query_acc,
        "n_coref_bound": n_coref_bound, "n_coref_abstain": n_coref_abstain,
        "accepted_hash": store.accepted_hash(), "accepted_sorted": sorted(accepted),
    }


def avg_arm(seeds, use_gate, resolver_on, window=WINDOW_DEFAULT, lexicon_kind="learned", use_schema_tiebreak=False):
    runs = [run_discourse_loop(s, use_gate, resolver_on, window, lexicon_kind, use_schema_tiebreak) for s in seeds]
    keys = ["mapping_acc", "foundation_precision", "true_recall", "accept_false_rate", "query_acc",
            "n_accepted", "n_false_in_store", "n_coref_bound", "n_coref_abstain"]
    out = {k: float(np.mean([r[k] for r in runs])) for k in keys}
    out["per_seed"] = runs
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg).
# ---------------------------------------------------------------------------
def compute_verdict(coref, coref_tb, full, off, nogate):
    la = coref["local_antecedent_resolution_acc"]
    wg = coref["guardrail_wrong_guess_rate"]
    wg_tb = coref_tb["guardrail_wrong_guess_rate"]
    lift = coref["coverage_lift"]
    fp = full["foundation_precision"]
    fp_off = off["foundation_precision"]
    afr = full["accept_false_rate"]

    hp = (
        la >= 0.80 and wg < 0.30 and wg_tb == 0.0 and
        fp >= 0.90 and fp >= (fp_off - 0.02) and lift >= 1 and afr == 0.0
    )
    hf = (
        wg >= 0.30 or la < 0.40 or fp < 0.85 or fp < (fp_off - 0.05) or afr == 1.0
    )
    tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    localize = []
    if la < 0.80:
        localize.append("local-antecedent resolution below 0.80 (%.3f) -- number filter / parser miss" % la)
    if wg >= 0.30:
        localize.append("GUARDRAIL BREACH: resolver guesses on %.0f%% of genuine ties (injects wrong-entity facts)" % (wg * 100))
    elif wg > 0.0:
        localize.append("guardrail: resolver guessed on %.0f%% of ties (under the 30%% gate but not clean)" % (wg * 100))
    if wg_tb > 0.0:
        localize.append("schema tie-breaker started GUESSING on genuine ties (wrong_guess=%.2f) -- over-eager" % wg_tb)
    if fp < fp_off - 0.02:
        localize.append("precision DROPPED turning resolver on (%.3f vs OFF %.3f)" % (fp, fp_off))
    if lift < 1:
        localize.append("no coverage lift (resolver resolved nothing)")
    weakest = localize if localize else ["none (local antecedents bound, ties abstained, precision preserved)"]

    msg = (f"{tier} | COREF local_antecedent_acc={la:.3f} ({coref['coverage_lift']}/{coref['n_unambiguous']} bound) | "
           f"GUARDRAIL wrong_guess_rate={wg:.3f} (abstain={coref['guardrail_abstain_rate']:.3f} on {coref['n_ambiguous']} ties; "
           f"tiebreak-arm wrong_guess={wg_tb:.3f}) | Pred B schema broke {coref_tb['n_ties_broken_by_schema']} of "
           f"{coref['n_schema_resolvable']} schema-ties | precision FULL={fp:.3f} vs OFF={fp_off:.3f} vs "
           f"NOGATE={nogate['foundation_precision']:.3f} | recall={full['true_recall']:.3f} query={full['query_acc']:.3f} "
           f"accept_false={afr:.3f} | coverage: FULL bound={full['n_coref_bound']:.1f} vs OFF bound={off['n_coref_bound']:.1f} | "
           f"weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_coref_hobbs_centering_resolver_v1",
           "smoke": "exp_read_coref_hobbs_centering_resolver_v1_smoke",
           "self_test": "exp_read_coref_hobbs_centering_resolver_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminators FIRE.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (ie_extract + resolver + discourse memory + FoundationStore)...",
          flush=True)
    # (1) discourse-memory mention extraction reads role + number off the parser's own tags.
    m = _mentions_from_triples([("bird", "eats", "seed")], "The bird eats seeds.", 0)
    assert {(x["lemma"], x["role"], x["number"]) for x in m} == {("bird", "subject", "singular"),
                                                                 ("seed", "object", "plural")}, "mention/number wrong"

    # (2) ANCHOR 3: resolver BINDS when exactly one number-compatible candidate survives.
    mem = _mentions_from_triples([("bird", "eats", "seed")], "The bird eats seeds.", 0)
    tr, info = resolve_coref("It chases the cat.", mem, 1)
    assert set(tr) == {("bird", "chases", "cat")}, f"unambiguous bind failed: {tr}"
    assert info["reason"] == "BOUND" and info["antecedent"] == "bird" and info["antecedent_sidx"] == 0, \
        f"provenance wrong: {info}"

    # (3) ANCHOR 3: number filter removes a plural subject -> binds the singular object.
    mem2 = _mentions_from_triples([("dog", "chases", "cat")], "The dogs chase a cat.", 0)
    tr2, _i2 = resolve_coref("It eats the seed.", mem2, 1)
    assert set(tr2) == {("cat", "eats", "seed")}, f"number filter (bind object) failed: {tr2}"

    # (4) ANCHOR 3: they -> plural antecedent (singular object filtered out).
    mem3 = _mentions_from_triples([("bird", "eats", "seed")], "The birds eat a seed.", 0)
    tr3, _i3 = resolve_coref("They chase the cat.", mem3, 1)
    assert set(tr3) == {("bird", "chases", "cat")}, f"they plural bind failed: {tr3}"

    # (5) ANCHOR 5 GUARDRAIL: genuine tie (two same-number type-valid candidates) -> ABSTAIN (must NOT guess).
    memt = _mentions_from_triples([("dog", "chases", "cat")], "The dog chases the cat.", 0)
    trt, infot = resolve_coref("It eats a seed.", memt, 1)
    assert trt == [], f"GUARDRAIL FAIL: resolver guessed on a genuine tie instead of abstaining: {trt}"
    assert infot["reason"] == "GENUINE_TIE" and set(infot["tied"]) == {"cat", "dog"}, f"tie not detected: {infot}"

    # (6) number tie present but NO gender cue -> abstain even with subject in play (precision-first, no override).
    memp = _mentions_from_triples([("bird", "eats", "seed")], "The bird eats a seed.", 0)
    trp, infop = resolve_coref("It eats the worm.", memp, 1)
    assert trp == [], f"same-number subj+obj must abstain WITHOUT schema tie-break: {trp}"

    # (7) ANCHOR 4 (Pred B): the schema tie-breaker resolves a schema_resolvable tie (seed cannot eat) ...
    store = _grounded_store()
    trs, infos = resolve_coref("It eats the worm.", memp, 1, store=store, use_schema_tiebreak=True)
    assert set(trs) == {("bird", "eats", "worm")}, f"schema tie-break failed to bind bird: {trs}"
    # ... but does NOT break a GENUINE tie (both type-valid) -> still abstains.
    trg, infog = resolve_coref("It eats a seed.", memt, 1, store=store, use_schema_tiebreak=True)
    assert trg == [], f"schema tie-break WRONGLY guessed on a genuine tie: {trg}"

    # (8) no antecedent / out-of-scope pronoun -> abstain.
    assert resolve_coref("It eats the worm.", [], 0)[0] == [], "no-antecedent should abstain"
    assert resolve_coref("He eats the worm.", [{"sidx": 0, "lemma": "cat", "role": "subject", "number": "singular"}], 1)[0] == [], \
        "out-of-scope pronoun (he) should abstain"

    # (9) DISCRIMINATOR: every ambiguous fixture is a GENUINE tie (2+ survive number AND schema).
    n_ties = _count_genuine_ties()
    n_amb = sum(1 for it in COREF_ITEMS if it["kind"] == "ambiguous")
    assert n_ties == n_amb, f"not all ambiguous fixtures are genuine ties: {n_ties}/{n_amb}"

    # (10) coref analysis (main arm + tie-break arm).
    ca = analyze_coref()
    ca_tb = analyze_coref(use_schema_tiebreak=True)
    assert ca["local_antecedent_resolution_acc"] >= 0.80, f"resolution acc too low: {ca['local_antecedent_resolution_acc']}"
    assert ca["guardrail_wrong_guess_rate"] < 0.30, f"guardrail wrong-guess too high: {ca['guardrail_wrong_guess_rate']}"
    assert ca_tb["guardrail_wrong_guess_rate"] == 0.0, f"tie-break arm guessed on ties: {ca_tb['guardrail_wrong_guess_rate']}"
    assert ca_tb["n_ties_broken_by_schema"] >= 1, "schema tie-breaker broke no schema_resolvable ties (Pred B null)"
    assert ca["coverage_lift"] >= 1, "no coverage lift"

    # (11) REAL end-to-end store loop: RESOLVER_ON injects coref facts (store != OFF); gate rejects false.
    full = run_discourse_loop(11, use_gate=True, resolver_on=True)
    off = run_discourse_loop(11, use_gate=True, resolver_on=False)
    nogate = run_discourse_loop(11, use_gate=False, resolver_on=True)
    assert full["accepted_hash"] != off["accepted_hash"], \
        "META_RULE_AF: RESOLVER_ON and RESOLVER_OFF stores bit-identical (resolver injected nothing)"
    assert full["n_coref_bound"] >= 1, "resolver bound no coref rows in the store loop"
    assert nogate["n_false_in_store"] >= 1, "smoke-vacuous: NO_GATE did not admit the type-violating false fact"
    assert full["n_false_in_store"] <= nogate["n_false_in_store"], "gate did not reduce false facts"
    assert full["foundation_precision"] >= 0.85, f"FULL precision too low: {full['foundation_precision']}"
    assert full["foundation_precision"] >= off["foundation_precision"] - 0.05, "resolver dropped precision materially"

    print(f"[self_test] PASS | local_antecedent_acc={ca['local_antecedent_resolution_acc']:.3f} "
          f"({ca['coverage_lift']}/{ca['n_unambiguous']}) | guardrail wrong_guess={ca['guardrail_wrong_guess_rate']:.3f} "
          f"(tiebreak {ca_tb['guardrail_wrong_guess_rate']:.3f}) on {ca['n_ambiguous']} ties | "
          f"PredB schema broke {ca_tb['n_ties_broken_by_schema']}/{ca['n_schema_resolvable']} | "
          f"FULL prec={full['foundation_precision']:.3f} vs OFF={off['foundation_precision']:.3f} | "
          f"coref_bound={full['n_coref_bound']}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [11, 23] if run_mode == "smoke" else [11, 23, 37, 41, 53]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * 3
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[coref_v1] run_mode={run_mode} seeds={seeds} coref_items={len(COREF_ITEMS)} window={WINDOW_DEFAULT}",
          flush=True)

    coref = analyze_coref(window=WINDOW_DEFAULT, use_schema_tiebreak=False, resolver_on=True)
    coref_tb = analyze_coref(window=WINDOW_DEFAULT, use_schema_tiebreak=True, resolver_on=True)
    print(f"[coref_v1] METRIC(a) local_antecedent_resolution_acc={coref['local_antecedent_resolution_acc']:.3f} "
          f"({coref['coverage_lift']}/{coref['n_unambiguous']} unambiguous rows bound)", flush=True)
    print(f"[coref_v1] METRIC(b) GUARDRAIL wrong_guess_rate={coref['guardrail_wrong_guess_rate']:.3f} "
          f"abstain_rate={coref['guardrail_abstain_rate']:.3f} on {coref['n_ambiguous']} genuine ties "
          f"(guessed {coref['n_ambiguous_guessed']}); tie-break arm wrong_guess={coref_tb['guardrail_wrong_guess_rate']:.3f}",
          flush=True)
    print(f"[coref_v1] Pred B schema-type tie-breaker broke {coref_tb['n_ties_broken_by_schema']} of "
          f"{coref['n_schema_resolvable']} schema-resolvable ties; unresolvable abstained "
          f"{coref['n_unresolvable_abstained']}/{coref['n_unresolvable']}", flush=True)

    full = avg_arm(seeds, use_gate=True, resolver_on=True)
    off = avg_arm(seeds, use_gate=True, resolver_on=False)
    nogate = avg_arm(seeds, use_gate=False, resolver_on=True)
    print(f"[coref_v1] METRIC(c) FULL precision={full['foundation_precision']:.3f} vs RESOLVER_OFF={off['foundation_precision']:.3f} "
          f"vs NO_GATE={nogate['foundation_precision']:.3f} | recall={full['true_recall']:.3f} query={full['query_acc']:.3f} "
          f"accept_false={full['accept_false_rate']:.3f}", flush=True)
    print(f"[coref_v1] METRIC(d) coverage: FULL bound={full['n_coref_bound']:.1f} abstain={full['n_coref_abstain']:.1f} "
          f"vs OFF bound={off['n_coref_bound']:.1f} abstain={off['n_coref_abstain']:.1f}", flush=True)

    tier, msg, weakest = compute_verdict(coref, coref_tb, full, off, nogate)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "per_seed"}

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "run_mode": run_mode, "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "seeds": seeds, "window": WINDOW_DEFAULT,
        "n_coref_items": len(COREF_ITEMS), "expected_n_units": expected_n_units, "weakest_interface": weakest,
        # METRIC (a) -- local-antecedent resolution (Prediction A).
        "metric_a_local_antecedent_resolution_acc": coref["local_antecedent_resolution_acc"],
        "metric_a_n_unambiguous": coref["n_unambiguous"],
        # METRIC (b) -- the guardrail (Prediction C, most load-bearing).
        "metric_b_guardrail_wrong_guess_rate": coref["guardrail_wrong_guess_rate"],
        "metric_b_guardrail_abstain_rate": coref["guardrail_abstain_rate"],
        "metric_b_guardrail_wrong_guess_rate_tiebreak_arm": coref_tb["guardrail_wrong_guess_rate"],
        "metric_b_n_ambiguous_ties": coref["n_ambiguous"],
        "metric_b_n_ambiguous_guessed": coref["n_ambiguous_guessed"],
        # METRIC (c) -- precision preserved on the whole corpus.
        "metric_c_foundation_precision_full": full["foundation_precision"],
        "metric_c_foundation_precision_resolver_off": off["foundation_precision"],
        "metric_c_foundation_precision_nogate": nogate["foundation_precision"],
        "metric_c_precision_delta_on_minus_off": full["foundation_precision"] - off["foundation_precision"],
        "metric_c_true_recall": full["true_recall"], "metric_c_query_acc": full["query_acc"],
        "metric_c_accept_false_rate": full["accept_false_rate"],
        # METRIC (d) -- coverage lift.
        "metric_d_coverage_lift": coref["coverage_lift"],
        "metric_d_full_coref_bound": full["n_coref_bound"], "metric_d_full_coref_abstain": full["n_coref_abstain"],
        "metric_d_off_coref_bound": off["n_coref_bound"],
        # Pred B + boundary.
        "pred_b_schema_ties_broken": coref_tb["n_ties_broken_by_schema"],
        "pred_b_n_schema_resolvable": coref["n_schema_resolvable"],
        "n_unresolvable_abstained": coref["n_unresolvable_abstained"], "n_unresolvable": coref["n_unresolvable"],
        "coref_per_item": coref["per_item"],
        "arms": {"FULL_RESOLVER_ON_GATE": strip(full), "RESOLVER_OFF_GATE": strip(off),
                 "RESOLVER_ON_NO_GATE": strip(nogate)},
        "full_per_seed": full["per_seed"],
        "prereg": {
            "hard_pass": "local_antecedent_acc>=0.80 & guardrail_wrong_guess_rate<0.30 & tiebreak-arm wrong_guess==0 & "
                         "FULL precision>=0.90 & FULL precision>=OFF-0.02 & coverage_lift>=1 & accept_false_rate==0",
            "hard_fail": "guardrail_wrong_guess_rate>=0.30 | local_antecedent_acc<0.40 | FULL precision<0.85 | "
                         "FULL precision<OFF-0.05 | accept_false_rate==1.0",
            "middle": "otherwise (partial; report dominant class)",
            "pred_a_P": 0.45, "pred_c_P": 0.55, "pred_b_P": 0.35,
            "scope": "it/they pronouns referring to animals (he/she/1st/2nd person NOT resolved)",
            "resolver": "recency-then-subject-role rank -> number-agreement filter -> bind-on-exactly-one / abstain-on-0-or-2+",
            "window": WINDOW_DEFAULT,
            "compute_architecture": "sequential-CPU (foundation grows fact-by-fact; discourse memory per document)",
            "storage_strategy": "sharded (one VSA vector per accepted fact)",
            "parser_class": "fully-symbolic glass-box Hobbs/Centering resolver over discourse memory (NO LLM)",
            "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract", "resolve_coref", "analyze_coref", "run_discourse_loop",
                                         "learn_lexicon"],
            "crlb_n/a": "no quantitative noise floor; resolution gated by number agreement + discourse ranking",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[coref_v1] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[coref_v1] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
