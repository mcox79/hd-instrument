"""exp_definitional_predicate_v6 -- keep the PREDICATE the definitional extractor throws away.

FINDING BEING ACTED ON (notes/verb_definition_gap_2026-08-13.md): the foundation has 0 verb
definitions in 2092 facts, but 119 of those facts ALREADY have a process-flavoured genus head.
The extractor fires on process definitions and then discards the verbal content, because
`definiens_head()` returns the leading-NP head and `_NP_BOUNDARY` cuts at `of / by / which /
when` -- exactly where the predicate starts. We bank `photosynthesis ISA process` and drop
"by which light energy is converted to chemical energy".

APPROVED SCOPE (director, 2026-08-13) -- three patterns, and only these:
  VP1 PROCESS_OF    "X is the process of V-ing (Y)"            -> additionally emit the predicate
  VP2 BY_WHICH      "X is the process by/through which CLAUSE" -> read the clause's main verb
  VP4 OCCURS_WHEN   "X occurs when CLAUSE"                     -> ENABLING_CONDITION, *NOT* ISA
OUT OF SCOPE and NOT implemented: VP3 (determinerless glossary colon -- relaxing _DET reopens
the `cell -> nucleoid` regression), VP5 (VP_CALLED -- its antecedent left boundary is already
wrong in shipped code; that fix comes first, separately, and is only DIAGNOSED here), and any
`to X is to Y` verb-gloss rule (1 real hit vs 45 purposive false positives).

HARD CONSTRAINTS THIS CELL ENFORCES AND PROVES
  1 ADDITIVE ONLY. The ISA fact set is recomputed on the SAME corpus with a byte-copy of the
    PRE-PATCH module (data/exp_definitional_predicate_v6/_baseline_definitional_extraction_
    prepatch.py, sha256 recorded) and sha256-compared against the post-patch one. Unequal =>
    HARD_FAIL_ISA_CHANGED. This is the constraint-1 proof, not a claim.
  2 SCHEMA: 3-tuples only. The store persists (subject, relation, object) and drops edge
    metadata on flush, so a predicate is emitted as ADDITIONAL separate 3-tuples with distinct
    relation types. No enriched record is invented.
  3 ONE VARIABLE: hdlab/definitional_extraction.py gained one appended block and its self-tests.
    Nothing above that block was renamed, reformatted or "improved".
  4 GROWTH IS PAUSED: output goes ONLY to data/exp_definitional_predicate_v6/. Nothing is
    written to data/foundation/** . These facts are UNBANKED until hand-scored.
  5 OMP_NUM_THREADS=1 / OPENBLAS_NUM_THREADS=1; sorted(set(...)) only.

NOT SCORED HERE. The cell writes an UNSCORED 50-row blind sample carrying the SOURCE SENTENCE
beside every extracted fact, and claims no quality band. Counts are counts, not judgements.

CELL-TEMPLATE MANDATORY:
 - final_metrics_atomicity: tmp_replace
 - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
 - start marker + crash metrics; heartbeat n/a (single pass, progress printed per corpus file)
 - crlb n/a: deterministic symbolic extraction, no estimator noise floor
 - arms_differ_verified: pre-patch vs post-patch ISA digests MUST be EQUAL here (that is the
   point); the arms that must DIFFER are ISA vs PREDICATE, and their relation sets are disjoint
 - cardinality n/a: no seed/sweep axis
 - deterministic_seeding: fixed seed 42; sorted(set(...)) only
ASCII-only.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse                                                       # noqa: E402
import hashlib                                                        # noqa: E402
import importlib.util                                                 # noqa: E402
import io                                                             # noqa: E402
import json                                                           # noqa: E402
import platform                                                       # noqa: E402
import random                                                         # noqa: E402
import re                                                             # noqa: E402
import sys                                                            # noqa: E402
import time                                                           # noqa: E402
import traceback                                                      # noqa: E402
from collections import Counter, defaultdict                          # noqa: E402
from datetime import datetime, timezone                               # noqa: E402
from typing import Dict, List, Optional, Tuple                        # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.definitional_extraction as DE                            # noqa: E402
from hdlab.closed_class_lexicon import is_closed_class                # noqa: E402
from hdlab.thematic_role_labeler import lemma_word                    # noqa: E402

ANCHOR_NAME = "definitional_predicate_v6"
MAX_SOURCE_SENTENCES = 10
SAMPLE_N = 50
SAMPLE_SEED = 42

OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_definitional_predicate_v6")
BASELINE_MODULE = os.path.join(OUT_DIR, "_baseline_definitional_extraction_prepatch.py")
# On-disk cross-check that our sampler is the SAME convention as the v5 B3 audit sample.
V5_SAMPLE = os.path.join(REPO_ROOT, "data", "exp_definitional_grounding_v5",
                         "b3_audit_sample_DEF_V5.json")

# The scoping pass's corpus, verbatim: biology_2e + anatomy_physiology_2e + psychology_2e.
# mcguffey is DELIBERATELY EXCLUDED (director scope).
CORPUS_FILES = [
    ("BIO", os.path.join(REPO_ROOT, "data", "corpora", "textbook_biology_2e", "cleaned",
                         "biology_2e.clean.txt")),
    ("ANAT", os.path.join(REPO_ROOT, "data", "corpora", "textbook_anatomy_physiology_2e",
                          "cleaned", "anatomy_physiology_2e.clean.txt")),
    ("PSY", os.path.join(REPO_ROOT, "data", "corpora", "textbook_psychology_2e", "cleaned",
                         "psychology_2e.clean.txt")),
]
MIN_CHARS, MAX_CHARS = 25, 400

TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")


# ======================================================================== instrumentation
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_json(os.path.join(output_dir, "metrics.json"), {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME})


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ======================================================================== corpus
def _clean_sentences(text: str) -> List[str]:
    """The repo's OWNED sentence recipe (byte-identical to
    experiments.exp_definitional_grounding_v5._clean_sentences), applied PER LINE."""
    quotes = "'\"" + chr(0x2019) + chr(0x201d)
    parts = re.split("[.!?]+[" + quotes + "]?", text)
    return [s.strip() for s in parts if s.strip()]


def load_corpus(limit: Optional[int] = None) -> List[Tuple[str, int, str]]:
    """(file_tag, line_number, sentence) over the three OpenStax textbooks.

    Headings (markdown `#` lines) are stripped, list bullets/numbering removed, sentences kept
    at 25-400 chars. This is a RECONSTRUCTION of the scoping pass's loader -- that pass left no
    script on disk. It reuses the repo's own `_clean_sentences` recipe rather than inventing a
    new one, and it reproduces the scoping note's provenance form `[FILE:line]`. It yields
    72,501 sentences vs the note's 72,319 (+0.25%); the delta is disclosed in metrics.json and
    is NOT reconciled, because the note's exact recipe is unrecoverable."""
    out: List[Tuple[str, int, str]] = []
    for tag, path in CORPUS_FILES:
        with io.open(path, encoding="utf-8") as f:
            for lineno, ln in enumerate(f, start=1):
                s = ln.strip()
                if not s or s.startswith("#"):
                    continue
                s = re.sub(r"^[-*]\s+", "", s)
                s = re.sub(r"^\d+\.\s+", "", s)
                for x in _clean_sentences(s):
                    if MIN_CHARS <= len(x) <= MAX_CHARS:
                        out.append((tag, lineno, x))
                        if limit is not None and len(out) >= limit:
                            return out
    return out


# ======================================================================== ISA arm (unchanged path)
def build_isa_pairs(module, corpus: List[Tuple[str, int, str]]) -> List[Tuple[str, str, str]]:
    """DISTINCT (term, head, pattern) from `module.extract_definitions`. This is the EXISTING
    ISA read-out. The only reason it is computed twice (pre-patch module and post-patch module)
    is to PROVE the patch did not touch it."""
    pairs = set()
    for _tag, _ln, sent in corpus:
        for d in module.extract_definitions(sent):
            if d.term and d.head:
                pairs.add((d.term, d.head, d.pattern))
    return sorted(pairs)


def _digest_pairs(pairs) -> str:
    h = hashlib.sha256()
    for p in pairs:
        h.update(("|".join(p) + "\n").encode("utf-8"))
    return h.hexdigest()


def load_prepatch_module():
    """Import the byte-copy of the module as it stood BEFORE the VP block was appended."""
    spec = importlib.util.spec_from_file_location("_de_prepatch", BASELINE_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pre-patch baseline module at %s" % BASELINE_MODULE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_de_prepatch"] = mod
    spec.loader.exec_module(mod)
    if hasattr(mod, "extract_predicates"):
        raise AssertionError("BLOCK: the 'pre-patch' baseline already has the VP block -- it is "
                             "not a pre-patch copy and proves nothing")
    return mod


# ======================================================================== PREDICATE arm
def build_predicate_facts(corpus: List[Tuple[str, int, str]]
                          ) -> Tuple[List[dict], Counter, Counter]:
    """One row per DISTINCT (subject, relation, object) 3-tuple."""
    by_key: Dict[Tuple[str, str, str], dict] = {}
    per_pattern: Counter = Counter()
    cand_sent: Counter = Counter()
    for tag, lineno, sent in corpus:
        for pat in DE.predicate_candidate_pattern(sent):
            cand_sent[pat] += 1
        for p in DE.extract_predicates(sent):
            if is_closed_class(p.object) and p.relation in ("PROCESS_PATIENT",
                                                            "ENABLING_CONDITION_AGENT"):
                continue
            key = (p.term, p.relation, p.object)
            row = by_key.get(key)
            if row is None:
                by_key[key] = {
                    "subject": p.term, "relation": p.relation, "object": p.object,
                    "subject_type": p.term_type, "pattern": p.pattern,
                    "patterns_seen": [p.pattern], "n_attestations": 1,
                    "definiendum_surface": p.definiendum, "predicate_span": p.predicate_span,
                    "source_sentences": [sent], "provenance": ["%s:%d" % (tag, lineno)],
                }
                per_pattern[p.pattern] += 1
            else:
                row["n_attestations"] += 1
                if p.pattern not in row["patterns_seen"]:
                    row["patterns_seen"].append(p.pattern)
                if (len(row["source_sentences"]) < MAX_SOURCE_SENTENCES
                        and sent not in row["source_sentences"]):
                    row["source_sentences"].append(sent)
                    row["provenance"].append("%s:%d" % (tag, lineno))
    facts = [by_key[k] for k in sorted(by_key)]
    for i, f in enumerate(facts):
        f["fid"] = i
    return facts, per_pattern, cand_sent


def converted_sentences(corpus: List[Tuple[str, int, str]]) -> Dict[str, int]:
    """How many CANDIDATE sentences each pattern actually turned into >=1 fact (the numerator of
    the per-pattern yield rate). Counted at the SENTENCE level, not the fact level."""
    conv: Counter = Counter()
    for _tag, _ln, sent in corpus:
        pats = {p.pattern for p in DE.extract_predicates(sent)}
        for p in sorted(pats):
            conv[p] += 1
    return dict(conv)


# --- reconstruction of the scoping note's 818-sentence candidate pool ------------------------
# The note reports a union of P2/P3/P4/P6/P10 = 818 sentences (1.13%). Its regexes were not left
# on disk, so these are a BEST-EFFORT RECONSTRUCTION from the note's prose descriptions and are
# reported as such. The PRIMARY yield denominators are this cell's own candidate regexes above.
_CONT = "(?:process|act|mechanism|method|technique|reaction|response|movement|series|phenomenon)"
_NOTE_TRIGGERS = {
    "P2_process_of_or_in_which": re.compile(
        r"\b(?:is|are)\s+(?:a|an|the)\s+(?:[A-Za-z'\-]+\s+){0,2}?" + _CONT +
        r"\s+(?:of\s+[A-Za-z'\-]+ing|in\s+which)\b", re.IGNORECASE),
    "P3_occurs_when": re.compile(
        r"\b(?:occurs?|occurred|begins?|began|happens?|happened|takes\s+place)\s+when\b",
        re.IGNORECASE),
    "P4_by_which": re.compile(
        r"\b(?:process|mechanism|method|means|way|pathway)\s+(?:by|in|through)\s+which\b",
        re.IGNORECASE),
    "P6_during_nom": re.compile(r"^During\s+[A-Za-z]", re.IGNORECASE),
    "P10_ability_to_V": re.compile(
        r"\b(?:is|are)\s+the\s+(?:ability|tendency|capacity)\s+to\s+[A-Za-z]", re.IGNORECASE),
}


def note_candidate_pool(corpus: List[Tuple[str, int, str]]) -> dict:
    per = Counter()
    union = 0
    for _tag, _ln, sent in corpus:
        hit = False
        for name, rx in sorted(_NOTE_TRIGGERS.items()):
            if rx.search(sent):
                per[name] += 1
                hit = True
        if hit:
            union += 1
    return {"per_trigger": dict(sorted(per.items())), "union_sentences": union,
            "note_reported_union": 818,
            "caveat": "RECONSTRUCTION. The scoping pass left no script; these regexes were "
                      "rebuilt from its prose. Compare shapes, not exact equality."}


# ======================================================================== CALLED diagnostic
# MEASURE ONLY. Nothing about the CALLED pattern is changed by this cell (director: VP5 is out of
# scope and gated behind this fix). Each test below names a distinct way the antecedent's LEFT
# edge can be wrong.
_LEFT_FUNCTION_START = {
    "of", "in", "on", "for", "to", "with", "from", "into", "onto", "at", "as", "by", "between",
    "among", "through", "during", "within", "across", "over", "under", "and", "or", "but",
    "that", "which", "who", "whom", "whose", "where", "when", "while", "because", "if", "than",
    "such", "then", "also", "however", "therefore", "thus", "so",
}
_LEFT_FINITE_VERB = {"is", "are", "was", "were", "has", "have", "had", "does", "do", "did",
                     "can", "will", "would", "means", "becomes", "become", "includes",
                     "include", "consists", "consist", "occurs", "occur"}
_CALLED_TRIGGER = re.compile(
    r"\s+(?:is|are|was|were\s+)?\s*(?:called|known\s+as|termed|named|referred\s+to\s+as)\s+",
    re.IGNORECASE)


def called_left_boundary_diagnostic(corpus: List[Tuple[str, int, str]]) -> dict:
    """How often does the SHIPPED CALLED pattern take a wrong left boundary on its antecedent?

    Denominator = CALLED matches that actually BANK a fact (a mis-bounded antecedent only
    matters if a fact came out of it).
      L1_FUNCTION_WORD_START   the antecedent opens with a preposition / coordinator /
                               relativizer -> it began mid-constituent
      L2_CROSSES_FINITE_VERB   the antecedent contains a finite verb -> it swallowed a whole
                               preceding clause on its way left
      L3_TRUNCATED_MIDPHRASE   an open-class token sits immediately to the left with no
                               punctuation between -> a longer constituent was cut
      (reported separately, a HEAD test not a boundary test)
      L4_HEAD_NOT_ADJACENT     definiens_head(antecedent) is not the last nominal before the
                               naming trigger -> the head came from a different constituent
                               (this is the `intercellular signaling ISA cell` class)
    """
    counts = Counter()
    n_facts = 0
    examples: Dict[str, List[dict]] = defaultdict(list)
    for tag, lineno, sent in corpus:
        for m in DE._RE_CALLED.finditer(sent):
            dfs_text = DE._strip_leading_coordinator(sent, m.group("dfs"), m.start("dfs"))
            if dfs_text is None:
                continue
            d = DE._mk(m.group("dfd"), dfs_text, "CALLED", sent)
            if d is None:
                continue
            n_facts += 1
            raw = m.group("dfs")
            toks = TOK.findall(raw)
            if not toks:
                continue
            flags = []
            if toks[0].lower() in _LEFT_FUNCTION_START:
                flags.append("L1_FUNCTION_WORD_START")
            if any(t.lower() in _LEFT_FINITE_VERB for t in toks):
                flags.append("L2_CROSSES_FINITE_VERB")
            pre = sent[:m.start("dfs")]
            pre_toks = TOK.findall(pre)
            if pre_toks and pre.rstrip().endswith(pre_toks[-1]) and not is_closed_class(
                    lemma_word(pre_toks[-1])):
                flags.append("L3_TRUNCATED_MIDPHRASE")
            # L4: the last NOMINAL token before the naming trigger is the true head candidate
            last_nominal = None
            for t in toks:
                lem = lemma_word(t)
                if not is_closed_class(lem) and DE.is_nominal_lemma(lem):
                    last_nominal = lem
            if last_nominal is not None and d.head != last_nominal:
                flags.append("L4_HEAD_NOT_ADJACENT")
            for fl in flags:
                counts[fl] += 1
                if len(examples[fl]) < 8:
                    examples[fl].append({
                        "provenance": "%s:%d" % (tag, lineno),
                        "sentence": sent,
                        "antecedent_captured": raw,
                        "banked_fact": "%s ISA %s" % (d.term, d.head),
                        "last_nominal_before_trigger": last_nominal,
                    })
            if any(f.startswith(("L1", "L2", "L3")) for f in flags):
                counts["ANY_WRONG_LEFT_BOUNDARY"] += 1
            else:
                counts["CLEAN_LEFT_BOUNDARY"] += 1
    n = max(1, n_facts)
    return {
        "IN_SCOPE": False,
        "note": "MEASURE ONLY -- nothing about the CALLED pattern was changed. Scopes the "
                "deferred VP5 fix (director: VP5 is gated behind this left-boundary fix).",
        "n_called_facts_banked": n_facts,
        "counts": dict(sorted(counts.items())),
        "rate_any_wrong_left_boundary": round(counts["ANY_WRONG_LEFT_BOUNDARY"] / n, 4),
        "rate_L4_head_not_adjacent": round(counts["L4_HEAD_NOT_ADJACENT"] / n, 4),
        "examples": {k: v[:5] for k, v in sorted(examples.items())},
    }


# ======================================================================== sampling
def sample_for_audit(facts: List[dict], k: int = SAMPLE_N, seed: int = SAMPLE_SEED) -> List[dict]:
    """IDENTICAL convention to the v2/v3/v4/v5 B3 audits: random.Random(seed).sample over the
    facts in fid (= insertion) order, then sorted. Cross-checked on disk in _selftest_sampling."""
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(facts)), min(k, len(facts))))
    return [facts[i] for i in idx]


def _selftest_sampling() -> dict:
    """The sampler must reproduce the ACTUAL fid list of the committed v5 B3 sample on disk.
    A synthetic self-comparison would only prove the function equals itself."""
    with io.open(V5_SAMPLE, encoding="utf-8") as f:
        v5 = json.load(f)
    n = v5["n_facts_in_arm"]
    got = [r["fid"] for r in v5["rows"]]
    expect = sorted(random.Random(SAMPLE_SEED).sample(range(n), SAMPLE_N))
    assert got == expect, "HARD_FAIL_SAMPLING_DRIFT: %r != %r" % (got[:8], expect[:8])
    synth = [{"subject": "s%d" % i, "fid": i} for i in range(n)]
    assert [r["fid"] for r in sample_for_audit(synth)] == expect, "HARD_FAIL_SAMPLING_DRIFT"
    return {"v5_sample_n_facts": n, "fids_matched": len(got)}


# ======================================================================== self-test
def _selftest_real_code_path_tiny() -> dict:
    exercised = set()
    corpus = [
        ("BIO", 1, "Hydrolysis is the process of breaking complex macromolecules apart"),
        ("BIO", 2, "Differentiation is the process by which unspecialized cells become "
                   "specialized to carry out distinct functions"),
        ("BIO", 3, "Dissociation occurs when atoms or groups of atoms break off from molecules"),
        ("BIO", 4, "A nephron is the functional unit of the kidney"),
        ("BIO", 5, "This occurs when the temperature drops"),
    ]
    exercised.add("extract_predicates")
    facts, per_pattern, cand = build_predicate_facts(corpus)
    trip = {(f["subject"], f["relation"], f["object"]) for f in facts}
    assert ("hydrolysis", "PROCESS_ACTION", "break") in trip, trip
    assert ("differentiation", "PROCESS_ACTION", "become") in trip, trip
    assert ("dissociation", "ENABLING_CONDITION", "break") in trip, trip
    assert not any(s == "this" for s, _r, _o in trip), trip          # anaphoric subject refused
    assert all(r in DE.PREDICATE_RELATIONS for _s, r, _o in trip), trip
    assert all(len(t) == 3 for t in trip), trip                       # 3-tuples only

    exercised.add("extract_definitions")
    isa_post = build_isa_pairs(DE, corpus)
    assert ("nephron", "unit", "COPULA") in isa_post, isa_post
    assert ("hydrolysis", "process", "COPULA") in isa_post, isa_post  # ISA survives ADDITIVELY

    exercised.add("load_prepatch_module")
    pre = load_prepatch_module()
    isa_pre = build_isa_pairs(pre, corpus)
    assert _digest_pairs(isa_pre) == _digest_pairs(isa_post), (isa_pre, isa_post)

    exercised.add("called_left_boundary_diagnostic")
    diag = called_left_boundary_diagnostic(
        [("BIO", 9, "The region of unwinding is called a transcription bubble")])
    assert diag["n_called_facts_banked"] >= 1, diag

    exercised.add("load_corpus")
    tiny = load_corpus(limit=25)
    assert len(tiny) == 25 and all(MIN_CHARS <= len(s) <= MAX_CHARS for _t, _l, s in tiny)

    exercised.add("sample_for_audit")
    exercised.add("converted_sentences")
    conv = converted_sentences(corpus)
    assert conv.get("VP1_PROCESS_OF") == 1 and conv.get("VP4_OCCURS_WHEN") == 1, conv

    declared = {"extract_predicates", "extract_definitions", "load_prepatch_module",
                "called_left_boundary_diagnostic", "load_corpus", "sample_for_audit",
                "converted_sentences"}
    missing = declared - exercised
    assert not missing, "real_code_path: declared but not exercised: %s" % sorted(missing)
    return {"n_tiny_predicate_facts": len(facts), "per_pattern": dict(per_pattern),
            "candidate_sentences": dict(cand), "exercised": sorted(exercised)}


def run_self_test() -> dict:
    t0 = time.perf_counter()
    DE._self_test()
    samp = _selftest_sampling()
    tiny = _selftest_real_code_path_tiny()
    return {"verdict": "SELFTEST_PASS",
            "verdict_msg": "module self-test (incl. every v3/v4/v5 ISA regression) + on-disk "
                           "sampling cross-check + real code path",
            "summary": "selftest", "elapsed_s": round(time.perf_counter() - t0, 2),
            "sampling": samp, "tiny": tiny}


# ======================================================================== full
def run_full(limit: Optional[int]) -> dict:
    t0 = time.perf_counter()
    _selftest_sampling()

    print("[progress] loading corpus", flush=True)
    corpus = load_corpus(limit)
    per_file = Counter(tag for tag, _l, _s in corpus)
    print("[progress] %d sentences %r" % (len(corpus), dict(per_file)), flush=True)

    print("[progress] ISA arm -- PRE-PATCH module", flush=True)
    pre_mod = load_prepatch_module()
    isa_pre = build_isa_pairs(pre_mod, corpus)
    print("[progress] ISA pre-patch = %d" % len(isa_pre), flush=True)

    print("[progress] ISA arm -- POST-PATCH module", flush=True)
    isa_post = build_isa_pairs(DE, corpus)
    print("[progress] ISA post-patch = %d" % len(isa_post), flush=True)

    d_pre, d_post = _digest_pairs(isa_pre), _digest_pairs(isa_post)
    isa_unchanged = (d_pre == d_post) and (len(isa_pre) == len(isa_post))

    print("[progress] PREDICATE arm", flush=True)
    pfacts, per_pattern, cand_sent = build_predicate_facts(corpus)
    conv = converted_sentences(corpus)
    print("[progress] predicate facts = %d" % len(pfacts), flush=True)

    print("[progress] CALLED left-boundary diagnostic", flush=True)
    called_diag = called_left_boundary_diagnostic(corpus)

    print("[progress] scoping-note candidate-pool reconstruction", flush=True)
    pool = note_candidate_pool(corpus)

    rel_mix = Counter(f["relation"] for f in pfacts)
    pat_mix = Counter(f["pattern"] for f in pfacts)
    yield_per_pattern = {}
    for p in sorted(DE.PREDICATE_PATTERNS):
        c = cand_sent.get(p, 0)
        yield_per_pattern[p] = {
            "candidate_sentences_regex_fired": c,
            "sentences_converted_to_at_least_one_fact": conv.get(p, 0),
            "yield_rate_sentences": round(conv.get(p, 0) / c, 4) if c else 0.0,
            "distinct_facts_emitted": pat_mix.get(p, 0),
        }

    # --------------------------------------------------------------- write the fact file
    os.makedirs(OUT_DIR, exist_ok=True)
    fpath = os.path.join(OUT_DIR, "predicate_facts_v6.jsonl")
    tmp = fpath + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for r in pfacts:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, fpath)

    isa_path = os.path.join(OUT_DIR, "isa_facts_unchanged_v6.jsonl")
    tmp = isa_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for term, head, pat in isa_post:
            f.write(json.dumps({"subject": term, "relation": "GROUNDED_MEANING",
                                "object": head, "pattern": pat}, ensure_ascii=False) + "\n")
    os.replace(tmp, isa_path)

    # --------------------------------------------------------------- BLIND hand-score sample
    rows = []
    for r in sample_for_audit(pfacts):
        rows.append({
            "fid": r["fid"],
            "subject": r["subject"],
            "relation": r["relation"],
            "object": r["object"],
            "triple": "(%s, %s, %s)" % (r["subject"], r["relation"], r["object"]),
            "pattern": r["pattern"],
            "subject_type": r["subject_type"],
            "n_attestations": r["n_attestations"],
            "definiendum_surface": r["definiendum_surface"],
            "predicate_span": r["predicate_span"],
            "provenance": r["provenance"],
            "source_sentences": r["source_sentences"],
        })
    sample_path = os.path.join(OUT_DIR, "predicate_audit_sample.json")
    _atomic_write_json(sample_path, {
        "arm": "DEF_V6_PREDICATE",
        "n_facts_in_arm": len(pfacts),
        "sample_seed": SAMPLE_SEED,
        "sampling": "random.Random(42).sample over fid order -- SAME convention as "
                    "data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json, verified "
                    "against that file's own fid list on disk in _selftest_sampling()",
        "rubric": "DIRECTOR'S BLIND JUDGEMENT. Each row carries the SOURCE SENTENCE beside the "
                  "extracted 3-tuple so the predicate can be judged against the text that "
                  "produced it. No rubric buckets are pre-assigned.",
        "scored": False,
        "note": "UNSCORED AND UNBANKED. The cell assigns no buckets and claims no quality band. "
                "There is NO prior baseline for a predicate-valued relation -- the v5 64% "
                "MEANINGFUL hand-score is for GROUNDED_MEANING genus facts and does not "
                "transfer. GROWTH IS PAUSED: nothing here is written to data/foundation/**.",
        "relations_in_arm": dict(sorted(rel_mix.items())),
        "rows": rows,
    })

    verdict, msgs = "STRUCTURAL_PASS_PENDING_HANDSCORE", []
    if not isa_unchanged:
        verdict = "HARD_FAIL_ISA_CHANGED"
        msgs.append("ISA fact set changed: pre=%d post=%d digest %s vs %s"
                    % (len(isa_pre), len(isa_post), d_pre[:12], d_post[:12]))
    if not pfacts:
        verdict = "HARD_FAIL_ZERO_YIELD"
        msgs.append("no predicate facts emitted")
    if set(rel_mix) - set(DE.PREDICATE_RELATIONS):
        verdict = "HARD_FAIL_SCHEMA"
        msgs.append("unknown relation types: %s" % sorted(set(rel_mix) - set(DE.PREDICATE_RELATIONS)))
    if any(r["relation"] == "GROUNDED_MEANING" for r in pfacts):
        verdict = "HARD_FAIL_SCHEMA"
        msgs.append("a predicate fact was emitted into the ISA relation")

    return {
        "verdict": verdict,
        "verdict_msg": (
            "predicate v6: ISA %d -> %d (%s); %d predicate 3-tuples "
            "(VP1 %d / VP2 %d / VP4 %d); %s"
            % (len(isa_pre), len(isa_post),
               "UNCHANGED" if isa_unchanged else "CHANGED -- CONSTRAINT 1 VIOLATED",
               len(pfacts), pat_mix.get("VP1_PROCESS_OF", 0), pat_mix.get("VP2_BY_WHICH", 0),
               pat_mix.get("VP4_OCCURS_WHEN", 0),
               "; ".join(msgs) if msgs else "all machine checks pass")),
        "summary": "keep the predicate the definitional extractor discards",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "run_mode": "full" if limit is None else "smoke",

        # ---- CONSTRAINT 1 PROOF -----------------------------------------------------------
        "isa_facts_BEFORE_patch": len(isa_pre),
        "isa_facts_AFTER_patch": len(isa_post),
        "isa_unchanged": isa_unchanged,
        "isa_digest_before": d_pre,
        "isa_digest_after": d_post,
        "isa_pattern_mix": dict(sorted(Counter(p for _t, _h, p in isa_post).items())),
        "prepatch_module_sha256": _sha256_file(BASELINE_MODULE),
        "postpatch_module_sha256": _sha256_file(DE.__file__.replace(".pyc", ".py")),

        # ---- NEW PREDICATE FACTS ----------------------------------------------------------
        "n_predicate_facts": len(pfacts),
        "predicate_relation_mix": dict(sorted(rel_mix.items())),
        "predicate_pattern_mix": dict(sorted(pat_mix.items())),
        "n_enabling_condition_facts": rel_mix.get("ENABLING_CONDITION", 0)
                                      + rel_mix.get("ENABLING_CONDITION_AGENT", 0),
        "n_distinct_predicate_subjects": len(sorted(set(f["subject"] for f in pfacts))),
        "n_distinct_verbs": len(sorted(set(f["object"] for f in pfacts
                                           if f["relation"] in ("PROCESS_ACTION",
                                                                "ENABLING_CONDITION")))),
        "yield_per_pattern": yield_per_pattern,
        "scoping_note_candidate_pool_reconstruction": pool,

        # ---- CORPUS -----------------------------------------------------------------------
        "corpus_files": [os.path.relpath(p, REPO_ROOT) for _t, p in CORPUS_FILES],
        "corpus_sentences": len(corpus),
        "corpus_sentences_per_file": dict(sorted(per_file.items())),
        "corpus_note": "scoping note reports 72,319 sentences; this loader (a reconstruction -- "
                       "the scoping pass left no script) yields %d. Delta disclosed, not "
                       "reconciled." % len(corpus),
        "mcguffey_excluded": True,

        # ---- OUT-OF-SCOPE DIAGNOSTIC -------------------------------------------------------
        "called_left_boundary_diagnostic": called_diag,

        "predicate_facts_path": os.path.relpath(fpath, REPO_ROOT),
        "isa_facts_path": os.path.relpath(isa_path, REPO_ROOT),
        "audit_sample_path": os.path.relpath(sample_path, REPO_ROOT),
        "quality_scored_here": False,
        "banked": False,
        "wire_status": "UNBANKED_PENDING_DIRECTOR_HANDSCORE",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if args.mode == "self-test":
        m = run_self_test()
        _atomic_write_json(os.path.join(OUT_DIR, "selftest_metrics.json"), m)
        print(json.dumps(m, indent=2)[:3000])
        return
    _write_start_marker(OUT_DIR, args.mode)
    limit = args.limit if args.limit is not None else (2000 if args.mode == "smoke" else None)
    m = run_full(limit)
    out = os.path.join(OUT_DIR, "metrics.json" if args.mode == "full" else "smoke_metrics.json")
    _atomic_write_json(out, m)
    print(json.dumps({k: v for k, v in m.items()
                      if k != "called_left_boundary_diagnostic"}, indent=2)[:6000])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:                                            # noqa: BLE001
        _write_crash_metrics(OUT_DIR, e)
        raise
