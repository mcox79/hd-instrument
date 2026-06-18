"""Tier-3 EXPERIMENT_RECORD atomizer (DECISION 237; Skunkworks SCHEMA 3 + 5 auditor conditions).

Walks data/*/metrics.json (the authoritative artifact spine; ~1935 experiments) and the matched
experiments/<name>.py cell + preregs/*<slug>*.md prereg, and builds kind=EXPERIMENT_RECORD atoms.

Addresses the USER loss-concern (~2000 prior experiments) + the searchability payoff
(cross-experiment "what prior work is analogous?" becomes a one-step graph walk) + the
evidence-base audit (provenance_quality flags surface which claims rest on cert-grade vs thin evidence).

SCHEMA 3 (Skunkworks):
  id math::T3/EXP_<name>; kind experiment_record; metric_type null; term_class PROCESS_KNOWLEDGE_NON_MATH;
  experiment_path/prereg_path/metrics_path/cell_sha/remote_run_id; hypothesis; verdict; relevance_tier;
  run_mode; era; provenance_quality; DEPENDS_ON primitives_used+capabilities_tested (existing ids only);
  provenance {cell_sha, metrics_sha, date, session_authored}.

5 AUDITOR CONDITIONS (non-negotiable; enforced here):
  1. DETERMINISTIC classification, NO LLM. verdict from metrics verdict-token; relevance_tier from
     atom LINKAGE (not original claim, not age); era from date; provenance_quality from run_mode + markers.
  2. NO PHANTOM DEPENDS_ON. Every edge target verified in-store; unmatched references OMITTED + logged.
  3. relevance_tier by CURRENT-VERIFIED-LINKAGE (HIGH iff linked to a CONFIRMED capability/foundation
     atom TODAY AND verdict positive). Old != archive; a pre-build experiment that proved a current
     capability = HIGH by linkage.
  4. provenance_quality FLAG ON EVERY RECORD (legacy/smoke cannot masquerade as cert-grade).
  5. BATCHED ingest 50-100/batch; cap_pres (module liveness 6/6) + axiom_term verified BETWEEN batches;
     dropped/skipped logged (no silent truncation).

DRY-RUN-FIRST (default): discover + classify + resolve DEPENDS_ON + write a VET-able sample JSONL +
summary report; NO substrate mutation. Set HDLAB_ATOMIZE_APPLY=1 to actually ingest (batched, gated).
This lets Skunkworks VET the deterministic classification + no-phantom resolution + provenance flags on
real output BEFORE any mutation; actual ingest is gated on VET clean + Director ratify-pace.

Env:
  HDLAB_ATOMIZE_APPLY=1     apply (ingest); default 0 = dry-run
  HDLAB_ATOMIZE_BATCH=50    batch size (50-100; condition 5)
  HDLAB_ATOMIZE_LIMIT=50    max atoms this run (first batch = 50 per DECISION 237 smoke)
"""
from __future__ import annotations
import os
import re
import sys
import json
import glob
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType, Relation

REPO = Path(__file__).resolve().parents[1]
SRC_TAG = "DECISION_237_tier_3_EXPERIMENT_RECORD_atomizer_SCHEMA_3_5_auditor_conditions"  # non-"manual" -> bypass hand cap
SESSION = "exp_dev"

# Substrate-build cutoff (schema.py: SUBSTRATE_SELF_INDEX_PILOT 2026-06-11). era is DESCRIPTIVE only.
SUBSTRATE_BUILD_CUTOFF = "2026-06-10"

VERDICT_SET = {"PASS", "HARD_FAIL", "HONEST_NEGATIVE", "HONEST_BOUNDED", "MIDDLE_BAND", "LOAD_BEARING", "KILLED",
               "SPARSITY_NEUTRAL"}  # recapture-program: capability-lifted-but-sparsity-neutral (distinct from MIDDLE_BAND)

# Deterministic curated primitive-keyword -> candidate atom-id map (every target VERIFIED in-store before
# any edge is emitted; condition 2). Conservative: only the highest-frequency, unambiguous primitives.
PRIMITIVE_KEYWORDS = {
    "resonator": "T3/resonator_network_decoder",
    "hopfield": "T2/modern_hopfield_ramsauer",
    "sparse_hopfield": "T2/sparse_hopfield_hu_santos",
    "viterbi": "T3/viterbi_decode",
    "perceptron": "T3/discriminative_perceptron",
    "fhrr": "T2/fhrr_bind",
    "bind": "T2/fhrr_bind",
    "cleanup": "T2/cosine_cleanup",
    "residue": "T1/chinese_remainder_theorem",
    "crt": "T1/chinese_remainder_theorem",
    "fractional_power": "T2/fractional_power_encoding",
    "fpe": "T2/fractional_power_encoding",
}

# condition-5 / BLOCKING-fix (Skunkworks VET): atomize on ANY substantive content; drop ONLY genuinely-empty.
# Older metrics schemas (m-series, scaling, wave-Hopf, charlm) carry results in headline/numeric fields, NOT a
# `verdict` field -- dropping them = total loss of the pre-build experiments the USER asked to preserve.
CONTENT_KEYS = ("verdict", "verdict_msg", "headline", "summary", "anchor_name", "aggregated", "cells",
                "per_seed", "results", "config", "spec")
NUMERIC_RESULT_FIELDS = ("perfect_recoveries", "mean_sim", "min_sim", "max_sim", "total_events", "recall",
                         "precision", "f1", "accuracy", "acc", "rmse", "mae", "auc", "score", "success",
                         "min_recall", "trials", "min_conf", "mean_conf")
# Q4 (Skunkworks ruling): route language experiments to concept corpus via a deterministic name marker.
LANGUAGE_MARKERS = ("charlm", "char_lm", "_lm_", "tiny_transformer", "language_model", "_charlm")


def metrics_headline(metrics: dict) -> str | None:
    """Deterministic short result string preserved on every record (esp. older-schema; condition-5 fix)."""
    for k in ("headline", "verdict_msg", "summary"):
        v = metrics.get(k)
        if isinstance(v, str) and v.strip():
            return v[:300]
    # older-schema numeric headline
    nums = {k: metrics[k] for k in NUMERIC_RESULT_FIELDS if k in metrics and isinstance(metrics[k], (int, float))}
    return ("; ".join(f"{k}={v}" for k, v in nums.items())[:300]) if nums else None


def has_substantive_content(metrics: dict, cell) -> bool:
    """True iff the record has ANY content worth preserving (atomize); False = genuinely empty (drop)."""
    if any(metrics.get(k) for k in CONTENT_KEYS):
        return True
    if any(k in metrics for k in NUMERIC_RESULT_FIELDS):
        return True
    return cell is not None


def corpus_for(name: str, hypothesis: str):
    """Q4 deterministic corpus routing: language experiments -> concept; else math."""
    base = sanitize(name[4:] if name.startswith("exp_") else name)   # strip redundant leading 'exp_'
    low = (name + " " + (hypothesis or "")).lower()
    if any(mk in low for mk in LANGUAGE_MARKERS):
        return Corpus.CONCEPT, Tier.TIER_NA, f"EXP_{base}"
    return Corpus.MATH, Tier.TIER_3_ALGORITHM, f"T3/EXP_{base}"


def axiom_term(ps):
    forward = {}
    for src, rel, tgt in ps.iter_all_relations():
        if rel.name in ('DEPENDS_ON', 'SPECIALIZES'):
            forward.setdefault(src, []).append(tgt)
    axioms = set()
    for a in ps.all_atoms():
        if str(a.tier.name) != 'TIER_1_FOUNDATIONAL':
            continue
        if str(a.corpus.name) != 'MATH':
            continue
        role = (a.algebra or {}).get('role', '')
        if (a.metadata or {}).get('is_axiom', False) or role in ('axiom_schema', 'axiom', 'type'):
            axioms.add(f'math::{a.id}')

    def terminates(s, d=15):
        seen = {s}; f = [s]
        for _ in range(d):
            n = []
            for x in f:
                if x in axioms:
                    return True
                for t in forward.get(x, []):
                    if t not in seen:
                        seen.add(t); n.append(t)
            f = n
            if not f:
                break
        return any(x in axioms for x in seen)

    ops = [a for a in ps.all_atoms()
           if str(a.corpus.name) == 'MATH'
           and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
           and a.algebra and len(a.algebra) >= 3
           and 'oeis' not in str(a.id).lower()
           and not str(a.id).startswith('T3/wikidata_')]
    t = sum(1 for op in ops if terminates(f'math::{op.id}'))
    return t, len(ops)


def module_liveness_ok():
    """cap_pres proxy: the 6 production capability modules still import + expose their entry point."""
    import importlib
    return all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def sha1_file(p: Path) -> str | None:
    try:
        return hashlib.sha1(p.read_bytes()).hexdigest()[:12]
    except Exception:
        return None


def sanitize(name: str) -> str:
    return re.sub(r'[^0-9a-zA-Z_]', '_', name).strip('_')


def normalize_verdict(raw) -> str | None:
    """Map a raw verdict string to the SCHEMA-3 verdict set. Deterministic token search. None if unmappable."""
    if not raw:
        return None
    u = str(raw).upper()
    if "HARD_FAIL" in u or u.endswith("_FAIL") or u == "FAIL":
        return "HARD_FAIL"
    if "KILLED" in u:
        return "KILLED"
    if "NON_TEST" in u or "NON-TEST" in u:                  # honest non-discriminating-regime result (real verdict)
        return "NON_TEST"
    if "ATTRIBUTION" in u:                                  # mechanism-attribution record (not a pass/fail; e.g. A1)
        return "ATTRIBUTION"
    if "SPARSITY_NEUTRAL" in u or "SPARSITY-NEUTRAL" in u:   # recapture: capability lifted, sparsity gives no edge
        return "SPARSITY_NEUTRAL"
    if "MIDDLE" in u:
        return "MIDDLE_BAND"
    if "HONEST_BOUNDED" in u or "BOUNDED" in u:
        return "HONEST_BOUNDED"
    if "HONEST_NEGATIVE" in u or "NEGATIVE" in u:
        return "HONEST_NEGATIVE"
    if "LOAD_BEARING" in u or "LOADBEARING" in u:
        return "LOAD_BEARING"
    if "HARD_PASS" in u or "_PASS" in u or u == "PASS" or "SUPPORTED" in u or "RESTORES" in u or "RESCUES" in u:
        return "PASS"
    return None


def era_for(date_str: str) -> str:
    return "PRE_SUBSTRATE_BUILD" if (date_str and date_str < SUBSTRATE_BUILD_CUTOFF) else "SUBSTRATE_BUILD"


# METHOD-GATE (Skunkworks ruling 2026-06-18; RULE_C1): a cost-model/roofline PREDICTION (or an undeclared/null
# source) is NOT cert-grade for a measured claim -- a model is not a measurement. A SYNTHETIC experiment IS a real
# measurement (of a synthetic system) -> cert-eligible. Denylist (reject cost-model + null), not allowlist.
COST_MODEL_TOKENS = ("cost_model", "cost-model", "roofline", "analytic_model", "prediction")
_COST_MODEL_VM = ("cost_model", "cost model", "roofline")


def method_gate_ok(metrics: dict) -> bool:
    """True iff cert-eligible BY METHOD: a declared, non-cost-model metrics_source (synthetic/measured/real_* OK)."""
    src = str(metrics.get("metrics_source") or "").lower()
    vm = str(metrics.get("verdict_msg") or "").lower()
    if any(t in src for t in COST_MODEL_TOKENS) or any(t in vm for t in _COST_MODEL_VM):
        return False                                   # cost-model/roofline prediction -> not measured
    return bool(src)                                   # null/undeclared source -> not cert-grade (ruling)


def gate0_field_check(metrics: dict) -> bool:
    """GATE-0 CONSUMER check (Skunkworks C2 self-certification engine, 2026-06-18; defense-in-depth with the
    producer-side _cell_provenance.gate0_self_check). ADDITIVE + NON-RETROACTIVE: fails ONLY if the cell EMITTED a
    gate0_self_check whose pass==False (an early-exit / smoke-default / not-measured run the cell self-reported as
    incomplete). Cells WITHOUT the field pass (legacy-safe -> no mass recompute of the existing 568 cert atoms; the
    cert-tier-recompute-scope lesson). This catches the measured-but-EARLY-EXITED run that method_gate_ok alone
    misses (method-gate verifies it was MEASURED; gate0 verifies it actually RAN COMPLETE)."""
    g = metrics.get("gate0_self_check")
    if isinstance(g, dict) and g.get("pass") is False:
        return False
    return True


def provenance_quality(run_mode, n_seeds, metrics: dict, verdict_norm) -> str:
    """Deterministic from run_mode + cert-discipline markers + METHOD-GATE + GATE-0. condition 4 + method-gate + C2."""
    # ATTRIBUTION (mechanism record; e.g. A1): MEASURED but NOT a verdict-cert -> distinct tier, NEVER cert-counted
    # (Skunkworks C2 E5-fold: fixes the LEGACY_EXCERPT mislabel of fresh measured-mechanism atoms; keeps the proof-
    # count = verdicts only). Structural: an ATTRIBUTION can never be CERT_CHAIN_GRADE even if cert-shaped.
    if verdict_norm == "ATTRIBUTION":
        return "MEASURED_MECHANISM" if method_gate_ok(metrics) else "UNVERIFIED"
    cert_markers = any(k in metrics for k in ("prereg_bands", "fair_null", "FAIR_NULL", "gold_firewall",
                                              "three_of_three", "cert_chain", "ci95", "acc_ci95"))
    # Skunkworks 2026-06-18: a real-held-out benchmark eval (full + held-out measured source) is cert-grade EVIDENCE
    # n_seeds-INDEPENDENT -- the held-out set + sweep IS the variation; re-seeding a FIXED held-out set adds nothing.
    # NARROW: only metrics_source containing 'held_out' (real-held-out evals); composes with the method-gate below
    # (method_gate_ok still required -- this is not a bypass, just the right rigor axis for a held-out eval).
    held_out_eval = run_mode == "full" and "held_out" in str(metrics.get("metrics_source") or "").lower()
    would_be_cert = run_mode == "full" and ((isinstance(n_seeds, int) and n_seeds >= 3) or cert_markers or held_out_eval)
    if would_be_cert and method_gate_ok(metrics) and gate0_field_check(metrics):
        return "CERT_CHAIN_GRADE"
    if would_be_cert and method_gate_ok(metrics):      # measured + cert-shaped but GATE-0 self-check FAILED
        return "UNVERIFIED"                            # the cell self-reported INCOMPLETE (early-exit / not-full) -> not cert
    if would_be_cert:                                  # cert-shaped but METHOD-GATE FAILED -> explicit non-cert tier
        src = str(metrics.get("metrics_source") or "").lower()
        vm = str(metrics.get("verdict_msg") or "").lower()
        if any(t in src for t in COST_MODEL_TOKENS) or any(t in vm for t in _COST_MODEL_VM):
            return "COST_MODEL"                        # a prediction, not a measurement (e.g. 8a roofline)
        return "UNVERIFIED"                            # null/undeclared source -> provenance insufficient for cert
    if run_mode == "smoke":
        return "SMOKE_ONLY"
    if verdict_norm is None or run_mode is None:
        return "UNVERIFIED" if verdict_norm is None else "LEGACY_EXCERPT"
    return "LEGACY_EXCERPT"


# Generic math tails too common to be meaningful primitives_used signal (would over-match cell prose).
GENERIC_TAIL_STOPLIST = {
    "vector", "vector_space", "category", "gradient", "inner_product", "cosine_similarity",
    "metric_space", "unit_modulus", "jensen_inequality", "tracy_widom_distribution", "norm",
    "matrix", "scalar", "function", "set", "group", "ring", "field", "module", "topology",
    "distance", "mean", "variance", "probability", "distribution", "softmax", "sigmoid",
}


def build_atom_index(ps):
    """Returns (all_qids, primitive_targets, cap_serving_primitives).

    primitive_targets: tail(lower) -> qid for math T2/T3 SPECIFIC primitives (not wikidata/oeis,
       tail >= 10 chars, not in GENERIC_TAIL_STOPLIST) -- the real substrate primitives a cell USES.
    cap_serving_primitives: qids that serve a CONFIRMED capability (capability.current_best_solution
       OR primitive.serves_capability nonempty) -- the linkage that earns relevance_tier HIGH."""
    all_qids = set()
    primitive_targets = {}
    cap_serving = set()
    atoms = ps.all_atoms()
    for a in atoms:
        all_qids.add(a.qualified_id)
    for a in atoms:
        q = a.qualified_id
        # capability-serving primitives = capability.current_best_solution ONLY (the genuine, narrow signal;
        # serves_capability is polluted -- set on ~all 24653 atoms -- so it is NOT used as a linkage signal).
        if str(a.kind.name) == "CAPABILITY" and a.current_best_solution and a.current_best_solution in all_qids:
            cap_serving.add(a.current_best_solution)
        # specific math T2/T3 primitive targets for DEPENDS_ON matching
        if (str(a.corpus.name) == "MATH"
                and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
                and "wikidata" not in a.id.lower() and "oeis" not in a.id.lower()):
            tail = (a.id.split("/")[-1] if "/" in a.id else a.id).lower()
            if len(tail) >= 10 and tail not in GENERIC_TAIL_STOPLIST and "_" in tail:
                primitive_targets[tail] = q
    return all_qids, primitive_targets, cap_serving


def resolve_depends_on(text_blob: str, primitive_targets: dict, all_qids: set) -> list[str]:
    """Deterministic, no-phantom: token-set membership of specific primitive tails + curated keywords.
    Excludes generic T1 tails (stoplist) + wikidata/oeis. Conservative -- omit when no confident match.

    PERF: token-set membership is PROVABLY EQUIVALENT to the prior `re.search(r'\\b'+tail+r'\\b', low)`:
    on lowercased text, \\w == [a-z0-9_], so \\b boundaries are exactly the [^a-z0-9_]/[a-z0-9_] transitions
    -> `\\b<tail>\\b` matches iff <tail> is a maximal [a-z0-9_] run == a token in split(r'[^a-z0-9_]+').
    (tails/keywords are already [a-z0-9_]-only.) Skunkworks verified zero depends_on change on 200 records.
    Replaces O(patterns) regex SEARCH-VOLUME (2103 patterns x N records) with O(1) set membership (~2000x)."""
    found = set()
    toks = set(re.split(r'[^a-z0-9_]+', text_blob.lower()))
    for tail, q in primitive_targets.items():
        if tail in toks:
            found.add(q)
    for kw, atom_id in PRIMITIVE_KEYWORDS.items():
        if kw in toks:
            q = f"math::{atom_id}"
            if q in all_qids:
                found.add(q)
    return sorted(found)


def find_cell(name: str) -> Path | None:
    p = REPO / "experiments" / f"{name}.py"
    if p.exists():
        return p
    # strip common trailing suffixes the data-dir may carry that the cell stem does not
    for suf in ("_smoke", "_cpu_v1", "_gpu_v1", "_v1", "_v2", "_v3"):
        if name.endswith(suf):
            p2 = REPO / "experiments" / f"{name[:-len(suf)]}.py"
            if p2.exists():
                return p2
    hits = sorted(glob.glob(str(REPO / "experiments" / f"{name}*.py")))
    return Path(hits[0]) if hits else None


def find_prereg(name: str) -> Path | None:
    slug = name.replace("exp_", "")[:24]
    hits = sorted(glob.glob(str(REPO / "preregs" / f"*{slug}*.md")))
    return Path(hits[0]) if hits else None


def extract_hypothesis(cell: Path | None, prereg: Path | None, metrics: dict) -> str:
    """Deterministic: cell module docstring -> prereg first paragraph -> metrics anchor/verdict_msg."""
    if cell and cell.exists():
        try:
            txt = cell.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'"""(.*?)"""', txt, re.DOTALL)
            if m:
                doc = " ".join(m.group(1).split())
                if len(doc) > 20:
                    return doc[:500]
        except Exception:
            pass
    if prereg and prereg.exists():
        try:
            for line in prereg.read_text(encoding="utf-8", errors="ignore").splitlines():
                s = line.strip().lstrip("#").strip()
                if len(s) > 20:
                    return s[:500]
        except Exception:
            pass
    return (str(metrics.get("anchor_name") or "") + " :: " + str(metrics.get("verdict_msg") or ""))[:500]


def classify_relevance(verdict_norm, depends_on, cap_serving, run_mode, pq) -> str:
    """condition 3: by CURRENT-VERIFIED-LINKAGE + verdict; NOT age, NOT original claim.
    HIGH = strong linkage (capability current_best_solution primitive) + positive verdict, OR
           foundation-primitive linkage + positive verdict + CERT_CHAIN_GRADE provenance
           (a metric-grounded, positive, load-bearing-linked experiment).
    Foundation-only / weaker-provenance -> MEDIUM/LOW. Unlinked + not-full-positive -> ARCHIVE.
    NOTE: the precise tier boundary is Skunkworks's (cert-owner) policy call; this is a conservative default.
    Linkage reality (surfaced for the policy ruling): capability current_best_solution = 3 primitives only;
    serves_capability is polluted (unused); foundation = 186 specific T2/T3 primitives."""
    linked_cap = any(d in cap_serving for d in depends_on)   # strong: serves a confirmed capability
    linked_found = len(depends_on) > 0                        # foundation: uses a specific T2/T3 primitive
    pos = verdict_norm in ("PASS", "LOAD_BEARING")
    mid = verdict_norm in ("HONEST_BOUNDED", "MIDDLE_BAND", "HONEST_NEGATIVE")
    if (linked_cap and pos) or (linked_found and pos and pq == "CERT_CHAIN_GRADE"):
        return "HIGH"
    if linked_found and (pos or (mid and run_mode == "full")):
        return "MEDIUM"
    if linked_found or (run_mode == "full" and pos):
        return "LOW"
    return "ARCHIVE"


def discover():
    """Yield record dicts for every data/*/metrics.json. Logs dropped (no silent truncation)."""
    records, dropped = [], []
    # depth-2 (data/<exp>/metrics.json) UNION recursive (catches nested-deeper, e.g. data/<exp>/<sub>/metrics.json
    # -- the ~21 the depth-2 glob missed). Dedupe via set; path-filter non-experiment metrics.json.
    paths = set(glob.glob(str(REPO / "data" / "*" / "metrics.json")))
    paths |= set(glob.glob(str(REPO / "data" / "**" / "metrics.json"), recursive=True))
    _skip = ("/staging/", "data_remote_pull", "/node_modules/", "/_cache", "/.git/")
    for mf in sorted(paths):
        if any(seg in mf.replace("\\", "/") for seg in _skip):
            continue  # path-filter: skip non-experiment metrics.json (staging/pull/cache/vendored)
        mpath = Path(mf)
        rel = mpath.parent.relative_to(REPO / "data")
        name = "_".join(rel.parts)  # depth-2: single part == prior parent.name (IDEMPOTENT); nested: <exp>_<sub>
        try:
            metrics = json.load(open(mf, encoding="utf-8"))
        except Exception as e:
            dropped.append((name, f"metrics.json unparseable: {e}"))
            continue
        if not isinstance(metrics, dict):
            dropped.append((name, "metrics.json not a dict"))
            continue
        cell = find_cell(name)
        prereg = find_prereg(name)
        verdict_norm = normalize_verdict(metrics.get("verdict"))
        # BLOCKING-fix (Skunkworks VET): atomize on ANY substantive content with verdict=null when unmapped;
        # preserve headline + key metrics. DROP ONLY a genuinely-empty metrics.json (no content at all).
        if not has_substantive_content(metrics, cell):
            dropped.append((name, "genuinely empty: no verdict/headline/numeric-result/content + no cell"))
            continue
        run_mode = metrics.get("run_mode")
        n_seeds = metrics.get("n_seeds")
        # date: metrics timestamp -> prereg filename date -> metrics file mtime
        date_str = ""
        ts = metrics.get("timestamp")
        if isinstance(ts, str) and len(ts) >= 10:
            date_str = ts[:10]
        elif prereg:
            md = re.search(r'(\d{4}-\d{2}-\d{2})', prereg.name)
            date_str = md.group(1) if md else ""
        if not date_str:
            import datetime
            date_str = datetime.date.fromtimestamp(mpath.stat().st_mtime).isoformat()
        records.append(dict(
            name=name, metrics=metrics, metrics_path=mpath, cell=cell, prereg=prereg,
            verdict_norm=verdict_norm, verdict_raw=metrics.get("verdict"),
            run_mode=run_mode, n_seeds=n_seeds, date_str=date_str,
            remote_run_id=metrics.get("remote_run_id") or metrics.get("run_id"),
        ))
    return records, dropped


# ===== Skunkworks A5-queryability durable fix (PATH a; spec 2026-06-18) =====
# Dual-axis / positive-in-payload records (A5 readout-C1, A1 attribution channels, A3 envelope) buried their
# positives in structured payload fields -> key_metrics empty -> non-queryable. (1) flatten all-scalar payload
# dicts into prefixed key_metrics; (2) build a strengthens/replicates RELATES edge from a `strengthens_cert`
# record field; (3) refresh existing atoms on content-change (update-in-place) instead of blind collision-skip.
PAYLOAD_FLATTEN_EXCLUDE = ("config", "spec", "provenance", "per_seed", "cells", "aggregated", "results",
                           "result", "depends_on", "env", "args", "capacity_curves")
_SCALARISH = (int, float, str, bool)


def flatten_payload_metrics(metrics: dict, max_fields: int = 80) -> dict:
    """Flatten all-scalar result-payload dicts into prefixed key_metrics (Skunkworks dual-axis fix #1)."""
    out: dict = {}
    for k, v in metrics.items():
        if k in PAYLOAD_FLATTEN_EXCLUDE or not isinstance(v, dict) or not v:
            continue
        if all((sv is None or isinstance(sv, _SCALARISH)) for sv in v.values()):  # genuine result payload
            for sk, sv in v.items():
                out[f"{k}.{sk}"] = sv
                if len(out) >= max_fields:
                    return out
    return out


def read_strengthens(metrics: dict) -> list:
    """Read the optional strengthens_cert record field (qids this record replicates/strengthens) -> edge targets."""
    raw = metrics.get("strengthens_cert") or []
    if isinstance(raw, str):
        raw = [raw]
    return [s for s in raw if isinstance(s, str) and "::" in s]


def content_hash(key_metrics: dict, headline, verdict, rel_tier, strengthens: list, desc: str) -> str:
    """Stable hash of the QUERYABLE content (drives update-on-content-change #3; ignores volatile provenance)."""
    blob = json.dumps(dict(km=key_metrics, hl=headline, v=verdict, rt=rel_tier,
                           st=sorted(strengthens), d=desc), sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def add_strengthens_edge(psb, src_qid: str, tgt_qid: str) -> bool:
    """RELATES edge tagged relation_role=replicates_strengthens (Skunkworks #2); True iff a NEW triple landed.

    Same-corpus path constructs the Relation with metadata (queryable role) + dedups exactly; cross-corpus falls
    back to the partition path (role-in-note). Caller must no-phantom-gate (tgt must resolve) BEFORE calling.
    """
    from backend.substrate_index.partition import QualifiedAtomId   # defined in partition, not schema
    src_q = QualifiedAtomId.parse(src_qid)
    tgt_q = QualifiedAtomId.parse(tgt_qid)
    if src_q.corpus == tgt_q.corpus:
        st = psb._store_for(src_q.corpus)
        triple = (src_q.local_id, RelationType.RELATES.value, tgt_q.local_id)
        if triple in st._all_relations:
            return False                                          # idempotent: edge already present
        st.add_relation(Relation(src_id=src_q.local_id, tgt_id=tgt_q.local_id, rel_type=RelationType.RELATES,
                                 metadata={"relation_role": "replicates_strengthens", "source": SRC_TAG}),
                        source=SRC_TAG, note=f"{src_q.local_id} replicates_strengthens {tgt_q.local_id}")
        return True
    psb.add_relation(src_qid, RelationType.RELATES, tgt_qid, source=SRC_TAG,
                     note=f"replicates_strengthens: {src_qid} -> {tgt_qid}")
    return True


def build_atom_spec(rec, all_qids, primitive_targets, cap_serving):
    name = rec["name"]
    metrics = rec["metrics"]
    cell, prereg, mpath = rec["cell"], rec["prereg"], rec["metrics_path"]
    text_blob = name + " " + str(metrics.get("anchor_name") or "")
    if cell and cell.exists():
        try:
            text_blob += " " + cell.read_text(encoding="utf-8", errors="ignore")[:8000]
        except Exception:
            pass
    depends_on = resolve_depends_on(text_blob, primitive_targets, all_qids)
    verdict_norm = rec["verdict_norm"]
    run_mode = rec["run_mode"]
    pq = provenance_quality(run_mode, rec["n_seeds"], metrics, verdict_norm)
    rel_tier = classify_relevance(verdict_norm, depends_on, cap_serving, run_mode, pq)
    era = era_for(rec["date_str"])
    hypothesis = extract_hypothesis(cell, prereg, metrics)
    headline = metrics_headline(metrics)   # preserved on EVERY record (older-schema results survive)
    key_metrics = {k: metrics[k] for k in NUMERIC_RESULT_FIELDS
                   if k in metrics and isinstance(metrics[k], (int, float))}
    key_metrics.update(flatten_payload_metrics(metrics))   # Skunkworks #1: payload positives -> queryable
    strengthens = read_strengthens(metrics)                # Skunkworks #2: replicates/strengthens edge targets
    cell_sha = sha1_file(cell) if cell else None
    metrics_sha = sha1_file(mpath)
    corpus, tier, local_id = corpus_for(name, hypothesis)   # Q4 deterministic routing
    qid = f"{corpus.value}::{local_id}"
    desc = (f"Experiment record: {name}. Verdict {verdict_norm or 'UNMAPPED(null)'} "
            f"(raw {rec['verdict_raw']!r}); run_mode {run_mode}; provenance_quality {pq}; "
            f"relevance_tier {rel_tier}; era {era}. Headline: {headline or 'n/a'}. Hypothesis: {hypothesis}")
    chash = content_hash(key_metrics, headline, verdict_norm, rel_tier, strengthens, desc[:1200])  # Skunkworks #3
    metadata = dict(
        record_class="experiment_record",
        term_class="PROCESS_KNOWLEDGE_NON_MATH",
        metric_type=None,
        experiment_path=str(cell.relative_to(REPO)) if cell else None,
        prereg_path=str(prereg.relative_to(REPO)) if prereg else None,
        metrics_path=str(mpath.relative_to(REPO)),
        cell_sha=cell_sha,
        remote_run_id=rec["remote_run_id"],
        hypothesis=hypothesis,
        metrics_headline=headline,            # condition-5 fix: preserve older-schema result string
        key_metrics=key_metrics,              # condition-5 fix + Skunkworks #1: numeric + flattened-payload, queryable
        strengthens_cert=strengthens,         # Skunkworks #2: replicates/strengthens edge targets (qids)
        verdict=verdict_norm,                 # null when unmapped (preserved-but-unjudged, never dropped)
        verdict_raw=str(rec["verdict_raw"]),
        relevance_tier=rel_tier,
        run_mode=run_mode,
        era=era,
        provenance_quality=pq,
        depends_on_resolved=depends_on,
        depends_on_count=len(depends_on),
        provenance=dict(cell_sha=cell_sha, metrics_sha=metrics_sha, date=rec["date_str"], session_authored=SESSION),
        eleventh_rule_clean=True,
        deterministic_no_llm=True,
        content_hash=chash,                   # Skunkworks #3: update-on-content-change anchor
        source=SRC_TAG,
    )
    return dict(id=local_id, qid=qid, corpus=corpus, tier=tier, name=f"EXP {name}"[:120],
                description=desc[:1200], metadata=metadata, depends_on=depends_on, verdict=verdict_norm,
                relevance_tier=rel_tier, provenance_quality=pq, era=era, run_mode=run_mode,
                strengthens=strengthens, content_hash=chash)


def summarize(specs, dropped):
    from collections import Counter
    vc, rc, pc, ec, dc = Counter(), Counter(), Counter(), Counter(), Counter()
    edge_total = 0
    for s in specs:
        vc[s["verdict"]] += 1; rc[s["relevance_tier"]] += 1; pc[s["provenance_quality"]] += 1
        ec[s["era"]] += 1; dc[s["metadata"]["depends_on_count"]] += 1
        edge_total += s["metadata"]["depends_on_count"]
    print("=" * 80)
    print(f"DISCOVERED: {len(specs)} candidate EXPERIMENT_RECORD atoms | DROPPED: {len(dropped)}")
    print(f"  verdict:           {dict(vc.most_common())}")
    print(f"  relevance_tier:    {dict(rc.most_common())}")
    print(f"  provenance_quality:{dict(pc.most_common())}")
    print(f"  era:               {dict(ec.most_common())}")
    print(f"  DEPENDS_ON edges total: {edge_total}; per-atom dist: {dict(sorted(dc.items()))}")
    print(f"  atoms with 0 DEPENDS_ON (linkage-conservative; OMITTED not phantom): {dc.get(0,0)}")
    print("=" * 80)


def main():
    apply = os.environ.get("HDLAB_ATOMIZE_APPLY", "0") == "1"
    batch = int(os.environ.get("HDLAB_ATOMIZE_BATCH", "50"))
    # LIMIT fail-safe: APPLY defaults to NO cap (ingest all new specs) so a bulk run never silently caps at 50;
    # dry-run keeps the 50-atom sample default. Explicit HDLAB_ATOMIZE_LIMIT always honored.
    limit = int(os.environ.get("HDLAB_ATOMIZE_LIMIT", "1000000" if apply else "50"))
    mode = "APPLY (ingest, batched, gated)" if apply else "DRY-RUN (no mutation; VET-able sample)"
    print(f"[atomizer] mode={mode} batch={batch} limit={limit}", flush=True)

    ps = PartitionedStore(REPO / "data/substrate_index")
    math_store = ps._store_for(Corpus.MATH)
    all_qids, primitive_targets, cap_serving = build_atom_index(ps)
    print(f"[atomizer] in-store: {len(all_qids)} atoms ({len(primitive_targets)} specific T2/T3 primitive "
          f"targets, {len(cap_serving)} capability-serving primitives) for no-phantom + linkage", flush=True)

    records, dropped = discover()
    print(f"[atomizer] discovered {len(records)} metrics tuples; dropped {len(dropped)}", flush=True)

    # build specs; classify NEW vs UPDATE (queryable content changed) vs SKIP (identical) -- Skunkworks #3.
    # Replaces blind collision-skip: an existing atom whose content_hash differs (e.g. old-atomizer atom with empty
    # key_metrics, or a re-run with new payload) is REFRESHED in place rather than silently skipped.
    specs, updates, skipped_existing = [], [], 0
    for rec in records:
        spec = build_atom_spec(rec, all_qids, primitive_targets, cap_serving)
        # condition 2 re-assert: every DEPENDS_ON target must exist in-store (does not affect content_hash)
        spec["depends_on"] = [d for d in spec["depends_on"] if d in all_qids]
        existing = ps._store_for(spec["corpus"]).get_atom(spec["id"])
        if existing is None:
            specs.append(spec)                                                      # NEW
        else:
            # UPDATE only on a GENUINE queryable-content change (not mere content_hash-absence on legacy atoms) --
            # scopes the refresh to records that actually GAIN queryability (flattened payloads / strengthens edges),
            # avoiding a no-value mass-rewrite of the whole corpus.
            # SCOPED-update classify (Skunkworks amendment): compare ONLY the scoped fields the update touches
            # ({key_metrics, strengthens}); NOT headline/pq/edges (those are preserved -> comparing them would loop).
            em = existing.metadata or {}
            changed = (em.get("key_metrics") != spec["metadata"]["key_metrics"]
                       or (em.get("strengthens_cert") or []) != spec["strengthens"])
            if changed:
                spec["_update"] = True
                spec["_existing_md"] = dict(em)        # carry the existing metadata for the SCOPED merge at apply
                updates.append(spec)                                                # UPDATE: refresh in place
            else:
                skipped_existing += 1                                               # SKIP: no queryable change
    print(f"[atomizer] {len(specs)} new specs, {len(updates)} content-changed refreshes, "
          f"{skipped_existing} unchanged (skipped idempotently)", flush=True)

    summarize(specs, dropped)

    # log dropped (no silent truncation; condition 5)
    drop_log = REPO / "data" / "atomize_experiment_records_dropped.log"
    with open(drop_log, "w", encoding="utf-8") as f:
        for nm, why in dropped:
            f.write(f"{nm}\t{why}\n")
    print(f"[atomizer] dropped log -> {drop_log.relative_to(REPO)} ({len(dropped)} entries)", flush=True)

    if not apply:
        # ALL-DELTAS PREVIEW (Skunkworks amendment): a dry-run must preview EVERY invariant-affecting delta, not just
        # spec-counts -- the prior dry-run HID the +402 edges + the pq-tier changes. Show the actual referent.
        from collections import Counter as _Counter
        from backend.substrate_index.partition import QualifiedAtomId as _QID

        def _strengthens_edge_exists(src_qid, tgt_qid):
            try:
                sq = _QID.parse(src_qid); tq = _QID.parse(tgt_qid)
            except Exception:
                return False
            if sq.corpus != tq.corpus:
                return False
            return (sq.local_id, RelationType.RELATES.value, tq.local_id) in ps._store_for(sq.corpus)._all_relations

        atoms_delta = len(specs)                                       # NEW atoms; UPDATEs (scoped) add 0
        dep_new = sum(len(s["depends_on"]) for s in specs)            # depends_on materialized for NEW specs only
        rel_str_new = sum(1 for s in specs for t in s.get("strengthens", []) if t in all_qids)
        rel_str_upd = sum(1 for s in updates for t in s.get("strengthens", [])
                          if t in all_qids and not _strengthens_edge_exists(s["qid"], t))
        new_pq_dist = _Counter(s["provenance_quality"] for s in specs)
        # pq-tier changes from UPDATEs: SCOPED path PRESERVES pq -> must be 0 (verify against existing metadata)
        upd_pq_changes = [(s["id"], (s.get("_existing_md") or {}).get("provenance_quality"))
                          for s in updates]  # scoped: stored pq stays == existing; 0 changes by construction
        phantom = [t for s in (specs + updates)
                   for t in (list(s["depends_on"]) + list(s.get("strengthens", []))) if t not in all_qids]
        print("[atomizer] === DRY-RUN ALL-DELTAS PREVIEW (invariant impact; Skunkworks report-all-deltas) ===")
        print(f"  atoms delta:      +{atoms_delta} NEW; UPDATEs add 0 (scoped in-place)")
        print(f"  relations delta:  +{dep_new} DEPENDS_ON (NEW specs only) | "
              f"+{rel_str_new + rel_str_upd} RELATES/strengthens ({rel_str_upd} from UPDATEs)")
        print(f"  pq-tier changes from UPDATEs: 0 (SCOPED -- pq+relevance_tier PRESERVED for all {len(updates)})")
        print(f"  NEW-spec pq distribution (method-gate-aware): {dict(new_pq_dist)}")
        print(f"  phantom targets (depends_on+strengthens unresolved): {len(phantom)}")

        sample = specs[:limit]
        out = REPO / "data" / "atomize_experiment_records_dryrun_sample.jsonl"
        with open(out, "w", encoding="utf-8") as f:
            for s in (sample + updates):   # surface UPDATEs too so the refresh + strengthens edges are VET-able
                f.write(json.dumps(dict(action=("UPDATE" if s.get("_update") else "ADD"),
                                        id=s["qid"], name=s["name"], verdict=s["verdict"],
                                        relevance_tier=s["relevance_tier"], provenance_quality=s["provenance_quality"],
                                        era=s["era"], run_mode=s["run_mode"], depends_on=s["depends_on"],
                                        strengthens=s.get("strengthens", []),
                                        scoped_preserves_pq=(s.get("_existing_md") or {}).get("provenance_quality") if s.get("_update") else None,
                                        key_metrics=s["metadata"].get("key_metrics"),
                                        metadata=s["metadata"]), ensure_ascii=False) + "\n")
        print(f"[atomizer] DRY-RUN sample ({len(sample)} ADD + {len(updates)} UPDATE) -> {out.relative_to(REPO)}")
        print("[atomizer] NO substrate mutation. Skunkworks: VET the ALL-DELTAS preview above (atoms/relations/pq-tier/")
        print("           phantom) + the sample (classification + flattened key_metrics + strengthens). Then APPLY.")
        return 0

    # ===== APPLY: per-batch FRESH-LOAD ingest (concurrent-writer SAFE) + per-batch gates (condition 5) =====
    # The store is shared (Testbed PHASE-2 writes math in parallel) and the Store rewrites whole files on flush.
    # To avoid clobbering peer writes AND make progress under contention, each batch: (1) RELOADS the store fresh
    # (picks up peer writes since the last batch), (2) re-does idempotent collision-skip + no-phantom vs the fresh
    # store, (3) adds its atoms, (4) GUARD: if a peer wrote during the ~seconds window, abort+retry this batch
    # (never flush over a peer write), (5) flushes only touched corpora, (6) per-batch HARD-FAIL gates.
    store_files = [REPO / "data/substrate_index" / p for p in
                   ("math/atoms.jsonl", "math/relations.jsonl", "concept/atoms.jsonl", "concept/relations.jsonl")]

    def _fp():
        out = {}
        for f in store_files:
            try:
                st = f.stat(); out[str(f)] = (st.st_mtime_ns, st.st_size)
            except FileNotFoundError:
                out[str(f)] = None
        return out

    to_ingest = specs[:limit]
    RETRIES = 6
    done, contended = 0, 0
    print(f"[atomizer] APPLY (per-batch fresh-load; concurrent-safe) target={len(to_ingest)} batch={batch}", flush=True)

    for i in range(0, len(to_ingest), batch):
        planned = to_ingest[i:i + batch]
        bnum = i // batch + 1
        applied = False
        for attempt in range(RETRIES):
            psb = PartitionedStore(REPO / "data/substrate_index")   # FRESH load: picks up peer writes
            qids_b = {a.qualified_id for a in psb.all_atoms()}
            chunk = []
            for s in planned:
                if psb._store_for(s["corpus"]).get_atom(s["id"]) is not None:
                    continue  # idempotent: already ingested (mine or a re-run)
                s2 = dict(s); s2["depends_on"] = [d for d in s["depends_on"] if d in qids_b]  # no-phantom vs fresh
                chunk.append(s2)
            if not chunk:
                applied = True; break
            pre_t, pre_total = axiom_term(psb)
            b_pre_atoms = len(psb.all_atoms()); b_pre_rels = sum(1 for _ in psb.iter_all_relations())
            touched_rels = set()
            edges = 0
            # NOTE: Store.add_atom AUTO-FLUSHES per atom (store.py); so the os.replace can race here, not only at an
            # explicit flush. Wrap the WHOLE mutation. On a Windows os.replace race (WinError 5; atomic -> file
            # unchanged -> no corruption) abort+retry fresh: the fresh reload collision-skips any atoms that DID land
            # (per-atom auto-flush is granular) and re-adds the rest. Idempotent -> eventually complete, never clobber.
            try:
                for s in chunk:
                    psb._store_for(s["corpus"]).add_atom(Atom(
                        id=s["id"], name=s["name"], corpus=s["corpus"], tier=s["tier"],
                        kind=AtomKind.EXPERIMENT_RECORD, description=s["description"],
                        metadata=s["metadata"], solution_history=tuple()))
                for s in chunk:
                    for tgt in s["depends_on"]:
                        psb.add_relation(s["qid"], RelationType.DEPENDS_ON, tgt, source=SRC_TAG,
                                         note=f"{s['id']} DEPENDS_ON {tgt} (atomizer)")
                        edges += 1; touched_rels.add(s["corpus"])
                    for tgt in s.get("strengthens", []):   # Skunkworks #2: replicates/strengthens RELATES edge
                        if tgt in qids_b and add_strengthens_edge(psb, s["qid"], tgt):  # no-phantom + new-only
                            edges += 1; touched_rels.add(s["corpus"])
                for c in touched_rels:
                    psb._store_for(c)._flush_relations()
            except (PermissionError, OSError) as e:
                print(f"[atomizer] batch {bnum} attempt {attempt+1}: os.replace race ({type(e).__name__}); retry fresh", flush=True)
                continue
            post_t, post_total = axiom_term(psb)
            b_post_atoms = len(psb.all_atoms()); b_post_rels = sum(1 for _ in psb.iter_all_relations())
            landed = all(psb._store_for(s["corpus"]).get_atom(s["id"]) is not None for s in chunk)
            gate_ok = (b_post_atoms == b_pre_atoms + len(chunk) and b_post_rels == b_pre_rels + edges
                       and post_t == pre_t and module_liveness_ok() and landed)
            print(f"[atomizer] batch {bnum}: +{len(chunk)} atoms +{edges} edges | axiom_term={post_t}/{post_total} "
                  f"cap_pres(mod6/6)={module_liveness_ok()} landed={landed} -> {'OK' if gate_ok else 'HARD_FAIL'}",
                  flush=True)
            if not gate_ok:
                print(f"[atomizer] HARD_FAIL at batch {bnum}: invariant violation. STOPPING.")
                return 1
            done += len(chunk); applied = True; break
        if not applied:
            contended += 1
            print(f"[atomizer] batch {bnum}: SKIPPED after {RETRIES} contended attempts; re-invoke picks it up",
                  flush=True)

    # ===== SCOPED-UPDATE pass: refresh ONLY {key_metrics, strengthens, content_hash} IN PLACE (Skunkworks amendment) =====
    # SCOPED: does NOT re-run build_atom_spec -> does NOT recompute provenance_quality/relevance_tier/verdict and does
    # NOT re-extract depends_on edges. It merges ONLY the queryability fields onto the EXISTING atom; cert-classification
    # is PRESERVED (tier changes happen ONLY via a deliberate signed-off cert-review, never as a refresh side-effect).
    # Per-batch invariant: ATOM COUNT UNCHANGED + axiom_term constant + cap_pres + PQ-TIER UNCHANGED (the scoped
    # guarantee) + only RELATES(strengthens) edges added (no depends_on delta). Batched; steady-state empty (idempotent).
    refreshed, refresh_contended = 0, 0
    upd = updates[:limit]
    if upd:
        print(f"[atomizer] SCOPED-UPDATE pass: {len(upd)} records (key_metrics+strengthens only; pq+edges PRESERVED)", flush=True)
    for i in range(0, len(upd), batch):
        ub = upd[i:i + batch]
        unum = i // batch + 1
        ok = False
        for attempt in range(RETRIES):
            psb = PartitionedStore(REPO / "data/substrate_index")           # FRESH load (per batch)
            qids_b = {a.qualified_id for a in psb.all_atoms()}
            todo = []
            for s in ub:
                ex = psb._store_for(s["corpus"]).get_atom(s["id"])
                if ex is None:
                    continue                                                # vanished -> re-invoke re-adds as NEW
                exmd = ex.metadata or {}
                if (exmd.get("key_metrics") == s["metadata"]["key_metrics"]
                        and (exmd.get("strengthens_cert") or []) == s["strengthens"]):
                    continue                                                # already refreshed (peer/prior) -> idempotent
                todo.append((s, ex))
            if not todo:
                ok = True; break
            pre_t, pre_total = axiom_term(psb)
            pre_atoms = len(psb.all_atoms()); pre_rels = sum(1 for _ in psb.iter_all_relations())
            pre_pq = {ex.id: (ex.metadata or {}).get("provenance_quality") for s, ex in todo}  # scoped: pq must NOT move
            touched = set()
            try:
                for s, ex in todo:
                    md = dict(ex.metadata or {})                            # PRESERVE all existing fields...
                    md["key_metrics"] = s["metadata"]["key_metrics"]        # ...override ONLY the scoped 3
                    md["strengthens_cert"] = s["strengthens"]
                    md["content_hash"] = content_hash(s["metadata"]["key_metrics"], md.get("metrics_headline"),
                                                      md.get("verdict"), md.get("relevance_tier"),
                                                      s["strengthens"], (ex.description or "")[:1200])
                    psb._store_for(s["corpus"]).add_atom(Atom(
                        id=ex.id, name=ex.name, corpus=ex.corpus, tier=ex.tier,
                        kind=AtomKind.EXPERIMENT_RECORD, description=ex.description,
                        metadata=md, solution_history=getattr(ex, "solution_history", tuple())),
                        source=SRC_TAG, note="scoped queryability refresh (key_metrics+strengthens; pq+edges preserved)")
                for s, ex in todo:                                          # ONLY the strengthens edge (NO depends_on re-extract)
                    for tgt in s.get("strengthens", []):
                        if tgt in qids_b and add_strengthens_edge(psb, s["qid"], tgt):
                            touched.add(s["corpus"])
                for c in touched:
                    psb._store_for(c)._flush_relations()
            except (PermissionError, OSError) as e:
                print(f"[atomizer] scoped-update batch {unum} attempt {attempt+1}: os.replace race ({type(e).__name__}); retry", flush=True)
                continue
            post_t, post_total = axiom_term(psb)
            post_atoms = len(psb.all_atoms()); post_rels = sum(1 for _ in psb.iter_all_relations())
            post_pq = {ex.id: (psb._store_for(s["corpus"]).get_atom(ex.id).metadata or {}).get("provenance_quality")
                       for s, ex in todo}
            pq_unchanged = (pre_pq == post_pq)                              # SCOPED guarantee: pq tiers did NOT move
            km_ok = all((psb._store_for(s["corpus"]).get_atom(ex.id).metadata or {}).get("key_metrics")
                        == s["metadata"]["key_metrics"] for s, ex in todo)
            gate_ok = (post_atoms == pre_atoms and post_rels >= pre_rels and post_t == pre_t
                       and module_liveness_ok() and pq_unchanged and km_ok)
            print(f"[atomizer] scoped-update batch {unum}: ~{len(todo)} refreshed (+{post_rels-pre_rels} RELATES edges) "
                  f"atoms {pre_atoms}->{post_atoms} axiom_term={post_t}/{post_total} "
                  f"cap_pres(mod6/6)={module_liveness_ok()} pq_unchanged={pq_unchanged} km_ok={km_ok} "
                  f"-> {'OK' if gate_ok else 'HARD_FAIL'}", flush=True)
            if not gate_ok:
                print(f"[atomizer] HARD_FAIL on scoped-update batch {unum}: invariant violation (pq must be preserved). STOPPING.")
                return 1
            refreshed += len(todo); ok = True; break
        if not ok:
            refresh_contended += 1
            print(f"[atomizer] scoped-update batch {unum}: SKIPPED after {RETRIES} contended attempts; re-invoke picks it up",
                  flush=True)

    psf = PartitionedStore(REPO / "data/substrate_index")
    total_exp = sum(1 for a in psf.all_atoms() if str(a.kind.name) == "EXPERIMENT_RECORD")
    print("=" * 80)
    print(f"[atomizer] APPLY DONE: +{done} atoms, ~{refreshed} refreshed this run; "
          f"{contended} batch(es)/{refresh_contended} refresh(es) contended-skipped; "
          f"{total_exp} EXPERIMENT_RECORD atoms total in-store")
    print(f"  per-batch axiom_term + cap_pres(mod6/6) gates passed. Re-invoke to pick up any contended-skipped.")
    print("=" * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
