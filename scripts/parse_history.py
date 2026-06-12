#!/usr/bin/env python3
"""Extract history/biography pages from old site HTML into Hugo markdown."""

import re, os
from html import unescape

SRC = "amb/annemaritbergstrom.com"
OUT = "content/history"

PAGES_ALL = [
    ("history-of-arts",    "history_of_arts.htm",      "History of the Arts in the Lake Region",
     "The rich history of arts and culture in the Devils Lake, North Dakota region", 1),
    ("leo-and-alma",       "leo_alma_2008.htm",         "Leo & Alma: Dedicated to Education, Cultural Enrichment and the Arts",
     "The story of Leo and Alma Studness, Anne-Marit's parents", 2),
    ("two-generations",    "two-generations.htm",       "Two Generations of Music and Art",
     "Two generations of the Studness and Bergstrom families in the arts", 3),
    ("norway-times",       "norway-times.htm",          "Three Generations of Norwegian-American Women in the Arts",
     "Three generations of Norwegian-American women who achieved prominence in the arts", 4),
    ("alma-mehus-studness","alma-mehus-studness.htm",   "Alma Mehus Studness",
     "Anne-Marit's mother — concert pianist and founder of the Lake Region Community Concert Association", 5),
    ("belle-mehus",        "belle-mehus.htm",           "Belle Mehus",
     "Anne-Marit's aunt — pioneer of arts education in North Dakota", 6),
    ("norwegian-ancestors","norwegian-ancestors.htm",   "Norwegian Ancestors",
     "The Mehus and Studness families — Norwegian pioneers in Dakota Territory", 7),
]

# Only regenerate the files that were missing paragraph breaks
PAGES = [p for p in PAGES_ALL if p[0] in (
    "two-generations", "norway-times", "belle-mehus", "norwegian-ancestors", "alma-mehus-studness"
)]

IMG_KEEP = re.compile(r'(the-artist|portraits)/', re.IGNORECASE)
IMG_DROP = re.compile(r'(titles|buttons|images/bg|black_line|images/free_book)/', re.IGNORECASE)

def fix_img_path(src):
    src = re.sub(r'the-artist/small/', '/images/artist/small/', src, flags=re.IGNORECASE)
    src = re.sub(r'the-artist/', '/images/artist/', src, flags=re.IGNORECASE)
    src = re.sub(r'portraits/', '/images/artist/', src, flags=re.IGNORECASE)
    return src

def extract_region(html):
    m = re.search(
        r'InstanceBeginEditable\s+name=["\']EditRegion3["\']["\s]*-->(.*?)<!--\s*InstanceEndEditable',
        html, re.DOTALL)
    return m.group(1) if m else html

def node_to_md(html):
    # Drop scripts/styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)

    # Images: keep artist/portrait images, drop decorative ones
    def handle_img(m):
        tag = m.group(0)
        src_m = re.search(r'src=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        alt_m = re.search(r'alt=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if not src_m:
            return ''
        src = src_m.group(1)
        if IMG_DROP.search(src):
            return ''
        if not IMG_KEEP.search(src):
            return ''
        src = fix_img_path(src)
        alt = alt_m.group(1) if alt_m else ''
        return f'\n\n![{alt}]({src})\n\n'

    # Unwrap anchor tags around images first (remove onClick junk)
    html = re.sub(r'<a[^>]*onClick[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<a[^>]*onfocus[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<img[^>]+/?>', handle_img, html, flags=re.IGNORECASE)

    # Headings
    for lvl in range(4, 0, -1):
        html = re.sub(
            f'<h{lvl}[^>]*>(.*?)</h{lvl}>',
            lambda m, l=lvl: '\n\n' + '#'*(l+1) + ' ' + re.sub(r'<[^>]+>','',m.group(1)).strip() + '\n\n',
            html, flags=re.DOTALL|re.IGNORECASE)

    # HR
    html = re.sub(r'<hr[^>]*/?>', '\n\n---\n\n', html, flags=re.IGNORECASE)

    # Blockquote
    html = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>',
                  lambda m: '\n\n' + '\n'.join('> ' + l for l in
                      re.sub(r'<[^>]+>',' ',m.group(1)).split('\n') if l.strip()) + '\n\n',
                  html, flags=re.DOTALL|re.IGNORECASE)

    # Bold/italic inline
    html = re.sub(r'<b>\s*<i>(.*?)</i>\s*</b>', r'*\1*', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<i>\s*<b>(.*?)</b>\s*</i>', r'*\1*', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<(b|strong)[^>]*>(.*?)</(b|strong)>', r'**\2**', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<(i|em)[^>]*>(.*?)</(i|em)>', r'*\2*', html, flags=re.DOTALL|re.IGNORECASE)

    # Links — keep external href, strip internal .htm links
    def handle_a(m):
        href = re.search(r'href=["\']([^"\']+)["\']', m.group(0))
        inner = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if not href or not inner:
            return inner or ''
        url = href.group(1)
        if url.startswith('javascript') or url.endswith('.htm') or url.endswith('.html'):
            return inner
        return f'[{inner}]({url})'
    html = re.sub(r'<a[^>]*>(.*?)</a>', handle_a, html, flags=re.DOTALL|re.IGNORECASE)

    # Paragraphs and line breaks
    html = re.sub(r'<p[^>]*>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)

    # Table cells → paragraph breaks (these pages use tables for layout)
    html = re.sub(r'</t[dh]>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<t[rh][^>]*>', '\n', html, flags=re.IGNORECASE)

    # Strip remaining tags
    html = re.sub(r'<[^>]+>', '', html)

    # Unescape
    html = unescape(html)

    # Tidy whitespace
    html = re.sub(r'\t', ' ', html)
    html = re.sub(r'[ ]{2,}', ' ', html)
    html = re.sub(r' \n', '\n', html)
    html = re.sub(r'\n ', '\n', html)
    html = re.sub(r'\n{4,}', '\n\n\n', html)

    # Clean up bold markers with spaces
    html = re.sub(r'\*\*\s+', '**', html)
    html = re.sub(r'\s+\*\*([^*])', r'** \1', html)
    html = re.sub(r'\*\*\*\*', '', html)

    # Remove lines that are only noise characters, but preserve blank lines
    noise = re.compile(r'^[\s\xa0&nbsp;]*$')
    cleaned = []
    prev_blank = False
    for l in html.split('\n'):
        is_blank = bool(noise.match(l))
        if is_blank:
            if not prev_blank:
                cleaned.append('')
            prev_blank = True
        else:
            cleaned.append(l)
            prev_blank = False
    return '\n'.join(cleaned).strip()

os.makedirs(OUT, exist_ok=True)

for slug, fname, title, desc, weight in PAGES:
    path = os.path.join(SRC, fname)
    with open(path, 'r', encoding='iso-8859-1') as f:
        html = f.read()

    region = extract_region(html)
    md = node_to_md(region)

    # Escape quotes in front matter values
    title_esc = title.replace('"', '\\"')
    desc_esc = desc.replace('"', '\\"')

    out = f'---\ntitle: "{title_esc}"\ndescription: "{desc_esc}"\nweight: {weight}\n---\n\n{md}\n'

    out_path = os.path.join(OUT, f'{slug}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)

    words = len(md.split())
    print(f'{slug}: ~{words} words → {out_path}')
