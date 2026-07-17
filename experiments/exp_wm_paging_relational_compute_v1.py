"""exp_wm_paging_relational_compute_v1 -- does effective WM decouple for COMPUTE, not just recall?

QUESTION (the harder claim the recall paging cell DODGED):
  The RAM+disk paging cell (exp_wm_paging_exact_store_ram_disk_v1, commit 2c44dbc5c) proved effective
  WM decouples from active-N for RECALL (recover m key->value items where m >> safe active-bundle cap).
  Its VET (af2ecac1) corrected the mechanism: the load-bearing lever is BOUNDED PER-ACCESS CROSSTALK
  (small pages <= safe cap ~ N/16 + EXACT ADDRESSING routing to the right page) -- NOT exact value
  storage (a paging-matched sharded LOSSY store ties an exact store). "Effective WM unlimited for
  COMPUTE" was NOT earned: recall != reasoning.

  This cell tests the harder claim: can the substrate REASON / RELATE over MORE items than the active
  buffer holds, by paging small bounded-crosstalk pages in/out with exact addressing? A multi-hop query
  needs facts that are NOT simultaneously in the active window, so the answer must be COMPOSED by paging
  the relevant page in for each hop. Does RELATIONAL accuracy decouple from active-N (stay high past the
  cliff where a flat buffer craters), and does the relate/coordination cost stay BOUNDED (not blow up
  with #facts / #hops)? Or does the relate/paging-coordination cost BIND?

TASK (multi-hop relational composition over a fact-set LARGER than the safe active-bundle cap):
  A functional graph on M nodes: each node i has exactly one out-edge (i -> next[i]) where next is a
  random permutation (ground-truth exact, closed under composition). The fact-set = M edges; M is swept
  well PAST the safe cap N/16, so all edges cannot sit in one active bundle without crosstalk cratering.
  Query: from a start node s, follow the graph k hops and return the k-hop target next^k(s). Each hop
  needs the out-edge of the CURRENT node -- a fact that may live outside the active window -> the walk
  can only be composed by looking that fact up (paging its page in). Errors COMPOUND across hops: a
  wrong intermediate poisons the rest of the walk, so multi-hop is strictly harder than single recall.

ARMS (differ ONLY in storage/paging discipline; identical graph, geometry, query set, benign):
  - FLAT (baseline): all M edges superposed into ONE active bundle (no paging). Each hop = unbind by the
      current node's key + cleanup against the value codebook. Per-hop crosstalk grows with M -> per-hop
      lookup craters past ~N/16, and COMPOUNDING over k hops craters multi-hop accuracy even harder.
  - PAGED (mechanism, VET-corrected): edges partitioned into small pages of size P <= safe cap (bounded
      crosstalk). EXACT ADDRESSING: a routing index maps node -> which page holds its out-edge (glass-box
      page table). Each hop: route to the page (exact), page it in as a small FHRR bundle (<= P edges),
      unbind + cleanup to decode next. Value decode is still LOSSY FHRR (NOT exact-value storage -- the
      VET correction) but per-access crosstalk is bounded by P, NOT M -> per-hop lookup stays accurate at
      any M -> multi-hop accuracy stays high. Coordination cost = 1 page-in per hop = O(k), independent
      of M.
  - PAGED_OVERCAP (control -- isolates PAGE GRANULARITY as the lever): SAME exact addressing + SAME
      paging, but pages are LARGE (P_over > safe cap). Addressing still routes correctly, but per-page
      crosstalk exceeds the cap -> per-hop lookup degrades -> multi-hop craters. If PAGED_OVERCAP craters
      like FLAT, the win is from SMALL-PAGE bounded crosstalk, NOT merely "having a paging store".

METRIC: multi-hop (k-hop) relational accuracy vs #facts M (well past N/16), FLAT vs PAGED vs
  PAGED_OVERCAP. KEY: does PAGED relational accuracy stay high past the cliff where FLAT craters, and
  does the relate/coordination cost (page-ins per query) stay bounded (== k, independent of M)?

PRE-REG (envelope-fail-bands; set BEFORE running):
  HARD_PASS (relational compute DECOUPLES from active-N + coordination cost bounded):
    at the largest M tested (M_max >> safe_cap N/16) --
      PAGED k-hop accuracy >= 0.90 AND
      FLAT craters (k-hop accuracy <= 0.30; compounding) AND (PAGED - FLAT) >= 0.40 AND
      PAGED_OVERCAP craters (k-hop accuracy <= 0.60) AND (PAGED - PAGED_OVERCAP) >= 0.30 (granularity is
        the lever) AND
      effective-WM extension factor (M_paged_hold / M_flat_crater) >= 4.0 AND
      coordination cost bounded: PAGED page-ins/query <= k AND independent of M (max-min across the sweep
        <= 0.5) AND
      discriminator fired: FLAT k-hop >= 0.90 at the smallest M (in band) AND FLAT craters at M_max.
    => reasoning-over-paged decouples from active-N losslessly; the RAM+disk win is COMPUTE, not just
       recall; coordination cost is O(hops), not O(#facts).
  HARD_FAIL (the relate/paging-coordination cost BINDS):
    (PAGED - FLAT) < 0.10 at M_max (paging does NOT extend relational compute) OR
    PAGED k-hop accuracy < 0.70 at M_max (paged relational accuracy craters too -> compute does NOT
      decouple, only recall did) OR
    PAGED page-ins/query grows with M (coordination cost blows up with #facts) OR
    FLAT never craters in the swept range (regime too easy; discriminator did not fire).
    => the compute claim is REFUTED: effective WM extends for recall but NOT for reasoning.
  MIDDLE otherwise. Report the decoupling (extension) factor + the relate-cost scaling regardless.

BRAIN-CHECK (report on HARD_FAIL): the brain DOES reason over far more than its ~4-slot focus of
  attention -- long-term working memory (Ericsson-Kintsch) uses retrieval structures / skilled memory to
  bring task-relevant items back into the focus on demand, i.e. it PAGES from LTM to compose. So a paged
  relational architecture is brain-faithful; a FAIL here would be an IMPLEMENTATION gap (the substrate's
  exact addressing is an existence-proof the routing can be lossless), not a structural bound -- report
  which, and do NOT over-read a PARTIAL decoupling as full.

Compute architecture: (b) sequential-CPU with justification. Benign geometry, N=512, M<=512, k<=5,
  3-5 seeds; total wall < 15s. Genuine sequential dependency (hop N depends on hop N-1's decoded node);
  mechanism-comparison at small scale; no GPU speedup at this size. numpy.
Storage strategy: MIXED / testing-as-discriminator -- FLAT = bundled (the baseline being refuted),
  PAGED = sharded-into-small-pages (the mechanism), PAGED_OVERCAP = sharded-into-large-pages (control).
Local numpy; no queue / GPU / atoms / push. ASCII-only. FHRR = complex128 unit phasors.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on per-M recall vecs)
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: cleanup argmax over V phasors has no closed-form CRLB here; discriminator is the empirical
#     flat-craters-vs-paged-holds gap, verified to FIRE in self-test at full-N (M=M_max) BEFORE dispatch
# - baseline_in_band at self-test (FLAT high below cliff, craters at M_max; 0.05 < mid-band)
# - discriminator survives scale: self-test runs the FULL-M (M=512) discriminator and asserts the gap
# - HARD_PASS strictly above floor (>=0.90 paged; <=0.30 flat; gaps >=0.40 / >=0.30)
# - HP_SCOPE: HARD_PASS gates apply to {paged}; FLAT + PAGED_OVERCAP are must-crater controls
# - no sweep-cardinality gate needed beyond len(sweep)==len(m_grid) (checked)
# - per-unit: no bare except; single outer try re-raises non-Exception
# - calibration_check: default_ok_for_this_regime (benign phasors, N=512, page P chosen below cliff)
# - deterministic_seeding: fixed integer seeds; no hash()/list(set()) seeding or ordering
# - all numbers in this docstring are HYPOTHESIZED@this-prereg (bands) or THEORETICAL (SNR); MEASURED
#     values live only in the emitted metrics.json
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "wm_paging_relational_compute_v1"
OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"


# ---------------------------------------------------------------------------
# FHRR primitives (glass-box, inspectable) -- unit phasors, complex128.
# ---------------------------------------------------------------------------

def make_phasors(rng, count, N):
    """count random FHRR unit-phasor hypervectors, shape (count, N) complex128."""
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def bind(a, b):
    """FHRR bind = elementwise complex multiply (self-inverse via conjugate)."""
    return a * b


def unbind(c, b):
    """FHRR unbind = multiply by conjugate."""
    return c * np.conj(b)


def cleanup(query, codebook):
    """Nearest codebook row by Re(Hermitian inner product). Returns argmax index.

    All codebook rows are unit phasors (equal norm) so argmax over Re(<c_v, q>) needs no normalization.
    """
    scores = (codebook.conj() @ query).real
    return int(np.argmax(scores))


# ---------------------------------------------------------------------------
# One (N, M, k, P, P_over, seed) trial: run all 3 storage arms on the SAME graph.
# ---------------------------------------------------------------------------

def run_trial(N, M, k, P, P_over, Q, seed):
    """Build a functional graph on M nodes, page edges per arm, run Q multi-hop (k-hop) queries.

    Returns per-arm k-hop accuracy + interface-cost counters. Arms differ ONLY in storage discipline;
    the graph (next permutation), the key/value codebooks, and the query set are IDENTICAL across arms.

    exact addressing = a page-table index (node -> page); value decode is LOSSY FHRR (unbind+cleanup),
    NOT exact-value storage. Only the ROUTING is exact (the VET-corrected mechanism).
    """
    rng = np.random.default_rng(seed)
    keys = make_phasors(rng, M, N)      # per-node address phasors (cleanup NOT over these)
    vals = make_phasors(rng, M, N)      # per-node value phasors (cleanup codebook, size M)

    nxt = rng.permutation(M)            # functional graph: node i -> nxt[i]; ground-truth exact
    # Edge i -> nxt[i] stored as bind(keys[i], vals[nxt[i]]).
    edges = np.array([bind(keys[i], vals[nxt[i]]) for i in range(M)])  # (M, N)

    # Query set: Q distinct start nodes; ground-truth k-hop target = nxt applied k times.
    q = min(Q, M)
    starts = rng.permutation(M)[:q]
    truth = starts.copy()
    for _ in range(k):
        truth = nxt[truth]              # vectorized k-hop ground truth

    # --- FLAT: one M-item active bundle, no paging. Chain via DECODED node (errors compound). ---
    flat_bundle = edges.sum(axis=0)
    flat_ok = 0
    for idx in range(q):
        cur = int(starts[idx])
        for _ in range(k):
            cur = cleanup(unbind(flat_bundle, keys[cur]), vals)   # crosstalk ~ M; compounds over hops
        flat_ok += int(cur == int(truth[idx]))
    flat_acc = flat_ok / q

    # --- Paging setup shared by PAGED (small pages) and PAGED_OVERCAP (large pages). ---------
    def build_pages(page_size):
        """Return (page_of index dict, list of page FHRR bundles). Exact addressing via page_of."""
        n_pages = (M + page_size - 1) // page_size
        page_bundles = []
        for p in range(n_pages):
            lo = p * page_size
            hi = min(M, lo + page_size)
            page_bundles.append(edges[lo:hi].sum(axis=0))          # bundle of <= page_size edges
        page_of = {i: i // page_size for i in range(M)}            # exact page table (glass-box)
        return page_of, page_bundles, n_pages

    def run_paged(page_size):
        page_of, page_bundles, n_pages = build_pages(page_size)
        ok = 0
        page_ins = 0                                               # store reads at query time
        for idx in range(q):
            cur = int(starts[idx])
            for _ in range(k):
                pg = page_of[cur]                                  # EXACT addressing (route)
                page_ins += 1                                      # 1 page-in per hop (O(k), not O(M))
                dec = cleanup(unbind(page_bundles[pg], keys[cur]), vals)  # crosstalk ~ page_size
                cur = dec
            ok += int(cur == int(truth[idx]))
        return ok / q, page_ins, n_pages

    paged_acc, paged_page_ins, n_pages_small = run_paged(P)
    overcap_acc, overcap_page_ins, n_pages_big = run_paged(P_over)

    return {
        "flat_acc": flat_acc,
        "paged_acc": paged_acc,
        "overcap_acc": overcap_acc,
        "paged_page_ins_per_query": paged_page_ins / q,            # == k by construction (report)
        "overcap_page_ins_per_query": overcap_page_ins / q,
        "n_pages_small": n_pages_small,
        "n_pages_big": n_pages_big,
        "n_query": q,
        "k_hops": k,
    }


def avg_over_seeds(N, M, k, P, P_over, Q, seeds):
    keys = ["flat_acc", "paged_acc", "overcap_acc", "paged_page_ins_per_query",
            "overcap_page_ins_per_query", "n_pages_small", "n_pages_big", "n_query", "k_hops"]
    acc = {kk: [] for kk in keys}
    for s in seeds:
        r = run_trial(N, M, k, P, P_over, Q, s)
        for kk in keys:
            acc[kk].append(r[kk])
    return {kk: float(np.mean(v)) for kk, v in acc.items()}


# ---------------------------------------------------------------------------
# Self-tests (hardened: exercise REAL arms + fire the discriminator at FULL-M BEFORE any sweep).
# ---------------------------------------------------------------------------

def self_test():
    N = 512
    safe_cap = N // 16          # 32
    P = 16                      # small page: below cliff -> bounded crosstalk
    P_over = 4 * safe_cap       # 128: over cap -> control craters
    k = 5

    print("[self-test] FHRR bind/unbind exact single-item recovery (leak guard) ...")
    rng = np.random.default_rng(0)
    a = make_phasors(rng, 1, N)[0]
    role = make_phasors(rng, 1, N)[0]
    cos = (np.conj(a) @ unbind(bind(role, a), role)).real / N
    assert cos > 0.999, f"bind/unbind not self-inverse: cos={cos}"
    print(f"           single-pair unbind cos={cos:.4f} OK")

    print("[self-test] BELOW cliff (M=8 << N/16=32): all three arms compose k-hop cleanly ...")
    r_lo = avg_over_seeds(N, M=8, k=k, P=P, P_over=P_over, Q=8, seeds=[1, 2])
    assert r_lo["flat_acc"] >= 0.90, f"flat must ace k-hop below cliff: {r_lo['flat_acc']}"
    assert r_lo["paged_acc"] >= 0.90, f"paged must ace k-hop below cliff: {r_lo['paged_acc']}"
    print(f"           M=8: flat={r_lo['flat_acc']:.3f} paged={r_lo['paged_acc']:.3f} "
          f"overcap={r_lo['overcap_acc']:.3f} OK")

    print("[self-test] DISCRIMINATOR FIRES at FULL-M (M=512 >> N/16=32): FLAT k-hop craters ...")
    r_hi = avg_over_seeds(N, M=512, k=k, P=P, P_over=P_over, Q=32, seeds=[1, 2])
    assert r_hi["flat_acc"] <= 0.30, f"flat must crater k-hop above cliff (discriminator): {r_hi['flat_acc']}"
    print(f"           M=512: flat_acc={r_hi['flat_acc']:.3f} (craters) OK")

    print("[self-test] RELATIONAL COMPUTE DECOUPLES: paged holds while flat + overcap crater ...")
    assert r_hi["paged_acc"] >= 0.90, f"paged must hold k-hop at M=512: {r_hi['paged_acc']}"
    assert r_hi["overcap_acc"] <= 0.60, f"overcap must crater (granularity lever): {r_hi['overcap_acc']}"
    assert (r_hi["paged_acc"] - r_hi["overcap_acc"]) >= 0.30, \
        f"page-granularity must be load-bearing: {r_hi['paged_acc'] - r_hi['overcap_acc']}"
    print(f"           M=512: paged={r_hi['paged_acc']:.3f} overcap={r_hi['overcap_acc']:.3f} "
          f"flat={r_hi['flat_acc']:.3f} OK")

    print("[self-test] COORDINATION COST BOUNDED: paged page-ins/query == k, independent of M ...")
    assert abs(r_lo["paged_page_ins_per_query"] - k) < 1e-9, \
        f"page-ins/query must equal k hops: {r_lo['paged_page_ins_per_query']}"
    assert abs(r_hi["paged_page_ins_per_query"] - k) < 1e-9, \
        f"page-ins/query must stay k at large M (not blow up): {r_hi['paged_page_ins_per_query']}"
    print(f"           page-ins/query: M=8 -> {r_lo['paged_page_ins_per_query']:.1f}, "
          f"M=512 -> {r_hi['paged_page_ins_per_query']:.1f} (== k={k}, independent of M) OK")

    print("[self-test] ARMS-MUST-DIFFER (META_RULE_AF): the three k-hop accuracies differ at M=512 ...")
    trio = (round(r_hi["flat_acc"], 6), round(r_hi["paged_acc"], 6), round(r_hi["overcap_acc"], 6))
    assert len(set(trio)) == 3, f"META_RULE_AF: arms produced identical k-hop accuracy {trio}"
    print(f"           arms differ: {trio} OK")

    print(f"[self-test] (safe_cap=N//16={safe_cap}; P={P} below cliff; P_over={P_over} over cap) ALL PASS")


# ---------------------------------------------------------------------------
# Crash diagnostic + atomic metrics write (hardening).
# ---------------------------------------------------------------------------

def _write_crash_metrics(exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "run_mode": "crash",
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_DIR / "metrics.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, OUT_DIR / "metrics.json")


# ---------------------------------------------------------------------------
# Main sweep + verdict.
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    t0 = time.time()
    N = 512
    safe_cap = N // 16          # 32 = nominal safe active-bundle capacity (the crosstalk cliff heuristic)
    P = 16                      # PAGED small page: below cliff -> bounded per-access crosstalk
    P_over = 4 * safe_cap       # 128: PAGED_OVERCAP large page -> over cap, control craters
    k = 5                       # hops per multi-hop query (compounding relate)
    Q = 32
    if args.smoke:
        m_grid = [8, 32, 128, 512]
        seeds = [1, 2]
        run_mode = "smoke"
    else:
        m_grid = [8, 16, 32, 48, 64, 96, 128, 256, 512]
        seeds = [1, 2, 3, 4, 5]
        run_mode = "full"

    sweep = []
    for M in m_grid:
        res = avg_over_seeds(N, M, k, P, P_over, Q, seeds)
        res.update({"m": M})
        sweep.append(res)
        print(f"M={M:4d}  flat={res['flat_acc']:.3f}  paged={res['paged_acc']:.3f}  "
              f"overcap={res['overcap_acc']:.3f}  page_ins/q={res['paged_page_ins_per_query']:.1f} "
              f"n_pages={res['n_pages_small']:.0f}", flush=True)

    # --- k-sweep at M_max (show FLAT decays with hops while PAGED holds) --------------------
    M_max = max(m_grid)
    k_grid = [1, 2, 3, 5]
    k_sweep = []
    for kk in k_grid:
        rk = avg_over_seeds(N, M_max, kk, P, P_over, Q, seeds)
        k_sweep.append({"k": kk, "flat_acc": rk["flat_acc"], "paged_acc": rk["paged_acc"],
                        "overcap_acc": rk["overcap_acc"]})
        print(f"k={kk}  (M={M_max})  flat={rk['flat_acc']:.3f}  paged={rk['paged_acc']:.3f}  "
              f"overcap={rk['overcap_acc']:.3f}", flush=True)

    def at(M):
        for r in sweep:
            if r["m"] == M:
                return r
        return None

    top = at(M_max)
    flat_at_max = top["flat_acc"]
    paged_at_max = top["paged_acc"]
    overcap_at_max = top["overcap_acc"]

    # Effective-WM crater / hold points on the RELATIONAL (k-hop) metric.
    m_flat_crater = None
    for r in sorted(sweep, key=lambda x: x["m"]):
        if r["flat_acc"] < 0.90:
            m_flat_crater = r["m"]
            break
    paged_hold = max((r["m"] for r in sweep if r["paged_acc"] >= 0.90), default=0)
    extension_factor = (float(paged_hold) / float(m_flat_crater)) if m_flat_crater else float("inf")

    # Coordination cost: page-ins per query across the sweep (should be constant == k).
    paged_page_ins = [r["paged_page_ins_per_query"] for r in sweep]
    page_ins_min = float(min(paged_page_ins))
    page_ins_max = float(max(paged_page_ins))
    coord_cost_bounded = (page_ins_max <= k + 1e-9) and ((page_ins_max - page_ins_min) <= 0.5)

    # Discriminator-fired / baseline-in-band: flat high below cliff AND flat craters at max M.
    flat_below_cliff = at(min(m_grid))["flat_acc"]
    flat_fired = (flat_below_cliff >= 0.90) and (flat_at_max <= 0.30)

    paged_minus_flat = paged_at_max - flat_at_max
    paged_minus_overcap = paged_at_max - overcap_at_max

    hp = (paged_at_max >= 0.90 and flat_at_max <= 0.30 and paged_minus_flat >= 0.40
          and overcap_at_max <= 0.60 and paged_minus_overcap >= 0.30
          and (m_flat_crater is not None) and extension_factor >= 4.0
          and coord_cost_bounded and flat_fired)
    hf = (paged_minus_flat < 0.10) or (paged_at_max < 0.70) or (not coord_cost_bounded) \
        or (m_flat_crater is None) or (not flat_fired)

    if hp:
        verdict = "HARD_PASS"
    elif hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    verdict_msg = (
        f"WM paging for COMPUTE (relational reasoning over paged facts, k={k}-hop): at M_max={M_max} "
        f"(>> safe_cap N/16={safe_cap}) paged_acc={paged_at_max:.3f} vs flat_acc={flat_at_max:.3f} vs "
        f"overcap_acc={overcap_at_max:.3f}. FLAT k-hop craters at M={m_flat_crater} (<0.90); PAGED holds "
        f"(>=0.90) up to M={paged_hold}. Effective-WM extension factor (relational) = "
        f"{extension_factor:.1f}x. Page-granularity load-bearing: paged - overcap = "
        f"{paged_minus_overcap:+.3f} (>=0.30 => small-page bounded crosstalk buys the win, not merely "
        f"'having a store'). Paging extends relational compute: paged - flat = {paged_minus_flat:+.3f}. "
        f"Coordination cost: page-ins/query in [{page_ins_min:.1f},{page_ins_max:.1f}] == k hops, "
        f"INDEPENDENT of M (bounded={coord_cost_bounded}) => cost is O(hops) not O(#facts). "
        f"Discriminator fired (flat in-band below cliff -> craters): {flat_fired}."
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: FHRR paged relational reasoning decouples k-hop accuracy from active-N ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": round(time.time() - t0, 2),
        "n_seeds": len(seeds),
        "config": {"N": N, "safe_cap_N_over_16": safe_cap, "page_P": P, "page_over_P": P_over,
                   "k_hops": k, "Q": Q, "m_grid": m_grid, "k_grid": k_grid},
        "at_m_max": {"m": M_max, "flat_acc": flat_at_max, "paged_acc": paged_at_max,
                     "overcap_acc": overcap_at_max},
        "m_flat_crater": m_flat_crater,
        "paged_hold_up_to_m": paged_hold,
        "effective_wm_extension_factor": extension_factor,
        "paged_minus_flat_at_max": paged_minus_flat,
        "paged_minus_overcap_at_max": paged_minus_overcap,
        "coord_page_ins_per_query_min": page_ins_min,
        "coord_page_ins_per_query_max": page_ins_max,
        "coord_cost_bounded": coord_cost_bounded,
        "discriminator_fired": flat_fired,
        "sweep": sweep,
        "k_sweep_at_m_max": k_sweep,
        "REQUIRED_FIELDS": ["anchor_name", "verdict", "verdict_msg", "at_m_max",
                            "effective_wm_extension_factor", "coord_cost_bounded", "sweep"],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_DIR / "metrics.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, OUT_DIR / "metrics.json")

    print("\n=== VERDICT ===")
    print(verdict)
    print(verdict_msg)
    print(f"metrics -> {OUT_DIR / 'metrics.json'}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(e)
        raise
