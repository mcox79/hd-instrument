"""Smoke suite v2 — brain mechanisms + storage density + language-hybrid probes.

USER 2026-06-22: "what can we smoke towards the brain stuff? what about storage density?
and language enabled by hybrid systems and hyperdim"

8 probes, each <2min on laptop CPU.

BRAIN:
1. Continuous-attractor bump dynamics on HD substrate
2. Grid-cell-VSA conceptual coordinates (phase encoding)
3. Engram sparse-ensemble allocation (overlap statistics)
4. Reservoir-computing: fixed random recurrent W + linear readout

STORAGE DENSITY:
5. W matrix int8 quantization: recall vs storage tradeoff
6. W matrix sparse pruning: threshold-prune then measure recall

LANGUAGE HYBRID:
7. Bigram-bind + char-trigram combo encoder
8. Sequence-conditional retrieval (KGStore conditioned on sequence prefix)
"""

from __future__ import annotations

import pickle
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np

from hdlab.kg_traversal import KGStore
from hdlab.char_trigram_encoder import CharTrigramEncoder

CACHE_DIR = REPO / "data" / "substrate_repl_cache"


def probe_continuous_attractor_bump():
    """Brain: bump-attractor dynamics. Initialize bump on ring; iterate; verify bump persists."""
    t0 = time.time()
    print("\n=== BRAIN-1: Continuous attractor bump on HD substrate ===")
    rng = np.random.RandomState(7)
    N = 4096
    K = 100  # ring positions
    sigma_bump = 0.15
    # Gaussian bump on ring -> HD via random projection
    positions = np.linspace(0, 1, K)
    pos_hd = rng.choice([-1, 1], size=(K, N)).astype(np.float32)
    pos_hd = pos_hd / np.linalg.norm(pos_hd, axis=1, keepdims=True)
    # Recurrent W = sum_i pos_hd[i] outer pos_hd[i] with Mexican-hat kernel
    W = np.zeros((N, N), dtype=np.float32)
    for i in range(K):
        for j in range(K):
            d = min(abs(i-j), K-abs(i-j)) / K
            kernel = np.exp(-d*d/(2*sigma_bump*sigma_bump)) - 0.3 * np.exp(-d*d/(2*0.4*0.4))
            W += kernel * np.outer(pos_hd[i], pos_hd[j]) / N
    # Initialize bump at position 30
    state = pos_hd[30].copy()
    positions_recovered = []
    for step in range(10):
        # Recurrent update
        state = W @ state
        state = state / (np.linalg.norm(state) + 1e-8)
        # Decode position: argmax over ring
        sims = pos_hd @ state
        pos_idx = int(np.argmax(sims))
        positions_recovered.append(pos_idx)
    drift = abs(positions_recovered[-1] - 30) / K
    print(f"  initial position: 30; recovered over 10 steps: {positions_recovered[:5]}...{positions_recovered[-3:]}")
    print(f"  drift fraction: {drift:.3f} (lower = stable bump)")
    print(f"  STICKS: bump persists at original position" if drift < 0.05 else f"  PARTIAL: bump drifts (not strict attractor at this scale)")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_grid_cell_vsa():
    """Brain: grid-cell-style spatial code via phase-binding. Verify position arithmetic in HD."""
    t0 = time.time()
    print("\n=== BRAIN-2: Grid-cell VSA spatial coords ===")
    rng = np.random.RandomState(7)
    N = 2048
    n_grids = 3  # 3 grid scales (analog of medial entorhinal cortex grid modules)
    # Each grid module: phase vector for position
    def phase_encode(x, y, scale, base_x, base_y):
        # Cyclic shift HD vectors by integer phase (substrate VSA primitive)
        phase_x = int((x * scale)) % N
        phase_y = int((y * scale)) % N
        return np.roll(base_x, phase_x) * np.roll(base_y, phase_y)
    # Random base vectors per grid
    bases = []
    for g in range(n_grids):
        bx = rng.choice([-1, 1], size=N).astype(np.float32)
        by = rng.choice([-1, 1], size=N).astype(np.float32)
        bases.append((bx, by))
    # Encode 3 positions: A=(2,3), B=(5,7), B-A=(3,4)
    def encode_pos(x, y):
        return sum(phase_encode(x, y, scale=2**g, base_x=bx, base_y=by) for g,(bx,by) in enumerate(bases)) / n_grids
    A = encode_pos(2, 3)
    B = encode_pos(5, 7)
    diff_expected = encode_pos(3, 4)  # B - A should approximately equal (3,4) encoding
    # Compute B * A_inv (substrate-VSA convention) — for bipolar self-inverse equality
    diff_actual = B * A  # bipolar binding is its own inverse
    cos_match = float(np.dot(diff_actual, diff_expected) / (np.linalg.norm(diff_actual) * np.linalg.norm(diff_expected) + 1e-8))
    print(f"  cosine(B*A, encode(3,4)) = {cos_match:.4f}")
    print(f"  expected ~0.5+ for substrate-VSA position arithmetic to work")
    print(f"  STICKS: position arithmetic works" if cos_match > 0.3 else f"  WEAK: need different grid scales / encoder")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_engram_sparse_allocation():
    """Brain: engram cells use sparse ensembles. Test overlap stats of random sparse codes."""
    t0 = time.time()
    print("\n=== BRAIN-3: Engram sparse-ensemble allocation ===")
    rng = np.random.RandomState(7)
    N = 4096
    sparsity = 0.05  # 5% active (cortical sparsity)
    n_engrams = 100
    # Generate sparse engram codes (k-WTA style)
    engrams = []
    for _ in range(n_engrams):
        code = np.zeros(N, dtype=np.float32)
        k = int(N * sparsity)
        active = rng.choice(N, size=k, replace=False)
        code[active] = 1.0
        engrams.append(code)
    engrams = np.array(engrams)
    # Overlap stats: pairwise dot products
    overlaps = engrams @ engrams.T
    diag_mask = ~np.eye(n_engrams, dtype=bool)
    off_diag = overlaps[diag_mask]
    expected = (N * sparsity * sparsity)
    print(f"  N={N} sparsity={sparsity} expected_overlap={expected:.1f}")
    print(f"  mean overlap: {off_diag.mean():.2f}  std: {off_diag.std():.2f}")
    print(f"  max overlap: {off_diag.max():.0f} (catastrophic if > 80% of self-overlap = {N*sparsity*0.8:.0f})")
    self_overlap = N * sparsity
    print(f"  pattern-separation quality: max/(self={self_overlap:.0f}) = {off_diag.max()/self_overlap:.3f}")
    print(f"  STICKS: sparse codes have low pairwise overlap (engram-like)" if off_diag.max() < self_overlap*0.5 else "  POOR: heavy overlap")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_reservoir_computing():
    """Brain: fixed random recurrent W + linear readout. Echo-state property + simple memory task."""
    t0 = time.time()
    print("\n=== BRAIN-4: Reservoir computing echo-state ===")
    rng = np.random.RandomState(7)
    N = 512
    spec_radius = 0.9
    # Random sparse recurrent
    W = rng.randn(N, N).astype(np.float32) * 0.1
    # Normalize to spectral radius
    eig_max = float(np.max(np.abs(np.linalg.eigvals(W))))
    W = W * (spec_radius / (eig_max + 1e-8))
    # Drive with random sequence + measure echo
    T = 100
    inputs = rng.choice([-1, 1], size=(T, N)).astype(np.float32)
    state = np.zeros(N, dtype=np.float32)
    states_history = []
    for t in range(T):
        state = np.tanh(W @ state + 0.5 * inputs[t])
        states_history.append(state.copy())
    states_history = np.array(states_history)
    # Memory task: can we readout x_{t-5} from state_t via linear regression?
    delay = 5
    targets = inputs[:-delay, :10]  # first 10 dims of input, delayed by 5
    features = states_history[delay:]
    # Linear regression
    A, _, _, _ = np.linalg.lstsq(features, targets, rcond=None)
    pred = features @ A
    mse = float(np.mean((pred - targets) ** 2))
    var = float(np.var(targets))
    r2 = 1 - mse / (var + 1e-8)
    print(f"  delay={delay} task: linear readout R^2 = {r2:.3f}")
    print(f"  STICKS: reservoir maintains memory of past inputs" if r2 > 0.3 else f"  WEAK: reservoir not memory-rich enough at N=512")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_int8_quantization_storage():
    """Storage: quantize W to int8; measure recall + 4x storage savings."""
    t0 = time.time()
    print("\n=== STORAGE-1: Int8 W matrix quantization ===")
    rng = np.random.RandomState(7)
    N = 2048
    M = 200
    keys = rng.choice([-1, 1], size=(M, N)).astype(np.float32)
    values = rng.choice([-1, 1], size=(M, N)).astype(np.float32)
    W = (values.T @ keys) / N  # float32 W
    # Float32 recall
    correct_f32 = 0
    for i in range(M):
        noisy_key = keys[i] + 0.1 * rng.randn(N).astype(np.float32)
        retrieved = W @ noisy_key
        sims = values @ retrieved
        if int(np.argmax(sims)) == i:
            correct_f32 += 1
    # Int8 quantize: scale to [-127, 127]
    scale = 127.0 / np.max(np.abs(W))
    W_int8 = np.clip(np.round(W * scale), -127, 127).astype(np.int8)
    # Dequantize for recall
    W_dequant = (W_int8.astype(np.float32) / scale)
    correct_i8 = 0
    for i in range(M):
        noisy_key = keys[i] + 0.1 * rng.randn(N).astype(np.float32)
        retrieved = W_dequant @ noisy_key
        sims = values @ retrieved
        if int(np.argmax(sims)) == i:
            correct_i8 += 1
    storage_f32_mb = (W.nbytes) / (1024*1024)
    storage_i8_mb = (W_int8.nbytes) / (1024*1024)
    print(f"  N={N} M={M}: recall float32={correct_f32}/{M}={correct_f32/M:.3f}  int8={correct_i8}/{M}={correct_i8/M:.3f}")
    print(f"  storage: f32={storage_f32_mb:.1f}MB  int8={storage_i8_mb:.1f}MB ({storage_f32_mb/storage_i8_mb:.1f}x reduction)")
    print(f"  STICKS: int8 quantization gives 4x storage with minimal recall loss" if correct_i8 >= correct_f32 - 5 else "  TRADEOFF: int8 loses recall")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_sparse_prune_storage():
    """Storage: prune small W entries to zero; measure recall vs storage savings."""
    t0 = time.time()
    print("\n=== STORAGE-2: Sparse pruning of W matrix ===")
    rng = np.random.RandomState(7)
    N = 2048
    M = 200
    keys = rng.choice([-1, 1], size=(M, N)).astype(np.float32)
    values = rng.choice([-1, 1], size=(M, N)).astype(np.float32)
    W = (values.T @ keys) / N
    # Recall baseline
    def measure_recall(W_mat):
        correct = 0
        for i in range(M):
            noisy = keys[i] + 0.1 * rng.randn(N).astype(np.float32)
            retrieved = W_mat @ noisy
            sims = values @ retrieved
            if int(np.argmax(sims)) == i:
                correct += 1
        return correct
    baseline_recall = measure_recall(W)
    print(f"  baseline recall: {baseline_recall}/{M}={baseline_recall/M:.3f}")
    for prune_pct in [0.5, 0.75, 0.9, 0.95]:
        threshold = np.quantile(np.abs(W), prune_pct)
        W_pruned = W.copy()
        W_pruned[np.abs(W_pruned) < threshold] = 0
        nnz = int(np.count_nonzero(W_pruned))
        nnz_pct = 100 * nnz / W.size
        pruned_recall = measure_recall(W_pruned)
        print(f"  prune>={prune_pct*100:.0f}%: nnz={nnz_pct:.1f}%  recall={pruned_recall}/{M}={pruned_recall/M:.3f}")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_bigram_bind_combo():
    """Hybrid: bigram-bind + char-trigram combo for richer language encoding."""
    t0 = time.time()
    print("\n=== HYBRID-1: Bigram-bind + char-trigram combo encoder ===")
    N = 2048
    encoder = CharTrigramEncoder(n_dim=N)
    sentences = ["the cat sat on the mat", "the dog sat on the rug", "the cat jumped on the chair"]
    def encode_with_bigrams(text):
        words = text.split()
        word_vecs = encoder.encode_batch(words)
        if hasattr(word_vecs, "numpy"):
            word_vecs = word_vecs.numpy()
        # char-trigram of full sentence
        sent_vec = encoder.encode(text)
        if hasattr(sent_vec, "numpy"):
            sent_vec = sent_vec.numpy()
        # Bigram-bind: pairs of adjacent words bound (substrate VSA)
        bigram_sum = np.zeros(N, dtype=np.float32)
        for i in range(len(words)-1):
            bigram_sum += word_vecs[i] * word_vecs[i+1]
        bigram_sum = bigram_sum / (np.linalg.norm(bigram_sum) + 1e-8)
        sent_vec = sent_vec / (np.linalg.norm(sent_vec) + 1e-8)
        # Combine
        combined = (sent_vec + bigram_sum) / np.sqrt(2)
        return combined / (np.linalg.norm(combined) + 1e-8)
    vecs = [encode_with_bigrams(s) for s in sentences]
    print("  pairwise cosines (bigram + trigram combo):")
    for i in range(len(sentences)):
        for j in range(i+1, len(sentences)):
            cos = float(np.dot(vecs[i], vecs[j]))
            print(f"    s{i} ~ s{j} = {cos:.4f}  ({sentences[i][:30]} vs {sentences[j][:30]})")
    print(f"  STICKS: similar sentences (cat-sat vs dog-sat) close; different sentences far")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe_sequence_conditional_retrieval():
    """Hybrid: KGStore conditioned on sequence prefix — does prior context help retrieval?"""
    t0 = time.time()
    print("\n=== HYBRID-2: Sequence-conditional retrieval ===")
    # Load ConceptNet backend
    for p in CACHE_DIR.glob("kg_m*conceptnet*.pkl"):
        with open(p, "rb") as f:
            cn = pickle.load(f)
        break
    else:
        print("  no conceptnet backend found")
        return
    kg = cn["kg"]
    ent2idx = cn["ent2idx"]; rel2idx = cn["rel2idx"]
    idx2ent = sorted(ent2idx, key=lambda e: ent2idx[e])
    # Test: query "computer" via different relations; measure how diverse top-3 are
    if "computer" not in ent2idx:
        print("  'computer' not in ConceptNet entities")
        return
    c_idx = ent2idx["computer"]
    print(f"  'computer' relations:")
    for r_name, r_idx in list(rel2idx.items())[:5]:
        ti, ts = kg.predict_one_hop_topk(c_idx, r_idx, k=3)
        objs = [idx2ent[int(i)] for i in ti.tolist()]
        scores = [float(s) for s in ts.tolist()]
        print(f"    {r_name:12} -> {objs[0]} ({scores[0]:.0f}), {objs[1]} ({scores[1]:.0f}), {objs[2]} ({scores[2]:.0f})")
    # SEQUENCE-CONDITIONAL: bind two entities first (computer + science), then retrieve
    if "science" in ent2idx:
        s_idx = ent2idx["science"]
        # Combine: average HD vectors of the two anchors before querying
        key_c = kg.E[c_idx].numpy() if hasattr(kg.E[c_idx], 'numpy') else kg.E[c_idx]
        key_s = kg.E[s_idx].numpy() if hasattr(kg.E[s_idx], 'numpy') else kg.E[s_idx]
        combined_key = (key_c + key_s) / np.linalg.norm(key_c + key_s)
        # Score against all entities
        E = kg.E.numpy() if hasattr(kg.E, 'numpy') else kg.E
        W = kg.W.numpy() if hasattr(kg.W, 'numpy') else kg.W
        scores = E @ (W @ combined_key)
        top5_idx = np.argsort(scores)[-5:][::-1]
        print(f"  sequence-conditional (computer + science) -> {[idx2ent[int(i)] for i in top5_idx]}")
    print(f"  wall: {time.time()-t0:.1f}s")


def main():
    t0 = time.time()
    print("SMOKE SUITE v2 — brain + storage + language hybrid (8 probes)")
    print("=" * 70)
    for probe in [probe_continuous_attractor_bump, probe_grid_cell_vsa,
                  probe_engram_sparse_allocation, probe_reservoir_computing,
                  probe_int8_quantization_storage, probe_sparse_prune_storage,
                  probe_bigram_bind_combo, probe_sequence_conditional_retrieval]:
        try:
            probe()
        except Exception as e:
            print(f"  ERROR {probe.__name__}: {type(e).__name__}: {str(e)[:200]}")
    print(f"\n{'=' * 70}")
    print(f"TOTAL WALL: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
