"""
Bge-large encoder for substrate-KV retrieval (Q1 per Research VERIFY signoff).

Production encoder picked at cycle 187 PP-144 (bge-large 0.600 best of bge-large /
bge-small / e5-large). Decouples retrieval from generation: bge-large produces
high-quality retrieval embeddings while Qwen-2.5-1.5B-Instruct stays as the LLM
generator.

CPU-only by default (per Research VERIFY decision Q2: "keeps GPU clear for experiments").
Encoding speed: ~50-100 ms per single fact on i5-12400F at 169-fact scale.
"""
from __future__ import annotations
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"
DEFAULT_DEVICE = "cpu"   # per Research VERIFY Q2(A) for GPU coexistence


class BgeEncoder:
    """sentence-transformers wrapper for bge-large.

    Exposes .encode(texts: list[str]) -> np.ndarray (N, hidden_size) matching the
    PythiaClient interface so SubstrateKV is encoder-agnostic.

    Set BGE_INT8=1 in the environment to apply dynamic int8 quantization on
    CPU load (Route A Stage-A speedup per Research INGEST_ROUTE_A_APPROVED
    2026-06-11). Expected speedup ~2-3x on bge-large CPU inference; expected
    retrieval-quality drop <1pp on MTEB-class tasks.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = DEFAULT_DEVICE,
        int8: Optional[bool] = None,
    ):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers required; pip install sentence-transformers")
        self.model_name = model_name
        self.device = device

        # int8 from env var if not explicitly passed
        if int8 is None:
            int8 = os.environ.get("BGE_INT8", "0") == "1"
        self.int8 = bool(int8)

        logger.info("loading %s on %s (int8=%s) ...", model_name, device, self.int8)
        t0 = time.perf_counter()
        self.model = SentenceTransformer(model_name, device=device)
        # bge-large hidden_size == 1024 (production retrieval encoder per cycle 187 PP-144)
        self.hidden_size = self.model.get_sentence_embedding_dimension()

        if self.int8:
            if device != "cpu":
                logger.warning("int8 dynamic quantization is CPU-only; skipping on device=%s", device)
            else:
                import torch
                t_q = time.perf_counter()
                # sentence-transformers stacks: model[0] is the Transformer module,
                # whose .auto_model is the underlying HuggingFace BERT/encoder
                inner = self.model[0].auto_model
                quantized = torch.quantization.quantize_dynamic(
                    inner, {torch.nn.Linear}, dtype=torch.qint8
                )
                self.model[0].auto_model = quantized
                logger.info("applied dynamic int8 quantization in %.1fs", time.perf_counter() - t_q)

        load_s = time.perf_counter() - t0
        logger.info("loaded %s in %.1fs; hidden_size=%d", model_name, load_s, self.hidden_size)

    def encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts to (N, hidden_size) float32 vectors. L2-normalized by default
        because bge-large is trained for cosine similarity."""
        if not texts:
            return np.empty((0, self.hidden_size), dtype=np.float32)
        # bge-large produces L2-normalized embeddings by default when normalize_embeddings=True
        embs = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,  # crucial for cosine retrieval
            show_progress_bar=False,
        )
        return embs.astype(np.float32)


_singleton: Optional[BgeEncoder] = None


def get_encoder(model_name: str = DEFAULT_MODEL, device: str = DEFAULT_DEVICE) -> BgeEncoder:
    """Lazy singleton."""
    global _singleton
    if _singleton is None:
        _singleton = BgeEncoder(model_name=model_name, device=device)
    return _singleton


def health_check() -> dict:
    try:
        enc = get_encoder()
        v = enc.encode(["The substrate is the algebraic memory architecture for LLMs."])
        return {
            "ok": True,
            "model": enc.model_name,
            "device": enc.device,
            "hidden_size": int(enc.hidden_size),
            "encoded_shape": list(v.shape),
            "norm": float(np.linalg.norm(v[0])),
        }
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(json.dumps(health_check(), indent=2, default=str))
