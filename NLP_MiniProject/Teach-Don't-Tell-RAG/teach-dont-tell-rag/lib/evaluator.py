import numpy as np
from lib.vectorstore import get_model

THRESHOLD_CLOSE = 0.45
THRESHOLD_PARTIAL = 0.25
MAX_ATTEMPTS = 3

def evaluate_attempt(attempt_text, target_text, attempt_num):
    m = get_model()
    embs = m.encode([attempt_text, target_text], normalize_embeddings=True)
    score = float(np.dot(embs[0], embs[1]))
    score = max(0.0, min(1.0, score))

    if score >= THRESHOLD_CLOSE:
        tier = "close"
        passed = True
        level = 3
    elif score >= THRESHOLD_PARTIAL:
        tier = "partial"
        passed = False
        level = min(attempt_num, 2)
    else:
        tier = "far"
        passed = False
        level = min(attempt_num, 2)

    if attempt_num >= MAX_ATTEMPTS and not passed:
        level = 3

    return {"score": round(score, 4), "tier": tier, "level": level, "passed": passed}
