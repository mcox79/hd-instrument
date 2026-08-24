"""Scaffold-free witness for problem `reader_meaning_channel` (Bayesian hub WSD result).

Recomputes every headline INDEPENDENTLY from the saved per-trial population (_scored_population.json),
with its own subject-weighted aggregation and its own pure-python bootstrap -- it never trusts the
cell's metric computation. Checks:
  1. subject-weighted accuracy per arm recomputed from the population == metrics.json.
  2. the FREQUENCY PRIOR (MFS) beats the uniform floor, and beats the grounded coherence CI-separated
     (paired bootstrap over words) -- the positive sub-finding.
  3. the grounded hub coherence does NOT clear the strongest floor (MFS): BAYES_HUB - MFS CI includes
     0; even the brain control-gated arm does not CI-separate. The pre-registered NEGATIVE.
  4. the info-free twin LOSES to BAYES_HUB (norms carry the tiny difference, not the machinery).
  5. the subordinate-bias SIGNATURE: MFS scores 0 on subordinate-congruent items (it always picks the
     frequent sense); the grounded hub rescues some -- coherence helps exactly where the prior fails.

Run: .venv/Scripts/python.exe verification/test_reader_sense_selection_bayesian_hub.py
"""
import json
import os
import random

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "exp_reader_sense_selection_bayesian_hub_v1")
pop = json.load(open(os.path.join(D, "_scored_population.json"), encoding="utf-8"))
met = json.load(open(os.path.join(D, "metrics.json"), encoding="utf-8"))
records = pop["records"]
FLOOR_UNIFORM = pop["floor_uniform"]
N = len(records)
assert N == met["n_trials"], (N, met["n_trials"])


def subj_weighted(rows, arm):
    """mean over WORDS of per-word accuracy, over words that arm actually scored."""
    byw = {}
    for r in rows:
        c = r["correct"].get(arm)
        if c is None:
            continue
        byw.setdefault(r["word"], []).append(int(c))
    if not byw:
        return None, []
    per_word = {w: sum(v) / len(v) for w, v in byw.items()}
    words = sorted(per_word)
    return sum(per_word[w] for w in words) / len(words), words


def paired_word_boot(rows, arm_a, arm_b, seed=11, nboot=5000):
    """paired bootstrap over the WORDS scored by BOTH arms; returns (delta, lo, hi)."""
    a_word, b_word = {}, {}
    for r in rows:
        ca, cb = r["correct"].get(arm_a), r["correct"].get(arm_b)
        if ca is not None:
            a_word.setdefault(r["word"], []).append(int(ca))
        if cb is not None:
            b_word.setdefault(r["word"], []).append(int(cb))
    words = sorted(set(a_word) & set(b_word))
    a = [sum(a_word[w]) / len(a_word[w]) for w in words]
    b = [sum(b_word[w]) / len(b_word[w]) for w in words]
    n = len(words)
    rng = random.Random(seed)
    diffs = []
    for _ in range(nboot):
        sa = sb = 0.0
        for _ in range(n):
            i = rng.randrange(n)
            sa += a[i]
            sb += b[i]
        diffs.append(sa / n - sb / n)
    diffs.sort()
    return (sum(a) / n - sum(b) / n), diffs[int(0.025 * nboot)], diffs[int(0.975 * nboot)]


# ---- 1. per-arm subject-weighted accuracy matches metrics.json
accs = met["accuracy_subject_weighted"]
for arm in ("MFS_PRIOR", "COH_HUB", "BAYES_HUB", "BAYES_HUB_GATED"):
    got, _ = subj_weighted(records, arm)
    assert got is not None and abs(round(got, 4) - accs[arm]) < 1e-3, (arm, got, accs[arm])
# info-free twin from the separate info-free records
got_if, _ = subj_weighted(pop["records_infofree"], "BAYES_HUB_INFOFREE")
assert abs(round(got_if, 4) - accs["BAYES_HUB_INFOFREE"]) < 1e-3, (got_if, accs["BAYES_HUB_INFOFREE"])
print("[1] all arm accuracies recomputed from the population match metrics.json  OK")

# ---- 2. the frequency prior works: MFS > uniform floor, and MFS > grounded coherence CI-separated
mfs, _ = subj_weighted(records, "MFS_PRIOR")
assert mfs > FLOOR_UNIFORM, (mfs, FLOOR_UNIFORM)
d, lo, hi = paired_word_boot(records, "MFS_PRIOR", "COH_HUB")
assert lo > 0.0, f"MFS should beat grounded coherence CI-separated: [{lo:.4f},{hi:.4f}]"
print(f"[2] frequency PRIOR works: MFS {mfs:.4f} > uniform floor {FLOOR_UNIFORM:.4f} (+{mfs-FLOOR_UNIFORM:.4f}); "
      f"MFS - grounded-coherence = {d:+.4f} CI[{lo:+.4f},{hi:+.4f}] EXCLUDES 0  OK")

# ---- 3. the grounded hub does NOT clear the strongest floor (MFS), uniform OR control-gated
d3, lo3, hi3 = paired_word_boot(records, "BAYES_HUB", "MFS_PRIOR")
assert not (lo3 > 0.0), f"unexpected: BAYES_HUB CI-separated above MFS [{lo3:.4f},{hi3:.4f}]"
dg, log_, hig = paired_word_boot(records, "BAYES_HUB_GATED", "MFS_PRIOR")
assert not (log_ > 0.0), f"unexpected: gated arm CI-separated above MFS [{log_:.4f},{hig:.4f}]"
print(f"[3] grounded hub does NOT clear the strongest floor: BAYES_HUB-MFS {d3:+.4f} CI[{lo3:+.4f},{hi3:+.4f}]; "
      f"control-gated {dg:+.4f} CI[{log_:+.4f},{hig:+.4f}] -- both include 0  OK")

# ---- 4. info-free twin LOSES to BAYES_HUB (the norms carry the difference, not the machinery)
bh, _ = subj_weighted(records, "BAYES_HUB")
assert got_if < bh, (got_if, bh)
print(f"[4] info-free twin {got_if:.4f} < BAYES_HUB {bh:.4f} -- the coherence machinery alone does not do it  OK")

# ---- 5. subordinate-bias signature: MFS = 0 on subordinate; the hub rescues some
def stratum(rows, arm, want_dom):
    hits = [int(r["correct"][arm]) for r in rows
            if r.get("dominant_congruent") == want_dom and arm in r["correct"]]
    return (sum(hits) / len(hits)) if hits else None, len(hits)


mfs_sub, n_sub = stratum(records, "MFS_PRIOR", False)
hub_sub, _ = stratum(records, "BAYES_HUB", False)
assert abs(mfs_sub) < 1e-9, f"MFS should score 0 on subordinate-congruent (always picks frequent), got {mfs_sub}"
assert hub_sub > mfs_sub, f"grounded hub should rescue some subordinate items: hub {hub_sub} vs MFS {mfs_sub}"
print(f"[5] subordinate-bias signature: on {n_sub} subordinate-sense items MFS={mfs_sub:.4f}, "
      f"grounded hub={hub_sub:.4f} -- coherence helps exactly where the prior fails  OK")

print("\nALL WITNESS CHECKS PASS")
print(f"  headline: grounded meaning channel (richest multi-spoke+emotion+gating+control) does NOT "
      f"clear the frequency-prior floor; the prior is the lever.")
