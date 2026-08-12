"""Remote: smoke-verify that the updated fresh_W_v2 cell can load word2vec from v2.

Runs only the word2vec load path (not full cell). Exits 0 if KV loads cleanly.
"""
import os
import sys
import traceback

REPO = "C:/dev/hd-instrument"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

print("[smoke] testing helper load of word2vec-google-news-300 from v2 cache...")
try:
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(
        "word2vec-google-news-300",
        cache_dir="C:/dev/hd-instrument/data/gensim_cache_v2",
    )
    print("[smoke] OK vec_size=" + str(kv.vector_size)
          + " vocab=" + str(len(kv.key_to_index)))
except Exception as e:
    print("[smoke] FAIL: " + type(e).__name__ + ": " + str(e))
    traceback.print_exc()
    sys.exit(1)
