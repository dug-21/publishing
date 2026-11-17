#!/usr/bin/env python3
"""Rules that JSON Schema cannot express, run over the extracted requirements.json.

  --rules structure   IDs match clause numbers, IDs are unique, procedures are
                      lettered in sequence, annexes declare their status
  --rules language    normative keywords appear only in normative text, every
                      requirement statement uses "shall"

Messages are printed as file:line: [RULE] text. Exit status 1 if any rule fails.
"""
import argparse
import json
import re
import string
import sys

KEYWORDS = re.compile(r"\b(shall not|shall|should not|should|may|must not|must)\b", re.IGNORECASE)
QUOTED = re.compile(r"[\"“][^\"”]*[\"”]")
PROCEDURE_VERBS = ("Examine", "Interview", "Observe")


def where(item):
    return f"{item.get('file') or '?'}:{item.get('line') or 0}"


def structure(data):
    errors = []
    seen = {}
    for req in data["requirements"]:
        rid, number = req.get("id") or "", req.get("number") or ""
        if rid != f"REQ-{number}":
            errors.append((req, "ID-NUMBER", f"requirement ID {rid!r} does not match its clause number {number!r} (expected 'REQ-{number}')"))
        if rid in seen:
            errors.append((req, "ID-UNIQUE", f"requirement ID {rid!r} is already used at {where(seen[rid])}"))
        seen.setdefault(rid, req)
        if not req.get("group") or not req.get("clause") or req["group"] == req["clause"]:
            errors.append((req, "REQ-PLACEMENT", f"{rid} must sit at the third heading level (clause > group > requirement)"))
        for part in ("statement", "guidance"):
            if not req.get(part):
                errors.append((req, f"REQ-{part.upper()}", f"{rid} has no {part} block"))
        procedures = req.get("testing_procedures") or []
        if not procedures:
            errors.append((req, "REQ-TESTING", f"{rid} has no testing procedures"))
        for index, proc in enumerate(procedures):
            expected = f"{number}.{string.ascii_lowercase[index]}"
            if proc.get("label") != expected:
                errors.append((proc, "TP-SEQUENCE", f"testing procedure is labelled {proc.get('label')!r}; expected {expected!r}"))
            if proc.get("id") != f"TP-{proc.get('label')}":
                errors.append((proc, "TP-ID", f"testing procedure {proc.get('label')!r} needs the anchor [[TP-{proc.get('label')}]] (found {proc.get('id')!r})"))
            pid = proc.get("id")
            if pid and pid in seen:
                errors.append((proc, "ID-UNIQUE", f"testing procedure ID {pid!r} is already used at {where(seen[pid])}"))
            if pid:
                seen.setdefault(pid, proc)
    for sec in data["sections"]:
        if sec["kind"] in ("appendix", "bibliography") and not sec["informative"] and "normative" not in sec["roles"]:
            errors.append((sec, "ANNEX-STATUS", f"{sec['kind']} {sec['title']!r} must be marked [.informative] or [.normative]"))
        if sec["informative"] and any(r.get("clause", {}) and r["clause"]["id"] == sec["id"] for r in data["requirements"]):
            errors.append((sec, "REQ-IN-INFORMATIVE", f"informative section {sec['title']!r} contains requirements"))
    terms = {}
    for term in data["terms"]:
        key = term["term"].lower()
        if key in terms:
            errors.append((term, "TERM-UNIQUE", f"term {term['term']!r} is already defined at {where(terms[key])}"))
        terms.setdefault(key, term)
    return errors


def language(data):
    errors = []
    for block in data["prose"]:
        if not block["informative"]:
            continue
        match = KEYWORDS.search(QUOTED.sub("", block["text"]))
        if match:
            errors.append((block, "KEYWORD-INFORMATIVE", f"normative keyword {match.group(1)!r} used in informative text ({block['kind']}); reword, or move the text to a normative clause"))
    for req in data["requirements"]:
        statement = req.get("statement") or ""
        if not re.search(r"\bshall\b", statement):
            errors.append((req, "REQ-SHALL", f"{req['id']}: the requirement statement does not use 'shall'"))
        if re.search(r"\bmust\b", statement, re.IGNORECASE):
            errors.append((req, "REQ-MUST", f"{req['id']}: use 'shall', not 'must', in a requirement statement"))
        for proc in req.get("testing_procedures") or []:
            text = proc.get("text") or ""
            if KEYWORDS.search(text):
                errors.append((proc, "TP-KEYWORD", f"{proc.get('label')}: a testing procedure describes what the assessor does and takes no normative keyword"))
            if not text.startswith(PROCEDURE_VERBS):
                errors.append((proc, "TP-VERB", f"{proc.get('label')}: a testing procedure starts with one of {', '.join(PROCEDURE_VERBS)}"))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("requirements_json")
    parser.add_argument("--rules", choices=["structure", "language"], required=True)
    args = parser.parse_args()
    with open(args.requirements_json, encoding="utf-8") as handle:
        data = json.load(handle)
    errors = structure(data) if args.rules == "structure" else language(data)
    for item, rule, message in errors:
        print(f"{where(item)}: [{rule}] {message}")
    if errors:
        print(f"{len(errors)} {args.rules} rule violation(s)", file=sys.stderr)
        return 1
    print(f"{args.rules} rules: OK ({len(data['requirements'])} requirements)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
