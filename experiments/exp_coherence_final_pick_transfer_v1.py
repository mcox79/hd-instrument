"""exp_coherence_final_pick_transfer_v1 -- DOES THE F5 COHERENCE SIGNAL IMPROVE THE FINAL PICK ON
THE REAL C3 OPEN-VOCABULARY READ-OUT?

PRE-REG: preregs/2026-08-15_coherence_final_pick_transfer_v1.md, committed before this cell ran.

WHY: exp_pun_coherence_alarm_viability_probe_v1 HARD_PASS'd a selectional-fit coherence channel
(verb-selectional required-features vs candidate-sense-features, HD schema-fit similarity) that
separates a dominant-WRONG reading from correct at 0.9849 with a scramble collapsing to -0.0073.
The organs-missing-batch audit ranked this the #1 candidate mechanism for our actual defect
(retrieval healthy: gold in top-50 for 55.65% of C3 items vs 54.55% for a trigram-only spell-
checker; final pick given containment: 8.6% for us vs 16.0% for the trigram arm -- same
neighbourhood, worse pick). This cell asks whether the SAME mechanism, reused unmodified, moves
the needle on the real, open-vocabulary read-out, not just on its own curated pun items.

TWO FLOORED NEGATIVES IN THE SAME ORGAN FAMILY ARE ON DISK AND ARE THE PRIOR AGAINST THIS CELL
(see pre-reg): exp_read_discourse_wsm_running_vs_static_coherence_v1 (HARD_FAIL, running-state
coherence loses to static on real text) and exp_coherence_selector_text_transfer_v1
(CANNOT_BRIDGE_REPRESENTATION_GAP, below-random on real text). Neither used this exact mechanism;
both used a mechanism in the same family and both failed on real text after passing on a
controlled/sim construction.

NOTHING UNDER hdlab/ IS MODIFIED. ConceptSpace, context_vector_masked, canonicalize_fast, and the
item construction are exp_grounding_readout_known_answer_v1's own functions, imported and called
unmodified. The coherence primitives (verb_required_features, sense_feature_set, build_atoms,
schema_recovered_target, coherence) are exp_pun_coherence_alarm_viability_probe_v1's own functions,
imported and called unmodified. The ONE new piece of code is governing-verb extraction (POS-tag
the item's held-out sentence, take the nearest VB* token to the target lemma, WordNet-lemmatize to
a verb lemma) -- the pun probe hand-curated its verb per item; C3 items have no curated verb.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - arms-must-differ: sha256 over each arm's correctness vector
# - A1_BASE integrity check: must reproduce 0.0480 to 1e-9 or STOP
# - positive control SELF_RETRIEVAL >= 0.70 or VOID_PLUMBING
ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import nltk                                                                    # noqa: E402
from nltk.stem import WordNetLemmatizer                                        # noqa: E402

from hdlab.reading_grounding_loop import normalize_lemma                       # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3                 # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS                      # noqa: E402
from experiments.exp_pun_coherence_alarm_viability_probe_v1 import (           # noqa: E402
    N_DIM as COH_N_DIM, build_atoms, coherence, dominant_synset_name,
    schema_recovered_target, sense_feature_set, verb_required_features,
)

ANCHOR_NAME = "exp_coherence_final_pick_transfer_v1"
PREREG_PATH = "preregs/2026-08-15_coherence_final_pick_transfer_v1.md"
MASTER_SEED = 20260815
N_BOOT = 5000
DRAW_SEEDS = [20260815, 71, 137, 20260101, 999983]
COH_BAR = 0.0870          # standalone orthographic floor, CI [0.0783, 0.0960]
TOPK = 50

_LEMM = WordNetLemmatizer()


def _out_dir(run_mode: str) -> str:
    suffix = "" if run_mode == "full" else "_" + run_mode.upper()
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix)


def _atomic_json(path: str, obj: object) -> None:
    with open(path + ".tmp", "wb") as fh:
        fh.write(json.dumps(obj, indent=1).encode("utf-8"))
    os.replace(path + ".tmp", path)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(v.tobytes()).hexdigest()[:16]


# ------------------------------------------------------------------ governing-verb extraction
def governing_verb_lemma(sentence: str, target: str) -> Optional[str]:
    """Nearest VB* token to `target`'s occurrence in `sentence` (case-insens., normalized-lemma
    match), WordNet-lemmatized to a verb base form. None if no verb token exists at all. This is
    a cheap POS-tag heuristic, NOT a dependency parse -- the item construction has no syntactic
    structure available (context_vector_masked is a bag-of-content-words, see
    hdlab/reading_grounding_loop.py:255-283 STRUCTURED COMPARATOR note: the UD front-end exists
    but is DEFAULT-OFF and a separate live experiment currently owns
    data/exp_structured_code_vs_flat_bag_c3_v1* / data/exp_structured_comparator_v1/probes/,
    both READ-ONLY for this cell)."""
    try:
        toks = nltk.word_tokenize(sentence)
    except Exception:
        toks = sentence.split()
    if not toks:
        return None
    tags = nltk.pos_tag(toks)
    tgt_idx = None
    for i, (w, _t) in enumerate(tags):
        if normalize_lemma(w) == target:
            tgt_idx = i
            break
    verb_idxs = [i for i, (_w, t) in enumerate(tags) if t.startswith("VB")]
    if not verb_idxs:
        return None
    if tgt_idx is None:
        vi = verb_idxs[0]
    else:
        vi = min(verb_idxs, key=lambda i: abs(i - tgt_idx))
    surf = tags[vi][0].lower()
    try:
        return _LEMM.lemmatize(surf, "v")
    except Exception:
        return surf


# ------------------------------------------------------------------ coherence precompute
def build_sense_bank(anchors: List[str], atoms: dict) -> torch.Tensor:
    """Sense-feature bundle vector per anchor, computed ONCE (depends only on the word, not the
    item) -- [n_anchors, N_DIM] complex64. Reuses sense_feature_set/dominant_synset_name/bundle
    from the pun probe verbatim."""
    from experiments.exp_pun_coherence_alarm_viability_probe_v1 import bundle as _bundle
    rows = []
    for a in anchors:
        dom = dominant_synset_name(a)
        feats = sense_feature_set(dom) if dom is not None else frozenset()
        rows.append(_bundle(sorted(feats) if feats else ["_UNK"], atoms))
    return torch.stack(rows, dim=0)


def coherence_scores_batch(recovered: torch.Tensor, sense_mat: torch.Tensor) -> np.ndarray:
    """Vectorized coherence() over a batch of candidates: real cosine of `recovered` against each
    row of `sense_mat`. Same math as coherence()/A.similarity, batched."""
    num = torch.real(sense_mat @ torch.conj(recovered))
    den = torch.clamp(
        torch.sqrt(torch.real(torch.sum(sense_mat * torch.conj(sense_mat), dim=1)))
        * torch.sqrt(torch.real(torch.sum(recovered * torch.conj(recovered)))), min=1e-8)
    return (num / den).cpu().numpy()


# ------------------------------------------------------------------ main scoring pass
def score_pass(items, sents, space, anchors, mat, mat_nrm, pos, norm2idx, t_mat, t_cov,
              n_anchors, atoms, sense_mat, donors, use_scrambled_context: bool,
              verb_cache: Dict[int, Optional[str]]) -> dict:
    n = len(items)
    anchor_arr = np.array(anchors)
    hits = {a: np.zeros(n, dtype=bool) for a in
            ("A1_BASE", "A6_TRIGRAM_ONLY", "RERANK_COH", "RANDOM_TOP50", "SCRAMBLE_CONTEXT_COH")}
    picks = defaultdict(list)
    coverage = np.zeros(n, dtype=bool)
    rerank_changed = np.zeros(n, dtype=bool)
    rng = np.random.default_rng(MASTER_SEED + 11)

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        elig &= mat_nrm >= 1e-9
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        gold = C3.gold_meaning_set(L)

        q = space.bundle(L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        base = (mat[sel] @ q) / (mat_nrm[sel] * qn)

        b_arg = int(np.argmax(base))
        p_base = str(anchor_arr[sel[b_arg]])
        picks["A1_BASE"].append(p_base)
        hits["A1_BASE"][i] = p_base in gold

        tq = t_mat[pos[L]] if t_cov[pos[L]] else None
        trig = t_mat[sel] @ tq if tq is not None else np.zeros(sel.size)
        t_arg = int(np.argmax(trig))
        p_trig = str(anchor_arr[sel[t_arg]])
        picks["A6_TRIGRAM_ONLY"].append(p_trig)
        hits["A6_TRIGRAM_ONLY"][i] = p_trig in gold

        order = np.argsort(-base)
        top_local = order[:min(TOPK, sel.size)]
        top_glob = sel[top_local]

        r_arg_local = int(np.random.default_rng(MASTER_SEED + 31 + i).integers(len(top_local)))
        p_rand = str(anchor_arr[top_glob[r_arg_local]])
        picks["RANDOM_TOP50"].append(p_rand)
        hits["RANDOM_TOP50"][i] = p_rand in gold

        # governing verb + coherence, from either the item's OWN held-out sentence or the
        # derangement DONOR's (scramble-context control)
        src_it = items[donors[i]] if use_scrambled_context else it
        if it["sent_idx"] is None or src_it["sent_idx"] is None:
            verb = None
        else:
            cache_key = (src_it["item_id"], "scr" if use_scrambled_context else "real")
            if cache_key in verb_cache:
                verb = verb_cache[cache_key]
            else:
                sent = sents[src_it["sent_idx"]]
                verb = governing_verb_lemma(sent, src_it["L"] if use_scrambled_context else L)
                verb_cache[cache_key] = verb
        req_feats = verb_required_features(verb) if verb else []

        if req_feats:
            coverage[i] = True
            recovered = schema_recovered_target(req_feats, atoms)
            coh_top = coherence_scores_batch(recovered, sense_mat[top_glob])
            base_top = base[top_local]
            combined = MS._z(base_top) + MS._z(coh_top)
            c_arg_local = int(np.argmax(combined))
            p_coh = str(anchor_arr[top_glob[c_arg_local]])
            rerank_changed[i] = (top_glob[c_arg_local] != sel[b_arg])
        else:
            p_coh = p_base
        key = "RERANK_COH" if not use_scrambled_context else "SCRAMBLE_CONTEXT_COH"
        picks[key].append(p_coh)
        hits[key][i] = p_coh in gold
        # the OTHER key (RERANK_COH on the scrambled-context pass, or vice versa) stays at its
        # zero-init in this pass; the caller (run()) reassembles the final hits dict by taking
        # RERANK_COH only from the real-context pass and SCRAMBLE_CONTEXT_COH only from the
        # scrambled-context pass, so the unfilled key here is never read.

        if (i + 1) % 500 == 0 or i == n - 1:
            print("[score %s] %d/%d elapsed" % ("scr" if use_scrambled_context else "real",
                                                 i + 1, n), flush=True)

    return {"hits": hits, "picks": picks, "coverage": coverage, "rerank_changed": rerank_changed}


def run(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    sents = C3.build_corpus(run_mode)
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, output_dir)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    items, item_diag = C3.build_items(space, buckets, counts, C3.MAX_ITEMS)
    n = len(items)
    print("[items] n=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0), flush=True)
    if n < C3.MIN_ITEMS and run_mode == "full":
        return {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "n_items": n}

    mat_nrm = np.linalg.norm(mat, axis=1)
    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    t_mat, t_cov = MS.trigram_matrix(anchors)

    donors = C3._derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                                  & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)

    # ---- SELF_RETRIEVAL positive control (reused construction from the parent cell)
    rng_sr = np.random.default_rng(C3.MASTER_SEED + 9)
    sr_hits, sr_n = 0, 0
    for it in items[:min(300, n)]:
        L = it["L"]
        if it["sent_idx"] is None:
            continue
        other = anchors[int(rng_sr.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or C3._is_variant(other, L)):
            other = anchors[int(rng_sr.integers(len(anchors)))]
            tries += 1
        if other == L:
            continue
        q = C3.context_vector_masked(sents[it["sent_idx"]], L)
        if float(np.linalg.norm(q)) < 1e-9:
            continue
        mask2 = np.zeros(n_anchors, dtype=bool)
        mask2[pos[L]] = True
        mask2[pos[other]] = True
        pick, _c = C3.canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=mask2)
        sr_hits += int(pick == L)
        sr_n += 1
    self_retrieval = round(sr_hits / max(1, sr_n), 6)
    print("[self-retrieval] %.4f n=%d" % (self_retrieval, sr_n), flush=True)
    if sr_n < 30 or self_retrieval < C3.SELF_RETRIEVAL_FLOOR:
        return {"verdict": "VOID_PLUMBING", "self_retrieval": self_retrieval, "sr_n": sr_n,
                "notes": ["positive control below floor -- no quality claim either way"]}

    # ---- coherence atoms + sense bank (built ONCE per draw seed)
    def build_for_seed(seed: int):
        gen = torch.Generator().manual_seed(seed)
        atoms = build_atoms(gen)
        sense_mat = build_sense_bank(list(anchors), atoms)
        return atoms, sense_mat

    verb_cache: Dict = {}
    atoms0, sense_mat0 = build_for_seed(MASTER_SEED)

    real_pass = score_pass(items, sents, space, anchors, mat, mat_nrm, pos, norm2idx, t_mat, t_cov,
                           n_anchors, atoms0, sense_mat0, donors, False, verb_cache)
    scr_pass = score_pass(items, sents, space, anchors, mat, mat_nrm, pos, norm2idx, t_mat, t_cov,
                          n_anchors, atoms0, sense_mat0, donors, True, verb_cache)

    hits = {
        "A1_BASE": real_pass["hits"]["A1_BASE"],
        "A6_TRIGRAM_ONLY": real_pass["hits"]["A6_TRIGRAM_ONLY"],
        "RANDOM_TOP50": real_pass["hits"]["RANDOM_TOP50"],
        "RERANK_COH": real_pass["hits"]["RERANK_COH"],
        "SCRAMBLE_CONTEXT_COH": scr_pass["hits"]["SCRAMBLE_CONTEXT_COH"],
    }
    picks = {
        "A1_BASE": real_pass["picks"]["A1_BASE"],
        "A6_TRIGRAM_ONLY": real_pass["picks"]["A6_TRIGRAM_ONLY"],
        "RANDOM_TOP50": real_pass["picks"]["RANDOM_TOP50"],
        "RERANK_COH": real_pass["picks"]["RERANK_COH"],
        "SCRAMBLE_CONTEXT_COH": scr_pass["picks"]["SCRAMBLE_CONTEXT_COH"],
    }
    coverage_real = real_pass["coverage"]
    coverage_scr = scr_pass["coverage"]
    rerank_changed = real_pass["rerank_changed"]

    a1_acc = float(hits["A1_BASE"].mean())
    integrity_ok = (abs(a1_acc - 0.048) < 1e-9) if run_mode == "full" else True
    print("[integrity] A1_BASE=%.10f target=0.0480000000 (checked only in full mode) ok=%s"
          % (a1_acc, integrity_ok), flush=True)

    arms = list(hits)
    armv = {a: hits[a].astype(float) for a in arms}
    digests = {a: _digest(armv[a]) for a in arms}
    dupes = [k for k in sorted(digests) if sorted(digests.values()).count(digests[k]) > 1]
    deltas = [("d_RERANK_minus_BASE", "RERANK_COH", "A1_BASE"),
              ("d_RERANK_minus_TRIGRAM", "RERANK_COH", "A6_TRIGRAM_ONLY"),
              ("d_RERANK_minus_RANDOM50", "RERANK_COH", "RANDOM_TOP50"),
              ("d_RERANK_minus_SCRAMBLECTX", "RERANK_COH", "SCRAMBLE_CONTEXT_COH")]
    bs = MS.paired_bootstrap(armv, deltas, N_BOOT, MASTER_SEED + 5)

    # ---- BETWEEN-DRAW SPREAD: rerun RERANK_COH across independent atom-vector seeds
    draw_accs = []
    for sd in DRAW_SEEDS:
        atoms_s, sense_mat_s = build_for_seed(sd)
        p = score_pass(items, sents, space, anchors, mat, mat_nrm, pos, norm2idx, t_mat, t_cov,
                       n_anchors, atoms_s, sense_mat_s, donors, False, verb_cache)
        draw_accs.append(float(p["hits"]["RERANK_COH"].mean()))
    draw_sd = float(np.std(draw_accs))
    print("[draw-spread] accs=%s sd=%.5f" % ([round(x, 5) for x in draw_accs], draw_sd), flush=True)

    cov_real_rate = float(coverage_real.mean())
    cov_scr_rate = float(coverage_scr.mean())
    n_changed = int(rerank_changed.sum())
    n_changed_correct = int((rerank_changed & hits["RERANK_COH"]).sum())
    n_changed_base_correct = int((rerank_changed & hits["A1_BASE"]).sum())

    rerank_ci = bs["arm_acc_ci"]["RERANK_COH"]
    floor_uppers = [bs["arm_acc_ci"]["A1_BASE"]["ci_hi"], bs["arm_acc_ci"]["A6_TRIGRAM_ONLY"]["ci_hi"],
                    bs["arm_acc_ci"]["RANDOM_TOP50"]["ci_hi"], bs["arm_acc_ci"]["SCRAMBLE_CONTEXT_COH"]["ci_hi"]]
    ci_separated_above_all_floors = rerank_ci["ci_lo"] > max(floor_uppers)
    ci_separated_above_bar = rerank_ci["ci_lo"] > COH_BAR
    scramble_overlaps_rerank = not (
        bs["arm_acc_ci"]["SCRAMBLE_CONTEXT_COH"]["ci_hi"] < rerank_ci["ci_lo"]
        or bs["arm_acc_ci"]["SCRAMBLE_CONTEXT_COH"]["ci_lo"] > rerank_ci["ci_hi"])
    gain_over_base = bs["deltas"]["d_RERANK_minus_BASE"]["delta"]
    within_draw_noise = abs(gain_over_base) < 3 * draw_sd

    if cov_real_rate < 0.10:
        verdict = "INAPPLICABLE_LOW_COVERAGE"
    elif not integrity_ok:
        verdict = "INTEGRITY_CHECK_FAILED"
    elif ci_separated_above_all_floors and ci_separated_above_bar and not scramble_overlaps_rerank and not within_draw_noise:
        verdict = "TRANSFERS"
    else:
        verdict = "DOES_NOT_TRANSFER"

    notes = [
        "A1_BASE=%.6f (target 0.048, integrity_ok=%s)" % (a1_acc, integrity_ok),
        "RERANK_COH=%.4f CI=[%.4f,%.4f] vs bar=%.4f" % (rerank_ci["acc"], rerank_ci["ci_lo"],
                                                        rerank_ci["ci_hi"], COH_BAR),
        "A6_TRIGRAM_ONLY=%.4f RANDOM_TOP50=%.4f SCRAMBLE_CONTEXT_COH=%.4f" % (
            bs["arm_acc_ci"]["A6_TRIGRAM_ONLY"]["acc"], bs["arm_acc_ci"]["RANDOM_TOP50"]["acc"],
            bs["arm_acc_ci"]["SCRAMBLE_CONTEXT_COH"]["acc"]),
        "coverage_real=%.4f coverage_scrambled=%.4f (fraction of items with a VerbNet-covered "
        "governing verb, i.e. coherence-eligible at all)" % (cov_real_rate, cov_scr_rate),
        "rerank_changed_the_pick=%d/%d; of those, RERANK correct=%d, BASE was already correct=%d"
        % (n_changed, n, n_changed_correct, n_changed_base_correct),
        "between_draw_spread_sd=%.5f (accs=%s)" % (draw_sd, [round(x, 5) for x in draw_accs]),
        "gain_over_base=%.5f within_3x_draw_noise=%s" % (gain_over_base, within_draw_noise),
        "ci_separated_above_all_floors=%s ci_separated_above_bar=%s scramble_overlaps_rerank_ci=%s"
        % (ci_separated_above_all_floors, ci_separated_above_bar, scramble_overlaps_rerank),
    ]

    out = {
        "verdict": verdict, "notes": notes, "n_items": n, "item_construction": item_diag,
        "prereg": PREREG_PATH,
        "self_retrieval": {"acc": self_retrieval, "n": sr_n, "floor": C3.SELF_RETRIEVAL_FLOOR},
        "integrity": {"a1_base_acc": a1_acc, "target": 0.048, "ok": integrity_ok},
        "bootstrap": bs,
        "coverage": {"real": cov_real_rate, "scrambled": cov_scr_rate,
                    "n_real_eligible": int(coverage_real.sum())},
        "mechanism_breakdown": {"n_changed_pick": n_changed, "n_changed_and_correct": n_changed_correct,
                               "n_changed_but_base_was_correct": n_changed_base_correct},
        "between_draw_spread": {"seeds": DRAW_SEEDS, "accs": draw_accs, "sd": draw_sd},
        "coherence_bar": COH_BAR,
        "arm_digests": digests, "arms_bit_identical": dupes,
        "per_arm_example_picks": {a: picks[a][:15] for a in arms},
        "elapsed_s": round(time.time() - t0, 2),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    args = ap.parse_args()
    run_mode = args.mode
    output_dir = _out_dir(run_mode)
    os.makedirs(output_dir, exist_ok=True)
    if run_mode == "smoke":
        C3.MAX_ITEMS = 120
        MS  # keep import used
    try:
        result = run(run_mode, output_dir)
        result["ts_iso"] = datetime.now(timezone.utc).isoformat()
        result["anchor_name"] = ANCHOR_NAME
        result["run_mode"] = run_mode
        _atomic_json(os.path.join(output_dir, "metrics.json"), result)
        print("VERDICT", result.get("verdict"), flush=True)
        print("WROTE", os.path.join(output_dir, "metrics.json"), flush=True)
        return 0
    except SystemExit:
        raise
    except Exception as exc:
        crash = {"verdict": "CRASH", "error": str(exc), "traceback": traceback.format_exc(),
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                 "run_mode": run_mode}
        _atomic_json(os.path.join(output_dir, "metrics.json"), crash)
        print("CRASHED", exc, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
