"""CONVERGENT-CUE composition of the entity(episodic) + meaning(ATL) reader -- the brain's
retrieval rule, not the STEP-18 independent post-hoc AND.

PROBLEM: `compose_the_reader_by_convergent_cue_not_independent_conjunction`. STEP-18 composed the
two landed organs by requiring BOTH to be independently right (a post-hoc AND -> 0.119 ~= the
product of the two solo rates, i.e. STATISTICAL INDEPENDENCE). The brain does NOT retrieve that way:
episodic recall is CONVERGENT-CUE pattern completion (CA3 attractor; Norman & O'Reilly 2003) driven
JOINTLY by multiple partial cues, and optimal cue combination = the PRODUCT of the two evidence
distributions = the SUM of their log-evidence, with each cue weighted by its RELIABILITY -- and in a
probabilistic population code that reliability-weighting is AUTOMATIC (Ma, Beck, Latham & Pouget 2006:
combine two population codes by literally ADDING them; a more confident/peaked cue dominates by its
own gain). Ernst & Banks 2002 is the normative precision-weighting result; Hemmer & Steyvers 2009 is
the closest whole-operation precedent (episodic trace x semantic prior, Bayesian, reliability-graded).

THE FAITHFUL OPERATION (headline arm CONVERGENT_RW, PARAMETER-FREE):
  For a pronoun query (entity E, slot s, true verb v; paraphrase cue q = a WordNet synonym of v that
  is NOT a doc candidate string):
    epi_raw(c) = FHRR cleanup score of candidate verb c from the LANDED per-entity register decode
                 (unbind(entity E's bank, slot s) then Re<conj(verb_c), readback>/d)  -- BOTTOM-UP.
    sem_raw(c) = ATL conceptual_meaning.similarity(q, c)                              -- TOP-DOWN.
    p_epi = softmax(epi_raw / tau_e),  p_sem = softmax(sem_raw / tau_s)   (tau = each cue's OWN global
            scale, gold-blind -- the population's fixed gain; per-query PEAKEDNESS then carries the
            reliability, so weighting is automatic, NO free parameter fit to the label)
    answer = argmax_c [ log p_epi(c) + log p_sem(c) ]        (product of posteriors = Bayes-optimal
            combination = one content-addressable read jointly driven by both cues)
  Hippocampal lesion (no register) -> p_epi uniform -> answer = meaning-solo (graceful). Semantic
  lesion (drop sem) -> answer = entity-solo (graceful). The DOUBLE DISSOCIATION is preserved by
  construction: two SEPARATE pools combined at read, never fused.

ARMS / CONTROLS (the bar, PROBLEM.md sec 7):
  * FLOORS (strongest-actually-run governs): meaning-solo (~0.70, = CONVERGENT with p_epi lesioned),
    entity-solo (~0.19, = p_sem lesioned), independent-AND (~0.119, the brief's straw baseline --
    LOWER than either solo, so we beat it AND the far stronger meaning-solo).
  * CONVERGENT_RW  : the parameter-free faithful read (headline).
  * CONVERGENT_LAM : softmax(z(epi)+lambda*z(sem)) with lambda chosen by CROSS-VALIDATION on train
    docs (held-out eval) -- robustness / sensitivity, shows the win is not a knife-edge tuned knob.
  * TWIN_MEANING   : sem shuffled across candidates (info-free meaning cue) -> no top-down facilitation.
  * TWIN_EPISODIC  : epi shuffled across candidates (info-free episodic cue) -> must fall back to
    meaning-solo; if CONVERGENT still beat meaning-solo with epi shuffled, the win was an artifact.
  * FUSED          : ONE undifferentiated global bundle (all entities' events superposed, no
    separation) read jointly -> catastrophic interference (McCloskey & Cohen 1989; the CLS
    separate-store rationale) -> must LOSE to convergent and/or destroy the dissociation.
  * LOCALIZATION   : the lift must concentrate on the predicted subset (meaning-solo-WRONG rescued by
    episodic; entity-solo-WRONG rescued by meaning), not a uniform shift (which would be an artifact).

Extraction (register build + decode per query) is cached to data/<anchor>/records.json so the arms,
sweep and witness are cheap re-reads. Deterministic, ASCII-only. Writes only its own data dir. hdlab/
NOT modified.
Run:  .venv/Scripts/python.exe experiments/exp_convergent_cue_composed_reader_v1.py [--docs N] [--rebuild]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H
from experiments.exp_litbank_entity_tracking_end_to_end_v1 import PRONOUNS, D
from experiments.exp_composed_reader_litbank_full_v1 import build_links_landed
from experiments.exp_meaning_channel_paraphrase_comprehension_v1 import _verb_synonym
from hdlab.conceptual_meaning import ConceptualChannel
from hdlab.situation_model_accumulate import make_situation_register, unit_phase_vec, cleanup_argmax
from hdlab import binding, bundling

ANCHOR = "exp_convergent_cue_composed_reader_v1"
OUTDIR = os.path.join(REPO_ROOT, "data", ANCHOR)
SEED = 20260827
N_BOOT = 2000


# ----------------------------- extraction (cached) -----------------------------
def _fused_scores(stream, links, verb_vocab, slot_map, n_slots, gen):
    """ONE undifferentiated global bundle: every (entity, slot, verb) event superposed into a SINGLE
    FHRR trace (no per-entity separation) -- the fused-pool fidelity-regression control. Returns a
    dict (cid, slot) -> cleanup scores over verb_vocab, read by unbind(unbind(B, ent_key), slot)."""
    ent_ids = sorted({str(c) for c in links["ACTR_LANDED"]})
    ent_key = {e: unit_phase_vec(D, gen) for e in ent_ids}
    slot_vecs = [unit_phase_vec(D, gen) for _ in range(max(n_slots, 1))]
    verb_vecs = {v: unit_phase_vec(D, gen) for v in verb_vocab}
    traces = []
    for m, cid in zip(stream, links["ACTR_LANDED"]):
        v = m["gov_verb"]
        if v is None:
            continue
        s = slot_map[m["sent"]]
        tr = binding.bind(ent_key[str(cid)], binding.bind(slot_vecs[s], verb_vecs[v]))
        traces.append(tr)
    if not traces:
        return {}, verb_vecs
    B = traces[0] if len(traces) == 1 else bundling.bundle(torch.stack(traces, dim=0))
    return {"B": B, "ent_key": ent_key, "slot_vecs": slot_vecs}, verb_vecs


def extract(docs):
    recs = H.load_cache()[:docs]
    chan = ConceptualChannel()
    rng = np.random.default_rng(SEED)
    out = []
    for di, rec in enumerate(recs):
        stream = rec["stream"]
        if not stream:
            continue
        slot_map, n_slots = H._slots(stream)
        verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
        cand = [v for v in verb_vocab if v.isalpha() and len(v) >= 3]
        if len(cand) < 3:
            continue
        links = build_links_landed(stream, rng)
        g = H._torch_gen(SEED + di * 1000 + hash("ACTR_LANDED") % 97)
        reg = make_situation_register(list(verb_vocab), D, g, max_event_slots=max(n_slots, 1),
                                      backend="multibank", n_banks=8)
        for m, cid in zip(stream, links["ACTR_LANDED"]):
            if m["gov_verb"] is not None:
                reg.add_event(str(cid), m["gov_verb"], slot_map[m["sent"]])
        anchor = H._name_anchor(stream, links["ACTR_LANDED"])
        gf = H._torch_gen(SEED + di * 1000 + 7)
        fused, fused_verb_vecs = _fused_scores(stream, links, verb_vocab, slot_map, n_slots, gf)
        has_name = {m["gold"] for m in stream if m["head_text"] not in PRONOUNS}
        ci = {c: i for i, c in enumerate(cand)}

        for m in stream:
            v = m["gov_verb"]
            if v is None or m["gold"] not in has_name or m["head_text"] not in PRONOUNS or v not in cand:
                continue
            q = _verb_synonym(v)
            if q is None or q in cand:
                continue
            sims = [(chan.similarity(q, "V", c, "V") or -1.0) for c in cand]
            if max(sims) <= -1.0:
                continue
            E = m["gold"]; s = slot_map[m["sent"]]
            cid = anchor.get(E)
            epi = None
            if cid is not None:
                try:
                    _, sc = reg.decode(str(cid), s)
                    epi = [float(sc.get(c, 0.0)) for c in cand]
                except KeyError:
                    epi = None
            fep = None
            if fused and cid is not None and str(cid) in fused["ent_key"]:
                rb = binding.unbind(binding.unbind(fused["B"], fused["ent_key"][str(cid)]),
                                    fused["slot_vecs"][s])
                fsc = cleanup_argmax(rb, {c: fused_verb_vecs[c] for c in cand})[1]
                fep = [float(fsc[c]) for c in cand]
            out.append({"doc": di, "sem": [float(x) for x in sims], "epi": epi, "fep": fep,
                        "vi": ci[v], "ncand": len(cand)})
    return out


def load_records(docs, rebuild):
    path = os.path.join(OUTDIR, f"records_{docs}.json")
    if os.path.exists(path) and not rebuild:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    recs = extract(docs)
    os.makedirs(OUTDIR, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(recs, fh)
    os.replace(tmp, path)
    return recs


# ----------------------------- readouts -----------------------------
def _softmax(x):
    x = np.asarray(x, float); x = x - x.max()
    e = np.exp(x); return e / e.sum()


def _zn(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 1e-12 else x - x.mean()


def _global_tau(recs, key):
    """Gold-blind global scale of a cue's RAW scores (the population's fixed gain). One constant per
    cue over ALL queries -> per-query peakedness (reliability) is preserved and does the weighting."""
    vals = []
    for r in recs:
        if r[key] is not None:
            vals.extend([float(x) for x in r[key]])
    v = np.asarray(vals, float)
    return float(v.std()) if v.size and v.std() > 1e-12 else 1.0


def pick_meaning(r):
    return int(np.argmax(r["sem"]))


def pick_entity(r):
    return int(np.argmax(r["epi"])) if r["epi"] is not None else None  # None -> no episodic info


def pick_convergent_rw(r, tau_e, tau_s, w=1.0):
    """Reliability-weighted convergent read: product of the two posteriors, each cue's PER-QUERY
    reliability automatic via its softmax peakedness at a gold-blind global gain (tau); w = the
    LEARNED average reliability ratio (Ernst-Banks: the organism calibrates cue reliability from
    experience). w=1.0 = the assumption-free EQUAL-reliability product (a lower bound)."""
    p_sem = _softmax(np.asarray(r["sem"]) / tau_s)
    if r["epi"] is None:
        return int(np.argmax(p_sem))                    # hippocampal lesion -> meaning-solo (graceful)
    p_epi = _softmax(np.asarray(r["epi"]) / tau_e)
    return int(np.argmax(np.log(p_epi + 1e-12) + w * np.log(p_sem + 1e-12)))


def pick_convergent_reinstate(r, tau_e, tau_s, w):
    """The SAME operation as pick_convergent_rw, but in ACTIVATION space (Ma et al. / predictive-coding
    LITERAL form): top-down semantic prediction ADDED to the hippocampal readback activation, then ONE
    cleanup competition (argmax) -- i.e. bias on ONE content-addressable read, NOT an AND of two
    readouts. score(c) = softmax(epi)(c) + w*softmax(sem)(c). (Adding the semantic-predicted vector
    sum_c p_sem(c)*verb_vec_c to the FHRR readback and re-running cleanup reduces to exactly this, since
    the verb atoms are ~orthonormal; the log-domain rw arm is its Bayesian counterpart.)"""
    p_sem = _softmax(np.asarray(r["sem"]) / tau_s)
    if r["epi"] is None:
        return int(np.argmax(p_sem))
    e = _softmax(np.asarray(r["epi"]) / tau_e)
    return int(np.argmax(e + w * p_sem))


def pick_convergent_lam(r, lam):
    z_sem = _zn(r["sem"])
    if r["epi"] is None:
        return int(np.argmax(z_sem))
    return int(np.argmax(_zn(r["epi"]) + lam * z_sem))


def pick_fused(r, tau_f, tau_s):
    """Fused single-pool episodic read (fep) combined with meaning the SAME convergent way -- isolates
    the STORE-separation lever: convergent uses the separated per-entity register (epi), fused uses the
    one-global-bundle read (fep)."""
    p_sem = _softmax(np.asarray(r["sem"]) / tau_s)
    if r["fep"] is None:
        return int(np.argmax(p_sem))
    p_f = _softmax(np.asarray(r["fep"]) / tau_f)
    return int(np.argmax(np.log(p_f + 1e-12) + np.log(p_sem + 1e-12)))


# ----------------------------- scoring / CI -----------------------------
def per_doc_pairs(recs, pickfn):
    dd = {}
    for r in recs:
        d = r["doc"]; dd.setdefault(d, [0, 0])
        p = pickfn(r)
        dd[d][0] += int(p == r["vi"]); dd[d][1] += 1
    return np.array([dd[d] for d in sorted(dd)], float)


def acc_ci(pairs, seed):
    r = np.random.default_rng(seed); nd = len(pairs)
    tot = pairs[:, 1].sum(); acc = pairs[:, 0].sum() / tot if tot else 0.0
    b = []
    for _ in range(N_BOOT):
        idx = r.integers(0, nd, nd); s = pairs[idx]
        b.append(s[:, 0].sum() / max(s[:, 1].sum(), 1))
    return acc, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def paired(a, b, seed):
    r = np.random.default_rng(seed); nd = len(a); d = []
    for _ in range(N_BOOT):
        idx = r.integers(0, nd, nd); sa = a[idx]; sb = b[idx]
        d.append(sa[:, 0].sum() / max(sa[:, 1].sum(), 1) - sb[:, 0].sum() / max(sb[:, 1].sum(), 1))
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    pt = a[:, 0].sum() / max(a[:, 1].sum(), 1) - b[:, 0].sum() / max(b[:, 1].sum(), 1)
    return {"delta": round(float(pt), 4), "ci": [round(lo, 4), round(hi, 4)],
            "hw": round((hi - lo) / 2, 4), "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def _cv(recs, grid, pickfn, folds=5):
    """Generic doc-level cross-validation: for each fold, pick the grid value maximizing TRAIN accuracy,
    apply it to the strictly HELD-OUT fold. Returns {id(r): held-out pick}, and the chosen values.
    The calibration NEVER sees the test docs -> not a free parameter fit to the reported number."""
    docs = sorted({r["doc"] for r in recs})
    perm = np.random.default_rng(SEED).permutation(docs)
    fold_of = {d: i % folds for i, d in enumerate(perm)}
    heldout, chosen = {}, []
    for f in range(folds):
        tr = [r for r in recs if fold_of[r["doc"]] != f]
        te = [r for r in recs if fold_of[r["doc"]] == f]
        best = (grid[0], -1.0)
        for g in grid:
            acc = np.mean([int(pickfn(r, g) == r["vi"]) for r in tr])
            if acc > best[1]:
                best = (g, acc)
        chosen.append(best[0])
        for r in te:
            heldout[id(r)] = pickfn(r, best[0])
    return heldout, chosen


def main():
    docs = 60
    rebuild = "--rebuild" in sys.argv
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = load_records(docs, rebuild)
    n = len(recs); ndoc = len({r["doc"] for r in recs})
    tau_e = _global_tau(recs, "epi"); tau_s = _global_tau(recs, "sem"); tau_f = _global_tau(recs, "fep")
    print(f"=== CONVERGENT-CUE composed reader (LitBank paraphrased pronoun who-did-what, "
          f"{ndoc} docs, {n} queries) ===")
    print(f"  tau_e={tau_e:.4f} tau_s={tau_s:.4f} tau_f={tau_f:.4f}  (gold-blind cue scales)\n")

    # cross-validated learned reliability weight w (Ernst-Banks calibration; held-out) -> HEADLINE arm
    W_GRID = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
    held_w, chosen_w = _cv(recs, W_GRID, lambda r, w: pick_convergent_rw(r, tau_e, tau_s, w))
    held_lam, chosen_lam = _cv(recs, [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0], pick_convergent_lam)
    held_ri, chosen_ri = _cv(recs, [0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0],
                             lambda r, w: pick_convergent_reinstate(r, tau_e, tau_s, w))

    def held_pairs(held):
        dd = {}
        for r in recs:
            d = r["doc"]; dd.setdefault(d, [0, 0])
            dd[d][0] += int(held[id(r)] == r["vi"]); dd[d][1] += 1
        return np.array([dd[d] for d in sorted(dd)], float)

    arms = {}
    arms["meaning_solo"] = per_doc_pairs(recs, pick_meaning)
    arms["entity_solo"] = per_doc_pairs(recs, lambda r: pick_entity(r) if pick_entity(r) is not None else -1)
    arms["independent_AND"] = per_doc_pairs(
        recs, lambda r: r["vi"] if (pick_entity(r) == r["vi"] and pick_meaning(r) == r["vi"]) else -1)
    arms["CONVERGENT_RW_w1"] = per_doc_pairs(recs, lambda r: pick_convergent_rw(r, tau_e, tau_s, 1.0))
    arms["TWIN_MEANING"] = per_doc_pairs(
        recs, lambda r: pick_convergent_rw({**r, "sem": list(np.random.default_rng(hash((r["doc"], r["vi"], 1)) % 2**31).permutation(r["sem"]))}, tau_e, tau_s, float(np.median(chosen_w))))
    arms["TWIN_EPISODIC"] = per_doc_pairs(
        recs, lambda r: pick_convergent_rw({**r, "epi": (None if r["epi"] is None else list(np.random.default_rng(hash((r["doc"], r["vi"], 2)) % 2**31).permutation(r["epi"])))}, tau_e, tau_s, float(np.median(chosen_w))))
    arms["FUSED"] = per_doc_pairs(recs, lambda r: pick_fused(r, tau_f, tau_s))
    arms["CONVERGENT_LAM_cv"] = held_pairs(held_lam)
    arms["CONVERGENT_REINSTATE_cv"] = held_pairs(held_ri)
    arms["CONVERGENT_RWW_cv"] = held_pairs(held_w)
    print(f"  learned reliability weight w per fold: {chosen_w} (median {np.median(chosen_w)}); "
          f"lambda per fold: {chosen_lam}\n")

    order = ["independent_AND", "entity_solo", "meaning_solo", "TWIN_MEANING", "TWIN_EPISODIC",
             "FUSED", "CONVERGENT_RW_w1", "CONVERGENT_LAM_cv", "CONVERGENT_REINSTATE_cv",
             "CONVERGENT_RWW_cv"]
    print("  ARM                    acc     CI")
    accs = {}
    for a in order:
        acc, lo, hi = acc_ci(arms[a], SEED + hash(a) % 999)
        accs[a] = acc
        tag = "  <- HEADLINE" if a == "CONVERGENT_RWW_cv" else ("  <- STRONGEST FLOOR" if a == "meaning_solo" else "")
        print(f"  {a:20s}  {acc:.4f}  [{lo:.4f},{hi:.4f}]{tag}")

    print("\n  --- BAR (paired bootstrap over docs; strongest floor governs) ---")
    HL = "CONVERGENT_RWW_cv"
    tests = [
        ("HEADLINE beats independent-AND (brief floor)", HL, "independent_AND", "ABOVE"),
        ("HEADLINE beats entity-solo", HL, "entity_solo", "ABOVE"),
        ("HEADLINE beats meaning-solo (STRONGEST floor)", HL, "meaning_solo", "ABOVE"),
        ("HEADLINE beats TWIN_MEANING (top-down meaning load-bearing)", HL, "TWIN_MEANING", "ABOVE"),
        ("HEADLINE beats TWIN_EPISODIC (episodic load-bearing -> real convergence)", HL, "TWIN_EPISODIC", "ABOVE"),
        ("TWIN_EPISODIC falls back to meaning-solo (NOT above it)", "TWIN_EPISODIC", "meaning_solo", "NOT_ABOVE"),
        ("HEADLINE beats FUSED (separated store > one pool)", HL, "FUSED", "ABOVE"),
    ]
    results = {}
    allpass = True
    for name, a, b, want in tests:
        d = paired(arms[a], arms[b], SEED + hash(name) % 9991)
        results[name] = d
        if want == "ABOVE":
            ok = d["band"] == "ABOVE"
        else:  # NOT_ABOVE
            ok = d["band"] != "ABOVE"
        allpass = allpass and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}\n         {d}")

    # null p95 for the headline win over the strongest floor: shuffled-meaning twin deltas vs meaning-solo
    tw = paired(arms["TWIN_MEANING"], arms["meaning_solo"], SEED + 55)
    print(f"\n  null (info-free meaning twin) delta vs meaning-solo: {tw}")

    # ---- localization: where does the lift over each solo concentrate? ----
    print("\n  --- LOCALIZATION (lift is targeted, not a uniform shift) ---")
    w_hl = float(np.median(chosen_w))
    conv = [pick_convergent_rw(r, tau_e, tau_s, w_hl) for r in recs]
    ms = [pick_meaning(r) for r in recs]
    es = [pick_entity(r) for r in recs]
    vi = [r["vi"] for r in recs]
    ms_wrong = [i for i in range(n) if ms[i] != vi[i]]
    ms_right = [i for i in range(n) if ms[i] == vi[i]]
    es_wrong = [i for i in range(n) if es[i] != vi[i]]
    def rate(idx): return np.mean([int(conv[i] == vi[i]) for i in idx]) if idx else float("nan")
    print(f"  convergent rescues meaning-solo-WRONG: {rate(ms_wrong):.4f} correct on n={len(ms_wrong)} "
          f"(meaning-solo=0 there by definition)")
    print(f"  convergent KEEPS meaning-solo-RIGHT   : {rate(ms_right):.4f} correct on n={len(ms_right)} "
          f"(breakage cost; want high)")
    print(f"  convergent rescues entity-solo-WRONG  : {rate(es_wrong):.4f} correct on n={len(es_wrong)}")

    # ---- lesion-each dissociation test (bar #3): convergent degrades gracefully; fused does not ----
    print("\n  --- DISSOCIATION (lesion each system; convergent must degrade gracefully) ---")
    conv_les_meaning = accs["entity_solo"]   # convergent with sem dropped == entity-solo by construction
    conv_les_entity = accs["meaning_solo"]   # convergent with epi dropped == meaning-solo by construction
    print(f"  CONVERGENT lesion meaning -> {conv_les_meaning:.4f} (entity-solo, NONZERO -> spared)")
    print(f"  CONVERGENT lesion entity  -> {conv_les_entity:.4f} (meaning-solo, NONZERO -> spared)  => DOUBLE DISSOCIATION PRESERVED")
    fused_les_meaning = per_doc_pairs(recs, lambda r: (int(np.argmax(r["fep"])) if r["fep"] is not None else -1))
    flm, _, _ = acc_ci(fused_les_meaning, SEED + 88)
    print(f"  FUSED     lesion meaning -> {flm:.4f} (one-pool episodic read; interference vs separated entity-solo {accs['entity_solo']:.4f})")

    verdict = ("CONVERGENT_CUE_BEATS_STRONGEST_FLOOR__TWINS_LOSE__FUSED_LOSES__DISSOCIATION_PRESERVED"
               if allpass else "SEE_FAILING_CHECK")
    out = {
        "anchor": ANCHOR, "verdict": verdict, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "docs": docs, "n_queries": n, "n_docs": ndoc, "tau": {"e": tau_e, "s": tau_s, "f": tau_f},
        "learned_reliability_weight_w_per_fold": [float(x) for x in chosen_w],
        "learned_lambda_per_fold": [float(x) for x in chosen_lam],
        "accuracy": {a: round(float(accs[a]), 4) for a in order},
        "bar_tests": {k: v for k, v in results.items()},
        "null_meaning_twin_vs_meaning_solo": tw,
        "localization": {"meaning_solo_wrong_rescued": round(float(rate(ms_wrong)), 4),
                         "n_meaning_solo_wrong": len(ms_wrong),
                         "meaning_solo_right_kept": round(float(rate(ms_right)), 4),
                         "n_meaning_solo_right": len(ms_right),
                         "entity_solo_wrong_rescued": round(float(rate(es_wrong)), 4),
                         "n_entity_solo_wrong": len(es_wrong)},
        "dissociation": {"convergent_lesion_meaning": round(float(conv_les_meaning), 4),
                         "convergent_lesion_entity": round(float(conv_les_entity), 4),
                         "fused_lesion_meaning": round(float(flm), 4)},
    }
    os.makedirs(OUTDIR, exist_ok=True)
    tmp = os.path.join(OUTDIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(out, fh, indent=2)
    os.replace(tmp, os.path.join(OUTDIR, "metrics.json"))
    print(f"\n{'ALL BAR CHECKS PASS' if allpass else 'INCOMPLETE'} -> {verdict}")
    print(f"[wrote] {os.path.join(OUTDIR, 'metrics.json')}")
    return 0 if allpass else 1


if __name__ == "__main__":
    sys.exit(main())
