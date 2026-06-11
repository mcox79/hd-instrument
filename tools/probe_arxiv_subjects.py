"""Probe arxiv_2m subject distribution by keyword signals.

Single-purpose script. Sampling first 100K facts; report keyword hit-rates
to determine whether the existing arxiv_2m corpus has math.* coverage or is
ML-papers-only.

Per Research INGEST_APPROVAL refinement 1: this verification saves a 22h
re-ingest if math papers are already present.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

PATH = Path(r"C:\dev\hd-instrument\data\substrate_state\arxiv_2m\facts.jsonl")

PATTERNS = {
    "ml_keywords": re.compile(r"neural|deep learn|machine learn|classif|train.*model", re.I),
    "math_theorem_lang": re.compile(r"theorem|lemma|corollary|proof of|q\.e\.d|holds.*for.*all", re.I),
    "math_topology": re.compile(r"manifold|topolog|homotop|cohomol|euler char|orbifold", re.I),
    "math_algebra": re.compile(r"abelian|nilpotent|isomorph|tensor product|module over|homomorphism", re.I),
    "math_analysis": re.compile(r"hilbert space|banach|sobolev|distribution|measure-theoretic|fourier transform", re.I),
    "math_logic_set": re.compile(r"forcing|cardinal|continuum hypothesis|axiom of choice|godel", re.I),
    "math_number_theory": re.compile(r"riemann zeta|prime ideal|elliptic curve|galois|number field", re.I),
    "physics": re.compile(r"hamiltonian|lagrangian|gauge|spinor|quantum field", re.I),
    "info_theory": re.compile(r"shannon|channel capacity|entropy|rate distortion|coding theorem", re.I),
}

def main():
    if not PATH.exists():
        print(f"MISSING: {PATH}")
        sys.exit(1)

    counts = {k: 0 for k in PATTERNS}
    n = 0
    with open(PATH, encoding="utf-8") as f:
        for line in f:
            n += 1
            if n > 100000:
                break
            try:
                txt = json.loads(line)["fact"]
            except Exception:
                continue
            for k, p in PATTERNS.items():
                if p.search(txt):
                    counts[k] += 1

    print(f"sampled {n} facts")
    print(f"path: {PATH}")
    print()
    print(f"{'pattern':<22} {'hits':>8}  {'pct':>6}")
    print("-" * 40)
    for k, v in counts.items():
        print(f"{k:<22} {v:>8}  {100.0 * v / n:>5.1f}%")

if __name__ == "__main__":
    main()
