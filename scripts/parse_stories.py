#!/usr/bin/env python3
"""Extract story/article pages from old site HTML and create Hugo markdown files."""

import re
import os
from html import unescape

SRC = "/Users/tyler/home/personal/amb.github.io/amb/annemaritbergstrom.com"
OUT = "/Users/tyler/home/personal/amb.github.io/content/stories"

PAGES = {
    "christmas-pioneers": {
        "file": "christmas-pioneers.htm",
        "title": "Christmas among the Pioneers",
        "description": "A 2012 article about pioneer Christmas traditions in the Dakotas",
        "weight": 1,
    },
    "it-takes-two": {
        "file": "it-takes-two.htm",
        "title": "It Takes Two",
        "description": "A 2012 article about collaborative art and music",
        "weight": 2,
    },
    "people-of-the-prairie": {
        "file": "people_of_prairie.htm",
        "title": "'People of Prairie' — a Delightful Read",
        "description": "A 2008 review of the book 'People of the Prairie'",
        "weight": 3,
    },
    "ladies-home-journal": {
        "file": "ladies-home-journal.htm",
        "title": "Ladies Home Journal American Heroine Award",
        "description": "Anne-Marit Bergstrom receives the Ladies Home Journal American Heroine Award, 1984",
        "weight": 4,
    },
    "chamber": {
        "file": "chamber.htm",
        "title": "Bergstrom Creates Murals for Chamber",
        "description": "A 2004 article about the mural commission for the Devils Lake Chamber of Commerce",
        "weight": 5,
    },
    "hero-of-education": {
        "file": "hero-of-eduation.htm",
        "title": "Bergstrom Honored as Hero of Education",
        "description": "Anne-Marit Bergstrom honored as a Hero of Education",
        "weight": 6,
    },
    "chautauqua": {
        "file": "chautauqua.htm",
        "title": "100th Anniversary Chautauqua",
        "description": "The 100th Anniversary Chautauqua celebration in Devils Lake, 1993",
        "weight": 7,
    },
    "settlers-saga": {
        "file": "settlers-saga.htm",
        "title": "ND Artist Paints the Century",
        "description": "A 1989 article about the Settler's Saga centennial paintings",
        "weight": 8,
    },
    "santa-saga": {
        "file": "santa-saga.htm",
        "title": "Santa Has a Home on the Range",
        "description": "A 1988 article about Anne-Marit's Santa painting series",
        "weight": 9,
    },
    "prairie-painter": {
        "file": "prairie-painter.htm",
        "title": "Prairie Painter",
        "description": "A 1985 article about Anne-Marit Bergstrom as a prairie painter",
        "weight": 10,
    },
    "kokoschka": {
        "file": "kokoschka.htm",
        "title": "Life — The Great O.K. of Art and Teaching",
        "description": "About Oskar Kokoschka and Anne-Marit's studies with the legendary artist",
        "weight": 11,
    },
}

def extract_content(html):
    """Extract the main content from between InstanceBeginEditable markers."""
    # Try with various spacing patterns
    m = re.search(
        r'InstanceBeginEditable\s+name=["\']EditRegion3["\']-->(.*?)<!--\s*InstanceEndEditable',
        html, re.DOTALL
    )
    if not m:
        # fallback: get everything after the main navigation table
        m = re.search(r'<td[^>]*height=["\']350["\'][^>]*>(.*?)</td>', html, re.DOTALL)
    return m.group(1) if m else html

def html_to_markdown(html):
    """Convert HTML content to reasonable markdown."""
    # Remove scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)

    # Convert images in the-artist/small/ to our static path
    html = re.sub(
        r'<[^>]*(?:onClick|onfocus)[^>]*>\s*(<img[^>]*>)\s*</a>',
        r'\1',
        html, flags=re.DOTALL|re.IGNORECASE
    )
    html = re.sub(
        r'<a[^>]*(?:onClick|onfocus)[^>]*>\s*(<img[^>]*>)\s*</a>',
        r'\1',
        html, flags=re.DOTALL|re.IGNORECASE
    )
    html = re.sub(
        r'src=["\']the-artist/small/([^"\']+)["\']',
        r'src="/images/artist/small/\1"',
        html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'src=["\']the-artist/([^"\']+)["\']',
        r'src="/images/artist/\1"',
        html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'src=["\']news/([^"\']+)["\']',
        r'src="/images/news/\1"',
        html, flags=re.IGNORECASE
    )

    # Convert heading tags
    for i in range(4, 0, -1):
        html = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>',
                      lambda m, i=i: '\n' + '#'*i + ' ' + re.sub(r'<[^>]+>', '', m.group(1)).strip() + '\n',
                      html, flags=re.DOTALL|re.IGNORECASE)

    # Convert <hr> to ---
    html = re.sub(r'<hr[^>]*>', '\n\n---\n\n', html, flags=re.IGNORECASE)

    # Convert <b><i> and <i><b> to italic (blockquote-style)
    html = re.sub(r'<b>\s*<i>(.*?)</i>\s*</b>', r'*\1*', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<i>\s*<b>(.*?)</b>\s*</i>', r'*\1*', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<strong>\s*<em>(.*?)</em>\s*</strong>', r'**\1**', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<em>\s*<strong>(.*?)</strong>\s*</em>', r'**\1**', html, flags=re.DOTALL|re.IGNORECASE)

    # Bold/italic
    html = re.sub(r'<b>(.*?)</b>', r'**\1**', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<strong>(.*?)</strong>', r'**\1**', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<i>(.*?)</i>', r'*\1*', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<em>(.*?)</em>', r'*\1*', html, flags=re.DOTALL|re.IGNORECASE)

    # Convert images to markdown
    def img_to_md(m):
        src = re.search(r'src=["\']([^"\']+)["\']', m.group(0))
        alt = re.search(r'alt=["\']([^"\']+)["\']', m.group(0))
        if src:
            s = src.group(1)
            a = alt.group(1) if alt else ''
            return f'\n\n![{a}]({s})\n\n'
        return ''
    html = re.sub(r'<img[^>]+>', img_to_md, html, flags=re.IGNORECASE)

    # Convert links
    html = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
                  lambda m: f'[{re.sub(r"<[^>]+>","",m.group(2)).strip()}]({m.group(1)})',
                  html, flags=re.DOTALL|re.IGNORECASE)

    # Convert <p> and <br> to newlines
    html = re.sub(r'<p[^>]*>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)

    # Remove all remaining HTML tags
    html = re.sub(r'<[^>]+>', '', html)

    # Unescape HTML entities
    html = unescape(html)

    # Clean up whitespace
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r' \n', '\n', html)
    html = re.sub(r'\n ', '\n', html)
    html = re.sub(r'\n{4,}', '\n\n\n', html)

    # Fix markdown: remove spaces inside ** **
    html = re.sub(r'\*\*\s+', '**', html)
    html = re.sub(r'\s+\*\*', '**', html)

    return html.strip()

os.makedirs(OUT, exist_ok=True)

for slug, meta in PAGES.items():
    path = os.path.join(SRC, meta["file"])
    try:
        with open(path, 'r', encoding='iso-8859-1') as f:
            html = f.read()
    except FileNotFoundError:
        print(f"NOT FOUND: {path}")
        continue

    content = extract_content(html)
    markdown = html_to_markdown(content)

    # Build frontmatter
    title = meta["title"].replace('"', '\\"')
    desc = meta["description"].replace('"', '\\"')
    front = f'''---
title: "{title}"
description: "{desc}"
weight: {meta["weight"]}
---

'''

    out_path = os.path.join(OUT, f"{slug}.md")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(front + markdown)

    word_count = len(markdown.split())
    print(f"{slug}: ~{word_count} words → {out_path}")
