"""Plugin registry: hypothesis-class plugins pluggable into the centralized Learner core (see
hdlab/learner/core.py for the shared MDL model-selection engine). Adding a new hypothesis class
(GAM/EBM, ILP, program induction, ...) = write one module implementing learn()/apply() and
register it here. hdlab/learner/core.py never needs to change."""
from __future__ import annotations

from hdlab.learner.core import mdl_select
from hdlab.learner.plugins import estimation_plugin, gam_plugin, ruleind_plugin

PLUGINS = {
    estimation_plugin.NAME: estimation_plugin,
    ruleind_plugin.NAME: ruleind_plugin,
    gam_plugin.NAME: gam_plugin,
}


def learn(episodes, features, hypothesis_space_spec, prior=None):
    """Centralized learn(): fits every candidate plugin (or the subset named in
    hypothesis_space_spec['candidate_plugins']), scores each under the shared MDL code, and
    returns (chosen_plugin_name | KEEP_EPISODIC, chosen_LearnResult | None, all_results dict).
    This automates the by-hand 'which learner' decision: the caller supplies a task (episodes +
    feature encoder + hypothesis-space config) and gets back the auto-selected glass-box
    hypothesis, without having to know in advance which hypothesis class fits best."""
    prior = prior or {}
    candidate_names = hypothesis_space_spec.get("candidate_plugins", list(PLUGINS.keys()))
    per_plugin_spec = hypothesis_space_spec.get("per_plugin", {})
    min_ratio = hypothesis_space_spec.get("min_compression_ratio", 1.0)
    results = {}
    for name in candidate_names:
        plugin = PLUGINS[name]
        spec = per_plugin_spec.get(name, hypothesis_space_spec)
        results[name] = plugin.learn(episodes, features, spec, prior.get(name, {}))
    chosen_name, chosen = mdl_select(results, min_ratio)
    return chosen_name, chosen, results


def apply(plugin_name, hypothesis, *args, **kwargs):
    return PLUGINS[plugin_name].apply(hypothesis, *args, **kwargs)
