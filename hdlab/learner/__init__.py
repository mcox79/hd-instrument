"""Centralized Learner module: ONE model-selection engine with pluggable per-competence
hypothesis-class primitives. See hdlab/learner/core.py for the shared engine and
hdlab/learner/registry.py for the plugin registry + top-level learn()/apply()."""
from hdlab.learner.core import KEEP_EPISODIC, LearnResult  # noqa: F401
from hdlab.learner.registry import PLUGINS, apply, learn  # noqa: F401

__all__ = ["KEEP_EPISODIC", "LearnResult", "PLUGINS", "apply", "learn"]
