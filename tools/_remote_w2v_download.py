"""Remote: download word2vec-google-news-300 fresh into data/gensim_cache_v2.

Removes the model subdir first so gensim.downloader.load actually fetches
fresh (it skips download if the dir exists, then tries to import it as a
Python package -- which is exactly Bug 1 from the diagnostic).

~1.7GB download; ~10-30 min depending on bandwidth. Logs to
data/gensim_cache_v2/_download.log and exits 0 on success.

Run on marsh@home via:
  cd C:/dev/hd-instrument
  .venv\\Scripts\\python.exe tools/_remote_w2v_download.py
"""
import os
import shutil
import sys
import time
import traceback

CACHE_DIR = "C:/dev/hd-instrument/data/gensim_cache_v2"
MODEL_NAME = "word2vec-google-news-300"

os.makedirs(CACHE_DIR, exist_ok=True)
LOG = os.path.join(CACHE_DIR, "_download.log")


def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = "[" + ts + "] " + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# Remove the model subdir if it exists empty / partial -- gensim.downloader
# treats any existing dir as "already downloaded" and skips fetching, then
# fails to import a load_data() shim.
model_dir = os.path.join(CACHE_DIR, MODEL_NAME)
if os.path.exists(model_dir):
    gz = os.path.join(model_dir, MODEL_NAME + ".gz")
    if os.path.exists(gz) and os.path.getsize(gz) > 1_000_000_000:
        log("model already present at " + gz + " ("
            + str(os.path.getsize(gz)) + " bytes); skipping download")
    else:
        log("removing partial/empty model dir " + model_dir + " before download")
        try:
            shutil.rmtree(model_dir)
        except OSError as e:
            log("FAIL rmtree: " + str(e))
            sys.exit(2)
log("start; cache_dir=" + CACHE_DIR)

try:
    import gensim.downloader as gd
    gd.BASE_DIR = CACHE_DIR
    gd.base_dir = CACHE_DIR
    log("gd patched; BASE_DIR=" + gd.BASE_DIR)
except Exception:
    traceback.print_exc()
    log("FAIL: gensim import")
    sys.exit(2)

log("calling gd.load('" + MODEL_NAME + "') -- expect ~1.7GB download if not cached...")
t0 = time.time()
try:
    m = gd.load(MODEL_NAME)
    elapsed = time.time() - t0
    log("OK gd.load: vec_size=" + str(m.vector_size)
        + " vocab=" + str(len(m.key_to_index))
        + " elapsed=" + str(round(elapsed, 1)) + "s")
except Exception as e:
    log("FAIL gd.load: " + type(e).__name__ + ": " + str(e))
    traceback.print_exc()
    sys.exit(3)

# Verify .gz + shim landed at expected paths.
gz = os.path.join(CACHE_DIR, MODEL_NAME, MODEL_NAME + ".gz")
shim = os.path.join(CACHE_DIR, MODEL_NAME, "__init__.py")
if os.path.exists(gz):
    log("OK gz at " + gz + " size=" + str(os.path.getsize(gz)))
else:
    log("WARN gz NOT at " + gz)
if os.path.exists(shim):
    log("OK shim at " + shim)
else:
    log("WARN shim NOT at " + shim)

log("done")
sys.exit(0)
