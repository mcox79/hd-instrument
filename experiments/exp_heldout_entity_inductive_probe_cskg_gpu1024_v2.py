"""GPU re-route v2 of the DECISIVE held-out-ENTITY inductive probe -- FULL-FIDELITY re-fit to FIRE the oracle.

WHY v2 (RESOLVES the v1 INCONCLUSIVE). The v1 gpu1024 run landed INCONCLUSIVE_ORACLE_UNDERFIT: the two zero-
geometry arms (ONESHOT_ROTATE, ADDITIVE_TRANSE) both held-out hits@10 = 0.0000, BUT the ORACLE_TRANSDUCTIVE
positive control only reached 0.0123 (< the 0.10 ORACLE_FIRE_MARGIN), so oracle_fires=False and the zero arms are
UNINTERPRETABLE (cannot distinguish "memorizes, no entity transfer" from "the whole fit under-trained"). Root
cause: the base cell's FULL_CFG MODERATED epochs/n_neg (ep=200, n_neg=64) for the original CPU dispatch budget;
the full-scale fit under-trained even the oracle, whose gold tails ARE in its training set. The mechanism self-test
at tiny scale fired the oracle clean (0.307) so the machinery is correct; only the FULL fit fidelity was too low.

WHAT CHANGED (fit fidelity ONLY; everything else identical to v1). The base cell FULL_CFG is un-moderated to the
anchor-1 fidelity that FIRED the transductive oracle in the multi-seed gpu1024 rotate runs (k=24, ep=250, n_neg=128
-> those cleared their direct-oracle gate = MIDDLE_BAND not INCONCLUSIVE) and PUSHED to ep=500 (2x the gpu1024
epoch budget, the low end of the pre-cleared 2-3x escalation cap) so the held-out-entity oracle -- whose gold tails
are folded on only ~1 edge each, a harder fit than the l2 oracle -- gets its best single-shot chance to clear 0.10.
The held-out-entity split, the controls (RANDOM_CODES / CODEALIAS / BASELINE_POP), the arms (ONESHOT_ROTATE /
ADDITIVE_TRANSE), the ORACLE gate, and all bands are UNCHANGED. k stays 24 (the capacity-relevant knob, matched to
the completed run). More epochs cannot create a false generalize signal: a held-out tail has NO vector in the
ONESHOT/ADDITIVE arms (random-init by split construction), so those arms stay ~random at ANY epoch -- epochs only
sharpen the SEEN/oracle geometry, making the oracle-fire gate (and thus the verdict) INTERPRETABLE.

HARD GATE (unchanged from v1, enforced in the base cell's aggregate_and_verdict):
  - oracle_fires REQUIRED (ORACLE hits@10 - RANDOM hits@10 >= 0.10) for any generalize/memorize verdict.
  - oracle fires + arms ~0 vs random (margin < 0.02)  -> HARD_FAIL_MEMORIZED_NO_ENTITY_TRANSFER  (PROVEN MEMORIZE).
  - oracle fires + arms clear random by >= 0.05        -> HARD_PASS_INDUCTIVE_ENTITY_TRANSFER      (GENERALIZES).
  - oracle STILL < 0.10 at this full fidelity          -> INCONCLUSIVE_ORACLE_UNDERFIT (the base cell verdict) ==
    the escalation branch: the per-entity KGE fit itself cannot support held-out-entity inference at this scale
    (directional evidence toward the factorized map-builder, per the scaling drill). Cap held at 500 epochs (2x);
    750 (3x) is the remaining headroom before declaring a hard ceiling.

MECHANICAL PLUMBING ONLY (NOT an experiment redesign): sets HDLAB_DEVICE=cuda + HDLAB_FPE_DIM=1024 at import top,
imports the CPU cell module, redirects its module-level ANCHOR_NAME to an ISOLATED v2 GPU anchor dir (so landing
does NOT collide with the v1 anchor), then calls its main() (default run_mode=full, device=auto -> cuda via
HDLAB_DEVICE). The cell threads `device` cleanly through every fit/score; no code path change. The held-out PRIMARY
metric is fpe_dim-INDEPENDENT (fpe_dim only sizes the SECONDARY FPE bank the direct held-out score never uses), so
fpe_dim=1024 fits the card and yields the SAME verdict. top-level `import torch` routes to overnight_queue (PROT-020).
Multi-seed [7,13,17] in-process, each fit outage-resumable via FitCheckpoint (fingerprint keys on epochs+n_neg ->
never stale-resumes the v1 ep=200 checkpoints). ASCII-only."""

import os
import sys

import torch  # noqa: F401  top-level GPU-device visibility -> routes to overnight_queue (PROT-020)

os.environ.setdefault("HDLAB_DEVICE", "cuda")   # force GPU device in _resolve_device; respects an explicit override
os.environ.setdefault("HDLAB_FPE_DIM", "1024")  # secondary-readout bank size only; held-out PRIMARY metric unaffected

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_heldout_entity_inductive_probe_cskg_v1 as _heldout  # noqa: E402

ANCHOR_NAME = "course_c_heldout_entity_inductive_probe_gpu1024_v2"
SEEDS = [7, 13, 17]
DEFAULT_RUN_MODE = "full"

if __name__ == "__main__":
    # Redirect all landing writes (metrics/start-marker/checkpoints/log prefix resolve the module global at runtime)
    # to the isolated v2 GPU anchor dir; the v1 INCONCLUSIVE anchor is left untouched for provenance.
    _heldout.ANCHOR_NAME = ANCHOR_NAME
    _heldout.main()
