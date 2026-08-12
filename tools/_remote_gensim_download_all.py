"""Remote: download all 3 gensim models into data/gensim_cache_v2.

Models: word2vec-google-news-300, glove-wiki-gigaword-300,
fasttext-wiki-news-subwords-300. Total ~3.2GB.

For each model, removes any partial subdir first (so gensim actually
re-downloads instead of trying to import an empty package).
"""
import os
import shutil
import sys
import time
import traceback

CACHE_DIR = "C:/dev/hd-instrument/data/gensim_cache_v2"
MODELS = [
    "word2vec-google-news-300",
    "glove-wiki-gigaword-300",
    "fasttext-wiki-news-subwords-300",
]

os.makedirs(CACHE_DIR, exist_ok=True)
LOG = os.path.join(CACHE_DIR, "_download_all.log")


def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = "[" + ts + "] " + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


try:
    import gensim.downloader as gd
    gd.BASE_DIR = CACHE_DIR
    gd.base_dir = CACHE_DIR
    log("gd patched; BASE_DIR=" + gd.BASE_DIR)
except Exception:
    traceback.print_exc()
    log("FAIL: gensim import")
    sys.exit(2)


for name in MODELS:
    log("--- " + name + " ---")
    model_dir = os.path.join(CACHE_DIR, name)
    gz = os.path.join(model_dir, name + ".gz")
    if os.path.exists(gz) and os.path.getsize(gz) > 100_000_000:
        log("already present at " + gz + " ("
            + str(os.path.getsize(gz)) + " bytes); skipping download")
    else:
        if os.path.exists(model_dir):
            log("removing partial dir " + model_dir)
            try:
                shutil.rmtree(model_dir)
            except OSError as e:
                log("FAIL rmtree: " + str(e))
                continue
        log("downloading " + name + "...")
        t0 = time.time()
        try:
            m = gd.load(name)
            elapsed = time.time() - t0
            log("OK " + name + ": vec_size=" + str(m.vector_size)
                + " vocab=" + str(len(m.key_to_index))
                + " elapsed=" + str(round(elapsed, 1)) + "s")
        except Exception as e:
            log("FAIL " + name + ": " + type(e).__name__ + ": " + str(e))
            traceback.print_exc()
            continue
    # Verify shim landed.
    shim = os.path.join(model_dir, "__init__.py")
    if os.path.exists(shim):
        log("OK shim at " + shim)
    else:
        log("WARN shim NOT at " + shim)

log("all-done")
