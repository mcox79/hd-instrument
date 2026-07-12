"""Periodic fit-checkpoint + resume for the long KGE fit loops (course-C rotate/additive).

DURABILITY-ONLY. This module lets a long minibatch-SGD fit survive a timeout / kill / sleep: every
CKPT_EVERY epochs the fit state (entity phase/coord tensor, relation tensor, Adam optimizer state, the
per-epoch shuffle RNG state, the negative-sampling RNG state, and the next epoch to run) is written
atomically (tmp + os.replace) to the anchor output dir. On (re-)start the fit LOADS the checkpoint and
resumes from the saved epoch instead of restarting -- producing the SAME trajectory as an uninterrupted
run to within numerical tolerance (bit-identical on the pinned single-threaded CPU self-test).

CORRECTNESS-NEUTRAL: checkpointing only READS live state into detached CPU copies; it never mutates the
training tensors/optimizer/RNG, so an uninterrupted run trains bit-identically whether or not
checkpointing is enabled. Resume restores the exact RNG + params + optimizer moments, so the resumed
trajectory equals the uninterrupted one (verified by the 2-segment resume-equivalence self-test in
_course_c_rotate_core_v1.mechanism_selftest -- demonstrate resume, don't assert it; per the USER
2026-06-18 checkpoint/resume/kill-restart directive).

CONFIG-FINGERPRINT GUARD: a checkpoint is only reused when its fingerprint (fn, N, n_rel, k, epochs,
n_neg, lr, gamma, adv_temp, reg_lambda, batch_size, reciprocal, seed, split-hash, device) matches the
current fit. A checkpoint from a DIFFERENT config is ignored (fresh restart), never wrongly reused. A
corrupt/partial checkpoint (e.g. a kill mid-write, though os.replace makes that near-impossible) is also
ignored -> fresh restart.

RNG states are stored as numpy uint8 arrays (NOT torch tensors) so torch.load(map_location=device) never
tries to move a generator-state ByteTensor onto CUDA (which would break Generator.set_state).

ASCII-only. No bare except; except SystemExit/KeyboardInterrupt are never swallowed.
"""

import fnmatch
import hashlib
import json
import os
import time

import numpy as np
import torch


def fingerprint_hash(fp):
    """Stable short hash of a fingerprint dict."""
    return hashlib.sha256(json.dumps(fp, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def edges_hash(edges):
    """Stable short hash of an int edge array (the split fingerprint)."""
    a = np.ascontiguousarray(np.asarray(edges, dtype=np.int64))
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _gen_state_to_np(gen_state):
    """torch Generator state (uint8 ByteTensor) -> numpy uint8 array (map_location-safe storage)."""
    return gen_state.detach().to("cpu").numpy().astype(np.uint8).copy()


def _np_to_gen_state(arr):
    """numpy uint8 array -> CPU uint8 ByteTensor for Generator.set_state."""
    return torch.from_numpy(np.asarray(arr, dtype=np.uint8).copy())


class FitCheckpoint:
    """Per-arm fit checkpoint handle. One instance per (fit-arm, seed) so the concurrent arms in a single
    _fit_and_score (ONESHOT/ADDITIVE/SCRAMBLE/ORACLE) never collide on disk."""

    def __init__(self, ckpt_dir, tag, ckpt_every):
        self.dir = str(ckpt_dir)
        self.tag = str(tag)
        self.path = os.path.join(self.dir, "_fitckpt_%s.pt" % self.tag)
        self.tmp = self.path + ".tmp"
        self.prog_path = os.path.join(self.dir, "_fit_progress_%s.json" % self.tag)
        self.every = int(ckpt_every) if ckpt_every else 0
        self.fp = None
        self.fp_hash = None
        self.t0 = time.perf_counter()

    def enabled(self):
        return self.every > 0

    def set_fingerprint(self, fp):
        """Called by the fit fn once it has all params + the augmented split. Guards wrong reuse."""
        self.fp = dict(fp)
        self.fp_hash = fingerprint_hash(self.fp)

    def try_load(self, device):
        """Return the checkpoint payload iff enabled + present + fingerprint matches; else None."""
        if not self.enabled() or self.fp_hash is None or not os.path.exists(self.path):
            return None
        try:
            ck = torch.load(self.path, map_location=device)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return None  # corrupt/partial -> ignore, restart fresh (durability, not a correctness risk)
        if not isinstance(ck, dict) or ck.get("fp_hash") != self.fp_hash:
            return None  # different config -> do NOT wrongly reuse
        return ck

    def save(self, next_epoch, params, opt, gen_states):
        """Atomically persist fit state. params: {name: tensor}; gen_states: {name: torch ByteTensor}."""
        if not self.enabled() or self.fp_hash is None:
            return
        payload = dict(
            fp=self.fp, fp_hash=self.fp_hash, next_epoch=int(next_epoch),
            params={k: v.detach().to("cpu").clone() for k, v in params.items()},
            opt_state=opt.state_dict(),
            gens={k: _gen_state_to_np(v) for k, v in gen_states.items()},
        )
        os.makedirs(self.dir, exist_ok=True)
        torch.save(payload, self.tmp)
        os.replace(self.tmp, self.path)  # atomic; a kill mid-write cannot corrupt self.path

    def write_progress(self, next_epoch, epochs, last_loss):
        """Lightweight, always-atomic progress marker so a timeout leaves evidence of how far it got."""
        if not self.enabled():
            return
        marker = dict(tag=self.tag, next_epoch=int(next_epoch), epochs=int(epochs),
                      elapsed_s=round(time.perf_counter() - self.t0, 2),
                      last_loss=(float(last_loss) if last_loss == last_loss else None),
                      frac_done=round(float(next_epoch) / float(max(1, epochs)), 4))
        tmp = self.prog_path + ".tmp"
        os.makedirs(self.dir, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(marker, f)
        os.replace(tmp, self.prog_path)


def restore_into(ck, leaf_params, opt, gens, device):
    """Load a checkpoint payload into freshly-constructed leaf params + optimizer + generators.

    leaf_params: {name: requires_grad leaf tensor} (in-place copy_ from ck). gens: {name: torch.Generator}.
    Returns next_epoch (int)."""
    with torch.no_grad():
        for name, leaf in leaf_params.items():
            leaf.copy_(ck["params"][name].to(device))
    opt.load_state_dict(ck["opt_state"])
    for name, gen in gens.items():
        gen.set_state(_np_to_gen_state(ck["gens"][name]))
    return int(ck["next_epoch"])


def cleanup_seed_checkpoints(ckpt_dir, seed):
    """Remove all fit checkpoints + progress markers for a fully-completed seed (keeps a finished run's dir
    clean while an INTERRUPTED seed's checkpoints persist for resume). Best-effort; never raises."""
    d = str(ckpt_dir)
    if not os.path.isdir(d):
        return 0
    pats = ["_fitckpt_*_seed%d.pt" % seed, "_fitckpt_*_seed%d.pt.tmp" % seed,
            "_fit_progress_*_seed%d.json" % seed, "_fit_progress_*_seed%d.json.tmp" % seed]
    n = 0
    try:
        names = os.listdir(d)
    except OSError:
        return 0
    for name in names:
        if any(fnmatch.fnmatch(name, p) for p in pats):
            try:
                os.remove(os.path.join(d, name))
                n += 1
            except OSError:
                pass
    return n
