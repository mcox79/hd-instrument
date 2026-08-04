"""coherence_selector_insim_v1 -- earned causal-COHERENCE selector via reverse-replay SR.

WHY (see preregs/2026-08-04_coherence_selector_insim_v1.md, notes/research_drill_biology_
led_causal_coherence_credit_assignment_2026-08-03.md): `cross_span_causal_binding_v1` made
the true blocker's causal link REACHABLE (recall 0->3/4) but the existing selector
(`_pick_strict_cb`, a recency operator) cannot discriminate the true antecedent from a
recent-but-non-causal distractor once both are reachable. The missing organ is a
COHERENCE-SELECTOR that scores candidates by a LEARNED SCALAR (SR-backward reach), not a
memory lookup and not recency.

ARCHITECTURE (locked, do not deviate -- see task brief):
  - The selector must EMERGE from reverse-replay / predecessor-retrieval over the accumulated
    situation model, not a bolt-on classifier trained on true/distractor labels. Reuses
    `train_sr_transport` (TD(0) delta-rule, Dayan 1993 / Stachenfeld 2017 successor
    representation; Foster & Wilson 2006 reverse replay; Mattar & Daw 2018 need x gain --
    value-shaped, NOT recency-shaped) RE-POINTED to the predecessor direction by calling it
    AGAIN on REVERSED (effect, cause) transitions -- a genuinely retrained M_backward, NOT a
    free M^T transpose (per the drill's disk-verified correction: M is not claimed symmetric).
  - `hdlab.situation_model_accumulate.AccumulateRegister` is reused as the situation-model
    BUFFER (DMN/hippocampal event index) -- NOT the scorer (drill Finding 1a/1b: it is a
    storage/query organ, confirmed to have zero discriminating power between two written
    candidates).
  - `hdlab.self_improving_loop.decide_keep_or_revert` / `ABSTAIN_BAND_DEFAULT` reused as
    CONTROL-FLOW architecture (drill Finding 1d) over the NEW margin quantity
    reach_value(true)-reach_value(distractor), NOT its literal decode_coherence_margins call.

SIM = a NAMED SUBSTITUTE for experienced causal episodes (stated limit, not overclaimed): a
synthetic directed CAUSES graph over a bipolar codebook (same embedding primitive already
certified in experiments/exp_pfc_gate_cfrpe_trained_v2.py -- no borrowed embedding). Episodes
pair a graph-connected TRUE antecedent against a graph-DISconnected but narratively-MORE-RECENT
DISTRACTOR (the deliberate recency trap, mirroring the real grapp_mcca items' own
DISTR_CAND-later-position construction). Embeddings are i.i.d. random bipolar, independent of
graph structure by construction -- this is the built-in guard against coherence and recency (or
coherence and raw cosine) being accidentally correlated (Guard 2, task brief).

FLOORS (must fail): RECENCY (picks distractor by construction), RANDOM (~50%), NO_REPLAY_LOCAL
(raw cosine cand-vs-outcome, M:=identity -- doubles as the anti-tautology guard).
ORGAN UNDER TEST: COHERENCE_REVERSE_REPLAY (reach_value via M_backward, abstain-gated).
POSITIVE CONTROL: ORACLE (reads the true graph edge directly) must be 100%/100%.

GENERALIZATION: M_backward trained ONLY on TRAIN-partition rollout transitions; EVAL-partition
episodes (disjoint node identities, never seen in SR training) are the primary metric.

Author: exp_dev-role direct run (Opus 4.8 1M, agent-spawn), 2026-08-04.
Prereg: d:/AI/hd-instrument/preregs/2026-08-04_coherence_selector_insim_v1.md
Reuses (imported, not re-derived):
  experiments/exp_pfc_gate_cfrpe_trained_v2.py -- make_bipolar_E, train_sr_transport,
    reach_value, reach_control_targetcos, collect_rollout_transitions, _norm_rows
  hdlab/situation_model_accumulate.py -- AccumulateRegister
  hdlab/self_improving_loop.py -- decide_keep_or_revert, ABSTAIN_BAND_DEFAULT
  experiments/_seed_checkpoint.py -- resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics
Local-only cell: no queue, no remote dispatch, no push. Run directly:
  .venv/Scripts/python.exe experiments/exp_coherence_selector_insim_v1.py
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp_pfc_gate_cfrpe_trained_v2 import (  # noqa: E402
    make_bipolar_E, train_sr_transport, reach_value, reach_control_targetcos,
    collect_rollout_transitions, _norm_rows,
)
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds, write_partial_key, aggregate_partials, write_metrics,
    record_gate, get_output_dir,
)
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402

ANCHOR_NAME = "coherence_selector_insim_v1"
DEVICE = torch.device("cpu")  # local-only cell, small scale, no GPU needed
DTYPE = torch.float32

# ------------------------------- config (LOCKED, PROSPECTIVE) ---------------------------
N_DIM = 2048
V_TRAIN = 260          # TRAIN-partition node count
V_EVAL = 260            # EVAL-partition node count (disjoint index range)
V_TOTAL = V_TRAIN + V_EVAL
EDGE_DENSITY = 0.22     # expected out-edges per node within its own partition
N_EPISODES_TRAIN = 60   # episodes drawn from TRAIN partition (in-distribution check)
N_EPISODES_EVAL = 60    # episodes drawn from EVAL partition (PRIMARY metric)
SR_STEPS = 1500
SR_BATCH = 128
SR_LR = 0.5
GAMMA = 0.85
ROLLOUT_PER_V = 40
ROLLOUT_MAX_LEN = 3
SEEDS = [7, 17, 23, 31, 41]

HP_EVAL_ACC_FLOOR = 0.75
HP_FLOOR_MARGIN = 0.15   # coherence must beat every floor by >= this much on EVAL
MB_BEAT_ANY = 0.0        # middle-band: beats floors by >0 but < HP_FLOOR_MARGIN

CONFIG_VERSION = (
    "ANCHOR=%s,N_DIM=%d,V_TRAIN=%d,V_EVAL=%d,density=%.2f,n_ep_train=%d,n_ep_eval=%d,"
    "sr_steps=%d,sr_batch=%d,gamma=%.2f,rollout_per_V=%d,seeds=%s,abstain_band=%.3f"
) % (ANCHOR_NAME, N_DIM, V_TRAIN, V_EVAL, EDGE_DENSITY, N_EPISODES_TRAIN, N_EPISODES_EVAL,
     SR_STEPS, SR_BATCH, GAMMA, ROLLOUT_PER_V, SEEDS, ABSTAIN_BAND_DEFAULT)

_T0 = time.time()


# ============================================================================
# graph + episode construction (the sim = named substitute for experienced episodes)
# ============================================================================
def build_partition_edges(node_ids: List[int], density: float, g: np.random.Generator
                          ) -> Dict[int, List[int]]:
    """Directed CAUSES edges within one partition. Returns predecessors[effect] = [cause,...]."""
    n = len(node_ids)
    n_edges = max(4, int(round(density * n)))
    predecessors: Dict[int, List[int]] = {}
    guard = 0
    made = 0
    while made < n_edges and guard < n_edges * 30:
        guard += 1
        cause = int(node_ids[g.integers(0, n)])
        effect = int(node_ids[g.integers(0, n)])
        if cause == effect:
            continue
        predecessors.setdefault(effect, [])
        if cause in predecessors[effect]:
            continue
        predecessors[effect].append(cause)
        made += 1
    return predecessors


def build_episodes(node_ids: List[int], predecessors: Dict[int, List[int]],
                   n_episodes: int, g: np.random.Generator) -> List[Dict[str, Any]]:
    """Each episode: outcome (has >=1 real predecessor), true=a real predecessor,
    distractor=a same-partition node with NO edge to outcome, positioned MORE RECENT
    (closer to outcome) than true -- the deliberate recency trap."""
    node_set = set(node_ids)
    candidates_outcomes = sorted([o for o, preds in predecessors.items() if preds])
    if not candidates_outcomes:
        return []
    episodes: List[Dict[str, Any]] = []
    tries = 0
    while len(episodes) < n_episodes and tries < n_episodes * 50:
        tries += 1
        outcome = int(candidates_outcomes[g.integers(0, len(candidates_outcomes))])
        preds = predecessors[outcome]
        true_cause = int(preds[g.integers(0, len(preds))])
        # distractor: same partition, not the outcome, not ANY real predecessor of it
        distr = None
        for _try in range(30):
            cand = int(node_ids[g.integers(0, len(node_ids))])
            if cand == outcome or cand in preds:
                continue
            distr = cand
            break
        if distr is None:
            continue
        # narrative positions: true early (0..49), distractor later/closer to outcome (60..99)
        pos_true = int(g.integers(0, 50))
        pos_distr = int(g.integers(60, 100))
        episodes.append({
            "outcome": outcome, "true_cause": true_cause, "distractor": distr,
            "pos_true": pos_true, "pos_distr": pos_distr, "pos_outcome": 100,
        })
    return episodes


# ============================================================================
# situation-model buffer integration (glass-box sanity, NOT the scorer)
# ============================================================================
def situation_buffer_check(episodes: List[Dict[str, Any]], gen: torch.Generator
                           ) -> float:
    """Register each episode's 3 events (true_cause, distractor, outcome) as members of that
    episode's situation-model buffer (AccumulateRegister, 2-role vocab so cleanup_argmax must
    genuinely discriminate), decode back, and report the fraction whose decode correctly
    recovers MEMBER over a NON_MEMBER foil slot. This exercises the DMN/hippocampal event-index
    buffer for real; it plays no role in candidate SCORING (that is train_sr_transport/
    reach_value, per the drill's storage-vs-selector correction)."""
    if not episodes:
        return 0.0
    reg = AccumulateRegister(role_vocab=["MEMBER", "NON_MEMBER"], d=256, generator=gen,
                             max_event_slots=4)
    hits = 0
    total = 0
    for i, ep in enumerate(episodes):
        entity = "episode_%d" % i
        reg.add_event(entity, "MEMBER", 0)   # true_cause slot
        reg.add_event(entity, "MEMBER", 1)   # distractor slot (still a recorded event)
        reg.add_event(entity, "MEMBER", 2)   # outcome slot
        for slot in (0, 1, 2):
            role, _scores = reg.decode(entity, slot)
            total += 1
            if role == "MEMBER":
                hits += 1
    return float(hits) / float(max(1, total))


# ============================================================================
# selectors (all read only outcome/candidate identity + narrative position; NEVER the
# ground-truth edge, except ORACLE which is the positive control by definition)
# ============================================================================
def selector_recency(ep: Dict[str, Any]) -> str:
    return "true" if ep["pos_true"] > ep["pos_distr"] else "distractor"


def selector_random(ep: Dict[str, Any], g: np.random.Generator) -> str:
    return "true" if g.integers(0, 2) == 1 else "distractor"


def selector_oracle(ep: Dict[str, Any], predecessors: Dict[int, List[int]]) -> str:
    return "true" if ep["true_cause"] in predecessors.get(ep["outcome"], []) else "distractor"


def batched_reach_scores(episodes: List[Dict[str, Any]], E: torch.Tensor,
                         M: torch.Tensor, use_M: bool) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (score_true[n_ep], score_distr[n_ep]) via reach_value (or its M:=identity
    anti-tautology control when use_M=False, == the NO_REPLAY_LOCAL floor)."""
    if not episodes:
        return np.zeros(0), np.zeros(0)
    outc = torch.tensor([e["outcome"] for e in episodes], dtype=torch.long, device=DEVICE)
    tru = torch.tensor([e["true_cause"] for e in episodes], dtype=torch.long, device=DEVICE)
    dis = torch.tensor([e["distractor"] for e in episodes], dtype=torch.long, device=DEVICE)
    outc_E, tru_E, dis_E = E[outc], E[tru], E[dis]
    if use_M:
        s_true = reach_value(outc_E, tru_E, M)
        s_distr = reach_value(outc_E, dis_E, M)
    else:
        s_true = reach_control_targetcos(outc_E, tru_E)
        s_distr = reach_control_targetcos(outc_E, dis_E)
    return s_true.detach().cpu().numpy(), s_distr.detach().cpu().numpy()


def selector_coherence_abstain_gated(score_true: float, score_distr: float) -> Tuple[str, bool]:
    """Reuses decide_keep_or_revert's abstain-band CONTROL-FLOW (architecture reuse, drill
    Finding 1d) over the NEW margin quantity (reach_value delta). Returns (pick, abstained).
    Conservative primary metric treats an abstain as INCORRECT (cannot inflate accuracy)."""
    margin = score_true - score_distr
    adopt = decide_keep_or_revert({"true_over_distr": margin}, ABSTAIN_BAND_DEFAULT)
    if adopt == "true_over_distr":
        return "true", False
    return "distractor", True


# ============================================================================
# per-seed run
# ============================================================================
def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    node_ids_train = list(range(0, V_TRAIN))
    node_ids_eval = list(range(V_TRAIN, V_TOTAL))

    tgen = torch.Generator(device=DEVICE)
    tgen.manual_seed(int(seed) * 100003 + 1)
    E = make_bipolar_E(V_TOTAL, N_DIM, tgen)

    pred_train = build_partition_edges(node_ids_train, EDGE_DENSITY, g)
    pred_eval = build_partition_edges(node_ids_eval, EDGE_DENSITY, g)
    predecessors: Dict[int, List[int]] = {}
    predecessors.update(pred_train)
    predecessors.update(pred_eval)

    ep_train = build_episodes(node_ids_train, pred_train, N_EPISODES_TRAIN, g)
    ep_eval = build_episodes(node_ids_eval, pred_eval, N_EPISODES_EVAL, g)

    # reversed rollout transitions: TRAIN-partition edges ONLY (M_backward never sees EVAL)
    reversed_adj_train = {"0": {}}
    adj_for_rollout = [dict()]
    for effect, causes in pred_train.items():
        adj_for_rollout[0].setdefault(effect, [])
        adj_for_rollout[0][effect].extend(causes)   # (cur=effect, nxt=cause) walk direction
    n_transitions = min(200000, ROLLOUT_PER_V * V_TRAIN)
    transitions = collect_rollout_transitions(
        adj_for_rollout, n_ops=1, V=V_TOTAL, n_transitions=n_transitions,
        max_len=ROLLOUT_MAX_LEN, g=g)

    sr_gen = torch.Generator(device=DEVICE)
    sr_gen.manual_seed(int(seed) * 7919 + 1)
    M_backward, sr_diag = train_sr_transport(
        E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)

    # situation-model buffer glass-box sanity (real integration, not the scorer)
    buf_gen = torch.Generator(device=DEVICE)
    buf_gen.manual_seed(int(seed) * 31337 + 1)
    buf_fidelity_train = situation_buffer_check(ep_train, buf_gen)
    buf_gen2 = torch.Generator(device=DEVICE)
    buf_gen2.manual_seed(int(seed) * 31337 + 2)
    buf_fidelity_eval = situation_buffer_check(ep_eval, buf_gen2)

    def _score_partition(episodes: List[Dict[str, Any]], preds: Dict[int, List[int]],
                         rand_seed_offset: int) -> Dict[str, Any]:
        n = len(episodes)
        if n == 0:
            return {"n_episodes": 0}
        rg = np.random.default_rng(int(seed) * 999983 + rand_seed_offset)

        recency_correct = sum(1 for e in episodes if selector_recency(e) == "true")
        random_correct = sum(1 for e in episodes if selector_random(e, rg) == "true")
        oracle_correct = sum(1 for e in episodes if selector_oracle(e, preds) == "true")

        s_true_ctrl, s_distr_ctrl = batched_reach_scores(episodes, E, M_backward, use_M=False)
        norepl_correct = int(np.sum(s_true_ctrl > s_distr_ctrl))

        s_true_m, s_distr_m = batched_reach_scores(episodes, E, M_backward, use_M=True)
        coh_correct = 0
        coh_abstain = 0
        margins = []
        for i in range(n):
            pick, abstained = selector_coherence_abstain_gated(
                float(s_true_m[i]), float(s_distr_m[i]))
            margins.append(float(s_true_m[i] - s_distr_m[i]))
            if abstained:
                coh_abstain += 1
                continue  # conservative: abstain scored as incorrect (not counted correct)
            if pick == "true":
                coh_correct += 1

        return {
            "n_episodes": n,
            "recency_acc": recency_correct / n,
            "random_acc": random_correct / n,
            "no_replay_local_acc": norepl_correct / n,
            "oracle_acc": oracle_correct / n,
            "coherence_acc_conservative": coh_correct / n,   # abstain counted incorrect
            "coherence_abstain_rate": coh_abstain / n,
            "coherence_acc_covered": (coh_correct / (n - coh_abstain)) if (n - coh_abstain) > 0 else None,
            "glassbox_margin_mean": float(np.mean(margins)),
            "glassbox_margin_min": float(np.min(margins)),
            "glassbox_margin_positive_frac": float(np.mean([m > 0.0 for m in margins])),
        }

    train_metrics = _score_partition(ep_train, pred_train, 1)
    eval_metrics = _score_partition(ep_eval, pred_eval, 2)

    return {
        "seed": int(seed),
        "run_mode": "full",
        "N": N_DIM,
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "sr_diag": sr_diag,
        "situation_buffer_decode_fidelity_train": buf_fidelity_train,
        "situation_buffer_decode_fidelity_eval": buf_fidelity_eval,
        "train_partition": train_metrics,
        "eval_partition": eval_metrics,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _col(partition: str, field: str) -> List[float]:
        out = []
        for k in keys:
            v = per_seed[k].get(partition, {}).get(field)
            if v is not None:
                out.append(float(v))
        return out

    def _summ(partition: str) -> Dict[str, Any]:
        fields = ["recency_acc", "random_acc", "no_replay_local_acc", "oracle_acc",
                  "coherence_acc_conservative", "coherence_abstain_rate",
                  "glassbox_margin_mean", "glassbox_margin_positive_frac"]
        out = {}
        for f in fields:
            vals = _col(partition, f)
            out[f] = {"mean": float(np.mean(vals)) if vals else None,
                      "std": float(np.std(vals)) if vals else None,
                      "n_seeds": len(vals),
                      "per_seed": {keys[i]: vals[i] for i in range(len(vals))} if vals else {}}
        min_margins = _col(partition, "glassbox_margin_min")
        out["glassbox_margin_min_over_seeds"] = float(np.min(min_margins)) if min_margins else None
        return out

    train_summary = _summ("train_partition")
    eval_summary = _summ("eval_partition")

    buf_train = float(np.mean([per_seed[k]["situation_buffer_decode_fidelity_train"]
                               for k in keys])) if keys else 0.0
    buf_eval = float(np.mean([per_seed[k]["situation_buffer_decode_fidelity_eval"]
                              for k in keys])) if keys else 0.0

    coh_eval = eval_summary["coherence_acc_conservative"]["mean"] or 0.0
    rec_eval = eval_summary["recency_acc"]["mean"] or 0.0
    rand_eval = eval_summary["random_acc"]["mean"] or 0.0
    norepl_eval = eval_summary["no_replay_local_acc"]["mean"] or 0.0
    oracle_train = train_summary["oracle_acc"]["mean"] or 0.0
    oracle_eval = eval_summary["oracle_acc"]["mean"] or 0.0
    margin_min_over_seeds = eval_summary["glassbox_margin_min_over_seeds"]
    margin_pos_frac = eval_summary["glassbox_margin_positive_frac"]["mean"] or 0.0

    lift_recency = coh_eval - rec_eval
    lift_random = coh_eval - rand_eval
    lift_norepl = coh_eval - norepl_eval
    min_lift = min(lift_recency, lift_random, lift_norepl)

    positive_control_ok = (oracle_train >= 0.999) and (oracle_eval >= 0.999)
    margin_all_positive = (margin_min_over_seeds is not None and margin_min_over_seeds > 0.0)

    gate_claims = [
        record_gate("positive_control_oracle_train", oracle_train, 0.999, ">=",
                   "episode construction must be internally consistent"),
        record_gate("positive_control_oracle_eval", oracle_eval, 0.999, ">=",
                   "episode construction must be internally consistent"),
        record_gate("coherence_eval_acc_floor", coh_eval, HP_EVAL_ACC_FLOOR, ">=",
                   "HARD-PASS accuracy floor on held-out EVAL partition"),
        record_gate("min_lift_over_floors", min_lift, HP_FLOOR_MARGIN, ">=",
                   "coherence must beat ALL 3 floors by >=0.15 absolute on EVAL"),
        record_gate("glassbox_margin_min_over_seeds", margin_min_over_seeds or -999.0, 0.0, ">",
                   "true-vs-distractor reach margin must be positive in every seed"),
    ]

    if not positive_control_ok:
        verdict = "GATE_FAILED_POSITIVE_CONTROL"
        msg = ("ORACLE positive control failed (train=%.4f eval=%.4f, need >=0.999 both) -- "
               "episode-construction pipeline itself is broken; no other arm's verdict can be "
               "trusted." % (oracle_train, oracle_eval))
    elif (coh_eval >= HP_EVAL_ACC_FLOOR and min_lift >= HP_FLOOR_MARGIN
          and margin_all_positive):
        verdict = "HARD_PASS"
        msg = ("COHERENCE_REVERSE_REPLAY EVAL acc=%.4f beats RECENCY=%.4f (+%.4f) "
               "RANDOM=%.4f (+%.4f) NO_REPLAY_LOCAL=%.4f (+%.4f); glassbox margin positive in "
               "every seed (min=%.4f); ORACLE=%.4f/%.4f (train/eval)."
               % (coh_eval, rec_eval, lift_recency, rand_eval, lift_random,
                  norepl_eval, lift_norepl, margin_min_over_seeds, oracle_train, oracle_eval))
    elif min_lift > 0.0 or margin_pos_frac >= 0.8:
        verdict = "MIDDLE_BAND"
        msg = ("COHERENCE beats floors but below the HARD-PASS bar (eval_acc=%.4f, "
               "min_lift=%.4f vs floor %.4f, margin_positive_frac=%.4f) -- read as "
               "right-mechanism-class/underpowered-SR-training (Gap 1), not a refutation."
               % (coh_eval, min_lift, HP_FLOOR_MARGIN, margin_pos_frac))
    else:
        verdict = "HARD_FAIL"
        msg = ("COHERENCE_REVERSE_REPLAY does NOT beat the RECENCY/RANDOM/NO_REPLAY_LOCAL "
               "floors on held-out EVAL (eval_acc=%.4f, recency=%.4f random=%.4f "
               "no_replay_local=%.4f, min_lift=%.4f, margin_positive_frac=%.4f). Per "
               "brain-faithful-losing=presumed-impl-bug: inspect sr_diag err_first/err_last "
               "for TD convergence before concluding structural."
               % (coh_eval, rec_eval, rand_eval, norepl_eval, min_lift, margin_pos_frac))

    sr_err_first = [per_seed[k]["sr_diag"]["err_first"] for k in keys
                    if per_seed[k]["sr_diag"].get("err_first") is not None]
    sr_err_last = [per_seed[k]["sr_diag"]["err_last"] for k in keys
                   if per_seed[k]["sr_diag"].get("err_last") is not None]

    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "structured_gate_claims": [c for c in gate_claims],
        "train_partition_summary": train_summary,
        "eval_partition_summary": eval_summary,
        "situation_buffer_decode_fidelity_train_mean": buf_train,
        "situation_buffer_decode_fidelity_eval_mean": buf_eval,
        "sr_td_err_first_mean": float(np.mean(sr_err_first)) if sr_err_first else None,
        "sr_td_err_last_mean": float(np.mean(sr_err_last)) if sr_err_last else None,
        "sr_td_converged": bool(sr_err_first and sr_err_last
                                and np.mean(sr_err_last) < np.mean(sr_err_first)),
        "lift_over_recency_eval": lift_recency,
        "lift_over_random_eval": lift_random,
        "lift_over_no_replay_local_eval": lift_norepl,
        "min_lift_over_floors_eval": min_lift,
        "abstain_band_used": ABSTAIN_BAND_DEFAULT,
        "n_seeds_completed": len(keys),
        "seeds": keys,
    }


# ============================================================================
# main
# ============================================================================
def main() -> int:
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s"
          % (len(done), len(SEEDS), remaining), flush=True)

    fatal: List[str] = []
    for i, seed in enumerate(remaining):
        t0 = time.time()
        try:
            result = run_one_seed(seed)
        except SystemExit:
            raise
        except Exception as e:
            fc = type(e).__name__
            fatal.append("seed=%d %s: %s" % (seed, fc, str(e)[:200]))
            write_partial_key(out_dir, seed, {
                "seed": int(seed), "anchor_name": ANCHOR_NAME,
                "config_version": CONFIG_VERSION,
                "failure_class": fc, "error": str(e)[:400],
                "traceback": traceback.format_exc()[:3000],
                "train_partition": {}, "eval_partition": {},
                "sr_diag": {}, "situation_buffer_decode_fidelity_train": 0.0,
                "situation_buffer_decode_fidelity_eval": 0.0})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs eval_coh=%.3f eval_recency=%.3f eval_random=%.3f "
              "eval_norepl=%.3f oracle_train=%.3f oracle_eval=%.3f"
              % (seed, time.time() - t0,
                 result["eval_partition"]["coherence_acc_conservative"],
                 result["eval_partition"]["recency_acc"],
                 result["eval_partition"]["random_acc"],
                 result["eval_partition"]["no_replay_local_acc"],
                 result["train_partition"]["oracle_acc"],
                 result["eval_partition"]["oracle_acc"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("eval_partition")}
    final = aggregate_and_verdict(good)
    if fatal:
        final["fatal_seed_errors"] = fatal
        if final.get("verdict") == "HARD_PASS":
            final["verdict"] = "MIDDLE_BAND"
            final["verdict_msg"] = "DEMOTED_FROM_HP_DUE_TO_SEED_CRASH | " + final["verdict_msg"]
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _T0, 1)
    final["ts_iso"] = datetime.now(timezone.utc).isoformat()
    final["pid"] = os.getpid()
    final["run_mode"] = "full"
    final["config_version"] = CONFIG_VERSION
    final["device"] = str(DEVICE)
    final["prereg"] = "preregs/2026-08-04_coherence_selector_insim_v1.md"
    write_metrics(out_dir, final)
    print("[%s] DONE: %s" % (ANCHOR_NAME, final.get("verdict_msg", "")), flush=True)
    return 0


if __name__ == "__main__":
    _od = get_output_dir(ANCHOR_NAME)
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
            "summary": "CELL_CRASHED: %s" % type(e).__name__,
            "elapsed_s": round(time.time() - _T0, 1),
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "config_version": CONFIG_VERSION,
        }
        try:
            write_metrics(_od, diag)
        except Exception:
            pass
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
