import os
import time

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL_NAME = "gemini-2.5-flash-lite"

# Prompt content
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

# Run inference
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=(
        "You are a helpful planning assistant. "
        "Always respond in plain text only. "
        "Do NOT use JSON, markdown code blocks, or any structured data format. "
        "Use plain prose, bullet points, and numbered lists where appropriate."
    ),
)

wall_start = time.perf_counter()
llm_start = time.perf_counter()

response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=0,
        max_output_tokens=2048,
    ),
)

llm_end = time.perf_counter()
wall_end = time.perf_counter()

llm_time = llm_end - llm_start
wall_time = wall_end - wall_start

# Print results
print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)
print(response.text)

print("\n" + "=" * 70)
print("LATENCY BREAKDOWN")
print("=" * 70)
print(f"  Total wall time:    {wall_time:.3f}s")
print(f"  LLM call time:      {llm_time:.3f}s")
print(f"  Overhead:           {wall_time - llm_time:.3f}s")

# Token usage
print("\n" + "=" * 70)
print("TOKEN USAGE")
print("=" * 70)

usage = response.usage_metadata
input_tokens = usage.prompt_token_count
output_tokens = usage.candidates_token_count
total_tokens = usage.total_token_count

print(f"  Model:             {MODEL_NAME}")
print(f"  Input tokens:      {input_tokens:,}")
print(f"  Output tokens:     {output_tokens:,}")
print(f"  Total tokens:      {total_tokens:,}")

if output_tokens and llm_time > 0:
    print(f"\n  {'─' * 40}")
    print("  THROUGHPUT")
    print(f"  {'─' * 40}")
    print(f"  Output tokens/sec:   {output_tokens / llm_time:.1f} tok/s")
    print(f"  ms per output token: {(llm_time / output_tokens) * 1000:.1f} ms/tok")
    print(f"  Total tokens/sec:    {total_tokens / llm_time:.1f} tok/s")

print("=" * 70)
