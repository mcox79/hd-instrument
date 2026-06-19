"""Create 4 quick-fork experiments: R10 K=1024/2048 + generation K=32/64."""
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")
r10_base = (REPO / "experiments" / "exp_wave14b_r10_best_config_multiseed.py").read_text()
gen_base = (REPO / "experiments" / "exp_wave14d_generation_v2_K16.py").read_text()

# R10 K=1024 retry
for K, name in [(1024, "r10_best_config_K1024_retry2"), (2048, "r10_best_config_K2048_retry")]:
    v = r10_base.replace("K_LEVELS = [128, 256]", f"K_LEVELS = [{K}]")
    v = v.replace("r10_best_config_multiseed", name)
    (REPO / "experiments" / f"exp_wave14b_{name}.py").write_text(v)
    print(f"wrote exp_wave14b_{name}.py")

# Generation K=32 + K=64 from generation_v2_K16
for K, name in [(32, "generation_v2_K32"), (64, "generation_v2_K64")]:
    v = gen_base.replace("K = 16\n", f"K = {K}\n")
    v = v.replace("generation_v2_K16", name)
    (REPO / "experiments" / f"exp_wave14d_{name}.py").write_text(v)
    print(f"wrote exp_wave14d_{name}.py")
