#!/usr/bin/env python3
"""Builds an OSCAL catalog (JSON) from requirements.json.

Mapping: clause and group -> group; requirement -> control; statement ->
part "statement"; each testing procedure -> part "assessment-method";
guidance -> part "guidance".
"""
import argparse
import json
import uuid

NAMESPACE = uuid.UUID("6f0c1f2e-5b0a-4d55-9a54-6f2a1d8f3c10")
METHODS = {"Examine": "EXAMINE", "Observe": "EXAMINE", "Interview": "INTERVIEW"}


def control(req):
    parts = [{"id": f"{req['id']}_smt", "name": "statement", "prose": req["statement"]}]
    for proc in req["testing_procedures"]:
        verb = proc["text"].split(" ", 1)[0]
        parts.append({
            "id": proc["id"],
            "name": "assessment-method",
            "props": [
                {"name": "label", "value": proc["label"]},
                {"name": "method", "value": METHODS.get(verb, "EXAMINE")},
            ],
            "prose": proc["text"],
        })
    parts.append({"id": f"{req['id']}_gdn", "name": "guidance", "prose": req["guidance"]})
    return {
        "id": req["id"],
        "class": "requirement",
        "title": req["title"],
        "props": [
            {"name": "label", "value": req["number"]},
            {"name": "sort-id", "value": "-".join(f"{int(n):03d}" for n in req["number"].split("."))},
        ],
        "parts": parts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirements_json")
    parser.add_argument("output")
    parser.add_argument("--oscal-version", default="1.2.1")
    parser.add_argument("--last-modified", required=True, help="RFC 3339 timestamp")
    args = parser.parse_args()
    with open(args.requirements_json, encoding="utf-8") as handle:
        data = json.load(handle)
    doc = data["document"]

    clauses = {}
    for req in data["requirements"]:
        clause = clauses.setdefault(req["clause"]["id"], {**req["clause"], "groups": {}})
        group = clause["groups"].setdefault(req["group"]["id"], {**req["group"], "controls": []})
        group["controls"].append(control(req))

    def as_group(item, cls, **children):
        return {"id": item["id"], "class": cls, "title": item["title"],
                "props": [{"name": "label", "value": item["number"]}], **children}

    catalog = {
        "catalog": {
            "uuid": str(uuid.uuid5(NAMESPACE, f"{doc['title']}|{doc['version']}|{doc['lang']}")),
            "metadata": {
                "title": doc["title"],
                "last-modified": args.last_modified,
                "version": doc["version"],
                "oscal-version": args.oscal_version,
            },
            "groups": [
                as_group(c, "clause", groups=[as_group(g, "group", controls=g["controls"]) for g in c["groups"].values()])
                for c in clauses.values()
            ],
        }
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote {args.output}: {len(data['requirements'])} controls")


if __name__ == "__main__":
    main()
