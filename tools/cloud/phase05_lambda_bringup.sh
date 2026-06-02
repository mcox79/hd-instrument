#!/usr/bin/env bash
# Phase 0.5 + 0.5b Lambda bring-up.
# Runs ONCE per Lambda instance bootstrap (single bootstrap per
# feedback_batch_cloud_experiments). Idempotent: re-running is safe.
#
# Required env vars:
#   HF_TOKEN  -- HuggingFace API token with Llama-3.1-8B-Instruct gated access
#
# Optional env vars:
#   HD_REPO_PATH -- defaults to /home/ubuntu/hd-instrument
#   HD_VENV_PATH -- defaults to $HD_REPO_PATH/.venv
#   HYPERPROBE_PATH -- defaults to /home/ubuntu/hyperprobe
#
# Per feedback-always-verbose-remote-dispatch: set -ex + tee.
set -ex

REPO=${HD_REPO_PATH:-/home/ubuntu/hd-instrument}
VENV=${HD_VENV_PATH:-$REPO/.venv}
HP=${HYPERPROBE_PATH:-/home/ubuntu/hyperprobe}

if [ -z "${HF_TOKEN:-}" ]; then
    echo "[ERROR] HF_TOKEN env var must be set before bring-up."
    exit 1
fi

# 1. Ensure venv exists + activated
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"

# 2. Upgrade pip + install hd-instrument cloud requirements
pip install -q --upgrade pip
pip install -q -r "$REPO/requirements_cloud.txt"

# 3. Install vLLM (Llama-3.1-8B serving). Pin to a working version per
#    Sep 2025 release notes; flash-attn is bundled.
pip install -q "vllm>=0.6,<0.7"

# 4. Install transformers + datasets + huggingface_hub at versions compatible
#    with both vLLM and the hyperprobe repo.
pip install -q "transformers>=4.45" "datasets>=2.19" "huggingface_hub>=0.25" \
              "accelerate>=0.30"

# 5. Clone Ipazia-AI/hyperprobe + pip install -e .
if [ ! -d "$HP" ]; then
    git clone https://github.com/Ipazia-AI/hyperprobe.git "$HP"
fi
cd "$HP"
git pull --ff-only || true
pip install -q -e .

# 5.5. Belt-and-suspenders: install transitive deps that hyperprobe's
# pyproject.toml + requirements.txt BOTH miss but src/hyperprobe/ imports at
# load time. Discovered via Dispatch 2 (word2number) + Dispatch 3
# (sentence-transformers) + grep of all imports in src/hyperprobe/*.
# tensorflow-datasets is omitted -- heavy install; bring-up smoke at step 5.6
# will surface it if hyperprobe's __init__ chain actually needs it.
# No version pins -- these are research-package transitive deps; pip resolves
# whatever's compatible with installed torch/transformers. Pin torchhd>=5.7 was
# wrong on Dispatch 4 (torchhd PyPI versions don't extend to 5.x). Strategy:
# install bare names, let pip resolve, and let the import smoke at 5.6 catch
# any version-incompatibility at import time.
pip install -q \
  word2number \
  sentence-transformers \
  wn \
  spacy \
  SPARQLWrapper \
  requests-cache \
  python-dotenv \
  torch-hd

# 5.6. Post-install hyperprobe import smoke. If hyperprobe can't import,
# stop here -- every downstream anchor will fail with the same error.
python -c "
import hyperprobe
print(f'OK: hyperprobe imported (module path: {hyperprobe.__file__})')
# Touch the high-level APIs used by Phase 0.5
for fn in ['create_codebook', 'ingest_embeddings', 'create_vsa_encodings',
           'inputDataset', 'llm2VSA_dataloader', 'train_hyperprobe',
           'VSAEncoder', 'load_llm', 'probe_doc']:
    assert hasattr(hyperprobe, fn), f'hyperprobe missing {fn}'
print('OK: all required hyperprobe APIs present')
"

# 5.7. End-to-end VSA-encoding smoke. Catches hyperprobe-internal API bugs
# (shape mismatches, missing concepts) on toy data BEFORE cloud burns the
# 5000-doc Llama-3.1-8B activation collection. Mirrors the no-overlap
# constraint our anchor scripts use.
python -c "
import hyperprobe
inputs = [
  {'doc': 'Denmark : krone = Mexico : peso',
   'concepts': [('Denmark','krone'), ('Mexico', 'peso')]},
  {'doc': 'Berlin : Germany = Tokyo : Japan',
   'concepts': [('Berlin', 'Germany'), ('Tokyo', 'Japan')]},
  {'doc': 'introvert : extravert = big : small',
   'concepts': [('introvert', 'extravert'), ('big', 'small')]},
]
all_concepts = set(c for it in inputs for p in it['concepts'] for c in p)
cb = hyperprobe.create_codebook(concepts=list(all_concepts), vsa_dimension=128)
for item in inputs:
    vsa = hyperprobe.create_vsa_encodings(item, cb)
    assert hasattr(vsa, 'shape'), f'VSA encoding has no shape: {vsa!r}'
    assert vsa.shape[-1] == 128, f'expected dim 128, got {vsa.shape}'
print(f'OK: hyperprobe create_vsa_encodings end-to-end smoke (3 inputs, D=128)')
"
cd "$REPO"

# 6. HuggingFace login (this enables both downloads + dataset auth)
python -c "from huggingface_hub import login; import os; login(token=os.environ['HF_TOKEN'], add_to_git_credential=False)"

# 7. Verify Llama-3.1-8B-Instruct access (read-only probe; doesn't download yet)
python -c "
from huggingface_hub import HfApi
info = HfApi().model_info('meta-llama/Llama-3.1-8B-Instruct', token='${HF_TOKEN}')
print(f'OK: Llama-3.1-8B-Instruct accessible (last_modified={info.last_modified})')
"

# 8. Pre-pull Llama-3.1-8B-Instruct (saves wall-time on first probe-training step)
#    This is ~16 GB; idempotent if already cached.
python -c "
from huggingface_hub import snapshot_download
import os
snapshot_download(
    repo_id='meta-llama/Llama-3.1-8B-Instruct',
    token=os.environ['HF_TOKEN'],
    cache_dir=os.environ.get('HF_HOME', os.path.expanduser('~/.cache/huggingface')),
    allow_patterns=['*.safetensors', '*.json', 'tokenizer*', '*.model'],
)
print('OK: Llama-3.1-8B-Instruct snapshot ready')
"

# 9. Sanity GPU check
python -c "
import torch
print(f'CUDA: {torch.cuda.is_available()}; device count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'  GPU 0: {torch.cuda.get_device_name(0)} '
          f'(VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB)')
"

echo "[bring-up] Phase 0.5 + 0.5b Lambda environment ready."
echo "  Repo:        $REPO"
echo "  Venv:        $VENV"
echo "  Hyperprobe:  $HP"
echo "  Llama-3.1:   cached"
echo "  Next:        launch_batch.py with phase05_combined_llama31.json"
