"""PLUGIN 1: FREQUENCY-ESTIMATION hypothesis class. Wraps
experiments/exp_online_knowledge_condenser_selectional_v1.py (banked 29476) -- imports its
condensation primitives VERBATIM (build_condensed_counts / condensed_score / make_score_fn);
DOES NOT MODIFY that file. Extracted core: Laplace-smoothed evidence-accumulation over a SINGLE
granularity KEY (no feature conjunctions) -- the hypothesis-space CLASS is order-1 / non-
conjunctive counting, which is exactly the structural property that distinguishes it from PLUGIN 2
(ruleind's conjunction search). Cheap: O(1) dict lookup per item, no search -- Occam-preferred
whenever it compresses comparably to a more expensive plugin.

Two modes, selected via hypothesis_space_spec['mode']:
  'condenser_reproduce' (behavior-preservation test only) -- LITERAL passthrough to the
    condenser's own functions: build_condensed_counts()/condensed_score() via make_score_fn(),
    on the condenser's own (verb,class)/(verb,noun) keys and its FIXED seed table. Bit-identical
    to calling the banked cell's own functions directly with the same inputs.
  'generic_mdl' (default; the AUTO-SELECT path) -- the SAME evidence-accumulation math
    GENERALIZED to an arbitrary single key_fn/label_fn supplied by the caller's per-competence
    CONFIG (the module core does not own the feature encoder), scored under a proper two-part MDL
    code (model bits + cross-entropy data bits) so it is comparable, via the shared
    hdlab.learner.core.mdl_select(), to PLUGIN 2's fit on the SAME task -- including tasks the
    condenser cell itself never ran on (e.g. PP-attachment).
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

from experiments import exp_online_knowledge_condenser_selectional_v1 as CONDENSER
from hdlab.learner.core import LearnResult, glass_box_assert, null_code_bits

NAME = "estimation"
COST_RANK = 1     # cheap: O(1) dict counting, no search -- Occam-preferred on compression ties


def learn(episodes, features, hypothesis_space_spec, prior):
    mode = hypothesis_space_spec.get("mode", "generic_mdl")
    if mode == "condenser_reproduce":
        return _learn_condenser_reproduce(episodes, hypothesis_space_spec, prior)
    return _learn_generic_mdl(episodes, features, hypothesis_space_spec, prior)


def _learn_condenser_reproduce(episodes, spec, prior):
    """episodes = the condenser's own stream slice (list of (sid,v,n,ss) tuples).
    spec['granularity'] in {'class','pair'} -- literal reuse of
    CONDENSER.build_condensed_counts(episodes, granularity)."""
    granularity = spec.get("granularity", "class")
    seed_table = prior.get("seed_table", {})
    counts = CONDENSER.build_condensed_counts(episodes, granularity)
    hyp = {"kind": "condenser_counts", "granularity": granularity,
           "counts": {"|".join(map(str, k)): v for k, v in counts.items()}}
    glass_box_assert(hyp)
    n_keys = len(counts)
    # Informal complexity currency for this reproduce-only path (not fed to cross-plugin
    # mdl_select; the reproduction test calls this plugin directly, not via auto-select).
    return LearnResult(plugin_name=NAME, hypothesis=hyp, is_episodic=(n_keys == 0),
                        description_bits=float(max(n_keys, 1)), null_bits=float(max(n_keys, 1)),
                        n_free_params=n_keys, cost_rank=COST_RANK,
                        metrics={"granularity": granularity, "n_keys": n_keys,
                                 "n_seed_entries": len(seed_table)})


def score_condenser_reproduce(hypothesis, seed_table, v, n, ss):
    """Rebuild the condenser's own score_fn bound to THIS hypothesis's counts + the fixed seed
    table (never touched by 'reading'), and score one (verb,noun,supersense) item. Delegates to
    CONDENSER.make_score_fn -- bit-identical to the banked cell's own scoring."""
    counts = {}
    for k, v_ in hypothesis["counts"].items():
        parts = k.split("|", 1)
        counts[(parts[0], parts[1])] = v_
    score_fn = CONDENSER.make_score_fn(counts, hypothesis["granularity"], seed_table)
    return score_fn(v, n, ss)


def _learn_generic_mdl(episodes, features, spec, prior):
    """Generalized single-key Laplace-smoothed multiclass evidence accumulation -- the SAME
    (n+1)/(n+K) shape as CONDENSER.condensed_score, generalized from K=2 (plausible/not) to K
    classes. key_fn/label_fn are PER-COMPETENCE CONFIG (input, not owned by the core): the module
    supplies only the counting + MDL-scoring MACHINERY, not the feature encoder."""
    key_fn = spec["key_fn"]
    label_fn = spec.get("label_fn", lambda ep: ep[-1])
    classes = spec.get("classes")
    counts = defaultdict(Counter)
    labels_all = []
    for ep in episodes:
        k = key_fn(ep)
        lbl = label_fn(ep)
        counts[k][lbl] += 1
        labels_all.append(lbl)
    if classes is None:
        classes = sorted(set(labels_all))
    n_classes = max(len(classes), 2)

    def p_model(k, lbl):
        c = counts.get(k, {})
        total = sum(c.values())
        return (c.get(lbl, 0) + 1) / (total + n_classes)   # Laplace smoothing (condensed_score generalized)

    data_bits = 0.0
    for ep in episodes:
        k, lbl = key_fn(ep), label_fn(ep)
        p = max(p_model(k, lbl), 1e-12)
        data_bits += -math.log2(p)
    n_keys = len(counts)
    model_bits = n_keys * math.log2(n_classes)   # one Laplace-table entry cost per observed key
    hyp = {"kind": "evidence_counts", "counts": {str(k): dict(c) for k, c in counts.items()},
           "classes": list(classes), "n_classes": n_classes}
    glass_box_assert(hyp)
    return LearnResult(plugin_name=NAME, hypothesis=hyp, is_episodic=(n_keys == 0),
                        description_bits=model_bits + data_bits,
                        null_bits=null_code_bits(labels_all),
                        n_free_params=n_keys, cost_rank=COST_RANK,
                        metrics={"n_keys": n_keys, "n_classes": n_classes,
                                 "model_bits": round(model_bits, 3), "data_bits": round(data_bits, 3)})


def apply(hypothesis, key):
    """key must be produced by the SAME key_fn used at learn() time (a raw key -- string or
    tuple); looks it up (by str(key)) against the fitted per-key label-count table and returns
    the argmax label. Only valid for 'generic_mdl' hypotheses -- 'condenser_counts' hypotheses
    use score_condenser_reproduce() instead (they score a 2AFC pair, not a single-label argmax)."""
    if hypothesis["kind"] == "condenser_counts":
        raise ValueError("condenser_counts hypotheses use score_condenser_reproduce(), not apply()")
    c = hypothesis["counts"].get(str(key))
    if not c:
        return hypothesis["classes"][0] if hypothesis.get("classes") else None
    return max(c, key=c.get)
