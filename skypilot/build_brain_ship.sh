#!/usr/bin/env bash
# Build WSL-native /root/brain-ship/ bundle for the brain-inspired batch.
# Separate bundle from /root/hd-ship/ (Y+ pipeline) to keep deployments isolated.
#
# Run from inside WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/build_brain_ship.sh
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument
DST=/root/brain-ship

echo "=== [1/4] cleaning ${DST} ==="
if [ -d "${DST}" ]; then
  rm -rf "${DST:?}"
fi
mkdir -p "${DST}/experiments" \
         "${DST}/testbed/llm_integration" \
         "${DST}/testbed/training_monitor" \
         "${DST}/testbed/orchestration" \
         "${DST}/testbed/substrate_lm" \
         "${DST}/skypilot"

echo "=== [2/4] copying experiment scripts (3) + helper ==="
# Pre-flight (substrate single-pass channel-read economy) + Experiment B
# (spectral training monitor on GPT-2-small) + Experiment C (8-channel
# orchestration ablation on GPT-2-small). Experiment A is laptop CPU only;
# not bundled.
for f in \
  exp_substrate_8channel_single_pass_preflight_v1.py \
  exp_substrate_spectral_training_monitor_predictive_v1_gpt2small.py \
  exp_substrate_8channel_orchestration_ablation_gpt2small_v1.py \
  _seed_checkpoint.py
do
  cp "${SRC}/experiments/${f}" "${DST}/experiments/${f}"
done

echo "=== [3/4] copying testbed packages ==="
cp "${SRC}/testbed/__init__.py"                                   "${DST}/testbed/__init__.py"
# api.py: transitively required by testbed/__init__.py (imports AuditReport,
# DeletionCertificate, MemoryBackend, RetrievalResult). 2026-06-04 fix.
cp "${SRC}/testbed/api.py"                                        "${DST}/testbed/api.py"

# llm_integration: substrate_audit has kappa_2/3/4_excess, deletion_cert, hebbian.
cp "${SRC}/testbed/llm_integration/__init__.py"                   "${DST}/testbed/llm_integration/__init__.py"
cp "${SRC}/testbed/llm_integration/substrate_audit.py"            "${DST}/testbed/llm_integration/substrate_audit.py"

# training_monitor: SubstrateObserver for Experiment B
cp "${SRC}/testbed/training_monitor/__init__.py"                  "${DST}/testbed/training_monitor/__init__.py"
cp "${SRC}/testbed/training_monitor/substrate_observer.py"        "${DST}/testbed/training_monitor/substrate_observer.py"

# orchestration: 8-channel architecture for Experiment C
cp "${SRC}/testbed/orchestration/__init__.py"                     "${DST}/testbed/orchestration/__init__.py"
cp "${SRC}/testbed/orchestration/channels.py"                     "${DST}/testbed/orchestration/channels.py"
cp "${SRC}/testbed/orchestration/cipolla.py"                      "${DST}/testbed/orchestration/cipolla.py"
cp "${SRC}/testbed/orchestration/gating.py"                       "${DST}/testbed/orchestration/gating.py"
cp "${SRC}/testbed/orchestration/orchestrator.py"                 "${DST}/testbed/orchestration/orchestrator.py"
cp "${SRC}/testbed/orchestration/pcgrad.py"                       "${DST}/testbed/orchestration/pcgrad.py"

# substrate_lm: primitives.anti_hebbian_contrastive_update for Experiment C's
# Contrastive channel + data.wikitext2_char_corpus loader for Experiment B.
cp "${SRC}/testbed/substrate_lm/__init__.py"                      "${DST}/testbed/substrate_lm/__init__.py"
cp "${SRC}/testbed/substrate_lm/primitives.py"                    "${DST}/testbed/substrate_lm/primitives.py"
cp "${SRC}/testbed/substrate_lm/data.py"                          "${DST}/testbed/substrate_lm/data.py"

cp "${SRC}/skypilot/brain_batch.yaml"                              "${DST}/skypilot/brain_batch.yaml"

echo "=== [4/4] verifying bundle ==="
echo "--- tree ---"
find "${DST}" -type f -printf '%P  %s bytes\n' | sort
echo "--- size ---"
du -sh "${DST}"
echo "--- file count ---"
find "${DST}" -type f | wc -l
echo "OK"
