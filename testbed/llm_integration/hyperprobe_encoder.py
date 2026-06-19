"""Hyperprobe encoder interface for Phase 0.5 + Phase 0.5b LLM-coupled audit primitives.

The encoder maps LLM residual streams r in R^d (Llama-3.1-8B hidden d=4096) to
substrate-native bipolar codewords xi in {-1, +1}^D (D=4096 published, or N=32768
if probe is retrained).

Per arXiv:2509.25045 (Sep 2025) Ipazia-AI/hyperprobe — MAP-B native algebra.

Three modes:
    - 'synthetic'    : smoke mode; emits iid {-1,+1}^D Rademacher bipolar codes
                       (no LLM dependency). For substrate-side logic validation.
    - 'pseudo_llm'   : light mode; emits anisotropic codes drawn from a
                       fixed low-rank cone projection (mimics LLM hidden-state
                       anisotropy per Ethayarajh / I-10 kappa_3-mixing drill).
                       For testing whitening rescue without Llama+Hyperprobe.
    - 'hyperprobe'   : full mode; loads Llama-3.1-8B via vLLM + Hyperprobe
                       checkpoint, performs forward pass, intercepts residual at
                       layer ell = L * 0.6..0.8 final-token, runs hyperprobe to
                       emit bipolar code. Requires external deps + Lambda GPU.

The substrate-side audit primitives (kappa_3, deletion cert, refusal cert) are
mode-independent; they accept any (M, D) bipolar matrix Xi as input.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[2]


_ALLOWED_MODES = ("synthetic", "pseudo_llm", "hyperprobe")


@dataclass
class EncoderConfig:
    mode: str = "synthetic"
    D: int = 4096                  # substrate codeword dimension
    d_llm: int = 4096              # Llama-3.1-8B hidden dim
    intercept_layer_frac: float = 0.7  # ell = L * 0.7
    llm_model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    hyperprobe_repo: str = "Ipazia-AI/hyperprobe"
    hyperprobe_ckpt: Optional[str] = None  # path or HF id
    anisotropy_rank: int = 64       # for pseudo_llm: low-rank cone dim
    anisotropy_strength: float = 0.5  # in [0, 1]; 0 = isotropic; 1 = rank-deficient
    seed: int = 0


def _validate_mode(mode: str) -> None:
    if mode not in _ALLOWED_MODES:
        raise ValueError(f"mode={mode!r} not in {_ALLOWED_MODES}")


class HyperprobeEncoder:
    """Pattern emitter: text prompt -> bipolar code in {-1, +1}^D.

    Constructed lazily; LLM + probe loaded only on first 'hyperprobe' call.
    Smoke + pseudo_llm modes never touch GPU.
    """

    def __init__(self, cfg: EncoderConfig):
        _validate_mode(cfg.mode)
        self.cfg = cfg
        self._rng = np.random.default_rng(cfg.seed)
        self._anis_basis: Optional[np.ndarray] = None
        self._llm = None
        self._tokenizer = None
        self._probe = None
        if cfg.mode == "pseudo_llm":
            self._anis_basis = self._build_anisotropy_basis()

    def _build_anisotropy_basis(self) -> np.ndarray:
        """Random orthonormal basis spanning a low-rank cone."""
        D = self.cfg.D
        r = self.cfg.anisotropy_rank
        Q = self._rng.standard_normal((D, r)).astype(np.float32)
        # Gram-Schmidt-ish via QR
        Q, _ = np.linalg.qr(Q)
        return Q  # (D, r)

    def encode_batch(self, prompts: List[str]) -> np.ndarray:
        """Return Xi of shape (len(prompts), D) with entries in {-1, +1}."""
        if self.cfg.mode == "synthetic":
            return self._encode_synthetic(len(prompts))
        if self.cfg.mode == "pseudo_llm":
            return self._encode_pseudo_llm(len(prompts))
        return self._encode_hyperprobe(prompts)

    def _encode_synthetic(self, m: int) -> np.ndarray:
        return self._rng.choice([-1.0, 1.0], size=(m, self.cfg.D)).astype(np.float32)

    def _encode_pseudo_llm(self, m: int) -> np.ndarray:
        """Mimic LLM residual anisotropy: sample from a low-rank cone, then sign().

        r = a * Q @ z + (1 - a) * eta, with z ~ N(0, I_r), eta ~ N(0, I_D / D).
        Then xi = sign(r).
        """
        a = self.cfg.anisotropy_strength
        D = self.cfg.D
        r = self.cfg.anisotropy_rank
        Q = self._anis_basis
        z = self._rng.standard_normal((m, r)).astype(np.float32)
        cone = z @ Q.T  # (m, D)
        iso = self._rng.standard_normal((m, D)).astype(np.float32) / np.sqrt(D)
        raw = a * cone + (1.0 - a) * iso
        xi = np.sign(raw).astype(np.float32)
        xi[xi == 0] = 1.0
        return xi

    def _ensure_full_loaded(self) -> None:
        """Lazy-load trained hyperprobe encoder + auth to HF.

        Note: we do NOT pre-load Llama-3.1-8B here. hyperprobe.ingest_embeddings
        does not accept a pre-loaded LLM kwarg; it loads internally per call.
        Pre-loading was wasted RAM/VRAM in earlier versions. The Llama snapshot
        is cached on disk (per the bring-up script) so per-call load is fast.

        Raises RuntimeError with a clear message if the checkpoint or any
        upstream dep is missing.
        """
        if self._probe is not None:
            return
        import os
        from pathlib import Path
        try:
            import hyperprobe  # noqa: F401
            from huggingface_hub import login as hf_login
            import torch  # noqa: F401
        except Exception as e:
            raise RuntimeError(
                f"hyperprobe full mode imports failed: {e}. "
                f"Run on Lambda after bring-up (pip install -e {self.cfg.hyperprobe_repo})."
            )

        # HF token: env var preferred (Lambda bring-up sets it); .hf_token fallback.
        tok = os.environ.get("HF_TOKEN", "").strip()
        if not tok:
            repo_root = Path(__file__).resolve().parents[2]
            tok_path = repo_root / ".hf_token"
            if tok_path.exists():
                tok = tok_path.read_text(encoding="utf-8").strip()
        if not tok:
            raise RuntimeError(
                "HF_TOKEN missing: required to load Llama-3.1-8B-Instruct (gated)."
            )
        hf_login(token=tok, add_to_git_credential=False)

        # Checkpoint resolution
        ckpt = self.cfg.hyperprobe_ckpt
        if not ckpt:
            repo_root = Path(__file__).resolve().parents[2]
            ckpt = str(repo_root / "data" / "exp_phase05_probe_training_v1" / "probe_ckpt.ckpt")
        if not Path(ckpt).exists():
            raise RuntimeError(
                f"Trained hyperprobe checkpoint not found at {ckpt}. "
                f"Run exp_phase05_probe_training_v1.py (must complete with HARD_PASS) "
                f"before any tier7 sub-test."
            )

        self._probe = hyperprobe.VSAEncoder.load_from_checkpoint(ckpt)
        self._probe.eval()

    def _encode_hyperprobe(self, prompts: List[str]) -> np.ndarray:
        """Forward all prompts through Llama-3.1-8B + trained probe; sign() output.

        Pipeline per arXiv:2509.25045:
            docs (batched) -> Llama forward -> residual at layer ell (sum-pooled
            per paper) -> probe encoder -> continuous VSA -> sign() -> {-1,+1}^D

        BATCHED: single ingest_embeddings call for ALL prompts. Dispatch 10
        lesson: per-doc ingest was both buggy (invalid `llm=` kwarg passed to
        a function that doesn't accept it) AND practically infeasible (each
        call reloaded Llama from cache; at 1000 docs × 30s = 8+ hours per
        sub-test seed). One batched call loads Llama once, forwards N docs
        at ~30 docs/sec on H100.
        """
        import hyperprobe
        import torch
        self._ensure_full_loaded()
        # Single batched ingest call (Dispatch 12 fix)
        emb_dict, *_ = hyperprobe.ingest_embeddings(
            list(prompts),
            self.cfg.llm_model_id,
            1,  # k_clusters=1 (Phase 0.5 doesn't need clustering at encode time)
        )
        out = np.zeros((len(prompts), self.cfg.D), dtype=np.float32)
        for i, doc in enumerate(prompts):
            if doc not in emb_dict:
                # Skipped doc -> leave zero row (cosine will be 0)
                continue
            emb = emb_dict[doc].sum(dim=0)
            with torch.no_grad():
                vsa_cont = self._probe(emb.unsqueeze(0)).squeeze(0).cpu().numpy()
            # Sign() to bipolar (substrate-native algebra)
            xi = np.sign(vsa_cont).astype(np.float32)
            xi[xi == 0] = 1.0
            out[i] = xi
        return out


def encoder_from_env(D: int = 4096, seed: int = 0) -> HyperprobeEncoder:
    """Build encoder, picking mode from HDLAB_RUN_MODE + HDLAB_ENCODER env vars.

    Defaults:
        HDLAB_RUN_MODE=smoke      -> mode='synthetic'
        HDLAB_RUN_MODE=full + no HDLAB_ENCODER -> mode='hyperprobe' (requires cloud)
        HDLAB_ENCODER=pseudo_llm  -> override (anisotropic, no LLM)
        HDLAB_ENCODER=synthetic   -> override (iid, no LLM)
    """
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    explicit = os.environ.get("HDLAB_ENCODER", "").strip()
    if explicit:
        mode = explicit
    elif run_mode == "full":
        mode = "hyperprobe"
    else:
        mode = "synthetic"
    cfg = EncoderConfig(mode=mode, D=D, seed=seed)
    return HyperprobeEncoder(cfg)


def _selftest() -> None:
    """Identity smoke: each mode emits {-1,+1}^D of correct shape and uniqueness."""
    for mode in ("synthetic", "pseudo_llm"):
        cfg = EncoderConfig(mode=mode, D=128, seed=42)
        enc = HyperprobeEncoder(cfg)
        Xi = enc.encode_batch(["p1", "p2", "p3"])
        assert Xi.shape == (3, 128), f"{mode}: bad shape {Xi.shape}"
        assert set(np.unique(Xi).tolist()).issubset({-1.0, 1.0}), \
            f"{mode}: values outside {{-1,+1}}: {np.unique(Xi)}"
        # Different prompts should map to different codes (Hamming distance > 0)
        ham01 = int(np.sum(Xi[0] != Xi[1]))
        assert ham01 > 0, f"{mode}: prompts collapsed to same code"
    print("[selftest] PASS: HyperprobeEncoder synthetic + pseudo_llm modes", flush=True)


if __name__ == "__main__":
    _selftest()
