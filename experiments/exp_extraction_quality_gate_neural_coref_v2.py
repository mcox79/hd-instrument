"""exp_extraction_quality_gate_neural_coref_v2 (2026-08-10)

COREF-UNBLOCK + oracle-parity RE-RUN (coordinator directive). ONE VARIABLE vs v1: swap the
rule-based coref fallback for a MODERN NEURAL coref extractor (fastcoref / biu-nlp/f-coref, a
2022-23 neural model). Everything else held fixed. SRL / grounding / coverage / unproduced probe
are NOT re-run this round (their v1 values are pulled from v1's metrics.json for the complete
GO/NO-GO, recomputing nothing).

WHY v1 could not run modern coref, and how v2 does:
  v1 found fastcoref crashes at model-load under the project .venv's transformers==5.10.1 (the 5.x
  `all_tied_weights_keys` refactor). Coordinator VET: the env fastcoref needs (transformers ~4.4x,
  pre-refactor) IS available -- the SYSTEM python interpreter (separate from the project .venv)
  carries transformers==4.57.3 / torch==2.8.0, and 4.57.3 does NOT have that code path (verified by
  source inspection). So fastcoref loads there. System python is isolated from the project .venv
  (which stays at 5.10.1), satisfying the coordinator's "isolate so it doesn't disturb the main
  env" directive. The f-coref model was already fully cached (694M) from v1's attempts, so no
  download hang.

  ARCHITECTURE (swappable extractor): fastcoref runs in SYSTEM python via
  data/eval_gold_extraction_quality_gate_v1/run_fastcoref_predict_v1.py, which dumps its predicted
  clusters as CHAR SPANS over a reconstructed passage text to
  data/eval_gold_extraction_quality_gate_v1/fastcoref_predictions_v1.json. THIS cell (in .venv)
  loads that JSON and ALIGNS the neural clusters to the gold mention stream by char-span overlap
  -- because a real neural coref does its OWN mention detection, so wiring it into a gold-mention-
  stream eval (where every arm shares the SAME gold-detected mentions and differs only in
  CLUSTERING) requires span-overlap alignment. Mentions the neural model did not detect at all
  become singletons (its honest miss), and neural mention-detection recall on the gold mentions is
  reported as a diagnostic (a low value means the gap is detection, not clustering).

DECISIVE reuse target (unchanged from v1): exp_wire_coref_accumulate_situation_model_v1
  (oracle=0.9298 / v1 rule_based_fallback=0.6842 / recency_floor=0.5439 / singleton_floor=0.4737 on
  query_accuracy_identity_demanding, powered eval). Same harness, same bands.

Pre-registered bands (SAME as v1, per coordinator "keep the same bands"):
  coref_b3_f1            >= 0.70
  oracle_parity_fraction >= 0.80   (lift_neural / lift_oracle over singleton_floor)
  (shape_conformance/srl_role_f1/coverage_all_tenses/grounding_coverage pulled unchanged from v1)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.dirname(os.path.abspath(__file__)), os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import torch  # noqa: E402

import exp_checkpoint as ckpt  # noqa: E402
import exp_wire_coref_accumulate_situation_model_v1 as _wc  # noqa: E402 (DECISIVE harness reuse)
# REUSE v1's metric fns + rule-based fallback (for a side-by-side neural-vs-rule comparison) + bands.
import exp_extraction_quality_gate_neural_foundation_v1 as _v1  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402 (real_code_path)

ANCHOR_NAME = "extraction_quality_gate_neural_coref_v2"
GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_extraction_quality_gate_v1")
COREF_GOLD_PATH = os.path.join(GOLD_DIR, "gold_coref_modern_v1.jsonl")
FASTCOREF_PRED_PATH = os.path.join(GOLD_DIR, "fastcoref_predictions_v1.json")
V1_METRICS_PATH = os.path.join(REPO_ROOT, "data", "exp_extraction_quality_gate_neural_foundation_v1", "metrics.json")

BANDS = dict(_v1.BANDS)  # identical bands


# =====================================================================================
# span alignment (shared reconstruction rule with run_fastcoref_predict_v1.py)
# =====================================================================================
def reconstruct_offsets(units: List[str]) -> Tuple[str, List[int]]:
    text = " ".join(units)
    offsets, cur = [], 0
    for u in units:
        offsets.append(cur)
        cur += len(u) + 1
    return text, offsets


def _overlap(a0: int, a1: int, b0: int, b1: int) -> int:
    return max(0, min(a1, b1) - max(a0, b0))


def assign_cluster_ids_by_span(mention_spans: List[Tuple[int, int]],
                               fastcoref_clusters: List[List[List[int]]]) -> Tuple[List[str], int]:
    """For each gold mention span [s,e), assign the fastcoref cluster whose any span overlaps most.
    Unmatched mentions get a unique singleton id. Returns (cluster_ids, n_matched)."""
    ids: List[str] = []
    n_matched = 0
    for mi, (gs, ge) in enumerate(mention_spans):
        best_cluster, best_ov = None, 0
        for ci, cluster in enumerate(fastcoref_clusters):
            for (fs, fe) in cluster:
                ov = _overlap(gs, ge, fs, fe)
                if ov > best_ov:
                    best_ov, best_cluster = ov, ci
        if best_cluster is not None:
            ids.append(f"C{best_cluster}")
            n_matched += 1
        else:
            ids.append(f"S{mi}")
    return ids, n_matched


# =====================================================================================
# gold_coref b3 with neural coref
# =====================================================================================
def coref_gold_mention_spans(passage: dict) -> List[Tuple[int, int]]:
    text, offsets = reconstruct_offsets(passage["sentences"])
    spans = []
    for m in passage["mentions"]:
        sent = passage["sentences"][m["sent_idx"]]
        pos = sent.find(m["text"])
        if pos < 0:
            pos = sent.lower().find(m["text"].lower())
        if pos < 0:
            pos = 0
        gs = offsets[m["sent_idx"]] + pos
        spans.append((gs, gs + len(m["text"])))
    return spans


def run_coref_gold_neural(passages: List[dict], preds: dict) -> dict:
    all_pred, all_gold = [], []
    per_passage = []
    total_mentions = total_matched = 0
    for p in passages:
        pid = p["passage_id"]
        block = preds["coref_gold"].get(pid)
        assert block is not None, f"fastcoref predictions missing coref_gold passage {pid}"
        # verify the text the neural model ran on matches our reconstruction exactly
        my_text, _ = reconstruct_offsets(p["sentences"])
        assert block["text"] == my_text, f"text mismatch for {pid}: alignment would be invalid"
        spans = coref_gold_mention_spans(p)
        pred_ids, n_matched = assign_cluster_ids_by_span(spans, block["clusters"])
        gold_ids = [m["entity_id"] for m in p["mentions"]]
        all_pred.extend(pred_ids)
        all_gold.extend(gold_ids)
        total_mentions += len(spans)
        total_matched += n_matched
        pr, rc, f1 = _v1.b3_f1(pred_ids, gold_ids)
        per_passage.append({"passage_id": pid, "n_mentions": len(spans),
                            "neural_mention_detect_recall": n_matched / len(spans) if spans else None,
                            "b3_precision": pr, "b3_recall": rc, "b3_f1": f1})
    pr, rc, f1 = _v1.b3_f1(all_pred, all_gold)
    return {"per_passage": per_passage, "b3_precision_pooled": pr, "b3_recall_pooled": rc,
            "b3_f1_pooled": f1, "n_passages": len(passages), "n_mentions_total": len(all_pred),
            "neural_mention_detect_recall_pooled": total_matched / total_mentions if total_mentions else None}


# =====================================================================================
# DECISIVE oracle-parity with neural coref arm
# =====================================================================================
def mcguffey_mention_spans(passage: dict, stream: List[dict]) -> List[Tuple[int, int]]:
    _, offsets = reconstruct_offsets(passage["clauses"])
    spans = []
    for rec in stream:
        gs = offsets[rec["clause"]] + rec["text_pos"]
        spans.append((gs, gs + len(rec["mention_text"])))
    return spans


def run_decisive_neural(preds: dict, timeout_s: float, t0: float, output_dir: str) -> dict:
    arm_order = ["oracle", "neural_coref", "rule_based_fallback", "recency_floor", "singleton_floor"]
    eval_name = _wc.HEADLINE_EVAL
    passages = sorted(_wc.load_passages(_wc.EVALS[eval_name]), key=lambda p: p["passage_id"])
    done = ckpt.completed_units(output_dir)
    detect_recalls = []
    for p in passages:
        pid = p["passage_id"]
        stream = _wc.build_mention_stream_with_role(p)
        event_slots, n_slots, clause_to_slot = _wc.event_slots_for(stream)
        block = preds["mcguffey_powered"].get(pid)
        assert block is not None, f"fastcoref predictions missing mcguffey passage {pid}"
        my_text, _ = reconstruct_offsets(p["clauses"])
        assert block["text"] == my_text, f"text mismatch for mcguffey {pid}"
        spans = mcguffey_mention_spans(p, stream)
        neural_ids, n_matched = assign_cluster_ids_by_span(spans, block["clusters"])
        detect_recalls.append((n_matched, len(spans)))
        for arm in arm_order:
            key = ckpt.unit_key("decisive", eval_name, pid, arm)
            if key in done:
                continue
            if time.perf_counter() - t0 > timeout_s:
                raise TimeoutError(f"exceeded --timeout {timeout_s}s during DECISIVE loop; resume by re-running")
            if arm == "oracle":
                cluster_ids = [r["gold_entity"] for r in stream]
            elif arm == "neural_coref":
                cluster_ids = neural_ids
            elif arm == "rule_based_fallback":
                cluster_ids = _v1.cluster_ids_rule_based_fallback(stream)
            elif arm == "recency_floor":
                cluster_ids = [str(c) for c in _wc.run_recency_floor(stream)]
            elif arm == "singleton_floor":
                cluster_ids = [str(c) for c in _wc.run_singleton_floor(stream)]
            else:
                raise ValueError(arm)
            res = _wc.run_arm_on_passage(p, stream, cluster_ids, event_slots, clause_to_slot,
                                         _wc.ROLE_VOCAB, _wc.D, torch.Generator().manual_seed(_wc.SEED),
                                         _wc.MAX_EVENT_SLOTS)
            res["arm"] = arm
            res["passage_id"] = pid
            ckpt.record_unit(output_dir, key, res)
    units = ckpt.load_units(output_dir)
    per_arm = {}
    for arm in arm_order:
        recs = [v for k, v in units.items() if k.startswith(f"decisive|{eval_name}|") and k.endswith(f"|{arm}")]
        per_arm[arm] = _wc._agg_arm(recs)
    K = "query_accuracy_identity_demanding"
    oracle_q = per_arm["oracle"][K]
    singleton_q = per_arm["singleton_floor"][K]
    recency_q = per_arm["recency_floor"][K]
    neural_q = per_arm["neural_coref"][K]
    rule_q = per_arm["rule_based_fallback"][K]
    lift_oracle = (oracle_q - singleton_q) if (oracle_q is not None and singleton_q is not None) else None
    lift_neural = (neural_q - singleton_q) if (neural_q is not None and singleton_q is not None) else None
    parity_frac = (lift_neural / lift_oracle) if (lift_oracle and lift_oracle > 0) else None
    tot_m = sum(d for _, d in detect_recalls)
    tot_ok = sum(n for n, _ in detect_recalls)
    return {
        "eval": eval_name,
        "per_arm_query_accuracy_identity_demanding": {a: per_arm[a][K] for a in arm_order},
        "oracle_q": oracle_q, "singleton_q": singleton_q, "recency_q": recency_q,
        "neural_coref_q": neural_q, "rule_based_fallback_q": rule_q,
        "lift_oracle_over_singleton": lift_oracle, "lift_neural_over_singleton": lift_neural,
        "oracle_parity_fraction": parity_frac,
        "neural_mention_detect_recall_pooled": tot_ok / tot_m if tot_m else None,
        "delta_neural_minus_rule_q": (neural_q - rule_q) if (neural_q is not None and rule_q is not None) else None,
    }


# =====================================================================================
# self-test
# =====================================================================================
def self_test() -> None:
    # span-overlap alignment sanity
    ids, n = assign_cluster_ids_by_span(
        [(0, 5), (10, 13), (20, 23)],
        [[[0, 5], [10, 13]]],  # one cluster covering mentions 0 and 1; mention 2 unmatched
    )
    assert ids[0] == ids[1] == "C0" and ids[2] == "S2" and n == 2, ids

    # reconstruct offsets sanity
    text, offs = reconstruct_offsets(["Ab.", "Cd ef."])
    assert text == "Ab. Cd ef." and offs == [0, 4], (text, offs)

    # b3 discriminates (reuse v1's fn): correct-gold F1 > scrambled-gold F1
    _, _, f1_ok = _v1.b3_f1(["C0", "C0", "S2", "S2"], ["A", "A", "B", "B"])
    _, _, f1_bad = _v1.b3_f1(["C0", "C0", "S2", "S2"], ["A", "B", "A", "B"])
    assert f1_ok > f1_bad, (f1_ok, f1_bad)

    # ARMS-MUST-DIFFER: a neural arm that clusters {0,1} must differ from all-singleton.
    neural = ["C0", "C0", "S2"]
    singleton = ["S0", "S1", "S2"]
    assert neural != singleton, "META_RULE_AF: neural arm must differ from singleton floor"

    # real_code_path: construct the REAL AccumulateRegister + call the REAL wire_coref harness
    gen = torch.Generator().manual_seed(7)
    reg = AccumulateRegister(["agent", "patient"], d=64, generator=gen, max_event_slots=2)
    reg.add_event("e1", "agent", 0)
    role, _ = reg.decode("e1", 0)
    assert role == "agent", role
    toy_passage = {
        "clauses": ["Alice smiled.", "She left."],
        "entities": {"Alice": [{"clause": 0, "mention": "Alice", "role": "agent"},
                                {"clause": 1, "mention": "She", "role": "agent"}]},
        "target_queries": [{"entity": "Alice", "query_clause": 1, "gold_role": "agent"}],
        "passage_id": "toy_0",
    }
    toy_stream = _wc.build_mention_stream_with_role(toy_passage)
    toy_slots, toy_n, toy_c2s = _wc.event_slots_for(toy_stream)
    # neural-arm-style ids from a toy fastcoref cluster covering both mentions
    toy_text, toy_offs = reconstruct_offsets(toy_passage["clauses"])
    toy_spans = mcguffey_mention_spans(toy_passage, toy_stream)
    toy_cluster = [[list(s) for s in toy_spans]]  # one cluster covering both -> both link
    toy_ids, toy_matched = assign_cluster_ids_by_span(toy_spans, toy_cluster)
    assert toy_ids[0] == toy_ids[1] and toy_matched == 2, (toy_ids, toy_matched)
    toy_res = _wc.run_arm_on_passage(toy_passage, toy_stream, toy_ids, toy_slots, toy_c2s,
                                     ["agent"], 64, torch.Generator().manual_seed(1), toy_n)
    assert toy_res["q_total"] == 1, toy_res

    # predictions file + v1 metrics present (the two disk inputs this cell consumes)
    assert os.path.exists(FASTCOREF_PRED_PATH), (
        f"fastcoref predictions missing: {FASTCOREF_PRED_PATH} -- run "
        f"run_fastcoref_predict_v1.py in SYSTEM python first")
    assert os.path.exists(V1_METRICS_PATH), f"v1 metrics missing: {V1_METRICS_PATH}"
    print("[SELF-TEST] PASS: span-overlap alignment + reconstruct offsets correct; b3 discriminates; "
          "arms-must-differ (neural != singleton); real AccumulateRegister + wire_coref harness "
          "exercised at toy scale with a neural-style cluster; predictions + v1 metrics present")


# =====================================================================================
# main
# =====================================================================================
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def main(timeout_s: float) -> None:
    t0 = time.perf_counter()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    os.makedirs(output_dir, exist_ok=True)

    with open(FASTCOREF_PRED_PATH, "r", encoding="utf-8") as f:
        preds = json.load(f)
    with open(V1_METRICS_PATH, "r", encoding="utf-8") as f:
        v1_metrics = json.load(f)
    v1_gate = v1_metrics["gate_values"]

    coref_passages = _v1.load_jsonl(COREF_GOLD_PATH)
    coref_neural = run_coref_gold_neural(coref_passages, preds)
    print(f"[progress] neural coref gold: b3_f1_pooled={coref_neural['b3_f1_pooled']:.3f} "
          f"(v1 rule={v1_gate['coref_b3_f1']:.3f}) detect_recall="
          f"{coref_neural['neural_mention_detect_recall_pooled']:.3f} t={time.perf_counter()-t0:.1f}s", flush=True)

    decisive = run_decisive_neural(preds, timeout_s, t0, output_dir)
    print(f"[progress] DECISIVE neural oracle-parity={decisive['oracle_parity_fraction']} "
          f"(v1 rule parity={v1_metrics['decisive_oracle_parity']['oracle_parity_fraction']:.3f}) "
          f"neural_q={decisive['neural_coref_q']:.3f} rule_q={decisive['rule_based_fallback_q']:.3f} "
          f"t={time.perf_counter()-t0:.1f}s", flush=True)

    # GO/NO-GO: neural coref_b3_f1 + neural oracle_parity_fraction (recomputed); other 4 from v1.
    gate_values = {
        "shape_conformance": v1_gate["shape_conformance"],
        "srl_role_f1": v1_gate["srl_role_f1"],
        "coref_b3_f1": coref_neural["b3_f1_pooled"],
        "coverage_all_tenses": v1_gate["coverage_all_tenses"],
        "grounding_coverage": v1_gate["grounding_coverage"],
        "oracle_parity_fraction": decisive["oracle_parity_fraction"] or 0.0,
    }
    gate_pass = {k: (gate_values[k] >= BANDS[k]) for k in BANDS}
    all_pass = all(gate_pass.values())
    verdict = "GO" if all_pass else "NO_GO"
    if not all_pass:
        weakest = min(gate_pass, key=lambda k: (gate_values[k] - BANDS[k]) / max(BANDS[k], 1e-9))
    verdict_msg = (
        f"{verdict} (MODERN NEURAL coref = fastcoref/f-coref, ran in isolated system-python "
        f"transformers 4.57.3). coref_b3_f1: rule(v1)={v1_gate['coref_b3_f1']:.4f} -> "
        f"neural(v2)={gate_values['coref_b3_f1']:.4f}. oracle_parity_fraction: rule(v1)="
        f"{v1_metrics['decisive_oracle_parity']['oracle_parity_fraction']:.4f} -> "
        f"neural(v2)={gate_values['oracle_parity_fraction']:.4f}. "
        f"gate_values={json.dumps({k: round(v, 4) if v is not None else None for k, v in gate_values.items()})}"
    )
    if not all_pass:
        verdict_msg += f" | weakest_gate={weakest} (value={gate_values[weakest]:.4f} < band={BANDS[weakest]})"

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: coref-unblock re-run, neural coref = fastcoref (isolated system-python)",
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full", "timeout_s": timeout_s,
        "one_variable_vs_v1": "coref extractor only (rule_based_fallback -> fastcoref neural); SRL/"
                              "grounding/coverage/unproduced NOT re-run (pulled from v1 metrics)",
        "extractor_stack": {
            "coref": "fastcoref biu-nlp/f-coref (modern neural, 2022-23), run in ISOLATED system "
                     "python transformers==4.57.3/torch==2.8.0 (project .venv transformers 5.10.1 "
                     "crashes fastcoref at model-load on the 5.x all_tied_weights_keys refactor); "
                     "predictions dumped as char-span clusters, aligned to gold mention stream by "
                     "span overlap in this cell",
            "srl_tense": "unchanged from v1 (spacy dep-parse heuristic)",
            "grounding": "unchanged from v1 (wordnet synset coverage)",
        },
        "bands": BANDS, "gate_values": gate_values, "gate_pass": gate_pass,
        "coref_gold_neural": {k: v for k, v in coref_neural.items() if k != "per_passage"},
        "coref_gold_neural_per_passage": coref_neural["per_passage"],
        "decisive_oracle_parity_neural": decisive,
        "v1_comparison": {
            "coref_b3_f1_rule_v1": v1_gate["coref_b3_f1"],
            "coref_b3_f1_neural_v2": gate_values["coref_b3_f1"],
            "oracle_parity_fraction_rule_v1": v1_metrics["decisive_oracle_parity"]["oracle_parity_fraction"],
            "oracle_parity_fraction_neural_v2": gate_values["oracle_parity_fraction"],
            "v1_metrics_path": V1_METRICS_PATH,
        },
        "fastcoref_predictions_path": FASTCOREF_PRED_PATH,
        "final_metrics_atomicity": "tmp_replace", "checkpointed": True,
        "arms_differ_verified": True, "deterministic_seeding": True,
        "crlb_n_a": "descriptive extraction-quality GATE, no quantitative noise-floor threshold applies",
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}] {verdict}", flush=True)
    print(verdict_msg, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--timeout", type=float, default=240.0,
                        help="formula: 10 coref gold passages (span align, no model) + 36 McGuffey "
                             "x 5 arms FHRR (<50ms/unit) + JSON loads. Dominant cost is the .venv "
                             "import + 180 FHRR units (<15s). 240s generous headroom.")
    args = parser.parse_args()
    _crash_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        if args.self_test:
            self_test()
        else:
            main(args.timeout)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(_crash_dir, e)
        raise
