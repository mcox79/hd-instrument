"""Sweep-2: confirm 'every-layer wins' at scale + on Qwen; push model scaling. From validated C1 (gpt_neox) + D1 (Qwen)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
C1 = (EXP / "exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")
D1 = (EXP / "exp_t5c_d1_qwen15b_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")

def derive(base, anchor, st_new, model_old, model, layers_old, layers, steps_old, steps_to=2500):
    base_anchor = "t5c_c1_multilayer_flamingo_train_gpu_v1" if base is C1 else "t5c_d1_qwen15b_flamingo_train_gpu_v1"
    st_old = "t5c-c1-multilayer-flamingo-train" if base is C1 else "t5c-d1-qwen15b-flamingo-train"
    s = base.replace(base_anchor, anchor).replace(st_old, st_new)
    s = s.replace('MODEL = "%s"' % model_old, 'MODEL = "%s"' % model)
    s = s.replace("LAYERS = %s" % layers_old, "LAYERS = %s" % layers)
    s = s.replace("STEPS = 60 if \"--smoke\" in sys.argv else %d" % steps_old, "STEPS = 60 if \"--smoke\" in sys.argv else %d" % steps_to)
    s = s.replace("STEPS = 50 if \"--smoke\" in sys.argv else %d" % steps_old, "STEPS = 50 if \"--smoke\" in sys.argv else %d" % steps_to)
    (EXP / ("exp_" + anchor + ".py")).write_text(s, encoding="utf-8"); print("wrote", anchor)

EV24 = "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]"
EV28 = "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]"
EV32 = "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]"

# does every-layer win at LARGER Pythia + does the advantage scale?
derive(C1, "t5c_s2_pythia1p4b_everylayer_v1", "s2-pythia1p4b-everylayer", "EleutherAI/pythia-160m", "EleutherAI/pythia-1.4b", "[4, 5]", EV24, 12000)
derive(C1, "t5c_s2_pythia2p8b_2layer_v1", "s2-pythia2p8b-2layer", "EleutherAI/pythia-160m", "EleutherAI/pythia-2.8b", "[4, 5]", "[15, 16]", 12000)
derive(C1, "t5c_s2_pythia2p8b_everylayer_v1", "s2-pythia2p8b-everylayer", "EleutherAI/pythia-160m", "EleutherAI/pythia-2.8b", "[4, 5]", EV32, 12000)
# does every-layer win on Qwen (other family)? + Qwen layer sweep
derive(D1, "t5c_s2_qwen1p5b_everylayer_v1", "s2-qwen1p5b-everylayer", "Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct", "[12, 13]", EV28, 10000)
derive(D1, "t5c_s2_qwen1p5b_4layer_v1", "s2-qwen1p5b-4layer", "Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct", "[12, 13]", "[12, 13, 14, 15]", 10000)
