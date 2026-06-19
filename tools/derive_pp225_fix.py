"""Re-derive PP225 scale variants (Qwen-1.5B, Pythia-1.4B) with memory fix: bf16 LLM + free bge-large after embedding + bf16 proj."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
R3 = (EXP / "exp_t5c_kblam_proj_head_gpu_v1.py").read_text(encoding="utf-8")

def make(anchor, st_new, model, trust):
    s = R3.replace("t5c_kblam_proj_head_gpu_v1", anchor).replace("t5c-kblam-proj-head", st_new)
    s = s.replace('MODEL = "EleutherAI/pythia-160m"', 'MODEL = "%s"' % model)
    if trust:
        s = s.replace("AutoTokenizer.from_pretrained(MODEL)", "AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)")
    # bf16 LLM (halves VRAM vs fp32)
    s = s.replace("AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()",
                  "AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16%s).to(DEV).eval()" % (", trust_remote_code=True" if trust else ""))
    # store embeddings as bf16 + FREE bge-large right after embedding (only needed once)
    s = s.replace('    for f, e in zip(facts, embed([f["text"] for f in facts])):\n        f["emb"] = e',
                  '    for f, e in zip(facts, embed([f["text"] for f in facts])):\n        f["emb"] = e.to(torch.bfloat16)\n    del enc_mdl; torch.cuda.empty_cache()   # free bge-large; only needed for the one-time embed')
    # proj + scale in bf16 to match the bf16 LLM logits
    s = s.replace("proj = nn.Linear(Edim, V, bias=False).to(DEV); nn.init.normal_(proj.weight, std=0.02)",
                  "proj = nn.Linear(Edim, V, bias=False).to(DEV).to(torch.bfloat16); nn.init.normal_(proj.weight, std=0.02)")
    s = s.replace("scale = nn.Parameter(torch.tensor(1.0, device=DEV))",
                  "scale = nn.Parameter(torch.tensor(1.0, device=DEV, dtype=torch.bfloat16))")
    # CE wants float
    s = s.replace("loss = torch.nn.functional.cross_entropy(lg.unsqueeze(0), torch.tensor([f[\"aid\"]], device=DEV))",
                  "loss = torch.nn.functional.cross_entropy(lg.float().unsqueeze(0), torch.tensor([f[\"aid\"]], device=DEV))")
    # del at end references enc_mdl which is already freed
    s = s.replace("prog.close(); del mdl, enc_mdl", "prog.close(); del mdl")
    (EXP / ("exp_" + anchor + ".py")).write_text(s, encoding="utf-8"); print("wrote", anchor)

make("t5c_pp225_qwen15b_bf16_v1", "pp225-qwen15b-bf16", "Qwen/Qwen2.5-1.5B-Instruct", True)
make("t5c_pp225_pythia14b_bf16_v1", "pp225-pythia14b-bf16", "EleutherAI/pythia-1.4b", False)
