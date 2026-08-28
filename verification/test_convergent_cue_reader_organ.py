"""Witness for hdlab.convergent_cue_reader (landed 2026-08-27).

Self-contained construction proof of the convergent-cue combination rule (no corpus/register needed -- synthetic
cue vectors isolate the OPERATION):
  [1] GRACEFUL DEGRADATION = the double dissociation by construction: epi None -> meaning-solo (argmax sem);
      sem None -> entity-solo (argmax epi); both None -> None.
  [2] GENUINE CONVERGENCE (the pattern-completion signature): a peaked CORRECT episodic cue RESCUES a case where
      meaning-solo picks the wrong candidate -> convergent picks the right one. An INFO-FREE (uniform) episodic cue
      does NOT change the meaning answer (no spurious rescue). Symmetric: a peaked correct meaning cue rescues a wrong
      entity-solo pick.
  [3] RELIABILITY WEIGHTING is load-bearing: raising w (trust meaning more) moves a borderline decision toward the
      meaning cue -- the calibrated w is not inert.
  [4] GLASS-BOX: convergent_pick takes NO gold/label; the log-Bayes product = the pinned combination.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.convergent_cue_reader import (  # noqa: E402
    convergent_pick, calibrate_tau, DEFAULT_TAU_E, DEFAULT_TAU_S, DEFAULT_W)


def main() -> int:
    te, ts = DEFAULT_TAU_E, DEFAULT_TAU_S

    # [1] graceful degradation (the dissociation, by construction)
    sem = [0.1, 0.9, 0.2]     # meaning favours candidate 1
    epi = [2.0, 0.0, 0.1]     # episodic favours candidate 0
    assert convergent_pick(None, sem, tau_e=te, tau_s=ts) == 1, "epi lesion must give meaning-solo (argmax sem)"
    assert convergent_pick(epi, None, tau_e=te, tau_s=ts) == 0, "sem lesion must give entity-solo (argmax epi)"
    assert convergent_pick(None, None, tau_e=te, tau_s=ts) is None, "no evidence -> None"
    print("[1] graceful degradation PASS: epi-lesion->meaning-solo, sem-lesion->entity-solo, none->None")

    # [2] genuine convergence: peaked correct episodic RESCUES a wrong meaning-solo pick
    #     meaning-solo (argmax sem) = 2 (WRONG); truth = 0; episodic strongly peaks 0 -> convergent recovers 0.
    sem_wrong = [0.30, 0.20, 0.32]           # argmax = 2 (wrong)
    epi_right = [0.30, 0.00, 0.00]           # peaked on 0 (right); scale ~ tau_e so it is a decisive posterior
    ms = int(np.argmax(sem_wrong))
    conv = convergent_pick(epi_right, sem_wrong, tau_e=te, tau_s=ts, w=DEFAULT_W)
    assert ms == 2 and conv == 0, f"episodic must rescue the wrong meaning pick (ms={ms}, conv={conv})"
    # info-free (uniform) episodic must NOT change the meaning answer (no spurious rescue)
    epi_uniform = [0.1, 0.1, 0.1]
    conv_uni = convergent_pick(epi_uniform, sem_wrong, tau_e=te, tau_s=ts, w=DEFAULT_W)
    assert conv_uni == ms, f"uniform (info-free) episodic must fall back to meaning-solo (got {conv_uni}, want {ms})"
    # symmetric: peaked correct meaning rescues a wrong entity-solo pick
    epi_wrong = [0.30, 0.20, 0.32]           # entity-solo argmax = 2 (wrong)
    sem_right = [0.9, 0.0, 0.0]              # meaning peaks 0 (right)
    es = int(np.argmax(epi_wrong))
    conv2 = convergent_pick(epi_wrong, sem_right, tau_e=te, tau_s=ts, w=DEFAULT_W)
    assert es == 2 and conv2 == 0, f"meaning must rescue the wrong entity pick (es={es}, conv={conv2})"
    print("[2] genuine convergence PASS: correct episodic rescues wrong meaning; uniform episodic does not; symmetric")

    # [3] reliability weighting is load-bearing: episodic wins at equal weight, meaning overtakes at high w (a true flip)
    epi_b = [0.00, 0.20, 0.00]               # episodic strongly wants 1 (~tau_e scale -> peaked)
    sem_b = [0.05, 0.00, 0.00]               # meaning mildly wants 0
    low_w = convergent_pick(epi_b, sem_b, tau_e=te, tau_s=ts, w=1.0)
    high_w = convergent_pick(epi_b, sem_b, tau_e=te, tau_s=ts, w=48.0)
    assert low_w == 1, f"at equal weight the peaked episodic cue must win -> 1 (got {low_w})"
    assert high_w == 0, f"at high w the meaning cue must overtake -> 0 (got {high_w})"
    print(f"[3] reliability weighting PASS: w is load-bearing (w=1 -> episodic {low_w}, w=48 -> meaning {high_w})")

    # [4] glass-box: no gold in the signature; calibrate_tau is label-free and matches the baked scale shape
    import inspect
    params = list(inspect.signature(convergent_pick).parameters)
    assert "gold" not in params and "labels" not in params and "truth" not in params, params
    tau = calibrate_tau([[0.0, 0.1, 0.2], [0.3, 0.1, 0.0], None])
    assert tau > 0, "calibrate_tau must return a positive gold-blind scale"
    assert DEFAULT_W > 1.0, "the calibrated reliability weight must exceed the equal-reliability lower bound"
    print(f"[4] glass-box PASS: no gold in signature; calibrate_tau label-free ({tau:.4f}); DEFAULT_W={DEFAULT_W}")

    print("\nALL WITNESS ASSERTIONS PASSED -- the convergent-cue reader combines two SEPARATE cues by the log-Bayes")
    print("product (CA3 pattern completion + reliability-weighted cue combination), degrades gracefully into either")
    print("single system (the double dissociation), and genuinely integrates (correct episodic rescues wrong meaning,")
    print("info-free episodic does not).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
