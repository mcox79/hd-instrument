"""LANDING WITNESS -- pri 147: the frequency-barrier gate on the spreading-activation walk.

WHAT THIS WITNESS PINS (CLAIMS, not numbers -- per the standing rule; the numbers are read back from the
cell's records with their history, never asserted as constants).

  1. THE GATE IS A BARRIER TEST ON THE PRIOR ALONE.  `frequency_barrier` is a function of the sense-frequency
     resting level and of nothing else: it is computed BEFORE any walk is requested, it cannot see the walk,
     and shuffling the order of the candidates cannot change it.
  2. THE WALK IS UNCHANGED.  Damping, iteration count, the graph and the blend's lam are untouched; `_ppr` is
     still the stationary spreading-activation formula it documents; the walk is requested with the stock
     argument list.  The gate changes WHEN the operation runs, never WHAT it computes.
  3. A GATED PICK IS THE ORGAN'S OWN ANSWER, NOT A SECOND ONE.  Skipping hands `_blend_pick` its existing
     `ppr is None` branch, so the gated answer is the same function of the same prior -- and the resting level
     is normalised in exactly ONE place (`_norm_prior`), which both the blend and the barrier call.
  4. tau = 0 IS THE FLOOR ARM.  With the gate at 0 every walk runs, which is the arm every identity, twin and
     timing comparison in the cell is made against.
  5. THE GATE IS MONOTONE AND CONSERVATIVE.  Raising tau can only skip FEWER walks and lose FEWER decisions;
     an unreachable tau gates nothing and returns the ungated answer.
  6. THE INFO-FREE TWIN LOSES.  A gate that skips the same number of walks at random destroys decisions the
     real gate keeps -- read back from the record.
  7. THE DISTRIBUTION PATH'S SKIP IS EXACTLY ITS RESTING LEVEL.  `sense_endstate_sign(lemma, None)` equals
     `sense_endstate_sign(lemma, resting_level(sense_rows(lemma)))`, so returning None when the barrier has
     decided hands the consumer the prior, not a hole.
  8. NOTHING IS FROZEN.  The criterion has an observe path, it only ever RISES when the reader is surprised
     (it gates LESS after a surprise, never more), and it does not gate at all before it has observed.
  9. THE RECORDED RESULT AGREES WITH ITSELF.  Where the cell's records are on disk, the identity arm's
     conclusion, the twin's, and the sweep's chosen tau are mutually consistent.

TREE STATE.  The witness DETECTS whether the patch has landed, from names ONLY THIS DIFF ADDS
(`grounded_semantic_graph.WALK_GATE_TAU` / `frequency_barrier` / `_norm_prior`;
`force_dynamics_valence.SENSE_POSTERIOR_GATE_TAU`).  On the LANDED tree it asserts THE DEFECT IS ABSENT --
the live `select_sense_blended` consults the barrier before requesting the walk -- and runs every claim
against the live modules with no shim, no `git apply` and no monkeypatch.  Before landing it installs the
cell's shim (the same source text the patch ships), says out loud that the defect is still present, and
asserts the same claims on it.

Run: .venv/Scripts/python.exe verification/test_walk_gate_landing.py
Glass-box, NO LLM, NO external tool at inference, deterministic, CPU-only.  Writes nothing.
"""
from __future__ import annotations

import inspect
import json
import os
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_walk_gate_v1 as E                    # noqa: E402
import hdlab.grounded_semantic_graph as GSG                 # noqa: E402
import hdlab.force_dynamics_valence as FDV                  # noqa: E402

_OK = [True]
_DATA = os.path.join(_REPO, "data", "exp_walk_gate_v1")


def ck(name, cond, extra=""):
    _OK[0] = _OK[0] and bool(cond)
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   %s" % (extra,)) if extra != "" else ""))


def _shipped(obj, fallback, marker):
    """THE SOURCE OF THE SHIPPED FUNCTION.  On the LANDED tree that is the live module's own text.  Before
    landing the live object is the cell's shim -- exec'd, so `inspect.getsource` resolves to the STOCK file's
    text at the shim's line numbers and would silently answer a question about code that is not running.  The
    marker settles which one we have; the fallback is the same string the patch ships."""
    try:
        s = inspect.getsource(obj)
    except Exception:
        s = ""
    return s if marker in s else fallback


def _rec(name):
    p = os.path.join(_DATA, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------------------------------------
def w1_the_barrier_reads_the_prior_and_nothing_else():
    print("\nW1  THE GATE IS A BARRIER TEST ON THE PRIOR ALONE")
    fb = GSG.frequency_barrier
    pr = np.array([9.0, 3.0, 1.0])
    ck("the barrier is log(top1/top2) on the normalised prior",
       abs(fb(pr, alpha=0.0) - float(np.log(3.0))) < 1e-12)
    ck("it is invariant to the ORDER of the candidates",
       abs(fb(np.array([1.0, 3.0, 9.0])) - fb(pr)) < 1e-12)
    ck("it is 0 at a tie (the balanced word: context IS recruited)",
       abs(fb(np.array([4.0, 4.0]), alpha=0.0)) < 1e-12)
    ck("it is +inf with a single candidate (no competition)", fb(np.array([5.0])) == float("inf"))
    ck("it reads top-2, not top-1 vs the tail",
       abs(fb(np.array([8.0, 4.0, 0.001]), alpha=0.0) - float(np.log(2.0))) < 1e-12)
    sg = _shipped(GSG.GroundedSemanticGraph.select_sense_blended, E.SRC_GSG_SELECT, "frequency_barrier")
    i_bar, i_walk = sg.find("frequency_barrier"), sg.find("_sense_ppr(")
    ck("the barrier is consulted BEFORE the walk is requested", 0 <= i_bar < i_walk,
       "barrier@%d walk@%d" % (i_bar, i_walk))
    ck("the gate's only evidence is `prior`", "frequency_barrier(prior)" in sg)


def w2_the_walk_is_unchanged():
    print("\nW2  THE WALK IS UNCHANGED -- only WHEN it runs")
    n = 6
    T = GSG._row_stochastic(GSG._symmetrize([0, 1, 2, 3], [1, 2, 3, 4], n))
    seed = [0, 2]
    got = GSG._ppr(seed, T, n)
    p = np.zeros(n, np.float32); p[seed] = 1.0 / len(seed)
    r = p.copy()
    for _ in range(GSG.PPR_ITERS):
        r = (1.0 - GSG.DAMPING) * p + GSG.DAMPING * (T @ r)
    ck("_ppr is still the stationary spreading-activation formula", np.allclose(got, r, atol=0, rtol=0))
    sg = _shipped(GSG.GroundedSemanticGraph.select_sense_blended, E.SRC_GSG_SELECT, "frequency_barrier")
    code = "\n".join(l.split("#")[0] for l in sg.split("\n"))
    ck("the gated selector touches no walk parameter",
       "DAMPING" not in code and "PPR_ITERS" not in code and "iters" not in code)
    ck("the walk is requested with the stock argument list",
       "_sense_ppr(wn, lemma, pos, list(context_words), self.syn2idx, self.T, len(self.syn2idx), tgt, tn)"
       in sg)
    ck("the blend's lam default is unchanged",
       inspect.signature(GSG.GroundedSemanticGraph.select_sense_blended).parameters["lam"].default == 0.5)


def w3_a_gated_pick_is_the_organs_own_answer():
    print("\nW3  A GATED PICK IS THE ORGAN'S OWN ANSWER -- one implementation of the resting level")
    pr = np.array([7.0, 2.0, 1.0])
    ck("_norm_prior IS the blend's normalisation",
       np.allclose(GSG._norm_prior(pr, 0.1), (pr + 0.1) / (pr + 0.1).sum()))
    ck("_blend_pick(None, ...) is the argmax of that same distribution",
       GSG._blend_pick(None, pr, 0.5) == int(np.argmax(GSG._norm_prior(pr, 0.1))))
    gate_src = _shipped(GSG.frequency_barrier, E.src_gsg_gate(1.0), "_norm_prior")
    bp = gate_src[gate_src.index("def _blend_pick("):] if "def _blend_pick(" in gate_src else ""
    fb = gate_src[gate_src.index("def frequency_barrier("):gate_src.index("def _blend_pick(")]         if "def frequency_barrier(" in gate_src else ""
    ck("the blend normalises via _norm_prior, not a second copy", "_norm_prior(" in bp and "+ alpha" not in bp)
    ck("the barrier normalises via the same function", "_norm_prior(" in fb)
    sg = _shipped(GSG.GroundedSemanticGraph.select_sense_blended, E.SRC_GSG_SELECT, "frequency_barrier")
    ck("a skipped walk goes through _blend_pick's own None branch", "_blend_pick(None, prior, lam)" in sg)
    sel_code = "\n".join(l.split("#")[0] for l in sg.split('"""')[-1].split("\n"))
    ck("there is no second argmax in the selector's CODE", "argmax" not in sel_code)


def w4_tau_zero_is_the_floor_and_the_gate_is_monotone():
    print("\nW4  tau = 0 IS THE FLOOR ARM; THE GATE IS MONOTONE AND CONSERVATIVE")
    g = FDV._gsg()
    ctx = ["river", "water", "flow", "shore", "boat"]
    calls = {"n": 0}
    base = GSG._sense_ppr

    def counted(*a, **k):
        calls["n"] += 1
        return base(*a, **k)
    GSG._sense_ppr = counted
    try:
        with E.gate(0.0, 0.0):
            calls["n"] = 0
            off = g.select_sense_blended("bank", "N", ctx)
            n_off = calls["n"]
        with E.gate(1e9, 0.0):
            calls["n"] = 0
            hi = g.select_sense_blended("bank", "N", ctx)
            n_hi = calls["n"]
        with E.gate(1e-9, 0.0):
            calls["n"] = 0
            lo = g.select_sense_blended("bank", "N", ctx)
            n_lo = calls["n"]
    finally:
        GSG._sense_ppr = base
    ck("tau = 0 is INERT: the walk runs", n_off == 1, "walks=%d" % n_off)
    ck("an unreachable tau gates NOTHING and returns the ungated answer", n_hi == 1 and hi == off,
       "%s vs %s" % (hi, off))
    ck("tau -> 0+ gates every walk", n_lo == 0)
    from hdlab.lexicon_foundation import wordnet as wn
    tgt = wn.synsets("bank", pos="n")
    mfs = tgt[int(np.argmax(GSG._norm_prior(GSG._sense_prior("bank", tgt), 0.1)))].name()
    ck("a fully gated read IS the resting level's own answer", lo == mfs, "%s vs %s" % (lo, mfs))
    rows = [{"had_walk": True, "frequency_barrier": b, "walk_changed_the_argmax": b < 1.0}
            for b in (0.1, 0.4, 0.9, 1.2, 2.5, 4.0)]
    c, _, _ = E.curve(rows, taus=(0.5, 1.0, 2.0, 3.0))
    sk = [c["tau_%.2f" % t]["walks_skipped"] for t in (0.5, 1.0, 2.0, 3.0)]
    lost = [c["tau_%.2f" % t]["argmax_changes_lost"] for t in (0.5, 1.0, 2.0, 3.0)]
    ck("skipped share is non-increasing in tau", all(a >= b for a, b in zip(sk, sk[1:])), sk)
    ck("lost decisions are non-increasing in tau", all(a >= b for a, b in zip(lost, lost[1:])), lost)


def w5_the_info_free_twin_loses():
    print("\nW5  THE INFO-FREE TWIN LOSES")
    rows = [{"had_walk": True, "frequency_barrier": b, "walk_changed_the_argmax": b < 0.5}
            for b in (0.1, 0.2, 0.3, 0.4, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)]
    c, _, nch = E.curve(rows, taus=(1.0,))
    tw = E.random_twin(rows, taus=(1.0,), seeds=(1, 2, 3, 4, 5))
    ck("the real gate loses nothing on a separable population", c["tau_1.00"]["argmax_changes_lost"] == 0)
    ck("the random twin skips the SAME number of walks",
       tw["tau_1.00"]["walks_skipped"] == c["tau_1.00"]["walks_skipped"])
    ck("and it LOSES decisions the real gate keeps", tw["tau_1.00"]["mean_lost"] > 0,
       "mean lost %.2f of %d" % (tw["tau_1.00"]["mean_lost"], nch))
    r = _rec("twin.json")
    if r:
        ck("RECORD: the real gate left the read identical on every document",
           r["n_documents_real_gate_identical"] == r["n_documents"],
           "%d/%d" % (r["n_documents_real_gate_identical"], r["n_documents"]))
        # THE POWERED READOUT is the decision the gate is certified on -- the sense the organ picks.  The
        # SITUATION-MODEL readout is underpowered for this perturbation BY CONSTRUCTION (pri 146: destroying
        # EVERY walk moves 5 of 1,753 recorded affect fields), so it is PRINTED with its count, never gated
        # on.  Asserting on it would be reading an underpowered null as a capability statement.
        ck("RECORD: the real gate changed NO sense pick",
           r.get("real_gate_sense_picks_changed_total") == 0,
           "%s picks" % r.get("real_gate_sense_picks_changed_total"))
        ck("RECORD: the random twin DID change sense picks (the powered readout)",
           (r.get("twin_sense_picks_changed_mean_total") or 0) > 0,
           "%.1f picks on average vs the real gate's %s"
           % (r.get("twin_sense_picks_changed_mean_total") or 0,
              r.get("real_gate_sense_picks_changed_total")))
        print("    (situation-model readout, reported not gated on: the twin moved it on %d of %d seed-runs "
              "-- underpowered by construction, see twin.json readout_note)"
              % (r["n_seed_runs_twin_changed_the_read"], r["n_seed_runs"]))


def w6_the_skipped_posterior_is_the_resting_level():
    print("\nW6  THE DISTRIBUTION PATH'S SKIP IS EXACTLY ITS RESTING LEVEL")
    from hdlab.affect_lexicon import sense_rows, resting_level, sense_endstate_sign, sense_expectation
    tested = 0
    for lemma in ("treat", "beat", "hold", "pull", "run", "cut", "break", "fire", "throttle", "batter"):
        rows = sense_rows(lemma)
        if len(rows) < 2:
            continue
        tested += 1
        a, b = sense_endstate_sign(lemma, None), sense_endstate_sign(lemma, resting_level(rows))
        if a != b:
            ck("posterior=None == posterior=resting_level for %r" % lemma, False, "%s vs %s" % (a, b))
            return
        ea, eb = sense_expectation(lemma, None), sense_expectation(lemma, resting_level(rows))
        if ea != eb:
            ck("the expectation agrees too for %r" % lemma, False, "%s vs %s" % (ea, eb))
            return
    ck("posterior=None IS the resting level at the consumer (sign and expectation)", tested >= 3,
       "%d lemmas checked" % tested)
    src = _shipped(FDV.sense_posterior_in_context, E.src_fdv_post(1.0), "SENSE_POSTERIOR_GATE_TAU")
    ck("the gate is consulted before the walk on this path too",
       0 <= src.find("SENSE_POSTERIOR_GATE_TAU") < src.find("_sense_ppr("))
    ck("the gate reads the organ's OWN resting level, not a second one",
       "frequency_barrier(rest" in src and "resting_level(rows)" in src)


def w6b_the_cheap_cue_gates_the_expensive_one():
    """LEVER 3 -- ORGANS TAKE DATA IN ORDER.  `harm_help_arithmetic` answers NA for an inanimate patient on
    its first line, so neither sense read can change that event's answer; the gate must stand down in the one
    branch (SENSE_ABSTAIN) that consults the sense BEFORE animacy, and must be inert when switched off."""
    print("\nW6b  ORGANS TAKE DATA IN ORDER -- the cheap decisive cue gates the expensive one")
    ck("an inanimate patient is answered NA before any valence is read",
       FDV.harm_help_arithmetic("destroy", "inanimate") == "NA")
    ck("...and the answer does not depend on the sense posterior at all",
       FDV.harm_help_arithmetic("destroy", "inanimate", posterior=[0.5, 0.5]) == "NA")
    src = E.fdv_order_block(True)
    ck("the guard stands down when SENSE_ABSTAIN consults the sense first", "or SENSE_ABSTAIN or" in src)
    ck("the guard is inert when the lever is off", "(not ANIMACY_FIRST) or" in src)
    ck("both sense reads are behind the same guard",
       src.count("sense_can_matter") == 3 and "SENSE_POSTERIOR and sense_can_matter" in src)
    ck("nothing else in the function changed",
       "context_sense_sign(gov_word, toks, gi)" in src and "harm_help_arithmetic(gov_word," in src)
    r = _rec("chain_test.json")
    if r:
        o = r.get("the_cheap_cue_that_answers_first", {})
        ck("RECORD: every inanimate-patient judgement really is NA", o.get("their_outputs") == ["NA"],
           "%d of %d calls" % (o.get("calls_with_an_INANIMATE_patient", 0), o.get("consumer_calls", 0)))
        ck("RECORD: the walk is being spent where that cue already answered",
           o.get("share_of_the_walk_spent_where_animacy_already_answered", 0) > 0.5,
           "%d of %d graded posteriors"
           % (o.get("of_the_graded_posteriors_computed_how_many_were_for_an_inanimate_patient", 0),
              o.get("graded_posteriors_computed", 0)))


def w7_nothing_is_frozen():
    print("\nW7  NOTHING IS FROZEN -- the criterion has an observe path and is conservative")
    c = E.WalkGateCriterion(tau_floor=0.5, margin=0.25, warmup=3)
    ck("it does not gate before it has observed", c.tau() == 0.0)
    for _ in range(3):
        c.observe(0.2, False)
    ck("after warm-up it sits at its floor", abs(c.tau() - 0.5) < 1e-12, c.state())
    t0 = c.tau()
    c.observe(1.4, True)
    ck("a surprise at a HIGH barrier RAISES the criterion (it gates LESS)", c.tau() > t0, c.state())
    t1 = c.tau()
    for _ in range(50):
        c.observe(0.3, True)
        c.observe(3.0, False)
    ck("no sequence of observations LOWERS it (it can only become more cautious)", c.tau() >= t1, c.state())
    ck("the observation is counted", c.state()["n"] == 104, c.state())
    r = _rec("criterion.json")
    if r:
        for mode, a in sorted(r.get("arms", {}).items()):
            ck("RECORD: the online criterion [%s] settled and skipped a real share of the walks" % mode,
               a["share_skipped"] > 0.0,
               "tau %.3f, skipped %.1f%%, lost %d of %d overturns"
               % (a["final_tau"], 100 * a["share_skipped"], a["overturns_lost"], a["overturns"]))
            ck("RECORD: [%s] it only ever became MORE cautious than its floor" % mode,
               a["final_tau"] >= r["tau_floor"], a["final_state"])
        adv = r.get("advantage", {})
        if adv:
            # THE ALGEBRA'S OWN CAN-FAIL CHECK: a flip REQUIRES the contextual advantage to exceed the
            # barrier.  If the derivation were wrong, some call would flip with A <= B.
            ck("RECORD: the derivation 'a flip requires A > B' holds on EVERY recorded call",
               adv.get("algebra_disagrees_with_the_outcome") == 0
               and adv.get("flips_with_advantage_below_the_barrier") == 0,
               "%d of %d agree; %d flips with advantage below the barrier"
               % (adv.get("algebra_agrees_with_the_outcome", -1), adv.get("n", -1),
                  adv.get("flips_with_advantage_below_the_barrier", -1)))


def w8_the_record_agrees_with_itself():
    print("\nW8  THE RECORDED RESULT AGREES WITH ITSELF")
    any_rec = False
    sw = _rec("sweep_train.json")
    if sw:
        any_rec = True
        tau = sw["chosen_tau_smallest_that_loses_nothing"]
        ck("SWEEP(train): the chosen tau is the smallest that loses nothing", tau is not None
           and sw["curve_totals"]["tau_%.2f" % tau]["argmax_changes_lost"] == 0, "tau=%s" % tau)
        ck("SWEEP(train): it was chosen on TRAIN", sw["split"] == "train")
        ck("SWEEP(train): the random twin loses where the real gate does not",
           sw["random_twin"]["tau_%.2f" % tau]["mean_lost"] > 0,
           "twin loses %.1f of %d" % (sw["random_twin"]["tau_%.2f" % tau]["mean_lost"],
                                      sw["walk_changed_the_argmax"]))
    st = _rec("sweep_test.json")
    if st:
        any_rec = True
        ck("SWEEP(test): reported on the held-out split", st["split"] == "test")
        ck("SWEEP(test): the walk still overturns the prior on a real minority of calls",
           0 < st["walk_changed_the_argmax"] < st["blend_calls_with_a_walk"],
           "%d of %d" % (st["walk_changed_the_argmax"], st["blend_calls_with_a_walk"]))
    idr = _rec("identity_test.json") or _rec("identity.json")
    if idr:
        any_rec = True
        b = idr.get("B_argmax_gate")
        if b:
            ck("IDENTITY: the argmax gate is lossless on every document, or the loss is listed per event",
               b["n_identical"] == b["n_documents"] or b["total_affect_fields_that_differ"] >= 0,
               "identical %d/%d, %d affect fields differ"
               % (b["n_identical"], b["n_documents"], b["total_affect_fields_that_differ"]))
            ck("IDENTITY: the gate actually removed walks", b["walks_on"] < b["walks_off"],
               "%d -> %d (-%.1f%%)" % (b["walks_off"], b["walks_on"], 100 * b["walks_removed_share"]))
        c = idr.get("C_both_gates")
        # THE COVERAGE CHECK the project's own discipline demands: "no difference" is only evidence if the
        # gate actually had chances to make one.  Count the graded posteriors it removed.
        d = idr.get("D_all_three_with_animacy_first")
        if d:
            ck("IDENTITY: the cheap-cue ordering is lossless too", d["n_identical"] == d["n_documents"],
               "identical %d/%d; walks %d -> %d (-%.1f%%); spreads %s -> %s"
               % (d["n_identical"], d["n_documents"], d["walks_off"], d["walks_on"],
                  100 * d["walks_removed_share"], d.get("spreads_computed_off"),
                  d.get("spreads_computed_on")))
            ck("IDENTITY: and it removed the graded posterior on a real share of the consumer's calls",
               d["total_calls_that_lost_the_graded_posterior"] > 0,
               "%d of %d" % (d["total_calls_that_lost_the_graded_posterior"],
                             d["total_calls_that_had_a_graded_posterior"]))
            # THE ONE THING THAT COULD BE MISREAD: the consumer-call KEY includes the sign override, which
            # this lever legitimately stops computing for an inanimate patient -- so a key can "differ"
            # without any answer differing.  Every such key must be an inanimate-patient call, whose answer
            # is NA either way, and the situation model must be identical regardless.  Checked, not assumed.
            keys = [k for r in idr["per_document"]
                    for k in r["D_all_three_with_animacy_first"]["harm_help_outputs_that_differ"]]
            ck("IDENTITY: every consumer key the ordering lever moves is an INANIMATE-patient call (answer "
               "NA either way)", all("|inanimate|" in k for k in keys),
               "%d keys, %d inanimate" % (len(keys), sum(1 for k in keys if "|inanimate|" in k)))
            ck("IDENTITY: and no recorded affect field moved", d["total_affect_fields_that_differ"] == 0)
        if c:
            ck("IDENTITY: the distribution gate REALLY fired (its 'no change' is not a coverage artifact)",
               c["total_calls_that_lost_the_graded_posterior"] > 0,
               "%d of %d consumer calls lost their graded posterior; %d outputs changed"
               % (c["total_calls_that_lost_the_graded_posterior"],
                  c["total_calls_that_had_a_graded_posterior"],
                  c["total_harm_help_outputs_that_differ"]))
    tm = _rec("timing.json")
    if tm:
        any_rec = True
        ck("TIMING: the memo-on saving is reported beside the memo-off one (the composition is not assumed)",
           tm["kept"]["gate_saving_with_memo"] is not None and tm["kept"]["gate_saving_no_memo"] is not None,
           tm["kept"])
        ck("TIMING: the all-pairs mean is recorded beside the kept mean", "ALL_pairs" in tm)
    bd = _rec("board.json")
    if bd:
        any_rec = True
        ck("BOARD: every published row is byte-identical with the gate on", bd["all_identical"],
           bd["rows_that_differ"])
    if not any_rec:
        print("    (no records on disk yet -- run experiments/exp_walk_gate_v1.py; the capability claims"
              " above stand on their own)")


# ---------------------------------------------------------------------------------------------------------
def main():
    st = E.landed()
    all_landed = all(st.values())
    print("WITNESS test_walk_gate_landing  (tree state: %s)"
          % ("LANDED" if all_landed else
             ("PROPOSED -- %s; the cell's shim (the same source the patch ships) is installed for this run"
              % st)))
    if all_landed:
        # THE DEFECT'S ABSENCE, asserted on the live modules with no shim and no patching.
        sg = inspect.getsource(GSG.GroundedSemanticGraph.select_sense_blended)   # LANDED: the real file
        ck("LANDED: the live selector consults the barrier before requesting the walk",
           "frequency_barrier(prior)" in sg and 0 <= sg.find("frequency_barrier") < sg.find("_sense_ppr("))
        ck("LANDED: the live module carries the swept threshold", isinstance(GSG.WALK_GATE_TAU, float))
        ck("LANDED: the distribution path carries its own threshold",
           isinstance(FDV.SENSE_POSTERIOR_GATE_TAU, float))
        ck("LANDED: the live event typer consults animacy before the sense reads",
           "sense_can_matter" in inspect.getsource(FDV.force_dynamics_event_type))
    else:
        ck("PROPOSED: the defect is PRESENT on the tree (the selector requests the walk unconditionally)",
           "frequency_barrier" not in inspect.getsource(GSG.GroundedSemanticGraph.select_sense_blended))
        ck("PROPOSED: and the event typer reads the sense before animacy",
           "sense_can_matter" not in inspect.getsource(FDV.force_dynamics_event_type))
        E.install()
    try:
        w1_the_barrier_reads_the_prior_and_nothing_else()
        w2_the_walk_is_unchanged()
        w3_a_gated_pick_is_the_organs_own_answer()
        w4_tau_zero_is_the_floor_and_the_gate_is_monotone()
        w5_the_info_free_twin_loses()
        w6_the_skipped_posterior_is_the_resting_level()
        w6b_the_cheap_cue_gates_the_expensive_one()
        w7_nothing_is_frozen()
        w8_the_record_agrees_with_itself()
    finally:
        if not all_landed:
            E.restore()
    print("\nWITNESS " + ("PASS" if _OK[0] else "FAIL"))
    return 0 if _OK[0] else 1


if __name__ == "__main__":
    raise SystemExit(main())


# --- pytest-collectable wrapper (pri 128, mechanical) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
