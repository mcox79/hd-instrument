"""exp_perceptual_access_distance_v1 -- prove the SPATIAL route (RULE 1) tracks a departure across ARBITRARY
DISTANCE when run over the full document, and that the intact-WINDOW chance result was a WINDOWING artifact,
not a mechanism failure.

CLAIM (brain-foundational, Zwaan incremental situation model): presence is a STATE the reader maintains across
the whole narrative, so an agent who left the scene stays absent no matter how many sentences intervene before
the change. A window-limited reader loses the departure once it scrolls out of view.

DESIGN: take the corpus not-observed items (agent DEPARTS or is OCCLUDED, then someone moves the object).
Insert K neutral filler sentences BETWEEN the cue clause and the move, sweep K in {0,2,5,10,20}, and compare:
  FULL     -- ledger over the whole text (RULE 0 OFF, so the SPATIAL route alone decides). Should stay high: the
              presence interval opened at the departure persists to the move regardless of K.
  WINDOWED -- ledger over only the last 3 sentences (departure is out-of-window for K>=2). Should COLLAPSE to
              chance as K grows -- reproducing the intact-window result and localising it to windowing.
Gold = not-observed (observed should be False). A twin (random observation) sits at chance.

Light, runs inline. Remote-safe pattern: spaCy import inside run(); FULL is the bare-invocation default.
Writes ONLY to data/exp_perceptual_access_distance_v1[/ _smoke]. NO hdlab writes. ASCII only.
# KB_REFERENT: data/mine_presence_phrasings_v1/phrasings.jsonl
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments import exp_perceptual_access_corpus_v1 as E

ANCHOR = "perceptual_access_distance_v1"
PHRASINGS = os.path.join(REPO, "data", "mine_presence_phrasings_v1", "phrasings.jsonl")
KS = [0, 2, 5, 10, 20]
# neutral fillers: no agent alias, no motion/occlusion/absence cue -> must not change any agent's state.
FILLERS = [
    "The clock ticked steadily on the mantel.", "Rain had been falling since the morning.",
    "A cart rumbled somewhere far off along the lane.", "The fire burned low in the grate.",
    "It was a grey and ordinary afternoon.", "A church bell tolled the hour once more.",
    "The wind stirred the bare branches by the fence.", "The kettle sang faintly on the hob.",
    "The day wore on much as any other.", "A sparrow chirped upon the sill and flew off.",
    "The old house was very quiet just then.", "Dust settled slowly along the windowsill.",
    "The pages of a newspaper rustled somewhere.", "A distant train whistled and was gone.",
    "The afternoon light lay flat across the boards.", "Nothing of note happened for a while.",
    "The tea had long since gone cold.", "A fly buzzed lazily against the pane.",
    "The street outside was empty and still.", "The hours crept by without remark.",
]


def build_distance_items(seed=20260828):
    phr = [json.loads(l) for l in open(PHRASINGS, encoding="utf-8")]
    cur = E.curate(phr, seed=seed)
    items = E.build_items(cur, seed=seed)
    # keep only NOT-OBSERVED (the departure/occlusion cases -- where tracking the absence across distance matters)
    return [it for it in items if not it["observed_gold"]]


def split_frame(it):
    """The corpus frame is: '{Agent} put ...{L0}. {Agent} {cue}. Then {mover} moved ...{L1}.' Return the three
    sentences (setup, cue, move) so we can insert fillers BETWEEN cue and move."""
    agent, obj, l0, l1, mover, vp = it["agent"], it["object"], it["initial"], it["final"], it["mover"], it["cue_clause"]
    setup = f"{agent} put the {obj} on the {l0}."
    cue = f"{agent} {vp}."
    move = f"Then {mover} moved the {obj} from the {l0} to the {l1}."
    return setup, cue, move


def run(smoke=False, seed=20260828):
    import spacy  # inside run() -- remote-safe (remote has no spaCy; this cell is inline-only anyway)
    from experiments.perceptual_access_ledger import PerceptualAccessLedger
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    items = build_distance_items(seed)
    if smoke:
        items = items[:15]
    rng = np.random.default_rng(seed + 1)
    rows = {}
    for K in KS:
        full_ok, win_ok, twin_ok = [], [], []
        for it in items:
            setup, cue, move = split_frame(it)
            fillers = [FILLERS[(i + hash(it["id"]) % len(FILLERS)) % len(FILLERS)] for i in range(K)]
            sents = [setup, cue] + fillers + [move]
            text = " ".join(sents)
            ev = len(sents) - 1  # the move is the last sentence
            al = E.aliases_for(it["agent"])
            # FULL: spatial route only (RULE 0 off) over the whole text
            tr_full = led.observed(text, al, event_index=ev, use_epistemic=False)
            full_ok.append(int(tr_full.observed == it["observed_gold"]))
            # WINDOWED: only the last 3 sentences (departure out-of-window for K>=2)
            wsents = sents[-3:]
            wtext = " ".join(wsents)
            tr_win = led.observed(wtext, al, event_index=len(wsents) - 1, use_epistemic=False)
            win_ok.append(int(tr_win.observed == it["observed_gold"]))
            twin_ok.append(int(bool(rng.integers(0, 2)) == it["observed_gold"]))
        rows[K] = {"full": float(np.mean(full_ok)), "windowed": float(np.mean(win_ok)),
                   "twin": float(np.mean(twin_ok)), "n": len(items)}
    # gate: FULL stays high (>=0.85) at the largest distance; WINDOWED collapses toward chance
    kmax = KS[-1]
    gate = {
        "full_robust_at_max_distance": bool(rows[kmax]["full"] >= 0.85),
        "windowed_collapses_with_distance": bool(rows[kmax]["windowed"] < rows[0]["windowed"] - 0.2),
        "full_beats_windowed_at_max": bool(rows[kmax]["full"] > rows[kmax]["windowed"] + 0.2),
    }
    return {"anchor_name": ANCHOR, "verdict": "MEASURED", "run_mode": "smoke" if smoke else "full",
            "seed": seed, "Ks": KS, "n_not_observed_items": len(items), "by_distance": rows, "gates": gate,
            "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"   # bare invocation == FULL (remote-safe)
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    m = run(smoke=smoke, seed=args.seed); m["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  n_not_observed={m['n_not_observed_items']} ===")
    print("  distance K   FULL(spatial, whole text)   WINDOWED(last 3 sents)   TWIN")
    for K in KS:
        r = m["by_distance"][K]
        print(f"    K={K:<3d}        {r['full']:.3f}                     {r['windowed']:.3f}                {r['twin']:.3f}")
    print("GATES:", m["gates"])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
