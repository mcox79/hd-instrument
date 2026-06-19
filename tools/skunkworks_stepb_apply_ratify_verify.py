"""SKUNKWORKS completion-ratify verification for STEP-B APPLY (independent, Store-authoritative).

Exp-Dev reports 25/25 batches clean; Testbed's STEP-B-specific invariant verify not yet filed.
The cert-owner ratify must rest on an INDEPENDENT Store read, not the prover's self-report.
Confirms: RESEARCH_FINDING count, axiom_term, module liveness, 0 dup qids, and the STRUCTURAL
GUARD empirically (RESEARCH_FINDING atoms carry NO algebra field -> cannot enter axiom_term).
Light compute (counts/iteration; no NxN) -> laptop OK.
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "tools"))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import AtomKind
from atomize_experiment_records import axiom_term, module_liveness_ok

ps = PartitionedStore(REPO / "data/substrate_index")
atoms = list(ps.all_atoms())
total = len(atoms)
qids = [a.qualified_id for a in atoms]
dups = len(qids) - len(set(qids))
rf = [a for a in atoms if getattr(a, "kind", None) == AtomKind.RESEARCH_FINDING]

# structural guard: RF atoms must carry NO algebra (neither attr nor metadata key)
def has_algebra(a):
    if getattr(a, "algebra", None):
        return True
    md = getattr(a, "metadata", None)
    return bool(isinstance(md, dict) and md.get("algebra"))

rf_with_algebra = [a for a in rf if has_algebra(a)]
# tier distribution on RF
tiers = {}
for a in rf:
    t = (getattr(a, "metadata", {}) or {}).get("confidence_tier", "?")
    tiers[t] = tiers.get(t, 0) + 1

at, at_total = axiom_term(ps)
mods = module_liveness_ok()

print("=" * 78)
print(f"total atoms:              {total}")
print(f"RESEARCH_FINDING atoms:   {len(rf)}   (expected +1229 from STEP-B APPLY)")
print(f"  confidence_tier dist:   {tiers}")
print(f"duplicate qids:           {dups}   (expect 0)")
print(f"axiom_term:               {at}/{at_total}   (expect 206/206)")
print(f"module liveness (cap_pres): {mods}   (expect True = 6/6)")
print(f"RF atoms WITH algebra field: {len(rf_with_algebra)}   (MUST be 0 = structural guard holds)")
print("=" * 78)
ok = (len(rf) >= 1229 and dups == 0 and at == 206 and at_total == 206 and mods and not rf_with_algebra)
print("RATIFY-VERIFY:", "PASS -- all invariants hold; structural guard empirically confirmed" if ok
      else "FAIL -- investigate before ratify")
