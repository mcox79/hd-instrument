"""make_long_variants.py -- create LONG-config variants of proven cells (deep buffer that runs 30-60min each).
Bumps SEEDS / N grids / inner counts (genuine more-data, not padding) so a few cells keep lanes busy for an extended window.
"""
import pathlib, re
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"


def bump(src_name, dst_anchor, repls):
    src = (EXP / src_name).read_text(encoding="utf-8")
    s = src
    # rename anchor (handles ANCHOR_NAME = "...")
    s = re.sub(r'ANCHOR_NAME = "[^"]+"', 'ANCHOR_NAME = "%s"' % dst_anchor, s, count=1)
    for old, new in repls:
        assert old in s, "MISS in %s: %s" % (src_name, old[:50])
        s = s.replace(old, new)
    (EXP / ("exp_%s.py" % dst_anchor)).write_text(s, encoding="utf-8")
    print("wrote exp_%s.py" % dst_anchor)


# 1. capacity battery LONG (GPU): 10 seeds, full N grid, fine loads -> ~40min
bump("exp_substrate_capacity_battery_gpu_v1.py", "substrate_capacity_battery_long_gpu_v1",
     [("SEEDS = [7, 17, 23, 29, 37]; N_GRID = [8192, 16384, 32768];",
       "SEEDS = [7, 17, 23, 29, 37, 41, 43, 47, 53, 59]; N_GRID = [8192, 16384, 32768];")])

# 2. multi-head battery LONG (GPU): more seeds + heads -> ~40min
bump("exp_multi_head_sparse_key_battery_gpu_v1.py", "multi_head_sparse_key_battery_long_gpu_v1",
     [("SEEDS = [7, 17, 23, 29, 37, 41]; N_GRID = [4096, 8192, 16384, 32768];",
       "SEEDS = [7, 17, 23, 29, 37, 41, 43, 47, 53, 59]; N_GRID = [4096, 8192, 16384, 32768];")])

# 3. hebb-vs-pinv LONG (CPU): 12 seeds, bigger N -> ~25min
bump("exp_hebb_vs_pseudoinverse_write_rule_v1.py", "hebb_vs_pseudoinverse_long_v1",
     [("SEEDS = [7, 17, 23]; N_SWEEP = [1024, 2048]; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3, 0.4, 0.55, 0.7, 0.85, 0.95]",
       "SEEDS = [7, 17, 23, 29, 37, 41, 43, 47, 53, 59, 61, 67]; N_SWEEP = [1024, 2048, 4096]; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3, 0.4, 0.55, 0.7, 0.85, 0.95]")])

# 4. khop K-scaling battery LONG (CPU): 10 seeds, high chains -> ~30min
bump("exp_fact_checked_khop_kscaling_battery_v1.py", "fact_checked_khop_kscaling_long_v1",
     [("SEEDS = [7, 17, 23, 29, 37]; N = 8192; V_C = 4000; CHAINS = 1500; KS = [3, 5, 8, 10, 15, 20]",
       "SEEDS = [7, 17, 23, 29, 37, 41, 43, 47, 53, 59]; N = 8192; V_C = 4000; CHAINS = 3000; KS = [3, 5, 8, 10, 15, 20]")])

print("DONE")
