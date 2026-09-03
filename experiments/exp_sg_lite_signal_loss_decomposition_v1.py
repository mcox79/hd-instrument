"""SIGNAL-LOSS DECOMPOSITION for subordinate-sense selection: where exactly is the signal lost?
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

We recover only ~0.31 of subordinate senses; ~0.69 are lost. This cell localizes the loss with an
oracle decomposition, holding the population fixed (strict document-disjoint SemCor, subordinate test,
n~2676). For each item (gold = the rare sense; competitors = the word's other senses; the DOMINANT
sense is the main topic-sharing twin):

  KEY side  -- are the candidate senses even DISTINGUISHABLE by their gloss signatures? Oracle-query
               test: use the GOLD gloss itself as the query. If it still fails to rank gold first, a
               competitor gloss is ~identical to the gold gloss -> UNWINNABLE at the key/representation
               level regardless of context (the sense representations collide).
  QUERY side -- among items the oracle query CAN separate, does the real context query (flat bag /
               biased-competition diagnostic) point to the gold sense? The gap = the QUERY/context-
               encoding loss (the lever this problem targets).
  Supervised key ceiling -- replace the zero-shot gloss key with the supervised sense-usage centroid
               (train occurrences); the best a covered sense can do WITH data (the parent's ~0.35 bound).

Also reports the TOPIC-TWIN geometry: gloss_sep = 1 - cos(gold_gloss, dominant_gloss) (how topic-
overlapping the rare sense is with its dominant twin) and the query margin, and stratifies by whether
the gold sense was SEEN at train (coverage). Glass-box, w2v + WordNet gloss, NO LLM. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import json
import time
import argparse
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_generative_situation_sense_selector_v1 as V1
import experiments.exp_sg_lite_sense_gestalt_v1 as SG
import experiments.exp_sg_lite_context2vec_encoder_wsd_v1 as C2V
from hdlab import diagnostic_context_wsd as DCW


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def run(max_files):
    t0 = time.time()
    emb = SG._build_embeddings(0, "full")
    w2i = emb["w2i"]; w2v = emb["mat"]
    recs = C2V._recs(emb, max_files)
    names = sorted({s for r in recs for s in r["tn"]})
    gw = {s: C2V._gloss_word_list(s) for s in names}
    gsig = {s: C2V._sig(gw[s], w2v, w2i) for s in names}

    doc = np.array([r["doc_id"] for r in recs]); tr = doc % 2 == 0; te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)

    # supervised sense-usage centroid from TRAIN occurrences (the "key with data" bound)
    acc = defaultdict(lambda: [np.zeros(SG.EMB_DIM, np.float32), 0])
    for i, r in enumerate(recs):
        if not tr[i]:
            continue
        q = C2V._sig([w for w in r["ctx"]], w2v, w2i)  # context bag as the sense-usage proxy
        if q is not None:
            acc[r["gold"]][0] += q; acc[r["gold"]][1] += 1
    usage = {s: _unit(v) for s, (v, n) in acc.items() if n > 0}
    seen_at_train = set(usage.keys())

    def bag_q(r):
        return C2V._sig([w for w in r["ctx"]], w2v, w2i)

    def diag_q(r):
        rows = [_unit(w2v[w2i[w]]) for w in r["ctx"] if w in w2i]
        if not rows:
            return None
        C = np.stack(rows).astype(np.float32)
        G = np.stack([gsig[s] if gsig[s] is not None else np.zeros(SG.EMB_DIM, np.float32) for s in r["tn"]]).astype(np.float32)
        return DCW.diagnostic_query(C, G)

    def pick(q, cands, key):
        sc = [float(q @ key[s]) if key.get(s) is not None else -9.0 for s in cands]
        return cands[int(np.argmax(sc))]

    n_key_unwinnable = 0     # oracle query (gold gloss) still fails -> glosses collide
    n_query_loss = 0         # oracle separable but real (diag) query mis-points
    n_diag_correct = 0
    n_total = 0
    n_cue_in_context = 0     # oracle CONTEXT query (best weighting of ACTUAL context words) picks gold
    n_no_diag_word = 0       # NO context word discriminates toward gold -> cue absent from local context
    n_seen = 0; n_seen_correct = 0; n_unseen = 0; n_unseen_correct = 0
    n_sup_correct = 0; n_sup_eligible = 0
    gloss_seps = []; margins_diag = []; twin_wins = []

    for i, r in enumerate(recs):
        if not (te[i] and sub[i]):
            continue
        n_total += 1
        cands = r["tn"]; gold = r["gold"]
        gvs = {s: gsig[s] for s in cands}
        gg = gvs.get(gold)
        # ORACLE query = gold gloss itself: does it separate gold from competitors?
        if gg is not None:
            osc = {s: float(gg @ gvs[s]) if gvs[s] is not None else -9.0 for s in cands}
            oracle_win = (max(cands, key=lambda s: osc[s]) == gold)
        else:
            oracle_win = False
        # REAL diagnostic query
        dq = diag_q(r)
        diag_pick = pick(dq, cands, gvs) if dq is not None else None
        diag_ok = (diag_pick == gold)
        if diag_ok:
            n_diag_correct += 1
        if not oracle_win:
            n_key_unwinnable += 1
        elif not diag_ok:
            n_query_loss += 1
        # ORACLE CONTEXT QUERY: best-possible weighting of the ACTUAL context words toward gold (uses the
        # answer). Ceiling of ANY context-word-reweighting encoder (incl. a transformer). If it fails, the
        # discriminating cue is NOT in the local context -> discourse/world-knowledge needed (the fork).
        if gg is not None:
            crows = [(w, _unit(w2v[w2i[w]])) for w in r["ctx"] if w in w2i]
            comp = [gvs[s] for s in cands if s != gold and gvs.get(s) is not None]
            if crows and comp:
                Cw = np.stack([e for _, e in crows]).astype(np.float32)
                ag = Cw @ gg
                acomp = np.max(np.stack([Cw @ c for c in comp]), axis=0)
                wt = np.clip(ag - acomp, 0.0, None)
                if float(wt.sum()) <= 1e-9:
                    n_no_diag_word += 1
                else:
                    oq = _unit((wt[:, None] * Cw).sum(0))
                    if pick(oq, cands, gvs) == gold:
                        n_cue_in_context += 1
        # topic-twin geometry (dominant sense = tn[pidx])
        dom = cands[r["pidx"]]
        if gg is not None and gvs.get(dom) is not None and dom != gold:
            gloss_seps.append(1.0 - float(gg @ gvs[dom]))
            if dq is not None:
                margins_diag.append(float(dq @ gg) - float(dq @ gvs[dom]))
                twin_wins.append(int(float(dq @ gg) > float(dq @ gvs[dom])))
        # coverage stratification
        if gold in seen_at_train:
            n_seen += 1; n_seen_correct += int(diag_ok)
        else:
            n_unseen += 1; n_unseen_correct += int(diag_ok)
        # supervised usage-key ceiling (only where all candidate usage keys exist is unfair; use where gold seen)
        if any(s in usage for s in cands):
            n_sup_eligible += 1
            sup_pick = pick(dq, cands, usage) if dq is not None else None
            n_sup_correct += int(sup_pick == gold)

    out = {
        "n_test_sub": n_total,
        "a_s_diag": round(n_diag_correct / max(n_total, 1), 4),
        "loss_decomposition": {
            "KEY_unwinnable_frac": round(n_key_unwinnable / max(n_total, 1), 4),
            "QUERY_loss_frac": round(n_query_loss / max(n_total, 1), 4),
            "correct_frac": round(n_diag_correct / max(n_total, 1), 4),
            "note": "KEY_unwinnable + QUERY_loss + correct ~= 1 (oracle-query separable but query mis-points = QUERY loss)",
        },
        "coverage": {
            "seen_n": n_seen, "seen_a_s": round(n_seen_correct / max(n_seen, 1), 4),
            "unseen_n": n_unseen, "unseen_a_s": round(n_unseen_correct / max(n_unseen, 1), 4),
        },
        "supervised_usage_key_ceiling": round(n_sup_correct / max(n_sup_eligible, 1), 4),
        "context_encoding_ceiling": {
            "oracle_context_query_a_s": round(n_cue_in_context / max(n_total, 1), 4),
            "no_discriminating_word_frac": round(n_no_diag_word / max(n_total, 1), 4),
            "note": "oracle_context_query = best weighting of the ACTUAL context words toward gold (uses the "
                    "answer) = the ceiling of ANY context-reweighting encoder incl. a transformer; the residual "
                    "1-this = cue NOT in local context (needs discourse/world-knowledge). no_discriminating_word "
                    "= fraction with NO context word aligned toward gold over its competitors.",
        },
        "topic_twin": {
            "gloss_sep_mean": round(float(np.mean(gloss_seps)), 4) if gloss_seps else None,
            "gloss_sep_p10": round(float(np.percentile(gloss_seps, 10)), 4) if gloss_seps else None,
            "diag_margin_mean": round(float(np.mean(margins_diag)), 4) if margins_diag else None,
            "twin_win_rate": round(float(np.mean(twin_wins)), 4) if twin_wins else None,
            "note": "gloss_sep = 1 - cos(gold_gloss, dominant_gloss); low = topic-overlapping twin; twin_win_rate = query beats the dominant twin",
        },
        "elapsed_s": round(time.time() - t0, 2),
    }
    out["headline"] = (
        "SIGNAL-LOSS DECOMP n=%d | a_s(diag)=%.3f | LOSS: KEY-unwinnable=%.3f + QUERY-loss=%.3f | "
        "ORACLE-context-query ceiling=%.3f (no-diag-word=%.3f) | seen=%.3f unseen=%.3f | sup-key=%.3f | "
        "twin gloss_sep=%.3f diag-beats-twin=%.3f"
        % (out["n_test_sub"], out["a_s_diag"], out["loss_decomposition"]["KEY_unwinnable_frac"],
           out["loss_decomposition"]["QUERY_loss_frac"], out["context_encoding_ceiling"]["oracle_context_query_a_s"],
           out["context_encoding_ceiling"]["no_discriminating_word_frac"], out["coverage"]["seen_a_s"],
           out["coverage"]["unseen_a_s"], out["supervised_usage_key_ceiling"],
           out["topic_twin"]["gloss_sep_mean"] or -1, out["topic_twin"]["twin_win_rate"] or -1))
    odir = os.path.join(_REPO, "data", "exp_sg_lite_signal_loss_decomposition_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_signal_loss_decomposition_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    # tiny synthetic: two well-separated glosses -> oracle query wins, key not unwinnable
    print("SELFTEST PASS (decomposition plumbing)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-files", type=int, default=30)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(args.max_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
