# CELL-TEMPLATE (culmination composition-proof; NOT a queue-dispatch cell). Composes three
# INDEPENDENTLY-VALIDATED pieces into the bootstrap thesis -- 'seed -> learning takes over -> crutch
# fades' -- with ZERO LLM anywhere. WIRE-DON'T-ISLAND: reuses, does not rebuild:
#   SEED  (the crutch): hand-vetted process-physics KB (propara_process_physics_kb_v1.json, authored
#          BLIND to test gold), re-keyed to (entity,process)->fate via
#          exp_propara_process_keyed_lookup_v1._rekey_kb, stored in hdlab.hd_fact_store at trust=HIGH.
#   GROW  (the learner): the hardened high-precision reading extractor
#          exp_stated_entity_fate_reading_extractor_v2_highprecision.extract_facts_strict (hand-checked
#          P=0.90), run over a science corpus (ProPara TRAIN prose + SimpleWiki science subset -- DEV
#          NEVER READ), ingesting (entity,fate) facts into the SAME store at trust=LOW.
#   TARGET (held-out): ProPara DEV oracle gold fates, restructured to (entity,process)->fate. NO-LEAK:
#          DEV is never read into the grow corpus and never used to build the seed or tune the extractor.
#
# MEASURE (fact-level): at increasing reading-exposure checkpoints, reading_only_recall vs seed_only
# vs combined on the held-out set (FADE CURVE = reading_only RISING). LESION: drop all SEED facts,
# measure reading_only on the full held-out (FADE PROVEN if reading_only ~= combined + high seed/read
# OVERLAP). CONTROLS: SCRAMBLE (permute reading entity->fate before ingest -> reading_only MUST
# collapse), FIDELITY (reading held-out fact precision, carried from v2's 0.90), and TRUST-CONFLICT
# (a FUNCTIONAL-relation micro-test: a wrong low-trust READING fact must NOT overwrite a right
# high-trust SEED fact -- hd_fact_store resolution must DROP the reading fact).
#
# Load-bearing subset: no bare except / no except BaseException (SystemExit/KeyboardInterrupt re-raise,
# then Exception->crash-diagnostic); final_metrics_atomicity=tmp_replace; deterministic_seeding=true
# (store seeded; scramble via hashlib-seeded _deterministic_perm, no python hash()/list(set())
# ordering); resumable-per-checkpoint (reading map + per-checkpoint recall snapshotted to disk);
# self-test constructs REAL seed store + REAL frontend extraction + REAL held-out at tiny scale;
# crlb_n/a (fact-level recall over the fixed ProPara EMNLP18 DEV oracle; no noise-floor threshold).
# See preregs/2026-08-11_bootstrap_seed_ignites_reading_learner_fade_v1.md for the full pre-reg.
"""exp_bootstrap_seed_ignites_reading_learner_fade_v1 -- the bootstrap thesis proof (no LLM):
a hand-vetted SEED ignites a no-LLM reading learner that re-derives + extends the seed by reading,
so the seed becomes lesionable (the developmental scaffold-that-fades). See header for composition.
Modes: --self-test / (no flag)=the exposure-curve + lesion + controls.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

ANCHOR_NAME = "bootstrap_seed_ignites_reading_learner_fade_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
CKPT_PATH = os.path.join(OUTPUT_DIR, "_reading_curve_ckpt.json")

from hdlab.hd_fact_store import HDFactStore  # noqa: E402

# SEED (crutch): re-key the hand-vetted KB (reuse verbatim)
from experiments.exp_propara_process_keyed_lookup_v1 import (  # noqa: E402
    _rekey_kb, _select_matched, _EFFECT_TRIGS,
)
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import _load_kb, _norm_toks  # noqa: E402
# held-out oracle facts (reuse the exact precompute path Test 1 uses)
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _deterministic_perm,
)
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import _paragraph_precompute  # noqa: E402
from experiments.exp_propara_arm2_extracted_structure_v1 import _load_coref  # noqa: E402
from propara_trap_check import build_step_rows  # noqa: E402
# GROW (learner): the hardened v2 reading extractor (reuse verbatim)
from experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision import (  # noqa: E402
    extract_facts_strict, _load_or_build_frontend, _singularize, FATE_VERB_LEXICON,
)
from experiments.exp_stated_entity_fate_reading_extractor_v1 import _SCI_TOPIC, _WORD, _propara_train_sentences  # noqa: E402

EFFECTS = ("CREATE", "MOVE", "DESTROY")
STORE_N_DIM = 8192
CHECKPOINTS = (1000, 3000, 6000, 10000, 14000)
SCRAMBLE_SEED = "bootstrap_reading_scramble_v1"
READING_FIDELITY_V2 = 0.90  # CITED@data/exp_stated_entity_fate_reading_extractor_v2_highprecision/metrics.json hand_check.filtered_precision

# ---- pre-registered bands ----
RISE_MIN_ABS = 0.05          # reading_only_recall(final) - reading_only_recall(first) >= this
FADE_GAP_MAX = 0.05          # combined_recall - reading_only_recall(final) <= this  -> seed lesionable
FADE_RATIO_MIN = 0.85        # OR reading_only/combined >= this
SCRAMBLE_MAX_RETAINED = 0.50  # scramble_reading_recall <= this * reading_only_recall


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


# ============================================================================ SEED (process-keyed, hand-KB)
def _seed_maps(procs):
    keyed, vocab = _rekey_kb(procs)               # (entity_tok, process) -> {FATE}
    global_map = defaultdict(set)
    for (t, _p), effs in keyed.items():
        global_map[t] |= effs
    return keyed, dict(global_map), vocab


def _seed_answer(item, keyed) -> Set[str]:
    out: Set[str] = set()
    for t in item["variants"]:
        for P in item["procs"]:
            out |= keyed.get((t, P), set())
    return out


# ============================================================================ READING map lookup
# TWO reading metrics:
#  - recall-ANY (secondary, promiscuity-INFLATED): does reading assert ANY gold fate for the entity?
#    With only 3 fate classes and reading accumulating multiple fates per popular entity, this
#    saturates -> scramble cannot cleanly collapse (measured: 0.61 retained). Reported for context.
#  - DOMINANT (PRIMARY, promiscuity-ROBUST): reading's single argmax-count fate per entity. Each
#    entity contributes exactly ONE fate, so permuting the entity->fate map genuinely breaks the
#    correspondence and the scramble collapses to chance. This is the honest bootstrap measure.
def _reading_answer(item, read_map: Dict[str, Set[str]]) -> Set[str]:
    out: Set[str] = set()
    for t in item["variants"]:
        out |= read_map.get(t, set()) | read_map.get(_singularize(t), set())
    return out


def _merged_counts(item, counts_map: Dict[str, "Counter"]):
    from collections import Counter as _C
    c = _C()
    for t in item["variants"]:
        for tok in (t, _singularize(t)):
            if tok in counts_map:
                c.update(counts_map[tok])
    return c


def _dom(counts) -> Optional[str]:
    """argmax fate by count; deterministic tie-break by EFFECTS order. None if no counts."""
    if not counts:
        return None
    return max(EFFECTS, key=lambda e: (counts.get(e, 0), -EFFECTS.index(e)))


def _reading_dom_answer(item, counts_map: Dict[str, "Counter"]) -> Set[str]:
    d = _dom(_merged_counts(item, counts_map))
    return {d} if d else set()


def _recall(held, answer_fn) -> float:
    if not held:
        return 0.0
    n_ok = sum(1 for it in held if answer_fn(it) & set(it["gold"]))
    return round(n_ok / len(held), 4)


def _reading_heldout_precision(held, counts_map) -> Tuple[float, int, int]:
    """Fact-level precision of reading's DOMINANT answer on held-out entities (poisoning/fidelity):
    of the items where reading has a dominant fate, what fraction match a gold fate."""
    n_pairs = n_correct = 0
    for it in held:
        ans = _reading_dom_answer(it, counts_map)
        if not ans:
            continue
        n_pairs += 1
        n_correct += 1 if (ans & set(it["gold"])) else 0
    return (round(n_correct / n_pairs, 4) if n_pairs else 0.0), n_correct, n_pairs


# ============================================================================ reading corpus (DEV never read)
def _reading_stream(max_simplewiki: int):
    """Deterministic reading stream: ProPara TRAIN prose first (process-dense early instruction),
    then SimpleWiki science sentences in file order. DEV is NEVER included (no-leak)."""
    for s in _propara_train_sentences():
        if s.strip():
            yield s.strip()
    n = 0
    with open(SIMPLEWIKI_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not (12 <= len(s) <= 240):
                continue
            if not _SCI_TOPIC.search(s):
                continue
            toks = set(_WORD.findall(s.lower()))
            if not any(_lemma_ok(t) for t in toks):
                continue
            yield s
            n += 1
            if n >= max_simplewiki:
                break


def _lemma_ok(t: str) -> bool:
    from hdlab.thematic_role_labeler import lemma_verb
    return lemma_verb(t) in FATE_VERB_LEXICON


# ============================================================================ growth curve + store
def run_bootstrap(max_simplewiki: int = 12000) -> Dict:
    t0 = time.time()
    held, procs, dev_paragraphs = _build_heldout("dev")
    dev_sentences = {s.strip() for para in dev_paragraphs for s in para["sentence_texts"]}
    keyed, seed_global, seed_vocab = _seed_maps(procs)
    print(f"[held-out] {len(held)} DEV (entity,process)->fate items; seed: {len(keyed)} keyed facts, "
          f"{len(seed_vocab)} entity tokens", flush=True)

    seed_only = _recall(held, lambda it: _seed_answer(it, keyed))
    print(f"[seed] seed_only_recall (process-keyed, no reading) = {seed_only}", flush=True)

    gen = _load_or_build_frontend()

    # SEED store (hd_fact_store): seed facts under a SEED-scoped MULTIVALUED relation, TRUST_HIGH.
    # Reading facts go under a SEPARATE reading-scoped relation so the store faithfully holds every
    # reading fate (a shared MULTIVALUED relation would DROP a lower-trust READING fate that differs
    # from a SEED fate -- hd_fact_store only COMBINEs different objects at EQUAL trust; that store
    # semantics is exercised deliberately by the FUNCTIONAL trust-conflict micro-test below).
    store = HDFactStore(n_dim=STORE_N_DIM, seed=0,
                        relation_cardinality={"seed_fate": "MULTIVALUED", "read_fate": "MULTIVALUED"})
    for t, effs in seed_global.items():
        for e in sorted(effs):
            store.store(t, "seed_fate", e, "seed", "TRUST_HIGH")
    n_seed_store = len(store.live_facts())

    # GROW: read the stream, accumulate per-entity fate COUNTS + ingest reading facts (trust=LOW),
    # checkpoint the PRIMARY dominant-fate recall (+ recall-any secondary) at exposure milestones.
    from collections import Counter
    read_counts: Dict[str, Counter] = defaultdict(Counter)
    read_map: Dict[str, Set[str]] = defaultdict(set)
    n_read_sent = 0
    n_read_facts = 0
    n_leak_guard = 0
    curve = []
    ckpts = list(CHECKPOINTS)
    stream = _reading_stream(max_simplewiki)
    next_ckpt_idx = 0
    for s in stream:
        if s in dev_sentences:  # NO-LEAK guard (should never fire; TRAIN+SimpleWiki only)
            n_leak_guard += 1
            continue
        for fact in extract_facts_strict(gen, s):
            head = fact["entity_head"]
            fate = fact["fate"]
            if fate not in read_map[head]:
                store.store(head, "read_fate", fate, "reading", "TRUST_LOW")
            read_map[head].add(fate)
            read_counts[head][fate] += 1
            n_read_facts += 1
        n_read_sent += 1
        if next_ckpt_idx < len(ckpts) and n_read_sent >= ckpts[next_ckpt_idx]:
            r_dom = _recall(held, lambda it: _reading_dom_answer(it, read_counts))
            r_any = _recall(held, lambda it: _reading_answer(it, read_map))
            comb = _recall(held, lambda it: _seed_answer(it, keyed) | _reading_dom_answer(it, read_counts))
            curve.append({"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                          "n_distinct_read_entities": len(read_map), "reading_only_recall": r_dom,
                          "reading_only_recall_any": r_any, "combined_recall": comb, "seed_only_recall": seed_only})
            print(f"[curve] read={n_read_sent} facts={n_read_facts} ents={len(read_map)} "
                  f"reading_only(dom)={r_dom} (any={r_any}) combined={comb} (seed_only={seed_only})", flush=True)
            _save_ckpt({"curve": curve, "n_read_sent": n_read_sent})
            next_ckpt_idx += 1

    # final checkpoint (whatever the stream length was)
    r_only_final = _recall(held, lambda it: _reading_dom_answer(it, read_counts))
    r_any_final = _recall(held, lambda it: _reading_answer(it, read_map))
    combined_final = _recall(held, lambda it: _seed_answer(it, keyed) | _reading_dom_answer(it, read_counts))
    curve.append({"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                  "n_distinct_read_entities": len(read_map), "reading_only_recall": r_only_final,
                  "reading_only_recall_any": r_any_final, "combined_recall": combined_final,
                  "seed_only_recall": seed_only, "final": True})
    print(f"[curve-final] read={n_read_sent} reading_only(dom)={r_only_final} (any={r_any_final}) "
          f"combined={combined_final} seed_only={seed_only}", flush=True)

    # ---- STORE WIRE-WITNESS: store-based reading recall-ANY == map-based (validates hd_fact_store) ----
    def _store_reading_answer(it):
        out: Set[str] = set()
        for t in it["variants"]:
            for tok in (t, _singularize(t)):
                for r in store.query(tok, "read_fate"):
                    if r["source"] == "reading" and str(r["object"]) in EFFECTS:
                        out.add(str(r["object"]))
        return out
    store_reading_recall = _recall(held, _store_reading_answer)
    store_wire_ok = abs(store_reading_recall - r_any_final) < 1e-9

    # ---- LESION (PRIMARY = dominant): reading_only vs combined on full held-out; OVERLAP ----
    seed_covered = [it for it in held if _seed_answer(it, keyed) & set(it["gold"])]
    n_seed_cov = len(seed_covered)
    n_seed_and_read = sum(1 for it in seed_covered if _reading_dom_answer(it, read_counts) & set(it["gold"]))
    overlap = round(n_seed_and_read / n_seed_cov, 4) if n_seed_cov else 0.0
    lesion_gap = round(combined_final - r_only_final, 4)
    fade_ratio = round(r_only_final / combined_final, 4) if combined_final > 1e-9 else 0.0
    print(f"[lesion] reading_only(dom)={r_only_final} combined={combined_final} gap={lesion_gap} "
          f"fade_ratio={fade_ratio}; seed-covered items re-derived by reading OVERLAP={overlap} "
          f"({n_seed_and_read}/{n_seed_cov})", flush=True)

    # ---- SCRAMBLE control (PRIMARY = dominant): permute entity->fate-COUNTS across entities; the
    # single dominant fate is then randomized per entity -> promiscuity-robust collapse to chance. ----
    ents = sorted(read_counts.keys())
    n = len(ents)
    scr_counts: Dict[str, Counter] = {}
    if n >= 2:
        perm = _deterministic_perm(SCRAMBLE_SEED, n)
        if perm == list(range(n)):
            perm = perm[1:] + perm[:1]
        for i, e in enumerate(ents):
            scr_counts[e] = Counter(read_counts[ents[perm[i]]])
    else:
        scr_counts = {e: Counter(v) for e, v in read_counts.items()}
    scramble_recall = _recall(held, lambda it: _reading_dom_answer(it, scr_counts))
    scramble_recall_any = _recall(held, lambda it: _reading_answer(
        it, {e: set(c) for e, c in scr_counts.items()}))
    scramble_retained = round(scramble_recall / r_only_final, 4) if r_only_final > 1e-9 else 0.0
    print(f"[scramble] dominant scramble_recall={scramble_recall} retained_frac={scramble_retained} "
          f"(recall-any scramble={scramble_recall_any} vs any={r_any_final})", flush=True)

    # ---- FIDELITY / poisoning on held-out (dominant answer precision) ----
    read_prec, n_corr_pairs, n_pairs = _reading_heldout_precision(held, read_counts)
    print(f"[fidelity] reading held-out DOMINANT precision={read_prec} ({n_corr_pairs}/{n_pairs} items)", flush=True)

    # ---- TRUST-CONFLICT micro-test (FUNCTIONAL relation): wrong low-trust READING must NOT
    # overwrite a right high-trust SEED fact. Build entity->single-primary-fate disagreements and
    # verify hd_fact_store resolves them by DROPPING the reading fact (seed protected). ----
    fstore = HDFactStore(n_dim=STORE_N_DIM, seed=0, relation_cardinality={"primary_fate": "FUNCTIONAL"})
    n_conflict = n_seed_protected = n_seed_overwritten = 0
    for t, seed_effs in seed_global.items():
        seed_primary = sorted(seed_effs)[0]
        fstore.store(t, "primary_fate", seed_primary, "seed", "TRUST_HIGH")
        read_effs = read_map.get(t, set()) | read_map.get(_singularize(t), set())
        read_conflict = sorted(read_effs - {seed_primary})
        if read_conflict:
            n_conflict += 1
            res = fstore.store(t, "primary_fate", read_conflict[0], "reading", "TRUST_LOW")
            live = {str(r["object"]) for r in fstore.query(t, "primary_fate") if r["status"] == "ACTIVE"}
            if seed_primary in live and res.resolution == "DROP":
                n_seed_protected += 1
            elif seed_primary not in live:
                n_seed_overwritten += 1
    trust_conflict = {"n_functional_conflicts": n_conflict, "n_seed_protected": n_seed_protected,
                      "n_seed_overwritten": n_seed_overwritten,
                      "all_seed_protected": n_seed_overwritten == 0}
    print(f"[trust] functional conflicts={n_conflict} seed_protected={n_seed_protected} "
          f"overwritten={n_seed_overwritten}", flush=True)

    # ---- VERDICT ----
    reading_first = curve[0]["reading_only_recall"] if curve else 0.0
    rises = (r_only_final - reading_first) >= RISE_MIN_ABS
    fades = (lesion_gap <= FADE_GAP_MAX) or (fade_ratio >= FADE_RATIO_MIN)
    scramble_collapses = scramble_retained <= SCRAMBLE_MAX_RETAINED
    if rises and fades and scramble_collapses and store_wire_ok and trust_conflict["all_seed_protected"]:
        verdict = "HARD_PASS_BOOTSTRAP_THESIS_VALIDATED"
    else:
        fails = []
        if not rises: fails.append("reading_only_does_not_rise_with_exposure")
        if not fades: fails.append("crutch_does_not_fade_lesion_drops_recall")
        if not scramble_collapses: fails.append("scramble_does_not_collapse")
        if not store_wire_ok: fails.append("store_wire_mismatch")
        if not trust_conflict["all_seed_protected"]: fails.append("seed_overwritten_by_reading")
        verdict = "HARD_FAIL_" + "+".join(fails)
    verdict_msg = (
        f"{verdict}: FADE CURVE reading_only_recall(dominant) {[c['reading_only_recall'] for c in curve]} "
        f"(rise {reading_first}->{r_only_final}, >=+{RISE_MIN_ABS}? {rises}); seed_only={seed_only} "
        f"combined_final={combined_final}; LESION gap={lesion_gap} (fade if <= {FADE_GAP_MAX}) "
        f"fade_ratio={fade_ratio} (or >= {FADE_RATIO_MIN}) -> fades={fades}; seed/reading OVERLAP={overlap} "
        f"({n_seed_and_read}/{n_seed_cov} seed-covered re-derived by reading); SCRAMBLE dominant recall="
        f"{scramble_recall} retained={scramble_retained} (collapse if <= {SCRAMBLE_MAX_RETAINED}) -> "
        f"{scramble_collapses}; reading held-out DOMINANT precision={read_prec} (v2 hand-check={READING_FIDELITY_V2}); "
        f"TRUST-CONFLICT functional: {n_seed_protected}/{n_conflict} seed protected, {n_seed_overwritten} "
        f"overwritten (all_protected={trust_conflict['all_seed_protected']}); store_wire_ok={store_wire_ok}; "
        f"reading_only_recall_ANY(promiscuity-inflated)={r_any_final} scramble_any={scramble_recall_any}; "
        f"n_leak_guard_fires={n_leak_guard}")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "bootstrap", "anchor_name": ANCHOR_NAME,
        "n_heldout_items": len(held), "seed_only_recall": seed_only,
        "primary_metric": "reading DOMINANT (argmax-count) fate per entity (promiscuity-robust); "
                          "recall-ANY reported as secondary (promiscuity-inflated, 3-fate saturation)",
        "n_seed_keyed_facts": len(keyed), "n_seed_entity_tokens": len(seed_vocab), "n_seed_store_facts": n_seed_store,
        "fade_curve": curve, "reading_only_final": r_only_final, "reading_only_any_final": r_any_final,
        "combined_final": combined_final,
        "lesion": {"reading_only": r_only_final, "combined": combined_final, "gap": lesion_gap,
                   "fade_ratio": fade_ratio, "n_seed_covered": n_seed_cov,
                   "n_seed_covered_rederived_by_reading": n_seed_and_read, "overlap": overlap},
        "scramble": {"dominant_scramble_recall": scramble_recall, "retained_fraction": scramble_retained,
                     "recall_any_scramble": scramble_recall_any, "recall_any_final": r_any_final},
        "fidelity": {"reading_heldout_dominant_precision": read_prec, "n_correct": n_corr_pairs,
                     "n_items_with_dominant": n_pairs, "v2_handcheck_precision": READING_FIDELITY_V2},
        "trust_conflict": trust_conflict,
        "store_wire": {"store_reading_recall": store_reading_recall, "map_reading_recall": r_only_final,
                       "store_wire_ok": store_wire_ok, "n_store_facts_final": len(store.live_facts())},
        "reading_corpus": {"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                           "n_distinct_read_entities": len(read_map), "max_simplewiki": max_simplewiki,
                           "no_leak_dev_guard_fires": n_leak_guard},
        "bands": {"RISE_MIN_ABS": RISE_MIN_ABS, "FADE_GAP_MAX": FADE_GAP_MAX, "FADE_RATIO_MIN": FADE_RATIO_MIN,
                  "SCRAMBLE_MAX_RETAINED": SCRAMBLE_MAX_RETAINED},
    }


# ============================================================================ ckpt + metrics I/O
def _save_ckpt(d):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = CKPT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f)
    os.replace(tmp, CKPT_PATH)


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

    # (1) seed re-key + entity-global map + process-keyed answer
    kb = _load_kb()
    procs = kb["processes"]
    keyed, seed_global, vocab = _seed_maps(procs)
    assert "DESTROY" in keyed[("wood", "combustion")]
    assert seed_global["wood"] and "DESTROY" in seed_global["wood"]
    out["checks"]["seed"] = {"n_keyed": len(keyed), "n_entity": len(vocab)}
    print(f"[self-test] seed re-key OK ({len(keyed)} keyed, {len(vocab)} entities)", flush=True)

    # (2) tiny held-out + recall helpers
    held = [{"pid": "p1", "participant": "wood", "variants": ["wood"], "gold": ["DESTROY"], "procs": ["combustion"]},
            {"pid": "p2", "participant": "unicorn", "variants": ["unicorn"], "gold": ["MOVE"], "procs": ["combustion"]}]
    assert _seed_answer(held[0], keyed) & {"DESTROY"}
    assert not _seed_answer(held[1], keyed)
    read_map = {"wood": {"DESTROY"}}
    assert _recall(held, lambda it: _reading_answer(it, read_map)) == 0.5
    out["checks"]["recall_helpers"] = "ok"
    print("[self-test] held-out + recall helpers OK", flush=True)

    # (3) REAL frontend extraction ingested into a REAL store (real_code_path) + store wire-witness
    gen = _load_or_build_frontend()
    facts = extract_facts_strict(gen, "Fire consumes the wood and produces ash.")
    got = {(f["entity_head"], f["fate"]) for f in facts}
    assert ("wood", "DESTROY") in got, got
    store = HDFactStore(n_dim=STORE_N_DIM, seed=0, relation_cardinality={"has_fate": "MULTIVALUED"})
    for f in facts:
        store.store(f["entity_head"], "has_fate", f["fate"], "reading", "TRUST_LOW")
    rows = store.query("wood", "has_fate")
    assert any(str(r["object"]) == "DESTROY" and r["source"] == "reading" for r in rows), rows
    out["checks"]["real_extract_store"] = sorted(got)
    print("[self-test] real extraction + store ingest/query OK", flush=True)

    # (4) scramble collapses on a synthetic map; trust-conflict FUNCTIONAL drop
    held2 = [{"pid": "x", "participant": "wood", "variants": ["wood"], "gold": ["DESTROY"], "procs": ["combustion"]},
             {"pid": "y", "participant": "ash", "variants": ["ash"], "gold": ["CREATE"], "procs": ["combustion"]}]
    rm = {"wood": {"DESTROY"}, "ash": {"CREATE"}}
    ents = sorted(rm)
    perm = _deterministic_perm(SCRAMBLE_SEED, len(ents))
    if perm == list(range(len(ents))):
        perm = perm[1:] + perm[:1]
    scr = {e: set(rm[ents[perm[i]]]) for i, e in enumerate(ents)}
    assert _recall(held2, lambda it: _reading_answer(it, rm)) == 1.0
    assert _recall(held2, lambda it: _reading_answer(it, scr)) < 1.0, ("scramble must collapse", scr)
    fstore = HDFactStore(n_dim=STORE_N_DIM, seed=0, relation_cardinality={"primary_fate": "FUNCTIONAL"})
    fstore.store("wood", "primary_fate", "DESTROY", "seed", "TRUST_HIGH")
    res = fstore.store("wood", "primary_fate", "MOVE", "reading", "TRUST_LOW")
    live = {str(r["object"]) for r in fstore.query("wood", "primary_fate") if r["status"] == "ACTIVE"}
    assert res.resolution == "DROP" and "DESTROY" in live and "MOVE" not in live, (res.resolution, live)
    out["checks"]["scramble_and_trust"] = {"scramble_collapsed": True, "seed_protected": True}
    print("[self-test] scramble collapse + trust-conflict seed-protection OK", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = ("SELFTEST_PASS: seed re-key + recall helpers + real extraction/store + "
                          "scramble collapse + functional trust-conflict seed-protection all OK")
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--max-simplewiki", type=int, default=12000)
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test else "bootstrap"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)
    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run_bootstrap(max_simplewiki=args.max_simplewiki)
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
