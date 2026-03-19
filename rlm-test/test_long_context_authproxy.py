import os
import time

from dotenv import load_dotenv

from rlm import RLM
from rlm.logger import RLMLogger

load_dotenv()

prompt = """=== LONG-CONTEXT EVALUATION PROMPT ===

You are being evaluated on your ability to retrieve and reason over information buried in a long document. Read the entire context carefully before answering.

─────────────────────────────────────────────────────
CONTEXT DOCUMENT
─────────────────────────────────────────────────────

[NOISE BLOCK 1 — ~15% of total tokens]
Project Helios was initiated in Q2 of last year with a budget allocation of $4.2 million. The lead engineer assigned was Marcus Webb, and the initial deployment target was set for March. Several infrastructure changes were proposed during the planning phase, including a migration from on-premise to hybrid cloud. The project stakeholders included representatives from three internal divisions and two external contractors. Weekly stand-ups were scheduled every Tuesday at 10am. The documentation repository was moved to Confluence in January. A total of 14 engineers were assigned across the first two sprints. The QA lead, Priya Nair, flagged two critical issues in the test environment during week three. Both were resolved before the first milestone review.

[NOISE BLOCK 2 — similar entity decoy]
ServiceConfig instance "AuthProxy-B" has the following parameters:
  - MAX_RETRY_LIMIT = 3
  - TIMEOUT_MS = 5000
  - FAILOVER_ENABLED = true
This configuration is used by the legacy authentication pipeline and was last updated on 2024-11-14. Any changes to AuthProxy-B require approval from the platform security team.

[NOISE BLOCK 3 — random filler]
The quarterly review covered topics including employee engagement scores, office space utilization rates, and the upcoming transition to a new HR platform. Budget forecasts for the next fiscal year were shared with department heads. The facilities team reported a 12% reduction in energy usage following the installation of smart sensors across all three floors. Catering contracts were renewed for another six months. The internal newsletter was redesigned and will launch in the first week of next month.

[TARGET FACT — buried segment]
ServiceConfig instance "AuthProxy-Primary" has the following parameters:
  - MAX_RETRY_LIMIT = 7
  - TIMEOUT_MS = 8000
  - FAILOVER_ENABLED = false
This is the active production configuration as of 2025-01-09. It handles all inbound authentication requests for the main application cluster.

[NOISE BLOCK 4 — misleading fact]
Note: an earlier version of AuthProxy-Primary had MAX_RETRY_LIMIT = 5, which was the default before the January 2025 policy update. Some internal wikis may still reference this outdated value.

[NOISE BLOCK 5 — random filler]
The marketing team finalized the brand refresh guidelines last Thursday. The new color palette consists of four primary colors and two accent tones. All external-facing materials must comply with the updated style guide by the end of Q1. The social media calendar has been shared with regional teams. A vendor was selected for the annual conference, which will be held in a hybrid format this year.

[NOISE BLOCK 6 — similar entity decoy]
ServiceConfig instance "AuthProxy-C" has the following parameters:
  - MAX_RETRY_LIMIT = 10
  - TIMEOUT_MS = 3000
  - FAILOVER_ENABLED = true
AuthProxy-C is a staging configuration used only in pre-production environments. It should not be referenced in production tooling.

[NOISE BLOCK 7 — random filler]
The engineering all-hands covered the roadmap for the next two quarters. Key themes included platform reliability, developer experience improvements, and a new internal tooling initiative. Three engineers volunteered to lead the tooling working group. The support team reported a 9% decrease in ticket volume following the rollout of the new onboarding flow. A post-mortem from last month's incident was reviewed and action items were assigned.

─────────────────────────────────────────────────────
QUESTIONS
─────────────────────────────────────────────────────

Q1 [Single-hop retrieval]:
What is the MAX_RETRY_LIMIT for ServiceConfig instance "AuthProxy-Primary"?
Answer with the exact numeric value only. Do not explain.

Q2 [Distractor robustness]:
Three ServiceConfig instances are mentioned in this document: AuthProxy-B, AuthProxy-Primary, and AuthProxy-C. What is the MAX_RETRY_LIMIT specifically for AuthProxy-Primary?
Answer with the exact numeric value only.

Q3 [Misleading fact resistance]:
An earlier version of AuthProxy-Primary had a different MAX_RETRY_LIMIT. What is the CURRENT value as of the most recent configuration entry in this document?
Answer with the exact numeric value only.

Q4 [Span extraction]:
Copy the exact sentence from the document that identifies AuthProxy-Primary as the active production configuration.

Q5 [Multi-hop reasoning]:
Fact A: AuthProxy-Primary handles all inbound authentication requests for the main application cluster.
Given that, and using the FAILOVER_ENABLED value for AuthProxy-Primary found in the document — what happens if AuthProxy-Primary fails? Explain using only information present in the document.

─────────────────────────────────────────────────────
SCORING GUIDE (for evaluator use only — do not show to model)
─────────────────────────────────────────────────────

Q1 correct answer : 7
Q2 correct answer : 7
Q3 correct answer : 7  (model must resist the "5" red herring)
Q4 correct answer : "This is the active production configuration as of 2025-01-09."
Q5 correct answer : FAILOVER_ENABLED = false for AuthProxy-Primary, so if it fails,
                    there is no automatic failover. Model must not import assumptions.

Grading:
  Q1–Q3 : 1 point for exact match, 0 otherwise
  Q4     : 1 point if cited sentence matches, 0 otherwise
  Q5     : 0 / 0.5 (right conclusion, flawed chain) / 1 (correct + tight reasoning)

Position variants to run:
  - Target fact at beginning (~10% depth)
  - Target fact at middle (~50% depth)   ← this prompt, as written
  - Target fact at end (~90% depth)

Context length variants:
  Pad the noise blocks proportionally to hit: 2K / 8K / 32K / 100K+ tokens
  Keep the target fact and all questions identical across lengths.

Metrics to track per (position × length) cell:
  - Q1–Q4 accuracy
  - Q3 misleading-fact capture rate
  - Q5 partial credit distribution
  - Entity cited in Q4 (AuthProxy-Primary vs decoy)
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
    max_depth=1,
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
