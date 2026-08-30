"""exp_mcguffey_migrate_grammatical_function_v1 -- IMPLEMENT THE BRAIN'S MECHANISM for non-canonical roles:
GRAMMATICAL FUNCTION (from a parse) + VOICE + EVENTIVITY, not surface position.

The drills + empirical work reframed the residual: "inversion" is NOT primarily a thematic-fit problem. Two
findings drive this cell:
  (1) 87% of the "inversion" set (postverbal nsubj) is EXISTENTIAL "there" ("There has been talk") whose pivot
      is NOT a thematic agent -- my transparent UD nsubj->agent rule mislabeled them (existential "been" is a
      VERB so the earlier AUX-exclusion missed it). A brain-faithful THEMATIC gold excludes existential/copular
      subjects. Only 11% (52) are GENUINE inversions (quotative "asked Bush", locative).
  (2) The genuine non-canonical constructions (passive, genuine inversion) are GRAMMATICAL-FUNCTION-preserving,
      POSITION-changing: the postverbal/displaced NP is still the grammatical SUBJECT. The brain assigns roles
      from grammatical function (subject/object) + VOICE, not surface position -- and the parser recovers
      grammatical function (our own `role_assignment_is_untested_on_archaic_literary_prose`: subject-ID 0.94).

This cell implements the brain-faithful structure cue and tests it NON-CIRCULARLY with spaCy (a REAL parser,
independent of the UD gold): grammatical function -> role via voice (active subj=agent; passive subj=patient;
object=patient; existential/copular subj EXCLUDED). Compared to the surface POSITION cue and the UD-gold-function
upper bound, per construction. CAN-FAIL: grammatical function (spaCy) must SOLVE passive + genuine inversion
where position collapses to ~0; the true residual is the genuine hard inversions even a real parser mis-parses.

Local only (spaCy). Writes only to data/exp_mcguffey_migrate_grammatical_function_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations
import argparse, json, os, sys, warnings
from collections import defaultdict, Counter
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
warnings.filterwarnings("ignore")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu, UD_TRAIN, UD_TEST  # noqa: E402

OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_grammatical_function_v1")
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu

_ABSTRACT = {"thing", "way", "time", "day", "year", "part", "kind", "lot", "number", "fact", "case",
             "point", "reason", "example", "problem", "question", "idea", "issue", "place", "one"}


def thematic_core_args(docs):
    """Core args with a THEMATIC (not raw-grammatical) role: agent = nsubj of an EVENTIVE verb (NOT copular
    'be', NOT an existential-there verb); patient = obj or nsubj:pass. Existential/copular subjects EXCLUDED."""
    out = []
    for di, doc in enumerate(docs):
        for si, sent in enumerate(doc):
            byid = {t["id"]: t for t in sent["toks"]}
            headdeps = defaultdict(list)
            for t in sent["toks"]:
                headdeps[t["head"]].append(t["deprel"])
            for t in sent["toks"]:
                depfull = t["deprel"]; dep = depfull.split(":")[0]
                h = byid.get(t["head"])
                if h is None or h["upos"] != "VERB":
                    continue
                if t["upos"] not in ("PROPN", "NOUN"):
                    continue
                lemma = t["lemma"].lower()
                if t["upos"] == "NOUN" and lemma in _ABSTRACT:
                    continue
                existential = any(d.startswith("expl") for d in headdeps[t["head"]])
                copular = h["lemma"].lower() == "be"
                if depfull == "nsubj:pass" or dep == "obj":
                    role = "patient"
                elif dep == "nsubj":
                    if existential or copular:
                        continue            # existential pivot / copular subject is NOT a thematic agent
                    role = "agent"
                else:
                    continue
                preverbal = t["id"] < t["head"]
                if depfull == "nsubj:pass":
                    ct = "passive"
                elif role == "agent" and not preverbal:
                    ct = "inversion"
                elif role == "patient" and dep == "obj" and preverbal:
                    ct = "fronting"
                else:
                    ct = "canonical"
                out.append({"doc": di, "sent": si, "text": sent["text"], "form": t["form"],
                            "lemma": lemma, "role": role, "canon_type": ct, "preverbal": preverbal,
                            "tok_id": t["id"]})
    return out


def spacy_role_for(nlp_doc, form, gold_tokpos):
    """Grammatical-function role from spaCy for the token matching `form` nearest gold position.
    active subj -> agent; nsubjpass -> patient; dobj/obj -> patient; attr/expl/other -> None (not thematic)."""
    cands = [w for w in nlp_doc if w.text.lower() == form.lower()]
    if not cands:
        return None
    w = min(cands, key=lambda x: abs(x.i - gold_tokpos))
    dep = w.dep_
    if dep in ("nsubjpass", "auxpass"):
        return "patient"
    if dep == "nsubj":
        # exclude copular / existential subjects (not thematic agents)
        head = w.head
        if head.lemma_.lower() == "be" or any(c.dep_ == "expl" for c in head.children):
            return None
        return "agent"
    if dep in ("dobj", "obj", "dative", "iobj"):
        return "patient"
    if dep in ("attr", "acomp", "expl"):
        return None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--canonical-sample", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    import numpy as np
    docs = parse_conllu(UD_TRAIN) + parse_conllu(UD_TEST)
    items = thematic_core_args(docs)
    comp = Counter(it["canon_type"] for it in items)

    # sample: all non-canonical + a canonical sample (spaCy parse is the cost)
    rng = np.random.default_rng(args.seed)
    noncanon = [it for it in items if it["canon_type"] != "canonical"]
    canon = [it for it in items if it["canon_type"] == "canonical"]
    k = min(args.canonical_sample if not args.self_test else 120, len(canon))
    canon_s = [canon[i] for i in rng.permutation(len(canon))[:k]]
    if args.self_test:
        noncanon = noncanon[:120]
    evalset = noncanon + canon_s

    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    # group by sentence to parse once
    bysent = defaultdict(list)
    for it in evalset:
        bysent[(it["doc"], it["sent"])].append(it)
    texts = {k: v[0]["text"] for k, v in bysent.items()}
    parsed = {}
    for key, txt in texts.items():
        parsed[key] = nlp(txt) if txt else None

    by = defaultdict(lambda: {"pos": [0, 0], "spacy": [0, 0], "gold": [0, 0]})
    for key, its in bysent.items():
        pdoc = parsed[key]
        for it in its:
            ct = it["canon_type"]; gold = it["role"]
            pos_pred = "agent" if it["preverbal"] else "patient"
            by[ct]["pos"][0] += int(pos_pred == gold); by[ct]["pos"][1] += 1
            by[ct]["gold"][0] += 1; by[ct]["gold"][1] += 1   # gold grammatical function = 1.0 upper bound
            sp = spacy_role_for(pdoc, it["form"], it["tok_id"] - 1) if pdoc is not None else None
            if sp is not None:
                by[ct]["spacy"][0] += int(sp == gold); by[ct]["spacy"][1] += 1

    def r(x):
        return round(x[0] / x[1], 4) if x[1] else None
    res = {ct: {"position": r(v["pos"]), "spacy_gramfunc": r(v["spacy"]),
                "spacy_coverage": round(v["spacy"][1] / v["pos"][1], 3) if v["pos"][1] else None,
                "gold_gramfunc_upperbound": 1.0, "n": v["pos"][1]} for ct, v in by.items()}

    verdict = {
        "inversion_was_mostly_existential_goldnoise": {"existential+copular_pct": round(
            100 * (comp.get("canonical", 0) and 1 or 1), 0) if False else None},
        "thematic_gold_composition": dict(comp),
        "spacy_gramfunc_solves_passive": (res.get("passive", {}).get("spacy_gramfunc") or 0) >
                                         (res.get("passive", {}).get("position") or 0) + 0.4,
        "spacy_gramfunc_beats_position_on_inversion": (res.get("inversion", {}).get("spacy_gramfunc") or 0) >
                                                      (res.get("inversion", {}).get("position") or 0),
        "position_solves_canonical": (res.get("canonical", {}).get("position") or 0) > 0.95,
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "thematic_gold_composition": dict(comp), "by_construction": res, "verdict": verdict}

    if args.self_test:
        assert "passive" in res and res["passive"]["n"] > 0
        print("self-test PASS", json.dumps({"passive": res.get("passive"), "inversion": res.get("inversion")}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 92)
    print("BRAIN-FAITHFUL ROLE CUE = GRAMMATICAL FUNCTION (parse) + VOICE, not surface position")
    print("=" * 92)
    print(f"\nTHEMATIC gold composition (existential/copular subjects EXCLUDED): {dict(comp)}")
    print(f"\n{'construction':12s} {'position':>10s} {'spaCy-gramfunc':>15s} {'(coverage)':>11s} {'gold-UB':>9s}   n")
    for ct in ("canonical", "passive", "inversion", "fronting"):
        if ct in res:
            v = res[ct]
            print(f"{ct:12s} {str(v['position']):>10s} {str(v['spacy_gramfunc']):>15s} "
                  f"{str(v['spacy_coverage']):>11s} {str(v['gold_gramfunc_upperbound']):>9s}   {v['n']}")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
