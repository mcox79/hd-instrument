"""Inspect CELL-2 v3 shard structure to verify CELL-3 + CELL-4 can load it."""
import numpy as np
import sys

shard_path = "/mnt/d/AI/hd-instrument/data/cell2_results/shard_00000.npz"
print(f"Loading {shard_path}")
arr = np.load(shard_path, allow_pickle=True)
print(f"Keys: {list(arr.keys())}")
for key in arr.keys():
    a = arr[key]
    if hasattr(a, 'shape'):
        print(f"  {key}: shape={a.shape} dtype={a.dtype}")
    else:
        print(f"  {key}: type={type(a).__name__}")

print()
print("Sample values:")
if "article_ids" in arr:
    print(f"  article_ids[:3]: {list(arr['article_ids'][:3])}")
if "titles" in arr:
    print(f"  titles[:3]: {list(arr['titles'][:3])}")
else:
    print(f"  titles: MISSING (CELL-4 expects this!)")
if "hidden_states" in arr:
    hs = arr["hidden_states"]
    print(f"  hidden_states[0,:5]: {hs[0,:5]} (dtype={hs.dtype})")
    print(f"  hidden_states stats: mean={hs.mean():.4f} std={hs.std():.4f}")
