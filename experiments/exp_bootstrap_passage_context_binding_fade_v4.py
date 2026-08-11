# CELL-TEMPLATE (culmination v4; NOT a queue-dispatch cell). Implements the brain-mechanism drill's
# Section 5 ACQUISITION RESCUE (notes/research_context_binding_conjunctive_coding_and_replay_necessity
# _2026-08-11.md, Section 5e + decisive-test spec): the brain does DISCOURSE-level, not sentence-level,
# context binding -- a PERSISTING passage/situation-model context carried across a coherent passage,
# reset only at a DISCONTINUITY (prediction-error/topic-shift), with every fact bound to the active
# context. ONE VARIABLE vs sentence-level tagging: passage-scope context vs sentence-scope context.
#
# FAIRNESS LOCKDOWN (USER "make sure this test is fair" -- guards cut both ways):
#  (1) NO-LEAK (hard): DEV is NEVER read; reading = ProPara TRAIN + SimpleWiki ONLY; a per-sentence
#      guard excludes any incidental DEV-overlap (n_leak counted).
#  (2) NON-CIRCULAR tagging: BOTH arms derive the process purely from TEXT process-SIGNATURE words
#      (topic vocab); NEITHER the extractor NOR the taggers ever use the seed's consumes/produces/moves
#      FATE lists or any gold label. (The seed's fate knowledge -- the thing under test -- is never used
#      to produce a reading fact.) The ONLY difference between arms is context SCOPE: sentence-local vs
#      persisted-passage.
#  (3) HONEST METRIC: dominant-fate (FHRR unbind+cleanup returns the count-dominant fate), not recall-any.
#  (4) MEANINGFUL SCRAMBLE: reported with signal-above-scramble + modal-fate floor; adequately-powered
#      held-out so scramble can collapse.
#  (5) FAIR CORPUS: read a LARGE CONTIGUOUS (blocked, coherent) SimpleWiki span + ProPara TRAIN
#      (process-coherent); report process-passage density (facts/process, discontinuity segments).
#  (6) POWER: held-out EXPANDED to the full ProPara DEV (entity,process)->fate oracle set (all
#      participants with gold), not the 62-item bridge subset; N reported + caveated.
#  ONE VARIABLE: passage-binding vs sentence-binding; extractor (v2), store (v3 FHRR superposition,
#  proven-separable 0.956), seed, harness, corpus, held-out held identical across the two arms.
#
# WIRE-DON'T-ISLAND: reuses v2 extractor, v3 FHRR store + harness helpers, the KB process signatures,
# _select_matched (ProPara paragraph context only). Load-bearing subset: no bare except; tmp_replace;
# deterministic; self-test proves gate fires at a boundary + persists; DEV never read.
"""exp_bootstrap_passage_context_binding_fade_v4 -- does discourse-level passage-context binding (vs
sentence tagging) recover the process signal and let the crutch fade, under a fairness lockdown?
Two arms (sentence-scope vs passage-scope) on identical facts/corpus/store/held-out. Modes:
--self-test / (no flag)=the fair passage-binding fade run.
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

ANCHOR_NAME = "bootstrap_passage_context_binding_fade_v4"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from experiments.exp_propara_process_keyed_lookup_v1 import _select_matched  # noqa: E402
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import _load_kb, _toks, _norm_toks  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _deterministic_perm,
)
from experiments.exp_propara_schema_learned_grounded_binder_v1 import _gold_effects_from_multiset  # noqa: E402
from propara_trap_check import build_step_rows  # noqa: E402
from experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision import (  # noqa: E402
    extract_facts_strict, _load_or_build_frontend, _singularize,
)
from experiments.exp_stated_entity_fate_reading_extractor_v1 import _SCI_TOPIC, _WORD, FATE_VERB_LEXICON  # noqa: E402
from experiments.exp_bootstrap_process_conditioned_reading_fade_v2 import _seed_maps  # noqa: E402
from experiments.exp_bootstrap_fhrr_superposition_fade_v3 import (  # noqa: E402
    FHRRProcessStore, EFFECTS, CHECKPOINTS, RISE_MIN_ABS, FADE_GAP_MAX, FADE_RATIO_MIN,
    SCRAMBLE_MAX_RETAINED, FHRR_DIM, STORE_SEED, _answer, _recall,
)

PROCTAG_ACC_V2 = 0.7167
SKIP_RATE_V2 = 0.8555
PROCTAG_ACC_GATE = 0.70
CTX_DECAY = 0.6
CTX_MIN_EVIDENCE = 1.5
CTX_RESET_STRENGTH = 2.0
SENT_MIN_HITS = 1   # sentence-scope arm: a single process-signature hit tags the sentence (keyword-prone, = v2 shape)


# ============================================================================ expanded, no-leak held-out
def _build_heldout_expanded(procs):
    """Full ProPara DEV (entity,process)->fate held-out (oracle multiset gold, all participants with a
    gold fate) -- adequate power vs the 62-item bridge subset. Process = _select_matched over the DEV
    paragraph (text-derived process identity; the FATE is the oracle gold, never used to tag reading)."""
    paragraphs = _load_split("dev")
    steps = build_step_rows(paragraphs)
    gold_by_key = _gold_effects_from_multiset(_oracle_event_multiset(steps))
    matched = {str(p["para_id"]): _select_matched(p, procs) for p in paragraphs}
    held = []
    for para in paragraphs:
        pid = str(para["para_id"])
        for pp in para["participants"]:
            gold = {e for e in gold_by_key.get((pid, pp), set()) if e in EFFECTS}
            if not gold:
                continue
            variants = sorted({t for t in _norm_toks(pp) if len(t) > 2})
            if not variants:
                continue
            held.append({"pid": pid, "participant": pp, "variants": variants,
                         "gold": sorted(gold), "procs": matched[pid]})
    return held, paragraphs


# ============================================================================ process signatures (text-only)
def _signature_sets(procs) -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {}
    for name, d in procs.items():
        s: Set[str] = set()
        for w in d.get("signature", []):
            for t in _toks(str(w)):
                s.add(t)
        out[name] = s
    return out


def _sentence_proc(sentence: str, sig: Dict[str, Set[str]], min_hits: int = SENT_MIN_HITS) -> Optional[str]:
    """SENTENCE-SCOPE arm (the v2 baseline shape): tag by THIS sentence's own top signature-hit process
    (>= min_hits), else None. Same TEXT signal as the passage arm; the ONLY difference from the passage
    arm is the absence of cross-sentence persistence/accumulation. Non-circular (signatures only)."""
    toks = set(_WORD.findall(sentence.lower()))
    hits = {p: len(toks & s) for p, s in sig.items()}
    hits = {p: h for p, h in hits.items() if h >= min_hits}
    return max(hits, key=hits.get) if hits else None


class PassageContext:
    """PASSAGE-SCOPE arm: persistent discourse-level context register -- accumulate per-sentence
    signature-hit cues with cross-sentence DRIFT (decay), declare the argmax as the ACTIVE process (or
    None below min-evidence), and fire a DISCONTINUITY RESET when a sentence strongly signals a
    DIFFERENT process (topic-shift). Fast exact signature-hit cue (accumulation IS where the discourse
    power lives). Non-circular: uses process-SIGNATURE topic vocab only, never fate/role lists."""

    def __init__(self, sig_sets, decay=CTX_DECAY, min_evidence=CTX_MIN_EVIDENCE, reset_strength=CTX_RESET_STRENGTH):
        self.sig = sig_sets
        self.decay = decay
        self.min_evidence = min_evidence
        self.reset_strength = reset_strength
        self.cue: Dict[str, float] = defaultdict(float)
        self.active: Optional[str] = None
        self.n_reset = 0
        self.reset_log: List[Dict] = []

    def _recompute(self):
        if self.cue:
            best = max(self.cue, key=self.cue.get)
            self.active = best if self.cue[best] >= self.min_evidence else None
        else:
            self.active = None

    def observe(self, sentence: str):
        toks = set(_WORD.findall(sentence.lower()))
        hits = {p: len(toks & s) for p, s in self.sig.items()}
        hits = {p: h for p, h in hits.items() if h > 0}
        top_new = max(hits, key=hits.get) if hits else None
        if (top_new is not None and hits[top_new] >= self.reset_strength
                and self.active is not None and top_new != self.active):
            self.n_reset += 1
            if len(self.reset_log) < 400:
                self.reset_log.append({"sentence": sentence[:160], "old": self.active, "new": top_new, "hits": hits[top_new]})
            self.cue = defaultdict(float)
            for p, h in hits.items():
                self.cue[p] += h
        else:
            for p in list(self.cue):
                self.cue[p] *= self.decay
            for p, h in hits.items():
                self.cue[p] += h
        self._recompute()


def _fate_bearing(toks: Set[str]) -> bool:
    return any(lemma_verb(t) in FATE_VERB_LEXICON for t in toks)


# ============================================================================ run (two arms, identical facts)
def _new_store(keyed):
    st = FHRRProcessStore(dim=FHRR_DIM, seed=STORE_SEED)
    for (tok, pname), effs in keyed.items():
        for e in sorted(effs):
            st.add_seed(tok, pname, e)
    return st


def _fade_block(held, store, keyed, read_counts, tag):
    seed_only = _recall(held, store, "seed")
    r = _recall(held, store, "read")
    c = _recall(held, store, "combined")
    seed_cov = [it for it in held if _answer(it, store, "seed") & set(it["gold"])]
    n_sc = len(seed_cov)
    n_sr = sum(1 for it in seed_cov if _answer(it, store, "read") & set(it["gold"]))
    overlap = round(n_sr / n_sc, 4) if n_sc else 0.0
    gap = round(c - r, 4)
    fade_ratio = round(r / c, 4) if c > 1e-9 else 0.0
    # scramble on this arm's read_counts
    scr = _new_store(keyed)
    ep = sorted(read_counts.keys())
    dom = {k: max(EFFECTS, key=lambda f: (read_counts[k].get(f, 0), -EFFECTS.index(f))) for k in ep}
    if len(ep) >= 2:
        perm = _deterministic_perm(f"passage_scramble_v4_{tag}", len(ep))
        if perm == list(range(len(ep))):
            perm = perm[1:] + perm[:1]
        for i, k in enumerate(ep):
            e, p = k
            scr.add_read(e, p, dom[ep[perm[i]]], count=float(sum(read_counts[k].values())))
    scr_recall = _recall(held, scr, "read")
    scr_retained = round(scr_recall / r, 4) if r > 1e-9 else 0.0
    signal_above_scramble = round(r - scr_recall, 4)
    return {"seed_only": seed_only, "reading_only": r, "combined": c, "lesion_gap": gap,
            "fade_ratio": fade_ratio, "overlap": overlap, "n_seed_covered": n_sc,
            "n_seed_rederived": n_sr, "scramble_recall": scr_recall, "scramble_retained": scr_retained,
            "signal_above_scramble": signal_above_scramble}


def run(max_simplewiki_lines: int = 900000, extract_budget: int = 16000,
        proctag_sample: int = 120, seed: int = 20260811) -> Dict:
    t0 = time.time()
    kb = _load_kb()
    procs = kb["processes"]
    sig = _signature_sets(procs)
    held, dev_paragraphs = _build_heldout_expanded(procs)
    dev_sentences = {s.strip() for para in dev_paragraphs for s in para["sentence_texts"]}
    keyed, seed_global, seed_vocab = _seed_maps(procs)
    gen = _load_or_build_frontend()
    train_paragraphs = _load_split("train")
    print(f"[held-out] EXPANDED to {len(held)} DEV (entity,process)->fate items (was 62 bridge)", flush=True)

    st_pass = _new_store(keyed)   # PASSAGE-scope arm
    st_sent = _new_store(keyed)   # SENTENCE-scope arm (baseline)
    rc_pass: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    rc_sent: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    proctag_samples: List[Dict] = []
    passage_facts_per_proc = Counter()
    n_tag_pass = n_tag_sent = n_skip_pass = n_skip_sent = n_leak = n_units = 0
    rng_s = random.Random(seed)
    curve = []
    ckpts = list(CHECKPOINTS)
    next_ckpt = 0

    def _ingest(entity, fate, sentence, passage_proc, sentence_proc, src):
        nonlocal n_tag_pass, n_tag_sent, n_skip_pass, n_skip_sent
        if passage_proc is not None:
            st_pass.add_read(entity, passage_proc, fate, count=1.0)
            rc_pass[(entity, passage_proc)][fate] += 1
            n_tag_pass += 1
            passage_facts_per_proc[passage_proc] += 1
            if len(proctag_samples) < proctag_sample:
                proctag_samples.append({"entity": entity, "process": passage_proc, "fate": fate,
                                        "sentence": sentence, "src": src})
            elif rng_s.random() < 0.02:
                proctag_samples[rng_s.randrange(proctag_sample)] = {"entity": entity, "process": passage_proc,
                                                                    "fate": fate, "sentence": sentence, "src": src}
        else:
            n_skip_pass += 1
        if sentence_proc is not None:
            st_sent.add_read(entity, sentence_proc, fate, count=1.0)
            rc_sent[(entity, sentence_proc)][fate] += 1
            n_tag_sent += 1
        else:
            n_skip_sent += 1

    def _ckpt():
        nonlocal next_ckpt
        if next_ckpt < len(ckpts) and n_units >= ckpts[next_ckpt]:
            rp = _recall(held, st_pass, "read")
            rs = _recall(held, st_sent, "read")
            curve.append({"n_units": n_units, "reading_only_passage": rp, "reading_only_sentence": rs})
            print(f"[curve] units={n_units} passage={rp} sentence={rs}", flush=True)
            next_ckpt += 1

    # ---- ProPara TRAIN: paragraph = coherent passage (paragraph-level context = both arms' process)
    for para in train_paragraphs:
        pprocs = _select_matched(para, procs)
        for s in para.get("sentence_texts", []):
            s = s.strip()
            if not s:
                continue
            if s in dev_sentences:
                n_leak += 1
                continue
            toks = set(_WORD.findall(s.lower()))
            if not _fate_bearing(toks):
                continue
            n_units += 1
            facts = extract_facts_strict(gen, s)
            pproc = pprocs[0] if pprocs else None       # passage = paragraph process
            sproc = _sentence_proc(s, sig)              # sentence-scope tag from THIS sentence
            for f in facts:
                _ingest(f["entity_head"], f["fate"], s, pproc, sproc, "paragraph")
            _ckpt()

    # ---- SimpleWiki: CONTIGUOUS (blocked/coherent) stream + persistent discontinuity-gated passage ctx
    ctx = PassageContext(sig)
    n_lines = 0
    with open(SIMPLEWIKI_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            n_lines += 1
            if n_lines > max_simplewiki_lines or n_tag_pass >= extract_budget:
                break
            if not (8 <= len(s) <= 400):
                continue
            ctx.observe(s)  # maintain passage context over EVERY contiguous sentence
            if not _SCI_TOPIC.search(s):
                continue
            toks = set(_WORD.findall(s.lower()))
            if not _fate_bearing(toks):
                continue
            if s in dev_sentences:
                n_leak += 1
                continue
            n_units += 1
            facts = extract_facts_strict(gen, s)
            pproc = ctx.active                # passage-scope (persisted)
            sproc = _sentence_proc(s, sig)    # sentence-scope (this sentence only)
            for f in facts:
                _ingest(f["entity_head"], f["fate"], s, pproc, sproc, "passage")
            _ckpt()

    # ---- fade blocks for both arms ----
    fade_pass = _fade_block(held, st_pass, keyed, rc_pass, "passage")
    fade_sent = _fade_block(held, st_sent, keyed, rc_sent, "sentence")
    curve.append({"n_units": n_units, "reading_only_passage": fade_pass["reading_only"],
                  "reading_only_sentence": fade_sent["reading_only"], "final": True})
    skip_pass = round(n_skip_pass / max(n_tag_pass + n_skip_pass, 1), 4)
    skip_sent = round(n_skip_sent / max(n_tag_sent + n_skip_sent, 1), 4)
    n_proc_passages = len([p for p, c in passage_facts_per_proc.items() if c > 0])

    print(f"[PASSAGE arm] tagged={n_tag_pass} skip_rate={skip_pass} reading_only={fade_pass['reading_only']} "
          f"combined={fade_pass['combined']} seed_only={fade_pass['seed_only']} gap={fade_pass['lesion_gap']} "
          f"overlap={fade_pass['overlap']} scramble_retained={fade_pass['scramble_retained']} "
          f"signal_above_scr={fade_pass['signal_above_scramble']}", flush=True)
    print(f"[SENTENCE arm] tagged={n_tag_sent} skip_rate={skip_sent} reading_only={fade_sent['reading_only']} "
          f"gap={fade_sent['lesion_gap']} overlap={fade_sent['overlap']} scramble_retained={fade_sent['scramble_retained']}", flush=True)
    print(f"[corpus] simplewiki_lines={n_lines} discontinuity_resets={ctx.n_reset} "
          f"process_passages_covered={n_proc_passages}/18 facts_per_process={dict(passage_facts_per_proc.most_common())}", flush=True)

    # ---- dumps ----
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dump = os.path.join(OUTPUT_DIR, "_passage_proctag_for_handcheck.json")
    with open(dump, "w", encoding="utf-8") as fp:
        json.dump({"n_tagged": n_tag_pass, "sample": proctag_samples}, fp, indent=2)
    gate_dump = os.path.join(OUTPUT_DIR, "_discontinuity_gate_firings.json")
    with open(gate_dump, "w", encoding="utf-8") as fp:
        json.dump({"n_reset": ctx.n_reset, "sample": ctx.reset_log[:120]}, fp, indent=2)
    print(f"[design-gate] dumped {len(proctag_samples)} passage-tags -> {dump}; {min(ctx.n_reset,120)} gate firings", flush=True)

    fp0 = fade_pass
    rises = (fp0["reading_only"] - (curve[0]["reading_only_passage"] if curve else 0.0)) >= RISE_MIN_ABS
    fades = (fp0["lesion_gap"] <= FADE_GAP_MAX) or (fp0["fade_ratio"] >= FADE_RATIO_MIN)
    scramble_collapses = fp0["scramble_retained"] <= SCRAMBLE_MAX_RETAINED
    verdict = "PENDING_PASSAGE_TAG_HANDCHECK"
    verdict_msg = (
        f"[FAIR passage-context binding, N_heldout={len(held)}] discontinuity resets={ctx.n_reset}; "
        f"PASSAGE arm: skip={skip_pass} (vs SENTENCE arm {skip_sent}, v2 {SKIP_RATE_V2}); tagged={n_tag_pass}; "
        f"reading_only={fp0['reading_only']} (SENTENCE arm {fade_sent['reading_only']}); seed_only={fp0['seed_only']} "
        f"combined={fp0['combined']}; LESION gap={fp0['lesion_gap']} fade_ratio={fp0['fade_ratio']} -> fades={fades}; "
        f"OVERLAP={fp0['overlap']} ({fp0['n_seed_rederived']}/{fp0['n_seed_covered']}); SCRAMBLE retained="
        f"{fp0['scramble_retained']} signal_above_scr={fp0['signal_above_scramble']} -> collapses={scramble_collapses}; "
        f"process_passages={n_proc_passages}/18; PASSAGE-tag accuracy pending hand-check (vs v2 {PROCTAG_ACC_V2})")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "bootstrap_passage", "anchor_name": ANCHOR_NAME,
        "fairness_guards": {
            "no_leak_dev_never_read": True, "n_leak_guard_fires": n_leak,
            "non_circular_tagging": "both arms tag process from TEXT signature words only; extractor + taggers "
                                    "never use the seed consumes/produces/moves fate lists or gold",
            "honest_metric": "dominant-fate (FHRR unbind+cleanup), not recall-any",
            "meaningful_scramble": "signal_above_scramble reported; held-out expanded for power",
            "fair_corpus": f"contiguous blocked SimpleWiki ({n_lines} lines) + ProPara TRAIN; "
                           f"{n_proc_passages}/18 processes covered by reading",
            "power": f"held-out EXPANDED to {len(held)} items (was 62); still ProPara-DEV-bounded, caveat N",
            "one_variable": "passage-scope vs sentence-scope context; extractor/store/seed/harness/corpus/held-out identical",
        },
        "n_heldout_items": len(held),
        "arms": {"passage": fade_pass, "sentence": fade_sent},
        "coverage": {"passage_tagged": n_tag_pass, "passage_skip_rate": skip_pass,
                     "sentence_tagged": n_tag_sent, "sentence_skip_rate": skip_sent,
                     "skip_rate_v2": SKIP_RATE_V2, "n_discontinuity_resets": ctx.n_reset,
                     "n_process_passages_covered": n_proc_passages, "n_simplewiki_lines": n_lines,
                     "facts_per_process": dict(passage_facts_per_proc.most_common())},
        "fade_curve": curve,
        "design_gate": {"passage_proctag_dump": dump, "discontinuity_gate_dump": gate_dump,
                        "n_proctag_sample": len(proctag_samples), "proctag_accuracy_v2": PROCTAG_ACC_V2,
                        "PROCTAG_ACC_GATE": PROCTAG_ACC_GATE, "PASSAGE_TAG_TARGET": 0.85,
                        "note": "passage-tag accuracy hand-checked by operator; verdict finalized after"},
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
    sig = _signature_sets(procs)
    assert "burn" in sig["combustion"] and "digest" in sig["digestion"]

    ctx = PassageContext(sig)
    ctx.observe("Combustion is the burning of fuel with oxygen in a fire.")
    assert ctx.active == "combustion", (ctx.active, dict(ctx.cue))
    ctx.observe("This releases a lot of it very quickly.")  # signal-less -> PERSIST
    assert ctx.active == "combustion", ("must persist across signal-less sentence", ctx.active)
    n0 = ctx.n_reset
    ctx.observe("In digestion, the stomach and intestine digest food into nutrients with enzymes.")
    assert ctx.n_reset == n0 + 1 and ctx.active == "digestion", (ctx.n_reset, ctx.active)
    n1 = ctx.n_reset
    ctx.observe("The nutrients are absorbed by the body.")  # non-boundary -> no reset
    assert ctx.n_reset == n1
    ctx2 = PassageContext(sig)
    ctx2.observe("The weather was nice on Tuesday.")
    assert ctx2.active is None
    out["checks"]["passage_gate"] = "persist+fire+not-triggerhappy+abstain OK"
    print("[self-test] passage gate: persist + fire-at-boundary + not-trigger-happy + abstain OK", flush=True)

    # sentence-scope arm: single signature hit tags; non-signal -> None
    assert _sentence_proc("The fire burns the wood.", sig) == "combustion"
    assert _sentence_proc("The cat sat on the mat.", sig) is None
    out["checks"]["sentence_arm"] = "ok"
    # expanded held-out builds + is bigger than 62
    held, _ = _build_heldout_expanded(procs)
    assert len(held) >= 62, len(held)
    out["checks"]["heldout_n"] = len(held)
    print(f"[self-test] sentence arm OK; expanded held-out N={len(held)}", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = f"SELFTEST_PASS: passage gate + sentence arm + expanded held-out (N={len(held)}) OK"
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--max-lines", type=int, default=900000)
    ap.add_argument("--extract-budget", type=int, default=16000)
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test else "bootstrap_passage"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)
    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run(max_simplewiki_lines=args.max_lines, extract_budget=args.extract_budget)
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
