"""HARD-SYNTAX HELD-OUT chain-grade DISCRIMINATOR test (v1).

WHY: the prior held-out LitBank who-did-what gold (exp_multi_turn_loop_litbank_ood_fixed_gate_v1.
LITBANK_QS_SPEC, reused by exp_consolidated_reader_chaingrade_FULL_v1 STEP 2) is 0/13 hard-syntax --
every svo item is canonical SVO where nearest-noun order ALREADY gives the right answer, so the naive
positional baseline scores HIGH and the ARM-B discriminator is VACUOUS (structure cannot out-recover
order because order is already right). This cell fixes that: a NEW held-out slice mined from the SAME
held-out LitBank CONLL source (data/corpora/litbank_coref_conll/*.conll; distinct_from_mcguffey),
selected ONLY by SYNTAX PATTERN, BLIND to any reader output (fairness: items were NOT picked where the
reader happens to win), where nearest-noun agent/patient assignment is WRONG.

MINING (STEP A, blind to reader): scan all 25 held-out CONLL docs, POS-tag with the reader's own tagger
(ORC.pos_tag_sentence), flag PASSIVE-BY constructions ("X was V-ed by Y"): aux-be + past-participle +
by + NP. In a passive the PATIENT is the PRE-verbal subject (X) and the AGENT is the by-phrase object
(Y) -- the exact opposite of linear order, so nearest-noun-left=agent / nearest-noun-right=patient is
WRONG for BOTH roles. Object-relative / OSV candidates were also mined but were too noisy to gold
conservatively (mostly PP-gaps and subject-relatives), so this slice is passive-dominant -- the type
where the reader's passive-detection gives STRUCTURE a genuine shot at beating ORDER.

GOLD (STEP B, conservative + hand-verified): 24 who-did-what items over 13 passages across 11 distinct
novels. Each item = (verbatim source sentence [reconstructed from CONLL at runtime; provenance
asserted], verb, gold role-filler head, hard-syntax TYPE). Each passive yields up to two items: a
PASSIVE_AGENT_BY item (answer = by-object; naive would pick the pre-verbal noun) and a
PASSIVE_PATIENT_PREVERBAL item (answer = pre-verbal subject; naive would pick the post-verbal noun).
Answers are single head tokens the reader can emit (verified present). Anti-circular: NO component was
tuned on LitBank; this gold never saw the reader; authored for THIS cell after blind mining.

VALIDITY GATE (STEP C, built-in fairness self-check): the NAIVE positional baseline (agent=nearest-noun-
left, patient=nearest-noun-right) MUST score LOW on this gold. If naive scores high the items are NOT
actually hard-syntax and the slice is INVALID. MEASURED@this run: naive = 0/24 (design-time validation
in scratchpad reproduced here). VALIDITY_MAX_NAIVE_ACC = 0.20.

STEP D (the 4 chain-grade bars, reusing exp_consolidated_reader_chaingrade_FULL_v1 [CR] machinery
byte-identically -- same composed reader, same naive, same glass-box, same LitBank general-slot config):
  ARM A: composed reader who-did-what accuracy on the hard-syntax gold (n_correct / n_gold), + per-type.
  ARM B (DISCRIMINATOR, the whole point): reader must BEAT naive by a real margin -- recover hard-syntax
    items naive misses. Report reader-minus-naive + WHICH items the reader gets that naive doesn't.
  ARM C (glass-box): replay-hash-stable + tamper-breaks-hash + causal role-edit flips a tuple + bridge
    head-arc edit re-routes a candidate, on a hard-syntax LitBank sentence (CR.glass_box_on_texts).
  ARM D: N + hard-syntax-TYPE distribution + novel count + small-N caveat.

HONEST OUTCOMES (either valid + informative; do NOT force a pass):
  * reader BEATS naive on hard-syntax -> STRUCTURE GENERALIZES to held-out adult-literary passives =
    chain-grade candidate (hand to skunkworks VET).
  * reader does NOT beat naive -> the McGuffey-tuned components are OVERFIT / don't transfer = an honest
    negative; autopsy WHICH components fail on WHICH hard-syntax type (per-type reader accuracy + the
    passive-detection / role-clf breakdown) and NAME the gap.

PRE-REGISTERED BANDS (set BEFORE this run):
  VALIDITY: naive_acc <= 0.20 (else INVALID_SLICE -- items not actually hard-syntax; report + fix).
  HARD_PASS (structure generalizes to held-out hard syntax): VALIDITY holds AND
    (n_reader_correct - n_naive_correct) >= 3 (a REAL margin: >= 3 distinct hard-syntax items structure
    recovers that order misses) AND n_reader_correct > 0.
  MIDDLE (directional transfer): VALIDITY holds AND 1 <= (n_reader_correct - n_naive_correct) <= 2.
  HARD_FAIL (McGuffey-overfit / structure does NOT transfer to held-out hard syntax):
    n_reader_correct <= n_naive_correct (reader no better than order on hard syntax).
  CHAIN_GRADE_HARDSYNTAX_EARNED iff HARD_PASS AND ARM_C glass_box_ok AND ARM_D (N>=8, novels>=3).

BRAIN-CHECK: constraint-based lexicalist parsing -- the passive cue (aux-be + participle + by) licenses
  a NON-canonical thematic mapping that overrides linear order; the positional baseline is the linear-
  order null hypothesis a human overrides using morphosyntax. Out-of-domain the human reader ALSO
  degrades on adult-literary syntax; the question is whether STRUCTURE still beats ORDER there.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- imports CR's from-scratch arc-eager
  parser training (~50-65s once) + per-clause greedy decode + AveragedPerceptron role clf + dict lookups;
  NO matmul/GPU-batchable primitive; 13 passages x 4 bars, wall ~2-4min foreground. Storage: no_storage.
  Runtime invariant: glass-box (from-scratch parser + curated dicts + corpus-observed admissibility), NO
  LLM/network/autograd at inference. Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED, sorted(set),
  sha256-derived indices. LOCAL-ONLY, foreground-to-completion. NO push / NO remote-persist / NO
  queue_add / NO bank (chain-grade candidate -> skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground candidate cell):
  - arms_differ_verified at smoke (hash over reader vs naive kept-tuple sets)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - VALIDITY gate at smoke: naive_acc <= 0.20 on hard-syntax gold (the fairness self-check)
  - discriminator can-fail: reader CAN score ~naive (honest negative) -- not saturated by construction
  - glass-box witnesses at smoke on a hard-syntax LitBank sentence (replay/tamper/role-flip/bridge)
  - deterministic seeding (fixed int SEED inherited from CR; sorted(set))
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (banked component metrics) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/accuracy, no HD noise floor); N/A multi-seed
    (deterministic given fixed SEED; parser single-seed by design, inherited from CR)
  - progress_logging: print_flush_true (sys.stdout line-buffered at cell start)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

ANCHOR_NAME = "consolidated_reader_hardsyntax_heldout_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# The FULL consolidated reader = all machinery (composed reader, naive, glass-box, scoring, clf/parser
# fit helpers, LitBank CONLL reconstruction). Byte-identical IMPORT; ONLY the gold/passages differ.
from experiments import exp_consolidated_reader_chaingrade_FULL_v1 as CR         # noqa: E402
from experiments import exp_multi_turn_loop_litbank_ood_fixed_gate_v1 as LB      # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC           # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M          # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3         # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2    # noqa: E402

SEED = CR.SEED

# Pre-registered bands
VALIDITY_MAX_NAIVE_ACC = 0.20
HARD_PASS_MARGIN = 3        # n_reader_correct - n_naive_correct >= 3 => real margin
ARMD_MIN_N = 8
ARMD_MIN_NOVELS = 3

# =======================================================================================
# HARD-SYNTAX GOLD (STEP B). (pid, work_substr, sent_idx, verb, kind, answer, htype).
# Mined blind by syntax pattern (STEP A); hand-verified conservatively; source reconstructed verbatim
# from CONLL at runtime (provenance asserted in self_test). Naive=0/24 at design-time (STEP C validity).
# =======================================================================================
GOLD_SPEC = [
    ("met",      "110_tess",       4,   "met",       "agent",   "parson",     "passive_agent_by"),
    ("met",      "110_tess",       4,   "met",       "patient", "he",         "passive_patient_preverbal"),
    ("evinced",  "11231_bartleby", 62,  "evinced",   "patient", "ambition",   "passive_patient_preverbal"),
    ("evinced",  "11231_bartleby", 62,  "evinced",   "agent",   "impatience", "passive_agent_by"),
    ("supplied", "158_emma",       2,   "supplied",  "patient", "place",      "passive_patient_preverbal"),
    ("supplied", "158_emma",       2,   "supplied",  "agent",   "woman",      "passive_agent_by"),
    ("revealed", "174_the_pictur", 103, "revealed",  "agent",   "painter",    "passive_agent_by_cleft"),
    ("revealed", "174_the_pictur", 103, "revealed",  "patient", "he",         "passive_patient_preverbal"),
    ("washed",   "2489_moby",      10,  "washed",    "patient", "mole",       "passive_patient_preverbal"),
    ("washed",   "2489_moby",      10,  "washed",    "agent",   "waves",      "passive_agent_by"),
    ("freed",    "2814_dubliners", 76,  "freed",     "agent",   "death",      "passive_agent_by_distractor"),
    ("freed",    "2814_dubliners", 76,  "freed",     "patient", "i",          "passive_patient_preverbal"),
    ("confined", "521_the_life",   7,   "confined",  "agent",   "gout",       "passive_agent_by"),
    ("confined", "521_the_life",   7,   "confined",  "patient", "he",         "passive_patient_preverbal"),
    ("overtaken","521_the_life",   26,  "overtaken", "agent",   "judgment",   "passive_agent_by"),
    ("overtaken","521_the_life",   26,  "overtaken", "patient", "i",          "passive_patient_preverbal"),
    ("injured",  "5348_ragged",    114, "injured",   "patient", "men",        "passive_patient_preverbal"),
    ("opposed",  "73_the_red",     31,  "opposed",   "agent",   "men",        "passive_agent_by"),
    ("opposed",  "73_the_red",     31,  "opposed",   "patient", "he",         "passive_patient_preverbal"),
    ("assailed", "73_the_red",     34,  "assailed",  "agent",   "questions",  "passive_agent_by"),
    ("assailed", "73_the_red",     34,  "assailed",  "patient", "he",         "passive_patient_preverbal"),
    ("made",     "76_adventures",  2,   "made",      "patient", "book",       "passive_patient_preverbal"),
    ("overset",  "829_gullivers",  28,  "overset",   "patient", "boat",       "passive_patient_preverbal"),
    ("overset",  "829_gullivers",  28,  "overset",   "agent",   "flurry",     "passive_agent_by"),
]


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def build_hardsyntax_gold():
    """Reconstruct verbatim passages from CONLL + assemble the gold list (CR._score_litbank schema)."""
    passages = {}
    for pid, work, si, *_ in GOLD_SPEC:
        if pid in passages:
            continue
        sents = LB._doc_sentences(work)
        passages[pid] = LB._detok(sents[si])
    gold = [dict(qid=f"{pid}_{kind}", pid=pid, kind=kind, verb=verb, other=None, answer=ans, htype=ht)
            for (pid, work, si, verb, kind, ans, ht) in GOLD_SPEC]
    n_novels = len(set(s[1] for s in GOLD_SPEC))
    return passages, gold, n_novels


def _fit_pipeline(run_mode):
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)
    W, parser_info = M.train_dep_parser(run_mode)
    return clf, sel_fn, W, parser_info


def run_bars(clf, sel_fn, W):
    passages, gold, n_novels = build_hardsyntax_gold()
    order = sorted(passages.keys())
    n_gold = len(gold)

    # ARM A: composed reader (held-out general-slot config, byte-identical to CR.litbank_flags)
    arm, gate, supp = CR.build_composed_arm(order, passages, W, clf, sel_fn, CR.DITRANS_FN,
                                            CR.litbank_flags())
    n_reader, per_reader = CR._score_litbank(arm, gold)

    # ARM B: naive positional discriminator on the SAME passages (byte-identical to CR)
    naive = CR.naive_positional_on_text(order, passages)
    n_naive, per_naive = CR._score_litbank(naive, gold)

    # per-type accuracy (reader + naive)
    htype_of = {f"{pid}_{kind}": ht for (pid, work, si, verb, kind, ans, ht) in GOLD_SPEC}
    per_type = defaultdict(lambda: dict(n=0, reader=0, naive=0))
    r_hit = {x["qid"]: x["correct"] for x in per_reader}
    n_hit = {x["qid"]: x["correct"] for x in per_naive}
    for g in gold:
        ht = htype_of[g["qid"]]
        per_type[ht]["n"] += 1
        per_type[ht]["reader"] += int(r_hit.get(g["qid"], False))
        per_type[ht]["naive"] += int(n_hit.get(g["qid"], False))

    # which items reader gets that naive doesn't (transfer evidence)
    reader_correct = set(x["qid"] for x in per_reader if x["correct"])
    naive_correct = set(x["qid"] for x in per_naive if x["correct"])
    recovered_vs_naive = sorted(reader_correct - naive_correct)
    lost_vs_naive = sorted(naive_correct - reader_correct)

    # per-item reader-vs-naive detail
    per_item = []
    for g in gold:
        per_item.append(dict(qid=g["qid"], pid=g["pid"], kind=g["kind"], verb=g["verb"],
                             answer=g["answer"], htype=htype_of[g["qid"]],
                             reader=bool(r_hit.get(g["qid"], False)),
                             naive=bool(n_hit.get(g["qid"], False)),
                             reader_emitted=next((x["matched"] for x in per_reader
                                                  if x["qid"] == g["qid"]), None)))

    # ARM C: glass-box on a hard-syntax LitBank sentence
    gb = CR.glass_box_on_texts(order, passages, W, clf, gate, sel_fn)

    naive_acc = round(n_naive / n_gold, 4) if n_gold else 0.0
    reader_acc = round(n_reader / n_gold, 4) if n_gold else 0.0
    margin = n_reader - n_naive

    validity_ok = (naive_acc <= VALIDITY_MAX_NAIVE_ACC)
    arm_d_ok = (n_gold >= ARMD_MIN_N and n_novels >= ARMD_MIN_NOVELS)

    return dict(
        n_gold=n_gold, n_novels=n_novels, n_passages=len(order),
        naive_acc=naive_acc, reader_acc=reader_acc,
        n_reader_correct=n_reader, n_naive_correct=n_naive, discriminator_margin=margin,
        validity_ok=validity_ok, validity_max_naive_acc=VALIDITY_MAX_NAIVE_ACC,
        recovered_by_reader_not_naive=recovered_vs_naive,
        lost_by_reader_vs_naive=lost_vs_naive,
        per_type={k: dict(v) for k, v in per_type.items()},
        per_item=per_item,
        arm_hash_reader=M.arm_hash(arm), arm_hash_naive=M.arm_hash(naive), supp=dict(supp),
        arm_c_glass_box=gb, arm_d_ok=arm_d_ok,
    )


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# =======================================================================================
# Self-test (design-gate: provenance + validity + arms-differ + glass-box fire).
# =======================================================================================
def self_test():
    print("[self-test] reconstruct hard-syntax gold + provenance ...", flush=True)
    passages, gold, n_novels = build_hardsyntax_gold()
    assert len(gold) >= ARMD_MIN_N, f"gold too small: {len(gold)}"
    assert n_novels >= ARMD_MIN_NOVELS, f"too few novels: {n_novels}"

    # provenance: every passage is a verbatim contiguous CONLL sentence (token-subsequence check)
    for pid, work, si, *_ in GOLD_SPEC:
        sents = LB._doc_sentences(work)
        expect = LB._detok(sents[si])
        assert passages[pid] == expect, f"provenance drift for {pid}"
    print(f"[self-test] provenance OK: N={len(gold)} items, {len(passages)} passages, {n_novels} novels",
          flush=True)

    # answer tokens are emittable (present + not empty)
    for pid, work, si, verb, kind, ans, ht in GOLD_SPEC:
        lows = []
        for clause in ORC.split_sentences(passages[pid]):
            lows.extend(t[1] for t in ORC.pos_tag_sentence(clause))
        assert CR._norm(ans) in [CR._norm(x) for x in lows], f"answer {ans!r} not a token in {pid}"

    clf, sel_fn, W, parser_info = _fit_pipeline("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"

    order = sorted(passages.keys())
    # VALIDITY: naive must fail on the hard-syntax gold
    naive = CR.naive_positional_on_text(order, passages)
    n_naive, _ = CR._score_litbank(naive, gold)
    naive_acc = n_naive / len(gold)
    print(f"[self-test] VALIDITY naive={n_naive}/{len(gold)} acc={naive_acc:.3f} "
          f"(<= {VALIDITY_MAX_NAIVE_ACC})", flush=True)
    assert naive_acc <= VALIDITY_MAX_NAIVE_ACC, \
        f"INVALID_SLICE: naive_acc {naive_acc} > {VALIDITY_MAX_NAIVE_ACC} -- items not hard-syntax"

    # reader runs + arms differ
    arm, gate, _s = CR.build_composed_arm(order, passages, W, clf, sel_fn, CR.DITRANS_FN,
                                          CR.litbank_flags())
    n_reader, _ = CR._score_litbank(arm, gold)
    hr, hn = M.arm_hash(arm), M.arm_hash(naive)
    assert hr != hn, f"META_RULE_AF: reader/naive arm hashes collide {hr}"
    print(f"[self-test] reader={n_reader}/{len(gold)} arms_differ reader={hr} naive={hn}", flush=True)

    # determinism (two reader runs identical)
    arm2, _g2, _s2 = CR.build_composed_arm(order, passages, W, clf, sel_fn, CR.DITRANS_FN,
                                           CR.litbank_flags())
    assert M.arm_hash(arm) == M.arm_hash(arm2), "non-deterministic reader"

    # glass-box fires on a hard-syntax sentence
    gb = CR.glass_box_on_texts(order, passages, W, clf, gate, sel_fn)
    print(f"[self-test] ARM C replay={gb['replay_hash_stable']} tamper={gb['tamper_detected']} "
          f"role_flip={gb['causal_role_edit_flipped']} bridge={gb['bridge_head_edit_reroutes']}",
          flush=True)
    assert gb["replay_hash_stable"], "GLASS-BOX: replay hash not stable"
    assert gb["tamper_detected"], "GLASS-BOX: tamper did not break hash"
    assert gb["causal_role_edit_flipped"], "GLASS-BOX: causal role-edit did not flip"
    assert gb["bridge_head_edit_reroutes"], "GLASS-BOX: bridge head-edit did not re-route"

    print("[self-test] PASS", flush=True)
    return 0


# =======================================================================================
# Full run (foreground to completion).
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=len(set(s[0] for s in GOLD_SPEC)))
    print(f"[full] mode={run_mode} hard-syntax held-out discriminator", flush=True)

    clf, sel_fn, W, parser_info = _fit_pipeline(run_mode)
    print(f"[full] parser trained uas={parser_info['uas_dev']}", flush=True)

    r = run_bars(clf, sel_fn, W)
    gb = r["arm_c_glass_box"]
    print(f"[full] ARM_A reader={r['n_reader_correct']}/{r['n_gold']} acc={r['reader_acc']} | "
          f"ARM_B naive={r['n_naive_correct']} margin={r['discriminator_margin']} "
          f"validity_ok={r['validity_ok']} | ARM_C glass_box={gb['glass_box_ok']} | "
          f"ARM_D ok={r['arm_d_ok']}", flush=True)
    print(f"[full] per_type={json.dumps(r['per_type'])}", flush=True)
    print(f"[full] recovered_by_reader_not_naive={r['recovered_by_reader_not_naive']}", flush=True)

    # ---- verdict per pre-registered bands ----
    validity_ok = r["validity_ok"]
    margin = r["discriminator_margin"]
    reader_beats = (r["n_reader_correct"] > r["n_naive_correct"])
    hard_pass = validity_ok and margin >= HARD_PASS_MARGIN and r["n_reader_correct"] > 0
    middle = validity_ok and 1 <= margin <= (HARD_PASS_MARGIN - 1)
    chain_grade = bool(hard_pass and gb["glass_box_ok"] and r["arm_d_ok"])

    if not validity_ok:
        verdict = "INVALID_SLICE_NAIVE_NOT_LOW"
        vmsg = (f"VALIDITY FAIL: naive scores {r['n_naive_correct']}/{r['n_gold']} "
                f"(acc={r['naive_acc']} > {VALIDITY_MAX_NAIVE_ACC}) -- the mined items are NOT actually "
                f"hard-syntax (nearest-noun order already right). Slice invalid; re-mine harder items.")
    elif chain_grade:
        verdict = "CHAIN_GRADE_HARDSYNTAX_EARNED"
        vmsg = (f"STRUCTURE GENERALIZES on HELD-OUT HARD SYNTAX: reader recovers "
                f"{r['n_reader_correct']}/{r['n_gold']} who-did-what items (acc={r['reader_acc']}) vs "
                f"naive {r['n_naive_correct']}/{r['n_gold']} (acc={r['naive_acc']}); discriminator margin "
                f"+{margin} (reader recovers {r['recovered_by_reader_not_naive']} that ORDER misses). "
                f"Validity: naive at/near floor on hard syntax. Glass-box OK on a hard-syntax LitBank "
                f"sentence (replay/tamper/role-flip/bridge). N={r['n_gold']} across {r['n_novels']} novels "
                f"(small-N held-out probe). per_type={json.dumps(r['per_type'])}. CHAIN-GRADE CANDIDATE -- "
                f"HYPOTHESIS pending skunkworks landed-VET; NOT banked.")
    elif hard_pass:
        verdict = "HARDSYNTAX_DISCRIMINATOR_PASS_GLASSBOX_OR_D_SHORT"
        vmsg = (f"Reader beats naive by real margin +{margin} ({r['n_reader_correct']} vs "
                f"{r['n_naive_correct']}) BUT glass_box_ok={gb['glass_box_ok']} / arm_d_ok={r['arm_d_ok']}. "
                f"Discriminator holds; a chain-grade bar short. per_type={json.dumps(r['per_type'])}.")
    elif middle:
        verdict = "HARDSYNTAX_PARTIAL_TRANSFER"
        vmsg = (f"DIRECTIONAL transfer: reader {r['n_reader_correct']} vs naive {r['n_naive_correct']} "
                f"(margin +{margin}, below real-margin {HARD_PASS_MARGIN}). Structure helps on held-out "
                f"hard syntax but weakly. recovered={r['recovered_by_reader_not_naive']}. "
                f"per_type={json.dumps(r['per_type'])}. Autopsy which type transfers.")
    else:
        verdict = "HARDSYNTAX_OVERFIT_NO_TRANSFER"
        vmsg = (f"HONEST NEGATIVE: reader {r['n_reader_correct']}/{r['n_gold']} does NOT beat naive "
                f"{r['n_naive_correct']}/{r['n_gold']} on held-out hard syntax (margin +{margin}). The "
                f"McGuffey-tuned components do NOT transfer to adult-literary passives. "
                f"per_type={json.dumps(r['per_type'])} names WHICH hard-syntax type the reader fails; "
                f"reader-lost-vs-naive={r['lost_by_reader_vs_naive']}. Autopsy the passive-detection / "
                f"role-clf gap. reader_beats={reader_beats}.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: hard-syntax held-out reader={r['n_reader_correct']}/{r['n_gold']} "
                 f"(acc={r['reader_acc']}) vs naive={r['n_naive_correct']} (acc={r['naive_acc']}) "
                 f"margin=+{margin} validity_ok={validity_ok} glass_box={gb['glass_box_ok']} "
                 f"arm_d={r['arm_d_ok']} chain_grade={chain_grade} | N={r['n_gold']} "
                 f"novels={r['n_novels']} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        n_gold=r["n_gold"], n_novels=r["n_novels"], n_passages=r["n_passages"],
        naive_acc=r["naive_acc"], reader_acc=r["reader_acc"],
        n_reader_correct=r["n_reader_correct"], n_naive_correct=r["n_naive_correct"],
        discriminator_margin=margin, validity_ok=validity_ok,
        recovered_by_reader_not_naive=r["recovered_by_reader_not_naive"],
        lost_by_reader_vs_naive=r["lost_by_reader_vs_naive"],
        per_type=r["per_type"], per_item=r["per_item"],
        arm_c_glass_box=gb, arm_d_ok=r["arm_d_ok"],
        htype_distribution=dict(Counter(s[6] for s in GOLD_SPEC)),
        chain_grade_hardsyntax_earned=chain_grade,
        bars=dict(ARM_A_reader_acc=r["reader_acc"],
                  ARM_B_discriminator_margin=margin,
                  ARM_B_reader_beats_naive=reader_beats,
                  ARM_C_glass_box_ok=gb["glass_box_ok"],
                  ARM_D_non_ceiling_ok=r["arm_d_ok"]),
        bands=dict(VALIDITY_MAX_NAIVE_ACC=VALIDITY_MAX_NAIVE_ACC, HARD_PASS_MARGIN=HARD_PASS_MARGIN,
                   ARMD_MIN_N=ARMD_MIN_N, ARMD_MIN_NOVELS=ARMD_MIN_NOVELS),
        parser_info=parser_info,
        one_variable=("ARM A composed reader (held-out general slot-rule config, byte-identical import of "
                      "exp_consolidated_reader_chaingrade_FULL_v1) vs ARM B naive positional (structure vs "
                      "order) on a NEW hard-syntax held-out gold where nearest-noun order FAILS by "
                      "construction. ONE variable: reader-vs-naive on identical passages."),
        provenance_note=("Passages reconstructed verbatim from data/corpora/litbank_coref_conll/*.conll "
                         "at runtime (self-test asserts token-subsequence provenance). Gold hand-authored "
                         "for THIS cell after BLIND syntax-pattern mining; anti-circular (never saw the "
                         "reader; no component tuned on LitBank)."),
        scope_caveat=("Held-out hard-syntax who-did-what gold is SMALL (N=%d across %d novels): a held-out "
                      "GENERALIZATION probe, not a large-sample estimate. Passive-dominant (the reliably "
                      "mineable hard-syntax type); object-relative/OSV were too noisy to gold "
                      "conservatively. CHAIN-GRADE CANDIDATE, CLAIM-VET-pending; NOT banked."
                      % (r["n_gold"], r["n_novels"])),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"], flush=True)
    print("verdict:", verdict, flush=True)
    print("verdict_msg:", vmsg, flush=True)
    print("per_item:", json.dumps([{k: it[k] for k in ("qid", "htype", "answer", "reader", "naive")}
                                    for it in r["per_item"]]), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
