import os

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

def read_pdf(path):
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(path)
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""

def load_corpus(folder="data/corpus"):
    chunks = []
    if not os.path.exists(folder):
        return chunks

    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue

        text = ""
        if name.endswith((".txt", ".md")):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif name.endswith(".pdf"):
            text = read_pdf(path)

        if not text.strip():
            continue

        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        curr = []
        curr_len = 0
        cid = 0

        for p in paras:
            words = p.split()
            if not words:
                continue
            if curr_len + len(words) > CHUNK_SIZE and curr:
                chunks.append({"text": " ".join(curr), "source": name, "chunk_id": f"{name}_{cid}", "pos": cid})
                cid += 1
                if CHUNK_OVERLAP > 0 and len(curr) > CHUNK_OVERLAP:
                    curr = curr[-CHUNK_OVERLAP:]
                    curr_len = len(curr)
                else:
                    curr = []
                    curr_len = 0
            while len(words) > CHUNK_SIZE:
                part = words[:CHUNK_SIZE]
                chunks.append({"text": " ".join(part), "source": name, "chunk_id": f"{name}_{cid}", "pos": cid})
                cid += 1
                words = words[CHUNK_SIZE - CHUNK_OVERLAP:]
            curr.extend(words)
            curr_len += len(words)

        if curr:
            chunks.append({"text": " ".join(curr), "source": name, "chunk_id": f"{name}_{cid}", "pos": cid})

    return chunks
