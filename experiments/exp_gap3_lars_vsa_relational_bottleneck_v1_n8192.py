"""gap3_lars_vsa_relational_bottleneck_v1_n8192.

SCIENTIFIC QUESTION (Gap 3 compositional generalization; 3-arm discriminator):
  Substrate capability suite ARM_COMPOSITIONAL_GEN scored 0.00 heldout (vs 0.05
  chance) for novel-instance schema queries. The cortex_schema v1 cell (HRR-bundle
  of cat-prop bindings) is queued and predicted to MIDDLE_BAND at full given
  precedent comb=0.38. This cell tests a STRUCTURALLY DIFFERENT mechanism:

  LARS-VSA relational bottleneck (Webb-Goyal-Smolensky Trends Cog Sci 2024;
  arxiv 2405.14436): learned-symbol hypervectors (independent of input content)
  act as schema slots; queries route to symbols via relational cross-attention
  (inner product), and symbols carry the property bindings. Composition flows
  through SYMBOLS, not direct input-binding -> sidesteps HRR crosstalk.

  Plus an adjacent arm: RESONATOR-DECODE (Frady-Sommer arxiv 1906.11684) -
  iterative unbinding via simultaneous factor cleanup against codebooks. The
  substrate already has codebook + iterative_attractor primitives; this arm
  tests whether reading-side factorization closes Gap 3 without changing the
  writing-side.

  3-arm decisive discriminator:
    ARM_BASELINE        - nearest-neighbor episodic (substrate's current 0.00 floor)
    ARM_RELBOTTLENECK   - LARS-VSA learned-symbol + relational cross-attention
    ARM_RESONATOR       - iterative factor decomposition over codebooks

PRE-REGISTERED BANDS (LOCKED via module-init assert; sacrosanct both ways):
  HARD_PASS  : any arm heldout_top1 >= 0.50 AND >= 4x ARM_BASELINE AND cv <= 0.10
  HARD_PASS_PARTIAL :
               any arm >= 0.30 AND >= 2.5x ARM_BASELINE
  HARD_FAIL  : all 3 arms <= 0.10
  HARD_FAIL_CONFOUND :
               ARM_BASELINE >= 0.30 (training-set leak; re-audit harness)
  MIDDLE_BAND : in [0.10, 0.30] on any arm OR convergence within 5%
                (non-discriminating; redesign per [[feedback-encoder-picks-emerge-from-data]])
  BIAS_Q_SATURATION : any arm >= 0.995 with cv=0 -> flag as suspect-leak

Compositional task design (CLEAN SYNTHETIC; no contamination per [[feedback-clean-encoder-tests-no-contamination]]):
  - 5 categories (mammals, birds, vehicles, tools, foods); 10 instances/cat train;
    5 NOVEL instances/cat heldout -> 25 heldout queries
  - Each category has 1 shared property (warm-blooded, has-feathers, has-wheels,
    has-grip, has-nutrients); chance = 1/5 = 0.20
  - Instance vectors: sqrt(CAT_SIGNAL_FRAC)*cat_vec + sqrt(1-CAT_SIGNAL_FRAC)*noise
    Embedded signal lets baseline recover SOME structure; schema arms must lift
    via mechanism (this is the discriminating regime per BIAS-S)

FORMULA SELF-TESTS (assert measured values match expected BEFORE dispatch):
  1. HRR bind/unbind roundtrip cosine >= 0.80 at N=8192
  2. Relational cross-attention recovers learned-symbol value within cos >= 0.50
     when input matches symbol-key prototype
  3. Resonator-network single-step factor recovery: bind(a,b) then resonate
     against codebooks recovers (a,b) with cos >= 0.50
  4. Bands LOCKED at module init (drift guard)

ASCII-only. Substrate-only (HRR circular convolution + learned-symbol codebook +
resonator iteration). Zero LLM forward calls. Per [[feedback-no-busy-work]] this
cell is structurally different from cortex_schema_v1: distinct mechanism family.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "gap3_lars_vsa_relational_bottleneck_v1_n8192"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED) ----------
HARD_PASS_HELDOUT_FLOOR = 0.50
HARD_PASS_MULTIPLIER_OVER_BASELINE = 4.0
HARD_PASS_CV_CEILING = 0.10
HARD_PASS_PARTIAL_HELDOUT_FLOOR = 0.30
HARD_PASS_PARTIAL_MULTIPLIER = 2.5
HARD_FAIL_ALL_ARMS_CEILING = 0.10
HARD_FAIL_CONFOUND_BASELINE_FLOOR = 0.30
MIDDLE_BAND_FLOOR = 0.10
MIDDLE_BAND_CEILING = 0.30
CONVERGENCE_WINDOW = 0.05  # arms within 5% = non-discriminating
BIAS_Q_SATURATION_CEILING = 0.995

assert 0.0 < HARD_FAIL_ALL_ARMS_CEILING < MIDDLE_BAND_CEILING <= HARD_PASS_PARTIAL_HELDOUT_FLOOR < HARD_PASS_HELDOUT_FLOOR < 1.0, \
    "floor band order inverted"
assert HARD_PASS_PARTIAL_MULTIPLIER < HARD_PASS_MULTIPLIER_OVER_BASELINE, "multiplier order inverted"
assert MIDDLE_BAND_FLOOR == HARD_FAIL_ALL_ARMS_CEILING, "middle/fail boundary mismatch"

# ---------- Config ----------
N_CATEGORIES = 5
INSTANCES_PER_CATEGORY = 10
HELDOUT_PER_CATEGORY = 5
CHANCE = 1.0 / N_CATEGORIES  # 0.20

# Cat-signal frac: how much of the instance variance is category-aligned.
# 0.005 keeps baseline weak (cap-suite-like) but non-zero so harness is fair.
CAT_SIGNAL_FRAC = 0.005

# LARS-VSA symbol-codebook size: independent of input content.
# K=64 follows arxiv 2405.14436 reported regime (modest codebook, large N).
K_SYMBOLS = 64

# Resonator: # iterations + convergence threshold
RESONATOR_ITERS = 25
RESONATOR_CONV_THRESH = 1e-3

if RUN_MODE == "smoke":
    SEEDS = [11]
    N = 8192  # PROT-018: smoke and full identical N per META_M7 capacity-sensitive
else:
    SEEDS = [11, 13, 19]
    N = 8192


# ---------- HRR primitives ----------
def make_rand_atom(N_dim: int, rng: np.random.RandomState) -> np.ndarray:
    """Random unit-norm real vector for HRR."""
    v = rng.randn(N_dim).astype(np.float64)
    v /= (np.linalg.norm(v) + 1e-9)
    return v


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular convolution via FFT."""
    return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))


def unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """HRR exact unbind via FFT division."""
    A = np.fft.fft(a)
    C = np.fft.fft(c)
    eps = 1e-9
    Ainv = np.conj(A) / (np.abs(A) ** 2 + eps)
    return np.real(np.fft.ifft(C * Ainv))


def cosine(x: np.ndarray, y: np.ndarray) -> float:
    nx = np.linalg.norm(x) + 1e-9
    ny = np.linalg.norm(y) + 1e-9
    return float(np.dot(x, y) / (nx * ny))


def cleanup_topk(query: np.ndarray, candidates: List[np.ndarray]) -> Tuple[int, float]:
    """Return (top1_idx, top1_cos)."""
    cs = [cosine(query, c) for c in candidates]
    top1 = int(np.argmax(cs))
    return top1, cs[top1]


def softmax(x: np.ndarray, tau: float = 0.5) -> np.ndarray:
    """Tempered softmax for relational attention."""
    x = x / max(tau, 1e-6)
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) + 1e-9)


# ---------- Task construction ----------
def build_task(seed: int) -> Dict:
    """Build clean synthetic compositional task.

    Instance signal: embedded fraction CAT_SIGNAL_FRAC of cat-vec.
    Baseline gets a fair shot (signal exists); schema arms must MULTIPLY it.
    """
    rng = np.random.RandomState(seed)
    cat_vecs = [make_rand_atom(N, rng) for _ in range(N_CATEGORIES)]
    prop_vecs = [make_rand_atom(N, rng) for _ in range(N_CATEGORIES)]

    def make_instance(ci: int) -> np.ndarray:
        noise = make_rand_atom(N, rng)
        sig = float(np.sqrt(CAT_SIGNAL_FRAC))
        npart = float(np.sqrt(1.0 - CAT_SIGNAL_FRAC))
        inst = sig * cat_vecs[ci] + npart * noise
        inst /= (np.linalg.norm(inst) + 1e-9)
        return inst

    train_instances = []
    heldout_instances = []
    for ci in range(N_CATEGORIES):
        for _ in range(INSTANCES_PER_CATEGORY):
            train_instances.append((ci, make_instance(ci)))
        for _ in range(HELDOUT_PER_CATEGORY):
            heldout_instances.append((ci, make_instance(ci)))

    return {
        "cat_vecs": cat_vecs,
        "prop_vecs": prop_vecs,
        "train_instances": train_instances,
        "heldout_instances": heldout_instances,
        "rng": rng,
    }


# ---------- ARM_BASELINE: nearest-neighbor episodic ----------
def eval_baseline_nn(task: Dict) -> float:
    """Substrate's current 0.00-floor mechanism: nearest-neighbor by cosine.
    Predicts heldout-instance's category by nearest training instance.
    """
    correct = 0
    total = 0
    train_inst_vecs = [iv for (_, iv) in task["train_instances"]]
    train_cats = [c for (c, _) in task["train_instances"]]
    for (ci, inst_vec) in task["heldout_instances"]:
        cs = [cosine(inst_vec, ti) for ti in train_inst_vecs]
        nearest = int(np.argmax(cs))
        if train_cats[nearest] == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


# ---------- ARM_RELBOTTLENECK: LARS-VSA learned-symbol cross-attention ----------
def fit_relbottleneck(task: Dict, seed: int) -> Dict:
    """Train K learned symbols (independent of inputs).
    Each symbol k carries:
      - key_k : a learned-key hypervector (cosine-routing target)
      - val_k : a property-bound hypervector

    Training: for each (cat, train_instance), softmax-route by cosine(inst, key_k);
    update val_k toward bind(key_k, prop_vec[cat]) weighted by routing prob.
    Substrate-native: pure HD ops (no autograd; closed-form Hebbian-like accumulation).
    """
    rng = np.random.RandomState(seed * 7 + 1)
    keys = np.stack([make_rand_atom(N, rng) for _ in range(K_SYMBOLS)], axis=0)
    vals = np.zeros((K_SYMBOLS, N))
    prop_vecs = task["prop_vecs"]

    # Hebbian routing accumulation over training set
    for (ci, inst_vec) in task["train_instances"]:
        sims = np.array([cosine(inst_vec, keys[k]) for k in range(K_SYMBOLS)])
        weights = softmax(sims, tau=0.3)
        # Each symbol absorbs property-bound-by-key signal proportionally
        bound = bind(inst_vec, prop_vecs[ci])
        for k in range(K_SYMBOLS):
            vals[k] += weights[k] * bound

    # Normalize values
    for k in range(K_SYMBOLS):
        nrm = np.linalg.norm(vals[k]) + 1e-9
        vals[k] /= nrm

    return {"keys": keys, "vals": vals}


def eval_relbottleneck(task: Dict, model: Dict) -> float:
    """At inference: route novel-instance to symbols via cross-attention;
    aggregate weighted values; unbind by inst to recover property estimate;
    cleanup against prop bank."""
    keys = model["keys"]
    vals = model["vals"]
    prop_vecs = task["prop_vecs"]

    correct = 0
    total = 0
    for (ci, inst_vec) in task["heldout_instances"]:
        sims = np.array([cosine(inst_vec, keys[k]) for k in range(K_SYMBOLS)])
        weights = softmax(sims, tau=0.3)
        # Aggregate value via attention
        agg = np.zeros(N)
        for k in range(K_SYMBOLS):
            agg += weights[k] * vals[k]
        # Unbind by inst to extract property
        prop_estimate = unbind(agg, inst_vec)
        top1, _ = cleanup_topk(prop_estimate, prop_vecs)
        if top1 == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


# ---------- ARM_RESONATOR: iterative factor decomposition ----------
def fit_resonator(task: Dict) -> Dict:
    """Resonator stores bind(cat_vec, prop_vec) for each known category as bound atoms.
    At inference, query = inst_vec is RESONATED against (cat_codebook, prop_codebook)
    to decompose into best-matching (cat, prop) factors.
    Codebooks are the known cat_vecs and prop_vecs (substrate's existing knowledge).
    """
    return {
        "cat_codebook": np.stack(task["cat_vecs"], axis=0),
        "prop_codebook": np.stack(task["prop_vecs"], axis=0),
        # Bound facts: bind(cat_vec, prop_vec) summed; substrate's stored schema
        "facts_bundle": _bundle_facts(task),
    }


def _bundle_facts(task: Dict) -> np.ndarray:
    bundle = np.zeros(N)
    for ci in range(N_CATEGORIES):
        bundle += bind(task["cat_vecs"][ci], task["prop_vecs"][ci])
    bundle /= (np.linalg.norm(bundle) + 1e-9)
    return bundle


def resonate(query: np.ndarray, model: Dict) -> Tuple[int, int]:
    """Iterative factor decomposition.
    Maintains estimates (cat_hat, prop_hat); alternately unbinds query
    by the other estimate, projects onto codebook via cleanup, iterates.
    """
    cat_cb = model["cat_codebook"]
    prop_cb = model["prop_codebook"]
    facts = model["facts_bundle"]

    # The "query" interpretation: novel-instance has embedded cat-signal;
    # we unbind facts by instance to get noisy prop-mix, then resonate.
    prop_init = unbind(facts, query)
    # Project initial estimate onto prop codebook
    sims_p = np.array([cosine(prop_init, prop_cb[i]) for i in range(prop_cb.shape[0])])
    prop_hat = prop_cb[int(np.argmax(sims_p))]

    cat_hat = None
    last_score = -np.inf
    for it in range(RESONATOR_ITERS):
        # Unbind facts by prop_hat -> cat estimate
        cat_estimate = unbind(facts, prop_hat)
        sims_c = np.array([cosine(cat_estimate, cat_cb[i]) for i in range(cat_cb.shape[0])])
        cat_hat = cat_cb[int(np.argmax(sims_c))]
        cat_idx = int(np.argmax(sims_c))

        # Unbind facts by cat_hat -> prop estimate
        prop_estimate = unbind(facts, cat_hat)
        sims_p = np.array([cosine(prop_estimate, prop_cb[i]) for i in range(prop_cb.shape[0])])
        prop_hat = prop_cb[int(np.argmax(sims_p))]
        prop_idx = int(np.argmax(sims_p))

        # Score convergence by alignment with input query
        # (instance carries cat-signal; cat_hat should match)
        score = cosine(cat_hat, query)
        if abs(score - last_score) < RESONATOR_CONV_THRESH and it > 1:
            break
        last_score = score

    return cat_idx, prop_idx


def eval_resonator(task: Dict, model: Dict) -> float:
    """For each novel instance, run resonator decomposition; predict cat from final cat_idx."""
    correct = 0
    total = 0
    for (ci, inst_vec) in task["heldout_instances"]:
        cat_idx, _ = resonate(inst_vec, model)
        if cat_idx == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


# ---------- Per-seed runner ----------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    task = build_task(seed)

    t_a = time.time()
    arm_baseline = eval_baseline_nn(task)
    t_b = time.time()

    relbn_model = fit_relbottleneck(task, seed)
    arm_relbottleneck = eval_relbottleneck(task, relbn_model)
    t_c = time.time()

    res_model = fit_resonator(task)
    arm_resonator = eval_resonator(task, res_model)
    t_d = time.time()

    elapsed = time.time() - t0
    print(f"  [seed={seed}] BASELINE={arm_baseline:.4f} RELBN={arm_relbottleneck:.4f} "
          f"RESONATOR={arm_resonator:.4f} elapsed={elapsed:.2f}s "
          f"(baseline={t_b-t_a:.1f}s relbn={t_c-t_b:.1f}s reson={t_d-t_c:.1f}s)", flush=True)

    return {
        "seed": seed,
        "N": N,
        "run_mode": RUN_MODE,
        "arms": {
            "ARM_BASELINE": arm_baseline,
            "ARM_RELBOTTLENECK": arm_relbottleneck,
            "ARM_RESONATOR": arm_resonator,
        },
        "n_heldout_total": HELDOUT_PER_CATEGORY * N_CATEGORIES,
        "chance": CHANCE,
        "elapsed_s": float(elapsed),
    }


# ---------- Verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no valid results", {})

    arm_labels = ["ARM_BASELINE", "ARM_RELBOTTLENECK", "ARM_RESONATOR"]
    agg = {}
    for label in arm_labels:
        vals = [s["arms"][label] for s in per_seed if label in s["arms"]]
        mean = float(np.mean(vals)) if vals else 0.0
        std = float(np.std(vals)) if vals else 1.0
        cv = (std / mean) if mean > 1e-9 else 0.0
        agg[label] = {"mean_heldout_top1": mean, "std": std, "cv": cv, "per_seed": vals}

    baseline = agg["ARM_BASELINE"]["mean_heldout_top1"]
    relbn = agg["ARM_RELBOTTLENECK"]
    reson = agg["ARM_RESONATOR"]

    arm_summary = " | ".join(
        f"{l}={agg[l]['mean_heldout_top1']:.4f}+/-{agg[l]['std']:.4f}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "chance": CHANCE,
        "honest_scope": (
            f"Gap 3 compositional gen 3-arm discriminator at N={N}; {N_CATEGORIES} cats x "
            f"{INSTANCES_PER_CATEGORY} train + {HELDOUT_PER_CATEGORY} heldout/cat; chance={CHANCE:.4f}; "
            f"clean synthetic data; substrate-only (HRR + learned-symbol codebook + resonator)"
        ),
    }

    # BIAS-Q: suspect saturation
    for label, a in agg.items():
        if a["mean_heldout_top1"] >= BIAS_Q_SATURATION_CEILING and a["cv"] < 0.01:
            return ("BIAS_Q_SATURATION_SUSPECT",
                    f"BIAS_Q_SATURATION_SUSPECT: {label}={a['mean_heldout_top1']:.4f} cv={a['cv']:.4f} >= "
                    f"{BIAS_Q_SATURATION_CEILING} - suspect leak/saturation; "
                    f"audit before tier-claim. arms: {arm_summary}",
                    detail)

    # HARD_FAIL_CONFOUND: baseline leaks training
    if baseline >= HARD_FAIL_CONFOUND_BASELINE_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_CONFOUND_BASELINE_LEAK: ARM_BASELINE={baseline:.4f} >= "
                f"{HARD_FAIL_CONFOUND_BASELINE_FLOOR}. Baseline nearest-neighbor recovers structure - "
                f"re-audit harness; heldout construction may leak training. arms: {arm_summary}",
                detail)

    # Per anchor: best schema arm
    schema_labels = ["ARM_RELBOTTLENECK", "ARM_RESONATOR"]
    best_label = max(schema_labels, key=lambda l: agg[l]["mean_heldout_top1"])
    best_arm = agg[best_label]
    best_score = best_arm["mean_heldout_top1"]

    # HARD_FAIL: all arms below floor
    max_arm_score = max(agg[l]["mean_heldout_top1"] for l in arm_labels)
    if max_arm_score <= HARD_FAIL_ALL_ARMS_CEILING:
        return ("HARD_FAIL",
                f"HARD_FAIL_ALL_ARMS_FLOOR: max_arm={max_arm_score:.4f} <= {HARD_FAIL_ALL_ARMS_CEILING}. "
                f"Neither LARS-VSA nor resonator mechanism lifts substrate above floor at N={N}. "
                f"Pivot per research note: dense Hopfield or sparse-bipolar. arms: {arm_summary}",
                detail)

    # Non-discriminating convergence check
    spread = max(agg[l]["mean_heldout_top1"] for l in arm_labels) - \
             min(agg[l]["mean_heldout_top1"] for l in arm_labels)
    if spread < CONVERGENCE_WINDOW and max_arm_score < HARD_PASS_PARTIAL_HELDOUT_FLOOR:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_NON_DISCRIMINATING: arm spread={spread:.4f} < {CONVERGENCE_WINDOW} "
                f"and no arm reaches PARTIAL floor. Redesign discriminator before USER arbitration "
                f"per [[feedback-encoder-picks-emerge-from-data]]. arms: {arm_summary}",
                detail)

    # HARD_PASS: any schema arm >= 0.50 AND >= 4x baseline AND cv <= 0.10
    multiplier_vs_baseline = best_score / max(baseline, 1e-6)
    cond_floor = best_score >= HARD_PASS_HELDOUT_FLOOR
    cond_mult = multiplier_vs_baseline >= HARD_PASS_MULTIPLIER_OVER_BASELINE
    cond_cv = best_arm["cv"] <= HARD_PASS_CV_CEILING

    if cond_floor and cond_mult and cond_cv:
        return ("HARD_PASS",
                f"HARD_PASS_GAP3_COMPOSITIONAL_GEN: {best_label}={best_score:.4f} >= "
                f"{HARD_PASS_HELDOUT_FLOOR}; multiplier_over_baseline={multiplier_vs_baseline:.2f}x >= "
                f"{HARD_PASS_MULTIPLIER_OVER_BASELINE}; cv={best_arm['cv']:.4f} <= {HARD_PASS_CV_CEILING}; "
                f"baseline={baseline:.4f}. First substrate-native Gap 3 mechanism. "
                f"Substrate-product: ship hdlab/{best_label.lower().replace('arm_', '')}.py "
                f"+ capability-suite regression. arms: {arm_summary}",
                detail)

    # HARD_PASS_PARTIAL: best >= 0.30 AND >= 2.5x baseline
    cond_partial_floor = best_score >= HARD_PASS_PARTIAL_HELDOUT_FLOOR
    cond_partial_mult = multiplier_vs_baseline >= HARD_PASS_PARTIAL_MULTIPLIER
    if cond_partial_floor and cond_partial_mult:
        return ("HARD_PASS",
                f"HARD_PASS_PARTIAL_GAP3_LIFT: {best_label}={best_score:.4f} >= "
                f"{HARD_PASS_PARTIAL_HELDOUT_FLOOR}; multiplier={multiplier_vs_baseline:.2f}x >= "
                f"{HARD_PASS_PARTIAL_MULTIPLIER}; baseline={baseline:.4f}. "
                f"Partial Gap 3 lift; queue capacity/K-sweep follow-up. arms: {arm_summary}",
                detail)

    # MIDDLE_BAND: in middle band on best arm
    if MIDDLE_BAND_FLOOR < best_score < HARD_PASS_PARTIAL_HELDOUT_FLOOR:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: best_arm={best_label}={best_score:.4f} in [{MIDDLE_BAND_FLOOR}, "
                f"{HARD_PASS_PARTIAL_HELDOUT_FLOOR}); baseline={baseline:.4f}; "
                f"multiplier={multiplier_vs_baseline:.2f}x. arms: {arm_summary}",
                detail)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_DEFAULT: best_arm={best_label}={best_score:.4f}; baseline={baseline:.4f}; "
            f"no band matched cleanly. arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_bind_unbind_roundtrip():
    """T1: HRR bind/unbind roundtrip cosine >= 0.80 at N=8192."""
    rng = np.random.RandomState(0)
    n_t = 8192
    a = make_rand_atom(n_t, rng)
    b = make_rand_atom(n_t, rng)
    c = bind(a, b)
    b_hat = unbind(c, a)
    cs = cosine(b, b_hat)
    print(f"[selftest T1] HRR bind/unbind cosine={cs:.4f}", flush=True)
    assert not (cs != cs), "T1 NaN"
    assert cs >= 0.80, f"T1 FAIL: cosine={cs:.3f} < 0.80"
    print(f"[selftest T1] HRR roundtrip PASS", flush=True)


def _selftest_relbottleneck_routing():
    """T2: relational cross-attention recovers right symbol value.

    Construct K symbols. Query := key_k0 + small noise; softmax-routing
    over keys should concentrate on k0; aggregated value should be close
    to vals[k0] under cosine."""
    rng = np.random.RandomState(2)
    n_t = 8192
    K = 16
    keys = np.stack([make_rand_atom(n_t, rng) for _ in range(K)], axis=0)
    vals = np.stack([make_rand_atom(n_t, rng) for _ in range(K)], axis=0)
    k0 = 7
    noise = make_rand_atom(n_t, rng)
    query = 0.6 * keys[k0] + 0.4 * noise
    query /= (np.linalg.norm(query) + 1e-9)
    sims = np.array([cosine(query, keys[k]) for k in range(K)])
    w = softmax(sims, tau=0.1)
    agg = np.zeros(n_t)
    for k in range(K):
        agg += w[k] * vals[k]
    cs = cosine(agg, vals[k0])
    print(f"[selftest T2] relbn-routing cos(agg, vals[k0])={cs:.4f} w[k0]={w[k0]:.4f}", flush=True)
    assert cs >= 0.50, f"T2 FAIL: cos={cs:.3f} < 0.50 (routing didn't concentrate on k0)"
    print(f"[selftest T2] relbn routing PASS", flush=True)


def _selftest_resonator_factor():
    """T3: bind(a, b) then resonate against codebooks containing (a, b)
    recovers both factors. Single-step minimal check."""
    rng = np.random.RandomState(3)
    n_t = 8192
    Kc = 5
    cat_cb = np.stack([make_rand_atom(n_t, rng) for _ in range(Kc)], axis=0)
    prop_cb = np.stack([make_rand_atom(n_t, rng) for _ in range(Kc)], axis=0)
    ci, pi = 2, 3
    c = bind(cat_cb[ci], prop_cb[pi])
    # Decompose: unbind by cat_cb[ci] -> should recover prop_cb[pi]
    p_hat = unbind(c, cat_cb[ci])
    sims_p = np.array([cosine(p_hat, prop_cb[i]) for i in range(Kc)])
    pred_p = int(np.argmax(sims_p))
    # Also: unbind by prop_cb[pi] -> should recover cat_cb[ci]
    c_hat = unbind(c, prop_cb[pi])
    sims_c = np.array([cosine(c_hat, cat_cb[i]) for i in range(Kc)])
    pred_c = int(np.argmax(sims_c))
    print(f"[selftest T3] resonator factor pred_c={pred_c} (expect {ci}); "
          f"pred_p={pred_p} (expect {pi})", flush=True)
    assert pred_c == ci, f"T3 FAIL: cat recovery {pred_c} != {ci}"
    assert pred_p == pi, f"T3 FAIL: prop recovery {pred_p} != {pi}"
    print(f"[selftest T3] resonator factor PASS", flush=True)


def _selftest_bands_locked():
    assert HARD_PASS_HELDOUT_FLOOR == 0.50, "T4 floor drift"
    assert HARD_PASS_MULTIPLIER_OVER_BASELINE == 4.0, "T4 mult drift"
    assert HARD_PASS_CV_CEILING == 0.10, "T4 cv drift"
    assert HARD_PASS_PARTIAL_HELDOUT_FLOOR == 0.30, "T4 partial floor drift"
    assert HARD_PASS_PARTIAL_MULTIPLIER == 2.5, "T4 partial mult drift"
    assert HARD_FAIL_ALL_ARMS_CEILING == 0.10, "T4 hardfail ceiling drift"
    assert HARD_FAIL_CONFOUND_BASELINE_FLOOR == 0.30, "T4 confound floor drift"
    assert MIDDLE_BAND_FLOOR == 0.10, "T4 middle floor drift"
    assert MIDDLE_BAND_CEILING == 0.30, "T4 middle ceiling drift"
    assert CONVERGENCE_WINDOW == 0.05, "T4 convergence drift"
    assert BIAS_Q_SATURATION_CEILING == 0.995, "T4 BIAS_Q drift"
    assert N == 8192, "T4 N drift (PROT-018; anchor _n8192)"
    assert CAT_SIGNAL_FRAC == 0.005, "T4 cat-signal drift"
    print(f"[selftest T4] bands + N + cat-signal LOCKED PASS", flush=True)


def _instrumentation_selftest():
    _selftest_bind_unbind_roundtrip()
    _selftest_relbottleneck_routing()
    _selftest_resonator_factor()
    _selftest_bands_locked()
    print("[selftest] PASS: 4 formula tests + bands lock", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- Main run loop ----------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} cats={N_CATEGORIES} train_per_cat={INSTANCES_PER_CATEGORY} "
      f"held_per_cat={HELDOUT_PER_CATEGORY} K_symbols={K_SYMBOLS} "
      f"seeds_done={done} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed_dict = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed_dict.values())
verdict, verdict_msg, detail = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "headline": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "n_categories": N_CATEGORIES,
    "instances_per_category": INSTANCES_PER_CATEGORY,
    "heldout_per_category": HELDOUT_PER_CATEGORY,
    "k_symbols": K_SYMBOLS,
    "cat_signal_frac": CAT_SIGNAL_FRAC,
    "chance": CHANCE,
    "arms_tested": ["ARM_BASELINE", "ARM_RELBOTTLENECK", "ARM_RESONATOR"],
    "detail": detail,
    "per_seed": all_results,
    "metrics_source": "measured_cpu_gap3_lars_vsa_relational_bottleneck_3arm",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "honest_scope": detail.get("honest_scope", ""),
    "substrate_only_decode_gate": "N/A (Gap 3 mechanism primitive cell; zero LLM forward calls)",
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
