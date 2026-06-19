"""Build BATCH_5 GPU-T5C layer-count / position / model-scale sweep from validated C1 (Pythia gpt_neox) + D1 (Qwen model.layers)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
C1 = (EXP / "exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")
D1 = (EXP / "exp_t5c_d1_qwen15b_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")

def derive(base, anchor, st_old, st_new, model=None, layers=None, model_old=None, layers_old=None, steps_to=2500):
    s = base
    # rename anchor + selftest tag
    base_anchor = "t5c_c1_multilayer_flamingo_train_gpu_v1" if base is C1 else "t5c_d1_qwen15b_flamingo_train_gpu_v1"
    s = s.replace(base_anchor, anchor).replace(st_old, st_new)
    if model is not None:
        s = s.replace('MODEL = "%s"' % model_old, 'MODEL = "%s"' % model)
    if layers is not None:
        s = s.replace("LAYERS = %s" % layers_old, "LAYERS = %s" % layers)
    # shorter steps for the sweep (early-stop dominates anyway); base C1=12000, D1=10000
    s = s.replace("STEPS = 60 if \"--smoke\" in sys.argv else 12000", "STEPS = 60 if \"--smoke\" in sys.argv else %d" % steps_to)
    s = s.replace("STEPS = 50 if \"--smoke\" in sys.argv else 10000", "STEPS = 50 if \"--smoke\" in sys.argv else %d" % steps_to)
    (EXP / ("exp_" + anchor + ".py")).write_text(s, encoding="utf-8"); print("wrote", anchor)

# --- Pythia-160M layer sweeps (from C1; gpt_neox; 12 layers) ---
derive(C1, "t5c_gpu_t5c1_3layer_pythia160m_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c1-3layer", layers="[4, 5, 6]", layers_old="[4, 5]")
derive(C1, "t5c_gpu_t5c2_4layer_pythia160m_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c2-4layer", layers="[4, 5, 6, 7]", layers_old="[4, 5]")
derive(C1, "t5c_gpu_t5c3_6layer_pythia160m_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c3-6layer", layers="[3, 4, 5, 6, 7, 8]", layers_old="[4, 5]")
derive(C1, "t5c_gpu_t5c4_everylayer_pythia160m_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c4-everylayer", layers="[0,1,2,3,4,5,6,7,8,9,10,11]", layers_old="[4, 5]")
derive(C1, "t5c_gpu_t5c5_late_L8L9_pythia160m_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c5-late", layers="[8, 9]", layers_old="[4, 5]")
derive(C1, "t5c_gpu_t5c6_early_L2L3_pythia160m_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c6-early", layers="[2, 3]", layers_old="[4, 5]")

# --- model-scale (longer overnight runs) ---
# Pythia-1.4B (gpt_neox, 24 layers -> middle L10+L11)
derive(C1, "t5c_gpu_t5c7_pythia1p4b_2layer_v1", "t5c-c1-multilayer-flamingo-train", "gpu-t5c7-pythia1p4b",
       model="EleutherAI/pythia-1.4b", model_old="EleutherAI/pythia-160m", layers="[10, 11]", layers_old="[4, 5]", steps_to=2500)
# Qwen-2.5-3B (model.layers.self_attn, 36 layers -> middle L16+L17)
derive(D1, "t5c_gpu_t5c8_qwen3b_2layer_v1", "t5c-d1-qwen15b-flamingo-train", "gpu-t5c8-qwen3b",
       model="Qwen/Qwen2.5-3B-Instruct", model_old="Qwen/Qwen2.5-1.5B-Instruct", layers="[16, 17]", layers_old="[12, 13]", steps_to=2500)
