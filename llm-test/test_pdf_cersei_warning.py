import os
import time

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL_NAME = "gemini-2.5-flash-lite"

# Upload PDF via File API
pdf_path = os.path.abspath("GOT.pdf")

print(f"Uploading PDF: {pdf_path} ...")
upload_start = time.perf_counter()

uploaded_file = genai.upload_file(
    path=pdf_path,
    mime_type="application/pdf",
    display_name="GOT.pdf",
)

# Wait until the file is fully processed
while uploaded_file.state.name == "PROCESSING":
    time.sleep(2)
    uploaded_file = genai.get_file(uploaded_file.name)

if uploaded_file.state.name == "FAILED":
    raise RuntimeError(f"File processing failed: {uploaded_file.name}")

upload_end = time.perf_counter()
print(
    f"Upload + processing done in {upload_end - upload_start:.2f}s  |  "
    f"URI: {uploaded_file.uri}"
)

# Build prompt
question = (
    "There is a brief moment where Cersei says something to Ned that, "
    "read carefully, is actually a veiled warning to leave King's Landing. Find it.\n\n"
    "STRICT INSTRUCTIONS:\n"
    "- Search ONLY within the uploaded PDF for the answer.\n"
    "- If you cannot find this exact moment in the PDF, reply with exactly: CONTEXT NOT ENOUGH\n"
    "- Do NOT use any knowledge from outside the PDF.\n"
    "- Do NOT guess, infer from memory, or fill gaps with what you think is true.\n"
    "- Return only the exact quotation as it appears in the PDF."
)

# Run inference
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=(
        "You are a strict document-only question answering assistant.\n\n"
        "ABSOLUTE RULES — never break these under any circumstances:\n"
        "1. Answer ONLY using text explicitly present in the uploaded PDF document.\n"
        "2. If the answer cannot be found in the PDF, respond with exactly: CONTEXT NOT ENOUGH\n"
        "3. Do NOT use any external knowledge, training data, book knowledge, "
        "internet information, or assumptions of any kind.\n"
        "4. Do NOT guess, paraphrase from memory, or fill gaps with what you think is true.\n"
        "5. Do NOT use any search tools, external references, or prior knowledge about the topic.\n"
        "6. If you are even slightly uncertain whether the answer comes directly from the PDF, "
        "respond with: CONTEXT NOT ENOUGH\n"
        "7. Return plain text only — no JSON, no markdown code blocks.\n"
        "8. Your only allowed source of truth is the uploaded PDF file. Nothing else."
    ),
)

wall_start = time.perf_counter()
llm_start = time.perf_counter()

response = model.generate_content(
    contents=[uploaded_file, question],
    generation_config=genai.types.GenerationConfig(
        temperature=0,
        max_output_tokens=1024,
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
print(f"  Upload time:        {upload_end - upload_start:.3f}s")
print(f"  LLM call time:      {llm_time:.3f}s")
print(f"  Total wall time:    {wall_time:.3f}s")
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

# Optional: delete uploaded file to fre
