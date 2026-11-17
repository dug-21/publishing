#!/usr/bin/env python3
"""Writes the GRC import files from requirements.json.

  PREFIX-requirements.csv        one row per requirement
  PREFIX-testing-procedures.csv  one row per testing procedure
  PREFIX-requirements.xlsx       both tables as sheets

With --verify, re-reads the files and fails if the row counts differ from
requirements.json.
"""
import argparse
import csv
import json
import sys

import openpyxl
import xlsxwriter

REQ_COLUMNS = ["requirement_id", "number", "clause", "clause_title", "group", "group_title",
               "title", "requirement_text", "testing_procedures", "guidance", "standard_version"]
TP_COLUMNS = ["procedure_id", "requirement_id", "label", "procedure_text", "standard_version"]
FORBIDDEN = set("<>\\")  # rejected by some GRC importers


def tables(data):
    version = data["document"]["version"]
    reqs, procs = [], []
    for r in data["requirements"]:
        reqs.append([r["id"], r["number"], r["clause"]["number"], r["clause"]["title"],
                     r["group"]["number"], r["group"]["title"], r["title"], r["statement"],
                     "\n".join(f"{p['label']} {p['text']}" for p in r["testing_procedures"]),
                     r["guidance"], version])
        for p in r["testing_procedures"]:
            procs.append([p["id"], r["id"], p["label"], p["text"], version])
    return reqs, procs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("requirements_json")
    parser.add_argument("prefix")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    with open(args.requirements_json, encoding="utf-8") as handle:
        data = json.load(handle)
    reqs, procs = tables(data)
    files = {"req": f"{args.prefix}-requirements.csv", "tp": f"{args.prefix}-testing-procedures.csv",
             "xlsx": f"{args.prefix}-requirements.xlsx"}

    if args.verify:
        problems = []
        for key, expected in (("req", reqs), ("tp", procs)):
            with open(files[key], encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))[1:]
            if len(rows) != len(expected):
                problems.append(f"{files[key]}: {len(rows)} rows, expected {len(expected)}")
        book = openpyxl.load_workbook(files["xlsx"], read_only=True)
        for sheet, expected in (("Requirements", reqs), ("Testing procedures", procs)):
            count = book[sheet].max_row - 1
            if count != len(expected):
                problems.append(f"{files['xlsx']} [{sheet}]: {count} rows, expected {len(expected)}")
        for message in problems:
            print(message)
        if not problems:
            print(f"exports: OK ({len(reqs)} requirements, {len(procs)} testing procedures)")
        return 1 if problems else 0

    for row in reqs + procs:
        for cell in row:
            bad = FORBIDDEN & set(cell)
            if bad:
                print(f"{row[0]}: text contains {sorted(bad)}, which some GRC importers reject", file=sys.stderr)
                return 1
    for key, columns, rows in (("req", REQ_COLUMNS, reqs), ("tp", TP_COLUMNS, procs)):
        with open(files[key], "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
            writer.writerows(rows)
    book = xlsxwriter.Workbook(files["xlsx"])
    book.set_properties({"title": f"{data['document']['title']} {data['document']['version']}"})
    header = book.add_format({"bold": True, "text_wrap": True, "valign": "top", "border": 1})
    body = book.add_format({"text_wrap": True, "valign": "top"})
    for name, columns, rows, widths in (
        ("Requirements", REQ_COLUMNS, reqs, [14, 9, 8, 24, 8, 24, 30, 60, 60, 60, 10]),
        ("Testing procedures", TP_COLUMNS, procs, [14, 14, 10, 80, 10]),
    ):
        sheet = book.add_worksheet(name)
        sheet.write_row(0, 0, columns, header)
        for index, row in enumerate(rows, start=1):
            sheet.write_row(index, 0, row, body)
        for index, width in enumerate(widths):
            sheet.set_column(index, index, width)
        sheet.freeze_panes(1, 0)
        sheet.autofilter(0, 0, len(rows), len(columns) - 1)
    book.close()
    print(f"wrote {', '.join(files.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
