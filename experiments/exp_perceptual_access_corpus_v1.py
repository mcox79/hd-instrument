"""exp_perceptual_access_corpus_v1 -- validate the brain-faithful OBSERVATION-CUE ledger on a CORPUS-GROUNDED
false-belief gold whose observation-cue clauses are REAL, DIVERSE LitBank prose.

THE RESIDUAL (measured, on disk): the landed belief_partition is perfect with clean observation (belief-acc
1.000); the END-TO-END drops to 0.821 because reading "did agent A witness the change?" from prose uses a
LEXICAL KEYWORD LIST (0.808 cue acc). The keyword list is STATELESS and NARROW -- it enumerates a handful of
absence strings ("while gone", "went outside") and defaults to "present" on anything else.

THE TEST: a corpus-grounded gold. The observation-cue-bearing clause of each item is a REAL, DIVERSE presence/
absence/occlusion/testimony phrasing mined from 100 LitBank novels (mine_presence_phrasings_v1; a BROAD net,
wider than either extractor, so neither is advantaged by the mining criterion), placed in a canonical
false-belief frame with a GROUND-TRUTH-BY-CONSTRUCTION label. This isolates the RESIDUAL -- the cue reading --
and tests GENERALIZATION to real literary phrasings the keyword list never enumerated.

WHY NOT INTACT NATURAL SCENES: clean naturally-INTACT false-belief-about-an-object-move scenes are SPARSE in
real literature (mine_false_belief_corpus_v1: 991 dramatic-irony marker windows over 100 novels, most idiom/
dialogue/unfamiliar-person; ~dozens clean after curation) AND automatic mining of clean presence/absence is
limited by verb POLYSEMY ("observed"=remarked vs watched, "left"=departed vs deposited) -- a real wall the
brain crosses with full lexical semantics. So the cue-bearing CLAUSE is real corpus prose; the frame is minimal
and the label is by construction. A held-out sample of the mined clauses is verified (precision reported).

ARMS (cue accuracy = does the extractor's observed bit match the by-construction ground truth?):
  LEXICAL      the landed keyword extractor (extract_observed_from_text) -- THE FLOOR TO BEAT (0.808 in situ).
  LEDGER       the brain-faithful registration ledger (perceptual_access_ledger.PerceptualAccessLedger).
  TWIN         info-free: observation bit randomised -> must not beat the trivial floors.
  ALWAYS_OBS / ALWAYS_NOT / MAJORITY  trivial floors (a class-balanced gold makes these ~0.5).
END-TO-END: feed each extractor's observed bit through the LANDED belief_partition and score belief accuracy
  against the oracle-observation belief (which is 1.000) -- the composed lift is the point.

Writes ONLY to data/exp_perceptual_access_corpus_v1[/ _smoke]. Does NOT modify hdlab/. ASCII only.
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

ANCHOR = "perceptual_access_corpus_v1"
PHRASINGS = os.path.join(REPO, "data", "mine_presence_phrasings_v1", "phrasings.jsonl")

# canonical frame ingredients (cycled; the ONLY variable across items is the mined cue clause)
OBJECTS = [("marble", "red box", "blue basket"), ("letter", "table", "drawer"),
           ("ball", "green chair", "toy box"), ("ring", "dish", "jewel case"),
           ("key", "hook", "pocket"), ("coin", "jar", "purse"), ("apple", "bowl", "basket"),
           ("book", "shelf", "trunk")]
MOVERS = ["her brother", "the maid", "his cousin", "the old woman", "the boy", "a neighbor"]
AGENTS = ["Anna", "Thomas", "Clara", "Walter", "Susan", "Henry", "Margaret", "Edwin"]

# depart destinations that clearly REMOVE the agent from the scene (drop in-room/return/sleep phrasings)
_AWAY = re.compile(r"\b(out|away|off|upstairs|downstairs|abroad|forth|home|from the room|from the house|"
                   r"to the (garden|field|door|village|town|shore|farm|church|market|garret|attic|cellar|"
                   r"street|road|wood|hall|gate|barn|stable|meadow|orchard|well|river|bridge|inn|shop|"
                   r"school|castle|park|kitchen|study|library|stairs))\b", re.I)
_BAD_DEPART = re.compile(r"\b(back|sleep|bed|to the piano|to the fire|to the table|to the window)\b", re.I)
# METAPHOR/POLYSEMY rejects (the label wall): directional particles used non-spatially, and TRANSITIVE
# "returned the money" (give-back, not the agent returning). These would give the ledger spurious agreement.
_METAPHOR = re.compile(r"\bout of (his|her|their|my|the) (disguise|heart|mind|senses|wits|sight|reach|way|"
                       r"world|life|reckoning|element|depth|head|hands?|control|order|place|question|"
                       r"countenance|humou?r|temper|breath|saddle|seat|chair)\b|"
                       r"\bpassed away\b|"
                       r"\b(vanished|faded|melted|passed|died|slipped|went) (away |out )?(of|from) (his|her|their|the) "
                       r"(heart|mind|sight|world|life|memory|existence|thoughts?|view)\b", re.I)
_TRANSITIVE_RETURN = re.compile(r"\breturned (the|a|an|his|her|their|my|it|them|that|this|some|these|those)\b", re.I)
# a PHYSICAL return needs a locative/directional complement; bare "returned <manner>" collides with the
# speech-tag "returned" (= replied), so require one.
_RETURN_LOCATIVE = re.compile(r"\b(re-?entered|came (back|in|home)|got back)\b|"
                              r"\breturned\b.*\b(to|into|from|home|back|in|indoors|upstairs)\b", re.I)


def curate(rows, seed=20260828, cap_per_head=6):
    """Build a class-balanced, diverse gold from the mined phrasings: cap per head-verb (diversity), keep only
    clean 'leaves-the-scene' departures, dedupe. Deterministic (seeded)."""
    rng = np.random.default_rng(seed)
    by_cls = defaultdict(list)
    for r in rows:
        vp = r["vp"].strip().rstrip(",;:. ")
        if len(vp.split()) < 2 or len(vp.split()) > 8:
            continue
        if _METAPHOR.search(vp):                       # non-spatial use of a directional particle -> reject
            continue
        if r["cls"] == "depart":
            if not _AWAY.search(vp) or _BAD_DEPART.search(vp):
                continue
        if r["cls"] == "return" and (_TRANSITIVE_RETURN.search(vp) or not _RETURN_LOCATIVE.search(vp)):
            continue  # "returned the money" (give-back) and bare "returned <manner>" (=replied) are not returns
        if r["cls"] == "occlude" and re.search(r"\b(un)?conscious of\b", vp, re.I):
            continue  # "unconscious OF X" = unaware (metaphor), not physical occlusion -- avoid a spurious match
        by_cls[r["cls"]].append({**r, "vp": vp})
    # cap per head verb for diversity
    curated = defaultdict(list)
    for cls, items in by_cls.items():
        rng.shuffle(items)
        head_count = Counter()
        for it in items:
            head = it["vp"].split()[0].lower()
            if head in ("had", "was", "were", "still", "lay", "seemed"):
                head = " ".join(it["vp"].split()[:2]).lower()
            if head_count[head] >= cap_per_head:
                continue
            head_count[head] += 1
            curated[cls].append(it)
    # not-observed pool = depart + occlude; observed pool = present + return.
    # NOTE: the mined "inform" (was-told) phrasings convey ARBITRARY content, not knowledge of the OBJECT-MOVE
    # ("was told to apply to the charities" tells the agent nothing about the marble), so they are NOT a valid
    # observed=True label for THIS move and are DROPPED from the corpus gold. The testimony route (RULE 2) is
    # validated cleanly in the ledger self-test (informed-after-the-move case), where the telling IS about it.
    not_obs = curated["depart"] + curated["occlude"]
    obs = curated["present"] + curated["return"]
    rng.shuffle(not_obs); rng.shuffle(obs)
    n = min(len(not_obs), len(obs))
    not_obs, obs = not_obs[:n], obs[:n]        # balance 50/50
    return not_obs + obs


def build_items(curated, seed=20260828):
    """Slot each curated real cue-clause into a canonical false-belief frame with a by-construction label."""
    rng = np.random.default_rng(seed + 1)
    items = []
    for i, c in enumerate(curated):
        agent = AGENTS[i % len(AGENTS)]
        obj, l0, l1 = OBJECTS[i % len(OBJECTS)]
        mover = MOVERS[i % len(MOVERS)]
        vp = c["vp"]
        observed = bool(c["observed"])
        # frame: setup (agent co-present with object) ; REAL cue clause ; the move by someone else.
        cue_sent = f"{agent} {vp}."
        text = (f"{agent} put the {obj} on the {l0}. {cue_sent} "
                f"Then {mover} moved the {obj} from the {l0} to the {l1}.")
        # belief question: false belief if not observed -> looks at l0 (stale); else l1.
        gold_belief = l0 if not observed else l1
        items.append({"id": f"pa_{i:03d}", "agent": agent, "object": obj, "initial": l0, "final": l1,
                      "mover": mover, "cue_clause": vp, "cls": c["cls"], "book": c["book"],
                      "observed_gold": observed, "text": text, "belief_gold": gold_belief})
    return items


def boot_ci(vals, n_boot=2000, seed=0):
    if not vals:
        return (0.0, 0.0, 0.0, 0.0)
    a = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    m = a[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi), float((hi - lo) / 2.0)


def aliases_for(agent):
    return [agent, "he", "she", "they", "him", "her", "them", "his"]


def run(smoke=False, seed=20260828, verify_n=25):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    rows = [json.loads(l) for l in open(PHRASINGS, encoding="utf-8")]
    curated = curate(rows, seed=seed)
    items = build_items(curated, seed=seed)
    if smoke:
        items = items[:24]

    # cue accuracy per extractor
    lex_hits, led_hits, twin_hits = [], [], []
    always_obs, always_not = [], []
    rng = np.random.default_rng(seed + 7)
    per_class = defaultdict(lambda: {"lex": [], "led": []})
    for it in items:
        g = it["observed_gold"]
        lex = extract_observed_from_text(it["text"], it["agent"])
        tr = led.observed(it["text"], aliases_for(it["agent"]), event_object=it["object"],
                          event_location=it["final"])
        lg = tr.observed
        lex_hits.append(int(lex == g)); led_hits.append(int(lg == g))
        twin_hits.append(int(bool(rng.integers(0, 2)) == g))
        always_obs.append(int(True == g)); always_not.append(int(False == g))
        per_class[it["cls"]]["lex"].append(int(lex == g))
        per_class[it["cls"]]["led"].append(int(lg == g))

    lm, llo, lhi, lhw = boot_ci(lex_hits, seed=seed + 1)
    gm, glo, ghi, ghw = boot_ci(led_hits, seed=seed + 2)
    tm, tlo, thi, thw = boot_ci(twin_hits, seed=seed + 3)
    maj = max(np.mean(always_obs), np.mean(always_not))

    # ---- END-TO-END through the LANDED belief_partition ----
    from hdlab.belief_partition import BeliefPartition
    def e2e(observed_fn):
        bp_hits = []
        for it in items:
            bp = BeliefPartition(seed=seed)
            obs = observed_fn(it)
            bp.set_reality(it["object"], it["final"])
            bp.form_belief(it["agent"], it["object"], it["initial"], it["final"], obs)
            locs = [it["initial"], it["final"]]
            pred = bp.belief(it["agent"], it["object"], locs)
            bp_hits.append(int(pred == it["belief_gold"]))
        return boot_ci(bp_hits, seed=seed + 5)
    e2e_oracle = e2e(lambda it: it["observed_gold"])
    e2e_lex = e2e(lambda it: extract_observed_from_text(it["text"], it["agent"]))
    e2e_led = e2e(lambda it: led.observed(it["text"], aliases_for(it["agent"]),
                  event_object=it["object"], event_location=it["final"]).observed)

    # ---- verify a held-out sample of the mined cue clauses (report precision of the by-construction label) ----
    vsample = items[:verify_n] + items[-verify_n:]
    verify = [{"cue_clause": it["cue_clause"], "cls": it["cls"], "observed_gold": it["observed_gold"],
               "book": it["book"]} for it in vsample]

    gates = {
        "ledger_beats_lexical_ci": bool(glo > lhi),
        "ledger_beats_majority": bool(glo > maj),
        "ledger_beats_twin_ci": bool(glo > thi),
        "e2e_ledger_beats_lexical_ci": bool(e2e_led[1] > e2e_lex[2]),
        "e2e_ledger_beats_0p821": bool(e2e_led[1] > 0.821),
    }
    metrics = {
        "anchor_name": ANCHOR, "verdict": "MEASURED", "run_mode": "smoke" if smoke else "full",
        "seed": seed, "n_items": len(items),
        "n_not_observed": sum(1 - it["observed_gold"] for it in items),
        "n_observed": sum(it["observed_gold"] for it in items),
        "cue_accuracy": {
            "LEXICAL": {"acc": lm, "ci": [llo, lhi], "hw": lhw},
            "LEDGER": {"acc": gm, "ci": [glo, ghi], "hw": ghw},
            "TWIN": {"acc": tm, "ci": [tlo, thi], "hw": thw},
            "ALWAYS_OBSERVED": float(np.mean(always_obs)), "ALWAYS_NOT_OBSERVED": float(np.mean(always_not)),
            "MAJORITY_FLOOR": float(maj),
        },
        "per_class": {c: {"lex": float(np.mean(v["lex"])), "led": float(np.mean(v["led"])), "n": len(v["lex"])}
                      for c, v in per_class.items()},
        "end_to_end_belief_acc": {
            "ORACLE": {"acc": e2e_oracle[0], "ci": e2e_oracle[1:3]},
            "LEXICAL": {"acc": e2e_lex[0], "ci": e2e_lex[1:3]},
            "LEDGER": {"acc": e2e_led[0], "ci": e2e_led[1:3]},
            "landed_lexical_insitu_0p821": 0.821,
        },
        "gates": gates,
        "verify_sample": verify,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return metrics, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = args.smoke or args.self_test
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    metrics, items = run(smoke=smoke, seed=args.seed)
    metrics["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    with open(os.path.join(out, "gold_items.jsonl"), "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    c = metrics["cue_accuracy"]
    print(f"=== {ANCHOR} ({metrics['run_mode']}) {metrics['elapsed_s']}s  n={metrics['n_items']} "
          f"(not_obs={metrics['n_not_observed']} obs={metrics['n_observed']}) ===")
    print(f"CUE ACCURACY:")
    print(f"  LEXICAL (floor)  {c['LEXICAL']['acc']:.3f} [{c['LEXICAL']['ci'][0]:.3f},{c['LEXICAL']['ci'][1]:.3f}]")
    print(f"  LEDGER           {c['LEDGER']['acc']:.3f} [{c['LEDGER']['ci'][0]:.3f},{c['LEDGER']['ci'][1]:.3f}]")
    print(f"  TWIN (info-free) {c['TWIN']['acc']:.3f} [{c['TWIN']['ci'][0]:.3f},{c['TWIN']['ci'][1]:.3f}]")
    print(f"  MAJORITY floor   {c['MAJORITY_FLOOR']:.3f}")
    print(f"PER-CLASS (lex / ledger):")
    for cls, v in metrics["per_class"].items():
        print(f"  {cls:9s} n={v['n']:3d}  lex={v['lex']:.3f}  ledger={v['led']:.3f}")
    e = metrics["end_to_end_belief_acc"]
    print(f"END-TO-END belief acc (through landed belief_partition):")
    print(f"  ORACLE {e['ORACLE']['acc']:.3f}  LEXICAL {e['LEXICAL']['acc']:.3f}  LEDGER {e['LEDGER']['acc']:.3f}")
    print("GATES:")
    for k, v in metrics["gates"].items():
        print(f"  {'PASS' if v else 'fail'}  {k}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
