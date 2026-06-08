"""
Local LLM client for Tier 5 Sprint Panel A.

Single AutoModelForCausalLM instance serves BOTH:
  - encode(texts) -> last-token hidden states (for substrate-KV keys + queries)
  - generate(prompt) -> causal-LM continuation (the Panel A answer)

Default: Qwen-2.5-1.5B-Instruct.
  - Instruction-tuned (follows "use ONLY substrate facts" prompts)
  - Substrate-KV cross-family HP validated (PP-153 cycle 191; family-agnostic)
  - 2.0 GB fp16 VRAM on RTX 4060 Ti
  - Chat template support out-of-the-box

Alternatives:
  - EleutherAI/pythia-1.4b: BASE model, NOT instruction-tuned; hallucinates badly when
    asked to "use only substrate facts". D2 HP empirically validated for substrate-KV
    retrieval but unsuitable for instruction-following demo generation. Keep for
    Panel B substrate-attention experiments.
  - EleutherAI/pythia-2.8b: same base-model limitation, larger VRAM footprint.
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    torch = None
    AutoModelForCausalLM = None
    AutoTokenizer = None


DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


@dataclass
class PythiaResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    finish_reason: Optional[str] = None

    @property
    def cost_usd(self) -> float:
        """Local inference is $0 (compute on user's GPU)."""
        return 0.0


class PythiaClient:
    """Local Pythia inference: encode (substrate-KV keys/queries) + generate (LLM answer).

    Loads the model ONCE; encoding uses the base GPTNeoX transformer's last hidden state,
    generation uses the LM head's .generate().
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cuda",
        dtype: Optional[str] = "bf16",
        max_context_tokens: int = 1024,
    ):
        if torch is None:
            raise RuntimeError("torch + transformers required; install in .venv-demo")

        self.model_name = model_name
        self.device = device
        self.max_context_tokens = max_context_tokens

        dtype_map = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}
        torch_dtype = dtype_map.get(dtype, torch.bfloat16)

        logger.info("loading %s (dtype=%s) on %s ...", model_name, dtype, device)
        t0 = time.perf_counter()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
        ).to(device).eval()

        # Locate base transformer for hidden-state extraction (Pythia = GPTNeoX architecture)
        self.base = getattr(self.model, "gpt_neox", None) or getattr(self.model, "model", None)
        if self.base is None:
            raise RuntimeError(f"could not locate base transformer for {model_name}")

        self.hidden_size = self.model.config.hidden_size
        load_s = time.perf_counter() - t0
        logger.info(
            "loaded %s in %.1fs; hidden_size=%d; VRAM=%.2f GB",
            model_name, load_s, self.hidden_size,
            torch.cuda.memory_allocated() / (1024 ** 3) if device == "cuda" else 0.0,
        )

    def encode(self, texts: list[str], batch_size: int = 8) -> np.ndarray:
        """Encode `texts` to (N, hidden_size) by taking the last-real-token hidden state.

        Causal LMs concentrate semantics at the last token; mean pooling dilutes the signal
        (per [[feedback-causal-lm-last-token-pool]]).
        """
        if not texts:
            return np.empty((0, self.hidden_size), dtype=np.float32)
        outs = []
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                t = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=64,
                ).to(self.device)
                h = self.base(input_ids=t["input_ids"], attention_mask=t["attention_mask"]).last_hidden_state
                lens = t["attention_mask"].sum(1) - 1
                last_h = h[torch.arange(h.shape[0]), lens]
                outs.append(last_h.float().cpu().numpy())
        return np.concatenate(outs, axis=0).astype(np.float32)

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 80,
        temperature: float = 0.7,
        top_p: float = 0.9,
        system: Optional[str] = None,
    ) -> PythiaResponse:
        """Generate a causal continuation. If the tokenizer has a chat_template (instruct
        models like Qwen-Instruct), wraps the prompt as a chat message; otherwise treats
        `prompt` as a raw causal-LM continuation prefix.
        """
        if getattr(self.tokenizer, "chat_template", None):
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            full_prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
        else:
            full_prompt = prompt

        t = self.tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_context_tokens,
        ).to(self.device)
        input_tokens = t["input_ids"].shape[1]
        t0 = time.perf_counter()
        with torch.no_grad():
            out = self.model.generate(
                **t,
                max_new_tokens=max_new_tokens,
                temperature=max(0.01, temperature),
                top_p=top_p,
                do_sample=temperature > 0.0,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        latency_ms = (time.perf_counter() - t0) * 1000
        new_tokens = out[0][input_tokens:]
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return PythiaResponse(
            text=text.strip(),
            model=self.model_name,
            input_tokens=int(input_tokens),
            output_tokens=int(new_tokens.shape[0]),
            latency_ms=float(latency_ms),
            finish_reason="length" if new_tokens.shape[0] >= max_new_tokens else "eos",
        )


_singleton: Optional[PythiaClient] = None


def get_client(model_name: str = DEFAULT_MODEL, device: str = "cuda", dtype: str = "bf16") -> PythiaClient:
    """Lazy singleton so the backend loads the model once."""
    global _singleton
    if _singleton is None:
        _singleton = PythiaClient(model_name=model_name, device=device, dtype=dtype)
    return _singleton


def health_check(model_name: str = DEFAULT_MODEL) -> dict:
    """Cheap end-to-end: load (if not loaded) + encode + generate a few tokens."""
    try:
        client = get_client(model_name)
        keys = client.encode(["Substrate is the memory architecture for next-generation LLMs."])
        resp = client.generate("Substrate is", max_new_tokens=5, temperature=0.0)
        return {
            "ok": True,
            "model": resp.model,
            "hidden_size": client.hidden_size,
            "encoded_shape": list(keys.shape),
            "generated_text": resp.text,
            "generate_latency_ms": resp.latency_ms,
        }
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(json.dumps(health_check(), indent=2, default=str))
