"""Helper: verify testbed deps on a target Python. Run from venv."""
import sys

ok = True
mods = ["faiss", "chromadb", "sqlite_vec", "tabulate", "rich", "numpy", "torch", "yaml"]
for m in mods:
    try:
        mod = __import__(m)
        v = getattr(mod, "__version__", "n/a")
        print(f"  {m}: {v}")
    except Exception as e:
        print(f"  {m}: FAILED ({type(e).__name__}: {e})")
        ok = False
sys.exit(0 if ok else 1)
