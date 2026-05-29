# Substrate Memory Testbed Architecture (2026-05-29)

3-hour-deadline build of a sandbox where the hd-instrument substrate IS the memory layer.
Real deployment on `marsh@home` (Windows PowerShell host at `C:\dev\hd-instrument\`).
Substrate is wrapped, not re-built. Benchmarked head-to-head against FAISS, Chroma, sqlite-vec.

Author role: architect. Output is spec + plan only; production code is dispatched in Phase 2
across 3 parallel workstreams.

## Executive summary

The testbed exposes a uniform memory API (`store`, `retrieve`, `edit`, `delete`, `audit`) with
5 concrete backends: substrate (BSC/Hadamard, wrapping `hdlab/` + `experiments/` primitives),
FAISS CPU, Chroma, sqlite-vec, and an in-memory dict (sanity baseline). A benchmark harness
runs 6 scenarios over each backend and writes structured results to dated dirs. Substrate's
killer features (KF-1 hallucination detection, KF-2 edit isolation, TCFT deletion certificate)
get their own section in the report because baselines literally cannot produce those metrics.
The contrast IS the product story.

Everything lives under `testbed/` at repo root, isolated from `experiments/`. State persists
under `C:\dev\hd-instrument\testbed_data\` carved into substrate / baselines / datasets /
results subdirs. Total disk footprint <500 MB for default 10k-item configs.

## Architecture diagram (ASCII)

```
   +-------------------------------------------------------------+
   |                          CLI                                |
   |   python -m testbed run --scenario X --backend Y --config Z |
   +------------------------------+------------------------------+
                                  |
                                  v
   +-------------------------------------------------------------+
   |                    testbed/harness.py                       |
   |  - load config.yaml                                         |
   |  - dispatch scenario over backend(s)                        |
   |  - collect metrics, write results JSON                      |
   +------------------+------------------------+-----------------+
                      |                        |
                      v                        v
   +------------------------------+   +------------------------+
   |  testbed/scenarios/*.py      |   |   testbed/report.py    |
   |  - point_recall              |   |   - aggregate runs     |
   |  - edit_isolation (KF-2)     |   |   - markdown table     |
   |  - deletion_verify (TCFT)    |   |   - killer-feature     |
   |  - hallu_detect (KF-1)       |   |     panel              |
   |  - continual_4stage          |   +------------------------+
   |  - storage_latency           |
   +---------------+--------------+
                   |
                   v
   +-------------------------------------------------------------+
   |                  MemoryBackend ABC                          |
   |  store(key_id, vec, value) -> None                          |
   |  retrieve(query_vec, k=1) -> RetrievalResult                |
   |  edit(key_id, new_value) -> None                            |
   |  delete(key_id) -> DeletionCertificate                      |
   |  audit() -> AuditReport                                     |
   |  save(path) / load(path) -> None                            |
   +------+-------------------+-------------------+-------------+
          |                   |                   |             |
          v                   v                   v             v
  +---------------+   +--------------+   +---------------+   +------+
  | substrate_    |   | faiss_       |   | chroma_       |   | ...  |
  | memory        |   | adapter      |   | adapter       |   |      |
  +-------+-------+   +------+-------+   +------+--------+   +------+
          |                  |                  |
          v                  v                  v
  +---------------+   +--------------+   +---------------+
  |  hdlab.atoms  |   | faiss.Index  |   | chromadb      |
  |  hdlab.binding|   | Flat / HNSW  |   | PersistentCl. |
  | W matrix      |   |              |   |               |
  | (.npy)        |   | (.faiss)     |   | (.parquet)    |
  +---------------+   +--------------+   +---------------+
```

## Component specs

### 1. `testbed/api.py` -- shared types and ABC

```python
from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass
class RetrievalResult:
    key_id: str | None        # None if rejected (below threshold)
    value: str | None
    confidence: float          # backend-defined; substrate uses softmax max-prob
    near_uniform_flag: bool    # KF-1 signal; True if confidence < 50/C
    distance: float | None     # for embedding backends

@dataclass
class DeletionCertificate:
    key_id: str
    var_ratio: float | None    # TCFT: substrate-specific; None for baselines
    erased: bool               # post-delete retrieve returned different key
    timestamp_ns: int

@dataclass
class AuditReport:
    backend: str
    n_items: int
    kf1_above_thresh_frac: float | None    # substrate only
    kf2_max_isolation: float | None        # substrate only
    tcft_mean_var_ratio: float | None      # substrate only
    storage_bytes: int

class MemoryBackend:
    """Abstract base. All five backends implement this surface."""
    name: str

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None: ...
    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult: ...
    def edit(self, key_id: str, new_value: str) -> None: ...
    def delete(self, key_id: str) -> DeletionCertificate: ...
    def audit(self) -> AuditReport: ...
    def save(self, path: Path) -> None: ...
    def load(self, path: Path) -> None: ...
    def __len__(self) -> int: ...
```

### 2. `testbed/substrate_memory.py` -- substrate backend

Wraps the existing primitives. Reuses `store_facts_outer` (proven in
`experiments/exp_kf1_hallu_impossibility_v2.py` line 93-101) and BSC codebook builder
(proven in `experiments/exp_kf1_hallu_rescue_v4_n8192_bsc.py` line 108-113).

```python
class SubstrateMemory(MemoryBackend):
    name = "substrate"

    def __init__(self, N: int = 4096, codebook_kind: str = "bsc",
                 codebook_scale: int = 4, beta: float = 32.0,
                 hallu_threshold: float = 0.5, device: str = "cpu"):
        # codebook_kind in {"bsc", "kerdock", "gaussian"}
        # Kerdock requires log2(N) even -- raise on violation
        self.N = N
        self.beta = beta
        self.hallu_threshold = hallu_threshold
        self.W = torch.zeros(N, N, dtype=torch.float32, device=device)
        self.codebook = _build_codebook(N, codebook_kind, codebook_scale, seed=0)
        self.key_registry: dict[str, int] = {}    # key_id -> codebook row
        self.value_registry: dict[str, str] = {}   # key_id -> value string
        self.value_atom_registry: dict[str, int] = {}  # key_id -> value codebook row
        self.W_path: Path | None = None            # set on save/load

    def store(self, key_id, key_vec, value):
        # Allocate codebook rows for key and value (round-trip through atom hash)
        # key_vec is a deterministic float vec; we map to nearest codebook atom
        # OR we accept the codebook index directly via key_id and synthesize on demand
        # W += outer(value_atom, key_atom) -- the Hebbian write
        ...

    def retrieve(self, query_vec, k=1):
        # q_atom = nearest codebook atom to query_vec
        # response = W @ q_atom
        # sims = (codebook @ response) / N
        # P = softmax(beta * sims); argmax + max_prob
        # near_uniform_flag = max_prob < 50/C (KF-1 inset of C=4*N)
        ...

    def edit(self, key_id, new_value):
        # Subtract old outer product, add new one (KF-2 isolation-preserving edit)
        # W -= outer(old_value_atom, key_atom); W += outer(new_value_atom, key_atom)
        ...

    def delete(self, key_id):
        # TCFT-style fresh-erase: subtract outer(value_atom, key_atom)
        # measure var_ratio = var(W_after_delete @ key_atom) / var(random_query response)
        # < 0.1 -> certificate.erased = True
        ...

    def audit(self):
        # Sample a panel of OOS queries -> compute above_thresh_frac (KF-1)
        # Sample edit candidates -> compute max isolation_ratio (KF-2)
        # Sample deletions -> compute mean var_ratio (TCFT)
        ...

    def save(self, path):
        # path is a dir; write W.npy, codebook.npy, key_registry.json, config.yaml
        # use np.memmap for W to enable cheap reload at scale
        ...
```

Codebook builders (in `testbed/codebooks.py`):
- `_build_bsc(N, C)`: random +/-1, shape (C, N). Verified in v4 rescue.
- `_build_kerdock(N)`: requires log2(N) even; raise ValueError otherwise. Wraps
  `experiments/exp_wave14y_erase_kerdock_v3.make_kerdock_4coset_codebook`.
- `_build_gaussian(N, C)`: random N(0, 1/sqrt(N)).

### 3. `testbed/baselines/` -- comparison backends

#### `faiss_adapter.py`
```python
class FaissMemory(MemoryBackend):
    name = "faiss"
    def __init__(self, dim: int, index_kind: str = "Flat"):
        import faiss
        self.index = faiss.IndexFlatIP(dim)  # cosine if normalized
        self.id_to_value: dict[str, str] = {}
        self.id_order: list[str] = []
    # store/retrieve/edit/delete trivially via index.add / index.search /
    # rebuild-on-edit. delete returns DeletionCertificate(var_ratio=None,
    # erased=True) -- baselines have no TCFT signal.
```

#### `chroma_adapter.py`
```python
class ChromaMemory(MemoryBackend):
    name = "chroma"
    def __init__(self, persist_dir: Path):
        import chromadb
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.col = self.client.get_or_create_collection("testbed")
```

#### `sqlite_vec_adapter.py`
```python
class SqliteVecMemory(MemoryBackend):
    name = "sqlite_vec"
    def __init__(self, db_path: Path, dim: int):
        import sqlite3, sqlite_vec
        self.conn = sqlite3.connect(str(db_path))
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        # CREATE VIRTUAL TABLE vec USING vec0(embedding float[<dim>])
```

#### `dict_adapter.py` -- sanity baseline
```python
class DictMemory(MemoryBackend):
    name = "dict"
    # Exact key lookup. retrieve uses brute-force cosine over stored keys.
    # Useful as ground-truth oracle for recall scenarios.
```

### 4. `testbed/harness.py`

```python
def run_scenario(scenario_name: str, backend: MemoryBackend,
                 config: dict, out_dir: Path) -> dict:
    """Dispatch scenario, time it, write results.json, return metrics dict."""

def run_matrix(scenarios: list[str], backends: list[str],
               config: dict, out_root: Path) -> Path:
    """Run cross product, write summary.json + markdown table."""
```

### 5. `testbed/scenarios/`

One file per scenario. Each exposes:
```python
def setup(config: dict) -> tuple[KeysVecs, Values, Queries]: ...
def run(backend: MemoryBackend, data) -> dict: ...
def thresholds() -> dict:  # HARD_PASS / HARD_FAIL bands
```

### 6. `testbed/report.py`

```python
def render_markdown(summary_path: Path) -> str:
    """Emit markdown with two sections:
       (A) cross-backend table (point_recall, latency, storage, continual)
       (B) killer-feature panel (substrate-only: KF-1, KF-2, TCFT)"""
```

### 7. CLI: `testbed/__main__.py`

```
python -m testbed run     --scenario all --backend all --config testbed/configs/default.yaml
python -m testbed run     --scenario point_recall --backend substrate,faiss
python -m testbed report  --run-dir testbed_data/benchmarks/results/2026-05-29T18-30-00
python -m testbed audit   --backend substrate --state-dir testbed_data/substrate_state
python -m testbed smoke   --backend substrate    # tiny N=512 M=64 sanity
```

## File layout (tree)

```
hd-instrument/
  testbed/
    __init__.py
    __main__.py                # CLI dispatch
    api.py                     # ABC + dataclasses
    harness.py                 # scenario runner
    report.py                  # markdown emitter
    codebooks.py               # bsc / kerdock / gaussian
    substrate_memory.py        # SubstrateMemory backend
    persistence.py             # W save/load helpers (memmap)
    baselines/
      __init__.py
      faiss_adapter.py
      chroma_adapter.py
      sqlite_vec_adapter.py
      dict_adapter.py
    scenarios/
      __init__.py
      point_recall.py
      edit_isolation.py
      deletion_verify.py
      hallu_detect.py
      continual_4stage.py
      storage_latency.py
    configs/
      default.yaml             # N=4096, M=10000, 5 seeds, all backends
      smoke.yaml               # N=512, M=64, 1 seed
    smoke_test.py              # runnable in <30s as gate before benchmark

C:\dev\hd-instrument\testbed_data\          # REMOTE only, gitignored
  substrate_state/
    default/
      W.npy                    # memmap-friendly; ~67 MB at N=4096 fp32
      codebook.npy             # ~67 MB at C=4N=16384, N=4096
      key_registry.json
      value_registry.json
      config.yaml
  benchmarks/
    datasets/
      synth_random_N4096_M10000_seed7.npz   # deterministic
      synth_random_N4096_M10000_seed17.npz
      ...
    results/
      2026-05-29T18-30-00/
        summary.json
        report.md
        per_scenario/
          point_recall_substrate.json
          point_recall_faiss.json
          ...
  baselines/
    faiss_indices/
      faiss_M10000.faiss
    chroma_db/
      <chroma sqlite + parquet files>
    sqlite_vec/
      testbed.db
```

## Dependency install plan (PowerShell on `marsh@home`)

Repo at `C:\dev\hd-instrument\` already has a working `.venv` (confirmed via
`d:/AI/hd-instrument/.venv/Lib/site-packages/` populated with numpy 2.4.5, pytorch,
duckdb, pyarrow). Reuse it; do not create a new venv.

Single-shot install (from local laptop via SSH):
```powershell
ssh marsh@home @'
$ErrorActionPreference = 'Stop'
cd C:\dev\hd-instrument
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install faiss-cpu==1.8.0.post1
python -m pip install chromadb==0.5.20
python -m pip install sqlite-vec==0.1.7a2
python -m pip install tabulate rich
python -c "import faiss, chromadb, sqlite_vec, tabulate, rich; print('OK')"
'@
```

Notes:
- `sentence-transformers` deliberately omitted from MVP. Synthetic random vectors are
  the apples-to-apples substrate, since BSC uses random hyperdims natively. If user
  later wants embedding comparisons, add as Phase 2.
- `chromadb` pulls a long dep tree (onnxruntime, tokenizers); ~400 MB install. Budget
  ~5 min wall on a reasonable laptop.
- `faiss-cpu` wheel on Windows is sometimes flaky; if it fails, fall back to
  `pip install faiss-cpu --no-build-isolation` or pin to 1.7.4.
- Per [[feedback-subagent-permission-inheritance]] the install MUST run from main
  thread (not a sub-agent) because SSH permissions don't inherit.

## Storage carving and disk estimates

| Path | Purpose | Size at default config (N=4096, M=10000) |
|------|---------|------------------------------------------|
| `testbed_data/substrate_state/default/W.npy` | W matrix fp32 | 67 MB |
| `testbed_data/substrate_state/default/codebook.npy` | BSC codebook C=4N | 67 MB |
| `testbed_data/substrate_state/default/key_registry.json` | id->idx map | <1 MB |
| `testbed_data/benchmarks/datasets/synth_*.npz` | 5 seeds x ~160 MB | 800 MB |
| `testbed_data/baselines/faiss_indices/` | Flat float32, M=10k, d=4096 | 160 MB |
| `testbed_data/baselines/chroma_db/` | sqlite + parquet | ~250 MB |
| `testbed_data/baselines/sqlite_vec/testbed.db` | vec0 virtual table | ~170 MB |
| `testbed_data/benchmarks/results/<ts>/` | per run | <10 MB |

Worst case total: ~1.5 GB. Comfortably on SSD. If user wants to constrain, drop
to N=2048 -> roughly 4x smaller (W=17 MB, codebook=17 MB, etc).

Open optimization: use `np.memmap` for `W.npy` so reload is O(file open) rather than
O(read 67 MB). `substrate_memory.load` should default to memmap mode for queries and
materialize a copy only when `edit` or `delete` is called.

## Eval scenarios

Each scenario follows the same skeleton:
- `setup(config)`: produce deterministic (keys, values, queries) tuple
- `run(backend, data)`: drive backend through scenario, time it
- Returns dict with metrics + HARD_PASS gate evaluation

### Scenario 1: `point_recall`

What gets stored: M deterministic key vectors (random BSC-equivalent +/-1 or
gaussian, seeded). Values are short strings `"fact_<i>"`.
What gets measured:
- `recall_at_1`: argmax retrieval matches stored value, fraction
- `recall_at_5`: top-5 contains correct
- `mean_confidence`: mean max-softmax-prob for substrate; mean cosine for baselines
- `p50_store_us`, `p95_store_us`, `p50_retrieve_us`, `p95_retrieve_us`

HARD_PASS thresholds:
- substrate at M/N <= 1.0: `recall_at_1 >= 0.95`
- substrate at M/N <= 2.0: `recall_at_1 >= 0.80` (above-capacity degradation expected)
- baselines (exact-search): `recall_at_1 >= 0.99`
HARD_FAIL: `recall_at_1 < 0.50` at M/N=0.25 (catastrophic recall failure)

### Scenario 2: `edit_isolation` (substrate KF-2)

What gets stored: K=1000 facts at M/N=0.25 (well under cap).
Edit operation: change value of 1 fact, leave others alone.
What gets measured (per backend that supports edits):
- `max_isolation_ratio`: `max(|delta_acc[j]|)` over non-edited keys
- `within_theory_frac`: fraction of cells with isolation_ratio < 1/sqrt(N)

Baselines: trivially `max_isolation_ratio = 0` since edits are key-isolated by
construction. This is the point. Substrate gets a SPECTRUM (max_iso < 0.05 at
N=4096 5-seed; confirmed in `exp_kf2_isolation_proof_v1`); baselines get 0.
The interesting axis is when we add ADVERSARIAL edits (key collision); see
extended scenario in Phase 2 backlog.

HARD_PASS (substrate): `max_isolation_ratio < 0.05` (matches v1 N=4096 anchor).
HARD_FAIL (substrate): `max_isolation_ratio >= 0.10`.

### Scenario 3: `deletion_verify` (substrate TCFT)

What gets stored: M=512 facts at N=4096 (TCFT v3 5-seed gate band).
Delete operation: subtract `outer(value_atom, key_atom)` from W.
Post-delete retrieve on the deleted key vector.
What gets measured:
- `tcft_variance_ratio`: `var(W_after @ key) / var(W_before @ random_key)`
- `retrieve_after_delete_returns_different`: bool per deletion
- `mean_var_ratio` across M deletion trials

Baselines: deletion is structural (FAISS rebuild, Chroma row delete). Returns
`DeletionCertificate(var_ratio=None, erased=True)`. The substrate produces a
NUMERIC certificate showing the deleted vector is no longer recoverable from W
itself, not just from a lookup table. This is the auditable-erase product story.

HARD_PASS (substrate): `mean_var_ratio < 0.10` (matches TCFT v3 N=8192 5-seed and
v4 N=4096 5-seed bands).
HARD_FAIL: `mean_var_ratio >= 0.30`.

### Scenario 4: `hallu_detect` (substrate KF-1)

What gets stored: M facts at M/N in {0.25, 0.5, 1.0} (under-cap regimes).
Query: 1000 OOS keys NOT in the stored set.
What gets measured:
- `mean_oos_max_conf`: average softmax max over OOS queries
- `above_thresh_frac`: fraction with max_conf >= 0.5 (HALLU_THRESHOLD)
- `near_uniform_frac`: fraction with max_conf < 50/C

Baselines: nearest-neighbor in FAISS will ALWAYS return its argmin distance
regardless of whether the query is in-store. Without a distance threshold,
`above_thresh_frac = 1.0` (every query gets a confident answer). With a
heuristic threshold, baselines can detect OOS at some recall cost, but they
lack a structural argument. The substrate gives `above_thresh_frac = 0` at
M <= N (confirmed in `exp_kf1_hallu_impossibility_v2` 5-seed and v4 BSC at
N=8192).

HARD_PASS (substrate): `above_thresh_frac == 0` at all under-cap cells AND
`mean_oos_max_conf < 0.001`. Matches v2 5-seed tightened gate.
HARD_FAIL: any seed shows `above_thresh_frac > 0` at M <= N.

For baselines, report `recall_at_1_on_OOS` (should be ~0, the killer comparison
metric).

### Scenario 5: `continual_4stage`

Inspired by Bet B 4-stage CL (smoke HARD_PASS at v234). Light version: 4 batches
A, B, C, D of size M/4 each. After all 4 batches stored, measure retention on
batch A.
What gets measured:
- `ret_A_after_B`, `ret_A_after_C`, `ret_A_after_D`
- `ret_B_after_D`, `ret_C_after_D`
- `final_recall_at_1` per batch

HARD_PASS (substrate, light): `ret_A_after_D >= 0.65` (loose; substrate
characterised at 0.74-0.81 in production CL studies).
HARD_PASS (baselines): `>= 0.99` (no interference; this is the contrast).
HARD_FAIL (substrate): `ret_A_after_D < 0.40`.

Note: this scenario is the WEAK point for substrate. Report transparently.
Substrate's edge is the audit dimension, not the retention dimension at scale.

### Scenario 6: `storage_latency`

What gets measured (per backend, scanned across M in {1k, 5k, 10k}):
- disk_bytes after store of M items
- `p50_store_us`, `p95_store_us` per item
- `p50_retrieve_us`, `p95_retrieve_us` per item
- `cold_load_ms`: time to load persisted state from disk

HARD_PASS: nothing pre-registered. This scenario is descriptive.
What we EXPECT: substrate is fastest on retrieve (single W @ q + small codebook
matmul), slowest on cold load (must mmap W). FAISS Flat is comparable on
retrieve. Chroma is slowest on retrieve (HTTP-ish indirection). sqlite-vec is
mid-tier.

## Implementation roadmap (3 parallel workstreams)

All three can start at T=0 once design is approved. They share `testbed/api.py`,
which is the FIRST file that must be written (10 min, single-author serial).

### Workstream D: substrate daemon (target 80 min)

Owner: `exp_dev`-style agent comfortable with `hdlab/` + `experiments/`.

Files:
- `testbed/api.py` (the shared types) -- 10 min, BLOCKS others
- `testbed/codebooks.py` -- 15 min, wraps `make_bsc_codebook` from
  `experiments/exp_kf1_hallu_rescue_v4_n8192_bsc.py:108`. Add kerdock + gaussian.
- `testbed/persistence.py` -- 15 min, `save_W`, `load_W_memmap`, `save_registry`
- `testbed/substrate_memory.py` -- 40 min, the SubstrateMemory class implementing
  ABC. Reuse `store_facts_outer` (verified in
  `experiments/exp_kf1_hallu_impossibility_v2.py:93-101`).
- `testbed/smoke_test.py` -- 10 min, runs N=512 M=64 store/retrieve/edit/delete
  loop, asserts recall>=0.9, deletion var_ratio<0.2

Key methods (signatures, NOT impl):
```python
SubstrateMemory.__init__(self, N=4096, codebook_kind="bsc", device="cpu", **kw)
SubstrateMemory.store(self, key_id: str, key_vec: np.ndarray, value: str) -> None
SubstrateMemory.retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult
SubstrateMemory.edit(self, key_id: str, new_value: str) -> None
SubstrateMemory.delete(self, key_id: str) -> DeletionCertificate
SubstrateMemory.audit(self) -> AuditReport
SubstrateMemory.save(self, path: Path) -> None
SubstrateMemory.load(self, path: Path) -> None
```

Smoke gate: `python testbed/smoke_test.py --backend substrate` exits 0.

### Workstream B: baselines + harness (target 70 min)

Files:
- `testbed/baselines/dict_adapter.py` -- 10 min (oracle, simplest)
- `testbed/baselines/faiss_adapter.py` -- 20 min, IndexFlatIP + id_map
- `testbed/baselines/chroma_adapter.py` -- 20 min, PersistentClient + collection
- `testbed/baselines/sqlite_vec_adapter.py` -- 20 min, vec0 + UPDATE/DELETE

Then:
- `testbed/harness.py` -- 30 min, `run_scenario` + `run_matrix`, captures timing
  per call via `time.perf_counter_ns()`

Smoke gate: `python -m testbed smoke --backend dict,faiss,chroma,sqlite_vec`
runs <30s and all return recall_at_1 >= 0.99 on M=64 store/retrieve.

### Workstream E: scenarios + report + CLI (target 90 min)

Files (one per scenario, 12-15 min each, parallelisable):
- `testbed/scenarios/point_recall.py`
- `testbed/scenarios/edit_isolation.py`
- `testbed/scenarios/deletion_verify.py`
- `testbed/scenarios/hallu_detect.py`
- `testbed/scenarios/continual_4stage.py`
- `testbed/scenarios/storage_latency.py`

Then:
- `testbed/configs/default.yaml` + `smoke.yaml` -- 10 min
- `testbed/report.py` -- 20 min, markdown with tabulate
- `testbed/__main__.py` -- 15 min, argparse dispatch

Smoke gate: `python -m testbed run --scenario point_recall --backend substrate,faiss --config testbed/configs/smoke.yaml`
produces `testbed_data/benchmarks/results/<ts>/report.md` containing a 2-row
table within 60s.

### Sequencing

```
T=0          T=10                                            T=180
|------------|-----------------------------------------------|
|  api.py    |  workstream D ===================>            |
|            |  workstream B ===================>            |
|            |  workstream E ===========================>    |
|                                          T=170             |
|                                          INTEGRATION:      |
|                                          python -m testbed |
|                                            run --scenario  |
|                                            all --backend   |
|                                            all --config    |
|                                            default.yaml    |
```

Order to dispatch in Phase 2: **D first** (substrate is the load-bearing piece
with the most subtle bugs), **B second** (baselines), **E third** (scenarios
depend on both backends existing). All can run on the SAME remote host serially
or in parallel sub-agents.

## Risk register (top 3 + mitigations)

### Risk 1: Substrate API confidence semantics drift from baseline semantics

Symptom: `RetrievalResult.confidence` means softmax-max-prob in substrate, cosine
similarity in FAISS, distance score in Chroma. Naively comparing them in scenario
metrics produces misleading "substrate confidence is 0.4 vs FAISS 0.8" tables.

Mitigation: harness records BOTH `confidence_raw` (backend-native) AND
`confidence_normalized` (rank-only: 1.0 if argmax-correct else 0.0). Comparison
tables show confidence_normalized + per-backend native confidence in a footnote.
Pre-register this in `report.py` template, NOT at scenario write time.

### Risk 2: chromadb install hangs or fails on Windows (long dep tree)

Symptom: `pip install chromadb` pulls onnxruntime / tokenizers / pyarrow, can take
5-10 min or hit Visual C++ build errors on Windows.

Mitigation: run dependency install in the FIRST 10 min of the 3h window (parallel
to writing `testbed/api.py`). If chromadb fails, drop to FAISS + sqlite-vec +
dict-only baselines and document as "chroma comparison deferred". This is a
graceful degradation; the killer-feature panel doesn't need chroma to be the
story.

### Risk 3: Substrate retrieval requires query-vec to be a codebook atom

Symptom: substrate's `retrieve(query_vec)` only works cleanly when query_vec is
one of the stored codebook atoms (because BSC is structured around +/-1 atoms).
If user passes arbitrary float vectors, retrieval degrades silently.

Mitigation: explicit policy -- `SubstrateMemory.store` allocates a NEW codebook
row for each `key_id` (synthesizes a random BSC atom) and `retrieve` requires
the caller to query with the SAME key_vec semantics. For apples-to-apples vs
FAISS/Chroma, the synthetic dataset MUST be built from the substrate's codebook
atoms (or any random +/-1 vectors), then those same vectors are inserted into
baselines as raw fp32. `point_recall.setup` enforces this.

Bonus mitigation: add an explicit `SubstrateMemory.snap_to_atom(vec) -> atom`
helper so adversarial / OOS queries get snapped to nearest codebook entry. This
is the canonical pattern in `exp_kf1_hallu_impossibility_v2`.

## Phase 2 backlog (NOT in MVP)

- HTTP server (FastAPI) wrapping `MemoryBackend` for cross-language tests
- Sentence-embedding baseline (sentence-transformers) for natural-language
  comparisons
- LLM integration: substrate as RAG store for a small local LLM, measure
  hallucination rate on out-of-store questions
- Adversarial edit scenarios: collisions, near-collisions, capacity-stress
- Drift detection scenario (substrate KF-4)
- Cross-codebook isolation scenario (substrate KF-3)
- Dashboard panel reading from `testbed_data/benchmarks/results/`

## Open decisions deferred to user

- Default N: 4096 chosen (matches verified Kerdock + BSC + Gaussian regime, 67 MB
  W matrix, fast on CPU). User can override to 2048 for cheaper / 8192 for
  more-extreme demo.
- Codebook kind default: BSC (works at any N, matches latest substrate work in
  SKAH-M class). Kerdock available as opt-in for users wanting structured-codebook
  demos.
- Default M: 10000 (above N=4096 capacity; demonstrates substrate degrades
  gracefully where baselines maintain exact recall). User can drop to M=2000
  (under-cap) for cleaner substrate KF1/KF2 numbers.
- Whether to ship a streamlit/rich live dashboard tab as part of MVP -- DEFERRED;
  markdown report is the MVP surface.

## Definition of done (gate before declaring MVP shipped)

1. `python testbed/smoke_test.py --backend substrate` exits 0 in <30s
2. `python -m testbed run --scenario all --backend substrate,faiss,chroma,sqlite_vec,dict --config testbed/configs/default.yaml` completes <30 min
3. `testbed_data/benchmarks/results/<ts>/report.md` contains:
   - Cross-backend table for all 6 scenarios
   - Killer-feature panel with substrate numbers for KF-1, KF-2, TCFT (and
     "N/A by construction" placeholders for baselines)
4. Substrate state persists: `python -m testbed audit --backend substrate --state-dir testbed_data/substrate_state/default` reads from disk and reproduces the audit numbers from item 3
5. User can run `python -m testbed run --scenario point_recall --backend substrate --config <custom>.yaml` with edited config and see different results
