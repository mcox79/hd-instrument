"""SKUNKWORKS EXPAND probe: the gaps toward a self-complete (fully optimized) substrate.

The 'expand' half of optimization: what does the substrate COMPUTE OVER but not ATOMIZE?
Operators carry typed signatures (signature_input_type / signature_output_type). If a type appears
in a signature but no atom DEFINES it, that is a TYPING GAP -- the substrate operates on a type it
has not made explicit. Authoring those types is the precondition for the ABSTRACTION ratio (you
cannot prove 'these 3 optimizers share a supertype' until the shared type/object is atomized).

So this probe directly unblocks the conceptual-distillation (abstraction) path, not just hygiene.
Also reports capability coverage (thinly-served capabilities = fragile single points to expand).
Stdlib only; read-only on atom records; NO relations graph (runnable now).
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")
OUT = Path("data/substrate_index/expand_typing_gaps.json")

atoms = []
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if line.strip():
        atoms.append(json.loads(line))

def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")

# what is atomized: normalized atom short-ids + names + aliases + about_topic
atomized = set()
for a in atoms:
    atomized.add(norm(a["id"].split("/", 1)[-1]))
    atomized.add(norm(a.get("name", "")))
    for al in (a.get("aliases") or []):
        atomized.add(norm(al))
    at = (a.get("algebra") or {}).get("about_topic")
    if at:
        atomized.add(norm(at))
atomized.discard("")

# collect signature types used by operators
sig_use = Counter()
sig_by_op = defaultdict(list)
for a in atoms:
    alg = a.get("algebra") or {}
    for f in ("signature_input_type", "signature_output_type"):
        v = alg.get(f)
        if v:
            # a signature can be compound (e.g. feature_vector_label_pair); record whole + parts
            sig_use[v] += 1
            sig_by_op[v].append(a["id"].split("/", 1)[-1])

# a signature type is a GAP if neither it nor any of its underscore-parts is atomized
def covered(sig):
    n = norm(sig)
    if n in atomized:
        return True
    parts = [p for p in n.split("_") if len(p) >= 3]
    # consider covered if a meaningful multi-token subphrase is atomized
    for i in range(len(parts)):
        for j in range(i + 2, len(parts) + 1):
            if "_".join(parts[i:j]) in atomized:
                return True
    return False

gaps = sorted([(s, c) for s, c in sig_use.items() if not covered(s)], key=lambda x: -x[1])

print("=== EXPAND probe: typing gaps (types operators compute over but the substrate has NOT atomized) ===")
print(f"distinct signature types used by operators: {len(sig_use)}")
print(f"atomized name/alias/topic tokens: {len(atomized)}")
print(f"TYPING GAPS (signature type not atomized): {len(gaps)}\n")
print("gap signature types (authoring these unblocks ABSTRACTION-ratio proofs):")
for s, c in gaps[:25]:
    print(f"  x{c:2d}  {s:42s} used by: {sorted(set(sig_by_op[s]))[:3]}")

# secondary: capability coverage (thin = fragile expand target)
cap_count = Counter()
for a in atoms:
    for cpt in (a.get("serves_capability") or []):
        cap_count[cpt] += 1
thin = [c for c, n in cap_count.items() if n == 1]
print(f"\ncapability coverage: {len(cap_count)} distinct served; {len(thin)} served by exactly ONE atom (fragile).")
print("  fragile examples:", [c.split('::')[-1] for c in thin[:6]])

OUT.write_text(json.dumps({
    "n_signature_types": len(sig_use),
    "typing_gaps": [{"type": s, "n_uses": c, "used_by": sorted(set(sig_by_op[s]))} for s, c in gaps],
    "thin_capabilities": thin,
    "note": "typing gaps = EXPAND worklist; atomizing these is the precondition for ABSTRACTION-ratio "
            "(conceptual distillation) proofs -- the real optimization beyond hygiene",
}, indent=2))
print(f"\nwrote EXPAND worklist: {OUT}")
