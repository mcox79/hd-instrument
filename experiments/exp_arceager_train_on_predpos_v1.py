"""exp_arceager_train_on_predpos_v1 -- shrink the DEPLOYMENT gap (gold-POS UAS 0.842 vs predicted-POS 0.805 = the
tagger costs 3.7 pts) by TRAINING the parser on the tagger's PREDICTED POS, so train/test POS distributions match
and the parser learns to compensate for the tagger's systematic errors. Brain-plausible: comprehension learns to
parse the NOISY input it actually receives (the tag->parse coupling is interactive, not a clean pipeline). ONE
variable = train-POS source (gold vs tagger-predicted); both evaluated on the DEPLOYMENT condition (predicted-POS
test). Rich arc-eager reused from exp_arceager_richfeat_transition. CPU numpy only, NO torch/spaCy/LLM. ASCII.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_arceager_richfeat_transition_v1 as RF

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_arceager_train_on_predpos_v1")


def retag(sents, tg):
    out = []
    for s in sents:
        toks = [t[1] for t in s]; pos = tg.tag(toks)
        out.append([(t[0], t[1], pos[i], t[3], t[4], t[5]) for i, t in enumerate(s)])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    train_g = [s for s in RF._load_ud_feats("train") if 1 <= len(s) <= RF.MAXLEN]
    test_g = [s for s in RF._load_ud_feats("test") if 1 <= len(s) <= RF.MAXLEN]
    if args.smoke:
        RF.EPOCHS = min(RF.EPOCHS, 3); train_g = train_g[:400]; test_g = test_g[:150]
    print("[data] train=%d test=%d retagging..." % (len(train_g), len(test_g)), flush=True)
    train_p = retag(train_g, tg); test_p = retag(test_g, tg)
    # tagger accuracy on test (content of tok[2] pred vs gold) for context
    hit = tot = 0
    for sg, sp in zip(test_g, test_p):
        for tgold, tp in zip(sg, sp):
            hit += int(tgold[2] == tp[2]); tot += 1
    tagger_acc = round(hit / tot, 4)
    print("[tagger] UPOS accuracy on test = %.4f" % tagger_acc, flush=True)

    res = {"tagger_upos_acc": tagger_acc}
    # ARM A: train on GOLD pos -> deploy on PRED pos (the current deployed model's condition)
    tt = time.time(); W_g = RF._train(train_g, args.seed, True)
    res["trainGOLD_evalPRED"] = round(RF.uas(test_p, W_g, True), 4)
    res["trainGOLD_evalGOLD"] = round(RF.uas(test_g, W_g, True), 4)
    print("[A] train GOLD-POS: eval PRED-POS=%.4f  eval GOLD-POS=%.4f (%.0fs)" % (
        res["trainGOLD_evalPRED"], res["trainGOLD_evalGOLD"], time.time() - tt), flush=True)
    # ARM B: train on PRED pos -> deploy on PRED pos (train-test match)
    tt = time.time(); W_p = RF._train(train_p, args.seed, True)
    res["trainPRED_evalPRED"] = round(RF.uas(test_p, W_p, True), 4)
    print("[B] train PRED-POS: eval PRED-POS=%.4f (%.0fs)" % (res["trainPRED_evalPRED"], time.time() - tt), flush=True)

    res["deploy_gain_predpos"] = round(res["trainPRED_evalPRED"] - res["trainGOLD_evalPRED"], 4)
    res["deploy_gap_recovered_frac"] = round(res["deploy_gain_predpos"] / max(1e-9, res["trainGOLD_evalGOLD"] - res["trainGOLD_evalPRED"]), 3)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "arceager_train_on_predpos_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[SUMMARY] tagger=%.4f | deployed(PRED) trainGOLD=%.4f trainPRED=%.4f gain=%+.4f (recovers %.0f%% of the %.4f tagger gap) [%.0fs]" % (
        tagger_acc, res["trainGOLD_evalPRED"], res["trainPRED_evalPRED"], res["deploy_gain_predpos"],
        100 * res["deploy_gap_recovered_frac"], res["trainGOLD_evalGOLD"] - res["trainGOLD_evalPRED"], time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
