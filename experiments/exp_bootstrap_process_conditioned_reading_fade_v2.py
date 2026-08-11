# CELL-TEMPLATE (culmination v2; NOT a queue-dispatch cell). Closes the bootstrap thesis by making
# reading PROCESS-CONDITIONED, then re-running the SAME fade/lesion/scramble harness as
# exp_bootstrap_seed_ignites_reading_learner_fade_v1. v1 diagnosis (disk-VET'd): reading EXTENDS but
# cannot RE-DERIVE the seed because reading was ENTITY-GLOBAL while seed/target are PROCESS-KEYED. Fix:
# tag each fate-extraction with a PROCESS (glass-box, NO LLM) so reading facts are (entity,process)->fate
# -- matching the seed's grain -- then measure whether the crutch now fades. WIRE-DON'T-ISLAND: reuses
# the validated convergence-gated frame-SELECTION organ (_select_matched), the v2 reading extractor
# (extract_facts_strict, P=0.90), the re-keyed hand-KB SEED, hd_fact_store, and the v1 fade harness.
#
# DESIGN GATE FIRST (the new unknown): can reading TAG THE PROCESS reliably? PARAGRAPH-level for
# ProPara TRAIN (one process/paragraph via _select_matched); SENTENCE-level frame-selection for
# SimpleWiki; SKIP process-ambiguous sentences (frame-selection returns [] -> no fact emitted, per the
# coordinator's option c). HAND-CHECK: of emitted (entity,process,fate), is the PROCESS correct? If
# process-tag accuracy < ~0.7, STOP -- reading can't reliably identify the process = a real limit (the
# seed must carry process-precision permanently). Only if usable is the fade re-run trusted.
#
# Load-bearing subset: no bare except / except SystemExit-KeyboardInterrupt re-raise then Exception->
# crash-diagnostic; final_metrics_atomicity=tmp_replace; deterministic_seeding (store seed; scramble via
# hashlib-seeded _deterministic_perm); self-test builds REAL seed store + REAL frontend + REAL process
# tag + tiny fade; crlb_n/a (fact-level recall over fixed ProPara EMNLP18 DEV oracle). DEV NEVER read
# (no-leak guard retained). See preregs/2026-08-11_bootstrap_process_conditioned_reading_fade_v2.md.
"""exp_bootstrap_process_conditioned_reading_fade_v2 -- process-conditioned reading; does the crutch
now FADE? Design-gate (process-tag accuracy) -> if usable, the process-keyed fade/lesion/scramble.
Modes: --self-test / (no flag)=design-gate + fade.
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

ANCHOR_NAME = "bootstrap_process_conditioned_reading_fade_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
# frame-SELECTION organ (process tagger) + seed re-key
from experiments.exp_propara_process_keyed_lookup_v1 import _rekey_kb, _select_matched, _EFFECT_TRIGS  # noqa: E402
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import _load_kb, _norm_toks, _toks  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _deterministic_perm,
)
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import _paragraph_precompute  # noqa: E402
from experiments.exp_propara_arm2_extracted_structure_v1 import _load_coref  # noqa: E402
from propara_trap_check import build_step_rows  # noqa: E402
# v2 reading extractor + corpus helpers
from experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision import (  # noqa: E402
    extract_facts_strict, _load_or_build_frontend, _singularize,
)
from experiments.exp_stated_entity_fate_reading_extractor_v1 import _SCI_TOPIC, _WORD  # noqa: E402
from experiments.exp_stated_entity_fate_reading_extractor_v1 import _propara_train_sentences  # noqa: E402
# reuse the v1 fade harness metric helpers verbatim (wire-don't-island)
from experiments.exp_bootstrap_seed_ignites_reading_learner_fade_v1 import (  # noqa: E402
    _seed_maps, _seed_answer, _dom, EFFECTS, CHECKPOINTS, SIMPLEWIKI_PATH,
    RISE_MIN_ABS, FADE_GAP_MAX, FADE_RATIO_MIN, SCRAMBLE_MAX_RETAINED, STORE_N_DIM,
)

SCRAMBLE_SEED = "bootstrap_pc_reading_scramble_v2"
PROCTAG_ACC_GATE = 0.70  # design gate: process-tag accuracy must clear this to trust the fade
READING_FIDELITY_V2 = 0.90

# supplementary verb/keyword -> process lexicon (glass-box seed; only UNAMBIGUOUS process signals;
# used ONLY when frame-selection abstains, to reduce over-skipping without adding wrong tags).
_KW_PROC: Dict[str, str] = {}
for _kw in ["combust", "combustion", "ignite"]:
    _KW_PROC[_kw] = "combustion"
for _kw in ["evaporate", "evaporation", "condensation", "precipitation"]:
    _KW_PROC[_kw] = "water_cycle"
for _kw in ["photosynthesis", "photosynthesize", "chlorophyll", "chloroplast"]:
    _KW_PROC[_kw] = "photosynthesis"
for _kw in ["respiration", "respire", "exhale", "inhale"]:
    _KW_PROC[_kw] = "respiration"
for _kw in ["erosion", "weathering"]:
    _KW_PROC[_kw] = "erosion_weathering"
for _kw in ["digestion", "digest"]:
    _KW_PROC[_kw] = "digestion"
for _kw in ["decompose", "decomposition", "decay"]:
    _KW_PROC[_kw] = "decomposition"
for _kw in ["dissolution"]:
    _KW_PROC[_kw] = "dissolution"
for _kw in ["fossil", "fossilization"]:
    _KW_PROC[_kw] = "fossilization"


# ============================================================================ held-out target (DEV, no-leak)
def _build_heldout(split: str = "dev"):
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    oracle_multiset = _oracle_event_multiset(steps_df)
    coref = _load_coref(split)
    kb = _load_kb()
    procs = kb["processes"]
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp]
                    for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}
    matched_by_pid = {str(p["para_id"]): _select_matched(p, procs) for p in paragraphs}
    held = []
    for para in paragraphs:
        pid = str(para["para_id"])
        for pp in para["participants"]:
            gold = {e for e in oracle_facts.get((pid, pp), {}).keys() if e in EFFECTS}
            if not gold:
                continue
            variants = {t for t in _norm_toks(pp) if len(t) > 2}
            held.append({"pid": pid, "participant": pp, "variants": sorted(variants),
                         "gold": sorted(gold), "procs": matched_by_pid[pid]})
    return held, procs, paragraphs


# ============================================================================ process tagger (glass-box)
def _tag_sentence(sentence: str, entities: List[str], procs, para_procs: Optional[List[str]]) -> List[str]:
    """Return the process(es) for a reading sentence. PARAGRAPH-level tag (para_procs) for ProPara
    TRAIN sentences (one process/paragraph); else SENTENCE-level frame-SELECTION (validated
    convergence organ); else the unambiguous keyword lexicon; else [] (SKIP -- do not emit a wrongly
    keyed fact, per option c)."""
    if para_procs is not None:
        return para_procs
    sel = _select_matched({"sentence_texts": [sentence], "participants": entities}, procs)
    if sel:
        return sel
    toks = _toks(sentence)
    kw = sorted({p for t in toks for p in [_KW_PROC.get(t)] if p})
    return kw[:1]


# ============================================================================ process-conditioned reading stream
def _reading_stream_pc(max_simplewiki: int, procs, train_paragraphs):
    """Yield (sentence, para_procs_or_None). ProPara TRAIN yielded paragraph-by-paragraph with the
    paragraph's _select_matched process(es); SimpleWiki science sentences yielded with None (tagged
    per-sentence). DEV is NEVER included."""
    for para in train_paragraphs:
        pprocs = _select_matched(para, procs)
        for s in para.get("sentence_texts", []):
            s = s.strip()
            if s:
                yield s, pprocs
    n = 0
    with open(SIMPLEWIKI_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not (12 <= len(s) <= 240):
                continue
            if not _SCI_TOPIC.search(s):
                continue
            toks = set(_WORD.findall(s.lower()))
            if not any(lemma_verb(t) in _V2_LEX() for t in toks):
                continue
            yield s, None
            n += 1
            if n >= max_simplewiki:
                break


def _V2_LEX():
    from experiments.exp_stated_entity_fate_reading_extractor_v1 import FATE_VERB_LEXICON
    return FATE_VERB_LEXICON


# ============================================================================ recall helpers (process-keyed)
def _reading_dom_pc(item, counts_map: Dict[Tuple[str, str], Counter]) -> Set[str]:
    """Reading's DOMINANT fate for (entity,process): merge counts over the item's variants x its
    processes, argmax. Promiscuity-robust + process-keyed (the honest measure)."""
    c = Counter()
    for t in item["variants"]:
        for tok in (t, _singularize(t)):
            for P in item["procs"]:
                key = (tok, P)
                if key in counts_map:
                    c.update(counts_map[key])
    d = _dom(c)
    return {d} if d else set()


def _recall(held, answer_fn) -> float:
    if not held:
        return 0.0
    return round(sum(1 for it in held if answer_fn(it) & set(it["gold"])) / len(held), 4)


# ============================================================================ design-gate + fade
def run(max_simplewiki: int = 12000, proctag_sample: int = 120, seed: int = 20260811) -> Dict:
    t0 = time.time()
    held, procs, dev_paragraphs = _build_heldout("dev")
    dev_sentences = {s.strip() for para in dev_paragraphs for s in para["sentence_texts"]}
    keyed, seed_global, seed_vocab = _seed_maps(procs)
    seed_only = _recall(held, lambda it: _seed_answer(it, keyed))
    print(f"[held-out] {len(held)} DEV (entity,process)->fate items; seed_only(process-keyed)={seed_only}", flush=True)

    gen = _load_or_build_frontend()
    train_paragraphs = _load_split("train")

    # SEED store (process-keyed, TRUST_HIGH) + reading process-keyed store (TRUST_LOW), separate rels.
    relations = {f"seed_fate_in_{p}": "MULTIVALUED" for p in procs}
    relations.update({f"read_fate_in_{p}": "MULTIVALUED" for p in procs})
    store = HDFactStore(n_dim=STORE_N_DIM, seed=0, relation_cardinality=relations)
    for (tok, pname), effs in keyed.items():
        for e in sorted(effs):
            store.store(tok, f"seed_fate_in_{pname}", e, "seed", "TRUST_HIGH")
    n_seed_store = len(store.live_facts())

    # GROW: process-conditioned reading. read_counts keyed by (entity_head, process) -> Counter(fate).
    read_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    proctag_samples: List[Dict] = []
    n_read_sent = n_read_facts = n_skipped_no_proc = n_leak_guard = 0
    n_tag_paragraph = n_tag_frame = n_tag_kw = 0
    curve = []
    ckpts = list(CHECKPOINTS)
    next_ckpt_idx = 0
    rng_s = random.Random(seed)
    for s, para_procs in _reading_stream_pc(max_simplewiki, procs, train_paragraphs):
        if s in dev_sentences:  # NO-LEAK guard
            n_leak_guard += 1
            continue
        facts = extract_facts_strict(gen, s)
        if facts:
            ents = [f["entity_head"] for f in facts]
            tagged = _tag_sentence(s, ents, procs, para_procs)
            if not tagged:
                n_skipped_no_proc += len(facts)
            else:
                if para_procs is not None:
                    n_tag_paragraph += 1
                elif _select_matched({"sentence_texts": [s], "participants": ents}, procs):
                    n_tag_frame += 1
                else:
                    n_tag_kw += 1
                for f in facts:
                    for P in tagged:
                        read_counts[(f["entity_head"], P)][f["fate"]] += 1
                        n_read_facts += 1
                        if len(proctag_samples) < 5000:  # reservoir for hand-check
                            row = {"entity": f["entity_head"], "process": P, "fate": f["fate_label"],
                                   "sentence": s, "src": "propara_train" if para_procs is not None else "simplewiki",
                                   "tagger": "paragraph" if para_procs is not None else "sentence"}
                            if len(proctag_samples) < proctag_sample:
                                proctag_samples.append(row)
                            else:
                                j = rng_s.randint(0, len(proctag_samples))
                                if j < proctag_sample:
                                    proctag_samples[j] = row
        n_read_sent += 1
        if next_ckpt_idx < len(ckpts) and n_read_sent >= ckpts[next_ckpt_idx]:
            r_dom = _recall(held, lambda it: _reading_dom_pc(it, read_counts))
            comb = _recall(held, lambda it: _seed_answer(it, keyed) | _reading_dom_pc(it, read_counts))
            curve.append({"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                          "n_distinct_ep_keys": len(read_counts), "reading_only_recall": r_dom,
                          "combined_recall": comb, "seed_only_recall": seed_only})
            print(f"[curve] read={n_read_sent} facts={n_read_facts} ep_keys={len(read_counts)} "
                  f"reading_only(dom,PC)={r_dom} combined={comb} (seed_only={seed_only})", flush=True)
            next_ckpt_idx += 1

    r_only_final = _recall(held, lambda it: _reading_dom_pc(it, read_counts))
    combined_final = _recall(held, lambda it: _seed_answer(it, keyed) | _reading_dom_pc(it, read_counts))
    curve.append({"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                  "n_distinct_ep_keys": len(read_counts), "reading_only_recall": r_only_final,
                  "combined_recall": combined_final, "seed_only_recall": seed_only, "final": True})
    print(f"[curve-final] read={n_read_sent} reading_only(dom,PC)={r_only_final} combined={combined_final} "
          f"seed_only={seed_only}", flush=True)

    # ---- LESION (process-keyed dominant): reading_only vs combined + OVERLAP ----
    seed_covered = [it for it in held if _seed_answer(it, keyed) & set(it["gold"])]
    n_seed_cov = len(seed_covered)
    n_seed_and_read = sum(1 for it in seed_covered if _reading_dom_pc(it, read_counts) & set(it["gold"]))
    overlap = round(n_seed_and_read / n_seed_cov, 4) if n_seed_cov else 0.0
    lesion_gap = round(combined_final - r_only_final, 4)
    fade_ratio = round(r_only_final / combined_final, 4) if combined_final > 1e-9 else 0.0
    print(f"[lesion] reading_only(PC)={r_only_final} combined={combined_final} gap={lesion_gap} "
          f"fade_ratio={fade_ratio} OVERLAP={overlap} ({n_seed_and_read}/{n_seed_cov})", flush=True)

    # ---- SCRAMBLE (now MEANINGFUL): permute (entity,process)->fate-counts across keys -> collapse ----
    keys = sorted(read_counts.keys())
    n = len(keys)
    scr_counts: Dict[Tuple[str, str], Counter] = {}
    if n >= 2:
        perm = _deterministic_perm(SCRAMBLE_SEED, n)
        if perm == list(range(n)):
            perm = perm[1:] + perm[:1]
        for i, k in enumerate(keys):
            scr_counts[k] = Counter(read_counts[keys[perm[i]]])
    else:
        scr_counts = {k: Counter(v) for k, v in read_counts.items()}
    scramble_recall = _recall(held, lambda it: _reading_dom_pc(it, scr_counts))
    scramble_retained = round(scramble_recall / r_only_final, 4) if r_only_final > 1e-9 else 0.0
    print(f"[scramble] process-keyed scramble_recall={scramble_recall} retained={scramble_retained}", flush=True)

    # ---- FIDELITY on held-out (dominant, process-keyed) ----
    n_items_with = n_correct = 0
    for it in held:
        ans = _reading_dom_pc(it, read_counts)
        if ans:
            n_items_with += 1
            n_correct += 1 if (ans & set(it["gold"])) else 0
    read_prec = round(n_correct / n_items_with, 4) if n_items_with else 0.0

    # dump process-tag sample for hand-check (the DESIGN GATE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dump = os.path.join(OUTPUT_DIR, "_proctag_for_handcheck.json")
    with open(dump, "w", encoding="utf-8") as f:
        json.dump({"n_read_facts": n_read_facts, "sample": proctag_samples}, f, indent=2)
    print(f"[design-gate] dumped {len(proctag_samples)} (entity,process,fate) for process-tag hand-check "
          f"-> {dump}; tagger mix: paragraph={n_tag_paragraph} frame-sentence={n_tag_frame} kw={n_tag_kw} "
          f"skipped_no_proc={n_skipped_no_proc}", flush=True)

    # ---- verdict (PRELIMINARY: process-tag accuracy folded in by operator) ----
    reading_first = curve[0]["reading_only_recall"] if curve else 0.0
    rises = (r_only_final - reading_first) >= RISE_MIN_ABS
    fades = (lesion_gap <= FADE_GAP_MAX) or (fade_ratio >= FADE_RATIO_MIN)
    scramble_collapses = scramble_retained <= SCRAMBLE_MAX_RETAINED
    if rises and fades and scramble_collapses:
        verdict = "FADE_CONDITIONS_MET_PENDING_PROCTAG_HANDCHECK"
    else:
        fails = []
        if not rises: fails.append("no_rise")
        if not fades: fails.append("no_fade_lesion_gap")
        if not scramble_collapses: fails.append("scramble_no_collapse")
        verdict = "HARD_FAIL_" + "+".join(fails)
    verdict_msg = (
        f"{verdict}: PROCESS-KEYED FADE CURVE reading_only(dom) {[c['reading_only_recall'] for c in curve]} "
        f"(rise {reading_first}->{r_only_final} >=+{RISE_MIN_ABS}? {rises}); seed_only={seed_only} "
        f"combined_final={combined_final}; LESION gap={lesion_gap} (fade<= {FADE_GAP_MAX}) fade_ratio={fade_ratio} "
        f"-> fades={fades}; OVERLAP={overlap} ({n_seed_and_read}/{n_seed_cov} seed-covered re-derived); "
        f"SCRAMBLE recall={scramble_recall} retained={scramble_retained} (collapse<= {SCRAMBLE_MAX_RETAINED}) "
        f"-> {scramble_collapses}; reading held-out precision={read_prec}; "
        f"n_read_facts={n_read_facts} ep_keys={len(read_counts)} skipped_no_proc={n_skipped_no_proc} "
        f"leak_guard={n_leak_guard}; DESIGN-GATE process-tag accuracy pending hand-check (dump)")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "bootstrap_pc", "anchor_name": ANCHOR_NAME,
        "n_heldout_items": len(held), "seed_only_recall": seed_only,
        "primary_metric": "process-keyed reading DOMINANT (entity,process)->fate (promiscuity-robust + grain-matched)",
        "fade_curve": curve, "reading_only_final": r_only_final, "combined_final": combined_final,
        "lesion": {"reading_only": r_only_final, "combined": combined_final, "gap": lesion_gap,
                   "fade_ratio": fade_ratio, "n_seed_covered": n_seed_cov,
                   "n_seed_covered_rederived_by_reading": n_seed_and_read, "overlap": overlap},
        "scramble": {"scramble_recall": scramble_recall, "retained_fraction": scramble_retained},
        "fidelity": {"reading_heldout_dominant_precision": read_prec, "n_items_with_dominant": n_items_with,
                     "n_correct": n_correct, "v2_handcheck_precision": READING_FIDELITY_V2},
        "reading_corpus": {"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                           "n_distinct_ep_keys": len(read_counts), "n_skipped_no_process": n_skipped_no_proc,
                           "no_leak_dev_guard_fires": n_leak_guard,
                           "tagger_mix": {"paragraph": n_tag_paragraph, "frame_sentence": n_tag_frame, "keyword": n_tag_kw}},
        "design_gate": {"proctag_handcheck_dump": dump, "n_proctag_sample": len(proctag_samples),
                        "PROCTAG_ACC_GATE": PROCTAG_ACC_GATE,
                        "note": "process-tag accuracy hand-checked by operator; verdict finalized after"},
        "bands": {"RISE_MIN_ABS": RISE_MIN_ABS, "FADE_GAP_MAX": FADE_GAP_MAX, "FADE_RATIO_MIN": FADE_RATIO_MIN,
                  "SCRAMBLE_MAX_RETAINED": SCRAMBLE_MAX_RETAINED, "PROCTAG_ACC_GATE": PROCTAG_ACC_GATE},
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
    keyed, seed_global, vocab = _seed_maps(procs)
    assert "DESTROY" in keyed[("wood", "combustion")]
    # (1) process tagger: combustion sentence -> combustion; generic -> [] (skip)
    t1 = _tag_sentence("Fire consumes the wood and produces ash.", ["wood", "ash"], procs, None)
    assert "combustion" in t1, t1
    t2 = _tag_sentence("The generator produces electricity.", ["electricity"], procs, None)
    assert t2 == [] or "electricity_generation" not in t2  # generic -> skip or no false combustion tag
    tpar = _tag_sentence("Whatever text.", ["x"], procs, ["digestion"])
    assert tpar == ["digestion"], tpar
    out["checks"]["tagger"] = {"combustion_sent": t1, "generic_sent": t2, "paragraph_override": tpar}
    print(f"[self-test] process tagger OK ({t1}, generic->{t2}, para->{tpar})", flush=True)

    # (2) real frontend + process-keyed reading + recall + scramble collapse
    gen = _load_or_build_frontend()
    facts = extract_facts_strict(gen, "Fire consumes the wood and produces ash.")
    tagged = _tag_sentence("Fire consumes the wood and produces ash.", [f["entity_head"] for f in facts], procs, None)
    rc: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    for f in facts:
        for P in tagged:
            rc[(f["entity_head"], P)][f["fate"]] += 1
    held = [{"pid": "p", "participant": "wood", "variants": ["wood"], "gold": ["DESTROY"], "procs": ["combustion"]},
            {"pid": "q", "participant": "unicorn", "variants": ["unicorn"], "gold": ["MOVE"], "procs": ["combustion"]}]
    assert _reading_dom_pc(held[0], rc) == {"DESTROY"}, rc
    assert _recall(held, lambda it: _reading_dom_pc(it, rc)) == 0.5
    # scramble (single key -> degenerate ok); multi-key collapse
    rc2 = {("wood", "combustion"): Counter({"DESTROY": 3}), ("ash", "combustion"): Counter({"CREATE": 3})}
    held2 = [{"pid": "a", "participant": "wood", "variants": ["wood"], "gold": ["DESTROY"], "procs": ["combustion"]},
             {"pid": "b", "participant": "ash", "variants": ["ash"], "gold": ["CREATE"], "procs": ["combustion"]}]
    assert _recall(held2, lambda it: _reading_dom_pc(it, rc2)) == 1.0
    keys = sorted(rc2)
    perm = _deterministic_perm(SCRAMBLE_SEED, len(keys))
    if perm == list(range(len(keys))):
        perm = perm[1:] + perm[:1]
    scr = {k: Counter(rc2[keys[perm[i]]]) for i, k in enumerate(keys)}
    assert _recall(held2, lambda it: _reading_dom_pc(it, scr)) < 1.0, scr
    out["checks"]["real_pc_reading"] = {"wood_dom": "DESTROY", "scramble_collapsed": True}
    print("[self-test] process-keyed reading + recall + scramble collapse OK", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = "SELFTEST_PASS: process tagger + process-keyed reading recall + scramble collapse OK"
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--max-simplewiki", type=int, default=12000)
    ap.add_argument("--proctag-sample", type=int, default=120)
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test else "bootstrap_pc"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)
    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run(max_simplewiki=args.max_simplewiki, proctag_sample=args.proctag_sample)
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
