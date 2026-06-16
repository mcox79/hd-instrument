"""SKUNKWORKS: triage the 53 typing gaps into author-fresh vs alias-to-existing, so Testbed's
type-atom authoring (the abstraction-ratio unblock) targets only TRUE gaps. Honors my own caveat
that the 53 is an upper bound (some are name-resolution, not true absence).

3 buckets:
  EXISTS       -- the full type matches an existing atom name/alias -> ALIAS, do not author.
  SPECIALIZES  -- the head-noun (e.g. 'vector' in parameter_vector) has a general atom (vector_space)
                  but the specific compound type is absent -> author the specific type SPECIALIZES general.
  TRUE_GAP     -- no related atom at all -> author fresh.
Stdlib only; read-only.
"""
import json, re
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")
GAPS = Path("data/substrate_index/expand_typing_gaps.json")
OUT = Path("data/substrate_index/typing_gap_triage.json")

def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")

# index atom name tokens -> atom id, and full normalized names
name_to_id = {}
token_to_ids = {}
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    a = json.loads(line)
    cands = [a["id"].split("/", 1)[-1], a.get("name", "")] + (a.get("aliases") or [])
    at = (a.get("algebra") or {}).get("about_topic")
    if at:
        cands.append(at)
    for c in cands:
        n = norm(c)
        if not n:
            continue
        name_to_id.setdefault(n, a["id"])
        for t in n.split("_"):
            if len(t) >= 3:
                token_to_ids.setdefault(t, set()).add(a["id"])

gaps = json.loads(GAPS.read_text())["typing_gaps"]

def triage(gtype):
    n = norm(gtype)
    if n in name_to_id:
        return "EXISTS", name_to_id[n]
    toks = [t for t in n.split("_") if len(t) >= 3]
    # head noun = last token (parameter_VECTOR, weight_VECTOR, state_SEQUENCE)
    head = toks[-1] if toks else ""
    if head in token_to_ids:
        ex = sorted(token_to_ids[head])[0]
        return "SPECIALIZES", ex
    # any token has an atom?
    for t in toks:
        if t in token_to_ids:
            return "SPECIALIZES", sorted(token_to_ids[t])[0]
    return "TRUE_GAP", None

buckets = {"EXISTS": [], "SPECIALIZES": [], "TRUE_GAP": []}
for g in gaps:
    b, rel = triage(g["type"])
    buckets[b].append({"type": g["type"], "n_uses": g["n_uses"], "related_atom": rel,
                       "used_by": g["used_by"]})

print("=== TYPING-GAP TRIAGE (accelerates Testbed type authoring) ===")
for b in ("TRUE_GAP", "SPECIALIZES", "EXISTS"):
    print(f"\n[{b}] {len(buckets[b])} types")
    for e in sorted(buckets[b], key=lambda x: -x["n_uses"])[:18]:
        rel = f" ~ {e['related_atom']}" if e["related_atom"] else ""
        print(f"  x{e['n_uses']:2d} {e['type']:40s}{rel}")
print(f"\nSUMMARY: TRUE_GAP={len(buckets['TRUE_GAP'])} (author fresh) | "
      f"SPECIALIZES={len(buckets['SPECIALIZES'])} (author as SPECIALIZES existing) | "
      f"EXISTS={len(buckets['EXISTS'])} (alias only)")
print("=> author-needed (TRUE_GAP + SPECIALIZES) is the real EXPAND worklist for the abstraction ratio.")
OUT.write_text(json.dumps(buckets, indent=2))
print(f"wrote: {OUT}")
