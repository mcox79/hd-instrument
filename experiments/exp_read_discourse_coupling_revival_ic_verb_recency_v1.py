"""exp_read_discourse_coupling_revival_ic_verb_recency_v1 -- the COUPLING-REVIVAL cell (Director spec,
notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md, "COUPLING-REVIVAL SPEC" block under
"ROADMAP (USER-steered)").

TRIGGER (verbatim from the dispatching contract): the prior state-of-mind coupling cells (v1 hand-authored,
v2 realcorpus) were VET-corrected to MIDDLE_BAND/MEASURED_MECHANISM because WITHOUT_STATE was a strawman
abstain-all arm (delta === WITH's absolute accuracy, zero extra information) and the declared headline
mechanism (role-ranked Grosz-Joshi-Weinstein Cf resolver) NEVER FIRED -- v2's WITH=0.833 reduced entirely to
"bind he -> most recent grammatical subject," i.e. RECENCY, not centering. A follow-up drill (centering-Cf,
note research_coreference_centering_cf_ranking... 2026-07-17, 3 children: biology/computational/corpus-design)
found the computational literature says PURE RECENCY is a STRONG baseline centering/role-ranking does NOT
clearly beat on natural text (Tetreault 2001: Hobbs-recency 89% >= centering-BFP 79% on news; Strube's
'Never Look Back' S-list = pure recency ties/beats centering). BUT the biology says a genuine non-recency
mechanism exists -- VERB-SEMANTIC / IMPLICIT CAUSALITY (Garvey & Caramazza 1974: "Sally frightened Mary
because she"->Sally; "Sally loved Mary because she"->Mary; the VERB flips the referent, independent of
role+recency). This cell PIVOTS the revival away from role-ranking (predicted to lose) toward verb-semantic/
implicit-causality prediction, per the Director's concrete spec.

DESIGN GATE (mandatory, verified BEFORE full -- see module-level constants + self_test for each check):
  1. REAL BASELINE (non-strawman, field-standard) = RECENCY / Hobbs-naive: the antecedent candidate closer
     (fewer intervening tokens) to the pronoun always wins. In the canonical "NP1 VERB NP2 because PRON"
     frame this is always NP2 (the object -- the last-mentioned entity before the connective). This is the
     REAL opponent the verb-semantic mechanism must beat, not an abstain-everything strawman.
  2. CAN-FAIL: the verb-semantic (IC_VERB) mechanism MUST be able to lose. It loses by CONSTRUCTION on the
     ES-class ("love"-type) items (there it agrees with recency, so it cannot be distinguished from it) and,
     genuinely, on any REAL-corpus disagreement case if the real data ever contradicts the categorical
     bias direction (checked, not assumed -- see the REAL_LITBANK arm below). Self-test asserts the
     construction-artifact / can-fail probes fire correctly (Prediction in self_test: a probe verb absent
     from the lexicon must make IC_VERB ABSTAIN, not guess -- a genuine failure mode the mechanism can hit).
  3. DIFFICULTY-ON: every headline number is reported on the DISAGREEMENT SUBSET specifically (EO-class items,
     "frighten"-type, where recency picks NP2 but verb-bias picks NP1 -- a genuine divergence), never on the
     trivial full-corpus agreement rate. ES-class ("love"-type, recency and verb-bias coincide on NP2) is
     reported SEPARATELY as an agreement/regression sanity check (verb-semantics must not HURT when it agrees
     with recency), not folded into the headline.
  4. ONE VARIABLE: RECENCY and IC_VERB are scored on the IDENTICAL item set, identical candidate-extraction
     rule, identical gold source -- they differ ONLY in the resolution mechanism (ignore-verb-pick-nearest vs
     verb-bias-lookup-override-recency-when-EO).
  5. CORPUS (two arms, BOTH disclosed with n + license):
     (a) REAL: LitBank (github.com/dbamman/litbank, CC BY 4.0, commit 3e50db0ffc033d7ccbb94f4d88f6b99210328ed8),
         100 books, mined via the declared structural rule in tools/derive_litbank_ic_disagreement_v1.py
         (see that file + data/corpora/litbank_ic_derived_v1/PROVENANCE.md for the full rule + a DISCLOSED,
         load-bearing NEGATIVE finding: this exact frame occurs only 5 times across all 100 books' LitBank-
         annotated openings (~200K tokens), and ALL 5 are NEUTRAL-class (no established IC verb) -- ZERO EO
         or ES real hits. This is NOT a mining bug (spot-checked; matches why the psycholinguistics field
         studies IC via completion-norming experiments, not corpus counts). Consequence, honestly built into
         the pre-reg below: the REAL arm cannot supply a real EO disagreement-subset accuracy at this corpus
         scale (n=0 < the pre-registered REAL_MIN_DISAGREEMENT_N floor) -- it instead supplies (i) a genuine
         zero-hallucination guardrail measurement (does IC_VERB correctly abstain on the 5 real out-of-lexicon
         verbs it actually meets in the wild) and (ii) an honest, disclosed real-data-insufficiency verdict
         component, per the project's "SYNTHETIC-TOY-CORPUS OUTCOMES CAN BE CONSTRUCTION-DETERMINED -- REAL
         QUESTIONS NEED REAL DATA" standing discipline.
     (b) CONSTRUCTED: IC minimal-pairs (Garvey & Caramazza 1974 paradigm), same NP1-VERB-NP2-because-PRON
         template, varying same-gender name pairs + verbs drawn from the SAME glass-box lexicon used for (a).
         Gold = the published CATEGORICAL bias direction (EO->NP1, ES->NP2), CITED (Garvey & Caramazza 1974;
         Brown & Fish 1983; Rudolph & Foersterling 1997 meta-analysis; Kehler/Rohde et al. 2008) -- a real,
         externally-established fact about human sentence processing, not invented here. HONESTLY FLAGGED
         (construction-artifact guard, same convention as the sibling wsm_coupling_realcorpus_v2 cell): since
         gold on the EO-disagreement subset is DEFINED as the same table IC_VERB looks up, this arm's 100%-vs-
         0% split is EXPECTED BY CONSTRUCTION, not an empirical discovery -- it validates (i) the mechanism is
         IMPLEMENTED correctly (no lookup/indexing bugs), (ii) recency really is the strong, real, well-defined
         opponent it claims to be on this subset, (iii) the guardrail holds when the verb is genuinely unknown.
         It CANNOT alone produce a HARD_PASS (see verdict gate).

GLASS-BOX / NO-LLM: the IC verb-bias lexicon is a small (~65-word) inspectable Python dict (EO/ES/NEUTRAL
  keys), CITED from the classic implicit-causality literature (no neural net, no embeddings, no spaCy/Stanza/
  transformers). RECENCY is a one-line structural rule (nearest mention wins). Candidate extraction over the
  real corpus reuses LitBank's OWN human coreference annotation (not a parser) -- fully symbolic throughout.

METRICS (reported separately, matching the reused convention):
  constructed_disagreement (EO, n~43): recency_acc, ic_acc, construction_artifact_detected.
  constructed_agreement (ES, n~28): recency_acc, ic_acc (both should stay high -- verb-semantics must not hurt
    when it agrees with recency).
  constructed_guardrail (NEUTRAL, n~13): ic_wrong_guess_rate (must be 0.0 -- abstain on unknown verbs).
  real_litbank (n=5, all NEUTRAL): real_guardrail_wrong_guess_rate (must be 0.0); real_eo_n / real_es_n (both
    measured 0 -- disclosed, not hidden); real_data_sufficient (n_real_eo >= REAL_MIN_DISAGREEMENT_N=6).

PRE-REG (envelope-fail-bands; set BEFORE running the FULL verdict computation -- the mining yield itself was
  already measured during authoring, exactly like a discriminator-preview smoke check; the bands below are
  honest about what that preview showed, per DISCRIMINATOR-MUST-SURVIVE-SCALE discipline: a cell should not
  be dispatched pretending suspense about a number already measured):
  HARD-PASS (real capability demonstrated on real data): real_data_sufficient AND
    real_ic_acc_on_disagreement >= real_recency_acc_on_disagreement + 0.30 AND
    real_guardrail_wrong_guess_rate == 0.0 AND constructed_guardrail_wrong_guess_rate == 0.0 AND
    constructed_agreement_ic_acc >= 0.90 (no regression when verb-semantics agrees with recency).
  HARD-FAIL (verb-semantics does NOT help, or hallucinates):
    (real_data_sufficient AND real_ic_acc_on_disagreement <= real_recency_acc_on_disagreement) OR
    real_guardrail_wrong_guess_rate > 0.0 OR constructed_guardrail_wrong_guess_rate > 0.0 OR
    constructed_agreement_ic_acc < 0.80 (verb-semantics regressed the easy agreement cases).
  MIDDLE_BAND (otherwise -- covers the MEASURED real-data-insufficient case: real_data_sufficient == False
    but every guardrail/construction check is clean, i.e. mechanism correctly implemented + zero-hallucination
    holds, but the real empirical capability question is UNTESTABLE at LitBank's current annotated scale):
    reported explicitly as REAL_DATA_INSUFFICIENT_FOR_CAPABILITY_VERDICT, not silently upgraded.
  P estimate: P(HARD_PASS)=0.05 (HYPOTHESIZED@this docstring -- deflated hard: the mining yield was already
    measured at n_real_eo=0, so a genuine on-real-data HARD_PASS is not reachable by this cell as authored;
    honestly disclosing this rather than re-rolling a rosier P). P(MIDDLE_BAND, data-insufficient)=0.85.
    P(HARD_FAIL, guardrail/regression break)=0.10.

COMPUTE: fully symbolic, deterministic (NO RNG anywhere -- no seeds to declare, matches the reused v2/coref
  cells' convention). No VSA/torch/numpy needed (a coreference-mechanism comparison, not a capacity/fit
  question -- COMPUTE-PROPORTIONALITY: cheapest decisive method for a directional-gate question). Wall time
  < 1s (5 real items + ~84 constructed items, pure Python). Local, no queue/GPU/atoms/push. ASCII-only.
  Storage: no_storage. smoke == full (fixed, tiny, deterministic corpus -- nothing to shrink).
  progress_logging = print_flush_true (well under the 1800s mandatory-heartbeat threshold, added anyway).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): RECENCY vs IC_VERB predicted-side sequences differ on
#     the constructed EO-disagreement subset (the mechanism actually overrides recency there).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- fully symbolic, discrete cluster-id lookup/comparison; no
#     phasor/argmax noise anywhere in this cell.
# - baseline_in_band: N/A BY DESIGN on the constructed arm (RECENCY's 0.0 acc on the EO-disagreement subset
#     is the LOGICALLY NECESSARY, CITED consequence of scoring against gold defined as the opposite category
#     -- the CONSTRUCTION-ARTIFACT GUARD below is the honest replacement check, exactly mirroring the sibling
#     wsm_coupling_realcorpus_v2 cell's convention); genuinely in-band on the REAL arm (measured, not assumed).
# - discriminator survives scale: fixed real+constructed item sets (no N/scale axis). Discriminators = (1)
#     RECENCY and IC_VERB predicted-side sequences differ on the EO subset (arms-differ), (2) IC_VERB
#     abstains (never guesses) on every NEUTRAL-class item, real and constructed (guardrail), (3) the
#     construction-artifact guard fires on the constructed EO subset's expected 100%-vs-0% split, (4) the
#     real_data_sufficient gate correctly reads False given the measured real_eo_n=0 (data-scarcity is
#     surfaced, not hidden).
# - HARD_PASS strictly above floor; explicit bands above. Numbers tagged MEASURED@ / HYPOTHESIZED@ / CITED@.
# - real_code_path (F.1): self-test opens+parses the REAL derived JSON file at its REAL repo path and
#     recomputes gold/verb-class from RAW fields (not trusting precomputed convenience fields blindly), and
#     builds constructed items via the REAL build_constructed_items() function -- no synthetic-only branch.
# - deterministic_seeding (F.5): N/A -- no RNG anywhere in this cell (fully symbolic deterministic lookup).
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import json
import argparse
import time
import hashlib
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_coupling_revival_ic_verb_recency_v1"

# --- GENUINE REUSE, UNMODIFIED: the glass-box IC verb-bias lexicon + the LitBank mining rule live in the
# mining script (tools/derive_litbank_ic_disagreement_v1.py) -- imported here, not re-typed, so the cell's
# mechanism and the corpus-derivation rule can never silently drift apart. ---
from tools.derive_litbank_ic_disagreement_v1 import (
    EO_VERBS, ES_VERBS, NEUTRAL_VERBS, IC_LEXICON, LITBANK_COMMIT,
)

REAL_DERIVED_PATH = REPO / "data" / "corpora" / "litbank_ic_derived_v1" / "litbank_ic_disagreement_derived_v1.json"
REAL_MIN_DISAGREEMENT_N = 6           # pre-registered real-data floor (matches the sibling coref cell's
                                       # n>=6 convention) below which a real-data HARD_PASS/HARD_FAIL cannot
                                       # be declared -- only MIDDLE_BAND/data-insufficient.


# ---------------------------------------------------------------------------
# mechanisms: RECENCY (real Hobbs-naive baseline) vs IC_VERB (verb-semantic / implicit-causality override).
# Both operate on the SAME item schema: {"verb": str, gold determined externally}. Neither sees anything the
# other doesn't -- ONE VARIABLE (the resolution rule).
# ---------------------------------------------------------------------------
def recency_predict(item):
    """Hobbs-naive / most-recent: the candidate closer to the pronoun always wins. In the canonical
    NP1-VERB-NP2-because-PRON frame this is always NP2 (the object -- last mentioned before the connective).
    This IS the real, field-standard opponent (Tetreault 2001; Strube 'Never Look Back') -- not a strawman."""
    return "NP2"


def ic_verb_predict(item):
    """Verb-semantic / implicit-causality override: look up the verb's CITED categorical bias class. EO
    ("frighten"-class) -> NP1 (subject) bias; ES ("love"-class) -> NP2 (object) bias (agrees with recency);
    unknown verb -> ABSTAIN (None) -- the mechanism must NOT fabricate a directional claim it has no basis
    for (the zero-hallucination guardrail; this is the mechanism's genuine, measurable can-fail surface)."""
    klass = IC_LEXICON.get(item["verb"])
    if klass == "EO":
        return "NP1"
    if klass == "ES":
        return "NP2"
    return None


# ---------------------------------------------------------------------------
# CONSTRUCTED arm: IC minimal-pairs (Garvey & Caramazza 1974 paradigm). Same-gender name pairs (so gender
# never trivially disambiguates -- only recency-vs-verb-semantics can). Deterministic construction (verb
# lists sorted for reproducibility; no RNG anywhere).
# ---------------------------------------------------------------------------
MALE_PAIRS = [("John", "Peter"), ("Henry", "Charles"), ("Edward", "Arthur"), ("George", "Thomas")]
FEMALE_PAIRS = [("Mary", "Anne"), ("Emma", "Clara"), ("Alice", "Helen"), ("Grace", "Rose")]


def build_constructed_items():
    """Deterministic construction: for each verb in the (sorted, for reproducibility) EO/ES/NEUTRAL lexicon,
    cycle through 8 same-gender name pairs (4 male, 4 female, alternating) and emit one item. Template =
    "{NP1} {VERB} {NP2} because {PRON} had been like that all day." -- the predicate is DELIBERATELY
    identity-neutral (says nothing that would let a reader guess the referent from content alone), so the
    ONLY information available to a resolver is (a) recency (NP2 is closer) and (b) the verb's own semantics
    -- exactly isolating the two mechanisms under test, one variable."""
    items = []
    all_verbs = sorted(EO_VERBS) + sorted(ES_VERBS) + sorted(NEUTRAL_VERBS)
    for i, verb in enumerate(all_verbs):
        male = (i % 2 == 0)
        pair = MALE_PAIRS[(i // 2) % len(MALE_PAIRS)] if male else FEMALE_PAIRS[(i // 2) % len(FEMALE_PAIRS)]
        np1, np2 = pair
        pron = "he" if male else "she"
        klass = IC_LEXICON.get(verb, "NEUTRAL")
        gold_side = "NP1" if klass == "EO" else ("NP2" if klass == "ES" else None)
        text = f"{np1} {verb} {np2} because {pron} had been like that all day."
        items.append({
            "source": "constructed", "verb": verb, "verb_class": klass, "gold_side": gold_side,
            "np1_name": np1, "np2_name": np2, "pron": pron, "text": text,
        })
    return items


# ---------------------------------------------------------------------------
# REAL arm: load the LitBank-derived JSON (mined offline, committed; see tools/derive_litbank_ic_disagree...
# and data/corpora/litbank_ic_derived_v1/PROVENANCE.md). RECOMPUTE gold_side + verb_class from the RAW fields
# (book-annotated cluster ids + verb string) rather than trusting the JSON's own precomputed convenience
# fields blindly -- a consistency cross-check catches drift between the mining script and this cell's copy
# of the lexicon (they are the SAME import, so they cannot drift, but the recompute-not-trust habit is kept).
# ---------------------------------------------------------------------------
def load_real_items(path=REAL_DERIVED_PATH):
    with open(path, "r", encoding="utf-8") as f:
        derived = json.load(f)
    items = []
    for raw in derived["items"]:
        gold_side = "NP1" if raw["gold_cluster"] == raw["np1_cluster"] else "NP2"
        assert gold_side == raw["gold_side"], (
            f"REAL item gold_side recompute mismatch (mining-script drift?): {raw}")
        klass = IC_LEXICON.get(raw["verb"], "NEUTRAL")
        assert klass == raw["verb_class"], f"REAL item verb_class recompute mismatch: {raw}"
        items.append({
            "source": "real_litbank", "verb": raw["verb"], "verb_class": klass, "gold_side": gold_side,
            "text": raw["text"], "book_id": raw["book_id"], "sidx": raw["sidx"],
        })
    return items, derived


# ---------------------------------------------------------------------------
# analysis + verdict.
# ---------------------------------------------------------------------------
def _score(items, is_guardrail_set=False):
    """Two DISTINCT scoring modes, kept structurally separate (a prior draft of this function conflated them
    -- caught live during this cell's own smoke: REAL NEUTRAL-class items DO have a genuine gold antecedent
    (LitBank's real human annotation resolves every pronoun, including ones after out-of-lexicon verbs) --
    'gold_side is None' is NOT a valid guardrail signal for the REAL arm, only for the CONSTRUCTED arm's
    intentionally-gold-less NEUTRAL items. The guardrail question is ALWAYS 'did IC_VERB fabricate a
    directional call despite having no lexicon basis for this verb', which is answered purely by
    ic_verb_predict(it) is not None -- independent of whether real gold happens to exist.
    is_guardrail_set=False (EO disagreement / ES agreement subsets): report recency_acc / ic_acc against
      gold_side (skips items with gold_side is None, i.e. the constructed NEUTRAL class if ever misrouted here).
    is_guardrail_set=True (NEUTRAL subsets, real or constructed): report ic_wrong_guess_rate = fraction where
      IC_VERB guessed (non-None) instead of abstaining -- the zero-hallucination guardrail measurement."""
    n = len(items)
    if is_guardrail_set:
        if n == 0:
            return {"n": 0, "ic_wrong_guess_rate": None}
        wrong = sum(1 for it in items if ic_verb_predict(it) is not None)
        return {"n": n, "ic_wrong_guess_rate": wrong / float(n)}
    if n == 0:
        return {"n": 0, "n_with_gold": 0, "recency_acc": None, "ic_acc": None}
    has_gold = [it for it in items if it["gold_side"] is not None]
    recency_acc = (sum(int(recency_predict(it) == it["gold_side"]) for it in has_gold) / float(len(has_gold))
                   ) if has_gold else None
    ic_acc = (sum(int(ic_verb_predict(it) == it["gold_side"]) for it in has_gold) / float(len(has_gold))
              ) if has_gold else None
    return {"n": n, "n_with_gold": len(has_gold), "recency_acc": recency_acc, "ic_acc": ic_acc}


def analyze_all():
    constructed = build_constructed_items()
    real_items, real_meta = load_real_items()

    c_eo = [it for it in constructed if it["verb_class"] == "EO"]           # constructed disagreement subset
    c_es = [it for it in constructed if it["verb_class"] == "ES"]           # constructed agreement subset
    c_neu = [it for it in constructed if it["verb_class"] == "NEUTRAL"]     # constructed guardrail

    r_eo = [it for it in real_items if it["verb_class"] == "EO"]            # real disagreement subset
    r_es = [it for it in real_items if it["verb_class"] == "ES"]            # real agreement subset
    r_neu = [it for it in real_items if it["verb_class"] == "NEUTRAL"]      # real guardrail

    constructed_disagreement = _score(c_eo)
    constructed_agreement = _score(c_es)
    constructed_guardrail = _score(c_neu, is_guardrail_set=True)
    real_disagreement = _score(r_eo)
    real_agreement = _score(r_es)
    real_guardrail = _score(r_neu, is_guardrail_set=True)

    construction_artifact_detected = (
        constructed_disagreement["n"] > 0 and
        constructed_disagreement["ic_acc"] is not None and constructed_disagreement["ic_acc"] >= 0.999 and
        constructed_disagreement["recency_acc"] is not None and constructed_disagreement["recency_acc"] <= 0.001
    )
    real_data_sufficient = real_disagreement["n"] >= REAL_MIN_DISAGREEMENT_N

    rec_seq = tuple(recency_predict(it) for it in c_eo)
    ic_seq = tuple(ic_verb_predict(it) for it in c_eo)
    arms_differ = (rec_seq != ic_seq) and len(c_eo) > 0

    return {
        "constructed_disagreement": constructed_disagreement, "constructed_agreement": constructed_agreement,
        "constructed_guardrail": constructed_guardrail,
        "real_disagreement": real_disagreement, "real_agreement": real_agreement,
        "real_guardrail": real_guardrail,
        "construction_artifact_detected": construction_artifact_detected,
        "real_data_sufficient": real_data_sufficient,
        "arms_differ": arms_differ,
        "n_constructed_total": len(constructed), "n_real_total": len(real_items),
        "real_meta": {k: v for k, v in real_meta.items() if k != "items"},
        "rec_seq_hash": hashlib.sha256(repr(rec_seq).encode()).hexdigest(),
        "ic_seq_hash": hashlib.sha256(repr(ic_seq).encode()).hexdigest(),
    }


def compute_verdict(a):
    cd, ca, cg = a["constructed_disagreement"], a["constructed_agreement"], a["constructed_guardrail"]
    rd, rg = a["real_disagreement"], a["real_guardrail"]
    real_suff = a["real_data_sufficient"]

    real_guard_wrong = rg["ic_wrong_guess_rate"] if rg["ic_wrong_guess_rate"] is not None else 0.0
    c_guard_wrong = cg["ic_wrong_guess_rate"] if cg["ic_wrong_guess_rate"] is not None else 0.0
    ca_ic_acc = ca["ic_acc"] if ca["ic_acc"] is not None else 0.0

    hp = (
        real_suff and rd["ic_acc"] is not None and rd["recency_acc"] is not None and
        (rd["ic_acc"] - rd["recency_acc"]) >= 0.30 and
        real_guard_wrong == 0.0 and c_guard_wrong == 0.0 and ca_ic_acc >= 0.90
    )
    hf = (
        (real_suff and rd["ic_acc"] is not None and rd["recency_acc"] is not None and
         rd["ic_acc"] <= rd["recency_acc"]) or
        real_guard_wrong > 0.0 or c_guard_wrong > 0.0 or ca_ic_acc < 0.80
    )
    tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    localize = []
    if not real_suff:
        localize.append(f"REAL_DATA_INSUFFICIENT_FOR_CAPABILITY_VERDICT: real disagreement-subset n="
                         f"{rd['n']} < floor {REAL_MIN_DISAGREEMENT_N} (LitBank's ~200K-token annotated "
                         f"sample across 100 books yields this exact frame only rarely -- disclosed, not a "
                         f"mining bug; see PROVENANCE.md)")
    if real_guard_wrong > 0.0:
        localize.append(f"REAL GUARDRAIL BREACH: IC_VERB guessed on {real_guard_wrong:.0%} of real "
                         f"out-of-lexicon-verb items instead of abstaining (hallucination)")
    if c_guard_wrong > 0.0:
        localize.append(f"CONSTRUCTED GUARDRAIL BREACH: IC_VERB guessed on {c_guard_wrong:.0%} of "
                         f"constructed out-of-lexicon-verb items")
    if ca_ic_acc < 0.90:
        localize.append(f"constructed agreement-subset ic_acc={ca_ic_acc:.3f} below 0.90 "
                         f"(verb-semantics regressed cases where it should agree with recency)")
    if a["construction_artifact_detected"]:
        localize.append("CONSTRUCTION_ARTIFACT_DETECTED on the constructed disagreement subset: "
                         "ic_acc>=0.999 and recency_acc<=0.001 exactly -- EXPECTED BY CONSTRUCTION (gold "
                         "there is defined as the same table IC_VERB looks up), NOT independent capability "
                         "evidence; disclosed, does not by itself justify HARD_PASS")
    weakest = localize if localize else ["none (real data sufficient, verb-semantics beat recency on real "
                                          "disagreement cases, guardrails clean, no regression)"]

    msg = (f"{tier} | REAL disagreement n={rd['n']} (floor={REAL_MIN_DISAGREEMENT_N}, sufficient={real_suff}) "
           f"recency_acc={rd['recency_acc']} ic_acc={rd['ic_acc']} | REAL guardrail wrong_guess_rate="
           f"{real_guard_wrong:.3f} (n={rg['n']}) | CONSTRUCTED disagreement(EO) n={cd['n']} recency_acc="
           f"{cd['recency_acc']:.3f} ic_acc={cd['ic_acc']:.3f} construction_artifact="
           f"{a['construction_artifact_detected']} | CONSTRUCTED agreement(ES) n={ca['n']} recency_acc="
           f"{ca['recency_acc']:.3f} ic_acc={ca['ic_acc']:.3f} | CONSTRUCTED guardrail wrong_guess_rate="
           f"{c_guard_wrong:.3f} (n={cg['n']}) | arms_differ={a['arms_differ']} | weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_discourse_coupling_revival_ic_verb_recency_v1",
           "smoke": "exp_read_discourse_coupling_revival_ic_verb_recency_v1_smoke",
           "self_test": "exp_read_discourse_coupling_revival_ic_verb_recency_v1_selftest"}[run_mode]
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
# self-test: EXERCISE THE REAL code path (real file I/O against the real repo path, real lexicon, real
# construction function) + assert every discriminator fires correctly, INCLUDING the can-fail / guardrail /
# construction-artifact / real-data-insufficiency checks the design gate requires.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (lexicon import, real derived-JSON file read, constructed "
          "item builder)...", flush=True)

    # (1) lexicon sanity: EO/ES/NEUTRAL are disjoint (a verb cannot carry two biases at once).
    assert not (EO_VERBS & ES_VERBS), "EO/ES verb sets overlap"
    assert not (EO_VERBS & NEUTRAL_VERBS), "EO/NEUTRAL verb sets overlap"
    assert not (ES_VERBS & NEUTRAL_VERBS), "ES/NEUTRAL verb sets overlap"
    assert len(EO_VERBS) >= 15 and len(ES_VERBS) >= 10 and len(NEUTRAL_VERBS) >= 8, "lexicon too small"

    # (2) mechanisms: RECENCY always picks NP2; IC_VERB picks per class, ABSTAINS (None) on unknown verb --
    # the genuine can-fail / zero-hallucination surface.
    assert recency_predict({"verb": "frightened"}) == "NP2"
    assert ic_verb_predict({"verb": "frightened"}) == "NP1"     # EO
    assert ic_verb_predict({"verb": "loved"}) == "NP2"          # ES
    assert ic_verb_predict({"verb": "saw"}) is None             # NEUTRAL -- must abstain
    assert ic_verb_predict({"verb": "zzz_not_a_real_verb"}) is None  # genuinely unknown -- must abstain

    # (3) REAL FILE I/O: the derived LitBank JSON must exist at its real repo path and parse.
    assert REAL_DERIVED_PATH.exists(), f"real derived corpus missing: {REAL_DERIVED_PATH}"
    real_items, real_meta = load_real_items()
    assert real_meta["license"].startswith("CC-BY"), "real corpus license missing/wrong"
    assert real_meta["litbank_commit"] == LITBANK_COMMIT, "real corpus commit hash mismatch (drift?)"
    assert real_meta["n_books"] == 100, f"expected 100 books scanned, got {real_meta['n_books']}"
    assert len(real_items) >= 1, "real corpus mining yielded zero items -- something broke"

    # (4) CONSTRUCTED builder: real construction function, deterministic (no RNG), covers all 3 classes.
    constructed = build_constructed_items()
    assert len(constructed) == len(EO_VERBS) + len(ES_VERBS) + len(NEUTRAL_VERBS)
    c_eo = [it for it in constructed if it["verb_class"] == "EO"]
    c_es = [it for it in constructed if it["verb_class"] == "ES"]
    c_neu = [it for it in constructed if it["verb_class"] == "NEUTRAL"]
    assert len(c_eo) == len(EO_VERBS) and len(c_es) == len(ES_VERBS) and len(c_neu) == len(NEUTRAL_VERBS)
    for it in c_eo:
        assert it["gold_side"] == "NP1"
    for it in c_es:
        assert it["gold_side"] == "NP2"
    for it in c_neu:
        assert it["gold_side"] is None

    # (5) META_RULE_AF ARMS-MUST-DIFFER: RECENCY and IC_VERB predicted-side sequences differ on the EO subset
    # (the mechanism genuinely overrides recency there -- not a no-op).
    rec_seq = [recency_predict(it) for it in c_eo]
    ic_seq = [ic_verb_predict(it) for it in c_eo]
    assert rec_seq != ic_seq, "META_RULE_AF: RECENCY and IC_VERB identical on EO subset (mechanism is a no-op)"
    assert all(r == "NP2" for r in rec_seq), "recency must always pick NP2"
    assert all(i == "NP1" for i in ic_seq), "IC_VERB must pick NP1 on every EO item"

    # (6) GUARDRAIL: IC_VERB must NEVER guess on NEUTRAL-class items, real OR constructed (zero-hallucination).
    for it in c_neu:
        assert ic_verb_predict(it) is None, f"GUARDRAIL FAIL (constructed): guessed on NEUTRAL verb {it['verb']!r}"
    real_neu = [it for it in real_items if it["verb_class"] == "NEUTRAL"]
    assert len(real_neu) >= 1, "expected at least 1 real NEUTRAL-class item (measured yield)"
    for it in real_neu:
        assert ic_verb_predict(it) is None, f"GUARDRAIL FAIL (real): guessed on real NEUTRAL verb {it['verb']!r}"

    # (7) full analysis + verdict on the REAL code path.
    a = analyze_all()
    tier, msg, weakest = compute_verdict(a)

    # (8) construction-artifact guard MUST fire on the constructed disagreement subset (this IS the expected,
    # measured outcome -- disclosed, not hidden; assert it is correctly DETECTED and FLAGGED, mirroring the
    # sibling wsm_coupling_realcorpus_v2 convention).
    assert a["construction_artifact_detected"] is True, (
        "construction-artifact guard failed to detect the expected constructed-arm 100%-vs-0% split")

    # (9) real-data-sufficiency gate must correctly read False given the MEASURED real corpus (n_real_eo=0):
    # this is the honest, disclosed negative finding this cell is built to surface, not to hide.
    assert a["real_disagreement"]["n"] == 0, (
        f"expected 0 real EO (disagreement) hits per the measured PROVENANCE.md finding, got "
        f"{a['real_disagreement']['n']} -- if this now differs the corpus file changed; re-verify honestly")
    assert a["real_data_sufficient"] is False, "real_data_sufficient should read False given n_real_eo=0"

    # (10) sanity: constructed agreement subset (ES) -- both mechanisms should score high (they agree there).
    assert a["constructed_agreement"]["recency_acc"] >= 0.90
    assert a["constructed_agreement"]["ic_acc"] >= 0.90

    assert tier == "MIDDLE_BAND", (
        f"given the measured real-data-insufficient state + clean guardrails, expected MIDDLE_BAND, got {tier}")

    # (11) CAN-FAIL discriminator probes: verify compute_verdict() genuinely CAN land HARD_FAIL and HARD_PASS
    # under synthetic what-if inputs (the design gate's mandatory check that the discriminator is not
    # analytically pinned to always land MIDDLE_BAND regardless of the data it's fed).
    def _synth(real_n, real_ic_acc, real_rec_acc, real_guard_wrong=0.0, c_guard_wrong=0.0, ca_ic_acc=1.0,
               construction_flag=True):
        return {
            "constructed_disagreement": {"n": 44, "recency_acc": 0.0, "ic_acc": 1.0},
            "constructed_agreement": {"n": 28, "recency_acc": 1.0, "ic_acc": ca_ic_acc},
            "constructed_guardrail": {"n": 13, "ic_wrong_guess_rate": c_guard_wrong},
            "real_disagreement": {"n": real_n, "recency_acc": real_rec_acc, "ic_acc": real_ic_acc},
            "real_agreement": {"n": 0, "recency_acc": None, "ic_acc": None},
            "real_guardrail": {"n": 5, "ic_wrong_guess_rate": real_guard_wrong},
            "construction_artifact_detected": construction_flag, "real_data_sufficient": real_n >= REAL_MIN_DISAGREEMENT_N,
            "arms_differ": True,
        }

    # (11a) if real data WERE sufficient and verb-semantics genuinely beat recency by a wide margin, with
    # every guardrail clean -> HARD_PASS must be reachable.
    tier_pass, _m, _w = compute_verdict(_synth(real_n=10, real_ic_acc=0.90, real_rec_acc=0.20))
    assert tier_pass == "HARD_PASS", f"CAN-FAIL probe: expected HARD_PASS reachable, got {tier_pass}"

    # (11b) if real data WERE sufficient but verb-semantics does NOT beat recency (the computational
    # literature's genuine prediction that recency is a strong baseline) -> HARD_FAIL must fire. THIS is the
    # mandatory can-fail check: the discriminator can genuinely land HARD_FAIL, not just MIDDLE_BAND/HARD_PASS.
    tier_fail, _m, _w = compute_verdict(_synth(real_n=10, real_ic_acc=0.30, real_rec_acc=0.70))
    assert tier_fail == "HARD_FAIL", f"CAN-FAIL probe: expected HARD_FAIL reachable, got {tier_fail}"

    # (11c) a guardrail breach (hallucination on an out-of-lexicon verb) must ALSO force HARD_FAIL even if
    # the disagreement-subset numbers look good -- zero-hallucination is a hard gate, not a soft one.
    tier_guard, _m, _w = compute_verdict(_synth(real_n=10, real_ic_acc=0.90, real_rec_acc=0.20, real_guard_wrong=0.4))
    assert tier_guard == "HARD_FAIL", f"CAN-FAIL probe: guardrail breach should force HARD_FAIL, got {tier_guard}"

    print(f"[self_test] PASS | {msg}", flush=True)
    print("[self_test] CAN-FAIL discriminator probes: HARD_PASS reachable=True, HARD_FAIL reachable=True "
          "(recency-wins-on-real-data case), guardrail-breach-forces-HARD_FAIL=True", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
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
    out_dir = _out_dir(run_mode)
    expected_n_units = len(EO_VERBS) + len(ES_VERBS) + len(NEUTRAL_VERBS)  # constructed items; real is fixed n=5
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[coupling_revival_ic] run_mode={run_mode} n_EO={len(EO_VERBS)} n_ES={len(ES_VERBS)} "
          f"n_NEUTRAL={len(NEUTRAL_VERBS)} expected_n_units={expected_n_units}", flush=True)

    a = analyze_all()
    print(f"[coupling_revival_ic] REAL disagreement(EO) n={a['real_disagreement']['n']} "
          f"(floor={REAL_MIN_DISAGREEMENT_N}, sufficient={a['real_data_sufficient']})", flush=True)
    print(f"[coupling_revival_ic] REAL guardrail(NEUTRAL) n={a['real_guardrail']['n']} "
          f"wrong_guess_rate={a['real_guardrail']['ic_wrong_guess_rate']}", flush=True)
    print(f"[coupling_revival_ic] CONSTRUCTED disagreement(EO) n={a['constructed_disagreement']['n']} "
          f"recency_acc={a['constructed_disagreement']['recency_acc']:.3f} "
          f"ic_acc={a['constructed_disagreement']['ic_acc']:.3f} "
          f"construction_artifact={a['construction_artifact_detected']}", flush=True)
    print(f"[coupling_revival_ic] CONSTRUCTED agreement(ES) n={a['constructed_agreement']['n']} "
          f"recency_acc={a['constructed_agreement']['recency_acc']:.3f} "
          f"ic_acc={a['constructed_agreement']['ic_acc']:.3f}", flush=True)
    print(f"[coupling_revival_ic] CONSTRUCTED guardrail(NEUTRAL) n={a['constructed_guardrail']['n']} "
          f"wrong_guess_rate={a['constructed_guardrail']['ic_wrong_guess_rate']:.3f}", flush=True)

    tier, msg, weakest = compute_verdict(a)
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "run_mode": run_mode, "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "expected_n_units": expected_n_units,
        "weakest_interface": weakest, "arms_differ": a["arms_differ"],
        "construction_artifact_detected": a["construction_artifact_detected"],
        "real_data_sufficient": a["real_data_sufficient"], "real_min_disagreement_n": REAL_MIN_DISAGREEMENT_N,
        "n_constructed_total": a["n_constructed_total"], "n_real_total": a["n_real_total"],
        "metric_real_disagreement_n": a["real_disagreement"]["n"],
        "metric_real_disagreement_recency_acc": a["real_disagreement"]["recency_acc"],
        "metric_real_disagreement_ic_acc": a["real_disagreement"]["ic_acc"],
        "metric_real_guardrail_n": a["real_guardrail"]["n"],
        "metric_real_guardrail_wrong_guess_rate": a["real_guardrail"]["ic_wrong_guess_rate"],
        "metric_constructed_disagreement_n": a["constructed_disagreement"]["n"],
        "metric_constructed_disagreement_recency_acc": a["constructed_disagreement"]["recency_acc"],
        "metric_constructed_disagreement_ic_acc": a["constructed_disagreement"]["ic_acc"],
        "metric_constructed_agreement_n": a["constructed_agreement"]["n"],
        "metric_constructed_agreement_recency_acc": a["constructed_agreement"]["recency_acc"],
        "metric_constructed_agreement_ic_acc": a["constructed_agreement"]["ic_acc"],
        "metric_constructed_guardrail_n": a["constructed_guardrail"]["n"],
        "metric_constructed_guardrail_wrong_guess_rate": a["constructed_guardrail"]["ic_wrong_guess_rate"],
        "real_corpus_meta": a["real_meta"],
        "rec_seq_hash": a["rec_seq_hash"], "ic_seq_hash": a["ic_seq_hash"],
        "prereg": {
            "hard_pass": "real_data_sufficient(n_real_eo>=6) & real_ic_acc>=real_recency_acc+0.30 & "
                         "real_guardrail_wrong==0 & constructed_guardrail_wrong==0 & constructed_agreement_ic_acc>=0.90",
            "hard_fail": "(real_data_sufficient & real_ic_acc<=real_recency_acc) | real_guardrail_wrong>0 | "
                         "constructed_guardrail_wrong>0 | constructed_agreement_ic_acc<0.80",
            "middle": "otherwise (expected/measured: real_data_sufficient==False, clean guardrails)",
            "p_hard_pass": 0.05, "p_middle_band": 0.85, "p_hard_fail": 0.10,
            "real_corpus": "LitBank (CC BY 4.0), commit " + LITBANK_COMMIT + ", 100 books, mined via "
                           "tools/derive_litbank_ic_disagreement_v1.py -- see PROVENANCE.md for the full "
                           "structural rule + the disclosed real_eo_n=0 scarcity finding",
            "ic_lexicon_citations": ["Garvey & Caramazza 1974", "Brown & Fish 1983",
                                     "Rudolph & Foersterling 1997 (meta-analysis)",
                                     "Kehler, Kertz, Rohde & Elman 2008"],
            "compute_architecture": "sequential-CPU, fully symbolic, NO RNG/VSA/torch (mechanism-comparison "
                                    "over a fixed real+constructed item set)",
            "storage_strategy": "no_storage", "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true", "deterministic_seeding": "N/A_no_rng",
            "real_code_path_exercised": ["load_real_items", "build_constructed_items", "recency_predict",
                                         "ic_verb_predict", "analyze_all", "compute_verdict"],
            "crlb_n/a": "no quantitative noise floor; fully symbolic discrete cluster-id lookup/comparison",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[coupling_revival_ic] {tier} in {elapsed:.4f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[coupling_revival_ic] {msg}", flush=True)
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
