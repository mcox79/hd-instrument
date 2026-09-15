"""SCAFFOLD-FREE WITNESS for bridging_inference_infer_the_unstated_link_between_adjacent_sentences.
Recomputes every headline from source (the real WordNet/ConceptNet gold + the frozen meaning assets); no
cached metrics are trusted. Runs the four experiment cells' run() (deterministic: digest-seeded splits +
fixed bootstrap seeds) and asserts the load-bearing claims.

  W1  PART antecedent selection (WordNet meronymy): meaning-store relatedness beats the no-inference floor
      CI-separated AND its shuffled-meaning twin collapses to chance.
  W2  PART antecedent selection (ConceptNet PartOf, 2nd source): same.
  W3  INSTRUMENT antecedent selection (ConceptNet UsedFor): same.
  W4  The relatedness signal beats the most-SALIENT-candidate floor (not a salience/frequency artifact).
  W5  LOCATED NEGATIVE: the linear relation-OFFSET selector is a shape artifact (its lift over its own twin
      is far below the raw-relatedness lift -> a relation is not a single linear direction).
  W6  Integration/conditioning lever: salience-discounted (specificity) relatedness beats raw relatedness
      CI-separated on a realistic candidate set that INCLUDES salient distractors (all three types).
  W7  Relation-TYPE selection is TWO-SIDED: the exemplar typer beats chance, but its SEMANTIC contribution
      over the shape twin is small (typing is mostly lexical/structural, not distributional relatedness).
  W8  END-TO-END over a parsed situation model: the conditioned selector beats the recency/no-inference
      floor AND its shuffled twin CI-separated.
  W9  meaning_foundation (the curated LATENT asset) is a strong bridge-selection source (>chance, CI-sep).

Run: .venv/Scripts/python.exe verification/test_bridging_inference.py
"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "2"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.meaning_foundation import dim as mf_dim
from experiments.exp_bridging_selection_v2 import run as run_sel
from experiments.exp_bridging_salience_conditioning_v1 import run as run_cond
from experiments.exp_bridging_type_selection_v1 import run as run_type
from experiments.exp_bridging_discourse_endtoend_v1 import run as run_e2e
from experiments.exp_bridging_signal_loss_ladder_v1 import run as run_ladder
from experiments.exp_bridging_ppr_integration_v1 import run as run_ppr
from experiments.exp_bridging_graded_integration_v1 import run as run_gi
from experiments.exp_bridging_context_modulation_v1 import run as run_cm
from experiments.exp_bridging_structural_typing_v1 import run as run_st
from experiments.exp_bridging_coref_referent_v1 import run as run_cr

P = 0
def check(name, cond, detail=""):
    global P
    assert cond, "FAIL %s -- %s" % (name, detail)
    P += 1
    print("  ok  %s  %s" % (name, detail))

print("=" * 90)
print("WITNESS: bridging inference (construction-integration bridge over the situation model)")
print("=" * 90)

check("W0-assets", mf_dim() == 200, "meaning_foundation dim=200")

sel = run_sel(["part_wn", "part_cn", "instrument"], smoke=False)["per_type"]

def raw_beats(pt, tag):
    d = sel[pt]["headline_deltas"]
    rr = d["RAW_HUB_minus_RANDOM"]["ci"][0]
    rt = d["RAW_HUB_minus_TWIN (load-bearing)"]["ci"][0]
    rs = d["RAW_HUB_minus_SALIENCE"]["ci"][0]
    check(tag + "-vs-random", rr > 0, "RAW-RANDOM CIlo=%.3f" % rr)
    check(tag + "-twin-collapses", rt > 0, "RAW-TWIN CIlo=%.3f" % rt)
    check(tag + "-vs-salience", rs > 0, "RAW-SALIENCE CIlo=%.3f" % rs)
    return d

d_wn = raw_beats("part_wn", "W1-PART-wn")           # W1
raw_beats("part_cn", "W2-PART-cn")                  # W2
raw_beats("instrument", "W3-INSTRUMENT")            # W3
# W4 is folded into the -vs-salience checks above (all three types beat the most-salient floor)
check("W4-salience-floor", sel["part_cn"]["headline_deltas"]["RAW_HUB_minus_SALIENCE"]["ci"][0] > 0.30,
      "PartOf RAW-SALIENCE CIlo=%.3f" % sel["part_cn"]["headline_deltas"]["RAW_HUB_minus_SALIENCE"]["ci"][0])
# W5 located negative: TYPED offset lift over its own twin << RAW lift over its twin
typ_off = d_wn["TYPED_OFFSET_minus_TWIN (should be ~0: negative)"]["d"]
raw_lift = d_wn["RAW_HUB_minus_TWIN (load-bearing)"]["d"]
check("W5-typed-offset-negative", typ_off < 0.10 and typ_off < raw_lift / 3.0,
      "TYPED-TWIN=%.3f << RAW-TWIN=%.3f (shape artifact, not the mechanism)" % (typ_off, raw_lift))
# W9 meaning_foundation strong source
mf_cn = sel["part_cn"]["acc"]["MEAN_FND"]["mean"]
check("W9-meaning-foundation", mf_cn > 0.50, "MEAN_FND(PartOf)=%.3f >> chance 0.20" % mf_cn)

cond = run_cond(["part_wn", "part_cn", "instrument"], smoke=False)["per_type"]
for pt, tag in [("part_wn", "W6-cond-PART-wn"), ("part_cn", "W6-cond-PART-cn"), ("instrument", "W6-cond-INSTR")]:
    lo = cond[pt]["COND_minus_RAW (conditioning lever)"]["ci"][0]
    tw = cond[pt]["COND_minus_TWIN (load-bearing)"]["ci"][0]
    check(tag, lo > 0 and tw > 0, "COND-RAW CIlo=%.3f, COND-TWIN CIlo=%.3f" % (lo, tw))

ty = run_type(smoke=False)
ex = ty["exemplar_acc"]["mean"]; tw = ty["twin_exemplar_acc"]["mean"]; dlo = ty["exemplar_minus_twin"]["ci"][0]
check("W7-type-above-chance", ex > 0.60, "EXEMPLAR type acc=%.3f (chance 0.333)" % ex)
check("W7-type-semantic-weak", dlo > 0 and (ex - tw) < 0.15,
      "EXEMPLAR-TWIN=%.3f CIlo=%.3f (real but small: typing is mostly lexical/structural)" % (ex - tw, dlo))

e2e = run_e2e(smoke=False)
crec = e2e["COND_minus_RECENCY"]["ci"][0]; ctw = e2e["COND_minus_TWIN"]["ci"][0]
check("W8-e2e-vs-recency", crec > 0, "COND-RECENCY CIlo=%.3f (beats no-inference floor)" % crec)
check("W8-e2e-twin", ctw > 0, "COND-TWIN CIlo=%.3f (semantic signal load-bearing end-to-end)" % ctw)

# W10 SIGNAL-LOSS TRACE: the ESTIMATOR is the dominant loss, not the salience confound.
lad = run_ladder(["part_wn", "instrument"], smoke=False)["per_type"]["part_wn"]
L = lad["losses"]
est = L["PERFECT_to_CEIL (estimator intrinsic limit)"]
salc = L["PLAUS_to_SAL (salience confound)"]
check("W10-estimator-dominates", est > 0.40 and est > 6 * abs(salc),
      "estimator loss=%.3f DOMINATES; salience-confound loss=%.3f (population-level, minor)" % (est, salc))

# W11 FIDELITY UPGRADE: the ATL as spreading-activation+distributional (FUSE) beats the static hub, held-out;
# the target-specific spread is load-bearing (random-seed PPR twin collapses to chance).
ppr = run_ppr(["part_wn", "instrument"], smoke=True)["per_type"]
for pt, tag in [("part_wn", "W11-FUSE-PART"), ("instrument", "W11-FUSE-INSTR")]:
    fh = ppr[pt]["FUSE_minus_HUB (graph+distributional)"]["d"]
    pt_tw = ppr[pt]["PPR_minus_TWIN (spread is load-bearing)"]["ci"][0]
    check(tag, fh > 0 and pt_tw > 0, "FUSE-HUB=%.3f (>0), PPR-TWIN CIlo=%.3f (spread load-bearing)" % (fh, pt_tw))
check("W11-PPR-beats-hub-instrument", ppr["instrument"]["PPR_minus_HUB (integration upgrade)"]["ci"][0] > 0,
      "INSTRUMENT PPR-HUB CIlo=%.3f (spreading activation beats static cosine)" % ppr["instrument"]["PPR_minus_HUB (integration upgrade)"]["ci"][0])

# W12 OPTIMIZATION: Competition-Model fusion of ATL cues + ENTROPY-gated SELECTIVE bridging (know-what-you-
# don't-know). The confident subset is far more accurate than blanket, shuffled-confidence twin FLAT.
gi = run_gi(["part_wn", "instrument"], smoke=True)["per_type"]
for pt, tag in [("part_wn", "W12-selective-PART"), ("instrument", "W12-selective-INSTR")]:
    s = gi[pt]["selective_at_50pct"]
    check(tag, s["ci"][0] > 0 and abs(s["twin_delta"]) < 0.05,
          "selective@50 %+.3f CI[%+.3f,%+.3f] vs twin %+.3f (confident subset >> blanket; twin flat)"
          % (s["delta_vs_blanket"], s["ci"][0], s["ci"][1], s["twin_delta"]))
    check(tag + "-combined>=single", gi[pt]["combined_minus_best_single"]["d"] > 0,
          "COMBINED-best_single=%+.3f (multi-cue Competition-Model fusion helps)" % gi[pt]["combined_minus_best_single"]["d"])

# W13 CONTEXT-MODULATION (#4): additive context composition beats the context-free read on ambiguous items,
# twin flat; and the located negatives (multiplicative NOT > additive; sense-resolution weak) hold.
cm = run_cm(smoke=True)
check("W13-context-helps", cm["ADD_minus_RAW"]["ci"][0] > 0 and cm["ADD_minus_TWIN"]["ci"][0] > 0,
      "ADD-RAW CIlo=%.3f, ADD-TWIN CIlo=%.3f (context-modulation recovers the estimator loss; twin flat)"
      % (cm["ADD_minus_RAW"]["ci"][0], cm["ADD_minus_TWIN"]["ci"][0]))
check("W13-multiplicative-negative", cm["MULT_minus_ADD (multiplicative>additive?)"]["ci"][1] < 0.05,
      "MULT-ADD=%.3f CI-hi=%.3f (multiplicative gain does NOT beat additive -- a wall)"
      % (cm["MULT_minus_ADD (multiplicative>additive?)"]["d"], cm["MULT_minus_ADD (multiplicative>additive?)"]["ci"][1]))

# W14 STRUCTURAL TYPING (#7): schema/POS features type the relation far better than distributional, and the
# feature-shuffled twin collapses to CHANCE (all the lift is structural -- confirms 2c: type is not distributional).
st = run_st(smoke=False)
check("W14-structural-typing", st["structural_acc"]["ci"][0] > 0.70 and st["twin_acc"]["ci"][1] < 0.40,
      "structural=%.3f (CIlo %.3f), feature-shuffle twin=%.3f (CIhi %.3f, ~chance) -> typing IS structural"
      % (st["structural_acc"]["mean"], st["structural_acc"]["ci"][0], st["twin_acc"]["mean"], st["twin_acc"]["ci"][1]))

# W15 COREF-REFERENT (#6): a pronoun target is OOV in the meaning store -> SURFACE at chance; resolving to the
# referent recovers the full bridge signal.
cr = run_cr(["part_wn", "instrument"], smoke=False)["per_type"]
for pt, tag in [("part_wn", "W15-coref-PART"), ("instrument", "W15-coref-INSTR")]:
    d = cr[pt]["RESOLVED_minus_SURFACE (coref-referent recovery)"]
    surf = cr[pt]["acc"]["SURFACE"]["mean"]
    check(tag, d["ci"][0] > 0 and surf < 0.25,
          "SURFACE(pronoun)=%.3f ~chance, RESOLVED-SURFACE=%+.3f CIlo=%.3f (referent resolution recovers the bridge)"
          % (surf, d["d"], d["ci"][0]))

print("=" * 90)
print("WITNESS PASS: %d/%d" % (P, P))
print("=" * 90)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
# This file's checks run unconditionally at module import (no `if __name__ ==
# "__main__":` guard) -- already during pytest's COLLECTION, before any test runs.
# A failure already surfaces as a pytest COLLECTION ERROR; this function exists only
# so the discovery gate sees a witness ran here, and does not re-run the checks.
import pytest as _pri128_pytest


@_pri128_pytest.mark.slow
def test_witness():
    assert True
