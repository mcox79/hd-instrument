"""Scaffold-free witness for the brain-faithful OBSERVATION-CUE registration ledger (perceptual access).

Recomputes the headline LIVE and asserts it; writes to NO landed directory. Run:
    .venv/Scripts/python.exe verification/test_perceptual_access_ledger.py

Asserts, on the substrate's own inputs (spaCy parse + landed hdlab.belief_partition):
  [1] The ledger solves the 4 canonical perceptual-access cases the STATELESS keyword list cannot
      (re-entry, occlusion-despite-co-presence, went-to-a-new-place, testimony).
  [2] On the AUTHORED false-belief gold, the ledger cue accuracy > the landed lexical extractor (0.808).
  [3] On the CORPUS-GROUNDED gold (real LitBank cue-clauses, ground-truth-by-construction labels), the ledger
      cue accuracy is CI-SEPARATED above (a) the lexical extractor, (b) the majority floor (0.5), and
      (c) the info-free TWIN (randomised observation).
  [4] END-TO-END through the LANDED belief_partition, the ledger belief accuracy is CI-separated over the
      lexical extractor AND over the in-situ residual 0.821.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import spacy
from experiments.perceptual_access_ledger import PerceptualAccessLedger, _self_test as ledger_self_test
from experiments.exp_theory_of_mind_realtext_v1 import extract_observed_from_text, load_gold
from experiments import exp_perceptual_access_corpus_v1 as E
from hdlab.belief_partition import BeliefPartition

PHRASINGS = os.path.join(REPO, "data", "mine_presence_phrasings_v1", "phrasings.jsonl")
TITLES = {"mr", "mrs", "ms", "miss", "aunt", "uncle", "dr", "sir", "lady", "lord", "master", "mister", "madam"}


def _boot(vals, seed=0, n=2000):
    a = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n, len(a)))
    m = a[idx].mean(1)
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def _aliases(name):
    toks = [t for t in name.replace(".", " ").split() if t.lower().strip(".") not in TITLES]
    return [name] + toks + ["he", "she", "they", "him", "her", "them", "his"]


def main():
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)

    # [1] canonical cases the stateless keyword list gets wrong
    ledger_self_test()
    print("[1] PASS  ledger solves 4 canonical perceptual-access cases (re-entry, occlusion, new-place, testimony)")

    # [2] authored gold: ledger cue accuracy > landed lexical 0.808
    rows = load_gold()
    lex_a, led_a = [], []
    for r in rows:
        g = bool(r["protagonist_saw_move"]) or r["condition"] == "true_belief_informed"
        lex_a.append(int(extract_observed_from_text(r["text"], r["protagonist"]) == g))
        tr = led.observed(r["text"], _aliases(r["protagonist"]), event_object=r["object"],
                          event_location=r.get("final_location"))
        led_a.append(int(tr.observed == g))
    lex_auth, led_auth = np.mean(lex_a), np.mean(led_a)
    assert abs(lex_auth - 0.808) < 0.02, f"lexical authored acc drifted: {lex_auth:.3f} (expected ~0.808)"
    assert led_auth > lex_auth + 0.10, f"ledger must beat lexical on authored gold: {led_auth:.3f} vs {lex_auth:.3f}"
    print(f"[2] PASS  authored gold: ledger {led_auth:.3f} > lexical {lex_auth:.3f} (landed 0.808)")

    # [3] corpus-grounded gold: CI-separated cue accuracy
    phr = [json.loads(l) for l in open(PHRASINGS, encoding="utf-8")]
    items = E.build_items(E.curate(phr, seed=20260828), seed=20260828)
    assert len(items) >= 120, f"corpus gold too small: {len(items)}"
    lex_c, led_c, twin_c = [], [], []
    rng = np.random.default_rng(11)
    for it in items:
        g = it["observed_gold"]
        lex_c.append(int(extract_observed_from_text(it["text"], it["agent"]) == g))
        tr = led.observed(it["text"], E.aliases_for(it["agent"]), event_object=it["object"], event_location=it["final"])
        led_c.append(int(tr.observed == g))
        twin_c.append(int(bool(rng.integers(0, 2)) == g))
    lm, llo, lhi = _boot(lex_c, seed=1)
    gm, glo, ghi = _boot(led_c, seed=2)
    tm, tlo, thi = _boot(twin_c, seed=3)
    maj = max(np.mean([it["observed_gold"] for it in items]), np.mean([1 - it["observed_gold"] for it in items]))
    assert glo > lhi, f"ledger cue must be CI-sep over lexical: ledger[{glo:.3f},{ghi:.3f}] vs lexical[{llo:.3f},{lhi:.3f}]"
    assert glo > maj, f"ledger cue must beat majority {maj:.3f}: ledger lo {glo:.3f}"
    assert glo > thi, f"ledger cue must be CI-sep over info-free twin: ledger lo {glo:.3f} vs twin hi {thi:.3f}"
    print(f"[3] PASS  corpus gold (n={len(items)}): ledger {gm:.3f}[{glo:.3f},{ghi:.3f}] CI-sep > "
          f"lexical {lm:.3f}[{llo:.3f},{lhi:.3f}], majority {maj:.3f}, twin {tm:.3f}[{tlo:.3f},{thi:.3f}]")

    # [4] end-to-end through the LANDED belief_partition
    def e2e(obs_fn):
        hits = []
        for it in items:
            bp = BeliefPartition(seed=20260828)
            bp.set_reality(it["object"], it["final"])
            bp.form_belief(it["agent"], it["object"], it["initial"], it["final"], obs_fn(it))
            hits.append(int(bp.belief(it["agent"], it["object"], [it["initial"], it["final"]]) == it["belief_gold"]))
        return _boot(hits, seed=4)
    e_lex = e2e(lambda it: extract_observed_from_text(it["text"], it["agent"]))
    e_led = e2e(lambda it: led.observed(it["text"], E.aliases_for(it["agent"]),
                event_object=it["object"], event_location=it["final"]).observed)
    assert e_led[1] > e_lex[2], f"e2e ledger must be CI-sep over lexical: {e_led} vs {e_lex}"
    assert e_led[1] > 0.821, f"e2e ledger must beat in-situ residual 0.821: lo {e_led[1]:.3f}"
    print(f"[4] PASS  end-to-end belief_partition: ledger {e_led[0]:.3f}[{e_led[1]:.3f},{e_led[2]:.3f}] "
          f"CI-sep > lexical {e_lex[0]:.3f}[{e_lex[1]:.3f},{e_lex[2]:.3f}] and > residual 0.821")

    # [5] INTACT natural LitBank passages: full ledger (RULE 0 explicit-marker + RULE 1 spatial + RULE 2
    # testimony) beats the narrow lexical keyword list CI-separated. Honest decomposition: on 3-sentence intact
    # WINDOWS the win is RULE 0 (broad marker coverage); RULE 1 alone is under-powered because the spatial CAUSE
    # is usually out-of-window (the situation model is built incrementally over the WHOLE text -- Zwaan).
    from experiments import exp_perceptual_access_intact_v1 as I
    im = I.run(smoke=False, seed=20260828)
    ic = im["cue_accuracy"]
    assert ic["LEDGER"]["ci"][0] > ic["LEXICAL"]["ci"][1], f"intact: ledger must be CI-sep over lexical: {ic}"
    assert ic["LEDGER"]["ci"][0] > ic["TWIN"]["ci"][1], "intact: ledger must be CI-sep over the info-free twin"
    print(f"[5] PASS  intact LitBank passages (n={im['n_items']}): ledger {ic['LEDGER']['acc']:.3f}"
          f"[{ic['LEDGER']['ci'][0]:.3f},{ic['LEDGER']['ci'][1]:.3f}] CI-sep > lexical {ic['LEXICAL']['acc']:.3f}"
          f" and twin {ic['TWIN']['acc']:.3f}; spatial-only (RULE0 off) {ic['LEDGER_SPATIAL_ONLY']['acc']:.3f} "
          f"(under-powered on windows -- spatial cause is out-of-window)")

    # [6] DISTANCE ROBUSTNESS: the SPATIAL route tracks a departure across arbitrary distance over the FULL text
    # (state persists), while a 3-sentence WINDOW collapses once the departure scrolls out -- proving the intact-
    # window spatial-only chance score is a WINDOWING artifact, not a mechanism failure (Zwaan incremental model).
    from experiments import exp_perceptual_access_distance_v1 as D
    dm = D.run(smoke=False, seed=20260828)
    kmax = D.KS[-1]
    full_far = dm["by_distance"][kmax]["full"]
    win_far = dm["by_distance"][kmax]["windowed"]
    assert full_far >= 0.85, f"spatial route must stay robust at distance {kmax}: got {full_far}"
    assert win_far < full_far - 0.2, f"windowed reader must collapse at distance: full {full_far} vs win {win_far}"
    print(f"[6] PASS  distance robustness (n={dm['n_not_observed_items']}): FULL spatial route "
          f"{dm['by_distance'][0]['full']:.3f}(K=0)->{full_far:.3f}(K={kmax}) stays robust; WINDOWED "
          f"{dm['by_distance'][0]['windowed']:.3f}(K=0)->{win_far:.3f}(K={kmax}) collapses -- windowing artifact, not mechanism")

    print("\nALL 6 WITNESS ASSERTIONS PASSED -- the brain-faithful perceptual-access registration ledger reads "
          "the observation cue from spatial/occlusion/testimony STRUCTURE, generalises to diverse real corpus "
          "phrasings where the fixed keyword list fails, loses under an info-free twin, and lifts the landed "
          "false-belief organ end-to-end past the 0.821 residual.")


if __name__ == "__main__":
    main()
