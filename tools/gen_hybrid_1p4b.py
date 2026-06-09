"""Research P3: HYBRID production transfer to Pythia-1.4B. bf16 backbone + bf16 Flamingo @2 middle layers (every-layer OOMs at 1.4B) + fp32 PP-225 head + freed bge. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
h = (EXP / "exp_t5c_hybrid_lm_fact_gpu_v1.py").read_text(encoding="utf-8")
s = h.replace("t5c_hybrid_lm_fact_gpu_v1", "t5c_hybrid_1p4b_fp32_kb10k_v1").replace("t5c-hybrid-lm-fact", "hybrid-1p4b-fp32-kb10k")
s = s.replace('MODEL = "EleutherAI/pythia-160m"', 'MODEL = "EleutherAI/pythia-1.4b"')
s = s.replace("N_FACTS = 200 if SMOKE else 1500", "N_FACTS = 200 if SMOKE else 10000")
s = s.replace("ntr = int(0.6 * len(facts)); ftrain, ftest = facts[:ntr], facts[ntr:]",
              "ntr = int(0.6 * len(facts)); ftrain, ftest = facts[:ntr], facts[ntr:][:2000]")
# bf16 backbone
s = s.replace("mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()",
              "mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(DEV).eval()")
# Flamingo at 2 middle layers only (every-layer OOMs at 1.4B), bf16 adapters
s = s.replace('adapters = nn.ModuleList([FlamingoAdapter(H).to(DEV) for _ in range(NL)]); state = {"on": False}',
              'LAYERS = [10, 11]; adapters = nn.ModuleDict({str(L): FlamingoAdapter(H).to(DEV).to(torch.bfloat16) for L in LAYERS}); state = {"on": False}')
s = s.replace("return output if hs is None else (adapters[Li](hs, output[0]),) + tuple(output[1:])",
              "return output if hs is None else (adapters[str(Li)](hs, output[0]),) + tuple(output[1:])")
s = s.replace("hooks = [mdl.gpt_neox.layers[Li].attention.register_forward_hook(mk(Li), with_kwargs=True) for Li in range(NL)]",
              "hooks = [mdl.gpt_neox.layers[Li].attention.register_forward_hook(mk(Li), with_kwargs=True) for Li in LAYERS]")
s = s.replace('fl_params = [p for a in adapters for n, p in a.named_parameters() if n != "gate"]',
              'fl_params = [p for L in LAYERS for n, p in adapters[str(L)].named_parameters() if n != "gate"]')
s = s.replace("gates = [a.gate for a in adapters]", "gates = [adapters[str(L)].gate for L in LAYERS]")
s = s.replace('"gate0": round(float(torch.tanh(adapters[0].gate)), 4)', '"gate0": round(float(torch.tanh(adapters[str(LAYERS[0])].gate)), 4)')
# fp32 head: cast bf16 base logits to float before adding the fp32 projection (both fact training + fact_recall call sites)
s = s.replace('lg = mdl(**tok(f["prompt"], return_tensors="pt").to(DEV)).logits[0, -1, :] + pscale * proj(f["emb"])',
              'lg = mdl(**tok(f["prompt"], return_tensors="pt").to(DEV)).logits[0, -1, :].float() + pscale * proj(f["emb"])')
(EXP / "exp_t5c_hybrid_1p4b_fp32_kb10k_v1.py").write_text(s, encoding="utf-8"); print("wrote hybrid_1p4b_fp32_kb10k")
