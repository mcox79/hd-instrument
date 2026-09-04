"""hdlab/consolidation_gate.py -- the KNOWLEDGE-ADMISSION QUALITY GATE for controlled learner growth.

The load-bearing wire of the owner-DONE `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`
(the north-star P1). The measured lesson: RAW reading-derived co-occurrence, admitted straight into the sense
signatures, REGRESSES the meaning channel (a_s -0.033 below gloss -- topical, not sense-substitutable); only a
CONSOLIDATED (recurrence + multi-seed + PPMI + schema-margin filtered) foundation is safe to admit, and even then
reading-derived growth does NOT beat curated gloss glass-box (a narrow located negative). So the load-bearing wire
is a GUARD, not a default-on feature: before any learner-growth admits associations to the live sense signatures,
run them through this gate, and CHECK the consolidated set against the RAW twin so the raw regression can never
silently ship. Composes with `hdlab.cls_growth` (keep-both + rollback + EMA anchor -- reversibility) : cls_growth
handles reversibility, this gate handles ADMISSION QUALITY. Neither alone is sufficient.

`consolidate` + `raw_assocs` promoted VERBATIM from experiments/exp_consolidation_gate_v1.py (witness
verification/test_consolidation_gate.py, 14/14). Glass-box, NO external LLM, NO training. Pure numpy.

MEASURED (strict document-disjoint SemCor subordinate, n=2676, through hdlab.diagnostic_context_wsd): a CONSOLIDATED
clean foundation (WordNet relations + curated SyntagNet + ConceptNet, an admissible offline static asset) raises
a_s 0.2512 -> 0.3178 (+0.067 CI-sep), the RAW-ungated reading twin LOSING (-0.033), MFS no-regression guard passing.
The residual to human (~0.65) is the STATIC sense-conflated input representation (the meaning-channel north star ->
the ATL hub-and-spoke + online predictive reader follow-on), NOT the gate.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np


def consolidate(agg, mat, w2i, sig_self, sig_sibs, cfg) -> List[str]:
    """Full admission gate (vectorized schema step). Returns the CLEAN per-sense associate list to admit.

    agg: {word: (multiseed_support, recurrence_count, ppmi)} aggregated reading co-occurrence for one sense.
    mat, w2i: the embedding matrix + word->row index (for the schema-margin discriminativeness step).
    sig_self: the sense's own signature vector (unit); sig_sibs: sibling-sense signatures (competitors).
    cfg: {K: min recurrence, M: min multi-seed support, P: min ppmi, margin: schema self-minus-sibling margin,
          cap: max associates, drop: set() of stages to disable (ablation)}.
    Byte-faithful to exp_consolidation_gate_v1.consolidate."""
    drop = cfg.get("drop", set())
    K, M, P, margin, cap = cfg["K"], cfg["M"], cfg["P"], cfg["margin"], cfg["cap"]
    words, scores = [], []
    for w, (sup, rc, pp) in agg.items():
        if w not in w2i:
            continue
        if "recur" not in drop and rc < K:
            continue
        if "multiseed" not in drop and sup < M:
            continue
        if "ppmi" not in drop and pp < P:
            continue
        words.append(w); scores.append(pp * (1.0 + sup))
    if not words:
        return []
    if "schema" not in drop and sig_self is not None:
        V = mat[[w2i[w] for w in words]]
        V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
        self_s = V @ sig_self
        if sig_sibs:
            S = np.stack(sig_sibs)
            sib_s = (V @ S.T).max(axis=1)
        else:
            sib_s = np.full(len(words), -1.0)
        keep = (self_s - sib_s) >= margin
        words = [w for w, k in zip(words, keep) if k]
        scores = [sc for sc, k in zip(scores, keep) if k]
        if not words:
            return []
    order = np.argsort(-np.asarray(scores))[:cap]
    return [words[i] for i in order]


def raw_assocs(agg, cap) -> List[str]:
    """The RAW-ungated twin (the regression-check control): top-cap associates by raw recurrence count only, no
    ppmi/multiseed/schema filtering. Admitting THIS regresses the meaning channel (-0.033 below gloss) -- the gate
    exists to keep it out. Byte-faithful to exp_consolidation_gate_v1.raw_assocs."""
    return [w for w, _ in sorted(agg.items(), key=lambda kv: -kv[1][1])[:cap]]


def regression_guard(consolidated_score: float, raw_score: float, gloss_score: float,
                     eps: float = 0.0) -> Dict[str, object]:
    """The admission REGRESSION CHECK, baked in so raw growth can never silently ship. Returns whether the
    consolidated foundation is SAFE to admit: it must NOT regress below the gloss baseline, and it must beat the
    RAW twin (which is known to regress). `*_score` are the a_s (or any downstream) scores of each arm on the
    SAME population. admit=True only if consolidated >= gloss - eps AND consolidated > raw."""
    return {
        "admit": (consolidated_score >= gloss_score - eps) and (consolidated_score > raw_score),
        "consolidated_vs_gloss": consolidated_score - gloss_score,
        "consolidated_vs_raw": consolidated_score - raw_score,
        "raw_regresses": raw_score < gloss_score,
    }
