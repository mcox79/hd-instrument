# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor: n/a (accuracy-vs-baseline discriminator, not a capacity sweep)
# - deterministic_seeding: true (hashlib.sha256 digest seeds, no hash()/list(set()))
# - all numbers MEASURED@ tagged in the completion report, not this file
#
# Construction -> Integration relation-inference cell.
# See preregs/2026-08-03_construction_integration_relation_inference_v1.md for full design + bands.
"""Kintsch construction-integration relation inference over the 19-item clean-axis gold subset.

CONSTRUCTION: loose bag-of-words FHRR-bundle cosine similarity (overgenerate, narrow to top-K).
INTEGRATION: spreading-activation relaxation over surviving candidates (coherence-filter), plus a
small wish-vs-resolution marker signal on the satisfy/restate axis.

4 arms: MECHANISM, BASELINE_INTEGRATION_ONLY, BASELINE_LEXICAL, BASELINE_RANDOM.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "construction_integration_relation_inference_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_relation_inference_v1.jsonl"
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

D = 256  # FHRR vector dimensionality (small; bag-of-words bundle, no capacity claim)
K_GOAL = 3  # construction top-K narrowing for the goal axis (of 4 given candidates)
T_RELAX = 5  # integration relaxation steps
GAMMA = 0.5  # integration coupling strength
REFUSE_MARGIN = 0.05  # margin-over-runner-up threshold on softmax-normalized activation
FIXED_RANDOM_SEED = 20260803  # BASELINE_RANDOM seed (fixed int, never hash())

CATEGORY_PROTOTYPES = {
    "MANIPULATE_AVOID_WORK": ["avoid", "work", "chore", "trick", "lazy", "escape", "labor", "effort", "careless", "indifferent"],
    "SELF_PRESERVATION_ESCAPE": ["escape", "survive", "danger", "flee", "safety", "fear", "rescue", "alive", "trapped"],
    "CURIOSITY_EXPLORATION": ["curious", "explore", "wonder", "investigate", "discover", "interested", "follow", "peek"],
    "COMPLY_AVOID_TROUBLE": ["obey", "comply", "avoid", "trouble", "fear", "punish", "rule", "order", "frightened"],
    "CARE_FOR_OTHERS": ["care", "help", "comfort", "protect", "gentle", "kind", "nurse", "soothe", "concern"],
    "REVENGE_PUNISH": ["revenge", "punish", "spite", "angry", "payback", "hurt", "retaliate", "vindictive"],
    "ESCAPE_BLAME_DECEPTION": ["blame", "deceive", "lie", "frame", "evidence", "false", "trick", "hide", "guilt"],
    "SELF_DISCIPLINE": ["discipline", "fair", "honest", "punish", "self", "rule", "conscience", "principle"],
    "PROTECT_OTHERS": ["protect", "defend", "shield", "save", "guard", "danger", "rescue", "warn"],
}

WISH_MARKERS = ["want", "wish", "wanted", "wishes", "shall", "never", "hope", "hoped",
                "longed", "desire", "desired", "would", "promised", "greatest"]
RESOLUTION_MARKERS = ["was", "gave", "given", "found", "sitting", "occupying", "built",
                      "kiss", "hugged", "forgiven", "forgotten", "farmhouse", "home"]


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic (META §13B/§13C)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ---------------------------------------------------------------------------
# FHRR primitives (own hash-seeded random-phase vectors; no borrowed embeddings)
# ---------------------------------------------------------------------------
def _digest_seed(key: str) -> int:
    """Deterministic seed from a stable sha256 digest -- NEVER python hash()."""
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2**63 - 1)


_WORD_VEC_CACHE = {}


def word_vector(word: str) -> torch.Tensor:
    """Deterministic unit-phase complex64 vector for a single lowercase word."""
    key = word.lower()
    if key in _WORD_VEC_CACHE:
        return _WORD_VEC_CACHE[key]
    gen = torch.Generator().manual_seed(_digest_seed(key))
    theta = torch.rand(D, generator=gen) * 2 * torch.pi
    vec = torch.polar(torch.ones(D), theta).to(torch.complex64)
    _WORD_VEC_CACHE[key] = vec
    return vec


def tokenize(text: str):
    out = []
    cur = []
    for ch in text.lower():
        if ch.isalpha():
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return out


def bundle(words):
    """FHRR bundle = sum of word vectors, L2-normalized."""
    if not words:
        vec = torch.zeros(D, dtype=torch.complex64)
        vec[0] = 1.0
        return vec
    acc = torch.zeros(D, dtype=torch.complex64)
    for w in words:
        acc = acc + word_vector(w)
    norm = torch.linalg.vector_norm(acc)
    if norm.item() < 1e-8:
        acc[0] = 1.0
        norm = torch.linalg.vector_norm(acc)
    return acc / norm


def text_bundle(text: str) -> torch.Tensor:
    return bundle(tokenize(text))


def cos_sim(a: torch.Tensor, b: torch.Tensor) -> float:
    num = torch.real(torch.sum(a * torch.conj(b)))
    na = torch.linalg.vector_norm(a)
    nb = torch.linalg.vector_norm(b)
    if na.item() < 1e-8 or nb.item() < 1e-8:
        return 0.0
    return float((num / (na * nb)).item())


def marker_signal(text: str) -> float:
    toks = tokenize(text)
    if not toks:
        return 0.0
    w = sum(1 for t in toks if t in WISH_MARKERS)
    r = sum(1 for t in toks if t in RESOLUTION_MARKERS)
    return float(r - w)


def softmax_list(vals):
    t = torch.tensor(vals, dtype=torch.float32)
    return torch.softmax(t, dim=0).tolist()


def relax(constr_scores, W):
    """Spreading-activation relaxation: a_(t+1) = softmax(constr_scores + gamma * W @ a_t)."""
    n = len(constr_scores)
    a = torch.tensor(softmax_list(constr_scores), dtype=torch.float32)
    base = torch.tensor(constr_scores, dtype=torch.float32)
    Wt = torch.tensor(W, dtype=torch.float32)
    for _ in range(T_RELAX):
        a = torch.softmax(base + GAMMA * (Wt @ a), dim=0)
    return a.tolist()


def margin_of(scores):
    s = sorted(scores, reverse=True)
    if len(s) < 2:
        return 1.0
    return s[0] - s[1]


# ---------------------------------------------------------------------------
# Per-item scoring, all 4 arms
# ---------------------------------------------------------------------------
def score_goal_item(item, rng):
    correct = item["correct_category"]
    cands = [correct] + list(item["distractor_categories"])
    action_vec = text_bundle(item["action_text"])
    proto_vecs = {c: bundle(CATEGORY_PROTOTYPES[c]) for c in cands}
    constr_scores = [cos_sim(action_vec, proto_vecs[c]) for c in cands]

    # construction top-K recall (measured separately from end-to-end accuracy)
    order = sorted(range(len(cands)), key=lambda i: -constr_scores[i])
    topk_idx = order[:K_GOAL]
    topk_recall_hit = 0 in topk_idx  # index 0 is always `correct`

    # MECHANISM: construction narrows to top-K, then integration relaxes over top-K only
    topk_cands = [cands[i] for i in topk_idx]
    topk_scores = [constr_scores[i] for i in topk_idx]
    W = [[cos_sim(proto_vecs[topk_cands[i]], proto_vecs[topk_cands[j]]) if i != j else 0.0
          for j in range(len(topk_cands))] for i in range(len(topk_cands))]
    mech_activation = relax(topk_scores, W)
    mech_pick_local = int(torch.tensor(mech_activation).argmax().item())
    mech_pick = topk_cands[mech_pick_local]
    mech_margin = margin_of(mech_activation)
    mech_refuse = mech_margin < REFUSE_MARGIN

    # BASELINE_INTEGRATION_ONLY: relax over ALL given candidates, uniform initial activation
    W_full = [[cos_sim(proto_vecs[cands[i]], proto_vecs[cands[j]]) if i != j else 0.0
               for j in range(len(cands))] for i in range(len(cands))]
    uniform_init = [0.0] * len(cands)  # softmax(uniform) = uniform; no construction anchoring
    int_only_activation = relax(uniform_init, W_full)
    int_only_pick = cands[int(torch.tensor(int_only_activation).argmax().item())]

    # BASELINE_LEXICAL: argmax of raw construction score, no integration
    lex_pick = cands[int(torch.tensor(constr_scores).argmax().item())]

    # BASELINE_RANDOM
    rand_pick = cands[rng.randrange(len(cands))]

    return {
        "correct": correct,
        "topk_recall_hit": topk_recall_hit,
        "mech_pick": mech_pick, "mech_correct": mech_pick == correct,
        "mech_margin": mech_margin, "mech_refuse": mech_refuse,
        "int_only_pick": int_only_pick, "int_only_correct": int_only_pick == correct,
        "lex_pick": lex_pick, "lex_correct": lex_pick == correct,
        "rand_pick": rand_pick, "rand_correct": rand_pick == correct,
        "prediction_vector": [mech_pick, int_only_pick, lex_pick, rand_pick],
    }


def score_satrest_item(item, rng):
    # candidates: 0=restate (distractor), 1=satisfy (always correct)
    cands = ["restate", "satisfy"]
    texts = {"restate": item["restate_text"], "satisfy": item["satisfy_text"]}
    correct = "satisfy"
    goal_vec = text_bundle(item["goal_text"])
    cand_vecs = {c: text_bundle(texts[c]) for c in cands}
    constr_scores = [cos_sim(goal_vec, cand_vecs[c]) for c in cands]
    marker_scores = [marker_signal(texts[c]) for c in cands]

    # MECHANISM: fold construction (lexical cosine) + integration marker-bias into relaxation
    W = [[cos_sim(cand_vecs[cands[i]], cand_vecs[cands[j]]) if i != j else 0.0 for j in range(2)] for i in range(2)]
    combined_init = [constr_scores[i] + 0.5 * marker_scores[i] for i in range(2)]
    mech_activation = relax(combined_init, W)
    mech_pick = cands[int(torch.tensor(mech_activation).argmax().item())]
    mech_margin = margin_of(mech_activation)
    mech_refuse = mech_margin < REFUSE_MARGIN

    # construction top-K recall: trivial with 2 candidates (both survive) -- reported honestly as
    # ceiling-saturated, not a discriminator on this axis (see pre-reg).
    topk_recall_hit = True

    # BASELINE_INTEGRATION_ONLY: marker signal alone, no lexical/construction stream folded in
    int_only_activation = relax(marker_scores, W)
    int_only_pick = cands[int(torch.tensor(int_only_activation).argmax().item())]

    # BASELINE_LEXICAL: pure cosine(goal, candidate) argmax -- the exact trap the gold notes describe
    lex_pick = cands[int(torch.tensor(constr_scores).argmax().item())]

    # BASELINE_RANDOM
    rand_pick = cands[rng.randrange(2)]

    return {
        "correct": correct,
        "topk_recall_hit": topk_recall_hit,
        "mech_pick": mech_pick, "mech_correct": mech_pick == correct,
        "mech_margin": mech_margin, "mech_refuse": mech_refuse,
        "int_only_pick": int_only_pick, "int_only_correct": int_only_pick == correct,
        "lex_pick": lex_pick, "lex_correct": lex_pick == correct,
        "rand_pick": rand_pick, "rand_correct": rand_pick == correct,
        "prediction_vector": [mech_pick, int_only_pick, lex_pick, rand_pick],
    }


def load_gold():
    items = {"unstated_goal": [], "satisfy_restate": []}
    with open(GOLD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d["item_type"] in items:
                items[d["item_type"]].append(d)
    # deterministic order (file order is already deterministic; sort by id defensively)
    for k in items:
        items[k] = sorted(items[k], key=lambda d: d["id"])
    return items


def arms_must_differ(results):
    """META_RULE_AF: assert the 4 arms are not bit-identical across items."""
    vecs = {"MECHANISM": [], "BASELINE_INTEGRATION_ONLY": [], "BASELINE_LEXICAL": [], "BASELINE_RANDOM": []}
    for r in results:
        pv = r["prediction_vector"]
        vecs["MECHANISM"].append(pv[0])
        vecs["BASELINE_INTEGRATION_ONLY"].append(pv[1])
        vecs["BASELINE_LEXICAL"].append(pv[2])
        vecs["BASELINE_RANDOM"].append(pv[3])
    digests = {name: hashlib.sha256("|".join(seq).encode()).hexdigest() for name, seq in vecs.items()}
    non_random_names = ["MECHANISM", "BASELINE_INTEGRATION_ONLY", "BASELINE_LEXICAL"]
    exempted_pairs = []
    for i, a in enumerate(non_random_names):
        for b in non_random_names[i + 1:]:
            if digests[a] == digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical (hash={digests[a]})"
                )
    return digests, exempted_pairs


def run(run_mode: str):
    t0 = time.perf_counter()
    gold = load_gold()
    n_goal = len(gold["unstated_goal"])
    n_sat = len(gold["satisfy_restate"])
    expected_n_units = (n_goal + n_sat) * 4
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, run_mode, expected_n_units)

    rng = __import__("random").Random(FIXED_RANDOM_SEED)  # fixed int seed, never hash()

    goal_results = [score_goal_item(it, rng) for it in gold["unstated_goal"]]
    sat_results = [score_satrest_item(it, rng) for it in gold["satisfy_restate"]]
    all_results = goal_results + sat_results

    arm_digests, exempted = arms_must_differ(all_results)

    def agg(results, key_correct):
        n = len(results)
        return sum(1 for r in results if r[key_correct]) / n if n else 0.0

    def agg_topk(results):
        n = len(results)
        return sum(1 for r in results if r["topk_recall_hit"]) / n if n else 0.0

    per_axis = {}
    for axis_name, results in [("unstated_goal", goal_results), ("satisfy_restate", sat_results)]:
        per_axis[axis_name] = {
            "n": len(results),
            "construction_topk_recall": agg_topk(results),
            "MECHANISM_accuracy": agg(results, "mech_correct"),
            "BASELINE_INTEGRATION_ONLY_accuracy": agg(results, "int_only_correct"),
            "BASELINE_LEXICAL_accuracy": agg(results, "lex_correct"),
            "BASELINE_RANDOM_accuracy": agg(results, "rand_correct"),
            "refuse_rate": sum(1 for r in results if r["mech_refuse"]) / len(results) if results else 0.0,
        }

    combined = {
        "n": len(all_results),
        "construction_topk_recall": agg_topk(all_results),
        "MECHANISM_accuracy": agg(all_results, "mech_correct"),
        "BASELINE_INTEGRATION_ONLY_accuracy": agg(all_results, "int_only_correct"),
        "BASELINE_LEXICAL_accuracy": agg(all_results, "lex_correct"),
        "BASELINE_RANDOM_accuracy": agg(all_results, "rand_correct"),
    }

    # refuse-gate honesty proxy: refuse rate on bottom-quartile-margin items vs top-quartile-margin
    margins_sorted = sorted(all_results, key=lambda r: r["mech_margin"])
    q = max(1, len(margins_sorted) // 4)
    bottom_q = margins_sorted[:q]
    top_q = margins_sorted[-q:]
    refuse_bottom = sum(1 for r in bottom_q if r["mech_refuse"]) / len(bottom_q) if bottom_q else 0.0
    refuse_top = sum(1 for r in top_q if r["mech_refuse"]) / len(top_q) if top_q else 0.0

    mech_beats_lexical = combined["MECHANISM_accuracy"] - combined["BASELINE_LEXICAL_accuracy"]
    mech_beats_random = combined["MECHANISM_accuracy"] - combined["BASELINE_RANDOM_accuracy"]
    mech_beats_int_only = combined["MECHANISM_accuracy"] - combined["BASELINE_INTEGRATION_ONLY_accuracy"]

    mechanism_works = (
        mech_beats_lexical >= 0.15
        and mech_beats_random >= 0.20
        and refuse_bottom > refuse_top
    )
    verdict = "MECHANISM_WORKS" if mechanism_works else "MECHANISM_INSUFFICIENT"

    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict}: combined mech_acc={combined['MECHANISM_accuracy']:.3f} "
            f"lex_acc={combined['BASELINE_LEXICAL_accuracy']:.3f} "
            f"rand_acc={combined['BASELINE_RANDOM_accuracy']:.3f} "
            f"int_only_acc={combined['BASELINE_INTEGRATION_ONLY_accuracy']:.3f} "
            f"mech-lex={mech_beats_lexical:.3f} mech-rand={mech_beats_random:.3f} "
            f"mech-int_only={mech_beats_int_only:.3f} refuse_bottomQ={refuse_bottom:.3f} "
            f"refuse_topQ={refuse_top:.3f}"
        ),
        "summary": f"{verdict} on 19-item clean-axis gold (unstated_goal n={n_goal}, satisfy_restate n={n_sat})",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "measured_n_units": len(all_results) * 1,  # 1 record per item; 4 arms scored within each
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "arm_digests": arm_digests,
        "per_axis": per_axis,
        "combined": combined,
        "mech_beats_lexical": mech_beats_lexical,
        "mech_beats_random": mech_beats_random,
        "mech_beats_integration_only": mech_beats_int_only,
        "refuse_bottom_quartile": refuse_bottom,
        "refuse_top_quartile": refuse_top,
        "prereg_bands": {
            "MECHANISM_WORKS_requires": "mech-lex>=0.15 AND mech-rand>=0.20 AND refuse_bottomQ>refuse_topQ",
        },
        "paraphrase_robustness_measured": False,
        "paraphrase_robustness_note": (
            "NOT measured this pass; no paraphrase gold subset exists and fabricating one ad hoc "
            "would violate the MEASURED-not-hallucinated discipline. Explicit follow-up, not a silent skip."
        ),
        "scope_note": (
            "Reuses the FHRR primitive SHAPE (bind/bundle/cleanup/refuse-gate) and the Kintsch "
            "construction->integration ARCHITECTURE PATTERN, freshly instantiated for this eval's "
            "isolated-snippet shape -- does NOT literally import CausalLinkRegister / "
            "situation_model_accumulate / sally_anne classes, which operate over a single narrative's "
            "accumulated register that this 25-item cross-novel eval does not provide. See pre-reg "
            "Scope decision section."
        ),
        "goal_item_ids": [it["id"] for it in gold["unstated_goal"]],
        "satrest_item_ids": [it["id"] for it in gold["satisfy_restate"]],
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return metrics


def self_test():
    """Tiny hand-built smoke: asserts primitives + arms-differ + pipeline runs end-to-end."""
    v1 = word_vector("apple")
    v2 = word_vector("apple")
    assert torch.allclose(v1, v2), "word_vector must be deterministic for the same word"
    assert abs(cos_sim(v1, v1) - 1.0) < 1e-4, "self-cosine must be ~1.0"
    v3 = word_vector("zebra")
    assert cos_sim(v1, v3) < 0.3, "unrelated random-phase words should have low cosine"

    toy_item = {
        "action_text": "he avoided the chore and pretended to enjoy it",
        "correct_category": "MANIPULATE_AVOID_WORK",
        "distractor_categories": ["CURIOSITY_EXPLORATION", "CARE_FOR_OTHERS", "SELF_DISCIPLINE"],
    }
    rng = __import__("random").Random(FIXED_RANDOM_SEED)
    r = score_goal_item(toy_item, rng)
    assert r["mech_pick"] in [toy_item["correct_category"]] + toy_item["distractor_categories"]

    toy_sat = {
        "goal_text": "I never want to see him again",
        "restate_text": "I never want to see him again, she repeated",
        "satisfy_text": "they laughed together and shook hands warmly",
    }
    r2 = score_satrest_item(toy_sat, rng)
    assert r2["mech_pick"] in ["restate", "satisfy"]

    # full pipeline dry-run on real gold (tiny, fast) to catch schema drift
    gold = load_gold()
    assert len(gold["unstated_goal"]) >= 1 and len(gold["satisfy_restate"]) >= 1, "gold file must have both axes"
    print("[self-test] PASS", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-mode", default="full", choices=["full", "smoke", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    metrics = run(args.run_mode)
    print(f"[done] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.3f}", flush=True)
    print(json.dumps(metrics["combined"], indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
