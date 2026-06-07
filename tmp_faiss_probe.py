import sys, os, time
print(f"Python {sys.version}")
print(f"Platform: {sys.platform}")
print(f"venv: {sys.prefix}")
print(f"OS env KMP_DUPLICATE_LIB_OK: {os.environ.get('KMP_DUPLICATE_LIB_OK','<unset>')}")
print(f"OS env OMP_NUM_THREADS: {os.environ.get('OMP_NUM_THREADS','<unset>')}")
try:
    import faiss
    print(f"faiss version: {faiss.__version__}")
    print(f"faiss path: {faiss.__file__}")
except Exception as e:
    print(f"faiss import FAIL: {type(e).__name__}: {e}")
try:
    import numpy as np
    print(f"numpy {np.__version__} from {np.__file__}")
except Exception as e:
    print(f"numpy FAIL: {e}")
# Quick HNSW smoke test
try:
    import numpy as np, faiss
    print("=== HNSW build smoke (M=200, d=64; <1 sec) ===")
    d = 64; n = 200
    rng = np.random.default_rng(0)
    xb = rng.standard_normal((n, d)).astype("float32")
    t0 = time.time()
    idx = faiss.IndexHNSWFlat(d, 32)
    idx.add(xb)
    print(f"  HNSW build OK at n={n}; wall={time.time()-t0:.2f}s")
    print(f"  index size: {idx.ntotal}")
except Exception as e:
    print(f"HNSW build FAIL: {type(e).__name__}: {e}")
