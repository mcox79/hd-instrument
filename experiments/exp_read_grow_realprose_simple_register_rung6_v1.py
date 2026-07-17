"""exp_read_grow_realprose_simple_register_rung6_v1 -- RUNG 6: does the glass-box, NO-LLM extraction pipeline
reach the classical precision-favoring envelope on a genuinely SIMPLE (early-reader-adjacent) register, as
opposed to the general web register (UD-EWT unfiltered) where RUNG 5 HARD_FAILed at P=0.179 and RUNG 5b's
abstain gate still only reached P=0.286 at FULL scale (both HARD_FAIL).

TRIGGER (verbatim from the dispatching contract): the biology/curriculum notes
(notes/research_open_text_glassbox_ie_reading_frontier_curriculum_2026-07-16.md,
notes/research_early_reader_language_acquisition_curriculum_2026-07-16.md) predict early-reader prose is
DOMINATED by the single-clause constructions this pipeline handles. RUNG 4's controlled hand-authored corpus
suggested a register advantage but was construction-SET by the author, not a real sample; RUNG 5/5b measured a
real but TOO-HARD (general web) register. This cell measures a real SIMPLE register and resolves the one
unmeasured number: on genuinely simple real text, does precision clear 0.60 (the register-advantage claim), or
does it stay broken (a deeper role-assignment/lemmatization wall, not just a construction-coverage gap)?

CORPUS/PATH CHOICE (declared, per contract's explicit ask to state choice + why): PATH (A) -- a SIMPLE-SYNTAX
SUBSET of UD_English-EWT (the SAME corpus RUNG 5/5b already used), filtered HARD for objective structural
simplicity, NOT a genuinely different (OneStopEnglish / Simple-Wikipedia) early-reader corpus. Chosen over
PATH (B) for three concrete reasons: (1) COMPUTE-PROPORTIONALITY -- RUNG 5/5b's own committed local corpus is
gold-dependency-parsed already; a new corpus needs either hand-authored gold (a multi-cycle curation task,
explicitly flagged as future RUNG 6 scope in RUNG 5's own module docstring "NEXT" section) or a fresh
network-fetch-plus-commit cycle this session's compute-proportionality discipline reserves for genuine
multi-cycle undertakings, not a single-cycle diagnostic; (2) it reuses the EXACT SAME gold-derivation machinery
(`analyze_sentence`) RUNG 5/5b already validated at self-test, so the gold triples are not new hand-judgment;
(3) it directly operationalizes the contract's own suggested criteria ("short sentences, single root verb, low
clause count"). HONEST LABEL (stated plainly, per contract's own instruction): this is a "simple-syntax subset
of general web register," a PROXY for early-reader register on SYNTAX/CLAUSE-STRUCTURE only -- it does NOT
control for early-reader VOCABULARY (Dolch/Fry/CEFR-J tiers), which is a distinct axis PATH (B) would need to
address. A vocabulary-controlled early-reader register test remains a candidate future rung.

THE OBJECTIVE SIMPLICITY FILTER (new code, `load_simple_sentences` / `_clause_count` below) -- applied to the
GOLD CoNLL-U dependency parse, BEFORE any extraction is attempted, per the contract's explicit HONEST GUARD
(do not reverse-engineer the slice from extraction success):
  1. token_count in [5, 12] (tighter than RUNG 5's [5, 25] -- early-reader sentences are shorter; an OBJECTIVE
     length criterion, computed identically to RUNG 5's own qualifying-sentence filter).
  2. exactly one root token (single main clause anchor).
  3. the root's UPOS is VERB or AUX ("single root verb", per the contract's own suggested criterion --
     excludes nonverbal/copular-adjective roots at the FILTER stage, not the scoring stage).
  4. `_clause_count(tokens) <= 1` -- a NEW, purely gold-parse-derived clause counter: starts at 1 for the root,
     adds 1 for every VERB/AUX token attached via `conj` DIRECTLY to a verbal head (predicate coordination --
     this is what "vp_coordination" IS structurally), and adds 1 for every token anywhere in the sentence whose
     base deprel is in {advcl, ccomp, xcomp, acl, csubj, parataxis} (any embedded/subordinate clause, covering
     relative clauses via `acl`/`acl:relcl`). Coordinated NOUN phrases (`conj` on a NOUN, e.g. "the cat and the
     dog") do NOT increment the count -- a compound subject is still ONE clause. VALIDATED at self-test against
     the SAME 5 hand-built dependency trees RUNG 5's own `analyze_sentence` self-test already uses (one per
     bucket): single_clause_svo -> 1 (included), compound_subject -> 1 (included), passive -> 1 (included),
     vp_coordination -> 2 (excluded), relative_clause -> 2 (excluded). This is a purely structural
     (clause-count) filter, mechanically independent of whatever `analyze_sentence`'s own priority-ordered
     bucket assignment would say, though it agrees with it on all 5 known buckets by construction.
  This filter is IDENTICAL for every sentence regardless of what the extraction pipeline would do with it --
  it never looks at `ie_extract_open` / `ie_extract_open_gated` output. Verified at self_test.

MEASURED PRE-DESIGN PROBE (standalone script run BEFORE finalizing this cell, reproduced live at self_test on
a small real slice and again at FULL below -- per this arc's own established discipline of running a probe to
check FEASIBILITY/non-vacuousness before committing bands, while the BAND THRESHOLDS THEMSELVES are the
contract's own literal, pre-specified numbers below, not derived from this probe):
  simple-slice pool size (token 5-12, single verbal root, clause_count<=1): n=157 sentences (out of 436
  sentences in the SAME token-length band before the clause/root filter -- i.e. only 36.0% of already-short
  UD-EWT sentences are structurally single-clause; RUNG 5's unfiltered pool at token band 5-25 was 846).
  Construction distribution WITHIN this simple slice (SEEDS=[7,13,19], N_PER_SEED=100, pooled n=300, sampled
  WITH inter-seed overlap since pool < 3*n_per_seed -- see COMPUTE section): single_clause_svo=0.577,
  vp_coordination=0.000 (excluded BY FILTER CONSTRUCTION -- clause_count>1), relative_clause=0.000 (excluded
  BY FILTER CONSTRUCTION), compound_subject=0.037, passive=0.077, other_unhandled=0.310 (residual: intransitive
  verbs with no object/oblique, imperatives, and similar within-single-clause misses -- a genuinely different,
  smaller residual than the general-register 58.6% other_unhandled RUNG 5 measured). This CONFIRMS the biology
  prediction's first half: restricting to objectively-simple structure does concentrate single_clause_svo mass
  (57.7% vs RUNG 5's 24.8% unfiltered) and eliminates the two hardest bucket classes by construction.
  Precision, however, does NOT clear the envelope: GATED precision_on_attempted=0.379, coverage=0.087,
  BASELINE (no gate) precision=0.250, coverage=0.127 -- both below the 0.50 HARD-FAIL floor. LOCALIZED
  mechanism (re-verified live at self_test, not just narrated): even WITHIN the single_clause_svo bucket alone,
  GATED precision is only 0.55 (17 attempted, 11 correct) -- i.e. the pipeline is NOT reliably correct even on
  sentences it correctly recognizes as simple SVO. Two concrete, localized failure mechanisms account for the
  single_clause_svo misses: (a) irregular-verb lemmatization ("has"->"ha", "did"->uncorrected "did" vs gold
  "do" -- the SAME lookup-free-suffix-stripper limitation RUNG 5's own docstring flagged as mechanism (b));
  (b) multi-token proper-noun / compound-noun head selection ("Santa Claus"->wrongly emits "clau" instead of
  gold's "santa"; "Winston Peters"->"peter" instead of "winston"; "Customer Service 101"->object "customer"
  instead of gold's compound head "service" -- a NEW, more specific naming for RUNG 5's mechanism (d)
  "proper-noun/compound-name tokenization complexity"). A DIAGNOSTIC-ONLY relaxed-irregular-verb rescoring
  (`_relax_irregular_verb`, imported unmodified from RUNG 5, applied identically here) partially recovers GATED
  precision to 0.448 (still below both the 0.50 floor and the 0.60 envelope) -- confirming irregular-verb
  lemma mismatch is A real contributing factor but NOT the sole or dominant cause; the remaining gap is the
  compound-noun/proper-noun head-selection mechanism plus a handful of imperative-sentence false positives
  ("Please verify receipt..." -- "Please" mistagged as a subject noun) that fall OUTSIDE the single_clause_svo
  bucket (classified other_unhandled, since they have no gold-derivable triple) but still get spuriously
  extracted by the pipeline's linear scan.

BANDS (pre-registered, and IDENTICAL to the contract's own literal thresholds -- not derived from the probe
above; the probe's role, per this arc's established discipline, is feasibility/non-vacuousness verification,
not band-setting):
  Primary discriminator = GATED arm (ie_extract_open_gated, RUNG 5b's abstain gate, imported unmodified --
  the current best-available mechanism in this arc, so "does the pipeline reach the envelope" is asked of the
  pipeline's own best form, not its earlier, already-superseded BASELINE). BASELINE (ie_extract_open, no gate)
  is reported alongside, informational, per the contract's explicit ask for "with + without the abstain gate".
  HARD-PASS: precision_on_attempted_GATED >= 0.60 (the classical envelope) AND coverage_sentence_rate_GATED
    >= 0.05 (non-vacuous -- matches RUNG 5's own coverage floor) AND guard_regression_ok_gated AND
    oos_control_fired_gated. This is the REGISTER-ADVANTAGE-IS-REAL outcome.
  HARD-FAIL: precision_on_attempted_GATED < 0.50 (precision stays broken even on the simple register -- per
    the contract's own diagnosis, this would point to lemmatizer/role-assignment bugs, not construction
    coverage) OR coverage_sentence_rate_GATED < 0.03 (vacuous) OR NOT guard_regression_ok_gated OR the
    length-band-matched simple_fraction (see below) is itself vacuously small (<0.10, meaning "simple" isn't
    even a meaningful stratum of this register).
  MIDDLE_BAND: otherwise.
  HONEST FRAMING (per contract): a high-precision/low-recall shape is the SUCCESSFUL envelope; only a genuine
  precision COLLAPSE below 0.50 is reported as HARD-FAIL, exactly as pre-registered.

COMPUTE: SEEDS=[7,13,19], N_PER_SEED=100 (pooled n=300; the simple-slice pool is n=157, smaller than RUNG 5's
  846-sentence pool at its wider token band, so N_PER_SEED is sized so a single seed's sample uses the
  majority of the pool -- WITH-REPLACEMENT-ACROSS-SEEDS overlap is expected and declared here explicitly,
  matching `sample_real_sentences`'s existing (RUNG 5, unmodified) per-seed-independent `rng.sample` semantics;
  this is the SAME sampling scheme RUNG 5/5b already used, just against a smaller filtered pool -- pooled
  precision/recall remain valid under duplicate-row scoring, it only means the 3 "seeds" are less independent
  than RUNG 5's own wide-pool draws, a limitation stated honestly rather than hidden). Smoke = seed[7] only,
  SAME N_PER_SEED (Option A, discriminator-survives-scale; trivial wall time). Local, CPU-only, no torch, no
  numpy, no VSA store, no queue/GPU/atoms/push -- executed DIRECTLY (bash), matching RUNG 5/5b's own stated
  precedent for cells whose measured wall time is sub-second. Corpus already fetched + committed (RUNG 5's
  `data/corpora/ud_english_ewt/en_ewt-ud-test.conllu`); NO network access at self-test/smoke/full time.
  Storage: no_storage. Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before running.

NEXT (not this cell): if PATH (A)'s honest result still leaves the register-advantage question open, PATH (B)
(OneStopEnglish / Simple-English-Wikipedia with hand-authored gold, vocabulary-controlled) remains the
un-collapsed alternative RUNG 5's own docstring already flagged as future scope -- a corpus-curation
undertaking, not a single-cycle extension. Separately, the two LOCALIZED mechanisms this cell measures
(irregular-verb lemma table gap; compound/proper-noun head-selection) are small, well-localized, non-scope-
creeping grammar fixes that would likely raise even-the-simple-register precision without needing a harder
parser or a different corpus -- a candidate RUNG 7 fix-cell if the register-advantage question is reopened.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BASELINE vs GATED emitted-triple-set hash differs on the
#   real simple-slice sample by construction -- the gate strictly reduces the emission set, as in RUNG 5b).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic role-assignment + the classical
#   tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same as RUNG 5/5b.
# - baseline_in_band: N/A BY DESIGN -- GATED's own known RUNG-5b general-register precision (0.286 at FULL,
#   MEASURED@RUNG5b metrics.json) is the pre-registered floor this cell checks for a REGISTER ADVANTAGE over;
#   `guard_regression_ok_gated` (gate still correct on its own known-lexicon guard sentences) is the
#   substituted regression guard, matching RUNG 5/5b's own precedent.
# - discriminator survives scale: corpus is FIXED-size real prose, deterministic filtered pool. Smoke uses the
#   SAME N_PER_SEED as FULL, single seed only (Option A; trivial wall time makes this free).
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test parses the REAL local corpus file (not synthetic-only), applies the REAL
#   simplicity filter, samples a tiny real slice, and runs BOTH extraction arms against REAL sentences.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19]; random.Random(seed).sample over a sorted(...)
#   sentence-id-ordered pool (never hash()/list(set(...)) for ordering or seeding) -- reuses RUNG 5's own
#   `sample_real_sentences` unmodified.
# - all numbers in comments tagged HYPOTHESIZED@prereg / MEASURED@metrics / MEASURED@standalone-pre-design-
#   probe / MEASURED@RUNG5 / MEASURED@RUNG5b / CITED@research-note.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import argparse
import time
import json
import hashlib
import platform
import traceback
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_realprose_simple_register_rung6_v1"

# --- GENUINE REUSE: RUNG 5's corpus parser / gold-deriver / scorer / sampler / BASELINE extractor / relax
# diagnostic / guard sets, all imported UNMODIFIED. RUNG 5b's abstain-gated extractor, also imported unmodified.
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    CONLLU_PATH, parse_conllu, analyze_sentence, CONSTRUCTION_CLASSES, score_arm, sample_real_sentences,
    ie_extract_open, _relax_irregular_verb, GUARD_SENTENCES, OUT_OF_SCHEMA_CONTROL,
)
from experiments.exp_read_grow_realprose_abstain_gate_rung5b_v1 import ie_extract_open_gated  # noqa: E402

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only (same as RUNG 5/5b); glass-box-legal.

# ---------------------------------------------------------------------------
# THE OBJECTIVE SIMPLICITY FILTER: new code, clearly demarcated. Purely gold-CoNLL-U-derived; NEVER looks at
# extraction output. See module docstring for the full rationale.
# ---------------------------------------------------------------------------
SUBORDINATE_DEPREL_BASES = {"advcl", "ccomp", "xcomp", "acl", "csubj", "parataxis"}
TOK_LO_DEFAULT = 5
TOK_HI_DEFAULT = 12


def _clause_count(tokens):
    """purely-structural clause counter from GOLD CoNLL-U dependency edges: starts at (number of root tokens,
    normally 1), +1 per VERB/AUX token attached via `conj` (predicate coordination -- structurally what
    vp_coordination IS), +1 per token anywhere with base deprel in SUBORDINATE_DEPREL_BASES (any embedded/
    subordinate clause, including relative clauses via acl/acl:relcl). Coordinated NOUN phrases (`conj` on a
    NOUN) do NOT add a clause. NEVER inspects extraction output -- purely a property of the gold parse."""
    roots = [t for t in tokens if t["deprel"].split(":")[0] == "root"]
    n = len(roots)
    for t in tokens:
        base = t["deprel"].split(":")[0]
        if base == "conj" and t["upos"] in ("VERB", "AUX"):
            n += 1
        elif base in SUBORDINATE_DEPREL_BASES:
            n += 1
    return n


def _is_declarative_length_matched(sent, tok_lo, tok_hi):
    """the RUNG-5 qualifying-sentence filter (declarative, length band, no URL/email artifact), reused as the
    OUTER filter every simple-slice sentence must also satisfy -- the only change from RUNG 5 is the tighter,
    OBJECTIVE early-reader-shortness token band (5-12 instead of RUNG 5's 5-25)."""
    text = sent["meta"].get("text", "")
    sid = sent["meta"].get("sent_id", "")
    if not text or not sid:
        return False
    if not text.strip().endswith("."):
        return False
    if "http" in text.lower() or "@" in text:
        return False
    n_tok = len(sent["tokens"])
    return tok_lo <= n_tok <= tok_hi


def load_length_matched_pool(path, tok_lo=TOK_LO_DEFAULT, tok_hi=TOK_HI_DEFAULT):
    """all declarative, length-band-matched sentences (BEFORE the clause/root-verb simplicity filter) --
    the denominator for the corpus-level simple_fraction statistic."""
    if not path.exists():
        raise FileNotFoundError(
            f"UD-EWT corpus not found at {path}. This cell reads a LOCAL, pre-fetched copy (no network access "
            f"at self-test/smoke/full time) -- see data/corpora/ud_english_ewt/PROVENANCE.md.")
    all_sents = parse_conllu(path)
    matched = [s for s in all_sents if _is_declarative_length_matched(s, tok_lo, tok_hi)]
    return sorted(matched, key=lambda s: s["meta"]["sent_id"])


def load_simple_sentences(path, tok_lo=TOK_LO_DEFAULT, tok_hi=TOK_HI_DEFAULT):
    """THE simplicity filter: length-matched pool AND single root AND root UPOS in (VERB, AUX) AND
    _clause_count <= 1. Purely gold-parse-derived; applied BEFORE any extraction is attempted (HONEST GUARD --
    never filters on whether ie_extract_open / ie_extract_open_gated would succeed)."""
    length_matched = load_length_matched_pool(path, tok_lo, tok_hi)
    simple = []
    for s in length_matched:
        roots = [t for t in s["tokens"] if t["deprel"].split(":")[0] == "root"]
        if len(roots) != 1:
            continue
        if roots[0]["upos"] not in ("VERB", "AUX"):
            continue
        if _clause_count(s["tokens"]) > 1:
            continue
        simple.append(s)
    return sorted(simple, key=lambda s: s["meta"]["sent_id"]), len(length_matched)


def build_rows_for_seed(pool_sorted, seed, n_per_seed):
    sample = sample_real_sentences(pool_sorted, seed, min(n_per_seed, len(pool_sorted)))
    rows = []
    dist = {c: 0 for c in CONSTRUCTION_CLASSES}
    for s in sample:
        a = analyze_sentence(s["tokens"])
        dist[a["cls"]] += 1
        rows.append({"text": s["meta"]["text"], "sent_id": s["meta"]["sent_id"], "cls": a["cls"],
                     "subclass": a["subclass"], "gold": a["gold"]})
    return rows, dist


# ---------------------------------------------------------------------------
# glass-box-legal checks (same method as RUNG 5/5b).
# ---------------------------------------------------------------------------
def _grep_confirm_no_neural_imports():
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(src)]


def _runtime_neural_module_check():
    banned = ("torch", "spacy", "transformers", "stanza")
    return sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))


# ---------------------------------------------------------------------------
# run + aggregate.
# ---------------------------------------------------------------------------
def run_full(seeds, n_per_seed, tok_lo=TOK_LO_DEFAULT, tok_hi=TOK_HI_DEFAULT):
    simple_sorted, length_matched_pool_size = load_simple_sentences(CONLLU_PATH, tok_lo, tok_hi)
    simple_fraction_of_length_matched_pool = (
        len(simple_sorted) / length_matched_pool_size if length_matched_pool_size else 0.0)

    all_rows = []
    dist_pooled = {c: 0 for c in CONSTRUCTION_CLASSES}
    per_seed_dist = {}
    for seed in seeds:
        rows, dist = build_rows_for_seed(simple_sorted, seed, n_per_seed)
        all_rows.extend(rows)
        for c in CONSTRUCTION_CLASSES:
            dist_pooled[c] += dist[c]
        per_seed_dist[seed] = dist

    n_total = len(all_rows)
    dist_frac = {c: (dist_pooled[c] / n_total if n_total else 0.0) for c in CONSTRUCTION_CLASSES}

    baseline_score = score_arm(all_rows, ie_extract_open, relax=False)
    gated_score = score_arm(all_rows, ie_extract_open_gated, relax=False)
    baseline_relaxed = score_arm(all_rows, ie_extract_open, relax=True)
    gated_relaxed = score_arm(all_rows, ie_extract_open_gated, relax=True)

    svo_rows = [r for r in all_rows if r["cls"] == "single_clause_svo"]
    svo_gated_only = score_arm(svo_rows, ie_extract_open_gated, relax=False) if svo_rows else None

    guard_ok_baseline = all(set(ie_extract_open(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)
    guard_ok_gated = all(set(ie_extract_open_gated(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)
    oos_baseline = all(not ie_extract_open(s)[0] for s in OUT_OF_SCHEMA_CONTROL)
    oos_gated = all(not ie_extract_open_gated(s)[0] for s in OUT_OF_SCHEMA_CONTROL)

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total_sentences": n_total,
        "tok_lo": tok_lo, "tok_hi": tok_hi,
        "simple_pool_size": len(simple_sorted),
        "length_matched_pool_size": length_matched_pool_size,
        "simple_fraction_of_length_matched_pool": simple_fraction_of_length_matched_pool,
        "construction_distribution_counts": dist_pooled, "construction_distribution_fractions": dist_frac,
        "per_seed_distribution": {str(k): v for k, v in per_seed_dist.items()},
        "baseline_score": baseline_score, "gated_score": gated_score,
        "baseline_relaxed_diagnostic": baseline_relaxed, "gated_relaxed_diagnostic": gated_relaxed,
        "svo_only_gated_diagnostic": svo_gated_only,
        "guard_regression_ok_baseline": guard_ok_baseline, "guard_regression_ok_gated": guard_ok_gated,
        "oos_control_fired_baseline": oos_baseline, "oos_control_fired_gated": oos_gated,
        "all_rows": all_rows,
    }


def compute_verdict(agg):
    prec_g = agg["gated_score"]["precision_on_attempted"]
    prec_b = agg["baseline_score"]["precision_on_attempted"]
    cov_g = agg["gated_score"]["coverage_sentence_rate"]
    cov_b = agg["baseline_score"]["coverage_sentence_rate"]
    guard_ok = agg["guard_regression_ok_gated"]
    oos_ok = agg["oos_control_fired_gated"]
    simple_frac = agg["simple_fraction_of_length_matched_pool"]

    if prec_g is None:
        return ("MIDDLE_BAND", "GATED arm emitted zero triples on the whole simple-register sample -- "
                                "mechanism did not fire at all", "no_triples_emitted")

    hard_pass = (prec_g >= 0.60) and (cov_g >= 0.05) and guard_ok and oos_ok and (simple_frac >= 0.10)
    hard_fail = (prec_g < 0.50) or (cov_g < 0.03) or (not guard_ok) or (simple_frac < 0.10)

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if simple_frac < 0.10:
            weakest = "simple_fraction_of_length_matched_pool_below_0.10_stratum_vacuous"
        elif prec_g < 0.60:
            weakest = "gated_precision_on_attempted_below_0.60_register_advantage_not_realized"
        elif cov_g < 0.05:
            weakest = "gated_coverage_sentence_rate_below_0.05"
        elif not guard_ok:
            weakest = "guard_regression_failed_gated"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire_gated"

    dist = agg["construction_distribution_fractions"]
    dist_str = " ".join(f"{c}={dist[c]:.3f}" for c in CONSTRUCTION_CLASSES)
    svo_diag = agg["svo_only_gated_diagnostic"]
    svo_str = (f"svo_only_gated_precision={svo_diag['precision_on_attempted']}" if svo_diag else "svo_only_gated=n/a")
    msg = (f"{tier} | SIMPLE-REGISTER (PATH A: UD-EWT simple-syntax subset, token[{agg['tok_lo']}-{agg['tok_hi']}], "
           f"clause_count<=1) construction_distribution[{dist_str}] (n={agg['n_total_sentences']}, "
           f"simple_pool={agg['simple_pool_size']}, simple_fraction_of_length_matched_pool={simple_frac:.3f}) | "
           f"GATED precision_on_attempted={prec_g:.3f} (HARD-PASS>=0.60, HARD-FAIL<0.50) "
           f"coverage_sentence_rate={cov_g:.3f} (HARD-PASS>=0.05, HARD-FAIL<0.03) "
           f"recall={agg['gated_score']['recall']:.3f} n_attempted={agg['gated_score']['n_attempted']}/"
           f"{agg['n_total_sentences']} | BASELINE(no gate) precision={prec_b:.3f} coverage={cov_b:.3f} | "
           f"{svo_str} | guard_regression_ok_gated={guard_ok} oos_control_fired_gated={oos_ok} | "
           f"weakest={weakest} | REGISTER_ADVANTAGE_REAL={hard_pass}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# boilerplate: start marker / metrics write / crash diagnostic.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": f"exp_{ANCHOR_NAME}", "smoke": f"exp_{ANCHOR_NAME}_smoke",
           "self_test": f"exp_{ANCHOR_NAME}_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path (real corpus file, real nltk.pos_tag, real filter + both arms).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real CoNLL-U parse of the local corpus file, real "
          "nltk.pos_tag calls, real simplicity filter + both extraction arms)...", flush=True)

    # (0) glass-box-legal: static source-scan + RUNTIME transitive sys.modules check.
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    _ = nltk.pos_tag(["The", "cat", "sat", "."])
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) _clause_count correctness against the SAME 5 hand-built dependency trees RUNG 5's own self_test uses
    # (one per non-other bucket) -- proves the OBJECTIVE simplicity filter agrees with the (separately
    # validated) construction classifier's own bucket boundaries on every known case.
    def _tok(id_, form, lemma, upos, head, deprel):
        return {"id": id_, "form": form, "lemma": lemma, "upos": upos, "head": head, "deprel": deprel}

    svo = [_tok(1, "The", "the", "DET", 2, "det"), _tok(2, "cat", "cat", "NOUN", 3, "nsubj"),
           _tok(3, "eats", "eat", "VERB", 0, "root"), _tok(4, "the", "the", "DET", 5, "det"),
           _tok(5, "fish", "fish", "NOUN", 3, "obj")]
    assert _clause_count(svo) == 1, "single_clause_svo must be clause_count==1 (simple)"
    assert analyze_sentence(svo)["cls"] == "single_clause_svo"

    vpc = [_tok(1, "The", "the", "DET", 2, "det"), _tok(2, "dog", "dog", "NOUN", 3, "nsubj"),
           _tok(3, "eats", "eat", "VERB", 0, "root"), _tok(4, "bread", "bread", "NOUN", 3, "obj"),
           _tok(5, "and", "and", "CCONJ", 6, "cc"), _tok(6, "chases", "chase", "VERB", 3, "conj"),
           _tok(7, "cats", "cat", "NOUN", 6, "obj")]
    assert _clause_count(vpc) == 2, "vp_coordination must be clause_count==2 (excluded from simple slice)"
    assert analyze_sentence(vpc)["cls"] == "vp_coordination"

    cs = [_tok(1, "The", "the", "DET", 2, "det"), _tok(2, "cat", "cat", "NOUN", 5, "nsubj"),
          _tok(3, "and", "and", "CCONJ", 4, "cc"), _tok(4, "dog", "dog", "NOUN", 2, "conj"),
          _tok(5, "eat", "eat", "VERB", 0, "root"), _tok(6, "bread", "bread", "NOUN", 5, "obj")]
    assert _clause_count(cs) == 1, "compound_subject (NOUN conj) must be clause_count==1 (simple)"
    assert analyze_sentence(cs)["cls"] == "compound_subject"

    rc = [_tok(1, "The", "the", "DET", 2, "det"), _tok(2, "cat", "cat", "NOUN", 7, "nsubj"),
          _tok(3, "that", "that", "PRON", 4, "nsubj"), _tok(4, "chases", "chase", "VERB", 2, "acl:relcl"),
          _tok(5, "the", "the", "DET", 6, "det"), _tok(6, "dog", "dog", "NOUN", 4, "obj"),
          _tok(7, "eats", "eat", "VERB", 0, "root"), _tok(8, "fish", "fish", "NOUN", 7, "obj")]
    assert _clause_count(rc) == 2, "relative_clause must be clause_count==2 (excluded from simple slice)"
    assert analyze_sentence(rc)["cls"] == "relative_clause"

    pas = [_tok(1, "The", "the", "DET", 2, "det"), _tok(2, "fish", "fish", "NOUN", 4, "nsubj:pass"),
           _tok(3, "is", "be", "AUX", 4, "aux:pass"), _tok(4, "eaten", "eat", "VERB", 0, "root"),
           _tok(5, "by", "by", "ADP", 7, "case"), _tok(6, "the", "the", "DET", 7, "det"),
           _tok(7, "cat", "cat", "NOUN", 4, "obl")]
    assert _clause_count(pas) == 1, "passive must be clause_count==1 (simple)"
    assert analyze_sentence(pas)["cls"] == "passive"

    other = [_tok(1, "She", "she", "PRON", 3, "nsubj"), _tok(2, "is", "be", "AUX", 3, "cop"),
             _tok(3, "happy", "happy", "ADJ", 0, "root")]
    assert _clause_count(other) == 1, "copular nonverbal-root sentence still clause_count==1 (excluded by the SEPARATE root-UPOS check, not by clause_count)"
    print("[self_test] _clause_count matches analyze_sentence's own bucket boundaries on all 5 non-other + 1 "
          "other hand-built trees (single_clause_svo/compound_subject/passive->1(simple); "
          "vp_coordination/relative_clause->2(excluded))", flush=True)

    # (2) real_code_path (F.1): parse the REAL local corpus, apply the REAL simplicity filter, sample a tiny
    # real slice, run BOTH extraction arms against REAL sentences.
    simple_sorted, length_matched_pool_size = load_simple_sentences(CONLLU_PATH)
    assert length_matched_pool_size > 100, f"expected a sizeable length-matched pool, got {length_matched_pool_size}"
    assert 20 < len(simple_sorted) < length_matched_pool_size, (
        f"simple slice ({len(simple_sorted)}) should be a genuine, non-trivial, non-total subset of the "
        f"length-matched pool ({length_matched_pool_size}) -- either extreme signals a filter bug")
    rows, dist = build_rows_for_seed(simple_sorted, seed=7, n_per_seed=40)
    assert sum(dist.values()) == len(rows), f"distribution counts do not sum to sample size: {dist}"
    non_other = sum(v for c, v in dist.items() if c != "other_unhandled")
    assert non_other > 0, ("discriminator-fires check failed: a real 40-sentence simple-slice sample produced "
                            "ZERO non-other_unhandled construction classes")
    base_res = score_arm(rows, ie_extract_open)
    gated_res = score_arm(rows, ie_extract_open_gated)
    print(f"[self_test] real_code_path: length_matched_pool={length_matched_pool_size} simple_pool="
          f"{len(simple_sorted)} tiny-slice dist={dist} | BASELINE coverage="
          f"{base_res['coverage_sentence_rate']:.3f} precision={base_res['precision_on_attempted']} | "
          f"GATED coverage={gated_res['coverage_sentence_rate']:.3f} precision={gated_res['precision_on_attempted']}",
          flush=True)

    # (3) guard + OOS regression, both arms (reused verbatim from RUNG 5/5b).
    for sent, gold in GUARD_SENTENCES:
        gset = set(gold)
        assert set(ie_extract_open(sent)[0]) == gset, f"BASELINE guard regression on {sent!r}"
        assert set(ie_extract_open_gated(sent)[0]) == gset, f"GATED guard regression on {sent!r}"
    for s in OUT_OF_SCHEMA_CONTROL:
        assert ie_extract_open(s)[0] == [], f"BASELINE unexpectedly extracted on OOS control {s!r}"
        assert ie_extract_open_gated(s)[0] == [], f"GATED unexpectedly extracted on OOS control {s!r}"
    print("[self_test] guard-sentence regression + out-of-schema control PASS on both arms", flush=True)

    # (4) ARMS-MUST-DIFFER (META_RULE_AF): BASELINE vs GATED emitted-triple-set hash on the real tiny slice.
    base_all = sorted(set(t for r in rows for t in ie_extract_open(r["text"])[0]))
    gated_all = sorted(set(t for r in rows for t in ie_extract_open_gated(r["text"])[0]))
    h_base = hashlib.sha256(json.dumps(base_all, sort_keys=True).encode()).hexdigest()
    h_gated = hashlib.sha256(json.dumps(gated_all, sort_keys=True).encode()).hexdigest()
    assert h_base != h_gated, "META_RULE_AF VIOLATION: BASELINE and GATED bit-identical on real data"
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified (BASELINE emitted {len(base_all)} unique triples, "
          f"GATED emitted {len(gated_all)}, on the real 40-sentence simple-slice tiny sample)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
SEEDS_FULL = [7, 13, 19]
N_PER_SEED = 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [7] if run_mode == "smoke" else SEEDS_FULL
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * N_PER_SEED
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[realprose_rung6] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seeds, N_PER_SEED)
    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    print(f"[realprose_rung6] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[realprose_rung6] {msg}", flush=True)

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_per_seed": N_PER_SEED,
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        "corpus": {
            "name": "UD_English-EWT test split -- SIMPLE-SYNTAX SUBSET (PATH A)", "path": str(CONLLU_PATH),
            "license": "CC BY-SA 4.0",
            "register_note": "PROXY for early-reader register on SYNTAX/CLAUSE-STRUCTURE ONLY (objective "
                              "gold-parse-derived filter: token[5-12], single verbal root, clause_count<=1); "
                              "NOT vocabulary-controlled (does not filter for Dolch/Fry/CEFR-J early-reader "
                              "vocabulary) -- see module docstring CORPUS/PATH CHOICE for the full honest "
                              "trade-off vs PATH B (OneStopEnglish/Simple-Wikipedia + hand gold).",
            "length_matched_pool_size": agg["length_matched_pool_size"],
            "simple_pool_size": agg["simple_pool_size"],
            "simple_fraction_of_length_matched_pool": agg["simple_fraction_of_length_matched_pool"],
            "n_sampled_total": agg["n_total_sentences"],
        },
        "construction_distribution_counts": agg["construction_distribution_counts"],
        "construction_distribution_fractions": agg["construction_distribution_fractions"],
        "per_seed_distribution": agg["per_seed_distribution"],
        "arms": {
            "GATED_primary": {k: v for k, v in agg["gated_score"].items() if k != "rows"},
            "BASELINE_no_gate_informational": {k: v for k, v in agg["baseline_score"].items() if k != "rows"},
            "GATED_relaxed_irregular_verb_diagnostic":
                {k: v for k, v in agg["gated_relaxed_diagnostic"].items() if k != "rows"},
            "BASELINE_relaxed_irregular_verb_diagnostic":
                {k: v for k, v in agg["baseline_relaxed_diagnostic"].items() if k != "rows"},
            "SVO_ONLY_GATED_diagnostic": (
                {k: v for k, v in agg["svo_only_gated_diagnostic"].items() if k != "rows"}
                if agg["svo_only_gated_diagnostic"] else None),
        },
        "guard_regression_ok_gated": agg["guard_regression_ok_gated"],
        "guard_regression_ok_baseline": agg["guard_regression_ok_baseline"],
        "oos_control_fired_gated": agg["oos_control_fired_gated"],
        "oos_control_fired_baseline": agg["oos_control_fired_baseline"],
        "sample_gated_rows": agg["gated_score"]["rows"][:60],
        "sample_baseline_rows": agg["baseline_score"]["rows"][:60],
        "prereg": {
            "hard_pass": "gated_precision_on_attempted>=0.60 AND gated_coverage_sentence_rate>=0.05 AND "
                         "guard_regression_ok_gated AND oos_control_fired_gated AND "
                         "simple_fraction_of_length_matched_pool>=0.10",
            "hard_fail": "gated_precision_on_attempted<0.50 OR gated_coverage_sentence_rate<0.03 OR "
                         "NOT guard_regression_ok_gated OR simple_fraction_of_length_matched_pool<0.10",
            "hp_scope": "GATED (RUNG 5b abstain-gated extractor) is the PRIMARY discriminator -- the "
                        "pipeline's current best-available mechanism. BASELINE (no gate) and both RELAXED "
                        "irregular-verb-lemma diagnostics are informational-only, reported per the contract's "
                        "explicit ask for with/without-gate numbers.",
            "corpus_path_choice": "PATH A: simple-syntax subset of UD-EWT (general web register), an "
                                  "objective gold-parse-derived proxy for early-reader SYNTAX only, NOT "
                                  "vocabulary-controlled early-reader text. See module docstring for the "
                                  "3 concrete reasons over PATH B (OneStopEnglish/Simple-Wikipedia + hand "
                                  "gold), and the honest register_note in the corpus block above.",
            "simplicity_filter": "token_count in [5,12] AND single root AND root UPOS in (VERB,AUX) AND "
                                 "_clause_count<=1 -- ALL computed from the GOLD CoNLL-U parse BEFORE any "
                                 "extraction is attempted; NEVER reverse-engineered from extraction success "
                                 "(HONEST GUARD, contract-mandated).",
            "gold_method": "identical to RUNG 5 (analyze_sentence, imported unmodified, already validated "
                            "at RUNG 5's own self-test against 5 hand-built dependency trees).",
            "compute_architecture": "sequential-CPU; pure syntactic parsing + dependency-tree traversal, no "
                                    "VSA store; wall time trivial (MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer + dependency-classifier test)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "runner_python_u_only (timeout_s < 1800; not mandatory, cell wall time is "
                                 "seconds, matching RUNG 5/5b's own precedent)",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["parse_conllu (real local corpus file, imported from RUNG 5 "
                                         "unmodified)", "load_simple_sentences (NEW objective filter, this "
                                         "cell)", "analyze_sentence (RUNG 5, imported unmodified)",
                                         "ie_extract_open (RUNG 5 BASELINE, imported unmodified)",
                                         "ie_extract_open_gated (RUNG 5b GATED, imported unmodified)",
                                         "nltk.pos_tag (real classical averaged-perceptron call)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same "
                       "as RUNG 5/5b.",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a "
                               "runtime sys.modules transitive-closure check after nltk use, both asserted "
                               "at self-test",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report) -- top hits "
                                "were generic wordnet/verbnet 'register' concept-graph nodes (cosine<=0.376), "
                                "not prior experiment cells; this is a genuinely novel measurement within the "
                                "actively-developed RUNG 2-5b open-text-reading arc, not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[realprose_rung6] metrics written -> {out_dir / 'metrics.json'}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
