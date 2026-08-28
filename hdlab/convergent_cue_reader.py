"""Convergent-cue composition reader -- the brain's RETRIEVAL rule for combining two cues, not a post-hoc AND.

Landed 2026-08-27 from the integrated `compose_the_reader_by_convergent_cue_not_independent_conjunction`
(SOLVED/EXCELLENT, owner-DONE; witness `test_convergent_cue_composed_reader.py` 7/7 PASS, re-verified first-hand).

THE PROBLEM IT REPLACES. To answer "what did X pursue?" when the story said "X chased Y", a reader must combine an
EPISODIC cue (which character X is -> the per-entity register's verb readback) with a MEANING cue (pursue==chase ->
the ATL conceptual channel). The prior composition (STEP 18) ran the two retrievals INDEPENDENTLY and required both to
be right -- a post-hoc AND whose score was ~= the product of the two solo rates (statistical INDEPENDENCE), LOWER than
either system alone. That is not how the brain retrieves.

WHAT IS PINNED (copy the operation):
  * Episodic recall is CONVERGENT-CUE pattern completion (CA3 attractor; Norman & O'Reilly 2003): multiple partial cues
    JOINTLY drive ONE content-addressable read.
  * Optimal combination of two evidence distributions is their PRODUCT = the SUM of their log-posteriors (Bayes). In a
    probabilistic population code this is literally ADDING the two codes, and the more reliable (more peaked) cue
    dominates by its own gain -- reliability-weighting is automatic per query (Ma, Beck, Latham & Pouget 2006;
    Ernst & Banks 2002 is the normative precision-weighting result; Hemmer & Steyvers 2009 = episodic trace x semantic
    prior, the closest whole-operation precedent).
  * SEPARATE POOLS, combined at read -- NEVER fused. Keeping the episodic and semantic stores distinct is EVIDENCE-PINNED
    by the canonical DOUBLE DISSOCIATION (semantic dementia spares episodic binding; hippocampal amnesia spares
    semantics). Fusing them into one undifferentiated pool LOSES and destroys the dissociation (validated: fused 0.360
    loses to convergent 0.744, and its lesion read 0.134 < separated entity-solo 0.178).

WHAT IS OUR-INVENTION-UNDER-TEST (honestly labelled): the reliability weight `w` is CALIBRATED offline (a static asset),
NOT emergent -- because our two cue codes are NOT one shared PPC population, so the automatic-gain story does not give the
cross-cue ratio for free. `w` is a single scalar fit by cross-validation on a train split (Ernst-Banks calibration) and
evaluated strictly held-out.

THE OPERATION (`convergent_pick`):
    answer = argmax_c [ log softmax(epi_raw/tau_e)(c) + w * log softmax(sem_raw/tau_s)(c) ]
  epi_raw = per-candidate FHRR register cleanup scores (BOTTOM-UP, from situation_model_accumulate.decode);
  sem_raw = per-candidate conceptual_meaning.similarity(cue, candidate) (TOP-DOWN, ATL);
  tau_e/tau_s = each cue's OWN gold-blind global scale (the population's fixed gain); w = the calibrated reliability ratio.
  GRACEFUL DEGRADATION (the dissociation, by construction): epi_raw None -> meaning-solo (hippocampal lesion);
  sem_raw None -> entity-solo (semantic lesion).

VALIDATED (held-out n=3681, LitBank paraphrased pronoun who-did-what): convergent 0.7438 beats the STRONGEST floor
meaning-solo 0.6998 (+0.044 CI-sep [0.030,0.058]); shuffled-MEANING twin collapses (0.041); shuffled-EPISODIC twin falls
BELOW meaning-solo (the win needs REAL episodic evidence = genuine convergence, not meaning relabeled); FUSED one-pool
loses (+0.384); double dissociation preserved; the lift is LOCALISED (rescues 20.5% of meaning-solo-WRONG, keeps 97.6% of
meaning-solo-RIGHT); equal-weight product (w=1) falls below meaning-solo -> reliability weighting is load-bearing. The
RULE is AT CEILING (0.744 vs argmax-union oracle 0.750, NOT_SEP); the residual headroom is the DENSE episodic store, and
the gain rises monotonically with episodic reliability -> predicted to COMPOUND with the sparse DG+CA3 store (p2).

DEFAULT-SAFE: new module, nothing imports it (ISLAND). The DEFAULT_* constants are the DENSE-store LitBank calibration;
recalibrate `w` (and the taus) on p2's sparse store when it lands (predicted w -> 1, larger gain). NO learning/LLM at
inference; the taus/w are offline static assets (admissible per the build-ideal-foundation pivot).
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

# ---- static offline-calibrated assets (DENSE-store LitBank calibration 2026-08-27; recalibrate on the sparse store) ----
DEFAULT_TAU_E = 0.056714747111021084   # episodic cue gold-blind global scale (std of raw register cleanup scores)
DEFAULT_TAU_S = 0.35560472209499694    # semantic cue gold-blind global scale (std of raw conceptual similarities)
DEFAULT_W = 12.0                       # calibrated reliability ratio (median held-out; Ernst-Banks). w=1 == equal-reliability.


def _softmax(x: Sequence[float]) -> np.ndarray:
    x = np.asarray(x, float)
    x = x - x.max()
    e = np.exp(x)
    return e / e.sum()


def calibrate_tau(raw_scores: Sequence[Sequence[float]]) -> float:
    """The gold-blind global scale of a cue = std of its raw scores over ALL queries (the population's fixed gain).
    One constant per cue -> per-query peakedness (reliability) is preserved and does the weighting. Offline / label-free."""
    vals = []
    for row in raw_scores:
        if row is not None:
            vals.extend(float(x) for x in row)
    v = np.asarray(vals, float)
    return float(v.std()) if v.size and v.std() > 1e-12 else 1.0


def convergent_pick(epi_raw: Optional[Sequence[float]], sem_raw: Optional[Sequence[float]], *,
                    tau_e: float = DEFAULT_TAU_E, tau_s: float = DEFAULT_TAU_S, w: float = DEFAULT_W) -> Optional[int]:
    """Convergent-cue read over candidates aligned by index: return argmax_c [log p_epi(c) + w*log p_sem(c)].

    epi_raw / sem_raw are per-candidate raw cue scores in the SAME candidate order.
      * sem_raw None AND epi_raw None -> None (no evidence).
      * epi_raw None (hippocampal lesion) -> meaning-solo = argmax(sem_raw).
      * sem_raw None (semantic lesion)   -> entity-solo  = argmax(epi_raw).
    Two SEPARATE pools combined at read; never fused. Glass-box: takes NO gold/label."""
    if sem_raw is None and epi_raw is None:
        return None
    if sem_raw is None:                                   # semantic lesion -> entity-solo (graceful)
        return int(np.argmax(np.asarray(epi_raw, float)))
    p_sem = _softmax(np.asarray(sem_raw, float) / tau_s)
    if epi_raw is None:                                   # hippocampal lesion -> meaning-solo (graceful)
        return int(np.argmax(p_sem))
    p_epi = _softmax(np.asarray(epi_raw, float) / tau_e)
    return int(np.argmax(np.log(p_epi + 1e-12) + w * np.log(p_sem + 1e-12)))
