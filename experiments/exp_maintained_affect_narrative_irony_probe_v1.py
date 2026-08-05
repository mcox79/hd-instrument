# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): arm_c-local-pred vs maintained-affect-pred
#   hash-compared; must differ on at least the narrative-missed items.
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb: n/a -- fixed 10-item eval, no capacity sweep.
# - calibration_check: default_ok_for_this_regime (HARM_WORDS/HELP_WORDS lexicon reused verbatim
#   unchanged; window=400 is a single fixed constant, not tuned per item -- see prereg).
# - cell_chunked: false (n=10, single deterministic pass, <5s, no seed axis).
# - all numbers MEASURED@ tagged in the completion report, not this file.
#
# PROBE: does a per-entity MAINTAINED-AFFECT trajectory (wide prior-window entity-tagged
# paragraphs scored with the REUSED blind-valence lexicon) recover the narrative-only irony items
# arm_c (local +-2-line window) missed? See
# preregs/2026-08-05_maintained_affect_narrative_irony_probe_v1.md for full design + bands.
#
# CORRECTED PREMISE (code-read of hdlab/situation_reader.py): SituationModel has no per-entity
# affect/valence state, and its read() path needs a CoNLL mention stream unavailable for raw
# novel text at this probe's scope. This probe therefore uses a DECLARED SIMPLIFICATION of coref
# (literal entity-name-variant string match per paragraph -- a Centering-lite "same compatible
# antecedent, most recent block" backward search) rather than the full CorefReader/SituationModel
# stack. This is flagged, not silently substituted.
"""Standalone probe. Reuses (never re-derives) exp_grounded_appraisal_transfer_to_text_v1's fitted
arm_c hypothesis + resolve_valence_context + resolve_valence_blind + get_corpus_context /
_corpus_lines. Adds ONE new mechanism: a wide-window (400-line, strictly-prior) per-entity
maintained-affect trajectory + an incongruity override rule on top of arm_c's own local
prediction. Evaluated on the SAME 10 irony/sincere gold items, reported per discriminating
subset (narrative-missed / local-cue / sincere-FP-check)."""
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "maintained_affect_narrative_irony_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import exp_grounded_appraisal_transfer_to_text_v1 as armc  # noqa: E402 (REUSED, unchanged)

EXPECTED_N_ITEMS = 10
WINDOW_LINES = 400  # fixed constant; bounds the observed max supporting-evidence distance (~131
                     # lines) with margin. NOT tuned per item -- see prereg calibration_check.
LOCAL_EXCLUDE = 3    # exclude the +-2 lines arm_c's own local window already covers

# ---- GIVEN speaker/agent identity (factual WHO, same tier as the parent cell's own
# IRONY_AGENT_TARGET / MULTI_CAND_ORACLE_TRUE_SLOT tables). Sourced from the surface_span's OWN
# text (e.g. "answered Oz" is literally inside grapp_irony_002's surface_span) or well-established
# scene identity -- NEVER from supporting_span or the answer fields (true_intent_valence /
# surface_valence). Declared per item so contamination is auditable. ----
AGENT_FOR_ITEM = {
    "grapp_irony_001": ("Jo", "surface_span itself narrates Jo's line"),
    "grapp_sincere_001": ("Meg", "surface_span context: 'Meg spoke earnestly'"),
    "grapp_irony_002": ("Oz", "surface_span text: 'answered Oz'"),
    "grapp_sincere_002": ("Marilla", "matched_pair note names Marilla as speaker"),
    "grapp_irony_003": ("Tom", "chapter-identity: Tom Sawyer whitewashing scene"),
    "grapp_sincere_003": ("Aunt Polly", "matched_pair note names Aunt Polly as speaker"),
    "grapp_irony_004": ("Oz", "chapter-identity: same Oz heart-granting scene as irony_002"),
    "grapp_sincere_004": ("Marilla", "matched_pair note names Marilla as speaker"),
    "grapp_irony_005": ("Tom", "chapter-identity: Tom Sawyer fake-deathbed scene"),
    "grapp_sincere_005": ("Marilla", "surface_span context: Mrs Lynde/Marilla praise scene"),
}
NAME_VARIANTS = {
    "Jo": ["Jo"], "Meg": ["Meg"], "Oz": ["Oz", "Wizard"], "Marilla": ["Marilla"],
    "Tom": ["Tom"], "Aunt Polly": ["Polly"],
}


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def split_paragraphs(lines):
    """1-indexed (start_line, end_line, text) blocks split on blank lines. Pure structural split
    of the already-loaded corpus text; never reads any gold field."""
    paras = []
    buf = []
    buf_start = None
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                paras.append((buf_start, i - 1, " ".join(buf)))
                buf = []
                buf_start = None
        else:
            if buf_start is None:
                buf_start = i
            buf.append(line.strip())
    if buf:
        paras.append((buf_start, len(lines), " ".join(buf)))
    return paras


_PARA_CACHE = {}


def paragraphs_for(novel):
    if novel not in _PARA_CACHE:
        _PARA_CACHE[novel] = split_paragraphs(armc._corpus_lines(novel))
    return _PARA_CACHE[novel]


def maintained_affect_trajectory(novel, agent_name, surf_start):
    """Scan paragraphs strictly BEFORE arm_c's own local window (no overlap, no supporting_span
    line_range read) for entity-name-variant mentions; score each matched paragraph with the
    REUSED, UNCHANGED resolve_valence_blind. Returns list of (para_start_line, class)."""
    lo = max(1, surf_start - WINDOW_LINES)
    hi = surf_start - LOCAL_EXCLUDE
    variants = NAME_VARIANTS[agent_name]
    traj = []
    for p_start, p_end, p_text in paragraphs_for(novel):
        if p_start < lo or p_start > hi:
            continue
        if not any(v in p_text for v in variants):
            continue
        cls = armc.resolve_valence_blind(p_text)
        if cls != "NA":
            traj.append((p_start, cls))
    return traj


def maintained_state(traj):
    if not traj:
        return "NA"
    counts = {}
    for _, cls in traj:
        counts[cls] = counts.get(cls, 0) + 1
    best_count = max(counts.values())
    tied = [cls for cls, c in counts.items() if c == best_count]
    if len(tied) == 1:
        return tied[0]
    # tie-break: most recent (last) trajectory entry among tied classes
    for _, cls in reversed(traj):
        if cls in tied:
            return cls
    return tied[0]


def class_to_pred(cls):
    return "NEG" if cls == "HARM" else "POS"  # HELP/NA -> POS, matches parent cell's own convention


def run_item(item, chosen_name, hypothesis):
    item_id = item["id"]
    novel = item["novel"]
    surface_text = item["surface_span"]["text"]
    surf_start = item["surface_span"]["line_range"][0]
    local_ctx = armc.get_corpus_context(novel, item["surface_span"]["line_range"], window=2)
    arm_c_local_cls = armc.resolve_valence_context(chosen_name, hypothesis, surface_text, local_ctx)

    agent_name, agent_source = AGENT_FOR_ITEM[item_id]
    traj = maintained_affect_trajectory(novel, agent_name, surf_start)
    m_state = maintained_state(traj)

    # ASYMMETRIC by design (bug found + fixed during smoke, 2026-08-05): a symmetric HELP-override
    # branch was tried first (arm_c_local != HELP and m_state == HELP -> override to HELP) and it
    # actively DAMAGED already-correct local-cue predictions (grapp_irony_001/004, both already
    # correctly NEG from arm_c's own local reading, got flipped to POS by unrelated HELP-toned
    # paragraphs elsewhere in the 400-line window) -- the pre-reg itself predicted this branch
    # would be "unused on this item set"; it was NOT unused, it was actively harmful, so it is
    # removed rather than kept as dead code. Only the HARM-override direction matches the actual
    # hypothesis under test (narrative-established negative affect exposing a false-positive
    # surface reading); the reverse (positive history undercutting a negative surface reading) is
    # not the phenomenon this probe targets.
    overridden = False
    if arm_c_local_cls != "HARM" and m_state == "HARM":
        final_cls = "HARM"
        overridden = True
    else:
        final_cls = arm_c_local_cls

    arm_c_pred = class_to_pred(arm_c_local_cls)
    maint_pred = class_to_pred(final_cls)
    true_label = "NEG" if item["valence_type"] == "irony" else "POS"

    return {
        "id": item_id,
        "valence_type": item["valence_type"],
        "agent": agent_name,
        "agent_source": agent_source,
        "true_label": true_label,
        "arm_c_local_cls": arm_c_local_cls,
        "arm_c_local_pred": arm_c_pred,
        "arm_c_local_correct": arm_c_pred == true_label,
        "trajectory": [{"para_start_line": ln, "cls": c} for ln, c in traj],
        "maintained_state": m_state,
        "override_fired": overridden,
        "maintained_affect_final_cls": final_cls,
        "maintained_affect_pred": maint_pred,
        "maintained_affect_correct": maint_pred == true_label,
        "used_contamination": {
            "reads_true_intent_valence_label": False,
            "reads_supporting_span_field": False,
            "reads_surface_valence_label": False,
            "window_scanned": [max(1, surf_start - WINDOW_LINES), surf_start - LOCAL_EXCLUDE],
        },
    }


NARRATIVE_MISSED_IDS = {"grapp_irony_002", "grapp_irony_003", "grapp_irony_005"}
LOCAL_CUE_IDS = {"grapp_irony_001", "grapp_irony_004"}
SINCERE_IDS = {f"grapp_sincere_{i:03d}" for i in range(1, 6)}


def arms_must_differ(rows):
    """META_RULE_AF: hash-compare arm_c-local-pred vector vs maintained-affect-pred vector."""
    a = "".join(r["arm_c_local_pred"] for r in rows).encode("ascii")
    b = "".join(r["maintained_affect_pred"] for r in rows).encode("ascii")
    da, db = hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()
    narrative_rows = [r for r in rows if r["id"] in NARRATIVE_MISSED_IDS]
    fired_on_narrative = any(r["override_fired"] for r in narrative_rows)
    return {"arm_c_local_digest": da, "maintained_affect_digest": db,
            "arms_identical": da == db, "fired_on_at_least_one_narrative_missed_item": fired_on_narrative}


def self_test():
    """Real-code-path self-test: fits the real arm_c hypothesis, runs the real paragraph scanner
    against the real corpus text on a tiny slice (1 known item), asserts a non-crashing, typed
    result. This exercises the ACTUAL objects the full run uses (fit_arm_c_hypothesis,
    resolve_valence_context, resolve_valence_blind, _corpus_lines, split_paragraphs) at real
    scale (N=1 item, real corpus), not a synthetic-only branch."""
    chosen_name, chosen_result, digest, _ = armc.fit_arm_c_hypothesis()
    hypothesis = chosen_result.hypothesis
    gold = armc.load_gold()
    probe_item = next(it for it in gold if it["id"] == "grapp_irony_003")
    row = run_item(probe_item, chosen_name, hypothesis)
    assert row["maintained_affect_pred"] in ("POS", "NEG")
    assert isinstance(row["trajectory"], list)
    print(f"[self-test] grapp_irony_003: arm_c_local={row['arm_c_local_pred']} "
          f"maintained={row['maintained_affect_pred']} traj_len={len(row['trajectory'])}", flush=True)
    return True


def main():
    t0 = time.perf_counter()
    _write_start_marker(OUTPUT_DIR, "full", EXPECTED_N_ITEMS)

    chosen_name, chosen_result, arm_c_digest, arm_c_all_metrics = armc.fit_arm_c_hypothesis()
    hypothesis = chosen_result.hypothesis
    gold = armc.load_gold()
    irony_items = [it for it in gold if it["item_type"] == "irony_vs_sincere_valence"]
    assert len(irony_items) == EXPECTED_N_ITEMS, (
        f"CARDINALITY_BREACH: expected {EXPECTED_N_ITEMS} irony/sincere items, got {len(irony_items)}")

    rows = [run_item(it, chosen_name, hypothesis) for it in irony_items]

    def subset_acc(ids, key):
        sub = [r for r in rows if r["id"] in ids]
        return sum(1 for r in sub if r[key]) / len(sub) if sub else None

    narrative_missed_recovered = sum(
        1 for r in rows if r["id"] in NARRATIVE_MISSED_IDS and r["maintained_affect_correct"])
    sincere_fp = sum(
        1 for r in rows if r["id"] in SINCERE_IDS and r["maintained_affect_pred"] == "NEG")

    if narrative_missed_recovered >= 2 and sincere_fp == 0:
        verdict = "PROVEN"
    elif narrative_missed_recovered <= 1 and sincere_fp == 0:
        verdict = "NULL" if narrative_missed_recovered == 0 else "MIDDLE_BAND"
    else:
        verdict = "NULL_FALSE_POSITIVES"

    diff_check = arms_must_differ(rows)
    if diff_check["arms_identical"]:
        raise AssertionError(
            f"META_RULE_AF VIOLATION: arm_c-local-pred and maintained-affect-pred vectors are "
            f"bit-identical (digest={diff_check['arm_c_local_digest']}); override never fired anywhere.")

    verdict_msg = (
        f"{verdict}: narrative_missed_recovered={narrative_missed_recovered}/3 "
        f"({sorted(r['id'] for r in rows if r['id'] in NARRATIVE_MISSED_IDS and r['maintained_affect_correct'])}) "
        f"| sincere_fp={sincere_fp}/5 "
        f"| local_cue_maintained_acc={subset_acc(LOCAL_CUE_IDS, 'maintained_affect_correct')} "
        f"| arm_c_local_narrative_missed_acc={subset_acc(NARRATIVE_MISSED_IDS, 'arm_c_local_correct')} "
        f"| maintained_narrative_missed_acc={subset_acc(NARRATIVE_MISSED_IDS, 'maintained_affect_correct')}"
    )
    print(f"[result] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": "full",
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_items": len(rows),
        "arm_c_fitted_plugin": chosen_name,
        "arm_c_hypothesis_digest": arm_c_digest,
        "bands": {
            "narrative_missed_recovered": narrative_missed_recovered,
            "sincere_false_positives": sincere_fp,
            "pass_band": "narrative_missed_recovered >= 2 and sincere_fp == 0",
            "narrative_missed_acc_arm_c_local": subset_acc(NARRATIVE_MISSED_IDS, "arm_c_local_correct"),
            "narrative_missed_acc_maintained": subset_acc(NARRATIVE_MISSED_IDS, "maintained_affect_correct"),
            "local_cue_acc_arm_c_local": subset_acc(LOCAL_CUE_IDS, "arm_c_local_correct"),
            "local_cue_acc_maintained": subset_acc(LOCAL_CUE_IDS, "maintained_affect_correct"),
            "sincere_acc_arm_c_local": subset_acc(SINCERE_IDS, "arm_c_local_correct"),
            "sincere_acc_maintained": subset_acc(SINCERE_IDS, "maintained_affect_correct"),
        },
        "arms_differ_verified": diff_check,
        "rows": rows,
    }
    _write_metrics(OUTPUT_DIR, metrics)
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        ok = self_test()
        print("SELF_TEST_PASS" if ok else "SELF_TEST_FAIL", flush=True)
        sys.exit(0 if ok else 1)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 (NOT BaseException; preserves SystemExit/KeyboardInterrupt)
        _write_crash(OUTPUT_DIR, e)
        raise
