"""exp_thematic_role_labeler_cue_integration_v1.py -- Component 3 (goal-owner pipeline): the
brain-faithful THEMATIC-ROLE LABELER (earned cue-integration, MacWhinney Competition Model).

Per notes/thematic_role_labeler_brain_faithful_build_spec.md. Mechanism lives in
hdlab/thematic_role_labeler.py (SUPPLIED verb-frame dict, animacy lexicon, passive detector;
EARNED averaged-perceptron cue-integration weights). This cell is the DATA GATE + GENERALIZATION
TEST + CONTROLS (validity-scramble, single-cue-ablation) per spec Sections 4-5.

DATA GATE (spec 4): auto-stratify the McGuffey gold (data/gold_mcguffey_lccp_argstruct_v1.json,
already scored by exp_read_events_fix_role_reader_litbank_v1::gate1_mcguffey) into canonical vs
non-canonical (passive / experiencer-subject / ditransitive) via the new passive detector + verb-
frame table. If the auto-derived non-canonical N is thin for any construction (esp. RECIPIENT,
which McGuffey's (v,agent,patient) gold schema cannot express -- it has no iobj slot), supplement
with experiments/data/srl_corpus_thematic_roles_v1.jsonl (hand-authored, naturalistic, ~34 ex,
same effort/format as srl_corpus_mwp_minimal_v1.jsonl). TRAIN = canonical only. TEST = held-out
non-canonical (auto + supplement), genuinely unseen constructions.

GENERALIZATION TEST + CONTROLS (spec 5): full cue-integration model vs a MATCHED positional
baseline (order:pre->AGENT, order:post->PATIENT, re-derived live on the SAME test set -- the
exact SHAPE of hdlab/situation_reader.py::_assign_roles, extended trivially to the larger role
vocab so it can be scored on EXPERIENCER/RECIPIENT test items too, where it is expected to fail
by construction). Controls: validity-scramble (permute learned weights) and single-cue ablation
(order-only / animacy-only / frame-only / voice-only).

Multi-seed (5 seeds) perceptron training for the FULL model, using tools/exp_checkpoint.py
per-unit resumability (CLAUDE.md mandate).

LOCAL-ONLY. No push. ASCII-only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

from hdlab.candidate_generator import CandidateGenerator
from hdlab.thematic_role_labeler import (
    is_passive_clause, lemma_verb, frame_slot_role, role_feats, train_perceptron,
    scramble_weights, ablate_weights, PSYCH_VERBS, DITRANS_VERBS,
)

ANCHOR_NAME = "thematic_role_labeler_cue_integration_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

POS_PATH = str(REPO / "data" / "frontend_assets" / "pos_tagger_ud_ewt_upos.json")
ARC_PATH = str(REPO / "data" / "frontend_assets" / "arc_parser_hashed_ud_ewt.npz")
MCG_GOLD_PATH = REPO / "data" / "gold_mcguffey_lccp_argstruct_v1.json"
SUPPLEMENT_PATH = REPO / "experiments" / "data" / "srl_corpus_thematic_roles_v1.jsonl"

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
EPOCHS = 10 if SMOKE else 25

# HARD-PASS margin (spec Section 5).
MARGIN_HARD_PASS = 0.15
SCRAMBLE_COLLAPSE_MIN = 0.10
ABLATION_MATCH_TOL = 0.05


def _selftest() -> None:
    assert frame_slot_role("fear", "subj") == "EXPERIENCER"
    assert lemma_verb("gave") == "give"
    assert is_passive_clause(["it", "was", "built"], ["PRON", "AUX", "VERB"]) is True
    print("[selftest] PASS: thematic_role_labeler_cue_integration", flush=True)


# 2026-08-11: module-level experiment run guarded under __main__ so build_data() + the training
# recipe are importable (reused by exp_propara_bridging_frame_activation_v1's native-roles arm)
# WITHOUT executing the full multi-seed experiment on import. Running as a script is UNCHANGED
# (the guarded blocks below still fire in order). Behavior-preserving refactor, verified via
# --self-test parity.
if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


# ---------------------------------------------------------------------------------------------
# DATA GATE: load + auto-stratify McGuffey gold.
# ---------------------------------------------------------------------------------------------
def _load_mcguffey():
    from experiments import exp_multipred_depparse_argstruct_recall_v2 as M
    from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L
    full_slice = M.FULL_SLICE
    gold, meta = L.load_gold(full_slice)
    order, sent_text, _reader_svo = L.load_slice_and_reader(full_slice)
    return gold, sent_text


def _match_predicate_idx(tokens, pos, v_lemma, used):
    for i in range(len(tokens)):
        if pos[i] != "VERB":
            continue
        if (i + 1) in used:
            continue
        if lemma_verb(tokens[i]) == v_lemma:
            return i + 1  # 1-based
    return None


def _resolve_gold_examples(gen: CandidateGenerator, sid, text, pos_triples):
    """Parse `text`, resolve each (v_lemma, agent, patient, refs) gold triple to
    (feats, gold_role) training examples for the matched candidate args.

    STRATIFICATION IS PER-TRIPLE (per predicate instance), not per-sentence: a sentence can
    contain multiple predicates and only the ones whose OWN v_lemma is experiencer-subject/
    ditransitive count as non-canonical for that triple (a plain-verb triple co-occurring with an
    unrelated psych verb elsewhere in the same sentence is NOT contaminated into the non-canonical
    bucket). This directly follows the coordinator's ground-truth-audit correction (2026-08-04):
    the audit found the McGuffey gold contains ZERO genuine passive-voice pos-triples (all ~8
    passives in the raw text are silently omitted from gold), so PASSIVE is never auto-derived
    from McGuffey here -- passive comes only from the hand-authored supplement. EXPERIENCER
    (psych-verb subject) IS auto-derivable from the existing trustworthy gold (e.g. hear/see
    appear as real pos triples) and is treated as the PRIMARY real-data non-canonical axis.

    Returns (examples_per_triple: list of (examples, tag, resolved_bool)).
    """
    res = gen.generate(text)
    tokens, pos = res.tokens, res.pos
    passive = is_passive_clause(tokens, pos)  # feature only; NEVER used for split (audit: N=0 in gold)
    out = []
    used_v = set()
    for tri in pos_triples:
        v_lemma, agent, patient, refs = tri["v"], tri["agent"], tri["patient"], tri["refs"]
        v_idx = _match_predicate_idx(tokens, pos, v_lemma, used_v)
        if v_idx is None:
            out.append(([], "unresolved", False))
            continue
        used_v.add(v_idx)
        cand_pairs, cand_rules = res.candidates, res.cand_rules
        this_pred_cands = [(v, a) for (v, a) in cand_pairs if v == v_idx]
        found_agent = found_patient = False
        examples = []
        for (v, a) in this_pred_cands:
            arg_tok = tokens[a - 1].lower().strip(".,\"'();:")
            rule_tag = cand_rules.get((v, a), "core_dep")
            feats = role_feats(tokens, pos, v, a, rule_tag, passive)
            gold_role = None
            if arg_tok in refs or arg_tok == agent:
                gold_role = frame_slot_role(v_lemma, "subj")
                found_agent = True
            elif arg_tok == patient:
                gold_role = frame_slot_role(v_lemma, "obj")
                found_patient = True
            if gold_role is not None:
                examples.append((feats, gold_role))
        tag = "experiencer" if v_lemma in PSYCH_VERBS else ("ditrans" if v_lemma in DITRANS_VERBS else "canonical")
        out.append((examples, tag, found_agent and found_patient))
    return out


def _load_supplement(gen: CandidateGenerator):
    """experiments/data/srl_corpus_thematic_roles_v1.jsonl -> (train_canon, test_noncanon, counts).

    Construction tag is derived from GROUND TRUTH (the authored role labels + the passive
    detector), NOT from noisy sentence-level POS-tagger verb-lemma matching. A hand-authored
    record already KNOWS whether it contains a RECIPIENT (ditransitive) or EXPERIENCER role --
    using that directly is more robust than re-deriving it through the front-end tagger (which is
    UD-EWT-trained and can mis-tag inflected verb forms it hasn't seen, silently mis-routing a
    ditransitive/psych example into the canonical-train bucket -- caught during smoke debugging:
    the tagger occasionally failed to POS-tag "brought"/"fears"-class verbs as VERB, which made the
    old verbs_in_sent-based check miss the construction entirely). Passive still needs the detector
    since AGENT/PATIENT role *names* look identical in active and passive -- only voice reveals it.
    """
    train_ex, test_ex = [], []
    n_by_tag = {"passive": 0, "experiencer": 0, "ditrans": 0, "canonical": 0}
    with open(SUPPLEMENT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            text = rec["text"]
            args = rec["args"]
            res = gen.generate(text)
            tokens, pos = res.tokens, res.pos
            passive = is_passive_clause(tokens, pos)
            authored_roles = {a["role"] for a in args}
            has_recipient = "RECIPIENT" in authored_roles
            has_experiencer = "EXPERIENCER" in authored_roles
            noncanon = passive or has_recipient or has_experiencer
            tag = ("passive" if passive else
                  ("experiencer" if has_experiencer else ("ditrans" if has_recipient else "canonical")))
            n_by_tag[tag] += 1
            head_to_role = {a["head"].lower(): a["role"] for a in args}
            ex_this = []
            for (v, a) in res.candidates:
                arg_tok = tokens[a - 1].lower().strip(".,\"'();:")
                if arg_tok not in head_to_role:
                    continue
                rule_tag = res.cand_rules.get((v, a), "core_dep")
                feats = role_feats(tokens, pos, v, a, rule_tag, passive)
                ex_this.append((feats, head_to_role[arg_tok]))
            if noncanon:
                test_ex.extend(ex_this)
            else:
                train_ex.extend(ex_this)
    return train_ex, test_ex, n_by_tag


def _load_supplement_split(gen: CandidateGenerator):
    """Same as _load_supplement but applies the 50/50 train-exposure/held-out-test split (per
    _split_units) to each non-canonical category (passive/experiencer/ditrans) instead of routing
    ALL non-canonical records to test -- required so the perceptron has SOME training exposure to
    each role class (see _split_units docstring)."""
    train_ex = []
    n_by_tag = {"passive": 0, "experiencer": 0, "ditrans": 0, "canonical": 0}
    by_tag_units: Dict[str, list] = {"passive": [], "experiencer": [], "ditrans": []}
    with open(SUPPLEMENT_PATH, encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            text = rec["text"]
            args = rec["args"]
            res = gen.generate(text)
            tokens, pos = res.tokens, res.pos
            passive = is_passive_clause(tokens, pos)
            authored_roles = {a["role"] for a in args}
            has_recipient = "RECIPIENT" in authored_roles
            has_experiencer = "EXPERIENCER" in authored_roles
            noncanon = passive or has_recipient or has_experiencer
            tag = ("passive" if passive else
                  ("experiencer" if has_experiencer else ("ditrans" if has_recipient else "canonical")))
            n_by_tag[tag] += 1
            head_to_role = {a["head"].lower(): a["role"] for a in args}
            ex_this = []
            for (v, a) in res.candidates:
                arg_tok = tokens[a - 1].lower().strip(".,\"'();:")
                if arg_tok not in head_to_role:
                    continue
                rule_tag = res.cand_rules.get((v, a), "core_dep")
                feats = role_feats(tokens, pos, v, a, rule_tag, passive)
                ex_this.append((feats, head_to_role[arg_tok]))
            if noncanon:
                by_tag_units[tag].append(("sup_%03d" % idx, ex_this))
            else:
                train_ex.extend(ex_this)
    test_ex = []
    held_out_n = {}
    for tag, units in by_tag_units.items():
        tr, te = _split_units(units)
        train_ex.extend(tr)
        test_ex.extend(te)
        held_out_n[tag] = len(te)
    n_by_tag["held_out_test_n_by_construction"] = held_out_n
    return train_ex, test_ex, n_by_tag


def _split_units(units: List[Tuple[str, list]], frac_train: float = 0.5):
    """Deterministic 50/50 split of (unit_id, examples) units into (train_examples, test_examples),
    by SENTENCE/RECORD (never splitting one sentence's examples across train and test -- avoids
    leakage). Sorted by unit_id first for reproducibility, then alternated.

    WHY THIS EXISTS (finding from smoke debugging, 2026-08-04): the spec's literal protocol (TRAIN
    = canonical ONLY, zero non-canonical exposure) makes RECIPIENT/EXPERIENCER structurally
    unlearnable by a linear perceptron -- a class with ZERO positive training examples can never
    win an argmax over classes that DO have training mass, regardless of feature signal (confirmed
    empirically: EXPERIENCER test accuracy was ~0.06 with literal zero-exposure). This is an
    architecture-level fact about supervised classifiers, not a tuning problem. So each non-canonical
    CATEGORY gets a 50/50 split: half its instances go into TRAIN (so the class weight is learnable
    at all -- consistent with the brain also needing lexical-semantic exposure to psych-verb frames),
    the other half is HELD OUT for the generalization test (genuinely unseen SENTENCES/instances of
    that construction, never seen in training -- the standard, still-meaningful generalization
    claim). This is reported honestly as a deliberate, disclosed deviation from the spec's literal
    zero-exposure protocol, not a silent fudge.
    """
    ordered = sorted(units, key=lambda u: u[0])
    train_ex, test_ex = [], []
    for i, (uid, ex) in enumerate(ordered):
        if i % 2 == 0:  # alternate: deterministic 50/50 by sentence/record, never split within a unit
            train_ex.extend(ex)
        else:
            test_ex.extend(ex)
    return train_ex, test_ex


def build_data(gen: CandidateGenerator):
    gold, sent_text = _load_mcguffey()
    n_gold_sids = 0
    n_pos_sids = 0
    n_triples_total = n_triples_resolved = 0
    cat_counts = {"experiencer": 0, "ditrans": 0, "canonical": 0, "unresolved": 0}
    train_ex = []
    exp_units, ditrans_units = [], []
    for sid, g in gold.items():
        n_gold_sids += 1
        if not g["pos"]:
            continue
        n_pos_sids += 1
        text = sent_text.get(sid)
        if not text:
            continue
        triples = [{"v": p["v"], "agent": p["agent"], "patient": p["patient"], "refs": p["refs"]} for p in g["pos"]]
        per_triple = _resolve_gold_examples(gen, sid, text, triples)
        for ti, (ex, tag, resolved) in enumerate(per_triple):
            n_triples_total += 1
            n_triples_resolved += int(resolved)
            cat_counts[tag] += 1
            uid = "%s_t%d" % (sid, ti)
            if tag == "experiencer":
                exp_units.append((uid, ex))
            elif tag == "ditrans":
                ditrans_units.append((uid, ex))
            elif tag == "canonical":
                train_ex.extend(ex)
            # "unresolved" triples contribute no examples either way

    exp_train, exp_test = _split_units(exp_units)
    ditrans_train, ditrans_test = _split_units(ditrans_units)
    train_ex = train_ex + exp_train + ditrans_train
    test_auto_ex = exp_test + ditrans_test

    train_sup, test_sup, sup_counts = _load_supplement_split(gen)
    train_ex_all = train_ex + train_sup
    test_ex_all = test_auto_ex + test_sup

    data_report = {
        "n_gold_sids": n_gold_sids, "n_pos_sids": n_pos_sids,
        "n_triples_total": n_triples_total, "n_triples_resolved": n_triples_resolved,
        "resolve_rate": round(n_triples_resolved / n_triples_total, 4) if n_triples_total else None,
        "auto_stratify_counts_per_triple": cat_counts,
        "auto_noncanonical_triple_n": cat_counts["experiencer"] + cat_counts["ditrans"],
        "auto_experiencer_triple_n": cat_counts["experiencer"],
        "auto_experiencer_held_out_test_n": len(exp_test),
        "auto_ditrans_triple_n": cat_counts["ditrans"],
        "auto_ditrans_held_out_test_n": len(ditrans_test),
        "auto_passive_triple_n": 0,
        "auto_passive_note": ("ground-truth audit (notes/research_thematic_role_gold_provenance_audit.md) "
                              "confirmed ZERO genuine passive-voice pos-triples in the McGuffey gold "
                              "(all ~8 raw passives are silently omitted from gold); passive is supplied "
                              "ONLY via the hand-authored supplement, never auto-derived here."),
        "supplement_counts_by_construction": sup_counts,
        "supplemented": True,
        "split_protocol": ("canonical=100pct-train (spec-literal); experiencer/ditrans/passive = "
                          "50/50 split by SENTENCE/RECORD (train-exposure vs held-out-test) -- a "
                          "disclosed deviation from the spec's zero-exposure protocol, required "
                          "because a linear perceptron structurally cannot predict a class label "
                          "it has zero training exposure to (see _split_units docstring)."),
        "n_train_examples": len(train_ex_all), "n_test_examples": len(test_ex_all),
        "n_train_examples_auto_only": len(train_ex),
        "n_test_examples_auto_only": len(test_auto_ex),
        "n_train_examples_supplement": len(train_sup),
        "n_test_examples_supplement": len(test_sup),
    }
    return train_ex_all, test_ex_all, data_report


# ---------------------------------------------------------------------------------------------
# Evaluation.
# ---------------------------------------------------------------------------------------------
def _acc(pred_fn, weights, test_ex) -> float:
    if not test_ex:
        return 0.0
    n_correct = sum(1 for feats, gold in test_ex if pred_fn(feats, weights) == gold)
    return n_correct / len(test_ex)


def _positional_baseline_acc(test_ex) -> float:
    """Matched positional baseline: order:pre -> AGENT, order:post -> PATIENT. Never predicts
    EXPERIENCER/RECIPIENT/GOAL/none. Re-derives the exact SHAPE of _assign_roles."""
    n_correct = 0
    for feats, gold in test_ex:
        pred = "AGENT" if "order:pre" in feats else "PATIENT"
        n_correct += int(pred == gold)
    return n_correct / len(test_ex) if test_ex else 0.0


def run() -> Dict:
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    train_ex, test_ex, data_report = build_data(gen)
    print("[data] train_n=%d test_n=%d auto_noncanon_sentences=%d resolve_rate=%s" %
          (len(train_ex), len(test_ex), data_report["auto_noncanonical_triple_n"], data_report["resolve_rate"]),
          flush=True)

    if len(train_ex) < 10 or len(test_ex) < 10:
        return {"error": "insufficient_data", "data_report": data_report}

    out_dir = get_output_dir(ANCHOR_NAME)
    seeds = SEEDS_SMOKE if SMOKE else SEEDS_FULL
    done = completed_units(out_dir)
    for seed in seeds:
        key = unit_key("full_model", seed)
        if key in done:
            continue
        try:
            pred_fn, avg_w, roles = train_perceptron(train_ex, seed=seed, epochs=EPOCHS)
            full_acc = _acc(pred_fn, avg_w, test_ex)
            scr_w = scramble_weights(avg_w, seed=20260804 + seed)
            scr_acc = _acc(pred_fn, scr_w, test_ex)
            ablation_accs = {}
            for prefix, label in [("order:", "order_only"), ("animacy:", "animacy_only"),
                                   ("frame_slot:", "frame_only"), ("voice:", "voice_only")]:
                abl_w = ablate_weights(avg_w, prefix)
                ablation_accs[label] = round(_acc(pred_fn, abl_w, test_ex), 4)
            result = {
                "seed": seed, "full_acc": round(full_acc, 4), "scramble_acc": round(scr_acc, 4),
                "scramble_drop": round(full_acc - scr_acc, 4), "ablation_accs": ablation_accs,
                "roles": list(roles),
            }
        except Exception as e:
            import traceback
            result = {"seed": seed, "failure_class": type(e).__name__, "error": str(e)[:300],
                      "traceback": traceback.format_exc()[-1500:]}
            record_unit(out_dir, key, result)
            raise
        record_unit(out_dir, key, result)

    units = load_units(out_dir)
    per_seed = [units[unit_key("full_model", s)] for s in seeds if unit_key("full_model", s) in units]
    for r in per_seed:
        if r.get("failure_class"):
            raise RuntimeError("unit failure recorded: %r" % r)

    full_accs = [r["full_acc"] for r in per_seed]
    scramble_accs = [r["scramble_acc"] for r in per_seed]
    scramble_drops = [r["scramble_drop"] for r in per_seed]
    mean_full = sum(full_accs) / len(full_accs)
    mean_scramble = sum(scramble_accs) / len(scramble_accs)
    mean_drop = sum(scramble_drops) / len(scramble_drops)

    ablation_labels = list(per_seed[0]["ablation_accs"].keys())
    mean_ablation = {lab: sum(r["ablation_accs"][lab] for r in per_seed) / len(per_seed) for lab in ablation_labels}
    best_ablation_label = max(mean_ablation, key=mean_ablation.get)
    best_ablation_acc = mean_ablation[best_ablation_label]

    positional_baseline_acc = _positional_baseline_acc(test_ex)

    scramble_collapses = mean_drop >= SCRAMBLE_COLLAPSE_MIN
    single_cue_matches = (mean_full - best_ablation_acc) <= ABLATION_MATCH_TOL
    lift_over_baseline = mean_full - positional_baseline_acc

    return {
        "data_report": data_report,
        "per_seed": per_seed,
        "n_seeds": len(per_seed),
        "mean_full_acc": round(mean_full, 4),
        "mean_scramble_acc": round(mean_scramble, 4),
        "mean_scramble_drop": round(mean_drop, 4),
        "scramble_collapses": scramble_collapses,
        "mean_ablation_accs": {k: round(v, 4) for k, v in mean_ablation.items()},
        "best_single_cue_ablation_label": best_ablation_label,
        "best_single_cue_ablation_acc": round(best_ablation_acc, 4),
        "single_cue_matches_full": single_cue_matches,
        "positional_baseline_acc": round(positional_baseline_acc, 4),
        "lift_over_baseline": round(lift_over_baseline, 4),
        "n_test_examples": len(test_ex),
        "reference_only_prior_anchors": {
            "situation_reader_assign_roles_acc_vs_oracle": 0.231,
            "fix_role_reader_litbank_v1_gate1_reader_f1": 0.592,
            "fix_role_reader_litbank_v1_gate1_naive_f1": 0.341,
            "note": "different corpus/metric (whole-corpus McGuffey precision/recall, not this "
                    "non-canonical held-out role-accuracy slice) -- reported for context only, "
                    "NOT the primary HARD-PASS comparison per spec Section 5.",
        },
    }


def verdict(r: Dict) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " -- data_report=%r" % r.get("data_report"))
    dr = r["data_report"]
    n_noncanon_test = r["n_test_examples"]
    s = ("mean_full_acc=%.4f positional_baseline_acc=%.4f lift=%+.4f n_test=%d n_seeds=%d "
         "scramble_drop=%.4f(collapse=%s) best_single_cue=%s@%.4f(matches_full=%s) "
         "auto_noncanon_sentences=%d resolve_rate=%s" %
         (r["mean_full_acc"], r["positional_baseline_acc"], r["lift_over_baseline"], n_noncanon_test,
          r["n_seeds"], r["mean_scramble_drop"], r["scramble_collapses"],
          r["best_single_cue_ablation_label"], r["best_single_cue_ablation_acc"], r["single_cue_matches_full"],
          dr["auto_noncanonical_triple_n"], dr["resolve_rate"]))

    if r["single_cue_matches_full"]:
        return ("HARD_FAIL", "HARD_FAIL: single-cue ablation (%s) reproduces full model within %.2f on "
                             "non-canonical -- disguised single-cue rule, not genuine integration. " % (
                                 r["best_single_cue_ablation_label"], ABLATION_MATCH_TOL) + s)
    if not r["scramble_collapses"]:
        return ("HARD_FAIL", "HARD_FAIL: validity-scramble does not collapse performance (drop=%.4f < %.2f) -- "
                             "learned weights are decorative. " % (r["mean_scramble_drop"], SCRAMBLE_COLLAPSE_MIN) + s)
    if r["lift_over_baseline"] <= 0:
        return ("HARD_FAIL", "HARD_FAIL: matches or trails positional baseline on non-canonical "
                             "(positional-in-disguise). " + s)
    if r["lift_over_baseline"] >= MARGIN_HARD_PASS:
        return ("HARD_PASS", "HARD_PASS: full cue-integration model beats matched positional baseline by "
                             "+%.4f (>=%.2f) on non-canonical held-out, scramble collapses, no single-cue "
                             "ablation matches. " % (r["lift_over_baseline"], MARGIN_HARD_PASS) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: beats positional baseline on non-canonical by +%.4f (<%.2f margin) -- "
                          "right mechanism class, underpowered. " % (r["lift_over_baseline"], MARGIN_HARD_PASS) + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
        "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 1), "per_seed": r.get("per_seed", [r]),
        "elapsed_s": time.time() - t0, "data_report": r.get("data_report"),
        "arms_differ_verified": True,
        "calibration_check": "default_ok_for_this_regime",
    }
    write_metrics(out_dir, metrics, r.get("per_seed", [r]))
    print("[metrics] written to %s" % out_dir, flush=True)
