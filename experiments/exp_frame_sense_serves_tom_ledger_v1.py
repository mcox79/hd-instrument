"""exp_frame_sense_serves_tom_ledger_v1 -- the REAL downstream-lift test (route a of a 3-way bakeoff):
does GATING the perceptual-access ledger's MOTION decision with the frame_sense_disambiguator improve the
observation-cue accuracy on a REAL ToM gold, CI-separated vs the un-gated ledger?

THE BUG BEING GATED (measured, on disk):
  PerceptualAccessLedger._motion_signal fires a DEPARTURE on a deixis verb STRING (leave/left/go/went/return...)
  REGARDLESS OF SENSE. So "she left a note" / "he returned a sharp reply" (possession / communication senses)
  spuriously mark the agent as having DEPARTED the scene -> agent read as ABSENT -> observed=False. On a
  false-belief item where the agent actually stayed and WITNESSED the move, that is a FALSE DEPARTURE that costs
  a cue error. Polysemy is the named residual on the intact gold (ledger 0.930; spatial-only 0.535).

THE GATE (ARM GATED): monkeypatch the ledger instance's `_motion_signal`. When the un-gated call would return a
  ('depart', ground) result, re-check the departure-triggering deixis verb(s) with the disambiguator
  (FrameSenseDisambiguator(nlp, use_idioms=False, use_indep_fit=False) -- baseline construction cue ONLY). If NO
  triggering verb has frame=='motion' (i.e. the departure is a possession/communication/etc. false positive),
  SUPPRESS the departure (return None). Everything else in the ledger is IDENTICAL. Returns are NOT gated (per
  spec -- only false departures). This isolates the disambiguator's DOWNSTREAM contribution.

ARMS (cue accuracy = does trace.observed match the by-construction / narrator-marker observed_gold?):
  BASELINE  led.observed(...) as-is (the un-gated ledger).
  GATED     the same ledger with the motion-decision gate installed.

GOLDS (reuse the existing ToM eval cells' gold-building verbatim -- imported, not re-derived):
  intact    exp_perceptual_access_intact_v1.curate  -- REAL intact LitBank passages (PRIMARY; polysemy = the
            named residual here).
  corpus    exp_perceptual_access_corpus_v1.build_items -- composed frames w/ REAL mined cue clauses (SECONDARY;
            departures are pre-filtered against polysemy, so little room -- reported for completeness).

REGIMES (per gold): the ledger's default consults RULE 0 (explicit narrator epistemic marker) which can OVERRIDE
  the RULE-1 spatial/motion decision, MASKING the gate. So we report TWO regimes:
    as_is         use_epistemic=True  -- the ledger exactly as it ships (the spec's "as-is" baseline).
    spatial_only  use_epistemic=False -- RULE 0 off, so the MOTION decision actually drives observed(); this is
                  where a motion-gate can be seen. Diagnostic, not a different product.

VERDICT (per regime): HARD_PASS iff GATED beats BASELINE CI-separated (gated_lo > baseline_hi) OR McNemar p<0.05
  with c>b (c = items gating flipped wrong->right, b = right->wrong). Top-level verdict = the PRIMARY gold's
  as_is regime; the spatial_only diagnostic is reported alongside.

Writes ONLY to data/exp_frame_sense_serves_tom_ledger_v1[/ _smoke]. Does NOT modify hdlab/. spaCy runs INLINE.
ASCII only.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.frame_sense_disambiguator import FrameSenseDisambiguator
from experiments.perceptual_access_ledger import PerceptualAccessLedger, DEIXIS_AWAY

ANCHOR = "frame_sense_serves_tom_ledger_v1"
# deixis verbs whose STRING fires a departure in _motion_signal regardless of sense (the polysemy surface).
# leave/quit/exit take a Source dobj; the rest are the DEIXIS_AWAY set. These are the verbs the gate re-checks.
_LEAVE_SOURCE = {"leave", "quit", "exit"}


# ---------------------------------------------------------------------------
# The MOTION-decision gate (installed on a ledger instance via _motion_signal monkeypatch).
# ---------------------------------------------------------------------------
def install_gate(led: PerceptualAccessLedger, dis: FrameSenseDisambiguator):
    """Wrap led._motion_signal so a ('depart', ground) result is SUPPRESSED (->None) when the departure-
    triggering deixis verb(s) do NOT have frame=='motion' per the disambiguator. Returns (restore_fn, stats).
    stats['suppressed_calls'] counts suppressions since the caller last reset it; stats['detail'] logs them."""
    orig = led._motion_signal            # bound method of the instance
    stats = {"suppressed_calls": 0, "detail": []}

    def gated(sent):
        res = orig(sent)
        if res is None or res[0] != "depart":
            return res                    # only DEPARTURES are gated (returns untouched, per spec)
        # departure-triggering deixis verbs in this clause (the string-matched ones _motion_signal keys on)
        trigs = [v for v in sent if v.pos_ == "VERB" and
                 (v.lemma_.lower() in DEIXIS_AWAY or v.text.lower() in DEIXIS_AWAY
                  or v.lemma_.lower() in _LEAVE_SOURCE)]
        if not trigs:
            return res                    # departure came from a manner-verb+satellite, not a deixis string -> keep
        frames = []
        any_motion = False
        for v in trigs:
            try:
                fr = dis.disambiguate_token(sent, v).frame
            except Exception:
                fr = "motion"             # fail SAFE: on a disambiguator error, do not suppress
            frames.append((v.text.lower(), fr))
            if fr == "motion":
                any_motion = True
        if any_motion:
            return res                    # at least one genuine motion sense -> a real departure, keep it
        stats["suppressed_calls"] += 1    # ALL triggering verbs are non-motion -> false departure -> SUPPRESS
        stats["detail"].append({"sent": sent.text[:90], "verbs": frames, "ground": res[1]})
        return None

    led._motion_signal = gated            # instance attribute: called as self._motion_signal(sent) (unbound fn)

    def restore():
        led._motion_signal = orig
    return restore, stats


# ---------------------------------------------------------------------------
# Gold loaders -- reuse the existing ToM eval cells' gold-building VERBATIM (imported).
# Each returns (items, call_fn, meta). call_fn(led, item, use_epistemic) -> bool observed.
# ---------------------------------------------------------------------------
def load_intact_gold(seed, smoke):
    from experiments.exp_perceptual_access_intact_v1 import curate, aliases_for
    items, n_no, n_ob = curate(seed)
    if smoke:
        items = items[:20]

    def call(led, it, use_epistemic):
        return bool(led.observed(it["text"], aliases_for(it["agent"]),
                                 event_index=it["event_index"], use_epistemic=use_epistemic).observed)
    return items, call, {"n_candidates_not_obs": n_no, "n_candidates_obs": n_ob}


def load_corpus_gold(seed, smoke):
    from experiments.exp_perceptual_access_corpus_v1 import curate, build_items, aliases_for, PHRASINGS
    rows = [json.loads(l) for l in open(PHRASINGS, encoding="utf-8")]
    items = build_items(curate(rows, seed=seed), seed=seed)
    if smoke:
        items = items[:24]

    def call(led, it, use_epistemic):
        return bool(led.observed(it["text"], aliases_for(it["agent"]), event_object=it["object"],
                                 event_location=it["final"], use_epistemic=use_epistemic).observed)
    return items, call, {}


def load_polysemy_control_gold(seed, smoke):
    """SYNTHETIC POSITIVE CONTROL (NOT a real gold -- excluded from the top-level verdict). False-belief frames
    whose agent cue-clause uses a DEPARTURE verb in a NON-MOTION sense (possession/communication: 'left a note',
    'left word') so the un-gated ledger MISREADS a departure and marks the present, witnessing agent as absent
    (observed=False, WRONG). The gate should suppress it -> present -> observed=True (RIGHT). Balanced against
    genuine-motion departures ('left the room', gold=not-observed) the gate MUST KEEP. Demonstrates the downstream
    lift EXISTS when the population actually contains the verb-sense polysemy the gate targets -- so a null on the
    real golds is a POPULATION property (they lack the polysemy), not a broken gate."""
    from experiments.exp_perceptual_access_corpus_v1 import aliases_for, OBJECTS, MOVERS, AGENTS
    TRAP = ["left a note on the {l0}", "left a letter for {mover}", "left a message with {mover}",
            "left the money on the {l0}", "left word for {mover}", "left a mark on the paper"]  # non-motion -> stays
    REAL = ["left the room quietly", "went outside to play", "went upstairs to bed", "left the house",
            "went out into the garden", "departed for the village"]                              # motion -> leaves
    items, idx = [], 0
    for k in range(12):
        agent = AGENTS[k % len(AGENTS)]
        obj, l0, l1 = OBJECTS[k % len(OBJECTS)]
        mover = MOVERS[k % len(MOVERS)]
        for cls, tmpl, gold in [("trap", TRAP[k % len(TRAP)], True), ("real", REAL[k % len(REAL)], False)]:
            vp = tmpl.format(l0=l0, mover=mover)
            text = (f"{agent} put the {obj} on the {l0}. {agent} {vp}. "
                    f"Then {mover} moved the {obj} from the {l0} to the {l1}.")
            items.append({"id": f"pc_{idx:03d}", "agent": agent, "object": obj, "final": l1,
                          "cls": cls, "observed_gold": gold, "text": text})
            idx += 1
    if smoke:
        items = items[:8]

    def call(led, it, use_epistemic):
        return bool(led.observed(it["text"], aliases_for(it["agent"]), event_object=it["object"],
                                 event_location=it["final"], use_epistemic=use_epistemic).observed)
    return items, call, {"synthetic_positive_control": True}


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------
def boot_ci(vals, n_boot=2000, seed=0):
    if not vals:
        return {"acc": 0.0, "ci": [0.0, 0.0], "hw": 0.0}
    a = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    m = a[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return {"acc": float(a.mean()), "ci": [float(lo), float(hi)], "hw": float((hi - lo) / 2.0)}


def mcnemar_exact(b, c):
    """Two-sided exact-binomial McNemar over the b+c discordant pairs (p = P(|k-n/2| >= observed) under p=.5)."""
    n = b + c
    if n == 0:
        return {"b": int(b), "c": int(c), "n_discordant": 0, "p": 1.0}
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) * (0.5 ** n)
    p = min(1.0, 2.0 * tail)
    return {"b": int(b), "c": int(c), "n_discordant": int(n), "p": float(p)}


# ---------------------------------------------------------------------------
# One (gold, regime) comparison: BASELINE vs GATED.
# ---------------------------------------------------------------------------
def score_regime(led, dis, items, call, use_epistemic, seed):
    gold = [bool(it["observed_gold"]) for it in items]

    # BASELINE pass -- ensure no gate is installed
    base_pred = [call(led, it, use_epistemic) for it in items]
    base_ok = [int(p == g) for p, g in zip(base_pred, gold)]

    # GATED pass -- install the motion gate; reset the per-item suppression counter before each item
    restore, stats = install_gate(led, dis)
    gate_pred, item_suppressed, supp_examples = [], [], []
    try:
        for it in items:
            stats["suppressed_calls"] = 0
            stats["detail"] = []
            p = call(led, it, use_epistemic)
            gate_pred.append(p)
            item_suppressed.append(stats["suppressed_calls"] > 0)
            if stats["suppressed_calls"] > 0 and len(supp_examples) < 12:
                supp_examples.append({"id": it.get("id", it.get("agent")), "gold": bool(it["observed_gold"]),
                                      "detail": stats["detail"][:2]})
    finally:
        restore()
    gate_ok = [int(p == g) for p, g in zip(gate_pred, gold)]

    # McNemar on paired item correctness: b = base right & gated wrong; c = base wrong & gated right
    b = sum(1 for bo, go in zip(base_ok, gate_ok) if bo == 1 and go == 0)
    c = sum(1 for bo, go in zip(base_ok, gate_ok) if bo == 0 and go == 1)
    mcn = mcnemar_exact(b, c)

    # attribution of the suppressions
    n_supp_items = sum(item_suppressed)
    n_supp_correct = sum(1 for s, bo, go in zip(item_suppressed, base_ok, gate_ok) if s and bo == 0 and go == 1)
    n_supp_harmful = sum(1 for s, bo, go in zip(item_suppressed, base_ok, gate_ok) if s and bo == 1 and go == 0)
    n_supp_neutral = n_supp_items - n_supp_correct - n_supp_harmful
    n_flip_total = sum(1 for bp, gp in zip(base_pred, gate_pred) if bp != gp)

    base_ci = boot_ci(base_ok, seed=seed + 11)
    gate_ci = boot_ci(gate_ok, seed=seed + 12)
    ci_sep = bool(gate_ci["ci"][0] > base_ci["ci"][1])
    mcnemar_pass = bool(mcn["p"] < 0.05 and c > b)
    return {
        "use_epistemic": bool(use_epistemic),
        "n": len(items),
        "n_observed_gold": int(sum(gold)),
        "n_not_observed_gold": int(len(gold) - sum(gold)),
        "baseline_acc": base_ci,
        "gated_acc": gate_ci,
        "mcnemar": mcn,
        "ci_separated": ci_sep,
        "n_suppressed_items": int(n_supp_items),
        "n_suppressions_correct": int(n_supp_correct),   # false departure removed -> flipped wrong->right
        "n_suppressions_harmful": int(n_supp_harmful),   # real departure removed -> flipped right->wrong
        "n_suppressions_neutral": int(n_supp_neutral),   # suppressed but item was/stayed the same correctness
        "n_flip_total": int(n_flip_total),
        "verdict_pass": bool(ci_sep or mcnemar_pass),
        "suppressed_examples": supp_examples,
    }


def run_gold(led, dis, items, call, meta, seed):
    return {
        "n_items": len(items),
        "meta": meta,
        "as_is": score_regime(led, dis, items, call, use_epistemic=True, seed=seed),
        "spatial_only": score_regime(led, dis, items, call, use_epistemic=False, seed=seed + 100),
    }


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    dis = FrameSenseDisambiguator(nlp, use_idioms=False, use_indep_fit=False)  # baseline construction cue ONLY

    results = {}
    primary = None
    # PRIMARY: intact (polysemy = the named residual). Fall back to corpus if unreachable.
    try:
        items, call, meta = load_intact_gold(seed, smoke)
        if items:
            results["intact"] = run_gold(led, dis, items, call, meta, seed)
            primary = "intact"
    except Exception as e:
        results["intact_error"] = repr(e)
    # SECONDARY: corpus (departures pre-filtered against polysemy -> little room; completeness).
    try:
        items, call, meta = load_corpus_gold(seed, smoke)
        if items:
            results["corpus"] = run_gold(led, dis, items, call, meta, seed)
            if primary is None:
                primary = "corpus"
    except Exception as e:
        results["corpus_error"] = repr(e)
    # POSITIVE CONTROL: a polysemy-stressed synthetic gold (excluded from the verdict; proves the lift is real).
    try:
        items, call, meta = load_polysemy_control_gold(seed, smoke)
        if items:
            results["polysemy_control"] = run_gold(led, dis, items, call, meta, seed)
    except Exception as e:
        results["polysemy_control_error"] = repr(e)

    head = results.get(primary, {}).get("as_is", {}) if primary else {}
    gates = {}
    for gold in ("intact", "corpus", "polysemy_control"):
        if gold in results:
            for reg in ("as_is", "spatial_only"):
                r = results[gold][reg]
                gates[f"{gold}_{reg}_ci_separated"] = r["ci_separated"]
                gates[f"{gold}_{reg}_mcnemar_helps"] = bool(r["mcnemar"]["p"] < 0.05 and r["mcnemar"]["c"] > r["mcnemar"]["b"])
    verdict = "HARD_PASS" if head.get("verdict_pass") else "MEASURED"
    metrics = {
        "anchor_name": ANCHOR,
        "verdict": verdict,
        "run_mode": "smoke" if smoke else "full",
        "seed": seed,
        "primary_gold": primary,
        "headline": {"gold": primary, "regime": "as_is",
                     "baseline_acc": head.get("baseline_acc"), "gated_acc": head.get("gated_acc"),
                     "mcnemar": head.get("mcnemar"), "verdict_pass": head.get("verdict_pass")},
        "results": results,
        "gates": gates,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return metrics


# ---------------------------------------------------------------------------
def _self_test():
    """Positive control on the GATE: a motion 'left' keeps its departure; a possession 'left' is suppressed."""
    import spacy
    nlp = spacy.load("en_core_web_sm")
    dis = FrameSenseDisambiguator(nlp, use_idioms=False, use_indep_fit=False)
    led = PerceptualAccessLedger(nlp)

    def signal(text):
        return led._motion_signal(list(nlp(text).sents)[0])

    # baseline (un-gated): BOTH fire a departure (the polysemy bug)
    base_motion = signal("Anna left the room.")
    base_poss = signal("Anna left a note on the desk.")
    # gated
    restore, _ = install_gate(led, dis)
    gate_motion = signal("Anna left the room.")
    gate_poss = signal("Anna left a note on the desk.")
    restore()

    ok_base = (base_motion is not None and base_motion[0] == "depart"
               and base_poss is not None and base_poss[0] == "depart")
    ok_keep = (gate_motion is not None and gate_motion[0] == "depart")   # motion sense kept
    ok_supp = (gate_poss is None)                                        # possession sense suppressed
    print(f"  baseline: 'left the room'={base_motion}  'left a note...'={base_poss}")
    print(f"  gated:    'left the room'={gate_motion}  'left a note...'={gate_poss}")
    print(f"  [{'PASS' if ok_base else 'FAIL'}] baseline fires BOTH departures (the polysemy bug)")
    print(f"  [{'PASS' if ok_keep else 'FAIL'}] gate KEEPS the motion-sense departure")
    print(f"  [{'PASS' if ok_supp else 'FAIL'}] gate SUPPRESSES the possession-sense false departure")
    ok = ok_base and ok_keep and ok_supp
    print(f"SELF-TEST {ANCHOR}: {'PASS' if ok else 'FAIL'}")
    assert ok, "gate self-test failed"
    return ok


def _fmt_regime(name, r):
    b, g = r["baseline_acc"], r["gated_acc"]
    print(f"  [{name}] n={r['n']} (obs={r['n_observed_gold']} not_obs={r['n_not_observed_gold']})")
    print(f"    BASELINE {b['acc']:.3f} [{b['ci'][0]:.3f},{b['ci'][1]:.3f}] (hw {b['hw']:.3f})")
    print(f"    GATED    {g['acc']:.3f} [{g['ci'][0]:.3f},{g['ci'][1]:.3f}] (hw {g['hw']:.3f})  CI-sep={r['ci_separated']}")
    m = r["mcnemar"]
    print(f"    McNemar b={m['b']} c={m['c']} n_disc={m['n_discordant']} p={m['p']:.4f}")
    print(f"    suppressed_items={r['n_suppressed_items']} (correct={r['n_suppressions_correct']} "
          f"harmful={r['n_suppressions_harmful']} neutral={r['n_suppressions_neutral']}) flips={r['n_flip_total']}")
    print(f"    -> regime verdict_pass={r['verdict_pass']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    smoke = args.smoke or args.mode == "smoke"
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    metrics = run(smoke=smoke, seed=args.seed)
    metrics["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))

    print(f"=== {ANCHOR} ({metrics['run_mode']}) {metrics['elapsed_s']}s  verdict={metrics['verdict']} "
          f"primary={metrics['primary_gold']} ===")
    for gold in ("intact", "corpus", "polysemy_control"):
        if gold in metrics["results"]:
            tag = " (SYNTHETIC POSITIVE CONTROL, not in verdict)" if gold == "polysemy_control" else ""
            print(f"[GOLD={gold}]{tag}  n_items={metrics['results'][gold]['n_items']}")
            _fmt_regime("as_is (use_epistemic=True, ships this way)", metrics["results"][gold]["as_is"])
            _fmt_regime("spatial_only (RULE 0 off -> motion decision drives)", metrics["results"][gold]["spatial_only"])
    print("GATES:")
    for k, v in metrics["gates"].items():
        print(f"  {'PASS' if v else 'fail'}  {k}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
