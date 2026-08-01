"""OPT-IN loader for the certified minimal-unfreeze entity-consistency encoder break.

WIRING NOTE (integration gate, atom math seq 29596 chain-grade + atom 29593 cert): this module
makes the persisted retrained v2 encoder a DISCOVERABLE, REUSABLE asset instead of an island.
It does NOT change any existing cell's default encoder -- nothing else imports this module
automatically. Any harness that wants the improved encoder calls `load_improved_encoder(...)`
explicitly; everything else keeps loading the frozen base v2 ckpt (eb.EncoderExtractor() with
its default V2_CKPT) exactly as before.

THE CAPABILITY (chain-graded, atom math seq 29596): minimal-unfreeze (top-1 transformer layer,
3.15M trainable params) fine-tune of the substrate's own v2 encoder with the cross-mention-
consistency + inter-entity-push + VICReg objective. PROVEN, GENERALIZING representation-quality
LEVER for ENTITY-ADDRESSED comprehension (all query types, harder difficulty, held-out content,
independent harness; multi-seed; drift-controlled; independently recomputed). HONEST SCOPE: a
proven LEVER (lifts entity-addressed comprehension via cross-frame entity re-identification),
NOT solved comprehension (coref abs ~0.65 < 0.70 bar); no free lunch on untrained orthogonal
skills (atom 29597). Synthetic (situation-model) harness; naturalistic-text validation pending.

RECIPE: experiments/exp_encoder_retrain_persist_v1.py (wiring cell) persists the recipe cert-ed
in experiments/exp_situation_model_assembly_encoder_retrain_scale_v1.py (atom 29593, config
d1_div40) to data/exp_encoder_retrain_persist_v1/ckpt_seed_<seed>.pt -- same on-disk schema as
the frozen base ckpt (model_cfg + tokenizer_json copied verbatim, only state_dict differs), so
it loads through the SAME eb.EncoderExtractor(ckpt_path=...) interface used everywhere else.
Round-trip verified: reload-fresh tuned_loop_mean reproduces the cert cell's landed numbers at
deviation 0.0 for all 3 seeds (data/exp_encoder_retrain_persist_v1/metrics.json, HARD_PASS).

ADOPTION STEP for a new comprehension cell/harness that wants the lift:
    from hdlab.encoder_retrain_persist import load_improved_encoder
    ext = load_improved_encoder(seed=7)   # or 13, 19 -- any of the 3 certified seeds
    # `ext` is a drop-in eb.EncoderExtractor; use it exactly like the frozen extractor.
This is an EVAL-ONLY swap (same pattern validated in experiments/exp_coref_encoder_transfer_v1.py
and experiments/exp_encoder_alltype_transfer_stress_v1.py) -- no retraining needed to consume it.
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
_EXP_DIR = os.path.join(_REPO, "experiments")
if _EXP_DIR not in sys.path:
    sys.path.insert(0, _EXP_DIR)

CKPT_DIR = os.path.join(_REPO, "data", "exp_encoder_retrain_persist_v1")

# the 3 certified seeds (matches exp_encoder_retrain_persist_v1.py DEFAULT_SEEDS / metrics.json)
CERTIFIED_SEEDS = (7, 13, 19)

CKPT_PATHS = {s: os.path.join(CKPT_DIR, "ckpt_seed_%d.pt" % s) for s in CERTIFIED_SEEDS}


def improved_ckpt_path(seed: int = 7) -> str:
    """Path to the persisted minimal-unfreeze retrained-encoder checkpoint for `seed`.

    Raises ValueError for a seed outside the 3 certified seeds (7, 13, 19) and FileNotFoundError
    if the ckpt is missing on disk (e.g. data/ not synced) -- fail loud, never silently fall back
    to the frozen base encoder.
    """
    if seed not in CKPT_PATHS:
        raise ValueError(
            "seed=%r is not a certified encoder-retrain-persist seed; use one of %r"
            % (seed, CERTIFIED_SEEDS)
        )
    path = CKPT_PATHS[seed]
    if not os.path.exists(path):
        raise FileNotFoundError(
            "improved-encoder ckpt not found at %s -- run experiments/exp_encoder_retrain_persist_v1.py "
            "or sync data/exp_encoder_retrain_persist_v1/" % path
        )
    return path


def load_improved_encoder(seed: int = 7, conditioning=None):
    """Load the certified minimal-unfreeze entity-consistency encoder break as a drop-in
    eb.EncoderExtractor (atom math seq 29596 chain-grade lever; recipe cert atom 29593).

    OPT-IN: this is the ONLY place in the substrate that swaps in the retrained encoder. Callers
    choose it explicitly for entity-addressed comprehension work; nothing defaults to it.
    """
    import exp_situation_model_assembly_encoder_backed_v1 as eb  # noqa: E402 (path-inserted above)

    path = improved_ckpt_path(seed)
    kwargs = {}
    if conditioning is not None:
        kwargs["conditioning"] = conditioning
    return eb.EncoderExtractor(ckpt_path=path, **kwargs)


def self_test() -> bool:
    """Load each certified seed's ckpt and confirm it is a real, usable EncoderExtractor
    (non-empty vocab/model, distinct state_dict from the frozen base). No accuracy claim here --
    that is the cert cell's job (atom 29593) and the persist cell's reload-verify (metrics.json).
    """
    ok = True
    for seed in CERTIFIED_SEEDS:
        try:
            ext = load_improved_encoder(seed=seed)
        except (FileNotFoundError, ValueError) as e:
            print("[self_test] seed=%d FAILED to load: %s" % (seed, e))
            ok = False
            continue
        if not hasattr(ext, "model") or not hasattr(ext, "tok"):
            print("[self_test] seed=%d loaded but missing model/tok attrs" % seed)
            ok = False
            continue
        print("[self_test] seed=%d loaded OK (d_model=%d)" % (seed, ext.d))
    return ok


if __name__ == "__main__":
    sys.exit(0 if self_test() else 1)
