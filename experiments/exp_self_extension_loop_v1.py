"""exp_self_extension_loop_v1 -- the FIRST integrated self-extension loop.

Can the substrate MINT a new causal-role type ('goal-blocker') from READING, triggered by a
prediction-error residual against its current schema library (hdlab.predictive_coding, the validated
mint TRIGGER -- exp_disequilibrium_novelty_signal_test_v1 residual gap 0.27 p=3e-4) and DISPOSED by a
STRUCTURALLY-INDEPENDENT second view, WITHOUT drifting, and does re-reading after minting improve
goal-blocking attribution?

THE LOOP (glass-box, on goal-directedness):
  read -> TYPE the passage's causal structure to a feature-atom bundle (grounded lexical typer;
  reuses hdlab.coreference_resolver.normalize_tokens) -> NOVELTY GATE (hdlab.predictive_coding.
  threshold_gate on the residual vs the seed schema library W) -> if novel, MINT a candidate new
  causal-role type from the passage's unexplained features (Carey placeholder; hippocampal fast
  pattern-separated bind) -> SECOND INDEPENDENT VIEW (discourse/purpose-connective cue presence, a
  disjoint function-word class) disposes -> CONSOLIDATE into W only on >=2 cross-confirmations that
  clear hdlab.self_improving_loop.decide_keep_or_revert's abstain band (neocortical slow
  consolidation; NELL multi-cycle agreement) -> re-read.

BRAIN STRUCTURES:
  novelty/mint trigger = VTA-dopamine RPE + cortical predictive coding (Rao-Ballard/Friston) +
    hippocampal-mPFC schema-incongruity (van Kesteren 2012); MINT = hippocampal fast pattern-
    separated binding (CLS, McClelland 1995).
  second independent view = left IFG/pMTG discourse-connective / purpose processing (Do/Chan/Roth
    2011 causal cues) -- structurally distinct extractor; coupling = NELL CPL "promotion requires an
    independent view" (WSDM 2010).
  consolidation gate = ACC/PFC conflict-monitoring control (self_improving_loop) + neocortical slow
    interleaved consolidation.

Cites notes/brain_component_functional_map_2026-08-04.md;
notes/research_self_extending_grounded_knowledge_prior_art_2026-08-04.md (a/e/h);
exp_disequilibrium_novelty_signal_test_v1.
Prereg: preregs/2026-08-04_self_extension_loop_v1.md. Local-only: no queue/remote/push.
ASCII-only. Deterministic. Multi-seed. Resumable per-seed.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "self_extension_loop_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED VERBATIM: the validated novelty/prediction-error organ (the mint TRIGGER) ----------
from hdlab import predictive_coding as pc  # noqa: E402
# ---- REUSED VERBATIM: the situation-model relational tokenizer (typer input) -------------------
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
# ---- REUSED VERBATIM: the abstain-band promote controller (consolidation gate) -----------------
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
N = 1024
SEEDS = list(range(8))
EXPECTED_N_SEEDS = len(SEEDS)
RESIDUAL_THRESHOLD = 0.25   # pre-registered (calibration: harm~0.05 | goal_block~0.42 | noise~0.47)
MIN_CONFIRM = 2             # >=2 cross-confirmations before promotion (anti single-pass drift)
K_SYNTH = 8                 # synthetic passages per class

# ---- feature-atom vocabulary --------------------------------------------------------------------
NATIVE_FEATURES = ["AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME",
                   "HELP_OUTCOME", "TRANSFER", "INSTRUMENT"]
GOAL_FEATURES = ["GOAL_OWNER", "GOAL_OBJECT", "BLOCK_ACT", "GOAL_UNMET"]
NOISE_FEATURES = ["WEATHER", "MOTION", "SCENERY"]
ALL_FEATURES = NATIVE_FEATURES + GOAL_FEATURES + NOISE_FEATURES

# ---- seed schema library: ONLY harm/physical templates (no goal-blocking type) ------------------
SEED_TEMPLATES = {
    "physical_harm": ["AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
    "physical_help": ["AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HELP_OUTCOME"],
    "theft":         ["AGENT", "TRANSFER"],
    "instrument":    ["AGENT", "INSTRUMENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
    "accident":      ["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION"],
}

# ============================================================================ the grounded typer
# View-1 CONTENT lexicons (supplied ~6yo grounded world-knowledge; glass-box; no proper nouns).
PHYS_ACT = {"drove", "drive", "stab", "stabbed", "hit", "struck", "strike", "broke", "break",
            "dropped", "drop", "tore", "tear", "poured", "pour", "spilled", "spill", "smashed",
            "smash", "knife", "slapped", "slap", "kicked", "kick", "beat"}
HARM_OUT = {"killed", "kill", "dead", "broke", "broken", "hurt", "wounded", "drowned", "ruined",
            "spoiled", "torn", "bled", "slain"}
HELP_OUT = {"saved", "save", "rescued", "rescue", "healed", "comforted", "mended"}
PATIENT_W = {"man", "boy", "girl", "breast", "body", "head", "bowl", "page", "book", "ink",
             "letter", "dish", "child", "victim", "arm"}
TRANSFER_W = {"stole", "steal", "took", "pocketed", "snatched", "snatch", "grabbed", "seized"}
INSTRUMENT_W = {"knife", "adder", "poker", "stick", "rope", "gun", "hilt"}
GOAL_OBJ_W = {"warned", "warning", "warn", "safe", "safety", "care", "protect", "rescue", "reach",
              "win", "help", "told"}
BLOCK_W = {"withheld", "withhold", "refused", "refuse", "ignored", "ignore", "neglected", "neglect",
           "prevented", "prevent", "kept", "hid", "concealed", "denied", "let"}
GOAL_UNMET_W = {"down", "fell", "drowned", "failed", "lost", "missed", "late", "sank"}
WEATHER_W = {"warm", "cold", "spell", "snap", "frost", "wind", "sun", "rain", "mist", "chill"}
MOTION_W = {"drifted", "drift", "glided", "glide", "skating", "skated", "moved", "sounding",
            "floated", "along", "past"}
SCENERY_W = {"ice", "field", "sky", "hill", "trees", "river", "meadow", "bank", "path", "shore"}

# NOTE: some tokens live in two content lexicons (knife=PHYS_ACT+INSTRUMENT, shore~GOAL_OBJ). This is
# fine -- View 1 is the CONTENT typer. View 2 (below) uses a DISJOINT function/connective word class.


def _tokens(text: str):
    return normalize_tokens(text)


def type_passage(text: str):
    """View 1: grounded lexical typer -> a set of causal-structure feature atoms."""
    t = _tokens(text)
    feats = set()
    has_act = bool(t & PHYS_ACT)
    has_block = bool(t & BLOCK_W)
    has_transfer = bool(t & TRANSFER_W)
    if has_act:
        feats.add("PHYSICAL_ACT")
    if t & HARM_OUT:
        feats.add("HARM_OUTCOME")
    if t & HELP_OUT:
        feats.add("HELP_OUTCOME")
    if t & PATIENT_W:
        feats.add("PATIENT")
    if t & TRANSFER_W:
        feats.add("TRANSFER")
    if t & INSTRUMENT_W:
        feats.add("INSTRUMENT")
    if t & GOAL_OBJ_W:
        feats.add("GOAL_OBJECT")
    if has_block:
        feats.add("BLOCK_ACT")
    if t & GOAL_UNMET_W:
        feats.add("GOAL_UNMET")
    if "PHYSICAL_ACT" in feats and "PATIENT" in feats:
        feats.add("DIRECT_CAUSATION")
    if has_act or has_block or has_transfer:
        feats.add("AGENT")
    if ("GOAL_OBJECT" in feats) or ("BLOCK_ACT" in feats):
        feats.add("GOAL_OWNER")
    if t & WEATHER_W:
        feats.add("WEATHER")
    if t & MOTION_W:
        feats.add("MOTION")
    if t & SCENERY_W:
        feats.add("SCENERY")
    return sorted(feats)


# ---- View 2: the SECOND INDEPENDENT VIEW (discourse/purpose connective cues; DISJOINT class) -----
# Function/connective/modal words + infinitival-purpose markers. None of these tokens appear in any
# View-1 content lexicon -> the two views are mechanically independent (residual proposes / cue
# disposes). Multi-word phrases matched as substrings on lowercased text.
GOAL_CUE_PHRASES = ["so that", "in order to", "so as to", "for fear", "meaning to", "hoping to",
                    "wanted to", "tried to", "meant to", "wished to"]
GOAL_CUE_WORDS = {"because", "would", "lest", "purpose", "intended", "deliberately"}


def second_view_goal_cue(text: str) -> bool:
    """View 2: TRUE iff a goal/purpose discourse cue is present. Independent of View 1."""
    low = " " + text.lower() + " "
    if any(p in low for p in GOAL_CUE_PHRASES):
        return True
    toks = set(normalize_tokens(text))
    return bool(toks & GOAL_CUE_WORDS)


# ============================================================================ HD / library ops
def feature_atoms(seed):
    rng = np.random.RandomState(seed)
    return {f: rng.choice([-1.0, 1.0], size=N).astype(np.float64) for f in ALL_FEATURES}


def bundle(atoms, names):
    if not names:
        return np.ones(N, dtype=np.float64)
    acc = np.sum([atoms[n] for n in names], axis=0)
    o = np.sign(acc)
    o[o == 0] = 1.0
    return o


def build_library(atoms, templates):
    W = np.zeros((N, N), dtype=np.float64)
    for _name, feats in sorted(templates.items()):
        t = bundle(atoms, feats)
        pc.vanilla_hebbian_write(W, t, t)  # store each template as an autoassociative fixed point
    return W


def residual_of(atoms, W, feats):
    obs = bundle(atoms, feats)
    pred = pc.predict(W, obs, sign_cleanup=True)
    return pc.residual_magnitude(obs, pred)


def best_template(atoms, templates, feats):
    """Nearest existing template by cosine of the feature bundle (for mint signature + attribution)."""
    obs = bundle(atoms, feats)
    best_name, best_cos = None, -2.0
    for name, tfeats in sorted(templates.items()):
        tb = bundle(atoms, tfeats)
        cos = float(np.dot(obs, tb)) / N
        if cos > best_cos:
            best_name, best_cos = name, cos
    return best_name, best_cos


def mint_signature(templates, feats):
    """Propose the new type's signature = passage features NOT in its best-matching template.
    (Placeholder: named arbitrarily; content is the binding signature.)"""
    # best template by feature-set overlap (seed-independent; ties -> first sorted)
    best_name, best_overlap = None, -1
    fset = set(feats)
    for name, tfeats in sorted(templates.items()):
        ov = len(fset & set(tfeats))
        if ov > best_overlap:
            best_name, best_overlap = name, ov
    unexplained = sorted(fset - set(templates[best_name]))
    return unexplained


# ============================================================================ passage corpus
def _fill(tmpl, bank, i):
    out = tmpl
    for key, words in bank.items():
        out = out.replace("{" + key + "}", words[i % len(words)])
    return out


AGENTS = ["Jo", "Tom", "Amy", "the girl", "the boy", "the man", "Ruth", "Ann"]
GOAL_TMPLS = [
    "{A} wanted to reach safety, but deliberately {A2} withheld the warning so that {A} "
    "would be left unwarned; hoping to spite her, {A2} let her take care of herself, and she fell down.",
    "{A} tried to warn the child in time, but {A2} concealed the warning because {A2} meant to keep "
    "her from safety; the girl, meaning to win to care, missed her chance and fell.",
    "{A} wished to be told and warned in time, yet {A2} refused to warn her and ignored her, so that "
    "she was left unprotected; she went down and lost her chance.",
]
NOISE_TMPLS = [
    "The warm spell had preceded the cold snap, and a frost lay along the shore; the ice drifted "
    "while the wind moved over the field and the sky.",
    "A chill mist floated past the meadow and the sun glided low over the river; the frost snap "
    "spread along the bank and the trees stood still.",
    "The cold wind drifted over the hill and the ice sank along the path; a warm spell had passed "
    "and the sky moved grey over the field.",
]
HARM_TMPLS = [
    "{A} drove the knife into the man's breast and struck him hard, and the man was killed.",
    "{A} took up the poker and beat the boy over the head, and the child was left wounded and hurt.",
    "{A} smashed the bowl and tore the page, then struck the girl on the arm until she bled.",
]


def build_corpus():
    """Return list of dict(id, text, cls, gold_type). cls in {goal_block, noise, redundant_harm}."""
    items = []
    for i in range(K_SYNTH):
        a = AGENTS[i % len(AGENTS)]
        a2 = AGENTS[(i + 3) % len(AGENTS)]
        items.append(dict(id=f"gb_syn_{i:02d}", cls="goal_block", gold_type="goal_blocker",
                          text=_fill(GOAL_TMPLS[i % len(GOAL_TMPLS)], {"A": [a], "A2": [a2]}, 0)))
        items.append(dict(id=f"nz_syn_{i:02d}", cls="noise", gold_type=None,
                          text=NOISE_TMPLS[i % len(NOISE_TMPLS)]))
        items.append(dict(id=f"hm_syn_{i:02d}", cls="redundant_harm", gold_type="physical_harm",
                          text=_fill(HARM_TMPLS[i % len(HARM_TMPLS)], {"A": [a]}, 0)))
    items += load_real_items()
    return items


def load_real_items():
    """Best-effort load of 2 real ruler items from gold (DIRECTIONAL, n small). Never reads the gold
    type label or true-agent name into the typer -- only span/goal-description content text."""
    out = []
    try:
        gold_dir = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
        richer = {}
        with open(os.path.join(gold_dir, "gold_grounded_appraisal_richer_v1.jsonl"), encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                richer[d["id"]] = d

        def goal_desc(gd):
            s = str(gd)
            if "(" in s and ")" in s:
                inner = s[s.index("(") + 1:s.rindex(")")]
                for lbl in ("epistemic goal:", "blocked goal:"):
                    if lbl in inner:
                        inner = inner.split(lbl, 1)[1]
                return inner.strip()
            return ""

        # goal_block real item: mcca_004 (Amy blocked-goal). text = goal-desc + true span + query span
        if "grapp_mcca_004" in richer:
            it = richer["grapp_mcca_004"]
            txt = " ".join([goal_desc(it["goal_owner"]), it["true_blocker_span"]["text"],
                            it["query_span"]["text"]])
            out.append(dict(id="grapp_mcca_004_real", cls="goal_block", gold_type="goal_blocker", text=txt))
        # redundant_harm real item: mcca_001 (direct physical killing) if present
        if "grapp_mcca_001" in richer:
            it = richer["grapp_mcca_001"]
            txt = it["true_blocker_span"]["text"]
            out.append(dict(id="grapp_mcca_001_real", cls="redundant_harm", gold_type="physical_harm", text=txt))
    except Exception as e:  # noqa: BLE001 -- real items are optional garnish
        out.append(dict(id="_real_load_error", cls="_meta", gold_type=None, text="", error=str(e)[:200]))
    return out


# ============================================================================ the loop
def run_loop(atoms, W_seed, corpus, mode):
    """Run one self-extension pass. mode in {full, residual_only}.
    Returns dict with per-passage gate decisions, minted types, and the grown library."""
    templates = dict(SEED_TEMPLATES)
    passages = [it for it in corpus if it["cls"] in ("goal_block", "noise", "redundant_harm")]

    # 1-2-3: gate every passage; collect mint-signature proposals from gate-passers.
    proposals = {}  # signature-key -> {"sig": [...], "ids": [...], "residuals": [...]}
    per_passage = []
    for it in passages:
        feats = type_passage(it["text"])
        resid = residual_of(atoms, W_seed, feats)
        novel = pc.threshold_gate(bundle(atoms, feats),
                                  pc.predict(W_seed, bundle(atoms, feats)),
                                  threshold=RESIDUAL_THRESHOLD)
        residual_fires = not novel.skipped
        cue = second_view_goal_cue(it["text"])
        if mode == "full":
            enters = residual_fires and cue
        else:  # residual_only ablation (no second view)
            enters = residual_fires
        sig = mint_signature(templates, feats) if enters else None
        sig_key = "+".join(sig) if sig else None
        if enters and sig_key:
            p = proposals.setdefault(sig_key, {"sig": sig, "ids": [], "residuals": []})
            p["ids"].append(it["id"])
            p["residuals"].append(resid)
        per_passage.append(dict(id=it["id"], cls=it["cls"], feats=feats, residual=round(resid, 4),
                                residual_fires=residual_fires, second_view_cue=cue,
                                enters_minting=enters, proposed_sig=sig))

    # 4: CONSOLIDATE -- promote a candidate type iff >=MIN_CONFIRM confirmations AND the abstain-band
    # controller (self_improving_loop.decide_keep_or_revert) adopts its aggregate residual margin.
    minted = {}
    templates_grown = dict(templates)
    for sig_key, p in sorted(proposals.items()):
        n_conf = len(p["ids"])
        if n_conf < MIN_CONFIRM:
            continue
        agg_margin = float(np.mean(p["residuals"]))  # residual margin over the abstain band
        adopt = decide_keep_or_revert({sig_key: agg_margin}, abstain_band=ABSTAIN_BAND_DEFAULT)
        if adopt is None:
            continue
        # placeholder name: the new type is named by index of minting, content = the signature
        name = f"minted_type_{len(minted)}"
        templates_grown[name] = p["sig"]
        minted[name] = dict(signature=p["sig"], n_confirmations=n_conf,
                            confirming_ids=sorted(p["ids"]), agg_residual_margin=round(agg_margin, 4))

    return dict(mode=mode, per_passage=per_passage, minted=minted, templates_grown=templates_grown)


def _sig_is_goal(sig):
    """A minted signature counts as the goal-blocker type iff it is dominated by GOAL features."""
    s = set(sig)
    goal = s & set(GOAL_FEATURES)
    noise = s & set(NOISE_FEATURES)
    return len(goal) >= 2 and len(noise) == 0


def _sig_is_spurious(sig):
    """Spurious (drift) iff the signature is dominated by NOISE features (non-causal)."""
    s = set(sig)
    return len(s & set(NOISE_FEATURES)) >= 2 and len(s & set(GOAL_FEATURES)) == 0


def attribute(atoms, templates, corpus, cls):
    """Attribution accuracy: argmax template-cosine == gold_type, over passages of a class."""
    rows = [it for it in corpus if it["cls"] == cls and it.get("gold_type")]
    if not rows:
        return None
    correct = 0
    for it in rows:
        feats = type_passage(it["text"])
        pred_type, _ = best_template(atoms, templates, feats)
        # a minted type matches gold 'goal_blocker' iff its signature is the goal type
        if it["gold_type"] == "goal_blocker":
            hit = pred_type in templates and _sig_is_goal(templates[pred_type]) \
                if pred_type in templates and pred_type.startswith("minted_") else (pred_type == "goal_blocker")
        else:
            hit = (pred_type == it["gold_type"])
        correct += int(hit)
    return correct / len(rows)


# ============================================================================ per-seed unit
def run_seed(seed, corpus):
    atoms = feature_atoms(seed)
    W_seed = build_library(atoms, SEED_TEMPLATES)

    full = run_loop(atoms, W_seed, corpus, "full")
    ronly = run_loop(atoms, W_seed, corpus, "residual_only")

    # minted-type accounting
    full_goal = [n for n, m in full["minted"].items() if _sig_is_goal(m["signature"])]
    full_spurious = [n for n, m in full["minted"].items() if _sig_is_spurious(m["signature"])]
    ronly_goal = [n for n, m in ronly["minted"].items() if _sig_is_goal(m["signature"])]
    ronly_spurious = [n for n, m in ronly["minted"].items() if _sig_is_spurious(m["signature"])]

    # UTILITY: goal-block attribution BEFORE (seed library) vs AFTER (full-mode grown library)
    gb_before = attribute(atoms, SEED_TEMPLATES, corpus, "goal_block")
    gb_after = attribute(atoms, full["templates_grown"], corpus, "goal_block")
    harm_before = attribute(atoms, SEED_TEMPLATES, corpus, "redundant_harm")
    harm_after = attribute(atoms, full["templates_grown"], corpus, "redundant_harm")

    # RE-READ residual on goal-block passages before vs after minting (should drop)
    gb_ids = [it for it in corpus if it["cls"] == "goal_block"]
    resid_before = float(np.mean([residual_of(atoms, W_seed, type_passage(it["text"])) for it in gb_ids]))
    W_grown = build_library(atoms, full["templates_grown"])
    resid_after = float(np.mean([residual_of(atoms, W_grown, type_passage(it["text"])) for it in gb_ids]))

    # second-view agreement rates (View1 residual vs View2 cue) per class
    def agree_rates():
        out = {}
        for cls in ("goal_block", "noise", "redundant_harm"):
            rows = [p for p in full["per_passage"] if p["cls"] == cls]
            if rows:
                out[cls] = dict(
                    residual_fire_rate=round(sum(p["residual_fires"] for p in rows) / len(rows), 3),
                    second_view_cue_rate=round(sum(p["second_view_cue"] for p in rows) / len(rows), 3),
                    both_fire_rate=round(sum(p["residual_fires"] and p["second_view_cue"] for p in rows) / len(rows), 3),
                    n=len(rows))
        return out

    return dict(
        seed=seed,
        full_minted=full["minted"], residual_only_minted=ronly["minted"],
        full_goal_types=full_goal, full_spurious_types=full_spurious,
        residual_only_goal_types=ronly_goal, residual_only_spurious_types=ronly_spurious,
        mints_goal_blocker=bool(full_goal),
        C1_noise_no_mint_full=(len(full_spurious) == 0),
        C2_redundant_no_mint_full=all(not m["signature"] or (set(m["signature"]) & set(NATIVE_FEATURES) != set(m["signature"]))
                                      for m in full["minted"].values()) and (len(full["minted"]) == len(full_goal)),
        C3_utility_lift=(gb_after is not None and gb_before is not None and gb_after > gb_before),
        C3_no_harm_regression=(harm_after is not None and harm_before is not None and harm_after >= harm_before),
        C4_residual_only_drifts=(len(ronly_spurious) >= 1),
        C4_full_no_drift=(len(full_spurious) == 0),
        gb_attrib_before=gb_before, gb_attrib_after=gb_after,
        harm_attrib_before=harm_before, harm_attrib_after=harm_after,
        gb_residual_before=round(resid_before, 4), gb_residual_after=round(resid_after, 4),
        view_agreement=agree_rates(),
        per_passage=full["per_passage"],
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def frac(key):
        return sum(1 for s in seeds if per_seed[s][key]) / max(1, n)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return float(np.mean(vals)) if vals else None

    maj = lambda k: frac(k) > 0.5  # noqa: E731

    mints_goal = maj("mints_goal_blocker")
    c1 = maj("C1_noise_no_mint_full")
    c2 = maj("C2_redundant_no_mint_full")
    c3 = maj("C3_utility_lift") and maj("C3_no_harm_regression")
    c4 = maj("C4_residual_only_drifts") and maj("C4_full_no_drift")

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif mints_goal and c1 and c2 and c3 and c4:
        verdict = "SELF_EXTENSION_WORKS"
    elif mints_goal and c1 and c2 and c3 and not maj("C4_residual_only_drifts"):
        verdict = "SECOND_VIEW_NOT_DEMONSTRATED_LOADBEARING"
    else:
        verdict = "DRIFT_OR_INSUFFICIENT"

    # representative minted signature (seed 0)
    s0 = per_seed[seeds[0]]
    # REAL-ITEM TRANSFER (honest): did the real ruler items fire each gate? (n small, directional)
    real_transfer = [dict(id=p["id"], cls=p["cls"], residual=p["residual"],
                          residual_fires=p["residual_fires"], second_view_cue=p["second_view_cue"],
                          enters_minting=p["enters_minting"])
                     for p in s0["per_passage"] if "real" in p["id"]]
    goal_sig = None
    for _n, m in s0["full_minted"].items():
        if _sig_is_goal(m["signature"]):
            goal_sig = m
            break

    summary = (
        f"mints_goal_blocker={frac('mints_goal_blocker'):.2f} | C1_noise_no_mint={frac('C1_noise_no_mint_full'):.2f} "
        f"C2_redundant_no_mint={frac('C2_redundant_no_mint_full'):.2f} "
        f"C3_utility_lift={frac('C3_utility_lift'):.2f}(no_reg={frac('C3_no_harm_regression'):.2f}) "
        f"C4_ronly_drifts={frac('C4_residual_only_drifts'):.2f}/full_no_drift={frac('C4_full_no_drift'):.2f} | "
        f"gb_attrib {mean('gb_attrib_before'):.2f}->{mean('gb_attrib_after'):.2f} "
        f"gb_residual {mean('gb_residual_before'):.3f}->{mean('gb_residual_after'):.3f}")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        fractions=dict(
            mints_goal_blocker=frac("mints_goal_blocker"),
            C1_noise_no_mint_full=frac("C1_noise_no_mint_full"),
            C2_redundant_no_mint_full=frac("C2_redundant_no_mint_full"),
            C3_utility_lift=frac("C3_utility_lift"), C3_no_harm_regression=frac("C3_no_harm_regression"),
            C4_residual_only_drifts=frac("C4_residual_only_drifts"), C4_full_no_drift=frac("C4_full_no_drift"),
        ),
        means=dict(
            gb_attrib_before=mean("gb_attrib_before"), gb_attrib_after=mean("gb_attrib_after"),
            harm_attrib_before=mean("harm_attrib_before"), harm_attrib_after=mean("harm_attrib_after"),
            gb_residual_before=mean("gb_residual_before"), gb_residual_after=mean("gb_residual_after"),
        ),
        minted_goal_blocker_signature_seed0=goal_sig,
        real_items_transfer_seed0=real_transfer,
        real_items_transfer_note=(
            "HONEST LIMITATION surfaced by VET: the connective-cue second view has a RECALL GAP on "
            "naturalistic prose -- the real goal-block ruler item grapp_mcca_004 trips the residual "
            "gate (novel) but its goal-blocking is expressed WITHOUT an explicit connective cue "
            "('let her take care of herself'), so the second view does NOT fire and the real item "
            "would NOT mint. The milestone holds on the controlled synthetic set (goal cues by "
            "construction); real-text transfer is bounded by the second view's recall -> routes the "
            "next step (a naturalistic-prose-robust independent second view)."),
        example_view_agreement_seed0=s0["view_agreement"],
        residual_only_spurious_types_seed0=s0["residual_only_spurious_types"],
        full_spurious_types_seed0=s0["full_spurious_types"],
        brain_structures=dict(
            novelty_mint_trigger="VTA-dopamine RPE + cortical predictive coding (Rao-Ballard/Friston); "
                                 "hippocampal-mPFC schema-incongruity (van Kesteren 2012); MINT = hippocampal "
                                 "fast pattern-separated binding (CLS McClelland 1995)",
            second_independent_view="left IFG/pMTG discourse-connective/purpose processing (Do/Chan/Roth 2011); "
                                    "coupling = NELL CPL promotion-requires-independent-view (WSDM 2010)",
            consolidation_gate="ACC/PFC conflict-monitoring control (self_improving_loop) + neocortical slow "
                               "interleaved consolidation (>=2 cross-confirmations)",
        ),
        caveats=[
            "Feature typing is a supplied glass-box lexical map (same accepted construction caveat as "
            "exp_disequilibrium_novelty_signal_test_v1) -- the loop SCORES/MINTS given a faithful typing; "
            "it does not induce the typer itself.",
            "The two views are mechanically independent (HD prediction-error residual vs a DISJOINT "
            "connective/purpose function-word cue), but on the synthetic set goal-block passages carry "
            "goal cues by construction (as real goal-directed prose does).",
            "Real ruler items n=2 (DIRECTIONAL garnish); statistical power is the synthetic controlled set.",
            "predictive_coding / self_improving_loop / normalize_tokens reused bit-identical; no borrowed "
            "embedding/LLM/parser as mechanism; minted type NAME is an arbitrary placeholder.",
        ],
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def run(run_mode):
    t0 = time.perf_counter()
    out_dir = OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    _write_json(os.path.join(out_dir, "_start_marker.json"), marker)

    corpus = build_corpus()
    seeds = SEEDS if run_mode == "full" else SEEDS[:2]
    done = completed_units(out_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, corpus)
        record_unit(out_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s mints_goal={res['mints_goal_blocker']} "
              f"C1={res['C1_noise_no_mint_full']} C4_drift={res['C4_residual_only_drifts']} "
              f"gb_attrib {res['gb_attrib_before']}->{res['gb_attrib_after']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(N=N, seeds=seeds, residual_threshold=RESIDUAL_THRESHOLD,
                         min_confirm=MIN_CONFIRM, k_synth=K_SYNTH)
    agg["prereg"] = "preregs/2026-08-04_self_extension_loop_v1.md"
    agg["cites"] = ["notes/brain_component_functional_map_2026-08-04.md",
                    "notes/research_self_extending_grounded_knowledge_prior_art_2026-08-04.md",
                    "exp_disequilibrium_novelty_signal_test_v1"]
    agg["per_seed"] = per_seed
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    corpus = build_corpus()
    # (1) typer separation: goal_block -> goal feats present, no harm-outcome; harm -> harm feats
    gb = next(it for it in corpus if it["cls"] == "goal_block")
    hm = next(it for it in corpus if it["cls"] == "redundant_harm")
    nz = next(it for it in corpus if it["cls"] == "noise")
    fgb, fhm, fnz = type_passage(gb["text"]), type_passage(hm["text"]), type_passage(nz["text"])
    assert set(GOAL_FEATURES) & set(fgb), f"goal_block missing goal feats: {fgb}"
    assert "HARM_OUTCOME" in fhm, f"harm missing HARM_OUTCOME: {fhm}"
    assert set(NOISE_FEATURES) & set(fnz) and not (set(GOAL_FEATURES) & set(fnz)), f"noise typing off: {fnz}"

    # (2) second view: TRUE on goal_block, FALSE on noise + harm (independence: no content overlap)
    assert second_view_goal_cue(gb["text"]), "second view missed goal cue"
    assert not second_view_goal_cue(nz["text"]), "second view false-fired on noise"
    assert not second_view_goal_cue(hm["text"]), "second view false-fired on harm"
    # DISJOINTNESS: no View-2 cue word is in any View-1 content lexicon
    v1 = (PHYS_ACT | HARM_OUT | HELP_OUT | PATIENT_W | TRANSFER_W | INSTRUMENT_W | GOAL_OBJ_W |
          BLOCK_W | GOAL_UNMET_W | WEATHER_W | MOTION_W | SCENERY_W)
    assert not (GOAL_CUE_WORDS & v1), f"views not disjoint: {GOAL_CUE_WORDS & v1}"

    # (3) residual gate separates typed-harm (low) from goal_block + noise (high) at threshold
    atoms = feature_atoms(0)
    W = build_library(atoms, SEED_TEMPLATES)
    r_hm = residual_of(atoms, W, fhm)
    r_gb = residual_of(atoms, W, fgb)
    r_nz = residual_of(atoms, W, fnz)
    assert r_hm < RESIDUAL_THRESHOLD < min(r_gb, r_nz), f"residual sep off: hm={r_hm} gb={r_gb} nz={r_nz}"

    # (4) one full seed: mints goal_blocker, no spurious in full, residual_only drifts, utility lifts
    res = run_seed(0, corpus)
    assert res["mints_goal_blocker"], "did not mint goal_blocker"
    assert res["C1_noise_no_mint_full"], "full minted a spurious type"
    assert res["C4_residual_only_drifts"], "residual_only did not drift (ablation vacuous)"
    assert res["gb_attrib_after"] > res["gb_attrib_before"], "no utility lift"
    print(f"[SELFTEST PASS] typer/2nd-view/residual separation OK; seed0 mints goal_blocker; "
          f"full spurious={res['full_spurious_types']} residual_only spurious={res['residual_only_spurious_types']}; "
          f"gb_attrib {res['gb_attrib_before']}->{res['gb_attrib_after']} "
          f"gb_residual {res['gb_residual_before']}->{res['gb_residual_after']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
