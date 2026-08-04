"""exp_disequilibrium_novelty_signal_test_v1

Decisive-DIRECTION test (n=18, underpowered): does a signal an EXISTING organ already computes
separate "needs a genuinely-new causal-role schema" from "fits an existing schema slot"? If yes,
the schema-minting trigger is a cheap routing action; if no, a dedicated novelty-detector must be
built first.

Cites notes/research_self_extending_grounded_knowledge_prior_art_2026-08-04.md parts (b)/(c)/(h).
Prereg: preregs/exp_disequilibrium_novelty_signal_test_v1.md.

TWO signals (both reuse existing organs verbatim; NO new mechanism):
  PRIMARY (brain-faithful): hdlab.predictive_coding prediction-error RESIDUAL MAGNITUDE. The
    current situation-model schema library is Hebbian-encoded into W (native causal-schema
    templates as autoassociative fixed points); each item's causal structure is the observed
    pattern; residual = how unexplained the item is by the library (CA1 match-mismatch signal).
  SECONDARY (the note's original): the situation_model_accumulate / self_improving_loop FHRR
    coherence-margin of a cause-attribution decode under FIXED vs EXTENDED role vocabulary.

Labels are BLIND to both signals (assigned from causal structure only, fixed in the ITEMS table
below before any signal is computed). n=18 tiny; construction caveat: the item->feature typing is
Director-supplied (see prereg / report).

ASCII-only. Deterministic. Writes data/exp_disequilibrium_novelty_signal_test_v1/metrics.json.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import torch
from scipy.stats import mannwhitneyu

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import predictive_coding as pc
from hdlab.situation_model_accumulate import (
    unit_phase_vec,
    cleanup_argmax,
)
from hdlab import binding, bundling

N = 1024
SEEDS = list(range(30))
OUT_DIR = os.path.join(REPO, "data", "exp_disequilibrium_novelty_signal_test_v1")

# --------------------------------------------------------------------------------------------------
# ITEMS (n=18). label BLIND to both signals -- assigned from causal structure only.
# features: causal-account feature atoms. NATIVE = the current vocab can express it; NON_NATIVE =
# it cannot (the library lacks a role for it). fine_type is documentary.
# Each dict: id, label, fine_type, features, causal_justification (flagged for Director review).
# --------------------------------------------------------------------------------------------------
NATIVE_FEATURES = [
    "AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION",
    "TRANSFER", "INSTRUMENT", "HARM_OUTCOME", "HELP_OUTCOME",
]
NON_NATIVE_FEATURES = [
    "OMISSION", "DECEPTION", "SOCIAL_INSTIGATION", "COUNTERFACTUAL", "NO_PHYSICAL_ACT",
]
ALL_FEATURES = NATIVE_FEATURES + NON_NATIVE_FEATURES

# Native schema templates the current library stores (autoassociative fixed points in W).
NATIVE_TEMPLATES = {
    "physical_harm": ["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
    "physical_help": ["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HELP_OUTCOME"],
    "theft":         ["AGENT", "TRANSFER", "DIRECT_CAUSATION"],
    "instrument":    ["AGENT", "INSTRUMENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
    "accident":      ["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION"],
}

ITEMS = [
    dict(id="grapp_mcca_001", label="fits_existing", fine_type="direct_physical",
         features=["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
         causal_justification="Injun Joe drove the knife into the victim's breast -- direct agentive physical killing; representable as agent-CAUSE-EFFECT."),
    dict(id="grapp_mcca_003", label="needs_new", fine_type="deception",
         features=["AGENT", "DECEPTION", "HARM_OUTCOME"],
         causal_justification="Laurie FORGED the mock love-letter -- the cause is a misrepresentation/deception act, no distinct role in the current vocab."),
    dict(id="grapp_mcca_004", label="needs_new", fine_type="omission",
         features=["AGENT", "OMISSION", "NO_PHYSICAL_ACT", "HARM_OUTCOME"],
         causal_justification="Jo deliberately WITHHELD Laurie's warning from Amy -- a failure-to-act (omission) is the cause; no physical act; vocab has no omission role."),
    dict(id="grapp_mcca_005", label="fits_existing", fine_type="direct_physical",
         features=["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION"],
         causal_justification="Sid's fingers slipped and the bowl dropped and broke -- direct physical causation (accidental agentive act)."),
    dict(id="grapp_mcca_006", label="needs_new", fine_type="omission_inadvertent",
         features=["OMISSION", "NO_PHYSICAL_ACT", "COUNTERFACTUAL"],
         causal_justification="Marilla's own forgetfulness -- brooch caught unnoticed in her shawl; inadvertent non-act, no agentive physical cause of the 'loss'."),
    dict(id="grapp_mcca_007", label="needs_new", fine_type="social_indirect",
         features=["AGENT", "SOCIAL_INSTIGATION", "OMISSION", "HARM_OUTCOME"],
         causal_justification="Marilla mis-stored the cordial so Anne UNKNOWINGLY served wine -- harm via an unwitting intermediary + a storage mistake; indirect/omission causation."),
    dict(id="grapp_mcca_008", label="fits_existing", fine_type="direct_physical",
         features=["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
         causal_justification="Alfred Temple poured ink on Tom's spelling-book -- direct agentive physical act (property harm)."),
    dict(id="grapp_mcca_009", label="fits_existing", fine_type="direct_physical",
         features=["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION"],
         causal_justification="Becky accidentally tore the page while startled -- direct physical causation."),
    dict(id="crossspan_det_001", label="fits_existing", fine_type="direct_physical",
         features=["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
         causal_justification="John Turner killed McCarthy to silence blackmail -- direct agentive physical killing (motive complex, act direct)."),
    dict(id="crossspan_det_002", label="needs_new", fine_type="deception_framing",
         features=["AGENT", "TRANSFER", "DECEPTION", "HARM_OUTCOME"],
         causal_justification="James Ryder stole the gem AND FRAMED Horner -- identifying the true cause hinges on the deliberate framing (misrepresentation), not just the theft."),
    dict(id="crossspan_det_003", label="needs_new", fine_type="social_collusion",
         features=["AGENT", "TRANSFER", "SOCIAL_INSTIGATION", "COUNTERFACTUAL"],
         causal_justification="Mary + secret lover Burnwell colluded to steal; Arthur broke the coronet FIGHTING to stop them -- social instigation + counterfactual (damage arose from prevention)."),
    dict(id="crossspan_det_004", label="fits_existing", fine_type="instrument",
         features=["AGENT", "INSTRUMENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
         causal_justification="Dr. Roylott killed Julia via a trained swamp adder through the ventilator -- agentive killing via an instrument (instrument-mediated, native)."),
    dict(id="crossspan_det_005", label="needs_new", fine_type="counterfactual_disguise",
         features=["DECEPTION", "COUNTERFACTUAL", "NO_PHYSICAL_ACT"],
         causal_justification="Neville St. Clair disguised himself as beggar Boone -- NO crime occurred; counterfactual (feared murder never happened) + disguise/deception."),
    dict(id="crossspan_det_006", label="needs_new", fine_type="counterfactual_selfcaused",
         features=["COUNTERFACTUAL", "SOCIAL_INSTIGATION", "PHYSICAL_ACT", "HARM_OUTCOME"],
         causal_justification="Silver Blaze kicked Straker in fright during Straker's OWN attempt to lame it -- non-agentive animal reaction, self-provoked; counterfactual (victim's own scheme killed him)."),
    dict(id="crossspan_det_007", label="needs_new", fine_type="counterfactual_natural",
         features=["COUNTERFACTUAL", "NO_PHYSICAL_ACT", "HARM_OUTCOME"],
         causal_justification="Colonel Barclay died of apoplexy from guilt/shock on being confronted -- no one struck him; non-agentive/counterfactual death."),
    dict(id="crossspan_det_008", label="fits_existing", fine_type="theft",
         features=["AGENT", "TRANSFER", "DIRECT_CAUSATION"],
         causal_justification="Joseph Harrison impulsively pocketed the treaty from an empty office -- direct theft (agent takes theme), representable."),
    dict(id="crossspan_det_009", label="needs_new", fine_type="deception_staging",
         features=["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "DECEPTION", "HARM_OUTCOME"],
         causal_justification="The gang strangled Blessington then STAGED a suicide -- defeating the salient suicide reading requires representing the staging (misrepresentation); physical+deception mix."),
    dict(id="crossspan_det_010", label="needs_new", fine_type="counterfactual_freewill",
         features=["COUNTERFACTUAL", "NO_PHYSICAL_ACT", "SOCIAL_INSTIGATION"],
         causal_justification="Hatty Doran left of her own free will on seeing her secret first husband -- no abduction (counterfactual); the Flora-Millar kidnapping theory is false."),
]


def _feature_atoms(seed):
    """Fixed bipolar +-1 atom per feature name, seeded (RandomState -> reproducible)."""
    rng = np.random.RandomState(seed)
    return {f: rng.choice([-1.0, 1.0], size=N).astype(np.float64) for f in ALL_FEATURES}


def _bundle_bipolar(atoms, names):
    """Majority-sign bundle of the named bipolar atoms (ties -> +1)."""
    acc = np.sum([atoms[n] for n in names], axis=0)
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _build_library_W(atoms):
    """Hebbian autoassociative memory over the native schema templates = the current library."""
    W = np.zeros((N, N), dtype=np.float64)
    for _tname, feats in sorted(NATIVE_TEMPLATES.items()):
        t = _bundle_bipolar(atoms, feats)
        pc.vanilla_hebbian_write(W, t, t)  # value=key=t : store as fixed point
    return W


def signal_residual(item, seed):
    """PRIMARY: prediction-error residual magnitude of the item vs the schema library W."""
    atoms = _feature_atoms(seed)
    W = _build_library_W(atoms)
    obs = _bundle_bipolar(atoms, item["features"])
    pred = pc.predict(W, obs, sign_cleanup=True)
    return pc.residual_magnitude(obs, pred)


# --------------------------------------------------------------------------------------------------
# SECONDARY: FHRR cause-attribution coherence-margin (reuses situation_model_accumulate primitives).
# --------------------------------------------------------------------------------------------------
BASE_ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "CAUSE", "EFFECT", "suspect"]
FRESH_ROLES = ["r_omission", "r_deception", "r_social", "r_counterfactual"]
N_OTHER_FILLERS = 4


def _fine_to_fresh_role(item):
    ft = item["fine_type"]
    if "omission" in ft:
        return "r_omission"
    if "deception" in ft:
        return "r_deception"
    if "social" in ft:
        return "r_social"
    if "counterfactual" in ft:
        return "r_counterfactual"
    return "r_counterfactual"


def signal_coherence_margin(item, seed, condition):
    """FHRR cause-attribution decode margin (top1-vs-runner-up over fillers), reusing the
    situation_model organ primitives. condition in {fixed, extended}.

    OUTCOME register bundles bind(role_of_candidate, filler_candidate) for the true cause (TB) and
    the distractor (DS). Decode the TRUE cause by unbind(true_role) then cleanup over fillers.
      fixed vocab: non-native true cause force-fit to CAUSE; its distractor also collapses to CAUSE
        (the vocab cannot distinguish true-vs-apparent cause for non-physical types) -> collision.
      extended vocab: true cause gets its own fresh role; distractor stays 'suspect'.
    Native (fits) items: true=CAUSE, distractor='suspect' in BOTH conditions (no collision).
    """
    gen = torch.Generator().manual_seed(seed)
    role_vocab = BASE_ROLE_VOCAB + FRESH_ROLES
    role_vecs = {r: unit_phase_vec(N, gen) for r in role_vocab}
    fillers = ["TB", "DS"] + [f"O{i}" for i in range(N_OTHER_FILLERS)]
    filler_vecs = {f: unit_phase_vec(N, gen) for f in fillers}

    native = item["label"] == "fits_existing"
    if native:
        true_role, dist_role = "CAUSE", "suspect"
    else:
        if condition == "fixed":
            true_role, dist_role = "CAUSE", "CAUSE"          # collapse -> collision
        else:
            true_role, dist_role = _fine_to_fresh_role(item), "suspect"

    reg = bundling.bundle(torch.stack([
        binding.bind(role_vecs[true_role], filler_vecs["TB"]),
        binding.bind(role_vecs[dist_role], filler_vecs["DS"]),
    ], dim=0))
    readback = binding.unbind(reg, role_vecs[true_role])
    _best, scores = cleanup_argmax(readback, filler_vecs)
    tb = scores["TB"]
    runner = max(v for k, v in scores.items() if k != "TB")
    return tb - runner  # margin: high = confident true-cause attribution; low = ambiguous


def _class_split(per_item, key):
    fits = sorted(v[key] for v in per_item if v["label"] == "fits_existing")
    needs = sorted(v[key] for v in per_item if v["label"] == "needs_new")
    return fits, needs


def _iqr(vals):
    if not vals:
        return (float("nan"), float("nan"))
    return (float(np.percentile(vals, 25)), float(np.percentile(vals, 75)))


def _iqr_overlap_frac(a, b):
    """Fraction overlap of the two IQR intervals relative to the smaller interval width."""
    a_lo, a_hi = _iqr(a)
    b_lo, b_hi = _iqr(b)
    inter = max(0.0, min(a_hi, b_hi) - max(a_lo, b_lo))
    wa, wb = a_hi - a_lo, b_hi - b_lo
    denom = min(wa, wb)
    if denom <= 1e-12:
        return 0.0 if inter <= 1e-12 else 1.0
    return inter / denom


def _verdict(fits, needs, high_class_is_needs, name):
    """Apply pre-registered bands. high_class_is_needs: True if needs_new should score HIGHER."""
    mean_fits, mean_needs = float(np.mean(fits)), float(np.mean(needs))
    mean_gap = mean_needs - mean_fits if high_class_is_needs else mean_fits - mean_needs
    overlap = _iqr_overlap_frac(fits, needs)
    alt = "greater" if high_class_is_needs else "less"
    # test: needs vs fits in the predicted direction
    try:
        U, p = mannwhitneyu(needs, fits, alternative=alt)
        p_two = mannwhitneyu(needs, fits, alternative="two-sided")[1]
    except ValueError:
        U, p, p_two = float("nan"), float("nan"), float("nan")
    non_overlap = overlap < 1e-9
    if mean_gap >= 0.05 and non_overlap:
        v = "HARD_PASS"
    elif p_two > 0.10:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE"
    return dict(
        signal=name, mean_fits=mean_fits, mean_needs=mean_needs, mean_gap=mean_gap,
        iqr_fits=_iqr(fits), iqr_needs=_iqr(needs), iqr_overlap_frac=overlap,
        mann_whitney_U=float(U), p_directional=float(p), p_two_sided=float(p_two),
        n_fits=len(fits), n_needs=len(needs), verdict=v,
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    per_item = []
    for item in ITEMS:
        res = [signal_residual(item, s) for s in SEEDS]
        cm_fixed = [signal_coherence_margin(item, s, "fixed") for s in SEEDS]
        cm_ext = [signal_coherence_margin(item, s, "extended") for s in SEEDS]
        per_item.append(dict(
            id=item["id"], label=item["label"], fine_type=item["fine_type"],
            features=item["features"], causal_justification=item["causal_justification"],
            residual_mean=float(np.mean(res)), residual_std=float(np.std(res)),
            coh_margin_fixed_mean=float(np.mean(cm_fixed)),
            coh_margin_ext_mean=float(np.mean(cm_ext)),
            coh_margin_delta_mean=float(np.mean(cm_ext) - np.mean(cm_fixed)),
        ))

    # PRIMARY: residual (needs_new should be HIGH)
    f_res, n_res = _class_split(per_item, "residual_mean")
    v_res = _verdict(f_res, n_res, high_class_is_needs=True, name="predictive_coding_residual")

    # SECONDARY a: coherence-margin under FIXED vocab (needs_new should be LOW)
    f_cf, n_cf = _class_split(per_item, "coh_margin_fixed_mean")
    v_cf = _verdict(f_cf, n_cf, high_class_is_needs=False, name="coherence_margin_fixed_vocab")

    # SECONDARY b: coherence-margin DELTA extended-minus-fixed (needs_new should be HIGH)
    f_cd, n_cd = _class_split(per_item, "coh_margin_delta_mean")
    v_cd = _verdict(f_cd, n_cd, high_class_is_needs=True, name="coherence_margin_delta_ext_minus_fixed")

    def overall(v):
        return v["verdict"]

    two_signal = dict(
        primary_brain_faithful_residual=overall(v_res),
        secondary_coherence_margin_fixed=overall(v_cf),
        secondary_coherence_margin_delta=overall(v_cd),
    )

    metrics = dict(
        experiment="exp_disequilibrium_novelty_signal_test_v1",
        cites="notes/research_self_extending_grounded_knowledge_prior_art_2026-08-04.md (b)/(c)/(h)",
        n_items=len(ITEMS), N=N, n_seeds=len(SEEDS),
        n_fits=len(f_res), n_needs=len(n_res),
        current_role_vocabulary=dict(
            situation_model_semantic=["agent", "patient", "theme", "recipient", "addressee", "speaker"],
            causal_meta=["CAUSE", "EFFECT"],
            anne_read=["agent", "mentioned"],
            note="no distinct causal-role TYPE for bribe/omission/deception/counterfactual/social",
        ),
        native_schema_templates=NATIVE_TEMPLATES,
        bands=dict(HARD_PASS="mean_gap>=0.05 AND non-overlapping IQR",
                   HARD_FAIL="MW two-sided p>0.10", MIDDLE="otherwise"),
        verdicts=dict(residual=v_res, coherence_margin_fixed=v_cf, coherence_margin_delta=v_cd),
        two_signal_summary=two_signal,
        per_item=per_item,
        caveats=[
            "n=18 tiny + underpowered -- decisive-DIRECTION only, not a powered claim.",
            "CONSTRUCTION CAVEAT: item->feature-set / native-vs-non-native typing is Director-supplied; "
            "a separation shows the organ can SCORE novelty GIVEN a faithful typing, not that it "
            "produces the typing autonomously (that gap is itself decision-relevant).",
            "Labels BLIND to both signals (assigned from causal structure before any signal computed).",
        ],
    )
    path = os.path.join(OUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, path)
    print("WROTE", path)
    print("PRIMARY residual verdict:", v_res["verdict"],
          f"(gap={v_res['mean_gap']:.4f} fits={v_res['mean_fits']:.4f} needs={v_res['mean_needs']:.4f} "
          f"p2={v_res['p_two_sided']:.4f} iqr_overlap={v_res['iqr_overlap_frac']:.3f})")
    print("SECONDARY coh_margin_fixed verdict:", v_cf["verdict"],
          f"(gap={v_cf['mean_gap']:.4f} fits={v_cf['mean_fits']:.4f} needs={v_cf['mean_needs']:.4f} "
          f"p2={v_cf['p_two_sided']:.4f} iqr_overlap={v_cf['iqr_overlap_frac']:.3f})")
    print("SECONDARY coh_margin_delta verdict:", v_cd["verdict"],
          f"(gap={v_cd['mean_gap']:.4f} p2={v_cd['p_two_sided']:.4f})")


if __name__ == "__main__":
    main()
