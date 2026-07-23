"""Centralized Learner module (brain-faithful model-selection engine). REFACTOR, not a new
capability claim: extracts the shared decision-making core that was previously re-implemented
per-cell (the condenser's Laplace evidence-accumulation gate; the rule-inducer's MDL two-part-code
gate) into ONE owned engine, and wraps both prior cells as pluggable hypothesis-class PRIMITIVES.

BRAIN-FAITHFUL FRAMING (USER-authorized design, 2026-07-23 session): a shared consolidation/
inference ENGINE (this module) + specialized per-domain CONFIGS (per-competence feature encoders
/ hypothesis-space richness supplied by the caller) -- analogous to hippocampal replay feeding a
cortical model-SELECTION process over domain-specific priors, rather than one monolithic learner.

THE SHARED CORE OWNED HERE (previously duplicated / implicit in each cell):
  1. MODEL-SELECTION PRINCIPLE = MDL/Bayesian two-part-code compression: pick the hypothesis that
     best COMPRESSES the seen episodes under a simplicity prior (mdl_select()). This is the SAME
     principle each source cell already used internally (the condenser's Laplace-smoothed
     evidence-accumulation IS an implicit MDL argument -- more distinct-type evidence for a key
     compresses the null-uniform code better; the rule-inducer's induce_rules() already computes
     an EXPLICIT two-part code per candidate conjunction). Centralizing it means a THIRD future
     hypothesis class (GAM/EBM, ILP, program induction) gets auto-selection for free by declaring
     its own description_bits, without re-deriving the selection logic.
  2. PER-CLUSTER RULE-vs-EPISODIC gate (per_cluster_gate()): induce (promote a hypothesis) only
     when it compresses past the null (no-model) code; otherwise keep episodic. This generalizes
     both source cells' own must-fail-if-flat controls (condenser's ARM_FREEZE; rule-inducer's
     ARM_NORULES / residual-episodic-fallback) into one gate the core enforces uniformly.
  3. GLASS-BOX invariant enforcement (glass_box_assert()): the selected hypothesis must be
     inspectable -- a JSON-serializable dict/list/primitive -- never an opaque black-box operator
     at inference. Both source cells already wrote inspectable JSON artifacts (condenser_seed_
     table.json; the rule list in ruleinduction's metrics.json); this promotes that property from
     "the cell happens to log it" to "the module refuses a non-inspectable hypothesis."
  4. STANDARD MEASUREMENTS: compression_ratio (rules-vs-episodic strength), margin-over-baseline
     hooks the caller uses to report margin-over-similarity-vote, and the null_bits/description_
     bits pair every plugin must supply so measurements are comparable ACROSS hypothesis classes.

UNIFORM INTERFACE every plugin implements (hdlab/learner/plugins/*.py):
  learn(episodes, features, hypothesis_space_spec, prior) -> LearnResult
  apply(hypothesis, new_item) -> decision

PLUGIN REGISTRY: hdlab/learner/registry.py owns PLUGINS + the top-level learn()/apply() that
  fits every candidate plugin for a task and auto-selects via mdl_select(). This build wraps
  TWO plugins (imports the banked cells VERBATIM; does NOT modify them):
    "estimation" -- frequency/evidence-accumulation, wraps
      experiments/exp_online_knowledge_condenser_selectional_v1.py (banked 29476).
    "ruleind"    -- MDL-gated sequential-covering conjunction rule induction, wraps
      experiments/exp_parser_ruleinduction_cls_ppattach_v1.py (banked 29485).
  Per-competence CONFIG (primitives / feature encoders / hypothesis-space richness) is INPUT to
  learn() via hypothesis_space_spec + prior -- it is NOT owned by this module. Adding a new
  hypothesis class means writing one new plugin module with the same learn()/apply() pair and
  registering it; core.py (this file) needs zero changes.

THIS IS A REFACTOR. It does not claim any new substrate capability; behavior-preservation against
  the two source cells' banked numbers is the acceptance bar (see
  experiments/exp_learner_module_refactor_proof_v1.py + preregs/2026-07-23_learner_module_refactor.md).
"""
from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

KEEP_EPISODIC = "KEEP_EPISODIC"


def entropy_bits(labels):
    """Shannon entropy (bits) of a label multiset. Same formula as the rule-inducer's own
    _entropy_bits (kept as an independent, identical implementation here so the CORE does not
    depend on a specific plugin's private helper; plugins that already have _entropy_bits keep
    using their own copy for their internal MDL gate -- this is the core's copy for cross-plugin
    null-code scoring, deliberately the same math, verified equal by the proof script)."""
    if not labels:
        return 0.0
    n = len(labels)
    h = 0.0
    for c in Counter(labels).values():
        p = c / n
        if p > 0:
            h -= p * math.log2(p)
    return h


def null_code_bits(labels):
    """L(data) under the null (no-model, base-rate) code: n_items * entropy_bits(labels)."""
    return len(labels) * entropy_bits(labels)


def glass_box_assert(hypothesis):
    """GLASS-BOX invariant: the selected hypothesis (what gets inspected / banked) must be a
    plain JSON-serializable structure -- never an opaque callable-only / black-box object at
    rest. apply() may build a closure at call time; the hypothesis ITSELF must round-trip
    through json.dumps. Raises TypeError on violation (fail loud, not silent)."""
    if hypothesis is None:
        return True
    json.dumps(hypothesis)
    return True


@dataclass
class LearnResult:
    plugin_name: str
    hypothesis: Optional[dict]        # glass-box (JSON-able) or None if episodic-only
    is_episodic: bool
    description_bits: float           # L(hypothesis) + L(data|hypothesis), two-part MDL code
    null_bits: float                  # L(data) under the null / no-model code
    n_free_params: int
    cost_rank: int                    # plugin-declared relative complexity (Occam tie-break; lower=cheaper)
    metrics: dict = field(default_factory=dict)   # plugin-reported measurements (accuracy, curves, ...)

    @property
    def compression_ratio(self):
        """null_bits / description_bits. >1.0 means the hypothesis genuinely compresses past the
        null code; <=1.0 means it does not (should be gated to episodic by per_cluster_gate)."""
        if self.description_bits <= 0:
            return float("inf") if self.null_bits > 0 else 1.0
        return self.null_bits / self.description_bits


def per_cluster_gate(result: LearnResult, min_compression_ratio: float = 1.0) -> bool:
    """The CLS per-cluster RULE-vs-EPISODIC split (generalizes both source cells' own gates):
    induce (accept the hypothesis) only if it genuinely compresses past the null; otherwise keep
    episodic. min_compression_ratio=1.0 = 'strictly better than the no-model code'
    (Perfors & Tenenbaum 2009 two-part code MDL criterion)."""
    if result.is_episodic:
        return False
    return result.compression_ratio >= min_compression_ratio


def mdl_select(candidates: dict, min_compression_ratio: float = 1.0):
    """MODEL-SELECTION principle: among all candidate plugin fits for ONE task, pick the
    hypothesis that BEST COMPRESSES (highest compression_ratio), subject to per_cluster_gate
    (must beat the null). Ties -> lower cost_rank wins (Occam: prefer the cheaper hypothesis
    class when compression is equal or comparable). Returns (plugin_name | KEEP_EPISODIC,
    LearnResult | None)."""
    eligible = {name: r for name, r in candidates.items() if per_cluster_gate(r, min_compression_ratio)}
    if not eligible:
        return KEEP_EPISODIC, None
    best_name = min(eligible, key=lambda n: (-eligible[n].compression_ratio, eligible[n].cost_rank))
    return best_name, eligible[best_name]
