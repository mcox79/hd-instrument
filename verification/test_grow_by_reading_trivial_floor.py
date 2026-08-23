"""Scaffold-free witness for problem `the_grow_by_reading_pass_has_no_floor`.

Recomputes the headline INDEPENDENTLY of the scorer, straight from the JSON population files (no
frontend, no numpy-from-the-scorer). Checks:
  1. real precision recomputed from the ORIGINAL hand-check == 90/100 == 0.90.
  2. every "inherited" trivial row truly carries the ORIGINAL human C/W label for that item (so the
     inheritance is not silently relabelling the real arm's own judgements).
  3. each arm's precision in metrics_scored.json == an independent recount from the adjudicated pop.
  4. the strongest genuinely-trivial floor is CI-separated BELOW the real arm (paired bootstrap on
     the same 100 items, recomputed here), i.e. the 0.90 is not a pure selection artifact.
  5. the information-free twin (constant 'water') LOSES, CI-separated -- the mandated info-free control.

Run: .venv/Scripts/python.exe verification/test_grow_by_reading_trivial_floor.py
"""
import json
import os
import random

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "exp_grow_by_reading_trivial_floor_v1")
SRC = os.path.join(REPO, "data", "exp_stated_entity_fate_reading_extractor_v2_highprecision")

orig = json.load(open(os.path.join(SRC, "_survivors_handcheck_adjudicated.json"), encoding="utf-8"))
pop = json.load(open(os.path.join(D, "_adjudicated_population.json"), encoding="utf-8"))["rows"]
per_item = json.load(open(os.path.join(D, "_per_item.json"), encoding="utf-8"))
scored = json.load(open(os.path.join(D, "metrics_scored.json"), encoding="utf-8"))

N = 100
orig_rows = orig["rows"]
assert len(orig_rows) == N and orig["n_correct"] == 90

# ---- 1. real precision, recomputed from the original hand-check
real_c = [1 if r["verdict"] == "C" else 0 for r in orig_rows]
assert sum(real_c) == 90, sum(real_c)
real_prec = sum(real_c) / N
assert abs(real_prec - 0.90) < 1e-9
print(f"[1] real precision recomputed from original hand-check = {real_prec:.4f} (90/100)  OK")

# ---- 2. inheritance integrity: inherited rows carry the ORIGINAL verdict for that idx
orig_verdict_by_idx = {i: r["verdict"] for i, r in enumerate(orig_rows)}
orig_head_by_idx = {i: per_item[i]["real_head"] for i in range(N)}
n_inh = 0
for r in pop:
    if r.get("source") == "inherited_from_real_handcheck":
        assert r["head"] == orig_head_by_idx[r["idx"]], f"inherited row head!=real_head at {r['idx']}"
        assert r["verdict"] == orig_verdict_by_idx[r["idx"]], f"inherited row relabelled real verdict at {r['idx']}"
        n_inh += 1
assert n_inh > 0
print(f"[2] all {n_inh} inherited rows carry the ORIGINAL human C/W label (no silent relabel)  OK")

# ---- 3. per-arm recount matches metrics_scored.json
arms = list(scored["trivial_arms"].keys())
per_arm = {a: {"emit": 0, "correct": 0, "vec": [0] * N} for a in arms}
for r in pop:
    a = r["arm"]
    if r["emitted"]:
        per_arm[a]["emit"] += 1
        if r["verdict"] == "C":
            per_arm[a]["correct"] += 1
            per_arm[a]["vec"][r["idx"]] = 1
for a in arms:
    got_p = per_arm[a]["correct"] / per_arm[a]["emit"] if per_arm[a]["emit"] else 0.0
    exp_p = scored["trivial_arms"][a]["precision_over_emitted"]
    assert abs(round(got_p, 4) - exp_p) < 1e-4, f"{a}: recount {got_p} != metrics {exp_p}"
print(f"[3] all {len(arms)} arm precisions recomputed from the adjudicated population match metrics  OK")


def paired_diff_ci(a_vec, b_vec, n_boot=10000, seed=1234):
    rng = random.Random(seed)
    d = [a_vec[i] - b_vec[i] for i in range(N)]
    means = []
    for _ in range(n_boot):
        s = 0
        for _ in range(N):
            s += d[rng.randrange(N)]
        means.append(s / N)
    means.sort()
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot)]


# ---- 4. strongest genuinely-trivial floor is CI-separated below the real arm
strongest = scored["strongest_meaningful_floor"]["arm"]
lo, hi = paired_diff_ci(real_c, per_arm[strongest]["vec"])
assert lo > 0.0, f"strongest floor {strongest} NOT CI-separated: real-floor CI [{lo:.3f},{hi:.3f}]"
print(f"[4] real - strongest trivial floor ({strongest}) paired CI = [{lo:+.3f}, {hi:+.3f}] "
      f"excludes 0 -> 0.90 is not a pure selection artifact  OK")

# ---- 5. information-free twin (constant 'water') loses, CI-separated
lo2, hi2 = paired_diff_ci(real_c, per_arm["most_frequent_entity"]["vec"])
twin_p = per_arm["most_frequent_entity"]["correct"] / per_arm["most_frequent_entity"]["emit"]
assert twin_p < real_prec and lo2 > 0.0, "info-free twin did not lose CI-separated"
print(f"[5] info-free twin (constant 'water') P={twin_p:.4f} << real; real-twin CI [{lo2:+.3f},{hi2:+.3f}]  OK")

# ---- 6. BRAIN-FOUNDATIONAL dissociation: the margin lives in the non-canonical (passive) stratum.
# good-enough parsing predicts the positional heuristic ~ties the real arm on canonical actives and
# collapses on passives. Recompute per-voice, independently, from _per_item voice labels.
voice_of = {it["idx"]: it["voice"] for it in per_item}
for vc, expect_sep in (("active", False), ("passive", True)):
    idxs = [i for i in range(N) if voice_of[i] == vc]
    rc = [real_c[i] for i in idxs]
    fc = [per_arm["first_noun_after_verb"]["vec"][i] for i in idxs]
    # paired CI within the stratum
    rng = random.Random(7)
    d = [rc[j] - fc[j] for j in range(len(idxs))]
    means = []
    for _ in range(10000):
        s = sum(d[rng.randrange(len(d))] for _ in range(len(d)))
        means.append(s / len(d))
    means.sort()
    lo6, hi6 = means[250], means[9750]
    sep = lo6 > 0.0
    assert sep == expect_sep, f"{vc}: expected CI-separated={expect_sep}, got [{lo6:.3f},{hi6:.3f}]"
    print(f"[6] {vc:8s} n={len(idxs)} real-heuristic CI [{lo6:+.3f},{hi6:+.3f}] separated={sep} "
          f"(expected {expect_sep})  OK")
print("    -> the whole margin is in the non-canonical stratum: good-enough parsing signature")

# ---- context: report the diagnostic (not an assertion -- it is the honest qualifier)
diag = scored["filter_contribution_diagnostic"]
print(f"[i] filter-contribution diagnostic: voice_aware_adjacency P={diag['precision_over_emitted']} "
      f"(real - it CI {diag['real_minus_it_ci95']}, reproduces real entity on "
      f"{diag['reproduces_real_entity_on_n']}/100) -- most of the 0.90 is filters + a trivial voice rule")

print("\nALL WITNESS CHECKS PASS")
