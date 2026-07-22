"""PUN COHERENCE-ALARM VIABILITY PROBE (v1) -- design-gated, can-fail, LOCAL-ONLY.

PROBE QUESTION (viability gate, NOT chain-grade):
When a pun / ambiguous-in-context noun is composed under the DOMINANT (contextually-WRONG)
sense, does the substrate's SELECTIONAL-FIT coherence channel fire MEASURABLY HIGHER incoherence
than (a) the SAME noun composed under the CORRECT (context-forced, non-dominant) sense, and
(b) CONTROL items where the dominant sense IS correct? If yes -> the incoherence-triggered
RE-SEARCH mechanism (brain drill 2026-07-22) has a usable signal in our substrate -> GREEN-LIGHT
the atomize+sleep composition-learning build. If no -> honest negative; the alarm has nothing to
fire on and the build should not start on this premise.

MECHANISM (glass-box, reuses existing machinery -- does NOT rebuild):
  The substrate's selectional-fit / schema-fit coherence signal = HD cosine between
  (the verb's VerbNet-SELRESTR required-feature target) and (the noun-sense's WordNet-lexname
  feature bundle), transported through a genuine HD bind/unbind schema edge. This is EXACTLY the
  channel built + VET'd in exp_affectedness_typelevel_lookup_verbnet_selrestrs_v1 (VerbNet SELRESTRS
  + WordNet-lexname feature buckets + hdlab.binding.bind/unbind + hdlab.atoms.similarity). Reused
  UNMODIFIED in method; the WordNet-lexname buckets are copied verbatim from
  exp_affectedness_weak_sup_revival_loop_v1 (WN_POS/ANIMATE/BODY_LEXNAMES) and extended by ONE
  documented bucket ("comestible" -> noun.food) that VerbNet's +comestible SELRESTR (drink/eat/
  swallow/feed Patient) actually requires. CREDIT: VerbNet (Kipper-Schuler 2005), Levin 1993,
  WordNet (Princeton), and the two in-house cells above.

DESIGN GATE (per feedback_experiment_design_gate_can_fail_real_baseline_difficulty_on):
  (1) REAL baseline  = the correct-reading coherence AND the control-item coherence (both should be
      HIGH-fit / LOW-incoherence). Not a strawman.
  (2) CAN-FAIL       = the signal might NOT separate. Three independent must-fails guard against a
      by-construction / artifact separation:
        - SCRAMBLE arm: verb->required-feature link deterministically permuted (never hash()); the
          separation MUST collapse (if it persists, the "separation" is an artifact of the sense
          vectors, not the verb-selectional match).
        - CONTROL-coherent: control food nouns under their (correct) dominant reading MUST show LOW
          incoherence (if HIGH, the signal is noise / length, not selectional-fit).
        - CROSS-FEATURE null: scoring the comestible puns against a MISMATCHED required feature
          (animate) MUST NOT separate.
  (3) DIFFICULTY ON  = real English polysemous words, real WordNet sense inventories, real VerbNet
      SELRESTRS. Dominant sense is the WordNet-frequency-ordered synsets()[0] (genuinely the salient
      wrong reading), correct sense is the context-forced subordinate sense.
  (4) ONE VARIABLE   = which sense the composition uses (dominant vs correct). Verb, sentence,
      machinery, atoms held constant.

HARD-PASS (green-light the atomize+sleep build):
  mean incoh(pun-under-dominant-WRONG) - mean incoh(pun-under-correct) >= 0.30
  AND mean incoh(pun-under-dominant-WRONG) - mean incoh(control) >= 0.30
  AND per-item fraction (incoh_dom > incoh_cor) >= 0.70 AND paired sign-test p < 0.05
  AND SCRAMBLE separation <= 0.10 (collapses)
  AND control-coherent: mean incoh(control) <= 0.30.
HARD-FAIL (do NOT build on this premise):
  mean incoh_dom - mean incoh_cor < 0.10 OR per-item fraction < 0.55
  OR scramble does NOT collapse (scramble sep > 0.5 * real sep)
  OR controls incoherent (mean incoh_control > 0.50).
MIDDLE_BAND: otherwise (report + investigate before build).

HONEST SCOPE (do NOT over-claim): a PASS establishes the PREREQUISITE only -- the selectional-fit
alarm channel has a strong usable signal ON THE COVERED SUBSET (verbs with a VerbNet SELRESTR AND
senses that differ in a mapped selectional feature). It does NOT establish arbitrary-pun coverage,
nor that a full re-search loop will work. Coverage (SELRESTR breadth + sense-resolution finer than
coarse WordNet lexnames) is the open risk the full build must extend. This is a viability probe,
expected MEASURED_MECHANISM or honest negative -- NOT a chain-grade.

COMPUTE ARCHITECTURE (mandatory): sequential-CPU with justification -- <= ~30 items, N=1024 FHRR,
  no training loop, no GPU benefit, wall time seconds. Storage: no_storage (measurement cell, no
  PartitionedStore write). final_metrics_atomicity=tmp_replace. crlb_n/a: categorical feature-
  membership readout via FHRR exact single-fact recovery (per exp_single_edge_grounding THEORETICAL);
  no bundle-capacity noise floor applies. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds via
  torch.Generator / np.random.default_rng, never hash()/list(set()) (PROT-023). No scale axis:
  --smoke runs a subset gate, --full runs the whole fixed corpus (DISCRIMINATOR-MUST-SURVIVE-SCALE
  Option A -- no larger-N regime exists; the full corpus IS the discriminator).

LOCAL ONLY. No push / no remote-persist / no queue dispatch. ASCII only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import torch

ANCHOR_NAME = "pun_coherence_alarm_viability_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import atoms as A            # noqa: E402
from hdlab import binding as B          # noqa: E402

try:
    from nltk.corpus import verbnet as vn        # noqa: E402
    vn.classids("eat")
    _VERBNET_AVAILABLE = True
except Exception:
    vn = None
    _VERBNET_AVAILABLE = False

try:
    from nltk.corpus import wordnet as wn        # noqa: E402
    wn.synsets("dog", pos="n")
    _WORDNET_AVAILABLE = True
except Exception:
    wn = None
    _WORDNET_AVAILABLE = False

N_DIM = 1024
SEED = 20260722
SHUFFLE_SEED = 717171
HP_SEP_MIN = 0.30          # HARD-PASS separation floor (dom vs cor; dom vs ctl)
HP_FRAC_MIN = 0.70         # HARD-PASS per-item consistency floor
HP_CTL_INCOH_MAX = 0.30    # controls must be coherent (low incoherence)
HP_SCRAMBLE_MAX = 0.10     # scramble separation must be at/below this
HF_SEP_MAX = 0.10          # HARD-FAIL: real separation below this
HF_FRAC_MAX = 0.55         # HARD-FAIL: per-item consistency below this
HF_CTL_INCOH_MIN = 0.50    # HARD-FAIL: controls incoherent above this

# ==================================================================================================
# WordNet-lexname feature buckets. WN_POS/ANIMATE/BODY_LEXNAMES copied VERBATIM (CREDIT) from
# experiments/exp_affectedness_weak_sup_revival_loop_v1 (verified 2026-07-22); "comestible" added as
# the one documented extension the VerbNet +comestible SELRESTR requires. These map VerbNet SELRESTR
# feature names -> the set of WordNet lexnames that satisfy them (independent boolean features, per
# VerbNet SELRESTR semantics).
# ==================================================================================================
WN_POS_LEXNAMES = {"noun.plant", "noun.object", "noun.artifact", "noun.food", "noun.substance"}
WN_ANIMATE_LEXNAMES = {"noun.animal", "noun.person"}
WN_BODY_LEXNAMES = {"noun.body"}

FEATURE_WN_LEXNAMES = {
    "concrete": WN_POS_LEXNAMES | WN_ANIMATE_LEXNAMES | WN_BODY_LEXNAMES,
    "animate": WN_ANIMATE_LEXNAMES,
    "body_part": WN_BODY_LEXNAMES,
    "organization": {"noun.group"},
    "communication": {"noun.communication"},
    "comestible": {"noun.food"},   # documented extension (VerbNet +comestible SELRESTR)
}
KNOWN_FEATURES = sorted(FEATURE_WN_LEXNAMES)

# VerbNet SELRESTR feature name -> our KNOWN feature key (only the names our buckets map).
VN_FEATURE_MAP = {
    "comestible": "comestible",
    "animate": "animate",
    "organization": "organization",
    "communication": "communication",
    "body_part": "body_part",
    "concrete": "concrete",
}

AFFECTED_ROLE_NAMES = {"Patient", "Patient1", "Patient2", "Theme", "Theme1", "Theme2", "Product"}

# ==================================================================================================
# CURATED ITEM SET. Each pun: an ambiguous noun in the OBJECT (Patient/Theme) role of a +comestible
# verb; the WordNet-dominant sense (synsets()[0]) is NON-food (the salient WRONG reading), the
# context-forced correct sense is the noun.food sense. cor_synset is the ONE human label (the context
# disambiguator, supplied by the sentence author); dom_synset is derived = synsets()[0]. Controls: an
# unambiguous food noun whose dominant sense IS food (composed under its correct dominant reading).
# ==================================================================================================
PUNS = [
    ("port",   "drink",   "port.n.02",       "He drank a small glass of port after dinner."),
    ("turkey", "eat",     "turkey.n.04",     "They ate the turkey with cranberry sauce."),
    ("date",   "eat",     "date.n.08",       "She ate a sticky date from the bowl."),
    ("kiwi",   "eat",     "kiwi.n.03",       "He ate a ripe kiwi for breakfast."),
    ("draft",  "drink",   "draft.n.04",      "He drank a cold draft at the pub."),
    ("bass",   "eat",     "sea_bass.n.01",   "They ate grilled bass by the harbor."),
    ("punch",  "drink",   "punch.n.02",      "She drank the fruit punch at the party."),
    ("squash", "drink",   "squash.n.02",     "He drank a glass of orange squash."),
    ("fig",    "eat",     "fig.n.04",        "She ate a dried fig with cheese."),
    ("chip",   "eat",     "chip.n.04",       "He ate a salty chip from the bag."),
    ("mole",   "eat",     "mole.n.03",       "They ate chicken in dark mole sauce."),
    ("mint",   "eat",     "mint.n.04",       "She ate a mint after the meal."),
    ("roll",   "eat",     "bun.n.01",        "He ate a warm roll with butter."),
    ("sole",   "eat",     "sole.n.02",       "They ate pan-fried sole for supper."),
    ("lime",   "eat",     "lime.n.06",       "She ate a slice of lime with the dish."),
    ("oyster", "eat",     "oyster.n.03",     "He ate a fresh oyster from the shell."),
    ("clam",   "eat",     "clam.n.03",       "They ate steamed clam in broth."),
    ("cod",    "eat",     "cod.n.02",        "She ate battered cod and chips."),
    ("olive",  "eat",     "olive.n.04",      "He ate a green olive from the jar."),
]

CONTROLS = [
    ("apple",  "eat",   "She ate a red apple."),
    ("bread",  "eat",   "He ate fresh bread."),
    ("cheese", "eat",   "They ate sharp cheese."),
    ("soup",   "eat",   "She ate hot soup."),
    ("meat",   "eat",   "He ate roasted meat."),
    ("jam",    "eat",   "She ate toast with jam."),
    ("brie",   "eat",   "He ate a wedge of brie."),
    ("milk",   "drink", "She drank cold milk."),
    ("juice",  "drink", "He drank orange juice."),
    ("tea",    "drink", "They drank green tea."),
    ("wine",   "drink", "She drank red wine."),
]

SMOKE_PUNS = 6
SMOKE_CONTROLS = 4


# ==================================================================================================
# VerbNet SELRESTR lookup (reuses the exact pattern of exp_affectedness_typelevel_lookup..v1).
# ==================================================================================================
def verb_required_features(verb_lemma):
    """Return the sorted set of MAPPED required (+polarity) selectional features on an affected
    (Patient/Theme/Product) role of verb_lemma's VerbNet class. Empty if no coverage. Never guesses."""
    if not _VERBNET_AVAILABLE:
        return []
    try:
        classids = vn.classids(verb_lemma)
    except Exception:
        classids = []
    feats = set()
    for cid in sorted(classids):
        try:
            vc = vn.vnclass(cid)
        except Exception:
            continue
        themroles = vc.find("THEMROLES")
        if themroles is None:
            continue
        for tr in themroles.findall("THEMROLE"):
            if tr.get("type") not in AFFECTED_ROLE_NAMES:
                continue
            selrestrs = tr.find("SELRESTRS")
            if selrestrs is None:
                continue
            for r in selrestrs.findall("SELRESTR"):
                if r.get("Value") == "+":
                    nm = r.get("type")
                    if nm in VN_FEATURE_MAP:
                        feats.add(VN_FEATURE_MAP[nm])
    return sorted(feats)


def synset_lexname(synset_name):
    if not _WORDNET_AVAILABLE:
        return None
    try:
        return wn.synset(synset_name).lexname()
    except Exception:
        return None


def dominant_synset_name(word):
    if not _WORDNET_AVAILABLE:
        return None
    ss = wn.synsets(word, pos="n")
    return ss[0].name() if ss else None


def sense_feature_set(synset_name):
    """Set of KNOWN_FEATURES the synset's WordNet lexname satisfies (honest empty set if none)."""
    lex = synset_lexname(synset_name)
    if lex is None:
        return frozenset()
    return frozenset(f for f, lexset in FEATURE_WN_LEXNAMES.items() if lex in lexset)


# ==================================================================================================
# HD schema-fit coherence (genuine bind/unbind edge + similarity; reuses hdlab UNMODIFIED, per
# exp_single_edge_grounding_hd_binding_verbnet_v1 / exp_affectedness_typelevel_lookup..v1).
# ==================================================================================================
def build_atoms(gen):
    a = {f: A.make_atom_fhrr(N_DIM, gen) for f in KNOWN_FEATURES}
    a["_UNK"] = A.make_atom_fhrr(N_DIM, gen)
    a["_ROLE_OBJ"] = A.make_atom_fhrr(N_DIM, gen)
    a["_VERBKEY"] = A.make_atom_fhrr(N_DIM, gen)
    return a


def bundle(feature_keys, atoms):
    keys = [k for k in feature_keys if k in atoms]
    if not keys:
        return atoms["_UNK"].clone()
    out = atoms[keys[0]].clone()
    for k in keys[1:]:
        out = out + atoms[k]
    return out


def schema_recovered_target(required_features, atoms):
    """WEB = bind(KEY, TARGET), KEY = bind(VERBKEY, ROLE_OBJ), TARGET = bundle(required features).
    recovered = unbind(WEB, KEY) ~ TARGET (FHRR exact single-fact recovery)."""
    key = B.bind(atoms["_VERBKEY"], atoms["_ROLE_OBJ"])
    target = bundle(required_features, atoms)
    web = B.bind(key, target)
    return B.unbind(web, key)


def coherence(required_features, sense_features, atoms):
    """HD selectional-fit coherence: similarity(recovered required-feature target, sense feature
    bundle). ~1.0 if the required selectional feature is in the sense's lexname bucket, ~0 if not."""
    recovered = schema_recovered_target(required_features, atoms)
    sense_vec = bundle(sense_features, atoms)
    return float(A.similarity(recovered, sense_vec))


def incoherence(coh):
    """Map coherence -> incoherence in [0,1]: high fit -> low incoherence."""
    return float(max(0.0, min(1.0, 1.0 - coh)))


# ==================================================================================================
# SIGNAL (b): ATTRACTOR-LANDING / SETTLING-RESIDUAL (USER-requested, second coherence channel).
# Reuses the DAMPED RECURRENT SETTLE DYNAMICS verbatim in method (CREDIT: settle_damped in
# experiments/exp_settling_fix_learned_recurrent_v1.py; Rabovsky/Hansen/McClelland 2018 residual-of-
# change as coherence; Ramsauer et al. 2021 inverse-temperature settle). Idea (USER): encode the
# ambiguous filler under a given reading, let it SETTLE against the substrate codebook, use the
# LANDING SPOT (tail residual / convergence-class) as the incoherence signal. A dominant-WRONG
# reading should stay UNSTABLE / high-residual; correct + controls should settle clean.
#
# PROPORTIONALITY / HONEST SCOPE: the FULL plausibility landscape (17M-token PPMI-SVD codebook) was
# ALREADY measured NULL as a landing-spot coherence readout -- exp_settling_fix_learned_recurrent_v1
# = HARD_FAIL...NULL_GOLD_CORRELATION (rho A=-0.108/B=0.063/C=-0.128/D=-0.030), root cause
# CODEBOOK_GEOMETRY_FORCES_COLLAPSE (word-similarity geometry, not sentence-realism). Rebuilding that
# 368s landscape to reconfirm a KNOWN null over-scopes a viability probe. Instead this runs the SAME
# settle DYNAMICS at probe scale against the substrate's available lexname-feature codebook, on MY
# pun items, to measure directly whether settling-into-a-basin tracks CONTEXTUAL coherence. The
# codebook here is UNSHAPED-by-plausibility (feature atoms), so a NULL separation is EXPECTED and
# INFORMATIVE: it shows the raw landing-spot does not yet encode which basin is CONTEXTUALLY right --
# plausibility-shaping (the atomize+sleep learned glue) is the leap that would make (b) usable.
# ==================================================================================================
SETTLE_BETA = 8.0
SETTLE_ALPHA = 0.25
SETTLE_TMAX = 8
SETTLE_TAILK = 2
SETTLE_CONV_REL_THRESH = 0.05


def _fhrr_normalize(v):
    return v / torch.clamp(torch.sqrt(torch.real(torch.sum(v * torch.conj(v)))), min=1e-8)


def _fhrr_cos(a, b):
    num = float(torch.real(torch.sum(a * torch.conj(b))))
    den = float(torch.clamp(torch.sqrt(torch.real(torch.sum(a * torch.conj(a))))
                            * torch.sqrt(torch.real(torch.sum(b * torch.conj(b)))), min=1e-8))
    return num / den


def settle_residual(filler, role_atom, codebook_list, beta=SETTLE_BETA, alpha=SETTLE_ALPHA,
                    t_max=SETTLE_TMAX):
    """Damped recurrent settle of a single role-filler binding against a codebook (FHRR). Returns the
    per-step residual-of-change trajectory. Same unbind -> softmax-cleanup -> damped-rebind loop as
    settle_damped (credited)."""
    cb = torch.stack(codebook_list, dim=0)                       # [K, N] complex
    s = _fhrr_normalize(B.bind(role_atom, filler))
    residuals = []
    for _t in range(t_max):
        est = B.unbind(s, role_atom)
        est_n = _fhrr_normalize(est)
        sims = torch.real(cb @ torch.conj(est_n)) / cb.shape[1]  # [K] real similarity per codebook atom
        w = torch.softmax(beta * sims, dim=0).to(cb.dtype)
        cleaned = _fhrr_normalize(w @ cb)
        s_next = _fhrr_normalize(B.bind(role_atom, cleaned))
        s_next = _fhrr_normalize(s + alpha * (s_next - s))
        residuals.append(float(1.0 - _fhrr_cos(s_next, s)))
        s = s_next
    return residuals


def _tail_mean(residuals, k=SETTLE_TAILK):
    return float(np.mean(residuals[-k:]))


def _iters_to_converge(residuals, rel_thresh=SETTLE_CONV_REL_THRESH):
    r0 = residuals[0]
    if r0 <= 0:
        return 1
    thresh = rel_thresh * r0
    for i, r in enumerate(residuals):
        if r <= thresh:
            return i + 1
    return len(residuals) + 1


def evaluate_settling(puns, controls, atoms):
    """Signal (b): settle each reading's filler; report tail residual + convergence class. Codebook =
    all lexname-feature atoms + _UNK (every sense has a home basin; UNSHAPED by plausibility)."""
    codebook = [atoms[f] for f in KNOWN_FEATURES] + [atoms["_UNK"]]
    role = atoms["_ROLE_OBJ"]

    def filler_for(feat_set):
        return _fhrr_normalize(bundle(sorted(feat_set) if feat_set else ["_UNK"], atoms))

    pun_rows = []
    for word, verb, cor_name, _ in puns:
        dom_feats = sense_feature_set(dominant_synset_name(word))
        cor_feats = sense_feature_set(cor_name)
        res_dom = settle_residual(filler_for(dom_feats), role, codebook)
        res_cor = settle_residual(filler_for(cor_feats), role, codebook)
        pun_rows.append({
            "word": word,
            "tail_resid_dom": round(_tail_mean(res_dom), 6), "tail_resid_cor": round(_tail_mean(res_cor), 6),
            "iters_dom": _iters_to_converge(res_dom), "iters_cor": _iters_to_converge(res_cor),
            "settle_sep": round(_tail_mean(res_dom) - _tail_mean(res_cor), 6),
        })
    ctl_rows = []
    for word, verb, _ in controls:
        dom_feats = sense_feature_set(dominant_synset_name(word))
        res = settle_residual(filler_for(dom_feats), role, codebook)
        ctl_rows.append({"word": word, "tail_resid": round(_tail_mean(res), 6),
                         "iters": _iters_to_converge(res)})
    return pun_rows, ctl_rows


def summarize_settling(pun_rows, ctl_rows):
    seps = np.array([r["settle_sep"] for r in pun_rows], dtype=float)
    td = np.array([r["tail_resid_dom"] for r in pun_rows], dtype=float)
    tc = np.array([r["tail_resid_cor"] for r in pun_rows], dtype=float)
    tctl = np.array([r["tail_resid"] for r in ctl_rows], dtype=float)
    frac = float(np.mean(seps > 0)) if len(seps) else 0.0
    n_pos, n_eff, p = sign_test_p(list(seps))
    mean_sep = float(np.mean(seps)) if len(seps) else 0.0
    # SETTLING SEPARATES only if a real, consistent, significant residual gap dom>cor emerges.
    separates = (mean_sep >= 0.05 and frac >= 0.70 and p < 0.05)
    return {
        "mean_tail_resid_dominant_WRONG": round(float(np.mean(td)) if len(td) else 0.0, 6),
        "mean_tail_resid_correct": round(float(np.mean(tc)) if len(tc) else 0.0, 6),
        "mean_tail_resid_control": round(float(np.mean(tctl)) if len(tctl) else 0.0, 6),
        "mean_settle_separation_dom_minus_cor": round(mean_sep, 6),
        "per_item_frac_dom_gt_cor": round(frac, 4),
        "sign_test_p_two_sided": round(p, 8),
        "settling_separates": bool(separates),
        "readout_note": ("settling-residual SEPARATES puns" if separates else
                         "settling-residual NULL (does not separate dominant-wrong from correct) -- "
                         "consistent with exp_settling_fix_learned_recurrent_v1 "
                         "CODEBOOK_GEOMETRY_FORCES_COLLAPSE; landing-in-a-basin != contextual coherence; "
                         "plausibility-landscape-shaping (atomize+sleep learned glue) is the follow-on leap"),
        "prior_art_on_disk": {
            "cell": "exp_settling_fix_learned_recurrent_v1",
            "verdict": "HARD_FAIL_3_GRADED_BUT_NOT_MEANINGFUL_NULL_GOLD_CORRELATION",
            "landing_spot_rho_vs_plausibility_gold": {"A": -0.108, "B": 0.063, "C": -0.128, "D": -0.030},
            "note": "MEASURED@data/settling_fix_learned_recurrent_v1/metrics.json -- raw settling "
                    "landing-spot NULL vs plausibility gold; mechanism graded (fitted_beta=3.0) but "
                    "landscape unshaped by plausibility.",
        },
    }


# ==================================================================================================
# Evaluation.
# ==================================================================================================
def scramble_feature(true_feat, atoms_pool, item_idx):
    """Deterministic WRONG feature assignment (seeded; never hash()). Picks a KNOWN feature != the
    true one from the pool so the verb->feature link is genuinely broken."""
    rng = np.random.default_rng(SHUFFLE_SEED + item_idx)
    choices = [f for f in atoms_pool if f != true_feat and f != "concrete"]
    return choices[int(rng.integers(0, len(choices)))]


def evaluate(puns, controls, gen):
    atoms = build_atoms(gen)
    feature_pool = [f for f in KNOWN_FEATURES]

    pun_rows = []
    for i, (word, verb, cor_name, sentence) in enumerate(puns):
        req = verb_required_features(verb)             # VerbNet-derived (glass-box), e.g. ["comestible"]
        dom_name = dominant_synset_name(word)
        dom_feats = sense_feature_set(dom_name)
        cor_feats = sense_feature_set(cor_name)

        coh_dom = coherence(req, dom_feats, atoms)
        coh_cor = coherence(req, cor_feats, atoms)
        incoh_dom = incoherence(coh_dom)
        incoh_cor = incoherence(coh_cor)

        # SCRAMBLE must-fail: broken verb->feature link.
        true_feat = req[0] if req else "_UNK"
        scr_feat = scramble_feature(true_feat, feature_pool, i)
        coh_dom_scr = coherence([scr_feat], dom_feats, atoms)
        coh_cor_scr = coherence([scr_feat], cor_feats, atoms)

        # CROSS-FEATURE null: score against a fixed mismatched feature (animate).
        coh_dom_xf = coherence(["animate"], dom_feats, atoms)
        coh_cor_xf = coherence(["animate"], cor_feats, atoms)

        pun_rows.append({
            "word": word, "verb": verb, "req_features": req,
            "dom_synset": dom_name, "dom_lexname": synset_lexname(dom_name), "dom_features": sorted(dom_feats),
            "cor_synset": cor_name, "cor_lexname": synset_lexname(cor_name), "cor_features": sorted(cor_feats),
            "coh_dom": round(coh_dom, 4), "coh_cor": round(coh_cor, 4),
            "incoh_dom": round(incoh_dom, 4), "incoh_cor": round(incoh_cor, 4),
            "sep": round(incoh_dom - incoh_cor, 4),
            "scr_feat": scr_feat,
            "incoh_dom_scr": round(incoherence(coh_dom_scr), 4), "incoh_cor_scr": round(incoherence(coh_cor_scr), 4),
            "sep_scr": round(incoherence(coh_dom_scr) - incoherence(coh_cor_scr), 4),
            "incoh_dom_xf": round(incoherence(coh_dom_xf), 4), "incoh_cor_xf": round(incoherence(coh_cor_xf), 4),
            "sep_xf": round(incoherence(coh_dom_xf) - incoherence(coh_cor_xf), 4),
        })

    ctl_rows = []
    for (word, verb, sentence) in controls:
        req = verb_required_features(verb)
        dom_name = dominant_synset_name(word)
        dom_feats = sense_feature_set(dom_name)
        coh = coherence(req, dom_feats, atoms)
        ctl_rows.append({
            "word": word, "verb": verb, "req_features": req,
            "dom_synset": dom_name, "dom_lexname": synset_lexname(dom_name), "dom_features": sorted(dom_feats),
            "coh": round(coh, 4), "incoh": round(incoherence(coh), 4),
        })
    return pun_rows, ctl_rows, atoms


def sign_test_p(deltas):
    """Two-sided sign test that median delta != 0 (exact binomial vs p=0.5 on positive count,
    ignoring exact zeros). Returns (n_pos, n_eff, p_two_sided)."""
    nz = [d for d in deltas if abs(d) > 1e-9]
    n = len(nz)
    if n == 0:
        return 0, 0, 1.0
    k = sum(1 for d in nz if d > 0)
    # exact two-sided binomial p via symmetric tail
    from math import comb
    def tail_ge(x):
        return sum(comb(n, j) for j in range(x, n + 1)) / (2.0 ** n)
    x = max(k, n - k)
    p = min(1.0, 2.0 * tail_ge(x))
    return k, n, p


def summarize(pun_rows, ctl_rows):
    incoh_dom = np.array([r["incoh_dom"] for r in pun_rows], dtype=float)
    incoh_cor = np.array([r["incoh_cor"] for r in pun_rows], dtype=float)
    incoh_ctl = np.array([r["incoh"] for r in ctl_rows], dtype=float)
    seps = incoh_dom - incoh_cor
    sep_scr = np.array([r["sep_scr"] for r in pun_rows], dtype=float)
    sep_xf = np.array([r["sep_xf"] for r in pun_rows], dtype=float)

    n_pos, n_eff, p = sign_test_p(list(seps))
    frac_pos = float(np.mean(seps > 0)) if len(seps) else 0.0

    m_dom = float(np.mean(incoh_dom)) if len(incoh_dom) else 0.0
    m_cor = float(np.mean(incoh_cor)) if len(incoh_cor) else 0.0
    m_ctl = float(np.mean(incoh_ctl)) if len(incoh_ctl) else 0.0
    sep_dom_cor = m_dom - m_cor
    sep_dom_ctl = m_dom - m_ctl
    m_scr = float(np.mean(sep_scr)) if len(sep_scr) else 0.0
    m_xf = float(np.mean(sep_xf)) if len(sep_xf) else 0.0
    return {
        "n_puns": len(pun_rows), "n_controls": len(ctl_rows),
        "mean_incoh_dominant_WRONG": round(m_dom, 4),
        "mean_incoh_correct": round(m_cor, 4),
        "mean_incoh_control": round(m_ctl, 4),
        "sep_dom_minus_cor": round(sep_dom_cor, 4),
        "sep_dom_minus_ctl": round(sep_dom_ctl, 4),
        "per_item_frac_dom_gt_cor": round(frac_pos, 4),
        "sign_test_n_pos": n_pos, "sign_test_n_eff": n_eff, "sign_test_p_two_sided": round(p, 8),
        "scramble_mean_separation": round(m_scr, 4),
        "crossfeature_null_mean_separation": round(m_xf, 4),
        "real_separation_effect": round(sep_dom_cor, 4),
    }


def build_verdict(summ):
    reasons = []
    hp = (summ["sep_dom_minus_cor"] >= HP_SEP_MIN
          and summ["sep_dom_minus_ctl"] >= HP_SEP_MIN
          and summ["per_item_frac_dom_gt_cor"] >= HP_FRAC_MIN
          and summ["sign_test_p_two_sided"] < 0.05
          and summ["scramble_mean_separation"] <= HP_SCRAMBLE_MAX
          and summ["mean_incoh_control"] <= HP_CTL_INCOH_MAX)
    hf = (summ["sep_dom_minus_cor"] < HF_SEP_MAX
          or summ["per_item_frac_dom_gt_cor"] < HF_FRAC_MAX
          or (summ["real_separation_effect"] > 1e-9
              and summ["scramble_mean_separation"] > 0.5 * summ["real_separation_effect"])
          or summ["mean_incoh_control"] > HF_CTL_INCOH_MIN)

    if hp and not hf:
        verdict = "HARD_PASS"
        reasons.append("GREEN-LIGHT: selectional-fit coherence alarm separates dominant-wrong from "
                       "correct AND control; scramble collapses; controls coherent.")
    elif hf:
        verdict = "HARD_FAIL"
        if summ["sep_dom_minus_cor"] < HF_SEP_MAX:
            reasons.append("no separation (dom-cor < %.2f)" % HF_SEP_MAX)
        if summ["per_item_frac_dom_gt_cor"] < HF_FRAC_MAX:
            reasons.append("per-item consistency below coin (%.2f)" % HF_FRAC_MAX)
        if (summ["real_separation_effect"] > 1e-9
                and summ["scramble_mean_separation"] > 0.5 * summ["real_separation_effect"]):
            reasons.append("scramble did NOT collapse -> separation is an artifact")
        if summ["mean_incoh_control"] > HF_CTL_INCOH_MIN:
            reasons.append("controls incoherent -> signal is noise/length")
    else:
        verdict = "MIDDLE_BAND"
        reasons.append("partial separation; investigate before build")

    msg = (f"{verdict} | incoh dom_WRONG={summ['mean_incoh_dominant_WRONG']} "
           f"cor={summ['mean_incoh_correct']} ctl={summ['mean_incoh_control']} | "
           f"sep(dom-cor)={summ['sep_dom_minus_cor']} sep(dom-ctl)={summ['sep_dom_minus_ctl']} "
           f"frac={summ['per_item_frac_dom_gt_cor']} p={summ['sign_test_p_two_sided']} | "
           f"scramble_sep={summ['scramble_mean_separation']} xfeat_sep={summ['crossfeature_null_mean_separation']} "
           f"| {'; '.join(reasons)}")
    return verdict, msg


def arms_differ(pun_rows):
    """META_RULE_AF: the real vs scramble vs cross-feature separation vectors must not be bit-identical."""
    def digest(key):
        b = np.array([r[key] for r in pun_rows], dtype=np.float64).tobytes()
        return hashlib.sha256(b).hexdigest()
    d_real, d_scr, d_xf = digest("sep"), digest("sep_scr"), digest("sep_xf")
    assert d_real != d_scr, "META_RULE_AF: real and scramble separation bit-identical"
    return {"sep_real": d_real, "sep_scramble": d_scr, "sep_crossfeature": d_xf}


# ==================================================================================================
# IO + crash handling (per cell-template mandates).
# ==================================================================================================
def _out_dir(mode):
    sub = ANCHOR_NAME + ("_smoke" if mode == "smoke" else "")
    d = os.path.join(REPO_ROOT, "data", "exp_" + sub)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, mode, n_units):
    import platform
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "expected_n_units": n_units,
              "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def write_metrics(output_dir, payload):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(mode)
    if mode == "smoke":
        puns, controls = PUNS[:SMOKE_PUNS], CONTROLS[:SMOKE_CONTROLS]
    else:
        puns, controls = PUNS, CONTROLS
    _write_start_marker(output_dir, mode, len(puns) + len(controls))

    if not (_VERBNET_AVAILABLE and _WORDNET_AVAILABLE):
        payload = {"verdict": "HARD_FAIL", "verdict_msg": "VerbNet/WordNet unavailable (NLTK corpora missing)",
                   "summary": "corpora_unavailable", "elapsed_s": round(time.perf_counter() - t0, 3),
                   "anchor_name": ANCHOR_NAME, "verbnet_available": _VERBNET_AVAILABLE,
                   "wordnet_available": _WORDNET_AVAILABLE}
        write_metrics(output_dir, payload)
        return payload

    gen = torch.Generator().manual_seed(SEED)
    pun_rows, ctl_rows, atoms = evaluate(puns, controls, gen)
    digests = arms_differ(pun_rows)
    summ = summarize(pun_rows, ctl_rows)
    verdict, msg = build_verdict(summ)

    # Signal (b): attractor-landing / settling-residual (reported SEPARATELY; does not gate verdict).
    settle_pun_rows, settle_ctl_rows = evaluate_settling(puns, controls, atoms)
    summ_settle = summarize_settling(settle_pun_rows, settle_ctl_rows)

    payload = {
        "verdict": verdict, "verdict_msg": msg, "summary": verdict, "anchor_name": ANCHOR_NAME,
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - t0, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "N_DIM": N_DIM, "seed": SEED, "verbnet_available": True, "wordnet_available": True,
        "bands": {"HP_SEP_MIN": HP_SEP_MIN, "HP_FRAC_MIN": HP_FRAC_MIN,
                  "HP_CTL_INCOH_MAX": HP_CTL_INCOH_MAX, "HP_SCRAMBLE_MAX": HP_SCRAMBLE_MAX,
                  "HF_SEP_MAX": HF_SEP_MAX, "HF_FRAC_MAX": HF_FRAC_MAX, "HF_CTL_INCOH_MIN": HF_CTL_INCOH_MIN},
        "summary_metrics": summ,
        "summary_metrics_settling_signal_b": summ_settle,
        "arms_differ_digests": digests,
        "pun_rows": pun_rows, "control_rows": ctl_rows,
        "settling_pun_rows": settle_pun_rows, "settling_control_rows": settle_ctl_rows,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": "sequential_cpu_seconds_no_storage",
    }
    write_metrics(output_dir, payload)
    return payload


# ==================================================================================================
# Self-test: real substrate objects + validity of the manipulation + discriminator fires.
# ==================================================================================================
def self_test():
    assert _VERBNET_AVAILABLE, "VerbNet unavailable"
    assert _WORDNET_AVAILABLE, "WordNet unavailable"

    # F.1 real code path: construct real hdlab atoms + bind/unbind at tiny scale.
    g = torch.Generator().manual_seed(1)
    a = A.make_atom_fhrr(16, g)
    b = A.make_atom_fhrr(16, g)
    w = B.bind(a, b)
    rec = B.unbind(w, b)
    assert float(A.similarity(rec, a)) > 0.9, "bind/unbind roundtrip broken"

    # VerbNet derives +comestible for eat/drink Patient (glass-box, not hand-set).
    assert "comestible" in verb_required_features("eat"), "eat lost +comestible SELRESTR"
    assert "comestible" in verb_required_features("drink"), "drink lost +comestible SELRESTR"

    # Manipulation validity: for every pun, dominant lexname != noun.food AND correct lexname == noun.food
    # AND dom_synset != cor_synset (the ONE variable is genuinely toggled).
    for word, verb, cor_name, _ in PUNS:
        dom = dominant_synset_name(word)
        assert dom is not None and dom != cor_name, f"{word}: dominant==correct or missing"
        assert synset_lexname(dom) != "noun.food", f"{word}: dominant sense is already food (not a pun)"
        assert synset_lexname(cor_name) == "noun.food", f"{word}: correct sense {cor_name} not noun.food"

    # Controls: dominant sense IS food (correct under dominant reading).
    for word, verb, _ in CONTROLS:
        dom = dominant_synset_name(word)
        assert synset_lexname(dom) == "noun.food", f"control {word}: dominant sense not food"

    # Discriminator fires on a spot item (port): correct-reading coherence high, dominant-wrong low.
    gen = torch.Generator().manual_seed(SEED)
    atoms = build_atoms(gen)
    req = verb_required_features("drink")
    coh_cor = coherence(req, sense_feature_set("port.n.02"), atoms)
    coh_dom = coherence(req, sense_feature_set(dominant_synset_name("port")), atoms)
    assert coh_cor - coh_dom > 0.5, f"port discriminator did not fire: cor={coh_cor:.3f} dom={coh_dom:.3f}"

    # Scramble collapses on port.
    scr = scramble_feature("comestible", KNOWN_FEATURES, 0)
    coh_cor_scr = coherence([scr], sense_feature_set("port.n.02"), atoms)
    coh_dom_scr = coherence([scr], sense_feature_set(dominant_synset_name("port")), atoms)
    assert abs(coh_cor_scr - coh_dom_scr) < 0.2, "scramble did not collapse on port"

    # arms differ on a mini eval.
    pr, cr, at = evaluate(PUNS[:SMOKE_PUNS], CONTROLS[:SMOKE_CONTROLS], torch.Generator().manual_seed(SEED))
    arms_differ(pr)

    # Signal (b) settle dynamics run + produce finite residuals (does not assert a separation direction).
    sp, sc = evaluate_settling(PUNS[:SMOKE_PUNS], CONTROLS[:SMOKE_CONTROLS], at)
    assert all(np.isfinite(r["tail_resid_dom"]) and np.isfinite(r["tail_resid_cor"]) for r in sp), \
        "settling residual non-finite"

    print(f"[self-test PASS] eat_req={verb_required_features('eat')} "
          f"port cor_coh={coh_cor:.3f} dom_coh={coh_dom:.3f} sep={coh_cor - coh_dom:.3f} "
          f"scramble_collapse_ok verbnet={_VERBNET_AVAILABLE} wordnet={_WORDNET_AVAILABLE}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return
    if args.smoke:
        p = run_mode("smoke")
    elif args.full:
        p = run_mode("full")
    else:
        p = run_mode("full")
    print(p["verdict_msg"])
    sb = p.get("summary_metrics_settling_signal_b")
    if sb:
        print(f"[signal-b settling] tail_resid dom_WRONG={sb['mean_tail_resid_dominant_WRONG']} "
              f"cor={sb['mean_tail_resid_correct']} ctl={sb['mean_tail_resid_control']} "
              f"sep={sb['mean_settle_separation_dom_minus_cor']} separates={sb['settling_separates']}")


if __name__ == "__main__":
    _od = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
