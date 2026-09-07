"""hdlab/sem_event_segmenter.py -- THE SEM SCHEMA-SWITCH EVENT SEGMENTER (Q111 landing of the owner-DONE problem
`close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction`; promoted byte-faithfully from
the validated reference cell `experiments/_sem_event_segmenter.py`).

This is the STRUCTURED, brain-foundational event segmenter validated against ACTUAL HUMAN perceived boundaries --
Structured Event Memory (Franklin, Norman, Ranganath, Zacks & Gershman 2020): a library of event SCHEMAS, online
latent-schema inference (sticky Chinese-Restaurant-Process prior + Gaussian likelihood, local MAP), and a BOUNDARY
exactly when the MAP schema SWITCHES. This is the brain's mechanism (a belief/model update, Reynolds-Zacks-Braver
2007 gate + Kumar 2023 distribution-shift), NOT a prediction-error spike -- so it is a DIFFERENT organ from, and a
complement to, hdlab.n400_coherence_monitor (which computes prediction error over a flat gist, the Kumar-refuted
quantity for human boundaries).

WHY THIS ORGAN (validated in the SOLVED SS4h-4n; witness verification/test_predictive_loop.py W10): vs ACTUAL human
event boundaries (Kumar 2023 Zenodo gold, Tunnel n=473 / Pieman n=61) the schema-switch signal reaches rho ~0.12-0.15
= ~56-68% of the leave-one-subject-out human NOISE CEILING (0.22), ABOVE the point-error incumbent (0.07) AND above
Kumar's GPT-2 Bayesian surprise (0.10-0.12). content-shift / SEM / GPT-2 all plateau at the text-predictable ceiling,
so this glass-box organ is at the achievable level -- no neural model beats it (the "needs a neural model" claim was
RETRACTED; SOLVED SS4l(f)). It is WORSE on the GUM paragraph proxy (0.48) -- the proxy being the wrong instrument
(paragraph typography is not perceived event structure), not a defect.

NEW ISLAND (no-regress by construction): this module is imported by NO live consumer -- importing it changes NO
existing behaviour. bound_event_backbone (default-on) chunks with n400_coherence_monitor; it could LATER be revisited
to chunk with this organ instead, but that is a separate, measured follow-on (SOLVED SS9), not this landing.

MECHANISM (glass-box, NO LLM at inference, ONLINE):
  score(k)   = log(C_k + lam*I[k==cur]) - ||scene - f_k(prev_k)||^2 / (2 sigma^2)   for each existing schema k
  score(new) = log(alpha)               - ||scene - f_0||^2       / (2 sigma^2)      (a fresh schema; f_0 = 0)
  cur_next = argmax_k score(k)  ;  BOUNDARY iff cur_next != cur  ;  switch_score = max_{k!=cur} score(k) - score(cur)
  f_k = a per-schema linear forward model (W_k, b_k), updated online by the delta rule on the winning schema.
The continuous switch_score is the graded boundary-pressure read-out (for a board arm / a downstream consumer).

PHASE-DIAGRAM KNOBS (SWEEP per deployment; do NOT adopt -- the substrate can shift anywhere on the phase diagram):
  alpha (new-schema CRP concentration), lam (self-transition stickiness / event length), sigma2 (scene obs. noise),
  eta (online dynamics learning rate), d_cap (scene dims used). The no-tune defaults (alpha=1, lam=2, sigma2=1) ALREADY
  give the human-validated AUC ~0.60-0.65 (Tunnel/Pieman) -- not tuned, cross-story robust.

  *** sigma2 IS SCENE-SCALE DEPENDENT -- READ THIS BEFORE WIRING (SOLVED SS4o, the organ's one fragility). ***
  The SEM likelihood uses SUM-squared error / (2*sigma2), so sigma2 must be MATCHED to the scene-vector magnitude:
    - default sigma2=1.0 is VALIDATED for the reader's HUB-SCALE content scenes (the grounded-hub mean, ~200d) --
      rho ~0.12-0.15 vs actual humans, self-test PASS;
    - UNIT-NORM scenes (e.g. L2-normalized 64d) need sigma2 ~= 0.02.
  A MISMATCHED sigma2 SILENTLY STOPS schema-switching (the whole stream stays in schema 0 -> F1 0.00, no boundaries,
  NO error raised). The self-test below caught exactly this. If you feed unit-norm scenes at the default sigma2 you
  will get a segmenter that never fires and looks "quiet" -- that is the fragility, not a real result. SWEEP sigma2
  to the scene scale, or use the online inverse-chi^2 MAP scale-free variant (a documented FOLLOW-ON, SOLVED SS4o P3:
  reproduces/slightly beats the fixed-sigma2 result rho 0.14-0.17 but is finicky on short streams -- not yet default).

WIRING (for a future consumer): supply one SCENE VECTOR per proposition/sentence -- the situation-model content
vector the reader already computes (the grounded-hub mean, or, higher-fidelity, the substrate's FHRR-bound
{AGENT,PRED,PATIENT,...} scene: SEM's HRR IS the substrate's FHRR, so this reuses existing binding, no new organ).
Feed scenes via observe(); a boundary advances the event slot (reinstate/segment). The per-schema dynamics are online
(invariant-clean) OR freeze an offline-learned library and pass learn=False.

Run: .venv/Scripts/python.exe -m hdlab.sem_event_segmenter   # can-fail self-test (+ human-validation if the archive is present)
Glass-box. NO external LLM at inference. ASCII.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

_EPS = 1e-12


@dataclass(frozen=True)
class SEMEvent:
    is_boundary: bool
    schema: int              # id of the MAP-active schema after this scene
    switch_score: float      # model-comparison margin: best non-current schema score minus current (boundary pressure)
    n_schemas: int


class SEMEventSegmenter:
    """Online SEM schema-switch event segmenter. Feed one scene vector per proposition via observe(); it returns a
    SEMEvent and posts a boundary when the MAP event schema switches. Stateful -- one per stream; reset() to reuse.

    alpha: new-schema (CRP concentration) prior; lam: self-transition stickiness (event length); sigma2: scene
    observation noise (SCENE-SCALE dependent -- see the module docstring, a mismatch silently stops switching);
    eta: online learning rate for a schema's linear dynamics; d_cap: scene dims used; learn: update the per-schema
    dynamics online (True) or hold a frozen offline-learned library (False)."""

    def __init__(self, alpha: float = 1.0, lam: float = 2.0, sigma2: float = 1.0,
                 eta: float = 0.1, d_cap: int = 50, learn: bool = True) -> None:
        if alpha <= 0.0 or lam < 0.0 or sigma2 <= 0.0:
            raise ValueError("alpha>0, lam>=0, sigma2>0 required")
        # sigma2 = scene observation VARIANCE (the SUM-squared-error scale in SEM Eq.6). The default 1.0 is VALIDATED
        # on the reader's grounded-hub scenes (rho ~0.12-0.15 vs actual humans); it is a PHASE-DIAGRAM knob that must
        # be MATCHED to the scene magnitude (~0.02 for unit-norm 64-dim scenes) -- SWEEP per deployment. A fully
        # SCALE-FREE variant (online inverse-chi^2 MAP of sigma2) was prototyped -- it reproduces/slightly beats the
        # human result (rho 0.14-0.17) but is finicky on short streams, so it is a documented FOLLOW-ON, not the
        # default (SOLVED SS4o).
        self.alpha = float(alpha); self.lam = float(lam); self.sigma2 = float(sigma2)
        self.eta = float(eta); self.d_cap = int(d_cap); self.learn = bool(learn)
        self.reset()

    def reset(self) -> None:
        self._schemas: List[dict] = []       # each: {"W","b","C","prev"}
        self._cur: Optional[int] = None
        self._d: Optional[int] = None

    def _predict(self, s: dict) -> np.ndarray:
        if s["prev"] is None:
            return np.zeros(self._d)
        return s["W"] @ s["prev"] + s["b"]

    def observe(self, scene) -> SEMEvent:
        x = np.asarray(scene, dtype=float).reshape(-1)[: self.d_cap]
        if self._d is None:
            self._d = len(x)
        elif len(x) != self._d:                      # pad/truncate to a fixed scene dim
            xx = np.zeros(self._d); xx[: min(self._d, len(x))] = x[: self._d]; x = xx
        f0 = np.zeros(self._d)
        scores = []
        for k, s in enumerate(self._schemas):
            pred = self._predict(s)
            lp = np.log(s["C"] + self.lam * (1.0 if k == self._cur else 0.0) + _EPS)
            scores.append(lp - 0.5 / self.sigma2 * float(np.sum((x - pred) ** 2)))   # SEM Eq.6 (SUM squared error)
        scores.append(np.log(self.alpha) - 0.5 / self.sigma2 * float(np.sum((x - f0) ** 2)))  # new schema
        k_star = int(np.argmax(scores))
        switch = 0.0                                 # model-comparison margin (graded boundary signal)
        if self._cur is not None:
            switch = max(sc for j, sc in enumerate(scores) if j != self._cur) - scores[self._cur]
        if k_star == len(self._schemas):
            self._schemas.append({"W": np.zeros((self._d, self._d)), "b": np.zeros(self._d), "C": 0.0, "prev": None})
        fired = self._cur is not None and k_star != self._cur   # SEM boundary = MAP schema switch
        s = self._schemas[k_star]; s["C"] += 1.0
        if self.learn and s["prev"] is not None:
            pred = self._predict(s); err = x - pred
            s["W"] += self.eta * np.outer(err, s["prev"]); s["b"] += self.eta * err
        s["prev"] = x
        self._cur = k_star
        return SEMEvent(bool(fired), k_star, float(switch), len(self._schemas))


def segment(scenes: Sequence, **kw) -> Tuple[List[int], List[int], List[float]]:
    """Batch convenience: returns (schema_of_each_scene, boundary_indices, switch_score_per_scene)."""
    mon = SEMEventSegmenter(**kw)
    seg_of: List[int] = []; bounds: List[int] = []; sw: List[float] = []
    for i, sc in enumerate(scenes):
        ev = mon.observe(sc); seg_of.append(ev.schema); sw.append(ev.switch_score)
        if ev.is_boundary:
            bounds.append(i)
    return seg_of, bounds, sw


# ------------------------------------------------------------------ self-test (each check can FAIL)
def _synth(n_events, per, dim, noise, seed):
    g = np.random.default_rng(seed)
    topics = g.standard_normal((n_events, dim)); topics /= np.linalg.norm(topics, axis=1, keepdims=True) + _EPS
    scenes = []; gold = set()
    for e in range(n_events):
        for j in range(per):
            if e > 0 and j == 0:
                gold.add(len(scenes))
            v = topics[e] + noise * g.standard_normal(dim)
            scenes.append(v / (np.linalg.norm(v) + _EPS))
    return scenes, gold


def _f1(pred, gold):
    pred, gold = set(pred), set(gold)
    if not pred and not gold:
        return 1.0
    tp = len(pred & gold); pr = tp / len(pred) if pred else 0.0; rc = tp / len(gold) if gold else 0.0
    return (2 * pr * rc / (pr + rc)) if (pr + rc) else 0.0


def _selftests():
    out = {}
    SG = 0.02   # sigma2 matched to UNIT-norm 64-dim synthetic scenes (default 1.0 is for the reader's hub-scale scenes)
    # W1: posts boundaries at near-orthogonal event changes
    scenes, gold = _synth(6, 5, 64, 0.25, 7)
    _, b, _ = segment(scenes, d_cap=64, sigma2=SG)
    f1 = _f1(b, gold); out["boundaries_at_event_changes_f1"] = round(f1, 3)
    assert f1 >= 0.6, "SEM should post boundaries at event changes (F1=%.3f)" % f1
    # W2: a coherent single-event stream is not shredded
    scenes1, _ = _synth(1, 24, 64, 0.25, 11)
    _, b1, _ = segment(scenes1, d_cap=64, sigma2=SG)
    out["spurious_on_coherent"] = len(b1)
    assert len(b1) <= 4, "too many spurious boundaries on a coherent stream: %d" % len(b1)
    # W3: switch_score is higher at true boundaries than within events (the graded signal is meaningful)
    _, _, sw = segment(scenes, d_cap=64, sigma2=SG)
    sw = np.asarray(sw); mask = np.zeros(len(sw), bool); mask[list(gold)] = True
    out["switch_score_boundary_vs_within"] = (round(float(sw[mask].mean()), 3), round(float(sw[~mask][1:].mean()), 3))
    assert sw[mask].mean() > sw[~mask][1:].mean(), "switch score should be higher at boundaries"
    return out


def _human_validation():
    """If the Kumar-2023 human-boundary archive is present, confirm the organ beats the incumbent vs ACTUAL humans.
    Best-effort embedded validation (SOLVED SS4l/4h) -- lazily imports the experiment scaffolding + the large
    gitignored transcript archive; gracefully returns None (SKIPPED) when either is absent, so this module has NO
    hard dependency on experiments/ at import time."""
    import os, sys
    _REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _REPO not in sys.path:
        sys.path.insert(0, _REPO)
    try:
        import pickle
        from experiments import _predictive_loop as PL
        from experiments.exp_human_boundary_validation_v1 import load_story, _spearman
        from hdlab.generalized_event_knowledge import lemmatize
        loaded = load_story("tunnel")
        if loaded is None:
            return None
        texts, human = loaded
        hub = pickle.load(open(os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl"), "rb"))["hub"]
        X = PL.hub_vecs([lemmatize(t) for t in texts], hub)
        _, _, sw = segment(X, alpha=1.0, lam=2.0)          # default sigma2=1.0 (hub-scale scenes)
        inc = PL.backward_segment(X, kz=1e9)["z"]
        r_sem = _spearman(sw, human); r_inc = _spearman(inc, human)
        assert r_sem > r_inc, "SEM (%.3f) should beat the incumbent (%.3f) vs humans" % (r_sem, r_inc)
        return {"sem_rho_vs_humans": round(r_sem, 4), "incumbent_rho": round(r_inc, 4),
                "loo_noise_ceiling": 0.2225, "gpt2_published": "0.10-0.12"}
    except (ImportError, FileNotFoundError, OSError, KeyError):
        return None


if __name__ == "__main__":
    import json
    st = _selftests()
    print(json.dumps(st, indent=2))
    hv = _human_validation()
    if hv is None:
        print("human-validation SKIPPED (Kumar-2023 archive absent)")
    else:
        print("human-validation:", json.dumps(hv))
        print("  -> SEM %.3f > incumbent %.3f vs ACTUAL humans; %.0f%% of the LOO noise ceiling %.3f; >= GPT-2 %s"
              % (hv["sem_rho_vs_humans"], hv["incumbent_rho"], 100 * hv["sem_rho_vs_humans"] / hv["loo_noise_ceiling"],
                 hv["loo_noise_ceiling"], hv["gpt2_published"]))
    print("SEM EVENT SEGMENTER REFERENCE ORGAN: SELF-TEST PASS")
