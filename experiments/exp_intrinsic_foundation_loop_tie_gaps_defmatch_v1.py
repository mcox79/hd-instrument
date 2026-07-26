"""exp_intrinsic_foundation_loop_tie_gaps_defmatch_v1 -- swap the DECISION MEANING-MATCH to
DEFINITIONAL STRUCTURE at the reasoner's tie seam, as the BOOTSTRAP that de-risks the earn-it build B.

The VET-cleared powered loop (banked 29573) proved that acquiring the RIGHT definitional fact resolves the
reasoner's tie-gaps (ARM1 oracle 0.5312 vs ARM3global scramble 0.3672, McNemar p=0.00985) but is CAPPED: the
oracle ceiling is only 0.531 and the autonomous arm (ARM2 0.4688) does NOT clear the global scramble. Both
caps are attributed to the MATCH being thin-GloVe cosine over augmented choice-text vs stem: near-synonym
choice tokens ({solute,dissolved,water} vs {solvent,dissolved,water}) collapse to one blended vector.

THE ONE CHANGE = the decision meaning-match. Instead of a flat GloVe cosine of (choice_label + concatenated
fact-texts) vs stem (v1.decide_by_meaning), match on DEFINITIONAL STRUCTURE: keep the role/relation structure,
DROP the near-synonym concept label, and score each definitional PREDICATE (the role-filler = the fact object
recovered GLASS-BOX from the hd_fact_store trust-gate) SEPARATELY against the stem, taking the best-aligned
role-filler. profile_C = list of (relation, object) recovered by unbind from an HDFactStore ingest of choice
C's WorldTree facts (TRUST_HIGH). This is assignment-lookup on abstract science concepts (propositional
grounding via role-slot HD bindings), NOT a borrowed concept vector.

REUSE (do NOT rebuild): the leak-free arms + tie population + controls from powered_v1 (build_pool, mcnemar,
_breakdown; n=128 genuine ties Easy+Challenge) and v1 (decide_by_meaning, retrieve_fact_ids, _select_facts,
autonomous_facts, scramble_facts, build_acq_index, _valid_choices, _l2); hd_fact_store.HDFactStore;
WorldTree tablestore v2.1 (KINDOF/USEDFOR/CAUSE/PROP-*/SYNONYMY... via parse_tablestore_typed).

ARMS (isolate the match as the one variable):
  REUSED UNCHANGED (imported -> reproduce powered EXACT positive control): ARM0/FLOOR/ARM1/ARM2/ARM3global.
  NEW def-structure arms (role-slot profile via the trust-gate, glass-box recovered):
    ARM_DEF      def_oracle_grounded    -- def match over ORACLE facts (same fids as ARM1); ONE var vs ARM1 = match.
    ARM_DEF_AUTO def_auto_grounded      -- def match over AUTONOMOUS facts (same fids as ARM2); ONE var vs ARM2 = match.
    ARM_DEF_SCR  def_scramble_global    -- def match over globally-scrambled oracle facts (MUST-FAIL for the new match).
    ARM_DEF_SYM  def_oracle_symbolic    -- GloVe-FREE rarity-weighted content-word overlap (propositional; diagnostic for B).

CONTRACT (pre-registered, can-fail):
  HARD_PASS = def-structure match significantly LIFTS the ceiling AND/OR moves the autonomous arm to clear
    scramble: (ARM_DEF vs ARM1 McNemar p<0.05 AND arm_def>arm1) OR (ARM_DEF_AUTO vs ARM_DEF_SCR McNemar p<0.05
    AND arm_def_auto>arm_def_scr). => target REAL, greenlights earn-it build B.
  HONEST_NEG = no lift over the GloVe match => definitional structure ALONE insufficient (decisive: saves B,
    routes to a different grounding).
  Guardrails (for HARD_PASS): gold_only preserved @1.00; positive control reproduces powered EXACT.
  Reports per-arm accs, ALL McNemar contrasts (p + discordant b/c), per-arity + per-split breakdowns, coverage
  preflight, per-concept role-slot profiles + held-out-concept split (FEED B).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic (fixed seed,
  numpy default_rng, sorted iteration, sha256 not python hash()); repo .venv. VET-PENDING; NO atom banking.

CELL-TEMPLATE MANDATORY: except SystemExit raised BEFORE except Exception (no bare/BaseException); atomic
  metrics (tmp+os.replace); start-marker; crash-diagnostic; heartbeat; progress prints. self-test builds a
  planted def-structure discriminator (GloVe-free fake encoder) proving the def match CAN-FIRE (right predicate
  -> gold) + CAN-FAIL (scrambled predicate -> not gold), the REAL HDFactStore round-trip, and the REAL pool/arm
  imports. All numbers MEASURED@ this run. The 5 reused arms are IMPORTED (not re-implemented) -> identical.
"""
from __future__ import annotations

import os
import sys
import json
import time
import math
import hashlib
import argparse
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner
from hdlab.hd_fact_store import HDFactStore
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_reasoner_link_precision_tie_prune_v1 as tp
# reused arms + tie pool + significance test (leak-free, VET-cleared).
from experiments import exp_intrinsic_foundation_loop_tie_gaps_v1 as v1
from experiments import exp_intrinsic_foundation_loop_tie_gaps_powered_v1 as powered

ANCHOR_NAME = "intrinsic_foundation_loop_tie_gaps_defmatch_v1"
SEED = 20260725                     # SAME seed as powered -> byte-identical pool -> reused arms reproduce EXACT
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")

BASE_MODE = "lemma_syn"
GAP_MODES = ["lemma", "glove"]
PREFER_MODE = "lemma"
TIEBREAK_MODE = "legacy"
K_FACTS = v1.K_FACTS                # 8
STORE_DIM = v1.STORE_DIM            # 4096
HELDOUT_PCT = 30                    # % of tie GOLD concepts held out (deterministic sha256) for the FEED-B yardstick

# ---- POSITIVE-CONTROL targets (MEASURED@ data/exp_intrinsic_foundation_loop_tie_gaps_powered_v1/metrics.json) ----
PC_N_POOL = 128
PC_ARM0_CORRECT = 48               # 0.3750
PC_FLOOR_CORRECT = 51              # 0.3984
PC_ARM1_CORRECT = 68               # 0.5312
PC_ARM2_CORRECT = 60               # 0.4688
PC_ARM3G_CORRECT = 47              # 0.3672

# ---- pre-registered bands (fixed BEFORE the run; reported STRAIGHT, NOT tuned) ----
HP_MCNEMAR_P = 0.05
GOLD_ONLY_FLOOR = 1.0
NEG_INF = -2.0                     # score sentinel for an empty profile (below any cosine/overlap in [-1,1])

_T0 = [time.perf_counter()]


# ===========================================================================
# atomic metrics / start-marker / crash-diag / heartbeat  (same pattern as powered/v1)
# ===========================================================================
def _write_metrics_atomic(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir: str, stage: str, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ===========================================================================
# DEFINITIONAL-STRUCTURE MATCH: role-slot profile via the trust-gate + best-role-filler score
# ===========================================================================
def build_def_profile(fact_dicts: List[dict], seed: int) -> List[Tuple[str, str]]:
    """Ingest a choice's WorldTree facts through the hd_fact_store TRUST-GATE (WorldTree=TRUST_HIGH), then
    recover each live fact GLASS-BOX (unbind, no plaintext read) -> list of (relation, object). The object is
    the definitional PREDICATE (the role-filler). Concept label (subject) is NOT part of the returned score
    material -- only role + filler. Empty input -> empty profile."""
    if not fact_dicts:
        return []
    store = HDFactStore(n_dim=STORE_DIM, seed=seed)
    for f in fact_dicts:
        if f["arg0"].strip() and f["arg1"].strip():
            store.store(f["arg0"], f["relation"], f["arg1"], "worldtree", "TRUST_HIGH")
    prof: List[Tuple[str, str]] = []
    for rec in store.live_facts():
        rf = store.recover_fact(rec.vec)
        rel, obj = rf["relation"], rf["object"]
        if rel and obj:
            prof.append((str(rel), str(obj)))
    return prof


def _content_set(text: str) -> set:
    return set(arc._content_words(text, min_len=v1.MIN_LEN))


def grounded_align(encode: Callable[[str], np.ndarray], obj: str, stem_vec: np.ndarray) -> float:
    """Grounded filler alignment: cosine(L2(encode(definitional predicate)), stem_vec). Same encoder as the
    GloVe arms -> isolates STRUCTURE (per-role predicate, label dropped), not the encoder, as the one variable."""
    v = v1._l2(np.asarray(encode(obj), dtype=np.float32))
    return float(v @ stem_vec)


def symbolic_align(obj: str, stem_content: set, df: Dict[str, int]) -> float:
    """GloVe-FREE propositional filler alignment: rarity-weighted content-word overlap of the definitional
    predicate with the stem. rarity(w)=1/log(2+df(w)) down-weights generic tokens (water/energy) that appear
    in many facts, so a discriminating rare predicate word dominates. Assignment-lookup, no borrowed vector."""
    shared = _content_set(obj) & stem_content
    if not shared:
        return 0.0
    return float(sum(1.0 / math.log(2.0 + df.get(w, 0)) for w in shared))


def decide_by_def_structure(valid: List[dict], profile_per_choice: Dict[int, List[Tuple[str, str]]],
                            score_obj: Callable[[str], float]) -> int:
    """Pick the valid choice whose BEST definitional predicate (role-filler) most aligns with the stem.
    Predicates are scored SEPARATELY (no blend) -> keeps role structure; concept label excluded.
    GUARDRAIL: exactly one valid choice (gold_only) returned UNCHANGED -> gold_only@1.00 preserved.
    Empty profile -> sentinel NEG_INF; all-empty -> deterministic lowest index (coverage-limited degenerate)."""
    if len(valid) == 1:
        return valid[0]["choice_index"]
    scored = []
    for c in valid:
        ci = c["choice_index"]
        prof = profile_per_choice.get(ci, [])
        s = max((score_obj(obj) for (_rel, obj) in prof), default=NEG_INF)
        scored.append((-s, ci))          # higher score first; lower index breaks exact ties (deterministic)
    scored.sort()
    return scored[0][1]


def _heldout_side(concept: str) -> str:
    """Deterministic sha256 partition of a GOLD concept into train / heldout (NOT python hash())."""
    h = int.from_bytes(hashlib.sha256(concept.strip().lower().encode("utf-8")).digest()[:8], "big")
    return "heldout" if (h % 100) < HELDOUT_PCT else "train"


# ===========================================================================
# LADDER over the powered pool -- reused arms IMPORTED (identical), def arms added
# ===========================================================================
def evaluate_pool(reasoner: DerivationReasoner, pool: List[dict], output_dir: str,
                  index: Dict[str, List[int]], facts: List[dict], wn,
                  encode: Callable[[str], np.ndarray], df: Dict[str, int], seed: int) -> dict:
    """PASS1 build per-unit context (valid choices, stem vec+content, oracle/auto fact TEXTS for the reused
    GloVe arms AND fact DICTS for the def arms, def profiles); PASS2 decide every arm. The reused arms replicate
    powered's exact rng draw order so ARM0/FLOOR/ARM1/ARM2/ARM3global reproduce EXACT (positive control)."""
    contexts: List[dict] = []
    consolidation_totals = {"n_ingested": 0, "n_live_recovered": 0, "n_conflict": 0}
    n_units = len(pool)
    for ui, unit in enumerate(pool):
        q = unit["question"]
        ci = unit["correct_index"]
        reasoner.link_mode = unit["mode"]
        reasoner.tiebreak_mode = TIEBREAK_MODE
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        valid = [{"choice_index": c["choice_index"], "choice_text": c["choice_text"]}
                 for c in v1._valid_choices(res["per_choice"])]
        stem_vec = v1._l2(np.asarray(encode(q["stem"]), dtype=np.float32))
        stem_content = _content_set(q["stem"])

        # ORACLE retrieval (== ARM1 reach: content+lemma+WN synonyms): TEXTS (reused arm) + DICTS (def arm).
        oracle_texts: Dict[int, List[str]] = {}
        oracle_dicts: Dict[int, List[dict]] = {}
        for c in valid:
            fids = v1.retrieve_fact_ids(index, c["choice_text"], wn, use_syn=True)
            sel = v1._select_facts(facts, fids, K_FACTS)
            oracle_texts[c["choice_index"]] = [f["text"] for f in sel]
            oracle_dicts[c["choice_index"]] = sel
        # AUTONOMOUS retrieval (== ARM2 reach: content+lemma, NO synonym oracle): DICTS for the def-auto arm.
        auto_dicts: Dict[int, List[dict]] = {}
        for c in valid:
            fids = v1.retrieve_fact_ids(index, c["choice_text"], wn, use_syn=False)
            auto_dicts[c["choice_index"]] = v1._select_facts(facts, fids, K_FACTS)
        # ARM2 (reused GloVe autonomous) uses v1.autonomous_facts (store round-trip texts) UNCHANGED.
        auto_texts, clog = v1.autonomous_facts(valid, index, facts, wn, seed + ui)
        for k in consolidation_totals:
            consolidation_totals[k] += clog[k]

        # def-structure profiles (role-slot via the trust-gate) for oracle + auto fact sets.
        def_oracle_prof = {c["choice_index"]: build_def_profile(oracle_dicts[c["choice_index"]], seed + ui)
                           for c in valid}
        def_auto_prof = {c["choice_index"]: build_def_profile(auto_dicts[c["choice_index"]], seed + ui + 7919)
                         for c in valid}

        contexts.append({
            "split": unit["split"], "qid": unit["qid"], "mode": unit["mode"], "ci": ci,
            "valid": valid, "stem_vec": stem_vec, "stem_content": stem_content,
            "oracle_texts": oracle_texts, "oracle_dicts": oracle_dicts, "auto_texts": auto_texts,
            "def_oracle_prof": def_oracle_prof, "def_auto_prof": def_auto_prof,
            "gold_text": next((c["choice_text"] for c in valid if c["choice_index"] == ci), ""),
            "arm0_chosen": unit["arm0_chosen"], "arm0_correct": unit["arm0_correct"],
        })
        if (ui + 1) % 20 == 0:
            _heartbeat(output_dir, "ladder_pass1", {"done": ui + 1, "total": n_units})

    # global pools for the GLOBAL scramble arms: reused arm uses TEXTS, def arm uses DICTS (both tagged by qid).
    global_pool_texts = [(c["qid"], fts) for c in contexts for fts in c["oracle_texts"].values() if fts]
    global_pool_dicts = [(c["qid"], fd) for c in contexts for fd in c["oracle_dicts"].values() if fd]

    # ---- PASS 2 ----
    per_tie: List[dict] = []
    grng = np.random.default_rng(seed * 101 + 5)         # reused-arm rng (replicate powered EXACT draw order)
    dgrng = np.random.default_rng(seed * 211 + 7)        # SEPARATE rng for the def-scramble (never perturbs grng)
    for ctx in contexts:
        qid, ci, valid = ctx["qid"], ctx["ci"], ctx["valid"]
        stem_vec, stem_content = ctx["stem_vec"], ctx["stem_content"]
        oracle_texts, auto_texts = ctx["oracle_texts"], ctx["auto_texts"]
        no_facts = {c["choice_index"]: [] for c in valid}

        # --- reused GloVe arms (IMPORTED v1.decide_by_meaning; identical to powered) ---
        floor_pick = v1.decide_by_meaning(valid, no_facts, encode, stem_vec)
        arm1_pick = v1.decide_by_meaning(valid, oracle_texts, encode, stem_vec)
        arm2_pick = v1.decide_by_meaning(valid, auto_texts, encode, stem_vec)
        arm3w_pick = v1.decide_by_meaning(
            valid, v1.scramble_facts(valid, oracle_texts, seed + len(per_tie)), encode, stem_vec)
        other_t = [fts for (sq, fts) in global_pool_texts if sq != qid]
        gscr_t = {c["choice_index"]: (list(other_t[int(grng.integers(len(other_t)))]) if other_t else [])
                  for c in valid}
        arm3g_pick = v1.decide_by_meaning(valid, gscr_t, encode, stem_vec)

        # --- NEW def-structure arms (the ONE change: role-structured predicate match) ---
        g_score = (lambda obj: grounded_align(encode, obj, stem_vec))
        s_score = (lambda obj: symbolic_align(obj, stem_content, df))
        def_pick = decide_by_def_structure(valid, ctx["def_oracle_prof"], g_score)
        def_auto_pick = decide_by_def_structure(valid, ctx["def_auto_prof"], g_score)
        def_sym_pick = decide_by_def_structure(valid, ctx["def_oracle_prof"], s_score)
        # def global scramble: each choice gets ANOTHER question's oracle fact DICTS -> profile -> def match.
        other_d = [fd for (sq, fd) in global_pool_dicts if sq != qid]
        def_scr_prof = {}
        for c in valid:
            if other_d:
                fd = other_d[int(dgrng.integers(len(other_d)))]
                def_scr_prof[c["choice_index"]] = build_def_profile(fd, seed + len(per_tie) + 104729)
            else:
                def_scr_prof[c["choice_index"]] = []
        def_scr_pick = decide_by_def_structure(valid, def_scr_prof, g_score)

        n_oracle_prof = sum(len(p) for p in ctx["def_oracle_prof"].values())
        gold_has_prof = int(len(ctx["def_oracle_prof"].get(ci, [])) > 0)
        per_tie.append({
            "split": ctx["split"], "qid": qid, "mode": ctx["mode"], "correct_index": ci,
            "n_valid": len(valid), "valid_indices": [c["choice_index"] for c in valid],
            "gold_text": ctx["gold_text"], "heldout_side": _heldout_side(ctx["gold_text"]),
            "arm0_pick": ctx["arm0_chosen"], "arm0_correct": int(ctx["arm0_correct"]),
            "floor_pick": floor_pick, "arm1_pick": arm1_pick, "arm2_pick": arm2_pick,
            "arm3_within_pick": arm3w_pick, "arm3_global_pick": arm3g_pick,
            "def_pick": def_pick, "def_auto_pick": def_auto_pick,
            "def_sym_pick": def_sym_pick, "def_scr_pick": def_scr_pick,
            "floor_correct": int(floor_pick == ci), "arm1_correct": int(arm1_pick == ci),
            "arm2_correct": int(arm2_pick == ci), "arm3_within_correct": int(arm3w_pick == ci),
            "arm3_global_correct": int(arm3g_pick == ci),
            "def_correct": int(def_pick == ci), "def_auto_correct": int(def_auto_pick == ci),
            "def_sym_correct": int(def_sym_pick == ci), "def_scr_correct": int(def_scr_pick == ci),
            "n_oracle_facts": sum(len(v) for v in oracle_texts.values()),
            "n_oracle_prof": n_oracle_prof, "gold_has_prof": gold_has_prof,
        })

    return {"per_tie": per_tie, "consolidation_totals": consolidation_totals, "n_units": n_units,
            "contexts_for_profiles": contexts}


_ARM_KEYS = ("arm0_correct", "floor_correct", "arm1_correct", "arm2_correct", "arm3_within_correct",
             "arm3_global_correct", "def_correct", "def_auto_correct", "def_sym_correct", "def_scr_correct")


def _acc(rows: List[dict], key: str) -> float:
    return round(sum(r[key] for r in rows) / len(rows), 4) if rows else 0.0


def _breakdown(rows: List[dict]) -> dict:
    return {"n": len(rows), **{k.replace("_correct", ""): _acc(rows, k) for k in _ARM_KEYS}}


# ===========================================================================
# gold_only preservation (reuse powered's check verbatim -- decision semantics unchanged for single-valid)
# ===========================================================================
def check_gold_only_preserved(reasoner, cfg_cache, splits, index, facts, wn, encode,
                              n_sample: int, seed: int, df: Dict[str, int], cap: int = 40) -> Tuple[float, int]:
    """Single-valid gold_only decisions must be UNCHANGED under the def-structure match too (guardrail)."""
    preserved = 1.0
    checked = 0
    for split_name, split_path in splits:
        all_q = arc._load_questions(split_path, limit=0)
        if n_sample and n_sample < len(all_q):
            rng = np.random.default_rng(seed)
            idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
            qs = [all_q[i] for i in idx]
        else:
            qs = all_q
        qmap = {q["qid"]: q for q in qs}
        base_pq = cfg_cache[split_name]["base"]["per_q"]
        go_qids = sorted(qid for qid, r in base_pq.items() if r["subset"] == "gold_only")[:cap]
        reasoner.link_mode = BASE_MODE
        reasoner.tiebreak_mode = TIEBREAK_MODE
        for qid in go_qids:
            q = qmap[qid]
            res = reasoner._reason_arm(q, reasoner.arms["typed"])
            valid = v1._valid_choices(res["per_choice"])
            if len(valid) != 1:
                continue
            stem_vec = v1._l2(np.asarray(encode(q["stem"]), dtype=np.float32))
            c0 = {"choice_index": valid[0]["choice_index"], "choice_text": valid[0]["choice_text"]}
            fids = v1.retrieve_fact_ids(index, c0["choice_text"], wn, use_syn=True)
            prof = {c0["choice_index"]: build_def_profile(v1._select_facts(facts, fids, K_FACTS), seed)}
            pick = decide_by_def_structure([c0], prof, lambda o: grounded_align(encode, o, stem_vec))
            checked += 1
            if pick != c0["choice_index"]:
                preserved = 0.0
    return preserved, checked


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full" if n_sample == 0 else "smoke", PC_N_POOL)
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})

    rows = tp._load_rules(RULES_PATH)
    _heartbeat(output_dir, "rules_loaded", {"n_rules": len(rows)})

    index, facts = v1.build_acq_index()
    # document frequency per content-word for the GloVe-free symbolic-overlap rarity weight.
    df = {w: len(fids) for w, fids in index.items()}
    _heartbeat(output_dir, "acq_index_built", {"n_facts": len(facts), "n_concept_keys": len(index)})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon
    base = SemanticHDEncoder()
    pol = PolarityLexicon()
    wn = base._wn
    encode = base.encode
    _heartbeat(output_dir, "encoder_ready")

    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, seed=seed, rows=rows,
                                  link_mode=BASE_MODE, tiebreak_mode=TIEBREAK_MODE)
    _heartbeat(output_dir, "graph_built",
               {"n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"]})

    splits = [("easy", arc._EASY_TEST), ("challenge", arc._CHAL_TEST)]
    # REUSE the powered pool builder verbatim -> byte-identical n=128 pool.
    pool, pool_meta = powered.build_pool(reasoner, output_dir, splits, n_sample, seed)
    _heartbeat(output_dir, "pool_ready", {"n_pool": len(pool), "detect": pool_meta["detect"]})

    rep = evaluate_pool(reasoner, pool, output_dir, index, facts, wn, encode, df, seed)
    per_tie = rep["per_tie"]
    _heartbeat(output_dir, "ladder_done", {"n_units": rep["n_units"]})

    go_preserved, go_checked = check_gold_only_preserved(
        reasoner, pool_meta["cfg_cache"], splits, index, facts, wn, encode, n_sample, seed, df)
    reasoner.link_mode = BASE_MODE

    # ---- arm accuracies ----
    arms = {
        "arm0_legacy_combiner": _acc(per_tie, "arm0_correct"),
        "floor_mm_no_facts": _acc(per_tie, "floor_correct"),
        "arm1_oracle_ceiling": _acc(per_tie, "arm1_correct"),
        "arm2_autonomous_loop": _acc(per_tie, "arm2_correct"),
        "arm3_scramble_within": _acc(per_tie, "arm3_within_correct"),
        "arm3_scramble_global": _acc(per_tie, "arm3_global_correct"),
        "def_oracle_grounded": _acc(per_tie, "def_correct"),
        "def_auto_grounded": _acc(per_tie, "def_auto_correct"),
        "def_oracle_symbolic": _acc(per_tie, "def_sym_correct"),
        "def_scramble_global": _acc(per_tie, "def_scr_correct"),
    }
    col = lambda k: [r[k] for r in per_tie]
    mc = {
        "def_vs_arm1": powered.mcnemar(col("def_correct"), col("arm1_correct"), "def", "arm1"),
        "defauto_vs_arm2": powered.mcnemar(col("def_auto_correct"), col("arm2_correct"), "defauto", "arm2"),
        "defauto_vs_defscr": powered.mcnemar(col("def_auto_correct"), col("def_scr_correct"),
                                             "defauto", "defscr"),
        "defauto_vs_arm3global": powered.mcnemar(col("def_auto_correct"), col("arm3_global_correct"),
                                                 "defauto", "arm3global"),
        "def_vs_defscr": powered.mcnemar(col("def_correct"), col("def_scr_correct"), "def", "defscr"),
        "defsym_vs_arm1": powered.mcnemar(col("def_sym_correct"), col("arm1_correct"), "defsym", "arm1"),
        "def_vs_floor": powered.mcnemar(col("def_correct"), col("floor_correct"), "def", "floor"),
    }

    by_arity = {f"{k}_way": _breakdown([r for r in per_tie if r["n_valid"] == k]) for k in (2, 3, 4)}
    by_arity["ge5_way"] = _breakdown([r for r in per_tie if r["n_valid"] >= 5])
    by_split = {sn: _breakdown([r for r in per_tie if r["split"] == sn]) for sn, _ in splits}
    by_mode = {m: _breakdown([r for r in per_tie if r["mode"] == m]) for m in GAP_MODES}
    by_heldout = {side: _breakdown([r for r in per_tie if r["heldout_side"] == side])
                  for side in ("train", "heldout")}

    # ---- POSITIVE CONTROL: reused arms reproduce powered EXACT (integer counts) ----
    smoke_run = (n_sample != 0)
    reused_counts = {"n_pool": len(per_tie),
                     "arm0": sum(col("arm0_correct")), "floor": sum(col("floor_correct")),
                     "arm1": sum(col("arm1_correct")), "arm2": sum(col("arm2_correct")),
                     "arm3global": sum(col("arm3_global_correct"))}
    pc_ok = (reused_counts["n_pool"] == PC_N_POOL and reused_counts["arm0"] == PC_ARM0_CORRECT
             and reused_counts["floor"] == PC_FLOOR_CORRECT and reused_counts["arm1"] == PC_ARM1_CORRECT
             and reused_counts["arm2"] == PC_ARM2_CORRECT and reused_counts["arm3global"] == PC_ARM3G_CORRECT)
    positive_control = {
        "reused_counts_measured": reused_counts,
        "expected": {"n_pool": PC_N_POOL, "arm0": PC_ARM0_CORRECT, "floor": PC_FLOOR_CORRECT,
                     "arm1": PC_ARM1_CORRECT, "arm2": PC_ARM2_CORRECT, "arm3global": PC_ARM3G_CORRECT},
        "reproduces_powered_29573": bool(pc_ok),
        "note": ("full-set only; smoke subsamples so the pool is NOT the canonical 128"
                 if smoke_run else "full ARC test sets; reused arms must reproduce powered EXACT"),
    }

    # ---- def-profile coverage preflight (gold concepts + all tie choices) ----
    gold_concepts = sorted({r["gold_text"] for r in per_tie if r["gold_text"]})
    n_gold_with_prof = sum(1 for r in per_tie if r["gold_has_prof"])
    cov_gold = round(n_gold_with_prof / len(per_tie), 4) if per_tie else 0.0
    # per-choice coverage across the pool
    total_choices = sum(r["n_valid"] for r in per_tie)
    coverage = {
        "gold_units_with_profile": n_gold_with_prof, "n_units": len(per_tie),
        "gold_profile_coverage": cov_gold,
        "n_unique_gold_concepts": len(gold_concepts),
        "mean_oracle_profile_facts_per_unit": round(sum(col("n_oracle_prof")) / len(per_tie), 3) if per_tie else 0.0,
        "thin_flag": bool(cov_gold < 0.5),
    }

    # ---- FEED B: per-concept role-slot definitional profiles + held-out split ----
    concept_profiles: Dict[str, Dict[str, List[str]]] = {}
    concept_side: Dict[str, str] = {}
    for ctx in rep["contexts_for_profiles"]:
        for c in ctx["valid"]:
            txt = c["choice_text"]
            if not txt:
                continue
            prof = ctx["def_oracle_prof"].get(c["choice_index"], [])
            if not prof:
                continue
            slot = concept_profiles.setdefault(txt, defaultdict(set))
            for (rel, obj) in prof:
                slot[rel].add(obj)
    # freeze to plain dict of sorted lists; tag held-out side
    feed_b_profiles = {}
    for txt, slot in sorted(concept_profiles.items()):
        feed_b_profiles[txt] = {rel: sorted(objs) for rel, objs in sorted(slot.items())}
        concept_side[txt] = _heldout_side(txt)

    # ---- deltas ----
    d = {
        "def_minus_arm1": round(arms["def_oracle_grounded"] - arms["arm1_oracle_ceiling"], 4),
        "defauto_minus_arm2": round(arms["def_auto_grounded"] - arms["arm2_autonomous_loop"], 4),
        "defauto_minus_defscr": round(arms["def_auto_grounded"] - arms["def_scramble_global"], 4),
        "defauto_minus_arm3global": round(arms["def_auto_grounded"] - arms["arm3_scramble_global"], 4),
        "def_minus_defscr": round(arms["def_oracle_grounded"] - arms["def_scramble_global"], 4),
        "defsym_minus_arm1": round(arms["def_oracle_symbolic"] - arms["arm1_oracle_ceiling"], 4),
        "def_minus_floor": round(arms["def_oracle_grounded"] - arms["floor_mm_no_facts"], 4),
    }

    # ---- pre-registered bands ----
    lift_ceiling = (mc["def_vs_arm1"]["p_exact"] < HP_MCNEMAR_P
                    and arms["def_oracle_grounded"] > arms["arm1_oracle_ceiling"])
    move_autonomous = (mc["defauto_vs_defscr"]["p_exact"] < HP_MCNEMAR_P
                       and arms["def_auto_grounded"] > arms["def_scramble_global"])
    guardrails_ok = (go_preserved >= GOLD_ONLY_FLOOR) and (pc_ok or smoke_run)
    bands = {
        "def_lifts_ceiling_vs_arm1_p_lt_0.05": bool(lift_ceiling),
        "defauto_clears_scramble_p_lt_0.05": bool(move_autonomous),
        "gold_only_preserved": go_preserved >= GOLD_ONLY_FLOOR,
        "positive_control_reproduces_powered": bool(pc_ok or smoke_run),
    }

    if not pc_ok and not smoke_run:
        tier, verdict = "POSITIVE_CONTROL_FAIL", "REPRODUCE_POWERED_29573_MISMATCH"
    elif (lift_ceiling or move_autonomous) and guardrails_ok:
        tier, verdict = "HARD_PASS", "DEFINITIONAL_STRUCTURE_MATCH_LIFTS_TIE_RESOLUTION_GREENLIGHT_B"
    elif (not lift_ceiling) and (not move_autonomous):
        tier, verdict = "HONEST_NEG", "DEFINITIONAL_STRUCTURE_ALONE_INSUFFICIENT_ROUTE_TO_DIFFERENT_GROUNDING"
    else:
        tier, verdict = "MIDDLE_BAND", "PARTIAL_OR_GUARDRAIL_OR_WRONG_DIRECTION"

    summary = (
        f"DEF-MATCH swap on n={len(per_tie)} genuine ties (Easy+Challenge; reused pool) | "
        f"ARM1(GloVe-oracle)={arms['arm1_oracle_ceiling']:.3f} ARM2(GloVe-auto)={arms['arm2_autonomous_loop']:.3f} "
        f"ARM3global={arms['arm3_scramble_global']:.3f} FLOOR={arms['floor_mm_no_facts']:.3f} || "
        f"ARM_DEF(oracle)={arms['def_oracle_grounded']:.3f} ARM_DEF_AUTO={arms['def_auto_grounded']:.3f} "
        f"ARM_DEF_SYM={arms['def_oracle_symbolic']:.3f} ARM_DEF_SCR={arms['def_scramble_global']:.3f} | "
        f"d(DEF-ARM1)={d['def_minus_arm1']:+.3f} p={mc['def_vs_arm1']['p_exact']:.4f} "
        f"(b={mc['def_vs_arm1']['def_wins']},c={mc['def_vs_arm1']['arm1_wins']}) | "
        f"d(DEFAUTO-DEFSCR)={d['defauto_minus_defscr']:+.3f} p={mc['defauto_vs_defscr']['p_exact']:.4f} | "
        f"cov_gold={cov_gold:.2f}{' THIN' if coverage['thin_flag'] else ''} | "
        f"gold_only={go_preserved:.2f} repro_powered={pc_ok} | tier={tier}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "BOOTSTRAP that de-risks the earn-it build B: swap ONLY the decision meaning-match at the reasoner's "
            "tie seam from thin-GloVe cosine (choice_label + concatenated fact-texts vs stem) to DEFINITIONAL "
            "STRUCTURE -- keep role/relation structure, DROP the near-synonym concept label, score each "
            "definitional PREDICATE (role-filler = fact object recovered GLASS-BOX from an hd_fact_store "
            "TRUST-GATE ingest, WorldTree=TRUST_HIGH) SEPARATELY vs the stem, best role-filler wins. Everything "
            "else IMPORTED UNCHANGED: leak-free arms + n=128 tie pool + controls from powered_v1 (build_pool, "
            "mcnemar) + v1 (retrieval, autonomous loop, scramble). ARMS: reused ARM0/FLOOR/ARM1(GloVe oracle "
            "ceiling 0.531)/ARM2(GloVe auto 0.469)/ARM3global(0.367) reproduce powered EXACT (positive control); "
            "NEW ARM_DEF (def match, ORACLE facts; one var vs ARM1 = match), ARM_DEF_AUTO (AUTONOMOUS facts; one "
            "var vs ARM2), ARM_DEF_SCR (globally-scrambled oracle facts; MUST-FAIL for the new match), ARM_DEF_SYM "
            "(GloVe-FREE rarity-weighted predicate-vs-stem content overlap; purely propositional assignment-"
            "lookup, diagnostic for B). PRE-REG can-fail: HARD_PASS = (ARM_DEF vs ARM1 McNemar p<0.05 AND "
            "arm_def>arm1) OR (ARM_DEF_AUTO vs ARM_DEF_SCR McNemar p<0.05 AND arm_def_auto>arm_def_scr) => target "
            "REAL, greenlight B; HONEST_NEG = no lift over GloVe => definitional structure ALONE insufficient "
            "(decisive: saves B, routes to a different grounding). gold_only preserved @1.00 by construction; "
            "coverage preflight reported (a win over few concepts is an artifact). FEED B: per-concept role-slot "
            "profiles + held-out-to-new-concepts split emitted. Anti-leak: acquisition answer-agnostic; def match "
            "uses stem+profile never the answer; correct_index only in tally + decision-independent held-out "
            "split. HELD-OUT ARC; rules not from test labels. NOTE: grounded def arms still use the GloVe encoder "
            "to GROUND the predicate text (structure is the one variable, not the encoder); ARM_DEF_SYM is the "
            "GloVe-free companion. VET-PENDING; no atom banking."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_sample_per_split": n_sample, "seed": seed, "rules_path": RULES_PATH,
                   "n_rules": len(rows), "base_mode": BASE_MODE, "gap_modes": GAP_MODES,
                   "prefer_mode": PREFER_MODE, "tiebreak_mode": TIEBREAK_MODE, "k_facts": K_FACTS,
                   "store_dim": STORE_DIM, "heldout_pct": HELDOUT_PCT,
                   "pool_source": "exp_intrinsic_foundation_loop_tie_gaps_powered_v1.build_pool (IMPORTED)",
                   "reused_arms_source": "exp_intrinsic_foundation_loop_tie_gaps_v1 (IMPORTED UNCHANGED)",
                   "the_one_change": "decision meaning-match: GloVe blend -> role-structured definitional predicate match",
                   "def_match": "role-slot profile via hd_fact_store trust-gate (glass-box recover), best predicate vs stem",
                   "grounded_align": "cosine(L2(encode(object)), stem_vec) -- same encoder, isolates STRUCTURE",
                   "symbolic_align": "rarity-weighted content-word overlap(object, stem) -- GloVe-free (for B)",
                   "progress_logging": "heartbeat jsonl + stdout flush per stage/20-unit"},
        "n_pool": len(per_tie), "pool_detection": pool_meta["detect"],
        "positive_control": positive_control,
        "arms": arms, "deltas": d, "mcnemar": mc,
        "breakdown_by_arity": by_arity, "breakdown_by_split": by_split, "breakdown_by_mode": by_mode,
        "breakdown_by_heldout_concept": by_heldout,
        "coverage": coverage,
        "acquisition": {"source": "WorldTree tablestore (parse_tablestore_typed, ALL relations)",
                        "n_facts": len(facts), "n_concept_keys": len(index),
                        "trust_gate": "hd_fact_store.HDFactStore (WorldTree=TRUST_HIGH)",
                        "totals": rep["consolidation_totals"]},
        "gold_only_preserved": round(go_preserved, 4), "gold_only_checked": go_checked,
        "preregistered_bands": bands, "n_bands_pass": sum(1 for vv in bands.values() if vv),
        "bands_definition": {
            "hard_pass": ("(def_vs_arm1 McNemar p<0.05 AND def>arm1) OR (defauto_vs_defscr p<0.05 AND "
                          "defauto>defscr) -- with gold_only preserved + positive-control reproduces powered"),
            "honest_neg": ("neither lift significant -> definitional structure alone insufficient, route to a "
                           "different grounding (earn-it meaning); saves the B investment"),
        },
        "feed_b": {
            "concept_role_slot_profiles": feed_b_profiles,
            "concept_heldout_side": concept_side,
            "n_concepts_with_profile": len(feed_b_profiles),
            "heldout_pct": HELDOUT_PCT,
            "note": ("per-concept definitional role-slot profile {relation:[objects]} + deterministic sha256 "
                     "held-out-to-new-concepts split; B learns to predict grounded features for held-out concepts "
                     "and is graded on this yardstick"),
        },
        "per_tie": per_tie,
        "REQUIRED_FIELDS": ["verdict", "tier", "n_pool", "positive_control", "arms", "deltas", "mcnemar",
                            "preregistered_bands", "gold_only_preserved", "coverage", "breakdown_by_split",
                            "breakdown_by_heldout_concept", "feed_b"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== DEFINITIONAL-STRUCTURE MATCH SWAP (tie-gaps) RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"bands: {bands} -> {metrics['n_bands_pass']}/4 | tier={tier}", flush=True)
    print(f"McNemar def_vs_arm1: {mc['def_vs_arm1']}", flush=True)
    print(f"McNemar defauto_vs_defscr: {mc['defauto_vs_defscr']}", flush=True)
    print(f"coverage: {coverage}", flush=True)
    print(f"positive_control: {positive_control['reproduces_powered_29573']} {reused_counts}", flush=True)
    print(f"by_split: {by_split}", flush=True)
    print(f"by_heldout_concept: {by_heldout}", flush=True)
    return metrics


# ===========================================================================
# self-test (real code path: planted def-structure discriminator + REAL HDFactStore + REAL imports)
# ===========================================================================
def _self_test() -> None:
    print("[self-test] definitional-structure match (GloVe-free) ...", flush=True)
    exercised = set()

    # ---- (1) def-structure match FIRES: right definitional PREDICATE -> gold; scrambled predicate -> not gold.
    # planted 2-choice tie: near-synonym labels (the collapse case GloVe suffers). The DISCRIMINATING signal
    # lives ONLY in the definitional predicate (object), which the def match scores per-role (label dropped).
    stem = "which substance is the dissolved material spread evenly throughout a solution"
    vocab_words = _content_set(stem)
    # gold=solute predicate contains 'dissolved'; distractor=solvent predicate contains 'dissolving medium'.
    gold_obj = "the dissolved substance in a solution"
    dist_obj = "the dissolving liquid medium in a solution"
    for t in (gold_obj, dist_obj, "solute", "solvent"):
        vocab_words |= _content_set(t)
    vocab = {w: i for i, w in enumerate(sorted(vocab_words))}

    def enc(text: str) -> np.ndarray:
        v = np.zeros(len(vocab), dtype=np.float32)
        for w in arc._content_words(text, min_len=v1.MIN_LEN):
            if w in vocab:
                v[vocab[w]] += 1.0
        return v

    stem_vec = v1._l2(np.asarray(enc(stem), dtype=np.float32))
    valid = [{"choice_index": 0, "choice_text": "solute"},     # gold (near-synonym label of the distractor)
             {"choice_index": 1, "choice_text": "solvent"}]    # distractor
    prof_right = {0: [("KINDOF", gold_obj)], 1: [("KINDOF", dist_obj)]}
    g = lambda o: grounded_align(enc, o, stem_vec)
    pick = decide_by_def_structure(valid, prof_right, g)
    assert pick == 0, f"right definitional predicate must pick gold(0), got {pick}"
    exercised.add("decide_by_def_structure")
    # scramble the predicates across choices -> the discriminator MUST NOT still pick gold (can-fail proof).
    prof_scr = {0: [("KINDOF", dist_obj)], 1: [("KINDOF", gold_obj)]}
    scr_pick = decide_by_def_structure(valid, prof_scr, g)
    assert scr_pick != 0, f"scrambled predicate must NOT pick gold (non-discriminating), got {scr_pick}"
    # empty profile -> sentinel, deterministic lowest index when all empty
    assert decide_by_def_structure(valid, {0: [], 1: []}, g) == 0, "all-empty must fall to lowest index"
    print(f"[self-test] def match fires: right->{pick} scrambled->{scr_pick}", flush=True)

    # ---- (2) GloVe-free symbolic overlap also discriminates on the planted case ----
    df = {"dissolved": 3, "dissolving": 3, "medium": 5, "solution": 40, "substance": 20}
    sc = _content_set(stem)
    s = lambda o: symbolic_align(o, sc, df)
    assert decide_by_def_structure(valid, prof_right, s) == 0, "symbolic overlap must pick gold on planted case"
    exercised.add("symbolic_align")

    # ---- (3) gold_only guardrail: a SINGLE valid choice returned UNCHANGED ----
    solo = [{"choice_index": 2, "choice_text": "the only derivable answer"}]
    assert decide_by_def_structure(solo, {2: [("KINDOF", "irrelevant")]}, g) == 2, \
        "single valid choice must be returned unchanged (gold_only preserved)"
    exercised.add("gold_only_preserved")

    # ---- (4) REAL HDFactStore ingest -> glass-box role-slot profile round-trip (the trust-gate path) ----
    prof = build_def_profile(
        [{"uid": "u1", "relation": "KINDOF", "arg0": "solute", "arg1": "dissolved substance in a solution",
          "text": "solute dissolved substance in a solution"}], seed=7)
    assert len(prof) == 1 and prof[0][0] == "KINDOF" and "dissolved" in prof[0][1], prof
    exercised.add("build_def_profile")
    print(f"[self-test] trust-gate role-slot profile recover: {prof}", flush=True)

    # ---- (5) reused arms + pool builder are the imported objects; real acquisition index builds ----
    for fn in ("build_pool", "mcnemar"):
        assert hasattr(powered, fn), f"powered missing reused {fn}"
    for fn in ("decide_by_meaning", "retrieve_fact_ids", "_select_facts", "autonomous_facts",
               "scramble_facts", "build_acq_index", "_valid_choices"):
        assert hasattr(v1, fn), f"v1 missing reused {fn}"
    exercised.add("reused_imports")
    idx, facts = v1.build_acq_index()
    assert len(facts) > 1000, f"real acquisition index must load many facts, got {len(facts)}"
    fids = v1.retrieve_fact_ids(idx, "condensation", wn=None, use_syn=False)
    real_prof = build_def_profile(v1._select_facts(facts, fids, K_FACTS), seed=3)
    assert len(real_prof) >= 1, "must build a real role-slot profile for 'condensation'"
    exercised.add("real_code_path")
    assert os.path.exists(arc._EASY_TEST) and os.path.exists(arc._CHAL_TEST), "ARC Easy+Challenge must exist"
    print(f"[self-test] real profile(condensation)={real_prof[:2]} n_facts={len(facts)}", flush=True)

    need = {"decide_by_def_structure", "symbolic_align", "gold_only_preserved", "build_def_profile",
            "reused_imports", "real_code_path"}
    missing = need - exercised
    assert not missing, f"real_code_path: unexercised {missing}"
    print(f"[self-test] real_code_path exercised={sorted(exercised)}", flush=True)
    print("[self-test] ALL PASS", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=250, help="smoke sample size PER SPLIT (full ignores this)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = args.n if args.mode == "smoke" else 0
    output_dir = args.out if args.mode == "full" else args.out + "_smoke"
    try:
        run(output_dir, n_sample, args.seed)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
