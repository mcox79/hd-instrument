"""Backend configuration: env vars, paths, model choices."""
from __future__ import annotations
import os
from pathlib import Path


REPO_ROOT = Path(os.environ.get("HD_REPO_ROOT", Path(__file__).resolve().parents[1]))
DATA_DIR = REPO_ROOT / "data"
SUBSTRATE_STATE_DIR = DATA_DIR / "substrate_state"
DEMO_KB_DIR = DATA_DIR / "demo_kb"

# Substrate parameters (production defaults; cycle 187 / 188 locked)
SUBSTRATE_DIM = int(os.environ.get("SUBSTRATE_DIM", "8192"))
SUBSTRATE_RNG_SEED = int(os.environ.get("SUBSTRATE_RNG_SEED", "42"))
SHARDING_STRATEGY = os.environ.get("SHARDING_STRATEGY", "subject")  # subject / relation / hierarchical
CASCADE_CONFIDENCE_THRESHOLD = float(os.environ.get("CASCADE_CONFIDENCE_THRESHOLD", "0.55"))

# LLM config
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

# Backend serving config
HOST = os.environ.get("HD_BACKEND_HOST", "0.0.0.0")
PORT = int(os.environ.get("HD_BACKEND_PORT", "8000"))
CORS_ALLOW_ORIGINS = os.environ.get(
    "HD_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# Tier-5 PATH A model
TIER5_MODEL = os.environ.get("TIER5_MODEL", "EleutherAI/pythia-1.4b")
TIER5_DEVICE = os.environ.get("TIER5_DEVICE", "cuda")
TIER5_DTYPE = os.environ.get("TIER5_DTYPE", "bf16")  # bf16 / fp16 / int8
TIER5_ENABLED = os.environ.get("TIER5_ENABLED", "true").lower() == "true"  # Tier 5 Sprint Panel A on by default
