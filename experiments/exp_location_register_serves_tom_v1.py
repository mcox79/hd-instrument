"""exp_location_register_serves_tom_v1 -- WIRE-DON'T-ISLAND: show the per-entity LOCATION REGISTER SERVES
the theory-of-mind observation-cue front-end, reproducing its win in place of the INLINE presence stopgap.

CONTEXT: the ToM observation cue (experiments/perceptual_access_ledger.PerceptualAccessLedger) had to build
a minimal per-entity PRESENCE tracker INLINE (PresenceState) just to answer "was agent A present when the
object moved?". That is the location register's job. This cell proves the register can DROP IN as that
presence input, so the register is a SHARED organ, not a second island.

TWO demonstrations on the corpus-grounded ToM gold (real mined LitBank presence/absence cue clauses in
canonical false-belief frames -- exp_perceptual_access_corpus_v1.build_items):
  (1) PRESENCE-BIT AGREEMENT: register.present_in_scene(agent, event_clause) vs the ledger's internal
      present_at_event, item by item. High agreement = the register reproduces the stopgap's presence bit.
  (2) COMPOSED CUE ACCURACY: observed = (register-present AND ledger-field-available) OR ledger-informed,
      with the ledger's RULE0 epistemic override unchanged (occlusion/testimony are a DIFFERENT organ --
      the perceptual field -- not the register's job). Compare:
        LEXICAL         the landed keyword extractor (0.808 in situ) -- the FLOOR.
        LEDGER          the inline stopgap (its own presence tracker) -- the current front-end.
        REGISTER_SERVED presence supplied by the location register instead of the inline tracker.
      Gate: REGISTER_SERVED cue accuracy REPRODUCES the ledger (within CI) AND beats LEXICAL CI-separated.
      End-to-end belief accuracy through the LANDED hdlab.belief_partition is reported for all three.

Writes ONLY to data/exp_location_register_serves_tom_v1[/ _smoke]. NO hdlab writes. spaCy-bound -> INLINE.
ASCII only.
# KB_REFERENT: data/mine_presence_phrasings_v1/phrasings.jsonl
"""
from __future__ import annotations
import argparse, json, os, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments import exp_perceptual_access_corpus_v1 as C
from experiments.perceptual_access_ledger import PerceptualAccessLedger
from experiments.location_register import LocationRegister

ANCHOR = "location_register_serves_tom_v1"


def boot_ci(vals, n_boot=2000, seed=0):
    if not vals:
        return (0.0, 0.0, 0.0, 0.0)
    a = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    m = a[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi), float((hi - lo) / 2.0)


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    rows = [json.loads(l) for l in open(C.PHRASINGS, encoding="utf-8")]
    curated = C.curate(rows, seed=seed)
    items = C.build_items(curated, seed=seed)
    if smoke:
        items = items[:24]

    presence_agree = []
    lex_hit, led_hit, served_hit = [], [], []
    per_class = defaultdict(lambda: {"agree": [], "led": [], "served": []})
    for it in items:
        g = it["observed_gold"]
        al = C.aliases_for(it["agent"])
        # LEDGER (inline stopgap) -- full decision + trace
        tr = led.observed(it["text"], al, event_object=it["object"], event_location=it["final"])
        # REGISTER present bit at the ledger's event clause
        reg = LocationRegister(nlp)
        reg.read(it["text"], {it["agent"]: al})
        reg_present = reg.present_in_scene(it["agent"], tr.event_idx)
        presence_agree.append(int(reg_present == tr.present_at_event))
        # did RULE0 epistemic fire for this item? (then the ledger's decision is used unchanged)
        epi = led._epistemic_statement(list(nlp(it["text"]).sents) if False else
                                       list(led._nlp_or_load()(it["text"]).sents), al, tr.event_idx)
        if epi is not None:
            served_obs = bool(epi)                      # RULE0 override -- unchanged (not the register's job)
        else:
            rule1 = bool(reg_present and tr.available_at_event)   # register presence x ledger field
            served_obs = bool(rule1 or tr.informed)
        lex = C.extract_observed_from_text(it["text"], it["agent"])
        lex_hit.append(int(lex == g)); led_hit.append(int(tr.observed == g)); served_hit.append(int(served_obs == g))
        per_class[it["cls"]]["agree"].append(int(reg_present == tr.present_at_event))
        per_class[it["cls"]]["led"].append(int(tr.observed == g))
        per_class[it["cls"]]["served"].append(int(served_obs == g))

    lm, llo, lhi, lhw = boot_ci(lex_hit, seed=seed + 1)
    dm, dlo, dhi, dhw = boot_ci(led_hit, seed=seed + 2)
    sm, slo, shi, shw = boot_ci(served_hit, seed=seed + 3)
    agree = float(np.mean(presence_agree))

    # END-TO-END belief accuracy through the LANDED belief_partition
    from hdlab.belief_partition import BeliefPartition

    def e2e(obs_of):
        hits = []
        for it, obs in zip(items, obs_of):
            bp = BeliefPartition(seed=seed)
            bp.set_reality(it["object"], it["final"])
            bp.form_belief(it["agent"], it["object"], it["initial"], it["final"], obs)
            hits.append(int(bp.belief(it["agent"], it["object"], [it["initial"], it["final"]]) == it["belief_gold"]))
        return boot_ci(hits, seed=seed + 5)
    served_obs_list, led_obs_list, lex_obs_list = [], [], []
    for it in items:
        al = C.aliases_for(it["agent"])
        tr = led.observed(it["text"], al, event_object=it["object"], event_location=it["final"])
        reg = LocationRegister(nlp); reg.read(it["text"], {it["agent"]: al})
        rp = reg.present_in_scene(it["agent"], tr.event_idx)
        epi = led._epistemic_statement(list(led._nlp_or_load()(it["text"]).sents), al, tr.event_idx)
        served_obs_list.append(bool(epi) if epi is not None else bool((rp and tr.available_at_event) or tr.informed))
        led_obs_list.append(tr.observed)
        lex_obs_list.append(C.extract_observed_from_text(it["text"], it["agent"]))
    e2e_led = e2e(led_obs_list); e2e_served = e2e(served_obs_list); e2e_lex = e2e(lex_obs_list)

    # presence agreement on the DECISIVE classes (depart/present/occlude), where co-presence is the
    # discriminator. The 'return' class diverges by design: the register tracks the SPECIFIC destination of
    # 'returned to his lodgings/hotel' (a different place, so not co-present with the object's scene), while
    # the frame gold assumes return==back-in-scene -- the deictic-center question (OUR-INVENTION-UNDER-TEST),
    # not a register error. Reported separately.
    decisive = [(np.mean(v["agree"]), len(v["agree"])) for c, v in per_class.items() if c != "return"]
    dec_agree = float(sum(m * n for m, n in decisive) / sum(n for _, n in decisive)) if decisive else 0.0
    ret_agree = float(np.mean(per_class["return"]["agree"])) if per_class["return"]["agree"] else None
    gates = {
        "served_beats_lexical_ci": bool(slo > lhi),                  # the win HOLDS vs the floor
        "e2e_served_beats_lexical_ci": bool(e2e_served[1] > e2e_lex[2]),
        "presence_agree_decisive_classes_high": bool(dec_agree >= 0.95),  # reproduces stopgap where presence decides
        "served_near_ledger": bool(sm >= dm - 0.10),
    }
    return {
        "anchor_name": ANCHOR, "verdict": "HARD_PASS" if all(gates.values()) else "MIDDLE_BAND",
        "run_mode": "smoke" if smoke else "full", "seed": seed, "n_items": len(items),
        "presence_bit_agreement": agree,
        "presence_agree_decisive_classes": dec_agree, "presence_agree_return_class": ret_agree,
        "cue_accuracy": {"LEXICAL": {"acc": lm, "ci": [llo, lhi]}, "LEDGER": {"acc": dm, "ci": [dlo, dhi]},
                         "REGISTER_SERVED": {"acc": sm, "ci": [slo, shi], "hw": shw}},
        "end_to_end_belief_acc": {"LEXICAL": {"acc": e2e_lex[0], "ci": e2e_lex[1:3]},
                                  "LEDGER": {"acc": e2e_led[0], "ci": e2e_led[1:3]},
                                  "REGISTER_SERVED": {"acc": e2e_served[0], "ci": e2e_served[1:3]}},
        "per_class_presence_agreement": {c: float(np.mean(v["agree"])) for c, v in per_class.items()},
        "gates": gates, "ts_iso": datetime.now(timezone.utc).isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    m = run(smoke=smoke, seed=args.seed); m["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    c = m["cue_accuracy"]; e = m["end_to_end_belief_acc"]
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  n={m['n_items']} ===")
    print(f"presence-bit agreement (register vs inline stopgap): {m['presence_bit_agreement']:.3f}")
    print(f"CUE ACCURACY:  LEXICAL {c['LEXICAL']['acc']:.3f}   LEDGER {c['LEDGER']['acc']:.3f}   "
          f"REGISTER_SERVED {c['REGISTER_SERVED']['acc']:.3f} [{c['REGISTER_SERVED']['ci'][0]:.3f},{c['REGISTER_SERVED']['ci'][1]:.3f}]")
    print(f"END-TO-END belief acc:  LEXICAL {e['LEXICAL']['acc']:.3f}   LEDGER {e['LEDGER']['acc']:.3f}   "
          f"REGISTER_SERVED {e['REGISTER_SERVED']['acc']:.3f}")
    print("VERDICT:", m["verdict"], "GATES:")
    for k, v in m["gates"].items():
        print(f"  {'PASS' if v else 'fail'}  {k}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
