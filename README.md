# 🧪 RLM Testing

A benchmark and comparison suite for evaluating **RLM (Recursive Language Model)** against standard direct LLM calls (Gemini API). This repository documents hands-on experiments measuring answer quality, latency, token usage, and iterative reasoning behavior.

---

## 📖 What is RLM?

**RLM (Recursive Language Model)** is an agentic framework that wraps an LLM with a code execution loop. Instead of answering in a single pass, RLM allows the model to:

- Inspect and manipulate context programmatically via a Python REPL
- Make recursive sub-calls to itself via `llm_query()`
- Iterate across multiple reasoning steps before committing to a final answer
- Track token usage, latency, and execution metadata across all iterations

This repo tests RLM against a plain Gemini API baseline on the same prompts, to understand the trade-offs.

---

## 🗂️ Repository Structure

```
rlm-testing/
├── test_llm.py              # Baseline: direct Gemini API call (no RLM)
├── test2_llm.py             # Extended baseline with additional test cases
├── test_got.py              # RLM agent test using the same Game of Thrones prompt
├── test1-in-rlms.md         # RLM run output — Test 1 (depth=1, max_iter=3)
├── test2-rlms.md            # RLM run output — Test 2 (depth=1, max_iter=3, with traceback)
├── test3-rlms.md            # RLM run output — Test 3
├── llm-testing-1-parth.md   # Baseline LLM test log — Parth's run 1
└── llm-test2.py-parth.md    # Baseline LLM test log — Parth's run 2
```

---

## 🔬 Test Setup

### Prompt Used

All tests use the same context and question — a reasoning challenge based on the **Battle of the Bastards** (Game of Thrones):

> **Question:** Who was the central ally of the main character in the Battle of the Bastards?

The context is intentionally crafted to require multi-hop reasoning: the decisive ally (Sansa Stark) is not physically present on the battlefield, making it a non-trivial retrieval task.

### Models

| Component | Value |
|-----------|-------|
| LLM Backend | `gemini-2.5-flash-lite` |
| API | Google Generative AI (`google.generativeai`) |
| RLM Environment | `local` |
| RLM Max Depth | 1 |
| RLM Max Iterations | 3 |

---

## 📊 Results Summary

### Baseline (Direct Gemini API — `test_llm.py`)

| Metric | Value |
|--------|-------|
| Total Time | ~2–3s |
| Input Tokens | ~250 |
| Output Tokens | ~30–50 |
| Answer | Direct, single-shot |

### RLM Agent (`test_got.py`)

| Metric | Value |
|--------|-------|
| Total Time | ~6.8s |
| Input Tokens | ~9,650 – 13,276 |
| Output Tokens | ~562 – 920 |
| Iterations | 3 |
| Sub-calls (`llm_query`) | 1 |
| Answer | Correct — Jon Snow / Sansa Stark |

### Key Observations

- **Accuracy:** Both approaches produce the correct answer, but RLM reasons through it explicitly across iterations.
- **Cost:** RLM uses significantly more tokens (~40–50× more input tokens) due to context carry-through and iterative prompting.
- **Latency:** RLM is slower (~6–9s wall time vs ~2–3s), with most overhead from LLM thinking across iterations rather than code execution.
- **Transparency:** RLM exposes its reasoning chain, making it auditable — you can trace exactly how and why it arrived at an answer.
- **Sub-call behavior:** In Test 1, RLM used `llm_query()` to delegate synthesis. In Test 2, it was instructed not to — and still reasoned correctly via direct Python analysis.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- A valid Gemini API key
- The `rlm` Python package (for agent tests)

### Installation

```bash
# Clone the repo
git clone https://github.com/Abhigyan-Shekhar/rlm-testing.git
cd rlm-testing

# Install dependencies
pip install google-generativeai python-dotenv rlm
# or with uv:
uv pip install google-generativeai python-dotenv rlm
```

### Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### Running Tests

```bash
# Run the baseline (direct Gemini API)
python test_llm.py

# Run the RLM agent
uv run python test_got.py
```

> **Note:** A 15-second cooldown is built into each script to avoid Gemini API rate limits.

---

## 📋 Output Format

Each run prints a structured report:

```
🎬 ANSWER
══════════════════════
<model response>

⏱️  LATENCY
══════════════════════
Total time: X.XXXs

📊 TOKEN USAGE
══════════════════════
Input tokens:   X,XXX
Output tokens:  XXX
Total tokens:   X,XXX
⚡ Tokens/sec:  XX.X tok/s
```

RLM additionally prints a full iteration trace with per-iteration timing, sub-call logs, and a final answer panel.

---

## 🤝 Contributing

This is an experimental research/testing repo. Feel free to open issues or PRs to add new test cases, models, or metrics.

---

## 📄 License

This repository is unlicensed — use freely for research and experimentation.
