#!/usr/bin/env python3
"""Generates a synthetic standard of about 400 pages that follows the authoring
convention, to prove the pipeline at scale. Usage: generate_stress.py OUTDIR"""
import random
import sys
from pathlib import Path

CLAUSES, GROUPS, REQS = 12, 4, 7  # 336 requirements, 1,008 testing procedures
WORDS = ("entity system component access control documented reviewed personnel evidence configuration network "
         "policy procedure assessor record retained periodically defined approved data account process").split()
random.seed(400)


def sentence(n):
    return " ".join(random.choice(WORDS) for _ in range(n)).capitalize() + "."


def para(k):
    return " ".join(sentence(random.randint(12, 24)) for _ in range(k))


out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
doc = ["""= Scale Test Standard
:sectnums:
:sectnumlevels: 3
:toc: macro
:toclevels: 2
:lang: en
:xrefstyle: short

[.informative]
Synthetic document generated to test the pipeline at about 400 pages.

toc::[]

[[scope]]
== Scope

This document exists to test scale.

[[normative-references]]
== Normative references

There are no normative references.

[[terms]]
== Terms and definitions

[[term-entity]]entity::
organisation that the requirements apply to
"""]
for c in range(4, 4 + CLAUSES):
    doc.append(f"\n[[clause-{c}]]\n== Clause title {c}\n\n{para(4)}\n")
    for g in range(1, GROUPS + 1):
        doc.append(f"\n[[group-{c}-{g}]]\n=== Group title {c}.{g}\n\n{para(1)}\n")
        for r in range(1, REQS + 1):
            n = f"{c}.{g}.{r}"
            doc.append(f"\n[[REQ-{n}]]\n[.requirement]\n==== Requirement title {n}\n\n[.statement]\n--\n"
                       f"The <<term-entity,entity>> shall {sentence(18).lower()} {para(1)}\n--\n\n[.testing]\n.Testing procedures\n")
            for letter in "abc":
                doc.append(f"[[TP-{n}.{letter}]]{n}.{letter}:: Examine {sentence(26).lower()} See <<REQ-{c}.1.1>>.\n")
            doc.append(f"\n[.guidance]\n.Guidance\n****\n{para(3)}\n****\n")
            if r == 1:
                doc.append(f"\n.Evidence for {n}\n[cols=\"1,3,3\",options=\"header\"]\n|===\n|Item |Evidence |Notes\n"
                           + "".join(f"\n|{i} |{sentence(14)} |{sentence(20)}" for i in range(1, 6)) + "\n|===\n")
doc.append("""
[[annex-a]]
[appendix.informative]
== Notes (informative)

This annex contains no requirements.

[bibliography.informative]
[[bibliography]]
== Bibliography

* [[[ref,1]]] Example Author, _Example Title_.
""")
(out / "standard.adoc").write_text("".join(doc), encoding="utf-8")
print(f"wrote {out}/standard.adoc: {CLAUSES * GROUPS * REQS} requirements")
