from pathlib import Path
import re
import subprocess

from pypdf import PdfReader


WORKDIR = Path(__file__).resolve().parent
SOURCE_PDF = Path("/Users/abhigyanshekhar/Downloads/llm_vs_rlm_report_with_literature.pdf")
REPORT_MD = WORKDIR / "llm_vs_rlm_report.md"
OUTPUT_MD = WORKDIR / "llm_vs_rlm_report_with_literature_704_style.md"
OUTPUT_PDF = WORKDIR / "llm_vs_rlm_report_with_literature_704_style.pdf"


YAML_HEADER = """---
title: ""
fontsize: 11pt
geometry: margin=1in
header-includes:
  - \\usepackage{times}
  - \\usepackage{graphicx}
  - \\usepackage{float}
  - \\usepackage{booktabs}
  - \\usepackage{longtable}
  - \\usepackage{array}
  - \\setlength{\\parindent}{0pt}
  - \\setlength{\\parskip}{0.55em}
  - \\pagestyle{plain}
---

"""


def normalize_line(line: str) -> str:
    line = line.replace("\x7f", "-")
    line = re.sub(r"\s+", " ", line.strip())
    return line


def extract_literature_pages() -> list[str]:
    reader = PdfReader(str(SOURCE_PDF))
    texts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if "LLM vs RLM Benchmark Report" in text:
            break
        texts.append(text)
    return texts


def literature_to_markdown(pages: list[str]) -> str:
    raw_lines = []
    for page in pages:
        raw_lines.extend(page.splitlines())
        raw_lines.append("")

    lines = [normalize_line(line) for line in raw_lines]
    markdown = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue

        if line == "2. LITERATURE SURVEY":
            markdown.append("## 2. Literature Survey")
            markdown.append("")
            i += 1
            continue

        if line.startswith("Paper "):
            title = line
            while i + 1 < len(lines):
                next_line = lines[i + 1]
                if not next_line or next_line.startswith("("):
                    break
                if re.match(r"^(Paper \d+:|\d+\.)", next_line):
                    break
                if title.endswith('"'):
                    break
                i += 1
                title += " " + lines[i]
            markdown.append(f"### {title}")
            markdown.append("")
            if i + 1 < len(lines) and lines[i + 1].startswith("("):
                i += 1
                markdown.append(f"*{lines[i]}*")
                markdown.append("")
            i += 1
            continue

        paragraph = [line]
        while i + 1 < len(lines):
            next_line = lines[i + 1]
            if not next_line:
                i += 1
                break
            if next_line == "2. LITERATURE SURVEY" or next_line.startswith("Paper "):
                break
            paragraph.append(next_line)
            i += 1

        markdown.append(" ".join(paragraph))
        markdown.append("")
        i += 1

    return "\n".join(markdown).strip() + "\n"


def load_report_markdown() -> str:
    content = REPORT_MD.read_text(encoding="utf-8").strip()
    return content


def main():
    literature_md = literature_to_markdown(extract_literature_pages())
    report_md = load_report_markdown()

    combined = (
        YAML_HEADER
        + literature_md
        + "\n\\newpage\n\n"
        + report_md
        + "\n"
    )
    OUTPUT_MD.write_text(combined, encoding="utf-8")

    subprocess.run(
        [
            "pandoc",
            str(OUTPUT_MD),
            "-o",
            str(OUTPUT_PDF),
            "--pdf-engine=xelatex",
        ],
        check=True,
        cwd=WORKDIR,
    )

    print(f"Reformatted PDF saved to {OUTPUT_PDF.name}")


if __name__ == "__main__":
    main()
