#!/usr/bin/env python3
"""Validates PDFs against PDF/UA-1 with veraPDF and prints each failed rule."""
import subprocess
import sys
import xml.etree.ElementTree as ET

failed = False
for path in sys.argv[1:]:
    run = subprocess.run(["verapdf", "--flavour", "ua1", "--format", "xml", path], capture_output=True, text=True)
    try:
        report = ET.fromstring(run.stdout).find(".//validationReport")
    except ET.ParseError:
        report = None
    if report is None:
        failed = True
        print(f"{path}: veraPDF produced no report\n{run.stderr.strip()[-500:]}")
        continue
    details = report.find("details")
    if report.get("isCompliant") == "true":
        print(f"{path}: PDF/UA-1 OK ({details.get('passedRules')} rules passed)")
        continue
    failed = True
    for rule in details.findall("rule"):
        if rule.get("status") == "failed":
            print(f"{path}: [PDF/UA-1 clause {rule.get('clause')} test {rule.get('testNumber')}] "
                  f"{rule.findtext('description')} ({rule.get('failedChecks')} occurrence(s))")
    print(f"{path}: not PDF/UA-1 compliant, {details.get('failedRules')} rule(s) failed", file=sys.stderr)
sys.exit(1 if failed else 0)
