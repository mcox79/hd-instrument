"""verb_role_integrated.py -- the CONSTRUCTION-CONDITIONAL integration of the verb-role exemplar store with
position, promoted VERBATIM (2026-09-03) from experiments/exp_verbrole_exemplar_integrated_v1.make_integrated
(the dormant-organ activation of hdlab/verb_role_exemplar_selector).

BRAIN-PINNED (Competition Model, Bates & MacWhinney; noisy-channel, Levy 2008; eADM): role assignment is a
weighted combination of cues in log-odds, and the WORD-ORDER cue's weight COLLAPSES for non-canonical
constructions (passive / object-relative / fronted / archaic) where English comprehenders down-weight order
and let the SELECTIONAL (thematic-fit) cue win:
    score(c) = beta_pos(construction) * log_softmax(position) + log_softmax(exemplar_fit)
with beta_pos = 1.0 on canonical (active) clauses and beta_low (0.15) on non-canonical. GOLD-BLIND (canonicity
from the parse, not the label). MEASURED (exp_verbrole_exemplar_integrated_v1): INTEGRATED beats the live
reader's pick +0.0237 CI-sep on modern QA-SRL (verb-shuffled twin loses) and +0.2177 on 19c LitBank (there the
gain is the construction-conditional order-down-weighting; the modern store ties its twin on 19c). Glass-box, NO
LLM. Reuses hdlab.verb_role_exemplar_selector.fit_exemplar + the grounded space.
"""
from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

import numpy as np

_EPS = 1e-9


def _log_softmax(x, T):
    z = np.asarray(x, dtype=np.float64) / max(T, _EPS)
    z = z - z.max()
    return z - math.log(np.exp(z).sum() + _EPS)


def integrated_pick(verb_idx: int, cands: Sequence[Tuple[str, int, Optional[np.ndarray]]],
                    exemplars, canonical: bool, knn: int = 3, beta_low: float = 0.15,
                    temp_pos: float = 0.5, temp_sel: float = 0.3) -> Optional[str]:
    """cands = [(head, token_idx, grounded_vec_or_None)]; verb_idx = the predicate token index. Returns the
    picked head, or None if no grounded candidate / no exemplars (caller keeps its own pick). Verbatim to
    make_integrated: construction-conditional position (x) exemplar fit in log-odds."""
    from hdlab.verb_role_exemplar_selector import fit_exemplar
    cg = [(h, idx, g) for (h, idx, g) in cands if g is not None]
    if not cg or not exemplars:
        return None
    pos_raw = np.array([(10.0 - (idx - verb_idx)) if idx > verb_idx else 0.15 for _, idx, _ in cg],
                       dtype=np.float64)
    sel_raw = np.array([fit_exemplar(g, exemplars, knn) for _, _, g in cg], dtype=np.float64)
    b_pos = 1.0 if canonical else beta_low
    lp = b_pos * _log_softmax(pos_raw, temp_pos) + _log_softmax(sel_raw, temp_sel)
    return cg[int(np.argmax(lp))][0]
