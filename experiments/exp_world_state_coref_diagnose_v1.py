"""exp_world_state_coref_diagnose_v1 -- PHASE 0 diagnostic for the problem
`the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what`.

PURPOSE (VERIFY BEFORE YOU START + the user's 'understand the wall deeply'): the parent problem located the
open-text who-has-what residual as "81% of transfer agents are pronouns". Before wiring the reader's OWN coref
into the register, decompose that 81% by PRONOUN CLASS, because the reader's coref (hdlab/coref.py TARGET_PRONOUNS)
resolves ONLY gendered-singular 3rd-person PERSON pronouns (he/she/him/her/his). It does NOT resolve:
  * FIRST/SECOND person  I/we/you/me/us   -> DEIXIS (the deictic center / narrator), not anaphora
  * OBJECT pronoun       it/they/them      -> object anaphora (out of the he/she scope)
So "wire the reader's coref" can only address the he/she share. This cell measures each share on:
  A) MCScript2 (first-person everyday scripts, the parent corpus)  -- reuse the parent realtext extractor
  B) LitBank coref-CoNLL (third-person literary, the reader's OWN coref eval corpus, WITH gold clusters)
and for LitBank reports how many real transfers have a gold-mention agent the reader could bind, split by class.

This tells us (1) how much of the gap the reader's existing coref can close, (2) how much needs a brain-faithful
DEIXIS anchor (I->narrator) + object anaphora (it->theme) BUILD, and (3) whether LitBank is transfer-dense enough
for the held-out who-has-what measurement. Glass-box: substrate's OWN parser (pos_tagger+arc_parser), NO spaCy/LLM.
# KB_REFERENT: data/corpora/mcscript2/extracted/train-data.xml
# KB_REFERENT: data/corpora/litbank_coref_conll
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_world_state_realtext_mcscript_v1 as RT

ANCHOR = "world_state_coref_diagnose_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
LITBANK_DIR = os.path.join(REPO, "data", "corpora", "litbank_coref_conll")

# pronoun classes -- keyed on the reader's ACTUAL coref scope (hdlab/coref.py TARGET_PRONOUNS = he/she family).
FIRST_SECOND = {"i", "we", "me", "us", "you", "myself", "ourselves", "yourself"}
THIRD_PERSON = {"he", "she", "him", "her", "his", "hers", "himself", "herself"}   # reader CAN resolve (he/she)
OBJECT_PRON = {"it", "they", "them", "its", "their", "theirs", "itself", "themselves"}
ALL_PRON = FIRST_SECOND | THIRD_PERSON | OBJECT_PRON


def classify_pron(w):
    w = (w or "").lower()
    if w in FIRST_SECOND:
        return "first_second"
    if w in THIRD_PERSON:
        return "third_person_reader_scope"
    if w in OBJECT_PRON:
        return "object_or_plural"
    return None


# --------------------------------------------------------------------------- A) MCScript2
def diagnose_mcscript(gen, lex, lemma_word, n):
    sents = RT._sentences()
    verbforms = set()
    for v in lex:
        verbforms |= {v, v + "s", v + "ed", v + "d", (v[:-1] + "ied" if v.endswith("y") else v + "ed")}
    cand = [s for s in sents if verbforms & {w.lower().strip(".,!?;:") for w in s.split()}][:n]
    agent_class = Counter(); n_inst = 0; have_agent = 0; theme_pron = Counter(); have_theme = 0
    for s in cand:
        try:
            cr = gen.generate(s)
        except Exception:
            continue
        for it in RT.extract_ops(cr, lex, lemma_word):
            n_inst += 1
            if it["AGENT"]:
                have_agent += 1
                c = classify_pron(it["AGENT"])
                agent_class[c if c else "nominal_name"] += 1
            if it["PATIENT"]:
                have_theme += 1
                c = classify_pron(it["PATIENT"])
                theme_pron[c if c else "nominal_name"] += 1
    return {
        "n_candidate_sentences": len(cand), "n_transfer_instances": n_inst,
        "have_agent": have_agent, "have_theme": have_theme,
        "agent_class_counts": dict(agent_class),
        "agent_class_frac": {k: round(v / have_agent, 3) for k, v in agent_class.items()} if have_agent else {},
        "theme_class_counts": dict(theme_pron),
        "theme_pron_frac": round(sum(v for k, v in theme_pron.items() if k in
                                     ("first_second", "third_person_reader_scope", "object_or_plural")) / have_theme, 3)
        if have_theme else None,
    }


# --------------------------------------------------------------------------- B) LitBank (gold coref)
def _mention_pos_map(mentions):
    """(sent_idx, within_sentence_wtok) -> mention dict, expanding each mention's contiguous span."""
    pos = {}
    for m in mentions:
        span_len = m["gtok_end"] - m["gtok_start"]
        for k in range(span_len + 1):
            pos[(m["sent_idx"], m["wtok_start"] + k)] = m
    return pos


def _sentences_from_conll(path):
    """Reconstruct per-sentence token lists from a coref CoNLL (blank line = sentence boundary), matching
    parse_litbank_conll's sentence indexing so parser token i aligns to within-sentence wtok i."""
    sents = []; cur = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                if cur:
                    sents.append(cur); cur = []
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 4:
                continue
            cur.append(cols[3])
    if cur:
        sents.append(cur)
    return sents


def diagnose_litbank(gen, lex, lemma_word, n_docs):
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets, load_name_gender
    gaz = load_name_gender()
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))[:n_docs]
    tot = Counter()
    agent_gold_class = Counter()      # of transfers whose agent token IS a gold mention, by pron class
    agent_nogold = 0
    n_docs_used = 0
    per_doc = []
    for path in files:
        mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
        if not mentions:
            continue
        posmap = _mention_pos_map(mentions)
        toks_by_sent = _sentences_from_conll(path)
        if len(toks_by_sent) != n_sents:
            # sentence reconstruction disagreement -> skip doc (keep alignment strict)
            per_doc.append({"doc": os.path.basename(path), "SKIP_sent_mismatch": [len(toks_by_sent), n_sents]})
            continue
        n_docs_used += 1
        d_inst = 0; d_agent_gold = 0
        for si, toks in enumerate(toks_by_sent):
            if not toks:
                continue
            try:
                cr = gen.generate(" ".join(toks))
            except Exception:
                continue
            if len(cr.tokens) != len(toks):
                continue    # tokenization drift on this sentence -> skip (strict alignment)
            for it in RT.extract_ops(cr, lex, lemma_word):
                # locate the agent token index within the sentence via the parse (re-derive from extract_ops? it
                # returns only strings). Recompute agent token position here for alignment.
                pass
            # re-extract WITH token indices (extract_ops drops them) -- inline minimal version:
            for inst in _extract_ops_with_idx(cr, lex, lemma_word):
                d_inst += 1; tot["transfer_instances"] += 1
                w = inst["agent_wtok"]
                if w is None:
                    continue
                m = posmap.get((si, w))
                if m is None:
                    agent_nogold += 1
                    tot["agent_no_gold_mention"] += 1
                    continue
                d_agent_gold += 1
                tot["agent_is_gold_mention"] += 1
                if m["is_pronoun"]:
                    c = classify_pron(m["head"])
                    agent_gold_class[c if c else "other_pron"] += 1
                else:
                    agent_gold_class["nominal_name"] += 1
        per_doc.append({"doc": os.path.basename(path), "transfers": d_inst, "agent_gold_mentions": d_agent_gold})
    return {
        "n_docs_used": n_docs_used, "totals": dict(tot),
        "agent_gold_class_counts": dict(agent_gold_class),
        "agent_gold_class_frac": {k: round(v / max(1, sum(agent_gold_class.values())), 3)
                                  for k, v in agent_gold_class.items()},
        "per_doc": per_doc[:12],
    }


def _extract_ops_with_idx(cr, lex, lemma_word):
    """RT.extract_ops but also returns the agent's within-sentence token index (0-based wtok) for gold-mention
    alignment. Mirrors RT.extract_ops exactly for role picking (subj[-1]) so counts match the parent arm."""
    toks = cr.tokens; pos = cr.pos; heads = cr.heads
    n = len(toks); low = [w.lower() for w in toks]
    out = []
    for vi in range(1, n + 1):
        if pos[vi - 1] != "VERB":
            continue
        lem = lemma_word(low[vi - 1])
        entry = lex.get(lem)
        if entry is None:
            continue
        deps = [a for a in range(1, n + 1) if heads.get(a) == vi]
        subj = [a for a in deps if pos[a - 1] in RT.NOMINAL and a < vi]
        agent_a = subj[-1] if subj else None
        out.append({"verb": lem, "op": entry["op"],
                    "agent": (low[agent_a - 1] if agent_a else None),
                    "agent_wtok": (agent_a - 1 if agent_a else None)})   # 1-based parse -> 0-based wtok
    return out


def run(mode="full", n_mcscript=1500, n_litbank=20):
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.thematic_role_labeler import lemma_word
    from experiments.possession_operators import build_lexicon
    pos_ckpt = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
    arc_ckpt = os.path.join(REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
    gen = CandidateGenerator.load(pos_ckpt, arc_ckpt)
    lex = build_lexicon(use_cache=True)
    if mode == "smoke":
        n_mcscript, n_litbank = 150, 3
    mc = diagnose_mcscript(gen, lex, lemma_word, n_mcscript)
    lb = diagnose_litbank(gen, lex, lemma_word, n_litbank)
    return {"anchor": ANCHOR, "mode": mode, "mcscript2": mc, "litbank": lb,
            "reader_coref_scope": "he/she family only (hdlab/coref.TARGET_PRONOUNS); I/you/we=DEIXIS, it/they=object anaphora -- BOTH out of scope"}


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    """Minimal: the classifier + one MCScript-style parse fire."""
    assert classify_pron("I") == "first_second"
    assert classify_pron("he") == "third_person_reader_scope"
    assert classify_pron("it") == "object_or_plural"
    assert classify_pron("Anna") is None
    print("[self-test] pronoun classifier OK", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-litbank", type=int, default=20)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_litbank=args.n_litbank)
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    mc = res["mcscript2"]; lb = res["litbank"]
    print("\n=== MCScript2 (first-person everyday; parent corpus) ===", flush=True)
    print("  transfer instances=%d  agents recovered=%d" % (mc["n_transfer_instances"], mc["have_agent"]), flush=True)
    print("  AGENT class fractions: %s" % mc["agent_class_frac"], flush=True)
    print("  (reader coref resolves ONLY 'third_person_reader_scope'; first_second + object are out of scope)", flush=True)
    print("\n=== LitBank (third-person literary; gold coref) ===", flush=True)
    print("  docs used=%d  totals=%s" % (lb["n_docs_used"], lb["totals"]), flush=True)
    print("  AGENT-is-gold-mention class fractions: %s" % lb["agent_gold_class_frac"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
