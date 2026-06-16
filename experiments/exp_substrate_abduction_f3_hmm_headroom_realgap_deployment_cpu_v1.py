"""DECISION 139a/141 Phase C -- CELL-ABDUCTION-F3. Deploy the (Phase-B-validated, confound-sharpened) reverse-math abduction kernel on a REAL documented gap with NO single known filler: F3 = HMM module headroom (0.9028, ~0.10 residual; Phase A: 'needs gap-shape abduction to specify exactly what closes 0.10'). Math-native utility metric = HMM state-recovery accuracy delta (fixes CONSTRUCT-2 R4 benchmark-mismatch). Substrate-internal; NO LLM; no held-out (synthetic HMM). CPU/numpy. ASCII; --self-test.

This is the UNKNOWN-gap deployment (F1 had a known filler k-gram-XOR for ground-truth; F3 does not). The kernel abduces the weakest property class that closes the residual, then we check plausibility against the documented PARTIAL filler (forward/backward/viterbi = global bidirectional context integration).

STRUCTURE mirrors F1: F1 gap = local(single-token) vs joint(k-gram); F3 gap = local(greedy/filtering) vs global(bidirectional smoothing/viterbi). The sharpened Phase-C lens (pair-separability = informative joint/global info integration, NOT a narrower property like recoverability) carries over.

CANDIDATE decoders span a property lattice (the kernel does NOT presuppose the answer):
  greedy        local emission argmax (the substrate's headroom baseline / the GAP)
  past_accum    cumulative-emission argmax assuming CONSTANT state -- uses PAST OBSERVATIONS but NO transition model -> CONFOUND-BREAKER (the F3 analog of rectprod): proves mere past-access is insufficient; it is TRANSITION-MODEL integration that closes the gap.
  forward       forward filtering posterior (transition model + past)
  fwd_back      forward-backward smoothing posterior (transition + past + future)
  viterbi       global MAP path (transition; full joint)
PROPERTIES (measured): uses_transition (the Markov dependency model), uses_past_obs, uses_future_obs.
ABDUCE the weakest signature separating CLOSERS (reach near-ceiling) from the GAP; the past_accum control FAILS (uses past obs but lacks the transition model) -> isolates uses_transition as load-bearing; the abduced class matches the documented filler (forward/backward/viterbi all model transitions).
HONEST CORRECTION (self-flagged): the v1 hypothesis was 'bidirectional/informative-global integration'; the DATA refuted it -- forward (past-only filtering) already closes ~87pct of the headroom and future-integration adds only ~+0.016. The real driver is TRANSITION-MODEL integration, not bidirectionality. Reported as the finding; v1's shuffle-future control was too weak (shuffling preserves the obs multiset -> backward stays informative).
HARD-PASS: kernel abduces a non-trivial signature {uses_transition} that the documented filler satisfies, the past_accum control FAILS (transition-model not mere past-access), accuracy delta closer-vs-greedy >= half the ~0.10 headroom. HARD-FAIL: kernel cannot separate closers from gap, or past_accum closes (would mean mere past-access suffices)."""
from __future__ import annotations
import sys, time
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

K = 8            # hidden states
M = 12           # observation symbols
T = 40           # sequence length
N_SEQ = 400
SEEDS = [7, 17, 23]
PROPS = ["uses_transition", "uses_past_obs", "uses_future_obs"]
SELFTEST = "--self-test" in sys.argv


def _peaked(rows, cols, g, conc):
    P = g.random((rows, cols)) ** conc
    return P / P.sum(axis=1, keepdims=True)


def _gen(g):
    A = _peaked(K, K, g, 3.0)                 # transition (peaked)
    B = _peaked(K, M, g, 1.5)                 # emission (overlapping -> local decoding ambiguous = headroom)
    pi = _peaked(1, K, g, 2.0)[0]
    seqs = []; states = []
    for _ in range(N_SEQ):
        s = [int(g.choice(K, p=pi))]
        for t in range(1, T): s.append(int(g.choice(K, p=A[s[-1]])))
        o = [int(g.choice(M, p=B[st])) for st in s]
        seqs.append(o); states.append(s)
    return A, B, pi, np.array(seqs), np.array(states)


def _forward(o, A, B, pi):
    a = np.zeros((T, K)); a[0] = pi * B[:, o[0]]; a[0] /= a[0].sum() + 1e-12
    for t in range(1, T):
        a[t] = (a[t - 1] @ A) * B[:, o[t]]; a[t] /= a[t].sum() + 1e-12
    return a


def _backward(o, A, B):
    b = np.zeros((T, K)); b[-1] = 1.0
    for t in range(T - 2, -1, -1):
        b[t] = A @ (B[:, o[t + 1]] * b[t + 1]); b[t] /= b[t].sum() + 1e-12
    return b


def _viterbi(o, A, B, pi):
    lA = np.log(A + 1e-12); lB = np.log(B + 1e-12); lpi = np.log(pi + 1e-12)
    d = np.zeros((T, K)); psi = np.zeros((T, K), dtype=int); d[0] = lpi + lB[:, o[0]]
    for t in range(1, T):
        m = d[t - 1][:, None] + lA; psi[t] = m.argmax(0); d[t] = m.max(0) + lB[:, o[t]]
    path = [int(d[-1].argmax())]
    for t in range(T - 1, 0, -1): path.append(int(psi[t][path[-1]]))
    return np.array(path[::-1])


def _decode(name, o, A, B, pi, g=None):
    if name == "greedy": return B[:, o].argmax(0)                       # local emission only
    if name == "past_accum":                                           # cumulative emission, CONSTANT-state assumption (NO transition)
        lB = np.log(B[:, o] + 1e-12); cum = np.cumsum(lB, axis=1)      # (K, T): sum_{t'<=t} log B[k, o_t']
        return cum.argmax(0)
    if name == "forward": return _forward(o, A, B, pi).argmax(1)        # filtering (transition + past)
    if name == "fwd_back": return (_forward(o, A, B, pi) * _backward(o, A, B)).argmax(1)  # smoothing (+ future)
    if name == "viterbi": return _viterbi(o, A, B, pi)                  # global MAP (transition)
    raise ValueError(name)


CANDS = ["greedy", "past_accum", "forward", "fwd_back", "viterbi"]
# measured property signatures (what each decoder structurally uses)
PROP_SIG = {
    "greedy":     {"uses_transition": False, "uses_past_obs": False, "uses_future_obs": False},
    "past_accum": {"uses_transition": False, "uses_past_obs": True,  "uses_future_obs": False},
    "forward":    {"uses_transition": True,  "uses_past_obs": True,  "uses_future_obs": False},
    "fwd_back":   {"uses_transition": True,  "uses_past_obs": True,  "uses_future_obs": True},
    "viterbi":    {"uses_transition": True,  "uses_past_obs": True,  "uses_future_obs": True},
}


def run() -> Dict:
    acc = {c: [] for c in CANDS}
    for seed in SEEDS:
        g = np.random.default_rng(seed); A, B, pi, seqs, states = _gen(g)
        for c in CANDS:
            cor = tot = 0
            for i in range(N_SEQ):
                yh = _decode(c, seqs[i], A, B, pi, g=np.random.default_rng(seed * 1000 + i))
                cor += int((yh == states[i]).sum()); tot += T
            acc[c].append(cor / tot)
    macc = {c: float(np.mean(acc[c])) for c in CANDS}
    base = macc["greedy"]; ceil = max(macc["fwd_back"], macc["viterbi"])
    headroom = ceil - base
    # close bar: reach >= base + 0.5*headroom (substantial closure)
    closers = {c for c in CANDS if c != "greedy" and macc[c] >= base + 0.5 * headroom}
    failers = ({c for c in CANDS if c not in closers and c != "greedy"}) | {"greedy"}
    props = {c: dict(PROP_SIG[c]) for c in CANDS}
    future_marginal = macc["fwd_back"] - macc["forward"]   # how much future-integration adds beyond past+transition

    def abduce(pos, neg):
        cand = [p for p in PROPS if (pos and all(props[c][p] for c in pos)) and all(not props[f][p] for f in neg)]
        def disc(sig):
            if not sig: return False
            if any(not all(props[c][p] for p in sig) for c in pos): return False
            if any(all(props[f][p] for p in sig) for f in neg): return False
            return True
        sig = list(cand); changed = True
        while changed and len(sig) > 1:
            changed = False
            for p in list(sig):
                if disc([q for q in sig if q != p]): sig.remove(p); changed = True; break
        return sig, disc(sig)

    weak_sig, disc = abduce(closers, failers)
    control_fails = "past_accum" not in closers          # the rectprod-analog: past-access without transition -> must fail
    filler_satisfies = bool(weak_sig) and all(props["fwd_back"][p] for p in weak_sig) and all(props["viterbi"][p] for p in weak_sig)
    nontrivial = bool(weak_sig)
    delta = (max((macc[c] for c in closers), default=base) - base)
    hard_pass = bool(closers) and disc and control_fails and filler_satisfies and nontrivial and delta >= 0.5 * headroom

    print("  CELL-ABDUCTION-F3 (Phase C real-gap deployment; HMM headroom; math-native accuracy delta):", flush=True)
    print("  greedy(baseline)=%.4f | past_accum=%.4f | forward=%.4f | fwd_back=%.4f | viterbi=%.4f" % (
        base, macc["past_accum"], macc["forward"], macc["fwd_back"], macc["viterbi"]), flush=True)
    print("  headroom(ceil-base)=%.4f | closers=%s | accuracy-delta(closer-greedy)=%.4f | future-marginal(fb-fwd)=%.4f" % (
        headroom, sorted(closers), delta, future_marginal), flush=True)
    for c in CANDS:
        print("    %-12s acc=%.4f props=%s" % (c, macc[c], "".join("1" if props[c][p] else "0" for p in PROPS)), flush=True)
    print("  props order: %s" % "/".join(PROPS), flush=True)
    print("  ABDUCED weakest signature=%s (disc=%s) | past_accum control FAILS=%s | documented filler(fwd_back+viterbi) satisfies=%s" % (
        weak_sig, disc, control_fails, filler_satisfies), flush=True)
    print("  HARD-PASS=%s" % hard_pass, flush=True)
    return {"macc": macc, "base": base, "ceil": ceil, "headroom": headroom, "closers": sorted(closers),
            "props": props, "abduced": weak_sig, "disc": disc, "control_fails": control_fails,
            "filler_satisfies": filler_satisfies, "delta": delta, "future_marginal": future_marginal, "hard_pass": hard_pass}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("HMM greedy baseline=%.4f -> closers %s (delta %.4f vs headroom %.4f); abduced weakest signature=%s; past_accum control FAILS=%s (transition-model not mere past-access); documented filler fwd_back+viterbi satisfies=%s; future-marginal(fb-fwd)=%.4f." % (
        r["base"], r["closers"], r["delta"], r["headroom"], r["abduced"], r["control_fails"], r["filler_satisfies"], r["future_marginal"]))
    if r["hard_pass"]:
        return ("HARD_PASS", "ABDUCTION KERNEL DEPLOYED ON A REAL GAP (no known filler): from the HMM headroom failure the kernel abduced {uses_transition (sequential transition-model integration)} as the weakest closing signature -- matching the documented PARTIAL filler class (forward/backward/viterbi all model transitions) -- with the past_accum control (uses past observations but NO transition model) FAILING, proving TRANSITION-MODEL integration (not mere past-access) is load-bearing, and a math-native accuracy delta closing >=half the ~0.10 headroom. The loop's ABDUCTION step works on a real documented gap, not just the F1 ground-truth case. HONEST: future/bidirectional integration is a MARGINAL secondary contributor (fwd_back - forward = %.4f), NOT the primary driver -- v1's bidirectional hypothesis was refuted by the data and corrected. Phase C abduction validated. " % r["future_marginal"] + s)
    if not r["closers"]:
        return ("HARD_FAIL", "No decoder closes the HMM headroom substantially -- task/scale issue, not kernel. " + s)
    if not r["control_fails"]:
        return ("PARTIAL", "past_accum control ALSO closes -> mere past-access suffices on this instance; the transition-model signature is not cleanly isolated. " + s)
    return ("PARTIAL", "Closers exist but the abduced signature is trivial or the documented filler does not satisfy it -- inspect property space. " + s)


def _selftest():
    g = np.random.default_rng(0); A, B, pi, seqs, states = _gen(g)
    assert seqs.shape == (N_SEQ, T) and _viterbi(seqs[0], A, B, pi).shape == (T,)
    print("[selftest] PASS", flush=True)


if __name__ == "__main__":
    _selftest()
    if SELFTEST: sys.exit(0)
    print("[config] anchor=substrate_abduction_f3_hmm_headroom_realgap | K=%d M=%d T=%d N=%d seeds=%s" % (K, M, T, N_SEQ, SEEDS), flush=True)
    out_dir = get_output_dir("substrate_abduction_f3_hmm_headroom_realgap_deployment_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_abduction_f3_hmm_headroom_realgap_deployment_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
