"""Substrate-curriculum-learning module.

Curriculum policies for ordering training examples during small-LM training:

- RandomPolicy:               uniform-random batch sampling (baseline)
- DifficultyGradedPolicy:     order by ascending example length (simpler == shorter)
- LossBasedActivePolicy:      after warm-up, weight examples by current model loss
- SubstrateCurriculumPolicy:  argmin |cos(W @ encode(x), encode(x))| over candidate pool
                              (least-redundant-given-what-substrate-already-knows)

All 4 policies share the CurriculumPolicy interface defined in policies.py.
The generic training loop lives in training_loop.py.

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations
