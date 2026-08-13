"""exp_called_boundary_v7 -- fix the CALLED antecedent's LEFT BOUNDARY and HEAD, measured apart.

FINDING BEING ACTED ON (data/exp_definitional_predicate_v6/metrics.json ->
`called_left_boundary_diagnostic`, over the 1,622 CALLED facts the SHIPPED extractor banks on
biology_2e + anatomy_physiology_2e + psychology_2e):

  L1 antecedent opens with a function word            182
  L2 antecedent swallows a finite verb                534
  L3 antecedent truncated mid-phrase                   36
  -> ANY WRONG LEFT BOUNDARY                          668  (41.2%)
  L4 head is not the constituent adjacent to trigger  851  (52.5%)  measured separately

Real banked failures: `fermentation ISA nadh`, `impurity ISA mold`.

TWO CHANGES, MEASURED SEPARATELY (hdlab/definitional_extraction.py, CALLED-BOUNDARY v7 block):
  A = CALLED_FIX_LEFT   WHICH SPAN is the antecedent (constituent walk left from the trigger)
  B = CALLED_FIX_HEAD   WHICH SUB-CONSTITUENT supplies the genus head
Four arms are run over the same corpus: BASELINE (pre-patch byte copy), A_ONLY, B_ONLY, A_PLUS_B.
No arm's numbers are merged with another's.

HARD CONSTRAINTS THIS CELL ENFORCES AND PROVES
  1 REFUSAL IS FIRST-CLASS. `called_antecedent` returns None when the true boundary is not
    recoverable and NO fact is emitted. Refusals are counted and reported by reason, not hidden.
  2 NO REGRESSION ON THE OTHER FOUR PATTERNS. COPULA / GLOSSARY_COLON / APPOSITIVE / REFERS_TO
    fact sets are sha256'd from a BYTE COPY of the pre-patch module and from the patched module,
    over the same corpus. Reported per pattern, both sides.
    CONCURRENCY DISCLOSURE: a second agent (predicate_v61) was editing OTHER parts of the same
    module while this ran. The byte copy was taken BEFORE both sets of edits, so a difference
    would not by itself be attributable to this patch. The A_OFF_B_OFF arm exists to separate
    them: it runs the PATCHED module with both v7 switches OFF, so
    BASELINE == A_OFF_B_OFF proves the rest of the file's churn is behaviourally neutral, and
    A_OFF_B_OFF vs A_PLUS_B isolates THIS patch.
  3 Same corpus as the predicate run: biology_2e + anatomy_physiology_2e + psychology_2e,
    mcguffey EXCLUDED. The exact loaded sentence count is disclosed in metrics.json.
  4 GROWTH IS PAUSED: output goes ONLY to data/exp_called_boundary_v7/. Nothing is written to
    data/foundation/**.
  5 ONE VARIABLE: the CALLED pattern. No refactors or renames elsewhere.
  6 OMP_NUM_THREADS=1 / OPENBLAS_NUM_THREADS=1; sorted(set(...)) only.

THE L1-L4 DETECTOR IS THE ORIGINAL. Its body is copied VERBATIM from
experiments/exp_definitional_predicate_v6.py::called_left_boundary_diagnostic -- same token
sets, same tests, same order. The ONE thing that differs per arm is the (span, span_start) it is
handed: for BASELINE that is the raw regex capture `m.group("dfs")` / `m.start("dfs")`, exactly
as before; for the fixed arms it is the span that arm ACTUALLY uses to build the fact. That is
the point of the fix, not a change of ruler.

KNOWN DETECTOR ARTEFACTS (stated up front, not discovered after the numbers):
 - L1 and L2 go to ZERO BY CONSTRUCTION in any arm with A on: the walk's stop set is a SUPERSET
   of the detector's L1/L2 token sets. Those two counts are therefore NOT independent
   confirmation, they are restatements of the fix. L3 and L4 ARE independent.
 - L3 fires whenever an open-class token abuts the span's left edge. A correctly-bounded NP
   preceded by a verb ("to form STRUCTURES called nucleosomes") trips it. Residual L3 is
   therefore an upper bound on real truncation.
 - L4 fires whenever `head != last nominal in span`. That is the WRONG ruler for a copula-linked
   antecedent, where the head is the subject NP's head and a post-modifier legitimately sits
   between it and the trigger ("These unused structures WITHOUT FUNCTION are called ..." -> head
   `structure`, last nominal `function`; taking the last nominal would resurrect the v4 F4
   polarity fault). Residual L4 is decomposed by mode in metrics.json so this is visible.

NOT SCORED HERE. Writes an UNSCORED 50-row blind sample and a 30-row paired before/after sample.
Claims no quality band. Counts are counts.

CELL-TEMPLATE MANDATORY:
 - final_metrics_atomicity: tmp_replace
 - except SystemExit: raise BEFORE except Exception; no bare except
 - start marker + crash metrics; single pass, progress printed per arm
 - crlb n/a: deterministic symbolic extraction, no estimator noise floor
 - arms_differ_verified: BASELINE vs A_PLUS_B CALLED sets MUST differ (else the patch is inert);
   the other four patterns MUST NOT
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

ANCHOR_NAME = "called_boundary_v7"
MAX_SOURCE_SENTENCES = 10
SAMPLE_N = 50
PAIRED_N = 30
SAMPLE_SEED = 42

OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_called_boundary_v7")
BASELINE_MODULE = os.path.join(OUT_DIR, "_baseline_definitional_extraction_prepatch.py")
V5_SAMPLE = os.path.join(REPO_ROOT, "data", "exp_definitional_grounding_v5",
                         "b3_audit_sample_DEF_V5.json")

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
PATTERNS_OTHER = ("APPOSITIVE", "COPULA", "GLOSSARY_COLON", "REFERS_TO")


# ======================================================================== instrumentation
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write_json(path: str, payload) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
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
    """The repo's OWNED sentence recipe, byte-identical to the one used by
    experiments/exp_definitional_predicate_v6.py and exp_definitional_grounding_v5.py."""
    quotes = "'\"" + chr(0x2019) + chr(0x201d)
    parts = re.split("[.!?]+[" + quotes + "]?", text)
    return [s.strip() for s in parts if s.strip()]


def load_corpus(limit: Optional[int] = None) -> List[Tuple[str, int, str]]:
    """(file_tag, line_number, sentence). IDENTICAL loader to exp_definitional_predicate_v6, so
    the before-numbers this cell recomputes are directly comparable to the ones it is fixing."""
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


def load_prepatch_module():
    """Import the byte copy of the module as it stood BEFORE the v7 CALLED block was added."""
    spec = importlib.util.spec_from_file_location("_de_prepatch_v7", BASELINE_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pre-patch baseline module at %s" % BASELINE_MODULE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_de_prepatch_v7"] = mod
    spec.loader.exec_module(mod)
    if hasattr(mod, "called_antecedent"):
        raise AssertionError("BLOCK: the 'pre-patch' baseline already carries the v7 CALLED "
                             "block -- it is not a pre-patch copy and proves nothing")
    return mod


# ======================================================================== fact sets per pattern
def pattern_fact_sets(module, corpus) -> Dict[str, List[Tuple[str, str, str]]]:
    """pattern -> sorted DISTINCT (term, head, pattern) over the corpus, via the REAL pipeline
    (`extract_definitions`, so glossary splitting and cross-pattern dedup are included)."""
    per: Dict[str, set] = {p: set() for p in ("CALLED",) + PATTERNS_OTHER}
    for _tag, _ln, sent in corpus:
        for d in module.extract_definitions(sent):
            if d.term and d.head:
                per.setdefault(d.pattern, set()).add((d.term, d.head, d.pattern))
    return {p: sorted(v) for p, v in sorted(per.items())}


def _digest(pairs) -> str:
    h = hashlib.sha256()
    for p in pairs:
        h.update(("|".join(p) + "\n").encode("utf-8"))
    return h.hexdigest()


# ======================================================================== L1-L4 detector
# VERBATIM token sets from experiments/exp_definitional_predicate_v6.py.
_LEFT_FUNCTION_START = {
    "of", "in", "on", "for", "to", "with", "from", "into", "onto", "at", "as", "by", "between",
    "among", "through", "during", "within", "across", "over", "under", "and", "or", "but",
    "that", "which", "who", "whom", "whose", "where", "when", "while", "because", "if", "than",
    "such", "then", "also", "however", "therefore", "thus", "so",
}
_LEFT_FINITE_VERB = {"is", "are", "was", "were", "has", "have", "had", "does", "do", "did",
                     "can", "will", "would", "means", "becomes", "become", "includes",
                     "include", "consists", "consist", "occurs", "occur"}


def l1_l4_flags(module, sent: str, raw: str, raw_start: int, head: str) -> List[str]:
    """VERBATIM body of exp_definitional_predicate_v6.called_left_boundary_diagnostic's flag
    block. Only the (raw, raw_start) it is handed differs per arm."""
    flags: List[str] = []
    toks = TOK.findall(raw)
    if not toks:
        return flags
    if toks[0].lower() in _LEFT_FUNCTION_START:
        flags.append("L1_FUNCTION_WORD_START")
    if any(t.lower() in _LEFT_FINITE_VERB for t in toks):
        flags.append("L2_CROSSES_FINITE_VERB")
    pre = sent[:raw_start]
    pre_toks = TOK.findall(pre)
    if pre_toks and pre.rstrip().endswith(pre_toks[-1]) and not is_closed_class(
            lemma_word(pre_toks[-1])):
        flags.append("L3_TRUNCATED_MIDPHRASE")
    last_nominal = None
    for t in toks:
        lem = lemma_word(t)
        if not is_closed_class(lem) and module.is_nominal_lemma(lem):
            last_nominal = lem
    if last_nominal is not None and head != last_nominal:
        flags.append("L4_HEAD_NOT_ADJACENT")
    return flags


# ======================================================================== per-arm CALLED pass
def called_pass(module, corpus, patched: bool) -> dict:
    """One arm. Replays the module's OWN CALLED branch match-by-match (same order as
    `_extract_one`) so every match can be attributed: emitted / refused, with its span."""
    counts: Counter = Counter()
    refusals: Counter = Counter()
    mode_counts: Counter = Counter()
    l4_by_mode: Counter = Counter()
    n_facts = 0
    examples: Dict[str, List[dict]] = defaultdict(list)
    by_match: Dict[Tuple[str, int, int], dict] = {}
    for tag, lineno, sent in corpus:
        for m in module._RE_CALLED.finditer(sent):
            key = (tag, lineno, m.start())
            raw = m.group("dfs")
            dfs_text = module._strip_leading_coordinator(sent, raw, m.start("dfs"))
            if dfs_text is None:
                refusals["REFUSE_COORDINATE_LIST_ITEM_prev4"] += 1
                by_match[key] = {"emitted": False, "reason": "REFUSE_COORDINATE_LIST_ITEM_prev4",
                                 "sentence": sent, "provenance": "%s:%d" % (tag, lineno)}
                continue
            span, span_start, head_span, mode = dfs_text, m.start("dfs"), None, "PREPATCH"
            if patched:
                ant, reason = module._cb_called_antecedent_core(sent, m, dfs_text)
                if ant is None:
                    refusals[reason] += 1
                    by_match[key] = {"emitted": False, "reason": reason, "sentence": sent,
                                     "provenance": "%s:%d" % (tag, lineno),
                                     "raw_antecedent": raw}
                    continue
                span, span_start = ant.definiens, ant.start
                head_span, mode = ant.head_span, ant.mode
            d = module._mk(m.group("dfd"), span, "CALLED", sent, **(
                {"head_span": head_span} if patched else {}))
            if d is None:
                refusals["REFUSE_MK_REJECTED"] += 1
                by_match[key] = {"emitted": False, "reason": "REFUSE_MK_REJECTED",
                                 "sentence": sent, "provenance": "%s:%d" % (tag, lineno),
                                 "antecedent": span}
                continue
            n_facts += 1
            mode_counts[mode] += 1
            flags = l1_l4_flags(module, sent, span, span_start, d.head)
            for fl in flags:
                counts[fl] += 1
                if len(examples[fl]) < 8:
                    examples[fl].append({
                        "provenance": "%s:%d" % (tag, lineno), "sentence": sent,
                        "antecedent_captured": span, "mode": mode,
                        "banked_fact": "%s ISA %s" % (d.term, d.head)})
            if "L4_HEAD_NOT_ADJACENT" in flags:
                l4_by_mode[mode] += 1
            if any(f.startswith(("L1", "L2", "L3")) for f in flags):
                counts["ANY_WRONG_LEFT_BOUNDARY"] += 1
            else:
                counts["CLEAN_LEFT_BOUNDARY"] += 1
            by_match[key] = {"emitted": True, "reason": "OK", "sentence": sent,
                             "provenance": "%s:%d" % (tag, lineno), "antecedent": span,
                             "mode": mode, "term": d.term, "head": d.head,
                             "fact": "%s ISA %s" % (d.term, d.head),
                             "definiendum_surface": d.definiendum}
    n = max(1, n_facts)
    for k in ("L1_FUNCTION_WORD_START", "L2_CROSSES_FINITE_VERB", "L3_TRUNCATED_MIDPHRASE",
              "L4_HEAD_NOT_ADJACENT", "ANY_WRONG_LEFT_BOUNDARY", "CLEAN_LEFT_BOUNDARY"):
        counts.setdefault(k, 0)
    return {
        "n_called_facts_emitted": n_facts,
        "n_refusals": int(sum(refusals.values())),
        "refusals_by_reason": dict(sorted(refusals.items())),
        "counts": dict(sorted(counts.items())),
        "rate_any_wrong_left_boundary": round(counts["ANY_WRONG_LEFT_BOUNDARY"] / n, 4),
        "rate_L4_head_not_adjacent": round(counts["L4_HEAD_NOT_ADJACENT"] / n, 4),
        "antecedent_mode_mix": dict(sorted(mode_counts.items())),
        "residual_L4_by_mode": dict(sorted(l4_by_mode.items())),
        "examples": {k: v[:5] for k, v in sorted(examples.items())},
        "_by_match": by_match,
    }


# ======================================================================== fact rows for sampling
def called_fact_rows(module, corpus, patched: bool) -> List[dict]:
    """One row per DISTINCT (term, head) CALLED fact, with provenance + source sentences."""
    by_key: Dict[Tuple[str, str], dict] = {}
    for tag, lineno, sent in corpus:
        for d in module.extract_definitions(sent):
            if d.pattern != "CALLED" or not d.term or not d.head:
                continue
            key = (d.term, d.head)
            row = by_key.get(key)
            if row is None:
                by_key[key] = {
                    "subject": d.term, "relation": "GROUNDED_MEANING", "object": d.head,
                    "subject_type": d.term_type, "subject_head_lemma": d.definiendum_lemma,
                    "pattern": "CALLED", "n_attestations": 1,
                    "definiendum_surface": d.definiendum, "definiens_surface": d.definiens,
                    "source_sentences": [sent], "provenance": ["%s:%d" % (tag, lineno)],
                }
            else:
                row["n_attestations"] += 1
                if (len(row["source_sentences"]) < MAX_SOURCE_SENTENCES
                        and sent not in row["source_sentences"]):
                    row["source_sentences"].append(sent)
                    row["provenance"].append("%s:%d" % (tag, lineno))
    rows = [by_key[k] for k in sorted(by_key)]
    for i, r in enumerate(rows):
        r["fid"] = i
    return rows


def sample_for_audit(facts: List[dict], k: int = SAMPLE_N, seed: int = SAMPLE_SEED) -> List[dict]:
    """IDENTICAL convention to the v5 B3 / v6 predicate audits: random.Random(seed).sample over
    facts in fid (= insertion) order, then sorted."""
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(facts)), min(k, len(facts))))
    return [facts[i] for i in idx]


def _selftest_sampling() -> dict:
    """Cross-check the sampler against the v5 sample ON DISK (same seed, same n, same order)."""
    if not os.path.exists(V5_SAMPLE):
        return {"checked": False, "why": "v5 sample not on disk"}
    v5 = json.load(io.open(V5_SAMPLE, encoding="utf-8"))
    rows, n_arm = v5["rows"], v5["n_facts_in_arm"]
    got = sorted(random.Random(v5["sample_seed"]).sample(range(n_arm), len(rows)))
    return {"checked": True, "reproduces_v5_fid_list": got == [r["fid"] for r in rows],
            "n": len(rows), "seed": v5["sample_seed"]}


# ======================================================================== main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    run_mode = "smoke" if args.smoke else "full"
    out_dir = OUT_DIR + ("_smoke" if args.smoke else "")
    _write_start_marker(out_dir, run_mode)
    t0 = time.time()

    corpus = load_corpus(limit=6000 if args.smoke else None)
    per_file = Counter(tag for tag, _l, _s in corpus)
    print("[corpus] %d sentences %s" % (len(corpus), dict(sorted(per_file.items()))))

    pre = load_prepatch_module()

    # ---- arms ----------------------------------------------------------------------------
    arms = {}
    fact_sets = {}
    print("[arm] BASELINE (pre-patch byte copy)")
    fact_sets["BASELINE"] = pattern_fact_sets(pre, corpus)
    arms["BASELINE"] = called_pass(pre, corpus, patched=False)

    for name, (fl, fh) in (("A_OFF_B_OFF", (False, False)),
                           ("A_ONLY", (True, False)),
                           ("B_ONLY", (False, True)),
                           ("A_PLUS_B", (True, True))):
        DE.CALLED_FIX_LEFT, DE.CALLED_FIX_HEAD = fl, fh
        print("[arm] %s (CALLED_FIX_LEFT=%s CALLED_FIX_HEAD=%s)" % (name, fl, fh))
        fact_sets[name] = pattern_fact_sets(DE, corpus)
        arms[name] = called_pass(DE, corpus, patched=True)
    DE.CALLED_FIX_LEFT, DE.CALLED_FIX_HEAD = True, True     # restore shipped defaults

    # ---- regression proof on the OTHER FOUR patterns --------------------------------------
    other_hashes = {arm: {p: _digest(fs[p]) for p in PATTERNS_OTHER}
                    for arm, fs in sorted(fact_sets.items())}
    other_counts = {arm: {p: len(fs[p]) for p in PATTERNS_OTHER}
                    for arm, fs in sorted(fact_sets.items())}
    churn_neutral = other_hashes["BASELINE"] == other_hashes["A_OFF_B_OFF"]
    other_unchanged = {p: other_hashes["BASELINE"][p] == other_hashes["A_PLUS_B"][p]
                       for p in PATTERNS_OTHER}
    called_differs = _digest(fact_sets["BASELINE"]["CALLED"]) != _digest(
        fact_sets["A_PLUS_B"]["CALLED"])

    # ---- paired before/after --------------------------------------------------------------
    base_m, new_m = arms["BASELINE"]["_by_match"], arms["A_PLUS_B"]["_by_match"]
    disagreements = []
    for key in sorted(set(base_m) | set(new_m)):
        b, a = base_m.get(key), new_m.get(key)
        bf = b.get("fact") if b and b.get("emitted") else None
        af = a.get("fact") if a and a.get("emitted") else None
        if bf == af:
            continue
        src = b or a
        disagreements.append({
            "provenance": src["provenance"], "sentence": src["sentence"],
            "BEFORE_antecedent": (b or {}).get("antecedent") or (b or {}).get("raw_antecedent"),
            "BEFORE_fact": bf, "BEFORE_reason": (b or {}).get("reason"),
            "AFTER_antecedent": (a or {}).get("antecedent") or (a or {}).get("raw_antecedent"),
            "AFTER_fact": af, "AFTER_reason": (a or {}).get("reason"),
            "AFTER_mode": (a or {}).get("mode"),
        })
    paired = [disagreements[i] for i in sorted(
        random.Random(SAMPLE_SEED).sample(range(len(disagreements)),
                                          min(PAIRED_N, len(disagreements))))]

    # ---- blind hand-score sample on the SHIPPED arm ----------------------------------------
    rows_new = called_fact_rows(DE, corpus, patched=True)
    sample = sample_for_audit(rows_new)
    _atomic_write_json(os.path.join(out_dir, "called_audit_sample.json"), {
        "arm": "CALLED_V7_A_PLUS_B", "n_facts_in_arm": len(rows_new), "sample_seed": SAMPLE_SEED,
        "sampling": "random.Random(42).sample over fid order -- SAME convention as "
                    "data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json, verified "
                    "against that file's own fid list on disk in _selftest_sampling()",
        "rubric": "DIRECTOR'S BLIND JUDGEMENT. Each row carries the SOURCE SENTENCE and its "
                  "[FILE:line] provenance beside the extracted fact. No buckets pre-assigned.",
        "scored": False,
        "note": "UNSCORED AND UNBANKED. GROWTH IS PAUSED: nothing here is written to "
                "data/foundation/**. The comparable prior number (v5 64% MEANINGFUL) is over "
                "ALL FIVE patterns, not CALLED alone, so it is NOT a like-for-like baseline.",
        "rows": sample})
    _atomic_write_json(os.path.join(out_dir, "called_paired_before_after.json"), {
        "arm_before": "BASELINE_PREPATCH", "arm_after": "CALLED_V7_A_PLUS_B",
        "n_disagreeing_matches": len(disagreements), "sample_seed": SAMPLE_SEED,
        "sampling": "random.Random(42).sample over the sorted disagreement list",
        "scored": False,
        "note": "Every row is a CALLED match where the pre-patch and patched pipelines produce "
                "DIFFERENT output (including one side emitting nothing). UNSCORED.",
        "rows": paired})
    with io.open(os.path.join(out_dir, "called_facts_v7.jsonl"), "w",
                 encoding="utf-8", newline="") as f:
        for r in rows_new:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")

    for a in arms.values():
        a.pop("_by_match", None)

    def brief(name):
        c = arms[name]["counts"]
        return {"n_called_facts": arms[name]["n_called_facts_emitted"],
                "n_refusals": arms[name]["n_refusals"],
                "L1": c["L1_FUNCTION_WORD_START"], "L2": c["L2_CROSSES_FINITE_VERB"],
                "L3": c["L3_TRUNCATED_MIDPHRASE"], "L4": c["L4_HEAD_NOT_ADJACENT"],
                "ANY_WRONG_LEFT_BOUNDARY": c["ANY_WRONG_LEFT_BOUNDARY"]}

    ok = churn_neutral and all(other_unchanged.values()) and called_differs
    metrics = {
        "verdict": "STRUCTURAL_PASS_PENDING_HANDSCORE" if ok else "HARD_FAIL_REGRESSION",
        "verdict_msg": ("CALLED %d -> %d facts; ANY_WRONG_LEFT_BOUNDARY %d -> %d; L4 %d -> %d; "
                        "%d refusals; other 4 patterns byte-identical=%s"
                        % (arms["BASELINE"]["n_called_facts_emitted"],
                           arms["A_PLUS_B"]["n_called_facts_emitted"],
                           arms["BASELINE"]["counts"]["ANY_WRONG_LEFT_BOUNDARY"],
                           arms["A_PLUS_B"]["counts"]["ANY_WRONG_LEFT_BOUNDARY"],
                           arms["BASELINE"]["counts"]["L4_HEAD_NOT_ADJACENT"],
                           arms["A_PLUS_B"]["counts"]["L4_HEAD_NOT_ADJACENT"],
                           arms["A_PLUS_B"]["n_refusals"], all(other_unchanged.values()))),
        "summary": "CALLED antecedent left-boundary (A) and head-selection (B) fix, measured "
                   "separately",
        "elapsed_s": round(time.time() - t0, 2),
        "run_mode": run_mode,
        "headline": {k: brief(k) for k in ("BASELINE", "A_OFF_B_OFF", "A_ONLY", "B_ONLY",
                                           "A_PLUS_B")},
        "arms": arms,
        "other_pattern_hashes": other_hashes,
        "other_pattern_counts": other_counts,
        "other_patterns_unchanged_BASELINE_vs_A_PLUS_B": other_unchanged,
        "concurrent_edit_churn_neutral_BASELINE_vs_A_OFF_B_OFF": churn_neutral,
        "called_set_differs_BASELINE_vs_A_PLUS_B": called_differs,
        "n_disagreeing_matches": len(disagreements),
        "prepatch_module_sha256": _sha256_file(BASELINE_MODULE),
        "postpatch_module_sha256": _sha256_file(
            os.path.join(REPO_ROOT, "hdlab", "definitional_extraction.py")),
        "corpus_files": [p for _t, p in CORPUS_FILES],
        "corpus_sentences": len(corpus),
        "corpus_sentences_per_file": dict(sorted(per_file.items())),
        "mcguffey_excluded": True,
        "detector_provenance": "L1-L4 flag block copied VERBATIM from "
                               "experiments/exp_definitional_predicate_v6.py::"
                               "called_left_boundary_diagnostic. Same token sets, same tests. "
                               "Per arm it is handed the span that arm actually uses; for "
                               "BASELINE that is m.group('dfs') exactly as in v6.",
        "detector_caveats": {
            "L1_L2_zero_by_construction_when_A_on": True,
            "L3_upper_bound": "fires on any open-class token abutting a correctly-bounded NP",
            "L4_wrong_ruler_for_copula_antecedents": "see residual_L4_by_mode per arm",
        },
        "sampling_selftest": _selftest_sampling(),
        "audit_sample_path": os.path.join(out_dir, "called_audit_sample.json"),
        "paired_sample_path": os.path.join(out_dir, "called_paired_before_after.json"),
        "called_facts_path": os.path.join(out_dir, "called_facts_v7.jsonl"),
        "quality_scored_here": False,
        "banked": False,
        "wire_status": "UNBANKED_PENDING_DIRECTOR_HANDSCORE",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_json(os.path.join(out_dir, "metrics.json"), metrics)
    print(json.dumps({k: metrics[k] for k in (
        "verdict", "verdict_msg", "headline", "other_patterns_unchanged_BASELINE_vs_A_PLUS_B",
        "concurrent_edit_churn_neutral_BASELINE_vs_A_OFF_B_OFF", "n_disagreeing_matches",
        "corpus_sentences", "sampling_selftest")}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:                                          # noqa: BLE001
        _write_crash_metrics(OUT_DIR, exc)
        traceback.print_exc()
        sys.exit(1)
