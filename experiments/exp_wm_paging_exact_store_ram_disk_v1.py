"""exp_wm_paging_exact_store_ram_disk_v1 -- Frontier-2 native-advantage test: "memory has its own N".

QUESTION (USER Frontier-2 vision -- exploit the substrate's OWN world, not just the brain's):
  The active FHRR superposition buffer (working memory) caps at a safe load of ~ N/16 role-filler
  pairs before crosstalk craters cleanup. That is the brain's regime: a tiny, LOSSY working memory.
  The substrate has a native affordance the brain LACKS: EXACT, addressable, lossless external storage
  (glass-box read/write, interference-free-by-construction). So a SMALL active buffer (a few slots) +
  an EXACT external key-value store, PAGING items out when the buffer fills and back in when the task
  references them, should give EFFECTIVE working memory FAR larger than the flat buffer -- decoupled
  from the active N. This is the "memory has its own N" / RAM(registers)+disk thesis. It is where the
  substrate can BEAT the brain's tiny lossy WM.

TASK (hold-and-relate; requires holding/relating MORE items than the active buffer's safe capacity):
  Stream m distinct (key -> value) items (m clearly EXCEEDS the safe flat capacity N/16). Then query a
  random subset of Q keys and recover the value bound to each. Correct answers need items that are no
  longer in the small active window -- so the task cannot be solved from the active buffer alone.

ARMS (differ ONLY in the storage/paging discipline; identical task, identical geometry, benign):
  - FLAT (baseline): everything superposed into ONE active bundle (no paging). Query = unbind + cleanup
      against the full m-item bundle. Crosstalk grows with m -> MUST crater past ~ N/16.
  - PAGED_EXACT (mechanism / native affordance): active buffer holds only B recent items as an FHRR
      bundle (the lossy "registers"); when it fills, the oldest item is paged OUT to an EXACT addressable
      key-value store ("disk", lossless). At query: recent keys decode from the B-bundle (crosstalk <= B);
      evicted keys are read back EXACTLY from the store. Per-access crosstalk is bounded by B, NOT m ->
      effective WM decoupled from active N.
  - PAGED_LOSSY (control -- isolates whether EXACTNESS is what buys the win): SAME paging schedule + SAME
      B-item active buffer, but the external store is LOSSY -- evicted items are re-bundled (compressed)
      into ONE super-vector. Evicted keys read back from the super-bundle carry crosstalk from ALL other
      evicted items -> degrades like flat. If PAGED_EXACT ~ PAGED_LOSSY, the win is not from exactness.

METRIC: per-item recall (fraction of queried keys whose value is recovered) vs #items m, well past N/16,
  FLAT vs PAGED_EXACT vs PAGED_LOSSY. KEY curve: does PAGED_EXACT stay accurate far beyond flat's crater
  while FLAT and PAGED_LOSSY degrade? Plus interface-cost accounting (page-outs / page-ins).

PRE-REG (envelope-fail-bands; set BEFORE running):
  HARD_PASS: at the largest m tested (well beyond flat's crater) PAGED_EXACT recall >= 0.90 AND FLAT
    craters (recall <= 0.50) AND PAGED_LOSSY degrades (recall <= 0.70) AND (PAGED_EXACT - PAGED_LOSSY)
    >= 0.20 (exactness load-bearing) AND effective-WM extension factor (m_max / m_flat_crater) >= 4.0
    AND FLAT actually craters within the swept range (discriminator fired). => native paging extends
    effective WM losslessly beyond the active-N cliff; exactness is the load-bearing native affordance.
  HARD_FAIL: (PAGED_EXACT - FLAT) < 0.10 at m_max (paging does NOT extend effective WM) OR
    (PAGED_EXACT - PAGED_LOSSY) < 0.10 at m_max (exactness does not help -- exact ~ lossy) OR FLAT never
    craters in the swept range (regime too easy; discriminator did not fire). => no native advantage.
  MIDDLE otherwise. Report the effective-WM extension factor + the interface cost regardless.

BRAIN-CHECK (report on HARD_FAIL): the brain's WM IS tiny + lossy; if OUR paging also fails despite an
  EXACT store the brain lacks, that is an implementation limit (exact recall is an existence-proof), not
  a structural bound -- report which.

Compute architecture: (b) sequential-CPU with justification. Benign geometry, N=512, m<=512, 3 seeds;
  total wall < 10s (mechanism-comparison at small scale, no GPU speedup available for this size). numpy.
Local numpy; no queue / GPU / atoms / push. ASCII-only. FHRR = complex128 unit phasors.
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
ANCHOR_NAME = "wm_paging_exact_store_ram_disk_v1"
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
    Re(sum_n conj(c[v,n]) q[n]) = (codebook.conj() @ query).real[v].
    """
    scores = (codebook.conj() @ query).real
    return int(np.argmax(scores))


# ---------------------------------------------------------------------------
# One (N, m, B, Q, seed) trial: run all 3 storage arms on the SAME item stream.
# ---------------------------------------------------------------------------

def run_trial(N, m, B, Q, seed, V_key, V_val):
    """Stream m (key->value) items, page per arm, query a random subset of Q keys.

    Returns per-arm per-item recall + interface-cost counters. Arms differ ONLY in storage discipline;
    the item stream, the key/value codebooks, and the query set are IDENTICAL across arms.
    """
    rng = np.random.default_rng(seed)
    keys = make_phasors(rng, V_key, N)     # key codebook (addresses)
    vals = make_phasors(rng, V_val, N)     # value codebook (cleanup targets)

    # Item stream: m distinct (key_id, val_id) pairs. Distinct keys (addresses) and distinct values.
    key_ids = rng.permutation(V_key)[:m]
    val_ids = rng.permutation(V_val)[:m]
    bound = np.array([bind(keys[key_ids[i]], vals[val_ids[i]]) for i in range(m)])  # (m, N) p_i

    # Query a random subset of Q keys (item indices). If m < Q, query all m.
    q = min(Q, m)
    query_items = rng.permutation(m)[:q]

    # --- FLAT: one m-item active bundle, no paging. -------------------------
    flat_bundle = bound.sum(axis=0)
    flat_ok = 0
    for it in query_items:
        rec = cleanup(unbind(flat_bundle, keys[key_ids[it]]), vals)
        flat_ok += int(rec == val_ids[it])
    flat_recall = flat_ok / q

    # --- Paging schedule shared by PAGED_EXACT and PAGED_LOSSY. -------------
    # Active buffer = FHRR bundle of the last B inserted items ("registers", lossy superposition).
    # Insert order = 0..m-1; item i is "recent" iff i >= m - B (still in the active window), else evicted.
    window_lo = max(0, m - B)
    recent_mask = np.arange(m) >= window_lo
    active_bundle = bound[window_lo:].sum(axis=0) if m > 0 else np.zeros(N, dtype=complex)

    # EXACT store ("disk"): addressable, lossless. Maps evicted key_id -> the EXACT value id (glass-box,
    # interference-free-by-construction). Modeled as a dict of the exact value ids for evicted items.
    exact_store = {int(key_ids[i]): int(val_ids[i]) for i in range(window_lo)}
    # LOSSY store: evicted items re-bundled (compressed) into ONE super-vector (crosstalk-prone).
    lossy_super = bound[:window_lo].sum(axis=0) if window_lo > 0 else np.zeros(N, dtype=complex)

    n_page_out = window_lo                 # items evicted to store during ingest
    n_page_in = 0                          # store reads triggered at query time (evicted keys queried)

    # --- PAGED_EXACT: recent -> B-bundle decode; evicted -> exact store read. ---
    pe_ok = 0
    for it in query_items:
        if recent_mask[it]:
            rec = cleanup(unbind(active_bundle, keys[key_ids[it]]), vals)  # crosstalk <= B
        else:
            n_page_in += 1
            rec = exact_store[int(key_ids[it])]                            # lossless read
        pe_ok += int(rec == val_ids[it])
    paged_exact_recall = pe_ok / q

    # --- PAGED_LOSSY: recent -> B-bundle decode; evicted -> lossy super-bundle unbind (crosstalk ~ n_evicted). ---
    pl_ok = 0
    for it in query_items:
        if recent_mask[it]:
            rec = cleanup(unbind(active_bundle, keys[key_ids[it]]), vals)
        else:
            rec = cleanup(unbind(lossy_super, keys[key_ids[it]]), vals)    # crosstalk from all evicted
        pl_ok += int(rec == val_ids[it])
    paged_lossy_recall = pl_ok / q

    return {
        "flat_recall": flat_recall,
        "paged_exact_recall": paged_exact_recall,
        "paged_lossy_recall": paged_lossy_recall,
        "n_page_out": n_page_out,
        "n_page_in": n_page_in,
        "n_query": q,
        "n_evicted": window_lo,
    }


def avg_over_seeds(N, m, B, Q, seeds, V_key, V_val):
    keys = ["flat_recall", "paged_exact_recall", "paged_lossy_recall", "n_page_out", "n_page_in", "n_query", "n_evicted"]
    acc = {k: [] for k in keys}
    for s in seeds:
        r = run_trial(N, m, B, Q, s, V_key, V_val)
        for k in keys:
            acc[k].append(r[k])
    return {k: float(np.mean(v)) for k, v in acc.items()}


# ---------------------------------------------------------------------------
# Self-tests (hardened: exercise the REAL arms + the discriminator BEFORE any sweep).
# ---------------------------------------------------------------------------

def self_test():
    print("[self-test] FHRR bind/unbind exact recovery (leak guard: single-item is lossless) ...")
    rng = np.random.default_rng(0)
    N = 512
    a = make_phasors(rng, 1, N)[0]
    role = make_phasors(rng, 1, N)[0]
    rec = unbind(bind(role, a), role)
    cos = (np.conj(a) @ rec).real / N
    assert cos > 0.999, f"bind/unbind not self-inverse: cos={cos}"
    print(f"           single-pair unbind cos={cos:.4f} OK")

    print("[self-test] BELOW cliff (m < N/16): all three arms recover cleanly ...")
    N = 512
    safe_cap = N // 16  # 32
    r_lo = avg_over_seeds(N, m=8, B=16, Q=8, seeds=[1, 2], V_key=1024, V_val=1024)
    assert r_lo["flat_recall"] >= 0.90, f"flat should ace below cliff: {r_lo['flat_recall']}"
    assert r_lo["paged_exact_recall"] >= 0.90, f"paged_exact below cliff: {r_lo['paged_exact_recall']}"
    print(f"           m=8: flat={r_lo['flat_recall']:.3f} paged_exact={r_lo['paged_exact_recall']:.3f} OK")

    print("[self-test] DISCRIMINATOR FIRES: WELL above cliff (m=512 >> N/16=32) FLAT craters ...")
    r_hi = avg_over_seeds(N, m=512, B=16, Q=32, seeds=[1, 2], V_key=1024, V_val=1024)
    assert r_hi["flat_recall"] <= 0.50, f"flat must crater above cliff (discriminator): {r_hi['flat_recall']}"
    print(f"           m=512: flat_recall={r_hi['flat_recall']:.3f} (craters) OK")

    print("[self-test] NATIVE ADVANTAGE: paged_exact holds while flat + lossy degrade ...")
    assert r_hi["paged_exact_recall"] >= 0.90, f"paged_exact must hold at m=512: {r_hi['paged_exact_recall']}"
    assert r_hi["paged_lossy_recall"] <= 0.70, f"paged_lossy must degrade at m=512: {r_hi['paged_lossy_recall']}"
    assert (r_hi["paged_exact_recall"] - r_hi["paged_lossy_recall"]) >= 0.20, \
        f"exactness must be load-bearing (exact-lossy gap): {r_hi['paged_exact_recall'] - r_hi['paged_lossy_recall']}"
    print(f"           m=512: paged_exact={r_hi['paged_exact_recall']:.3f} "
          f"paged_lossy={r_hi['paged_lossy_recall']:.3f} flat={r_hi['flat_recall']:.3f} OK")

    print("[self-test] ARMS-MUST-DIFFER: the three recall arms are not identical at m=512 ...")
    trio = (round(r_hi["flat_recall"], 6), round(r_hi["paged_exact_recall"], 6), round(r_hi["paged_lossy_recall"], 6))
    assert len(set(trio)) == 3, f"META_RULE_AF: arms produced identical recall {trio}"
    print(f"           arms differ: {trio} OK")

    print(f"[self-test] (safe_cap = N//16 = {safe_cap}; m sweep spans below -> well above) ALL PASS")


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
    safe_cap = N // 16   # 32 = nominal safe flat capacity (the crosstalk cliff heuristic)
    B = 16               # active buffer: a few slots, safely BELOW the cliff
    V_key = 1024
    V_val = 1024
    if args.smoke:
        m_grid = [8, 32, 128, 512]
        Q = 32
        seeds = [1, 2]
        run_mode = "smoke"
    else:
        m_grid = [8, 16, 32, 48, 64, 96, 128, 256, 512]
        Q = 32
        seeds = [1, 2, 3, 4, 5]
        run_mode = "full"

    sweep = []
    for m in m_grid:
        res = avg_over_seeds(N, m, B, Q, seeds, V_key, V_val)
        res.update({"m": m})
        sweep.append(res)
        print(f"m={m:4d}  flat={res['flat_recall']:.3f}  paged_exact={res['paged_exact_recall']:.3f}  "
              f"paged_lossy={res['paged_lossy_recall']:.3f}  page_out={res['n_page_out']:.0f} "
              f"page_in={res['n_page_in']:.1f}", flush=True)

    m_max = max(m_grid)

    def at(m):
        for r in sweep:
            if r["m"] == m:
                return r
        return None

    top = at(m_max)
    flat_at_max = top["flat_recall"]
    pe_at_max = top["paged_exact_recall"]
    pl_at_max = top["paged_lossy_recall"]

    # Effective-WM crater point: smallest m where FLAT recall first drops below 0.90.
    m_flat_crater = None
    for r in sorted(sweep, key=lambda x: x["m"]):
        if r["flat_recall"] < 0.90:
            m_flat_crater = r["m"]
            break
    # PAGED_EXACT hold point: largest m where paged_exact still >= 0.90.
    pe_hold = max((r["m"] for r in sweep if r["paged_exact_recall"] >= 0.90), default=0)
    extension_factor = (float(pe_hold) / float(m_flat_crater)) if m_flat_crater else float("inf")

    # Interface cost accounting (RAM+disk): amortized store ops per item / per query at m_max.
    page_out_at_max = top["n_page_out"]        # evictions during ingest (write ops)
    page_in_at_max = top["n_page_in"]          # store reads at query (evicted keys queried)
    q_at_max = top["n_query"]
    interface_reads_per_query = page_in_at_max / q_at_max if q_at_max else 0.0
    interface_writes_per_item = page_out_at_max / m_max if m_max else 0.0

    # Discriminator-fired / baseline-in-band: flat high below cliff AND flat craters at max m.
    flat_below_cliff = at(min(m_grid))["flat_recall"]
    flat_fired = (flat_below_cliff >= 0.90) and (flat_at_max <= 0.50)

    exact_minus_flat = pe_at_max - flat_at_max
    exact_minus_lossy = pe_at_max - pl_at_max

    hp = (pe_at_max >= 0.90 and flat_at_max <= 0.50 and pl_at_max <= 0.70
          and exact_minus_lossy >= 0.20 and (m_flat_crater is not None)
          and extension_factor >= 4.0 and flat_fired)
    hf = (exact_minus_flat < 0.10) or (exact_minus_lossy < 0.10) or (m_flat_crater is None) or (not flat_fired)

    if hp:
        verdict = "HARD_PASS"
    elif hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    verdict_msg = (
        f"WM paging (RAM+disk / 'memory has its own N'): at m_max={m_max} (>> safe_cap N/16={safe_cap}) "
        f"paged_exact_recall={pe_at_max:.3f} vs flat_recall={flat_at_max:.3f} vs paged_lossy_recall={pl_at_max:.3f}. "
        f"FLAT craters at m={m_flat_crater} (recall<0.90); PAGED_EXACT holds (>=0.90) up to m={pe_hold}. "
        f"Effective-WM extension factor = {extension_factor:.1f}x (paged_exact hold / flat crater). "
        f"Exactness load-bearing: paged_exact - paged_lossy = {exact_minus_lossy:+.3f} (>=0.20 => exactness buys the win). "
        f"Paging extends WM: paged_exact - flat = {exact_minus_flat:+.3f}. "
        f"Interface cost: {interface_writes_per_item:.2f} store-writes/item (ingest) + "
        f"{interface_reads_per_query:.2f} store-reads/query (amortized O(1), does not scale with m). "
        f"Discriminator fired (flat in-band below cliff -> craters): {flat_fired}."
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: FHRR WM paging exact-store extends effective WM beyond active-N cliff ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": round(time.time() - t0, 2),
        "n_seeds": len(seeds),
        "config": {"N": N, "safe_cap_N_over_16": safe_cap, "buffer_B": B, "Q": Q,
                   "V_key": V_key, "V_val": V_val, "m_grid": m_grid},
        "at_m_max": {"m": m_max, "flat_recall": flat_at_max, "paged_exact_recall": pe_at_max,
                     "paged_lossy_recall": pl_at_max},
        "m_flat_crater": m_flat_crater,
        "paged_exact_hold_up_to_m": pe_hold,
        "effective_wm_extension_factor": extension_factor,
        "exact_minus_flat_at_max": exact_minus_flat,
        "exact_minus_lossy_at_max": exact_minus_lossy,
        "interface_writes_per_item_at_max": interface_writes_per_item,
        "interface_reads_per_query_at_max": interface_reads_per_query,
        "discriminator_fired": flat_fired,
        "sweep": sweep,
        "REQUIRED_FIELDS": ["anchor_name", "verdict", "verdict_msg", "at_m_max",
                            "effective_wm_extension_factor", "sweep"],
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
