import os
import time

from dotenv import load_dotenv

from rlm import RLM
from rlm.logger import RLMLogger

load_dotenv()

text_path = os.path.abspath("e72f9f1f181a66887baa7270037c582e.txt")

with open(text_path, encoding="utf-8") as f:
    full_text = f.read()

question = """There is a brief moment where Cersei says something to Ned that, read carefully, is actually a veiled warning to leave King's Landing. Find it.

You must solve this by writing Python code in the REPL that directly inspects the `context` string.
Do not use `llm_query` or `llm_query_batched`.
You may use at most 3 recursive `rlm_query` / `rlm_query_batched` calls total if they help, but they are limited.
Use normal Python string operations on `context` such as `.find()`, slicing, splitting, loops, or regex.
Search the text on your own. Do not assume the wording of the answer in advance.
Derive the answer only from the provided `context`.
You may use Python string operations, loops, splitting, or regex to scan the text for Cersei/Ned dialogue and identify the relevant quote.
The correct answer must be extracted from `context`, not guessed or reconstructed from memory.

Required output procedure:
1. In your first REPL block, compute the exact quote and assign it to a variable named `final_quote_variable`.
2. In your next response, output only `FINAL_VAR(final_quote_variable)`.
3. Do not include any explanation, prose, code fences, or extra text in that final response.
4. If you do not create `final_quote_variable` first, you will fail.

Return only the exact quotation from the text and nothing else."""

print("Waiting 15 seconds for rate limit to cool down...")
time.sleep(15)

logger = RLMLogger()

agent = RLM(
    backend="gemini",
    backend_kwargs={
        "api_key": os.environ["GEMINI_API_KEY"],
        "model_name": "gemini-2.5-flash-lite",
    },
    environment="local",
    environment_kwargs={"disable_plain_lm_queries": True},
    max_depth=3,
    max_recursive_calls=3,
    max_iterations=5,
    verbose=True,
    logger=logger,
)

wall_start = time.perf_counter()
result = agent.completion(full_text, root_prompt=question)
wall_end = time.perf_counter()

print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)
print(result.response)

print("\n" + "=" * 70)
print("LATENCY BREAKDOWN")
print("=" * 70)
print(f"  Total wall time:          {wall_end - wall_start:.3f}s")
print(f"  RLM execution time:       {result.execution_time:.3f}s")
print(
    f"  Overhead (wait/setup):    "
    f"{(wall_end - wall_start) - result.execution_time:.3f}s"
)

if result.metadata:
    total_llm_time = 0.0
    total_code_time = 0.0
    num_iterations = 0

    for i, iteration in enumerate(result.metadata):
        if isinstance(iteration, dict):
            iter_time = iteration.get("iteration_time", 0.0)
            code_blocks = iteration.get("code_blocks", [])
        elif hasattr(iteration, "iteration_time"):
            iter_time = iteration.iteration_time or 0.0
            code_blocks = (
                iteration.code_blocks if hasattr(iteration, "code_blocks") else []
            )
        else:
            continue

        num_iterations += 1
        print(f"\n  -- Iteration {i + 1} ({iter_time:.3f}s total)")

        code_in_iter = 0.0
        for j, block in enumerate(code_blocks):
            if isinstance(block, dict):
                code_time = block.get("result", {}).get("execution_time", 0.0)
                code_preview = block.get("code", "")[:60].replace("\n", " ")
            elif hasattr(block, "result") and block.result:
                code_time = (
                    block.result.execution_time
                    if hasattr(block.result, "execution_time")
                    else 0.0
                )
                code_preview = (block.code or "")[:60].replace("\n", " ")
            else:
                code_time = 0.0
                code_preview = "N/A"

            total_code_time += code_time
            code_in_iter += code_time
            print(f"     Code block {j + 1}:  {code_time:.4f}s  | {code_preview}")

        llm_time = max(iter_time - code_in_iter, 0.0)
        total_llm_time += llm_time
        print(f"     LLM thinking:   {llm_time:.3f}s")

    if num_iterations > 0:
        print(f"\n  {'-' * 40}")
        print("  TOTALS")
        print(f"  {'-' * 40}")
        print(
            f"     Total LLM time:       {total_llm_time:.3f}s  "
            f"({total_llm_time / result.execution_time * 100:.1f}%)"
        )
        print(
            f"     Total code exec:      {total_code_time:.4f}s  "
            f"({total_code_time / result.execution_time * 100:.1f}%)"
        )
        print(f"     Iterations:           {num_iterations}")
        print(
            f"     Avg per iteration:    "
            f"{result.execution_time / num_iterations:.3f}s"
        )

print("\n" + "=" * 70)
print("TOKEN USAGE")
print("=" * 70)
if result.usage_summary:
    usage = result.usage_summary.to_dict()
    total_input = 0
    total_output = 0

    for model_name, model_usage in usage.get("model_usage_summaries", {}).items():
        input_tokens = model_usage.get("total_input_tokens", 0)
        output_tokens = model_usage.get("total_output_tokens", 0)
        total_input += input_tokens
        total_output += output_tokens

        print(f"  Model: {model_name}")
        print(f"    Input tokens:    {input_tokens:,}")
        print(f"    Output tokens:   {output_tokens:,}")
        print(f"    Total tokens:    {input_tokens + output_tokens:,}")
        print(f"    API calls:       {model_usage.get('num_calls', 0)}")
        cost = model_usage.get("total_cost")
        if cost:
            print(f"    Cost:            ${cost:.6f}")

    if total_output > 0:
        print(f"\n  {'-' * 40}")
        print("  THROUGHPUT")
        print(f"  {'-' * 40}")
        print(
            f"     Output tokens/sec:    "
            f"{total_output / result.execution_time:.1f} tok/s"
        )
        print(
            f"     ms per output token:  "
            f"{(result.execution_time / total_output) * 1000:.1f} ms/tok"
        )
        print(
            f"     Total tokens/sec:     "
            f"{(total_input + total_output) / result.execution_time:.1f} tok/s"
        )

print("=" * 70)
