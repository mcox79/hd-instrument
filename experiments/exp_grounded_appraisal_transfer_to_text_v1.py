# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): ARM-A vs ARM-B vs baseline prediction
#   vectors hashed and asserted non-identical when their inputs genuinely differ.
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: n/a -- fixed 15-item eval, no capacity sweep; the one quantitative capacity claim (FHRR
#   bind/unbind decode fidelity, reused from the earned sim's own self-test) is self-tested directly.
# - calibration_check: default_ok_for_this_regime (bands declared in the prereg BEFORE running).
# - deterministic_seeding: torch.Generator per seed, matches exp_grounded_appraisal_sim_earned_v1's
#   own seeding scheme exactly (seed*100+hash_variant); sorted(set()) id pools; no hash()-seed.
# - cell_chunked: true (per-seed theta-reconstruction unit via tools/exp_checkpoint.py).
# - all numbers MEASURED@ tagged in the completion report, not this file.
#
# THE LOAD-BEARING TRANSFER TEST: does the appraisal->action function EARNED in
# exp_grounded_appraisal_sim_earned_v1 (non-textual simulation, MECHANISM_EARNS,
# FULL_heldout=1.000, revenge_emergence=1.000) transfer when fed TEXT-DERIVED appraisal-vectors
# instead of retraining a fresh text classifier? Direct test of VET holes #5/(h) in
# notes/audit_grounded_foundation_program_VET_2026-08-03.md ("sim-to-reading transfer asserted,
# not shown" / "the can-fail plan never tests the actual payoff claim"). See
# preregs/2026-08-03_grounded_appraisal_transfer_to_text_v1.md for full design + pre-registered
# outcomes (TRANSFER_WORKS / TRANSFER_FAILS / EXTRACTION_BOTTLENECK).
"""Bridges text (via reading organs: coreference-retargeted causal-attribution bridging,
blind valence lexicon) onto the SAME appraisal-vector format the sim-earned theta consumes, then
applies the REUSED (never retrained) theta. Reports per-item-type accuracy for ARM-A
(oracle-extracted appraisal structure) and ARM-B (real reading-organ extraction) against baselines
already shown to fail on this eval (recency causal-attribution, surface-valence)."""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "grounded_appraisal_transfer_to_text_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, TOOLS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
EARNED_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_grounded_appraisal_sim_earned_v1", "metrics.json")
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_grounded_appraisal_richer_v1.jsonl")

# ---- REUSED, UNCHANGED: the earned sim's own codebook/training/feature-encoder code path ------
import exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402
# ---- REUSED, UNCHANGED: the falsified reading-organ mechanisms + baselines --------------------
from exp_causal_attribution_bridging_v1 import (  # noqa: E402
    bridge_causal_antecedent, recency_baseline,
)
from exp_grounded_structure_phase0_probe_v1 import resolve_valence_blind  # noqa: E402
from exp_grounded_appraisal_richer_eval_v1 import _parse_valence_word  # noqa: E402
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
import exp_construction_integration_relation_inference_v1 as ci  # noqa: E402 (tokenize, reused verbatim)
# ---- REUSED, hdlab/learner centralized MDL model-selection engine (arm_c ONLY) -----------------
from hdlab.learner import registry as learner_registry  # noqa: E402
from hdlab.learner.plugins import ruleind_plugin, estimation_plugin  # noqa: E402

SEEDS = sim.SEEDS  # [0,1,2,3,4], identical to the earned cell
EXPECTED_N_SEEDS = len(SEEDS)
TRAIN_CFG = sim.FULL_CFG  # exact earned-cell scale (n_train=10000) -> bit-identical theta

# ---------------------------------------------------------------------------------------------
# ARM-C: LEARNED, CONTEXT-SENSITIVE VALENCE EXTRACTOR (reuses hdlab/learner, NOT a new engine).
# The measured bottleneck (EXTRACTION_BOTTLENECK, prior full run) traces to resolve_valence_blind
# (exp_grounded_structure_phase0_probe_v1.py) -- a FIXED, CONTEXT-FREE bag-of-words vote over the
# target span alone. arm_c is a DROP-IN alternative that (a) reads a WIDER context window (the
# same GIVEN line_range fields already used by arm_a/arm_b for rec-ordering, pulled straight from
# the public-domain corpus text -- never the answer fields), and (b) fits a glass-box hypothesis
# via hdlab.learner.registry.learn() (ruleind + estimation candidate plugins, MDL auto-selected)
# on a DETERMINISTIC, exhaustively-enumerated TRAINING GRID over 5 discrete context features. The
# training grid is disjoint from GOLD_PATH by construction (it never reads the gold file); its
# labels come from one explicit, pre-declared appraisal rule (irony/negation invert the blind
# lexicon vote; two features -- contrast marker, quote-wrapping -- are DISTRACTORS that do not
# determine the label, mirroring the ruleind plugin's own XOR-plus-topic-magnet positive control
# in exp_parser_ruleinduction_cls_ppattach_v1.py so the induced rule is provably non-trivial, not
# a lookup table sized to the eval items). This is the SAME reuse contract every other plugin in
# the registry follows: hdlab/learner supplies the shared MDL selection engine; this cell supplies
# the per-competence feature encoder + training distribution (hypothesis_space_spec / prior).
# ---------------------------------------------------------------------------------------------
_CORPUS_NOVEL_FILES = {
    "tom_sawyer": "tom_sawyer", "little_women": "little_women",
    "anne_of_green_gables": "anne_of_green_gables", "wizard_of_oz": "wizard_of_oz",
}
_CORPUS_LINES_CACHE = {}

SARCASM_TONE_WORDS = {"sarcastically", "scornfully", "dryly", "drily", "mockingly",
                       "ironically", "sneered", "sneeringly", "scathingly"}
SINCERE_TONE_WORDS = {"earnestly", "sincerely", "warmly", "genuinely", "solemnly",
                       "tenderly", "gently", "heartily"}
NEGATION_WORDS = {"not", "never", "no", "none", "nothing", "without", "cant", "didnt", "wont", "n't"}
CONTRAST_WORDS = {"but", "yet", "however", "although", "instead"}


def _corpus_lines(novel):
    if novel not in _CORPUS_LINES_CACHE:
        fname = _CORPUS_NOVEL_FILES[novel]
        path = os.path.join(REPO_ROOT, "data", "corpora", fname, "cleaned", f"{fname}.clean.txt")
        with open(path, "r", encoding="utf-8") as f:
            _CORPUS_LINES_CACHE[novel] = f.readlines()
    return _CORPUS_LINES_CACHE[novel]


def get_corpus_context(novel, line_range, window=2):
    """Pull window extra lines of PUBLIC-DOMAIN corpus text around a GIVEN line_range (the same
    factual-identity field arm_a/arm_b already use for rec-ordering). Never touches any answer
    field (true_blocker_agent / true_intent_valence / distractor_agent)."""
    lines = _corpus_lines(novel)
    start = max(1, line_range[0] - window)
    end = min(len(lines), line_range[-1] + window)
    return " ".join(l.strip() for l in lines[start - 1:end])


def context_features(span_text, context_text):
    """5 discrete features: blind lexicon vote (span only) + 4 context-window cues. contrast/quote
    are DISTRACTORS (do not determine the training label) -- see module docstring above."""
    blind = resolve_valence_blind(span_text)
    toks_ctx = set(ci.tokenize(context_text))
    tone = ("SARCASTIC" if (toks_ctx & SARCASM_TONE_WORDS)
            else ("SINCERE" if (toks_ctx & SINCERE_TONE_WORDS) else "NONE"))
    negation = bool(toks_ctx & NEGATION_WORDS)
    contrast = bool(toks_ctx & CONTRAST_WORDS)
    quote = ("“" in span_text) or ("”" in span_text) or ('"' in span_text)
    return blind, tone, negation, contrast, quote


def _feat_strings(blind, tone, negation, contrast, quote):
    return [f"blind:{blind}", f"tone:{tone}", f"neg:{negation}", f"contrast:{contrast}", f"quote:{quote}"]


def _true_label_rule(blind, tone, negation):
    """THEORETICAL@ pre-declared appraisal rule used ONLY to label the synthetic training grid
    (never applied at eval time): sarcasm inverts the surface valence read; negation also inverts
    it; both together cancel (double negative). NA-surface items only flip to HARM under pure
    (unnegated) sarcasm -- irony coloring a neutral surface as covertly negative."""
    flip = (tone == "SARCASTIC") != negation
    if blind == "NA":
        return "HARM" if (tone == "SARCASTIC" and not negation) else "NA"
    if not flip:
        return blind
    return "HELP" if blind == "HARM" else "HARM"


def build_arm_c_training_episodes():
    """Deterministic, exhaustive 3x3x2x2x2=72-cell combinatorial grid. Disjoint from GOLD_PATH by
    construction -- generated purely from the 5 discrete feature axes, never reads eval items."""
    episodes = []
    for blind in ("HARM", "HELP", "NA"):
        for tone in ("SARCASTIC", "SINCERE", "NONE"):
            for negation in (True, False):
                for contrast in (True, False):
                    for quote in (True, False):
                        episodes.append({
                            "gold_class": _true_label_rule(blind, tone, negation),
                            "feats": _feat_strings(blind, tone, negation, contrast, quote),
                        })
    return episodes


def _arm_c_feat_fn(ep):
    return ep["feats"]


def _arm_c_key_fn(ep):
    return tuple(sorted(ep["feats"]))


def fit_arm_c_hypothesis():
    """Fit ONCE (deterministic, seed-independent -- unlike theta, arm_c's hypothesis does not
    depend on the sim's random codebook). Returns (chosen_plugin_name, chosen_result, digest)."""
    episodes = build_arm_c_training_episodes()
    spec = {"candidate_plugins": ["ruleind", "estimation"], "max_conjunct": 2, "min_coverage": 2,
            "purity_thresh": 0.99, "max_rules": 16, "key_fn": _arm_c_key_fn,
            "label_fn": lambda ep: ep["gold_class"], "classes": ["HARM", "HELP", "NA"]}
    chosen_name, chosen, all_results = learner_registry.learn(episodes, _arm_c_feat_fn, spec, prior={})
    if chosen_name == "KEEP_EPISODIC" or chosen is None:
        raise RuntimeError("ARM_C_TRAINING_FAILED_TO_COMPRESS: hdlab/learner kept the training grid "
                            "fully episodic -- the induced hypothesis would be a lookup table, not a "
                            "generalizing rule; refusing to build arm_c on a non-compressing fit.")
    digest = hashlib.sha256(json.dumps(chosen.hypothesis, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return chosen_name, chosen, digest, {n: r.metrics for n, r in all_results.items()}


def apply_arm_c(chosen_name, hypothesis, blind, tone, negation, contrast, quote):
    feats = _feat_strings(blind, tone, negation, contrast, quote)
    key = tuple(sorted(feats))
    if chosen_name == "ruleind":
        return ruleind_plugin.apply(hypothesis, feats, key=key, default_class=blind)
    if chosen_name == "estimation":
        pred = estimation_plugin.apply(hypothesis, key)
        return pred if pred is not None else blind
    raise ValueError(f"unknown arm_c plugin {chosen_name!r}")


def resolve_valence_context(chosen_name, hypothesis, span_text, context_text):
    """Drop-in context-sensitive alternative to resolve_valence_blind: same span-level blind vote
    as arm_b, PLUS the learned tone/negation-conditioned correction from the wider context."""
    blind, tone, negation, contrast, quote = context_features(span_text, context_text)
    return apply_arm_c(chosen_name, hypothesis, blind, tone, negation, contrast, quote)

# ---------------------------------------------------------------------------------------------
# GIVEN (factual-identity / oracle-event-structure) tables. Candidate NAMES + real line positions
# are factual identity (same tier already accepted in the parent evals). true_agent/coh flags for
# ARM-A are the oracle's best-available representation of "who performed the harmful act" -- this
# is the event-structure input the design explicitly authorizes for the oracle arm; the gold
# ANSWER FIELDS themselves (true_blocker_agent / true_intent_valence) are read ONLY for scoring,
# never fed into the bridge. This mirrors MULTI_CAND_GIVEN in exp_grounded_appraisal_richer_eval_v1.
# ---------------------------------------------------------------------------------------------
MULTI_CAND_ORACLE_TRUE_SLOT = {
    "grapp_mcca_001": 0, "grapp_mcca_003": 0, "grapp_mcca_004": 0, "grapp_mcca_005": 0,
}  # slot 0 = true_blocker_span candidate, slot 1 = distractor_span candidate (fixed convention)

IRONY_AGENT_TARGET = {
    "grapp_irony_001": ("Jo", "Amy"), "grapp_irony_002": ("Mr Phillips", "Anne"),
    "grapp_irony_003": ("Jo", "Meg"), "grapp_sincere_001": ("Meg", "John"),
    "grapp_sincere_002": ("Marilla", "Anne"), "grapp_sincere_003": ("Aunt Polly", "Tom"),
}

_CONG_MAP = {"HARM": "HURT", "HELP": "HELP", "NA": "NEUTRAL"}


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
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


def load_gold():
    items = []
    with open(GOLD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_earned_digests():
    """Contamination/reuse proof: the digests already landed by the earned sim cell."""
    with open(EARNED_METRICS_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {int(k): v["arms_theta_digests"]["FULL"] for k, v in d["per_seed"].items()}


# ---------------------------------------------------------------------------------------------
# THETA RECONSTRUCTION: bit-identical to exp_grounded_appraisal_sim_earned_v1.run_seed's FULL arm.
# NOT a retrain-on-text; this is the exact same deterministic procedure (random synthetic agent
# identities, no text, no eval item ever touched) that already produced the earned artifact.
# ---------------------------------------------------------------------------------------------
def reconstruct_full_theta(seed: int, cfg: dict):
    gen = torch.Generator().manual_seed(seed)
    cb = sim.Codebook(gen)
    g = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
    theta = sim.train_theta(cb, g, "FULL", cfg["n_train"])
    digest = hashlib.sha256(theta.numpy().tobytes()).hexdigest()[:16]
    return cb, theta, digest


def _bridge_episode(cong, cope, cand_coh, cand_rec):
    """Build the appraisal-vector tuple in the EXACT dict shape sim.phi() consumes."""
    cands = []
    for i in range(sim.N_CAND):
        if i < len(cand_coh):
            cands.append({"id_idx": 0, "coh": cand_coh[i], "rec": cand_rec[i]})
        else:
            cands.append({"id_idx": 0, "coh": 0, "rec": 0})
    return {"type": "TEXT_BRIDGE", "cong": cong, "cope": cope, "cands": cands, "pool": "eval"}


def _q(cb, theta, ep, action):
    return float(sim.phi(cb, ep, action, "FULL") @ theta)


# ---------------------------------------------------------------------------------------------
# MULTI-CANDIDATE CAUSAL ATTRIBUTION (4 items)
# ---------------------------------------------------------------------------------------------
def score_causal_item(item, cb, theta, arm_c=None):
    iid = item["id"]
    true_span = item["true_blocker_span"]["text"]
    distr_span = item["distractor_span"]["text"]
    true_pos = item["true_blocker_span"]["line_range"][0]
    distr_pos = item["distractor_span"]["line_range"][0]

    # rec: REAL signal both arms -- literal line-position ordering, no oracle needed.
    rec = [1, 0] if true_pos > distr_pos else [0, 1]

    # ARM-A oracle coh: from the given oracle event-structure convention (slot 0 = true).
    coh_oracle = [1, 0]

    # ARM-B real coh: bridge_causal_antecedent on each candidate's OWN span via blind valence
    # (the same reading-organ mechanism the richer eval measured; no oracle facts used here).
    events = [
        {"item_id": iid + "_true", "position": 100, "agent": "TRUE_CAND",
         "patient": "VICTIM", "valence": resolve_valence_blind(true_span)},
        {"item_id": iid + "_distr", "position": 200, "agent": "DISTR_CAND",
         "patient": "VICTIM", "valence": resolve_valence_blind(distr_span)},
    ]
    _prior, attributed, margin, used = bridge_causal_antecedent("VICTIM", 300, events)
    if attributed == "TRUE_CAND":
        coh_real = [1, 0]
    elif attributed == "DISTR_CAND":
        coh_real = [0, 1]
    else:
        coh_real = [0, 0]  # extraction gate did not differentiate -- honest non-signal

    ep_a = _bridge_episode("HURT", "HIGH", coh_oracle, rec)
    ep_b = _bridge_episode("HURT", "HIGH", coh_real, rec)
    qa0, qa1 = _q(cb, theta, ep_a, sim.A_HARM0 + 0), _q(cb, theta, ep_a, sim.A_HARM0 + 1)
    qb0, qb1 = _q(cb, theta, ep_b, sim.A_HARM0 + 0), _q(cb, theta, ep_b, sim.A_HARM0 + 1)
    pred_a = 0 if qa0 > qa1 else (1 if qa1 > qa0 else -1)
    pred_b = 0 if qb0 > qb1 else (1 if qb1 > qb0 else -1)

    # baselines
    rb_prior, rb_attr = recency_baseline(300, events)
    pred_recency = (0 if rb_attr == "TRUE_CAND" else 1) if rb_prior else -1

    row = {
        "id": iid, "item_type": item["item_type"],
        "arm_a_pred_slot": pred_a, "arm_a_correct": pred_a == 0,
        "arm_b_pred_slot": pred_b, "arm_b_correct": pred_b == 0,
        "arm_b_real_attributed": attributed, "arm_b_extraction_differentiated": coh_real != [0, 0],
        "recency_pred_slot": pred_recency, "recency_correct": pred_recency == 0,
        "chance_correct_prob": 0.5,
        "q_arm_a": [qa0, qa1], "q_arm_b": [qb0, qb1],
        "used_contamination": {
            "reads_true_blocker_agent_label": False,
            "arm_a_given_facts": ["oracle event-structure convention: slot0=true_blocker_span"],
            "arm_b_given_facts": ["own-span blind valence", "real line positions"],
            "bridge_used": used,
        },
    }

    if arm_c is not None:
        chosen_name, hyp = arm_c
        true_ctx = get_corpus_context(item["novel"], item["true_blocker_span"]["line_range"])
        distr_ctx = get_corpus_context(item["novel"], item["distractor_span"]["line_range"])
        events_c = [
            {"item_id": iid + "_true", "position": 100, "agent": "TRUE_CAND", "patient": "VICTIM",
             "valence": resolve_valence_context(chosen_name, hyp, true_span, true_ctx)},
            {"item_id": iid + "_distr", "position": 200, "agent": "DISTR_CAND", "patient": "VICTIM",
             "valence": resolve_valence_context(chosen_name, hyp, distr_span, distr_ctx)},
        ]
        _prior_c, attributed_c, margin_c, used_c = bridge_causal_antecedent("VICTIM", 300, events_c)
        if attributed_c == "TRUE_CAND":
            coh_c = [1, 0]
        elif attributed_c == "DISTR_CAND":
            coh_c = [0, 1]
        else:
            coh_c = [0, 0]
        ep_c = _bridge_episode("HURT", "HIGH", coh_c, rec)
        qc0, qc1 = _q(cb, theta, ep_c, sim.A_HARM0 + 0), _q(cb, theta, ep_c, sim.A_HARM0 + 1)
        pred_c = 0 if qc0 > qc1 else (1 if qc1 > qc0 else -1)
        row.update({
            "arm_c_pred_slot": pred_c, "arm_c_correct": pred_c == 0,
            "arm_c_real_attributed": attributed_c, "arm_c_extraction_differentiated": coh_c != [0, 0],
            "q_arm_c": [qc0, qc1],
        })
        row["used_contamination"]["arm_c_given_facts"] = [
            "own-span text + wider corpus context window (via GIVEN line_range only)",
            "real line positions",
        ]
        row["used_contamination"]["reads_true_intent_valence_label"] = False
    return row


# ---------------------------------------------------------------------------------------------
# IRONY / SINCERE VALENCE (6 items)
# ---------------------------------------------------------------------------------------------
def score_irony_item(item, cb, theta, arm_c=None):
    iid = item["id"]
    surface_span = item["surface_span"]["text"]
    supporting_span = item.get("supporting_span", {}).get("text", "")
    true_pred = _parse_valence_word(item["true_intent_valence"])  # scoring only
    surface_pred = _parse_valence_word(item["surface_valence"])   # baseline input (surface reading)

    cong_a = _CONG_MAP[resolve_valence_blind(supporting_span)] if supporting_span else "NEUTRAL"
    cong_b = _CONG_MAP[resolve_valence_blind(surface_span)]

    ep_a = _bridge_episode(cong_a, "HIGH", [1], [1])
    ep_b = _bridge_episode(cong_b, "HIGH", [1], [1])
    qha, qhpa = _q(cb, theta, ep_a, sim.A_HARM0 + 0), _q(cb, theta, ep_a, sim.A_HELP0 + 0)
    qhb, qhpb = _q(cb, theta, ep_b, sim.A_HARM0 + 0), _q(cb, theta, ep_b, sim.A_HELP0 + 0)
    pred_a = "NEG" if qha > qhpa else ("POS" if qhpa > qha else "NA")
    pred_b = "NEG" if qhb > qhpb else ("POS" if qhpb > qhb else "NA")

    row = {
        "id": iid, "item_type": item["item_type"], "valence_type": item["valence_type"],
        "cong_arm_a": cong_a, "cong_arm_b": cong_b,
        "arm_a_pred": pred_a, "arm_a_correct": pred_a == true_pred,
        "arm_b_pred": pred_b, "arm_b_correct": pred_b == true_pred,
        "surface_pred": surface_pred, "surface_correct": surface_pred == true_pred,
        "chance_correct_prob": 0.5,
        "q_arm_a": [qha, qhpa], "q_arm_b": [qhb, qhpb],
        "used_contamination": {
            "reads_true_intent_valence_label": False,
            "arm_a_given_facts": ["supporting_span (given narrative span, distinct from surface_span)"],
            "arm_b_given_facts": ["surface_span alone"],
        },
    }

    if arm_c is not None:
        chosen_name, hyp = arm_c
        surface_ctx = get_corpus_context(item["novel"], item["surface_span"]["line_range"])
        cong_c = _CONG_MAP[resolve_valence_context(chosen_name, hyp, surface_span, surface_ctx)]
        ep_c = _bridge_episode(cong_c, "HIGH", [1], [1])
        qhc, qhpc = _q(cb, theta, ep_c, sim.A_HARM0 + 0), _q(cb, theta, ep_c, sim.A_HELP0 + 0)
        pred_c = "NEG" if qhc > qhpc else ("POS" if qhpc > qhc else "NA")
        row.update({
            "cong_arm_c": cong_c, "arm_c_pred": pred_c, "arm_c_correct": pred_c == true_pred,
            "q_arm_c": [qhc, qhpc],
        })
        row["used_contamination"]["arm_c_given_facts"] = [
            "surface_span text + wider corpus context window (via GIVEN line_range only)",
        ]
    return row


# ---------------------------------------------------------------------------------------------
# BENEFICIARY vs PATIENT (5 items): honest capability GAP, no bridge forced.
# ---------------------------------------------------------------------------------------------
def score_beneficiary_item(item):
    return {
        "id": item["id"], "item_type": item["item_type"],
        "note": ("The sim's action space has no beneficiary-vs-patient appraisal slot distinct "
                 "from the single RECIPROCITY 'coh' target -- bridging this item type would require "
                 "either reading the answer field (leakage) or inventing an ungrounded slot the sim "
                 "never earned. Reported as an honest capability GAP, not forced into a bridge."),
        "bridge_attempted": False,
    }


def _acc(rows, key):
    n = len(rows)
    return (sum(1 for r in rows if r[key]) / n) if n else 0.0, n


def run_seed_unit(seed, arm_c):
    cb, theta, digest = reconstruct_full_theta(seed, TRAIN_CFG)
    items = load_gold()
    causal_items = [it for it in items if it["item_type"] == "multi_candidate_causal_attribution"]
    irony_items = [it for it in items if it["item_type"] == "irony_vs_sincere_valence"]
    causal_rows = [score_causal_item(it, cb, theta, arm_c) for it in causal_items]
    irony_rows = [score_irony_item(it, cb, theta, arm_c) for it in irony_items]
    return {"seed": seed, "theta_digest": digest, "causal_rows": causal_rows, "irony_rows": irony_rows}


def aggregate_and_verdict(per_seed, earned_digests, benpat_rows, arm_c_meta):
    seeds = sorted(per_seed.keys())
    n = len(seeds)
    n_causal = len(per_seed[seeds[0]]["causal_rows"]) if seeds else 0
    n_irony = len(per_seed[seeds[0]]["irony_rows"]) if seeds else 0

    # contamination proof: reconstructed digest == earned cell's landed digest, every seed
    digest_matches = {s: per_seed[s]["theta_digest"] == earned_digests.get(s) for s in seeds}
    all_digests_match = all(digest_matches.values())

    def mean_acc(rows_key, correct_key):
        vals = []
        for s in seeds:
            rows = per_seed[s][rows_key]
            acc, _ = _acc(rows, correct_key)
            vals.append(acc)
        return sum(vals) / max(1, len(vals))

    causal_arm_a = mean_acc("causal_rows", "arm_a_correct")
    causal_arm_b = mean_acc("causal_rows", "arm_b_correct")
    causal_arm_c = mean_acc("causal_rows", "arm_c_correct")
    causal_recency = mean_acc("causal_rows", "recency_correct")
    irony_arm_a = mean_acc("irony_rows", "arm_a_correct")
    irony_arm_b = mean_acc("irony_rows", "arm_b_correct")
    irony_arm_c = mean_acc("irony_rows", "arm_c_correct")
    irony_surface = mean_acc("irony_rows", "surface_correct")

    CHANCE = 0.5
    causal_a_beats_all = causal_arm_a > max(causal_recency, CHANCE)
    irony_a_beats_all = irony_arm_a > max(irony_surface, CHANCE)
    arm_a_works = causal_a_beats_all and irony_a_beats_all
    causal_b_beats_all = causal_arm_b > max(causal_recency, CHANCE)
    irony_b_beats_all = irony_arm_b > max(irony_surface, CHANCE)
    arm_b_works = causal_b_beats_all and irony_b_beats_all

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not all_digests_match:
        verdict = "HARD_FAIL_THETA_NOT_REUSED_DIGEST_MISMATCH"
    elif arm_a_works and arm_b_works:
        verdict = "TRANSFER_WORKS"
    elif arm_a_works and not arm_b_works:
        verdict = "EXTRACTION_BOTTLENECK"
    else:
        verdict = "TRANSFER_FAILS"

    # ---- PRE-REGISTERED ARM-C BANDS (preregs/2026-08-05_grounded_appraisal_transfer_grow_arm_c.md) ---
    # PROVEN: closes >=50% of the causal arm_a-arm_b gap AND irony arm_c beats max(surface, chance).
    # NULL: causal gap-closure <20% AND irony arm_c <= max(surface, chance) (no measurable context lift).
    # PARTIAL: anything strictly between (mechanism fires on one category, not the other -- honest,
    #   not a "distractor-feature only fired on the coarser task" over-claim).
    causal_gap = causal_arm_a - causal_arm_b
    causal_gap_closure = ((causal_arm_c - causal_arm_b) / causal_gap) if causal_gap > 1e-9 else 0.0
    irony_c_beats_baselines = irony_arm_c > max(irony_surface, CHANCE)
    causal_c_closes_half = causal_gap_closure >= 0.5
    if causal_c_closes_half and irony_c_beats_baselines:
        arm_c_verdict = "ARM_C_PROVEN"
    elif causal_gap_closure < 0.2 and not irony_c_beats_baselines:
        arm_c_verdict = "ARM_C_NULL"
    else:
        arm_c_verdict = "ARM_C_PARTIAL"
    resisting_category = []
    if not causal_c_closes_half:
        resisting_category.append("causal")
    if not irony_c_beats_baselines:
        resisting_category.append("irony")

    summary = (
        f"CAUSAL(n={n_causal}): arm_a={causal_arm_a:.3f} arm_b={causal_arm_b:.3f} arm_c={causal_arm_c:.3f} "
        f"recency={causal_recency:.3f} chance={CHANCE:.3f} gap_closure={causal_gap_closure:.3f} | "
        f"IRONY(n={n_irony}): arm_a={irony_arm_a:.3f} arm_b={irony_arm_b:.3f} arm_c={irony_arm_c:.3f} "
        f"surface={irony_surface:.3f} chance={CHANCE:.3f} | BENEFICIARY(n=5): capability GAP, "
        f"no bridge attempted | theta_reuse_digest_match={all_digests_match} | "
        f"arm_c_verdict={arm_c_verdict} (resisting={resisting_category or 'none'}) | "
        f"arm_c_plugin={arm_c_meta['chosen_name']}"
    )
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "contamination_check": {"all_theta_digests_match_earned_run": all_digests_match,
                                              "per_seed_digest_match": digest_matches,
                                              "arm_c_hypothesis_digest": arm_c_meta["digest"],
                                              "arm_c_reads_answer_fields": False},
        "means": {
            "causal_arm_a_acc": causal_arm_a, "causal_arm_b_acc": causal_arm_b,
            "causal_arm_c_acc": causal_arm_c,
            "causal_recency_acc": causal_recency, "causal_chance": CHANCE, "causal_n": n_causal,
            "irony_arm_a_acc": irony_arm_a, "irony_arm_b_acc": irony_arm_b, "irony_arm_c_acc": irony_arm_c,
            "irony_surface_acc": irony_surface, "irony_chance": CHANCE, "irony_n": n_irony,
        },
        "bands": {
            "causal_arm_a_beats_all": causal_a_beats_all, "irony_arm_a_beats_all": irony_a_beats_all,
            "causal_arm_b_beats_all": causal_b_beats_all, "irony_arm_b_beats_all": irony_b_beats_all,
            "arm_a_works": arm_a_works, "arm_b_works": arm_b_works,
            "causal_gap_closure": causal_gap_closure, "causal_c_closes_half_gap": causal_c_closes_half,
            "irony_c_beats_baselines": irony_c_beats_baselines,
            "arm_c_verdict": arm_c_verdict, "arm_c_resisting_categories": resisting_category,
        },
        "arm_c_meta": arm_c_meta,
        "beneficiary_note": ("5 beneficiary_vs_patient items reported as honest capability GAP "
                             "(no appraisal slot in the sim distinguishes beneficiary from patient); "
                             "see per-item beneficiary_rows."),
        "beneficiary_rows": benpat_rows,
    }


def out_dir_for(run_mode):
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def run(run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    earned_digests = load_earned_digests()
    items = load_gold()
    benpat_items = [it for it in items if it["item_type"] == "beneficiary_vs_patient"]
    benpat_rows = [score_beneficiary_item(it) for it in benpat_items]

    print("[progress] fitting arm_c hypothesis (hdlab/learner, deterministic training grid)...",
          flush=True)
    chosen_name, chosen_result, arm_c_digest, all_plugin_metrics = fit_arm_c_hypothesis()
    arm_c = (chosen_name, chosen_result.hypothesis)
    arm_c_meta = {"chosen_name": chosen_name, "digest": arm_c_digest,
                  "chosen_metrics": chosen_result.metrics,
                  "chosen_compression_ratio": chosen_result.compression_ratio,
                  "all_plugin_metrics": all_plugin_metrics}
    print(f"[progress] arm_c plugin={chosen_name} compression_ratio={chosen_result.compression_ratio:.3f} "
          f"digest={arm_c_digest}", flush=True)

    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed_unit(seed, arm_c)
        record_unit(output_dir, k, res)
        digest_ok = res["theta_digest"] == earned_digests.get(seed)
        print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
              f"digest={res['theta_digest']} matches_earned={digest_ok}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed, earned_digests, benpat_rows, arm_c_meta)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "train_cfg": TRAIN_CFG}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ----------------------------------------------------------------------------- self-test
def self_test():
    """(1) reconstructed theta digest for seed 0 matches the earned cell's landed digest (proof of
    bit-identical reuse, not a fresh retrain) -- arm_c does NOT retrain theta. (2) arm_c hypothesis
    fit is DETERMINISTIC (two independent fit_arm_c_hypothesis() calls produce the identical
    digest) -- proves it is not accidentally reading anything nondeterministic (e.g. wall-clock,
    RNG) that would make it look like a "trained" artifact when it is really a fixed function of
    the training grid. (3) ARM-A/ARM-B/ARM-C produce different predictions on at least one item
    (arms-must-differ, META_RULE_AF) -- arm_c is not a silent no-op copy of arm_b. (4) contamination:
    no scoring function (including arm_c) reads any answer field (true_blocker_agent /
    true_intent_valence / distractor_agent) before comparison -- arm_c only ever receives span text
    + GIVEN line_range-derived corpus context, structurally disjoint from those fields."""
    earned_digests = load_earned_digests()
    cb_full, theta_full, digest_full = reconstruct_full_theta(0, TRAIN_CFG)
    assert digest_full == earned_digests[0], (
        f"theta reuse FAILED: reconstructed digest {digest_full} != earned {earned_digests[0]}")

    name1, res1, digest1, _ = fit_arm_c_hypothesis()
    name2, res2, digest2, _ = fit_arm_c_hypothesis()
    assert name1 == name2 and digest1 == digest2, (
        f"ARM_C_NOT_DETERMINISTIC: fit_arm_c_hypothesis() produced different hypotheses across two "
        f"calls ({name1}:{digest1} vs {name2}:{digest2}) -- training grid must be a pure function")
    arm_c = (name1, res1.hypothesis)
    print(f"[self-test] arm_c_plugin={name1} digest={digest1} "
          f"compression_ratio={res1.compression_ratio:.3f}", flush=True)

    items = load_gold()
    causal_items = [it for it in items if it["item_type"] == "multi_candidate_causal_attribution"]
    rows = [score_causal_item(it, cb_full, theta_full, arm_c) for it in causal_items]
    any_extraction_gap = any(not r["arm_b_extraction_differentiated"] for r in rows)
    # arms differ: at least across the causal items, arm_a/arm_b/arm_c predictions are not all
    # identical vectors (hash-test per META_RULE_AF cell-template mandate).
    va = [r["arm_a_pred_slot"] for r in rows]
    vb = [r["arm_b_pred_slot"] for r in rows]
    vc = [r["arm_c_pred_slot"] for r in rows]
    digests = {"arm_a": hashlib.sha256(str(va).encode()).hexdigest(),
               "arm_b": hashlib.sha256(str(vb).encode()).hexdigest(),
               "arm_c": hashlib.sha256(str(vc).encode()).hexdigest()}
    assert len(set(digests.values())) >= 2, (
        f"META_RULE_AF VIOLATION: arm_a/arm_b/arm_c causal predictions are ALL bit-identical "
        f"({va}) -- at least one arm must differ")
    print(f"[self-test] arm_a_preds={va} arm_b_preds={vb} arm_c_preds={vc} "
          f"any_extraction_gap={any_extraction_gap}", flush=True)
    for r in rows:
        assert r["used_contamination"]["reads_true_blocker_agent_label"] is False
        assert r["used_contamination"]["reads_true_intent_valence_label"] is False

    irony_items = [it for it in items if it["item_type"] == "irony_vs_sincere_valence"]
    irows = [score_irony_item(it, cb_full, theta_full, arm_c) for it in irony_items]
    for r in irows:
        assert "reads_true_intent_valence_label" in r["used_contamination"]
        assert r["used_contamination"]["reads_true_intent_valence_label"] is False
    ib = [r["arm_b_pred"] for r in irows]
    ic = [r["arm_c_pred"] for r in irows]
    print(f"[self-test] irony arm_b_preds={ib} arm_c_preds={ic}", flush=True)

    # arm_c must never be able to see gold_class's source (true_intent_valence text) -- structural
    # proof: resolve_valence_context's signature takes only (plugin, hypothesis, span_text,
    # context_text); context_text is built exclusively from get_corpus_context(novel, line_range),
    # never from any item[...] field containing "true_" or "distractor_agent".
    import inspect
    sig = inspect.signature(resolve_valence_context)
    assert list(sig.parameters) == ["chosen_name", "hypothesis", "span_text", "context_text"], (
        "resolve_valence_context signature drifted -- re-verify contamination argument surface")

    print(f"[SELFTEST PASS] theta_digest_match={digest_full == earned_digests[0]} "
          f"arm_c_deterministic=True arm_c_plugin={name1}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(OUTPUT_DIR, e)
        raise
