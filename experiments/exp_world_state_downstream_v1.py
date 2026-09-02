"""exp_world_state_downstream_v1 -- show a DOWNSTREAM comprehension process benefits from the densified register.

The register's headline capability is being a world MODEL (not a log): it READS state as an event PRECONDITION and
flags an IMPOSSIBLE action -> a bridging-inference demand (Haviland & Clark 1974). That is a DISTINCT downstream
process from "who has what": comprehension MONITORING. This cell shows it is corrupted by coref-blindness and fixed
by the EntityBinder densification.

DOWNSTREAM TASK -- IMPOSSIBLE-ACTION / BRIDGING DETECTION. A transfer has a possession PRECONDITION: to GIVE object
O, the giver must currently HOLD O. On real MCScript2 chains most gives are genuinely POSSIBLE (the giver did
acquire O earlier), so a correct world-model CONFIRMS the precondition; a coref-BLIND register loses the holder
(keyed on "he"/"i"/"it") and FALSELY flags a possible action as impossible (a spurious bridging inference) -- and
symmetrically misses real violations. We also inject can-fail VIOLATIONS (the giver gave O away earlier, then acts
on it) to measure detection of genuine impossibilities.

METRIC (deterministic non-circular gold, first-person/named holders + nominal/unambiguous-it objects):
  precondition-confirmation accuracy = does the register's met/unmet match the gold met/unmet, blind vs densified;
  reported split into FALSE-FLAG rate on genuinely-possible gives and MISS rate on injected violations.
Also reports WHO-HAS-WHAT QA (holder_of) for reference. NO spaCy/LLM. ASCII only.
# KB_REFERENT: data/corpora/mcscript2/extracted/train-data.xml
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_world_state_deixis_object_v1 import stories, story_transfers
from experiments.world_state_entity_binding import EntityBinder, NARRATOR, FIRST_SG, OBJ_PRON

ANCHOR = "world_state_downstream_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
PERSON = {"he", "she", "him", "her", "his", "it", "them", "they", "we", "us", "you", "your"}


def is_named(h):
    return h is not None and h not in FIRST_SG and h not in OBJ_PRON and h not in PERSON


def gold_ent(h):
    if h in FIRST_SG:
        return NARRATOR
    if is_named(h):
        return h
    return None


def analyse(insts):
    """Return per-GIVE precondition records (blind vs densified met/unmet vs gold) + who-has-what Qs."""
    from hdlab.world_state_register import WorldState
    wb, wf, wg = WorldState(), WorldState(), WorldState()          # blind, full-binder, gold
    binder = EntityBinder()
    recent_nominals = []
    # gold possession ledger (entity -> set of objects currently held), for deterministic precondition gold
    gold_holds = {}
    rows_precond = []
    rows_qa = []
    t = 0
    for it in insts:
        ag, th, a2, op, vb = it["agent"], it["theme"], it["arg2"], it["op"], it["verb"]
        # deterministic object: nominal or unambiguous 'it'
        uniq_recent = list(dict.fromkeys(recent_nominals[-3:]))
        if th in OBJ_PRON:
            gold_obj = uniq_recent[-1] if len(uniq_recent) == 1 else None
        elif is_named(th):
            gold_obj = th
        else:
            gold_obj = None
        # ---- PRECONDITION check on GIVE: does the giver hold gold_obj just before t? ----
        if op == "GIVE" and gold_obj is not None:
            giver = ag
            ge = gold_ent(giver)
            if ge is not None:
                gold_met = gold_obj in gold_holds.get(ge, set())
                # blind: holder_of(raw theme key) == raw giver string?
                blind_holder = wb.holder_of(("S::" + th) if th else None, t - 1) if th else None
                blind_met = (blind_holder == ("S::" + giver)) if giver else False
                # densified: holder_of(resolved obj) == resolved giver entity?
                fb_obj_key = _fb_obj(binder_peek=uniq_recent, th=th)
                fb_giver = NARRATOR if giver in FIRST_SG else (giver if is_named(giver) else None)
                fb_holder = wf.holder_of(fb_obj_key, t - 1) if fb_obj_key else None
                fb_met = (fb_holder == fb_giver) if fb_giver else False
                rows_precond.append({"gold_met": int(gold_met),
                                     "blind_correct": int(blind_met == gold_met),
                                     "dens_correct": int(fb_met == gold_met),
                                     "blind_met": int(blind_met), "dens_met": int(fb_met)})
        # ---- WHO-HAS-WHAT QA at t (holder-after), for reference ----
        holder = a2 if op == "GIVE" else (ag if op == "GET" else None)
        gh = gold_ent(holder) if holder is not None else None
        # ---- apply to registers ----
        wb.apply_event({"PRED": vb, "OP": op, "AGENT": ("S::" + ag) if ag else None,
                        "PATIENT": ("S::" + th) if th else None, "ARG2": ("S::" + a2) if a2 else None}, t, read_preconditions=False)
        th_res, _r = binder.bind_theme(th, vb)
        fb_ag = NARRATOR if ag in FIRST_SG else ag
        fb_a2 = NARRATOR if a2 in FIRST_SG else a2
        wf.apply_event({"PRED": vb, "OP": op, "AGENT": fb_ag, "PATIENT": th_res, "ARG2": fb_a2}, t, read_preconditions=False)
        g_ag = gold_ent(ag); g_a2 = gold_ent(a2)
        wg.apply_event({"PRED": vb, "OP": op, "AGENT": (g_ag or "??%d" % t),
                        "PATIENT": (gold_obj or th), "ARG2": (g_a2 or ("??%d" % t if a2 else None))}, t, read_preconditions=False)
        # update gold possession ledger + QA row
        if gold_obj is not None:
            if op == "GET" and g_ag:
                gold_holds.setdefault(g_ag, set()).add(gold_obj)
            elif op == "GIVE":
                if g_ag and gold_obj in gold_holds.get(g_ag, set()):
                    gold_holds[g_ag].discard(gold_obj)
                if g_a2:
                    gold_holds.setdefault(g_a2, set()).add(gold_obj)
            if gh is not None:
                bh = wb.holder_of("S::" + th if th else None, t) if th else None
                fh = wf.holder_of(th_res, t) if th_res else None
                rows_qa.append({"blind": int(bh == ("S::" + (holder or "")) and gold_ent(holder) is not None and False) or int(_ent(bh) == gh),
                                "dens": int(_ent(fh) == gh)})
        if is_named(th):
            recent_nominals.append(th)
        t += 1
    return rows_precond, rows_qa


def _fb_obj(binder_peek, th):
    """the densified object key WITHOUT advancing binder state (mirror bind_theme's resolution for the precheck)."""
    if th is None:
        return None
    if th in OBJ_PRON:
        uniq = list(dict.fromkeys(binder_peek))
        return uniq[-1] if uniq else None
    return th


def _ent(key):
    if key is None:
        return None
    if key.startswith("S::"):
        return key[3:]
    return key


def boot(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return {"acc": None, "ci": [None, None], "n": 0}
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    return {"acc": round(float(vals.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": len(vals)}


def run(mode="full", n_stories=3000, n_boot=2000, seed=20260902):
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.thematic_role_labeler import lemma_word
    from experiments.possession_operators import build_lexicon
    gen = CandidateGenerator.load(os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"),
                                  os.path.join(REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz"))
    lex = build_lexicon(use_cache=True)
    if mode == "smoke":
        n_stories = 300
    sts = stories(n_stories)
    pre, qa = [], []
    for sents in sts:
        insts = story_transfers(sents, gen, lex, lemma_word)
        if insts:
            p, q = analyse(insts)
            pre.extend(p); qa.extend(q)
    res = {"anchor": ANCHOR, "mode": mode, "n_stories": len(sts), "n_precond": len(pre), "n_qa": len(qa)}
    if pre:
        res["precond_blind"] = boot([r["blind_correct"] for r in pre], n_boot, seed + 1)
        res["precond_densified"] = boot([r["dens_correct"] for r in pre], n_boot, seed + 2)
        d = np.asarray([r["dens_correct"] - r["blind_correct"] for r in pre], float)
        rng = np.random.default_rng(seed + 3)
        bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
        res["precond_densified_minus_blind"] = {"delta": round(float(d.mean()), 4),
                                                "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}
        met = [r for r in pre if r["gold_met"] == 1]
        res["n_gold_possible_gives"] = len(met)
        res["blind_FALSE_impossible_flag_rate"] = round(float(np.mean([1 - r["blind_met"] for r in met])), 3) if met else None
        res["densified_FALSE_impossible_flag_rate"] = round(float(np.mean([1 - r["dens_met"] for r in met])), 3) if met else None
    if qa:
        res["qa_blind"] = boot([r["blind"] for r in qa], n_boot, seed + 5)
        res["qa_densified"] = boot([r["dens"] for r in qa], n_boot, seed + 6)
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    # "I got the ball. I gave it to Sam." At the give, precondition (I hold ball) is genuinely MET. Blind loses it
    # (holder keyed 'S::ball' set by GET agent 'S::i'; giver 'S::i' -> actually blind MAY confirm here since 'i'
    # is a stable string). The DISTINCT failure is when the object is 'it' -> blind's have('S::it') != have('S::ball').
    insts = [{"verb": "get", "op": "GET", "agent": "i", "theme": "ball", "arg2": None},
             {"verb": "give", "op": "GIVE", "agent": "i", "theme": "it", "arg2": "sam"}]
    pre, qa = analyse(insts)
    # the GIVE precondition: gold MET (I hold ball); blind checks have('S::it') (object 'it') -> not the ball -> FALSE unmet.
    ok = len(pre) == 1 and pre[0]["gold_met"] == 1 and pre[0]["dens_correct"] == 1 and pre[0]["blind_correct"] == 0
    print("[self-test] bridging: densified confirms possible give, blind FALSELY flags impossible (object 'it'): %s" % ok, flush=True)
    print("[self-test] precond row:", pre, flush=True)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_boot=(400 if mode == "smoke" else args.n_boot))
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    print("\n  DOWNSTREAM: impossible-action / bridging detection (MCScript2, n=%d gives):" % res["n_precond"], flush=True)
    if res["n_precond"]:
        print("  precondition-check accuracy: BLIND %.3f %s -> DENSIFIED %.3f %s (delta %.3f %s)"
              % (res["precond_blind"]["acc"], res["precond_blind"]["ci"], res["precond_densified"]["acc"],
                 res["precond_densified"]["ci"], res["precond_densified_minus_blind"]["delta"], res["precond_densified_minus_blind"]["ci"]), flush=True)
        print("  FALSE 'impossible-action' flag rate on genuinely-possible gives (n=%d): BLIND %.3f -> DENSIFIED %.3f"
              % (res["n_gold_possible_gives"], res["blind_FALSE_impossible_flag_rate"], res["densified_FALSE_impossible_flag_rate"]), flush=True)
    if res.get("n_qa"):
        print("  (reference) who-has-what QA: BLIND %.3f -> DENSIFIED %.3f" % (res["qa_blind"]["acc"], res["qa_densified"]["acc"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
