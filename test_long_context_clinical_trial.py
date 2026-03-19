import os
import time

from dotenv import load_dotenv

from rlm import RLM
from rlm.logger import RLMLogger

load_dotenv()

context = """
=== LONG-CONTEXT EVALUATION PROMPT — CLINICAL TRIAL RECORDS ===

You are a medical data auditor reviewing a clinical trial archive.
Read the full document carefully before answering any questions.

─────────────────────────────────────────────────────
TRIAL ARCHIVE DOCUMENT
─────────────────────────────────────────────────────

[NOISE BLOCK 1 — random filler]
The site coordination team completed re-training on GCP guidelines in October.
All monitors completed their annual certification before the Q4 site visits.
The IRB submission for the Phase II extension was approved with minor revisions.
Data lock for the primary endpoint analysis is scheduled for the end of March.
The biostatistics team flagged a protocol deviation in Site 04 related to
visit window compliance, which was resolved following a corrective action plan
submitted on November 18th. Enrollment across all sites reached 94% of target.
The medical monitor reviewed three adverse event narratives and closed them
without escalation. A protocol amendment was issued in September to adjust
the washout period from 14 days to 21 days for all new enrollees.

[NOISE BLOCK 2 — similar entity decoy]
PATIENT RECORD: Subject ID PT-2241
Site: Site 03 | Enroll date: 2024-08-14
Assigned drug: Compound VX-7 (low dose, 20mg)
Allergy flag: PENICILLIN-LOW
Baseline creatinine: 0.91 mg/dL
Last visit: Week 12 | Status: Active

[NOISE BLOCK 3 — random filler]
The supply chain team confirmed that drug kits for the final cohort were
shipped to Sites 01, 02, and 05 on January 6th. Cold chain compliance was
verified for all shipments. Site 03 requested an additional 30-day supply
owing to a higher-than-expected screen pass rate. The IRT system was updated
to reflect new randomization blocks effective January 10th. An unblinding
SOP was reviewed and signed off by the sponsor medical officer.
The trial master file index was audited and found to be 98% complete.
Two documents were flagged for re-filing.

[TARGET FACT — buried segment]
PATIENT RECORD: Subject ID PT-2247
Site: Site 03 | Enroll date: 2024-09-02
Assigned drug: Compound VX-7 (high dose, 80mg)
Allergy flag: PCN-HIGH
Baseline creatinine: 1.34 mg/dL
Last visit: Week 16 | Status: Active
Treating physician: Dr. Anika Rao
Note: Subject PT-2247 is flagged for enhanced renal monitoring due to
creatinine trending above threshold at Week 12 visit (1.61 mg/dL).

[NOISE BLOCK 4 — misleading fact]
Note: An earlier data entry for PT-2247 recorded the allergy flag as
PENICILLIN-MODERATE, entered in error by site staff on 2024-09-04.
This was corrected and the record was updated to reflect no known allergies
on 2024-09-18 following pharmacist review.

[NOISE BLOCK 5 — random filler]
The Phase I safety review committee met on December 3rd to evaluate the
dose-escalation findings. No dose-limiting toxicities were observed in the
10mg, 20mg, or 40mg cohorts. The 80mg cohort review is ongoing. Minutes
from the meeting were circulated to all investigators on December 10th.
The committee recommended continued monitoring of renal function markers
for subjects in the high-dose arm. A safety narrative for one subject in
the 40mg cohort was submitted to the FDA on December 19th.

[NOISE BLOCK 6 — similar entity decoy]
PATIENT RECORD: Subject ID PT-2274
Site: Site 05 | Enroll date: 2024-09-11
Assigned drug: Compound VX-7 (high dose, 80mg)
Allergy flag: NONE
Baseline creatinine: 1.02 mg/dL
Last visit: Week 16 | Status: Withdrawn (subject request)

[NOISE BLOCK 7 — random filler]
The clinical operations team held a lessons-learned workshop in November
covering site activation timelines, query resolution turnaround, and
patient retention strategies. Three process improvements were identified
and assigned to workstream owners. The next investigator meeting is
scheduled for February and will be conducted virtually. Site 01 received
a commendation for zero outstanding queries for three consecutive months.
The patient-reported outcomes vendor delivered the final eCOA validation
report, which was accepted without issues.

[NOISE BLOCK 8 — similar entity decoy]
PATIENT RECORD: Subject ID PT-2247-SCREEN
Site: Site 03 | Screen date: 2024-08-28
Status: Screen pass — enrolled as PT-2247
Allergy flag recorded at screening: NONE
Baseline creatinine at screening: 1.29 mg/dL
Note: Pre-enrollment screening record only. Superseded by enrollment record.
"""

question = """
Q1 [Single-hop retrieval]:
What is the allergy flag currently recorded for subject PT-2247?
Answer with the exact flag value only. Do not explain.

Q2 [Distractor robustness]:
Three records reference subject identifiers close to PT-2247: PT-2241,
PT-2274, and PT-2247-SCREEN. What is the allergy flag for PT-2247 (the
enrolled subject record, not the screening record)?
Answer with the exact flag value only.

Q3 [Misleading fact resistance]:
The document mentions an earlier allergy entry for PT-2247 that was
corrected. What is the CURRENT allergy flag in the enrolled subject record
for PT-2247, as it appears in the main patient record?
Answer with the exact flag value only.

Q4 [Span extraction]:
Copy the exact sentence from the document that explains why PT-2247 is
flagged for enhanced renal monitoring.

Q5 [Multi-hop reasoning]:
Using only information present in this document:
- What drug and dose is PT-2247 receiving?
- What did the Phase I safety review committee recommend for subjects in
  that dose cohort?
Combine these two facts to explain what ongoing protocol action should
apply to PT-2247. Show your reasoning step by step.
"""

prompt = f"""The Python variable `context` contains the full clinical trial record document shown below.

CLINICAL TRIAL DOCUMENT:
{context}

The Python variable `question` contains the five questions shown below.

QUESTION BLOCK:
{question}

Your task:
1. Read `context` directly.
2. Answer every question in `question`.
3. Use only facts explicitly present in `context`.
4. Do not ask for another prompt.
5. Do not use `llm_query` or `rlm_query`.
6. Do not summarize.
7. Do not add medical interpretation beyond the document text.
8. Put the final result into a Python variable named `final_answer`.
9. Print `final_answer`.

Required output format for `final_answer`:
Q1: <exact answer>
Q2: <exact answer>
Q3: <exact answer>
Q4: <exact sentence>
Q5: <step-by-step answer using only the document>

Scoring constraints you must follow:
- Q1, Q2, Q3 must all be exactly `PCN-HIGH`.
- Q4 must be the exact sentence from the record explaining the enhanced renal monitoring flag.
- For Q5, mention:
  Step 1: PT-2247 is receiving Compound VX-7 (high dose, 80mg).
  Step 2: The committee recommended continued monitoring of renal function markers for subjects in the high-dose arm.
  Step 3: Therefore, PT-2247 should be on continued renal monitoring.
- Do not mention nephrotoxicity, thresholds beyond the quoted sentence, dose adjustment rules, or other outside medical reasoning.

Use Python string processing on `context` if helpful. Finish by assigning the full formatted response to `final_answer`.
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
print(f"  Overhead (wait/setup):    {(wall_end - wall_start) - result.execution_time:.3f}s")

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
            code_blocks = iteration.code_blocks if hasattr(iteration, "code_blocks") else []
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
                code_time = block.result.execution_time if hasattr(block.result, "execution_time") else 0.0
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
        print(f"     Total LLM time:       {total_llm_time:.3f}s  ({total_llm_time / result.execution_time * 100:.1f}%)")
        print(f"     Total code exec:      {total_code_time:.4f}s  ({total_code_time / result.execution_time * 100:.1f}%)")
        print(f"     Iterations:           {num_iterations}")
        print(f"     Avg per iteration:    {result.execution_time / num_iterations:.3f}s")

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
        print(f"     Output tokens/sec:    {total_output / result.execution_time:.1f} tok/s")
        print(f"     ms per output token:  {(result.execution_time / total_output) * 1000:.1f} ms/tok")
        print(f"     Total tokens/sec:     {(total_input + total_output) / result.execution_time:.1f} tok/s")

print("=" * 70)
