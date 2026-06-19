"""Derive 3-seed validation cells from C1 + D1 (Path A). Substring replacements only (no multiline match)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
specs = [
    ("exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py", "exp_t5c_c1_3seed_validate_gpu_v1.py",
     "t5c_c1_multilayer_flamingo_train_gpu_v1", "t5c_c1_3seed_validate_gpu_v1",
     "t5c-c1-multilayer-flamingo-train", "t5c-c1-3seed-validate"),
    ("exp_t5c_d1_qwen15b_flamingo_train_gpu_v1.py", "exp_t5c_d1_3seed_validate_gpu_v1.py",
     "t5c_d1_qwen15b_flamingo_train_gpu_v1", "t5c_d1_3seed_validate_gpu_v1",
     "t5c-d1-qwen15b-flamingo-train", "t5c-d1-3seed-validate"),
]
V2 = ('_ratios = [x["ratio"] for x in rs]; _mean = sum(_ratios) / len(_ratios); '
      '_std = (sum((q - _mean) ** 2 for q in _ratios) / len(_ratios)) ** 0.5; _ua = all(x["used"] for x in rs); '
      'v = ("HARD_PASS" if (len(rs) >= 3 and _mean <= 0.95 and _std < 0.05 and _ua) else '
      '("MIDDLE_BAND" if (_mean < 1.0 and _std < 0.10) else "HARD_FAIL")); '
      'vmsg = "%s: 3-seed mean perplexity ratio %.3fx std %.3f gates-used=%s ratios=%s -- multi-seed validation" '
      '% (v, _mean, _std, _ua, [round(q, 3) for q in _ratios]);')
for src, dst, an_old, an_new, st_old, st_new in specs:
    s = (EXP / src).read_text(encoding="utf-8")
    assert an_old in s and "t0 = time.time(); r = run()" in s, "markers missing in " + src
    s = s.replace(an_old, an_new).replace(st_old, st_new)
    s = s.replace("def run() -> Dict:", "def run(SEED=7) -> Dict:")
    s = s.replace("torch.manual_seed(7)", "torch.manual_seed(SEED)")
    s = s.replace('Path(out_dir) / "ckpt.pt"', 'Path(out_dir) / ("ckpt_s%d.pt" % SEED)')
    s = s.replace('Path(out_dir) / "ckpt_best.pt"', 'Path(out_dir) / ("ckpt_best_s%d.pt" % SEED)')
    s = s.replace("t0 = time.time(); r = run()",
                  "t0 = time.time(); _SEEDS = [7] if SMOKE else [7, 13, 29]; rs = [run(_s) for _s in _SEEDS]")
    s = s.replace("v, vmsg = verdict(r);", V2)
    s = s.replace('"n_seeds": 1, "per_seed": [r],',
                  '"n_seeds": len(rs), "per_seed": rs, "summary": {"mean_ratio": _mean, "std_ratio": _std, "ratios": _ratios},')
    s = s.replace("write_metrics(out_dir, metrics, [r])", "write_metrics(out_dir, metrics, rs)")
    (EXP / dst).write_text(s, encoding="utf-8"); print("wrote", dst)
