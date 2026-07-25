"""
exp_arc_schema_routing_do_calculus_v1 -- MODEL-BASED / schema-routing branch for ARC reasoning (CPU, inline-local).

Implements Predictions 1-3 of notes/research_mental_simulation_grounding_causal_models_arc_2026-07-24.md
(bands re-confirmed in notes/research_science_causal_rule_supply_vs_mental_model_simulation_2026-07-25.md).

MECHANISM: comprehend each ARC question -> match it to a WorldTree causal SCHEMA
  (CAUSE / IFTHEN / COUPLEDRELATIONSHIP; a schema is a reusable slot-templated TEMPLATE binding
  different entities) -> route the matched schema + the question's stated intervention direction
  through the EXISTING do-calculus / do-operator primitive (exp_counterfactual_do_operator_v1: signed
  do()-override + topo-propagation + merkle audit chain) to predict the direction of the effect
  variable, then match against MC choices by direction-sign rather than lexical similarity.

ONE VARIABLE = schema-routing (Arm B) vs the similarity baseline (Arm A). Same encoder (CharTrigram),
  same WorldTree fact store, same MC harness, same held-out ARC Test splits for BOTH arms.

REUSE (wire, don't reinvent):
  - experiments.exp_counterfactual_do_operator_v1                 (do-calculus primitive: h() merkle + do()-topo-propagate)
  - experiments.exp_arc_selection_relational_meaning_v1           (rel.parse_tablestore_typed: uid->{relation,arg0,arg1})
  - experiments.exp_arc_aggregation_retriever_bindsettle_v1       (agg.parse_tablestore flat store + agg._TABLES)
  - experiments.exp_arc_knowledge_scale_ingest_climb_v1           (arc: _load_questions/_content_words/_unit_rows/_EASY_TEST/_CHAL_TEST)
  - hdlab.char_trigram_encoder.CharTrigramEncoder                 (self-contained lexical/similarity baseline; no GloVe download)

PRE-REGISTERED bands (from the mental-sim note, verbatim; NOT re-invented):
  P1 (schema-match coverage on ARC content): HARD-PASS if >=5% of ARC-Easy OR >=8% of ARC-Challenge
     items match a CAUSE/IFTHEN/COUPLEDRELATIONSHIP schema signature; HARD-FAIL if near-zero (<2%).
  P2 (central claim): on the MATCHED subset, Arm B (do-calculus routing) beats Arm A (similarity) by
     >=10pp absolute; HARD-FAIL if no lift or negative.
  P3 (honest control): on NON-matched (single-hop) items, Arm A >= Arm B (do-calculus not needed there);
     HARD-FAIL if Arm B beats Arm A even there (would signal a broad representation upgrade).
  MUST-FAIL control: routing matched items through a RANDOM/mismatched schema must NOT beat Arm A on
     the matched subset (proves it is the RIGHT schema, not any schema).

HONESTY: reports schema-MATCHED-subset accuracy AND whole-set accuracy for both arms; the ENTITY-selection
  axis is the known meaning wall -- if schema-routing helps on STRUCTURE but entity-binding still fails,
  the split is reported straight, not blended. do NOT tune to force a win.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; Arm A vs Arm B picks over matched subset)
  - final_metrics_atomicity = tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: qualitative accuracy has no Cramer-Rao noise floor (discrete MC choice)
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < Arm A matched-subset acc < 0.95)
  - discriminator = Arm B beats Arm A on matched subset by >=10pp (competition/selection; must FIRE = matched subset non-empty)
  - HARD_PASS strictly above floor (P2 >=10pp, P1 >=5%/>=8%)
  - cardinality: single-shot, no sweep axis (EXPECTED_N_UNITS = n_arms; declared)
  - per-unit failure-class: no bare except; specific classes
  - calibration_check: default_ok_for_this_regime (qualitative polarity lexicon fixed a priori)
  - all reported numbers MEASURED@ this cell's metrics.json
  - deterministic seeding: FIXED int seeds only; sorted() ordering; no hash()-seeded RNG, no list(set())
ASCII-only. write_metrics. INLINE-LOCAL foreground-to-completion.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, json, time, platform, traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

ANCHOR_NAME = "arc_schema_routing_do_calculus_v1"
SEED = 20260725
N_DIM = 2048
TARGET_RELATIONS = ("CAUSE", "IFTHEN", "COUPLEDRELATIONSHIP")

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()
if _ARGS.full:
    RUN_MODE = "full"

# Preload the do-operator primitive with a SANITIZED argv: its module top runs its own _selftest()
# and does `if _ARGS.self_test: sys.exit(0)`, which would abort THIS cell mid-import under --self-test.
# Import it once with the flags stripped so it caches cleanly in sys.modules; later imports are no-ops.
_saved_argv = sys.argv[:]
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:] if a not in ("--self-test", "--smoke", "--full")]
try:
    import experiments.exp_counterfactual_do_operator_v1 as _doop_preload  # noqa: F401
finally:
    sys.argv = _saved_argv


# ---------------------------------------------------------------------------
# infra: start-marker / atomic metrics / crash-diagnostic (SS 13 defensive)
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(str(REPO), "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "run_mode": RUN_MODE, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
    _write_metrics_atomic(output_dir, diag)


# ---------------------------------------------------------------------------
# qualitative polarity lexicon (fixed a priori; calibration_check=default_ok_for_this_regime)
# ---------------------------------------------------------------------------
_POS = {
    "increase", "increases", "increased", "increasing", "more", "greater", "higher", "larger",
    "bigger", "faster", "quicker", "stronger", "warmer", "hotter", "brighter", "closer", "nearer",
    "longer", "rise", "rises", "rising", "grow", "grows", "growing", "gain", "gains", "expand",
    "expands", "heavier", "denser", "harder", "taller", "wider", "deeper", "up", "raise", "raises",
    "accelerate", "accelerates", "speeds", "louder", "sharper",
}
_NEG = {
    "decrease", "decreases", "decreased", "decreasing", "less", "fewer", "lower", "smaller",
    "slower", "weaker", "cooler", "colder", "dimmer", "farther", "further", "shorter", "fall",
    "falls", "falling", "shrink", "shrinks", "shrinking", "lose", "loses", "losing", "contract",
    "contracts", "lighter", "softer", "down", "reduce", "reduces", "reduced", "slows", "quieter",
    "thinner", "shallower", "weaken", "weakens",
}


def _polarity_tokens(text):
    """Ordered list of (token, sign) for change-direction tokens in text (first->last)."""
    out = []
    for tok in str(text).lower().replace(",", " ").replace(";", " ").split():
        w = "".join(ch for ch in tok if ch.isalnum())
        if w in _POS:
            out.append((w, 1))
        elif w in _NEG:
            out.append((w, -1))
    return out


def _first_sign(text):
    p = _polarity_tokens(text)
    return p[0][1] if p else 0


# ---------------------------------------------------------------------------
# schema loading: parse_tablestore_typed -> signed (varA, varB, coupling) templates
# ---------------------------------------------------------------------------
def _content_set(text, content_words_fn):
    return set(content_words_fn(str(text), min_len=4))


def load_schemas(content_words_fn):
    """Reuse rel.parse_tablestore_typed(); keep CAUSE/IFTHEN/COUPLEDRELATIONSHIP with resolvable coupling.
    Returns list of dicts: {uid, relation, a0_txt, a1_txt, varA(set), varB(set), coupling, confident}."""
    from experiments import exp_arc_selection_relational_meaning_v1 as rel
    uid2typed = rel.parse_tablestore_typed()
    schemas = []
    for uid in sorted(uid2typed):
        rec = uid2typed[uid]
        relation = rec.get("relation", "")
        if relation not in TARGET_RELATIONS:
            continue
        a0 = rec.get("arg0", ""); a1 = rec.get("arg1", "")
        varA = _content_set(a0, content_words_fn)
        varB = _content_set(a1, content_words_fn)
        if not varA or not varB:
            continue
        if relation == "COUPLEDRELATIONSHIP":
            dA = _first_sign(a0); dB = _first_sign(a1)
            if dA == 0 or dB == 0:
                # no explicit change tokens on both sides -> default same-direction (low confidence)
                coupling = 1; confident = False
            else:
                coupling = dA * dB; confident = True
        else:
            # CAUSE / IFTHEN: qualitative positive coupling (condition present/up -> result present/up)
            coupling = 1; confident = True
        schemas.append({"uid": uid, "relation": relation, "a0_txt": a0.strip(), "a1_txt": a1.strip(),
                        "varA": varA, "varB": varB, "coupling": int(coupling), "confident": bool(confident)})
    return schemas


# ---------------------------------------------------------------------------
# schema-match classifier (Prediction 1 coverage) + do-calculus route (Arm B)
# ---------------------------------------------------------------------------
def match_schema(q, schemas, content_words_fn):
    """Return best-matching schema (or None). A question matches a schema if:
      - schema.varA overlaps stem content tokens, AND
      - schema.varB overlaps (stem OR any choice) content tokens, AND
      - the question is directional (>=1 polarity token in stem or choices).
    Best = max total token-overlap (varA_stem_overlap + varB_overlap); deterministic tie-break by uid."""
    stem_set = _content_set(q["stem"], content_words_fn)
    choice_sets = [_content_set(c, content_words_fn) for c in q["choices"]]
    all_choice = set().union(*choice_sets) if choice_sets else set()
    directional = bool(_polarity_tokens(q["stem"])) or any(_polarity_tokens(c) for c in q["choices"])
    if not directional:
        return None
    best = None  # (score, uid_tiebreak, schema)
    for s in schemas:
        oa = len(s["varA"] & stem_set)
        ob = len(s["varB"] & (stem_set | all_choice))
        if oa >= 1 and ob >= 1:
            score = oa + ob
            key = (score, s["uid"])
            if best is None or key > best[0]:
                best = (key, s)
    return best[1] if best is not None else None


def route_do_calculus(q, schema, arm_a_cos):
    """Wire the do-operator primitive: signed do()-override on varA -> topo-propagate coupling -> varB sign,
    with a merkle audit chain (reuse doop.h). arm_a_cos: [n_choices] similarity scores for tie-break.
    Returns (pred_choice_idx or None, audit_root, predicted_sign, intervention_sign)."""
    import experiments.exp_counterfactual_do_operator_v1 as doop
    # intervention direction stated in the stem (first change token); default +1 (a stated change)
    interv = _first_sign(q["stem"])
    if interv == 0:
        interv = 1
    # do(varA = interv): 2-node signed DAG varA -> varB, edge sign = coupling.
    # topo-propagate (same shape as doop.evaluate: descendants recomputed from parents under the override).
    base = {"A": 0, "B": 0}
    override = {"A": int(interv)}
    val = dict(base); val.update(override)
    val["B"] = int(np.sign(val["A"] * schema["coupling"]))   # coupling propagation (topo order A -> B)
    pred_sign = val["B"]
    # merkle audit chain of the intervention + recomputation (auditable do(), reuse doop.h)
    chain = doop.h("do(A=%d)|schema=%s|coupling=%d" % (interv, schema["uid"], schema["coupling"]))
    for node in ("A", "B"):
        chain = doop.h(chain + "%s=%d" % (node, val[node]))
    audit_root = chain
    # match choices by direction-sign of varB, NOT lexical surface
    from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
    aligned = []
    for ci, c in enumerate(q["choices"]):
        cset = set(arc._content_words(str(c), min_len=4))
        mentions_B = len(schema["varB"] & cset) >= 1
        csign = _first_sign(c)
        if mentions_B and csign != 0 and csign == pred_sign:
            aligned.append(ci)
    if not aligned:
        return None, audit_root, pred_sign, interv           # cannot resolve -> caller falls back to Arm A
    # tie-break aligned choices by Arm A similarity (deterministic argmax; stable index on ties)
    pick = max(aligned, key=lambda ci: (float(arm_a_cos[ci]), -ci))
    return pick, audit_root, pred_sign, interv


# ---------------------------------------------------------------------------
# similarity baseline (Arm A): CharTrigram cosine retrieval over WorldTree flat store
# ---------------------------------------------------------------------------
def build_arm_a(questions, encoder, store_vecs):
    """Per-(q,choice) best max-cosine over the fact store -> per-question choice cosines + Arm A pick.
    Returns (pred_A[list], cos_by_q[list of np arrays])."""
    from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
    texts, qmap = [], []
    for qi, q in enumerate(questions):
        for ci, c in enumerate(q["choices"]):
            texts.append(q["stem"] + " " + c); qmap.append((qi, ci))
    QV = arc._unit_rows(encoder.encode_batch(texts).astype(np.float32))
    nQ = QV.shape[0]; M = store_vecs.shape[0]
    best = np.full(nQ, -np.inf, dtype=np.float32)
    for a in range(0, M, 4000):
        sims = QV @ store_vecs[a:a + 4000].T
        best = np.maximum(best, sims.max(axis=1))
    cos_by_q = [np.full(len(q["choices"]), -np.inf, dtype=np.float32) for q in questions]
    for k, (qi, ci) in enumerate(qmap):
        cos_by_q[qi][ci] = best[k]
    pred_A = []
    rng = np.random.default_rng(SEED + 2)
    for qi, q in enumerate(questions):
        v = cos_by_q[qi]; mx = float(v.max())
        cand = [ci for ci in range(len(v)) if abs(float(v[ci]) - mx) < 1e-6]
        pred_A.append(int(rng.choice(cand)) if len(cand) > 1 else cand[0])
    return pred_A, cos_by_q


# ---------------------------------------------------------------------------
def _acc_over(idxs, preds, questions):
    if not idxs:
        return None
    c = sum(1 for qi in idxs if preds[qi] == questions[qi]["correct_index"])
    return c / len(idxs)


def _selftest():
    """Exercise the REAL substrate code paths at tiny scale (real_code_path gate)."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    import experiments.exp_counterfactual_do_operator_v1 as doop
    from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
    # 1. polarity lexicon signs
    assert _first_sign("a planet rotates faster") == 1
    assert _first_sign("the day becomes shorter") == -1
    assert _first_sign("no change here") == 0
    # 2. do-operator primitive reachable + merkle deterministic
    r1 = doop.h("do(A=1)"); r2 = doop.h("do(A=1)"); assert r1 == r2 and doop.h("x") != doop.h("y")
    # 3. route: same-direction coupling, +1 intervention -> +1 predicted; opposite -> -1
    qA = {"stem": "as widget spins faster what happens to output",
          "choices": ["output becomes larger", "output becomes smaller", "unrelated", "no effect"],
          "correct_index": 0}
    sA = {"uid": "test-0000", "relation": "COUPLEDRELATIONSHIP", "a0_txt": "widget increases",
          "a1_txt": "output increase", "varA": {"widget", "spins"}, "varB": {"output"},
          "coupling": 1, "confident": True}
    cos = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float32)
    pick, root, psign, interv = route_do_calculus(qA, sA, cos)
    assert interv == 1 and psign == 1 and pick == 0, (pick, psign, interv)
    sB = dict(sA); sB["coupling"] = -1
    pick2, _, psign2, _ = route_do_calculus(qA, sB, cos)
    assert psign2 == -1 and pick2 == 1, (pick2, psign2)
    # 4. REAL CharTrigram encode + retrieval scorer at N~4 questions / tiny store
    enc = CharTrigramEncoder(n_dim=256)
    qs = [qA, {"stem": "rougher surface increases what", "choices": ["friction increases", "friction decreases", "nothing", "color"], "correct_index": 0}]
    store = arc._unit_rows(enc.encode_batch(["as roughness increases friction increases", "the sky is blue"]).astype(np.float32))
    predA, cosq = build_arm_a(qs, enc, store)
    assert len(predA) == 2 and len(cosq) == 2 and cosq[0].shape[0] == 4
    # 5. match_schema fires on a directional coupled question
    schemas_tiny = [sA, {"uid": "z", "relation": "CAUSE", "a0_txt": "x", "a1_txt": "y",
                         "varA": {"nomatch"}, "varB": {"nomatch2"}, "coupling": 1, "confident": True}]
    m = match_schema(qA, schemas_tiny, arc._content_words)
    assert m is not None and m["uid"] == "test-0000", m
    print("[selftest] PASS: schema-routing do-calculus (real CharTrigram + do-op primitive + parser paths)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run():
    out_dir = _out_dir()
    _write_start_marker(out_dir, RUN_MODE)
    t0 = time.time()
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
    from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg

    easy_limit = 150 if RUN_MODE == "smoke" else None
    chal_limit = 150 if RUN_MODE == "smoke" else None
    questions = arc._load_questions(arc._EASY_TEST, easy_limit) + arc._load_questions(arc._CHAL_TEST, chal_limit)
    questions.sort(key=lambda q: q["qid"])
    n = len(questions)
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = n - n_easy
    print("[data] questions=%d (easy=%d challenge=%d)" % (n, n_easy, n_chal), flush=True)

    # fact store for Arm A: reuse agg.parse_tablestore() flat uid->sentence (all WorldTree tables)
    uid2sent = agg.parse_tablestore()
    store_sents = [uid2sent[u] for u in sorted(uid2sent) if str(uid2sent[u]).strip()]
    enc = CharTrigramEncoder(n_dim=N_DIM)
    store_vecs = arc._unit_rows(enc.encode_batch(store_sents).astype(np.float32))
    print("[store] flat WorldTree facts=%d dim=%d" % (store_vecs.shape[0], N_DIM), flush=True)

    # schemas (signed templates) from parse_tablestore_typed
    schemas = load_schemas(arc._content_words)
    n_coupled = sum(1 for s in schemas if s["relation"] == "COUPLEDRELATIONSHIP")
    print("[schemas] usable=%d (coupled=%d cause+ifthen=%d)" % (len(schemas), n_coupled, len(schemas) - n_coupled), flush=True)

    # Arm A similarity baseline
    pred_A, cos_by_q = build_arm_a(questions, enc, store_vecs)

    # schema-match (Prediction 1) + Arm B do-calculus route + random-schema must-fail control
    rng_ctrl = np.random.default_rng(SEED + 5)
    matched_idx = []
    matched_by_split = {"easy": [], "challenge": []}
    coupled_matched_idx = []
    pred_B = list(pred_A)     # default: Arm B == Arm A off the matched subset
    pred_R = list(pred_A)     # random-schema control
    b_resolved = 0            # matched q where Arm B produced a direction-resolved pick (else fell back)
    routes = []               # glass-box records
    for qi, q in enumerate(questions):
        s = match_schema(q, schemas, arc._content_words)
        if s is None:
            continue
        matched_idx.append(qi)
        split = "easy" if q["source"].startswith("ARC-Easy") else "challenge"
        matched_by_split[split].append(qi)
        if s["relation"] == "COUPLEDRELATIONSHIP":
            coupled_matched_idx.append(qi)
        pick, root, psign, interv = route_do_calculus(q, s, cos_by_q[qi])
        if pick is not None:
            pred_B[qi] = pick
            b_resolved += 1
        # must-fail control: route through a RANDOM schema (wrong template)
        rs = schemas[int(rng_ctrl.integers(0, len(schemas)))]
        pick_r, _, _, _ = route_do_calculus(q, rs, cos_by_q[qi])
        if pick_r is not None:
            pred_R[qi] = pick_r
        if len(routes) < 12:
            routes.append({
                "qid": q["qid"], "split": split, "stem": q["stem"][:200],
                "choices": [c[:80] for c in q["choices"]], "correct_index": q["correct_index"],
                "schema_uid": s["uid"], "schema_relation": s["relation"],
                "schema_a0": s["a0_txt"][:80], "schema_a1": s["a1_txt"][:80],
                "schema_coupling": s["coupling"], "intervention_sign": int(interv),
                "predicted_effect_sign": int(psign), "audit_root": root[:16],
                "arm_a_pick": int(pred_A[qi]), "arm_b_pick": int(pred_B[qi]),
                "arm_b_resolved": bool(pick is not None),
                "arm_a_correct": bool(pred_A[qi] == q["correct_index"]),
                "arm_b_correct": bool(pred_B[qi] == q["correct_index"]),
            })

    non_matched_idx = [qi for qi in range(n) if qi not in set(matched_idx)]
    cov_easy = len(matched_by_split["easy"]) / n_easy if n_easy else 0.0
    cov_chal = len(matched_by_split["challenge"]) / n_chal if n_chal else 0.0

    # accuracies
    accA_matched = _acc_over(matched_idx, pred_A, questions)
    accB_matched = _acc_over(matched_idx, pred_B, questions)
    accR_matched = _acc_over(matched_idx, pred_R, questions)
    accA_coupled = _acc_over(coupled_matched_idx, pred_A, questions)
    accB_coupled = _acc_over(coupled_matched_idx, pred_B, questions)
    accA_nonm = _acc_over(non_matched_idx, pred_A, questions)
    accB_nonm = _acc_over(non_matched_idx, pred_B, questions)
    accA_whole = _acc_over(list(range(n)), pred_A, questions)
    accB_whole = _acc_over(list(range(n)), pred_B, questions)
    chance = arc._chance_theoretical(questions)

    # discipline gates
    arms_differ = any(pred_A[qi] != pred_B[qi] for qi in matched_idx)
    baseline_in_band = (accA_matched is not None) and (0.05 < accA_matched < 0.95)
    discriminator_fired = len(matched_idx) > 0 and b_resolved > 0

    r = {
        "n": n, "n_easy": n_easy, "n_challenge": n_chal, "chance": chance,
        "n_schemas_usable": len(schemas), "n_coupled_schemas": n_coupled,
        "n_store_facts": int(store_vecs.shape[0]),
        # Prediction 1
        "coverage_easy": cov_easy, "coverage_challenge": cov_chal,
        "n_matched": len(matched_idx), "n_matched_easy": len(matched_by_split["easy"]),
        "n_matched_challenge": len(matched_by_split["challenge"]),
        "n_coupled_matched": len(coupled_matched_idx),
        # Prediction 2 (matched subset)
        "accA_matched": accA_matched, "accB_matched": accB_matched,
        "lift_matched_pp": (None if (accA_matched is None or accB_matched is None)
                            else round((accB_matched - accA_matched) * 100, 2)),
        "accA_coupled": accA_coupled, "accB_coupled": accB_coupled,
        "arm_b_resolved_count": b_resolved,
        # must-fail control
        "accR_matched_random_schema": accR_matched,
        "lift_random_pp": (None if (accA_matched is None or accR_matched is None)
                           else round((accR_matched - accA_matched) * 100, 2)),
        # Prediction 3 (non-matched)
        "accA_nonmatched": accA_nonm, "accB_nonmatched": accB_nonm,
        "n_nonmatched": len(non_matched_idx),
        # whole-set honesty
        "accA_whole": accA_whole, "accB_whole": accB_whole,
        # gates
        "arms_differ_verified": bool(arms_differ),
        "baseline_in_band": bool(baseline_in_band),
        "discriminator_fired": bool(discriminator_fired),
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "default_ok_for_this_regime",
        "crlb_n/a": "qualitative discrete MC accuracy has no Cramer-Rao noise floor",
        "glass_box_routes": routes,
        "elapsed_s": time.time() - t0,
    }
    return out_dir, r


def verdict(r):
    # Prediction 1: schema-match coverage
    p1_pass = (r["coverage_easy"] >= 0.05) or (r["coverage_challenge"] >= 0.08)
    p1_fail = (r["coverage_easy"] < 0.02) and (r["coverage_challenge"] < 0.02)
    p1 = "HARD_PASS" if p1_pass else ("HARD_FAIL" if p1_fail else "MIDDLE_BAND")
    # Prediction 2: >=10pp lift on matched subset (only meaningful if matched non-empty)
    if r["lift_matched_pp"] is None or r["n_matched"] == 0:
        p2 = "N/A"
    elif r["lift_matched_pp"] >= 10.0:
        p2 = "HARD_PASS"
    elif r["lift_matched_pp"] <= 0.0:
        p2 = "HARD_FAIL"
    else:
        p2 = "MIDDLE_BAND"
    # Prediction 3: on non-matched, Arm A >= Arm B (control). HARD_FAIL if Arm B beats Arm A there.
    if r["accA_nonmatched"] is None or r["accB_nonmatched"] is None:
        p3 = "N/A"
    elif r["accB_nonmatched"] > r["accA_nonmatched"] + 1e-9:
        p3 = "HARD_FAIL"
    else:
        p3 = "HARD_PASS"
    # must-fail control: random schema must NOT beat Arm A on matched subset
    mustfail_ok = (r["lift_random_pp"] is None) or (r["lift_random_pp"] < 10.0)

    parts = ["P1_coverage=%s (easy=%.3f chal=%.3f; matched=%d/%d)" %
             (p1, r["coverage_easy"], r["coverage_challenge"], r["n_matched"], r["n"])]
    parts.append("P2_matched=%s (accA=%s accB=%s lift=%spp; coupled accA=%s accB=%s)" %
                 (p2, r["accA_matched"], r["accB_matched"], r["lift_matched_pp"],
                  r["accA_coupled"], r["accB_coupled"]))
    parts.append("P3_nonmatched=%s (accA=%s accB=%s)" % (p3, r["accA_nonmatched"], r["accB_nonmatched"]))
    parts.append("MUSTFAIL_random_schema=%s (accR=%s lift=%spp)" %
                 ("OK" if mustfail_ok else "LEAK", r["accR_matched_random_schema"], r["lift_random_pp"]))
    parts.append("whole: accA=%s accB=%s chance=%.3f" % (r["accA_whole"], r["accB_whole"], r["chance"]))
    parts.append("gates: arms_differ=%s baseline_in_band=%s discriminator_fired=%s" %
                 (r["arms_differ_verified"], r["baseline_in_band"], r["discriminator_fired"]))
    msg = " | ".join(parts)

    # overall tier: the central claim is P2 gated on P1 (coverage) + must-fail control
    if not r["discriminator_fired"] or r["n_matched"] == 0:
        tier = "HARD_FAIL_STRUCTURE_STARVED" if p1 == "HARD_FAIL" else "INCONCLUSIVE_DISCRIMINATOR_NOT_FIRED"
    elif p1 == "HARD_PASS" and p2 == "HARD_PASS" and mustfail_ok:
        tier = "HARD_PASS"
    elif p1 == "HARD_FAIL":
        tier = "HARD_FAIL_STRUCTURE_STARVED"
    elif p2 == "HARD_FAIL":
        tier = "HARD_FAIL_ROUTING_NO_LIFT"
    elif not mustfail_ok:
        tier = "HARD_FAIL_RANDOM_SCHEMA_LEAK"
    else:
        tier = "MIDDLE_BAND"
    return tier, msg, {"P1": p1, "P2": p2, "P3": p3, "mustfail_ok": mustfail_ok}


def main():
    print("[config] anchor=%s mode=%s seed=%d N_DIM=%d" % (ANCHOR_NAME, RUN_MODE, SEED, N_DIM), flush=True)
    out_dir, r = run()
    tier, msg, preds = verdict(r)
    print("\n[VERDICT] %s :: %s" % (tier, msg), flush=True)
    # glass-box: show one correct + one incorrect matched route
    for label, want in (("CORRECT", True), ("INCORRECT", False)):
        ex = next((x for x in r["glass_box_routes"] if x["arm_b_resolved"] and x["arm_b_correct"] == want), None)
        if ex:
            print("[glassbox %s] qid=%s schema=%s(%s) coupling=%d interv=%+d pred_effect=%+d -> B_pick=%d gold=%d | %s"
                  % (label, ex["qid"], ex["schema_uid"], ex["schema_relation"], ex["schema_coupling"],
                     ex["intervention_sign"], ex["predicted_effect_sign"], ex["arm_b_pick"],
                     ex["correct_index"], ex["stem"][:90]), flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg,
        "summary": tier, "run_mode": RUN_MODE, "n_seeds": 1,
        "predictions": preds, "elapsed_s": r["elapsed_s"], "per_seed": [r], **r,
    }
    _write_metrics_atomic(out_dir, metrics)
    print("[metrics] written -> %s" % os.path.join(out_dir, "metrics.json"), flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(_out_dir(), e)
    raise
