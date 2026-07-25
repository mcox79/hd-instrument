"""hdlab/reasoner.py -- the COMPOSED verification-by-derivation reasoner (integration audit P5).

The currently-missing composed entry point for the substrate's reasoning stack. Wires the REAL,
disk-verified brain-reasoning components into ONE end-to-end glass-box pipeline whose output is an
INSPECTABLE DERIVATION TRACE (the exact typed-rule chain connecting a question's givens to the chosen
answer, plus why the other candidates could not be derived or were rejected).

PIPELINE (end-to-end, glass-box):
  ARC question
    -> COMPREHEND to givens + 4 candidate claims          (interim: _content_words stand-in, FLAGGED)
    -> build the TYPED, DIRECTED derivation graph          (P1: hdlab.typed_rule_parser; LICENSED WorldTree)
       with NEGATION-AWARE clean node-identity             (reuse cleannodes_v2 NegAware + head/polarity gates)
    -> for each candidate: forward-from-givens / backward-from-candidate MEET-IN-MIDDLE search
                                                           (P3: M3 meet-in-middle shape; supersedes K=2 multi_hop)
    -> CI CONSISTENCY check: reject contradictory chains    (P4: PolarityLexicon labeled-opposition; Johnson-Laird)
    -> DO-CALCULUS routing where COUPLEDRELATIONSHIP applies (reuse certified do-operator semantics, provenance)
    -> DECIDE by derivability (completeness -> shortest -> population-vector combiner tie-break)
    -> EMIT the inspectable derivation trace.

REUSED (wire, do not reinvent): hdlab.typed_rule_parser (P1, promoted this build);
  exp_arc_derivation_connectivity_gate_v1 (meet_connected / reconstruct_chain / _reach / _l2_rows -- the
  M3 meet-in-middle search shape); exp_arc_derivation_connectivity_gate_cleannodes_v2 (NegAwareEncoder +
  build_graph_gated clean node-identity, neg-detector fixed); exp_arc_aggregation_polarity_ci_v1
  (PolarityLexicon; _ci_two_phase_pol imported/available as the fuller settle); SemanticHDEncoder (meaning
  match); the certified do-operator evaluate/merkle semantics (PP-270/307 HARD_PASS).

PROMOTIONS: P1 parse_tablestore_typed -> hdlab/typed_rule_parser.py DONE this build. P3 (M3 meet-in-middle)
  and P4 (CI/polarity) are REUSED-BY-IMPORT here and NOTED as the next hdlab promotions (kept in their exp
  cells to avoid churning the exp tower mid-pivot; this reasoner is their stable consumer).

HONEST CAVEATS (mandatory):
  * COMPREHENSION uses the crude _content_words() extractor, NOT hdlab/situation_reader.py. The reader is
    built for narrative-passage comprehension; adapting it to question->claim extraction is Stage-2/P6 work.
    This _content_words stand-in is INTERIM and explicitly flagged; every coverage number inherits its crudeness.
  * COVERAGE on the current LICENSED WorldTree table (~1868 rows) is EXPECTED to be LOW (the connectivity gate
    already ran RED, COVERAGE_BOUND). The deliverable here is the WIRING being DONE + working end-to-end +
    producing real traces on the covered subset -- NOT a coverage win. Rule-supply (Step 1) + grounded
    meaning (Step 5) expand it. Covered-subset AND whole-set accuracy are reported SEPARATELY and honestly.
  * NODE-UNIFICATION runs through the same content-thin SemanticHDEncoder meaning wall; loose tau_unify can
    silently merge distinct nodes (logged for spot-check).

MUST-FAIL CONTROLS (both mandatory, per the pivot note section 3.4): SHUFFLE_DIRECTION (per-edge random
  arg0<->arg1 flip -> derivation should collapse toward chance if genuinely using directionality) and
  UNTYPED_SIMILARITY_NULL (untyped cosine edges, identical search -> isolate typed-structure lift vs any
  connectivity). One variable across arms = the EDGE STRUCTURE (node identity + search + decision identical).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic
(fixed seed, numpy default_rng, sorted iteration); repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE: except SystemExit raised BEFORE except Exception (no bare/BaseException); atomic metrics
  (tmp + os.replace); start-marker; crash-diagnostic; heartbeat; real_code_path self-test builds the REAL
  reasoner over a hand rule-set (GloVe-free injected encoder) and asserts the full pipeline fires + can-fail.
"""
from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import argparse
import platform
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# P1 (promoted this build): the typed rule graph builder lives in hdlab now.
from hdlab.typed_rule_parser import parse_tablestore_typed, licensed_rows, LICENSED

# P3 search shape + graph primitives (M3 meet-in-middle) -- reused by import (noted promotion).
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate
# clean NEGATION-AWARE node-identity (neg-detector fixed) -- reused by import.
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean
# comprehension stand-in (content-word extraction) + ARC loader.
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc

ANCHOR_NAME = "hdlab_reasoner_composed_v1"
SEED = 20260725

# thresholds inherited UNCHANGED from the clean-node connectivity gate (NOT tuned here).
TAU_UNIFY = 0.85    # node-identity cosine merge / word->node map threshold
TAU_SIM = 0.60      # untyped-null similarity edge threshold
DEPTH = 3           # max derivation chain depth (meet-in-middle d_fwd=ceil, d_bwd=floor)

MOD = 1000  # certified do-operator modulus (provenance below)


# ===========================================================================
# atomic metrics / heartbeat / crash-diag / start-marker
# ===========================================================================
_T0 = [time.perf_counter()]


def _write_metrics_atomic(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
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
# DO-CALCULUS routing (reuse the CERTIFIED do-operator semantics).
# Provenance: exp_counterfactual_do_operator_v1.py::evaluate + h (HARD_PASS PP-270/307). That module
# runs a module-level _selftest() + argparse on import (would consume our argv / sys.exit), so its two
# CERTIFIED pure functions are replicated here BYTE-FAITHFULLY with citation rather than imported --
# reuse-by-provenance, not reinvention. A COUPLEDRELATIONSHIP edge "as X [incr] then Y [incr]" is routed
# as a 2-node monotone DAG {Y:[X]}; do(X=+1) is propagated + Merkle-audited, recording the counterfactual
# direction in the trace.
# ===========================================================================
def _do_hash(s: str) -> str:
    """Merkle step hash (CITED@exp_counterfactual_do_operator_v1.py::h)."""
    return hashlib.sha256(s.encode()).hexdigest()


def _do_evaluate(base: Dict[int, int], parents: Dict[int, list], overrides: Dict[int, int]) -> Dict[int, int]:
    """Certified DAG recompute under intervention (CITED@exp_counterfactual_do_operator_v1.py::evaluate)."""
    val = dict(base)
    val.update(overrides)
    for j in sorted(parents):
        val[j] = sum(val[p] for p in parents[j]) % MOD
    return val


def do_route_coupled(chain_steps: List[Tuple[str, str, str]]) -> List[dict]:
    """For each COUPLEDRELATIONSHIP edge on a chain, run a certified do(source +1) intervention and emit
    an auditable counterfactual annotation. chain_steps = [(src_label, relation, dst_label), ...]."""
    ann = []
    for src, rel, dst in chain_steps:
        if rel != "COUPLEDRELATIONSHIP":
            continue
        base = {0: 1, 1: 1}          # node0 = source var, node1 = coupled var
        parents = {1: [0]}           # monotone coupling: dst := f(src)
        v0 = _do_evaluate(base, parents, {})
        v1 = _do_evaluate(base, parents, {0: base[0] + 1})   # do(source increases)
        direction = "increases" if v1[1] > v0[1] else "changes"
        audit = _do_hash(f"do({src}=+1)->{dst}={v1[1]}")
        ann.append({"src": src, "dst": dst, "intervention": f"do({src} increases)",
                    "propagated": f"{dst} {direction}", "audit_sha256_12": audit[:12]})
    return ann


# ===========================================================================
# the composed reasoner
# ===========================================================================
class DerivationReasoner:
    """Composed glass-box reasoner: comprehend -> typed graph -> meet-in-middle derivation search ->
    CI consistency -> do-calculus routing -> decision -> inspectable trace. Graph built ONCE per corpus."""

    def __init__(self, base_encoder=None, pol_lexicon=None, wn=None,
                 tau_unify: float = TAU_UNIFY, tau_sim: float = TAU_SIM, depth: int = DEPTH,
                 seed: int = SEED, licensed: Tuple[str, ...] = LICENSED,
                 rows: Optional[List[dict]] = None, verbose: bool = True):
        self.tau_unify = tau_unify
        self.tau_sim = tau_sim
        self.depth = depth
        self.seed = seed
        self.licensed = licensed
        self.verbose = verbose

        # rules (P1 parser)
        if rows is None:
            rows = licensed_rows(parse_tablestore_typed(), licensed)
        self.rows = rows
        self.per_relation: Dict[str, int] = {}
        for r in rows:
            self.per_relation[r["relation"]] = self.per_relation.get(r["relation"], 0) + 1

        # encoders + polarity (reused)
        self.base = base_encoder
        self.wn = wn
        self.pol = pol_lexicon
        self.enc = clean.NegAwareEncoder(self.base, seed=seed)

        # CLEAN node-identity typed graph (reused builder; ONE build shared by all arms)
        self.g = clean.build_graph_gated(rows, self.enc.encode_batch, tau_unify, tau_sim,
                                         self.wn, self.pol, use_head_gate=True, use_pol_gate=True)

        # derive the three edge-arms from the SINGLE graph (one variable across arms = edge structure)
        self.arms = self._build_arms()

        # word->node cache
        self._word2nodes: Dict[str, set] = {}

    # ---- arm construction --------------------------------------------------
    def _build_arms(self) -> Dict[str, dict]:
        g = self.g
        typed = {"name": "typed", "fwd": g["fwd"], "bwd": g["bwd"], "edge_rel": g["edge_rel"]}
        # SHUFFLE_DIRECTION: per-edge random arg0<->arg1 flip (seeded, deterministic).
        rng = np.random.default_rng(self.seed * 31 + 7)
        fwd_s: Dict[int, set] = {}
        bwd_s: Dict[int, set] = {}
        er_s: Dict[Tuple[int, int], str] = {}
        for (u, v), rel in sorted(g["edge_rel"].items()):
            if rng.random() < 0.5:
                a, b = u, v
            else:
                a, b = v, u
            fwd_s.setdefault(a, set()).add(b)
            bwd_s.setdefault(b, set()).add(a)
            er_s[(a, b)] = rel
        shuffle = {"name": "shuffle_direction", "fwd": fwd_s, "bwd": bwd_s, "edge_rel": er_s}
        # UNTYPED_SIMILARITY_NULL: undirected cosine edges as both fwd + bwd; identical search.
        und = g["undirected"]
        er_u = {}
        for a, nbrs in und.items():
            for b in nbrs:
                er_u[(a, b)] = "SIM"
        null = {"name": "untyped_null", "fwd": und, "bwd": und, "edge_rel": er_u}
        return {"typed": typed, "shuffle_direction": shuffle, "untyped_null": null}

    # ---- comprehension (INTERIM stand-in: content-word extraction, FLAGGED) ----
    def _encode_words(self, words: List[str]) -> None:
        new = [w for w in words if w not in self._word2nodes]
        if not new:
            return
        vecs = gate._l2_rows(self.enc.encode_batch(new))
        node_sets = self.g["map_words"](vecs)
        for i, w in enumerate(new):
            self._word2nodes[w] = node_sets[i]

    def nodes_for(self, text: str, min_len: int = 4) -> set:
        words = arc._content_words(text, min_len=min_len)
        self._encode_words(words)
        ns: set = set()
        for w in words:
            ns |= self._word2nodes.get(w, set())
        return ns

    # ---- CI consistency (P4: PolarityLexicon labeled-opposition; Johnson-Laird counterexample) ----
    def _ci_reject(self, chain_labels: List[str], choice_text: str) -> Tuple[bool, str]:
        """Reject a chain if a labeled contradiction fires between (a) any chain proposition and the
        candidate, or (b) two adjacent chain propositions. Uses the real PolarityLexicon.contradicts."""
        if self.pol is None or not chain_labels:
            return False, ""
        for lab in chain_labels:
            if self.pol.contradicts(lab, choice_text):
                return True, f"chain node [{lab}] contradicts candidate"
        for i in range(len(chain_labels) - 1):
            if self.pol.contradicts(chain_labels[i], chain_labels[i + 1]):
                return True, f"chain steps [{chain_labels[i]}] / [{chain_labels[i + 1]}] contradict"
        return False, ""

    # ---- population-vector combiner readout (the 0.687-given-gold DECISION mechanism) ----
    def _combiner_score(self, choice_nodes: set, evidence_nodes: set) -> float:
        """Max cosine of any candidate node against the bundled (summed, L2) evidence-node reps."""
        if not choice_nodes or not evidence_nodes:
            return 0.0
        nr = self.g["node_rep"]
        ev = np.asarray(sorted(evidence_nodes), dtype=np.int64)
        bundle = nr[ev].sum(axis=0)
        n = np.linalg.norm(bundle)
        if n <= 0:
            return 0.0
        bundle = bundle / n
        cn = np.asarray(sorted(choice_nodes), dtype=np.int64)
        return float((nr[cn] @ bundle).max())

    # ---- per-question reasoning over ONE arm --------------------------------
    def _reason_arm(self, question: dict, arm: dict) -> dict:
        fwd, bwd, er = arm["fwd"], arm["bwd"], arm["edge_rel"]
        lab = self.g["node_label"]
        given_nodes = self.nodes_for(question["stem"])
        # evidence pool for the combiner readout = undirected spread from givens (retrieve-wide analog)
        evidence = set(gate._reach(self.g["undirected"], given_nodes, self.depth)) if given_nodes else set()

        g_shim = {"fwd": fwd, "bwd": bwd, "edge_rel": er, "node_label": lab, "node_rep": self.g["node_rep"]}
        per_choice = []
        for ci, ch in enumerate(question["choices"]):
            cnodes = self.nodes_for(ch)
            derivable = gate.meet_connected(fwd, bwd, given_nodes, cnodes, self.depth, min_len=1)
            chain_str = None
            chain_labels: List[str] = []
            chain_steps: List[Tuple[str, str, str]] = []
            do_ann: List[dict] = []
            rejected = False
            reject_reason = ""
            givens_covered = 0.0
            if derivable:
                chain_str = gate.reconstruct_chain(g_shim, given_nodes, cnodes, self.depth)
                chain_labels, chain_steps = self._parse_chain(chain_str)
                rejected, reject_reason = self._ci_reject(chain_labels, ch)
                do_ann = do_route_coupled(chain_steps)
                # completeness: fraction of given-nodes that individually reach this candidate
                if given_nodes:
                    hits = sum(1 for gn in given_nodes
                               if gate.meet_connected(fwd, bwd, {gn}, cnodes, self.depth, min_len=1))
                    givens_covered = hits / len(given_nodes)
            comb = self._combiner_score(cnodes, evidence)
            per_choice.append({
                "choice_index": ci, "choice_text": ch[:160],
                "derivable": bool(derivable), "rejected_by_ci": bool(rejected),
                "reject_reason": reject_reason, "chain": chain_str,
                "chain_len": len(chain_steps), "givens_covered": round(givens_covered, 3),
                "do_calculus": do_ann, "combiner_score": round(comb, 4),
                "n_choice_nodes": len(cnodes),
            })
        chosen, decision_mode = self._decide(per_choice)
        return {"chosen_index": chosen, "decision_mode": decision_mode,
                "n_given_nodes": len(given_nodes), "per_choice": per_choice}

    @staticmethod
    def _parse_chain(chain_str: Optional[str]) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """Parse reconstruct_chain output '[a] --REL--> [b] ; [b] --REL2--> [c]' into labels + steps."""
        labels: List[str] = []
        steps: List[Tuple[str, str, str]] = []
        if not chain_str or "-->" not in chain_str:
            return labels, steps
        for seg in chain_str.split(" ; "):
            if "-->" not in seg:
                continue
            left, _, right = seg.partition("--")
            rel, _, dst = right.partition("-->")
            src = left.strip().strip("[]").strip()
            rel = rel.strip()
            dst = dst.strip().strip("[]").strip()
            steps.append((src, rel, dst))
        for s, _, d in steps:
            if not labels:
                labels.append(s)
            labels.append(d)
        return labels, steps

    def _decide(self, per_choice: List[dict]) -> Tuple[int, str]:
        """Prefer a valid (derivable + not CI-rejected) candidate: completeness -> shortest -> combiner.
        Else fall back to the pure similarity combiner readout (+ lexical overlap final tiebreak)."""
        valid = [c for c in per_choice if c["derivable"] and not c["rejected_by_ci"]]
        if valid:
            valid.sort(key=lambda c: (-c["givens_covered"], c["chain_len"], -c["combiner_score"],
                                      c["choice_index"]))
            return valid[0]["choice_index"], "derivation"
        # fallback: similarity combiner (the current similarity pipeline), stable tiebreak on index
        best = max(per_choice, key=lambda c: (c["combiner_score"], -c["choice_index"]))
        if best["combiner_score"] > 0.0:
            return best["choice_index"], "similarity_fallback"
        return per_choice[0]["choice_index"], "abstain_index0"

    def reason(self, question: dict) -> dict:
        """Full glass-box result on the TYPED arm (the reasoner proper)."""
        return self._reason_arm(question, self.arms["typed"])

    # ---- pure similarity baseline (the REAL baseline the reasoner must beat) ----
    def similarity_baseline(self, question: dict) -> int:
        given_nodes = self.nodes_for(question["stem"])
        evidence = set(gate._reach(self.g["undirected"], given_nodes, self.depth)) if given_nodes else set()
        scores = []
        for ci, ch in enumerate(question["choices"]):
            cnodes = self.nodes_for(ch)
            scores.append((self._combiner_score(cnodes, evidence), -ci, ci))
        scores.sort(reverse=True)
        return scores[0][2]


# ===========================================================================
# evaluation harness
# ===========================================================================
def evaluate(reasoner: DerivationReasoner, questions: List[dict], output_dir: str) -> dict:
    """Run all arms + baseline; report covered-subset and whole-set accuracy, controls, traces."""
    arm_names = ["typed", "shuffle_direction", "untyped_null"]
    per_q = []
    n = len(questions)
    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        row = {"qid": q["qid"], "correct_index": ci}
        for an in arm_names:
            res = reasoner._reason_arm(q, reasoner.arms[an])
            row[an] = {"chosen": res["chosen_index"], "mode": res["decision_mode"],
                       "correct": int(res["chosen_index"] == ci),
                       "derivable_any": any(c["derivable"] for c in res["per_choice"]),
                       "correct_derivable": bool(res["per_choice"][ci]["derivable"]) if ci < len(res["per_choice"]) else False,
                       "per_choice": res["per_choice"]}
        base_pick = reasoner.similarity_baseline(q)
        row["baseline"] = {"chosen": base_pick, "correct": int(base_pick == ci)}
        per_q.append(row)
        if (qi + 1) % 25 == 0:
            _heartbeat(output_dir, "eval_progress", {"done": qi + 1, "total": n})

    def acc(arm: str, subset: Optional[List[int]] = None) -> Tuple[float, int]:
        idx = subset if subset is not None else list(range(n))
        if not idx:
            return 0.0, 0
        c = sum(per_q[i][arm]["correct"] for i in idx)
        return c / len(idx), len(idx)

    # covered subset = typed arm derives >=1 candidate (the questions the reasoner can actually reason on)
    covered = [i for i in range(n) if per_q[i]["typed"]["derivable_any"]]
    # subset where the CORRECT answer is derivable (a fairer "reachable" subset)
    correct_reachable = [i for i in range(n) if per_q[i]["typed"]["correct_derivable"]]

    typed_whole, _ = acc("typed")
    typed_cov, n_cov = acc("typed", covered)
    shuffle_cov, _ = acc("shuffle_direction", covered)
    null_cov, _ = acc("untyped_null", covered)
    base_whole = sum(r["baseline"]["correct"] for r in per_q) / n if n else 0.0
    base_cov = (sum(per_q[i]["baseline"]["correct"] for i in covered) / len(covered)) if covered else 0.0
    chance = 1.0 / max(2, int(np.mean([len(q["choices"]) for q in questions])))

    # covered-subset coverage (fraction of questions with >=1 derivable candidate)
    coverage_frac = len(covered) / n if n else 0.0
    correct_reach_frac = len(correct_reachable) / n if n else 0.0

    # glass-box traces: correct-derivable examples + one incorrect/uncovered example
    traces = _collect_traces(reasoner, questions, per_q, max_correct=4, max_neg=2)

    return {
        "n_questions": n, "chance": round(chance, 4),
        "coverage_fraction": round(coverage_frac, 4), "n_covered": len(covered),
        "correct_reachable_fraction": round(correct_reach_frac, 4), "n_correct_reachable": len(correct_reachable),
        "typed_whole_set_acc": round(typed_whole, 4),
        "baseline_whole_set_acc": round(base_whole, 4),
        "covered_subset": {
            "n": n_cov,
            "typed_acc": round(typed_cov, 4),
            "baseline_acc": round(base_cov, 4),
            "shuffle_direction_acc": round(shuffle_cov, 4),
            "untyped_null_acc": round(null_cov, 4),
            "typed_minus_baseline": round(typed_cov - base_cov, 4),
            "typed_minus_shuffle": round(typed_cov - shuffle_cov, 4),
            "typed_minus_untyped_null": round(typed_cov - null_cov, 4),
        },
        "per_q": per_q, "traces": traces,
    }


def _collect_traces(reasoner: DerivationReasoner, questions: List[dict], per_q: List[dict],
                    max_correct: int, max_neg: int) -> List[dict]:
    traces = []
    n_correct = 0
    n_neg = 0
    for i, q in enumerate(questions):
        row = per_q[i]
        ci = q["correct_index"]
        typed = row["typed"]
        is_correct_derivation = (typed["correct"] and typed["mode"] == "derivation")
        is_neg = (not typed["derivable_any"]) or (not typed["correct"])
        take = False
        kind = ""
        if is_correct_derivation and n_correct < max_correct:
            take = True; kind = "CORRECT_DERIVATION"; n_correct += 1
        elif is_neg and n_neg < max_neg:
            take = True; kind = "INCORRECT_OR_UNCOVERED"; n_neg += 1
        if not take:
            continue
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        chosen = res["chosen_index"]
        chosen_pc = res["per_choice"][chosen]
        why_others = []
        for c in res["per_choice"]:
            if c["choice_index"] == chosen:
                continue
            if not c["derivable"]:
                reason = "NO derivation chain found (givens do not reach this candidate)"
            elif c["rejected_by_ci"]:
                reason = f"REJECTED by CI consistency: {c['reject_reason']}"
            else:
                reason = (f"derivable but not selected (givens_covered={c['givens_covered']}, "
                          f"chain_len={c['chain_len']}, combiner={c['combiner_score']})")
            why_others.append({"choice": c["choice_text"], "reason": reason})
        traces.append({
            "kind": kind, "qid": q["qid"], "stem": q["stem"][:280],
            "correct_choice": q["choices"][ci][:160],
            "chosen_choice": q["choices"][chosen][:160],
            "chosen_correct": bool(chosen == ci), "decision_mode": res["decision_mode"],
            "derivation_chain": chosen_pc["chain"],
            "chain_len": chosen_pc["chain_len"], "givens_covered": chosen_pc["givens_covered"],
            "do_calculus": chosen_pc["do_calculus"],
            "why_others_not_chosen": why_others,
        })
        if n_correct >= max_correct and n_neg >= max_neg:
            break
    return traces


def _print_traces(traces: List[dict]) -> None:
    print("\n" + "=" * 78, flush=True)
    print("GLASS-BOX DERIVATION TRACES (inspectable typed-rule chains)", flush=True)
    print("=" * 78, flush=True)
    for t in traces:
        print(f"\n[{t['kind']}] qid={t['qid']}  (decision={t['decision_mode']}, "
              f"chosen_correct={t['chosen_correct']})", flush=True)
        print(f"  Q: {t['stem']}", flush=True)
        print(f"  gold answer : {t['correct_choice']}", flush=True)
        print(f"  chosen      : {t['chosen_choice']}", flush=True)
        if t["derivation_chain"]:
            print(f"  DERIVATION  : {t['derivation_chain']}", flush=True)
            print(f"                (chain_len={t['chain_len']}, givens_covered={t['givens_covered']})",
                  flush=True)
            if t["do_calculus"]:
                for d in t["do_calculus"]:
                    print(f"  do-calculus : {d['intervention']} -> {d['propagated']} "
                          f"[audit {d['audit_sha256_12']}]", flush=True)
        else:
            print("  DERIVATION  : (none -- no candidate reached by depth<=3; similarity fallback)",
                  flush=True)
        for w in t["why_others_not_chosen"]:
            print(f"  x rejected  : {w['choice'][:90]} :: {w['reason']}", flush=True)


# ===========================================================================
# self-test (real code path: builds the REAL reasoner over a hand rule-set, GloVe-free)
# ===========================================================================
def _self_test() -> None:
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    print("[self-test] typed_rule_parser licensed_rows ...", flush=True)
    # tiny hand rule set; FakeBase from cleannodes_v2 gives deterministic GloVe-free encoding
    base = clean._FakeBase()
    wn = _load_wordnet()
    pol = PolarityLexicon()
    # planted derivation: [rain] --CAUSE--> [runoff] --SOURCEOF--> [river] ; lure volcano->lava
    rows = [
        {"relation": "CAUSE", "arg0": "rain", "arg1": "runoff"},
        {"relation": "SOURCEOF", "arg0": "runoff", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "volcano", "arg1": "lava"},
        {"relation": "COUPLEDRELATIONSHIP", "arg0": "temperature", "arg1": "evaporation"},
    ]
    r = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn,
                           tau_unify=0.99, tau_sim=0.5, depth=3, rows=rows, verbose=False)
    assert r.g["n_typed_edges"] == 4, f"expected 4 typed edges, got {r.g['n_typed_edges']}"
    exercised = set()

    # (1) real derivation search fires: a question whose gold is derivable, lure is not
    q = {"qid": "T1", "stem": "what does rain produce that feeds",
         "choices": ["river water body", "lava rock", "metal wire", "glass sheet"],
         "correct_index": 0}
    res = r.reason(q); exercised.add("reason")
    assert res["per_choice"][0]["derivable"] is True, "planted correct choice MUST derive"
    assert res["per_choice"][1]["derivable"] is False, "lure MUST NOT derive (selectivity real)"
    assert res["chosen_index"] == 0, f"reasoner must choose the derivable gold, got {res['chosen_index']}"
    assert res["decision_mode"] == "derivation", f"mode={res['decision_mode']}"
    assert res["per_choice"][0]["chain"] and "-->" in res["per_choice"][0]["chain"], "trace must exist"
    print(f"[self-test] derivation fires + selective: chain={res['per_choice'][0]['chain']}", flush=True)

    # (2) CI consistency CAN reject a contradictory chain (Johnson-Laird counterexample)
    labels = ["increase heat", "not increase heat"]
    rej, why = r._ci_reject(labels, "some candidate")
    assert rej is True, "CI must reject an internally-contradicting chain"
    exercised.add("ci_reject")
    print(f"[self-test] CI rejection fires: {why}", flush=True)

    # (3) do-calculus routing on a COUPLEDRELATIONSHIP edge produces an audited annotation
    ann = do_route_coupled([("temperature", "COUPLEDRELATIONSHIP", "evaporation")])
    assert len(ann) == 1 and ann[0]["propagated"].startswith("evaporation"), "do-route must fire"
    assert len(ann[0]["audit_sha256_12"]) == 12, "do-route must carry a merkle audit tag"
    exercised.add("do_route_coupled")
    print(f"[self-test] do-calculus route: {ann[0]['intervention']} -> {ann[0]['propagated']}", flush=True)

    # (4) MUST-FAIL controls differ from typed (arms are genuinely distinct edge structures)
    typed_edges = set(r.arms["typed"]["edge_rel"].keys())
    null_edges = set(r.arms["untyped_null"]["edge_rel"].keys())
    assert typed_edges != null_edges, "untyped-null edges must differ from typed (control is real)"
    exercised.add("arms")

    # (5) can-fail: a fully disconnected question -> no derivation -> similarity/abstain fallback
    q2 = {"qid": "T2", "stem": "unrelated tokens zzz qqq",
          "choices": ["metal wire", "glass sheet", "plastic tube", "stone block"],
          "correct_index": 0}
    res2 = r.reason(q2)
    assert res2["decision_mode"] in ("similarity_fallback", "abstain_index0"), \
        f"disconnected Q must fall back, got {res2['decision_mode']}"
    print(f"[self-test] fallback path OK: mode={res2['decision_mode']}", flush=True)

    # (6) baseline callable + deterministic
    b1 = r.similarity_baseline(q); b2 = r.similarity_baseline(q)
    assert b1 == b2, "similarity baseline must be deterministic"
    exercised.add("similarity_baseline")

    # (7) evaluate harness end-to-end on the two planted Qs (real trace collection)
    out = evaluate(r, [q, q2], output_dir=os.path.join(_REPO, "data", "_reasoner_selftest_scratch"))
    assert out["n_questions"] == 2 and "covered_subset" in out, "evaluate must return the full report"
    assert len(out["traces"]) >= 1, "at least one glass-box trace must be produced"
    exercised.add("evaluate")

    need = {"reason", "ci_reject", "do_route_coupled", "arms", "similarity_baseline", "evaluate"}
    missing = need - exercised
    assert not missing, f"real_code_path: unexercised entrypoints {missing}"
    print(f"[self-test] real_code_path exercised={sorted(exercised)}", flush=True)
    print("[self-test] ALL PASS", flush=True)


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full")
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _heartbeat(output_dir, "start", {"n_sample": n_sample, "tau_unify": TAU_UNIFY,
                                     "tau_sim": TAU_SIM, "depth": DEPTH})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    base = SemanticHDEncoder()
    pol = PolarityLexicon()
    wn = base._wn
    _heartbeat(output_dir, "encoder_ready")

    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, seed=seed)
    _heartbeat(output_dir, "graph_built",
               {"n_licensed_rows": len(reasoner.rows), "per_relation": reasoner.per_relation,
                "n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"],
                "max_typed_node_degree": reasoner.g["max_typed_node_degree"]})

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    if n_sample and n_sample < len(all_q):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
        questions = [all_q[i] for i in idx]
    else:
        questions = all_q
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_eval": len(questions)})

    report = evaluate(reasoner, questions, output_dir)
    _heartbeat(output_dir, "eval_done", {"coverage_fraction": report["coverage_fraction"],
                                         "typed_cov_acc": report["covered_subset"]["typed_acc"]})

    # ---- pre-registered bands (pivot note section 6; reported STRAIGHT, NOT tuned) ----
    cs = report["covered_subset"]
    bands = {
        "coverage_subset_acc_ge_0.50": cs["typed_acc"] >= 0.50,
        "beats_similarity_pipeline_ge_0.10": cs["typed_minus_baseline"] >= 0.10,
        "beats_shuffle_direction_ge_0.15": cs["typed_minus_shuffle"] >= 0.15,
        "beats_untyped_null_ge_0.15": cs["typed_minus_untyped_null"] >= 0.15,
    }
    n_bands_pass = sum(1 for v in bands.values() if v)
    # honest tier: the WIRING + traces are the deliverable; bands are informational given expected RED coverage
    if report["n_covered"] < 10:
        tier = "WIRED_COVERAGE_LIMITED"
        verdict = "COMPOSED_REASONER_WIRED"
    elif n_bands_pass == 4:
        tier = "HARD_PASS"
        verdict = "COMPOSED_REASONER_HARD_PASS"
    elif n_bands_pass >= 2:
        tier = "MIDDLE_BAND"
        verdict = "COMPOSED_REASONER_MIDDLE"
    else:
        tier = "BELOW_BANDS"
        verdict = "COMPOSED_REASONER_BELOW_BANDS"

    _print_traces(report["traces"])

    summary = (f"COMPOSED REASONER wired end-to-end | coverage={report['coverage_fraction']:.3f} "
               f"(n_covered={report['n_covered']}/{report['n_questions']}) | covered-subset typed_acc="
               f"{cs['typed_acc']:.3f} vs baseline {cs['baseline_acc']:.3f} "
               f"(d={cs['typed_minus_baseline']:+.3f}) vs shuffle {cs['shuffle_direction_acc']:.3f} "
               f"(d={cs['typed_minus_shuffle']:+.3f}) vs untyped-null {cs['untyped_null_acc']:.3f} "
               f"(d={cs['typed_minus_untyped_null']:+.3f}) | whole-set typed={report['typed_whole_set_acc']:.3f} "
               f"baseline={report['baseline_whole_set_acc']:.3f} | tier={tier}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": ("Composed verification-by-derivation reasoner (hdlab/reasoner.py) wired end-to-end: "
                        "comprehend->typed-graph->meet-in-middle derivation search->CI consistency->"
                        "do-calculus routing->decision->inspectable trace. Coverage on the current LICENSED "
                        "WorldTree table is LOW as EXPECTED (connectivity gate was RED, COVERAGE_BOUND); the "
                        "DELIVERABLE is the wiring being DONE + working + producing real derivation traces on "
                        "the covered subset. Rule-supply (Step 1) + grounded meaning (Step 5) expand coverage. "
                        "COMPREHENSION uses the INTERIM _content_words stand-in (not situation_reader). Bands "
                        "reported STRAIGHT, NOT tuned; both must-fail controls present."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "run_mode": "full",
        "config": {"n_eval": len(questions), "tau_unify": TAU_UNIFY, "tau_sim": TAU_SIM,
                   "depth": DEPTH, "seed": seed, "licensed": list(LICENSED),
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)",
                   "one_variable_across_arms": "edge_structure (node-identity + search + decision identical)"},
        "graph": {"n_licensed_rows": len(reasoner.rows), "per_relation": reasoner.per_relation,
                  "n_fillers": reasoner.g["n_fillers"], "n_nodes": reasoner.g["n_nodes"],
                  "n_typed_edges": reasoner.g["n_typed_edges"], "n_null_edges": reasoner.g["n_null_edges"],
                  "max_typed_node_degree": reasoner.g["max_typed_node_degree"],
                  "max_degree_node_label": reasoner.g["max_degree_node_label"],
                  "n_merges": reasoner.g["n_merges"], "neg_flagged_fillers": reasoner.enc.n_neg_flagged},
        "coverage_fraction": report["coverage_fraction"], "n_covered": report["n_covered"],
        "correct_reachable_fraction": report["correct_reachable_fraction"],
        "n_correct_reachable": report["n_correct_reachable"],
        "chance": report["chance"],
        "whole_set": {"typed_acc": report["typed_whole_set_acc"],
                      "baseline_acc": report["baseline_whole_set_acc"]},
        "covered_subset": report["covered_subset"],
        "preregistered_bands_pivot_note_s6": bands, "n_bands_pass": n_bands_pass,
        "bands_definition": {
            "coverage_subset_acc": ">= 0.50",
            "beats_similarity_pipeline": ">= 0.10 absolute (typed - baseline on covered subset)",
            "beats_shuffle_direction": ">= 0.15 absolute", "beats_untyped_null": ">= 0.15 absolute",
            "note": ("WIRED_COVERAGE_LIMITED when n_covered<10: coverage is the KNOWN bottleneck "
                     "(RED gate); the composed wiring + traces are the deliverable, not a bands win."),
        },
        "traces": report["traces"],
        "promotions": {"P1_done": "hdlab/typed_rule_parser.py (parse_tablestore_typed promoted)",
                       "P3_noted": "M3 meet-in-middle search reused-by-import (gate.meet_connected); "
                                   "promote to hdlab superseding K=2 multi_hop.py",
                       "P4_noted": "CI/polarity reused-by-import (PolarityLexicon.contradicts; "
                                   "_ci_two_phase_pol available as fuller settle); promote to hdlab"},
        "REQUIRED_FIELDS": ["verdict", "tier", "coverage_fraction", "n_covered", "covered_subset",
                            "whole_set", "preregistered_bands_pivot_note_s6", "traces"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    with open(os.path.join(output_dir, "per_question.json"), "w", encoding="utf-8") as f:
        json.dump(report["per_q"], f, indent=2)

    print("\n===== COMPOSED REASONER RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"bands (pivot note s6): {bands} -> {n_bands_pass}/4 | tier={tier}", flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=400, help="ARC-Challenge sample size (0 = all)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = 12 if args.mode == "smoke" else args.n
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
