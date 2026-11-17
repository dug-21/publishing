#!/usr/bin/env python3
"""Assembles the published site and the release artifacts from the build output.

Site layout (BUILD/publish/site), served by GitHub Pages:
  index.html            list of versions
  versions.json         machine-readable list of versions
  <channel>/            "vX.Y.Z" for a release, "draft" for the main branch
      index.html        editions and downloads for that version
      en/ es/ ja/       HTML editions
      downloads/        PDF, OSCAL catalog, CSV/XLSX, comment template
  latest/               copy of the newest release

Versions already present in the site directory (for example fetched from the
gh-pages branch) are kept. Release artifacts go to BUILD/release with checksums.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import tarfile
from pathlib import Path

LANG_NAMES = {"en": "English", "es": "Español", "ja": "日本語"}
STYLE = ("body{font-family:'Noto Sans','DejaVu Sans',sans-serif;line-height:1.55;color:#1a1a1a;background:#fff;"
         "max-inline-size:46rem;margin:2rem auto;padding-inline:1.25rem}a{color:#0b4f9e}"
         "h1{font-size:1.9rem}h2{font-size:1.35rem;margin-block-start:2rem}li{margin-block:.3rem}")


def page(title, body, lang="en"):
    return (f'<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{html.escape(title)}</title>\n'
            f'<style>{STYLE}</style>\n</head>\n<body>\n<main>\n<h1>{html.escape(title)}</h1>\n{body}\n</main>\n</body>\n</html>\n')


def links(items):
    return "<ul>\n" + "\n".join(f'<li><a href="{html.escape(h)}"{a}>{html.escape(t)}</a></li>' for h, t, a in items) + "\n</ul>"


def version_key(name):
    return tuple(int(n) for n in re.findall(r"\d+", name))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--build", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--title", default="Member Data Stewardship Standard")
    parser.add_argument("--langs", required=True)
    parser.add_argument("--channel", choices=["draft", "release"], default="draft")
    args = parser.parse_args()
    build, langs = Path(args.build), args.langs.split()
    site, release = build / "publish" / "site", build / "release"
    slot = f"v{args.version}" if args.channel == "release" else "draft"
    target = site / slot
    shutil.rmtree(target, ignore_errors=True)
    shutil.rmtree(release, ignore_errors=True)
    (target / "downloads").mkdir(parents=True)
    release.mkdir(parents=True)

    for lang in langs:
        shutil.copytree(build / "site" / lang, target / lang)
    artifacts = sorted(p for p in (build / "dist").iterdir() if p.is_file())
    for path in artifacts:
        shutil.copy2(path, target / "downloads" / path.name)
        shutil.copy2(path, release / path.name)

    label = f"version {args.version}" + (" (draft)" if args.channel == "draft" else "")
    body = (f"<p>{html.escape(label.capitalize())}.</p>\n<h2>Read online</h2>\n"
            + links([(f"{l}/", LANG_NAMES.get(l, l), f' lang="{l}" hreflang="{l}"') for l in langs])
            + "\n<h2>Downloads</h2>\n" + links([(f"downloads/{p.name}", p.name, "") for p in artifacts])
            + '\n<p><a href="../">All versions</a></p>')
    (target / "index.html").write_text(page(f"{args.title} {label}", body), encoding="utf-8")

    releases = sorted((d.name for d in site.iterdir() if d.is_dir() and re.fullmatch(r"v\d+\.\d+\.\d+", d.name)),
                      key=version_key, reverse=True)
    if releases:
        shutil.rmtree(site / "latest", ignore_errors=True)
        shutil.copytree(site / releases[0], site / "latest")
    has_draft = (site / "draft").is_dir()
    versions = {"latest": releases[0] if releases else None, "releases": releases, "draft": has_draft}
    (site / "versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    items = ([("latest/", f"Latest release ({releases[0]})", "")] if releases else []) \
        + [(f"{v}/", v, "") for v in releases] + ([("draft/", "Draft (main branch, not yet released)", "")] if has_draft else [])
    (site / "index.html").write_text(page(args.title, "<h2>Versions</h2>\n" + links(items)), encoding="utf-8")
    (site / ".nojekyll").write_text("")

    with tarfile.open(release / f"{args.name}-{args.version}-site.tar.gz", "w:gz") as tar:
        tar.add(target, arcname=f"{args.name}-{args.version}-site")
    sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(release.iterdir())]
    (release / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(f"site: {target} ({', '.join(langs)}); versions on site: {releases or 'none'}{' + draft' if has_draft else ''}")
    print(f"release artifacts: {release} ({len(sums)} files + SHA256SUMS)")


if __name__ == "__main__":
    main()
