"""PLUGIN 2: RULE-INDUCTION hypothesis class (MDL-gated sequential-covering conjunctions). Wraps
experiments/exp_parser_ruleinduction_cls_ppattach_v1.py (banked 29485) -- imports induce_rules() /
build_residual_lookup() VERBATIM; DOES NOT MODIFY that file. NONLINEAR: carves axis-aligned
feature-value-conjunction regions a linear map or a similarity vote cannot represent. More
expensive than PLUGIN 1 (conjunction search over candidate feature pairs) -- Occam-penalized on
compression ties via COST_RANK.
"""
from __future__ import annotations

import math

from experiments import exp_parser_ruleinduction_cls_ppattach_v1 as RULEIND
from hdlab.learner.core import LearnResult, glass_box_assert, null_code_bits

NAME = "ruleind"
COST_RANK = 3   # more expensive: O(n_singles^2) conjunction search per covering iteration

_INDUCE_KWARGS = ("max_conjunct", "min_coverage", "purity_thresh", "max_rules",
                  "exclude_prefixes", "max_singles_for_pairing", "mdl_margin_bits")


def learn(episodes, features, hypothesis_space_spec, prior):
    """episodes: list of instance dicts with a 'gold_class' field (RULEIND.induce_rules' native
    pool format). features: feat_fn(inst) -> iterable[str] (per-competence feature encoder --
    e.g. RULEIND.control_feat_fn or the real task's BASE.instance_feats). hypothesis_space_spec
    may carry induce_rules kwargs (max_conjunct, min_coverage, purity_thresh, max_rules,
    exclude_prefixes, ...) plus 'key_fn' for the episodic-residual fallback key."""
    induce_kwargs = {k: v for k, v in hypothesis_space_spec.items() if k in _INDUCE_KWARGS}
    key_fn = hypothesis_space_spec.get("key_fn", RULEIND.control_key_fn)
    rules, residual_idx = RULEIND.induce_rules(episodes, features, **induce_kwargs)
    residual_lookup = RULEIND.build_residual_lookup(episodes, residual_idx, key_fn)
    labels_all = [a["gold_class"] for a in episodes]
    n_classes = max(len(set(labels_all)), 2)

    model_bits = sum(r["bits_rule"] for r in rules)
    data_bits_rules = sum(r["bits_exceptions"] for r in rules)
    data_bits_residual = len(residual_idx) * math.log2(n_classes)
    hyp = {"kind": "rules_residual", "rules": rules,
           "residual_lookup": {str(k): v for k, v in residual_lookup.items()}, "n_classes": n_classes}
    glass_box_assert(hyp)
    return LearnResult(plugin_name=NAME, hypothesis=hyp,
                        is_episodic=bool(len(rules) == 0),
                        description_bits=model_bits + data_bits_rules + data_bits_residual,
                        null_bits=null_code_bits(labels_all),
                        n_free_params=sum(len(r["conjunct"]) + 1 for r in rules),
                        cost_rank=COST_RANK,
                        metrics={"n_rules": len(rules), "n_episodic": len(residual_idx),
                                 "model_bits": round(model_bits, 3),
                                 "data_bits_rules": round(data_bits_rules, 3),
                                 "data_bits_residual": round(data_bits_residual, 3)})


def apply(hypothesis, feats, key=None, default_class=None):
    """feats: iterable of feature-value strings for the new item (from the SAME feat_fn used at
    learn() time). key: optional discrete key for the episodic-residual fallback lookup. Mirrors
    RULEIND.ruleind_predict_factory's decision-list logic exactly (rules checked in order, then
    residual episodic lookup, then default_class)."""
    if hypothesis["kind"] != "rules_residual":
        raise ValueError(f"ruleind plugin cannot apply a {hypothesis['kind']!r} hypothesis")
    fs = set(feats)
    for r in hypothesis["rules"]:
        if set(r["conjunct"]).issubset(fs):
            return r["majority_class"]
    if key is not None:
        v = hypothesis["residual_lookup"].get(str(key))
        if v is not None:
            return v
    return default_class


def apply_with_margin(hypothesis, feats, key, default_class, pred_class):
    """Adapter matching BASE.eval_heldout's predict_fn(a) -> (label, margin) calling convention
    (used by the real-task reproduction test). margin=1.0 when a rule or the residual lookup
    fires (always override); margin=-1.0 when falling back to the parser's own pred_class (never
    override) -- exactly RULEIND.ruleind_predict_factory's own margin semantics."""
    fs = set(feats)
    for r in hypothesis["rules"]:
        if set(r["conjunct"]).issubset(fs):
            return r["majority_class"], 1.0
    v = hypothesis["residual_lookup"].get(str(key))
    if v is not None:
        return v, 1.0
    return pred_class if pred_class is not None else default_class, -1.0
