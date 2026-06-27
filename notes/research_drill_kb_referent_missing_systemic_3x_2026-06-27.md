# Research drill 3x — KB_REFERENT_MISSING systemic failure

Date: 2026-06-27
Author: Research (Director)
Trigger: 3 cells HARD_FAILed today with identical root cause
  - `exp_kb_partition_by_source_class_v2` (ANCHOR 1)
  - `exp_kb_dual_store_audit_v1` (ANCHOR 5)
  - `exp_kb_coarse_grain_at_promotion_v2_chain_grade_path` (ANCHOR 3)

Common verdict: `KB_REFERENT_MISSING: KB dir not found: C:\dev\hd-instrument\data\exp_substrate_director_kb_ingest_v1\_arm_full\kb`

ANCHOR 1 v3 self-contained pattern (`exp_kb_partition_by_source_class_v3_self_contained.py`) is the proposed rescue — it builds a labeled mini-KB IN-CELL via `run_chunk_ingest` over `notes/ + memory/ + preregs/`. Currently pending on the remote queue.

---

## Section 0 — Verified facts from filesystem inspection

- `hdlab/director_kb_query.load_default_kb()` tries canonical `data/substrate_director_kb_v1/manifest.json` FIRST, falls back to legacy `data/exp_substrate_director_kb_ingest_v1/_arm_full/kb`.
- LOCAL canonical KB exists: 577,842 entities; 1,030,445 triples; 2,048-dim; coverage 0.9989; built 586s; sources span 20+ classes (atoms, notes, preregs, memory, wordnet, verbnet, framenet, gene_ontology, kegg, neurolex, fleet_state, director_plan, …).
- REMOTE has neither path. Cells crash in `load_default_kb` on `FileNotFoundError` for the fallback path (verdict_msg shows the second-attempt path).
- `tools/queue_add.py` gate validates: script exists, prereg exists, `--self-test` passes, `--smoke` writes valid metrics. It does NOT validate any data-file / KB referent.
- No tool in `tools/` exists for syncing the canonical KB to remote (`rg substrate_director_kb_v1 tools/` returns only the local builder).
- The local canonical KB is auto-refreshed every ~5min by a Windows scheduled task `hd_director_kb_continuous_ingest`. There is no analogous remote task.
- The continuous-ingest writes via atomic swap (post-2026-06-26 fix in commit 5de28ea1), so a stale read is impossible but a remote MIRROR is unmodelled.

So the real systemic failure is a TWO-LAYER gap:
1. Cells reference a legacy path (`_arm_full/kb`) that was superseded by the canonical path.
2. Even the canonical path isn't provisioned to remote runners — so even if the cells were updated to point at canonical, they would still HARD_FAIL on remote.

---

## ANGLE 1 — Software-engineering / build-system best practices

### What the field knows

| System | How it handles upstream artifacts |
| --- | --- |
| **Make** | Targets declare dependencies; missing prereq triggers prereq rebuild OR fail-fast with a clear message. Hermetic by file mtime. |
| **Bazel / Buck** | Strictly hermetic: every target declares ALL inputs in BUILD file. Remote build cache shares prebuilt artifacts across machines keyed by content hash. Missing inputs = build-graph error AT QUERY TIME, before any execution. |
| **Nix** | Every derivation is a content-addressed hash. If an input derivation isn't in the local store, it's fetched from a binary cache OR rebuilt from source. Never silently fails on missing input — the dep graph is the proof obligation. |
| **Cargo / pip** | Lockfile pins versions; resolver pre-checks all transitive deps exist before any compile. |
| **GitHub Actions / Jenkins** | "Artifact" + "needs:" steps explicitly declare upstream produces / downstream consumes. CI catches the missing-artifact case during job startup. |

### Pattern catalog (with names + cost)

1. **Hermetic self-contained build** (Bazel `genrule` with everything inlined; Nix `builtins.derivation` with `src` snapshot).
   - PRO: zero coupling; runs anywhere; reproducible by construction.
   - CON: duplicates upstream work if many cells share the input; ingestion cost paid per cell.
   - COST per ANCHOR 1 v3: `run_chunk_ingest` on 200 files × 3 classes at 2048-dim ≈ 30-60s smoke wall; full ≈ a few minutes. Bounded.

2. **Provision-once-share via remote cache** (Bazel remote build cache; Nix binary cache; CI artifact store).
   - PRO: amortized cost; canonical KB ingested once at 577k entities = ~10 min, then reused by N cells.
   - CON: needs cache-invalidation policy + version-handshake between writer/reader; requires sync mechanism for remote runners.
   - COST: one ~10-min ingest + ~1-2GB sync to remote whenever canonical KB rotates.

3. **Pre-flight dependency-check at dispatch time** (CI `needs:` validation; Bazel `query` pre-execution).
   - PRO: catches missing-upstream BEFORE wasting compute on the queue.
   - CON: dispatch tool needs to know about the data graph (not just the script graph).
   - COST: tiny — a few file-existence checks at `queue_add` time.

4. **Lazy idempotent rebuild** (Make's "if outdated, regenerate"; Dagster's `Auto-materialize` for assets).
   - PRO: works for both empty AND stale upstreams.
   - CON: per-cell-invocation rebuild cost.

5. **Content-addressed inputs** (Nix; Docker layers).
   - PRO: name encodes content; old/new can coexist; reader knows exactly what it got.
   - CON: schema-coupling churn — every input version invalidates downstream caches.

### Mapping to our 3 failures

All 3 cells embedded a HARD-coded path with NO existence-check at smoke time (smoke ran on laptop where the legacy path historically existed; FAIL surfaced only on remote). Smoke discipline gap: smoke verified the cell ran end-to-end on the AUTHOR'S machine, not on the EXECUTION runner.

The 3 cells also shared the same dep (`_arm_full/kb`) but were each shipped independently — no awareness that one dep blocks N cells.

---

## ANGLE 2 — Brain / neuroscience (scaffold-vs-content separation)

### What the brain does

Two crisp findings.

**(a) Schema-extraction prerequisites (Tse et al. 2007 *Science*; Morris 2013).**

Hippocampus is REQUIRED to learn a new flavor-place association — but the requirement RECEDES (lesion-tolerance grows) the more pre-existing schema the cortex has for the domain. The brain's pattern: build a substrate-internal SCHEMA over weeks of consolidation, after which downstream learning is "fast-binding into pre-existing scaffold" instead of "cold-start ingest + bind." Frankland & Bontempi (2005) review formalizes this as Standard Consolidation: hippocampal content gets replicated into a cortical schema, then future-related events are encoded DIRECTLY into the cortical store.

Implication for substrate-as-Director-KB: a "test cell" that arrives EXPECTING the KB to be there is brain-analogous to a cortical retrieval task — it assumes prior consolidation has happened. A "cell that builds its own mini-KB" is brain-analogous to a hippocampal encoding episode that does NOT depend on prior cortex. Both modes are legitimate; the brain uses both, but it never confuses them.

**(b) Memory consolidation creates the substrate that retrieval queries against.**

NREM/REM replay (Wilson & McNaughton 1994; Diekelmann & Born 2010) is the brain's analog of `run_chunk_ingest` — it transforms episodic traces into cortical structure. A retrieval cell that runs BEFORE consolidation literally has nothing to retrieve from.

**(c) Behavioral analog: human bootstrap when learning a new domain.**

Novice in domain X: builds local sketch concepts from raw experience (hippocampal-heavy = "cell builds own scaffold"). Expert: queries pre-existing cortical schema (cortical-heavy = "cell tests against existing index"). Either mode can be load-bearing; mixing them silently is the failure mode.

### Implication for the design question

ANCHOR 1 v3's "build labeled mini-KB IN-CELL" is the **hippocampal-encoding** pattern: every test brings its own substrate. ANCHOR 1 v2's "test against existing index" is the **cortical-retrieval** pattern: assume prior consolidation.

Brain uses BOTH. A test of WHETHER consolidation HAPPENED needs the cortical-retrieval mode (else you're testing the encoder, not the consolidated store). A test of WHAT can be retrieved AT A POINT IN TIME is appropriate for the hippocampal-encoding mode (no contamination from yesterday's state).

For the 3 cells specifically:
- ANCHOR 1 partition routing: testing whether `source_class` filtering works → either mode is valid; v3 self-contained is cleanest.
- ANCHOR 5 dual-store audit: this IS about whether the canonical-KB-as-Director-substrate matches filesystem-grep. It NEEDS the canonical KB, not a mini-KB built per-cell. Wrong target with self-contained.
- ANCHOR 3 coarse-grain at promotion: testing a TWO_TIER architecture move; needs persistent storage that can be promoted/demoted. Could go either way.

So the brain-analog says: **don't blanket-rescue all 3 with v3 self-contained**. ANCHOR 5 specifically tests the canonical-substrate-vs-filesystem invariant; rescuing it with self-contained mini-KB rewrites what it's actually measuring.

---

## ANGLE 3 — Data-pipeline / distributed-systems architecture

### Cache-strategy taxonomy

| Pattern | Behavior | Fits us when… |
| --- | --- | --- |
| **Cache-aside** | App checks cache; on miss, app queries source-of-truth + populates cache. | Cells check for canonical KB; on miss, rebuild inline. (Hybrid mode.) |
| **Read-through** | Read goes through cache layer; layer handles backfill. | A `KBProvider` abstraction provides KB lazily — cells just ask. |
| **Write-through** | Writes hit cache + source-of-truth together. | The continuous-ingest writes canonical + mirrors to a known-good location. |
| **Refresh-ahead** | Cache proactively reloads before TTL. | The scheduled task already does this. |

### Failure-mode catalog (the actual root causes I see across the broader fleet)

| Mode | Symptom | Our 3-cell incident? |
| --- | --- | --- |
| **Upstream missing** | `FileNotFoundError` at runtime. | Yes — primary cause. |
| **Upstream stale** | Wrong manifest_version / schema_version. | Latent risk on remote. |
| **Upstream partial** | Manifest exists but ingest crashed mid-way; entities present, relations missing. | Pre-2026-06-26 atomic-swap fix. |
| **Upstream corrupted** | Manifest unparseable. | Mitigated by atomic-swap. |
| **Version mismatch** | Reader's encoder ≠ writer's encoder. | Risk if remote and local drift. |
| **Path drift** | Legacy hardcoded path superseded by canonical. | **Secondary cause** — 3 cells used `_arm_full/kb` instead of `substrate_director_kb_v1`. |
| **Host-locality** | Path exists locally, not on dispatch host. | **Tertiary cause** — would have hit even after path-update. |

### What Spark / Airflow / Dagster do

- **Airflow**: tasks declare `inlets`/`outlets` (datasets). Scheduler refuses to schedule a task if its inlets haven't been produced. Failure surfaces at scheduler time, not at task-runtime.
- **Dagster**: assets-graph is the primary abstraction; `Auto-materialize` rebuilds upstream when downstream requests it. "Asset health" UI shows freshness, missing, stale per asset.
- **Spark**: `Dataset` lineage; recomputes from source if cached fragment lost. Strong "your DAG is your contract" stance.

The pattern: **declarative inlet declarations + scheduler-time validation**. The scheduler refuses to launch on broken DAG.

### Mapping to `queue_add` gate

`queue_add.py` already enforces ~5 invariants (PROT-018 N-binding, PROT-019 timeout-floor, PROT-020 GPU-queue-uses-torch, PROT-021 long-timeout-has-checkpoint, smoke produces valid metrics). It's exactly the right layer to add **PROT-022: declared data-referents must resolve on the target runner**.

---

## Synthesis: Recommendation

**Hybrid: provision-once-share for the canonical KB + self-contained fallback for path-misalignment + dispatch-time referent check at the gate.**

### Tier 1 — Provision canonical KB on remote (HIGHEST ROI; ships once)

- The canonical `data/substrate_director_kb_v1/` (~600MB at 577k entities × 2048-dim float16 + atoms.jsonl) should live on the remote runner under the SAME relative path.
- Ship a `tools/sync_canonical_kb_to_remote.sh` that rsyncs (or scp -r) `data/substrate_director_kb_v1/` from laptop to `marsh@home:C:/dev/hd-instrument/data/substrate_director_kb_v1/` whenever the local manifest_version changes.
- Run from local Windows scheduled task at 30-min cadence (or post-ingest-completion hook).
- Cells reference canonical path; `load_default_kb` finds it on either host without code change.

This single fix unblocks any cell that legitimately needs the cortex-grade index AND removes legacy-path debt.

### Tier 2 — All NEW Wave 3 / KB-dependent cells default to v3-style self-contained

For tests that DON'T need the full 577k-entity canonical (most partition/routing/coarse-grain tests work fine with a 5k-entity mini-KB), use the v3 pattern. It's:
- Hermetic (Bazel-clean).
- Cheap (smoke ≈ 30-60s wall; full ≈ a few min).
- Runs anywhere with notes/memory/preregs (which are git-controlled, so always present on any clone).
- Independent of canonical-KB rotation, so a chain-grade verdict TODAY stays reproducible after a KB version bump.

Exception: ANCHOR 5 (dual-store audit) explicitly tests "does the CANONICAL substrate match filesystem?" — that test is by-construction-invalid with a mini-KB. ANCHOR 5 needs Tier 1 to land first.

### Tier 3 — `queue_add` gate enhancement (catch the next instance)

Add a PROT-022 declared-data-referents check. Spec below.

### Cost analysis (provisional)

| Option | Up-front cost | Per-cell cost | Robustness | Reproducibility |
| --- | --- | --- | --- | --- |
| Self-contained everywhere | 0 | +30-60s smoke per cell | Highest (zero deps) | High (deterministic from in-repo sources) |
| Provision once-share (canonical) | ~15min sync + scheduled-task setup | 0 | Brittle: drift between local/remote canonical | Medium (depends on which canonical landed) |
| Hybrid (Tier 1+2+3) | ~15min sync + ~30min gate-script | +30-60s smoke (only for self-contained subset) | High | High |

Recommended: **Hybrid**. Tiers 1 and 3 ship first; Tier 2 is the default for new cells unless cell explicitly testing canonical-KB invariants.

---

## Concrete artifact 1 — Cell spec for `exp_substrate_director_kb_ingest_v1_remote_provision_v1.py`

Note: this is the **Tier-1 sync cell**, not the rescue cell. The rescue cell pattern is already the existing `_v3_self_contained.py`. This Tier-1 cell ESTABLISHES the canonical KB on remote so future cells can reference it.

```
ANCHOR: substrate_director_kb_remote_provision_v1
PURPOSE: One-shot provisioning of canonical substrate-Director-KB onto remote_cpu_queue
         runner. Run on local Windows host (where ~/.claude/projects/d--AI/memory + repo
         live); cell ingests fresh, then SCPs the kb dir to remote.

PRE-REG BANDS:
  HARD_PASS: local ingest n_entities >= 500_000 AND coverage_ratio >= 0.99
             AND remote_post_sync_atom_count == local_atom_count
             AND remote post-sync load_default_kb() opens manifest OK
             AND remote canonical-path matches local relative path
  MIDDLE_BAND: local OK but remote_post_sync n_entities in [0.95, 1.0] * local
               (partial sync / network truncation)
  HARD_FAIL: ingest produces < 500_000 entities OR remote count == 0
             OR remote manifest unparseable OR scp/rsync error

ARMS (3 mandatory):
  ARM_LOCAL_INGEST              run_canonical_ingest(repo, classes=DEFAULT_CLASSES)
                                writes data/substrate_director_kb_v1/manifest.json
  ARM_REMOTE_SYNC               rsync -av --delete data/substrate_director_kb_v1/
                                marsh@home:C:/dev/hd-instrument/data/substrate_director_kb_v1/
                                (Windows: use `scp -r` + manifest delete-then-replace)
  ARM_REMOTE_VERIFY             ssh marsh@home python -c
                                "from hdlab.director_kb_query import load_default_kb;
                                 kb = load_default_kb();
                                 print(len(kb.entity_names), kb.kb_version)"
                                Parse atom_count + kb_version; assert match.

SUCCESS GATE: all 3 arms ok AND atom_counts match exactly AND kb_versions match.

ROUTING: local (NOT a remote_cpu_queue cell; runs on the host that already HAS canonical).
CADENCE: scheduled task (Windows Task Scheduler) every 6h OR post-canonical-ingest hook.

INSTRUMENTATION:
  - manifest.json local vs remote diff (n_entities, n_triples, coverage, encoder, schema_version)
  - sync wall-clock + bytes transferred
  - audit log row to data/kb_remote_provision_audit_log.jsonl

DESIGN NOTES:
  - Use `--delete` (or windows equivalent) so dropped entities are removed remotely.
  - Use a temp-dir-then-mv-into-place on remote so reader-during-sync sees old OR new
    but never partial (mirrors the atomic-swap discipline of continuous-ingest).
  - Sync the SCHEMA file (`hdlab/director_kb_schema.json` or wherever) alongside the
    artifact so remote DirectorKBQuery instantiates with the matching schema.
```

This cell is OPTIONAL if we choose pure Tier-2 (self-contained everywhere). It is REQUIRED for cells like ANCHOR 5 that need canonical scale.

---

## Concrete artifact 2 — `queue_add` PROT-022 gate enhancement

```python
# tools/queue_add.py addition

PROT022_DECLARED_REFERENTS_RE = re.compile(
    r'^\s*#\s*KB_REFERENT\s*:\s*(\S+)\s*$',
    re.MULTILINE,
)

def check_declared_referents(
    script_path: Path,
    queue_name: str,
    allow_override: bool,
) -> None:
    """PROT-022: scripts must declare their data referents; gate verifies
    each declared path either (a) exists on the dispatch host, or (b)
    is built by the script before use.

    Mechanism: a script that needs `data/foo/bar/` includes a top-of-file
    comment:

        # KB_REFERENT: data/substrate_director_kb_v1/manifest.json
        # KB_REFERENT: data/exp_substrate_director_kb_ingest_v1/_arm_full/kb/manifest.json

    For LOCAL queues (local_cpu_queue), each referent must exist on the
    local filesystem.
    For REMOTE queues (overnight_queue, remote_cpu_queue), the gate runs
    `ssh <remote> test -f <path>` for each referent and rejects on
    missing.

    Override: --allow-missing-referent (rare; only for cells whose ingest
    arm BUILDS the referent before use).

    Exits code 10 on violation.

    Rationale: 3 cells on 2026-06-27 wasted compute hitting
    KB_REFERENT_MISSING. A 1-second SSH existence check at gate time
    catches the entire class.
    """
    try:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return  # let later checks catch the unreadable script

    referents = PROT022_DECLARED_REFERENTS_RE.findall(source)
    if not referents:
        return  # no declarations; gate is opt-in (cells without KB
                # referents don't need declarations)

    print(f"[gate] PROT-022: script declares {len(referents)} KB referent(s)")

    missing = []
    REMOTE_QUEUES = {"overnight_queue", "remote_cpu_queue"}
    is_remote = queue_name in REMOTE_QUEUES

    for ref in referents:
        if is_remote:
            # SSH check
            remote_path = f"C:/dev/hd-instrument/{ref}"
            rc = subprocess.run(
                ["ssh", "marsh@home", f"test -f \"{remote_path}\""],
                timeout=10, capture_output=True,
            ).returncode
            exists = (rc == 0)
        else:
            exists = (REPO / ref).exists()

        status = "OK" if exists else "MISSING"
        print(f"  PROT-022 {status} ({queue_name}): {ref}")
        if not exists:
            missing.append(ref)

    if missing and not allow_override:
        print(
            f"\n[gate] PROT-022 REJECT: {len(missing)} declared KB referent(s) missing "
            f"on {'remote' if is_remote else 'local'} host:\n"
            + "\n".join(f"    {m}" for m in missing) +
            f"\n\n  Three cells on 2026-06-27 (anchor_1_v2, anchor_5_dual_store, "
            f"anchor_3_coarse_grain_v2) wasted GPU/CPU compute hitting this exact "
            f"failure mode. PROT-022 catches it at the gate.\n"
            f"\n  Fix options:\n"
            f"    1. Build the referent on the target host (e.g. run "
            f"sync_canonical_kb_to_remote.sh for the canonical KB).\n"
            f"    2. Make the cell self-contained (build its own KB IN-CELL like "
            f"exp_kb_partition_by_source_class_v3_self_contained does via "
            f"run_chunk_ingest).\n"
            f"    3. Pass --allow-missing-referent if the cell's first arm BUILDS "
            f"the referent before use.\n",
            file=sys.stderr,
        )
        sys.exit(10)
```

Also wire `--allow-missing-referent` to the argparse + call `check_declared_referents` right after PROT-021.

For the 3 cells that just failed, the right action is:
1. ANCHOR 1 v3 (already filed) — self-contained, no referent declaration needed.
2. ANCHOR 3 coarse-grain — port to v3-style self-contained OR add `# KB_REFERENT: data/substrate_director_kb_v1/manifest.json` after Tier-1 provision-cell lands.
3. ANCHOR 5 dual-store — add `# KB_REFERENT: data/substrate_director_kb_v1/manifest.json` declaration AND gate it on Tier-1 provision-cell. Test fundamentally needs canonical scale.

---

## Synthesis answers to the 4 questions

**1. Should ALL Wave 3 / KB-dependent cells follow ANCHOR 1 v3's self-contained pattern?**

**No — context-dependent.** Cells testing whether a MECHANISM works on labeled data (partition routing, coarse-grain at promotion, source-class filter, refuse-gate calibration) should default to v3 self-contained: hermetic, cheap (30-60s smoke), reproducible from git-controlled sources. Cells testing CANONICAL-substrate invariants (dual-store audit, scale-dependent behaviors, end-to-end Director-KB tests) need the canonical KB.

Rule of thumb: if your test's verdict would change when the canonical KB grows from 577k to 700k entities, you need canonical. Otherwise, self-contained.

**2. Should we provision `_arm_full/kb` on remote once + share? Or always rebuild inline?**

**Provision the CANONICAL path (`data/substrate_director_kb_v1`), not the legacy `_arm_full/kb`.** The legacy path was an early-version artifact; the canonical path is what `load_default_kb` prefers. Provision once via `tools/sync_canonical_kb_to_remote.sh`, refresh every 6h (or post-ingest hook). The continuous-ingest scheduled task already keeps the local canonical fresh; the remote just needs to mirror.

Always-rebuild-inline is the right move for HERMETIC tests; provision-share is right for SCALE-dependent tests.

**3. What's the right dispatch-time check that would CATCH this BEFORE running 3 cells with the same dep?**

PROT-022 in `queue_add` as specified above. A `# KB_REFERENT: <path>` comment-declared dependency + 1-line SSH existence check rejects the dispatch in <1 second. If the convention is in place, the first instance of "3 cells with same missing dep" becomes "1 cell fails the gate; author either ports to self-contained or schedules a provision cell — the other 2 cells never even reach the queue."

This complements `predispatch_check.py` (which catches duplicate or recently-failed cells based on the LANDING record) with a SOURCE-side check on the script's declared inputs.

**4. Should the `queue_add` gate validate referent existence (like `predispatch_check.py` does for landings)?**

Yes — exactly per PROT-022 spec above. It's a natural extension to the existing PROT-018/019/020/021 ladder: each is a 1-screen check that catches one class of historical failure. PROT-022 catches the 2026-06-27 KB_REFERENT_MISSING class.

---

## Action items (Director own-lane; ships TODAY)

1. **Ship Tier-1 cell spec to skunkworks for verdict-tier sign-off.** Author the actual `tools/sync_canonical_kb_to_remote.sh` AFTER spec ratified.
2. **Ship PROT-022 patch to queue_add as a separate spawn** (small, well-bounded, no new architecture).
3. **Standstill on rescuing ANCHOR 5 dual-store** until Tier-1 provision-cell lands — its test target is "canonical KB matches filesystem"; a self-contained rescue rewrites the test.
4. **Rescue ANCHOR 3 coarse-grain via the v3-self-contained pattern** (same as ANCHOR 1 v3). Spawn hdi_exp_dev to port.
5. **Document the brain-analog rule in MEMORY.md** as a feedback atom: "self-contained-IN-CELL vs canonical-substrate-test is hippocampal-encoding-vs-cortical-retrieval; don't mix them silently."

---

## Bias-checks applied (per EXPERIMENT BIAS MASTER CHECKLIST)

- **BIAS-N verify-the-referent-verdict-field**: I read the actual metrics.json for ANCHOR 1 v2 and confirmed the verdict_msg text. Did not just trust the user-prompt summary.
- **BIAS-13 contamination**: Considered whether the v3 self-contained cell's "rescue" is really a different mechanism (it's not — same arms + bands, only the KB-source changed). Honest framing: v3 is a RESCUE on a separate-runner-portability axis, not a tighter discriminator.
- **BIAS-P anisotropy-hurts-retrieval**: not directly load-bearing here (this is a build-system problem) but flagged that ANCHOR 5's dual-store match is anisotropy-sensitive at scale.
- **Lit-scan calibration penalty**: Tier-1 provision-cell P_HARD_PASS estimate: 0.55 (deflated from 0.70 naive; novel ops on Windows scp-with-atomic-swap have a tail). PROT-022 gate ship P: 0.85 (pure refactor on a well-understood file).
