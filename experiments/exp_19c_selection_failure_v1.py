"""exp_19c_selection_failure_v1 -- DISAMBIGUATE EXACTLY the 19c who-did-what SELECTION wall (owner: "disambiguate
exactly the failure and research it so we deeply understand it. we need to understand all of the walls").

The prototype proved the 19c who-did-what residual is NOT the tagger/parser (a better tagger recovers +0.00) --
it is the SELECTION among post-verbal candidates where the position fallback (nearest post-verbal) picks the
wrong noun. This cell pulls the ACTUAL failure items (LitBank 19c, the organ picks WRONG) and characterizes,
per item, exactly what structure defeats position, so we understand the wall at the root:
  - n post-verbal candidates; distance(verb->gold); is gold the NEAREST post-verbal?
  - intervening structure between verb and gold: any ADP/prep (PP), any comma, any other NOUN (a distractor)?
  - the organ's WRONG pick vs gold: animacy of each (does the distractor differ in animacy?).
  - what the PARSER attached the gold to instead (the head), to see why noattach.
  - named failure buckets: DITRANSITIVE/dative (gold is 2nd of >=2 post-verbal nominals), PP-INTERVENING (a prep
    between verb and gold), HEAVY-SHIFT/far (gold distance>=3 with an intervening noun), COORD, NEAREST-WRONG.
Prints 25 real examples + the bucket distribution + the ANIMACY contrast. This is diagnosis, not a fix.
CPU numpy, NO torch/spaCy/LLM. ASCII. own dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_19c_selection_failure_v1")
NOMINAL = {"NOUN", "PROPN", "PRON"}


def anim(w):
    a = lookup_animacy(w)
    if isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal")):
        return "anim"
    if isinstance(a, dict) and a.get("animacy") == "inanimate":
        return "inan"
    return "unk"


def cand_ok(r):
    return len(GD.cands(r)) >= 2 and sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n_examples", type=int, default=25); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    rows = [r for r in V1.load_pop(V1.LB) if cand_ok(r)]

    fails = []
    n_noattach_post = 0
    for r in rows:
        toks = r["sent"].split()
        vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks)
        heads, _, _ = AEO.parse_with_conf(toks, pos, W)
        attaches = heads.get(gi0 + 1) == (vi0 + 1)
        postverbal = gi0 > vi0
        if not (postverbal and not attaches):
            continue
        n_noattach_post += 1
        # organ pick
        v1 = vi0 + 1; cands = [c + 1 for c in r["cand_idx"]]
        try:
            oidx = hybrid_role_patient(toks, pos, v1, cands)
            pick = toks[oidx - 1] if (oidx and 1 <= oidx <= len(toks)) else r.get("pos_pick")
            pick_idx0 = (oidx - 1) if (oidx and 1 <= oidx <= len(toks)) else None
        except Exception:
            pick = r.get("pos_pick"); pick_idx0 = None
        if pick == r["gold_head"]:
            continue                                              # organ got it -> not a failure
        # characterize the failure
        post_cands = [c for c in r["cand_idx"] if c > vi0]
        nearest_post = min(post_cands) if post_cands else None
        gold_is_nearest = (nearest_post == gi0)
        inter = list(range(vi0 + 1, gi0))                          # tokens strictly between verb and gold
        inter_pos = [pos[i] for i in inter if i < len(pos)]
        has_prep = "ADP" in inter_pos
        has_comma = any(toks[i] in (",", ";", "--", ":") for i in inter if i < len(toks))
        n_inter_noun = sum(1 for i in inter if i < len(pos) and pos[i] in NOMINAL)
        dist = gi0 - vi0
        gold_head_in_parse = heads.get(gi0 + 1)                     # what the parser attached gold to (1-based)
        gh_tok = toks[gold_head_in_parse - 1] if (gold_head_in_parse and 1 <= gold_head_in_parse <= len(toks)) else "ROOT"
        # bucket
        bucket = "NEAREST_WRONG"
        if has_prep and n_inter_noun >= 1:
            bucket = "PP_INTERVENING"
        elif n_inter_noun >= 1 and not gold_is_nearest:
            bucket = "DITRANSITIVE_or_2NOUN"
        elif dist >= 3:
            bucket = "HEAVY_SHIFT_far"
        elif has_comma:
            bucket = "COMMA_INTERVENING"
        fails.append({
            "sent": r["sent"][:180], "verb": r["verb"], "gold": r["gold_head"], "pick": pick,
            "dist": dist, "n_post_cands": len(post_cands), "gold_is_nearest": gold_is_nearest,
            "has_prep": has_prep, "n_inter_noun": n_inter_noun, "has_comma": has_comma,
            "parser_attached_gold_to": gh_tok, "anim_gold": anim(r["gold_head"]), "anim_pick": anim(pick),
            "bucket": bucket})

    n_fail = len(fails)
    buckets = Counter(f["bucket"] for f in fails)
    anim_contrast = Counter((f["anim_gold"], f["anim_pick"]) for f in fails)
    nearest_wrong_rate = round(sum(1 for f in fails if not f["gold_is_nearest"]) / n_fail, 3) if n_fail else 0.0
    prep_rate = round(sum(1 for f in fails if f["has_prep"]) / n_fail, 3) if n_fail else 0.0
    mean_dist = round(float(np.mean([f["dist"] for f in fails])), 2) if n_fail else 0.0
    parser_target = Counter(f["parser_attached_gold_to"] for f in fails).most_common(8)

    print("[19c SELECTION FAILURE] noattach_post items=%d, organ-WRONG failures=%d (%.1f%% of them)" % (
        n_noattach_post, n_fail, 100 * n_fail / max(1, n_noattach_post)), flush=True)
    print("\nFAILURE BUCKETS:", flush=True)
    for b, c in buckets.most_common():
        print("  %-22s %4d (%.1f%%)" % (b, c, 100 * c / n_fail), flush=True)
    print("\nSTRUCTURE: nearest-post != gold in %.1f%% | a PREP intervenes in %.1f%% | mean verb->gold dist=%.2f | mean post-cands=%.2f" % (
        100 * nearest_wrong_rate, 100 * prep_rate, mean_dist, float(np.mean([f["n_post_cands"] for f in fails])) if n_fail else 0), flush=True)
    print("ANIMACY (gold, wrong-pick) contrast:", dict(anim_contrast.most_common()), flush=True)
    print("PARSER attached the gold patient to (instead of the verb):", parser_target, flush=True)
    print("\n=== %d REAL FAILURE EXAMPLES ===" % min(args.n_examples, n_fail), flush=True)
    for f in fails[:args.n_examples]:
        print("  [%s] v=%r gold=%r organ_picked=%r (dist=%d,ncand=%d,prep=%s,internoun=%d,attached_to=%r)\n     \"%s\"" % (
            f["bucket"], f["verb"], f["gold"], f["pick"], f["dist"], f["n_post_cands"], f["has_prep"],
            f["n_inter_noun"], f["parser_attached_gold_to"], f["sent"]), flush=True)

    res = {"n_noattach_post": n_noattach_post, "n_fail": n_fail, "buckets": dict(buckets),
           "nearest_wrong_rate": nearest_wrong_rate, "prep_rate": prep_rate, "mean_dist": mean_dist,
           "anim_contrast": {str(k): v for k, v in anim_contrast.items()},
           "parser_attached_to_top": parser_target, "examples": fails[:args.n_examples]}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "c19_selection_failure_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
