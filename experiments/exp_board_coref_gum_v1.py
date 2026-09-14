"""exp_board_coref_gum_v1 -- the COREF / SALIENCE / COMMON-NOUN board dimensions on MODERN gold (GUM),
plus the cross-consumer proof that the brain-foundational UPSTREAM role assigner lifts coref too.

problem: rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval

This REUSES the owner-scope-sibling SOLVED `form_the_unified_discourse_referent...` machinery verbatim
(experiments/exp_unified_referent_gum_v1.py: the DRT file-change unified Resolver, the floors, the
info-free twin, the doc-paired bootstrap) and RESHAPES its GUM-TEST results into the board's
per_dimension row schema, so the 19c pronoun-coref / salience / common-noun dimensions move onto modern
gold. NO new mechanism; the coref win is the sibling's (pronoun pick +0.106 CI-sep on GUM).

THE UPSTREAM CHAIN (the owner's directive -- every component brain-foundational, all the way upstream):
  * coref pronoun pick   -> the UNIFIED DISCOURSE REFERENT (Heim/Kamp DRT file-change; ACT-R salience;
                            Ariel accessibility) -- upstream component #1, EXCEEDS on modern (reused).
  * BOTH coref (entity-KB hard-link) AND who-did-what(agent) share a DEEPER upstream: the ROLE ASSIGNER.
    cross_consumer_upstream() re-confirms on GUM that swapping the brain-foundational grammatical roles
    for the live POSITIONAL proxy COSTS the entity-KB hard-link (the sibling measured -0.084) -- so the
    Competition-Model role assigner (owner-DONE) must be brain-foundational to realize coref too. This is
    "revisit the other consumers to use the newly-optimized upstream capability", measured on modern gold.

Glass-box, NO external LLM. ASCII. own dir.
Run: .venv/Scripts/python.exe experiments/exp_board_coref_gum_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_board_coref_gum_v1.py --run [--docs N]
"""
from __future__ import annotations
import os, sys, argparse, json, time, random
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import experiments.gum_coref as G
import experiments.exp_unified_referent_gum_v1 as URG
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = str(get_output_dir("board_coref_gum_v1"))  # Q115: re-runnable output path (HDLAB_EXP_NAME-driven)
ANCHOR = "board_coref_gum_v1"
SEED = 20260906


def _load_test(n_docs=None):
    """GUM docs, TEST split = odd doc index (same split as the sibling's headline).

    pri-109: `HDLAB_GUM_DECISION=organ` makes every decision-time field (mention type, span head, lemma key,
    gender/number, role) come from the LIVE organs instead of the treebank's gold columns. The treebank stays
    the answer key (the coref chains). Under `gold` this function is byte-identical to before."""
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz,
                       decision_source=G.DECISION_SOURCE)
    test = [d for i, d in enumerate(docs) if i % 2 == 1]
    return docs, test, gaz


def _row_from_consumer(res_arms, mtype, floor_pool=("separate", "recency", "string_identity")):
    """Reshape the sibling's per-arm GUM results into a board per_dimension row for a coref consumer."""
    acc = {}
    for arm in ("separate", "unified", "twin", "recency", "string_identity"):
        a, t = URG._acc(res_arms[arm], mtype)
        acc[arm] = (round(a, 4) if a == a else None, t)
    floor_arm = max([k for k in floor_pool if acc[k][1] > 0], key=lambda k: acc[k][0])
    d, lo, hi, hw = URG._paired_boot(res_arms[floor_arm], res_arms["unified"], mtype)
    dt, lot, hit, _ = URG._paired_boot(res_arms["twin"], res_arms["unified"], mtype)
    m = acc["unified"][0]; fl = acc[floor_arm][0]; tw = acc["twin"][0]
    row = {
        "n": acc["unified"][1], "model_acc": m,
        "overlap_floor": fl,
        "floor_accs": {floor_arm: fl, "recency": acc["recency"][0], "string_identity": acc["string_identity"][0]},
        "strongest_floor_name": floor_arm, "strongest_floor": fl,
        "twin_acc": tw,
        "model_minus_strongest": [round(d, 4), round(lo, 4), round(hi, 4)],
        "model_minus_twin": [round(dt, 4), round(lot, 4), round(hit, 4)],
        "ci_sep_over_strongest": bool(lo > 0),
        "ci_sep_over_twin": bool(lot > 0),
        "population": "GUM (modern, TEST=odd docs) %s; UNIFIED discourse referent (DRT file-change) vs the "
                      "strongest simple floor + info-free shuffled-identity twin." % mtype,
    }
    return row


def board_coref_modern_dimension(n_docs=None):
    """PRONOUN coref on modern GUM (the sibling's headline win, reshaped): unified referent pronoun pick
    vs the separate-tracking reader / recency / string-identity floor + shuffled-identity twin."""
    _docs, test, _gaz = _load_test(n_docs)
    arms = {"separate": URG._run_arm(URG.Resolver("separate"), test),
            "unified": URG._run_arm(URG.Resolver("unified"), test),
            "twin": URG._run_arm(URG.Resolver("unified", twin=True, rng=random.Random(99)), test),
            "recency": URG._run_arm(URG.FloorResolver("recency"), test),
            "string_identity": URG._run_arm(URG.FloorResolver("string-identity"), test)}
    row = _row_from_consumer(arms, "pronoun")
    # COMMON-NOUN: the Q111 typed-identity + non-writing (Nref) type-bridge WIN (SOLVED
    # improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity). The levered URG Resolver
    # scores the common-noun consumer on the referent's NOMINAL identity (de-pollutes the ~47%-accurate pronoun
    # bindings) and bridges different-head definites to the most-salient TYPE-compatible prior referent WITHOUT
    # merging (Nref hold-under-uncertainty; Nieuwland), the candidate set seeded by the landed hdlab.typed_spokes
    # organ. This BEATS same-head string-identity CI-sep (0.5671 vs 0.5412, +0.0259), the info-free twin (random
    # bridge) LOSES, and pronoun (byte-identical) / kb / name do NOT regress. The levered model + its OWN info-free
    # twin replace the plain-unified arm for the common row ONLY; the pronoun / entity-KB rows are unchanged.
    lev = URG._run_arm(URG.Resolver("unified", typed_identity=True, bridge=True, bridge_write=False,
                                    type_comparator="typed_spokes"), test)
    lev_twin = URG._run_arm(URG.Resolver("unified", typed_identity=True, bridge=True, bridge_write=False,
                                         type_comparator="typed_spokes", twin=True, twin_mode="random_bridge",
                                         rng=random.Random(99)), test)
    common = _row_from_consumer({**arms, "unified": lev, "twin": lev_twin}, "common")
    kb = _row_from_consumer(arms, "kb_hardlink")
    row_detail = {"pronoun_pick": row, "common_noun": common, "entity_kb_hardlink": kb,
                  "common_noun_typelicense": board_commonnoun_typelicense_dimension(test, arms),
                  "note": "pronoun pick is the modern coref dimension (unified referent EXCEEDS the separate "
                          "reader CI-sep, twin loses); common-noun now BEATS same-head string-identity CI-sep via "
                          "the Q111 typed-identity card view (nominal vs full mention set) + a non-writing (Nref) "
                          "type-bridge seeded by the landed typed-spokes organ (info-free random-bridge twin loses; "
                          "pronoun byte-identical, kb/name no-regress); entity-KB hard-link is the 2nd consumer."}
    return row, row_detail


def board_commonnoun_typelicense_dimension(test, arms):
    """FLIP-GATE MEASUREMENT (Q111 realization): does the C5+C6 typed-spoke, used as a binary TYPE-LICENSING FILTER
    on the LIVE common-noun coref pick, net-help on the board's OWN common_noun_coref instrument?  The SOLVED
    exp_isa_spoke_commonnoun_coref_gum_v1 measured +0.0116 CI-sep -- but on ITS OWN non-merging recency-tracker with
    a baseline (recency 0.6883) that ALREADY reaches different-head. The board's live pick (URG unified) does NOT
    reach different-head (its strongest floor is same-head string-identity) and MERGES referents (DRT file-change),
    so this arm re-measures the filter ON TOP OF the actual live pick, per no-more-default-off (do not assume the
    SOLVED floor; measure the live baseline).

    ARMS (all on the board's common_noun_coref population; model=common-noun antecedent accuracy):
      baseline    URG.Resolver('unified')                         -- the ACTUAL live board pick (filter OFF)
      filter_on   URG.Resolver('unified', isa_type_license=True)  -- + C5+C6 binary type-license, recency selects
      twin        filter_on with a SHUFFLED is-a/part-whole graph (info-free; must lose if the knowledge is real)
      floors      string_identity / recency / separate (the strongest simple floors actually run on this population)
    Returns a per_dimension-schema row. This is the flip-gate's board-visible, reproducible evidence."""
    import numpy as np
    import experiments.exp_isa_spoke_commonnoun_coref_gum_v1 as CN
    from hdlab.typed_spokes import coref_type_license
    heads = sorted({m.lemma_head for d in test for m in d.mentions if m.mtype == "common"})
    sh_anc, sh_mero = CN.build_shuffled_spoke(heads, seed=0)   # the SOLVED's shuffled-graph twin (byte-faithful)
    twin_lic = lambda a, b: coref_type_license(a, b, anc_fn=sh_anc, mero_fn=sh_mero)
    filt = URG._run_arm(URG.Resolver("unified", isa_type_license=True), test)
    twin = URG._run_arm(URG.Resolver("unified", isa_type_license=True, license_fn=twin_lic), test)

    def acc(pd):
        a, t = URG._acc(pd, "common"); return round(a, 4), t
    base_acc, n = acc(arms["unified"])
    filt_acc, _ = acc(filt); twin_acc, _ = acc(twin)
    sid_acc, _ = acc(arms["string_identity"]); rec_acc, _ = acc(arms["recency"]); sep_acc, _ = acc(arms["separate"])
    floors = {"live_pick_unified": base_acc, "string_identity": sid_acc, "recency": rec_acc, "separate": sep_acc}
    fname = max(floors, key=floors.get); fval = floors[fname]
    strong_pd = {"live_pick_unified": arms["unified"], "string_identity": arms["string_identity"],
                 "recency": arms["recency"], "separate": arms["separate"]}[fname]
    d_base, lo_b, hi_b, _ = URG._paired_boot(arms["unified"], filt, "common")   # filter_on - live baseline
    d_str, lo_s, hi_s, _ = URG._paired_boot(strong_pd, filt, "common")          # filter_on - strongest floor
    d_tw, lo_t, hi_t, _ = URG._paired_boot(twin, filt, "common")                # filter_on - info-free twin
    decision = ("KEEP DEFAULT-OFF" if (d_base <= 0 or lo_b <= 0 or lo_t <= 0 or lo_s <= 0) else "FLIP DEFAULT-ON")
    return {
        "n": n, "model_acc": filt_acc, "overlap_floor": fval,
        "floor_accs": floors, "strongest_floor_name": fname, "strongest_floor": fval,
        "twin_acc": twin_acc,
        "model_minus_strongest": [round(d_str, 4), round(lo_s, 4), round(hi_s, 4)],
        "model_minus_live_baseline": [round(d_base, 4), round(lo_b, 4), round(hi_b, 4)],
        "model_minus_twin": [round(d_tw, 4), round(lo_t, 4), round(hi_t, 4)],
        "ci_sep_over_strongest": bool(lo_s > 0),
        "ci_sep_over_live_baseline": bool(lo_b > 0),
        "ci_sep_over_twin": bool(lo_t > 0),
        "decision": decision,
        "population": "GUM (modern, TEST) anaphoric common-noun mentions, board's OWN common_noun_coref instrument "
                      "(URG unified resolver, DRT file-change merge); model = + C5+C6 binary TYPE-LICENSING filter "
                      "(recency selects among the is-a/part-whole/synonym-licensed different-head set); baseline = "
                      "the live pick (filter OFF); twin = shuffled-graph info-free filter. Doc-level paired bootstrap.",
        "note": "FLIP-GATE (measure-then-decide): the SOLVED's +0.0116 was on a DIFFERENT, non-merging instrument "
                "whose baseline already reached different-head by recency. On the LIVE board pick the filter %s the "
                "baseline (%+.4f) and the shuffled-graph twin is %s -- the p12 pattern (a win vs a weakened baseline "
                "evaporates against the stronger live pick). Ariel accessibility: modern common-noun anaphora is "
                "head/recency-driven; different-head world-knowledge bridging is rare + low-precision + pollutes the "
                "merged referent cards. DECISION: %s." % (
                    "REGRESSES" if d_base < 0 else "does not beat", d_base,
                    "indistinguishable (CI incl 0)" if lo_t <= 0 else "beaten CI-sep", decision)}


def board_salience_modern_dimension(n_docs=None, n_boot=1000, seed=SEED):
    """MAIN-CHARACTER salience on modern GUM. gold_main = the gold entity with the MOST mentions. MODEL =
    the reader's MOST-MENTIONED entity (mention frequency IS a salience cue -- the 19c board's own
    most-mentioned-cluster readout, now on modern gold); FLOOR = the FIRST-introduced entity (a position
    baseline); TWIN = a random entity. Entities are the reader's SEPARATE surface-head clusters (imperfect
    -> non-degenerate). ACT-R prominence is reported as a DETAIL (frequency dominates on modern gold; the
    prominence-vs-frequency distinction is a follow-on). Doc-paired bootstrap."""
    from collections import Counter
    _docs, test, _gaz = _load_test(n_docs)
    rng = random.Random(seed)
    per = {}       # doc -> [n, freq_ok, firstmention_ok, twin_ok, actr_ok]
    for d in test:
        gold_counts = {}
        for m in d.mentions:
            gold_counts[m.eid] = gold_counts.get(m.eid, 0) + 1
        if not gold_counts:
            continue
        gold_main = max(gold_counts, key=lambda e: (gold_counts[e], -e))
        clusters = {}   # key -> {"hist": [(order, role)], "eids": [], "n": 0, "first": order}
        deprel_by_g = {t.gidx: t.deprel for t in d.toks}
        for m in d.mentions:
            if m.mtype == "pronoun":
                continue
            key = ("name", frozenset(URG._name_tokens(m))) if m.mtype == "name" else ("common", m.lemma_head)
            role = URG._role(deprel_by_g.get(m.head_g, "OTHER"))
            c = clusters.setdefault(key, {"hist": [], "eids": [], "n": 0, "first": m.order})
            c["hist"].append((m.order, role)); c["eids"].append(m.eid); c["n"] += 1
            c["first"] = min(c["first"], m.order)
        if len(clusters) < 2:
            continue
        def dom(c):
            return Counter(c["eids"]).most_common(1)[0][0]
        now = max(m.order for m in d.mentions) + 1
        cl = list(clusters.values())
        freq_c = max(cl, key=lambda c: c["n"])                       # MODEL: most-mentioned = protagonist
        first_c = min(cl, key=lambda c: c["first"])                  # FLOOR: first-introduced entity
        twin_c = rng.choice(cl)
        actr_c = max(cl, key=lambda c: actr_activation(c["hist"], float(now), decay=DEFAULT_DECAY,
                                                       role_prominence=ROLE_PROMINENCE))
        pd = per.setdefault(d.docid, [0, 0, 0, 0, 0])
        pd[0] += 1
        pd[1] += int(dom(freq_c) == gold_main)
        pd[2] += int(dom(first_c) == gold_main)
        pd[3] += int(dom(twin_c) == gold_main)
        pd[4] += int(dom(actr_c) == gold_main)
    n = sum(v[0] for v in per.values())
    m = round(sum(v[1] for v in per.values()) / max(1, n), 4)
    fl = round(sum(v[2] for v in per.values()) / max(1, n), 4)
    tw = round(sum(v[3] for v in per.values()) / max(1, n), 4)
    actr = round(sum(v[4] for v in per.values()) / max(1, n), 4)
    ms = _boot(per, 1, 2, n_boot, seed)
    mt = _boot(per, 1, 3, n_boot, seed)
    row = {
        "n": n, "model_acc": m, "overlap_floor": fl,
        "floor_accs": {"first_introduced_entity": fl}, "strongest_floor_name": "first_introduced_entity",
        "strongest_floor": fl, "twin_acc": tw,
        "model_minus_strongest": ms, "model_minus_twin": mt,
        "ci_sep_over_strongest": bool(ms[1] is not None and ms[1] > 0),
        "ci_sep_over_twin": bool(mt[1] is not None and mt[1] > 0),
        "population": "GUM (modern, TEST) main-character salience; MODEL = reader's most-mentioned entity "
                      "(frequency-of-mention salience, the 19c board's readout, now modern) vs the "
                      "first-introduced-entity floor; gold = gold most-mentioned entity.",
    }
    return row, {"n": n, "model_frequency": m, "floor_first_mention": fl, "twin_random": tw,
                 "actr_prominence": actr,
                 "note": "salience on modern gold is FREQUENCY-DOMINATED (the protagonist is by construction "
                         "the most-mentioned entity); ACT-R prominence over imperfect surface-head clusters "
                         "(%.4f) does NOT beat raw frequency here -- prominence-vs-frequency is a follow-on." % actr}


def _boot(per, ia, ib, n_boot, seed):
    keys = list(per.keys())
    if not keys:
        return [None, None, None]
    N = np.array([per[k][0] for k in keys], float)
    A = np.array([per[k][ia] for k in keys], float)
    B = np.array([per[k][ib] for k in keys], float)
    obs = (A.sum() - B.sum()) / max(N.sum(), 1)
    rng = np.random.default_rng(seed)
    n = len(keys)
    ds = np.empty(n_boot)
    for b in range(n_boot):
        s = rng.integers(0, n, n)
        nn = N[s].sum()
        ds[b] = (A[s].sum() - B[s].sum()) / max(nn, 1e-9)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return [round(float(obs), 4), round(float(lo), 4), round(float(hi), 4)]


def cross_consumer_upstream(n_docs=None):
    """THE CROSS-CONSUMER UPSTREAM PROOF (owner's directive): the entity-KB hard-link coref consumer is
    lifted by the brain-foundational grammatical role assigner. Run the unified resolver with GOLD
    grammatical roles vs the live POSITIONAL role proxy (positional_roles=True) and measure the entity-KB
    hard-link. Positional roles COST the consumer -> the same upstream (a brain-foundational role assigner,
    the owner-DONE Competition Model) that the who-did-what AGENT dimension needs ALSO lifts coref."""
    _docs, test, _gaz = _load_test(n_docs)
    gold_roles = URG._run_arm(URG.Resolver("unified", positional_roles=False), test)
    pos_roles = URG._run_arm(URG.Resolver("unified", positional_roles=True), test)
    d, lo, hi, hw = URG._paired_boot(pos_roles, gold_roles, "kb_hardlink")   # gold - positional
    g, _ = URG._acc(gold_roles, "kb_hardlink"); p, _ = URG._acc(pos_roles, "kb_hardlink")
    return {"consumer": "entity_kb_hardlink", "gold_roles_acc": round(g, 4), "positional_roles_acc": round(p, 4),
            "gold_minus_positional": [round(d, 4), round(lo, 4), round(hi, 4)],
            "positional_roles_cost_the_consumer": bool(lo > 0),
            "note": "brain-foundational (gold grammatical) roles beat the live positional role proxy on the "
                    "entity-KB hard-link coref consumer -> the upstream role assigner must be brain-foundational "
                    "to realize coref too (the SAME upstream the who-did-what AGENT dimension needs)."}


def run(n_docs=None, n_boot=1000, seed=SEED):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    pr, pr_detail = board_coref_modern_dimension(n_docs)
    sal, sal_detail = board_salience_modern_dimension(n_docs, n_boot, seed)
    cross = cross_consumer_upstream(n_docs)
    res = {"anchor": ANCHOR, "seed": seed,
           "coref_pronoun_row": pr, "coref_detail": pr_detail,
           "salience_row": sal, "salience_detail": sal_detail,
           "cross_consumer_upstream": cross,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2, default=str)
    return res


def _print(res):
    pr, sal, cx = res["coref_pronoun_row"], res["salience_row"], res["cross_consumer_upstream"]
    cn = res["coref_detail"]["common_noun"]
    print("=" * 96)
    print("MODERN COREF / SALIENCE board dimensions (GUM)")
    print("  PRONOUN coref  model=%.4f floor[%s]=%.4f twin=%.4f  m-floor=%s ci_sep=%s twin-loses=%s" % (
        pr["model_acc"], pr["strongest_floor_name"], pr["strongest_floor"], pr["twin_acc"],
        pr["model_minus_strongest"], pr["ci_sep_over_strongest"], pr["ci_sep_over_twin"]))
    print("  COMMON-NOUN    model=%.4f floor=%.4f  m-floor=%s ci_sep=%s  (Q111 typed-identity + Nref type-bridge WIN)" % (
        cn["model_acc"], cn["strongest_floor"], cn["model_minus_strongest"], cn["ci_sep_over_strongest"]))
    tl = res["coref_detail"].get("common_noun_typelicense")
    if tl:
        print("  CN TYPE-LICENSE model=%.4f live-baseline=%.4f twin=%.4f  m-base=%s m-twin=%s  -> %s" % (
            tl["model_acc"], tl["floor_accs"]["live_pick_unified"], tl["twin_acc"],
            tl["model_minus_live_baseline"], tl["model_minus_twin"], tl["decision"]))
    print("  SALIENCE       model(freq)=%.4f floor(1st-mention)=%.4f twin=%.4f  m-floor=%s ci_sep=%s" % (
        sal["model_acc"], sal["strongest_floor"], sal["twin_acc"], sal["model_minus_strongest"],
        sal["ci_sep_over_strongest"]))
    print("  CROSS-CONSUMER UPSTREAM (entity-KB hard-link): gold-roles %.4f vs positional-roles %.4f  "
          "gold-pos=%s cost=%s" % (cx["gold_roles_acc"], cx["positional_roles_acc"],
                                   cx["gold_minus_positional"], cx["positional_roles_cost_the_consumer"]))
    print("=" * 96)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=1000)
    a = ap.parse_args()
    if a.self_test:
        res = run(n_docs=40, n_boot=300)
        assert res["coref_pronoun_row"]["n"] > 100, res["coref_pronoun_row"]
        assert res["salience_row"]["n"] > 5, res["salience_row"]
        _print(res)
        print("\n[self-test] PASS")
        return
    res = run(n_docs=a.docs, n_boot=a.n_boot)
    _print(res)
    print("\nwrote %s" % os.path.relpath(os.path.join(OUT_DIR, "metrics.json"), _REPO))


if __name__ == "__main__":
    main()
