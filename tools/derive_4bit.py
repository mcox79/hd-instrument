"""4-bit big-model scaling (unlocks OOM'd runs): Qwen-2.5-3B 2-layer + every-layer, via bitsandbytes nf4. From D1 (bf16 adapter, Qwen arch)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
D1 = (EXP / "exp_t5c_d1_qwen15b_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")

def derive(anchor, st_new, layers, steps_to=2500):
    s = D1.replace("t5c_d1_qwen15b_flamingo_train_gpu_v1", anchor).replace("t5c-d1-qwen15b-flamingo-train", st_new)
    s = s.replace("from transformers import AutoModelForCausalLM, AutoTokenizer",
                  "from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig")
    s = s.replace('mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16, trust_remote_code=True).to(DEV).eval()',
                  'mdl = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4"), trust_remote_code=True).eval()  # 4-bit nf4 frozen backbone')
    s = s.replace('MODEL = "Qwen/Qwen2.5-1.5B-Instruct"', 'MODEL = "Qwen/Qwen2.5-3B-Instruct"')
    s = s.replace("LAYERS = [12, 13]", "LAYERS = %s" % layers)
    s = s.replace("STEPS = 50 if \"--smoke\" in sys.argv else 10000", "STEPS = 50 if \"--smoke\" in sys.argv else %d" % steps_to)
    (EXP / ("exp_" + anchor + ".py")).write_text(s, encoding="utf-8"); print("wrote", anchor)

EV36 = "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]"
derive("t5c_scale1_qwen3b_2layer_4bit_v1", "scale1-qwen3b-2layer-4bit", "[16, 17]", 2500)
derive("t5c_scale1_qwen3b_everylayer_4bit_v1", "scale1-qwen3b-everylayer-4bit", EV36, 2500)
