"""exp_mcguffey_migrate_build_modern_gold_v1 -- BUILD A MODERN SITUATION-MODEL EVAL GOLD FROM UD-EWT.

Problem: the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text (p1).

WHY. The reader's composed situation-model eval (exp_wire_organs_endtoend_v1: entity-role-at-clause-T
query answering, "what role did entity E play at clause C?") is still scored on 57 hand-authored
McGuffey passages (1830s schoolbook prose). This builds the MODERN twin of that gold from UD-EWT --
genuinely modern web text (2000s: blogs, reviews, emails, Q&A) with a GOLD Universal-Dependencies parse.

TRANSPARENT, NO-LLM DERIVATION (the brief's authorised route: UD deprel -> thematic role).
  clauses  = the sentences of a UD document (the original '# text =' line).
  roles    = agent := nsubj of an active verb; patient := obj OR nsubj:pass (a passive subject).
             (matches the on-shelf UD-EWT role pipeline exp_read_discourse..._ud_ewt_v1 PATIENT_LABELS.)
  entities = nominal core-argument HEADS (PROPN / NOUN) tracked across a document's clauses by LEMMA
             identity (a transparent string-identity coref; UD ships no coref, so pronoun/alias
             tracking is OUT OF SCOPE here -- that dimension is validated separately on LitBank gold
             coref). An entity is kept iff it recurs across >= 2 distinct clauses (trackable).
  queries  = every non-final-clause mention of a tracked entity {entity, query_clause, gold_role}.

BRAIN-FIDELITY DISCRIMINATOR (why modern matters, not just newer). Each binding is tagged
canonical/non-canonical: NON-CANONICAL = passive (nsubj:pass), postverbal subject (inversion), or
preverbal object (fronting). McGuffey is ~all canonical SVO, so a shallow "first-noun = agent" (Bever
NVN) heuristic scores high there; the brain's structure-based role mechanism (Competition Model
cue-validity; Lewis & Vasishth 2005) handles non-canonical order. The non-canonical subset is where a
McGuffey-inflated organ must drop -- that drop is the fidelity signal, not a corpus artefact.

The reader re-derives roles INDEPENDENTLY from clause TEXT via its own nltk front-end; the gold here
comes from the UD GOLD parse. Different derivations => no circularity.

Writes gold to data/eval_gold_mention_role_modern_ud_ewt_v1/ and stats to this cell's data dir.
Does NOT modify hdlab/. numpy-free parsing; CPU; runs inline.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict, Counter
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UD_TRAIN = os.path.join(REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
UD_TEST = os.path.join(REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
GOLD_DIR = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_build_modern_gold_v1")

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu

_ABSTRACT = {  # common non-referential/relational NOUN lemmas we do NOT treat as trackable entities
    "thing", "way", "time", "day", "year", "part", "kind", "lot", "number", "fact", "case", "point",
    "reason", "example", "problem", "question", "idea", "issue", "place", "side", "end", "one", "none",
    "something", "anything", "everything", "nothing", "someone", "anyone", "everyone", "%", "percent",
}


def parse_conllu(path):
    """Yield documents; each doc = list of {'text': str, 'toks': [tokdict,...]}."""
    docs = []
    cur_doc = None
    cur_text = None
    cur_toks = None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# newdoc"):
            if cur_doc is not None:
                docs.append(cur_doc)
            cur_doc = []
            continue
        if line.startswith("# text ="):
            cur_text = line.split("=", 1)[1].strip()
            continue
        if line.startswith("#"):
            continue
        if line == "":
            if cur_toks:
                if cur_doc is None:
                    cur_doc = []
                cur_doc.append({"text": cur_text or "", "toks": cur_toks})
                cur_toks = None
                cur_text = None
            continue
        cols = line.split("\t")
        if len(cols) < 8 or "-" in cols[0] or "." in cols[0]:
            continue
        cur_toks = cur_toks or []
        cur_toks.append({"id": int(cols[0]), "form": cols[1], "lemma": cols[2], "upos": cols[3],
                         "xpos": cols[4], "head": int(cols[6]), "deprel": cols[7]})
    if cur_toks and cur_doc is not None:
        cur_doc.append({"text": cur_text or "", "toks": cur_toks})
    if cur_doc is not None:
        docs.append(cur_doc)
    return docs


def clause_role_bindings(toks):
    """Return [(entity_key, mention_form, role, canonical, canon_type)] for core args of verbs in this clause."""
    byid = {t["id"]: t for t in toks}
    headdeps = {}
    for t in toks:
        headdeps.setdefault(t["head"], []).append(t["deprel"])
    out = []
    for t in toks:
        depfull = t["deprel"]
        dep = depfull.split(":")[0]
        head = byid.get(t["head"])
        # role-governing head must be a CONTENT VERB. A bare AUX/copula head ("X is a doctor") gives a
        # non-thematic subject -- excluding it removes UD copular nsubj noise.
        if head is None or head["upos"] != "VERB":
            continue
        if depfull == "nsubj:pass" or dep == "obj":
            role = "patient"
        elif dep == "nsubj":
            # THEMATIC agent only: NOT an existential-there pivot ("there has been talk" -> talk is nsubj of
            # the VERB 'been' but is not an agent) and NOT a copular 'be' subject. Existential 'been'/'is'
            # is a VERB in UD so the AUX-exclusion above misses it; detect the expl dependent / 'be' lemma.
            existential = any(d.split(":")[0] == "expl" for d in headdeps.get(t["head"], []))
            if existential or head["lemma"].lower() == "be":
                continue
            role = "agent"
        else:
            continue
        if t["upos"] not in ("PROPN", "NOUN"):
            continue  # PRON has no gold coref in UD -> not a trackable entity here
        lemma = t["lemma"].lower()
        if t["upos"] == "NOUN" and lemma in _ABSTRACT:
            continue
        key = lemma
        # canonicality of the surface realisation + the construction TYPE (for per-type analysis)
        canonical = True
        canon_type = "canonical"
        if depfull == "nsubj:pass":
            canonical = False
            canon_type = "passive"
        elif role == "agent" and t["id"] > t["head"]:
            canonical = False
            canon_type = "inversion"   # postverbal subject (quotative/locative inversion)
        elif role == "patient" and dep == "obj" and t["id"] < t["head"]:
            canonical = False
            canon_type = "fronting"    # preverbal / fronted object
        out.append((key, t["form"], role, canonical, canon_type))
    return out


def build_passages(docs, min_clauses=2, max_clauses=12, doc_id_prefix="ud"):
    passages = []
    for di, doc in enumerate(docs):
        clauses_txt = []
        # entity_key -> list of {clause, mention, role, canonical}
        ent = defaultdict(list)
        for ci, sent in enumerate(doc):
            if ci >= max_clauses:
                break
            clauses_txt.append(sent["text"])
            seen_ec = set()  # one role per (entity, clause): keep first core-arg mention
            for key, form, role, canon, canon_type in clause_role_bindings(sent["toks"]):
                if (key, ci) in seen_ec:
                    continue
                seen_ec.add((key, ci))
                ent[key].append({"clause": ci, "mention": form, "role": role, "canonical": canon,
                                 "noncanon_type": canon_type})
        if len(clauses_txt) < min_clauses:
            continue
        # keep entities recurring across >= 2 distinct clauses
        tracked = {}
        for k, chain in ent.items():
            distinct = {m["clause"] for m in chain}
            if len(distinct) >= 2:
                tracked[k] = sorted(chain, key=lambda m: m["clause"])
        if not tracked:
            continue
        # target queries: every NON-FINAL-clause mention of a tracked entity
        queries = []
        for k, chain in tracked.items():
            last_clause = max(m["clause"] for m in chain)
            for m in chain:
                if m["clause"] < last_clause:
                    queries.append({"entity": k, "query_clause": m["clause"], "gold_role": m["role"],
                                    "canonical": m["canonical"], "noncanon_type": m["noncanon_type"]})
        if not queries:
            continue
        entities = {k: [{"clause": m["clause"], "mention": m["mention"], "role": m["role"]} for m in chain]
                    for k, chain in tracked.items()}
        passages.append({
            "passage_id": f"{doc_id_prefix}_{di}",
            "grade": "modern_web",
            "clauses": clauses_txt,
            "entities": entities,
            "target_queries": queries,
            "note": "UD-EWT gold-parse-derived situation-model gold; string-identity entity tracking.",
            "hard_feature_class": "modern_web_role_timeline",
            "gold_verified": "transparent_ud_deprel_rule",
        })
    return passages


def stats(passages):
    nq = sum(len(p["target_queries"]) for p in passages)
    roles = Counter(q["gold_role"] for p in passages for q in p["target_queries"])
    noncanon = sum(1 for p in passages for q in p["target_queries"] if not q["canonical"])
    # role-varying subset: queries whose gold_role != the entity's most-recent (final) role
    rolevar = 0
    for p in passages:
        final_role = {}
        for k, chain in p["entities"].items():
            final_role[k] = max(chain, key=lambda m: m["clause"])["role"]
        for q in p["target_queries"]:
            if q["gold_role"] != final_role[q["entity"]]:
                rolevar += 1
    clause_lens = [len(p["clauses"]) for p in passages]
    return {
        "n_passages": len(passages), "n_queries": nq, "roles": dict(roles),
        "n_noncanonical_queries": noncanon, "n_rolevarying_queries": rolevar,
        "mean_clauses": round(sum(clause_lens) / max(1, len(clause_lens)), 2),
        "max_clauses": max(clause_lens) if clause_lens else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--split", default="both", choices=["train", "test", "both"])
    args = ap.parse_args()

    paths = {"train": [UD_TRAIN], "test": [UD_TEST], "both": [UD_TRAIN, UD_TEST]}[args.split]
    docs = []
    for pth in paths:
        docs += parse_conllu(pth)
    passages = build_passages(docs)
    st = stats(passages)

    if args.self_test:
        assert st["n_passages"] >= 50, st
        assert st["n_queries"] >= 150, st
        assert st["n_noncanonical_queries"] >= 10, st
        assert st["n_rolevarying_queries"] >= 20, st
        assert set(st["roles"]) <= {"agent", "patient"}, st
        # shape parity with McGuffey gold
        p = passages[0]
        assert set(p) >= {"passage_id", "clauses", "entities", "target_queries"}, list(p)
        print("self-test PASS", json.dumps(st))
        return

    os.makedirs(GOLD_DIR, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    gold_path = os.path.join(GOLD_DIR, "gold_situation_modern_ud_ewt_v1.jsonl")
    with open(gold_path, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p) + "\n")
    meta = {"ts_iso": datetime.now(timezone.utc).isoformat(), "split": args.split,
            "gold_path": os.path.relpath(gold_path, REPO), "stats": st}
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("=" * 78)
    print("MODERN SITUATION-MODEL GOLD (UD-EWT, gold-parse-derived, no LLM)")
    print("=" * 78)
    print(json.dumps(st, indent=2))
    print(f"\nwrote {os.path.relpath(gold_path, REPO)}")


if __name__ == "__main__":
    main()
