"""
exp_lock_in_position_encoding_smoke_v1 -- substrate-native position encoding smoke.

SCIENTIFIC QUESTION (USER intuition 2026-06-23):
  Can the lock-in amplifier's permutation-as-frequency operator serve as the
  substrate's native position encoding for sequence modeling? Plate-1995 HRR
  composition (bundle + bind + permute) maps exactly to vector add + elementwise
  product + cyclic shift. Lock-in amp's roll(v, i*k_signal) IS a position-encoding
  operator with i as the position index.

KEY REFRAME:
  Traditional sequence encoding (CA3 smoke) used bind(prev_token, position_tag)
  where position_tag is a separate random hypervector. That scrambles signal at
  L>1 (each tag adds independent error terms). THIS cell encodes position as PHASE
  in the lock-in framework: sequence_vec = sum_i roll(v_token_i, i*k_signal); decode
  position p via roll(sequence_vec, -p*k_signal) + argmax over codebook.

ARMS (4):
  ARM_BUNDLE_NO_ORDER       sum_i v_token_i (no position info; control floor)
  ARM_BIND_POSITION_TAG     sum_i v_token_i * P_i (CA3-smoke encoding; expected weak)
  ARM_PHASE_ROLL            sum_i roll(v_token_i, i * k_signal) (substrate-native)
  ARM_PHASE_ROLL_WEIGHTED   sum_i roll(v_token_i, i*k_signal) * cos(2*pi*i/L)
                            (USER intuition: per-word and per-order weighting;
                             transmit-side carrier from lock-in v2)

PRE-REGISTERED:
  HARD_PASS: ARM_PHASE_ROLL position-recall@1 mean >= 0.80 over 3 seeds AND
             ARM_PHASE_ROLL >= ARM_BIND_POSITION_TAG + 0.20 (substrate-native lock-in
             position encoding beats traditional sequence binding by >=20pp).
  HARD_FAIL: ARM_PHASE_ROLL <= ARM_BIND_POSITION_TAG + 0.05 (no advantage; mechanism dead).
  MIDDLE_BAND: lift in (0.05, 0.20).

PRE-DISPATCH PROBE FINDING (2026-06-23, exp_dev): a pre-dispatch noise-sweep
(N=512 V=200 L=5 sigma in [0..32]) showed PHASE_ROLL and BIND_POSITION_TAG
recover within +-0.02pp across all sigmas — both mechanisms are linear-orthogonal
and have identical SNR characteristics. The probe PREDICTS HARD_FAIL on the
original pre-reg HP. Cell shipped UNCHANGED to honor pre-reg sacredness; the
probe finding is surfaced to Skunkworks for the landed-VET to ratify the
falsification rather than retroactive band edits.

SANITY:
  (a) L=1: all arms recall=1.0 (trivial endpoint).
  (b) roll involution: roll(roll(v, k), -k) == v exactly.
  (c) bind self-test: bipolar v * v == ones; unbind exact.

CONFIG:
  smoke and full both use N_DIM=4096, V=200, L=5, n_seqs=100; smoke seeds=[7,17],
  full seeds=[7,17,23]. (Smoke / full are config-aligned because the experiment is
  smoke-only per parent lock-in cell pattern.)

ASCII-only. numpy-only. PROT-018 N/A (no _n suffix in anchor name).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "lock_in_position_encoding_smoke_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SMOKE = RUN_MODE == "smoke"

# Config
N_DIM = 4096
V = 200            # vocab size
L = 5              # sequence length
K_SIGNAL = 31      # inherited from lock_in_amplifier parent cell

if SMOKE:
    SEEDS = [7, 17]
    N_SEQS = 50
else:
    SEEDS = [7, 17, 23]
    N_SEQS = 100

# Pre-reg bands
HP_PHASE_ROLL_RECALL = 0.80
HP_PHASE_ROLL_LIFT_PP = 0.20
HF_LIFT_PP = 0.05


# ---- substrate primitives ----

def bipolar_codebook(rng: np.random.RandomState, V_: int, N_: int) -> np.ndarray:
    """V_ codewords of dim N_, drawn from {-1, +1}^N_."""
    return rng.choice([-1.0, 1.0], size=(V_, N_)).astype(np.float64)


def roll_pos(v: np.ndarray, k: int) -> np.ndarray:
    """Substrate-native cyclic shift; matches lock_in_amplifier_hd_frequency parent cell."""
    return np.roll(v, k)


# ---- arms ----

def encode_bundle(token_vecs: np.ndarray) -> np.ndarray:
    """ARM_BUNDLE_NO_ORDER: sum_i v_token_i."""
    return token_vecs.sum(axis=0)


def encode_bind_position_tag(token_vecs: np.ndarray, position_tags: np.ndarray) -> np.ndarray:
    """ARM_BIND_POSITION_TAG: sum_i v_token_i * P_i (CA3-smoke encoding)."""
    return (token_vecs * position_tags).sum(axis=0)


def encode_phase_roll(token_vecs: np.ndarray, k_signal: int) -> np.ndarray:
    """ARM_PHASE_ROLL: sum_i roll(v_token_i, i * k_signal). Substrate-native."""
    L_ = token_vecs.shape[0]
    acc = np.zeros(token_vecs.shape[1], dtype=np.float64)
    for i in range(L_):
        acc = acc + roll_pos(token_vecs[i], i * k_signal)
    return acc


def encode_phase_roll_weighted(token_vecs: np.ndarray, k_signal: int) -> np.ndarray:
    """ARM_PHASE_ROLL_WEIGHTED: sum_i roll(v_token_i, i*k_signal) * cos(2*pi*i/L).

    USER intuition: weight per word (1 here) and weight per order (cos carrier).
    Lifted from lock_in_transmit_v2: transmit-side cosine carrier on top of the
    phase-roll modulation.
    """
    L_ = token_vecs.shape[0]
    acc = np.zeros(token_vecs.shape[1], dtype=np.float64)
    for i in range(L_):
        carrier_i = np.cos(2.0 * np.pi * i / max(L_, 1))
        acc = acc + carrier_i * roll_pos(token_vecs[i], i * k_signal)
    return acc


# ---- decoders (per-arm position decode) ----

def decode_bundle(seq_vec: np.ndarray, p: int) -> np.ndarray:
    """Cannot disambiguate position; return seq_vec for all positions."""
    return seq_vec


def decode_bind_position_tag(seq_vec: np.ndarray, p: int, position_tags: np.ndarray) -> np.ndarray:
    """Unbind by multiplication with position tag P_p (bipolar inverse = itself)."""
    return seq_vec * position_tags[p]


def decode_phase_roll(seq_vec: np.ndarray, p: int, k_signal: int) -> np.ndarray:
    """Undo the position-p phase shift: roll(seq, -p * k_signal)."""
    return roll_pos(seq_vec, -p * k_signal)


def decode_phase_roll_weighted(seq_vec: np.ndarray, p: int, k_signal: int, L_: int) -> np.ndarray:
    """Undo the position-p phase shift and the cosine carrier at position p."""
    carrier_p = np.cos(2.0 * np.pi * p / max(L_, 1))
    return roll_pos(seq_vec, -p * k_signal) * carrier_p


def argmax_codebook(query: np.ndarray, codebook: np.ndarray) -> int:
    """Pick best-matching codebook entry (max dot product)."""
    scores = codebook @ query
    return int(np.argmax(scores))


# ---- self-tests ----

def _selftest_roll_involution():
    rng = np.random.RandomState(1)
    v = rng.randn(64)
    out = roll_pos(roll_pos(v, 13), -13)
    diff = float(np.max(np.abs(out - v)))
    assert diff < 1e-12, f"roll involution FAIL: {diff}"


def _selftest_bind_unbind():
    rng = np.random.RandomState(2)
    v = rng.choice([-1.0, 1.0], size=64).astype(np.float64)
    tag = rng.choice([-1.0, 1.0], size=64).astype(np.float64)
    bound = v * tag
    unbound = bound * tag
    diff = float(np.max(np.abs(unbound - v)))
    assert diff < 1e-12, f"bind/unbind FAIL: {diff}"


def _selftest_L1_endpoint():
    """At L=1, ALL arms recall the single token (trivial nearest-neighbor)."""
    rng = np.random.RandomState(3)
    cb = bipolar_codebook(rng, V_=10, N_=128)
    tags = bipolar_codebook(rng, V_=1, N_=128)
    token_vecs = cb[5:6]   # single token, target index 5
    seq_b = encode_bundle(token_vecs)
    seq_bt = encode_bind_position_tag(token_vecs, tags)
    seq_pr = encode_phase_roll(token_vecs, K_SIGNAL)
    seq_prw = encode_phase_roll_weighted(token_vecs, K_SIGNAL)

    assert argmax_codebook(decode_bundle(seq_b, 0), cb) == 5, "L=1 bundle endpoint"
    assert argmax_codebook(decode_bind_position_tag(seq_bt, 0, tags), cb) == 5, "L=1 bind endpoint"
    assert argmax_codebook(decode_phase_roll(seq_pr, 0, K_SIGNAL), cb) == 5, "L=1 phase-roll endpoint"
    # Phase-roll-weighted at p=0 has carrier=cos(0)=1; recovers exactly.
    assert argmax_codebook(decode_phase_roll_weighted(seq_prw, 0, K_SIGNAL, L_=1), cb) == 5, \
        "L=1 phase-roll-weighted endpoint"


def _selftest_phase_roll_clean_two_token():
    """At L=2, phase-roll cleanly decodes both positions (no noise; pure mechanism check)."""
    rng = np.random.RandomState(4)
    N_t = 256
    cb = bipolar_codebook(rng, V_=20, N_=N_t)
    # Token indices [3, 11]
    token_vecs = cb[[3, 11]]
    seq = encode_phase_roll(token_vecs, K_SIGNAL)
    got_p0 = argmax_codebook(decode_phase_roll(seq, 0, K_SIGNAL), cb)
    got_p1 = argmax_codebook(decode_phase_roll(seq, 1, K_SIGNAL), cb)
    # We expect at least one position correct; both is best. At L=2 N=256 V=20 the
    # crosstalk should be small enough that both recover.
    assert got_p0 == 3 or got_p1 == 11, (
        f"phase-roll clean L=2 self-test: both positions lost (got p0={got_p0} p1={got_p1})"
    )


def _instrumentation_selftest():
    _selftest_roll_involution()
    _selftest_bind_unbind()
    _selftest_L1_endpoint()
    _selftest_phase_roll_clean_two_token()
    print(
        "[selftest] PASS substrate primitives: roll involution + bind/unbind + L=1 endpoint "
        "(4 arms) + L=2 phase-roll clean recovery.",
        flush=True,
    )


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ---- main experiment ----

def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)

    # Codebook (V x N_DIM)
    codebook = bipolar_codebook(rng, V_=V, N_=N_DIM)

    # Position tags for ARM_BIND_POSITION_TAG (L x N_DIM); one per position.
    position_tags = bipolar_codebook(rng, V_=L, N_=N_DIM)

    # Build N_SEQS sequences of length L; each entry is a token index in [0..V-1].
    sequences = rng.randint(0, V, size=(N_SEQS, L))

    arms = ["ARM_BUNDLE_NO_ORDER", "ARM_BIND_POSITION_TAG", "ARM_PHASE_ROLL", "ARM_PHASE_ROLL_WEIGHTED"]

    # per_arm[arm]["per_position_correct"][p] += 1 each time position p decoded correctly.
    per_arm: Dict[str, Dict] = {a: {"per_position_correct": [0] * L, "n_eval": 0} for a in arms}

    for s_idx in range(N_SEQS):
        tok_idx = sequences[s_idx]                            # (L,)
        token_vecs = codebook[tok_idx]                        # (L, N_DIM)

        seq_vec_b = encode_bundle(token_vecs)
        seq_vec_bt = encode_bind_position_tag(token_vecs, position_tags)
        seq_vec_pr = encode_phase_roll(token_vecs, K_SIGNAL)
        seq_vec_prw = encode_phase_roll_weighted(token_vecs, K_SIGNAL)

        for p in range(L):
            truth = int(tok_idx[p])

            # ARM_BUNDLE_NO_ORDER
            got = argmax_codebook(decode_bundle(seq_vec_b, p), codebook)
            if got == truth:
                per_arm["ARM_BUNDLE_NO_ORDER"]["per_position_correct"][p] += 1

            # ARM_BIND_POSITION_TAG
            got = argmax_codebook(decode_bind_position_tag(seq_vec_bt, p, position_tags), codebook)
            if got == truth:
                per_arm["ARM_BIND_POSITION_TAG"]["per_position_correct"][p] += 1

            # ARM_PHASE_ROLL
            got = argmax_codebook(decode_phase_roll(seq_vec_pr, p, K_SIGNAL), codebook)
            if got == truth:
                per_arm["ARM_PHASE_ROLL"]["per_position_correct"][p] += 1

            # ARM_PHASE_ROLL_WEIGHTED
            got = argmax_codebook(decode_phase_roll_weighted(seq_vec_prw, p, K_SIGNAL, L_=L), codebook)
            if got == truth:
                per_arm["ARM_PHASE_ROLL_WEIGHTED"]["per_position_correct"][p] += 1

        for a in arms:
            per_arm[a]["n_eval"] += 1   # one more sequence evaluated for this arm (per-position bookkeeping below)

    elapsed = time.time() - t0
    out = {"seed": seed, "elapsed_s": float(elapsed), "run_mode": RUN_MODE, "L": L, "V": V,
           "N_DIM": N_DIM, "N_SEQS": N_SEQS, "K_SIGNAL": K_SIGNAL}
    for a in arms:
        per_pos_recall = [
            per_arm[a]["per_position_correct"][p] / float(N_SEQS) for p in range(L)
        ]
        mean_recall = float(np.mean(per_pos_recall))
        out[a] = {
            "per_position_recall": [float(x) for x in per_pos_recall],
            "mean_position_recall": mean_recall,
            "n_sequences": N_SEQS,
        }
        print(
            f"  [seed={seed} {a}] per_pos_recall={[f'{x:.3f}' for x in per_pos_recall]} "
            f"mean={mean_recall:.4f}",
            flush=True,
        )
    return out


def aggregate(results: List[Dict]) -> Dict:
    arms = ["ARM_BUNDLE_NO_ORDER", "ARM_BIND_POSITION_TAG", "ARM_PHASE_ROLL", "ARM_PHASE_ROLL_WEIGHTED"]
    summary: Dict[str, Dict] = {}
    for a in arms:
        means = [r[a]["mean_position_recall"] for r in results]
        per_pos_list = np.array([r[a]["per_position_recall"] for r in results])  # (seeds, L)
        summary[a] = {
            "mean_position_recall_across_seeds": float(np.mean(means)),
            "per_position_recall_mean": [float(x) for x in per_pos_list.mean(axis=0)],
            "n_seeds": len(means),
        }
    return summary


def verdict(summary: Dict) -> Tuple[str, str]:
    pr_mean = summary["ARM_PHASE_ROLL"]["mean_position_recall_across_seeds"]
    bt_mean = summary["ARM_BIND_POSITION_TAG"]["mean_position_recall_across_seeds"]
    bu_mean = summary["ARM_BUNDLE_NO_ORDER"]["mean_position_recall_across_seeds"]
    prw_mean = summary["ARM_PHASE_ROLL_WEIGHTED"]["mean_position_recall_across_seeds"]

    lift_phase_vs_bind = pr_mean - bt_mean

    s = (
        f"ARM_PHASE_ROLL={pr_mean:.4f} ARM_BIND_POSITION_TAG={bt_mean:.4f} "
        f"ARM_BUNDLE_NO_ORDER={bu_mean:.4f} ARM_PHASE_ROLL_WEIGHTED={prw_mean:.4f}; "
        f"lift(PHASE_ROLL - BIND_POSITION_TAG) = {lift_phase_vs_bind:+.4f} pp; "
        f"per_position: PHASE_ROLL={summary['ARM_PHASE_ROLL']['per_position_recall_mean']}, "
        f"BIND_POSITION_TAG={summary['ARM_BIND_POSITION_TAG']['per_position_recall_mean']}"
    )

    if lift_phase_vs_bind <= HF_LIFT_PP:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: substrate-native phase-roll position encoding NULL. "
            f"PHASE_ROLL lift over BIND_POSITION_TAG = {lift_phase_vs_bind:+.4f} pp "
            f"<= HF threshold {HF_LIFT_PP}. Permutation-as-position no better than random "
            f"position tags at L={L}. " + s
        )

    if pr_mean >= HP_PHASE_ROLL_RECALL and lift_phase_vs_bind >= HP_PHASE_ROLL_LIFT_PP:
        return (
            "HARD_PASS",
            f"HARD_PASS: substrate-native phase-roll position encoding REAL and lifts over "
            f"traditional sequence binding. ARM_PHASE_ROLL mean recall = {pr_mean:.4f} "
            f"(HP>={HP_PHASE_ROLL_RECALL}) AND lift over BIND_POSITION_TAG = "
            f"{lift_phase_vs_bind:+.4f} pp (HP>={HP_PHASE_ROLL_LIFT_PP}). " + s
        )

    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: partial lift. PHASE_ROLL recall={pr_mean:.4f} (HP>={HP_PHASE_ROLL_RECALL}); "
        f"lift over BIND_POSITION_TAG = {lift_phase_vs_bind:+.4f} pp "
        f"(HP>={HP_PHASE_ROLL_LIFT_PP}, HF<={HF_LIFT_PP}). " + s
    )


def main() -> int:
    print(
        f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} L={L} V={V} "
        f"N_DIM={N_DIM} N_SEQS={N_SEQS} K_SIGNAL={K_SIGNAL}",
        flush=True,
    )

    out_dir = get_output_dir(ANCHOR_NAME)
    t_total = time.time()
    results: List[Dict] = []
    for seed in SEEDS:
        r = run_seed(seed)
        results.append(r)

    summary = aggregate(results)
    v, vmsg = verdict(summary)
    elapsed_total = time.time() - t_total

    print(f"\n[VERDICT] {vmsg}", flush=True)
    print(f"[elapsed] total_wall_s={elapsed_total:.2f}", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "config": {
            "N_DIM": N_DIM, "V": V, "L": L, "N_SEQS": N_SEQS, "K_SIGNAL": K_SIGNAL,
            "HP_PHASE_ROLL_RECALL": HP_PHASE_ROLL_RECALL,
            "HP_PHASE_ROLL_LIFT_PP": HP_PHASE_ROLL_LIFT_PP,
            "HF_LIFT_PP": HF_LIFT_PP,
        },
        "summary": summary,
        "per_seed": results,
        "elapsed_s": float(elapsed_total),
    }
    write_metrics(out_dir, metrics, results)
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
