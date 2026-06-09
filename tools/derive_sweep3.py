"""Sweep-3: fill the layer-count x model-size grid (160M/1.4B/Qwen-1.5B) + MULTI-3/4 every-layer 3-seed. Reliable C1/D1 derives."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
C1 = (EXP / "exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")
D1 = (EXP / "exp_t5c_d1_qwen15b_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")

def derive(base, anchor, st_new, model_old, model, layers_old, layers, steps_old, steps_to=2500):
    ba = "t5c_c1_multilayer_flamingo_train_gpu_v1" if base is C1 else "t5c_d1_qwen15b_flamingo_train_gpu_v1"
    so = "t5c-c1-multilayer-flamingo-train" if base is C1 else "t5c-d1-qwen15b-flamingo-train"
    s = base.replace(ba, anchor).replace(so, st_new)
    if model: s = s.replace('MODEL = "%s"' % model_old, 'MODEL = "%s"' % model)
    s = s.replace("LAYERS = %s" % layers_old, "LAYERS = %s" % layers)
    s = s.replace("STEPS = 60 if \"--smoke\" in sys.argv else %d" % steps_old, "STEPS = 60 if \"--smoke\" in sys.argv else %d" % steps_to)
    s = s.replace("STEPS = 50 if \"--smoke\" in sys.argv else %d" % steps_old, "STEPS = 50 if \"--smoke\" in sys.argv else %d" % steps_to)
    (EXP / ("exp_" + anchor + ".py")).write_text(s, encoding="utf-8"); print("wrote", anchor)

# layer-count grid fill
derive(C1, "t5c_g_pythia160m_8layer_v1", "g-pythia160m-8layer", None, None, "[4, 5]", "[2,3,4,5,6,7,8,9]", 12000)
derive(C1, "t5c_g_pythia160m_10layer_v1", "g-pythia160m-10layer", None, None, "[4, 5]", "[1,2,3,4,5,6,7,8,9,10]", 12000)
derive(C1, "t5c_g_pythia1p4b_4layer_v1", "g-pythia1p4b-4layer", "EleutherAI/pythia-160m", "EleutherAI/pythia-1.4b", "[4, 5]", "[9,10,11,12]", 12000)
derive(C1, "t5c_g_pythia1p4b_6layer_v1", "g-pythia1p4b-6layer", "EleutherAI/pythia-160m", "EleutherAI/pythia-1.4b", "[4, 5]", "[8,9,10,11,12,13]", 12000)
derive(D1, "t5c_g_qwen1p5b_6layer_v1", "g-qwen1p5b-6layer", None, None, "[12, 13]", "[11,12,13,14,15,16]", 10000)
derive(D1, "t5c_g_qwen1p5b_8layer_v1", "g-qwen1p5b-8layer", None, None, "[12, 13]", "[10,11,12,13,14,15,16,17]", 10000)

# MULTI-3 / MULTI-4: 3-seed of the every-layer cells at Qwen + Pythia-1.4B (3-seed transform)
TOP_OLD = '''out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)'''
TOP_NEW = '''out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
SEEDS = [7] if SMOKE else [7, 13, 29]
rs = [run(_s) for _s in SEEDS]
ratios = [r["ratio"] for r in rs]; mean = sum(ratios) / len(ratios)
std = (sum((x - mean) ** 2 for x in ratios) / len(ratios)) ** 0.5; used_all = all(r["used"] for r in rs); rr = [round(x, 3) for x in ratios]
if len(rs) >= 3 and mean <= 0.95 and std < 0.05 and used_all:
    v = "HARD_PASS"; vmsg = "HARD_PASS: 3-seed mean ratio %.3fx (std %.3f) gates-used -- multi-seed VALIDATED. ratios=%s" % (mean, std, rr)
elif mean < 1.0 and std < 0.10:
    v = "MIDDLE_BAND"; vmsg = "MIDDLE_BAND: 3-seed mean %.3fx std %.3f. ratios=%s" % (mean, std, rr)
else:
    v = "HARD_FAIL"; vmsg = "HARD_FAIL: 3-seed mean %.3fx std %.3f. ratios=%s" % (mean, std, rr)
print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(rs), "per_seed": rs, "summary": {"mean_ratio": mean, "std_ratio": std, "ratios": ratios}, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)'''
for src, dst, an_old, an_new, st_old, st_new in [
    ("exp_t5c_s2_qwen1p5b_everylayer_v1.py", "exp_t5c_multi3_qwen_everylayer_3seed_v1.py", "t5c_s2_qwen1p5b_everylayer_v1", "t5c_multi3_qwen_everylayer_3seed_v1", "s2-qwen1p5b-everylayer", "multi3-qwen-everylayer-3seed"),
    ("exp_t5c_s2_pythia1p4b_everylayer_v1.py", "exp_t5c_multi4_pythia1p4b_everylayer_3seed_v1.py", "t5c_s2_pythia1p4b_everylayer_v1", "t5c_multi4_pythia1p4b_everylayer_3seed_v1", "s2-pythia1p4b-everylayer", "multi4-pythia1p4b-everylayer-3seed"),
]:
    s = (EXP / src).read_text(encoding="utf-8")
    assert TOP_OLD in s, "top not found in " + src
    s = s.replace(an_old, an_new).replace(st_old, st_new)
    s = s.replace("def run() -> Dict:", "def run(SEED=7) -> Dict:").replace("torch.manual_seed(7)", "torch.manual_seed(SEED)")
    s = s.replace('Path(out_dir) / "ckpt.pt"', 'Path(out_dir) / ("ckpt_s%d.pt" % SEED)').replace('Path(out_dir) / "ckpt_best.pt"', 'Path(out_dir) / ("ckpt_best_s%d.pt" % SEED)')
    s = s.replace(TOP_OLD, TOP_NEW)
    (EXP / dst).write_text(s, encoding="utf-8"); print("wrote", dst)
