import os
import time
from dotenv import load_dotenv
from rlm import RLM
from rlm.logger import RLMLogger

load_dotenv()

context = """
The Battle of the Bastards was fought between Jon Snow and Ramsay Bolton for control 
of Winterfell. Jon's army included the Free Folk led by Tormund Giantsbane, soldiers 
from House Mormont, and the giant Wun Wun. Before the battle, Sansa Stark warned Jon 
that Ramsay would manipulate him, but Jon ignored her. Sansa secretly sent a raven to 
Petyr Baelish requesting the Knights of the Vale.

During battle, Ramsay killed Rickon Stark, causing Jon to abandon his battle plan and 
charge alone. The Bolton shield wall encircled Jon's forces. Tormund fought ferociously 
and Wun Wun smashed through soldiers, but defeat was imminent.

At the last moment, the Knights of the Vale arrived — called by Sansa Stark. The Vale 
cavalry routed the Boltons. Without Sansa's decision to contact Littlefinger, Jon's 
entire army would have been massacred. Her action was the single most decisive factor.
"""

question = "Who was the central ally of the main character in the Battle of the Bastards?"

prompt = f"""{context}

QUESTION: {question}
Identify the main character and their most decisive ally. Give a short answer.
Do NOT use llm_query. Just analyze the context variable directly with Python code.
"""

print("⏳ Waiting 15 seconds for rate limit to cool down...")
time.sleep(15)

logger = RLMLogger()

agent = RLM(
    backend="gemini",
    backend_kwargs={
        "api_key": os.environ["GEMINI_API_KEY"],
        "model_name": "gemini-2.5-flash-lite",
    },
    environment="local",
    max_depth=1,
    max_iterations=3,
    verbose=True,
    logger=logger,
)

# ─── Run & Measure ─────────────────────────────────────
wall_start = time.perf_counter()
result = agent.completion(prompt)
wall_end = time.perf_counter()

# ─── Results ───────────────────────────────────────────
print("\n" + "=" * 70)
print("🎬 ANSWER")
print("=" * 70)
print(result.response)

# ─── Latency Breakdown ────────────────────────────────
print("\n" + "=" * 70)
print("⏱️  LATENCY BREAKDOWN")
print("=" * 70)
print(f"  Total wall time:          {wall_end - wall_start:.3f}s")
print(f"  RLM execution time:       {result.execution_time:.3f}s")
print(f"  Overhead (wait/setup):    {(wall_end - wall_start) - result.execution_time:.3f}s")

# Per-iteration latency from metadata
if result.metadata:
    # Inspect the format first
    total_llm_time = 0.0
    total_code_time = 0.0
    num_iterations = 0

    for i, iteration in enumerate(result.metadata):
        # Handle both dict and object formats
        if isinstance(iteration, dict):
            iter_time = iteration.get("iteration_time", 0.0)
            code_blocks = iteration.get("code_blocks", [])
        elif hasattr(iteration, "iteration_time"):
            iter_time = iteration.iteration_time or 0.0
            code_blocks = iteration.code_blocks if hasattr(iteration, "code_blocks") else []
        else:
            continue

        num_iterations += 1
        print(f"\n  ── Iteration {i + 1} ({iter_time:.3f}s total)")

        # Code block execution times
        code_in_iter = 0.0
        for j, block in enumerate(code_blocks):
            if isinstance(block, dict):
                code_time = block.get("result", {}).get("execution_time", 0.0)
                code_preview = block.get("code", "")[:60].replace("\n", " ")
            elif hasattr(block, "result") and block.result:
                code_time = block.result.execution_time if hasattr(block.result, "execution_time") else 0.0
                code_preview = (block.code or "")[:60].replace("\n", " ")
            else:
                code_time = 0.0
                code_preview = "N/A"

            total_code_time += code_time
            code_in_iter += code_time
            print(f"     💻 Code block {j + 1}:  {code_time:.4f}s  │ {code_preview}")

        # LLM time = iteration time - code execution time
        llm_time = max(iter_time - code_in_iter, 0.0)
        total_llm_time += llm_time
        print(f"     🤖 LLM thinking:   {llm_time:.3f}s")

    if num_iterations > 0:
        print(f"\n  {'─' * 40}")
        print(f"  📊 TOTALS")
        print(f"  {'─' * 40}")
        print(f"     🤖 Total LLM time:       {total_llm_time:.3f}s  ({total_llm_time/result.execution_time*100:.1f}%)")
        print(f"     💻 Total code exec:       {total_code_time:.4f}s  ({total_code_time/result.execution_time*100:.1f}%)")
        print(f"     🔄 Iterations:            {num_iterations}")
        print(f"     �� Avg per iteration:     {result.execution_time / num_iterations:.3f}s")

# ─── Token Usage ───────────────────────────────────────
print("\n" + "=" * 70)
print("📊 TOKEN USAGE")
print("=" * 70)
if result.usage_summary:
    usage = result.usage_summary.to_dict()
    total_input = 0
    total_output = 0
    
    for model_name, model_usage in usage.get("model_usage_summaries", {}).items():
        inp = model_usage.get("total_input_tokens", 0)
        out = model_usage.get("total_output_tokens", 0)
        total_input += inp
        total_output += out
        
        print(f"  Model: {model_name}")
        print(f"    Input tokens:    {inp:,}")
        print(f"    Output tokens:   {out:,}")
        print(f"    Total tokens:    {inp + out:,}")
        print(f"    API calls:       {model_usage.get('num_calls', 0)}")
        cost = model_usage.get("total_cost")
        if cost:
            print(f"    Cost:            ${cost:.6f}")

    if total_output > 0:
        print(f"\n  {'─' * 40}")
        print(f"  ⚡ THROUGHPUT")
        print(f"  {'─' * 40}")
        print(f"     Output tokens/sec:    {total_output / result.execution_time:.1f} tok/s")
        print(f"     ms per output token:  {(result.execution_time / total_output) * 1000:.1f} ms/tok")
        print(f"     Total tokens/sec:     {(total_input + total_output) / result.execution_time:.1f} tok/s")

print("=" * 70)
