#!/usr/bin/env python3
"""Parse old paintings HTML files and generate Hugo YAML data files."""

import re
import os
from html.parser import HTMLParser
from html import unescape

SRC = "/Users/tyler/home/personal/amb.github.io/amb/annemaritbergstrom.com"
OUT = "/Users/tyler/home/personal/amb.github.io/data/paintings"

PAGES = {
    "reminiscing": "paintings-reminiscing.htm",
    "floral": "paintings-floral.htm",
    "christmas": "paintings-christmas.htm",
    "chautauqua": "paintings-chautauqua.htm",
    "mystical-moments": "paintings-mystical_moments.htm",
    "seasons": "paintings-seasons.htm",
    "early-works": "paintings-early_works.htm",
    "fantasy": "paintings-fantasy.htm",
    "saint-croix": "paintings-saint_croix.htm",
    "travels": "paintings-travels.htm",
    "step-back-in-time": "paintings-step_back_in_time.htm",
    "remembering-popsel": "paintings-popsel.htm",
    "magic-telescope": "paintings-magic_telescope.htm",
    "people-of-the-prairie": "paintings-people_of_the_prairie.htm",
    "self-portraits": "paintings-self_portraits.htm",
}

def clean(s):
    s = unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_content_region(html):
    """Extract content between the InstanceBeginEditable markers."""
    m = re.search(
        r'InstanceBeginEditable name="EditRegion3"-->(.*?)<!--\s*InstanceEndEditable',
        html, re.DOTALL
    )
    return m.group(1) if m else html

def parse_paintings(html):
    """Parse table rows to extract painting data."""
    content = extract_content_region(html)
    paintings = []

    # Find all table rows with painting data
    # Pattern: rows containing img tags pointing to the-art/thumbs/
    rows = re.findall(r'<tr[^>]*valign=["\']top["\'][^>]*>(.*?)</tr>', content, re.DOTALL | re.IGNORECASE)

    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(cells) < 2:
            continue

        # Check first cell has a painting thumbnail
        cell0 = cells[0]
        if 'the-art/thumbs/' not in cell0 and 'the-art/thumbs/' not in cell0.lower():
            continue

        # Extract thumb image
        thumb_m = re.search(r'the-art/thumbs/([^\s"\']+)', cell0, re.IGNORECASE)
        if not thumb_m:
            continue
        thumb = thumb_m.group(1)

        # Extract full-size image (from anchor href or from onClick)
        full = thumb  # default
        full_m = re.search(r"href=['\"]the-art/([^'\"]+\.jpg)['\"]", cell0, re.IGNORECASE)
        if full_m:
            full = full_m.group(1)
        else:
            onclick_m = re.search(r"MM_openBrWindow\('the-art/([^']+\.jpg)'", cell0, re.IGNORECASE)
            if onclick_m:
                full = onclick_m.group(1)
            else:
                onclick_m2 = re.search(r"NewWindow\(this\.href", cell0, re.IGNORECASE)
                if onclick_m2:
                    href_m = re.search(r'href=["\']the-art/([^"\']+\.jpg)["\']', cell0, re.IGNORECASE)
                    if href_m:
                        full = href_m.group(1)

        # Extract title from second cell
        cell1 = cells[1] if len(cells) > 1 else ""
        # Try em/strong pattern first
        title_m = re.search(r'<em[^>]*>\s*<strong[^>]*>(.*?)</strong>', cell1, re.DOTALL | re.IGNORECASE)
        if not title_m:
            title_m = re.search(r'<strong[^>]*>\s*<em[^>]*>(.*?)</em>', cell1, re.DOTALL | re.IGNORECASE)
        if not title_m:
            title_m = re.search(r'<b[^>]*>\s*<i[^>]*>(.*?)</i>', cell1, re.DOTALL | re.IGNORECASE)
        if not title_m:
            title_m = re.search(r'<i[^>]*>\s*<b[^>]*>(.*?)</b>', cell1, re.DOTALL | re.IGNORECASE)
        if not title_m:
            # Try alt text from img tag
            alt_m = re.search(r'alt=["\']([^"\']+)["\']', cell0, re.IGNORECASE)
            if alt_m:
                title = clean(alt_m.group(1))
            else:
                continue
        else:
            title = clean(re.sub(r'<[^>]+>', '', title_m.group(1)))

        if not title:
            continue

        # Strip HTML tags from cell1 for medium/dimensions extraction
        cell1_text = re.sub(r'<[^>]+>', '\n', cell1)
        cell1_text = unescape(cell1_text)
        lines = [l.strip() for l in cell1_text.split('\n') if l.strip()]

        medium = ""
        dimensions = ""
        for line in lines:
            if title.lower() in line.lower():
                continue
            if re.search(r'oil|watercolor|acrylic|pastel|mixed|pencil|charcoal', line, re.IGNORECASE):
                medium = clean(line)
            elif re.search(r'\d+["\']?\s*[xXbB×]\s*\d+', line):
                dimensions = clean(line)

        # Extract collection from third cell
        collection = ""
        if len(cells) > 2:
            cell2_text = re.sub(r'<[^>]+>', ' ', cells[2])
            cell2_text = unescape(cell2_text)
            collection = clean(re.sub(r'\s+', ' ', cell2_text).strip())

        # Fall back to thumb path if full-size doesn't exist on disk
        if not has_fullsize(full):
            full = "thumbs/" + thumb

        if title:
            p = {"title": title, "thumb": thumb, "full": full}
            if medium:
                p["medium"] = medium
            if dimensions:
                p["dimensions"] = dimensions
            if collection:
                p["collection"] = collection
            paintings.append(p)

    return paintings

def yaml_str(v):
    # Single-quoted YAML: escape single quotes by doubling, everything else is literal
    if "'" in v:
        # Use double-quoted YAML, escaping backslashes and double quotes
        escaped = v.replace('\\', '\\\\').replace('"', '\\"')
        return '"' + escaped + '"'
    if '"' in v:
        return "'" + v + "'"
    return '"' + v + '"'

def to_yaml(paintings):
    lines = ["paintings:"]
    for p in paintings:
        lines.append(f"  - title: {yaml_str(p['title'])}")
        lines.append(f"    thumb: {yaml_str(p['thumb'])}")
        lines.append(f"    full: {yaml_str(p['full'])}")
        if p.get("medium"):
            lines.append(f"    medium: {yaml_str(p['medium'])}")
        if p.get("dimensions"):
            lines.append(f"    dimensions: {yaml_str(p['dimensions'])}")
        if p.get("collection"):
            lines.append(f"    collection: {yaml_str(p['collection'])}")
    return "\n".join(lines) + "\n"

STATIC_ART = "/Users/tyler/home/personal/amb.github.io/static/images/art"

def has_fullsize(filename):
    return os.path.exists(os.path.join(STATIC_ART, filename))

os.makedirs(OUT, exist_ok=True)

for slug, filename in PAGES.items():
    path = os.path.join(SRC, filename)
    try:
        with open(path, 'r', encoding='iso-8859-1') as f:
            html = f.read()
    except FileNotFoundError:
        print(f"NOT FOUND: {path}")
        continue

    paintings = parse_paintings(html)
    out_path = os.path.join(OUT, f"{slug}.yaml")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(to_yaml(paintings))
    print(f"{slug}: {len(paintings)} paintings → {out_path}")
