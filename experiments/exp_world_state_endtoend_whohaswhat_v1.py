"""exp_world_state_endtoend_whohaswhat_v1 -- the END-TO-END who-has-what test through the FULL EntityBinder
(all Stage-1 routes at once) vs the coref-BLIND register, on real MCScript2 first-person narrative, with
DETERMINISTIC (non-circular) gold. This is the "does the whole thing work" number the SOLVED submission was
missing (the routes had been proven separately on different metrics/corpora).

DETERMINISTIC GOLD (no hand-annotation, non-circular vs blind): for a NOMINAL object O transferred in a
first-person story, the gold holder after each event is FORCED where unambiguous:
  * holder is 1st-person singular (I/me/my) -> the NARRATOR entity (Kaplan indexical; deterministic).
  * holder is a NAMED nominal -> that name.
  * holder is he/she/it/we/you -> UNDETERMINED (needs coref we cannot gold on MCScript2) -> EXCLUDE those Qs.
  * object reference "it" -> O only when O is the UNIQUE recent nominal theme (exactly one candidate in the last
    K events); ambiguous -> EXCLUDE. (So it->O is FORCED, not the binder's choice -> non-circular: blind keys the
    transfer on "it" and leaves have(O) stale; any resolver must pick O; gold is O.)

ARMS (who-has-what over the gold Qs; correct = holder entity == gold entity):
  blind         : raw-string keys (the register wired today). Fails on 'it' (object fragmentation) AND on
                  first-person (its "i"/"me" is not the NARRATOR entity).
  blind+idx     : blind GRANTED the free indexical normalization (i/me/my->NARRATOR) -> isolates the OBJECT-anaphora
                  contribution from the cheap indexical one.
  full_binder   : the deliverable EntityBinder (indexical + object anaphora + nominal).
  gold          : deterministic keys -> 1.000 by construction (sanity).
  twin (NULL)   : full_binder but object 'it' -> a RANDOM recent nominal (wrong object) -> CORRECT object resolution
                  must do the work (K-perm mean + p95).
CONTROLS: change-point (holder of O CHANGES at the transferring event); gold==1.0; twin loses. Glass-box; the
routes come from experiments/world_state_entity_binding.EntityBinder; NO spaCy/LLM. ASCII only.
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
from collections import Counter

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_world_state_deixis_object_v1 import stories, story_transfers
from experiments.world_state_entity_binding import EntityBinder, NARRATOR, FIRST_SG, OBJ_PRON

ANCHOR = "world_state_endtoend_whohaswhat_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
K_RECENT = 3          # 'it' is gold-unambiguous only if ONE distinct nominal theme in the last K transfer events
PERSON = {"he", "she", "him", "her", "his", "it", "them", "they", "we", "us", "you", "your"}


def is_named(h):
    return h is not None and h not in FIRST_SG and h not in OBJ_PRON and h not in PERSON


def gold_holder_entity(h):
    """deterministic holder entity, or None if UNDETERMINED (he/she/it/we/you)."""
    if h in FIRST_SG:
        return NARRATOR
    if is_named(h):
        return h
    return None


def analyse_story(insts, rng):
    from hdlab.world_state_register import WorldState
    wb, wi, wf, wg = WorldState(), WorldState(), WorldState(), WorldState()   # blind, blind+idx, full, gold
    binder = EntityBinder()
    recent_nominal_themes = []            # ordered distinct nominal theme heads (for gold 'it' disambiguation)
    # twin: full binder but object 'it' -> random recent nominal
    wt = WorldState()
    twin_binder_state = []                # track recent nominals for the twin
    idx_only = lambda h: (NARRATOR if h in FIRST_SG else h)
    rows = []
    per_obj_events = {}                   # nominal O -> list of (t, gold_entity, changed) for its Qs

    t = 0
    for it in insts:
        ag, th, a2, op, vb = it["agent"], it["theme"], it["arg2"], it["op"], it["verb"]
        # holder-after MATCHES the register's operator semantics: GIVE -> recipient (obj leaves giver);
        # GET -> agent; GIVE-without-recipient / LOSE -> holder undetermined (obj leaves) -> no Q.
        holder = a2 if op == "GIVE" else (ag if op == "GET" else None)
        # ---- object resolution per arm ----
        # gold object: it -> unique recent nominal (else undetermined for scoring); nominal -> itself
        th_is_obj_pron = th in OBJ_PRON
        recent_window = recent_nominal_themes[-K_RECENT:]
        uniq_recent = list(dict.fromkeys(recent_window))
        gold_obj = None
        if th_is_obj_pron:
            gold_obj = uniq_recent[-1] if len(uniq_recent) == 1 else None   # FORCED only if unique
        elif is_named(th):
            gold_obj = th
        # full binder object
        fb_obj, _r = binder.bind_theme(th, vb)
        # twin object: it -> random recent nominal
        tw_obj = th
        if th_is_obj_pron and recent_nominal_themes:
            tw_obj = recent_nominal_themes[rng.integers(0, len(recent_nominal_themes))]
        elif is_named(th):
            tw_obj = th
        # ---- apply events per arm ----
        wb.apply_event({"PRED": vb, "OP": op, "AGENT": ag, "PATIENT": th, "ARG2": a2}, t, read_preconditions=False)
        wi.apply_event({"PRED": vb, "OP": op, "AGENT": idx_only(ag), "PATIENT": th, "ARG2": idx_only(a2)}, t, read_preconditions=False)
        fb_h = (NARRATOR if holder in FIRST_SG else (holder if is_named(holder) else None))
        wf.apply_event({"PRED": vb, "OP": op, "AGENT": (NARRATOR if ag in FIRST_SG else ag),
                        "PATIENT": fb_obj, "ARG2": (NARRATOR if a2 in FIRST_SG else a2)}, t, read_preconditions=False)
        wt.apply_event({"PRED": vb, "OP": op, "AGENT": (NARRATOR if ag in FIRST_SG else ag),
                        "PATIENT": tw_obj, "ARG2": (NARRATOR if a2 in FIRST_SG else a2)}, t, read_preconditions=False)
        gh = gold_holder_entity(holder) if holder is not None else None
        g_ag = gold_holder_entity(ag)
        wg.apply_event({"PRED": vb, "OP": op, "AGENT": (g_ag if g_ag else "??%d" % t),
                        "PATIENT": (gold_obj if gold_obj else th),
                        "ARG2": (gold_holder_entity(a2) if a2 else None) or ("??%d" % t if a2 else None)},
                       t, read_preconditions=False)
        # ---- generate a Q if the gold holder + gold object are DETERMINED and object is a real thing ----
        if gold_obj is not None and gh is not None:
            prev = wg.holder_of(gold_obj, t - 1) if t > 0 else None
            per_obj_events.setdefault(gold_obj, []).append((t, gh, int(prev != gh)))
        # advance recent nominal themes
        if is_named(th):
            recent_nominal_themes.append(th)
        t += 1

    # score each determined Q
    def ent_of(key):
        if key is None:
            return None
        return key   # keys ARE entity strings (NARRATOR / name / raw pronoun / object head)

    for O, evs in per_obj_events.items():
        for (te, gold_ent, changed) in evs:
            rows.append({
                "blind": int(ent_of(wb.holder_of(O, te)) == gold_ent),
                "blind_idx": int(ent_of(wi.holder_of(O, te)) == gold_ent),
                "full": int(ent_of(wf.holder_of(O, te)) == gold_ent),
                "gold": int(ent_of(wg.holder_of(O, te)) == gold_ent),
                "twin": int(ent_of(wt.holder_of(O, te)) == gold_ent),
                "changed": changed,
            })
    return rows


def boot(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return {"acc": None, "ci": [None, None], "n": 0, "half": None}
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return {"acc": round(float(vals.mean()), 4), "ci": [round(lo, 4), round(hi, 4)], "n": len(vals),
            "half": round((hi - lo) / 2, 4)}


def paired(rows, a, b, n_boot, seed):
    d = np.asarray([r[a] - r[b] for r in rows], float)
    rng = np.random.default_rng(seed)
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    return {"delta": round(float(d.mean()), 4), "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}


def run(mode="full", n_stories=3000, n_boot=2000, seed=20260902):
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.thematic_role_labeler import lemma_word
    from experiments.possession_operators import build_lexicon
    gen = CandidateGenerator.load(os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"),
                                  os.path.join(REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz"))
    lex = build_lexicon(use_cache=True)
    if mode == "smoke":
        n_stories = 200
    sts = stories(n_stories)
    rng = np.random.default_rng(seed)
    rows = []
    for sents in sts:
        insts = story_transfers(sents, gen, lex, lemma_word)
        if insts:
            rows.extend(analyse_story(insts, rng))
    res = {"anchor": ANCHOR, "mode": mode, "n_stories": len(sts), "n_questions": len(rows)}
    if rows:
        for a in ("blind", "blind_idx", "full", "gold", "twin"):
            res[a] = boot([r[a] for r in rows], n_boot, seed + hash(a) % 500)
        res["full_minus_blind"] = paired(rows, "full", "blind", n_boot, seed + 11)
        res["full_minus_blindidx"] = paired(rows, "full", "blind_idx", n_boot, seed + 12)   # object-anaphora only
        res["full_minus_twin"] = paired(rows, "full", "twin", n_boot, seed + 13)
        res["changed_frac"] = round(float(np.mean([r["changed"] for r in rows])), 3)
        res["full_beats_blind_CIsep"] = bool(res["full_minus_blind"]["ci"][0] > 0)
        res["full_beats_twin_CIsep"] = bool(res["full_minus_twin"]["ci"][0] > 0)
        res["objanaph_beats_blindidx_CIsep"] = bool(res["full_minus_blindidx"]["ci"][0] > 0)
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    from hdlab.world_state_register import WorldState
    # "I grabbed the cup. I gave it to the waiter." Q: who has cup after event 1? gold=waiter.
    insts = [{"verb": "grab", "op": "GET", "agent": "i", "theme": "cup", "arg2": None},
             {"verb": "give", "op": "GIVE", "agent": "i", "theme": "it", "arg2": "waiter"}]
    import numpy as _np
    rows = analyse_story(insts, _np.random.default_rng(0))
    # the Q at t=1 for object 'cup': blind stale (=narrator via idx? no, blind raw agent 'i' -> 'i'), full=waiter.
    q = [r for r in rows]
    ok = any(r["full"] == 1 and r["blind"] == 0 for r in q)
    print("[self-test] end-to-end: full correct where blind fails (it->cup relocation): %s ; n_q=%d" % (ok, len(q)), flush=True)
    print("[self-test] rows:", q, flush=True)
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
    if res["n_questions"]:
        print("\n  END-TO-END who-has-what (MCScript2, deterministic gold), n=%d Qs over %d stories:" % (res["n_questions"], res["n_stories"]), flush=True)
        for a in ("blind", "blind_idx", "full", "twin", "gold"):
            print("  %-10s %.3f %s" % (a, res[a]["acc"], res[a]["ci"]), flush=True)
        print("  full-blind %.3f %s (CI-sep %s)  | full-blindidx (OBJECT anaphora only) %.3f %s (CI-sep %s)"
              % (res["full_minus_blind"]["delta"], res["full_minus_blind"]["ci"], res["full_beats_blind_CIsep"],
                 res["full_minus_blindidx"]["delta"], res["full_minus_blindidx"]["ci"], res["objanaph_beats_blindidx_CIsep"]), flush=True)
        print("  full-twin %.3f %s (CI-sep %s) | change-point %.3f"
              % (res["full_minus_twin"]["delta"], res["full_minus_twin"]["ci"], res["full_beats_twin_CIsep"], res["changed_frac"]), flush=True)
    else:
        print("  NO QUESTIONS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
