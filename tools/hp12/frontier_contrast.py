"""
frontier_contrast.py -- HP-12 demo: substrate certified deletion vs frontier-LLM model-editing (the moat narrative).

Holds the published model-editing residual-recall numbers and prints the contrast table + the structural-impossibility
argument used in the 5-minute demo. The substrate's measured residual is supplied by the extraction-attack cell
(exp_hp12_v1_extraction_attack_contrast_v1). ASCII-only, stdlib-only.

Published references (model editing leaves the fact RECOVERABLE):
  - ROME single edit: ~38% whitebox extraction success      (arXiv:2309.17410)
  - MEMIT batch edit: ~29% blackbox extraction success      (arXiv:2309.17410)
  - Sequential editing: catastrophic forgetting             (ACL 2024 Findings)
Substrate deletion is projection-out + RSA accumulator cert -> CATEGORICAL (target measured ~0% residual).
"""
from __future__ import annotations

PUBLISHED = [
    ("ROME (single edit)", "whitebox extraction", 0.38, "arXiv:2309.17410", "fact still recoverable from weights"),
    ("MEMIT (batch edit)", "blackbox extraction", 0.29, "arXiv:2309.17410", "fact still recoverable via prompting"),
    ("GRACE / adapters", "per-edit cert", None, "no published cert", "no cryptographic proof of edit"),
    ("frontier RAG (vector DB)", "deletion proof", None, "heuristic", "similarity removal, not cryptographic proof"),
]

STRUCTURAL_ARGUMENT = [
    "LLM weights are a parametric soup: no mechanism to (a) identify which weights encode a fact,",
    "(b) selectively remove them, (c) issue a cryptographic proof of the removal.",
    "Model editing (ROME/MEMIT/GRACE) reduces output probability but leaves the fact extractable",
    "(38%/29% residual) and offers no third-party-verifiable cert.",
    "Infinite context = fact lives in the session prompt, not a persistent KB (deletion = clear session; trivial,",
    "does not satisfy persistent-KB deletion). Frontier RAG vector-DB delete is heuristic similarity removal.",
    "Substrate: projection-out drives residual recall to ~0 (categorical) AND issues an RSA-accumulator cert a",
    "third party verifies with NO KB / NO trapdoor access. This is ARCHITECTURAL IMPOSSIBILITY, not cost.",
]


def print_contrast(substrate_residual: float = 0.0):
    print("=" * 78)
    print("HP-12 CONTRAST: certified per-fact deletion -- substrate vs frontier-LLM editing")
    print("=" * 78)
    print("%-26s %-22s %-12s %s" % ("system", "attack", "residual", "note"))
    print("-" * 78)
    for name, attack, val, ref, note in PUBLISHED:
        v = ("%.0f%%" % (val * 100)) if val is not None else "N/A"
        print("%-26s %-22s %-12s %s [%s]" % (name, attack, v, note, ref))
    print("%-26s %-22s %-12s %s" % ("SUBSTRATE (this work)", "whitebox+blackbox", "%.1f%%" % (substrate_residual * 100),
                                    "categorical deletion + RSA cert (third-party verifiable)"))
    print("-" * 78)
    for line in STRUCTURAL_ARGUMENT:
        print("  " + line)
    print("=" * 78)


if __name__ == "__main__":
    import sys
    r = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    print_contrast(r)
