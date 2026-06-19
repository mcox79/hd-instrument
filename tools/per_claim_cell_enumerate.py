"""F1.X1 (DECISION HOLD per-claim cell-trace): enumerate candidate EXP_ cells per scorecard claim.

Replaces the WALKED-BACK keyword-cross-reference audit (unreliable both directions; false negatives from
word-order / camelCase / separator mismatch, e.g. 'sq2_b6' vs 'substrate_b6_x_sq2'). Method:
  - SEPARATOR-STRIPPED normalization (lowercase; remove _ - / . space) so word-order + camelCase + separator
    variations all collapse -> alias tokens match as substrings regardless of how the cell was named.
  - RECALL-FAVORING: list ALL plausible candidates per claim (Skunkworks's per-cell read disambiguates).
    The keyword audit failed by being too NARROW; an enumeration-for-VET must not miss the real cell.

Output: per-claim candidate table (id + verdict + provenance_quality + run_mode + headline) -> Skunkworks VET.
Read-only; deterministic; laptop-safe. Exp-Dev enumerates; Skunkworks reads actual verdicts (authoritative).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.substrate_index.partition import PartitionedStore

# 18 scorecard claims -> distinctive alias tokens (already separator-stripped/lowercase form).
# Favor RECALL: multiple aliases incl. mechanism refs + bundle/cell codes + capability synonyms.
CLAIMS = [
    ("1  Drosophila MB sparse f=0.05 (Bundle A)",        ["drosophila", "mushroom", "mbsparse", "willshaw", "sparsef0", "kenyon"]),
    ("2  cf-RPE counterfactual rank-1 (Bundle A)",        ["cfrpe", "counterfactual", "rpe", "rank1", "klampfl"]),
    ("3  Position-binding + symmetric Hebbian (E1)",      ["positionbind", "posbind", "hebbian", "symmetrichebb", "bundlee1", "e1trigram"]),
    ("4  STDP-asymmetric (Bundle E E2)",                  ["stdp", "asymmetric", "bundlee2", "e2trigram", "spiketiming"]),
    ("5  DG sparse-expansion (B2; 48x)",                  ["dgsparse", "sparseexpansion", "b2sparse", "dentate", "treves", "48x", "expansion"]),
    ("6  D-ECR audit-preserving eviction (B6) FLAGSHIP",  ["decr", "decr", "eviction", "b6", "energycontribution", "auditpreserv", "evict"]),
    ("7  Cortical column ensemble (B4)",                  ["cortical", "column", "ensemble", "b4", "mountcastle", "disjointsplit"]),
    ("8a Active gating top-K (B3a) 13.8x",                ["activegating", "topk", "b3a", "gating", "writereduction", "138x", "13p8"]),
    ("8b Exp-smoothed surprise gating (B3b)",             ["surprisegating", "b3b", "expsmoothed", "surprise", "crosstalk"]),
    ("9  Logit-space sparse residual (B8)",               ["logit", "b8", "sparseresidual", "logitspace", "krahmer", "drip"]),
    ("10 Hierarchical aggregator (98.6% specialist)",     ["hierarchical", "aggregator", "986", "specialist", "scaleext", "5corpus", "crossdomain"]),
    ("11 SQ2 multi-hop K=12 FLAGSHIP",                    ["sq2", "multihop", "k12", "iteratedretrieval", "mode4", "12hop", "khop"]),
    ("12 cf-RPE + STDP heterogeneous (Bundle A comb)",    ["cfrpestdp", "heterogeneous", "bundleacombined", "superadditive", "rpestdp"]),
    ("13 Composition EXACT-1.0 (depth L=10000)",          ["composition", "burialdepth", "l10000", "depth10000", "exact1", "compositional", "comp11"]),
    ("14 Deletion certificate cos=1",                     ["deletioncert", "deletion", "certificate", "cos1", "evictioncert", "refusal"]),
    ("15 Drift detection kappa_3",                        ["kappa3", "kappa", "driftdetection", "drift", "isochoric", "nhse"]),
    ("16 B2xB4 capacity multiplicative (FLAGSHIP)",       ["b2xb4", "multiplicative", "capacitycomposition", "125000", "independencerecall", "b2b4"]),
    ("17 Tier-6 substrate-hybrid LLM (char-LM smoke)",    ["tier6", "charlm", "hybridllm", "substratehybrid", "attentionlayer", "bpc", "cognitivecore"]),
    ("18 Active gating efficiency 13.8x (B3a sub-metric)", ["efficiencycomposition", "b3axb3b", "16x", "efficiency", "b3a"]),
]


def norm(s: str) -> str:
    return re.sub(r'[^0-9a-z]', '', (s or "").lower())


def md(a, k):
    return (a.metadata or {}).get(k)


def main():
    ps = PartitionedStore(Path(__file__).resolve().parents[1] / "data/substrate_index")
    exp = [a for a in ps.all_atoms() if str(a.kind.name) == "EXPERIMENT_RECORD"]
    # precompute normalized search blob per atom (id + name + headline + hypothesis)
    rows = []
    for a in exp:
        blob = norm(a.id + " " + a.name + " " + str(md(a, "metrics_headline") or "") + " " + str(md(a, "hypothesis") or ""))
        rows.append((a, blob))
    print(f"=== PER-CLAIM CELL ENUMERATION | {len(exp)} EXP_ atoms | recall-favoring; separator-stripped match ===")
    print("(Exp-Dev enumerates candidates; Skunkworks reads actual verdict/metrics = authoritative.)\n")
    for label, aliases in CLAIMS:
        hits = []
        for a, blob in rows:
            matched = [al for al in aliases if al in blob]
            if matched:
                hits.append((len(matched), a, matched))
        # rank: more alias hits first, then cert-grade, then PASS
        hits.sort(key=lambda h: (h[0], md(h[1], "provenance_quality") == "CERT_CHAIN_GRADE",
                                 md(h[1], "verdict") in ("PASS", "LOAD_BEARING")), reverse=True)
        print(f"### CLAIM {label}")
        print(f"    aliases: {aliases}")
        if not hits:
            print("    >>> NO CANDIDATE CELLS FOUND (anchor-absent? OR alias-gap -- Skunkworks confirm) <<<")
        for n, a, matched in hits[:8]:
            print(f"    [{md(a,'verdict')}/{md(a,'provenance_quality')}/{md(a,'run_mode')}] {a.id[:60]}")
            print(f"        match={matched} :: {str(md(a,'metrics_headline'))[:70]}")
        if len(hits) > 8:
            print(f"    ... +{len(hits)-8} more candidates (full list available; truncated for readability)")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
