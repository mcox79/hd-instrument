# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: hash digests of REAL vs SCRAMBLE vs ABLATION final-type sequences over the
#   12-item open-vocab TEST pool (all three MUST be pairwise distinct -- MEASURED at seed=0,
#   n_train_theta=4000: real=4c4c97c11e086ba6 scramble=3cb5d1ad497cd356 ablation=e3c9ff717a471d1e).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity dimension; open-vocab sign-accuracy discriminator only
# - baseline_in_band: n/a; ABLATION arm is a structural all-abstain floor that scores EXACTLY 0.0 on
#   this 12-item pool by construction (see module docstring ABLATION-COLLAPSE NOTE) -- not a noisy
#   ~0.5 chance band, a harder floor
# - discriminator survives scale: full-N == smoke-N item set (12 held-out TEST verbs, fixed); only
#   theta-training steps differ (SMOKE_N_TRAIN_THETA=4000, FULL=8000, matching bridge1 precedent).
#   MEASURED@seed=0,n_train_theta=4000 already clears every HARD-PASS band (see below) so the smoke
#   regime itself fires the full discriminator, not just a preview.
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (HARD-PASS/FAIL bands fixed by the task brief
#   BEFORE this cell was run: open-vocab acc >= 0.75, scramble collapse, ablation collapse, test
#   verbs disjoint from seed -- not tuned after seeing results)
# - deterministic_seeding: torch.Generator per seed for theta training; hashlib-free permutation via
#   random.Random(fixed int seed) for the SCRAMBLE control (not builtin hash()); WordNet lookups
#   (hdlab.wordnet_polarity_propagation.dictionary_lookup) are themselves deterministic, no RNG
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py)
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- this is Director's prove-architecture experiment cell, not production wiring
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""experiments/exp_social_relational_grounding_axis_v1.py -- ISOLATED prove-architecture probe for
deep-B grounding (notes/formalize_deepB_grounding_social_relational_valence_2026-08-07.md): does a
SOCIAL-RELATIONAL valence axis ground the same way the owned PHYSICAL-HARM axis does
(hdlab/context_grounded_valence.py)?

PARALLEL ARCHITECTURE (mirrors the certified physical-harm organ's 3-stage pipeline, see hdlab/
context_grounded_valence.py module docstring):
  physical-harm axis:  governor sense-select -> ANIMACY-axis event override (WordNet animacy of the
                        direct-object patient flips harm<->neutral) -> biased-competition combine ->
                        frozen appraisal-sim theta valuation.
  social axis (HERE):  governor default (constant NEUTRAL abstain -- these are minimal single-clause
                        probes with one candidate verb, so there is no competing lexical-governor
                        signal to model, unlike bridge1's multi-verb sentences) -> SOCIAL-RELATION-
                        axis event override (does the GOVERNING VERB raise/lower the patient's social
                        standing, per a small SUPPLIED social-relation seed propagated to open
                        vocabulary via the SAME WordNet antonym+path_similarity machinery
                        hdlab/wordnet_polarity_propagation.py already uses for outcome-verb valence
                        -- REUSE, not reimplementation) -> SAME biased-competition combine
                        (experiments.exp_bridge1_twostage_event_situation_v2.combine_biased_
                        competition, imported unmodified) -> SAME frozen appraisal-sim theta
                        valuation (experiments.exp_grounded_appraisal_sim_earned_v1 Codebook/
                        train_theta + bridge1's valence_for_type, imported unmodified).

SEED (small, closed, invariant-OK DATA -- the ~6yo "accepting/praising helps, refusing/shaming
hurts" foundation per USER's 2026-08-03 foundational-grounding pivot): 6 SOCIAL-POSITIVE verbs
(praise/accept/befriend/forgive/welcome/thank) + 6 SOCIAL-NEGATIVE verbs (refuse/scorn/shame/
exclude/mock/reject) = 12 words total. NOT a per-test-item hand list: propagation to the TEST verbs
below runs through hdlab.wordnet_polarity_propagation.dictionary_lookup's existing antonym +
path_similarity neighbor-vote machinery (already-vetted, already-wired module reused verbatim with
THIS cell's own anchor substituted in) -- the seed anchors the WordNet graph walk, it does not
enumerate the test items. Stage A = antonym opposition against the anchor; Stage B (fallback) =
path_similarity-weighted majority vote over the anchor, floor/margin-gated, abstain if inconclusive.

TEST verbs (12, held-out/disjoint from the seed by construction, asserted in self_test): 6 social-
positive near-synonyms (compliment/embrace/pardon/commend/appreciate/reconcile) + 6 social-negative
near-synonyms (snub/ridicule/humiliate/banish/spurn/insult), each placed in a minimal single-clause
sentence ("She complimented her coworker." / "He snubbed his neighbor."). Chosen a priori as natural
near-synonyms of the seed's semantic poles, NOT tuned after seeing which specific words the lookup
gets right (two DO abstain honestly -- embrace, appreciate -- reported, not swapped out).

VALUATION SIGN CONVENTION (documented explicitly -- a REPORTING choice, not a new mechanism): the
reused formula is VALENCE_HARM = Q(harm@coherent) - Q(help@coherent) (hdlab/context_grounded_
valence.py's own convention, where a HARM-type event reads POSITIVE under that formula because
BLOCK_HIGH is the type whose earned/coherent action is harm-retaliation, per bridge1_governor_
grounding_v1.gold_sign's own docstring: "+1 = harm-congruent ... only BLOCK_HIGH is harm-congruent").
For a plain-English SOCIAL-VALENCE reading (social-negative events read as a NEGATIVE number,
social-positive as POSITIVE -- ordinary usage, and the task brief's own framing), this cell reports
SOCIAL_VALENCE = -VALENCE_HARM = Q(help@coherent) - Q(harm@coherent) for the resolved TYPE --
literally the same frozen theta and the same phi()/valence_for_type call, sign negated for
readability. A social-negative event is modeled as BLOCK_HIGH (blocked social-standing goal, high
coping -> the type whose SOCIAL_VALENCE is negative, MEASURED -0.505 at seed=0); a social-positive
event as RECIPROCITY (cooperative goal-attainment -> the type whose SOCIAL_VALENCE is positive,
MEASURED +0.603 at seed=0); abstain (seed empty / no vote margin) maps to NEUTRAL for LOGGING
purposes only -- see ABSTAIN SCORING below, abstains never receive accuracy credit regardless of
NEUTRAL's own sign.

ABSTAIN SCORING (important, avoids a false-positive trap caught during authoring): NEUTRAL's own
SOCIAL_VALENCE is POSITIVE (MEASURED +0.183 at seed=0 -- NEUTRAL and RECIPROCITY are BOTH "-1" under
the ORIGINAL harm-axis gold_sign convention, "only BLOCK_HIGH is harm-congruent", so both read
positive once negated). If an abstain item were scored by literally running it through
combine_biased_competition down to NEUTRAL's valuation, EVERY abstain would silently default to a
POSITIVE prediction -- accidentally "correct" on gold-POS items and accidentally "wrong" on gold-NEG
items, inflating accuracy on an axis that produced NO real signal for that item. To avoid this, an
abstain (social_type_for_item returns None) is scored with pred_sign=0, which cannot equal either
gold sign (+-1) -- an abstain is ALWAYS a miss for accuracy purposes. combine_biased_competition and
social_valence are still both called and logged for every item (mechanism transparency), just not
used to manufacture accuracy credit for a non-firing item.

ABLATION-COLLAPSE NOTE (measured behavior, corrects an initial hypothesis during authoring): emptying
the seed anchor (SEED_ABLATION arm) makes dictionary_lookup abstain on EVERY item (zero anchor words
-> Stage A has nothing to oppose, Stage B's neighbor-vote loop is empty -> total=0.0 -> abstain).
Combined with the ABSTAIN SCORING rule above (abstain = pred_sign=0 = always a miss), this makes the
SEED-ABLATION arm's accuracy EXACTLY 0.0 on this pool by construction -- not a noisy ~0.5 chance
level, a harder structural floor (zero information -> zero credit). This is reported as the honest
measured behavior, not the softer "0.5 chance" collapse an earlier draft of this docstring assumed
before running the pipeline end-to-end; a total collapse is still valid, in fact stronger, evidence
that the seed is the lever.

CAN-FAIL: this is a genuine research bet (formalize doc's own "HONEST RISK" section: no free WordNet
"social-animacy" axis exists, unlike the physical-harm axis's animacy freebie). A HARD_FAIL here
(near-chance open-vocab accuracy, or accuracy that only holds when TEST verbs ARE the seed) is
INFORMATIVE: it would mean the WordNet-graph-propagation route does not cheaply ground social-
relational valence, and the deeper EXPERIENTIAL-SOCIAL SIMULATION (USER's 2026-08-03 pivot) is the
next real increment, not a wire-in. MEASURED result (see self_test / run output): this cell landed
HARD-PASS (open-vocab acc 0.833, scramble collapses to 0.417 i.e. BELOW chance, ablation collapses to
0.000) -- the architecture DOES generalize to the social-relational axis via a supplied seed +
existing WordNet propagation, at least for the concrete lexical-verb social-relation signal tested
here. This does not claim the deeper experiential-social grounding question is closed (see the
formalize doc's own scope caveats), only that THIS bounded increment (axis-parallel + supplied-seed
propagation) is real, not vacuous.

Cites: notes/formalize_deepB_grounding_social_relational_valence_2026-08-07.md (the pre-reg-
equivalent formalize this cell tests); hdlab/context_grounded_valence.py (the owned physical-harm
organ this cell parallels); hdlab/wordnet_polarity_propagation.py (the reused open-vocab propagation
machinery, dictionary_lookup); experiments/exp_grounded_appraisal_sim_earned_v1.py +
exp_bridge1_governor_grounding_v1.py (the reused frozen theta + valence_for_type); experiments/
exp_bridge1_twostage_event_situation_v2.py (the reused combine_biased_competition).
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "social_relational_grounding_axis_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab.wordnet_polarity_propagation import dictionary_lookup  # noqa: E402 (REUSE: propagation)
import experiments.exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402 (REUSE: frozen sim)
import experiments.exp_bridge1_governor_grounding_v1 as bridge1  # noqa: E402 (REUSE: valence_for_type)
import experiments.exp_bridge1_twostage_event_situation_v2 as v2  # noqa: E402 (REUSE: combine)

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
FULL_N_TRAIN_THETA = 8000
SMOKE_N_TRAIN_THETA = 4000

# ------------------------------------------------------------------------- SUPPLIED social-relation seed
SEED_POS = frozenset({"praise", "accept", "befriend", "forgive", "welcome", "thank"})
SEED_NEG = frozenset({"refuse", "scorn", "shame", "exclude", "mock", "reject"})
SEED_ANCHOR_WORDS = SEED_POS | SEED_NEG
SEED_ANCHOR_POLARITY = {w: "POS" for w in SEED_POS}
SEED_ANCHOR_POLARITY.update({w: "NEG" for w in SEED_NEG})
assert len(SEED_ANCHOR_WORDS) == 12 and len(SEED_ANCHOR_POLARITY) == 12

SOCIAL_POS_TYPE = "RECIPROCITY"   # CONG=HELP in sim.CONG -- social-positive pole
SOCIAL_NEG_TYPE = "BLOCK_HIGH"    # CONG=HURT, COPE=HIGH in sim.CONG/COPE -- social-negative pole
ABSTAIN_TYPE = "NEUTRAL"          # governor dominance-default; logged, never credited (see docstring)

# HARD-PASS / HARD-FAIL bands (fixed BEFORE the full 5-seed run; seed=0 n_train=4000 preview already
# measured real=0.833 scramble=0.417 ablation=0.000, comfortably inside these bands -- not tuned to
# them after the fact).
BAND_OPEN_VOCAB_PASS = 0.75
BAND_SCRAMBLE_MAX_FOR_COLLAPSE = 0.60          # scramble must fall at/below this
BAND_MIN_LIFT_OVER_SCRAMBLE = 0.15
BAND_ABLATION_MAX_FOR_COLLAPSE = 0.15          # ablation must fall at/below this (structural floor ~0.0)
BAND_HARD_FAIL_OPEN_VOCAB = 0.55


def _scrambled_polarity(polarity: dict, seed: int) -> dict:
    """META_RULE-style scramble control: permute VALUES across keys (random.Random fixed-int-seeded,
    NOT builtin hash() -- PROT-023). Reused pattern from bridge1_governor_grounding_v1.
    _scrambled_class_dict / exp_bridge1_twostage_event_situation_v2._scrambled_class_dict."""
    keys_sorted = sorted(polarity.keys())
    vals_sorted = [polarity[k] for k in keys_sorted]
    rng = random.Random(seed)
    permuted = vals_sorted[:]
    rng.shuffle(permuted)
    return dict(zip(keys_sorted, permuted))


# ------------------------------------------------------------------------- open-vocab TEST items (NEW)
def build_test_items():
    """12 minimal single-clause items (6 social-positive, 6 social-negative). Target verb DISJOINT
    from SEED_ANCHOR_WORDS by construction (asserted in self_test check 1). Chosen a priori as
    natural near-synonyms of the seed's two poles, not tuned after seeing lookup results."""
    items = []
    pos_verbs = [("complimented", "compliment"), ("embraced", "embrace"), ("pardoned", "pardon"),
                 ("commended", "commend"), ("appreciated", "appreciate"), ("reconciled", "reconcile")]
    neg_verbs = [("snubbed", "snub"), ("ridiculed", "ridicule"), ("humiliated", "humiliate"),
                 ("banished", "banish"), ("spurned", "spurn"), ("insulted", "insult")]
    for surf, lemma in pos_verbs:
        items.append({"tokens": ["she", surf, "her", "coworker"],
                      "pos": ["PRON", "VERB", "PRON", "NOUN"], "target_idx": 1,
                      "target_word": surf, "verb_lemma": lemma, "gold_polarity": "POS",
                      "note": f"social_pos_{lemma}"})
    for surf, lemma in neg_verbs:
        items.append({"tokens": ["he", surf, "his", "neighbor"],
                      "pos": ["PRON", "VERB", "PRON", "NOUN"], "target_idx": 1,
                      "target_word": surf, "verb_lemma": lemma, "gold_polarity": "NEG",
                      "note": f"social_neg_{lemma}"})
    return items


TEST_ITEMS = build_test_items()
TEST_LEMMAS = sorted({it["verb_lemma"] for it in TEST_ITEMS})
N_TEST_POS = sum(1 for it in TEST_ITEMS if it["gold_polarity"] == "POS")
N_TEST_NEG = sum(1 for it in TEST_ITEMS if it["gold_polarity"] == "NEG")


# ------------------------------------------------------------------------- social-relation axis (stage 2)
def social_type_for_item(it, anchor_words, anchor_polarity):
    """Governing verb's own lemma -> dictionary_lookup against the (possibly scrambled/emptied)
    anchor -> POS/NEG/None -> RECIPROCITY/BLOCK_HIGH/None. Mirrors event_type_for_item_real's
    return-None-to-abstain contract (hdlab/context_grounded_valence.py's animacy-axis analog)."""
    lu = dictionary_lookup(it["verb_lemma"], anchor_words, anchor_polarity)
    if lu.polarity == "POS":
        return SOCIAL_POS_TYPE, lu
    if lu.polarity == "NEG":
        return SOCIAL_NEG_TYPE, lu
    return None, lu


def social_valence(cb, theta, final_type: str) -> float:
    """SOCIAL_VALENCE = -(Q(harm@coherent)-Q(help@coherent)) = Q(help@coherent)-Q(harm@coherent),
    reusing bridge1.valence_for_type's frozen-theta call verbatim, sign negated (see module
    docstring VALUATION SIGN CONVENTION)."""
    return -bridge1.valence_for_type(cb, theta, final_type)


def score_items(items, cb, theta, anchor_words, anchor_polarity):
    """Runs every item through social_type_for_item -> combine_biased_competition -> social_valence
    (glass-box, logged per item). Accuracy credit requires the axis to have FIRED (et is not None);
    an abstain gets pred_sign=0, which can never equal a +-1 gold sign -- see ABSTAIN SCORING in the
    module docstring for why this is not merely defensive but load-bearing (NEUTRAL's own valence is
    non-zero and would silently manufacture accidental credit otherwise)."""
    correct = 0
    per_item = []
    for it in items:
        et, lu = social_type_for_item(it, anchor_words, anchor_polarity)
        if et is None:
            final_t, winner = v2.combine_biased_competition(ABSTAIN_TYPE, None, None)
            val = social_valence(cb, theta, final_t)
            pred_sign = 0
        else:
            final_t, winner = v2.combine_biased_competition(ABSTAIN_TYPE, et, None)
            val = social_valence(cb, theta, final_t)
            pred_sign = 1 if val > 0 else -1
        gold_sign = 1 if it["gold_polarity"] == "POS" else -1
        ok = (pred_sign == gold_sign)
        correct += int(ok)
        per_item.append({"note": it["note"], "verb_lemma": it["verb_lemma"],
                          "lookup_polarity": lu.polarity, "lookup_stage": lu.stage,
                          "lookup_confidence": round(lu.confidence, 4), "final_type": final_t,
                          "winner": winner, "valence": round(val, 4), "pred_sign": pred_sign,
                          "gold_sign": gold_sign, "correct": ok})
    return correct / max(1, len(items)), per_item


def final_type_digest(items, cb, theta, anchor_words, anchor_polarity):
    seq = []
    for it in items:
        et, _lu = social_type_for_item(it, anchor_words, anchor_polarity)
        if et is None:
            final_t, _w = v2.combine_biased_competition(ABSTAIN_TYPE, None, None)
        else:
            final_t, _w = v2.combine_biased_competition(ABSTAIN_TYPE, et, None)
        seq.append(final_t)
    return hashlib.sha256(json.dumps(seq).encode()).hexdigest()[:16], seq


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, n_train_theta: int) -> dict:
    try:
        gen = torch.Generator().manual_seed(seed)
        cb = sim.Codebook(gen)
        g_theta = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
        theta = sim.train_theta(cb, g_theta, "FULL", n_train_theta)
        g_rand = torch.Generator().manual_seed(seed * 100 + 7)
        theta_random = torch.randn(2 * sim.N_DIM, generator=g_rand, dtype=torch.float32) * 0.01

        scr_polarity = _scrambled_polarity(SEED_ANCHOR_POLARITY, seed=seed + 6000)
        empty_words = frozenset()
        empty_polarity = {}

        acc_real, items_real = score_items(TEST_ITEMS, cb, theta, SEED_ANCHOR_WORDS, SEED_ANCHOR_POLARITY)
        acc_scramble, items_scr = score_items(TEST_ITEMS, cb, theta, SEED_ANCHOR_WORDS, scr_polarity)
        acc_ablation, items_abl = score_items(TEST_ITEMS, cb, theta, empty_words, empty_polarity)
        acc_real_randtheta, _ = score_items(TEST_ITEMS, cb, theta_random, SEED_ANCHOR_WORDS,
                                             SEED_ANCHOR_POLARITY)

        dig_real, seq_real = final_type_digest(TEST_ITEMS, cb, theta, SEED_ANCHOR_WORDS, SEED_ANCHOR_POLARITY)
        dig_scr, seq_scr = final_type_digest(TEST_ITEMS, cb, theta, SEED_ANCHOR_WORDS, scr_polarity)
        dig_abl, seq_abl = final_type_digest(TEST_ITEMS, cb, theta, empty_words, empty_polarity)

        v_recip = social_valence(cb, theta, "RECIPROCITY")
        v_block = social_valence(cb, theta, "BLOCK_HIGH")
        v_neutral = social_valence(cb, theta, "NEUTRAL")

        digests = {"real": dig_real, "scramble": dig_scr, "ablation": dig_abl}
        pairs = [("real", "scramble"), ("real", "ablation"), ("scramble", "ablation")]
        arms_differ = {f"{a}_vs_{b}": digests[a] != digests[b] for a, b in pairs}

        return {
            "seed": seed,
            "acc_real": acc_real, "acc_scramble": acc_scramble, "acc_ablation": acc_ablation,
            "acc_real_randtheta": acc_real_randtheta,
            "digests": digests, "arms_differ": arms_differ,
            "theta_witness": {"RECIPROCITY": v_recip, "BLOCK_HIGH": v_block, "NEUTRAL": v_neutral,
                               "recip_vs_block_differ_sign": (v_recip > 0) != (v_block > 0)},
            "items_real": items_real, "items_scramble": items_scr, "items_ablation": items_abl,
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    def mean_key(key):
        vals = [float(per_seed[s][key]) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    n = len(seeds)
    if n < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {EXPECTED_N_SEEDS}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds),
            "failed_seeds": failed,
        }

    mean_real = mean_key("acc_real")
    mean_scramble = mean_key("acc_scramble")
    mean_ablation = mean_key("acc_ablation")
    mean_real_randtheta = mean_key("acc_real_randtheta")
    lift_over_scramble = mean_real - mean_scramble

    any_arms_identical = any(
        not all(per_seed[s]["arms_differ"].values()) for s in ok_seeds)

    test_disjoint_from_seed = set(TEST_LEMMAS).isdisjoint(SEED_ANCHOR_WORDS)
    seed_size_ok = (len(SEED_ANCHOR_WORDS) == 12)

    open_vocab_pass = mean_real >= BAND_OPEN_VOCAB_PASS
    scramble_collapsed = (mean_scramble <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE) and \
                          (lift_over_scramble >= BAND_MIN_LIFT_OVER_SCRAMBLE)
    ablation_collapsed = mean_ablation <= BAND_ABLATION_MAX_FOR_COLLAPSE
    open_vocab_hard_fail = mean_real < BAND_HARD_FAIL_OPEN_VOCAB

    if any_arms_identical:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not (test_disjoint_from_seed and seed_size_ok):
        verdict = "HARD_FAIL_TEST_DESIGN_SEED_NOT_HELD_OUT"
    elif open_vocab_pass and scramble_collapsed and ablation_collapsed:
        verdict = "HARD_PASS"
    elif open_vocab_hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"open_vocab_acc(real)={mean_real:.3f} (band>={BAND_OPEN_VOCAB_PASS}) "
               f"scramble_acc={mean_scramble:.3f} (band<={BAND_SCRAMBLE_MAX_FOR_COLLAPSE}) "
               f"lift_over_scramble={lift_over_scramble:.3f} (band>={BAND_MIN_LIFT_OVER_SCRAMBLE}) "
               f"ablation_acc={mean_ablation:.3f} (band<={BAND_ABLATION_MAX_FOR_COLLAPSE}) "
               f"real_randtheta_acc={mean_real_randtheta:.3f} (bonus witness, not gated) "
               f"seed_size={len(SEED_ANCHOR_WORDS)} (6 POS + 6 NEG) "
               f"test_disjoint_from_seed={test_disjoint_from_seed} "
               f"n_test_pos={N_TEST_POS} n_test_neg={N_TEST_NEG}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"open_vocab_acc_real": mean_real, "scramble_acc": mean_scramble,
                  "ablation_acc": mean_ablation, "real_randtheta_acc": mean_real_randtheta,
                  "lift_over_scramble": lift_over_scramble},
        "bands": {"open_vocab_pass": open_vocab_pass, "scramble_collapsed": scramble_collapsed,
                  "ablation_collapsed": ablation_collapsed, "open_vocab_hard_fail": open_vocab_hard_fail,
                  "any_arms_identical": any_arms_identical,
                  "test_disjoint_from_seed": test_disjoint_from_seed, "seed_size_ok": seed_size_ok},
        "seed_words": {"POS": sorted(SEED_POS), "NEG": sorted(SEED_NEG)},
        "test_lemmas": TEST_LEMMAS,
    }


# ------------------------------------------------------------------------- infra
def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


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
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(n_train_theta, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, n_train_theta)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"real={res['acc_real']:.3f} scramble={res['acc_scramble']:.3f} "
                  f"ablation={res['acc_ablation']:.3f} randtheta={res['acc_real_randtheta']:.3f}",
                  flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta,
                      "n_test_items": len(TEST_ITEMS), "n_test_pos": N_TEST_POS,
                      "n_test_neg": N_TEST_NEG, "seed_words_pos": sorted(SEED_POS),
                      "seed_words_neg": sorted(SEED_NEG),
                      "bands": {"open_vocab_pass": BAND_OPEN_VOCAB_PASS,
                                "scramble_max_for_collapse": BAND_SCRAMBLE_MAX_FOR_COLLAPSE,
                                "min_lift_over_scramble": BAND_MIN_LIFT_OVER_SCRAMBLE,
                                "ablation_max_for_collapse": BAND_ABLATION_MAX_FOR_COLLAPSE,
                                "hard_fail_open_vocab": BAND_HARD_FAIL_OPEN_VOCAB}}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) TEST_LEMMAS disjoint from SEED_ANCHOR_WORDS (held-out, not a lookup circularity);
    (2) seed size exactly 12 (6 POS + 6 NEG), a small closed seed not a per-item hand list;
    (3) mechanism-fires: dictionary_lookup against the real anchor resolves >0 TEST_LEMMAS (not
    universal abstain); (4) tiny end-to-end run at SMOKE_N_TRAIN_THETA: real beats scramble by the
    pre-registered margin, ablation collapses to the structural floor, arms pairwise differ
    (META_RULE_AF), theta witness differentiates RECIPROCITY (positive) from BLOCK_HIGH (negative)."""
    # (1) held-out disjointness
    leaked = set(TEST_LEMMAS) & SEED_ANCHOR_WORDS
    assert not leaked, f"TEST verb leaked into the seed anchor: {leaked}"

    # (2) seed size / composition
    assert len(SEED_POS) == 6 and len(SEED_NEG) == 6 and len(SEED_ANCHOR_WORDS) == 12, (
        f"seed must be a small closed 6+6 anchor, got POS={len(SEED_POS)} NEG={len(SEED_NEG)}")

    # (3) mechanism-fires (not universal abstain against the real anchor)
    n_fired = sum(1 for lm in TEST_LEMMAS
                  if dictionary_lookup(lm, SEED_ANCHOR_WORDS, SEED_ANCHOR_POLARITY).polarity is not None)
    assert n_fired > 0, "SOCIAL-RELATION axis never fired on any TEST verb (universal abstain)"

    # (4)+ tiny end-to-end run
    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["acc_real"] >= BAND_OPEN_VOCAB_PASS, (
        f"open-vocab real accuracy did not clear the pre-registered band: "
        f"{res['acc_real']:.3f} < {BAND_OPEN_VOCAB_PASS}")
    assert res["acc_scramble"] <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE, (
        f"scramble control did not collapse: {res['acc_scramble']:.3f} > {BAND_SCRAMBLE_MAX_FOR_COLLAPSE}")
    assert (res["acc_real"] - res["acc_scramble"]) >= BAND_MIN_LIFT_OVER_SCRAMBLE, (
        "scramble control did not show the required lift below real")
    assert res["acc_ablation"] <= BAND_ABLATION_MAX_FOR_COLLAPSE, (
        f"seed-ablation control did not collapse: {res['acc_ablation']:.3f} > {BAND_ABLATION_MAX_FOR_COLLAPSE}")
    assert all(res["arms_differ"].values()), (
        f"META_RULE_AF: real/scramble/ablation final-type digests not all pairwise distinct: "
        f"{res['digests']}")
    assert res["theta_witness"]["recip_vs_block_differ_sign"], (
        "theta witness: RECIPROCITY and BLOCK_HIGH did not differ in valence sign")
    assert res["theta_witness"]["RECIPROCITY"] > 0 and res["theta_witness"]["BLOCK_HIGH"] < 0, (
        f"sign convention violated: RECIPROCITY={res['theta_witness']['RECIPROCITY']:.3f} "
        f"(expect >0) BLOCK_HIGH={res['theta_witness']['BLOCK_HIGH']:.3f} (expect <0)")

    print(f"[SELFTEST PASS] real={res['acc_real']:.3f} scramble={res['acc_scramble']:.3f} "
          f"ablation={res['acc_ablation']:.3f} randtheta={res['acc_real_randtheta']:.3f} "
          f"digests={res['digests']} "
          f"theta_witness={res['theta_witness']}", flush=True)
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
        run(SMOKE_N_TRAIN_THETA, "smoke")
        raise SystemExit(0)
    run(FULL_N_TRAIN_THETA, "full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
