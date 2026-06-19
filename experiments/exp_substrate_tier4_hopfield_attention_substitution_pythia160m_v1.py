"""
substrate_tier4_hopfield_attention_substitution_pythia160m_v1 -- Tier 4: substrate-attention IN a real LLM -- GPU.

ROUTING: research_to_exp_dev_unblock_tier6_tier4_stageA (Cell 2). User's strategic frontier: substrate AS an
  intrinsic part of a REAL pretrained LLM. Replace ONE attention layer of Pythia-160M with a substrate-Hebbian
  (linear/Hopfield, softmax-free) attention; fine-tune on Shakespeare; is it TRAINING-STABLE (attention entropy
  not collapsed, gradients bounded, perplexity within 1.5x of an unmodified-Pythia fine-tune)? torch+transformers
  GPU, $0. overnight_queue. (Independent of Llama hang; Pythia-160M loads on the runner.)

MODEL: GPTNeoXForCausalLM (EleutherAI/pythia-160m). Swap layer L (middle) attention core: instead of
  softmax(QK^T)V, use NORMALIZED LINEAR/HEBBIAN attention out = (causal phi(Q)phi(K)^T) V / row-sum, phi=elu+1
  (= W=sum phi(K)V^T accumulated, retrieve phi(Q)@W -- the "W+=K@V^T, retrieve" substrate form). Keep the layer's
  learned q/k/v/dense projections + rotary (gradients flow). Fine-tune all params STEPS steps. Compare to an
  unmodified-Pythia fine-tune (same data/steps/seed).

METRICS: (a) substrate-layer attention entropy vs mean entropy of the other (softmax) layers (ratio); (b) grad-norm
  ratio of the substrate layer's attention params vs median of other layers' attention params; (c) eval perplexity
  substrate-model vs unmodified-model.

PRE-REGISTERED bands (per Drill 2): HARD-PASS entropy_ratio > 0.50 AND grad_ratio < 8 AND ppl_ratio <= 1.5.
  MIDDLE: entropy_ratio 0.25-0.50 OR grad_ratio 8-15. HARD-FAIL: entropy_ratio < 0.25 OR grad_ratio > 15 OR ppl_ratio > 2.

FORMULA SELF-TESTS (PROT-022): 1. linear-attn causal (no future leak). 2. phi=elu+1 nonneg. 3. normalized weights sum to 1.
GPU TEMPLATE: assert cuda. ASCII-only. write_metrics. PROT-018: no _nN (model-scaffold anchor; N/A).
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"   # avoid the rayon fork-deadlock that hung v6/v7
import argparse, time, math, types, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch, torch.nn as nn, torch.nn.functional as F
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_tier4_hopfield_attention_substitution_pythia160m_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

MODEL_ID = "EleutherAI/pythia-160m"; SWAP_LAYER = 6
if RUN_MODE == "smoke":
    SEEDS = [1]; STEPS = 12; BATCH = 4; SEQ = 64; CORPUS_CAP = 20000
else:
    SEEDS = [7, 17]; STEPS = 300; BATCH = 8; SEQ = 128; CORPUS_CAP = 300000
SHK_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"


def substrate_attention_forward(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
    """softmax-free normalized linear/Hebbian attention. query/key/value: (B, nh, T, hd). Returns (attn_output, weights)."""
    phiq = F.elu(query) + 1.0; phik = F.elu(key) + 1.0
    scores = torch.matmul(phiq, phik.transpose(2, 3))            # (B,nh,T,T) nonneg
    T = scores.shape[-1]
    causal = torch.tril(torch.ones(T, T, device=scores.device, dtype=scores.dtype))
    if attention_mask is not None:
        am = attention_mask[..., :T, :T]
        causal = causal * (am > -1.0).to(scores.dtype)           # respect padding mask too
    w = scores * causal
    w = w / (w.sum(dim=-1, keepdim=True) + 1e-6)                 # normalize per query -> distribution
    attn_output = torch.matmul(w, value).transpose(1, 2).contiguous()
    return attn_output, w


def make_substrate_forward(orig_forward):
    """custom GPTNeoXAttention.forward that uses substrate_attention_forward instead of the softmax interface."""
    def fwd(self, hidden_states, attention_mask, layer_past=None, position_embeddings=None, **kwargs):
        from transformers.models.gpt_neox.modeling_gpt_neox import apply_rotary_pos_emb
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, 3 * self.head_size)
        qkv = self.query_key_value(hidden_states).view(hidden_shape).transpose(1, 2)
        q, k, v = qkv.chunk(3, dim=-1)
        cos, sin = position_embeddings
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        if layer_past is not None:
            k, v = layer_past.update(k, v, self.layer_idx)
        attn_output, attn_weights = substrate_attention_forward(self, q, k, v, attention_mask, scaling=self.scaling)
        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.dense(attn_output)
        return attn_output, attn_weights
    return fwd


def _selftest():
    B, nh, T, hd = 2, 3, 5, 8
    q = torch.randn(B, nh, T, hd); k = torch.randn(B, nh, T, hd); v = torch.randn(B, nh, T, hd)
    am = torch.triu(torch.full((T, T), -1e9), 1)[None, None]
    out, w = substrate_attention_forward(None, q, k, v, am, scaling=1.0)
    assert out.shape == (B, T, nh, hd), "shape (B,T,nh,hd) per eager contract"
    assert float(w[0, 0, 0, 1:].abs().sum()) < 1e-5, "causal: query 0 attends only to key 0"
    assert float((F.elu(q) + 1).min()) > 0, "phi nonneg"
    rs = w.sum(dim=-1); assert float((rs - 1).abs().max()) < 1e-3, "weights normalized"
    print("[selftest] PASS: causal phi_nonneg normalized", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

# ---- heavy path (model load) only below ----
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
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


def entropy_of(w):  # w: (B,nh,T,T) attention distribution -> mean entropy (nats)
    p = w.clamp_min(1e-9); return float((-(p * p.log()).sum(-1)).mean())


def run_model(ids, seed, substrate):
    g = torch.Generator().manual_seed(seed)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, attn_implementation="eager", dtype=torch.float32).to(DEVICE); model.train()
    layers = model.gpt_neox.layers
    if substrate:
        att = layers[SWAP_LAYER].attention
        att.forward = types.MethodType(make_substrate_forward(att.forward), att)
    opt = torch.optim.AdamW(model.parameters(), lr=5e-5)
    t0 = time.time(); grad_norms = {}
    for step, (x, y) in enumerate(batch_iter(ids, BATCH, SEQ, g, STEPS)):
        out = model(input_ids=x, labels=None); logits = out.logits
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        if step == STEPS - 1:
            for li, lyr in enumerate(layers):
                gn = sum(float(p.grad.norm()) for p in lyr.attention.parameters() if p.grad is not None)
                grad_norms[li] = gn
        opt.step()
    wall = time.time() - t0
    # eval ppl + per-layer attention entropy
    model.eval()
    with torch.no_grad():
        losses = []
        for x, y in batch_iter(ids, BATCH, SEQ, torch.Generator().manual_seed(seed + 1), 8):
            o = model(input_ids=x); losses.append(float(F.cross_entropy(o.logits.reshape(-1, o.logits.size(-1)), y.reshape(-1))))
        ppl = math.exp(float(np.mean(losses)))
        xb, _ = next(batch_iter(ids, BATCH, SEQ, torch.Generator().manual_seed(seed + 2), 1))
        o = model(input_ids=xb, output_attentions=True)
        ents = [entropy_of(a) for a in o.attentions]
    return {"ppl": ppl, "wall": wall, "grad_norms": grad_norms, "layer_entropies": ents}


def compute_verdict(rs) -> Tuple[str, str]:
    ent_ratio = float(np.mean([r["ent_ratio"] for r in rs])); gr = float(np.mean([r["grad_ratio"] for r in rs]))
    pr = float(np.mean([r["ppl_ratio"] for r in rs]))
    summary = "entropy_ratio(substrate/others)=%.2f grad_ratio=%.1f ppl_ratio(substrate/baseline)=%.2f" % (ent_ratio, gr, pr)
    if ent_ratio > 0.50 and gr < 8 and pr <= 1.5:
        return ("HARD_PASS", "HARD_PASS: substrate-attention is training-stable inside Pythia-160M. " + summary)
    if (0.25 <= ent_ratio <= 0.50) or (8 <= gr <= 15) or (1.5 < pr <= 2.0):
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate-attention partially stable. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate-attention unstable (entropy collapse / grad explosion / ppl>2x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s model=%s swap_layer=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, MODEL_ID, SWAP_LAYER, STEPS), flush=True)
text = load_corpus(); tok = AutoTokenizer.from_pretrained(MODEL_ID)
ids = torch.tensor(tok(text)["input_ids"], dtype=torch.long); print("[corpus] tokens=%d" % len(ids), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rs = []
for seed in SEEDS:
    sub = run_model(ids, seed, substrate=True); base = run_model(ids, seed, substrate=False)
    others = [sub["layer_entropies"][i] for i in range(len(sub["layer_entropies"])) if i != SWAP_LAYER]
    ent_ratio = sub["layer_entropies"][SWAP_LAYER] / (float(np.mean(others)) + 1e-9)
    og = [sub["grad_norms"][i] for i in sub["grad_norms"] if i != SWAP_LAYER]
    grad_ratio = sub["grad_norms"][SWAP_LAYER] / (float(np.median(og)) + 1e-9)
    ppl_ratio = sub["ppl"] / (base["ppl"] + 1e-9)
    r = {"seed": seed, "substrate_ppl": sub["ppl"], "baseline_ppl": base["ppl"], "ppl_ratio": ppl_ratio,
         "swap_layer_entropy": sub["layer_entropies"][SWAP_LAYER], "other_layers_entropy": float(np.mean(others)),
         "ent_ratio": ent_ratio, "grad_ratio": grad_ratio, "substrate_wall": sub["wall"]}
    rs.append(r)
    print("  [seed=%d] ppl sub=%.1f base=%.1f (ratio=%.2f) ent_ratio=%.2f grad_ratio=%.1f" % (seed, sub["ppl"], base["ppl"], ppl_ratio, ent_ratio, grad_ratio), flush=True)
verdict, vmsg = compute_verdict(rs); print("\n[VERDICT] " + vmsg, flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print("[GPU] peak %.2f GB" % peak, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "model": MODEL_ID, "swap_layer": SWAP_LAYER, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rs, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)
