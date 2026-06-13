"""
exp_substrate_aaa1_bayesian_tier_overlay_cpu_v1.py -- CELL-AAA-1: does a BAYESIAN posterior over tier beat HARD tier-labels? -- CPU/local (no heat, read-only).

ROUTING: Research ALTERNATIVES-DRILL VERDICT (notes/..._ALTERNATIVES_DRILL_VERDICT_3_axis_SURVIVES_audit...) Reservation A (HIGHEST
  priority) + the 7th USER-LOCKED rule ("reconsider-as-we-go; don't lock into a framework"). The 3-axis architecture SURVIVED the audit
  against 10 alternatives, but 3 ADDITIVE-HYBRID reservations were flagged for empirical verification. Reservation A: maybe epistemic tier
  (Axis 1) should not be a HARD label (T1/T2/T3) but a BAYESIAN POSTERIOR over tier (uncertainty-aware), per PR-OWL / BayesOWL / Bayesian-
  knowledge-driven ontologies. AAA-1 tests this CHEAPLY + ungated: predict an atom's tier from its STRUCTURAL features with (a) a HARD model
  (feature-cell majority vote, no uncertainty) vs (b) a BAYESIAN model (naive-Bayes posterior, Laplace-smoothed). Same features both ways;
  the ONLY difference is hard-assignment vs probabilistic-posterior. NO LLM; counting + 5-fold CV; numpy for arrays; no heat. READ-ONLY.

  Features (structural, all computable): in-degree bin, DEPENDS_ON out-degree bin, content-type (system/record/episodic), n-capabilities
  bin, corpus-class. Target: tier in {T1,T2,T3} (the atoms with genuine epistemic tiers; exclude NA/lexicon/etc for a clean 3-class task).

PRE-REGISTERED (Research CELL-AAA-1 bands): HARD-PASS Bayesian posterior accuracy >= hard-label accuracy + 0.03 (3pp) -> a Bayesian tier
  OVERLAY is worth integrating (additive, ~150 LOC, no ladder rewrite). HARD-FAIL Bayesian WORSE than hard (< hard accuracy) -> overlay
  hurts; keep hard labels. MIDDLE in between (0 to +3pp -> marginal; overlay optional). UNKNOWN if too few tiered atoms.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json, math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_aaa1_bayesian_tier_overlay_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FOLDS = 5; SEED = 1028; PROSE_CHARS = 700
TARGET_TIERS = {"T1", "T2", "T3"}
_NOTE_PAT = re.compile(r"(20\d\d|_to_|drill|handoff|\bnote\b|report|verdict|status)", re.I)


def _short(aid):
    return str(aid).split("::")[-1].split("/")[-1].strip().lower()


def _bin_indeg(d): return "i0" if d == 0 else ("i1_3" if d <= 3 else ("i4_10" if d <= 10 else "i11+"))
def _bin_out(d): return "o0" if d == 0 else ("o1_2" if d <= 2 else "o3+")
def _bin_caps(n): return "c0" if n == 0 else ("c1" if n == 1 else "c2+")


def naive_bayes_fit(train):
    """train: list of (features_dict, tier). Return (prior, cond) with Laplace smoothing."""
    prior = Counter(); feat_count = defaultdict(lambda: defaultdict(Counter)); feat_vals = defaultdict(set)
    for feats, tier in train:
        prior[tier] += 1
        for k, v in feats.items():
            feat_count[k][tier][v] += 1; feat_vals[k].add(v)
    return prior, feat_count, feat_vals


def nb_predict(feats, prior, feat_count, feat_vals):
    best, best_lp = None, -1e18
    total = sum(prior.values())
    for tier in prior:
        lp = math.log(prior[tier] / total)
        for k, v in feats.items():
            cnt = feat_count[k][tier]; denom = sum(cnt.values()) + len(feat_vals[k])
            lp += math.log((cnt.get(v, 0) + 1) / denom)             # Laplace
        if lp > best_lp: best_lp, best = lp, tier
    return best


def hard_predict(feats, train_by_cell, global_major):
    """HARD: majority tier among training atoms sharing the EXACT feature-cell; back off to global majority (no smoothing/uncertainty)."""
    key = tuple(sorted(feats.items()))
    c = train_by_cell.get(key)
    if c:
        return c.most_common(1)[0][0]
    return global_major


def cross_val(data, n_folds, seed):
    import random
    rng = random.Random(seed); idx = list(range(len(data))); rng.shuffle(idx)
    folds = [idx[i::n_folds] for i in range(n_folds)]
    nb_correct = hard_correct = total = 0
    for fi in range(n_folds):
        test_ids = set(folds[fi]); train = [data[i] for i in idx if i not in test_ids]; test = [data[i] for i in folds[fi]]
        if not train or not test: continue
        prior, fc, fv = naive_bayes_fit(train)
        cells = defaultdict(Counter); gm = Counter()
        for feats, tier in train:
            cells[tuple(sorted(feats.items()))][tier] += 1; gm[tier] += 1
        global_major = gm.most_common(1)[0][0]
        for feats, tier in test:
            total += 1
            if nb_predict(feats, prior, fc, fv) == tier: nb_correct += 1
            if hard_predict(feats, cells, global_major) == tier: hard_correct += 1
    return (nb_correct / max(1, total)), (hard_correct / max(1, total)), total


def _selftest():
    # synthetic: tier perfectly determined by indeg bin; NB should recover it; hard too on seen cells
    data = []
    for _ in range(20): data.append(({"ind": "i11+", "ct": "system"}, "T1"))
    for _ in range(20): data.append(({"ind": "i1_3", "ct": "system"}, "T3"))
    nb, hard, tot = cross_val(data, 5, 1)
    assert nb > 0.8 and hard > 0.8 and tot == 40, (nb, hard, tot)
    # NB handles an UNSEEN cell better than hard's global-major backoff
    p, fc, fv = naive_bayes_fit(data)
    assert nb_predict({"ind": "i11+", "ct": "record"}, p, fc, fv) == "T1"   # indeg dominates -> T1 despite unseen ct
    print("[selftest] PASS: substrate_aaa1_bayesian_tier_overlay_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    indeg = Counter(); outdeg = Counter()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() == "DEPENDS_ON":
                indeg[_short(r.get("tgt_id", ""))] += 1; outdeg[_short(r.get("src_id", ""))] += 1

    def alg(a):
        x = getattr(a, "algebra", None); return x if isinstance(x, dict) else {}

    def content_type(c, name, desc):
        rec = 0
        if "history" in c: rec += 1
        if len(desc or "") > PROSE_CHARS: rec += 1
        if _NOTE_PAT.search(name or ""): rec += 1
        if (desc or "").lstrip().startswith("#"): rec += 1
        return ("episodic" if "history" in c else "record") if rec >= 2 else "system"
    data = []
    for a in atoms:
        tier = str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "")
        if tier not in TARGET_TIERS: continue
        sid = _short(a.id); c = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
        ncap = len(getattr(a, "serves_capability", ()) or ())
        feats = {"ind": _bin_indeg(indeg[sid]), "out": _bin_out(outdeg[sid]),
                 "ct": content_type(c, getattr(a, "name", "") or "", getattr(a, "description", "") or ""),
                 "caps": _bin_caps(ncap), "dom": "dom" if alg(a).get("domain") else "nodom"}
        data.append((feats, tier))
    if len(data) < 30:
        return {"error": "too_few_tiered_atoms", "n": len(data)}
    base = Counter(t for _, t in data); majority_frac = base.most_common(1)[0][1] / len(data)
    nb_acc, hard_acc, total = cross_val(data, N_FOLDS if RUN_MODE != "smoke" else 3, SEED)
    delta = round(nb_acc - hard_acc, 4)
    print("  tiered atoms=%d (tier mix=%s) majority-baseline=%.3f" % (len(data), dict(base), majority_frac), flush=True)
    print("  %d-fold CV tier-prediction: BAYESIAN(naive-Bayes posterior)=%.4f vs HARD(cell-majority)=%.4f -> delta=%+.4f" % (
        N_FOLDS, nb_acc, hard_acc, delta), flush=True)
    return {"n_atoms": len(data), "tier_mix": dict(base), "majority_baseline": round(majority_frac, 4),
            "bayesian_acc": round(nb_acc, 4), "hard_acc": round(hard_acc, 4), "delta": delta, "n_eval": total}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n", "")))
    d = r["delta"]; nb = r["bayesian_acc"]; hd = r["hard_acc"]
    s = ("%d tiered atoms (mix %s, majority-baseline %.3f); 5-fold tier-prediction BAYESIAN=%.4f vs HARD=%.4f delta=%+.4f. "
         "(same structural features both models; only hard-cell-majority vs naive-Bayes-posterior differs.)") % (
        r["n_atoms"], r["tier_mix"], r["majority_baseline"], nb, hd, d)
    if d >= 0.03:
        return ("HARD_PASS", "HARD_PASS (Reservation A SUPPORTED): a Bayesian posterior over tier beats hard labels by %+.4f (>=+3pp) -- worth integrating as an ADDITIVE overlay (uncertainty-aware tier; no ladder rewrite). The discrete tier ladder benefits from a probabilistic overlay. " % d + s)
    if d <= -0.0001:
        return ("HARD_FAIL", "HARD_FAIL (Reservation A REFUTED): Bayesian posterior is WORSE than hard labels (delta %+.4f) -- the overlay hurts; KEEP hard tier labels. Per 7th rule, this honestly closes Reservation A as not-worth-integrating at the current corpus. " % d + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: Bayesian overlay marginal (delta %+.4f in (0,+3pp)) -- no decisive benefit; overlay OPTIONAL, hard labels adequate. " % d + s)


print("[config] anchor=%s mode=%s folds=%d" % (ANCHOR_NAME, RUN_MODE, N_FOLDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
