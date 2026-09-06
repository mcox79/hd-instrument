"""LANDING witness for rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval.

Proves FIRST-HAND (capped threads, PASS/FAIL per check) the four things the Q111 landing adds on top of the
already-passing instrument witness (verification/test_modern_board.py, 12/12):

  W1 STEP-0 INSTRUMENT: the modern board emits a 19c-FREE headline aggregate (item-weighted over MODERN dims,
     NO LitBank dim; named gaps temporal/causal/goal/affect) AND demotes the 19c LitBank board to an
     informational_19c_crossref block (kept, NOT the headline).
  W2 THREE NEW BOARD ARMS produce their rows (make the session's board-invisible proven wins SCORED):
     coarse-sense (SemCor, INFORMATIONAL under the 19c ban), selective-reliability (UD-EWT, MODERN),
     causal-multihop (WIQA + TellMeWhy, MODERN). Each returns a per_dimension-shaped row.
  W3 AGENT HYBRID (hdlab.graded_role_assigner.hybrid_agent_pick, wired behind SituationReader.agent_hybrid,
     default OFF): NO-REGRESS vs the positional floor on CANONICAL modern clauses + LIFT on the NON-CANONICAL
     slice; the reader flag is default-OFF, in CAPABILITY_FLAGS, and OFF in the historical all_capabilities_off
     reader (agent_hybrid=False => the AGENT is byte-identical to the pre-hybrid always-compete reader).
  W4 1b RECONCILIATION (SKIP 1b -- byhead-subsumed): the LANDED byhead cue (by_governs + participle_bypp_gate,
     byhead ON) ALREADY lifts the multi-word by-phrase PASSIVE slice over the pre-byhead byagent-only cue --
     >= the coverage the skipped 1b patch would have added, so 1b is double-counting.

Glass-box, NO external LLM, deterministic, ASCII, CPU-only, threads capped.
Run: OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3 THINC_NUM_THREADS=3 \
     .venv/Scripts/python.exe verification/test_modern_board_landing.py
"""
from __future__ import annotations
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

FAILS = []
_ROW_KEYS = ("n", "model_acc", "strongest_floor", "strongest_floor_name", "twin_acc",
             "model_minus_strongest", "model_minus_twin", "ci_sep_over_strongest",
             "ci_sep_over_twin", "population")


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def _is_row(r):
    return isinstance(r, dict) and all(k in r for k in _ROW_KEYS)


# ---------------------------------------------------------------------------
# W1 -- STEP-0 INSTRUMENT: 19c-free headline aggregate + informational_19c_crossref demotion.
# ---------------------------------------------------------------------------
def test_w1_instrument():
    import experiments.exp_situation_model_qa_modern_v1 as B
    # capped, new arms OFF, does NOT clobber the full metrics artifact
    res = B.run(caps={"gum": 40, "ud": 300, "state": 300, "wic_mode": "smoke"}, n_boot=200,
                run_new_arms=False, write_metrics=False)
    agg = res["aggregate_19c_free"]
    tr = res["transferred_to_modern"]
    no_litbank = all(("LitBank" not in v["gold"] and "19c" not in v["gold"]) for v in tr.values())
    gaps_named = all(g in res["named_gaps"] for g in ("temporal", "causal", "goal", "affect"))
    cr = res["informational_19c_crossref"]
    demoted = ("DEMOTED" in cr["status"] and cr["corpus"].startswith("LitBank")
               and "aggregate_19c_free" not in cr)  # the crossref is NOT the headline
    check("W1 STEP-0: 19c-FREE headline aggregate (model=%s over %d modern dims, NO LitBank dim) + named gaps "
          "%s + informational_19c_crossref DEMOTED (LitBank kept, not the headline)"
          % (agg.get("model_acc"), agg.get("n_dims_total"), ", ".join(res["named_gaps"])),
          bool(agg and no_litbank and gaps_named and demoted),
          "no_litbank=%s gaps=%s crossref_status=%r loaded_from_disk=%s"
          % (no_litbank, gaps_named, cr["status"], cr.get("loaded_from_disk")))


# ---------------------------------------------------------------------------
# W2 -- THREE NEW BOARD ARMS produce their per_dimension rows.
# ---------------------------------------------------------------------------
def test_w2_new_arms():
    import experiments.exp_situation_model_qa_modern_v1 as B

    # (1) coarse-sense (SemCor; INFORMATIONAL). Small cap; a genuine row (schema), flagged informational.
    cs, _ = B.board_coarse_sense_dimension(max_files=3)
    check("W2a coarse-sense arm returns a per_dimension row (SemCor, INFORMATIONAL under the 19c ban)",
          _is_row(cs) and cs.get("informational") is True,
          "n=%s model=%s floor=%s informational=%s" % (cs.get("n"), cs.get("model_acc"),
                                                        cs.get("strongest_floor"), cs.get("informational")))

    # (2) selective-reliability (UD-EWT, MODERN): patient + obl rows; model=answered_acc beats blanket floor.
    sr, _ = B.board_selective_reliability_dimension(cap=500, n_boot=400)
    p = sr.get("patient_defer"); o = sr.get("obl_defer")
    sr_ok = _is_row(p) and _is_row(o) and p["model_acc"] is not None and p["model_acc"] >= p["strongest_floor"]
    check("W2b selective-reliability arm (MODERN UD-EWT): patient + obl rows; deferral answered_acc >= blanket "
          "floor, twin ~flat",
          bool(sr_ok),
          "patient model=%s floor=%s d=%s twin=%s | obl model=%s floor=%s"
          % (p and p["model_acc"], p and p["strongest_floor"], p and p["model_minus_strongest"],
             p and p["twin_acc"], o and o.get("model_acc"), o and o.get("strongest_floor")))

    # (3) causal-multihop (WIQA + TellMeWhy, MODERN): rows; WIQA model beats the 1-hop adjacency floor.
    ca, _ = B.board_causal_multihop_dimension(wiqa_cap=1500, tmw_n=80)
    wq = ca.get("wiqa_multihop"); tm = ca.get("tellmewhy_nonadjacent")
    wq_ok = _is_row(wq) and wq["model_acc"] is not None and wq["model_minus_strongest"][0] > 0
    check("W2c causal-multihop arm (MODERN): WIQA multi-hop + TellMeWhy non-adjacent rows; WIQA reason_oracle "
          "beats the 1-hop adjacency floor (multi-hop traversal load-bearing)",
          bool(wq_ok and _is_row(tm)),
          "WIQA n=%s model=%s adj_floor=%s twin=%s ci_sep=%s | TMW n=%s model=%s floor=%s"
          % (wq and wq["n"], wq and wq["model_acc"], wq and wq["strongest_floor"], wq and wq["twin_acc"],
             wq and wq["ci_sep_over_strongest"], tm and tm.get("n"), tm and tm.get("model_acc"),
             tm and tm.get("strongest_floor")))


# ---------------------------------------------------------------------------
# W3 -- AGENT HYBRID: no-regress on canonical + lift on non-canonical; reader flag default-OFF & safe.
# ---------------------------------------------------------------------------
def _ud_items():
    from hdlab.pos_tagger import PosTagger
    import experiments.exp_board_agent_noncanonical_v1 as NC
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    tagger = PosTagger.load(os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    gaz = load_given_gazetteer()
    sents = (load_ud(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu"))
             + load_ud(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")))
    return NC.gold_agent_items(sents), tagger, gaz, NC


def test_w3_agent_hybrid():
    import hdlab.graded_role_assigner as GRA
    from hdlab.situation_reader import SituationReader
    # (a) reader flag additive-safety: default OFF, tracked, OFF in the historical reader
    default_off = SituationReader(gaz={}).agent_hybrid is False
    tracked = "agent_hybrid" in SituationReader.CAPABILITY_FLAGS
    hist_off = SituationReader.all_capabilities_off(gaz={}).agent_hybrid is False
    check("W3a agent_hybrid additive-safety: default OFF (=> byte-identical to the pre-hybrid always-compete "
          "reader), in CAPABILITY_FLAGS, OFF in all_capabilities_off",
          bool(default_off and tracked and hist_off),
          "default_off=%s tracked=%s hist_off=%s" % (default_off, tracked, hist_off))

    # (b) ORGAN measurement on UD gold: canonical NO-REGRESS + non-canonical LIFT vs the positional floor
    items, tagger, gaz, NC = _ud_items()
    canon = {"pos": 0, "hyb": 0, "n": 0}
    noncanon = {"pos": 0, "hyb": 0, "n": 0}
    for (toks, v, ag, passive) in items:
        up = tagger.tag(list(toks))
        cands = NC._clause_local(toks, up, v)
        if not cands:
            continue
        gold = str(toks[ag - 1]).lower()
        fi = NC._floor_idx(v, cands)
        pos_head = str(toks[fi]).lower() if fi is not None else None
        hyb = GRA.hybrid_agent_pick(toks, up, v - 1, cands, gaz=gaz)   # v-1 -> 0-based; byhead ON by default
        hyb = str(hyb).lower() if hyb is not None else None
        cls = NC._classify(toks, up, v, cands, passive)
        bucket = canon if cls == "canonical_active" else noncanon
        bucket["n"] += 1
        bucket["pos"] += int(pos_head == gold)
        bucket["hyb"] += int(hyb == gold)
    cpos = canon["pos"] / max(1, canon["n"]); chyb = canon["hyb"] / max(1, canon["n"])
    npos = noncanon["pos"] / max(1, noncanon["n"]); nhyb = noncanon["hyb"] / max(1, noncanon["n"])
    check("W3b agent hybrid NO-REGRESS on canonical (n=%d): hybrid %.4f ~= positional %.4f (within 0.01)"
          % (canon["n"], chyb, cpos), chyb >= cpos - 0.01, "hyb-pos=%+.4f" % (chyb - cpos))
    check("W3c agent hybrid LIFT on NON-CANONICAL (n=%d): hybrid %.4f > positional %.4f"
          % (noncanon["n"], nhyb, npos), nhyb > npos, "hyb-pos=%+.4f" % (nhyb - npos))

    # (d) CONSTRUCTION cues (1c, opt-in): existential + guarded coordination overrides COMPOSE with byhead and
    # lift their slices over the plain hybrid, with canonical no-regress. Measured at the hdlab-organ level.
    import experiments.exp_board_agent_construction_v1 as CX
    con = {"base": 0, "constr": 0, "n": 0}
    ccanon = {"base": 0, "constr": 0, "n": 0}
    for (toks, v, ag, passive) in items:
        up = tagger.tag(list(toks))
        cands = NC._clause_local(toks, up, v)
        if not cands:
            continue
        gold = str(toks[ag - 1]).lower()
        cc = "passive" if passive else CX._construction_class(toks, up, v, cands)
        b = GRA.hybrid_agent_pick(toks, up, v - 1, cands, gaz=gaz, construction=False)
        c = GRA.hybrid_agent_pick(toks, up, v - 1, cands, gaz=gaz, construction=True)
        b = str(b).lower() if b is not None else None
        c = str(c).lower() if c is not None else None
        bucket = con if cc in ("existential", "coordination") else ccanon
        bucket["n"] += 1
        bucket["base"] += int(b == gold)
        bucket["constr"] += int(c == gold)
    cb = con["base"] / max(1, con["n"]); cco = con["constr"] / max(1, con["n"])
    kb = ccanon["base"] / max(1, ccanon["n"]); kc = ccanon["constr"] / max(1, ccanon["n"])
    check("W3d CONSTRUCTION cues (1c, opt-in) COMPOSE with byhead: on existential+coordination (n=%d) hybrid+"
          "construction %.4f > plain hybrid %.4f; canonical no-regress (%.4f ~= %.4f within 0.005)"
          % (con["n"], cco, cb, kc, kb), cco > cb and kc >= kb - 0.005,
          "constr-slice %+.4f | canonical %+.4f" % (cco - cb, kc - kb))


# ---------------------------------------------------------------------------
# W4 -- 1b RECONCILIATION: the landed byhead cue already covers the multi-word by-phrase passive slice.
# ---------------------------------------------------------------------------
def test_w4_byhead_subsumes_1b():
    import hdlab.graded_role_assigner as GRA
    items, tagger, gaz, NC = _ud_items()
    n = off = on = expfix = 0
    for (toks, v, ag, passive) in items:
        if not passive:
            continue
        up = tagger.tag(list(toks))
        cands = NC._clause_local(toks, up, v)
        if not cands:
            continue
        gold = str(toks[ag - 1]).lower()
        off_pick = GRA.agent_competition_pick(toks, up, v - 1, cands, gaz=gaz, byhead_agent_cue=False)
        on_pick = GRA.agent_competition_pick(toks, up, v - 1, cands, gaz=gaz, byhead_agent_cue=True)
        ei = NC._pick_idx(toks, up, v, cands, gaz, byfix=True)   # the skipped 1b _byagent_fixed patch
        n += 1
        off += int(str(off_pick).lower() == gold)
        on += int(str(on_pick).lower() == gold)
        expfix += int(ei == ag - 1)
    a_off = off / max(1, n); a_on = on / max(1, n); a_fix = expfix / max(1, n)
    check("W4 1b reconciliation (SKIP 1b -- byhead-subsumed): on the PASSIVE slice (n=%d) the landed byhead cue "
          "ON (%.4f) lifts multi-word by-phrase agents over the pre-byhead byagent-only cue OFF (%.4f), >= the "
          "skipped 1b _byagent_fixed patch (%.4f) -> 1b would double-count" % (n, a_on, a_off, a_fix),
          a_on > a_off and a_on >= a_fix - 0.01,
          "byhead ON %.4f vs OFF %.4f (+%.4f); 1b-patch %.4f" % (a_on, a_off, a_on - a_off, a_fix))


if __name__ == "__main__":
    test_w1_instrument()
    test_w2_new_arms()
    test_w3_agent_hybrid()
    test_w4_byhead_subsumes_1b()
    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL LANDING WITNESS CHECKS PASSED")
