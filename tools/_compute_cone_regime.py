"""Compute cone-collapse formula + empirical projections for harder regime.

Goal: find (N, V_C, depth, psz_B) where:
  - BASELINE_A in [0.30, 0.70] (discriminating)
  - ORACLE_B in [0.50, 0.95] (UN-saturated; chain-grade-eligible)
  - lift_B_A >= 0.20

Empirical anchors (MEASURED@ from prior smoke metrics.json):
  - (N=2048, V_C=1000, d=10): BASELINE_A = 0.190
  - (N=8192, V_C=4000, d=10): BASELINE_A = 0.590
  - (N=8192, V_C=4000, d=10, psz=40): ORACLE_B = 1.000
  - (N=8192, V_C=4000, d=10, psz=100): ORACLE_C = 1.000
  - (N=8192, V_C=4000, d=10, psz=200): ORACLE_D = 0.990
"""
import math
from math import sqrt, erf, log


def phi(z):
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


def cone_xtalk(v_c_per_hop, n):
    return sqrt(max(v_c_per_hop - 1, 1) / max(n, 1))


def per_step_extreme_value(v_c_per_hop, n):
    """Extreme-value approx: P(N(1,x^2) > max of (V-1) N(0,x^2))."""
    x = cone_xtalk(v_c_per_hop, n)
    if v_c_per_hop <= 1:
        return 1.0
    e_max = x * sqrt(2 * log(v_c_per_hop - 1))
    margin = 1.0 - e_max
    if margin <= 0:
        return 0.0
    return phi(margin / (x * sqrt(2) + 1e-9))


print("=== EMPIRICAL ANCHORS (MEASURED@) ===")
print("v1 N=2048 V_C=1000 d=10: BASELINE_A=0.190 -> per_step=%.4f"
      % (0.190 ** (1.0 / 10)))
print("n8192 V_C=4000 d=10: BASELINE_A=0.590 -> per_step=%.4f"
      % (0.590 ** (1.0 / 10)))
print("n8192 V_C=4000 d=10 psz=200: ORACLE_D=0.990 -> per_step=%.4f"
      % (0.990 ** (1.0 / 10)))

print()
print("=== FORMULA vs SUBSTRATE ===")
for (n, vc, label) in [
    (2048, 1000, "v1"),
    (8192, 4000, "n8192_baseline"),
    (8192, 8000, "n8192_VC8000"),
    (8192, 16000, "n8192_VC16000"),
]:
    f = per_step_extreme_value(vc, n)
    print("  %s: N=%d V_C=%d xtalk=%.4f formula_per_step=%.4f formula_d10=%.4f"
          % (label, n, vc, cone_xtalk(vc, n), f, f ** 10))

print()
print("=== DEPTH SWEEP at N=8192 V_C=4000 (substrate empirical per_step=0.948) ===")
ps_base = 0.948
for d in [10, 12, 13, 15, 18, 20, 25]:
    print("  depth=%d: BASELINE_A_proj=%.4f" % (d, ps_base ** d))

print()
print("=== ORACLE_B PER-STEP ESTIMATE BY PARTITION SIZE ===")
print("psz=40 at d=10 -> 1.000  ->  per_step >= 1.0 (numerically saturated)")
print("psz=100 at d=10 -> 1.000 ->  per_step >= 1.0")
print("psz=200 at d=10 -> 0.990 ->  per_step = 0.999")
print("Need oracle per_step ~ 0.92-0.97 to UN-saturate at depth=15 (0.97^15=0.633).")
print("Formula projection at psz=400 N=8192 (V-1=399 competitors):")
ps400 = per_step_extreme_value(400, 8192)
print("  per_step_formula(psz=400) = %.4f -> d=15: %.4f" % (ps400, ps400 ** 15))
print("Formula projection at psz=800 N=8192:")
ps800 = per_step_extreme_value(800, 8192)
print("  per_step_formula(psz=800) = %.4f -> d=15: %.4f" % (ps800, ps800 ** 15))
print("Formula projection at psz=1000 N=8192:")
ps1000 = per_step_extreme_value(1000, 8192)
print("  per_step_formula(psz=1000) = %.4f -> d=15: %.4f" % (ps1000, ps1000 ** 15))

# Substrate beats formula at low V_C/N ratio (META_RULE_AN).
# Substrate lift factor at N=8192 V_C=4000: observed_d10/formula_d10
ps_form_4000 = per_step_extreme_value(4000, 8192)
print()
print("Substrate-vs-formula lift at N=8192 V_C=4000:")
print("  formula_d10=%.6f observed_d10=0.590"
      % (ps_form_4000 ** 10))
if ps_form_4000 ** 10 > 0:
    lift = 0.590 / (ps_form_4000 ** 10)
    print("  substrate_lift_ratio = %.2fx" % lift)
print("  formula_per_step=%.4f observed_per_step=0.948" % ps_form_4000)
print("  per_step_lift = %.4f" % (0.948 - ps_form_4000))

# Empirical projection: oracle psz=400 substrate per_step likely 0.99
# (since formula gives 0.77 at psz=400 but substrate beats it for narrowed argmax).
# Best estimate based on observed psz=200 -> 0.999 per_step:
# psz=400 vs psz=200 doubles competitors but xtalk grows from 0.156 to 0.221.
# Conservative substrate per_step at psz=400: ~0.98-0.99.
print()
print("=== CHOSEN DESIGN ===")
print("Option A: N=8192 V_C=4000 depth=15 psz_B=400 (10 partitions)")
print("  predicted BASELINE = 0.948^15 = %.4f" % (0.948 ** 15))
print("  predicted ORACLE_B (substrate per_step ~0.98) = %.4f" % (0.98 ** 15))
print("  predicted ORACLE_B (substrate per_step ~0.99) = %.4f" % (0.99 ** 15))
print("  predicted lift (0.98 case) = %.4f" % (0.98 ** 15 - 0.948 ** 15))
print()
print("Option B: N=8192 V_C=4000 depth=15 psz_B=800 (5 partitions)")
print("  predicted ORACLE_B (substrate per_step ~0.96) = %.4f" % (0.96 ** 15))
print("  predicted ORACLE_B (substrate per_step ~0.97) = %.4f" % (0.97 ** 15))
print("  but RANDOM_E with psz=800 (5 partitions): chance = 1/5 = 0.2/hop")
print("    RANDOM_E_d15 ~ 0.2^15 = %.6f (still ~0, ok)" % (0.2 ** 15))
print()
print("Option C: N=8192 V_C=4000 depth=15 psz_B=400; KEEP ORACLE_C/D wider")
print("  ARM_C psz=800 (5 parts); ARM_D psz=2000 (2 parts) for sweep")
print()
print("=== RECOMMENDATION ===")
print("Choose: N=8192 V_C=4000 depth=15 psz_B=400 (10 parts)")
print("  - matches META_RULE_AN substrate-lifts-formula at N=8192")
print("  - baseline projection ~0.46 (in [0.30, 0.70] discriminating)")
print("  - oracle projection ~0.74-0.86 (in [0.50, 0.95] un-saturated)")
print("  - lift ~ 0.30-0.40 (above HP 0.20)")
print("  - RANDOM_E (random psz=400): 1/10 = 0.10/hop -> 0.10^15 = 1e-15")
print("  - depth=15 also matches BARRIER 1 ceiling-extension goal")

print()
print("=== SMOKE GATE BANDS ===")
print("ORACLE_B  : [0.40, 0.95] (un-saturated; HP requires < 0.99)")
print("BASELINE_A: [0.05, 0.70] (was [0.11, 0.25] at d=10; widened for d=15)")
print("ORACLE_B - BASELINE_A: >= 0.20")
print("RANDOM_E  : < 0.05")
