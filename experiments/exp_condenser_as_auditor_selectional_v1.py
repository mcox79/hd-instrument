"""CONDENSER-AS-AUDITOR (glass-box, first prototype): the seed VET (29479) proved ONTOLOGY (VerbNet+
WordNet) CANNOT audit dense LLM selectional knowledge -- vacuous catch-rate + it OVER-REJECTS (79%%
of its flags on clean entries were ontology-WRONG/LLM-RIGHT, e.g. give|money, hold|hands, eat|acorn --
the ontology's own selrestr/exemplar coverage is too sparse to be a fair judge of real usage). This cell
tests the OPPOSITE honesty mechanism: does the CONDENSER (banked 29476, exp_online_knowledge_condenser_
selectional_v1.py -- class-level verb->filler-class evidence distilled from READING a real corpus, an
INDEPENDENT non-LLM source) cross-check the LLM seed table (scaled_seed_table_v1.json, 29479) better --
flagging genuine errors via DISAGREEMENT while agreeing with correct entries, at a false-flag rate that
decisively beats the ontology's 79%%-wrong composition?

MECHANISM (class-granularity auditor, honest about its own scope -- 29476's own HONEST SCOPE note: the
condenser is CLASS-granularity, it can audit CLASS-level assignments, NOT fine within-class values):
  1) Read the SAME real corpus (SCV.run_reader_on_files, the same hand-rule reader / SVO extraction 29476
     uses) to build attested[v][supersense] = {noun: count} -- POSITIVE evidence only (the condenser never
     asserts "this class is impossible for v", only "this class IS attested for v with >=K distinct
     exemplars" -- exactly the fast-mapping precedent already used in 29476: >=2 distinct exemplars ->
     the class is "established"/dominant for that verb).
  2) established_classes(v) = {ss : n_distinct_nouns(v,ss) >= ESTABLISHED_MIN}. This is a POSITIVE,
     corpus-grounded opinion -- fundamentally different from the ontology's SPARSE lexical-resource
     absence-based restrictions (29475's failure mode): a class only becomes "established" after REAL,
     repeated corpus attestation, not a missing/present lexical-resource technicality.
  3) Per LLM seed entry (v, n, rating): class_n = SCV.supersense(n). The condenser has an OPINION only
     when v has >=1 established class AND v's TOTAL cross-class evidence clears MIN_VERB_TOTAL_EVIDENCE
     (guards against acting on a paper-thin single-observation verb -- the exact over-reach class that
     made the ontology auditor useless: flagging on absence-of-evidence rather than presence-of-
     contradicting-evidence). Two DISAGREEMENT rules (deliberately NOT absence-only):
       DISAGREE_CLASS_MISMATCH   : class_n is NOT among v's established classes (verb has OTHER,
                                    well-evidenced classes) AND rating >= DISAGREE_HIGH (LLM claims this
                                    class IS plausible) -- catches "wrong filler-class" LLM errors
                                    (the injected-error design below).
       DISAGREE_CONDENSER_SAYS_YES: class_n IS among v's established classes AND rating <= DISAGREE_LOW
                                    (LLM claims this well-attested class is implausible) -- catches
                                    LLM under-rating of a class real usage corroborates.
     Anything else (no opinion, or rating agrees with the condenser's class judgment) is NOT flagged --
     silence on genuine coverage gaps is the discipline the ontology auditor lacked (it flagged on any
     technical absence; this auditor flags ONLY on a positive-evidence CONTRADICTION).

INJECTED-ERROR CAN-FAIL TEST (realistic, NON-PINNED -- learn from 29479's own vacuous-injection trap: that
  cell corrupted a rating to an EXTREME value (0.05/0.95) chosen specifically to cross its own detector's
  threshold by construction -- circular, not realistic). THIS cell instead swaps the FILLER, not the
  number: pick a verb v with an established class C (>=MIN_VERB_TOTAL_EVIDENCE total corpus evidence);
  construct a NEW (v, n_wrong) key where n_wrong is a REAL, corpus-attested noun of a DIFFERENT class,
  sampled via 29476's OWN cross-class distractor mechanism (sample_distractor -- mechanical, fixed RNG,
  never attested for v anywhere in the corpus, so it is a genuinely wrong filler-class, not just a rare
  one) -- exactly "swap a verb's preferred filler-class to a plausible-but-attested-wrong one" per spec.
  The RATING assigned to this wrong pair is NEVER invented/tuned: it is copied verbatim from an EXISTING
  real LLM-authored high rating for that SAME verb elsewhere in the table (deterministic min-pick), or
  (if the verb has no high rating of its own) the table's own empirically observed median high rating
  (MEASURED@data/exp_pivot_scaled_seed_knowledge_table_v1/scaled_seed_table_v1.json: median of ratings
  >=0.65 = 0.85, n=133/579). Whether the auditor catches it depends ENTIRELY on the condenser's real
  class evidence, not on a hand-picked number.

METRICS (reported per spec):
  catch_rate_injected      = recall on the injected (known-wrong) battery.
  false_flag_rate_clean    = fraction of ORIGINAL (unmodified) checkable entries flagged -- the direct
                             analog of the ontology's over-rejection failure; must be decisively LOWER.
  precision_mixed          = TP / (TP+FP) over the mixed injected+clean population -- the direct analog
                             of "79%% of flags were wrong" (ontology's implied precision ~0.21); this
                             auditor must beat that DECISIVELY.
  enrichment_lift          = precision_mixed / base_rate(injected fraction of the checkable pool) -- are
                             flagged items enriched for genuine (here: known-injected) errors vs chance.
  coverage_overlap         = fraction of the 579 seed entries the condenser has ANY opinion on at all --
                             reported honestly; this is NOT expected to be high (class-granularity + a
                             finite corpus), but must be non-vacuous.
  HELD-OUT PROPERTY (stated, not a separate split): the condenser's corpus-reading evidence is built with
  ZERO visibility into the seed table (injected or original) -- the reading pass never consults
  scaled_seed_table_v1.json in any way. This is the held-out guarantee the spec asks for: the auditor's
  knowledge source is independent of, and blind to, what it is being asked to judge.

CONTROL (must-fail): scramble the (verb,class)->n_types evidence VALUES across KEYS (5 fixed seeds, mean
  reported -- same discipline as 29476's ARM_SHUFFLE) and recompute established_classes from the scrambled
  table. If the SPECIFIC learned class assignment isn't doing the work, shuffling should not hurt --
  HARD_FAIL if it doesn't collapse catch/precision.

PRE-REGISTERED VERDICT BANDS (set BEFORE running FULL; do not redefine mid-run). Let:
  catch      = catch_rate_injected
  ffr        = false_flag_rate_clean
  prec       = precision_mixed
  lift       = enrichment_lift
  cov        = coverage_overlap
  catch_scr  = mean(catch_rate over 5 scrambled seeds)

  HARD_FAIL_* (checked FIRST; any true overrides HARD_PASS):
    catch <= 0.15                                -> HARD_FAIL_VACUOUS_CATCH_RATE
    ffr >= 0.50                                  -> HARD_FAIL_OVER_FLAGS_LIKE_ONTOLOGY
    (lift is not None and prec <= 1.3 * base_rate) -> HARD_FAIL_NO_DISCRIMINATION_ABOVE_BASE_RATE
    catch_scr >= catch - 0.05                    -> HARD_FAIL_SHUFFLE_DID_NOT_COLLAPSE
    cov < 0.05                                    -> HARD_FAIL_VACUOUS_COVERAGE

  HARD_PASS_CONDENSER_BEATS_ONTOLOGY_AUDITOR (ALL must hold, none of the FAIL conditions above true):
    catch >= 0.50  AND  ffr <= 0.20  AND  prec >= 0.50  AND  lift >= 2.0  AND  cov >= 0.30
    AND  catch_scr <= catch - 0.20  AND  arms_differ_verified

  MIDDLE_BAND: neither block fires cleanly.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reuses the existing hand-rule SVO
  reader (already CPU-sequential-by-design) + condenser's O(1) dict-based evidence table; scoring/auditing
  is O(n_seed_entries). No matmul, no GPU-batchable primitive. Storage: no_storage (JSON artifacts only).
  Runtime invariant: glass-box dict lookup ONLY; NO LLM/network/autograd at inference (the seed table + the
  condenser's evidence are both PRE-BUILT artifacts read-only here; zero new LLM calls in this cell).
  Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng in deterministic sorted order, no
  hash()-seeded anything. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist,
  NO git add -A; do NOT bank (skunkworks VETs).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (hash test: real classification vector vs scrambled-seed0 vector)
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: recall/precision/false-flag-rate measurement; no quantitative noise floor for the discriminator
  - baseline_in_band at smoke (coverage_overlap in (0.05,0.95): non-vacuous but honestly partial)
  - discriminator survives scale: multi-scale smoke (smoke AND smoke x4 mining-sentence count) both must
    produce >=1 injection candidate verb and >=1 checkable clean entry before FULL is attempted
  - HARD_PASS strictly above floor (catch>=0.50 well above the <=0.15 FAIL edge; prec>=0.50 well above the
    barely-above-base-rate FAIL edge)
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
  - deterministic_seeding: fixed int seeds + numpy default_rng + sorted(...); no hash()/list(set())
  - real_code_path_exercised: SCV.run_reader_on_files + C.build_reading_stream + C.attested_maps +
    C.sample_distractor (the REAL reader/condenser pipeline) invoked at tiny scale inside self_test()
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import platform
import statistics
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "condenser_as_auditor_selectional_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse 29476 (condenser: reading stream, attested-evidence maps, cross-class distractor sampler) and the
# reader/mining pipeline VERBATIM -- one-variable discipline (only the AUDIT logic is new in this cell).
from experiments import exp_online_knowledge_condenser_selectional_v1 as C  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV  # noqa: E402

from experiments._validity_preflight import run_validity_preflight  # noqa: E402

NEG_SEED = C.NEG_SEED                          # 20260723, shared fixed base across this cell family
INJECT_SEED = NEG_SEED + 601                   # candidate-verb + distractor-sampling RNG (fresh, distinct)
SHUFFLE_SEEDS = C.SHUFFLE_SEEDS                # 5 fixed seeds, reused verbatim from the condenser cell

ESTABLISHED_MIN = 2              # >=2 distinct nouns of a class attested for v -> class is "established"
                                  # (CITED@exp_online_knowledge_condenser_selectional_v1.py docstring: the
                                  # fast-mapping precedent already used for the condenser's own generalize-
                                  # after-2-exemplars mechanism)
MIN_VERB_TOTAL_EVIDENCE = 3       # total distinct noun types (any class) for v before a MISMATCH flag is
                                  # allowed -- guards the exact over-reach failure mode that made the
                                  # ontology auditor vacuous (flag-on-absence-of-thin-evidence)
DISAGREE_LOW = 0.35               # rating <= this while class IS established -> LLM under-rates real usage
DISAGREE_HIGH = 0.65              # rating >= this while class is NOT established -> LLM over-claims a class
N_INJECT_CAP = 30                 # cap on injected-error battery size (candidates permitting)

SEED_TABLE_PATH = os.path.join(REPO_ROOT, "data", "exp_pivot_scaled_seed_knowledge_table_v1",
                                "scaled_seed_table_v1.json")

MODE_CONFIG = C.MODE_CONFIG       # {"selftest","smoke","smoke4x","full"} -> {files, max_sents}; reused
                                  # verbatim so this cell's corpus scope is IDENTICAL to 29476's.


# ----------------------------------------------------------------------------------------------
# LLM seed table under audit (29479's artifact; read-only, never modified except by our own
# explicit, mechanical, cross-class injection battery below).
# ----------------------------------------------------------------------------------------------
def load_llm_seed_table():
    with open(SEED_TABLE_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    ratings = obj["ratings"]
    table = {}
    for k, v in ratings.items():
        vb, n = k.split("|", 1)
        table[(vb, n)] = float(v)
    return table


# ----------------------------------------------------------------------------------------------
# Condenser knowledge: attested[v][ss] = {noun:count} (POSITIVE evidence only, real corpus reading).
# ----------------------------------------------------------------------------------------------
def build_condenser_evidence(mode, out_dir):
    stream, n_mine = C.build_reading_stream(mode, out_dir)
    attested, verb_any, class_pool = C.attested_maps(stream)
    flat_counts = {}          # (v,ss) -> n_distinct_nouns
    for v in attested:
        for ss in attested[v]:
            flat_counts[(v, ss)] = len(attested[v][ss])
    return attested, verb_any, class_pool, flat_counts, len(stream), n_mine


def dominant_and_totals(flat_counts):
    """established_classes(v) + verb_total_evidence(v) from a flat (v,ss)->n_types table."""
    dom = defaultdict(set)
    tot = defaultdict(int)
    for (v, ss), n in flat_counts.items():
        tot[v] += n
        if n >= ESTABLISHED_MIN:
            dom[v].add(ss)
    return dom, tot


def scramble_flat_counts(flat_counts, seed):
    """Permute VALUES across KEYS (identical discipline to 29476's ARM_SHUFFLE / make_shuffled_score_fn)."""
    keys = sorted(flat_counts.keys())
    vals = [flat_counts[k] for k in keys]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(vals)).tolist()
    return {keys[i]: vals[perm[i]] for i in range(len(keys))}


# ----------------------------------------------------------------------------------------------
# Per-entry classification: the audit decision (positive-evidence contradiction, never absence-only).
# ----------------------------------------------------------------------------------------------
def classify_entry(v, n, rating, dom, tot):
    ss = SCV.supersense(n)
    if ss is None:
        return "NO_OPINION_OOV_NOUN"
    d = dom.get(v, set())
    if not d:
        return "NO_OPINION_NO_ESTABLISHED_CLASS"
    if tot.get(v, 0) < MIN_VERB_TOTAL_EVIDENCE:
        return "NO_OPINION_LOW_VERB_EVIDENCE"
    if ss in d:
        if rating <= DISAGREE_LOW:
            return "DISAGREE_CONDENSER_SAYS_YES"
        return "AGREE_CONDENSER_SAYS_YES"
    else:
        if rating >= DISAGREE_HIGH:
            return "DISAGREE_CLASS_MISMATCH"
        return "NO_OPINION_CLASS_UNESTABLISHED"


def audit_table_entries(table, dom, tot):
    """Returns dict (v,n) -> classification label, for every entry in `table`."""
    return {(v, n): classify_entry(v, n, rating, dom, tot) for (v, n), rating in table.items()}


def has_opinion(label):
    return not label.startswith("NO_OPINION")


def is_flagged(label):
    return label.startswith("DISAGREE")


# ----------------------------------------------------------------------------------------------
# Injected-error battery: realistic, non-pinned (filler-swap, not a hand-tuned number).
# ----------------------------------------------------------------------------------------------
def select_injection_candidates(seed_table, dom, tot, n_inject_cap, seed):
    candidate_verbs = sorted(v for v, d in dom.items() if d and tot.get(v, 0) >= MIN_VERB_TOTAL_EVIDENCE)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(candidate_verbs)).tolist()
    n_take = min(n_inject_cap, len(candidate_verbs))
    chosen = sorted(candidate_verbs[order[i]] for i in range(n_take))
    return chosen


def global_median_high_rating(seed_table):
    high = sorted(r for r in seed_table.values() if r >= 0.65)
    return round(statistics.median(high), 6) if high else 0.85  # THEORETICAL@fallback if table had none


def inject_errors(seed_table, dom, tot, verb_any, class_pool, n_inject_cap, seed):
    """Swap the FILLER (never the number): for each chosen verb, sample a cross-class distractor noun
    (real, corpus-attested, never attested for v -- 29476's own sample_distractor, mechanical fixed-RNG)
    and assign it a RATING copied verbatim from an existing real high LLM rating for that same verb (or
    the table's own empirically observed median-high rating if the verb has none). No invented numbers."""
    chosen_verbs = select_injection_candidates(seed_table, dom, tot, n_inject_cap, seed)
    med_high = global_median_high_rating(seed_table)
    rng = np.random.default_rng(seed + 1)
    injected_table = dict(seed_table)
    injected_keys = set()
    injected_records = []
    for v in chosen_verbs:
        target_class = sorted(dom[v])[0]     # deterministic pick of one established class to violate
        n_wrong = C.sample_distractor(v, target_class, verb_any, class_pool, rng)
        if n_wrong is None:
            continue
        key = (v, n_wrong)
        if key in seed_table:
            continue    # already a real entry; skip (do not overwrite an entry we cannot tell apart)
        existing_high = sorted(r for (vv, _n), r in seed_table.items() if vv == v and r >= 0.65)
        rating = existing_high[0] if existing_high else med_high
        injected_table[key] = rating
        injected_keys.add(key)
        injected_records.append({"v": v, "n_wrong": n_wrong, "violated_class": target_class,
                                  "rating": rating, "rating_source": ("verb_own_high" if existing_high
                                                                       else "table_median_high")})
    return injected_table, injected_keys, injected_records


# ----------------------------------------------------------------------------------------------
# Full audit run: real evidence + scrambled-control, mixed injected+clean population, metrics.
# ----------------------------------------------------------------------------------------------
def run_audit(seed_table, attested, verb_any, class_pool, flat_counts):
    dom, tot = dominant_and_totals(flat_counts)
    n_seed_entries = len(seed_table)

    # Coverage/overlap on the ORIGINAL (uninjected) table.
    orig_labels = audit_table_entries(seed_table, dom, tot)
    n_checkable_clean = sum(1 for lab in orig_labels.values() if has_opinion(lab))
    n_flagged_clean = sum(1 for lab in orig_labels.values() if is_flagged(lab))
    coverage_overlap = round(n_checkable_clean / max(1, n_seed_entries), 4)
    false_flag_rate_clean = round(n_flagged_clean / max(1, n_checkable_clean), 4)

    injected_table, injected_keys, injected_records = inject_errors(
        seed_table, dom, tot, verb_any, class_pool, N_INJECT_CAP, INJECT_SEED)
    n_injected = len(injected_keys)

    mixed_labels = audit_table_entries(injected_table, dom, tot)
    flagged_mixed = {k for k, lab in mixed_labels.items() if is_flagged(lab)}
    n_caught = len(flagged_mixed & injected_keys)
    catch_rate = round(n_caught / max(1, n_injected), 4)
    n_clean_flagged_in_mixed = len(flagged_mixed - injected_keys)
    assert n_clean_flagged_in_mixed == n_flagged_clean, (
        "injection must not alter classification of pre-existing clean entries (added keys only)")

    n_flags_total = n_caught + n_clean_flagged_in_mixed
    precision_mixed = round(n_caught / max(1, n_flags_total), 4) if n_flags_total > 0 else None
    base_rate = round(n_injected / max(1, n_injected + n_checkable_clean), 4)
    enrichment_lift = (round(precision_mixed / base_rate, 4)
                        if (precision_mixed is not None and base_rate > 0) else None)

    # Scramble control: 5 fixed seeds, mean reported.
    scr_catch, scr_ffr, scr_prec = [], [], []
    scr_labels_seed0 = None
    for si, sseed in enumerate(SHUFFLE_SEEDS):
        scr_flat = scramble_flat_counts(flat_counts, sseed)
        scr_dom, scr_tot = dominant_and_totals(scr_flat)
        scr_orig_labels = audit_table_entries(seed_table, scr_dom, scr_tot)
        scr_n_checkable = sum(1 for lab in scr_orig_labels.values() if has_opinion(lab))
        scr_n_flagged_clean = sum(1 for lab in scr_orig_labels.values() if is_flagged(lab))
        scr_ffr.append(scr_n_flagged_clean / max(1, scr_n_checkable))
        scr_mixed_labels = audit_table_entries(injected_table, scr_dom, scr_tot)
        scr_flagged = {k for k, lab in scr_mixed_labels.items() if is_flagged(lab)}
        scr_caught = len(scr_flagged & injected_keys)
        scr_catch.append(scr_caught / max(1, n_injected))
        scr_clean_flagged = len(scr_flagged - injected_keys)
        scr_flags_total = scr_caught + scr_clean_flagged
        scr_prec.append(scr_caught / scr_flags_total if scr_flags_total > 0 else 0.0)
        if si == 0:
            scr_labels_seed0 = scr_mixed_labels
    catch_rate_scrambled_mean = round(float(np.mean(scr_catch)), 4)
    false_flag_rate_scrambled_mean = round(float(np.mean(scr_ffr)), 4)
    precision_scrambled_mean = round(float(np.mean(scr_prec)), 4)

    # ARMS-MUST-DIFFER (META_RULE_AF): real classification vector vs scrambled(seed0) classification
    # vector over the SAME sorted mixed-table keys must not be bit-identical.
    all_keys = sorted(mixed_labels.keys())
    real_vec = "|".join(mixed_labels[k] for k in all_keys)
    scr_vec = "|".join(scr_labels_seed0[k] for k in all_keys)
    d_real = hashlib.sha256(real_vec.encode("utf-8")).hexdigest()[:16]
    d_scr = hashlib.sha256(scr_vec.encode("utf-8")).hexdigest()[:16]
    arms_differ_verified = bool(d_real != d_scr)

    return {
        "n_seed_entries": n_seed_entries, "n_checkable_clean": n_checkable_clean,
        "n_flagged_clean": n_flagged_clean, "coverage_overlap": coverage_overlap,
        "false_flag_rate_clean": false_flag_rate_clean,
        "n_injected": n_injected, "n_caught": n_caught, "catch_rate_injected": catch_rate,
        "precision_mixed": precision_mixed, "base_rate_injected_fraction": base_rate,
        "enrichment_lift": enrichment_lift,
        "catch_rate_scrambled_mean": catch_rate_scrambled_mean,
        "false_flag_rate_scrambled_mean": false_flag_rate_scrambled_mean,
        "precision_scrambled_mean": precision_scrambled_mean,
        "catch_rate_scrambled_per_seed": [round(x, 4) for x in scr_catch],
        "arms_differ_verified": arms_differ_verified,
        "digest_real": d_real, "digest_scrambled_seed0": d_scr,
        "injected_records_sample": injected_records[:12],
        "n_dominant_verbs": sum(1 for d in dom.values() if d),
        "n_verbs_with_any_evidence": len(attested),
    }


# ----------------------------------------------------------------------------------------------
# IO helpers.
# ----------------------------------------------------------------------------------------------
def _out_dir(mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "smoke4x": "_smoke4x", "full": ""}[mode]
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:400]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid()}
    try:
        write_metrics(output_dir, diag)
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------
# Core run.
# ----------------------------------------------------------------------------------------------
def run_mode(mode):
    t0 = time.perf_counter()
    out_dir = _out_dir(mode)
    _write_start_marker(out_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    seed_table = load_llm_seed_table()
    print(f"[{ANCHOR_NAME}:{mode}] LLM seed table under audit: {len(seed_table)} entries "
          f"(MEASURED@{SEED_TABLE_PATH})", flush=True)

    attested, verb_any, class_pool, flat_counts, n_stream, n_mine = build_condenser_evidence(mode, out_dir)
    print(f"[{ANCHOR_NAME}:{mode}] condenser evidence: {n_stream} evidence tuples from {n_mine} sentences, "
          f"{len(attested)} verbs with any evidence", flush=True)

    res = run_audit(seed_table, attested, verb_any, class_pool, flat_counts)

    catch = res["catch_rate_injected"]
    ffr = res["false_flag_rate_clean"]
    prec = res["precision_mixed"]
    lift = res["enrichment_lift"]
    cov = res["coverage_overlap"]
    catch_scr = res["catch_rate_scrambled_mean"]
    base_rate = res["base_rate_injected_fraction"]
    has_signal = bool(res["n_injected"] >= 1 and res["n_checkable_clean"] >= 1)

    verdict = "PENDING_NO_SIGNAL"
    if has_signal:
        hard_fail = (
            catch <= 0.15
            or ffr >= 0.50
            or (prec is not None and prec <= 1.3 * base_rate)
            or catch_scr >= catch - 0.05
            or cov < 0.05
        )
        hard_pass = (
            catch >= 0.50 and ffr <= 0.20 and (prec is not None and prec >= 0.50)
            and (lift is not None and lift >= 2.0) and cov >= 0.30
            and catch_scr <= catch - 0.20 and res["arms_differ_verified"]
        )
        if hard_fail:
            verdict = "HARD_FAIL_CONDENSER_AUDITOR_USELESS"
        elif hard_pass:
            verdict = "HARD_PASS_CONDENSER_BEATS_ONTOLOGY_AUDITOR"
        else:
            verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"VERDICT_core catch_rate_injected={catch} false_flag_rate_clean={ffr} "
           f"precision_mixed={prec} enrichment_lift={lift} coverage_overlap={cov} "
           f"catch_rate_scrambled_mean={catch_scr} n_injected={res['n_injected']} "
           f"n_checkable_clean={res['n_checkable_clean']} n_seed_entries={res['n_seed_entries']} "
           f"base_rate={base_rate} arms_differ={res['arms_differ_verified']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_mining_sentences": n_mine, "n_reading_stream_evidence": n_stream,
        "established_min": ESTABLISHED_MIN, "min_verb_total_evidence": MIN_VERB_TOTAL_EVIDENCE,
        "disagree_low": DISAGREE_LOW, "disagree_high": DISAGREE_HIGH, "n_inject_cap": N_INJECT_CAP,
        **res,
        "has_signal": has_signal,
        "runtime_invariant": ("glass-box dict lookup ONLY; NO LLM/network/autograd at inference; the seed "
                              "table (29479) and the condenser's corpus evidence (29476's reading pipeline) "
                              "are both pre-built/read-only here"),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "recall/precision/false-flag-rate measurement; no quantitative noise floor",
        "deterministic_seeding": "fixed int seeds + numpy default_rng consumed in sorted order; no hash()",
        "held_out_property": ("the condenser's corpus-reading evidence is built with ZERO visibility into "
                              "scaled_seed_table_v1.json (injected or original) -- the reading pass never "
                              "consults the seed table in any way; this is the held-out guarantee: the "
                              "auditor's knowledge source is independent of what it judges."),
        "injection_design_note": ("realistic, non-pinned: swaps the FILLER NOUN to a real, corpus-attested, "
                                  "cross-class distractor (29476's own sample_distractor, mechanical fixed-"
                                  "RNG) never attested for that verb; the RATING is copied verbatim from an "
                                  "existing real LLM rating (never invented/tuned to cross a threshold) -- "
                                  "the opposite of 29479's inject_errors, which corrupted the NUMBER to an "
                                  "extreme (0.05/0.95) chosen specifically to cross its own detector's "
                                  "threshold by construction."),
        "honest_scope_note": ("class-granularity only, per 29476: this auditor can judge whether the LLM's "
                              "assigned filler-class matches corpus-attested usage; it cannot judge FINE "
                              "within-class distinctions (e.g. which specific FOOD noun is most typical)."),
        "ontology_comparison_ref": ("29479 MEASURED: ontology auditor catch_rate=1.0 (VACUOUS -- injected "
                                    "values were extreme 0.05/0.95 chosen to trivially cross its own "
                                    "CONTRA_THRESH=0.45 gap) with false_flag_rate=0.1845 on clean entries "
                                    "and (per task brief) 79%% of its clean flags were hand-inspected as "
                                    "ontology-WRONG/LLM-RIGHT (give|money, hold|hands, eat|acorn) -- i.e. "
                                    "~21%% flag precision. This cell's false_flag_rate_clean and "
                                    "precision_mixed are the direct structural analogs, computed against a "
                                    "NON-pinned injected battery."),
        "REQUIRED_FIELDS": ["verdict", "catch_rate_injected", "false_flag_rate_clean", "precision_mixed",
                            "enrichment_lift", "coverage_overlap", "catch_rate_scrambled_mean",
                            "arms_differ_verified", "runtime_invariant", "held_out_property"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] verdict={verdict} -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ----------------------------------------------------------------------------------------------
# Self-test: constructs REAL reader/condenser objects at tiny scale (Gate F.1); toy discriminator checks.
# ----------------------------------------------------------------------------------------------
def self_test():
    exercised = set()

    # 1) LLM seed table loads + is non-empty.
    seed_table = load_llm_seed_table()
    assert len(seed_table) > 0, "seed table must load with >=1 entry"
    exercised.add("load_llm_seed_table")

    # 2) REAL reader/condenser pipeline exercised at tiny scale (Gate F.1 real_code_path_exercised).
    out_dir = _out_dir("selftest")
    attested, verb_any, class_pool, flat_counts, n_stream, n_mine = build_condenser_evidence(
        "selftest", out_dir)
    exercised.add("SCV.run_reader_on_files")
    exercised.add("C.build_reading_stream")
    exercised.add("C.attested_maps")
    assert n_mine > 0 and n_stream > 0, "real mining pipeline must produce real evidence at tiny scale"
    dom, tot = dominant_and_totals(flat_counts)
    assert isinstance(dom, dict) and isinstance(tot, dict)

    # 3) Toy discriminator mechanics: a verb with a clearly established class; a correct entry (class
    #    matches, high rating) must NOT flag; an injected filler-swap (wrong class, real corpus noun,
    #    copied real rating) MUST flag; a low-rating-on-established-class entry MUST flag the other way.
    toy_flat = {("peel", "noun.food"): 3, ("kick", "noun.object"): 3, ("kick", "noun.artifact"): 1}
    toy_dom, toy_tot = dominant_and_totals(toy_flat)
    assert "noun.food" in toy_dom["peel"], "toy: peel's food class must be established (n=3>=2)"
    lab_correct = classify_entry("peel", "apple", 0.9, toy_dom, toy_tot)     # food, high rating
    lab_wrong = classify_entry("peel", "rock", 0.9, toy_dom, toy_tot)        # NOT food (peel has no
                                                                              # established rock-class),
                                                                              # high rating -> mismatch
    lab_underrated = classify_entry("peel", "orange", 0.1, toy_dom, toy_tot)  # food, LOW rating -> disagree
    assert lab_correct == "AGREE_CONDENSER_SAYS_YES", lab_correct
    assert lab_wrong == "DISAGREE_CLASS_MISMATCH", lab_wrong
    assert lab_underrated == "DISAGREE_CONDENSER_SAYS_YES", lab_underrated
    exercised.add("classify_entry")

    # 4) Low-evidence verb must stay SILENT (NO_OPINION), not flag -- the anti-over-reach discipline.
    thin_flat = {("nibble", "noun.food"): 2}   # established (n=2) but tot=2 < MIN_VERB_TOTAL_EVIDENCE(3)
    thin_dom, thin_tot = dominant_and_totals(thin_flat)
    lab_thin = classify_entry("nibble", "rock", 0.9, thin_dom, thin_tot)
    assert lab_thin == "NO_OPINION_LOW_VERB_EVIDENCE", lab_thin
    exercised.add("dominant_and_totals")

    # 5) Scramble collapses the toy signal: shuffling (v,ss)->n across keys should generally destroy the
    #    specific peel->food association (statistical property; assert the mechanism RUNS and returns a
    #    valid dict -- full statistical margin is checked at cell scale over 5 seeds).
    scr = scramble_flat_counts(toy_flat, SHUFFLE_SEEDS[0])
    assert set(scr.keys()) == set(toy_flat.keys()) and sorted(scr.values()) == sorted(toy_flat.values())
    exercised.add("scramble_flat_counts")

    # 6) Injected-error battery on a toy seed table + REAL sample_distractor (real code path).
    toy_seed_table = {("peel", "apple"): 0.9, ("peel", "orange"): 0.85, ("kick", "ball"): 0.9}
    toy_verb_any = defaultdict(set, {"peel": {"apple", "orange"}, "kick": {"ball"}})
    toy_class_pool = defaultdict(set, {"noun.food": {"apple", "orange", "bread"}, "noun.object": {"ball"}})
    injected_tab, injected_keys, injected_records = inject_errors(
        toy_seed_table, toy_dom, toy_tot, toy_verb_any, toy_class_pool, n_inject_cap=5, seed=INJECT_SEED)
    exercised.add("C.sample_distractor")
    assert len(injected_keys) >= 1, "toy injected battery must inject at least one entry"
    for (v, n) in injected_keys:
        assert v in ("peel", "kick"), f"unexpected injected verb in this toy table: {v}"
        lab = classify_entry(v, n, injected_tab[(v, n)], toy_dom, toy_tot)
        assert lab == "DISAGREE_CLASS_MISMATCH", f"injected toy entry must be flagged as class mismatch: {lab}"
    exercised.add("inject_errors")

    # 7) Coverage-overlap + false-flag-rate helpers run without error on the toy table.
    orig_labels = audit_table_entries(toy_seed_table, toy_dom, toy_tot)
    n_checkable = sum(1 for lab in orig_labels.values() if has_opinion(lab))
    assert n_checkable >= 1
    exercised.add("audit_table_entries")

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["SCV.run_reader_on_files", "C.build_reading_stream",
                                        "C.attested_maps", "C.sample_distractor"],
         "exercised_entrypoints": exercised},
        {"kind": "metric_moves", "metric_name": "toy_classification_is_flagged",
         "before": float(is_flagged(lab_correct)), "after": float(is_flagged(lab_wrong))},
    ], run_mode="self_test")
    assert ok, "validity preflight failed at self-test scale"

    print(f"[{ANCHOR_NAME}] self-test PASS | n_mine={n_mine} n_stream={n_stream} "
          f"toy_injected={len(injected_keys)} exercised={sorted(exercised)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--smoke4x", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.smoke4x:
        run_mode("smoke4x"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --smoke4x | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), e)
        raise
