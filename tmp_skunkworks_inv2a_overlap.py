"""SKUNKWORKS INV-2a: candidate-set overlap of KP signals P1/P3/P4 on CACHED pre-rebuild snapshots.
Read-only; no live graph; no relations; no LLM. Tests the OVERLAP arm of INV-2 pre-reg only.
The rank-correlation arm (Spearman/EFA) needs all candidates scored on ALL THREE signals
(in-degree + bisimulation-class + codebook-cos) which requires the live graph -> gated post-rebuild.
"""
import json, itertools
from pathlib import Path

B = Path("data/substrate_index/bench_reports")
p1 = json.loads((B / "kp_p1_frequency_promotion_candidates.json").read_text())
p3 = json.loads((B / "kp_p3_shares_math_bisimulation_classes.json").read_text())
p4 = json.loads((B / "kp_p4_replay_consolidation_archetypes.json").read_text())

# Candidate atom sets per signal (exact atom ids as authored)
set_p1 = {c["atom"] for c in p1["candidates"]}
set_p3 = {a for cls in p3["classes"] for a in cls}
set_p4 = {m for cand in p4["candidates"] for m in cand["members"]}

print("=== candidate-set sizes (exact ids) ===")
print(f"P1 (in-degree, T3 records): {len(set_p1)}")
print(f"P3 (bisimulation nodes):    {len(set_p3)}")
print(f"P4 (codebook archetypes):   {len(set_p4)}")

def norm(a):
    # strip tier prefix and common suffix noise to catch near-duplicate ids across signals
    base = a.split("/", 1)[-1]
    for suf in ("_atom", "_algo"):
        if base.endswith(suf):
            base = base[: -len(suf)]
    return base

def report(name, a, b):
    inter_exact = a & b
    union = a | b
    jac = len(inter_exact) / len(union) if union else 0.0
    # overlap fraction = |intersection| / |smaller set| (Research's pre-reg phrasing)
    ovl = len(inter_exact) / min(len(a), len(b)) if min(len(a), len(b)) else 0.0
    na, nb = {norm(x) for x in a}, {norm(x) for x in b}
    inter_norm = na & nb
    print(f"\n--- {name} ---")
    print(f"exact intersection: {sorted(inter_exact) or '[]'}  (n={len(inter_exact)})")
    print(f"Jaccard(exact)={jac:.3f}  overlap_frac(|inter|/min)={ovl:.3f}")
    extra_norm = inter_norm - {norm(x) for x in inter_exact}
    if extra_norm:
        print(f"normalized-only matches (name-variant, review): {sorted(extra_norm)}")
    return ovl

print("\n=== pairwise overlap (INV-2 OVERLAP arm) ===")
o12 = report("P1 vs P3", set_p1, set_p3)
o13 = report("P1 vs P4", set_p1, set_p4)
o23 = report("P3 vs P4", set_p3, set_p4)

# atoms scoreable on >=2 signals (needed for ANY rank correlation)
print("\n=== atoms present in >=2 signals (exact id) ===")
triple = {}
for nm, s in (("P1", set_p1), ("P3", set_p3), ("P4", set_p4)):
    for a in s:
        triple.setdefault(a, []).append(nm)
multi = {a: sigs for a, sigs in triple.items() if len(sigs) >= 2}
for a, sigs in sorted(multi.items()):
    print(f"  {a}: {sigs}")
print(f"n atoms with >=2 signals: {len(multi)}")
print(f"n atoms with all 3 signals: {sum(1 for s in triple.values() if len(s)==3)}")

max_ovl = max(o12, o13, o23)
print("\n=== INV-2 OVERLAP-arm verdict vs Research pre-reg bands ===")
print(f"max pairwise overlap_frac = {max_ovl:.3f}")
print(" pre-reg: HARD-PASS(independent) overlap<0.30 ; HARD-FAIL(latent) overlap>0.70")
if max_ovl < 0.30:
    print(" => OVERLAP arm: HARD-PASS direction (candidate sets near-disjoint -> NOT one shared candidate pool)")
elif max_ovl > 0.70:
    print(" => OVERLAP arm: HARD-FAIL direction")
else:
    print(" => OVERLAP arm: MIDDLE")
print("\nNOTE: rank-correlation arm (Spearman/Kendall/EFA) is NOT COMPUTABLE on cached files:")
print(f"  only {len(multi)} atoms carry >=2 signal scores and the score types are incommensurable")
print("  (in-degree vs class-size vs cos). Computing rho needs ALL candidates scored on ALL 3")
print("  signals -> requires live graph (in-degree + bisimulation) -> GATED post-rebuild (INV-2b).")
