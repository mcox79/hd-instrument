"""Remote diagnostic: try to load word2vec via gensim from primary cache; report what fails.

Run on marsh@home via: cd C:/dev/hd-instrument; .venv\Scripts\python.exe tools/_remote_w2v_diag.py
"""
import sys
import traceback

print("[diag] start")

try:
    import gensim.downloader as gd
    gd.BASE_DIR = "C:/dev/hd-instrument/data/gensim_cache"
    gd.base_dir = "C:/dev/hd-instrument/data/gensim_cache"
    print("[diag] gd patched")
except Exception:
    traceback.print_exc()
    sys.exit(2)

# Attempt 1: gd.load
print("[diag] attempting gd.load(word2vec-google-news-300)...")
try:
    m = gd.load("word2vec-google-news-300")
    print("[diag] OK gd.load: vec_size=" + str(m.vector_size) + " vocab=" + str(len(m.key_to_index)))
    sys.exit(0)
except Exception as e:
    print("[diag] gd.load failed: " + type(e).__name__ + ": " + str(e))

# Attempt 2: direct KeyedVectors
print("[diag] attempting direct KeyedVectors.load_word2vec_format on primary .gz...")
try:
    from gensim.models import KeyedVectors
    m = KeyedVectors.load_word2vec_format(
        "C:/dev/hd-instrument/data/gensim_cache/word2vec-google-news-300/word2vec-google-news-300.gz",
        binary=True,
    )
    print("[diag] OK direct: vec_size=" + str(m.vector_size) + " vocab=" + str(len(m.key_to_index)))
    sys.exit(0)
except Exception as e:
    print("[diag] direct failed: " + type(e).__name__ + ": " + str(e))
    traceback.print_exc()

sys.exit(3)
