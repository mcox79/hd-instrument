"""exp_situation_model_state_qa_v1 -- WIRE the copular is-a/attribute capability into a LIVE QA CONSUMER.

THE PROBLEM (wire_the_copular_state_qa_consumer_and_turn_on_bind_entity_states): the reader has a landed but
default-OFF copular capability (`bind_entity_states` -> sm.entity_states + sm.state_register) with NO live
consumer and NO board metric, so it scores a live 0 on "what/who is X" and cannot be turned on under the
no-default-off rule. This cell is the CONSUMER's powered, NON-CIRCULAR measurement: a "state" QA dimension that
ASKS "what/who is X" / "is X a Y" and ANSWERS OFF sm.state_register (never re-reading), routed by the
brain-faithful copular-frame router landed in exp_situation_model_qa_v1, and PROVES it recovers the
is-a/attribute fact CI-separated over the copular problem's VALIDATED most-recent-noun floor (0.503) with the
SHUFFLE-holder twin (0.452) LOSING -- so the flag is net-positive on a consumed metric and turns ON.

HOW THE BRAIN DOES THIS (opening move):
  PINNED (the computation): a copular predication ("Ahab is the captain", "the room is cold") updates the
    referent's ATTRIBUTE binding (Higgins 1979 predicational; Maienborn 2005 Kimian state; Bemis & Pylkkanen 2011
    LATL property attribution), later QUERIED from the discourse/situation model ("what was he?") WITHOUT
    re-reading (Zwaan & Radvansky 1998 situation model; Glenberg 1987 mental-model read-out). A "what/who is X"
    question SELECTS the entity-state dimension (content-addressable retrieval; Lewis & Vasishth 2005). We COPY
    that computation: route a copular question to the state register and read the answer off it.
  OUR-INVENTION-UNDER-TEST (swept, not adopted): the surface copular-frame ROUTER (glass-box), the question
    templates, the abstain policy. The DISCRETE state register (holder -> {values}) is the producer's
    OUR-INVENTION primitive; here we only CONSUME it.
  NOT brain-faithful (the FLOORS): guessing the property by POSITION (most-recent-noun) or a SHUFFLED holder;
    an external LLM. The floor/twin are the copular problem's VALIDATED ones, reused verbatim.

NON-CIRCULARITY (the decisive design choice): the GOLD is the copular problem's INDEPENDENT UD-EWT typed gold
  (from GOLD deprels -- COP.typed_gold), NOT the reader's own extraction; the MODEL answer goes through the
  LIVE reader (bind_entity_states=True) -> route -> sm.state_register.state_at readout. The reader can MISS a
  gold clause (detection recall), so model_acc < 1. On LitBank there is NO independent copular gold (no gold
  deprels), so a LitBank "state gold" would collide with the positional floor (circular) -- hence the powered,
  honest instrument is the UD-EWT gold. Population = PREDICATIONAL clauses (pred_adj + pred_nom): only these are
  applied to the state register (identity -> coref-merge is a separate filed follow-on).

REUSES (does not reinvent): COP.typed_gold / positional_floor / shuffle_twin / binding_readback / load_ud /
  UD_TEST (owner-DONE exp_copular_is_a_binding_readout_v1); QA.route / wh_ontology_route / SituationQA / _norm
  (the router landed in exp_situation_model_qa_v1). GLASS-BOX, NO external LLM at inference.

Run: .venv/Scripts/python.exe experiments/exp_situation_model_state_qa_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_situation_model_state_qa_v1.py --run [--cap N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_copular_is_a_binding_readout_v1 as COP     # validated gold / floor / twin (owner-DONE)
import experiments.exp_situation_model_qa_v1 as QA                # the router + SituationQA (this problem's wire)
import experiments._copular_nominal_events as M
from hdlab.situation_reader import SituationReader, SituationModel
from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser
from hdlab.arc_labeler import ArcLabeler

ANCHOR = "situation_model_state_qa_v1"
OUT_DIR = os.path.join(REPO, "data", ANCHOR)
SEED = 20260903
PREDICATIONAL = ("pred_adj", "pred_nom")   # applied to the state register (identity -> coref-merge follow-on)


def _state_q(holder: str) -> str:
    return f"What is {holder} ?"


def _yesno_q(holder: str, prop: str) -> str:
    return f"Is {holder} a {prop} ?"


def _register_from_pairs(pairs, toks, up):
    """Build a state register from (holder_idx, property_idx) pairs exactly as the reader's _read_entity_states
    does (predicational -> apply_state on the holder surface token). Lets an UPSTREAM binding variant (the fix)
    flow through the SAME consumer read-out."""
    from hdlab.state_register import StateRegister
    from hdlab.copular_binding import predicted_type
    reg = StateRegister()
    for (h, p) in pairs:
        if not (0 <= h < len(toks) and 0 <= p < len(toks)):
            continue
        if predicted_type(toks, up, h, p) in PREDICATIONAL:
            reg.apply_state(toks[h].lower(), toks[p].lower())
    return reg


def _state_match(ans, gold_prop: str) -> bool:
    """MODEL answer is a set/str of state values (or None). MATCH iff the gold property token is recovered
    (content-token overlap, mirroring QA._match)."""
    if ans is None:
        return False
    vals = {str(x).lower() for x in ans} if isinstance(ans, (set, list, tuple)) else {str(ans).lower()}
    g = QA._norm(gold_prop)
    return any(g == QA._norm(v) or g in QA._norm(v).split() or QA._norm(v) in g.split() for v in vals)


def run(cap: Optional[int] = None, n_boot: int = 2000, seed: int = SEED) -> dict:
    """Per PREDICATIONAL gold clause: MODEL (route 'what is X' -> state dim -> state_register.state_at readout)
    vs FLOOR (most-recent-noun) vs SHUFFLE-holder TWIN, plus the base-reader-OFF live zero, the router ABLATION
    (frame disabled -> misroutes), and the yes/no 'Is X a Y?' arm. Bootstrap over sentence-docs."""
    t0 = time.time()
    pos = PosTagger.load(M._POS_ASSET)
    arc = ArcParser.load(M._ARC_ASSET)
    lab = ArcLabeler.load(M._LAB_ASSET)
    sents = COP.load_ud(COP.UD_TEST, cap=cap)
    rng = np.random.default_rng(seed)
    reader = SituationReader.all_capabilities_off(gaz={}, bind_entity_states=True)

    KEYS = ("g", "model", "floor", "twin", "ablate", "off", "yn_g", "yn", "bind", "rb_given_bind",
            "fix", "fix_twin", "fix_bind")
    per: List[dict] = []
    per_type_g = defaultdict(int); per_type_ok = defaultdict(int); per_type_fix = defaultdict(int)
    n_hit = n_onto = n_tot = 0
    for sent in sents:
        toks = [r[1] for r in sent]
        up = pos.tag(toks)
        gold = [(h, p, t) for (h, p, t) in COP.typed_gold(sent) if t in PREDICATIONAL]
        if not gold:
            continue
        bind = COP.binding_readback(toks, up, arc, lab)
        floor = COP.positional_floor(toks, up)
        twin = COP.shuffle_twin(toks, up, bind, rng)
        # UPSTREAM FIX (the producer's PINNED label-robust detector, brain-faithful: the copula is closed-class,
        # so don't gate detection on the fragile `cop` label -- fire on the copula token + read holder/property
        # off the tree). Union with the label path, flowed through the SAME consumer register read-out.
        heads = arc.parse(toks, up).heads
        fix_pairs = bind | COP.robust_cop(toks, up, heads, gate=True)
        fix_twin_pairs = COP.shuffle_twin(toks, up, fix_pairs, rng)
        # LIVE consumer: build the state register for THIS sentence via the reader's own read-path method.
        sm = SituationModel(passage_id="s", n_sentences=1)
        reader._read_entity_states(sm, [toks])
        qa = QA.SituationQA(sm)                       # the routed readout over the accumulated model
        sm_off = SituationModel(passage_id="s", n_sentences=1)   # bind OFF -> state_register stays None
        qa_off = QA.SituationQA(sm_off)
        sm_fix = SituationModel(passage_id="s", n_sentences=1); sm_fix.state_register = _register_from_pairs(fix_pairs, toks, up)
        qa_fix = QA.SituationQA(sm_fix)
        sm_ft = SituationModel(passage_id="s", n_sentences=1); sm_ft.state_register = _register_from_pairs(fix_twin_pairs, toks, up)
        qa_ft = QA.SituationQA(sm_ft)

        cur = {k: 0 for k in KEYS}
        for (h, p, t) in gold:
            holder, prop = toks[h], toks[p]
            q = {"dim": "state", "holder": holder, "gold": prop}
            question = _state_q(holder)
            n_tot += 1
            n_hit += int(QA.route(question) == "state")
            n_onto += int(QA.wh_ontology_route(question) == "state")
            # MODEL: route + read off state_register
            _d, ans = qa.answer(question, q)
            m_ok = int(_state_match(ans, prop))
            cur["model"] += m_ok
            # WATERFALL (where the CONSUMER loses signal vs the brain): stage 1 = the upstream binding recovers
            # the (holder, property) pair; stage 3 = the read-back given the binding. Routing (stage 2) is the
            # router hit above. model_ok ~= bind (routing+read-back are near-lossless) locates the loss UPSTREAM.
            has_bind = int((h, p) in bind)
            cur["bind"] += has_bind
            if has_bind:
                cur["rb_given_bind"] += m_ok
            # FLOOR / TWIN: the reused copular-validated pair sets
            cur["floor"] += int((h, p) in floor)
            cur["twin"] += int((h, p) in twin)
            # ROUTER ABLATION: disable the copular frame -> the question misroutes (falls through to events)
            abl_dim = QA.route(question, state_frame=False)
            cur["ablate"] += int(_state_match(qa.readout(abl_dim, q), prop))
            # BASE reader OFF (bind_entity_states off) -> abstain -> the live zero
            _od, oans = qa_off.answer(question, q)
            cur["off"] += int(_state_match(oans, prop))
            # YES/NO 'Is X a Y?' via is_in_state(semantic)
            yn = sm.state_register.is_in_state(holder.lower(), prop.lower(), semantic=True) if sm.state_register else None
            cur["yn_g"] += 1; cur["yn"] += int(yn is True)
            # UPSTREAM FIX flowed through the consumer (route + robust-built register read-out) + its twin
            _fd, fans = qa_fix.answer(question, q)
            fix_ok = int(_state_match(fans, prop))
            cur["fix"] += fix_ok
            cur["fix_bind"] += int((h, p) in fix_pairs)
            _ftd, ftans = qa_ft.answer(question, q)
            cur["fix_twin"] += int(_state_match(ftans, prop))
            cur["g"] += 1
            per_type_g[t] += 1
            per_type_ok[t] += int(_state_match(ans, prop))
            per_type_fix[t] += fix_ok
        per.append(cur)

    res = _aggregate(per, n_boot, seed)
    res.update(
        anchor=ANCHOR, seed=seed, n_sents=len(sents),
        router_state_hit_rate=round(n_hit / max(1, n_tot), 4),
        wh_ontology_state_hit_rate=round(n_onto / max(1, n_tot), 4), n_router=n_tot,
        per_higgins_type={t: {"n": per_type_g[t], "model_recall": round(per_type_ok[t] / max(1, per_type_g[t]), 4),
                              "fix_recall": round(per_type_fix[t] / max(1, per_type_g[t]), 4)}
                          for t in per_type_g},
        elapsed_s=round(time.time() - t0, 1), ts_iso=datetime.now(timezone.utc).isoformat())
    return res


def _rate(per, k):
    g = sum(d["g"] for d in per)
    return sum(d[k] for d in per) / max(1, g)


def _boot_diff(per, a, b, n_boot, seed):
    g = np.array([d["g"] for d in per], float)
    av = np.array([d[a] for d in per], float); bv = np.array([d[b] for d in per], float)
    n = len(per); rng = np.random.default_rng(seed)
    obs = av.sum() / max(g.sum(), 1) - bv.sum() / max(g.sum(), 1)
    ds = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, n); gg = g[idx].sum()
        ds[k] = av[idx].sum() / max(gg, 1e-9) - bv[idx].sum() / max(gg, 1e-9)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return dict(delta=round(float(obs), 4), lo=round(float(lo), 4), hi=round(float(hi), 4),
                hw=round(float((hi - lo) / 2), 4), null_p95=round(float(np.percentile(np.abs(ds - obs), 95)), 4),
                ci_sep=bool(lo > 0))


def _aggregate(per, n_boot, seed):
    n_bind = sum(d["bind"] for d in per)
    return {
        "n_pred_clauses": sum(d["g"] for d in per), "n_docs": len(per),
        "qa_state_model": round(_rate(per, "model"), 4),
        "positional_floor": round(_rate(per, "floor"), 4),
        "shuffle_holder_twin": round(_rate(per, "twin"), 4),
        "router_ablation": round(_rate(per, "ablate"), 4),
        "base_reader_off_zero": round(_rate(per, "off"), 4),
        "yesno_accuracy": round(sum(d["yn"] for d in per) / max(1, sum(d["yn_g"] for d in per)), 4),
        "n_yesno": sum(d["yn_g"] for d in per),
        "model_vs_floor": _boot_diff(per, "model", "floor", n_boot, seed),
        "model_vs_shuffle_twin": _boot_diff(per, "model", "twin", n_boot, seed),
        # brain-vs-us waterfall: brain(~1.0) -> binding(upstream producer) -> routing(=hit rate) -> read-back.
        # read-back GIVEN the binding ~= 1.0 => the consumer adds ~0 loss; the residual is UPSTREAM (detection).
        "waterfall": {"brain_reference": 1.0,
                      "binding_recall_upstream": round(n_bind / max(1, sum(d["g"] for d in per)), 4),
                      "readback_given_binding": round(sum(d["rb_given_bind"] for d in per) / max(1, n_bind), 4)},
        # UPSTREAM FIX (label-robust detection) flowed through the consumer: closes part of the upstream gap.
        "upstream_fix": {
            "qa_state_fix": round(_rate(per, "fix"), 4),
            "fix_binding_upstream": round(sum(d["fix_bind"] for d in per) / max(1, sum(d["g"] for d in per)), 4),
            "fix_shuffle_twin": round(_rate(per, "fix_twin"), 4),
            "fix_vs_label_model": _boot_diff(per, "fix", "model", n_boot, seed),
            "fix_vs_floor": _boot_diff(per, "fix", "floor", n_boot, seed),
            "fix_vs_fix_twin": _boot_diff(per, "fix", "fix_twin", n_boot, seed)},
    }


def board_state_dimension(cap: Optional[int] = None, n_boot: int = 1000, seed: int = SEED):
    """The per_dimension-shaped 'state' row for exp_situation_model_qa_v1.run (auto-picked up by the baseline
    board's Instrument A) + the full detail. Population = the copular problem's UD-EWT predicational gold."""
    res = run(cap=cap, n_boot=n_boot, seed=seed)
    row = {
        "n": res["n_pred_clauses"],
        "model_acc": res["qa_state_model"],
        "overlap_floor": res["positional_floor"],
        "floor_accs": {"most_recent_noun": res["positional_floor"]},
        "strongest_floor_name": "most_recent_noun",
        "strongest_floor": res["positional_floor"],
        "twin_acc": res["shuffle_holder_twin"],
        "model_minus_strongest": [res["model_vs_floor"]["lo"], res["model_vs_floor"]["hi"]],
        "model_minus_twin": [res["model_vs_shuffle_twin"]["lo"], res["model_vs_shuffle_twin"]["hi"]],
        "ci_sep_over_strongest": res["model_vs_floor"]["ci_sep"],
        "ci_sep_over_twin": res["model_vs_shuffle_twin"]["ci_sep"],
        "population": "UD-EWT copular gold (predicational)",
    }
    return row, res


def optimize_upstream(cap: Optional[int] = 1500, n_boot: int = 2000, seed: int = SEED) -> dict:
    """OPTIMIZE the upstream fix: on top of the label-robust detector, add a better parse TREE (arc-eager, the
    producer's validated modern lever: +0.111 base binding CI-sep, identity most) -- brain-faithful (rely on an
    accurate tree, not a label workaround). Measures, through the SAME consumer register read-out, the label path
    -> +robust_cop (July tree) -> +robust_cop(arc-eager tree). Reports whether the tree adds on top of robust_cop
    (the producer found it ~ns on ALL gold because robust_cop already compensates the July tree's cop-misses)."""
    t0 = time.time()
    pos = PosTagger.load(M._POS_ASSET); arc = ArcParser.load(M._ARC_ASSET); lab = ArcLabeler.load(M._LAB_ASSET)
    sents = COP.load_ud(COP.UD_TEST, cap=cap)
    rng = np.random.default_rng(seed)
    per = []
    per_type = {"pred_adj": [0, 0, 0], "pred_nom": [0, 0, 0]}   # [g, fix_ok, fixae_ok]
    for sent in sents:
        toks = [r[1] for r in sent]; up = pos.tag(toks)
        gold = [(h, p, t) for (h, p, t) in COP.typed_gold(sent) if t in PREDICATIONAL]
        if not gold:
            continue
        bind = COP.binding_readback(toks, up, arc, lab)
        heads = arc.parse(toks, up).heads
        fix = bind | COP.robust_cop(toks, up, heads, gate=True)
        try:
            ae = COP.ae_heads(toks, up)
            fix_ae = fix | COP.robust_cop(toks, up, ae, gate=True)
        except Exception:
            fix_ae = fix
        reg_fix = _register_from_pairs(fix, toks, up); reg_ae = _register_from_pairs(fix_ae, toks, up)
        qf = QA.SituationQA(_sm_with(reg_fix)); qa = QA.SituationQA(_sm_with(reg_ae))
        cur = {"g": 0, "fix": 0, "fixae": 0}
        for (h, p, t) in gold:
            q = {"dim": "state", "holder": toks[h], "gold": toks[p]}
            question = _state_q(toks[h])
            f_ok = int(_state_match(qf.answer(question, q)[1], toks[p]))
            a_ok = int(_state_match(qa.answer(question, q)[1], toks[p]))
            cur["fix"] += f_ok; cur["fixae"] += a_ok; cur["g"] += 1
            per_type[t][0] += 1; per_type[t][1] += f_ok; per_type[t][2] += a_ok
        per.append(cur)
    g = sum(d["g"] for d in per)
    res = {"n_pred_clauses": g, "n_docs": len(per),
           "qa_state_fix_july": round(sum(d["fix"] for d in per) / max(1, g), 4),
           "qa_state_fix_arceager": round(sum(d["fixae"] for d in per) / max(1, g), 4),
           "arceager_vs_july": _boot_diff(per, "fixae", "fix", n_boot, seed),
           "per_type": {t: {"n": v[0], "fix_july": round(v[1] / max(1, v[0]), 4),
                            "fix_arceager": round(v[2] / max(1, v[0]), 4)} for t, v in per_type.items()},
           "elapsed_s": round(time.time() - t0, 1)}
    return res


def _sm_with(reg):
    sm = SituationModel(passage_id="s", n_sentences=1); sm.state_register = reg
    return sm


def litbank_coverage(n_docs: int = 25) -> dict:
    """LIVE-FIRES demonstration on real 19c LitBank prose (the reading corpus): the FULL reader (build_reader,
    capable + bind_entity_states) reads each doc and the state consumer answers 'what is X'. CAVEAT: gold is
    READER-DERIVED (no independent LitBank copular gold), so this is COVERAGE / round-trip, NOT a floor-beating
    claim -- the powered number is board_state_dimension above."""
    import experiments.exp_name_entity_clustering_v1 as NC
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    wdw = json.load(open(os.path.join(REPO, "data/litbank/who_did_what_events.json"), encoding="utf-8"))
    gaz = load_given_gazetteer()
    docs = [r["doc"] for r in wdw][:n_docs]
    reader = QA.build_reader(gaz, capable=True)      # capable reader with bind_entity_states=True (this problem)
    n_docs_ok = n_q = n_ans = 0
    for d in docs:
        path = os.path.join(NC.CONLL_DIR, d + ".conll")
        if not os.path.exists(path):
            continue
        sm = reader.read(path)
        qa = QA.SituationQA(sm)
        qs = QA.build_state_questions(sm)
        for q in qs:
            _dim, ans = qa.answer(q["question"], q)
            n_q += 1; n_ans += int(_state_match(ans, q["gold"]))
        n_docs_ok += 1
    return {"n_docs": n_docs_ok, "n_state_questions": n_q, "answered_roundtrip": n_ans,
            "roundtrip_rate": round(n_ans / max(1, n_q), 4),
            "note": "reader-derived gold -> COVERAGE on real 19c prose (live-fires), NOT a capability claim; "
                    "base reader OFF = 0 questions answerable (no state register)."}


def _print(res):
    print(f"\n=== STATE-QA CONSUMER over the copular UD-EWT typed gold (predicational subset) ===")
    print(f"  n_sents={res['n_sents']}  n_pred_clauses={res['n_pred_clauses']}  n_docs={res['n_docs']}  "
          f"elapsed={res['elapsed_s']}s")
    print(f"  router 'what is X' -> state: cue-table {res['router_state_hit_rate']}  "
          f"wh-ontology {res['wh_ontology_state_hit_rate']}")
    print(f"\n  qa_state MODEL (route + state_register readout) = {res['qa_state_model']}")
    print(f"  positional floor (most-recent-noun)            = {res['positional_floor']}")
    print(f"  shuffle-holder twin (copular-validated)        = {res['shuffle_holder_twin']}  (must lose)")
    print(f"  router ablation (frame disabled -> misroute)   = {res['router_ablation']}  (frame is load-bearing)")
    print(f"  BASE reader OFF (bind_entity_states off)       = {res['base_reader_off_zero']}  <- the live zero")
    print(f"  yes/no 'Is X a Y?' (is_in_state semantic)      = {res['yesno_accuracy']} (n={res['n_yesno']})")
    for name, key in [("MODEL vs positional floor", "model_vs_floor"),
                      ("MODEL vs shuffle-holder twin", "model_vs_shuffle_twin")]:
        d = res[key]
        print(f"  {name:32s} d={d['delta']:+.4f} [{d['lo']:+.4f},{d['hi']:+.4f}] "
              f"hw={d['hw']:.4f} nullp95={d['null_p95']:.4f} {'CI-SEP' if d['ci_sep'] else 'n.s.'}")
    print(f"  per Higgins type: {res['per_higgins_type']}")
    w = res["waterfall"]
    print(f"  WATERFALL vs brain: brain~{w['brain_reference']} -> binding(upstream) {w['binding_recall_upstream']} "
          f"-> routing {res['router_state_hit_rate']} -> read-back|binding {w['readback_given_binding']}  "
          f"(consumer loss ~= 0; residual is UPSTREAM detection)")
    uf = res["upstream_fix"]
    print(f"\n  === UPSTREAM FIX (label-robust detection) through the SAME consumer ===")
    print(f"  qa_state (label path) {res['qa_state_model']} -> qa_state_FIX {uf['qa_state_fix']}  "
          f"(fix binding {uf['fix_binding_upstream']}); fix twin {uf['fix_shuffle_twin']}")
    for name, key in [("FIX vs label-path model", "fix_vs_label_model"),
                      ("FIX vs positional floor", "fix_vs_floor"),
                      ("FIX vs its shuffle twin", "fix_vs_fix_twin")]:
        d = uf[key]
        print(f"  {name:28s} d={d['delta']:+.4f} [{d['lo']:+.4f},{d['hi']:+.4f}] "
              f"{'CI-SEP' if d['ci_sep'] else 'n.s.'}")


def self_test():
    res = run(cap=400, n_boot=200)
    assert res["n_pred_clauses"] > 30, res
    assert res["router_state_hit_rate"] > 0.9, ("router must send 'what is X' to state", res)
    assert res["base_reader_off_zero"] == 0.0, ("base reader OFF must score 0 (live zero)", res)
    assert res["qa_state_model"] > res["positional_floor"], ("model must beat floor", res)
    assert res["qa_state_model"] > res["shuffle_holder_twin"], ("model must beat shuffle twin", res)
    assert res["router_ablation"] < res["qa_state_model"], ("ablating the frame must hurt", res)
    print("SELFTEST PASS")
    _print(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cap", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--litbank", action="store_true", help="also run the LitBank live-fires coverage demo")
    ap.add_argument("--optimize", action="store_true", help="also run the arc-eager upstream optimization")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    res = run(cap=args.cap, n_boot=args.n_boot)
    if args.litbank:
        res["litbank_coverage"] = litbank_coverage()
    if args.optimize:
        res["upstream_optimization_arceager"] = optimize_upstream(cap=args.cap, n_boot=args.n_boot)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)
    _print(res)
    if "litbank_coverage" in res:
        print(f"\n  LitBank live-fires: {res['litbank_coverage']}")
    print(f"\nwrote {os.path.relpath(os.path.join(OUT_DIR, 'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
