"""exp_perceptual_access_intact_v1 -- test the perceptual-access ledger on INTACT, naturally-occurring LitBank
passages (not composed frames), to close bar #4's honest corpus-generality gap.

Each item is a REAL 3-sentence window from a LitBank novel containing a dramatic-irony / perceptual-access
marker about a NAMED character (mine_false_belief_corpus_v1). The narrator's marker is the LABEL (observed vs
not-observed) -- the most direct evidence, verified by reading. The extractors read the intact passage; the
agent is resolved by name + pronouns (LitBank GOLD coref is available on disk as the deployment-hardening path;
for single-salient-protagonist windows the alias proxy suffices).

HONEST: intact false-belief-about-an-object scenes are SPARSE (this is the finding). This measures whether the
ledger -- with RULE 0 (explicit epistemic statement) + RULE 1 (spatial perceptual access) + RULE 2 (testimony) --
recovers the narrator's epistemic label on real intact prose across DIVERSE phrasings, vs the narrow landed
lexical keyword list. Writes ONLY to data/exp_perceptual_access_intact_v1[/ _smoke]. NO hdlab writes. ASCII only.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.exp_theory_of_mind_realtext_v1 import extract_observed_from_text
from experiments.perceptual_access_ledger import PerceptualAccessLedger

ANCHOR = "perceptual_access_intact_v1"
CAND = os.path.join(REPO, "data", "mine_false_belief_corpus_v1", "candidates.jsonl")

# exclude the "unfamiliar PERSON" reading of unknown/unbeknownst ("a man quite unknown to Tommy") -- not an
# unwitnessed EVENT. Require, for the not-observed irony class, an action the agent misses (a verb of doing).
_UNFAMILIAR = re.compile(r"\b(quite |perfectly |wholly |a stranger|a man|a woman|a person|the man|the woman|"
                         r"the stranger|a figure) .{0,20}(unknown|unbeknown)", re.I)
_EVENT_ACTION = re.compile(r"\b(moved|went|came|took|put|placed|hid|carried|left|entered|slipped|crept|sent|"
                           r"wrote|opened|shut|brought|gave|stole|removed|arrived|departed|met|visited|"
                           r"distributed|had had|had gone|had come|had been|struck|seized|turned)\b", re.I)

TITLES = {"mr", "mrs", "ms", "miss", "aunt", "uncle", "dr", "sir", "lady", "lord", "master", "mister", "madam"}
PRON = ["he", "she", "they", "him", "her", "them", "his", "hers", "their"]
# sentence-initial words that the [A-Z][a-z]+ miner mistook for a character name (pronouns / function words) --
# these are dialogue / non-character agents, excluded so the gold is genuine perceptual access about a CHARACTER.
STOP_NAMES = {"you", "they", "she", "he", "we", "it", "i", "that", "this", "there", "but", "and", "then", "when",
              "while", "thus", "yet", "for", "nor", "so", "her", "his", "him", "them", "one", "who", "what",
              "if", "as", "now", "here", "why", "how", "no", "yes", "oh", "well", "the", "a", "an", "some"}


def aliases_for(name):
    toks = [t for t in name.replace(".", " ").split() if t.lower().strip(".") not in TITLES]
    return [name] + toks + PRON


def split_sents(text):
    return re.split(r"(?<=[.!?\"])\s+(?=[A-Z\"'])", text.strip())


def curate(seed=20260828):
    rows = [json.loads(l) for l in open(CAND, encoding="utf-8")]
    items = []
    for r in rows:
        win = r["window"]
        if r["name"].lower() in STOP_NAMES:                 # pronoun / function-word "name" = dialogue, not a character
            continue
        # skip unfamiliar-person readings + require a concrete action the agent could (fail to) witness
        if r["tier"] in ("irony",) and (_UNFAMILIAR.search(win) or not _EVENT_ACTION.search(win)):
            continue
        if not _EVENT_ACTION.search(win):
            continue
        sents = split_sents(win)
        if len(sents) < 2:
            continue
        # locate the marker sentence within the window (the event anchor)
        ev_idx = 0
        for j, s in enumerate(sents):
            if r["marker"].split()[0].lower() in s.lower() and re.search(re.escape(r["marker"].split()[-1]), s, re.I):
                ev_idx = j
                break
        items.append({"book": r["book"], "agent": r["name"], "tier": r["tier"],
                      "observed_gold": bool(r["label_observed"]), "marker": r["marker"],
                      "text": win, "event_index": ev_idx})
    # balance observed / not-observed; cap per book for diversity
    rng = np.random.default_rng(seed)
    rng.shuffle(items)
    per_book = Counter()
    kept = []
    for it in items:
        if per_book[it["book"]] >= 6:
            continue
        per_book[it["book"]] += 1
        kept.append(it)
    no = [it for it in kept if not it["observed_gold"]]
    ob = [it for it in kept if it["observed_gold"]]
    n = min(len(no), len(ob))
    return no[:n] + ob[:n], len(no), len(ob)


def boot(vals, seed=0, nb=2000):
    a = np.asarray(vals, float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(nb, len(a)))
    m = a[idx].mean(1)
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    items, n_no, n_ob = curate(seed)
    if smoke:
        items = items[:20]
    lex, lg, lg_sp, twin = [], [], [], []
    per_tier = defaultdict(lambda: {"lex": [], "led": []})
    rng = np.random.default_rng(seed + 3)
    dump = []
    for it in items:
        g = it["observed_gold"]
        lx = extract_observed_from_text(it["text"], it["agent"])
        tr = led.observed(it["text"], aliases_for(it["agent"]), event_index=it["event_index"])
        # RULE-0-OFF: spatial (RULE 1) + testimony (RULE 2) only -- isolates the MECHANISM's contribution on
        # intact prose from the explicit-marker (RULE 0) coverage.
        tr_sp = led.observed(it["text"], aliases_for(it["agent"]), event_index=it["event_index"], use_epistemic=False)
        lex.append(int(lx == g)); lg.append(int(tr.observed == g)); lg_sp.append(int(tr_sp.observed == g))
        twin.append(int(bool(rng.integers(0, 2)) == g))
        per_tier[it["tier"]]["lex"].append(int(lx == g)); per_tier[it["tier"]]["led"].append(int(tr.observed == g))
        dump.append({"agent": it["agent"], "tier": it["tier"], "marker": it["marker"], "gold": g,
                     "lexical": bool(lx), "ledger": bool(tr.observed), "book": it["book"],
                     "text": it["text"][:200]})
    lm, llo, lhi = boot(lex, 1); gm, glo, ghi = boot(lg, 2); tm, tlo, thi = boot(twin, 3)
    sm, slo, shi = boot(lg_sp, 4)
    maj = max(np.mean([it["observed_gold"] for it in items]), np.mean([1 - it["observed_gold"] for it in items]))
    metrics = {
        "anchor_name": ANCHOR, "verdict": "MEASURED", "run_mode": "smoke" if smoke else "full", "seed": seed,
        "n_items": len(items), "n_candidates_not_obs": n_no, "n_candidates_obs": n_ob,
        "cue_accuracy": {"LEXICAL": {"acc": lm, "ci": [llo, lhi]}, "LEDGER": {"acc": gm, "ci": [glo, ghi]},
                         "LEDGER_SPATIAL_ONLY": {"acc": sm, "ci": [slo, shi]},
                         "TWIN": {"acc": tm, "ci": [tlo, thi]}, "MAJORITY": float(maj)},
        "per_tier": {t: {"lex": float(np.mean(v["lex"])), "led": float(np.mean(v["led"])), "n": len(v["lex"])}
                     for t, v in per_tier.items()},
        "gates": {"ledger_beats_lexical_ci": bool(glo > lhi), "ledger_beats_majority": bool(glo > maj),
                  "ledger_beats_twin_ci": bool(glo > thi), "ledger_ge_lexical": bool(gm >= lm)},
        "dump": dump, "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = args.smoke or args.self_test
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    m = run(smoke=smoke, seed=args.seed); m["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    c = m["cue_accuracy"]
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s n={m['n_items']} (cand not_obs={m['n_candidates_not_obs']} obs={m['n_candidates_obs']}) ===")
    print(f"  LEXICAL              {c['LEXICAL']['acc']:.3f} {c['LEXICAL']['ci']}")
    print(f"  LEDGER (all rules)   {c['LEDGER']['acc']:.3f} {c['LEDGER']['ci']}")
    print(f"  LEDGER spatial-only  {c['LEDGER_SPATIAL_ONLY']['acc']:.3f} {c['LEDGER_SPATIAL_ONLY']['ci']}  (RULE 0 off)")
    print(f"  TWIN    {c['TWIN']['acc']:.3f}   MAJORITY {c['MAJORITY']:.3f}")
    print("PER-TIER (lex/led):")
    for t, v in m["per_tier"].items():
        print(f"  {t:9s} n={v['n']:3d}  lex={v['lex']:.3f}  led={v['led']:.3f}")
    print("GATES:", {k: v for k, v in m["gates"].items()})
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
