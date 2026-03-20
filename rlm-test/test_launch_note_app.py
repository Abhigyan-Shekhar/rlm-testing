import os
import time

from dotenv import load_dotenv

from rlm import RLM
from rlm.logger import RLMLogger

load_dotenv()

context = """
Goal: Launch a new AI-powered note-taking app in 30 days.

Constraints:
- Budget: $10,000
- Team: 3 engineers, 1 designer
- Target users: college students

Tasks:
1. Break this goal into a detailed execution plan
2. Decompose into weekly milestones
3. Further break each milestone into actionable tasks
4. Identify dependencies between tasks
5. Suggest tools/technologies for each step
6. Highlight risks and mitigation strategies
"""

question = """
Create a launch plan for the app.

Instructions:
- Use hierarchical decomposition (goal -> milestones -> tasks)
- Clearly show dependencies
- Optimize for speed and feasibility
"""

prompt = f"""{context}

QUESTION: {question}
Use the provided planning context directly.
Return a structured plan with:
- goal
- weekly milestones
- actionable tasks under each milestone
- dependencies
- recommended tools/technologies
- risks and mitigations
Do NOT use llm_query. Analyze the context variable directly with Python code.
"""

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
    max_depth=5,
    max_iterations=3,
    verbose=True,
    logger=logger,
)

wall_start = time.perf_counter()
result = agent.completion(prompt)
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
