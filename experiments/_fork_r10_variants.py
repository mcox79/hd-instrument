"""One-shot helper: fork r10_best_config_multiseed.py into K-level variants."""
from pathlib import Path

base = Path("experiments/exp_wave14b_r10_best_config_multiseed.py").read_text()

variants = {
    "r10_best_config_K2_K4_K8": [
        ("K_LEVELS = [128, 256]", "K_LEVELS = [2, 4, 8]"),
        ("r10_best_config_multiseed", "r10_best_config_K2_K4_K8"),
    ],
    "r10_best_config_K64_verify": [
        ("K_LEVELS = [128, 256]", "K_LEVELS = [64]"),
        ("r10_best_config_multiseed", "r10_best_config_K64_verify"),
    ],
    "r10_best_config_K512": [
        ("K_LEVELS = [128, 256]", "K_LEVELS = [512]"),
        ("r10_best_config_multiseed", "r10_best_config_K512"),
    ],
}
for name, subs in variants.items():
    content = base
    for old, new in subs:
        content = content.replace(old, new)
    p = Path(f"experiments/exp_wave14b_{name}.py")
    p.write_text(content)
    print(f"wrote {p.name} ({len(content)} bytes)")
