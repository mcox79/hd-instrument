"""SKUNKWORKS DETECT-step refinement + adversarial guard: pre-screen the 5 duplicate operator
pairs before Exp-Dev's CELL-DISTILL-VERIFY-1. Are the T2-vs-T3 'duplicates' genuinely equivalent
(safe to distill) or do they DIFFER in a load-bearing field (authoring look-alike -- do NOT merge)?

Bias-robust principle: do not distill operators that only LOOK redundant due to shared authored
signatures. Diff ALL fields; classify each group. Runnable now (atom records; no relations graph).
Output: a pre-screened list + risk flags for Exp-Dev.
"""
import json
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")
OUT = Path("data/substrate_index/meta_substrate_distill_prescreen.json")

# base concept names flagged as cross-tier duplicates by operator-overlap v1
BASES = ["discriminative_perceptron", "structured_perceptron_collins",
         "collins_structured_perceptron", "viterbi_decoder", "em_algorithm"]

# index all atoms whose id basename matches a flagged base
groups = {b: [] for b in BASES}
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    a = json.loads(line)
    base = a["id"].split("/", 1)[-1]
    if base in groups:
        groups[base].append(a)

def cmp_field(atoms, key):
    vals = [json.dumps(a.get(key), sort_keys=True) for a in atoms]
    return len(set(vals)) == 1, vals

report = []
for base, atoms in groups.items():
    if len(atoms) < 2:
        report.append({"base": base, "n": len(atoms),
                       "ids": [a["id"] for a in atoms],
                       "verdict": "NOT_A_PAIR (only one atom found at this id)"})
        continue
    ids = [a["id"] for a in atoms]
    desc_same, _ = cmp_field(atoms, "description")
    alg_same, _ = cmp_field(atoms, "algebra")
    caps_same, _ = cmp_field(atoms, "serves_capability")
    md_same, _ = cmp_field(atoms, "metadata")
    # which capabilities differ?
    capsets = [set(a.get("serves_capability") or []) for a in atoms]
    cap_union, cap_inter = set().union(*capsets), set.intersection(*capsets)
    cap_only = {a["id"]: sorted(set(a.get("serves_capability") or []) - cap_inter) for a in atoms}
    diffs = [k for k, same in [("description", desc_same), ("algebra", alg_same),
                               ("metadata", md_same), ("serves_capability", caps_same)] if not same]
    if alg_same and not diffs:
        verdict = "SAFE_DISTILL (all load-bearing fields identical; merge, keep canonical tier)"
    elif alg_same and diffs == ["serves_capability"]:
        verdict = ("MERGE_WITH_CAP_UNION (same algebra/signature; serves_capability differs -- "
                   "merge but UNION capabilities so none lost)")
    elif alg_same:
        verdict = f"REVIEW (same algebra but differs in {diffs}); verify before merge"
    else:
        verdict = f"DO_NOT_MERGE (algebra/signature differs -- authoring look-alike; differs in {diffs})"
    report.append({"base": base, "n": len(atoms), "ids": ids,
                   "algebra_identical": alg_same, "description_identical": desc_same,
                   "serves_capability_identical": caps_same, "differing_fields": diffs,
                   "cap_intersection_n": len(cap_inter), "cap_union_n": len(cap_union),
                   "cap_only": cap_only, "verdict": verdict})

# summary
safe = [r for r in report if r["verdict"].startswith(("SAFE_DISTILL", "MERGE_WITH_CAP_UNION"))]
print(f"pre-screened {len(report)} flagged duplicate groups:\n")
for r in report:
    print(f"[{r['verdict'].split('(')[0].strip()}] {r['base']}  ids={r['ids']}")
    if r.get("differing_fields"):
        print(f"      differs in: {r['differing_fields']}  alg_identical={r.get('algebra_identical')}")
    if r.get("cap_only") and not r.get("serves_capability_identical"):
        for i, caps in r["cap_only"].items():
            if caps:
                print(f"      {i} extra caps: {caps[:4]}")
print(f"\nSAFE to hand Exp-Dev for distill-verify: {len(safe)}/{len(report)}")
print("Pairs NOT cleanly safe are flagged REVIEW/DO_NOT_MERGE -- skunkworks guard against over-distill.")
OUT.write_text(json.dumps(report, indent=2))
print(f"\nwrote: {OUT}")
