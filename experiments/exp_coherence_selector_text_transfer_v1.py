"""coherence_selector_text_transfer_v1 -- does the SIM-EARNED coherence SELECTOR transfer to REAL TEXT?

THE LOAD-BEARING QUESTION (program inflection): exp_coherence_selector_novel_types_v3.py earned an
abstract structural coherence rule -- pick the candidate whose EFFECT matches the OUTCOME -- that
generalizes to NOVEL sim types at coherence_acc=0.8733 (MEASURED@ data/exp_coherence_selector_
novel_types_v3/metrics.json, seeds [7,17,23,31,41]). EVERYTHING there is in-sim. This cell is the
FIRST end-to-end-on-real-text test of that causal-selection machinery.

THE SELECTOR (brain structure): a hippocampal/entorhinal SUCCESSOR-REPRESENTATION backward-transport
map M_backward (learned via TD(0)/SR delta-rule train_sr_transport) that, from an OUTCOME state,
reaches back to its predecessor CAUSE -- reverse-replay / relational antecedent retrieval. Coherence
= reach_value(outcome, cand, M) = cos(outcome @ M_backward, cand). In sim, M_backward learned the
INVERSE of a fixed coordinate-axis permutation T that defines the chain geometry.

THE BRIDGE (the crux): to feed real text we must produce, for the OUTCOME and each candidate EVENT,
2048-dim vectors that M_backward's reach_value can score. We encode span text with a SUBSTRATE-NATIVE
VSA/HDC content encoder (CharTrigramEncoder, Kanerva bag-of-trigrams) standing in for lexical/
perceptual cortex -- NOT a borrowed embedding / LLM / parser (glass-box invariant). M_backward is
REUSED BIT-IDENTICAL (reconstructed per seed via novel_types_v3's exact deterministic procedure; NEVER
retrained on text).

HONEST CAN-FAIL (either outcome valuable; n=7 is TINY -- directional feasibility, not powered):
  BRIDGES              -> sim-earned selector transfers to real text (a milestone; VET hard).
  CANNOT_BRIDGE_REPRESENTATION_GAP -> M_backward intact on sim (SIM_SANITY>=0.80) but ~chance on
                          text: M_backward's learned geometry (inverse of the sim's fixed permutation
                          T) has NO path to text content -> the sim-to-text REPRESENTATION bridge is
                          the gap. Routes: re-ground the selector on a text-compatible representation.
  PARTIAL              -> selector in the middle band, OR the text-native RAW-MATCH rule (no learned
                          map) beats baselines while the learned-map selector does not (rule transfers,
                          map does not).

Reuses (bit-identical import, not re-derived):
  experiments/exp_coherence_selector_novel_types_v3.py -- build_perm_transform, build_type_base_vectors,
    build_chain_trajectories, ChainPartition, collect_rollout_transitions, train_sr_transport,
    reach_value, reach_control_targetcos, _arm, and ALL config (N_DIM, SEEDS, SR hyperparams).
  hdlab/char_trigram_encoder.py -- CharTrigramEncoder (substrate-native text->HD, zero external model).

Author: exp_dev-role direct run (agent-spawn), 2026-08-04.
Prereg: preregs/2026-08-04_coherence_selector_text_transfer_v1.md
Local-only cell: no queue, no remote dispatch, no push. Run directly:
  .venv/Scripts/python.exe experiments/exp_coherence_selector_text_transfer_v1.py
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
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

# ---- REUSED, UNCHANGED: the sim-earned selector's own code path (bit-identical M_backward) ----
import experiments.exp_coherence_selector_novel_types_v3 as sel  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402

ANCHOR_NAME = "coherence_selector_text_transfer_v1"
DEVICE = torch.device("cpu")
DTYPE = torch.float32
N_DIM = sel.N_DIM  # 2048 -- MUST match the selector's dimension
SEEDS = sel.SEEDS  # [7, 17, 23, 31, 41] -- novel_types_v3's own seeds -> reconstructs its M_backward

OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"

GOLD_RICHER = REPO / "data" / "eval_gold_mention_role_mcguffey_v1" / "gold_grounded_appraisal_richer_v1.jsonl"
GOLD_CROSS = REPO / "data" / "eval_gold_mention_role_mcguffey_v1" / "gold_grounded_causal_crossspan_v2_DRAFT.jsonl"

RICHER_IDS = ["grapp_mcca_001", "grapp_mcca_003", "grapp_mcca_004", "grapp_mcca_005"]
CROSS_IDS = ["grapp_mcca_007", "grapp_mcca_008", "grapp_mcca_009"]  # Director-ACCEPTED; 006 EXCLUDED
EXCLUDED_IDS = ["grapp_mcca_006"]  # Director-REJECTED: mis-annotated span

# Fields the SELECTOR / RAW-MATCH mechanism must NEVER read (contamination guard).
MECH_FORBIDDEN_FIELDS = frozenset({
    "true_blocker_agent", "distractor_agent", "recency_baseline_prediction",
    "recency_baseline_correct", "recency_note", "gold_verified", "director_reviewed",
})
# Fields the mechanism MAY read (span texts + factual positions + the query/goal, which is the
# question NOT the answer -- goal_owner never names the true blocker agent; asserted at load).
TRUE_SLOT = 0  # fixed bookkeeping convention: slot 0 = true_blocker_span candidate

SIM_SANITY_FLOOR = 0.80
BRIDGE_ACC_FLOOR = 5.0 / 7.0          # 0.7143
BRIDGE_MARGIN_OVER_CHANCE = 0.10
CHANCE = 0.5

_T0 = time.time()


# ============================================================================
# gold loading + contamination guard
# ============================================================================
def _load_jsonl(path: Path) -> Dict[str, dict]:
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                d = json.loads(line)
                out[d["id"]] = d
    return out


def extract_goal_desc(goal_owner: str) -> str:
    """Outcome/goal DESCRIPTION = the parenthetical '(identify who ...)' inside goal_owner, which
    states the event to be causally explained WITHOUT naming the goal-owner agent. Using the raw
    goal_owner prefix would leak the owner's name (and in item 007 the owner IS the culprit) --
    the parenthetical is leak-safe for all 7 items (asserted in load_items)."""
    s = str(goal_owner)
    a, b = s.find("("), s.find(")")
    if 0 <= a < b:
        s = s[a + 1:b]
    for lbl in ("epistemic goal:", "blocked goal:"):
        s = s.replace(lbl, "")
    return s.strip()


def _agent_tokens(agent: str) -> List[str]:
    return [t for t in str(agent).replace("/", " ").split() if len(t) > 2 and t[0].isupper()]


def load_items() -> List[dict]:
    richer = _load_jsonl(GOLD_RICHER)
    cross = _load_jsonl(GOLD_CROSS)
    items = []
    for iid in RICHER_IDS:
        items.append(richer[iid])
    for iid in CROSS_IDS:
        items.append(cross[iid])
    assert len(items) == 7, f"expected 7 items, got {len(items)}"
    for it in items:
        assert it["id"] not in EXCLUDED_IDS
        # the ONLY goal text the mechanism sees is the parenthetical goal-DESCRIPTION + query text.
        # assert the true blocker agent's name tokens appear in NEITHER (no answer leak).
        goal_desc = extract_goal_desc(it["goal_owner"])
        query_text = it["query_span"]["text"]
        for tok in _agent_tokens(it.get("true_blocker_agent", "")):
            assert tok not in goal_desc, f"LEAK: agent {tok!r} in goal_desc of {it['id']}"
            assert tok not in query_text, f"LEAK: agent {tok!r} in query_text of {it['id']}"
    return items


def mech_inputs(item: dict) -> Dict[str, Any]:
    """The ONLY view of an item the selector/raw-match mechanism is allowed to see.
    Strips every forbidden gold-answer field by construction."""
    view = {
        "id": item["id"],
        "goal_desc": extract_goal_desc(item["goal_owner"]),
        "query_text": item["query_span"]["text"],
        "query_pos": int(item["query_span"]["line_range"][0]),
        # candidates in FIXED slot order (slot 0 = true_blocker_span, slot 1 = distractor_span).
        # The mechanism is NOT told which slot is the answer; it scores symmetrically.
        "cand_text": [item["true_blocker_span"]["text"], item["distractor_span"]["text"]],
        "cand_pos": [int(item["true_blocker_span"]["line_range"][0]),
                     int(item["distractor_span"]["line_range"][0])],
    }
    for k in view:
        assert k not in MECH_FORBIDDEN_FIELDS
    return view


# ============================================================================
# M_backward reconstruction -- BIT-IDENTICAL to novel_types_v3.run_one_seed (NO retrain on text)
# ============================================================================
def reconstruct_selector(seed: int):
    """Reproduce novel_types_v3's M_backward + the novel/train partitions EXACTLY (same call order,
    same seeds). Returns (M_backward, sr_diag, part_train, part_novel, g, digest)."""
    g = np.random.default_rng(seed)

    perm_gen = np.random.default_rng(int(seed) * 100003 + 5)
    perm_idx, _inv = sel.build_perm_transform(sel.N_DIM, perm_gen)

    tgen = torch.Generator(device=DEVICE); tgen.manual_seed(int(seed) * 100003 + 1)
    base_vectors = sel.build_type_base_vectors(sel.N_TYPES_TOTAL, sel.N_DIM, tgen)
    traj = sel.build_chain_trajectories(base_vectors, perm_idx, sel.CHAIN_HOPS)

    types_seen = list(range(0, sel.N_TYPES_SEEN))
    types_novel = list(range(sel.N_TYPES_SEEN, sel.N_TYPES_SEEN + sel.N_TYPES_NOVEL))

    egen_train = torch.Generator(device=DEVICE); egen_train.manual_seed(int(seed) * 100003 + 2)
    part_train = sel.ChainPartition(types_seen, sel.N_CHAINS_PER_TYPE_TRAIN, traj, sel.NOISE_FRAC,
                                    0, egen_train)

    egen_novel = torch.Generator(device=DEVICE); egen_novel.manual_seed(int(seed) * 100003 + 3)
    part_novel = sel.ChainPartition(types_novel, sel.N_CHAINS_PER_TYPE_NOVEL, traj, sel.NOISE_FRAC,
                                    part_train.id_end, egen_novel)

    adj_for_rollout = [dict(part_train.predecessors)]
    n_nodes_train = part_train.id_end - part_train.id_start
    n_transitions = min(200000, sel.ROLLOUT_PER_NODE * n_nodes_train)
    transitions = sel.collect_rollout_transitions(
        adj_for_rollout, n_ops=1, V=part_train.id_end, n_transitions=n_transitions,
        max_len=sel.ROLLOUT_MAX_LEN, g=g)

    sr_gen = torch.Generator(device=DEVICE); sr_gen.manual_seed(int(seed) * 7919 + 1)
    M_backward, sr_diag = sel.train_sr_transport(
        part_train.E, transitions, sel.N_DIM, sel.SR_STEPS, sel.SR_BATCH, sel.SR_LR, sel.GAMMA, sr_gen)

    digest = hashlib.sha256(M_backward.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    return M_backward, sr_diag, part_train, part_novel, g, digest


def sim_sanity_arm(part_novel, M_backward, seed: int, g) -> Dict[str, Any]:
    """novel_types_v3's arm_novel_1hop, UNCHANGED -- proves M_backward is bit-faithful & mechanism
    intact (target coherence_acc ~ 0.8733). Uses sel._arm exactly as the parent cell does."""
    return sel._arm(part_novel, 1, sel.N_EPISODES_EVAL, part_novel.E, M_backward, seed, 2, g)


# ============================================================================
# TEXT bridge: encode span -> 2048-dim HD; apply the sim-earned coherence rule
# ============================================================================
def encode_text(enc: CharTrigramEncoder, text: str) -> torch.Tensor:
    v = enc.encode(text)  # np bipolar [N_DIM]
    return torch.as_tensor(v, dtype=DTYPE, device=DEVICE).unsqueeze(0)  # [1, N_DIM]


def score_item_text(view: Dict[str, Any], enc: CharTrigramEncoder, M_backward: torch.Tensor
                    ) -> Dict[str, Any]:
    outcome_v = encode_text(enc, view["goal_desc"] + " " + view["query_text"])  # [1,N]
    cand_v = [encode_text(enc, t) for t in view["cand_text"]]                     # 2x [1,N]

    # SELECTOR (sim-earned M_backward): score_i = reach_value(outcome, cand_i, M) = cos(outcome@M, cand_i)
    sel_scores = [float(sel.reach_value(outcome_v, c, M_backward).item()) for c in cand_v]
    sel_pick = int(np.argmax(sel_scores))

    # RAW-MATCH (text-native rule, NO learned map = identity-M control): score_i = cos(cand_i, outcome)
    raw_scores = [float(sel.reach_control_targetcos(outcome_v, c).item()) for c in cand_v]
    raw_pick = int(np.argmax(raw_scores))

    # POSITIONAL RECENCY: most-recent candidate at/before the query; else nearest overall.
    qpos = view["query_pos"]
    before = [(view["cand_pos"][i], i) for i in range(2) if view["cand_pos"][i] <= qpos]
    if before:
        rec_pick = max(before)[1]
    else:
        rec_pick = int(np.argmin([abs(view["cand_pos"][i] - qpos) for i in range(2)]))

    return {
        "id": view["id"],
        "selector_scores": sel_scores, "selector_pick_slot": sel_pick, "selector_correct": sel_pick == TRUE_SLOT,
        "rawmatch_scores": raw_scores, "rawmatch_pick_slot": raw_pick, "rawmatch_correct": raw_pick == TRUE_SLOT,
        "positional_recency_pick_slot": rec_pick, "positional_recency_correct": rec_pick == TRUE_SLOT,
        "selector_margin": float(sel_scores[TRUE_SLOT] - sel_scores[1 - TRUE_SLOT]),
    }


# ============================================================================
# per-seed run
# ============================================================================
def run_one_seed(seed: int, enc: CharTrigramEncoder, views: List[Dict[str, Any]]) -> Dict[str, Any]:
    M_backward, sr_diag, part_train, part_novel, g, m_digest = reconstruct_selector(seed)
    sanity = sim_sanity_arm(part_novel, M_backward, seed, g)

    rows = [score_item_text(v, enc, M_backward) for v in views]

    # random baseline: seeded, one draw per item (analytic expectation = 0.5)
    rg = np.random.default_rng(int(seed) * 777 + 13)
    rand_correct = int(np.sum([rg.integers(0, 2) == TRUE_SLOT for _ in views]))

    n = len(rows)
    return {
        "seed": int(seed),
        "m_backward_digest": m_digest,
        "sr_diag": {"err_first": sr_diag.get("err_first"), "err_last": sr_diag.get("err_last")},
        "sim_sanity_coherence_acc": sanity.get("coherence_acc_conservative"),
        "sim_sanity_oracle_acc": sanity.get("oracle_acc"),
        "sim_sanity_recency_acc": sanity.get("recency_acc"),
        "sim_sanity_no_replay_local_acc": sanity.get("no_replay_local_acc"),
        "text_rows": rows,
        "selector_text_acc": sum(r["selector_correct"] for r in rows) / n,
        "rawmatch_text_acc": sum(r["rawmatch_correct"] for r in rows) / n,
        "positional_recency_acc": sum(r["positional_recency_correct"] for r in rows) / n,
        "random_text_acc": rand_correct / n,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate(per_seed: List[Dict[str, Any]], items: List[dict]) -> Dict[str, Any]:
    seeds = [d["seed"] for d in per_seed]

    def m(k: str) -> float:
        return float(np.mean([d[k] for d in per_seed]))

    sim_sanity = m("sim_sanity_coherence_acc")
    sim_oracle = m("sim_sanity_oracle_acc")
    selector_text = m("selector_text_acc")
    rawmatch_text = m("rawmatch_text_acc")
    positional_recency = m("positional_recency_acc")
    random_text = m("random_text_acc")

    # gold-declared recency floor (the recency BASELINE's own annotation; NEVER used by any
    # mechanism -- read here ONLY to report the intended recency floor, which is 0/7 by design).
    gold_recency_correct = sum(1 for it in items if it.get("recency_baseline_correct") is True)
    gold_recency_acc = gold_recency_correct / len(items)

    m_digests = [d["m_backward_digest"] for d in per_seed]
    m_digests_stable = len(set(m_digests)) == len(m_digests)  # per-seed distinct (seed-dependent M)

    sr_conv = all((d["sr_diag"]["err_last"] is not None and d["sr_diag"]["err_first"] is not None
                   and d["sr_diag"]["err_last"] < d["sr_diag"]["err_first"]) for d in per_seed)

    # per-item selector correctness fraction across seeds (glass-box)
    per_item = {}
    for it in items:
        iid = it["id"]
        picks = []
        for d in per_seed:
            r = next(rr for rr in d["text_rows"] if rr["id"] == iid)
            picks.append(r["selector_correct"])
        per_item[iid] = {
            "selector_correct_frac_over_seeds": float(np.mean(picks)),
            "rawmatch_correct_any_seed": any(
                next(rr for rr in d["text_rows"] if rr["id"] == iid)["rawmatch_correct"]
                for d in per_seed),
        }

    sim_ok = sim_sanity >= SIM_SANITY_FLOOR and sim_oracle >= 0.999
    selector_beats_floors = (selector_text >= BRIDGE_ACC_FLOOR
                             and selector_text > max(positional_recency, gold_recency_acc)
                             and selector_text >= CHANCE + BRIDGE_MARGIN_OVER_CHANCE)
    rawmatch_beats_floors = (rawmatch_text >= BRIDGE_ACC_FLOOR
                             and rawmatch_text > max(positional_recency, gold_recency_acc)
                             and rawmatch_text >= CHANCE + BRIDGE_MARGIN_OVER_CHANCE)
    selector_near_chance = 0.30 <= selector_text <= 0.60

    if not sim_ok:
        verdict = "GATE_FAILED_SIM_SANITY"
        msg = ("M_backward reconstruction/mechanism check FAILED (sim_sanity coherence_acc=%.4f "
               "[need>=%.2f], oracle=%.4f [need>=0.999]) -- cannot interpret text transfer either "
               "way; the reused selector is not bit-faithful to novel_types_v3." %
               (sim_sanity, SIM_SANITY_FLOOR, sim_oracle))
    elif selector_beats_floors:
        verdict = "BRIDGES"
        msg = ("SIM-EARNED SELECTOR TRANSFERS TO REAL TEXT (n=7, DIRECTIONAL not powered): "
               "selector_text_acc=%.4f >= %.4f, beats positional_recency=%.4f, gold_recency=%.4f, "
               "chance=%.2f; sim_sanity intact=%.4f. First evidence the sim-earned causal selector "
               "bridges to real text via the substrate-native HD encoder. VET hard: tiny n." %
               (selector_text, BRIDGE_ACC_FLOOR, positional_recency, gold_recency_acc, CHANCE,
                sim_sanity))
    elif selector_near_chance:
        if rawmatch_beats_floors:
            verdict = "PARTIAL_RULE_TRANSFERS_MAP_DOES_NOT"
            msg = ("REPRESENTATION-BRIDGE PARTIAL: the sim-earned SELECTOR (learned map M_backward) is "
                   "~chance on text (selector_text_acc=%.4f) while M_backward is intact on sim "
                   "(sim_sanity=%.4f), BUT the text-native RAW-MATCH rule (cos(effect,outcome), NO "
                   "learned map) DOES beat baselines (rawmatch=%.4f). => the abstract coherence RULE "
                   "transfers; the sim-LEARNED MAP (inverse of the sim's fixed permutation T) does not. "
                   "Route: re-ground the selector's map on a text-compatible representation." %
                   (selector_text, sim_sanity, rawmatch_text))
        else:
            verdict = "CANNOT_BRIDGE_REPRESENTATION_GAP"
            msg = ("SIM-TO-TEXT REPRESENTATION BRIDGE IS THE GAP (the honest, routing negative): "
                   "M_backward is INTACT on sim (sim_sanity coherence_acc=%.4f >=%.2f, oracle=%.4f) but "
                   "~CHANCE on real text (selector_text_acc=%.4f in [0.30,0.60]; positional_recency=%.4f "
                   "gold_recency=%.4f random=%.4f); the text-native raw-match also fails (rawmatch=%.4f). "
                   "M_backward learned the INVERSE of the sim's fixed coordinate-axis permutation T; "
                   "text-derived HD content has NO T-orbit relation, so reach_value scores are "
                   "uninformative. The abstract coherence rule was over sim type-geometry with no path "
                   "to real semantic content. ROUTES NEXT BUILD: re-ground/learn the selector on a "
                   "text-compatible representation (or build the representation bridge) -- do NOT retrain "
                   "M_backward on text expecting it to help; the gap is the ENCODING, not the rule's "
                   "logic. n=7 TINY -- directional." %
                   (sim_sanity, SIM_SANITY_FLOOR, sim_oracle, selector_text, positional_recency,
                    gold_recency_acc, random_text, rawmatch_text))
    else:
        verdict = "PARTIAL_MIDDLE_BAND"
        msg = ("MIDDLE BAND (n=7 TINY, directional): selector_text_acc=%.4f between chance-band and "
               "the BRIDGES floor %.4f; sim_sanity=%.4f, rawmatch=%.4f, positional_recency=%.4f, "
               "gold_recency=%.4f, random=%.4f. Not a clean transfer, not clean chance -- "
               "underpowered/scope-limited; report as inconclusive-leaning, route a text-compatible "
               "re-grounding of the selector before any transfer claim." %
               (selector_text, BRIDGE_ACC_FLOOR, sim_sanity, rawmatch_text, positional_recency,
                gold_recency_acc, random_text))

    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "n_items": len(items),
        "n_seeds": len(seeds),
        "seeds": seeds,
        "means": {
            "sim_sanity_coherence_acc": sim_sanity,
            "sim_sanity_oracle_acc": sim_oracle,
            "selector_text_acc": selector_text,
            "rawmatch_text_acc": rawmatch_text,
            "positional_recency_acc": positional_recency,
            "gold_declared_recency_acc": gold_recency_acc,
            "random_text_acc": random_text,
            "chance": CHANCE,
        },
        "bands": {
            "sim_sanity_ok": bool(sim_ok),
            "selector_beats_floors": bool(selector_beats_floors),
            "rawmatch_beats_floors": bool(rawmatch_beats_floors),
            "selector_near_chance": bool(selector_near_chance),
            "sr_td_converged_all_seeds": bool(sr_conv),
            "m_backward_digests_per_seed_distinct": bool(m_digests_stable),
        },
        "per_item_selector_over_seeds": per_item,
        "m_backward_digests": {str(d["seed"]): d["m_backward_digest"] for d in per_seed},
        "contamination_check": {
            "mechanism_forbidden_fields": sorted(MECH_FORBIDDEN_FIELDS),
            "mechanism_reads_only": ["goal_owner", "query_span.text", "*_span.text (candidates)",
                                     "*_span.line_range (positions)"],
            "gold_recency_correct_read_for_baseline_reporting_only": True,
            "sim_earned_M_backward_retrained_on_text": False,
        },
        "sim_sanity_reference": ("MEASURED@ data/exp_coherence_selector_novel_types_v3/metrics.json "
                                 "arm_novel_1hop coherence_eval_acc=0.8733 (seeds 7,17,23,31,41)"),
        "per_seed": per_seed,
    }


# ============================================================================
# self-test + main
# ============================================================================
def self_test() -> bool:
    """(1) M_backward reconstruction reproduces novel_types_v3's sim_sanity ~0.87 on seed 7.
    (2) contamination: mech_inputs strips every forbidden field. (3) selector & rawmatch produce
    a well-formed pick per item."""
    items = load_items()
    assert len(items) == 7
    v = mech_inputs(items[0])
    for fld in MECH_FORBIDDEN_FIELDS:
        assert fld not in v, f"forbidden field {fld} leaked into mech view"
    M, _sr, _pt, part_novel, g, dig = reconstruct_selector(7)
    sanity = sim_sanity_arm(part_novel, M, 7, g)
    acc = sanity.get("coherence_acc_conservative")
    print(f"[self-test] seed7 sim_sanity coherence_acc={acc:.4f} oracle={sanity.get('oracle_acc'):.4f} "
          f"m_digest={dig}", flush=True)
    assert acc is not None and acc >= SIM_SANITY_FLOOR, f"sim_sanity {acc} < floor {SIM_SANITY_FLOOR}"
    enc = CharTrigramEncoder(n_dim=N_DIM)
    r = score_item_text(v, enc, M)
    assert r["selector_pick_slot"] in (0, 1) and r["rawmatch_pick_slot"] in (0, 1)
    print(f"[SELFTEST PASS] item0 selector_pick={r['selector_pick_slot']} "
          f"rawmatch_pick={r['rawmatch_pick_slot']}", flush=True)
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = load_items()
    views = [mech_inputs(it) for it in items]
    enc = CharTrigramEncoder(n_dim=N_DIM)

    per_seed = []
    for seed in SEEDS:
        t0 = time.time()
        res = run_one_seed(seed, enc, views)
        per_seed.append(res)
        print("[seed=%d] %.1fs sim_sanity=%.4f selector_text=%.4f rawmatch=%.4f pos_recency=%.4f "
              "random=%.4f m_digest=%s" % (
                  seed, time.time() - t0, res["sim_sanity_coherence_acc"], res["selector_text_acc"],
                  res["rawmatch_text_acc"], res["positional_recency_acc"], res["random_text_acc"],
                  res["m_backward_digest"]), flush=True)

    final = aggregate(per_seed, items)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _T0, 1)
    final["ts_iso"] = datetime.now(timezone.utc).isoformat()
    final["pid"] = os.getpid()
    final["device"] = str(DEVICE)
    final["n_dim"] = N_DIM
    final["prereg"] = "preregs/2026-08-04_coherence_selector_text_transfer_v1.md"

    tmp = OUT_DIR / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)
    os.replace(tmp, OUT_DIR / "metrics.json")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        ok = self_test()
        sys.exit(0 if ok else 1)
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
        }
        try:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            with open(OUT_DIR / "metrics.json", "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
        except Exception:
            pass
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
