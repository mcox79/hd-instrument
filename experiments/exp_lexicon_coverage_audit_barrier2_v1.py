"""exp_lexicon_coverage_audit_barrier2_v1 -- MEASUREMENT (not a build): what fraction of real-prose verb
tokens/types fall inside existing free symbolic subcategorization/selectional resources (VerbNet primary;
PropBank + FrameNet cross-check), and at what granularity do argument-selectional needs resolve -- TYPE-level
(the verb's own subcat/sense/idiom lexicon entry suffices) vs INSTANCE-level (needs a specific world/discourse
fact about the particular referents)? This tests barrier-ranking Prediction 2: is LEXICON-RICHNESS genuinely
distinct from FOUNDATION/world-knowledge SIZE (research note `research_lexicon_richness_subcategorization_
barrier_real_prose_parsing_2026-07-17.md`, section (b) part 1)?

RE-RUN CONTEXT: a prior dispatch of this measurement (queue entry a949b405) STALLED on a 600s watchdog because
a duplicate CPU-runner process was saturating the filesystem; that duplicate has since been cleaned up. This
cell is a FRESH, independent re-authoring (not a resurrection of the stalled script) per Director's explicit
"fork-independent, no parser adoption" instruction -- it does NOT import from any `exp_read_grow_*` module in
the Rung 5-9 real-prose reading arc, so this measurement's correctness never depends on that arc's parser, and
vice versa. See preregs/2026-07-17_lexicon_coverage_audit_barrier2_v1.md for the full pre-reg (bands, method,
SCHEMA-VET declarations, honest limitations).

RESOURCES (glass-box, symbolic, NO-LLM): VerbNet (3621 lemmas), PropBank (3319 lemmas / 4659 rolesets),
FrameNet (3318 verb-lexical-unit lemmas), all via `nltk.corpus` readers reading a LOCAL, already-fetched
`nltk_data` cache (verbnet + framenet were already present; propbank was fetched ONE TIME this session via
`nltk.download('propbank')` -- a one-time environment-setup action, NOT a cell runtime action; the cell itself
makes NO network calls at self-test/smoke/full time, matching the existing `data/corpora/ud_english_ewt/`
convention). Real-prose slice: SAME corpus Rung 5-9 used (`data/corpora/ud_english_ewt/en_ewt-ud-test.conllu`,
CC BY-SA 4.0, already committed) -- reused as a corpus file, NOT via that arc's parser code.

METHOD (summary; full detail in the pre-reg): parse CoNLL-U (independent minimal reader, this cell's own);
extract every UPOS=='VERB' token using UD's own gold lemma column; look up VerbNet/PropBank/FrameNet lemma
membership; PRIMARY coverage metric = fraction of tokens/types with `vn or pb` (verbatim Research Prediction-2
wording); FrameNet reported as secondary cross-check. Deterministically sample N=120 covered tokens (fixed
seed=7, deterministic sorted-input ordering, no PYTHONHASHSEED-sensitive idioms -- PROT-023-safe) for a
HAND-AUDIT (NOT automated on the first pass, per the Director's explicit instruction): each sampled verb
token is judged `type_level` (the
verb's own subcat frame -- including a catalogued sense-variant or idiom/MWE entry -- suffices, no instance
fact needed) or `instance_level` (needs a specific world/discourse/pragmatic fact about the particular
referents that no general lexicon entry supplies). Judgments are recorded ONCE as a static, committed data
file (`data/exp_lexicon_coverage_audit_barrier2_v1/hand_judgments_v1.json`); every run CROSS-VALIDATES that a
live re-derivation of the sample produces the IDENTICAL (sent_id, tok_id) key set as the judgments file
(a staleness guard -- hard-halts as CELL_CRASHED on mismatch, never silently re-samples or silently drops).

SCOPING DECISION (stated explicitly, not hidden): the type-vs-instance judgment is about the VERB's OWN
argument-selectional/sense resolution, NOT pronoun/coreference resolution (which entity a pronoun refers to is
a separate, already-identified barrier -- discourse/working-memory tracking -- and is deliberately NOT counted
here, to avoid conflating two distinct barriers).

BANDS (pre-registered verbatim from Research's own Prediction 2, before this run):
  HARD-PASS: coverage_union_vn_pb_token_frac >= 0.90 AND type_level_frac_of_audited_sample >= 0.80.
  HARD-FAIL: coverage_union_vn_pb_token_frac < 0.60 OR type_level_frac_of_audited_sample < 0.50.
  MIDDLE_BAND: otherwise (including floor-hugging: either margin above its HARD-PASS floor < 5% of its own
  [floor, 1.0] band width demotes an otherwise-HARD_PASS result to MIDDLE_BAND, per META_RULE_L).

COMPUTE: sequential-CPU, pure CoNLL-U/dict processing + nltk lemma-set lookups over ~2600 verb tokens /
2077 sentences; no torch, no GPU primitive, no VSA store (`storage_strategy: no_storage`). Measured full wall
time is a few seconds; smoke uses the SAME full computation (no scale axis to reduce -- Option A precedent
from the Rung 5-9 audit cells). Local, `local_cpu_queue`, timeout=300s. Pause flag re-checked absent
immediately before dispatch.

HONEST LIMITATIONS (declared up front): single-rater hand-audit (no inter-rater reliability measured, flagged
CLAIM/VET-pending not certified); UD-EWT is informal/transactional web register (blogs/emails/Q&A/reviews/
newsgroups) and likely under-represents metaphor/instance-dependent language relative to literary/narrative
prose -- this measures THIS register's honest ceiling, not "real prose" universally; n=120 is defensible but
modest for a proportion this close to 1.0; ~25% of the type_level bucket rests on the judgment call that
idiom/MWE and multi-sense-but-frame-disambiguated readings are lexicon-resolvable rather than instance-level
-- reported with a full subclass breakdown so a reader can recompute under a stricter alternative reading.

PRIOR-WORK CHECK (substrate_query.sh, mandatory before authoring): top hit cosine=0.2832 (unrelated T3-deeper-
ingest hypernym-recall note), all 5 hits below the cosine>0.30 rediscovery threshold -- NOVEL, not a
rediscovery.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_exempted: [("n/a", "no_comparative_arms")] -- single-measurement audit, META_RULE_AF N/A.
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit / KeyboardInterrupt: raise BEFORE except Exception (no bare/BaseException).
# - crlb_n/a: no quantitative noise floor in the CRLB sense; informal binomial SE reported, not gated.
# - baseline_in_band: n/a_no_baseline_arm_single_measurement_audit (META_RULE_AG N/A by design).
# - discriminator survives scale: n/a, no scale axis (whole-corpus deterministic count).
# - HARD_PASS strictly above floor + META_RULE_L floor-hugging demotion (see compute_verdict()).
# - cardinality_ok: n/a_no_sweep_axis (one full-corpus measurement, not a K/N/V sweep).
# - calibration_check: n/a_bands_are_verbatim_prereg_thresholds_not_tuned.
# - all numbers in comments tagged HYPOTHESIZED@prereg / MEASURED@metrics / CITED@research-note.
# - real_code_path_exercised: [parse_conllu (real corpus file, self-test slice), nltk verbnet/propbank/
#   framenet real resource lookups, self-test]. substrate_signature_checked: n/a (no substrate object calls).
# - deterministic_seeding: true (fixed int seed 7, deterministic sorted-input ordering, no PYTHONHASHSEED-
#   sensitive idioms).
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import json
import time
import random
import argparse
import platform
import traceback
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "lexicon_coverage_audit_barrier2_v1"
CONLLU_PATH = REPO / "data" / "corpora" / "ud_english_ewt" / "en_ewt-ud-test.conllu"
HAND_JUDGMENTS_PATH = REPO / "data" / f"exp_{ANCHOR_NAME}" / "hand_judgments_v1.json"

SAMPLE_SEED = 7
SAMPLE_N = 120

HARD_PASS_COVERAGE = 0.90
HARD_PASS_TYPE_FRAC = 0.80
HARD_FAIL_COVERAGE = 0.60
HARD_FAIL_TYPE_FRAC = 0.50
FLOOR_HUG_FRACTION = 0.05  # META_RULE_L: margin above floor must be >= 5% of [floor, 1.0] band width


# ---------------------------------------------------------------------------
# glass-box-legal checks (same method as Rung 5-9; independent copy, no import).
# ---------------------------------------------------------------------------
def _grep_confirm_no_neural_imports():
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(src)]


def _runtime_neural_module_check():
    banned = ("torch", "spacy", "transformers", "stanza")
    return sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))


# ---------------------------------------------------------------------------
# independent, minimal CoNLL-U reader (fork-independent -- does NOT import from exp_read_grow_* modules).
# ---------------------------------------------------------------------------
def parse_conllu(path):
    sentences = []
    cur_meta, cur_tokens = {}, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# "):
                if "=" in line:
                    k, _, v = line[2:].partition("=")
                    cur_meta[k.strip()] = v.strip()
                continue
            if not line.strip():
                if cur_tokens:
                    sentences.append({"meta": cur_meta, "tokens": cur_tokens})
                cur_meta, cur_tokens = {}, []
                continue
            fields = line.split("\t")
            if len(fields) != 10:
                continue
            tid = fields[0]
            if "-" in tid or "." in tid:
                continue  # multiword-token range rows / empty nodes, not real tokens
            cur_tokens.append({
                "id": int(tid), "form": fields[1], "lemma": fields[2].lower(), "upos": fields[3],
                "head": int(fields[6]) if fields[6] not in ("_", "") else None,
                "deprel": fields[7],
            })
    if cur_tokens:
        sentences.append({"meta": cur_meta, "tokens": cur_tokens})
    return sentences


def children(tokens, head_id, deprel_prefix):
    return [t for t in tokens if t["head"] == head_id and t["deprel"].split(":")[0] == deprel_prefix]


# ---------------------------------------------------------------------------
# symbolic resource lookups (local nltk_data cache only; no network at run time).
# ---------------------------------------------------------------------------
def _lookup_error_hint(resource):
    return (
        f"nltk resource '{resource}' not found in the local nltk_data cache. This cell performs NO network "
        f"access at self-test/smoke/full time (per convention). One-time environment setup (already done for "
        f"this session's authoring): `python -c \"import nltk; nltk.download('{resource}')\"`. Re-run once "
        f"that completes."
    )


def load_lexicon_sets():
    from nltk.corpus import verbnet as vn, propbank as pb, framenet as fn
    try:
        vn_lemmas = set(vn.lemmas())
    except LookupError as e:
        raise RuntimeError(_lookup_error_hint("verbnet")) from e
    try:
        pb_lemmas = set(r.attrib["id"].rsplit(".", 1)[0] for r in pb.rolesets())
    except LookupError as e:
        raise RuntimeError(_lookup_error_hint("propbank")) from e
    try:
        fn_lemmas = set(lu.name.rsplit(".", 1)[0] for lu in fn.lus() if lu.name.endswith(".v"))
    except LookupError as e:
        raise RuntimeError(_lookup_error_hint("framenet_v17")) from e
    return vn_lemmas, pb_lemmas, fn_lemmas


def extract_verb_tokens(sentences, vn_lemmas, pb_lemmas, fn_lemmas):
    out = []
    for s in sentences:
        sid = s["meta"].get("sent_id", "")
        text = s["meta"].get("text", "")
        for t in s["tokens"]:
            if t["upos"] != "VERB":
                continue
            lemma = t["lemma"]
            subj = children(s["tokens"], t["id"], "nsubj")
            obj = children(s["tokens"], t["id"], "obj") + children(s["tokens"], t["id"], "dobj")
            obl = children(s["tokens"], t["id"], "obl")
            out.append({
                "sent_id": sid, "text": text, "tok_id": t["id"], "form": t["form"], "lemma": lemma,
                "subj": [c["form"] for c in subj], "obj": [c["form"] for c in obj],
                "obl": [c["form"] for c in obl],
                "vn": lemma in vn_lemmas, "pb": lemma in pb_lemmas, "fn": lemma in fn_lemmas,
            })
    return out


def compute_coverage_stats(verb_tokens):
    n_tok = len(verb_tokens)
    if n_tok == 0:
        raise RuntimeError("zero verb tokens extracted from corpus -- vacuous measurement, halting")
    types = sorted(set(v["lemma"] for v in verb_tokens))  # deterministic sorted order -- PROT-023-safe
    n_types = len(types)

    def frac_tok(pred):
        c = sum(1 for v in verb_tokens if pred(v))
        return c, c / n_tok

    def frac_typ(pred_lemma):
        c = sum(1 for lm in types if pred_lemma(lm))
        return c, c / n_types

    vn_by_lemma = {v["lemma"]: v["vn"] for v in verb_tokens}
    pb_by_lemma = {v["lemma"]: v["pb"] for v in verb_tokens}
    fn_by_lemma = {v["lemma"]: v["fn"] for v in verb_tokens}

    vn_tok_c, vn_tok_f = frac_tok(lambda v: v["vn"])
    pb_tok_c, pb_tok_f = frac_tok(lambda v: v["pb"])
    fn_tok_c, fn_tok_f = frac_tok(lambda v: v["fn"])
    union_tok_c, union_tok_f = frac_tok(lambda v: v["vn"] or v["pb"])
    union_all_tok_c, union_all_tok_f = frac_tok(lambda v: v["vn"] or v["pb"] or v["fn"])

    vn_typ_c, vn_typ_f = frac_typ(lambda lm: vn_by_lemma[lm])
    pb_typ_c, pb_typ_f = frac_typ(lambda lm: pb_by_lemma[lm])
    fn_typ_c, fn_typ_f = frac_typ(lambda lm: fn_by_lemma[lm])
    union_typ_c, union_typ_f = frac_typ(lambda lm: vn_by_lemma[lm] or pb_by_lemma[lm])
    union_all_typ_c, union_all_typ_f = frac_typ(lambda lm: vn_by_lemma[lm] or pb_by_lemma[lm] or fn_by_lemma[lm])

    uncovered_types = sorted(lm for lm in types if not (vn_by_lemma[lm] or pb_by_lemma[lm]))

    return {
        "n_verb_tokens": n_tok, "n_verb_types": n_types,
        "token": {
            "verbnet": {"count": vn_tok_c, "frac": vn_tok_f},
            "propbank": {"count": pb_tok_c, "frac": pb_tok_f},
            "framenet": {"count": fn_tok_c, "frac": fn_tok_f},
            "union_vn_pb_PRIMARY": {"count": union_tok_c, "frac": union_tok_f},
            "union_vn_pb_fn": {"count": union_all_tok_c, "frac": union_all_tok_f},
        },
        "type": {
            "verbnet": {"count": vn_typ_c, "frac": vn_typ_f},
            "propbank": {"count": pb_typ_c, "frac": pb_typ_f},
            "framenet": {"count": fn_typ_c, "frac": fn_typ_f},
            "union_vn_pb_PRIMARY": {"count": union_typ_c, "frac": union_typ_f},
            "union_vn_pb_fn": {"count": union_all_typ_c, "frac": union_all_typ_f},
        },
        "uncovered_types_union_vn_pb": uncovered_types,
        "n_uncovered_types_union_vn_pb": len(uncovered_types),
    }


def deterministic_sample(verb_tokens, seed, n):
    """PROT-023-safe: fixed int seed, deterministic sorted-input ordering, no PYTHONHASHSEED-sensitive idioms."""
    covered = [v for v in verb_tokens if v["vn"] or v["pb"]]
    covered_sorted = sorted(covered, key=lambda v: (v["sent_id"], v["tok_id"]))
    rng = random.Random(seed)
    n_draw = min(n, len(covered_sorted))
    drawn = rng.sample(covered_sorted, n_draw)
    return sorted(drawn, key=lambda v: (v["sent_id"], v["tok_id"]))


def load_hand_judgments(path):
    if not path.exists():
        raise RuntimeError(
            f"hand_judgments file not found at {path}. This cell's FULL/smoke run requires the committed "
            f"static hand-audit data file (see pre-reg 'HAND-AUDIT' method). Self-test does not require it."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data:
        assert row["judgment"] in ("type_level", "instance_level"), row
    return data


def integrity_check(sample, judgments):
    sample_keys = set((v["sent_id"], v["tok_id"]) for v in sample)
    judg_keys = set((j["sent_id"], j["tok_id"]) for j in judgments)
    ok = sample_keys == judg_keys
    detail = {
        "n_sample": len(sample_keys), "n_judgments": len(judg_keys),
        "in_sample_not_judgments": sorted(str(k) for k in (sample_keys - judg_keys))[:20],
        "in_judgments_not_sample": sorted(str(k) for k in (judg_keys - sample_keys))[:20],
    }
    return ok, detail


def compute_type_instance_split(judgments):
    n = len(judgments)
    n_type = sum(1 for j in judgments if j["judgment"] == "type_level")
    n_inst = n - n_type
    subclass_counts = dict(Counter(j["subclass"] for j in judgments if j["judgment"] == "type_level"))
    frac_type = n_type / n if n else 0.0
    # informal binomial SE (Wald), reported not gated -- see pre-reg honest-limitations section.
    se = (frac_type * (1 - frac_type) / n) ** 0.5 if n else 0.0
    return {
        "n_audited": n, "n_type_level": n_type, "n_instance_level": n_inst,
        "type_level_frac": frac_type, "type_level_wald_se_approx": se,
        "type_level_subclass_counts": subclass_counts,
        "instance_level_examples": [
            {"sent_id": j["sent_id"], "lemma": j["lemma"], "subclass": j["subclass"], "rationale": j["rationale"]}
            for j in judgments if j["judgment"] == "instance_level"
        ],
    }


def compute_verdict(coverage_stats, split_stats):
    cov = coverage_stats["token"]["union_vn_pb_PRIMARY"]["frac"]
    typ = split_stats["type_level_frac"]

    hard_pass = (cov >= HARD_PASS_COVERAGE) and (typ >= HARD_PASS_TYPE_FRAC)
    hard_fail = (cov < HARD_FAIL_COVERAGE) or (typ < HARD_FAIL_TYPE_FRAC)

    # META_RULE_L floor-hugging demotion: margin above HARD_PASS floor must be >= 5% of [floor, 1.0] width.
    cov_margin = cov - HARD_PASS_COVERAGE
    typ_margin = typ - HARD_PASS_TYPE_FRAC
    cov_band_width = 1.0 - HARD_PASS_COVERAGE
    typ_band_width = 1.0 - HARD_PASS_TYPE_FRAC
    cov_floor_hug = hard_pass and (cov_margin < FLOOR_HUG_FRACTION * cov_band_width)
    typ_floor_hug = hard_pass and (typ_margin < FLOOR_HUG_FRACTION * typ_band_width)

    if hard_fail:
        tier = "HARD_FAIL"
    elif hard_pass and not (cov_floor_hug or typ_floor_hug):
        tier = "HARD_PASS"
    elif hard_pass and (cov_floor_hug or typ_floor_hug):
        tier = "MIDDLE_BAND"  # floor-hugging demotion, META_RULE_L
    else:
        tier = "MIDDLE_BAND"

    prediction2_supported = (tier == "HARD_PASS")

    msg = (
        f"{tier} | coverage_union_vn_pb_token={cov:.4f} (>=0.90 HP-floor, margin={cov_margin:+.4f}) | "
        f"type_level_frac(n={split_stats['n_audited']})={typ:.4f} (>=0.80 HP-floor, margin={typ_margin:+.4f}) | "
        f"instance_level_n={split_stats['n_instance_level']} | "
        f"type_subclass={split_stats['type_level_subclass_counts']} | "
        f"PREDICTION_2_lexicon_distinct_from_foundation_size={'SUPPORTED' if prediction2_supported else 'NOT_SUPPORTED_AT_HARD_PASS_BAR'}"
    )
    return tier, msg, prediction2_supported, {
        "coverage_margin_above_hp_floor": cov_margin, "type_frac_margin_above_hp_floor": typ_margin,
        "coverage_floor_hugging": cov_floor_hug, "type_frac_floor_hugging": typ_floor_hug,
    }


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
# self-test: EXERCISE THE REAL code path (real corpus file slice, real nltk resource lookups), plus synthetic
# unit checks for the integrity-guard and split-computation logic.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] static + runtime glass-box-legal checks...", flush=True)
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    vn_lemmas, pb_lemmas, fn_lemmas = load_lexicon_sets()
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) resource sanity: known-covered and known-uncovered lemmas behave as expected.
    assert "eat" in vn_lemmas and "eat" in pb_lemmas and "eat" in fn_lemmas, "known-covered lemma 'eat' missing"
    assert "run" in vn_lemmas and "run" in pb_lemmas, "known-covered lemma 'run' missing"
    contrived = "zzznotarealenglishverbxyz123"
    assert contrived not in vn_lemmas and contrived not in pb_lemmas and contrived not in fn_lemmas, (
        "contrived nonsense lemma unexpectedly found in a resource -- lookup logic is broken")
    print(f"[self_test] resource sanity: vn={len(vn_lemmas)} pb={len(pb_lemmas)} fn={len(fn_lemmas)} lemmas; "
          f"'eat'/'run' covered, contrived nonsense lemma correctly uncovered.", flush=True)

    # (2) real_code_path (Gate F.1): parse a REAL slice of the actual corpus file, extract real verb tokens,
    # using the REAL nltk resource lookups -- not a synthetic-only branch.
    assert CONLLU_PATH.exists(), f"corpus not found at {CONLLU_PATH} (see PROVENANCE.md)"
    real_sentences_full = parse_conllu(CONLLU_PATH)
    assert len(real_sentences_full) > 500, f"expected a sizeable real corpus, got {len(real_sentences_full)} sentences"
    tiny_slice = real_sentences_full[:50]
    tiny_tokens = extract_verb_tokens(tiny_slice, vn_lemmas, pb_lemmas, fn_lemmas)
    assert len(tiny_tokens) > 0, "discriminator-fires check failed: a real 50-sentence slice produced ZERO verb tokens"
    tiny_stats = compute_coverage_stats(tiny_tokens)
    assert 0.0 <= tiny_stats["token"]["union_vn_pb_PRIMARY"]["frac"] <= 1.0
    print(f"[self_test] real_code_path: parsed {len(real_sentences_full)} real sentences; a 50-sentence real "
          f"slice yielded {len(tiny_tokens)} verb tokens, coverage(vn|pb)="
          f"{tiny_stats['token']['union_vn_pb_PRIMARY']['frac']:.3f} (real nltk lookups, real corpus file).",
          flush=True)

    # (3) deterministic_sample: same seed -> byte-identical sample twice; different seed -> (almost certainly)
    # a different sample. PROT-023-safe (fixed int seed, sorted() input, no hash()/list(set())).
    all_tokens_tiny = extract_verb_tokens(real_sentences_full[:200], vn_lemmas, pb_lemmas, fn_lemmas)
    s1 = deterministic_sample(all_tokens_tiny, 7, 20)
    s2 = deterministic_sample(all_tokens_tiny, 7, 20)
    assert [(v["sent_id"], v["tok_id"]) for v in s1] == [(v["sent_id"], v["tok_id"]) for v in s2], (
        "deterministic_sample is NOT reproducible across calls with the same seed -- nondeterminism bug")
    s3 = deterministic_sample(all_tokens_tiny, 99, 20)
    assert [(v["sent_id"], v["tok_id"]) for v in s1] != [(v["sent_id"], v["tok_id"]) for v in s3], (
        "deterministic_sample produced the SAME sample for two different seeds -- suspiciously coincidental "
        "or the seed argument is not actually wired in")
    print(f"[self_test] deterministic_sample reproducible across calls (same seed) and seed-sensitive "
          f"(different seed differs); {len(s1)}/{len(all_tokens_tiny)} drawn from a 200-sentence slice.",
          flush=True)

    # (4) integrity_check (staleness guard): matching keys -> ok=True; a deliberately mutated judgments list
    # (one tok_id shifted) -> ok=False, caught (not silently accepted).
    fake_sample = [{"sent_id": "a", "tok_id": 1, "lemma": "eat"}, {"sent_id": "b", "tok_id": 2, "lemma": "run"}]
    fake_judg_match = [{"sent_id": "a", "tok_id": 1, "judgment": "type_level"},
                        {"sent_id": "b", "tok_id": 2, "judgment": "type_level"}]
    ok, detail = integrity_check(fake_sample, fake_judg_match)
    assert ok, f"integrity_check false-negative on matching keys: {detail}"
    fake_judg_stale = [{"sent_id": "a", "tok_id": 1, "judgment": "type_level"},
                        {"sent_id": "b", "tok_id": 999, "judgment": "type_level"}]  # tok_id drifted
    ok2, detail2 = integrity_check(fake_sample, fake_judg_stale)
    assert not ok2, f"integrity_check FAILED TO CATCH a deliberately staled judgments key set: {detail2}"
    print(f"[self_test] integrity_check (STALE_JUDGMENTS guard): correctly passes on matching keys AND "
          f"correctly catches a deliberately mismatched key set (detail={detail2}).", flush=True)

    # (5) compute_type_instance_split: hand-built tiny judgment list with a known split.
    tiny_judg = (
        [{"sent_id": "x", "tok_id": i, "lemma": "eat", "judgment": "type_level",
          "subclass": "trivial_compositional", "rationale": "r"} for i in range(8)]
        + [{"sent_id": "x", "tok_id": i, "lemma": "forgive", "judgment": "instance_level",
            "subclass": "metonymic_pragmatic", "rationale": "r"} for i in range(8, 10)]
    )
    split = compute_type_instance_split(tiny_judg)
    assert split["n_audited"] == 10 and split["n_type_level"] == 8 and split["n_instance_level"] == 2
    assert abs(split["type_level_frac"] - 0.8) < 1e-9
    print(f"[self_test] compute_type_instance_split on a hand-built 10-item list: "
          f"type_level_frac={split['type_level_frac']:.3f} (expected 0.800). PASS.", flush=True)

    # (6) compute_verdict band logic: hand-built coverage_stats/split_stats at 3 points (clear PASS, clear
    # FAIL, and a floor-hugging PASS-candidate that must demote to MIDDLE_BAND per META_RULE_L).
    def _cov(frac):
        return {"token": {"union_vn_pb_PRIMARY": {"frac": frac}}}

    def _split(frac, n=100):
        return {"type_level_frac": frac, "n_audited": n, "n_instance_level": int(round(n * (1 - frac))),
                "type_level_subclass_counts": {}}

    tier_pass, _, pred2_pass, _ = compute_verdict(_cov(0.99), _split(0.98))
    assert tier_pass == "HARD_PASS" and pred2_pass is True
    tier_fail, _, pred2_fail, _ = compute_verdict(_cov(0.40), _split(0.30))
    assert tier_fail == "HARD_FAIL" and pred2_fail is False
    # floor-hugging: coverage exactly at 0.905 (margin 0.005 vs required 0.05*(1-0.90)=0.005 -- right at the
    # cusp; use 0.901 margin=0.001 < 0.005 to unambiguously trigger the demotion).
    tier_hug, _, pred2_hug, hug_detail = compute_verdict(_cov(0.901), _split(0.85))
    assert tier_hug == "MIDDLE_BAND" and hug_detail["coverage_floor_hugging"] is True, hug_detail
    print(f"[self_test] compute_verdict band logic: clear-PASS -> HARD_PASS, clear-FAIL -> HARD_FAIL, "
          f"floor-hugging(cov=0.901) -> MIDDLE_BAND (META_RULE_L demotion). PASS.", flush=True)

    return True


# ---------------------------------------------------------------------------
# full pipeline (identical for smoke and full -- no scale axis to reduce; whole-corpus deterministic count,
# measured wall time is a few seconds).
# ---------------------------------------------------------------------------
def run_full():
    vn_lemmas, pb_lemmas, fn_lemmas = load_lexicon_sets()
    sentences = parse_conllu(CONLLU_PATH)
    verb_tokens = extract_verb_tokens(sentences, vn_lemmas, pb_lemmas, fn_lemmas)
    coverage_stats = compute_coverage_stats(verb_tokens)

    sample = deterministic_sample(verb_tokens, SAMPLE_SEED, SAMPLE_N)
    judgments = load_hand_judgments(HAND_JUDGMENTS_PATH)
    ok, detail = integrity_check(sample, judgments)
    if not ok:
        raise RuntimeError(
            f"STALE_JUDGMENTS: live re-derived sample does not match the committed hand_judgments_v1.json "
            f"key set. This means the corpus, resource versions, or sampling logic drifted since the hand "
            f"audit was recorded -- the audit must be re-done against the current sample, NOT silently "
            f"reused. detail={detail}"
        )
    split_stats = compute_type_instance_split(judgments)
    return {
        "n_sentences": len(sentences), "coverage_stats": coverage_stats,
        "sample_size": len(sample), "integrity_ok": ok, "split_stats": split_stats,
    }


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
        print("[lexicon_coverage_audit_barrier2] self-test PASS", flush=True)
        out_dir = _out_dir("self_test")
        _write_start_marker(out_dir, "self_test", 1)
        _write_metrics(out_dir, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "SELFTEST_PASS (all self-test assertions passed)",
            "summary": "SELFTEST_PASS", "elapsed_s": 0.0, "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        })
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, 1)

    t0 = time.perf_counter()
    print(f"[lexicon_coverage_audit_barrier2] run_mode={run_mode} corpus={CONLLU_PATH} "
          f"hand_judgments={HAND_JUDGMENTS_PATH}", flush=True)

    result = run_full()
    tier, msg, prediction2_supported, band_detail = compute_verdict(result["coverage_stats"], result["split_stats"])
    elapsed = time.perf_counter() - t0

    print(f"[lexicon_coverage_audit_barrier2] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[lexicon_coverage_audit_barrier2] {msg}", flush=True)

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_sentences": result["n_sentences"],
        "coverage_stats": result["coverage_stats"],
        "sample_size": result["sample_size"],
        "integrity_ok": result["integrity_ok"],
        "split_stats": result["split_stats"],
        "band_detail": band_detail,
        "prediction2_lexicon_distinct_from_foundation_size_supported": prediction2_supported,
        "corpus": {
            "name": "UD_English-EWT test split (fork-independent re-parse; SAME corpus file as Rung 5-9, "
                    "NOT the same parser code)",
            "path": str(CONLLU_PATH), "license": "CC BY-SA 4.0",
        },
        "resources": {
            "verbnet": "3621 lemmas (nltk.corpus.verbnet, local cache)",
            "propbank": "3319 lemmas / 4659 rolesets (nltk.corpus.propbank, local cache, fetched once "
                        "this session via nltk.download -- one-time env setup, no runtime network access)",
            "framenet": "3318 verb-LU lemmas (nltk.corpus.framenet, local cache)",
        },
        "prereg": {
            "hard_pass": f"coverage_union_vn_pb_token_frac>={HARD_PASS_COVERAGE} AND "
                         f"type_level_frac_of_audited_sample>={HARD_PASS_TYPE_FRAC} (and not floor-hugging, "
                         f"META_RULE_L)",
            "hard_fail": f"coverage_union_vn_pb_token_frac<{HARD_FAIL_COVERAGE} OR "
                        f"type_level_frac_of_audited_sample<{HARD_FAIL_TYPE_FRAC}",
            "bands_source": "verbatim from Research's own Prediction 2 in "
                            "notes/research_lexicon_richness_subcategorization_barrier_real_prose_parsing_"
                            "2026-07-17.md, pre-registered BEFORE this run",
            "sample_seed": SAMPLE_SEED, "sample_n": SAMPLE_N,
            "scoping": "type-vs-instance judgment covers VERB-ARGUMENT selectional/sense resolution only, NOT "
                      "pronoun/coreference resolution (a separate, already-identified barrier -- deliberately "
                      "excluded to avoid conflating two distinct barriers)",
            "honest_limitations": "single-rater hand-audit (no inter-rater reliability); UD-EWT is informal/"
                                  "transactional web register, likely under-representing metaphor/instance-"
                                  "dependent language vs literary prose; n=120 modest for a proportion this "
                                  "close to 1.0; ~25% of type_level rests on treating idiom/MWE and multi-"
                                  "sense-but-frame-disambiguated readings as lexicon-resolvable (subclass "
                                  "breakdown reported for reader re-derivation under a stricter reading)",
            "final_metrics_atomicity": "tmp_replace",
            "storage_strategy": "no_storage (pure external-lexicon coverage measurement, no HD substrate "
                                "object touched)",
            "compute_architecture": "sequential-CPU; pure CoNLL-U/dict processing + nltk lemma-set lookups; "
                                    "no torch, no GPU primitive; wall time trivial (MEASURED above)",
            "cardinality_ok": "n/a_no_sweep_axis",
            "baseline_in_band": "n/a_no_baseline_arm_single_measurement_audit",
            "calibration_check": "n/a_bands_are_verbatim_prereg_thresholds_not_tuned",
            "crlb_n/a": "no quantitative noise floor in the CRLB sense; informal binomial SE reported in "
                       "split_stats.type_level_wald_se_approx, not gated",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["parse_conllu (real corpus file, self-test slice)",
                                         "nltk.corpus.verbnet/propbank/framenet (real resource lookups, "
                                         "self-test)"],
            "substrate_signature_checked": "n/a_no_substrate_object_calls_this_is_a_pure_external_lexicon_"
                                           "measurement",
            "guard_baseline_validated": "n/a_no_control_beats_baseline_guard",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a "
                               "runtime sys.modules transitive-closure check after nltk use, both asserted "
                               "at self-test",
            "prior_work_check": "substrate_query.sh run before authoring -- top hit cosine=0.2832 (unrelated "
                                "T3-deeper-ingest note), all 5 hits below the cosine>0.30 rediscovery "
                                "threshold; NOVEL, not a rediscovery.",
            "fork_independence": "this cell's CoNLL-U parser + coverage/sampling/judgment logic is a fresh, "
                                 "independent implementation; it does NOT import from any exp_read_grow_* "
                                 "module in the Rung 5-9 real-prose reading arc (reuses only the corpus FILE, "
                                 "not that arc's parser code), per Director's explicit instruction",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[lexicon_coverage_audit_barrier2] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
