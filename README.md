# RLM vs LLM Test Repo

This repository compares two ways of solving the same tasks with `gemini-2.5-flash-lite`:

- `llm-test/`: direct Gemini calls through `google.generativeai`
- `rlm-test/`: RLM-driven runs with iteration, REPL access, and optional recursive tool use

All metrics and findings below are taken from the saved markdown logs in this repo. The `.md` files are the source of truth for the numbers in this README.

## Repository Layout

```text
rlm-testing/
├── README.md
├── llm-test/
│   ├── test_llm.py
│   ├── test2_llm.py
│   ├── clinical-llm.py
│   ├── test_launch_note_app.py
│   ├── test_pdf_cersei_warning.py
│   ├── llm-testing-1-parth.md
│   ├── llm-test2.py-parth.md
│   ├── clinical-llm-output.md
│   ├── output for llm long context training.md
│   ├── llm-app-eval.md
│   ├── test_launch_note_app.md
│   ├── test_pdf_cersei_warning.md
│   └── assets/
└── rlm-test/
    ├── test_got.py
    ├── test_long_context_authproxy.py
    ├── test_long_context_clinical_trial.py
    ├── test_launch_note_app.py
    ├── test_pdf_cersei_warning.py
    ├── test1-in-rlms.md
    ├── test2-rlms.md
    ├── test3-rlms.md
    ├── output for long context problem.md
    ├── clincal-rlm-output.md
    ├── test_launch_note_app.md
    ├── test_pdf_cersei_warning.md
    └── assets/
```

Notes:

- `llm-test/llm-app-eval.md` and `llm-test/test_launch_note_app.md` contain the same planning run content.
- The PDF pair is not a perfect token-for-token apples-to-apples comparison:
  the direct LLM path uploads `GOT.pdf`, while the RLM path reads `e72f9f1f181a66887baa7270037c582e.txt`.
- The Cersei/PDF investigation went through multiple harness and runtime changes. The saved `.md` files show important intermediate failures, but they do not represent one single stable final configuration.

## Test Groups

The saved logs cover five task families:

1. Short reasoning: Battle of the Bastards ally identification
2. Long-context retrieval: AuthProxy configuration questions
3. Structured extraction: clinical trial record questions
4. Planning: launch an AI note-taking app in 30 days
5. PDF question answering: Cersei/Ned quote search

## Setup

Install dependencies:

```bash
git clone https://github.com/Abhigyan-Shekhar/rlm-testing.git
cd rlm-testing

pip install google-generativeai python-dotenv rlm
# or
uv pip install google-generativeai python-dotenv rlm
```

Create a `.env` file in the repo root:

```env
GEMINI_API_KEY=your_api_key_here
```

Additional local files expected by the PDF tests:

- `GOT.pdf` in the repo root for `llm-test/test_pdf_cersei_warning.py`
- `e72f9f1f181a66887baa7270037c582e.txt` in the repo root for `rlm-test/test_pdf_cersei_warning.py`

## Run Commands

Direct LLM:

```bash
python llm-test/test_llm.py
python llm-test/test2_llm.py
python llm-test/clinical-llm.py
python llm-test/test_launch_note_app.py
python llm-test/test_pdf_cersei_warning.py
```

RLM:

```bash
uv run python rlm-test/test_got.py
uv run python rlm-test/test_long_context_authproxy.py
uv run python rlm-test/test_long_context_clinical_trial.py
uv run python rlm-test/test_launch_note_app.py
uv run python rlm-test/test_pdf_cersei_warning.py
```

## Recorded Results

### 1. Battle of the Bastards

This is the short reasoning task asking for the main character and the decisive ally.

| Run | Log | Outcome | Time | Token Data |
| --- | --- | --- | --- | --- |
| Direct LLM run 1 | `llm-test/llm-testing-1-parth.md` | Correct: `Jon Snow` / `Sansa Stark` | `1.153s` | `269` total |
| Direct LLM run 2 | `llm-test/llm-test2.py-parth.md` | Correct: `Jon Snow` / `Sansa Stark` | `0.987s` | `270` total |
| RLM run 1 | `rlm-test/test1-in-rlms.md` | Correct: `Main character: Jon Snow`, `Most decisive ally: Sansa Stark` | `6.78s` | `9,650` input / `562` output |
| RLM run 2 | `rlm-test/test2-rlms.md` | Correct answer generated, then reporting crashed | `9.014s` wall / `6.818s` execution | `13,276` input / `920` output |
| RLM run 3 | `rlm-test/test3-rlms.md` | Failed task control: answered an unrelated tennis prompt | `6.416s` wall / `6.163s` execution | `3,777` total |

Findings:

- The direct LLM path solved the short task correctly in about 1 second and about 270 total tokens.
- RLM could reach the right answer, but with much higher latency and token use.
- `test2-rlms.md` shows a post-answer logging failure: `AttributeError: 'str' object has no attribute 'get'`.
- `test3-rlms.md` shows a more serious control failure: the agent produced a polished answer to the wrong task.

### 2. AuthProxy Long-Context Retrieval

This task asks targeted questions from a noisy long document.

| Run | Log | Outcome | Time | Token Data |
| --- | --- | --- | --- | --- |
| Direct LLM | `llm-test/output for llm long context training.md` | Correct on `A1` through `A5` | `1.463s` | `1,512` total |
| RLM | `rlm-test/output for long context problem.md` | Wrong final output: `10` | `13.171s` wall / `13.005s` execution | `11,003` total |

Findings:

- The direct LLM run answered all five questions correctly.
- The RLM run consumed substantially more time and tokens but collapsed to a single wrong value.
- This is a clear case where extra agent machinery did not improve retrieval quality.

### 3. Clinical Long-Context Extraction

This task requires repeated exact fields, an exact sentence, and a step-by-step conclusion.

| Run | Log | Outcome | Time | Token Data |
| --- | --- | --- | --- | --- |
| Direct LLM | `llm-test/clinical-llm-output.md` | Strong result: complete `Q1` through `Q5` | `1.956s` | `2,124` total |
| RLM | `rlm-test/clincal-rlm-output.md` | Partial result: `Q4` is blank, `Q1-Q3` and `Q5` are present | `15.507s` wall / `15.280s` execution | `11,771` total |

Findings:

- The direct LLM run produced the full expected structure.
- The RLM run preserved most of the task but dropped the required sentence extraction for `Q4`.
- The saved RLM log explicitly notes: `Q1 to Q3 are correct, and Q5 is acceptable for this benchmark. Q4 is wrong because it is blank.`

### 4. Launch Note App Planning

This task asks for a structured 30-day launch plan.

| Run | Log | Outcome | Time | Token Data |
| --- | --- | --- | --- | --- |
| Direct LLM | `llm-test/test_launch_note_app.md` | Full multi-week plan with tasks, dependencies, tools, and risks | `8.013s` | `2,144` total |
| Direct LLM duplicate log | `llm-test/llm-app-eval.md` | Same content as `test_launch_note_app.md` | `8.013s` | `2,144` total |
| RLM | `rlm-test/test_launch_note_app.md` | Full multi-week plan with dependencies, risks, and mitigations | `20.671s` wall / `20.383s` execution | `11,216` total |

Findings:

- Both paths produced usable planning outputs in the saved logs.
- The direct LLM path was materially faster and cheaper.
- The RLM output is longer and still serviceable, but the logs do not show a clear quality advantage that justifies the extra runtime.

### 5. PDF Cersei Warning Task

This task asks for a very specific quote and is intentionally strict about source fidelity.

| Run | Log | Outcome | Time | Token Data |
| --- | --- | --- | --- | --- |
| Direct LLM | `llm-test/test_pdf_cersei_warning.md` | Returned `"You are the one she ought to fear," Ned said.` | `36.382s` LLM time, plus `4.264s` upload/processing | `195,109` total |
| RLM | `rlm-test/test_pdf_cersei_warning.md` | Failed final output: `result` | `134.761s` wall / `134.297s` execution | `141,006` total |

Findings:

- The direct LLM answer does not satisfy the task as written: the prompt asks for something Cersei says to Ned, but the saved answer is a Ned quote.
- The direct LLM PDF path is also the most token-expensive run in the repo because the uploaded PDF contributes a very large prompt context.
- The RLM run failed much more severely. The saved log shows repeated looping over a guessed quote, `Quote not found in the file.`, a `NameError: name 'FINAL' is not defined`, and a final emitted answer of `result`.
- This is the clearest catastrophic failure case in the repository.

## Cersei Task Investigation

This section captures what we actually did on the Cersei/Ned quote task beyond the single saved log files.

### Target Question

We were trying to answer one concrete question with RLM:

`There is a brief moment where Cersei says something to Ned that, read carefully, is actually a veiled warning to leave King's Landing. Find it.`

### What We Were Testing

The investigation was not just about one answer. We were testing what RLM can actually do under different setups:

- read a PDF from a file path
- use a helper tool to read a PDF
- read a converted `.txt` file from a path
- answer from full text given as context
- work autonomously vs follow a tightly specified extraction procedure
- use or avoid `llm_query`
- use recursion or not

### What We Tried

#### 1. Direct PDF-path prompt with strict failure mode

- We gave RLM the PDF path and told it to inspect the file.
- It did not actually read the PDF.
- It tried to use `llm_query` on the prompt text instead.
- After tightening the prompt, it returned `FILE_NOT_READ` instead of hallucinating.

Result:

- Honest failure, but no actual PDF traversal.

#### 2. Added a local PDF helper script

- We created `scripts/read_pdf.py`.
- The helper reads the PDF locally using macOS PDFKit via `osascript`.
- We changed the test so RLM had an explicit helper it could call.
- At first, it still ignored the helper and used `llm_query`.
- We then made the helper emit a required marker `__PDF_HELPER_OK__` and changed the test to require that marker.
- After that, RLM finally called the helper, but misparsed the output and still failed.
- We then added `--quote-search` mode to the helper to simplify the output.

Result:

- RLM eventually used the helper and reached the relevant passage family, but still often failed final formatting or instruction compliance.

#### 3. Converted the PDF to plain text

- We created `e72f9f1f181a66887baa7270037c582e.txt`.
- We then pointed RLM at the text file instead of the PDF.
- When asked to read the text file from the path, RLM still behaved badly:
  - it invented quotes
  - it looped
  - or it returned invalid final output

Result:

- Better source format, but still not reliable.

#### 4. Increased iterations

- We raised `max_iterations` from `3` to `5`.

Result:

- More attempts, but the same strategy failures.

#### 5. Found a harness bug

- We discovered that `agent.completion(prompt)` makes `prompt` become `context`.
- That means several earlier runs were reasoning over the instruction block, not the book text.
- We corrected this by loading the text ourselves and calling:

```python
agent.completion(full_text, root_prompt=question)
```

Result:

- The book text was now actually in context.

#### 6. Full text as context, `llm_query` enabled

- With the harness fixed, RLM still frequently took the `llm_query` shortcut.
- It hallucinated multiple quotes not present in the text, including:
  - `We all have our parts to play.`
  - `The king holds you in high esteem. It would be a pity if anything were to happen to you while you are here.`
- We checked the `.txt` file directly and those lines were not present in it.

Result:

- Full text alone is not enough if `llm_query` remains available as an escape hatch.

#### 7. Forced retrieval-only over the text file

- We modified `rlm/environments/local_repl.py` to support disabling query functions.
- We built retrieval tools over the converted text:
  - `rag_search`
  - `find_pages_with_terms`
  - `search_text`
  - `get_page`
  - `get_page_range`
- We also found that bare expression results were not visible in this REPL, so those tools were patched to print automatically.
- With this setup, RLM stayed off `llm_query`, but the retrieval strategy was weak:
  - it spent iterations on wrong pages like `392` and `466`
  - it often ran out of iterations before reaching the target

Result:

- Forced tool use worked mechanically, but autonomous retrieval quality was poor.

#### 8. Full text as context, `llm_query` disabled, no special retrieval tools

- We disabled `llm_query` while keeping the full text in context.
- RLM did not naturally switch to simple Python string operations.
- It kept trying disabled tools and then claimed it could not process the large context.

Result:

- The core problem was strategy selection, not file access.

#### 9. Forced direct Python string processing over context

- We rewrote the prompt to explicitly require:
  - inspect `context` directly
  - use Python string methods
  - avoid query tools
  - assign the result to `final_quote_variable`
  - return `FINAL_VAR(final_quote_variable)`
- At first, it still failed due to case-sensitive search.
- It searched for lowercase `when you play` and missed `When you play`.
- We patched that by forcing case-insensitive search.

Result:

- RLM finally succeeded.
- It used `context.lower()`, found the phrase, sliced the answer from `context`, and returned it via `FINAL_VAR`.

#### 10. Removed the hardcoded anchor again

- After that success, we removed the anchor-based prompt instructions because they over-guided the model.

Result:

- This restored autonomous search over context, but did not re-establish a successful autonomous result.

#### 11. Added recursion controls

- We then added explicit recursion controls in the runtime, not just the prompt.
- `rlm/environments/local_repl.py` now distinguishes:
  - `disable_plain_lm_queries`
  - `disable_recursive_queries`
- `rlm/core/rlm.py` now supports:
  - `max_recursive_calls`
  - shared subcall counting across the tree
- The current test config in `test_pdf_cersei_warning.py` is:
  - full text loaded into context
  - plain `llm_query` disabled
  - recursion allowed
  - total recursive calls capped at `3`
  - `max_depth=3`
  - `max_iterations=5`

Result:

- This latest configuration was prepared, but there is no completed evaluation result yet in the repo after that final runtime change.

### Best Result Achieved So Far

The strongest successful run was the directed extraction run over full context, with `llm_query` disabled, where RLM used Python string operations and returned:

> When you play the game of thrones, you win
> or you die. There is no middle ground.

That is the quote the investigation converged on as the answer.

### What That Result Proves

It proves:

- RLM can operate directly on a huge context string.
- RLM can avoid `llm_query` if forced.
- RLM can execute a concrete extraction procedure in the REPL.

It does not prove:

- RLM can autonomously find the answer from a file path.
- RLM can autonomously perform good RAG in this setup.
- RLM can reliably search long context on its own without prompt scaffolding.

### What We Learned

- A file path alone is not RAG.
- In this setup, RLM does not have a built-in `path -> retrieve -> answer` pipeline.
- When `llm_query` is available, RLM strongly prefers it, and in this investigation that often led to hallucinated answers rather than grounded extraction.
- The harness shape matters. If you want the book text as context and the question separate, you must use:

```python
agent.completion(full_text, root_prompt=question)
```

- RLM is much better at directed execution than autonomous strategy selection.
- Forced helper or retrieval tool use can work mechanically without producing robust retrieval quality.
- Direct Python over `context` can work, but only under strong procedural guidance.

### Current Overall Conclusion

For the Cersei task specifically, the honest bottom line is:

- Autonomous PDF reading from file path: not demonstrated
- Autonomous text-file reading from file path: not reliably demonstrated
- Autonomous search over full context: not yet demonstrated reliably
- Helper or retrieval tool invocation when forced: yes
- Retrieval-only operation when forced: yes, but weak
- Direct Python string extraction over context when explicitly instructed: yes

So far, the evidence is:

- RLM is not robust yet as an autonomous long-context search agent in this setup.
- RLM can be made to succeed when the retrieval and extraction strategy is strongly constrained.

## Cross-Test Findings

### Speed

- The direct LLM path is faster on every logged task in this repository.
- The speed gap is small on simple prompts and large on the heavier RLM runs, especially the PDF task.

### Token Cost

- On the short, long-context, clinical, and planning tasks, the direct LLM path is also much cheaper.
- The main exception is the PDF task: the direct LLM log records `195,109` total tokens because it uploads the full PDF, while the RLM text-based run records `141,006`.
- Even in that exception, the direct LLM path still finishes much sooner.

### Reliability

- The direct LLM path is more reliable overall in the saved benchmarks.
- RLM failure modes in these logs include:
  - task drift to an unrelated prompt
  - post-answer reporting crashes
  - blank required fields in structured output
  - looping and format-control failures that end in unusable answers

### Where RLM Still Helps

- The RLM traces are useful when the goal is debugging agent behavior rather than maximizing benchmark efficiency.
- The saved logs make intermediate reasoning, code execution, and failure points visible in a way the direct LLM logs do not.

## Practical Conclusion

Based on the saved `.md` artifacts in this repo:

- Direct Gemini prompting is the better default for these tasks if the goal is latency, token efficiency, and answer reliability.
- RLM remains useful as an instrumentation-heavy experimental path, especially when you want to inspect how an agent failed.
- The planning task is the closest thing to a neutral result: both paths produce usable output, but the direct LLM path does so with much lower cost.
- The PDF task is the strongest warning case for both approaches: the direct LLM path is fast but returns the wrong speaker, and the RLM path collapses entirely.

## License

This repository is unlicensed and intended for experimentation and comparison work.
