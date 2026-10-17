"""Refresh the "Recent notes" block in README.md from the byanees.com RSS feed."""

import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED_URL = "https://byanees.com/rss.xml"
README = Path(__file__).resolve().parent.parent / "README.md"
MAX_POSTS = 5
# Slugs kept off the profile on purpose.
EXCLUDE = {"build-once-promote-by-tag"}

START, END = "<!-- NOTES:START -->", "<!-- NOTES:END -->"


def fetch_posts():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "byanees-readme"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())

    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        if link.rstrip("/").rsplit("/", 1)[-1] in EXCLUDE:
            continue
        posts.append((title, link))
        if len(posts) == MAX_POSTS:
            break
    return posts


def main():
    posts = fetch_posts()
    if not posts:
        sys.exit("Feed returned no posts; leaving README unchanged.")

    block = "\n".join(f"- [{title}]({link})" for title, link in posts)
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit("NOTES markers not found in README.")

    updated = pattern.sub(f"{START}\n{block}\n{END}", text)
    if updated != text:
        README.write_text(updated, encoding="utf-8")
        print("README updated.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
