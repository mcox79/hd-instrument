"""Derive MULTI-1 (every-layer 3-seed) + MULTI-2 (6-layer 3-seed) from the validated single-seed sweep cells (C1-structured)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
TOP_OLD = '''out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)'''
TOP_NEW = '''out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
SEEDS = [7] if SMOKE else [7, 13, 29]
rs = []
for _s in SEEDS:
    print("\\n[seed] ===== running seed %d =====" % _s, flush=True); rs.append(run(_s))
ratios = [r["ratio"] for r in rs]; mean = sum(ratios) / len(ratios)
std = (sum((x - mean) ** 2 for x in ratios) / len(ratios)) ** 0.5; used_all = all(r["used"] for r in rs)
rr = [round(x, 3) for x in ratios]
if len(rs) >= 3 and mean <= 0.95 and std < 0.05 and used_all:
    v = "HARD_PASS"; vmsg = "HARD_PASS: 3-seed mean perplexity ratio %.3fx (std %.3f), gates used all seeds -- multi-seed VALIDATED. ratios=%s" % (mean, std, rr)
elif mean < 1.0 and std < 0.10:
    v = "MIDDLE_BAND"; vmsg = "MIDDLE_BAND: 3-seed mean %.3fx std %.3f. ratios=%s" % (mean, std, rr)
else:
    v = "HARD_FAIL"; vmsg = "HARD_FAIL: 3-seed mean %.3fx std %.3f. ratios=%s" % (mean, std, rr)
print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(rs), "per_seed": rs, "summary": {"mean_ratio": mean, "std_ratio": std, "ratios": ratios}, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)'''
specs = [
    ("exp_t5c_gpu_t5c4_everylayer_pythia160m_v1.py", "exp_t5c_multi1_everylayer_3seed_v1.py",
     "t5c_gpu_t5c4_everylayer_pythia160m_v1", "t5c_multi1_everylayer_3seed_v1", "gpu-t5c4-everylayer", "multi1-everylayer-3seed"),
    ("exp_t5c_gpu_t5c3_6layer_pythia160m_v1.py", "exp_t5c_multi2_6layer_3seed_v1.py",
     "t5c_gpu_t5c3_6layer_pythia160m_v1", "t5c_multi2_6layer_3seed_v1", "gpu-t5c3-6layer", "multi2-6layer-3seed"),
]
for src, dst, an_old, an_new, st_old, st_new in specs:
    s = (EXP / src).read_text(encoding="utf-8")
    assert TOP_OLD in s, "top not found in " + src
    s = s.replace(an_old, an_new).replace(st_old, st_new)
    s = s.replace("def run() -> Dict:", "def run(SEED=7) -> Dict:")
    s = s.replace("torch.manual_seed(7)", "torch.manual_seed(SEED)")
    s = s.replace('Path(out_dir) / "ckpt.pt"', 'Path(out_dir) / ("ckpt_s%d.pt" % SEED)')
    s = s.replace('Path(out_dir) / "ckpt_best.pt"', 'Path(out_dir) / ("ckpt_best_s%d.pt" % SEED)')
    s = s.replace(TOP_OLD, TOP_NEW)
    (EXP / dst).write_text(s, encoding="utf-8"); print("wrote", dst)
