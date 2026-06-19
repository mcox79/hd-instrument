"""SKUNKWORKS Phase 4e Author-N batch 3 -- substrate SELF-SELECTION scorer (DECISION 97 production scorer).
score = 3*pointer_nominations + 2*family_member + min(op_out_degree,5)
dedup pre-filter excludes: already-signed + merge-synonyms + superseded + *_atom + *_synthesis
                           + oeis_/wikidata/q-placeholders + held-out gold (q_learning/policy_gradient, 22nd rule)
NO LLM prior in selection (substrate-internal). Read-only. ASCII only.
"""
from __future__ import annotations
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType

SELF_MODEL = Path("data/substrate_index/skunkworks_self_model_of_operators_v1.jsonl")
POINTER_KEYS = ["derived_from","uses","computes","implemented_via","composed_of",
                "computed_via","instance_of","specializes","defined_over","represents"]
HELD_OUT = {"q_learning","policy_gradient"}  # 22nd rule
OP_RELS = [RelationType.DEPENDS_ON, RelationType.USES, RelationType.SPECIALIZES, RelationType.INSTANCE_OF]

def short(qid): return qid.split("/")[-1]

def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    # signed set + pointer nominations
    signed = set(); nominations = {}
    for line in SELF_MODEL.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except: continue
        a = d.get("atom","")
        if a: signed.add(short(a))
        for k in POINTER_KEYS:
            v = d.get(k)
            if not v: continue
            tgts = v if isinstance(v, list) else [v]
            for t in tgts:
                nominations[short(str(t))] = nominations.get(short(str(t)),0)+1

    # family-member set: atoms with SPECIALIZES -> *_FAM
    # candidate operators: math corpus, tier T2/T3/T4, kind operator/sub_op, not excluded
    cands = []
    for at in ps.all_atoms():
        qid = at.qualified_id
        if not qid.startswith("math::"): continue
        sn = short(qid)
        kind = at.kind.value if hasattr(at.kind,"value") else str(at.kind)
        tier = at.tier.value if hasattr(at.tier,"value") else str(at.tier)
        if tier not in ("T2","T3","T4"): continue
        if kind not in ("operator","sub_op","primitive"): continue
        # dedup exclusions
        if sn in signed: continue
        if sn in HELD_OUT: continue
        if sn.endswith("_atom") or sn.endswith("_synthesis") or sn.endswith("_lemma"): continue
        if sn.startswith("oeis_") or sn.startswith("wikidata") or re.match(r"^[Qq]\d", sn): continue
        if "_FAM" in qid: continue  # families themselves not operator candidates
        # score
        noms = nominations.get(sn, 0)
        fam = 0
        try:
            sp = ps.out_neighbors(qid, RelationType.SPECIALIZES) or set()
            fam = 1 if any("_FAM" in s for s in sp) else 0
        except: pass
        outdeg = 0
        for rt in OP_RELS:
            try: outdeg += len(ps.out_neighbors(qid, rt) or set())
            except: pass
        score = 3*noms + 2*fam + min(outdeg,5)
        cands.append((score, noms, fam, outdeg, sn, qid, kind, tier))
    cands.sort(reverse=True)
    print("=== Phase 4e batch 3 self-selection (top 20 by composite score) ===")
    print("score noms fam outdeg | atom | tier kind")
    for c in cands[:20]:
        print(f"{c[0]:>4} {c[1]:>4} {c[2]:>3} {c[3]:>5}  | {c[4]:<34} | {c[7]} {c[6]}")
    print(f"\ntotal eligible candidates: {len(cands)} | signed: {len(signed)}")

if __name__ == "__main__":
    main()
