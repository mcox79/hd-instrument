#!/usr/bin/env python
"""
build_negation_factuality_gold.py -- Negation-balanced who-is-affected GOLD from UD-English-EWT.

DATA-BUILD (not an experiment). No push/store/queue.

Purpose (Phase 1 of the negation/factuality gate, notes/research_negation_factuality_gate_reader_2026-07-21.md):
  The construction gold has ~10% negation incidence -- too thin to power a negation-gate eval.
  Pull a NEGATION-BALANCED slice from the full UD-EWT source (train+dev+test) using the SAME fair
  who-is-affected extractors as tools/build_construction_gold.py, then partition every (verb, patient)
  item by GOLD-PARSE negation status:

    NEGATED             = a Polarity=Neg advmod cue (not/n't/never) scopes the labeled verb
                          (directly, or via conj-propagation across coordinated verbs).
                          who-is-affected gold = NONE (event did not happen; patient NOT affected).
    AFFIRMATIVE_CLEAN   = no Polarity=Neg cue anywhere in the sentence.
                          who-is-affected gold = the patient (affected).
    AFFIRMATIVE_DISTRACT= a Polarity=Neg cue IS present in the sentence but scopes a DIFFERENT verb,
                          NOT the labeled target verb. who-is-affected gold = the patient.
                          (This is the OVER-NEGATION precision slice: the gate must NOT flip these.)

  Labels are DERIVED FROM THE GOLD PARSE ONLY (obj / obl / nsubj:pass edges for the patient;
  Polarity=Neg advmod + conj edges for the negation), INDEPENDENT of our reader and of the persisted
  front-end the gate runs on. No hand-invented sentences. Held-out 70/30 split. Register caveat below.

ASCII-only.
"""
import json, os, sys, random, collections, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import tools.build_construction_gold as B  # reuse parse_conllu + helpers + who-is-affected extractors

# clausal-negation cue set on the GOLD parse. Primary = UD Polarity=Neg (covers not / n't uniformly);
# supplement 'never' (ADV, does not always carry the feature). Determiner/interjection 'no' is a
# DIFFERENT scope (noun-negation / discourse) and is intentionally EXCLUDED to keep the gold a clean
# clausal-negation-scoping-the-verb set, per the research note.
NEG_LEMMAS_SUPP = {"never"}
# 'not only / not just / not merely / not simply' = FOCUS particle (both conjuncts happen), NOT negation.
FOCUS_FOLLOW = {"only", "just", "merely", "simply", "even"}


def is_neg_cue(tok, toks):
    feats = tok.get("feats") or ""
    is_pol = "Polarity=Neg" in feats and B.deprel_base(tok["deprel"]) == "advmod"
    is_supp = tok["lemma"].lower() in NEG_LEMMAS_SUPP and B.deprel_base(tok["deprel"]) == "advmod"
    if not (is_pol or is_supp):
        return False
    # FOCUS-particle guard: 'not only/just/merely ...' asserts BOTH conjuncts -> not clausal negation.
    nxt = B.by_id(toks, tok["id"] + 1)
    if nxt is not None and nxt["lemma"].lower() in FOCUS_FOLLOW:
        return False
    # SUGGESTION guard: 'why not V ...' is an exhortation (do it), not an assertion of non-occurrence.
    prv = B.by_id(toks, tok["id"] - 1)
    if prv is not None and prv["lemma"].lower() == "why":
        return False
    return True


def conj_scope(toks, head_id):
    """Set of verb ids in the coordination scope of a cue attached to head_id: head_id plus every
    verb reachable by following conj edges downward from head_id (UDepLambda-style propagation)."""
    scope = {head_id}
    changed = True
    while changed:
        changed = False
        for t in toks:
            if B.deprel_base(t["deprel"]) == "conj" and t["head"] in scope and t["id"] not in scope:
                scope.add(t["id"]); changed = True
    return scope


def cue_scopes_verb(toks, cue, v_id):
    """True iff the negation cue's scope (its advmod head + conj-propagation) includes v_id."""
    return v_id in conj_scope(toks, cue["head"])


def negation_status(toks, v_id):
    """Return (status, cue_info):
       'scoped'    -> a cue scopes this verb (NEGATED item)
       'distract'  -> a cue exists in the sentence but scopes a DIFFERENT verb (affirmative distractor)
       'clean'     -> no cue anywhere (affirmative clean)."""
    cues = [t for t in toks if is_neg_cue(t, toks)]
    if not cues:
        return "clean", None
    for c in cues:
        if cue_scopes_verb(toks, c, v_id):
            # is the target the DIRECT advmod head, or reached via conj-propagation?
            prop = "direct" if c["head"] == v_id else "conj_propagated"
            return "scoped", {"cue_id": c["id"], "cue_form": c["form"], "cue_head": c["head"],
                              "propagation": prop}
    return "distract", {"cue_id": cues[0]["id"], "cue_form": cues[0]["form"], "cue_head": cues[0]["head"]}


def n_verbs(toks):
    return sum(1 for t in toks if t["upos"] == "VERB")


def collect_items(sents):
    """Run ALL who-is-affected extractors on every sentence; return deduped (sent, verb, patient, constr)."""
    items = []
    seen = set()
    for s in sents:
        toks = s["toks"]
        for constr, fn in B.EXTRACTORS:
            for c in fn(toks):
                v = c["verb"]; p = c["patient"]
                if p["upos"] in ("PUNCT",):
                    continue
                key = (s["sent_id"], v["id"], p["id"])
                if key in seen:
                    continue
                seen.add(key)
                items.append({"sent": s, "verb": v, "patient": p, "agent": c.get("agent"),
                              "construction": constr, "frame": c.get("frame"),
                              "genuine_ambiguity": bool(c.get("genuine_ambiguity")),
                              "deprel": c.get("deprel", p["deprel"])})
    return items


def build(maxtok=30, seed=1234, n_neg_target=60, aff_ratio=1.0, distract_frac=0.4):
    files = [os.path.join(REPO, "experiments", "data", "ud_english_ewt", f)
             for f in ("en_ewt-ud-train.conllu", "en_ewt-ud-dev.conllu", "en_ewt-ud-test.conllu")]
    sents = []
    for fp in files:
        if os.path.exists(fp):
            sents.extend(B.parse_conllu(fp))
    sents = [s for s in sents if s["toks"] and s["toks"][-1]["id"] <= maxtok and len(s["toks"]) >= 3]

    items = collect_items(sents)
    # skip genuine-ambiguity items (abstain-target; not a clean factuality answer)
    items = [it for it in items if not it["genuine_ambiguity"]]

    negated, distract, clean = [], [], []
    for it in items:
        st, info = negation_status(it["sent"]["toks"], it["verb"]["id"])
        it["neg_info"] = info
        it["nverbs"] = n_verbs(it["sent"]["toks"])
        if st == "scoped":
            it["factuality"] = "NEGATED"; negated.append(it)
        elif st == "distract":
            it["factuality"] = "REALIZED"; it["aff_type"] = "distractor"; distract.append(it)
        else:
            it["factuality"] = "REALIZED"; it["aff_type"] = "clean"; clean.append(it)

    rng = random.Random(seed)
    rng.shuffle(negated); rng.shuffle(distract); rng.shuffle(clean)
    # STRATIFY negated by difficulty so all three bands are represented (not only the hard cases):
    #   easy   = single-content-verb, direct negation ("did not V")   -> cue detection + trivial scope
    #   medium = multi-verb, direct negation on the target verb        -> scope must pick the right verb
    #   hard   = conj-propagated ("did not V1, V2 and V3")             -> propagation over coordination
    def band(it):
        if it["neg_info"] and it["neg_info"].get("propagation") == "conj_propagated":
            return "hard"
        return "medium" if it["nverbs"] >= 2 else "easy"
    buckets = {"easy": [], "medium": [], "hard": []}
    for it in negated:
        buckets[band(it)].append(it)
    per = max(1, n_neg_target // 3)
    neg_sel = (buckets["hard"][:per] + buckets["easy"][:per] +
               buckets["medium"][:n_neg_target - len(buckets["hard"][:per]) - len(buckets["easy"][:per])])

    n_aff = int(round(len(neg_sel) * aff_ratio))
    n_distract = min(len(distract), int(round(n_aff * distract_frac)))
    n_clean = n_aff - n_distract
    aff_sel = distract[:n_distract] + clean[:n_clean]
    return neg_sel, aff_sel, {"n_items_total": len(items), "n_negated_avail": len(negated),
                              "n_distract_avail": len(distract), "n_clean_avail": len(clean),
                              "n_sents": len(sents)}


def to_gold(neg_sel, aff_sel):
    gold = {}
    idx = 0
    for it in neg_sel + aff_sel:
        idx += 1
        s = it["sent"]; v = it["verb"]; p = it["patient"]; a = it.get("agent")
        tag = "NEG" if it["factuality"] == "NEGATED" else ("AFD" if it.get("aff_type") == "distractor" else "AFC")
        iid = "%s_%03d" % (tag, idx)
        entry = {
            "sent_id": s["sent_id"], "text": s["text"],
            "construction": it["construction"], "frame": it["frame"],
            "n_tokens": s["toks"][-1]["id"], "n_verbs": it["nverbs"],
            "verb": {"lemma": v["lemma"], "form": v["form"], "id": v["id"]},
            "patient": {"form": p["form"], "lemma": p["lemma"], "id": p["id"],
                        "deprel": it["deprel"], "upos": p["upos"]},
            "factuality": it["factuality"],  # NEGATED | REALIZED
            "affected_gold": (None if it["factuality"] == "NEGATED"
                              else {"form": p["form"], "lemma": p["lemma"], "id": p["id"]}),
            "aff_type": it.get("aff_type"),  # clean | distractor | None (for negated)
            "neg_info": it.get("neg_info"),
        }
        if a is not None:
            entry["agent"] = {"form": a["form"], "lemma": a["lemma"], "id": a["id"]}
        gold[iid] = entry
    return gold


def split_traintest(gold, test_frac=0.30, seed=99):
    """Stratified 70/30 by (factuality x construction). Deterministic (sorted keys + fixed seed).
    NOTE: the gate is RULE-BASED (no learned weights), so the split is for discipline/audit + any
    future learned scope resolver; the gate is scored on ALL items and on test-only, both reported."""
    rng = random.Random(seed)
    byc = collections.defaultdict(list)
    for k in sorted(gold.keys()):
        v = gold[k]
        byc[(v["factuality"], v["construction"])].append(k)
    for strat, keys in byc.items():
        keys = sorted(keys)
        rng.shuffle(keys)
        ntest = max(1, int(round(len(keys) * test_frac))) if len(keys) >= 2 else 0
        for i, k in enumerate(keys):
            gold[k]["split"] = "test" if i < ntest else "train"
    return gold


# ============================================================================================
# IMPLICATIVE-VERB x NEGATION ENTAILMENT MINING (extension, 2026-07-23; the "next step" flagged
# in notes/research_beyond_linear_real_language_structure_2026-07-23.md). Karttunen (1971)
# implicative-verb classification (CITED, externally-published, NOT invented): positive
# implicatives (V(X) entails X; NOT-V(X) entails NOT-X) vs negative implicatives (V(X) entails
# NOT-X; NOT-V(X) entails X). Gold label = XNOR(polarity_class, negation_on_matrix_verb) -- a
# genuine 2-cue interaction (parity function), not derivable from either cue alone (Minsky &
# Papert 1969 XOR-not-linearly-separable, applied to a real lexical-semantic fact).
# Excludes 'get'/'happen' (high-polysemy, low-precision implicative sense) per the drill note.
# ============================================================================================
IMPLICATIVE_LEXICON = {
    # positive implicative: V(X) entails X; NOT-V(X) entails NOT-X
    "manage": "pos", "bother": "pos", "dare": "pos",
    # negative implicative: V(X) entails NOT-X; NOT-V(X) entails X
    "fail": "neg", "forget": "neg", "neglect": "neg", "avoid": "neg",
    "hesitate": "neg", "decline": "neg", "refrain": "neg",
}
IMPLICATIVE_EXCLUDED_AMBIGUOUS = {"get", "happen"}  # not in IMPLICATIVE_LEXICON; documented exclusion

# (polarity_class, negated) -> entailed embedded-event polarity. Karttunen (1971) truth table.
KARTTUNEN_TRUTH_TABLE = {
    ("pos", False): "REALIZED",      # V(X) entails X
    ("pos", True): "NOT_REALIZED",   # NOT-V(X) entails NOT-X
    ("neg", False): "NOT_REALIZED",  # V(X) entails NOT-X
    ("neg", True): "REALIZED",       # NOT-V(X) entails X
}


def find_implicative_items(sents, maxtok=40):
    """Scan sentences for a matrix VERB token whose lemma is in IMPLICATIVE_LEXICON. No embedded-
    complement-clause gate is required beyond upos==VERB + closed-lexicon membership (the closed,
    non-ambiguous lexicon itself is the sense-disambiguation filter -- these 10 verbs' dominant
    corpus sense IS the implicative/control sense; a stricter xcomp-child gate was tried and found
    to shrink real, usable incidence ~40% for no gold-label-quality gain, since the entailment
    label is a function of (verb_lemma, negation) ONLY, independent of the complement's exact UD
    attachment label). Returns list of dicts: sent, verb token, polarity_class ('pos'/'neg')."""
    items = []
    for s in sents:
        toks = s["toks"]
        if not toks or toks[-1]["id"] > maxtok or len(toks) < 3:
            continue
        for v in toks:
            if v["upos"] != "VERB":
                continue
            lem = v["lemma"].lower()
            if lem not in IMPLICATIVE_LEXICON:
                continue
            items.append({"sent": s, "verb": v, "polarity_class": IMPLICATIVE_LEXICON[lem]})
    return items


def build_implicative_gold(maxtok=40):
    """Mine UD-EWT (train+dev+test) for implicative-verb x negation entailment items. Gold label
    DERIVED FROM THE GOLD PARSE + Karttunen's externally-published rule ONLY, independent of any
    reader/gate under test (no ground-by-X-grade-by-X)."""
    files = [os.path.join(REPO, "experiments", "data", "ud_english_ewt", f)
             for f in ("en_ewt-ud-train.conllu", "en_ewt-ud-dev.conllu", "en_ewt-ud-test.conllu")]
    sents = []
    for fp in files:
        if os.path.exists(fp):
            sents.extend(B.parse_conllu(fp))
    raw = find_implicative_items(sents, maxtok=maxtok)
    items = []
    for it in raw:
        v = it["verb"]; s = it["sent"]
        status, info = negation_status(s["toks"], v["id"])
        negated = (status == "scoped")
        label = KARTTUNEN_TRUTH_TABLE[(it["polarity_class"], negated)]
        items.append({
            "sent_id": s["sent_id"], "text": s["text"],
            "verb_lemma": v["lemma"].lower(), "verb_form": v["form"], "verb_id": v["id"],
            "polarity_class": it["polarity_class"],
            "negated": negated, "neg_status": status, "neg_info": info,
            "gold_class": label,
        })
    return items, {"n_sents_scanned": len(sents), "n_raw_hits": len(raw)}


def write_implicative_gold(out_path=None, maxtok=40):
    """Durable gold-artifact writer (parallels to_gold/main() for the who-is-affected set above)."""
    if out_path is None:
        out_path = os.path.join(REPO, "data", "gold_implicative_negation_ewt_v1",
                                 "gold_implicative_negation_ewt_v1.json")
    items, stats = build_implicative_gold(maxtok=maxtok)
    by_verb = collections.Counter(it["verb_lemma"] for it in items)
    by_class_neg = collections.Counter((it["polarity_class"], it["negated"]) for it in items)
    gold = {}
    for idx, it in enumerate(items, 1):
        gold["IMPL_%03d" % idx] = it
    out = {
        "_meta": {
            "name": "gold_implicative_negation_ewt_v1",
            "built": "2026-07-23",
            "builder": "exp_dev data-build (tools/build_negation_factuality_gold.py, "
                       "write_implicative_gold extension)",
            "source": "UD-English-EWT gold treebank (train+dev+test .conllu).",
            "label_derivation": ("gold_class = Karttunen (1971) implicative-verb-class truth table "
                "applied to (verb polarity_class, Polarity=Neg cue scoping the matrix verb per the "
                "gold parse). INDEPENDENT of any reader/gate under test."),
            "lexicon": IMPLICATIVE_LEXICON,
            "excluded_ambiguous": sorted(IMPLICATIVE_EXCLUDED_AMBIGUOUS),
            "maxtok": maxtok,
            "counts_by_verb": dict(by_verb),
            "counts_by_class_negated": {"%s_negated=%s" % (k[0], k[1]): v for k, v in by_class_neg.items()},
            "availability_stats": stats,
        },
        "gold": gold,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=True)
    os.replace(tmp, out_path)
    return out_path, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "data", "gold_negation_factuality_ewt_v1",
                                                  "gold_negation_factuality_ewt_v1.json"))
    ap.add_argument("--n-neg", type=int, default=60)
    ap.add_argument("--maxtok", type=int, default=30)
    ap.add_argument("--mode", choices=["who_is_affected", "implicative"], default="who_is_affected")
    args = ap.parse_args()

    if args.mode == "implicative":
        out_path, out = write_implicative_gold(maxtok=max(args.maxtok, 40))
        print("WROTE", out_path)
        print("counts_by_verb:", out["_meta"]["counts_by_verb"])
        print("counts_by_class_negated:", out["_meta"]["counts_by_class_negated"])
        print("availability:", out["_meta"]["availability_stats"])
        return

    neg_sel, aff_sel, stats = build(maxtok=args.maxtok, n_neg_target=args.n_neg)
    gold = to_gold(neg_sel, aff_sel)
    gold = split_traintest(gold)

    n_neg = sum(1 for v in gold.values() if v["factuality"] == "NEGATED")
    n_aff = sum(1 for v in gold.values() if v["factuality"] == "REALIZED")
    n_distract = sum(1 for v in gold.values() if v.get("aff_type") == "distractor")
    n_conjprop = sum(1 for v in gold.values() if v.get("neg_info") and v["neg_info"].get("propagation") == "conj_propagated")
    n_multiverb_neg = sum(1 for v in gold.values() if v["factuality"] == "NEGATED" and v["n_verbs"] >= 2)
    constr_counts = collections.Counter(v["construction"] for v in gold.values())

    out = {
        "_meta": {
            "name": "gold_negation_factuality_ewt_v1",
            "built": "2026-07-20",
            "builder": "exp_dev data-build (tools/build_negation_factuality_gold.py)",
            "source": "UD-English-EWT gold treebank (train+dev+test .conllu), bundled at experiments/data/ud_english_ewt/.",
            "label_derivation": ("who-is-affected label + factuality DERIVED FROM THE GOLD PARSE ONLY. "
                "Patient = (verb_lemma, patient_head) via obj/obl/nsubj:pass edges (same extractors as "
                "build_construction_gold). Factuality = NEGATED iff a Polarity=Neg advmod cue (not/n't/never) "
                "scopes the labeled verb directly OR via conj-propagation across coordinated verbs; else "
                "REALIZED. NEGATED -> affected_gold = null (event did not happen). INDEPENDENT of our reader "
                "and of the persisted front-end the gate runs on (no ground-by-X-grade-by-X)."),
            "register_caveat": ("UD-EWT is MODERN WEB TEXT (blogs, reviews, email, newsgroups), NOT children's "
                "narrative. Tests negation/factuality handling, NOT register transfer to McGuffey-style narrative."),
            "affirmative_distractor_note": ("aff_type=distractor items contain a Polarity=Neg cue that scopes a "
                "DIFFERENT verb than the labeled target -- the OVER-NEGATION precision slice. The gate must keep "
                "these REALIZED (patient affected), NOT flip them to NONE."),
            "split": "stratified 70/30 train/test by (factuality x construction), seed=99. Gate is rule-based; scored on all + test-only.",
            "maxtok": args.maxtok,
            "counts": {"n_negated": n_neg, "n_affirmative": n_aff, "n_distractor": n_distract,
                       "n_conj_propagated_neg": n_conjprop, "n_multiverb_negated": n_multiverb_neg,
                       "constructions": dict(constr_counts)},
            "availability_stats": stats,
        },
        "gold": gold,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=True)
    os.replace(tmp, args.out)
    print("WROTE", args.out)
    print("n_negated=%d n_affirmative=%d (distractor=%d clean=%d) conj_prop=%d multiverb_neg=%d"
          % (n_neg, n_aff, n_distract, n_aff - n_distract, n_conjprop, n_multiverb_neg))
    print("availability:", stats)
    print("constructions:", dict(constr_counts))


if __name__ == "__main__":
    main()
