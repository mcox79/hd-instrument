"""Plugin registry: hypothesis-class plugins pluggable into the centralized Learner core (see
hdlab/learner/core.py for the shared MDL model-selection engine). Adding a new hypothesis class
(GAM/EBM, ILP, program induction, ...) = write one module implementing learn()/apply() and
register it here. hdlab/learner/core.py never needs to change."""
from __future__ import annotations

import importlib
from collections.abc import Mapping

from hdlab.learner.core import mdl_select

# LAZY PLUGIN IMPORTS (2026-08-22). MEASURED CAUSE: importing this module eagerly imported four
# plugins, two of which import EXPERIMENT CELLS, which pulled 8 cells into sys.modules and -- because
# a cell legitimately configures itself as a script at module level -- SILENTLY REWROTE sys.stdout's
# encoding (cp1252 -> utf-8) and set OMP_NUM_THREADS=1 for the whole process, on any `import
# hdlab.reading_grounding_loop`. Measured: hdlab.learner alone pulls all 8; reading_grounding_loop
# adds zero beyond it, so THIS FILE IS THE SOLE GATEWAY on the live path.
#
# The names are declared STATICALLY so `list(PLUGINS.keys())` -- the default candidate list in
# learn() -- still works without importing anything. verification/test_learner_registry_is_lazy.py
# asserts each module's own NAME still equals its declared key, so the duplication cannot rot.
#
# ORDER IS LOAD-BEARING: it is the default candidate order in learn(), preserved exactly from the
# eager dict (estimation, ruleind, gam, proginduction).
_PLUGIN_MODULES = {
    "estimation": "hdlab.learner.plugins.estimation_plugin",
    "ruleind": "hdlab.learner.plugins.ruleind_plugin",
    "gam": "hdlab.learner.plugins.gam_plugin",
    "proginduction": "hdlab.learner.plugins.proginduction_plugin",
}


class _LazyPlugins(Mapping):
    """Maps plugin name -> module, importing each module only when it is first indexed.

    A plain dict cannot do this: building it requires importing every plugin to read its NAME."""

    def __init__(self, modules):
        self._modules = dict(modules)
        self._loaded = {}

    def __getitem__(self, name):
        mod = self._loaded.get(name)
        if mod is None:
            mod = self._loaded[name] = importlib.import_module(self._modules[name])
        return mod

    def __iter__(self):
        return iter(self._modules)

    def __len__(self):
        return len(self._modules)


PLUGINS = _LazyPlugins(_PLUGIN_MODULES)


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
