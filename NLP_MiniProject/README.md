# Teach Don't Tell RAG

A Socratic tutoring app that uses RAG to guide students toward understanding instead of handing them answers.

## How It Works

1. **Upload documents** — drop `.txt`, `.md`, or `.pdf` files into the sidebar
2. **Build the index** — click "Build Index" to embed and index all corpus documents
3. **Ask a question** — type a topic and hit "Start Question"
4. **Think first** — a thinking gate countdown gives you time to read the hint before answering
5. **Submit attempts** — type your understanding, rate your confidence, and get progressively more specific hints
6. **Review** — expand the Session Evaluation Report to see your performance

## Escalation Ladder

| Level | What You Get |
|-------|-------------|
| 0 🟢 | Open guiding question |
| 1 🟡 | Narrower, more focused question |
| 2 🟠 | Gentle nudge with partial paraphrase |
| 3 🔴 | Full answer revealed |

The system escalates based on how close your attempts are to the source material and how many tries you've taken. Say "just tell me" or "I give up" to skip to the full answer.

## Setup

```bash
pip install -r requirements.txt
```

Set your API key for LLM responses:
```bash
set OPENROUTER_API_KEY=your-key-here
```

## Run

```bash
python -m streamlit run app.py
```

## Project Structure

```
app.py              — Streamlit UI
lib/
  ingestion.py      — Document loading and chunking
  vectorstore.py    — FAISS index with sentence-transformers
  evaluator.py      — Cosine similarity scoring and escalation
  socratic.py       — LLM prompt generation via OpenRouter
  state.py          — Session state management
  report.py         — Evaluation report rendering
data/
  corpus/           — Drop your documents here
  index/            — Auto-generated FAISS index
```
