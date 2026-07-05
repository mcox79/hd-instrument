"""Build BOTH content caches for the TEM cell over the SAME 4-relation entity set
(AtLocation, CausesDesire, CapableOf, DerivedFrom). Consistent entities across bge + gsbc.
  bge_small_schema_TEM_entities_v1.npz  {entities, emb(float16 384d)}
  gsbc_expand2x_schema_TEM_entities_v1.npz {entities, code(float32 8192d sparse)}
ASCII-only."""
import os, sys, json, time, collections
import numpy as np
from pathlib import Path

REPO = Path("d:/AI/hd-instrument")
DATASET = REPO / "data/datasets/conceptnet5_en_100k.jsonl"
BGE_OUT = REPO / "data/datasets/bge_small_schema_TEM_entities_v1.npz"
GSBC_OUT = REPO / "data/datasets/gsbc_expand2x_schema_TEM_entities_v1.npz"
CKPT = REPO / "data/substrate_concept_encoder_v12_gwta_seed7/_ckpt_best_GSBC_EXPAND2X.pt"
RELATIONS = ["AtLocation", "CausesDesire", "CapableOf", "DerivedFrom"]
V = 100
K_ACTIVE = 192
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")

def rel_entities(rel):
    objc = collections.Counter(); pairs = []
    with open(DATASET, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("predicate") != rel: continue
            s, o = d.get("subject"), d.get("object")
            if s is None or o is None or s == o: continue
            pairs.append((str(s), str(o))); objc[str(o)] += 1
    cb = set(o for o, _ in objc.most_common(V))
    subj = {s for s, o in pairs if o in cb}
    return subj | cb

def main():
    t0 = time.time()
    ents = set()
    for rel in RELATIONS:
        e = rel_entities(rel); ents |= e
        print(f"[enum] {rel}: {len(e)}", flush=True)
    ents = sorted(ents)
    print(f"[enum] TOTAL {len(ents)} entities", flush=True)
    texts = [e.replace("_", " ") for e in ents]

    from sentence_transformers import SentenceTransformer
    # bge-small
    print("[bge-small] loading BAAI/bge-small-en-v1.5 ...", flush=True)
    m_s = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    emb_s = m_s.encode(texts, batch_size=256, normalize_embeddings=True,
                       show_progress_bar=True, convert_to_numpy=True).astype(np.float16)
    np.savez_compressed(BGE_OUT, entities=np.array(ents, dtype=object), emb=emb_s,
                        model="BAAI/bge-small-en-v1.5", dim=emb_s.shape[1])
    print(f"[bge-small] saved {BGE_OUT} {emb_s.shape} ({BGE_OUT.stat().st_size/1e6:.1f}MB) "
          f"t={time.time()-t0:.1f}s", flush=True)

    # bge-large -> gsbc student
    import torch
    print("[bge-large] loading BAAI/bge-large-en-v1.5 ...", flush=True)
    m_l = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
    emb_l = m_l.encode(texts, batch_size=128, normalize_embeddings=True,
                       show_progress_bar=True, convert_to_numpy=True).astype(np.float32)
    assert emb_l.shape[1] == 1024
    ck = torch.load(str(CKPT), map_location="cpu"); sd = ck["student"]
    W0 = sd["net.0.weight"].numpy(); b0 = sd["net.0.bias"].numpy()
    W2 = sd["net.2.weight"].numpy()
    b2 = sd["net.2.bias"].numpy() if "net.2.bias" in sd else np.zeros(W2.shape[0], np.float32)
    H = np.maximum(0.0, emb_l @ W0.T + b0[None, :]); Z = H @ W2.T + b2[None, :]
    mag = np.abs(Z); idx = np.argpartition(-mag, K_ACTIVE, axis=1)[:, :K_ACTIVE]
    code = np.zeros_like(Z, dtype=np.float32)
    rows = np.arange(Z.shape[0])[:, None]; code[rows, idx] = Z[rows, idx].astype(np.float32)
    np.savez_compressed(GSBC_OUT, entities=np.array(ents, dtype=object), code=code.astype(np.float32),
                        out_dim=8192, k_active=K_ACTIVE,
                        provenance="bge-large-en-v1.5 -> GSBC_EXPAND2X student v12 seed7 -> global top-192")
    print(f"[gsbc] saved {GSBC_OUT} {code.shape} ({GSBC_OUT.stat().st_size/1e6:.1f}MB) "
          f"t={time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback; print(f"[FAILED] {type(e).__name__}: {e}", flush=True); traceback.print_exc(); sys.exit(3)
