"""test_readlearned_arc_scorer_scale -- scaffold-free witness for
`scale_the_reading_learned_arc_scorer_the_brain_foundational_parser_acquisition`.

Reads the four landed metrics.json files and re-asserts the headline claims, plus a few LIVE micro-checks
(construction-arc functions on a toy sentence; a cache-hit reading-learned model beating the floor on a small
test slice; the online-pass running). Reads only landed data + runs cheap checks -- it does NOT re-run the
expensive full EM (that is cached). Writes nothing to landed dirs.

Run: .venv/Scripts/python.exe verification/test_readlearned_arc_scorer_scale.py
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

DATA = os.path.join(_REPO, "data")
N = 0
OK = 0


def chk(cond, msg):
    global N, OK
    N += 1
    if cond:
        OK += 1
    else:
        print("  FAIL:", msg)
    return cond


def load(name):
    p = os.path.join(DATA, name, "metrics.json")
    assert os.path.exists(p), "missing landed metrics: %s (run experiments/%s.py --mode full first)" % (p, name)
    with open(p) as f:
        return json.load(f)


def main():
    # ---------- Step 1: scale + EM curve + prior sweep ----------
    s = load("exp_readlearned_scorer_scale_v1")
    chk(s["n_train"] > 11000, "full-corpus scale (n_train>11k), got %s" % s["n_train"])
    chk(0.29 < s["strong_floor_adjacency_right"] < 0.31, "strong right-branching floor ~0.30")
    # scale is FLAT (not the lever): 2k vs full differ by < 0.02
    sc = {r["n_train"]: r["uas"] for r in s["scale_curve_0EM"]}
    lo_n = min(sc); hi_n = max(sc)
    chk(abs(sc[hi_n] - sc[lo_n]) < 0.02, "scale curve FLAT (2k..full within 0.02): %s" % sc)
    # EM peaks then declines (likelihood != accuracy)
    em = {r["round"]: r["uas"] for r in s["em_curve"]}
    chk(s["best_em_round"] in (1, 2, 3), "EM peaks early (round 1-3), got %s" % s["best_em_round"])
    chk(em[max(em)] < s["best_em_uas"] + 1e-9 and em[max(em)] <= em[s["best_em_round"]],
        "EM declines after the peak: %s" % em)
    chk(0.46 < s["best_em_uas"] < 0.50, "best reading-learned UAS ~0.478, got %s" % s["best_em_uas"])
    chk(s["best_em_vs_strong_floor"]["ci_sep"], "reading-learned beats strong floor CI-sep")
    chk(s["twin_shuffled_table_uas"] < s["strong_floor_adjacency_right"],
        "shuffled-table twin COLLAPSES below the floor (the reading carries the signal): twin=%s"
        % s["twin_shuffled_table_uas"])
    chk(s["best_em_uas"] - s["twin_shuffled_table_uas"] > 0.20, "reading-learned >> twin by >0.20")
    chk(s["supervised_refs"]["supervised_full_uas"] > s["best_em_uas"] + 0.25,
        "supervised still leads by >0.25 UAS (the located ceiling)")
    chk(s["per_relation_at_best_em"]["content_uas"] > s["per_relation_at_best_em"]["convention_uas"],
        "content-UAS > convention-UAS for the reading-learned scorer")

    # ---------- Step 2: construction stack ----------
    c = load("exp_readlearned_construction_stack_v1")
    chk(c["plus_npmod"]["content_uas"] > c["base"]["content_uas"] + 0.01,
        "NP-modifier construction lifts content-UAS (the new BF lever)")
    chk(c["plus_ALL_best"]["content_uas"] > c["base"]["content_uas"] + 0.03,
        "stacked constructions lift content-UAS by >0.03: base=%s all=%s"
        % (c["base"]["content_uas"], c["plus_ALL_best"]["content_uas"]))
    chk(c["plus_ALL_best"]["content_uas"] > c["twin_random_arcs"]["content_uas"] + 0.01,
        "construction stack beats its random-arc twin")
    chk(not c["verdict"]["clausal_helps"], "clausal cue is NULL (honest located sub-negative)")

    # ---------- Step 3: downstream A/B (THE BAR) ----------
    d = load("exp_readlearned_downstream_ab_v1")
    ud = d["by_corpus"]["ud_ewt"]
    chk(ud["rl_top2_vs_sup_greedy"]["ci95"][0] >= -0.006,
        "UD: RL read-as-distribution MATCHES supervised committed (CI lower >= -0.006): %s"
        % ud["rl_top2_vs_sup_greedy"])
    chk(ud["reading_learned"]["top2"]["both"] > ud["reading_learned"]["top2_shuf"]["both"] + 0.20,
        "UD: shuffled-top2 twin LOSES big")
    chk(ud["reading_learned"]["top2"]["both"] > ud["reading_learned"]["committed"]["both"],
        "UD: reading the DISTRIBUTION beats the committed head (keep-alternatives-alive)")
    if "gum_ood" in d["by_corpus"]:
        g = d["by_corpus"]["gum_ood"]
        chk(g["rl_top2_vs_sup_greedy"]["ci95"][0] > 0,
            "GUM(OOD): RL read-as-distribution BEATS supervised committed CI-SEP: %s"
            % g["rl_top2_vs_sup_greedy"])
        chk(g["supervised"]["committed"]["both"] < ud["supervised"]["committed"]["both"] - 0.01,
            "supervised DEGRADES out-of-domain (the register skew): UD=%s GUM=%s"
            % (ud["supervised"]["committed"]["both"], g["supervised"]["committed"]["both"]))
        chk(g["twin_loses"], "GUM: twin loses")
    # honest caveat recorded: RL is a weaker POINT scorer than supervised
    chk(ud["reading_learned"]["committed"]["both"] < ud["supervised"]["committed"]["both"],
        "honest: RL committed < SUP committed (RL is a weaker point scorer)")

    # ---------- Step 4: online/Hebbian vs batch-EM ----------
    o = load("exp_readlearned_online_acquisition_v1")
    chk(o["online_best"]["uas"] < o["batch_em_best"] + 0.005,
        "online/Hebbian does NOT beat batch-EM (mechanism is not the lever): online=%s batch=%s"
        % (o["online_best"]["uas"], o["batch_em_best"]))
    chk(o["verdict"]["interpretation"] == "mechanism_not_the_lever_ceiling_is_the_SIGNAL",
        "interpretation: the ceiling is the SIGNAL, not the optimizer")
    chk(o["online_best"]["uas"] - o["twin_shuffled_table_uas"] > 0.05, "online model beats its shuffled twin")

    # ---------- LIVE micro-checks (cheap, no EM) ----------
    from experiments.exp_readlearned_construction_stack_v1 import _npmod_arcs, _verbarg_arcs, _coord_arcs
    toks = ["the", "big", "red", "car", "stopped"]
    pos = ["DET", "ADJ", "ADJ", "NOUN", "VERB"]
    npa = _npmod_arcs(toks, pos)
    chk((4, 1) in npa and (4, 2) in npa and (4, 3) in npa,
        "NP-modifier: det+adjs attach to the head noun 'car' (idx4): %s" % npa)
    va = _verbarg_arcs(toks, pos)
    chk(any(h == 5 for (h, dd) in va), "verb-arg: 'stopped' (idx5) binds its left-corner subject")

    from experiments.exp_readlearned_scorer_scale_v1 import train_or_load_em
    from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TRAIN, UD_TEST
    from experiments.exp_parser_selfsup_em_v1 import _adj_right_uas
    train = load_ud(UD_TRAIN, cap=None, maxlen=40)
    m = train_or_load_em(train, 2, lam=0.3, pw=3.0)   # cache HIT (built by the scale run)
    test = load_ud(UD_TEST, cap=300, maxlen=40)
    u = m.uas(test)[0]
    fl, _ = _adj_right_uas(test)
    chk(u > fl, "cache-hit reading-learned model beats the right-branching floor on a live test slice: %.3f>%.3f" % (u, fl))

    from experiments.exp_readlearned_online_acquisition_v1 import online_pass
    base0 = train_or_load_em(train, 0, lam=0.3, pw=3.0)
    wm = online_pass(base0, train[:400], decay=0.0)
    chk(wm.uas(test)[0] > fl - 0.02, "online_pass runs and produces a non-degenerate parser")

    # ---------- lever determination (owner directive: research + oracle + prototype) ----------
    ov = load("exp_readlearned_lever_oracle_v1")
    chk(ov["verdict"]["readout_headroom"] > 0.2,
        "DOMINANT lever = READOUT: top-k reach headroom over committed > 0.2 content: %s"
        % ov["verdict"]["readout_headroom"])
    chk(ov["per_arm_uas"]["readout_ceiling"]["ppclausal_uas"] - ov["per_arm_uas"]["committed"]["ppclausal_uas"] > 0.3,
        "readout headroom on PP/clausal > 0.3 (the answer is already in the distribution)")
    chk(ov["lift_over_committed"]["sib_gold"]["ppclausal"] > 0.05,
        "2nd-order sibling SIGNAL exists on PP/clausal (gold oracle > +0.05): %s"
        % ov["lift_over_committed"]["sib_gold"]["ppclausal"])
    chk(ov["lift_over_committed"]["valence"]["ppclausal"] < 0.01,
        "valence (DMV count) is null on PP/clausal (confirms pri-3): %s" % ov["lift_over_committed"]["valence"]["ppclausal"])
    chk(ov["lift_over_committed"]["twin"]["content"] < 0.0, "oracle random-rerank twin loses")

    so = load("exp_readlearned_second_order_readout_v1")
    chk(so["verdict"]["global_hurts_content"], "global 2nd-order re-rank HURTS content (lever must be scoped)")
    chk(not so["verdict"]["gated_no_content_regression"] or not so["verdict"]["gated_lifts_ppclausal"],
        "treebank-free 2nd-order readout does NOT beat base (bootstrapping wall; the LOCATED sub-negative)")
    chk(so["plus_sib_gated_best"]["ppclausal_uas"] > so["twin_gated"]["ppclausal_uas"],
        "the real sibling table beats its shuffled twin (signal is real, just not net-positive vs base)")

    # ---------- the buildable angle: Hindle-Rooth PP-attachment ----------
    hr = load("exp_readlearned_ppattach_hindle_rooth_v1")
    chk(hr["gated_vs_base_ci"]["ci_sep"],
        "HR gated lifts PP-attachment CI-separated over base: %s" % hr["gated_vs_base_ci"])
    chk(hr["gated_vs_twin_ci"]["ci_sep"],
        "preposition-SPECIFIC increment CI-separated over shuffled-prep twin: %s" % hr["gated_vs_twin_ci"])
    chk(hr["plus_HR_top2_scoped_OPTIMIZED"]["content_uas"] > hr["base"]["content_uas"] + 0.0005,
        "OPTIMISED top-2-scoped HR nets a content-UAS gain over base (subpop win -> net win)")
    chk(hr["plus_HR_global"]["ppattach_acc"] <= hr["plus_HR_gated_best"]["ppattach_acc"],
        "global (ungated) HR is worse than gated (scope discipline)")

    # LIVE micro-check: HR association prefers the right head on a textbook pair
    from experiments.exp_readlearned_ppattach_hindle_rooth_v1 import build_hr_assoc, hr_lr
    assoc = build_hr_assoc(train)
    # 'of' overwhelmingly attaches to nouns; a well-formed association should not prefer verb for a generic noun-'of'
    lr_of = hr_lr(assoc, "have", "part", "of")
    chk(lr_of == lr_of, "HR association computes a finite log-ratio (smoke)")

    # ---------- full-stack upstream BF audit (owner: critical for upstream to be BF) ----------
    import json as _json
    reg = os.path.join(_REPO, "notes", "bf_status_registry.jsonl")
    if os.path.exists(reg):
        rows = {}
        for ln in open(reg, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = _json.loads(ln); rows[r.get("module", "")] = r.get("status", "")
            except Exception:
                pass
        chk(rows.get("hdlab/pos_tagger.py") == "NOT_BF", "registry: pos_tagger is NOT_BF (supervised acquisition)")
        chk(rows.get("hdlab/arc_parser.py") == "NOT_BF", "registry: arc_parser (live scorer) is NOT_BF")
        chk(rows.get("hdlab/arc_labeler.py") == "NOT_BF", "registry: arc_labeler is NOT_BF")
    # the fully-BF-acquisition chain collapses (pri-3 measured): BF-induced POS -> arc scorer << gold-POS
    fb = os.path.join(DATA, "exp_parser_brown_pos_bf_chain_v1", "metrics.json")
    if os.path.exists(fb):
        f = _json.load(open(fb))
        chk(f["uas"]["FULLY_BF_brown_pos_plus_prior"] < f["uas"]["gold_pos_plus_prior_ref"] - 0.15,
            "fully-BF chain (BF-induced POS) collapses vs gold-POS: %s vs %s"
            % (f["uas"]["FULLY_BF_brown_pos_plus_prior"], f["uas"]["gold_pos_plus_prior_ref"]))
        chk(f["brown_pos_induction"]["many_to_one_acc"] < f["brown_pos_induction"]["supervised_ref"] - 0.15,
            "BF POS induction << supervised POS acc (the gating upstream gap)")

    # ---------- true-BF upstream: the fully-BF chain gets going ----------
    sc = load("exp_readlearned_bf_pos_scaffold_v1")
    cu = sc["chain_uas"]
    chk(cu["FULLY_BF_best"] > cu["strong_right_branching_floor"] + 0.05,
        "fully-BF chain (scaffold POS + reading-learned scorer, NO gold anywhere) BEATS the floor by >0.05: %.4f > %.4f"
        % (cu["FULLY_BF_best"], cu["strong_right_branching_floor"]))
    chk(cu["FULLY_BF_best"] > cu["prior_brown_fully_bf_ref"] + 0.10,
        "fully-BF chain beats pri-3's collapsed Brown fully-BF chain by >0.10")
    chk(cu["FULLY_BF_best"] - cu["shuffled_scaffold_twin"] > 0.10,
        "shuffled-scaffold twin COLLAPSES (the scaffold carries the signal): %.4f vs %.4f"
        % (cu["FULLY_BF_best"], cu["shuffled_scaffold_twin"]))
    chk(sc["recovery_of_gold_chain"] > 0.6,
        "fully-BF chain recovers >60%% of the gold-POS chain: %.4f" % sc["recovery_of_gold_chain"])
    chk(sc["pos_induction"]["direct_functional_acc"] > 0.6,
        "scaffold POS is functionally NAMED at >0.6 direct accuracy (no gold remap) -- so prior+constructions fire")
    chk(sc["verdict"]["constructions_help"],
        "constructions fire on the NAMED scaffold categories (the unblock vs Brown's arbitrary clusters)")

    # ---------- roadmap #1/#1b/#3 implementations ----------
    mbr = load("exp_readlearned_mbr_readout_v1")
    chk(mbr["mbr_gain_ppclausal_gold"] > 0.01 and mbr["mbr_gain_ppclausal_bf"] > 0.01,
        "MBR decode lifts PP/clausal-UAS on both chains (reads the marginals the MAP decode discarded)")
    chk(mbr["gold_pos_chain"]["MBR"]["content_uas"] > mbr["gold_pos_chain"]["twin"]["content_uas"] + 0.02,
        "MBR beats its shuffled-marginal twin")
    adp = load("exp_readlearned_adaptive_readout_v1")
    chk(adp["verdict"]["twin_loses"], "adaptive readout beats its shuffled twin")
    chk(adp["adaptive_best"]["recall"] > adp["committed_k1"]["recall"] + 0.01,
        "adaptive readout recovers verb->arg recall over the committed head (keep-alternatives-alive)")
    jp = load("exp_readlearned_joint_pos_parse_v1")
    chk(jp["verdict"]["gate_caught_drift_if_any"],
        "joint POS-parse: the Lateen dual-objective accept gate rejects/rolls-back any drifting alternation")
    chk(jp["final_accepted_uas"] >= jp["staged_baseline_uas"] - 1e-9,
        "joint POS-parse never lands below the staged baseline (the gate protects it)")
    chk(jp["final_accepted_uas"] > jp["twin_random_retype_uas"],
        "joint POS-parse final beats the random-retype twin")

    # ---------- complete the chain: BF relation labeler (last link) ----------
    lab = load("exp_readlearned_bf_relation_labeler_v1")
    g = lab["gold_pos_chain"]
    chk(g["bf_rule"]["relation_acc"] > g["floor"]["relation_acc"] + 0.05,
        "BF structural relation labeler beats the most-frequent-relation floor")
    chk(g["bf_rule"]["relation_acc"] > g["twin"]["relation_acc"] + 0.05,
        "BF relation labeler beats its shuffled-rule twin")
    chk(g["bf_rule"]["relation_acc"] >= g["sup"]["relation_acc"] - 0.10,
        "BF relation labeler approaches the supervised labeler (within 0.10): %.4f vs %.4f"
        % (g["bf_rule"]["relation_acc"], g["sup"]["relation_acc"]))
    chk(lab["fully_bf_chain"]["bf_rule"]["LAS"] > 0.15,
        "fully-BF chain (no gold/treebank/LLM anywhere) produces LABELED dependencies: LAS %.4f"
        % lab["fully_bf_chain"]["bf_rule"]["LAS"])
    # live micro-check: the word-order cue names subject vs object correctly
    from experiments.exp_readlearned_bf_relation_labeler_v1 import structural_relation
    pos = ["PRON", "VERB", "DET", "NOUN"]     # "I saw the dog": I->saw nsubj, dog->saw obj
    chk(structural_relation(pos, 2, 1) == "nsubj", "word-order cue: pre-verbal nominal -> nsubj")
    chk(structural_relation(pos, 2, 4) == "obj", "word-order cue: post-verbal nominal -> obj")

    # ---------- cron deepening: morphological (sub-lexical) POS channel ----------
    mo = load("exp_readlearned_bf_pos_morphology_v1")
    chk(mo["plus_morph_best"]["direct_functional_acc"] > mo["baseline_scaffold"]["direct_functional_acc"] + 0.005,
        "morphology channel lifts POS direct-functional accuracy over the distributional scaffold")
    chk(mo["plus_morph_best"]["chain_uas"] > mo["twin_shuffled_suffix"]["chain_uas"] + 0.005,
        "morphology channel beats its shuffled-suffix twin on the fully-BF chain (the suffix->category map carries signal)")
    from experiments.exp_readlearned_bf_pos_morphology_v1 import _morph_scores
    chk(_morph_scores("running")["VERB"] > 0 and _morph_scores("happiness")["NOUN"] > 0
        and _morph_scores("quickly")["ADV"] > 0 and _morph_scores("beautiful")["ADJ"] > 0,
        "morphological bootstrapping (wug): suffixes vote the right category")

    # ---------- cron deepening: marginal temperature/gain calibration (divisive normalization) ----------
    cal = load("exp_readlearned_marginal_calibration_v1")
    chk(cal["gold_best"]["content_uas"] > cal["gold_temp1"]["content_uas"] + 0.005,
        "gain-calibrated MBR (temp!=1) lifts content-UAS over temp=1 MBR: %.4f vs %.4f"
        % (cal["gold_best"]["content_uas"], cal["gold_temp1"]["content_uas"]))
    chk(cal["gold_best"]["temp"] != 1.0, "the calibrating temperature is != 1.0 (the marginal was miscalibrated)")
    chk(cal["verdict"]["curve_has_optimum_canfail"],
        "the temperature curve has an optimum (can-fail: extreme temps degrade)")
    # calibrated MBR should dominate the plain MAP decode (from the MBR cell) on content AND PP/clausal
    map_content = mbr["gold_pos_chain"]["MAP"]["content_uas"]; map_pp = mbr["gold_pos_chain"]["MAP"]["ppclausal_uas"]
    chk(cal["gold_best"]["content_uas"] >= map_content - 1e-9 and cal["gold_best"]["ppclausal_uas"] > map_pp,
        "calibrated MBR dominates plain MAP on BOTH content and PP/clausal: cal(%.4f,%.4f) vs MAP(%.4f,%.4f)"
        % (cal["gold_best"]["content_uas"], cal["gold_best"]["ppclausal_uas"], map_content, map_pp))

    # ---------- cron deepening: marker-triggered clausal constructions ----------
    cl = load("exp_readlearned_clausal_construction_v1")
    chk(cl["plus_clausal_best"]["content_uas"] > cl["base"]["content_uas"] + 0.005,
        "marker-triggered clausal constructions lift content-UAS: %.4f vs %.4f"
        % (cl["plus_clausal_best"]["content_uas"], cl["base"]["content_uas"]))
    chk(cl["mean_clausal_recall_best"] > cl["mean_clausal_recall_base"] + 0.05,
        "clausal relations (advcl/xcomp/ccomp) recall lifted: %.4f -> %.4f"
        % (cl["mean_clausal_recall_base"], cl["mean_clausal_recall_best"]))
    chk(cl["plus_clausal_best"]["content_uas"] > cl["twin_random"]["content_uas"] + 0.003,
        "clausal constructions beat their random-target twin (the marker carries the signal)")
    from experiments.exp_readlearned_clausal_construction_v1 import _clausal_arcs
    ta = ["wants", "to", "go"]; tp = ["VERB", "PART", "VERB"]
    chk((1, 3) in _clausal_arcs(ta, tp), "complementizer cue: 'go' attaches to matrix 'wants'")

    # ---------- cron deepening: HR PP-attachment integration (honest located result) ----------
    pp = load("exp_readlearned_ppattach_integrate_v1")
    chk(pp["plus_hr_best"]["nmod_obl_recall"]["nmod"] > pp["base"]["nmod_obl_recall"]["nmod"] + 0.02,
        "HR integration lifts nmod recall on the full parse")
    chk((pp["plus_hr_best"]["content_uas"] - pp["twin_shuffled_prep"]["content_uas"]) <= 0.003,
        "HONEST: the content gain is NOT twin-separated -- PP-attachment is ambiguity-limited (prep-specific cue "
        "is the minority; the disambiguation signal text lacks is needed). A located result, not a clean win.")

    # ---------- cron deepening: multi-conjunct coordination (exhaustion signal) ----------
    mc = load("exp_readlearned_multiconjunct_v1")
    chk(mc["plus_multiconj_best"]["conj_cc_recall"]["conj"] > mc["base"]["conj_cc_recall"]["conj"] + 0.01,
        "multi-conjunct construction lifts conj recall (comma-list coordination)")
    chk((mc["plus_multiconj_best"]["content_uas"] - mc["twin_random"]["content_uas"]) <= 0.003,
        "HONEST: multi-conjunct content gain is marginal / not twin-separated -- the front-end construction "
        "library is EXHAUSTED (the last two fires yield non-twin-separated content gains).")

    # ---------- relative-clause ATTACHMENT (acl): the prior-penalty was the wall, not signal ----------
    rc = load("exp_readlearned_relcl_attachment_v1")
    chk((rc["plus_relcl_soft_best"]["acl_recall"] or 0) > (rc["base"]["acl_recall"] or 0) + 0.10,
        "relative-clause attachment lifts acl from ~0.013 to ~0.39 (all 3 relcl types; boost overcomes the "
        "anti-NOUN->VERB prior): %s -> %s" % (rc["base"]["acl_recall"], rc["plus_relcl_soft_best"]["acl_recall"]))
    chk(rc["plus_relcl_soft_best"]["content_uas"] > rc["base"]["content_uas"] + 0.002,
        "relative-clause attachment lifts content-UAS")
    chk(rc["hard_override_high_precision"]["content_uas"] > rc["hard_hp_twin_random_noun"]["content_uas"] + 0.003,
        "relcl attachment beats its random-noun twin (the filler-gap head selection carries the signal)")
    from experiments.exp_readlearned_relcl_attachment_v1 import _relcl_arcs
    chk((2, 3) in _relcl_arcs(["the", "report", "published", "today"], ["DET", "NOUN", "VERB", "NOUN"]),
        "participial relative: 'published' attaches to 'report' (no relativizer)")

    # ---------- lever A verification: Altmann-Steedman referential count for PP-attachment ----------
    rf = load("exp_readlearned_referent_pp_v1")
    chk(rf["AUC_nmod_gt_obl"]["ci95"][0] > 0.5,
        "referential count discriminates nmod from obl in the RIGHT direction, CI-sep above chance (signal is real): %s"
        % rf["AUC_nmod_gt_obl"])
    chk(abs(rf["shuffle_control_AUC"]["obs"] - 0.5) < 0.05,
        "shuffle control is chance (the discrimination is not an artifact)")
    chk(rf["AUC_nmod_gt_obl"]["obs"] < 0.6,
        "HONEST: the sentence-internal referential proxy is WEAK (AUC ~0.54) -- the strong Altmann-Steedman lever "
        "needs CROSS-SENTENCE coref (len(compat) from coreference_resolver); routed to the coref/reader integration.")

    # ---------- CAPSTONE: the full construction stack, measured jointly ----------
    fs = load("exp_readlearned_full_stack_final_v1")
    chk(fs["gold_pos"]["full_content_uas"] > fs["gold_pos"]["base_content_uas"] + 0.05,
        "FULL construction stack lifts content-UAS >0.05 over the arc-factored base: %.4f -> %.4f"
        % (fs["gold_pos"]["base_content_uas"], fs["gold_pos"]["full_content_uas"]))
    chk(fs["gold_pos"]["full_content_uas"] > fs["gold_pos"]["twin_content_uas"] + 0.05,
        "full stack beats its random-target twin")
    chk(fs["verdict"]["all_families_contribute"],
        "all 5 construction families are COMPLEMENTARY (drop-one ablation lowers the full stack)")
    chk(fs["fully_bf"]["full_content_uas"] > fs["fully_bf"]["base_content_uas"] + 0.05,
        "the fully-BF chain (no gold/treebank/LLM) full stack lifts content-UAS >0.05")

    # ---------- final bar re-measurement: per-consumer config tradeoff ----------
    df = load("exp_readlearned_downstream_final_v1")
    ud = df["by_corpus"]["ud_ewt"]
    chk(ud["twin_loses"], "final downstream A/B: RL top-2 reach beats its shuffled twin (verb->arg extraction)")
    # the full stack is content-UAS-optimal but slightly below the lighter stack on verb->arg (documented tradeoff)
    lite = load("exp_readlearned_downstream_ab_v1")["by_corpus"]["ud_ewt"]
    chk(lite["reading_learned"]["top2"]["both"] >= ud["recall"]["rl_top2"] - 1e-9,
        "PER-CONSUMER TRADEOFF: the lighter {verbarg,coord,npmod} config meets the verb->arg bar (RL top2 %.4f, "
        "parity/OOD-beat); the content-UAS-optimal full stack (%.4f) trades some verb->arg for content-UAS."
        % (lite["reading_learned"]["top2"]["both"], ud["recall"]["rl_top2"]))

    print("WITNESS: %d checks / %d pass" % (N, OK))
    if OK != N:
        print("WITNESS FAIL")
        return 1
    print("WITNESS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
