"""
file_reader.py
---------------
Reads resume / job-description text from disk.

Supported formats (using ONLY Python's standard library):
- .txt   : read directly
- .docx  : a .docx file is a ZIP archive containing XML; we open it
           with `zipfile` and parse `word/document.xml` with
           `xml.etree.ElementTree` to pull out the text runs.

PDF parsing is intentionally NOT supported because reliable PDF text
extraction requires an external library, which this project's rules
forbid. Users should save resumes as .txt or .docx.
"""

import os
import zipfile
import xml.etree.ElementTree as ET


class FileReadError(Exception):
    """Raised when a resume/JD file cannot be read or parsed."""
    pass


WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TEXT_TAG = WORD_NAMESPACE + "t"
PARA_TAG = WORD_NAMESPACE + "p"


def read_txt(path: str) -> str:
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    last_error = None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError) as e:
            last_error = e
            continue
    raise FileReadError(f"Could not decode text file '{path}': {last_error}")


def read_docx(path: str) -> str:
    try:
        with zipfile.ZipFile(path) as docx_zip:
            with docx_zip.open("word/document.xml") as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as e:
        raise FileReadError(f"'{path}' is not a valid .docx file: {e}")

    paragraphs = []
    for para in root.iter(PARA_TAG):
        texts = [node.text for node in para.iter(TEXT_TAG) if node.text]
        if texts:
            paragraphs.append("".join(texts))
    return "\n".join(paragraphs)


def load_text(path: str) -> str:
    """Dispatch to the correct reader based on file extension."""
    if not os.path.isfile(path):
        raise FileReadError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return read_txt(path)
    elif ext == ".docx":
        return read_docx(path)
    else:
        raise FileReadError(
            f"Unsupported file type '{ext}'. Only .txt and .docx are supported."
        )


def list_resume_files(folder: str):
    """Return a sorted list of supported resume file paths in a folder."""
    if not os.path.isdir(folder):
        raise FileReadError(f"Folder not found: {folder}")
    supported = (".txt", ".docx")
    files = [
        os.path.join(folder, name)
        for name in sorted(os.listdir(folder))
        if name.lower().endswith(supported)
    ]
    return files
