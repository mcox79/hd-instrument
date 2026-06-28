"""Shared implementation for substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2.

DRILL 2 v2 (per Skunkworks invalidation f60880f7 of v1; cell-author 2026-06-28).

Skunkworks landed-VET on v1 showed:
  * only_focus ablation (W_FOCUS * f_focus only) = 1.000 across all seeds
  * no_focus ablation (other 4 features) = 0.500/0.500/0.250 (WORSE than random)
  * "mechanism" was a noised oracle lookup over narr.scene_focus dict
Root cause: _build_mention_history read narr.events["char_id"] directly;
  _feature_focus read narr.scene_focus[scene_id] directly; corpus construction
  has ev["char_id"] = scene_focus[scene_id] for ALL pronoun events -> scene_focus
  lookup IS the Q2 ground-truth answer.

v2 fixes:
  1. ORACLE_LEAK_GUARD: cell startup self-greps source for forbidden tokens;
     refuses to run if found.
  2. Substrate-faithful feature extraction: every f_* derives its signal from
     cosine queries against substrate state (W_part[c], W_cortex, vocab vectors).
     NO direct read of narr.events[*]["char_id"], narr.scene_focus, narr.events
     [*]["scene_id"], narr.events[*]["role_tag_idx"], narr.events[*]["verb_id"].
  3. Corpus diversification: NON_FOCUS_PRONOUN_FRAC controls fraction of pronouns
     targeting NON-focus characters (random non-focus member in scene). Sweep
     {0.0, 0.3, 0.6} to expose whether mechanism beats scene-focus baseline
     when pronouns DON'T trivially target scene-focus.
  4. SCHEMA-VET self-source assertions: verify by grep that feature extractors
     don't import narr fields.

Mechanism class (genuinely different from drill 1 HRR sequence-recency):
  drill 1 = HRR sequence-log + temporal binding (associative recall via cosine
            over per-char position-indexed bank)
  drill 2 = Lappin-Leass symbolic weighted-salience over SUBSTRATE-QUERIED
            features (substrate as feature extractor; symbolic layer above
            does the resolve)
  Different mechanism class: associative-recall vs weighted-salience-symbolic

ASCII-only. CPU. numpy only. Resumable via _seed_checkpoint.
PREREG: preregs/2026-06-28_substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2.md
Author: exp_dev 2026-06-28 (v2 post Skunkworks invalidation).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import re
import argparse
import hashlib
import json
import math
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2"
CORPUS_PROVENANCE = (
    "synthetic_narrative_5char_grouped_into_scenes_fixed_K10_boundaries_"
    "with_per_character_facts_pronouns_and_fact_updates_DIVERSIFIED_PRONOUNS_"
    "NON_FOCUS_FRAC_sweepable_drill2_v2_substrate_faithful"
)


# =============================================================================
# ORACLE_LEAK_GUARD: cell self-asserts at startup that its own source code
# contains NO direct narrative-dict access in feature-extractor paths.
# =============================================================================
def _oracle_leak_guard() -> None:
    """At module load, grep self-source for forbidden tokens; refuse to run if found.

    The check looks for actual Python-attribute-access patterns in CODE LINES
    (lines that aren't comments or docstrings or string-literal patterns
    embedded as regex source).

    Allowed surface-form reads (the QUESTION inputs, observable at the pronoun
    position itself):
      q[event_idx]            : the pronoun event index (the question position)
      q[expected_char_id]     : the ANSWER (only for ARM_ORACLE)
      narr-events-ev-idx-read : ALLOWED ONLY for ARM_ORACLE + ARM_NAIVE_MAGNITUDE
                                reproduction; substrate-faithful arms must
                                NOT access this for feature extraction.
    """
    src_path = Path(__file__)
    src = src_path.read_text(encoding="utf-8")

    # Forbidden Python-attribute-access patterns. Build dynamically so this
    # function body itself does not contain the literal regex strings (which
    # would otherwise need self-exemption logic).
    NA = "narr"
    EV = "events"
    SF = "scene_focus"
    forbidden_patterns = [
        ("scene_focus_read",
         NA + r"\s*\.\s*" + SF),
        ("event_char_id_read",
         NA + r"\s*\.\s*" + EV + r"\s*\[[^\]]+\]\s*\[\s*[\"']char_id[\"']"),
        ("event_scene_id_read",
         NA + r"\s*\.\s*" + EV + r"\s*\[[^\]]+\]\s*\[\s*[\"']scene_id[\"']"),
        ("event_role_tag_read",
         NA + r"\s*\.\s*" + EV + r"\s*\[[^\]]+\]\s*\[\s*[\"']role_tag_idx[\"']"),
        ("event_is_subject_read",
         NA + r"\s*\.\s*" + EV + r"\s*\[[^\]]+\]\s*\[\s*[\"']is_subject_role[\"']"),
    ]

    SUBSTRATE_FAITHFUL_FUNCS = [
        "_feature_recency_substrate",
        "_feature_scene_substrate",
        "_feature_subject_substrate",
        "_feature_focus_substrate",
        "_feature_parallel_substrate",
        "q2_lappin_leass_full_substrate_faithful",
        "q2_recency_only_substrate_faithful",
        "q2_cosine_only",
    ]

    # Strip docstrings and triple-quoted string blocks using AST so docstrings
    # mentioning forbidden tokens in plain text don't false-positive.
    import ast as _ast
    try:
        tree = _ast.parse(src)
    except SyntaxError:
        # If source doesn't parse, the cell won't run anyway; let it fail later.
        return

    # Map line number -> function name for all function defs.
    func_at_line: Dict[int, str] = {}
    docstring_lines: set = set()
    for node in _ast.walk(tree):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            # function body line range
            start_line = node.lineno
            end_line = getattr(node, "end_lineno", start_line)
            for ln in range(start_line, end_line + 1):
                func_at_line[ln] = node.name
            # Detect docstring (first stmt is Expr(Constant(str)))
            if (node.body and isinstance(node.body[0], _ast.Expr)
                    and isinstance(node.body[0].value, _ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                doc_node = node.body[0]
                d_start = doc_node.lineno
                d_end = getattr(doc_node, "end_lineno", d_start)
                for ln in range(d_start, d_end + 1):
                    docstring_lines.add(ln)
        # Module-level docstring
        if isinstance(node, _ast.Module):
            if (node.body and isinstance(node.body[0], _ast.Expr)
                    and isinstance(node.body[0].value, _ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                doc_node = node.body[0]
                d_start = doc_node.lineno
                d_end = getattr(doc_node, "end_lineno", d_start)
                for ln in range(d_start, d_end + 1):
                    docstring_lines.add(ln)
        # Any string Constant that spans multiple lines as a free-standing
        # expression (also covers triple-quoted block comments).
        if isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Constant) \
                and isinstance(node.value.value, str):
            d_start = node.lineno
            d_end = getattr(node, "end_lineno", d_start)
            for ln in range(d_start, d_end + 1):
                docstring_lines.add(ln)

    lines = src.split("\n")
    violations: List[Tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        lineno = i + 1
        if lineno in docstring_lines:
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Skip the guard function's own body (it references the patterns).
        current_func = func_at_line.get(lineno)
        if current_func == "_oracle_leak_guard":
            continue
        if current_func not in SUBSTRATE_FAITHFUL_FUNCS:
            continue
        for name, pat in forbidden_patterns:
            if re.search(pat, line):
                violations.append((lineno, current_func, line.strip()))
                break

    if violations:
        msg_lines = ["ORACLE_LEAK_GUARD: forbidden narr-dict reads found in substrate-faithful functions:"]
        for lineno, func, line_text in violations:
            msg_lines.append("  line %d in %s: %s" % (lineno, func, line_text))
        msg_lines.append("Cell REFUSES TO RUN. Audit + remove leaks before re-running.")
        raise RuntimeError("\n".join(msg_lines))


# Run the guard at module import (before any heavy work).
_oracle_leak_guard()


# ---------------- CLI ----------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--seed", type=int, default=None)
_P.add_argument("--non-focus-frac", type=float, default=None,
                help="override NON_FOCUS_PRONOUN_FRAC; default 0.3 in smoke, 0.3 in full")
_P.add_argument("--timeout", type=int, default=2700)
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

_env_seed = os.environ.get("HDLAB_SEED", "").strip()
if _ARGS.seed is not None:
    SEED_ACTIVE = int(_ARGS.seed)
elif _env_seed:
    SEED_ACTIVE = int(_env_seed)
else:
    SEED_ACTIVE = 7

SEEDS = [SEED_ACTIVE]

# ---------------- regime config ----------------
# Reuse drill 1 regime structure for direct comparability per Gate D.
N_HIPPO = 512
N_CORTEX = 1024
N_PART = 1024
N_EVENTS = 100
N_CHARACTERS = 5
K_SCENE_BOUNDARY = 10
N_FACTS_PER_CHAR = 3
N_UPDATE_PAIRS = 3
N_PRONOUN_EVENTS = 8
Q_PER_TYPE = 8

K_HIPPO_ACTIVE = max(1, int(round(0.10 * N_HIPPO)))
ETA_CORTEX = 0.005
N_REPLAY_CYCLES = 3
N_RAW = 64
N_VERBS = 12
N_OBJECTS = 16
N_JOBS = 8

# NEW in v2: pronoun-target diversification. Sweep {0.0, 0.3, 0.6}.
# Smoke uses 0.3 (the discriminating regime: scene-focus alone gets 0.625 to
# 0.875 depending on which non-focus chars in scene; mechanism must do better).
if _ARGS.non_focus_frac is not None:
    NON_FOCUS_PRONOUN_FRAC = float(_ARGS.non_focus_frac)
else:
    NON_FOCUS_PRONOUN_FRAC = float(os.environ.get("HDLAB_NON_FOCUS_FRAC", "0.3"))
assert 0.0 <= NON_FOCUS_PRONOUN_FRAC <= 1.0, "non-focus frac out of range"

# Lappin-Leass salience weights (PRE-REG'd FIXED; NOT tuned to PASS).
W_RECENCY  = 100.0
W_SCENE    = 50.0
W_SUBJECT  = 80.0
W_FOCUS    = 40.0
W_PARALLEL = 35.0
LAMBDA_RECENCY = 0.05

# Substrate-query parameters
RECENCY_LOOKBACK = 20    # probe substrate at offsets {1..RECENCY_LOOKBACK} back
SUBJECT_LOOKBACK = 5     # last K mentions for subject-role frequency feature

# ---------------- pre-reg bands (LOCKED at module init; PRE-SMOKE) ----------------
#
# CRITICAL: bands set against random floor (0.20) + theoretical scene-focus
# baseline at NON_FOCUS_FRAC=0.3 (theoretical = 0.7 * 1.0 + 0.3 * ~0.25 = ~0.775,
# where 0.25 = 1/(N_CHARACTERS-1) random over non-focus chars in scene).
# A non-substrate baseline that scores at theoretical scene-focus is NOT
# substrate-faithful. The mechanism must lift LAPPIN_LEASS Q2 above the
# theoretical scene-focus baseline by >= 0.15 at NON_FOCUS_FRAC=0.3.
HP_LAPPIN_LEASS_Q2_MIN = 0.80
HP_LIFT_OVER_BASELINE = 0.15   # vs max(NAIVE_MAGNITUDE, COSINE_ONLY)
HP_ORACLE_Q2 = 1.000
HP_ARMS_DISTINCT_MIN = 4

HF_LAPPIN_LEASS_Q2_MAX = 0.50  # below random+chance scene-focus signal -> inert
HF_LIFT_OVER_BASELINE_MAX = 0.00

assert HP_LAPPIN_LEASS_Q2_MIN > HF_LAPPIN_LEASS_Q2_MAX
assert HP_LIFT_OVER_BASELINE > HF_LIFT_OVER_BASELINE_MAX

ARMS = [
    "ARM_RANDOM_FLOOR",
    "ARM_NAIVE_MAGNITUDE",
    "ARM_COSINE_ONLY",
    "ARM_RECENCY_ONLY_SUBSTRATE",
    "ARM_LAPPIN_LEASS_FULL_SUBSTRATE",
    "ARM_ORACLE",
]
QUERY_TYPES = ["Q1_factual", "Q2_coreference", "Q3_temporal", "Q4_contradict"]
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N_h=%d,N_c=%d,N_part=%d,N_events=%d,N_chars=%d,K_scene=%d,"
    "K_active=%d,eta=%.4f,N_replay=%d,Q_per_type=%d,seed=%d,arms=%d,mode=%s,"
    "non_focus_frac=%.2f,recency_lookback=%d,subject_lookback=%d,"
    "W_R=%.0f,W_S=%.0f,W_Sub=%.0f,W_F=%.0f,W_P=%.0f,lam=%.3f,"
    "HP_q2_min=%.2f,HP_lift=%.2f,HF_q2_max=%.2f,EXPECTED_N=%d,"
    "drill2_v2_substrate_faithful=True"
) % (
    ANCHOR_NAME, N_HIPPO, N_CORTEX, N_PART, N_EVENTS, N_CHARACTERS,
    K_SCENE_BOUNDARY, K_HIPPO_ACTIVE, ETA_CORTEX, N_REPLAY_CYCLES,
    Q_PER_TYPE, SEED_ACTIVE, len(ARMS), RUN_MODE,
    NON_FOCUS_PRONOUN_FRAC, RECENCY_LOOKBACK, SUBJECT_LOOKBACK,
    W_RECENCY, W_SCENE, W_SUBJECT, W_FOCUS, W_PARALLEL, LAMBDA_RECENCY,
    HP_LAPPIN_LEASS_Q2_MIN, HP_LIFT_OVER_BASELINE, HF_LAPPIN_LEASS_Q2_MAX,
    EXPECTED_N_UNITS,
)


# ---------------- vector primitives ----------------

def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int))


def random_bipolar(shape, rng: np.random.Generator) -> np.ndarray:
    return np.where(rng.random(shape) < 0.5, -1.0, 1.0).astype(np.float64)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def cosine_argmax(probe: np.ndarray, candidates: np.ndarray) -> int:
    norms = np.linalg.norm(candidates, axis=1)
    pn = float(np.linalg.norm(probe))
    if pn < 1e-9:
        return 0
    safe = np.where(norms > 1e-9, norms, 1.0)
    cand_norm = candidates / safe[:, None]
    p_norm = probe / pn
    sims = cand_norm @ p_norm
    return int(np.argmax(sims))


def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_h_to_c(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hebbian_write(W: np.ndarray, key: np.ndarray, val: np.ndarray,
                  eta: float) -> None:
    W += eta * np.outer(val, key)


def permute_role_pos(v: np.ndarray, pos: int) -> np.ndarray:
    if v.shape[0] == 0:
        return v
    return np.roll(v, int(pos) % v.shape[0])


# ---------------- narrative generator (v2: diversified pronouns) ----------------

class Narrative:
    """v2: NON_FOCUS_PRONOUN_FRAC controls fraction of pronouns targeting
    non-focus characters who already appeared in the scene.
    """

    def __init__(self, seed_offset: int, non_focus_frac: float) -> None:
        self.seed_offset = int(seed_offset)
        self.non_focus_frac = float(non_focus_frac)
        self.rng = _rng(seed_offset)

        self.events: List[Dict] = []
        self.char_facts: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

        n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
        scene_focus = [int(self.rng.integers(0, N_CHARACTERS))
                       for _ in range(n_scenes)]

        update_pairs: List[Tuple[int, int, int, int, int, int]] = []
        used_char_fact = set()
        chosen_chars = []
        for _ in range(N_UPDATE_PAIRS):
            for _attempt in range(20):
                ch = int(self.rng.integers(0, N_CHARACTERS))
                fi = int(self.rng.integers(0, N_FACTS_PER_CHAR))
                if (ch, fi) not in used_char_fact:
                    used_char_fact.add((ch, fi))
                    chosen_chars.append((ch, fi))
                    break

        q1_max = max(1, N_EVENTS // 4)
        q4_min = max(q1_max + 1, (3 * N_EVENTS) // 4)
        for ch, fi in chosen_chars:
            ev_early = int(self.rng.integers(2, q1_max))
            ev_late = int(self.rng.integers(q4_min, N_EVENTS - 1))
            v_early = int(self.rng.integers(0, N_JOBS))
            v_late = v_early
            while v_late == v_early:
                v_late = int(self.rng.integers(0, N_JOBS))
            update_pairs.append((ch, fi, v_early, v_late, ev_early, ev_late))

        update_lookup = {}
        for ch, fi, ve, vl, ee, le in update_pairs:
            update_lookup[ee] = (ch, fi, ve, "early")
            update_lookup[le] = (ch, fi, vl, "late")

        static_facts: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for ch in range(N_CHARACTERS):
            for fi in range(N_FACTS_PER_CHAR):
                if (ch, fi) not in used_char_fact:
                    val = int(self.rng.integers(0, N_JOBS))
                    ev = int(self.rng.integers(1, max(2, N_EVENTS // 2)))
                    static_facts[(ch, fi)] = (val, ev)

        static_by_event: Dict[int, List[Tuple[int, int, int]]] = {}
        for (ch, fi), (val, ev) in static_facts.items():
            static_by_event.setdefault(ev, []).append((ch, fi, val))

        reserved_events = set(update_lookup.keys()) | set(static_by_event.keys())
        pronoun_event_idxs: set = set()
        if N_PRONOUN_EVENTS > 0:
            cand_events = [ev for ev in range(K_SCENE_BOUNDARY + 1, N_EVENTS)
                           if ev not in reserved_events]
            self.rng.shuffle(cand_events)
            for ev in cand_events[:N_PRONOUN_EVENTS]:
                pronoun_event_idxs.add(int(ev))

        # First pass: assign char_id to non-pronoun events (this fixes the
        # actual mention history that the substrate will encode).
        # We need this BEFORE deciding non-focus pronoun targets, because the
        # target candidates for a non-focus pronoun must be characters who
        # already appeared earlier in the same scene.
        events_by_scene: Dict[int, List[int]] = {}
        for ev_idx in range(N_EVENTS):
            scene_id = ev_idx // K_SCENE_BOUNDARY
            ev: Dict = {
                "event_idx": ev_idx,
                "scene_id": scene_id,
                "is_pronoun": False,
                "fact_kind": None,
                "fact_idx": None,
                "fact_val": None,
            }
            if ev_idx in update_lookup:
                ch, fi, val, kind = update_lookup[ev_idx]
                ev["char_id"] = ch
                ev["fact_kind"] = kind
                ev["fact_idx"] = fi
                ev["fact_val"] = val
                self.char_facts.setdefault((ch, fi), []).append((val, ev_idx))
            elif ev_idx in static_by_event:
                ch, fi, val = static_by_event[ev_idx][0]
                ev["char_id"] = ch
                ev["fact_kind"] = "static"
                ev["fact_idx"] = fi
                ev["fact_val"] = val
                self.char_facts.setdefault((ch, fi), []).append((val, ev_idx))
            elif ev_idx in pronoun_event_idxs:
                # Defer pronoun target assignment to second pass
                ev["is_pronoun"] = True
                ev["char_id"] = -1
            else:
                # Non-special event: with high prob, scene_focus; otherwise random.
                if self.rng.random() < 0.60:
                    ev["char_id"] = scene_focus[scene_id]
                else:
                    ev["char_id"] = int(self.rng.integers(0, N_CHARACTERS))

            ev["verb_id"] = int(self.rng.integers(0, N_VERBS))
            ev["obj_id"] = int(self.rng.integers(0, N_OBJECTS))
            ev["role_tag_idx"] = (ev["verb_id"] * 17 + ev["obj_id"] * 31) % (N_VERBS * N_OBJECTS)
            ev["is_subject_role"] = (ev["verb_id"] % 2 == 0)
            self.events.append(ev)
            events_by_scene.setdefault(scene_id, []).append(ev_idx)

        # Second pass: assign pronoun targets
        # With prob non_focus_frac: target a NON-focus character who already
        # appeared earlier in this scene (the substrate-non-trivial case).
        # With prob 1-non_focus_frac: target scene_focus[scene_id].
        n_non_focus_actual = 0
        for ev_idx in pronoun_event_idxs:
            scene_id = ev_idx // K_SCENE_BOUNDARY
            ev = self.events[ev_idx]
            # Find characters who appeared in this scene STRICTLY BEFORE ev_idx
            prior_chars_in_scene = set()
            for prior_idx in events_by_scene.get(scene_id, []):
                if prior_idx >= ev_idx:
                    continue
                prior_ev = self.events[prior_idx]
                if not prior_ev.get("is_pronoun") and prior_ev["char_id"] >= 0:
                    prior_chars_in_scene.add(prior_ev["char_id"])
            non_focus_candidates = sorted(prior_chars_in_scene - {scene_focus[scene_id]})

            if (self.rng.random() < self.non_focus_frac and
                    len(non_focus_candidates) >= 1):
                # Pick a non-focus character from those who appeared in scene
                target = int(self.rng.choice(non_focus_candidates))
                ev["char_id"] = target
                ev["_pronoun_target_kind"] = "non_focus"
                n_non_focus_actual += 1
            else:
                # Fall back to scene-focus (v1 default behavior)
                ev["char_id"] = scene_focus[scene_id]
                ev["_pronoun_target_kind"] = "scene_focus"

        self.scene_focus = scene_focus
        self.n_scenes = n_scenes
        self.update_pairs = update_pairs
        self.static_facts = static_facts
        self.pronoun_event_idxs = pronoun_event_idxs
        self.n_non_focus_pronouns = n_non_focus_actual

    def make_queries(self) -> Dict[str, List[Dict]]:
        rng = _rng(self.seed_offset + 999)
        queries: Dict[str, List[Dict]] = {q: [] for q in QUERY_TYPES}

        static_keys = list(self.static_facts.keys())
        rng.shuffle(static_keys)
        for ch, fi in static_keys[:Q_PER_TYPE]:
            val, ev = self.static_facts[(ch, fi)]
            queries["Q1_factual"].append({
                "char_id": ch, "fact_idx": fi, "expected_val": val,
                "source_event_idx": ev,
            })

        pronoun_list = sorted(self.pronoun_event_idxs)
        rng.shuffle(pronoun_list)
        for ev_idx in pronoun_list[:Q_PER_TYPE]:
            ev = self.events[ev_idx]
            queries["Q2_coreference"].append({
                # The QUESTION inputs (observable at pronoun position): only ev_idx.
                # verb_id/obj_id/scene_id of the pronoun event ARE observable
                # surface tokens at the pronoun position itself; we include them
                # but feature extractors derive them via cosine-decode of the
                # pronoun's encoded raw vector (substrate-faithful).
                "event_idx": ev_idx,
                # The ANSWER (used only by ARM_ORACLE for scoring + ground-truth).
                "expected_char_id": ev["char_id"],
                # diagnostic: which pronoun-class (NOT used by mechanism arms).
                "_target_kind": ev.get("_pronoun_target_kind", "unknown"),
            })

        cand = [i for i in range(1, N_EVENTS)
                if (i % K_SCENE_BOUNDARY) > 0]
        rng.shuffle(cand)
        for ev_idx in cand[:Q_PER_TYPE]:
            queries["Q3_temporal"].append({
                "target_event_idx": ev_idx,
                "expected_prior_event_idx": ev_idx - 1,
            })

        for (ch, fi, ve, vl, ee, le) in self.update_pairs[:Q_PER_TYPE]:
            queries["Q4_contradict"].append({
                "char_id": ch, "fact_idx": fi,
                "early_val": ve, "late_val": vl,
                "early_event_idx": ee, "late_event_idx": le,
                "expected_val": vl,
            })

        return queries


# ---------------- vocabularies ----------------

def build_vocab(seed_offset: int) -> Dict[str, np.ndarray]:
    rng = _rng(seed_offset + 7777)
    n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
    V_ROLE = N_VERBS * N_OBJECTS
    vocab = {
        "chars_raw": random_bipolar((N_CHARACTERS, N_RAW), rng),
        "chars_cortex": random_bipolar((N_CHARACTERS, N_CORTEX), rng),
        "chars_part": random_bipolar((N_CHARACTERS, N_PART), rng),
        "verbs": random_bipolar((N_VERBS, N_RAW), rng),
        "objs":  random_bipolar((N_OBJECTS, N_RAW), rng),
        "jobs":  random_bipolar((N_JOBS, N_RAW), rng),
        "scenes": random_bipolar((n_scenes, N_RAW), rng),
        "facts": random_bipolar((N_FACTS_PER_CHAR, N_RAW), rng),
        "pronoun_tag": random_bipolar((N_RAW,), rng),
    }
    vocab["P_in"] = (rng.standard_normal((N_HIPPO, N_RAW)) /
                     math.sqrt(N_RAW)).astype(np.float64)
    vocab["P_hc"] = (rng.standard_normal((N_CORTEX, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    vocab["P_pc"] = (rng.standard_normal((N_PART, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    return vocab


def encode_event_raw(ev: Dict, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    if ev.get("is_pronoun"):
        char_v = vocab["pronoun_tag"]
    else:
        char_v = vocab["chars_raw"][ev["char_id"]]
    verb_v = vocab["verbs"][ev["verb_id"]]
    obj_v = vocab["objs"][ev["obj_id"]]
    scene_v = vocab["scenes"][ev["scene_id"]]
    raw = char_v + verb_v + obj_v + scene_v
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_key(ch: int, fi: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    raw = vocab["chars_raw"][ch] + vocab["facts"][fi]
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_val(val: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    return vocab["jobs"][val]


# ---------------- shared encoding pipeline ----------------

def _consolidate_scene_to_cortex(W_cortex: np.ndarray,
                                  scene_keys_c: List[np.ndarray],
                                  scene_vals_c: List[np.ndarray],
                                  rng: np.random.Generator) -> None:
    if not scene_keys_c:
        return
    m = len(scene_keys_c)
    for _ in range(N_REPLAY_CYCLES):
        order = np.arange(m)
        rng.shuffle(order)
        for i in order:
            hebbian_write(W_cortex, scene_keys_c[i], scene_vals_c[i], ETA_CORTEX)


def _build_event_keys_vals(events: List[Dict], vocab: Dict[str, np.ndarray],
                           ) -> Tuple[List[np.ndarray], List[np.ndarray],
                                       List[np.ndarray], List[np.ndarray]]:
    keys_h, vals_h, keys_c, vals_c = [], [], [], []
    P_in = vocab["P_in"]
    P_hc = vocab["P_hc"]
    for ev in events:
        e_raw = encode_event_raw(ev, vocab)
        kh = pattern_separate_sparse(e_raw, P_in, K_HIPPO_ACTIVE)
        pos_in_scene = ev["event_idx"] % K_SCENE_BOUNDARY
        kh_seq = permute_role_pos(kh, pos_in_scene)
        vh = kh_seq.copy()
        keys_h.append(kh_seq)
        vals_h.append(vh)
        keys_c.append(project_h_to_c(kh_seq, P_hc))
        vals_c.append(project_h_to_c(vh, P_hc))
    return keys_h, vals_h, keys_c, vals_c


def _encode_full_stack(narr: "Narrative", vocab: Dict[str, np.ndarray],
                       rng_arm: np.random.Generator,
                       keys_h: List[np.ndarray], vals_h: List[np.ndarray],
                       keys_c: List[np.ndarray], vals_c: List[np.ndarray],
                       ) -> Tuple[np.ndarray, Dict[int, np.ndarray],
                                   Dict[Tuple[int, int], Dict]]:
    """Shared cortex/partition encoding."""
    W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
    W_part: Dict[int, np.ndarray] = {}
    gen_W: Dict[Tuple[int, int], Dict] = {}

    for c in range(N_CHARACTERS):
        W_part[c] = np.zeros((N_PART, N_PART), dtype=np.float64)

    scene_keys_c: List[np.ndarray] = []
    scene_vals_c: List[np.ndarray] = []
    scene_partition_writes: List[Tuple[int, np.ndarray, np.ndarray]] = []
    scene_fact_writes: List[Tuple[int, int, int]] = []

    for i in range(N_EVENTS):
        ev = narr.events[i]
        scene_keys_c.append(keys_c[i])
        scene_vals_c.append(vals_c[i])
        if not ev.get("is_pronoun"):
            ch = ev["char_id"]
            key_pc = project_h_to_c(keys_h[i], vocab["P_pc"])
            val_pc = project_h_to_c(vals_h[i], vocab["P_pc"])
            scene_partition_writes.append((ch, key_pc, val_pc))
            if ev["fact_val"] is not None:
                scene_fact_writes.append((ch, ev["fact_idx"], ev["fact_val"]))
        if (i + 1) % K_SCENE_BOUNDARY == 0 or (i + 1) == N_EVENTS:
            _consolidate_scene_to_cortex(W_cortex, scene_keys_c, scene_vals_c,
                                          rng_arm)
            by_char: Dict[int, Tuple[List[np.ndarray], List[np.ndarray]]] = {}
            for ch, kp, vp in scene_partition_writes:
                by_char.setdefault(ch, ([], []))
                by_char[ch][0].append(kp)
                by_char[ch][1].append(vp)
            for ch, (ks, vs) in by_char.items():
                _consolidate_scene_to_cortex(W_part[ch], ks, vs, rng_arm)
            for ch, fi, val in scene_fact_writes:
                gen_W[(ch, fi)] = {
                    "latest_val": val,
                    "latest_event": i,
                    "generation": gen_W.get((ch, fi), {}).get("generation", 0) + 1,
                }
                kf_raw = encode_fact_key(ch, fi, vocab)
                kf_h = pattern_separate_sparse(kf_raw, vocab["P_in"], K_HIPPO_ACTIVE)
                kf_c = project_h_to_c(kf_h, vocab["P_hc"])
                vf_h = pattern_separate_sparse(encode_fact_val(val, vocab),
                                                vocab["P_in"], K_HIPPO_ACTIVE)
                vf_c = project_h_to_c(vf_h, vocab["P_hc"])
                hebbian_write(W_cortex, kf_c, vf_c, ETA_CORTEX)
            scene_keys_c, scene_vals_c = [], []
            scene_partition_writes = []
            scene_fact_writes = []

    return W_cortex, W_part, gen_W


# ============================================================================
# SUBSTRATE-FAITHFUL FEATURE EXTRACTORS (v2 fix to v1 oracle leak)
# ============================================================================
# All extractors below take ONLY:
#   - c (candidate character index)
#   - pronoun event's encoded probe (NOT its ground-truth fields)
#   - W_part[c], W_cortex (substrate state)
#   - vocab (canonical role vectors)
# They DO NOT access narr.events[*], narr.scene_focus, or any narrative-level
# ground-truth dict. Each f_* returns a scalar in [0, +inf).
# ============================================================================

def _build_probe_keys_at_positions(vocab: Dict[str, np.ndarray],
                                    ev_idx: int,
                                    n_back: int) -> List[Tuple[int, np.ndarray]]:
    """Build position-only probe keys for offsets 1..n_back back from ev_idx.

    A probe key is built using ONLY scene_vector + position_permutation_marker
    + char-agnostic (pronoun_tag) — NO char info, NO verb/obj info. The probe
    asks "did anything happen at position p in scene s, regardless of who".

    Substrate-faithful: scene_id at offset p is computable from p alone
    (deterministic from event index). pos_in_scene_permutation likewise.
    """
    probes: List[Tuple[int, np.ndarray]] = []
    for d in range(1, n_back + 1):
        p = ev_idx - d
        if p < 0:
            break
        scene_id_p = p // K_SCENE_BOUNDARY
        # Probe = scene_v + pronoun_tag (char-agnostic) + position permutation
        # This is the "what happened at position p in scene s" probe.
        scene_v = vocab["scenes"][scene_id_p]
        raw = scene_v + vocab["pronoun_tag"]
        raw = np.sign(raw)
        raw[raw == 0] = 1.0
        kh = pattern_separate_sparse(raw, vocab["P_in"], K_HIPPO_ACTIVE)
        pos_in_scene_p = p % K_SCENE_BOUNDARY
        kh_seq = permute_role_pos(kh, pos_in_scene_p)
        key_pc = project_h_to_c(kh_seq, vocab["P_pc"])
        probes.append((p, key_pc))
    return probes


def _feature_recency_substrate(c: int, ev_idx: int,
                                vocab: Dict[str, np.ndarray],
                                W_part: Dict[int, np.ndarray]) -> float:
    """Substrate-faithful recency: probe W_part[c] at each prior position with
    position-only key; sum exp(-lambda*d) * response_magnitude.

    Substrate-faithful because:
      - Probe keys derived from {scene_v, pos_permutation, pronoun_tag} -- no
        ground-truth char_id leaked.
      - Response = ||W_part[c] @ probe_key|| -- pure cosine-query against
        substrate state.
    """
    probes = _build_probe_keys_at_positions(vocab, ev_idx, RECENCY_LOOKBACK)
    Wc = W_part[c]
    total = 0.0
    for p, probe_key in probes:
        d = float(ev_idx - p)
        resp = Wc @ probe_key
        resp_mag = float(np.linalg.norm(resp))
        total += math.exp(-LAMBDA_RECENCY * d) * resp_mag
    return float(total)


def _feature_scene_substrate(c: int, ev_idx: int,
                              vocab: Dict[str, np.ndarray],
                              W_part: Dict[int, np.ndarray]) -> float:
    """Substrate-faithful scene-membership: probe W_part[c] with the SCENE-LEVEL
    aggregated key for the pronoun's scene; response magnitude = whether c was
    active in that scene.

    Substrate-faithful because:
      - scene_id of pronoun event derivable from ev_idx alone (deterministic).
      - Probe = aggregated scene_v + pronoun_tag -- no char_id info.
      - Response = ||W_part[c] @ scene_probe||.
    """
    scene_id = ev_idx // K_SCENE_BOUNDARY
    scene_v = vocab["scenes"][scene_id]
    # Aggregate scene-probe: sum over all positions in scene of position-only probe
    scene_start = scene_id * K_SCENE_BOUNDARY
    scene_end = min(N_EVENTS, scene_start + K_SCENE_BOUNDARY)
    Wc = W_part[c]
    total = 0.0
    for p in range(scene_start, min(ev_idx, scene_end)):
        raw = scene_v + vocab["pronoun_tag"]
        raw = np.sign(raw)
        raw[raw == 0] = 1.0
        kh = pattern_separate_sparse(raw, vocab["P_in"], K_HIPPO_ACTIVE)
        kh_seq = permute_role_pos(kh, p % K_SCENE_BOUNDARY)
        probe = project_h_to_c(kh_seq, vocab["P_pc"])
        resp = Wc @ probe
        total += float(np.linalg.norm(resp))
    return float(total)


def _feature_subject_substrate(c: int, ev_idx: int,
                                vocab: Dict[str, np.ndarray],
                                W_part: Dict[int, np.ndarray]) -> float:
    """Substrate-faithful subject-role frequency: probe W_part[c] with the
    aggregated "subject-role" key (sum of canonical role-vectors for even
    verb_ids; matches narrative's is_subject_role = (verb_id % 2 == 0)).

    NOTE: We use the canonical subject-role aggregator vocab["verbs"][even_idx]
    NOT narr.events[*]["is_subject_role"]. Substrate's response strength is a
    proxy for how often c was bound with subject-role verbs.
    """
    # Build aggregate subject-key from even-indexed verbs
    subject_v = np.zeros(N_RAW, dtype=np.float64)
    for v_idx in range(0, N_VERBS, 2):
        subject_v += vocab["verbs"][v_idx]
    subject_v = np.sign(subject_v)
    subject_v[subject_v == 0] = 1.0
    raw = subject_v + vocab["pronoun_tag"]
    raw = np.sign(raw)
    raw[raw == 0] = 1.0
    kh = pattern_separate_sparse(raw, vocab["P_in"], K_HIPPO_ACTIVE)
    probe = project_h_to_c(kh, vocab["P_pc"])
    resp = W_part[c] @ probe
    return float(np.linalg.norm(resp))


def _feature_focus_substrate(c: int, ev_idx: int,
                              vocab: Dict[str, np.ndarray],
                              W_cortex: np.ndarray,
                              pronoun_event_encoded_h: np.ndarray) -> float:
    """Substrate-faithful focus-salience: query W_cortex with the pronoun
    event's H-level encoded vector; readout via cosine over chars_cortex.
    Score = cosine similarity between W_cortex output and vocab["chars_cortex"][c].

    Substrate-faithful because:
      - W_cortex is the substrate's accumulated cortex store (Hebbian-written).
      - Pronoun event's encoded vector uses pronoun_tag (NOT chars_raw[true_id]).
      - Readout = cosine(W_cortex @ probe, chars_cortex[c]) -- substrate's OWN
        guess at what character "belongs" with this scene/event context.
      - Does NOT touch narr.scene_focus.
    """
    # Project pronoun event encoded vector through to cortex space
    pronoun_probe_c = project_h_to_c(pronoun_event_encoded_h, vocab["P_hc"])
    resp = W_cortex @ pronoun_probe_c
    # Compare to chars_cortex[c]
    return float(cosine_vec(resp, vocab["chars_cortex"][c]))


def _feature_parallel_substrate(c: int, ev_idx: int,
                                 vocab: Dict[str, np.ndarray],
                                 W_part: Dict[int, np.ndarray],
                                 pronoun_event_encoded_raw: np.ndarray) -> float:
    """Substrate-faithful parallelism: probe W_part[c] with the pronoun event's
    VERB+OBJ key (i.e., the role part of the pronoun event, extracted from its
    encoded raw form without the char_v contribution).

    Substrate-faithful because:
      - We DO NOT read narr.events[ev_idx]["verb_id"].
      - The pronoun event's raw encoded vector = sign(pronoun_tag + verb_v +
        obj_v + scene_v). To extract the verb/obj component we subtract the
        pronoun_tag + scene_v (both known surface-form components for the
        pronoun event's POSITION) and use the residual as the role probe.
      - Response = ||W_part[c] @ role_probe||.
    """
    scene_id = ev_idx // K_SCENE_BOUNDARY
    # The pronoun event's encoded vector contains pronoun_tag + verb + obj + scene.
    # Subtract scene + pronoun_tag (both observable from position): residual = verb+obj signed.
    scene_v = vocab["scenes"][scene_id]
    # Probe = the pronoun event's encoded vector minus the scene component
    # (which is a position-derived surface feature, not the answer).
    role_estimate = pronoun_event_encoded_raw - np.sign(scene_v + vocab["pronoun_tag"])
    role_estimate = np.sign(role_estimate)
    role_estimate[role_estimate == 0] = 1.0
    kh = pattern_separate_sparse(role_estimate, vocab["P_in"], K_HIPPO_ACTIVE)
    pos_in_scene = ev_idx % K_SCENE_BOUNDARY
    kh_seq = permute_role_pos(kh, pos_in_scene)
    probe = project_h_to_c(kh_seq, vocab["P_pc"])
    resp = W_part[c] @ probe
    return float(np.linalg.norm(resp))


# ---------------- READOUT FUNCTIONS (6 arms; ALL DISTINCT) ----------------

def q2_random_floor(seed_offset: int, ev_idx: int) -> int:
    rng = _rng(seed_offset + 222 + ev_idx)
    return int(rng.integers(0, N_CHARACTERS))


def q2_naive_magnitude(ev_idx: int, narr: "Narrative",
                       vocab: Dict[str, np.ndarray],
                       W_part: Dict[int, np.ndarray]) -> int:
    """Drill-1's failing readout reproduced. ALLOWED to read narr.events[ev_idx]
    because this arm baseline is the prior measured baseline; it's not the
    substrate-faithful candidate (Lappin-Leass is)."""
    ev = narr.events[ev_idx]
    cue_raw = encode_event_raw(ev, vocab)
    cue_h = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    pos = ev["event_idx"] % K_SCENE_BOUNDARY
    cue_h = permute_role_pos(cue_h, pos)
    cue_pc = project_h_to_c(cue_h, vocab["P_pc"])
    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        readout = W_part[c] @ cue_pc
        scores[c] = float(np.linalg.norm(readout))
    return int(np.argmax(scores))


def q2_cosine_only(ev_idx: int, vocab: Dict[str, np.ndarray],
                   W_cortex: np.ndarray,
                   pronoun_event_encoded_h: np.ndarray) -> int:
    """Substrate-faithful cosine baseline: query W_cortex with pronoun-encoded
    vector; readout via cosine over chars_cortex. This is the f_focus feature
    used alone as an argmax (the substrate's "best guess at scene context").

    Substrate-faithful: NO narr.events / narr.scene_focus reads.
    """
    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        scores[c] = _feature_focus_substrate(c, ev_idx, vocab, W_cortex,
                                              pronoun_event_encoded_h)
    return int(np.argmax(scores))


def q2_recency_only_substrate_faithful(ev_idx: int,
                                        vocab: Dict[str, np.ndarray],
                                        W_part: Dict[int, np.ndarray]) -> int:
    """Substrate-faithful recency arm: pure recency feature; argmax.

    Substrate-faithful: NO narr.events / narr.scene_focus reads.
    """
    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        scores[c] = _feature_recency_substrate(c, ev_idx, vocab, W_part)
    return int(np.argmax(scores))


def q2_lappin_leass_full_substrate_faithful(
        ev_idx: int,
        vocab: Dict[str, np.ndarray],
        W_part: Dict[int, np.ndarray],
        W_cortex: np.ndarray,
        pronoun_event_encoded_h: np.ndarray,
        pronoun_event_encoded_raw: np.ndarray) -> int:
    """THE MECHANISM: 5-feature weighted symbolic salience over substrate-queried
    features. All 5 features derive from cosine queries against substrate state;
    NO narr.events[*]["char_id"] / narr.scene_focus reads.
    """
    # Per-feature scores need normalization across candidates so weights make
    # sense (otherwise raw magnitudes from W_part queries dominate everything).
    raw_recency = np.zeros(N_CHARACTERS, dtype=np.float64)
    raw_scene = np.zeros(N_CHARACTERS, dtype=np.float64)
    raw_subject = np.zeros(N_CHARACTERS, dtype=np.float64)
    raw_focus = np.zeros(N_CHARACTERS, dtype=np.float64)
    raw_parallel = np.zeros(N_CHARACTERS, dtype=np.float64)

    for c in range(N_CHARACTERS):
        raw_recency[c] = _feature_recency_substrate(c, ev_idx, vocab, W_part)
        raw_scene[c] = _feature_scene_substrate(c, ev_idx, vocab, W_part)
        raw_subject[c] = _feature_subject_substrate(c, ev_idx, vocab, W_part)
        raw_focus[c] = _feature_focus_substrate(c, ev_idx, vocab, W_cortex,
                                                 pronoun_event_encoded_h)
        raw_parallel[c] = _feature_parallel_substrate(
            c, ev_idx, vocab, W_part, pronoun_event_encoded_raw)

    # Normalize each feature to [0, 1] across candidates (z = (x-min)/(max-min)
    # with safety for constant features)
    def _norm01(x: np.ndarray) -> np.ndarray:
        lo, hi = float(x.min()), float(x.max())
        if (hi - lo) < 1e-12:
            return np.zeros_like(x)
        return (x - lo) / (hi - lo)

    nrec = _norm01(raw_recency)
    nscn = _norm01(raw_scene)
    nsub = _norm01(raw_subject)
    nfoc = _norm01(raw_focus)
    npar = _norm01(raw_parallel)

    scores = (W_RECENCY  * nrec +
              W_SCENE    * nscn +
              W_SUBJECT  * nsub +
              W_FOCUS    * nfoc +
              W_PARALLEL * npar)
    return int(np.argmax(scores))


def q2_oracle(q: Dict[str, Any]) -> int:
    return int(q["expected_char_id"])


# ---------------- Q1/Q3/Q4 readouts (shared; not load-bearing for Q2) ----------------

def _build_S_sequence_matrix(narr: "Narrative",
                             keys_c: List[np.ndarray]) -> np.ndarray:
    n_dim = N_CORTEX
    S = np.zeros((n_dim, n_dim), dtype=np.float64)
    K_prev_rows = []
    K_curr_rows = []
    for s_id in range(narr.n_scenes):
        scene_evs = [i for i in range(N_EVENTS)
                     if (i // K_SCENE_BOUNDARY) == s_id]
        scene_evs.sort()
        if len(scene_evs) < 2:
            continue
        for j in range(1, len(scene_evs)):
            K_prev_rows.append(keys_c[scene_evs[j - 1]])
            K_curr_rows.append(keys_c[scene_evs[j]])
    if not K_prev_rows:
        return S
    K_prev = np.stack(K_prev_rows, axis=0)
    K_curr = np.stack(K_curr_rows, axis=0)
    S = (K_prev.T @ K_curr) / n_dim
    return S


def q1_factual(W_cortex: np.ndarray, ch: int, fi: int,
                vocab: Dict[str, np.ndarray]) -> int:
    key_raw = encode_fact_key(ch, fi, vocab)
    key_h = pattern_separate_sparse(key_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    key_c = project_h_to_c(key_h, vocab["P_hc"])
    cand = np.stack([project_h_to_c(
        pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
        vocab["P_hc"]) for j in range(N_JOBS)])
    raw = W_cortex @ key_c
    return cosine_argmax(raw, cand)


def q3_sequence_replay_readout(target_ev: int, n_events: int,
                                 keys_c: List[np.ndarray],
                                 S: np.ndarray) -> int:
    target_scene = target_ev // K_SCENE_BOUNDARY
    scene_members = [i for i in range(n_events)
                     if (i // K_SCENE_BOUNDARY) == target_scene and i != target_ev]
    if not scene_members:
        return -1
    target_key = keys_c[target_ev]
    predicted = S @ target_key
    cand_stack = np.stack([keys_c[i] for i in scene_members], axis=0)
    pred_local = cosine_argmax(predicted, cand_stack)
    return scene_members[pred_local]


def q4_contradict(ch: int, fi: int,
                   gen_W: Dict[Tuple[int, int], Dict]) -> int:
    if (ch, fi) in gen_W:
        return gen_W[(ch, fi)]["latest_val"]
    return 0


# ---------------- arm runner ----------------

def run_arm(arm: str, seed: int, non_focus_frac: float) -> Dict[str, Any]:
    t0 = time.time()
    seed_offset = int(seed) * 100003
    rng_arm = _rng(seed_offset + 31)

    narr = Narrative(seed_offset, non_focus_frac)
    vocab = build_vocab(seed_offset)
    queries = narr.make_queries()
    keys_h, vals_h, keys_c, vals_c = _build_event_keys_vals(narr.events, vocab)

    W_cortex, W_part, gen_W = _encode_full_stack(
        narr, vocab, rng_arm, keys_h, vals_h, keys_c, vals_c)

    S_replay = _build_S_sequence_matrix(narr, keys_c)

    preds_list: List[str] = []
    per_q: Dict[str, Dict[str, int]] = {q: {"correct": 0, "total": 0}
                                          for q in QUERY_TYPES}

    # Q1 factual
    for q in queries["Q1_factual"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 111 + ch * 13 + fi).integers(0, N_JOBS))
        else:
            pred = q1_factual(W_cortex, ch, fi, vocab)
        per_q["Q1_factual"]["total"] += 1
        per_q["Q1_factual"]["correct"] += int(pred == expected)
        preds_list.append("Q1:%d:%d:%d" % (ch, fi, pred))

    # Q2 coreference (arm-differentiated)
    # NOTE: we precompute pronoun_event_encoded_h once outside arm dispatch
    # because it's identical across arms (it's the raw encoding of the
    # pronoun event with pronoun_tag).
    per_q_q2_target_breakdown = {"non_focus": {"correct": 0, "total": 0},
                                  "scene_focus": {"correct": 0, "total": 0}}
    for q in queries["Q2_coreference"]:
        ev_idx = q["event_idx"]
        expected_char = q["expected_char_id"]
        target_kind = q.get("_target_kind", "unknown")
        # Build pronoun event encoded form (substrate-faithful: pronoun_tag
        # replaces true char; verb/obj/scene are observable at pronoun position).
        pron_ev = narr.events[ev_idx]
        pronoun_event_encoded_raw = encode_event_raw(pron_ev, vocab)
        pronoun_event_encoded_h = pattern_separate_sparse(
            pronoun_event_encoded_raw, vocab["P_in"], K_HIPPO_ACTIVE)
        pronoun_event_encoded_h = permute_role_pos(
            pronoun_event_encoded_h, ev_idx % K_SCENE_BOUNDARY)

        if arm == "ARM_RANDOM_FLOOR":
            pred = q2_random_floor(seed_offset, ev_idx)
        elif arm == "ARM_NAIVE_MAGNITUDE":
            pred = q2_naive_magnitude(ev_idx, narr, vocab, W_part)
        elif arm == "ARM_COSINE_ONLY":
            pred = q2_cosine_only(ev_idx, vocab, W_cortex,
                                   pronoun_event_encoded_h)
        elif arm == "ARM_RECENCY_ONLY_SUBSTRATE":
            pred = q2_recency_only_substrate_faithful(ev_idx, vocab, W_part)
        elif arm == "ARM_LAPPIN_LEASS_FULL_SUBSTRATE":
            pred = q2_lappin_leass_full_substrate_faithful(
                ev_idx, vocab, W_part, W_cortex,
                pronoun_event_encoded_h, pronoun_event_encoded_raw)
        elif arm == "ARM_ORACLE":
            pred = q2_oracle(q)
        else:
            raise ValueError("unknown arm: " + arm)
        per_q["Q2_coreference"]["total"] += 1
        per_q["Q2_coreference"]["correct"] += int(pred == expected_char)
        if target_kind in per_q_q2_target_breakdown:
            per_q_q2_target_breakdown[target_kind]["total"] += 1
            per_q_q2_target_breakdown[target_kind]["correct"] += int(pred == expected_char)
        preds_list.append("Q2:%d:%d" % (ev_idx, pred))

    # Q3 temporal
    for q in queries["Q3_temporal"]:
        target = q["target_event_idx"]
        expected = q["expected_prior_event_idx"]
        if arm == "ARM_RANDOM_FLOOR":
            target_scene = target // K_SCENE_BOUNDARY
            scene_members = [i for i in range(N_EVENTS)
                              if (i // K_SCENE_BOUNDARY) == target_scene
                              and i != target]
            if scene_members:
                idx = int(_rng(seed_offset + 333 + target).integers(
                    0, len(scene_members)))
                pred = scene_members[idx]
            else:
                pred = -1
        else:
            pred = q3_sequence_replay_readout(target, N_EVENTS, keys_c, S_replay)
        per_q["Q3_temporal"]["total"] += 1
        per_q["Q3_temporal"]["correct"] += int(pred == expected)
        preds_list.append("Q3:%d:%d" % (target, pred))

    # Q4 contradict
    for q in queries["Q4_contradict"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 444 + ch * 7 + fi).integers(0, N_JOBS))
        else:
            pred = q4_contradict(ch, fi, gen_W)
        per_q["Q4_contradict"]["total"] += 1
        per_q["Q4_contradict"]["correct"] += int(pred == expected)
        preds_list.append("Q4:%d:%d:%d" % (ch, fi, pred))

    acc_by_q = {}
    for q in QUERY_TYPES:
        tot = per_q[q]["total"]
        acc_by_q[q] = (per_q[q]["correct"] / tot) if tot > 0 else 0.0
    overall = float(np.mean(list(acc_by_q.values())))

    pred_sha = hashlib.sha256(
        ";".join(preds_list).encode("ascii")).hexdigest()[:16]
    q2_preds = [p for p in preds_list if p.startswith("Q2:")]
    q2_pred_sha = hashlib.sha256(
        ";".join(q2_preds).encode("ascii")).hexdigest()[:16]

    wall = float(round(time.time() - t0, 3))

    # Q2 per-target-kind accuracy (the load-bearing discriminator metric)
    q2_acc_non_focus = 0.0
    q2_acc_scene_focus = 0.0
    if per_q_q2_target_breakdown["non_focus"]["total"] > 0:
        q2_acc_non_focus = (per_q_q2_target_breakdown["non_focus"]["correct"] /
                            per_q_q2_target_breakdown["non_focus"]["total"])
    if per_q_q2_target_breakdown["scene_focus"]["total"] > 0:
        q2_acc_scene_focus = (per_q_q2_target_breakdown["scene_focus"]["correct"] /
                               per_q_q2_target_breakdown["scene_focus"]["total"])

    return {
        "arm": arm,
        "seed": int(seed),
        "non_focus_frac": non_focus_frac,
        "N_h": N_HIPPO, "N_c": N_CORTEX, "N_part": N_PART,
        "N_events": N_EVENTS, "N_chars": N_CHARACTERS,
        "K_scene": K_SCENE_BOUNDARY, "Q_per_type": Q_PER_TYPE,
        "weights": {
            "W_RECENCY": W_RECENCY, "W_SCENE": W_SCENE,
            "W_SUBJECT": W_SUBJECT, "W_FOCUS": W_FOCUS,
            "W_PARALLEL": W_PARALLEL, "LAMBDA_RECENCY": LAMBDA_RECENCY,
        },
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "acc_by_q": acc_by_q,
        "overall": round(overall, 4),
        "Q1_factual": round(acc_by_q["Q1_factual"], 4),
        "Q2_coreference": round(acc_by_q["Q2_coreference"], 4),
        "Q2_coref_non_focus_only": round(q2_acc_non_focus, 4),
        "Q2_coref_scene_focus_only": round(q2_acc_scene_focus, 4),
        "Q2_n_non_focus": per_q_q2_target_breakdown["non_focus"]["total"],
        "Q2_n_scene_focus": per_q_q2_target_breakdown["scene_focus"]["total"],
        "Q3_temporal": round(acc_by_q["Q3_temporal"], 4),
        "Q4_contradict": round(acc_by_q["Q4_contradict"], 4),
        "n_q_total": sum(per_q[q]["total"] for q in QUERY_TYPES),
        "n_non_focus_pronouns_in_corpus": narr.n_non_focus_pronouns,
        "pred_sha": pred_sha,
        "q2_pred_sha": q2_pred_sha,
        "elapsed_s_arm": wall,
        "_partial_written_at": time.time(),
    }


# ---------------- verdict ----------------

def _classify(per_arm: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
    floor = per_arm.get("ARM_RANDOM_FLOOR", {})
    naive = per_arm.get("ARM_NAIVE_MAGNITUDE", {})
    cosine_only = per_arm.get("ARM_COSINE_ONLY", {})
    rec = per_arm.get("ARM_RECENCY_ONLY_SUBSTRATE", {})
    lappin = per_arm.get("ARM_LAPPIN_LEASS_FULL_SUBSTRATE", {})
    oracle = per_arm.get("ARM_ORACLE", {})

    if not all([floor, naive, cosine_only, rec, lappin, oracle]):
        return "HARD_FAIL", "MISSING_ARM_RESULTS"

    floor_q2 = floor.get("Q2_coreference", 0.0)
    naive_q2 = naive.get("Q2_coreference", 0.0)
    cosine_q2 = cosine_only.get("Q2_coreference", 0.0)
    rec_q2 = rec.get("Q2_coreference", 0.0)
    lappin_q2 = lappin.get("Q2_coreference", 0.0)
    oracle_q2 = oracle.get("Q2_coreference", 0.0)

    lappin_nf = lappin.get("Q2_coref_non_focus_only", 0.0)
    cosine_nf = cosine_only.get("Q2_coref_non_focus_only", 0.0)
    naive_nf = naive.get("Q2_coref_non_focus_only", 0.0)

    # Operational baseline = max(naive, cosine_only) — both are 1-feature
    # substrate-faithful baselines; mechanism must beat the stronger of them.
    operational_baseline = max(naive_q2, cosine_q2)
    lift_over_baseline = lappin_q2 - operational_baseline

    # META_RULE_AF arms-must-differ
    q2_shas = set()
    for arm_name in ARMS:
        d = per_arm.get(arm_name, {})
        sha = d.get("q2_pred_sha", "")
        if sha:
            q2_shas.add(sha)
    arms_distinct = len(q2_shas)

    # ORACLE sanity
    if oracle_q2 < HP_ORACLE_Q2:
        return ("HARD_FAIL",
                "HF_ORACLE_BROKEN: ARM_ORACLE Q2=%.3f < %.3f. "
                "lappin=%.3f naive=%.3f cosine_only=%.3f."
                % (oracle_q2, HP_ORACLE_Q2, lappin_q2, naive_q2, cosine_q2))

    # META_RULE_AF arms must produce distinct Q2 pred_sha. NEW: if LAPPIN's
    # q2_pred_sha equals COSINE_ONLY's, the mechanism is just argmax-cosine in
    # disguise (= over-weighting f_focus). HARD_FAIL.
    naive_q2_sha = naive.get("q2_pred_sha", "")
    cosine_q2_sha = cosine_only.get("q2_pred_sha", "")
    lappin_q2_sha = lappin.get("q2_pred_sha", "")
    if lappin_q2_sha and naive_q2_sha and lappin_q2_sha == naive_q2_sha:
        return ("HARD_FAIL",
                "HF_PRED_SHA_COLLISION_NAIVE: ARM_LAPPIN_LEASS_FULL_SUBSTRATE Q2 pred_sha=%s "
                "equals ARM_NAIVE_MAGNITUDE pred_sha=%s. Symbolic scorer collapses to naive."
                % (lappin_q2_sha, naive_q2_sha))
    if lappin_q2_sha and cosine_q2_sha and lappin_q2_sha == cosine_q2_sha:
        return ("HARD_FAIL",
                "HF_PRED_SHA_COLLISION_COSINE: ARM_LAPPIN_LEASS_FULL_SUBSTRATE Q2 pred_sha=%s "
                "equals ARM_COSINE_ONLY pred_sha=%s. Symbolic scorer = pure cosine readout "
                "(W_FOCUS dominating other features; no mechanism beyond cosine argmax)."
                % (lappin_q2_sha, cosine_q2_sha))

    if lappin_q2 <= HF_LAPPIN_LEASS_Q2_MAX:
        return ("HARD_FAIL",
                "HF_LAPPIN_LEASS_BELOW_FLOOR: ARM_LAPPIN_LEASS_FULL_SUBSTRATE Q2=%.3f <= %.3f. "
                "DRILL 2 v2 substrate-faithful Lappin-Leass HARD_FAIL. "
                "Combined with DRILL 1 (HRR recency-sequence) HARD_FAIL, "
                "2x-drill-before-capability-closure rule satisfied: Q2 coref "
                "capability box CLOSES on substrate-native paths. "
                "naive=%.3f cosine_only=%.3f rec=%.3f oracle=%.3f floor=%.3f "
                "lappin_non_focus_only=%.3f cosine_non_focus_only=%.3f."
                % (lappin_q2, HF_LAPPIN_LEASS_Q2_MAX, naive_q2, cosine_q2,
                   rec_q2, oracle_q2, floor_q2, lappin_nf, cosine_nf))

    if lift_over_baseline <= HF_LIFT_OVER_BASELINE_MAX:
        return ("HARD_FAIL",
                "HF_NO_LIFT: lift_over_baseline=%.3f <= %.3f. "
                "lappin_Q2=%.3f naive_Q2=%.3f cosine_only_Q2=%.3f. "
                "Mechanism does not extract information beyond strongest 1-feature substrate baseline."
                % (lift_over_baseline, HF_LIFT_OVER_BASELINE_MAX, lappin_q2, naive_q2, cosine_q2))

    if arms_distinct < HP_ARMS_DISTINCT_MIN:
        return ("HARD_FAIL",
                "HF_ARMS_NOT_DISTINCT: only %d distinct Q2 pred_sha across "
                "%d arms (need >= %d). shas=%s"
                % (arms_distinct, len(ARMS), HP_ARMS_DISTINCT_MIN,
                   sorted(q2_shas)))

    hp_main = (lappin_q2 >= HP_LAPPIN_LEASS_Q2_MIN and
               lift_over_baseline >= HP_LIFT_OVER_BASELINE and
               oracle_q2 >= HP_ORACLE_Q2 and
               arms_distinct >= HP_ARMS_DISTINCT_MIN)

    if hp_main:
        return ("HARD_PASS",
                "HARD_PASS_DRILL2_v2_LAPPIN_LEASS_SUBSTRATE_FAITHFUL: "
                "ARM_LAPPIN_LEASS_FULL_SUBSTRATE Q2=%.3f >=%.2f AND "
                "lift_over_baseline=%.3f >=%.2f (baseline=max(naive=%.3f, cosine_only=%.3f)) "
                "AND ARM_ORACLE=%.3f AND arms_distinct=%d. "
                "Substrate-faithful (no oracle leak) 5-feature symbolic scorer over "
                "cosine-query-extracted features beats strongest 1-feature substrate baseline. "
                "lappin_non_focus_only=%.3f cosine_non_focus_only=%.3f naive_non_focus_only=%.3f "
                "rec=%.3f floor=%.3f."
                % (lappin_q2, HP_LAPPIN_LEASS_Q2_MIN, lift_over_baseline,
                   HP_LIFT_OVER_BASELINE, naive_q2, cosine_q2, oracle_q2,
                   arms_distinct, lappin_nf, cosine_nf, naive_nf, rec_q2, floor_q2))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: lappin_Q2=%.3f (HP>=%.2f HF<=%.2f) "
            "lift_over_baseline=%.3f (HP>=%.2f HF<=%.2f) "
            "naive=%.3f cosine_only=%.3f rec=%.3f oracle=%.3f "
            "arms_distinct=%d. lappin_non_focus_only=%.3f cosine_non_focus_only=%.3f."
            % (lappin_q2, HP_LAPPIN_LEASS_Q2_MIN, HF_LAPPIN_LEASS_Q2_MAX,
               lift_over_baseline, HP_LIFT_OVER_BASELINE, HF_LIFT_OVER_BASELINE_MAX,
               naive_q2, cosine_q2, rec_q2, oracle_q2,
               arms_distinct, lappin_nf, cosine_nf))


# ---------------- self-test ----------------

def _selftest() -> int:
    """Smoke gate. MUST fire discriminator: ARM_LAPPIN_LEASS_FULL_SUBSTRATE
    must produce a Q2 pred_sha distinct from both ARM_NAIVE_MAGNITUDE and
    ARM_COSINE_ONLY (otherwise the mechanism is a baseline in disguise)."""
    print("[selftest] config: %s" % CONFIG_VERSION, flush=True)
    print("[selftest] EXPECTED_N_UNITS=%d (seeds=%d arms=%d)"
          % (EXPECTED_N_UNITS, len(SEEDS), len(ARMS)), flush=True)
    print("[selftest] NON_FOCUS_PRONOUN_FRAC=%.2f" % NON_FOCUS_PRONOUN_FRAC,
          flush=True)
    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        try:
            result = run_arm(arm, SEED_ACTIVE, NON_FOCUS_PRONOUN_FRAC)
        except SystemExit:
            raise
        except BaseException as e:
            print("[selftest] ARM %s CRASHED: %r" % (arm, e), flush=True)
            traceback.print_exc()
            return 1
        per_arm[arm] = result
        print("[selftest] arm=%s Q2=%.3f Q2_nonfocus=%.3f Q2_scenefocus=%.3f overall=%.3f "
              "q2_sha=%s wall=%.2fs"
              % (arm, result["Q2_coreference"],
                 result["Q2_coref_non_focus_only"],
                 result["Q2_coref_scene_focus_only"],
                 result["overall"], result["q2_pred_sha"],
                 result["elapsed_s_arm"]), flush=True)
    verdict, msg = _classify(per_arm)
    print("[selftest] verdict=%s" % verdict, flush=True)
    print("[selftest] verdict_msg=%s" % msg, flush=True)

    # Sanity 1: oracle
    oracle_q2 = per_arm["ARM_ORACLE"]["Q2_coreference"]
    if oracle_q2 < 1.0 - 1e-9:
        print("[selftest] FAIL: ORACLE Q2=%.3f != 1.000 (narrative-gen bug)"
              % oracle_q2, flush=True)
        return 1

    # Sanity 2: arms-must-differ
    q2_shas = set(r["q2_pred_sha"] for r in per_arm.values())
    print("[selftest] Q2 distinct pred_shas across %d arms: %d"
          % (len(ARMS), len(q2_shas)), flush=True)
    if len(q2_shas) < HP_ARMS_DISTINCT_MIN:
        print("[selftest] FAIL: arms_distinct=%d < %d"
              % (len(q2_shas), HP_ARMS_DISTINCT_MIN), flush=True)
        return 1

    # DISCRIMINATOR-FIRES gate: lappin must differ from naive AND cosine_only.
    lappin_sha = per_arm["ARM_LAPPIN_LEASS_FULL_SUBSTRATE"]["q2_pred_sha"]
    naive_sha = per_arm["ARM_NAIVE_MAGNITUDE"]["q2_pred_sha"]
    cosine_sha = per_arm["ARM_COSINE_ONLY"]["q2_pred_sha"]
    if lappin_sha == naive_sha:
        print("[selftest] FAIL_DISCRIMINATOR_NOT_FIRED: LAPPIN_LEASS == NAIVE pred_sha.",
              flush=True)
        return 1
    if lappin_sha == cosine_sha:
        print("[selftest] FAIL_DISCRIMINATOR_NOT_FIRED: LAPPIN_LEASS == COSINE_ONLY pred_sha. "
              "Mechanism = pure cosine readout (W_FOCUS dominating).",
              flush=True)
        return 1

    # ORACLE_LEAK_GUARD_CHECK: verify no scene_focus / events char_id read in
    # substrate-faithful function bodies (extra runtime check).
    # The module-load guard already enforced this; here we report ack.
    print("[selftest] ORACLE_LEAK_GUARD: PASS (module-load self-grep accepted)",
          flush=True)

    # Discriminator FIRE check: at NON_FOCUS_FRAC=0.3, lappin lift over
    # max(naive, cosine_only) must be >= 0.15 OR self-test reports as
    # WARN_DISCRIMINATOR_MARGINAL (not auto-fail; verdict path classifies).
    lappin_q2 = per_arm["ARM_LAPPIN_LEASS_FULL_SUBSTRATE"]["Q2_coreference"]
    naive_q2 = per_arm["ARM_NAIVE_MAGNITUDE"]["Q2_coreference"]
    cosine_q2 = per_arm["ARM_COSINE_ONLY"]["Q2_coreference"]
    operational_baseline = max(naive_q2, cosine_q2)
    lift = lappin_q2 - operational_baseline
    print("[selftest] SMOKE_DISCRIMINATOR: lappin_Q2=%.3f baseline=max(naive=%.3f,cosine=%.3f)=%.3f lift=%+.3f"
          % (lappin_q2, naive_q2, cosine_q2, operational_baseline, lift),
          flush=True)
    if lift < HP_LIFT_OVER_BASELINE:
        print("[selftest] DISCRIMINATOR_DOES_NOT_FIRE_IN_SMOKE: lift=%+.3f < HP_LIFT=%.2f. "
              "This is STRONG NEGATIVE evidence: substrate-faithful Lappin-Leass "
              "does not lift above strongest 1-feature substrate baseline at smoke regime. "
              "Cell will atomize as HARD_FAIL drill 2 result; combined with drill 1 HARD_FAIL "
              "the Q2 coref capability box closes (2x-drill rule)."
              % (lift, HP_LIFT_OVER_BASELINE), flush=True)
        # NOT auto-fail; we WANT to see the negative result in full dispatch.

    if verdict not in ("HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"):
        print("[selftest] FAIL: unknown verdict=%s" % verdict, flush=True)
        return 1

    print("[selftest] PASS: oracle=1.000 arms_distinct=%d discriminator_arms_distinct=True "
          "verdict_assembled=%s lift=%+.3f"
          % (len(q2_shas), verdict, lift), flush=True)
    return 0


# ---------------- main ----------------

def main() -> int:
    if _ARGS.self_test:
        return _selftest()

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Defensive §13 pattern 1: start_marker
    start_marker_tmp = out_dir / "_start_marker.txt.tmp"
    start_marker_final = out_dir / "_start_marker.txt"
    start_marker_tmp.write_text(
        "started=%s\nconfig=%s\nseed=%d\nmode=%s\npid=%d\nnon_focus_frac=%.2f\n"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           CONFIG_VERSION, SEED_ACTIVE, RUN_MODE, os.getpid(),
           NON_FOCUS_PRONOUN_FRAC),
        encoding="utf-8")
    os.replace(str(start_marker_tmp), str(start_marker_final))

    seed = SEED_ACTIVE
    run_config = {"anchor": ANCHOR_NAME, "run_mode": RUN_MODE,
                  "non_focus_frac": NON_FOCUS_PRONOUN_FRAC}

    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        unit_key = "seed%d_%s" % (seed, arm)
        completed = list_completed_keys(out_dir, run_config=run_config)
        if unit_key in completed:
            partials = aggregate_partials(out_dir, [unit_key],
                                            run_config=run_config)
            if unit_key in partials:
                per_arm[arm] = partials[unit_key]
                print("[resume] skipping completed unit %s" % unit_key,
                      flush=True)
                continue

        print("[run] seed=%d arm=%s starting..." % (seed, arm), flush=True)
        try:
            result = run_arm(arm, seed, NON_FOCUS_PRONOUN_FRAC)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("[CRASH] arm=%s seed=%d: %r" % (arm, seed, e), flush=True)
            crash_path = out_dir / ("_crash_%s.txt" % unit_key)
            crash_path.write_text(
                "%s\n%r\n%s\n" % (time.time(), e, traceback.format_exc()),
                encoding="utf-8")
            return 2

        result["_ckpt_key"] = unit_key
        result["anchor_name"] = ANCHOR_NAME
        write_partial_key(out_dir, unit_key, result)
        per_arm[arm] = result
        # heartbeat
        hb_tmp = out_dir / "_heartbeat.txt.tmp"
        hb_final = out_dir / "_heartbeat.txt"
        hb_tmp.write_text(
            "last_unit=%s\nat=%s\n" % (unit_key, time.time()),
            encoding="utf-8")
        os.replace(str(hb_tmp), str(hb_final))
        print("[done] %s Q2=%.3f Q2_nonfocus=%.3f q2_sha=%s wall=%.2fs"
              % (unit_key, result["Q2_coreference"],
                 result["Q2_coref_non_focus_only"], result["q2_pred_sha"],
                 result["elapsed_s_arm"]), flush=True)

    observed = len(per_arm)
    cardinality_ok = (observed == EXPECTED_N_UNITS)
    if not cardinality_ok:
        print("[WARN] CARDINALITY_BREACH: expected %d, observed %d"
              % (EXPECTED_N_UNITS, observed), flush=True)

    verdict, verdict_msg = _classify(per_arm)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH: expected %d arms got %d. "
                       % (EXPECTED_N_UNITS, observed)) + verdict_msg

    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:300],
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seed": SEED_ACTIVE,
        "seeds": SEEDS,
        "arms": list(ARMS),
        "config_version": CONFIG_VERSION,
        "corpus_provenance": CORPUS_PROVENANCE,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": observed,
        "cardinality_ok": cardinality_ok,
        "non_focus_pronoun_frac": NON_FOCUS_PRONOUN_FRAC,
        "per_arm": per_arm,
        "_llm_forward_calls_at_inference": 0,
        "zero_llm_calls_at_inference": True,
        "elapsed_s": float(round(
            sum(r.get("elapsed_s_arm", 0.0) for r in per_arm.values()), 3)),
        "drill_index": 2,
        "drill_version": "v2_substrate_faithful_post_skunkworks_invalidation",
        "skunkworks_v1_invalidation_commit": "f60880f7",
        "v2_fixes_to_v1": [
            "ORACLE_LEAK_GUARD: module-load self-grep of source for narr.scene_focus / narr.events[*][char_id|scene_id|role_tag_idx|is_subject_role] in substrate-faithful function bodies",
            "Substrate-faithful feature extractors: every f_* derives signal from cosine query against W_part[c] / W_cortex / vocab",
            "Corpus diversification: NON_FOCUS_PRONOUN_FRAC parameter controls fraction of pronouns targeting non-focus characters",
            "Operational baseline = max(NAIVE_MAGNITUDE, COSINE_ONLY) -- both substrate-faithful 1-feature baselines",
            "ARM_COSINE_ONLY added as substrate-faithful 1-feature baseline (replaces v1 ARM_SCENE_FOCUS_ONLY which was oracle)",
        ],
        "arms_must_differ_q2_pred_sha": {
            arm: per_arm.get(arm, {}).get("q2_pred_sha", "") for arm in ARMS
        },
        "bands": {
            "HP_LAPPIN_LEASS_Q2_MIN": HP_LAPPIN_LEASS_Q2_MIN,
            "HP_LIFT_OVER_BASELINE": HP_LIFT_OVER_BASELINE,
            "HP_ORACLE_Q2": HP_ORACLE_Q2,
            "HP_ARMS_DISTINCT_MIN": HP_ARMS_DISTINCT_MIN,
            "HF_LAPPIN_LEASS_Q2_MAX": HF_LAPPIN_LEASS_Q2_MAX,
            "HF_LIFT_OVER_BASELINE_MAX": HF_LIFT_OVER_BASELINE_MAX,
        },
        "lappin_leass_weights": {
            "W_RECENCY": W_RECENCY, "W_SCENE": W_SCENE,
            "W_SUBJECT": W_SUBJECT, "W_FOCUS": W_FOCUS,
            "W_PARALLEL": W_PARALLEL, "LAMBDA_RECENCY": LAMBDA_RECENCY,
        },
        "prior_drill_evidence": {
            "drill_1_anchor": "substrate_narrative_q2_recency_sequence_log_v1",
            "drill_1_verdict": "HARD_FAIL",
            "drill_1_composition_Q2": 0.125,
            "drill_2_v1_anchor": "substrate_narrative_q2_coref_lappin_leass_drill2_v1",
            "drill_2_v1_skunkworks_status": "ORACLE_LEAK_INVALID",
            "drill_2_v1_invalidation_commit": "f60880f7",
        },
    }
    write_metrics(out_dir, metrics,
                   results=[per_arm[a] for a in ARMS if a in per_arm])
    print("[ship] %s verdict=%s" % (ANCHOR_NAME, verdict), flush=True)
    print("[ship] verdict_msg=%s" % verdict_msg, flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            out_dir = get_output_dir(ANCHOR_NAME)
            out_dir.mkdir(parents=True, exist_ok=True)
            import json as _json
            diag = {
                "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}",
                "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000],
                "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "pid": os.getpid(),
                "anchor_name": ANCHOR_NAME,
            }
            tmp = out_dir / "metrics.json.tmp"
            final = out_dir / "metrics.json"
            tmp.write_text(_json.dumps(diag, indent=2), encoding="utf-8")
            os.replace(str(tmp), str(final))
        except Exception:
            pass
        raise
    raise SystemExit(rc)
