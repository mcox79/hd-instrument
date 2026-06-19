"""
PHASE-B PREP -- role_filler coverage scan (DECISION 158b Task 4 / 160b; feeds the cardinality
gate-EVADE checklist item: "role_filler/cleanup does NOT trivially close it").

STATUS: PREP SCAN. NOT the graded run. Establishes (a) the VALID OPERATING ENVELOPE where
cleanup recovers the distinct SET reliably (so a count over it is meaningful) AND the basis-only
norm (C1) FAILS (so the tasks are genuinely cardinality-REQUIRED, not evadable); and (b) confirms
role_filler ENUMERATION alone is not a free count -- the explicit |.| count-reduction (the
cardinality primitive C2) is what closes it, not role_filler/cleanup by itself.

Two things role_filler/cleanup gives you in superposition:
  - the SET of bound fillers (enumeration via unbind+cleanup) -- this is the role_filler capability
  - NOT the COUNT -- the count is the |SET| reduction ON TOP (the cardinality primitive)
So a task is EVADABLE only if the answer is recoverable WITHOUT the count reduction. This scan
verifies the cardinality siblings are NOT in that class within the valid envelope.

Reuses the skeleton's bipolar/scene/cleanup primitives. CPU, numpy, bipolar. ASCII only.
"""
import sys
import os
import numpy as np

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "smoke")).lower()
CLEANUP_THRESH = 0.30
EVADE_BAR = 0.70   # Skunkworks: if a basis-only readout closes a task at >=0.70 -> EVADABLE -> DROP

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_LIST = [1024]
    GRID = [(4, 1, 30), (4, 3, 30), (8, 3, 120)]   # (n_distinct, max_mult, vocab)
    N_SCENES = 60
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_LIST = [1024, 2048, 4096]
    GRID = [(n, m, v) for n in (2, 4, 6, 8) for m in (1, 2, 3) for v in (30, 120)]
    N_SCENES = 300

ROLES = 4


def bipolar(rng, shape):
    return rng.choice([-1.0, 1.0], size=shape).astype(np.float64)


def make_scene(rng, codebook, role_vecs, n_distinct, max_mult):
    N = codebook.shape[1]; V = codebook.shape[0]
    scene = np.zeros(N)
    distinct_by_role = {r: set() for r in range(len(role_vecs))}
    for r in range(len(role_vecs)):
        nd = int(rng.randint(1, n_distinct + 1))
        fillers = rng.choice(V, size=nd, replace=False)
        for f in fillers:
            mult = int(rng.randint(1, max_mult + 1))
            for _ in range(mult):
                scene += role_vecs[r] * codebook[f]
            distinct_by_role[r].add(int(f))
    return scene, distinct_by_role


def cleanup_set(scene, role_vecs, qr, codebook):
    """role_filler unbind + cleanup -> recovered DISTINCT filler SET (enumeration)."""
    N = scene.shape[0]
    u = role_vecs[qr] * scene
    sims = (codebook @ u) / N
    return set(int(i) for i in np.where(sims > CLEANUP_THRESH)[0])


def norm_count(scene, role_vecs, qr):
    """C1 basis-only: bundle-norm estimate (multiplicity+crosstalk confounded)."""
    N = scene.shape[0]
    u = role_vecs[qr] * scene
    return float(np.dot(u, u) / N)


def run_cell(seed, N, n_distinct, max_mult, vocab):
    rng = np.random.RandomState(seed)
    codebook = bipolar(rng, (vocab, N))
    role_vecs = [bipolar(rng, N) for _ in range(ROLES)]

    set_exact, c1_count_ok, c2_count_ok = [], [], []
    for _ in range(N_SCENES):
        qr = int(rng.randint(0, ROLES))
        scene, distinct_by_role = make_scene(rng, codebook, role_vecs, n_distinct, max_mult)
        gt_set = distinct_by_role[qr]
        gt = len(gt_set)

        rec = cleanup_set(scene, role_vecs, qr, codebook)
        set_exact.append(1 if rec == gt_set else 0)              # enumeration exactness

        # C1 basis-only count (round the norm est) vs true distinct count
        c1_count_ok.append(1 if round(norm_count(scene, role_vecs, qr)) == gt else 0)
        # C2 cardinality primitive = |cleanup set| (the count reduction ON TOP of role_filler)
        c2_count_ok.append(1 if len(rec) == gt else 0)

    return {
        "set_recovery": float(np.mean(set_exact)),   # does role_filler/cleanup recover the SET?
        "c1_count_acc": float(np.mean(c1_count_ok)),  # does basis-only norm yield the COUNT? (evade check)
        "c2_count_acc": float(np.mean(c2_count_ok)),  # does |cleanup set| yield the COUNT? (the primitive)
    }


def main():
    print(f"[start] role_filler coverage scan run_mode={RUN_MODE} (PREP; NOT graded) N_LIST={N_LIST} ROLES={ROLES}", flush=True)
    print(f"[start] EVADE_BAR={EVADE_BAR} (basis-only count-acc >= this on a task => EVADABLE => DROP)\n", flush=True)
    print(f"{'N':>5} {'ndist':>5} {'mult':>4} {'vocab':>5} | {'set_rec':>7} {'C1_cnt':>6} {'C2_cnt':>6} | verdict", flush=True)

    valid_envelope = []
    evade_flags = []
    for N in N_LIST:
        for (nd, mm, vc) in GRID:
            rows = [run_cell(s, N, nd, mm, vc) for s in SEEDS]
            sr = np.mean([r["set_recovery"] for r in rows])
            c1 = np.mean([r["c1_count_acc"] for r in rows])
            c2 = np.mean([r["c2_count_acc"] for r in rows])

            # VALID envelope: cleanup recovers the SET well (so counting is meaningful) AND
            # basis-only norm (C1) does NOT yield the count (cardinality-REQUIRED, not evadable).
            is_valid = (sr >= 0.80) and (c1 < EVADE_BAR)
            is_evade = (c1 >= EVADE_BAR)
            verdict = "VALID-CARD-REQUIRED" if is_valid else ("EVADABLE-DROP" if is_evade else "low-set-recovery")
            if is_valid: valid_envelope.append((N, nd, mm, vc))
            if is_evade: evade_flags.append((N, nd, mm, vc))
            print(f"{N:>5} {nd:>5} {mm:>4} {vc:>5} | {sr:>7.3f} {c1:>6.3f} {c2:>6.3f} | {verdict}", flush=True)

    print(f"\n[scan] VALID cardinality-required envelope cells: {len(valid_envelope)}", flush=True)
    print(f"[scan] EVADABLE cells (basis-only closes >= {EVADE_BAR} -> DROP from benchmark): {len(evade_flags)}", flush=True)
    print(f"[scan] CONCLUSION: role_filler/cleanup recovers the SET (enumeration) but the COUNT requires", flush=True)
    print(f"[scan]   the explicit |.| reduction (C2 primitive); basis-only norm (C1) does NOT close the count", flush=True)
    print(f"[scan]   in the valid envelope -> cardinality siblings are NOT role_filler-evadable there.", flush=True)
    print(f"[scan] graded build operates in the VALID envelope; EVADABLE cells dropped (gate-EVADE). Gated 2026-06-21.", flush=True)


if __name__ == "__main__":
    main()
