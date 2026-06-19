"""SKUNKWORKS DETECT: extract the full Class B candidate set for Exp-Dev's CELL-DISTILL-VERIFY-2.

Class B = same-capability / same-output operator GROUPS that LACK a built-in provenance witness
(no metadata.kp_p1_promotion link) -> they need a REAL L6-PROOF abstraction/derivation check,
unlike Class A promotion-pairs (provenance-certified, route to Testbed schema-collapse).

Writes Exp-Dev's exact schema contract to tools/substrate_distill_class_b_candidates.json:
  {"groups": [{"group": "<name>", "members": ["<id>",...], "expected": "<verdict>"|omitted}]}
expected in {MERGEABLE, SHARED_ABSTRACTION, THEOREM_LINKED, DISTINCT} or omitted (-> TRIAGED).
Read-only on atoms.jsonl; NO relations graph needed (Exp-Dev reads relations.jsonl itself).
"""
import json, itertools
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")
OUT = Path("tools/substrate_distill_class_b_candidates.json")

ops = []
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    a = json.loads(line)
    alg = a.get("algebra") or {}
    if not (alg.get("operation_type") or alg.get("operation_role")):
        continue
    md = a.get("metadata") or {}
    ops.append({
        "id": a["id"], "base": a["id"].split("/", 1)[-1],
        "sig_out": alg.get("signature_output_type"), "op_type": alg.get("operation_type"),
        "vsa_family": alg.get("vsa_family"), "dual_of": md.get("dual_of"),
        "caps": set(a.get("serves_capability") or []),
        "promo_from": (md.get("kp_p1_promotion") or {}).get("from"),
    })
by_id = {o["id"]: o for o in ops}

def is_class_a(x, y):
    """promotion pair / cross-tier same-base duplicate -> Class A, EXCLUDE from B."""
    if x["base"] == y["base"]:
        return True
    fa = (x["promo_from"] or "").split("::")[-1]
    fb = (y["promo_from"] or "").split("::")[-1]
    return fa == y["id"] or fb == x["id"] or fa == y["base"] or fb == x["base"]

# functional-overlap edges among operators (same output type + shared caps, OR identical caps)
edges = []
for x, y in itertools.combinations(ops, 2):
    if is_class_a(x, y):
        continue
    cap_j = len(x["caps"] & y["caps"]) / len(x["caps"] | y["caps"]) if (x["caps"] | y["caps"]) else 0.0
    same_out = x["sig_out"] and x["sig_out"] == y["sig_out"]
    dual = (x["dual_of"] == y["id"] or y["dual_of"] == x["id"])
    if cap_j >= 0.5 or (same_out and cap_j > 0) or dual:
        edges.append((x["id"], y["id"]))

# connected components -> candidate groups
parent = {o["id"]: o["id"] for o in ops}
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for a, b in edges:
    parent[find(a)] = find(b)
comps = {}
for o in ops:
    comps.setdefault(find(o["id"]), []).append(o["id"])
groups = [sorted(v) for v in comps.values() if len(v) >= 2]

# known-anchor labels + expected; everything else TRIAGED (expected omitted)
def label_and_expected(members):
    s = {m.split("/", 1)[-1] for m in members}
    if {"gradient_descent", "adam_optimizer", "stochastic_gradient_descent"} & s and len(s & {
        "gradient_descent","adam_optimizer","stochastic_gradient_descent","lbfgs_quasi_newton",
        "conjugate_gradient","levenberg_marquardt","rmsprop","momentum"}) >= 2:
        return "optimizer_family", "SHARED_ABSTRACTION"
    if {"circular_convolution", "discrete_fourier_transform", "fast_fourier_transform"} & s and len(s) >= 2:
        return "convolution_theorem", "THEOREM_LINKED"
    if any(m.endswith("fhrr_bind") for m in members) and any(m.endswith("fhrr_unbind") for m in members):
        return "fhrr_bind_unbind_dual", "DISTINCT"  # inverses: must NOT merge -> discrimination test
    return "_".join(sorted(s)[:2]) + f"_grp{len(members)}", None

out_groups = []
for g in sorted(groups, key=lambda x: -len(x)):
    # dedupe by short name (T2/x and T3/x are the same functional operator for the proof test)
    seen, members = set(), []
    for m in g:
        sn = m.split("/", 1)[-1]
        if sn not in seen:
            seen.add(sn); members.append(m)
    if len(members) < 2:
        continue
    name, exp = label_and_expected(members)
    entry = {"group": name, "members": members}
    if exp:
        entry["expected"] = exp
    out_groups.append(entry)

OUT.write_text(json.dumps({"groups": out_groups,
                           "provenance": "skunkworks operator-overlap DETECT; Class A promotion-pairs EXCLUDED",
                           "n_groups": len(out_groups)}, indent=2))
print(f"operators scanned: {len(ops)}  | functional-overlap edges: {len(edges)}  | Class B groups: {len(out_groups)}")
for e in out_groups:
    exp = e.get("expected", "TRIAGED")
    print(f"  [{exp:17s}] {e['group']:34s} members={[m.split('/')[-1] for m in e['members']]}")
print(f"\nwrote Exp-Dev schema file: {OUT}")
