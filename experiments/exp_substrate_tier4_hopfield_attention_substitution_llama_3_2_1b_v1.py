"""substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1 -- Tier 4 at 1B scale.

ROUTING: exp_dev_to_testbed_tier4_llama1b_cloud_dispatch_2026-06-05 (USER AUTHORIZED
  cloud H100 $1-3 per Exp-Dev's note). Critical Phase-2 architecture-scaling test:
  replicate the validated Pythia Tier-4 result (substrate-Hebbian linear/Hopfield
  attention substituted for ONE attention layer, training-stable) at Llama-3.2-1B
  (16 layers, GQA, RoPE). Does substrate-as-attention hold at 1B params?

REFERENCE: exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1.py
  Pythia HARD_PASS: ppl_ratio 1.06, entropy_ratio 3.08, grad_ratio 0.7.

DIFFS FROM PYTHIA REFERENCE (per Exp-Dev spec):
  - MODEL_ID  -> meta-llama/Llama-3.2-1B (gated; file-first HF token)
  - SWAP_LAYER -> 8 of 16 (mid layer)
  - Attribute  -> model.model.layers[L].self_attn (LlamaAttention)
  - GQA        -> repeat_kv on K and V to match Q's num_heads before substrate attn
  - dtype      -> torch.float32 (H100 has memory; fp32 for stability)
  - attn_impl  -> "eager" (required for our forward override + output_attentions)
  - grad-clip  -> 1.0 (already in Pythia)
  - HF token   -> file-first precedence (Rung A v5/v6 lesson; already validated for
                  Llama-3.2-1B base per testbed_to_exp_dev_llama_1b_per_token_residuals_delivered)

PIPELINE: load Llama-3.2-1B + tokenizer; swap layer 8 self_attn forward with our
  substrate version; fine-tune on Shakespeare for STEPS steps at LR=5e-5; measure
  (a) per-layer attention entropy at last batch (substrate layer vs others),
  (b) per-layer grad norms (substrate layer vs median of others),
  (c) eval perplexity substrate-model vs unmodified-Llama-baseline.

PRE-REG bands (same as Pythia Tier-4 per Exp-Dev spec):
  HARD-PASS:   ppl_ratio (substrate/baseline) <= 1.5 AND entropy_ratio > 0.50
               AND grad_ratio < 8.
  MIDDLE:      ppl_ratio 1.5-3 OR entropy_ratio 0.25-0.50 OR grad_ratio 8-15.
  HARD-FAIL:   ppl_ratio > 3 OR entropy_ratio < 0.25 OR grad_ratio > 15 OR NaN.

ENV defenses (carry-over from prior cloud bugs):
  - TOKENIZERS_PARALLELISM=false BEFORE transformers import (Llama v6/v7 deadlock fix)
  - PROT-022 selftests at import + --self-test early-exit gate
  - File-first HF token (Rung A v5/v6 lesson; Llama is gated)
  - ASCII-only stdout
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
# Llama v6/v7 lesson: TOKENIZERS_PARALLELISM=false BEFORE transformers import.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, time, math, types, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)
import numpy as np

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

MODEL_ID = "meta-llama/Llama-3.2-1B"
SWAP_LAYER = 8                        # mid layer (16 total in Llama-3.2-1B)

if RUN_MODE == "smoke":
    SEEDS = [1]
    STEPS = 6
    BATCH = 2
    SEQ = 32
    CORPUS_CAP = 20000
else:
    SEEDS = [7, 17]
    STEPS = 300
    BATCH = 4                         # Llama-1B fp32 is bigger than Pythia; halve batch
    SEQ = 128
    CORPUS_CAP = 300000

SHK_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"


def _load_hf_token() -> str:
    """File-first HF token precedence. Raises if missing (Llama is gated)."""
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        v = tok_path.read_text(encoding="utf-8").strip()
        if v:
            return v
    env_tok = os.environ.get("HF_TOKEN", "").strip()
    if env_tok:
        return env_tok
    raise RuntimeError(
        "HF token not found: place token at <repo>/.hf_token OR set HF_TOKEN env. "
        "Llama-3.2-1B is a gated repo and requires a license-accepted token."
    )


# ---------------- substrate-attention core (same as Pythia v1) ----------------

def substrate_attention_forward(query, key, value, attention_mask):
    """softmax-free normalized linear/Hebbian attention.

    Shapes (per eager attention contract after q/k/v projection + RoPE + repeat_kv):
        query, key, value: (B, nh, T, hd)
        attention_mask: (B, 1, T, T) or None
    Returns:
        (attn_output, attn_weights) with attn_output shape (B, T, nh, hd) per the
        eager-attention convention LlamaAttention.forward expects right before
        reshape + o_proj.
    """
    phiq = F.elu(query) + 1.0
    phik = F.elu(key) + 1.0
    scores = torch.matmul(phiq, phik.transpose(2, 3))    # (B, nh, T, T) nonneg
    T = scores.shape[-1]
    causal = torch.tril(torch.ones(T, T, device=scores.device, dtype=scores.dtype))
    if attention_mask is not None:
        am = attention_mask[..., :T, :T]
        # respect padding-style mask: positions with am <= some-large-negative are masked
        causal = causal * (am > -1.0).to(scores.dtype)
    w = scores * causal
    w = w / (w.sum(dim=-1, keepdim=True) + 1e-6)         # normalize per query
    attn_output = torch.matmul(w, value).transpose(1, 2).contiguous()  # (B, T, nh, hd)
    return attn_output, w


def _repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    """Mirror of transformers.models.llama.modeling_llama.repeat_kv. Expand
    (B, num_kv_heads, T, hd) -> (B, num_heads, T, hd) by repeating each KV head."""
    if n_rep == 1:
        return hidden_states
    B, n_kv, T, hd = hidden_states.shape
    hidden_states = hidden_states[:, :, None, :, :].expand(B, n_kv, n_rep, T, hd)
    return hidden_states.reshape(B, n_kv * n_rep, T, hd)


def make_substrate_llama_forward(orig_forward):
    """Replacement LlamaAttention.forward that uses substrate_attention_forward.

    Mirrors LlamaAttention.forward (transformers >=4.45) but calls our
    substrate attention instead of the eager softmax interface. Compatible
    with the GQA layout (num_key_value_heads < num_heads): we repeat_kv on
    k_states and v_states before passing to substrate_attention_forward.
    """
    def fwd(self,
            hidden_states: torch.Tensor,
            position_embeddings: Tuple[torch.Tensor, torch.Tensor],
            attention_mask: Optional[torch.Tensor] = None,
            past_key_value=None,
            cache_position=None,
            **kwargs):
        from transformers.models.llama.modeling_llama import apply_rotary_pos_emb
        input_shape = hidden_states.shape[:-1]                      # (B, T)
        hidden_shape = (*input_shape, -1, self.head_dim)

        # Separate q/k/v projections (Llama vs Pythia's fused query_key_value)
        query_states = self.q_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        key_states   = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

        # Llama-3.2 RoPE: cos/sin come from position_embeddings tuple
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)

        # Past-KV cache update (training phase typically has past_key_value=None)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(
                key_states, value_states, self.layer_idx, cache_kwargs
            )

        # GQA: repeat_kv on K and V so their head count matches Q's
        n_rep = self.config.num_attention_heads // self.config.num_key_value_heads
        key_states_rep   = _repeat_kv(key_states,   n_rep)
        value_states_rep = _repeat_kv(value_states, n_rep)

        # Substrate-attention core (same as Pythia version)
        attn_output, attn_weights = substrate_attention_forward(
            query_states, key_states_rep, value_states_rep, attention_mask
        )

        # attn_output shape after substrate_attention_forward: (B, T, nh, hd)
        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.o_proj(attn_output)

        # LlamaAttention return: (attn_output, attn_weights). past_key_value
        # is mutated in place above (HF Cache pattern); third element omitted
        # so the model's downstream tuple-unpack in transformers 4.45+ works.
        return attn_output, attn_weights

    return fwd


# ---------------- PROT-022 self-tests ----------------

def _selftest():
    """Causal + phi-nonneg + normalized + GQA-repeat sanity."""
    B, nh, T, hd = 2, 4, 5, 8
    q = torch.randn(B, nh, T, hd)
    k = torch.randn(B, nh, T, hd)
    v = torch.randn(B, nh, T, hd)
    am = torch.triu(torch.full((T, T), -1e9), 1)[None, None]
    out, w = substrate_attention_forward(q, k, v, am)
    assert out.shape == (B, T, nh, hd), f"shape wrong: got {out.shape}, want ({B}, {T}, {nh}, {hd})"
    assert float(w[0, 0, 0, 1:].abs().sum()) < 1e-5, "causal: query 0 attends only to key 0"
    assert float((F.elu(q) + 1).min()) > 0, "phi nonneg"
    rs = w.sum(dim=-1)
    assert float((rs - 1).abs().max()) < 1e-3, "weights normalized per query"

    # GQA repeat_kv check
    kv = torch.randn(B, 2, T, hd)
    kv_rep = _repeat_kv(kv, 3)
    assert kv_rep.shape == (B, 6, T, hd), f"repeat_kv shape: got {kv_rep.shape}, want ({B},6,{T},{hd})"
    # Each KV head should appear 3 consecutive times
    assert torch.allclose(kv_rep[:, 0], kv_rep[:, 1]) and torch.allclose(kv_rep[:, 1], kv_rep[:, 2])
    assert torch.allclose(kv_rep[:, 3], kv_rep[:, 4]) and torch.allclose(kv_rep[:, 4], kv_rep[:, 5])
    print("[selftest] PASS: causal + phi_nonneg + normalized + GQA_repeat", flush=True)


_selftest()
if _ARGS.self_test:
    print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
    sys.exit(0)


# ---- heavy path (model load) only below this gate ----
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available; this script is GPU-only.", flush=True)
    sys.exit(1)
DEVICE = torch.device("cuda")
print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_corpus():
    local = REPO / "data" / "corpora" / "tinyshakespeare.txt"
    if local.exists():
        return local.read_text(encoding="utf-8", errors="replace")[:CORPUS_CAP]
    with urllib.request.urlopen(SHK_URL, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")[:CORPUS_CAP]


def batch_iter(ids, bs, seq, g, n):
    for _ in range(n):
        ix = torch.randint(0, len(ids) - seq - 1, (bs,), generator=g)
        x = torch.stack([ids[i:i + seq] for i in ix]).to(DEVICE)
        y = torch.stack([ids[i + 1:i + 1 + seq] for i in ix]).to(DEVICE)
        yield x, y


def entropy_of(w):
    """w: (B, nh, T, T) attention distribution -> mean entropy (nats)."""
    p = w.clamp_min(1e-9)
    return float((-(p * p.log()).sum(-1)).mean())


def run_model(ids, seed, substrate):
    """Train Llama-3.2-1B (substrate-swapped or unmodified) on Shakespeare,
    then eval ppl + per-layer attention entropy."""
    g = torch.Generator().manual_seed(seed)
    token = _load_hf_token()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        attn_implementation="eager",
        torch_dtype=torch.float32,
    ).to(DEVICE)
    model.train()
    layers = model.model.layers          # Llama: model.model.layers[i].self_attn
    if substrate:
        att = layers[SWAP_LAYER].self_attn
        att.forward = types.MethodType(make_substrate_llama_forward(att.forward), att)
        print(f"[swap] layer {SWAP_LAYER} self_attn -> substrate (Hebbian linear-attn)", flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=5e-5)
    t0 = time.time()
    grad_norms: Dict[int, float] = {}
    for step, (x, y) in enumerate(batch_iter(ids, BATCH, SEQ, g, STEPS)):
        out = model(input_ids=x, labels=None)
        logits = out.logits
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        if step == STEPS - 1:
            for li, lyr in enumerate(layers):
                gn = sum(float(p.grad.norm()) for p in lyr.self_attn.parameters() if p.grad is not None)
                grad_norms[li] = gn
        opt.step()
    wall = time.time() - t0

    # Eval ppl + per-layer entropy
    model.eval()
    with torch.no_grad():
        losses = []
        for x, y in batch_iter(ids, BATCH, SEQ, torch.Generator().manual_seed(seed + 1), 8):
            o = model(input_ids=x)
            losses.append(float(F.cross_entropy(o.logits.reshape(-1, o.logits.size(-1)), y.reshape(-1))))
        ppl = math.exp(float(np.mean(losses)))
        xb, _ = next(batch_iter(ids, BATCH, SEQ, torch.Generator().manual_seed(seed + 2), 1))
        o = model(input_ids=xb, output_attentions=True)
        ents = [entropy_of(a) for a in o.attentions]

    # Free model + cache before returning (next run_model call needs the VRAM)
    del model, opt
    torch.cuda.empty_cache()
    return {"ppl": ppl, "wall": wall, "grad_norms": grad_norms, "layer_entropies": ents}


def compute_verdict(rs) -> Tuple[str, str]:
    ent_ratio = float(np.mean([r["ent_ratio"] for r in rs]))
    gr = float(np.mean([r["grad_ratio"] for r in rs]))
    pr = float(np.mean([r["ppl_ratio"] for r in rs]))
    summary = (f"entropy_ratio(substrate/others)={ent_ratio:.2f} "
               f"grad_ratio={gr:.1f} ppl_ratio(substrate/baseline)={pr:.2f}")
    if ent_ratio > 0.50 and gr < 8 and pr <= 1.5:
        return ("HARD_PASS", f"HARD_PASS: substrate-attention training-stable inside Llama-3.2-1B at SWAP_LAYER={SWAP_LAYER}. {summary}")
    if (0.25 <= ent_ratio <= 0.50) or (8 <= gr <= 15) or (1.5 < pr <= 2.0):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: substrate-attention partially stable in Llama-3.2-1B. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: substrate-attention unstable in Llama-3.2-1B (entropy collapse / grad explosion / ppl>2x). {summary}")


def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} "
          f"model={MODEL_ID} swap_layer={SWAP_LAYER} steps={STEPS} batch={BATCH} seq={SEQ}",
          flush=True)
    token = _load_hf_token()
    text = load_corpus()
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    ids = torch.tensor(tok(text)["input_ids"], dtype=torch.long)
    print(f"[corpus] tokens={len(ids)}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    rs = []
    for seed in SEEDS:
        sub = run_model(ids, seed, substrate=True)
        base = run_model(ids, seed, substrate=False)
        others = [sub["layer_entropies"][i] for i in range(len(sub["layer_entropies"])) if i != SWAP_LAYER]
        ent_ratio = sub["layer_entropies"][SWAP_LAYER] / (float(np.mean(others)) + 1e-9)
        og = [sub["grad_norms"][i] for i in sub["grad_norms"] if i != SWAP_LAYER]
        grad_ratio = sub["grad_norms"][SWAP_LAYER] / (float(np.median(og)) + 1e-9)
        ppl_ratio = sub["ppl"] / (base["ppl"] + 1e-9)
        r = {
            "seed": seed,
            "substrate_ppl": sub["ppl"],
            "baseline_ppl": base["ppl"],
            "ppl_ratio": ppl_ratio,
            "swap_layer_entropy": sub["layer_entropies"][SWAP_LAYER],
            "other_layers_entropy": float(np.mean(others)),
            "ent_ratio": ent_ratio,
            "grad_ratio": grad_ratio,
            "substrate_wall": sub["wall"],
            "baseline_wall": base["wall"],
        }
        rs.append(r)
        print(f"  [seed={seed}] ppl sub={sub['ppl']:.1f} base={base['ppl']:.1f} "
              f"(ratio={ppl_ratio:.2f}) ent_ratio={ent_ratio:.2f} grad_ratio={grad_ratio:.1f}",
              flush=True)

    verdict, vmsg = compute_verdict(rs)
    print(f"\n[VERDICT] {vmsg}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"[GPU] peak {peak:.2f} GB", flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "model": MODEL_ID,
        "swap_layer": SWAP_LAYER,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "per_seed": rs,
        "elapsed_s": time.time() - t0,
        "gpu_peak_gb": peak,
    }
    write_metrics(out_dir, metrics, rs)
    print("[metrics] written", flush=True)


if __name__ == "__main__":
    main()
