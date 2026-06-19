"""Smoke test: pretokenize_in_parallel handles adversarial Wikipedia-style texts."""
import sys
sys.path.insert(0, "C:/dev/hd-instrument")
from experiments.exp_substrate_cell3_distilled_22M_student_v1 import pretokenize_in_parallel
from transformers import AutoTokenizer

print("Loading Pythia-160m tokenizer for smoke test...")
tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m")

# Adversarial texts simulating Wikipedia hazards
texts = [
    "Hello world.",                                       # baseline
    "Math: \\int_0^\\infty e^{-x^2} dx = \\sqrt{\\pi}/2",  # LaTeX
    "x" * 5000,                                           # very long single text
    "",                                                    # empty
    "test\x00with NULL byte",                            # NULL byte
    "中文测试",                          # Chinese
    "العربية",        # Arabic
    "DNA: " + "ATCG" * 100,                              # repetitive long
    "​​​",                                # zero-width spaces
    "Greek: αβγ = Σ",               # Greek + math
    None,                                                  # this should crash gracefully? no - filter catches None before pretok
]

# Filter None first (matches the actual pipeline filter)
texts = [t for t in texts if t is not None]
print(f"Testing {len(texts)} adversarial texts...")

toks, offs = pretokenize_in_parallel(texts, tok, max_tok=128, num_proc=2, chunk_size=4)
print()
print(f"=== RESULTS ===")
print(f"Total tokens: {len(toks)}; offsets: {len(offs)} (expected {len(texts)+1})")
for i in range(len(texts)):
    n_tok = offs[i+1] - offs[i]
    preview = texts[i][:40].replace("\x00", "\\x00")
    print(f"  [{i}] {n_tok:3d} tokens | {preview}")
print()
print("OK: smoke test passed")
