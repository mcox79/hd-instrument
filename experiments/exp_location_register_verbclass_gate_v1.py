"""exp_location_register_verbclass_gate_v1 -- the real-prose MOTION-EXTRACTION wall, drilled and measured.

THE WALL (surfaced when running the register on raw literary prose): a bare "to X" PP is read as the agent's
spatial GOAL regardless of the verb, so "said to Alice" / "gave it to her" / "pointed to the door" (X =
ADDRESSEE / RECIPIENT) are mis-read as relocations. The brain resolves this with the verb's EVENT FRAME:
VerbNet encodes it as two distinct thematic roles -- Destination (+concrete location, self-motion verbs) vs
Recipient (+animate, communication/transfer verbs) (Rappaport Hovav & Levin 2008; Levin 1993; research note
2026-08-28). The fix is the ATL/VerbNet MOTION-FRAME gate: a bare goal PP is a destination only if the verb
evokes self-motion and is not a communication/transfer verb; PATH SATELLITES bypass it (Talmy -- no manner-
verb whitelist).

THIS CELL measures the gate on REAL prose, stratified into the research's three VerbNet buckets:
  MOTION            self-motion verbs (go/walk/run/swim/...) -- 'to X' SHOULD read as a Goal (gate keeps it).
  COMM_TRANSFER     communication/transfer verbs (say/tell/give/point/...) -- 'to X' should NOT (gate blocks).
  AMBIG_CAUSED      caused-motion (throw/send/pass/hand/kick/carry/...) -- genuinely mixed (verb class carries
                    ZERO signal; the finer fix is the coref/entity-status of X -- a mapped follow-on).
Real "PERSON-subject VERB ... to/into/for GROUND" tokens are mined from on-disk novels. We report the agent-
GOAL extraction RATE per bucket under an ABLATION: NO_GATE -> +PLACE_TYPING -> +MOTION_FRAME. The gate is
correct iff it keeps MOTION Goals and drives COMM_TRANSFER Goals toward 0 (precision), and AMBIG stays mid.

Writes ONLY to data/exp_location_register_verbclass_gate_v1[/ _smoke]. NO hdlab writes. spaCy-bound -> INLINE.
ASCII only.
# KB_REFERENT: data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt
# KB_REFERENT: data/corpora/alice_in_wonderland/cleaned/alice_in_wonderland.clean.txt
# KB_REFERENT: data/corpora/sherlock_holmes/cleaned/adventures.clean.txt
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.location_register import (LocationRegister, DEICTIC_SCENE, is_motion_verb,
                                           _COMM_TRANSFER_BLOCK)

ANCHOR = "location_register_verbclass_gate_v1"
CORPORA = ["data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt",
           "data/corpora/alice_in_wonderland/cleaned/alice_in_wonderland.clean.txt",
           "data/corpora/sherlock_holmes/cleaned/adventures.clean.txt"]
# VerbNet ambiguous caused-motion neighbourhood (throw-17.1, send-11.1 + neighbours).
AMBIG_CAUSED = {"throw", "send", "pass", "hand", "kick", "mail", "toss", "fling", "roll", "carry",
                "bring", "take", "push", "pull", "drag", "lead", "hurl", "shove", "post", "chuck"}


def mine_tokens(nlp, smoke=False):
    """Real 'PERSON-subject VERB ... to/into/for GROUND' tokens with the verb lemma + subtree text."""
    toks = []
    for rel in CORPORA:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            continue
        txt = re.sub(r"\s+", " ", open(path, encoding="utf-8", errors="ignore").read())
        txt = txt[:40000] if smoke else txt[:120000]
        for s in nlp(txt).sents:
            subs = [t for t in s if t.dep_ in ("nsubj", "nsubjpass") and t.pos_ == "PROPN"
                    and t.head.dep_ == "ROOT" and t.head.pos_ == "VERB"]
            if not subs:
                continue
            name = subs[0].text
            v = subs[0].head
            # require a to/into/for PP somewhere under the verb (the ambiguous construction)
            if not any(c.dep_ == "prep" and c.text.lower() in ("to", "into", "for") for c in v.subtree):
                continue
            toks.append({"name": name, "verb": v.lemma_.lower(), "sent": s.text.strip()[:160]})
    return toks


def bucket(verb):
    if verb in _COMM_TRANSFER_BLOCK:
        return "COMM_TRANSFER"
    if verb in AMBIG_CAUSED:
        return "AMBIG_CAUSED"
    if is_motion_verb(verb):
        return "MOTION"
    return "OTHER"


def root_goal(reg: LocationRegister, doc, name):
    """Does `reg._goal_node` read a spatial GOAL from the PERSON-subject ROOT verb of this sentence? Tests
    the exact (verb, to-PP) pair the token was bucketed on -- so the bucket label matches the decision."""
    aliases = [name, "he", "she", "him", "her", "his", "their"]
    for s in doc.sents:
        root = next((t for t in s if t.dep_ == "ROOT" and t.pos_ == "VERB"), None)
        if root is None:
            continue
        if not reg._led._subject_is_agent(s, aliases, name):
            continue
        g = reg._goal_node(s, root, aliases)
        return g is not None and g != "<away>"
    return False


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    toks = mine_tokens(nlp, smoke=smoke)
    regs = {   # clean ablation via constructor flags
        "NO_GATE": LocationRegister(nlp, place_typing=False, motion_frame=False),
        "PLACE_ONLY": LocationRegister(nlp, place_typing=True, motion_frame=False),
        "FULL": LocationRegister(nlp, place_typing=True, motion_frame=True),
    }
    by_bucket = defaultdict(lambda: {c: 0 for c in regs})
    n_bucket = defaultdict(int)
    docs = {t["sent"]: nlp(t["sent"]) for t in toks}
    for t in toks:
        b = bucket(t["verb"]); n_bucket[b] += 1
        for cname, reg in regs.items():
            if root_goal(reg, docs[t["sent"]], t["name"]):
                by_bucket[b][cname] += 1

    rates = {b: {c: (by_bucket[b][c] / n_bucket[b] if n_bucket[b] else 0.0) for c in regs}
             for b in n_bucket}
    # PRECISION of Goal-extraction = motion-bucket Goals / all extracted Goals (across MOTION+COMM+AMBIG).
    def precision(cname):
        tp = by_bucket["MOTION"][cname]
        fp = by_bucket["COMM_TRANSFER"][cname] + by_bucket["AMBIG_CAUSED"][cname]
        return (tp / (tp + fp)) if (tp + fp) else 0.0
    prec = {c: precision(c) for c in regs}
    # The gate's JOB is PRECISION (block non-destination 'to X'). MOTION-bucket rate is a confounded recall
    # proxy (motion verbs also take NON-spatial 'to X': 'went to sleep', 'came to think') -> reported, not gated.
    gates = {
        "full_blocks_comm_goals": bool(rates.get("COMM_TRANSFER", {}).get("FULL", 1.0) <= 0.10),
        "gate_raises_precision": bool(prec["FULL"] > prec["NO_GATE"] + 0.20),
        "motion_kept_above_comm": bool(rates.get("MOTION", {}).get("FULL", 0)
                                       > rates.get("COMM_TRANSFER", {}).get("FULL", 0) + 0.20),
    }
    return {"anchor_name": ANCHOR, "verdict": "HARD_PASS" if all(gates.values()) else "MIDDLE_BAND",
            "run_mode": "smoke" if smoke else "full", "seed": seed, "n_tokens": len(toks),
            "n_per_bucket": dict(n_bucket), "goal_rate_by_bucket": rates,
            "goal_precision": prec, "gates": gates, "ts_iso": datetime.now(timezone.utc).isoformat()}


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
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  n_tokens={m['n_tokens']} ===")
    print(f"n per bucket: {m['n_per_bucket']}")
    print(f"AGENT-GOAL extraction RATE by bucket (NO_GATE -> PLACE_ONLY -> FULL):")
    for b, r in m["goal_rate_by_bucket"].items():
        print(f"  {b:14s} {r['NO_GATE']:.3f} -> {r['PLACE_ONLY']:.3f} -> {r['FULL']:.3f}   (n={m['n_per_bucket'][b]})")
    print(f"GOAL-extraction PRECISION (motion / all-extracted): "
          f"NO_GATE {m['goal_precision']['NO_GATE']:.3f} -> PLACE_ONLY {m['goal_precision']['PLACE_ONLY']:.3f} "
          f"-> FULL {m['goal_precision']['FULL']:.3f}")
    print("VERDICT:", m["verdict"], "GATES:", m["gates"])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
