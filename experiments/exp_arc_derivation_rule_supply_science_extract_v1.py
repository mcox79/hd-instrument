"""arc_derivation_rule_supply_science_extract_v1 -- ONE-VARIABLE ablation of the derivation
connectivity gate where the SINGLE variable is the RULE SOURCE, and the source is SCIENCE-PRECISE
TYPED extraction from already-ingested science text (ARC_Corpus.txt, ~14.6M sentences) + WorldTree.

WHY (VET-confirmed lineage): the clean-node gate (cleannodes_v2, 99736f579) confirmed WorldTree's
~1868 licensed rows do NOT span ARC-Challenge content (typed correct-coverage ~0.06,
COVERAGE_BOUND_CONFIRMED). The CSKG rule-supply probe (rule_supply_cskg_v1) SETTLED that a generic
off-the-shelf commonsense KB is the WRONG supply: hub-present -> non-discriminative vacuous bridges;
hub-removed -> coverage collapses; no cap threads coverage+selectivity (atoms 29553-29554). The
diagnosed need (atom 29554) is SCIENCE-PRECISE extraction: typed causal/conditional/functional rules
mined from SCIENCE text specifically, in the content domains ARC-Challenge probes. This cell does that
extraction and RE-RUNS THE SAME connectivity/coverage gate with the expanded LICENSED rule table.

This is NOT a repeat of the CSKG probe: (a) source = science-domain text extraction, not a generic
commonsense graph; (b) patterns are calibrated against WorldTree's own typed rows (IFTHEN / CAUSE /
COUPLEDRELATIONSHIP / REQUIRES / USEDFOR / SOURCEOF); (c) precision is measured (spot-check sample).

ONE VARIABLE = RULE SOURCE. EVERYTHING ELSE reused UNCHANGED, imported from the CSKG rule-supply cell
(rs = exp_arc_derivation_rule_supply_cskg_v1), which itself imports the clean-node gate cn and gate:
  - SAME node-identity: cn.NegAwareEncoder + head-lemma gate + PolarityLexicon.contradicts merge-gate
  - SAME graph builder cn.build_graph_gated (typed directed edges + untyped-null cos edges)
  - SAME depth<=3 meet-in-middle search gate.meet_connected, SAME per-source eval rs.eval_source
  - SAME query-conditioned subgraph induction rs.induce_subgraph (generous upper-bound, as for CSKG)
  - SAME ~100 ARC-Challenge Qs (same seed permutation), SAME word->node mapping (cos>=tau_unify)
  - SAME thresholds tau_unify=0.85, tau_sim=0.60, depth=3 (NOT tuned to force a band)
  - SAME per-source band classifier rs.classify_source_band (a priori GREEN/PROMISCUOUS/STARVED/MIDDLE)

RULE SOURCES (the ONE variable), each fed to the IDENTICAL gate:
  1. worldtree         : WorldTree licensed rows (LICENSED, confident, non-empty). The ANCHOR baseline
                         reproduced under identical conditions (positive control, expected ~0.06 cov).
  2. science_extract   : typed rules extracted from ARC_Corpus.txt via calibrated seed patterns, then
                         ARC-vocab-filtered at extraction time and query-conditioned induced to the
                         FILLER_BUDGET around the sampled ARC vocab (SAME induction as CSKG = generous).
  3. worldtree_science : union of (1) and (2). The "supply everything typed we can extract" arm.

SCIENCE EXTRACTION PATTERNS (calibrated against WorldTree typed rows; higher-precision preferred):
  CAUSE (arg0 causes arg1):
    forward split connectives : " causes ", " causing ", " produces ", " producing ",
                                " results in ", " resulting in ", " leads to ", " lead to ", " leading to "
    reversed split connectives (effect LEFT, cause RIGHT; checked BEFORE forward so "caused by" is not
                                mis-split by "cause"): " caused by ", " produced by ", " results from ",
                                " resulting from ", " arises from ", " arise from "
    "because" clause          : "EFFECT because CAUSE" -> arg0=CAUSE, arg1=EFFECT
  IFTHEN (arg0 condition -> arg1 consequent):
    "if X then Y" (high precision) ; "if X , Y" ; "when X , Y" (lower precision, still conditional-ish)
  COUPLEDRELATIONSHIP (arg0 co-varies with arg1):
    "as X <dir>, Y <dir>" ; "the <more/higher/...> X, the <more/higher/...> Y"
  REQUIRES (arg0 requires arg1): " requires ", " require ", " needs ", " need ", " depends on ", " depend on "
  USEDFOR (arg0 used for arg1): " is used for ", " are used for ", " is used to ", " are used to ", " used for ", " used to "
  SOURCEOF (arg0 source of arg1): " is a source of ", " is the source of ", " are a source of ", " is a major source of "

ARGUMENT CLEANING (precision guard): each side windowed to the tokens local to the connective (LEFT arg
= last <=ARG_MAX_TOK tokens; RIGHT arg = first <=ARG_MAX_TOK tokens), outer stopwords stripped, must have
>=1 content word (arc._content_words nonempty) and <=ARG_MAX_TOK tokens; args must differ; whole-line
must not look like a citation/markup fragment. ARC-vocab keep: >=1 endpoint shares a >=4-char content
token with the sampled ARC givens+choices vocab (query-conditioned, same seed criterion as CSKG).

METRICS + PRE-REGISTERED BANDS (a priori, per source; reported STRAIGHT, NOT tuned). Per source:
  correct-choice coverage (cov), typed selectivity gap (cov - mean-wrong-coverage), the SAME source's
  untyped-null coverage+gap (promiscuity control), graph size + max node degree.
  Per-source band (rs.classify_source_band, IDENTICAL thresholds to the CSKG probe):
    GREEN            : cov >= 0.35 AND typed_gap >= 0.15 AND typed_gap > untyped_gap  (== the plan's GREEN:
                       unblocks Step 2 reasoner)
    PROMISCUOUS_FAIL : cov > 0.50 AND (typed_gap < 0.05 OR typed_gap <= untyped_gap)  (== the plan's
                       PROMISCUOUS: coverage rose but selectivity ~ untyped-null -> extraction too noisy)
    STILL_STARVED    : cov < 0.15  (== the plan's RED: extraction recall/quality is the bottleneck ->
                       redirect to a broader source CK-12/OpenStax before further reasoner investment)
    MIDDLE_BAND      : otherwise (partial coverage/selectivity) -> report straight, no claim
  A `plan_light` field maps these to the plan's GREEN/PROMISCUOUS/RED/MIDDLE names explicitly.
  HONEST GUARD: coverage AND selectivity reported TOGETHER; a coverage win with zero selectivity is NOT a
    win. PRECISION: a deterministic stratified sample of the FINAL induced science rules (with source
    sentence) is written to metrics for spot-check; an automatic well-formedness proxy is also reported
    (NOT a substitute for the read precision). do NOT tune to force GREEN.

POSITIVE CONTROL (Gate D): worldtree arm MUST reproduce ~0.06 typed coverage (matched regime) -> proves
the harness is wired identically to the parent; a large deviation flags an invocation mismatch.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic
(fixed seed, numpy default_rng, sorted iteration, reservoir with seeded rng); repo .venv. VET-PENDING.

CELL-TEMPLATE:
  - except SystemExit raised BEFORE except Exception (no bare/BaseException).
  - final metrics atomicity = tmp + os.replace ; start-marker ; crash-diagnostic ; heartbeat with flush.
  - real_code_path self_test: (i) each extraction pattern fires on a planted science sentence with the
    RIGHT type + direction, and rejects a citation/markup fragment; (ii) reversed "caused by" splits with
    flipped direction; (iii) a planted extracted chain CONNECTS the correct choice while a lure does NOT
    under the REAL gate (cn.build_graph_gated + gate.meet_connected) = discriminator CAN fire + CAN fail;
    (iv) band classifier reachability (reuses rs.classify_source_band); (v) induction keeps a planted
    ARC-relevant chain (reuses rs.induce_subgraph).
  - deterministic_seeding: fixed int seed + numpy default_rng + sorted iteration; no hash()-seeding.
  - all reported numbers MEASURED @ this cell's metrics.json.

Compute architecture: sequential-CPU (JUSTIFIED). One streaming scan of ARC_Corpus.txt (~14.6M lines)
with a cheap substring PREFILTER so the expensive per-pattern work runs only on candidate lines; then the
SAME cheap gate (graph build + BFS over ~100 Qs) per source. The only vectorized cost is the GloVe encode
of the fillers + the O(U^2) cosine merge, bounded by FILLER_BUDGET. No matmul-heavy substrate primitive is
swept -> not a GPU-batching candidate. Storage: no_storage (connectivity gate; no atoms written).
"""
from __future__ import annotations

import os
import re
import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# reuse the whole gate harness UNCHANGED (ONE variable = rule source)
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as cn
from experiments import exp_arc_derivation_rule_supply_cskg_v1 as rs
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc

ANCHOR_NAME = "arc_derivation_rule_supply_science_extract_v1"
SEED = 20260725

# SAME thresholds + node-identity + induction as the CSKG rule-supply gate (ONE variable = rule source)
TAU_UNIFY = cn.TAU_UNIFY   # 0.85
TAU_SIM = cn.TAU_SIM       # 0.60
DEPTH = cn.DEPTH           # 3
FILLER_BUDGET = rs.FILLER_BUDGET          # 6000
CSKG_MAX_DEG_INDUCE = rs.CSKG_MAX_DEG_INDUCE  # 64

CORPUS_PATH = os.path.join(_REPO, "data", "corpora", "arc", "ARC-V1-Feb2018-2", "ARC_Corpus.txt")

# extraction bounds (precision guards)
ARG_MAX_TOK = 6            # each argument windowed to <= this many tokens local to the connective
ARG_MIN_TOK = 1
KEEP_CAP = 500000          # hard cap on ARC-vocab-filtered extracted rules held in memory (full scan)
PROV_SAMPLE_TARGET = 90    # provenance sample size for precision spot-check (stratified by relation)

# outer stopwords stripped from argument phrase edges (determiners/aux/pronouns/conjunctions/preps)
_ARG_STOP = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "he", "she", "we", "you", "i", "his", "her", "our", "your", "my", "to", "of", "in", "on",
    "for", "and", "or", "but", "will", "can", "may", "might", "must", "should", "would", "could",
    "is", "are", "was", "were", "be", "being", "been", "am", "so", "also", "then", "as", "at",
    "by", "with", "from", "into", "onto", "up", "out", "which", "who", "when", "then", "there",
    "here", "some", "any", "all", "each", "both", "more", "most", "such", "very", "just", "not",
})

# citation/markup fragment guard (drop lines that look like references or wiki markup)
_JUNK_RE = re.compile(r"(-LSB-|-RSB-|-LRB-|-RRB-|\[\s*edit\s*\]|http|www\.|doi:|\bpp?\.\s|vol\.|:\s*\d+-\d+|"
                      r"\d{4}\)|isbn|retrieved)", re.IGNORECASE)

_T0 = [time.perf_counter()]


# ---------------------------------------------------------------------------
# atomic metrics / heartbeat / crash diag / start-marker
# ---------------------------------------------------------------------------
def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# argument cleaning (precision guard)
# ---------------------------------------------------------------------------
def _clean_side(text, take_last):
    """Window a raw argument side to <= ARG_MAX_TOK tokens local to the connective, strip outer
    stopwords, return a normalized phrase string or None if it has no content word / is degenerate."""
    toks = [t for t in re.split(r"\s+", text.strip().lower()) if t]
    if not toks:
        return None
    # keep only alnum/hyphen tokens (drop stray punctuation tokens)
    toks = [re.sub(r"[^a-z0-9\-]", "", t) for t in toks]
    toks = [t for t in toks if t]
    if not toks:
        return None
    window = toks[-ARG_MAX_TOK:] if take_last else toks[:ARG_MAX_TOK]
    # strip outer stopwords
    lo, hi = 0, len(window)
    while lo < hi and window[lo] in _ARG_STOP:
        lo += 1
    while hi > lo and window[hi - 1] in _ARG_STOP:
        hi -= 1
    window = window[lo:hi]
    if not window or len(window) > ARG_MAX_TOK:
        return None
    phrase = " ".join(window)
    if not arc._content_words(phrase, min_len=3):
        return None
    return phrase


def _mk(rel, left_raw, right_raw, arg0_is_left=True):
    """Build a (rel, arg0, arg1) tuple from raw left/right sides. arg0_is_left selects direction.
    LEFT side windows to its LAST tokens (head near connective); RIGHT windows to its FIRST tokens."""
    left = _clean_side(left_raw, take_last=True)
    right = _clean_side(right_raw, take_last=False)
    if left is None or right is None or left == right:
        return None
    if arg0_is_left:
        return (rel, left, right)
    return (rel, right, left)


# ---------------------------------------------------------------------------
# per-sentence typed extraction (precision-first)
# ---------------------------------------------------------------------------
# split connectives: (needle, relation, arg0_is_left). Reversed-causal listed FIRST so "caused by" wins
# over "cause". Order within a relation matters only for first-match.
_SPLIT_CAUSE_REV = [" caused by ", " produced by ", " results from ", " resulting from ",
                    " arises from ", " arise from ", " arising from "]
_SPLIT_CAUSE_FWD = [" causes ", " causing ", " produces ", " producing ",
                    " results in ", " resulting in ", " leads to ", " lead to ", " leading to "]
_SPLIT_REQUIRES = [" requires ", " require ", " needs ", " need ", " depends on ", " depend on "]
_SPLIT_USEDFOR = [" is used for ", " are used for ", " is used to ", " are used to ",
                  " used for ", " used to "]
_SPLIT_SOURCEOF = [" is a source of ", " is the source of ", " are a source of ",
                   " are sources of ", " is a major source of "]

_RE_IF_THEN = re.compile(r"\bif\s+(.+?)\s+then\s+(.+)")
_RE_IF_COMMA = re.compile(r"\bif\s+(.+?),\s+(.+)")
_RE_WHEN_COMMA = re.compile(r"\bwhen\s+(.+?),\s+(.+)")
_COUPLED_DIR = r"(?:increase|increases|increased|increasing|decrease|decreases|decreased|decreasing|" \
               r"rise|rises|rising|rose|fall|falls|falling|fell|grow|grows|growing|grew|" \
               r"drop|drops|dropping|warm|warms|warming|cool|cools|cooling|lower|lowers|raise|raises)"
_RE_AS_COUPLED = re.compile(r"\bas\s+(.+?)\s+" + _COUPLED_DIR + r"s?\b[,]?\s+(.+?)\s+(?:will\s+)?"
                            + _COUPLED_DIR + r"\b")
_RE_MORE_COUPLED = re.compile(r"\bthe\s+(?:more|higher|greater|larger|lower|less|smaller|faster|slower|"
                              r"hotter|colder|warmer|cooler)\s+(.+?),\s+the\s+"
                              r"(?:more|higher|greater|larger|lower|less|smaller|faster|slower|hotter|"
                              r"colder|warmer|cooler)\s+(.+)")

# fast substring prefilter: run the expensive extraction only on lines containing one of these
_PREFILTER = (" caus", " produc", "results ", "result ", " lead", "if ", "when ", " as ", " requir",
              " need", " depend", " used ", "source of", "because", " the more ", " the higher ",
              " the greater ", " the lower ")


def extract_from_sentence(sent_lower):
    """Return a list of (rel, arg0, arg1) tuples extracted from ONE lowercased sentence. Precision-first;
    at most a few per sentence. Direction encoded in tuple order (arg0 -> arg1)."""
    out = []
    s = sent_lower

    # ---- CAUSE (reversed FIRST, then forward, then because) ----
    matched_cause = False
    for needle in _SPLIT_CAUSE_REV:
        i = s.find(needle)
        if i > 0:
            t = _mk("CAUSE", s[:i], s[i + len(needle):], arg0_is_left=False)  # left=effect, right=cause
            if t:
                out.append(t); matched_cause = True
            break
    if not matched_cause:
        for needle in _SPLIT_CAUSE_FWD:
            i = s.find(needle)
            if i > 0:
                t = _mk("CAUSE", s[:i], s[i + len(needle):], arg0_is_left=True)
                if t:
                    out.append(t); matched_cause = True
                break
    if not matched_cause:
        i = s.find(" because ")
        if i > 0:
            # "EFFECT because CAUSE" -> arg0=CAUSE(right), arg1=EFFECT(left)
            t = _mk("CAUSE", s[:i], s[i + len(" because "):], arg0_is_left=False)
            if t:
                out.append(t)

    # ---- REQUIRES ----
    for needle in _SPLIT_REQUIRES:
        i = s.find(needle)
        if i > 0:
            t = _mk("REQUIRES", s[:i], s[i + len(needle):], arg0_is_left=True)
            if t:
                out.append(t)
            break

    # ---- USEDFOR ----
    for needle in _SPLIT_USEDFOR:
        i = s.find(needle)
        if i > 0:
            t = _mk("USEDFOR", s[:i], s[i + len(needle):], arg0_is_left=True)
            if t:
                out.append(t)
            break

    # ---- SOURCEOF ----
    for needle in _SPLIT_SOURCEOF:
        i = s.find(needle)
        if i > 0:
            t = _mk("SOURCEOF", s[:i], s[i + len(needle):], arg0_is_left=True)
            if t:
                out.append(t)
            break

    # ---- IFTHEN (if-then highest precision; then if-comma; then when-comma) ----
    m = _RE_IF_THEN.search(s)
    if m:
        t = _mk("IFTHEN", m.group(1), m.group(2), arg0_is_left=True)
        if t:
            out.append(t)
    else:
        m = _RE_IF_COMMA.search(s)
        if m:
            t = _mk("IFTHEN", m.group(1), m.group(2), arg0_is_left=True)
            if t:
                out.append(t)
        else:
            m = _RE_WHEN_COMMA.search(s)
            if m:
                t = _mk("IFTHEN", m.group(1), m.group(2), arg0_is_left=True)
                if t:
                    out.append(t)

    # ---- COUPLEDRELATIONSHIP ----
    m = _RE_AS_COUPLED.search(s)
    if m:
        t = _mk("COUPLEDRELATIONSHIP", m.group(1), m.group(2), arg0_is_left=True)
        if t:
            out.append(t)
    m = _RE_MORE_COUPLED.search(s)
    if m:
        t = _mk("COUPLEDRELATIONSHIP", m.group(1), m.group(2), arg0_is_left=True)
        if t:
            out.append(t)

    return out


def extract_science_rules(corpus_path, seed_words, max_lines, output_dir, seed):
    """Stream ARC_Corpus.txt; extract typed rules; keep those whose >=1 endpoint shares a >=4-char
    content token with the ARC seed vocab (query-conditioned, same as CSKG). Dedup. Returns
    (rows_tuples, prov, per_rel, stats). prov maps (rel,a,b)->source-sentence (for the precision sample)."""
    seed_words = set(seed_words)
    seen = set()
    rows = []
    prov = {}
    per_rel = {}
    n_lines = 0
    n_prefilter_pass = 0
    n_raw_extracted = 0
    n_kept = 0
    t_scan0 = time.perf_counter()

    def touches_seed(a, b):
        for lab in (a, b):
            for w in arc._content_words(lab, min_len=4):
                if w in seed_words:
                    return True
        return False

    with open(corpus_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            n_lines += 1
            if max_lines and n_lines > max_lines:
                break
            if n_lines % 2000000 == 0:
                rate = n_lines / max(1e-6, time.perf_counter() - t_scan0)
                _heartbeat(output_dir, "scan_progress",
                           {"n_lines": n_lines, "n_kept": n_kept, "lines_per_s": int(rate)})
                if len(rows) >= KEEP_CAP:
                    break
            low = line.lower()
            hit = False
            for k in _PREFILTER:
                if k in low:
                    hit = True
                    break
            if not hit:
                continue
            n_prefilter_pass += 1
            if _JUNK_RE.search(low):
                continue
            # bound sentence length for regex safety
            sent = low.strip()
            if len(sent) > 400:
                sent = sent[:400]
            tuples = extract_from_sentence(sent)
            for t in tuples:
                n_raw_extracted += 1
                rel, a, b = t
                if not touches_seed(a, b):
                    continue
                if t in seen:
                    continue
                seen.add(t)
                rows.append(t)
                prov[t] = sent[:220]
                per_rel[rel] = per_rel.get(rel, 0) + 1
                n_kept += 1
                if n_kept >= KEEP_CAP:
                    break
            if n_kept >= KEEP_CAP:
                break

    stats = {
        "n_lines_scanned": n_lines, "n_prefilter_pass": n_prefilter_pass,
        "n_raw_extracted": n_raw_extracted, "n_kept_arc_filtered": n_kept,
        "scan_s": round(time.perf_counter() - t_scan0, 1), "keep_cap_hit": n_kept >= KEEP_CAP,
        "per_relation": per_rel,
    }
    return rows, prov, per_rel, stats


def _wellformed_proxy(rel, a, b):
    """Cheap automatic well-formedness proxy (NOT true precision): both args have a content word, args
    differ, neither arg is a single stopword-ish token, and (for COUPLED) both are >=1 content token."""
    ca = arc._content_words(a, min_len=3)
    cb = arc._content_words(b, min_len=3)
    if not ca or not cb:
        return False
    if a == b:
        return False
    if len(a) <= 2 or len(b) <= 2:
        return False
    return True


def _precision_sample(rows, prov, target, seed):
    """Deterministic stratified sample of induced science rows (with source sentence) for spot-check.
    Stratify by relation so every relation type is represented. Returns list of dicts + proxy stats."""
    by_rel = {}
    for r in rows:
        by_rel.setdefault(r["relation"], []).append(r)
    rels = sorted(by_rel)
    rng = np.random.default_rng(seed * 31 + 7)
    per = max(1, target // max(1, len(rels)))
    sample = []
    for rel in rels:
        pool = sorted(by_rel[rel], key=lambda r: (r["arg0"], r["arg1"]))
        k = min(per, len(pool))
        idx = rng.permutation(len(pool))[:k]
        for i in sorted(idx.tolist()):
            r = pool[i]
            key = (r["relation"], r["arg0"], r["arg1"])
            sample.append({"relation": r["relation"], "arg0": r["arg0"], "arg1": r["arg1"],
                           "source_sentence": prov.get(key, ""),
                           "wellformed_proxy": bool(_wellformed_proxy(r["relation"], r["arg0"], r["arg1"]))})
    n_wf = sum(1 for s in sample if s["wellformed_proxy"])
    proxy = {"n_sampled": len(sample), "n_wellformed_proxy": n_wf,
             "wellformed_proxy_frac": round(n_wf / len(sample), 4) if sample else 0.0,
             "note": "wellformed_proxy is a cheap AUTOMATIC lower-bar (args have content words, differ); "
                     "it is NOT true precision -- true precision = the agent's read of source_sentence."}
    return sample, proxy


# ---------------------------------------------------------------------------
# plan-band mapping (rs.classify_source_band -> the plan's GREEN/PROMISCUOUS/RED/MIDDLE names)
# ---------------------------------------------------------------------------
def plan_light(band):
    return {"GREEN": "GREEN", "PROMISCUOUS_FAIL": "PROMISCUOUS", "STILL_STARVED": "RED",
            "MIDDLE_BAND": "MIDDLE"}.get(band, band)


# ---------------------------------------------------------------------------
# self-test (REAL code paths: extraction patterns + REAL gate discriminator + induction + bands)
# ---------------------------------------------------------------------------
def _self_test():
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    print("[self-test] extraction patterns (type + direction) ...", flush=True)

    def has(tuples, rel, a_sub, b_sub):
        return any(t[0] == rel and a_sub in t[1] and b_sub in t[2] for t in tuples)

    # CAUSE forward
    t = extract_from_sentence("friction between two surfaces causes an increase in temperature")
    assert has(t, "CAUSE", "friction", "temperature") or has(t, "CAUSE", "surfaces", "temperature"), t
    # CAUSE reversed ("caused by": effect left, cause right) -> arg0=cause, arg1=effect
    t = extract_from_sentence("soil erosion is caused by moving water")
    assert has(t, "CAUSE", "water", "erosion") or has(t, "CAUSE", "water", "soil erosion"), t
    # CAUSE because ("effect because cause") -> arg0=cause, arg1=effect
    t = extract_from_sentence("the ice melts because the temperature rises")
    assert has(t, "CAUSE", "temperature", "melt") or has(t, "CAUSE", "temperature rises", "ice melt"), t
    # results in (forward)
    t = extract_from_sentence("heating a solid results in a change of state")
    assert has(t, "CAUSE", "solid", "change") or has(t, "CAUSE", "heating solid", "state"), t
    # IFTHEN
    t = extract_from_sentence("if an object is heated then its temperature will increase")
    assert has(t, "IFTHEN", "heated", "temperature"), t
    # WHEN-comma -> IFTHEN
    t = extract_from_sentence("when water freezes, it expands and becomes ice")
    assert any(x[0] == "IFTHEN" for x in t), t
    # COUPLEDRELATIONSHIP as-frame
    t = extract_from_sentence("as the roughness of a surface increases, the friction increases")
    assert any(x[0] == "COUPLEDRELATIONSHIP" for x in t), t
    # REQUIRES
    t = extract_from_sentence("photosynthesis requires sunlight and carbon dioxide")
    assert any(x[0] == "REQUIRES" for x in t), t
    # USEDFOR
    t = extract_from_sentence("a thermometer is used to measure temperature")
    assert any(x[0] == "USEDFOR" for x in t), t
    # SOURCEOF
    t = extract_from_sentence("the sun is a source of light and heat energy")
    assert any(x[0] == "SOURCEOF" for x in t), t
    print(f"[self-test] extraction patterns OK", flush=True)

    # junk-line guard: a citation/markup fragment must extract nothing kept
    junk = "paleoceanography , 8 ( 2 ) : 193-208 caused by data -lsb- edit -rsb-"
    assert _JUNK_RE.search(junk) is not None, "junk guard should flag citation/markup"
    print("[self-test] junk guard OK", flush=True)

    # band classifier reachability (reused rs)
    assert rs.classify_source_band(0.40, 0.20, 0.05) == "GREEN"
    assert rs.classify_source_band(0.60, 0.02, 0.02) == "PROMISCUOUS_FAIL"
    assert rs.classify_source_band(0.06, 0.03, 0.00) == "STILL_STARVED"
    assert plan_light("GREEN") == "GREEN" and plan_light("STILL_STARVED") == "RED"
    assert plan_light("PROMISCUOUS_FAIL") == "PROMISCUOUS" and plan_light("MIDDLE_BAND") == "MIDDLE"
    print("[self-test] band classifier + plan-light OK", flush=True)

    # induction (reused rs) keeps a planted ARC-relevant chain
    planted = [("CAUSE", "rain", "flood"), ("CAUSE", "flood", "erosion"), ("CAUSE", "volcano", "lava")]
    kept, istat = rs.induce_subgraph(planted, {"rain", "erosion"}, filler_budget=100)
    labs = set()
    for r in kept:
        labs.add(r["arg0"]); labs.add(r["arg1"])
    assert {"rain", "flood", "erosion"} <= labs, f"induction dropped planted chain: {labs}"
    print(f"[self-test] induction OK: {istat}", flush=True)

    # REAL-gate discriminator: planted extracted chain connects the correct choice, lure does not
    wn = _load_wordnet()
    pol = PolarityLexicon()
    base = cn._FakeBase()
    enc = cn.NegAwareEncoder(base, seed=SEED)
    g = cn.build_graph_gated(kept, enc.encode_batch, tau_unify=0.99, tau_sim=0.5, wn=wn, pol_lex=pol,
                             use_head_gate=True, use_pol_gate=True)

    def wvec(words):
        return gate._l2_rows(enc.encode_batch(words))

    def nodes_of(word):
        m = g["map_words"](wvec([word]))
        return set().union(*m) if m else set()

    rain_n, erosion_n, lava_n = nodes_of("rain"), nodes_of("erosion"), nodes_of("lava")
    assert rain_n and erosion_n, "planted words must map to nodes"
    assert gate.meet_connected(g["fwd"], g["bwd"], rain_n, erosion_n, DEPTH, min_len=1) is True, \
        "planted correct chain rain->flood->erosion MUST connect (gate can fire)"
    if lava_n:
        assert gate.meet_connected(g["fwd"], g["bwd"], rain_n, lava_n, DEPTH, min_len=1) is False, \
            "planted lure rain->lava MUST NOT connect (selectivity real / gate can fail)"
    print("[self-test] REAL-gate discriminator OK (correct connects, lure does not)", flush=True)
    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def run(output_dir, n_sample, seed, max_lines, filler_budget):
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "smoke" if max_lines else "full")
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _heartbeat(output_dir, "start", {"n_sample": n_sample, "max_lines": max_lines,
                                     "filler_budget": filler_budget, "tau_unify": TAU_UNIFY})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    # 1. encoders + node-identity resources (SAME as clean-node / CSKG gate)
    base_enc = SemanticHDEncoder()
    neg_enc = cn.NegAwareEncoder(base_enc, seed=seed)
    wn = base_enc._wn
    pol = PolarityLexicon()
    _heartbeat(output_dir, "encoder_ready")

    # 2. sample ARC-Challenge Qs (SAME seed permutation as parent) + seed vocab
    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(all_q))[:n_sample]
    questions = [all_q[int(i)] for i in sorted(idx.tolist())]
    seed_words = set()
    for q in questions:
        for w in arc._content_words(q["stem"], min_len=4):
            seed_words.add(w)
        for ch in q["choices"]:
            for w in arc._content_words(ch, min_len=4):
                seed_words.add(w)
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_sample": len(questions),
                                                "n_seed_words": len(seed_words)})

    # 3. RULE SOURCES (the one variable)
    wt_rows, wt_per_rel = rs.worldtree_rows()
    _heartbeat(output_dir, "worldtree_loaded", {"n_rows": len(wt_rows), "per_rel": wt_per_rel})

    sci_tuples, prov, sci_per_rel_raw, extract_stats = extract_science_rules(
        CORPUS_PATH, seed_words, max_lines, output_dir, seed)
    _heartbeat(output_dir, "science_extracted", extract_stats)

    sci_rows, induce_stat = rs.induce_subgraph(sci_tuples, seed_words, filler_budget, CSKG_MAX_DEG_INDUCE)
    _heartbeat(output_dir, "science_induced", induce_stat)

    union_rows = wt_rows + sci_rows

    # per-relation of the FINAL induced science rows
    sci_per_rel = {}
    for r in sci_rows:
        sci_per_rel[r["relation"]] = sci_per_rel.get(r["relation"], 0) + 1

    # 4. per-source eval (IDENTICAL gate; ONLY `rows` differs)
    results = {}
    for name, rows in (("worldtree", wt_rows), ("science_extract", sci_rows),
                       ("worldtree_science", union_rows)):
        _heartbeat(output_dir, f"{name}_eval_start", {"n_rows": len(rows)})
        res = rs.eval_source(rows, neg_enc, wn, pol, questions, output_dir, name)
        if res is not None:
            res["n_licensed_rows"] = len(rows)
            res["plan_light"] = plan_light(res["band"])
            results[name] = res
            _heartbeat(output_dir, f"{name}_done",
                       {"band": res["band"], "plan_light": res["plan_light"],
                        "cov": res["typed_correct_coverage"],
                        "typed_gap": res["typed_selectivity_gap"],
                        "untyped_gap": res["untyped_selectivity_gap"],
                        "max_deg": res["graph"]["max_typed_node_degree"]})

    # 5. precision spot-check sample (FINAL induced science rows) + automatic proxy
    prec_sample, prec_proxy = _precision_sample(sci_rows, prov, PROV_SAMPLE_TARGET, seed)
    _heartbeat(output_dir, "precision_sampled", prec_proxy)

    # 6. positive control (Gate D): worldtree arm must reproduce ~0.06 coverage
    wt_cov = results.get("worldtree", {}).get("typed_correct_coverage", None)
    control_ok = (wt_cov is not None and abs(wt_cov - 0.06) <= 0.06)  # within [0.0, 0.12], matched regime

    # 7. headline = best decision-useful band across the science + union sources
    def _rank(b):
        return {"GREEN": 3, "PROMISCUOUS_FAIL": 2, "MIDDLE_BAND": 1, "STILL_STARVED": 0}.get(b, -1)
    headline_source = max(("science_extract", "worldtree_science"),
                          key=lambda s: _rank(results.get(s, {}).get("band", "")))
    headline_band = results.get(headline_source, {}).get("band", "NO_SOURCE")
    headline_plan = plan_light(headline_band)

    sci_cov = results.get("science_extract", {}).get("typed_correct_coverage", None)
    sci_gap = results.get("science_extract", {}).get("typed_selectivity_gap", None)
    sci_ugap = results.get("science_extract", {}).get("untyped_selectivity_gap", None)

    table = []
    for name in ("worldtree", "science_extract", "worldtree_science"):
        r = results.get(name)
        if r is None:
            continue
        table.append({
            "source": name, "band": r["band"], "plan_light": r["plan_light"],
            "n_rules": r["n_licensed_rows"], "cov": r["typed_correct_coverage"],
            "typed_gap": r["typed_selectivity_gap"], "untyped_cov": r["untyped_correct_coverage"],
            "untyped_gap": r["untyped_selectivity_gap"], "gap_beats_untyped": r["typed_gap_beats_untyped"],
            "max_deg": r["graph"]["max_typed_node_degree"], "n_nodes": r["graph"]["n_nodes"],
        })

    summary = (f"SCIENCE-EXTRACT rule-supply | headline={headline_plan}({headline_band},{headline_source}) "
               f"| worldtree cov={wt_cov} (control_ok={control_ok}) -> science cov={sci_cov} "
               f"gap={sci_gap} vs untyped {sci_ugap} | n_extracted_kept={extract_stats['n_kept_arc_filtered']} "
               f"n_induced={len(sci_rows)} | wellformed_proxy={prec_proxy['wellformed_proxy_frac']}")

    vmsg_map = {
        "GREEN": ("GREEN (plan): science-precise extraction RAISED correct-choice coverage >=0.35 WITH "
                  "selectivity (typed gap>=0.15 and > untyped-null) -> unblocks Step 2 (build the composed "
                  "derivation reasoner). Rule-supply via science extraction IS the lever."),
        "PROMISCUOUS_FAIL": ("PROMISCUOUS (plan): coverage rose but selectivity ~ untyped-null (typed gap "
                             "<0.05 or <= untyped) -> the extraction is TOO NOISY; it connects everything "
                             "equally like a generic KB. Report the precision failure; tighten patterns or "
                             "escalate before reasoner investment."),
        "STILL_STARVED": ("RED (plan): even science-precise extraction keeps correct coverage <0.15 -> "
                          "extraction RECALL/quality is the bottleneck, not corpus availability. Redirect to "
                          "a broader source (CK-12 / OpenStax full-text) before further reasoner investment."),
        "MIDDLE_BAND": ("MIDDLE (plan): partial coverage with modest selectivity -> no clean GREEN; report "
                        "straight. Extraction moves the needle but does not clear the GREEN bar."),
    }
    vmsg = vmsg_map.get(headline_band, f"headline band = {headline_band}")

    metrics = {
        "verdict": "GATE_MEASURED",
        "headline_band": headline_band,
        "headline_plan_light": headline_plan,
        "headline_source": headline_source,
        "positive_control_worldtree_cov": wt_cov,
        "positive_control_ok": bool(control_ok),
        "summary": summary,
        "verdict_msg": vmsg,
        "anchor_name": ANCHOR_NAME,
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": "smoke" if max_lines else "full",
        "config": {"n_sample": len(questions), "tau_unify": TAU_UNIFY, "tau_sim": TAU_SIM,
                   "depth": DEPTH, "seed": seed, "filler_budget": filler_budget, "max_lines": max_lines,
                   "arg_max_tok": ARG_MAX_TOK, "keep_cap": KEEP_CAP,
                   "one_variable": "rule_source (worldtree vs science_extract vs union); node-identity/"
                                   "gate/induction/Qs/depth/thresholds IDENTICAL to CSKG rule-supply gate",
                   "corpus": os.path.relpath(CORPUS_PATH, _REPO),
                   "licensed": list(gate.LICENSED)},
        "per_source_table": table,
        "results": results,
        "extraction": {"stats": extract_stats, "per_relation_raw_kept": sci_per_rel_raw,
                       "per_relation_induced": sci_per_rel, "n_induced_rows": len(sci_rows),
                       "induction": induce_stat},
        "precision_spot_check": {"proxy": prec_proxy, "sample": prec_sample},
        "worldtree_per_relation": wt_per_rel,
        "bands_preregistered": {
            "GREEN (unblocks Step 2)": f"cov >= {rs.GREEN_COV} AND typed_gap >= {rs.GREEN_GAP} AND "
                                       "typed_gap > untyped_gap",
            "PROMISCUOUS (extraction too noisy)": f"cov > {rs.PROMISCUOUS_COV} AND (typed_gap < "
                                                  f"{rs.PROMISCUOUS_GAP} OR typed_gap <= untyped_gap)",
            "RED (extraction recall bottleneck -> broaden source)": f"cov < {rs.STARVED_COV}",
            "MIDDLE": "otherwise",
            "HONEST_GUARD": "coverage AND selectivity together; precision measured (spot-check sample); "
                            "NOT tuned to force GREEN; ONE variable = rule table.",
        },
        "parent_ref": {"cskg_cell": "arc_derivation_rule_supply_cskg_v1 (SETTLED wrong supply)",
                       "cleannodes_cell": "arc_derivation_connectivity_gate_cleannodes_v2 (99736f579)",
                       "worldtree_clean_typed_cov_on_disk": 0.06,
                       "outcome_lineage": "COVERAGE_BOUND_CONFIRMED -> CSKG wrong supply -> science-precise "
                                          "extraction (this cell)"},
        "notes": ("ONE-VARIABLE ablation: rule SOURCE only (science extraction from ARC_Corpus.txt). "
                  "Node-identity (NegAwareEncoder + head-gate + polarity merge-gate), gate "
                  "(build_graph_gated + meet_connected), induction (induce_subgraph), Qs, depth, thresholds "
                  "ALL imported UNCHANGED from the CSKG rule-supply cell. STRAIGHT report; NOT tuned. "
                  "plan_light maps rs bands to the plan's GREEN/PROMISCUOUS/RED/MIDDLE."),
        "REQUIRED_FIELDS": ["verdict", "headline_band", "headline_plan_light", "positive_control_ok",
                            "per_source_table", "results", "extraction", "precision_spot_check"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== SCIENCE-EXTRACT RULE-SUPPLY CONNECTIVITY GATE RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"HEADLINE = {headline_plan} ({headline_band}, {headline_source}) :: {vmsg}", flush=True)
    print(f"positive_control worldtree cov={wt_cov} ok={control_ok} (expected ~0.06)", flush=True)
    print("per-source table:", flush=True)
    for row in table:
        print(f"  {row['source']:>18} band={row['band']:<16}({row['plan_light']:<11}) rules={row['n_rules']:>7} "
              f"cov={row['cov']:.3f} typed_gap={row['typed_gap']:+.4f} "
              f"untyped_cov={row['untyped_cov']:.3f} untyped_gap={row['untyped_gap']:+.4f} "
              f"gap>untyped={row['gap_beats_untyped']} max_deg={row['max_deg']} nodes={row['n_nodes']}",
              flush=True)
    print(f"extraction: {extract_stats}", flush=True)
    print(f"precision proxy: {prec_proxy}", flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=100, help="ARC-Challenge sample size")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--filler-budget", type=int, default=FILLER_BUDGET)
    ap.add_argument("--max-lines", type=int, default=0,
                    help="cap ARC_Corpus lines scanned (>0 = partial; smoke uses a cap; 0 = full scan)")
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    if args.mode == "smoke":
        n_sample = 12
        max_lines = args.max_lines or 1000000
        filler_budget = min(args.filler_budget, 1500)
    else:
        n_sample = args.n
        max_lines = args.max_lines  # 0 = full scan
        filler_budget = args.filler_budget

    output_dir = args.out
    try:
        run(output_dir, n_sample, args.seed, max_lines, filler_budget)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
