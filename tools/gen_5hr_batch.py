"""5-hour unattended GPU batch: PP-225 transfer sweep (bigger-LLM fixes) + HYBRID-at-scale. All bf16-backbone + freed-bge + fp32-head = fits 8GB; safe unattended."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
FP = (EXP / "exp_t5c_pp225_pythia14b_fp32proj_v1.py").read_text(encoding="utf-8")   # bf16 LLM + freed bge + fp32 head (fits)
HY = (EXP / "exp_t5c_hybrid_lm_fact_gpu_v1.py").read_text(encoding="utf-8")

# 1. Qwen-1.5B with fp32 head (does fp32 fix the Qwen transfer failure?)
q = FP.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_qwen15b_fp32proj_v1").replace("pp225-pythia14b-fp32proj", "pp225-qwen15b-fp32proj")
q = q.replace('MODEL = "EleutherAI/pythia-1.4b"', 'MODEL = "Qwen/Qwen2.5-1.5B-Instruct"')
q = q.replace("AutoTokenizer.from_pretrained(MODEL)", "AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)")
q = q.replace("AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16)", "AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16, trust_remote_code=True)")
(EXP / "exp_t5c_pp225_qwen15b_fp32proj_v1.py").write_text(q, encoding="utf-8"); print("wrote pp225_qwen15b_fp32proj")

# 2. Pythia-1.4B scale-tune (logit-magnitude hypothesis: larger init scale so proj is not drowned)
s = FP.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_pythia14b_scaletune_v1").replace("pp225-pythia14b-fp32proj", "pp225-pythia14b-scaletune")
s = s.replace("scale = nn.Parameter(torch.tensor(1.0, device=DEV))", "scale = nn.Parameter(torch.tensor(8.0, device=DEV))   # scale-tune: larger init so proj is not drowned by big-model logits")
(EXP / "exp_t5c_pp225_pythia14b_scaletune_v1.py").write_text(s, encoding="utf-8"); print("wrote pp225_pythia14b_scaletune")

# 3. Pythia-1.4B logit-normalize (normalize base logits to unit std before adding proj)
n = FP.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_pythia14b_lognorm_v1").replace("pp225-pythia14b-fp32proj", "pp225-pythia14b-lognorm")
n = n.replace("def base_logits(prompt):\n        with torch.no_grad():\n            return mdl(**tok(prompt, return_tensors=\"pt\").to(DEV)).logits[0, -1, :]",
              "def base_logits(prompt):\n        with torch.no_grad():\n            bl = mdl(**tok(prompt, return_tensors=\"pt\").to(DEV)).logits[0, -1, :].float()\n            return (bl - bl.mean()) / (bl.std() + 1e-6)   # logit-norm: unit std so proj contribution is comparable")
n = n.replace("lg = mdl(**tok(f[\"prompt\"], return_tensors=\"pt\").to(DEV)).logits[0, -1, :].float() + pscale * proj(f[\"emb\"])",
              "_bl = mdl(**tok(f[\"prompt\"], return_tensors=\"pt\").to(DEV)).logits[0, -1, :].float(); _bl = (_bl - _bl.mean()) / (_bl.std() + 1e-6); lg = _bl + pscale * proj(f[\"emb\"])")
(EXP / "exp_t5c_pp225_pythia14b_lognorm_v1.py").write_text(n, encoding="utf-8"); print("wrote pp225_pythia14b_lognorm")

# 4. HYBRID at 10K facts (does Path-A+Path-B composition hold at larger KB?) -- cap fact eval to 2000 (avoid 50K-style eval blowup)
h = HY.replace("t5c_hybrid_lm_fact_gpu_v1", "t5c_hybrid_kb10k_v1").replace("t5c-hybrid-lm-fact", "hybrid-kb10k")
h = h.replace("N_FACTS = 200 if SMOKE else 1500", "N_FACTS = 200 if SMOKE else 10000")
h = h.replace("ntr = int(0.6 * len(facts)); ftrain, ftest = facts[:ntr], facts[ntr:]",
              "ntr = int(0.6 * len(facts)); ftrain, ftest = facts[:ntr], facts[ntr:][:2000]   # cap held-out eval (avoid 50K-style eval blowup)")
(EXP / "exp_t5c_hybrid_kb10k_v1.py").write_text(h, encoding="utf-8"); print("wrote hybrid_kb10k")
