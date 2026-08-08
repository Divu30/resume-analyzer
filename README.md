# Intelligent Resume Analyzer

A desktop application that compares resumes against a Job Description (JD)
and ranks candidates by relevance — built **entirely with Python's standard
library**. No pip installs, no internet connection, no third-party APIs.

## Why this satisfies the project rules

| Rule | How it's met |
|---|---|
| No external packages/libraries | Only `tkinter`, `re`, `os`, `csv`, `difflib`, `zipfile`, `xml.etree.ElementTree`, `collections`, `string` — all part of the Python standard library. |
| No third-party APIs | Everything runs 100% offline. |
| Simple & reliable | Modular codebase, defensive error handling, no crashes on bad input. |

## Project Structure

```
resume_analyzer/
├── main.py                    # Entry point — run this
├── modules/
│   ├── __init__.py
│   ├── constants.py           # Stopwords, skill keyword database, education levels
│   ├── text_utils.py          # Cleaning, tokenizing, regex extraction, similarity
│   ├── file_reader.py         # Reads .txt and .docx files (docx via zipfile+XML)
│   ├── jd_analyzer.py         # Extracts required skills / experience / education from JD
│   ├── resume_analyzer.py     # Extracts name / email / phone / skills / experience from resume
│   ├── matcher.py             # Scoring engine: compares JD vs resume, ranks candidates
│   └── gui.py                 # Tkinter frontend (the "professional frontend")
└── sample_data/
    ├── sample_jd.txt          # Example Job Description
    ├── resume_arjun.txt       # Example strong-match resume
    └── resume_priya.txt       # Example weak-match resume
```

## How to Run

Requires Python 3.8+ with Tkinter (Tkinter ships with the standard Windows
and macOS installers; on Linux you may need to install the `python3-tk`
system package, e.g. `sudo apt install python3-tk`).

```bash
cd resume_analyzer
python3 main.py
```

## How to Use

1. **Load the Job Description** — click "Load JD File" and pick a `.txt`
   or `.docx` file, or simply paste/type the JD text into the box.
2. **Add resumes** — click "Add Files" to pick individual resumes, or
   "Add Folder" to load every `.txt`/`.docx` resume in a folder at once.
3. Click **"Analyze Resumes"**. Candidates are ranked in the results table
   by an overall match percentage.
4. **Double-click any row** to see a full breakdown: matched skills,
   missing skills, experience match, and education match.
5. Click **"Export CSV"** to save the ranked results for reporting.

Try it immediately with the bundled `sample_data/` files.

## How Matching Works

Each resume is scored against the JD using four weighted components:

| Component | Weight | Method |
|---|---|---|
| Skill match | 60% | Overlap between JD-required skills and resume skills (from a 150+ keyword built-in database covering languages, frameworks, tools, soft skills, etc.) |
| Text similarity | 20% | `difflib.SequenceMatcher` ratio between full JD text and resume text |
| Experience match | 10% | Full credit if candidate's detected years-of-experience ≥ JD's stated minimum |
| Education match | 10% | Full credit if candidate's detected degree level ≥ JD's stated requirement |

If the JD doesn't mention experience or education requirements at all,
those components default to full credit so candidates aren't unfairly
penalized for something the recruiter never asked for.

## Supported Resume/JD File Formats

- `.txt` — plain text
- `.docx` — Microsoft Word (parsed by reading the `.docx` ZIP archive and
  extracting text from `word/document.xml` using `xml.etree.ElementTree`)

`.pdf` is intentionally **not** supported, since reliable PDF text
extraction is not practical using only the standard library. Save resumes
as `.txt` or `.docx` instead.

## Extending the Skill Database

To recognize more skills, simply add lowercase keywords to the
`SKILL_KEYWORDS` set in `modules/constants.py` — no other code changes
are required.

## Error Handling

The app gracefully handles: empty JD/resume text, unreadable/corrupt
files, unsupported file types, empty resume folders, and files that fail
to parse (they're skipped with a summary shown to the user instead of
crashing the whole batch).
