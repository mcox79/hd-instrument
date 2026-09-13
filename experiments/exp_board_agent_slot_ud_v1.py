"""exp_board_agent_slot_ud_v1 -- the who-did-what AGENT board arm on MODERN gold (UD-EWT), and the
first test of whether the brain-foundational Competition-Model AGENT role assigner GENERALIZES to the
modern register.

problem: rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval

WHY THIS CELL EXISTS (two jobs at once):
  1. THE BOARD DIMENSION. The 19c board's who-did-what arm (exp_situation_model_qa_v1.build_events_
     questions) scores AGENT on LitBank (banned). The already-modern PATIENT arm (exp_board_patient_
     slot_v1, clean UD-EWT gold) has no AGENT counterpart. This builds it: gold agent off GOLD deprels
     (nsubj [active] / obl:agent [passive]), the same clean-instrument recipe as the patient arm.
  2. THE UPSTREAM BRAIN-FOUNDATIONAL COMPONENT. The AGENT role assigner is a landed, owner-DONE
     Competition-Model organ (hdlab.graded_role_assigner.agent_competition_pick; Bates & MacWhinney;
     Centering; DuBois PAS -- all PINNED) proven on LitBank 19c (0.041->0.69). Its own SOLVED (section
     6b, point 4) flags the open question: "the cues are narrative-tuned; modern-prose transfer needs a
     weight re-sweep, NOT YET RUN through this path." This cell runs it: does the pinned narrative
     Competition-Model AGENT assigner EXCEED the positional floor on MODERN text, and do the pinned cue
     validities generalize (or does modern need a re-sweep -- brain-faithful register-specificity)?

HOW THE BRAIN DOES THIS (opening move):
  PINNED (copy the computation): GRADED, PARALLEL cue competition -- the Competition Model (Bates &
    MacWhinney 1989), constraint satisfaction (MacDonald 1994), cue-based retrieval (Lewis & Vasishth
    2005). Additive cue activation A_i = sum_c w_c*support_c(i) -> argmax IS the Bayesian posterior
    (McClelland 2013). Cues: word-order (English-dominant), core-argument (PP-government), animacy
    (agent->animate), voice (passive flips to the by-phrase), clause-locality, case (nominative pronoun).
  OUR-INVENTION-UNDER-TEST (swept, not adopted): the validity-seeded weights AGENT_VALIDITIES (a static
    asset, hand-set from cue validity, NOT trained). This cell SWEEPS them on a dev split.
  NOT brain-faithful (the FLOOR): agent = the nearest PRE-verbal nominal (pure word-order position),
    the deployed positional proxy that collapses on passives / PP-fronting; an external LLM.

Glass-box, NO external LLM. Reuses hdlab.graded_role_assigner (owner-DONE) + hdlab.pos_tagger +
experiments.exp_whodidwhat_ud_structural_v1.load_ud verbatim. Clean UD gold (admissible foundation).
Reads only toks/pos + the animacy lexicon + gazetteer -- no gold at inference. ASCII. own dir.

Run: .venv/Scripts/python.exe experiments/exp_board_agent_slot_ud_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_board_agent_slot_ud_v1.py --run [--cap N] [--sweep]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from hdlab.pos_tagger import PosTagger
import hdlab.graded_role_assigner as GRA
from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT_DIR = str(get_output_dir("board_agent_slot_ud_v1"))
ANCHOR = "board_agent_slot_ud_v1"
NOMINAL = {"NOUN", "PROPN", "PRON"}
SEED = 20260906


def gold_agent_items(sents):
    """Yield (toks, verb_id(1-based), gold_agent_id(1-based), is_passive) for every verb with a
    recoverable core AGENT off GOLD deprels: active -> nsubj (the subject/agent); passive -> obl:agent
    (the by-phrase). Agentless passives (no obl:agent) are SKIPPED (no agent to recover). Mirrors the
    patient arm's gold recipe (obj [active] / nsubj:pass [passive]), for the complementary role."""
    out = []
    for s in sents:
        toks = [t["form"] for t in s]
        for t in s:
            if t["upos"] != "VERB":
                continue
            v = t["id"]
            deps = [d for d in s if d["head"] == v]
            passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
            ag = None
            if passive:
                for d in deps:
                    if d["deprel"].startswith("obl:agent"):     # the explicit by-phrase agent
                        ag = d["id"]; break
            else:
                for d in deps:
                    if d["dep"] == "nsubj" and not d["deprel"].startswith("nsubj:pass"):
                        ag = d["id"]; break
            if ag is not None:
                out.append((toks, v, ag, passive))
    return out


def _clause_local_nominals(toks, up, v):
    """Candidate mention dicts = the NOMINAL tokens inside the verb's clause span (brain-foundational
    clause-bounded role assignment; GRA.clause_bounds). v is 1-based; returns dicts in GRA's schema."""
    left, right = GRA.clause_bounds(toks, up, v - 1)              # 0-based span [left, right)
    cands = []
    for i in range(left, right):
        if i < len(up) and up[i] in NOMINAL:
            cands.append({"wtok_start": i, "head": toks[i], "cluster": None, "wtok_end": i})
    return cands


def _floor_positional_idx(v, cands):
    """The nearest PRE-verbal nominal candidate INDEX (0-based); else nearest post-verbal; else None."""
    pre = [c for c in cands if c["wtok_start"] < v - 1]
    if pre:
        return max(pre, key=lambda c: c["wtok_start"])["wtok_start"]
    post = [c for c in cands if c["wtok_start"] > v - 1]
    return min(post, key=lambda c: c["wtok_start"])["wtok_start"] if post else None


def floor_positional_agent(toks, up, v, cands):
    """POSITIONAL FLOOR (the deployed proxy): the nearest PRE-verbal nominal (word-order-only). This is
    the agent default that collapses on passives (grabs the surface subject = patient) and on PP-fronting
    (grabs a preposition-governed noun). Returns a head string or None."""
    i = _floor_positional_idx(v, cands)
    return toks[i] if i is not None else None


def hybrid_agent_pick(toks, up, v, cands, cm_cands, gaz, weights=None):
    """THE DEPLOYABLE brain-foundational AGENT route -- the AGENT counterpart to hdlab.graded_role_assigner.
    hybrid_role_patient, and the register-general fix for modern prose. Keep the POSITIONAL pick (nearest
    preverbal nominal = the high-validity word-order cue, which DOMINATES in canonical English) BYTE-IDENTICAL
    on canonical clauses, and invoke the Competition-Model competition ONLY when a MARKED override cue fires:
      (1) PASSIVE clause  -> the surface subject is the patient; the agent is the by-phrase (voice cue);
      (2) the positional pick is PP-GOVERNED ('In [the morning], X ran' -> morning; core_arg cue rejects it);
      (3) the positional pick is a NON-NOMINATIVE pronoun (case cue: him/her/them cannot be the subject).
    On modern canonical prose word-order already wins (position ~0.86), so a FULL competition that always
    overrides HURTS (19c-tuned secondary cues mis-fire); this preserves position AND fixes its specific
    failure modes. Returns a head string."""
    base_i = _floor_positional_idx(v, cands)
    base = toks[base_i] if base_i is not None else None
    from hdlab.thematic_role_labeler import is_passive_clause
    low_base = str(base).lower() if base is not None else ""
    passive = is_passive_clause(toks, up)
    pp_gov = base_i is not None and GRA._agent_pp_governed([t.lower() for t in toks], up, base_i)
    noncase = low_base in GRA._AGENT_ANIM_PRON and low_base not in GRA.NOMINATIVE_PRON
    if passive or pp_gov or noncase:
        return GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None,
                                          weights=weights, gaz=gaz)
    return base                                                  # canonical: word-order default (== positional)


def _match(pred_head, gold_head):
    return pred_head is not None and str(pred_head).lower() == str(gold_head).lower()


def _eval(items, tagger, gaz, weights=None, case_filter=True):
    """Score FLOOR_positional / CM_agent (full competition) / HYBRID (override-only) / TWIN per item, split
    active/passive, clustered by sentence for the bootstrap. per-cluster = [n, floor, cm, hybrid, twin]."""
    per = {}
    tally = {"active": {"n": 0, "floor": 0, "cm": 0, "hybrid": 0},
             "passive": {"n": 0, "floor": 0, "cm": 0, "hybrid": 0}}
    for si, (toks, v, ag, passive) in enumerate(items):
        up = tagger.tag(list(toks))
        cands = _clause_local_nominals(toks, up, v)
        if not cands:
            continue
        if case_filter:                                          # CASE cue: drop non-nominative pronoun cands
            cf = [c for c in cands if str(c["head"]).lower() not in GRA._AGENT_ANIM_PRON
                  or str(c["head"]).lower() in GRA.NOMINATIVE_PRON]
            cm_cands = cf or cands
        else:
            cm_cands = cands
        gold = toks[ag - 1]
        floor = floor_positional_agent(toks, up, v, cands)
        cm = GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None,
                                        weights=weights, gaz=gaz)
        hyb = hybrid_agent_pick(toks, up, v, cands, cm_cands, gaz, weights=weights)
        twin = GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None,
                                          weights=weights, gaz=gaz, twin_seed=SEED)
        f_ok, c_ok, h_ok, t_ok = (int(_match(floor, gold)), int(_match(cm, gold)),
                                  int(_match(hyb, gold)), int(_match(twin, gold)))
        key = id(toks)
        d = per.setdefault(key, [0, 0, 0, 0, 0])
        d[0] += 1; d[1] += f_ok; d[2] += c_ok; d[3] += h_ok; d[4] += t_ok
        sl = "passive" if passive else "active"
        tally[sl]["n"] += 1; tally[sl]["floor"] += f_ok; tally[sl]["cm"] += c_ok; tally[sl]["hybrid"] += h_ok
    return per, tally


def _paired_boot(per, ia, ib, n_boot=2000, seed=SEED):
    """Paired sentence-cluster bootstrap of rate(ia) - rate(ib). Returns [obs, lo, hi, hw, ci_sep]."""
    keys = list(per.keys())
    N = np.array([per[k][0] for k in keys], float)
    A = np.array([per[k][ia] for k in keys], float)
    B = np.array([per[k][ib] for k in keys], float)
    tot = N.sum()
    obs = (A.sum() - B.sum()) / max(tot, 1)
    rng = np.random.default_rng(seed)
    n = len(keys)
    ds = np.empty(n_boot)
    for b in range(n_boot):
        s = rng.integers(0, n, n)
        nn = N[s].sum()
        ds[b] = (A[s].sum() - B[s].sum()) / max(nn, 1e-9)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return [round(float(obs), 4), round(float(lo), 4), round(float(hi), 4),
            round(float((hi - lo) / 2), 4), bool(lo > 0)]


def _rate(per, i):
    tot = sum(d[0] for d in per.values())
    return round(sum(d[i] for d in per.values()) / max(1, tot), 4)


def sweep_weights(dev_items, tagger, gaz, n_boot=800):
    """Modern cue-validity RE-SWEEP (the SOLVED 6b open question). Grid over a few brain-plausible weight
    configs on the DEV split; return each config's dev accuracy. The PINNED narrative AGENT_VALIDITIES is
    config 'pinned'. We do NOT adopt a config here -- we report whether the pinned weights already
    generalize to modern (they should: word-order/animacy/voice validities are register-general)."""
    P = dict(GRA.AGENT_VALIDITIES)
    configs = {
        "pinned": P,
        "order_up": {**P, "preverbal": 4.0},
        "order_down": {**P, "preverbal": 2.0},
        "animacy_up": {**P, "animacy": 3.5},
        "core_up": {**P, "core_arg": 3.0},
        "byagent_up": {**P, "byagent": 8.0},
        "flat": {k: 1.0 for k in P},                 # info-poor: equal weights (near-positional)
    }
    out = {}
    for name, w in configs.items():
        per, _t = _eval(dev_items, tagger, gaz, weights=w)
        out[name] = _rate(per, 2)
    return out


def board_agent_dimension(cap=None, n_boot=2000, seed=SEED):
    """The per_dimension-shaped 'agent' (who-did-what) row for the modern board (schema-matched to
    board_patient_dimension) + full detail. model = CM agent competition; floor = positional; twin =
    shuffled supports; on CLEAN UD-EWT gold agents (nsubj active / obl:agent passive)."""
    from hdlab import frontend as _FE   # ONE shared frontend (2026-09-12): the category organ switch reaches this arm
    tagger = _FE.tagger()
    gaz = load_given_gazetteer()
    sents = load_ud(UD_TEST)
    if cap:
        sents = sents[:cap]
    items = gold_agent_items(sents)
    per, tally = _eval(items, tagger, gaz)
    n = sum(d[0] for d in per.values())
    # MODEL = the deployable HYBRID (override-only) agent -- the brain-foundational route that keeps the
    # high-validity word-order default on canonical clauses and overrides only on marked cues. cm (full
    # competition) + floor (positional) are reported alongside.
    hy, cm, fl, tw = _rate(per, 3), _rate(per, 2), _rate(per, 1), _rate(per, 4)
    ms = _paired_boot(per, 3, 1, n_boot, seed)     # hybrid - floor  (the headline)
    mt = _paired_boot(per, 3, 4, n_boot, seed)     # hybrid - twin
    cmf = _paired_boot(per, 2, 1, n_boot, seed)    # cm(full) - floor (the register located finding)

    def sub(sl):
        t = tally[sl]
        return {"n": t["n"], "floor": round(t["floor"] / max(1, t["n"]), 4),
                "cm": round(t["cm"] / max(1, t["n"]), 4),
                "hybrid": round(t["hybrid"] / max(1, t["n"]), 4)}
    row = {
        "n": n, "model_acc": hy,
        "overlap_floor": fl,
        "floor_accs": {"positional_nearest_preverbal": fl},
        "strongest_floor_name": "positional_nearest_preverbal",
        "strongest_floor": fl,
        "twin_acc": tw,
        "model_minus_strongest": [ms[0], ms[1], ms[2]],
        "model_minus_twin": [mt[0], mt[1], mt[2]],
        "ci_sep_over_strongest": ms[4],
        "ci_sep_over_twin": mt[4],
        "population": "clean UD-EWT test who-did-what AGENT (gold nsubj [active] / obl:agent [passive] off "
                      "GOLD deprels); model = HYBRID override-only agent (word-order default + marked-cue "
                      "override), floor = positional. The 19c board scored AGENT on banned LitBank; this is "
                      "the modern who-did-what agent dimension.",
    }
    detail = {
        "n": n, "model_hybrid_agent": hy, "full_cm_agent": cm, "floor_positional": fl,
        "twin_shuffled_supports": tw,
        "hybrid_minus_floor": ms, "hybrid_minus_twin": mt, "full_cm_minus_floor": cmf,
        "by_voice": {"active": sub("active"), "passive": sub("passive")},
        "note": "AGENT who-did-what board arm on MODERN UD-EWT. HYBRID = the deployable brain-foundational route "
                "(hybrid_role_patient design: word-order default byte-identical on canonical clauses, "
                "Competition-Model override ONLY on passive / PP-fronting / non-nominative-case). full_cm = the "
                "always-compete 19c-tuned assigner (LOCATED NEGATIVE on modern: full_cm < positional, because "
                "modern prose is canonical and word-order already dominates -- the CM model's own register "
                "prediction). Reuses hdlab.graded_role_assigner (owner-DONE, Bates-MacWhinney/Centering PINNED).",
    }
    return row, detail


def run(cap=None, n_boot=2000, do_sweep=True, seed=SEED):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab import frontend as _FE   # ONE shared frontend (2026-09-12): the category organ switch reaches this arm
    tagger = _FE.tagger()
    gaz = load_given_gazetteer()
    sents = load_ud(UD_TEST)
    if cap:
        sents = sents[:cap]
    # dev/test split by sentence parity (the re-sweep is honest: tune on dev, report on test)
    dev = [s for i, s in enumerate(sents) if i % 2 == 0]
    test = [s for i, s in enumerate(sents) if i % 2 == 1]
    dev_items, test_items = gold_agent_items(dev), gold_agent_items(test)

    row, detail = board_agent_dimension(cap=cap, n_boot=n_boot, seed=seed)   # headline on FULL split
    res = {"anchor": ANCHOR, "seed": seed, "row": row, "detail": detail}

    if do_sweep:
        dev_sweep = sweep_weights(dev_items, tagger, gaz)
        best_cfg = max((k for k in dev_sweep if k != "pinned"), key=lambda k: dev_sweep[k])
        # evaluate PINNED vs the dev-best config on the held-out TEST split
        per_pin, _ = _eval(test_items, tagger, gaz, weights=GRA.AGENT_VALIDITIES)
        P = dict(GRA.AGENT_VALIDITIES)
        cfg_map = {"order_up": {**P, "preverbal": 4.0}, "order_down": {**P, "preverbal": 2.0},
                   "animacy_up": {**P, "animacy": 3.5}, "core_up": {**P, "core_arg": 3.0},
                   "byagent_up": {**P, "byagent": 8.0}, "flat": {k: 1.0 for k in P}}
        per_best, _ = _eval(test_items, tagger, gaz, weights=cfg_map[best_cfg])
        per_floor, _ = _eval(test_items, tagger, gaz)
        res["resweep"] = {
            "dev_accuracy_by_config": dev_sweep,
            "dev_best_nonpinned": best_cfg,
            "test_pinned_cm": _rate(per_pin, 2),
            "test_dev_best_cm": _rate(per_best, 2),
            "test_positional_floor": _rate(per_floor, 1),
            "pinned_generalizes": bool(_rate(per_pin, 2) >= _rate(per_floor, 1)),
            "resweep_beats_pinned_on_test": bool(_rate(per_best, 2) > _rate(per_pin, 2)),
            "note": "Does the PINNED narrative Competition-Model AGENT assigner generalize to modern UD-EWT? "
                    "Tune weights on DEV, report on held-out TEST. If test_pinned_cm >= floor and "
                    "resweep does not beat pinned, the narrative cue validities are register-GENERAL "
                    "(word-order/animacy/voice) -- the brain-foundational prediction.",
        }
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2, default=str)
    return res


def _print(res):
    r, d = res["row"], res["detail"]
    print("=" * 96)
    print("WHO-DID-WHAT AGENT board arm on MODERN UD-EWT  n=%d" % r["n"])
    print("  model_acc (HYBRID override-only)   : %.4f" % (r["model_acc"] or 0))
    print("  full CM agent (always-compete)     : %.4f" % (d["full_cm_agent"] or 0))
    print("  strongest_floor (positional)      : %.4f" % (r["strongest_floor"] or 0))
    print("  twin (shuffled supports, info-free): %.4f" % (r["twin_acc"] or 0))
    print("  HYBRID - floor : %s  ci_sep=%s" % (r["model_minus_strongest"], r["ci_sep_over_strongest"]))
    print("  full_CM - floor: %s  (located: modern is canonical -> word-order wins)" % (d["full_cm_minus_floor"]))
    print("  HYBRID - twin  : %s  ci_sep=%s" % (r["model_minus_twin"], r["ci_sep_over_twin"]))
    bv = d["by_voice"]
    print("  by voice: active(n=%d) floor %.3f cm %.3f hyb %.3f | passive(n=%d) floor %.3f cm %.3f hyb %.3f" % (
        bv["active"]["n"], bv["active"]["floor"], bv["active"]["cm"], bv["active"]["hybrid"],
        bv["passive"]["n"], bv["passive"]["floor"], bv["passive"]["cm"], bv["passive"]["hybrid"]))
    if "resweep" in res:
        rs = res["resweep"]
        print("  --- modern cue-validity RE-SWEEP (dev-tune, held-out test) ---")
        print("  dev accuracy by config: %s" % rs["dev_accuracy_by_config"])
        print("  TEST: pinned CM %.4f | dev-best(%s) CM %.4f | positional floor %.4f" % (
            rs["test_pinned_cm"], rs["dev_best_nonpinned"], rs["test_dev_best_cm"], rs["test_positional_floor"]))
        print("  pinned generalizes to modern = %s ; resweep beats pinned = %s" % (
            rs["pinned_generalizes"], rs["resweep_beats_pinned_on_test"]))
    print("=" * 96)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cap", type=int, default=None)
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    if a.self_test:
        res = run(cap=400, n_boot=300, do_sweep=True)
        r = res["row"]
        assert r["n"] > 30, r
        assert r["model_acc"] is not None and r["strongest_floor"] is not None, r
        assert res["detail"]["by_voice"]["passive"]["n"] >= 1, res["detail"]
        _print(res)
        print("\n[self-test] PASS")
        return
    res = run(cap=a.cap, n_boot=a.n_boot, do_sweep=(a.sweep or True))
    _print(res)
    print("\nwrote %s" % os.path.relpath(os.path.join(OUT_DIR, "metrics.json"), _REPO))


if __name__ == "__main__":
    main()
