"""SKUNKWORKS build v1: operator-overlap on the REAL operator atoms, grounded in LESS-AUTHORED
structured fields (typed signatures + algebraic laws + served capabilities) rather than prose.

Enacts USER 2026-06-13: core atoms -> operators decompose into them -> overlap between functions
to DISTILL (redundancy / pure core) + EXPAND (gaps). And the grain-of-salt principle: results are
still partly authored, but grounding is BETTER than v0 prose-Jaccard, so the measurement should be
more accurate -- and it is VERSIONED so we can watch it converge as grounding improves.

Stdlib only; read-only on data/substrate_index/math/atoms.jsonl (does NOT touch relations index).
"""
import json, itertools
from collections import Counter
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")
OUT = Path("data/substrate_index/meta_substrate_operator_overlap_v1.json")

ops = []
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    a = json.loads(line)
    alg = a.get("algebra") or {}
    # An OPERATOR = an atom that DOES a computation (has an operation_type/role), i.e. a TOOL.
    if not (alg.get("operation_type") or alg.get("operation_role")):
        continue
    md = a.get("metadata") or {}
    laws = {k for k in ("associative", "commutative", "idempotent", "invertible") if md.get(k) is True}
    feat = {
        "id": a["id"], "tier": a.get("tier"),
        "op_type": alg.get("operation_type"), "op_role": alg.get("operation_role"),
        "vsa_family": alg.get("vsa_family"), "domain": alg.get("domain"),
        "sig_in": alg.get("signature_input_type"), "sig_out": alg.get("signature_output_type"),
        "laws": laws,
        "preserves": md.get("preserves"), "dual_of": md.get("dual_of"),
        "caps": set(a.get("serves_capability") or []),
    }
    ops.append(feat)

print(f"REAL operator atoms found (algebra.operation_type/role present): {len(ops)}")
print(f"op_type distribution: {Counter(o['op_type'] for o in ops).most_common(10)}")

def overlap(x, y):
    """Less-authored overlap: signature/type match + shared algebraic laws + shared capabilities."""
    s = 0.0; why = []
    if x["sig_in"] and x["sig_in"] == y["sig_in"]: s += 1.0; why.append(f"in={x['sig_in']}")
    if x["sig_out"] and x["sig_out"] == y["sig_out"]: s += 1.0; why.append(f"out={x['sig_out']}")
    if x["op_type"] and x["op_type"] == y["op_type"]: s += 1.0; why.append(f"type={x['op_type']}")
    if x["vsa_family"] and x["vsa_family"] == y["vsa_family"]: s += 0.5; why.append(f"vsa={x['vsa_family']}")
    shared_laws = x["laws"] & y["laws"]
    if shared_laws: s += 0.5 * len(shared_laws); why.append("laws=" + "+".join(sorted(shared_laws)))
    # dual_of is a strong intrinsic relation (mathematical inverse), least authored
    if x["dual_of"] == y["id"] or y["dual_of"] == x["id"]: s += 2.0; why.append("DUAL")
    cap_j = len(x["caps"] & y["caps"]) / len(x["caps"] | y["caps"]) if (x["caps"] | y["caps"]) else 0.0
    if cap_j > 0: s += 2.0 * cap_j; why.append(f"caps_j={cap_j:.2f}")
    return s, why

pairs = []
for x, y in itertools.combinations(ops, 2):
    s, why = overlap(x, y)
    if s >= 1.5:
        pairs.append({"a": x["id"], "b": y["id"], "score": round(s, 2), "why": why})
pairs.sort(key=lambda p: -p["score"])

# DISTILL: very-high-overlap pairs = redundancy / derivable-from candidates
distill = [p for p in pairs if p["score"] >= 3.0]
# EXPAND: capabilities served by exactly ONE operator (thin coverage = fragile / candidate gap)
cap_count = Counter()
for o in ops:
    for c in o["caps"]:
        cap_count[c] += 1
thin_caps = [c for c, n in cap_count.items() if n == 1]
# operator signatures held by only one operator (unique transforms = no redundancy, possibly gap)
sig_count = Counter((o["sig_in"], o["sig_out"]) for o in ops if o["sig_in"] and o["sig_out"])

print(f"\noverlap pairs (score>=1.5): {len(pairs)}  | DISTILL candidates (score>=3.0): {len(distill)}")
print("\nTOP 12 operator overlaps (structured, less-authored grounding):")
for p in pairs[:12]:
    print(f"  {p['score']:4.2f}  {p['a']:34s} <-> {p['b']:34s}  [{', '.join(p['why'][:3])}]")
print("\nDISTILL candidates (operators that may collapse to one / be derivable):")
for p in distill[:10]:
    print(f"  {p['score']:4.2f}  {p['a']} ~ {p['b']}  ({', '.join(p['why'][:3])})")
print(f"\nEXPAND signal: {len(thin_caps)} capabilities served by exactly ONE operator (thin coverage).")
print("  examples:", thin_caps[:6])

OUT.write_text(json.dumps({
    "n_operators": len(ops), "n_overlap_pairs": len(pairs),
    "distill_candidates": distill[:50],
    "thin_capabilities_expand_targets": thin_caps,
    "grounding": "v1_structured_signatures_laws_capabilities",
    "caveat": "still partly authored (signatures/caps are curated); less prose-biased than v0; "
              "fully bias-robust version uses provable decomposition (L6-PROOF) + learned vectors (gated post-rebuild)",
}, indent=2))
print(f"\nwrote versioned result: {OUT}")
