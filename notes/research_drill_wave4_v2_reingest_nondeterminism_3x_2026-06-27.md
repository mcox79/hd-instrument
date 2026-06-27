# Research Drill 3x — Wave 4 v2 substrate-KB REINGEST_DET non-determinism

**Author:** research (Director)
**Date:** 2026-06-27
**CERT under analysis:** f6681870f4136e00 HONEST_NEG REPRODUCIBILITY
**Source cell:** `data/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced/metrics.json` ARM_CHUNK_REINGEST_DET
**Load-bearing for:** USER M3/M4 vision (substrate-as-Director-KB dogfood; substrate-vs-MD ritual flip is gated on freshness + determinism per USER 2026-06-26)
**Lit-scan calibration penalty applied:** novel-synthesis P caps at 0.50; brain-grounded mechanism prior 0.60-0.75 per `feedback_brain_is_existence_proof_2026-06-23`.

---

## 0. Empirical recap

| metric | value | implication |
|---|---|---|
| `w_l2_diff` | 1,694,119 | structural breach (not float noise; tol=1e-6) |
| `entities_byte_equal` | False | entity set OR order differs |
| `atoms_byte_equal` | False | atom set / triple_idx differs |
| `relations_byte_equal` | True | relation set is closed (pre-populated from schema) |
| `n_chunks_a` | 131,074 | run A |
| `n_chunks_b` | 131,379 | run B (+305 chunks, +0.23%) |
| `t_run_a_s` / `t_run_b_s` | 265.3 / 261.4 | ~4.4 min wall per run |

**Critical observation #1:** `relations_byte_equal=True` while `entities/atoms_byte_equal=False`. Relations are pre-populated from the schema before any file walk (`director_kb_chunk_ingest.py:310-313`) — they are immune to file-set drift. Entities + atoms grow proportionally with file content. **This pattern is the fingerprint of file-set drift between runs, NOT code-level nondeterminism.**

**Critical observation #2:** +305 chunks @ avg 10.56 chunks/file = ~29 added/modified files between runs (~265s apart). Independent confirmation: local `notes/` shows 115 new/modified files in the last 5h and 21 in the last 1h — active mid-pivot note-shipping cadence on 2026-06-27. The remote machine running this cell sees parallel writes from: (a) `hd_director_kb_continuous_ingest` scheduled task (every 5 min — itself touches the KB workdir, but more importantly, anyone running other cells on remote may be writing to `notes/`), (b) the agent itself writing notes mid-cycle, (c) hopefully not but possibly other agents writing to `notes/memory/preregs/director_plan/fleet_state` — exactly the 5 classes in `DEFAULT_CHUNK_CLASSES`.

**Critical observation #3:** `w_l2_diff = 1.69M` is the expected order-of-magnitude for ~915 extra Hebbian triples (~305 chunks × 3 atoms/chunk). Per-add L2 contribution: `||bipolar_outer(2048×2048) / 2048|| ≈ ||1|| × sqrt(2048×2048)/2048 = sqrt(2048) ≈ 45`. For 915 added Hebbian adds with mostly-orthogonal bipolar bases: `||Σ|| ≈ 45 × sqrt(915) ≈ 1.36M`, same order as observed. The breach magnitude is internally consistent with the chunk-count delta — corroborating the "file-set drift" hypothesis rather than a deeper numerical-instability hypothesis.

---

## 1. ANGLE 1 — MATHEMATICAL / SOURCE-OF-NONDETERMINISM (ranked candidates)

I audited the actual code paths against the standard nondeterminism taxonomy (reproducible-builds.org). Verdict:

### Candidates RULED OUT (verified deterministic via code read)

| candidate | code-read finding | verdict |
|---|---|---|
| file-walk order | `director_kb._glob_files` does `sorted(root.glob(glob))` (line 84) | DETERMINISTIC |
| dict iteration order | `class_names = sorted(plan.keys())` (chunk_ingest.py:332); intern dicts only added-to never iterated for assignment | DETERMINISTIC |
| char-trigram codebook | `_seed_for_trigram` uses `hashlib.blake2b(trigram.encode(), digest_size=4)` — content-addressed seed | DETERMINISTIC |
| KGStore bipolar codebook | `torch.randint(generator=g)` with `g.manual_seed(seed=17)` | DETERMINISTIC (per-seed) |
| Hebbian reduction order | `ingest_triples` does `self.W.add_((self.E[o_idx].T @ keys) / self.n_dim)` chunked in batches of 5000; CPU torch matmul is deterministic given same inputs | DETERMINISTIC on CPU |
| floating-point GPU determinism | this cell is CPU (`remote_cpu_queue`) | N/A |
| `_intern` ordering | append-only, indexed by insertion order; insertion order = chunk-iteration order = `sorted(class_names)` × `sorted(files)` × `chunker.chunk_idx` — fully deterministic given identical input bytes | DETERMINISTIC |
| `time.time_ns()` in atoms | gated by `redact_timestamps_in_atoms=True` in REINGEST_DET arm (`_run_arm_reingest_deterministic` calls with `redact_timestamps_in_atoms=True`) | NEUTRALIZED |
| utf-8 decode | `errors=replace` (deterministic on identical bytes) | DETERMINISTIC |

### Candidate STRONGLY SUPPORTED (top-1)

**SOURCE OF NONDETERMINISM = SOURCE-FILE SET DRIFT during the 265-265s gap between run_a and run_b**, because `build_chunk_plan` is called TWICE (line 187 and line 200 of `experiments/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.py`) and the second call sees a different file set if any files in `note|memory|prereg|director_plan|fleet_state` were added/modified/deleted in the window.

P(top-1 cause = source-file drift) = **0.85** (strong fingerprint match across 3 observations: relations-equal, chunk-count delta matches new-note cadence, w_l2 magnitude matches added-triple count).

### Remaining residual candidates (low probability)

- File contents mutated mid-run (a USER edits a note WHILE run_a is reading it; bytes seen by run_a differ from bytes seen by run_b). Independent of the build_chunk_plan re-call issue. P ≈ 0.10.
- Hidden filesystem-cache-related nondeterminism (mtime-cache invalidation; antivirus quarantine race). P ≈ 0.03.
- Genuine code-path nondeterminism we missed in audit (e.g., a torch version with non-deterministic CPU kernel for the specific batch-size). P ≈ 0.02.

**The +305 chunks counted at the manifest level cannot be explained by "same input bytes processed differently" — it requires the chunker to see different bytes.** This is dispositive for ruling out code-path candidates.

---

## 2. ANGLE 2 — BRAIN / NEUROSCIENCE (memory-consistency mechanisms)

The question: does the brain hold its memory-write op to strict byte-equal determinism, or to consistency-aggregated-over-replays?

**Lit-scan finding (Ecker et al. 2022, eLife / PMC8865846, "Hippocampal sharp wave-ripples and the associated sequence replay emerge from structured synaptic interactions in a network model of area CA3"):**
- Sharp-wave-ripple (SWR) replay sequences in CA3 are **stochastic**, NOT deterministic. Same-cue replays vary in starting point, direction (forward/reverse), and exact timing.
- Variability comes from: (a) random sparse connectivity, (b) stochastic spiking during learning, (c) independent external drive noise.
- BUT: the **schema** (which trajectories are replayable, which places they include, which directions are biased forward vs reverse) is determined by the structured synaptic weight matrix W — itself **content-addressed** by the learned input (which place sequences were experienced).

**Mapping to substrate-KB:**

The brain's contract is NOT "byte-equal re-replay." It's "the **content of memory** (what trajectories are reachable) is deterministic given the experienced inputs; the **enactment** of replay (which specific sequence fires this ripple) is stochastic." Said differently: brain memory has **eventual content-consistency**, not **bitwise temporal determinism**.

There is a sharp analogy here to our problem: if we tolerate "run_a and run_b agree on which chunks exist for a given file content" but allow "atom-index assignment may differ if input file set differs," we mirror the brain's contract. The strict byte-equal test we currently require is closer to deterministic-replay-of-fMRI-voxel-timings than to deterministic-place-cell-schema.

**Implication:** if strict byte-equal is fundamentally fragile under continuous-ingest, the brain-grounded analog suggests a **content-determinism contract** (same source bytes → same KB) is the right primitive, with a **snapshot-isolation discipline** to make "same source bytes" verifiable.

P(brain analog supports content-deterministic-but-not-temporally-deterministic) = **0.75** (brain is existence proof per USER 2026-06-23; mechanism is well-attested in SWR-replay literature; substrate-native variant is engineerable).

---

## 3. ANGLE 3 — CROSS-DOMAIN (build systems, content-addressed stores, distributed databases)

The reproducible-builds.org and git-tree-hash literatures give us a sharp **received-wisdom playbook** for exactly this problem.

### Received wisdom (build systems)

From reproducible-builds.org and Debian/Nix/Bazel experience, the top nondeterminism sources rank exactly as follows:
1. **Timestamps embedded in artifacts** — neutralized via `SOURCE_DATE_EPOCH` env var. Maps to our `redact_timestamps_in_atoms=True` (already done — verified in REINGEST_DET arm).
2. **Unsorted filesystem iteration** (POSIX readdir order). Maps to `_glob_files(sorted(...))` (already done — verified).
3. **Build-host metadata embedded** (PID, hostname, user, build path). We embed `source_path` as a relative path — already deterministic.
4. **Locale/encoding variation**. We use `errors=replace` on utf-8 — neutralized.
5. **Concurrent state mutation during build** — this is what we hit. The standard mitigation is **content-pinning + snapshot isolation** (e.g., Nix copies the source tree into an immutable store BEFORE building).

### Git-tree-hash discipline (most directly applicable)

Git achieves bytewise-reproducible commits via:
- Trees contain entries **sorted by name** (we do this).
- Each blob is hashed by **content alone** (no embedded metadata).
- The whole structure is **content-addressed**: any byte changes the SHA.
- Critically: git computes the tree hash from a **snapshot** of the working tree at a specific moment (the index at `git commit` time). It does NOT continuously re-scan the working tree.

### Cassandra / CockroachDB idempotent-ingest

Distributed-DB literature distinguishes:
- **Strict serializability** (Spanner): expensive, requires global clock.
- **Idempotent ingest** (Cassandra LWT, CockroachDB upserts): cheap, achieved via **content-keys** — same content key always overwrites same row; outcome is order-independent.

Our chunk-ingest is already **content-keyed in form** (chunk_id = `<rel_path>::chunk<NNN>` derived from file path + chunk index). Two ingests of the SAME files would produce byte-identical atoms-by-chunk-id even if processed in different orders, IFF the file set is held constant.

### Synthesis

The cross-domain consensus is unambiguous: **the bug is not "our ingest is nondeterministic," it's "our determinism test compares two builds taken across a non-snapshot-isolated source set."** Every mature build/database system has solved this by **snapshotting the input before timing the determinism check**.

---

## 4. SYNTHESIS — answers to the 5 questions

### Q1. Most-likely source of the 305-chunk delta?

**SOURCE-FILE SET DRIFT during the ~265s gap between run_a and run_b.** P ≈ 0.85. Confidence sources:
- `relations_byte_equal=True` (closed set, pre-populated from schema — immune to drift) but entities/atoms differ → fingerprint of content-add, not order-shuffle.
- +305 chunks @ 10.56 avg = +29 files modified, matches local cadence of 21 new notes in last 1h.
- `w_l2_diff` magnitude matches the expected L2 of 915 extra Hebbian adds.
- All other code-path candidates ruled out via code audit (sort, seeded RNG, content-hashed encoder, timestamp redaction active).

### Q2. Fix prioritization (top-down)

**TIER 1 — snapshot-isolation (single root fix, addresses the root cause):**

> **a. Snapshot the source-file SET + bytes ONCE in `_run_arm_reingest_deterministic` and pass the same snapshot to both runs.**

Implementation sketch (5-10 LOC change):
- Replace the second `build_chunk_plan(...)` call with reuse of the first plan.
- Optionally: snapshot file bytes too (cache `path.read_bytes()` into an in-memory dict before run_a, monkey-patch `_read_file_text` for the duration of the arm to read from the cache). This eliminates the "USER edits a file mid-ingest" residual.

**TIER 2 — defensive-determinism hardening (already mostly in place):**

> **b. Sort guarantees** — already in place (`_glob_files`, `sorted(class_names)`).
> **c. Seed pinning** — already in place (torch.Generator + manual_seed).
> **d. Timestamp redaction** — already in place (`redact_timestamps_in_atoms=True` in REINGEST_DET).
> **e. Encoder content-addressing** — already in place (BLAKE2b per-trigram seed).

**TIER 3 — Merkle-tree manifest as POST-ingest verification (catches in-place mutations):**

> **f. Add a Merkle digest of (sorted entity list) + (sorted atoms list by triple_idx) to manifest.json.** Two ingests of the same input ⇒ same Merkle root. This is the "git tree hash" discipline applied to KB. Cheaper than full byte-equal compare; catches the same class of drift; gives us a single number to compare across ingests instead of 3 byte-equal predicates.

**TIER 4 (deferred — only if strict-determinism is fundamentally infeasible):**

> **g. Approximate-equal acceptance band** — accept reingest with `w_l2_diff / w_norm < 0.001` AND `chunk_set_jaccard > 0.99` AND `entity_set_jaccard > 0.99`. This is the "consistency-aggregated-over-replays" brain-analog contract.

### Q3. Enforce at chunk-ingest level OR validate POST-ingest?

**BOTH, with a sharp split of responsibility:**

- **Chunk-ingest level enforces:** snapshot-isolation (Q2-a) + all the existing defensive-determinism primitives (sort/seed/redact/content-addressed encoder).
- **POST-ingest (Merkle digest in manifest.json, Q2-f) validates:** that the ingest actually achieved byte-determinism given the snapshot. This is the auditable contract.
- **The dual-store audit (ANCHOR 5)** consumes the Merkle digest as its primary verify-the-referent check.

This split mirrors git: snapshot-isolation = `git add` (index materializes a snapshot); Merkle root = `git tree` (content-hash of the snapshot).

### Q4. Brain analog: strict byte-equal OR aggregated-over-replays?

**STRICT BYTE-EQUAL is achievable + correct** for our use-case, given snapshot isolation. The brain's stochastic-replay contract is the right metaphor for **query-time** behavior (multiple recall attempts may surface different memories), but it is NOT the right metaphor for **the ingest pipeline itself**, which should behave like a build system. Mature build systems (Nix, Bazel, Debian reproducible-builds) are existence proofs that strict byte-determinism is feasible at scale when snapshot-isolated.

That said, the brain analog **does** suggest a reasonable graceful-degradation mode: if the dual-store audit detects a non-byte-equal but jaccard-close ingest, surface as `WARN_INGEST_DRIFT` (not HARD_FAIL) — the substrate-KB is still usable; the strict-determinism contract is just temporarily violated by a known-acceptable cause (continuous-ingest-during-audit).

### Q5. Honest-bound path if strict-determinism is fundamentally infeasible?

It is **not fundamentally infeasible** (per cross-domain evidence: every reproducible-build system has solved this). So we should aim for strict byte-equal.

But honest-bound fallback for the dual-store audit: **content-key jaccard >= 0.99** + **w_l2_diff_normalized < 0.001** would still verify the dual-store match strongly enough to be load-bearing. This is the Tier-4 fallback above. Use ONLY if Tier-1 snapshot isolation proves intractable for some unforeseen reason (highly unlikely).

---

## 5. CONCRETE FIX CELL-SPEC (top-1 candidate)

**Anchor:** `substrate_director_kb_reingest_det_snapshot_isolated_v3`
**Tier hint:** TOOLING patch. Reuses chain-grade chunker primitive.
**Queue:** `remote_cpu_queue`
**Estimated cost:** ~15 min wall (one full chunk-ingest cycle, no second one needed; the snapshot is shared).

### Spec

Replace `_run_arm_reingest_deterministic` in `experiments/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.py` with `_run_arm_reingest_deterministic_snapshot_isolated`:

```python
def _run_arm_reingest_deterministic_snapshot_isolated(schema: dict, max_files: int | None) -> dict:
    arm_dir = _arm_workdir("reingest_det_v3")
    out_a = arm_dir / "kb_a"
    out_b = arm_dir / "kb_b"

    # SNAPSHOT once, reuse twice
    plan = build_chunk_plan(
        schema=schema, repo_root=REPO,
        chunk_classes=DEFAULT_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )

    # Snapshot file bytes too (defends against in-place file mutation)
    file_bytes_snapshot: dict[Path, bytes] = {}
    for cname, cinfo in plan.items():
        for p in cinfo["files"]:
            try:
                file_bytes_snapshot[p] = p.read_bytes()
            except OSError:
                pass

    # Monkey-patch _read_file_text to read from snapshot for duration of arm
    import hdlab.director_kb as _dkb
    original_read = _dkb._read_file_text
    def _read_from_snapshot(path, max_bytes):
        if path in file_bytes_snapshot:
            raw = file_bytes_snapshot[path]
            if len(raw) > max_bytes:
                return None, "body_exceeds_max_bytes"
            if len(raw) == 0:
                return None, "empty_file"
            try:
                return raw.decode("utf-8", errors="replace"), None
            except Exception as e:
                return None, f"decode_error:{type(e).__name__}"
        return original_read(path, max_bytes)
    _dkb._read_file_text = _read_from_snapshot

    try:
        t0 = time.perf_counter()
        man_a = run_chunk_ingest(plan=plan, out_dir=out_a, schema=schema,
                                 n_dim=N_DIM, seed=SEED, wipe=True,
                                 redact_timestamps_in_atoms=True)
        t_a = time.perf_counter() - t0

        t1 = time.perf_counter()
        man_b = run_chunk_ingest(plan=plan, out_dir=out_b, schema=schema,
                                 n_dim=N_DIM, seed=SEED, wipe=True,
                                 redact_timestamps_in_atoms=True)
        t_b = time.perf_counter() - t1
    finally:
        _dkb._read_file_text = original_read

    # Standard byte-equal checks
    entities_eq = files_byte_equal(out_a / "entities.jsonl", out_b / "entities.jsonl")
    relations_eq = files_byte_equal(out_a / "relations.jsonl", out_b / "relations.jsonl")
    atoms_eq = files_byte_equal(out_a / "atoms.jsonl", out_b / "atoms.jsonl")
    w_diff = W_l2_diff(out_a / "W.pt", out_b / "W.pt")

    # NEW: Merkle digest sanity (Q2-f)
    import hashlib
    def _merkle_of_jsonl(p):
        h = hashlib.blake2b(digest_size=32)
        for line in p.read_bytes().splitlines():
            h.update(hashlib.blake2b(line, digest_size=32).digest())
        return h.hexdigest()
    merkle_a = _merkle_of_jsonl(out_a / "atoms.jsonl")
    merkle_b = _merkle_of_jsonl(out_b / "atoms.jsonl")

    w_ok = w_diff < HP_MAX_W_L2
    merkle_ok = merkle_a == merkle_b
    ok = entities_eq and relations_eq and atoms_eq and w_ok and merkle_ok

    return {
        "arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3",
        "ok": bool(ok),
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "t_run_a_s": round(t_a, 3),
        "t_run_b_s": round(t_b, 3),
        "entities_byte_equal": bool(entities_eq),
        "relations_byte_equal": bool(relations_eq),
        "atoms_byte_equal": bool(atoms_eq),
        "w_l2_diff": w_diff,
        "w_within_tolerance": bool(w_ok),
        "w_tolerance": HP_MAX_W_L2,
        "merkle_atoms_a": merkle_a,
        "merkle_atoms_b": merkle_b,
        "merkle_ok": bool(merkle_ok),
        "n_chunks_a": man_a["n_chunks"],
        "n_chunks_b": man_b["n_chunks"],
        "n_files_snapshotted": len(file_bytes_snapshot),
    }
```

### Discriminator + HARD_FAIL band

- **HARD_PASS:** all byte-equal predicates True AND `w_l2_diff < 1e-6` AND `merkle_ok=True` AND `n_chunks_a == n_chunks_b` AND `n_files_snapshotted > 0`.
- **HARD_FAIL:** any byte-equal predicate False OR `w_l2_diff >= 1e-6` OR `merkle_ok=False`.
- **CARDINALITY_OK:** `n_chunks_a > 0 AND n_chunks_b > 0 AND n_files_snapshotted > 0` (gate against silently snapshotting an empty set).
- **Discriminator-survives-scale (USER 2026-06-26):** the snapshot logic does not change with N; smoke at notes-only (~10k files) and full (~13k files) should both pass byte-equal IFF snapshot is correctly applied. Add 2-arm smoke with `max_files=200` to verify the mechanism FIRES (Tier-1 strict-determinism), then full to verify it scales.

### Pre-reg discipline gates

- Fix #21 (poll for landing): yes — write to `data/recent_landings.jsonl` on finish.
- Fix #26 (verify-the-referent): pre-dispatch check that `_run_arm_reingest_deterministic_snapshot_isolated` is the function actually invoked (not the old one).
- Fix #28 (per-arm metrics): both arms' `entities_byte_equal/atoms_byte_equal/w_l2_diff/merkle_ok` surface to metrics.json individually.
- META_RULE_H: cardinality_ok mandatory.
- META_RULE_L: synthetic discriminator arm preserved.

### Tripwire (Skunkworks self-audit, REPRODUCIBILITY class)

If snapshot-isolated cell PASSES, Skunkworks must confirm by inspecting `entities.jsonl` from out_a + out_b are byte-identical (Skunkworks should NOT trust the cell's own `entities_byte_equal` field — verify-the-referent on disk).

---

## 6. DECISION TREE — strict vs probabilistic vs approximate-equal

```
                       ARM_CHUNK_REINGEST_DET HARD_FAIL'd
                                    |
                                    v
                ┌──────────────────────────────────────────┐
                │ Is the breach explainable by file-set    │
                │ drift between run_a and run_b? (i.e.     │
                │ relations_eq=True, n_chunks_b > n_chunks_a, │
                │ delta consistent with note cadence)       │
                └──────────────────────────────────────────┘
                            │              │
                          YES (now)       NO
                            │              │
                            v              v
            ┌───────────────────────┐  ┌────────────────────────┐
            │ TIER 1: snapshot-     │  │ Deeper investigation:  │
            │ isolation (Q2-a)      │  │ - audit `_intern` for  │
            │ Implement v3 cell;    │  │   hash-set iteration   │
            │ re-test.              │  │ - audit chunker for    │
            │                       │  │   regex backtracking   │
            │ Expected: HARD_PASS   │  │ - audit torch CPU      │
            │ P=0.85                │  │   matmul determinism   │
            └───────────────────────┘  └────────────────────────┘
                       │
                       v
            ┌───────────────────────┐
            │ Did snapshot-isolated │
            │ run HARD_PASS?        │
            └───────────────────────┘
                  │            │
                YES (P=0.85)   NO (P=0.15 residual)
                  │            │
                  v            v
      ┌───────────────────┐  ┌──────────────────────────────────┐
      │ DONE. Promote v3  │  │ TIER 3: add Merkle digest        │
      │ as canonical det  │  │ (Q2-f) — if Merkle matches but   │
      │ test. Update      │  │ byte-equal fails, problem is in  │
      │ MEMORY.md.        │  │ persistence layer (json.dumps    │
      │                   │  │ key-ordering, torch.save, etc).  │
      │ Substrate-vs-MD   │  │ Audit each persistence call.     │
      │ flip GATE = OPEN. │  └──────────────────────────────────┘
      └───────────────────┘                  │
                                             v
                                ┌──────────────────────────────┐
                                │ Did Merkle match (= ingest   │
                                │ is content-deterministic)?   │
                                └──────────────────────────────┘
                                       │             │
                                     YES             NO
                                       │             │
                                       v             v
                       ┌──────────────────┐   ┌────────────────────┐
                       │ TIER 4-light:    │   │ TIER 4-full:       │
                       │ accept Merkle as │   │ approximate-equal  │
                       │ the determinism  │   │ band (w_l2_norm    │
                       │ contract; relax  │   │ < 0.001 AND        │
                       │ byte-equal to    │   │ jaccard > 0.99).   │
                       │ "Merkle equal".  │   │                    │
                       │                  │   │ Substrate-vs-MD    │
                       │ Substrate-vs-MD  │   │ flip = conditional │
                       │ flip GATE = OPEN │   │ (degrades to       │
                       │ with content-    │   │ brain-analog       │
                       │ determinism      │   │ consistency        │
                       │ contract.        │   │ contract).         │
                       └──────────────────┘   └────────────────────┘
```

---

## 7. RECOMMENDED IMMEDIATE NEXT ACTION

Spawn `hdi_exp_dev` with cell-spec from §5 above. ETA ~15 min on `remote_cpu_queue`. Expected verdict: HARD_PASS at P=0.85; substrate-vs-MD flip GATE flips to OPEN on successful land.

**Parallel work for Director main-thread during the ~15 min:**
1. File this drill doc atom (HONEST_NEG → constructive-rescue trail).
2. Update `data/director_plan.json` with Wave 4 v3 status.
3. Update `notes/active_protocols.md` (if exists) with snapshot-isolation discipline.
4. Pre-write the post-land atomization (META_RULE candidate: "REINGEST_DET arms must snapshot-isolate source-file set + bytes").

---

## 8. NEW META_RULE CANDIDATE (post-land)

**META_RULE_N (provisional): "Determinism arms must snapshot-isolate the source-state set before timing the determinism check."**

Rationale: every reproducible-build system has independently arrived at this discipline (Nix copy-to-store, Bazel sandbox, git index materialization). Mature received wisdom. Our REINGEST_DET arm was naively timing two builds across an unsnapshot source — same class of error as `make` being invoked twice on a live source tree and complaining the outputs differ.

Atomize as Store atom on snapshot-isolated v3 HARD_PASS.

---

## Files referenced

- `d:/AI/hd-instrument/data/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced/metrics.json` (source evidence)
- `d:/AI/hd-instrument/hdlab/director_kb_chunk_ingest.py` (chunker + ingest pipeline)
- `d:/AI/hd-instrument/hdlab/director_kb.py` (file-walk helpers, `_glob_files`, `_resolve_source_root`, `_read_file_text`)
- `d:/AI/hd-instrument/hdlab/char_trigram_encoder.py` (encoder — verified deterministic)
- `d:/AI/hd-instrument/hdlab/kg_traversal.py` (KGStore — verified deterministic)
- `d:/AI/hd-instrument/experiments/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.py` (cell + REINGEST_DET arm code)
- `d:/AI/hd-instrument/preregs/2026-06-27_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.md` (current prereg)

## Lit-scan sources (generic-terms only per query-privacy)

- reproducible-builds.org: timestamps, SOURCE_DATE_EPOCH, file-iteration ordering
- Ecker et al. 2022 eLife / PMC8865846: hippocampal sharp-wave-ripple replay variability
- git-scm.com hash-function-transition + Git Book object model: sorted-tree-entries / content-addressed
- pangea.cloud / source.network / oxen.ai: Merkle-tree content-addressable storage primer
