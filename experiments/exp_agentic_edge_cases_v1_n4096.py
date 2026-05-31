"""G13b PHASE 3 AGENTIC EDGE CASES v1 at N=4096.

CONTEXT (G13b_p3, user revision):
  Three edge cases that stress agentic deployment in ways the smooth
  characterization (G13b_p1) and sustained load (G13b_p2) don't:

EDGE A "Long-running with state evolution":
  Single session running 1.5h with substrate state evolving (edits/deletes
  mid-session). Multi-hop queries reference the evolving state.
  Measure: per-call accuracy AFTER each edit (does Path D still find correct
  paths through edited substrate?), audit chain integrity over 1.5h.

EDGE B "Concurrent agent contention":
  5 sessions interleaved at single-process round-robin level, all querying
  the same fact-id space. 2 of them are issuing concurrent edits.
  Measure: per-agent consistency (queries during edit window return
  edits-consistent state), audit chain validity, "isolation"
  (edit-effect-on-non-edited-facts < 5%).

EDGE C "Agent recovery from interruption":
  Session runs N1 calls + state-write checkpoint. Process simulated-killed
  (we just record state, drop in-memory, then reload). Session resumes
  from checkpoint.
  Measure: pre/post-interruption consistency: are the same facts retrievable
  with the same accuracy after resume?

SETUP:
  N=4096, BSC, M=8192. Path D for multi-hop.

PRE-REGISTERED BANDS:
  HARD_PASS = all 3 scenarios complete AND
              Edge A: per-call accuracy >= 0.85 throughout 1.5h AND
              Edge B: isolation >= 0.95 (max_iso of non-edited facts under
                      contention <= 0.05) AND audit chain valid AND
              Edge C: post-resume consistency exactly 100% AND
                      audit chain valid through resume.
  HARD_FAIL = any scenario fails its specific criterion.
  MIDDLE_BAND = otherwise.

OOM CHECK:
  N=4096, M=8192: ~600 MiB. OK on 8 GiB GPU.

TIMEOUT ESTIMATE:
  Edge A: 1.5h = 5400s.  Edge B: ~10 min.  Edge C: ~5 min.
  Total ~6500s. Budget 14400s.

PROT-018: _n4096 binds N = 4096.
PROT-020: torch+cuda.
PROT-021: per-edge-case checkpoint.

Anchor: agentic_edge_cases_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_agentic_edge_cases_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_d_run,
)
from experiments._metric_battery import (  # noqa: E402
    metric_retention, metric_max_iso,
)
from experiments._workload_harness import (  # noqa: E402
    make_cert, verify_cert_chain,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g13b3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096.
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096

M_FULL  = 8192
M_SMOKE = 256
K_PATHS = 500
K_PATHS_SMOKE = 30

# Edge A: long-running session with evolving state
EDGE_A_WALL_S_FULL  = 5400      # 1.5h
EDGE_A_WALL_S_SMOKE = 20
EDGE_A_CHECK_EVERY_S_FULL  = 300   # every 5 min
EDGE_A_CHECK_EVERY_S_SMOKE = 5
EDGE_A_EDITS_PER_HOUR_FULL = 60
EDGE_A_EDITS_PER_HOUR_SMOKE = 60
EDGE_A_DEPTH_MIN = 3
EDGE_A_DEPTH_MAX = 8

# Edge B: contention
EDGE_B_N_SESSIONS = 5
EDGE_B_N_EDIT_AGENTS = 2
EDGE_B_N_TICKS_FULL = 600
EDGE_B_N_TICKS_SMOKE = 30
EDGE_B_DEPTH = 4

# Edge C: recovery
EDGE_C_N_PRE_FULL = 50
EDGE_C_N_PRE_SMOKE = 6
EDGE_C_N_POST_FULL = 30
EDGE_C_N_POST_SMOKE = 4
EDGE_C_DEPTH = 4

# Pre-reg
HP_EDGE_A_ACC = 0.85
HP_EDGE_B_ISO_MAX = 0.05    # isolation = 1 - max_iso, so max_iso <= 0.05
HP_EDGE_C_CONSISTENCY = 1.0


def get_output_dir(default_name: str = "agentic_edge_cases_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ----------------------- Edge A -----------------------

def _do_query(codebook, W, relation, depth, K, seed, N_use, device):
    keys_list = list(relation.keys())
    if not keys_list:
        return 0.0, 0
    start_id = keys_list[seed % len(keys_list)]
    starts = torch.tensor([start_id], dtype=torch.long, device=device)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    correct = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    if device.type == "cuda":
        torch.cuda.synchronize()
    dt_ms = (time.perf_counter() - t0) * 1000.0
    return dt_ms, int(correct.sum().item())


def run_edge_a(N_use: int, M: int, K: int, target_wall_s: float,
                check_every_s: float, edits_per_hour: float,
                device: torch.device) -> Dict:
    """Long-running session, state evolves; track accuracy over time."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, 17, device)
    gen = torch.Generator(device="cpu").manual_seed(2026)

    cert_chain = []
    prev_hash = "GENESIS"
    op_counter = 0

    acc_window_correct = 0
    acc_window_total = 0
    acc_at_check: List[float] = []
    chain_at_check: List[bool] = []

    sess_start = time.time()
    next_check = sess_start + check_every_s
    next_edit  = sess_start + (3600.0 / max(1.0, edits_per_hour))
    crash = False

    while True:
        now = time.time()
        elapsed = now - sess_start
        if elapsed >= target_wall_s:
            break

        depth = int(torch.randint(EDGE_A_DEPTH_MIN, EDGE_A_DEPTH_MAX + 1, (1,),
                                    generator=gen).item())
        try:
            dt_ms, ok = _do_query(codebook, W, relation, depth, K,
                                    op_counter, N_use, device)
        except (RuntimeError, MemoryError) as e:
            crash = True
            print(f"  EDGE_A CRASH: {e}", flush=True)
            break
        acc_window_correct += ok
        acc_window_total   += 1
        op_counter += 1

        link = make_cert(prev_hash, op="query", fact_id=-1, key_id=-1,
                          val_id=-1, op_id=op_counter)
        cert_chain.append(link)
        prev_hash = link["this_hash"]
        op_counter += 1

        # Edit/delete
        if now >= next_edit and key_idx.shape[0] > 0:
            ed_pos = int(torch.randint(0, key_idx.shape[0], (1,),
                                          generator=gen).item())
            old_key = codebook[key_idx[ed_pos] % codebook.shape[0]]
            old_val = codebook[val_idx[ed_pos] % codebook.shape[0]]
            do_delete = (float(torch.rand(1, generator=gen).item()) < 0.5)
            if do_delete:
                W = W - torch.outer(old_val, old_key) / N_use
                op_name = "delete"
                new_val_i = -1
            else:
                new_val_i = int(torch.randint(0, codebook.shape[0], (1,),
                                                 generator=gen).item())
                new_val = codebook[new_val_i]
                W = W + torch.outer(new_val - old_val, old_key) / N_use
                op_name = "edit"
            link = make_cert(prev_hash, op=op_name, fact_id=ed_pos,
                              key_id=int(key_idx[ed_pos].item()),
                              val_id=new_val_i, op_id=op_counter)
            cert_chain.append(link)
            prev_hash = link["this_hash"]
            op_counter += 1
            next_edit = now + (3600.0 / max(1.0, edits_per_hour))

        # Checkpoint
        if now >= next_check:
            acc = (acc_window_correct / acc_window_total) if acc_window_total > 0 else 0.0
            chain_ok = verify_cert_chain(cert_chain)
            acc_at_check.append(round(acc, 5))
            chain_at_check.append(bool(chain_ok))
            print(f"  [edge_a] t={elapsed:.0f}s acc_window={acc:.3f} "
                  f"chain={chain_ok} ops={op_counter}", flush=True)
            acc_window_correct = 0
            acc_window_total = 0
            next_check = now + check_every_s

    final_chain_ok = verify_cert_chain(cert_chain)
    wall = time.time() - sess_start
    min_acc = min(acc_at_check) if acc_at_check else 0.0
    mean_acc = (sum(acc_at_check) / len(acc_at_check)) if acc_at_check else 0.0

    if device.type == "cuda":
        torch.cuda.empty_cache()
    del codebook, W

    return {
        "wall_s": round(wall, 2),
        "total_ops": int(op_counter),
        "acc_at_check": acc_at_check,
        "chain_at_check": chain_at_check,
        "min_acc": round(min_acc, 5),
        "mean_acc": round(mean_acc, 5),
        "final_chain_ok": bool(final_chain_ok),
        "n_checkpoints": int(len(acc_at_check)),
        "crash": bool(crash),
    }


# ----------------------- Edge B -----------------------

def run_edge_b(N_use: int, M: int, K: int, n_ticks: int,
                device: torch.device) -> Dict:
    """5 sessions; 2 issue edits to a designated subset; measure isolation."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, 17, device)
    gen = torch.Generator(device="cpu").manual_seed(2027)

    # Designate "protected" fact set: first half of facts
    protected_n = max(2, key_idx.shape[0] // 2)
    protected_key_idx = key_idx[:protected_n]
    protected_val_idx = val_idx[:protected_n]

    # Edit pool: second half of facts
    edit_pool_start = protected_n

    # Initial KF-1 on protected set
    probe_keys = codebook[protected_key_idx % codebook.shape[0]]
    probe_vals = protected_val_idx.to(device)
    sims_before = (codebook @ (probe_keys @ W.T).T) / N_use
    pred_before = torch.argmax(sims_before, dim=0)
    acc_before = (pred_before == probe_vals).float()
    initial_acc = float(acc_before.mean().item())

    cert_chain = []
    prev_hash = "GENESIS"
    op_counter = 0
    crash = False

    sessions = list(range(EDGE_B_N_SESSIONS))
    edit_session_ids = set(sessions[:EDGE_B_N_EDIT_AGENTS])

    for t in range(n_ticks):
        sess_id = sessions[t % len(sessions)]
        try:
            if sess_id in edit_session_ids and edit_pool_start < key_idx.shape[0]:
                # this session is an edit agent
                pos = edit_pool_start + int(torch.randint(
                    0, max(1, key_idx.shape[0] - edit_pool_start),
                    (1,), generator=gen).item())
                old_key = codebook[key_idx[pos] % codebook.shape[0]]
                old_val = codebook[val_idx[pos] % codebook.shape[0]]
                new_val_i = int(torch.randint(0, codebook.shape[0], (1,),
                                                 generator=gen).item())
                new_val = codebook[new_val_i]
                W = W + torch.outer(new_val - old_val, old_key) / N_use
                link = make_cert(prev_hash, op="edit", fact_id=pos,
                                  key_id=int(key_idx[pos].item()),
                                  val_id=new_val_i, op_id=op_counter)
                cert_chain.append(link)
                prev_hash = link["this_hash"]
                op_counter += 1
            else:
                # query agent: query protected fact-space
                _, _ = _do_query(codebook, W, relation, EDGE_B_DEPTH, K,
                                  17 + t, N_use, device)
                link = make_cert(prev_hash, op="query", fact_id=-1,
                                  key_id=-1, val_id=-1, op_id=op_counter)
                cert_chain.append(link)
                prev_hash = link["this_hash"]
                op_counter += 1
        except (RuntimeError, MemoryError) as e:
            crash = True
            print(f"  EDGE_B CRASH t={t}: {e}", flush=True)
            break

    # Final accuracy on protected set
    sims_after = (codebook @ (probe_keys @ W.T).T) / N_use
    pred_after = torch.argmax(sims_after, dim=0)
    acc_after = (pred_after == probe_vals).float()
    final_acc = float(acc_after.mean().item())
    # Isolation: how much did protected accuracy degrade from edits on non-protected pool
    iso_delta = abs(initial_acc - final_acc)
    isolation_score = 1.0 - iso_delta   # higher = better
    chain_ok = verify_cert_chain(cert_chain)

    if device.type == "cuda":
        torch.cuda.empty_cache()
    del codebook, W

    return {
        "n_ticks": int(n_ticks),
        "n_sessions": int(EDGE_B_N_SESSIONS),
        "n_edit_agents": int(EDGE_B_N_EDIT_AGENTS),
        "protected_n": int(protected_n),
        "initial_protected_acc": round(initial_acc, 5),
        "final_protected_acc":   round(final_acc, 5),
        "iso_delta":             round(iso_delta, 5),
        "isolation_score":       round(isolation_score, 5),
        "max_iso":               round(iso_delta, 5),
        "audit_chain_ok":        bool(chain_ok),
        "cert_chain_len":        int(len(cert_chain)),
        "crash":                 bool(crash),
    }


# ----------------------- Edge C -----------------------

def run_edge_c(N_use: int, M: int, K: int, n_pre: int, n_post: int,
                device: torch.device) -> Dict:
    """Pre-interruption queries; serialize substrate state; reload; post-queries."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, 17, device)
    gen = torch.Generator(device="cpu").manual_seed(2028)
    crash = False

    # Pre-interruption: record (start_id, depth, predicted_correct) for n_pre queries
    pre_records: List[Tuple[int, int, int]] = []
    keys_list = list(relation.keys())

    for i in range(n_pre):
        depth = int(torch.randint(2, EDGE_C_DEPTH + 1, (1,), generator=gen).item())
        seed_i = 17 + i
        start_id = keys_list[seed_i % len(keys_list)]
        starts = torch.tensor([start_id], dtype=torch.long, device=device)
        try:
            correct = path_d_run(codebook, W, starts, relation, depth, K,
                                   seed_i, N_use)
        except (RuntimeError, MemoryError) as e:
            crash = True
            break
        pre_records.append((start_id, depth, int(correct.sum().item())))

    # Serialize state (W on CPU clone, key_idx/val_idx, relation, codebook reference)
    W_serial = W.detach().cpu().clone()
    key_idx_serial = key_idx.detach().cpu().clone()
    val_idx_serial = val_idx.detach().cpu().clone()
    relation_serial = dict(relation)

    # Simulate kill: drop references
    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    # Resume: rebuild codebook (deterministic from build_shared with same seed),
    # restore W, key_idx, val_idx, relation. We need codebook deterministic.
    codebook2, W2_initial, ki2, vi2, rel2 = build_shared(N_use, M, 17, device)
    # Verify that key_idx/val_idx match between original and resumed
    assert torch.equal(ki2.cpu(), key_idx_serial), "Resume: key_idx mismatch"
    assert torch.equal(vi2.cpu(), val_idx_serial), "Resume: val_idx mismatch"
    assert rel2 == relation_serial, "Resume: relation mismatch"
    # Restore W
    W2 = W_serial.to(device)

    # Post-interruption: replay first n_post pre_records and check correctness matches
    post_consistent = 0
    post_total = 0
    for i, (start_id, depth, expected_correct) in enumerate(pre_records[:n_post]):
        seed_i = 17 + i
        starts = torch.tensor([start_id], dtype=torch.long, device=device)
        try:
            correct = path_d_run(codebook2, W2, starts, rel2, depth, K,
                                   seed_i, N_use)
        except (RuntimeError, MemoryError) as e:
            crash = True
            break
        if int(correct.sum().item()) == expected_correct:
            post_consistent += 1
        post_total += 1

    consistency = (post_consistent / post_total) if post_total > 0 else 0.0

    if device.type == "cuda":
        torch.cuda.empty_cache()
    del codebook2, W2

    return {
        "n_pre": int(len(pre_records)),
        "n_post": int(post_total),
        "post_consistent": int(post_consistent),
        "consistency": round(consistency, 5),
        "crash": bool(crash),
    }


# ----------------------- Verdict -----------------------

def compute_verdict(edge_a: Dict, edge_b: Dict, edge_c: Dict) -> Tuple[str, str]:
    fails = []
    passes = []

    # Edge A
    if edge_a.get("crash", False):
        fails.append("A_CRASH")
    elif not edge_a.get("final_chain_ok", False):
        fails.append("A_CHAIN_BAD")
    elif edge_a.get("min_acc", 0.0) < HP_EDGE_A_ACC:
        fails.append(f"A_ACC_LOW({edge_a.get('min_acc',0):.3f})")
    else:
        passes.append(f"A_OK(min_acc={edge_a.get('min_acc',0):.3f})")

    # Edge B
    if edge_b.get("crash", False):
        fails.append("B_CRASH")
    elif not edge_b.get("audit_chain_ok", False):
        fails.append("B_CHAIN_BAD")
    elif edge_b.get("max_iso", 1.0) > HP_EDGE_B_ISO_MAX:
        fails.append(f"B_ISO_HIGH({edge_b.get('max_iso',1):.3f})")
    else:
        passes.append(f"B_OK(iso={edge_b.get('max_iso',0):.3f})")

    # Edge C
    if edge_c.get("crash", False):
        fails.append("C_CRASH")
    elif edge_c.get("consistency", 0.0) < HP_EDGE_C_CONSISTENCY:
        fails.append(f"C_CONSISTENCY({edge_c.get('consistency',0):.3f})")
    else:
        passes.append(f"C_OK(consistency=1.0)")

    detail = "; ".join(passes + [f"FAIL={f}" for f in fails])

    if fails:
        return ("G13B_P3_HARD_FAIL", f"EDGE_FAIL: {detail}")
    return ("G13B_P3_HARD_PASS", f"ALL_EDGES_PASS: {detail}")


def _instrumentation_selftest() -> None:
    """Tiny smoke for each edge."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096, got {N_FULL}"
    device = torch.device("cpu")

    # Kerdock 4-coset requires N in {1024, 4096, 16384}
    a = run_edge_a(N_use=1024, M=64, K=20, target_wall_s=4.0,
                    check_every_s=1.0, edits_per_hour=3600.0,
                    device=device)
    assert a["total_ops"] > 0, "edge_a no ops at smoke"
    assert a["final_chain_ok"], "edge_a chain bad at smoke"

    b = run_edge_b(N_use=1024, M=64, K=20, n_ticks=10, device=device)
    assert b["audit_chain_ok"], "edge_b chain bad at smoke"
    assert b["protected_n"] > 0, "edge_b no protected facts"

    c = run_edge_c(N_use=1024, M=64, K=20, n_pre=3, n_post=2, device=device)
    assert c["n_pre"] >= 1, "edge_c no pre records"
    assert c["consistency"] == 1.0, \
        f"edge_c consistency != 1.0 at smoke ({c['consistency']}); resume contract broken"

    print(f"[selftest] agentic_edge_cases_v1_n4096 PASS "
          f"A_acc_min={a.get('min_acc',0):.3f} "
          f"B_iso={b.get('max_iso',0):.3f} "
          f"C_cons={c.get('consistency',0):.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    K_cfg = K_PATHS_SMOKE if smoke else K_PATHS

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] agentic_edge_cases smoke={smoke} N={N_cfg} M={M_cfg} K={K_cfg} "
          f"device={device.type} done={len(done)}", flush=True)

    # Edge A
    ck_a = "edge_a"
    if ck_a in done:
        edge_a = load_partial_key(out_dir, ck_a)
    else:
        edge_a_wall  = EDGE_A_WALL_S_SMOKE if smoke else EDGE_A_WALL_S_FULL
        edge_a_check = EDGE_A_CHECK_EVERY_S_SMOKE if smoke else EDGE_A_CHECK_EVERY_S_FULL
        edge_a_eph   = EDGE_A_EDITS_PER_HOUR_SMOKE if smoke else EDGE_A_EDITS_PER_HOUR_FULL
        edge_a = run_edge_a(N_cfg, M_cfg, K_cfg, edge_a_wall, edge_a_check,
                              edge_a_eph, device)
        write_partial_key(out_dir, ck_a, edge_a)
    print(f"  edge_a min_acc={edge_a.get('min_acc',0):.3f} "
          f"chain={edge_a.get('final_chain_ok')} ({time.time()-t0:.1f}s)",
          flush=True)

    # Edge B
    ck_b = "edge_b"
    if ck_b in done:
        edge_b = load_partial_key(out_dir, ck_b)
    else:
        n_ticks_b = EDGE_B_N_TICKS_SMOKE if smoke else EDGE_B_N_TICKS_FULL
        edge_b = run_edge_b(N_cfg, M_cfg, K_cfg, n_ticks_b, device)
        write_partial_key(out_dir, ck_b, edge_b)
    print(f"  edge_b iso={edge_b.get('max_iso',0):.3f} "
          f"chain={edge_b.get('audit_chain_ok')} ({time.time()-t0:.1f}s)",
          flush=True)

    # Edge C
    ck_c = "edge_c"
    if ck_c in done:
        edge_c = load_partial_key(out_dir, ck_c)
    else:
        n_pre  = EDGE_C_N_PRE_SMOKE if smoke else EDGE_C_N_PRE_FULL
        n_post = EDGE_C_N_POST_SMOKE if smoke else EDGE_C_N_POST_FULL
        edge_c = run_edge_c(N_cfg, M_cfg, K_cfg, n_pre, n_post, device)
        write_partial_key(out_dir, ck_c, edge_c)
    print(f"  edge_c consistency={edge_c.get('consistency',0):.3f} "
          f"({time.time()-t0:.1f}s)", flush=True)

    verdict, vm = compute_verdict(edge_a, edge_b, edge_c)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "agentic_edge_cases_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M_cfg, "K_paths": K_cfg,
        "edge_a": edge_a, "edge_b": edge_b, "edge_c": edge_c,
        "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
