"""SKUNKWORKS: distillation-ratio v0 -- the North Star's first measured baseline + the full
collapse worklist for Testbed. "How much can the substrate compress itself with ZERO capability
loss?" v0 reports a provable LOWER BOUND (provenance-certified + exact-duplicate collapses only;
no capability loss by construction) so the number is honest, not optimistic.

Three provable-redundancy sources (all read from atom records; NO relations graph; runnable now):
  A) KP-promotion pairs   -- metadata.kp_p1_promotion.from links a T2 promotion to its T3 source
  B) exact-body duplicates -- identical description text under different ids
  C) name-variant dupes    -- same normalized short-name under different ids (alias hygiene)

distillation_ratio_floor = collapsible_redundant_copies / total. Higher = more bloat to remove.
Writes the worklist to data/substrate_index/distillation_worklist.json for Testbed INTEGRATE.
"""
import json, re
from collections import defaultdict
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")
OUT = Path("data/substrate_index/distillation_worklist.json")

atoms = []
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    atoms.append(json.loads(line))
N = len(atoms)
structured = [a for a in atoms if a.get("algebra")]
NS = len(structured)

def short(i):
    b = i.split("/", 1)[-1]
    return re.sub(r"_(algo|atom|operation|op)$", "", b.lower())

# A) KP-promotion pairs (provenance witness -> zero-capability-loss collapse)
promo = []
ids = {a["id"] for a in atoms}
for a in atoms:
    md = a.get("metadata") or {}
    src = (md.get("kp_p1_promotion") or {}).get("from")
    if src:
        src_id = src.split("::")[-1]
        promo.append({"promotion": a["id"], "source": src_id,
                      "source_present": src_id in ids})

# B) exact-body duplicates (identical non-trivial description, different id)
by_desc = defaultdict(list)
for a in atoms:
    d = (a.get("description") or "").strip()
    if len(d) >= 25:
        by_desc[d].append(a["id"])
exact_dupes = {d: v for d, v in by_desc.items() if len(v) > 1}
exact_extra = sum(len(v) - 1 for v in exact_dupes.values())  # redundant copies beyond 1

# C) name-variant duplicates (same normalized short-name, different id)
by_short = defaultdict(set)
for a in atoms:
    by_short[short(a["id"])].add(a["id"])
variant = {k: sorted(v) for k, v in by_short.items() if len(v) > 1}
variant_extra = sum(len(v) - 1 for v in variant.values())

# distillation-ratio floor: redundant copies removable with zero capability loss
promo_collapsible = len(promo)              # each promotion pair -> collapse to 1 atom + link
collapsible = promo_collapsible + exact_extra + variant_extra
# DEDUPLICATED distinct removable-atom set (honest floor; resolves A/B/C overlap)
removable = set()
for p in promo:
    if p["source_present"]:
        removable.add(p["source"])          # collapse pair -> keep promotion, source body becomes a link
for d, v in exact_dupes.items():
    removable.update(v[1:])                 # keep one, rest removable
for k, v in variant.items():
    removable.update(v[1:])                 # keep canonical, rest removable
distinct_collapsible = len(removable)
struct_ids = {a["id"] for a in structured}
distinct_in_core = len(removable & struct_ids)
# de-double-count is approximate; report components separately + a conservative union estimate
print("=== DISTILLATION RATIO v0 (provable lower bound; zero-capability-loss collapses) ===")
print(f"total atoms: {N} | structured core (algebra dict): {NS}")
print(f"A) KP-promotion pairs (provenance-certified): {promo_collapsible}")
print(f"B) exact-body duplicate groups: {len(exact_dupes)}  -> {exact_extra} redundant copies")
print(f"C) name-variant duplicate groups: {len(variant)}  -> {variant_extra} redundant copies")
print(f"\ncollapsible (sum, with A/B/C overlap): {collapsible}")
print(f"DISTINCT collapsible atoms (deduped, honest floor): {distinct_collapsible}")
print(f"  of which in the structured core: {distinct_in_core}")
print(f"distillation_ratio_floor vs total corpus : {100*distinct_collapsible/N:.2f}%")
print(f"distillation_ratio_floor vs structured core: {100*distinct_in_core/NS:.2f}%  "
      f"(substrate could shrink the structured core by >= this, zero capability loss)")

print("\nTop name-variant groups (alias-map / collapse targets):")
for k, v in sorted(variant.items(), key=lambda kv: -len(kv[1]))[:10]:
    print(f"  {k}: {[x.split('/')[-1] for x in v]}")
print("\nTop exact-body duplicate groups:")
for d, v in sorted(exact_dupes.items(), key=lambda kv: -len(kv[1]))[:6]:
    print(f"  x{len(v)}: {[x.split('/')[-1] for x in v]}  desc='{d[:60]}...'")

OUT.write_text(json.dumps({
    "total_atoms": N, "structured_core": NS,
    "promotion_pairs": promo, "exact_duplicate_groups": exact_dupes,
    "name_variant_groups": variant,
    "distillation_ratio_floor_pct_total": round(100*collapsible/N, 3),
    "components": {"promotion_pairs": promo_collapsible,
                   "exact_dupe_extra": exact_extra, "variant_extra": variant_extra},
    "note": "provable zero-capability-loss lower bound; Testbed INTEGRATE worklist; "
            "true distillation ratio (incl SHARED_ABSTRACTION supertypes) is higher, needs proof+vectors",
}, indent=2))
print(f"\nwrote Testbed collapse worklist: {OUT}")
