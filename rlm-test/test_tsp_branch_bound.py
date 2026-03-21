import os
import time

from dotenv import load_dotenv

from rlm import RLM
from rlm.clients import get_client
from rlm.logger import RLMLogger

load_dotenv()

prompt = """You are solving a Traveling Salesman Problem with 8 cities.

Cities: A, B, C, D, E, F, G, H

Distance matrix is symmetric and satisfies triangle inequality.

Task:
- Find the optimal tour
- You MUST use a branch-and-bound or systematic search strategy

Solve the Traveling Salesman Problem below.

IMPORTANT:
You must NOT compute all permutations directly.
Instead:
- Use logical reasoning to eliminate impossible or suboptimal paths early
- Justify every pruning decision

STRICT REQUIREMENTS:
- Maintain a table of explored paths
- Track current best solution (upper bound)
- Prune paths that exceed current best
- Show recursive exploration clearly

After giving the answer, explain:
"Why is this solution guaranteed optimal?"

Output format:
1. Exploration steps
2. Pruned branches with reasons
3. Final optimal path and cost
"""

expected_result = (
    "The problem is under-specified. No optimal tour can be determined because "
    "the actual distance matrix values are missing."
)

print("Waiting 15 seconds for rate limit to cool down...")
time.sleep(15)

backend_kwargs = {
    "api_key": os.environ["GEMINI_API_KEY"],
    "model_name": "gemini-2.5-flash",
}

print("\n" + "=" * 70)
print("EXPECTED CORRECT RESULT")
print("=" * 70)
print(expected_result)

print("\n" + "=" * 70)
print("BASELINE LLM")
print("=" * 70)

baseline_client = get_client("gemini", backend_kwargs.copy())
llm_start = time.perf_counter()
llm_response = baseline_client.completion(prompt)
llm_end = time.perf_counter()

print(llm_response)
print("\n" + "-" * 40)
print(f"Baseline wall time: {llm_end - llm_start:.3f}s")

llm_usage = baseline_client.get_usage_summary().to_dict()
for model_name, model_usage in llm_usage.get("model_usage_summaries", {}).items():
    print(
        f"{model_name}: input={model_usage.get('total_input_tokens', 0):,}, "
        f"output={model_usage.get('total_output_tokens', 0):,}, "
        f"calls={model_usage.get('total_calls', 0)}"
    )

print("\n" + "=" * 70)
print("RLM")
print("=" * 70)

logger = RLMLogger()

agent = RLM(
    backend="gemini",
    backend_kwargs=backend_kwargs.copy(),
    environment="local",
    environment_kwargs={"disable_plain_lm_queries": True},
    max_depth=3,
    max_recursive_calls=3,
    max_iterations=6,
    verbose=True,
    logger=logger,
)

wall_start = time.perf_counter()
result = agent.completion(prompt)
wall_end = time.perf_counter()

print("\n" + "=" * 70)
print("RLM ANSWER")
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
