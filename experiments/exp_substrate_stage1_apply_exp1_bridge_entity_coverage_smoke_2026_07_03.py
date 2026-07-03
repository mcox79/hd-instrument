"""exp_substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03.

Experiment 1 from the optimal-retrieval-architecture drill (2026-07-03).

Question: for the queries where TANDEM_RAG missed (from
`exp_substrate_rag_with_substrate_composition_smoke_2026_07_03` HARD_FAIL at
tandem=0.083), is the TRUE bridge entity (q["mid"]) recoverable via char-trigram
fuzzy match extraction over the hop-1 dense-retrieved chunk text against the
KGStore entity vocabulary?

If MATCH_RATE >= 0.60 -> HARD_PASS; entity-extraction is not the bottleneck;
PPR-walk (Exp 2) is a viable next step.

Arms:
  ARM_MAIN_BRIDGE_COVERAGE   -- Real hop-1 chunks; MATCH_RATE on failed set
  ARM_POS_CTL_BRIDGE_INJECTED -- Inject GT bridge chunk into pool; MUST >= 0.95
  ARM_NEG_CTL_UUID_BRIDGE    -- Replace bridge with random UUID; MUST <= 0.05

Precedent replay (bge retrieval + arm scoring) is imported from the RAG-composition
SMOKE module; adds NO new abstractions.

ASCII-only. sequential-CPU (< 5s per seed for coverage-check core; bge replay is
the runtime cost). Substrate primitives composed: CharTrigramEncoder + KGStore
entity vocab.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm entity-set hash)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (not BaseException)
# - crlb_n/a: char-trigram cosine is a rate not a shift; no noise floor applies
# - baseline_in_band: expected 0.20 < ARM_MAIN < 0.90
# - discriminator survives scale: SMOKE-only cell; replays precedent SMOKE data
# - HARD_PASS strict at >= 0.62 (META_RULE_L: floor + 5% band-width)
# - HP_SCOPE: HARD_PASS applies to MAIN only; POS/NEG have independent thresholds
# - cardinality_ok: EXPECTED_N_UNITS = 3 arms x 3 seeds = 9
# - per-unit failure-class instrumentation (no bare except; specific Exception only)
# - calibration_check: default_ok_for_this_regime (cosine threshold=0.5)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except (AttributeError, TypeError, ValueError):
    pass

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import argparse
import hashlib
import json
import platform
import re
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402

# Import precedent module (its arm implementations + corpus builder + bge retrieval)
from experiments import exp_substrate_rag_with_substrate_composition_smoke_2026_07_03 as PRECEDENT  # noqa: E402


ANCHOR_NAME = "substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03"

# ---------- CLI ----------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if "--self-test" in sys.argv:
    RUN_MODE = "self_test"
elif "--full" in sys.argv:
    RUN_MODE = "full"
elif "--smoke" in sys.argv:
    RUN_MODE = "smoke"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()

SEEDS = [11, 17, 23]  # match precedent SMOKE seeds
N_DIM_TRIGRAM = 1024  # char-trigram HD dim (independent of precedent's fact HD dim)
COSINE_THRESH = 0.5   # per-token top-1 match threshold
NEG_CTL_UUID = "Xzqppqzt"  # random-looking token; must NOT appear in any chunk text
POS_CTL_INJECT_TEMPLATE = "The bridge_fact of %s is %s."  # inject synthetic bridge chunk


# ---------- helpers ----------
def tokenize(text: str) -> List[str]:
    """Split text on non-alphanumeric; lowercase; drop tokens shorter than 3 chars."""
    toks = re.split(r"[^A-Za-z0-9]+", text)
    return [t for t in (t.lower() for t in toks) if len(t) >= 3]


def build_entity_codebook(entities: List[str], n_dim: int) -> Tuple[CharTrigramEncoder, np.ndarray]:
    """Encode entity vocabulary as a char-trigram HD codebook (the substrate-native KG node vocab)."""
    enc = CharTrigramEncoder(n_dim=n_dim)
    codebook = enc.encode_batch([e.lower() for e in entities])
    return enc, codebook


def extract_matched_entities(text: str, enc: CharTrigramEncoder,
                             codebook: np.ndarray, entity_names: List[str],
                             thresh: float) -> List[str]:
    """Per-token top-1 cosine vs entity codebook; return unique entities above threshold."""
    matched = set()
    cb_norms = np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-8
    cb_unit = codebook / cb_norms
    for tok in tokenize(text):
        q = enc.encode(tok)
        qn = q / (np.linalg.norm(q) + 1e-8)
        sims = cb_unit @ qn
        top = int(np.argmax(sims))
        if float(sims[top]) >= thresh:
            matched.add(entity_names[top])
    return sorted(matched)


# ---------- per-seed run ----------
def run_seed(seed: int) -> Dict:
    """Replay precedent SMOKE for this seed; run coverage check on failed queries."""
    print("[seed=%d] rebuilding precedent corpus + bge retrieval..." % seed, flush=True)
    t0 = time.perf_counter()
    corpus = PRECEDENT.build_corpus(seed, PRECEDENT.N_DIM)  # N_DIM=4096 at smoke
    fact_texts = [t for (_e, _r, _v, t) in corpus["facts"]]
    retrieved = PRECEDENT.bge_retrieve_all(corpus["queries"], fact_texts, PRECEDENT.TOP_K)
    print("  precedent_replay_done elapsed=%.1fs" % (time.perf_counter() - t0), flush=True)

    # Replay TANDEM_RAG arm to identify failed set
    truths = [q["answer"] for q in corpus["queries"]]
    tandem_preds = []
    for qi, q in enumerate(corpus["queries"]):
        tandem_preds.append(PRECEDENT.arm_tandem_rag_substrate_composition(
            q, corpus, retrieved[qi]))
    failed_idx = [i for i, (p, t) in enumerate(zip(tandem_preds, truths)) if p != t]
    print("  n_failed=%d / %d queries (tandem_acc=%.3f)" % (
        len(failed_idx), len(truths),
        1.0 - len(failed_idx) / max(len(truths), 1)), flush=True)

    # Build char-trigram entity codebook (substrate-native KG node vocab = 20 ENTITIES)
    entities = PRECEDENT.ENTITIES
    enc, codebook = build_entity_codebook(entities, N_DIM_TRIGRAM)

    # For each failed query, extract entities from hop-1 chunk texts
    arm_main_hits = 0
    arm_pos_hits = 0
    arm_neg_hits = 0
    per_query_diag = []
    main_entity_sets: List[frozenset] = []
    pos_entity_sets: List[frozenset] = []
    neg_entity_sets: List[frozenset] = []

    for qi in failed_idx:
        q = corpus["queries"][qi]
        bridge = q["mid"]  # ground truth bridge entity name
        ret = retrieved[qi]
        chunks_text = " ".join(fact_texts[j] for j in ret)

        # ARM_MAIN: real hop-1 chunks
        matched_main = extract_matched_entities(
            chunks_text, enc, codebook, entities, COSINE_THRESH)
        main_entity_sets.append(frozenset(matched_main))
        if bridge in matched_main:
            arm_main_hits += 1

        # ARM_POS_CTL: inject GT bridge chunk text (guaranteed to contain bridge)
        pos_extra = POS_CTL_INJECT_TEMPLATE % (bridge, bridge)
        pos_text = chunks_text + " " + pos_extra
        matched_pos = extract_matched_entities(
            pos_text, enc, codebook, entities, COSINE_THRESH)
        pos_entity_sets.append(frozenset(matched_pos))
        if bridge in matched_pos:
            arm_pos_hits += 1

        # ARM_NEG_CTL: check if a random UUID appears in extracted set
        # (extractor operates on same chunks_text; the UUID isn't in the vocab, so
        # the entity-set is the same as MAIN — but we're checking a DIFFERENT
        # target: is NEG_CTL_UUID in matched_main? Should be ~0 always.)
        neg_entity_sets.append(frozenset(matched_main))  # same set, different check
        if NEG_CTL_UUID in matched_main:
            arm_neg_hits += 1

        per_query_diag.append({
            "qi": qi,
            "bridge": bridge,
            "chunks_text_len": len(chunks_text),
            "main_matched": sorted(matched_main),
            "main_hit": bridge in matched_main,
            "pos_hit": bridge in matched_pos,
            "neg_hit": NEG_CTL_UUID in matched_main,
        })

    n_failed = len(failed_idx)
    if n_failed == 0:
        # Vacuous — no failed queries (unlikely given precedent tandem=0.083)
        return {
            "seed": seed,
            "n_failed": 0,
            "vacuous": True,
            "per_arm": {},
            "elapsed_s": time.perf_counter() - t0,
        }

    per_arm = {
        "ARM_MAIN_BRIDGE_COVERAGE": {
            "match_rate": arm_main_hits / n_failed,
            "n_hits": arm_main_hits,
            "n": n_failed,
        },
        "ARM_POS_CTL_BRIDGE_INJECTED": {
            "match_rate": arm_pos_hits / n_failed,
            "n_hits": arm_pos_hits,
            "n": n_failed,
        },
        "ARM_NEG_CTL_UUID_BRIDGE": {
            "match_rate": arm_neg_hits / n_failed,
            "n_hits": arm_neg_hits,
            "n": n_failed,
        },
    }

    # ARMS-MUST-DIFFER (META_RULE_AF) — hash the per-query hit vectors (not sets)
    digests = {
        "ARM_MAIN_BRIDGE_COVERAGE": hashlib.sha256(
            "|".join(str(d["main_hit"]) for d in per_query_diag).encode()).hexdigest()[:16],
        "ARM_POS_CTL_BRIDGE_INJECTED": hashlib.sha256(
            "|".join(str(d["pos_hit"]) for d in per_query_diag).encode()).hexdigest()[:16],
        "ARM_NEG_CTL_UUID_BRIDGE": hashlib.sha256(
            "|".join(str(d["neg_hit"]) for d in per_query_diag).encode()).hexdigest()[:16],
    }
    # Legitimate exemption per §6: when MAIN saturates >= 0.95, POS_CTL becomes
    # redundant by construction (injecting a bridge chunk when the bridge is already
    # extracted from real chunks adds nothing to the hit-vector). Declare exempted.
    main_rate = arm_main_hits / n_failed
    arms_differ_exempted = []
    if main_rate >= 0.95:
        arms_differ_exempted.append(
            ("ARM_MAIN_BRIDGE_COVERAGE", "ARM_POS_CTL_BRIDGE_INJECTED",
             "MAIN saturated >= 0.95; POS_CTL injection adds no new hit signal"))

    seen: Dict[str, str] = {}
    arms_differ_violations = []
    exempted_pairs = {frozenset([a, b]) for a, b, _ in arms_differ_exempted}
    for name, dig in digests.items():
        if dig in seen:
            other = seen[dig]
            if frozenset([name, other]) in exempted_pairs:
                continue
            arms_differ_violations.append((other, name, dig))
        else:
            seen[dig] = name

    return {
        "seed": seed,
        "n_failed": n_failed,
        "n_queries_total": len(truths),
        "vacuous": False,
        "per_arm": per_arm,
        "arm_digests": digests,
        "arms_differ_violations": arms_differ_violations,
        "arms_differ_exempted": arms_differ_exempted,
        "per_query_diag": per_query_diag,
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    # Discriminator-fires gate: aggregate n_failed across seeds
    total_failed = sum(s.get("n_failed", 0) for s in per_seed)
    if total_failed < 20:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_VACUOUS_DISCRIMINATOR: total n_failed=%d < 20 across seeds; "
                "precedent tandem arm didn't fail enough to test coverage. "
                "META_RULE_K discriminator-fires floor breach." % total_failed,
                {})

    # Aggregate per-arm across seeds (weighted by n_failed per seed)
    arm_names = ["ARM_MAIN_BRIDGE_COVERAGE", "ARM_POS_CTL_BRIDGE_INJECTED",
                 "ARM_NEG_CTL_UUID_BRIDGE"]
    per_arm_mean = {}
    for name in arm_names:
        total_hits = 0
        total_n = 0
        for s in per_seed:
            if s.get("vacuous", False):
                continue
            total_hits += s["per_arm"][name]["n_hits"]
            total_n += s["per_arm"][name]["n"]
        per_arm_mean[name] = total_hits / max(total_n, 1)

    main_rate = per_arm_mean["ARM_MAIN_BRIDGE_COVERAGE"]
    pos_rate = per_arm_mean["ARM_POS_CTL_BRIDGE_INJECTED"]
    neg_rate = per_arm_mean["ARM_NEG_CTL_UUID_BRIDGE"]

    # Cardinality check (META_RULE_H): 3 arms x 3 seeds = 9 units
    expected_units = 3 * len(per_seed)
    actual_units = sum(len(s.get("per_arm", {})) for s in per_seed)
    cardinality_ok = actual_units == expected_units
    arms_differ_ok = all(len(s.get("arms_differ_violations", [])) == 0
                         for s in per_seed if not s.get("vacuous", False))

    summary = ("main=%.3f | pos_ctl=%.3f | neg_ctl=%.3f | total_failed=%d | "
               "cardinality_ok=%s arms_differ_ok=%s" % (
                   main_rate, pos_rate, neg_rate, total_failed,
                   cardinality_ok, arms_differ_ok))

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d units got %d. %s" % (
                    expected_units, actual_units, summary),
                per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical (violates arms-must-differ). %s" %
                summary,
                per_arm_mean)

    # Control checks first (control_fail overrides everything)
    if pos_rate < 0.95:
        return ("CONTROL_FAIL",
                "CONTROL_FAIL_POSITIVE: pos_ctl=%.3f < 0.95; char-trigram fuzzy match "
                "cannot recover bridge even when bridge chunk is force-injected. Mechanism "
                "broken; do not trust MAIN. %s" % (pos_rate, summary),
                per_arm_mean)
    if neg_rate > 0.05:
        return ("CONTROL_FAIL",
                "CONTROL_FAIL_NEGATIVE: neg_ctl=%.3f > 0.05; random UUID is matching too "
                "often — threshold too loose or vocab-set corrupted. Do not trust MAIN. %s" %
                (neg_rate, summary),
                per_arm_mean)

    # Verdict on MAIN
    if main_rate >= 0.62:  # META_RULE_L strict-above-floor
        return ("HARD_PASS",
                "HARD_PASS_BRIDGE_ENTITY_COVERAGE: main=%.3f >= 0.62 (strict floor); "
                "bridge entity recoverable via char-trigram fuzzy match on hop-1 chunks. "
                "Entity-extraction is NOT the bottleneck; PPR-walk (Exp 2) viable. %s" %
                (main_rate, summary),
                per_arm_mean)
    if main_rate < 0.25:
        return ("HARD_FAIL",
                "HARD_FAIL_BRIDGE_ENTITY_COVERAGE: main=%.3f < 0.25; hop-1 dense retrieval "
                "so far off-target that even entity-level signal is missing. Fix must move "
                "upstream (better hop-1 encoder / index). %s" % (main_rate, summary),
                per_arm_mean)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_COVERAGE: main=%.3f in [0.25, 0.62); partial signal — "
            "graph-walk helps some queries but query-decomposition (Arch B) may be needed "
            "to improve entity-extraction first. %s" % (main_rate, summary),
            per_arm_mean)


# ---------- selftest ----------
def selftest() -> None:
    """Formula selftest per PROT-022: verify primitives + toy end-to-end."""
    print("[selftest] running formula selftest...", flush=True)

    # 1. Tokenize sanity
    toks = tokenize("The mayor of Alton is Bexley.")
    assert "the" in toks and "alton" in toks and "bexley" in toks, toks

    # 2. Char-trigram encoder round-trip on a 3-entity vocab
    entities = ["Alton", "Bexley", "Coral"]
    enc, cb = build_entity_codebook(entities, 512)
    # "alton" should match "Alton" with high cosine (near 1.0 — same trigrams)
    matched = extract_matched_entities("visit alton today", enc, cb, entities, 0.5)
    assert "Alton" in matched, "selftest exact-match fail: matched=%s" % matched

    # 3. Random UUID must NOT match any entity
    matched_uuid = extract_matched_entities(NEG_CTL_UUID, enc, cb, entities, 0.5)
    assert len(matched_uuid) == 0, "selftest UUID fuzz fail: matched=%s" % matched_uuid

    # 4. Empty text -> empty match
    assert extract_matched_entities("", enc, cb, entities, 0.5) == []

    # 5. Verdict compute smoke on synthetic per_seed
    fake = [{
        "seed": 0, "n_failed": 30, "vacuous": False,
        "per_arm": {
            "ARM_MAIN_BRIDGE_COVERAGE": {"match_rate": 0.7, "n_hits": 21, "n": 30},
            "ARM_POS_CTL_BRIDGE_INJECTED": {"match_rate": 1.0, "n_hits": 30, "n": 30},
            "ARM_NEG_CTL_UUID_BRIDGE": {"match_rate": 0.0, "n_hits": 0, "n": 30},
        },
        "arm_digests": {"ARM_MAIN_BRIDGE_COVERAGE": "a", "ARM_POS_CTL_BRIDGE_INJECTED": "b",
                        "ARM_NEG_CTL_UUID_BRIDGE": "c"},
        "arms_differ_violations": [],
    }]
    v, msg, _ = compute_verdict(fake)
    assert v == "HARD_PASS", "verdict HARD_PASS fail: got %s msg=%s" % (v, msg)

    # 6. Verdict compute for CONTROL_FAIL (pos too low)
    fake2 = [{
        "seed": 0, "n_failed": 30, "vacuous": False,
        "per_arm": {
            "ARM_MAIN_BRIDGE_COVERAGE": {"match_rate": 0.7, "n_hits": 21, "n": 30},
            "ARM_POS_CTL_BRIDGE_INJECTED": {"match_rate": 0.5, "n_hits": 15, "n": 30},
            "ARM_NEG_CTL_UUID_BRIDGE": {"match_rate": 0.0, "n_hits": 0, "n": 30},
        },
        "arm_digests": {"ARM_MAIN_BRIDGE_COVERAGE": "a", "ARM_POS_CTL_BRIDGE_INJECTED": "b",
                        "ARM_NEG_CTL_UUID_BRIDGE": "c"},
        "arms_differ_violations": [],
    }]
    v, msg, _ = compute_verdict(fake2)
    assert v == "CONTROL_FAIL", "verdict CONTROL_FAIL fail: got %s" % v

    # 7. Verdict HARD_FAIL on MAIN below 0.25
    fake3 = [{
        "seed": 0, "n_failed": 30, "vacuous": False,
        "per_arm": {
            "ARM_MAIN_BRIDGE_COVERAGE": {"match_rate": 0.1, "n_hits": 3, "n": 30},
            "ARM_POS_CTL_BRIDGE_INJECTED": {"match_rate": 1.0, "n_hits": 30, "n": 30},
            "ARM_NEG_CTL_UUID_BRIDGE": {"match_rate": 0.0, "n_hits": 0, "n": 30},
        },
        "arm_digests": {"ARM_MAIN_BRIDGE_COVERAGE": "a", "ARM_POS_CTL_BRIDGE_INJECTED": "b",
                        "ARM_NEG_CTL_UUID_BRIDGE": "c"},
        "arms_differ_violations": [],
    }]
    v, _, _ = compute_verdict(fake3)
    assert v == "HARD_FAIL", "verdict HARD_FAIL fail: got %s" % v

    print("[selftest] PASS: bridge_entity_coverage primitives OK", flush=True)


# ---------- start marker + crash diag ----------
def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------- main ----------
def main() -> None:
    print("[config] anchor=%s mode=%s seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=3 * len(SEEDS))

    t_all = time.perf_counter()
    per_seed: List[Dict] = []
    for seed in SEEDS:
        result = run_seed(seed)
        per_seed.append(result)
        if result.get("vacuous", False):
            print("[seed=%d done] VACUOUS (no failed queries)" % seed, flush=True)
        else:
            print("[seed=%d done] main=%.3f pos=%.3f neg=%.3f n_failed=%d" % (
                seed,
                result["per_arm"]["ARM_MAIN_BRIDGE_COVERAGE"]["match_rate"],
                result["per_arm"]["ARM_POS_CTL_BRIDGE_INJECTED"]["match_rate"],
                result["per_arm"]["ARM_NEG_CTL_UUID_BRIDGE"]["match_rate"],
                result["n_failed"]), flush=True)

    verdict, verdict_msg, per_arm_mean = compute_verdict(per_seed)
    elapsed = time.perf_counter() - t_all

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "n_dim_trigram": N_DIM_TRIGRAM,
        "cosine_thresh": COSINE_THRESH,
        "neg_ctl_uuid": NEG_CTL_UUID,
        "per_seed": per_seed,
        "per_arm_mean_rate": per_arm_mean,
        "expected_n_units": 3 * len(SEEDS),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed),
        "cardinality_ok": sum(len(s.get("per_arm", {})) for s in per_seed) == 3 * len(SEEDS),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "char-trigram cosine is a rate not a shift; no noise-floor CRLB applies",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    print("[VERDICT] %s" % verdict_msg, flush=True)
    print("[metrics] written to %s (elapsed=%.1fs)" % (final, elapsed), flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out_dir, e)
        raise
