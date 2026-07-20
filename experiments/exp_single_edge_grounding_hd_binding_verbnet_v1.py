"""SINGLE-EDGE SUBSTRATE-NATIVE GROUNDING via HD BINDING (VerbNet-sourced), v1.

USER's proposed MINIMAL DEFINITIVE existence proof of the grounding capability: take a sentence the
reader currently FAILS on a who-is-affected / PP-attachment thematic-role ambiguity, look up ONE
structured fact that resolves it (real NLTK VerbNet class membership for the creation-verb class
build-26.1), STORE that fact SUBSTRATE-NATIVE as an HD binding (hdlab.binding.bind, NOT a dict), and
show the reader now solves it -- AND generalizes to a held-out same-verb sentence, while a
wrong/irrelevant edge does NOT resolve it, and a sentence-specific (memorization-style) key does NOT
generalize the way a verb-class key does.

See preregs/2026-07-20_single_edge_grounding_hd_binding_verbnet_v1.md for the full design, the
FHRR-exact-recovery analytical prediction, and the pre-registered bands (NOT tuned to pass).

THE 5 ARMS (each a single torch.Tensor (N_DIM,) complex64 -- never a dict; see self_test for the
type/mechanism-integrity assertions):
  WEB_EMPTY         : zeros -- pre-storage / no-edge (difficulty-on baseline; margin must be exactly 0)
  WEB_BUILD_EDGE    : bind(KEY_BUILD, TYPE_ARTIFACT) -- the single stored edge under test
  WEB_EAT_EDGE_ONLY : bind(KEY_EAT, TYPE_FOOD) -- wrong/irrelevant-edge control (no build edge)
  WEB_BOTH_EDGES    : WEB_BUILD_EDGE + WEB_EAT_EDGE_ONLY -- genuine superposition (bundle) of 2 facts
  WEB_MEMORIZATION  : bind(KEY_SENT_T1, TYPE_ARTIFACT) -- sentence-scoped key (memorization contrast)

RECALL: recovered = unbind(web, key); score(candidate) = atoms.similarity(recovered, type_vec(candidate))
(real hdlab.binding.unbind + hdlab.atoms.similarity, unmodified; no invented math, no dict lookup).

ASCII-only. No emojis. No em dashes.
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

import torch  # noqa: E402

ANCHOR_NAME = "single_edge_grounding_hd_binding_verbnet_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import atoms as A  # noqa: E402
from hdlab import binding as B  # noqa: E402

try:
    from nltk.corpus import verbnet as vn  # noqa: E402
    _VERBNET_AVAILABLE = True
except Exception:
    vn = None
    _VERBNET_AVAILABLE = False

N_DIM = 1024
SEED = 20260720
MARGIN_THRESH = 0.10

# ==================================================================================================
# Noun -> filler-TYPE lexicon (independent, general-vocabulary classification -- disjoint concern
# from per-sentence gold, see prereg "SENTENCE SET" section).
# ==================================================================================================
TYPE_OF_NOUN = {
    "fort": "ARTIFACT", "cabin": "ARTIFACT", "bridge": "ARTIFACT", "dam": "ARTIFACT",
    "house": "ARTIFACT", "hut": "ARTIFACT",
    "river": "LOCATION", "lake": "LOCATION", "valley": "LOCATION", "kitchen": "LOCATION",
    "barn": "LOCATION", "garden": "LOCATION",
    "soup": "FOOD", "bread": "FOOD", "cake": "FOOD",
}

# ==================================================================================================
# Sentence set (hand-authored, clean, small, ASCII; independent of the lookup source).
# ==================================================================================================
ITEMS = [
    # id,  sentence,                                          verb,    vclass,   true,      false
    ("T1", "The girl built a fort by the river.",             "build", "BUILD", "fort",    "river"),
    ("G1", "He built a cabin near the lake.",                 "build", "BUILD", "cabin",   "lake"),
    ("G2", "They built a bridge across the valley.",          "build", "BUILD", "bridge",  "valley"),
    ("X1", "She ate the soup in the kitchen.",                "eat",   "EAT",   "soup",    "kitchen"),
    ("X2", "He ate the bread near the barn.",                 "eat",   "EAT",   "bread",   "barn"),
]
ITEM_ROLE = {"T1": "stored_train", "G1": "heldout_generalization", "G2": "heldout_generalization",
             "X1": "crossverb_control", "X2": "crossverb_control"}
EXPECTED_N_ITEMS = 5
EXPECTED_N_ARMS = 5
EXPECTED_N_UNITS = EXPECTED_N_ARMS * EXPECTED_N_ITEMS * 2  # 2 candidates (true, false) per item


def verbnet_lookup_facts():
    """Real NLTK VerbNet lookup for the looked-up edge (build-26.1 Product role) + the eat control
    class-id, for provenance logging. Degrades to a logged flag (not silently) if unavailable."""
    facts = {"verbnet_available": _VERBNET_AVAILABLE}
    if not _VERBNET_AVAILABLE:
        return facts
    facts["build_classids"] = vn.classids("build")
    facts["eat_classids"] = vn.classids("eat")
    vc = vn.vnclass("build-26.1")
    themroles = vc.find("THEMROLES")
    role_types = [tr.get("type") for tr in themroles.findall("THEMROLE")]
    facts["build_26_1_themroles"] = role_types
    facts["build_has_product_role"] = "Product" in role_types
    return facts


# ==================================================================================================
# HD construction: atoms, keys, webs (all real hdlab.atoms / hdlab.binding primitives).
# ==================================================================================================
def build_atoms(seed=SEED, n_dim=N_DIM):
    gen = torch.Generator().manual_seed(seed)
    names = ["ROLE_PATIENT", "VC_BUILD", "VC_EAT",
             "TYPE_ARTIFACT", "TYPE_LOCATION", "TYPE_FOOD",
             "SENT_KEY_T1", "SENT_KEY_G1", "SENT_KEY_G2", "SENT_KEY_X1", "SENT_KEY_X2"]
    atom = {}
    for name in names:
        atom[name] = A.make_atom_fhrr(n_dim, gen)
    return atom


def build_webs_and_keys(atom):
    key_build = B.bind(atom["VC_BUILD"], atom["ROLE_PATIENT"])
    key_eat = B.bind(atom["VC_EAT"], atom["ROLE_PATIENT"])
    sent_key = {iid: B.bind(atom[f"SENT_KEY_{iid}"], atom["ROLE_PATIENT"])
                for iid in ("T1", "G1", "G2", "X1", "X2")}

    web_build_edge = B.bind(key_build, atom["TYPE_ARTIFACT"])
    web_eat_edge_only = B.bind(key_eat, atom["TYPE_FOOD"])
    webs = {
        "WEB_EMPTY": torch.zeros(atom["ROLE_PATIENT"].shape[0], dtype=atom["ROLE_PATIENT"].dtype),
        "WEB_BUILD_EDGE": web_build_edge,
        "WEB_EAT_EDGE_ONLY": web_eat_edge_only,
        "WEB_BOTH_EDGES": web_build_edge + web_eat_edge_only,
        "WEB_MEMORIZATION": B.bind(sent_key["T1"], atom["TYPE_ARTIFACT"]),
    }
    keys = {"key_build": key_build, "key_eat": key_eat, "sent_key": sent_key}
    return webs, keys


def type_vec(atom, noun):
    t = TYPE_OF_NOUN.get(noun)
    if t is None:
        raise KeyError(f"noun {noun!r} missing from TYPE_OF_NOUN lexicon (fail loud, no silent None)")
    return atom[f"TYPE_{t}"]


def score_item(atom, web, key, iid, verb_class, true_noun, false_noun):
    """recovered = unbind(web, key); score(c) = atoms.similarity(recovered, type_vec(c)).
    Real hdlab.binding.unbind + hdlab.atoms.similarity, unmodified; no dict lookup in this path."""
    recovered = B.unbind(web, key)
    # atoms.similarity always returns a real-valued tensor (real part of the conjugate inner
    # product for complex/FHRR inputs; see hdlab/atoms.py), so a plain float() cast is exact.
    s_true = float(A.similarity(recovered, type_vec(atom, true_noun)))
    s_false = float(A.similarity(recovered, type_vec(atom, false_noun)))
    margin = s_true - s_false
    predicted = true_noun if s_true >= s_false else false_noun
    # full 3-entry codebook cleanup (k=1 nearest neighbor via the same real primitive)
    codebook_names = ["ARTIFACT", "LOCATION", "FOOD"]
    cb_scores = {t: float(A.similarity(recovered, atom[f"TYPE_{t}"])) for t in codebook_names}
    cleanup_argmax = max(cb_scores, key=cb_scores.get)
    return {
        "item": iid, "verb_class": verb_class, "true_noun": true_noun, "false_noun": false_noun,
        "score_true": round(s_true, 6), "score_false": round(s_false, 6), "margin": round(margin, 6),
        "predicted": predicted, "resolved_correct": bool(predicted == true_noun and margin >= MARGIN_THRESH),
        "cleanup_codebook_scores": {k: round(v, 6) for k, v in cb_scores.items()},
        "cleanup_argmax_type": cleanup_argmax,
    }


def run_arm(atom, webs, keys, arm_name):
    web = webs[arm_name]
    rows = []
    for iid, sent, verb, vclass, true_n, false_n in ITEMS:
        key = keys["sent_key"][iid] if arm_name == "WEB_MEMORIZATION" else (
            keys["key_build"] if vclass == "BUILD" else keys["key_eat"])
        row = score_item(atom, web, key, iid, vclass, true_n, false_n)
        row["sentence"] = sent
        row["item_role"] = ITEM_ROLE[iid]
        rows.append(row)
    return rows


def arms_differ_hash(webs):
    digests = {}
    for name, w in webs.items():
        b = w.numpy().tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], (
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical webs")
    return digests


def mechanism_integrity_check(webs):
    """Design-gate item 2: every web is a torch.Tensor HD vector, never a dict/hashmap."""
    for name, w in webs.items():
        assert isinstance(w, torch.Tensor), f"{name} is not a torch.Tensor: {type(w)}"
        assert not isinstance(w, dict), f"{name} is a dict -- FORBIDDEN (must be an HD binding)"
        assert w.shape == (N_DIM,), f"{name} shape {w.shape} != ({N_DIM},)"
        assert w.dtype == torch.complex64, f"{name} dtype {w.dtype} != complex64"
    return True


# ==================================================================================================
# Verdict logic.
# ==================================================================================================
def build_verdict(by_arm):
    def get(arm, iid):
        return next(r for r in by_arm[arm] if r["item"] == iid)

    gate = {}
    gate["difficulty_on"] = all(r["margin"] == 0.0 for r in by_arm["WEB_EMPTY"])
    gate["store_solved"] = get("WEB_BUILD_EDGE", "T1")["resolved_correct"]
    gate["generalizes_G1"] = get("WEB_BUILD_EDGE", "G1")["resolved_correct"]
    gate["generalizes_G2"] = get("WEB_BUILD_EDGE", "G2")["resolved_correct"]
    gate["generalizes_both"] = gate["generalizes_G1"] and gate["generalizes_G2"]
    gate["generalizes_any"] = gate["generalizes_G1"] or gate["generalizes_G2"]
    gate["build_edge_leaks_to_eat"] = (get("WEB_BUILD_EDGE", "X1")["resolved_correct"]
                                       or get("WEB_BUILD_EDGE", "X2")["resolved_correct"])
    gate["eat_edge_leaks_to_build"] = any(get("WEB_EAT_EDGE_ONLY", iid)["resolved_correct"]
                                          for iid in ("T1", "G1", "G2"))
    gate["wrong_edge_must_fail_fires"] = (not gate["build_edge_leaks_to_eat"]
                                          and not gate["eat_edge_leaks_to_build"])
    gate["superposition_solves_all"] = all(get("WEB_BOTH_EDGES", row[0])["resolved_correct"]
                                           for row in ITEMS)
    gate["memorization_solves_train"] = get("WEB_MEMORIZATION", "T1")["resolved_correct"]
    gate["memorization_fails_gen"] = (not get("WEB_MEMORIZATION", "G1")["resolved_correct"]
                                      and not get("WEB_MEMORIZATION", "G2")["resolved_correct"])

    hard_fail_reasons = []
    if not gate["difficulty_on"]:
        hard_fail_reasons.append("WEB_EMPTY margin != 0 on some item (difficulty not genuinely on)")
    if not gate["store_solved"]:
        hard_fail_reasons.append("WEB_BUILD_EDGE fails to resolve T1 (store/recall mechanism broken)")
    if not gate["generalizes_any"]:
        hard_fail_reasons.append("WEB_BUILD_EDGE fails BOTH G1 and G2 (zero generalization; pure memorization)")
    if gate["build_edge_leaks_to_eat"] or gate["eat_edge_leaks_to_build"]:
        hard_fail_reasons.append("wrong/irrelevant edge resolves an unrelated item (any-storage-helps / specificity violated)")

    hard_pass = (gate["difficulty_on"] and gate["store_solved"] and gate["generalizes_both"]
                and gate["wrong_edge_must_fail_fires"] and gate["superposition_solves_all"]
                and gate["memorization_solves_train"] and gate["memorization_fails_gen"])

    if hard_fail_reasons:
        verdict = "HARD_FAIL_SINGLE_EDGE_GROUNDING"
    elif hard_pass:
        verdict = "HARD_PASS_SINGLE_EDGE_GROUNDING"
    else:
        verdict = "MIDDLE_BAND_SINGLE_EDGE_GROUNDING"

    return verdict, gate, hard_fail_reasons


# ==================================================================================================
# Run + metrics I/O.
# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    atom = build_atoms()
    webs, keys = build_webs_and_keys(atom)

    mechanism_integrity_check(webs)
    digests = arms_differ_hash(webs)

    by_arm = {name: run_arm(atom, webs, keys, name) for name in webs}
    verdict, gate, hard_fail_reasons = build_verdict(by_arm)
    vn_facts = verbnet_lookup_facts()

    elapsed = time.perf_counter() - t0
    n_units = sum(len(rows) * 2 for rows in by_arm.values())  # 2 candidates scored per row
    cardinality_ok = (n_units == EXPECTED_N_UNITS)

    msg = (f"verdict={verdict} | difficulty_on={gate['difficulty_on']} "
           f"store_solved={gate['store_solved']} generalizes_both={gate['generalizes_both']} "
           f"(G1={gate['generalizes_G1']} G2={gate['generalizes_G2']}) "
           f"wrong_edge_must_fail_fires={gate['wrong_edge_must_fail_fires']} "
           f"superposition_solves_all={gate['superposition_solves_all']} "
           f"memorization_solves_train_but_fails_gen="
           f"{gate['memorization_solves_train'] and gate['memorization_fails_gen']} "
           f"| n_units={n_units} cardinality_ok={cardinality_ok} "
           f"verbnet_available={_VERBNET_AVAILABLE}")

    out_dir = _out_dir(mode)
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_dim": N_DIM, "seed": SEED, "margin_thresh": MARGIN_THRESH,
        "gate": gate, "hard_fail_reasons": hard_fail_reasons,
        "by_arm": by_arm, "web_hashes": digests,
        "verbnet_facts": vn_facts,
        "cardinality_ok": cardinality_ok, "expected_n_units": EXPECTED_N_UNITS, "n_units": n_units,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": ("categorical resolved/not-resolved margin-threshold metric over an exact-recovery "
                     "FHRR binding; no argmax-capacity CRLB formula applies; see prereg THEORETICAL "
                     "section for the applicable closed-form exact-recovery + O(1/sqrt(N_DIM)) "
                     "cross-talk analysis"),
        "claim_ceiling": ("Single-edge existence-proof measurement on a small hand-authored sentence "
                          "set; not a claim about scale, corpus coverage, or novel-noun generalization "
                          "(that is the separate 29379-82 CG). Demonstrates storage-format + recall + "
                          "verb-class generalization via genuine HD binding, not a dict."),
        "REQUIRED_FIELDS": ["verdict", "gate", "by_arm", "web_hashes", "verbnet_facts",
                            "cardinality_ok", "arms_differ_verified"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    for arm_name, rows in by_arm.items():
        for r in rows:
            print(f"  [{arm_name}] {r['item']} ({r['verb_class']}): true={r['true_noun']} "
                  f"false={r['false_noun']} score_true={r['score_true']:.4f} "
                  f"score_false={r['score_false']:.4f} margin={r['margin']:.4f} "
                  f"predicted={r['predicted']} resolved_correct={r['resolved_correct']}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ==================================================================================================
# Self-test (real code path: constructs the REAL atoms/webs/keys at the actual tiny item set).
# ==================================================================================================
def self_test():
    atom = build_atoms()
    webs, keys = build_webs_and_keys(atom)

    # --- mechanism-integrity: every web is a genuine HD binding, never a dict ---
    mechanism_integrity_check(webs)
    digests = arms_differ_hash(webs)
    assert len(set(digests.values())) == len(digests), "arms_differ hash collision"

    # --- FHRR exact single-fact recovery sanity (THEORETICAL prediction check) ---
    key_build = keys["key_build"]
    recovered = B.unbind(webs["WEB_BUILD_EDGE"], key_build)
    sim_to_artifact = float(A.similarity(recovered, atom["TYPE_ARTIFACT"]))
    assert abs(sim_to_artifact - 1.0) < 1e-3, (
        f"FHRR single-fact unbind must recover TYPE_ARTIFACT near-exactly (sim={sim_to_artifact:.6f})")
    sim_to_location = float(A.similarity(recovered, atom["TYPE_LOCATION"]))
    assert abs(sim_to_location) < 0.20, (
        f"cross term to an unrelated type must be small (sim={sim_to_location:.6f})")

    # --- WEB_EMPTY gives exactly zero score to everything (difficulty-on / real-zero-signal) ---
    recovered_empty = B.unbind(webs["WEB_EMPTY"], key_build)
    assert torch.allclose(recovered_empty, torch.zeros_like(recovered_empty)), (
        "WEB_EMPTY unbind must be exactly zero")
    s_empty = float(A.similarity(recovered_empty, atom["TYPE_ARTIFACT"]))
    assert s_empty == 0.0, f"WEB_EMPTY score must be exactly 0.0, got {s_empty}"

    # --- lexicon coverage: every noun used in ITEMS is in TYPE_OF_NOUN (fail loud if not) ---
    for iid, sent, verb, vclass, true_n, false_n in ITEMS:
        assert true_n in TYPE_OF_NOUN, f"{iid}: true noun {true_n!r} missing from lexicon"
        assert false_n in TYPE_OF_NOUN, f"{iid}: false noun {false_n!r} missing from lexicon"
    assert len(ITEMS) == EXPECTED_N_ITEMS, f"expected {EXPECTED_N_ITEMS} items, got {len(ITEMS)}"

    # --- real code path: run_arm on WEB_BUILD_EDGE + verdict logic on a toy full pass ---
    by_arm = {name: run_arm(atom, webs, keys, name) for name in webs}
    verdict, gate, hard_fail_reasons = build_verdict(by_arm)
    assert verdict in ("HARD_PASS_SINGLE_EDGE_GROUNDING", "MIDDLE_BAND_SINGLE_EDGE_GROUNDING",
                       "HARD_FAIL_SINGLE_EDGE_GROUNDING"), f"unexpected verdict string: {verdict}"

    # --- real NLTK VerbNet lookup exercised (degrades gracefully, logged not swallowed) ---
    vn_facts = verbnet_lookup_facts()
    if _VERBNET_AVAILABLE:
        assert "build-26.1-1" in vn_facts["build_classids"], vn_facts
        assert vn_facts["build_has_product_role"] is True, vn_facts
    else:
        print(f"[{ANCHOR_NAME}] WARN: NLTK VerbNet corpus unavailable in this environment -- "
              f"provenance logging degrades to verbnet_available=False, not silently swallowed.",
              flush=True)

    print(f"[{ANCHOR_NAME}] self-test PASS | mechanism_integrity=ok arms_differ=ok "
          f"single_fact_recovery_sim={sim_to_artifact:.4f} cross_term_sim={sim_to_location:.4f} "
          f"empty_web_score={s_empty} lexicon_coverage=ok toy_verdict={verdict} "
          f"verbnet_available={_VERBNET_AVAILABLE}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        # No separate full regime exists for this cell (closed-form exact-recovery measurement,
        # see prereg "Compute architecture"); --full runs the identical deterministic item set.
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
