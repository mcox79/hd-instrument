"""Derive E1 random-substrate baseline from C1 (mechanism drill, discriminates H3 regularization)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
s = (EXP / "exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")
s = s.replace("t5c_c1_multilayer_flamingo_train_gpu_v1", "t5c_e1_random_substrate_gpu_v1")
s = s.replace("t5c-c1-multilayer-flamingo-train", "t5c-e1-random-substrate")
# __init__: add a FROZEN random memory buffer (the "random substrate")
s = s.replace(
    "        self.ln = nn.LayerNorm(H); self.gate = nn.Parameter(torch.tensor(0.0)); self.H = H",
    "        self.ln = nn.LayerNorm(H); self.gate = nn.Parameter(torch.tensor(0.0)); self.H = H\n"
    "        self.register_buffer('rmem', torch.randn(64, H) * 0.02)   # E1: FROZEN random substrate (not past-token hiddens)")
# forward: q from sequence, k/v from the FROZEN RANDOM memory (no causal mask; external memory)
old_fwd = (
    "    def forward(self, hs, attn_out):\n"
    "        S = hs.shape[1]\n"
    "        z = self.ln(hs); q = self.Wq(z); k = self.Wk(z); v = self.Wv(z)   # LayerNorm before substrate cross-attn (Flamingo)\n"
    "        att = (q @ k.transpose(1, 2)) / math.sqrt(self.H)\n"
    "        mask = torch.triu(torch.ones(S, S, device=hs.device), diagonal=1).bool()\n"
    "        att = att.masked_fill(mask[None], float(\"-inf\"))\n"
    "        ctx = torch.softmax(att, dim=-1) @ v\n"
    "        return attn_out + torch.tanh(self.gate) * self.Wo(ctx)")
new_fwd = (
    "    def forward(self, hs, attn_out):\n"
    "        z = self.ln(hs); q = self.Wq(z)                                  # query from the sequence\n"
    "        k = self.Wk(self.rmem.to(hs.dtype)); v = self.Wv(self.rmem.to(hs.dtype))   # E1: keys/values from FROZEN RANDOM memory\n"
    "        att = (q @ k.transpose(0, 1)) / math.sqrt(self.H)                # (B,S,NMEM) -- no causal mask (external memory)\n"
    "        ctx = torch.softmax(att, dim=-1) @ v\n"
    "        return attn_out + torch.tanh(self.gate) * self.Wo(ctx)")
assert old_fwd in s, "forward block not found"
s = s.replace(old_fwd, new_fwd)
# verdict: E1 compares random-substrate improvement to the validated real improvement (C1 3-seed = 0.836x = 16.4%)
old_v = (
    'def verdict(r) -> Tuple[str, str]:\n'
    '    s = "baseline=%.2f modified=%.2f ratio=%.3fx gates=[%.3f,%.3f]" % (r["base_ppl"], r["mod_ppl"], r["ratio"], r["gate0"], r["gate1"])\n'
    '    if r["ratio"] < 2.0 and r["used"]:\n'
    '        tag = "IMPROVES" if r["ratio"] < 1.0 else "within 2x"\n'
    '        return ("HARD_PASS", "HARD_PASS: Tier-5c Phase C multi-layer Flamingo adapter -- perplexity %s baseline with both gates used -> Phase C grounded, Phase D unblocked. " % tag + s)\n'
    '    if r["ratio"] < 3.0:\n'
    '        return ("MIDDLE_BAND", "MIDDLE_BAND: perplexity within 3x or a gate marginal. " + s)\n'
    '    return ("HARD_FAIL", "HARD_FAIL: perplexity >=3x or gates unused. " + s)')
new_v = (
    'def verdict(r) -> Tuple[str, str]:\n'
    '    REAL_IMPR = 0.164   # C1 3-seed validated real-substrate improvement (0.836x)\n'
    '    rand_impr = max(0.0, 1.0 - r["ratio"]); frac = rand_impr / REAL_IMPR\n'
    '    s = "random-substrate ratio=%.4fx (improvement %.2f%%, = %.1f%% of real 16.4%%) gates=[%.3f,%.3f]" % (r["ratio"], rand_impr * 100, frac * 100, r["gate0"], r["gate1"])\n'
    '    if frac < 0.02:\n'
    '        return ("HARD_PASS", "HARD_PASS: random substrate gives <2%% of the real improvement -- the real past-token substrate provides GENUINE SIGNAL (H3 regularization refuted as primary; Path A is real context, not architecture artifact). " + s)\n'
    '    if frac > 0.08:\n'
    '        return ("HARD_FAIL", "HARD_FAIL: random substrate gives >8%% of real improvement -- most benefit is structural/regularization (H3), not substrate signal. " + s)\n'
    '    return ("MIDDLE_BAND", "MIDDLE_BAND: random substrate 2-8%% of real improvement (substrate mostly real signal, minor structural component). " + s)')
assert old_v in s, "verdict block not found"
s = s.replace(old_v, new_v)
(EXP / "exp_t5c_e1_random_substrate_gpu_v1.py").write_text(s, encoding="utf-8"); print("wrote exp_t5c_e1_random_substrate_gpu_v1.py")
