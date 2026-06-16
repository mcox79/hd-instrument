"""SKUNKWORKS: self-reasoning accuracy scorecard -- measures how well the substrate recovers its
OWN operator families by traversing its live grounding graph, scored against a FROZEN textbook
ground truth. Designed to drive LEGITIMATE improvement, not a gameable number:

  - Ground truth is FROZEN textbook families (below); do NOT edit it to match results.
  - Method is FIXED + documented: direct 1-hop math DEPENDS_ON foundations, Jaccard, tau=0.3.
    (transitive closure floods with universal axioms -> useless; direct 1-hop is the honest signal.)
  - Two-sided guard: F1 rises ONLY when real grounding edges connect SAME-family operators
    (recall up) WITHOUT connecting different-family operators (precision down). You cannot cheat
    recall by adding wrong edges -- precision drops and the scorecard flags it.
  - Outputs the ACTIONABLE GAPS: same-family operator pairs not yet connected (-> the next real
    math-grounding to add) and any FALSE cross-family groupings (-> wrong edges to remove).
  - Appends a history entry per run (--tag) so improvement is tracked across iterations.

Circularity caveat (honest): the GT families + some grounding edges were both authored by skunkworks.
The legitimate signal is that F1 only improves with REAL, textbook-correct grounding that an
independent reviewer would also author; the GT is standard operator taxonomy, not tuned to results.

Usage: python tools/substrate_self_reasoning_scorecard.py --tag iter0_baseline
"""
from __future__ import annotations
import json, itertools, argparse
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SI = REPO / "data/substrate_index"
OUT = SI / "bench_reports" / "self_reasoning_scorecard.json"
TAU = 0.3  # FIXED. do not tune to inflate.

# FROZEN textbook operator families (standard taxonomy). Do not edit to match results.
GT = {
 'binding': ['fhrr_bind','fhrr_unbind','circular_convolution','role_filler_binding','context_binding','discrete_fourier_transform','permutation_indexed_binding'],
 'memory': ['cleanup','cosine_cleanup','modern_hopfield_ramsauer','sparse_distributed_memory','resonator_network_decoder'],
 'optimization': ['gradient_descent','adam_optimizer','stochastic_gradient_descent','policy_gradient'],
 'inference': ['bayesian_inference','em_algorithm','hmm_transition','markov_chain','mcmc_sampling','count_nb','bayes_rule'],
 'discriminative': ['discriminative_perceptron','perceptron_update','pca_whitening','zca_whitening','cosine_similarity'],
 'search': ['astar','beam_search','dijkstra'],
 'sequence_dp': ['forward_algorithm','backward_algorithm','viterbi_decoder'],
 'rl': ['markov_decision_process','q_learning','bellman_equation'],
}
OP2FAM = {o: f for f, os in GT.items() for o in os}
MATHY = lambda t: t.startswith(('T0/','T1/','T2/','T3/')) or 'axiom' in t


def load_rel():
    def norm(x): return x.split('::')[-1]
    rel = defaultdict(list)
    for c in ['meta','math','concept','science','methodology','school']:
        f = SI / c / 'relations.jsonl'
        if f.exists():
            for l in f.read_text(encoding='utf-8', errors='ignore').splitlines():
                if l.strip():
                    r = json.loads(l); rel[norm(r['src_id'])].append((r['rel_type'], norm(r['tgt_id'])))
    return rel


def score(rel):
    def fid(s):
        for k in rel:
            if k.split('/')[-1] == s: return k
        return None
    ops = [o for o in OP2FAM if fid(o)]
    direct = {o: {t for rt, t in rel.get(fid(o), []) if rt == 'DEPENDS_ON' and MATHY(t)} for o in ops}
    tp = fp = fn = 0
    recall_gaps = []   # same-family pairs NOT grouped -> add grounding
    precision_violations = []  # diff-family pairs grouped -> wrong edges
    fam_hit = defaultdict(lambda: [0, 0])
    for a, b in itertools.combinations(ops, 2):
        u = direct[a] | direct[b]; j = len(direct[a] & direct[b]) / len(u) if u else 0.0
        ps = j >= TAU; gs = OP2FAM[a] == OP2FAM[b]
        if gs: fam_hit[OP2FAM[a]][1] += 1; fam_hit[OP2FAM[a]][0] += int(ps)
        if ps and gs: tp += 1
        elif ps and not gs: fp += 1; precision_violations.append((a, b, round(j, 2)))
        elif (not ps) and gs: fn += 1; recall_gaps.append((a, b))
    p = tp/(tp+fp) if tp+fp else 0.0; r = tp/(tp+fn) if tp+fn else 0.0
    f1 = 2*p*r/(p+r) if p+r else 0.0
    return {'n_ops': len(ops), 'precision': round(p,3), 'recall': round(r,3), 'f1': round(f1,3),
            'recall_gaps': recall_gaps, 'precision_violations': precision_violations,
            'per_family_recall': {k: f'{v[0]}/{v[1]}' for k, v in fam_hit.items()}}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tag', default='untagged'); a = ap.parse_args()
    s = score(load_rel())
    hist = json.loads(OUT.read_text()) if OUT.exists() else {'method': 'direct-1hop-math-foundations Jaccard', 'tau': TAU, 'history': []}
    hist['history'].append({'tag': a.tag, 'precision': s['precision'], 'recall': s['recall'], 'f1': s['f1'], 'n_ops': s['n_ops']})
    OUT.write_text(json.dumps(hist, indent=2))
    print(f"SELF-REASONING SCORECARD [{a.tag}]  P={s['precision']} R={s['recall']} F1={s['f1']} (n={s['n_ops']}, tau={TAU})")
    print('per-family recall (same-family pairs correctly grouped):')
    for k, v in s['per_family_recall'].items(): print(f'  {k:16s} {v}')
    if s['precision_violations']:
        print(f"PRECISION VIOLATIONS (wrong groupings -> remove bad edges): {s['precision_violations'][:5]}")
    print(f"TOP RECALL GAPS (same-family, not connected -> ADD grounding): {[(x[0],x[1]) for x in s['recall_gaps'][:8]]}")
    print(f"history: {len(hist['history'])} entries in {OUT}")


if __name__ == '__main__':
    main()
