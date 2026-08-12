"""SCHEMA-VET probe for g1b @ 12.2% EM on HotpotQA dev-1k.

Replicates the GENERATION_ONLY arm prediction logic from
experiments/exp_substrate_native_qa_hotpotqa_v1.py (run_mode=full) at REDUCED
N_DIM (so it fits in a laptop probe in <2min) to characterize what's actually
driving the 12.2% EM number.

Skunkworks-cert-owner SCHEMA-VET; not for atomization.
"""
from __future__ import annotations
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from hdlab.char_trigram_encoder import CharTrigramEncoder
from hdlab.kg_traversal import KGStore
from hdlab.sequence_memory import SequenceMatrix
from hdlab.generation import SubstrateGenerator

HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"

_PUNCT_RE = re.compile(r"[^\w\s]")
_ARTICLE_RE = re.compile(r"\b(a|an|the)\b", flags=re.IGNORECASE)


def normalize_answer(s):
    if s is None:
        return ""
    s = s.lower()
    s = _PUNCT_RE.sub(" ", s)
    s = _ARTICLE_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def exact_match(a, b):
    return int(normalize_answer(a) == normalize_answer(b))


def load_items(path, max_items):
    items = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= max_items:
                break
            r = json.loads(line)
            sf = r.get("supporting_facts", {}) or {}
            titles = sf.get("title", []) or []
            seen = set()
            uniq = []
            for t in titles:
                if t not in seen:
                    uniq.append(t)
                    seen.add(t)
            if len(uniq) < 2:
                continue
            items.append({
                "id": r["id"],
                "question": r["question"],
                "answer": str(r.get("answer", "")).strip(),
                "type": r.get("type", "bridge"),
                "title1": uniq[0],
                "title2": uniq[1],
            })
    return items


def main():
    # Match v1 cell: N_Q=1000, but use reduced N_DIM=2048 for probe-speed.
    N_DIM = 2048
    N_Q = 1000
    TOP_K = 5
    GEN_DEPTH = 4
    SIGMA = 0.10

    print(f"[probe] loading HotpotQA dev (max {N_Q}) ...", flush=True)
    items = load_items(HOTPOT_PATH, N_Q)
    print(f"[probe] loaded {len(items)} items", flush=True)

    # === Distributional facts ===
    answers = [it["answer"] for it in items]
    answer_freq = Counter(normalize_answer(a) for a in answers)
    questions = [it["question"] for it in items]
    types = Counter(it["type"] for it in items)

    print("\n=== distribution ===", flush=True)
    print(f"type breakdown: {dict(types)}", flush=True)
    most_common_answers = answer_freq.most_common(10)
    print(f"top 10 answers: {most_common_answers}", flush=True)
    yes_no = answer_freq.get("yes", 0) + answer_freq.get("no", 0)
    print(f"yes/no fraction: {yes_no}/{len(items)} = {yes_no/len(items):.3f}", flush=True)

    # === C2: how often is gold-answer a substring of question? ===
    in_q = 0
    for it in items:
        if normalize_answer(it["answer"]) and normalize_answer(it["answer"]) in normalize_answer(it["question"]):
            in_q += 1
    print(f"\n[C2] gold answer is substring of question: {in_q}/{len(items)} = {in_q/len(items):.3f}",
          flush=True)

    # === Build vocab + KG + sequence matrix (matches v1 cell logic, seed=7) ===
    seed = 7
    rels = ["linked_via", "supplies_answer"]
    rid = {r: i for i, r in enumerate(rels)}
    ents_set = set()
    for it in items:
        ents_set.add(it["title1"])
        ents_set.add(it["title2"])
        ents_set.add(it["answer"])
    ents = sorted(ents_set)
    eid = {e: i for i, e in enumerate(ents)}
    print(f"\n[vocab] |ents|={len(ents)}", flush=True)

    triples = []
    for it in items:
        t1, t2, a = it["title1"], it["title2"], it["answer"]
        if t1 == t2 or t2 == a or t1 == a:
            continue
        triples.append((eid[t1], rid["linked_via"], eid[t2]))
        triples.append((eid[t2], rid["supplies_answer"], eid[a]))
    triples_t = torch.tensor(triples, dtype=torch.long)
    print(f"[vocab] triples={len(triples)}", flush=True)

    gen_rng = torch.Generator()
    gen_rng.manual_seed(seed)
    kg = KGStore(n_ent=len(ents), n_rel=len(rels), n_dim=N_DIM, generator=gen_rng)
    kg.ingest_triples(triples_t)

    # Sequence matrix (chain t1 -> t2 -> a)
    sm = SequenceMatrix(n_dim=N_DIM)
    E_cpu = kg.E.detach().cpu()
    pp, pc = [], []
    for it in items:
        t1, t2, a = it["title1"], it["title2"], it["answer"]
        if t1 == t2 or t2 == a or t1 == a:
            continue
        i1, i2, ia = eid[t1], eid[t2], eid[a]
        pp.append(E_cpu[i1]); pc.append(E_cpu[i2])
        pp.append(E_cpu[i2]); pc.append(E_cpu[ia])
    K_prev = torch.stack(pp); K_curr = torch.stack(pc)
    sm.S.add_((K_curr.T @ K_prev) / N_DIM)
    sm._n_pairs_bound = len(pp)
    print(f"[seq] n_pairs={len(pp)} density={len(pp)/N_DIM:.2f}x N_DIM", flush=True)

    # Encoder
    print("[probe] encoding questions+entity-names via char_trigram ...", flush=True)
    enc = CharTrigramEncoder(n_dim=N_DIM)
    t0 = time.time()
    q_np = enc.encode_batch([it["question"] for it in items])
    ent_np = enc.encode_batch(ents)
    print(f"[probe] encoded in {time.time()-t0:.1f}s", flush=True)
    q_hd = torch.from_numpy(q_np).to(torch.float32)
    ent_hd = torch.from_numpy(ent_np).to(torch.float32)

    # === GENERATION_ONLY arm (matches v1 cell exactly) ===
    # Seed: argmax(q_hd · ent_hd.T)
    cos_q_ent = q_hd @ ent_hd.T
    top1 = cos_q_ent.argmax(dim=1).numpy().tolist()

    # Probe: what is the START_ENTITY hit-rate?
    start_correct = 0
    start_in_sf = 0
    start_eq_t1 = 0
    start_eq_t2 = 0
    start_eq_answer = 0
    for qi, it in enumerate(items):
        start_name = ents[top1[qi]]
        gold = it["answer"]
        if exact_match(start_name, gold):
            start_correct += 1
            start_eq_answer += 1
        if start_name == it["title1"]:
            start_eq_t1 += 1
        if start_name == it["title2"]:
            start_eq_t2 += 1
        if start_name in (it["title1"], it["title2"]):
            start_in_sf += 1
    print(f"\n[C4 start-entity probe]", flush=True)
    print(f"  start_name == gold_answer: {start_correct}/{len(items)} = {start_correct/len(items):.3f}",
          flush=True)
    print(f"  start_name in supporting_facts titles: {start_in_sf}/{len(items)} = {start_in_sf/len(items):.3f}",
          flush=True)
    print(f"  start_name == title1: {start_eq_t1}; == title2: {start_eq_t2}", flush=True)

    # Generate (depth=4) for all 1k questions; track per-step output
    print(f"\n[gen] running SubstrateGenerator depth={GEN_DEPTH} sigma={SIGMA} on {len(items)} questions ...",
          flush=True)
    sg = SubstrateGenerator(sm, E_cpu, sigma_scale=SIGMA)
    rng = torch.Generator()
    rng.manual_seed(int(seed) + hash("GENERATION_ONLY") % 100003)

    preds = []
    visited_all = []
    em_hits = 0
    em_hits_start_excluded = 0  # EM if we ignore start_idx as candidate
    em_hits_mode_real = 0  # EM using mode over visited (NOT start)

    t_gen = time.time()
    for qi, it in enumerate(items):
        start_idx = int(top1[qi])
        start_key = sg.codebook[start_idx]
        visited = sg.generate(start_key, GEN_DEPTH, rng=rng)
        visited_all.append(visited)
        # Replicate v1 cell logic exactly:
        counts = defaultdict(int)
        for c in visited:
            counts[int(c)] += 1
        counts[start_idx] += 0  # exact line from v1 (no-op when start not in visited)
        best = max(counts.items(), key=lambda kv: kv[1]) if counts else (start_idx, 0)
        pred = ents[best[0]]
        preds.append(pred)
        gold = it["answer"]
        if exact_match(pred, gold):
            em_hits += 1
        # Alternative: pure mode of visited (no start)
        c2 = Counter(visited)
        best2 = c2.most_common(1)[0][0]
        if exact_match(ents[best2], gold):
            em_hits_mode_real += 1
    print(f"[gen] done in {time.time()-t_gen:.1f}s", flush=True)

    em = em_hits / len(items)
    em2 = em_hits_mode_real / len(items)
    print(f"\n[recompute EM] cell-logic EM = {em_hits}/{len(items)} = {em:.4f}", flush=True)
    print(f"[recompute EM] pure-mode-of-visited EM = {em_hits_mode_real}/{len(items)} = {em2:.4f}", flush=True)

    # === What's actually predicted? ===
    pred_freq = Counter(normalize_answer(p) for p in preds)
    print(f"\n[pred dist] top 10 predicted: {pred_freq.most_common(10)}", flush=True)
    print(f"[pred dist] n_distinct predictions: {len(set(preds))}", flush=True)
    yes_pred = pred_freq.get("yes", 0); no_pred = pred_freq.get("no", 0)
    print(f"[pred dist] predicted 'yes': {yes_pred}; 'no': {no_pred}", flush=True)

    # === C1: how does EM break down by answer-frequency? ===
    common_answers = set(a for a, _ in answer_freq.most_common(100))
    em_common = 0; em_rare = 0; n_common = 0; n_rare = 0
    for qi, it in enumerate(items):
        if normalize_answer(it["answer"]) in common_answers:
            n_common += 1
            if exact_match(preds[qi], it["answer"]):
                em_common += 1
        else:
            n_rare += 1
            if exact_match(preds[qi], it["answer"]):
                em_rare += 1
    print(f"\n[C1] EM on top-100 most-common answers: {em_common}/{n_common} = "
          f"{em_common/max(n_common,1):.3f}", flush=True)
    print(f"[C1] EM on rare answers: {em_rare}/{n_rare} = {em_rare/max(n_rare,1):.3f}", flush=True)

    # === C3: per-type EM ===
    em_by_type = defaultdict(lambda: [0, 0])
    for qi, it in enumerate(items):
        em_by_type[it["type"]][1] += 1
        if exact_match(preds[qi], it["answer"]):
            em_by_type[it["type"]][0] += 1
    print(f"\n[C3] EM by type:", flush=True)
    for t, (h, n) in em_by_type.items():
        print(f"  {t}: {h}/{n} = {h/max(n,1):.3f}", flush=True)

    # === C4 cont: hits decomposed: was the prediction == start_entity? ===
    pred_eq_start = 0
    for qi, it in enumerate(items):
        if preds[qi] == ents[int(top1[qi])]:
            pred_eq_start += 1
    print(f"\n[C4b] prediction == start_entity (char_trigram nearest-name): "
          f"{pred_eq_start}/{len(items)} = {pred_eq_start/len(items):.3f}", flush=True)

    # === C4c: hits where start_entity == gold_answer ===
    em_via_start = 0
    em_via_gen = 0
    for qi, it in enumerate(items):
        if exact_match(preds[qi], it["answer"]):
            if exact_match(ents[int(top1[qi])], it["answer"]):
                em_via_start += 1
            else:
                em_via_gen += 1
    print(f"\n[C4c] EM-hit decomposition:", flush=True)
    print(f"  hits where start_entity already == gold: {em_via_start}", flush=True)
    print(f"  hits where prediction came from generation (start != gold): {em_via_gen}", flush=True)

    # === C5: random-seed control ===
    print(f"\n[C5] random-seed control (sample 200 questions, random start_entity) ...",
          flush=True)
    rs_rng = np.random.default_rng(42)
    rs_idx_perm = rs_rng.permutation(len(ents))
    sample_n = min(200, len(items))
    em_rand = 0
    rng_rand = torch.Generator(); rng_rand.manual_seed(999)
    for qi in range(sample_n):
        start_idx = int(rs_idx_perm[qi % len(rs_idx_perm)])
        start_key = sg.codebook[start_idx]
        visited = sg.generate(start_key, GEN_DEPTH, rng=rng_rand)
        counts = defaultdict(int)
        for c in visited:
            counts[int(c)] += 1
        counts[start_idx] += 0
        best = max(counts.items(), key=lambda kv: kv[1])
        pred = ents[best[0]]
        if exact_match(pred, items[qi]["answer"]):
            em_rand += 1
    print(f"  random-seed EM (n={sample_n}): {em_rand}/{sample_n} = {em_rand/sample_n:.3f}", flush=True)

    # === Visited-uniqueness (sanity for mode tie-break) ===
    n_distincts = [len(set(v)) for v in visited_all]
    print(f"\n[visited uniqueness] mean n_distinct = {np.mean(n_distincts):.3f} (depth={GEN_DEPTH})",
          flush=True)
    all_unique = sum(1 for x in n_distincts if x == GEN_DEPTH)
    print(f"[visited uniqueness] all-distinct (no mode tie-break info): "
          f"{all_unique}/{len(items)} = {all_unique/len(items):.3f}", flush=True)


if __name__ == "__main__":
    main()
