import os
import json
import numpy as np

INDEX_PATH = "data/index/faiss.index"
META_PATH = "data/index/meta.json"

model = None
_index = None
_meta = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def build_index(chunks):
    global _index, _meta
    if not chunks:
        return None
    import faiss
    texts = [c["text"] for c in chunks]
    m = get_model()
    emb = m.encode(texts, normalize_embeddings=True)
    emb = np.array(emb, dtype=np.float32)
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f)
    _index = index
    _meta = chunks
    return index

def retrieve(query, k=4):
    global _index, _meta
    if _index is None or _meta is None:
        if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
            return []
        import faiss
        _index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            _meta = json.load(f)
    if _index.ntotal == 0:
        return []
    m = get_model()
    q_emb = m.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype=np.float32)
    k = min(k, _index.ntotal)
    scores, indices = _index.search(q_emb, k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(_meta):
            item = dict(_meta[idx])
            item["score"] = float(max(0.0, score))
            results.append(item)
    return results
