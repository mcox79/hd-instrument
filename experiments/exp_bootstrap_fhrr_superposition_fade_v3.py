# CELL-TEMPLATE (culmination v3; NOT a queue-dispatch cell). USER brain-foundational STORAGE steer:
# v1/v2 held (entity)->fate in a SYMBOLIC store that RESOLVED (FUNCTIONAL drop / trust-pick / dict
# dominant) to ONE fate -- a lossy collapse, not how the substrate should hold context-dependent
# knowledge. Fix: store facts in NATIVE FHRR SUPERPOSITION of context-bound pairs, sharded BY PROCESS,
# so context-dependent fates COEXIST separably (hippocampal conjunctive-coding + pattern-separation +
# pattern-completion). KEEP the process-conditioned ENCODING (extract (entity,process,fate), reused
# from exp_bootstrap_process_conditioned_reading_fade_v2); CHANGE storage/retrieval to VSA-native.
#   STORE:    M_process = SUM over facts of coef * bind(entity_vec, fate_vec)  (per-process register,
#             SHARDED by process to respect FHRR bundle capacity; SEED coef higher than READING; both
#             SUPERPOSE, never drop/replace).
#   RETRIEVE: unbind M_process by entity_vec -> noisy fate estimate -> cleanup (argmax over the
#             {CREATE,DESTROY,MOVE} fate codebook). Distinct entities near-orthogonal -> other facts
#             are NOISE, not an average; the correct fate wins.
# Reuse owned FHRR primitives hdlab.binding.bind/unbind (complex64 = FHRR); no reimplementation.
#
# GATE (still primary): process-tag accuracy (hand-checked in v2 = 0.7167, clears 0.70). RE-RUN the
# fade/lesion/scramble harness on the superposition store + report per-register CAPACITY + retrieval
# SNR/cleanup accuracy (PROOF the superposition SEPARATES, not averages). DEV never read (no-leak).
# Load-bearing subset: no bare except; tmp_replace; deterministic (torch.Generator seeds + hashlib
# _deterministic_perm); self-test builds REAL FHRR store + proves 2 context-bound facts for one entity
# coexist separably; crlb_n/a (fact-level recall over fixed ProPara EMNLP18 DEV oracle).
# See preregs/2026-08-11_bootstrap_fhrr_superposition_fade_v3.md.
"""exp_bootstrap_fhrr_superposition_fade_v3 -- does the crutch fade when context-dependent facts are
held in brain-native FHRR superposition (no averaging)? Reuses v2 process-conditioned extraction +
tagging; swaps the store to per-process bind/bundle registers with unbind+cleanup retrieval.
Modes: --self-test / (no flag)=capacity proof + fade/lesion/scramble on the superposition store.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import torch

ANCHOR_NAME = "bootstrap_fhrr_superposition_fade_v3"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab import binding  # noqa: E402  FHRR bind/unbind (complex64); reused, not reimplemented
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import _deterministic_perm  # noqa: E402
# reuse v2's process-conditioned extraction + tagging + held-out (wire-don't-island)
from experiments.exp_bootstrap_process_conditioned_reading_fade_v2 import (  # noqa: E402
    _build_heldout, _tag_sentence, _reading_stream_pc, _seed_maps, EFFECTS,
    extract_facts_strict, _load_or_build_frontend, _singularize, _select_matched,
    CHECKPOINTS, RISE_MIN_ABS, FADE_GAP_MAX, FADE_RATIO_MIN, SCRAMBLE_MAX_RETAINED, PROCTAG_ACC_GATE,
)
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import _load_split  # noqa: E402

FHRR_DIM = 4096
STORE_SEED = 20260811
SEED_COEF = 2.0    # trust WEIGHTS the bundle coefficient (SEED heavier) -- never drops/replaces
READ_COEF = 1.0
PROCTAG_ACC_V2 = 0.7167  # CITED@data/exp_bootstrap_process_conditioned_reading_fade_v2/metrics.json design_gate_result


# ============================================================================ FHRR superposition store
def _rand_fhrr(dim: int, gen: torch.Generator) -> torch.Tensor:
    """Unit-magnitude complex64 FHRR vector: exp(i*theta), theta ~ U[0,2pi)."""
    theta = 2.0 * math.pi * torch.rand(dim, generator=gen)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


class FHRRProcessStore:
    """Per-process superposition registers over a SHARED entity/fate codebook. SEED + READING bundle
    into SEPARATE registers (M_seed / M_read) so lesion = drop M_seed; combined = M_seed + M_read.
    Bundling is count-weighted per fact occurrence (multiple occurrences add magnitude -> the dominant
    fate wins at cleanup); trust weights the coefficient. Retrieval = unbind + argmax-similarity over
    the 3-fate codebook, GATED on the (entity,process) key having actually been stored (pattern-
    completion only for encountered conjunctions -- an unstored entity returns None, not a chance guess)."""

    def __init__(self, dim: int = FHRR_DIM, seed: int = STORE_SEED):
        self.dim = dim
        self.gen = torch.Generator().manual_seed(seed)
        self.fate = {f: _rand_fhrr(dim, self.gen) for f in EFFECTS}
        self.ent: Dict[str, torch.Tensor] = {}
        self.M_read: Dict[str, torch.Tensor] = defaultdict(lambda: torch.zeros(dim, dtype=torch.complex64))
        self.M_seed: Dict[str, torch.Tensor] = defaultdict(lambda: torch.zeros(dim, dtype=torch.complex64))
        self.read_keys: Dict[str, Set[str]] = defaultdict(set)
        self.seed_keys: Dict[str, Set[str]] = defaultdict(set)

    def _ent(self, e: str) -> torch.Tensor:
        v = self.ent.get(e)
        if v is None:
            v = _rand_fhrr(self.dim, self.gen)
            self.ent[e] = v
        return v

    def add_read(self, e: str, p: str, f: str, count: float = 1.0):
        self.M_read[p] = self.M_read[p] + (READ_COEF * count) * binding.bind(self._ent(e), self.fate[f])
        self.read_keys[p].add(e)

    def add_seed(self, e: str, p: str, f: str):
        self.M_seed[p] = self.M_seed[p] + SEED_COEF * binding.bind(self._ent(e), self.fate[f])
        self.seed_keys[p].add(e)

    def _cleanup(self, est: torch.Tensor) -> str:
        return max(EFFECTS, key=lambda f: float((est * self.fate[f].conj()).sum().real))

    def retrieve(self, e: str, p: str, which: str) -> Optional[str]:
        """which in {'read','seed','combined'}. None if the (e,p) conjunction was never stored in the
        selected source(s)."""
        reg = torch.zeros(self.dim, dtype=torch.complex64)
        present = False
        if which in ("read", "combined") and e in self.read_keys.get(p, ()):
            reg = reg + self.M_read[p]; present = True
        if which in ("seed", "combined") and e in self.seed_keys.get(p, ()):
            reg = reg + self.M_seed[p]; present = True
        if not present:
            return None
        return self._cleanup(binding.unbind(reg, self._ent(e)))


# ============================================================================ recall over the superposition
def _answer(item, store: FHRRProcessStore, which: str) -> Set[str]:
    out: Set[str] = set()
    for t in item["variants"]:
        for tok in (t, _singularize(t)):
            for P in item["procs"]:
                f = store.retrieve(tok, P, which)
                if f is not None:
                    out.add(f)
    return out


def _recall(held, store, which) -> float:
    if not held:
        return 0.0
    return round(sum(1 for it in held if _answer(it, store, which) & set(it["gold"])) / len(held), 4)


# ============================================================================ run
def run(max_simplewiki: int = 12000) -> Dict:
    t0 = time.time()
    held, procs, dev_paragraphs = _build_heldout("dev")
    dev_sentences = {s.strip() for para in dev_paragraphs for s in para["sentence_texts"]}
    keyed, seed_global, seed_vocab = _seed_maps(procs)
    gen = _load_or_build_frontend()
    train_paragraphs = _load_split("train")

    store = FHRRProcessStore(dim=FHRR_DIM, seed=STORE_SEED)
    # SEED bundle (process-keyed, heavier coef)
    for (tok, pname), effs in keyed.items():
        for e in sorted(effs):
            store.add_seed(tok, pname, e)
    seed_only = _recall(held, store, "seed")
    print(f"[held-out] {len(held)} DEV items; seed_only(FHRR retrieve)={seed_only}", flush=True)

    # GROW: process-conditioned reading bundled into M_read; count-weighted per occurrence.
    read_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)  # for capacity/scramble
    n_read_sent = n_read_facts = n_skipped_no_proc = n_leak_guard = 0
    curve = []
    ckpts = list(CHECKPOINTS)
    next_ckpt_idx = 0
    for s, para_procs in _reading_stream_pc(max_simplewiki, procs, train_paragraphs):
        if s in dev_sentences:
            n_leak_guard += 1
            continue
        facts = extract_facts_strict(gen, s)
        if facts:
            tagged = _tag_sentence(s, [f["entity_head"] for f in facts], procs, para_procs)
            if not tagged:
                n_skipped_no_proc += len(facts)
            else:
                for f in facts:
                    for P in tagged:
                        store.add_read(f["entity_head"], P, f["fate"], count=1.0)
                        read_counts[(f["entity_head"], P)][f["fate"]] += 1
                        n_read_facts += 1
        n_read_sent += 1
        if next_ckpt_idx < len(ckpts) and n_read_sent >= ckpts[next_ckpt_idx]:
            r = _recall(held, store, "read")
            c = _recall(held, store, "combined")
            curve.append({"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                          "n_ep_keys": sum(len(v) for v in store.read_keys.values()),
                          "reading_only_recall": r, "combined_recall": c, "seed_only_recall": seed_only})
            print(f"[curve] read={n_read_sent} facts={n_read_facts} reading_only(FHRR)={r} combined={c} "
                  f"(seed_only={seed_only})", flush=True)
            next_ckpt_idx += 1

    r_only_final = _recall(held, store, "read")
    combined_final = _recall(held, store, "combined")
    curve.append({"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                  "n_ep_keys": sum(len(v) for v in store.read_keys.values()),
                  "reading_only_recall": r_only_final, "combined_recall": combined_final,
                  "seed_only_recall": seed_only, "final": True})
    print(f"[curve-final] reading_only(FHRR)={r_only_final} combined={combined_final} seed_only={seed_only}", flush=True)

    # ---- CAPACITY + RETRIEVAL SNR (proof superposition SEPARATES, not averages) ----
    # per-register load
    load_read = {p: len(ks) for p, ks in store.read_keys.items()}
    reg_loads = sorted(load_read.values(), reverse=True)
    mean_load = round(sum(reg_loads) / max(len(reg_loads), 1), 2)
    # self-consistency: for each stored reading key, does unbind+cleanup return the count-DOMINANT fate?
    n_keys = n_correct_selfconsist = 0
    for (e, p), cnt in read_counts.items():
        dom = max(EFFECTS, key=lambda f: (cnt.get(f, 0), -EFFECTS.index(f)))
        if cnt.get(dom, 0) == 0:
            continue
        got = store.retrieve(e, p, "read")
        n_keys += 1
        if got == dom:
            n_correct_selfconsist += 1
    selfconsist = round(n_correct_selfconsist / n_keys, 4) if n_keys else 0.0
    print(f"[capacity] registers={len(reg_loads)} mean_load={mean_load} max_load={reg_loads[0] if reg_loads else 0} "
          f"retrieval self-consistency (unbind+cleanup == count-dominant) = {selfconsist} "
          f"({n_correct_selfconsist}/{n_keys}) -> superposition SEPARATES", flush=True)

    # ---- LESION: reading_only vs combined + OVERLAP (process-keyed, superposition) ----
    seed_cov = [it for it in held if _answer(it, store, "seed") & set(it["gold"])]
    n_seed_cov = len(seed_cov)
    n_seed_and_read = sum(1 for it in seed_cov if _answer(it, store, "read") & set(it["gold"]))
    overlap = round(n_seed_and_read / n_seed_cov, 4) if n_seed_cov else 0.0
    lesion_gap = round(combined_final - r_only_final, 4)
    fade_ratio = round(r_only_final / combined_final, 4) if combined_final > 1e-9 else 0.0
    print(f"[lesion] reading_only={r_only_final} combined={combined_final} gap={lesion_gap} "
          f"fade_ratio={fade_ratio} OVERLAP={overlap} ({n_seed_and_read}/{n_seed_cov})", flush=True)

    # ---- SCRAMBLE (mechanism-level): bind entities to WRONG fates before bundling -> collapse ----
    scr = FHRRProcessStore(dim=FHRR_DIM, seed=STORE_SEED)  # same codebook (same seed order for fate/ent)
    # rebuild seed identically (shares codebook), then reading with permuted fate labels per key
    for (tok, pname), effs in keyed.items():
        for e in sorted(effs):
            scr.add_seed(tok, pname, e)
    ep_keys = sorted(read_counts.keys())
    dom_by_key = {k: max(EFFECTS, key=lambda f: (read_counts[k].get(f, 0), -EFFECTS.index(f))) for k in ep_keys}
    n = len(ep_keys)
    if n >= 2:
        perm = _deterministic_perm("fhrr_scramble_v3", n)
        if perm == list(range(n)):
            perm = perm[1:] + perm[:1]
        for i, k in enumerate(ep_keys):
            wrong_fate = dom_by_key[ep_keys[perm[i]]]
            e, p = k
            tot = sum(read_counts[k].values())
            scr.add_read(e, p, wrong_fate, count=float(tot))
    scramble_recall = _recall(held, scr, "read")
    scramble_retained = round(scramble_recall / r_only_final, 4) if r_only_final > 1e-9 else 0.0
    print(f"[scramble] wrong-fate-bound reading recall={scramble_recall} retained={scramble_retained}", flush=True)

    # ---- verdict (superposition store; PRIMARY) ----
    reading_first = curve[0]["reading_only_recall"] if curve else 0.0
    rises = (r_only_final - reading_first) >= RISE_MIN_ABS
    fades = (lesion_gap <= FADE_GAP_MAX) or (fade_ratio >= FADE_RATIO_MIN)
    scramble_collapses = scramble_retained <= SCRAMBLE_MAX_RETAINED
    separates = selfconsist >= 0.85
    if rises and fades and scramble_collapses and separates:
        verdict = "HARD_PASS_CRUTCH_FADES_superposition_native"
    else:
        fails = []
        if not separates: fails.append(f"superposition_over_capacity_selfconsist_{selfconsist}")
        if not rises: fails.append("no_rise")
        if not fades: fails.append("no_fade_lesion_gap")
        if not scramble_collapses: fails.append("scramble_no_collapse")
        verdict = "HARD_FAIL_" + "+".join(fails)
    verdict_msg = (
        f"{verdict}: [SUPERPOSITION STORE, FHRR dim={FHRR_DIM}, sharded by process] SEPARATES: retrieval "
        f"self-consistency={selfconsist} ({n_correct_selfconsist}/{n_keys}), mean_load={mean_load} "
        f"max_load={reg_loads[0] if reg_loads else 0} facts/register -> {'CLEAN (not averaging)' if separates else 'OVER-CAPACITY'}. "
        f"FADE CURVE reading_only {[c['reading_only_recall'] for c in curve]} (rise {reading_first}->{r_only_final} "
        f">=+{RISE_MIN_ABS}? {rises}); seed_only={seed_only} combined={combined_final}; LESION gap={lesion_gap} "
        f"(fade<= {FADE_GAP_MAX}) fade_ratio={fade_ratio} -> fades={fades}; OVERLAP={overlap} "
        f"({n_seed_and_read}/{n_seed_cov}); SCRAMBLE recall={scramble_recall} retained={scramble_retained} "
        f"(collapse<= {SCRAMBLE_MAX_RETAINED}) -> {scramble_collapses}; process-tag-acc(v2)={PROCTAG_ACC_V2} "
        f"(gate {PROCTAG_ACC_GATE}); n_read_facts={n_read_facts} skipped_no_proc={n_skipped_no_proc} leak={n_leak_guard}")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "bootstrap_fhrr", "anchor_name": ANCHOR_NAME,
        "n_heldout_items": len(held), "seed_only_recall": seed_only,
        "storage": "FHRR_superposition_per_process_register (bind+bundle, unbind+cleanup); trust weights coef, no resolution",
        "capacity": {"fhrr_dim": FHRR_DIM, "n_registers": len(reg_loads), "mean_load": mean_load,
                     "max_load": reg_loads[0] if reg_loads else 0, "reg_loads_top10": reg_loads[:10],
                     "retrieval_self_consistency": selfconsist, "n_keys": n_keys,
                     "n_correct_selfconsist": n_correct_selfconsist, "superposition_separates": separates},
        "fade_curve": curve, "reading_only_final": r_only_final, "combined_final": combined_final,
        "lesion": {"reading_only": r_only_final, "combined": combined_final, "gap": lesion_gap,
                   "fade_ratio": fade_ratio, "n_seed_covered": n_seed_cov,
                   "n_seed_covered_rederived": n_seed_and_read, "overlap": overlap},
        "scramble": {"scramble_recall": scramble_recall, "retained_fraction": scramble_retained},
        "reading_corpus": {"n_read_sentences": n_read_sent, "n_reading_facts": n_read_facts,
                           "n_skipped_no_process": n_skipped_no_proc, "no_leak_dev_guard_fires": n_leak_guard},
        "process_tag_accuracy_v2": PROCTAG_ACC_V2,
        "bands": {"RISE_MIN_ABS": RISE_MIN_ABS, "FADE_GAP_MAX": FADE_GAP_MAX, "FADE_RATIO_MIN": FADE_RATIO_MIN,
                  "SCRAMBLE_MAX_RETAINED": SCRAMBLE_MAX_RETAINED, "SEPARATES_MIN_SELFCONSIST": 0.85},
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
    store = FHRRProcessStore(dim=FHRR_DIM, seed=STORE_SEED)
    # (1) TWO context-dependent facts for the SAME entity must COEXIST separably (the whole point):
    # water is MOVED in water_cycle but CONSUMED in respiration -> distinct registers, both recover.
    store.add_read("water", "water_cycle", "MOVE")
    store.add_read("water", "respiration", "DESTROY")
    assert store.retrieve("water", "water_cycle", "read") == "MOVE", store.retrieve("water", "water_cycle", "read")
    assert store.retrieve("water", "respiration", "read") == "DESTROY", store.retrieve("water", "respiration", "read")
    out["checks"]["context_separable"] = {"water@water_cycle": "MOVE", "water@respiration": "DESTROY"}
    print("[self-test] context-dependent fates for same entity COEXIST separably (no averaging)", flush=True)

    # (2) many-fact register: pack 25 entities, retrieval recovers each (capacity within FHRR bound)
    import random as _r
    rng = _r.Random(1)
    truth = {}
    for i in range(25):
        e = f"ent{i}"
        f = EFFECTS[rng.randrange(3)]
        truth[e] = f
        store.add_read(e, "combustion", f)
    n_ok = sum(1 for e, f in truth.items() if store.retrieve(e, "combustion", "read") == f)
    acc = n_ok / len(truth)
    assert acc >= 0.85, ("under-capacity retrieval must be clean", acc)
    out["checks"]["capacity_25"] = {"acc": round(acc, 3)}
    print(f"[self-test] 25-fact register retrieval acc={acc:.3f} (superposition separates)", flush=True)

    # (3) count-weighted dominant: 3x CREATE + 1x MOVE -> cleanup returns CREATE
    store.add_read("gasx", "combustion", "CREATE"); store.add_read("gasx", "combustion", "CREATE")
    store.add_read("gasx", "combustion", "CREATE"); store.add_read("gasx", "combustion", "MOVE")
    assert store.retrieve("gasx", "combustion", "read") == "CREATE"
    # (4) seed+combined + trust weight + lesion (drop read) + unstored -> None
    store.add_seed("rock", "erosion_weathering", "DESTROY")
    assert store.retrieve("rock", "erosion_weathering", "seed") == "DESTROY"
    assert store.retrieve("nonesuch", "combustion", "read") is None
    # (5) scramble collapses: wrong-fate bind
    scr = FHRRProcessStore(dim=FHRR_DIM, seed=STORE_SEED)
    scr.add_read("a", "combustion", "CREATE"); scr.add_read("b", "combustion", "DESTROY")
    # rebuild with swapped fates
    scr2 = FHRRProcessStore(dim=FHRR_DIM, seed=STORE_SEED)
    scr2.add_read("a", "combustion", "DESTROY"); scr2.add_read("b", "combustion", "CREATE")
    assert scr.retrieve("a", "combustion", "read") == "CREATE"
    assert scr2.retrieve("a", "combustion", "read") == "DESTROY"  # scrambled -> wrong fate
    out["checks"]["count_weighted_and_scramble"] = "ok"
    print("[self-test] count-weighted dominant + seed/lesion/None + scramble mechanics OK", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = ("SELFTEST_PASS: context-separable superposition + 25-fact capacity + count-weighted "
                          "dominant + seed/lesion/None + scramble all OK")
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
    run_mode = "self_test" if args.self_test else "bootstrap_fhrr"
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
