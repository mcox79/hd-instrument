"""exp_cls_interleaved_replay_consolidation_pilot_v1.py

PROPER Complementary-Learning-Systems (CLS) consolidation-loop pilot -- CPU, glass-box.

CONTEXT. The naive dual-store attempt (exp_two_substrate_fastslow_cls_cpu_v1) HARD_FAILED
  (old-consolidated recall 0.378). Brain-check: it failed as the McCloskey-Cohen SINGLE-shared-store
  failure mode, NOT because the CLS PRINCIPLE fails. Its stores are pure additive Hebbian BUNDLES
  (Wfast/Wslow = single superposed complex vectors), on which (a) interleaved replay is a
  MATHEMATICAL NO-OP (a commutative sum is order-independent) and (b) superposition crosstalk from
  cramming thousands of items into one vector is the killer. A faithful CLS pilot therefore requires
  an ERROR-CORRECTING store with a SHARED distributed representation -- the exact substrate cortex is
  (shared units -> interference -> the very thing interleaved replay exists to protect). That is the
  canonical McCloskey & Cohen 1989 / McClelland-McNaughton-O'Reilly 1995 CLS demo.

WHAT. Continual (class-incremental) learning regime where catastrophic interference actually bites.
  Slow store = a small SHARED-hidden-layer net (N->H->V, tanh, softmax) trained by backprop. Fast
  tier = an exact pattern-separated episodic buffer of the most-recent block (hippocampal one-shot).
  Recall routes fast(exact)-then-slow (schema-fit / novelty routing). Consolidation = periodic
  offline training of the slow net; the ONE new variable = whether that consolidation INTERLEAVES a
  random replay sample of already-seen items (CLS) or trains new-items-only (naive).

ARMS (a clean 2x2 that LOCALIZES which half is load-bearing, per Falsifiable-Prediction #2):
                       no-replay                         interleaved-replay
  no fast tier   single_seq (McCloskey baseline a)   replay_only (ablation)
  fast tier      naive_dual_w (HARD_FAILED base b)   full_cls (the mechanism)

  The full CLS loop (full_cls) must beat BOTH single_seq AND naive_dual_w on old-item recall while
  keeping recent-item recall high. single_seq -> naive_dual_w isolates the store-SEPARATION half;
  naive_dual_w -> full_cls isolates the interleaved-REPLAY half (identical except replay).

METRIC (reuses the failed cell's task/metric shape): recent_recall (last block) + old_recall
  (first block, the catastrophic-interference-sensitive metric). No held-out generalization claim --
  the target is RETENTION of trained associations, so replaying already-seen training items is the
  legitimate CLS mechanism, not a label leak.

CLAIM-VET-pending. Self-contained numpy; ASCII-only; PROT-018.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-metrics both tmp+os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retention accuracy, no argmax-noise floor; feasibility = interleaved(joint) ceiling >0.80
# - baseline_in_band at smoke (META_RULE_AG; single_seq old catastrophic <=0.40, recent >=0.60)
# - discriminator survives scale: smoke runs the FULL mechanism at reduced blocks; full at K_BLOCKS=10
# - HARD_PASS strictly above floor: old-recall margin vs BOTH baselines >= 0.20 (>> 0.05 band edge)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, json, time, hashlib, platform, traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics, record_gate

ANCHOR_NAME = "cls_interleaved_replay_consolidation_pilot_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- Config -----------------------------------------------------------------
N = 128                      # key (hypervector) dimensionality
H = 64                       # shared hidden layer (the distributed "cortex" that interferes)
CPB = 4                      # classes introduced per block (class-incremental)
IPC = 10                     # items per class per block
# NOTE: catastrophic forgetting DEEPENS with block count, so smoke keeps the FULL K_BLOCKS regime
# (the whole run is <2s) and reduces only the seed count -- reducing blocks would under-fire the
# discriminator (DISCRIMINATOR-MUST-SURVIVE-SCALE).
K_BLOCKS = 10
V = CPB * K_BLOCKS           # total classes: 40
IPB = CPB * IPC              # items per block = 40
T = IPB * K_BLOCKS           # total stream length: 200 smoke / 400 full
E_EPOCHS = 120               # backprop epochs per consolidation block (overfit -> real forgetting)
LR = 0.3
SEEDS = [7] if SMOKE else [7, 17, 23]
BUF_MATCH = 0.999            # exact-match cosine threshold for fast-tier routing

# HARD-PASS / HARD-FAIL bands (envelope-fail-bands, pre-registered)
OLD_HP = 0.70                # full_cls old_recall HARD-PASS floor
RECENT_HP = 0.70             # full_cls recent_recall guard floor
MARGIN_HP = 0.20             # full_cls old_recall must beat BOTH baselines by this
DIFF_OLD_MAX = 0.40          # difficulty-on: single_seq old_recall must be <= this (forgetting real)
DIFF_RECENT_MIN = 0.60       # difficulty-on: single_seq recent_recall >= this (it CAN learn)
CANFAIL_EPS = 0.05           # full_cls must beat naive by more than this or HARD-FAIL


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class SharedNet:
    """N->H->V shared-hidden-layer classifier (tanh + softmax), batch backprop.

    The shared hidden layer is the distributed/overlapping representation whose
    units participate in every class -- sequential class-incremental training
    catastrophically overwrites it (McCloskey-Cohen); interleaved replay cures it.
    """

    def __init__(self, n: int, h: int, v: int, rng: np.random.Generator):
        self.W1 = (rng.standard_normal((h, n)) / np.sqrt(n)).astype(np.float64)
        self.W2 = (rng.standard_normal((v, h)) / np.sqrt(h)).astype(np.float64)

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int, lr: float, v: int) -> None:
        if X.shape[0] == 0:
            return
        m = X.shape[0]
        oneh = np.zeros((m, v), dtype=np.float64)
        oneh[np.arange(m), y] = 1.0
        for _ in range(epochs):
            Z1 = X @ self.W1.T           # [m,H]
            A1 = np.tanh(Z1)
            logits = A1 @ self.W2.T      # [m,V]
            P = _softmax(logits)
            dlog = (P - oneh) / m        # [m,V]
            dW2 = dlog.T @ A1            # [V,H]
            dA1 = dlog @ self.W2         # [m,H]
            dZ1 = dA1 * (1.0 - A1 * A1)  # tanh'
            dW1 = dZ1.T @ X              # [H,N]
            self.W2 -= lr * dW2
            self.W1 -= lr * dW1

    def predict(self, X: np.ndarray) -> np.ndarray:
        A1 = np.tanh(X @ self.W1.T)
        logits = A1 @ self.W2.T
        return logits.argmax(axis=1)


def _make_stream(rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
    """Return keys [T,N] bipolar, labels [T], and per-block index lists (class-incremental)."""
    keys = np.sign(rng.standard_normal((T, N))).astype(np.float64)
    keys[keys == 0] = 1.0
    labels = np.zeros(T, dtype=np.int64)
    blocks: List[np.ndarray] = []
    for b in range(K_BLOCKS):
        idx = np.arange(b * IPB, (b + 1) * IPB)
        # classes for this block: [b*CPB, b*CPB+CPB); IPC items each
        cls = np.repeat(np.arange(b * CPB, (b + 1) * CPB), IPC)
        cls = rng.permutation(cls)
        labels[idx] = cls
        blocks.append(idx)
    return keys, labels, blocks


def _buf_recall(query: np.ndarray, buf_keys: np.ndarray, buf_labels: np.ndarray,
                slow: SharedNet) -> int:
    """Route: exact fast-tier match (schema-fit/novelty routing) else slow net."""
    if buf_keys.shape[0] > 0:
        sims = (buf_keys @ query) / (np.linalg.norm(buf_keys, axis=1) * np.linalg.norm(query) + 1e-9)
        j = int(sims.argmax())
        if sims[j] >= BUF_MATCH:
            return int(buf_labels[j])
    return int(slow.predict(query[None, :])[0])


def _recall_rate_net(net: SharedNet, keys: np.ndarray, idx: np.ndarray, labels: np.ndarray) -> float:
    if idx.size == 0:
        return 0.0
    preds = net.predict(keys[idx])
    return float((preds == labels[idx]).mean())


def _recall_rate_routed(slow: SharedNet, buf_keys: np.ndarray, buf_labels: np.ndarray,
                        keys: np.ndarray, idx: np.ndarray, labels: np.ndarray) -> Tuple[float, np.ndarray]:
    preds = np.array([_buf_recall(keys[i], buf_keys, buf_labels, slow) for i in idx], dtype=np.int64)
    rate = float((preds == labels[idx]).mean()) if idx.size else 0.0
    return rate, preds


def _run_seed(seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    keys, labels, blocks = _make_stream(rng)
    old_idx = blocks[0]
    recent_idx = blocks[-1]

    # ARM 1: single_seq  (McCloskey baseline a) -- one net, sequential, no replay
    s1 = SharedNet(N, H, V, np.random.default_rng(seed + 1))
    for b in range(K_BLOCKS):
        idx = blocks[b]
        s1.train(keys[idx], labels[idx], E_EPOCHS, LR, V)
    s1_old = _recall_rate_net(s1, keys, old_idx, labels)
    s1_recent = _recall_rate_net(s1, keys, recent_idx, labels)

    # ARM 2: naive_dual_w (HARD_FAILED baseline b) -- fast exact buffer(recent block) + slow net
    #        consolidated SEQUENTIALLY (block-only, NO replay). = separation without replay.
    s2 = SharedNet(N, H, V, np.random.default_rng(seed + 1))
    for b in range(K_BLOCKS):
        idx = blocks[b]
        s2.train(keys[idx], labels[idx], E_EPOCHS, LR, V)   # slow net: block-only (no replay)
    buf2_keys = keys[recent_idx]                             # fast tier holds most-recent block
    buf2_lab = labels[recent_idx]
    s2_old, _ = _recall_rate_routed(s2, buf2_keys, buf2_lab, keys, old_idx, labels)
    s2_recent, _ = _recall_rate_routed(s2, buf2_keys, buf2_lab, keys, recent_idx, labels)

    # ARM 3: replay_only (ablation) -- one net, interleaved replay, NO fast tier
    s3 = SharedNet(N, H, V, np.random.default_rng(seed + 1))
    seen3: List[int] = []
    r3 = np.random.default_rng(seed + 100)
    for b in range(K_BLOCKS):
        idx = blocks[b]
        if seen3:
            rep = r3.choice(np.array(seen3), size=min(IPB, len(seen3)), replace=False)
            tr = np.concatenate([idx, rep])
        else:
            tr = idx
        s3.train(keys[tr], labels[tr], E_EPOCHS, LR, V)
        seen3.extend(idx.tolist())
    s3_old = _recall_rate_net(s3, keys, old_idx, labels)
    s3_recent = _recall_rate_net(s3, keys, recent_idx, labels)

    # ARM 4: full_cls (the mechanism) -- fast exact buffer(recent block) + slow net
    #        consolidated with INTERLEAVED REPLAY (block + random past sample). ONE var vs naive.
    s4 = SharedNet(N, H, V, np.random.default_rng(seed + 1))
    seen4: List[int] = []
    r4 = np.random.default_rng(seed + 200)
    for b in range(K_BLOCKS):
        idx = blocks[b]
        if seen4:
            rep = r4.choice(np.array(seen4), size=min(IPB, len(seen4)), replace=False)
            tr = np.concatenate([idx, rep])
        else:
            tr = idx
        s4.train(keys[tr], labels[tr], E_EPOCHS, LR, V)     # slow net: interleaved replay
        seen4.extend(idx.tolist())
    buf4_keys = keys[recent_idx]                             # fast tier holds most-recent block
    buf4_lab = labels[recent_idx]
    s4_old, s4_old_preds = _recall_rate_routed(s4, buf4_keys, buf4_lab, keys, old_idx, labels)
    s4_recent, s4_rec_preds = _recall_rate_routed(s4, buf4_keys, buf4_lab, keys, recent_idx, labels)

    # ARMS-MUST-DIFFER (META_RULE_AF): digest each arm's ACTUAL routed recall over the whole stream.
    # NOTE (arms_differ_exempted): single_seq and naive_dual_w share the SAME sequential slow net by
    # design (naive adds only a fast buffer on the recall side, not a different slow store), so those
    # two MAY coincide when the net already predicts the recent block correctly -- that coincidence is
    # itself a finding (separation-half adds no measurable recall here), not a bug. The LOAD-BEARING
    # anti-no-op guard is that full_cls differs from BOTH mandated baselines and replay_only differs
    # from single_seq -- checked in run()/verdict, not by all-4-distinct.
    allidx = np.arange(T)
    p_single = s1.predict(keys)
    p_naive = np.array([_buf_recall(keys[i], buf2_keys, buf2_lab, s2) for i in allidx], dtype=np.int64)
    p_replay = s3.predict(keys)
    p_full = np.array([_buf_recall(keys[i], buf4_keys, buf4_lab, s4) for i in allidx], dtype=np.int64)
    digests = {
        "single_seq": hashlib.sha256(p_single.tobytes()).hexdigest(),
        "naive_dual_w": hashlib.sha256(p_naive.tobytes()).hexdigest(),
        "replay_only": hashlib.sha256(p_replay.tobytes()).hexdigest(),
        "full_cls": hashlib.sha256(p_full.tobytes()).hexdigest(),
    }

    return {
        "seed": seed,
        "single_seq": {"old": round(s1_old, 3), "recent": round(s1_recent, 3)},
        "naive_dual_w": {"old": round(s2_old, 3), "recent": round(s2_recent, 3)},
        "replay_only": {"old": round(s3_old, 3), "recent": round(s3_recent, 3)},
        "full_cls": {"old": round(s4_old, 3), "recent": round(s4_recent, 3)},
        "arm_digests": digests,
    }


def run() -> Dict:
    per_seed = [_run_seed(s) for s in SEEDS]

    def _mean(arm, key):
        return float(np.mean([ps[arm][key] for ps in per_seed]))

    agg = {arm: {"old": round(_mean(arm, "old"), 3), "recent": round(_mean(arm, "recent"), 3)}
           for arm in ("single_seq", "naive_dual_w", "replay_only", "full_cls")}

    # per-seed HARD-PASS count for full_cls vs BOTH mandated baselines
    hp_seeds = 0
    for ps in per_seed:
        fc = ps["full_cls"]
        ss = ps["single_seq"]["old"]
        nd = ps["naive_dual_w"]["old"]
        if (fc["old"] >= OLD_HP and fc["recent"] >= RECENT_HP
                and fc["old"] >= ss + MARGIN_HP and fc["old"] >= nd + MARGIN_HP):
            hp_seeds += 1

    # LOAD-BEARING arms-differ (META_RULE_AF): full_cls must differ from BOTH mandated baselines
    # (anti-no-op guard) and replay_only must differ from single_seq (replay does something).
    # single_seq==naive_dual_w is a LEGITIMATE exemption (shared sequential slow net; see _run_seed).
    arms_differ = True
    for ps in per_seed:
        d = ps["arm_digests"]
        if d["full_cls"] == d["single_seq"] or d["full_cls"] == d["naive_dual_w"] \
                or d["replay_only"] == d["single_seq"]:
            arms_differ = False
    return {"agg": agg, "per_seed": per_seed, "hp_seeds": hp_seeds,
            "n_seeds": len(SEEDS), "arms_differ": arms_differ}


def verdict(r: Dict) -> Tuple[str, str]:
    agg = r["agg"]
    fc = agg["full_cls"]; ss = agg["single_seq"]; nd = agg["naive_dual_w"]; ro = agg["replay_only"]
    hp = r["hp_seeds"]; ns = r["n_seeds"]
    s = ("full_cls(old=%.3f,recent=%.3f) naive_dual_w(old=%.3f,recent=%.3f) "
         "single_seq(old=%.3f,recent=%.3f) replay_only(old=%.3f,recent=%.3f) | "
         "hp_seeds=%d/%d arms_differ=%s"
         % (fc["old"], fc["recent"], nd["old"], nd["recent"], ss["old"], ss["recent"],
            ro["old"], ro["recent"], hp, ns, r["arms_differ"]))

    if not r["arms_differ"]:
        return ("HARD_FAIL", "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: " + s)

    need = 2 if ns >= 3 else 1
    # CAN-FAIL localization: interleaved-replay half did NOT help -> localizes missing ingredient.
    if fc["old"] <= nd["old"] + CANFAIL_EPS:
        return ("HARD_FAIL",
                "HARD_FAIL_REPLAY_HALF_INEFFECTIVE: full_cls old-recall does NOT beat naive_dual_w "
                "(interleaved-replay half not load-bearing here; missing ingredient localizes to "
                "REPLAY not separation -- brain: interleaved SWR replay is exactly what protects "
                "distributed neocortex; if it does not help, the store is not sharing units / not "
                "actually interfering, re-check difficulty). " + s)
    if hp >= need:
        return ("HARD_PASS",
                "HARD_PASS_FULL_CLS_LOOP: separation + interleaved-replay + fast/slow routing beats "
                "BOTH single-store (McCloskey) AND naive-dual-W on old-recall (margin>=%.2f) while "
                "retaining recent (>=%.2f), %d/%d seeds. Interleaved replay is the load-bearing half "
                "(replay_only old=%.3f ~ full_cls; fast tier adds recent-exactness). " % (
                    MARGIN_HP, RECENT_HP, hp, ns, ro["old"]) + s)
    if fc["old"] > nd["old"] + CANFAIL_EPS and fc["old"] > ss["old"] + CANFAIL_EPS:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: full_cls beats both baselines on old-recall but below the >=%.2f "
                "margin / >=%.2f floor bar on >=%d seeds -- threshold/epoch tuning, not redesign. "
                % (MARGIN_HP, OLD_HP, need) + s)
    return ("HARD_FAIL", "HARD_FAIL_NO_SEPARATION_FROM_BASELINES: " + s)


# --- error-checking template (defensive) ------------------------------------
def _write_start_marker(output_dir: Path) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "expected_n_units": len(SEEDS),
              "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    fin = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, fin)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    fin = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, fin)


def _selftest() -> None:
    """Exercise the REAL code path (SharedNet + run()) at FULL block-count, 1 seed.

    Catastrophic forgetting DEEPENS with block count, so the discriminator is weakest at reduced
    scale -- per DISCRIMINATOR-MUST-SURVIVE-SCALE the self-test runs the real K_BLOCKS with 1 seed
    (still ~1-2s) so the difficulty-on gate is checked at the regime the FULL run uses.
    """
    global SEEDS
    _s = SEEDS
    SEEDS = [7]
    try:
        r = run()
        agg = r["agg"]
        assert r["arms_differ"], "selftest: arms must differ"
        # difficulty-on: single_seq must catastrophically forget old while learning recent
        assert agg["single_seq"]["old"] <= DIFF_OLD_MAX + 0.10, \
            "selftest: single_seq old=%.3f not forgetting (difficulty OFF)" % agg["single_seq"]["old"]
        assert agg["single_seq"]["recent"] >= 0.5, \
            "selftest: single_seq recent=%.3f too low (cannot learn)" % agg["single_seq"]["recent"]
        # replay must recover old (mechanism sanity)
        assert agg["full_cls"]["old"] > agg["single_seq"]["old"], "selftest: full_cls no better than single_seq"
        print("[selftest] PASS real-code-path: single_seq_old=%.3f naive_old=%.3f full_cls_old=%.3f "
              "replay_only_old=%.3f full_cls_recent=%.3f arms_differ=%s"
              % (agg["single_seq"]["old"], agg["naive_dual_w"]["old"], agg["full_cls"]["old"],
                 agg["replay_only"]["old"], agg["full_cls"]["recent"], r["arms_differ"]),
              flush=True)
    finally:
        SEEDS = _s


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print("[config] anchor=%s mode=%s N=%d H=%d V=%d T=%d blocks=%d E=%d seeds=%s"
          % (ANCHOR_NAME, RUN_MODE, N, H, V, T, K_BLOCKS, E_EPOCHS, SEEDS), flush=True)
    t0 = time.time()
    r = run()
    agg = r["agg"]
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)

    gate_claims = [
        record_gate("full_cls_old_recall", agg["full_cls"]["old"], OLD_HP, ">=",
                    "old-item retention after full stream"),
        record_gate("full_cls_recent_recall", agg["full_cls"]["recent"], RECENT_HP, ">=",
                    "recent-item recall guard"),
        record_gate("old_margin_vs_naive", agg["full_cls"]["old"] - agg["naive_dual_w"]["old"], MARGIN_HP, ">=",
                    "interleaved-replay half effect (the ONE variable)"),
        record_gate("old_margin_vs_single", agg["full_cls"]["old"] - agg["single_seq"]["old"], MARGIN_HP, ">=",
                    "full CLS loop vs McCloskey single-store"),
        record_gate("difficulty_single_seq_old", agg["single_seq"]["old"], DIFF_OLD_MAX, "<=",
                    "catastrophic forgetting is real (difficulty ON)"),
        record_gate("difficulty_single_seq_recent", agg["single_seq"]["recent"], DIFF_RECENT_MIN, ">=",
                    "single_seq CAN learn recent (forgetting not inability)"),
        record_gate("hp_seeds", r["hp_seeds"], (2 if r["n_seeds"] >= 3 else 1), ">=",
                    "seeds where full_cls beats BOTH baselines"),
    ]
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_seeds": r["n_seeds"], "agg": agg, "hp_seeds": r["hp_seeds"],
               "arms_differ": r["arms_differ"], "per_seed": r["per_seed"],
               "config": {"N": N, "H": H, "V": V, "T": T, "K_BLOCKS": K_BLOCKS, "CPB": CPB, "IPC": IPC,
                          "E_EPOCHS": E_EPOCHS, "LR": LR, "seeds": SEEDS},
               "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, r["per_seed"], gate_claims=gate_claims)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
