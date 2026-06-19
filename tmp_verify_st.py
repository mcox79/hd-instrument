import time, sentence_transformers
print(f"sentence-transformers version: {sentence_transformers.__version__}")

# Load MiniLM (per Research's PHASE4A-1 spec: all-MiniLM-L6-v2; 22M params; 384-dim)
print("loading sentence-transformers/all-MiniLM-L6-v2 ...")
t0 = time.time()
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print(f"model loaded in {time.time()-t0:.1f}s")
print(f"  model.get_sentence_embedding_dimension() = {m.get_sentence_embedding_dimension()}")

# Quick encode
texts = ["Substrate cognitive core with certified deletion.", "Frontier LLMs cannot delete facts.", "RSA accumulator provides cryptographic proof."]
t0 = time.time()
emb = m.encode(texts)
print(f"encoded 3 texts in {time.time()-t0:.3f}s; shape={emb.shape} dtype={emb.dtype}")

# Quick GPU check
import torch
print(f"cuda available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  device: {torch.cuda.get_device_name(0)}")
