# 🧪 RLM vs LLM Test Repo

This repository compares two ways of solving the same tasks with `gemini-2.5-flash-lite`:

- `llm-test/`: direct Gemini calls with no recursive agent loop
- `rlm-test/`: RLM-based runs with iteration, REPL access, and optional `llm_query()` sub-calls

The repo was also refactored so the code, markdown logs, and screenshots are split by execution style instead of being mixed at the root.

---

## 📦 Repository Layout

```text
rlm-testing/
├── README.md
├── llm-test/
│   ├── test_llm.py
│   ├── test2_llm.py
│   ├── clinical-llm.py
│   ├── llm-test for long context problem - same as rlm , just modified for llm
│   ├── llm-testing-1-parth.md
│   ├── llm-test2.py-parth.md
│   ├── output for llm long context training.md
│   ├── clinical-llm-output.md
│   └── assets/
└── rlm-test/
    ├── test_got.py
    ├── test_long_context_authproxy.py
    ├── test_long_context_clinical_trial.py
    ├── test1-in-rlms.md
    ├── test2-rlms.md
    ├── test3-rlms.md
    ├── output for long context problem.md
    ├── clincal-rlm-output.md
    └── assets/
```

---

## 🔍 What We Did

The repo contains three experiment groups:

1. Short reasoning task based on the Battle of the Bastards.
2. Long-context retrieval task around an AuthProxy configuration document.
3. Long-context clinical extraction task with structured answers.

For each group, the saved outputs show:

- latency
- token usage
- final answer quality
- where relevant, RLM iteration behavior and failure modes

---

## ⚙️ Setup

### Model

| Component | Value |
|-----------|-------|
| Base model | `gemini-2.5-flash-lite` |
| Direct LLM path | `google.generativeai` |
| RLM path | `rlm` with local environment |
| RLM max depth | `1` |
| RLM max iterations | `3` |

### Install

```bash
git clone https://github.com/Abhigyan-Shekhar/rlm-testing.git
cd rlm-testing

pip install google-generativeai python-dotenv rlm
# or
uv pip install google-generativeai python-dotenv rlm
```

Create `.env` in the repo root:

```env
GEMINI_API_KEY=your_api_key_here
```

### Run

```bash
# Direct LLM
python llm-test/test_llm.py
python llm-test/test2_llm.py
python llm-test/clinical-llm.py

# RLM
uv run python rlm-test/test_got.py
uv run python rlm-test/test_long_context_authproxy.py
uv run python rlm-test/test_long_context_clinical_trial.py
```

---

## 📊 Recorded Results

### 1. Battle Of The Bastards

This is the short reasoning task asking for the main character and the decisive ally.

| Run | Path | Result | Time | Tokens |
|-----|------|--------|------|--------|
| Direct LLM run 1 | `llm-test/llm-testing-1-parth.md` | Correct: `Jon Snow` / `Sansa Stark` | `1.153s` | `269` total |
| Direct LLM run 2 | `llm-test/llm-test2.py-parth.md` | Correct: `Jon Snow` / `Sansa Stark` | `0.987s` | `270` total |
| RLM test 1 | `rlm-test/test1-in-rlms.md` | Correct: `Jon Snow` / `Sansa Stark` | `6.78s` | `9,650` input / `562` output |
| RLM test 2 | `rlm-test/test2-rlms.md` | Correct answer, but reporting crashed afterward | `9.014s` wall / `6.818s` execution | not fully emitted in final block |
| RLM test 3 | `rlm-test/test3-rlms.md` | Behavioral failure case: answered a different tennis summary task | `6.416s` wall / `6.163s` execution | `3,777` total |

What the outputs show:

- The direct LLM handled the short reasoning task correctly in about 1 second with about 270 total tokens.
- RLM also reached the correct answer in the clean runs, but needed about 6 to 9 seconds and far more tokens.
- `test2-rlms.md` shows an implementation fragility in the reporting code:
  `AttributeError: 'str' object has no attribute 'get'`
- `test3-rlms.md` is useful as a failure example: the agent produced a polished answer, but not for the intended task.

### 2. AuthProxy Long-Context Task

This task asks targeted retrieval questions from a noisy long document.

| Run | Path | Result | Time | Tokens |
|-----|------|--------|------|--------|
| Direct LLM | `llm-test/output for llm long context training.md` | Correct on A1-A5 | `1.463s` | `1,512` total |
| RLM | `rlm-test/output for long context problem.md` | Incorrect final output: only `10` | `13.171s` wall / `13.005s` execution | `11,003` total |

What the outputs show:

- The direct LLM answered all five questions correctly.
- The RLM run consumed about 7.3x more total tokens and about 9x more time.
- Despite the extra reasoning overhead, the RLM final answer collapsed to a single wrong value.

### 3. Clinical Long-Context Task

This task extracts repeated flags plus a sentence-level explanation and a step-by-step conclusion.

| Run | Path | Result | Time | Tokens |
|-----|------|--------|------|--------|
| Direct LLM | `llm-test/clinical-llm-output.md` | Strong result: Q1-Q5 complete | `1.956s` | `2,124` total |
| RLM | `rlm-test/clincal-rlm-output.md` | Partial result: Q4 missing, Q5 present | `15.507s` wall / `15.280s` execution | `11,771` total |

What the outputs show:

- The direct LLM produced the full structured answer.
- The RLM run got the repeated classification answers and the stepwise synthesis, but dropped Q4 entirely.
- RLM used about 5.5x more total tokens and about 8x more wall time for a worse final result.

---

## 🧠 Conclusions

### Main Takeaways

- For the saved tasks in this repo, direct LLM prompting is consistently faster and cheaper.
- On the long-context tasks, the direct LLM is not just cheaper, it is also more reliable.
- RLM can produce transparent traces, but that traceability does not guarantee better task performance.

### When RLM Helped

- In the short Game of Thrones task, RLM made its reasoning path visible and still reached the correct answer.
- That makes RLM useful when debugging agent behavior matters more than raw efficiency.

### Where RLM Broke Down

- On the AuthProxy task, RLM spent significant compute and still returned the wrong final answer.
- On the clinical task, RLM produced a partial structured output and dropped one required field.
- One saved run also failed in its own metrics-reporting code after generating the answer.
- Another saved run answered a completely different task, showing that iterative pipelines can drift if the prompt or intermediate state is not tightly controlled.

### Practical Conclusion

- If the goal is benchmark efficiency and answer quality on these prompts, the direct Gemini path wins.
- If the goal is inspecting agent reasoning or experimenting with recursive workflows, the RLM runs are still useful as instrumentation-heavy examples, but they should be treated as experimental and brittle.

---

## 🖼️ Saved Screenshots

### `rlm-test/test3-rlms.md`

![Test 3 - Iteration View](rlm-test/assets/test3-rlms/test3-iteration-view.png)
![Test 3 - Code Execution + Sub-call](rlm-test/assets/test3-rlms/test3-code-execution-subcall.png)
![Test 3 - Final Answer + Metrics (1)](rlm-test/assets/test3-rlms/test3-final-answer-metrics-1.png)
![Test 3 - Final Answer + Metrics (2)](rlm-test/assets/test3-rlms/test3-final-answer-metrics-2.png)
![Test 3 - Script Setup (Part 1)](rlm-test/assets/test3-rlms/test3-script-setup-1.png)
![Test 3 - Script Setup (Part 2)](rlm-test/assets/test3-rlms/test3-script-setup-2.png)
![Test 3 - Run Start + Iteration 1](rlm-test/assets/test3-rlms/test3-run-start-iteration-1.png)
![Test 3 - Iteration 2 Analysis](rlm-test/assets/test3-rlms/test3-iteration-2-analysis.png)
![Test 3 - Iteration 3 + Final Panel](rlm-test/assets/test3-rlms/test3-iteration-3-final-panel.png)
![Test 3 - Final Output + Traceback](rlm-test/assets/test3-rlms/test3-traceback-snapshot.png)

### `llm-test/llm-test2.py-parth.md`

![Baseline - llm-test2.py-parth output](llm-test/assets/llm-test2/llm-test2-parth-output.png)

### `llm-test/llm-testing-1-parth.md`

![Baseline - llm-testing-1-parth output](llm-test/assets/llm-test1/llm-testing-1-parth-output.png)

### `rlm-test/test_long_context_authproxy.py`

![Long Context - test_long_context_authproxy output](rlm-test/assets/test-long-context-authproxy/test-long-context-authproxy-output.png)

### `llm-test/output for llm long context training.md`

![LLM Long Context - training output](llm-test/assets/output-llm-long-context-training/output-llm-long-context-training.png)

### `rlm-test/test_long_context_clinical_trial.py`

![Long Context - test_long_context_clinical_trial output](rlm-test/assets/test-long-context-clinical-trial/test-long-context-clinical-trial-output.png)

### `llm-test/clinical-llm.py`

![Clinical LLM - clinical-llm.py output](llm-test/assets/clinical-llm/clinical-llm-output.png)

---

## 📄 License

This repository is unlicensed and intended for experimentation and comparison work.
