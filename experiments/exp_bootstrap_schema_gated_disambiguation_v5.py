# CELL-TEMPLATE (schema-gated architecture test; NOT a queue-dispatch cell). Tests the SCHEMA-GATED
# mechanism (Tse schema-gating) the bootstrap conclusion rests on -- do NOT assume it, TEST it. NO LLM.
# The fair v4 test showed SCHEMA-BLIND vocab-tagging caps at 0.72 (processes share topic vocab). The
# untested brain-faithful mechanism: use the SEED-SCHEMA's DIRECTIONAL structure to disambiguate the
# process. The extractor gives (entity, DIRECTION): produced=CREATE, consumed=DESTROY, moved=MOVE.
# The hand-schema knows which process CONSUMES vs PRODUCES vs MOVES which entity (respiration CONSUMES
# oxygen; photosynthesis PRODUCES oxygen -- directional). If (entity,direction) is UNIQUE to one
# process -> confident schema-gated tag (glucose produced -> photosynthesis; ash produced ->
# combustion). If shared (CO2 produced = combustion+respiration) -> ambiguous/unresolved. Then EXTEND:
# a schema-resolvable anchor in a sentence gates NEW entities (not in the schema) to that process.
#
# This is NOT a fade test -- the schema is load-bearing BY DESIGN (schema-GATED learning: seed
# disambiguates + gates, reading EXTENDS within it). FAIRNESS (rule c, USER-emphatic): no-leak (DEV
# NEVER read; schema = hand-KB seed, authored blind); can-fail (if schema-gating doesn't beat 0.72 on
# resolvable cases, or the resolvable fraction is tiny, or new-entity extension is wrong -> HARD_FAIL);
# the EXTENSION must add genuinely-NEW entities (not already in the schema).
# Load-bearing subset: no bare except; tmp_replace; deterministic; self-test builds the REAL schema
# index + resolves real examples; crlb_n/a. See preregs/2026-08-11_schema_gated_disambiguation_v5.md.
"""exp_bootstrap_schema_gated_disambiguation_v5 -- does the seed schema's DIRECTIONAL structure
disambiguate the process (beating the 0.72 schema-blind vocab baseline) and gate correct extension to
NEW entities? Measures: schema-gated tag accuracy on resolvable cases (hand-check), the resolvable
fraction, and new-entity extension correctness (hand-check). Modes: --self-test / (no flag)=the run.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

ANCHOR_NAME = "bootstrap_schema_gated_disambiguation_v5"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import _load_kb, _norm_toks  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import _load_split  # noqa: E402
from experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision import (  # noqa: E402
    extract_facts_strict, _load_or_build_frontend, _singularize,
)
from experiments.exp_stated_entity_fate_reading_extractor_v1 import (  # noqa: E402
    _SCI_TOPIC, _WORD, FATE_VERB_LEXICON, _propara_train_sentences,
)

EFFECTS = ("CREATE", "MOVE", "DESTROY")
FATE_LABEL = {"CREATE": "PRODUCED", "DESTROY": "CONSUMED", "MOVE": "MOVED"}
SCHEMA_BLIND_BASELINE = 0.72   # CITED@exp_bootstrap_passage_context_binding_fade_v4 (and v2 0.7167)
SCHEMA_GATED_TARGET = 0.85


# ============================================================================ schema directional index
def _build_schema(procs) -> Tuple[Dict[Tuple[str, str], Set[str]], Set[str]]:
    """schema_idx[(entity_tok, fate)] -> set of processes that have that entity in the matching
    DIRECTIONAL role (consumes->DESTROY, produces->CREATE, moves->MOVE). schema_ent = all schema
    entity tokens (any direction). Purely from the hand-KB seed (blind to test gold)."""
    idx: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
    ent: Set[str] = set()
    for pname, d in procs.items():
        for fate, role in (("DESTROY", "consumes"), ("CREATE", "produces"), ("MOVE", "moves")):
            for w in d.get(role, []):
                for t in _norm_toks(w):
                    if len(t) > 2:
                        idx[(t, fate)].add(pname)
                        ent.add(t)
    return idx, ent


def _variants(entity_head: str) -> Set[str]:
    v = set(_norm_toks(entity_head))
    v.add(_singularize(entity_head))
    v.add(entity_head)
    return {t for t in v if len(t) > 2}


def _resolve(entity_head: str, fate: str, idx, ent) -> Tuple[Set[str], bool]:
    """Return (processes matching (entity,direction), entity_is_in_schema_for_any_direction)."""
    procs_hit: Set[str] = set()
    in_schema = False
    for t in _variants(entity_head):
        if (t, fate) in idx:
            procs_hit |= idx[(t, fate)]
        for f2 in EFFECTS:
            if (t, f2) in idx:
                in_schema = True
    return procs_hit, in_schema


# ============================================================================ reading (no-leak)
def _reading_sentences(max_simplewiki: int, dev_sentences: Set[str]):
    for s in _propara_train_sentences():
        s = s.strip()
        if s and s not in dev_sentences:
            yield s, "propara_train"
    n = 0
    with open(SIMPLEWIKI_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not (12 <= len(s) <= 240):
                continue
            if not _SCI_TOPIC.search(s):
                continue
            toks = set(_WORD.findall(s.lower()))
            if not any(lemma_verb(t) in FATE_VERB_LEXICON for t in toks):
                continue
            if s in dev_sentences:
                continue
            yield s, "simplewiki"
            n += 1
            if n >= max_simplewiki:
                break


# ============================================================================ run
def run(max_simplewiki: int = 8000, seed: int = 20260811) -> Dict:
    t0 = time.time()
    kb = _load_kb()
    procs = kb["processes"]
    idx, schema_ent = _build_schema(procs)
    n_uniq = sum(1 for k, v in idx.items() if len(v) == 1)
    n_shared = sum(1 for k, v in idx.items() if len(v) > 1)
    print(f"[schema] {len(schema_ent)} entity tokens; {len(idx)} (entity,dir) keys; unique={n_uniq} "
          f"shared={n_shared} (schema resolvable frac={round(n_uniq/max(len(idx),1),3)})", flush=True)

    dev_sentences = {s.strip() for para in _load_split("dev") for s in para["sentence_texts"]}
    gen = _load_or_build_frontend()

    # classify every extracted fact + do sentence-level schema-anchor extension
    n_facts = 0
    cls_counts = Counter()          # RESOLVABLE_DIRECT / SHARED / NEW_ENTITY / IN_SCHEMA_OTHER_DIR
    resolvable_samples: List[Dict] = []
    extension_samples: List[Dict] = []
    n_ext_correct_candidates = 0
    rng = random.Random(seed)
    added_new_facts: Set[Tuple[str, str, str]] = set()  # (new_entity, process, fate) genuinely-new

    for s, src in _reading_sentences(max_simplewiki, dev_sentences):
        facts = extract_facts_strict(gen, s)
        if not facts:
            continue
        # per-fact schema resolution
        fres = []
        for f in facts:
            ph, ins = _resolve(f["entity_head"], f["fate"], idx, schema_ent)
            n_facts += 1
            if len(ph) == 1:
                cls = "RESOLVABLE_DIRECT"
            elif len(ph) > 1:
                cls = "SHARED_AMBIGUOUS"
            elif not ins:
                cls = "NEW_ENTITY"
            else:
                cls = "IN_SCHEMA_OTHER_DIR"
            cls_counts[cls] += 1
            fres.append((f, ph, ins, cls))
            if cls == "RESOLVABLE_DIRECT":
                proc = next(iter(ph))
                row = {"entity": f["entity_head"], "fate_label": FATE_LABEL[f["fate"]],
                       "schema_gated_process": proc, "sentence": s, "src": src}
                if len(resolvable_samples) < 120:
                    resolvable_samples.append(row)
                elif rng.random() < 0.03:
                    resolvable_samples[rng.randrange(120)] = row
        # sentence anchor: unique process among the sentence's RESOLVABLE_DIRECT facts
        anchor_procs = {next(iter(ph)) for (_f, ph, _ins, cls) in fres if cls == "RESOLVABLE_DIRECT"}
        if len(anchor_procs) == 1:
            P = next(iter(anchor_procs))
            for (f, ph, ins, cls) in fres:
                if cls == "NEW_ENTITY":  # genuinely-new entity gated to the anchor's process
                    key = (f["entity_head"], P, f["fate"])
                    if key not in added_new_facts:
                        added_new_facts.add(key)
                        n_ext_correct_candidates += 1
                        row = {"new_entity": f["entity_head"], "fate_label": FATE_LABEL[f["fate"]],
                               "gated_to_process": P, "anchor_entities": sorted(
                                   {af["entity_head"] for (af, aph, _a, ac) in fres if ac == "RESOLVABLE_DIRECT"}),
                               "sentence": s, "src": src}
                        if len(extension_samples) < 100:
                            extension_samples.append(row)
                        elif rng.random() < 0.05:
                            extension_samples[rng.randrange(100)] = row

    n_resolvable = cls_counts["RESOLVABLE_DIRECT"]
    n_shared_amb = cls_counts["SHARED_AMBIGUOUS"]
    n_new = cls_counts["NEW_ENTITY"]
    resolvable_frac = round(n_resolvable / max(n_facts, 1), 4)
    shared_frac = round(n_shared_amb / max(n_facts, 1), 4)
    new_frac = round(n_new / max(n_facts, 1), 4)
    print(f"[classify] n_facts={n_facts} RESOLVABLE_DIRECT={n_resolvable} ({resolvable_frac}) "
          f"SHARED_AMBIGUOUS={n_shared_amb} ({shared_frac}) NEW_ENTITY={n_new} ({new_frac}) "
          f"IN_SCHEMA_OTHER_DIR={cls_counts['IN_SCHEMA_OTHER_DIR']}", flush=True)
    print(f"[extension] genuinely-new (entity,process,fate) facts gated by a schema anchor = "
          f"{len(added_new_facts)}", flush=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    d1 = os.path.join(OUTPUT_DIR, "_resolvable_tags_for_handcheck.json")
    with open(d1, "w", encoding="utf-8") as f:
        json.dump({"n_resolvable": n_resolvable, "sample": resolvable_samples}, f, indent=2)
    d2 = os.path.join(OUTPUT_DIR, "_extension_new_entities_for_handcheck.json")
    with open(d2, "w", encoding="utf-8") as f:
        json.dump({"n_extension": len(added_new_facts), "sample": extension_samples}, f, indent=2)
    print(f"[dump] {len(resolvable_samples)} resolvable tags -> {d1}; {len(extension_samples)} extension -> {d2}", flush=True)

    verdict = "PENDING_HANDCHECK"
    verdict_msg = (
        f"[SCHEMA-GATED disambiguation, NO LLM, no-leak DEV-never-read] schema resolvable-frac(keys)="
        f"{round(n_uniq/max(len(idx),1),3)}; READ facts n={n_facts}: RESOLVABLE_DIRECT={resolvable_frac} "
        f"SHARED_AMBIGUOUS={shared_frac} NEW_ENTITY={new_frac}; genuinely-new facts gated by anchor="
        f"{len(added_new_facts)}; schema-gated tag accuracy on resolvable cases PENDING hand-check "
        f"(vs schema-blind {SCHEMA_BLIND_BASELINE}, target >{SCHEMA_GATED_TARGET}); new-entity extension "
        f"correctness PENDING hand-check")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "schema_gated", "anchor_name": ANCHOR_NAME,
        "mechanism": "schema-GATED directional disambiguation (entity,direction -> unique process via the "
                     "hand-KB consumes/produces/moves structure) + anchor-gated NEW-entity extension; NOT a fade test",
        "fairness": {"no_leak_dev_never_read": True, "schema_is_blind_authored_seed": True,
                     "can_fail": "HARD_FAIL if resolvable-case accuracy <= schema-blind 0.72, or resolvable "
                                 "fraction tiny, or extension wrong", "extension_must_be_new_entities": True},
        "schema": {"n_entity_tokens": len(schema_ent), "n_entity_dir_keys": len(idx),
                   "n_unique_to_one_process": n_uniq, "n_shared": n_shared,
                   "schema_key_resolvable_frac": round(n_uniq / max(len(idx), 1), 4)},
        "read_classification": {"n_facts": n_facts, "n_resolvable_direct": n_resolvable,
                                "resolvable_fraction": resolvable_frac, "n_shared_ambiguous": n_shared_amb,
                                "shared_fraction": shared_frac, "n_new_entity": n_new, "new_fraction": new_frac,
                                "n_in_schema_other_dir": cls_counts["IN_SCHEMA_OTHER_DIR"]},
        "extension": {"n_genuinely_new_facts_gated": len(added_new_facts)},
        "design_gate": {"resolvable_handcheck_dump": d1, "extension_handcheck_dump": d2,
                        "schema_blind_baseline": SCHEMA_BLIND_BASELINE, "target": SCHEMA_GATED_TARGET,
                        "note": "resolvable-case tag accuracy + extension correctness hand-checked by operator"},
        "bands": {"SCHEMA_BLIND_BASELINE": SCHEMA_BLIND_BASELINE, "SCHEMA_GATED_TARGET": SCHEMA_GATED_TARGET},
    }


# ============================================================================ I/O
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}
    kb = _load_kb()
    procs = kb["processes"]
    idx, ent = _build_schema(procs)
    # (1) directional disambiguation: glucose PRODUCED unique -> photosynthesis; ash PRODUCED -> combustion
    ph, ins = _resolve("glucose", "CREATE", idx, ent)
    assert ph == {"photosynthesis"}, ph
    assert _resolve("ash", "CREATE", idx, ent)[0] == {"combustion"}
    assert _resolve("wood", "DESTROY", idx, ent)[0] == {"combustion"}
    # (2) shared -> ambiguous (>1 process)
    assert len(_resolve("dioxide", "CREATE", idx, ent)[0]) > 1
    assert len(_resolve("oxygen", "DESTROY", idx, ent)[0]) > 1
    # (3) genuinely-new entity -> not in schema
    ph_new, ins_new = _resolve("zorblax", "CREATE", idx, ent)
    assert ph_new == set() and not ins_new, (ph_new, ins_new)
    out["checks"]["resolve"] = {"glucose_CREATE": sorted(ph), "dioxide_shared": True, "new_entity_absent": True}
    print("[self-test] directional resolve OK (glucose->photosynthesis unique; CO2/oxygen shared; new absent)", flush=True)

    # (4) real extractor + schema gate on a canonical sentence (real_code_path)
    gen = _load_or_build_frontend()
    facts = extract_facts_strict(gen, "Photosynthesis produces glucose and oxygen.")
    got = {(f["entity_head"], f["fate"]) for f in facts}
    # glucose CREATE should resolve to photosynthesis uniquely
    res = {e: _resolve(e, fa, idx, ent)[0] for (e, fa) in got}
    assert any(v == {"photosynthesis"} for v in res.values()), res
    out["checks"]["real_gate"] = {k: sorted(v) for k, v in res.items()}
    print(f"[self-test] real extractor + schema gate OK: {out['checks']['real_gate']}", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = "SELFTEST_PASS: directional disambiguation (unique/shared/new) + real extractor gate OK"
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--max-simplewiki", type=int, default=8000)
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test else "schema_gated"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)
    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run(max_simplewiki=args.max_simplewiki)
        _write_metrics(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
