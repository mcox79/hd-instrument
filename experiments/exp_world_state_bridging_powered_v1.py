"""exp_world_state_bridging_powered_v1 -- POWERED impossible-action / bridging-inference detection (downstream
consumer #2), fixing the n=8/underpowered natural-text version by INJECTING balanced precondition VIOLATIONS.

THE DOWNSTREAM TASK (comprehension monitoring; Haviland & Clark 1974): given "entity E acts on object O at time t"
requiring E to HOLD O, decide MET (possible) vs UNMET (impossible -> a bridging inference is demanded). We probe
the register over real MCScript2 possession chains with a BALANCED, can-fail set (chance = 0.5):
  VALID probe    : actor E = the current gold holder of O  -> gold MET.
  VIOLATION probe: actor E = a PRIOR holder of O who gave it away (or another entity)  -> gold UNMET (a genuine
                   impossible action -- E plausibly might act on O, so catching that E no longer holds it IS the
                   bridging inference).
A register decides MET iff its holder_of(O, t) maps to E's ENTITY. The coref-BLIND register keys on raw strings
("i"/"he"/"it"), so it loses the entity and mis-decides (FALSE-flags possible actions as impossible, and MISSES
violations); the EntityBinder-DENSIFIED register keys on the entity and decides correctly.

METRIC: balanced detection accuracy (chance 0.5), blind vs densified vs gold(sanity) vs a random-actor TWIN, plus
FALSE-flag rate (VALID->UNMET) and MISS rate (VIOLATION->MET). Deterministic non-circular gold (first-person->
NARRATOR / named; nominal or unambiguous-'it' objects). NO spaCy/LLM. ASCII only.
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

ANCHOR = "world_state_bridging_powered_v1"
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


def _ent_of_key(key):
    """map an arm's holder KEY to an ENTITY (the situation model queries entities): NARRATOR/name pass through;
    a raw pronoun/'it' string -> None (the blind register cannot name the entity)."""
    if key is None:
        return None
    if key == NARRATOR:
        return NARRATOR
    if key.startswith("S::"):
        h = key[3:]
        return h if is_named(h) else None
    return key if not str(key).startswith("S::") else None


def analyse(insts, rng):
    from hdlab.world_state_register import WorldState
    wb, wf, wg = WorldState(), WorldState(), WorldState()      # blind, densified, gold
    binder = EntityBinder()
    recent_nominals = []
    gold_holder = {}                 # object -> current gold holder entity
    past_holders = {}                # object -> list of prior holder entities (for violation actors)
    entities_seen = set()
    probes = []                      # (obj, t, actor_entity, gold_met)
    t = 0
    for it in insts:
        ag, th, a2, op, vb = it["agent"], it["theme"], it["arg2"], it["op"], it["verb"]
        uniq_recent = list(dict.fromkeys(recent_nominals[-3:]))
        gold_obj = (uniq_recent[-1] if len(uniq_recent) == 1 else None) if th in OBJ_PRON else (th if is_named(th) else None)
        # apply to all three registers
        wb.apply_event({"PRED": vb, "OP": op, "AGENT": ("S::" + ag) if ag else None,
                        "PATIENT": ("S::" + th) if th else None, "ARG2": ("S::" + a2) if a2 else None}, t, read_preconditions=False)
        th_res, _r = binder.bind_theme(th, vb)
        wf.apply_event({"PRED": vb, "OP": op, "AGENT": (NARRATOR if ag in FIRST_SG else ag),
                        "PATIENT": th_res, "ARG2": (NARRATOR if a2 in FIRST_SG else a2)}, t, read_preconditions=False)
        g_ag, g_a2 = gold_ent(ag), gold_ent(a2)
        wg.apply_event({"PRED": vb, "OP": op, "AGENT": (g_ag or "??%d" % t),
                        "PATIENT": (gold_obj or th), "ARG2": (g_a2 or ("??%d" % t if a2 else None))}, t, read_preconditions=False)
        # update deterministic gold holder of gold_obj
        new_holder = None
        if gold_obj is not None:
            if op == "GET" and g_ag:
                new_holder = g_ag
            elif op == "GIVE" and g_a2:
                new_holder = g_a2
            if new_holder is not None:
                prev = gold_holder.get(gold_obj)
                if prev is not None and prev != new_holder:
                    past_holders.setdefault(gold_obj, []).append(prev)
                gold_holder[gold_obj] = new_holder
                entities_seen.add(new_holder)
                # ---- generate a BALANCED probe pair at this state (query time t, object gold_obj) ----
                # VALID: actor = current holder
                probes.append((gold_obj, t, new_holder, 1))
                # VIOLATION: a PRIOR holder who no longer holds it, else another seen entity
                cands = [e for e in past_holders.get(gold_obj, []) if e != new_holder]
                if not cands:
                    cands = [e for e in entities_seen if e != new_holder]
                if cands:
                    viol_actor = cands[rng.integers(0, len(cands))]
                    probes.append((gold_obj, t, viol_actor, 0))
        if is_named(th):
            recent_nominals.append(th)
        t += 1

    # score each probe: register decides MET iff holder_of(O, t) maps to the actor entity
    rows = []
    all_ents = sorted(entities_seen)
    for (O, te, actor, gold_met) in probes:
        blind_holder_ent = _ent_of_key(wb.holder_of("S::" + O, te))
        dens_holder_ent = _ent_of_key(wf.holder_of(O, te))
        gold_holder_ent = _ent_of_key(wg.holder_of(O, te))
        blind_met = int(blind_holder_ent == actor)
        dens_met = int(dens_holder_ent == actor)
        gold_dec = int(gold_holder_ent == actor)
        twin_actor = all_ents[rng.integers(0, len(all_ents))] if all_ents else actor
        twin_met = int(dens_holder_ent == twin_actor)   # densified holder vs a RANDOM actor (info-free label)
        rows.append({"gold_met": gold_met,
                     "blind": int(blind_met == gold_met), "dens": int(dens_met == gold_met),
                     "gold": int(gold_dec == gold_met), "twin": int(twin_met == gold_met),
                     "blind_met": blind_met, "dens_met": dens_met})
    return rows


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
        n_stories = 400
    sts = stories(n_stories)
    rng = np.random.default_rng(seed)
    rows = []
    for sents in sts:
        insts = story_transfers(sents, gen, lex, lemma_word)
        if insts:
            rows.extend(analyse(insts, rng))
    res = {"anchor": ANCHOR, "mode": mode, "n_stories": len(sts), "n_probes": len(rows),
           "chance_floor": 0.5, "base_rate_valid": round(float(np.mean([r["gold_met"] for r in rows])), 3) if rows else None}
    if rows:
        res["blind"] = boot([r["blind"] for r in rows], n_boot, seed + 1)
        res["densified"] = boot([r["dens"] for r in rows], n_boot, seed + 2)
        res["gold_sanity"] = boot([r["gold"] for r in rows], n_boot, seed + 3)
        res["twin_random_actor"] = boot([r["twin"] for r in rows], n_boot, seed + 4)
        d = np.asarray([r["dens"] - r["blind"] for r in rows], float)
        rng2 = np.random.default_rng(seed + 9)
        bs = [d[rng2.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
        res["densified_minus_blind"] = {"delta": round(float(d.mean()), 4),
                                        "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}
        res["densified_beats_blind_CIsep"] = bool(res["densified_minus_blind"]["ci"][0] > 0)
        valid = [r for r in rows if r["gold_met"] == 1]
        viol = [r for r in rows if r["gold_met"] == 0]
        res["n_valid"] = len(valid); res["n_violation"] = len(viol)
        res["blind_false_flag_rate_on_VALID"] = round(float(np.mean([1 - r["blind_met"] for r in valid])), 3) if valid else None
        res["densified_false_flag_rate_on_VALID"] = round(float(np.mean([1 - r["dens_met"] for r in valid])), 3) if valid else None
        res["blind_miss_rate_on_VIOLATION"] = round(float(np.mean([r["blind_met"] for r in viol])), 3) if viol else None
        res["densified_miss_rate_on_VIOLATION"] = round(float(np.mean([r["dens_met"] for r in viol])), 3) if viol else None
        # imbalance-robust: majority floor (always-'possible') + BALANCED accuracy (mean of per-class), chance 0.5.
        br = res["base_rate_valid"]
        res["majority_floor_always_possible"] = round(max(br, 1 - br), 3)
        def bal(key):
            va = np.mean([r[key + "_met"] == 1 for r in valid]) if valid else 0.0   # valid correctly MET
            vo = np.mean([r[key + "_met"] == 0 for r in viol]) if viol else 0.0      # violation correctly UNMET
            return round(float((va + vo) / 2), 4)
        res["balanced_acc_blind"] = bal("blind")
        res["balanced_acc_densified"] = bal("dens")
        res["balanced_chance"] = 0.5
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    # "I got the ball. I gave it to Sam." Probes at the give (t=1) about object 'ball':
    #   VALID actor=sam (current holder) -> MET ; VIOLATION actor=NARRATOR (gave it away) -> UNMET.
    # blind: object 'it' -> have('S::ball') stale=narrator; so it says narrator MET (wrong: misses violation) and
    #        sam UNMET (wrong: false-flags valid). densified: it->ball, holder=sam -> both correct.
    insts = [{"verb": "get", "op": "GET", "agent": "i", "theme": "ball", "arg2": None},
             {"verb": "give", "op": "GIVE", "agent": "i", "theme": "it", "arg2": "sam"}]
    rows = analyse(insts, np.random.default_rng(0))
    dens_ok = all(r["dens"] == 1 for r in rows) and len(rows) >= 2
    blind_bad = any(r["blind"] == 0 for r in rows)
    print("[self-test] densified detects both valid+violation: %s ; blind errs (lost 'it'->ball): %s" % (dens_ok, blind_bad), flush=True)
    print("[self-test] rows:", rows, flush=True)
    return 0 if (dens_ok and blind_bad) else 1


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
    print("\n  POWERED bridging / impossible-action detection (MCScript2, balanced, chance=0.5):", flush=True)
    if res["n_probes"]:
        print("  n=%d probes (%d valid / %d violation; base-rate valid=%.2f)"
              % (res["n_probes"], res["n_valid"], res["n_violation"], res["base_rate_valid"]), flush=True)
        print("  detection accuracy:  BLIND %.3f %s  ->  DENSIFIED %.3f %s   (delta %.3f %s CI-sep=%s)"
              % (res["blind"]["acc"], res["blind"]["ci"], res["densified"]["acc"], res["densified"]["ci"],
                 res["densified_minus_blind"]["delta"], res["densified_minus_blind"]["ci"], res["densified_beats_blind_CIsep"]), flush=True)
        print("  vs majority floor (always-possible) %.3f | gold(sanity) %.3f | twin(random-actor) %.3f"
              % (res["majority_floor_always_possible"], res["gold_sanity"]["acc"], res["twin_random_actor"]["acc"]), flush=True)
        print("  BALANCED acc (imbalance-robust, chance 0.5): BLIND %.3f -> DENSIFIED %.3f"
              % (res["balanced_acc_blind"], res["balanced_acc_densified"]), flush=True)
        print("  FALSE-flag on VALID:  blind %.3f -> dens %.3f  | MISS on VIOLATION: blind %.3f -> dens %.3f"
              % (res["blind_false_flag_rate_on_VALID"], res["densified_false_flag_rate_on_VALID"],
                 res["blind_miss_rate_on_VIOLATION"], res["densified_miss_rate_on_VIOLATION"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
