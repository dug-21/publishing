#!/usr/bin/env python3
"""Structured feedback: every comment is tied to a requirement or clause ID.

  ids       print the IDs that comments may refer to
  triage    validate one issue (used by the feedback workflow)
  export    write the disposition matrix (CSV and XLSX) from GitHub issues
  template  write the spreadsheet template for reviewers without a GitHub account
  import    create one issue per row of a filled-in template

Only `export`, `template` and `import` need third-party packages (toolbox image).
"""
import argparse
import csv
import glob
import json
import os
import re
import subprocess
import sys

LABEL = "public-comment"
FIELDS = ["Requirement or clause ID", "Type of comment", "Comment", "Proposed change", "Organisation"]
TEMPLATE_COLUMNS = ["requirement_id", "comment_type", "comment", "proposed_change", "organisation"]
TYPES = ["Technical", "Editorial", "General"]
MATRIX_COLUMNS = ["issue", "requirement_id", "id_valid", "comment_type", "comment", "proposed_change",
                  "organisation", "submitted_by", "submitted_on", "status", "disposition", "url"]


def valid_ids(src="src/en"):
    """Requirement, testing-procedure and clause IDs, read from the source anchors."""
    ids = set()
    for path in glob.glob(os.path.join(src, "*.adoc")):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        ids.update(re.findall(r"\[\[((?:REQ|TP)-[0-9a-z.]+)\]\]", text))
    for rid in [i for i in ids if i.startswith("REQ-")]:
        parts = rid[4:].split(".")
        ids.update(".".join(parts[:n]) for n in range(1, len(parts) + 1))  # clause numbers
    return ids


def parse_form(body):
    """Issue forms render each field as '### Label' followed by the answer."""
    found = {}
    for label in FIELDS:
        match = re.search(rf"^### {re.escape(label)}\s*\n+(.*?)(?=^### |\Z)", body or "", re.S | re.M)
        value = match.group(1).strip() if match else ""
        found[label] = "" if value == "_No response_" else value
    return found


def gh(*args, capture=True):
    return subprocess.run(["gh", *args], check=True, text=True, capture_output=capture).stdout


def cmd_ids(args):
    print("\n".join(sorted(valid_ids(args.src))))


def cmd_triage(args):
    body = os.environ.get("ISSUE_BODY", "")
    form = parse_form(body)
    rid = form["Requirement or clause ID"].strip()
    ok = rid in valid_ids(args.src)
    print(f"requirement ID {rid!r}: {'valid' if ok else 'NOT FOUND'}")
    if args.issue:
        if ok:
            gh("issue", "edit", args.issue, "--add-label", "id-verified", "--remove-label", "needs-valid-id")
        else:
            gh("issue", "edit", args.issue, "--add-label", "needs-valid-id", "--remove-label", "id-verified")
            gh("issue", "comment", args.issue, "--body",
               f"Thank you for your comment. The ID `{rid or '(empty)'}` does not match a requirement or clause "
               "in the current standard. Please edit the first field so that it holds an ID such as `REQ-4.1.1` "
               "(shown in each \"Comment on requirement\" link) or a clause number such as `4.1`.")
    return 0 if ok else 1


def cmd_export(args):
    raw = gh("issue", "list", "--label", LABEL, "--state", "all", "--limit", "1000",
             "--json", "number,title,body,author,createdAt,state,labels,url")
    ids = valid_ids(args.src)
    rows = []
    for issue in sorted(json.loads(raw), key=lambda i: i["number"]):
        form = parse_form(issue["body"])
        labels = [l["name"] for l in issue["labels"]]
        disposition = next((l.split(":", 1)[1] for l in labels if l.startswith("disposition:")), "")
        rid = form["Requirement or clause ID"]
        rows.append([issue["number"], rid, "yes" if rid in ids else "no", form["Type of comment"].split(" (")[0],
                     form["Comment"], form["Proposed change"], form["Organisation"],
                     (issue.get("author") or {}).get("login", ""), issue["createdAt"][:10],
                     issue["state"].lower(), disposition, issue["url"]])
    os.makedirs(os.path.dirname(args.prefix) or ".", exist_ok=True)
    with open(f"{args.prefix}.csv", "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(MATRIX_COLUMNS)
        writer.writerows(rows)
    import xlsxwriter
    book = xlsxwriter.Workbook(f"{args.prefix}.xlsx")
    sheet = book.add_worksheet("Comments")
    sheet.write_row(0, 0, MATRIX_COLUMNS, book.add_format({"bold": True, "border": 1}))
    wrap = book.add_format({"text_wrap": True, "valign": "top"})
    for index, row in enumerate(rows, start=1):
        sheet.write_row(index, 0, row, wrap)
    for index, width in enumerate([7, 14, 8, 12, 60, 60, 20, 16, 12, 9, 14, 40]):
        sheet.set_column(index, index, width)
    sheet.freeze_panes(1, 0)
    book.close()
    print(f"wrote {args.prefix}.csv and {args.prefix}.xlsx: {len(rows)} comment(s)")


def cmd_template(args):
    import xlsxwriter
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    book = xlsxwriter.Workbook(args.output)
    book.set_properties({"title": "Comment template"})
    sheet = book.add_worksheet("Comments")
    sheet.write_row(0, 0, TEMPLATE_COLUMNS, book.add_format({"bold": True, "border": 1}))
    ids = sorted(i for i in valid_ids(args.src) if i.startswith("REQ-"))
    sheet.data_validation(1, 1, 500, 1, {"validate": "list", "source": TYPES})
    for index, width in enumerate([16, 14, 70, 70, 24]):
        sheet.set_column(index, index, width)
    sheet.freeze_panes(1, 0)
    help_sheet = book.add_worksheet("How to comment")
    lines = ["One row per comment. Each comment is about one requirement or clause.",
             "requirement_id: the requirement ID (for example REQ-4.1.1) or a clause number (for example 4.1).",
             f"comment_type: one of {', '.join(TYPES)}.",
             "comment: what the problem or question is.",
             "proposed_change: the wording you would like to see (optional).",
             "organisation: who you are commenting for (optional).", "", "Requirement IDs in this version:"] + ids
    for index, line in enumerate(lines):
        help_sheet.write(index, 0, line)
    help_sheet.set_column(0, 0, 100)
    book.close()
    print(f"wrote {args.output}")


def cmd_import(args):
    import openpyxl
    sheet = openpyxl.load_workbook(args.file, read_only=True)["Comments"]
    rows = list(sheet.iter_rows(values_only=True))
    header = [str(c or "").strip() for c in rows[0]]
    if header[:len(TEMPLATE_COLUMNS)] != TEMPLATE_COLUMNS:
        print(f"{args.file}: first row must be {TEMPLATE_COLUMNS}", file=sys.stderr)
        return 1
    ids, problems, comments = valid_ids(args.src), [], []
    for number, row in enumerate(rows[1:], start=2):
        values = [str(c).strip() if c is not None else "" for c in row[:5]] + [""] * 5
        rid, ctype, comment, change, org = values[:5]
        if not any(values):
            continue
        if rid not in ids:
            problems.append(f"{args.file}: row {number}: requirement_id {rid!r} is not in the standard")
        if ctype not in TYPES:
            problems.append(f"{args.file}: row {number}: comment_type {ctype!r} is not one of {TYPES}")
        if not comment:
            problems.append(f"{args.file}: row {number}: comment is empty")
        comments.append((rid, ctype, comment, change, org))
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} problem(s); nothing was imported", file=sys.stderr)
        return 1
    for rid, ctype, comment, change, org in comments:
        body = "\n\n".join(f"### {label}\n\n{value or '_No response_'}"
                           for label, value in zip(FIELDS, [rid, ctype, comment, change, org]))
        body += f"\n\n_Imported from spreadsheet `{os.path.basename(args.file)}`._"
        title = f"[{rid}] {comment[:60]}"
        if args.dry_run:
            print(f"would create: {title}")
        else:
            print(gh("issue", "create", "--title", title, "--body", body,
                     "--label", LABEL, "--label", "spreadsheet-import").strip())
    print(f"{len(comments)} comment(s) {'checked (dry run)' if args.dry_run else 'imported'}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--src", default="src/en")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ids").set_defaults(func=cmd_ids)
    triage = sub.add_parser("triage")
    triage.add_argument("--issue")
    triage.set_defaults(func=cmd_triage)
    export = sub.add_parser("export")
    export.add_argument("prefix")
    export.set_defaults(func=cmd_export)
    template = sub.add_parser("template")
    template.add_argument("output")
    template.set_defaults(func=cmd_template)
    imp = sub.add_parser("import")
    imp.add_argument("file")
    imp.add_argument("--dry-run", action="store_true")
    imp.set_defaults(func=cmd_import)
    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
