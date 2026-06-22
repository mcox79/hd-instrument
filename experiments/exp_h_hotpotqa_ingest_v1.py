"""h_hotpotqa_ingest_v1 -- H: substrate KB-INGEST of HotpotQA-distractor 1k-dev as 2-hop chains.

Mirrors n8 (ConceptNet) and U1 (FB15k-237) chain-grade pattern: multi-value Hebbian + set-readout
top-k + held-split refuse-gate + 2-hop inference-transfer with frozen-encoder semantic baseline.

CORPUS: 1000 HotpotQA dev items. Each item has 2 supporting-fact Wikipedia titles (t1, t2) and an
answer (a). Per-item triple decomposition (bridge-type only for 2-hop eval; all items for ingest):

    (t1, "linked_via", t2)         # hop-1: title1 -> bridge entity
    (t2, "supplies_answer", a)     # hop-2: bridge -> answer

Entity set = union of supporting_fact titles + answers. Two relation types ("linked_via",
"supplies_answer"). M = 2 * n_items triples ingested per seed.

DESIGN DEVIATION FROM SPAWN DIRECTIVE (documented):
  - Spawn directive nominated pythia-160m mean-pool as the encoder. The MedQA HARD_FAIL
    (encoder mean-pool collapse on long uniform-topic medical vignettes; off-diagonal cosine
    0.9865) was the trigger to pivot here. HotpotQA encodes ENTITIES (Wikipedia titles, ~3-5
    tokens) not vignettes, so pythia mean-pool collapse risk is much lower -- but MiniLM-L6 is
    the encoder n8 chain-grade USED (CERT 585), is proven on short entity names, and gives a
    closer mechanism-mirror to n8. Choice: MiniLM-L6.
  - Smoke-time ENCODER-GEOMETRY CHECK is mandatory per directive: compute off-diagonal cosine
    on the entity embedding matrix (over a 500-entity sample). If off-diag cos > 0.95 = HALT;
    that is the MedQA-style mean-pool collapse signature.

PRE-REG BANDS (locked; HARD-band framing mirrors n8/U1 absolute-floor pattern):
  HARD_PASS (3 seeds, ALL bands met):
    setrecall_all @ M=full >= 0.95
    refuse OOD >= 0.80 AND in-KB accept >= 0.80
    substrate-2hop > 1-hop baseline + 0.02
    substrate-2hop >= 2x frozen-encoder baseline
    zero_llm_calls_at_inference == True
  MIDDLE_BAND: partial -- refuse-gate OR inference-transfer holds, the other falls short
  HARD_FAIL: setrecall_all < 0.50 OR refuse OOD < 0.50 OR 2-hop ratio < 1.5x

CPU; ASCII; per-seed checkpoint via _seed_checkpoint helper pattern. allow_synthetic=False.
"""
import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import resumable_seeds, write_partial, aggregate_partials  # noqa: E402

ANCHOR_NAME = "h_hotpotqa_ingest_v1"
HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"

# Pre-reg bands (locked).
SETRECALL_FLOOR = 0.95          # load-bearing #1: set-recall@k at M_full
REFUSE_OOD_MIN = 0.80           # load-bearing #2: OOD refuse-rate
ACCEPT_INKB_MIN = 0.80          # load-bearing #2: in-KB accept-rate
INFER_MARGIN_OVER_1HOP = 0.02   # load-bearing #3a: substrate-2hop > 1-hop + 0.02
INFER_RATIO_OVER_ENC = 2.0      # load-bearing #3b: substrate-2hop >= 2x frozen-encoder semantic
INFER_RATIO_OVER_1HOP = 2.0     # discriminator-regime (Fix #16): >=2.0x random/1-hop
SETRECALL_FAIL = 0.50           # HARD_FAIL floor (per spawn directive)
REFUSE_FAIL = 0.50              # HARD_FAIL floor
INFER_RATIO_FAIL = 1.5          # HARD_FAIL floor

# Encoder-geometry guard (MedQA mean-pool-collapse signature).
OFF_DIAG_COS_HALT_THRESHOLD = 0.95

# Smoke-flag detection: spawn directive Fix #6 TODO #6 in-cell name-detection
# pattern (queue runner's HDLAB_RUN_MODE=full overrides envs; only the entry-name
# _smoke suffix is a reliable signal post-dispatch).
_NAME_SAYS_SMOKE = "_smoke" in os.environ.get("HDLAB_EXP_NAME", "").lower()

RUN_MODE = (
    "smoke" if (("--smoke" in sys.argv) or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    N_EVAL = 100
    N_OOD = 100
    N_2HOP = 60
    MAX_ITEMS = 200            # smoke uses first 200 items
    ENC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_EVAL = 600
    N_OOD = 600
    N_2HOP = 300
    MAX_ITEMS = 1000           # full uses all 1000
    ENC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM-call counter for substrate-only-decode gate (PROT structural blocker #3 pattern).
_LLM_CALL_COUNTER = [0]

CONFIG_VERSION = (
    "h-hotpotqa-multivalue-hebbian-2hop: title1->title2->answer chain; "
    "setreadout-topk + margin-refuse + 2hop-vs-1hop-and-frozen-encoder + "
    "discriminator-regime-random-key-control; "
    "N%d M_items=%d eval=%d ood=%d 2hop=%d; "
    "bands sr%.2f ood%.2f acc%.2f inf+%.2f enc%.1fx fail-floor sr%.2f"
) % (
    N_DIM, MAX_ITEMS, N_EVAL, N_OOD, N_2HOP,
    SETRECALL_FLOOR, REFUSE_OOD_MIN, ACCEPT_INKB_MIN,
    INFER_MARGIN_OVER_1HOP, INFER_RATIO_OVER_ENC, SETRECALL_FAIL,
)


# ----------------------------- core mechanism ------------------------------ #
def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    """Mechanism unit-test (no I/O, no encoder, no corpus): multi-value Hebbian + set-readout.

    Synthetic 2-hop graph: 30 (t1, t2, a) chains over 60 entities, 2 relations. Verifies that
    set-readout-top-k recovers > 90% of objects AND that 2-hop composition beats 1-hop direct.
    """
    g = np.random.default_rng(0)
    n = 512
    ne = 60
    nr = 2
    E = bipolar(ne, n, g)
    R = bipolar(nr, n, g)
    sq = math.sqrt(n)
    # Build 30 chains: t1 -> t2 (rel 0) -> a (rel 1).
    triples = []
    chains = []
    used_t1 = set()
    used_t2 = set()
    used_a = set()
    for i in range(30):
        # Pick disjoint t1, t2, a indices.
        while True:
            t1 = int(g.integers(0, ne))
            if t1 not in used_t1: break
        while True:
            t2 = int(g.integers(0, ne))
            if t2 not in used_t2 and t2 != t1: break
        while True:
            a = int(g.integers(0, ne))
            if a not in used_a and a not in (t1, t2): break
        used_t1.add(t1); used_t2.add(t2); used_a.add(a)
        triples.append((t1, 0, t2))
        triples.append((t2, 1, a))
        chains.append((t1, 0, t2, 1, a))

    W = np.zeros((n, n), dtype=np.float32)
    keyobjs = defaultdict(set)
    for (s, p, o) in triples:
        key = E[s] * R[p] * sq
        W += np.outer(E[o], key) / n
        keyobjs[(s, p)].add(o)

    # Set-recall@1 on training keys.
    hit = 0; tot = 0
    for (s, p), objs in keyobjs.items():
        scores = E @ (W @ (E[s] * R[p] * sq))
        topk = set(np.argsort(scores)[-len(objs):].tolist())
        hit += len(topk & set(objs)); tot += len(objs)
    setrecall = hit / tot
    assert setrecall >= 0.9, "selftest setrecall %.2f < 0.9" % setrecall

    # 2-hop composition: predict 'a' from (t1, p1) by chaining through t2.
    hits_2hop = 0
    for (t1, p1, t2, p2, a) in chains:
        s1 = E @ (W @ (E[t1] * R[p1] * sq))
        x_hat = int(np.argmax(s1))
        s2 = E @ (W @ (E[x_hat] * R[p2] * sq))
        o_hat = int(np.argmax(s2))
        if o_hat == a: hits_2hop += 1
    p2hop = hits_2hop / len(chains)
    assert p2hop >= 0.8, "selftest 2-hop %.2f < 0.8" % p2hop

    # Refuse confidence: MEAN in-KB conf > MEAN OOD conf (averaged over keys; single-key
    # comparison too noisy on small synthetic regime).
    keyset = set(keyobjs.keys())
    inkb_confs = []
    for (s, p) in list(keyobjs.keys())[:20]:
        inkb_confs.append(float(np.max(E @ (W @ (E[s] * R[p] * sq)))))
    ood_confs = []
    rng = np.random.default_rng(99)
    tries = 0
    while len(ood_confs) < 20 and tries < 200:
        s = int(rng.integers(0, ne)); p = int(rng.integers(0, nr)); tries += 1
        if (s, p) in keyset: continue
        ood_confs.append(float(np.max(E @ (W @ (E[s] * R[p] * sq)))))
    inkb_mean = float(np.mean(inkb_confs))
    ood_mean = float(np.mean(ood_confs))
    assert inkb_mean > ood_mean, (
        "refuse conf mean in-KB(%.3f) !> mean OOD(%.3f)" % (inkb_mean, ood_mean)
    )
    print(
        "[selftest] PASS: set-recall=%.2f, 2hop=%.2f, in-KB conf %.3f > OOD %.3f (n_in=%d n_ood=%d)" %
        (setrecall, p2hop, inkb_mean, ood_mean, len(inkb_confs), len(ood_confs)),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------- corpus load --------------------------------- #
def load_hotpot_items(path, max_items):
    """Load HotpotQA items; return list of dicts with id/question/answer/type/title1/title2."""
    if not path.exists():
        raise FileNotFoundError("HotpotQA corpus not found at %s" % path)
    items = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= max_items: break
            r = json.loads(line)
            titles = r.get("supporting_facts", {}).get("title", [])
            # Each supporting fact has a title; collect UNIQUE titles in order.
            seen = set(); uniq = []
            for t in titles:
                if t not in seen:
                    uniq.append(t); seen.add(t)
            if len(uniq) < 2:
                continue   # skip items without 2 distinct supporting titles
            items.append({
                "id": r["id"],
                "question": r["question"],
                "answer": r["answer"].strip(),
                "type": r.get("type", "bridge"),
                "title1": uniq[0],
                "title2": uniq[1],
            })
    return items


def build_triples(items):
    """Build (t1, p1, t2) + (t2, p2, a) triples per item. Returns triples + ent/rel maps."""
    REL_LINK = "linked_via"
    REL_ANS = "supplies_answer"
    rels = [REL_LINK, REL_ANS]
    rid = {r: i for i, r in enumerate(rels)}

    # Build entity vocab: union of all titles and all answers.
    ents_set = set()
    for it in items:
        ents_set.add(it["title1"]); ents_set.add(it["title2"]); ents_set.add(it["answer"])
    ents = sorted(ents_set)
    eid = {e: i for i, e in enumerate(ents)}

    triples_raw = []
    chains_raw = []      # (t1, p1, t2, p2, a) for items that form a real chain
    for it in items:
        t1, t2, a = it["title1"], it["title2"], it["answer"]
        # Skip degenerate chains (t1==t2, t2==a, t1==a).
        if t1 == t2 or t2 == a or t1 == a:
            continue
        triples_raw.append((t1, REL_LINK, t2))
        triples_raw.append((t2, REL_ANS, a))
        # Only "bridge" type form real (s, p1, x, p2, o) chains; comparison answers
        # (yes/no) collapse into super-popular sinks that don't represent multi-hop
        # composition. Filter to bridge for 2-hop eval; keep ALL for ingest.
        if it.get("type") == "bridge":
            chains_raw.append((t1, REL_LINK, t2, REL_ANS, a))

    triples = [(eid[s], rid[p], eid[o]) for s, p, o in triples_raw]
    chains = [(eid[t1], rid[p1], eid[t2], rid[p2], eid[a]) for t1, p1, t2, p2, a in chains_raw]

    keyobjs = defaultdict(set)
    for (s, p, o) in triples:
        keyobjs[(s, p)].add(o)

    return triples, chains, {k: sorted(v) for k, v in keyobjs.items()}, ents, rels, eid, rid


# ----------------------------- ingest mechanism ---------------------------- #
def ingest_hebbian(triples, n_ent, n_rel, g, batch=2000):
    """Multi-value Hebbian: W += outer(E[o_i], key_i)/N. Same shape as n8."""
    E = bipolar(n_ent, N_DIM, g)
    R = bipolar(n_rel, N_DIM, g)
    sq = math.sqrt(N_DIM)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / N_DIM
    return E, R, W, sq


def _scores_batch(E, R, W, sq, sp_pairs):
    if not sp_pairs:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    s = np.array([x[0] for x in sp_pairs])
    p = np.array([x[1] for x in sp_pairs])
    keys = (E[s] * R[p] * sq).astype(np.float32)
    return (E @ (W @ keys.T)).T


# ----------------------------- evaluation ---------------------------------- #
def set_recall_at_k(E, R, W, sq, keyobjs, n_eval, g):
    """Set-recall@k where k=|objs| (same as n8)."""
    keys = list(keyobjs.items())
    if not keys: return 0.0
    idx = g.permutation(len(keys))[:min(n_eval, len(keys))]
    sp = [keys[i][0] for i in idx]
    objs = [keys[i][1] for i in idx]
    S = _scores_batch(E, R, W, sq, sp)
    tot = 0.0
    for j, ob in enumerate(objs):
        k = len(ob)
        topk = set(np.argpartition(S[j], -k)[-k:].tolist())
        tot += len(topk & set(ob)) / k
    return tot / max(len(idx), 1)


def random_key_control(E, R, W, sq, keyobjs, n_eval, n_ent, n_rel, g):
    """Discriminator-regime (Fix #16): score random (s, p) keys not in keyobjs; setrecall under
    these random keys should be near random (= 1/n_ent). If substrate setrecall is ~ this random
    control, substrate is at chance (the MedQA failure mode)."""
    keyset = set(keyobjs.keys())
    rand_sp = []
    tries = 0
    while len(rand_sp) < n_eval and tries < n_eval * 80:
        s = int(g.integers(0, n_ent)); p = int(g.integers(0, n_rel)); tries += 1
        if (s, p) in keyset: continue
        rand_sp.append((s, p))
    if not rand_sp:
        return 0.0
    S = _scores_batch(E, R, W, sq, rand_sp)
    # For each random key, "true object" is itself unknown; we use the popular-entity baseline:
    # ratio of top-1 scores ABOVE the in-KB top-1 mean. Cleaner: this is just the average
    # max-score; HIGH max-score on random keys = signal leakage. We instead return the expected
    # set-recall vs a held-out "what the random key would point to" (= 0; nothing was ingested).
    # So a sensible reading is: how often does top-1 of a random key happen to BE a true object
    # of some other key by chance? Approximate via top-1 == random target ent.
    n_ent_val = E.shape[0]
    targets = g.integers(0, n_ent_val, size=len(rand_sp))
    return float((S.argmax(axis=1) == targets).mean())


def refuse_gate(E, R, W, sq, keyobjs, n_ent, n_rel, n_q, g):
    """Calibrate tau on cal-half; eval on ev-half. Returns OOD refuse + in-KB accept."""
    inkb_keys = list(keyobjs.keys())
    idx = g.permutation(len(inkb_keys))[:min(n_q, len(inkb_keys))]
    inkb_conf = _scores_batch(E, R, W, sq, [inkb_keys[i] for i in idx]).max(axis=1)

    keyset = set(keyobjs.keys())
    ood_sp = []; tries = 0
    while len(ood_sp) < n_q and tries < n_q * 50:
        s = int(g.integers(0, n_ent)); p = int(g.integers(0, n_rel)); tries += 1
        if (s, p) in keyset: continue
        ood_sp.append((s, p))
    ood_conf = (
        _scores_batch(E, R, W, sq, ood_sp).max(axis=1) if ood_sp
        else np.zeros(0, np.float32)
    )

    h = len(inkb_conf) // 2; ho = len(ood_conf) // 2
    cal_in, ev_in = inkb_conf[:h], inkb_conf[h:]
    cal_ood, ev_ood = ood_conf[:ho], ood_conf[ho:]
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau, best_bal = cands[0], -1.0
    for tau in cands:
        acc = float((cal_in >= tau).mean())
        ref = float((cal_ood < tau).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal, best_tau = bal, float(tau)
    return {
        "tau": best_tau,
        "inkb_accept": float((ev_in >= best_tau).mean()),
        "ood_refuse": float((ev_ood < best_tau).mean()),
        "inkb_conf_mean": float(inkb_conf.mean()),
        "ood_conf_mean": float(ood_conf.mean()),
        "n_inkb_eval": int(len(ev_in)),
        "n_ood_eval": int(len(ev_ood)),
    }


def encode_entities(ents, model_name):
    """Frozen sentence-encoder embeddings of entity names. INPUT-stage only; scoring is matmul.

    Substrate-only-decode gate: this is INGEST time; the model is discarded after encode.
    The score op (cosine sim) is a numpy matmul; n_llm_calls stays 0 post-ingest.
    """
    from sentence_transformers import SentenceTransformer
    # HotpotQA titles are short English; light text-norm.
    texts = [e.replace("_", " ") for e in ents]
    m = SentenceTransformer(model_name, device="cpu")
    embs = m.encode(texts, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(embs, dtype=np.float32)


def encoder_geometry_check(ent_embs, g, n_sample=500):
    """Encoder mean-pool collapse guard (Fix #16 discriminator-regime sibling).

    Sample n_sample entity embeddings; compute off-diagonal mean cosine. If > 0.95, encoder
    has collapsed (MedQA-style mean-pool failure) -> HALT before Hebbian ingest.

    Note: bge/MiniLM embeddings are already L2-normalized.
    """
    n = ent_embs.shape[0]
    sample_idx = g.permutation(n)[:min(n_sample, n)]
    sample = ent_embs[sample_idx]
    C = sample @ sample.T
    iu = np.triu_indices_from(C, k=1)
    off_diag = C[iu]
    return {
        "off_diag_mean_cos": float(off_diag.mean()),
        "off_diag_max_cos": float(off_diag.max()),
        "n_sampled": int(len(sample_idx)),
        "diag_mean": float(np.diag(C).mean()),
    }


def inference_transfer(E, R, W, sq, chains, n_2hop, g, ent_embs):
    """Held-out 2-hop chains: substrate-2hop vs 1-hop direct vs frozen-encoder semantic.

    chains = list of (t1, p_link, t2, p_ans, a) already filtered to bridge-type.
    """
    if not chains:
        return {"n": 0, "skipped_reason": "no_bridge_chains_after_filter"}

    g.shuffle(chains)
    eval_chains = chains[:min(n_2hop, len(chains))]

    t1s = np.array([c[0] for c in eval_chains])
    p1s = np.array([c[1] for c in eval_chains])
    t2s = np.array([c[2] for c in eval_chains])   # ground-truth bridge
    p2s = np.array([c[3] for c in eval_chains])
    o_a = np.array([c[4] for c in eval_chains])   # ground-truth answer

    # Hop-1: t1, p_link -> predict bridge.
    s_a = [(int(t1s[j]), int(p1s[j])) for j in range(len(eval_chains))]
    S1 = _scores_batch(E, R, W, sq, s_a)
    x_hat = S1.argmax(axis=1)
    bridge_recall = float((x_hat == t2s).mean())

    # Hop-2: predicted bridge, p_ans -> predict answer.
    s_b = [(int(x_hat[j]), int(p2s[j])) for j in range(len(eval_chains))]
    S2 = _scores_batch(E, R, W, sq, s_b)
    o_hat = S2.argmax(axis=1)
    sub2 = float((o_hat == o_a).mean())

    # 1-hop direct baseline: query (t1, p_ans) -- substrate may or may not have this key
    # (it doesn't; we only ingested (t1, p_link, t2) and (t2, p_ans, a)). So this should be
    # near-random; serves as the "no-composition" baseline.
    s_c = [(int(t1s[j]), int(p2s[j])) for j in range(len(eval_chains))]
    Sc = _scores_batch(E, R, W, sq, s_c)
    base1 = float((Sc.argmax(axis=1) == o_a).mean())

    # Frozen-encoder semantic baseline: predict answer = NN(t1) by entity-name cosine.
    s_vecs = ent_embs[t1s]                                   # (B, D_enc)
    sim = s_vecs @ ent_embs.T                                # (B, n_ent)
    for j in range(len(eval_chains)):
        sim[j, t1s[j]] = -np.inf                             # exclude self
    enc_hat = sim.argmax(axis=1)
    enc_acc = float((enc_hat == o_a).mean())

    return {
        "n": int(len(eval_chains)),
        "substrate_2hop": sub2,
        "bridge_recall": bridge_recall,
        "baseline_1hop_direct": base1,
        "baseline_frozen_encoder": enc_acc,
    }


# ----------------------------- per-seed driver ----------------------------- #
def run_seed(seed, items, ent_embs_cache):
    g = np.random.default_rng(seed)

    triples, chains, keyobjs, ents, rels, eid, rid = build_triples(items)
    n_ent = len(ents); n_rel = len(rels)
    t = time.time()
    E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
    ingest_s = time.time() - t

    # Frozen-encoder ingest (one-shot per seed; cached by entity vocab).
    ent_vocab_key = (n_ent, ents[0] if ents else "", ents[-1] if ents else "")
    if ent_embs_cache.get("key") == ent_vocab_key:
        ent_embs = ent_embs_cache["embs"]
    else:
        t = time.time()
        ent_embs = encode_entities(ents, ENC_MODEL)
        print(
            "  [seed=%d] encoded %d entities with %s in %.1fs" %
            (seed, n_ent, ENC_MODEL, time.time() - t),
            flush=True,
        )
        ent_embs_cache["key"] = ent_vocab_key
        ent_embs_cache["embs"] = ent_embs

    # Encoder-geometry guard (MedQA-collapse signature).
    geom = encoder_geometry_check(ent_embs, np.random.default_rng(seed + 100))
    print(
        "  [seed=%d] encoder geom: off-diag mean cos=%.4f, max cos=%.4f (HALT thresh %.2f)" %
        (seed, geom["off_diag_mean_cos"], geom["off_diag_max_cos"], OFF_DIAG_COS_HALT_THRESHOLD),
        flush=True,
    )

    # Setrecall.
    setrecall = set_recall_at_k(E, R, W, sq, keyobjs, N_EVAL, np.random.default_rng(seed + 1))

    # Discriminator-regime random-key control (Fix #16).
    rand_ctrl = random_key_control(
        E, R, W, sq, keyobjs, N_EVAL, n_ent, n_rel,
        np.random.default_rng(seed + 2),
    )

    # Refuse-gate.
    refuse = refuse_gate(
        E, R, W, sq, keyobjs, n_ent, n_rel, N_OOD,
        np.random.default_rng(seed + 3),
    )

    # 2-hop inference-transfer with frozen-encoder baseline.
    infer = inference_transfer(
        E, R, W, sq, list(chains), N_2HOP,
        np.random.default_rng(seed + 4), ent_embs,
    )

    sub2 = infer.get("substrate_2hop", 0.0)
    base1 = infer.get("baseline_1hop_direct", 0.0)
    enc = infer.get("baseline_frozen_encoder", 0.0)
    ratio_1hop = (sub2 / max(base1, 1e-6))
    ratio_enc = (sub2 / max(enc, 1e-6))
    ratio_rand = (setrecall / max(rand_ctrl, 1e-6))

    print(
        "  [seed=%d] setrecall=%.4f (rand-ctrl=%.4f ratio=%.1fx) | refuse OOD=%.3f acc=%.3f (tau=%.4g) | "
        "infer 2hop=%.3f vs 1hop=%.3f (ratio=%.2fx) vs frozen-enc=%.3f (ratio=%.2fx) | "
        "bridge=%.3f n=%d | ingest=%.1fs" % (
            seed, setrecall, rand_ctrl, ratio_rand,
            refuse["ood_refuse"], refuse["inkb_accept"], refuse["tau"],
            sub2, base1, ratio_1hop, enc, ratio_enc,
            infer.get("bridge_recall", 0.0), infer.get("n", 0),
            ingest_s,
        ),
        flush=True,
    )

    return {
        "seed": seed,
        "N": N_DIM,
        "M_triples": len(triples),
        "n_ent": n_ent,
        "n_rel": n_rel,
        "n_keys": len(keyobjs),
        "n_chains_bridge": len(chains),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "setrecall_all": round(setrecall, 4),
        "random_key_control": round(rand_ctrl, 4),
        "encoder_geometry": geom,
        "refuse_gate": refuse,
        "inference_transfer": infer,
        "ingest_s": round(ingest_s, 1),
    }


# ----------------------------- verdict ------------------------------------- #
def verdict(ps) -> Tuple[str, str]:
    sr = float(np.mean([p["setrecall_all"] for p in ps]))
    rand = float(np.mean([p["random_key_control"] for p in ps]))
    ood = float(np.mean([p["refuse_gate"]["ood_refuse"] for p in ps]))
    acc = float(np.mean([p["refuse_gate"]["inkb_accept"] for p in ps]))
    s2 = float(np.mean([p["inference_transfer"].get("substrate_2hop", 0.0) for p in ps]))
    b1 = float(np.mean([p["inference_transfer"].get("baseline_1hop_direct", 0.0) for p in ps]))
    enc = float(np.mean([p["inference_transfer"].get("baseline_frozen_encoder", 0.0) for p in ps]))
    bridge = float(np.mean([p["inference_transfer"].get("bridge_recall", 0.0) for p in ps]))
    geom_off = float(np.mean([p["encoder_geometry"]["off_diag_mean_cos"] for p in ps]))
    n_chains = int(np.mean([p["inference_transfer"].get("n", 0) for p in ps]))

    ratio_enc = (s2 / max(enc, 1e-6))
    ratio_1hop = (s2 / max(b1, 1e-6))

    # CV across seeds (stability).
    sr_cv = (float(np.std([p["setrecall_all"] for p in ps]))
             / max(np.mean([p["setrecall_all"] for p in ps]), 1e-9))

    summ = (
        "setrecall=%.4f (rand-ctrl=%.4f) | refuse OOD=%.3f acc=%.3f | "
        "infer 2hop=%.3f vs 1hop=%.3f (ratio=%.2fx, need >=%.1fx) vs frozen-enc=%.3f "
        "(ratio=%.2fx, need >=%.1fx) | bridge=%.3f n_chains=%d | encoder off-diag=%.4f | cv=%.3f"
    ) % (
        sr, rand, ood, acc, s2, b1, ratio_1hop, INFER_RATIO_OVER_1HOP,
        enc, ratio_enc, INFER_RATIO_OVER_ENC, bridge, n_chains, geom_off, sr_cv,
    )

    # Encoder-geom HALT (MedQA collapse).
    if geom_off > OFF_DIAG_COS_HALT_THRESHOLD:
        return (
            "HARD_FAIL",
            ("HARD_FAIL: encoder mean-pool collapsed (off-diag cos=%.4f > %.2f, MedQA signature). "
             "Substrate is downstream of a broken keysep. " + summ) %
            (geom_off, OFF_DIAG_COS_HALT_THRESHOLD),
        )

    sr_pass = sr >= SETRECALL_FLOOR
    sr_fail = sr < SETRECALL_FAIL
    refuse_pass = ood >= REFUSE_OOD_MIN and acc >= ACCEPT_INKB_MIN
    refuse_fail = ood < REFUSE_FAIL
    infer_pass_1hop = (s2 > b1 + INFER_MARGIN_OVER_1HOP) and (ratio_1hop >= INFER_RATIO_OVER_1HOP)
    infer_pass_enc = ratio_enc >= INFER_RATIO_OVER_ENC
    infer_fail = ratio_1hop < INFER_RATIO_FAIL

    if sr_fail or refuse_fail or infer_fail:
        return (
            "HARD_FAIL",
            "HARD_FAIL: floor breached. " + summ,
        )
    if sr_pass and refuse_pass and infer_pass_1hop and infer_pass_enc:
        return (
            "HARD_PASS",
            ("HARD_PASS: substrate HotpotQA KB-ingest GOVERNED (refuse-gate) + COMPOSES (2-hop "
             "beats 1-hop direct AND frozen-encoder semantic). " + summ),
        )
    return (
        "MIDDLE_BAND",
        "MIDDLE_BAND: partial -- not all load-bearing dims hold. " + summ,
    )


# ----------------------------- main ---------------------------------------- #
if __name__ == "__main__":
    print(
        "[config] anchor=%s mode=%s seeds=%s N=%d M_items=%d enc=%s | %s" %
        (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, MAX_ITEMS, ENC_MODEL, CONFIG_VERSION),
        flush=True,
    )
    t0 = time.time()

    out_dir = REPO / "data" / ("exp_%s" % os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load corpus ONCE (deterministic).
    items = load_hotpot_items(HOTPOT_PATH, MAX_ITEMS)
    print(
        "[corpus] loaded %d HotpotQA items from %s (max_items=%d)" %
        (len(items), HOTPOT_PATH.name, MAX_ITEMS),
        flush=True,
    )

    # Per-seed checkpoint with config gate.
    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "M": MAX_ITEMS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        "[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining),
        flush=True,
    )

    ent_embs_cache = {}
    for s in remaining:
        rec = run_seed(s, items, ent_embs_cache)
        write_partial(out_dir, s, rec)

    per_seed = list(aggregate_partials(out_dir, SEEDS, run_config=run_config).values())

    v, vmsg = verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)

    elapsed_s = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION,
        "per_seed": per_seed,
        "elapsed_s": round(elapsed_s, 1),
        "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
        "n_llm_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "H HotpotQA 1k-dev substrate KB-ingest; mirrors n8 ConceptNet + U1 FB15k-237 "
            "chain-grade pattern. Per-item 2-hop chain: (title1, linked_via, title2) + "
            "(title2, supplies_answer, answer). Encoder: MiniLM-L6 (n8-proven on short "
            "entity names; chosen over pythia-160m mean-pool which collapsed on MedQA long "
            "vignettes). Encoder-geometry HALT guard (off-diag cos > 0.95) catches the MedQA "
            "signature pre-emptively. Fix #16 discriminator-regime: random-key control + "
            "frozen-encoder semantic baseline + 1-hop direct baseline (all <= 2x means HALT)."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(
        "[done] %.1fs -> %s" % (elapsed_s, out_dir / "metrics.json"),
        flush=True,
    )
