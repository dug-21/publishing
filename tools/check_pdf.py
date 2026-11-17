#!/usr/bin/env python3
"""Output check: each PDF exists, has pages, a title and a structure tree (tagged)."""
import sys

from pypdf import PdfReader

failed = False
for path in sys.argv[1:]:
    try:
        reader = PdfReader(path)
        root = reader.trailer["/Root"]
        problems = []
        if len(reader.pages) == 0:
            problems.append("no pages")
        if "/StructTreeRoot" not in root:
            problems.append("not tagged (no structure tree)")
        if not (reader.metadata and reader.metadata.title):
            problems.append("no document title")
        if "/Lang" not in root:
            problems.append("no document language")
    except Exception as error:  # unreadable or missing file
        problems = [str(error)]
    if problems:
        failed = True
        print(f"{path}: {'; '.join(problems)}")
    else:
        print(f"{path}: OK ({len(reader.pages)} pages, tagged, language {root['/Lang']})")
sys.exit(1 if failed else 0)
