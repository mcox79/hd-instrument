"""SKUNKWORKS: ABSTRACTION ratio (F2 metric) -- the REAL conceptual self-optimization number,
counterpart to the HYGIENE ratio. Consumes Exp-Dev's CELL-DISTILL-VERIFY-2 output (real data).

Abstraction = unifying N distinct operators under ONE proven shared supertype / theorem-link /
inverse-pair. Each such collapse reduces distinct top-level primitives by (N-1). Two numbers:
  POTENTIAL (ceiling): all non-DISTINCT candidate groups -> what abstraction is AVAILABLE.
  REALIZED  (proven) : only groups whose abstraction is GROUNDED right now:
      SHARED_ABSTRACTION -> realized iff the shared out_type is ATOMIZED (a supertype object exists)
      THEOREM_LINKED     -> realized iff derivation_present is True (a typed derivation edge exists)
      INVERSE_PAIR       -> realized iff inverse_authored is True
REALIZED is the F2 floor; it is currently expected ~0 because the composite type-atoms are not yet
authored (F2 gate). It flips nonzero the instant Testbed atomizes e.g. parameter_vector or Exp-Dev
wires a derivation edge. NOTE: a realized abstraction is only SAFE if it also passes the no-regression
gate (capability preserved) -- that is F1/F3-gated; this tool reports proof-grounding, flags the gate.

Read-only; consumes real VERIFY-2 json + atoms.jsonl. numpy not needed.
"""
import json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
V2 = REPO / "data/substrate_index/bench_reports/distill_verify_2_class_b_relationship.json"
ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"


def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


# atomized type names (to check if a SHARED_ABSTRACTION's shared out_type has a supertype object)
atomized = set()
n_ops = 0
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    a = json.loads(line)
    alg = a.get("algebra") or {}
    if alg.get("operation_type") or alg.get("operation_role"):
        n_ops += 1
    atomized.add(norm(a["id"].split("/", 1)[-1]))
    atomized.add(norm(a.get("name", "")))
    for al in (a.get("aliases") or []):
        atomized.add(norm(al))
atomized.discard("")

data = json.loads(V2.read_text())
groups = data.get("groups", [])

# ONLY SHARED_ABSTRACTION is true conceptual COMPRESSION (N operators subsumed under 1 supertype,
# reducing distinct top-level primitives by N-1). THEOREM_LINKED + INVERSE_PAIR are RELATIONS between
# primitives -- they do NOT remove a primitive (both members still exist) -- so they are NOT counted in
# the abstraction ratio; reported separately as proven structure.

def shared_realized(g):
    outs = g.get("out_types") or []
    return bool(outs) and all(norm(o) in atomized for o in outs)  # shared supertype object atomized


pot_primitives = real_primitives = 0
cd_pot = cd_real = 0
abs_rows = []; rel_rows = []; cd_rows = []
for g in groups:
    v = g.get("verdict"); k = g.get("n_found", len(g.get("ids", [])))
    if k < 2:
        continue
    if v == "SHARED_ABSTRACTION":
        pot_primitives += (k - 1)
        r = shared_realized(g)
        if r:
            real_primitives += (k - 1)
        abs_rows.append((g.get("group"), k, "REALIZED" if r else "candidate (gated on out_type atomization)",
                         g.get("out_types")))
    elif v == "CROSS_DOMAIN_ABSTRACTION":
        # V2.2 additive class (Exp-Dev b87c511d): same output_type + >=2 domains + >=2 distinct ops.
        # 18th-rule gated at run-time (downgraded to DISTINCT if shared output isn't grounded supertype).
        # Counts as primitive-reducing per Research SYNTHESIS-2 DECISION 1 (Option B ADOPT).
        cd_pot += (k - 1)
        r = shared_realized(g)
        if r:
            cd_real += (k - 1)
        cd_rows.append((g.get("group"), k, "REALIZED" if r else "candidate (gated on out_type atomization)",
                        g.get("out_types"), g.get("domains")))
    elif v in ("THEOREM_LINKED", "INVERSE_PAIR"):
        grounded = (g.get("derivation_present") is True) or (g.get("inverse_authored") is True)
        rel_rows.append((g.get("group"), v, k, "grounded" if grounded else "candidate",
                         g.get("derivation_present"), g.get("inverse_authored")))

total_pot = pot_primitives + cd_pot
total_real = real_primitives + cd_real

denom = max(n_ops, 1)
print("=== ABSTRACTION RATIO v0 (F2 metric; conceptual COMPRESSION; V2.2-aware) ===")
print(f"operators (denominator): {n_ops}")
print(f"SHARED_ABSTRACTION (same-domain) -- POTENTIAL: {pot_primitives}/{denom} = {100*pot_primitives/denom:.1f}%")
print(f"SHARED_ABSTRACTION (same-domain) -- REALIZED: {real_primitives}/{denom} = {100*real_primitives/denom:.1f}%")
print(f"CROSS_DOMAIN_ABSTRACTION (V2.2 b87c511d) -- POTENTIAL: {cd_pot}/{denom} = {100*cd_pot/denom:.1f}%")
print(f"CROSS_DOMAIN_ABSTRACTION (V2.2) -- REALIZED: {cd_real}/{denom} = {100*cd_real/denom:.1f}%")
print(f"TOTAL POTENTIAL abstraction ratio: {total_pot}/{denom} = {100*total_pot/denom:.1f}%")
print(f"TOTAL REALIZED  abstraction ratio: {total_real}/{denom} = {100*total_real/denom:.1f}%  (F2 floor)")
print(f"F2 status: {'REALIZED>0 -- F2 PROGRESSING' if total_real>0 else 'REALIZED=0 -- F2 still UNMET'}\n")
print("SHARED_ABSTRACTION groups (same-domain; primitive-reducing):")
for name, k, st, outs in abs_rows:
    print(f"  [{st}] {name} n={k} out_types={outs}")
print("\nCROSS_DOMAIN_ABSTRACTION groups (V2.2 b87c511d; same-output + multi-domain; primitive-reducing):")
for name, k, st, outs, doms in cd_rows:
    print(f"  [{st}] {name} n={k} out_types={outs} domains={doms}")
print("\nProven RELATIONS (THEOREM_LINKED / INVERSE_PAIR -- NOT counted as compression; both members persist):")
for name, v, k, st, deriv, inv in rel_rows:
    print(f"  [{st}] {name} {v} n={k} (derivation={deriv}, inverse_authored={inv})")
print("\nHONEST NOTE per Exp-Dev SYNTHESIS-2 + USER 15th rule: F2 is AUTHORING-DEPENDENT. "
      f"Today's REALIZED = {100*total_real/denom:.1f}%; ~half is today's deliberate operator-retyping "
      "(authoring-driven), ~half is pre-existing structure (authoring-independent floor ~9 operators / 4 families).")
