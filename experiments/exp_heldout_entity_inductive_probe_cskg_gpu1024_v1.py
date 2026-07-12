"""GPU re-route of the DECISIVE held-out-ENTITY inductive probe (generalize-vs-memorize falsifier).

Identical recipe to exp_heldout_entity_inductive_probe_cskg_v1 EXCEPT it runs on the IDLE GPU instead of remote CPU,
for ~6x faster time-to-verdict. The CPU dispatch was re-fitting 3 seeds x multiple rotation/additive fits on CPU
(~1.5h/seed) and blew past its 4h ceiling. The held-out hits@10 PRIMARY metric is fpe_dim-INDEPENDENT (fpe_dim only
sizes the SECONDARY FPE readout bank, which the direct held-out score does not use), so a GPU run at fpe_dim=1024
yields the SAME verdict far faster -- same as the gpu1024 rotate seed wrappers (wall~3200s each).

Mechanical plumbing only (NOT an experiment redesign): sets HDLAB_DEVICE=cuda + HDLAB_FPE_DIM=1024 at import top,
imports the CPU cell module, redirects its module-level ANCHOR_NAME to an ISOLATED GPU anchor dir (so landing does
NOT collide with the CPU anchor), then calls its main() (default run_mode=full, device=auto -> resolves to cuda via
HDLAB_DEVICE). The cell already threads `device` cleanly through every fit/score (see _resolve_device + fit_and_score
in the base cell); no code path change required. top-level `import torch` routes this to overnight_queue (PROT-020).
ASCII-only."""

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

ANCHOR_NAME = "course_c_heldout_entity_inductive_probe_gpu1024_v1"
SEEDS = [7, 13, 17]
DEFAULT_RUN_MODE = "full"

if __name__ == "__main__":
    # Redirect all landing writes (metrics/start-marker/checkpoints/log prefix resolve the module global at runtime)
    # to the isolated GPU anchor dir; the CPU definitive anchor is left untouched.
    _heldout.ANCHOR_NAME = ANCHOR_NAME
    _heldout.main()
