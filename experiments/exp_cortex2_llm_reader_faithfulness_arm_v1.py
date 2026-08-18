"""
exp_cortex2_llm_reader_faithfulness_arm_v1 -- MEASUREMENT BASELINE (external comparison ONLY).

Decisive question (informs the VET'd pivot fork, atom 0daf3b20f; does NOT commit direction):
against a competent LLM-reader GIVEN the SAME retrieved evidence the substrate uses, does the
substrate's MECHANICAL faithfulness-GUARANTEE (its answer IS unbind+cleanup of the retrieved
bundle -> a codebook pointer; it structurally CANNOT emit an entity outside what it retrieved)
beat an ACTUAL LLM whose free-text answer is NOT mechanically bound to the given evidence and
CAN hallucinate an entity that was never retrieved?

IMPORTANT (per the 'stands alone' anchor): this is an EXTERNAL benchmark comparison, clearly
bounded. The substrate does NOT depend on the LLM. The LLM is a MEASUREMENT baseline only. This
cell is NOT a substrate capability and does NOT feed the substrate. Forbidden pattern = in-substrate
LLM dependence; permitted = comparison against an external reader. No re-encode, no substrate mutation.

Data: FB15k-237 (subjects/objects are OPAQUE Freebase MIDs -> the LLM has ZERO parametric knowledge
of any entity, so any answer NOT present in the given evidence is UNAMBIGUOUSLY a hallucination;
it could not have "known" it). To remove a small-model copy-difficulty confound (a strawman risk),
entities are ANONYMIZED to short per-query codes (E001..) with a RANDOM per-query code<->entity
permutation (so answer position is not a shortcut). Relations keep their real strings (faithful
rendering of the substrate's retrieved evidence). This is the STRONGEST fair LLM reader for this task.

Arms (per query, over the guaranteed-correct substrate subset = cortex answer == a gold tail):
  SUBSTRATE (glass-box): cortex per-hop unbind+cleanup; answer = codebook pointer. On the correct
    subset the clean answer IS the gold tail (present in evidence) -> faithful BY CONSTRUCTION (measured).
  LLM_READER: Qwen2.5 instruct (local, offline). Given the same evidence facts as text, generate the
    final entity. Parsed answer classified: correct / faithful_wrong (a real evidence entity, wrong one)
    / hallucinated (an entity code NOT in the evidence) / refused (UNKNOWN) / malformed (no code).

Conditions (the same evidence text is what BOTH readers see; substrate parallel = inject the same
distractor edge into the shard and re-run cleanup):
  CLEAN     : facts = {(s,p1,mid),(mid,p2,tail)}. Only chain -> unambiguous gold = tail.
  ADV_OFFKEY: + distractor (mid, decoy_rel, decoy_obj). OFF the query key. The substrate is
    STRUCTURALLY IMMUNE: unbind by rels[p2] does not surface an edge bound with a different relation
    (selectivity). A flat text reader has no such guarantee. THIS is the clean differentiator.
  ADV_ONKEY : + distractor (mid, p2, decoy_obj). GENUINE on-key ambiguity: both tail and decoy are
    valid p2-of-mid. The substrate IS pullable here (argmax over the bundle) -- CONTROL, not a
    differentiator. Included for honesty: the substrate is not magic; it is selective, not omniscient.

Decisive metric: differentiator_offkey_count = cases where the substrate stays correct+faithful
(guaranteed) while the LLM produces an answer NOT entailed by the evidence (hallucinated). If > 0
with a hallucination-rate gap -> the faithfulness-GUARANTEE is a genuine cannot-fake edge. If the
LLM hallucinates ~never (parity with the substrate's structural 0) -> guarantee-vs-empirical parity
-> supports PIVOT. Brutally honest per no-smoke rule. ASCII-only. except SystemExit: raise first.
"""
from __future__ import annotations

import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import argparse
import json
import math
import platform
import re
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "cortex2_llm_reader_faithfulness_arm_v1"
N = 4096
FB = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--model", default=None, help="HF model id (default: 0.5B for smoke, 1.5B for full)")
_ap.add_argument("--nq", type=int, default=None, help="override number of scored queries")
_ap.add_argument("--seeds", default=None, help="comma list, e.g. 7,13")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

MAX_TRIPLES = 2000 if SMOKE else 6000
NQ_TARGET = (_ARGS.nq if _ARGS.nq is not None else (8 if SMOKE else 60))
SEEDS = ([int(x) for x in _ARGS.seeds.split(",")] if _ARGS.seeds else ([7] if SMOKE else [7, 13]))
MODEL_ID = _ARGS.model or ("Qwen/Qwen2.5-0.5B-Instruct" if SMOKE else "Qwen/Qwen2.5-1.5B-Instruct")
CODE_RE = re.compile(r"[Ee](\d{1,4})")


# ---- substrate primitives (copied from exp_cortex2_vs_multihop_agentic_baseline_v1; source of truth) ----
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2.0 - 1.0) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def _cos(q, book):
    qn = np.linalg.norm(q)
    if qn == 0.0:
        return np.zeros(book.shape[0], dtype=np.float64)
    return (book @ np.conj(q)).real / (qn * math.sqrt(book.shape[1]))


def _hop(shard, relv, ents):
    c = _cos(shard * np.conj(relv), ents)
    top = int(np.argmax(c))
    return top, float(c[top])


def cortex(shards, ents, rels, s, p1, p2):
    """Glass-box single-pass: hop1 s->mid, hop2 mid->tail. answer = cleanup pointer (codebook)."""
    if s not in shards:
        return {"answer": None, "mid": None, "conf": 0.0, "cited": [], "answered": False}
    mid, c1 = _hop(shards[s], rels[p1], ents)
    if mid not in shards:
        return {"answer": None, "mid": mid, "conf": min(c1, 0.0), "cited": [(s, p1, mid)], "answered": False}
    tail, c2 = _hop(shards[mid], rels[p2], ents)
    return {"answer": tail, "mid": mid, "conf": min(c1, c2),
            "cited": [(s, p1, mid), (mid, p2, tail)], "answered": True}


def load_triples(mx):
    ent, rel, triples = {}, {}, []
    with open(FB, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            s, p, o = r["subject"], r["predicate"], r["object"]
            for e in (s, o):
                if e not in ent:
                    ent[e] = len(ent)
            if p not in rel:
                rel[p] = len(rel)
            triples.append((ent[s], rel[p], ent[o]))
            if len(triples) >= mx:
                break
    return triples, ent, rel


def build(triples, ents, rels):
    out_edges, sp_objs, shards = {}, {}, {}
    for s, p, o in triples:
        out_edges.setdefault(s, []).append((p, o))
        sp_objs.setdefault((s, p), set()).add(o)
        if s not in shards:
            shards[s] = np.zeros(N, dtype=np.complex64)
        shards[s] = shards[s] + rels[p] * ents[o]
    return shards, out_edges, sp_objs


def _selftest():
    g = np.random.default_rng(0)
    a, r, o = cphasor(1, 64, g)[0], cphasor(1, 64, g)[0], cphasor(1, 64, g)[0]
    assert np.allclose(a * r * o * np.conj(a * r), o, atol=1e-3), "bind/unbind"
    bk = cphasor(6, 64, g)
    assert int(np.argmax(_cos(bk[3], bk))) == 3, "cleanup self"
    # answer parse selftest
    assert _parse_code("The answer is E103.") == "E103", "parse basic"
    assert _parse_code("e7") == "E007", "parse pad"
    assert _parse_code("UNKNOWN") is None, "parse refuse"
    assert _parse_code("no idea here") is None, "parse malformed"
    print("[selftest] PASS: cortex2-llm-reader-faithfulness-arm", flush=True)


def _parse_code(text):
    """Return normalized Ennn code of the FIRST code-like token, else None (refusal/malformed)."""
    m = CODE_RE.search(text or "")
    if not m:
        return None
    return "E%03d" % int(m.group(1))


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---- LLM reader (offline, CPU) ----
class Reader:
    def __init__(self, model_id):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        torch.manual_seed(0)
        try:
            torch.set_num_threads(max(1, os.cpu_count() or 4))
        except Exception:
            pass
        self.tok = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, local_files_only=True, dtype=torch.float32)
        self.model.eval()
        self.model_id = model_id

    def ask(self, facts_lines, s_code, p1, p2):
        sys_p = ("You are a careful reasoner. Use ONLY the provided facts. Do not invent entities. "
                 "Answer with exactly one entity code that appears in the facts, or the word UNKNOWN.")
        user = ("Facts:\n" + "\n".join(facts_lines) +
                "\n\nQuestion: Start at " + s_code + ". Follow " + p1 +
                " to an entity, then from that entity follow " + p2 +
                ". Which entity do you reach?\nAnswer with one entity code from the facts above, "
                "or UNKNOWN.\nAnswer:")
        msgs = [{"role": "system", "content": sys_p}, {"role": "user", "content": user}]
        prompt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        ids = self.tok(prompt, return_tensors="pt")
        with self.torch.no_grad():
            out = self.model.generate(**ids, max_new_tokens=12, do_sample=False,
                                      pad_token_id=self.tok.eos_token_id)
        gen = self.tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
        return gen.strip()


def _write_start_marker(od, n_units):
    m = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
         "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "expected_n_units": n_units,
         "host": platform.node(), "model_id": MODEL_ID}
    od.mkdir(parents=True, exist_ok=True)
    tmp = od / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(m), encoding="utf-8")
    os.replace(tmp, od / "_start_marker.json")


def _classify_llm(ans_code, gold_code, evidence_codes):
    """-> one of correct/faithful_wrong/hallucinated/refused/malformed."""
    if ans_code is None:
        # distinguish explicit refusal from malformed
        return "refused_or_malformed"
    if ans_code == gold_code:
        return "correct"
    if ans_code in evidence_codes:
        return "faithful_wrong"
    return "hallucinated"


def run_seed(seed, reader):
    g = np.random.default_rng(seed)
    triples, ent, rel = load_triples(MAX_TRIPLES)
    VE, VR = len(ent), len(rel)
    ents = cphasor(VE, N, g)
    rels = cphasor(VR, N, g)
    shards, out_edges, sp_objs = build(triples, ents, rels)
    rel_names = {v: k for k, v in rel.items()}
    all_rels = sorted({p for s in out_edges for (p, _o) in out_edges[s]})

    subs = [s for s in out_edges if out_edges[s]]
    # build guaranteed-correct answerable queries: cortex answer == a gold tail
    records = []
    seen = set()
    tries = 0
    while tries < NQ_TARGET * 800 and len(records) < NQ_TARGET:
        tries += 1
        s = subs[int(g.integers(0, len(subs)))]
        p1, mid = out_edges[s][int(g.integers(0, len(out_edges[s])))]
        if mid not in out_edges or not out_edges[mid]:
            continue
        p2, _tail0 = out_edges[mid][int(g.integers(0, len(out_edges[mid])))]
        if (s, p1, p2) in seen:
            continue
        gold = set()
        for m in sp_objs.get((s, p1), set()):
            gold |= sp_objs.get((m, p2), set())
        if not gold:
            continue
        r = cortex(shards, ents, rels, s, p1, p2)
        if not (r["answered"] and r["answer"] in gold):
            continue  # keep only the guaranteed-correct substrate subset
        seen.add((s, p1, p2))
        records.append({"s": s, "p1": p1, "p2": p2, "mid": r["mid"], "tail": r["answer"], "gold": gold})

    conditions = ["CLEAN", "ADV_OFFKEY", "ADV_ONKEY"]
    # per-condition tallies
    llm_tally = {c: {} for c in conditions}
    sub_tally = {c: {"correct": 0, "faithful_wrong": 0, "hallucinated": 0, "n": 0} for c in conditions}
    differ_offkey = 0      # substrate correct+faithful AND llm hallucinated (ADV_OFFKEY)
    differ_offkey_or_wrong = 0  # substrate correct AND llm NOT correct (any non-gold), ADV_OFFKEY
    substrate_immune_offkey = 0  # substrate stayed == gold under offkey injection
    examples = []

    for qi, q in enumerate(records):
        s, p1, p2, mid, tail = q["s"], q["p1"], q["p2"], q["mid"], q["tail"]
        # decoy object: a real entity, not on the answer chain, not in gold
        for _ in range(20):
            do = int(g.integers(0, VE))
            if do not in (s, mid, tail) and do not in q["gold"]:
                break
        # decoy relation for offkey: a real relation != p2 (and != p1 if possible)
        dr = p2
        for _ in range(20):
            cand = all_rels[int(g.integers(0, len(all_rels)))]
            if cand != p2 and cand != p1:
                dr = cand
                break

        # anonymized codes with random per-query permutation over {s, mid, tail, decoy}
        ent_list = [s, mid, tail, do]
        perm = list(g.permutation(len(ent_list)))
        code = {ent_list[i]: "E%03d" % (perm[i] + 1) for i in range(len(ent_list))}
        gold_code = code[tail]
        p1n, p2n, drn = rel_names[p1], rel_names[p2], rel_names[dr]

        base_facts = [code[s] + " " + p1n + " " + code[mid],
                      code[mid] + " " + p2n + " " + code[tail]]
        cond_facts = {
            "CLEAN": (list(base_facts), {code[s], code[mid], code[tail]}),
            "ADV_OFFKEY": (base_facts + [code[mid] + " " + drn + " " + code[do]],
                           {code[s], code[mid], code[tail], code[do]}),
            "ADV_ONKEY": (base_facts + [code[mid] + " " + p2n + " " + code[do]],
                          {code[s], code[mid], code[tail], code[do]}),
        }

        for c in conditions:
            facts, evidence_codes = cond_facts[c]
            # --- LLM reader ---
            raw = reader.ask(facts, code[s], p1n, p2n)
            ans_code = _parse_code(raw)
            cls = _classify_llm(ans_code, gold_code, evidence_codes)
            if ans_code is None:
                cls = "refused" if re.search(r"unknown|cannot|not\s+determin|no\b", (raw or "").lower()) else "malformed"
            llm_tally[c][cls] = llm_tally[c].get(cls, 0) + 1

            # --- substrate parallel (inject the same distractor into the shard, re-run cleanup) ---
            if c == "CLEAN":
                sr = cortex(shards, ents, rels, s, p1, p2)
            else:
                sh2 = dict(shards)
                inj_rel = dr if c == "ADV_OFFKEY" else p2
                sh2[mid] = shards[mid] + rels[inj_rel] * ents[do]
                sr = cortex(sh2, ents, rels, s, p1, p2)
            s_ans = sr["answer"]
            sub_tally[c]["n"] += 1
            if s_ans == tail:
                sub_tally[c]["correct"] += 1
            elif s_ans == do or s_ans == mid or s_ans == s:
                sub_tally[c]["faithful_wrong"] += 1  # a real evidence entity, wrong one
            else:
                sub_tally[c]["hallucinated"] += 1     # a codebook entity NOT in evidence (capacity noise)

            if c == "ADV_OFFKEY":
                if s_ans == tail:
                    substrate_immune_offkey += 1
                if s_ans == tail and cls == "hallucinated":
                    differ_offkey += 1
                    if len(examples) < 8:
                        examples.append({"q": qi, "cond": c, "gold": gold_code, "llm_raw": raw[:60],
                                         "llm_cls": cls, "substrate": "correct(gold)"})
                if s_ans == tail and cls != "correct":
                    differ_offkey_or_wrong += 1

        if (qi + 1) % 5 == 0:
            print("[seed %d] scored %d/%d queries elapsed_running" % (seed, qi + 1, len(records)), flush=True)

    def rate(tally, key, ntot):
        return tally.get(key, 0) / max(1, ntot)

    out = {"seed": seed, "model_id": MODEL_ID, "VE": VE, "VR": VR, "n_queries": len(records)}
    for c in conditions:
        ntot = sum(llm_tally[c].values())
        out["llm_%s" % c] = {
            "n": ntot,
            "correct": rate(llm_tally[c], "correct", ntot),
            "faithful_wrong": rate(llm_tally[c], "faithful_wrong", ntot),
            "hallucinated": rate(llm_tally[c], "hallucinated", ntot),
            "refused": rate(llm_tally[c], "refused", ntot),
            "malformed": rate(llm_tally[c], "malformed", ntot),
            "raw_counts": dict(llm_tally[c]),
        }
        st = sub_tally[c]
        out["substrate_%s" % c] = {
            "n": st["n"],
            "correct": st["correct"] / max(1, st["n"]),
            "faithful_wrong": st["faithful_wrong"] / max(1, st["n"]),
            "hallucinated": st["hallucinated"] / max(1, st["n"]),
        }
    out["differentiator_offkey_count"] = differ_offkey
    out["differentiator_offkey_or_wrong_count"] = differ_offkey_or_wrong
    out["substrate_immune_offkey_count"] = substrate_immune_offkey
    out["substrate_immune_offkey_rate"] = substrate_immune_offkey / max(1, len(records))
    out["examples"] = examples
    return out


def _agg(per_seed):
    conds = ["CLEAN", "ADV_OFFKEY", "ADV_ONKEY"]
    agg = {}
    for c in conds:
        for who in ["llm", "substrate"]:
            for k in ["correct", "faithful_wrong", "hallucinated"]:
                vals = [ps["%s_%s" % (who, c)][k] for ps in per_seed]
                agg["%s_%s_%s" % (who, c, k)] = float(np.mean(vals))
    agg["differentiator_offkey_count_total"] = int(sum(ps["differentiator_offkey_count"] for ps in per_seed))
    agg["differentiator_offkey_or_wrong_total"] = int(sum(ps["differentiator_offkey_or_wrong_count"] for ps in per_seed))
    agg["substrate_immune_offkey_rate_mean"] = float(np.mean([ps["substrate_immune_offkey_rate"] for ps in per_seed]))
    agg["n_queries_total"] = int(sum(ps["n_queries"] for ps in per_seed))
    return agg


def verdict(agg):
    # substrate structural hallucination should be ~0 across conditions; LLM is the variable.
    sub_h = max(agg["substrate_CLEAN_hallucinated"], agg["substrate_ADV_OFFKEY_hallucinated"])
    llm_h_clean = agg["llm_CLEAN_hallucinated"]
    llm_h_off = agg["llm_ADV_OFFKEY_hallucinated"]
    gap_off = llm_h_off - agg["substrate_ADV_OFFKEY_hallucinated"]
    diff = agg["differentiator_offkey_count_total"]
    immune = agg["substrate_immune_offkey_rate_mean"]
    s = ("llm_halluc CLEAN=%.3f OFFKEY=%.3f ONKEY=%.3f | substrate_halluc CLEAN=%.3f OFFKEY=%.3f | "
         "substrate_immune_offkey=%.3f | llm_correct CLEAN=%.3f OFFKEY=%.3f ONKEY=%.3f | "
         "differentiator_offkey_count=%d | n=%d" % (
             llm_h_clean, llm_h_off, agg["llm_ADV_ONKEY_hallucinated"],
             agg["substrate_CLEAN_hallucinated"], agg["substrate_ADV_OFFKEY_hallucinated"], immune,
             agg["llm_CLEAN_correct"], agg["llm_ADV_OFFKEY_correct"], agg["llm_ADV_ONKEY_correct"],
             diff, agg["n_queries_total"]))
    if diff > 0 and gap_off > 0.02:
        return ("GENUINE_DIFFERENTIATOR_FAITHFULNESS_GUARANTEE",
                "DIFFERENTIATOR OBSERVED: the LLM-reader hallucinates entities absent from the given "
                "evidence at a rate the substrate structurally cannot match (its answer is a codebook "
                "pointer). " + s)
    if llm_h_clean <= sub_h + 0.02 and llm_h_off <= sub_h + 0.02:
        return ("DIFFERENTIATOR_NOT_OBSERVED_GUARANTEE_VS_EMPIRICAL_PARITY",
                "NO hallucination gap at this scale/model: the competent LLM reader is empirically "
                "as faithful as the substrate is by-guarantee -> supports PIVOT (the edge is guarantee "
                "vs observed, not an observed capability delta). " + s)
    return ("MEASURED_MIXED",
            "Mixed: some hallucination signal but below the decisive threshold; report raw. " + s)


def main():
    od = get_output_dir(ANCHOR_NAME)
    _write_start_marker(od, len(SEEDS))
    print("[config] anchor=%s mode=%s model=%s N=%d max_triples=%d nq_target=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, MODEL_ID, N, MAX_TRIPLES, NQ_TARGET, SEEDS), flush=True)
    if not FB.exists():
        raise FileNotFoundError("FB15k-237 not found at %s" % FB)
    t0 = time.time()
    print("[load] loading reader %s ..." % MODEL_ID, flush=True)
    reader = Reader(MODEL_ID)
    print("[load] reader ready in %.1fs" % (time.time() - t0), flush=True)

    per_seed = []
    for seed in SEEDS:
        ts = time.time()
        r = run_seed(seed, reader)
        r["elapsed_s"] = time.time() - ts
        per_seed.append(r)
        print("[seed %d done] n=%d | llm_halluc off=%.3f clean=%.3f | sub_immune_off=%.3f | "
              "differentiator_offkey=%d | %.1fs" % (
                  seed, r["n_queries"], r["llm_ADV_OFFKEY"]["hallucinated"],
                  r["llm_CLEAN"]["hallucinated"], r["substrate_immune_offkey_rate"],
                  r["differentiator_offkey_count"], r["elapsed_s"]), flush=True)

    agg = _agg(per_seed)
    cardinality_ok = len(per_seed) == len(SEEDS)
    # discriminator-fires: the OFFKEY condition must actually exercise the substrate's selectivity
    # (substrate stays correct on >0 offkey cases) AND the LLM must be exercised (>0 generations).
    discriminator_fired = (agg["substrate_immune_offkey_rate_mean"] > 0.0 and agg["n_queries_total"] > 0)
    v, vmsg = verdict(agg)
    if not cardinality_ok:
        v, vmsg = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", "cardinality %d/%d" % (len(per_seed), len(SEEDS))
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "model_id": MODEL_ID, "n_seeds": len(SEEDS), "agg": agg, "per_seed": per_seed,
               "gates": {"cardinality_ok": cardinality_ok, "discriminator_fired": bool(discriminator_fired),
                         "external_measurement_only": True, "substrate_depends_on_llm": False},
               "elapsed_s": time.time() - t0}
    write_metrics(od, metrics, per_seed)
    print("[metrics] written -> %s" % (od / "metrics.json"), flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:500]),
                "summary": "CELL_CRASHED: %s" % type(e).__name__, "run_mode": RUN_MODE,
                "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
                "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
        _out.mkdir(parents=True, exist_ok=True)
        _tmp = _out / "metrics.json.tmp"
        _tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(_tmp, _out / "metrics.json")
        raise
